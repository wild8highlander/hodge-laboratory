#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Outcome Field v0.1: the exact-first design, entropy,
criticality, the trap detector and the extrapolation guard."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome.outcome_field import OutcomeField, entropy_bits   # noqa: E402
from outcome import tablebase_api as T                          # noqa: E402

MODEL_PATH = os.path.join(T.RESULTS_DIR, 'outcome_model.json')


@pytest.fixture(scope='module')
def field():
    return OutcomeField()


def test_entropy_bits_zero_and_max():
    assert entropy_bits([1.0, 0.0, 0.0]) == 0.0
    assert abs(entropy_bits([1.0 / 3] * 3) - 1.58496) < 1e-5


def test_exact_domain_mate(field):
    # the classical box: WK g6, Ra8, BK g8, Black to move — mate on board
    out = field.predict('R5k1/8/6K1/8/8/8/8/8 b - - 0 1')
    assert out['source'] == 'exact'
    assert out['domain'] == 'krk'
    assert out['outcome'] == 'white_win' and out['dtm_plies'] == 0
    assert out['probs'][T.WHITE_WIN] == 1.0
    assert out['entropy_bits'] == 0.0


def test_exact_domain_draw(field):
    out = field.predict('k7/R7/3K4/8/8/8/8/8 b - - 0 1')
    assert out['source'] == 'exact'
    assert out['outcome'] == 'draw'
    assert out['probs'][T.DRAW] == 1.0


def test_illegal_position_reported_honestly(field):
    # White to move with the black king en prise (Ra8 vs kg8)
    out = field.predict('R5k1/8/6K1/8/8/8/8/8 w - - 0 1')
    assert out['source'] == 'exact' and out['outcome'] == 'illegal'


def test_bare_kings_is_an_exact_draw(field):
    out = field.predict('8/8/8/8/8/8/1k6/K7 w - - 0 1')
    assert out['source'] == 'exact' and out['domain'] == 'kk'
    assert out['outcome'] == 'draw'


def test_trap_detection_in_drawn_krk(field):
    # drawn BTM KRK; 1...Ka2? walks into the mating net — the single
    # critical move the census-style surface must expose
    out = field.predict('8/3K4/8/8/8/8/8/kR6 b - - 0 1', with_moves=True)
    assert out['outcome'] == 'draw'
    assert out['criticality'] == 1.0
    assert out['critical_move'] == 'a1a2'
    traps = [m for m in out['moves'] if m['probs'] and
             m['probs'][T.WHITE_WIN] == 1.0]
    assert len(traps) == 1 and traps[0]['uci'] == 'a1a2'


def test_move_surface_covers_all_moves(field):
    out = field.predict('8/3K4/8/8/8/8/8/kR6 b - - 0 1', with_moves=True)
    assert out['moves'] is not None
    assert all(m['probs'] is not None for m in out['moves'])
    assert all(abs(sum(m['probs']) - 1.0) < 1e-9 for m in out['moves'])


@pytest.mark.skipif(not os.path.exists(MODEL_PATH),
                    reason='frozen outcome model not present')
def test_model_fallback_is_flagged_as_extrapolation(field):
    # a 32-piece middlegame is outside the tablebase-only training domain:
    # the field must be reported with the honest extrapolation flag
    out = field.predict(
        'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3')
    assert out['source'] == 'model'
    assert out['extrapolation'] is True
    assert abs(sum(out['probs']) - 1.0) < 1e-9


@pytest.mark.skipif(not os.path.exists(MODEL_PATH),
                    reason='frozen outcome model not present')
def test_frozen_model_matches_certificate():
    # the evaluate command re-derives the frozen pooled accuracy
    import io
    import contextlib
    from outcome import cli
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(['evaluate'])
    assert rc == 0
    assert 'MATCHES THE FROZEN CERTIFICATE' in buf.getvalue()
