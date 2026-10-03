"""The dual-scheme character census (Wave 1; protocol run V1-style).

A character (a, b) of the Fermat level N has conductor
d = N / gcd(N, a, b).  The census histogram {d: h_d} must satisfy
    sum_d h_d = g(N) = (N-1)(N-2)/2   (the genus of the Fermat curve),
and it is computed by two INDEPENDENT schemes whose agreement is the
statement:

  Scheme A (direct)   — enumerate a, b with 1 <= a, 1 <= b, a + b < N.
  Scheme B (Moebius)  — inclusion-exclusion
        h_d = sum_{m | d} mu(m) * c(d/m),  c(k) = (k-1)(k-2)/2.

The two-scheme pattern is the laboratory's core falsifiability tool:
any implementation error breaks the agreement on some conductor.
"""

from math import gcd
from typing import Dict, List, Tuple

from .poly import mobius_mu


def census_direct(N: int) -> Tuple[Dict[int, int], Dict[int, List[Tuple[int, int]]], int]:
    """Scheme A: direct enumeration of eigencharacters by conductor."""
    h: Dict[int, int] = {}
    by_d: Dict[int, List[Tuple[int, int]]] = {}
    for a in range(1, N):
        for b in range(1, N - a):
            d = N // gcd(gcd(N, a), b)
            h[d] = h.get(d, 0) + 1
            by_d.setdefault(d, []).append((a, b))
    genus = (N - 1) * (N - 2) // 2
    return dict(sorted(h.items())), dict(sorted(by_d.items())), genus


def census_mobius(N: int) -> Dict[int, int]:
    """Scheme B: Moebius inversion over the conductor lattice."""
    def c(k: int) -> int:
        return (k - 1) * (k - 2) // 2 if k >= 3 else 0

    out: Dict[int, int] = {}
    for d in range(2, N + 1):
        if N % d:
            continue
        s = 0
        for m in range(1, d + 1):
            if d % m == 0:
                s += mobius_mu(m) * c(d // m)
        if s:
            out[d] = s
    return dict(sorted(out.items()))


def census_agreement(N: int) -> bool:
    """The two schemes must agree on every conductor."""
    h, _, _ = census_direct(N)
    hm = census_mobius(N)
    return h == hm


def genus(N: int) -> int:
    return (N - 1) * (N - 2) // 2


# Frozen reference values (hodge-laboratory baseline, V1 layer).
FROZEN_CENSUS = {
    7:  {7: 15},
    9:  {3: 1, 9: 27},
    11: {11: 45},
    15: {3: 1, 5: 6, 15: 84},
    30: {3: 1, 5: 6, 6: 9, 10: 30, 15: 84, 30: 276},
}
