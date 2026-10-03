# From Stands to Algorithms: A Formalization-First Roadmap for the Hodge Laboratory Program (v1.5–v1.8)

**Author:** Isaev Iskhak Khamzatovich · ORCID 0009-0003-7299-0701
**Repository:** [github.com/wild8highlander/hodge-laboratory](https://github.com/wild8highlander/hodge-laboratory)
**Companion project:** Chess Particle Dynamics (chess-dynamics-lab v2.2.0)
**Status:** plan of record for the 6-month horizon · October 2026 · v1.0

> This document is the roadmap referenced by the README (Section 17). It is versioned
> with the code; every version gate (v1.5, v1.6, v1.7, v1.8) cites it as the plan of
> record. A typeset PDF edition with appendices (full input schema, SNF pseudocode,
> Griffiths–Dwork sketch, detailed ledger, certificate map) accompanies the release.

---

## 1. Executive Summary

This roadmap responds to the scientific directive issued after the review of the
`hodge-laboratory` program (v1.4: twenty theorem monographs, certificates A–J,
protocol V1–V9, five-language verification, Lean 4 kernel). The reviewer's assessment
is adopted here as the founding statement of the next phase: **the program currently
constitutes a reproducible verification laboratory on fixed stands — not a
polynomial-time algorithm for the Hodge conjecture, and its connection to P vs NP is
at present only methodological, not mathematical.** The way forward consists of two
directives:

1. **Directive I (input formalization).** Define precisely how an arbitrary manifold
   and a Hodge class are presented to the laboratory as *input data*, so that the
   notion of "running the verification on X" is meaningful beyond the closed list of
   stands.
2. **Directive II (complexity).** For each input class the program accepts, prove or
   measure *explicit resource bounds* — ideally polynomial bounds in the bit length
   of the input — separating what is claimed from what is merely illustrated.

Both directives are implemented through five work packages:

| WP | Name | One-line goal | Gate |
|----|------|---------------|------|
| **WP1** | Input formalization | Grammar `HODGE-INPUT v1` for (variety, Hodge class) pairs, in four levels | v1.7 |
| **WP2** | Complexity ledger | Bit-complexity accounting per subroutine; target theorem for the Fermat family | v1.6–v1.8 |
| **WP3** | Stands | N=11 rung, computed SNF engine, computed Gross normalization, Dwork pencil | v1.5–v1.8 |
| **WP4** | Lean 4 | Machine-checked input grammar, SNF spec, two-scheme census agreement | v1.8 |
| **WP5** | Methodology transfer | Trilemma, falsification corpora, honest negatives, verdict ladder | continuous |

The organizing principle is deliberately conservative: **every claim must name its
input class, its output, and its resource bound.** This discipline is imported
wholesale from the companion project `chess-dynamics-lab`, whose complexity note N1
and "trilemma" (§8) already demonstrate how to state what a computational program
does and does not prove.

The headline mathematical content is the **target theorem for the Fermat family**
(§6): within the family of Fermat hypersurfaces — where the Hodge conjecture is a
theorem of Shioda — verifying that a given Hodge class is algebraic and producing an
explicit cycle certificate reduces to exact integer linear algebra on data the
laboratory already computes (the character census and the closed-form Γ-periods).
Consequently the verification admits a *polynomial-time* implementation in the input
size, with all three properties of the trilemma — polynomial, exact, explicit —
satisfied simultaneously. This is the first claim of the program that is
simultaneously (i) non-trivial, (ii) provable with current machinery, and
(iii) directly responsive to Directive II.

**By month 6 the program delivers:** the `HODGE-INPUT` parser and normalizer (WP1);
the computed Smith-normal-form engine replacing the hardcoded literal
`(1,1,5,5,15,15,15,15)` with a regression-locked implementation (WP3, v1.6); the
N=11 rung with certificate K (WP3, v1.5); a unified exact layer generating minimal
polynomials of `2cos(2π/n)` for arbitrary n (WP3, v1.7); the first Level-1 stand —
the Dwork pencil — with periods certified against high-precision quadrature
(WP3, v1.8); and a Lean 4 package formalizing the input grammar and the normal-form
specification (WP4).

**What this roadmap deliberately does *not* do:** it does not claim a polynomial-time
algorithm for the Hodge conjecture in general; it does not claim any consequence for
P vs NP; it does not reinterpret the chess branch as evidence about NP-hardness.
These exclusions are stated as falsifiable commitments (§4, Remark 4.5) and are
enforced by the verdict ladder (§9).

---

## 2. Where the Program Stands

### 2.1 The ladder of stands and what is computed on it

The `hodge-laboratory` program (v1.4) is organized as a ladder of **stands** — fixed
geometric objects on which a fixed verification conveyor is executed. The single-file
laboratory `laboratory.py` (≈ 2,600 lines) executes the full protocol V1–V9 in about
two seconds and is cross-verified in five languages plus a Lean 4 kernel that
machine-checks the integer identities without axioms.

| Stand | Input data | Key computed invariants |
|-------|-----------|-------------------------|
| Torus (calibration) | triple (4, 1, 4π²) | δ = π/4; Δ_Ch = 4π² + δ²/2 − δ⁵ = 39.4879953934… (float and mpmath, 40 dps); monotonicity of π/N family |
| K3 (Fermat quartic) | 48 lines + class h | exact ℚ-rank 20 of the 49×49 intersection matrix (maximum Picard number, Shioda); relation among line classes ∼ h |
| Klein quartic | constants c₄ = 105, Δ = −343 | j = −3375 = −15³ exact; identity Δj = c₄³; τ = (1+√−7)/2; period Ω ≈ 1.9333117… |
| N=7 (Hurwitz) | census(7) | genus 15; census {7:15}; Vieta triple (−1,−2,1) exact in ℤ[ζ₇]/(Φ₇); irreducibility over GF(2); Cardano form of b_Ch(7) |
| N=9 (Macbeth) | census(9) | genus 28; census {3:1, 9:27}; Vieta triple (0,−3,−1); b_Ch(9) |
| N=15/30 (flagship) | census(15/30) | genera 91/406; SNF (1,1,5,5,15,15,15,15) (**literal, not computed**); disc = 3⁴5⁶ = 1125²; vol_h = 1125 (cited); radicals of b_Ch in ℤ[√5][√(30∓6√5)] |
| Errata E8 | g = 1..3 | full enumeration of 2^{2g} quadratic forms; Arf invariant counts (enumeration as proof) |
| Binary code | 48×48 grid | flow (1,1): t\* = 48; reference sums 212/432/114, total 806 |

The verification protocol **V1–V9** consists of nine independently checkable stages:
census by two schemes (direct gcd counting and Möbius inversion, V1); closed-form
versus tanh-sinh quadrature with maximum deviation 3.9×10⁻³⁶ over 90 tests (V2) and
the exact phase law arg P = 2π(ra+sb)/N (V3); μ_N×μ_N-equivariance (V4); orbit-sum
vanishing with a positive control (V5); the reflection ladder
Γ(k/N)Γ(1−k/N) = π/sin(πk/N) at 7.0×10⁻³⁶ (V6); numerical rank of the period matrix
by SVD (V7); DFT-orthogonality (V8); and a deep-precision record at 70 dps with
residual 1.26×10⁻⁷¹ (V9). Every threshold exceeds the observed remainder by two to
three orders of magnitude, and any violation yields a `FAILURES PRESENT` verdict
with exit code 1.

### 2.2 What is proved, what is computed, what is cited

The program's own trichotomy is one of its strongest assets and is retained as an
audit standard.

- **Machine-proved** (Lean 4, `native_decide`, no axioms): the genus formula for
  Fermat curves, census sums including inclusion–exclusion through
  c(k) = (k−1)(k−2)/2, the SNF product, the Klein integers, Arf counts, and the
  termination time t\* = lcm(W/gcd(a,W), H/gcd(b,H)).
- **Exactly computed** (integer or rational arithmetic in Python/C/Rust): the K3 rank
  20 by fractional elimination, censuses, Vieta triples in ℤ[ζ_N]/(Φ_N), the
  j-invariant.
- **High-precision verified** (mpmath 35–70 dps, Julia BigFloat 240 bits):
  quadrature agreements V2, V6, V9.
- **Documented citations**: reference constants, the physical interpretation of
  certificates A–D, and — importantly for this roadmap — the SNF tuple, the
  signature and determinant of the K3 intersection matrix, and the Gross
  Γ-normalization vol_h = 1125.

> **Audit target.** Three quantities that the program *prints* are not yet
> *computed*: the Smith normal form of the N=15/30 period matrix (currently a
> literal), the determinant and signature of the K3 lattice (currently declared),
> and the Gross normalization (currently quoted to 10⁻¹¹⁹ in the monograph but not
> recomputed in code). Each becomes a computed quantity under WP3.

### 2.3 The input/output surface of the current code

An honest inventory of the generalization surface of `laboratory.py` shows that
parametric generality exists **only inside the Fermat family**. Fully general entry
points: `census(N)` and `census_mobius(N)` for arbitrary N with two independent
schemes; `omega_closed`, `period_closed` and `period_numeric` for arbitrary
(N, a, b, r, s) subject to the holomorphicity constraint 1 ≤ a, 1 ≤ b, a+b ≤ N−1;
the designer menu accepting N ∈ [4, 64]; a batch JSON mode with six run types; and a
CM-lattice sweep for d ≤ 100. Everything else is hard-coded: the torus triple, the
48 lines of the quartic with their combinatorial intersection rules, the Klein
constants 105/−343, the dictionaries `BCH_RADICALS` (levels 15/30 only) and
`CYC_CUBICS` (levels 7/9 only), and the SNF literal. Crucially, **there is no entity
in the code corresponding to "a manifold"**: no parser of defining equations, no
construction of a period matrix from an equation, no notion of an arbitrary Hodge
class as input. The reviewer's first directive targets precisely this gap.

### 2.4 The honest boundary

The program's FAQ already states that the repository is not a proof of the Hodge
conjecture and does not claim to be one. This roadmap sharpens that boundary into a
positive research program. The stands sit inside the *known-true zone* of the Hodge
conjecture: the Hodge conjecture holds for Fermat varieties by Shioda's theorem, the
Fermat quartic K3 surface attains the maximal Picard number ρ = 20
[Shioda–Katsura 1979], and the cyclotomic rungs N = 7/9/15/30 are exact-structure
cases. The gap is therefore not the truth of the conjecture on the stands but the
**form** in which the program consumes geometry: fixed objects with baked-in data
rather than a declarative input language with complexity-annotated algorithms.
Closing this form-gap is what §4–§7 do; the chess branch supplies the statement
discipline (§9).

---

## 3. The Directive, Formalized

### 3.1 Decision problem

> **Definition 3.1 (Verification instance).** A *verification instance* is a pair
> (D, α) where:
> - **D** is a finite *description* of a smooth complex projective variety X(D),
>   belonging to one of the accepted input classes C₀ ⊂ C₁ ⊂ C₂ ⊂ C₃ (§5.1);
> - **α** is a finite specification of a rational Hodge class, i.e. a ℚ-linear
>   combination of named basis elements of H^{2p}(X(D), ℚ) of the kind that the
>   input class exposes (characters, reduced forms, or curve classes).
>
> The *input size* |D, α| is the total bit length of the description in a fixed
> serialization (`HODGE-INPUT v1`, Appendix A).

> **Decision problem 3.2 (VER-HODGE(Cᵢ, p)).** Given an instance (D, α) with
> X(D) ∈ Cᵢ and α of coniveau p: either return an **ALGEBRAIC CERTIFICATE** — exact
> data representing an algebraic cycle Z on X(D) whose Hodge class equals α — or
> return **NOT-DETERMINED**; never return **NON-ALGEBRAIC** unless a proof of
> non-algebraicity is attached. The problem is *polynomial-time solvable* on Cᵢ if
> there is an algorithm whose total bit complexity is polynomial in |D, α|.

Three design choices encode the reviewer's caution into the problem statement itself:

1. **The output contract is asymmetric:** the program may abstain (NOT-DETERMINED)
   but may never assert non-algebraicity without proof, which keeps the laboratory on
   the safe side of an open problem.
2. **The certificate must be exact** — rational or integer data, not floating-point —
   so that the Lean layer (WP4) can check it without trusting numerics.
3. **The resource measure is the bit length of the serialized input**, not an
   abstract complexity parameter such as the degree alone; this is what makes the
   statements of §6 meaningful and checkable.

### 3.2 The statement discipline

Every mathematical or computational claim made by the program after this roadmap
must carry the triple **(input class, output, resource bound)**. The discipline is
imported from the chess branch, where it separates the mathematically proven
statement "generalized chess is EXPTIME-complete, hence no polynomial-time exact
solver exists" [Fraenkel–Lichtenstein 1981] from the empirically measured behavior
of the in-house polynomial solver. The Hodge laboratory adopts the same discipline
and adds a verdict ladder (§9) that grades every stand according to the strength of
its verification class.

> **Acceptance criterion 3.3 (Claim registry).** From v1.5 on, the repository
> maintains `claims/registry.yaml`, in which every claim of the README, the
> monographs, and the certificates is registered with its triple, its verification
> class (machine-proved, exactly computed, high-precision verified, documented), and
> its falsification test (a CI-run command whose failure invalidates the claim).
> A claim without a triple or a test is a documentation defect.

### 3.3 Work packages and falsification conditions

| WP | Directive | Deliverable | Falsified if |
|----|-----------|-------------|--------------|
| WP1 | I | `HODGE-INPUT v1` parser, normalizer, four levels | A valid instance of an accepted level cannot be executed end-to-end |
| WP2 | II | Complexity ledger; target theorem for C₀ | Any ledger entry lacks a bound or a measurement; the target theorem's linear-algebra reduction exceeds polynomial time on generated instances |
| WP3 | I+II | Stands v1.5–v1.8 (N=11, SNF engine, Gross normalization, Dwork pencil) | A new stand fails V1–V9 or disagrees with the frozen baseline |
| WP4 | I | Lean package: grammar, SNF spec, census agreement | Lean check fails on a valid instance or the grammar accepts malformed input |
| WP5 | discipline | Verdict ladder, claim registry, falsification corpora | A shipped claim lacks a registry entry or a test |

> **Remark 3.4 (Exclusions).** The following are excluded from the program's claims
> for the entire horizon of this roadmap: (i) any polynomial-time claim for
> VER-HODGE beyond the class C₀ of Fermat-type inputs; (ii) any statement connecting
> the Hodge laboratory to P vs NP beyond the methodological trilemma; (iii) any
> reinterpretation of the chess EXPTIME-completeness result as evidence about the
> Hodge conjecture. These exclusions are registered in the claim registry with
> `status: excluded`.

---

## 4. WP1 — Input Formalization

### 4.1 Levels of input generality

Input classes are organized as an increasing sequence of generality levels. Each
level must be **fully consumable**: a level is declared supported only when an
arbitrary instance of that level passes the protocol V1–V9 end-to-end, with all
certificates computed (not documented) and the complexity ledger populated for every
subroutine invoked.

- **Level 0 — Fermat-type parametric family (C₀).** Varieties: Fermat hypersurfaces
  X_{N,m} ⊂ ℙ^m given by the integer triple (N, m), together with their quotients
  relevant to the cyclotomic rungs. Hodge classes: characters of μ_N^{m+1}, i.e. the
  census list C_{N,m} = {(a₀,…,a_m) ∈ (ℤ/Nℤ)^{m+1} : aᵢ ≠ 0, a₀+⋯+a_m ≡ 0 (mod N)},
  expressed in the character basis. This level is already parametric in the code
  (`census`, `period_closed`); what is missing is the declarative wrapper and the
  cycle-certificate machinery.
- **Level 1 — Smooth hypersurfaces (C₁).** Varieties: X_f = {f = 0} ⊂ ℙⁿ with f a
  homogeneous polynomial over ℚ of degree d, smooth over ℂ. Hodge classes: rational
  combinations of reduced forms in the Griffiths residue description of
  F^{n−p}H^{n−p}, or cycles. The Dwork pencil is the flagship instance.
- **Level 2 — Plane curves and their Jacobians (C₂).** Varieties: smooth plane
  curves C : g(x, y) = 0 of degree d over ℚ, with the period matrix of Jac(C) as the
  central computed object. The Klein quartic is re-interpreted as a Level-2 instance
  whose invariants the program already reproduces exactly.
- **Level 3 — Complete intersections (C₃).** Design-only in this roadmap: varieties
  cut by several equations; the census formalism of Shioda–Katsura extends, but the
  period machinery is deferred.

### 4.2 The `HODGE-INPUT v1` grammar

Instances are serialized as JSON documents with three top-level blocks: `variety`
(kind + parameters or an explicit equation), `hodge_class` (basis name +
coefficients), and `verification` (protocol options, precision, certificate
requests). The `basis` field is the pivot of the design: it names the concrete
finite generating set in which the class is expressed — exactly the data the
certificate machinery consumes.

```json
{
  "schema": "hodge-input/1.0",
  "variety": { "kind": "fermat-hypersurface", "degree": 15, "ambient_dim": 5 },
  "hodge_class": {
    "codimension": 2,
    "basis": "census-characters",
    "coefficients": [ [1,2,3,4,5,0], "... others ... " ]
  },
  "verification": {
    "protocol": "V1-V9",
    "precision_dps": 40,
    "certificates": ["shioda-linear-spaces", "snf", "period-closure"],
    "exact_arithmetic": true
  }
}
```

The parser performs four normalizations before any mathematics happens, each
independently testable and Lean-checkable (WP4):

1. **Well-formedness** — schema validation with strict types;
2. **Coherence** — the coefficients must be dimension-consistent with the declared
   basis and codimension;
3. **Smoothing prechecks** — for levels 1–2, a square-free and Jacobian-rank
   screening of the defining equation over ℚ before any transcendental work is
   attempted;
4. **Canonicalization** — rational coefficients rewritten in lowest terms with
   positive denominators, the character list sorted, so that identical inputs
   produce bit-identical runs (the chess branch's reproducibility rule).

```
ALGORITHM: HODGE-INPUT v1 parser and normalizer
IN : JSON document J claiming schema "hodge-input/1.0"
OUT: canonical instance I = (D, α) or REJECT with reason

for each block B ∈ {variety, hodge_class, verification}:
    validate B against the schema; on failure return REJECT(B)
resolve the variety kind; attach the level tag ℓ ∈ {0,1,2,3}
if ℓ ≥ 1:
    f ← parse defining polynomial(s) over ℚ
    if f not square-free or Jacobian rank deficient over ℚ (screening):
        return REJECT(smoothing)
normalize all coefficients to lowest terms; sort characters; deduplicate
return canonical I with provenance hash h(I)
```

### 4.3 Closing the Level-0 gap

Level 0 is the level at which the reviewer's directive is answered with existing
machinery. Three items complete it:

1. **The declarative wrapper.** The (N, m) triple and the census characters become
   first-class input, replacing the menu-driven flow; the batch mode gains the run
   types `snf`, `rank`, and `cycle-certificate`.
2. **The cycle side.** For Fermat varieties the space of Hodge classes is generated
   by classes of linear subspaces [Shioda 1979; Ran 1980/81; Aoki 1989]; the program
   must therefore construct, for a given character combination α, the explicit
   incidence data of linear spaces on X_{N,m} and the integer matrix expressing the
   Shioda generators in the character basis.
3. **The certificate output.** ALGEBRAIC CERTIFICATE is emitted as a JSON document
   containing the cycle as a rational combination of linear spaces, the equality
   check in cohomology, and the provenance hash — a document the Lean layer can
   audit.

### 4.4 Level 1: from equations to periods

For smooth hypersurfaces the period matrix is no longer available in closed form,
and the pipeline follows the Griffiths–Dwork theory: the Hodge filtration is
computed by reducing rational n-forms modulo the Jacobian ideal; Picard–Fuchs
equations of one-parameter families (the Dwork pencil) are derived by creative
telescoping; periods are obtained by certified numerical integration of the
Picard–Fuchs system. The algorithmic foundation exists in the literature with
complexity statements: Lairez gives a deterministic algorithm computing periods of
rational integrals of hypersurfaces to certified precision, with polynomial bit
complexity in fixed dimension [Lairez 2016]; the Dwork pencil periods admit
hypergeometric closed forms in the Calabi–Yau literature [Candelas et al. 1991;
Cox–Katz 1999]; and the point-counting analogue (Dwork cohomology) is the basis of
the Lauder–Wan machinery [Lauder 2004].

The v1.8 stand restricts the first Level-1 input to the Dwork pencil
ψ: x₀⁵ + ⋯ + x₄⁵ − 5ψ·x₀x₁x₂x₃x₄ = 0 in ℙ⁴, because its periods are
cross-checkable against both the hypergeometric closed forms and the existing
Γ-formula machinery at the Fermat point ψ = 1.

> **Acceptance criterion 4.1 (Level-1).** The v1.8 stand accepts any rational
> ψ ≠ μ₅-specialization of the Dwork pencil, computes the five Picard–Fuchs periods
> to d significant digits in Õ(d^c) time with certified error < 10⁻ᵈ, agrees with
> the hypergeometric evaluation to that precision, and emits an EXACT-CONSISTENT
> verdict when the numerically recognized monodromy-invariant quantities match their
> LLL-recognized algebraic values over ℚ.

### 4.5 Level 2: curves

Plane curves enter with the Klein quartic as the anchor instance: the program
already reproduces its j-invariant, CM point τ = (1+√−7)/2, and period
Ω ≈ 1.9333117… from the stand constants. The Level-2 task is to **rederive** these
quantities from the curve equation x³y + y³z + z³x = 0 through the general pipeline
(period-matrix computation, certified integration, algebraic-number recognition by
LLL [LLL 1982]), thereby demonstrating that the general machinery recovers the
special-case values. The complexity ledger for Level 2 leans on the
Monsky–Washnitzer / Kedlaya tradition for the p-adic side [Kedlaya 2001] and on the
exact-modular-forms program of Edixhoven–Couveignes [2011] for the architectural
pattern of "certified numerical + exactly lifted" computation.

### 4.6 A worked Level-0 walk-through

To make the input-first workflow concrete, consider the Hurwitz rung as a
`HODGE-INPUT` document. The instance declares `variety.kind =
"fermat-hypersurface"`, `degree = 7`, `ambient_dim = 2` (the Fermat plane curve of
degree seven), and a Hodge class of codimension 1 in the character basis.
Execution proceeds exactly as the current stand does, but every step is now
attributable to an input field rather than to baked-in code:

1. **Normalization.** The parser validates the schema, canonicalizes coefficients,
   and computes the provenance hash. The level tag ℓ = 0 resolves the conveyor:
   census first, closed-form periods second, exact layer third.
2. **Census.** `census(7)` and `census_mobius(7)` agree: h₇ = 15 with profile
   {7:15}, genus 15. The two-scheme agreement is the V1 gate; a disagreement would
   abort with REJECT at the coherence stage of the pipeline.
3. **Periods.** For the declared characters (a, b) with a + b = 7, the closed form
   P(r,s) = ⅐·ζ₇^{ra+sb}·Γ(a/7)Γ(b/7)/Γ(1) is evaluated; the tanh-sinh layer
   (V2/V3) verifies the phase law to 10⁻³⁶-class residuals.
4. **Exact layer.** The braking constant b_Ch(7) = 1 − cos(2π/7) is recognized by
   its minimal polynomial over the real subfield, the Vieta triple (−1,−2,1) is
   certified in ℤ[ζ₇]/(Φ₇), and irreducibility over GF(2) is established — the I/J
   certificate pattern, now emitted as a machine-checkable certificate document.
5. **Verdict.** The certificate bundle (census agreement, period closure, exact
   layer, provenance hash) is returned with verdict class FULL; the claim registry
   records the run against the baseline key.

The same document template, with `degree = 15` and `ambient_dim = 5`, reproduces
the flagship run including the SNF branch once the v1.6 engine lands — which is
precisely the sense in which "the stand" becomes an instance of "the input class".
No per-stand code is touched; the ladder becomes data.

### 4.7 Normalization invariants and cross-level checks

Three invariants make the input layer trustworthy enough to build certificates on:

- **Canonicalization idempotence.** Normalizing an already-normalized document is
  the identity, and identical mathematical inputs presented with cosmetic
  differences (key order, whitespace, equivalent fractions) hash identically — the
  property that makes regression baselines meaningful across refactors.
- **Level monotonicity.** Every Level-ℓ instance is a valid Level-(ℓ+1) instance in
  the coarsest admissible basis (a Fermat hypersurface is a smooth hypersurface; a
  smooth hypersurface is a complete-intersection degeneracy), so cross-level
  consistency checks — the Fermat point of the Dwork pencil against Level-0 closed
  forms (§7.5), the Klein quartic as a Level-2 curve against its Level-0 cousin
  data — are structurally well-posed rather than ad hoc.
- **Rejection totality.** For malformed or incoherent input, the pipeline must
  reject at the parser stage, never mid-protocol; this keeps the verification
  layers free of input-dependent branches and is the property the Lean grammar
  formalizes first (§8.1).

---

## 5. WP2 — Complexity Ledger

### 5.1 Method: measure the wall, then name it

The chess branch earned its complexity note N1 by *measuring* the wall before naming
it: the cost of exact solving was bounded from below by the size of the state space,
the certificate blow-up was measured as ~10^{0.91n} against the n⁶-sized table, and
the polynomial solver's losses were quantified (E1–E3). WP2 imports this method into
the Hodge laboratory: for every subroutine invoked on an input class, the ledger
records (input, output, known or measured bound, implementation status). The ledger
is a live artifact (`complexity/ledger.yaml`) regenerated by CI; the initial state
is given below and expanded in the PDF edition (Appendix D).

| Subroutine | Input → output | Bound | Status (v1.4) |
|------------|----------------|-------|----------------|
| Census enumeration | N → C_{N,m} (all characters) | output-sensitive O(\|C_{N,m}\|) | computed, 2 schemes |
| Möbius cross-check | N → census sums | O(poly(N)) | computed |
| Γ-period (closed form) | (N, a, b) → Ω_{a,b} | O(1) formula + precision d: Õ(d) | computed |
| tanh-sinh verification | entries, d → residual | Õ(d) per entry | computed, 35–70 dps |
| Exact ℚ-rank | matrix → rank | polynomial (fraction-free) | computed (`_int_rank`) |
| Smith normal form | A ∈ ℤ^{r×s} | poly [Kannan–Bachem 1979; Storjohann 1996] | **literal, not computed** |
| LLL reduction | lattice basis | poly [LLL 1982] | documented (cert. F) |
| Polynomial factorization over ℚ | f → factors | poly [LLL 1982] | partial |
| Arithmetic in ℤ[ζ_N]/(Φ_N) | elements → sum/product | poly in φ(N) | computed |
| Minimal polynomial of 2cos(2π/n) | n → polynomial | poly in φ(n) | hardcoded n ∈ {7,9,15,30} |
| Griffiths–Dwork reduction (Level 1) | f, forms → reduced | poly for fixed n [Lairez 2016] | absent |
| Picard–Fuchs coefficients | family → ODE | poly [Lairez 2016; Bostan et al. 2018] | absent |

### 5.2 The target theorem for the Fermat family

> **Fact 5.1 (Shioda; Ran; Aoki).** For the Fermat hypersurface X_{N,m} ⊂ ℙ^m, the
> space of Hodge classes B^p(X_{N,m}) is generated over ℚ by the cohomology classes
> of linear subspaces contained in X_{N,m}; in particular the Hodge conjecture holds
> for Fermat varieties [Shioda 1979; Ran 1980/81; Aoki 1989]. The intersection
> pairing on the span of linear spaces is explicitly computable from incidence data,
> and the character decomposition of the middle cohomology is governed by the census
> C_{N,m} [Shioda–Katsura 1979].

> **Target theorem 5.2 (Fermat-family verification, informal form).** There is an
> algorithm that, given (N, m) and a Hodge class α specified as a ℚ-combination of
> census characters of X_{N,m} (with coefficients given by integers of bit length
> b), decides VER-HODGE(C₀, p) correctly: it either returns an explicit algebraic
> cycle certificate — α written as a ℚ-combination of classes of linear subspaces,
> with the equality certified by exact incidence arithmetic — or reports
> NOT-DETERMINED when the character list provided does not span a Hodge-stable
> subspace. The total bit complexity is polynomial in |C_{N,m}| · b, and the
> certificate is exact (rational), explicit (it names the cycles), and
> machine-checkable.

> **Remark 5.3 (Why the trilemma resolves on Level 0).** The chess branch
> formulated the working trilemma: *polynomial, exact, explicit — choose two*, with
> the polynomial-but-inexact particle solver and the exact-but-exponential table
> base as the two measured horns. The Fermat family is the exceptional regime where
> the trilemma collapses to three satisfiable clauses, precisely because Shioda's
> theorem supplies the generators: exactness and explicitness are inherited from the
> incidence matrix, and polynomiality from exact linear algebra. This is the
> structural reason the roadmap concentrates the complexity claims on Level 0 rather
> than diluting them across levels.

**Proof plan (four steps, each mapped to a deliverable).**

- **(S1)** Formalize the character census and its Hodge-stable decomposition
  following [Shioda–Katsura 1979] — already computed for arbitrary N.
- **(S2)** Build the incidence matrix M of linear spaces versus character basis, an
  integer matrix whose entries are combinatorially explicit (counts of linear
  spaces with prescribed character profile).
- **(S3)** Solve Mz = c over ℚ with fraction-free elimination and compute the Smith
  normal form of M by [Kannan–Bachem 1979; Storjohann 1996] to certify the
  arithmetic lattice of the cycle space — the generalization of the exact rank-20
  computation already performed on the K3 stand.
- **(S4)** Emit the certificate and have Lean re-check the equality by exact
  rational arithmetic.

Polynomiality follows because every step is exact linear algebra on matrices of
size O(|C_{N,m}|).

### 5.3 The K3 prototype and concrete input sizes

The target theorem is not built on sand: its prototype is already computed and
frozen. On the K3 stand, the program receives 48 lines and the class h, builds the
49×49 intersection matrix over ℚ with exact fractional arithmetic, and eliminates —
obtaining the exact rank 20, the maximal Picard number of the Fermat quartic
[Shioda–Katsura 1979]. This is exactly the S2–S3 pattern of the proof plan
(incidence matrix, exact elimination) at N = 4, m = 3: the certificate of
algebraicity for the span of the 48 line classes is the computed elimination itself.
WP2's contribution is to generalize the pattern from "the fixed 48 lines" to the
full Shioda generator set of X_{N,m} and to record its complexity, not to invent
new machinery.

The concrete input sizes make the polynomial claim quantitative. For the Fermat
plane curve of degree N, the census size is h_N = (N−1)(N−2)/2 (the genus), so
h₇ = 15, h₉ = 28, h₁₁ = 45; for the flagship fivefold family the middle cohomology
census is h₁₅ = 91 and h₃₀ = 406 (with the profile decompositions 91 = 1 + 6 + 84
and 406 = 1 + 6 + 9 + 30 + 84 + 276 already computed by the two schemes). The
integer matrices entering the certificate therefore range from 15×15 to a few
hundred rows — sizes at which exact fraction-free elimination and Kannan–Bachem SNF
run in well under a second, in keeping with the two-second full-protocol execution
of v1.4. Polynomiality here is not an asymptotic abstraction but a statement about
workloads the program already performs.

### 5.4 Where the wall is

The honest boundary of polynomial claims is drawn as follows.

1. **Beyond C₀ the generating set of Hodge classes is not known a priori.** For a
   general hypersurface, Fact 5.1 has no analogue, and VER-HODGE has no known
   algorithm at all — the certificate side can be attempted, the completeness side
   cannot be promised.
2. **The Level-1 pipeline is polynomial only for fixed ambient dimension n** in the
   sense of [Lairez 2016]; the dependence on n is controlled but must be measured,
   not assumed.
3. **Algebraic-number recognition** ("which algebraic number is this period?") via
   LLL is polynomial in the numerical precision but requires a height bound on the
   target; the ledger records the height bound as an assumption per stand, in the
   spirit of the certificate F pattern (q-scan, minimal polynomial recognition).
4. **No structural complexity claims.** Mirroring the chess note's "untouchability"
   argument: no statement of the form "VER-HODGE is NP-hard" or "VER-HODGE ∈ NP" is
   claimed, known, or required by the program; the complexity ledger measures the
   *shape of the wall* for the accepted classes, exactly as E1–E3 did for chess, and
   leaves the structural complexity questions open by default.

---

## 6. WP3 — Stands v1.5–v1.8

WP3 upgrades the ladder itself. Each version gate adds one stand or one computed
capability, preserves the frozen baseline (every new value enters
`baseline_v1_v9.json` with a regression branch), and propagates to the polyglot and
web mirrors according to the propagation protocol (§7.6).

### 6.1 v1.5 — The N=11 rung (certificate K)

The N=11 rung is the natural next cyclotomic level and is already scoped in the
repository's own roadmap: genus g(11) = 45, census h₁₁ = 45, and the braking
constant b_Ch(11) = 1 − cos(2π/11), whose minimal polynomial is a quintic over ℚ
with coefficients in the real cyclotomic subfield. Deliverables:

1. the automated minimal-polynomial routine for 2cos(2π/n) for arbitrary n —
   replacing the hardcoded dictionaries with exact arithmetic in ℤ[x]/(Φ_n) (the
   polynomial kernels `_poly_mul`, `_poly_mod_phi`, `_minpoly_irreducible_gf2`
   already support the pipeline);
2. certificate K following the I/J pattern (census, Vieta data in
   ℤ[ζ₁₁]/(Φ₁₁), GF(2) irreducibility, exact radical or Cardano form);
3. monograph slot T21;
4. baseline and polyglot propagation.

The Vieta-identification step is the only genuinely new mathematics; it follows the
two-scheme discipline (symbolic derivation plus high-precision numeric cross-check
at 40 dps).

### 6.2 v1.6 — The SNF engine (certificate H computed)

The Smith normal form tuple (1,1,5,5,15,15,15,15) currently printed by the flagship
stand is a **literal**. v1.6 replaces it with a computed Smith normal form over ℤ,
implemented after Kannan–Bachem [1979] with the Storjohann refinement [1996] for
the elimination schedule (pseudocode in the PDF edition, Appendix B). Acceptance
tests:

1. the computed SNF of the N=15/30 period matrix equals the frozen literal,
   byte-identical;
2. properties — diagonal divisibility chain d₁ | d₂ | ⋯, product ∏dᵢ = |det|, and
   unimodular round-trip — hold on a generated suite of random integer matrices
   with known answers;
3. the same engine recomputes the Arf-enumeration lattices and the K3 intersection
   lattice, upgrading the declared det 64 and signature (1,19) to computed
   quantities (signature via the numerical–exact bridging rule: Sylvester counts on
   the certified rational form).

Monograph slot T22 documents the engine and the general SNF-spectrum program for
N = 7/9/11.

### 6.3 v1.6+ — Gross normalization computed

The Gross Γ-normalization vol_h = (2π)³² ∏ₖ Γ(k/N)^{−cₖ} = 1125 is quoted with
residual 10⁻¹¹⁹ but not recomputed in code. The v1.6 wave adds a
`gross_normalization` run type that performs the high-precision evaluation via
`mpmath` at 80–100 dps, cross-checks the integer result 1125 exactly, and —
crucially — generalizes the census-weighted Γ-product to arbitrary N, turning a
cited constant into a parametric family. This is also the template for upgrading
the remaining "documented" certificate items to "computed" status (certificate map,
PDF edition, Appendix E).

### 6.4 v1.7 — Unified exact layer + `HODGE-INPUT` parser

v1.7 unifies the exact-layer machinery: for arbitrary n, the program derives Φ_n,
the minimal polynomial of 2cos(2π/n), Vieta-profile data, and irreducibility
certificates without per-level dictionaries, and exposes the whole conveyor through
the `HODGE-INPUT v1` parser (§4.2). The designer menu is retained as a thin shell
over the parser. Level-0 instances become **executable documents**: the flagship
triple (15, 5), the quartic (4, 3), and the rungs (7, 2), (9, 2), (11, 2) all run
from `.json` inputs, with provenance hashes recorded in the claim registry
(Criterion 3.3).

### 6.5 v1.8 — First Level-1 stand: the Dwork pencil

v1.8 introduces the first stand whose input is an *equation*: the Dwork pencil of
quintic threefolds

```
X_ψ :  x₀⁵ + x₁⁵ + x₂⁵ + x₃⁵ + x₄⁵ − 5ψ·x₀x₁x₂x₃x₄ = 0  ⊂  ℙ⁴.
```

The stand computes:

- the Griffiths–Dwork reduction of the invariant middle forms (PDF edition,
  Appendix C);
- the Picard–Fuchs equation of the pencil (cross-checked against the classical
  order-4 operator [Candelas et al. 1991; Cox–Katz 1999]);
- certified periods at rational ψ-points via the algorithmic framework of
  [Lairez 2016] with tanh-sinh quadrature as the independent numerics;
- the algebraic recognition of the Fermat point ψ = 1 against the Level-0
  Γ-values — the first **cross-level consistency check** of the program, where a
  Level-1 pipeline must reproduce a Level-0 closed form.

The verdict classes follow the honesty ladder of §9.

### 6.6 Propagation protocol

Every stand upgrade propagates in a fixed order:

1. `laboratory.py` with baseline branch;
2. pytest suite (new checks mirror the two-scheme pattern);
3. polyglot cores — the C and Rust integer kernels receive the exact-arithmetic
   parts, the JS web mirror receives the display constants, with bit-identical
   expected values;
4. Lean kernel — the machine-checked identities gain the new integer facts;
5. monograph slot and CHANGELOG.

A wave is closed only when all five layers report `ALL CHECKS PASSED`, which keeps
the triple-stacked codebase (Python / polyglot / web) from drifting — the
maintenance risk analyzed in §11.

---

## 7. WP4 — Lean 4 Formalization

### 7.1 Scope: what to formalize first

The Lean layer currently machine-checks integer identities (`native_decide`, no
axioms, no Mathlib). The roadmap extends it in three increments, ordered by
formalization cost:

1. **The input grammar.** `HODGE-INPUT v1` as inductive types (variety kinds, basis
   names, coefficient vectors), with parsers rejecting malformed documents by
   construction — a small, self-contained development.
2. **The SNF specification.** The normal-form properties (divisibility chain,
   unimodular equivalence, invariance) as a spec against which the Python engine's
   outputs are checked; this uses Mathlib's existing Smith-normal-form development
   [mathlib 2020] and keeps the complexity claims outside Lean.
3. **The census agreement.** The two-scheme equality (direct gcd counting versus
   Möbius inversion) for all N below a bound, generalizing the existing
   machine-checked census identities.

> **Acceptance criterion 7.1 (Lean, month 6).**
> (i) every shipped `HODGE-INPUT` instance has a Lean-auditable provenance record
> (grammar validity, canonicalization hash);
> (ii) the SNF engine's output on the regression suite is verified against the
> Mathlib-specified normal form properties;
> (iii) the two-scheme census agreement is machine-checked for N ≤ 64;
> (iv) `lake check` completes in CI under 15 minutes with a pinned Mathlib
> toolchain.

### 7.2 What stays outside Lean

Complexity classes beyond what Mathlib supports, transcendental period values, and
the Griffiths–Dwork reduction remain outside the formal scope for this horizon. The
decision rule is the one already used by the program: **Lean formalizes
discrete-certificate correctness, while numerical verification remains the task of
the high-precision protocol with its explicit thresholds.** This division of labor
keeps the Lean layer axiom-light and the CI sustainable on a single-maintainer
budget.

### 7.3 CI integration

The Lean package lives under `verification/lean4/` with its own `lakefile`, pinned
`lean-toolchain`, and a cached `elan` install in CI. Rebuilds trigger on three
events: toolchain pin change (weekly Mathlib sync window), grammar version bump, or
certificate-format change. The Lean checks are **gating, not advisory**: a failed
`lake check` blocks a release exactly as a failed V1–V9 run does, preserving the
program's invariant that every shipped claim is executable-checked somewhere.

---

## 8. WP5 — Methodology Transfer from the Chess Branch

The chess-dynamics-lab program (v2.2.0) is the methodological proving ground of the
same authorial school: it transplanted the "dynamic principle" from Hodge-theoretic
stands to chess and, in doing so, developed a set of engineering patterns for making
computational mathematics *honest*. This section transfers four of them into the
Hodge laboratory. The transfer is one-directional by design: physics metaphors
(Lagrangians, damping, vortices) remain interpretive in both programs and are never
promoted to mathematical claims.

### 8.1 The trilemma as statement discipline

> **Trilemma (working rule, imported from chess note N1).** For a computational
> claim, choose at most three of: **polynomial** (resource bound poly in input
> size), **exact** (certificate free of floating-point data), **explicit** (the
> answer names its witnesses — cycles, not mere existence). Any claim that satisfies
> all three must come with a proof; any claim that gives one up must say which and
> why.

In the chess branch the trilemma is measured, not asserted: the particle solver is
polynomial and explicit but loses 17.56% of won KRK positions and +2.95 plies of
optimality (E1), while the exact table base is exact and explicit but exponential
(E3). The Hodge analogue is immediate: on Level 0 the trilemma collapses (all three
hold, Target theorem 5.2); on Levels 1–2 exactness is limited by height-bound
assumptions in algebraic recognition, and explicitness is limited by the absence of
known generators. Every stand in v1.5–v1.8 is annotated with its trilemma status in
the claim registry, and the README's certificate table gains a trilemma column.

### 8.2 Falsification-first engineering

The chess program's Epoch VI mines disagreements between model and oracle
(`falsify.py`): every hard error became a regression corpus row (E10), and the next
model version is contractually required to compress the corpus without breaking the
headline metrics. The Hodge analogue is a **near-miss corpus**: instances of
`HODGE-INPUT` that are deliberately wrong in one dimension — a character outside
the holomorphicity constraint, a coefficient vector violating Hodge-stability, a
ψ-value at a singular fiber — each paired with the exact REJECT / NOT-DETERMINED
verdict the pipeline must produce. The corpus lives in `counterexamples/`, is
executed in CI, and grows only additively, exactly like its chess counterpart.

### 8.3 Honest negatives as frozen artifacts

The chess branch froze its negative results with the same care as its positives:
the soft-target hypothesis was *falsified* and kept (hard targets win, 0.9499 vs
0.9086), the interaction-hinge basis was *denied* by a double gate (E13), and the
Elo-context prior was shown to *hurt* on oracle-domain positions (E12). The Hodge
laboratory adopts the pattern as a publication rule: an upgrade that fails its gate
is frozen as a negative experiment (E-numbering continues), documented in the
monograph, and never silently dropped. Concretely expected negative space: LLL
recognition without a height bound (recognized *wrong* algebraic numbers),
quadrature depth scaling at high N (where the 140-row SVD cap of V7 degrades), and
Griffiths–Dwork reduction blow-up on degenerate families.

### 8.4 The verdict ladder

The chess large-board laboratory introduced an explicit ladder of proof classes —
FULL > WEAK > ULTRA-WEAK > PARTIAL POLICY — so that the 112×112 verdict could be
reported as a policy-based partial result without overclaiming. The Hodge
laboratory adopts the same ladder with Hodge-specific classes:

| Class | Meaning | Current holders |
|-------|---------|-----------------|
| **FULL** | machine-checked certificate + closed-form equality | K3 rank (exact ℚ), censuses, Arf |
| **WEAK** | exact computation, one independent scheme | Vieta triples, j-invariant |
| **ULTRA-WEAK** | high-precision agreement, thresholds passed | V2/V6/V9 quadrature stands |
| **PARTIAL POLICY** | pipeline verdict on an input class, generators not exhaustive | (target class of the Dwork pencil stand) |

Every stand carries its class in the README; upgrading a class requires an upgrade
of the machinery, not of the prose.

### 8.5 What the chess branch gives, summarized

| Chess pattern | Source | Hodge application |
|---------------|--------|-------------------|
| Trilemma N1 | `complexity/P_VS_NP.md` | statement discipline + registry column (§8.1) |
| Falsification engine (E10) | `outcome/falsify.py` | near-miss corpus `counterexamples/` (§8.2) |
| Honest negatives (E12, E13) | frozen experiments | negative-experiment ledger in monographs (§8.3) |
| Verdict ladder | `large_board_lab` | honesty classes for stands (§8.4) |
| Bit-identical polyglot | `polyglot/` C1–C10 | propagation protocol cross-checks (§6.6) |
| Vortex reading | `vortex/` E4 | interpretive period-flow visualization (web mirror only) |

---

## 9. Timeline — 26 Weeks

The horizon is six months, organized in six waves with hard gates. Effort assumes a
single maintainer with intermittent reviewer input; every wave contains a
documentation slot and a CI slot so that the monograph collection and the
verification suite grow together, in the style the program has followed since v1.0.

| Weeks | Wave | Content | Gate (version) |
|-------|------|---------|----------------|
| 1–4 | Foundation | claim registry `claims/registry.yaml`; complexity ledger skeleton `complexity/ledger.yaml`; near-miss corpus bootstrap; `HODGE-INPUT` schema draft + parser prototype; Lean grammar skeleton | registry and ledger live in CI (v1.5-pre) |
| 5–9 | v1.5 | N=11 rung: automated minimal polynomial of 2cos(2π/11), census(11) dual-scheme, Vieta data in ℤ[ζ₁₁], certificate K, monograph T21, baseline + polyglot propagation | certificate K ALL CHECKS PASSED (v1.5) |
| 10–14 | v1.6 | SNF engine (Kannan–Bachem/Storjohann) + regression suite; flagship literal replaced; K3 determinant/signature upgraded to computed; Gross normalization computed at 80–100 dps; monograph T22 | SNF regression green, 1125 recomputed (v1.6) |
| 15–19 | v1.7 | unified exact layer for arbitrary n; `HODGE-INPUT v1` parser finalized; Level-0 instances as executable JSON documents; batch types `snf`/`rank`/`cycle-certificate`; Lean: grammar + census agreement N ≤ 64 | five Level-0 instances run from JSON end-to-end (v1.7) |
| 20–24 | v1.8 | Dwork pencil stand: Griffiths–Dwork reduction, Picard–Fuchs, certified periods, Fermat-point cross-level check; Lean: SNF spec wiring; paper draft (§12) | Level-1 acceptance (Criterion 4.1) on a ψ-grid (v1.8) |
| 25–26 | Release | full protocol re-run, frozen baseline v1.8, Zenodo DOI, README roadmap rewrite, monograph T24 (Dwork stand) | five-layer propagation closed (v1.8) |

**Dependency logic.** The parser (WP1) unblocks the executable-document format that
WP2's ledger and WP4's grammar consume; the stands (WP3) produce the data that the
ledger annotates; WP5 is continuously verified by CI rather than scheduled. The
critical path is WP3 (mathematics + propagation), which is why the trilemma-free
Level-0 work is front-loaded and the Level-1 Dwork stand is scheduled only after
the exact layer has been unified.

```
  [WP3 stands v1.5→v1.8] ──▶ [WP1 parser: grammar+levels] ──▶ [WP2 ledger: target theorem]
                                        │                                │
                                        ▼                                ▼
                              [WP4 Lean: grammar, SNF spec] ──▶ [WP5 registry, verdict ladder]
```

---

## 10. Risks and Mitigations

The register below follows the review discipline of the chess branch: every risk is
paired with a mitigation that is an executable artifact (a gate, a test, a frozen
experiment), not a promise. Likelihood and impact are graded H/M/L against the
six-month horizon and the single-maintainer budget; the two structural risks —
triple-stack drift and the bus factor — are permanent features of the program's
architecture and are therefore managed by protocol rather than by hope. Risks that
materialize are converted into frozen negative experiments (§8.3) rather than
silently re-scoped.

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Griffiths–Dwork reduction blow-up on degenerate families | M | M | restrict v1.8 to the Dwork pencil; pre-screen singular fibers in the parser (smoothing prechecks); measure, do not assume, the n-dependence [Lairez 2016] |
| LLL recognition without height bounds returns wrong algebraic numbers | M | H | height bound recorded as an assumption per stand (cert. F pattern); negative result is frozen as an experiment, not patched over |
| Mathlib/Lean churn breaks CI | M | M | pinned toolchain; weekly sync window; `native_decide` layer kept Mathlib-free |
| Triple-stack drift (Python / polyglot / web) | H | M | five-layer propagation protocol (§6.6); release blocked unless all layers pass |
| Scope creep toward general Hodge claims | M | H | Remark 3.4 (exclusions); claim registry `status: excluded`; trilemma column in README |
| Baseline drift across versions | L | H | additive baseline branches; byte-identical regression on the flagship literals until superseded by computed values (v1.6) |
| Single-maintainer bus factor | H | M | monographs as executable documentation; propagation scripts; registry doubles as on-boarding map |
| Quadrature precision wall at high N (V7 SVD cap 140 rows) | M | M | cap documented as PARTIAL POLICY class; adaptive-precision tanh-sinh; V7 redesigned as certified rank verification via exact elimination on subblocks |

---

## 11. Publication and Dissemination Plan

**Paper target.** The v1.8 wave culminates in a paper with the working title
*"Verifying Hodge classes in parametric families: input formats, certificates, and
complexity bounds"*. The paper's claims are exactly the registry claims of v1.8:
the target theorem of §5.2 (with full proof), the complexity ledger for C₀, the
computed SNF results for N = 7/9/11/15/30, and the Dwork-pencil cross-level check.
The venue profile is a computational-mathematics journal or conference in the orbit
of [Lairez 2016; Kedlaya 2001; Edixhoven–Couveignes 2011]; the chess branch's
"Particle Limit" paper is the stylistic precedent for measured-claims writing.

**Monograph slots.** T21 (N=11, certificate K), T22 (SNF spectra and the engine),
T23 (claim registry and the trilemma discipline), T24 (the Dwork pencil stand).
Each monograph follows the existing RU/EN × PDF/DOCX pipeline; the unified
monograph gains a new part "From stands to algorithms" mirroring §3–§5 of this
document.

**Repository and DOI.** This roadmap is committed as `docs/ROADMAP.md` and versioned
with the code; the Zenodo record is minted per version gate (v1.5, v1.6, v1.7,
v1.8), each citing this document as the plan of record. The README's Roadmap
section is replaced by a pointer to `docs/ROADMAP.md` plus the current gate status,
so that the plan and the repository never diverge.

---

## 12. References

1. N. Aoki, *Algebraic cycles on Fermat varieties*, Comment. Math. Univ. St. Pauli **38** (1989), 111–125.
2. S. Aaronson, A. Wigderson, *Algebrization: a new barrier in complexity theory*, ACM Trans. Comput. Theory **1** (2009), no. 1, Art. 2.
3. T. Baker, J. Gill, R. Solovay, *Relativizations of the P = ?NP question*, SIAM J. Comput. **4** (1975), no. 4, 431–442.
4. A. Bostan, F. Chyzak, M. Lairez, B. Salvy, *Generalized Hermite reduction, creative telescoping and definite integration of D-finite functions*, Proc. ISSAC 2018, ACM, 2018, 161–168.
5. P. Candelas, P. S. Green, T. Hübsch, *Connecting Calabi–Yau compactifications*, Nuclear Phys. B **330** (1991); and P. Candelas et al., *A pair of Calabi–Yau manifolds as an exactly soluble superconformal theory*, Nuclear Phys. B **359** (1991), 21–74.
6. C. H. Clemens, *A Scrapbook of Complex Curve Theory*, Plenum Press, New York, 1980.
7. D. A. Cox, S. Katz, *Mirror Symmetry and Algebraic Geometry*, Math. Surveys Monogr. **68**, AMS, Providence, RI, 1999.
8. P. Deligne, *Théorie de Hodge. II*, Publ. Math. IHÉS **40** (1971), 5–57.
9. B. Dwork, *On the zeta function of a hypersurface*, Publ. Math. IHÉS **12** (1963), 5–68.
10. B. Edixhoven, J.-M. Couveignes (eds.), *Computational Aspects of Modular Forms and Galois Representations*, Ann. of Math. Stud. **176**, Princeton University Press, 2011.
11. A. S. Fraenkel, D. Lichtenstein, *Computing a perfect strategy for n×n chess requires time exponential in n*, J. Combin. Theory Ser. A **31** (1981), no. 2, 199–214.
12. B. Gross, *Heights and special values of L-series*, in: Number Theory (Montréal, 1985), CMS Conf. Proc. **7**, AMS, 1987, 115–187.
13. P. A. Griffiths, *On the periods of certain rational integrals. I, II*, Ann. of Math. (2) **90** (1969), 460–495; 496–540.
14. J. Hartmanis, R. E. Stearns, *On the computational complexity of algorithms*, Trans. Amer. Math. Soc. **117** (1965), 285–306.
15. I. I. Isaev, *Chess Particle Dynamics: A Certifiable Laboratory* (chess-dynamics-lab, v2.2.0), research program with monograph series and protocols C1–C9, 2026; incl. complexity notes N1–N2.
16. I. I. Isaev, *Hodge Laboratory: The Dynamic Principle Laboratory* (hodge-laboratory, v1.4), reproducible verification platform: certificates A–J, protocol V1–V9, twenty theorem monographs, 2025. https://github.com/wild8highlander/hodge-laboratory
17. R. Kannan, A. Bachem, *Polynomial algorithms for computing the Smith and Hermite normal forms of an integer matrix*, SIAM J. Comput. **8** (1979), no. 4, 499–507.
18. K. S. Kedlaya, *Counting points on hyperelliptic curves using Monsky–Washnitzer cohomology*, J. Ramanujan Math. Soc. **16** (2001), no. 4, 323–338.
19. A. G. B. Lauder, *Counting solutions to equations in many variables over finite fields*, Found. Comput. Math. **4** (2004), no. 3, 221–267.
20. P. Lairez, *Computing periods of rational integrals*, Math. Comp. **85** (2016), no. 300, 1719–1752.
21. J. P. Lewis, *A Survey of the Hodge Conjecture*, 2nd rev. ed. (J. P. Murre), CBMS Regional Conf. Ser. in Math. **10**, AMS, 1999.
22. A. K. Lenstra, H. W. Lenstra, Jr., L. Lovász, *Factoring polynomials with rational coefficients*, Math. Ann. **261** (1982), no. 4, 515–534.
23. The mathlib Community, *The Lean mathematical library*, Proc. CPP 2020, ACM, 2020, 367–381.
24. Z. Ran, *Cycles on Fermat hypersurfaces*, Compositio Math. **42** (1980/81), no. 1, 121–142.
25. A. A. Razborov, S. Rudich, *Natural proofs*, J. Comput. System Sci. **55** (1997), no. 1, 224–234.
26. J. Schaeffer et al., *Checkers is solved*, Science **317** (2007), no. 5844, 1518–1522.
27. T. Shioda, *The Hodge conjecture for Fermat varieties*, Math. Ann. **245** (1979), no. 2, 175–184.
28. T. Shioda, T. Katsura, *On Fermat varieties*, Tôhoku Math. J. (2) **31** (1979), no. 1, 97–115.
29. A. Storjohann, *Near optimal algorithms for computing Smith normal forms of integer matrices*, Proc. ISSAC 1996, ACM, 1996, 267–274.
30. C. Voisin, *Hodge Theory and Complex Algebraic Geometry. I, II*, Cambridge Stud. Adv. Math. **76, 77**, Cambridge University Press, 2002–2003.

---

## 13. Notation and Glossary

| Symbol / term | Meaning |
|---------------|---------|
| X_{N,m} | Fermat hypersurface Σxᵢᴺ = 0 of degree N in ℙ^m |
| C_{N,m} | census: the character list of X_{N,m}, i.e. tuples (a₀,…,a_m) with aᵢ ≠ 0, Σaᵢ ≡ 0 (mod N) |
| Ω_{a,b} | closed-form period Γ(a/N)Γ(b/N)/Γ((a+b)/N) |
| P(r,s) | period entry ⅟N·ζ_N^{cr+ds}·Ω_{a,b} of the character-basis period matrix |
| Δ_Ch | unified dynamic principle value Δ₀ − R/4 + δ²/2 − δ⁵/k with δ = π/n |
| b_Ch(n) | braking constant 1 − cos(2π/n); its exact layer lives in ℤ[ζ_N]/(Φ_N) |
| Φ_n, ζ_n | the n-th cyclotomic polynomial and primitive root of unity |
| ρ | Picard number (rank of the Néron–Severi lattice); the K3 stand attains ρ = 20 |
| SNF | Smith normal form over ℤ; the flagship tuple (1,1,5,5,15,15,15,15) is its frozen value |
| LLL | Lenstra–Lenstra–Lovász lattice reduction; the rationalization engine of certificate F |
| dps | decimal places of the high-precision verification layer (mpmath / BigFloat) |
| VER-HODGE(Cᵢ,p) | the decision problem of §3.1 on input class Cᵢ, codimension p |
| Level ℓ (Cℓ) | input generality level: 0 Fermat-type, 1 smooth hypersurfaces, 2 plane curves, 3 complete intersections |
| `HODGE-INPUT v1` | the JSON input grammar of §4.2 (Appendix A of the PDF edition) |
| Certificate | exact machine-checkable document proving one registry claim (cycle data, SNF, period closure) |
| Claim registry | `claims/registry.yaml`: every claim with its (input class, output, bound) triple and test |
| Complexity ledger | `complexity/ledger.yaml`: per-subroutine resource bounds and implementation status |
| Trilemma | working rule: polynomial, exact, explicit — a claim satisfies all three only with a proof attached |
| Verdict ladder | honesty classes FULL > WEAK > ULTRA-WEAK > PARTIAL POLICY (§8.4) |
| Near-miss corpus | `counterexamples/`: invalid instances paired with the verdict the pipeline must produce |
| Protocol V1–V9 | the nine-stage verification conveyor; C1–C9 is its chess-branch counterpart |
| Falsification | the practice of freezing failed upgrades as negative experiments (chess E10/E12/E13 pattern) |

---

## Appendix A. `HODGE-INPUT v1` — Field Reference

Full normative schema (flagship example N=15 in the PDF edition, Appendix A):

| Field | Type | Semantics and constraints |
|-------|------|---------------------------|
| `schema` | string | format tag; pinned `hodge-input/1.0` |
| `variety.kind` | enum | resolves the conveyor and the level tag ℓ |
| `variety.degree` | int | d ≥ 3; for level 0 also fixes the cyclotomic order N = d |
| `variety.ambient_dim` | int | m ≥ 2; omitted for plane curves (m = 2) |
| `variety.equation` | object | required for ℓ ≥ 1; homogeneous over ℚ; smoothing-screened |
| `variety.family_parameter` | object | level 1 only; rational value, must avoid singular fibers |
| `hodge_class.codimension` | int | p of H^{2p}; dimension-checked against the basis |
| `hodge_class.basis` | enum | names the finite generating set consumed by certificates |
| `hodge_class.coefficients` | array | exact combination; canonicalized to lowest terms |
| `verification.precision_dps` | int | numeric layer precision (default 40; V9 uses 70) |
| `verification.certificates` | array | subset of the certificate registry |
| `verification.exact_arithmetic` | bool | when true, no certificate may contain float data |
| `provenance` | object | stand name, baseline key, free note; hashed into the run record |

## Appendix B. SNF Engine — Contract and Regression Plan

The computed Smith normal form (Kannan–Bachem with Storjohann elimination schedule)
records the unimodular transforms (U, V) with U·A·V = S and enforces the
divisibility chain S₁₁ | S₂₂ | ⋯ by gcd/lcm 2×2 blocks. Regression plan:

- **(R1) Flagship equality.** Computed SNF of the N=15/30 period matrix equals the
  frozen literal (1,1,5,5,15,15,15,15) byte-identically.
- **(R2) Property suite.** 10⁴ generated matrices (sizes up to 200×200, entries to
  10⁶): divisibility chain, ∏dᵢ = \|det\|, zero rows/columns canonicalized,
  unimodular round-trip UAV = S exact.
- **(R3) Cross-language.** The C and Rust polyglot kernels reproduce the diagonal on
  the suite bit-identically.
- **(R4) Timing ledger.** Measured wall-clock vs. the poly bound of
  [Kannan–Bachem 1979; Storjohann 1996] appended to `complexity/ledger.yaml`.

## Appendix C. Certificate Map: A–J and Work Packages

| Cert | Content | Status (v1.4) | Target |
|------|---------|---------------|--------|
| A | cycle certificator, divisor on K3, kernel 29 | documented | v1.7 computed (WP2 S3) |
| B | period closure of kernel 29, blind spot | documented | v1.7 computed |
| C | μ₄-equivariance isotypy of K3 | documented | v1.7 computed |
| D | universal μ₄ theorem | documented | stays documented (mathematical statement) |
| E | flow termination t\* = lcm | computed | retained; generalized |
| F | LLL rationalization, CM recognition | partially computed | v1.7 full (height-bound ledger) |
| G | Hodge lattice indices, Chow–Selberg | numeric | v1.7 exact layer |
| H | flagship SNF, vol_h = 1125, Q = 480 | literal + partial | v1.6 fully computed |
| I/J | rungs N = 7/9 | computed | retained; template for K |
| K | rung N = 11 (new) | none | v1.5 |
