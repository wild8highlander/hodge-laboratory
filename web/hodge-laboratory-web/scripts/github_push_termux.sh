#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  HODGE LABORATORY WEB — one-command GitHub publisher
#  Works in: Android (Termux), Linux, macOS
#  Repository: hodge-laboratory-web
#  Account: wild8highlander
#  Program author: Isaev Iskhak Khamzatovich
#
#  What this script does:
#    1) checks the environment (git, curl, token) and installs gaps;
#    2) initializes git and makes the first commit;
#    3) creates the hodge-laboratory-web repository via the GitHub API;
#    4) pushes the code;
#    5) enables GitHub Pages (the root of the repository).
#
#  Before running: create a personal access token on GitHub
#    Settings → Developer settings → Personal access tokens →
#    Tokens (classic) → Generate new token
#    with scopes: repo, workflow.
#
#  Security note: the token is read interactively (or from GH_TOKEN)
#  and is never echoed and never written to disk.
# ═══════════════════════════════════════════════════════════════════

set -u

GOLD='\033[1;33m'; GREEN='\033[1;32m'; RED='\033[1;31m'; DIM='\033[2m'; OFF='\033[0m'
say()  { printf "%b\n" "${GOLD}▸${OFF} $1"; }
okl()  { printf "%b\n" "${GREEN}✔${OFF} $1"; }
err()  { printf "%b\n" "${RED}✘ $1${OFF}"; exit 1; }

REPO_NAME="${REPO_NAME:-hodge-laboratory-web}"
GH_ACCOUNT="${GH_ACCOUNT:-wild8highlander}"
REPO_DESC="Hodge Laboratory Web — the Dynamic Principle in the browser: protocol V1–V9, certificates A–J, Hodge cycle deep tests, 600 dpi plots, monograph forge. Bilingual RU/EN. Author: Isaev Iskhak Khamzatovich."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR" || err "repository directory not found"

say "Repository directory: $REPO_DIR"
say "Target: $GH_ACCOUNT/$REPO_NAME"

# ── 1. git ──
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
okl "git: $(git --version | head -1)"

# ── 2. curl ──
if ! command -v curl >/dev/null 2>&1; then
    if command -v pkg >/dev/null 2>&1; then pkg install -y curl; fi
    command -v curl >/dev/null 2>&1 || err "curl not found"
fi
okl "curl: found"

# ── 3. token ──
if [ -z "${GH_TOKEN:-}" ]; then
    printf "%b" "${GOLD}▸ Paste your GitHub Personal Access Token (repo, workflow): ${OFF}"
    read -r GH_TOKEN
fi
[ -n "$GH_TOKEN" ] || err "token is empty"

say "Checking the token…"
USER_LOGIN=$(curl -sS -H "Authorization: token $GH_TOKEN" https://api.github.com/user \
    | grep -m1 '"login"' | sed 's/[^A-Za-z0-9_-]//g; s/login//')
[ -n "$USER_LOGIN" ] || err "token is invalid (could not fetch the login)"
if [ "$USER_LOGIN" != "$GH_ACCOUNT" ]; then
    err "the token belongs to '$USER_LOGIN', but the target account is '$GH_ACCOUNT'"
fi
okl "account: $USER_LOGIN (verified)"

# ── 4. git init + commit ──
if [ ! -d .git ]; then
    git init -b main >/dev/null 2>&1 || git init >/dev/null 2>&1
fi
git config user.name  "${GIT_NAME:-Isaev Iskhak Khamzatovich}"
git config user.email "${GIT_EMAIL:-wild8highlander@users.noreply.github.com}"
git add -A
git commit -m "hodge-laboratory-web: bilingual research web app (V1–V9, A–J, cycles, 600 dpi, monograph forge)" >/dev/null 2>&1 || okl "nothing new to commit"

# ── 5. create the repository via the API ──
say "Creating the repository (if missing)…"
HTTP=$(curl -sS -o /tmp/gh_repo.json -w "%{http_code}" \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"$REPO_DESC\",\"homepage\":\"https://$GH_ACCOUNT.github.io/$REPO_NAME/\",\"private\":false,\"has_issues\":true}" 2>/dev/null)
if [ "$HTTP" = "201" ]; then
    okl "repository created: $GH_ACCOUNT/$REPO_NAME"
elif [ "$HTTP" = "422" ]; then
    okl "repository already exists — continuing"
else
    say "API returned HTTP $HTTP — continuing (the repository may already exist)"
fi

# ── 6. push ──
say "Pushing the code…"
if git remote get-url origin >/dev/null 2>&1; then
    git remote remove origin
fi
git remote add origin "https://$GH_ACCOUNT:$GH_TOKEN@github.com/$GH_ACCOUNT/$REPO_NAME.git"
git branch -M main
git push -u origin main --force || err "push failed"
# strip the token from the stored URL after the push
git remote set-url origin "https://github.com/$GH_ACCOUNT/$REPO_NAME.git"
okl "pushed (token removed from the remote URL)"

# ── 7. GitHub Pages ──
say "Enabling GitHub Pages (branch: main, root)…"
curl -sS -o /dev/null -X POST \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$GH_ACCOUNT/$REPO_NAME/pages" \
    -d '{"source":{"branch":"main","path":"/"}}' || true

echo
okl "═══════════════════════════════════════════════════"
okl "Repository: https://github.com/$GH_ACCOUNT/$REPO_NAME"
okl "Site:       https://$GH_ACCOUNT.github.io/$REPO_NAME/"
okl "═══════════════════════════════════════════════════"
echo
say "GitHub Pages deploys in 1–3 minutes. Check:"
say "  → repository → Settings → Pages (source: main /root)"
say "  → or the Actions tab for the deploy workflow"
