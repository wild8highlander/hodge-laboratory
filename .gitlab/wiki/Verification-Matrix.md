# Verification Matrix

Every layer of the program is checked by at least one independent
implementation; the exact integer layer is additionally machine-checked by
the Lean 4 kernel. The table is the CI contract: `.gitlab-ci.yml` runs one
job per row (or per column group) on every pipeline.

## Protocol and certificates

| Layer | Implementation | Command | Tolerance |
|---|---|---|---|
| Protocol V1–V9 + stands + certificates A–J | Python (mpmath, numpy) | `python3 laboratory.py --lang en --run all --no-plots` | exact + 1e-25…1e-30 |
| Baseline reproducibility record | Python | `python3 laboratory.py --lang en --check-baseline` | byte-exact verdict vs `results/baseline_v1_v9.json` |
| Batch scenario replay | Python | `--batch examples/batch_smoke.json --batch-out reports/batch_smoke_out.json` | per-scenario |

## Native backends

| Backend | Source | Build / run | What it covers |
|---|---|---|---|
| C | `verification/c/verify_hodge.c` | `gcc -O2 -Wall -o verify_hodge_c … -lm` | exact rank census over Q = 20 |
| Rust | `verification/rust/verify_hodge.rs` | `rustc -O -o verify_hodge_rs …` | exact integer layer |
| Julia | `verification/julia/verify_hodge.jl` | `julia verify_hodge.jl` | 240-bit BigFloat periods, phases, censuses |
| Fortran | `verification/fortran/verify_hodge.f90` | `gfortran -O2 -o verify_hodge_f …` | high-precision period identities |
| Lean 4 | `verification/lean/HodgeLaboratory.lean` | `lean HodgeLaboratory.lean` (kernel only, no Mathlib, no axioms) | exact integer identities (`native_decide` / `decide`) |
| Polyglot hub | `polyglot/` (Python, C, Rust, Go, Julia) | `./polyglot/run_all.sh` | 19 shared checks per language — nightly |

## Where the numbers live

- `results/baseline_v1_v9.json` — the reproducibility record the CI
  cross-checks against;
- `reports/verification_log.txt` — the human-readable run log (an artifact
  of every pipeline, kept for 1 week);
- `reports/plots/` — 600-dpi figures, regenerated nightly with plots
  enabled;
- `monograph/` and `theorems/T01…T22` — RU/EN PDF+DOCX monographs whose
  quoted numbers must match the baseline (see the *documentation* issue
  template).

## Failure handling

A red backend job is a **reproducibility incident**: open the issue with
the `verification_failure` template, paste the full measured/tolerance
output, and state whether `results/baseline_v1_v9.json` was modified.
Protocol-affecting changes must regenerate the baseline in the same MR.
