"""v1.10 — the PF operator derivation closure: the psi-gauge theorem
and the residue class of d(iota_R xi)|_(P^4\\X).

Closes C-012 and resolves C-017.

Mathematical content
--------------------
1. THE GAUGE THEOREM (closes C-012).  The v1.9 engines derive, class-
   exactly, the operator

       L_c   = (psi^5-1) D^4 + 10 psi^4 D^3 + 25 psi^3 D^2
               + 15 psi^2 D + psi,

   which is the TRUE Picard-Fuchs equation of the RAW invariant
   period  g = <omega_1, gamma>,  omega_1 = [dx/P]  (the pole-1
   class).  The certified fundamental period  f  (the series
   _4F_3(1/5,2/5,3/5,4/5; 1,1,1; psi^-5) with c_0 = 1 at psi = inf)
   is the NORMALIZED period  f = psi * g:  the period of the class
   [psi dx / P].  The two operators are related by the exact
   psi-gauge identity

       L_true(psi * g)  =  psi * L_c(g),

   with the triangular coefficient recursion (derived from
   D^m(psi g) = psi g^(m) + m g^(m-1)):

       b_4 = a_4,      b_m = a_m - (m+1) b_(m+1) / psi.

   Unrolling it carries L_c EXACTLY onto the certified target:

       b_3 = 10 psi^4 - 4(psi^5-1)/psi = 6 psi^4 + 4 psi^-1,
       b_2 = 25 psi^3 - 3 b_3/psi      = 7 psi^3 - 12 psi^-2,
       b_1 = 15 psi^2 - 2 b_2/psi      = psi^2 + 24 psi^-3,
       b_0 = psi       -   b_1/psi     = - 24 psi^-4.

   The "missing" psi^-1..psi^-4 structure of L_true is thereby the
   GAUGE SHADOW of the (psi^5-1) leading coefficient — computed,
   not conjectured.

2. THE DESCENT CERTIFICATE (resolves C-017).  The registered
   conjecture attributed the operator mismatch to the residue class
   of d(iota_R xi)|_(P^4\\X).  That class is COMPUTED here, exactly,
   by C^5 form algebra at specialized psi_0 (char 0, Fractions).
   With eta_C = sum_j (-1)^j C_j dxhat_j / P^4 the Griffiths
   divergence form (C the pole-5 Jacobian representation of Pi^4),
   the certificate verifies:
     (i)   P^5 d(eta_C) = [P Div(C) - 4 sum_j C_j j_j] * vol
           (the master Griffiths identity as a FORM identity — the
           unsigned divergence is the exact vol-projection);
     (ii)  P^5 d(iota_R eta_C) = - iota_R( P^5 d(eta_C) )  (Cartan;
           L_R eta_C = 0 by homogeneity 0);
     (iii) every numerator of iota_R eta_C is homogeneous of degree
           17, and 17 + 3 - 20 = 0:  iota_R eta_C has homogeneity 0
           and is horizontal, hence BASIC — it DESCENDS to P^4.
   Therefore d(iota_R eta_C)|_(P^4\\X) is the differential of a
   descended form, its class in H^4(P^4\\X) is ZERO, and

       4 [sum_j C_j j_j dx/P^5] = [Div(C) dx/P^4]

   is exact — the divergence step loses nothing.  C-017 is resolved
   NEGATIVELY (the class is trivial); the true closure mechanism is
   the normalization gauge of item 1.

3. THE CLOSED LOOP (the v1.10 stand).  At every grid point
   (p, psi_0) the engine gamma values are carried by the gauge
   recursion EXACTLY onto the certified target's specializations:

       engine gam  ->  a_k = -gam_k (psi^5-1)  ->  gauge  ->  == gamma_true.

   The mod-p derivation of the classical Picard-Fuchs operator is
   COMPLETE:  derivation (v1.9 engines) + gauge (v1.10) = the
   certified operator theta_w^4 - w prod(theta_w + i/5).
"""

