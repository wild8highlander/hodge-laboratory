/* chess-oracle · chess.js
   Minimal 0x88 engine for the endgames K+R vs K, K+Q vs K, K+N vs K and
   K+P vs K — a faithful JS subset of dynamics.py (chess-dynamics-lab).
   No castling, no en passant; promotion is auto-queen (DTM-sufficient:
   the queen move-set dominates rook/bishop, and N/B under-promotion
   lands in KNK/KBK where no mate exists). White has exactly one king
   plus one strong piece (R/Q/N/P), Black a lone king.

   Conventions match dynamics.py: white pieces are positive codes, black
   pieces negative; squares are 0x88 (sq = 16*rank + file); moves are plain
   objects {f, t, promo?}. Pseudo-legal generation + make/test/unmake
   legality, exactly like the Python reference. */

(function (global) {
  'use strict';

  var EMPTY = 0, WP = 1, WN = 2, WB = 3, WR = 4, WQ = 5, WK = 6,
      BP = -1, BN = -2, BB = -3, BR = -4, BQ = -5, BK = -6;
  var DIR_ROOK = [16, -16, 1, -1];
  var DIR_BISHOP = [17, 15, -17, -15];
  var DIR_KING = DIR_ROOK.concat(DIR_BISHOP);
  var KNIGHT_OFFS = [33, 31, 18, 14, -33, -31, -18, -14];
  var PIECE_VALUE = { 1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0,
                      '-1': 1, '-2': 3, '-3': 3, '-4': 5, '-5': 9,
                      '-6': 0 };
  var STRONG = [WR, WQ, WN, WP];

  function sqName(sq) { return 'abcdefgh'[sq & 7] + (1 + (sq >> 4)); }
  function nameSq(s) {
    return (s.charCodeAt(0) - 97) + 16 * (s.charCodeAt(1) - 49);
  }
  function onBoard(sq) { return !(sq & 0x88); }

  function Position() {
    this.board = new Int8Array(128);
    this.side = 1;               // 1 = white to move, -1 = black
  }

  Position.prototype.clone = function () {
    var p = new Position();
    p.board.set(this.board);
    p.side = this.side;
    return p;
  };

  Position.prototype.setFromSetup = function (wk, wq, bk, wqCode, side) {
    this.board = new Int8Array(128);
    this.board[wk] = WK;
    this.board[wq] = wqCode;     // WR or WQ
    this.board[bk] = BK;
    this.side = side;
    return this;
  };

  Position.prototype.kingSquare = function (side) {
    var code = side > 0 ? WK : BK;
    for (var sq = 0; sq < 128; sq++) {
      if (!(sq & 0x88) && this.board[sq] === code) return sq;
    }
    return -1;
  };

  Position.prototype.strongSquare = function () {
    for (var sq = 0; sq < 128; sq++) {
      if (!(sq & 0x88) && STRONG.indexOf(this.board[sq]) >= 0) {
        return sq;
      }
    }
    return -1;
  };

  Position.prototype.strongCode = function () {
    var sq = this.strongSquare();
    return sq < 0 ? 0 : this.board[sq];
  };

  /* Is `sq` attacked by any piece of side `by`? Sliders with blocking,
     knight offsets, pawn diagonals. */
  Position.prototype.attacked = function (sq, by) {
    var b = this.board, i, o, t;
    // enemy king adjacency
    for (i = 0; i < 8; i++) {
      t = sq + DIR_KING[i];
      if (onBoard(t) && b[t] === (by > 0 ? WK : BK)) return true;
    }
    // knight offsets (no blocking concept)
    for (i = 0; i < 8; i++) {
      t = sq + KNIGHT_OFFS[i];
      if (onBoard(t) && b[t] === (by > 0 ? WN : BN)) return true;
    }
    // pawn diagonals: a white pawn on t attacks t+15/t+17, hence sq is
    // attacked by a white pawn standing at sq-15 / sq-17; a black pawn
    // attacks downward, so sq+15 / sq+17 for black attackers
    if (by > 0) {
      t = sq - 15; if (onBoard(t) && b[t] === WP) return true;
      t = sq - 17; if (onBoard(t) && b[t] === WP) return true;
    } else {
      t = sq + 15; if (onBoard(t) && b[t] === BP) return true;
      t = sq + 17; if (onBoard(t) && b[t] === BP) return true;
    }
    // slider rays from sq outward: the FIRST piece on the ray decides
    for (i = 0; i < 4; i++) {
      for (o = sq + DIR_ROOK[i]; onBoard(o); o += DIR_ROOK[i]) {
        if (b[o] !== EMPTY) {
          if (by > 0 && (b[o] === WR || b[o] === WQ)) return true;
          if (by < 0 && (b[o] === BR || b[o] === BQ)) return true;
          break;
        }
      }
    }
    for (i = 0; i < 4; i++) {
      for (o = sq + DIR_BISHOP[i]; onBoard(o); o += DIR_BISHOP[i]) {
        if (b[o] !== EMPTY) {
          if (by > 0 && b[o] === WQ) return true;
          if (by < 0 && b[o] === BQ) return true;
          break;
        }
      }
    }
    return false;
  };

  Position.prototype.inCheck = function (side) {
    var k = this.kingSquare(side);
    return k >= 0 && this.attacked(k, -side);
  };

  Position.prototype.pseudoMoves = function () {
    var b = this.board, side = this.side, out = [], sq, i, o, t;
    for (sq = 0; sq < 128; sq++) {
      if (sq & 0x88) continue;
      var p = b[sq];
      if (p === EMPTY || (p > 0) !== (side > 0)) continue;
      var ap = p > 0 ? p : -p;
      if (ap === 6) {                                  // king
        for (i = 0; i < 8; i++) {
          t = sq + DIR_KING[i];
          if (!onBoard(t)) continue;
          var tp = b[t];
          if (tp !== EMPTY && (tp > 0) === (side > 0)) continue;
          out.push({ f: sq, t: t });
        }
      } else if (ap === 2) {                           // knight
        for (i = 0; i < 8; i++) {
          t = sq + KNIGHT_OFFS[i];
          if (!onBoard(t)) continue;
          var np = b[t];
          if (np !== EMPTY && (np > 0) === (side > 0)) continue;
          out.push({ f: sq, t: t });
        }
      } else if (ap === 1) {                           // pawn
        var fwd = side > 0 ? 16 : -16;
        var startRank = side > 0 ? 1 : 6;
        var promoRank = side > 0 ? 7 : 0;
        t = sq + fwd;
        if (onBoard(t) && b[t] === EMPTY) {
          out.push({ f: sq, t: t,
                     promo: (t >> 4) === promoRank ? (side > 0 ? WQ : BQ)
                                                   : 0 });
          if ((sq >> 4) === startRank) {
            var t2 = sq + 2 * fwd;
            if (onBoard(t2) && b[t2] === EMPTY) {
              out.push({ f: sq, t: t2, promo: 0 });
            }
          }
        }
        for (i = -1; i <= 1; i += 2) {
          t = sq + fwd + i;
          if (!onBoard(t)) continue;
          var cp = b[t];
          if (cp !== EMPTY && (cp > 0) !== (side > 0)) {
            out.push({ f: sq, t: t,
                       promo: (t >> 4) === promoRank ? (side > 0 ? WQ : BQ)
                                                     : 0 });
          }
        }
      } else {                                         // rook or bishop or queen
        var dirs = ap === 4 ? DIR_ROOK
                 : (ap === 3 ? DIR_BISHOP
                             : DIR_ROOK.concat(DIR_BISHOP));
        for (i = 0; i < dirs.length; i++) {
          for (o = sq + dirs[i]; onBoard(o); o += dirs[i]) {
            var q = b[o];
            if (q === EMPTY) { out.push({ f: sq, t: o }); continue; }
            if ((q > 0) !== (side > 0)) out.push({ f: sq, t: o });
            break;
          }
        }
      }
    }
    return out;
  };

  /* make/unmake with undo records (captures always land on the target;
     promotion is carried on the move object and restored by undo.moved). */
  Position.prototype.make = function (m) {
    var undo = { f: m.f, t: m.t, captured: this.board[m.t],
                 moved: this.board[m.f], promo: m.promo || 0 };
    this.board[m.t] = undo.promo ? undo.promo : undo.moved;
    this.board[m.f] = EMPTY;
    this.side = -this.side;
    return undo;
  };

  Position.prototype.unmake = function (undo) {
    this.board[undo.f] = undo.moved;
    this.board[undo.t] = undo.captured;
    this.side = -this.side;
  };

  Position.prototype.legalMoves = function () {
    var out = [], self = this, moves = this.pseudoMoves(), i, undo, mover;
    for (i = 0; i < moves.length; i++) {
      undo = this.make(moves[i]);
      mover = -this.side;                       // the side that just moved
      if (!this.attacked(this.kingSquare(mover), this.side)) {
        out.push(moves[i]);
      }
      this.unmake(undo);
    }
    return out;
  };

  Position.prototype.isLegalSetup = function () {
    var wk = this.kingSquare(1), bk = this.kingSquare(-1);
    var wq = this.strongSquare();
    if (wk < 0 || bk < 0 || wq < 0) return { ok: false, why: 'pieces' };
    if (wk === wq || wk === bk || wq === bk) return { ok: false, why: 'overlap' };
    var df = Math.abs((wk & 7) - (bk & 7));
    var dr = Math.abs((wk >> 4) - (bk >> 4));
    if (df <= 1 && dr <= 1) return { ok: false, why: 'kings-adjacent' };
    // black king must not be en prise when White is to move
    if (this.side === 1 && this.attacked(bk, 1)) {
      return { ok: false, why: 'black-en-prise' };
    }
    // a pawn cannot stand on its own first rank (outside the KPK space)
    if (this.board[wq] === WP && (wq >> 4) === 0) {
      return { ok: false, why: 'pawn-rank' };
    }
    // with Black to move the White pawn must not be capturable-for-free
    // is NOT a setup error (the capture is a legal move -> draw)
    return { ok: true };
  };

  /* material balance of `side` in pawn units (PIECE_VALUE of dynamics.py) */
  Position.prototype.material = function (side) {
    var s = 0, sq, p;
    for (sq = 0; sq < 128; sq++) {
      if (sq & 0x88) continue;
      p = this.board[sq];
      if (p !== EMPTY && (p > 0) === (side > 0)) s += PIECE_VALUE[p];
    }
    return s;
  };

  /* pseudo-legal move count of `side` (pseudo_mobility in dynamics.py) */
  Position.prototype.pseudoMobility = function (side) {
    var saved = this.side;
    this.side = side;
    var n = this.pseudoMoves().length;
    this.side = saved;
    return n;
  };

  /* threat field Theta[c] = #pieces of `side` attacking c (K3, blocking;
     knight offsets and pawn diagonals are non-sliding) */
  Position.prototype.threatField = function (side) {
    var theta = new Int8Array(128), sq, p, i, dirs, o;
    for (sq = 0; sq < 128; sq++) {
      if (sq & 0x88) continue;
      p = this.board[sq];
      if (p === EMPTY || (p > 0) !== (side > 0)) continue;
      var ap = p > 0 ? p : -p;
      if (ap === 2) {                                  // knight
        for (i = 0; i < 8; i++) {
          o = sq + KNIGHT_OFFS[i];
          if (onBoard(o)) theta[o] += 1;
        }
      } else if (ap === 1) {                           // pawn
        o = sq + (p > 0 ? 15 : -17);
        if (onBoard(o)) theta[o] += 1;
        o = sq + (p > 0 ? 17 : -15);
        if (onBoard(o)) theta[o] += 1;
      } else {
        dirs = ap === 6 ? DIR_KING : (ap === 4 ? DIR_ROOK
               : (ap === 3 ? DIR_BISHOP
                           : DIR_ROOK.concat(DIR_BISHOP)));
        for (i = 0; i < dirs.length; i++) {
          for (o = sq + dirs[i]; onBoard(o); o += dirs[i]) {
            theta[o] += 1;
            if (this.board[o] !== EMPTY) break;    // blocking=True semantics
          }
        }
      }
    }
    return theta;
  };

  Position.prototype.toFEN = function () {
    var rows = [], r, f, row, emp, p, sym;
    var map = {};
    map[WK] = 'K'; map[WR] = 'R'; map[WQ] = 'Q'; map[WN] = 'N'; map[WP] = 'P';
    map[BK] = 'k'; map[BR] = 'r'; map[BQ] = 'q'; map[BN] = 'n'; map[BP] = 'p';
    for (r = 7; r >= 0; r--) {
      row = ''; emp = 0;
      for (f = 0; f < 8; f++) {
        p = this.board[16 * r + f];
        if (p === EMPTY) { emp++; continue; }
        if (emp) { row += emp; emp = 0; }
        sym = map[p] || '?';
        row += sym;
      }
      if (emp) row += emp;
      rows.push(row);
    }
    return rows.join('/') + ' ' + (this.side === 1 ? 'w' : 'b') +
           ' - - 0 1';
  };

  Position.fromFEN = function (fen) {
    var pos = new Position();
    var parts = fen.trim().split(/\s+/);
    var rows = parts[0].split('/');
    var map = { K: WK, R: WR, Q: WQ, N: WN, P: WP,
                k: BK, r: BR, q: BQ, n: BN, p: BP };
    var r, f, row, ch, sq;
    for (r = 0; r < 8; r++) {
      row = rows[7 - r]; f = 0;
      for (var i = 0; i < row.length; i++) {
        ch = row[i];
        if (ch >= '1' && ch <= '8') { f += +ch; continue; }
        sq = 16 * r + f;
        pos.board[sq] = map[ch];
        f++;
      }
    }
    pos.side = (parts[1] === 'b') ? -1 : 1;
    return pos;
  };

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.chess = {
    Position: Position,
    EMPTY: EMPTY, WP: WP, WN: WN, WB: WB, WR: WR, WQ: WQ, WK: WK,
    BP: BP, BN: BN, BB: BB, BR: BR, BQ: BQ, BK: BK,
    DIR_KING: DIR_KING, DIR_ROOK: DIR_ROOK,
    KNIGHT_OFFS: KNIGHT_OFFS,
    sqName: sqName, nameSq: nameSq, onBoard: onBoard,
    PIECE_VALUE: PIECE_VALUE
  };
})(window);
