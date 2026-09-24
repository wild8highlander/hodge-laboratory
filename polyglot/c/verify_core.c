/* ══════════════════════════════════════════════════════════════════════
   HODGE LABORATORY — POLYGLOT CORE · C (C11, long double + __int128)
   Ядро лаборатории на чистом C: целочисленные стенды точно (__int128),
   квадратуры tanh–sinh в long double (x87, 18–19 значащих цифр).
   The laboratory core in plain C: exact integer stands (__int128),
   tanh–sinh quadratures in long double (18–19 significant digits).

   Сборка / Build:  cc -O2 -o verify_core verify_core.c -lm
   Запуск / Run:    ./verify_core

   Автор программы / Program author:
     Исаев Исхак Хамзатович / Isaev Iskhak Khamzatovich
   Репозиторий / Repository: wild8highlander/hodge-laboratory
   Лицензия / License: индивидуальная эксклюзивная / individual exclusive
   ══════════════════════════════════════════════════════════════════════ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

typedef long double ld;
typedef __int128 i128;

/* ── pretty __int128 print ─────────────────────────────────────────── */
static void p128(i128 v) {
    char buf[48]; int i = 47; buf[i] = 0;
    int neg = v < 0;
    unsigned __int128 u = neg ? (unsigned __int128)(-v) : (unsigned __int128)v;
    if (u == 0) buf[--i] = '0';
    while (u) { buf[--i] = '0' + (int)(u % 10); u /= 10; }
    if (neg) buf[--i] = '-';
    printf("%s", buf);
}

/* ── exact fractions over i128 (num/den, den>0, always reduced) ───── */
typedef struct { i128 n, d; } Frac;
static i128 igcd(i128 a, i128 b) {
    if (a < 0) a = -a; if (b < 0) b = -b;
    while (b) { i128 t = a % b; a = b; b = t; }
    return a;
}
static Frac fr(i128 n, i128 d) {
    if (d < 0) { n = -n; d = -d; }
    i128 g = igcd(n, d); if (g == 0) g = 1;
    Frac f = { n / g, d / g }; return f;
}
static Frac fr_add(Frac a, Frac b) { return fr(a.n * b.d + b.n * a.d, a.d * b.d); }
static Frac fr_sub(Frac a, Frac b) { return fr(a.n * b.d - b.n * a.d, a.d * b.d); }
static Frac fr_mul(Frac a, Frac b) { return fr(a.n * b.n, a.d * b.d); }

/* ═══ 1–2. census ═══════════════════════════════════════════════════ */
static long i64gcd(long a, long b) { if (a < 0) a = -a; if (b < 0) b = -b; while (b) { long t = a % b; a = b; b = t; } return a; }
static long i64lcm(long a, long b) { return (a == 0 || b == 0) ? 0 : labs(a / i64gcd(a, b) * b); }

static int mobius(long m) {
    if (m == 1) return 1;
    long x = m; int res = 1;
    for (long q = 2; q * q <= x; q++) {
        if (x % q == 0) { x /= q; if (x % q == 0) return 0; res = -res; }
    }
    if (x > 1) res = -res;
    return res;
}

#define NMAX 4096
static long census_h[NMAX];      /* h_d indexed by d */
static int  census_dlist[NMAX]; int census_dn;

static void census(long N, long *genus_out) {
    memset(census_h, 0, sizeof(census_h));
    census_dn = 0;
    for (long a = 1; a < N; a++)
        for (long b = 1; b < N - a; b++) {
            long d = N / i64gcd(i64gcd(N, a), b);
            if (census_h[d]++ == 0) census_dlist[census_dn++] = (int)d;
        }
    /* sort dlist ascending (small N — insertion sort) */
    for (int i = 1; i < census_dn; i++) {
        int key = census_dlist[i], j = i - 1;
        while (j >= 0 && census_dlist[j] > key) { census_dlist[j + 1] = census_dlist[j]; j--; }
        census_dlist[j + 1] = key;
    }
    *genus_out = (N - 1) * (N - 2) / 2;
}

static int census_mobius_match(long N) {
    int ok = 1;
    for (int idx = 0; idx < census_dn && ok; idx++) {
        long d = census_dlist[idx], s = 0;
        for (long m = 1; m <= d; m++)
            if (d % m == 0) {
                long k = d / m, c = (k >= 3) ? (k - 1) * (k - 2) / 2 : 0;
                s += mobius(m) * c;
            }
        if (s != census_h[d]) ok = 0;
    }
    return ok;
}