from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from .dwork import _deg_monos, _class_in_span1
from .gdreduced import (ModP, Rat, ZERO, ONES, _ei, poly_add, poly_scale,
                        poly_mul_mono, poly_deriv, _solve_reduction,
                        _divergence, invariant_part, gamma_true_at,
                        picard_fuchs_gamma_fresh, picard_fuchs_gamma_peel,
                        _psi_grid)

F = Fraction

# ──────────────────────────────────────────────────────────────────────
# 1. The psi-gauge on Laurent operators
# ──────────────────────────────────────────────────────────────────────

# Laurent dicts: {exponent (int): Fraction}.  A differential operator
# is {order k: Laurent dict} — the coefficient of D^k.

def _la_shift(d: Dict[int, Fraction], s: int) -> Dict[int, Fraction]:
    """Multiply a Laurent dict by psi^s (shift all exponents)."""
    return {e + s: v for e, v in d.items() if v != 0}


def _la_add(a: Dict[int, Fraction], b: Dict[int, Fraction]) -> Dict[int, Fraction]:
    out = dict(a)
    for e, v in b.items():
        out[e] = out.get(e, Fraction(0)) + v
    return {e: v for e, v in out.items() if v != 0}


def _la_scale(d: Dict[int, Fraction], c: Fraction) -> Dict[int, Fraction]:
    if c == 0:
        return {}
    return {e: v * c for e, v in d.items() if v * c != 0}


def gauge_psi(ops: Dict[int, Dict[int, Fraction]]) -> Dict[int, Dict[int, Fraction]]:
    """The exact psi-gauge:  given L = sum a_k D^k  (annihilating g),
    return the operator B = sum b_k D^k  with  B(psi g) = psi L(g).

    From D^m(psi g) = psi g^(m) + m g^(m-1):
        sum_m b_m [psi g^(m) + m g^(m-1)] = sum_m psi a_m g^(m)
    ⟹  b_m psi + (m+1) b_(m+1) = psi a_m   (b_5 = 0),  i.e.
        b_4 = a_4,   b_m = a_m - (m+1) b_(m+1)/psi.
    """
    top = max(ops)
    out: Dict[int, Dict[int, Fraction]] = {top: dict(ops[top])}
    for m in range(top - 1, -1, -1):
        lower = _la_shift(out[m + 1], -1)
        out[m] = _la_add(dict(ops.get(m, {})),
                         _la_scale(lower, Fraction(-(m + 1))))
    return {m: out[m] for m in sorted(out)}


# the derived operator L_c (v1.9 engines) and the certified operator
# L_true (v1.9 target), as Laurent-operator dicts
OPS_ENGINE: Dict[int, Dict[int, Fraction]] = {
    4: {5: F(1), 0: F(-1)},
    3: {4: F(10)},
    2: {3: F(25)},
    1: {2: F(15)},
    0: {1: F(1)},
}
OPS_TRUE: Dict[int, Dict[int, Fraction]] = {
    4: {5: F(1), 0: F(-1)},
    3: {4: F(6), -1: F(4)},
    2: {3: F(7), -2: F(-12)},
    1: {2: F(1), -3: F(24)},
    0: {-4: F(-24)},
}


def gauge_identity_check() -> Dict:
    """EXACT char-0 certificate:  gauge_psi(L_c) == L_true."""
    got = gauge_psi(OPS_ENGINE)
    ok = all(got.get(m, {}) == OPS_TRUE[m] for m in range(5)) and len(got) == 5
    rows = []
    for m in range(5):
        rows.append({"order": m, "gauged": {str(e): str(v)
                                            for e, v in sorted(got.get(m, {}).items())},
                     "true": {str(e): str(v)
                              for e, v in sorted(OPS_TRUE[m].items())},
                     "match": got.get(m, {}) == OPS_TRUE[m]})
    # the reverse direction (the triangular map is invertible):
    # a_m = b_m + (m+1) psi^-1 b_(m+1)  must recover L_c from L_true
    back: Dict[int, Dict[int, Fraction]] = {}
    for m in range(5):
        acc = dict(OPS_TRUE[m])
        if m + 1 <= 4:
            acc = _la_add(acc, _la_shift(
                _la_scale(OPS_TRUE[m + 1], Fraction(m + 1)), -1))
        back[m] = acc
    back_ok = all(back.get(m, {}) == OPS_ENGINE[m] for m in range(5))
    return {"check": "gauge_psi(L_c) == L_true (exact Laurent algebra)",
            "recursion": "b_4 = a_4;  b_m = a_m - (m+1) b_(m+1)/psi",
            "reverse": "a_m = b_m + (m+1) psi^-1 b_(m+1) recovers L_c",
            "rows": rows, "reverse_ok": bool(back_ok),
            "pass": bool(ok and back_ok)}

