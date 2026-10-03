# Changelog

## v1.11.0 — the Dwork family at every Calabi-Yau degree + the tube-program register

### the mod-p Picard-Fuchs derivation generalized to d = 3, 4, 5 (C-020, V24)
- the headline result: the v1.9/v1.10 derivation machinery (the
  representation-system class reduction + the Krylov closure + the
  psi-gauge) now runs at EVERY Calabi-Yau degree of the Dwork
  construction — d = 3 (cubic in P^2, elliptic curves, PF order 2),
  d = 4 (quartic in P^3, K3 surfaces, PF order 3), d = 5 (the
  quintic, PF order 4) — verhodge/dwork_family.py, protocol stand
  V24
- the certified classical operators, converted EXACTLY (Laurent
  algebra, no numerics) from theta_z^{d-1} - z prod(theta_z + j/d),
  z = psi^{-d}, with the STRUCTURAL (psi^d - 1) leading coefficient
  and the psi^-1..psi^{-(d-1)} gauge shadow:
    d=3: (psi^3-1) f'' + (psi^2 + 2psi^-1) f' - 2psi^-2 f = 0
    d=4: (psi^4-1) f''' + (3psi^3 + 3psi^-1) f'' + (psi^2 - 6psi^-2) f'
         + 6psi^-3 f = 0
    d=5: the v1.10 certified operator, reproduced EXACTLY
         (regression: the general machinery == the dedicated
         quintic pipeline at every specialization)
- five certification layers per degree, all green: the exact
  series annihilation (n <= 31, rational arithmetic), the exact
  two-directional gauge identity L_true(psi g) = psi L_c(g), the
  char-0 closed loop over Q, the mod-p closed loop on
  degree-adapted grids (p = 1 mod d: 103/109/193 for d = 3,
  101/281/401 for d = 4, 101/191/281 for d = 5), and the
  hypergeometric numerical seals at ~1e-92
- the general-d class-reduction theorem: the char-[e_j] ansatz is
  exact at every degree (both monomial parts of the Jacobian
  generator j_j = d x_j^{d-1} - d psi Pi_hat_j share the character
  -[e_j] in (Z/d)^*/(Z/d)(1,..,1)); the Krylov bridge gains the
  minus sign a_{m-1} = -(psi^d - 1) d(d-1) Omega_m prod_{k=m}^{d-2} dk
  (L_c(h) = 0, not h^{(d-1)} = companion)

### the tube-program register (C-019 OPEN, computed evidence; NE06)
- the undelivered half of the v1.11 directive (the tube-integral
  identification f = psi<omega_1> as an independent normalization
  stamp) is REGISTERED with precise computed evidence: the exact
  chart identity
    Q^3 d(iota_R Omega'/Q^2) = (4Q + 2 sum_j x_j dQ_j) dx^4
  (verified by polynomial form algebra) shows the chart class
  [eta|chart] = 0 — the naive affine period formula
  dx1 dx2 dx3/(dQ_4) computes ZERO on chart-contained cycles, so
  the honest tube stamp needs the Cech/twist across chart
  boundaries (the level-set tube over the real projective slice;
  the v1.12 plan is in the ledger)
- near-miss NE06 (computed): the homogeneous-Euler trap — the cone
  constant structure (n + 2 deg) does NOT transport to the chart
  because Q is inhomogeneous there (sum x_j Q_j = 5(Q-1), not 5Q);
  every Euler-type constant must be recomputed after an affine
  pullback


## v1.10.0 — the PF derivation closure: the psi-gauge theorem + the descent certificate

### the mod-p Picard-Fuchs derivation is COMPLETE (C-012 closed, V23)
- the headline result: the v1.9 derivation engines (the
  representation chain and the peel closure) + the v1.10 psi-gauge
  reproduce the CLASSICAL operator theta_w^4 -
  w prod(theta_w+i/5) EXACTLY, at every (p, psi_0) of the mod-p
  grid (p = 101, 191, 281), both engines: the closed loop is
  72/72 green (verhodge/gauge.py, protocol stand V23)
- THE GAUGE THEOREM (C-018, computed): the engines' operator
    L_c = (psi^5-1) D^4 + 10 psi^4 D^3 + 25 psi^3 D^2
          + 15 psi^2 D + psi
  is the TRUE PF equation of the RAW invariant period
  g = <omega_1, gamma>, omega_1 = [dx/P]; the certified
  fundamental period f is the NORMALIZED period f = psi*g (the
  period of the class [psi dx/P]); the exact identity
    L_true(psi g) = psi L_c(g),
  with the triangular recursion b_4 = a_4,
  b_m = a_m - (m+1) b_(m+1)/psi, carries L_c term-by-term onto
  the certified target: b_3 = 6psi^4+4psi^-1, b_2 = 7psi^3-12psi^-2,
  b_1 = psi^2+24psi^-3, b_0 = -24psi^-4 — the "missing"
  psi^-1..psi^-4 structure is the GAUGE SHADOW of the (psi^5-1)
  leading coefficient (computed, exact Laurent-operator algebra,
  verified in both directions)
- numerical seal: L_c annihilates the raw period g = f/psi with
  relative residual ~1.6e-71 / 5.7e-72 at psi = 2, 3 (the period
  independently evaluated by mpmath's hypergeometric)
- THE DESCENT CERTIFICATE (C-017 RESOLVED, computed negative): the
  registered v1.9 conjecture attributed the operator mismatch to
  the residue class of d(iota_R xi)|_(P^4\X).  That class is now
  COMPUTED by exact C^5 form algebra (at psi_0 = 2, 3, char 0):
  the master divergence step is verified as a FORM identity
    P^5 d(eta_C) = [P Div(C) - 4 sum_j C_j j_j] vol
  (the unsigned divergence is exactly the vol-projection of an
  exact form), the Cartan identity
    P^5 d(iota_R eta_C) = - iota_R(P^5 d(eta_C))
  holds exactly, and every numerator of iota_R eta_C has degree 17
  (form degree 3, pole P^4: 17+3-20 = 0) — iota_R eta_C is BASIC
  (horizontal, homogeneity 0) and DESCENDS to P^4, so
  d(iota_R eta_C)|_(P^4\X) is exact: the residue class is TRIVIAL
  and the divergence step loses nothing.  The v1.9 root-cause
  story ("homogeneity -1, does not descend") was an arithmetic
  slip (16+4 = 20, not 16+3); the honest ledger corrects it
- the singular fibers psi^5 = 1 degenerate coherently on all
  three layers (the representation solve, the gauge comparison,
  the certified structural poles)
- protocol: V23_pf_closure_v110 added (the closure stand) +
  V22b updated to the RESOLVED state; artifacts
  verification/V22_pf_operator.json, V23_gauge_closure.json;
  registry: C-012 computed/closed, C-017 resolved (computed
  negative), C-018 added (the gauge theorem); ledger: +3 rows
  (gauge_psi, descent_certificate, the V23 grid)

## v1.9.0 — the class-reduction machinery + the certified operator target

### v1.9 — the Picard-Fuchs stand rebuilt (V22)
- the CERTIFIED target fixed and certified in code (the headline
  result): the classical operator theta_w^4 - w prod(theta_w+i/5)
  converts to the psi-form
    (psi^5-1) f'''' + (6psi^4+4psi^-1) f''' + (7psi^3-12psi^-2) f''
    + (psi^2+24psi^-3) f' - 24 psi^-4 f = 0,
  with the STRUCTURAL (psi^5-1) denominator (poles at the singular
  fibers) and the psi = 0 irregular pole (w = infinity); certified
  three ways in code: the series-recurrence identity (n <= 30,
  exact), the exact Laurent algebra of the Krylov normalization,
  and a ~1e-61 residual on the independently evaluated
  hypergeometric period
