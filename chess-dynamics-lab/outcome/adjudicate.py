#!/usr/bin/env python3
"""outcome/adjudicate.py — whole-game adjudication through the E9 model.

Epoch VIII closes the loop the program has been building since Epoch IV:
the E12 audit replays real games, the E9 trajectory model forecasts a
line's final outcome from its prefix — this module joins them and asks
the referee question:

    "given the oracle-space prefix of a whole game, how early and how
     reliably can each instrument call the final result?"

The referee panel (four arms, one question):

    exact                   the position oracle at the cutoff entry (the
                            theorem — at the FINAL entry it must agree
                            with the Result header, at earlier cutoffs
                            it honestly may not: a drawn position can
                            still be blundered);
    state                   the frozen state model (the E8 ensemble /
                            E13 router) evaluated at the cutoff position
                            — the E12 arm, which sees no history;
    trajectory_gated        the E9 gated pooling model over the whole
                            prefix — history counts;
    trajectory_final_only   the E9 no-history ablation twin — the
                            control that isolates what the gate adds.

Adjudication curve: every arm must call the result from the first t+1
oracle entries, for t in ADJ_TS; accuracy and log loss are scored
against the Result header at game level.  A game with no oracle-space
entries is skipped and counted (the classical scores never reach a
frozen domain — the referee only judges where the certificates speak).

Honesty notes.  The E9 gate input g_t = [t/T, dtm/cap] uses the
oracle-entry ordinal as the time axis and the EXACT DTM of each entry —
the referee works inside certificate space, where both are well defined,
and this is stated, not hidden.  No model is retrained here: E15 is a
pure evaluation of frozen artifacts, so it is bit-reproducible by
construction.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from outcome import features as F                           # noqa: E402
from outcome import falsify as FLS                          # noqa: E402
from outcome import metrics as MT                           # noqa: E402
from outcome import model as M                              # noqa: E402
from outcome import pgn as P                                # noqa: E402
from outcome import realgames as RG                         # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402
from outcome import trajectory as TR                        # noqa: E402

TRAJECTORY_PATH = os.path.join(T.RESULTS_DIR, 'outcome_trajectory.json')
ADJ_TS = (0, 1, 2, 3, 5, 10, 20, -1)     # -1 = the final oracle entry
ARMS = ('exact', 'state', 'trajectory_gated', 'trajectory_final_only')


def load_trajectory_models(path=TRAJECTORY_PATH):
    """The two frozen E9 models (gated + final-only) from the certificate."""
    with open(path, 'r', encoding='utf-8') as fh:
        report = json.load(fh)
    gated = TR.TrajectoryModel.from_json(report['model_gated'])
    final_only = TR.TrajectoryModel.from_json(report['model_final_only'])
    return gated, final_only


def _one_hot(cls):
    probs = [0.0, 0.0, 0.0]
    if cls is not None:
        probs[cls] = 1.0
    return probs


def game_steps(game, names):
    """Oracle-space steps of one replayed game — the referee's view.

    Returns (X, G, kinds, cls) where X are phase-space vectors, G the
    E9 gate inputs (time axis = oracle-entry ordinal), kinds the domain
    of each entry ('kk' for bare kings) and cls the exact outcome class
    of each entry."""
    X, G, kinds, cls = [], [], [], []
    for pos in game.replay():
        kind, wk, piece_sq, bk, stm = TR.pos_to_quad(pos)
        if kind is None:
            continue                        # outside the oracle space
        if kind == 'kk':
            dtm = None
            entry_cls = T.DRAW              # the bare-kings theorem
        else:
            probe = T.probe_state(kind, wk, piece_sq, bk, stm)
            if not probe['legal']:
                continue
            dtm = probe['dtm_plies']
            entry_cls = probe['cls']
        X.append(F.extract_vector(pos, names))
        t = len(X) - 1
        G.append([t / float(TR.DEFAULT_HORIZON),
                  (dtm if dtm is not None else -1) / TR.DTM_CAP])
        kinds.append(kind)
        cls.append(entry_cls)
    return X, G, kinds, cls


def adjudicate_game(game, proba_fn, gated, final_only, names):
    """One game -> per-entry probabilities for every arm (None if the
    game never enters the oracle space)."""
    X, G, kinds, cls = game_steps(game, names)
    if not X:
        return None
    n = len(X)
    state = [list(proba_fn([X[i]], kinds[i])[0]) for i in range(n)]
    traj_gated = [gated.predict_prefix(X, G, i) for i in range(n)]
    traj_final = [final_only.predict_prefix(X, G, i) for i in range(n)]
    return {
        'file': game.headers.get('_file', ''),
        'source': RG.source_of(game),
        'result': game.result,
        'actual_cls': game.result_cls(),
        'n_entries': n,
        'entries_per_kind': {k: kinds.count(k) for k in sorted(set(kinds))},
        'probs': {
            'exact': [_one_hot(cls[i]) for i in range(n)],
            'state': state,
            'trajectory_gated': traj_gated,
            'trajectory_final_only': traj_final,
        },
        'cls': cls,
    }


def _cutoff_index(t, n):
    """ADJ_TS cutoff -> concrete entry index (clamped, -1 = last)."""
    if t < 0:
        return n - 1
    return min(t, n - 1)


def _curve(recs, arm):
    """Game-level adjudication curve of one arm over scoreable games."""
    out = {}
    for t in ADJ_TS:
        y_true, probs_all = [], []
        for rec in recs:
            c = _cutoff_index(t, rec['n_entries'])
            probs_all.append(rec['probs'][arm][c])
            y_true.append(rec['actual_cls'])
        preds = [max(range(3), key=lambda k: p[k]) for p in probs_all]
        key = 'final' if t < 0 else str(t)
        out[key] = {
            'accuracy': round(MT.accuracy(y_true, preds), 6),
            'log_loss': round(MT.log_loss(y_true, probs_all), 6),
            'n': len(y_true),
        }
    return out


def _final_summary(recs):
    """Final-entry referee panel: accuracy/logloss/Brier + call flips
    (how often the arm's verdict changes between consecutive entries —
    the stability a real arbiter would demand)."""
    out = {}
    for arm in ARMS:
        y_true = [rec['actual_cls'] for rec in recs]
        probs_all = [rec['probs'][arm][rec['n_entries'] - 1] for rec in recs]
        preds = [max(range(3), key=lambda k: p[k]) for p in probs_all]
        flips = pairs = 0
        for rec in recs:
            for a, b in zip(rec['probs'][arm], rec['probs'][arm][1:]):
                pairs += 1
                flips += (max(range(3), key=lambda k: a[k])
                          != max(range(3), key=lambda k: b[k]))
        out[arm] = {
            'accuracy': round(MT.accuracy(y_true, preds), 6),
            'log_loss': round(MT.log_loss(y_true, probs_all), 6),
            'brier': round(MT.brier(y_true, probs_all), 6),
            'verdict_flips': flips,
            'verdict_pairs': pairs,
            'flip_rate': round(flips / max(pairs, 1), 6),
        }
    return out


def adjudicate_corpus(paths, model_path=None, trajectory_path=TRAJECTORY_PATH,
                      log=print):
    """The E15 experiment over a PGN file or a directory of .pgn files."""
    t0 = time.time()
    games = RG._load_games(paths, log)
    if not games:
        raise SystemExit('no PGN games found under %r' % (paths,))
    payload = M.load_model(model_path or RG.MODEL_PATH)
    names, proba_fn, _ridge = FLS.load_heads(payload)
    gated, final_only = load_trajectory_models(trajectory_path)
    if gated.dim != len(names) or final_only.dim != len(names):
        raise SystemExit('trajectory model dim %d/%d != feature dim %d '
                         '(the E9 certificate does not match this '
                         'feature spec)' % (gated.dim, final_only.dim,
                                            len(names)))

    recs, skipped_no_entry = [], 0
    for g in games:
        try:
            rec = adjudicate_game(g, proba_fn, gated, final_only, names)
        except P.PGNError as exc:
            log('  %-34s FAILED REPLAY: %s'
                % (g.headers.get('_file', '?'), exc))
            continue
        if rec is None:
            skipped_no_entry += 1
            continue
        if rec['actual_cls'] is None:
            rec['scoreable'] = False
        else:
            rec['scoreable'] = True
            recs.append(rec)
        log('  %-34s %-15s result %-7s entries %2d'
            % (rec['file'], rec['source'], rec['result'], rec['n_entries']))

    scoreable = [r for r in recs if r['scoreable']]
    per_kind = {}
    for rec in recs:
        for k, n in rec['entries_per_kind'].items():
            per_kind[k] = per_kind.get(k, 0) + n
    curves = {arm: _curve(scoreable, arm) for arm in ARMS}
    finals = _final_summary(scoreable)
    report = {
        'certificate': 'E15 — whole-game adjudication (the E9 referee)',
        'recipe': {
            'corpus': paths,
            'model': os.path.basename(model_path or RG.MODEL_PATH),
            'trajectory': os.path.basename(trajectory_path),
            'arms': list(ARMS),
            'cutoffs': list(ADJ_TS),
            'ground_truth': 'the Result header at game level',
            'gate_time_axis': 'oracle-entry ordinal / %d' % TR.DEFAULT_HORIZON,
            'gate_dtm': 'exact oracle DTM of each entry (-1 for bare kings)',
            'note': 'pure evaluation of frozen artifacts; no retraining',
        },
        'totals': {
            'games': len(games),
            'games_in_oracle_space': len(recs),
            'games_scoreable': len(scoreable),
            'skipped_no_oracle_entries': skipped_no_entry,
            'oracle_entries': sum(r['n_entries'] for r in recs),
            'entries_per_kind': per_kind,
            'sources': {s: sum(1 for r in recs if r['source'] == s)
                        for s in sorted(set(r['source'] for r in recs))},
        },
        'adjudication_curves': curves,
        'final_entry': finals,
        'per_game': [{
            'file': r['file'], 'source': r['source'], 'result': r['result'],
            'n_entries': r['n_entries'], 'scoreable': r['scoreable'],
            'final_verdicts': {
                arm: max(range(3), key=lambda k:
                         r['probs'][arm][r['n_entries'] - 1])
                for arm in ARMS},
        } for r in recs],
        'runtime_seconds': round(time.time() - t0, 1),
    }
    return report
