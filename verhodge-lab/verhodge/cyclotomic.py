"""The unified exact layer for 2cos(2*pi/n) — Waves v1.5 and v1.7.

Replaces the per-level dictionaries of hodge-laboratory v1.3/v1.4 with
a single parametric engine.  For arbitrary n >= 3 the module derives:

  (1) Phi_n                 — by the exact divisor product formula;
  (2) the minimal polynomial of x = 2cos(2*pi/n) — by the COLLAPSE
      algorithm: the conjugates x_k = zeta^k + zeta^{-k} live in
      Z[zeta]/(Phi_n); the product  prod (T - x_k)  over the unit
      classes {k ~ -k} is formed by pure integer polynomial arithmetic
      modulo Phi_n, and every coefficient must COLLAPSE to an integer
      constant — that collapse IS the exact identity (the elementary
      symmetric functions of the conjugates are Galois-invariant
      algebraic integers);
  (3) the GF(2) irreducibility certificate (Rabin test) proving the
      collapsed polynomial is minimal;
  (4) the Vieta profile (elementary symmetric integers s_1..s_d);
  (5) the two-scheme numeric cross-check at 40 dps: the collapsed
      polynomial must vanish at 2cos(2*pi/n) to < 1e-25.

The collapsed coefficients (s_1, ..., s_d) are the Vieta data of the
roadmap's certificates I/J/K (n = 7 / 9 / 11).

Braking constants: b_Ch(n) = 1 - cos(2*pi/n).  Closed radical forms
are installed for the rungs n = 7, 9, 15, 30 (Hurwitz / Macbeath /
the N=15-30 stand); for n = 11 the cyclic-quintic Lagrange-resolvent
identity is certified numerically (casus irreducibilis: the exact
layer carries the algebraic burden).
"""

from math import gcd
from typing import Dict, List, Optional, Tuple

from .poly import (cyclotomic, euler_phi, padd, psub, pmul, pdeg,
                   pmod_monic, g2_is_irreducible)

try:
    import mpmath as _mp
    HAVE_MPMATH = True
except Exception:  # pragma: no cover
    HAVE_MPMATH = False


# ──────────────────────────────────────────────────────────────────────
# Elements of Z[zeta]/(Phi_n): integer lists, LOWEST degree first,
# reduced modulo the monic Phi_n.
# ──────────────────────────────────────────────────────────────────────

def _elt_pow_sum(n: int, k: int) -> List[int]:
    """zeta^k + zeta^{-k} as an element of Z[zeta]/(Phi_n)."""
    phi = cyclotomic(n)
    e = [0] * n
    e[k % n] += 1
    e[(n - k) % n] += 1
    return pmod_monic(e, phi)


def _elt_mul(n: int, a: List[int], b: List[int]) -> List[int]:
    return pmod_monic(pmul(a, b), cyclotomic(n))


def _elt_add(a: List[int], b: List[int]) -> List[int]:
    return padd(a, b)


def _elt_as_int(a: List[int]) -> Optional[int]:
    """The constant if the element collapses to Z, else None."""
    if not a:
        return 0
    if len(a) == 1:
        return a[0]
    return None


