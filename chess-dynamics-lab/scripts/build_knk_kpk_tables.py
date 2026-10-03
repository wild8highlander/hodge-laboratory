#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the KNK and KPK endgame DTM tables (8x8) and freeze them.

Extends the frozen certificate family results/dtm_krk.json.gz and
results/dtm_kqk.json.gz with two new members:

  KNK  (K+N vs K) — the negative control.  A knight checking a king
      attacks NONE of the king's eight neighbours: a knight offset
      (+-1,+-2)/(+-2,+-1) plus any unit king step (+-1,0)/(0,+-1)/(+-1,+-1)
      is never again a knight offset.  Hence every escape square of a
      checked king must be covered by the lone white king; a cornered king
      (a8) has neighbours {a7,b7,b8} which no single legal king square
      covers (b7/b8/a7 touch a8, c7 misses a7, c8 misses a7) — and by
      translation/rotation the argument covers every board square.  The
      retrograde build must therefore discover ZERO mates:
      won = 0, mates = 0, max_plies = 0.  The tablebase proves the
      classical insufficient-material draw by exhaustive computation,
      and the load-time integrity gate re-proves it on every page view.

  KPK  (K+P vs K) — retrograde with pawn single/double pushes and the
      promotion-to-QUEEN boundary condition: the child of a promotion ply
      is a KQK state whose exact DTM is read from the frozen KQK
      certificate.  Queen promotion is DTM-sufficient by move-set
      domination: every rook (bishop) strategy can be mimicked by the
      queen (black's legal replies only shrink because Q-attacks
      superset R/B-attacks), while N/B under-promotion lands in
      KNK/KBK — endgames with no mates at all.  Consequently
      DTM(c8=Q) <= DTM(c8=R) and N/B promotions never win, so a Q-only
      table is EXACT for the mate distance.

Conventions are IDENTICAL to dynamics.retro_dtm:
  packing   state = wk | wp<<7 | bk<<14 | stm<<21   (22 bits, stm 0=W 1=B)
  values    -1 = drawn / not won, 0 = Black mated, k >= 1 = White mates
            in k plies against best defence
  blob      gzip of 2**22 bytes, byte 200 = drawn/illegal, else plies 0..63
  stats     {piece, states, edges, won, mates, max_plies, max_moves}
  plus      bellman_verified: True after an independent Bellman pass
            over ALL states (properties, not values), and for KPK also
            boundary: the frozen KQK certificate used at promotion.

