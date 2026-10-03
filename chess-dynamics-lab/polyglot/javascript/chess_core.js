#!/usr/bin/env node
/*
  chess_core.js — POLYGLOT VERIFICATION CORE (JavaScript implementation)

  Program author: Isaev Iskhak Khamzatovich
  Repository: github.com/wild8highlander/chess-dynamics-lab
  License: individual exclusive license (see LICENSE)

  The same 10-check battery as polyglot/python/chess_core.py.
  Run:  node chess_core.js     (expects the verdict 10/10)
*/
'use strict';

// ── board (0x88) ───────────────────────────────────────────────────────
const EMPTY = 0;
const WP = 1, WN = 2, WB = 3, WR = 4, WQ = 5, WK = 6;
const BP = -1, BN = -2, BB = -3, BR = -4, BQ = -5, BK = -6;
const KNIGHT_OFFS = [31, 33, 14, 18, -31, -33, -14, -18];
const BISHOP_DIRS = [15, 17, -15, -17];
const ROOK_DIRS = [16, -16, 1, -1];
const KING_DIRS = [15, 16, 17, 1, -15, -16, -17, -1];
const WK_CASTLE = 1, WQ_CASTLE = 2, BK_CASTLE = 4, BQ_CASTLE = 8;
const FLAG_DOUBLE = 1, FLAG_EP = 2, FLAG_CASTLE = 3;
const FILES = 'abcdefgh';
const SQUARES = [];
for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) SQUARES.push(16 * r + f);

function name_sq(s) { return 16 * (s.charCodeAt(1) - 49) + FILES.indexOf(s[0]); }

function Pos() {
  this.board = new Int8Array(128);
  this.side = 1;
  this.castling = 0;
  this.ep = -1;
}

Pos.prototype.setFen = function (placement, sideCh, castling, ep) {
  this.board.fill(0);
  let rank = 7, file = 0;
  const CHAR = { P: WP, N: WN, B: WB, R: WR, Q: WQ, K: WK,
                 p: BP, n: BN, b: BB, r: BR, q: BQ, k: BK };
  for (const ch of placement) {
    if (ch === '/') { rank--; file = 0; continue; }
    if (ch >= '1' && ch <= '8') { file += +ch; continue; }
    this.board[16 * rank + file++] = CHAR[ch];
  }
  this.side = sideCh === 'w' ? 1 : -1;
  this.castling = 0;
  if (castling !== '-') for (const ch of castling)
    this.castling |= ch === 'K' ? WK_CASTLE : ch === 'Q' ? WQ_CASTLE
                   : ch === 'k' ? BK_CASTLE : BQ_CASTLE;
  this.ep = ep === '-' ? -1 : name_sq(ep);
  return this;
};

function attacked(b, sq, by) {
  const poffs = by === 1 ? [-15, -17] : [15, 17];
  for (const off of poffs) {
    const s = sq + off;
    if (!(s & 0x88) && b[s] === by) return true;
  }
  for (const off of KNIGHT_OFFS) {
    const s = sq + off;
    if (!(s & 0x88) && b[s] === 2 * by) return true;
  }
  for (const off of KING_DIRS) {
    const s = sq + off;
    if (!(s & 0x88) && b[s] === 6 * by) return true;
  }
  for (const [dirs, k1, k2] of [[BISHOP_DIRS, 3, 5], [ROOK_DIRS, 4, 5]]) {
    for (const off of dirs) {
      let s = sq + off;
      while (!(s & 0x88)) {
        const p = b[s];
        if (p !== EMPTY) {
          if ((p > 0) === (by > 0) && (Math.abs(p) === k1 || Math.abs(p) === k2))
            return true;
          break;
        }
        s += off;
      }
    }
  }
  return false;
}

function king_sq(pos, side) {
  const t = 6 * side;
  for (const sq of SQUARES) if (pos.board[sq] === t) return sq;
  throw new Error('king missing');
}

