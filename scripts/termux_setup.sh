#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  HODGE LABORATORY — environment bootstrap
#  Works in: Android (Termux), Linux, macOS
#
#  What this script does:
#    1) installs Python and pip if missing (via pkg/apt/brew);
#    2) installs the laboratory dependencies (mpmath, numpy, matplotlib);
#    3) runs the full V1–V9 protocol once and prints the verdict.
#
#  For publishing the repository to GitHub use the companion script:
#      bash scripts/github_push_termux.sh
# ═══════════════════════════════════════════════════════════════════

set -u

GOLD='\033[38;5;179m'; GREEN='\033[32m'; RED='\033[31m'; DIM='\033[2m'; OFF='\033[0m'
say() { printf "%b\n" "${GOLD}▸${OFF} $1"; }
okl() { printf "%b\n" "${GREEN}✔${OFF} $1"; }
err() { printf "%b\n" "${RED}✘ $1${OFF}"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR" || err "repository directory not found"

say "Repository directory: $REPO_DIR"

# ── 1. Python ──────────────────────────────────────────────────────
if ! command -v python3 >/dev/null 2>&1; then
    say "python3 not found — installing…"
    if command -v pkg >/dev/null 2>&1; then
        pkg install -y python || err "install python: pkg install python"
    elif command -v apt >/dev/null 2>&1; then
        sudo apt-get install -y python3 python3-pip \
            || err "install python3 manually"
    elif command -v brew >/dev/null 2>&1; then
        brew install python || err "install python manually"
    else
        err "no supported package manager found (pkg/apt/brew)"
    fi
fi
okl "python: $(python3 --version)"

# ── 2. Dependencies ────────────────────────────────────────────────
say "Installing laboratory dependencies…"
# Termux note: if matplotlib wheels fail, `pkg install matplotlib`
# provides the system build; numpy/scipy are likewise available.
if ! python3 -m pip install -r requirements.txt; then
    say "pip install failed — trying the Termux system packages…"
    command -v pkg >/dev/null 2>&1 && {
        pkg install -y python-numpy python-matplotlib || true
    }
    python3 -m pip install mpmath || err "cannot install mpmath"
fi
okl "dependencies installed"

# ── 3. Run the protocol once ───────────────────────────────────────
say "Running the full V1–V9 protocol (deterministic, ~2 s)…"
NO_PLOTS_FLAG=""
python3 -c "import matplotlib" 2>/dev/null || NO_PLOTS_FLAG="--no-plots"
python3 laboratory.py --lang en --run all --no-plots $NO_PLOTS_FLAG \
    || err "the protocol reported FAILURES — see the output above"
okl "verdict: ALL CHECKS PASSED"

# ── Done ───────────────────────────────────────────────────────────
echo
printf "%b\n" "${GREEN}════════════════════════════════════════════════════${OFF}"
okl "ENVIRONMENT READY"
say "Interactive laboratory:  python3 laboratory.py"
say "Full protocol:           python3 laboratory.py --run all"
say "Baseline cross-check:    python3 laboratory.py --check-baseline"
say "Unit tests:              python3 -m pytest tests/ -q  (needs pytest)"
printf "%b\n" "${DIM}© 2026 Isaev Iskhak Khamzatovich — all rights reserved${OFF}"
printf "%b\n" "${GREEN}════════════════════════════════════════════════════${OFF}"
