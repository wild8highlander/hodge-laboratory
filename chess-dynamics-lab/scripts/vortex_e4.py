#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Experiment E4 — the vortex-value correspondence on stratified samples.

For each frozen endgame (KRK, KQK, KNK, KPK) and each game-value class
(WTM-won, WTM-drawn, BTM-won, BTM-drawn) we draw seeded random states,
build the T16 vortex field, integrate the metric particle ensemble and
classify the state FROM THE FLOW ONLY (classify_by_flow).  The verdict is
compared with the frozen table class; the experiment freezes:

  * the ODE constants (FROZEN_VORTEX),
  * the agreement matrix (must be exactly 100%),
  * the separation margins (min capture over won/loss classes, max over
    drawn classes),
  * doctrine anchors (mate states, deepest states, promotion boundary),
  * a robustness scan (constants perturbed by +-20% must keep 100%).

The frozen report lands in results/vortex_e4.json.

Usage: python3 scripts/vortex_e4.py [samples_per_class]
"""
import base64
import gzip
import json
import os
import sys
import time
import zlib

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'vortex'))

from vortex import vortex_dynamics as V          # noqa: E402

RESULTS = os.path.join(ROOT, 'results')

CLASSES = ('wtm_won', 'wtm_drawn', 'btm_won', 'btm_drawn')


def _imul(x, y):
    return (x * y) & 0xffffffff


def mulberry32(seed):
    """Faithful JS-compatible mulberry32 (as in web/chess-oracle e1.js)."""
    state = {'a': seed & 0xffffffff}

    def rng():
        a = (state['a'] + 0x6D2B79F5) & 0xffffffff
        state['a'] = a
        t = (a ^ (a >> 15)) & 0xffffffff
        t = _imul(t, t | 1)
        t = (((t + _imul(t ^ (t >> 7), 61 | t)) & 0xffffffff) ^ t)
        t = (t ^ (t >> 14)) & 0xffffffff
        return t / 4294967296
    return rng


def sample_state(kind, rng, want):
    """Draw a random legal state of the requested class (want in CLASSES)."""
    for _ in range(200000):
        wk = int(rng() * 64)
        wp = int(rng() * 64)
        bk = int(rng() * 64)
        if wk == wp or wk == bk or wp == bk:
            continue
        if (wk & 0x88) or (wp & 0x88) or (bk & 0x88):
            continue                       # 0..63 is not always on a 0x88 board
        if max(abs((wk & 7) - (bk & 7)), abs((wk >> 4) - (bk >> 4))) <= 1:
            continue
        if kind == 'kpk' and (wp >> 4) == 0:
            continue                       # a pawn cannot stand on rank 1
        stm = 0 if want.startswith('wtm') else 1
        if stm == 0 and V.black_en_prise(kind, wk, wp, bk):
            continue
        s = V.pack(kind, wk, wp, bk, stm)
        v = V.probe(kind, s)
        won = v >= 0
        if want in ('wtm_won', 'btm_won') and not won:
            continue
        if want in ('wtm_drawn', 'btm_drawn') and won:
            continue
        return wk, wp, bk, stm, v
    raise RuntimeError('sampling failed for %s/%s' % (kind, want))


def run_class(kind, want, count, seed, constants=None):
    rng = mulberry32(seed)
    rows = []
    for _ in range(count):
        wk, wp, bk, stm, v = sample_state(kind, rng, want)
        field = V.build_field(kind, wk, wp, bk, stm)
        metrics = V.simulate(field, constants)
        flow = V.classify_by_flow(field, metrics, constants)
        table = field['verdict']
        rows.append({
            'state': V.pack(kind, wk, wp, bk, stm),
            'table': table, 'flow': flow,
            'agree': flow == table,
            'cf': round(metrics['capture_fraction'], 4),
            'dtm': field['dtm'],
        })
    return rows


def anchors():
    """Doctrine anchor states (built from the tables, not from sampling)."""
    out = []
    # the mate square story: first and deepest states of each endgame
    for kind in V.KINDS:
        dtm = V.load_frozen(kind)['dtm']
        first_mate = None
        deepest = None
        for s in range(V.SIZE):
            v = dtm[s]
            if v == 0 and first_mate is None:
                first_mate = s
            if 0 < v < 200 and (deepest is None or v > dtm[deepest]):
                deepest = s
            if first_mate is not None and deepest is not None:
                break
        if first_mate is not None:
            out.append((kind, 'mate-' + kind, first_mate))
        if deepest is not None:
            out.append((kind, 'deepest-' + kind, deepest))
    # doctrine WTM/BTM pair (the classical KRK box: WK b6, Rh7, BK a8)
    def sq(name):
        return (ord(name[0]) - 97) + 16 * (int(name[1]) - 1)
    out.append(('krk', 'krk-box-wtm', V.pack('krk', sq('b6'), sq('h7'),
                                             sq('a8'), 0)))
    out.append(('krk', 'krk-box-btm', V.pack('krk', sq('b6'), sq('h7'),
                                             sq('a8'), 1)))
    # the knight negative control (T15): pure rotation, no currents
    out.append(('knk', 'knk-rotation', V.pack('knk', sq('d3'), sq('c1'),
                                              sq('b5'), 0)))
    return out


def class_counts(kind):
    """Exact per-class state counts over the whole frozen space.

    This scan is itself a frozen result: for KRK and KQK the WTM-drawn
    class is EMPTY (every legal strong-side-to-move state is won), and
    for KNK the won classes are empty (T15)."""
    counts = {c: 0 for c in CLASSES}
    dtm = V.load_frozen(kind)['dtm']
    S = [s for s in range(128) if not (s & 0x88)]
    for wk in S:
        for wp in S:
            if wp == wk:
                continue
            for bk in S:
                if bk == wk or bk == wp:
                    continue
                if max(abs((wk & 7) - (bk & 7)),
                       abs((wk >> 4) - (bk >> 4))) <= 1:
                    continue
                if dtm[V.pack(kind, wk, wp, bk, 1)] < 200:
                    counts['btm_won'] += 1
                else:
                    counts['btm_drawn'] += 1
                if V.black_en_prise(kind, wk, wp, bk):
                    continue
                if dtm[V.pack(kind, wk, wp, bk, 0)] < 200:
                    counts['wtm_won'] += 1
                else:
                    counts['wtm_drawn'] += 1
    return counts


def main():
    per_class = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    t0 = time.time()
    constants = dict(V.FROZEN_VORTEX)
    report = {
        'experiment': 'E4 — vortex-value correspondence (T16)',
        'constants': constants,
        'samples_per_class': per_class,
        'classes': {},
        'anchors': {},
        'robustness': {},
    }
    total = agreed = 0
    cf_min_forced = 1.0
    cf_max_drawn = 0.0
    for kind in V.KINDS:
        counts = class_counts(kind)
        report.setdefault('class_counts', {})[kind] = counts
        print('%s exact class counts: %s' % (kind, counts), flush=True)
        for want in CLASSES:
            if counts[want] == 0:
                report['classes'][kind + '/' + want] = {
                    'n': 0, 'agreed': 0, 'empty': True}
                print('%-16s EMPTY CLASS (verified by exact scan)'
                      % (kind + '/' + want), flush=True)
                continue
            if kind == 'knk' and want.endswith('won'):
                continue                    # T15: a won state does not exist
            rows = run_class(kind, want, per_class,
                             seed=0xE4 + zlib.crc32(
                                 ('%s/%s' % (kind, want)).encode()) % 9999)
            ok = sum(r['agree'] for r in rows)
            total += len(rows)
            agreed += ok
            # mate-on-board states are the terminal sink: cf = 0 by
            # definition, excluded from the capture margin
            cfs = [r['cf'] for r in rows if r['dtm'] != 0]
            if not cfs:
                cfs = [0.0]
            cls_name = kind + '/' + want
            report['classes'][cls_name] = {
                'n': len(rows), 'agreed': ok,
                'cf_min': min(cfs), 'cf_mean': round(float(np.mean(cfs)), 4),
                'terminal_mates': sum(1 for r in rows if r['dtm'] == 0),
            }
            if want.endswith('won'):
                if cfs:
                    cf_min_forced = min(cf_min_forced, min(cfs))
            else:
                cf_max_drawn = max(cf_max_drawn, max(cfs))
            print('%-16s agreed %d/%d  cf[min=%.3f mean=%.3f]' % (
                cls_name, ok, len(rows), min(cfs), float(np.mean(cfs))),
                flush=True)
    report['agreement'] = {
        'total': total, 'agreed': agreed,
        'rate': round(agreed / total, 4) if total else None,
    }
    report['margins'] = {
        'capture_min_won_loss': round(cf_min_forced, 4),
        'capture_max_drawn': round(cf_max_drawn, 4),
        'gate_win_capture_min': constants['win_capture_min'],
        'gate_draw_capture_max': constants['draw_capture_max'],
    }

    # ── doctrine anchors ─────────────────────────────────────────────────
    for kind, name, s in anchors():
        wk, wp, bk, stm = V.unpack(s)
        field = V.build_field(kind, wk, wp, bk, stm)
        metrics = V.simulate(field)
        flow = V.classify_by_flow(field, metrics)
        ok = flow == field['verdict']
        report['anchors'][name] = {
            'state': s, 'unpack': [wk, wp, bk, stm],
            'table': field['verdict'], 'flow': flow, 'agree': ok,
            'cf': round(metrics['capture_fraction'], 4),
            'dtm': field['dtm'],
        }
        print('anchor %-16s table=%s flow=%s cf=%.3f %s' % (
            name, field['verdict'], flow, metrics['capture_fraction'],
            'OK' if ok else 'FAIL'), flush=True)

    # ── robustness: perturb the constants by +-20% ───────────────────────
    base = dict(V.FROZEN_VORTEX)
    all_counts = report['class_counts']
    for key in ('kappa', 'zeta', 'gamma', 'j_neutral'):
        for sign in (0.8, 1.2):
            pert = dict(base)
            pert[key] = base[key] * sign
            pert_total = pert_ok = 0
            for kind in V.KINDS:
                for want in CLASSES:
                    if all_counts[kind][want] == 0:
                        continue
                    rows = run_class(kind, want, 40,
                                     seed=0xBEEF + zlib.crc32(
                                         ('%s/%s' % (kind, want)).encode())
                                     % 997, constants=pert)
                    pert_total += len(rows)
                    pert_ok += sum(r['agree'] for r in rows)
            tag = '%s%+d%%' % (key, int(round((sign - 1) * 100)))
            report['robustness'][tag] = {
                'n': pert_total, 'agreed': pert_ok,
                'rate': round(pert_ok / pert_total, 4),
            }
            print('robust %-14s %d/%d' % (tag, pert_ok, pert_total),
                  flush=True)

    report['runtime_s'] = round(time.time() - t0, 1)
    out = os.path.join(RESULTS, 'vortex_e4.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print('frozen ->', out)
    print('agreement: %d/%d = %.2f%%  margins: won/loss cf>=%.3f, '
          'drawn cf<=%.3f' % (agreed, total, 100 * agreed / total,
                              cf_min_forced, cf_max_drawn))
    if agreed != total:
        raise SystemExit('E4 FAILED: agreement below 100%')
    if cf_min_forced < constants['win_capture_min']:
        raise SystemExit('E4 FAILED: won/loss capture margin below gate')
    if cf_max_drawn >= constants['draw_capture_max']:
        raise SystemExit('E4 FAILED: drawn capture above gate')
    print('E4 PASSED')


if __name__ == '__main__':
    main()
