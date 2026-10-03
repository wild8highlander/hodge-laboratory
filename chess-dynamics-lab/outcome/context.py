#!/usr/bin/env python3
"""outcome/context.py — the Bayesian player-context layer (Epoch IV).

The exact layer of the Outcome Field is a theorem and does not care who
is at the board.  The MODEL layer, however, is a forecast of *practical
conversion* — and practical conversion depends on the players: the same
theoretically-drawn position converts more often for the stronger (or
better-prepared) side.  This module implements the program's Epoch IV
prior without fabricating any data:

    P_final = blend( P_model, Elo prior of the rating gap )

The blend is a two-step Bayesian-flavoured operation:

1.  Expected scores.  The model's distribution implies the expected
    score  s_model = P_W + 0.5·P_D.  The classical Elo formula implies
    the prior  s_elo = 1/(1+10^(-ΔR/400))  for the rating gap ΔR
    (optionally shifted by a documented clock prior).
2.  Redistribution.  The blended expected score
    s' = (1−w)·s_model + w·s_elo   (w = context weight, capped)
    is re-expanded to a full (P_W, P_D, P_L) by preserving the model's
    *decisive share* r = P_W/(P_W+P_L): the context moves the expected
    score, it does not invent draw propensity.

Honesty rules:

*  No player database, no invented statistics: the layer ships with
   three constants (CONTEXT_WEIGHT, CLOCK_ELO_PER_DOUBLING, CLOCK_CLAMP)
   documented as priors, and w = 0 (a strict no-op) whenever no rating
   information is supplied.
*  Game-level splits: when whole games (not tablebase states) are
   trained on, neighbouring plies of one game are near-duplicates; the
   split must therefore be lifted to whole games.  split_of_game()
   provides the deterministic hash split; a unit test pins that one
   game's positions never straddle two splits.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402

# ── frozen priors (documented, not fitted) ───────────────────────────────
CONTEXT_WEIGHT = 0.25       # default trust in the Elo prior
WEIGHT_CAP = 0.6            # never let the prior dominate the model
CLOCK_ELO_PER_DOUBLING = 30.0   # Elo shift per doubled clock ratio
CLOCK_CLAMP = 150.0         # max Elo shift from the clock prior
EPS = 1e-6

SPLIT_THRESHOLDS = (700, 850)       # <700 train, <850 valid, else test
SPLIT_NAMES = ('train', 'valid', 'test')


def elo_expected(rating_delta):
    """Classical Elo expectation of White's score for a rating gap."""
    return 1.0 / (1.0 + 10.0 ** (-rating_delta / 400.0))


def clock_rating_shift(clock_white, clock_black):
    """Documented clock prior: the side with the larger remaining clock
    is 'effectively stronger' by CLOCK_ELO_PER_DOUBLING Elo per doubled
    time ratio, clamped to ±CLOCK_CLAMP.  Returns the shift in Elo."""
    if not clock_white or not clock_black or clock_white <= 0 \
            or clock_black <= 0:
        return 0.0
    ratio = max(clock_white / clock_black, clock_black / clock_white)
    shift = CLOCK_ELO_PER_DOUBLING * math.log2(max(ratio, 1.0))
    shift = min(shift, CLOCK_CLAMP)
    return shift if clock_white > clock_black else -shift


