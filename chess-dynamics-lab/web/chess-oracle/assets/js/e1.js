/* chess-oracle · e1.js
   In-browser replay of experiment E1 (particles vs oracle).

   Protocol (identical to complexity/experiment_particles_vs_oracle.py):
   sample won White-to-move states; let the three-layer greedy ParticleSolver
   choose ONE move; classify against the frozen DTM oracle:
     saved   — the resulting position is still won for White;
     lost    — the move lands in a drawn position (the win is gone forever);
     optimal — the move lands at DTM-1 (the Bellman-optimal choice);
     delta   — the price of greediness: (child DTM) - (position DTM) plies.

   The frozen run (sample 5000, seed 42) measured save-rate 0.8244 (KRK) /
   0.9562 (KQK). The browser run uses its own seeded PRNG, so the numbers
   are an independent measurement — the panel shows both. */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;
  var TB = global.ChessOracle.tb;

  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function sampleWonState(tb, rng) {
    for (var guard = 0; guard < 100000; guard++) {
      var wk = (rng() * 64) | 0, wq = (rng() * 64) | 0,
          bk = (rng() * 64) | 0;
      if (wk === wq || wk === bk || wq === bk) continue;
      var df = Math.abs((wk & 7) - (bk & 7));
      var dr = Math.abs((wk >> 4) - (bk >> 4));
      if (df <= 1 && dr <= 1) continue;
      var pos = new C.Position().setFromSetup(wk, wq, bk,
                                              tb.spec.pieceCode, 1);
      if (pos.attacked(bk, 1)) continue;        // black en prise, WTM
      var state = TB.packState(wk, wq, bk, 0);
      var info = tb.probe(state);
      if (info.won && !info.mate) {
        return { pos: pos, state: state, info: info };
      }
    }
    return null;
  }

  function runE1(tb, count, seed, solver) {
    var rng = mulberry32(seed);
    var saved = 0, lost = 0, optimal = 0;
    var deltaSum = 0, deltaCount = 0, deltaMax = 0;
    var examples = [];
    for (var i = 0; i < count; i++) {
      var s = sampleWonState(tb, rng);
      if (!s) break;
      var m = solver.chooseMove(s.pos);
      if (!m) break;
      var child = TB.probeAfterMove(tb, s.pos, m);
      if (child === null) { i--; continue; }
      if (child.won) {
        saved++;
        var d = child.plies - s.info.plies;
        deltaSum += d; deltaCount++;
        if (d > deltaMax) deltaMax = d;
        if (child.plies === s.info.plies - 1) optimal++;
        if (examples.length < 3 && d >= 6) {
          examples.push({
            fen: s.pos.toFEN(), move: C.sqName(m.f) + C.sqName(m.t),
            dtm_before_moves: (s.info.plies + 1) >> 1,
            dtm_after_moves: (child.plies + 1) >> 1
          });
        }
      } else {
        lost++;
        if (examples.length < 3) {
          examples.push({
            fen: s.pos.toFEN(), move: C.sqName(m.f) + C.sqName(m.t),
            dtm_before_moves: (s.info.plies + 1) >> 1,
            dtm_after_moves: null, lost: true
          });
        }
      }
    }
    var evaluated = saved + lost;
    return {
      count: evaluated, seed: seed, saved: saved, lost: lost,
      save_rate: evaluated ? saved / evaluated : 0,
      optimal_rate: evaluated ? optimal / evaluated : 0,
      mean_delta_plies: deltaCount ? deltaSum / deltaCount : 0,
      max_delta_plies: deltaMax,
      examples: examples,
      frozen: tb.spec.frozenE1
    };
  }

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.e1 = {
    runE1: runE1, sampleWonState: sampleWonState, mulberry32: mulberry32
  };
})(window);
