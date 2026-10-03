/* chess-oracle · vortex.js — the T16 vortex-value correspondence, live.

   The frozen DTM certificate is re-encoded as a planar flow on the board:

     vortices   fixed-circulation rotation centres at the three pieces —
                pure rotation, the "eternal swirl" of drawn positions;
     currents   one per legal move, classified by the child value read
                from the loaded tablebase (child value EXCLUDES the move
                ply; promotion children are valued through the frozen KQK
                certificate exactly like the table build):
                  escape   child drawn / piece captured — a closed orbit,
                           the drawing resource (J = 0);
                  descent  child won, value descends the Lyapunov ladder
                           (J = d - v >= 1) — the net pulls;
                  neutral  child won, no progress (weak current J = 0.5,
                           still inside the basin);
                  trap     a blunder current of the DEFENDER in a drawn
                           position (J = 1) — the snare E1 measures.

   THE ANSWER TO THE OUTCOME QUESTION, AS FLOW TOPOLOGY:
     WIN  100%  — descent currents exist, the mover owns the net, every
                  metric trajectory is captured (capture_fraction = 1);
     DRAW       — a drawing resource exists: closed orbits survive, the
                  drawn positions never develop a forced current;
     LOSS       — the same net, but every defence feeds it: all targets
                  descend, the defender is swept in.

   The METRIC ensemble (the classifier) integrates the damped gradient
   flow of the value — the lower envelope of cones U = min_t J*|x-c_t| —
   whose only minima are the targets themselves; the VISUAL layer adds
   the vortices and the in-basin swirl suppression so that captured
   trajectories spiral (the eye of the storm collapses onto the sink)
   while drawn positions keep closed orbits forever.

   Constants and classification gates are frozen by experiment E4
   (results/vortex_e4.json): 1800/1800 agreement with the tables,
   capture separation 1.000 / 0.000, robust to +-20% perturbations. */

