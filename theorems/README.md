# 📚 Standalone Theorem Monographs

<div align="center">

**20 self-sufficient studies · 80 documents · PDF + DOCX · RU/EN · complete proofs**

Each theorem of the program is packaged as a standalone monograph:
statement, complete proof, protocol data, summary of what is proved,
and a verification guide. The monographs can be read, cited, and used
individually — at any time and in any order.

</div>

---

## 🗂 Full index

### Part I. The foundation of the cyclotomic stand N=15/30

| № | Folder | Theorem | Core result |
|---|---|---|---|
| 1 | [`T01_genus_fermat`](T01_genus_fermat/) | **Genus of the Fermat curve** | g = (N−1)(N−2)/2; g(15)=91, g(30)=406 — from Riemann–Hurwitz |
| 2 | [`T02_closed_period_form`](T02_closed_period_form/) | **Closed period form** | P = (1/N)ζ^{ra+sb}Ω_{a,b}; Ω = Γ(a/N)Γ(b/N)/Γ((a+b)/N) |
| 3 | [`T03_gamma_identities`](T03_gamma_identities/) | **Γ-identities** | reflection + Gauss multiplication; the inventory of relations |
| 4 | [`T04_riemann_relations`](T04_riemann_relations/) | **Theorem 1: Riemann as an identity** | Ω^T=Ω; Im Ω ≻ 0 — identically, without numerical checks |
| 5 | [`T05_gamma_normalization`](T05_gamma_normalization/) | **Theorem 2: Γ-normalization** | denominator N; fractional parts of π; radicals b_Ch(15), b_Ch(30) |
| 6 | [`T06_polarization_indices`](T06_polarization_indices/) | **Theorem 3: polarization and indices** | J — a polarization of weight 1; block indices computable (Hermite–Smith) |

### Part II. The calibration stands

| № | Folder | Theorem | Core result |
|---|---|---|---|
| 7 | [`T07_torus_triple`](T07_torus_triple/) | **The torus triple and the corrections** | (4, 1, 4π²); δ=π/4; γ=δ⁴; Δ_Ch = 39.4880 — all from first principles |
| 8 | [`T08_k3_stand`](T08_k3_stand/) | **The K3 stand** | ρ = 20 = max (Shioda); (1,19); det 64; 48 lines; the family ~ h |
| 9 | [`T09_errata_e8`](T09_errata_e8/) | **Errata E8** | 36 even (Arf=0) / 28 odd (Arf=1) on genus 3 — full enumeration |

### Part III. The certificates of the program

| № | Folder | Theorem | Core result |
|---|---|---|---|
| 10 | [`T10_certificate_b`](T10_certificate_b/) | **Certificate B** | closing the kernel 29 by periods; blind spot 29+2 → 0 |
| 11 | [`T11_certificate_c`](T11_certificate_c/) | **Certificate C** | μ₄-equivariance: 22 = 1+7+7+7; the regular representation x⁴−1 |
| 12 | [`T12_certificate_d`](T12_certificate_d/) | **Certificate D** | the universal μ₄-theorem: [L,P]=0; functoriality; ℤ[i] |
| 13 | [`T13_certificate_e`](T13_certificate_e/) | **Certificate E** | flow termination: t\* = lcm(W/gcd(a,W), H/gcd(b,H)) |
| 14 | [`T14_certificate_f`](T14_certificate_f/) | **Certificate F** | rationalization: 2ε < 1/Q²; Q=256; LLL: 4X²−7; negative test 4π² |
| 15 | [`T15_certificate_g`](T15_certificate_g/) | **Certificate G** | λ_{m,n}=(2π)²\|mτ−n\|²/(Im τ)²; CM fractions 16π²/d, 4π²/d; π/15, π/30 |
| 16 | [`T16_certificate_h_klein`](T16_certificate_h_klein/) | **Certificate H + Klein** | vol_h = 1125 = √disc; SNF (1,1,5,5,15,15,15,15); j = −3375 |

### Part IV. The cubic rungs

| № | Folder | Theorem | Core result |
|---|---|---|---|
| 17 | [`T17_certificate_i_hurwitz`](T17_certificate_i_hurwitz/) | **Certificate I: the Hurwitz rung N = 7** | census 15 = h₇; x³+x²−2x−1, Vieta (−1,−2,1) exact in ℤ[ζ]/(Φ₇); Cardano with the exact pairing ∛t·∛t̄ = 7/9; phase π/7 |
| 18 | [`T18_certificate_j_macbeath`](T18_certificate_j_macbeath/) | **Certificate J: the Macbeath rung N = 9** | census 28 = 1 + 27; x³−3x+1, Vieta (0,−3,−1); Cardano arguments are roots of unity: ∛ω = ζ₉; phase π/9 |

### Part V. The exact layer

| № | Folder | Theorem | Core result |
|---|---|---|---|
| 19 | [`T19_quartic_tower`](T19_quartic_tower/) | **The quartic tower of N = 15/30** | b_Ch(15) = (7−√5−√(30−6√5))/8, b_Ch(30) = (9−√5−√(30+6√5))/8; minimal quartics with P₃₀(x) = P₁₅(−x); ββ′ = 12√5 — one cyclic field, two rungs; disc = 1125 |
| 20 | [`T20_conductor_census`](T20_conductor_census/) | **The conductor census** | the triangle c(N) = (N−1)(N−2)/2; lifting lemma + Möbius inversion; self-similarity h_d(N) = h_d(d); 15, 28 = 1+27, 91 = 1+6+84, 406 = 1+6+9+30+84+276 — two schemes, bit-for-bit |

---

## 📐 The uniform structure of every monograph

All 80 documents (PDF and DOCX in both languages) follow one scheme:

