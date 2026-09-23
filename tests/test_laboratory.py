"""Unit tests for the Hodge Laboratory core (laboratory.py).

The suite focuses on the exact integer layer and the high-precision
period identities.  Everything is deterministic — no seeds, no
randomness.  Run:  python3 -m pytest tests/ -q
"""

import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    'laboratory', REPO / 'laboratory.py')
laboratory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(laboratory)

mp = laboratory.mp
mpf = laboratory.mpf

mp.dps = 35


# ────────────────────────────────────────────────────────────────────
# V1 — character census
# ────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('N,genus', [(4, 3), (5, 6), (7, 15), (15, 91),
                                     (30, 406)])
def test_census_total_matches_genus(N, genus):
    h, by_d, g = laboratory.census(N)
    assert g == genus
    assert sum(h.values()) == g


def test_census_two_independent_schemes_agree():
    """The direct gcd census and the Möbius inversion must agree."""
    for N in (8, 12, 15, 30):
        h, _, _ = laboratory.census(N)
        hm = laboratory.census_mobius(N)
        for d in set(h) | set(hm):
            assert h.get(d, 0) == hm.get(d, 0), (N, d)


def test_census_known_tables():
    h15, _, _ = laboratory.census(15)
    assert h15 == {3: 1, 5: 6, 15: 84}
    h30, _, _ = laboratory.census(30)
    assert h30 == {3: 1, 5: 6, 6: 9, 10: 30, 15: 84, 30: 276}


# ────────────────────────────────────────────────────────────────────
# Periods: closed form vs independent quadrature
# ────────────────────────────────────────────────────────────────────

def test_period_closed_vs_numeric_small_sample():
    """Closed Gamma-form vs tanh-sinh quadrature, independent methods."""
    worst = 0.0
    for (N, a, b) in ((15, 1, 1), (15, 2, 3), (30, 1, 2)):
        for (r, s) in ((0, 0), (1, 0), (0, 1)):
            pc = laboratory.period_closed(N, a, b, r, s)
            pn = laboratory.period_numeric(N, a, b, r, s)
            worst = max(worst, laboratory.rel_err(pc, pn))
    assert worst < 1e-25, worst


def test_phase_law_exact():
    """arg P(r, s) must equal 2*pi*(r*a + s*b)/N exactly."""
    N, a, b = 15, 2, 3
    for (r, s) in ((0, 0), (1, 0), (0, 1), (2, 5)):
        pn = laboratory.period_numeric(N, a, b, r, s)
        expected = 2 * mp.pi * ((r * a + s * b) % N) / N
        dev = abs(mp.arg(pn) - expected)
        dev = min(dev, abs(dev - 2 * mp.pi))
        assert float(dev) < 1e-25, (r, s, float(dev))


def test_equivariance():
    """P(r+u, s+v) = zeta^{ua+vb} * P(r, s) — the mu_N x mu_N law."""
    N = 15
    for (a, b) in ((1, 1), (2, 3)):
        for (u, v) in ((1, 0), (0, 1), (1, 1)):
            base = laboratory.period_closed(N, a, b, 1, 0)
            shifted = laboratory.period_closed(N, a, b, 1 + u, v)
            factor = laboratory.expj(2 * mp.pi * ((u * a + v * b) % N) / N)
            assert laboratory.rel_err(shifted, factor * base) < 1e-30


def test_chain_integrity_v5():
    """Orbit sum over (k, k) vanishes for a+b not 0 mod N and equals
    Omega for the positive control a+b = N."""
    def orbit_sum(N, a, b):
        acc = laboratory.mpc(0)
        for k in range(N):
            acc += laboratory.period_closed(N, a, b, k, k)
        return acc

    for N in (15, 30):
        for (a, b) in ((2, 3), (4, 7)):
            val = abs(orbit_sum(N, a, b))
            norm = abs(laboratory.omega_closed(N, a, b))
            assert float(val / norm) < 1e-25, (N, a, b, float(val))
        a, b = (7, 8) if N == 15 else (7, 23)
        dev = laboratory.rel_err(orbit_sum(N, a, b),
                                 laboratory.omega_closed(N, a, b))
        assert dev < 1e-25, (N, a, b, dev)


