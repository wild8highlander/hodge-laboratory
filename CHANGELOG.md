# Changelog

All notable changes to Hodge Laboratory are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — roadmap v1.2 + v1.4

### Added

* **Roadmap v1.2 — radical arithmetic for `b_Ch(15)` and `b_Ch(30)`
  inside the designer** (menu item 5): the braking constants now ship
  with closed radical forms — `b_Ch(15) = (7 − √5 − √(30−6√5))/8`,
  `b_Ch(30) = (9 − √5 − √(30+6√5))/8` — each certified by two
  layers. The exact layer runs on pure integer arithmetic in the
  biquadratic tower `Z[√5][√(30∓6√5)]`: the radical satisfies its
  monic quartic minimal polynomial exactly (`x⁴−x³−4x²+4x+1` for
  N=15, `x⁴+x³−4x²−4x+1` for N=30) and the quartic is irreducible
  over GF(2). The numeric layer compares the closed form against
  mpmath `cos` at the working dps (threshold 1e-25, measured margins
  ≈1e-34). New API: `bch_closed`, `bch_numeric`, `bch_exact_layer`,
  `BCH_RADICALS`.
* **Roadmap v1.4 — batch experiment mode**: `python3 laboratory.py
  --batch scenario.json [--batch-out FILE]` runs a scripted queue of
  designer experiments — `period`, `census`, `cm`, `flow`, `bch`,
  `omega` — and writes a combined JSON verdict (default
  `reports/batch_report.json`) with a per-run verdict, the
  `ALL PASS` / `FAIL` summary and the scenario dps. The queue is
  deterministic and crash-hardened: a malformed run is recorded as a
  failure and never kills the batch. Exit codes mirror the verdict:
  `0` ALL PASS, `1` failures present, `2` malformed scenario file.
  The designer (menu item 7) accepts the same scenario
  interactively; a ready scenario ships as
  [`examples/batch_smoke.json`](examples/batch_smoke.json).
* **`scripts/set_doi.sh`** — one-command registration of the minted
  Zenodo DOI: rewrites the README badge and the `identifiers` block
  of `CITATION.cff`; the concept DOI is added via
  `CONCEPT_DOI=10.5281/zenodo.<ID>`.
* 10 new pytest tests (40 total): the exact b_Ch certificate, the
  known minimal quartics, the batch queue (ALL PASS, FAIL,
  crash-hardening, scenario dps).

### Fixed

* **README** — the DOI badge carried the placeholder
  `10.5281/zenodo.XXXXXX` and linked to the «DOI NOT FOUND» page at
  doi.org (no Zenodo record exists yet). The badge is now a neutral
  «pending Zenodo mint» state linking to §15; once the record is
  minted, `scripts/set_doi.sh` installs the real DOI in one command.
* `reports/` — reference artifacts regenerated with v1.1.2 (the
  committed copies were stale v1.1.0 runs with a vacuous `V7` entry).

## [1.1.2] — 2026-09-22

### Fixed

* **`verification/fortran/verify_hodge.f90`** — the file did not
  compile with gfortran ≥ 8, so the CI "Fortran verification" step
  failed on every run (`Error: Type mismatch in argument …; passed
  INTEGER(4) to INTEGER(8)`): twelve call sites passed default-kind
  integer expressions into `integer(int64)` dummies. The literals in
  the Klein / SNF / ladder / K3 / genus checks now carry the `_int64`
  suffix, `tstar` converts its reduced dimensions with
  `int(…, int64)` before calling `lcm64`, and `isqrt` computes its
  seed in double precision. 24 checks, all pass.
* **`verification/julia/verify_hodge.jl`** — the script had never run
  to completion: Base Julia has no `gamma` (it lives in the external
  SpecialFunctions.jl), so the first period check crashed with
  `UndefVarError: gamma not defined`. Log-Γ is now evaluated
  self-containedly by the Stirling series with argument shifting,
  with the Bernoulli numbers from the exact `Rational{BigInt}`
  recurrence. Two soft-scope bugs made the `worst`/`ph_dev`/`eq`
  accumulators local to their loops, so the corresponding checks
  compared the untouched global 0.0 — vacuous passes; the
  accumulators are now declared `global`. The tanh–sinh quadrature
  at 41 nodes was far from its 1e-25 threshold (measured worst
  1.2e-7); the grid 2·125+1 nodes, h = 0.048 brings the worst case
  down to 5.8e-35. 14 checks, all pass (Julia 1.11).
* **`verification/lean/HodgeLaboratory.lean`** — the panel could not
  elaborate at all under the advertised "Lean 4 kernel only, no
  Mathlib" setup: it used the Mathlib notations `ℕ`/`ℤ` as the types,
  which plain core Lean does not equip with arithmetic instances —
  dozens of `failed to synthesize OfNat ℕ …` errors on essentially
  every line.  All type ascriptions now use the core names `Nat` /
  `Int`, and the panel is kernel-checked end-to-end (Lean 4.21,
  exit 0).  Additionally the g = 1 even theta-characteristic example
  asserted `2^1·(2^1+1) = 3`, a false proposition (2·3 = 6) that the
  kernel rejects; it now verifies the correct `2^0·(2^1+1) = 3`,
  matching the closed formula 2^(g−1)(2^g+1) used by every other
  stack.
