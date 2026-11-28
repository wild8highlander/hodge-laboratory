# GitLab Setup — Hodge Laboratory

This document describes the **GitLab-native infrastructure** added to this
repository (the mirror of the GitHub original), how it was provisioned with
one command (`push_to_gitlab.sh`), and the few steps that remain manual.

Everything below refers to the project
[`wild8highlander1/hodge-laboratory`](https://gitlab.com/wild8highlander1/hodge-laboratory).

---

## 1. What this package adds

| Feature | File / mechanism | When it runs |
|---|---|---|
| Full CI pipeline | `.gitlab-ci.yml` | every push, MR, schedule, tag |
| Python protocol matrix (3.10 / 3.11 / 3.12) | job `protocol` (`parallel:matrix`) | every pipeline |
| Unit tests + JUnit + coverage | job `pytest` | every pipeline |
| Batch smoke scenario | job `smoke-batch` (`examples/batch_smoke.json`) | every pipeline |
| C verification | job `verify:c` (gcc 14) | every pipeline |
| Fortran verification | job `verify:fortran` (gfortran) | every pipeline |
| Rust verification | job `verify:rust` (rustc 1) | every pipeline |
| Julia verification | job `verify:julia` (julia 1.10) | every pipeline |
| Lean 4 kernel check | job `verify:lean` (elan, cached toolchain) | every pipeline |
| Polyglot hub (Py+C+Rust+Go+Julia) | job `nightly:polyglot` | nightly schedule |
| Full protocol **with** 600-dpi plots | job `nightly:protocol-with-plots` | nightly schedule |
| Dependency audit | job `security:pip-audit` (`pip-audit --strict`) | main push + nightly |
| Secret Detection | GitLab template `Jobs/Secret-Detection` | every pipeline |
| SAST | GitLab template `Jobs/SAST` | every pipeline |
| Code Quality | GitLab template `Jobs/Code-Quality` | every pipeline |
| Package build (sdist + wheel) | job `build:sdist-wheel` | main + tags |
| Static site (docs/ landing) | job `pages` | main branch |
| Releases from CHANGELOG | job `release` (`release-cli`) | tags `v*` |
| MR templates | `.gitlab/merge_request_templates/` | every new MR |
| Issue templates | `.gitlab/issue_templates/` | every new issue |
| Ownership routing | `CODEOWNERS` | every MR |
| Security policy | `SECURITY.md` (GitLab section added) | always |
| Coverage / pipeline / release badges | project badges (API) | always |

### Pipeline stages

```
lint → test → verify → build → security → pages → release
```

`test` and `verify` jobs run in parallel inside a stage, so the whole
matrix (including Lean) finishes in roughly the wall time of its slowest
member. SAST, Secret Detection and Code Quality run in the `test` stage
alongside the Python jobs.

---

## 2. One-command provisioning

```bash
export GITLAB_TOKEN="glpat-…"      # PAT, scope `api`, Maintainer role
./push_to_gitlab.sh
```

The script:

1. commits all packaged files to `main` (or to `--branch NAME` + opens an MR);
2. sets merge settings (pipeline must succeed, source branch removed);
3. protects `main` (push/merge: Maintainers) and tags `v*` (create: Maintainers);
4. adds the **pipeline**, **coverage** and **release** badges;
5. creates the **nightly schedule** (`30 2 * * *` UTC);
6. creates the triage **labels** (bug, enhancement, documentation,
   verification, theorem, security, release, needs-triage);
7. requires **1 approval** on merge requests (best effort — see §5);
8. creates/updates the **wiki** pages: *Home*, *CI-CD Pipeline*,
   *Verification Matrix*.

Options: `--dry-run` (plan only), `--branch NAME` (commit + MR),
`--skip-push` (configure an already-updated repo), `--skip-config`,
`--commit-message "…"`. The token is never echoed and never stored.

---

## 3. Pipelines

| Trigger | What runs |
|---|---|
| Push to any branch | full matrix (no plots), Pages skipped |
| Merge request | full matrix on the MR — widgets: tests, coverage, code quality, security |
| Schedule (nightly 02:30 UTC) | full matrix **+** plots **+** polyglot hub **+** pip-audit |
| Manual (Run pipeline) | full matrix |
| Tag `v*` | full matrix + `build:sdist-wheel` + GitLab Release with notes extracted from `CHANGELOG.md` |

Releases are assembled from the changelog section `## [x.y.z]` matching the
tag `vx.y.z`; if the section is missing, a stub description pointing to
`CHANGELOG.md` is used and the pipeline still succeeds.

**How to cut a release:**

1. bump `__version__` in `laboratory.py`, `version` in `pyproject.toml` and
   `CITATION.cff`;
2. move `[Unreleased]` items into a new `## [x.y.z]` section of `CHANGELOG.md`;
3. commit, then `git tag vx.y.z && git push origin vx.y.z`
   (tags are protected — Maintainers only);
4. the tag pipeline runs the whole matrix and publishes the Release with
   attached links (Pages landing, CHANGELOG).

### Compute minutes

On GitLab.com the Free tier includes 400 compute minutes per month, and this
pipeline is minutes-hungry (Lean downloads a toolchain on first run, Julia
and the Python matrix ×3 add up). Options:

- keep MR pipelines for real changes and let the nightly schedule be the
  heavy run — the `workflow:` rules already avoid duplicate pipelines;
- apply to the **GitLab for Open Source** program (public research projects
  receive a substantially larger minutes pool);
- mark rarely-needed jobs `when: manual` in `.gitlab-ci.yml`.

---

## 4. GitLab Pages

The `pages` job publishes `docs/` **as is** (the landing already contains
`docs/index.html`). Live URL:

> <https://wild8highlander1.gitlab.io/hodge-laboratory/>

First run creates the site automatically; subsequent runs redeploy on every
push to `main`. The deployment record (`commit + timestamp`) is written to
`DEPLOY_INFO.txt` in the site root.

The GitHub Pages mirror (via `.github/workflows/pages.yml`) can keep
running in parallel — the two sites are independent.

---

## 5. Remaining manual steps (UI)

The API cannot do (or cannot do on the Free tier) a handful of things:

1. **MR approval rules beyond the basic setting** — additional approvers or
   per-file approval rules require Premium. Basic *1 approval required* is
   set by the script when the tier allows it
   (**Settings → Merge requests → Merge checks / Approvals**).
2. **Activate the nightly schedule** — if the created schedule shows as
   inactive, press **Play** in **CI/CD → Schedules** (ownership of the
   schedule belongs to the creating user).
3. **Security dashboard review** — after the first default-branch pipeline,
   look at **Secure → Vulnerability report**; SAST findings in the bundled
   web apps (`web/`, `chess-dynamics-lab/web/`) are expected noise from
   vendored JS and can be dismissed or added to an exclusion list
   (`SAST_EXCLUDED_PATHS` in `.gitlab-ci.yml`).
4. **Repository mirroring (optional)** — to keep GitHub and GitLab in sync
   automatically, set a *pull mirror*: **Settings → Repository → Mirroring
   repositories** → GitHub URL + token with `repo` scope, direction *Pull*.
   Push mirroring (GitLab → GitHub) is configured the same way in reverse.
5. **Wiki Home check** — the script creates/updates the pages but the wiki
   needs to be enabled for the project (it is set by the script; verify in
   **Settings → General → Visibility** if pages fail to appear).

### Not enabled on purpose

| Feature | Why |
|---|---|
| Auto DevOps | the repository has its own full pipeline; Auto DevOps would duplicate it |
| Container registry / DAST | no Dockerfile, no running server — offline scientific package |
| Dependency Scanning (analyzer) | no lockfiles in the repo; `pip-audit` covers the declared deps |
| Kubernetes agent | no cluster target |
| Requirement / iteration boards | Premium features, no usage scenario here |

---

## 6. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `verify:lean` fails on first run | elan download was slow or the `stable` toolchain moved. Re-run (toolchain is cached); if it persists, pin the version: replace `--default-toolchain stable` with e.g. `leanprover/lean4:v4.15.0` in `.gitlab-ci.yml` |
| `security:pip-audit` red | a real CVE in `requirements.txt` deps — read the job log, pin the fixed version; if it is a false positive, drop `--strict` for that package via `--ignore-vuln ID` |
| SAST findings in `web/` JS | vendored/minified JS; dismiss in the vulnerability report or extend `SAST_EXCLUDED_PATHS` |
| `protocol` job fails in the matrix but not locally | check `mp.dps` dependence — all three Python versions must produce identical integer layers; artifacts (`reports/`) are attached to the job for diffing |
| Badge shows `unknown` | coverage badge fills after the first `pytest` job on `main`; release badge fills after the first `v*` release |
| Commit rejected | `main` is protected by design — push via MR (`./push_to_gitlab.sh --branch NAME`) |

---

## 7. Security policy

`SECURITY.md` now covers both mirrors: on GitLab, report vulnerabilities as
**confidential issues** (Issues → New issue → *confidential*). Secret
Detection runs on every pipeline and blocks nothing silently — findings are
visible in the vulnerability report.

---

## 8. Feature parity checklist (GitHub → GitLab)

| GitHub feature | GitLab equivalent | Status |
|---|---|---|
| Actions CI matrix | `.gitlab-ci.yml` `protocol` + `verify:*` | ✅ |
| Pages workflow | `pages` job → gitlab.io URL | ✅ |
| PR template | 2 MR templates | ✅ |
| Issue templates (3) | issue templates (5, incl. domain-specific) | ✅ |
| FUNDING.yml | GitLab has no funding widget — `FUNDING.yml` lives on the GitHub mirror | ➖ n/a |
| Security tab (private reporting) | confidential issues + vulnerability report | ✅ |
| Releases (tag-based) | `release` job from `CHANGELOG.md` | ✅ |
| Badges | pipeline / coverage / release project badges | ✅ |
| CODEOWNERS | `CODEOWNERS` (GitLab reads it natively) | ✅ |
| Zenodo / DOI | unchanged (`CITATION.cff`, `.zenodo.json`) | ✅ |
| Wiki | 3 wiki pages provisioned via API | ✅ |
