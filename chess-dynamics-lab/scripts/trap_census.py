#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trap census — the exhaustive structural twin of experiment E1 (T17).

E1 SAMPLES: it draws seeded won states and asks what the greedy particle
solver does ONCE.  This script EXHAUSTS: over every legal state of the
four frozen endgames (KRK, KQK, KNK, KPK) and every legal move it
classifies the child value against the parent value and counts the
move classes.  Nothing here is sampled, so the output is a population
fact, not an estimate.

Move classes (child value v EXCLUDES the move ply; a KPK promotion child
is valued through the frozen KQK certificate exactly as in the build):

  WTM won parent d (White owns the net):
    optimal   v = d-1                     — a Bellman descent step;
    waste     v >= d                      — still won, DTM wasted by
                                            ddtm = v-(d-1) plies (the
                                            exact population analog of
                                            E1's "price of greed");
    slack     v < 0                       — the win is gone forever
                                            (win -> draw, E1's "lost").
  WTM drawn parent:
    keep      every move keeps the draw (Bellman: no won child exists).
  BTM drawn parent:
    trap      v >= 0                      — the move turns the draw into
                                            a LOSS (draw -> loss): the
                                            snare the user asked to
                                            highlight;
    keep      v < 0 or a capture          — the drawing resource.
  BTM won parent d (the defender is being mated):
    optimal_def  v = d-1                  — the most resistant defence;
    accel        v > d-1                  — accelerates the mate by
                                            (v-(d-1)) plies;
    escape       a capture of the piece   — impossible in a won parent
                                            (Bellman; counted defensively).

KNK is the zero control: every parent is drawn and every child is drawn,
so traps = slack = waste = 0 by exhaustion (T15 in move-class language).

Frozen output: results/trap_census.json (aggregate counts only — the
per-state detail stays recomputable from the tables).

Usage: python3 scripts/trap_census.py
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'vortex'))

from vortex import vortex_dynamics as V          # noqa: E402

RESULTS = os.path.join(ROOT, 'results')
SQUARES = [s for s in range(128) if not (s & 0x88)]


