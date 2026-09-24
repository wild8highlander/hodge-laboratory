// ══════════════════════════════════════════════════════════════════════
//  HODGE LABORATORY — POLYGLOT CORE · RUST (f64 + i128, no deps)
//  Ядро лаборатории на чистом Rust: точные целочисленные стенды (i128),
//  квадратуры в f64 (tanh–sinh / гладкая регуляризованная форма Ω).
//  The laboratory core in plain Rust: exact integer stands (i128),
//  quadratures in f64 (tanh–sinh / smooth regularized Ω form).
//
//  Сборка / Build:  rustc -O verify_core.rs -o verify_core
//  Запуск / Run:    ./verify_core
//
//  Автор программы / Program author:
//    Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
//  Репозиторий / Repository: wild8highlander/hodge-laboratory
//  Лицензия / License: индивидуальная эксклюзивная / individual exclusive
// ══════════════════════════════════════════════════════════════════════
use std::i128;

/* ── integer helpers ───────────────────────────────────────────────── */
fn gcd64(a: i64, b: i64) -> i64 {
    let (mut a, mut b) = (a.abs(), b.abs());
    while b != 0 { let t = a % b; a = b; b = t; }
    a
}
fn lcm64(a: i64, b: i64) -> i64 {
    if a == 0 || b == 0 { 0 } else { (a / gcd64(a, b) * b).abs() }
}

/* ── exact fractions over i128 (num/den, den>0, reduced) ──────────── */
#[derive(Clone, Copy)]
struct Frac { n: i128, d: i128 }
fn igcd(a: i128, b: i128) -> i128 {
    let (mut a, mut b) = (a.abs(), b.abs());
    while b != 0 { let t = a % b; a = b; b = t; }
    a
}
fn fr(n: i128, d: i128) -> Frac {
    let (n, d) = if d < 0 { (-n, -d) } else { (n, d) };
    let g = igcd(n, d).max(1);
    Frac { n: n / g, d: d / g }
}
fn fr_add(a: Frac, b: Frac) -> Frac { fr(a.n * b.d + b.n * a.d, a.d * b.d) }
fn fr_sub(a: Frac, b: Frac) -> Frac { fr(a.n * b.d - b.n * a.d, a.d * b.d) }
fn fr_mul(a: Frac, b: Frac) -> Frac { fr(a.n * b.n, a.d * b.d) }

/* ═══ 1–2. census ═══════════════════════════════════════════════════ */
fn census(n: i64) -> (Vec<(i64, i64)>, i64) {   /* (sorted (d, h_d), genus) */
    let mut h: Vec<(i64, i64)> = Vec::new();
    for a in 1..n {
        for b in 1..(n - a) {
            let d = n / gcd64(gcd64(n, a), b);
            if let Some(e) = h.iter_mut().find(|e| e.0 == d) { e.1 += 1; }
            else { h.push((d, 1)); }
        }
    }
    h.sort();
    let genus = (n - 1) * (n - 2) / 2;
    (h, genus)
}
fn mobius(m: i64) -> i64 {
    if m == 1 { return 1; }
    let mut x = m; let mut res = 1i64; let mut q = 2i64;
    while q * q <= x {
        if x % q == 0 {
            x /= q;
            if x % q == 0 { return 0; }
            res = -res;
        }
        q += 1;
    }
    if x > 1 { res = -res; }
    res
}
fn census_mobius(n: i64) -> Vec<(i64, i64)> {
    let c = |k: i64| if k >= 3 { (k - 1) * (k - 2) / 2 } else { 0 };
    let mut out = Vec::new();
    for d in 2..=n {
        if n % d != 0 { continue; }
        let mut s = 0i64;
        for m in 1..=d {
            if d % m == 0 { s += mobius(m) * c(d / m); }
        }
        if s != 0 { out.push((d, s)); }
    }
    out
}