* **`.github/workflows/ci.yml`** — actions bumped past the Node 20
  deprecation (`checkout@v4` → `v7`, `setup-python@v5` → `v7`,
  `upload-artifact@v4` → `v7`) and the runner is pinned to
  `ubuntu-24.04` ahead of the ubuntu-latest → Ubuntu 26 migration
  (announced for October 2026), silencing the three warnings and
  three notices shown on every run.

### Added

* regression test for the Lean g = 1 Arf count (29 → 30 pytest
  tests).

## [1.1.1] — 2026-09-22

### Fixed

* **`verification/lean/HodgeLaboratory.lean`** — the even
  theta-characteristic count for g = 2 verified the wrong proposition
  `2^0·(2^2+1) = 5`; the closed formula and every other stack (C,
  Rust, the pytest Arf enumeration) give **2^1·(2^2+1) = 10**. The
  Lean panel now verifies the correct identity; a bare duplicate of
  the g = 3 check was removed.
* **`laboratory.py` — multilingual runner** ignored the exit code of
  the compiled backends, so a backend whose self-checks failed was
  still printed as `PASS`. The runner now reports `FAIL (exit code N)`,
  records the verdict in the results collector, and `--run multi`
  exits `1` when any present backend fails — as
  `verification/README.md` always claimed ("CI reads the exit codes").
* **`laboratory.py` — experiment designer** crashed with an unhandled
  `ValueError` on malformed numeric input (e.g. `xy zw` instead of two
  integers), taking down the whole interactive menu. New
  `ask_pair()` helper warns and keeps the default instead; the t*
  designer item additionally validates W, H, a, b ≥ 1 (a zero step
  previously produced a meaningless or crashing lcm).
* **`laboratory.py` — `ask_int()`** printed the fixed message "Enter
  an integer from 20 to 120" for every prompt regardless of the
  prompt's actual range; the message now reflects the real [lo, hi]
  bounds in both languages.
* **`laboratory.py` — baseline cross-check** contained the tautology
  `(36, 28) == (36, 28)`, so the E8 Arf counts were never actually
  recomputed. `--check-baseline` now performs the genuine full
  enumeration of the 64 quadratic forms on (ℤ/2)⁶, compares it with
  the closed formulas, and cross-checks both against the frozen
  baseline; the binary-code (1,1)-walk closure is likewise verified
  against the baseline's `visited = 48`.
* **`laboratory.py` — plot tile T8** relied on a loop variable leaked
  from an earlier tile to pick its level; the DFT tile now sets its
  level explicitly (N = 15).
* **`laboratory.py` — `--run reports`** wrote the reports twice (once
  as the selected block, once unconditionally); the duplicate write
  is removed.
* **`scripts/github_push_termux.sh`** embedded the GitHub token into
  the origin remote URL, persisting it in plain text in
  `.git/config` — contradicting the script's own security note. The
  remote URL is now token-free (and scrubbed if an older version left
  a token behind); the token is passed only via a one-shot push URL
  that lives in memory.
* **`verification/fortran/verify_hodge.f90`** — removed unused
  variables in `sum_census` (warned about by `-Wall`).
* **`pyproject.toml`** — added the missing `[build-system]` section
  and `py-modules = ["laboratory"]`, so `pip install .` now works.

### Added

* six README figures in `docs/assets/` — the hero banner and the
  census, phase-lattice, reflection-ladder, genus, residuals and DFT
  tiles rendered from the laboratory's own plotting pipeline;
* regression tests (24 → 29): designer-input hardening, the
  range-correct `ask_int` message, the multilingual runner's
  fail/pass verdicts, and the Lean g = 2 Arf count;
* README badge anchors fixed (`#5-…`, `#6-…`, `#8-…` slugs) so the
  Protocol/Certificates/Verification badges actually scroll to their
  sections.

## [1.1.0] — 2026-09-22

### Fixed (verification correctness)

* **`verification/julia/verify_hodge.jl`**
  * added the missing `using Printf` — the script previously crashed
    with `UndefVarError` on the first `@sprintf`;
  * fixed the Klein check sign: `105^3 ÷ 343 == -3375` was always
    false (the quotient is `+3375`); the identity now checks
    `j = −105³/343 = −3375 = −15³` and `|Δ|·|j| = 105³`;
  * `setprecision(BigFloat, 70)` set 70 **bits** (~21 decimal digits)
    while the thresholds demanded 1e-60 — the precision is now
    **240 bits (~72 digits)** so every threshold is genuinely
    reachable;
  * the independent quadrature integrated the wrong interval
    (tanh–sinh nodes covered u ∈ [−0.67, 0.67] instead of [0, 1]);
    it now maps t ↦ (1 + tanh(π/2·sinh t))/2 onto [0, 1] with 41
    double-exponential nodes;
  * all transcendental constants now use `big(π)` at working
    precision instead of 16-digit `Float64` promotion.
* **`verification/fortran/verify_hodge.f90`** — same Klein sign bug:
  `105**3/343` was compared against `−3375` and always failed; the
  program exited `1`. Fixed and documented.
