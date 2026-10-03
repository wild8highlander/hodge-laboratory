// chess_core.rs — POLYGLOT VERIFICATION CORE (Rust implementation)
//
// Program author: Isaev Iskhak Khamzatovich
// Repository: github.com/wild8highlander/chess-dynamics-lab
// License: individual exclusive license (see LICENSE)
//
// The same 10-check battery as polyglot/python/chess_core.py:
//
//   C1  board algebra      V4 orbits 20 (8x2 + 12x4), D4 orbits 10 (Burnside)
//   C2  move-graph census  edges R448 B280 N168 K210 Q728
//   C3  mobility census    sums R896 B560 N336 K420 Q1456, max 14/13/8/8/27
//   C4  flow termination   t* = lcm(W/gcd(a,W), H/gcd(b,H)) on 9 cases
//   C5  perft identities   20 / 400 / 8902 / 197281 from the initial position
//   C6  threat fields      D4-equivariance (pawnless) + pawn anomaly 176
//   C7  kinetic energy     initial mobility 20, after 1.e4 mobility 30
//   C8  mate certificates  Morphy m2 (a1a6), ladder m2, N+R m1 (g1g8)
//   C9  Zobrist hashing    incremental hash over a fixed playout + splitmix64
//   C10 knight tour        the frozen closed tour: 64 cells, closure move
//
// Build:  rustc -O rust/chess_core.rs -o chess_core_rs && ./chess_core_rs
// Run:    ./chess_core_rs            (expects the verdict 10/10)
//
// No external crates (std only), no randomness, no floating point.
// Piece codes are EXPLICIT constants (white 1..6, black -1..-6) — no
// auto-increment enums that would break on negatives.
// splitmix64 / Zobrist use native wrapping u64 arithmetic
// (wrapping_add / wrapping_mul so debug builds do not panic).
// Classic perft pitfalls respected below: sliders use ALL their
// directions (queen 8, rook/bishop 4), en-passant capture is generated
// only from the correct pawn rank (4 for White, 3 for Black, 0-based),
// a move that would capture a king is never legal, and castling rights
// are updated when the king/rook moves or a rook square is captured.

// ── board (0x88): sq = 16*rank + file, off-board iff (sq & 0x88) != 0 ──

const EMPTY: i32 = 0;
const WP: i32 = 1;
const WN: i32 = 2;
const WB: i32 = 3;
const WR: i32 = 4;
const WQ: i32 = 5;
const WK: i32 = 6;
const BP: i32 = -1;
const BN: i32 = -2;
const BB: i32 = -3;
const BR: i32 = -4;
const BQ: i32 = -5;
const BK: i32 = -6;

const KNIGHT_OFFS: [i32; 8] = [31, 33, 14, 18, -31, -33, -14, -18];
const BISHOP_DIRS: [i32; 4] = [15, 17, -15, -17];
const ROOK_DIRS: [i32; 4] = [16, -16, 1, -1];
const KING_DIRS: [i32; 8] = [15, 16, 17, 1, -15, -16, -17, -1];

const A1: i32 = 0;
const E1: i32 = 4;
const H1: i32 = 7;
const A8: i32 = 112;
const E8: i32 = 116;
const H8: i32 = 119;

const WK_CASTLE: i32 = 1;
const WQ_CASTLE: i32 = 2;
const BK_CASTLE: i32 = 4;
const BQ_CASTLE: i32 = 8;

const FLAG_NORMAL: i32 = 0;
const FLAG_DOUBLE: i32 = 1;
const FLAG_EP: i32 = 2;
const FLAG_CASTLE: i32 = 3;

const EXPECTED_SM: [u64; 3] = [
    0x910A2DEC89025CC1, // splitmix64(1)
    0x975835DE1C9756CE, // splitmix64(2)
    0x1D0B14E4DB018FED, // splitmix64(3)
];

// the frozen closed knight tour (from polyglot/python/chess_core.py)
const KNIGHT_TOUR: [&str; 64] = [
    "f5", "h4", "g2", "e1", "c2", "a1", "b3", "c1", "a2", "b4", "a6", "b8",
    "d7", "f8", "h7", "g5", "h3", "g1", "e2", "g3", "h1", "f2", "d1", "b2",
    "d3", "f4", "h5", "g7", "e8", "f6", "g8", "h6", "g4", "h2", "f1", "e3",
    "d5", "c7", "a8", "b6", "a4", "c3", "b1", "a3", "b5", "a7", "c8", "e7",
    "g6", "h8", "f7", "e5", "f3", "d2", "c4", "a5", "c6", "d4", "e6", "d8",
    "b7", "c5", "e4", "d6",
];

// D4 group acting on (file, rank) pairs:
//   0 id, 1 rot90, 2 rot180, 3 rot270,
//   4 mirror-h, 5 mirror-v, 6 main diagonal, 7 anti diagonal.
fn d4_apply(g: usize, f: i32, r: i32) -> (i32, i32) {
    match g {
        0 => (f, r),
        1 => (r, 7 - f),
        2 => (7 - f, 7 - r),
        3 => (7 - r, f),
        4 => (7 - f, r),
        5 => (f, 7 - r),
        6 => (r, f),
        _ => (7 - r, 7 - f),
    }
}