```
┌─────────────────────────────────────────────────────┐
│  TITLE: theorem · subtitle · author · number        │
├─────────────────────────────────────────────────────┤
│  1. SETTING — the place of the theorem in the       │
│     program; what exactly is claimed and why        │
│  2. THEOREM/LEMMA — the precise statement in a      │
│     theorem environment                             │
│  3. PROOF — complete, from first principles;        │
│     every formula justified                         │
│  4. PROTOCOL DATA — the exact certificate numbers   │
│     (deviations, ranks, invariants)                 │
│  5. SUMMARY OF WHAT IS PROVED — the result and the  │
│     mechanism (identity / arithmetic / integral)    │
│  6. VERIFICATION — how to reproduce: the            │
│     laboratory.py menu item, the Lean block,        │
│     the exit codes                                  │
└─────────────────────────────────────────────────────┘
```

Files in each folder:

| File | Content |
|---|---|
| `monograph_RU.pdf` | the full theorem monograph (Russian, LaTeX/tectonic) |
| `monograph_RU.docx` | Word edition of the same monograph with native OMML equations (Russian) |
| `monograph_EN.pdf` | the full theorem monograph (English, LaTeX/tectonic) |
| `monograph_EN.docx` | Word edition of the same monograph with native OMML equations (English) |
| `latex/ru/monograph.tex` | LaTeX source (Russian) |
| `latex/en/monograph.tex` | LaTeX source (English) |

The DOCX editions are generated from the same LaTeX sources
(`scripts/build_theorem_docx.py`: pandoc + a styled reference
template), so the two formats never diverge in content — a proof
edited once appears identically in both.

---

## 🧬 How the collection grows

Every newly proved roadmap item becomes a monograph in the same
four-format package, so the collection expands without changing its
shape:

```
1. write  latex/ru/monograph.tex  and  latex/en/monograph.tex
          (the six-block scheme above; theorem environments +
           statusbox/databox/verifybox)
2. build  monograph_RU.pdf / monograph_EN.pdf   (tectonic)
3. build  monograph_RU.docx / monograph_EN.docx
          (scripts/build_theorem_docx.py — pandoc, native OMML,
           styled protocol boxes, RU/EN metadata)
4. register  the row in the index above + the roadmap checkbox
```

Next slots: **T21 = the cyclic quintic rung N = 11** (roadmap v1.5,
certificate K) and **T22 = the SNF spectra of the rungs**
(v1.6) — their content is fixed by the laboratory once the
respective roadmap items are proved.

---

## 🔗 Cross-references

The monographs reference one another by number and the sections of
the unified monograph (`monograph/`). The logical reading path:

```
T01 genus ──→ T02 period ──→ T03 Γ-identities ──→ T04 Riemann
                                                    │
T07 torus ──→ T08 K3 ──→ T10 B ──→ T11 C ──→ T12 D  │
                       │                            ▼
T09 E8                 └──→ T14 F ──→ T15 G ──→ T06 indices
                                                │
T13 E (flow)                                    ▼
                                    T16 H + Klein (closing the arch)
T05 normalization ◄── T02, T03 ◄── the foundation

T17 Hurwitz N=7 ─┐
T18 Macbeath N=9 ─┼── the cubic rungs (certificates I, J)
                  │
T19 quartic tower (15/30) ── the exact layer of v1.2
T20 census ──────────────── the multiplicities behind G/H
```

Every monograph is self-sufficient: reading its proof requires none
of the others — the cross-references are navigation, not dependency.

---

## 🔬 Verification of each theorem

| Theorem | Laboratory entry | Lean block |
|---|---|---|
| 1 genus | V1 census; designer N | `genus_fermat` |
| 2 period | V2/V3/V4; designer | — |
| 3 Γ-identities | V6 | — |
| 4 Riemann | V7 sanity row | — |
| 5 normalization | the N=15/30 stand; the b_Ch plot | `bch_radicals` |
| 6 indices | certificate H1 | `snf_product`, `stand_disc` |
| 7 torus | Stands → Torus | — |
| 8 K3 | Stands → K3 (exact rank 20) | — |
| 9 E8 | Stands → Errata (enumeration) | `errata_e8` |
| 10 B | Certificates → B | — |
| 11 C | Certificates → C | — |
| 12 D | Certificates → D | — |
| 13 E | Certificates → E; designer t* | `termination_lcm` |
| 14 F | Certificates → F | `klein_integers` |
| 15 G | Certificates → G; designer d | — |
| 16 H | Certificates → H; Stands → Klein | `stand_disc`, `klein_integers` |
| 17 I | Certificates → I; Stands → N=7 | — |
| 18 J | Certificates → J; Stands → N=9 | — |
| 19 tower | Designer item 5; batch `bch` (N=15/30) | `bch_radicals` |
| 20 census | Protocol V1; `--check-baseline` | `genus_fermat` |

The exit codes of all implementations: `0` — accepted, `1` — failure.

---

## 📖 How to cite a standalone monograph

```bibtex
@misc{isaev2026t08,
  author = {Isaev, Iskhak Khamzatovich},
  title  = {The K3 Stand: Neron--Severi Rank 20. Standalone Theorem
            Monograph 8/20},
  year   = {2026},
  howpublished = {hodge-laboratory repository},
  url    = {https://github.com/wild8highlander/hodge-laboratory}
}
```

Adjust the number and title per the index above; the repository-level
citation lives in [`../CITATION.cff`](../CITATION.cff) and the main
[`../README.md`](../README.md).

---

## ⚖️ License

Individual exclusive license of Isaev Iskhak Khamzatovich — all
rights to all monographs belong to the author; any use without his
written permission is prohibited. See [`../LICENSE`](../LICENSE).

<div align="center">

© 2026 Isaev Iskhak Khamzatovich · All rights reserved

</div>
