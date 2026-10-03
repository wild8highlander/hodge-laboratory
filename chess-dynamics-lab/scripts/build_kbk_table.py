#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the KBK endgame DTM table (8x8) and freeze it.

Extends the frozen certificate family results/dtm_*.json.gz with the
DIAGONAL negative control:

  KBK  (K+B vs K) — a lone bishop can never mate.  A bishop attacks only
      squares of one colour complex; a checked king on colour C always
      has orthogonal neighbours on the opposite colour, which no bishop
      ever attacks, and the lone white king cannot cover them all without
      standing next to the checked king.  The retrograde build must
      therefore discover ZERO mates:  won = 0, mates = 0, max_plies = 0 —
      the insufficient-material theorem proved by exhaustive computation,
      exactly as KNK proved the knight case.  Two negative controls with
      different board geometries (knight offsets vs diagonal rays) make
      the "no forced win" family structural, not anecdotal.

Implementation note: the children generators of the KRK/KQK builder
(dynamics._children_white / dynamics._children_black) are piece-code
generic, so the KBK build reuses them verbatim with the bishop code —
including the correct x-ray handling when the black king steps along a
bishop ray (the vacated square re-opens the attack).

Conventions are IDENTICAL to the KRK/KQK/KNK/KPK certificates:
  packing   state = wk | wp<<7 | bk<<14 | stm<<21   (22 bits, stm 0=W 1=B)
  values    -1 = drawn / not won, 0 = Black mated, k >= 1 = White mates
            in k plies against best defence
  blob      gzip of 2**22 bytes, byte 200 = drawn/illegal, else plies 0..63
  stats     {piece, states, edges, won, mates, max_plies, max_moves}
  plus      bellman_verified: True after an independent Bellman pass
            over ALL states (properties, not values).

