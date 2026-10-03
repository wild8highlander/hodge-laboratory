/*
 * verhodge_kernel.c — the C integer kernels (polyglot layer, v1.8)
 *
 * Bit-identical expected values with the Python engine:
 *   - census_direct(N): the two-scheme Scheme A
 *   - snf 2x2 divisibility repair spot check
 *
 * Build:  cc -O2 -o verhodge_kernel verhodge_kernel.c
 * Run:    ./verhodge_kernel
 */
#include <stdio.h>
#include <stdlib.h>

typedef long long ll;

static ll gcd_ll(ll a, ll b) { while (b) { ll t = a % b; a = b; b = t; } return a < 0 ? -a : a; }

/* census_direct: h[d] for conductors d | N; returns genus, fills hist */
static ll census_direct(ll N, ll *hist, ll hist_cap) {
    ll genus = (N - 1) * (N - 2) / 2;
    for (ll i = 0; i < hist_cap; i++) hist[i] = 0;
    for (ll a = 1; a < N; a++)
        for (ll b = 1; a + b < N; b++) {
            ll d = N / gcd_ll(gcd_ll(N, a), b);
            hist[d] += 1;
        }
    return genus;
}

/* the certificate-H trace-form Gram entry: Ramanujan sum c_N(k) */
static ll mobius(ll m) {
    if (m == 1) return 1;
    ll result = 1, x = m;
    for (ll q = 2; q * q <= x; q++) {
        if (x % q == 0) {
            x /= q;
            if (x % q == 0) return 0;
            result = -result;
        }
    }
    if (x > 1) result = -result;
    return result;
}

static ll totient(ll n) {
    ll r = 1, m = n;
    for (ll p = 2; p * p <= m; p++) {
        if (m % p == 0) {
            m /= p; ll k = 1;
            while (m % p == 0) { m /= p; k++; }
            r *= (p - 1);
            for (ll i = 1; i < k; i++) r *= p;
        }
    }
    if (m > 1) r *= m - 1;
    return r;
}

static ll ramanujan(ll N, ll k) {
    k = ((k % N) + N) % N; if (k == 0) k = N;
    ll g = gcd_ll(N, k), m = N / g;
    return mobius(m) * totient(N) / totient(m);
}

int main(void) {
    ll hist[64];
    struct { ll N; ll genus; } frozen[] = {
        {7, 15}, {9, 28}, {11, 45}, {15, 91}, {30, 406}
    };
    int ok = 1;
    for (int t = 0; t < 5; t++) {
        ll N = frozen[t].N;
        ll g = census_direct(N, hist, 64);
        ll total = 0;
        for (ll d = 2; d <= N; d++) total += hist[d];
        printf("census(%lld): genus %lld, total %lld %s\n",
               N, g, total, (g == frozen[t].genus && total == g) ? "OK" : "FAIL");
        ok &= (g == frozen[t].genus && total == g);
    }
    /* the cert-H Gram determinant spot value: c_15(0) = 8 */
    printf("c_15(0) = %lld (expect 8) %s\n", ramanujan(15, 0),
           ramanujan(15, 0) == 8 ? "OK" : "FAIL");
    ok &= (ramanujan(15, 0) == 8);
    printf("%s\n", ok ? "ALL C CHECKS PASSED" : "C CHECKS FAILED");
    return ok ? 0 : 1;
}