def scan_kind(kind):
    """Exhaustive move-class census of one frozen endgame."""
    dtm = V.load_frozen(kind)['dtm']
    kqk = V.load_frozen('kqk')['dtm'] if kind == 'kpk' else None

    # ── WTM scan (legal = Black not en prise) ────────────────────────────
    w = {'states': 0, 'moves': 0, 'optimal': 0, 'waste': 0, 'slack': 0,
         'with_slack': 0, 'with_waste': 0,
         'ddtm_sum': 0, 'ddtm_max': 0, 'won_states': 0,
         'bellman_violations': 0}
    # ── BTM scan (every non-adjacent triple) ─────────────────────────────
    b = {'states': 0, 'won_states': 0, 'drawn_states': 0, 'moves': 0,
         'traps': 0, 'with_traps': 0, 'max_traps': 0,
         'deepest_trap_plies': 0, 'keeps': 0, 'escapes': 0,
         'optimal_def': 0, 'accel_sum': 0, 'accel_count': 0,
         'accel_max': 0}
    t0 = time.time()
    for wk in SQUARES:
        for wp in SQUARES:
            if wp == wk:
                continue
            for bk in SQUARES:
                if bk == wk or bk == wp:
                    continue
                if max(abs((wk & 7) - (bk & 7)),
                       abs((wk >> 4) - (bk >> 4))) <= 1:
                    continue
                if kind == 'kpk' and not (1 <= (wp >> 4) <= 6):
                    continue          # the builder packs the pawn on
                                      # ranks 2..7 only: rank 1 does not
                                      # exist for a white pawn and on
                                      # rank 8 it has promoted — the
                                      # census must enumerate exactly
                                      # the table's universe (a first
                                      # draft counted 55,920 phantom
                                      # rank-8 states; caught by the
                                      # E5 cross-assert vs the table
                                      # header, 2026-09-30)

                # ── Black to move ────────────────────────────────────
                b['states'] += 1
                parent = V.probe(kind, V.pack(kind, wk, wp, bk, 1))
                ch, captured = V.children_black(kind, wk, wp, bk)
                vals = [(-1 if dtm[c] >= 200 else dtm[c]) for c in ch]
                if parent >= 0:
                    b['won_states'] += 1
                else:
                    b['drawn_states'] += 1
                traps = 0
                if captured:
                    b['escapes'] += 1
                    b['moves'] += 1
                    if parent >= 0:
                        # would contradict Bellman (won parent with an
                        # escape) — the build forbids it; count honestly
                        b['bellman_note'] = b.get('bellman_note', 0) + 1
                    else:
                        b['keeps'] += 1
                for v in vals:
                    b['moves'] += 1
                    if parent < 0:
                        if v >= 0:
                            traps += 1
                            b['traps'] += 1
                            if v > b['deepest_trap_plies']:
                                b['deepest_trap_plies'] = v
                        else:
                            b['keeps'] += 1
                    else:
                        if v < 0:
                            # escape in a won parent: Bellman violation
                            b['bellman_note'] = \
                                b.get('bellman_note', 0) + 1
                        elif v == parent - 1:
                            b['optimal_def'] += 1
                        else:
                            b['accel_sum'] += v - (parent - 1)
                            b['accel_count'] += 1
                            if v - (parent - 1) > b['accel_max']:
                                b['accel_max'] = v - (parent - 1)
                if traps:
                    b['with_traps'] += 1
                    if traps > b['max_traps']:
                        b['max_traps'] = traps

                # ── White to move (legal iff Black not en prise) ─────
                if V.black_en_prise(kind, wk, wp, bk):
                    continue
                w['states'] += 1
                parent = V.probe(kind, V.pack(kind, wk, wp, bk, 0))
                children = V.children_white(kind, wk, wp, bk, dtm, kqk)
                if parent >= 0:
                    w['won_states'] += 1
                slack = 0
                waste = 0
                for v, _f, _t in children:
                    w['moves'] += 1
                    if parent >= 0:
                        if v < 0:
                            slack += 1
                            w['slack'] += 1
                        elif v == parent - 1:
                            w['optimal'] += 1
                        else:
                            waste += 1
                            w['waste'] += 1
                            ddtm = v - (parent - 1)
                            w['ddtm_sum'] += ddtm
                            if ddtm > w['ddtm_max']:
                                w['ddtm_max'] = ddtm
                    else:
                        if v >= 0:
                            w['bellman_violations'] += 1
                if slack:
                    w['with_slack'] += 1
                if waste:
                    w['with_waste'] += 1
    w['ddtm_mean'] = round(w['ddtm_sum'] / w['waste'], 4) \
        if w['waste'] else 0.0
    b['accel_mean'] = round(b['accel_sum'] / b['accel_count'], 4) \
        if b['accel_count'] else 0.0
    b['trap_share'] = round(b['traps'] / b['moves'], 6) \
        if b['moves'] else 0.0
    w['optimal_share'] = round(w['optimal'] / w['moves'], 6) \
        if w['moves'] else 0.0
    return {'kind': kind, 'wtm': w, 'btm': b,
            'runtime_s': round(time.time() - t0, 1)}


def main():
    t0 = time.time()
    report = {
        'experiment': 'T17 trap census — exhaustive move classes over '
                      'the four frozen endgames (the population twin '
                      'of sampled E1)',
        'semantics': {
            'child_value': 'DTM plies excluding the move ply; KPK '
                           'promotion children valued through the '
                           'frozen KQK certificate',
            'trap': 'BTM drawn -> child won (draw becomes a loss)',
            'slack': 'WTM won -> child drawn (win becomes a draw)',
            'waste': 'WTM won -> child won above d-1 (ddtm plies lost)',
            'optimal': 'child at exactly d-1 (Bellman descent)',
            'optimal_def': 'BTM won -> child at exactly d-1 (most '
                           'resistant defence)',
            'accel': 'BTM won -> child above d-1 (mate arrives sooner)',
        },
        'kinds': {},
    }
    for kind in V.KINDS:
        res = scan_kind(kind)
        report['kinds'][kind] = res
        w, b = res['wtm'], res['btm']
        print('%-4s %6.1fs  WTM won %6d (slack %5d in %5d states, waste '
              '%6d, ddtm mean %.3f max %d)  BTM drawn %6d '
              '(traps %6d in %6d states, max %d, deepest %d plies)' % (
                  kind, res['runtime_s'], w['won_states'], w['slack'],
                  w['with_slack'], w['waste'], w['ddtm_mean'],
                  w['ddtm_max'], b['drawn_states'], b['traps'],
                  b['with_traps'], b['max_traps'],
                  b['deepest_trap_plies']), flush=True)
        if w.get('bellman_violations'):
            raise SystemExit('%s: Bellman violation in WTM scan'
                             % kind)
        if b.get('bellman_note'):
            raise SystemExit('%s: Bellman violation in BTM scan'
                             % kind)
    report['runtime_s'] = round(time.time() - t0, 1)
    out = os.path.join(RESULTS, 'trap_census.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print('frozen ->', out)
    print('T17 CENSUS PASSED')


if __name__ == '__main__':
    main()