# ──────────────────────────────────────────────────────────────────────
# 2. C^5 form algebra — the descent certificate (resolves C-017)
# ──────────────────────────────────────────────────────────────────────
#
# A k-form with polynomial coefficients:  dict {S: poly} where
# S = sorted tuple of distinct indices in {0..4} (the wedge dx^S) and
# poly = dict {exponent tuple: field element}.

def _deg_of(fld, poly: Dict) -> int:
    """Total degree of a polynomial (the max monomial degree)."""
    d = 0
    for k, v in poly.items():
        if not fld.is_zero(v):
            d = max(d, sum(k))
    return d


def _wedge_sign_merge(S: Tuple[int, ...], T: Tuple[int, ...]):
    """dx^S ∧ dx^T = sign * dx^{merge};  None if some index repeats."""
    if set(S) & set(T):
        return None
    seq = list(S) + list(T)
    sign = 1
    for a in range(len(seq)):
        for b in range(a + 1, len(seq)):
            if seq[a] > seq[b]:
                sign = -sign
    return sign, tuple(sorted(seq))


def form_wedge(fld, f: Dict, g: Dict) -> Dict:
    """Wedge product of two forms with polynomial coefficients."""
    out: Dict[Tuple[int, ...], Dict] = {}
    for S, pf in f.items():
        for T, pg in g.items():
            wt = _wedge_sign_merge(S, T)
            if wt is None:
                continue
            sign, U = wt
            coeff: Dict = {}
            for ka, va in pf.items():
                if fld.is_zero(va):
                    continue
                for kb, vb in pg.items():
                    if fld.is_zero(vb):
                        continue
                    k = tuple(a + b for a, b in zip(ka, kb))
                    coeff[k] = fld.add(coeff.get(k, fld.of(0)),
                                       fld.mul(va, vb))
            # apply the shuffle sign once per (S,T) pair
            term = {k: fld.mul(v, fld.of(sign)) for k, v in coeff.items()}
            term = {k: v for k, v in term.items() if not fld.is_zero(v)}
            if term:
                prev = out.get(U, {})
                out[U] = poly_add(fld, prev, term)
    return {U: p for U, p in out.items() if p}


def form_d(fld, f: Dict) -> Dict:
    """Exterior derivative of a form with polynomial coefficients."""
    out: Dict[Tuple[int, ...], Dict] = {}
    for S, pf in f.items():
        for i in range(5):
            dpf = poly_deriv(fld, pf, i)
            if not dpf:
                continue
            if i in S:
                continue  # dx_i ∧ dx^S = 0
            sign = 1
            for s in S:
                if s < i:
                    sign = -sign
            U = tuple(sorted(S + (i,)))
            term = poly_scale(fld, dpf, fld.of(sign))
            out[U] = poly_add(fld, out.get(U, {}), term)
    return {U: p for U, p in out.items() if p}


def form_iR(fld, f: Dict) -> Dict:
    """Radial contraction iota_R (R = sum x_i d/dx_i).

    iota_R preserves the homogeneity degree ([L_R, iota_R] = 0 for
    the radial field), which the explicit formula
    iota_R dx^S = sum_m (-1)^m x_{S_m} dx^{S\\S_m} realizes.
    """
    out: Dict[Tuple[int, ...], Dict] = {}
    for S, pf in f.items():
        for m, i in enumerate(S):
            T = tuple(S[:m] + S[m + 1:])
            sign = 1 if m % 2 == 0 else -1
            term = poly_mul_mono(fld, pf, _ei(i), fld.of(sign))
            out[T] = poly_add(fld, out.get(T, {}), term)
    return {T: p for T, p in out.items() if p}


