#!/usr/bin/env python3
"""outcome/realgames.py — real games through the Epoch IV layers (E12).

Epoch IV was designed on priors; E12 connects it to actual games.  The
audit replays every game ply by ply with the certified legality
machinery (outcome.pgn), finds the plies that land inside the oracle
space (a frozen domain or bare kings) and scores THREE arms against the
ground truth:

    exact           the theorem (tablebase / bare-kings rule) — the
                    upper bound any statistical layer cannot exceed;
    model           the distilled phase-space model (the E8 ensemble,
                    the E11 router where a specialist is promoted);
    model+context   the Epoch IV water-filling blend with the Elo prior
                    read from the PGN headers (WhiteElo/BlackElo).

Corpus sources and their honesty contract:

    human-classical  public-domain classical scores.  They carry NO Elo
                     headers, so the context layer must be a strict
                     no-op on them — the audit verifies exactly that
                     (blended == model on every row) instead of
                     trusting the promise;
    engine           laboratory self-play games (no ratings: no-op);
    tablebase-walk   seeded walks through the frozen domains whose
                     terminal outcome is known from the certificates.
                     They carry SIMULATED, clearly-labeled Elo headers
                     (generated with a documented alignment knob, never
                     from real player data) so the context A/B has
                     signal — the report separates aligned / independent
                     alignment so "what a rating prior is worth" is
                     measured, not assumed.

Game-level ground truth is the Result header; position-level ground
truth is the exact oracle.  A game whose Result contradicts the board
(mate delivered but scored 0-1) is flagged, never silently fixed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import context as CTX                          # noqa: E402
from outcome import falsify as FLS                          # noqa: E402
from outcome import features as F                           # noqa: E402
from outcome import metrics as MT                           # noqa: E402
from outcome import model as M                              # noqa: E402
from outcome import pgn as P                                # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402
from outcome import trajectory as TR                        # noqa: E402

MODEL_PATH = os.path.join(T.RESULTS_DIR, 'outcome_model.json')

SOURCES = ('human-classical', 'engine', 'tablebase-walk')


def _log(p):
    """Natural log with the same floor as metrics.log_loss."""
    import math
    return math.log(max(p, 1e-15))


def _int_or_none(text):
    try:
        v = int(str(text).strip())
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def game_player_context(game):
    """PlayerContext from PGN headers; None when the game carries no
    ratings (the strict no-op contract of the context layer)."""
    rw = _int_or_none(game.headers.get('WhiteElo'))
    rb = _int_or_none(game.headers.get('BlackElo'))
    if rw is None or rb is None:
        return None
    return CTX.PlayerContext(rating_white=rw, rating_black=rb)


def source_of(game):
    src = game.headers.get('Source')
    return src if src in SOURCES else 'human-classical'


def _one_hot(cls):
    probs = [0.0, 0.0, 0.0]
    if cls is not None:
        probs[cls] = 1.0
    return probs


def audit_positions(game, proba_fn, names):
    """Rows for every ply inside the oracle space of one game.

    proba_fn: (X, slice_key) -> list of probability rows (the frozen
    load_heads convention).  Returns (rows, flags) where flags records
    whether the context prior was active anywhere."""
    positions = game.replay()
    ctx = game_player_context(game)
    rows = []
    context_active = ctx is not None
    for ply, pos in enumerate(positions):
        kind, wk, piece_sq, bk, stm = TR.pos_to_quad(pos)
        if kind is None:
            continue                            # outside the oracle space
        if kind == 'kk':
            probe = {'legal': True, 'outcome': 'draw', 'cls': T.DRAW,
                     'dtm_plies': None}
            slice_key = None
        else:
            probe = T.probe_state(kind, wk, piece_sq, bk, stm)
            slice_key = kind
            if not probe['legal']:
                continue
        vec = F.extract_vector(pos, names)
        p_model = [float(v) for v in proba_fn([vec], slice_key)[0]]
        if ctx is not None:
            p_blend, blend_info = CTX.blend(p_model, ctx)
            context_active = context_active and \
                blend_info.get('weight', 0.0) > 0.0
        else:
            p_blend, blend_info = list(p_model), {'weight': 0.0}
        rows.append({
            'ply': ply,
            'kind': kind,
            'fen': pos.to_fen(),
            'exact_cls': probe['cls'],
            'dtm_plies': probe['dtm_plies'],
            'exact_probs': _one_hot(probe['cls']),
            'model_probs': [round(v, 6) for v in p_model],
            'blended_probs': [round(v, 6) for v in p_blend],
            'context_weight': blend_info.get('weight', 0.0),
        })
    return rows, context_active


def score_rows(rows, actual_cls):
    """Game-level scoring of the three arms against the actual result.

    Returns {'exact': {...}, 'model': {...}, 'model+context': {...}};
    metrics are None when the game has no oracle entries or no usable
    Result header — recorded honestly, never imputed."""
    if not rows or actual_cls is None:
        return None
    out = {}
    for arm, key in (('exact', 'exact_probs'),
                     ('model', 'model_probs'),
                     ('model+context', 'blended_probs')):
        probs = [r[key] for r in rows]
        preds = [max(range(3), key=lambda k: p[k]) for p in probs]
        out[arm] = {
            'log_loss': round(MT.log_loss([actual_cls] * len(probs), probs),
                              6),
            'accuracy': round(MT.accuracy([actual_cls] * len(probs), preds),
                              6),
            'brier': round(MT.brier([actual_cls] * len(probs), probs), 6),
        }
    # drift: how often does the model's argmax flip between consecutive
    # oracle entries of the same game (the real-game surprise rate)
    flips = 0
    for a, b in zip(rows, rows[1:]):
        pa = max(range(3), key=lambda k: a['model_probs'][k])
        pb = max(range(3), key=lambda k: b['model_probs'][k])
        flips += (pa != pb)
    out['model_argmax_flips'] = flips
    out['n_entries'] = len(rows)
    return out


def audit_game(game, proba_fn, names):
    """One game -> its audit record (rows kept JSON-ready)."""
    rows, context_active = audit_positions(game, proba_fn, names)
    scores = score_rows(rows, game.result_cls())
    kinds = {}
    for r in rows:
        kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
    return {
        'file': game.headers.get('_file', ''),
        'source': source_of(game),
        'white': game.headers.get('White', '?'),
        'black': game.headers.get('Black', '?'),
        'result': game.result,
        'plies': len(game.sans),
        'context_active': bool(context_active),
        'entries_per_kind': kinds,
        'scores': scores,
        'rows': rows,
    }


def audit_corpus(paths, model_path=None, log=print):
    """The E12 audit over a PGN file or a directory of .pgn files."""
    games = _load_games(paths, log)
    if not games:
        raise SystemExit('no PGN games found under %r' % (paths,))
    payload = M.load_model(model_path or MODEL_PATH)
    names, proba, _ridge = FLS.load_heads(payload)

    per_game = []
    for g in games:
        try:
            rec = audit_game(g, proba, names)
        except P.PGNError as exc:
            log('  %-34s FAILED REPLAY: %s'
                % (g.headers.get('_file', '?'), exc))
            per_game.append({'file': g.headers.get('_file', ''),
                             'source': source_of(g),
                             'error': str(exc), 'rows': [],
                             'entries_per_kind': {}, 'scores': None,
                             'context_active': False, 'plies': 0,
                             'result': g.result})
            continue
        rec['file'] = rec['file'] or g.headers.get('_file', '')
        per_game.append(rec)
        s = rec['scores']
        entry = 'entries %2d' % sum(rec['entries_per_kind'].values()) \
            if rec['entries_per_kind'] else 'no oracle entries'
        if s:
            log('  %-34s %-15s result %-7s %s | model logloss %.3f | '
                'ctx logloss %.3f'
                % (rec['file'], rec['source'], rec['result'], entry,
                   s['model']['log_loss'], s['model+context']['log_loss']))
        else:
            log('  %-34s %-15s result %-7s %s'
                % (rec['file'], rec['source'], rec['result'], entry))

    report = _aggregate(per_game)
    report['recipe'] = {
        'model': os.path.basename(model_path or MODEL_PATH),
        'n_games': len(per_game),
        'protocol': 'position-level oracle entries scored at game level '
                    'against the Result header; exact arm = the upper '
                    'bound; context = Elo prior from PGN headers',
    }
    return report, per_game


def _load_games(paths, log):
    files = []
    if os.path.isdir(paths):
        for name in sorted(os.listdir(paths)):
            if name.lower().endswith('.pgn'):
                files.append(os.path.join(paths, name))
    else:
        files = [paths]
    games = []
    for path in files:
        for g in P.read_pgn_file(path):
            g.headers['_file'] = os.path.basename(path)
            games.append(g)
    return games


def _aggregate(per_game):
    """Corpus-level aggregates (position-level and game-level)."""
    n_rows = 0
    pos_agree = pos_total = 0            # model argmax vs exact oracle
    pos_ll_model = pos_ll_blend = 0.0
    pos_ll_exact = 0.0
    kinds = {}
    sources = {}
    game_scores = {'exact': [], 'model': [], 'model+context': []}
    flips = flip_pairs = 0
    no_op_rows = 0
    flagged = []
    for rec in per_game:
        sources[rec['source']] = sources.get(rec['source'], 0) + 1
        for k, n in rec['entries_per_kind'].items():
            kinds[k] = kinds.get(k, 0) + n
        s = rec['scores']
        if s:
            for arm in game_scores:
                game_scores[arm].append((s[arm]['log_loss'],
                                         s[arm]['accuracy'],
                                         s[arm]['brier']))
            flips += s['model_argmax_flips']
            flip_pairs += max(s['n_entries'] - 1, 0)
        for r in rec['rows']:
            n_rows += 1
            if r['context_weight'] == 0.0:
                no_op_rows += 1
            cls = r['exact_cls']
            if cls is None:
                continue
            pos_ll_exact -= _log(r['exact_probs'][cls])
            pos_ll_model -= _log(r['model_probs'][cls])
            pos_ll_blend -= _log(r['blended_probs'][cls])
            pred = max(range(3), key=lambda k: r['model_probs'][k])
            pos_agree += (pred == cls)
            pos_total += 1
        # result/board consistency flag (mate scored as a loss etc.)
        if rec['result'] not in ('1-0', '0-1', '1/2-1/2', '*'):
            flagged.append(rec['file'])

    def _mean(seq, idx):
        return round(sum(v[idx] for v in seq) / max(len(seq), 1), 6)

    def _pack(seq):
        return {'n': len(seq), 'log_loss': _mean(seq, 0),
                'accuracy': _mean(seq, 1), 'brier': _mean(seq, 2)}

    return {
        'certificate': 'E12 — real games through the Epoch IV layers',
        'totals': {
            'games': len(per_game),
            'games_with_result': sum(
                1 for r in per_game if r['scores']),
            'oracle_entries': n_rows,
            'sources': sources,
            'entries_per_kind': kinds,
            'context_noop_rows': no_op_rows,
        },
        'position_level': {
            'model_vs_exact_agreement': round(pos_agree / max(pos_total, 1),
                                              6),
            'n_scored_positions': pos_total,
            'log_loss_exact': round(pos_ll_exact / max(pos_total, 1), 6),
            'log_loss_model': round(pos_ll_model / max(pos_total, 1), 6),
            'log_loss_model_context': round(
                pos_ll_blend / max(pos_total, 1), 6),
        },
        'game_level': {arm: _pack(seq) for arm, seq in game_scores.items()},
        'model_argmax_flip_rate': round(flips / max(flip_pairs, 1), 6),
        'context_noop_share': round(no_op_rows / max(n_rows, 1), 6),
        'flagged_results': flagged,
    }
