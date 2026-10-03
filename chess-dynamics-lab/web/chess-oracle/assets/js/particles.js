/* chess-oracle · particles.js
   Faithful JS port of the three-layer greedy ParticleSolver
   (complexity/generalized_chess.py). KNOWS NOTHING ABOUT DTM TABLES.

   score(m) = [material(s) - material(-s)]                    (potential)
            + mu * [pseudoMobility(s) - pseudoMobility(-s)]   (kinetic)
            + lam * mean_{c in K(-s)} Theta_s[c]              (K3 pressure)

   mu = 0.1 (T05), lam = 0.25 (K3 weight); Theta_s uses blocking attacks;
   the enemy-king neighbourhood K(-s) = king square + its 8 neighbours.
   Deterministic lexicographic UCI tie-break (KLEIN determinism). */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;

  function ParticleSolver(mu, lam) {
    this.mu = (mu === undefined) ? 0.1 : mu;
    this.lam = (lam === undefined) ? 0.25 : lam;
  }

  ParticleSolver.prototype.meanPressure = function (pos, side) {
    var theta = pos.threatField(side);
    var ek = pos.kingSquare(-side);
    var cells = [ek], i, t;
    for (i = 0; i < 8; i++) {
      t = ek + C.DIR_KING[i];
      if (C.onBoard(t)) cells.push(t);
    }
    var sum = 0;
    for (i = 0; i < cells.length; i++) sum += theta[cells[i]];
    return sum / cells.length;
  };

  ParticleSolver.prototype.scoreAfter = function (pos, m) {
    var s = pos.side;
    var undo = pos.make(m);
    var mat = pos.material(s) - pos.material(-s);
    var mob = pos.pseudoMobility(s) - pos.pseudoMobility(-s);
    var pressure = this.meanPressure(pos, s);
    pos.unmake(undo);
    return mat + this.mu * mob + this.lam * pressure;
  };

  ParticleSolver.prototype.chooseMove = function (pos) {
    var moves = pos.legalMoves();
    if (moves.length === 0) return null;
    var best = null, bestScore = null, bestUci = null;
    for (var i = 0; i < moves.length; i++) {
      var sc = this.scoreAfter(pos, moves[i]);
      var uci = C.sqName(moves[i].f) + C.sqName(moves[i].t);
      if (best === null || sc > bestScore ||
          (sc === bestScore && uci < bestUci)) {
        best = moves[i]; bestScore = sc; bestUci = uci;
      }
    }
    return best;
  };

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.particles = { ParticleSolver: ParticleSolver };
})(window);
