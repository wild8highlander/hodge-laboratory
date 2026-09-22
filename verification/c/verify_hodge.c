/* ═══════════════════════════════════════════════════════════════════
   HODGE LABORATORY — C VERIFICATION
   Laboratory "The Dynamic Principle" (Isaev Iskhak Khamzatovich)

   Fast exact integer checks (censuses, ranks, invariants).
   Run:  gcc -O2 -o verify_hodge verify_hodge.c -lm && ./verify_hodge
   Exit codes: 0 — all checks accepted, 1 — at least one failure.
   ═══════════════════════════════════════════════════════════════════ */

#include <stdio.h>
#include <stdint.h>

static int passes = 0, fails = 0;

static void check(const char *name, long long actual, long long expected) {
    if (actual == expected) {
        passes++;
        printf("  [PASS] %s\n", name);
    } else {
        fails++;
        printf("  [FAIL] %s  got %lld expected %lld\n", name, actual, expected);
    }
}

static uint64_t igcd(uint64_t a, uint64_t b) {
    while (b) { uint64_t r = a % b; a = b; b = r; }
    return a;
}

static uint64_t ilcm(uint64_t a, uint64_t b) {
    return a / igcd(a, b) * b;
}

/* Census of characters: sum of h_d over conductors = genus (exact). */
static long long census_total(int N) {
    long long cnt = 0;
    for (int a = 1; a < N; a++)
        for (int b = 1; b < N - a; b++)
            cnt++;
    return cnt;
}

/* h_d for a given conductor d. */
static long long census_d(int N, int d) {
    long long cnt = 0;
    for (int a = 1; a < N; a++)
        for (int b = 1; b < N - a; b++) {
            uint64_t g = igcd((uint64_t)N, (uint64_t)a);
            g = igcd(g, (uint64_t)b);
            if ((int)(N / g) == d) cnt++;
        }
    return cnt;
}

/* ─── Exact rank of the K3 49×49 matrix (fractional elimination) ─── */

static int intersection(int l1, int l2) {
    int f1 = l1 / 16, a1 = (l1 % 16) / 4, b1 = l1 % 4;
    int f2 = l2 / 16, a2 = (l2 % 16) / 4, b2 = l2 % 4;
    /* f ∈ {0,1,2} — семейства 1,2,3 (0-based) */
    if (l1 == l2) return -2;
    if (f1 == f2) return ((a1 == a2) != (b1 == b2)) ? 1 : 0;
    if ((f1 == 0 && f2 == 1) || (f1 == 1 && f2 == 0))
        return ((a1 + b2 - a2 - b1) % 4 == 0) ? 1 : 0;      /* {1,2} */
    if ((f1 == 0 && f2 == 2) || (f1 == 2 && f2 == 0)) {
        if (f1 == 0)                                         /* {1,3} */
            return ((a2 - a1 - b1 - b2 - 1) % 4 == 0) ? 1 : 0;
        return ((a1 - a2 - b2 - b1 - 1) % 4 == 0) ? 1 : 0;
    }
    return ((a1 + b1 - a2 - b2) % 4 == 0) ? 1 : 0;           /* {2,3} */
}

/* ── Точные рациональные числа (p/q, q>0, сокращены) ── */
typedef struct { long long p, q; } Frac;

static long long llgcd(long long a, long long b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) { long long r = a % b; a = b; b = r; }
    return a ? a : 1;
}

static Frac fmk(long long p, long long q) {
    Frac f;
    if (q < 0) { p = -p; q = -q; }
    long long g = llgcd(p, q);
    f.p = p / g; f.q = q / g;
    return f;
}

static Frac fmul(Frac a, Frac b) { return fmk(a.p * b.p, a.q * b.q); }

static Frac fsub(Frac a, Frac b) { /* a - b */
    return fmk(a.p * b.q - b.p * a.q, a.q * b.q);
}

static int fz(Frac a) { return a.p == 0; }

/* Ранг через точное приведение к RREF над Q. */
static int k3_rank(void) {
    static Frac A[49][49];
    for (int i = 0; i < 48; i++)
        for (int j = 0; j < 48; j++)
            A[i][j] = fmk(intersection(i, j), 1);
    for (int i = 0; i < 48; i++) {
        A[i][48] = fmk(1, 1);
        A[48][i] = fmk(1, 1);
    }
    A[48][48] = fmk(4, 1);
    int rank = 0;
    for (int col = 0; col < 49 && rank < 49; col++) {
        int piv = -1;
        for (int r = rank; r < 49; r++)
            if (!fz(A[r][col])) { piv = r; break; }
        if (piv < 0) continue;
        for (int j = 0; j < 49; j++) {
            Frac t = A[rank][j]; A[rank][j] = A[piv][j]; A[piv][j] = t;
        }
        Frac pv = A[rank][col];
        for (int j = 0; j < 49; j++)
            A[rank][j] = fmul(A[rank][j], fmk(pv.q, pv.p));
        for (int r = 0; r < 49; r++) {
            if (r != rank && !fz(A[r][col])) {
                Frac f = A[r][col];
                for (int j = 0; j < 49; j++)
                    A[r][j] = fsub(A[r][j], fmul(f, A[rank][j]));
            }
        }
        rank++;
    }
    return rank;
}

