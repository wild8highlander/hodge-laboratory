#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  COMPLEXITY LABORATORY · generalized_chess.py
  chess-dynamics-lab — module for the EXPTIME barrier study.

  Program author: Isaev Iskhak Khamzatovich
  Repository: github.com/wild8highlander/chess-dynamics-lab
  License: individual exclusive license (see LICENSE)

  PURPOSE.

    The user question behind this module:

        "Generalized chess on an n x n board is EXPTIME-complete.
         If someone found a polynomial algorithm for it, that would mean
         P = EXPTIME and a collapse of complexity classes."

    This module turns the question into an EXPERIMENT and two THEOREMS
    (documented in the monograph paper "The Particle Limit"):

      T13 (impossibility)    P ⊊ EXPTIME is a THEOREM (deterministic time
                             hierarchy, Hartmanis–Stearns 1965), so a
                             polynomial algorithm for EXPTIME-complete
                             generalized chess CANNOT exist. The "if someone
                             found" scenario is logically inconsistent —
                             not merely unlikely.

      T14 (particle horizon) What CAN be polynomial:
                             (i)   the three-layer particle solver picks a
                                   move in O(n^4) time — but it is only an
                                   APPROXIMATOR (its loss rate against the
                                   exact oracle is measured, not assumed);
                             (ii)  for a FIXED number of pieces k the number
                                   of states is O(n^{2k-2}) — polynomial in
                                   n — so the retrograde oracle itself is
                                   polynomial in n for fixed k; the
                                   exponential wall lives in k, not in n;
                             (iii) for growing k any greedy polynomial
                                   solver loses the win on some positions
                                   (the exponential "tunnel" argument).

    THE CODE IS HONEST: ParticleSolver never looks at any DTM table. Its
    quality against the exact retrograde oracle is measured, not assumed.

  CONTENTS.

    ParticleSolver       three-layer greedy move chooser (K3 threat pressure
                         + TORUS Lagrangian energy; KLEIN determinism via a
                         lexicographic tie-break). O(n^4) per move.
    squares_n(n)         0x88 square list of an n x n board (n <= 8).
    position_from_state / state_of_position
                         bridges between packed KRK/KQK states and Position.
    retro_dtm_nxn        exact retrograde DTM for K+R/K+Q vs K on n x n
                         boards (the dynamics.retro_dtm algorithm,
                         generalized); reproduces the frozen 8x8 tables
                         bit-exactly (verified in experiment_scaling.py).
    ParticleSolver.playout
                         full particle-vs-particle greedy game.

  CLI:
    python3 complexity/generalized_chess.py --selftest    sanity checks
    python3 complexity/generalized_chess.py --demo        one oracle game
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
from array import array

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynamics import (  # noqa: E402
    EMPTY, WR, WQ, WK, BK, KING_DIRS, KING_NB,
    piece_attack_squares, threat_field, material, pseudo_mobility,
    Position, move_to_uci, pack_state,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1. THE PARTICLE SOLVER (Layer K3 + Layer TORUS; polynomial move chooser)
# ══════════════════════════════════════════════════════════════════════════════

class ParticleSolver:
    """Greedy three-layer move chooser. KNOWS NOTHING ABOUT DTM TABLES.

    For the side `s` to move, a candidate move m is scored on the resulting
    position:

        score(m) = [material(s) - material(-s)]                    (potential)
                 + mu * [mobility(s) - mobility(-s)]               (kinetic)
                 + lam * mean_{c ~ K(-s)} Theta_s[c]               (K3 pressure)

    where Theta_s is the threat field of side s (Theorem T04), K(-s) is the
    enemy king square plus its king-neighbourhood, mu = 0.1 (T05 constant),
    lam = 0.25 (K3 pressure weight). The chooser takes the argmax with a
    deterministic lexicographic UCI tie-break (KLEIN determinism).

    Cost per move: O(#moves x (movegen + field)) = O(n^2 * k * n^2) = O(n^4 k)
    for k particles on an n x n board — POLYNOMIAL in the board size.
    """

    def __init__(self, mu=0.1, lam=0.25, n=8):
        self.mu = mu
        self.lam = lam
        self.n = n
        valid = set(squares_n(n))
        self.valid = valid
        self.king_nb = {sq: [sq + o for o in KING_DIRS if (sq + o) in valid]
                        for sq in valid}

    # ── scoring of one candidate move ────────────────────────────────────
    def score_after(self, pos, m):
        """Particle score of the position after move m, from the viewpoint
        of the side that made the move. Position is restored before return."""
        s = pos.side
        undo = pos.make(m)
        try:
            mat = material(pos, s) - material(pos, -s)
            mob = pseudo_mobility(pos, s) - pseudo_mobility(pos, -s)
            theta = threat_field(pos, s)
            ek = pos.king_sq(-s)
            cells = [ek] + self.king_nb.get(ek, [])
            pressure = sum(theta[c] for c in cells) / float(len(cells))
            return mat + self.mu * mob + self.lam * pressure
        finally:
            pos.unmake(undo)

    # ── the polynomial move chooser ──────────────────────────────────────
    def choose_move(self, pos, node_counter=None):
        """argmax over legal moves of the particle score; None if no moves.
        Tie-break: lexicographically smallest UCI (deterministic)."""
        moves = pos.legal_moves()
        if not moves:
            return None
        if node_counter is not None:
            node_counter[0] += len(moves)
        best, best_key = None, None
        for m in moves:
            sc = self.score_after(pos, m)
            key = (-sc, move_to_uci(m))     # min-tuple == max score, lex uci
            if best_key is None or key < best_key:
                best, best_key = m, key
        return best

    # ── full greedy playout ───────────────────────────────────────────────
    def playout(self, pos, max_plies=512):
        """Particle-vs-particle game; returns (plies, final_position)."""
        p = 0
        seen = set()
        while p < max_plies:
            m = self.choose_move(pos)
            if m is None:
                break
            pos.make(m)
            p += 1
            key = tuple(pos.board) + (pos.side,)
            if key in seen:                 # repetition: greedy loop
                break
            seen.add(key)
        return p, pos


# ══════════════════════════════════════════════════════════════════════════════
# 2. GENERALIZED BOARD GEOMETRY (n x n, n <= 8 — 0x88 keeps 7-bit squares)
# ══════════════════════════════════════════════════════════════════════════════

def squares_n(n):
    """0x88 squares of an n x n board. Valid for 1 <= n <= 8 (the squares are
    a subset of the 8x8 square set, so pack_state indices stay compatible)."""
    return [16 * r + f for r in range(n) for f in range(n)]


def kings_adjacent_n(a, b):
    return max(abs((a & 7) - (b & 7)), abs((a >> 4) - (b >> 4))) <= 1


def _board3(wk, wp, bk, piece):
    b = [EMPTY] * 128
    b[wk], b[wp], b[bk] = WK, piece, BK
    return b


def position_from_state(wk, wp, bk, stm, piece=WR):
    """Build a Position from packed KRK/KQK coordinates (piece = WR or WQ).
    Returns None for an illegal triple (overlap, adjacent kings, or the
    black king en prise with White to move)."""
    if wk == wp or wk == bk or wp == bk or kings_adjacent_n(wk, bk):
        return None
    if stm == 0 and bk in piece_attack_squares(_board3(wk, wp, bk, piece),
                                               wp, blocking=True):
        return None
    pos = Position()
    pos.board = _board3(wk, wp, bk, piece)
    pos.side = 1 if stm == 0 else -1
    return pos


def state_of_position(pos):
    """(wk, wp, bk, stm) of a KRK/KQK Position, or None if the piece set
    differs from {WK, BK, exactly one strong white piece}."""
    wk = wp = bk = None
    code = 0
    for sq in range(128):
        p = pos.board[sq]
        if p == EMPTY:
            continue
        if p == WK:
            if wk is not None:
                return None
            wk = sq
        elif p == BK:
            if bk is not None:
                return None
            bk = sq
        elif p in (WR, WQ):
            if wp is not None or (code and code != p):
                return None
            wp, code = sq, p
        else:
            return None
    if wk is None or wp is None or bk is None:
        return None
    return wk, wp, bk, 0 if pos.side == 1 else 1


# ══════════════════════════════════════════════════════════════════════════════
# 3. GENERALIZED RETROGRADE DTM (K+R / K+Q vs K on an n x n board)
# ══════════════════════════════════════════════════════════════════════════════

def _children_white_n(wk, wq, bk, code, board):
    """White-to-move children (packed ints) of (wk, wq, bk) on any n<=8 board
    (all squares involved already lie on the n x n board by construction)."""
    ch = []
    for dest in KING_NB[wk]:
        if dest == wq or dest == bk or dest in KING_NB[bk]:
            continue
        ch.append(dest | (wq << 7) | (bk << 14) | (1 << 21))
    board[wk], board[wq], board[bk] = WK, code, BK
    for dest in piece_attack_squares(board, wq, blocking=True):
        if dest == wk or dest == bk:
            continue
        ch.append(wk | (dest << 7) | (bk << 14) | (1 << 21))
    return ch


def _children_black_n(wk, wq, bk, code, board, valid):
    """Black-to-move children; returns (children, capture_flag). The set
    `valid` restricts every square to the n x n board."""
    ch = []
    captured = 0
    board[wk], board[wq], board[bk] = WK, code, BK
    for dest in KING_NB[bk]:
        if dest not in valid:
            continue                     # off-board for this n
        if dest == wk:
            continue
        if dest in KING_NB[wk]:
            continue                     # adjacent to the White king: illegal
        if dest == wq:
            captured = 1                 # legal capture of an undefended piece
            continue                     # -> K vs K afterwards: draw
        # Test legality on a board WITHOUT the old black king (it has moved
        # to dest): dynamics._children_black builds board2 = {wk, wq, dest}.
        # Keeping BK on bk would let the phantom king block the rook line.
        board[bk] = EMPTY
        board[dest] = BK
        hit = dest in piece_attack_squares(board, wq, blocking=True)
        board[dest] = EMPTY
        board[bk] = BK
        if hit:
            continue                     # moving into check: illegal
        ch.append(wk | (wq << 7) | (dest << 14))
    return ch, captured


def retro_dtm_nxn(n, strong_piece=WR, progress=None):
    """Exact DTM (in plies) for K+R vs K / K+Q vs K on an n x n board.

    The same layered retrograde algorithm as dynamics.retro_dtm (Bellman
    induction over the full state space, CSR predecessor lists). For n = 8
    the result is bit-identical to the frozen results/dtm_*.json.gz tables
    (verified by experiment_scaling.py). dtm[s] = -1 means the state is
    illegal/unreachable or game-theoretically drawn; 0 = checkmate.

    Returns (dtm, stats). Wall-clock time is O(n^6) states x O(n^2) work.
    """
    code = WQ if strong_piece == 5 else WR
    SIZE = 1 << 22
    dtm = [-1] * SIZE
    valid = set(squares_n(n))
    sqs = sorted(valid)

    # ── pass 1: enumerate states, build flat successor list ───────────────
    succ_flat = array('i')
    succ_ptr = array('i', bytes(4 * (SIZE + 1)))
    cnt = array('i', bytes(4 * SIZE))
    escape = bytearray(SIZE)
    n_states = 0
    board = [EMPTY] * 128
    for wk in sqs:
        for wq in sqs:
            if wq == wk:
                continue
            for bk in sqs:
                if bk == wk or bk == wq or kings_adjacent_n(wk, bk):
                    continue
                # FRESH board per triple: stale pieces from the previous
                # triple would act as phantom blockers/attackers (the n=8
                # check against the frozen table catches exactly this).
                board = [EMPTY] * 128
                board[wk], board[wq], board[bk] = WK, code, BK
                targets = piece_attack_squares(board, wq, blocking=True)
                if bk not in targets:
                    s0 = pack_state(wk, wq, bk, 0)
                    ch = _children_white_n(wk, wq, bk, code, board)
                    succ_ptr[s0] = len(succ_flat)
                    cnt[s0] = len(ch)
                    succ_flat.extend(ch)
                    n_states += 1
                ch, captured = _children_black_n(wk, wq, bk, code, board,
                                                 valid)
                s1 = pack_state(wk, wq, bk, 1)
                succ_ptr[s1] = len(succ_flat)
                cnt[s1] = len(ch)
                succ_flat.extend(ch)
                if captured:
                    escape[s1] = 1
                if not ch and not captured and bk in targets:
                    dtm[s1] = 0                # checkmate (layer 0)
                n_states += 1
    succ_ptr[SIZE] = len(succ_flat)
    total = len(succ_flat)
    if progress:
        progress("states", n_states)
        progress("edges", total)

    # ── predecessor CSR (count + fill) ────────────────────────────────────
    pred_cnt = array('i', bytes(4 * SIZE))
    for s in range(SIZE):
        for k in range(succ_ptr[s], succ_ptr[s] + cnt[s]):
            pred_cnt[succ_flat[k]] += 1
    pred_ptr = array('i', bytes(4 * (SIZE + 1)))
    acc = 0
    for s in range(SIZE):
        pred_ptr[s] = acc
        acc += pred_cnt[s]
    pred_ptr[SIZE] = acc
    pred_arr = array('i', bytes(4 * acc))
    fill_pos = pred_ptr[:-1].tolist()
    for s in range(SIZE):
        for k in range(succ_ptr[s], succ_ptr[s] + cnt[s]):
            c = succ_flat[k]
            pred_arr[fill_pos[c]] = s
            fill_pos[c] += 1

    # ── layered retrograde propagation (Bellman) ──────────────────────────
    frontier = [s for s in range(SIZE) if dtm[s] == 0]
    depth = 0
    max_plies = 0
    while frontier:
        depth += 1
        nxt = []
        for child in frontier:
            lo, hi = pred_ptr[child], pred_ptr[child + 1]
            for k in range(lo, hi):
                parent = pred_arr[k]
                if dtm[parent] >= 0:
                    continue
                if not (parent >> 21):         # White to move: exists a move
                    dtm[parent] = depth
                    if depth > max_plies:
                        max_plies = depth
                    nxt.append(parent)
                else:                          # Black to move: ALL moves win
                    if escape[parent]:
                        continue               # Black recaptures: draw
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
                    if all_won:
                        d = mx + 1
                        dtm[parent] = d
                        if d > max_plies:
                            max_plies = d
                        nxt.append(parent)
        frontier = nxt

    stats = {'n': n, 'piece': 'Q' if code == WQ else 'R',
             'states': n_states, 'edges': total,
             'won': sum(1 for v in dtm if v >= 0),
             'mates': sum(1 for v in dtm if v == 0),
             'max_plies': max_plies,
             'max_moves': (max_plies + 1) // 2 if max_plies >= 0 else -1}
    return dtm, stats


# ══════════════════════════════════════════════════════════════════════════════
# 4. SELF-TEST AND DEMO
# ══════════════════════════════════════════════════════════════════════════════

def _selftest():
    """Sanity: state bridges are inverse functions; the 4x4 retrograde
    terminates with a plausible DTM landscape; the solver stays legal and
    deterministic."""
    pos = Position()
    pos.set_fen('8/8/8/4k3/8/8/8/R3K3 w - - 0 1')
    st = state_of_position(pos)
    assert st is not None, 'state_of_position failed on a KRK position'
    wk, wp, bk, stm = st
    pos2 = position_from_state(wk, wp, bk, stm, WR)
    assert pos2 is not None and pos2.to_fen() == pos.to_fen(), \
        'position_from_state is not the inverse of state_of_position'

    t0 = time.time()
    dtm, stats = retro_dtm_nxn(4, WR)
    el = time.time() - t0
    assert stats['mates'] > 0 and stats['won'] > 0, 'empty 4x4 table'
    print('4x4 KRK retrograde: %d states, %d won, %d mates, max DTM %d moves,'
          ' %.1fs' % (stats['states'], stats['won'], stats['mates'],
                      stats['max_moves'], el))

    solver = ParticleSolver(n=8)
    picked = []
    for _ in range(5):
        m = solver.choose_move(pos)
        assert m is not None and m in pos.legal_moves(), \
            'solver chose an illegal move'
        picked.append(move_to_uci(m))
        pos.make(m)
        if not pos.legal_moves():
            break
    print('particle solver: 5 deterministic greedy plies, all legal:',
          ' '.join(picked))
    print('SELFTEST OK')


def _demo():
    """One particle-vs-oracle KRK game: every particle move is checked
    against the frozen 8x8 DTM table (before / after)."""
    from dynamics import load_dtm_cache, dtm_state_of
    loaded = load_dtm_cache('R')
    assert loaded is not None, 'results/dtm_krk.json.gz not found'
    dtm, _ = loaded
    pos = Position()
    pos.set_fen('8/8/8/4k3/8/8/8/R3K3 w - - 0 1')
    solver = ParticleSolver(n=8)
    print('FEN                          move   DTM-before  DTM-after')
    for ply in range(40):
        st = state_of_position(pos)
        if st is None:
            print('position left the K+R vs K space')
            break
        d0 = dtm_state_of(dtm, *st)
        m = solver.choose_move(pos)
        if m is None:
            print('no legal moves after %d plies (mate or stalemate)' % ply)
            break
        uci = move_to_uci(m)
        pos.make(m)
        st1 = state_of_position(pos)
        d1 = dtm_state_of(dtm, *st1) if st1 else -3
        print('%-28s %-6s %-10s %s' % (pos.to_fen().split()[0], uci, d0, d1))
    print('DEMO OK')


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ran = False
    if '--selftest' in argv:
        _selftest()
        ran = True
    if '--demo' in argv:
        _demo()
        ran = True
    if not ran:
        _selftest()
    return 0


if __name__ == '__main__':
    sys.exit(main())