(function (global) {
  'use strict';

  var C = global.ChessOracle.chess;
  var TB = global.ChessOracle.tb;

  var FROZEN = {
    gamma: 0.90,          // vortex circulation (visual layer)
    kappa: 3.20,          // descent-current gain
    j_neutral: 0.50,      // weak current of a won-but-not-descending move
    zeta: 2.00,           // in-basin damping
    swirl_gate: 3.00,     // swirl suppression inside a basin
    dt: 0.02,
    steps: 1100,
    n_particles: 144,     // 12x12 metric lattice
    capture_radius: 0.30,
    capture_hold: 20,
    win_capture_min: 0.98,
    draw_capture_max: 0.98,
    cone_eps: 0.15,
    view_particles: 260   // visual ensemble (jittered lattice)
  };

  function sqCenter(s) { return { x: (s & 7) + 0.5, y: (s >> 4) + 0.5 }; }

  /* ── field construction (mirrors vortex/vortex_dynamics.build_field) ── */
  function buildField(tb, pos) {
    var wk = pos.kingSquare(1), bk = pos.kingSquare(-1),
        wp = pos.strongSquare();
    if (wk < 0 || bk < 0 || wp < 0) return null;
    var state = TB.stateOfPosition(pos);
    if (state === null) return null;               // K vs K: outside spaces
    var stm = pos.side === 1 ? 0 : 1;
    var parent = tb.probe(state);
    var currents = [], escapes = 0, descents = 0;
    var moves = pos.legalMoves();
    var i, m, child, J;

    if (stm === 1 && parent.mate) {
      // checkmate on the board: the terminal sink, no dynamics left
      return { kind: tb.kind, wk: wk, wp: wp, bk: bk, stm: stm,
               verdict: 'LOSS', dtm: 0, terminal: true,
               currents: [], escapes: 0, descents: 0,
               vortices: [{ sq: wk, g: FROZEN.gamma },
                          { sq: bk, g: FROZEN.gamma },
                          { sq: wp, g: FROZEN.gamma }] };
    }

    for (i = 0; i < moves.length; i++) {
      m = moves[i];
      child = TB.probeAfterMove(tb, pos, m);       // null = capture -> K vs K
      if (stm === 0) {                             // strong side to move
        if (parent.won && child !== null && child.won) {
          if (child.plies < parent.plies) {
            J = parent.plies - child.plies;        // >= 1 by Bellman
            descents++;
            currents.push({ from: m.f, to: m.t, J: J, tag: 'descent' });
          } else {
            currents.push({ from: m.f, to: m.t, J: FROZEN.j_neutral,
                            tag: 'neutral' });
          }
        } else {
          escapes++;
          currents.push({ from: m.f, to: m.t, J: 0, tag: 'escape' });
        }
      } else {                                     // weak side to move
        if (parent.won) {
          if (child !== null && child.won) {
            J = parent.plies - child.plies;
            descents++;
            currents.push({ from: m.f, to: m.t, J: J, tag: 'descent' });
          } else {
            escapes++;                             // would contradict Bellman
            currents.push({ from: m.f, to: m.t, J: 0, tag: 'escape' });
          }
        } else {
          if (child !== null && child.won) {
            currents.push({ from: m.f, to: m.t, J: 1, tag: 'trap' });
          } else {
            escapes++;
            currents.push({ from: m.f, to: m.t, J: 0, tag: 'escape' });
          }
        }
      }
    }

    var verdict;
    if (stm === 0) verdict = descents > 0 ? 'WIN' : 'DRAW';
    else verdict = (escapes > 0 || descents === 0) ? 'DRAW' : 'LOSS';

    return { kind: tb.kind, wk: wk, wp: wp, bk: bk, stm: stm,
             verdict: verdict,
             dtm: parent.won ? parent.plies : null,
             terminal: false,
             currents: currents, escapes: escapes, descents: descents,
             vortices: [{ sq: wk, g: FROZEN.gamma },
                        { sq: bk, g: FROZEN.gamma },
                        { sq: wp, g: FROZEN.gamma }] };
  }

  /* ── metric ensemble: damped gradient flow on min_t J*|x - c_t| ─────── */
  function simulate(field) {
    var forced = [], i;
    for (i = 0; i < field.currents.length; i++) {
      var cur = field.currents[i];
      if ((cur.tag === 'descent' || cur.tag === 'neutral') && cur.J > 0) {
        forced.push({ c: sqCenter(cur.to), J: cur.J });
      }
    }
    var n = FROZEN.n_particles, side = 12, m = forced.length;
    var xs = new Float64Array(n * 2), vs = new Float64Array(n * 2);
    var x0 = new Float64Array(n * 2);
    var stepX = 7.5 / (side - 1), k, r, c;
    for (var iy = 0; iy < side; iy++) {
      for (var ix = 0; ix < side; ix++) {
        k = iy * side + ix;
        xs[k * 2] = 0.25 + ix * stepX;
        xs[k * 2 + 1] = 0.25 + iy * stepX;
        x0[k * 2] = xs[k * 2]; x0[k * 2 + 1] = xs[k * 2 + 1];
      }
    }
    var captured = new Uint8Array(n), hold = new Uint32Array(n);
    if (m > 0) {
      var cx = new Float64Array(m), cy = new Float64Array(m),
          Jv = new Float64Array(m);
      for (i = 0; i < m; i++) { cx[i] = forced[i].c.x; cy[i] = forced[i].c.y;
                               Jv[i] = forced[i].J; }
      var rCap2 = FROZEN.capture_radius * FROZEN.capture_radius;
      for (var s = 0; s < FROZEN.steps; s++) {
        var allCap = true;
        for (k = 0; k < n; k++) {
          if (captured[k]) continue;
          // owning target: argmin_t J_t * |x - c_t|
          var best = -1, bestW = Infinity, bx = 0, by = 0, bd = 0;
          for (r = 0; r < m; r++) {
            var dx = xs[k * 2] - cx[r], dy = xs[k * 2 + 1] - cy[r];
            var d2 = dx * dx + dy * dy, w = Jv[r] * Math.sqrt(d2);
            if (w < bestW) { bestW = w; best = r;
                             bx = -dx; by = -dy; bd = Math.sqrt(d2); }
          }
          var inv = 1 / (bd + FROZEN.cone_eps);
          var ax = FROZEN.kappa * Jv[best] * bx * inv;
          var ay = FROZEN.kappa * Jv[best] * by * inv;
          var zt = FROZEN.zeta * Jv[best];
          vs[k * 2] += (ax - zt * vs[k * 2]) * FROZEN.dt;
          vs[k * 2 + 1] += (ay - zt * vs[k * 2 + 1]) * FROZEN.dt;
          xs[k * 2] += vs[k * 2] * FROZEN.dt;
          xs[k * 2 + 1] += vs[k * 2 + 1] * FROZEN.dt;
          if (xs[k * 2] < 0) xs[k * 2] = 0;
          if (xs[k * 2] > 8) xs[k * 2] = 8;
          if (xs[k * 2 + 1] < 0) xs[k * 2 + 1] = 0;
          if (xs[k * 2 + 1] > 8) xs[k * 2 + 1] = 8;
          var hMin2 = Infinity;
          for (r = 0; r < m; r++) {
            var ex = xs[k * 2] - cx[r], ey = xs[k * 2 + 1] - cy[r];
            var q = ex * ex + ey * ey;
            if (q < hMin2) hMin2 = q;
          }
          if (hMin2 < rCap2) hold[k]++;
          if (hold[k] >= FROZEN.capture_hold) captured[k] = 1;
          else allCap = false;
        }
        if (allCap) break;
      }
    }
    var nCap = 0, freeR = 0, drift = 0, nFree = 0;
    for (k = 0; k < n; k++) {
      if (captured[k]) { nCap++; continue; }
      nFree++;
      var dMin = Infinity;
      for (r = 0; r < m; r++) {
        var fx = xs[k * 2] - cx[r], fy = xs[k * 2 + 1] - cy[r];
        var d2f = fx * fx + fy * fy;
        if (d2f < dMin) dMin = d2f;
      }
      freeR += m > 0 ? Math.sqrt(dMin)
                     : Math.sqrt((xs[k * 2] - 4) * (xs[k * 2] - 4) +
                                 (xs[k * 2 + 1] - 4) * (xs[k * 2 + 1] - 4));
      drift += Math.sqrt((xs[k * 2] - x0[k * 2]) * (xs[k * 2] - x0[k * 2]) +
                         (xs[k * 2 + 1] - x0[k * 2 + 1]) *
                         (xs[k * 2 + 1] - x0[k * 2 + 1]));
    }
    return { n_particles: n, n_targets: m,
             capture_fraction: nCap / n,
             mean_free_radius: nFree ? freeR / nFree : 0,
             net_drift: nFree ? drift / nFree : 0 };
  }

  /* ── flow-only classifier (mirrors classify_by_flow) ────────────────── */
  function classify(field, metrics) {
    var gateOk = true;
    if (field.terminal) return { cls: 'LOSS', gateOk: true, terminal: true };
    if (field.stm === 0) {
      if (field.descents > 0) {
        if (metrics.capture_fraction < FROZEN.win_capture_min) gateOk = false;
        return { cls: 'WIN', gateOk: gateOk };
      }
      return { cls: 'DRAW', gateOk: true };
    }
    if (field.escapes > 0) {
      if (metrics.capture_fraction >= FROZEN.draw_capture_max) gateOk = false;
      return { cls: 'DRAW', gateOk: gateOk };
    }
    if (field.descents > 0) {
      if (metrics.capture_fraction < FROZEN.win_capture_min) gateOk = false;
      return { cls: 'LOSS', gateOk: gateOk };
    }
    return { cls: 'DRAW', gateOk: true };
  }

  global.ChessOracle = global.ChessOracle || {};
  global.ChessOracle.vortex = {
    FROZEN: FROZEN, buildField: buildField, simulate: simulate,
    classify: classify, sqCenter: sqCenter
  };
})(window);