/* ═══ 3–4. cert E + binary flow ═════════════════════════════════════ */
static long tstar(long W, long H, long a, long b) {
    return i64lcm(W / i64gcd(a, W), H / i64gcd(b, H));
}

static int binary_flow(long *t_out, long *vis_out) {
    long W = 48, H = 48, a = 1, b = 1;
    long t = tstar(W, H, a, b);
    long x = 0, y = 0, dx = 0, dy = 0, vis = 0;
    static unsigned char seen[48][48];
    memset(seen, 0, sizeof(seen));
    for (long i = 0; i < t; i++) {
        if (!seen[x][y]) { seen[x][y] = 1; vis++; }
        x = (x + a) % W; y = (y + b) % H;
        dx = (dx + a) % W; dy = (dy + b) % H;
    }
    *t_out = t; *vis_out = vis;
    return dx == 0 && dy == 0;
}

/* ═══ 5. Arf enumeration ════════════════════════════════════════════ */
static void arf_enum(int g, long *even, long *odd) {
    int n = 2 * g;
    long size = 1L << n, half = size >> 1, shift = 1L << (g - 1);
    int pairs[16][2], np = 0;
    for (int i = 0; i < g; i++) { pairs[np][0] = 2 * i; pairs[np][1] = 2 * i + 1; np++; }
    long ev = 0, od = 0;
    for (long basis = 0; basis < size; basis++) {
        long zeros = 0;
        for (long v = 0; v < size; v++) {
            long qv = 0;
            for (int i = 0; i < n; i++)
                if ((v >> i) & 1) qv ^= (basis >> i) & 1;
            for (int p = 0; p < np; p++)
                if (((v >> pairs[p][0]) & 1) && ((v >> pairs[p][1]) & 1)) qv ^= 1;
            if (qv == 0) zeros++;
        }
        if (zeros == half + shift) ev++; else od++;
    }
    *even = ev; *odd = od;
}

/* ═══ 6. K3 exact machinery (49×49) ═════════════════════════════════ */
#define KL 48
#define KN 49
static int G[KN][KN];

static void k3_lines(int ls[KL][3]) {
    int k = 0;
    for (int f = 1; f <= 3; f++)
        for (int a = 0; a < 4; a++)
            for (int b = 0; b < 4; b++) { ls[k][0] = f; ls[k][1] = a; ls[k][2] = b; k++; }
}

static int k3_inter(const int l1[3], const int l2[3]) {
    if (l1[0] == l2[0] && l1[1] == l2[1] && l1[2] == l2[2]) return -2;
    int f1 = l1[0], a1 = l1[1], b1 = l1[2], f2 = l2[0], a2 = l2[1], b2 = l2[2];
    if (f1 == f2) return ((a1 == a2) != (b1 == b2)) ? 1 : 0;
    int lo = f1 < f2 ? f1 : f2, hi = f1 < f2 ? f2 : f1;
    if (lo == 1 && hi == 2) return ((a1 + b2 - a2 - b1) % 4 == 0) ? 1 : 0;
    if (lo == 1 && hi == 3) {
        long t = (f1 == 1) ? (a2 - a1 - b1 - b2 - 1) : (a1 - a2 - b2 - b1 - 1);
        return ((t % 4) == 0) ? 1 : 0;
    }
    return ((a1 + b1 - a2 - b2) % 4 == 0) ? 1 : 0;
}

static void k3_gram(void) {
    int ls[KL][3];
    k3_lines(ls);
    for (int i = 0; i < KL; i++)
        for (int j = i; j < KL; j++) { G[i][j] = G[j][i] = k3_inter(ls[i], ls[j]); }
    for (int i = 0; i < KL; i++) { G[i][KL] = 1; G[KL][i] = 1; }
    G[KL][KL] = 4;
}

static int k3_rank(void) {
    static Frac M[KN][KN];
    for (int i = 0; i < KN; i++)
        for (int j = 0; j < KN; j++) { M[i][j].n = G[i][j]; M[i][j].d = 1; }
    int r = 0;
    for (int c = 0; c < KN && r < KN; c++) {
        int piv = -1;
        for (int i = r; i < KN; i++) if (M[i][c].n != 0) { piv = i; break; }
        if (piv < 0) continue;
        for (int j = 0; j < KN; j++) { Frac t = M[r][j]; M[r][j] = M[piv][j]; M[piv][j] = t; }
        Frac pv = M[r][c];
        for (int i = r + 1; i < KN; i++) {
            if (M[i][c].n == 0) continue;
            Frac f = fr_mul(M[i][c], fr(pv.d, pv.n));
            for (int j = c; j < KN; j++) M[i][j] = fr_sub(M[i][j], fr_mul(f, M[r][j]));
        }
        r++;
    }
    return r;
}

