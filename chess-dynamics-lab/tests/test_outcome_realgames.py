#!/usr/bin/env python3
"""tests/test_outcome_realgames.py — real games through Epoch IV (E12).

Covers: the player-context no-op contract on games without ratings,
the audit rows (exact / model / blended), the honesty check that the
audit pipeline reproduces model errors on known-hard states, scoring
and aggregation, and the CLI smoke over the bundled corpus.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

import dynamics as D
from outcome import context as CTX
from outcome import falsify as FLS
from outcome import model as M
from outcome import pgn as P
from outcome import realgames as RG
from outcome import tablebase_api as T

DATA_GAMES = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'data', 'games')
PROD_MODEL = os.path.join(T.RESULTS_DIR, 'outcome_model.json')


def _heads():
    payload = M.load_model(PROD_MODEL)
    return FLS.load_heads(payload)


# ── the context contract ─────────────────────────────────────────────────
def test_no_ratings_means_no_context():
    game = P.read_pgn_file(
        os.path.join(DATA_GAMES, 'reti_tartakower_1910.pgn'))[0]
    assert RG.game_player_context(game) is None


def test_ratings_become_a_player_context():
    game = P.Game({'WhiteElo': '2100', 'BlackElo': '1850'})
    ctx = RG.game_player_context(game)
    assert isinstance(ctx, CTX.PlayerContext)
    assert ctx.rating_delta() == 250.0


def test_bad_rating_headers_are_ignored():
    assert RG.game_player_context(P.Game({'WhiteElo': 'none',
                                          'BlackElo': '1850'})) is None
    assert RG.game_player_context(P.Game({'WhiteElo': '-3',
                                          'BlackElo': '1850'})) is None


# ── the audit rows ───────────────────────────────────────────────────────
def test_audit_positions_on_a_kpk_walk():
    names, proba, _ = _heads()
    root = '8/2P5/k7/4K3/8/8/8/8 w - - 0 1'
    game = P.Game({'Result': '1-0', 'Source': 'tablebase-walk',
                   'WhiteElo': '1650', 'BlackElo': '1400'}, root, [])
    # one legal move from the root (c8=Q)
    pos = D.Position().set_fen(root)
    game.sans = [P.san_of_move(pos, pos.legal_moves()[0])]
    rows, context_active = RG.audit_positions(game, proba, names)
    assert rows and context_active is True
    r0 = rows[0]
    assert r0['kind'] == 'kpk'
    assert r0['exact_cls'] in (T.WHITE_WIN, T.DRAW)
    assert abs(sum(r0['model_probs']) - 1.0) < 1e-6
    assert abs(sum(r0['blended_probs']) - 1.0) < 1e-6
    # the context blend moved the expected score toward the Elo prior
    s_model = r0['model_probs'][2] + 0.5 * r0['model_probs'][1]
    s_blend = r0['blended_probs'][2] + 0.5 * r0['blended_probs'][1]
    assert s_blend < s_model or abs(s_blend - s_model) < 1e-9  # prior 0.81


def test_audit_reproduces_model_errors_on_hard_states():
    """Honesty: the audit must NOT agree with the model on states E10
    recorded as hard errors (agreement there would mean a leak)."""
    import csv
    import random
    csv_path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'counterexamples',
        'counterexamples.csv')
    if not os.path.exists(csv_path):
        pytest.skip('counterexamples corpus not frozen')
    hard = []
    with open(csv_path) as fh:
        for r in csv.DictReader(fh):
            if 'hard_error' in (r.get('categories') or ''):
                hard.append(r['fen'])
    assert hard
    names, proba, _ = _heads()
    sample = random.Random(11).sample(hard, min(20, len(hard)))
    agree = 0
    for fen in sample:
        game = P.Game({'Result': '*'}, fen, [])
        rows, _ = RG.audit_positions(game, proba, names)
        assert len(rows) == 1
        pred = max(range(3), key=lambda k: rows[0]['model_probs'][k])
        agree += (pred == rows[0]['exact_cls'])
    assert agree < len(sample) // 2        # the model really is wrong there


def test_audit_skips_positions_outside_the_oracle():
    names, proba, _ = _heads()
    game = P.read_pgn_file(
        os.path.join(DATA_GAMES, 'morphy_brunswick_1858.pgn'))[0]
    rows, context_active = RG.audit_positions(game, proba, names)
    assert rows == [] and context_active is False


# ── scoring ──────────────────────────────────────────────────────────────
def test_score_rows_none_when_no_entries_or_no_result():
    assert RG.score_rows([], T.WHITE_WIN) is None
    rows = [{'exact_probs': [0.0, 0.0, 1.0], 'model_probs': [0.1, 0.1, 0.8],
             'blended_probs': [0.1, 0.1, 0.8]}]
    assert RG.score_rows(rows, None) is None


def test_score_rows_prefers_exact_truth():
    rows = [{'exact_probs': [0.0, 0.0, 1.0], 'model_probs': [0.6, 0.2, 0.2],
             'blended_probs': [0.6, 0.2, 0.2]}]
    s = RG.score_rows(rows, T.WHITE_WIN)
    assert s['exact']['log_loss'] == 0.0
    assert s['exact']['accuracy'] == 1.0
    assert s['model']['log_loss'] > s['exact']['log_loss']
    assert s['model_argmax_flips'] == 0


# ── the corpus audit (small, deterministic) ─────────────────────────────
def test_audit_corpus_end_to_end(tmp_path):
    class _Log:
        def __call__(self, *a):
            pass
    report, per_game = RG.audit_corpus(
        os.path.join(DATA_GAMES, 'walks_kpk.pgn'),
        model_path=PROD_MODEL, log=_Log())
    assert report['totals']['games'] == 12
    assert report['totals']['oracle_entries'] > 0
    assert report['position_level']['n_scored_positions'] > 0
    # every walk game carries sim ratings, so the context is active and
    # the corpus-level no-op share is 0 (documented behaviour)
    assert report['totals']['sources'] == {'tablebase-walk': 12}
    assert len(per_game) == 12
    for rec in per_game:
        assert rec['source'] == 'tablebase-walk'
        assert rec['plies'] > 0


def test_audit_corpus_flags_nothing_on_frozen_corpus():
    class _Log:
        def __call__(self, *a):
            pass
    report, _ = RG.audit_corpus(DATA_GAMES, model_path=PROD_MODEL,
                                log=_Log())
    assert report['flagged_results'] == []
    assert report['totals']['games'] >= 25
    human = report['totals']['sources'].get('human-classical', 0)
    assert human == 3


def test_cli_games_smoke(tmp_path):
    from outcome import cli
    args = type('A', (), {})()
    args.path = os.path.join(DATA_GAMES, 'walks_kqk.pgn')
    args.model = PROD_MODEL
    args.out = os.path.join(str(tmp_path), 'e12.json')
    rc = cli.cmd_games(args)
    assert rc == 0
    import json
    with open(args.out) as fh:
        report = json.load(fh)
    assert report['certificate'].startswith('E12')
