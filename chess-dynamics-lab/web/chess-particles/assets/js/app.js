/* ════════════════════════════════════════════════════════════════════
   Chess Particle Dynamics — a certifiable web laboratory
   app.js — fully self-contained, no build tools, no dependencies.

   Contents
     1. 0x88 chess engine (full legal movegen: castling, en passant,
        promotion, pins/checks; checkmate / stalemate)
     2. Board algebra D4 / V4, orbit census, Burnside
     3. t* flow termination + damped billiard (γ = π⁴/256)
     4. splitmix64 on BigInt + exact inverse
     5. Threat fields (Θ(c)) + Lagrangian energy E = [M_w−M_b] + μ[m_w−m_b]
     6. Protocol C1–C10 — honest, computed in your browser
     7. Theory cards T01–T12 (frozen facts, RU/EN)
     8. i18n (RU default / EN, localStorage)
     9. Canvas particle renderer + UI wiring

   window.CDL exposes the pure core (used by console and by node tests).
   ════════════════════════════════════════════════════════════════════ */
(function () {
'use strict';

/* ═══════════════════════ 1. ENGINE (0x88) ═══════════════════════════ */
var EMPTY = 0, PAWN = 1, KNIGHT = 2, BISHOP = 3, ROOK = 4, QUEEN = 5, KING = 6;
var WHITE = 1, BLACK = -1;
var KNIGHT_OFFS = [33, 31, 18, 14, -33, -31, -18, -14];
var KING_DIRS   = [16, -16, 1, -1, 17, 15, -17, -15];
var BISHOP_DIRS = [17, 15, -17, -15];
var ROOK_DIRS   = [16, -16, 1, -1];
var PIECE_LETTER  = ['', 'P', 'N', 'B', 'R', 'Q', 'K'];
var PIECE_GLYPH_W = ['', '\u2659', '\u2658', '\u2657', '\u2656', '\u2655', '\u2654'];
var PIECE_GLYPH_B = ['', '\u265F', '\u265E', '\u265D', '\u265C', '\u265B', '\u265A'];
var PIECE_VALUE   = [0, 1, 3, 3, 5, 9, 0];           // material units (king 0)
var FLAG_EP = 1, FLAG_CASTLE = 2, FLAG_DOUBLE = 3;
var CASTLE_WK = 1, CASTLE_WQ = 2, CASTLE_BK = 4, CASTLE_BQ = 8;

var SQUARES = (function () {
  var a = [];
  for (var sq = 0; sq < 128; sq++) { if (sq & 0x88) { sq += 7; continue; } a.push(sq); }
  return a;
})();

/* n×n sub-boards live inside the same 0x88 lattice: a square is on the
   live board iff it is valid 0x88 AND inside the n×n corner.  The
   protocol C1–C10 keeps its own 8×8 constants (SQUARES); every
   live-engine path derives its bounds from pos.n (T14 generalized
   boards, complexity module link). */
function onSq(s, n) {
  return !(s & 0x88) && (s & 7) < n && (s >> 4) < n;
}
var _sqCache = {};
function squaresOf(n) {
  if (n === 8) return SQUARES;
  if (!_sqCache[n]) {
    var a = [];
    for (var r = 0; r < n; r++) for (var f = 0; f < n; f++) a.push(16 * r + f);
    _sqCache[n] = a;
  }
  return _sqCache[n];
}

/* castling-rights masks: rights &= MASK[from] & MASK[to] */
var CASTLE_MASK = new Uint8Array(128);
for (var i = 0; i < 128; i++) CASTLE_MASK[i] = 15;
CASTLE_MASK[0x00] = 15 & ~CASTLE_WQ;   // a1 rook
CASTLE_MASK[0x04] = 15 & ~(CASTLE_WK | CASTLE_WQ); // e1 king
CASTLE_MASK[0x07] = 15 & ~CASTLE_WK;   // h1 rook
CASTLE_MASK[0x70] = 15 & ~CASTLE_BQ;   // a8 rook
CASTLE_MASK[0x74] = 15 & ~(CASTLE_BK | CASTLE_BQ); // e8 king
CASTLE_MASK[0x77] = 15 & ~CASTLE_BK;   // h8 rook

var START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
var MORPHY_FEN = 'kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1';
var PAWNLESS_FEN = 'rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w - - 0 1';

/* generalized presets: scaled-down copies of the complexity module's
   KRK demo ('8/8/8/4k3/8/8/8/R3K3 w'), verified LEGAL and WON with the
   exact retrograde oracle retro_dtm_nxn (scripts/verify_nxn_presets.py):
     4×4: won in 9 plies · 5×5: 13 plies · 6×6: 17 plies */
var PRESETS = {};
PRESETS[8] = START_FEN;
PRESETS[6] = '6/6/3k2/6/6/R2K2 w - - 0 1';
PRESETS[5] = '5/5/2k2/5/R2K1 w - - 0 1';
PRESETS[4] = '4/2k1/4/R2K w - - 0 1';
var SIZES = [8, 6, 5, 4];

function sqName(sq) { return 'abcdefgh'.charAt(sq & 7) + (1 + (sq >> 4)); }
function nameSq(s) { return ('abcdefgh'.indexOf(s.charAt(0))) + (parseInt(s.charAt(1), 10) - 1) * 16; }
function mv(from, to, promo, flag) { return from | (to << 7) | ((promo || 0) << 14) | ((flag || 0) << 18); }
function mvFrom(m) { return m & 127; }
function mvTo(m) { return (m >> 7) & 127; }
function mvPromo(m) { return (m >> 14) & 7; }
function mvFlag(m) { return (m >> 18) & 3; }
function moveUci(m) {
  var s = sqName(mvFrom(m)) + sqName(mvTo(m));
  var p = mvPromo(m);
  if (p) s += 'nbrq'.charAt(p - 1);
  return s;
}

function createPos(n) {
  return { board: new Int8Array(128), side: 1, castling: 15, ep: -1,
           kings: [-1, -1], halfmove: 0, fullmove: 1, n: n || 8 };
}

function setFen(pos, fen) {
  pos.board = new Int8Array(128);
  pos.kings = [-1, -1];
  var parts = fen.trim().split(/\s+/);
  var ranks = parts[0].split('/');
  var N = Math.max(1, Math.min(8, ranks.length));   // size follows FEN
  pos.n = N;
  for (var ri = 0; ri < N; ri++) {
    var rank = N - 1 - ri, file = 0, row = ranks[ri];
    for (var ci = 0; ci < row.length; ci++) {
      var ch = row.charAt(ci);
      if (ch >= '1' && ch <= '8') { file += ch.charCodeAt(0) - 48; continue; }
      var up = ch.toUpperCase(), code = ' PNBRQK'.indexOf(up);
      if (code <= 0) continue;
      var p = code * (ch === up ? 1 : -1);
      var sq = rank * 16 + file;
      pos.board[sq] = p;
      if (p === KING) pos.kings[0] = sq;
      if (p === -KING) pos.kings[1] = sq;
      file++;
    }
  }
  pos.side = (parts[1] === 'b') ? -1 : 1;
  pos.castling = 0;
  if (parts[2] && parts[2] !== '-') {
    if (parts[2].indexOf('K') >= 0) pos.castling |= CASTLE_WK;
    if (parts[2].indexOf('Q') >= 0) pos.castling |= CASTLE_WQ;
    if (parts[2].indexOf('k') >= 0) pos.castling |= CASTLE_BK;
    if (parts[2].indexOf('q') >= 0) pos.castling |= CASTLE_BQ;
  }
  pos.ep = (parts[3] && parts[3] !== '-') ? nameSq(parts[3]) : -1;
  pos.halfmove = parts[4] ? parseInt(parts[4], 10) || 0 : 0;
  pos.fullmove = parts[5] ? parseInt(parts[5], 10) || 1 : 1;
  return pos;
}

function toFen(pos) {
  var N = pos.n || 8;
  var rows = [];
  for (var ri = N - 1; ri >= 0; ri--) {
    var row = '', gap = 0;
    for (var f = 0; f < N; f++) {
      var p = pos.board[ri * 16 + f];
      if (!p) { gap++; continue; }
      if (gap) { row += gap; gap = 0; }
      var l = PIECE_LETTER[p > 0 ? p : -p];
      row += p > 0 ? l : l.toLowerCase();
    }
    if (gap) row += gap;
    rows.push(row);
  }
  var cast = (pos.castling & CASTLE_WK ? 'K' : '') + (pos.castling & CASTLE_WQ ? 'Q' : '') +
             (pos.castling & CASTLE_BK ? 'k' : '') + (pos.castling & CASTLE_BQ ? 'q' : '');
  if (!cast) cast = '-';
  return rows.join('/') + ' ' + (pos.side === 1 ? 'w' : 'b') + ' ' + cast + ' ' +
         (pos.ep >= 0 ? sqName(pos.ep) : '-') + ' ' + pos.halfmove + ' ' + pos.fullmove;
}

/* is square `sq` attacked by side `by`? (bounds: n×n board) */
function attacked(board, sq, by, n) {
  n = n || 8;
  var s, o, p, k;
  if (by === 1) {
    s = sq - 15; if (onSq(s, n) && board[s] === PAWN) return true;
    s = sq - 17; if (onSq(s, n) && board[s] === PAWN) return true;
  } else {
    s = sq + 15; if (onSq(s, n) && board[s] === -PAWN) return true;
    s = sq + 17; if (onSq(s, n) && board[s] === -PAWN) return true;
  }
  for (k = 0; k < 8; k++) {
    s = sq + KNIGHT_OFFS[k];
    if (onSq(s, n) && board[s] === by * KNIGHT) return true;
  }
  for (k = 0; k < 8; k++) {
    s = sq + KING_DIRS[k];
    if (onSq(s, n) && board[s] === by * KING) return true;
  }
  for (k = 0; k < 4; k++) {
    o = ROOK_DIRS[k]; s = sq + o;
    while (onSq(s, n)) {
      p = board[s];
      if (p) { if (p === by * ROOK || p === by * QUEEN) return true; break; }
      s += o;
    }
  }
  for (k = 0; k < 4; k++) {
    o = BISHOP_DIRS[k]; s = sq + o;
    while (onSq(s, n)) {
      p = board[s];
      if (p) { if (p === by * BISHOP || p === by * QUEEN) return true; break; }
      s += o;
    }
  }
  return false;
}

function genCastles(pos, sq, out) {
  var b = pos.board, side = pos.side;
  if (pos.n !== 8) return;             // castling exists on the 8×8 board only
  if (side === 1 && sq === 0x04) {
    if ((pos.castling & CASTLE_WK) && !b[0x05] && !b[0x06] &&
        !attacked(b, 0x04, -1) && !attacked(b, 0x05, -1))
      out.push(mv(0x04, 0x06, 0, FLAG_CASTLE));
    if ((pos.castling & CASTLE_WQ) && !b[0x03] && !b[0x02] && !b[0x01] &&
        !attacked(b, 0x04, -1) && !attacked(b, 0x03, -1))
      out.push(mv(0x04, 0x02, 0, FLAG_CASTLE));
  } else if (side === -1 && sq === 0x74) {
    if ((pos.castling & CASTLE_BK) && !b[0x75] && !b[0x76] &&
        !attacked(b, 0x74, 1) && !attacked(b, 0x75, 1))
      out.push(mv(0x74, 0x76, 0, FLAG_CASTLE));
    if ((pos.castling & CASTLE_BQ) && !b[0x73] && !b[0x72] && !b[0x71] &&
        !attacked(b, 0x74, 1) && !attacked(b, 0x73, 1))
      out.push(mv(0x74, 0x72, 0, FLAG_CASTLE));
  }
}

/* pseudo-legal move generation (king captures never generated);
   all bounds are the n×n corner of the 0x88 lattice (pos.n) */
function genMoves(pos) {
  var b = pos.board, side = pos.side, out = [];
  var N = pos.n || 8;
  for (var sq = 0; sq < 128; sq++) {
    if (sq & 0x88) { sq += 7; continue; }
    if ((sq & 7) >= N || (sq >> 4) >= N) continue;   // outside the n×n board
    var p = b[sq];
    if (!p || (p > 0) !== (side > 0)) continue;
    var ap = p > 0 ? p : -p;
    if (ap === PAWN) {
      var fwd = 16 * side, rank = sq >> 4;
      var promoRank = side === 1 ? N - 2 : 1;
      var startRank = side === 1 ? 1 : N - 2;
      var one = sq + fwd;
      if (!(one & 0x88) && (one & 7) < N && !b[one]) {
        if (rank === promoRank) {
          out.push(mv(sq, one, QUEEN, 0)); out.push(mv(sq, one, ROOK, 0));
          out.push(mv(sq, one, BISHOP, 0)); out.push(mv(sq, one, KNIGHT, 0));
        } else {
          out.push(mv(sq, one, 0, 0));
          /* double push only while the landing square stays strictly
             before the promotion rank (n ≥ 6; on 4×4/5×5 every pawn is
             already adjacent to its promotion horizon) */
          if (rank === startRank && N > 5) {
            var two = sq + 2 * fwd;
            if (!b[two]) out.push(mv(sq, two, 0, FLAG_DOUBLE));
          }
        }
      }
      for (var dc = -1; dc <= 1; dc += 2) {
        var to = sq + fwd + dc;
        if (to & 0x88) continue;
        if ((to & 7) >= N || (to >> 4) >= N) continue;
        var t = b[to];
        if (t && (t > 0) !== (side > 0) && t !== KING && t !== -KING) {
          if (rank === promoRank) {
            out.push(mv(sq, to, QUEEN, 0)); out.push(mv(sq, to, ROOK, 0));
            out.push(mv(sq, to, BISHOP, 0)); out.push(mv(sq, to, KNIGHT, 0));
          } else out.push(mv(sq, to, 0, 0));
        } else if (!t && to === pos.ep &&
                   rank === (side === 1 ? N - 4 : 3)) {
          /* ep capture: the capturing pawn always stands on the passer's
             landing rank (guards against artificial side flips) */
          out.push(mv(sq, to, 0, FLAG_EP));
        }
      }
    } else if (ap === KNIGHT || ap === KING) {
      var offs = ap === KNIGHT ? KNIGHT_OFFS : KING_DIRS;
      for (var k = 0; k < 8; k++) {
        var s2 = sq + offs[k];
        if (!onSq(s2, N)) continue;
        var t2 = b[s2];
        if (!t2) out.push(mv(sq, s2, 0, 0));
        else if ((t2 > 0) !== (side > 0) && t2 !== KING && t2 !== -KING) out.push(mv(sq, s2, 0, 0));
      }
      if (ap === KING) genCastles(pos, sq, out);
    } else {
      var dirs = ap === ROOK ? ROOK_DIRS : (ap === BISHOP ? BISHOP_DIRS : KING_DIRS);
      var nd = ap === QUEEN ? 8 : 4;
      for (var d = 0; d < nd; d++) {
        var o = dirs[d], ts = sq + o;
        while (onSq(ts, N)) {
          var tp = b[ts];
          if (!tp) out.push(mv(sq, ts, 0, 0));
          else {
            if ((tp > 0) !== (side > 0) && tp !== KING && tp !== -KING) out.push(mv(sq, ts, 0, 0));
            break;
          }
          ts += o;
        }
      }
    }
  }
  return out;
}

function make(pos, m) {
  var b = pos.board;
  var from = mvFrom(m), to = mvTo(m), promo = mvPromo(m), flag = mvFlag(m);
  var piece = b[from], side = pos.side;
  var undo = { m: m, captured: b[to], castling: pos.castling, ep: pos.ep,
               kw: pos.kings[0], kb: pos.kings[1], halfmove: pos.halfmove };
  b[to] = promo ? promo * side : piece;
  b[from] = EMPTY;
  pos.ep = -1;
  if (flag === FLAG_DOUBLE) pos.ep = from + 16 * side;
  else if (flag === FLAG_EP) {
    var cap = to - 16 * side;
    undo.captured = b[cap];
    b[cap] = EMPTY;
  } else if (flag === FLAG_CASTLE) {
    if (to === 0x06) { b[0x05] = b[0x07]; b[0x07] = EMPTY; }
    else if (to === 0x02) { b[0x03] = b[0x00]; b[0x00] = EMPTY; }
    else if (to === 0x76) { b[0x75] = b[0x77]; b[0x77] = EMPTY; }
    else { b[0x73] = b[0x70]; b[0x70] = EMPTY; }
  }
  if (piece === KING) pos.kings[0] = to;
  else if (piece === -KING) pos.kings[1] = to;
  pos.castling &= CASTLE_MASK[from] & CASTLE_MASK[to];
  pos.side = -side;
  return undo;
}

function unmake(pos, undo) {
  var m = undo.m, b = pos.board;
  var from = mvFrom(m), to = mvTo(m), promo = mvPromo(m), flag = mvFlag(m);
  pos.side = -pos.side;
  var side = pos.side;
  var piece = promo ? PAWN * side : b[to];
  b[from] = piece;
  if (flag === FLAG_EP) {
    b[to] = EMPTY;
    b[to - 16 * side] = -side * PAWN;
  } else {
    b[to] = undo.captured;
  }
  if (flag === FLAG_CASTLE) {
    if (to === 0x06) { b[0x07] = b[0x05]; b[0x05] = EMPTY; }
    else if (to === 0x02) { b[0x00] = b[0x03]; b[0x03] = EMPTY; }
    else if (to === 0x76) { b[0x77] = b[0x75]; b[0x75] = EMPTY; }
    else { b[0x70] = b[0x73]; b[0x73] = EMPTY; }
  }
  if (piece === KING) pos.kings[0] = from;
  else if (piece === -KING) pos.kings[1] = from;
  pos.castling = undo.castling;
  pos.ep = undo.ep;
  pos.halfmove = undo.halfmove;
}

function inCheck(pos, side) {
  var s = (side === undefined) ? pos.side : side;
  return attacked(pos.board, s === 1 ? pos.kings[0] : pos.kings[1], -s,
                  pos.n || 8);
}

function legalMoves(pos) {
  var out = [], pseudo = genMoves(pos), side = pos.side, ki = side === 1 ? 0 : 1;
  for (var i = 0; i < pseudo.length; i++) {
    var u = make(pos, pseudo[i]);
    if (!attacked(pos.board, pos.kings[ki], -side, pos.n || 8)) out.push(pseudo[i]);
    unmake(pos, u);
  }
  return out;
}

function perft(pos, depth) {
  if (depth === 0) return 1;
  var moves = legalMoves(pos), n = 0;
  if (depth === 1) return moves.length;
  for (var i = 0; i < moves.length; i++) {
    var u = make(pos, moves[i]);
    n += perft(pos, depth - 1);
    unmake(pos, u);
  }
  return n;
}

/* 0 no game over; 1 checkmate; 2 stalemate */
function gameStatus(pos) {
  var moves = legalMoves(pos);
  if (moves.length === 0) return inCheck(pos) ? 1 : 2;
  return 0;
}

function findMove(pos, fromName, toName, promoLetter) {
  var from = nameSq(fromName), to = nameSq(toName), moves = legalMoves(pos);
  for (var i = 0; i < moves.length; i++) {
    var m = moves[i];
    if (mvFrom(m) === from && mvTo(m) === to) {
      if (promoLetter) {
        if (mvPromo(m) === promoCode(promoLetter)) return m;
      } else return m;
    }
  }
  return 0;
}

/* uci -> move for the CURRENT position (e.g. 'e2e4', 'a7a8q') */
function uciToMove(pos, uci) {
  return findMove(pos, uci.slice(0, 2), uci.slice(2, 4), uci.length > 4 ? uci.charAt(4) : '');
}
/* promo letter -> piece code: n=2 b=3 r=4 q=5 */
function promoCode(ch) { return 'nbrq'.indexOf(ch) + 2; }

/* ═════════════ 2. BOARD ALGEBRA: D4 / V4 (Theorem T01) ══════════════ */
function G_id(f, r) { return [f, r]; }
function G_rot90(f, r) { return [r, 7 - f]; }
function G_rot180(f, r) { return [7 - f, 7 - r]; }
function G_rot270(f, r) { return [7 - r, f]; }
function G_mirh(f, r) { return [7 - f, r]; }
function G_mirv(f, r) { return [f, 7 - r]; }
function G_diag(f, r) { return [r, f]; }
function G_anti(f, r) { return [7 - r, 7 - f]; }
var D4 = [G_id, G_rot90, G_rot180, G_rot270, G_mirh, G_mirv, G_diag, G_anti];
var V4 = [G_id, G_rot180, G_diag, G_anti];

function orbitCensus(G) {
  var seen = {}, orbs = [], small = 0, big = 0;
  for (var f = 0; f < 8; f++) for (var r = 0; r < 8; r++) {
    if (seen[f + ',' + r]) continue;
    var orb = [];
    for (var k = 0; k < G.length; k++) {
      var gr = G[k](f, r);
      if (orb.indexOf(gr[0] + ',' + gr[1]) < 0) orb.push(gr[0] + ',' + gr[1]);
    }
    for (var j = 0; j < orb.length; j++) seen[orb[j]] = true;
    orbs.push(orb);
    if (orb.length === 2) small++; else if (orb.length === 4) big++;
  }
  return { count: orbs.length, small: small, big: big, orbits: orbs };
}
function burnside(G, fixes) {
  var total = 0;
  for (var k = 0; k < G.length; k++) total += fixes(k, G[k]);
  return total / G.length;
}

/* ═══════ 3. t* FLOW TERMINATION + DAMPED BILLIARD (Theorem T06) ═════ */
function gcd2(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { var t = a % b; a = b; b = t; } return a; }
function lcm2(a, b) { return a / gcd2(a, b) * b; }
function tstar(W, H, a, b) {
  var gx = gcd2(a, W) || W, gy = gcd2(b, H) || H;
  return lcm2(W / gx, H / gy);
}
function simulateTstar(W, H, a, b) {
  var x = 0, y = 0, steps = 0;
  do {
    x = ((x + a) % W + W) % W;
    y = ((y + b) % H + H) % H;
    steps++;
    if (steps > 1000000) return -1;
  } while (x !== 0 || y !== 0);
  return steps;
}
var GAMMA_TORUS = Math.PI * Math.PI * Math.PI * Math.PI / 256;   // π⁴/256 ≈ 0.3805042619

/* Layer-K3 damped billiard (mirror reflections, braking γ per step).
   Returns {steps, path, reflections, atRest, ratio}; ratio → 1.0 */
function simulateBilliard(W, H, a, b, gamma, eps, maxSteps) {
  eps = eps || 1e-12; maxSteps = maxSteps || 200000;
  var x = 0.5, y = 0.5, vx = a, vy = b;
  var v0 = Math.sqrt(vx * vx + vy * vy);
  var path = 0, reflections = 0, points = [{ x: x, y: y }];
  if (v0 === 0) return { steps: 0, path: 0, reflections: 0, atRest: true, ratio: 1, points: points };
  var exact = v0 / (1 - gamma);
  for (var step = 1; step <= maxSteps; step++) {
    var speed = Math.sqrt(vx * vx + vy * vy);
    if (speed < eps) return { steps: step - 1, path: path, reflections: reflections, atRest: true,
                              ratio: path / exact, points: points, exact: exact };
    var nx = x + vx, nvx = vx, ny = y + vy, nvy = vy;
    while (nx < 0 || nx > W) { nx = nx < 0 ? -nx : 2 * W - nx; nvx = -nvx; reflections++; }
    while (ny < 0 || ny > H) { ny = ny < 0 ? -ny : 2 * H - ny; nvy = -nvy; reflections++; }
    x = nx; y = ny; vx = nvx; vy = nvy;
    path += speed;
    points.push({ x: x, y: y });
    vx *= gamma; vy *= gamma;
  }
  return { steps: maxSteps, path: path, reflections: reflections, atRest: false,
           ratio: path / exact, points: points, exact: exact };
}

/* ═══════════ 4. SPLITMIX64 ON BIGINT + EXACT INVERSE (T09) ══════════ */
var MASK64 = (typeof BigInt !== 'undefined') ? (1n << 64n) - 1n : 0;
var GOLDEN = 0x9E3779B97F4A7C15n;
var SM_A = 0xBF58476D1CE4E5B9n;
var SM_B = 0x94D049BB133111EBn;
function modInv64(a) {          // a odd → Newton iteration mod 2^64
  var x = a;
  for (var i = 0; i < 6; i++) x = (x * (2n - a * x)) & MASK64;
  return x;
}
var SM_A_INV = (typeof BigInt !== 'undefined') ? modInv64(SM_A) : 0n;
var SM_B_INV = (typeof BigInt !== 'undefined') ? modInv64(SM_B) : 0n;

function splitmix64(x) {
  x = (x + GOLDEN) & MASK64;
  var z = x;
  z = ((z ^ (z >> 30n)) * SM_A) & MASK64;
  z = ((z ^ (z >> 27n)) * SM_B) & MASK64;
  return (z ^ (z >> 31n)) & MASK64;
}
function splitmix64Inverse(y) {
  var z = y;
  z ^= z >> 31n; z ^= z >> 62n;          // undo z ^= z >> 31
  z = (z * SM_B_INV) & MASK64;           // undo z *= SM_B
  z ^= z >> 27n; z ^= z >> 54n;          // undo z ^= z >> 27
  z = (z * SM_A_INV) & MASK64;           // undo z *= SM_A
  z ^= z >> 30n; z ^= z >> 60n;          // undo z ^= z >> 30
  return (z - GOLDEN) & MASK64;
}
function hex64(x) {
  var h = x.toString(16).toUpperCase();
  while (h.length < 16) h = '0' + h;
  return '0x' + h;
}

/* seeded PRNG (mulberry32) — deterministic auto flow */
function mulberry32(seed) {
  var t = seed >>> 0;
  return function () {
    t += 0x6D2B79F5;
    var r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

/* ═══ 5. THREAT FIELDS (T04) + LAGRANGIAN ENERGY (T05) ═══════════════ */
/* squares attacked by the piece on sq; sliders stop at first occupied;
   bounds = the n×n corner (n defaults to 8 for the protocol's own uses) */
function pieceAttackSquares(board, sq, blocking, n) {
  n = n || 8;
  if (blocking === undefined) blocking = true;
  var p = board[sq], ap = p > 0 ? p : -p, out = [], s, k, o;
  if (ap === PAWN) {
    var fwd = 16 * (p > 0 ? 1 : -1);
    s = sq + fwd - 1; if (onSq(s, n)) out.push(s);
    s = sq + fwd + 1; if (onSq(s, n)) out.push(s);
  } else if (ap === KNIGHT) {
    for (k = 0; k < 8; k++) { s = sq + KNIGHT_OFFS[k]; if (onSq(s, n)) out.push(s); }
  } else if (ap === KING) {
    for (k = 0; k < 8; k++) { s = sq + KING_DIRS[k]; if (onSq(s, n)) out.push(s); }
  } else {
    var dirs = ap === ROOK ? ROOK_DIRS : (ap === BISHOP ? BISHOP_DIRS : KING_DIRS);
    var nd = ap === QUEEN ? 8 : 4;
    for (k = 0; k < nd; k++) {
      o = dirs[k]; s = sq + o;
      while (onSq(s, n)) {
        out.push(s);
        if (blocking && board[s] !== EMPTY) break;
        s += o;
      }
    }
  }
  return out;
}

function threatField(pos, side) {
  var N = pos.n || 8, SQ = squaresOf(N);
  var theta = new Int32Array(128), k;
  for (var i = 0; i < SQ.length; i++) {
    var sq = SQ[i], p = pos.board[sq];
    if (p !== EMPTY && (p > 0) === (side > 0)) {
      var at = pieceAttackSquares(pos.board, sq, undefined, N);
      for (k = 0; k < at.length; k++) theta[at[k]]++;
    }
  }
  return theta;
}
function attackSum(pos, side) {           // Σ_c Θ(c) — the field mass
  var N = pos.n || 8, SQ = squaresOf(N);
  var th = threatField(pos, side), total = 0;
  for (var i = 0; i < SQ.length; i++) total += th[SQ[i]];
  return total;
}

/* attack pairs (f, t) for the Θ-flow animation: every attacker→target
   incidence behind the field (sliders with blocking, exactly the pairs
   that threatField counts) */
function attackPairs(pos, side) {
  var N = pos.n || 8, SQ = squaresOf(N);
  var out = [], k;
  for (var i = 0; i < SQ.length; i++) {
    var sq = SQ[i], p = pos.board[sq];
    if (p !== EMPTY && (p > 0) === (side > 0)) {
      var at = pieceAttackSquares(pos.board, sq, undefined, N);
      for (k = 0; k < at.length; k++) out.push({ f: sq, t: at[k] });
    }
  }
  return out;
}

/* Θ(g·p, g·c) must equal Θ(p, c): count violations over the group
   (protocol-only: the 8×8 square set, independent of the live board) */
function equivarianceViolations(pos, side, group) {
  group = group || D4;
  var theta = threatField({ board: pos.board, side: side, n: 8 }, side), bad = 0;
  for (var g = 0; g < group.length; g++) {
    var G = group[g];
    var bg = new Int8Array(128);
    for (var i = 0; i < SQUARES.length; i++) {
      var sq = SQUARES[i], p = pos.board[sq];
      if (p !== EMPTY) {
        var gr = G(sq & 7, sq >> 4);
        bg[16 * gr[1] + gr[0]] = p;
      }
    }
    var tg = threatField({ board: bg, side: side, n: 8 }, side);
    for (var j = 0; j < SQUARES.length; j++) {
      var s2 = SQUARES[j], g2 = G(s2 & 7, s2 >> 4);
      if (tg[16 * g2[1] + g2[0]] !== theta[s2]) bad++;
    }
  }
  return bad;
}

function material(pos, side) {
  var N = pos.n || 8, SQ = squaresOf(N);
  var total = 0;
  for (var i = 0; i < SQ.length; i++) {
    var sq = SQ[i], p = pos.board[sq];
    if (p !== EMPTY && (p > 0) === (side > 0)) total += PIECE_VALUE[p > 0 ? p : -p];
  }
  return total;
}
function mobility(pos, side) {            // legal moves of `side` regardless of turn
  var saved = pos.side;
  pos.side = side;
  var n = legalMoves(pos).length;
  pos.side = saved;
  return n;
}
var MU = 0.1;
function energy(pos) {                    // White's viewpoint, E = [M_w−M_b] + μ[m_w−m_b]
  var mw = mobility(pos, WHITE), mb = mobility(pos, BLACK);
  return { E: (material(pos, WHITE) - material(pos, BLACK)) + MU * (mw - mb),
           Mw: material(pos, WHITE), Mb: material(pos, BLACK), mw: mw, mb: mb };
}

/* ═══ 5b. GENERALIZED KRK SPACE (complexity-module link, T14) ════════ */
/* Exact (states, edges) of the K+R vs K space on an n×n board — the
   same enumeration the frozen E2 experiment (complexity_scaling.json,
   experiment_scaling.py) ran in Python; the JS recount below must match
   it digit-for-digit (the protocol-style check lives in the cx card).
   Semantics (bit-faithful to generalized_chess.retro_dtm_nxn):
     - king neighbourhoods are the 8×8 0x88 ones: for n < 8 a white king
       on the rim keeps its off-sub-board 0x88 moves in the successor
       list (they pack into the 22-bit state and stay valueless/drawn);
     - only the BLACK king destinations are restricted to the n×n board;
     - a WTM state is legal iff the Black king is not attacked (rays of
       the 0x88 scan, white king may block);
     - a capture of the rook is a flagged escape, not an edge. */
function krkSpace(n) {
  var SQ = squaresOf(n), valid = {}, i, j, k;
  for (i = 0; i < SQ.length; i++) valid[SQ[i]] = true;
  var KN = {};                            // 8×8 king neighbourhoods
  for (i = 0; i < SQUARES.length; i++) {
    var s = SQUARES[i], list = [];
    for (k = 0; k < 8; k++) {
      var t = s + KING_DIRS[k];
      if (!(t & 0x88)) list.push(t);
    }
    KN[s] = list;
  }
  var states = 0, edges = 0;
  var board = new Int8Array(128), board2 = new Int8Array(128);
  for (var wi = 0; wi < SQ.length; wi++) {
    var wk = SQ[wi];
    for (var pi = 0; pi < SQ.length; pi++) {
      var wp = SQ[pi];
      if (wp === wk) continue;
      for (var bi = 0; bi < SQ.length; bi++) {
        var bk = SQ[bi];
        if (bk === wk || bk === wp) continue;
        var df = Math.abs((wk & 7) - (bk & 7)),
            dr = Math.abs((wk >> 4) - (bk >> 4));
        if (df <= 1 && dr <= 1) continue;           // adjacent kings
        // ── Black to move: always a state ──────────────────────────
        states++;
        for (var b1 = 0; b1 < KN[bk].length; b1++) {
          var dest = KN[bk][b1];
          if (!valid[dest]) continue;               // black stays on n×n
          if (dest === wk || KN[wk].indexOf(dest) >= 0) continue;
          if (dest === wp) continue;                // capture = escape
          board2[wk] = KING; board2[wp] = ROOK; board2[dest] = -KING;
          var hit = pieceAttackSquares(board2, wp, true).indexOf(dest) >= 0;
          board2[wk] = 0; board2[wp] = 0; board2[dest] = 0;
          if (hit) continue;                        // into a slider check
          edges++;
        }
        // ── White to move: legal iff Black king not attacked ───────
        board[wk] = KING; board[wp] = ROOK; board[bk] = -KING;
        var targets = pieceAttackSquares(board, wp, true);
        if (targets.indexOf(bk) < 0) {
          states++;
          for (var w1 = 0; w1 < KN[wk].length; w1++) {
            var d1 = KN[wk][w1];
            if (d1 === wp || d1 === bk || KN[bk].indexOf(d1) >= 0) continue;
            edges++;
          }
          for (var w2 = 0; w2 < targets.length; w2++) {
            var d2 = targets[w2];
            if (d2 === wk || d2 === bk) continue;
            edges++;
          }
        }
        board[wk] = 0; board[wp] = 0; board[bk] = 0;
      }
    }
  }
  return { states: states, edges: edges };
}

/* frozen E2 rows (results/complexity_scaling.json): the live recount
   must reproduce states and edges exactly; won/maxMoves are retrograde
   facts of the frozen experiment and are shown as such */
var FROZEN_E2 = {
  4: { states: 3496,   edges: 26992,   won: 2884,   maxMoves: 7 },
  5: { states: 17528,  edges: 161265,  won: 15324,  maxMoves: 10 },
  6: { states: 60800,  edges: 620224,  won: 55148,  maxMoves: 12 },
  7: { states: 168260, edges: 1837205, won: 156320, maxMoves: 14 },
  8: { states: 399112, edges: 4447032, won: 376868, maxMoves: 16 }
};

/* ═══════════════ 6. PROTOCOL C1–C10 (computed, honest) ══════════════ */
/* small DFS mate search: returns plies of the fastest mate, 0 if none */
function mateDfs(pos, depth) {
  if (depth <= 0) return 0;
  var best = 0;
  var moves = legalMoves(pos);
  for (var i = 0; i < moves.length; i++) {
    var u = make(pos, moves[i]);
    var replies = legalMoves(pos);
    if (replies.length === 0) {
      var mated = attacked(pos.board, pos.side === 1 ? pos.kings[0] : pos.kings[1], -pos.side,
                           pos.n || 8);
      unmake(pos, u);
      if (mated) return 1;
      continue;
    }
    if (depth >= 2) {
      var allMated = true, worst = 0;
      for (var r = 0; r < replies.length; r++) {
        var u2 = make(pos, replies[r]);
        var sub = mateDfs(pos, depth - 2);
        unmake(pos, u2);
        if (!sub) { allMated = false; break; }
        if (sub > worst) worst = sub;
      }
      if (allMated) {
        unmake(pos, u);
        var cand = worst + 2;
        if (!best || cand < best) { best = cand; if (best <= 3) return best; }
        continue;
      }
    }
    unmake(pos, u);
  }
  return best;
}

/* closed knight tour, Warnsdorff from f5 with the deterministic
   final-step tie-break «prefer d6» (the documented closure square) */
var KNIGHT_NB = (function () {
  var nb = {};
  for (var i = 0; i < SQUARES.length; i++) {
    var sq = SQUARES[i], list = [];
    for (var k = 0; k < 8; k++) {
      var s = sq + KNIGHT_OFFS[k];
      if (!(s & 0x88)) list.push(s);
    }
    nb[sq] = list;
  }
  return nb;
})();
function knightNeighbour(a, b) {
  var df = Math.abs((a & 7) - (b & 7)), dr = Math.abs((a >> 4) - (b >> 4));
  return (df === 1 && dr === 2) || (df === 2 && dr === 1);
}
function warnsdorffTour(startName) {
  var start = nameSq(startName);
  var used = {}, tour = [start];
  used[start] = true;
  var deadEnd = false;
  while (tour.length < 64) {
    var cur = tour[tour.length - 1], cands = [];
    var nb = KNIGHT_NB[cur];
    for (var i = 0; i < nb.length; i++) if (!used[nb[i]]) cands.push(nb[i]);
    if (!cands.length) { deadEnd = true; break; }
    var pick;
    if (tour.length === 63) {
      /* final step: prefer a square adjacent to the start (closure) */
      var closing = cands.filter(function (n) { return knightNeighbour(n, start); });
      var pool = closing.length ? closing : cands;
      pick = pool.indexOf(nameSq('d6')) >= 0 ? nameSq('d6')
           : pool.slice().sort(function (a, b) {
               var da = 0, db = 0;
               for (var x = 0; x < KNIGHT_NB[a].length; x++) if (!used[KNIGHT_NB[a][x]]) da++;
               for (var y = 0; y < KNIGHT_NB[b].length; y++) if (!used[KNIGHT_NB[b][y]]) db++;
               return da - db || a - b;
             })[0];
    } else {
      pick = cands.slice().sort(function (a, b) {
        var da = 0, db = 0;
        for (var x = 0; x < KNIGHT_NB[a].length; x++) if (!used[KNIGHT_NB[a][x]]) da++;
        for (var y = 0; y < KNIGHT_NB[b].length; y++) if (!used[KNIGHT_NB[b][y]]) db++;
        return da - db || a - b;
      })[0];
    }
    tour.push(pick);
    used[pick] = true;
  }
  return { tour: deadEnd ? null : tour, deadEnd: deadEnd };
}
function verifyTour(tour) {
  if (!tour || tour.length !== 64) return { ok: false, why: 'length' };
  var seen = {};
  for (var i = 0; i < 64; i++) {
    if (seen[tour[i]]) return { ok: false, why: 'duplicate' };
    seen[tour[i]] = true;
  }
  if (Object.keys(seen).length !== 64) return { ok: false, why: 'distinct' };
  for (var j = 0; j < 64; j++)
    if (!knightNeighbour(tour[j], tour[(j + 1) % 64])) return { ok: false, why: 'knight step ' + j };
  return { ok: true, closed: knightNeighbour(tour[63], tour[0]),
           closure: sqName(tour[63]) + '\u2192' + sqName(tour[0]) };
}

function runProtocol(deep) {
  var rows = [];
  function row(code, descKey, expected, computed, pass, ms) {
    rows.push({ code: code, descKey: descKey, expected: expected,
                computed: computed, pass: !!pass, ms: ms });
  }

  /* C1 — board algebra: V4 / D4 orbit census + Burnside */
  var t0 = performanceNow();
  var v4 = orbitCensus(V4), d4 = orbitCensus(D4);
  var bV4 = burnside(V4, function (k, G) {
    var n = 0;
    for (var f = 0; f < 8; f++) for (var r = 0; r < 8; r++) {
      var g2 = G(f, r); if (g2[0] === f && g2[1] === r) n++;
    }
    return n;
  });
  var bD4 = burnside(D4, function (k, G) {
    var n = 0;
    for (var f = 0; f < 8; f++) for (var r = 0; r < 8; r++) {
      var g3 = G(f, r); if (g3[0] === f && g3[1] === r) n++;
    }
    return n;
  });
  row('C1', 'proto.c1.desc',
      'V4 20 (8\u00D72+12\u00D74) \u00B7 D4 10 (Burnside)',
      'V4=' + v4.count + ' (' + v4.small + '\u00D72+' + v4.big + '\u00D74) \u00B7 D4=' + d4.count +
      ' \u00B7 Burnside ' + bV4 + '/' + bD4,
      v4.count === 20 && v4.small === 8 && v4.big === 12 &&
      d4.count === 10 && bV4 === 20 && bD4 === 10,
      performanceNow() - t0);

  /* C2 — move-graph edge census on the empty board */
  t0 = performanceNow();
  var b = new Int8Array(128);
  var types = [[ROOK, 'R'], [BISHOP, 'B'], [KNIGHT, 'N'], [KING, 'K'], [QUEEN, 'Q']];
  var edges = {}, edgesOk = true;
  for (var ti = 0; ti < types.length; ti++) {
    var tt = types[ti][0], total = 0;
    for (var i2 = 0; i2 < SQUARES.length; i2++) {
      b[SQUARES[i2]] = tt;
      total += pieceAttackSquares(b, SQUARES[i2], true).length;
      b[SQUARES[i2]] = EMPTY;
    }
    edges[types[ti][1]] = total / 2;
  }
  edgesOk = edges.R === 448 && edges.B === 280 && edges.N === 168 &&
            edges.K === 210 && edges.Q === 728;
  row('C2', 'proto.c2.desc',
      'R448 / B280 / N168 / K210 / Q728',
      'R' + edges.R + ' / B' + edges.B + ' / N' + edges.N + ' / K' + edges.K + ' / Q' + edges.Q,
      edgesOk, performanceNow() - t0);

  /* C3 — mobility census: sums and maxima */
  t0 = performanceNow();
  var sums = {}, maxima = {};
  for (var ti3 = 0; ti3 < types.length; ti3++) {
    var t3 = types[ti3][0], sum = 0, mx = 0;
    for (var i3 = 0; i3 < SQUARES.length; i3++) {
      b[SQUARES[i3]] = t3;
      var n3 = pieceAttackSquares(b, SQUARES[i3], false).length;
      sum += n3; if (n3 > mx) mx = n3;
      b[SQUARES[i3]] = EMPTY;
    }
    sums[types[ti3][1]] = sum; maxima[types[ti3][1]] = mx;
  }
  row('C3', 'proto.c3.desc',
      '\u03A3 K420/N336/B560/R896/Q1456 \u00B7 max 8/8/13/14/27',
      '\u03A3 K' + sums.K + '/N' + sums.N + '/B' + sums.B + '/R' + sums.R + '/Q' + sums.Q +
      ' \u00B7 max ' + maxima.K + '/' + maxima.N + '/' + maxima.B + '/' + maxima.R + '/' + maxima.Q,
      sums.K === 420 && sums.N === 336 && sums.B === 560 && sums.R === 896 && sums.Q === 1456 &&
      maxima.K === 8 && maxima.N === 8 && maxima.B === 13 && maxima.R === 14 && maxima.Q === 27,
      performanceNow() - t0);

  /* C4 — t* formula vs simulation over a grid of (W,H,a,b) */
  t0 = performanceNow();
  var cases = 0, tOk = true;
  var Ws = [5, 7, 8, 12, 48], Hs = [6, 8, 13, 36];
  for (var wi = 0; wi < Ws.length; wi++) for (var hi = 0; hi < Hs.length; hi++)
    for (var a4 = -2; a4 <= 3; a4++) for (var b4 = -1; b4 <= 4; b4++) {
      if (a4 === 0 && b4 === 0) continue;
      cases++;
      if (tstar(Ws[wi], Hs[hi], a4, b4) !== simulateTstar(Ws[wi], Hs[hi], a4, b4)) tOk = false;
    }
  var bill = simulateBilliard(8, 8, 3, 2, GAMMA_TORUS);
  var c4ok = tOk && bill.atRest && Math.abs(bill.ratio - 1) < 1e-9;
  row('C4', 'proto.c4.desc',
      't* = lcm(W/gcd(a,W), H/gcd(b,H)) \u2014 all cases \u00B7 path ratio \u2192 1',
      cases + ' cases: formula = simulation \u00B7 \u03B3-path ratio ' + bill.ratio.toFixed(6) +
      ' (\u03B3 = \u03C0\u2074/256)',
      c4ok, performanceNow() - t0);

  /* C5 — perft identities from the initial position */
  t0 = performanceNow();
  var pos5 = setFen(createPos(), START_FEN);
  var p1 = perft(pos5, 1), p2 = perft(pos5, 2), p3 = perft(pos5, 3);
  var p4 = null;
  if (deep) p4 = perft(pos5, 4);
  var c5exp = '20 / 400 / 8902' + (deep ? ' / 197281' : '');
  var c5comp = p1 + ' / ' + p2 + ' / ' + p3 + (deep ? ' / ' + p4 : ' (+197281 deep)');
  row('C5', 'proto.c5.desc', c5exp, c5comp,
      p1 === 20 && p2 === 400 && p3 === 8902 && (!deep || p4 === 197281),
      performanceNow() - t0);

  /* C6 — threat fields: mass, equivariance, pawn anomaly */
  t0 = performanceNow();
  var start = setFen(createPos(), START_FEN);
  var massW = attackSum(start, WHITE), massB = attackSum(start, BLACK);
  var pawnless = setFen(createPos(), PAWNLESS_FEN);
  var vW = equivarianceViolations(pawnless, WHITE);
  var vB = equivarianceViolations(pawnless, BLACK);
  var anomaly = equivarianceViolations(start, WHITE) + equivarianceViolations(start, BLACK);
  row('C6', 'proto.c6.desc',
      'mass 38/38 \u00B7 equivariance 0/0 \u00B7 pawn anomaly 176 = 88+88',
      'mass ' + massW + '/' + massB + ' \u00B7 violations (pawnless, D4 incl. 180\u00B0) ' +
      vW + '/' + vB + ' \u00B7 anomaly ' + anomaly,
      massW === 38 && massB === 38 && vW === 0 && vB === 0 && anomaly === 176,
      performanceNow() - t0);

  /* C7 — Lagrangian energy: E0 = 0, after 1.e4 kinetic +1.0 */
  t0 = performanceNow();
  var pos7 = setFen(createPos(), START_FEN);
  var e0 = energy(pos7);
  var m7 = findMove(pos7, 'e2', 'e4');
  var u7 = make(pos7, m7);
  var e1 = energy(pos7);
  unmake(pos7, u7);
  var c7ok = e0.mw === 20 && e0.mb === 20 && e1.mw === 30 && e1.mb === 20 &&
             Math.abs(e0.E) < 1e-12 && Math.abs(e1.E - 1.0) < 1e-12;
  row('C7', 'proto.c7.desc',
      'mobility 20 \u2192 30 after 1.e4 \u00B7 E0 = 0 \u00B7 E = +1.0 (\u03BC = 0.1)',
      'm(White) ' + e0.mw + ' \u2192 ' + e1.mw + ' \u00B7 E0 = ' + e0.E.toFixed(1) +
      ' \u00B7 E(after 1.e4) = ' + (e1.E >= 0 ? '+' : '') + e1.E.toFixed(1),
      c7ok, performanceNow() - t0);

  /* C8 — mate certificates: Morphy miniature */
  t0 = performanceNow();
  var morphy = setFen(createPos(), MORPHY_FEN);
  var plies = mateDfs(morphy, 4);
  var keyOk = false;
  var keyM = findMove(morphy, 'a1', 'a6');
  if (keyM) {
    var u8 = make(morphy, keyM);
    keyOk = true;
    var reps = legalMoves(morphy);
    if (!reps.length) keyOk = false;
    for (var r8 = 0; r8 < reps.length && keyOk; r8++) {
      var uu = make(morphy, reps[r8]);
      var sub8 = mateDfs(morphy, 1);
      unmake(morphy, uu);
      if (sub8 !== 1) keyOk = false;
    }
    unmake(morphy, u8);
  }
  /* PV by deterministic extraction: fastest mating line */
  var pv = extractPV(setFen(createPos(), MORPHY_FEN), 4);
  var pvStr = pv.join(' ');
  var pvOk = pvStr === 'a1a6 b7a6 b6b7';
  row('C8', 'proto.c8.desc',
      'mate in 3 plies \u00B7 key a1a6 \u00B7 PV a1a6 b7a6 b6b7',
      plies + ' plies \u00B7 key a1a6 ' + (keyOk ? '\u2713' : '\u2717') + ' \u00B7 PV ' + pvStr,
      plies === 3 && keyOk && pvOk, performanceNow() - t0);

  /* C9 — splitmix64 vectors + exact inverse round-trip 1..2000 */
  t0 = performanceNow();
  var sm1 = splitmix64(1n), sm2 = splitmix64(2n), sm3 = splitmix64(3n);
  var smOk = sm1 === 0x910A2DEC89025CC1n && sm2 === 0x975835DE1C9756CEn &&
             sm3 === 0x1D0B14E4DB018FEDn;
  var invOk = 0, N9 = 2000;
  for (var x9 = 1n; x9 <= BigInt(N9); x9++)
    if (splitmix64Inverse(splitmix64(x9)) === x9) invOk++;
  row('C9', 'proto.c9.desc',
      'sm(1)=0x910A2DEC89025CC1 \u00B7 sm(2)=0x975835DE1C9756CE \u00B7 sm(3)=0x1D0B14E4DB018FED \u00B7 inverse 2000/2000',
      smOk ? 'vectors \u2713 ' : 'vectors \u2717 ' + hex64(sm1) + ' \u00B7 inverse ' + invOk + '/' + N9,
      smOk && invOk === N9, performanceNow() - t0);

  /* C10 — knight tour: Warnsdorff from f5, final-step preference d6 */
  t0 = performanceNow();
  var res10 = warnsdorffTour('f5');
  var ver10 = verifyTour(res10.tour);
  row('C10', 'proto.c10.desc',
      'closed tour from f5 \u00B7 64 moves \u00B7 closure d6\u2192f5',
      res10.deadEnd ? 'greedy dead end \u2014 no tour'
        : (ver10.ok ? 'Warnsdorff: 64 unique \u00B7 ' +
           (ver10.closed ? 'closed (' + ver10.closure + ')' : 'open') +
           ' \u00B7 64 knight steps' : 'invalid: ' + ver10.why),
      ver10.ok && ver10.closed && ver10.closure === 'd6\u2192f5',
      performanceNow() - t0);

  return rows;
}

/* fastest mating line (deterministic: first mate in generation order) */
function extractPV(pos, plies) {
  var line = [], ok = pvRecurse(pos, plies, line);
  return ok ? line : [];
}
function pvRecurse(pos, plies, line) {
  if (plies <= 0) return false;
  var moves = legalMoves(pos);
  for (var i = 0; i < moves.length; i++) {
    var u = make(pos, moves[i]);
    var replies = legalMoves(pos);
    if (replies.length === 0) {
      var mated = attacked(pos.board, pos.side === 1 ? pos.kings[0] : pos.kings[1], -pos.side,
                           pos.n || 8);
      if (mated) {
        unmake(pos, u);
        line.push(moveUci(moves[i]));
        return true;
      }
      unmake(pos, u);
      continue;
    }
    if (plies >= 2) {
      /* opponent survives only if some reply avoids mate */
      var refuted = false;
      for (var r = 0; r < replies.length; r++) {
        var u2 = make(pos, replies[r]);
        var sub = mateDfs(pos, plies - 2);
        unmake(pos, u2);
        if (!sub) { refuted = true; break; }
      }
      if (!refuted) {
        /* choose the first legal reply, then continue the line */
        var subLine = [];
        var u3 = make(pos, replies[0]);
        var done = pvRecurse(pos, plies - 2, subLine);
        unmake(pos, u3);
        unmake(pos, u);
        if (done) {
          line.push(moveUci(moves[i]));
          line.push(moveUci(replies[0]));
          for (var s9 = 0; s9 < subLine.length; s9++) line.push(subLine[s9]);
          return true;
        }
      }
    }
    unmake(pos, u);
  }
  return false;
}

function performanceNow() {
  return (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
}

/* ═══════════════ 7. THEORY T01–T12 (frozen facts, RU/EN) ════════════ */
var THEORIES = [
  { id: 'T01',
    ru: { title: 'Орбиты доски', text: 'Группа V4 разбивает 64 клетки на 20 орбит (8 диагональных размера 2 и 12 внесистемных размера 4), полная группа D4 — на 10 орбит; оба числа дают формулы Бернсайда.',
          formula: 'V4: (64+0+8+8)/4 = 20 · D4: (64+8+8)/8 = 10' },
    en: { title: 'Board orbits', text: 'The V4 group splits the 64 squares into 20 orbits (8 diagonal size-2 and 12 off-diagonal size-4), the full D4 group into 10; both counts follow from Burnside\'s lemma.',
          formula: 'V4: (64+0+8+8)/4 = 20 · D4: (64+8+8)/8 = 10' } },
  { id: 'T02',
    ru: { title: 'Кинематика частиц', text: 'Граф ходов пустой доски имеет ровно 448 рок-ребер, 280 слоновьих, 168 коневых, 210 королевских и 728 ферзевых.',
          formula: 'E = ½·Σ deg(c): R448 / B280 / N168 / K210 / Q728' },
    en: { title: 'Particle kinematics', text: 'The empty-board move graph has exactly 448 rook edges, 280 bishop, 168 knight, 210 king and 728 queen edges.',
          formula: 'E = ½·Σ deg(c): R448 / B280 / N168 / K210 / Q728' } },
  { id: 'T03',
    ru: { title: 'Кензус мобильности', text: 'Суммы степеней по всем клеткам равны K420/N336/B560/R896/Q1456, а максимумы в центре — 8/8/13/14/27.',
          formula: 'Σ K420 · N336 · B560 · R896 · Q1456; max 8/8/13/14/27' },
    en: { title: 'Mobility census', text: 'The mobility sums over all squares are K420/N336/B560/R896/Q1456 with central maxima 8/8/13/14/27.',
          formula: 'Σ K420 · N336 · B560 · R896 · Q1456; max 8/8/13/14/27' } },
  { id: 'T04',
    ru: { title: 'Поля угроз', text: 'Тождество атаки связывает массу поля с суммой атак частиц; в начальной позиции каждая сторона несёт массу 38, а ориентированность пешек даёт конечную аномалию 176 = 88+88.',
          formula: 'Σ_c Θ(c) = Σ_π |A(π)| = 38 · anomaly 88+88 = 176' },
    en: { title: 'Threat fields', text: 'The attack identity ties the field mass to the sum of particle attack counts; in the initial position each side carries mass 38, and pawn orientation yields the finite anomaly 176 = 88+88.',
          formula: 'Σ_c Θ(c) = Σ_π |A(π)| = 38 · anomaly 88+88 = 176' } },
  { id: 'T05',
    ru: { title: 'Лагранжиан энергии', text: 'Энергия потока разделяется на материальную и кинетическую части с весом μ = 0.1; после 1.e4 белый фланг получает ровно +1.0 кинетической энергии.',
          formula: 'E = [M(w)−M(b)] + μ·[m(w)−m(b)], μ = 0.1; after 1.e4: ΔE = +1.0' },
    en: { title: 'Lagrangian energy', text: 'The flow energy splits into a material and a kinetic term with weight μ = 0.1; after 1.e4 White gains exactly +1.0 of kinetic energy.',
          formula: 'E = [M(w)−M(b)] + μ·[m(w)−m(b)], μ = 0.1; after 1.e4: ΔE = +1.0' } },
  { id: 'T06',
    ru: { title: 'Завершимость потока', text: 'Модульный поток на сетке W×H замыкается за точное время t*, а зеркальный бильярд с торможением γ = π⁴/256 проходит до остановки конечный путь |v₀|/(1−γ).',
          formula: 't* = lcm(W/gcd(a,W), H/gcd(b,H)) · γ = π⁴/256 · path |v₀|/(1−γ)' },
    en: { title: 'Flow termination', text: 'The modular flow on a W×H grid closes at the exact time t*, while the mirror billiard with braking γ = π⁴/256 travels the finite path |v₀|/(1−γ) before rest.',
          formula: 't* = lcm(W/gcd(a,W), H/gcd(b,H)) · γ = π⁴/256 · path |v₀|/(1−γ)' } },
  { id: 'T07',
    ru: { title: 'Конь-первооткрыватель', text: 'Правило Варнсдорфа строит из f5 замкнутый обход доски: 64 хода, замыкание d6→f5 — маршрут частицы-коня через всю решётку.',
          formula: 'Warnsdorff(f5) → 64 moves · closure d6→f5' },
    en: { title: 'The knight discoverer', text: 'The Warnsdorff rule builds a closed board tour from f5: 64 moves with closure d6→f5 — a knight-particle route across the whole lattice.',
          formula: 'Warnsdorff(f5) → 64 moves · closure d6→f5' } },
  { id: 'T08',
    ru: { title: 'Идентичности perft', text: 'Дерево легальных ходов из начальной позиции нарастает строго как 20/400/8902/197281/4865609 — эталон корректности любого движка.',
          formula: 'perft(1..5) = 20 / 400 / 8902 / 197281 / 4865609' },
    en: { title: 'Perft identities', text: 'The legal-move tree from the initial position grows strictly as 20/400/8902/197281/4865609 — the correctness reference for any engine.',
          formula: 'perft(1..5) = 20 / 400 / 8902 / 197281 / 4865609' } },
  { id: 'T09',
    ru: { title: 'Инкрементальность Цобриста', text: '1562 ключа Цобриста порождаются splitmix64 с фиксированным зерном; биективность конструкции доказывается точной инверсией.',
          formula: 'seed 0x1234567890ABCDEF · sm(1)=0x910A2DEC89025CC1 · golden 0x9E3779B97F4A7C15' },
    en: { title: 'Zobrist incrementality', text: '1562 Zobrist keys are generated by splitmix64 from a fixed seed; bijectivity of the construction is proven by the exact inverse.',
          formula: 'seed 0x1234567890ABCDEF · sm(1)=0x910A2DEC89025CC1 · golden 0x9E3779B97F4A7C15' } },
  { id: 'T10',
    ru: { title: 'Альфа-бета границы', text: 'Отсечение альфа-бета сокращает перебор с 421/9323/206604/5072213 узлов полного дерева до 79/731/3345/19753 — экспоненциальный выигрыш при том же ответе.',
          formula: '79/731/3345/19753 vs 421/9323/206604/5072213 nodes' },
    en: { title: 'Alpha-beta bounds', text: 'Alpha-beta pruning shrinks the search from 421/9323/206604/5072213 full-tree nodes to 79/731/3345/19753 — an exponential saving with the identical answer.',
          formula: '79/731/3345/19753 vs 421/9323/206604/5072213 nodes' } },
  { id: 'T11',
    ru: { title: 'Сертификаты мата', text: 'Ретроградный анализ даёт KRK: 399112 состояний и максимум 32 полухода, KQK: 368452 состояния и 20 полуходов, ноль нарушений Беллмана; миниатюра Морфи матуется ключом a1a6.',
          formula: 'KRK 399112/4447032/216/32 plies · KQK 368452/4869496/364/20 · PV a1a6 b7a6 b6b7' },
    en: { title: 'Mate certificates', text: 'Retrograde analysis gives KRK: 399112 states, max 32 plies; KQK: 368452 states, 20 plies; zero Bellman violations; the Morphy miniature is mated by the key a1a6.',
          formula: 'KRK 399112/4447032/216/32 plies · KQK 368452/4869496/364/20 · PV a1a6 b7a6 b6b7' } },
  { id: 'T12',
    ru: { title: 'Пространство состояний и протокол', text: 'Протокол C1–C9 замыкает все теоремы в воспроизводимый конвейер с вердиктом ALL CHECKS PASSED; полиглот-батарея C1–C10 повторяет его на 7 языках с вердиктом 10/10.',
          formula: 'C1–C9 ↔ T01–T12 · ALL CHECKS PASSED · polyglot 10/10' },
    en: { title: 'State space and protocol', text: 'The C1–C9 protocol closes all theorems into a reproducible pipeline with the verdict ALL CHECKS PASSED; the polyglot battery C1–C10 repeats it in 7 languages with the verdict 10/10.',
          formula: 'C1–C9 ↔ T01–T12 · ALL CHECKS PASSED · polyglot 10/10' } }
];

/* ═══════════════════════ 8. I18N (RU / EN) ══════════════════════════ */
var DICT = {
  ru: {
    'app.title': 'Chess Particle Dynamics',
    'brand.sub': 'Сертифицируемая шахматная лаборатория · частицы на 8×8',
    'nav.flow': 'Живой поток', 'nav.theory': 'Теоремы', 'nav.protocol': 'Протокол C',
    'nav.about': 'О программе', 'nav.aria': 'Разделы приложения',
    'tip.menu': 'Показать/скрыть разделы', 'tip.lang': 'Язык / Language',

    'flow.title': 'Живой поток частиц на шахматной доске',
    'flow.lede': 'Фигуры — светящиеся частицы (золото — белые, фиолет — чёрные). Включите авто-поток с сеяным ПСЧ-генератором или ходите вручную: кликните фигуру, затем подсвеченную клетку.',
    'flow.state': 'Позиция (частицы)',
    'flow.state.kicker': '0x88 · полная легальность',
    'lbl.size': 'Размер доски',
    'size.hint': 'T14: обобщённые доски n×n из complexity-модуля; пресет — K+Л против K, выигран (проверено ретроградным оракулом)',
    'cx.title': 'Пространство состояний KRK на n×n',
    'cx.kicker': 'живое перечисление против замороженного E2',
    'cx.desc': 'Число состояний K+Л против K растёт как O(n⁶) — полином по n при фиксированном числе фигур (T14): экспоненциальная стена обобщённых шахмат живёт в числе фигур k, а не в размере доски. Таблица пересчитывается в вашем браузере тем же перечислением, что и замороженный эксперимент E2 (complexity_scaling.json); для n<8 в рёбрах остаётся вырожденный хвост королевских выходов за пределы субдоски (упаковка 0x88) — они входят и в замороженные числа. Ретроградный DTM на n×n воспроизводит замороженные 8×8-таблицы бит-в-бит (E2: mismatches = 0).',
    'cx.states': 'состояний',
    'cx.edges': 'рёбер',
    'cx.won': 'выиграно',
    'cx.maxdtm': 'макс. DTM (ходов)',
    'cx.current': 'Текущая доска: {n}×{n}',
    'flow.legend.white': 'Частица белых', 'flow.legend.black': 'Частица чёрных',
    'flow.legend.field': 'Поле угроз Θ(c): золото → бирюза',
    'flow.legend.fieldAnim': 'Поток Θ(c): кванты поля, золото — белые, бирюза — чёрные',
    'flow.legend.last': 'Последний ход', 'flow.legend.check': 'Шах королю',
    'flow.legend.target': 'Доступные ходы',
    'board.aria': 'Шахматная доска n×n: светящиеся частицы фигур, поле угроз, подсветка ходов / Chessboard n×n: glowing piece particles, threat field, move highlights',

    'controls.title': 'Управление',
    'btn.play': '▶ Авто-поток', 'btn.pause': '⏸ Пауза', 'btn.step': '⏭ Ход',
    'btn.reset': '↺ Сброс', 'btn.copy': 'Копировать',
    'lbl.speed': 'Скорость, полуходов/с', 'lbl.seed': 'Зерно ПСЧ',
    'lbl.field': 'Поле угроз Θ(c)', 'lbl.glyphs': 'Классические глифы ♟',
    'field.hint': 'Тепловая карта: число атакующих частиц на клетке',
    'lbl.fieldAnim': 'Анимация потока Θ(c)',
    'field.animHint': 'Кванты поля текут от атакующей частицы к атакуемой клетке; цвет — сторона атакующего. Границы позиций перетекают плавно (кроссфейд).',
    'glyphs.hint': 'Поверх частиц рисуются юникод-фигуры',
    'mode.chip.auto': 'авто-поток', 'mode.chip.manual': 'ручной режим',

    'energy.title': 'Энергия Лагранжиана',
    'energy.kicker': 'μ = 0.1',
    'energy.E': 'E = [M_w − M_b] + μ·[m_w − m_b]',
    'energy.material': 'Материал M (баланс)',
    'energy.mobility': 'Мобильность m (легальные ходы)',
    'energy.row.material': 'M_w / M_b', 'energy.row.mobility': 'm_w / m_b',
    'energy.row.ply': 'Полуходов', 'energy.row.side': 'Ход белых / Ход чёрных',
    'energy.row.E': 'E (взгляд белых)',
    'side.w': 'белых', 'side.b': 'чёрных',
    'status.play': 'игра', 'status.check': 'шах!', 'status.checkmate': 'мат',
    'status.stalemate': 'пат', 'status.auto': 'авто', 'status.mated': 'мат поставлен',
    'fen.label': 'FEN позиции',

    'flow.moves': 'Лента ходов',
    'flow.empty': '— пусто: включите авто-поток или сделайте ход —',
    'flow.copied': 'Скопировано в буфер',
    'flow.gameover.mate': 'Мат. Победитель:',
    'flow.gameover.stale': 'Пат — ничья.',
    'flow.gameover.reset': 'Нажмите «Сброс» для новой партии.',

    'tstar.title': 't* — бильярд с демпфированием',
    'tstar.kicker': 'γ = π⁴/256',
    'tstar.desc': 'Частица на геометрии доски N×N: зеркальные отражения со торможением γ на каждом шаге; полный путь до остановки |v₀|/(1−γ). Скорости ограничены ±(N−1).',
    'tstar.lbl.a': 'Скорость a', 'tstar.lbl.b': 'Скорость b',
    'tstar.t': 'Точное время t* = lcm(W/gcd(a,W), H/gcd(b,H))',
    'tstar.path': 'Формула пути |v₀|/(1−γ)',
    'tstar.sim': 'Симуляция пути (K3)',
    'tstar.refl': 'Отражений',
    'tstar.aria': 'Демпфированный бильярд на сетке 8×8 / Damped billiard on the 8×8 grid',
    'tstar.err': 'Шаг (0,0) вырожден — задайте ненулевую скорость.',

    'theory.title': 'Двенадцать теорем',
    'theory.lede': 'Замороженные факты лаборатории: T01–T12 связывают алгебру доски, кинематику частиц и протокол верификации. Каждая теорема выпущена отдельной монографией (RU/EN × PDF/DOCX).',
    'theory.note': 'Значения в формулах — точные замороженные константы проекта; часть из них пересчитывается вживую в разделе «Протокол C».',

    'proto.title': 'Протокол C — батарея честных проверок',
    'proto.lede': 'C1–C10 вычисляются в вашем браузере над собственным движком этой страницы. Значения не подставлены: FAIL возможен и отображается честно.',
    'proto.run': '⟳ Запустить все', 'proto.deep': '⏱ Глубоко (perft 4)',
    'proto.deep.hint': 'Добавляет perft(4) = 197281 — занимает секунды',
    'proto.col.code': 'Код', 'proto.col.check': 'Проверка',
    'proto.col.expected': 'Ожидается', 'proto.col.computed': 'Вычислено',
    'proto.col.result': 'Итог', 'proto.col.ms': 'мс',
    'proto.note': 'Все проверки выполняются синхронно; «Глубоко» добавляет perft(4). Результаты зависят только от кода страницы — детерминированы.',
    'proto.verdict': 'вердикт:',

    'proto.c1.desc': 'Алгебра доски: орбиты V4 и D4 + формулы Бернсайда',
    'proto.c2.desc': 'Кинематика: перепись рёбер графа ходов пустой доски',
    'proto.c3.desc': 'Перепись мобильности: суммы и центральные максимумы',
    'proto.c4.desc': 'Завершимость: t* — формула против симуляции (сетка W,H,a,b) + путь бильярда',
    'proto.c5.desc': 'Идентичности perft из начальной позиции (свой движок)',
    'proto.c6.desc': 'Поля угроз: масса 38, D4-эквивариантность без пешек, пешечная аномалия',
    'proto.c7.desc': 'Энергия: мобильность 20 → 30 после 1.e4, E0 = 0, E = +1.0',
    'proto.c8.desc': 'Мат: DFS-поиск мата на миниатюре Морфи (ключ a1a6, PV)',
    'proto.c9.desc': 'splitmix64 (BigInt): векторы и точная инверсия 1..2000',
    'proto.c10.desc': 'Обход коня: Варнсдорф из f5, финальный шаг с предпочтением d6',

    'about.title': 'О программе',
    'about.p1': '«Chess Particle Dynamics» — веб-лаборатория проекта chess-dynamics-lab: шахматные фигуры рассматриваются как светящиеся частицы на решётке 8×8, а вся теория — орбиты, переписи, поля угроз, энергия, завершимость потока — верифицируется протоколом C1–C10 прямо в браузере.',
    'about.p2': 'Программа является развитием методологии hodge-laboratory: три слоя динамики (поля угроз K3, лагранжев поиск на торе, дискретный поток Клейна), 12 теорем-монографий и честный протокол проверок без подставленных результатов.',
    'about.p3': 'Комплект: 12 монографий теорем × RU/EN × PDF/DOCX, монография «Chess Particle Dynamics», протокол C1–C9 (Python, single-file dynamics.py) и полиглот-батарея C1–C10 на 7 языках.',
    'about.credit': 'Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich',
    'about.mono': '12 монографий теорем × RU/EN × PDF/DOCX (48 файлов) + монография × RU/EN × PDF/DOCX',
    'about.repo': 'Репозиторий: github.com/wild8highlander/chess-dynamics-lab',
    'about.repo.href': 'https://github.com/wild8highlander/chess-dynamics-lab',
    'about.license': 'Лицензия: индивидуальная исключительная лицензия / License: individual exclusive license',
    'about.tech': 'Статическое приложение: HTML + CSS + JS без сборки; открывается файлом index.html, на GitHub Pages и в Termux.',

    'footer.text': 'Chess Particle Dynamics · шахматная лаборатория / chess laboratory · v1.0.0',
    'footer.author': 'Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich',

    'log.copy.ok': 'Скопировано: ',
    'toast.proto.done': 'Протокол выполнен: '
  },
  en: {
    'app.title': 'Chess Particle Dynamics',
    'brand.sub': 'A certifiable chess laboratory · particles on 8×8',
    'nav.flow': 'Live flow', 'nav.theory': 'Theorems', 'nav.protocol': 'Protocol C',
    'nav.about': 'About', 'nav.aria': 'App sections',
    'tip.menu': 'Show/hide sections', 'tip.lang': 'Язык / Language',

    'flow.title': 'Live particle flow on the chessboard',
    'flow.lede': 'Pieces are glowing particles (gold = White, violet = Black). Enable the seeded auto flow or play manually: click a piece, then a highlighted square.',
    'flow.state': 'Position (particles)',
    'flow.state.kicker': '0x88 · full legality',
    'lbl.size': 'Board size',
    'size.hint': 'T14: generalized n×n boards from the complexity module; the preset is K+R vs K, won (verified by the retrograde oracle)',
    'cx.title': 'The KRK state space on n×n',
    'cx.kicker': 'live enumeration vs frozen E2',
    'cx.desc': 'The number of K+R vs K states grows as O(n⁶) — polynomial in n for a fixed piece count (T14): the exponential wall of generalized chess lives in the piece number k, not in the board size. The table is recomputed in your browser by the same enumeration as the frozen E2 experiment (complexity_scaling.json); for n < 8 the edges keep the degenerate tail of king moves off the sub-board (the 0x88 packing) — they are part of the frozen numbers too. The retrograde DTM on n×n reproduces the frozen 8×8 tables bit-exactly (E2: mismatches = 0).',
    'cx.states': 'states',
    'cx.edges': 'edges',
    'cx.won': 'won',
    'cx.maxdtm': 'max DTM (moves)',
    'cx.current': 'Current board: {n}×{n}',
    'flow.legend.white': 'White particle', 'flow.legend.black': 'Black particle',
    'flow.legend.field': 'Threat field Θ(c): gold → cyan',
    'flow.legend.fieldAnim': 'Θ(c) flow: field quanta, gold — White, cyan — Black',
    'flow.legend.last': 'Last move', 'flow.legend.check': 'King in check',
    'flow.legend.target': 'Available moves',
    'board.aria': 'Chessboard n×n: glowing piece particles, threat field, move highlights / Шахматная доска n×n: светящиеся частицы фигур, поле угроз, подсветка ходов',

    'controls.title': 'Controls',
    'btn.play': '▶ Auto flow', 'btn.pause': '⏸ Pause', 'btn.step': '⏭ Step',
    'btn.reset': '↺ Reset', 'btn.copy': 'Copy',
    'lbl.speed': 'Speed, plies/s', 'lbl.seed': 'PRNG seed',
    'lbl.field': 'Threat field Θ(c)', 'lbl.glyphs': 'Classical glyphs ♟',
    'field.hint': 'Heat map: number of attacking particles per square',
    'lbl.fieldAnim': 'Θ(c) flow animation',
    'field.animHint': 'Field quanta stream from the attacking particle to the attacked square; colour = attacking side. Position changes crossfade smoothly.',
    'glyphs.hint': 'Unicode pieces are drawn on top of the particles',
    'mode.chip.auto': 'auto flow', 'mode.chip.manual': 'manual mode',

    'energy.title': 'Lagrangian energy',
    'energy.kicker': 'μ = 0.1',
    'energy.E': 'E = [M_w − M_b] + μ·[m_w − m_b]',
    'energy.material': 'Material M (balance)',
    'energy.mobility': 'Mobility m (legal moves)',
    'energy.row.material': 'M_w / M_b', 'energy.row.mobility': 'm_w / m_b',
    'energy.row.ply': 'Plies', 'energy.row.side': 'White to move / Black to move',
    'energy.row.E': 'E (White\'s view)',
    'side.w': 'White', 'side.b': 'Black',
    'status.play': 'play', 'status.check': 'check!', 'status.checkmate': 'checkmate',
    'status.stalemate': 'stalemate', 'status.auto': 'auto', 'status.mated': 'mate delivered',
    'fen.label': 'Position FEN',

    'flow.moves': 'Move strip',
    'flow.empty': '— empty: start the auto flow or make a move —',
    'flow.copied': 'Copied to clipboard',
    'flow.gameover.mate': 'Checkmate. Winner:',
    'flow.gameover.stale': 'Stalemate — draw.',
    'flow.gameover.reset': 'Press «Reset» for a new game.',

    'tstar.title': 't* — damped billiard',
    'tstar.kicker': 'γ = π⁴/256',
    'tstar.desc': 'A particle on the N×N board geometry: mirror reflections with braking γ at each step; the total path until rest is |v₀|/(1−γ). Velocities are capped at ±(N−1).',
    'tstar.lbl.a': 'Velocity a', 'tstar.lbl.b': 'Velocity b',
    'tstar.t': 'Exact time t* = lcm(W/gcd(a,W), H/gcd(b,H))',
    'tstar.path': 'Path formula |v₀|/(1−γ)',
    'tstar.sim': 'Simulated path (K3)',
    'tstar.refl': 'Reflections',
    'tstar.aria': 'Damped billiard on the 8×8 grid / Демпфированный бильярд на сетке 8×8',
    'tstar.err': 'Step (0,0) is degenerate — set a non-zero velocity.',

    'theory.title': 'Twelve theorems',
    'theory.lede': 'Frozen facts of the laboratory: T01–T12 connect board algebra, particle kinematics and the verification protocol. Each theorem ships as a separate monograph (RU/EN × PDF/DOCX).',
    'theory.note': 'Values in the formulas are exact frozen constants of the project; some of them are recomputed live in the «Protocol C» section.',

    'proto.title': 'Protocol C — the honest battery',
    'proto.lede': 'C1–C10 are computed in your browser over this page\'s own engine. Values are never substituted: FAIL is possible and shown honestly.',
    'proto.run': '⟳ Run all', 'proto.deep': '⏱ Deep (perft 4)',
    'proto.deep.hint': 'Adds perft(4) = 197281 — takes seconds',
    'proto.col.code': 'Code', 'proto.col.check': 'Check',
    'proto.col.expected': 'Expected', 'proto.col.computed': 'Computed',
    'proto.col.result': 'Result', 'proto.col.ms': 'ms',
    'proto.note': 'All checks run synchronously; «Deep» adds perft(4). Results depend only on the page code — fully deterministic.',
    'proto.verdict': 'verdict:',

    'proto.c1.desc': 'Board algebra: V4 and D4 orbits + Burnside formulas',
    'proto.c2.desc': 'Kinematics: edge census of the empty-board move graph',
    'proto.c3.desc': 'Mobility census: sums and central maxima',
    'proto.c4.desc': 'Termination: t* formula vs simulation (grid W,H,a,b) + billiard path',
    'proto.c5.desc': 'Perft identities from the initial position (own engine)',
    'proto.c6.desc': 'Threat fields: mass 38, pawnless D4-equivariance, pawn anomaly',
    'proto.c7.desc': 'Energy: mobility 20 → 30 after 1.e4, E0 = 0, E = +1.0',
    'proto.c8.desc': 'Mate: DFS mate search on the Morphy miniature (key a1a6, PV)',
    'proto.c9.desc': 'splitmix64 (BigInt): vectors and exact inverse 1..2000',
    'proto.c10.desc': 'Knight tour: Warnsdorff from f5, final step preferring d6',

    'about.title': 'About',
    'about.p1': '«Chess Particle Dynamics» is the web laboratory of the chess-dynamics-lab project: chess pieces are treated as glowing particles on the 8×8 lattice, and the whole theory — orbits, censuses, threat fields, energy, flow termination — is verified by the C1–C10 protocol right in the browser.',
    'about.p2': 'The program develops the hodge-laboratory methodology: three layers of dynamics (K3 threat fields, Lagrangian search on the torus, the discrete Klein flow), 12 theorem monographs and an honest verification protocol with no substituted results.',
    'about.p3': 'The kit: 12 theorem monographs × RU/EN × PDF/DOCX, the «Chess Particle Dynamics» monograph, the C1–C9 protocol (Python, single-file dynamics.py) and the C1–C10 polyglot battery in 7 languages.',
    'about.credit': 'Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich',
    'about.mono': '12 theorem monographs × RU/EN × PDF/DOCX (48 files) + monograph × RU/EN × PDF/DOCX',
    'about.repo': 'Repository: github.com/wild8highlander/chess-dynamics-lab',
    'about.repo.href': 'https://github.com/wild8highlander/chess-dynamics-lab',
    'about.license': 'License: individual exclusive license / Лицензия: индивидуальная исключительная',
    'about.tech': 'Static application: HTML + CSS + JS with no build step; opens as index.html, on GitHub Pages and in Termux.',

    'footer.text': 'Chess Particle Dynamics · chess laboratory / шахматная лаборатория · v1.0.0',
    'footer.author': 'Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich',

    'log.copy.ok': 'Copied: ',
    'toast.proto.done': 'Protocol finished: '
  }
};

var currentLang = 'ru';
function t(key) {
  var d = DICT[currentLang] || DICT.ru;
  return (d[key] !== undefined) ? d[key] : (DICT.ru[key] !== undefined ? DICT.ru[key] : key);
}
function applyI18n() {
  document.documentElement.lang = currentLang;
  var els = document.querySelectorAll('[data-i18n]');
  for (var i = 0; i < els.length; i++) {
    var el = els[i], key = el.getAttribute('data-i18n');
    if (el.tagName === 'A' && key === 'about.repo') {
      el.textContent = t(key);
      el.setAttribute('href', t('about.repo.href'));
    } else el.textContent = t(key);
  }
  var titles = document.querySelectorAll('[data-i18n-title]');
  for (var j = 0; j < titles.length; j++)
    titles[j].setAttribute('title', t(titles[j].getAttribute('data-i18n-title')));
  var arias = document.querySelectorAll('[data-i18n-aria]');
  for (var k = 0; k < arias.length; k++)
    arias[k].setAttribute('aria-label', t(arias[k].getAttribute('data-i18n-aria')));
  var phs = document.querySelectorAll('[data-i18n-ph]');
  for (var m = 0; m < phs.length; m++)
    phs[m].setAttribute('placeholder', t(phs[m].getAttribute('data-i18n-ph')));
}

/* ═════════════ 9. RENDERER + UI (browser only) ══════════════════════ */
var App = {
  pos: null, size: 8,
  playing: false, speed: 3, seed: 0x12345678, rng: null,
  fieldOn: false, glyphsOn: false,
  field: null,                       // combined Θ(c) overlay
  fieldAnimOn: false,                // Θ-flow: animated field quanta
  fieldQuanta: [],                   // {f, t, ph, sp, color}
  lastField: null,                   // previous stable field (crossfade)
  fieldFadeOld: null, fieldFadeT0: 0,
  selection: 0, targets: [],
  history: [], san: [],
  particles: [], fx: [],
  acc: 0, lastFrame: 0, lastEnergy: 0,
  over: 0,                           // gameStatus snapshot
  billiard: null, billPts: [], billPath: 0, billPos: { x: 0.5, y: 0.5 },
  billV: { x: 1, y: 1 }, billRefl: 0,
  protoRows: null, protoDeep: false, protoRunning: false,
  sec: 'flow', reducedMotion: false
};

/* ── helpers ─────────────────────────────────────────────────────────── */
function $(id) { return document.getElementById(id); }
var toastTimer = null;
function toast(msg, warn) {
  var el = $('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = 'toast show' + (warn ? ' warn' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () { el.className = 'toast'; }, 3000);
}
function sizeCanvas(cv) {
  var dpr = Math.min(2.5, window.devicePixelRatio || 1);
  var r = cv.parentElement.getBoundingClientRect();
  var w = Math.max(120, Math.round(r.width) - 2);
  var h = Math.max(120, Math.round(r.height) - 2);
  cv.width = Math.round(w * dpr);
  cv.height = Math.round(h * dpr);
  cv._lw = w; cv._lh = h; cv._dpr = dpr;
}

/* ── particle bookkeeping ──────────────────────────────────────────── */
function buildParticles() {
  App.particles = [];
  var SQ = squaresOf(App.pos.n || 8);
  for (var i = 0; i < SQ.length; i++) {
    var sq = SQ[i], p = App.pos.board[sq];
    if (!p) continue;
    App.particles.push({ sq: sq, code: p, x: -1, y: -1, fly: null, trail: [], born: performanceNow() });
  }
}
function particleAt(sq) {
  for (var i = 0; i < App.particles.length; i++)
    if (App.particles[i].sq === sq && !App.particles[i].dead) return App.particles[i];
  return null;
}
/* sync particles with the board after a move; animate from→to */
function animateMove(m, undo) {
  var from = mvFrom(m), to = mvTo(m), flag = mvFlag(m), promo = mvPromo(m);
  var side = -App.pos.side;                       // side that moved
  var flying = particleAt(from);
  var capturedSq = flag === FLAG_EP ? to - 16 * side : to;
  var victim = (undo.captured || flag === FLAG_EP) ? particleAt(capturedSq) : null;
  if (victim && flying && victim !== flying) {
    victim.dead = true;
    victim.death = performanceNow();
  } else if (victim === flying) {
    /* EP: victim sits elsewhere — handled above; safety */
  }
  if (flying) {
    flying.sq = to;
    flying.fly = { fromSq: from, t0: performanceNow() };
    if (promo) flying.code = promo * side;
  }
  if (flag === FLAG_CASTLE) {
    var rFrom, rTo;
    if (to === 0x06) { rFrom = 0x07; rTo = 0x05; }
    else if (to === 0x02) { rFrom = 0x00; rTo = 0x03; }
    else if (to === 0x76) { rFrom = 0x77; rTo = 0x75; }
    else { rFrom = 0x70; rTo = 0x73; }
    var rook = particleAt(rFrom);
    if (rook) { rook.sq = rTo; rook.fly = { fromSq: rFrom, t0: performanceNow() + 40 }; }
  }
  /* safety: rebuild if bookkeeping drifted */
  var real = {};
  var SQr = squaresOf(App.pos.n || 8);
  for (var i = 0; i < SQr.length; i++) real[SQr[i]] = App.pos.board[SQr[i]];
  for (var j = 0; j < App.particles.length; j++) {
    var pt = App.particles[j];
    if (!pt.dead && real[pt.sq] !== pt.code) { buildParticles(); return; }
  }
}

/* ── move application ──────────────────────────────────────────────── */
function playMove(m, isAuto) {
  if (!m) return;
  var undo = make(App.pos, m);
  animateMove(m, undo);
  App.history.push({ uci: moveUci(m), side: -App.pos.side, undo: undo, m: m });
  App.selection = 0; App.targets = [];
  App.over = gameStatus(App.pos);
  App.field = null;                              // invalidate overlay
  updateEnergy();
  updateStats();
  renderMoveStrip();
  if (App.over && App.playing) setPlaying(false);
}

function setPlaying(on) {
  App.playing = on;
  var b = $('btnFlow');
  if (b) {
    b.textContent = on ? t('btn.pause') : t('btn.play');
    b.className = 'btn primary' + (on ? ' running' : '');
  }
  var chip = $('modeChip');
  if (chip) {
    chip.textContent = on ? t('mode.chip.auto') : t('mode.chip.manual');
    chip.className = 'mode-chip ' + (on ? 'm-run' : 'm-rest');
  }
}
function resetGame(newSeed) {
  var n = App.size || 8;
  App.pos = setFen(createPos(n), PRESETS[n] || START_FEN);
  if (newSeed || App.rng === null) App.rng = mulberry32(App.seed);
  App.history = []; App.over = 0; App.selection = 0; App.targets = [];
  App.field = null; App.acc = 0; App.particles = []; App.fx = [];
  buildParticles();
  setPlaying(App.playing);
  updateEnergy(); updateStats(); renderMoveStrip();
}

/* board-size switch (T14 generalized boards): load the verified KRK
   preset for the new n and rebuild every layer (particles, field,
   billiard) — honest reset, no cross-size history */
function setBoardSize(n) {
  n = SIZES.indexOf(n) >= 0 ? n : 8;
  App.size = n;
  try { localStorage.setItem('cdl.size', String(n)); } catch (e) { }
  var sel = $('selSize');
  if (sel && sel.value !== String(n)) sel.value = String(n);
  resetGame(false);
  updateVelocityInputs();
  restartBilliard();
  renderCxCard();
}

function autoStep() {
  if (App.over) { setPlaying(false); return; }
  var moves = legalMoves(App.pos);
  if (!moves.length) { App.over = gameStatus(App.pos); setPlaying(false); return; }
  var m = moves[Math.floor(App.rng() * moves.length)];
  playMove(m, true);
}

/* ── energy / stats panels ─────────────────────────────────────────── */
function updateEnergy() {
  var e = energy(App.pos);
  var elE = $('enE'), elMw = $('enMw'), elMb = $('enMb'),
      elmw = $('enmw'), elmb = $('enmb'),
      barM = $('barMat'), barMw = $('barMw'), barMb = $('barMb'),
      barW = $('barMobW'), barB = $('barMobB');
  if (!elE) return;
  elE.textContent = (e.E >= 0 ? '+' : '') + e.E.toFixed(1);
  elE.className = 'energy-val ' + (e.E > 0 ? 'pos' : e.E < 0 ? 'neg' : 'zero');
  elMw.textContent = e.Mw; elMb.textContent = e.Mb;
  elmw.textContent = e.mw; elmb.textContent = e.mb;
  var mTot = Math.max(1, e.Mw + e.Mb);
  barMw.style.width = (e.Mw / mTot * 100).toFixed(1) + '%';
  barMb.style.width = (e.Mb / mTot * 100).toFixed(1) + '%';
  barW.style.width = Math.min(100, e.mw / 60 * 100).toFixed(1) + '%';
  barB.style.width = Math.min(100, e.mb / 60 * 100).toFixed(1) + '%';
  barM.style.left = (50 + Math.max(-50, Math.min(50, (e.Mw - e.Mb) / 39 * 50))).toFixed(1) + '%';
}
function updateStats() {
  var ply = $('stPly'), side = $('stSide'), st = $('stStatus'), fen = $('stFen');
  if (!ply) return;
  ply.textContent = String(App.history.length);
  side.textContent = App.pos.side === 1 ? t('side.w') : t('side.b');
  var s = App.over;
  st.textContent = s === 1 ? t('status.checkmate') : s === 2 ? t('status.stalemate')
                 : inCheck(App.pos) ? t('status.check') : t('status.play');
  st.className = 'mode-chip ' + (s === 1 ? 'm-rest' : s === 2 ? 'm-term'
                 : inCheck(App.pos) ? 'm-rest' : 'm-run');
  fen.textContent = toFen(App.pos);
  var chip = $('sizeChip');
  if (chip) chip.textContent = (App.pos.n || 8) + '×' + (App.pos.n || 8);
}
function renderMoveStrip() {
  var strip = $('moveStrip'), meta = $('moveMeta');
  if (!strip) return;
  if (!App.history.length) {
    strip.innerHTML = '<span class="chain-empty">' + esc(t('flow.empty')) + '</span>';
    meta.textContent = '';
    return;
  }
  var html = '';
  for (var i = 0; i < App.history.length; i += 2) {
    var n = (i / 2 + 1);
    var w = App.history[i] ? App.history[i].uci : '';
    var bl = App.history[i + 1] ? App.history[i + 1].uci : '';
    var cls = (i + 1 >= App.history.length) ? ' last' : '';
    html += '<span class="mv-no">' + n + '.</span> <span class="mv-w' + cls + '">' + w +
            '</span>' + (bl ? ' <span class="mv-b' + cls + '">' + bl + '</span>' : '') + '  ';
  }
  strip.innerHTML = html;
  strip.scrollTop = strip.scrollHeight;
  var statusTxt = App.over === 1 ? ' · ' + t('status.checkmate')
                : App.over === 2 ? ' · ' + t('status.stalemate')
                : inCheck(App.pos) ? ' · ' + t('status.check') : '';
  meta.textContent = 'plies=' + App.history.length + statusTxt;
}
function esc(s) {
  return String(s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}

/* ── t* billiard card ──────────────────────────────────────────────── */
function restartBilliard() {
  var N = App.size || (App.pos && App.pos.n) || 8;
  var va = parseInt($('inpVa').value, 10) || 0;
  var vb = parseInt($('inpVb').value, 10) || 0;
  va = Math.max(-(N - 1), Math.min(N - 1, va));
  vb = Math.max(-(N - 1), Math.min(N - 1, vb));
  App.billV = { x: va, y: vb };
  App.billPts = [{ x: 0.5, y: 0.5 }];
  App.billPos = { x: 0.5, y: 0.5 };
  App.billPath = 0; App.billRefl = 0;
  var W = N, H = N;
  var ts = $('tsVal'), tp = $('tsPath'), tsim = $('tsSim'), tr = $('tsRefl'), warn = $('tsWarn');
  if (va === 0 && vb === 0) {
    ts.textContent = '—'; tp.textContent = '—'; tsim.textContent = '—'; tr.textContent = '—';
    warn.textContent = t('tstar.err');
    return;
  }
  warn.textContent = '';
  var tval = tstar(W, H, va, vb);
  var v0 = Math.sqrt(va * va + vb * vb);
  var exact = v0 / (1 - GAMMA_TORUS);
  var sim = simulateBilliard(W, H, va, vb, GAMMA_TORUS);
  ts.textContent = 't* = ' + tval;
  tp.textContent = exact.toFixed(4) + '  (|v₀| = ' + v0.toFixed(3) + ')';
  tsim.textContent = sim.path.toFixed(4) + ' · ratio ' + sim.ratio.toFixed(6);
  tr.textContent = String(sim.reflections);
}

/* ── board renderer ────────────────────────────────────────────────── */
/* rebuild the Θ(c) overlay + the animated field quanta after a move */
function ensureField(now) {
  if (App.field || !App.pos) return;
  var N = App.pos.n || 8, SQ = squaresOf(N);
  var thW = threatField(App.pos, WHITE), thB = threatField(App.pos, BLACK);
  var tot = new Int32Array(128);
  for (var i = 0; i < SQ.length; i++) {
    tot[SQ[i]] = thW[SQ[i]] + thB[SQ[i]];
  }
  App.fieldFadeOld = App.lastField;          // crossfade source
  App.fieldFadeT0 = now;
  App.field = tot;
  App.lastField = tot;
  rebuildQuanta();
}

/* Θ-flow quanta: one glowing quantum per attacker→target incidence;
   golden-ratio phase stagger keeps the stream from pulsing in step */
function rebuildQuanta() {
  App.fieldQuanta = [];
  if (!App.fieldAnimOn || !App.pos) return;
  var plan = [[WHITE, '#f2d38a'], [BLACK, '#69dfda']];
  for (var s = 0; s < 2; s++) {
    var pairs = attackPairs(App.pos, plan[s][0]);
    var stride = pairs.length > 320 ? Math.ceil(pairs.length / 320) : 1;
    for (var i = 0; i < pairs.length; i += stride) {
      App.fieldQuanta.push({
        f: pairs[i].f, t: pairs[i].t, color: plan[s][1],
        ph: (i * 0.618033988749895) % 1,
        sp: 0.35 + 0.3 * (((i * 2654435761) >>> 0) % 1000) / 1000
      });
    }
  }
}

function drawBoard(now) {
  var cv = $('boardCanvas');
  if (!cv) return;
  if (!cv._lw) sizeCanvas(cv);
  var ctx = cv.getContext('2d');
  var w = cv._lw, h = cv._lh;
  ctx.setTransform(cv._dpr, 0, 0, cv._dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  var N = App.pos.n || 8;
  var cell = Math.min(w, h) / N;
  var ox = (w - cell * N) / 2, oy = (h - cell * N) / 2;

  /* squares */
  for (var r = 0; r < N; r++) for (var f = 0; f < N; f++) {
    var dark = (f + r) % 2 === 1;
    ctx.fillStyle = dark ? '#0C1830' : '#15223C';
    ctx.fillRect(ox + f * cell, oy + (N - 1 - r) * cell, cell + 0.5, cell + 0.5);
  }

  /* threat field overlay Θ(c) (+ crossfade between positions) */
  function tint(field, mul) {
    var SQ = squaresOf(N);
    for (var i = 0; i < SQ.length; i++) {
      var sq2 = SQ[i], v = field[sq2];
      if (!v) continue;
      var tt = Math.min(1, v / 6);
      var rr = Math.round(201 + (63 - 201) * tt);
      var gg = Math.round(169 + (201 - 169) * tt);
      var bb2 = Math.round(106 + (173 - 106) * tt);
      ctx.fillStyle = 'rgba(' + rr + ',' + gg + ',' + bb2 + ',' +
                      ((0.14 + 0.4 * tt) * mul).toFixed(3) + ')';
      var f2 = sq2 & 7, r2 = sq2 >> 4;
      ctx.fillRect(ox + f2 * cell, oy + (N - 1 - r2) * cell, cell, cell);
    }
  }
  if (App.fieldOn || App.fieldAnimOn) ensureField(now);
  if (App.field) {
    var fk = App.fieldFadeOld && App.fieldFadeT0
           ? (now - App.fieldFadeT0) / 350 : 1;
    if (fk >= 1) {
      App.fieldFadeOld = null;
      tint(App.field, 1);
    } else {
      tint(App.fieldFadeOld, 1 - fk);
      tint(App.field, fk);
    }
  }
  /* Θ-flow: animated field quanta streaming attacker → target */
  if (App.fieldAnimOn && !App.reducedMotion && App.fieldQuanta.length) {
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (var q = 0; q < App.fieldQuanta.length; q++) {
      var qa = App.fieldQuanta[q];
      var ph = (qa.ph + now * 0.001 * qa.sp) % 1;
      var e2 = ph < 0.5 ? 2 * ph * ph
                        : 1 - Math.pow(-2 * ph + 2, 2) / 2;
      var fx = qa.f & 7, fy = qa.f >> 4, tx2 = qa.t & 7, ty2 = qa.t >> 4;
      var xq = ox + (fx + (tx2 - fx) * e2) * cell + cell / 2;
      var yq = oy + (N - 1 - fy + ((N - 1 - ty2) - (N - 1 - fy)) * e2) * cell + cell / 2;
      ctx.beginPath();
      ctx.arc(xq, yq, cell * 0.075, 0, Math.PI * 2);
      ctx.fillStyle = qa.color;
      ctx.globalAlpha = 0.55 * Math.sin(Math.PI * ph);
      ctx.shadowColor = qa.color;
      ctx.shadowBlur = 7;
      ctx.fill();
    }
    ctx.restore();
  }

  /* last move */
  if (App.history.length) {
    var lm = App.history[App.history.length - 1].m;
    strokeSquareCtx(ctx, ox, oy, cell, mvFrom(lm), 'rgba(227,201,143,.5)', 2, N);
    strokeSquareCtx(ctx, ox, oy, cell, mvTo(lm), 'rgba(227,201,143,.75)', 2, N);
  }
  /* check ring */
  if (inCheck(App.pos)) {
    var ks = App.pos.side === 1 ? App.pos.kings[0] : App.pos.kings[1];
    var cx = ox + (ks & 7) * cell + cell / 2, cy = oy + (N - 1 - (ks >> 4)) * cell + cell / 2;
    ctx.beginPath();
    ctx.arc(cx, cy, cell * 0.46, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(224,108,108,.9)';
    ctx.lineWidth = 2.5;
    ctx.shadowColor = 'rgba(224,108,108,.8)';
    ctx.shadowBlur = 12;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
  /* selection + targets */
  if (App.selection) {
    strokeSquareCtx(ctx, ox, oy, cell, App.selection, 'rgba(201,169,106,.95)', 2.5);
    for (var i3 = 0; i3 < App.targets.length; i3++) {
      var tg = App.targets[i3], m3 = tg.m, to3 = mvTo(m3);
      var x3 = ox + (to3 & 7) * cell + cell / 2, y3 = oy + (N - 1 - (to3 >> 4)) * cell + cell / 2;
      if (tg.capture) {
        ctx.beginPath();
        ctx.arc(x3, y3, cell * 0.42, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(216,123,160,.95)';
        ctx.lineWidth = 2.5;
        ctx.stroke();
      } else {
        ctx.beginPath();
        ctx.arc(x3, y3, cell * 0.14, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(201,169,106,.85)';
        ctx.shadowColor = 'rgba(201,169,106,.6)';
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }
  }

  /* particles (with fly animation + trails) */
  var animDur = App.reducedMotion ? 0 : Math.max(140, Math.min(420, 900 / Math.max(1, App.speed)));
  for (var p = 0; p < App.particles.length; p++) {
    var pt = App.particles[p];
    var homeX = ox + (pt.sq & 7) * cell + cell / 2;
    var homeY = oy + (N - 1 - (pt.sq >> 4)) * cell + cell / 2;
    var px = homeX, py = homeY;
    if (pt.fly) {
      if (App.reducedMotion) { pt.fly = null; }
      else {
        var k = Math.min(1, Math.max(0, (now - pt.fly.t0) / animDur));
        var ease = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        var oX = ox + (pt.fly.fromSq & 7) * cell + cell / 2;
        var oY = oy + (N - 1 - (pt.fly.fromSq >> 4)) * cell + cell / 2;
        px = oX + (homeX - oX) * ease;
        py = oY + (homeY - oY) * ease;
        pt.trail.push({ x: px, y: py, life: 1 });
        if (pt.trail.length > 26) pt.trail.shift();
        if (k >= 1) pt.fly = null;
      }
    }
    pt.x = px; pt.y = py;
  }
  /* trails */
  for (var s = 0; s < App.particles.length; s++) {
    var ps = App.particles[s];
    var col = ps.code > 0 ? '201,169,106' : '157,123,216';
    for (var d = 0; d < ps.trail.length; d++) {
      var dot = ps.trail[d];
      dot.life -= 0.035;
      if (dot.life <= 0) continue;
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, cell * 0.10 * dot.life, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(' + col + ',' + (0.32 * dot.life).toFixed(3) + ')';
      ctx.fill();
    }
    while (ps.trail.length && ps.trail[0].life <= 0) ps.trail.shift();
  }
  /* dead particles fade */
  for (var d2 = App.particles.length - 1; d2 >= 0; d2--) {
    var pd = App.particles[d2];
    if (!pd.dead) continue;
    var age = (now - pd.death) / 420;
    if (age >= 1) { App.particles.splice(d2, 1); continue; }
    drawParticle(ctx, pd.x, pd.y, cell * (1 - age), pd.code, 1 - age, false, now);
  }
  /* live particles */
  for (var lv = 0; lv < App.particles.length; lv++) {
    var pl = App.particles[lv];
    if (pl.dead) continue;
    drawParticle(ctx, pl.x, pl.y, cell, pl.code, 1, App.glyphsOn, now);
  }

  /* coordinates */
  ctx.font = '600 ' + Math.max(8, cell * 0.18).toFixed(0) + 'px "JetBrains Mono", monospace';
  ctx.fillStyle = 'rgba(140,162,188,.75)';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (var f8 = 0; f8 < N; f8++) {
    ctx.fillText('abcdefgh'.charAt(f8), ox + f8 * cell + cell / 2, oy + N * cell + cell * 0.16);
    ctx.fillText(String(N - f8), ox - cell * 0.16, oy + f8 * cell + cell / 2);
  }
}
function strokeSquareCtx(ctx, ox, oy, cell, sq, color, lw, n) {
  n = n || 8;
  var f = sq & 7, r = sq >> 4;
  ctx.strokeStyle = color;
  ctx.lineWidth = lw;
  ctx.strokeRect(ox + f * cell + 1, oy + (n - 1 - r) * cell + 1, cell - 2, cell - 2);
}
function drawParticle(ctx, x, y, cell, code, alpha, glyphs, now) {
  var isW = code > 0, ap = isW ? code : -code;
  var rad = cell * 0.31;
  var pulse = 1 + 0.05 * Math.sin((now || 0) / 500 + x * 0.11 + y * 0.07);
  var core = isW ? '#F6E7C1' : '#D9C8F5';
  var mid = isW ? '#C9A96A' : '#9D7BD8';
  var edge = isW ? 'rgba(201,169,106,0)' : 'rgba(157,123,216,0)';
  ctx.save();
  ctx.globalAlpha = alpha;
  var g = ctx.createRadialGradient(x, y, rad * 0.1, x, y, rad * 1.6 * pulse);
  g.addColorStop(0, core);
  g.addColorStop(0.55, mid);
  g.addColorStop(1, edge);
  ctx.shadowColor = isW ? 'rgba(201,169,106,.85)' : 'rgba(157,123,216,.85)';
  ctx.shadowBlur = cell * 0.42;
  ctx.beginPath();
  ctx.arc(x, y, rad * 1.25 * pulse, 0, Math.PI * 2);
  ctx.fillStyle = g;
  ctx.fill();
  ctx.shadowBlur = 0;
  if (glyphs) {
    ctx.font = (cell * 0.62).toFixed(0) + 'px serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = isW ? '#F6E7C1' : '#B79AEA';
    ctx.fillText(isW ? PIECE_GLYPH_W[ap] : PIECE_GLYPH_B[ap], x, y + cell * 0.02);
  } else {
    ctx.font = '700 ' + (cell * 0.30).toFixed(0) + 'px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = isW ? '#241A05' : '#17102A';
    ctx.fillText(PIECE_LETTER[ap], x, y + cell * 0.015);
  }
  ctx.restore();
}

/* ── billiard renderer ─────────────────────────────────────────────── */
var billLast = 0;
function drawBilliard(now) {
  var cv = $('billiardCanvas');
  if (!cv) return;
  if (!cv._lw) sizeCanvas(cv);
  var ctx = cv.getContext('2d');
  var w = cv._lw, h = cv._lh;
  ctx.setTransform(cv._dpr, 0, 0, cv._dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  var N = App.size || (App.pos && App.pos.n) || 8;
  var cell = Math.min(w, h) / N;
  var ox = (w - cell * N) / 2, oy = (h - cell * N) / 2;

  for (var r = 0; r < N; r++) for (var f = 0; f < N; f++) {
    ctx.fillStyle = (f + r) % 2 === 1 ? '#0C1830' : '#131F38';
    ctx.fillRect(ox + f * cell, oy + (N - 1 - r) * cell, cell + 0.5, cell + 0.5);
  }
  ctx.strokeStyle = 'rgba(201,169,106,.35)';
  ctx.lineWidth = 1.5;
  ctx.strokeRect(ox + 0.75, oy + 0.75, cell * N - 1.5, cell * N - 1.5);

  var vx = App.billV.x, vy = App.billV.y;
  if (vx === 0 && vy === 0) return;
  var dt = Math.min(0.05, (now - (billLast || now)) / 1000);
  billLast = now;
  var speed0 = Math.sqrt(vx * vx + vy * vy);
  var stepsF = speed0 * dt;                 // cells to travel this frame
  var guard = 0;
  while (stepsF > 1e-6 && guard++ < 64) {
    var step = Math.min(stepsF, speed0 * 0.25);
    var nx = App.billPos.x + App.billV.x / speed0 * step;
    var ny = App.billPos.y + App.billV.y / speed0 * step;
    var bounced = false;
    while (nx < 0 || nx > N) { nx = nx < 0 ? -nx : 2 * N - nx; App.billV.x = -App.billV.x; bounced = true; }
    while (ny < 0 || ny > N) { ny = ny < 0 ? -ny : 2 * N - ny; App.billV.y = -App.billV.y; bounced = true; }
    if (bounced) {
      App.billRefl++;
      App.billPts.push({ x: nx, y: ny, b: true });
      App.billV.x *= GAMMA_TORUS; App.billV.y *= GAMMA_TORUS;
    }
    App.billPos.x = nx; App.billPos.y = ny;
    App.billPath += step;
    App.billPts.push({ x: nx, y: ny });
    if (App.billPts.length > 900) App.billPts.shift();
    var sp = Math.sqrt(App.billV.x * App.billV.x + App.billV.y * App.billV.y);
    if (sp < 0.004 * speed0) {
      App.billV.x = 0; App.billV.y = 0;
      if (App.tsTimer === undefined || now - (App.tsTimer || 0) > 2400) {
        App.tsTimer = now;
        restartBilliard();                    // relaunch loop
      }
      break;
    }
    stepsF -= step;
  }

  /* trail */
  if (App.billPts.length > 1) {
    ctx.lineWidth = 1.8;
    for (var i = 1; i < App.billPts.length; i++) {
      var a = App.billPts[i - 1], bpt = App.billPts[i];
      var al = 0.05 + 0.5 * (i / App.billPts.length);
      ctx.strokeStyle = bpt.b ? 'rgba(63,201,173,' + al.toFixed(3) + ')'
                             : 'rgba(227,201,143,' + al.toFixed(3) + ')';
      ctx.beginPath();
      ctx.moveTo(ox + a.x * cell, oy + (N - a.y) * cell);
      ctx.lineTo(ox + bpt.x * cell, oy + (N - bpt.y) * cell);
      ctx.stroke();
    }
  }
  /* particle */
  var px = ox + App.billPos.x * cell, py = oy + (N - App.billPos.y) * cell;
  var g2 = ctx.createRadialGradient(px, py, 1, px, py, cell * 0.55);
  g2.addColorStop(0, '#F6E7C1');
  g2.addColorStop(0.6, 'rgba(63,201,173,.8)');
  g2.addColorStop(1, 'rgba(63,201,173,0)');
  ctx.shadowColor = 'rgba(63,201,173,.9)';
  ctx.shadowBlur = cell * 0.5;
  ctx.beginPath();
  ctx.arc(px, py, cell * 0.22, 0, Math.PI * 2);
  ctx.fillStyle = g2;
  ctx.fill();
  ctx.shadowBlur = 0;
}

/* ── theory + protocol rendering ───────────────────────────────────── */
function renderTheory() {
  var wrap = $('theoryGrid');
  if (!wrap) return;
  var html = '';
  for (var i = 0; i < THEORIES.length; i++) {
    var th = THEORIES[i], loc = th[currentLang] || th.ru;
    html += '<article class="card theory-card">' +
      '<div class="tc-head"><span class="tc-id">' + th.id + '</span>' +
      '<h3 class="tc-title">' + esc(loc.title) + '</h3></div>' +
      '<p class="tc-text">' + esc(loc.text) + '</p>' +
      '<div class="formula-line">' + esc(loc.formula) + '</div></article>';
  }
  wrap.innerHTML = html;
}

/* ── complexity card: the live n×n KRK space vs frozen E2 ─────────── */
var CX_LIVE = null;                      // cached {n: {states, edges}}
function computeCx() {
  if (CX_LIVE) return CX_LIVE;
  CX_LIVE = {};
  for (var i = 0; i < SIZES.length; i++) {
    var n = SIZES[i];
    CX_LIVE[n] = krkSpace(n);
  }
  return CX_LIVE;
}
function renderCxCard() {
  var box = $('cx-out');
  if (!box) return;
  var live = CX_LIVE;
  if (!live) {
    box.innerHTML = '<p class="hint">…</p>';
    setTimeout(function () {
      computeCx();
      renderCxCard();
    }, 30);
    return;
  }
  var rowsOk = true;
  var html = '<table class="data-table cx-table"><thead><tr>' +
    '<th>n</th><th>' + esc(t('cx.states')) + '</th><th>E2</th>' +
    '<th>' + esc(t('cx.edges')) + '</th><th>E2</th>' +
    '<th>' + esc(t('cx.won')) + '</th><th>' + esc(t('cx.maxdtm')) + '</th>' +
    '<th>✓</th></tr></thead><tbody>';
  for (var i = SIZES.length - 1; i >= 0; i--) {
    var n = SIZES[i], fr = FROZEN_E2[n], lv = live[n];
    var ok = lv.states === fr.states && lv.edges === fr.edges;
    if (!ok) rowsOk = false;
    html += '<tr' + (n === App.size ? ' class="cx-cur"' : '') + '>' +
      '<td class="mono">' + n + '</td>' +
      '<td class="mono">' + lv.states.toLocaleString() + '</td>' +
      '<td class="mono">' + fr.states.toLocaleString() + '</td>' +
      '<td class="mono">' + lv.edges.toLocaleString() + '</td>' +
      '<td class="mono">' + fr.edges.toLocaleString() + '</td>' +
      '<td class="mono">' + fr.won.toLocaleString() + '</td>' +
      '<td class="mono">' + fr.maxMoves + '</td>' +
      '<td class="mono ' + (ok ? 'cx-ok' : 'cx-bad') + '">' + (ok ? '✓' : '✗') + '</td></tr>';
  }
  html += '</tbody></table>';
  box.innerHTML = html;
  var cur = $('cx-current');
  if (cur) cur.textContent =
    t('cx.current').replace(/\{n\}/g, String(App.size)) + ' · ' +
    FROZEN_E2[App.size].states.toLocaleString() + ' ' + t('cx.states');
}
function renderProtocol() {
  var body = $('protoBody');
  if (!body) return;
  if (!App.protoRows) { body.innerHTML = ''; return; }
  var rows = App.protoRows, passN = 0, html = '';
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    if (r.pass) passN++;
    html += '<tr><td class="proto-id">' + r.code + '</td>' +
      '<td>' + esc(t(r.descKey)) + '</td>' +
      '<td class="mono td-exp">' + esc(r.expected) + '</td>' +
      '<td class="mono td-comp">' + esc(r.computed) + '</td>' +
      '<td><span class="pill ' + (r.pass ? 'pill-pass' : 'pill-fail') + '">' +
      (r.pass ? 'PASS' : 'FAIL') + '</span></td>' +
      '<td class="mono td-ms">' + r.ms.toFixed(1) + '</td></tr>';
  }
  body.innerHTML = html;
  var banner = $('protoVerdict');
  banner.textContent = t('proto.verdict') + ' ' + passN + '/' + rows.length +
                       (passN === rows.length ? ' — ALL CHECKS PASSED' : '');
  banner.className = 'verdict-banner ' + (passN === rows.length ? 'ok' : 'bad');
}
function runProtocolUI(deep) {
  if (App.protoRunning) return;
  App.protoRunning = true;
  App.protoDeep = !!deep;
  var btn = $('btnProtoRun');
  if (btn) btn.disabled = true;
  setTimeout(function () {
    var t0 = performanceNow();
    App.protoRows = runProtocol(App.protoDeep);
    renderProtocol();
    if (btn) btn.disabled = false;
    App.protoRunning = false;
    toast(t('toast.proto.done') + ((performanceNow() - t0) / 1000).toFixed(2) + ' s');
  }, 30);
}

/* ── interaction ───────────────────────────────────────────────────── */
function boardPointer(ev) {
  var cv = $('boardCanvas');
  if (!cv || App.over) return;
  var N = App.pos.n || 8;
  var rect = cv.getBoundingClientRect();
  var w = cv._lw || rect.width, h = cv._lh || rect.height;
  var cell = Math.min(w, h) / N;
  var ox = (w - cell * N) / 2, oy = (h - cell * N) / 2;
  var cx = (ev.clientX !== undefined ? ev.clientX : 0) - rect.left;
  var cy = (ev.clientY !== undefined ? ev.clientY : 0) - rect.top;
  var f = Math.floor((cx - ox) / cell), rr = (N - 1) - Math.floor((cy - oy) / cell);
  if (f < 0 || f > N - 1 || rr < 0 || rr > N - 1) return;
  var sq = rr * 16 + f;
  var p = App.pos.board[sq];

  /* target selected? */
  for (var i = 0; i < App.targets.length; i++) {
    if (mvTo(App.targets[i].m) === sq) {
      playMove(App.targets[i].m, false);
      return;
    }
  }
  /* own piece → select */
  if (p && (p > 0) === (App.pos.side > 0)) {
    if (App.selection === sq) { App.selection = 0; App.targets = []; return; }
    App.selection = sq;
    App.targets = [];
    var moves = legalMoves(App.pos);
    for (var j = 0; j < moves.length; j++) {
      if (mvFrom(moves[j]) === sq) {
        App.targets.push({ m: moves[j], capture: !!App.pos.board[mvTo(moves[j])] });
      }
    }
  } else {
    App.selection = 0; App.targets = [];
  }
}

/* ── main loop ─────────────────────────────────────────────────────── */
function frame(now) {
  if (App.playing && !App.over) {
    var dt = Math.min(0.25, (now - App.lastFrame) / 1000 || 0);
    App.acc += dt * App.speed;
    var n = Math.min(24, Math.floor(App.acc));
    App.acc -= Math.floor(App.acc);
    while (n-- > 0 && App.playing && !App.over) autoStep();
  }
  App.lastFrame = now;
  drawBoard(now);
  drawBilliard(now);
  requestAnimationFrame(frame);
}

/* ── sections / navigation ─────────────────────────────────────────── */
function showSec(sec) {
  App.sec = sec;
  var secs = ['flow', 'theory', 'protocol', 'about'];
  for (var i = 0; i < secs.length; i++) {
    var el = $('sec-' + secs[i]);
    if (el) el.className = 'sec' + (secs[i] === sec ? ' active' : '');
  }
  var btns = document.querySelectorAll('[data-sec]');
  for (var b = 0; b < btns.length; b++) {
    var on = btns[b].getAttribute('data-sec') === sec;
    btns[b].className = btns[b].className.replace(/ ?active/g, '') + (on ? ' active' : '');
    btns[b].setAttribute('aria-selected', on ? 'true' : 'false');
  }
  document.body.classList.remove('sidebar-open');
  var tg = $('sidebarToggle');
  if (tg) tg.setAttribute('aria-expanded', 'false');
  if (sec === 'theory') renderTheory();
  if (sec === 'protocol' && !App.protoRows) runProtocolUI(false);
  window.scrollTo(0, 0);
}

function setLang(lang) {
  currentLang = (lang === 'en') ? 'en' : 'ru';
  try { localStorage.setItem('cdl.lang', currentLang); } catch (e) { /* private mode */ }
  var ru = $('langRu'), en = $('langEn');
  if (ru && en) {
    ru.className = 'lang-btn' + (currentLang === 'ru' ? ' active' : '');
    en.className = 'lang-btn' + (currentLang === 'en' ? ' active' : '');
  }
  applyI18n();
  renderTheory();
  if (App.protoRows) renderProtocol();
  setPlaying(App.playing);
  updateStats();
  renderMoveStrip();
  renderCxCard();
}

/* ── init ──────────────────────────────────────────────────────────── */
function initUI() {
  App.reducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var saved = 'ru';
  try { saved = localStorage.getItem('cdl.lang') || 'ru'; } catch (e) { }
  currentLang = (saved === 'en') ? 'en' : 'ru';
  applyI18n();

  var savedSize = 8;
  try { savedSize = parseInt(localStorage.getItem('cdl.size'), 10) || 8; } catch (e) { }
  App.size = SIZES.indexOf(savedSize) >= 0 ? savedSize : 8;
  App.pos = setFen(createPos(App.size), PRESETS[App.size] || START_FEN);
  var sel = $('selSize');
  if (sel) {
    sel.value = String(App.size);
    sel.addEventListener('change', function () {
      setPlaying(false);
      setBoardSize(parseInt(sel.value, 10) || 8);
    });
  }
  App.rng = mulberry32(App.seed);
  buildParticles();
  updateEnergy(); updateStats(); renderMoveStrip();
  setPlaying(false);
  updateVelocityInputs();
  restartBilliard();
  renderCxCard();

  /* nav */
  var navBtns = document.querySelectorAll('[data-sec]');
  for (var i = 0; i < navBtns.length; i++) {
    (function (btn) {
      btn.addEventListener('click', function () { showSec(btn.getAttribute('data-sec')); });
    })(navBtns[i]);
  }
  var toggle = $('sidebarToggle');
  if (toggle) toggle.addEventListener('click', function () {
    var open = document.body.classList.toggle('sidebar-open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  /* lang */
  var lr = $('langRu'), le = $('langEn');
  if (lr) lr.addEventListener('click', function () { setLang('ru'); });
  if (le) le.addEventListener('click', function () { setLang('en'); });
  lr = le = null;
  if ($('langRu')) { $('langRu').className = 'lang-btn' + (currentLang === 'ru' ? ' active' : ''); }
  if ($('langEn')) { $('langEn').className = 'lang-btn' + (currentLang === 'en' ? ' active' : ''); }

  /* controls */
  $('btnFlow').addEventListener('click', function () { setPlaying(!App.playing); });
  $('btnStep').addEventListener('click', function () {
    setPlaying(false); autoStep();
  });
  $('btnReset').addEventListener('click', function () {
    App.seed = (parseInt($('inpSeed').value, 10) || 0) >>> 0;
    App.rng = mulberry32(App.seed);
    resetGame(false);
  });
  $('inpSpeed').addEventListener('input', function () {
    App.speed = parseFloat(this.value);
    $('speedVal').textContent = String(App.speed);
  });
  $('inpSeed').value = '305419896';
  $('chkField').addEventListener('change', function () {
    App.fieldOn = this.checked;
    App.field = null;
    App.lastField = null;
    App.fieldFadeOld = null;
  });
  $('chkFieldAnim').addEventListener('change', function () {
    App.fieldAnimOn = this.checked;
    App.field = null;              // rebuild overlay + quanta
    App.lastField = null;          // no crossfade on a manual toggle
    App.fieldFadeOld = null;
  });
  $('chkGlyphs').addEventListener('change', function () {
    App.glyphsOn = this.checked;
  });

  /* board interaction */
  var bc = $('boardCanvas');
  bc.addEventListener('pointerdown', function (ev) {
    ev.preventDefault();
    boardPointer(ev);
  });

  /* copy buttons */
  $('btnCopyPgn').addEventListener('click', function () {
    var s = '';
    for (var i = 0; i < App.history.length; i++)
      s += (i % 2 === 0 ? (i / 2 + 1) + '. ' : '') + App.history[i].uci + ' ';
    copyText(s.trim() || toFen(App.pos));
  });
  $('btnCopyFen').addEventListener('click', function () { copyText(toFen(App.pos)); });

  /* t* inputs */
  $('inpVa').addEventListener('change', restartBilliard);
  $('inpVb').addEventListener('change', restartBilliard);

  /* protocol */
  $('btnProtoRun').addEventListener('click', function () { runProtocolUI(false); });
  $('btnProtoDeep').addEventListener('click', function () { runProtocolUI(true); });

  /* resize */
  window.addEventListener('resize', function () {
    var c1 = $('boardCanvas'), c2 = $('billiardCanvas');
    if (c1) c1._lw = 0;
    if (c2) c2._lw = 0;
  });

  showSec('flow');
  requestAnimationFrame(frame);
}
function copyText(s) {
  var done = function () { toast(t('flow.copied')); };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(s).then(done, function () { fallbackCopy(s); done(); });
  } else { fallbackCopy(s); done(); }
}
function fallbackCopy(s) {
  var ta = document.createElement('textarea');
  ta.value = s;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); } catch (e) { }
  document.body.removeChild(ta);
}
/* the t* inputs must follow the board size (±(n−1)) */
function updateVelocityInputs() {
  var N = App.size || 8;
  var a = $('inpVa'), b = $('inpVb');
  if (a) { a.max = String(N - 1); if (parseInt(a.value, 10) > N - 1) a.value = String(N - 1); }
  if (b) { b.max = String(N - 1); if (parseInt(b.value, 10) > N - 1) b.value = String(N - 1); }
}

/* ═══════════════════════ export core / boot ═════════════════════════ */
var CDL = {
  version: '1.0.0',
  START_FEN: START_FEN, MORPHY_FEN: MORPHY_FEN, PAWNLESS_FEN: PAWNLESS_FEN,
  createPos: createPos, setFen: setFen, toFen: toFen,
  legalMoves: legalMoves, genMoves: genMoves, make: make, unmake: unmake,
  attacked: attacked, inCheck: inCheck, gameStatus: gameStatus,
  perft: perft, uciToMove: uciToMove, findMove: findMove, moveUci: moveUci,
  sqName: sqName, nameSq: nameSq, SQUARES: SQUARES,
  onSq: onSq, squaresOf: squaresOf, krkSpace: krkSpace,
  FROZEN_E2: FROZEN_E2, PRESETS: PRESETS, SIZES: SIZES,
  D4: D4, V4: V4, orbitCensus: orbitCensus, burnside: burnside,
  tstar: tstar, simulateTstar: simulateTstar, GAMMA_TORUS: GAMMA_TORUS,
  simulateBilliard: simulateBilliard,
  splitmix64: splitmix64, splitmix64Inverse: splitmix64Inverse, hex64: hex64,
  mulberry32: mulberry32,
  threatField: threatField, attackSum: attackSum, pieceAttackSquares: pieceAttackSquares,
  equivarianceViolations: equivarianceViolations,
  material: material, mobility: mobility, energy: energy, MU: MU,
  mateDfs: mateDfs, extractPV: extractPV,
  warnsdorffTour: warnsdorffTour, verifyTour: verifyTour, KNIGHT_NB: KNIGHT_NB,
  runProtocol: runProtocol, THEORIES: THEORIES, t: t, setLangExternal: function (l) { currentLang = l; }
};
if (typeof window !== 'undefined') window.CDL = CDL;

if (typeof document !== 'undefined' && typeof window !== 'undefined' &&
    document.getElementById('appRoot')) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUI);
  } else {
    initUI();
  }
}
})();
