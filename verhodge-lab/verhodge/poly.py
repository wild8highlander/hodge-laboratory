"""Integer polynomial kernels — the exact-arithmetic foundation (Wave 1).

Conventions
-----------
* Polynomials are integer coefficient lists, LOWEST degree first.
* Leading zeros are stripped by the constructors; the zero polynomial
  is ``[]``.
* Division is only by MONIC polynomials (exact integral quotients);
  this is all the cyclotomic layer needs and keeps every pivot
  integral.
* The GF(2) kernels work on coefficient lists reduced mod 2 and
  support the Rabin irreducibility test used by the exact layer to
  certify minimal polynomials.

No third-party dependencies: pure Python integers, mirroring the
discipline of hodge-laboratory/laboratory.py.
"""

from math import gcd
from typing import List, Tuple

# ──────────────────────────────────────────────────────────────────────
# Z[x] kernels (lowest-first)
# ──────────────────────────────────────────────────────────────────────

def _trim(a: List[int]) -> List[int]:
    while a and a[-1] == 0:
        a.pop()
    return a


def padd(a: List[int], b: List[int]) -> List[int]:
    """a + b."""
    n = max(len(a), len(b))
    out = [0] * n
    for i, v in enumerate(a):
        out[i] += v
    for i, v in enumerate(b):
        out[i] += v
    return _trim(out)


def psub(a: List[int], b: List[int]) -> List[int]:
    """a - b."""
    n = max(len(a), len(b))
    out = [0] * n
    for i, v in enumerate(a):
        out[i] += v
    for i, v in enumerate(b):
        out[i] -= v
    return _trim(out)


def pmul(a: List[int], b: List[int]) -> List[int]:
    """a * b (schoolbook; degrees here stay tiny)."""
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                out[i + j] += ai * bj
    return _trim(out)


def pscale(a: List[int], c: int) -> List[int]:
    """c * a."""
    if c == 0:
        return []
    return _trim([c * v for v in a])


def pdeg(a: List[int]) -> int:
    """Degree; -1 for the zero polynomial."""
    return len(a) - 1 if a else -1


def pdivmod_monic(a: List[int], m: List[int]) -> Tuple[List[int], List[int]]:
    """Exact division with remainder by a MONIC polynomial m.

    Raises ValueError if m is not monic.  All pivots stay integral.
    """
    if not m or m[-1] != 1:
        raise ValueError("divisor must be monic")
    a = list(a)
    q = [0] * max(0, len(a) - len(m) + 1)
    dm = len(m) - 1
    for i in range(len(a) - 1, dm - 1, -1):
        k = a[i]
        if k:
            q[i - dm] = k
            for j in range(dm + 1):
                a[i - dm + j] -= k * m[j]
    return _trim(q), _trim(a[:dm])


def pmod_monic(a: List[int], m: List[int]) -> List[int]:
    return pdivmod_monic(a, m)[1]


def pder(a: List[int]) -> List[int]:
    """Formal derivative."""
    return _trim([i * a[i] for i in range(1, len(a))])


def peval_int(a: List[int], x: int) -> int:
    """Evaluate at an integer point (Horner)."""
    r = 0
    for v in reversed(a):
        r = r * x + v
    return r


def ppow_monic_mod(a: List[int], e: int, m: List[int]) -> List[int]:
    """a^e mod m via binary exponentiation (m monic)."""
    result = [1]
    base = pmod_monic(list(a), m)
    while e:
        if e & 1:
            result = pmod_monic(pmul(result, base), m)
        base = pmod_monic(pmul(base, base), m)
        e >>= 1
    return result


# ──────────────────────────────────────────────────────────────────────
# Cyclotomic polynomials via the divisor product formula
# ──────────────────────────────────────────────────────────────────────

def _divisors(n: int) -> List[int]:
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


_PHI_CACHE = {}


