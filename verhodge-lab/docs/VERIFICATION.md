# Verification layer — what is computed and how

The discipline (inherited from hodge-laboratory): every stand is a
TWO-SCHEME construction.  Scheme A and scheme B must agree exactly
on the discrete layer and to a stated threshold on the numeric
layer.  Any disagreement is a falsification event recorded in
`counterexamples/`.

## The scheme map

| stand | scheme A | scheme B | threshold |
|-------|----------|----------|-----------|
| census (V1) | direct gcd enumeration | Moebius inversion over each conductor d | exact, N in [3,64] |
| exact layer | the collapse in Z[zeta]/(Phi_n) | the polynomial vanishes at 2cos(2pi/n) at 40 dps | < 1e-25 |
| certificate K | the exact eta_j in Z[zeta_11, zeta_5] | the branch reconstruction of 2cos(2pi/11) | < 1e-30 |
| certificate H | the SNF of the trace-form Gram (Ramanujan sums) | the product = disc = 1125^2 = 3^4 5^6 | exact |
| K3 | the SNF/rank over Q | the Sylvester sign counts (numerical-exact bridging) | exact + gap check |
| Gross | the Gamma-product at 120 dps | the integer round-off against the SNF sqrt | < 1e-60 |
| peel recursion | the closed recursion | the symmetry sum rule sum_j y_j = P + 5 psi Pi | exact |
| periods | the exact-rational PF series | mpmath hypergeometric | < 1e-38 |
| point counts | meet-in-the-middle | the literal O(p^4) loop + Weil bounds | exact / bound |

## The protocol runs

`python -m verhodge.cli` executes V1, V13, K, V16, V17, V18, V19,
V20, V21, V22 and writes `results/baseline_v15_v18.json` with the final
verdict.  The run is the release gate: ALL CHECKS PASSED or the
failing run is named.

## What is deliberately NOT claimed

- no mod-p derivation of the Picard-Fuchs operator is shipped
  (the classical operator is documented and verified against the
  certified series; the derivation is the v1.9 item, C-012);
- no general-N exponent rule for the Gross product (C-014);
- no polynomial-time claims beyond Level 0 (C-015);
- the psi = 1 value is recorded with a computed PSLQ-negative:
  it is not a Gamma-sine monomial (C-013).

## V22 — the Picard–Fuchs operator stand (v1.9)

- target certification: the ψ-form of the classical operator with the
  structural (ψ⁵−1) denominator, certified three ways in code
  (series-recurrence identity n ≤ 30; exact Laurent algebra;
  ~1e-61 residual on the mpmath hypergeometric period)
- NE05: the v1.8 Laurent target refuted (computed residuals)
- reduction machinery: two independent engines (the v1.9
  representation chain over F_p/Q; the v1.8 peel closure), agreeing
  on the 48-point mod-p grid (p = 101, 191, 281; 16 ψ-points each)
  and on the 24-test battery (S5 values, sum rules, closed
  Jacobian identities, char-0 exactness)
- singular fibers: the reduction degenerates at all tested ψ⁵ = 1
- honest open item: the engine operator does not yet match the
  certified operator — the divergence step misses the residue class
  of d(ι_R ξ) (the Cartan primitive has homogeneity −1 and does not
  descend to P⁴); registered as C-016/C-017 with the computed
  difference data (verification/V22_pf_operator.json)


## V23 — the PF derivation closure (v1.10)

Command: `python -m verhodge` (the `pf_closure_v110` stand).
Artifact: `verification/V23_gauge_closure.json`.

| component | what is verified | verdict |
|-----------|------------------|---------|
| gauge_identity | `gauge_psi(L_c) == L_true` in exact Laurent-operator algebra (char 0), both directions (the reverse recursion `a_m = b_m + (m+1) psi^-1 b_(m+1)` recovers L_c) | exact |
| descent_certificate | the residue class of `d(iota_R xi)|_(P^4\X)` computed at psi_0 = 2, 3: the master form identity `P^5 d(eta_C) = [P Div(C) - 4 sum C_j j_j] vol`, the Cartan identity `P^5 d(iota_R eta_C) = -iota_R(P^5 d(eta_C))`, the homogeneity bookkeeping (numerators of degree 17) — `iota_R eta_C` is basic and descends; the class is TRIVIAL | exact |
| raw_period_residual | the derived operator annihilates the raw period `g = f/psi` (the certified period independently evaluated): relative residual ~1e-71 | < 1e-25 |
| modp_closed_loop | engine gamma values + the gauge recursion == the certified target's specializations, EXACTLY, at every (p, psi_0), p = 101/191/281, both engines | 72/72 |
| singular_fibers | the engines degenerate exactly at psi^5 = 1; the gauge comparison is undefined there (the structural poles) | coherent |

Verdict: the mod-p Griffiths-Dwork derivation of the classical
Picard-Fuchs operator of the Dwork pencil is COMPLETE (C-012
closed; C-017 resolved as a computed negative; C-018 the gauge
theorem, computed).

## V24 — the Dwork family at every Calabi-Yau degree (v1.11)

The stand `dwork_family_v111` (verhodge/dwork_family.py) generalizes
the full mod-p Picard-Fuchs derivation to d = 3, 4, 5.  Five
certification layers per degree: (1) the exact series annihilation
(termwise, n <= 31); (2) the exact two-directional gauge identity
L_true(psi g) = psi L_c(g) in the Laurent-operator algebra; (3) the
char-0 closed loop over Q; (4) the mod-p closed loop on
degree-adapted grids (p = 1 mod d: 103/109/193 for d = 3,
101/281/401 for d = 4, 101/191/281 for d = 5); (5) the
hypergeometric seals at ~1e-92.  The d = 5 branch reproduces the
dedicated v1.9/v1.10 quintic operator exactly (regression).
Artifacts: verification/V24_dwork_family.json; claims C-019 (open,
the tube stamp with the computed chart identity) and C-020 (the
general-degree gauge theorem); counterexample NE06 (the
homogeneous-Euler trap).  The honest ledger row V24b registers the
tube-program status and the v1.12 plan.