// V4 subgroup = id, rot180, diag, anti (indices into the D4 list)
const V4_IDX: [usize; 4] = [0, 2, 6, 7];

fn name_sq(s: &str) -> i32 {
    let b = s.as_bytes();
    let f = (b[0] - b'a') as i32;
    let r = (b[1] - b'1') as i32;
    16 * r + f
}

fn char_piece(ch: char) -> i32 {
    match ch {
        'P' => WP,
        'N' => WN,
        'B' => WB,
        'R' => WR,
        'Q' => WQ,
        'K' => WK,
        'p' => BP,
        'n' => BN,
        'b' => BB,
        'r' => BR,
        'q' => BQ,
        'k' => BK,
        _ => EMPTY,
    }
}

#[derive(Clone, Copy)]
struct Move {
    fr: i32,
    to: i32,
    promo: i32, // piece type 2..5, sign applied on make; 0 = none
    flag: i32,
}

const EMPTY_MOVE: Move = Move { fr: 0, to: 0, promo: 0, flag: 0 };

struct Position {
    board: [i32; 128],
    side: i32, // 1 = White to move, -1 = Black to move
    castling: i32,
    ep: i32, // en-passant target square or -1
}

fn clone_pos(p: &Position) -> Position {
    Position {
        board: p.board,
        side: p.side,
        castling: p.castling,
        ep: p.ep,
    }
}

#[derive(Clone, Copy)]
struct Undo {
    m: Move,
    captured: i32,
    castling: i32,
    ep: i32,
}

fn set_fen(pos: &mut Position, fen: &str) {
    let parts: Vec<&str> = fen.split_whitespace().collect();
    for i in 0..128 {
        pos.board[i] = EMPTY;
    }
    pos.side = 1;
    pos.castling = 0;
    pos.ep = -1;
    let mut rank = 7i32;
    let mut file = 0i32;
    for ch in parts[0].chars() {
        if ch == '/' {
            rank -= 1;
            file = 0;
            continue;
        }
        if ch >= '0' && ch <= '9' {
            file += ch as i32 - '0' as i32;
            continue;
        }
        pos.board[(16 * rank + file) as usize] = char_piece(ch);
        file += 1;
    }
    if parts.len() > 1 {
        pos.side = if parts[1] == "w" { 1 } else { -1 };
    }
    if parts.len() > 2 && parts[2] != "-" {
        for ch in parts[2].chars() {
            pos.castling |= match ch {
                'K' => 1,
                'Q' => 2,
                'k' => 4,
                'q' => 8,
                _ => 0,
            };
        }
    }
    if parts.len() > 3 && parts[3] != "-" {
        pos.ep = name_sq(parts[3]);
    }
}

fn attacked(b: &[i32; 128], sq: i32, by: i32) -> bool {
    // pawns: a white pawn (by == 1) attacks sq from sq-15 / sq-17
    let pawn_offs: [i32; 2] = if by == 1 { [-15, -17] } else { [15, 17] };
    for i in 0..2 {
        let s = sq + pawn_offs[i];
        if (s & 0x88) == 0 && b[s as usize] == by {
            return true;
        }
    }
    for i in 0..8 {
        let s = sq + KNIGHT_OFFS[i];
        if (s & 0x88) == 0 && b[s as usize] == 2 * by {
            return true;
        }
    }
    for i in 0..8 {
        let s = sq + KING_DIRS[i];
        if (s & 0x88) == 0 && b[s as usize] == 6 * by {
            return true;
        }
    }
    for dset in 0..2usize {
        let kinds: [i32; 2] = if dset == 0 { [3, 5] } else { [4, 5] };
        let dirs: &[i32] = if dset == 0 { &BISHOP_DIRS } else { &ROOK_DIRS };
        for i in 0..4 {
            let off = dirs[i];
            let mut s = sq + off;
            while (s & 0x88) == 0 {
                let p = b[s as usize];
                if p != EMPTY {
                    if (p > 0) == (by > 0)
                        && (p.abs() == kinds[0] || p.abs() == kinds[1])
                    {
                        return true;
                    }
                    break;
                }
                s += off;
            }
        }
    }
    false
}

fn king_sq(pos: &Position, side: i32) -> i32 {
    let t = 6 * side;
    for sq in 0..128 {
        if (sq & 0x88) != 0 {
            continue;
        }
        if pos.board[sq as usize] == t {
            return sq;
        }
    }
    panic!("king missing");
}

