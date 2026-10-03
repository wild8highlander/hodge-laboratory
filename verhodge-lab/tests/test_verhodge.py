"""The verhodge-lab test suite (pytest).

Waves v1.5-v1.8: the frozen-baseline regression, the two-scheme
discipline checks, the near-miss corpus, and the asymmetric
contract of the parser.
"""

import json
import os

import pytest

from verhodge.poly import cyclotomic, g2_is_irreducible, bareiss_det
from verhodge.census import census_direct, census_mobius, census_agreement, FROZEN_CENSUS
from verhodge.cyclotomic import (exact_layer, minpoly_2cos, FROZEN_CYC,
                                 FROZEN_CERT_K, bch_resolvent_11)
from verhodge.snf import smith_normal_form, smith_invariants
from verhodge.lattice import (cyclotomic_lattice_certificate,
                              k3_certificate, zeta30_is_zeta15)
from verhodge.gross import gross_normalization_certificate
from verhodge.input_schema import (parse_hodge_input, provenance_hash,
                                   dispatch, InputError, SCHEMA_VERSION)
from verhodge import dwork

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Wave 1/2: census + exact layer ──────────────────────────────────

def test_census_frozen_and_two_scheme():
    for N, exp in FROZEN_CENSUS.items():
        h, _, g = census_direct(N)
        assert h == exp
        assert h == census_mobius(N)
        assert sum(h.values()) == g


def test_census_agreement_range():
    for N in range(3, 40):
        assert census_agreement(N)


def test_phi_n_derived():
    assert cyclotomic(12) == [1, 0, -1, 0, 1]
    assert cyclotomic(1) == [-1, 1]
    assert all(cyclotomic(n)[-1] == 1 for n in range(2, 40))


@pytest.mark.parametrize("n", [5, 7, 9, 11, 15, 30])
def test_exact_layer(n):
    L = exact_layer(n)
    assert L["pass"]
    assert L["deg_matches_phi_half"]
    assert L["numeric_residual"] < 1e-25


def test_frozen_cubics_and_cert_k():
    assert minpoly_2cos(7) == (1, 1, -2, -1)
    assert minpoly_2cos(9) == (1, 0, -3, 1)
    assert minpoly_2cos(11) == (1, 1, -4, -3, 3, 1)
    assert g2_is_irreducible(list(minpoly_2cos(11)))


def test_near_miss_ne02_naive_snf():
    """The divisibility chain is NOT automatic (counterexample NE02)."""
    with open(os.path.join(ROOT, "counterexamples",
                           "NE02-naive-snf-diag.json")) as f:
        ne = json.load(f)
    assert ne["computed"]["divisibility_violated"]
    assert smith_invariants(ne["computed"]["matrix"]) == [1, 6]
    assert smith_invariants([[6, 0, 0], [0, 10, 0], [0, 0, 15]]) == \
        [1, 30, 30]


def test_near_miss_ne03_mobius_edge():
    """The Moebius census needs the c(k)=0 (k<3) guard (NE03)."""
    with open(os.path.join(ROOT, "counterexamples",
                           "NE03-mobius-edge-case.json")) as f:
        ne = json.load(f)
    assert ne["computed"]["disagrees"]


# ── Wave 3: SNF + lattices + Gross ──────────────────────────────────

def test_snf_properties_random():
    import random
    from verhodge.snf import egcd
    random.seed(11)
    for _ in range(25):
        m, n = random.randint(2, 5), random.randint(2, 5)
        A = [[random.randint(-9, 9) for _ in range(n)] for _ in range(m)]
        res = smith_normal_form(A)
        nz = [d for d in res["diag"] if d]
        assert all(nz[i + 1] % nz[i] == 0 for i in range(len(nz) - 1))
        # round trip
        U, V, S = res["U"], res["V"], res["S"]
        UA = [[sum(U[i][t] * A[t][j] for t in range(len(A)))
               for j in range(len(A[0]))] for i in range(len(U))]
        UAV = [[sum(UA[i][t] * V[t][j] for t in range(len(V)))
                for j in range(len(V[0]))] for i in range(len(UA))]
        assert UAV == S
        for i in range(min(len(A), len(A[0]))):
            assert all(S[i][j] == 0 for j in range(len(S[0])) if j != i)


def test_cert_h_byte_identical():
    from math import gcd
    from verhodge.poly import mobius_mu

    def tot(n):
        r, m, p = 1, n, 2
        while p * p <= m:
            if m % p == 0:
                m //= p
                k = 1
                while m % p == 0:
                    m //= p
                    k += 1
                r *= (p - 1) * p ** (k - 1)
            p += 1
        if m > 1:
            r *= m - 1
        return r

    def rj(N, k):
        g = gcd(N, k % N if k % N else N)
        m = N // g
        return mobius_mu(m) * tot(N) // tot(m)

    G = [[rj(15, i - j) for j in range(8)] for i in range(8)]
    inv = smith_invariants(G)
    assert inv == [1, 1, 5, 5, 15, 15, 15, 15]
    det = 1
    for d in inv:
        det *= d
    assert det == 3**4 * 5**6 == 1125 ** 2


def test_k3_computed():
    k = k3_certificate()
    assert k["pass"]
    assert k["snf_nonzero_invariants"][-2:] == [8, 8]


def test_zeta30_embedding():
    assert zeta30_is_zeta15()