Usage:  python3 scripts/build_kbk_table.py
"""
import base64
import json
import os
import sys
import time
from array import array

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dynamics as D                                        # noqa: E402
import build_knk_kpk_tables as B                            # noqa: E402

SIZE = B.SIZE
RESULTS = B.RESULTS


def pack(wk, wb, bk, stm):
    return wk | (wb << 7) | (bk << 14) | (stm << 21)


def bishop_targets(wk, wb, bk):
    """Squares attacked by the bishop with the full board in place."""
    board = [D.EMPTY] * 128
    board[wk], board[wb], board[bk] = D.WK, D.WB, D.BK
    return D.piece_attack_squares(board, wb, blocking=True)


def build_kbk(progress=None):
    """Retrograde build.  The frontier is expected to be EMPTY (no mate
    seeds): the layered propagation then terminates at depth 1 having
    proven that every state is drawn."""
    dtm = [-1] * SIZE
    succ_flat = array('i')
    succ_ptr = array('i', bytes(4 * (SIZE + 1)))
    cnt = array('i', bytes(4 * SIZE))
    escape = bytearray(SIZE)
    n_states = 0
    n_stalemate = 0
    for wk in D.SQUARES:
        for wb in D.SQUARES:
            if wb == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wb or D.kings_adjacent(wk, bk):
                    continue
                targets = bishop_targets(wk, wb, bk)
                if bk not in targets:                 # WTM: black not en prise
                    s0 = pack(wk, wb, bk, 0)
                    ch = D._children_white(wk, wb, bk, D.WB)
                    succ_ptr[s0] = len(succ_flat)
                    cnt[s0] = len(ch)
                    succ_flat.extend(ch)
                    n_states += 1
                ch, captured = D._children_black(wk, wb, bk, D.WB)
                s1 = pack(wk, wb, bk, 1)
                succ_ptr[s1] = len(succ_flat)
                cnt[s1] = len(ch)
                succ_flat.extend(ch)
                if captured:
                    escape[s1] = 1                    # bishop falls: K vs K
                if not ch and not captured and bk in targets:
                    dtm[s1] = 0                       # checkmate: the lemma says NEVER
                if not ch and not captured and bk not in targets:
                    n_stalemate += 1                  # stalemate: a legal draw
                n_states += 1
    succ_ptr[SIZE] = len(succ_flat)
    if progress:
        progress('states', n_states)
    pred_ptr, pred_arr, total = B.build_csr(dtm, succ_flat, succ_ptr, cnt)
    if progress:
        progress('edges', total)
    max_plies = B.propagate(dtm, pred_ptr, pred_arr, succ_flat, succ_ptr,
                            cnt, escape, {})
    stats = {'piece': 'B', 'states': n_states, 'edges': total,
             'won': sum(1 for v in dtm if v >= 0),
             'mates': sum(1 for v in dtm if v == 0),
             'max_plies': max_plies,
             'max_moves': (max_plies + 1) // 2 if max_plies else 0,
             'stalemates': n_stalemate}
    return dtm, stats


def verify_kbk(dtm):
    """Independent Bellman pass: properties over ALL states (no CSR).

    Checks, state by state and from geometry alone:
      1. no state carries a won label (won = 0),
      2. no BTM state satisfies the checkmate condition (the theorem),
      3. every label-less BTM state has a draw resource: a legal move, a
         capture, or stalemate-as-draw."""
    won = mates = 0
    for wk in D.SQUARES:
        for wb in D.SQUARES:
            if wb == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wb or D.kings_adjacent(wk, bk):
                    continue
                checked = bk in bishop_targets(wk, wb, bk)
                s0 = pack(wk, wb, bk, 0)
                if not checked:
                    v0 = dtm[s0]
                    ch = D._children_white(wk, wb, bk, D.WB)
                    if v0 >= 0:
                        won += 1
                        if v0 == 0:
                            mates += 1
                        ok = v0 >= 1 and (v0 - 1) in [dtm[c] for c in ch]
                        if not ok:
                            return False, 'WTM won property broken %r' % (
                                (wk, wb, bk, v0),)
                    else:
                        if any(dtm[c] >= 0 for c in ch):
                            return False, ('won child from drawn WTM %r'
                                           % ((wk, wb, bk),))
                s1 = pack(wk, wb, bk, 1)
                v1 = dtm[s1]
                ch, captured = D._children_black(wk, wb, bk, D.WB)
                if v1 == 0:
                    if checked and not ch and not captured:
                        mates += 1                    # unreachable by theorem
                    else:
                        return False, 'false mate label %r' % ((wk, wb, bk),)
                elif v1 >= 1:
                    won += 1
                    if captured or not ch or min(dtm[c] for c in ch) < 0:
                        return False, ('BTM won property broken %r'
                                       % ((wk, wb, bk, v1),))
                else:
                    if not ch and checked and not captured:
                        return False, ('MATE MISSED — diagonal theorem '
                                       'violated %r' % ((wk, wb, bk),))
                    if not (captured or (not ch and not checked)
                            or any(dtm[c] < 0 for c in ch)):
                        return False, ('no draw resource %r'
                                       % ((wk, wb, bk),))
    return True, 'won=%d mates=%d' % (won, mates)


def name_sq(s):
    return (ord(s[0]) - 97) + 16 * (int(s[1]) - 1)


def main():
    t0 = time.time()
    dtm, stats = build_kbk(lambda tag, n: progress(tag, n, 'KBK'))
    ok, msg = verify_kbk(dtm)
    print('KBK bellman: %s (%s) [%.1fs]' % (ok, msg, time.time() - t0))
    if not ok:
        return 1
    if stats['won'] != 0 or stats['mates'] != 0:
        print('KBK THEOREM VIOLATED: a lone-bishop mate exists!', stats)
        return 1
    print('KBK stats:', json.dumps(stats))
    # spot probes: classical KBK facts, every legal state must be a draw
    for sqs in [('c4', 'd5', 'a8'), ('a1', 'h8', 'a8'),
                ('e4', 'f5', 'h1'), ('b2', 'c3', 'a7')]:
        for stm in (0, 1):
            s = pack(name_sq(sqs[0]), name_sq(sqs[1]), name_sq(sqs[2]), stm)
            assert dtm[s] == -1, 'KBK spot probe %r stm=%d not drawn' % (sqs, stm)
    packing = ('state = wk | wp<<7 | bk<<14 | stm<<21 (22 bits, stm 0=White '
               '1=Black); byte 0..63 = DTM in plies, 200 = drawn/illegal; '
               'identical to the KRK/KQK certificates')
    size = B.freeze(dtm, stats, os.path.join(RESULTS, 'dtm_kbk.json.gz'),
                    packing + '; KBK: won = mates = 0 (the lone-bishop mate '
                    'does not exist)')
    print('KBK frozen: results/dtm_kbk.json.gz (%.1f KB)' % (size / 1024))
    return 0


def progress(tag, n, label):
    print('  %s %s: %d' % (label, tag, n))


if __name__ == '__main__':
    sys.exit(main())