function pseudo_moves(pos) {
  const b = pos.board, side = pos.side, moves = [];
  for (const fr of SQUARES) {
    const p = b[fr];
    if (p === EMPTY || (p > 0) !== (side > 0)) continue;
    const ap = Math.abs(p);
    if (ap === 1) {
      const fwd = 16 * side;
      const rank = fr >> 4;
      const promoRank = side === 1 ? 6 : 1;
      const startRank = side === 1 ? 1 : 6;
      const s = fr + fwd;
      if (!(s & 0x88) && b[s] === EMPTY) {
        if (rank === promoRank) {
          for (const pr of [5, 2, 4, 3]) moves.push(fr | (s << 7) | (pr << 14));
        } else {
          moves.push(fr | (s << 7));
          if (rank === startRank && b[s + fwd] === EMPTY)
            moves.push(fr | ((s + fwd) << 7) | (FLAG_DOUBLE << 18));
        }
      }
      for (const k of [-1, 1]) {
        const s2 = fr + fwd + k;
        if (s2 & 0x88) continue;
        const q = b[s2];
        if (q !== EMPTY && (q > 0) !== (side > 0)) {
          if (rank === promoRank) {
            for (const pr of [5, 2, 4, 3])
              moves.push(fr | (s2 << 7) | (pr << 14));
          } else moves.push(fr | (s2 << 7));
        } else if (s2 === pos.ep && q === EMPTY &&
                   rank === (side === 1 ? 4 : 3)) {
          moves.push(fr | (s2 << 7) | (FLAG_EP << 18));
        }
      }
    } else if (ap === 2 || ap === 6) {
      const offs = ap === 2 ? KNIGHT_OFFS : KING_DIRS;
      for (const off of offs) {
        const s = fr + off;
        if (s & 0x88) continue;
        const q = b[s];
        if (q === EMPTY || (q > 0) !== (side > 0)) moves.push(fr | (s << 7));
      }
    } else {
      const dirs = ap === 4 ? ROOK_DIRS : ap === 3 ? BISHOP_DIRS : KING_DIRS;
      const n = ap >= 5 ? 8 : 4;
      for (let k = 0; k < n; k++) {
        let s = fr + dirs[k];
        while (!(s & 0x88)) {
          const q = b[s];
          if (q === EMPTY) moves.push(fr | (s << 7));
          else {
            if ((q > 0) !== (side > 0)) moves.push(fr | (s << 7));
            break;
          }
          s += dirs[k];
        }
      }
    }
  }
  if (side === 1) {
    if ((pos.castling & WK_CASTLE) && b[5] === EMPTY && b[6] === EMPTY &&
        b[4] === WK && b[7] === WR &&
        !attacked(b, 4, -1) && !attacked(b, 5, -1) && !attacked(b, 6, -1))
      moves.push(4 | (6 << 7) | (FLAG_CASTLE << 18));
    if ((pos.castling & WQ_CASTLE) && b[3] === EMPTY && b[2] === EMPTY &&
        b[1] === EMPTY && b[4] === WK && b[0] === WR &&
        !attacked(b, 4, -1) && !attacked(b, 3, -1) && !attacked(b, 2, -1))
      moves.push(4 | (2 << 7) | (FLAG_CASTLE << 18));
  } else {
    if ((pos.castling & BK_CASTLE) && b[117] === EMPTY && b[118] === EMPTY &&
        b[116] === BK && b[119] === BR &&
        !attacked(b, 116, 1) && !attacked(b, 117, 1) && !attacked(b, 118, 1))
      moves.push(116 | (118 << 7) | (FLAG_CASTLE << 18));
    if ((pos.castling & BQ_CASTLE) && b[115] === EMPTY && b[114] === EMPTY &&
        b[113] === EMPTY && b[116] === BK && b[112] === BR &&
        !attacked(b, 116, 1) && !attacked(b, 115, 1) && !attacked(b, 114, 1))
      moves.push(116 | (114 << 7) | (FLAG_CASTLE << 18));
  }
  return moves;
}

