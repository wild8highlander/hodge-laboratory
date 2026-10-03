# -*- coding: utf-8 -*-
"""E5 — the solution-level ladder (note N2 companion).

The frozen report must agree with the live tables on the three solution
levels, and the E3 cross-check must hold: two independent implementations
of the minimal-strategy-tree recursion produce one number (500,900 nodes
for the hardest KRK position).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'vortex'))

from vortex import vortex_dynamics as V          # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from solve_levels_e5 import sq, probe, walk_pv, tree_size  # noqa: E402

REPORT = json.load(open(os.path.join(
    ROOT, 'results', 'solve_levels_e5.json')))


def test_strong_coverage_is_total():
    """Strong level: every legal state of every space is valued."""
    for kind, row in REPORT['strong'].items():
        assert row['won'] + row['drawn'] == row['states']
        assert row['coverage'] == 1.0
        assert row['bellman_verified']


def test_ultra_weak_anchors_all_pass():
    """Every classical doctrine anchor holds against the frozen tables."""
    assert REPORT['ultra_weak']['anchors']
    for a in REPORT['ultra_weak']['anchors']:
        assert a['pass'], a
        assert a['expected'] == a['probed']
    knk = REPORT['ultra_weak']['knk_universal_draw']
    assert knk['won_states'] == 0


def test_weak_lines_reach_mate_at_exact_dtm():
    """Weak level: PV length equals DTM and the tree fits the space."""
    for s in REPORT['weak']['starts']:
        assert s['pv_length'] == s['dtm_plies']
        assert s['strategy_tree']['nodes'] > 0
        assert s['strategy_tree']['share_of_space'] < 0.05


def test_e3_cross_check_match():
    """The hardest KRK tree: two implementations, one number."""
    cross = REPORT['weak']['e3_argmax_cross_check']
    assert cross['match']
    assert cross['tree_nodes_recomputed'] == 500900
    assert cross['tree_nodes_frozen_e3'] == 500900


def test_live_probe_and_walk_still_agree():
    """Live recomputation (not just the frozen JSON): the oracle box."""
    assert probe('krk', 'c2', 'b4', 'c8', 0) == 19
    pv = walk_pv('krk', 'c2', 'b4', 'c8', 0)
    assert len(pv) == 19
    assert all(len(m) == 4 for m in pv)       # 'from''to' moves
    assert len(set(pv[::2])) == len(pv[::2])  # no repeated White moves
    tree = tree_size('krk', 'c2', 'b4', 'c8', 0)
    frozen = [s for s in REPORT['weak']['starts'] if s['kind'] == 'krk'][0]
    assert tree['nodes'] == frozen['strategy_tree']['nodes']


def test_deepest_states_match_table_headers():
    """The argmax scan must reproduce the frozen max DTM per space."""
    for kind, row in REPORT['deepest'].items():
        header_max = REPORT['strong'][kind]['max_dtm_plies']
        vals = [row[side]['dtm_plies'] for side in ('wtm', 'btm')]
        vals = [v for v in vals if v is not None]
        if not vals:
            assert header_max == 0
        else:
            assert max(vals) == header_max