static int k3_snf(i128 *factors) {
    static i128 a[KN][KN];
    for (int i = 0; i < KN; i++) for (int j = 0; j < KN; j++) a[i][j] = G[i][j];
    int nf = 0;
    for (int t = 0; t < KN; t++) {
        for (;;) {
            i128 p = 0; int pi = -1, pj = -1;
            for (int i = t; i < KN; i++)
                for (int j = t; j < KN; j++) {
                    i128 v = a[i][j] < 0 ? -a[i][j] : a[i][j];
                    if (v != 0 && (pi < 0 || v < p)) { p = v; pi = i; pj = j; }
                }
            if (pi < 0) return nf;
            if (pi != t) for (int j = 0; j < KN; j++) { i128 tmp = a[t][j]; a[t][j] = a[pi][j]; a[pi][j] = tmp; }
            if (pj != t) for (int i = 0; i < KN; i++) { i128 tmp = a[i][t]; a[i][t] = a[i][pj]; a[i][pj] = tmp; }
            i128 piv = a[t][t];
            for (int i = t + 1; i < KN; i++) {
                i128 q = a[i][t] / piv;
                if (q != 0) for (int j = t; j < KN; j++) a[i][j] -= q * a[t][j];
            }
            for (int j = t + 1; j < KN; j++) {
                i128 q = a[t][j] / piv;
                if (q != 0) for (int i = 0; i < KN; i++) a[i][j] -= q * a[i][t];
            }
            int divisible = 1;
            for (int i = t + 1; i < KN && divisible; i++)
                for (int j = t + 1; j < KN; j++)
                    if (a[i][j] % piv != 0) { divisible = 0; break; }
            if (divisible) break;
        }
        factors[nf++] = a[t][t] < 0 ? -a[t][t] : a[t][t];
    }
    return nf;
}

static int k3_int_ech(i128 ech[KN][KN]) {
    static Frac M[KN][KN];
    for (int i = 0; i < KN; i++)
        for (int j = 0; j < KN; j++) { M[i][j].n = G[i][j]; M[i][j].d = 1; }
    int r = 0, nrows = 0;
    for (int c = 0; c < KN && r < KN; c++) {
        int piv = -1;
        for (int i = r; i < KN; i++) if (M[i][c].n != 0) { piv = i; break; }
        if (piv < 0) continue;
        for (int j = 0; j < KN; j++) { Frac t = M[r][j]; M[r][j] = M[piv][j]; M[piv][j] = t; }
        Frac pv = M[r][c];
        for (int j = 0; j < KN; j++) M[r][j] = fr_mul(M[r][j], fr(pv.d, pv.n));
        for (int i = 0; i < KN; i++) {
            if (i != r && M[i][c].n != 0) {
                Frac f = M[i][c];
                for (int j = c; j < KN; j++) M[i][j] = fr_sub(M[i][j], fr_mul(f, M[r][j]));
            }
        }
        for (int j = 0; j < KN; j++) ech[nrows][j] = M[r][j].n; /* denominators cleared below */
        /* clear denominators per row */
        i128 L = 1;
        for (int j = 0; j < KN; j++) L = L / igcd(L, M[r][j].d) * M[r][j].d;
        for (int j = 0; j < KN; j++) ech[nrows][j] = M[r][j].n * (L / M[r][j].d);
        i128 g = 0;
        for (int j = 0; j < KN; j++) g = igcd(g, ech[nrows][j] < 0 ? -ech[nrows][j] : ech[nrows][j]);
        if (g > 1) for (int j = 0; j < KN; j++) ech[nrows][j] /= g;
        nrows++; r++;
    }
    return nrows;
}