function make(pos, m) {
  const b = pos.board;
  const fr = m & 127, to = (m >> 7) & 127;
  const promo = (m >> 14) & 7, flag = (m >> 18) & 3;
  const side = pos.side;
  const piece = b[fr];
  const undo = { m, captured: b[to], castling: pos.castling, ep: pos.ep };
  b[fr] = EMPTY;
  if (flag === FLAG_EP) b[to - 16 * side] = EMPTY;
  b[to] = promo ? promo * side : piece;
  if (flag === FLAG_CASTLE) {
    if (to === 6) { b[7] = EMPTY; b[5] = WR; }
    else if (to === 2) { b[0] = EMPTY; b[3] = WR; }
    else if (to === 118) { b[119] = EMPTY; b[117] = BR; }
    else { b[112] = EMPTY; b[115] = BR; }
  }
  if (piece === WK) pos.castling &= ~(WK_CASTLE | WQ_CASTLE);
  else if (piece === BK) pos.castling &= ~(BK_CASTLE | BQ_CASTLE);
  if (fr === 7 || to === 7) pos.castling &= ~WK_CASTLE;
  if (fr === 0 || to === 0) pos.castling &= ~WQ_CASTLE;
  if (fr === 119 || to === 119) pos.castling &= ~BK_CASTLE;
  if (fr === 112 || to === 112) pos.castling &= ~BQ_CASTLE;
  pos.ep = flag === FLAG_DOUBLE ? fr + 16 * side : -1;
  pos.side = -side;
  return undo;
}

function unmake(pos, undo) {
  const b = pos.board;
  const fr = undo.m & 127, to = (undo.m >> 7) & 127;
  const promo = (undo.m >> 14) & 7, flag = (undo.m >> 18) & 3;
  const side = -pos.side;
  let piece = b[to];
  if (promo) piece = side;
  b[fr] = piece;
  b[to] = undo.captured;
  if (flag === FLAG_EP) b[to - 16 * side] = -side;
  if (flag === FLAG_CASTLE) {
    if (to === 6) { b[7] = WR; b[5] = EMPTY; }
    else if (to === 2) { b[0] = WR; b[3] = EMPTY; }
    else if (to === 118) { b[119] = BR; b[117] = EMPTY; }
    else { b[112] = BR; b[115] = EMPTY; }
  }
  pos.castling = undo.castling;
  pos.ep = undo.ep;
  pos.side = side;
}

function legal_moves(pos) {
  const out = [];
  for (const m of pseudo_moves(pos)) {
    if (Math.abs(pos.board[(m >> 7) & 127]) === 6) continue;
    const u = make(pos, m);
    if (!attacked(pos.board, king_sq(pos, -pos.side), pos.side)) out.push(m);
    unmake(pos, u);
  }
  return out;
}

function uci_to_move(pos, uci) {
  const fr = name_sq(uci.slice(0, 2)), to = name_sq(uci.slice(2, 4));
  const pr = uci.length > 4 ? { q: 5, n: 2, r: 4, b: 3 }[uci[4]] || 0 : 0;
  for (const m of legal_moves(pos)) {
    if ((m & 127) === fr && ((m >> 7) & 127) === to &&
        ((m >> 14) & 7) === pr) return m;
  }
  throw new Error('illegal move ' + uci);
}

function perft(pos, d) {
  if (d === 0) return 1;
  let n = 0;
  for (const m of legal_moves(pos)) {
    const u = make(pos, m);
    n += perft(pos, d - 1);
    unmake(pos, u);
  }
  return n;
}

// ── splitmix64 (via two 32-bit halves; BigInt for exactness) ──────────
const MASK64 = (1n << 64n) - 1n;
function splitmix64(x) {
  x = (x + 0x9E3779B97F4A7C15n) & MASK64;
  let z = x;
  z = ((z ^ (z >> 30n)) * 0xBF58476D1CE4E5B9n) & MASK64;
  z = ((z ^ (z >> 27n)) * 0x94D049BB133111EBn) & MASK64;
  return (z ^ (z >> 31n)) & MASK64;
}