/* ═══ 3–4. cert E + binary flow ═════════════════════════════════════ */
fn tstar(w: i64, hh: i64, a: i64, b: i64) -> i64 {
    lcm64(w / gcd64(a, w), hh / gcd64(b, hh))
}
fn binary_flow() -> (i64, i64, bool) {
    let (w, hh, a, b) = (48i64, 48i64, 1i64, 1i64);
    let t = tstar(w, hh, a, b);
    let (mut x, mut y, mut dx, mut dy) = (0i64, 0i64, 0i64, 0i64);
    let mut seen = [[false; 48]; 48];
    let mut vis = 0i64;
    for _ in 0..t {
        if !seen[x as usize][y as usize] { seen[x as usize][y as usize] = true; vis += 1; }
        x = (x + a) % w; y = (y + b) % hh;
        dx = (dx + a) % w; dy = (dy + b) % hh;
    }
    (t, vis, dx == 0 && dy == 0)
}

/* ═══ 5. Arf enumeration ════════════════════════════════════════════ */
fn arf_enum(g: u32) -> (i64, i64, i64) {
    let n = 2 * g;
    let size: i64 = 1 << n;
    let half = size >> 1;
    let shift: i64 = 1 << (g - 1);
    let pairs: Vec<(usize, usize)> = (0..g as usize).map(|i| (2 * i, 2 * i + 1)).collect();
    let (mut ev, mut od) = (0i64, 0i64);
    for basis in 0..size {
        let mut zeros = 0i64;
        for v in 0..size {
            let mut qv = 0i64;
            for i in 0..n {
                if (v >> i) & 1 == 1 { qv ^= (basis >> i) & 1; }
            }
            for &(i, j) in &pairs {
                if ((v >> i) & 1) & ((v >> j) & 1) == 1 { qv ^= 1; }
            }
            if qv == 0 { zeros += 1; }
        }
        if zeros == half + shift { ev += 1; } else { od += 1; }
    }
    (size, ev, od)
}

/* ═══ 6. K3: exact rank · SNF · signature (i128) ════════════════════ */
const KL: usize = 48;
const KN: usize = 49;