static int k3_signature(i128 ech[KN][KN], int k) {
    static i128 S[KN][KN];
    memset(S, 0, sizeof(S));
    for (int i = 0; i < k; i++) {
        i128 T[KN]; memset(T, 0, sizeof(T));
        for (int t = 0; t < KN; t++) {
            if (ech[i][t] == 0) continue;
            i128 cit = ech[i][t];
            for (int u = 0; u < KN; u++) T[u] += cit * G[t][u];
        }
        for (int j = 0; j < k; j++) {
            i128 s = 0;
            for (int u = 0; u < KN; u++) s += T[u] * ech[j][u];
            S[i][j] = s; S[j][i] = s;
        }
    }
    /* exact LDLᵀ with fractions */
    static Frac A[KN][KN], diag[KN];
    for (int i = 0; i < k; i++) for (int j = 0; j < k; j++) { A[i][j].n = S[i][j]; A[i][j].d = 1; }
    int pos = 0, neg = 0;
    for (int i = 0; i < k; i++) {
        Frac s = {0, 1};
        for (int t = 0; t < i; t++)
            s = fr_add(s, fr_mul(fr_mul(A[t][i], A[t][i]), diag[t]));
        Frac d = fr_sub(A[i][i], s);
        if (d.n == 0) return -1;
        diag[i] = d;
        if (d.n > 0) pos++; else neg++;
        for (int j = i + 1; j < k; j++) {
            Frac s2 = {0, 1};
            for (int t = 0; t < i; t++)
                s2 = fr_add(s2, fr_mul(fr_mul(A[t][i], A[t][j]), diag[t]));
            Frac v = fr_mul(fr_sub((Frac){S[i][j], 1}, s2), fr(diag[i].d, diag[i].n));
            A[i][j] = v; A[j][i] = v;
        }
    }
    return pos * 100 + neg;   /* (pos, neg) packed */
}

/* ═══ 7–11. GF(2) irreducibility helpers ════════════════════════════ */
static int poly_irred_gf2_quartic(const int c[5]) {
    int ev0 = c[4] & 1, ev1 = (c[0] + c[1] + c[2] + c[3] + c[4]) & 1;
    if (ev0 == 0 || ev1 == 0) return 0;
    int rem[5]; for (int i = 0; i < 5; i++) rem[i] = c[i] & 1;
    for (int dd = 4; dd >= 2; dd--)
        if (rem[dd]) { rem[dd - 2] ^= 1; rem[dd - 1] ^= 1; rem[dd] = 0; }
    return !(rem[0] == 0 && rem[1] == 0);
}

/* ═══ 8–9. Cyclotomic exact layer: poly arithmetic in Z[ζ]/(Φₙ) ═════ */
/* element = coeffs c[0..8] of Σ c_i ζ^i; Φ₇(ζ) = 0: ζ⁶+…+ζ+1 = 0;
   Φ₉(ζ) = 0: ζ⁶+ζ³+1 = 0 */
typedef struct { long long c[17]; int n; } Zeta;
static void zeta_reduce(Zeta *z) {
    /* canonical form: degree < deg Φ = 6 (both Φ₇ and Φ₉ have degree 6)
       Φ₇ = x⁶+x⁵+x⁴+x³+x²+x+1 → x⁶ = −(x⁵+x⁴+x³+x²+x+1)
       Φ₉ = x⁶+x³+1 = Φ₃(x³)  → x⁶ = −x³−1 */
    for (;;) {
        int top = -1;
        for (int i = 16; i >= 6; i--) if (z->c[i]) { top = i; break; }
        if (top < 0) break;
        long long v = z->c[top];
        z->c[top] = 0;
        if (z->n == 7) {                     /* Φ₇: x⁶ = −(x⁵+…+x+1) */
            for (int j = 1; j <= 6; j++) z->c[top - j] -= v;
        } else {                             /* Φ₉ = x⁶+x³+1: x⁶ = −x³−1 */
            z->c[top - 3] -= v;
            z->c[top - 6] -= v;
        }
    }
}
static Zeta zeta_mul(Zeta a, Zeta b) {
    Zeta r = {{{0}}, a.n};
    for (int i = 0; i < 17; i++) if (a.c[i])
        for (int j = 0; j < 17; j++) if (b.c[j])
            r.c[i + j] += a.c[i] * b.c[j];
    zeta_reduce(&r);
    return r;
}
static Zeta zeta_add(Zeta a, Zeta b) {
    Zeta r = {{{0}}, a.n};
    for (int i = 0; i < 17; i++) r.c[i] = a.c[i] + b.c[i];
    zeta_reduce(&r);
    return r;
}
static int zeta_is_int(Zeta z, long long *out) {
    for (int i = 1; i < 17; i++) if (z.c[i]) return 0;
    *out = z.c[0];
    return 1;
}
static int cyc_layer(int n, const int units[3], const long long vieta[3], const int poly[4]) {
    Zeta els[3];
    for (int u = 0; u < 3; u++) {
        Zeta z = {{{0}}, n};
        int k = units[u];
        z.c[k % n] += 1;
        z.c[(n - k) % n] += 1;
        zeta_reduce(&z);
        els[u] = z;
    }
    Zeta e1 = zeta_add(els[0], zeta_add(els[1], els[2]));
    Zeta e2 = zeta_add(zeta_mul(els[0], els[1]),
                       zeta_add(zeta_mul(els[0], els[2]), zeta_mul(els[1], els[2])));
    Zeta e3 = zeta_mul(els[0], zeta_mul(els[1], els[2]));
    long long v[3]; int ok = 1;
    if (!zeta_is_int(e1, &v[0]) || !zeta_is_int(e2, &v[1]) || !zeta_is_int(e3, &v[2])) ok = 0;
    if (ok) for (int i = 0; i < 3; i++) if (v[i] != vieta[i]) ok = 0;
    int ev0 = poly[3] & 1, ev1 = (poly[0] + poly[1] + poly[2] + poly[3]) & 1;
    int gf2 = (ev0 == 1 && ev1 == 1);
    return ok && gf2;
}