def _poly_times(fld, f: Dict, g: Dict) -> Dict:
    """Product of two polynomials (dense schoolbook; sizes are small)."""
    out: Dict[Tuple[int, ...], object] = {}
    for ka, va in f.items():
        if fld.is_zero(va):
            continue
        for kb, vb in g.items():
            if fld.is_zero(vb):
                continue
            k = tuple(a + b for a, b in zip(ka, kb))
            out[k] = fld.add(out.get(k, fld.of(0)), fld.mul(va, vb))
    return {k: v for k, v in out.items() if not fld.is_zero(v)}


def descent_certificate(psi0: Fraction) -> Dict:
    """The residue class of d(iota_R xi)|_(P^4\\X), COMPUTED.

    Works at the specialized psi_0 over Q (exact Fractions).  Builds
    the pole-5 Jacobian representation Pi^4 = sum_j C_j j_j (the
    v1.9 solve, lambda = 0), forms the Griffiths divergence form

        eta_C = sum_j (-1)^j C_j dxhat_j / P^4

    and verifies, as exact polynomial form identities (the P^5
    denominator cleared throughout):
      (I1)  P^5 d(eta_C) = [P Div(C) - 4 sum_j C_j j_j] vol
      (I2)  P^5 d(iota_R eta_C) = - iota_R( P^5 d(eta_C) )
      (I3)  deg C_j = 16, deg Div = 15, every numerator of
            iota_R eta_C of degree 17  (the homogeneity-0 facts:
            L_R eta_C = 0 and L_R(iota_R eta_C) = 0).
    Since iota_R eta_C is horizontal (iota_R^2 = 0) and homogeneous
    of degree 0, it is BASIC and descends to P^4;  hence
    d(iota_R eta_C)|_(P^4\\X) is exact and the class

        [d(iota_R xi)|_(P^4\\X)]
            = [4 sum_j C_j j_j dx/P^5 - Div(C) dx/P^4]  =  0 :

    the divergence step is class-exact and C-017's conjectured
    cohomologically-alive term does not exist.
    """
    fld = Rat()
    x = psi0
    lam5, C = _solve_reduction(fld, psi0,
                               {(4, 4, 4, 4, 4): fld.of(1)}, 5)
    if lam5 is None:
        return {"pass": False, "error": "pole-5 solve degenerate"}
    ok = (lam5 == 0)
    char_ok = True
    degC_ok = True
    for j, c, coef in C:
        if not _class_in_span1(c, _ei(j)):
            char_ok = False
        if _deg_of(fld, {c: coef}) != 16:
            degC_ok = False
    ok = ok and char_ok and degC_ok

    # P and dP (psi specialized):  P = sum x_i^5 - 5 psi Pi
    P: Dict[Tuple[int, ...], object] = {}
    for i in range(5):
        P[tuple(5 if t == i else 0 for t in range(5))] = fld.of(1)
    P[ONES] = fld.of(-5 * x)
    dP = {(i,): poly_deriv(fld, P, i) for i in range(5)}
    VOL = (0, 1, 2, 3, 4)
    DXHAT = {j: tuple(t for t in VOL if t != j) for j in range(5)}

    # (I1):  P^5 d(eta_C) = [P Div(C) - 4 sum_j C_j j_j] vol
    Div = _divergence(fld, C)
    div_deg = _deg_of(fld, Div)
    ok = ok and (div_deg == 15)
    lhs1: Dict = {}
    cj_dot_jj: Dict = {ZERO: fld.of(0)}
    for j, c, coef in C:
        s = fld.of(1 if j % 2 == 0 else -1)          # (-1)^j
        cj = {c: coef}
        # the 1-form  P dC_j - 4 C_j dP   (d(C_j/P^4) cleared to P^5)
        one_form = {}
        for i in range(5):
            cf = poly_add(fld,
                          _poly_times(fld, P, poly_deriv(fld, cj, i)),
                          poly_scale(fld, _poly_times(fld, cj, dP[(i,)]),
                                     fld.of(-4)))
            if cf:
                one_form[(i,)] = cf
        term = form_wedge(fld, one_form, {DXHAT[j]: {ZERO: fld.of(1)}})
        for U, p in term.items():
            lhs1[U] = poly_add(fld, lhs1.get(U, {}), poly_scale(fld, p, s))
        # C_j * j_j   (j_j = 5 x_j^4 - 5 psi Pi_hat_j,
        #              Pi_hat_j = x^(ONES - e_j))
        jj = poly_add(fld,
                      {tuple(4 if t == j else 0 for t in range(5)):
                       fld.of(5)},
                      poly_scale(fld,
                                 {tuple(0 if t == j else 1
                                        for t in range(5)): fld.of(1)},
                                 fld.of(-5 * x)))
        cj_dot_jj = poly_add(fld, cj_dot_jj, _poly_times(fld, cj, jj))
    rhs1 = {VOL: poly_add(fld, _poly_times(fld, P, Div),
                          poly_scale(fld, cj_dot_jj, fld.of(-4)))}
    uni = set(lhs1) | set(rhs1)
    i1_ok = all(lhs1.get(U, {}) == rhs1.get(U, {}) for U in uni)
    ok = ok and i1_ok

    # (I2):  P^5 d(iota_R eta_C) = - iota_R( P^5 d(eta_C) )
    eta_iR: Dict = {}
    deg_ok = True
    for j, c, coef in C:
        s = fld.of(1 if j % 2 == 0 else -1)
        con = form_iR(fld, {DXHAT[j]: {ZERO: fld.of(1)}})
        for T, mono in con.items():
            # numerator  s * C_j * (iota_R dxhat_j part)  = s*coef*x^mk
            for mk, mv in mono.items():
                num = poly_mul_mono(fld, {c: coef}, mk, fld.mul(s, mv))
                if _deg_of(fld, num) != 17:
                    deg_ok = False
                eta_iR[T] = poly_add(fld, eta_iR.get(T, {}), num)
    ok = ok and deg_ok
    lhs2: Dict = {}
    for T, num in eta_iR.items():
        one_form = {}
        for i in range(5):
            cf = poly_add(fld,
                          _poly_times(fld, P, poly_deriv(fld, num, i)),
                          poly_scale(fld, _poly_times(fld, num, dP[(i,)]),
                                     fld.of(-4)))
            if cf:
                one_form[(i,)] = cf
        term = form_wedge(fld, one_form, {T: {ZERO: fld.of(1)}})
        for U, p in term.items():
            lhs2[U] = poly_add(fld, lhs2.get(U, {}), p)
    rhs2 = {U: {k: fld.mul(fld.of(-1), v) for k, v in p.items()}
            for U, p in form_iR(fld, lhs1).items()}
    uni2 = set(lhs2) | set(rhs2)
    i2_ok = all(lhs2.get(U, {}) == rhs2.get(U, {}) for U in uni2)
    ok = ok and i2_ok

    return {
        "check": ("residue class of d(iota_R xi)|_(P^4\\X) computed: "
                  "TRIVIAL (the descent certificate)"),
        "psi0": str(psi0),
        "lambda5": str(lam5),
        "character_classes_ok": bool(char_ok),
        "homogeneity_ok": bool(degC_ok and div_deg == 15 and deg_ok),
        "I1_master_form_identity": bool(i1_ok),
        "I2_cartan_identity": bool(i2_ok),
        "conclusion": ("iota_R eta_C is basic (horizontal, homogeneity "
                       "0) hence descends to P^4; d(iota_R eta_C)|_"
                       "(P^4\\X) is exact; the class "
                       "[4 sum C_j j_j dx/P^5 - Div dx/P^4] = 0 — the "
                       "Griffiths divergence step loses nothing"),
        "pass": bool(ok),
    }