fn pseudo_moves(pos: &Position, out: &mut [Move; 256]) -> usize {
    let b = &pos.board;
    let side = pos.side;
    let mut n = 0usize;
    for rank in 0..8i32 {
        for file in 0..8i32 {
            let fr = 16 * rank + file;
            let piece = b[fr as usize];
            if piece == EMPTY || (piece > 0) != (side > 0) {
                continue;
            }
            let ap = piece.abs();
            if ap == 1 {
                let fwd = 16 * side;
                let promo_rank = if side == 1 { 6 } else { 1 };
                let start_rank = if side == 1 { 1 } else { 6 };
                let mut s = fr + fwd;
                if (s & 0x88) == 0 && b[s as usize] == EMPTY {
                    if rank == promo_rank {
                        let prs = [5i32, 2, 4, 3];
                        for k in 0..4 {
                            out[n] = Move { fr, to: s, promo: prs[k], flag: FLAG_NORMAL };
                            n += 1;
                        }
                    } else {
                        out[n] = Move { fr, to: s, promo: 0, flag: FLAG_NORMAL };
                        n += 1;
                        if rank == start_rank && b[(s + fwd) as usize] == EMPTY {
                            out[n] = Move { fr, to: s + fwd, promo: 0, flag: FLAG_DOUBLE };
                            n += 1;
                        }
                    }
                }
                for k in 0..2 {
                    let delta = if k == 0 { -1i32 } else { 1 };
                    let off = fwd + delta;
                    s = fr + off;
                    if (s & 0x88) != 0 {
                        continue;
                    }
                    let q = b[s as usize];
                    if q != EMPTY && (q > 0) != (side > 0) {
                        if rank == promo_rank {
                            let prs = [5i32, 2, 4, 3];
                            for j in 0..4 {
                                out[n] = Move { fr, to: s, promo: prs[j], flag: FLAG_NORMAL };
                                n += 1;
                            }
                        } else {
                            out[n] = Move { fr, to: s, promo: 0, flag: FLAG_NORMAL };
                            n += 1;
                        }
                    } else if s == pos.ep && q == EMPTY
                        && rank == (if side == 1 { 4 } else { 3 })
                    {
                        // en passant only from the correct pawn rank
                        out[n] = Move { fr, to: s, promo: 0, flag: FLAG_EP };
                        n += 1;
                    }
                }
            } else if ap == 2 || ap == 6 {
                let offs: &[i32] = if ap == 2 { &KNIGHT_OFFS } else { &KING_DIRS };
                for i in 0..8 {
                    let s = fr + offs[i];
                    if (s & 0x88) != 0 {
                        continue;
                    }
                    let q = b[s as usize];
                    if q == EMPTY || (q > 0) != (side > 0) {
                        out[n] = Move { fr, to: s, promo: 0, flag: FLAG_NORMAL };
                        n += 1;
                    }
                }
            } else {
                // sliders: rook 4 dirs, bishop 4 dirs, queen 8 dirs
                let dirs: &[i32] = if ap == 4 {
                    &ROOK_DIRS
                } else if ap == 3 {
                    &BISHOP_DIRS
                } else {
                    &KING_DIRS
                };
                let cnt: usize = if ap >= 5 { 8 } else { 4 };
                for i in 0..cnt {
                    let off = dirs[i];
                    let mut s = fr + off;
                    while (s & 0x88) == 0 {
                        let q = b[s as usize];
                        if q == EMPTY {
                            out[n] = Move { fr, to: s, promo: 0, flag: FLAG_NORMAL };
                            n += 1;
                        } else {
                            if (q > 0) != (side > 0) {
                                out[n] = Move { fr, to: s, promo: 0, flag: FLAG_NORMAL };
                                n += 1;
                            }
                            break;
                        }
                        s += off;
                    }
                }
            }
        }
    }
    // castling: rights present, path empty, rook in place,
    // king does not pass through or land on an attacked square
    if side == 1 {
        if (pos.castling & WK_CASTLE) != 0
            && b[5] == EMPTY && b[6] == EMPTY
            && b[4] == WK && b[7] == WR
            && !attacked(b, 4, -1) && !attacked(b, 5, -1) && !attacked(b, 6, -1)
        {
            out[n] = Move { fr: E1, to: 6, promo: 0, flag: FLAG_CASTLE };
            n += 1;
        }
        if (pos.castling & WQ_CASTLE) != 0
            && b[3] == EMPTY && b[2] == EMPTY && b[1] == EMPTY
            && b[4] == WK && b[0] == WR
            && !attacked(b, 4, -1) && !attacked(b, 3, -1) && !attacked(b, 2, -1)
        {
            out[n] = Move { fr: E1, to: 2, promo: 0, flag: FLAG_CASTLE };
            n += 1;
        }
    } else {
        if (pos.castling & BK_CASTLE) != 0
            && b[117] == EMPTY && b[118] == EMPTY
            && b[116] == BK && b[119] == BR
            && !attacked(b, 116, 1) && !attacked(b, 117, 1) && !attacked(b, 118, 1)
        {
            out[n] = Move { fr: E8, to: 118, promo: 0, flag: FLAG_CASTLE };
            n += 1;
        }
        if (pos.castling & BQ_CASTLE) != 0
            && b[115] == EMPTY && b[114] == EMPTY && b[113] == EMPTY
            && b[116] == BK && b[112] == BR
            && !attacked(b, 116, 1) && !attacked(b, 115, 1) && !attacked(b, 114, 1)
        {
            out[n] = Move { fr: E8, to: 114, promo: 0, flag: FLAG_CASTLE };
            n += 1;
        }
    }
    n
}

