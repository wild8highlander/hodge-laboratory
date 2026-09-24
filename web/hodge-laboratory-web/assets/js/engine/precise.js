/* ══════════════════════════════════════════════════════════════════════
   HODGE LABORATORY WEB — precise.js
   Arbitrary-precision fixed-point engine on BigInt (no dependencies).

   Web port of the mpmath layer of laboratory.py:
     π (Chudnovsky, binary splitting) · exp · ln · sin · cos · atan
     Γ via Stirling + exact rational Bernoulli numbers (shift method)
     tanh–sinh double-exponential quadrature on [0,1] (node cache)
     complex arithmetic + exp/ln/arg/sqrt/cbrt

   A number is a BigInt v representing the real value v / SC,
   SC = 10^P, P = dps + GUARD guard digits.
   ══════════════════════════════════════════════════════════════════════ */
(function (global) {
  'use strict';

  const GUARD = 26;
  let DPS = 35;
  let P = DPS + GUARD;
  let SC = 10n ** BigInt(P);

  const API = {};

  /* ── setup ────────────────────────────────────────────────────────── */
  API.setDps = function (dps) {
    DPS = Math.max(15, Math.min(200, dps | 0));
    P = DPS + GUARD;
    SC = 10n ** BigInt(P);
    _cache = {};
  };
  API.getDps = function () { return DPS; };

  /* ── constructors / conversion ────────────────────────────────────── */
  API.ofInt = function (n) { return BigInt(n) * SC; };
  API.ofRatio = function (num, den) { return _rdiv(BigInt(num) * SC, BigInt(den)); };
  API.ofStr = function (s) {
    s = String(s).trim();
    let sign = 1n;
    if (s[0] === '-') { sign = -1n; s = s.slice(1); }
    else if (s[0] === '+') s = s.slice(1);
    let mant = s, exp = 0n;
    const ei = s.search(/[eE]/);
    if (ei >= 0) { exp = BigInt(s.slice(ei + 1)); mant = s.slice(0, ei); }
    const dot = mant.indexOf('.');
    let digits;
    if (dot >= 0) {
      exp -= BigInt(mant.length - dot - 1);
      digits = BigInt((mant.slice(0, dot) + mant.slice(dot + 1)) || '0');
    } else digits = BigInt(mant || '0');
    if (exp >= 0n) return sign * digits * 10n ** exp * SC;
    return sign * _rdiv(digits * SC, 10n ** (-exp));
  };
  API.ofFloat = function (x) { return API.ofStr(Number(x).toPrecision(17)); };
  API.toFloat = function (a) {
    if (typeof a === 'number') return a;
    return parseFloat(API.toStr(a, 18));
  };
  API.toStr = function (a, digits) {
    if (typeof a !== 'bigint') return String(a);
    const d = Math.max(0, Math.min(digits == null ? DPS : digits, P - 2));
    const neg = a < 0n; const v = neg ? -a : a;
    const ip = v / SC; const fp = v % SC;
    let fs = fp.toString().padStart(P, '0').slice(0, d);
    if (fs.length < d) fs += '0'.repeat(d - fs.length);
    const body = ip.toString() + (d > 0 ? '.' + fs : '');
    return (neg && (ip !== 0n || BigInt(fs || '0') !== 0n) ? '-' : '') + body;
  };
  API.sci = function (a, sig) {
    // scientific notation for residuals; plain form in "human" range
    const f = API.toFloat(a);
    const af = Math.abs(f);
    if (af !== 0 && (af < 1e-5 || af >= 1e6)) return f.toExponential(sig == null ? 2 : sig);
    return API.toStr(a, sig == null ? 6 : sig);
  };

  /* ── core arithmetic ──────────────────────────────────────────────── */
  function _rdiv(a, b) {
    if (b < 0n) { a = -a; b = -b; }
    const half = b >> 1n;
    return a >= 0n ? (a + half) / b : -((-a + half) / b);
  }
  API.add = (a, b) => a + b;
  API.sub = (a, b) => a - b;
  API.neg = (a) => -a;
  API.abs = (a) => (a < 0n ? -a : a);
  API.cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  API.mul = (a, b) => _rdiv(a * b, SC);
  API.div = (a, b) => _rdiv(a * SC, b);
  API.recip = (a) => _rdiv(SC * SC, a);
  API.isZero = (a) => a === 0n;

  /* ── sqrt ─────────────────────────────────────────────────────────── */
  API.sqrt = function (a) {
    if (a < 0n) throw new Error('sqrt of negative');
    if (a === 0n) return 0n;
    const target = a * SC;      // = value(a) · SC² → sqrt gives scaled result
    let x = _isqrtBig(target);
    // adjust to nearest
    while (x > 0n && x * x > target) x--;
    while ((x + 1n) * (x + 1n) <= target) x++;
    return x;
  };
  function _isqrtBig(n) {
    if (n < 2n) return n;
    let x = 1n << BigInt(Math.ceil(_bitLen(n) / 2) + 1);
    for (;;) {
      const nx = (x + n / x) >> 1n;
      if (nx >= x) break;
      x = nx;
    }
    return x;
  }
  function _bitLen(n) { let l = 0; while (n) { n >>= 1n; l++; } return l; }

  /* ── constants cache ──────────────────────────────────────────────── */
  let _cache = {};
  function _const(key, gen) {
    if (_cache[key] === undefined) _cache[key] = gen();
    return _cache[key];
  }

  /* ── π · Chudnovsky ───────────────────────────────────────────────── */
  API.pi = function () {
    return _const('pi', function () {
      const A = 13591409n, B = 545140134n, D = 10939058860032000n;
      const terms = BigInt(Math.ceil((P + 14) / 14) + 2);
      function bs(a, b) {
        if (b - a === 1n) {
          const k = a;
          const pk = (6n * k - 5n) * (2n * k - 1n) * (6n * k - 1n);
          const qk = k * k * k * D;
          const sign = (k & 1n) === 0n ? 1n : -1n;
          return [pk, qk, sign * (A + B * k) * pk];
        }
        const mid = (a + b) >> 1n;
        const r1 = bs(a, mid), r2 = bs(mid, b);
        return [r1[0] * r2[0], r1[1] * r2[1], r1[2] * r2[1] + r2[2] * r1[0]];
      }
      const [, Q, T] = bs(1n, terms + 1n);
      // S = (A·Q + T)/Q ; π = 426880·√10005/S
      const denom = A * Q + T;
      const num = _rdiv(API.ofInt(426880n) * Q, denom);
      return API.mul(num, API.sqrt(API.ofInt(10005n)));
    });
  };

  /* ── exp / ln / pow ───────────────────────────────────────────────── */
  API.ln2 = function () {
    return _const('ln2', function () {
      // ln2 = 2·atanh(1/3)
      let term = _rdiv(SC, 3n), k = 1n, sum = 0n;
      const N = Math.ceil((P + 8) * 1.15);
      for (let i = 0; i < N; i++) { sum += term / k; term = _rdiv(term, 9n); k += 2n; }
      return 2n * sum;
    });
  };
  API.exp = function (x) {
    if (x === 0n) return API.ofInt(1);
    const neg = x < 0n; const ax = neg ? -x : x;
    const L2 = API.ln2();
    const q = _rdiv(ax, L2);
    const r = ax - q * L2;
    let sum = API.ofInt(1), term = API.ofInt(1);
    const kmax = Math.ceil(P * 1.2) + 30;
    for (let k = 1; k <= kmax; k++) {
      term = _rdiv(term * r, BigInt(k) * SC);
      sum += term;
      if (term === 0n) break;
    }
    let m = q, base = API.ofInt(2), res = API.ofInt(1);
    while (m > 0n) {
      if (m & 1n) res = API.mul(res, base);
      base = API.mul(base, base); m >>= 1n;
    }
    const out = API.mul(sum, res);
    return neg ? API.recip(out) : out;
  };
  API.ln = function (x) {
    if (x <= 0n) throw new Error('ln of non-positive');
    // normalize value v = x/SC to f ∈ [1,2): e2 = bl(x) − bl(SC) − 1
    const e2 = BigInt(_bitLen(x) - _bitLen(SC) - 1);
    let f;
    if (e2 >= 0n) f = x >> e2; else f = x << (-e2);
    const y = _rdiv((f - SC) * SC, f + SC);   // y = (f−1)/(f+1), SCALED
    const y2 = API.mul(y, y);
    let sum = 0n, term = y, k = 1n;
    const N = Math.ceil((P + 8) * 1.15);
    for (let i = 0; i < N; i++) { sum += term / k; term = API.mul(term, y2); k += 2n; }
    const L2 = API.ln2();
    return 2n * sum + e2 * L2;
  };
  API.pow = function (x, y) { return API.exp(API.mul(y, API.ln(x))); };
  API.powInt = function (x, n) {
    let r = API.ofInt(1), b = x, m = BigInt(n);
    while (m > 0n) {
      if (m & 1n) r = API.mul(r, b);
      b = API.mul(b, b); m >>= 1n;
    }
    return r;
  };

  /* ── trig ─────────────────────────────────────────────────────────── */
  API.sin = function (x) {
    const TAU = 2n * API.pi();
    let r = _modScaled(x, TAU);           // (−π, π]
    if (r > API.pi() / 2n) return _sinTaylor(API.pi() - r);
    if (r < -API.pi() / 2n) return -_sinTaylor(r + API.pi());
    return _sinTaylor(r);
  };
  API.cos = function (x) {
    const TAU = 2n * API.pi();
    let r = _modScaled(x, TAU);
    if (r > API.pi() / 2n) return -_cosTaylor(API.pi() - r);
    if (r < -API.pi() / 2n) return -_cosTaylor(r + API.pi());
    return _cosTaylor(r);
  };
  function _modScaled(x, m) { return x - _rdiv(x, m) * m; }
  function _sinTaylor(r) {
    let sum = 0n, term = r, k = 1n;
    const r2 = API.mul(r, r);
    for (let i = 0; i < 4 * P + 40; i++) {
      sum += term;
      term = _rdiv(-term * r2, (k + 1n) * (k + 2n) * SC);
      k += 2n;
      if (term === 0n) break;
    }
    return sum;
  }
  function _cosTaylor(r) {
    let sum = 0n, term = API.ofInt(1), k = 0n;
    const r2 = API.mul(r, r);
    for (let i = 0; i < 4 * P + 40; i++) {
      sum += term;
      term = _rdiv(-term * r2, (k + 1n) * (k + 2n) * SC);
      k += 2n;
      if (term === 0n) break;
    }
    return sum;
  }
  API.atan = function (x) {
    let a = API.abs(x);
    for (let i = 0; i < 2; i++)
      a = API.div(a, API.add(API.ofInt(1), API.sqrt(API.add(API.mul(a, a), API.ofInt(1)))));
    let sum = 0n, term = a, k = 1n;
    const a2 = API.mul(a, a);
    for (let i = 0; i < 4 * P + 40; i++) {
      sum += term / k;
      term = -_rdiv(term * a2, SC);
      k += 2n;
      if (term === 0n) break;
    }
    let out = 4n * sum;                    // two halvings
    return x < 0n ? -out : out;
  };
  API.atan2 = function (y, x) {
    if (x > 0n) return API.atan(_rdiv(y * SC, x));
    if (x < 0n) {
      const t = API.atan(_rdiv(API.abs(y) * SC, -x));
      return y >= 0n ? API.pi() - t : t - API.pi();
    }
    return y > 0n ? API.pi() / 2n : (y < 0n ? -API.pi() / 2n : 0n);
  };

  /* ── Bernoulli numbers (exact rationals) ──────────────────────────── */
  // Recurrence: Σ_{j=0}^{k} C(2k+1, 2j)·B_{2j} = (2k+1)/2  (odd B vanish)
  //   →  B_{2k} = [ (2k+1)/2 − Σ_{j<k} C(2k+1,2j)·B_{2j} ] / (2k+1)
  const _bernCache = [{ n: 1n, d: 1n }];  // B_0
  function bernoulli(k) {                  // B_{2k}
    if (_bernCache[k]) return _bernCache[k];
    const m = 2 * k + 1;
    let sn = 0n, sd = 1n;                  // Σ as exact fraction
    for (let j = 0; j < k; j++) {
      const c = _binom(BigInt(m), BigInt(2 * j));
      const b = bernoulli(j);
      sn = sn * b.d + (c * b.n) * sd;
      sd = sd * b.d;
      const g = _gcd(sn < 0n ? -sn : sn, sd);
      if (g > 1n) { sn /= g; sd /= g; }
    }
    // B = (m/2 − sn/sd)/m = (m·sd − 2·sn) / (2·m·sd)
    let n2 = BigInt(m) * sd - 2n * sn;
    let d2 = 2n * BigInt(m) * sd;
    if (n2 < 0n) { n2 = -n2; d2 = -d2; }
    const g = _gcd(n2, d2 < 0n ? -d2 : d2);
    _bernCache[k] = { n: n2 / g, d: d2 / g };
    return _bernCache[k];
  }
  function _gcd(a, b) { while (b) { const t = a % b; a = b; b = t; } return a; }
  const _binomCache = new Map();
  function _binom(n, k) {
    const key = n.toString() + ',' + k.toString();
    if (_binomCache.has(key)) return _binomCache.get(key);
    let r = 1n;
    for (let i = 0n; i < k; i++) r = r * (n - i) / (i + 1n);
    _binomCache.set(key, r);
    return r;
  }

  /* ── Γ (Stirling + shift) ─────────────────────────────────────────── */
  API.lgamma = function (x) {
    if (x <= 0n) throw new Error('lgamma: x>0 only');
    const zt = API.ofInt(Math.max(64, Math.ceil(P * 1.35)));  // SCALED threshold
    let m = 0n;
    if (x < zt) m = _rdiv(zt - x, SC) + 1n;
    const z = x + m * SC;
    const LN2PI = _const('ln2pi', () => API.ln2() + API.ln(API.pi()));
    let acc = API.mul(z - SC / 2n, API.ln(z)) - z + _rdiv(LN2PI, 2n);
    const zVal = API.toFloat(z);
    const nmax = Math.ceil((P + 8) / (2 * Math.log10(zVal))) + 3;
    for (let n = 1; n <= nmax; n++) {
      const b = bernoulli(n);
      const coef = API.ofRatio(b.n, b.d * BigInt(2 * n) * BigInt(2 * n - 1));
      acc += API.div(coef, API.powInt(z, 2 * n - 1));
    }
    if (m > 0n) {
      let xi = x;
      for (let i = 0n; i < m; i++) { acc -= API.ln(xi); xi += SC; }
    }
    return acc;
  };
  API.gamma = function (x) { return API.exp(API.lgamma(x)); };

  /* ── hyperbolic ───────────────────────────────────────────────────── */
  API.sinh = function (x) { const e = API.exp(x); return _rdiv(e - API.recip(e), 2n); };
  API.cosh = function (x) { const e = API.exp(x); return _rdiv(e + API.recip(e), 2n); };
  API.tanh = function (x) {
    const e2 = API.exp(API.mul(x, API.ofInt(2)));
    return API.div(e2 - API.ofInt(1), e2 + API.ofInt(1));
  };

  /* ── tanh–sinh quadrature on [0,1] with node cache ────────────────── */
  // I = ∫₀¹ f = h·Σ_k f(φ(kh))·φ'(kh),
  // φ(t) = ½(1+tanh((π/2)sinh t)) = e^{2x}/(e^{2x}+1), x=(π/2)sinh t
  // φ'(t) = (π/4)·cosh(t)/cosh²(x); φ(−t)=1−φ(t)
  function _tshNodes(level) {
    const key = 'tsh' + level + '@' + P;
    if (_cache[key]) return _cache[key];
    const h = API.div(API.ofInt(1), API.ofInt(1n << BigInt(level)));
    const PI2 = API.div(API.pi(), API.ofInt(2));
    const deepLim = -(P + 4) * 2.302585;   // ln(w) threshold
    const nodes = [];
    for (let k = 0; k < (1 << 21); k++) {
      const t = API.mul(h, API.ofInt(k));
      const e = API.exp(t);
      const ei = API.recip(e);
      const st = _rdiv(e - ei, 2n);                   // sinh t (scaled)
      const ct = _rdiv(e + ei, 2n);                   // cosh t (scaled)
      const x1 = API.mul(st, PI2);                    // (π/2)·sinh t
      // deep-break BEFORE evaluating cosh(x1): ln w ≈ ln(2·ct) − 2·x1
      if (k > 8 && API.toFloat(API.ln(API.mul(ct, API.ofInt(2)))) - 2 * API.toFloat(x1) < deepLim) break;
      const E = API.exp(x1);                          // e^{x1}
      const E2 = API.mul(E, E);                       // e^{2x1}
      const ch2 = _rdiv(E + API.recip(E), 2n);        // cosh x1 (scaled)
      const w = API.div(ct, API.mul(ch2, ch2));       // cosh t / cosh² x
      const phi = API.div(E2, API.add(E2, API.ofInt(1)));
      nodes.push({ u: phi, w: API.div(API.mul(API.mul(API.pi(), w), h), API.ofInt(4)), first: k === 0 });
    }
    _cache[key] = nodes;
    return nodes;
  }
  API.tanhSinh = function (f, level) {
    const nodes = _tshNodes(level || (DPS <= 45 ? 6 : DPS <= 90 ? 7 : 8));
    let sum = API.ofInt(0);
    for (const nd of nodes) {
      if (nd.first) { sum += API.mul(nd.w, f(nd.u)); }
      else {
        sum += API.mul(nd.w, f(nd.u));
        sum += API.mul(nd.w, f(API.sub(API.ofInt(1), nd.u)));
      }
    }
    return sum;
  };
  API.getTshNodes = function (level) {
    return _tshNodes(level || (DPS <= 45 ? 6 : DPS <= 90 ? 7 : 8));
  };

  /* ── complex layer ────────────────────────────────────────────────── */
  function C(re, im) { return { re, im }; }
  API.C = C;
  API.cAdd = (a, b) => C(a.re + b.re, a.im + b.im);
  API.cSub = (a, b) => C(a.re - b.re, a.im - b.im);
  API.cMul = (a, b) =>
    C(_rdiv(a.re * b.re - a.im * b.im, SC), _rdiv(a.re * b.im + a.im * b.re, SC));
  API.cScale = (a, s) => C(_rdiv(a.re * s, SC), _rdiv(a.im * s, SC));
  API.cDiv = function (a, b) {
    const d = _rdiv(b.re * b.re + b.im * b.im, SC);
    return C(_rdiv((a.re * b.re + a.im * b.im) * SC, d),
      _rdiv((a.im * b.re - a.re * b.im) * SC, d));
  };
  API.cAbs2 = (a) => _rdiv(a.re * a.re + a.im * a.im, SC);
  API.cAbs = (a) => API.sqrt(API.cAbs2(a));
  API.cExpI = (theta) => C(API.cos(theta), API.sin(theta));
  API.cExp = (z) => {
    const ea = API.exp(z.re);
    return C(API.mul(ea, API.cos(z.im)), API.mul(ea, API.sin(z.im)));
  };
  API.cArg = (a) => API.atan2(a.im, a.re);
  API.cLn = (a) => C(API.ln(API.cAbs(a)), API.cArg(a));
  API.cPowReal = (a, r) => { const l = API.cLn(a); return API.cExp(C(API.mul(l.re, r), API.mul(l.im, r))); };
  API.cCbrt = (a) => API.cPowReal(a, API.ofRatio(1, 3));
  API.cToFloat = (a) => ({ re: API.toFloat(a.re), im: API.toFloat(a.im) });
  API.cStr = function (a, d) {
    const sgn = a.im < 0n ? '-' : '+';
    return API.toStr(a.re, d) + ' ' + sgn + ' ' + API.toStr(API.abs(a.im), d) + 'i';
  };
  API.relErr = function (x, y) {  // port of rel_err (returns double)
    const d = API.toFloat(API.abs(x - y));
    const n = Math.max(API.toFloat(API.abs(x)), API.toFloat(API.abs(y)), 1e-40);
    return d / n;
  };

  global.Precise = API;
})(typeof window !== 'undefined' ? window : globalThis);
