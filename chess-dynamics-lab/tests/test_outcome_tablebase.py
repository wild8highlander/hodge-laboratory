#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the exact outcome oracle (Epoch I): probes, legality,
domain detection and the live census cross-check against the frozen
builder statistics."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import tablebase_api as T          # noqa: E402
import dynamics as D                            # noqa: E402


def sq(name):
    return D.name_sq(name)


KNIGHT_SAMPLE = [(sq('e4'), sq('d5'), sq('e6'), 0),
                 (sq('a1'), sq('b3'), sq('h8'), 1),
                 (sq('h1'), sq('f2'), sq('a8'), 0)]


# ── known exact values ───────────────────────────────────────────────────
def test_krk_box_mate_btm():
    # WK g6, Ra8, BK g8, Black to move: checkmate is on the board
    r = T.probe_state('krk', sq('g6'), sq('a8'), sq('g8'), 1)
    assert r['legal'] and r['outcome'] == 'white_win' and r['dtm_plies'] == 0


def test_krk_box_wtm_is_illegal():
    # the same placement with White to move: black king en prise
    r = T.probe_state('krk', sq('g6'), sq('a8'), sq('g8'), 0)
    assert r['outcome'] == 'illegal' and not r['legal']


def test_krk_mate_in_one():
    # WK g6, Ra7, BK g8, White to move: Ra8# — mate in 1 ply
    r = T.probe_state('krk', sq('g6'), sq('a7'), sq('g8'), 0)
    assert r['outcome'] == 'white_win' and r['dtm_plies'] == 1


def test_kpk_textbook_win():
    # Ke6 + Pe5 vs ke8, White to move: the classic king-ahead-of-pawn win
    r = T.probe_state('kpk', sq('e6'), sq('e5'), sq('e8'), 0)
    assert r['outcome'] == 'white_win' and r['dtm_plies'] == 21


def test_kpk_textbook_draw():
    # Ke1 + Pe2 vs ke5: the black king catches the pawn — draw
    r = T.probe_state('kpk', sq('e1'), sq('e2'), sq('e5'), 0)
    assert r['outcome'] == 'draw' and r['dtm_plies'] is None


def test_knk_is_a_draw_everywhere():
    # T15: a knight mate does not exist — sampled KNK states are all draws
    for wk, wp, bk, stm in KNIGHT_SAMPLE:
        r = T.probe_state('knk', wk, wp, bk, stm)
        assert r['outcome'] == 'draw'


def test_kings_adjacent_is_illegal():
    r = T.probe_state('krk', sq('e4'), sq('a1'), sq('e5'), 0)
    assert r['outcome'] == 'illegal'
    r = T.probe_state('kqk', sq('d4'), sq('a2'), sq('d5'), 1)
    assert r['outcome'] == 'illegal'


def test_pawn_on_back_ranks_is_outside_the_space():
    # the builders enumerate the pawn on ranks 2..7 only (0x88 ranks 1..6)
    assert not T.pawn_rank_ok(sq('a1'))
    assert not T.pawn_rank_ok(sq('a8'))
    assert T.pawn_rank_ok(sq('a2')) and T.pawn_rank_ok(sq('a7'))
    r = T.probe_state('kpk', sq('e4'), sq('a8'), sq('c6'), 0)
    assert r['outcome'] == 'illegal'


# ── domain detection ─────────────────────────────────────────────────────
def test_classify_fen_endgame():
    res = T.classify_fen('3k4/8/4K3/4P3/8/8/8/8 w - - 0 1')
    assert res['domain'] == 'kpk' and res['outcome'] == 'white_win'


def test_classify_fen_full_chess_is_unknown():
    res = T.classify_fen(
        'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3')
    assert res['domain'] is None and res['outcome'] == 'unknown'


def test_state_fen_round_trip():
    for wk, wp, bk, stm in KNIGHT_SAMPLE:
        fen = T.state_to_fen('knk', wk, wp, bk, stm)
        pos = D.Position().set_fen(fen)
        kind = T.detect_domain(pos)
        assert kind == 'knk'
        assert pos.king_sq(1) == wk and pos.king_sq(-1) == bk


# ── the live census cross-check (repo convention: fix code, not files) ──
def test_census_knk_matches_frozen_stats():
    # the cheapest full census (knight attacks are a lookup)
    live = T.census_kind('knk')
    frozen = T.load_table('knk')['stats']
    assert live['legal_states'] == frozen['states']
    assert live['won_states'] == frozen['won'] == 0