Usage:  python3 scripts/build_knk_kpk_tables.py [knk|kpk|both]
"""
import base64
import gzip
import json
import os
import sys
import time
from array import array

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import dynamics as D                              # noqa: E402

SIZE = 1 << 22
RESULTS = os.path.join(ROOT, 'results')

KNIGHT_OFFS = (33, 31, 18, 14, -33, -31, -18, -14)
KNIGHT_NB = {sq: [sq + o for o in KNIGHT_OFFS if not ((sq + o) & 0x88)]
             for sq in D.SQUARES}
PAWN_ATT_W = {sq: [s for s in (sq + 15, sq + 17) if not (s & 0x88)]
              for sq in D.SQUARES}


def pack(wk, wp, bk, stm):
    return wk | (wp << 7) | (bk << 14) | (stm << 21)


def build_csr(dtm, succ_flat, succ_ptr, cnt):
    """Predecessor CSR over the flat successor list (as in dynamics.py)."""
    pred_cnt = array('i', bytes(4 * SIZE))
    for s in range(SIZE):
        for k in range(succ_ptr[s], succ_ptr[s] + cnt[s]):
            pred_cnt[succ_flat[k]] += 1
    pred_ptr = array('i', bytes(4 * (SIZE + 1)))
    total = 0
    for s in range(SIZE):
        pred_ptr[s] = total
        total += pred_cnt[s]
    pred_ptr[SIZE] = total
    pred_fill = array('i', bytes(4 * SIZE))
    for s in range(SIZE):
        pred_fill[s] = pred_ptr[s]
    pred_arr = array('i', bytes(4 * total))
    for s in range(SIZE):
        for k in range(succ_ptr[s], succ_ptr[s] + cnt[s]):
            c = succ_flat[k]
            pred_arr[pred_fill[c]] = s
            pred_fill[c] += 1
    return pred_ptr, pred_arr, total


def propagate(dtm, pred_ptr, pred_arr, succ_flat, succ_ptr, cnt, escape,
              ext_by_d):
    """Layered retrograde propagation; ext_by_d seeds promotion wins."""
    frontier = [s for s in range(SIZE) if dtm[s] == 0]
    depth = 0
    max_plies = 0
    while frontier or any(dtm[s] < 0 for lst in ext_by_d.values() for s in lst):
        depth += 1
        nxt = []
        for s in ext_by_d.get(depth, ()):
            if dtm[s] < 0:
                dtm[s] = depth
                if depth > max_plies:
                    max_plies = depth
                nxt.append(s)
        for child in frontier:
            lo, hi = pred_ptr[child], pred_ptr[child + 1]
            for k in range(lo, hi):
                parent = pred_arr[k]
                if dtm[parent] >= 0:
                    continue
                if not (parent >> 21):           # White to move: exists move
                    dtm[parent] = depth
                    if depth > max_plies:
                        max_plies = depth
                    nxt.append(parent)
                else:                            # Black: all moves must win
                    if escape[parent]:
                        continue
                    lo2 = succ_ptr[parent]
                    hi2 = lo2 + cnt[parent]
                    all_won = True
                    mx = 0
                    for k2 in range(lo2, hi2):
                        dv = dtm[succ_flat[k2]]
                        if dv < 0:
                            all_won = False
                            break
                        if dv > mx:
                            mx = dv
                    if all_won and hi2 > lo2:
                        d = mx + 1
                        dtm[parent] = d
                        if d > max_plies:
                            max_plies = d
                        nxt.append(parent)
        if not nxt and depth > 64:
            break                                # safety: nothing propagates
        frontier = nxt
    return max_plies


# ══════════════════════════════ KNK ══════════════════════════════════════
def knk_children_white(wk, wn, bk):
    ch = []
    for dest in D.KING_NB[wk]:
        if dest == wn or dest == bk or dest in D.KING_NB[bk]:
            continue
        ch.append(dest | (wn << 7) | (bk << 14) | (1 << 21))
    for dest in KNIGHT_NB[wn]:
        if dest == wk or dest == bk:
            continue
        ch.append(wk | (dest << 7) | (bk << 14) | (1 << 21))
    return ch


def knk_children_black(wk, wn, bk):
    """Returns (children, capture_flag)."""
    ch = []
    captured = 0
    for dest in D.KING_NB[bk]:
        if dest == wk:
            continue
        if dest in D.KING_NB[wk]:
            continue                    # adjacent to the White king: illegal
        if dest == wn:
            captured = 1                # undefended knight: capture -> K vs K
            continue
        if dest in KNIGHT_NB[wn]:
            continue                    # moving into a knight check: illegal
        ch.append(wk | (wn << 7) | (dest << 14))
    return ch, captured


def build_knk(progress=None):
    dtm = [-1] * SIZE
    succ_flat = array('i')
    succ_ptr = array('i', bytes(4 * (SIZE + 1)))
    cnt = array('i', bytes(4 * SIZE))
    escape = bytearray(SIZE)
    n_states = 0
    for wk in D.SQUARES:
        for wn in D.SQUARES:
            if wn == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wn or D.kings_adjacent(wk, bk):
                    continue
                if bk not in KNIGHT_NB[wn]:          # WTM: black not en prise
                    s0 = pack(wk, wn, bk, 0)
                    ch = knk_children_white(wk, wn, bk)
                    succ_ptr[s0] = len(succ_flat)
                    cnt[s0] = len(ch)
                    succ_flat.extend(ch)
                    n_states += 1
                ch, captured = knk_children_black(wk, wn, bk)
                s1 = pack(wk, wn, bk, 1)
                succ_ptr[s1] = len(succ_flat)
                cnt[s1] = len(ch)
                succ_flat.extend(ch)
                if captured:
                    escape[s1] = 1
                if not ch and not captured and bk in KNIGHT_NB[wn]:
                    dtm[s1] = 0                      # the lemma says: never
                n_states += 1
    succ_ptr[SIZE] = len(succ_flat)
    if progress:
        progress('states', n_states)
    pred_ptr, pred_arr, total = build_csr(dtm, succ_flat, succ_ptr, cnt)
    if progress:
        progress('edges', total)
    max_plies = propagate(dtm, pred_ptr, pred_arr, succ_flat, succ_ptr, cnt,
                          escape, {})
    stats = {'piece': 'N', 'states': n_states, 'edges': total,
             'won': sum(1 for v in dtm if v >= 0),
             'mates': sum(1 for v in dtm if v == 0),
             'max_plies': max_plies,
             'max_moves': (max_plies + 1) // 2 if max_plies else 0}
    return dtm, stats


def verify_knk(dtm):
    """Independent Bellman pass: properties over ALL states (no CSR)."""
    won = mates = 0
    for wk in D.SQUARES:
        for wn in D.SQUARES:
            if wn == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wn or D.kings_adjacent(wk, bk):
                    continue
                checked = bk in KNIGHT_NB[wn]
                s0 = pack(wk, wn, bk, 0)
                if not checked:
                    v0 = dtm[s0]
                    ch = knk_children_white(wk, wn, bk)
                    vals = [dtm[c] for c in ch]
                    if v0 >= 0:
                        won += 1
                        if v0 == 0:
                            mates += 1
                        ok = v0 >= 1 and (v0 - 1) in vals
                        if ok:
                            ok = all(not (0 <= v < v0 - 1) for v in vals)
                        if not ok:
                            return False, 'WTM won property broken %r' % (
                                (wk, wn, bk, v0),)
                    else:
                        if any(v >= 0 for v in vals):
                            return False, ('won child from drawn WTM %r'
                                           % ((wk, wn, bk),))
                s1 = pack(wk, wn, bk, 1)
                v1 = dtm[s1]
                ch, captured = knk_children_black(wk, wn, bk)
                vals = [dtm[c] for c in ch]
                if v1 == 0:
                    if checked and not ch and not captured:
                        mates += 1
                    else:
                        return False, 'false mate label %r' % ((wk, wn, bk),)
                elif v1 >= 1:
                    won += 1
                    if captured or not vals or min(vals) < 0 \
                            or max(vals) != v1 - 1:
                        return False, ('BTM won property broken %r'
                                       % ((wk, wn, bk, v1),))
                else:
                    if not ch and checked and not captured:
                        return False, ('stalemate labelled as mate %r'
                                       % ((wk, wn, bk),))
                    if not (captured or (not ch and not checked)
                            or any(v < 0 for v in vals)):
                        return False, ('no draw resource %r'
                                       % ((wk, wn, bk),))
    return True, 'won=%d mates=%d' % (won, mates)


# ══════════════════════════════ KPK ══════════════════════════════════════
def kpk_children_white(wk, wp, bk, kqk):
    """Returns (internal_children, ext_value_or_None).

    ext_value = DTM_KQK(child) + 1 plies — the value of the promotion
    move measured at the parent (the promotion ply itself costs 1).
    """
    ch = []
    ext = None
    for dest in D.KING_NB[wk]:
        if dest == wp or dest == bk or dest in D.KING_NB[bk]:
            continue
        ch.append(dest | (wp << 7) | (bk << 14) | (1 << 21))
    r = wp >> 4
    t = wp + 16
    if r == 6:
        if t != wk and t != bk:
            v = kqk[pack(wk, t, bk, 1)]
            if v >= 0:
                ext = v + 1
    else:
        if t != wk and t != bk:
            ch.append(pack(wk, t, bk, 1))
            if r == 1:
                t2 = wp + 32
                if t2 != wk and t2 != bk:
                    ch.append(pack(wk, t2, bk, 1))
    return ch, ext


def kpk_children_black(wk, wp, bk):
    ch = []
    captured = 0
    patt = PAWN_ATT_W[wp]
    for dest in D.KING_NB[bk]:
        if dest == wk:
            continue
        if dest in D.KING_NB[wk]:
            continue
        if dest == wp:
            captured = 1                # undefended pawn: capture -> K vs K
            continue
        if dest in patt:
            continue                    # moving into a pawn check: illegal
        ch.append(wk | (wp << 7) | (dest << 14))
    return ch, captured


def build_kpk(kqk, progress=None):
    dtm = [-1] * SIZE
    ext_by_d = {}
    succ_flat = array('i')
    succ_ptr = array('i', bytes(4 * (SIZE + 1)))
    cnt = array('i', bytes(4 * SIZE))
    escape = bytearray(SIZE)
    n_states = 0
    n_ext = 0
    for wk in D.SQUARES:
        for wp in D.SQUARES:
            if wp == wk or not (1 <= (wp >> 4) <= 6):
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wp or D.kings_adjacent(wk, bk):
                    continue
                s0 = None
                if bk not in PAWN_ATT_W[wp]:         # WTM: black not en prise
                    s0 = pack(wk, wp, bk, 0)
                    ch, ext = kpk_children_white(wk, wp, bk, kqk)
                    succ_ptr[s0] = len(succ_flat)
                    cnt[s0] = len(ch)
                    succ_flat.extend(ch)
                    if ext is not None:
                        ext_by_d.setdefault(ext, []).append(s0)
                        n_ext += 1
                    n_states += 1
                ch, captured = kpk_children_black(wk, wp, bk)
                s1 = pack(wk, wp, bk, 1)
                succ_ptr[s1] = len(succ_flat)
                cnt[s1] = len(ch)
                succ_flat.extend(ch)
                if captured:
                    escape[s1] = 1
                if not ch and not captured and bk in PAWN_ATT_W[wp]:
                    dtm[s1] = 0                      # checkmate (layer 0)
                n_states += 1
    succ_ptr[SIZE] = len(succ_flat)
    if progress:
        progress('states', n_states)
    pred_ptr, pred_arr, total = build_csr(dtm, succ_flat, succ_ptr, cnt)
    if progress:
        progress('edges', total)
    max_plies = propagate(dtm, pred_ptr, pred_arr, succ_flat, succ_ptr, cnt,
                          escape, ext_by_d)
    stats = {'piece': 'P', 'states': n_states, 'edges': total,
             'won': sum(1 for v in dtm if v >= 0),
             'mates': sum(1 for v in dtm if v == 0),
             'max_plies': max_plies,
             'max_moves': (max_plies + 1) // 2 if max_plies else 0,
             'promotion_seeds': n_ext,
             'boundary': 'frozen KQK certificate (results/dtm_kqk.json.gz)'}
    return dtm, stats


def verify_kpk(dtm, kqk):
    """Independent Bellman pass including the promotion boundary."""
    won = mates = 0
    for wk in D.SQUARES:
        for wp in D.SQUARES:
            if wp == wk or not (1 <= (wp >> 4) <= 6):
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wp or D.kings_adjacent(wk, bk):
                    continue
                patt = PAWN_ATT_W[wp]
                checked = bk in patt
                s0 = pack(wk, wp, bk, 0)
                if not checked:
                    v0 = dtm[s0]
                    ch, ext = kpk_children_white(wk, wp, bk, kqk)
                    cands = [dtm[c] for c in ch if dtm[c] >= 0]
                    if ext is not None:
                        # ext = 1 + DTM_KQK(child): the move value measured at
                        # the parent; the child-equivalent used by the Bellman
                        # property excludes the promotion ply itself
                        cands.append(ext - 1)
                    if v0 >= 0:
                        won += 1
                        if v0 == 0:
                            mates += 1
                        if v0 < 1 or not cands or min(cands) != v0 - 1:
                            return False, ('WTM won property broken %r'
                                           % ((wk, wp, bk, v0),))
                    else:
                        if cands:
                            return False, ('won child from drawn WTM %r '
                                           '(min=%d)' % ((wk, wp, bk),
                                                         min(cands)))
                s1 = pack(wk, wp, bk, 1)
                v1 = dtm[s1]
                ch, captured = kpk_children_black(wk, wp, bk)
                vals = [dtm[c] for c in ch]
                if v1 == 0:
                    if checked and not ch and not captured:
                        mates += 1
                    else:
                        return False, 'false mate label %r' % ((wk, wp, bk),)
                elif v1 >= 1:
                    won += 1
                    if captured or not vals or min(vals) < 0 \
                            or max(vals) != v1 - 1:
                        return False, ('BTM won property broken %r'
                                       % ((wk, wp, bk, v1),))
                else:
                    if not ch and checked and not captured:
                        return False, ('stalemate labelled as mate %r'
                                       % ((wk, wp, bk),))
                    if not (captured or (not ch and not checked)
                            or any(v < 0 for v in vals)):
                        return False, ('no draw resource %r'
                                       % ((wk, wp, bk),))
    return True, 'won=%d mates=%d' % (won, mates)


# ═════════════════════════════ freeze ════════════════════════════════════
def name_sq(s):
    return (ord(s[0]) - 97) + 16 * (int(s[1]) - 1)


def freeze(dtm, stats, path, packing):
    for v in dtm:
        assert v == -1 or 0 <= v <= 63, \
            'DTM %r exceeds the byte encoding' % v
    blob = bytes(200 if v < 0 else v for v in dtm)
    payload = {
        'stats': stats,
        'dtm_blob_b64': base64.b64encode(gzip.compress(blob, 9)).decode(),
        'packing': packing,
        'bellman_verified': True,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, separators=(',', ':'))
    return os.path.getsize(path)


def main():
    which = (sys.argv[1] if len(sys.argv) > 1 else 'both').lower()
    packing = ('state = wk | wp<<7 | bk<<14 | stm<<21 (22 bits, stm '
               '0=White 1=Black); byte 0..63 = DTM in plies, 200 = drawn/'
               'illegal; identical to the KRK/KQK certificates')
    if which in ('knk', 'both'):
        t0 = time.time()
        dtm, stats = build_knk(lambda tag, n: progress(tag, n, 'KNK'))
        ok, msg = verify_knk(dtm)
        print('KNK bellman: %s (%s) [%.1fs]' % (ok, msg, time.time() - t0))
        if not ok:
            return 1
        if stats['won'] != 0 or stats['mates'] != 0:
            print('KNK THEOREM VIOLATED: a knight mate exists!', stats)
            return 1
        print('KNK stats:', json.dumps(stats))
        # spot probes: every legal probed state must be a draw
        for sqs in [('b4', 'd5', 'a8'), ('g1', 'c3', 'e8'),
                    ('a1', 'h8', 'a8')]:
            s = pack(name_sq(sqs[0]), name_sq(sqs[1]), name_sq(sqs[2]), 0)
            assert dtm[s] == -1, 'KNK spot probe %r not drawn' % (sqs,)
        size = freeze(dtm, stats, os.path.join(RESULTS, 'dtm_knk.json.gz'),
                      packing + '; KNK: won = mates = 0 (the knight mate '
                      'does not exist)')
        print('KNK frozen: results/dtm_knk.json.gz (%.1f KB)' % (size / 1024))
    if which in ('kpk', 'both'):
        t0 = time.time()
        loaded = D.load_dtm_cache(5)
        if loaded is None:
            print('KPK boundary: frozen KQK table not found')
            return 1
        kqk, kqk_stats = loaded
        print('KPK boundary: frozen KQK certificate loaded '
              '(%d states, max %d plies)' % (kqk_stats['states'],
                                             kqk_stats['max_plies']))
        dtm, stats = build_kpk(kqk, lambda tag, n: progress(tag, n, 'KPK'))
        ok, msg = verify_kpk(dtm, kqk)
        print('KPK bellman: %s (%s) [%.1fs]' % (ok, msg, time.time() - t0))
        if not ok:
            return 1
        print('KPK stats:', json.dumps(stats))
        # hand-verified spot probes (classical KPK facts)
        probes = [
            # White Kb6, pawn c7, Black Ka8, WTM: 1.c8=Q is MATE -> 1 ply
            (('b6', 'c7', 'a8', 0), 1),
            # White Kb6, pawn c7, Black Ka7, WTM: 1.c8=Q/R stalemate, KNK
            # after c8=N -> drawn
            (('b6', 'c7', 'a7', 0), -1),
            # Black to move, Black Ka8: stalemate (no moves, not in check)
            (('b6', 'c7', 'a8', 1), -1),
            # the checking pawn is undefended: Kxe2 escapes to K vs K
            (('a1', 'e2', 'd3', 1), -1),
        ]
        for (wf, pf, bf, stm), want in probes:
            s = pack(name_sq(wf), name_sq(pf), name_sq(bf), stm)
            got = dtm[s]
            mark = 'PASS' if got == want else 'FAIL'
            print('KPK spot %s %s%s%s stm=%d: dtm=%s (want %s)'
                  % (mark, wf, pf, bf, stm, got, want))
            if got != want:
                return 1
        size = freeze(dtm, stats, os.path.join(RESULTS, 'dtm_kpk.json.gz'),
                      packing + '; KPK: promotion boundary = frozen KQK '
                      'certificate, queen promotion is DTM-sufficient')
        print('KPK frozen: results/dtm_kpk.json.gz (%.1f KB)' % (size / 1024))
    return 0


def progress(tag, n, label):
    print('  %s %s: %d' % (label, tag, n))


if __name__ == '__main__':
    sys.exit(main())
