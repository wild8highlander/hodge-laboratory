# Contributing to Hodge Laboratory

Thank you for your interest in improving **Hodge Laboratory — The
Dynamic Principle Laboratory**. This document explains how to report
problems, propose changes, and keep the repository's verification
guarantees intact.

## ⚠️ Read first: the license context

The entire repository is distributed under the **individual exclusive
license of Isaev Iskhak Khamzatovich** (see [`LICENSE`](LICENSE)).
Any use, copying, or derivative work beyond reading and personal
study requires the author's written permission. By submitting a pull
request you acknowledge that your contribution may be incorporated,
modified, or declined at the author's sole discretion.

## 🐞 Reporting bugs

1. Open an issue using the **Bug report** template.
2. Include your environment (OS, Python version, `mpmath` version).
3. Paste the exact command and the failing check names
   (`python3 laboratory.py --run all` prints them).
4. If possible, attach `reports/hodge_report.json` from the failed run.

Reproduction failures of the V1–V9 protocol should use the dedicated
**Reproduction report** template — a verdict other than `ALL PASS` on
unmodified code is always a high-priority report.

## ✅ Before you propose code changes

The repository's central promise is **reproducibility**: every number
printed by the laboratory must be reproducible from a clean checkout.
Any change must keep that promise.

```bash
pip install mpmath numpy matplotlib pytest ruff
python3 laboratory.py --lang en --run all --no-plots   # must end: ALL PASS
python3 laboratory.py --lang en --check-baseline       # must end: PASS ×10
python3 -m pytest tests/ -q                            # all green
ruff check laboratory.py tests/                        # clean
```

If your change touches the verification stack (C, Rust, Julia,
Fortran, Lean), run the corresponding backend locally and confirm
exit code `0`:

| Stack   | Command |
|---------|---------|
| C       | `gcc -O2 -o vh verification/c/verify_hodge.c -lm && ./vh` |
| Rust    | `rustc -O verification/rust/verify_hodge.rs -o vh && ./vh` |
| Julia   | `julia verification/julia/verify_hodge.jl` |
| Fortran | `gfortran -O2 verification/fortran/verify_hodge.f90 -o vh && ./vh` |
| Lean 4  | `lean verification/lean/HodgeLaboratory.lean` |

## 🧭 Change guidelines

* **No randomness, ever.** The protocol is fully deterministic; do not
  introduce seeds, sampling, or time-dependent values into checks.
* **No free parameters.** The dynamic principle pipeline is
  parameter-free by construction — do not add tunable constants.
* **Exact first.** Integer identities must be checked with exact
  arithmetic (`int`, `Fraction`, Lean `native_decide`), not floats.
* **Document thresholds.** Any numeric threshold in a check must
  correspond to the documented baseline in `results/`.
* **Keep the single-file design** of `laboratory.py`; the monograph
  references its menu items by number.
* **Update the docs** (`README.md`, sub-READMEs, `CHANGELOG.md`) in the
  same pull request when behavior or numbers change.

## 🔀 Pull request process

1. Fork (with the author's written permission for substantive changes),
   create a feature branch.
2. Make your change with focused commits.
3. Verify the full checklist above.
4. Fill the pull request template; link the related issue.
5. Wait for CI — all jobs (protocol matrix, C/Fortran/Rust backends,
   lint, tests) must be green.

## 🪜 How to add a new stand to the ladder

The ladder of stands is the spine of the program: torus → K3 → Klein →
N = 7/9 → N = 15/30 (→ N = 11 in progress). A new rung must earn its
place — the geometry is the input, everything else is computed. The
checklist a new stand must satisfy:

1. **Fix the triple.** Decide the integer triple (n, B, λ₀) of the rung
   and justify it geometrically — no tuning knobs, ever.
2. **Exact layer first.** Provide the exact integer facts of the rung
   (genus, census by conductors, discriminant, SNF type) and freeze
   them in `results/baseline_v1_v9.json`.
3. **Implement the stand** as a menu item in `laboratory.py` and mirror
   it in `verification/` (at least one independent stack) — the
   agreement of implementations is the certificate.
4. **Write the theorem monograph** (T-numbered folder in `theorems/`,
   the six-block scheme, RU/EN × PDF/DOCX) and add the row to
   [`theorems/README.md`](theorems/README.md).
5. **Update the ladder table** in `README.md` §4 and the genus chart
   (`docs/assets/svg/genus_ladder.svg` — one rung = one point; the
   `scripts/theorem_of_week.py` rotation list picks it up
   automatically for the Theorem of the Week block).
6. **Keep the Lean queue honest**: if the rung's integer layer is not
   yet machine-checked, add it to the Lean queue list and say so in
   the README — a labeled TODO is acceptable, an unlabeled gap is not.

## 🎨 How to update the visual layer (README, SVG, Mermaid)

The visual system is GitHub-native: **no JavaScript anywhere**, no
external images, no build step. The rules that keep it that way:

* **Animated SVG assets** live in `docs/assets/svg/` (main repo),
  `chess-dynamics-lab/docs/assets/svg/` and `verhodge-lab/figures/svg/`.
  They are hand-written SVG + CSS/SMIL, referenced from the READMEs as
  `<img src="docs/assets/svg/NAME.svg">`. Every asset must:
  - carry `role="img"`, `<title>` and a descriptive `<alt>` at the
    reference site (accessibility is part of the design system);
  - respect `prefers-reduced-motion` (every asset ships a
    `@media (prefers-reduced-motion: reduce)` block);
  - validate as XML — run `python3 scripts/refresh_visuals.py`
    before committing (it also checks that every README image link
    resolves).
* **Mermaid diagrams** are versioned with the text and must render on
  GitHub: `flowchart`, `graph`, `xychart-beta` and `sequenceDiagram`
  are the supported vocabulary. Do not put Mermaid inside HTML table
  cells — GitHub will not render it there.
* **The Theorem of the Week block** in `README.md` lives between the
  machine markers `<!-- THEOREM-OF-WEEK:START/END -->` — edit the
  theorem list only in `scripts/theorem_of_week.py`, never inside the
  markers by hand (the weekly workflow rewrites the block).
* **Colors of the design system**: deep indigo `#0B1026` background,
  cyan `#22D3EE` geometry, violet `#A78BFA` rungs, magenta `#E879F9`
  spectra, gold `#FBBF24` certificates, green `#2EA043` verdicts.
  Keep new assets inside this palette so the pages read as one object.
* **Generated figures** (`docs/assets/genus.png` and friends) are
  regenerated from the frozen baseline by
  `python3 scripts/refresh_visuals.py` (CI runs it monthly and on
  demand) — never hand-edit a generated PNG.

## 📮 Questions

Open a [Discussion](https://github.com/wild8highlander/hodge-laboratory/discussions)
or an issue with the `question` label. See also [`SUPPORT.md`](SUPPORT.md).

---

© 2026 Isaev Iskhak Khamzatovich · All rights reserved