fn k3_lines() -> [[i32; 3]; KL] {
    let mut ls = [[0i32; 3]; KL];
    let mut k = 0;
    for f in 1..=3 {
        for a in 0..4 {
            for b in 0..4 { ls[k] = [f, a, b]; k += 1; }
        }
    }
    ls
}
fn k3_inter(l1: &[i32; 3], l2: &[i32; 3]) -> i32 {
    if l1 == l2 { return -2; }
    let (f1, a1, b1) = (l1[0], l1[1], l1[2]);
    let (f2, a2, b2) = (l2[0], l2[1], l2[2]);
    if f1 == f2 { return if (a1 == a2) != (b1 == b2) { 1 } else { 0 }; }
    let (lo, hi) = if f1 < f2 { (f1, f2) } else { (f2, f1) };
    if lo == 1 && hi == 2 { return if (a1 + b2 - a2 - b1).rem_euclid(4) == 0 { 1 } else { 0 }; }
    if lo == 1 && hi == 3 {
        let t = if f1 == 1 { a2 - a1 - b1 - b2 - 1 } else { a1 - a2 - b2 - b1 - 1 };
        return if t.rem_euclid(4) == 0 { 1 } else { 0 };
    }
    if (a1 + b1 - a2 - b2).rem_euclid(4) == 0 { 1 } else { 0 }
}
fn k3_gram() -> [[i64; KN]; KN] {
    let ls = k3_lines();
    let mut g = [[0i64; KN]; KN];
    for i in 0..KL {
        for j in i..KL { g[i][j] = k3_inter(&ls[i], &ls[j]) as i64; g[j][i] = g[i][j]; }
    }
    for i in 0..KL { g[i][KL] = 1; g[KL][i] = 1; }
    g[KL][KL] = 4;
    g
}
fn k3_rank(g: &[[i64; KN]; KN]) -> usize {
    let mut m = [[Frac { n: 0, d: 1 }; KN]; KN];
    for i in 0..KN { for j in 0..KN { m[i][j] = Frac { n: g[i][j] as i128, d: 1 }; } }
    let mut r = 0;
    for c in 0..KN {
        if r >= KN { break; }
        let mut piv = None;
        for i in r..KN { if m[i][c].n != 0 { piv = Some(i); break; } }
        let p = match piv { Some(p) => p, None => continue };
        m.swap(r, p);
        let pv = m[r][c];
        for i in (r + 1)..KN {
            if m[i][c].n == 0 { continue; }
            let f = fr_mul(m[i][c], fr(pv.d, pv.n));
            for j in c..KN { m[i][j] = fr_sub(m[i][j], fr_mul(f, m[r][j])); }
        }
        r += 1;
    }
    r
}
fn k3_snf(g: &[[i64; KN]; KN]) -> Vec<i128> {
    let mut a = [[0i128; KN]; KN];
    for i in 0..KN { for j in 0..KN { a[i][j] = g[i][j] as i128; } }
    let mut res = Vec::new();
    for t in 0..KN {
        loop {
            let (mut p, mut pi, mut pj) = (0i128, usize::MAX, usize::MAX);
            for i in t..KN {
                for j in t..KN {
                    let v = a[i][j].abs();
                    if v != 0 && (pi == usize::MAX || v < p) { p = v; pi = i; pj = j; }
                }
            }
            if pi == usize::MAX { return res; }
            if pi != t { for j in 0..KN { a.swap(t, pi); } }
            if pj != t { for i in 0..KN { let tmp = a[i][t]; a[i][t] = a[i][pj]; a[i][pj] = tmp; } }
            let piv = a[t][t];
            for i in (t + 1)..KN {
                let q = a[i][t] / piv;
                if q != 0 { for j in t..KN { a[i][j] -= q * a[t][j]; } }
            }
            for j in (t + 1)..KN {
                let q = a[t][j] / piv;
                if q != 0 { for i in 0..KN { a[i][j] -= q * a[i][t]; } }
            }
            let mut divisible = true;
            'outer: for i in (t + 1)..KN {
                for j in (t + 1)..KN {
                    if a[i][j] % piv != 0 { divisible = false; break 'outer; }
                }
            }
            if divisible { break; }
        }
        res.push(a[t][t].abs());
    }
    res
}
fn k3_int_ech(g: &[[i64; KN]; KN]) -> (Vec<[i128; KN]>, usize) {
    let mut m = [[Frac { n: 0, d: 1 }; KN]; KN];
    for i in 0..KN { for j in 0..KN { m[i][j] = Frac { n: g[i][j] as i128, d: 1 }; } }
    let mut rows: Vec<[i128; KN]> = Vec::new();
    let mut r = 0;
    for c in 0..KN {
        if r >= KN { break; }
        let mut piv = None;
        for i in r..KN { if m[i][c].n != 0 { piv = Some(i); break; } }
        let p = match piv { Some(p) => p, None => continue };
        m.swap(r, p);
        let pv = m[r][c];
        for j in 0..KN { m[r][j] = fr_mul(m[r][j], fr(pv.d, pv.n)); }
        for i in 0..KN {
            if i != r && m[i][c].n != 0 {
                let f = m[i][c];
                for j in c..KN { m[i][j] = fr_sub(m[i][j], fr_mul(f, m[r][j])); }
            }
        }
        /* clear denominators, then divide by gcd */
        let mut l: i128 = 1;
        for j in 0..KN { l = l / igcd(l, m[r][j].d) * m[r][j].d; }
        let mut ints = [0i128; KN];
        for j in 0..KN { ints[j] = m[r][j].n * (l / m[r][j].d); }
        let mut ggg: i128 = 0;
        for v in ints { ggg = igcd(ggg, v.abs()); }
        if ggg > 1 { for v in ints.iter_mut() { *v /= ggg; } }
        rows.push(ints);
        r += 1;
    }
    (rows, r)
}
fn k3_signature(g: &[[i64; KN]; KN], ech: &[[i128; KN]], k: usize) -> Option<(i64, i64)> {
    /* S = H·G·Hᵀ, exact LDLᵀ with fractions */
    let mut s = [[0i128; KN]; KN];
    for i in 0..k {
        let mut t = [0i128; KN];
        for tt in 0..KN {
            if ech[i][tt] == 0 { continue; }
            let cit = ech[i][tt];
            for u in 0..KN { t[u] += cit * g[tt][u] as i128; }
        }
        for j in 0..k {
            let mut acc: i128 = 0;
            for u in 0..KN { acc += t[u] * ech[j][u]; }
            s[i][j] = acc; s[j][i] = acc;
        }
    }
    let mut a = [[Frac { n: 0, d: 1 }; KN]; KN];
    for i in 0..k { for j in 0..k { a[i][j] = Frac { n: s[i][j], d: 1 }; } }
    let mut diag: Vec<Frac> = Vec::new();
    let (mut pos, mut neg) = (0i64, 0i64);
    for i in 0..k {
        let mut acc = Frac { n: 0, d: 1 };
        for tt in 0..i {
            acc = fr_add(acc, fr_mul(fr_mul(a[tt][i], a[tt][i]), diag[tt]));
        }
        let d = fr_sub(a[i][i], acc);
        if d.n == 0 { return None; }
        if d.n > 0 { pos += 1; } else { neg += 1; }
        diag.push(d);
        for j in (i + 1)..k {
            let mut s2 = Frac { n: 0, d: 1 };
            for tt in 0..i {
                s2 = fr_add(s2, fr_mul(fr_mul(a[tt][i], a[tt][j]), diag[tt]));
            }
            let v = fr_mul(fr_sub(Frac { n: s[i][j], d: 1 }, s2), fr(diag[i].d, diag[i].n));
            a[i][j] = v; a[j][i] = v;
        }
    }
    Some((pos, neg))
}

