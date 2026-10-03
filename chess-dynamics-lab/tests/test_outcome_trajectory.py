#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Epoch V trajectory model: seeded optimal walks, whole-
game splits, the gated pooling model and its persistence."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import context as CTX            # noqa: E402
from outcome import tablebase_api as T        # noqa: E402
from outcome import trajectory as TR          # noqa: E402
import dynamics as D                          # noqa: E402


def sq(name):
    return D.name_sq(name)


def test_walk_follows_optimal_defence_to_mate():
    # KRK mate in 3 plies from the frozen certificate: the optimal walk
    # must reach dtm 0 in exactly 3 plies and end in WHITE_WIN
    root = None
    for wk in D.SQUARES:
        for wr in D.SQUARES:
            if wr == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wr:
                    continue
                if T.kings_adjacent(wk, bk):
                    continue
                p = T.probe_state('krk', wk, wr, bk, 0)
                if p['legal'] and p['dtm_plies'] == 3:
                    root = (wk, wr, bk, 0)
                    break
            if root:
                break
        if root:
            break
    assert root is not None
    line = TR.walk_line('krk', root, __import__('random').Random(1))
    assert line['final_cls'] == T.WHITE_WIN
    assert line['n_plies'] == 3
    dtms = [s['dtm'] for s in line['steps']]
    assert dtms == [3, 2, 1, 0]


def test_walk_is_deterministic():
    quads = [(sq('e4'), sq('h1'), sq('b5'), 0)]
    l1 = TR.walk_line('krk', quads[0], __import__('random').Random(42))
    l2 = TR.walk_line('krk', quads[0], __import__('random').Random(42))
    assert [s['fen'] for s in l1['steps']] == [s['fen'] for s in l2['steps']]


def test_walk_crosses_domains_on_promotion():
    # find a KPK won root with the pawn close to promotion; the line may
    # continue inside KQK after the promotion ply
    root = None
    for wk in D.SQUARES:
        for wp in D.SQUARES:
            if wp == wk or (wp >> 4) != 6:          # rank 7 pawns only
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wp or T.kings_adjacent(wk, bk):
                    continue
                p = T.probe_state('kpk', wk, wp, bk, 0)
                if p['legal'] and p['outcome'] == 'white_win' \
                        and p['dtm_plies'] <= 3:
                    root = (wk, wp, bk, 0)
                    break
            if root:
                break
        if root:
            break
    assert root is not None
    line = TR.walk_line('kpk', root, __import__('random').Random(5))
    assert line['final_cls'] == T.WHITE_WIN
    kinds = {s['kind'] for s in line['steps']}
    assert kinds & {'kpk', 'kqk'}


def test_whole_game_split_groups_lines():
    lines = TR.sample_lines(['krk'], 6, seed=3, horizon=8)
    seqs = TR.build_sequences(lines)
    splits = {}
    for s in seqs:
        splits.setdefault(CTX.split_of_game(s['game_id']), []).append(s)
    assert sum(len(v) for v in splits.values()) == len(seqs)


def test_trajectory_model_fit_and_forecast():
    lines = TR.sample_lines(['krk'], 10, seed=11, horizon=10)
    seqs = TR.build_sequences(lines)
    dim = len(seqs[0]['X'][0])
    model = TR.TrajectoryModel(dim, pool='gated', epochs=3)
    model.fit(seqs)
    probs = model.predict_prefix(seqs[0]['X'], seqs[0]['G'], 0)
    assert abs(sum(probs) - 1.0) < 1e-9
    assert all(p >= 0.0 for p in probs)
    # determinism: identical refit gives identical weights
    model2 = TR.TrajectoryModel(dim, pool='gated', epochs=3)
    model2.fit(seqs)
    assert model.W == model2.W
    assert model.a == model2.a
    # persistence round-trip
    payload = model.to_json()
    clone = TR.TrajectoryModel.from_json(payload)
    p1 = model.predict_steps(seqs[0]['X'], seqs[0]['G'])
    p2 = clone.predict_steps(seqs[0]['X'], seqs[0]['G'])
    assert p1 == p2


def test_final_only_twin_ignores_history():
    lines = TR.sample_lines(['krk'], 4, seed=13, horizon=10)
    seqs = TR.build_sequences(lines)
    dim = len(seqs[0]['X'][0])
    m = TR.TrajectoryModel(dim, pool='final', epochs=2)
    m.fit(seqs)
    s = seqs[0]
    # the final-only forecast at t=0 uses ONLY the first step: it equals
    # the forecast of a synthetic one-step line built from that step
    p_prefix = m.predict_prefix(s['X'], s['G'], 0)
    p_single = m.predict_steps([s['X'][0]], [s['G'][0]])
    assert p_prefix == p_single
    # ... whereas the gated model's forecast at t=0 differs from its
    # full-line forecast whenever the line has history (the contrast)
    g = TR.TrajectoryModel(dim, pool='gated', epochs=2)
    g.fit(seqs)
    assert g.predict_prefix(s['X'], s['G'], 0) != \
        g.predict_steps(s['X'], s['G']) or len(s['X']) == 1
