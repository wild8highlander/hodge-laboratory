/* chess-oracle · audit.js
   LIVE Bellman audit of the frozen DTM table.

   The retrograde build certified the Bellman fixpoint over ALL states in
   Python. Here, every position the user actually VISITS is re-verified in
   the browser against an INDEPENDENT move generator (chess.js) — the proof
   stops being a frozen artifact and becomes a running process. Any single
   violation turns the banner red; the oracle does not bluff.

   Audited properties per state s (values: 0..63 = plies, 200 = drawn):

   BTM mate (v = 0, Black to move):
       no legal moves AND Black is in check.
   WTM won (v = d >= 1, White to move):
       exists a child with value d-1, and NO child with a won value < d-1
       (otherwise White would have been labelled earlier).
   BTM lost (v = d >= 1, Black to move):
       ALL children are won (no escape) AND max(child value) = d-1
       (best resistance) — Black cannot have a capturing escape.
   WTM drawn (v = 200, White to move):
       ALL children are drawn (any won child would make White win).
   BTM drawn (v = 200, Black to move):
       at least one of: a child with value 200 (a drawing retreat),
       stalemate (no legal moves, not in check), or an immediate capture
       of the undefended strong piece (K vs K afterwards — outside the
       packed state space, hence the `escape` flag of the retrograde). */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;
  var TB = global.ChessOracle.tb;

  function childStates(tb, pos) {
    var moves = pos.legalMoves(), out = [], i;
    for (i = 0; i < moves.length; i++) {
      var child = TB.probeAfterMove(tb, pos, moves[i]);
      out.push({ move: moves[i],
                 uci: C.sqName(moves[i].f) + C.sqName(moves[i].t),
                 state: null,
                 value: child == null ? null : child.raw });
    }
    return out;
  }

  function canCapturePiece(pos) {
    // Black king takes the strong piece if it stands adjacent and is not
    // defended by the White king (K vs K afterwards: draw).
    var bk = pos.kingSquare(-1), wq = pos.strongSquare(),
        wk = pos.kingSquare(1);
    if (bk < 0 || wq < 0 || wk < 0) return false;
    var near = false, i, t;
    for (i = 0; i < 8; i++) {
      t = bk + C.DIR_KING[i];
      if (t === wq) { near = true; break; }
    }
    if (!near) return false;
    for (i = 0; i < 8; i++) {
      t = wk + C.DIR_KING[i];
      if (t === wq) return false;            // defended: capture illegal
    }
    return true;
  }

  function auditState(tb, pos, state) {
    var info = tb.probe(state);
    var u = TB.unpackState(state);
    var isWhite = u.stm === 0;
    var children = null, verdict, reason, i;

    if (info.mate && !isWhite) {
      children = childStates(tb, pos);
      var noMoves = children.length === 0;
      var checked = pos.inCheck(-1);
      verdict = noMoves && checked;
      reason = noMoves && checked ? 'mate_confirmed'
                                  : 'mate_label_inconsistent';
    } else if (info.won && isWhite) {
      var d = info.plies;
      children = childStates(tb, pos);
      var hasOptimal = false, tooFast = false;
      for (i = 0; i < children.length; i++) {
        var cv = children[i].value;
        if (cv != null && cv < 200 && cv === d - 1) hasOptimal = true;
        if (cv != null && cv < 200 && cv < d - 1) tooFast = true;
      }
      verdict = hasOptimal && !tooFast;
      reason = verdict ? 'exists_child_d-1_no_faster'
                       : (tooFast ? 'child_faster_than_d-1'
                                  : 'no_child_with_d-1');
    } else if (info.won && !isWhite) {
      var dd = info.plies;
      children = childStates(tb, pos);
      var allWon = children.length > 0, mx = -1;
      for (i = 0; i < children.length; i++) {
        var w = children[i].value;
        if (w == null || w >= 200) { allWon = false; break; }
        if (w > mx) mx = w;
      }
      verdict = allWon && mx === dd - 1 && !canCapturePiece(pos);
      reason = verdict ? 'all_children_won_max_d-1'
                       : ('escape_or_wrong_max(mx=' + mx + ',d=' + dd + ')');
    } else if (isWhite) {                    // WTM drawn
      children = childStates(tb, pos);
      var anyWon = false;
      for (i = 0; i < children.length; i++) {
        if (children[i].value != null && children[i].value < 200) {
          anyWon = true; break;
        }
      }
      verdict = !anyWon;
      reason = verdict ? 'all_children_drawn'
                       : 'won_child_from_drawn_position';
    } else {                                 // BTM drawn
      var stalemate = false, drawingChild = false;
      children = childStates(tb, pos);
      if (children.length === 0 && !pos.inCheck(-1)) stalemate = true;
      for (i = 0; i < children.length; i++) {
        if (children[i].value === 200) { drawingChild = true; break; }
      }
      verdict = stalemate || drawingChild || canCapturePiece(pos);
      reason = stalemate ? 'stalemate'
             : drawingChild ? 'drawing_child'
             : canCapturePiece(pos) ? 'capture_escape'
             : 'no_draw_resource';
    }

    return { verdict: verdict, reason: reason, isWhite: isWhite,
             value: info.raw, plies: info.plies,
             children: children };
  }

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.audit = {
    auditState: auditState, childStates: childStates,
    canCapturePiece: canCapturePiece
  };
})(window);
