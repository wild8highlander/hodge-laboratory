<!-- MR template: Theorem / Monograph — for adding or updating theorem
     monographs (T-series), certificates (A–J) or the unified monograph.
     Use the Default template instead for ordinary code changes. -->

## Which collection item does this MR touch?

- Theorem number / directory: `theorems/TXX_.../`
- Certificate: A / B / C / D / E / F / G / H / I / J / none
- Part of the unified monograph: `monograph/`

## Statement of the item

<!-- The precise mathematical statement this monograph establishes or
     updates. Use LaTeX notation; the T-series READMEs are the model. -->

## Verification evidence

- [ ] The computational stand reproduces the statement:
      `python3 laboratory.py --lang en --run all --no-plots` — ALL PASS
- [ ] Lean 4 kernel check is unchanged or extended (`verification/lean/HodgeLaboratory.lean`)
- [ ] Baseline cross-check passes: `python3 laboratory.py --lang en --check-baseline`
- [ ] New/updated plots stored at 600 dpi in `reports/plots/`

## Artifacts rebuilt in this MR

- [ ] `theorems/TXX_.../monograph_RU.pdf` + `.docx`
- [ ] `theorems/TXX_.../monograph_EN.pdf` + `.docx`
- [ ] `theorems/TXX_.../latex/{ru,en}/monograph.tex`
- [ ] `theorems/TXX_.../README.md` (hero SVG, minimap, covers if applicable)

## Checklist

- [ ] `CHANGELOG.md` entry added under `[Unreleased]`
- [ ] `CITATION.cff` / `pyproject.toml` version bumped if this lands in a release
- [ ] Theorem index in the main `README.md` updated (if a new T-number)
- [ ] No baseline drift — the CI `protocol` jobs are green