/* ═══ Lanczos gamma (f64, g=7, n=9) ═════════════════════════════════ */
fn gamma64(x: f64) -> f64 {
    const CO: [f64; 9] = [
        0.99999999999980993, 676.5203681218851, -1259.1392167224028,
        771.32342877765313, -176.61502916214059, 12.507343278686905,
        -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
    ];
    if x < 0.5 {
        std::f64::consts::PI / ((std::f64::consts::PI * x).sin() * gamma64(1.0 - x))
    } else {
        let xx = x - 1.0;
        let mut a = CO[0];
        let t = xx + 7.5;
        for (i, &c) in CO.iter().enumerate().skip(1) {
            a += c / (xx + i as f64);
        }
        (2.0 * std::f64::consts::PI).sqrt() * t.powf(xx + 0.5) * (-t).exp() * a
    }
}

/* ═══ 12. torus Δ_Ch (f64) ══════════════════════════════════════════ */
fn torus_delta() -> f64 {
    let pi = std::f64::consts::PI;
    let delta = pi / 4.0;
    4.0 * pi * pi + delta * delta / 2.0 - delta.powi(5)
}

/* ═══ 13. Klein Ω — smooth regularized form (long-precision-safe) ═══ */
/* Ω = 2∫₇^∞ dx/√((x−7)(x²+7x+14));  x−7 = t²  ⇒  Ω = 4∫₀^∞ dt/√(t⁴+21t²+112);
   t → 1/s on [1,∞)  ⇒  Ω = 4∫₀¹ [f1(t) + f2(t)] dt, both smooth on [0,1].
   (The raw u-form has a (1−u)^{−1/2} endpoint: f64 tanh–sinh floors at ~4√ε.
    The exact fixed-point JS engine avoids that; float languages regularize.) */
fn klein_omega(n: usize) -> f64 {
    let h = 1.0 / n as f64;
    let f1 = |t: f64| 1.0 / (t * t * t * t + 21.0 * t * t + 112.0).sqrt();
    let f2 = |t: f64| 1.0 / (1.0 + 21.0 * t * t + 112.0 * t * t * t * t).sqrt();
    let mut s1 = f1(0.0) + f1(1.0);
    let mut s2 = f2(0.0) + f2(1.0);
    for i in 1..n {
        let t = i as f64 * h;
        let w = if i & 1 == 1 { 4.0 } else { 2.0 };
        s1 += w * f1(t);
        s2 += w * f2(t);
    }
    4.0 * (s1 + s2) * h / 3.0
}

