# CI-CD Pipeline

The GitLab pipeline (`.gitlab-ci.yml`) is the GitLab mirror of the GitHub
Actions suite — same checks, more automation.

```
lint → test → verify → build → security → pages → release
```

## What runs and when

| Trigger | Jobs |
|---|---|
| Push / MR | ruff · protocol ×3 (Python 3.10/3.11/3.12) · pytest (JUnit + coverage) · smoke-batch · verify:c · verify:fortran · verify:rust · verify:julia · verify:lean · SAST · Secret Detection · Code Quality |
| main push | + `security:pip-audit` + `build:sdist-wheel` + `pages` |
| Nightly schedule (02:30 UTC) | everything above + `nightly:protocol-with-plots` + `nightly:polyglot` |
| Tag `v*` | full matrix + `build:sdist-wheel` + `release` |

## Stage details

- **lint** — `ruff check laboratory.py tests/` with the project config from
  `pyproject.toml` (line-length 88, E501 deliberately ignored for banner art).
- **test** — `python3 laboratory.py --lang en --run all --no-plots` plus
  `--check-baseline` on every supported Python; pytest emits
  `reports/junit.xml` (GitLab test widget) and coverage for the badge;
  the batch smoke replays `examples/batch_smoke.json`.
- **verify** — each native backend compiles and runs exactly as the
  README prescribes; Lean uses the `stable` toolchain via elan (cached in
  `.elan/` between runs, no Mathlib — kernel only).
- **build** — sdist + wheel from `pyproject.toml`; the wheel import is
  smoke-tested before artifacts are kept.
- **security** — `pip-audit -r requirements.txt --strict`; findings fail the
  job (fix by pinning, or scope an ignore with `--ignore-vuln ID`).
- **pages** — copies `docs/` verbatim; live at
  <https://wild8highlander1.gitlab.io/hodge-laboratory/>.
- **release** — `release-cli` extracts the changelog section `## [x.y.z]`
  matching the tag and publishes the GitLab Release with asset links.

## Security analyzers

GitLab's built-in SAST, Secret Detection and Code Quality templates run on
every pipeline; results are visible under **Secure → Vulnerability report**.
Document/binary trees are excluded from SAST via `SAST_EXCLUDED_PATHS`
(`monograph,theorems,docs,reports,results`).

## Rules of the game

- `workflow:` rules prevent duplicate pipelines (a branch with an open MR
  runs only the MR pipeline); scheduled pipelines are never skipped.
- Jobs retry twice on runner system failures and are `interruptible`.
- Artifacts (`reports/`, `dist/`) are kept for 1 week (nightly plots: 1 month).
