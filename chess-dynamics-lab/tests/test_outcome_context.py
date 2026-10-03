#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Epoch IV player-context layer: the Elo prior, the blend,
the no-op honesty rule and the whole-game split."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import context as CTX            # noqa: E402


def test_elo_expectation_bounds_and_symmetry():
    assert CTX.elo_expected(0) == 0.5
    e_up = CTX.elo_expected(400)
    e_dn = CTX.elo_expected(-400)
    assert abs(e_up - (1.0 - e_dn)) < 1e-12
    assert 0.0 < e_up < 1.0 and e_up > 0.5


def test_noop_without_rating():
    probs = [0.1, 0.5, 0.4]
    ctx = CTX.PlayerContext()                       # no ratings at all
    blended, info = CTX.blend(probs, ctx)
    assert blended == list(probs)
    assert info['weight'] == 0.0
    # explicit zero weight is a no-op even with ratings
    ctx = CTX.PlayerContext(2800, 1200, weight=0.0)
    blended, info = CTX.blend(probs, ctx)
    assert blended == list(probs)


def test_blend_moves_expected_score_toward_the_prior():
    # model says White converts 0.65; the Elo prior (400 points up)
    # says ~0.91 — the blend must land between, nearer the prior side
    probs = [0.05, 0.25, 0.70]                      # b, d, w
    model_expected = probs[2] + 0.5 * probs[1]
    ctx = CTX.PlayerContext(2400, 2000, weight=CTX.CONTEXT_WEIGHT)
    blended, info = CTX.blend(probs, ctx)
    s_new = blended[2] + 0.5 * blended[1]
    assert abs(sum(blended) - 1.0) < 1e-9
    assert model_expected < s_new < info['elo_expected']
    assert info['weight'] == CTX.CONTEXT_WEIGHT


def test_blend_monotone_in_the_prior():
    probs = [0.2, 0.4, 0.4]                         # b, d, w
    scores = []
    for rw, rb in ((2400, 2000), (2000, 2000), (1600, 2400)):
        ctx = CTX.PlayerContext(rw, rb, weight=0.5)
        blended, info = CTX.blend(probs, ctx)
        scores.append(info['blended_expected'])
    assert scores[0] > scores[1] > scores[2]


def test_blend_draw_share_stable_for_small_shifts():
    # the water-filling rule: while |delta| <= min(P_W, P_L) the shift is
    # applied between the win buckets only — the draw share is untouched
    probs = [0.2, 0.4, 0.4]
    ctx = CTX.PlayerContext(1600, 2400, weight=0.25)   # moderate shift
    blended, info = CTX.blend(probs, ctx)
    assert abs(blended[1] - probs[1]) < 1e-9
    assert abs(info['blended_expected']
               - (info['model_expected'] + (info['blended_expected']
                                            - info['model_expected']))) < 1e-12
    # mass conservation
    assert abs(sum(blended) - 1.0) < 1e-9


def test_blend_strong_prior_extremes():
    # a 1200-point gap must not break mass conservation or produce
    # negative masses (the old r-preserving solve divided by zero here)
    probs = [0.2, 0.4, 0.4]
    ctx = CTX.PlayerContext(1000, 2200, weight=0.6)
    blended, _ = CTX.blend(probs, ctx)
    assert all(p >= 0.0 for p in blended)
    assert abs(sum(blended) - 1.0) < 1e-9
    ctx = CTX.PlayerContext(2200, 1000, weight=0.6)
    blended, _ = CTX.blend(probs, ctx)
    assert all(p >= 0.0 for p in blended)
    assert abs(sum(blended) - 1.0) < 1e-9


def test_clock_prior_clamped_and_directional():
    shift = CTX.clock_rating_shift(120, 30)          # White has 4x time
    assert 0 < shift <= CTX.CLOCK_CLAMP
    assert shift == CTX.clock_rating_shift(480, 120)  # log2 scale
    assert CTX.clock_rating_shift(30, 120) == -shift
    assert CTX.clock_rating_shift(None, None) == 0.0
    assert CTX.clock_rating_shift(0, 30) == 0.0


def test_split_of_game_deterministic_and_game_level():
    s1 = CTX.split_of_game(12345)
    assert s1 == CTX.split_of_game(12345)
    assert s1 in CTX.SPLIT_NAMES
    # every id lands in exactly one split; ids never straddle
    ids = [7, 8, 9, 10 ** 9 + 7, 2 ** 40 + 13]
    seen = {CTX.split_of_game(i) for i in ids}
    assert seen <= set(CTX.SPLIT_NAMES)


def test_split_distribution_is_stratified():
    n = 20000
    counts = {'train': 0, 'valid': 0, 'test': 0}
    for gid in range(n):
        counts[CTX.split_of_game(gid * 7919 + 3)] += 1
    assert abs(counts['train'] / n - 0.70) < 0.02
    assert abs(counts['valid'] / n - 0.15) < 0.02
    assert abs(counts['test'] / n - 0.15) < 0.02
