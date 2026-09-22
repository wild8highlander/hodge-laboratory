# Summary of the change

<!-- One or two sentences: what does this PR do? -->

## Motivation and context

<!-- Why is this change needed? Link the issue with "Fixes #NN". -->

## What kind of change is this?

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Documentation / typo fix
- [ ] Breaking change (fix or feature that changes published numbers or interfaces)

## Reproducibility checklist

The repository's core promise is that every printed number is
reproducible from a clean checkout. Confirm:

- [ ] `python3 laboratory.py --lang en --run all --no-plots` ends with **ALL PASS**
- [ ] `python3 laboratory.py --lang en --check-baseline` reports **all PASS**
- [ ] `python3 -m pytest tests/ -q` — all green
- [ ] `ruff check laboratory.py tests/` — clean
- [ ] If verification backends were touched: C / Rust / Julia / Fortran / Lean exit `0`
- [ ] Determinism preserved: no seeds, no randomness, no free parameters introduced
- [ ] Docs updated (`README.md`, sub-READMEs, `CHANGELOG.md`) if numbers or behavior changed

## Screenshots / console output (if applicable)

<!-- Paste the tail of the protocol run showing the summary verdict. -->

---

By submitting this pull request I confirm that my contribution may be
incorporated, modified, or declined at the author's sole discretion,
per the repository license ([`LICENSE`](../LICENSE)).
