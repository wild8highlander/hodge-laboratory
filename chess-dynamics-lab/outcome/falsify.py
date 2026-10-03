#!/usr/bin/env python3
"""outcome/falsify.py — the Falsification Engine (Epoch VI).

The plan's final epoch turns the laboratory against itself: instead of
celebrating the E8 certificate, the engine hunts the states where the
frozen model is WRONG — hard errors, miscalibrated confidences and
broken mate-distance forecasts — and freezes them into a curated
counterexample corpus (``counterexamples/``).

The corpus is a *regression benchmark by construction*: the next model
version must fix these states without breaking the certificate, and the
summary JSON records the per-kind error budget so any regression is a
diff, not a vibe.

Mining protocol (deterministic, bit-reproducible):

1.  states come from the same seeded rejection sampler as the E8
    dataset (same seed => same population), so every mined state is
    reproducible;
2.  predictions come from the frozen model payload: the ensemble (or
    the single softmax for v1 files), the per-domain temperature of the
    calibration layer, and the DTM ridge head when present;
3.  every state is labelled by the exact oracle (never by the model),
    and each row records its hash split — TEST-split errors are the
    generalization falsifications, TRAIN-split errors the underfit
    diagnostics;
4.  the corpus keeps ALL hard errors and the top-K worst miscalibrations
    per domain, sorted by the calibration gap 1 - P(true class).
"""
import csv
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from outcome import dataset as DS                           # noqa: E402
from outcome import model as M                              # noqa: E402
from outcome import nonlinear as NL                         # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402

DTM_ERROR_PLIES = 4.0          # |predicted - exact| DTM gap worth mining
LOW_CONFIDENCE = 0.5           # P(true class) below this = miscalibrated
TOP_K_CALIBRATION = 60         # worst-miscalibrated rows kept per domain


def load_heads(payload):
    """(proba_fn, dtm_fn) from a frozen model payload."""
    names = payload['feature_names']
    if payload.get('ensemble'):
        head = M.SoftmaxEnsemble.from_json(payload['ensemble'], len(names))

        def proba(X):
            return head.predict_proba_raw(X)
    else:
        head = M.SoftmaxRegression.from_json(payload['softmax'], len(names))

        def proba(X):
            return head.predict_proba_raw(X)
    cal = M.TemperatureCalibrator.from_json(payload['calibrator']) \
        if payload.get('calibrator') else None

    def proba_cal(X, slice_key):
        probs = proba(X)
        if cal is None:
            return probs
        return [cal.transform(p, slice_key) for p in probs]

    ridge = None
    if payload.get('ridge'):
        ridge = M.RidgeRegression.from_json(payload['ridge'], len(names))

    # the E11 nonlinear routes (if the payload carries any): the gated
    # predictor answers the routed slices with their specialists and
    # falls through to the global head everywhere else
    gated = NL.build_gated(payload, global_proba=proba_cal)
    if gated is not None:
        return names, gated.proba, ridge
    return names, proba_cal, ridge


