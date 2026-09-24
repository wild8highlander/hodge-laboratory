/* ══════════════════════════════════════════════════════════════════════
   HODGE LABORATORY WEB — fermat.js
   Faithful web port of the computational core of laboratory.py
   (protocol V1–V9 layer): census, closed period forms, tanh–sinh
   quadratures, radical constants b_Ch, the cyclotomic exact layer.

   Depends on precise.js (globalThis.Precise).
   ══════════════════════════════════════════════════════════════════════ */
(function (global) {
  'use strict';
  const P = global.Precise;
  const F = {};

  /* ── integer helpers ──────────────────────────────────────────────── */
  function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { const t = a % b; a = b; b = t; } return a; }
  F.gcd = gcd;
  F.lcm = (a, b) => (a === 0 || b === 0) ? 0 : Math.abs(a / gcd(a, b) * b);
  F.lcmBig = (a, b) => (a === 0n || b === 0n) ? 0n : (a < 0n ? -a : a) / _bgcd(a, b) * (b < 0n ? -b : b);
  function _bgcd(a, b) { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) { const t = a % b; a = b; b = t; } return a; }

  /* ── V1: conductor census (two independent schemes) ───────────────── */
  F.census = function (N) {
    const h = new Map(), byD = new Map();
    for (let a = 1; a < N; a++) {
      for (let b = 1; b < N - a; b++) {
        const d = N / gcd(gcd(N, a), b);
        h.set(d, (h.get(d) || 0) + 1);
        if (!byD.has(d)) byD.set(d, []);
        byD.get(d).push([a, b]);
      }
    }
    const genus = (N - 1) * (N - 2) / 2;
    const hObj = {}, bdObj = {};
    [...h.keys()].sort((x, y) => x - y).forEach(d => { hObj[d] = h.get(d); bdObj[d] = byD.get(d); });
    return { h: hObj, byD: bdObj, genus };
  };
  F.mobius = function (m) {
    if (m === 1) return 1;
    let result = 1, x = m;
    for (let q = 2; q * q <= x; q++) {
      if (x % q === 0) { x /= q; if (x % q === 0) return 0; result = -result; }
    }
    if (x > 1) result = -result;
    return result;
  };
  F.censusMobius = function (N) {
    const c = k => k >= 3 ? (k - 1) * (k - 2) / 2 : 0;
    const out = {};
    for (let d = 2; d <= N; d++) {
      if (N % d) continue;
      let s = 0;
      for (let m = 1; m <= d; m++) if (d % m === 0) s += F.mobius(m) * c(d / m);
      out[d] = s;
    }
    const filtered = {};
    for (const d of Object.keys(out)) if (out[d]) filtered[d] = out[d];
    return filtered;
  };

  /* ── closed period forms ──────────────────────────────────────────── */
  F.omegaClosed = function (N, a, b) {
    // Ω_{a,b} = Γ(a/N)Γ(b/N)/Γ((a+b)/N)  — real positive for a,b > 0
    const ga = P.gamma(P.div(P.ofInt(a), P.ofInt(N)));
    const gb = P.gamma(P.div(P.ofInt(b), P.ofInt(N)));
    const gab = P.gamma(P.div(P.ofInt(a + b), P.ofInt(N)));
    return P.div(P.mul(ga, gb), gab);
  };
  F.periodClosed = function (N, a, b, r, s) {
    // P = (1/N)·ζ^{ra+sb}·Ω_{a,b},  ζ = e^{2πi/N}
    const m = ((r * a + s * b) % N + N) % N;
    const zeta = P.cExpI(P.div(P.mul(P.mul(P.pi(), P.ofInt(2)), P.ofInt(m)), P.ofInt(N)));
    const om = F.omegaClosed(N, a, b);
    return { re: P.div(P.mul(zeta.re, om), P.ofInt(N)), im: P.div(P.mul(zeta.im, om), P.ofInt(N)) };
  };

  /* ── independent quadrature (no Γ anywhere) ───────────────────────── */
  // P = (1/N)ζ^{ra+s(b−N)}·[∫h1 + ∫h2], with
  // h1 = N·2^{−A}·u^{a−1}·(1−u^N/2)^{B−1}, h2 = N·2^{−B}·u^{b−1}·(1−u^N/2)^{A−1}
  const _lnCache = new Map();   // key N@P: per-node cached ln(1−u^N/2) for u and 1−u
  function _cachedLn(N) {
    const key = N + '@' + P.getDps();
    if (_lnCache.has(key)) return _lnCache.get(key);
    const arr = P.getTshNodes().map(nd => {
      const u = nd.u, u2 = P.sub(P.ofInt(1), u);
      const ln1 = P.ln(P.sub(P.ofInt(1), P.div(P.powInt(u, N), P.ofInt(2))));
      const ln2 = P.ln(P.sub(P.ofInt(1), P.div(P.powInt(u2, N), P.ofInt(2))));
      return { u, u2, w: nd.w, first: nd.first, ln1, ln2 };
    });
    _lnCache.set(key, arr);
    return arr;
  }

  F.periodNumeric = function (N, a, b, r, s) {
    const A = P.div(P.ofInt(a), P.ofInt(N));
    const B = P.div(P.ofInt(b), P.ofInt(N));
    const m = ((r * a + s * (b - N)) % N + N) % N;
    const cth = P.cExpI(P.div(P.mul(P.mul(P.pi(), P.ofInt(2)), P.ofInt(m)), P.ofInt(N)));
    const nodes = _cachedLn(N);
    const ln2 = P.ln2();
    const f2A = P.exp(P.neg(P.mul(A, ln2)));   // 2^{−A}
    const f2B = P.exp(P.neg(P.mul(B, ln2)));   // 2^{−B}
    function integrate(expA, expB, fac) {
      let sum = P.ofInt(0);
      for (const nd of nodes) {
        const upow = expA === 0 ? P.ofInt(1) : P.powInt(nd.u, expA);
        const v1 = P.mul(P.mul(nd.w, fac), P.mul(upow, P.exp(P.mul(expB, nd.ln1))));
        if (nd.first) { sum += P.mul(v1, P.ofInt(N)); continue; }
        const upow2 = expA === 0 ? P.ofInt(1) : P.powInt(nd.u2, expA);
        const v2 = P.mul(P.mul(nd.w, fac), P.mul(upow2, P.exp(P.mul(expB, nd.ln2))));
        sum += P.mul(P.add(v1, v2), P.ofInt(N));
      }
      return sum;
    }
    const i1 = integrate(a - 1, P.sub(B, P.ofInt(1)), f2A);
    const i2 = integrate(b - 1, P.sub(A, P.ofInt(1)), f2B);
    const total = i1 + i2;
    return { re: P.div(P.mul(cth.re, total), P.ofInt(N)), im: P.div(P.mul(cth.im, total), P.ofInt(N)) };
  };

  F.relErr = function (x, y) {
    // port of rel_err — works for real (BigInt) and complex ({re,im})
    if (typeof x === 'bigint' && typeof y === 'bigint') return P.relErr(x, y);
    const dx = P.sub(x.re, y.re), dy = P.sub(x.im, y.im);
    const d = AtoFloatIfBig(P.sqrt(_cAbs2Raw(dx, dy)));
    const nx = Math.max(cAbsFloat(x), cAbsFloat(y), 1e-40);
    return d / nx;
  };
  function _cAbs2Raw(re, im) {
    const a = typeof re === 'bigint' ? re : BigInt(0);
    const b = typeof im === 'bigint' ? im : BigInt(0);
    return _rdivRaw(a * a + b * b, P.ofInt(1));
  }
  function _rdivRaw(a, b) { return a / b; } // scaled/scaling → scaled
  function AtoFloatIfBig(v) { return typeof v === 'bigint' ? P.toFloat(v) : v; }
  function cAbsFloat(z) {
    if (typeof z === 'bigint') return Math.abs(P.toFloat(z));
    const re = P.toFloat(z.re), im = P.toFloat(z.im);
    return Math.hypot(re, im);
  }

  /* ── deterministic character sample (port of pick_chars) ──────────── */
  F.pickChars = function (byD, perD) {
    perD = perD || 3;
    const out = [];
    for (const d of Object.keys(byD).map(Number).sort((x, y) => x - y)) {
      const lst = byD[d]; const n = lst.length;
      const take = n >= 3 ? [...new Set([0, n >> 1, n - 1])].sort((x, y) => x - y) : lst.map((_, i) => i);
      for (const k of take.slice(0, perD)) out.push([d, lst[k]]);
    }
    return out;
  };

  /* ── radical constants b_Ch (roadmap v1.2) ────────────────────────── */
  // b_Ch(n) = 1 − cos(2π/n); closed radicals for n = 15, 30 live in the
  // biquadratic tower Z[√5][√D]: element = (A + B·β) with β² = D = d0+d1√5.
  F.BCH_RADICALS = {
    15: { D: [30, -6], m: [[1, 1], [1, 0]], den: 4, poly: [1, -1, -4, 4, 1], bch: '(7 − √5 − √(30−6√5)) / 8' },
    30: { D: [30, 6], m: [[-1, 1], [1, 0]], den: 4, poly: [1, 1, -4, -4, 1], bch: '(9 − √5 − √(30+6√5)) / 8' },
  };

  // Z[√5] arithmetic on integer pairs
  function z5mul(p, q) { return [p[0] * q[0] + 5 * p[1] * q[1], p[0] * q[1] + p[1] * q[0]]; }
  function z5add(p, q) { return [p[0] + q[0], p[1] + q[1]]; }
  // tower arithmetic: (A,B) of pairs — value A + B·β
  function twMul(u, v, D) {
    // (A1+B1β)(A2+B2β) = A1A2 + B1B2·D + (A1B2+A2B1)β
    return [z5add(z5mul(u[0], v[0]), z5mul(z5mul(u[1], v[1]), D)), z5add(z5mul(u[0], v[1]), z5mul(u[1], v[0]))];
  }
  function twAdd(u, v) { return [z5add(u[0], v[0]), z5add(u[1], v[1])]; }
  function twScale(u, k) { return [[u[0][0] * k, u[0][1] * k], [u[1][0] * k, u[1][1] * k]]; }

  F.bchExactLayer = function (n) {
    // (a) 4⁴·P(x) ≡ 0 exactly in the tower, where x = (c0+√5+β)/4 and
    //     X = 4x = c0+√5+β:  4⁴P(x) = X⁴ − 4X³ − 64X² + 256X + 256·(sign-adjusted)
    //     computed term-by-term from P's coefficients;
    // (b) P irreducible over GF(2).
    const spec = F.BCH_RADICALS[n];
    if (!spec) return { pass: false, supported: false };
    const D = spec.D, den = spec.den;
    const X = [[spec.m[0][0], spec.m[0][1]], [spec.m[1][0], spec.m[1][1]]]; // = den·x
    function twPowInt(u, e) {
      let r = [[1, 0], [0, 0]], b = u;   // identity element A=1, B=0
      while (e) { if (e & 1) r = twMul(r, b, D); b = twMul(b, b, D); e >>= 1; }
      return r;
    }
    const poly = spec.poly; // P(x) = Σ_j c_j x^j, highest-first; c_j = poly[deg−j]
    const deg = poly.length - 1;
    // cleared polynomial: den^deg·P(X/den) = Σ_j poly[deg−j]·den^(deg−j)·X^j
    let acc = [[0, 0], [0, 0]];
    for (let j = 0; j < poly.length; j++) {
      const c = poly[deg - j] * (den ** (deg - j));
      if (!c) continue;
      acc = twAdd(acc, twScale(twPowInt(X, j), c));
    }
    const zero = JSON.stringify([[0, 0], [0, 0]]);
    const residOk = JSON.stringify(acc) === zero;
    const gf2 = _polyIrredGf2(spec.poly);
    return { pass: residOk && gf2, residual_ok: residOk, gf2_irreducible: gf2, supported: true };
  };
  function _polyIrredGf2(coeffs) {
    // quartic: no root in F2 and not divisible by x²+x+1
    const d = coeffs.length - 1;
    if (d !== 4) return false;
    const ev0 = coeffs[4] & 1, ev1 = (coeffs[0] + coeffs[1] + coeffs[2] + coeffs[3] + coeffs[4]) & 1;
    if (ev0 === 0 || ev1 === 0) return false;
    // mod x²+x+1: reduce
    let rem = coeffs.slice();
    for (let i = 0; i <= 2; i++) { /* reduce degrees 4,3 */
      for (let dd = 4; dd >= 2; dd--) {
        if (rem[dd] & 1) { rem[dd - 2] = (rem[dd - 2] + 1) & 1; rem[dd - 1] = (rem[dd - 1] + 1) & 1; rem[dd] = 0; }
      }
    }
    const r0 = rem[0] & 1, r1 = rem[1] & 1;
    if (r0 === 0 && r1 === 0) return false;
    return true;
  }

  F.bchClosed = function (n) {
    if (n === 15) {
      const s5 = P.sqrt(P.ofInt(5));
      return P.div(P.sub(P.sub(P.ofInt(7), s5), P.sqrt(P.sub(P.ofInt(30), P.mul(P.ofInt(6), s5)))), P.ofInt(8));
    }
    if (n === 30) {
      const s5 = P.sqrt(P.ofInt(5));
      return P.div(P.sub(P.sub(P.ofInt(9), s5), P.sqrt(P.add(P.ofInt(30), P.mul(P.ofInt(6), s5)))), P.ofInt(8));
    }
    throw new Error('closed radical form installed for n = 15 and n = 30 only');
  };
  F.bchNumeric = function (n) {
    return P.sub(P.ofInt(1), P.cos(P.div(P.mul(P.mul(P.pi(), P.ofInt(2)), P.ofInt(1)), P.ofInt(n))));
  };

  /* ── cyclotomic exact layer (roadmap v1.3 — N = 7/9) ─────────────── */
  F.CYC_CUBICS = {
    7: { units: [1, 2, 3], poly: [1, 1, -2, -1], phi: [1, 1, 1, 1, 1, 1, 1], vieta: [-1, -2, 1],
      cardano: '2cos(2π/7) = ∛(7(1+3√−3)/54) + ∛(7(1−3√−3)/54) − 1/3',
      bch: 'b_Ch(7) = 7/6 − (∛(7(1+3√−3)/54) + ∛(7(1−3√−3)/54))/2', rung: 'Hurwitz' },
    9: { units: [1, 2, 4], poly: [1, 0, -3, 1], phi: [1, 0, 0, 1, 0, 0, 1], vieta: [0, -3, -1],
      cardano: '2cos(2π/9) = ∛((−1+√−3)/2) + ∛((−1−√−3)/2)',
      bch: 'b_Ch(9) = 1 − (∛((−1+√−3)/2) + ∛((−1−√−3)/2))/2', rung: 'Macbeath' },
  };

  function polyMul(a, b) {
    const res = new Array(a.length + b.length - 1).fill(0);
    for (let i = 0; i < a.length; i++) if (a[i]) for (let j = 0; j < b.length; j++) res[i + j] += a[i] * b[j];
    return res;
  }
  function polyModPhi(a, phi) {
    a = a.slice();
    const dphi = phi.length - 1;
    for (let i = 0; i < a.length - dphi; i++) {
      if (!a[i]) continue;
      for (let j = 1; j < phi.length; j++) a[i + j] -= a[i] * phi[j];
      a[i] = 0;
    }
    while (a.length && a[0] === 0) a.shift();
    return a.length ? a : [0];
  }
  F.cycExactLayer = function (n) {
    const spec = F.CYC_CUBICS[n];
    if (!spec) return { pass: false, supported: false };
    // x_k = ζ^k + ζ^{−k} in Z[ζ]/Φ_n; compute s1,s2,s3 of the three conjugates
    const x = [0, 1, 0, 0, 0, 0, 0]; // placeholder; use polynomial arithmetic:
    // element ζ^k + ζ^{−k} as poly: x^k + x^{n−k} reduced mod Φ
    const els = spec.units.map(k => {
      let p = new Array(n + 1).fill(0);
      p[k] += 1; p[n - k] += 1;
      p = polyModPhi(p, spec.phi);
      while (p.length < 1) p.push(0);
      return p;
    });
    function elAdd(p, q) {
      const out = new Array(Math.max(p.length, q.length)).fill(0);
      for (let i = 0; i < p.length; i++) out[out.length - p.length + i] += p[i];
      for (let i = 0; i < q.length; i++) out[out.length - q.length + i] += q[i];
      let r = polyModPhi(out, spec.phi);
      return r;
    }
    function elMul(p, q) { return polyModPhi(polyMul(p, q), spec.phi); }
    function elIsInt(p) { return p.length === 1; }
    // s1 = e1, s2 = e2, s3 = e3 over the three conjugates (highest-first normal)
    function norm(p) { while (p.length > 1 && p[0] === 0) p.shift(); return p; }
    const e1 = norm(elAdd(els[0], elAdd(els[1], els[2])));
    const e2 = norm(elAdd(elAdd(elMul(els[0], els[1]), elMul(els[0], els[2])), elMul(els[1], els[2])));
    const e3 = norm(elMul(els[0], elMul(els[1], els[2])));
    const vietaOk = e1.length === 1 && e2.length === 1 && e3.length === 1 &&
      e1[0] === spec.vieta[0] && e2[0] === spec.vieta[1] && e3[0] === spec.vieta[2];
    const gf2 = _polyIrredGf2Cubic(spec.poly);
    return { pass: vietaOk && gf2, vieta_match: vietaOk, gf2_irreducible: gf2, syms: [e1[0], e2[0], e3[0]], supported: true };
  };
  function _polyIrredGf2Cubic(coeffs) {
    const ev0 = coeffs[3] & 1, ev1 = (coeffs[0] + coeffs[1] + coeffs[2] + coeffs[3]) & 1;
    if (ev0 === 0 || ev1 === 0) return false;
    // cubic over GF(2): no root ⇒ irreducible
    return true;
  }
  F.bchCardano = function (n) {
    // casus irreducibilis closed forms — returns b_Ch(n) = 1 − cos(2π/n)
    if (n === 7) {
      // 2cos(2π/7) = S − 1/3, S = cbrt(z)+conj(cbrt(z)), z = 7(1+3i√3)/54
      // b_Ch(7) = 1 − cos = 7/6 − S/2
      const zre = P.div(P.ofInt(7), P.ofInt(54));
      const zim = P.div(P.mul(P.ofInt(21), P.sqrt(P.ofInt(3))), P.ofInt(54));
      const cb = P.cCbrt({ re: zre, im: zim });
      const S = P.mul(cb.re, P.ofInt(2));
      return P.sub(P.div(P.ofInt(7), P.ofInt(6)), P.div(S, P.ofInt(2)));
    }
    if (n === 9) {
      // 2cos(2π/9) = S, S = cbrt(z)+conj(cbrt(z)), z = (−1+i√3)/2
      // b_Ch(9) = 1 − S/2
      const zre = P.div(P.ofInt(-1), P.ofInt(2));
      const zim = P.div(P.sqrt(P.ofInt(3)), P.ofInt(2));
      const cb = P.cCbrt({ re: zre, im: zim });
      const S = P.mul(cb.re, P.ofInt(2));
      return P.sub(P.ofInt(1), P.div(S, P.ofInt(2)));
    }
    throw new Error('Cardano closed form installed for n = 7 and n = 9 only');
  };

  global.Fermat = F;
})(typeof window !== 'undefined' ? window : globalThis);