- the v1.8 Laurent comparison target REFUTED and removed
  (near-miss NE05, computed): it had no singular poles at all and
  does not annihilate the certified period; the whole v1.8
  "derivation mismatch" was measured against this wrong target
- the class-reduction machinery the user's program called for,
  built twice and cross-validated:
  * engine 1 (NEW, verhodge/gdreduced.py): the fresh
    Griffiths-Dwork chain — the generalized representation system
    A - lambda*Pi^(q-1) = sum_j C_j j_j (the char-[e_j] ansatz
    PROVED exact: the two monomial parts of j_j share the character
    -[e_j], so no cross-cancellation exists), the unique graded
    lambda, the unsigned-divergence step, the invariant projections
    (class-level exact by the isotypic directness), pole 5 -> 1;
    field-abstract: F_p AND Q (char-0 exact verification)
  * engine 2 (v1.8, retained): the peel closure over the verified
    Pi^4 representation solve
  * the two agree on the full 48-point mod-p grid (p = 101, 191,
    281) and on the 24-test algebraic battery: the S5-permutation
    values [y_i/P^2] = psi w2 + w1/5 (independent: pure algebra +
    sum rule + S5), the sum rules at every pole, the closed
    Jacobian identities ([x_i Pi^3 j_i/P^5] = w4), char-0 exactness
- the reduction degenerates EXACTLY at the singular fibers psi^5 = 1
  (computed at all 15 root points)
