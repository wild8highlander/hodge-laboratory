#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  HODGE LABORATORY — one-command DOI registration
#  Works in: Android (Termux), Linux, macOS
#
#  Registers the minted Zenodo DOI across the repository in one run:
#    1) the README DOI badge (pending state → the real DOI);
#    2) the `identifiers` block of CITATION.cff.
#
#  Usage:
#     bash scripts/set_doi.sh 10.5281/zenodo.1234567
#
#     # with the concept DOI (all versions):
#     CONCEPT_DOI=10.5281/zenodo.7654321 \
#         bash scripts/set_doi.sh 10.5281/zenodo.1234567
#
#  Where to get the DOI: see README §15 «Zenodo & DOI».
#  The script is idempotent — rerunning it just updates the values.
# ═══════════════════════════════════════════════════════════════════

set -eu

GOLD='\033[38;5;179m'; GREEN='\033[32m'; RED='\033[31m'; DIM='\033[2m'; OFF='\033[0m'
say() { printf "%b\n" "${GOLD}▸${OFF} $1"; }
okl() { printf "%b\n" "${GREEN}✔${OFF} $1"; }
err() { printf "%b\n" "${RED}✘ $1${OFF}"; exit 1; }

DOI="${1:-}"
[ -n "$DOI" ] || err "usage: bash scripts/set_doi.sh 10.5281/zenodo.<ID>"
printf '%s' "$DOI" | grep -Eq '^10\.5281/zenodo\.[0-9]+$' \
    || err "the DOI must look like 10.5281/zenodo.<digits>, got: $DOI"
CONCEPT_DOI="${CONCEPT_DOI:-}"
if [ -n "$CONCEPT_DOI" ]; then
    printf '%s' "$CONCEPT_DOI" | grep -Eq '^10\.5281/zenodo\.[0-9]+$' \
        || err "CONCEPT_DOI must look like 10.5281/zenodo.<digits>"
fi

# shields.io wants the slash escaped as %2F in the badge label
DOI_ESC=$(printf '%s' "$DOI" | sed 's|/|%2F|g')

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR" || err "repository directory not found"

# ── 1. README badge ─────────────────────────────────────────────────
NEW_BADGE="[![DOI](https://img.shields.io/badge/DOI-${DOI_ESC}-1284BA)](https://doi.org/${DOI})"
if grep -q "doi.org/${DOI})" README.md; then
    say "README: the badge already carries ${DOI} — skipped"
else
    awk -v line="$NEW_BADGE" '
        !done && /^\[\!\[DOI\]/ { print line; done = 1; next }
        { print }
    ' README.md > README.md.tmp \
        || err "could not rewrite README.md"
    [ -s README.md.tmp ] || err "README.md rewrite produced an empty file"
    mv README.md.tmp README.md
    okl "README.md — DOI badge updated → ${DOI}"
fi

# ── 2. CITATION.cff identifiers ─────────────────────────────────────
if grep -q 'type: doi' CITATION.cff && grep -q "\"${DOI}\"" CITATION.cff; then
    say "CITATION.cff: the DOI is already registered — skipped"
else
    awk -v doi="$DOI" -v concept="$CONCEPT_DOI" '
        {
            if ($0 ~ /^# A dedicated Zenodo DOI/) {
                print "  - type: doi"
                print "    value: \"" doi "\""
                print "    description: Zenodo DOI for this specific version"
                if (concept != "") {
                    print "  - type: doi"
                    print "    value: \"" concept "\""
                    print "    description: Zenodo concept DOI (all versions)"
                } else {
                    print "# (to add the concept DOI later, rerun with:"
                    print "#  CONCEPT_DOI=10.5281/zenodo.<ConceptID> bash scripts/set_doi.sh " doi ")"
                }
                inblock = 1
                next
            }
            if (inblock && $0 ~ /^#/) next
            inblock = 0
            print
        }
    ' CITATION.cff > CITATION.cff.tmp \
        || err "could not rewrite CITATION.cff"
    [ -s CITATION.cff.tmp ] || err "CITATION.cff rewrite produced an empty file"
    mv CITATION.cff.tmp CITATION.cff
    okl "CITATION.cff — identifiers block updated"
fi

# ── Done ────────────────────────────────────────────────────────────
echo
printf "%b\n" "${GREEN}════════════════════════════════════════════════════${OFF}"
okl "DOI REGISTERED: ${DOI}"
[ -n "$CONCEPT_DOI" ] && okl "CONCEPT DOI:    ${CONCEPT_DOI}"
say "Next steps:"
say "  git add README.md CITATION.cff"
say "  git commit -m 'Register the Zenodo DOI ${DOI}'"
say "  git push"
printf "%b\n" "${DIM}© 2026 Isaev Iskhak Khamzatovich — all rights reserved${OFF}"
printf "%b\n" "${GREEN}════════════════════════════════════════════════════${OFF}"