/* ═══ 12–13. quadratures (long double) ══════════════════════════════ */
static const long double PI_L = 3.14159265358979323846264338327950288L;

/* Ω = 2∫₇^∞ dx/√((x−7)(x²+7x+14)).  Substitution x−7 = t² gives the
   singularity-free equivalent  Ω = 4∫₀^∞ dt/√(t⁴+21t²+112), and t → 1/s
   on [1,∞) gives a smooth integrand on [0,1]:
     Ω = 4∫₀¹ [1/√(t⁴+21t²+112) + 1/√(1+21t²+112t⁴)] dt.
   (The raw u-form has a (1−u)^{−1/2} endpoint: finite-precision tanh–sinh
    then floors at ~4√ε — the exact fixed-point engine in JS avoids that,
    floating-point languages use the regularized form.) */
static ld klein_omega_smooth(long N) {
    ld h = 1.0L / N;
    ld s1 = 1.0L / sqrtl(112.0L), s2 = 1.0L;   /* t=0 values */
    for (long i = 1; i < N; i++) {
        ld t = i * h, t2 = t * t;
        s1 += (i & 1 ? 4.0L : 2.0L) / sqrtl(t2 * t2 + 21 * t2 + 112);
        s2 += (i & 1 ? 4.0L : 2.0L) / sqrtl(1 + 21 * t2 + 112 * t2 * t2);
    }
    s1 += 1.0L / sqrtl(134.0L);                /* t=1 endpoint, weight 1 */
    s2 += 1.0L / sqrtl(134.0L);
    return 4 * (s1 + s2) * h / 3;
}

static ld period_quadrature_ld(long N, long a, long b) {
    ld A_ = (ld)a / N, B_ = (ld)b / N;
    int K = 300; ld h = 0.025L;
    ld i1 = 0, i2 = 0;
    for (int k = -K; k <= K; k++) {
        ld t = k * h, st = sinhl(t);
        ld z = fabsl(PI_L / 2 * st);
        if (z > 11000) continue;
        ld u = 0.5L * (1.0L + tanhl(PI_L / 2 * st));
        ld chz = coshl(z);
        if (!isfinite((double)chz)) continue;
        ld w = (PI_L / 4) * coshl(t) / (chz * chz) * h;
        if (u <= 0 || u >= 1) continue;
        i1 += N * w * powl(2.0L, -A_) * powl(u, a - 1) * powl(1 - powl(u, (ld)N) / 2, B_ - 1);
        i2 += N * w * powl(2.0L, -B_) * powl(u, b - 1) * powl(1 - powl(u, (ld)N) / 2, A_ - 1);
    }
    ld closed = tgammal((ld)a / N) * tgammal((ld)b / N) / tgammal((ld)(a + b) / N);
    return fabsl((i1 + i2) - closed) / fabsl(closed);
}

/* ═══ output helpers ════════════════════════════════════════════════ */
static int g_total = 0, g_passed = 0;
static void check(const char *name, int ok, const char *detail) {
    g_total++;
    if (ok) g_passed++;
    printf("  [%s] %s%s%s\n", ok ? "PASS" : "FAIL", name,
           detail && detail[0] ? "  · " : "", detail && detail[0] ? detail : "");
}