- honest open item, sharpened and registered (C-016/C-017): the
  operator implied by the engines,
    (psi^5-1) f'''' + 10 psi^4 f''' + 25 psi^3 f'' + 15 psi^2 f'
    + psi f = 0,
  does NOT annihilate the certified period (computed, O(1) residual
  vs ~1e-61); root cause registered as a falsifiable conjecture:
  the Griffiths divergence step k[sum C_j j_j/P^(k+1)] =
  [Div(C)/P^k] misses the residue class of d(iota_R xi) — the
  Cartan primitive has homogeneity -1 and does not descend to P^4,
  so the missing term is cohomologically alive and carries exactly
  the psi^-1..psi^-4 structure in which the two operators differ
  (the engine operator is regular at psi = 0 and therefore cannot
  be the Gauss-Manin operator).  Scheduled v1.10.

### Honesty ledger (v1.9 additions)
- NE05: the wrong-target near-miss (computed, with the residuals)
- claim C-012 sharpened: the target half CLOSED, the divergence-
  normalization half registered with the root-cause conjecture
- claims C-016 (the stand state) and C-017 (the conjecture) added

## v1.8.0 — the roadmap waves v1.5–v1.8 implemented

### v1.5-pre — Foundation
- claim registry `claims/registry.yaml` (15 claims, statuses, evidence)
- complexity ledger `complexity/ledger.yaml`
- near-miss corpus `counterexamples/` (NE01–NE04, computed)
- integer polynomial kernels `verhodge/poly.py` (exact Z[x] and GF(2)
  Rabin irreducibility, Bareiss determinant)

### v1.5 — Certificate K (the N=11 rung)
- the unified exact layer: minpoly of 2cos(2π/n) by the collapse
  algorithm in Z[ζ]/(Φ_n) for arbitrary n
- certificate K: census {11:45}, the quintic x⁵+x⁴−4x³−3x²+3x+1,
  Vieta (1,−4,−3,3,1), GF(2) irreducibility, the cyclic-quintic
  Lagrange-resolvent identity (η_j = R_j⁵ ∈ Z[ζ₅] computed exactly;
  compatible branches (2,4,4,1,1); reconstruction residual 1.8e−41)
- frozen-cubic regression (n = 7, 9): byte-identical

### v1.6 — The SNF engine + computed lattices
- Kannan–Bachem SNF with tracked unimodulars; canonical Bezout
  coefficients (the divisibility case yields v = 0 — the property
  that keeps the clearing passes pollution-free); the 2×2 gcd/lcm
  divisibility repair with a monotone exponent measure
- regression: 80/80 known-answer + round trip + true-diagonal
- certificate H computed: the trace-form Gram of Z[ζ₁₅] and Z[ζ₃₀]
  (Ramanujan sums) → SNF (1,1,5,5,15,15,15,15) BYTE-IDENTICAL to the
  frozen literal; disc = 3⁴·5⁶ = 1265625 = 1125²
- the K3 stand computed: rank 20, SNF 1¹⁸·8·8 (det 64), signature
  (1,19), family relation
- ζ₃₀ = −ζ₁₅⁸ verified exactly (Φ₃₀(−ζ₁₅⁸) = 0)

### v1.6+ — Gross normalization computed
- vol_h = 1125 at N=15 (residual 5.9e−118) with the certified rule
  c_k = 4 + 2·[3|k]
- the N=30 identity derived by the duplication/reflection sine count
  (odd pairs cancel, c₁₅ = 0 forced): vol_h = 1125 (residual 1.8e−116)

### v1.7 — Unified exact layer + HODGE-INPUT v1
- the parser: four levels, canonicalization, sha256 provenance,
  the asymmetric dispatch (level-3 → NOT_DETERMINED)
- five Level-0 JSON documents run end to end (V20)

### v1.8 — The Dwork pencil stand (the first Level-1 input)
- the invariant Griffiths–Dwork cohomology via the closed peel
  recursion; verified by the exact symmetry sum rule
  Σ_j y_j = P + 5ψΠ; b³_inv = 4, Hodge (1,1,1,1)
- certified periods: the exact-rational PF-recurrence series vs
  mpmath hypergeometric, agreement < 1e−38 on the ψ-grid
- the classical PF operator documented and verified against the
  certified series; the mod-p derivation registered as v1.9
- Fermat-fiber point counts: meet-in-the-middle vs the literal
  O(p⁴) loop (agree at p = 11), Weil bounds at p = 11, 31, 41
- the ψ=1 value recorded (1.0707258684...); PSLQ over the
  Γ-sine log lattice: NO monomial relation (computed negative)

### Honesty ledger
- the near-miss corpus records the shortcuts that DO NOT work
  (float integrality, naive SNF, census edge cases, singular fibers)
- claim C-014 (the general-N exponent rule) is a registered
  conjecture, NOT a computed claim
- claim C-015: no polynomial-time claims beyond Level 0

## v1.4 (hodge-laboratory) — the baseline this program extends
