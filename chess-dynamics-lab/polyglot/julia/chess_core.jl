#!/usr/bin/env julia
#=
chess_core.jl — POLYGLOT VERIFICATION CORE (Julia implementation)

Program author: Isaev Iskhak Khamzatovich
Repository: github.com/wild8highlander/chess-dynamics-lab
License: individual exclusive license (see LICENSE)

One core, seven languages: Python, C, Rust, Go, Julia (this file),
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

No randomness, no floating point, no external packages (Base only).

Pitfalls honored (see polyglot/c/chess_core.c and polyglot/python/chess_core.py):
  - piece codes are explicit constants: white 1..6, black -1..-6;
  - the queen slides in ALL 8 directions (KING_DIRS doubles as the queen
    direction set), rook/bishop in their 4, knights/kings 8 offsets;
  - en passant is generated only from the correct pawn rank (rank index 4
    for White, 3 for Black; rank 0 = White's first rank);
  - a pseudo move that would capture a king is never legal;
  - castling rights are updated when the king/rook moves or when a rook
    square is captured;
  - splitmix64 / Zobrist keys use native UInt64 machine arithmetic (silent
    wraparound, logical >>); signed piece codes are never mixed into the
    unsigned hash math, and UInt64 constants are used for the splitmix
    test vectors;
  - boards are Vector{Int} indexed by 0x88 square + 1 (Julia is 1-based):
    every read goes through getp(b, sq), every write through b[sq + 1];
    integer division uses div(), never / (no floating point).

Run:  julia julia/chess_core.jl        (expects the verdict 10/10)
=#

# ========================================================================
# board (0x88)
# ========================================================================
const EMPTY = 0
const WP = 1;  const WN = 2;  const WB = 3;  const WR = 4;  const WQ = 5;  const WK = 6
const BP = -1; const BN = -2; const BB = -3; const BR = -4; const BQ = -5; const BK = -6
const KNIGHT_OFFS = (31, 33, 14, 18, -31, -33, -14, -18)
const BISHOP_DIRS = (15, 17, -15, -17)
const ROOK_DIRS = (16, -16, 1, -1)
const KING_DIRS = (15, 16, 17, 1, -15, -16, -17, -1)   # also the queen's 8 dirs
const A1 = 0;  const E1 = 4;  const H1 = 7
const A8 = 112; const E8 = 116; const H8 = 119
const WK_CASTLE = 1; const WQ_CASTLE = 2; const BK_CASTLE = 4; const BQ_CASTLE = 8
const FLAG_NORMAL = 0; const FLAG_DOUBLE = 1; const FLAG_EP = 2; const FLAG_CASTLE = 3
const FILES = "abcdefgh"
const SQUARES = [16 * r + f for r in 0:7 for f in 0:7]

const CHAR_PIECE = Dict('P' => WP, 'N' => WN, 'B' => WB, 'R' => WR,
                        'Q' => WQ, 'K' => WK, 'p' => BP, 'n' => BN,
                        'b' => BB, 'r' => BR, 'q' => BQ, 'k' => BK)

# 0x88 square of a 2-char algebraic name like "e4" (rank 0 = White's 1st rank)
function name_sq(s::AbstractString)
    return 16 * (Int(s[2]) - Int('1')) + (Int(s[1]) - Int('a'))
end

# read a piece on a 0x88 square (Julia arrays are 1-based: index sq + 1)
getp(b::Vector{Int}, sq::Int) = b[sq + 1]

# move encoding: fr | to<<7 | promo<<14 | flag<<18  (same as the reference)
enc(fr, to, promo = 0, flag = 0) = fr | (to << 7) | (promo << 14) | (flag << 18)
m_from(m) = m & 127
m_to(m) = (m >> 7) & 127
m_promo(m) = (m >> 14) & 7
m_flag(m) = (m >> 18) & 3

mutable struct Pos
    board::Vector{Int}
    side::Int
    castling::Int
    ep::Int
end
Pos() = Pos(fill(EMPTY, 128), 1, 0, -1)

function set_fen!(pos::Pos, placement::AbstractString, side_ch::AbstractString,
                  castling::AbstractString, ep::AbstractString)
    fill!(pos.board, EMPTY)
    rank = 7
    file = 0
    for ch in placement
        if ch == '/'
            rank -= 1
            file = 0
        elseif ch >= '1' && ch <= '8'
            file += Int(ch) - Int('0')
        else
            pos.board[16 * rank + file + 1] = CHAR_PIECE[ch]
            file += 1
        end
    end
    pos.side = side_ch == "w" ? 1 : -1
    pos.castling = 0
    if castling != "-"
        for ch in castling
            pos.castling |= ch == 'K' ? WK_CASTLE : ch == 'Q' ? WQ_CASTLE : ch == 'k' ? BK_CASTLE : BQ_CASTLE
        end
    end
    pos.ep = ep == "-" ? -1 : name_sq(ep)
    return pos
end

# is `sq` attacked by side `by` (1 = White, -1 = Black)?
function attacked(b::Vector{Int}, sq::Int, by::Int)
    for off in (by == 1 ? (-15, -17) : (15, 17))
        s = sq + off
        if (s & 0x88) == 0 && getp(b, s) == by
            return true
        end
    end
    for off in KNIGHT_OFFS
        s = sq + off
        if (s & 0x88) == 0 && getp(b, s) == 2 * by
            return true
        end
    end
    for off in KING_DIRS
        s = sq + off
        if (s & 0x88) == 0 && getp(b, s) == 6 * by
            return true
        end
    end
    for (dirs, k1, k2) in ((BISHOP_DIRS, 3, 5), (ROOK_DIRS, 4, 5))
        for off in dirs
            s = sq + off
            while (s & 0x88) == 0
                p = getp(b, s)
                if p != EMPTY
                    if (p > 0) == (by > 0) && (abs(p) == k1 || abs(p) == k2)
                        return true
                    end
                    break
                end
                s += off
            end
        end
    end
    return false
end

function king_sq(pos::Pos, side::Int)
    t = 6 * side
    for sq in SQUARES
        if getp(pos.board, sq) == t
            return sq
        end
    end
    error("king missing")
end

function pseudo_moves(pos::Pos)
    b = pos.board
    side = pos.side
    moves = Int[]
    for fr in SQUARES
        p = getp(b, fr)
        if p == EMPTY || (p > 0) != (side > 0)
            continue
        end
        ap = abs(p)
        if ap == 1
            fwd = 16 * side
            rank = fr >> 4
            promo_rank = side == 1 ? 6 : 1
            start_rank = side == 1 ? 1 : 6
            s = fr + fwd
            if (s & 0x88) == 0 && getp(b, s) == EMPTY
                if rank == promo_rank
                    for pr in (5, 2, 4, 3)
                        push!(moves, enc(fr, s, pr))
                    end
                else
                    push!(moves, enc(fr, s))
                    if rank == start_rank && getp(b, s + fwd) == EMPTY
                        push!(moves, enc(fr, s + fwd, 0, FLAG_DOUBLE))
                    end
                end
            end
            for off in (fwd - 1, fwd + 1)
                s = fr + off
                if (s & 0x88) != 0
                    continue
                end
                q = getp(b, s)
                if q != EMPTY && (q > 0) != (side > 0)
                    if rank == promo_rank
                        for pr in (5, 2, 4, 3)
                            push!(moves, enc(fr, s, pr))
                        end
                    else
                        push!(moves, enc(fr, s))
                    end
                elseif s == pos.ep && q == EMPTY && rank == (side == 1 ? 4 : 3)
                    push!(moves, enc(fr, s, 0, FLAG_EP))
                end
            end
        elseif ap == 2 || ap == 6
            for off in (ap == 2 ? KNIGHT_OFFS : KING_DIRS)
                s = fr + off
                if (s & 0x88) != 0
                    continue
                end
                q = getp(b, s)
                if q == EMPTY || (q > 0) != (side > 0)
                    push!(moves, enc(fr, s))
                end
            end
        else
            dirs = ap == 4 ? ROOK_DIRS : (ap == 3 ? BISHOP_DIRS : KING_DIRS)
            for off in dirs
                s = fr + off
                while (s & 0x88) == 0
                    q = getp(b, s)
                    if q == EMPTY
                        push!(moves, enc(fr, s))
                    else
                        if (q > 0) != (side > 0)
                            push!(moves, enc(fr, s))
                        end
                        break
                    end
                    s += off
                end
            end
        end
    end
    # castling (king not in check, path squares empty and not attacked)
    if side == 1
        if (pos.castling & WK_CASTLE) != 0 && getp(b, 5) == EMPTY && getp(b, 6) == EMPTY &&
           getp(b, 4) == WK && getp(b, 7) == WR &&
           !attacked(b, 4, -1) && !attacked(b, 5, -1) && !attacked(b, 6, -1)
            push!(moves, enc(E1, 6, 0, FLAG_CASTLE))
        end
        if (pos.castling & WQ_CASTLE) != 0 && getp(b, 3) == EMPTY && getp(b, 2) == EMPTY &&
           getp(b, 1) == EMPTY && getp(b, 4) == WK && getp(b, 0) == WR &&
           !attacked(b, 4, -1) && !attacked(b, 3, -1) && !attacked(b, 2, -1)
            push!(moves, enc(E1, 2, 0, FLAG_CASTLE))
        end
    else
        if (pos.castling & BK_CASTLE) != 0 && getp(b, 117) == EMPTY && getp(b, 118) == EMPTY &&
           getp(b, 116) == BK && getp(b, 119) == BR &&
           !attacked(b, 116, 1) && !attacked(b, 117, 1) && !attacked(b, 118, 1)
            push!(moves, enc(E8, 118, 0, FLAG_CASTLE))
        end
        if (pos.castling & BQ_CASTLE) != 0 && getp(b, 115) == EMPTY && getp(b, 114) == EMPTY &&
           getp(b, 113) == EMPTY && getp(b, 116) == BK && getp(b, 112) == BR &&
           !attacked(b, 116, 1) && !attacked(b, 115, 1) && !attacked(b, 114, 1)
            push!(moves, enc(E8, 114, 0, FLAG_CASTLE))
        end
    end
    return moves
end

mutable struct Undo
    m::Int
    captured::Int
    castling::Int
    ep::Int
end

function make!(pos::Pos, m::Int)
    b = pos.board
    fr = m_from(m)
    to = m_to(m)
    promo = m_promo(m)
    flag = m_flag(m)
    side = pos.side
    piece = getp(b, fr)
    captured = getp(b, to)
    u = Undo(m, captured, pos.castling, pos.ep)
    b[fr + 1] = EMPTY
    if flag == FLAG_EP
        b[to - 16 * side + 1] = EMPTY
    end
    b[to + 1] = promo != 0 ? promo * side : piece
    if flag == FLAG_CASTLE
        if to == 6
            b[7 + 1] = EMPTY;  b[5 + 1] = WR
        elseif to == 2
            b[0 + 1] = EMPTY;  b[3 + 1] = WR
        elseif to == 118
            b[119 + 1] = EMPTY; b[117 + 1] = BR
        else
            b[112 + 1] = EMPTY; b[115 + 1] = BR
        end
    end
    if piece == WK
        pos.castling &= ~(WK_CASTLE | WQ_CASTLE)
    elseif piece == BK
        pos.castling &= ~(BK_CASTLE | BQ_CASTLE)
    end
    if fr == H1 || to == H1
        pos.castling &= ~WK_CASTLE
    end
    if fr == A1 || to == A1
        pos.castling &= ~WQ_CASTLE
    end
    if fr == H8 || to == H8
        pos.castling &= ~BK_CASTLE
    end
    if fr == A8 || to == A8
        pos.castling &= ~BQ_CASTLE
    end
    pos.ep = flag == FLAG_DOUBLE ? fr + 16 * side : -1
    pos.side = -side
    return u
end

function unmake!(pos::Pos, u::Undo)
    b = pos.board
    fr = m_from(u.m)
    to = m_to(u.m)
    promo = m_promo(u.m)
    flag = m_flag(u.m)
    side = -pos.side
    piece = getp(b, to)
    if promo != 0
        piece = side
    end
    b[fr + 1] = piece
    b[to + 1] = u.captured
    if flag == FLAG_EP
        b[to - 16 * side + 1] = -side
    end
    if flag == FLAG_CASTLE
        if to == 6
            b[7 + 1] = WR;  b[5 + 1] = EMPTY
        elseif to == 2
            b[0 + 1] = WR;  b[3 + 1] = EMPTY
        elseif to == 118
            b[119 + 1] = BR; b[117 + 1] = EMPTY
        else
            b[112 + 1] = BR; b[115 + 1] = EMPTY
        end
    end
    pos.castling = u.castling
    pos.ep = u.ep
    pos.side = side
    return nothing
end

function legal_moves(pos::Pos)
    tmp = Pos(copy(pos.board), pos.side, pos.castling, pos.ep)
    out = Int[]
    for m in pseudo_moves(tmp)
        if abs(getp(tmp.board, m_to(m))) == 6   # a king capture is never legal
            continue
        end
        u = make!(tmp, m)
        if !attacked(tmp.board, king_sq(tmp, -tmp.side), tmp.side)
            push!(out, m)
        end
        unmake!(tmp, u)
    end
    return out
end

function uci_to_move(pos::Pos, u::AbstractString)
    fr = name_sq(u[1:2])
    to = name_sq(u[3:4])
    pr = 0
    if length(u) >= 5
        c = u[5]
        pr = c == 'q' ? 5 : c == 'n' ? 2 : c == 'r' ? 4 : c == 'b' ? 3 : 0
    end
    for m in legal_moves(pos)
        if m_from(m) == fr && m_to(m) == to && m_promo(m) == pr
            return m
        end
    end
    error("illegal move " * String(u))
end

function perft(pos::Pos, d::Int)
    if d == 0
        return 1
    end
    n = 0
    for m in legal_moves(pos)
        u = make!(pos, m)
        n += perft(pos, d - 1)
        unmake!(pos, u)
    end
    return n
end

# ========================================================================
# splitmix64 (native UInt64 arithmetic: wraps silently, >> is logical)
# ========================================================================
function splitmix64(x::UInt64)
    x += 0x9E3779B97F4A7C15
    z = x
    z = xor(z, z >> 30) * 0xBF58476D1CE4E5B9
    z = xor(z, z >> 27) * 0x94D049BB133111EB
    return xor(z, z >> 31)
end

# ========================================================================
# algebra helpers (D4 / V4 groups on (file, rank) pairs)
# ========================================================================
g_id(f, r) = (f, r)
g_rot90(f, r) = (r, 7 - f)
g_rot180(f, r) = (7 - f, 7 - r)
g_rot270(f, r) = (7 - r, f)
g_mirh(f, r) = (7 - f, r)
g_mirv(f, r) = (f, 7 - r)
g_diag(f, r) = (r, f)
g_anti(f, r) = (7 - r, 7 - f)

const D4 = [g_id, g_rot90, g_rot180, g_rot270, g_mirh, g_mirv, g_diag, g_anti]
const V4 = [g_id, g_rot180, g_diag, g_anti]

function orbits(group)
    seen = Set{Tuple{Int,Int}}()
    cnt = 0
    small = 0
    big = 0
    for f in 0:7
        for r in 0:7
            if (f, r) in seen
                continue
            end
            orb = Set{Tuple{Int,Int}}()
            for g in group
                push!(orb, g(f, r))
            end
            union!(seen, orb)
            cnt += 1
            if length(orb) == 2
                small += 1
            elseif length(orb) == 4
                big += 1
            end
        end
    end
    return cnt, small, big
end

function tstar(W::Int, H::Int, a::Int, b::Int)
    gx = gcd(abs(a), W)
    if gx == 0
        gx = W
    end
    gy = gcd(abs(b), H)
    if gy == 0
        gy = H
    end
    return lcm(div(W, gx), div(H, gy))
end

# squares attacked by the piece on sq; blocking=true stops sliders at blockers
function attack_squares(b::Vector{Int}, sq::Int, blocking::Bool)
    p = getp(b, sq)
    ap = abs(p)
    out = Int[]
    if ap == 1
        fwd = 16 * (p > 0 ? 1 : -1)
        for off in (fwd - 1, fwd + 1)
            s = sq + off
            if (s & 0x88) == 0
                push!(out, s)
            end
        end
    elseif ap == 2 || ap == 6
        for off in (ap == 2 ? KNIGHT_OFFS : KING_DIRS)
            s = sq + off
            if (s & 0x88) == 0
                push!(out, s)
            end
        end
    else
        dirs = ap == 4 ? ROOK_DIRS : (ap == 3 ? BISHOP_DIRS : KING_DIRS)
        for off in dirs
            s = sq + off
            while (s & 0x88) == 0
                push!(out, s)
                if blocking && getp(b, s) != EMPTY
                    break
                end
                s += off
            end
        end
    end
    return out
end

# violations of Theta(g.p, g.c) == Theta(p, c) over g in D4
function equivariance_violations(board::Vector{Int}, side::Int)
    theta = fill(0, 128)
    for sq in SQUARES
        p = getp(board, sq)
        if p != EMPTY && (p > 0) == (side > 0)
            for s in attack_squares(board, sq, true)
                theta[s + 1] += 1
            end
        end
    end
    bad = 0
    for g in D4
        bg = fill(EMPTY, 128)
        for sq in SQUARES
            p = getp(board, sq)
            if p != EMPTY
                f, r = g(sq & 7, sq >> 4)
                bg[16 * r + f + 1] = p
            end
        end
        tg = fill(0, 128)
        for sq in SQUARES
            p = getp(bg, sq)
            if p != EMPTY && (p > 0) == (side > 0)
                for s in attack_squares(bg, sq, true)
                    tg[s + 1] += 1
                end
            end
        end
        for sq in SQUARES
            f, r = g(sq & 7, sq >> 4)
            if tg[16 * r + f + 1] != theta[sq + 1]
                bad += 1
            end
        end
    end
    return bad
end

const KNIGHT_TOUR = split("f5 h4 g2 e1 c2 a1 b3 c1 a2 b4 a6 b8 d7 f8 h7 " *
                          "g5 h3 g1 e2 g3 h1 f2 d1 b2 d3 f4 h5 g7 e8 f6 " *
                          "g8 h6 g4 h2 f1 e3 d5 c7 a8 b6 a4 c3 b1 a3 b5 " *
                          "a7 c8 e7 g6 h8 f7 e5 f3 d2 c4 a5 c6 d4 e6 d8 " *
                          "b7 c5 e4 d6")

function is_knight_move(a::Int, b::Int)
    df = abs((a & 7) - (b & 7))
    dr = abs((a >> 4) - (b >> 4))
    return (df == 1 && dr == 2) || (df == 2 && dr == 1)
end

# forced-mate search: shortest mate for the side to move, 0 = none
function mate_search_plies(pos::Pos, max_depth::Int)
    for depth in 1:max_depth
        res = mate_dfs(pos, depth)
        if res != 0
            return res
        end
    end
    return 0
end

function mate_dfs(pos::Pos, depth::Int)
    if depth <= 0
        return 0
    end
    best = 0
    for m in legal_moves(pos)
        u = make!(pos, m)
        replies = legal_moves(pos)
        if isempty(replies)
            mated = attacked(pos.board, king_sq(pos, pos.side), -pos.side)
            unmake!(pos, u)
            if mated
                return 1
            end
            continue
        end
        if depth >= 2
            all_mated = true
            worst = 0
            for r in replies
                u2 = make!(pos, r)
                sub = mate_dfs(pos, depth - 2)
                unmake!(pos, u2)
                if sub == 0
                    all_mated = false
                    break
                end
                if sub > worst
                    worst = sub
                end
            end
            if all_mated
                unmake!(pos, u)
                cand = worst + 2
                if best == 0 || cand < best
                    best = cand
                    if best <= 3
                        return best
                    end
                end
                continue
            end
        end
        unmake!(pos, u)
    end
    return best
end

# every black reply to the key move must walk into a mate in 1
function key_mates_in_2(pos::Pos, fr_sq::Int, to_sq::Int)
    for m in legal_moves(pos)
        if m_from(m) == fr_sq && m_to(m) == to_sq
            u = make!(pos, m)
            ok_all = true
            for r in legal_moves(pos)
                u2 = make!(pos, r)
                sub = mate_search_plies(pos, 1)
                unmake!(pos, u2)
                if sub != 1
                    ok_all = false
                    break
                end
            end
            unmake!(pos, u)
            return ok_all
        end
    end
    return false
end

# ========================================================================
# THE BATTERY
# ========================================================================
function main()
    passed = 0
    total = 0
    function report(code, ok, note)
        passed += ok ? 1 : 0
        total += 1
        println("[$(ok ? "PASS" : "FAIL")] $(code)  $(note)")
        return nothing
    end

    # -- 1 board algebra -------------------------------------------------
    cnt, small, big = orbits(V4)
    d_cnt, _, _ = orbits(D4)
    burnside_d4 = div(64 + 0 + 0 + 0 + 0 + 0 + 8 + 8, 8)
    burnside_v4 = div(64 + 0 + 8 + 8, 4)
    note = "V4=$(cnt)($(small)+$(big)) D4=$(d_cnt) burnside $(burnside_v4)/$(burnside_d4)"
    report("C1", cnt == 20 && small == 8 && big == 12 && d_cnt == 10 &&
           burnside_d4 == 10 && burnside_v4 == 20, note)

    # -- 2 move-graph census ----------------------------------------------
    board = fill(EMPTY, 128)
    types = (WR, WB, WN, WK, WQ)
    directed = zeros(Int, 5)
    for i in 1:5
        for sq in SQUARES
            board[sq + 1] = types[i]
            directed[i] += length(attack_squares(board, sq, true))
            board[sq + 1] = EMPTY
        end
    end
    e = [div(directed[i], 2) for i in 1:5]
    note = "edges R$(e[1]) B$(e[2]) N$(e[3]) K$(e[4]) Q$(e[5])"
    report("C2", e[1] == 448 && e[2] == 280 && e[3] == 168 && e[4] == 210 &&
           e[5] == 728, note)

    # -- 3 mobility census -------------------------------------------------
    sums = directed   # single piece on an empty board: no blockers anywhere
    maxima = zeros(Int, 5)
    for i in 1:5
        for sq in SQUARES
            board[sq + 1] = types[i]
            m = length(attack_squares(board, sq, false))
            if m > maxima[i]
                maxima[i] = m
            end
            board[sq + 1] = EMPTY
        end
    end
    bishop_ok = true
    for sq in SQUARES
        f = sq & 7
        r = sq >> 4
        board[sq + 1] = WB
        m = length(attack_squares(board, sq, false))
        board[sq + 1] = EMPTY
        if m != 14 - abs(f - r) - abs(f + r - 7)
            bishop_ok = false
        end
    end
    note = "sums R$(sums[1]) B$(sums[2]) N$(sums[3]) K$(sums[4]) Q$(sums[5]); " *
           "max $(maxima[1])/$(maxima[2])/$(maxima[3])/$(maxima[4])/$(maxima[5])"
    report("C3", sums == [896, 560, 336, 420, 1456] &&
           maxima == [14, 13, 8, 8, 27] && bishop_ok, note)

    # -- 4 flow termination ------------------------------------------------
    cases = ((8, 8, 1, 1, 8), (8, 8, 3, 5, 8), (8, 8, 2, 2, 4),
             (8, 8, 1, 2, 8), (8, 8, 1, 0, 8), (8, 8, 2, 1, 8),
             (48, 48, 1, 1, 48), (24, 36, 3, 5, 72), (12, 12, 4, 6, 6))
    ok = true
    parts = String[]
    idx = 0
    for (W, H, a, b, t) in cases
        idx += 1
        ts = tstar(W, H, a, b)
        if idx <= 5
            push!(parts, string(ts))
        end
        if ts != t
            ok = false
        end
    end
    note = "9 t* cases: " * join(parts, ",")
    report("C4", ok, note)

    # -- 5 perft identities --------------------------------------------------
    pos = set_fen!(Pos(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "w", "KQkq", "-")
    p1 = perft(pos, 1)
    p2 = perft(pos, 2)
    p3 = perft(pos, 3)
    p4 = perft(pos, 4)
    note = "perft $(p1) $(p2) $(p3) $(p4)"
    report("C5", p1 == 20 && p2 == 400 && p3 == 8902 && p4 == 197281, note)

    # -- 6 threat fields -------------------------------------------------------
    pawnless = fill(EMPTY, 128)
    back = (WR, WN, WB, WQ, WK, WB, WN, WR)
    for f in 0:7
        pawnless[f + 1] = back[f + 1]
        pawnless[112 + f + 1] = -back[f + 1]
    end
    v_w = equivariance_violations(pawnless, 1)
    v_b = equivariance_violations(pawnless, -1)
    start = fill(EMPTY, 128)
    for f in 0:7
        start[f + 1] = back[f + 1]
        start[112 + f + 1] = -back[f + 1]
        start[16 + f + 1] = WP
        start[96 + f + 1] = BP
    end
    anomaly = equivariance_violations(start, 1) + equivariance_violations(start, -1)
    note = "pawnless violations $(v_w)/$(v_b), pawn anomaly $(anomaly)"
    report("C6", v_w == 0 && v_b == 0 && anomaly == 176, note)

    # -- 7 kinetic energy ---------------------------------------------------------
    pos = set_fen!(Pos(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "w", "KQkq", "-")
    m0 = length(legal_moves(pos))
    u = make!(pos, uci_to_move(pos, "e2e4"))
    pos.side = 1                       # count White's mobility
    m1 = length(legal_moves(pos))
    pos.side = -1
    unmake!(pos, u)
    note = "White mobility $(m0) -> $(m1) after 1.e4"
    report("C7", m0 == 20 && m1 == 30, note)

    # -- 8 mate certificates --------------------------------------------------------
    morphy = set_fen!(Pos(), "kbK5/pp6/1P6/8/8/8/8/R7", "w", "-", "-")
    key_ok = key_mates_in_2(morphy, name_sq("a1"), name_sq("a6"))
    plies_m = mate_search_plies(morphy, 4)
    ladder = set_fen!(Pos(), "7k/8/8/8/8/8/R7/1R4K1", "w", "-", "-")
    plies_l = mate_search_plies(ladder, 4)
    nr = set_fen!(Pos(), "7k/8/5N1K/8/8/8/8/6R1", "w", "-", "-")
    plies_n = mate_search_plies(nr, 2)
    nr_key = false
    for m in legal_moves(nr)
        if m_from(m) == name_sq("g1") && m_to(m) == name_sq("g8")
            u = make!(nr, m)
            replies = legal_moves(nr)
            mated = isempty(replies) && attacked(nr.board, king_sq(nr, nr.side), -nr.side)
            unmake!(nr, u)
            nr_key = mated
            break
        end
    end
    note = "morphy $(plies_m)(key a1a6) ladder $(plies_l) nr $(plies_n)(key g1g8)"
    report("C8", plies_m == 3 && key_ok && plies_l == 3 && plies_n == 1 &&
           nr_key, note)

    # -- 9 zobrist incrementality (fixed playout) -------------------------------------
    zob = Dict{Int,Vector{UInt64}}()
    state = UInt64(1)
    for piece in (1, 2, 3, 4, 5, 6, -1, -2, -3, -4, -5, -6)
        tbl = fill(UInt64(0), 128)
        for sq in 0:127
            state = splitmix64(state)
            tbl[sq + 1] = state
        end
        zob[piece] = tbl
    end
    side_key = splitmix64(state)

    function full_hash(b::Vector{Int}, side::Int)
        h = UInt64(0)
        for sq in SQUARES
            p = getp(b, sq)
            if p != EMPTY
                h = xor(h, zob[p][sq + 1])
            end
        end
        if side == -1
            h = xor(h, side_key)
        end
        return h
    end

    playout = ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6", "e1g1",
               "f8c5", "d2d3", "d7d6")
    pos = set_fen!(Pos(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "w", "KQkq", "-")
    h = full_hash(pos.board, pos.side)
    inc_ok = h == full_hash(pos.board, 1)
    for u_ in playout
        m = uci_to_move(pos, u_)
        fr = m_from(m)
        to = m_to(m)
        piece = getp(pos.board, fr)
        captured = getp(pos.board, to)
        h = xor(h, zob[piece][fr + 1])
        if captured != EMPTY
            h = xor(h, zob[captured][to + 1])
        end
        promo = m_promo(m)
        if promo != 0
            h = xor(h, zob[promo * pos.side][to + 1], zob[piece][to + 1])
        else
            h = xor(h, zob[piece][to + 1])
        end
        side = pos.side
        if m_flag(m) == FLAG_EP                 # en passant: captured pawn
            cap = to - 16 * side
            h = xor(h, zob[getp(pos.board, cap)][cap + 1])
        end
        if m_flag(m) == FLAG_CASTLE             # castling: rook relocation
            if to == 6
                h = xor(h, zob[WR][7 + 1], zob[WR][5 + 1])
            elseif to == 2
                h = xor(h, zob[WR][0 + 1], zob[WR][3 + 1])
            elseif to == 118
                h = xor(h, zob[BR][119 + 1], zob[BR][117 + 1])
            else
                h = xor(h, zob[BR][112 + 1], zob[BR][115 + 1])
            end
        end
        make!(pos, m)
        h = xor(h, side_key)
        if h != full_hash(pos.board, pos.side)
            inc_ok = false
            break
        end
    end
    sm_ok = splitmix64(UInt64(1)) == 0x910A2DEC89025CC1 &&
            splitmix64(UInt64(2)) == 0x975835DE1C9756CE &&
            splitmix64(UInt64(3)) == 0x1D0B14E4DB018FED
    note = "incremental hash over $(length(playout)) plies, splitmix vectors $(sm_ok ? "ok" : "BAD")"
    report("C9", inc_ok && sm_ok, note)

    # -- 10 knight tour certificate ------------------------------------------------------
    tour = [name_sq(s) for s in KNIGHT_TOUR]
    distinct = length(Set(tour)) == 64
    closed = true
    for i in 1:64
        nxt = (i % 64) + 1
        if !is_knight_move(tour[i], tour[nxt])
            closed = false
            break
        end
    end
    note = "tour 64 distinct cells, closure $(closed ? "ok" : "BAD")"
    report("C10", distinct && closed, note)

    # -- report ---------------------------------------------------------------------------
    println("verdict: $(passed)/$(total)")
    return passed == total ? 0 : 1
end

exit(main())
