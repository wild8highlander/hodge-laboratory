# Security Policy

## Supported versions

| Version | Supported | Notes |
|---------|-----------|-------|
| 1.1.x   | ✅ yes    | current `main` |
| 1.0.x   | ❌ no     | superseded — reproducibility fixes and CLI hardening landed in 1.1.0 |

## Scope

Hodge Laboratory is an offline scientific computing package. The
security-relevant surfaces are deliberately narrow:

* `laboratory.py` — reads only its own `results/baseline_v1_v9.json`
  for the `--check-baseline` mode and writes only into `reports/`;
* `scripts/github_push_termux.sh` — handles a GitHub personal access
  token supplied by the user;
* `.github/workflows/*` — CI definitions executed by GitHub.

The verification backends (C, Rust, Julia, Fortran, Lean) perform no
network access, no dynamic code loading, and no file writes outside
their build output.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Use GitHub's private vulnerability reporting
(**Security → Report a vulnerability** on the repository page), or
contact the author through the channels listed in
[`SUPPORT.md`](SUPPORT.md). Include:

1. affected file/line and version (`python3 laboratory.py --version`);
2. a minimal reproduction or proof of concept;
3. the expected and actual behavior.

You will receive an acknowledgement within 7 days. Fixes are released
as patch versions with a `CHANGELOG.md` entry; reporters are credited
in the release notes unless they prefer to stay anonymous.

## Token-handling guidance for the publish script

`scripts/github_push_termux.sh` requires a classic personal access
token with `repo` and `workflow` scopes:

* create the token with the **shortest practical expiry**;
* never commit tokens — the script reads them interactively or from
  the `GH_TOKEN` environment variable and does not echo them;
* the remote URL is rewritten with the token embedded only for the
  lifetime of the push; run `git remote set-url origin ...` without
  credentials afterwards if you share the checkout;
* revoke any token that may have been exposed immediately
  (GitHub → Settings → Developer settings → Personal access tokens).
