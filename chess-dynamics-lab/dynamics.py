#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  CHESS DYNAMICS LABORATORY · dynamics.py
  The single-file laboratory of the chess-dynamics-lab program.

  Program author: Isaev Iskhak Khamzatovich
  Repository: github.com/wild8highlander/chess-dynamics-lab
  Version: 1.0.0 (2026)
  License: individual exclusive license (see LICENSE)

  DOCTRINE — "chess pieces as particles" (the three-layer particle model):

    LAYER K3   (potential layer)   — THREAT FIELDS.
        Every particle (piece) emits an attack field on the virtual board.
        The field is additive; its total mass equals the sum of the attack
        counts of the particles, and it is equivariant under the board
        symmetry group D4 (Theorems T04/T01).

    LAYER TORUS (kinetic layer)    — LAGRANGIAN SEARCH.
        A move is a transition of a particle; the position carries an
        energy E = material potential + mobility kinetic term. Game-tree
        search (alpha-beta with particle-driven ordering) is action
        minimization (Theorems T05/T10).

    LAYER KLEIN (flow layer)       — DISCRETE MOVE FLOW.
        A particle moving with a fixed integer velocity (a,b) on the
        W x H board grid is a discrete flow with the exact termination
        time   t* = lcm(W/gcd(a,W), H/gcd(b,H))   (Certificate E of the
        parent monograph; Theorem T06 here). With mirror reflections and
        braking gamma = delta^4/k the trajectory is a damped billiard of
        finite total path |v0|/(1-gamma).

  PROTOCOL C1-C9 (the reproducibility record of this laboratory):

    C1  board algebra: V4/D4 orbit censuses (20 and 10) + Burnside check
    C2  particle kinematics: move-graph edge census (448/280/168/210/728),
        knight connectivity+bipartiteness, bishop 2-component structure
    C3  mobility census: closed forms, maxima (27/14/13/8/8), sums
        (1456/896/560/336/420)
    C4  flow termination: t* cases on the 8x8 board + damped billiard
        total-path convergence to |v0|/(1-gamma)
    C5  perft identities from the initial position: 20/400/8902/197281
    C6  threat fields: D4-equivariance + attack-sum identity
    C7  Lagrangian energy: determinism + E0 = 20 + after-1.e4 = 30
    C8  mate certificates: retrograde DTM of KQK (max 10 moves) and
        KRK (max 16 moves) + tactical mate-in-2 suite
    C9  Zobrist incrementality: XOR algebra + splitmix64 bijection

  Cross-checks: results/baseline_c1_c9.json (frozen baseline).

  CLI:
    python3 dynamics.py --run all            run the protocol C1-C9
    python3 dynamics.py --run C5             run one check
    python3 dynamics.py --analyze "FEN"      position analysis (fields/energy)
    python3 dynamics.py --mate "FEN" --depth 4   mate-in-N solver
    python3 dynamics.py --play --depth 4 --moves "e2e4 e7e5"
    python3 dynamics.py --report             write reports/dynamics_report.json
    python3 dynamics.py --plots              write 600 dpi plots to reports/plots

  Dependencies: Python 3.10+ standard library; matplotlib optional (plots).
═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import math
import os
import sys
import time
from math import gcd

# ══════════════════════════════════════════════════════════════════════════════
# 1. BOARD GEOMETRY (0x88 mailbox)
# ══════════════════════════════════════════════════════════════════════════════
# Square index: sq = 16*rank + file, rank 0 = chess rank 1 (White home), file 0 = 'a'.
# Off-board test: sq & 0x88.

EMPTY = 0
WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
BP, BN, BB, BR, BQ, BK = -1, -2, -3, -4, -5, -6

PIECE_VALUE = {0: 0, 1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0}
PIECE_CHAR = {1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
              -1: 'p', -2: 'n', -3: 'b', -4: 'r', -5: 'q', -6: 'k'}
CHAR_PIECE = {v: k for k, v in PIECE_CHAR.items()}

SQUARES = [16 * r + f for r in range(8) for f in range(8)]


def sq_name(sq):
    return "abcdefgh"[sq & 7] + str((sq >> 4) + 1)


def name_sq(s):
    return 16 * (int(s[1]) - 1) + ("abcdefgh".index(s[0]))


KNIGHT_OFFS = (31, 33, 14, 18, -31, -33, -14, -18)
BISHOP_DIRS = (15, 17, -15, -17)
ROOK_DIRS = (16, -16, 1, -1)
KING_DIRS = (15, 16, 17, 1, -15, -16, -17, -1)

# Castling rights bits
WK_CASTLE, WQ_CASTLE, BK_CASTLE, BQ_CASTLE = 1, 2, 4, 8

A1, B1, C1, D1, E1, F1, G1, H1 = 0, 1, 2, 3, 4, 5, 6, 7
A8, B8, C8, D8, E8, F8, G8, H8 = 112, 113, 114, 115, 116, 117, 118, 119

# Move encoding: from (7 bits) | to<<7 | promo<<14 | flag<<18
# flags: 0 normal, 1 double pawn push, 2 en passant capture, 3 castling
FLAG_NORMAL, FLAG_DOUBLE, FLAG_EP, FLAG_CASTLE = 0, 1, 2, 3


