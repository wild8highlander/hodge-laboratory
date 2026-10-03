#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
#  POLYGLOT RUNNER — the same core, seven languages
#  Program author: Isaev Iskhak Khamzatovich
#
#  Runs every available backend and prints a summary table.
#  Termux toolchains:  pkg install python clang rust golang nodejs julia openjdk-17
# ═══════════════════════════════════════════════════════════════════════
set -u
cd "$(dirname "$0")"

GOLD='\033[1;33m'; GREEN='\033[1;32m'; RED='\033[1;31m'; DIM='\033[2m'; OFF='\033[0m'
declare -a BACKENDS=()
declare -a VERDICTS=()

run_backend() {
    local name="$1"; shift
    if "$@" > "/tmp/polyglot_${name}.log" 2>&1; then
        local verdict
        verdict=$(grep -o 'verdict: [0-9]*/[0-9]*' "/tmp/polyglot_${name}.log" | tail -1)
        BACKENDS+=("$name"); VERDICTS+=("${verdict:-no verdict}")
        printf "%b\n" "${GREEN}✔${OFF} ${name}: ${verdict:-no verdict}"
    else
        BACKENDS+=("$name"); VERDICTS+=("FAILED")
        printf "%b\n" "${RED}✘${OFF} ${name}: FAILED (see /tmp/polyglot_${name}.log)"
    fi
}

printf "%b\n" "${GOLD}▸${OFF} POLYGLOT CORE — one theorem, seven languages"

# Python (reference)
if command -v python3 >/dev/null 2>&1; then
    run_backend python python3 python/chess_core.py
fi

# C
if command -v cc >/dev/null 2>&1 || command -v clang >/dev/null 2>&1; then
    CC=$(command -v clang || command -v cc)
    if "$CC" -O2 -o /tmp/chess_core_c c/chess_core.c -lm 2>/dev/null; then
        run_backend c /tmp/chess_core_c
    else
        BACKENDS+=("c"); VERDICTS+=("compile error")
        printf "%b\n" "${RED}✘${OFF} c: compile error"
    fi
fi

# Rust
if command -v rustc >/dev/null 2>&1; then
    if rustc -O rust/chess_core.rs -o /tmp/chess_core_rs 2>/dev/null; then
        run_backend rust /tmp/chess_core_rs
    else
        BACKENDS+=("rust"); VERDICTS+=("compile error")
        printf "%b\n" "${RED}✘${OFF} rust: compile error"
    fi
fi

# Go
if command -v go >/dev/null 2>&1; then
    if go build -o /tmp/chess_core_go go/chess_core.go 2>/dev/null; then
        run_backend go /tmp/chess_core_go
    else
        BACKENDS+=("go"); VERDICTS+=("compile error")
        printf "%b\n" "${RED}✘${OFF} go: compile error"
    fi
fi

# JavaScript
if command -v node >/dev/null 2>&1; then
    run_backend javascript node javascript/chess_core.js
fi

# Java
if command -v javac >/dev/null 2>&1; then
    if javac -d /tmp/polyglot_java java/ChessCore.java 2>/dev/null; then
        run_backend java java -cp /tmp/polyglot_java ChessCore
    else
        BACKENDS+=("java"); VERDICTS+=("compile error")
        printf "%b\n" "${RED}✘${OFF} java: compile error"
    fi
fi

# Julia
if command -v julia >/dev/null 2>&1; then
    run_backend julia julia julia/chess_core.jl
fi

echo
echo "─────────────────────────────────────────────"
for i in "${!BACKENDS[@]}"; do
    printf "  %-12s %s\n" "${BACKENDS[$i]}" "${VERDICTS[$i]}"
done
echo "─────────────────────────────────────────────"