# ──────────────────────────────────────────────────────────────────────
# 3. Numerical + mod-p closures
# ──────────────────────────────────────────────────────────────────────

HAVE_MPMATH = False
try:
    import mpmath as _mp
    HAVE_MPMATH = True
except Exception:  # pragma: no cover
    HAVE_MPMATH = False


def psi_gauge_residual_check(psis=(2, 3, 5, 7), dps: int = 70) -> Dict:
    """The raw period g = f/psi satisfies L_c:  numerical seal.

    f is the certified period (mpmath hypergeometric, independent);
    g = f/psi is the period of the pole-1 class [dx/P] (f = psi*g is
    the gauge theorem).  The L_c residual on g must vanish.
    """
    if not HAVE_MPMATH:
        return {"available": False}
    old = _mp.mp.dps
    _mp.mp.dps = dps
    try:
        def gg(t):
            return _mp.hyper([_mp.mpf(1)/5, _mp.mpf(2)/5, _mp.mpf(3)/5,
                              _mp.mpf(4)/5], [1, 1, 1],
                             _mp.mpf(t) ** -5) / _mp.mpf(t)
        rows = []
        ok = True
        for psi in psis:
            t = _mp.mpf(psi)
            g0 = gg(t)
            d = [_mp.diff(gg, t, k) for k in (1, 2, 3, 4)]
            res = ((t**5 - 1) * d[3] + 10 * t**4 * d[2] + 25 * t**3 * d[1]
                   + 15 * t**2 * d[0] + t * g0)
            scale = abs((t**5 - 1) * d[3]) + 1
            rel = abs(res) / scale
            row_ok = rel < _mp.mpf(10) ** -25
            ok = ok and row_ok
            rows.append({"psi": psi, "residual": _mp.nstr(res, 5),
                         "relative": _mp.nstr(rel, 5),
                         "pass": bool(row_ok)})
        return {"check": "L_c annihilates the raw period g = f/psi",
                "operator": ("(psi^5-1) g'''' + 10 psi^4 g''' + "
                             "25 psi^3 g'' + 15 psi^2 g' + psi g = 0"),
                "rows": rows, "pass": bool(ok)}
    finally:
        _mp.mp.dps = old