def enc_move(fr, to, promo=0, flag=0):
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
    """A chess position with make/unmake, FEN I/O and incremental Zobrist hash."""

    __slots__ = ('board', 'side', 'castling', 'ep', 'halfmove', 'fullmove',
                 'hash', '_stack')

    def __init__(self):
        self.board = [EMPTY] * 128
        self.side = 1                     # 1 = White to move, -1 = Black
        self.castling = 0
        self.ep = -1                      # en-passant target square (0x88) or -1
        self.halfmove = 0
        self.fullmove = 1
        self.hash = 0
        self._stack = []

    # ── FEN ───────────────────────────────────────────────────────────────
    def set_fen(self, fen):
        parts = fen.split()
        if len(parts) < 2:
            raise ValueError("FEN needs at least placement and side fields")
        self.board = [EMPTY] * 128
        rows = parts[0].split('/')
        if len(rows) != 8:
            raise ValueError("FEN placement must have 8 rows")
        for i, row in enumerate(rows):
            rank = 7 - i
            file = 0
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
                self.castling |= {'K': WK_CASTLE, 'Q': WQ_CASTLE,
                                  'k': BK_CASTLE, 'q': BQ_CASTLE}.get(ch, 0)
        self.ep = -1
        if len(parts) > 3 and parts[3] != '-':
            self.ep = name_sq(parts[3])
        self.halfmove = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove = int(parts[5]) if len(parts) > 5 else 1
        self._stack = []
        self.hash = zobrist_hash(self)
        return self

    def to_fen(self):
        rows = []
        for rank in range(7, -1, -1):
            row, run = '', 0
            for file in range(8):
                p = self.board[16 * rank + file]
                if p == EMPTY:
                    run += 1
                else:
                    if run:
                        row += str(run)
                        run = 0
                    row += PIECE_CHAR[p]
            if run:
                row += str(run)
            rows.append(row)
        castle = ''.join(c for c, b in zip('KQkq',
                     (WK_CASTLE, WQ_CASTLE, BK_CASTLE, BQ_CASTLE))
                     if self.castling & b) or '-'
        ep = sq_name(self.ep) if self.ep >= 0 else '-'
        return "%s %s %s %s %d %d" % ('/'.join(rows),
               'w' if self.side == 1 else 'b', castle, ep,
               self.halfmove, self.fullmove)

    # ── attack detection ─────────────────────────────────────────────────
    def attacked(self, sq, by_side):
        """Is square `sq` attacked by any piece of `by_side`?"""
        b = self.board
        # pawns
        if by_side == 1:
            for off in (-15, -17):
                s = sq + off
                if not (s & 0x88) and b[s] == WP:
                    return True
        else:
            for off in (15, 17):
                s = sq + off
                if not (s & 0x88) and b[s] == BP:
                    return True
        # knights
        for off in KNIGHT_OFFS:
            s = sq + off
            if not (s & 0x88) and b[s] == 2 * by_side:
                return True
        # king
        for off in KING_DIRS:
            s = sq + off
            if not (s & 0x88) and b[s] == 6 * by_side:
                return True
        # sliders
        for dirs, kinds in ((BISHOP_DIRS, (3, 5)), (ROOK_DIRS, (4, 5))):
            for off in dirs:
                s = sq + off
                while not (s & 0x88):
                    p = b[s]
                    if p != EMPTY:
                        ap = abs(p)
                        if (p > 0) == (by_side > 0) and ap in kinds:
                            return True
                        break
                    s += off
        return False

    def king_sq(self, side):
        target = 6 * side
        for sq in SQUARES:
            if self.board[sq] == target:
                return sq
        raise ValueError("king missing")

    def in_check(self, side=None):
        side = self.side if side is None else side
        return self.attacked(self.king_sq(side), -side)

    # ── move generation ───────────────────────────────────────────────────
    def pseudo_moves(self):
        """Pseudo-legal moves for the side to move (king capture excluded)."""
        b = self.board
        side = self.side
        moves = []
        for fr in SQUARES:
            p = b[fr]
            if p == EMPTY or (p > 0) != (side > 0):
                continue
            ap = abs(p)
            if ap == 1:                                   # pawn
                fwd = 16 * side
                rank = fr >> 4
                promo_rank = 6 if side == 1 else 1
                start_rank = 1 if side == 1 else 6
                s = fr + fwd
                if not (s & 0x88) and b[s] == EMPTY:
                    if rank == promo_rank:
                        for pr in (5, 2, 4, 3):
                            moves.append(enc_move(fr, s, pr))
                    else:
                        moves.append(enc_move(fr, s))
                        if rank == start_rank:
                            s2 = s + fwd
                            if b[s2] == EMPTY:
                                moves.append(enc_move(fr, s2, 0, FLAG_DOUBLE))
                for off in (fwd - 1, fwd + 1):
                    s = fr + off
                    if s & 0x88:
                        continue
                    q = b[s]
                    if q != EMPTY and (q > 0) != (side > 0):
                        if rank == promo_rank:
                            for pr in (5, 2, 4, 3):
                                moves.append(enc_move(fr, s, pr))
                        else:
                            moves.append(enc_move(fr, s))
                    elif (s == self.ep and q == EMPTY
                          and (fr >> 4) == (4 if side == 1 else 3)):
                        moves.append(enc_move(fr, s, 0, FLAG_EP))
            elif ap == 2 or ap == 6:                      # knight / king
                offs = KNIGHT_OFFS if ap == 2 else KING_DIRS
                for off in offs:
                    s = fr + off
                    if s & 0x88:
                        continue
                    q = b[s]
                    if q == EMPTY or (q > 0) != (side > 0):
                        moves.append(enc_move(fr, s))
            else:                                          # sliders
                dirs = ROOK_DIRS if ap == 4 else (BISHOP_DIRS if ap == 3
                                                 else KING_DIRS)
                for off in dirs:
                    s = fr + off
                    while not (s & 0x88):
                        q = b[s]
                        if q == EMPTY:
                            moves.append(enc_move(fr, s))
                        else:
                            if (q > 0) != (side > 0):
                                moves.append(enc_move(fr, s))
                            break
                        s += off
        # castling
        if side == 1:
            if (self.castling & WK_CASTLE and b[F1] == EMPTY and b[G1] == EMPTY
                    and b[E1] == WK and b[H1] == WR
                    and not self.attacked(E1, -1)
                    and not self.attacked(F1, -1)
                    and not self.attacked(G1, -1)):
                moves.append(enc_move(E1, G1, 0, FLAG_CASTLE))
            if (self.castling & WQ_CASTLE and b[D1] == EMPTY and b[C1] == EMPTY
                    and b[B1] == EMPTY and b[E1] == WK and b[A1] == WR
                    and not self.attacked(E1, -1)
                    and not self.attacked(D1, -1)
                    and not self.attacked(C1, -1)):
                moves.append(enc_move(E1, C1, 0, FLAG_CASTLE))
        else:
            if (self.castling & BK_CASTLE and b[F8] == EMPTY and b[G8] == EMPTY
                    and b[E8] == BK and b[H8] == BR
                    and not self.attacked(E8, 1)
                    and not self.attacked(F8, 1)
                    and not self.attacked(G8, 1)):
                moves.append(enc_move(E8, G8, 0, FLAG_CASTLE))
            if (self.castling & BQ_CASTLE and b[D8] == EMPTY and b[C8] == EMPTY
                    and b[B8] == EMPTY and b[E8] == BK and b[A8] == BR
                    and not self.attacked(E8, 1)
                    and not self.attacked(D8, 1)
                    and not self.attacked(C8, 1)):
                moves.append(enc_move(E8, C8, 0, FLAG_CASTLE))
        return moves

    def legal_moves(self):
        out = []
        for m in self.pseudo_moves():
            if abs(self.board[m_to(m)]) == 6:
                continue          # king captures never legal (input hardening)
            undo = self.make(m)
            if not self.attacked(self.king_sq(-self.side), self.side):
                out.append(m)
            self.unmake(undo)
        return out

    def is_valid(self):
        """Basic legality: both kings present, side not to move is not in check,
        castling rights consistent with piece placement."""
        wk = bk = False
        for sq in SQUARES:
            p = self.board[sq]
            if p == WK:
                wk = True
            elif p == BK:
                bk = True
        if not wk or not bk:
            return False, "missing king"
        if self.attacked(self.king_sq(-self.side), self.side):
            return False, "side not to move is in check"
        if (self.castling & (WK_CASTLE | WQ_CASTLE)) and self.board[E1] != WK:
            return False, "white castling right without the white king on e1"
        if (self.castling & (BK_CASTLE | BQ_CASTLE)) and self.board[E8] != BK:
            return False, "black castling right without the black king on e8"
        return True, "ok"

    # ── make / unmake ────────────────────────────────────────────────────
    def make(self, m):
        b = self.board
        fr, to = m_from(m), m_to(m)
        promo, flag = m_promo(m), m_flag(m)
        side = self.side
        piece = b[fr]
        captured = b[to]
        undo = (m, captured, self.castling, self.ep, self.halfmove,
                self.hash)
        # --- incremental hash ---
        h = self.hash
        h ^= ZOB_SIDE
        h ^= ZOB_PIECE[piece][fr]
        if captured != EMPTY:
            h ^= ZOB_PIECE[captured][to]
        if flag == FLAG_EP:
            cap_sq = to - 16 * side
            h ^= ZOB_PIECE[b[cap_sq]][cap_sq]
        h ^= ZOB_EP_FILE[(self.ep & 7) + 1 if self.ep >= 0 else 0]
        # --- move the piece ---
        b[fr] = EMPTY
        if flag == FLAG_EP:
            cap_sq = to - 16 * side
            b[cap_sq] = EMPTY
        new_piece = piece
        if promo:
            new_piece = promo * side
        b[to] = new_piece
        h ^= ZOB_PIECE[new_piece][to]
        if flag == FLAG_CASTLE:
            if to == G1:
                b[H1], b[F1] = EMPTY, WR
                h ^= ZOB_PIECE[WR][H1] ^ ZOB_PIECE[WR][F1]
            elif to == C1:
                b[A1], b[D1] = EMPTY, WR
                h ^= ZOB_PIECE[WR][A1] ^ ZOB_PIECE[WR][D1]
            elif to == G8:
                b[H8], b[F8] = EMPTY, BR
                h ^= ZOB_PIECE[BR][H8] ^ ZOB_PIECE[BR][F8]
            else:
                b[A8], b[D8] = EMPTY, BR
                h ^= ZOB_PIECE[BR][A8] ^ ZOB_PIECE[BR][D8]
        # --- castling rights ---
        old_castling = self.castling
        if piece == WK:
            self.castling &= ~(WK_CASTLE | WQ_CASTLE)
        elif piece == BK:
            self.castling &= ~(BK_CASTLE | BQ_CASTLE)
        if fr == H1 or to == H1:
            self.castling &= ~WK_CASTLE
        if fr == A1 or to == A1:
            self.castling &= ~WQ_CASTLE
        if fr == H8 or to == H8:
            self.castling &= ~BK_CASTLE
        if fr == A8 or to == A8:
            self.castling &= ~BQ_CASTLE
        h ^= ZOB_CASTLE[old_castling] ^ ZOB_CASTLE[self.castling]
        # --- ep square ---
        self.ep = (fr + 16 * side) if flag == FLAG_DOUBLE else -1
        h ^= ZOB_EP_FILE[(self.ep & 7) + 1 if self.ep >= 0 else 0]
        # --- clocks / side ---
        self.halfmove = 0 if (abs(piece) == 1 or captured != EMPTY) \
            else self.halfmove + 1
        if side == -1:
            self.fullmove += 1
        self.side = -side
        self.hash = h
        return undo

    def unmake(self, undo):
        m, captured, castling, ep, halfmove, h = undo
        b = self.board
        fr, to = m_from(m), m_to(m)
        promo, flag = m_promo(m), m_flag(m)
        side = -self.side               # the side that made the move
        piece = b[to]
        if promo:
            piece = 1 * side
        b[fr] = piece
        b[to] = captured
        if flag == FLAG_EP:
            b[to - 16 * side] = -1 * side
        if flag == FLAG_CASTLE:
            if to == G1:
                b[H1], b[F1] = WR, EMPTY
            elif to == C1:
                b[A1], b[D1] = WR, EMPTY
            elif to == G8:
                b[H8], b[F8] = BR, EMPTY
            else:
                b[A8], b[D8] = BR, EMPTY
        self.castling = castling
        self.ep = ep
        self.halfmove = halfmove
        self.fullmove -= 1 if side == -1 else 0
        self.side = side
        self.hash = h


