"""The computed Gross Gamma-normalization (Wave v1.6+).

Certificate H2 of hodge-laboratory v1.4 quotes
    vol_h = (2*pi)^32 * prod_{k=1}^{N-1} Gamma(k/N)^{-c_k} = 1125
with residual 1e-119 but does not recompute it.  This module turns
the cited constant into a computed, parametric evaluation:

  * the exponent rule for the N=15/30 stand (certified against the
    monograph T16/H2: c_k = 4 at the ten k with 3 !| k and c_k = 6
    at the four k with 3 | k; note sum_k c_k = 64 = 2 * 32 fixes
    the power of 2*pi);
  * high-precision evaluation at 120 dps via mpmath;
  * the integer round-off: |vol - 1125| < 1e-60 certifies the
    integral square root of disc = 1265625 from the SNF side
    (volume-discriminant agreement, the H1/H2 pair).

For arbitrary N the parametric evaluator `gross_volume` accepts any
exponent vector; the census-weighted rule for general N is an open
conjecture registered in claims/registry.yaml (C-014) — the module
returns NOT_DETERMINED rather than inventing exponents.
"""

from typing import Dict, List, Optional

try:
    import mpmath as _mp
    HAVE_MPMATH = True
except Exception:  # pragma: no cover
    HAVE_MPMATH = False

FROZEN_VOL_H = 1125


def exponent_rule_15_30(N: int, odd_d: int = 4) -> Optional[Dict[int, int]]:
    """The certified exponent rules for the N=15/30 stand.

    N=15 (certified, monograph T16/H2): c_k = 4 + 2*[3 | k].

    N=30 (derived by the duplication/reflection 'sine count'):
    the even indices inherit the N=15 vector, c_{2j} = c^15_j; the
    odd pairs (k, 30-k) contribute [Gamma(x) Gamma(1-x)]^{-d} =
    (pi/sin(pi x))^{-d}, and the odd-k sine product is exactly
    2^{-7}, so every odd pair cancels as (2*pi)^{-d} — the identity
    forces only c_15 = 0 (Gamma(1/2) = sqrt(pi)); the odd exponent d
    is conventional (default 4).

    Returns None for other levels (the general rule is C-014).
    """
    if N == 15:
        return {k: (6 if k % 3 == 0 else 4) for k in range(1, 15)}
    if N == 30:
        c = {}
        for k in range(1, 30):
            if k % 2 == 0:
                j = k // 2
                c[k] = 6 if j % 3 == 0 else 4
            elif k == 15:
                c[k] = 0
            else:
                c[k] = odd_d
        return c
    return None


def gross_volume(N: int, c: Dict[int, int], dps: int = 120):
    """vol_h = (2*pi)^{sum c_k / 2} * prod Gamma(k/N)^{-c_k} at dps."""
    if not HAVE_MPMATH:
        return None
    old = _mp.mp.dps
    _mp.mp.dps = dps
    try:
        logv = (_mp.mpf(sum(c.values())) / 2) * _mp.log(2 * _mp.pi)
        for k, ck in c.items():
            logv -= ck * _mp.log(_mp.gamma(_mp.mpf(k) / N))
        return _mp.e ** logv
    finally:
        _mp.mp.dps = old


def gross_normalization_certificate(dps: int = 120) -> Dict:
    """The computed vol_h for the N=15/30 stand (certificate H2)."""
    c15 = exponent_rule_15_30(15)
    c30 = exponent_rule_15_30(30)
    vol15 = gross_volume(15, c15, dps=dps)
    vol30 = gross_volume(30, c30, dps=dps)
    res15 = float(abs(vol15 - FROZEN_VOL_H))
    res30 = float(abs(vol30 - FROZEN_VOL_H))
    return {
        "stand": "N=15/30 Gross Gamma-normalization",
        "formula": "vol_h = (2*pi)^(sum c_k / 2) * prod Gamma(k/N)^(-c_k)",
        "c_15": {str(k): v for k, v in sorted(c15.items())},
        "c_30": {str(k): v for k, v in sorted(c30.items())},
        "sum_c_15": sum(c15.values()),
        "sum_c_30": sum(c30.values()),
        "vol_15": float(vol15),
        "vol_30": float(vol30),
        "residual_15": res15,
        "residual_30": res30,
        "threshold": 1e-60,
        "target": FROZEN_VOL_H,
        "sine_count_note": ("N=30: even indices inherit c^15; odd pairs "
                            "cancel via the reflection formula (odd sine "
                            "product = 2^-7); c_15 = 0 forced; the odd "
                            "exponent d = 4 is conventional"),
        "pass": bool(res15 < 1e-60 and res30 < 1e-60),
    }
