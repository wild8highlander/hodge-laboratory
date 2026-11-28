# Hodge Laboratory — Wiki

**The Dynamic Principle Laboratory** — unified monograph, certificates A–J,
a closed system of theorems, reproducible verification in 5 languages plus
the Lean 4 kernel.
Author: Isaev Iskhak Khamzatovich ([ORCID 0009-0003-7299-0701](https://orcid.org/0009-0003-7299-0701)).

## Entry points

| Where | What |
|---|---|
| [README](https://gitlab.com/wild8highlander1/hodge-laboratory/-/blob/main/README.md) | the bento-grid overview, quick start, all 23 sections |
| [CI-CD Pipeline](https://gitlab.com/wild8highlander1/hodge-laboratory/-/wikis/CI-CD-Pipeline) | how the GitLab pipeline verifies the program |
| [Verification Matrix](https://gitlab.com/wild8highlander1/hodge-laboratory/-/wikis/Verification-Matrix) | languages, backends, tolerances, artifacts |
| [GitLab Setup](https://gitlab.com/wild8highlander1/hodge-laboratory/-/blob/main/GITLAB_SETUP.md) | infrastructure provisioning and manual steps |
| [Pages landing](https://wild8highlander1.gitlab.io/hodge-laboratory/) | the visual site built from `docs/` |

## Quick start (one command)

```bash
python3 laboratory.py --lang en --run all --no-plots
```

Protocol V1–V9, every stand and every certificate runs locally in a few
minutes; the exit code is the verdict. The baseline cross-check:

```bash
python3 laboratory.py --lang en --check-baseline
```

## The laboratory in one paragraph

Geometry supplies only the integer triple **(n, B, λ₀)** — the rotation
order, the carrier index and the spectral threshold. A parameter-free
pipeline builds everything else: character censuses, exact integer
identities, high-precision period comparisons, flow experiments and the
certificate ladder A–J. Every layer is re-checked by independent backends
(Python, C, Rust, Julia, Fortran) and by the Lean 4 kernel for the exact
integer part — see [Verification Matrix](https://gitlab.com/wild8highlander1/hodge-laboratory/-/wikis/Verification-Matrix).

## Contributing

Issues and MRs use the repository templates (`bug_report`,
`verification_failure`, `feature_request`, `theorem_proposal`,
`documentation`; MR: *Default* / *Theorem_or_Monograph*). Any change that
touches the protocol must keep `protocol` jobs green and the baseline
unchanged, or explicitly regenerate `results/baseline_v1_v9.json` with the
new artifacts attached.
