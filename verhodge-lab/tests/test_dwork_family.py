"""The v1.11 tests: the Dwork family at every Calabi-Yau degree.

Covers: the certified psi-form operators (d = 3, 4, 5), the exact
series annihilation, the gauge identity both directions, the char-0
closed loop, the mod-p closed loop on degree-adapted prime grids, the
d = 5 regression against the v1.9/v1.10 certified target, the
hypergeometric numerical seal, and the chart-exactness certificate
(the C-019 tube register).
"""

from fractions import Fraction

from verhodge.dwork_family import (
    certified_psi_operator, series_coeffs, series_annihilation_check,
    gauge_identity_check_general, char0_closed_loop_d, closed_loop_d,
    hyper_seal_d, chart_exactness_certificate, la_eval, ModP,
)
from verhodge.gdreduced import TRUE_GAMMA_NUM, _laurent_eval
from verhodge.gauge import Rat


GRIDS = {3: (103, 109, 193), 4: (101, 281, 401), 5: (101, 191, 281)}


def test_series_ratios():
    for d, c1 in ((3, Fraction(2, 9)), (4, Fraction(6, 64)),
                  (5, Fraction(24, 625))):
        cs = series_coeffs(d, 2)
        assert cs[0] == 1 and cs[1] == c1


def test_series_annihilation_all_degrees():
    for d in (3, 4, 5):
        s = series_annihilation_check(d, 31)
        assert s["exact"], s


def test_certified_operator_leading_structure():
    for d in (3, 4, 5):
        b = certified_psi_operator(d)
        assert b[d - 1] == {0: Fraction(-1), d: Fraction(1)}


def test_gauge_identity_all_degrees():
    for d in (3, 4, 5):
        s = gauge_identity_check_general(d)
        assert s["exact"], s["violations"]


def test_char0_closed_loop_all_degrees():
    for d in (3, 4, 5):
        s = char0_closed_loop_d(d)
        assert s["all_ok"], s


def test_modp_closed_loop_all_degrees():
    for d in (3, 4, 5):
        s = closed_loop_d(d, GRIDS[d][:2], (2, 3))
        assert s["all_ok"], s["points"]


def test_d5_regression_against_v110_target():
    """The v1.11 general-d machinery must reproduce the certified
    v1.9/v1.10 quintic operator EXACTLY (the Laurent gamma
    specializations must agree mod p at grid points)."""
    b5 = certified_psi_operator(5)
    fld = Rat()
    for psi0 in (Fraction(2), Fraction(3), Fraction(5)):
        for j in (3, 2, 1, 0):
            got = la_eval(b5[j], psi0, fld)
            # the v1.10 gamma convention: g_j = -b_j/(psi^5 - 1)
            num = _laurent_eval(TRUE_GAMMA_NUM[j], psi0, fld)
            den = fld.sub(fld.pow_psi(psi0, 5), fld.of(1))
            want = fld.div(num, den)          # = -b_j/(psi^5-1)
            assert got == -want * den, (j, str(psi0), got, want)


def test_hyper_seal_all_degrees():
    for d in (3, 4, 5):
        s = hyper_seal_d(d, psis=(2.0, 3.0))
        assert s["worst_rel_residual"] < 1e-25, s


def test_chart_exactness_certificate():
    s = chart_exactness_certificate()
    assert s["exact"], s
    assert "14Q - 10" in s["constant"]
