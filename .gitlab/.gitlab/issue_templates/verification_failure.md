<!-- Issue template: verification failure — a backend / protocol / certificate
     check that FAILED. This is the highest-priority report class of the
     laboratory: it means reproducibility was broken somewhere. -->

## Which check failed?

- Protocol stage: V1–V9 (which one: <!-- V? -->)
- Certificate: A–J (which one: <!-- ? -->)
- Backend / language: Python / C / Rust / Julia / Fortran / Lean 4
- Baseline cross-check (`--check-baseline`)

## Exact command

```bash
# e.g. python3 laboratory.py --lang en --run all --no-plots
```

## Failure output

<!-- Full output including the measured value, the tolerance and the
     delta. Do not truncate the numeric lines. Use code fences. -->

```
```

## Environment

- `python3 laboratory.py --version` (if applicable):
- Compiler / interpreter versions (gcc, rustc, julia, gfortran, lean):
- OS / platform:
- Was `results/baseline_v1_v9.json` modified locally? yes / no

## Impact assessment

- [ ] Only this machine affected (environment-specific)
- [ ] Reproduces on a clean clone
- [ ] Reproduces in CI (link the failing GitLab job)
- [ ] Protocol / certificate verdict changed → reproducibility incident

/label ~verification ~needs-triage