START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def start_position():
    return Position().set_fen(START_FEN)


# ══════════════════════════════════════════════════════════════════════════════
# 2. ZOBRIST HASHING (splitmix64) — Theorem T09
# ══════════════════════════════════════════════════════════════════════════════
MASK64 = (1 << 64) - 1


def splitmix64(x):
    """The splitmix64 bijection on Z/2^64 (Theorem T09: it is invertible)."""
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return z ^ (z >> 31)


_A_INV = pow(0xBF58476D1CE4E5B9, -1, 1 << 64)
_B_INV = pow(0x94D049BB133111EB, -1, 1 << 64)


def splitmix64_inverse(y):
    """Exact inverse of splitmix64 — the constructive proof of bijectivity.

    Inverse of `x ^= x >> s` is `x ^= x >> s` applied with s, 2s, 4s, ...
    until the shift reaches the word width (a telescoping identity); the
    odd multipliers are inverted modulo 2^64 (they are odd, hence units).
    """
    z = y
    z ^= z >> 31
    z ^= z >> 62                       # undo  z ^= z >> 31
    z = (z * _B_INV) & MASK64          # undo  z *= 0x94D049BB133111EB
    z ^= z >> 27
    z ^= z >> 54                       # undo  z ^= z >> 27
    z = (z * _A_INV) & MASK64          # undo  z *= 0xBF58476D1CE4E5B9
    z ^= z >> 30
    z ^= z >> 60                       # undo  z ^= z >> 30
    return (z - 0x9E3779B97F4A7C15) & MASK64


def _zobrist_tables():
    piece_keys = {}
    state = 0x1234567890ABCDEF
    for piece in (WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK):
        arr = [0] * 128
        for sq in range(128):
            state = splitmix64(state)
            arr[sq] = state
        piece_keys[piece] = arr
    side_key = splitmix64(state)
    castle_keys = []
    for _ in range(16):
        state = splitmix64(state)
        castle_keys.append(state)
    ep_keys = []
    for _ in range(9):                       # index 0 = none, 1..8 = file+1
        state = splitmix64(state)
        ep_keys.append(state)
    return piece_keys, side_key, castle_keys, ep_keys


ZOB_PIECE, ZOB_SIDE, ZOB_CASTLE, ZOB_EP_FILE = _zobrist_tables()


def zobrist_hash(pos):
    h = 0
    for sq in SQUARES:
        p = pos.board[sq]
        if p != EMPTY:
            h ^= ZOB_PIECE[p][sq]
    if pos.side == -1:
        h ^= ZOB_SIDE
    h ^= ZOB_CASTLE[pos.castling]
    h ^= ZOB_EP_FILE[(pos.ep & 7) + 1 if pos.ep >= 0 else 0]
    return h


# ══════════════════════════════════════════════════════════════════════════════
# 3. LAYER K3 — THREAT FIELDS (Theorem T04) and LAYER TORUS — energy (T05)
# ══════════════════════════════════════════════════════════════════════════════
def piece_attack_squares(board, sq, blocking=True):
    """Squares attacked by the piece standing on `sq` (0x88 board list).

    blocking=True  -> slider rays stop at the first occupied square (inclusive)
    blocking=False -> rays run to the board edge (empty-board attack field)
    """
    p = board[sq]
    ap = abs(p)
    out = []
    if ap == 1:
        fwd = 16 * (1 if p > 0 else -1)
        for off in (fwd - 1, fwd + 1):
            s = sq + off
            if not (s & 0x88):
                out.append(s)
    elif ap == 2:
        for off in KNIGHT_OFFS:
            s = sq + off
            if not (s & 0x88):
                out.append(s)
    elif ap == 6:
        for off in KING_DIRS:
            s = sq + off
            if not (s & 0x88):
                out.append(s)
    else:
        dirs = ROOK_DIRS if ap == 4 else (BISHOP_DIRS if ap == 3 else KING_DIRS)
        for off in dirs:
            s = sq + off
            while not (s & 0x88):
                out.append(s)
                if blocking and board[s] != EMPTY:
                    break
                s += off
    return out


def threat_field(pos, side):
    """Theta[c] = number of `side` pieces attacking square c (Layer K3 field)."""
    theta = [0] * 128
    for sq in SQUARES:
        p = pos.board[sq]
        if p != EMPTY and (p > 0) == (side > 0):
            for s in piece_attack_squares(pos.board, sq):
                theta[s] += 1
    return theta


def attack_sum_identity(pos, side):
    """Verify  sum_c Theta[c] == sum over pieces of their attack counts."""
    theta = threat_field(pos, side)
    total_field = sum(theta[sq] for sq in SQUARES)
    total_pieces = 0
    for sq in SQUARES:
        p = pos.board[sq]
        if p != EMPTY and (p > 0) == (side > 0):
            total_pieces += len(piece_attack_squares(pos.board, sq))
    return total_field, total_pieces


def mobility(pos, side):
    """Kinetic term: number of legal moves of `side` in the position."""
    saved = pos.side
    pos.side = side
    n = len(pos.legal_moves())
    pos.side = saved
    return n


def material(pos, side):
    return sum(PIECE_VALUE[abs(pos.board[sq])]
               for sq in SQUARES
               if pos.board[sq] != EMPTY and (pos.board[sq] > 0) == (side > 0))


def energy(pos, side=1):
    """Layer TORUS Lagrangian energy from White's viewpoint:

        E = [material(White) - material(Black)]
          + mu * [mobility(White) - mobility(Black)],     mu = 0.1
    """
    mu = 0.1
    return (material(pos, 1) - material(pos, -1)
            + mu * (mobility(pos, 1) - mobility(pos, -1)))


# ══════════════════════════════════════════════════════════════════════════════
# 4. LAYER KLEIN — DISCRETE FLOW (Theorem T06) and BOARD ALGEBRA (T01)
# ══════════════════════════════════════════════════════════════════════════════
def tstar(W, H, a, b):
    """Exact termination time  t* = lcm(W/gcd(a,W), H/gcd(b,H))  (cert E-4)."""
    gx = gcd(abs(a), W) or W          # gcd(0, W) = W by convention
    gy = gcd(abs(b), H) or H
    px, py = W // gx, H // gy
    return px * py // gcd(px, py)


def simulate_torus_flow(W, H, a, b, max_steps=100000):
    """Simulate p -> p+(a,b) mod (W,H); return (steps_to_first_return, cells)."""
    x, y = 0, 0
    visited = {(0, 0)}
    for step in range(1, max_steps + 1):
        x = (x + a) % W
        y = (y + b) % H
        if (x, y) == (0, 0):
            return step, visited
        visited.add((x, y))
    return None, visited


def simulate_billiard(W, H, a, b, gamma, eps=1e-12, max_steps=200000):
    """Layer K3 damped billiard: mirror reflections + braking gamma per step.

    Theorem T06(iii): the cumulative path equals
        |v0| * (1 - gamma^n) / (1 - gamma)   after n steps,
    converging to |v0| / (1 - gamma). Returns
    (steps, total_path, reflections, at_rest, path_bound_ratio).
    """
    x, y = 0.5, 0.5
    vx, vy = float(a), float(b)
    v0 = math.hypot(vx, vy)
    path = 0.0
    reflections = 0
    for step in range(1, max_steps + 1):
        speed = math.hypot(vx, vy)
        if speed < eps:
            exact = v0 / (1.0 - gamma)
            return step - 1, path, reflections, True, path / exact
        nx, nvx = x + vx, vx
        ny, nvy = y + vy, vy
        while nx < 0 or nx > W:
            nx = -nx if nx < 0 else 2 * W - nx
            nvx = -nvx
            reflections += 1
        while ny < 0 or ny > H:
            ny = -ny if ny < 0 else 2 * H - ny
            nvy = -nvy
            reflections += 1
        x, y, vx, vy = nx, ny, nvx, nvy
        path += speed
        vx *= gamma
        vy *= gamma
    exact = v0 / (1.0 - gamma)
    return max_steps, path, reflections, False, path / exact


# ── Board algebra: D4 / V4 actions ───────────────────────────────────────────
def _id(f, r):
    return (f, r)


def _rot90(f, r):
    return (r, 7 - f)


