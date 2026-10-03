#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  CHESS-DYNAMICS-LAB — one-command GitHub publication
#  Works in: Android (Termux), Linux, macOS
#
#  Creates the repository under your GitHub account and pushes the
#  whole laboratory in a single run:
#    1) checks the environment (git, gh or a personal access token);
#    2) inits the repo, sets the identity, makes the initial commit;
#    3) creates the GitHub repository wild8highlander/chess-dynamics-lab;
#    4) pushes main + tags.
#
#  Usage:
#     bash scripts/termux_push.sh
#
#  Environment:
#     GH_USER    — GitHub account (default: wild8highlander)
#     GH_REPO    — repository name  (default: chess-dynamics-lab)
#     GH_TOKEN   — personal access token (classic, repo scope) OR
#                  install the gh CLI and run `gh auth login` first
# ═══════════════════════════════════════════════════════════════════

set -eu

GOLD='\033[1;33m'; GREEN='\033[1;32m'; RED='\033[1;31m'; OFF='\033[0m'
say() { printf "%b\n" "${GOLD}▸${OFF} $1"; }
okl() { printf "%b\n" "${GREEN}✔${OFF} $1"; }
err() { printf "%b\n" "${RED}✘ $1${OFF}"; exit 1; }

GH_USER="${GH_USER:-wild8highlander}"
GH_REPO="${GH_REPO:-chess-dynamics-lab}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR" || err "repository directory not found"

# ── 1. environment ──────────────────────────────────────────────────
command -v git >/dev/null 2>&1 || err "git is not installed (Termux: pkg install git)"
say "git: $(git --version)"

GH=""
if command -v gh >/dev/null 2>&1; then
    GH="gh"
    say "gh CLI found: $(gh --version | head -1)"
    gh auth status >/dev/null 2>&1 || err "gh is not authenticated — run: gh auth login"
else
    [ -n "${GH_TOKEN:-}" ] || err "neither gh CLI nor GH_TOKEN found.\n   install gh and run 'gh auth login', or export GH_TOKEN=<personal access token>"
    say "using GH_TOKEN (classic token, repo scope)"
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "$GH_USER"
git config user.email >/dev/null 2>&1 || git config user.email "${GH_USER}@users.noreply.github.com"

# ── 2. initial commit ───────────────────────────────────────────────
if [ ! -d .git ]; then
    git init -b main
    say "git repository initialized (branch main)"
fi
git add -A
if git diff --cached --quiet; then
    say "nothing to commit — the working tree is clean"
else
    git commit -m "chess-dynamics-lab v1.0.0: dynamics.py (C1-C9), polyglot core (7 languages), engine package, monographs T01-T12 + main (RU/EN, PDF/DOCX), web laboratory, docs, CI"
    okl "initial commit created"
fi

# ── 3. create the remote repository ─────────────────────────────────
if [ "$GH" = "gh" ]; then
    if gh repo view "$GH_USER/$GH_REPO" >/dev/null 2>&1; then
        say "repository $GH_USER/$GH_REPO already exists — reusing it"
        git remote remove origin 2>/dev/null || true
        git remote add origin "https://github.com/$GH_USER/$GH_REPO.git"
    else
        gh repo create "$GH_USER/$GH_REPO" --public --source=. --remote=origin --push=false \
            || err "could not create the repository via gh"
        okl "repository created: https://github.com/$GH_USER/$GH_REPO"
    fi
else
    say "creating the repository via the REST API…"
    STATUS=$(curl -s -o /tmp/gh_repo.json -w '%{http_code}' \
        -H "Authorization: token $GH_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        https://api.github.com/user/repos \
        -d "{\"name\":\"$GH_REPO\",\"private\":false,\"has_wiki\":false}" || true)
    [ "$STATUS" = "201" ] || [ "$STATUS" = "422" ] \
        || err "GitHub API returned $STATUS (see /tmp/gh_repo.json)"
    [ "$STATUS" = "201" ] && okl "repository created" || say "repository already exists (422) — reusing"
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://x-access-token:${GH_TOKEN}@github.com/${GH_USER}/${GH_REPO}.git"
fi

# ── 4. push ─────────────────────────────────────────────────────────
say "pushing main…"
git push -u origin main
okl "pushed: https://github.com/$GH_USER/$GH_REPO"
say "watch the CI run: https://github.com/$GH_USER/$GH_REPO/actions"
okl "done. The CI will verify the protocol and the polyglot battery in 7 languages."
