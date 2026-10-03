"""The v1.10 gauge/closure tests.

The psi-gauge theorem (C-018), the descent certificate (the
d(iota_R xi) class, C-017), the raw-period residual, and the
mod-p closed loop (C-012).
"""

from fractions import Fraction

import pytest

from verhodge.gauge import (gauge_identity_check, gauge_psi, OPS_ENGINE,
                            OPS_TRUE, descent_certificate,
                            psi_gauge_residual_check, modp_gauge_closure,
                            singular_fiber_note)
from verhodge.gdreduced import gamma_true_at, ModP


def test_gauge_identity_exact():
    """gauge_psi(L_c) == L_true exactly, both directions."""
    r = gauge_identity_check()
    assert r["pass"] and r["reverse_ok"]


def test_gauge_recursion_unrolls_to_target():
    """The unrolled recursion reproduces the certified coefficients."""
    got = gauge_psi(OPS_ENGINE)
    assert got[3] == {4: Fraction(6), -1: Fraction(4)}
    assert got[2] == {3: Fraction(7), -2: Fraction(-12)}
    assert got[1] == {2: Fraction(1), -3: Fraction(24)}
    assert got[0] == {-4: Fraction(-24)}
    assert got[4] == OPS_TRUE[4]


def test_descent_certificate_trivial_class():
    """The residue class of d(iota_R xi)|_(P^4\\X) is TRIVIAL."""
    for t in (Fraction(2), Fraction(3)):
        d = descent_certificate(t)
        assert d["pass"], d
        assert d["I1_master_form_identity"]
        assert d["I2_cartan_identity"]
        assert d["homogeneity_ok"]
        assert d["character_classes_ok"]
        assert d["lambda5"] == "0"


def test_raw_period_residual():
    """L_c annihilates g = f/psi (the raw pole-1 period)."""
    r = psi_gauge_residual_check((2, 3))
    assert r.get("pass", False)


def test_modp_gauge_closed_loop():
    """Derivation + gauge == certified operator, exact, mod p."""
    mc = modp_gauge_closure(primes=(101, 191), n_psi=4,
                            min_tests=8)
    assert mc["pass"]
    assert mc["n_fail"] == 0
    assert mc["n_tests"] >= 2 * 4 * 2


def test_gauge_values_match_certified_char0():
    """The specialized gauge recursion (char 0) matches the target."""
    from verhodge.gdreduced import Rat
    from verhodge.gauge import _gauge_values
    fld = Rat()
    for psi0 in (Fraction(2), Fraction(5)):
        den = psi0 ** 5 - 1
        # the ENGINE operator's monic coefficients at psi0, ASCENDING
        # order (g_0, g_1, g_2, g_3) — the engines' dict convention:
        # L_c = (psi^5-1) D^4 + 10 psi^4 D^3 + 25 psi^3 D^2
        #       + 15 psi^2 D + psi
        gam = [-psi0 / den,
               -15 * psi0 ** 2 / den,
               -25 * psi0 ** 3 / den,
               -10 * psi0 ** 4 / den]
        gauged = _gauge_values(fld, psi0, gam)
        for k in range(4):
            assert gauged[k] == gamma_true_at(k, psi0, fld)


def test_singular_fibers_degenerate_v110():
    sf = singular_fiber_note((101,))
    assert sf["all_degenerate"]
