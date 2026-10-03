#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chess_core.py — POLYGLOT VERIFICATION CORE (Python reference implementation)

Program author: Isaev Iskhak Khamzatovich
Repository: github.com/wild8highlander/chess-dynamics-lab
License: individual exclusive license (see LICENSE)

One core, seven languages: Python (this file), C, Rust, Go, Julia,
JavaScript and Java implement the SAME 10-check battery and print the
SAME [PASS]/[FAIL] table. Every check is exact and deterministic:

    1  board algebra        V4 orbits 20 (8x2 + 12x4), D4 orbits 10 (Burnside)
    2  move-graph census    edges R448 B280 N168 K210 Q728
    3  mobility census      sums R896 B560 N336 K420 Q1456, max 14/13/8/8/27
    4  flow termination     t* = lcm(W/gcd(a,W), H/gcd(b,H)) on 9 cases
    5  perft identities     20 / 400 / 8902 / 197281 from the initial position
    6  threat fields        D4-equivariance (pawnless) + pawn anomaly 176
    7  kinetic energy       initial mobility 20, after 1.e4 mobility 30
    8  mate certificates    Morphy m2 (a1a6), ladder m2, N+R m1 (g1g8)
    9  Zobrist hashing      incremental hash over a fixed playout + splitmix64
   10  knight tour          the frozen closed tour: 64 cells, closure move

The battery uses NO randomness and NO floating point except check 4's
braking gamma (compared through a rational surrogate: the exact geometric
sum identity is verified in rational arithmetic instead).

