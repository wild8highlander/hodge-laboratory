#!/usr/bin/env python3
"""outcome/metrics.py — the distillation benchmark metrics (Epoch III).

The program forbids reporting a naked "accuracy" (plan §13): the same
prediction can be information-rich or information-free depending on
calibration.  This module therefore measures:

    accuracy       the top-1 class hit rate
    log_loss       the proper scoring rule for probabilities
    brier          the multiclass Brier score (mean over samples)
    ece            expected calibration error over the max-probability
    macro_f1       the W/D/L balance of hard predictions
    mae            mean absolute error (the DTM head, in plies)
    confusion      per-class cross table
    calibration    the reliability table: is "70%" really 70%?

Every function is pure Python and deterministic; the baselines
(majority class, single-layer models) live in this module too so the
report can *prove* — not assert — that the dynamics add information.
"""
import math

EPS = 1e-12


def accuracy(y_true, y_pred):
    if not y_true:
        return 0.0
    hits = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return hits / len(y_true)


def log_loss(y_true, probs, n_classes=3):
    total = 0.0
    for t, p in zip(y_true, probs):
        total -= math.log(max(p[t], EPS))
    return total / max(len(y_true), 1)


def brier(y_true, probs, n_classes=3):
    total = 0.0
    for t, p in zip(y_true, probs):
        s = 0.0
        for k in range(n_classes):
            target = 1.0 if k == t else 0.0
            s += (p[k] - target) ** 2
        total += s
    return total / max(len(y_true), 1)


def macro_f1(y_true, y_pred, n_classes=3):
    f1s = []
    for k in range(n_classes):
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == k and p == k)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != k and p == k)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == k and p != k)
        denom = 2 * tp + fp + fn
        f1s.append((2 * tp / denom) if denom else 0.0)
    return sum(f1s) / n_classes


def confusion(y_true, y_pred, n_classes=3):
    table = [[0] * n_classes for _ in range(n_classes)]
    for t, p in zip(y_true, y_pred):
        table[t][p] += 1
    return table


def ece(y_true, probs, n_bins=10):
    """Expected calibration error over the max-probability class."""
    bins = [[] for _ in range(n_bins)]          # correctness flags per bin
    conf_sums = [0.0] * n_bins
    for t, p in zip(y_true, probs):
        conf = max(p)
        pred = p.index(conf)
        idx = min(int(conf * n_bins), n_bins - 1)
        bins[idx].append(1.0 if pred == t else 0.0)
        conf_sums[idx] += conf
    total = len(y_true)
    if not total:
        return 0.0
    e = 0.0
    for i, bucket in enumerate(bins):
        if bucket:
            mean_conf = conf_sums[i] / len(bucket)
            mean_acc = sum(bucket) / len(bucket)
            e += (len(bucket) / total) * abs(mean_acc - mean_conf)
    return e


def calibration_table(y_true, probs, n_bins=10):
    """Reliability table rows: [lo, hi, count, mean_conf, empirical_acc]."""
    rows = []
    conf_sums = [0.0] * n_bins
    acc_sums = [0.0] * n_bins
    counts = [0] * n_bins
    for t, p in zip(y_true, probs):
        conf = max(p)
        pred = p.index(conf)
        idx = min(int(conf * n_bins), n_bins - 1)
        counts[idx] += 1
        conf_sums[idx] += conf
        acc_sums[idx] += 1.0 if pred == t else 0.0
    for i in range(n_bins):
        lo, hi = i / n_bins, (i + 1) / n_bins
        if counts[i]:
            rows.append({'bin': i, 'lo': lo, 'hi': hi, 'count': counts[i],
                         'mean_conf': conf_sums[i] / counts[i],
                         'empirical_acc': acc_sums[i] / counts[i]})
        else:
            rows.append({'bin': i, 'lo': lo, 'hi': hi, 'count': 0,
                         'mean_conf': None, 'empirical_acc': None})
    return rows


def mae(y_true, y_pred):
    if not y_true:
        return 0.0
    return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)


def summarize(y_true, probs, n_classes=3):
    """The full metric block for one prediction set."""
    y_pred = [max(range(len(p)), key=lambda k: p[k]) for p in probs]
    return {
        'n': len(y_true),
        'accuracy': round(accuracy(y_true, y_pred), 6),
        'log_loss': round(log_loss(y_true, probs, n_classes), 6),
        'brier': round(brier(y_true, probs, n_classes), 6),
        'ece': round(ece(y_true, probs, n_bins=10), 6),
        'macro_f1': round(macro_f1(y_true, y_pred, n_classes), 6),
        'confusion': confusion(y_true, y_pred, n_classes),
    }


def majority_baseline(y_train, y_test, n_classes=3):
    """Predict the train-set majority class everywhere."""
    counts = [0] * n_classes
    for y in y_train:
        counts[y] += 1
    top = max(range(n_classes), key=lambda k: counts[k])
    probs = []
    total = len(y_train)
    for _ in y_test:
        probs.append([counts[k] / total for k in range(n_classes)])
    y_pred = [top] * len(y_test)
    return {
        'n': len(y_test),
        'accuracy': round(accuracy(y_test, y_pred), 6),
        'log_loss': round(log_loss(y_test, probs, n_classes), 6),
        'brier': round(brier(y_test, probs, n_classes), 6),
        'ece': round(ece(y_test, probs, n_bins=10), 6),
        'macro_f1': round(macro_f1(y_test, y_pred, n_classes), 6),
    }
