#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════
 HODGE LABORATORY — POLYGLOT CORE · PYTHON
 Ядро лаборатории на чистом Python (stdlib: decimal, fractions, math).
 The laboratory core in pure Python (standard library only).

 Запуск / Run:  python3 verify_core.py
 Автор программы / Program author: Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
 Репозиторий / Repository: wild8highlander/hodge-laboratory
 Лицензия / License: индивидуальная эксклюзивная / individual exclusive
═══════════════════════════════════════════════════════════════════════════
"""
from fractions import Fraction
from math import gcd, gamma, pi as PI_F64, sin
from decimal import Decimal, getcontext

getcontext().prec = 60
D = Decimal

# ── high-precision π (Chudnovsky, exact integer terms) ──────────────
def pi_decimal():
    from math import factorial as fact
    getcontext().prec += 8
    C = D(426880) * D(10005).sqrt()
    A, B, X = D(13591409), D(545140134), 262537412640768000  # 640320³
    S = D(0)
    for k in range(12):
        num = fact(6 * k) * (A + B * k)
        den = fact(3 * k) * fact(k) ** 3 * X ** k
        S += num / D(den) if k % 2 == 0 else -num / D(den)
    val = C / S
    getcontext().prec -= 8
    return +val

PI = pi_decimal()

def _reduce_2pi(x):
    two_pi = 2 * PI
    n = int(x / two_pi)
    x = x - n * two_pi
    if x > PI:
        x -= two_pi
    return x

def d_sin(x):
    x = _reduce_2pi(x if x >= 0 else -x)
    if x < 0:
        x = -x  # odd symmetry after reduction handled via sign of result
    neg = False
    x0 = _reduce_2pi(abs(x))
    term, s, k = x0, x0, 0
    while True:
        k += 1
        term = -term * x0 * x0 / D((2 * k) * (2 * k + 1))
        s += term
        if abs(term) < D(1) / D(10 ** (getcontext().prec - 2)):
            break
    return s

def d_cos(x):
    x0 = _reduce_2pi(abs(x))
    term, s, k = D(1), D(1), 0
    while True:
        k += 1
        term = -term * x0 * x0 / D((2 * k - 1) * (2 * k))
        s += term
        if abs(term) < D(1) / D(10 ** (getcontext().prec - 2)):
            break
    return s

def d_tanh(x):
    e2 = (2 * x).exp()
    return (e2 - 1) / (e2 + 1)

def d_sinh(x):
    e = x.exp()
    return (e - 1 / e) / 2

# ═══ 1–2. V1: census (direct + Möbius) ═══════════════════════════════════
def census(N):
    h, byD = {}, {}
    for a in range(1, N):
        for b in range(1, N - a):
            d = N // gcd(gcd(N, a), b)
            h[d] = h.get(d, 0) + 1
            byD.setdefault(d, []).append((a, b))
    genus = (N - 1) * (N - 2) // 2
    return h, byD, genus

def mobius(m):
    if m == 1:
        return 1
    result, x = 1, m
    q = 2
    while q * q <= x:
        if x % q == 0:
            x //= q
            if x % q == 0:
                return 0
            result = -result
        q += 1
    if x > 1:
        result = -result
    return result

def census_mobius(N):
    c = lambda k: (k - 1) * (k - 2) // 2 if k >= 3 else 0
    out = {}
    for d in range(2, N + 1):
        if N % d:
            continue
        s = sum(mobius(m) * c(d // m) for m in range(1, d + 1) if d % m == 0)
        if s:
            out[d] = s
    return out

# ═══ 3–4. cert E: t* and the binary flow ═════════════════════════════════
def lcm(a, b):
    return 0 if a == 0 or b == 0 else abs(a // gcd(a, b) * b)

def tstar(W, H, a, b):
    return lcm(W // gcd(a, W), H // gcd(b, H))

CERT_E_CASES = [(48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
                (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384)]

def binary_flow():
    W, H, a, b = 48, 48, 1, 1
    t = tstar(W, H, a, b)
    x = y = dx = dy = 0
    visited = set()
    for _ in range(t):
        visited.add((x, y))
        x = (x + a) % W
        y = (y + b) % H
        dx = (dx + a) % W
        dy = (dy + b) % H
    return t, len(visited), dx == 0 and dy == 0

# ═══ 5. Arf enumeration ═══════════════════════════════════════════════════
def arf_enumeration(g):
    n = 2 * g
    size = 1 << n
    half = size >> 1
    shift = 1 << (g - 1)
    pairs = [(2 * i, 2 * i + 1) for i in range(g)]
    even = odd = 0
    for basis in range(size):
        zeros = 0
        for v in range(size):
            qv = 0
            for i in range(n):
                if (v >> i) & 1:
                    qv ^= (basis >> i) & 1
            for (i, j) in pairs:
                if ((v >> i) & 1) and ((v >> j) & 1):
                    qv ^= 1
            if qv == 0:
                zeros += 1
        if zeros == half + shift:
            even += 1
        else:
            odd += 1
    return size, even, odd

# ═══ 6. K3: exact rank · SNF · signature ══════════════════════════════════
def k3_lines():
    return [(f, a, b) for f in (1, 2, 3) for a in range(4) for b in range(4)]

def k3_inter(l1, l2):
    if l1 == l2:
        return -2
    f1, a1, b1 = l1
    f2, a2, b2 = l2
    if f1 == f2:
        return 1 if (a1 == a2) != (b1 == b2) else 0
    ff = tuple(sorted((f1, f2)))
    if ff == (1, 2):
        return 1 if (a1 + b2 - a2 - b1) % 4 == 0 else 0
    if ff == (1, 3):
        if f1 == 1:
            return 1 if (a2 - a1 - b1 - b2 - 1) % 4 == 0 else 0
        return 1 if (a1 - a2 - b2 - b1 - 1) % 4 == 0 else 0
    return 1 if (a1 + b1 - a2 - b2) % 4 == 0 else 0

def k3_gram():
    ls = k3_lines()
    n = len(ls)
    G = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(i, n):
            G[i][j] = G[j][i] = k3_inter(ls[i], ls[j])
    for i in range(n):
        G[i][n] = G[n][i] = 1
    G[n][n] = 4
    return G, ls

def rank_fractions(Mint):
    n = len(Mint)
    M = [[Fraction(v) for v in row] for row in Mint]
    r = 0
    for c in range(n):
        if r >= n:
            break
        piv = next((i for i in range(r, n) if M[i][c] != 0), -1)
        if piv < 0:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        for i in range(r + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / pv
                for j in range(c, n):
                    M[i][j] -= f * M[r][j]
        r += 1
    return r

def snf(mat):
    a = [row[:] for row in mat]
    rows, cols = len(a), len(a[0])
    res = []
    for t in range(min(rows, cols)):
        while True:
            p, pi_, pj = 0, -1, -1
            for i in range(t, rows):
                for j in range(t, cols):
                    v = abs(a[i][j])
                    if v != 0 and (pi_ < 0 or v < p):
                        p, pi_, pj = v, i, j
            if pi_ < 0:
                return res
            if pi_ != t:
                a[t], a[pi_] = a[pi_], a[t]
            if pj != t:
                for i in range(rows):
                    a[i][t], a[i][pj] = a[i][pj], a[i][t]
            piv = a[t][t]
            for i in range(t + 1, rows):
                q = a[i][t] // piv
                if q != 0:
                    for j in range(t, cols):
                        a[i][j] -= q * a[t][j]
            for j in range(t + 1, cols):
                q = a[t][j] // piv
                if q != 0:
                    for i in range(rows):
                        a[i][j] -= q * a[i][t]
            if all(a[i][j] % piv == 0 for i in range(t + 1, rows) for j in range(t + 1, cols)):
                break
        res.append(abs(a[t][t]))
    return res

def int_ech_rows(Mint):
    n = len(Mint)
    M = [[Fraction(v) for v in row] for row in Mint]
    rowsF, r = [], 0
    for c in range(n):
        if r >= n:
            break
        piv = next((i for i in range(r, n) if M[i][c] != 0), -1)
        if piv < 0:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                for j in range(c, n):
                    M[i][j] -= f * M[r][j]
        rowsF.append(M[r][:])
        r += 1
    out = []
    for row in rowsF:
        L = 1
        for x in row:
            L = L // gcd(L, x.denominator) * x.denominator
        ints = [int(x * L) for x in row]
        g = 0
        for v in ints:
            g = gcd(g, abs(v))
        if g > 1:
            ints = [v // g for v in ints]
        out.append(ints)
    return out

def exact_signature(G, ech):
    n, k = len(G), len(ech)
    S = [[0] * k for _ in range(k)]
    for i in range(k):
        T = [0] * n
        for t in range(n):
            if ech[i][t] == 0:
                continue
            cit = ech[i][t]
            for u in range(n):
                T[u] += cit * G[t][u]
        for j in range(k):
            s = sum(T[u] * ech[j][u] for u in range(n))
            S[i][j] = S[j][i] = s
    A = [[Fraction(S[i][j]) for j in range(k)] for i in range(k)]
    diag = []
    for i in range(k):
        s = Fraction(0)
        for t in range(i):
            s += A[t][i] * A[t][i] * diag[t]
        d = A[i][i] - s
        if d == 0:
            return None
        diag.append(d)
        for j in range(i + 1, k):
            s2 = Fraction(0)
            for t in range(i):
                s2 += A[t][i] * A[t][j] * diag[t]
            v = (Fraction(S[i][j]) - s2) / diag[i]
            A[i][j] = A[j][i] = v
    pos = sum(1 for d in diag if d > 0)
    neg = sum(1 for d in diag if d < 0)
    return pos, neg

def k3_invariants():
    G, ls = k3_gram()
    n = len(G)
    rank = rank_fractions(G)
    factors = snf([r[:] for r in G])
    det = 1
    for v in factors:
        det *= v
    sig = exact_signature(G, int_ech_rows(G))
    idx = {}
    for i, l in enumerate(ls):
        idx[l] = i
    fam_ok = True
    for a in range(4):
        for j in range(n):
            s = sum(G[idx[(1, a, b)]][j] for b in range(4))
            if s != G[n - 1][j]:
                fam_ok = False
                break
        if not fam_ok:
            break
    return rank, det, factors, sig, fam_ok, len(ls)

# ═══ 7. Klein exact layer ═════════════════════════════════════════════════
def klein_exact():
    j = -(105 ** 3) // 343
    c1 = (j == -3375) and ((-15) ** 3 == -3375)
    c2 = (-343) * j == 105 ** 3 == 1157625
    expand = [0, 0, 0, 0]
    for i, ci in [(0, 1), (1, -7)]:
        for jj, cj in [(0, 1), (1, 7), (2, 14)]:
            expand[i + jj] += ci * cj
    c3 = expand == [1, 0, -35, -98]
    c4 = 7 ** 2 - 4 * 14 == -7
    return all([c1, c2, c3, c4])

# ═══ 8–9. Cyclotomic exact layer N=7/9 ════════════════════════════════════
CYC = {
    7: {'units': [1, 2, 3], 'phi': [1, 1, 1, 1, 1, 1, 1], 'vieta': [-1, -2, 1],
        'poly': [1, 1, -2, -1]},
    9: {'units': [1, 2, 4], 'phi': [1, 0, 0, 1, 0, 0, 1], 'vieta': [0, -3, -1],
        'poly': [1, 0, -3, 1]},
}

def poly_mul(a, b):
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                res[i + j] += ai * bj
    return res

def poly_mod_phi(a, phi):
    a = a[:]
    dphi = len(phi) - 1
    for i in range(len(a) - dphi):
        if not a[i]:
            continue
        for j in range(1, len(phi)):
            a[i + j] -= a[i] * phi[j]
        a[i] = 0
    while a and a[0] == 0:
        a.pop(0)
    return a if a else [0]

def cyc_exact_layer(n):
    spec = CYC[n]
    phi = spec['phi']
    els = []
    for k in spec['units']:
        p = [0] * (n + 1)
        p[k] += 1
        p[n - k] += 1
        els.append(poly_mod_phi(p, phi))
    def padd(p, q):
        out = [0] * max(len(p), len(q))
        for i in range(len(p)):
            out[len(out) - len(p) + i] += p[i]
        for i in range(len(q)):
            out[len(out) - len(q) + i] += q[i]
        return poly_mod_phi(out, phi)
    def pmul(p, q):
        return poly_mod_phi(poly_mul(p, q), phi)
    def norm(p):
        while len(p) > 1 and p[0] == 0:
            p.pop(0)
        return p
    e1 = norm(padd(els[0], padd(els[1], els[2])))
    e2 = norm(padd(padd(pmul(els[0], els[1]), pmul(els[0], els[2])), pmul(els[1], els[2])))
    e3 = norm(pmul(els[0], pmul(els[1], els[2])))
    vieta_ok = (len(e1) == 1 and len(e2) == 1 and len(e3) == 1 and
                [e1[0], e2[0], e3[0]] == spec['vieta'])
    c = spec['poly']
    ev0 = c[3] & 1
    ev1 = (c[0] + c[1] + c[2] + c[3]) & 1
    gf2 = (ev0 == 1 and ev1 == 1)
    return vieta_ok, gf2, (e1[0] if len(e1) == 1 else None,
                           e2[0] if len(e2) == 1 else None,
                           e3[0] if len(e3) == 1 else None)

# ═══ 10–11. BCH radical tower Z[√5][β] ════════════════════════════════════
BCH_RADICALS = {
    15: {'D': (30, -6), 'm': ((1, 1), (1, 0)), 'den': 4, 'poly': [1, -1, -4, 4, 1]},
    30: {'D': (30, 6), 'm': ((-1, 1), (1, 0)), 'den': 4, 'poly': [1, 1, -4, -4, 1]},
}

def z5mul(p, q):
    return (p[0] * q[0] + 5 * p[1] * q[1], p[0] * q[1] + p[1] * q[0])

def z5add(p, q):
    return (p[0] + q[0], p[1] + q[1])

def tw_mul(u, v, Dq):
    return (z5add(z5mul(u[0], v[0]), z5mul(z5mul(u[1], v[1]), Dq)),
            z5add(z5mul(u[0], v[1]), z5mul(u[1], v[0])))

def tw_add(u, v):
    return (z5add(u[0], v[0]), z5add(u[1], v[1]))

def tw_scale(u, k):
    return ((u[0][0] * k, u[0][1] * k), (u[1][0] * k, u[1][1] * k))

def tw_pow_int(u, e, Dq):
    r = ((1, 0), (0, 0))
    b = u
    while e:
        if e & 1:
            r = tw_mul(r, b, Dq)
        b = tw_mul(b, b, Dq)
        e >>= 1
    return r

def bch_exact_layer(n):
    spec = BCH_RADICALS[n]
    Dq = spec['D']
    den = spec['den']
    X = spec['m']
    poly = spec['poly']
    deg = len(poly) - 1
    acc = ((0, 0), (0, 0))
    for j in range(len(poly)):
        c = poly[deg - j] * den ** (deg - j)
        if not c:
            continue
        pw = tw_pow_int(X, j, Dq)
        acc = tw_add(acc, tw_scale(pw, c))
    resid_ok = acc == ((0, 0), (0, 0))
    c = spec['poly']
    ev0 = c[4] & 1
    ev1 = sum(c) & 1
    if ev0 == 0 or ev1 == 0:
        gf2 = False
    else:
        rem = [v & 1 for v in c]
        for dd in (4, 3):
            if rem[dd]:
                rem[dd - 2] ^= 1
                rem[dd - 1] ^= 1
                rem[dd] = 0
        gf2 = not (rem[0] == 0 and rem[1] == 0)
    return resid_ok, gf2

# ═══ 12. torus Δ_Ch ═══════════════════════════════════════════════════════
DELTA_REF = D('39.48799539346835051297464603266144167978')

def torus_delta_decimal():
    delta = PI / 4
    lam = 4 * PI * PI
    return lam + delta * delta / 2 - delta ** 5

# ═══ 13. Klein Ω quadrature ═══════════════════════════════════════════════
OMEGA_REF = D('1.93331170561681154673308')

def tanh_sinh_nodes(K, h):
    """u = ½(1 + tanh(π/2·sinh t)), w = (π/4)·cosh t/cosh²(π/2·sinh t)·h."""
    nodes = []
    hh = D(str(h))
    for k in range(-K, K + 1):
        t = D(k) * hh
        sh = d_sinh(t)
        half_pi_sh = PI / 2 * sh
        u = (1 + d_tanh(half_pi_sh)) / 2
        cht = (t.exp() + 1 / t.exp()) / 2
        esh = half_pi_sh.exp()
        ch_sh = (esh + 1 / esh) / 2
        w = (PI / 4) * cht / (ch_sh * ch_sh) * hh
        if 0 < u < 1:
            nodes.append((u, w))
    return nodes

def klein_omega_decimal(K=320, h='0.025'):
    nodes = tanh_sinh_nodes(K, h)
    total = D(0)
    for u, w in nodes:
        one = 1 - u
        x7 = u / one
        x = x7 + 7
        quad = x * x + 7 * x + 14
        total += w * 2 / (one * one * (x7 * quad).sqrt())
    return total

# ═══ 14. V6 Γ-reflection ══════════════════════════════════════════════════
def v6_reflection_f64():
    worst = 0.0
    N = 7
    for k in range(1, N):
        lhs = gamma(k / N) * gamma((N - k) / N)
        rhs = PI_F64 / sin(PI_F64 * k / N)
        worst = max(worst, abs(lhs - rhs) / abs(rhs))
    return worst

# ═══ 15. period closed vs tanh–sinh (f64) ═════════════════════════════════
def period_quadrature_f64(N, a, b, K=150, h=0.05):
    import math
    A_, B_ = a / N, b / N
    nodes = []
    for k in range(-K, K + 1):
        t = k * h
        st = math.sinh(t)
        z = abs(PI_F64 / 2 * st)
        if z > 350:  # u saturates at 1; weight < 1e−300
            continue
        u = 0.5 * (1 + math.tanh(PI_F64 / 2 * st))
        w = (PI_F64 / 4) * math.cosh(t) / (math.cosh(z) * math.cosh(z)) * h
        if 0.0 < u < 1.0:
            nodes.append((u, w))
    f2A = 2.0 ** (-A_)
    f2B = 2.0 ** (-B_)
    i1 = i2 = 0.0
    for u, w in nodes:
        i1 += N * w * f2A * u ** (a - 1) * (1 - u ** N / 2) ** (B_ - 1)
        i2 += N * w * f2B * u ** (b - 1) * (1 - u ** N / 2) ** (A_ - 1)
    closed = gamma(a / N) * gamma(b / N) / gamma((a + b) / N)
    return abs((i1 + i2) - closed) / abs(closed)

# ══════════════════════════════════════════════════════════════════════════
CHECKS = []

def check(name_en, ok, detail=""):
    CHECKS.append((ok, name_en))
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name_en}" + (f"  · {detail}" if detail else ""))

def main():
    print("════════════════════════════════════════════════════════════")
    print(" HODGE LABORATORY · POLYGLOT CORE · PYTHON")
    print(" Ядро лаборатории · целочисленная верификация / integer verification")
    print("════════════════════════════════════════════════════════════")

    print("\n[1-2] V1 · Census of conductors / Ценз проводников")
    expect = {7: 15, 9: 28, 15: 91, 30: 406}
    ok1 = ok2 = True
    hmap = {}
    for N in (7, 9, 15, 30):
        h, byD, genus = census(N)
        hm = census_mobius(N)
        ok1 &= (sum(h.values()) == genus == expect[N])
        ok2 &= (h == hm)
        hmap[N] = h
    check("Σh_d = g for N=7,9,15,30 · Σh_d = g", ok1,
          f"15/28/91/406 · N=30: {hmap[30]}")
    check("Möbius scheme agrees · схема Мёбиуса совпадает", ok2)

    print("\n[3] Certificate E · t* = lcm(W/gcd(a,W), H/gcd(b,H))")
    ok3 = all(tstar(W, H, a, b) == exp for W, H, a, b, exp in CERT_E_CASES)
    check("6 cert-E cases · 6 случаев cert E", ok3,
          "t*(48,48;1,1)=48 · t*(24,36;3,5)=72 · t*(12,12;4,6)=6 …")

    print("\n[4] Binary flow 48×48 / Двоичный поток")
    t, visited, closed = binary_flow()
    check("t*=48 · 48 cells · closure · замыкание", t == 48 and visited == 48 and closed,
          f"t*={t}, visited={visited}, closed={closed} · 48+212+432+114=806")

    print("\n[5] Arf enumeration / Перечисление Арфа")
    arf_ok = True
    arf_det = []
    for g in (1, 2, 3):
        size, even, odd = arf_enumeration(g)
        exp_even = (1 << (g - 1)) * ((1 << g) + 1)
        exp_odd = (1 << (g - 1)) * ((1 << g) - 1)
        arf_ok &= (size == (1 << 2 * g) and even == exp_even and odd == exp_odd)
        arf_det.append(f"g={g}: {even}/{odd}")
    check("even/odd forms g=1..3 · чётные/нечётные формы", arf_ok,
          " · ".join(arf_det) + " (g=3: 36/28)")

    print("\n[6] K3 stand · exact integer machinery / точная машина")
    rank, det, factors, sig, fam_ok, nlines = k3_invariants()
    check("48 lines on the Fermat quartic · прямых на квартике", nlines == 48)
    check("rank_Q = 20 = ρ (Shioda · Шиода)", rank == 20, f"rank={rank}")
    check("signature (1,19) — Hodge index · сигнатура", sig == (1, 19), f"sig={sig}")
    check("SNF → det = 64 = 8²", det == 64 and factors[-2:] == [8, 8],
          "factors=[1×18, 8, 8]" + f", det={det}")
    check("family relation Σ_b L1(a,b) ~ h · семейное соотношение", fam_ok)

    print("\n[7] Klein stand / Слой Клейна")
    check("j = −3375 = −15³ · Δ·j = 105³ · disc = −7", klein_exact(),
          "(v−7)(v²+7v+14) = v³−35v−98")

    print("\n[8-9] Cyclotomic layer N=7/9 / Циклотомический слой")
    v7, gf7, sy7 = cyc_exact_layer(7)
    v9, gf9, sy9 = cyc_exact_layer(9)
    check("N=7: Vieta in Z[ζ]/Φ₇ + GF(2) · Виета", v7 and gf7,
          f"s = {list(sy7)} · cubic irreducible over GF(2)")
    check("N=9: Vieta in Z[ζ]/Φ₉ + GF(2) · Виета", v9 and gf9,
          f"s = {list(sy9)}")

    print("\n[10-11] BCH radical tower / Радикальная башня")
    r15, g15 = bch_exact_layer(15)
    r30, g30 = bch_exact_layer(30)
    check("n=15: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r15 and g15,
          "b_Ch(15) = (7 − √5 − √(30−6√5))/8")
    check("n=30: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)", r30 and g30,
          "b_Ch(30) = (9 − √5 − √(30+6√5))/8")

    print("\n[12] Torus Δ_Ch · 60-digit arithmetic / 60-значная арифметика")
    delta = torus_delta_decimal()
    dev = abs(delta - DELTA_REF) / DELTA_REF
    check("Δ_Ch = 4π² + δ²/2 − δ⁵ (40-digit reference)", dev < D(10) ** -38,
          f"Δ_Ch = {str(delta)[:42]}")

    print("\n[13] Klein Ω quadrature / Квадратура Клейна")
    omega = klein_omega_decimal()
    eom = abs(omega - OMEGA_REF) / OMEGA_REF
    check("Ω = 2∫₇^∞ dx/√(x³−35x−98)", eom < D(10) ** -22,
          f"Ω = {str(omega)[:26]}, rel = {eom:.2e} (ref is 23-digit)")

    print("\n[14] V6 Γ-reflection / Формула отражения")
    e6 = v6_reflection_f64()
    check("Γ(k/N)Γ((N−k)/N) = π/sin(πk/N), N=7", e6 < 1e-12, f"max rel = {e6:.2e}")

    print("\n[15] Period closed vs tanh–sinh / Периоды")
    e15 = period_quadrature_f64(15, 2, 3)
    e9 = period_quadrature_f64(9, 1, 2)
    check("P_closed = P_numeric (N=15; N=9)", e15 < 1e-10 and e9 < 1e-10,
          f"rel = {e15:.2e} / {e9:.2e}")

    total = len(CHECKS)
    passed = sum(1 for ok, _ in CHECKS if ok)
    print("\n════════════════════════════════════════════════════════════")
    print(f" ИТОГ / RESULT: {passed}/{total}")
    if passed == total:
        print(" ✔ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ · ALL CHECKS PASSED")
    else:
        print(" ✘ ЕСТЬ ПРОВАЛЫ · THERE ARE FAILURES")
    print(" Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich")
    print("════════════════════════════════════════════════════════════")
    return 0 if passed == total else 1

if __name__ == "__main__":
    raise SystemExit(main())