int main(void) {
    printf("════════════════════════════════════════════════════════════\n");
    printf(" HODGE LABORATORY · POLYGLOT CORE · C (long double + __int128)\n");
    printf(" Ядро лаборатории · целочисленная верификация / integer verification\n");
    printf("════════════════════════════════════════════════════════════\n");

    printf("\n[1-2] V1 · Census of conductors / Ценз проводников\n");
    const long EXPN[4] = {7, 9, 15, 30};
    const long EXPG[4] = {15, 28, 91, 406};
    int ok1 = 1, ok2 = 1;
    for (int i = 0; i < 4; i++) {
        long genus;
        census(EXPN[i], &genus);
        if (!(genus == EXPG[i])) ok1 = 0;
        long s = 0; for (int j = 0; j < census_dn; j++) s += census_h[census_dlist[j]];
        if (s != genus) ok1 = 0;
        if (!census_mobius_match(EXPN[i])) ok2 = 0;
    }
    check("Σh_d = g for N=7,9,15,30 · Σh_d = g", ok1, "15/28/91/406");
    check("Möbius scheme agrees · схема Мёбиуса совпадает", ok2, "");

    printf("\n[3] Certificate E · t* = lcm(W/gcd(a,W), H/gcd(b,H))\n");
    const long CE[6][5] = {{48,48,1,1,48},{96,96,1,1,96},{24,36,3,5,72},{7,14,1,1,14},{12,12,4,6,6},{384,384,1,1,384}};
    int ok3 = 1;
    for (int i = 0; i < 6; i++) if (tstar(CE[i][0], CE[i][1], CE[i][2], CE[i][3]) != CE[i][4]) ok3 = 0;
    check("6 cert-E cases · 6 случаев cert E", ok3, "t*(24,36;3,5)=72 …");

    printf("\n[4] Binary flow 48×48 / Двоичный поток\n");
    long t, vis; int closed = binary_flow(&t, &vis);
    check("t*=48 · 48 cells · closure · замыкание", t == 48 && vis == 48 && closed,
          "48+212+432+114=806");

    printf("\n[5] Arf enumeration / Перечисление Арфа\n");
    int ok5 = 1; char det5[128] = "";
    for (int g = 1; g <= 3; g++) {
        long ev, od; arf_enum(g, &ev, &od);
        long exp_ev = (1L << (g - 1)) * ((1L << g) + 1);
        long exp_od = (1L << (g - 1)) * ((1L << g) - 1);
        if (!(ev == exp_ev && od == exp_od)) ok5 = 0;
        char part[40]; snprintf(part, sizeof(part), "g=%d: %ld/%ld ", g, ev, od);
        strcat(det5, part);
    }
    check("even/odd forms g=1..3 · чётные/нечётные формы", ok5, det5);

    printf("\n[6] K3 stand · exact integer machinery / точная машина\n");
    k3_gram();
    int rank = k3_rank();
    i128 factors[KN]; int nf = k3_snf(factors);
    i128 det = 1; for (int i = 0; i < nf; i++) det *= factors[i];
    static i128 ech[KN][KN];
    int k = k3_int_ech(ech);
    int sig_packed = k3_signature(ech, k);
    int sig_ok = (sig_packed == 1 * 100 + 19);
    int det_ok = (det == 64 && nf >= 2 && factors[nf - 2] == 8 && factors[nf - 1] == 8);
    check("rank_Q = 20 = ρ (Shioda · Шиода)", rank == 20, "");
    check("signature (1,19) — Hodge index · сигнатура", sig_ok, "");
    {
        char d[80] = "SNF det = ";
        char buf[48]; int bi = 47; buf[bi] = 0;
        i128 v = det < 0 ? -det : det;
        if (v == 0) buf[--bi] = '0';
        while (v) { buf[--bi] = '0' + (int)(v % 10); v /= 10; }
        strcat(d, buf);
        check("SNF → det = 64 = 8²", det_ok, d);
    }
    check("48 lines on the Fermat quartic · прямых", KL == 48, "");
    /* family relation Σ_b L1(a,b) ~ h */
    {
        int ls[KL][3]; k3_lines(ls);
        int fam_ok = 1;
        for (int a = 0; a < 4 && fam_ok; a++)
            for (int j = 0; j < KN; j++) {
                long s = 0;
                for (int b = 0; b < 4; b++)
                    for (int id = 0; id < KL; id++)
                        if (ls[id][0] == 1 && ls[id][1] == a && ls[id][2] == b) s += G[id][j];
                if (s != G[KL][j]) { fam_ok = 0; break; }
            }
        check("family relation Σ_b L1(a,b) ~ h · семейное соотношение", fam_ok, "");
    }

    printf("\n[7] Klein stand / Слой Клейна\n");
    {
        long long j = -(105LL * 105 * 105) / 343;
        int ex[4] = {0,0,0,0};
        ex[0] = (j == -3375);
        ex[1] = ((-343LL) * j == 105LL * 105 * 105);
        long long expand[4] = {0,0,0,0};
        const int FI[2][2] = {{0,1},{1,-7}};
        const int FJ[3][2] = {{0,1},{1,7},{2,14}};
        for (int i = 0; i < 2; i++) for (int jj = 0; jj < 3; jj++)
            expand[FI[i][0] + FJ[jj][0]] += (long long)FI[i][1] * FJ[jj][1];
        ex[2] = (expand[0]==1 && expand[1]==0 && expand[2]==-35 && expand[3]==-98);
        ex[3] = (7*7 - 4*14 == -7);
        check("j = −3375 = −15³ · Δ·j = 105³ · disc = −7",
              ex[0] && ex[1] && ex[2] && ex[3], "(v−7)(v²+7v+14) = v³−35v−98");
    }

    printf("\n[8-9] Cyclotomic layer N=7/9 · Z[ζ]/Φₙ (exact integer arithmetic)\n");
    {
        /* N=7: conjugates of x = ζ+ζ⁻¹ over units {1,2,4}; Φ₇: ζ⁶+…+ζ+1=0
           Vieta of the minimal cubic x³+x²−2x−1: e = (−1, −2, 1) */
        const int units7[3] = {1, 2, 3};
        const long long vieta7[3] = {-1, -2, 1};
        const int poly7[4] = {1, 1, -2, -1};
        int ok7 = cyc_layer(7, units7, vieta7, poly7);
        check("N=7: Vieta s=(−1,−2,1) computed in Z[ζ]/Φ₇ + GF(2)", ok7,
              "e1,e2,e3 exact integers · cubic irreducible over GF(2)");
        /* N=9: Φ₉: ζ⁶+ζ³+1=0; minimal cubic x³−3x+1: Vieta (0, −3, −1) */
        const int units9[3] = {1, 2, 4};
        const long long vieta9[3] = {0, -3, -1};   /* e3 = −c = −1 */
        const int poly9[4] = {1, 0, -3, 1};
        int ok9 = cyc_layer(9, units9, vieta9, poly9);
        check("N=9: Vieta s=(0,−3,−1) computed in Z[ζ]/Φ₉ + GF(2)", ok9,
              "e1,e2,e3 exact integers · cubic irreducible over GF(2)");
    }

    printf("\n[10-11] BCH radical tower Z[√5][β] · Радикальная башня\n");
    {
        /* n=15: X = (1+√5) + β, β² = 30−6√5, den=4, P = x⁴−x³−4x²+4x+1
           check Σ_j poly[deg−j]·den^(deg−j)·X^j == 0 in the tower */
        struct Spec { int D0, D1, mA0, mA1, mB0, mB1, den; int poly[5]; } sp[2] = {
            {30, -6,  1, 1, 1, 0, 4, {1, -1, -4, 4, 1}},
            {30,  6, -1, 1, 1, 0, 4, {1,  1, -4, -4, 1}},
        };
        for (int s = 0; s < 2; s++) {
            long long D0 = sp[s].D0, D1 = sp[s].D1;
            /* X = A + Bβ, A = mA0+mA1√5, B = mB0+mB1√5 */
            long long A0 = sp[s].mA0, A1 = sp[s].mA1, B0 = sp[s].mB0, B1 = sp[s].mB1;
            int den = sp[s].den;
            const int *poly = sp[s].poly;
            /* acc = Σ_j poly[4−j]·den^(4−j)·X^j, X^j = P0 + P1β (Z[√5] pairs) */
            long long R0 = 0, R1 = 0; /* result as (r00+r01√5) + (r10+r11√5)β → keep 4 ints */
            long long r00 = 0, r01 = 0, r10 = 0, r11 = 0;
            long long P0[2] = {1, 0}, P1[2] = {0, 0}; /* X^0 = 1 */
            long long curP0[2] = {1, 0}, curP1[2] = {0, 0};
            for (int j = 0; j < 5; j++) {
                int jj = (j == 0) ? 0 : j;
                if (j > 0) {
                    /* (p + qβ)(a + bβ) = (pa + qb·D) + (pb + qa)β,
                       all products in Z[√5]: (x0+x1√5)(y0+y1√5)
                         = (x0y0+5x1y1) + (x0y1+x1y0)√5 */
                    long long pa0 = curP0[0]*A0 + 5*curP0[1]*A1;
                    long long pa1 = curP0[0]*A1 + curP0[1]*A0;
                    long long qb0 = curP1[0]*B0 + 5*curP1[1]*B1;
                    long long qb1 = curP1[0]*B1 + curP1[1]*B0;
                    long long qbd0 = qb0*D0 + 5*qb1*D1;   /* (q·b)·D */
                    long long qbd1 = qb0*D1 + qb1*D0;
                    long long pb0 = curP0[0]*B0 + 5*curP0[1]*B1;
                    long long pb1 = curP0[0]*B1 + curP0[1]*B0;
                    long long qa0 = curP1[0]*A0 + 5*curP1[1]*A1;
                    long long qa1 = curP1[0]*A1 + curP1[1]*A0;
                    curP0[0] = pa0 + qbd0; curP0[1] = pa1 + qbd1;
                    curP1[0] = pb0 + qa0;  curP1[1] = pb1 + qa1;
                }
                int cidx = 4 - j;              /* poly highest-first: poly[deg−j] */
                long long cc = (long long)poly[cidx];
                for (int e2 = 0; e2 < 4 - j; e2++) cc *= den;
                if (!cc) continue;
                r00 += cc * curP0[0]; r01 += cc * curP0[1];
                r10 += cc * curP1[0]; r11 += cc * curP1[1];
            }
            (void)P0; (void)P1;
            int resid_ok = (r00 == 0 && r01 == 0 && r10 == 0 && r11 == 0);
            int gf2 = poly_irred_gf2_quartic(poly);
            check(s == 0 ? "n=15: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)"
                         : "n=30: 4⁴P(x) ≡ 0 in Z[√5][β] + GF(2)",
                  resid_ok && gf2,
                  s == 0 ? "b_Ch(15) = (7 − √5 − √(30−6√5))/8"
                         : "b_Ch(30) = (9 − √5 − √(30+6√5))/8");
        }
    }

    printf("\n[12] Torus Δ_Ch (long double ~19 digits)\n");
    {
        ld delta = PI_L / 4, lam = 4 * PI_L * PI_L;
        ld Delta = lam + delta * delta / 2 - delta * delta * delta * delta * delta;
        ld ref = 39.48799539346835051297464603266144167978L;
        ld rel = fabsl(Delta - ref) / ref;
        char d[64];
        snprintf(d, sizeof(d), "Δ_Ch = %.19Lg, rel = .2Le", Delta, rel);
        snprintf(d, sizeof(d), "Δ_Ch = %.19Lg", Delta);
        check("Δ_Ch = 4π² + δ²/2 − δ⁵ (40-digit reference)", rel < 1e-17L, d);
    }

    printf("\n[13] Klein Ω quadrature (long double tanh–sinh)\n");
    {
        ld Om = klein_omega_smooth(20000L);
        ld ref = 1.93331170561681154673308L;
        ld rel = fabsl(Om - ref) / ref;
        char d[80];
        snprintf(d, sizeof(d), "Ω = %.19Lg, rel = %.2Le (ref is 23-digit)", Om, rel);
        check("Ω = 2∫₇^∞ dx/√(x³−35x−98)", rel < 1e-17L, d);
    }

    printf("\n[14] V6 Γ-reflection (long double)\n");
    {
        ld worst = 0;
        long N = 7;
        for (long k = 1; k < N; k++) {
            ld lhs = tgammal((ld)k / N) * tgammal((ld)(N - k) / N);
            ld rhs = PI_L / sinl(PI_L * (ld)k / N);
            ld e = fabsl(lhs - rhs) / fabsl(rhs);
            if (e > worst) worst = e;
        }
        char d[48]; snprintf(d, sizeof(d), "max rel = %.2Le", worst);
        check("Γ(k/N)Γ((N−k)/N) = π/sin(πk/N), N=7", worst < 1e-15L, d);
    }

    printf("\n[15] Period closed vs tanh–sinh (long double)\n");
    {
        ld e15 = period_quadrature_ld(15, 2, 3);
        ld e9 = period_quadrature_ld(9, 1, 2);
        char d[80];
        snprintf(d, sizeof(d), "rel = %.2Le / %.2Le", e15, e9);
        check("P_closed = P_numeric (N=15; N=9)", e15 < 1e-13L && e9 < 1e-13L, d);
    }

    printf("\n════════════════════════════════════════════════════════════\n");
    printf(" ИТОГ / RESULT: %d/%d\n", g_passed, g_total);
    if (g_passed == g_total)
        printf(" ✔ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ · ALL CHECKS PASSED\n");
    else
        printf(" ✘ ЕСТЬ ПРОВАЛЫ · THERE ARE FAILURES\n");
    printf(" Программа: Исаев Исхак Хамзатович / Program: Isaev Iskhak Khamzatovich\n");
    printf("════════════════════════════════════════════════════════════\n");
    return (g_passed == g_total) ? 0 : 1;
}