fn make(pos: &mut Position, m: Move) -> Undo {
    let side = pos.side;
    let fr = m.fr;
    let to = m.to;
    let piece = pos.board[fr as usize];
    let u = Undo {
        m: m,
        captured: pos.board[to as usize],
        castling: pos.castling,
        ep: pos.ep,
    };
    pos.board[fr as usize] = EMPTY;
    if m.flag == FLAG_EP {
        pos.board[(to - 16 * side) as usize] = EMPTY;
    }
    pos.board[to as usize] = if m.promo != 0 { m.promo * side } else { piece };
    if m.flag == FLAG_CASTLE {
        if to == 6 {
            pos.board[7] = EMPTY;
            pos.board[5] = WR;
        } else if to == 2 {
            pos.board[0] = EMPTY;
            pos.board[3] = WR;
        } else if to == 118 {
            pos.board[119] = EMPTY;
            pos.board[117] = BR;
        } else {
            pos.board[112] = EMPTY;
            pos.board[115] = BR;
        }
    }
    // castling-rights updates (king move, rook move, rook captured)
    if piece == WK {
        pos.castling &= !(WK_CASTLE | WQ_CASTLE);
    } else if piece == BK {
        pos.castling &= !(BK_CASTLE | BQ_CASTLE);
    }
    if fr == H1 || to == H1 {
        pos.castling &= !WK_CASTLE;
    }
    if fr == A1 || to == A1 {
        pos.castling &= !WQ_CASTLE;
    }
    if fr == H8 || to == H8 {
        pos.castling &= !BK_CASTLE;
    }
    if fr == A8 || to == A8 {
        pos.castling &= !BQ_CASTLE;
    }
    pos.ep = if m.flag == FLAG_DOUBLE { fr + 16 * side } else { -1 };
    pos.side = -side;
    u
}

fn unmake(pos: &mut Position, u: Undo) {
    let m = u.m;
    let side = -pos.side; // the side that made the move
    let fr = m.fr;
    let to = m.to;
    let mut piece = pos.board[to as usize];
    if m.promo != 0 {
        piece = side; // was a pawn before the promotion
    }
    pos.board[fr as usize] = piece;
    pos.board[to as usize] = u.captured;
    if m.flag == FLAG_EP {
        pos.board[(to - 16 * side) as usize] = -side;
    }
    if m.flag == FLAG_CASTLE {
        if to == 6 {
            pos.board[7] = WR;
            pos.board[5] = EMPTY;
        } else if to == 2 {
            pos.board[0] = WR;
            pos.board[3] = EMPTY;
        } else if to == 118 {
            pos.board[119] = BR;
            pos.board[117] = EMPTY;
        } else {
            pos.board[112] = BR;
            pos.board[115] = EMPTY;
        }
    }
    pos.castling = u.castling;
    pos.ep = u.ep;
    pos.side = side;
}

fn legal_moves(pos: &Position, out: &mut [Move; 256]) -> usize {
    let mut tmp = clone_pos(pos);
    let mut pm = [EMPTY_MOVE; 256];
    let np = pseudo_moves(&tmp, &mut pm);
    let mut n = 0usize;
    for i in 0..np {
        let m = pm[i];
        if tmp.board[m.to as usize].abs() == 6 {
            continue; // a move that captures a king is never legal
        }
        let u = make(&mut tmp, m);
        let ks = king_sq(&tmp, -tmp.side);
        if !attacked(&tmp.board, ks, tmp.side) {
            out[n] = m;
            n += 1;
        }
        unmake(&mut tmp, u);
    }
    n
}

fn perft(pos: &mut Position, depth: i32) -> i64 {
    if depth == 0 {
        return 1;
    }
    let mut mv = [EMPTY_MOVE; 256];
    let n = legal_moves(pos, &mut mv);
    if depth == 1 {
        return n as i64;
    }
    let mut total = 0i64;
    for i in 0..n {
        let u = make(pos, mv[i]);
        total += perft(pos, depth - 1);
        unmake(pos, u);
    }
    total
}

// ── splitmix64 (wrapping u64 arithmetic) ────────────────────────────────

fn splitmix64(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9E3779B97F4A7C15u64);
    let mut z = x;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9u64);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EBu64);
    z ^ (z >> 31)
}

// ── t* flow termination ─────────────────────────────────────────────────

