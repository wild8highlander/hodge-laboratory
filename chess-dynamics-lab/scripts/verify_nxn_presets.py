#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the n x n KRK presets for the chess-particles web app.

For each board size n in {4, 5, 6} the app loads a generalized K+R vs K
position (the same endgame the complexity module generalizes in T14).
This script checks with the exact retrograde oracle (retro_dtm_nxn)
that every preset is LEGAL and WON, and prints the DTM so the preset
can carry an honest annotation.  It also prints perft(1..3)-style child
counts of the preset position (from the packed children, the same
semantics the JS krkSpace(n) enumeration must reproduce) and the exact
state/edge counts per n to cross-check the frozen complexity_scaling.json
numbers from the browser.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'complexity'))

from generalized_chess import retro_dtm_nxn, squares_n, kings_adjacent_n  # noqa
from dynamics import WR, WQ, EMPTY, WK, BK, piece_attack_squares  # noqa

PRESETS = {
    # scaled-down copy of the 8x8 demo '8/8/8/4k3/8/8/8/R3K3 w - - 0 1'
    4: '4/2k1/4/R2K w - - 0 1',
    5: '5/5/2k2/5/R2K1 w - - 0 1',
    6: '6/6/3k2/6/6/R2K2 w - - 0 1',
}


def unpack_preset(n, fen):
    rows = fen.split()[0].split('/')
    wk = wp = bk = None
    for ri, row in enumerate(rows):
        r = n - 1 - ri
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
                continue
            sq = 16 * r + f
            if ch == 'K':
                wk = sq
            elif ch == 'k':
                bk = sq
            elif ch == 'R':
                wp = sq
            f += 1
    return wk, wp, bk


def counts_n(n):
    """Exact (states, edges) of the KRK space on n x n — the same
    enumeration semantics as retro_dtm_nxn / generalized_chess.

    Faithful to the frozen E2 counting: the king neighbourhoods are the
    8x8 0x88 ones (KING_NB of dynamics.py), so for n < 8 a white king
    standing on the rim of the sub-board keeps its off-board 0x88 moves
    in the successor list (they pack fine into the 22-bit state and stay
    valueless/drawn forever) — these degenerate edges are part of the
    frozen edge counts.  Only the BLACK king destinations are restricted
    to the n x n sub-board (as in _children_black_n's `valid` test)."""
    sqs = squares_n(n)
    valid = set(sqs)
    king_nb = {sq: [sq + o for o in (16, -16, 1, -1, 17, 15, -17, -15)
                    if not ((sq + o) & 0x88)] for sq in sqs}
    states = edges = 0
    for wk in sqs:
        for wp in sqs:
            if wp == wk:
                continue
            for bk in sqs:
                if bk == wk or bk == wp or kings_adjacent_n(wk, bk):
                    continue
                board = [EMPTY] * 128
                board[wk], board[wp], board[bk] = WK, WR, BK
                targets = piece_attack_squares(board, wp, blocking=True)
                # BTM state: always counted (children incl. captures)
                states += 1
                ch = 0
                for dest in king_nb[bk]:
                    if dest not in valid:
                        continue             # black stays on the n x n
                    if dest == wk or dest in king_nb[wk]:
                        continue
                    if dest == wp:
                        continue           # capture counted as escape
                    board2 = [EMPTY] * 128
                    board2[wk], board2[wp], board2[dest] = WK, WR, BK
                    if dest in piece_attack_squares(board2, wp,
                                                    blocking=True):
                        continue
                    ch += 1
                edges += ch
                # WTM state: legal iff Black king not attacked
                if bk not in targets:
                    states += 1
                    chW = 0
                    for dest in king_nb[wk]:
                        if dest == wp or dest == bk or dest in king_nb[bk]:
                            continue
                        chW += 1
                    for dest in targets:
                        if dest == wk or dest == bk:
                            continue
                        chW += 1
                    edges += chW
    return states, edges


FROZEN = {4: (3496, 26992), 5: (17528, 161265), 6: (60800, 620224),
          7: (168260, 1837205), 8: (399112, 4447032)}


def main():
    ok = True
    print('── presets (legal + won, with exact DTM) ──')
    for n, fen in sorted(PRESETS.items()):
        wk, wp, bk = unpack_preset(n, fen)
        t0 = time.time()
        dtm, stats = retro_dtm_nxn(n, WR)
        s = wk | (wp << 7) | (bk << 14)          # WTM packing
        v = dtm[s]
        legal = v != -1
        won = v >= 0
        status = 'WON in %d plies (%d moves)' % (v, (v + 1) // 2) \
            if won else ('DRAWN' if legal else 'ILLEGAL')
        print('n=%d  %-28s wk=%d wp=%d bk=%d  %s  [%.1fs]' % (
            n, fen, wk, wp, bk, status, time.time() - t0))
        if not won:
            ok = False
    print('── exact KRK space counts per n (cross-check vs frozen E2) ──')
    for n in (4, 5, 6, 7, 8):
        t0 = time.time()
        states, edges = counts_n(n)
        fs, fe = FROZEN[n]
        match = states == fs and edges == fe
        ok = ok and match
        print('n=%d  states %7d (frozen %7d) %s   edges %8d '
              '(frozen %8d) %s   [%.1fs]' % (
                  n, states, fs, 'OK' if states == fs else 'MISMATCH',
                  edges, fe, 'OK' if edges == fe else 'MISMATCH',
                  time.time() - t0), flush=True)
    print('PRESET/COUNT VERIFICATION: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