// ── algebra ────────────────────────────────────────────────────────────
const g = {
  id: (f, r) => [f, r],
  rot90: (f, r) => [r, 7 - f],
  rot180: (f, r) => [7 - f, 7 - r],
  rot270: (f, r) => [7 - r, f],
  mirh: (f, r) => [7 - f, r],
  mirv: (f, r) => [f, 7 - r],
  diag: (f, r) => [r, f],
  anti: (f, r) => [7 - r, 7 - f],
};
const D4 = [g.id, g.rot90, g.rot180, g.rot270, g.mirh, g.mirv, g.diag, g.anti];
const V4 = [g.id, g.rot180, g.diag, g.anti];

function gcd2(a, b) { while (b) { const t = a % b; a = b; b = t; } return a; }
function lcm2(a, b) { return a / gcd2(a, b) * b; }
function tstar(W, H, a, b) {
  let gx = gcd2(Math.abs(a), W) || W;
  let gy = gcd2(Math.abs(b), H) || H;
  return lcm2(W / gx, H / gy);
}

function attack_squares(b, sq, blocking) {
  const p = b[sq], ap = Math.abs(p), out = [];
  if (ap === 1) {
    const fwd = 16 * (p > 0 ? 1 : -1);
    for (const k of [-1, 1]) {
      const s = sq + fwd + k;
      if (!(s & 0x88)) out.push(s);
    }
  } else if (ap === 2 || ap === 6) {
    const offs = ap === 2 ? KNIGHT_OFFS : KING_DIRS;
    for (const off of offs) {
      const s = sq + off;
      if (!(s & 0x88)) out.push(s);
    }
  } else {
    const dirs = ap === 4 ? ROOK_DIRS : ap === 3 ? BISHOP_DIRS : KING_DIRS;
    const n = ap >= 5 ? 8 : 4;
    for (let k = 0; k < n; k++) {
      let s = sq + dirs[k];
      while (!(s & 0x88)) {
        out.push(s);
        if (blocking && b[s] !== EMPTY) break;
        s += dirs[k];
      }
    }
  }
  return out;
}

function equivariance_violations(board, side) {
  const theta = new Int32Array(128);
  for (const sq of SQUARES) {
    const p = board[sq];
    if (p !== EMPTY && (p > 0) === (side > 0))
      for (const s of attack_squares(board, sq, true)) theta[s]++;
  }
  let bad = 0;
  for (const G of D4) {
    const bg = new Int8Array(128);
    for (const sq of SQUARES) {
      const p = board[sq];
      if (p !== EMPTY) {
        const [f, r] = G(sq & 7, sq >> 4);
        bg[16 * r + f] = p;
      }
    }
    const tg = new Int32Array(128);
    for (const sq of SQUARES) {
      const p = bg[sq];
      if (p !== EMPTY && (p > 0) === (side > 0))
        for (const s of attack_squares(bg, sq, true)) tg[s]++;
    }
    for (const sq of SQUARES) {
      const [f, r] = G(sq & 7, sq >> 4);
      if (tg[16 * r + f] !== theta[sq]) bad++;
    }
  }
  return bad;
}

const KNIGHT_TOUR = ("f5 h4 g2 e1 c2 a1 b3 c1 a2 b4 a6 b8 d7 f8 h7 g5 h3 " +
  "g1 e2 g3 h1 f2 d1 b2 d3 f4 h5 g7 e8 f6 g8 h6 g4 h2 f1 e3 d5 c7 a8 b6 " +
  "a4 c3 b1 a3 b5 a7 c8 e7 g6 h8 f7 e5 f3 d2 c4 a5 c6 d4 e6 d8 b7 c5 " +
  "e4 d6").split(' ');

function knight_neighbour(a, b) {
  const df = Math.abs((a & 7) - (b & 7)), dr = Math.abs((a >> 4) - (b >> 4));
  return (df === 1 && dr === 2) || (df === 2 && dr === 1);
}