def unit_class_reps(n: int) -> List[int]:
    """Reps of (Z/n)^x / {k ~ -k}: 1 <= k <= n//2, gcd(k, n) = 1."""
    return [k for k in range(1, n // 2 + 1) if gcd(k, n) == 1]


def minpoly_2cos_exact(n: int) -> Dict:
    """The collapse algorithm: exact minimal polynomial of 2cos(2*pi/n).

    Returns a dict with the polynomial (highest-first), the collapse
    flag, the degree check deg = phi(n)/2, and the Vieta profile.
    Raises AssertionError if any coefficient fails to collapse (that
    would falsify the Galois-invariance premise — the honest failure
    mode of the asymmetric contract).
    """
    if n < 3:
        raise ValueError("n >= 3 required")
    phi = cyclotomic(n)
    units = unit_class_reps(n)
    d = len(units)
    if d != euler_phi(n) // 2:
        raise AssertionError("unit class count mismatch")

    # P(T) = prod_{k in units} (T - x_k), coefficients in Z[zeta]/Phi_n.
    # coeffs[j] = coefficient of T^j (start: P = 1).
    coeffs: Dict[int, List[int]] = {0: [1]}
    for k in units:
        r = _elt_pow_sum(n, k)
        new: Dict[int, List[int]] = {}
        for pw, c in coeffs.items():
            new[pw + 1] = _elt_add(new.get(pw + 1, []), c)
            new[pw] = _elt_add(new.get(pw, []), psub([], _elt_mul(n, r, c)))
        coeffs = new

    collapsed: List[Optional[int]] = []
    ok = True
    for j in range(d + 1):
        v = _elt_as_int(coeffs.get(j, []))
        collapsed.append(v)
        if v is None:
            ok = False
    if not ok:
        raise AssertionError(
            f"2cos(2*pi/{n}): symmetric functions do not collapse to Z")

    # highest-first minimal polynomial: leading coeff must be 1
    high = list(reversed([v for v in collapsed]))
    if high[0] != 1:
        raise AssertionError("leading coefficient != 1")
    return {
        "n": n,
        "degree": d,
        "deg_matches_phi_half": d == euler_phi(n) // 2,
        "poly_high": high,                      # [1, s1, s2, ..., s_d] reading
        "vieta": high[1:],                      # (s_1, ..., s_d)
        "collapse": True,
    }


def minpoly_2cos(n: int) -> Tuple[int, ...]:
    """Highest-first integer coefficients of the minimal polynomial."""
    return tuple(minpoly_2cos_exact(n)["poly_high"])


def gf2_irreducible_certificate(poly_high: List[int]) -> bool:
    """GF(2) Rabin certificate for the collapsed polynomial."""
    return g2_is_irreducible(list(poly_high))


def numeric_residual(n: int, poly_high: List[int], dps: int = 40) -> float:
    """|P(2cos(2*pi/n))| at working precision — the independent scheme."""
    if not HAVE_MPMATH:
        return float("nan")
    old = _mp.mp.dps
    _mp.mp.dps = dps
    try:
        x = 2 * _mp.mp.cos(2 * _mp.mp.pi / n)
        r = _mp.mpf(0)
        for c in poly_high:
            r = r * x + _mp.mpf(c)
        return float(abs(r))
    finally:
        _mp.mp.dps = old


# ──────────────────────────────────────────────────────────────────────
# Braking constants b_Ch(n) = 1 - cos(2*pi/n)
# ──────────────────────────────────────────────────────────────────────

# Closed radical forms (hodge-laboratory v1.2, frozen; verified
# numerically by the two-scheme check below).
RADICAL_FORMS = {
    7:  "7/6 - (cuberoot(7*(1+3*sqrt(-3))/54) + cuberoot(7*(1-3*sqrt(-3))/54))/2",
    9:  "1 - (cuberoot((-1+sqrt(-3))/2) + cuberoot((-1-sqrt(-3))/2))/2",
    15: "(7 - sqrt(5) - sqrt(30 - 6*sqrt(5)))/8",
    30: "(9 - sqrt(5) - sqrt(30 + 6*sqrt(5)))/8",
}


def bch_numeric(n: int, dps: int = 40):
    """b_Ch(n) = 1 - cos(2*pi/n) at working dps."""
    if not HAVE_MPMATH:
        return None
    old = _mp.mp.dps
    _mp.mp.dps = dps
    try:
        return 1 - _mp.mp.cos(2 * _mp.mp.pi / n)
    finally:
        _mp.mp.dps = old


def bch_radical_residual(n: int, dps: int = 40) -> Optional[float]:
    """|radical form - b_Ch(n)| for the installed rungs (two schemes)."""
    if not HAVE_MPMATH or n not in (7, 9, 15, 30):
        return None
    old = _mp.mp.dps
    _mp.mp.dps = dps
    try:
        s5 = _mp.sqrt(_mp.mpf(5))
        if n == 15:
            rad = (7 - s5 - _mp.sqrt(30 - 6 * s5)) / 8
        elif n == 30:
            rad = (9 - s5 - _mp.sqrt(30 + 6 * s5)) / 8
        else:
            s3i = _mp.sqrt(_mp.mpf(-3))
            if n == 7:
                a = (7 * (1 + 3 * s3i) / 54) ** (_mp.mpf(1) / 3)
                b = (7 * (1 - 3 * s3i) / 54) ** (_mp.mpf(1) / 3)
                rad = _mp.mpf(7) / 6 - (a + b) / 2
            else:  # n == 9
                a = ((-1 + s3i) / 2) ** (_mp.mpf(1) / 3)
                b = ((-1 - s3i) / 2) ** (_mp.mpf(1) / 3)
                rad = 1 - (a + b) / 2
        return float(abs(rad - (1 - _mp.mp.cos(2 * _mp.mp.pi / n))))
    finally:
        _mp.mp.dps = old


def bch_resolvent_11(dps: int = 40) -> Dict:
    """Cyclic-quintic Lagrange-resolvent certificate for n = 11.

    The conjugates x_t = 2cos(2*pi*k_t/11), (k_t) = (1,2,4,8,5) the
    orbit of k -> 2k, form a Z/5-system with Galois generator
    sigma(x_t) = x_{t+1}.  The Lagrange resolvents

        R_j = sum_t x_t * xi^{-jt}      (xi = exp(2*pi*i/5))

    satisfy sigma(R_j) = xi^j R_j, hence

        eta_j := R_j^5  in  Q(xi)      (Z/5-symmetric), and

        x_0 = (1/5) sum_j theta_j,   theta_j^5 = eta_j,

    with compatible branches theta_j = xi^{b_j} * eta_j^{1/5}.
    The certificate has two schemes:

      * EXACT: eta_j computed in Z[zeta_11, xi] (bivariate quotient
        by (Phi_11, Phi_5)); the sigma-symmetry appears as the
        COLLAPSE of every zeta_11-coefficient to an integer, so
        eta_j is recorded as an element of Z[xi] (4 integers);
      * NUMERIC: R_j^5 (mpmath) vs the exact eta_j, and the branch
        search over 5^5 tuples reconstructing x_0 to < 1e-30.

    (casus irreducibilis: no real-radical form exists; the exact
    layer carries the algebra.)
    """
    if not HAVE_MPMATH:
        return {"available": False}
    from .poly import (cyclotomic as _cyc, pmul as _pmul, padd as _padd,
                       psub as _psub)

    phi11 = _cyc(11)
    phi5 = _cyc(5)

    # bivariate element = [e_0, e_1, e_2, e_3], e_b a u-poly (low-first)
    def ureduce(p):
        from .poly import pmod_monic
        return pmod_monic(p, phi11)

    def breduce(e):
        # reduce the v-degree: fold exponents mod 5 (zeta_5^5 = 1),
        # then canonicalize v^4 -> -1 - v - v^2 - v^3 (Phi_5 relation)
        out = [[], [], [], [], []]
        for b, c in enumerate(e):
            if not c:
                continue
            out[b % 5] = _padd(out[b % 5], c)
        c4 = out[4]
        out = out[:4]
        if c4:
            for b in range(4):
                out[b] = _psub(out[b], c4)   # v^4 = -1-v-v^2-v^3
        return [ureduce(c) for c in out]

    def bmul(e, f):
        out = [[] for _ in range(len(e) + len(f) - 1)]
        for i, a in enumerate(e):
            if not a:
                continue
            for j, b in enumerate(f):
                if b:
                    out[i + j] = _padd(out[i + j], _pmul(a, b))
        return breduce(out)

    def bscalar(e, c):
        return [([c] if c else []) for _ in e]

    def bfrom_int(c):
        return [[c], [], [], []]

    old = _mp.mp.dps
    _mp.mp.dps = dps
    try:
        xi = _mp.exp(2 * _mp.mp.pi * 1j / 5)
        ks = (1, 2, 4, 8, 5)
        orbit = [2 * _mp.mp.cos(2 * _mp.mp.pi * k / 11) for k in ks]
        R_num = [sum(orbit[t] * xi ** (-j * t) for t in range(5))
                 for j in range(5)]
        # exact R_j in Z[zeta_11, xi]:
        #   x_t = u^{k} + u^{11-k};  xi^{-jt} = v^{(5 - (j*t % 5)) % 5}
        R_exact = []
        for j in range(5):
            e = [[], [], [], [], []]
            for t, k in enumerate(ks):
                b = (-j * t) % 5
                e[b] = _padd(e[b], _padd(_mon_pow(k), _mon_pow(11 - k)))
            R_exact.append(breduce(e))
        # eta_j = R_j^5, assert collapse in the u-direction
        etas = []
        collapse_ok = True
        for j in range(5):
            eta = bmul(R_exact[j], R_exact[j])       # ^2
            eta = bmul(eta, eta)                      # ^4
            eta = bmul(eta, R_exact[j])               # ^5
            coords = []
            for c in eta:
                if not c or len(c) == 1:
                    coords.append(int(c[0]) if c else 0)
                else:
                    collapse_ok = False
                    coords.append(None)
            etas.append(coords)
        # numeric cross-checks (mpmath complex at working dps)
        def _ev5(coords):
            return sum(_mp.mpc(c) * xi ** b
                       for b, c in enumerate(coords) if c)
        res5 = [float(abs(R_num[j] ** 5 - _ev5(etas[j]))) for j in range(5)]
        # branch search: theta_j = xi^{b_j} * eta_j^{1/5}
        principal = [_ev5(etas[j]) ** (_mp.mpf(1) / 5) for j in range(5)]
        target = orbit[0]
        found = None
        from itertools import product as _iproduct
        for b in _iproduct(range(5), repeat=5):
            rec = sum((xi ** b[j]) * principal[j] for j in range(5)) / 5
            if abs(rec - target) < _mp.mpf(10) ** -(dps - 6):
                found = list(b)
                break
        mpoly = minpoly_2cos(11)
        return {
            "available": True,
            "eta_in_zeta5": etas,                     # coords of 1, xi, xi^2, xi^3
            "exact_collapse": collapse_ok,
            "power5_residuals": res5,
            "branch_exponents": found,
            "reconstruction_residual": (float(abs(rec - target))
                                        if found else None),
            "minpoly_residual": numeric_residual(11, mpoly, dps=dps),
            "orbit_k": list(ks),
            "minpoly_high": list(mpoly),
        }
    finally:
        _mp.mp.dps = old


def _mon_pow(k: int) -> List[int]:
    """u^k as a low-first list."""
    e = [0] * (k + 1)
    e[k] = 1
    return e


# ──────────────────────────────────────────────────────────────────────
# The unified exact-layer certificate (v1.7 conveyor)
# ──────────────────────────────────────────────────────────────────────

def exact_layer(n: int, dps: int = 40) -> Dict:
    """Full exact-layer certificate for the rung n.

    Two-scheme discipline:
      * symbolic: the collapse in Z[zeta]/(Phi_n)  (exact integers);
      * numeric : the polynomial vanishes at 2cos(2*pi/n) at dps;
      * finite  : GF(2) irreducibility (Rabin).
    """
    m = minpoly_2cos_exact(n)
    poly = m["poly_high"]
    res = numeric_residual(n, poly, dps=dps)
    gf2 = gf2_irreducible_certificate(poly)
    layer = {
        "n": n,
        "phi_n_degree": euler_phi(n),
        "degree": m["degree"],
        "poly_high": poly,
        "vieta": m["vieta"],
        "collapse": m["collapse"],
        "deg_matches_phi_half": m["deg_matches_phi_half"],
        "gf2_irreducible": gf2,
        "gf2_status": ("irreducible" if gf2
                        else "reducible (non-blocking for even degrees)"),
        "numeric_residual": res,
        "numeric_threshold": 1e-25,
        "bch_radical_installed": n in RADICAL_FORMS,
        "bch_radical_residual": bch_radical_residual(n, dps=dps),
        "rung_names": {7: "Hurwitz", 9: "Macbeath", 11: "quintic (cert K)"},
    }
    layer["pass"] = bool(
        layer["collapse"] and layer["deg_matches_phi_half"]
        and res < 1e-25
        and (layer["bch_radical_residual"] is None
             or layer["bch_radical_residual"] < 1e-30))
    return layer


# Frozen reference values (hodge-laboratory v1.3 baseline, V13 layer).
FROZEN_CYC = {
    7: {"syms": [-1, -2, 1], "poly": [1, 1, -2, -1], "gf2": True, "rung": "Hurwitz"},
    9: {"syms": [0, -3, -1], "poly": [1, 0, -3, 1], "gf2": True, "rung": "Macbeath"},
}
FROZEN_CERT_K = {
    11: {"poly": [1, 1, -4, -3, 3, 1], "vieta": [1, -4, -3, 3, 1]},
}