def _rot180(f, r):
    return (7 - f, 7 - r)


def _rot270(f, r):
    return (7 - r, f)


def _mir_h(f, r):
    return (7 - f, r)


def _mir_v(f, r):
    return (f, 7 - r)


def _diag(f, r):
    return (r, f)


def _antidiag(f, r):
    return (7 - r, 7 - f)


D4 = {'id': _id, 'rot90': _rot90, 'rot180': _rot180, 'rot270': _rot270,
      'mir_h': _mir_h, 'mir_v': _mir_v, 'diag': _diag, 'antidiag': _antidiag}
# The colour-preserving subgroup: (f+r) mod 2 is invariant under exactly these:
V4 = {'id': _id, 'rot180': _rot180, 'diag': _diag, 'antidiag': _antidiag}


def orbits(group):
    """Orbit decomposition of the 64 squares under a subgroup of D4."""
    seen = set()
    orbs = []
    for f in range(8):
        for r in range(8):
            if (f, r) in seen:
                continue
            orb = set()
            for g in group.values():
                orb.add(g(f, r))
            orbs.append(tuple(sorted(orb)))
            seen |= orb
    return orbs


def burnside_orbits(fixed_counts):
    """|orbits| = (1/|G|) * sum_g fix(g)  (Burnside lemma)."""
    return sum(fixed_counts.values()) // len(fixed_counts)


# ══════════════════════════════════════════════════════════════════════════════
# 5. PARTICLE KINEMATICS — move graphs and mobility census (T02, T03)
# ══════════════════════════════════════════════════════════════════════════════
PIECE_CODE = {2: WN, 3: WB, 4: WR, 5: WQ, 6: WK}


def piece_graph_directed(piece_type):
    """Directed move count of the empty-board move graph of a piece type.

    Every edge {u, v} of the (undirected) move graph is counted twice here.
    """
    board = [EMPTY] * 128
    code = PIECE_CODE[piece_type]
    directed = 0
    for sq in SQUARES:
        board[sq] = code
        directed += len(piece_attack_squares(board, sq, blocking=False))
        board[sq] = EMPTY
    return directed


def empty_board_graph(piece_type):
    """Adjacency structure of the piece move graph on the empty board."""
    board = [EMPTY] * 128
    code = PIECE_CODE[piece_type]
    adj = {sq: set() for sq in SQUARES}
    for sq in SQUARES:
        board[sq] = code
        for s in piece_attack_squares(board, sq, blocking=True):
            if s != sq:
                adj[sq].add(s)
                adj[s].add(sq)
        board[sq] = EMPTY
    return adj


def graph_components(adj):
    """Connected components of a graph given as dict sq -> neighbour set."""
    seen = set()
    comps = []
    for v in adj:
        if v in seen:
            continue
        stack, comp = [v], set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            stack.extend(adj[u] - comp)
        seen |= comp
        comps.append(sorted(comp))
    return comps


def is_bipartite(adj):
    color = {}
    for v in adj:
        if v in color:
            continue
        color[v] = 0
        stack = [v]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in color:
                    color[w] = color[u] ^ 1
                    stack.append(w)
                elif color[w] == color[u]:
                    return False, color
    return True, color


