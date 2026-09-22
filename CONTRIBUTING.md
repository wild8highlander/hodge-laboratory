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

## 📮 Questions

Open a [Discussion](https://github.com/wild8highlander/hodge-laboratory/discussions)
or an issue with the `question` label. See also [`SUPPORT.md`](SUPPORT.md).

---

© 2026 Isaev Iskhak Khamzatovich · All rights reserved