fn gcd_i(mut a: i32, mut b: i32) -> i32 {
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

fn lcm_i(a: i32, b: i32) -> i32 {
    a / gcd_i(a, b) * b
}

fn tstar(w: i32, h: i32, a: i32, b: i32) -> i32 {
    let mut gx = gcd_i(a.abs(), w);
    if gx == 0 {
        gx = w;
    }
    let mut gy = gcd_i(b.abs(), h);
    if gy == 0 {
        gy = h;
    }
    lcm_i(w / gx, h / gy)
}

// ── attack squares (threat field kernel) ────────────────────────────────

// Squares attacked by the piece on `sq`; `blocking` stops sliders at
// the first occupied square (the target square itself is included).
fn attack_squares(b: &[i32; 128], sq: i32, blocking: bool, out: &mut [i32; 64]) -> usize {
    let p = b[sq as usize];
    let ap = p.abs();
    let mut n = 0usize;
    if ap == 1 {
        let sign = if p > 0 { 1i32 } else { -1 };
        let fwd = 16 * sign;
        for k in 0..2 {
            let delta = if k == 0 { -1i32 } else { 1 };
            let s = sq + fwd + delta;
            if (s & 0x88) == 0 {
                out[n] = s;
                n += 1;
            }
        }
    } else if ap == 2 || ap == 6 {
        let offs: &[i32] = if ap == 2 { &KNIGHT_OFFS } else { &KING_DIRS };
        for i in 0..8 {
            let s = sq + offs[i];
            if (s & 0x88) == 0 {
                out[n] = s;
                n += 1;
            }
        }
    } else {
        let dirs: &[i32] = if ap == 4 {
            &ROOK_DIRS
        } else if ap == 3 {
            &BISHOP_DIRS
        } else {
            &KING_DIRS
        };
        let cnt: usize = if ap >= 5 { 8 } else { 4 };
        for i in 0..cnt {
            let off = dirs[i];
            let mut s = sq + off;
            while (s & 0x88) == 0 {
                out[n] = s;
                n += 1;
                if blocking && b[s as usize] != EMPTY {
                    break;
                }
                s += off;
            }
        }
    }
    n
}

fn equivariance_violations(board: &[i32; 128], side: i32) -> i32 {
    // Theta(g.p, g.c) == Theta(p, c) must hold for every g in D4
    let mut theta = [0i32; 128];
    let mut buf = [0i32; 64];
    for sq in 0..128i32 {
        if (sq & 0x88) != 0 {
            continue;
        }
        let p = board[sq as usize];
        if p != EMPTY && (p > 0) == (side > 0) {
            let n = attack_squares(board, sq, true, &mut buf);
            for k in 0..n {
                theta[buf[k] as usize] += 1;
            }
        }
    }
    let mut bad = 0i32;
    for gi in 0..8usize {
        let mut bg = [0i32; 128];
        for sq in 0..128i32 {
            if (sq & 0x88) != 0 {
                continue;
            }
            let p = board[sq as usize];
            if p != EMPTY {
                let (f2, r2) = d4_apply(gi, sq & 7, sq >> 4);
                bg[(16 * r2 + f2) as usize] = p;
            }
        }
        let mut tg = [0i32; 128];
        for sq in 0..128i32 {
            if (sq & 0x88) != 0 {
                continue;
            }
            let p = bg[sq as usize];
            if p != EMPTY && (p > 0) == (side > 0) {
                let n = attack_squares(&bg, sq, true, &mut buf);
                for k in 0..n {
                    tg[buf[k] as usize] += 1;
                }
            }
        }
        for sq in 0..128i32 {
            if (sq & 0x88) != 0 {
                continue;
            }
            let (f2, r2) = d4_apply(gi, sq & 7, sq >> 4);
            if tg[(16 * r2 + f2) as usize] != theta[sq as usize] {
                bad += 1;
            }
        }
    }
    bad
}

fn knight_neighbour(a: i32, b: i32) -> bool {
    let df = ((a & 7) - (b & 7)).abs();
    let dr = ((a >> 4) - (b >> 4)).abs();
    (df == 1 && dr == 2) || (df == 2 && dr == 1)
}

// ── forced-mate search (same algorithm as the references) ───────────────
// mate_dfs returns the length in plies of the shortest forced mate for
// the side to move within `depth` plies, or 0 if there is none.  The
// defender must have ALL replies lose; iterative deepening 1..max_depth
// in mate_search_plies; early return once best <= 3.

fn mate_dfs(pos: &mut Position, depth: i32) -> i32 {
    if depth <= 0 {
        return 0;
    }
    let mut mv = [EMPTY_MOVE; 256];
    let n = legal_moves(pos, &mut mv);
    let mut best = 0i32;
    for i in 0..n {
        let u = make(pos, mv[i]);
        let mut rep = [EMPTY_MOVE; 256];
        let rn = legal_moves(pos, &mut rep);
        if rn == 0 {
            let mated = attacked(&pos.board, king_sq(pos, pos.side), -pos.side);
            unmake(pos, u);
            if mated {
                return 1;
            }
            continue;
        }
        if depth >= 2 {
            let mut all_mated = true;
            let mut worst = 0i32;
            for j in 0..rn {
                let u2 = make(pos, rep[j]);
                let sub = mate_dfs(pos, depth - 2);
                unmake(pos, u2);
                if sub == 0 {
                    all_mated = false;
                    break;
                }
                if sub > worst {
                    worst = sub;
                }
            }
            if all_mated {
                unmake(pos, u);
                let cand = worst + 2;
                if best == 0 || cand < best {
                    best = cand;
                    if best <= 3 {
                        return best;
                    }
                }
                continue;
            }
        }
        unmake(pos, u);
    }
    best
}

fn mate_search_plies(pos: &mut Position, max_depth: i32) -> i32 {
    for depth in 1..=max_depth {
        let res = mate_dfs(pos, depth);
        if res != 0 {
            return res;
        }
    }
    0
}

fn uci_to_move(pos: &Position, uci: &str) -> Move {
    let fr = name_sq(&uci[0..2]);
    let to = name_sq(&uci[2..4]);
    let pr: i32 = if uci.len() > 4 {
        match uci.as_bytes()[4] {
            b'q' => 5,
            b'n' => 2,
            b'r' => 4,
            b'b' => 3,
            _ => 0,
        }
    } else {
        0
    };
    let mut mv = [EMPTY_MOVE; 256];
    let n = legal_moves(pos, &mut mv);
    for i in 0..n {
        if mv[i].fr == fr && mv[i].to == to && mv[i].promo == pr {
            return mv[i];
        }
    }
    panic!("illegal move {}", uci);
}

fn key_mates_in_2(pos: &mut Position, fr_sq: i32, to_sq: i32) -> bool {
    // after the key move, EVERY defender reply must lose to a mate in 1
    let mut mv = [EMPTY_MOVE; 256];
    let n = legal_moves(pos, &mut mv);
    for i in 0..n {
        let m = mv[i];
        if m.fr == fr_sq && m.to == to_sq {
            let u = make(pos, m);
            let mut ok_all = true;
            let mut rep = [EMPTY_MOVE; 256];
            let rn = legal_moves(pos, &mut rep);
            for j in 0..rn {
                let u2 = make(pos, rep[j]);
                let sub = mate_search_plies(pos, 1);
                unmake(pos, u2);
                if sub != 1 {
                    ok_all = false;
                    break;
                }
            }
            unmake(pos, u);
            return ok_all;
        }
    }
    false
}

// ── Zobrist tables (chained splitmix64, Python generation order) ────────

// rows 0..5 = white P,N,B,R,Q,K ; rows 6..11 = black P,N,B,R,Q,K
fn zob_row(piece: i32) -> usize {
    if piece > 0 {
        (piece - 1) as usize
    } else {
        (5 - piece) as usize
    }
}

fn full_hash(board: &[i32; 128], side: i32, zob: &[[u64; 128]; 12], side_key: u64) -> u64 {
    let mut h = 0u64;
    for sq in 0..128i32 {
        if (sq & 0x88) != 0 {
            continue;
        }
        let p = board[sq as usize];
        if p != EMPTY {
            h ^= zob[zob_row(p)][sq as usize];
        }
    }
    if side == -1 {
        h ^= side_key;
    }
    h
}

// ── the battery ─────────────────────────────────────────────────────────

fn check(code: &str, ok: bool, note: &str, pass_count: &mut i32, total: &mut i32) {
    *total += 1;
    if ok {
        *pass_count += 1;
    }
    println!("[{}] {}  {}", if ok { "PASS" } else { "FAIL" }, code, note);
}

fn main() {
    let mut pass_count = 0i32;
    let mut total = 0i32;

    // ── 1 board algebra ─────────────────────────────────────────────
    {
        let mut seen = [[false; 8]; 8];
        let mut cnt = 0i32;
        let mut small = 0i32;
        let mut big = 0i32;
        for f in 0..8i32 {
            for r in 0..8i32 {
                if seen[f as usize][r as usize] {
                    continue;
                }
                let mut sz = 0i32;
                let mut orbs = [(0i32, 0i32); 8];
                for k in 0..4usize {
                    let t = d4_apply(V4_IDX[k], f, r);
                    let mut dup = false;
                    for j in 0..sz as usize {
                        if orbs[j] == t {
                            dup = true;
                        }
                    }
                    if !dup {
                        orbs[sz as usize] = t;
                        sz += 1;
                    }
                    seen[t.0 as usize][t.1 as usize] = true;
                }
                cnt += 1;
                if sz == 2 {
                    small += 1;
                } else if sz == 4 {
                    big += 1;
                }
            }
        }
        let mut dseen = [[false; 8]; 8];
        let mut dcnt = 0i32;
        for f in 0..8i32 {
            for r in 0..8i32 {
                if dseen[f as usize][r as usize] {
                    continue;
                }
                for gi in 0..8usize {
                    let t = d4_apply(gi, f, r);
                    dseen[t.0 as usize][t.1 as usize] = true;
                }
                dcnt += 1;
            }
        }
        // Burnside fixed-point counts, hard-coded as in the reference:
        // D4 = [id, rot90, rot180, rot270, mirh, mirv, diag, anti]
        let bd4 = (64 + 0 + 0 + 0 + 0 + 0 + 8 + 8) / 8;
        // V4 = [id, rot180, diag, anti]
        let bv4 = (64 + 0 + 8 + 8) / 4;
        let note = format!(
            "V4={}({}+{}) D4={} burnside {}/{}",
            cnt, small, big, dcnt, bv4, bd4
        );
        let ok = cnt == 20 && small == 8 && big == 12 && dcnt == 10
            && bd4 == 10 && bv4 == 20;
        check("C1", ok, &note, &mut pass_count, &mut total);
    }

    // ── 2 move-graph census ─────────────────────────────────────────
    let mut board = [0i32; 128];
    let mut buf = [0i32; 64];
    let types = [WR, WB, WN, WK, WQ];
    let mut directed = [0i32; 5];
    for t in 0..5usize {
        for sq in 0..128i32 {
            if (sq & 0x88) != 0 {
                continue;
            }
            board[sq as usize] = types[t];
            directed[t] += attack_squares(&board, sq, true, &mut buf) as i32;
            board[sq as usize] = EMPTY;
        }
    }
    {
        let note = format!(
            "edges R{} B{} N{} K{} Q{}",
            directed[0] / 2, directed[1] / 2, directed[2] / 2,
            directed[3] / 2, directed[4] / 2
        );
        let ok = directed[0] / 2 == 448 && directed[1] / 2 == 280
            && directed[2] / 2 == 168 && directed[3] / 2 == 210
            && directed[4] / 2 == 728;
        check("C2", ok, &note, &mut pass_count, &mut total);
    }

    // ── 3 mobility census ───────────────────────────────────────────
    {
        let sums = directed; // same directed counts as C2 (empty board)
        let mut maxima = [0i32; 5];
        for t in 0..5usize {
            for sq in 0..128i32 {
                if (sq & 0x88) != 0 {
                    continue;
                }
                board[sq as usize] = types[t];
                let m = attack_squares(&board, sq, false, &mut buf) as i32;
                if m > maxima[t] {
                    maxima[t] = m;
                }
                board[sq as usize] = EMPTY;
            }
        }
        let mut bishop_ok = true;
        for sq in 0..128i32 {
            if (sq & 0x88) != 0 {
                continue;
            }
            let f = sq & 7;
            let r = sq >> 4;
            board[sq as usize] = WB;
            let m = attack_squares(&board, sq, false, &mut buf) as i32;
            board[sq as usize] = EMPTY;
            if m != 14 - (f - r).abs() - (f + r - 7).abs() {
                bishop_ok = false;
            }
        }
        let note = format!(
            "sums R{} B{} N{} K{} Q{}; max {}/{}/{}/{}/{}",
            sums[0], sums[1], sums[2], sums[3], sums[4],
            maxima[0], maxima[1], maxima[2], maxima[3], maxima[4]
        );
        let ok = sums == [896, 560, 336, 420, 1456]
            && maxima == [14, 13, 8, 8, 27]
            && bishop_ok;
        check("C3", ok, &note, &mut pass_count, &mut total);
    }

    // ── 4 flow termination ──────────────────────────────────────────
    {
        let w9 = [8i32, 8, 8, 8, 8, 8, 48, 24, 12];
        let h9 = [8i32, 8, 8, 8, 8, 8, 48, 36, 12];
        let a9 = [1i32, 3, 2, 1, 1, 2, 1, 3, 4];
        let b9 = [1i32, 5, 2, 2, 0, 1, 1, 5, 6];
        let e9 = [8i32, 8, 4, 8, 8, 8, 48, 72, 6];
        let mut got = [0i32; 9];
        let mut ok = true;
        for k in 0..9usize {
            got[k] = tstar(w9[k], h9[k], a9[k], b9[k]);
            if got[k] != e9[k] {
                ok = false;
            }
        }
        let note = format!(
            "9 t* cases: {},{},{},{},{}",
            got[0], got[1], got[2], got[3], got[4]
        );
        check("C4", ok, &note, &mut pass_count, &mut total);
    }

    // ── 5 perft identities ──────────────────────────────────────────
    let mut p = Position { board: [0i32; 128], side: 1, castling: 0, ep: -1 };
    set_fen(&mut p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    let p1 = perft(&mut p, 1);
    let p2 = perft(&mut p, 2);
    let p3 = perft(&mut p, 3);
    let p4 = perft(&mut p, 4);
    {
        let note = format!("perft {} {} {} {}", p1, p2, p3, p4);
        let ok = p1 == 20 && p2 == 400 && p3 == 8902 && p4 == 197281;
        check("C5", ok, &note, &mut pass_count, &mut total);
    }

    // ── 6 threat fields ─────────────────────────────────────────────
    {
        let back = [WR, WN, WB, WQ, WK, WB, WN, WR];
        let mut pawnless = [0i32; 128];
        for f in 0..8usize {
            pawnless[f] = back[f];
            pawnless[112 + f] = -back[f];
        }
        let v_w = equivariance_violations(&pawnless, 1);
        let v_b = equivariance_violations(&pawnless, -1);
        let mut start = [0i32; 128];
        for f in 0..8usize {
            start[f] = back[f];
            start[112 + f] = -back[f];
            start[16 + f] = WP;
            start[96 + f] = BP;
        }
        let anomaly = equivariance_violations(&start, 1)
            + equivariance_violations(&start, -1);
        let note = format!(
            "pawnless violations {}/{}, pawn anomaly {}",
            v_w, v_b, anomaly
        );
        let ok = v_w == 0 && v_b == 0 && anomaly == 176;
        check("C6", ok, &note, &mut pass_count, &mut total);
    }

    // ── 7 kinetic energy ────────────────────────────────────────────
    {
        let mut p = Position { board: [0i32; 128], side: 1, castling: 0, ep: -1 };
        set_fen(&mut p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
        let mut mv = [EMPTY_MOVE; 256];
        let m0 = legal_moves(&p, &mut mv);
        let key = uci_to_move(&p, "e2e4");
        let u = make(&mut p, key);
        p.side = 1; // count White's mobility after 1.e4
        let m1 = legal_moves(&p, &mut mv);
        p.side = -1;
        unmake(&mut p, u);
        let note = format!("White mobility {} -> {} after 1.e4", m0, m1);
        let ok = m0 == 20 && m1 == 30;
        check("C7", ok, &note, &mut pass_count, &mut total);
    }

    // ── 8 mate certificates ─────────────────────────────────────────
    {
        let mut p = Position { board: [0i32; 128], side: 1, castling: 0, ep: -1 };
        set_fen(&mut p, "kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1");
        let plies_m = mate_search_plies(&mut p, 4);
        let key_ok = key_mates_in_2(&mut p, name_sq("a1"), name_sq("a6"));
        set_fen(&mut p, "7k/8/8/8/8/8/R7/1R4K1 w - - 0 1");
        let plies_l = mate_search_plies(&mut p, 4);
        set_fen(&mut p, "7k/8/5N1K/8/8/8/8/6R1 w - - 0 1");
        let plies_n = mate_search_plies(&mut p, 2);
        // N+R mate in 1 with key g1g8: after Rg8 there are no replies
        // and the black king is attacked
        let mut nr_key = false;
        {
            let mut mv = [EMPTY_MOVE; 256];
            let n = legal_moves(&p, &mut mv);
            let g1 = name_sq("g1");
            let g8 = name_sq("g8");
            for i in 0..n {
                if mv[i].fr == g1 && mv[i].to == g8 {
                    let u = make(&mut p, mv[i]);
                    let mut rep = [EMPTY_MOVE; 256];
                    let rn = legal_moves(&p, &mut rep);
                    let mated = rn == 0
                        && attacked(&p.board, king_sq(&p, p.side), -p.side);
                    unmake(&mut p, u);
                    nr_key = mated;
                    break;
                }
            }
        }
        let note = format!(
            "morphy {}(key a1a6) ladder {} nr {}(key g1g8)",
            plies_m, plies_l, plies_n
        );
        let ok = plies_m == 3 && key_ok && plies_l == 3 && plies_n == 1 && nr_key;
        check("C8", ok, &note, &mut pass_count, &mut total);
    }

    // ── 9 zobrist incrementality (fixed playout) ─────────────────────
    {
        let mut zob = [[0u64; 128]; 12];
        let mut state = 1u64;
        for row in 0..12usize {
            for sq in 0..128usize {
                state = splitmix64(state);
                zob[row][sq] = state;
            }
        }
        let side_key = splitmix64(state);
        let mut p = Position { board: [0i32; 128], side: 1, castling: 0, ep: -1 };
        set_fen(&mut p, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
        let mut h = full_hash(&p.board, p.side, &zob, side_key);
        let mut inc_ok = h == full_hash(&p.board, 1, &zob, side_key);
        let playout = [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1b5",
            "g8f6", "e1g1", "f8c5", "d2d3", "d7d6",
        ];
        for &uci in playout.iter() {
            if !inc_ok {
                break;
            }
            let key = uci_to_move(&p, uci);
            let piece = p.board[key.fr as usize];
            let captured = p.board[key.to as usize];
            h ^= zob[zob_row(piece)][key.fr as usize];
            if captured != EMPTY {
                h ^= zob[zob_row(captured)][key.to as usize];
            }
            let promo = key.promo;
            if promo != 0 {
                h ^= zob[zob_row(promo * p.side)][key.to as usize]
                    ^ zob[zob_row(piece)][key.to as usize];
            } else {
                h ^= zob[zob_row(piece)][key.to as usize];
            }
            let side = p.side;
            if key.flag == FLAG_EP {
                // en passant: remove the captured pawn from the hash
                let cap_sq = (key.to - 16 * side) as usize;
                h ^= zob[zob_row(p.board[cap_sq])][cap_sq];
            }
            if key.flag == FLAG_CASTLE {
                // castling: move the rook in the hash
                if key.to == 6 {
                    h ^= zob[zob_row(WR)][7] ^ zob[zob_row(WR)][5];
                } else if key.to == 2 {
                    h ^= zob[zob_row(WR)][0] ^ zob[zob_row(WR)][3];
                } else if key.to == 118 {
                    h ^= zob[zob_row(BR)][119] ^ zob[zob_row(BR)][117];
                } else {
                    h ^= zob[zob_row(BR)][112] ^ zob[zob_row(BR)][115];
                }
            }
            make(&mut p, key);
            h ^= side_key;
            if h != full_hash(&p.board, p.side, &zob, side_key) {
                inc_ok = false;
            }
        }
        let sm_ok = splitmix64(1) == EXPECTED_SM[0]
            && splitmix64(2) == EXPECTED_SM[1]
            && splitmix64(3) == EXPECTED_SM[2];
        let note = format!(
            "incremental hash over 10 plies, splitmix vectors {}",
            if sm_ok { "ok" } else { "BAD" }
        );
        check("C9", inc_ok && sm_ok, &note, &mut pass_count, &mut total);
    }

    // ── 10 knight tour certificate ──────────────────────────────────
    {
        let mut tour = [0i32; 64];
        for i in 0..64usize {
            tour[i] = name_sq(KNIGHT_TOUR[i]);
        }
        let mut seen_t = [false; 128];
        let mut distinct = true;
        for i in 0..64usize {
            if seen_t[tour[i] as usize] {
                distinct = false;
            }
            seen_t[tour[i] as usize] = true;
        }
        let mut closed = true;
        for i in 0..64usize {
            if !knight_neighbour(tour[i], tour[(i + 1) % 64]) {
                closed = false;
                break;
            }
        }
        let note = format!(
            "tour 64 distinct cells, closure {}",
            if closed { "ok" } else { "BAD" }
        );
        check("C10", distinct && closed, &note, &mut pass_count, &mut total);
    }

    println!("verdict: {}/{}", pass_count, total);
    std::process::exit(if pass_count == total { 0 } else { 1 });
}
