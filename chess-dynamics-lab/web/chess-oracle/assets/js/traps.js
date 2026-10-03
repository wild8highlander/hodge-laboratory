/* chess-oracle · traps.js — T17: the trap classification, live.

   The frozen DTM certificate assigns every legal move of every position
   a class, by comparing the child value v (plies, EXCLUDING the move
   ply; a KPK promotion child is valued through the frozen KQK
   certificate exactly as in the table build) with the parent value d:

     mover WIN (d plies, the strong side owns the net)
       optimal  v = d-1                the Bellman descent step;
       waste    v >= d                 still won, but ddtm = v-(d-1)
                                       plies thrown away — the exact
                                       per-move quantity E1 measured by
                                       SAMPLING the greedy solver;
       slack    v < 0 (or capture)     the win is gone forever
                                       (win -> draw, E1's "lost");
     mover DRAW, strong side
       keep     every move holds the draw (Bellman: no won child
                                       exists, else the parent would
                                       be won);
     mover DRAW, weak side
       TRAP     v >= 0                 the move turns the draw into a
                                       LOSS (draw -> loss) — the snare
                                       the vortex layer marks J = 1 and
                                       the button highlights in crimson;
       keep     v < 0 or a capture     the drawing resource;
     mover LOSS (d plies to mate)
       resist   v = d-1                the most resistant defence;
       fast     v > d-1                accelerates the mate by
                                       accel = v-(d-1) plies.

   THE POPULATION TWIN: E1 samples (seeded won states, the greedy
   solver, ONE move each); scripts/trap_census.py EXHAUSTS all four
   frozen endgames and counts these classes over every legal state and
   every legal move.  Its aggregates are frozen below (FROZEN) and shown
   next to the live per-position structure — sample against population,
   greedy against exact.

   KNK is the zero control in move-class language: every parent is
   drawn and every child is drawn, so traps = slack = waste = 0 by
   exhaustion (T15). */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;
  var TB = global.ChessOracle.tb;

  /* Frozen by scripts/trap_census.py -> results/trap_census.json.
     btmDrawn: the defender's drawn positions (the trap habitat);
     wtmWon:   the attacker's won positions (the waste/slack habitat). */
  var FROZEN = {
    krk: {
      btmDrawn: { states: 22244, withTraps: 21764,
                  traps: 59624, moves: 1085792,
                  maxTraps: 4, deepestPlies: 31 },
      wtmWon: { states: 175168, moves: 3383416,
                optimalShare: 0.10675, slack: 262240,
                withSlack: 73152, waste: 2759996,
                ddtmMean: 5.8856, ddtmMax: 28 }
    },
    kqk: {
      btmDrawn: { states: 23048, withTraps: 19756,
                  traps: 32896, moves: 899216,
                  maxTraps: 2, deepestPlies: 17 },
      wtmWon: { states: 144508, moves: 3992456,
                optimalShare: 0.105285, slack: 290616,
                withSlack: 111480, waste: 3281496,
                ddtmMean: 3.9296, ddtmMax: 14 }
    },
    knk: {
      btmDrawn: { states: 223944, withTraps: 0,
                  traps: 0, moves: 1252056,
                  maxTraps: 0, deepestPlies: 0 },
      wtmWon: { states: 0, moves: 2291376,
                optimalShare: 0.0, slack: 0,
                withSlack: 0, waste: 0,
                ddtmMean: 0.0, ddtmMax: 0 }
    },
    kpk: {
      btmDrawn: { states: 168024, withTraps: 46054,
                  traps: 173786, moves: 1003214,
                  maxTraps: 7, deepestPlies: 55 },
      wtmWon: { states: 124954, moves: 1166864,
                optimalShare: 0.214282, slack: 181950,
                withSlack: 38644, waste: 469902,
                ddtmMean: 4.1005, ddtmMax: 32 }
    }
  };

  /* Classify every legal move of the current position.
     Returns null when the position is outside the loaded space
     (piece captured -> K vs K), and a terminal record when the game
     is already over (mate / stalemate). */
  function classify(tb, pos) {
    var st = TB.stateOfPosition(pos);
    if (st === null) return { kind: tb.kind, outside: true };
    var info = tb.probe(st);
    var white = pos.side === 1;
    var moves = pos.legalMoves();
    if (!moves.length) {
      return { kind: tb.kind, terminal: true,
               mated: !!info.mate, white: white };
    }
    var d = info.won ? info.plies : null;
    var moverClass = info.won ? (white ? 'WIN' : 'LOSS') : 'DRAW';
    var entries = [], i, m, child, e;
    var counts = { moves: 0, optimal: 0, waste: 0, slack: 0, trap: 0,
                   keep: 0, resist: 0, fast: 0 };
    var ddtmSum = 0, ddtmMax = 0, accelSum = 0, accelMax = 0;
    var deepestTrap = 0;
    for (i = 0; i < moves.length; i++) {
      m = moves[i];
      counts.moves++;
      child = TB.probeAfterMove(tb, pos, m);   // null = capture -> K vs K
      e = { m: m, from: m.f, to: m.t,
            uci: C.sqName(m.f) + C.sqName(m.t),
            child: child, cls: 'keep', ddtm: 0 };
      if (moverClass === 'WIN') {
        if (child === null) { e.cls = 'slack'; }         // defensive
        else if (child.won && child.plies === d - 1) {
          e.cls = 'optimal';
          counts.optimal++;
        } else if (child.won) {
          e.cls = 'waste';
          e.ddtm = child.plies - (d - 1);
          ddtmSum += e.ddtm;
          if (e.ddtm > ddtmMax) ddtmMax = e.ddtm;
          counts.waste++;
        } else {                                          // drawn child
          e.cls = 'slack';
          counts.slack++;
        }
      } else if (moverClass === 'DRAW') {
        if (!white && child !== null && child.won) {
          e.cls = 'trap';
          e.ddtm = child.plies;          // the loss depth after the trap
          if (child.plies > deepestTrap) deepestTrap = child.plies;
          counts.trap++;
        } else {
          e.cls = 'keep';                // draw held (or capture = K vs K)
          counts.keep++;
        }
      } else {                           // LOSS
        if (child !== null && child.won) {
          if (child.plies === d - 1) {
            e.cls = 'resist';
            counts.resist++;
          } else {
            e.cls = 'fast';
            e.ddtm = child.plies - (d - 1);
            accelSum += e.ddtm;
            if (e.ddtm > accelMax) accelMax = e.ddtm;
            counts.fast++;
          }
        } else {
          e.cls = 'keep';                // defensive (Bellman forbids)
          counts.keep++;
        }
      }
      entries.push(e);
    }
    if (moverClass === 'WIN' && counts.optimal === 0) {
      // cannot happen by Bellman (the minimum child sits at d-1)
      throw new Error('traps: won position without an optimal move');
    }
    return {
      kind: tb.kind, white: white, moverClass: moverClass, d: d,
      entries: entries, counts: counts,
      ddtmMean: counts.waste ? ddtmSum / counts.waste : 0,
      ddtmMax: ddtmMax,
      accelMean: counts.fast ? accelSum / counts.fast : 0,
      accelMax: accelMax,
      deepestTrap: deepestTrap,
      frozen: FROZEN[tb.kind] || null,
      frozenE1: tb.spec.frozenE1
    };
  }

  /* squares to highlight on the board, per class (from+to of each
     move); priority trap > slack > waste > resist on collisions */
  function highlightMap(res) {
    var map = {};
    if (!res || !res.entries) return map;
    var prio = { trap: 4, slack: 3, waste: 2, resist: 1 };
    var i, e, cls;
    for (i = 0; i < res.entries.length; i++) {
      e = res.entries[i];
      cls = prio[e.cls] ? e.cls : null;
      if (!cls) continue;
      [e.from, e.to].forEach(function (sq) {
        if (!map[sq] || prio[cls] > prio[map[sq]]) map[sq] = cls;
      });
    }
    return map;
  }

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.traps = {
    FROZEN: FROZEN, classify: classify, highlightMap: highlightMap
  };
})(window);
