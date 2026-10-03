#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Move Impact module: the counterfactual surface, the
pace economics on exact won parents, robustness on draws."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import impact as IMP              # noqa: E402
from outcome import tablebase_api as T         # noqa: E402
from outcome.outcome_field import OutcomeField  # noqa: E402
import dynamics as D                            # noqa: E402


def sq(name):
    return D.name_sq(name)


FIELD = OutcomeField()


def test_surface_on_mate_in_one():
    # WK g6, Ra7, BK g8, WTM: Ra8# is mate in 1 ply (parent dtm = 1)
    pos = D.Position().set_fen('6k1/R7/6K1/8/8/8/8/8 w - - 0 1')
    probe = T.probe_state('krk', sq('g6'), sq('a7'), sq('g8'), 0)
    assert probe['outcome'] == 'white_win' and probe['dtm_plies'] == 1
    rows = IMP.move_impact_surface(FIELD, pos)
    assert rows
    exact = FIELD._exact(pos)
    parent_dtm = exact[1]['dtm_plies']
    assert parent_dtm == 1
    # every child stays won: d_white_win == 0, all quiet, robustness 1
    for r in rows:
        if r['probs'] is None:
            continue
        assert r['d_white_win'] == 0.0
        assert r['category'] == 'quiet'
    summary = IMP.summarize(rows, [0.0, 0.0, 1.0], parent_dtm)
    assert summary['robustness_index'] == 1.0
    # degenerate dW: the field-vs-dtm agreement is honestly undefined
    assert summary['best_move_agreement'] is None
    # pace economics: the mating move keeps the optimal tempo (+1)
    assert summary['max_pace'] == 1
    assert summary['optimal_pace_moves'] >= 1


def _won_root(min_dtm=4):
    """Any legal WTM KRK state with DTM >= min_dtm (scanned from the
    table, not guessed)."""
    for wk in D.SQUARES:
        for wr in D.SQUARES:
            if wr == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wr or T.kings_adjacent(wk, bk):
                    continue
                p = T.probe_state('krk', wk, wr, bk, 0)
                if p['legal'] and p['dtm_plies'] is not None \
                        and p['dtm_plies'] >= min_dtm:
                    return (wk, wr, bk, 0), p['dtm_plies']
    return None, None


def test_pace_never_negative_for_optimal_child():
    # a longer KRK win: the argmin child DTM is exactly parent-1
    root, parent_dtm = _won_root(4)
    assert root is not None
    pos = D.Position().set_fen(T.state_to_fen('krk', *root))
    rows = IMP.move_impact_surface(FIELD, pos)
    child_dtms = [r['dtm_child'] for r in rows
                  if r['dtm_child'] is not None and r['dtm_child'] >= 0]
    assert min(child_dtms) == parent_dtm - 1
    paces = [r['pace'] for r in rows if r['pace'] is not None]
    assert max(paces) == 1


def test_drawn_parent_full_robustness():
    # a drawn KRK: no move can change the theorem
    pos = D.Position().set_fen('8/8/8/3k4/8/3K4/8/8 w - - 0 1')  # K vs K
    rows = IMP.move_impact_surface(FIELD, pos)
    assert rows == [] or all(r['probs'] is not None for r in rows)
    if rows:
        summary = IMP.summarize(rows, [0.0, 1.0, 0.0], None)
        assert summary['robustness_index'] == 1.0


def test_surface_sorted_and_complete():
    root, _ = _won_root(4)
    assert root is not None
    pos = D.Position().set_fen(T.state_to_fen('krk', *root))
    rows = IMP.move_impact_surface(FIELD, pos)
    n_legal = len(pos.legal_moves())
    assert len(rows) == n_legal
    dws = [r['d_white_win'] for r in rows if r['d_white_win'] is not None]
    # the module sorts by descending d_white_win (the v1 panel re-sorts)
    assert dws == sorted(dws, reverse=True)