def test_gross_computed():
    g = gross_normalization_certificate()
    assert g["pass"]
    assert g["residual_15"] < 1e-60
    assert g["residual_30"] < 1e-60


# ── Wave 4: HODGE-INPUT v1 ──────────────────────────────────────────

GOOD = {
    "schema": SCHEMA_VERSION,
    "variety": {"kind": "fermat-stand", "N": 15, "m": 5},
    "hodge_class": {"basis": "gamma-monomial"},
    "verification": {"type": "census"},
}


def test_parser_accepts_and_hashes():
    doc = parse_hodge_input(GOOD)
    h1 = provenance_hash(doc)
    h2 = provenance_hash(parse_hodge_input(json.dumps(GOOD)))
    assert h1 == h2 and len(h1) == 64
    runner, verdict = dispatch(doc)
    assert runner == "run_census"


@pytest.mark.parametrize("bad", [
    {"schema": "HODGE-INPUT v2"},
    {**GOOD, "variety": {"kind": "fermat-stand", "N": 1, "m": 5}},
    {**GOOD, "verification": {"type": "quantum-nonsense"}},
    {**GOOD, "hodge_class": {"basis": "mystery"}},
    {**GOOD, "variety": {"kind": "arbitrary-certified"}},
])
def test_parser_rejects(bad):
    with pytest.raises(InputError):
        parse_hodge_input(bad)


def test_asymmetric_contract_level3():
    doc = parse_hodge_input({
        "schema": SCHEMA_VERSION,
        "variety": {"kind": "arbitrary-certified",
                    "proof_ref": "monograph/T20"},
        "hodge_class": {"basis": "cycle"},
        "verification": {"type": "census"}})
    runner, verdict = dispatch(doc)
    assert runner is None and verdict == "NOT_DETERMINED"


def test_level0_documents_end_to_end():
    docs = os.path.join(ROOT, "inputs")
    names = [f for f in sorted(os.listdir(docs))
             if f.startswith("L0-") and f.endswith(".json")]
    assert len(names) >= 5
    for fname in names:
        with open(os.path.join(docs, fname)) as f:
            doc = parse_hodge_input(f.read())
        runner, verdict = dispatch(doc)
        assert runner is not None and verdict == "ALGEBRAIC_CERTIFICATE"


# ── Wave 5: the Dwork stand ─────────────────────────────────────────

def test_gd_cohomology():
    gd = dwork.gd_cohomology_certificate()
    assert gd["pass"]
    assert gd["b3_invariant"] == 4
    assert all(s["sum_rule_ok"] for s in gd["sum_rule_tests"])


def test_peel_known_values():
    assert dwork.peel_reduce((1, 0, 0, 0, 0), 0, 2) == \
        {2: {1: __import__("fractions").Fraction(1)},
         1: {0: __import__("fractions").Fraction(1, 5)}}


def test_periods_two_schemes():
    pc = dwork.periods_certificate((2, 3, 5))
    assert pc["pass"]


def test_point_counts():
    pc = dwork.point_count_certificate((11, 31), brute_prime=11)
    assert pc["pass"]


# ── near-miss NE04: singular fiber ──────────────────────────────────

def test_singular_fiber_flagged():
    doc = parse_hodge_input({
        "schema": SCHEMA_VERSION,
        "variety": {"kind": "dwork-pencil", "psi": 1},
        "hodge_class": {"basis": "residue-form"},
        "verification": {"type": "period"}})
    assert doc["variety"]["singular_fiber"] is True


# ── Wave 6 (v1.9): the PF operator stand ────────────────────────────

def test_pf_target_algebra():
    from verhodge.gdreduced import target_algebra_check, \
        operator_series_identity
    assert target_algebra_check()["pass"]
    assert operator_series_identity()["pass"]


def test_pf_psi_form_residual():
    from verhodge.gdreduced import psi_form_residual_check
    r = psi_form_residual_check((2, 3), dps=50)
    assert r["pass"]


def test_pf_engines_agree_modp():
    from verhodge.gdreduced import (ModP, picard_fuchs_gamma_fresh,
                                    picard_fuchs_gamma_peel)
    fld = ModP(101)
    for psi0 in (2, 3, 5):
        g_f = picard_fuchs_gamma_fresh(fld, psi0)
        g_p = picard_fuchs_gamma_peel(fld, psi0)
        assert g_f is not None and g_p is not None
        assert all(g_f[j] == g_p[j] for j in range(4))


def test_pf_singular_fibers_degenerate():
    from verhodge.gdreduced import (ModP, picard_fuchs_gamma_fresh)
    fld = ModP(101)
    for t in (1, 36):        # 1^5 = 36^5 = 1 (mod 101)
        assert picard_fuchs_gamma_fresh(fld, t) is None


def test_pf_gap_registered():
    from verhodge.gdreduced import operator_gap_analysis
    gap = operator_gap_analysis((2,))
    # v1.10: the v1.9 open gap is RESOLVED (the gauge theorem, V23)
    assert gap["status"].startswith("RESOLVED in v1.10")
    assert "C-012 closed" in gap["status"]


def test_near_miss_ne05_exists():
    import json, os
    d = json.load(open(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "counterexamples", "NE05-wrong-pf-target.json")))
    assert d["id"] == "NE05"


def test_registry_and_ledger_exist():
    assert os.path.exists(os.path.join(ROOT, "claims", "registry.yaml"))
    assert os.path.exists(os.path.join(ROOT, "complexity", "ledger.yaml"))
