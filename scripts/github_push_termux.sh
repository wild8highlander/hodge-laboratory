#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  HODGE LABORATORY — one-command GitHub publisher
#  Works in: Android (Termux), Linux, macOS
#  Repository: hodge-laboratory
#  Program author: Isaev Iskhak Khamzatovich
#
#  What this script does:
#    1) checks the environment (git, curl, token) and installs gaps;
#    2) initializes git and makes the first commit;
#    3) creates the hodge-laboratory repository via the GitHub API;
#    4) pushes the code;
#    5) enables GitHub Pages (docs/ folder via the Pages API).
#
#  Before running: create a personal access token on GitHub
#    Settings → Developer settings → Personal access tokens →
#    Tokens (classic) → Generate new token
#    with scopes: repo, workflow (delete_repo optional).
#
#  Security note: the token is read interactively (or from GH_TOKEN)
#  and is never echoed and never written to disk (the origin URL stays
#  token-free; the push uses a one-shot URL kept only in memory).
# ═══════════════════════════════════════════════════════════════════

set -u

GOLD='\033[38;5;179m'; GREEN='\033[32m'; RED='\033[31m'; DIM='\033[2m'; OFF='\033[0m'
say()  { printf "%b\n" "${GOLD}▸${OFF} $1"; }
okl()  { printf "%b\n" "${GREEN}✔${OFF} $1"; }
err()  { printf "%b\n" "${RED}✘ $1${OFF}"; exit 1; }

REPO_NAME="${REPO_NAME:-hodge-laboratory}"
REPO_DESC="The Dynamic Principle Laboratory — unified monograph, certificates A–H, closed theorem system, 5-language + Lean verification. Author: Isaev Iskhak Khamzatovich."

# ── 0. Repository directory = script dir /.. ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR" || err "repository directory not found"

say "Repository directory: $REPO_DIR"

# ── 1. Environment ──
if ! command -v git >/dev/null 2>&1; then
    say "git not found — installing…"
    if command -v pkg >/dev/null 2>&1; then
        pkg install -y git || err "install git: pkg install git"
    elif command -v apt >/dev/null 2>&1; then
        sudo apt-get install -y git || err "install git"
    elif command -v brew >/dev/null 2>&1; then
        brew install git || err "install git"
    else
        err "git not found and could not be installed"
    fi
fi
okl "git: $(git --version)"

if ! command -v curl >/dev/null 2>&1; then
    if command -v pkg >/dev/null 2>&1; then pkg install -y curl; fi
    command -v curl >/dev/null 2>&1 || err "curl not found"
fi
okl "curl: found"

# ── 2. Token ──
if [ -z "${GH_TOKEN:-}" ]; then
    printf "%b" "${GOLD}▸ Paste your GitHub Personal Access Token (repo, workflow): ${OFF}"
    read -r GH_TOKEN
fi
[ -n "$GH_TOKEN" ] || err "token is empty"

say "Checking the token…"
USER_LOGIN=$(curl -sS -H "Authorization: token $GH_TOKEN" \
    https://api.github.com/user | grep -m1 '"login"' | sed 's/[^A-Za-z0-9-]//g' | sed 's/login//')
[ -n "$USER_LOGIN" ] || err "token is invalid (could not fetch the login)"
okl "account: $USER_LOGIN"

# ── 3. git init + commit ──
if [ ! -d .git ]; then
    git init -b main >/dev/null 2>&1 || git init >/dev/null 2>&1
fi
git config user.name  "${GIT_NAME:-Isaev Iskhak Khamzatovich}"
git config user.email "${GIT_EMAIL:-$USER_LOGIN@users.noreply.github.com}"

# .gitignore for run artifacts
cat > .gitignore << 'GITEOF'
reports/plots/*.png
reports/*.json.tmp
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.DS_Store
verify_hodge
verify_hodge_f
verify_hodge_c
verify_hodge_rs
*.o
*.mod
.venv/
venv/
GITEOF

git add -A
git commit -m "Hodge Laboratory v1.1.0 — unified monograph, certificates A–H, closed theorem system, 5-language + Lean verification

Author: Isaev Iskhak Khamzatovich. All rights reserved." >/dev/null 2>&1 \
    || say "a commit already exists — skipping"

# ── 4. Create the repository via the API ──
say "Creating the repository $REPO_NAME…"
CREATE=$(curl -sS -H "Authorization: token $GH_TOKEN" -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"$REPO_DESC\",\"private\":false,\"has_issues\":true,\"has_wiki\":false}")
if echo "$CREATE" | grep -q '"full_name"'; then
    okl "repository created: $USER_LOGIN/$REPO_NAME"
elif echo "$CREATE" | grep -q 'already exists'; then
    say "repository already exists — continuing"
else
    err "could not create the repository: $(echo "$CREATE" | head -c 300)"
fi

REMOTE="https://github.com/$USER_LOGIN/$REPO_NAME.git"
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$REMOTE"
else
    # also scrubs any token embedded by an older version of this script
    git remote set-url origin "$REMOTE"
fi

# ── 5. Push ──
say "Pushing the code…"
BRANCH=$(git branch --show-current); [ -n "$BRANCH" ] || BRANCH=main
# The origin URL stays clean (no token — nothing is written to
# .git/config); the token is passed to git only via a one-shot URL that
# lives in memory for the duration of this push (regression: v1.1.1 —
# the token used to be persisted in .git/config in plain text).
PUSH_URL="https://x-access-token:$GH_TOKEN@github.com/$USER_LOGIN/$REPO_NAME.git"
if git ls-remote --exit-code "$PUSH_URL" "refs/heads/$BRANCH" >/dev/null 2>&1; then
    git pull --rebase "$PUSH_URL" "$BRANCH" || say "could not fast-forward — continuing"
fi
git push "$PUSH_URL" "$BRANCH:refs/heads/$BRANCH" \
    || err "push failed — check the token scopes (repo, workflow)"
git branch --set-upstream-to="origin/$BRANCH" "$BRANCH" >/dev/null 2>&1 \
    || say "upstream not set — push next time with: git push origin $BRANCH"
okl "code pushed to origin/$BRANCH"

# ── 6. GitHub Pages (via the Pages API, source = docs folder) ──
say "Enabling GitHub Pages (source: docs/)…"
PAGES=$(curl -sS -X POST \
    -H "Authorization: token $GH_TOKEN" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$USER_LOGIN/$REPO_NAME/pages" \
    -d "{\"source\":{\"branch\":\"$BRANCH\",\"path\":\"/docs\"}}")
if echo "$PAGES" | grep -q '"html_url"\|already exists\|409'; then
    okl "Pages enabled / already enabled"
else
    say "Pages: enable manually if the API replied with an error (Settings → Pages → branch: $BRANCH, /docs)"
fi

# ── Done ──
echo
printf "%b\n" "${GREEN}════════════════════════════════════════════════════${OFF}"
okl "REPOSITORY PUBLISHED"
say "https://github.com/$USER_LOGIN/$REPO_NAME"
say "Pages: https://$USER_LOGIN.github.io/$REPO_NAME/"
say "CI (Actions) starts automatically: protocol V1–V9 + C/Fortran/Rust verification"
printf "%b\n" "${DIM}© 2026 Isaev Iskhak Khamzatovich — all rights reserved${OFF}"
printf "%b\n" "${GREEN}════════════════════════════════════════════════════${OFF}"
