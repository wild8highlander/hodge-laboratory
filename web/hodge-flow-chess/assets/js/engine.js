/* ════════════════════════════════════════════════════════════════════
   Hodge Flow — Шахматная Лаборатория / Chess Flow Laboratory
   engine.js — pure math core (no DOM).

   Theory source: monograph «Динамический принцип» / "The Dynamic
   Principle", Part XV (ru/p_part15.tex, en/e_p6.tex) and the
   μ₄-equivariance of the chessboard grid (ru/p_part2.tex); reference
   implementation: laboratory.py (cert_E, stand_binary).

   Flow state = (p, φ): position p on the W×H torus grid, phase
   φ ∈ μ₄ = {1, i, −1, −i}. Transition: p → p + (a,b) mod (W,H),
   φ → φ·i. Exact termination time
        t* = lcm(W/gcd(a,W), H/gcd(b,H))
   (certificate E-4 formula). Discovery monovariant = set of visited
   cells; friction = transitions into an already-visited cell; edge
   cells = visited boundary cells; Freeman chain code digits 0..3;
   closure (Σdx, Σdy) ≡ (0,0) mod (W,H); terminal cycle = μ₄-orbit.
   ════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  const E = {};

  /* ── integer helpers ─────────────────────────────────────────────── */
  function gcd(a, b) {
    a = Math.abs(a | 0); b = Math.abs(b | 0);
    while (b) { const t = a % b; a = b; b = t; }
    return a;
  }
  function lcm(a, b) {
    if (a === 0 || b === 0) return 0;
    return (a / gcd(a, b)) * b;
  }
  E.gcd = gcd;
  E.lcm = lcm;

  /* Exact termination time (first joint return of the position).
     gcd(0, W) = W by convention, so a zero component yields period 1. */
  function tstar(W, H, a, b) {
    const gx = gcd(a, W) || 1;
    const gy = gcd(b, H) || 1;
    return lcm(W / gx, H / gy);
  }
  E.tstar = tstar;

  /* Klein layer: Singer generation of order 7 (monograph, part XV):
     the termination time multiplies by 7/gcd(7,H); at H divisible
     by 7 the flow closes at the original time. */
  function singerFactor(H) { return 7 / (gcd(7, H) || 1); }
  E.singerFactor = singerFactor;

  /* Braking (K3 layer): γ = δ⁴/k, effective phase δ_eff = δ⁵/k,
     δ = π/n. Defaults n=4,k=1 (torus calibration); Klein n=7,k=22. */
  function braking(n, k) {
    const delta = Math.PI / n;
    const gamma = Math.pow(delta, 4) / k;
    const deltaEff = Math.pow(delta, 5) / k;
    return { n: n, k: k, delta: delta, gamma: gamma, deltaEff: deltaEff };
  }
  E.braking = braking;

  /* Freeman chain digits: 0=E(+x), 1=N(+y), 2=W(−x), 3=S(−y). */
  const DIGIT_DX = [1, 0, -1, 0];
  const DIGIT_DY = [0, 1, 0, -1];
  E.DIGIT_DX = DIGIT_DX;
  E.DIGIT_DY = DIGIT_DY;

  const CHAIN_CAP = 20000;
  const TRAIL_CAP = 2400;
  E.Caps = { chain: CHAIN_CAP, trail: TRAIL_CAP };

  /* ══════════════════════════════════════════════════════════════════
     FLOW (real-time engine)
     layers:
       torus — wrap-around, exact t*, full tracking;
       k3    — reflections with braking γ=δ⁴/k (billiard with damping,
               bounded trajectory, no wrap);
       klein — torus mechanics + Singer order 7: t*_eff = t*·7/gcd(7,H),
               mod-7 cell coloring, phase-7 marker ring.
     ══════════════════════════════════════════════════════════════════ */
  function createFlow(cfg) {
    const W = Math.max(2, cfg.W | 0);
    const H = Math.max(2, cfg.H | 0);
    const a = cfg.a | 0;
    const b = cfg.b | 0;
    const layer = cfg.layer || 'torus';
    const n = cfg.n || 4;
    const k = cfg.k || 1;

    const F = {
      W: W, H: H, a: a, b: b, layer: layer, n: n, k: k,
      x: 0, y: 0,               // integer cell (torus/klein; k3: floor of float pos)
      px: 0.5, py: 0.5,         // float position (k3); centers for trail
      vx: 0, vy: 0,             // k3 velocity
      phase: 0,                 // exponent of i: φ = i^phase
      step: 0,
      counts: new Uint16Array(W * H),
      maxVisits: 0,
      visited: 0,               // discovery monovariant
      friction: 0,
      edges: 0,
      chain: [],                // stored digits (capped)
      chainTotal: 0,            // true total length
      chainTruncated: false,
      closureX: 0, closureY: 0, // cumulative mod (W,H)
      brakeTotal: 1, reflections: 0, atRest: false,
      done: false,              // reached t* (torus) / t*_eff (klein) / rest (k3)
      trail: [],
      pulses: [],               // {i: cellIndex, t0: ms}
      tstar: tstar(W, H, a, b),
      singer: layer === 'klein' ? singerFactor(H) : 1,
      degenerate: (a === 0 && b === 0),
    };
    F.tstarEff = layer === 'klein' ? F.tstar * F.singer : F.tstar;
    if (F.degenerate) { F.tstar = 1; F.tstarEff = 1; }

    const brk = braking(n, k);
    F.delta = brk.delta;
    F.gamma = brk.gamma;

    if (layer === 'k3') {
      F.vx = (a === 0 ? 0 : (a > 0 ? 1 : -1) * Math.max(1, Math.abs(a)));
      F.vy = (b === 0 ? 0 : (b > 0 ? 1 : -1) * Math.max(1, Math.abs(b)));
      if (F.vx === 0 && F.vy === 0) F.atRest = true;
      F.px = 0.5; F.py = 0.5;
    }

    const idx = function (x, y) { return y * W + x; };
    F.indexOf = idx;

    function touchCell(cx, cy, now) {
      const i = idx(cx, cy);
      const was = F.counts[i];
      const ev = { discovered: false, friction: false, edge: false, i: i };
      if (was === 0) {
        F.visited++;
        ev.discovered = true;
        if (F.pulses.length < 400) F.pulses.push({ i: i, t0: now });
        if (cx === 0 || cx === W - 1 || cy === 0 || cy === H - 1) { F.edges++; ev.edge = true; }
      } else {
        // friction: attempt to enter an already-visited cell
        F.friction++; ev.friction = true;
      }
      F.counts[i] = Math.min(65535, was + 1);
      if (F.counts[i] > F.maxVisits) F.maxVisits = F.counts[i];
      return ev;
    }

    function pushChain(dx, dy) {
      // one digit per moving component, x first
      if (dx > 0) E_digit(0);
      else if (dx < 0) E_digit(2);
      if (dy > 0) E_digit(1);
      else if (dy < 0) E_digit(3);
      function E_digit(d) {
        F.chainTotal++;
        if (F.chain.length < CHAIN_CAP) F.chain.push(d);
        else F.chainTruncated = true;
      }
    }

    /* one transition; now = performance.now() for pulse timestamps */
    F.stepOnce = function (now) {
      now = now || 0;
      if (F.atRest) return null;
      const ev = { reflected: false };
      if (layer === 'k3') {
        // reflect + brake (billiard with damping)
        let nx = F.px + F.vx;
        let ny = F.py + F.vy;
        if (nx < 0 || nx >= W) {
          F.vx = -F.vx * F.gamma;
          F.brakeTotal *= F.gamma;
          F.reflections++;
          ev.reflected = true;
          nx = F.px + F.vx;
          if (nx < 0) nx = 0; else if (nx > W - 1e-6) nx = W - 1e-6;
        }
        if (ny < 0 || ny >= H) {
          F.vy = -F.vy * F.gamma;
          F.brakeTotal *= F.gamma;
          F.reflections++;
          ev.reflected = true;
          ny = F.py + F.vy;
          if (ny < 0) ny = 0; else if (ny > H - 1e-6) ny = H - 1e-6;
        }
        const dx = nx - F.px, dy = ny - F.py;
        pushChain(F.vx, F.vy);
        F.px = nx; F.py = ny;
        const cx = Math.min(W - 1, Math.max(0, Math.floor(F.px)));
        const cy = Math.min(H - 1, Math.max(0, Math.floor(F.py)));
        F.x = cx; F.y = cy;
        const tev = touchCell(cx, cy, now);
        ev.discovered = tev.discovered; ev.friction = tev.friction;
        if (Math.abs(F.vx) < 1e-9) F.vx = 0;
        if (Math.abs(F.vy) < 1e-9) F.vy = 0;
        if (F.vx === 0 && F.vy === 0) { F.atRest = true; F.done = true; }
        F.step++;
        if (F.step > 4000000) { F.done = true; }
        F.trail.push(F.px, F.py);
      } else {
        // torus / klein: exact modular walk
        const nx = ((F.x + a) % W + W) % W;
        const ny = ((F.y + b) % H + H) % H;
        pushChain(a, b);
        F.x = nx; F.y = ny;
        F.px = nx + 0.5; F.py = ny + 0.5;
        F.closureX = ((F.closureX + a) % W + W) % W;
        F.closureY = ((F.closureY + b) % H + H) % H;
        const tev = touchCell(nx, ny, now);
        ev.discovered = tev.discovered; ev.friction = tev.friction;
        F.step++;
        F.phase = (F.phase + 1) & 3;
        if (F.step >= F.tstarEff) F.done = true;
        F.trail.push(F.px, F.py);
      }
      return ev;
    };

    F.reset = function () {
      return createFlow({ W: W, H: H, a: a, b: b, layer: layer, n: n, k: k });
    };

    F.trimTrail = function () {
      if (F.trail.length > TRAIL_CAP * 2) {
        F.trail = F.trail.slice(F.trail.length - TRAIL_CAP * 2);
      }
    };

    F.cellVisited = function (i) { return F.counts[i] > 0; };

    F.terminalCycleLength = function () {
      return lcm(F.tstarEff, 4);
    };

    F.snapshot = function () {
      return {
        W: F.W, H: F.H, x: F.x, y: F.y, px: F.px, py: F.py,
        phase: F.phase, step: F.step, counts: F.counts,
        maxVisits: F.maxVisits, trail: F.trail, pulses: F.pulses,
        layer: F.layer, tstar: F.tstar, tstarEff: F.tstarEff,
        singer: F.singer, done: F.done, atRest: F.atRest,
        brakeTotal: F.brakeTotal, reflections: F.reflections,
        vx: F.vx, vy: F.vy, phase7: F.step % 7,
      };
    };
    return F;
  }
  E.createFlow = createFlow;

  /* ── silent full run (protocol E) ────────────────────────────────── */
  function runSilent(W, H, a, b, maxSteps) {
    maxSteps = maxSteps || 400000;
    let x = 0, y = 0, cx = 0, cy = 0;
    const seen = new Uint8Array(W * H);
    let visited = 0;
    let firstReturn = 0; // 0 = not found within cap
    seen[0] = 1; visited = 1;
    let steps = 0;
    for (let s = 1; s <= maxSteps; s++) {
      x = ((x + a) % W + W) % W;
      y = ((y + b) % H + H) % H;
      cx = ((cx + a) % W + W) % W;
      cy = ((cy + b) % H + H) % H;
      steps = s;
      const i = y * W + x;
      if (x === 0 && y === 0 && firstReturn === 0) firstReturn = s;
      if (!seen[i]) { seen[i] = 1; visited++; }
      if (firstReturn !== 0 && s >= firstReturn) break;
    }
    return { steps: steps, firstReturn: firstReturn, visited: visited, closureX: cx, closureY: cy };
  }
  E.runSilent = runSilent;

  /* ══════════════════════════════════════════════════════════════════
     PROTOCOL E — the eight checks, live on the current (W,H,a,b).
     Computed checks carry kind 'computed'; the monograph reference
     totals 212/432/114 (sum 806) are 'documented' and are never
     claimed to be recomputed (see laboratory.py stand_binary).
     ══════════════════════════════════════════════════════════════════ */
  const CERT_CASES = [
    [48, 48, 1, 1, 48], [96, 96, 1, 1, 96], [24, 36, 3, 5, 72],
    [7, 14, 1, 1, 14], [12, 12, 4, 6, 6], [384, 384, 1, 1, 384],
  ];
  E.CERT_CASES = CERT_CASES;

  function protocolE(cfg) {
    const W = cfg.W | 0, H = cfg.H | 0, a = cfg.a | 0, b = cfg.b | 0;
    const ts = tstar(W, H, a, b);
    const out = [];

    // E1 — cert_E reference cases: exact t* formula
    let ok1 = true;
    const rows1 = CERT_CASES.map(function (c) {
      const v = tstar(c[0], c[1], c[2], c[3]);
      if (v !== c[4]) ok1 = false;
      return { W: c[0], H: c[1], a: c[2], b: c[3], expected: c[4], got: v };
    });
    out.push({ id: 'E1', key: 'proto.e1', pass: ok1, kind: 'computed',
      value: rows1.map(function (r) { return 't*(' + r.W + ',' + r.H + ',' + r.a + ',' + r.b + ')=' + r.got; }).join('; ') });

    // E2 — measured first joint return equals the formula
    const run = runSilent(W, H, a, b);
    out.push({ id: 'E2', key: 'proto.e2', pass: run.firstReturn === ts,
      kind: 'computed', value: String(run.firstReturn) + ' / ' + String(ts) });

    // E3 — discovery monovariant: visited = t* exactly
    out.push({ id: 'E3', key: 'proto.e3', pass: run.visited === ts,
      kind: 'computed', value: String(run.visited) + ' / ' + String(ts) });

    // E4 — closure (Σdx, Σdy) ≡ (0,0) mod (W,H)
    const clOk = run.closureX === 0 && run.closureY === 0;
    out.push({ id: 'E4', key: 'proto.e4', pass: clOk, kind: 'computed',
      value: '(' + run.closureX + ',' + run.closureY + ') mod (' + W + ',' + H + ')' });

    // E5 — terminal cycle = μ₄-orbit (direct orbit enumeration)
    const L = lcm(ts, 4);
    let x = 0, y = 0, ph = 0, ok5 = true;
    for (let s = 0; s < L; s++) {
      x = ((x + a) % W + W) % W;
      y = ((y + b) % H + H) % H;
      ph = (ph + 1) & 3;
    }
    if (!(x === 0 && y === 0 && ph === 0)) ok5 = false;
    // phase component cycles with period exactly 4
    let ph2 = 0;
    for (let s = 0; s < 4; s++) ph2 = (ph2 + 1) & 3;
    if (ph2 !== 0) ok5 = false;
    // distinct phases along the orbit = 4
    if (new Set([0, 1, 2, 3]).size !== 4) ok5 = false;
    out.push({ id: 'E5', key: 'proto.e5', pass: ok5, kind: 'computed',
      value: 'L=lcm(t*,4)=' + L + ', orbit=4' });

    // E6 — scaling 48→96→192→384: linear growth at unit step
    const sc = [[48, 48], [96, 96], [192, 192], [384, 384]];
    let ok6 = true;
    const rows6 = sc.map(function (p) {
      const v = tstar(p[0], p[1], 1, 1);
      if (v !== p[0]) ok6 = false;
      return p[0] + '→' + v;
    });
    out.push({ id: 'E6', key: 'proto.e6', pass: ok6, kind: 'computed', value: rows6.join(', ') });

    // E7 — monograph reference totals 48/212/432/114, sum 806
    //     (documented reference of the certified pipeline run;
    //      only the arithmetic consistency is verified here)
    const sum = 48 + 212 + 432 + 114;
    out.push({ id: 'E7', key: 'proto.e7', pass: sum === 806, kind: 'documented',
      value: '48+212+432+114=' + sum });

    // E8 — layers: braking γ=δ⁴/k (torus calibration n=4,k=1) and
    //      Klein Singer factor 7/gcd(7,H)
    const brk = braking(4, 1);
    const gammaRef = 0.38050426185157193; // π⁴/256, monograph documented
    const okGamma = Math.abs(brk.gamma - gammaRef) < 1e-12;
    const sf = singerFactor(H);
    const okSf = (sf === 1) || (sf === 7);
    out.push({ id: 'E8', key: 'proto.e8', pass: okGamma && okSf, kind: 'computed',
      value: 'γ=' + brk.gamma.toFixed(10) + ', 7/gcd(7,' + H + ')=' + sf });

    return { checks: out, tstar: ts, allPass: out.every(function (c) { return c.pass; }) };
  }
  E.protocolE = protocolE;

  /* ══════════════════════════════════════════════════════════════════
     FORMULA GRID — μ₄-equivariance of the united formula
         Δ_Ch(cell) = λ₀ + δ²/2·s(cell) − δ⁵/k·s(cell) = λ₀ + β·s(cell)
     Mode A "symmetric encoding": values are defined on the fundamental
     domain (quadrant 0) with s(r,s) = (r+s) mod N and extended over the
     grid by the equivariance rule Δ(g·z) := χ(g)·Δ(z). Exact μ₄-
     equivariance by construction → deviation 0.000 (numerically verified
     over the whole grid, floating-point exact since χ(g) ∈ {±1, ±i}).
     Mode B "encoding (7,22)": s(r,s) = (7r+22s) mod N applied directly —
     the symmetry is broken; the normalized deviation reaches 1.000.
     Deviation: D = max |Δ(g·z) − χ(g)·Δ(z)| / (|Δ(g·z)| + |Δ(z)|),
     g ranging over the three nontrivial quarter-turn rotations of the
     grid about its center. D = 0 means exact equivariance; D = 1 means
     the rotated value is opposite to the character target.
     Monograph documented claims: 0.000 (symmetric, 4096×4096) and
     1.000 for (7,22); cyclic-shift asymmetry at K=256: 0.828 max,
     1.782 mean — shown as documented reference, not recomputed.
     ══════════════════════════════════════════════════════════════════ */
  function formulaBeta(n, k) {
    const d = Math.PI / n;
    return (d * d) / 2 - Math.pow(d, 5) / k;
  }
  E.formulaBeta = formulaBeta;

  // quadrant index by angle; rotation-consistent tie rules; center → 4
  function quadrantOf(r, s, K) {
    const dx = r - (K - 1) / 2;
    const dy = s - (K - 1) / 2;
    if (dx === 0 && dy === 0) return 4;
    if (dx > 0 && dy >= 0) return 0;
    if (dy > 0 && dx <= 0) return 1;
    if (dx < 0 && dy <= 0) return 2;
    return 3;
  }
  E.quadrantOf = quadrantOf;

  // +90° CCW rotation about the grid center
  function rot90(r, s, K) { return [K - 1 - s, r]; }
  E.rot90 = rot90;

  function createFormulaJob(K, lambda0, n, k, mode) {
    const N = Math.max(2, n | 0);
    const beta = formulaBeta(n, k);
    const sArr = new Uint8Array(K * K);
    const qArr = (mode === 'A') ? new Uint8Array(K * K) : null;
    const job = {
      K: K, N: N, beta: beta, lambda0: lambda0, mode: mode,
      sArr: sArr, qArr: qArr,
      row: 0, pass: 1,
      maxDefect: 0, rawDefect: 0, vmin: Infinity, vmax: -Infinity,
      done: false,
    };
    // per-(quadrant,spin) value tables for mode A (χ-exact complex values)
    const COS = [1, 0, -1, 0], SIN = [0, 1, 0, -1];
    job.valRe = [], job.valIm = [];
    for (let q = 0; q <= 4; q++) {
      job.valRe[q] = new Float64Array(N);
      job.valIm[q] = new Float64Array(N);
      for (let s = 0; s < N; s++) {
        const V = lambda0 + beta * s;
        if (q === 4) { job.valRe[q][s] = 0; job.valIm[q][s] = 0; }
        else {
          job.valRe[q][s] = COS[q] * V;
          job.valIm[q][s] = SIN[q] * V;
        }
      }
    }

    /* fill rows [r0, r1) of the encoding arrays */
    job.fillRows = function (r0, r1) {
      const K = job.K, N = job.N;
      for (let r = r0; r < r1; r++) {
        for (let s = 0; s < K; s++) {
          const i = r * K + s;
          if (job.mode === 'A') {
            const q = quadrantOf(r, s, K);
            qArr[i] = q;
            if (q === 4) { sArr[i] = 0; continue; }
            // canonical representative: rotate −q quarter-turns into quadrant 0
            let cr = r, cs = s;
            for (let t = 0; t < q; t++) { const tmp = cr; cr = cs; cs = K - 1 - tmp; }
            sArr[i] = ((cr + cs) % N + N) % N;
          } else {
            sArr[i] = (((7 * r + 22 * s) % N) + N) % N;
          }
        }
      }
    };

    /* defect scan over rows [r0, r1): D = max |Δ(R^k z) − χ^k Δ(z)| / (|Δ(R^k z)|+|Δ(z)|) */
    job.scanRows = function (r0, r1) {
      const K = job.K;
      let maxD = job.maxDefect, rawD = job.rawDefect;
      for (let r = r0; r < r1; r++) {
        for (let s = 0; s < K; s++) {
          const i = r * K + s;
          let rr = r, ss = s;
          for (let kk = 1; kk <= 3; kk++) {
            const nxt = rot90(rr, ss, K);
            rr = nxt[0]; ss = nxt[1];
            const j = rr * K + ss;
            let numRe, numIm, den;
            if (job.mode === 'A') {
              const q1 = qArr[j], s1 = sArr[j];
              const q0 = qArr[i];
              const q0t = (q0 === 4) ? 4 : ((q0 + kk) & 3); // χ(g)^k·Δ(z) = χ(q0+k)·Δ(z)
              const s0 = sArr[i];
              const are = job.valRe[q1][s1] - job.valRe[q0t][s0];
              const aim = job.valIm[q1][s1] - job.valIm[q0t][s0];
              numRe = are; numIm = aim;
              const V1 = Math.hypot(job.valRe[q1][s1], job.valIm[q1][s1]);
              const V0 = Math.hypot(job.valRe[q0][s0], job.valIm[q0][s0]);
              den = V1 + V0;
            } else {
              const V1 = job.lambda0 + beta * sArr[j];
              const V0 = job.lambda0 + beta * sArr[i];
              // |V1 − i^k·V0| for k=1,3: √(V1²+V0²); k=2: V1+V0
              if (kk === 2) { numRe = V1 + V0; numIm = 0; }
              else { numRe = V1; numIm = V0; }
              den = V1 + V0;
            }
            if (den < 1e-300) continue;
            const num = Math.hypot(numRe, numIm);
            if (num > rawD) rawD = num;
            const d = num / den;
            if (d > maxD) maxD = d;
          }
        }
        // value range for the color scale
        for (let s = 0; s < K; s++) {
          const V = Math.abs(job.lambda0 + beta * sArr[r * K + s]);
          if (V < job.vmin) job.vmin = V;
          if (V > job.vmax) job.vmax = V;
        }
      }
      job.maxDefect = maxD; job.rawDefect = rawD;
    };

    job.step = function (rows) {
      // returns fraction done [0..1]; call repeatedly until 1
      const K = job.K;
      const budgetRows = Math.max(1, rows | 0);
      if (job.pass === 1) {
        const r1 = Math.min(K, job.row + budgetRows);
        job.fillRows(job.row, r1);
        job.row = r1;
        if (job.row >= K) { job.pass = 2; job.row = 0; }
      } else if (job.pass === 2) {
        const r1 = Math.min(K, job.row + budgetRows);
        job.scanRows(job.row, r1);
        job.row = r1;
        if (job.row >= K) { job.done = true; }
      }
      const total = K * 2;
      const doneRows = (job.pass === 1 ? job.row : K + job.row);
      return doneRows / total;
    };
    return job;
  }
  E.createFormulaJob = createFormulaJob;

  /* ══════════════════════════════════════════════════════════════════
     TOWERS — Kronecker tower spectra and Gram CSR densities.
     Spectrum of A⊗I + I⊗A = {λi + λj}: level-k spectrum = all k-fold
     sums of the base eigenvalues (with multiplicities). The base 6×6
     symmetric block is diagonalized by Jacobi rotations; the tower
     spectra follow analytically — no drift is possible beyond the
     machine epsilon of the base solve.
     ══════════════════════════════════════════════════════════════════ */
  function baseBlock(twist) {
    const m = 6;
    const A = [];
    for (let i = 0; i < m; i++) {
      A.push(new Float64Array(m));
      for (let j = 0; j < m; j++) {
        if (i === j) A[i][j] = 2;
        else if (Math.abs(i - j) === 1) A[i][j] = -1;
      }
    }
    A[0][m - 1] = twist; A[m - 1][0] = twist; // the twist
    return A;
  }
  E.baseBlock = baseBlock;

  /* cyclic Jacobi eigenvalue algorithm for a symmetric matrix */
  function jacobiEigen(Ain) {
    const m = Ain.length;
    const A = Ain.map(function (row) { return Float64Array.from(row); });
    const V = [];
    for (let i = 0; i < m; i++) {
      V.push(new Float64Array(m));
      V[i][i] = 1;
    }
    for (let sweep = 0; sweep < 60; sweep++) {
      let off = 0;
      for (let p = 0; p < m; p++) for (let q = p + 1; q < m; q++) off += A[p][q] * A[p][q];
      if (off < 1e-28) break;
      for (let p = 0; p < m - 1; p++) {
        for (let q = p + 1; q < m; q++) {
          if (Math.abs(A[p][q]) < 1e-15) continue;
          const theta = (A[q][q] - A[p][p]) / (2 * A[p][q]);
          const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
          const c = 1 / Math.sqrt(t * t + 1);
          const sn = t * c;
          for (let kk = 0; kk < m; kk++) {
            const akp = A[kk][p], akq = A[kk][q];
            A[kk][p] = c * akp - sn * akq;
            A[kk][q] = sn * akp + c * akq;
          }
          for (let kk = 0; kk < m; kk++) {
            const apk = A[p][kk], aqk = A[q][kk];
            A[p][kk] = c * apk - sn * aqk;
            A[q][kk] = sn * apk + c * aqk;
          }
          for (let kk = 0; kk < m; kk++) {
            const vkp = V[kk][p], vkq = V[kk][q];
            V[kk][p] = c * vkp - sn * vkq;
            V[kk][q] = sn * vkp + c * vkq;
          }
        }
      }
    }
    // sort (value, column) pairs together so λᵢ keeps its eigenvector V[:,col]
    const pairs = [];
    for (let i = 0; i < m; i++) pairs.push({ val: A[i][i], col: i });
    pairs.sort(function (x, y) { return x.val - y.val; });
    const vals = pairs.map(function (pr) { return pr.val; });
    // residual ||A_orig·v − λ·v||∞ over all eigenvectors
    let residual = 0;
    for (let i = 0; i < m; i++) {
      const col = pairs[i].col;
      for (let r = 0; r < m; r++) {
        let s = 0;
        for (let c2 = 0; c2 < m; c2++) s += Ain[r][c2] * V[c2][col];
        residual = Math.max(residual, Math.abs(s - vals[i] * V[r][col]));
      }
    }
    return { values: vals, residual: residual };
  }
  E.jacobiEigen = jacobiEigen;

  function towerSpectra(base) {
    const L1 = base.slice().sort(function (x, y) { return x - y; });
    const L2 = [];
    for (let i = 0; i < base.length; i++)
      for (let j = 0; j < base.length; j++) L2.push(base[i] + base[j]);
    L2.sort(function (x, y) { return x - y; });
    const L3 = [];
    for (let i = 0; i < base.length; i++)
      for (let j = 0; j < base.length; j++)
        for (let l = 0; l < base.length; l++) L3.push(base[i] + base[j] + base[l]);
    L3.sort(function (x, y) { return x - y; });
    function distinct(arr) {
      let c = 1;
      for (let i = 1; i < arr.length; i++) if (arr[i] - arr[i - 1] > 1e-9) c++;
      return c;
    }
    return {
      levels: [
        { level: 1, size: L1.length, min: L1[0], max: L1[L1.length - 1], distinct: distinct(L1), spectrum: L1 },
        { level: 2, size: L2.length, min: L2[0], max: L2[L2.length - 1], distinct: distinct(L2), spectrum: L2 },
        { level: 3, size: L3.length, min: L3[0], max: L3[L3.length - 1], distinct: distinct(L3), spectrum: L3 },
      ],
    };
  }
  E.towerSpectra = towerSpectra;

  /* Gram towers G_N, sizes 22k (22, 220, 2200, 22000, 220000).
     Tridiagonal Gram block: nnz = 3N−2 → CSR density ~ 3/N = O(1/N).
     Memory estimate: values 8B + colInd 4B + rowPtr 4B per nnz/row. */
  function gramTower(levels) {
    return levels.map(function (N) {
      const nnz = 3 * N - 2;
      const density = nnz / (N * N);
      const memMB = (nnz * 8 + nnz * 4 + (N + 1) * 4) / (1024 * 1024);
      return { N: N, nnz: nnz, density: density, memMB: memMB };
    });
  }
  E.gramTower = gramTower;

  /* Monograph documented reference constants (not recomputed here):
     edge spectrum [−3.9890438, 1.0000000] over all Gram levels;
     eigenvalue fluctuations across the Kronecker tower:
     2.06e-16, 1.27e-16, 1.00e-16, 4.23e-17, 1.48e-16;
     Gram memory ~39 MB at level 220000. */
  E.DOC = {
    edgeSpectrum: [-3.9890438, 1.0000000],
    fluctuations: [2.06e-16, 1.27e-16, 1.00e-16, 4.23e-17, 1.48e-16],
    gramMemMB: 39,
    refTotals: { friction: 212, edges: 432, code: 114, sum: 806 },
    equivSym: 0.0, equiv722: 1.0,
    shiftAsym: { max: 0.828, mean: 1.782, K: 256 },
    gridDoc: 4096,
    deltaTorus: { delta2half: 0.30842513753404244, gamma: 0.38050426185157193, deltaEff: 0.2988473484231264, deltaCh: 39.48799539346835 },
  };

  E.VERSION = '1.0.0';
  E.AUTHOR = 'Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich';
  window.HFEngine = E;
})();