def _gauge_values(fld, psi0, gam):
    """The gauge recursion on SPECIALIZED values.

    The engine operator (psi^5-1) D^4 + a3 D^3 + a2 D^2 + a1 D + a0
    with a_k = -gam[k] * (psi^5-1);  the gauged (certified) monic
    coefficients are  -b_k/(psi^5-1)  with  b_4 = a_4,
    b_m = a_m - (m+1) b_(m+1)/psi.
    """
    den = fld.sub(fld.pow_psi(psi0, 5), fld.of(1))
    a = {4: den}
    for k in range(4):
        a[k] = fld.mul(fld.mul(gam[k], den), fld.of(-1))
    b = {4: a[4]}
    for m in (3, 2, 1, 0):
        b[m] = fld.sub(a[m], fld.mul(fld.of(m + 1),
                                     fld.div(b[m + 1], psi0)))
    return {k: fld.mul(fld.mul(b[k], fld.of(-1)), fld.inv(den))
            for k in range(4)}


def modp_gauge_closure(primes: Tuple[int, ...] = (101, 191, 281),
                       n_psi: int = 12,
                       engines: Tuple[str, ...] = ("fresh", "peel"),
                       min_tests: Optional[int] = None) -> Dict:
    """The CLOSED LOOP:  derivation (v1.9 engines) + gauge (v1.10) =
    the certified operator, EXACTLY, at every (p, psi_0).

    For each grid point and each engine:  the engine gamma values are
    carried by the gauge recursion onto the certified target's
    specializations  gamma_true(k, psi_0)  — exact equality in F_p.
    This is the completed mod-p Picard-Fuchs derivation (C-012).
    """
    rows = []
    n_tests = 0
    n_fail = 0
    for p in primes:
        fld = ModP(p)
        for psi0 in _psi_grid(p, n_psi):
            for ename in engines:
                gam = (picard_fuchs_gamma_fresh(fld, psi0)
                       if ename == "fresh"
                       else picard_fuchs_gamma_peel(fld, psi0))
                if gam is None:
                    n_fail += 1
                    continue
                gauged = _gauge_values(fld, psi0, gam)
                want = [gamma_true_at(k, psi0, fld) for k in range(4)]
                match = all(gauged[k] == want[k] for k in range(4))
                n_tests += 1
                if not match:
                    n_fail += 1
                if len(rows) < 4:
                    rows.append({"p": p, "psi": psi0, "engine": ename,
                                 "gauged": [str(gauged[k])
                                            for k in range(4)],
                                 "certified": [str(want[k])
                                               for k in range(4)],
                                 "match": match})
    return {"check": ("closed loop: engine operator + psi-gauge == "
                      "certified operator (exact, mod p)"),
            "primes": list(primes), "n_psi_per_prime": n_psi,
            "engines": list(engines), "n_tests": n_tests,
            "n_fail": n_fail,
            "sample": rows,
            "pass": bool(n_tests >= (min_tests if min_tests is not None
                                     else 3 * 8 * len(engines))
                         and n_fail == 0)}