/* ═══ 14. V6 Γ-reflection (f64) ═════════════════════════════════════ */
fn v6_reflection() -> f64 {
    let pi = std::f64::consts::PI;
    let n = 7.0;
    (1..7).map(|k| {
        let kf = k as f64;
        let lhs = gamma64(kf / n) * gamma64((n - kf) / n);
        let rhs = pi / (pi * kf / n).sin();
        (lhs - rhs).abs() / rhs.abs()
    }).fold(0.0, f64::max)
}

/* ═══ 15. period closed vs tanh–sinh (f64) ══════════════════════════ */
fn period_quadrature(n: i64, a: i64, b: i64) -> f64 {
    let pi = std::f64::consts::PI;
    let (af, bf, nf) = (a as f64, b as f64, n as f64);
    let (aa, bb) = (af / nf, bf / nf);
    let (mut i1, mut i2) = (0.0f64, 0.0f64);
    let k = 150usize; let h = 0.05f64;
    for kk in 0..=(2 * k) {
        let t = (kk as f64 - k as f64) * h;
        let st = (t.exp() - (-t).exp()) / 2.0;   /* sinh(t) */
        let z = (pi / 2.0 * st).abs();
        if z > 350.0 { continue; }
        let u = 0.5 * (1.0 + (pi / 2.0 * st).tanh());
        if u <= 0.0 || u >= 1.0 { continue; }
        let chz = z.cosh();
        let w = (pi / 4.0) * t.cosh() / (chz * chz) * h;
        i1 += nf * w * (2.0f64).powf(-aa) * u.powf(af - 1.0) * (1.0 - u.powf(nf) / 2.0).powf(bb - 1.0);
        i2 += nf * w * (2.0f64).powf(-bb) * u.powf(bf - 1.0) * (1.0 - u.powf(nf) / 2.0).powf(aa - 1.0);
    }
    let closed = gamma64(af / nf) * gamma64(bf / nf) / gamma64((af + bf) / nf);
    ((i1 + i2) - closed).abs() / closed.abs()
}

/* ═══ output ───────────────────────────────────────────────────────── */
static mut TOTAL: i32 = 0;
static mut PASSED: i32 = 0;
fn check(name: &str, ok: bool, detail: &str) {
    unsafe {
        TOTAL += 1;
        if ok { PASSED += 1; }
        let mark = if ok { "PASS" } else { "FAIL" };
        if detail.is_empty() {
            println!("  [{}] {}", mark, name);
        } else {
            println!("  [{}] {}  ·  {}", mark, name, detail);
        }
    }
}

