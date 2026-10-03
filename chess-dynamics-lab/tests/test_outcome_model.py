#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the distillation layer (Epoch III): the zero-dependency
models, the metrics and the deterministic dataset machinery."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import dataset as DS               # noqa: E402
from outcome import metrics as MT               # noqa: E402
from outcome import model as M                  # noqa: E402
from outcome import tablebase_api as T          # noqa: E402


# ── dataset machinery ────────────────────────────────────────────────────
def test_sampling_is_deterministic_and_legal():
    a = DS.sample_states('krk', 200, seed=1234)
    b = DS.sample_states('krk', 200, seed=1234)
    assert a == b
    assert len(a) == 200
    for wk, wp, bk, stm in a:
        assert T.is_legal_state('krk', wk, wp, bk, stm)


def test_different_seeds_give_different_samples():
    a = DS.sample_states('krk', 200, seed=1)
    b = DS.sample_states('krk', 200, seed=2)
    assert a != b


def test_split_covers_all_buckets():
    seen = set()
    for s in range(0, 1 << 22, 9973):
        seen.add(DS.split_of(s, 0))
    assert seen == {'train', 'valid', 'test'}


def test_split_is_kind_aware():
    # the hash split mixes the kind index, so the same packed id splits
    # independently per domain; bucket shares must still hit 70/15/10
    counts = {'train': 0, 'valid': 0, 'test': 0}
    for s in range(10000):
        counts[DS.split_of(s, 3)] += 1
    assert abs(counts['train'] - 7000) < 200
    assert abs(counts['valid'] - 1500) < 150
    assert abs(counts['test'] - 1500) < 150
    # and at least some states disagree across kinds (kind mixed in)
    disagreements = sum(1 for s in range(500)
                        if DS.split_of(s, 0) != DS.split_of(s, 1))
    assert disagreements > 50


# ── the softmax head ─────────────────────────────────────────────────────
def _blob(n, shift, spread=0.7, seed=0):
    import random
    rng = random.Random(seed)
    X, y = [], []
    for k in range(3):
        for _ in range(n):
            X.append([rng.gauss(shift[k][j], spread) for j in range(2)])
            y.append(k)
    return X, y


def test_softmax_converges_on_separable_data():
    X, y = _blob(120, [(-3.0, -3.0), (0.0, 3.0), (3.0, -3.0)], seed=42)
    model = M.SoftmaxRegression(2, epochs=40)
    model.fit(X, y)
    probs = model.predict_proba_raw(X)
    pred = [max(range(3), key=lambda k: p[k]) for p in probs]
    assert MT.accuracy(y, pred) > 0.95
    assert all(abs(sum(p) - 1.0) < 1e-9 for p in probs)


def test_softmax_is_bit_reproducible():
    X, y = _blob(60, [(-2.0, 0.0), (2.0, 0.0), (0.0, 2.5)], seed=7)
    m1 = M.SoftmaxRegression(2, epochs=15).fit(X, y)
    m2 = M.SoftmaxRegression(2, epochs=15).fit(X, y)
    assert m1.W == m2.W
    assert m1.loss_history == m2.loss_history


def test_softmax_persistence_round_trip(tmp_path):
    X, y = _blob(60, [(-2.0, 0.0), (2.0, 0.0), (0.0, 2.5)], seed=7)
    model = M.SoftmaxRegression(2, epochs=15).fit(X, y)
    payload = model.to_json()
    restored = M.SoftmaxRegression.from_json(payload, 2)
    X2, _ = _blob(20, [(-2.0, 0.0), (2.0, 0.0), (0.0, 2.5)], seed=8)
    a = model.predict_proba_raw(X2)
    b = restored.predict_proba_raw(X2)
    assert a == b


# ── the ridge head ───────────────────────────────────────────────────────
def test_ridge_fits_linear_data():
    import random
    rng = random.Random(3)
    X = [[rng.random() * 10, rng.random() * 5] for _ in range(300)]
    y = [2.0 * x[0] - 1.0 * x[1] + 4.0 for x in X]
    model = M.RidgeRegression(2, epochs=200, lr=0.2)
    model.fit(X, y)
    preds = model.predict_raw(X)
    assert MT.mae(y, preds) < 0.1


# ── the metrics ──────────────────────────────────────────────────────────
def test_metrics_bounds_and_sanity():
    y = [0, 1, 2, 1]
    probs = [[0.7, 0.2, 0.1], [0.1, 0.8, 0.1],
             [0.2, 0.1, 0.7], [0.1, 0.6, 0.3]]
    s = MT.summarize(y, probs)
    assert 0.0 <= s['accuracy'] <= 1.0
    assert 0.0 <= s['brier'] <= 2.0
    assert 0.0 <= s['ece'] <= 1.0
    assert s['accuracy'] == 1.0          # top class always matches y
    assert s['brier'] < 0.2              # confident AND correct


def test_majority_baseline_is_weak_but_valid():
    y_train = [2] * 90 + [1] * 10
    y_test = [2] * 5 + [1] * 5
    base = MT.majority_baseline(y_train, y_test)
    assert base['accuracy'] == 0.5       # always predicts class 2


def test_calibration_table_rows():
    y = [1, 1, 1, 0]
    probs = [[0.2, 0.8, 0.0], [0.2, 0.8, 0.0],
             [0.2, 0.8, 0.0], [0.8, 0.1, 0.1]]
    rows = MT.calibration_table(y, probs)
    filled = [r for r in rows if r['count']]
    assert filled
    top = max(filled, key=lambda r: r['count'])
    # all four top predictions hit (0.8-0.9 bin: 3 draws + 1 black win)
    assert abs(top['empirical_acc'] - 1.0) < 1e-9