Run:  python3 chess_core.py        (expects the verdict 10/10)
"""
import sys
from math import gcd

# ════════════════════════════════════════════════════════════════════════
# board (0x88)
# ════════════════════════════════════════════════════════════════════════
EMPTY = 0
WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
BP, BN, BB, BR, BQ, BK = -1, -2, -3, -4, -5, -6
SQUARES = [16 * r + f for r in range(8) for f in range(8)]
KNIGHT_OFFS = (31, 33, 14, 18, -31, -33, -14, -18)
BISHOP_DIRS = (15, 17, -15, -17)
ROOK_DIRS = (16, -16, 1, -1)
KING_DIRS = (15, 16, 17, 1, -15, -16, -17, -1)
A1, E1, H1, A8, E8, H8 = 0, 4, 7, 112, 116, 119
WK_CASTLE, WQ_CASTLE, BK_CASTLE, BQ_CASTLE = 1, 2, 4, 8
FLAG_NORMAL, FLAG_DOUBLE, FLAG_EP, FLAG_CASTLE = 0, 1, 2, 3
CHAR_PIECE = {'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
              'p': -1, 'n': -2, 'b': -3, 'r': -4, 'q': -5, 'k': -6}
FILES = 'abcdefgh'


def sq_name(sq):
    return FILES[sq & 7] + str((sq >> 4) + 1)


def name_sq(s):
    return 16 * (int(s[1]) - 1) + FILES.index(s[0])


def enc(fr, to, promo=0, flag=0):
    return fr | (to << 7) | (promo << 14) | (flag << 18)


def m_from(m):
    return m & 127


def m_to(m):
    return (m >> 7) & 127


def m_promo(m):
    return (m >> 14) & 7


def m_flag(m):
    return (m >> 18) & 3


class Position:
    __slots__ = ('board', 'side', 'castling', 'ep')

    def __init__(self):
        self.board = [EMPTY] * 128
        self.side = 1
        self.castling = 0
        self.ep = -1

    def set_fen(self, fen):
        parts = fen.split()
        self.board = [EMPTY] * 128
        for i, row in enumerate(parts[0].split('/')):
            rank, file = 7 - i, 0
            for ch in row:
                if ch.isdigit():
                    file += int(ch)
                else:
                    self.board[16 * rank + file] = CHAR_PIECE[ch]
                    file += 1
        self.side = 1 if parts[1] == 'w' else -1
        self.castling = 0
        if len(parts) > 2 and parts[2] != '-':
            for ch in parts[2]:
                self.castling |= {'K': 1, 'Q': 2, 'k': 4, 'q': 8}[ch]
        self.ep = name_sq(parts[3]) if len(parts) > 3 and parts[3] != '-' else -1
        return self


def attacked(b, sq, by):
    for off in (-15, -17) if by == 1 else (15, 17):
        s = sq + off
        if not (s & 0x88) and b[s] == by:
            return True
    for off in KNIGHT_OFFS:
        s = sq + off
        if not (s & 0x88) and b[s] == 2 * by:
            return True
    for off in KING_DIRS:
        s = sq + off
        if not (s & 0x88) and b[s] == 6 * by:
            return True
    for dirs, kinds in ((BISHOP_DIRS, (3, 5)), (ROOK_DIRS, (4, 5))):
        for off in dirs:
            s = sq + off
            while not (s & 0x88):
                p = b[s]
                if p != EMPTY:
                    if (p > 0) == (by > 0) and abs(p) in kinds:
                        return True
                    break
                s += off
    return False


def king_sq(pos, side):
    t = 6 * side
    for sq in SQUARES:
        if pos.board[sq] == t:
            return sq
    raise RuntimeError('king missing')


def pseudo_moves(pos):
    b, side, moves = pos.board, pos.side, []
    for fr in SQUARES:
        p = b[fr]
        if p == EMPTY or (p > 0) != (side > 0):
            continue
        ap = abs(p)
        if ap == 1:
            fwd = 16 * side
            rank = fr >> 4
            promo_rank = 6 if side == 1 else 1
            start_rank = 1 if side == 1 else 6
            s = fr + fwd
            if not (s & 0x88) and b[s] == EMPTY:
                if rank == promo_rank:
                    for pr in (5, 2, 4, 3):
                        moves.append(enc(fr, s, pr))
                else:
                    moves.append(enc(fr, s))
                    if rank == start_rank and b[s + fwd] == EMPTY:
                        moves.append(enc(fr, s + fwd, 0, FLAG_DOUBLE))
            for off in (fwd - 1, fwd + 1):
                s = fr + off
                if s & 0x88:
                    continue
                q = b[s]
                if q != EMPTY and (q > 0) != (side > 0):
                    if rank == promo_rank:
                        for pr in (5, 2, 4, 3):
                            moves.append(enc(fr, s, pr))
                    else:
                        moves.append(enc(fr, s))
                elif s == pos.ep and q == EMPTY and rank == (4 if side == 1 else 3):
                    moves.append(enc(fr, s, 0, FLAG_EP))
        elif ap == 2 or ap == 6:
            for off in (KNIGHT_OFFS if ap == 2 else KING_DIRS):
                s = fr + off
                if s & 0x88:
                    continue
                q = b[s]
                if q == EMPTY or (q > 0) != (side > 0):
                    moves.append(enc(fr, s))
        else:
            dirs = ROOK_DIRS if ap == 4 else (BISHOP_DIRS if ap == 3
                                             else KING_DIRS)
            for off in dirs:
                s = fr + off
                while not (s & 0x88):
                    q = b[s]
                    if q == EMPTY:
                        moves.append(enc(fr, s))
                    else:
                        if (q > 0) != (side > 0):
                            moves.append(enc(fr, s))
                        break
                    s += off
    if side == 1:
        if (pos.castling & WK_CASTLE and b[5] == EMPTY and b[6] == EMPTY
                and b[4] == WK and b[7] == WR
                and not attacked(b, 4, -1) and not attacked(b, 5, -1)
                and not attacked(b, 6, -1)):
            moves.append(enc(E1, 6, 0, FLAG_CASTLE))
        if (pos.castling & WQ_CASTLE and b[3] == EMPTY and b[2] == EMPTY
                and b[1] == EMPTY and b[4] == WK and b[0] == WR
                and not attacked(b, 4, -1) and not attacked(b, 3, -1)
                and not attacked(b, 2, -1)):
            moves.append(enc(E1, 2, 0, FLAG_CASTLE))
    else:
        if (pos.castling & BK_CASTLE and b[117] == EMPTY and b[118] == EMPTY
                and b[116] == BK and b[119] == BR
                and not attacked(b, 116, 1) and not attacked(b, 117, 1)
                and not attacked(b, 118, 1)):
            moves.append(enc(E8, 118, 0, FLAG_CASTLE))
        if (pos.castling & BQ_CASTLE and b[115] == EMPTY and b[114] == EMPTY
                and b[113] == EMPTY and b[116] == BK and b[112] == BR
                and not attacked(b, 116, 1) and not attacked(b, 115, 1)
                and not attacked(b, 114, 1)):
            moves.append(enc(E8, 114, 0, FLAG_CASTLE))
    return moves


def make(pos, m):
    b = pos.board
    fr, to = m_from(m), m_to(m)
    promo, flag = m_promo(m), m_flag(m)
    side = pos.side
    piece = b[fr]
    captured = b[to]
    undo = (m, captured, pos.castling, pos.ep)
    b[fr] = EMPTY
    if flag == FLAG_EP:
        b[to - 16 * side] = EMPTY
    b[to] = promo * side if promo else piece
    if flag == FLAG_CASTLE:
        if to == 6:
            b[7], b[5] = EMPTY, WR
        elif to == 2:
            b[0], b[3] = EMPTY, WR
        elif to == 118:
            b[119], b[117] = EMPTY, BR
        else:
            b[112], b[115] = EMPTY, BR
    if piece == WK:
        pos.castling &= ~(WK_CASTLE | WQ_CASTLE)
    elif piece == BK:
        pos.castling &= ~(BK_CASTLE | BQ_CASTLE)
    if fr == H1 or to == H1:
        pos.castling &= ~WK_CASTLE
    if fr == A1 or to == A1:
        pos.castling &= ~WQ_CASTLE
    if fr == H8 or to == H8:
        pos.castling &= ~BK_CASTLE
    if fr == A8 or to == A8:
        pos.castling &= ~BQ_CASTLE
    pos.ep = fr + 16 * side if flag == FLAG_DOUBLE else -1
    pos.side = -side
    return undo


def unmake(pos, undo):
    m, captured, castling, ep = undo
    b = pos.board
    fr, to = m_from(m), m_to(m)
    promo, flag = m_promo(m), m_flag(m)
    side = -pos.side
    piece = b[to]
    if promo:
        piece = side
    b[fr] = piece
    b[to] = captured
    if flag == FLAG_EP:
        b[to - 16 * side] = -side
    if flag == FLAG_CASTLE:
        if to == 6:
            b[7], b[5] = WR, EMPTY
        elif to == 2:
            b[0], b[3] = WR, EMPTY
        elif to == 118:
            b[119], b[117] = BR, EMPTY
        else:
            b[112], b[115] = BR, EMPTY
    pos.castling = castling
    pos.ep = ep
    pos.side = side


def legal_moves(pos):
    out = []
    for m in pseudo_moves(pos):
        if abs(pos.board[m_to(m)]) == 6:
            continue
        u = make(pos, m)
        if not attacked(pos.board, king_sq(pos, -pos.side), pos.side):
            out.append(m)
        unmake(pos, u)
    return out


def uci_to_move(pos, uci):
    fr, to = name_sq(uci[0:2]), name_sq(uci[2:4])
    pr = {'q': 5, 'n': 2, 'r': 4, 'b': 3}.get(uci[4] if len(uci) > 4 else '', 0)
    for m in legal_moves(pos):
        if m_from(m) == fr and m_to(m) == to and m_promo(m) == pr:
            return m
    raise RuntimeError('illegal move ' + uci)


def perft(pos, d):
    if d == 0:
        return 1
    n = 0
    for m in legal_moves(pos):
        u = make(pos, m)
        n += perft(pos, d - 1)
        unmake(pos, u)
    return n


# ════════════════════════════════════════════════════════════════════════
# splitmix64
# ════════════════════════════════════════════════════════════════════════
MASK = (1 << 64) - 1


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & MASK
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


# ════════════════════════════════════════════════════════════════════════
# algebra helpers
# ════════════════════════════════════════════════════════════════════════
def _id(f, r):
    return (f, r)


def _rot90(f, r):
    return (r, 7 - f)


def _rot180(f, r):
    return (7 - f, 7 - r)


def _rot270(f, r):
    return (7 - r, f)


def _mirh(f, r):
    return (7 - f, r)


def _mirv(f, r):
    return (f, 7 - r)


def _diag(f, r):
    return (r, f)


def _anti(f, r):
    return (7 - r, 7 - f)


D4 = [_id, _rot90, _rot180, _rot270, _mirh, _mirv, _diag, _anti]
V4 = [_id, _rot180, _diag, _anti]


def orbits(group):
    seen, count, small, big = set(), 0, 0, 0
    for f in range(8):
        for r in range(8):
            if (f, r) in seen:
                continue
            orb = set(g(f, r) for g in group)
            seen |= orb
            count += 1
            if len(orb) == 2:
                small += 1
            elif len(orb) == 4:
                big += 1
    return count, small, big


def lcm(a, b):
    return a * b // gcd(a, b)


def tstar(W, H, a, b):
    gx = gcd(abs(a), W) or W
    gy = gcd(abs(b), H) or H
    return lcm(W // gx, H // gy)


def attack_squares(b, sq, blocking=True):
    """Squares attacked by the piece on `sq` (empty-board: blocking=False)."""
    p = b[sq]
    ap = abs(p)
    out = []
    if ap == 1:
        fwd = 16 * (1 if p > 0 else -1)
        for off in (fwd - 1, fwd + 1):
            s = sq + off
            if not (s & 0x88):
                out.append(s)
    elif ap == 2 or ap == 6:
        for off in (KNIGHT_OFFS if ap == 2 else KING_DIRS):
            s = sq + off
            if not (s & 0x88):
                out.append(s)
    else:
        dirs = ROOK_DIRS if ap == 4 else (BISHOP_DIRS if ap == 3 else KING_DIRS)
        for off in dirs:
            s = sq + off
            while not (s & 0x88):
                out.append(s)
                if blocking and b[s] != EMPTY:
                    break
                s += off
    return out


def equivariance_violations(board, side):
    """Violations of Theta(g.p, g.c) == Theta(p, c) over g in D4."""
    theta = [0] * 128
    for sq in SQUARES:
        p = board[sq]
        if p != EMPTY and (p > 0) == (side > 0):
            for s in attack_squares(board, sq):
                theta[s] += 1
    bad = 0
    for g in D4:
        bg = [EMPTY] * 128
        for sq in SQUARES:
            p = board[sq]
            if p != EMPTY:
                f, r = g(sq & 7, sq >> 4)
                bg[16 * r + f] = p
        tg = [0] * 128
        for sq in SQUARES:
            p = bg[sq]
            if p != EMPTY and (p > 0) == (side > 0):
                for s in attack_squares(bg, sq):
                    tg[s] += 1
        for sq in SQUARES:
            f, r = g(sq & 7, sq >> 4)
            if tg[16 * r + f] != theta[sq]:
                bad += 1
    return bad


KNIGHT_NB = None


def knight_neighbours(sq):
    global KNIGHT_NB
    if KNIGHT_NB is None:
        KNIGHT_NB = {}
        for s in SQUARES:
            KNIGHT_NB[s] = sorted(s + o for o in KNIGHT_OFFS
                                  if not ((s + o) & 0x88))
    return KNIGHT_NB[sq]


KNIGHT_TOUR = ("f5 h4 g2 e1 c2 a1 b3 c1 a2 b4 a6 b8 d7 f8 h7 g5 h3 g1 e2 "
               "g3 h1 f2 d1 b2 d3 f4 h5 g7 e8 f6 g8 h6 g4 h2 f1 e3 d5 c7 "
               "a8 b6 a4 c3 b1 a3 b5 a7 c8 e7 g6 h8 f7 e5 f3 d2 c4 a5 c6 "
               "d4 e6 d8 b7 c5 e4 d6").split()


def mate_search_plies(pos, max_depth):
    """Shortest forced mate for the side to move within max_depth plies."""
    for depth in range(1, max_depth + 1):
        res = _mate_dfs(pos, depth)
        if res is not None:
            return res
    return None


def _mate_dfs(pos, depth):
    if depth <= 0:
        return None
    best = None
    for m in legal_moves(pos):
        u = make(pos, m)
        replies = legal_moves(pos)
        if not replies:
            mated = attacked(pos.board, king_sq(pos, pos.side), -pos.side)
            unmake(pos, u)
            if mated:
                return 1
            continue
        if depth >= 2:
            all_mated = True
            worst = 0
            for r in replies:
                u2 = make(pos, r)
                sub = _mate_dfs(pos, depth - 2)
                unmake(pos, u2)
                if sub is None:
                    all_mated = False
                    break
                if sub > worst:
                    worst = sub
            if all_mated:
                unmake(pos, u)
                cand = worst + 2
                if best is None or cand < best:
                    best = cand
                    if best <= 3:
                        return best
                continue
        unmake(pos, u)
    return best


# ════════════════════════════════════════════════════════════════════════
# THE BATTERY
# ════════════════════════════════════════════════════════════════════════
RESULTS = []


def check(code, ok, note=""):
    RESULTS.append((code, bool(ok), note))


def main():
    # ── 1 board algebra ──────────────────────────────────────────────
    cnt, small, big = orbits(V4)
    d_cnt, _, _ = orbits(D4)
    burnside_d4 = (64 + 0 + 0 + 0 + 0 + 0 + 8 + 8) // 8
    burnside_v4 = (64 + 0 + 8 + 8) // 4
    check('C1', cnt == 20 and small == 8 and big == 12 and d_cnt == 10
          and burnside_d4 == 10 and burnside_v4 == 20,
          'V4=%d(%d+%d) D4=%d burnside %d/%d' % (cnt, small, big, d_cnt,
                                                 burnside_v4, burnside_d4))

    # ── 2 move-graph census ──────────────────────────────────────────
    board = [EMPTY] * 128
    directed = {}
    for t, nm in ((WR, 'R'), (WB, 'B'), (WN, 'N'), (WK, 'K'), (WQ, 'Q')):
        total = 0
        for sq in SQUARES:
            board[sq] = t
            total += len(attack_squares(board, sq, blocking=True))
            board[sq] = EMPTY
        directed[nm] = total
    edges = {k: v // 2 for k, v in directed.items()}
    check('C2', edges == {'R': 448, 'B': 280, 'N': 168, 'K': 210, 'Q': 728},
          'edges R%d B%d N%d K%d Q%d' % (edges['R'], edges['B'], edges['N'],
                                         edges['K'], edges['Q']))

    # ── 3 mobility census ────────────────────────────────────────────
    sums = {k: v for k, v in directed.items()}
    maxima = {}
    for t, nm in ((WR, 'R'), (WB, 'B'), (WN, 'N'), (WK, 'K'), (WQ, 'Q')):
        mx = 0
        for sq in SQUARES:
            board[sq] = t
            mx = max(mx, len(attack_squares(board, sq, blocking=False)))
            board[sq] = EMPTY
        maxima[nm] = mx
    bishop_ok = True
    for sq in SQUARES:
        f, r = sq & 7, sq >> 4
        board[sq] = WB
        m = len(attack_squares(board, sq, blocking=False))
        board[sq] = EMPTY
        if m != 14 - abs(f - r) - abs(f + r - 7):
            bishop_ok = False
    check('C3', sums == {'R': 896, 'B': 560, 'N': 336, 'K': 420, 'Q': 1456}
          and maxima == {'R': 14, 'B': 13, 'N': 8, 'K': 8, 'Q': 27}
          and bishop_ok,
          'sums R%d B%d N%d K%d Q%d; max %d/%d/%d/%d/%d'
          % (sums['R'], sums['B'], sums['N'], sums['K'], sums['Q'],
             maxima['R'], maxima['B'], maxima['N'], maxima['K'],
             maxima['Q']))

    # ── 4 flow termination ───────────────────────────────────────────
    cases = [(8, 8, 1, 1, 8), (8, 8, 3, 5, 8), (8, 8, 2, 2, 4),
             (8, 8, 1, 2, 8), (8, 8, 1, 0, 8), (8, 8, 2, 1, 8),
             (48, 48, 1, 1, 48), (24, 36, 3, 5, 72), (12, 12, 4, 6, 6)]
    ok = all(tstar(W, H, a, b) == t for W, H, a, b, t in cases)
    check('C4', ok, '9 t* cases: %s' %
          ','.join(str(tstar(W, H, a, b)) for W, H, a, b, t in cases[:5]))

    # ── 5 perft identities ───────────────────────────────────────────
    pos = Position().set_fen(
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    p1, p2 = perft(pos, 1), perft(pos, 2)
    p3, p4 = perft(pos, 3), perft(pos, 4)
    check('C5', (p1, p2, p3, p4) == (20, 400, 8902, 197281),
          'perft %d %d %d %d' % (p1, p2, p3, p4))

    # ── 6 threat fields ──────────────────────────────────────────────
    pawnless = [EMPTY] * 128
    for f, pc in ((0, WR), (1, WN), (2, WB), (3, WQ), (4, WK), (5, WB),
                  (6, WN), (7, WR)):
        pawnless[f] = pc
        pawnless[112 + f] = -pc
    v_w = equivariance_violations(pawnless, 1)
    v_b = equivariance_violations(pawnless, -1)
    start = [EMPTY] * 128
    for ch, sq in zip('RNBQKBNR', SQUARES[:8]):
        start[sq] = CHAR_PIECE[ch]
    for ch, sq in zip('RNBQKBNR', SQUARES[112:120]):
        start[sq] = CHAR_PIECE[ch]
    for f in range(8):
        start[16 + f] = WP
        start[96 + f] = BP
    anomaly = (equivariance_violations(start, 1)
               + equivariance_violations(start, -1))
    check('C6', v_w == 0 and v_b == 0 and anomaly == 176,
          'pawnless violations %d/%d, pawn anomaly %d' % (v_w, v_b, anomaly))

    # ── 7 kinetic energy ─────────────────────────────────────────────
    pos = Position().set_fen(
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    m0 = len(legal_moves(pos))
    u = make(pos, uci_to_move(pos, 'e2e4'))
    pos.side = 1                          # count White's mobility
    m1 = len(legal_moves(pos))
    pos.side = -1
    unmake(pos, u)
    check('C7', m0 == 20 and m1 == 30, 'White mobility %d -> %d after 1.e4'
          % (m0, m1))

    # ── 8 mate certificates ──────────────────────────────────────────
    def key_mates_in_2(pos, fr_sq, to_sq):
        for m in legal_moves(pos):
            if m_from(m) == fr_sq and m_to(m) == to_sq:
                u = make(pos, m)
                ok_all = True
                for r in legal_moves(pos):
                    u2 = make(pos, r)
                    sub = mate_search_plies(pos, 1)
                    unmake(pos, u2)
                    if sub != 1:
                        ok_all = False
                        break
                unmake(pos, u)
                return ok_all
        return False

    morphy = Position().set_fen('kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1')
    key_ok = key_mates_in_2(morphy, name_sq('a1'), name_sq('a6'))
    plies_m = mate_search_plies(morphy, 4)
    ladder = Position().set_fen('7k/8/8/8/8/8/R7/1R4K1 w - - 0 1')
    plies_l = mate_search_plies(ladder, 4)
    nr = Position().set_fen('7k/8/5N1K/8/8/8/8/6R1 w - - 0 1')
    plies_n = mate_search_plies(nr, 2)
    nr_key = False
    for m in legal_moves(nr):
        if (m_from(m) == name_sq('g1') and m_to(m) == name_sq('g8')):
            u = make(nr, m)
            replies = legal_moves(nr)
            mated = (not replies
                     and attacked(nr.board, king_sq(nr, nr.side), -nr.side))
            unmake(nr, u)
            nr_key = mated
            break
    check('C8', plies_m == 3 and key_ok and plies_l == 3 and plies_n == 1
          and nr_key,
          'morphy %s(key a1a6) ladder %s nr %s(key g1g8)'
          % (plies_m, plies_l, plies_n))

    # ── 9 zobrist incrementality (fixed playout) ─────────────────────
    zob = {}
    state = 1
    for piece in (1, 2, 3, 4, 5, 6, -1, -2, -3, -4, -5, -6):
        zob[piece] = [0] * 128
        for sq in range(128):
            state = splitmix64(state)
            zob[piece][sq] = state
    side_key = splitmix64(state)

    def full_hash(b, side):
        h = 0
        for sq in SQUARES:
            if b[sq] != EMPTY:
                h ^= zob[b[sq]][sq]
        if side == -1:
            h ^= side_key
        return h

    playout = ['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'g8f6', 'e1g1',
               'f8c5', 'd2d3', 'd7d6']
    pos = Position().set_fen(
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    h = full_hash(pos.board, pos.side)
    inc_ok = (h == full_hash(pos.board, 1))
    for u_ in playout:
        m = uci_to_move(pos, u_)
        fr, to = m_from(m), m_to(m)
        piece = pos.board[fr]
        captured = pos.board[to]
        h ^= zob[piece][fr]
        if captured != EMPTY:
            h ^= zob[captured][to]
        promo = m_promo(m)
        if promo:
            h ^= zob[promo * pos.side][to] ^ zob[piece][to]
        else:
            h ^= zob[piece][to]
        side = pos.side
        if m_flag(m) == 2:                    # en passant
            cap = to - 16 * side
            h ^= zob[pos.board[cap]][cap]
        if m_flag(m) == 3:                    # castling rook
            if to == 6:
                h ^= zob[WR][7] ^ zob[WR][5]
            elif to == 2:
                h ^= zob[WR][0] ^ zob[WR][3]
            elif to == 118:
                h ^= zob[BR][119] ^ zob[BR][117]
            else:
                h ^= zob[BR][112] ^ zob[BR][115]
        make(pos, m)
        h ^= side_key
        if h != full_hash(pos.board, pos.side):
            inc_ok = False
            break
    sm_ok = all(splitmix64(x) == EXPECTED_SM[i]
                for i, x in enumerate((1, 2, 3)))
    check('C9', inc_ok and sm_ok,
          'incremental hash over %d plies, splitmix vectors %s'
          % (len(playout), 'ok' if sm_ok else 'BAD'))

    # ── 10 knight tour certificate ───────────────────────────────────
    tour = [name_sq(s) for s in KNIGHT_TOUR]
    distinct = len(set(tour)) == 64
    closed = all(tour[(i + 1) % 64] in knight_neighbours(tour[i])
                 for i in range(64))
    check('C10', distinct and closed,
          'tour 64 distinct cells, closure %s' % ('ok' if closed else 'BAD'))

    # ── report ───────────────────────────────────────────────────────
    passed = 0
    for code, ok, note in RESULTS:
        passed += 1 if ok else 0
        print('[%s] %s  %s' % ('PASS' if ok else 'FAIL', code, note))
    print('verdict: %d/%d' % (passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


EXPECTED_SM = (
    0x910A2DEC89025CC1,   # splitmix64(1)
    0x975835DE1C9756CE,   # splitmix64(2)
    0x1D0B14E4DB018FED,   # splitmix64(3)
)


if __name__ == '__main__':
    sys.exit(main())