def test_reflection_ladder_v6():
    for N in (15, 30):
        for k in range(1, N):
            lhs = (laboratory.mgamma(mpf(k) / N)
                   * laboratory.mgamma(1 - mpf(k) / N))
            rhs = mp.pi / laboratory.sin(mp.pi * k / N)
            assert laboratory.rel_err(lhs, rhs) < 1e-30


# ────────────────────────────────────────────────────────────────────
# Exact integer layer
# ────────────────────────────────────────────────────────────────────

def test_k3_rank_exact():
    """Exact rank over Q of the 49x49 K3 intersection matrix is 20."""
    from laboratory import _int_rank

    def inter(l1, l2):
        if l1 == l2:
            return -2
        f1, a1, b1 = l1
        f2, a2, b2 = l2
        if f1 == f2:
            return 1 if ((a1 == a2) != (b1 == b2)) else 0
        if {f1, f2} == {1, 2}:
            return 1 if (a1 + b2 - a2 - b1) % 4 == 0 else 0
        if {f1, f2} == {1, 3}:
            if f1 == 1:
                return 1 if (a2 - a1 - b1 - b2 - 1) % 4 == 0 else 0
            return 1 if (a1 - a2 - b2 - b1 - 1) % 4 == 0 else 0
        return 1 if (a1 + b1 - a2 - b2) % 4 == 0 else 0

    lines = [(f, a, b) for f in (1, 2, 3)
             for a in range(4) for b in range(4)]
    n = len(lines)
    G = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(i, n):
            v = inter(lines[i], lines[j])
            G[i][j] = G[j][i] = v
    for i in range(n):
        G[i][n] = G[n][i] = 1
    G[n][n] = 4
    assert _int_rank(G) == 20


def test_k3_intersection_rules_sane():
    """Self-intersection of a line is -2; the diagonal of the Gram
    matrix is built from that rule."""
    def py_inter(l1, l2):
        if l1 == l2:
            return -2
        f1, a1, b1 = l1
        f2, a2, b2 = l2
        if f1 == f2:
            return 1 if ((a1 == a2) != (b1 == b2)) else 0
        if {f1, f2} == {1, 2}:
            return 1 if (a1 + b2 - a2 - b1) % 4 == 0 else 0
        if {f1, f2} == {1, 3}:
            if f1 == 1:
                return 1 if (a2 - a1 - b1 - b2 - 1) % 4 == 0 else 0
            return 1 if (a1 - a2 - b2 - b1 - 1) % 4 == 0 else 0
        return 1 if (a1 + b1 - a2 - b2) % 4 == 0 else 0

    lines = [(f, a, b) for f in (1, 2, 3)
             for a in range(4) for b in range(4)]
    for ln in lines:
        assert py_inter(ln, ln) == -2
    # symmetry of the pairing
    for l1 in lines[::7]:
        for l2 in lines[::5]:
            assert py_inter(l1, l2) == py_inter(l2, l1)


def test_snf_discriminant_volume():
    snf = (1, 1, 5, 5, 15, 15, 15, 15)
    disc = math.prod(snf)
    assert disc == 1265625
    assert math.isqrt(disc) == 1125
    assert disc == 3 ** 4 * 5 ** 6


def test_klein_invariants():
    c4, Delta = 105, -343
    j = c4 ** 3 // Delta
    assert j == -3375 == -(15 ** 3)
    assert Delta * j == c4 ** 3


def test_arf_enumeration_matches_closed_formulas():
    """The full enumeration of quadratic forms must reproduce the
    classical counts 2^(g-1)(2^g+1) / 2^(g-1)(2^g-1)."""
    for g in (1, 2, 3):
        total, even, odd = laboratory.arf_enumeration(g)
        assert total == 1 << (2 * g)
        assert even == (1 << (g - 1)) * ((1 << g) + 1)
        assert odd == (1 << (g - 1)) * ((1 << g) - 1)
    _, even3, odd3 = laboratory.arf_enumeration(3)
    assert (even3, odd3) == (36, 28)


