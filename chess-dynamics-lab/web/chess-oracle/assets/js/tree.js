/* chess-oracle · tree.js
   Interactive unfolding of the minimal winning-strategy tree — the E3
   experiment made tangible.

   T(w) = 1 + min_{b : dtm[b] = dtm[w]-1} ( 1 + sum_{r in replies(b)} T(r) )

   counted EXACTLY on the unfolded tree (the tree, not the DAG), memoised.
   For KPK the recursion CROSSES the promotion boundary: a promoted child
   lives in the KQK space, so memo keys carry the space and the whole
   promoted subtree is probed against the frozen KQK certificate. This is
   the explicit certificate; the frozen table is the implicit one. The
   explorer also walks levels: nodes per remaining-DTM level, so the user
   sees the exponential shape grow as deeper levels are included. */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;
  var TB = global.ChessOracle.tb;

  function TreeExplorer(tb) {
    this.tb = tb;
    this.rootKind = tb.kind;      // a 'kpk' tree may cross into 'kqk'
    this.memo = new Map();        // space|state -> exact T value
  }

  TreeExplorer.prototype.reset = function () {
    this.memo.clear();
  };

  /* Space of a position inside a tree rooted at rootKind: within a kpk
     tree a queen (or rook) as the strong piece can appear only through
     promotion, and then the position belongs to the kqk space. */
  function spaceOf(pos, rootKind) {
    if (rootKind !== 'kpk') return rootKind;
    var code = pos.strongCode();
    if (code === C.WQ || code === C.WR) return 'kqk';
    if (code === C.WP) return 'kpk';
    return null;                                  // K vs K: outside spaces
  }

  function probePos(pos, space) {
    if (space == null) return null;
    var t = TB.getLoaded(space);
    if (!t) return null;
    var st = TB.stateOfPosition(pos);
    return st === null ? null : t.probe(st);
  }

  /* Exact minimal tree size for a won WTM state (mirrors E3). */
  TreeExplorer.prototype.treeSize = function (state) {
    var rootKind = this.rootKind;
    var memo = this.memo;

    function rec(s, space) {
      var key = space + '|' + s;
      var v = memo.get(key);
      if (v !== undefined) return v;
      var t = TB.getLoaded(space);
      var u = TB.unpackState(s);
      var pos = new C.Position().setFromSetup(u.wk, u.wp, u.bk,
                                              t.spec.pieceCode, 1);
      var D = t.probe(s).plies;
      var moves = pos.legalMoves();
      var best = null;
      for (var i = 0; i < moves.length; i++) {
        var undo = pos.make(moves[i]);
        var childSpace = (space === 'kpk' && undo.promo) ? 'kqk' : space;
        var cv = probePos(pos, childSpace);
        var replies = [];
        if (cv && cv.won && cv.plies === D - 1) {
          var rmoves = pos.legalMoves();
          for (var j = 0; j < rmoves.length; j++) {
            var u2 = pos.make(rmoves[j]);
            var rs = TB.stateOfPosition(pos);
            pos.unmake(u2);
            if (rs != null) replies.push(rs);
          }
        }
        pos.unmake(undo);
        if (!cv || !cv.won || cv.plies !== D - 1) continue;
        var total = 1;                            // the BTM node b
        for (var k = 0; k < replies.length; k++) {
          total += rec(replies[k], childSpace);
        }
        if (best === null || total < best) best = total;
      }
      if (best === null) return 1;                // safety for D=1 edges
      var val = 1 + best;                         // the WTM node w
      memo.set(key, val);
      return val;
    }
    return rec(state, rootKind);
  };

  /* Per-level growth: how many tree nodes appear within `levels` plies.
     Memoised on (space, state, budget); a work cap keeps deep levels
     responsive (truncated flag reports the cap honestly). */
  TreeExplorer.prototype.levelProfile = function (state) {
    var WORK_CAP = 3000000;          // counted nodes per run
    var memo = new Map();
    var work = 0;
    var truncated = false;

    function countAt(s, budget, space) {
      // nodes of the minimal tree within `budget` plies of the root
      if (budget <= 0) return { nodes: 0, leaf: true };
      var key = space + '|' + s + '|' + budget;
      var hit = memo.get(key);
      if (hit !== undefined) return hit;
      if (work > WORK_CAP) { truncated = true; return { nodes: 0, leaf: true }; }
      work++;
      var t = TB.getLoaded(space);
      var u = TB.unpackState(s);
      var pos = new C.Position().setFromSetup(u.wk, u.wp, u.bk,
                                              t.spec.pieceCode, 1);
      var D = t.probe(s).plies;
      var moves = pos.legalMoves();
      var best = null;
      for (var i = 0; i < moves.length; i++) {
        var undo = pos.make(moves[i]);
        var childSpace = (space === 'kpk' && undo.promo) ? 'kqk' : space;
        var cv = probePos(pos, childSpace);
        var sub = null;
        if (cv && cv.won && cv.plies === D - 1) {
          sub = 1;                                // the BTM node b
          var rmoves = pos.legalMoves();
          for (var j = 0; j < rmoves.length; j++) {
            var u2 = pos.make(rmoves[j]);
            var rs = TB.stateOfPosition(pos);
            pos.unmake(u2);
            var r = rs == null ? { nodes: 0, leaf: true }
                               : countAt(rs, budget - 2, childSpace);
            sub += r.nodes;
          }
        }
        pos.unmake(undo);
        if (sub !== null && (best === null || sub < best)) best = sub;
      }
      var res = best === null ? { nodes: 1, leaf: true }
                              : { nodes: 1 + best, leaf: false };
      memo.set(key, res);
      return res;
    }

    var D = this.tb.probe(state).plies;
    var profile = [];
    for (var lv = 2; lv <= D; lv += 2) {
      var r = countAt(state, lv, this.rootKind);
      profile.push({ plies: lv, nodes: r.nodes,
                     complete: !r.leaf });
      if (r.leaf) break;
    }
    return { profile: profile, truncated: truncated };
  };

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.tree = {
    TreeExplorer: TreeExplorer, spaceOf: spaceOf, probePos: probePos
  };
})(window);
