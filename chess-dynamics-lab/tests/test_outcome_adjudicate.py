#!/usr/bin/env python3
"""tests/test_outcome_adjudicate.py — the E15 whole-game referee.

Covers: oracle-space step extraction on synthetic walk games, the
adjudication curve machinery, skip/scoreable accounting, determinism of
the frozen-artifact evaluation, and the dim-mismatch guard.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from outcome import adjudicate as ADJ
from outcome import features as F
from outcome import model as M
from outcome import pgn as P
from outcome import tablebase_api as T
from outcome import trajectory as TR

PROD_MODEL = os.path.join(T.RESULTS_DIR, 'outcome_model.json')
GAME_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'data', 'games')


def _walk_pgn(path, kind='krk', horizon=6, result='1-0'):
    """Freeze one seeded walk line into a tiny PGN file."""
    lines = TR.sample_lines([kind], 1, seed=3, horizon=horizon, log=None)
    line = lines[0]
    fens = [st['fen'] for st in line['steps']]
    sans = P.moves_between(fens)
    game = P.game_from_sans(fens[0], sans,
                            headers={'Result': result,
                                     'Source': 'tablebase-walk',
                                     'White': 'Walk', 'Black': 'Line',
                                     'SetUp': '1', 'FEN': fens[0]})
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(P.write_pgn([game]))
    return line


def test_game_steps_extracts_oracle_entries(tmp_path):
    line = _walk_pgn(os.path.join(str(tmp_path), 'w.pgn'))
    games = list(P.read_pgn_file(os.path.join(str(tmp_path), 'w.pgn')))
    game = games[0]
    names = list(F.FEATURE_NAMES)
    X, G, kinds, cls = ADJ.game_steps(game, names)
    assert len(X) == len(line['steps'])
    assert all(len(v) == len(names) for v in X)
    assert all(g[0] == i / float(TR.DEFAULT_HORIZON)
               for i, g in enumerate(G))
    assert all(-1.0 <= g[1] <= 1.0 for g in G)
    assert all(c is not None for c in cls)


def test_adjudicate_game_arms_and_skipping(tmp_path):
    path = os.path.join(str(tmp_path), 'w.pgn')
    _walk_pgn(path)
    games = list(P.read_pgn_file(path))
    payload = M.load_model(PROD_MODEL)
    from outcome import falsify as FLS
    names, proba_fn, _ = FLS.load_heads(payload)
    gated, final_only = ADJ.load_trajectory_models()
    rec = ADJ.adjudicate_game(games[0], proba_fn, gated, final_only, names)
    assert rec is not None
    assert set(rec['probs']) == set(ADJ.ARMS)
    n = rec['n_entries']
    for arm in ADJ.ARMS:
        assert len(rec['probs'][arm]) == n
    for p in rec['probs']['trajectory_gated']:
        assert abs(sum(p) - 1.0) < 1e-9
    assert rec['actual_cls'] == T.WHITE_WIN          # the walk ends in mate
    # a game that never enters the oracle space must be skipped
    classical = os.path.join(GAME_DIR, 'morphy_brunswick_1858.pgn')
    if os.path.exists(classical):
        cg = list(P.read_pgn_file(classical))[0]
        assert ADJ.adjudicate_game(cg, proba_fn, gated, final_only,
                                   names) is None


def test_cutoff_index_clamps():
    assert ADJ._cutoff_index(-1, 7) == 6
    assert ADJ._cutoff_index(0, 7) == 0
    assert ADJ._cutoff_index(20, 7) == 6
    assert ADJ._cutoff_index(3, 1) == 0


def test_curve_and_final_summary_shapes(tmp_path):
    path = os.path.join(str(tmp_path), 'w.pgn')
    _walk_pgn(path)
    report = ADJ.adjudicate_corpus(path, log=lambda *a: None)
    curves = report['adjudication_curves']
    assert set(curves) == set(ADJ.ARMS)
    for arm in ADJ.ARMS:
        assert set(curves[arm]) == {'0', '1', '2', '3', '5', '10', '20',
                                    'final'}
        for cell in curves[arm].values():
            assert cell['n'] == report['totals']['games_scoreable']
            assert 0.0 <= cell['accuracy'] <= 1.0
    finals = report['final_entry']
    assert finals['exact']['accuracy'] == 1.0         # the theorem
    assert finals['exact']['log_loss'] == 0.0
    assert finals['trajectory_gated']['accuracy'] == \
        curves['trajectory_gated']['final']['accuracy']
    # verdict flips are bounded by the number of consecutive pairs
    for arm in ADJ.ARMS:
        assert finals[arm]['verdict_flips'] <= finals[arm]['verdict_pairs']


def test_corpus_accounting_and_determinism(tmp_path):
    """Two runs over the same corpus must freeze identical reports."""
    out1 = os.path.join(str(tmp_path), 'r1.json')
    out2 = os.path.join(str(tmp_path), 'r2.json')
    argv1 = ['adjudicate', GAME_DIR, '--out', out1]
    argv2 = ['adjudicate', GAME_DIR, '--out', out2]
    from outcome import cli
    assert cli.main(argv1) == 0
    assert cli.main(argv2) == 0
    r1 = json.load(open(out1))
    r2 = json.load(open(out2))
    r1.pop('runtime_seconds'), r2.pop('runtime_seconds')
    assert r1 == r2
    totals = r1['totals']
    assert totals['games_scoreable'] + \
        totals['skipped_no_oracle_entries'] == totals['games']
    assert totals['oracle_entries'] > 0


def test_dim_mismatch_guard(tmp_path):
    """A trajectory certificate with the wrong dim must fail loudly."""
    fake = {'model_gated': {'pool': 'gated', 'dim': 5, 'epochs': 1,
                            'lr': 0.3, 'momentum': 0.9, 'l2': 1e-4,
                            'gate': [0.0, 0.0, 0.0],
                            'head': [[0.0] * 11 for _ in range(3)],
                            'mu': [0.0] * 5, 'sd': [1.0] * 5,
                            'loss_history': []},
            'model_final_only': {'pool': 'final', 'dim': 5, 'epochs': 1,
                                 'lr': 0.3, 'momentum': 0.9, 'l2': 1e-4,
                                 'gate': [0.0, 0.0, 0.0],
                                 'head': [[0.0] * 11 for _ in range(3)],
                                 'mu': [0.0] * 5, 'sd': [1.0] * 5,
                                 'loss_history': []}}
    bad = os.path.join(str(tmp_path), 'bad_traj.json')
    with open(bad, 'w', encoding='utf-8') as fh:
        json.dump(fake, fh)
    with pytest.raises(SystemExit):
        ADJ.adjudicate_corpus(GAME_DIR, trajectory_path=bad,
                              log=lambda *a: None)


def test_no_games_found(tmp_path):
    with pytest.raises(SystemExit):
        ADJ.adjudicate_corpus(str(tmp_path), log=lambda *a: None)
