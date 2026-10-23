#!/usr/bin/env python3
"""theorem_of_week.py — rotate the "Theorem of the Week" block in README.md.

Deterministic selection: ISO week number modulo the number of theorems.
The block lives between the machine markers

    <!-- THEOREM-OF-WEEK:START -->
    ... generated content ...
    <!-- THEOREM-OF-WEEK:END -->

and is rewritten in place. Run manually or from the weekly GitHub Actions
workflow (.github/workflows/theorem-of-week.yml). Zero dependencies.

© 2026 Isaev Iskhak Khamzatovich. Part of the hodge-laboratory program.
"""

from __future__ import annotations

import datetime as _dt
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

START = "<!-- THEOREM-OF-WEEK:START -->"
END = "<!-- THEOREM-OF-WEEK:END -->"

# The 20 standalone theorem monographs of the program (theorems/README.md).
THEOREMS: list[dict[str, str]] = [
    {"n": "T01", "folder": "T01_genus_fermat", "title": "Genus of the Fermat curve",
     "result": "g = (N−1)(N−2)/2; g(15) = 91, g(30) = 406 — from Riemann–Hurwitz"},
    {"n": "T02", "folder": "T02_closed_period_form", "title": "Closed period form",
     "result": "P = (1/N)·ζ^(ra+sb)·Ω(a,b); Ω = Γ(a/N)Γ(b/N)/Γ((a+b)/N)"},
    {"n": "T03", "folder": "T03_gamma_identities", "title": "Γ-identities",
     "result": "reflection + Gauss multiplication — the inventory of relations"},
    {"n": "T04", "folder": "T04_riemann_relations", "title": "Riemann as an identity",
     "result": "Ωᵀ = Ω; Im Ω ≻ 0 — identically, without numerical checks"},
    {"n": "T05", "folder": "T05_gamma_normalization", "title": "Γ-normalization",
     "result": "denominator N; fractional parts of π; radicals b_Ch(15), b_Ch(30)"},
    {"n": "T06", "folder": "T06_polarization_indices", "title": "Polarization and indices",
     "result": "J — a polarization of weight 1; block indices computable (Hermite–Smith)"},
    {"n": "T07", "folder": "T07_torus_triple", "title": "The torus triple and the corrections",
     "result": "(4, 1, 4π²); δ = π/4; Δ_Ch = 39.4880 — all from first principles"},
    {"n": "T08", "folder": "T08_k3_stand", "title": "The K3 stand",
     "result": "ρ = 20 = max (Shioda); signature (1,19); det 64; 48 lines"},
    {"n": "T09", "folder": "T09_errata_e8", "title": "Errata E8",
     "result": "36 even (Arf = 0) / 28 odd (Arf = 1) on genus 3 — full enumeration"},
    {"n": "T10", "folder": "T10_certificate_b", "title": "Certificate B",
     "result": "closing the kernel 29 by periods; blind spot 29+2 → 0"},
    {"n": "T11", "folder": "T11_certificate_c", "title": "Certificate C",
     "result": "μ₄-equivariance: 22 = 1+7+7+7; the regular representation x⁴−1"},
    {"n": "T12", "folder": "T12_certificate_d", "title": "Certificate D",
     "result": "the universal μ₄-theorem: [L,P] = 0; functoriality; ℤ[i]"},
    {"n": "T13", "folder": "T13_certificate_e", "title": "Certificate E",
     "result": "flow termination: t* = lcm(W/gcd(a,W), H/gcd(b,H))"},
    {"n": "T14", "folder": "T14_certificate_f", "title": "Certificate F",
     "result": "rationalization: Q = 256 (Cramér); LLL: 4X²−7; negative test 4π²"},
    {"n": "T15", "folder": "T15_certificate_g", "title": "Certificate G",
     "result": "λ(m,n) = (2π)²|mτ−n|²/(Im τ)²; CM fractions; π/15, π/30"},
    {"n": "T16", "folder": "T16_certificate_h_klein", "title": "Certificate H + Klein",
     "result": "vol_h = 1125 = √disc; SNF (1,1,5,5,15,15,15,15); j = −3375"},
    {"n": "T17", "folder": "T17_certificate_i_hurwitz", "title": "Certificate I — the Hurwitz rung N = 7",
     "result": "census 15 = h₇; Vieta (−1,−2,1) in ℤ[ζ]/(Φ₇); Cardano pairing 7/9"},
    {"n": "T18", "folder": "T18_certificate_j_macbeath", "title": "Certificate J — the Macbeath rung N = 9",
     "result": "census 28 = 1 + 27; x³−3x+1; Cardano arguments are roots of unity"},
    {"n": "T19", "folder": "T19_quartic_tower", "title": "The quartic tower of N = 15/30",
     "result": "b_Ch closed forms; minimal quartics; one cyclic field — two rungs"},
    {"n": "T20", "folder": "T20_conductor_census", "title": "The conductor census",
     "result": "two schemes — one genus; the exact Möbius layer"},
]

MONOGRAPH_NOTE = (
    "T21 (certificate K, the cyclic quintic rung N = 11) and T22 (the SNF "
    "engine) are drafted in [`verhodge-lab/monograph/`](verhodge-lab/monograph/) "
    "— slots that continue this numbering."
)


def week_index(today: _dt.date | None = None) -> int:
    """Deterministic selection: ISO week number modulo the theorem count."""
    today = today or _dt.date.today()
    iso = today.isocalendar()
    week = iso[1] + iso[0] * 53  # keep the counter strictly increasing over years
    return week % len(THEOREMS)


def render(idx: int) -> str:
    t = THEOREMS[idx]
    total = len(THEOREMS)
    lines = [
        f"> ### 📖 Theorem of the week — {t['n']}: {t['title']}",
        ">",
        f"> **{t['result']}**",
        ">",
        f"> Full monograph with the complete proof, protocol data and the verification",
        f"> guide: [`theorems/{t['folder']}/`](theorems/{t['folder']}/) ·",
        f"> index of all {total}: [`theorems/README.md`](theorems/README.md).",
        f"> (Rotation {idx + 1} of {total}; {MONOGRAPH_NOTE})",
    ]
    return "\n".join(lines)


def main() -> int:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("theorem_of_week: markers not found in README.md — nothing to do",
              file=sys.stderr)
        return 2
    idx = week_index()
    block = f"{START}\n{render(idx)}\n{END}"
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    new_text = pattern.sub(lambda _: block, text, count=1)
    if new_text == text:
        print(f"theorem_of_week: already up to date (index {idx})")
        return 0
    README.write_text(new_text, encoding="utf-8")
    print(f"theorem_of_week: rotated to index {idx} "
          f"({THEOREMS[idx]['n']} — {THEOREMS[idx]['title']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