def test_termination_formula_e4():
    cases = ((48, 48, 1, 1, 48), (96, 96, 1, 1, 96), (24, 36, 3, 5, 72),
             (7, 14, 1, 1, 14), (12, 12, 4, 6, 6), (384, 384, 1, 1, 384))
    for W, H, a, b, expected in cases:
        tstar = math.lcm(W // math.gcd(a, W), H // math.gcd(b, H))
        assert tstar == expected, (W, H, a, b)


def test_termination_via_explicit_walk():
    """The step (a, b) on the W x H torus returns to the origin exactly
    after t* steps — verified by an explicit walk."""
    for W, H, a, b in ((48, 48, 1, 1), (24, 36, 3, 5)):
        tstar = math.lcm(W // math.gcd(a, W), H // math.gcd(b, H))
        x = y = 0
        for _ in range(tstar):
            x = (x + a) % W
            y = (y + b) % H
        assert (x, y) == (0, 0)
        # and not earlier: t*/2 steps must NOT return for these cases
        x = y = 0
        for _ in range(tstar // 2):
            x = (x + a) % W
            y = (y + b) % H
        assert (x, y) != (0, 0)


# ────────────────────────────────────────────────────────────────────
# Presentation and infra
# ────────────────────────────────────────────────────────────────────

def test_banner_present():
    lowered = laboratory.BANNER.lower()
    assert 'dynamic principle' in lowered
    assert len(laboratory.BANNER.strip()) > 40


def test_both_language_dictionaries_complete():
    for lang in ('ru', 'en'):
        assert laboratory.L[lang]['menu'], lang
        assert laboratory.L[lang]['pass'] and laboratory.L[lang]['fail']


def test_version_present():
    assert laboratory.__version__


def test_baseline_crosscheck_passes():
    assert laboratory.check_baseline(
        str(REPO / 'results' / 'baseline_v1_v9.json')) is True


def test_int_rank_matches_fractions_reference():
    """_int_rank must agree with a straightforward Fraction RREF."""
    from laboratory import _int_rank

    def naive_rank(M):
        A = [[Fraction(x) for x in row] for row in M]
        m, n = len(A), len(A[0])
        rank, row = 0, 0
        for col in range(n):
            piv = next((r for r in range(row, m) if A[r][col] != 0), None)
            if piv is None:
                continue
            A[row], A[piv] = A[piv], A[row]
            pv = A[row][col]
            for r in range(m):
                if r != row and A[r][col] != 0:
                    f = A[r][col] / pv
                    A[r] = [a_ - f * b_ for a_, b_ in
                            zip(A[r], A[row], strict=True)]
            row += 1
            rank += 1
        return rank

    M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]          # rank 2
    assert _int_rank(M) == naive_rank(M) == 2
    M2 = [[2, 0], [0, 8], [4, 16]]                  # rank 2
    assert _int_rank(M2) == naive_rank(M2) == 2


# ────────────────────────────────────────────────────────────────────
# Regressions of v1.1.1
# ────────────────────────────────────────────────────────────────────

def test_ask_pair_survives_garbage_input(monkeypatch):
    """Regression: malformed designer input used to raise ValueError and
    crash the whole interactive menu."""
    monkeypatch.setattr('builtins.input', lambda _p: 'xy zw')
    assert laboratory.ask_pair('pair: ', (1, 1)) == (1, 1)
    monkeypatch.setattr('builtins.input', lambda _p: '15  7')
    assert laboratory.ask_pair('pair: ', (1, 1)) == (15, 7)
    monkeypatch.setattr('builtins.input', lambda _p: '')
    assert laboratory.ask_pair('pair: ', (4, 8)) == (4, 8)
    monkeypatch.setattr('builtins.input', lambda _p: '1 2 3')
    assert laboratory.ask_pair('pair: ', (1, 1)) == (1, 1)


def test_ask_int_reports_actual_range(monkeypatch):
    """Regression: the error message printed the fixed 20..120 range for
    every prompt instead of the prompt's own range."""
    seen = {}
    monkeypatch.setattr(laboratory, 'LANG', 'en')
    monkeypatch.setattr('builtins.input', lambda _p: '999')
    monkeypatch.setattr(
        'builtins.print',
        lambda *a, **k: seen.setdefault('msg', ' '.join(str(x) for x in a)))
    assert laboratory.ask_int('N [4..64]: ', 4, 64, 15) == 15
    assert 'from 4 to 64' in seen.get('msg', '')


def test_multilingual_runner_reports_failing_backend(tmp_path, monkeypatch):
    """Regression: a backend that exits non-zero must be reported as a
    failure and flip the verdict (it used to be printed as PASS)."""
    bad = tmp_path / 'bad_backend.py'
    bad.write_text('import sys\nprint("FAIL")\nsys.exit(1)\n', encoding='utf-8')
    fake = [('Fake', sys.executable, str(bad), [], [], 'run')]
    monkeypatch.setattr(laboratory, 'BACKENDS', fake)
    assert laboratory.run_multilingual() is False


def test_multilingual_runner_accepts_passing_backend(tmp_path, monkeypatch):
    good = tmp_path / 'good_backend.py'
    good.write_text('import sys\nprint("PASS")\nsys.exit(0)\n', encoding='utf-8')
    fake = [('Fake', sys.executable, str(good), [], [], 'run')]
    monkeypatch.setattr(laboratory, 'BACKENDS', fake)
    assert laboratory.run_multilingual() is True


def test_lean_panel_g2_arf_count_matches_formula():
    """Regression: the Lean panel verified 2^0*(2^2+1)=5 for g=2 while
    the closed formula and every other stack give 2^1*(2^2+1)=10."""
    lean = (REPO / 'verification' / 'lean' /
            'HodgeLaboratory.lean').read_text(encoding='utf-8')
    assert '2^1 * (2^2 + 1) = 10' in lean
    assert '2^0 * (2^2 + 1)' not in lean


def test_lean_panel_g1_arf_count_matches_formula():
    """Regression (v1.1.2): the Lean panel asserted 2^1*(2^1+1)=3 for g=1,
    a false proposition (2*3=6) that the kernel would reject; the closed
    formula gives 2^0*(2^1+1)=3."""
    lean = (REPO / 'verification' / 'lean' /
            'HodgeLaboratory.lean').read_text(encoding='utf-8')
    assert '2^0 * (2^1 + 1) = 3' in lean
    assert '2^1 * (2^1 + 1)' not in lean


# ────────────────────────────────────────────────────────────────────
# Roadmap v1.2 — radical closed forms for b_Ch(15) and b_Ch(30)
# ────────────────────────────────────────────────────────────────────

def test_bch_closed_forms_match_numeric():
    """The radicals (7−√5−√(30−6√5))/8 and (9−√5−√(30+6√5))/8 must
    reproduce 1 − cos(2π/n) at the working precision."""
    for n in (15, 30):
        closed = laboratory.bch_closed(n)
        numeric = laboratory.bch_numeric(n)
        assert laboratory.rel_err(closed, numeric) < 1e-30, n


def test_bch_exact_layer():
    """Pure-integer certificate: the radical satisfies its minimal
    quartic EXACTLY in Z[√5][√D], and the quartic is irreducible
    over GF(2) — so the radical is a true conjugate 2cos(2πk/n)."""
    for n in (15, 30):
        assert laboratory._bch_exact_residual(n) == ((0, 0), (0, 0)), n
        assert laboratory._bch_minpoly_irreducible(n) is True, n
        assert laboratory.bch_exact_layer(n) is True, n


def test_bch_minimal_polynomials_known():
    """The quartics pinned by the conjugate sums: N=15 →
    x⁴−x³−4x²+4x+1, N=30 → x⁴+x³−4x²−4x+1 (regression guard against
    accidental spec edits)."""
    assert laboratory.BCH_RADICALS[15]['poly'] == (1, -1, -4, 4, 1)
    assert laboratory.BCH_RADICALS[30]['poly'] == (1, 1, -4, -4, 1)


def test_bch_closed_rejects_other_levels():
    with pytest.raises(ValueError):
        laboratory.bch_closed(7)
    assert laboratory.bch_exact_layer(7) is False


def test_bch_radical_strings_present():
    assert '√5' in laboratory.BCH_RADICALS[15]['bch']
    assert '√5' in laboratory.BCH_RADICALS[30]['bch']
    assert '30' in laboratory.BCH_RADICALS[15]['bch']


# ────────────────────────────────────────────────────────────────────
# Roadmap v1.4 — batch experiment mode
# ────────────────────────────────────────────────────────────────────

def _write_scenario(tmp_path: Path, runs, **extra) -> str:
    scen = {'scenario': 'pytest', **extra, 'runs': runs}
    p = tmp_path / 'scenario.json'
    p.write_text(json.dumps(scen), encoding='utf-8')
    return str(p)


def test_batch_mode_all_pass(tmp_path):
    scen = _write_scenario(tmp_path, [
        {'type': 'period', 'N': 15, 'a': 2, 'b': 3, 'r': 0, 's': 1},
        {'type': 'census', 'N': 15},
        {'type': 'cm', 'd': 7},
        {'type': 'flow', 'W': 48, 'H': 48, 'a': 1, 'b': 1,
         'expected_t': 48},
        {'type': 'bch', 'n': 15},
        {'type': 'bch', 'n': 30},
        {'type': 'omega', 'N': 30, 'a': 1, 'b': 1},
    ])
    out = tmp_path / 'batch_report.json'
    assert laboratory.run_batch(scen, str(out), verbose=False) is True
    rep = json.loads(out.read_text(encoding='utf-8'))
    assert rep['verdict'] == 'ALL PASS'
    assert rep['summary'] == {'total': 7, 'passed': 7, 'failed': 0}
    assert all(r['pass'] for r in rep['runs'])


def test_batch_mode_bch_run_carries_the_radical(tmp_path):
    scen = _write_scenario(tmp_path, [{'type': 'bch', 'n': 15}])
    out = tmp_path / 'batch_report.json'
    laboratory.run_batch(scen, str(out), verbose=False)
    rep = json.loads(out.read_text(encoding='utf-8'))
    data = rep['runs'][0]['data']
    assert data['exact_layer'] is True
    assert '√5' in data['radical']
    assert data['rel'] < 1e-25


def test_batch_mode_failure_flips_verdict_and_exit(tmp_path):
    scen = _write_scenario(tmp_path, [
        {'type': 'period', 'N': 15, 'a': 1, 'b': 1, 'tolerance': 0.0},
        {'type': 'flow', 'W': 48, 'H': 48, 'a': 1, 'b': 1,
         'expected_t': 7},
    ])
    out = tmp_path / 'batch_report.json'
    assert laboratory.run_batch(scen, str(out), verbose=False) is False
    rep = json.loads(out.read_text(encoding='utf-8'))
    assert rep['verdict'] == 'FAIL'
    assert rep['summary']['failed'] == 2


def test_batch_mode_crash_hardened(tmp_path):
    """Malformed single runs are recorded as failures, never raised;
    a malformed scenario FILE raises ValueError (exit code 2 in CLI)."""
    scen = _write_scenario(tmp_path, [
        {'type': 'nope'},
        'not-an-object',
        {'type': 'period', 'N': 3},          # violates 4≤N≤64
        {'type': 'census', 'N': 'abc'},      # int() inside the runner
    ])
    out = tmp_path / 'batch_report.json'
    assert laboratory.run_batch(scen, str(out), verbose=False) is False
    rep = json.loads(out.read_text(encoding='utf-8'))
    assert rep['summary']['failed'] == 4
    assert 'unknown run type' in rep['runs'][0]['data']['error']

    broken = tmp_path / 'broken.json'
    broken.write_text('{not json', encoding='utf-8')
    with pytest.raises(ValueError):
        laboratory.run_batch(str(broken), str(tmp_path / 'o.json'),
                             verbose=False)

    empty = tmp_path / 'empty.json'
    empty.write_text('{"runs": []}', encoding='utf-8')
    with pytest.raises(ValueError):
        laboratory.run_batch(str(empty), str(tmp_path / 'o.json'),
                             verbose=False)

    bad_dps = _write_scenario(tmp_path, [{'type': 'cm', 'd': 7}],
                              dps=999)
    with pytest.raises(ValueError):
        laboratory.run_batch(bad_dps, str(tmp_path / 'o.json'),
                             verbose=False)


def test_batch_mode_honours_scenario_dps(tmp_path):
    scen = _write_scenario(tmp_path, [{'type': 'bch', 'n': 15}], dps=40)
    out = tmp_path / 'batch_report.json'
    old = laboratory.mp.dps
    try:
        laboratory.run_batch(scen, str(out), verbose=False)
        assert int(laboratory.mp.dps) == 40
        rep = json.loads(out.read_text(encoding='utf-8'))
        assert rep['meta']['dps'] == 40
    finally:
        laboratory.mp.dps = old
