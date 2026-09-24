#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
#  POLYGLOT CORE — run every available implementation / RU+EN
#  Запускает все доступные реализации ядра и сводит итог.
# ════════════════════════════════════════════════════════════════
set -u
cd "$(dirname "$0")"

GOLD='\033[1;33m'; GREEN='\033[1;32m'; RED='\033[1;31m'; OFF='\033[0m'
say() { printf "%b\n" "${GOLD}▸${OFF} $1"; }

TOTAL=0; OK=0

run() {  # name, command...
    local name="$1"; shift
    say "$name"
    if "$@" > /tmp/polyglot_${name}.log 2>&1; then
        printf "%b\n" "${GREEN}  ✔ $name: PASS${OFF}"
        TOTAL=$((TOTAL+1)); OK=$((OK+1))
    else
        printf "%b\n" "${RED}  ✘ $name: FAIL — детали / details: /tmp/polyglot_${name}.log${OFF}"
        TOTAL=$((TOTAL+1))
    fi
}

# Python
command -v python3 >/dev/null 2>&1 && run python python3 python/verify_core.py

# C
if command -v cc >/dev/null 2>&1 || command -v clang >/dev/null 2>&1 || command -v gcc >/dev/null 2>&1; then
    CC_BIN=cc; command -v cc >/dev/null 2>&1 || CC_BIN=clang; command -v clang >/dev/null 2>&1 || CC_BIN=gcc
    $CC_BIN -O2 -o /tmp/verify_core_c c/verify_core.c -lm 2>/dev/null && run c /tmp/verify_core_c
fi

# Rust
if command -v rustc >/dev/null 2>&1; then
    rustc -O rust/verify_core.rs -o /tmp/verify_core_rs 2>/dev/null && run rust /tmp/verify_core_rs
fi

# Go
if command -v go >/dev/null 2>&1; then
    (cd go && go build -o /tmp/verify_core_go verify_core.go) 2>/dev/null && run go /tmp/verify_core_go
fi

# Julia
if command -v julia >/dev/null 2>&1; then
    run julia julia julia/verify_core.jl
fi

echo
echo "═══════════════════════════════════════════════════════════"
printf " ИТОГ / TOTAL: ${GREEN}%d${OFF}/${TOTAL} языков прошли все 19 проверок / languages passed all 19 checks\n" "$OK"
echo "═══════════════════════════════════════════════════════════"
[ "$OK" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]