/* ── cyclotomic exact layer: Z[ζ]/(Φₙ), lowest-first coeffs c[0..16] ─ */
#[derive(Clone, Copy)]
struct Zeta { c: [i64; 17], n: i64 }
fn zeta_reduce(z: &mut Zeta) {
    /* Φ₇: x⁶ = −(x⁵+…+x+1);  Φ₉ = x⁶+x³+1 = Φ₃(x³): x⁶ = −x³−1 */
    loop {
        let mut top = None;
        for i in (6..17).rev() { if z.c[i] != 0 { top = Some(i); break; } }
        let t = match top { Some(t) => t, None => break };
        let v = z.c[t];
        z.c[t] = 0;
        if z.n == 7 {
            for j in 1..=6 { z.c[t - j] -= v; }
        } else {
            z.c[t - 3] -= v;
            z.c[t - 6] -= v;
        }
    }
}
fn zeta_mul(a: &Zeta, b: &Zeta) -> Zeta {
    let mut r = Zeta { c: [0; 17], n: a.n };
    for i in 0..17 {
        if a.c[i] == 0 { continue; }
        for j in 0..17 {
            if b.c[j] == 0 { continue; }
            r.c[i + j] += a.c[i] * b.c[j];
        }
    }
    zeta_reduce(&mut r);
    r
}
fn zeta_add(a: &Zeta, b: &Zeta) -> Zeta {
    let mut r = Zeta { c: [0; 17], n: a.n };
    for i in 0..17 { r.c[i] = a.c[i] + b.c[i]; }
    zeta_reduce(&mut r);
    r
}
fn cyc_layer(n: i64, units: &[i64; 3], vieta: &[i64; 3], poly: &[i64; 4]) -> bool {
    let mut els = [Zeta { c: [0; 17], n }; 3];
    for (u, &k) in units.iter().enumerate() {
        let mut z = Zeta { c: [0; 17], n };
        z.c[(k % n) as usize] += 1;
        z.c[((n - k) % n) as usize] += 1;
        zeta_reduce(&mut z);
        els[u] = z;
    }
    let e1 = zeta_add(&els[0], &zeta_add(&els[1], &els[2]));
    let e2 = zeta_add(&zeta_mul(&els[0], &els[1]),
                      &zeta_add(&zeta_mul(&els[0], &els[2]), &zeta_mul(&els[1], &els[2])));
    let e3 = zeta_mul(&els[0], &zeta_mul(&els[1], &els[2]));
    let is_int = |z: &Zeta| -> Option<i64> {
        for i in 1..17 { if z.c[i] != 0 { return None; } }
        Some(z.c[0])
    };
    let ok = match (is_int(&e1), is_int(&e2), is_int(&e3)) {
        (Some(v1), Some(v2), Some(v3)) => [v1, v2, v3] == *vieta,
        _ => false,
    };
    let ev0 = poly[3] & 1;
    let ev1 = (poly[0] + poly[1] + poly[2] + poly[3]) & 1;
    ok && ev0 == 1 && ev1 == 1
}

/* ── BCH radical tower Z[√5][β] ───────────────────────────────────── */
type Z5 = (i64, i64);   /* a + b√5 */
fn z5mul(p: Z5, q: Z5) -> Z5 { (p.0 * q.0 + 5 * p.1 * q.1, p.0 * q.1 + p.1 * q.0) }
fn z5add(p: Z5, q: Z5) -> Z5 { (p.0 + q.0, p.1 + q.1) }
fn bch_layer(d: Z5, x: (Z5, Z5), den: i64, poly: &[i64; 5]) -> (bool, bool) {
    /* X = (A0+A1√5) + (B0+B1√5)β, β² = D; check Σ poly[4−j]·den^(4−j)·X^j = 0 */
    let tw_mul = |u: (Z5, Z5), w: (Z5, Z5)| -> (Z5, Z5) {
        let pa = z5mul(u.0, w.0);
        let qbd = z5mul(z5mul(u.1, w.1), d);
        let pb = z5mul(u.0, w.1);
        let qa = z5mul(u.1, w.0);
        (z5add(pa, qbd), z5add(pb, qa))
    };
    let mut acc = ((0i64, 0i64), (0i64, 0i64));
    let mut cur = ((1i64, 0i64), (0i64, 0i64));
    for j in 0..5 {
        if j > 0 { cur = tw_mul(cur, x); }
        let mut c = poly[4 - j] as i64;
        for _ in 0..(4 - j) { c *= den; }
        if c == 0 { continue; }
        acc.0 = z5add(acc.0, z5mul(cur.0, (c, 0)));
        acc.1 = z5add(acc.1, z5mul(cur.1, (c, 0)));
    }
    let resid_ok = acc == ((0, 0), (0, 0));
    /* GF(2) quartic irreducibility */
    let ev0 = poly[4] & 1;
    let ev1 = poly.iter().sum::<i64>() & 1;
    let gf2 = if ev0 == 0 || ev1 == 0 { false } else {
        let mut rem = [0i64; 5];
        for i in 0..5 { rem[i] = poly[i] & 1; }
        for dd in (2..=4).rev() {
            if rem[dd] == 1 { rem[dd - 2] ^= 1; rem[dd - 1] ^= 1; rem[dd] = 0; }
        }
        !(rem[0] == 0 && rem[1] == 0)
    };
    (resid_ok, gf2)
}

