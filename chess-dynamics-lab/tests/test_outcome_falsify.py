#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Epoch VI falsification engine: a deliberately broken
model must be falsified; the corpus must be deterministic and complete."""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import falsify as FLS            # noqa: E402
from outcome import model as M                # noqa: E402
from outcome import tablebase_api as T        # noqa: E402


def _broken_model(tmp_path, feature_names):
    """A model hardwired to answer 'draw' (draw-bias 5.0): it MUST be
    falsified by the won states of KRK."""
    head = M.SoftmaxRegression(len(feature_names), epochs=1)
    head.W = [[0.0] * (len(feature_names) + 1) for _ in range(3)]
    head.W[1][0] = 5.0                      # the draw class dominates
    head._standardizer = M.Standardizer([0.0] * len(feature_names),
                                        [1.0] * len(feature_names))
    payload = {
        'feature_names': feature_names,
        'softmax': head.to_json(),
        'ensemble': None,
        'calibrator': None,
        'ridge': None,
        'recipe': {'kinds': ['krk'], 'per_kind': 40, 'seed': 2026},
        'metrics_pooled': {'accuracy': 0.0},
    }
    path = os.path.join(str(tmp_path), 'broken_model.json')
    M.save_model(path, payload)
    return path


def test_broken_model_is_falsified(tmp_path):
    names = ['piece_count_total', 'side_to_move']   # any tiny spec
    path = _broken_model(tmp_path, names)
    rows, summary = FLS.mine(path, ('krk',), 40, seed=2026)
    assert summary['per_kind']['krk']['n'] == 40
    assert summary['per_kind']['krk']['hard_errors'] > 0
    hard = [r for r in rows if 'hard_error' in r['categories']]
    assert hard
    # every hard error row is a won state mispredicted as draw
    for r in hard:
        assert r['cls_true'] == T.WHITE_WIN
        assert r['pred_class'] == 'draw'
        assert r['cal_gap'] > 0.5


def test_corpus_export_round_trip(tmp_path):
    names = ['piece_count_total', 'side_to_move']
    path = _broken_model(tmp_path, names)
    rows, summary = FLS.mine(path, ('krk',), 30, seed=7)
    out_dir = os.path.join(str(tmp_path), 'counterexamples')
    csv_path, json_path, md_path = FLS.export_corpus(rows, summary, out_dir)
    assert os.path.exists(csv_path)
    assert os.path.exists(json_path)
    assert os.path.exists(md_path)
    with open(csv_path, 'r', encoding='utf-8') as fh:
        reader = list(csv.DictReader(fh))
    assert len(reader) == summary['total_rows']
    assert len(reader) > 0
    with open(json_path, 'r', encoding='utf-8') as fh:
        reloaded = json.load(fh)
    assert reloaded['total_rows'] == summary['total_rows']
    assert 'hard_error_rate' in reloaded['per_kind']['krk']
    with open(md_path, 'r', encoding='utf-8') as fh:
        text = fh.read()
    assert 'falsification corpus' in text
    assert '| krk |' in text


def test_mining_is_deterministic(tmp_path):
    names = ['piece_count_total', 'side_to_move']
    path = _broken_model(tmp_path, names)
    rows1, _ = FLS.mine(path, ('krk',), 25, seed=99)
    rows2, _ = FLS.mine(path, ('krk',), 25, seed=99)
    assert rows1 == rows2
