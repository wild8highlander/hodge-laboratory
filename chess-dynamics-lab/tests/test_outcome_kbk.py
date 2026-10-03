#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the KBK certificate (v2): the diagonal negative control.
The lone-bishop mate does not exist — the frozen table must prove it,
and detect_domain must route lone-bishop positions there (the v1.5.0
KeyError regression)."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import tablebase_api as T          # noqa: E402
import dynamics as D                            # noqa: E402


def sq(name):
    return D.name_sq(name)


SAMPLE = [(sq('e4'), sq('d5'), sq('a5'), 0),
          (sq('a1'), sq('h8'), sq('a8'), 1),
          (sq('h1'), sq('f2'), sq('a8'), 0),
          (sq('b2'), sq('c3'), sq('a7'), 1)]


# ── known exact values ───────────────────────────────────────────────────
def test_kbk_is_a_draw_everywhere():
    # T15b: a lone-bishop mate does not exist — sampled states all draw
    for wk, wp, bk, stm in SAMPLE:
        r = T.probe_state('kbk', wk, wp, bk, stm)
        assert r['legal'] and r['outcome'] == 'draw' and r['dtm_plies'] is None


def test_kbk_blob_has_no_won_state():
    # the strongest form of the theorem: scan the WHOLE frozen blob
    tbl = T.load_table('kbk')
    assert not any(v != 200 for v in tbl['dtm'])


def test_kbk_illegal_shapes():
    # kings adjacent
    r = T.probe_state('kbk', sq('e4'), sq('a1'), sq('e5'), 0)
    assert r['outcome'] == 'illegal'
    # black king en prise with White to move
    r = T.probe_state('kbk', sq('g4'), sq('d7'), sq('e6'), 0)
    assert r['outcome'] == 'illegal'
    # overlap
    r = T.probe_state('kbk', sq('e4'), sq('e4'), sq('a8'), 0)
    assert r['outcome'] == 'illegal'


def test_kbk_classical_positions():
    # the a1-h8 corner cage: bishop on the long diagonal, king nearby —
    # still a draw in every configuration of this domain
    for wf, bf, bking in (('b3', 'a2', 'b1'), ('b3', 'a2', 'c1'),
                          ('f6', 'g7', 'h8')):
        for stm in (0, 1):
            r = T.probe_state('kbk', sq(wf), sq(bf), sq(bking), stm)
            if r['legal']:
                assert r['outcome'] == 'draw'


# ── domain detection (the v1.5.0 KeyError regression) ────────────────────
def test_detect_domain_bishop_is_kbk():
    pos = D.Position().set_fen('k7/8/8/8/8/4B2K/8/8 w - - 0 1')
    assert T.detect_domain(pos) == 'kbk'


def test_classify_fen_bishop_endgame():
    res = T.classify_fen('k7/8/8/8/8/4B2K/8/8 w - - 0 1')
    assert res['domain'] == 'kbk' and res['outcome'] == 'draw'


def test_kinds_contains_kbk_appended():
    # the v1 split indices must be preserved: kbk appended at the end
    assert T.KINDS == ('krk', 'kqk', 'knk', 'kpk', 'kbk')
    assert T.KIND_PIECE_CODE['kbk'] == D.WB
    assert T.KIND_PIECE_CHAR['kbk'] == 'B'