function mate_dfs(pos, depth) {
  if (depth <= 0) return 0;
  let best = 0;
  for (const m of legal_moves(pos)) {
    const u = make(pos, m);
    const replies = legal_moves(pos);
    if (replies.length === 0) {
      const mated = attacked(pos.board, king_sq(pos, pos.side), -pos.side);
      unmake(pos, u);
      if (mated) return 1;
      continue;
    }
    if (depth >= 2) {
      let allMated = true, worst = 0;
      for (const r of replies) {
        const u2 = make(pos, r);
        const sub = mate_dfs(pos, depth - 2);
        unmake(pos, u2);
        if (!sub) { allMated = false; break; }
        if (sub > worst) worst = sub;
      }
      if (allMated) {
        unmake(pos, u);
        const cand = worst + 2;
        if (!best || cand < best) {
          best = cand;
          if (best <= 3) return best;
        }
        continue;
      }
    }
    unmake(pos, u);
  }
  return best;
}

// ── the battery ────────────────────────────────────────────────────────
const RESULTS = [];
function check(code, ok, note) {
  RESULTS.push([code, !!ok, note]);
}

function main() {
  // 1 board algebra
  {
    const seen = Array.from({ length: 8 }, () => new Array(8).fill(false));
    let cnt = 0, small = 0, big = 0;
    for (let f = 0; f < 8; f++) for (let r = 0; r < 8; r++) {
      if (seen[f][r]) continue;
      const orb = new Set(V4.map(G => G(f, r).join(',')));
      for (const cell of orb) {
        const [a, b] = cell.split(',').map(Number);
        seen[a][b] = true;
      }
      cnt++;
      if (orb.size === 2) small++;
      else if (orb.size === 4) big++;
    }
    let dcnt = 0;
    const dseen = Array.from({ length: 8 }, () => new Array(8).fill(false));
    for (let f = 0; f < 8; f++) for (let r = 0; r < 8; r++) {
      if (dseen[f][r]) continue;
      for (const G of D4) {
        const [a, b] = G(f, r);
        dseen[a][b] = true;
      }
      dcnt++;
    }
    const bd4 = (64 + 8 + 8) / 8, bv4 = (64 + 8 + 8) / 4;
    check('C1', cnt === 20 && small === 8 && big === 12 && dcnt === 10 &&
          bd4 === 10 && bv4 === 20,
          `V4=${cnt}(${small}+${big}) D4=${dcnt} burnside ${bv4}/${bd4}`);
  }
  // 2 move-graph census
  {
    const b = new Int8Array(128);
    const types = [[WR, 'R'], [WB, 'B'], [WN, 'N'], [WK, 'K'], [WQ, 'Q']];
    const edges = {};
    for (const [t, nm] of types) {
      let total = 0;
      for (const sq of SQUARES) {
        b[sq] = t;
        total += attack_squares(b, sq, true).length;
        b[sq] = EMPTY;
      }
      edges[nm] = total / 2;
    }
    check('C2', edges.R === 448 && edges.B === 280 && edges.N === 168 &&
          edges.K === 210 && edges.Q === 728,
          `edges R${edges.R} B${edges.B} N${edges.N} K${edges.K} Q${edges.Q}`);
  }
  // 3 mobility census
  {
    const b = new Int8Array(128);
    const types = [[WR, 'R'], [WB, 'B'], [WN, 'N'], [WK, 'K'], [WQ, 'Q']];
    const sums = {}, maxima = {};
    let bishopOk = true;
    for (const [t, nm] of types) {
      let total = 0, mx = 0;
      for (const sq of SQUARES) {
        b[sq] = t;
        const n = attack_squares(b, sq, false).length;
        total += n;
        if (n > mx) mx = n;
        b[sq] = EMPTY;
      }
      sums[nm] = total;
      maxima[nm] = mx;
    }
    for (const sq of SQUARES) {
      const f = sq & 7, r = sq >> 4;
      b[sq] = WB;
      const m = attack_squares(b, sq, false).length;
      b[sq] = EMPTY;
      if (m !== 14 - Math.abs(f - r) - Math.abs(f + r - 7)) bishopOk = false;
    }
    check('C3', sums.R === 896 && sums.B === 560 && sums.N === 336 &&
          sums.K === 420 && sums.Q === 1456 && maxima.R === 14 &&
          maxima.B === 13 && maxima.N === 8 && maxima.K === 8 &&
          maxima.Q === 27 && bishopOk,
          `sums R${sums.R} B${sums.B} N${sums.N} K${sums.K} Q${sums.Q}; ` +
          `max ${maxima.R}/${maxima.B}/${maxima.N}/${maxima.K}/${maxima.Q}`);
  }
  // 4 flow termination
  {
    const cases = [[8, 8, 1, 1, 8], [8, 8, 3, 5, 8], [8, 8, 2, 2, 4],
      [8, 8, 1, 2, 8], [8, 8, 1, 0, 8], [8, 8, 2, 1, 8],
      [48, 48, 1, 1, 48], [24, 36, 3, 5, 72], [12, 12, 4, 6, 6]];
    const ok = cases.every(([W, H, a, b2, t]) => tstar(W, H, a, b2) === t);
    check('C4', ok,
      `9 t* cases: ${cases.slice(0, 5).map(c => tstar(c[0], c[1], c[2], c[3])).join(',')}`);
  }
  // 5 perft
  {
    const pos = new Pos().setFen(
      'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', 'w', 'KQkq', '-');
    const p1 = perft(pos, 1), p2 = perft(pos, 2);
    const p3 = perft(pos, 3), p4 = perft(pos, 4);
    check('C5', p1 === 20 && p2 === 400 && p3 === 8902 && p4 === 197281,
          `perft ${p1} ${p2} ${p3} ${p4}`);
  }
  // 6 threat fields
  {
    const pl = new Int8Array(128);
    const back = [WR, WN, WB, WQ, WK, WB, WN, WR];
    for (let f = 0; f < 8; f++) { pl[f] = back[f]; pl[112 + f] = -back[f]; }
    const vw = equivariance_violations(pl, 1);
    const vb = equivariance_violations(pl, -1);
    const st = new Int8Array(128);
    for (let f = 0; f < 8; f++) {
      st[f] = back[f];
      st[112 + f] = -back[f];
      st[16 + f] = WP;
      st[96 + f] = BP;
    }
    const anomaly = equivariance_violations(st, 1) +
                    equivariance_violations(st, -1);
    check('C6', vw === 0 && vb === 0 && anomaly === 176,
          `pawnless violations ${vw}/${vb}, pawn anomaly ${anomaly}`);
  }
  // 7 kinetic energy
  {
    const pos = new Pos().setFen(
      'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', 'w', 'KQkq', '-');
    const m0 = legal_moves(pos).length;
    const u = make(pos, uci_to_move(pos, 'e2e4'));
    pos.side = 1;
    const m1 = legal_moves(pos).length;
    pos.side = -1;
    unmake(pos, u);
    check('C7', m0 === 20 && m1 === 30,
          `White mobility ${m0} -> ${m1} after 1.e4`);
  }
  // 8 mate certificates
  {
    function keyMatesIn2(pos, frSq, toSq) {
      for (const m of legal_moves(pos)) {
        if ((m & 127) === frSq && ((m >> 7) & 127) === toSq) {
          const u = make(pos, m);
          let okAll = true;
          for (const r of legal_moves(pos)) {
            const u2 = make(pos, r);
            const sub = mate_dfs(pos, 1);
            unmake(pos, u2);
            if (sub !== 1) { okAll = false; break; }
          }
          unmake(pos, u);
          return okAll;
        }
      }
      return false;
    }
    const morphy = new Pos().setFen('kbK5/pp6/1P6/8/8/8/8/R7', 'w', '-', '-');
    const keyOk = keyMatesIn2(morphy, name_sq('a1'), name_sq('a6'));
    const pliesM = mate_dfs(morphy, 4);
    const ladder = new Pos().setFen('7k/8/8/8/8/8/R7/1R4K1', 'w', '-', '-');
    const pliesL = mate_dfs(ladder, 4);
    const nr = new Pos().setFen('7k/8/5N1K/8/8/8/8/6R1', 'w', '-', '-');
    const pliesN = mate_dfs(nr, 2);
    let nrKey = false;
    for (const m of legal_moves(nr)) {
      if ((m & 127) === name_sq('g1') && ((m >> 7) & 127) === name_sq('g8')) {
        const u = make(nr, m);
        const replies = legal_moves(nr);
        nrKey = replies.length === 0 &&
                attacked(nr.board, king_sq(nr, nr.side), -nr.side);
        unmake(nr, u);
        break;
      }
    }
    check('C8', pliesM === 3 && keyOk && pliesL === 3 && pliesN === 1 &&
          nrKey,
          `morphy ${pliesM}(key a1a6) ladder ${pliesL} nr ${pliesN}(key g1g8)`);
  }
  // 9 zobrist incrementality (fixed playout)
  {
    const zob = {};
    let state = 1n;
    for (const piece of [WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK]) {
      const arr = new Array(128);
      for (let sq = 0; sq < 128; sq++) arr[sq] = splitmix64(state++);
      zob[piece] = arr;
    }
    const sideKey = splitmix64(state);
    function fullHash(b, side) {
      let h = 0n;
      for (const sq of SQUARES)
        if (b[sq] !== EMPTY) h ^= zob[b[sq]][sq];
      if (side === -1) h ^= sideKey;
      return h;
    }
    const playout = ['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5', 'g8f6',
                    'e1g1', 'f8c5', 'd2d3', 'd7d6'];
    const pos = new Pos().setFen(
      'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', 'w', 'KQkq', '-');
    let h = fullHash(pos.board, pos.side);
    let incOk = true;
    for (const u_ of playout) {
      const m = uci_to_move(pos, u_);
      const fr = m & 127, to = (m >> 7) & 127;
      const promo = (m >> 14) & 7, flag = (m >> 18) & 3;
      const piece = pos.board[fr], captured = pos.board[to];
      h ^= zob[piece][fr];
      if (captured !== EMPTY) h ^= zob[captured][to];
      if (promo) h ^= zob[promo * pos.side][to] ^ zob[piece][to];
      else h ^= zob[piece][to];
      if (flag === FLAG_EP) {
        const cap = to - 16 * pos.side;
        h ^= zob[pos.board[cap]][cap];
      }
      if (flag === FLAG_CASTLE) {
        if (to === 6) h ^= zob[WR][7] ^ zob[WR][5];
        else if (to === 2) h ^= zob[WR][0] ^ zob[WR][3];
        else if (to === 118) h ^= zob[BR][119] ^ zob[BR][117];
        else h ^= zob[BR][112] ^ zob[BR][115];
      }
      make(pos, m);
      h ^= sideKey;
      if (h !== fullHash(pos.board, pos.side)) { incOk = false; break; }
    }
    const smOk = splitmix64(1n) === 0x910A2DEC89025CC1n &&
                 splitmix64(2n) === 0x975835DE1C9756CEn &&
                 splitmix64(3n) === 0x1D0B14E4DB018FEDn;
    check('C9', incOk && smOk,
          `incremental hash over ${playout.length} plies, ` +
          `splitmix vectors ${smOk ? 'ok' : 'BAD'}`);
  }
  // 10 knight tour
  {
    const tour = KNIGHT_TOUR.map(name_sq);
    const distinct = new Set(tour).size === 64;
    let closed = true;
    for (let i = 0; i < 64; i++)
      if (!knight_neighbour(tour[i], tour[(i + 1) % 64])) { closed = false; break; }
    check('C10', distinct && closed,
          `tour 64 distinct cells, closure ${closed ? 'ok' : 'BAD'}`);
  }
  // report
  let passed = 0;
  for (const [code, ok, note] of RESULTS) {
    if (ok) passed++;
    console.log(`[${ok ? 'PASS' : 'FAIL'}] ${code}  ${note}`);
  }
  console.log(`verdict: ${passed}/${RESULTS.length}`);
  return passed === RESULTS.length ? 0 : 1;
}

process.exit(main());