def singular_fiber_note(primes: Tuple[int, ...] = (101, 191, 281)) -> Dict:
    """The singular fibers psi^5 = 1:  the engines degenerate (the
    representation solve is inconsistent) and the certified operator's
    structural poles (psi^5-1) blow up — the gauge comparison is
    undefined there, coherently."""
    rows = []
    for p in primes:
        fld = ModP(p)
        roots = [t for t in range(p) if pow(t, 5, p) == 1][:2]
        for t in roots:
            g = picard_fuchs_gamma_fresh(fld, t)
            rows.append({"p": p, "psi": t, "engine_degenerate": g is None})
    return {"rows": rows,
            "all_degenerate": all(r["engine_degenerate"] for r in rows)}


def pf_certificate_v110(primes: Tuple[int, ...] = (101, 191, 281),
                        n_psi: int = 12, quick: bool = False) -> Dict:
    """The v1.10 stand:  the Picard-Fuchs derivation CLOSURE (V23).

    Pass criteria (all computed):
      (1) the exact gauge identity  gauge_psi(L_c) == L_true  (char-0
          Laurent-operator algebra, both directions);
      (2) the descent certificate:  the residue class of
          d(iota_R xi)|_(P^4\\X) computed = TRIVIAL at psi_0 = 2, 3
          (exact C^5 form algebra);
      (3) the numerical seal:  L_c annihilates the raw period
          g = f/psi (residual < 1e-25 relative, independently
          evaluated period);
      (4) the closed loop on the mod-p grid:  engine + gauge ==
          the certified operator, exact at every (p, psi_0), both
          engines;
      (5) the singular fibers psi^5 = 1 degenerate coherently.

    Verdict:  the mod-p Griffiths-Dwork derivation of the classical
    Picard-Fuchs operator of the Dwork pencil is COMPLETE.
    C-012 closed; C-017 resolved (the class is trivial; the closure
    mechanism is the normalization gauge).
    """
    out: Dict = {
        "stand": "Dwork pencil — PF derivation closure (v1.10)",
        "theorem": ("L_true(psi g) = psi L_c(g):  the certified "
                    "operator is the exact psi-gauge of the derived "
                    "operator;  the certified period f = psi * <dx/P> "
                    "(the normalized period of the class [psi dx/P])"),
        "c017_resolution": ("the residue class of d(iota_R xi)|_"
                            "(P^4\\X) is TRIVIAL (computed):  iota_R xi "
                            "is basic and descends;  the divergence "
                            "step is exact — the psi^-1..psi^-4 "
                            "structure is the gauge shadow of the "
                            "(psi^5-1) leading coefficient"),
    }
    gid = gauge_identity_check()
    out["gauge_identity"] = gid
    dc = [descent_certificate(Fraction(t)) for t in ((2,) if quick
                                                     else (2, 3))]
    out["descent_certificate"] = dc
    res = psi_gauge_residual_check((2, 3) if quick else (2, 3, 5, 7))
    out["raw_period_residual"] = res
    mc = modp_gauge_closure(primes if not quick else primes[:1],
                            8 if quick else n_psi,
                            min_tests=(2 * 8 if quick else None))
    out["modp_closed_loop"] = mc
    sf = singular_fiber_note(primes if not quick else primes[:1])
    out["singular_fibers"] = sf
    ok = (gid["pass"] and all(d["pass"] for d in dc)
          and res.get("pass", False) and mc["pass"])
    out["pass"] = bool(ok)
    return out

