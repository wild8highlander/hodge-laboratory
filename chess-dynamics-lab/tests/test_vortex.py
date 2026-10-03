#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the vortex layer (T16): field construction, flow classifier,
agreement with the frozen DTM certificates."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'vortex'))

from vortex import vortex_dynamics as V          # noqa: E402


def sq(name):
    return (ord(name[0]) - 97) + 16 * (int(name[1]) - 1)


def field(kind, wks, wps, bks, stm):
    return V.build_field(kind, sq(wks), sq(wps), sq(bks), stm)


# ── table integrity ──────────────────────────────────────────────────────
def test_load_frozen_all_kinds():
    for kind in V.KINDS:
        entry = V.load_frozen(kind)
        assert len(entry['dtm']) == V.SIZE
        assert entry['bellman_verified'] is True


def test_probe_draw_and_mate():
    dtm = V.load_frozen('krk')['dtm']
    assert V.probe('krk', V.pack('krk', 0, 1, 2, 0)) == -1  # kings adjacent
    # the classical box mate: WK g6, Ra8, BK g8, BTM
    assert V.probe('krk', V.pack('krk', sq('g6'), sq('a8'),
                                 sq('g8'), 1)) == 0


# ── field construction (T16 structural criterion) ───────────────────────
def test_krk_mate_in_two_wtm_is_win_with_descent():
    f = field('krk', 'g6', 'h1', 'g8', 0)
    assert f['verdict'] == 'WIN'
    assert f['descents'] >= 1
    assert f['dtm'] == 3
    # the mating net includes the rook hang as an escape current
    tags = [t for (_, _, _, t) in f['currents']]
    assert 'escape' in tags or 'descent' in tags


def test_krk_btm_same_pieces_is_loss():
    f = field('krk', 'g6', 'h1', 'g8', 1)
    assert f['verdict'] == 'LOSS'
    assert f['escapes'] == 0
    assert f['descents'] == len(f['currents']) > 0   # every defence feeds the net


def test_knk_is_pure_rotation_both_stms():
    for stm in (0, 1):
        f = field('knk', 'd3', 'c1', 'b5', stm)
        assert f['verdict'] == 'DRAW'
        assert f['descents'] == 0                 # no current anywhere


def test_kpk_wtm_drawn_exists():
    # doctrine: the opposition draw with the pawn on e5 (frozen: d5/e6/d8)
    f = field('kpk', 'd6', 'e5', 'e8', 0)
    assert f['verdict'] in ('DRAW', 'WIN')        # value from the table


def test_illegal_wtm_state_raises():
    # Qh1 attacks a8 along the diagonal: WTM would be illegal
    with pytest.raises(ValueError):
        field('kqk', 'b6', 'h1', 'a8', 0)


def test_mate_on_board_is_terminal_loss():
    # the first frozen KRK mate: a BTM state with dtm 0
    dtm = V.load_frozen('krk')['dtm']
    mate = next(s for s in range(V.SIZE) if dtm[s] == 0)
    wk, wp, bk, stm = V.unpack(mate)
    f = V.build_field('krk', wk, wp, bk, stm)
    assert f['verdict'] == 'LOSS'
    assert f['currents'] == []


# ── flow classification (measured, not probed) ───────────────────────────
def test_flow_classifier_matches_verdict_doctrine():
    cases = [('krk', 'g6', 'h1', 'g8', 0), ('krk', 'g6', 'h1', 'g8', 1),
             ('krk', 'b6', 'h7', 'a8', 0), ('krk', 'b6', 'h7', 'a8', 1),
             ('knk', 'd3', 'c1', 'b5', 0), ('knk', 'd3', 'c1', 'b5', 1),
             ('kqk', 'b6', 'b1', 'h8', 0), ('kqk', 'b6', 'b1', 'h8', 1)]
    for kind, a, b, c, stm in cases:
        f = field(kind, a, b, c, stm)
        m = V.simulate(f)
        assert V.classify_by_flow(f, m) == f['verdict']


def test_capture_separation():
    f_win = field('krk', 'b6', 'h7', 'a8', 0)
    m_win = V.simulate(f_win)
    assert m_win['capture_fraction'] >= V.FROZEN_VORTEX['win_capture_min']
    f_loss = field('krk', 'b6', 'h7', 'a8', 1)
    m_loss = V.simulate(f_loss)
    assert m_loss['capture_fraction'] >= V.FROZEN_VORTEX['win_capture_min']
    f_draw = field('knk', 'd3', 'c1', 'b5', 0)
    m_draw = V.simulate(f_draw)
    assert m_draw['capture_fraction'] == 0.0      # pure rotation: nothing
    # ever reaches a target, because no forced current exists


def test_promotion_boundary_through_kqk():
    # frozen anchor (exact table scan): WK a1, Pa7, BK c1, WTM — the
    # promotion child is a KQK state valued 10, parent dtm 11, so the
    # promotion move is a descent current with J = 1
    f = field('kpk', 'a1', 'a7', 'c1', 0)
    assert f['verdict'] == 'WIN'
    desc = [(t, J) for (_, t, J, tag) in f['currents'] if tag == 'descent']
    assert desc and max(J for (_, J) in desc) >= 1
    # the promotion target square (a8 = 112) is among the descent targets
    assert 112 in [t for (t, _) in desc]
    m = V.simulate(f)
    assert V.classify_by_flow(f, m) == 'WIN'


def test_minimal_sample_agreement():
    """A small seeded agreement run (the E4 protocol, reduced)."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    from vortex_e4 import run_class, class_counts
    total = agreed = 0
    for kind in V.KINDS:
        counts = class_counts(kind)
        for want, n in (('wtm_won', 12), ('wtm_drawn', 12),
                        ('btm_won', 12), ('btm_drawn', 12)):
            if counts[want] == 0:
                continue
            rows = run_class(kind, want, n, seed=0xC0FFEE)
            total += len(rows)
            agreed += sum(r['agree'] for r in rows)
    assert total > 0
    assert agreed == total                         # 100%, as in frozen E4
