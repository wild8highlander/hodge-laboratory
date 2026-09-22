# Verification in five languages and the Lean 4 kernel

Each implementation checks **the same base set of identities** of the
program: the genera 91 and 406; the censuses 1+6+84 and
1+6+9+30+84+276; the discriminant 1125²; the product of the SNF type;
the Klein invariants (j = −3375); the Arf counts (36 even / 28 odd on
genus 3); the termination t* = lcm(…); the binary-code cross-check
48/212/432/114. The agreement of independent implementations —
different languages, different ecosystems, no shared code — is the
strongest form of a reproducibility certificate.

| Language | File | Run |
|---|---|---|
| **Python 3.10+** | [`../laboratory.py`](../laboratory.py) | `python3 laboratory.py --run all` |
| **Lean 4** | `lean/HodgeLaboratory.lean` | `lean lean/HodgeLaboratory.lean` |
| **Julia 1.9+** | `julia/verify_hodge.jl` | `julia julia/verify_hodge.jl` |
| **Fortran (gfortran 10+)** | `fortran/verify_hodge.f90` | `gfortran -O2 -o vh fortran/verify_hodge.f90 && ./vh` |
| **C (gcc/clang)** | `c/verify_hodge.c` | `gcc -O2 -o vh c/verify_hodge.c -lm && ./vh` |
| **Rust (rustc 1.70+)** | `rust/verify_hodge.rs` | `rustc -O rust/verify_hodge.rs -o vh && ./vh` |

All backends are deterministic and exit `0` on full agreement, `1` on
any mismatch.

## What exactly is checked

### The integer layer (all implementations)

- Genus of the Fermat curve: `g(15)=91`, `g(30)=406`, `g(7)=15`, `g(4)=3`;
- Character census by conductor: exact sums `Σh_d = g`;
- The h_d tables: `1+6+84` (N=15) and `1+6+9+30+84+276` (N=30),
  including the full per-conductor table h(3)=1, h(5)=6, h(6)=9,
  h(10)=30, h(15)=84, h(30)=276;
- The stand discriminant: `3⁴·5⁶ = 1265625 = 1125²`;
- The product of the SNF type `(1,1,5,5,15,15,15,15) = 1265625`;
- The Klein invariants: `c₄³ = 105³ = 1157625`,
  `|Δ|·|j| = 343·3375 = 105³`, `j = −3375 = −15³`, `Δ = −7³`,
  `disc(v²+7v+14) = −7`;
- Errata E8: `36` even (`Arf=0`) + `28` odd (`Arf=1`) = `64`,
  plus g = 1, 2, 4 cross-checks;
- Flow termination (E4): `t*(48,48,1,1)=48`, `t*(24,36,3,5)=72`,
  `t*(12,12,4,6)=6`;
- Binary code reference totals: `48+212+432+114 = 806`;
- **K3: the exact rank of the 49×49 intersection matrix over ℚ = 20**
  (C and Rust — full rational elimination with fractions).

### The high-precision layer (Python mpmath / Julia BigFloat)

- The closed period form against the independent tanh–sinh
  quadrature (`3.9·10⁻³⁶` at dps = 35 in Python; BigFloat at
  240 bits ≈ 72 decimal digits in Julia);
- The phase law `arg P = 2π(ra+sb)/N` — deviation `0.0` in Python;
- The reflection ladder `Γ(k/N)Γ(1−k/N) = π/sin(πk/N)`;
- The μ_N×μ_N equivariance `P(r+u, s+v) = ζ^{ua+vb}·P(r, s)`;
- (Python only) the V5 orbit sums: Σ_k P(k, k) vanishes for
  a+b ≢ 0 (mod N) and equals Ω for the positive control a+b = N.

> **Julia precision note.** v1.1.0 fixed an early bug: 70 was meant
> as decimal digits but `setprecision(BigFloat, 70)` sets 70 *bits*.
> The current script sets 240 bits ≈ 72 digits and uses `big(π)` at
> working precision, so every threshold is honestly reachable.

### The machine layer (Lean 4, the kernel)

- Every integer identity is verified by full computation
  (`native_decide`, `decide`) — no axioms, no Mathlib;
- The propositions span the genus formula, the census sums and the
  Möbius inclusion–exclusion, the SNF product, the discriminant, the
  Klein integers, the Arf counts for g = 1..4, the termination times,
  and the K3 stand numbers;
- Exit codes: `0` — all propositions accepted, `1` — a failure.

## Verdict agreement

The laboratory (`laboratory.py`, menu items 7/8, or
`--run multi`) compiles and runs every available backend and prints
their tails; CI reads the exit codes. An error repeated
simultaneously in five independent ecosystems and in the Lean kernel
is practically impossible — and the pytest suite
([`../tests/`](../tests/)) plus the baseline cross-check
(`laboratory.py --check-baseline`) close the loop inside Python
itself.

---

**License:** the individual exclusive license of
Isaev Iskhak Khamzatovich (see `LICENSE` at the repository root).
Any use without the author's written permission is prohibited.

<div align="center">

© 2026 Isaev Iskhak Khamzatovich · All rights reserved

</div>