* **`laboratory.py`**
  * **V5 chain integrity** was vacuous: the two telescoping sums used
    identical terms `(a1, b1) == (a2, b2)` and cancelled identically,
    so the check proved `0 == 0`. V5 now computes the genuine orbit
    sum Σ_k P(k, k) = (Ω/N)·Σ_k ζ^{k(a+b)}, which must vanish for
    a+b ≢ 0 (mod N) and equal Ω for the positive control a+b = N;
  * **torus stand** contained a tautology `(π/n)⁴ − (π/n)⁴ < 1e-15`
    that verified nothing; replaced by real properties (strict
    monotonicity of the spin-phase family, the δ<1 ⇒ δ_eff<γ
    constraint for N ≥ 4, 2^(2g) = 4 spin structures, and an
    independent 40-digit mpmath recomputation of Δ_Ch);
  * **Klein stand** had dead code (an unused lambda, a `pass` loop,
    a bogus `p2` immediately overwritten); the stand now verifies
    the exact identity Δ·j = c₄³ and the discriminant −7 of the
    quadratic factor;
  * **errata E8 stand** claimed "full enumeration" but used closed
    formulas; it now performs a genuine enumeration of all 2^(2g)
    quadratic forms for g = 1..3 (`arf_enumeration`) and validates
    the closed formulas against it;
  * **binary code stand** computed `friction`/`edges` that were never
    verified and printed unconditional `ok()` lines for the
    reference totals; the stand now verifies t* = 48 by the exact
    E4 formula, the 48-cell closure of the (1,1) walk, and the
    48+212+432+114 = 806 consistency, labelling the monograph
    reference constants honestly;
  * `main_menu` toggled the language with `LANG = 'en' if LANG == 'ru'`
    without a `global LANG` declaration — pressing **L** crashed with
    `UnboundLocalError`;
  * `gcc` backend put `-lm` **before** the source file, which breaks
    symbol resolution on strict linkers; the flag order is fixed and
    build artifacts now go to a private temporary directory instead
    of the repository root;
  * `--dps` had no bounds validation on the CLI (the menu did);
  * the dead first loop in `show_menu` was removed;
  * plot tile T6 used stale residual constants that contradicted the
    baseline JSON (V8/V9); the tile now matches
    `results/baseline_v1_v9.json` exactly.
* **`verification/c/verify_hodge.c`** — removed the dead `while`
  fragment in `census_d` and the unused `line_index`; split the
  misleading combined Klein check into six exact identities; added
  the full N=30 h_d table, the g(7), g(4) genera and the
  t*(12,12,4,6) termination case (38 checks now).
* **`verification/rust/verify_hodge.rs`** — replaced `static mut` +
  `unsafe` counters with `AtomicU32` (compiles warning-free on the
  2024 edition); removed the unused `std::cmp` import and the wasted
  conductor computation; added the h(30,6), h(30,10) and sign-correct
  Klein checks.
* **`verification/lean/HodgeLaboratory.lean`** — replaced the
  misleading "i⁴ = 1" integer example and the artificial
  `432 < 114 + 400` proposition with honest, kernel-checked
  statements; all comments translated to English.

### Added

* `--version`, `--check-baseline` (cross-check of the exact integer
  layer against `results/baseline_v1_v9.json`), validated `--dps`;
* pytest suite `tests/test_laboratory.py` — 24 tests covering the
  census schemes, period identities, V5 orbit sums, the exact K3
  rank, Arf enumeration, termination walks and the baseline;
* CI workflow now runs ruff, the pytest suite, the baseline
  cross-check and the C/Fortran/Rust backends on every push;
* community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `SUPPORT.md`, issue/PR templates, `FUNDING.yml`;
* Zenodo metadata (`.zenodo.json`) with ORCID for automated DOI
  minting on release;
* `scripts/termux_setup.sh` — one-command environment bootstrap for
  Android/Termux;
* English-only documentation set; the Russian monographs (PDF/DOCX/
  LaTeX, unified and per-theorem) remain the authoritative research
  texts in both languages.

### Changed

* Documentation translated to English and substantially expanded;
  the bilingual interactive interface (RU/EN) of the laboratory is
  preserved as a feature;
* type hints and English docstrings throughout `laboratory.py`;
* `--run all` no longer short-circuits: a failing block never hides
  the verdict of the remaining blocks.

## [1.0.0] — 2026-09-21

* Initial public release: unified monograph (RU/EN × PDF/DOCX),
  16 standalone theorem monographs (RU/EN), the single-file
  laboratory with the V1–V9 protocol, stands and certificates A–H,
  five-language verification stack and the Lean 4 kernel panel.

[1.1.2]: https://github.com/wild8highlander/hodge-laboratory/releases/tag/v1.1.2
[1.1.1]: https://github.com/wild8highlander/hodge-laboratory/releases/tag/v1.1.1
[1.1.0]: https://github.com/wild8highlander/hodge-laboratory/releases/tag/v1.1.0
[1.0.0]: https://github.com/wild8highlander/hodge-laboratory/releases/tag/v1.0.0