def cyclotomic(n: int) -> List[int]:
    """Phi_n(x) as an integer list (lowest-first), monic.

    Computed by the exact product formula
        x^n - 1 = prod_{d | n} Phi_d(x)
    i.e.  Phi_n = (x^n - 1) / prod_{d | n, d < n} Phi_d,
    with every division exact because each Phi_d is monic.  This is
    the v1.7 requirement that the program *derives* Phi_n rather than
    reading it from a dictionary.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if n in _PHI_CACHE:
        return list(_PHI_CACHE[n])
    if n == 1:
        out = [-1, 1]                       # x - 1
    else:
        num = [0] * n + [1]                 # x^n - 1  (lowest-first)
        num[0] = -1
        prod = [1]
        for d in _divisors(n):
            if d < n:
                prod = pmul(prod, cyclotomic(d))
        q, r = pdivmod_monic(num, prod)
        if r:
            raise AssertionError("non-exact division building Phi_n")
        out = q
    _PHI_CACHE[n] = list(out)
    return list(out)


def euler_phi(n: int) -> int:
    """Euler totient (trial division; n is small here)."""
    if n < 1:
        raise ValueError
    result, m = 1, n
    p = 2
    while p * p <= m:
        if m % p == 0:
            m //= p
            k = 1
            while m % p == 0:
                m //= p
                k += 1
            result *= (p - 1) * p ** (k - 1)
        p += 1
    if m > 1:
        result *= m - 1
    return result


def mobius_mu(n: int) -> int:
    """Moebius function."""
    if n < 1:
        raise ValueError
    if n == 1:
        return 1
    mu, m, p = 1, n, 2
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            mu = -mu
        p += 1
    if m > 1:
        mu = -mu
    return mu


# ──────────────────────────────────────────────────────────────────────
# GF(2) kernels + Rabin irreducibility
# ──────────────────────────────────────────────────────────────────────

def _g2_trim(a: List[int]) -> List[int]:
    while a and a[-1] % 2 == 0:
        a.pop()
    return a


def g2_mul(a: List[int], b: List[int]) -> List[int]:
    out = [0] * (len(a) + len(b))
    for i, ai in enumerate(a):
        if ai & 1:
            for j, bj in enumerate(b):
                if bj & 1:
                    out[i + j] ^= 1
    return _g2_trim(out)


def g2_mod(a: List[int], m: List[int]) -> List[int]:
    """a mod m over GF(2) (m monic mod 2)."""
    a = [v & 1 for v in a]
    dm = len(m) - 1
    for i in range(len(a) - 1, dm - 1, -1):
        if a[i]:
            for j in range(dm + 1):
                a[i - dm + j] ^= m[j] & 1
    return _g2_trim(a)


def g2_gcd(a: List[int], b: List[int]) -> List[int]:
    a, b = _g2_trim([v & 1 for v in a]), _g2_trim([v & 1 for v in b])
    while b:
        a, b = b, g2_mod(a, b)
    return a


def g2_powmod(a: List[int], e: int, m: List[int]) -> List[int]:
    result = [1]
    base = g2_mod(list(a), m)
    while e:
        if e & 1:
            result = g2_mod(g2_mul(result, base), m)
        base = g2_mod(g2_mul(base, base), m)
        e >>= 1
    return result


def g2_is_irreducible(f: List[int]) -> bool:
    """Rabin irreducibility test over GF(2).

    f (deg d >= 1) is irreducible over F_2 iff
      (i)  x^(2^d) == x (mod f), and
      (ii) gcd(x^(2^(d/q)) - x, f) == 1 for every prime q | d.

    This is the computational certificate that a collapsed integer
    polynomial really is the minimal polynomial of 2cos(2*pi/n)
    (the two-scheme discipline: symbolic collapse + GF(2) test).
    """
    f = _g2_trim([v & 1 for v in f])
    d = len(f) - 1
    if d < 1:
        return False
    x = [0, 1]
    # (i) x^(2^d) == x mod f
    r = x
    for _ in range(d):
        r = g2_mod(g2_mul(r, r), f)
    if g2_psub(r, x) not in ([], [0]):
        if _g2_neq(r, [0, 1]):
            return False
    # (ii) gcd(x^(2^(d/q)) - x, f) == 1 for prime q | d
    qs = _prime_divisors(d)
    for q in qs:
        r = x
        for _ in range(d // q):
            r = g2_mod(g2_mul(r, r), f)
        g = g2_gcd(g2_psub(r, x), f)
        if len(g) - 1 != 0:            # gcd degree must be 0 (constant)
            return False
    return True


def _g2_neq(a: List[int], b: List[int]) -> bool:
    a = _g2_trim([v & 1 for v in a])
    b = _g2_trim([v & 1 for v in b])
    return a != b


def g2_psub(a: List[int], b: List[int]) -> List[int]:
    n = max(len(a), len(b))
    out = [0] * n
    for i, v in enumerate(a):
        out[i] ^= v & 1
    for i, v in enumerate(b):
        out[i] ^= v & 1
    return _g2_trim(out)


def _prime_divisors(n: int) -> List[int]:
    out, m, p = [], n, 2
    while p * p <= m:
        if m % p == 0:
            out.append(p)
            while m % p == 0:
                m //= p
        p += 1
    if m > 1:
        out.append(m)
    return out


# ──────────────────────────────────────────────────────────────────────
# Integer matrix kernels (exact rank / Bareiss determinant)
# ──────────────────────────────────────────────────────────────────────

def int_rank(A: List[List[int]]) -> int:
    """Exact rank over Q by fraction-free elimination.

    Rows are kept primitive by gcd normalization; pivots integral
    because each elimination step divides by the previous pivot's
    content.  (The K3 stand needs rank over Q, not SNF.)
    """
    A = [row[:] for row in A]
    m, n = len(A), len(A[0]) if A else 0
    rank = 0
    for col in range(n):
        piv = None
        for r in range(rank, m):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        A[rank], A[piv] = A[piv], A[rank]
        pv = A[rank][col]
        for r in range(rank + 1, m):
            f = A[r][col]
            if f:
                # keep integers: multiply-and-subtract with gcd cleanup
                g = gcd(abs(pv), abs(f))
                a = pv // g
                b = f // g
                A[r] = [b * A[rank][j] - a * A[r][j] for j in range(n)]
                cg = 0
                for v in A[r]:
                    cg = gcd(cg, abs(v))
                if cg > 1:
                    A[r] = [v // cg for v in A[r]]
        rank += 1
        if rank == m:
            break
    return rank


def bareiss_det(A: List[List[int]]) -> int:
    """Exact determinant by the Bareiss fraction-free algorithm."""
    A = [row[:] for row in A]
    n = len(A)
    if n == 0:
        return 1
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            for r in range(k + 1, n):
                if A[r][k] != 0:
                    A[k], A[r] = A[r], A[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
            A[i][k] = 0
        prev = A[k][k]
    return sign * A[n - 1][n - 1]
