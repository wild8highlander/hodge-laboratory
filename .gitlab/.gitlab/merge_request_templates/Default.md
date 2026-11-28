<!-- MR template: Default — general verification / code / docs changes.
     GitLab shows this template automatically for every new merge request. -->

## What does this MR do?

<!-- A short summary: what changed and why. Link related issues with `Closes #N`. -->

## Type of change

- [ ] Verification code (`laboratory.py`, `verification/`)
- [ ] Theorem monograph / certificate content (`theorems/`, `monograph/`)
- [ ] Reports / baseline data (`reports/`, `results/`)
- [ ] Documentation (`README.md`, `docs/`, `INSTRUCTION.md`)
- [ ] Infrastructure (CI/CD, templates, scripts)
- [ ] Other: <!-- describe -->

## Verification performed

<!-- Run locally before submitting; CI will repeat the full matrix. -->

- [ ] `python3 laboratory.py --lang en --run all --no-plots` — protocol V1–V9 ALL PASS
- [ ] `python3 laboratory.py --lang en --check-baseline` — matches `results/baseline_v1_v9.json`
- [ ] `python3 -m pytest tests/ -q` — all tests pass
- [ ] Native backends (only for `verification/` changes): C `gcc` / Rust `rustc` / Julia `julia` / Fortran `gfortran` / Lean `lean`

## Protocol and baseline impact

- Does this change any protocol result (V1–V9), certificate (A–J) or theorem status?
  - [ ] No — results are unchanged
  - [ ] Yes — regenerated artifacts are attached and `results/baseline_v1_v9.json` is updated in this MR

## Checklist

- [ ] `CHANGELOG.md` has an entry under `[Unreleased]`
- [ ] New dependencies are reflected in `requirements.txt` / `requirements-dev.txt` / `pyproject.toml`
- [ ] Monographs rebuilt (`monograph/`, `theorems/*/monograph_*.pdf|docx`) if content changed
- [ ] No private tokens or credentials in the diff