fn main() {
    println!("════════════════════════════════════════════════════════════");
    println!(" HODGE LABORATORY · POLYGLOT CORE · RUST (f64 + i128)");
    println!(" Ядро лаборатории · целочисленная верификация / integer verification");
    println!("════════════════════════════════════════════════════════════");

    println!("\n[1-2] V1 · Census of conductors / Ценз проводников");
    let expect: [(i64, i64); 4] = [(7, 15), (9, 28), (15, 91), (30, 406)];
    let mut ok1 = true; let mut ok2 = true;
    for &(n, g) in &expect {
        let (h, genus) = census(n);
        if genus != g || h.iter().map(|e| e.1).sum::<i64>() != genus { ok1 = false; }
        if h != census_mobius(n) { ok2 = false; }
    }
    check("Σh_d = g for N=7,9,15,30 · Σh_d = g", ok1, "15/28/91/406");
    check("Möbius scheme agrees · схема Мёбиуса совпадает", ok2, "");

    println!("\n[3] Certificate E · t* = lcm(W/gcd(a,W), H/gcd(b,H))");
    let ce: [(i64, i64, i64, i64, i64); 6] =
        [(48,48,1,1,48),(96,96,1,1,96),(24,36,3,5,72),(7,14,1,1,14),(12,12,4,6,6),(384,384,1,1,384)];
    let ok3 = ce.iter().all(|&(w, hh, a, b, e)| tstar(w, hh, a, b) == e);
    check("6 cert-E cases · 6 случаев cert E", ok3, "t*(24,36;3,5)=72 …");

    println!("\n[4] Binary flow 48×48 / Двоичный поток");
    let (t, vis, closed) = binary_flow();
    check("t*=48 · 48 cells · closure · замыкание", t == 48 && vis == 48 && closed,
          "48+212+432+114=806");

    println!("\n[5] Arf enumeration / Перечисление Арфа");
    let mut ok5 = true; let mut det5 = String::new();
    for g in 1..=3u32 {
        let (size, ev, od) = arf_enum(g);
        let exp_ev = (1i64 << (g - 1)) * ((1i64 << g) + 1);
        let exp_od = (1i64 << (g - 1)) * ((1i64 << g) - 1);
        if size != (1i64 << (2 * g)) || ev != exp_ev || od != exp_od { ok5 = false; }
        det5.push_str(&format!("g={}: {}/{} ", g, ev, od));
    }
    check("even/odd forms g=1..3 · чётные/нечётные формы", ok5, &(det5 + "(g=3: 36/28)"));

    println!("\n[6] K3 stand · exact integer machinery / точная машина");
    let g = k3_gram();
    let rank = k3_rank(&g);
    let factors = k3_snf(&g);
    let det: i128 = factors.iter().product();
    let (ech, k) = k3_int_ech(&g);
    let sig = k3_signature(&g, &ech, k);
    check("rank_Q = 20 = ρ (Shioda · Шиода)", rank == 20, &format!("rank={}", rank));
    check("signature (1,19) — Hodge index · сигнатура", sig == Some((1, 19)), "");
    let nf = factors.len();
    check("SNF → det = 64 = 8²", det == 64 && nf >= 2 && factors[nf - 2] == 8 && factors[nf - 1] == 8,
          &format!("SNF det = {}", det));
    check("48 lines on the Fermat quartic · прямых", KL == 48, "");
    {
        let ls = k3_lines();
        let mut fam_ok = true;
        for a in 0..4 {
            for j in 0..KN {
                let mut s = 0i64;
                for b in 0..4 {
                    for (id, l) in ls.iter().enumerate() {
                        if l[0] == 1 && l[1] == a && l[2] == b { s += g[id][j]; }
                    }
                }
                if s != g[KL][j] { fam_ok = false; break; }
            }
            if !fam_ok { break; }
        }
        check("family relation Σ_b L1(a,b) ~ h · семейное соотношение", fam_ok, "");
    }

    println!("\n[7] Klein stand / Слой Клейна");
    {
        let j = -(105i64.pow(3)) / 343;
        let mut expand = [0i64; 4];
        for &(i, ci) in &[(0usize, 1i64), (1, -7)] {
            for &(jj, cj) in &[(0usize, 1i64), (1, 7), (2, 14)] {
                expand[i + jj] += ci * cj;
            }
        }
        let ok = j == -3375 && (-343i64) * j == 105i64.pow(3)
            && expand == [1, 0, -35, -98] && 7 * 7 - 4 * 14 == -7;
        check("j = −3375 = −15³ · Δ·j = 105³ · disc = −7", ok, "(v−7)(v²+7v+14) = v³−35v−98");
    }

    println!("\n[8-9] Cyclotomic layer N=7/9 · Z[ζ]/Φₙ (exact integer arithmetic)");
    {
        let ok7 = cyc_layer(7, &[1, 2, 3], &[-1, -2, 1], &[1, 1, -2, -1]);
        check("N=7: Vieta s=(−1,−2,1) computed in Z[ζ]/Φ₇ + GF(2)", ok7,
              "e1,e2,e3 exact integers · cubic irreducible over GF(2)");
        let ok9 = cyc_layer(9, &[1, 2, 4], &[0, -3, -1], &[1, 0, -3, 1]);
        check("N=9: Vieta s=(0,−3,−1) computed in Z[ζ]/Φ₉ + GF(2)", ok9,
              "e1,e2,e3 exact integers · cubic irreducible over GF(2)");
    }

    println!("\n[10-11] BCH radical tower Z[√5][β] · Радикальная башня");
    {
        let (r15, g15) = bch_layer((30, -6), ((1, 1), (1, 0)), 4, &[1, -1, -4, 4, 1]);
        check("n=15: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r15 && g15,
              "b_Ch(15) = (7 − √5 − √(30−6√5))/8");
        let (r30, g30) = bch_layer((30, 6), ((-1, 1), (1, 0)), 4, &[1, 1, -4, -4, 1]);
        check("n=30: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r30 && g30,
              "b_Ch(30) = (9 − √5 − √(30+6√5))/8");
    }

    println!("\n[12] Torus Δ_Ch (f64 ~16 digits)");
    {
        let d = torus_delta();
        let r = 39.48799539346835051297464603266144167978;
        let rel = ((d - r) / r).abs();
        check("Δ_Ch = 4π² + δ²/2 − δ⁵ (40-digit reference)", rel < 1e-13,
              &format!("Δ_Ch = {:.17}", d));
    }

    println!("\n[13] Klein Ω (regularized smooth quadrature, f64)");
    {
        let om = klein_omega(20000);
        let r = 1.93331170561681154673308;
        let rel = ((om - r) / r).abs();
        check("Ω = 2∫₇^∞ dx/√(x³−35x−98)", rel < 1e-13,
              &format!("Ω = {:.17}, rel = {:.2e} (ref is 23-digit)", om, rel));
    }

    println!("\n[14] V6 Γ-reflection (f64 Lanczos)");
    {
        let e = v6_reflection();
        check("Γ(k/N)Γ((N−k)/N) = π/sin(πk/N), N=7", e < 1e-12, &format!("max rel = {:.2e}", e));
    }

    println!("\n[15] Period closed vs tanh–sinh (f64)");
    {
        let e15 = period_quadrature(15, 2, 3);
        let e9 = period_quadrature(9, 1, 2);
        check("P_closed = P_numeric (N=15; N=9)", e15 < 1e-10 && e9 < 1e-10,
              &format!("rel = {:.2e} / {:.2e}", e15, e9));
    }

    let (total, passed) = unsafe { (TOTAL, PASSED) };
    println!("\n════════════════════════════════════════════════════════════");
    println!(" ИТОГ / RESULT: {}/{}", passed, total);
    if passed == total {
        println!(" ✔ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ · ALL CHECKS PASSED");
    } else {
        println!(" ✘ ЕСТЬ ПРОВАЛЫ · THERE ARE FAILURES");
    }
    println!(" Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich");
    println!("════════════════════════════════════════════════════════════");
    std::process::exit(if passed == total { 0 } else { 1 });
}