class PlayerContext:
    """Who is at the board: ratings, clocks, prior weight."""

    def __init__(self, rating_white=None, rating_black=None,
                 clock_white=None, clock_black=None, weight=CONTEXT_WEIGHT):
        self.rating_white = rating_white
        self.rating_black = rating_black
        self.clock_white = clock_white
        self.clock_black = clock_black
        self.weight = min(max(weight, 0.0), WEIGHT_CAP)

    @classmethod
    def from_dict(cls, d):
        return cls(d.get('rating_white'), d.get('rating_black'),
                   d.get('clock_white'), d.get('clock_black'),
                   d.get('weight', CONTEXT_WEIGHT))

    def has_rating(self):
        return self.rating_white is not None and self.rating_black is not None

    def rating_delta(self):
        if not self.has_rating():
            return 0.0
        return (self.rating_white - self.rating_black
                + clock_rating_shift(self.clock_white, self.clock_black))

    def label(self):
        if not self.has_rating():
            return 'player context · no rating prior (no-op)'
        parts = ['Elo %d vs %d' % (self.rating_white, self.rating_black)]
        shift = clock_rating_shift(self.clock_white, self.clock_black)
        if shift:
            parts.append('clock shift %+d' % round(shift))
        return 'player context · %s' % ', '.join(parts)

    def to_dict(self):
        return {'rating_white': self.rating_white,
                'rating_black': self.rating_black,
                'clock_white': self.clock_white,
                'clock_black': self.clock_black,
                'weight': self.weight}


def blend(model_probs, ctx):
    """Blend the model layer with the context prior (water-filling).

    The expected-score shift  delta = s' − s_model  is applied in the
    documented water-filling order: first between the two win buckets
    (the draw share is untouched while  |delta| <= min(P_W, P_L)), and
    any excess pours into the draw bucket.  Mass is conserved exactly
    and the map is monotone in the prior.  A no-op
    (info['weight'] = 0.0) when the context carries no rating
    information or the weight is 0."""
    pw, pd, pl = model_probs[T.WHITE_WIN], model_probs[T.DRAW], \
        model_probs[T.BLACK_WIN]
    model_expected = pw + 0.5 * pd
    if ctx is None or not ctx.has_rating() or ctx.weight <= 0.0:
        return list(model_probs), {
            'label': (ctx.label() if ctx else 'no context'),
            'model_expected': round(model_expected, 6),
            'blended_expected': round(model_expected, 6),
            'elo_expected': None,
            'weight': 0.0,
        }
    s_elo = elo_expected(ctx.rating_delta())
    w = ctx.weight
    s_new = (1.0 - w) * model_expected + w * s_elo
    s_new = min(max(s_new, 0.0), 1.0)
    delta = s_new - model_expected
    pw2, pd2, pl2 = pw, pd, pl
    if delta > 0.0:                    # White should score more
        take = min(delta, pl2)         # moving x of mass shifts s by x
        pw2 += take
        pl2 -= take
        delta -= take
        if delta > 1e-12:              # excess pours into the draw bucket
            take = min(2.0 * delta, pd2)   # moving x raises s by x/2
            pw2 += take
            pd2 -= take
    elif delta < 0.0:                  # Black should score more
        delta = -delta
        take = min(delta, pw2)
        pl2 += take
        pw2 -= take
        delta -= take
        if delta > 1e-12:
            take = min(2.0 * delta, pd2)
            pl2 += take
            pd2 -= take
    total = pw2 + pd2 + pl2
    blended = [pl2 / total, pd2 / total, pw2 / total]
    info = {
        'label': ctx.label(),
        'model_expected': round(model_expected, 6),
        'blended_expected': round(s_new, 6),
        'elo_expected': round(s_elo, 6),
        'weight': round(w, 6),
    }
    return blended, info


def split_of_game(game_id):
    """Deterministic whole-game split (the Epoch IV leakage rule).

    Hash the game id with splitmix64; the same thresholds as the state
    split apply (70/15/10).  Every position of one game lands in the
    same split — neighbouring plies (near-duplicates) can never leak
    across the train/test boundary."""
    h = D.splitmix64(int(game_id) & 0xFFFFFFFFFFFFFFFF)
    bucket = h % 1000
    if bucket < SPLIT_THRESHOLDS[0]:
        return 'train'
    if bucket < SPLIT_THRESHOLDS[1]:
        return 'valid'
    return 'test'


def assign_game_splits(game_ids):
    """{game_id: split} for an iterable of game ids."""
    return {gid: split_of_game(gid) for gid in game_ids}