def mine(model_path, kinds, per_kind, seed=DS.DEFAULT_SEED,
         top_k=TOP_K_CALIBRATION, log=None):
    """Mine the counterexample corpus.  Returns (rows, summary)."""
    log = log or print
    payload = M.load_model(model_path)
    names, proba, ridge = load_heads(payload)
    rows = []
    per_kind_summary = {}
    for kind in kinds:
        t0 = time.time()
        recs = DS.build_sampled(kind, per_kind, seed)
        X = [[r['features'][n] for n in names] for r in recs]
        probs = proba(X, kind)
        dtms = ridge.predict_raw(X) if ridge is not None \
            else [None] * len(recs)
        n_hard = n_lowconf = n_dtmerr = 0
        kind_rows = []
        for r, p, dpred in zip(recs, probs, dtms):
            cls = r['cls']
            if cls is None:
                continue                      # illegal state: skip
            dtm_true = r['dtm_plies']
            pred = max(range(3), key=lambda k: p[k])
            cal_gap = round(1.0 - p[cls], 6)
            cats = []
            if pred != cls:
                cats.append('hard_error')
                n_hard += 1
            if p[cls] < LOW_CONFIDENCE:
                cats.append('low_confidence')
                n_lowconf += 1
            dtm_err = None
            if ridge is not None and dtm_true is not None and dtm_true >= 0:
                dtm_err = round(abs(max(0.0, dpred) - dtm_true), 3)
                if dtm_err > DTM_ERROR_PLIES:
                    cats.append('dtm_error')
                    n_dtmerr += 1
            kind_rows.append({
                'kind': kind,
                'state': r['state'],
                'fen': r['fen'],
                'split': DS.split_of(r['state'], DS.KINDS_INDEX[kind]),
                'cls_true': cls,
                'cls_true_name': T.CLASS_NAMES[cls],
                'dtm_true': dtm_true if dtm_true is not None else -1,
                'p_black_win': round(p[T.BLACK_WIN], 6),
                'p_draw': round(p[T.DRAW], 6),
                'p_white_win': round(p[T.WHITE_WIN], 6),
                'pred_class': T.CLASS_NAMES[pred],
                'cal_gap': cal_gap,
                'dtm_pred': (round(max(0.0, dpred), 3)
                             if dpred is not None else ''),
                'dtm_err': dtm_err if dtm_err is not None else '',
                'categories': '|'.join(cats),
            })
        # keep: all hard errors + top-K worst calibration gaps
        hard = [r for r in kind_rows if 'hard_error' in r['categories']]
        soft = sorted((r for r in kind_rows if 'hard_error'
                       not in r['categories']),
                      key=lambda r: (-r['cal_gap'], r['state']))[:top_k]
        rows.extend(hard)
        rows.extend(soft)
        n = len([r for r in recs if r['cls'] is not None])
        per_kind_summary[kind] = {
            'n': n,
            'hard_errors': n_hard,
            'low_confidence': n_lowconf,
            'dtm_errors': n_dtmerr,
            'hard_error_rate': round(n_hard / max(n, 1), 6),
            'kept_rows': len(hard) + len(soft),
            'seconds': round(time.time() - t0, 1),
        }
        log('  %-4s mined %d states: %d hard errors (%.2f%%), '
            '%d low-confidence, %d DTM outliers  [%.1fs]'
            % (kind, n, n_hard, 100.0 * n_hard / max(n, 1), n_lowconf,
               n_dtmerr, time.time() - t0))
    rows.sort(key=lambda r: (r['kind'], -r['cal_gap'], r['state']))
    summary = {
        'certificate': 'E10 — falsification corpus',
        'model': os.path.basename(model_path),
        'seed': seed,
        'per_kind': per_kind_summary,
        'total_rows': len(rows),
        'dtm_error_plies_threshold': DTM_ERROR_PLIES,
        'low_confidence_threshold': LOW_CONFIDENCE,
    }
    return rows, summary


CSV_COLUMNS = ['kind', 'state', 'fen', 'split', 'cls_true', 'cls_true_name',
               'dtm_true', 'p_black_win', 'p_draw', 'p_white_win',
               'pred_class', 'cal_gap', 'dtm_pred', 'dtm_err', 'categories']


def export_corpus(rows, summary, out_dir, readme_extra=''):
    """Freeze the corpus: CSV + summary JSON + a generated README."""
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, 'counterexamples.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    json_path = os.path.join(out_dir, 'summary.json')
    with open(json_path, 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    md_path = os.path.join(out_dir, 'README.md')
    lines = [
        '# counterexamples/ — the falsification corpus (Epoch VI)',
        '',
        'Generated by `python3 -m outcome falsify` against the frozen E8',
        'model.  Every row is a state where the statistical layer of the',
        'Outcome Field disagrees with the exact oracle:',
        '',
        '* `hard_error` — the argmax class is wrong;',
        '* `low_confidence` — P(true class) < %.2f;' % LOW_CONFIDENCE,
        '* `dtm_error` — the ridge DTM head is off by more than %.0f plies.'
        % DTM_ERROR_PLIES,
        '',
        'The corpus doubles as a regression benchmark: a future model',
        'version must reduce these counts without breaking the frozen',
        'certificate.  Regenerate with:',
        '',
        '```',
        'python3 -m outcome falsify --per-kind %d --seed %d'
        % (summary['per_kind'][list(summary['per_kind'])[0]]['n'],
           summary['seed']),
        '```',
        '',
        '| domain | mined | hard errors | rate | low conf | dtm outliers |',
        '|--------|-------|-------------|------|----------|--------------|',
    ]
    for kind, s in sorted(summary['per_kind'].items()):
        lines.append('| %s | %d | %d | %.4f | %d | %d |'
                     % (kind, s['n'], s['hard_errors'], s['hard_error_rate'],
                        s['low_confidence'], s['dtm_errors']))
    lines.append('')
    lines.append('Total corpus rows: %d (all hard errors + the top-%d '
                 'miscalibrations per domain).' % (summary['total_rows'],
                                                   TOP_K_CALIBRATION))
    if readme_extra:
        lines.append('')
        lines.append(readme_extra)
    with open(md_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    return csv_path, json_path, md_path
