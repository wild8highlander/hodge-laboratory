<!-- Issue template: theorem / certificate proposal — a proposal to add a
     new theorem monograph (T-number), certificate (A–J) or stand. -->

## Proposed item

- Proposed T-number: TXX
- Proposed directory: `theorems/TXX_short_name/`
- Certificate slot (if any): A–J
- Related existing theorems / stands:

## Precise statement

<!-- The full mathematical statement to be verified, in LaTeX notation.
     Include all hypotheses explicitly — no informal "obviously". -->

## Computational evidence available today

- [ ] Reproducible by an existing stand / mode of `laboratory.py` (which: )
- [ ] Needs a new stand (describe inputs, expected output, tolerance)
- [ ] Integer / exact layer (census, divisibility, congruence) — candidate
      for the Lean 4 kernel check
- [ ] High-precision analytic layer — candidate for mpmath / Julia / C

## Deliverables checklist

- [ ] `theorems/TXX_short_name/README.md` in the T-series style
- [ ] LaTeX sources `latex/{ru,en}/monograph.tex`
- [ ] Monographs `monograph_{RU,EN}.pdf` + `.docx`
- [ ] Baseline entries added and cross-checked
- [ ] `CHANGELOG.md` entry

/label ~theorem ~needs-triage