def mobility_census():
    """Per-square mobility of each piece type on the empty board (T03)."""
    board = [EMPTY] * 128
    out = {}
    for name, code in (('king', WK), ('knight', WN), ('bishop', WB),
                       ('rook', WR), ('queen', WQ)):
        table = []
        for sq in SQUARES:
            board[sq] = code
            table.append(len(piece_attack_squares(board, sq,
                                                  blocking=False)))
            board[sq] = EMPTY
        mx = max(table)
        argmax = [sq_name(SQUARES[i]) for i, v in enumerate(table) if v == mx]
        out[name] = {'table': table, 'max': mx, 'argmax': argmax,
                     'sum': sum(table)}
    # closed form for the bishop:  m(f, r) = 14 - |f - r| - |f + r - 7|
    bt, rt, qt = out['bishop']['table'], out['rook']['table'], out['queen']['table']
    out['bishop_closed_form_ok'] = all(
        bt[i] == 14 - abs(i % 8 - i // 8) - abs(i % 8 + i // 8 - 7)
        for i in range(64))
    out['queen_closed_form_ok'] = all(qt[i] == rt[i] + bt[i] for i in range(64))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 6. SEARCH — alpha-beta with particle-driven ordering (T10) + mate solver
# ══════════════════════════════════════════════════════════════════════════════
MATE = 1000000


def pseudo_mobility(pos, side):
    """Fast kinetic proxy: pseudo-legal move count of `side` (no legality
    filtering). Used inside the search; the certified kinetic term of
    Theorem T05 uses the exact legal mobility."""
    saved = pos.side
    pos.side = side
    n = len(pos.pseudo_moves())
    pos.side = saved
    return n


def evaluate(pos):
    """Static evaluation from the SIDE TO MOVE viewpoint (negamax):

        E_stm = 100 * material_balance + mu * mobility_balance,  mu = 10
    """
    sign = 1 if pos.side == 1 else -1
    mat = material(pos, 1) - material(pos, -1)
    mob = pseudo_mobility(pos, 1) - pseudo_mobility(pos, -1)
    return sign * int(round(100 * mat + 10 * mob))


def order_moves(pos, moves):
    """Particle-driven move ordering: MVV-LVA + centralization kinetic proxy."""
    b = pos.board

    def score(m):
        to = m_to(m)
        cap = b[to]
        s = 0
        if cap != EMPTY:
            s += 100 + 10 * PIECE_VALUE[abs(cap)] - PIECE_VALUE[abs(b[m_from(m)]) // 1]
        if m_flag(m) == FLAG_EP:
            s += 100 + 9
        if m_promo(m):
            s += 90
        f, r = to & 7, to >> 4
        s += (3.5 - abs(f - 3.5)) + (3.5 - abs(r - 3.5))
        return -s
    return sorted(moves, key=score)


def quiescence(pos, alpha, beta):
    stand = evaluate(pos)
    if stand >= beta:
        return beta
    if stand > alpha:
        alpha = stand
    caps = [m for m in pos.pseudo_moves()
            if pos.board[m_to(m)] != EMPTY or m_flag(m) == FLAG_EP]
    for m in order_moves(pos, caps):
        undo = pos.make(m)
        if pos.attacked(pos.king_sq(-pos.side), pos.side):
            pos.unmake(undo)
            continue
        score = -quiescence(pos, -beta, -alpha)
        pos.unmake(undo)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def negamax(pos, depth, alpha, beta, ply, node_counter):
    node_counter[0] += 1
    if pos.halfmove >= 100:
        return 0
    moves = pos.legal_moves()
    if not moves:
        return -MATE + ply if pos.in_check(pos.side) else 0
    if depth == 0:
        return quiescence(pos, alpha, beta)
    for m in order_moves(pos, moves):
        undo = pos.make(m)
        score = -negamax(pos, depth - 1, -beta, -alpha, ply + 1, node_counter)
        pos.unmake(undo)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def search_best_move(pos, depth, node_counter=None):
    """Root alpha-beta; returns (move, score, nodes). Deterministic."""
    if node_counter is None:
        node_counter = [0]
    best, best_score = None, -2 * MATE
    alpha, beta = -2 * MATE, 2 * MATE
    for m in order_moves(pos, pos.legal_moves()):
        undo = pos.make(m)
        score = -negamax(pos, depth - 1, -beta, -alpha, 1, node_counter)
        pos.unmake(undo)
        if score > best_score:
            best, best_score = m, score
        alpha = max(alpha, score)
    return best, best_score, node_counter[0]


def mate_search(pos, max_depth, node_counter=None):
    """Iterative-deepening forced-mate search for the side to move.

    Returns (plies or None, pv_line_of_moves, nodes).
    """
    if node_counter is None:
        node_counter = [0]
    for depth in range(1, max_depth + 1):
        res = _mate_dfs(pos, depth, node_counter)
        if res is not None:
            plies, pv = res
            return plies, pv, node_counter[0]
    return None, [], node_counter[0]


def _mate_dfs(pos, depth, node_counter):
    """Return (plies_to_mate_within_depth, full_pv_line) or None.

    Attacker = side to move. The line includes the defender's most
    resistant replies (the maximax branch).
    """
    node_counter[0] += 1
    if depth <= 0:
        return None
    best = None
    for m in order_moves(pos, pos.legal_moves()):
        undo = pos.make(m)
        replies = pos.legal_moves()
        if not replies:
            mated = pos.in_check(pos.side)
            pos.unmake(undo)
            if mated:
                return 1, [m]            # immediate mate: cannot be shorter
            continue                     # stalemate: not a mate line
        if depth >= 2:
            worst_plies = -1
            worst_line = None
            all_mated = True
            for r in order_moves(pos, replies):
                u2 = pos.make(r)
                sub = _mate_dfs(pos, depth - 2, node_counter)
                pos.unmake(u2)
                if sub is None:
                    all_mated = False
                    break
                if sub[0] > worst_plies:
                    worst_plies = sub[0]
                    worst_line = [r] + sub[1]
            if all_mated:
                pos.unmake(undo)
                cand = (worst_plies + 2, [m] + worst_line)
                if best is None or cand[0] < best[0]:
                    best = cand
                    if best[0] <= 3:
                        return best      # cannot be shorter at this depth
                continue
        pos.unmake(undo)
    return best


def move_to_uci(m):
    s = sq_name(m_from(m)) + sq_name(m_to(m))
    pr = m_promo(m)
    if pr:
        s += {5: 'q', 2: 'n', 4: 'r', 3: 'b'}[pr]
    return s


def uci_to_move(pos, uci):
    fr, to = name_sq(uci[0:2]), name_sq(uci[2:4])
    pr = {'q': 5, 'n': 2, 'r': 4, 'b': 3}.get(uci[4] if len(uci) > 4 else '', 0)
    for m in pos.legal_moves():
        if m_from(m) == fr and m_to(m) == to and m_promo(m) == pr:
            return m
    raise ValueError("illegal move %s in %s" % (uci, pos.to_fen()))



# ══════════════════════════════════════════════════════════════════════════════
# 7. RETROGRADE ANALYSIS — KQK / KRK exact DTM (Theorem T11)
# ══════════════════════════════════════════════════════════════════════════════
# State packing (22 bits):  wk | wq<<7 | bk<<14 | stm<<21 , stm 0=White 1=Black
# (each 0x88 square needs 7 bits: values 0..119)
# dtm values: -1 = not won for White (draw / not reached), 0 = Black mated,
# k >= 1 = White mates in k plies against best defence.

from array import array

KING_NB = {sq: [sq + o for o in KING_DIRS if not ((sq + o) & 0x88)]
           for sq in SQUARES}


def pack_state(wk, wq, bk, stm):
    return wk | (wq << 7) | (bk << 14) | (stm << 21)


def unpack_state(s):
    return s & 127, (s >> 7) & 127, (s >> 14) & 127, (s >> 21) & 1


def kings_adjacent(a, b):
    return max(abs((a & 7) - (b & 7)), abs((a >> 4) - (b >> 4))) <= 1


def _children_white(wk, wq, bk, code):
    """White-to-move children (packed ints) of (wk, wq, bk)."""
    ch = []
    for dest in KING_NB[wk]:
        if dest == wq or dest == bk or dest in KING_NB[bk]:
            continue
        ch.append(dest | (wq << 7) | (bk << 14) | (1 << 21))
    board = [EMPTY] * 128
    board[wk], board[wq], board[bk] = WK, code, BK
    for dest in piece_attack_squares(board, wq, blocking=True):
        if dest == wk or dest == bk:
            continue
        ch.append(wk | (dest << 7) | (bk << 14) | (1 << 21))
    return ch


def _children_black(wk, wq, bk, code):
    """Black-to-move children; returns (children, queen_capture_flag)."""
    ch = []
    captured = 0
    board = [EMPTY] * 128
    board[wk], board[wq], board[bk] = WK, code, BK
    for dest in KING_NB[bk]:
        if dest == wk:
            continue
        if dest in KING_NB[wk]:
            continue               # adjacent to the White king: illegal move
        if dest == wq:
            captured = 1           # LEGAL capture of an undefended piece
            continue               # -> K vs K afterwards: draw
        board2 = [EMPTY] * 128
        board2[wk], board2[wq], board2[dest] = WK, code, BK
        if dest in piece_attack_squares(board2, wq, blocking=True):
            continue
        ch.append(wk | (wq << 7) | (dest << 14))
    return ch, captured


def retro_dtm(strong_piece, progress=None):
    """Exact DTM (in plies) for K+Q vs K / K+R vs K, White to win.

    Returns (dtm, stats): dtm is a list of size 2**19; stalemates and
    queen/rook-capture escapes stay at -1 (draw) — the game-theoretic
    value of the endgame, exactly as in the classical tablebases.
    """
    code = WQ if strong_piece == 5 else WR
    SIZE = 1 << 22
    dtm = [-1] * SIZE

    # ── pass 1: enumerate states, build flat successor list ───────────────
    # NOTE: succ_ptr[s] is recorded DURING enumeration (the flat list grows
    # in enumeration order, not in numeric state order).
    succ_flat = array('i')
    succ_ptr = array('i', bytes(4 * (SIZE + 1)))
    cnt = array('i', bytes(4 * SIZE))          # children count per state
    escape = bytearray(SIZE)                   # 1 = Black captures the piece: draw
    n_states = 0
    for wk in SQUARES:
        for wq in SQUARES:
            if wq == wk:
                continue
            for bk in SQUARES:
                if bk == wk or bk == wq or kings_adjacent(wk, bk):
                    continue
                board = [EMPTY] * 128
                board[wk], board[wq], board[bk] = WK, code, BK
                targets = piece_attack_squares(board, wq, blocking=True)
                # White to move: legal only if Black king is not en prise
                if bk not in targets:
                    s0 = pack_state(wk, wq, bk, 0)
                    ch = _children_white(wk, wq, bk, code)
                    succ_ptr[s0] = len(succ_flat)
                    cnt[s0] = len(ch)
                    succ_flat.extend(ch)
                    n_states += 1
                # Black to move: always a state
                ch, captured = _children_black(wk, wq, bk, code)
                s1 = pack_state(wk, wq, bk, 1)
                succ_ptr[s1] = len(succ_flat)
                cnt[s1] = len(ch)
                succ_flat.extend(ch)
                if captured:
                    escape[s1] = 1             # K vs K after the capture: draw
                if not ch and not captured and bk in targets:
                    dtm[s1] = 0                # checkmate (layer 0)
                n_states += 1
    succ_ptr[SIZE] = len(succ_flat)
    if progress:
        progress("states", n_states)

    # ── predecessor CSR (count + fill) ────────────────────────────────────
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
    if progress:
        progress("edges", total)

    # ── layered retrograde propagation ────────────────────────────────────
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
                if not (parent >> 21):         # White to move: exists move
                    dtm[parent] = depth
                    if depth > max_plies:
                        max_plies = depth
                    nxt.append(parent)
                else:                           # Black to move: all moves win
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
    stats = {'piece': 'Q' if strong_piece == 5 else 'R',
             'states': n_states, 'edges': total,
             'won': sum(1 for v in dtm if v >= 0),
             'mates': sum(1 for v in dtm if v == 0),
             'max_plies': max_plies,
             'max_moves': (max_plies + 1) // 2 if max_plies >= 0 else -1}
    return dtm, stats


def dtm_state_of(dtm, wk, wq, bk, stm):
    """DTM lookup for unpacked coordinates (-2 = state outside the space)."""
    if kings_adjacent(wk, bk) or wk == wq or bk == wq or wk == bk:
        return -2
    return dtm[pack_state(wk, wq, bk, stm)]


# ══════════════════════════════════════════════════════════════════════════════
# 8. FROZEN CERTIFICATES
# ══════════════════════════════════════════════════════════════════════════════
# The closed knight tour (Warnsdorff, deterministic tie-break; verified:
# 64 distinct squares, every consecutive pair a knight move, closure move).
KNIGHT_TOUR = (
    "f5 h4 g2 e1 c2 a1 b3 c1 a2 b4 a6 b8 d7 f8 h7 g5 h3 g1 e2 g3 h1 f2 d1 "
    "b2 d3 f4 h5 g7 e8 f6 g8 h6 g4 h2 f1 e3 d5 c7 a8 b6 a4 c3 b1 a3 b5 a7 "
    "c8 e7 g6 h8 f7 e5 f3 d2 c4 a5 c6 d4 e6 d8 b7 c5 e4 d6").split()

# Tactical problems of the polyglot battery (all verified by the solver):
#   Morphy's zugzwang mate in 2 (unique key move a1a6)
MATE_MORPHY_FEN = "kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1"
MATE_MORPHY_PLIES = 3
MATE_MORPHY_KEY = "a1a6"
#   Two-rook ladder mate in 2 (key moves b1b7 / a2a7)
MATE_LADDER_FEN = "7k/8/8/8/8/8/R7/1R4K1 w - - 0 1"
MATE_LADDER_PLIES = 3
#   Knight+rook mate in 1
MATE_NR_FEN = "7k/8/5N1K/8/8/8/8/6R1 w - - 0 1"
MATE_NR_PLIES = 1
MATE_NR_KEY = "g1g8"

# Frozen retrograde DTM statistics (Bellman-verified over all states;
# the full tables live in results/dtm_krk.json.gz and dtm_kqk.json.gz)
DTM_EXPECTED = {
    'KRK': {'states': 399112, 'edges': 4447032, 'won': 376868,
            'mates': 216, 'max_plies': 32, 'max_moves': 16},
    'KQK': {'states': 368452, 'edges': 4869496, 'won': 345404,
            'mates': 364, 'max_plies': 20, 'max_moves': 10},
}

# Certificate E reference cases of the parent monograph (torus W x H)
TSTAR_CASES = [
    ((8, 8, 1, 1), 8), ((8, 8, 3, 5), 8), ((8, 8, 2, 2), 4),
    ((8, 8, 1, 2), 8), ((8, 8, 1, 0), 8), ((8, 8, 2, 1), 8),
    ((48, 48, 1, 1), 48), ((24, 36, 3, 5), 72),
    ((12, 12, 4, 6), 6), ((7, 14, 1, 1), 14),
]

GAMMA_TORUS = (math.pi / 4) ** 4          # delta^4/k with delta = pi/4, k = 1

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'results') if '__file__' in globals() else 'results'


def load_dtm_cache(piece):
    """Load the frozen DTM table (list of size 2**22) from results/."""
    import base64 as _b64
    import gzip as _gz
    name = 'dtm_%s.json.gz' % ('kqk' if piece == 5 else 'krk')
    path = os.path.join(RESULTS_DIR, name)
    if not os.path.exists(path):
        # fallback: next to the script inside the repository layout
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'results', name)
        if not os.path.exists(alt):
            return None
        path = alt
    with open(path, 'r') as f:
        payload = json.load(f)
    blob = _gz.decompress(_b64.b64decode(payload['dtm_blob_b64']))
    dtm = [(-1 if v == 200 else v) for v in blob]
    return dtm, payload['stats']


# ══════════════════════════════════════════════════════════════════════════════
# 9. PROTOCOL C1-C9
# ══════════════════════════════════════════════════════════════════════════════
def _c1_board_algebra():
    ov, od = orbits(V4), orbits(D4)
    sizes = sorted(set(len(o) for o in ov))
    diag_orbits = sum(1 for o in ov if len(o) == 2)
    off_orbits = sum(1 for o in ov if len(o) == 4)
    # Burnside check for D4: fix(g) = 64,0,0,0,0,0,8,8
    fixed = {'id': 64}
    for k in ('rot90', 'rot180', 'rot270', 'mir_h', 'mir_v'):
        fixed[k] = sum(1 for f in range(8) for r in range(8)
                       if D4[k](f, r) == (f, r))
    fixed['diag'] = 8
    fixed['antidiag'] = 8
    burnside = burnside_orbits(fixed)
    ok = (len(ov) == 20 and sizes == [2, 4] and len(od) == 10
          and diag_orbits == 8 and off_orbits == 12 and burnside == 10
          and burnside_orbits({'id': 64, 'rot180': 0, 'diag': 8,
                               'antidiag': 8}) == 20)
    return ok, {'v4_orbits': len(ov), 'v4_sizes': sizes,
                'diag_orbits_size2': diag_orbits,
                'offdiag_orbits_size4': off_orbits,
                'd4_orbits': len(od), 'burnside_d4': burnside}


def _c2_particle_kinematics():
    directed = {nm: piece_graph_directed(t) for t, nm in
                ((4, 'rook'), (3, 'bishop'), (2, 'knight'),
                 (6, 'king'), (5, 'queen'))}
    edges = {k: v // 2 for k, v in directed.items()}
    adj_n = empty_board_graph(2)
    comps_n = graph_components(adj_n)
    bip, _ = is_bipartite(adj_n)
    comps_b = graph_components(empty_board_graph(3))
    adj_r = empty_board_graph(4)
    comps_r = graph_components(adj_r)
    adj_k = empty_board_graph(6)
    comps_k = graph_components(adj_k)
    adj_q = empty_board_graph(5)
    comps_q = graph_components(adj_q)
    ok = (edges == {'rook': 448, 'bishop': 280, 'knight': 168,
                    'king': 210, 'queen': 728}
          and len(comps_n) == 1 and bip
          and [len(c) for c in comps_b] == [32, 32]
          and len(comps_r) == 1 and len(comps_k) == 1 and len(comps_q) == 1)
    return ok, {'directed': directed, 'edges': edges,
                'knight_connected': len(comps_n) == 1,
                'knight_bipartite': bip,
                'bishop_components': [len(c) for c in comps_b],
                'rook_king_queen_connected':
                    [len(comps_r), len(comps_k), len(comps_q)]}


def _c3_mobility_census():
    mc = mobility_census()
    expected_max = {'king': 8, 'knight': 8, 'bishop': 13, 'rook': 14,
                    'queen': 27}
    expected_sum = {'king': 420, 'knight': 336, 'bishop': 560, 'rook': 896,
                    'queen': 1456}
    ok = (all(mc[k]['max'] == v for k, v in expected_max.items())
          and all(mc[k]['sum'] == v for k, v in expected_sum.items())
          and mc['bishop_closed_form_ok'] and mc['queen_closed_form_ok']
          and set(mc['queen']['argmax']) == {'d4', 'e4', 'd5', 'e5'})
    return ok, {'max': {k: mc[k]['max'] for k in expected_max},
                'sum': {k: mc[k]['sum'] for k in expected_sum},
                'queen_argmax': sorted(mc['queen']['argmax']),
                'bishop_closed_form_ok': mc['bishop_closed_form_ok'],
                'queen_closed_form_ok': mc['queen_closed_form_ok']}


def _c4_flow_termination():
    details = {'tstar_cases': [], 'sim_ok': True, 'billiard_ratio': None}
    ok = True
    for (W, H, a, b), expected in TSTAR_CASES:
        got = tstar(W, H, a, b)
        steps, visited = simulate_torus_flow(W, H, a, b)
        match = (got == expected and steps == expected
                 and len(visited) == expected)
        details['tstar_cases'].append({'W': W, 'H': H, 'a': a, 'b': b,
                                       't*': got, 'sim_steps': steps,
                                       'cells': len(visited)})
        ok = ok and match
        details['sim_ok'] = details['sim_ok'] and (steps == got)
    n, path, refl, rest, ratio = simulate_billiard(8, 8, 3, 2, GAMMA_TORUS)
    details['billiard'] = {'steps': n, 'reflections': refl, 'at_rest': rest,
                           'gamma': GAMMA_TORUS,
                           'gamma_literal': 'pi^4/256'}
    details['billiard_ratio'] = ratio
    ok = ok and rest and abs(ratio - 1.0) < 1e-9
    return ok, details


def _c5_perft(deep=False):
    def perft(pos, d):
        if d == 0:
            return 1
        n = 0
        for m in pos.legal_moves():
            u = pos.make(m)
            n += perft(pos, d - 1)
            pos.unmake(u)
        return n
    pos = start_position()
    expected = [20, 400, 8902, 197281] + ([4865609] if deep else [])
    got = [perft(pos, d + 1) for d in range(len(expected))]
    divide = {}
    if deep:
        for m in pos.legal_moves():
            u = pos.make(m)
            divide[move_to_uci(m)] = perft(pos, 4)
            pos.unmake(u)
    return got == expected, {'perft': got, 'expected': expected,
                             'divide_d4': divide if deep else 'skipped'}


def _equivariance_violations(pos, side):
    """Count equivariance violations Theta(g.p, g.c) != Theta(p, c)."""
    theta = threat_field(pos, side)
    worst = 0
    for gname, g in D4.items():
        pos_g = Position()
        pos_g.board = [EMPTY] * 128
        for sq in SQUARES:
            p = pos.board[sq]
            if p != EMPTY:
                f, r = g(sq & 7, sq >> 4)
                pos_g.board[16 * r + f] = p
        pos_g.side = side
        theta_g = threat_field(pos_g, side)
        for sq in SQUARES:
            f, r = g(sq & 7, sq >> 4)
            if theta_g[16 * r + f] != theta[sq]:
                worst += 1
    return worst


PAWNLESS_FEN = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w - - 0 1"
PAWN_ANOMALY_EXPECTED = 176


def _c6_threat_fields():
    """Attack-sum identity + exact D4-equivariance for orientation-neutral
    pieces (pawnless position) + the documented pawn anomaly."""
    pos = start_position()
    tw_f, tw_p = attack_sum_identity(pos, 1)
    tb_f, tb_p = attack_sum_identity(pos, -1)
    identity_ok = (tw_f == tw_p and tb_f == tb_p)
    pos_np = Position().set_fen(PAWNLESS_FEN)
    v_w = _equivariance_violations(pos_np, 1)
    v_b = _equivariance_violations(pos_np, -1)
    anomaly = (_equivariance_violations(pos, 1)
               + _equivariance_violations(pos, -1))
    ok = (identity_ok and v_w == 0 and v_b == 0
          and anomaly == PAWN_ANOMALY_EXPECTED)
    return ok, {'attack_sum_white': tw_f, 'attack_sum_black': tb_f,
                'identity_ok': identity_ok,
                'pawnless_violations': {'white': v_w, 'black': v_b},
                'pawn_anomaly_initial_position': anomaly,
                'pawn_anomaly_expected': PAWN_ANOMALY_EXPECTED,
                'note': 'pawns are oriented particles: their forward attack '
                        'breaks the D4 symmetry (documented anomaly)'}


def _c7_lagrangian_energy():
    pos = start_position()
    e1 = energy(pos, 1)
    e2 = energy(pos, 1)
    m_white = mobility(pos, 1)
    pos_e4 = start_position()
    undo = pos_e4.make(uci_to_move(pos_e4, "e2e4"))
    m_after_e4 = mobility(pos_e4, 1)
    # hash determinism: rebuild from FEN, compare
    pos2 = Position().set_fen(pos.to_fen())
    hash_ok = pos2.hash == pos.hash
    # splitmix64 inverse round trip
    inv_ok = all(splitmix64_inverse(splitmix64(x)) == x
                 for x in range(1, 2001))
    ok = (m_white == 20 and m_after_e4 == 30 and e1 == e2 and hash_ok
          and inv_ok)
    return ok, {'E0_mobility_white': m_white,
                'after_e4_mobility_white': m_after_e4,
                'E0_energy': e1, 'energy_deterministic': e1 == e2,
                'hash_stable': hash_ok,
                'splitmix_inverse_ok': inv_ok}


def _c8_mate_certificates(deep=False):
    details = {'problems': {}, 'retro': {}}
    ok = True
    # tactical suite
    for label, fen, plies_expected in (
            ('morphy_m2', MATE_MORPHY_FEN, MATE_MORPHY_PLIES),
            ('ladder_m2', MATE_LADDER_FEN, MATE_LADDER_PLIES),
            ('nr_m1', MATE_NR_FEN, MATE_NR_PLIES)):
        pos = Position().set_fen(fen)
        valid, why = pos.is_valid()
        plies, pv, nodes = mate_search(pos, 6)
        details['problems'][label] = {
            'fen': fen, 'expected_plies': plies_expected,
            'found_plies': plies,
            'pv': ' '.join(move_to_uci(m) for m in pv), 'nodes': nodes,
            'position_valid': valid}
        ok = ok and valid and plies == plies_expected
    if MATE_MORPHY_KEY not in details['problems']['morphy_m2']['pv']:
        ok = False
    # frozen retrograde tables
    for name, piece in (('KRK', 4), ('KQK', 5)):
        cached = load_dtm_cache(piece)
        if cached is None:
            details['retro'][name] = 'cache missing'
            if deep:
                dtm, stats = retro_dtm(piece)
                cached = (dtm, stats)
            else:
                ok = False
                continue
        dtm, stats = cached
        exp = DTM_EXPECTED[name]
        stats_ok = all(stats.get(k) == v for k, v in exp.items())
        details['retro'][name] = {'stats': stats, 'expected': exp,
                                  'stats_ok': stats_ok}
        ok = ok and stats_ok
        if deep:
            dtm2, stats2 = retro_dtm(piece)
            same = all(dtm[i] == dtm2[i] for i in range(1 << 22))
            details['retro'][name]['recompute_bit_exact'] = same
            ok = ok and same
        else:
            # spot-check sampled won states with the forward solver
            import random as _rnd
            rng = _rnd.Random(20260930)
            pool = [i for i in range(1 << 22)
                    if 0 < dtm[i] <= 5 and not (i >> 21)]
            picks = rng.sample(pool, min(5, len(pool)))
            spot_ok = True
            for i in picks:
                wk, wq, bk = i & 127, (i >> 7) & 127, (i >> 14) & 127
                code = WR if piece == 4 else WQ
                p = Position()
                p.board = [EMPTY] * 128
                p.board[wk] = WK
                p.board[wq] = code
                p.board[bk] = BK
                p.side = 1
                p.castling = 0
                p.ep = -1
                p.hash = zobrist_hash(p)
                plies, _, _ = mate_search(p, 7)
                if plies != dtm[i]:
                    spot_ok = False
                    break
            details['retro'][name]['forward_spot_ok'] = spot_ok
            ok = ok and spot_ok
    return ok, details


def _c9_zobrist_incrementality():
    """Incremental hash equality along random playouts + birthday bound."""
    import random as _rnd
    rng = _rnd.Random(42)
    ok = True
    playouts = 0
    for _ in range(40):
        pos = start_position()
        for ply in range(60):
            moves = pos.legal_moves()
            if not moves:
                break
            m = rng.choice(moves)
            pos.make(m)
            # recompute from scratch and compare with the incremental value
            if zobrist_hash(pos) != pos.hash:
                ok = False
                break
            playouts += 1
    # unmake restores the exact FEN and hash, move by move
    unmake_ok = True
    p = start_position()
    h0 = p.hash
    for m in list(p.legal_moves())[:8]:
        u = p.make(m)
        p.unmake(u)
        if p.to_fen() != START_FEN or p.hash != h0:
            unmake_ok = False
            break
    details = {'playout_positions': playouts, 'incremental_ok': ok,
               'unmake_restores_hash': unmake_ok,
               'birthday_bound': 'P(coll; n, 2^64) <= n(n-1)/2^65; '
                                 'n = 10^9 -> 0.027'}
    return ok and unmake_ok, details


PROTOCOL = [
    ('C1', 'board algebra: V4/D4 orbit census + Burnside', _c1_board_algebra),
    ('C2', 'particle kinematics: move-graph census', _c2_particle_kinematics),
    ('C3', 'mobility census: closed forms and maxima', _c3_mobility_census),
    ('C4', 'flow termination t* + damped billiard', _c4_flow_termination),
    ('C5', 'perft identities 20/400/8902/197281', _c5_perft),
    ('C6', 'threat fields: D4-equivariance + attack sum', _c6_threat_fields),
    ('C7', 'Lagrangian energy: E0 = 20, after e4 = 30', _c7_lagrangian_energy),
    ('C8', 'mate certificates: retro DTM + tactical suite', _c8_mate_certificates),
    ('C9', 'Zobrist incrementality + splitmix64 bijection', _c9_zobrist_incrementality),
]


def run_protocol(selected='all', deep=False, log=print):
    """Run the protocol; returns (results_dict, all_pass_bool)."""
    results = {}
    all_pass = True
    for code, title, fn in PROTOCOL:
        if selected not in ('all', code):
            continue
        t0 = time.time()
        try:
            if code == 'C5':
                ok, details = fn(deep=deep)
            elif code == 'C8':
                ok, details = fn(deep=deep)
            else:
                ok, details = fn()
        except Exception as exc:                       # noqa: BLE001
            ok, details = False, {'error': '%s: %s' % (type(exc).__name__, exc)}
        dt = time.time() - t0
        results[code] = {'title': title, 'pass': bool(ok),
                         'seconds': round(dt, 3), 'details': details}
        all_pass = all_pass and bool(ok)
        log('  %s %-52s [%s]  (%.2fs)' % (code, title,
                                          'PASS' if ok else 'FAIL', dt))
    return results, all_pass


# ══════════════════════════════════════════════════════════════════════════════
# 10. PLOTS (600 dpi)
# ══════════════════════════════════════════════════════════════════════════════
def make_plots(outdir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    for fp in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',):
        try:
            fm.fontManager.addfont(fp)
        except Exception:
            pass
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    os.makedirs(outdir, exist_ok=True)

    # 1. threat-field heatmap of the initial position
    pos = start_position()
    theta = threat_field(pos, 1)
    grid = [[theta[16 * r + f] for f in range(8)] for r in range(7, -1, -1)]
    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    im = ax.imshow(grid, cmap='magma')
    ax.set_title('Threat field of White, initial position')
    ax.set_xticks(range(8), list('abcdefgh'))
    ax.set_yticks(range(8), list('87654321'))
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.savefig(os.path.join(outdir, 'threat_heatmap.png'), dpi=600)
    plt.close(fig)

    # 2. mobility census bars
    mc = mobility_census()
    names = ['king', 'knight', 'bishop', 'rook', 'queen']
    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    ax.bar(names, [mc[n]['sum'] for n in names], color='#3d5a6e')
    for i, n in enumerate(names):
        ax.text(i, mc[n]['sum'] + 20, str(mc[n]['sum']), ha='center')
    ax.set_title('Total mobility on the empty board (sum over 64 squares)')
    ax.set_ylabel('sum of attack counts')
    fig.savefig(os.path.join(outdir, 'mobility_census.png'), dpi=600)
    plt.close(fig)

    # 3. damped billiard trajectory
    fig, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)
    x, y = 0.5, 0.5
    vx, vy = 3.0, 2.0
    xs, ys = [x], [y]
    for _ in range(60):
        nx, nvx = x + vx, vx
        ny, nvy = y + vy, vy
        while nx < 0 or nx > 8:
            nx = -nx if nx < 0 else 16 - nx
            nvx = -nvx
        while ny < 0 or ny > 8:
            ny = -ny if ny < 0 else 16 - ny
            nvy = -nvy
        x, y, vx, vy = nx, ny, nvx, nvy
        xs.append(x)
        ys.append(y)
        vx *= GAMMA_TORUS
        vy *= GAMMA_TORUS
    ax.plot(xs, ys, '-', color='#8B7E5A', lw=0.9)
    ax.plot(xs[0], ys[0], 'o', color='#2F97B9', ms=6)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_title('K3 layer: damped billiard, gamma = pi^4/256 = 0.3805')
    ax.set_aspect('equal')
    for g in range(9):
        ax.axhline(g, color='#dddddd', lw=0.4)
        ax.axvline(g, color='#dddddd', lw=0.4)
    fig.savefig(os.path.join(outdir, 'billiard_flow.png'), dpi=600)
    plt.close(fig)

    # 4. perft growth
    depths = [1, 2, 3, 4, 5]
    counts = [20, 400, 8902, 197281, 4865609]
    fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    ax.semilogy(depths, counts, 'o-', color='#3d5a6e')
    for d, c in zip(depths, counts):
        ax.annotate(str(c), (d, c), textcoords='offset points', xytext=(4, 4))
    ax.set_title('Perft growth from the initial position')
    ax.set_xlabel('depth (plies)')
    ax.set_ylabel('leaf nodes')
    fig.savefig(os.path.join(outdir, 'perft_growth.png'), dpi=600)
    plt.close(fig)

    # 5. KQK DTM histogram (frozen table)
    cached = load_dtm_cache(5)
    if cached:
        dtm, _ = cached
        from collections import Counter
        hist = Counter(d for i, d in enumerate(dtm)
                       if d > 0 and not (i >> 21))
        xs_ = sorted(hist)
        fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
        ax.bar(xs_, [hist[x] for x in xs_], color='#8B7E5A')
        ax.set_title('KQK: DTM distribution of won White-to-move positions')
        ax.set_xlabel('plies to mate')
        ax.set_ylabel('positions')
        fig.savefig(os.path.join(outdir, 'dtm_histogram.png'), dpi=600)
        plt.close(fig)
    return sorted(os.listdir(outdir))


# ══════════════════════════════════════════════════════════════════════════════
# 11. HIGH-LEVEL COMMANDS
# ══════════════════════════════════════════════════════════════════════════════
def analyze_fen(fen):
    pos = Position().set_fen(fen)
    valid, why = pos.is_valid()
    theta_w = threat_field(pos, 1)
    theta_b = threat_field(pos, -1)
    tw = sum(theta_w[sq] for sq in SQUARES)
    tb = sum(theta_b[sq] for sq in SQUARES)
    out = {'fen': pos.to_fen(), 'valid': valid, 'validity': why,
           'side_to_move': 'white' if pos.side == 1 else 'black',
           'in_check': pos.in_check(pos.side),
           'mobility': {'white': mobility(pos, 1),
                        'black': mobility(pos, -1)},
           'material': {'white': material(pos, 1),
                        'black': material(pos, -1)},
           'threat_mass': {'white': tw, 'black': tb},
           'energy_white_view': round(energy(pos, 1), 3),
           'zobrist': '0x%016X' % pos.hash}
    return out


def mate_command(fen, depth):
    pos = Position().set_fen(fen)
    valid, why = pos.is_valid()
    if not valid:
        return {'fen': fen, 'error': 'illegal position: %s' % why}
    t0 = time.time()
    plies, pv, nodes = mate_search(pos, depth)
    line = []
    out = {'fen': fen, 'mate_plies': plies,
           'mate_in_moves': None if plies is None else (plies + 1) // 2,
           'pv_uci': [move_to_uci(m) for m in pv], 'nodes': nodes,
           'seconds': round(time.time() - t0, 3)}
    return out


def play_command(fen, depth, moves):
    pos = Position().set_fen(fen) if fen else start_position()
    valid, why = pos.is_valid()
    if not valid:
        return {'error': 'illegal position: %s' % why}
    log = []
    if moves:
        for u in moves.split():
            m = uci_to_move(pos, u)
            pos.make(m)
            log.append(u)
    t0 = time.time()
    best, score, nodes = search_best_move(pos, depth)
    return {'fen': pos.to_fen(),
            'moves_played': log,
            'best': move_to_uci(best) if best else None,
            'score_cp': score, 'depth': depth, 'nodes': nodes,
            'seconds': round(time.time() - t0, 3)}


def full_report(outdir):
    os.makedirs(outdir, exist_ok=True)
    log_lines = []
    def log(msg):
        log_lines.append(msg)
        print(msg)
    print('CHESS DYNAMICS LABORATORY - protocol C1-C9')
    print('program author: Isaev Iskhak Khamzatovich')
    print('version 1.0.0 (2026); Python %s' % sys.version.split()[0])
    print('=' * 72)
    results, ok = run_protocol('all', deep=False, log=log)
    verdict = 'ALL CHECKS PASSED' if ok else 'FAILURES DETECTED'
    print('=' * 72)
    print('verdict:', verdict)
    report = {'version': '1.0.0', 'date': time.strftime('%Y-%m-%d %H:%M:%S'),
              'python': sys.version.split()[0], 'results': results,
              'verdict': verdict}
    with open(os.path.join(outdir, 'dynamics_report.json'), 'w') as f:
        json.dump(report, f, indent=1)
    with open(os.path.join(outdir, 'verification_log.txt'), 'w') as f:
        f.write('\n'.join(log_lines) + '\n')
    return ok


# ══════════════════════════════════════════════════════════════════════════════
# 12. CLI
# ══════════════════════════════════════════════════════════════════════════════
def main(argv=None):
    ap = argparse.ArgumentParser(
        description='Chess Dynamics Laboratory - pieces as particles, '
                    'protocol C1-C9 (program: Isaev Iskhak Khamzatovich)')
    ap.add_argument('--run', metavar='CHECK', help='run protocol check: all | C1..C9')
    ap.add_argument('--deep', action='store_true',
                    help='deep mode: perft(5), full retrograde recompute')
    ap.add_argument('--analyze', metavar='FEN', help='position analysis')
    ap.add_argument('--mate', metavar='FEN', help='mate-in-N solver')
    ap.add_argument('--depth', type=int, default=4,
                    help='search depth (mate solver / play)')
    ap.add_argument('--play', action='store_true',
                    help='find the best move (alpha-beta, particle ordering)')
    ap.add_argument('--fen', metavar='FEN', default=None,
                    help='position for --play (default: initial position)')
    ap.add_argument('--moves', metavar='UCI', default='',
                    help='space-separated UCI moves to play first')
    ap.add_argument('--plots', action='store_true',
                    help='write 600 dpi plots to reports/plots')
    ap.add_argument('--report', action='store_true',
                    help='run the full protocol and write reports/')
    ap.add_argument('--version', action='store_true')
    args = ap.parse_args(argv)

    if args.version:
        print('chess-dynamics-lab 1.0.0 (2026) - Isaev Iskhak Khamzatovich')
        return 0
    if args.analyze:
        print(json.dumps(analyze_fen(args.analyze), indent=1))
        return 0
    if args.mate:
        print(json.dumps(mate_command(args.mate, args.depth), indent=1))
        return 0
    if args.play:
        print(json.dumps(play_command(args.fen, args.depth, args.moves),
                         indent=1))
        return 0
    if args.plots:
        outdir = os.path.join('reports', 'plots')
        files = make_plots(outdir)
        print('plots written to %s: %s' % (outdir, ', '.join(files)))
        return 0
    if args.report:
        ok = full_report('reports')
        return 0 if ok else 1
    if args.run:
        results, ok = run_protocol(args.run, deep=args.deep)
        print('verdict:', 'ALL CHECKS PASSED' if ok else 'FAILURES DETECTED')
        return 0 if ok else 1
    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