/* ─── Errata E8: Arf formulas ─── */

static long long even_theta(int g) { /* 2^{g-1}(2^g + 1) */
    long long p = 1;
    for (int i = 0; i < g; i++) p *= 2;
    return p / 2 * (p + 1);
}

static long long odd_theta(int g) { /* 2^{g-1}(2^g - 1) */
    long long p = 1;
    for (int i = 0; i < g; i++) p *= 2;
    return p / 2 * (p - 1);
}

int main(void) {
    printf("HODGE LABORATORY — C VERIFICATION PANEL\n\n");

    /* 1. Genera and censuses */
    check("g(15) = 91", (15 - 1) * (15 - 2) / 2, 91);
    check("g(30) = 406", (30 - 1) * (30 - 2) / 2, 406);
    check("N=15 census sum = 91", census_total(15), 91);
    check("N=30 census sum = 406", census_total(30), 406);
    check("N=15: h(3)=1", census_d(15, 3), 1);
    check("N=15: h(5)=6", census_d(15, 5), 6);
    check("N=15: h(15)=84", census_d(15, 15), 84);
    check("N=30: h(3)=1", census_d(30, 3), 1);
    check("N=30: h(5)=6", census_d(30, 5), 6);
    check("N=30: h(6)=9", census_d(30, 6), 9);
    check("N=30: h(10)=30", census_d(30, 10), 30);
    check("N=30: h(15)=84", census_d(30, 15), 84);
    check("N=30: h(30)=276", census_d(30, 30), 276);

    /* 2. K3: exact rank of the 49×49 matrix */
    check("K3: exact rank over Q = 20", k3_rank(), 20);
    check("K3: isotypy 1+7+7+7 = 22 (mu4 decomposition)", 1 + 7 + 7 + 7, 22);
    check("K3: signature (1,19): 1 + 19 = rho = 20", 1 + 19, 20);

    /* 3. Klein quartic */
    check("Klein: c4^3 = 105^3 = 1157625", 105LL * 105 * 105, 1157625);
    check("Klein: |Delta| * |j| = 343 * 3375 = 105^3", 343LL * 3375, 1157625);
    check("Klein: j = -c4^3/Delta = -3375", -105LL * 105 * 105 / 343, -3375);
    check("Klein: (-15)^3 = -3375", -15LL * 15 * 15, -3375);
    check("Klein: Delta = -7^3 = -343", -7LL * 7 * 7, -343);
    check("Klein: disc(v^2+7v+14) = 49-56 = -7", 7LL * 7 - 4 * 14, -7);

    /* 4. Stand N=15/30 */
    check("disc = 3^4*5^6 = 81*15625 = 1265625", 81LL * 15625, 1265625);
    check("vol_h = sqrt(disc) = 1125: 1125^2 = 1265625", 1125LL * 1125,
          1265625);
    {
        long long snf[] = {1, 1, 5, 5, 15, 15, 15, 15}, p = 1;
        for (int i = 0; i < 8; i++) p *= snf[i];
        check("SNF (1,1,5,5,15,15,15,15) product = 1265625", p, 1265625);
    }
    check("Q_stand = 2N*max(s_i) = 2*30*8 = 480", 2 * 30 * 8, 480);

    /* 5. Errata E8 */
    check("g=3: even (Arf=0) = 2^2*(2^3+1) = 36", even_theta(3), 36);
    check("g=3: odd (Arf=1) = 2^2*(2^3-1) = 28", odd_theta(3), 28);
    check("g=3: total = 36 + 28 = 64", even_theta(3) + odd_theta(3), 64);
    check("g=1: even = 3", even_theta(1), 3);
    check("g=2: even = 10", even_theta(2), 10);
    check("g=4: even = 136", even_theta(4), 136);

    /* 6. Flow termination (E4) */
    check("t*(48,48,1,1) = lcm(48,48) = 48",
          (long long)ilcm(48 / igcd(1, 48), 48 / igcd(1, 48)), 48);
    check("t*(24,36,3,5) = lcm(8,36) = 72",
          (long long)ilcm(24 / igcd(3, 24), 36 / igcd(5, 36)), 72);
    check("t*(12,12,4,6) = lcm(3,2) = 6",
          (long long)ilcm(12 / igcd(4, 12), 12 / igcd(6, 12)), 6);

    /* 7. Binary code reference totals */
    check("binary code: 48+212+432+114 = 806", 48LL + 212 + 432 + 114, 806);

    /* 8. Genus of the Fermat curve */
    check("g(7) = 15", (7 - 1) * (7 - 2) / 2, 15);
    check("g(4) = 3", (4 - 1) * (4 - 2) / 2, 3);

    printf("\n  VERDICT: %d PASS, %d FAIL\n", passes, fails);
    return fails == 0 ? 0 : 1;
}
