# 📚 Standalone Theorem Monographs

<div align="center">

**16 self-sufficient studies · 32 PDFs · two languages · complete proofs**

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

---

## 📐 The uniform structure of every monograph

All 32 PDFs follow one scheme:

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
| `monograph_RU.pdf` | the full theorem monograph (Russian) |
| `monograph_EN.pdf` | the full theorem monograph (English) |
| `latex/ru/monograph.tex` | LaTeX source (Russian) |
| `latex/en/monograph.tex` | LaTeX source (English) |

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
| cert. I | Certificates → I; Stands → N=7 | — |
| cert. J | Certificates → J; Stands → N=9 | — |

The certificates I (N = 7, the Hurwitz rung) and J (N = 9, the
Macbeath rung) are exercised by the laboratory and recorded in the
baseline; their standalone theorem monographs (T17, T18) are
scheduled in the roadmap (v1.7).

The exit codes of all implementations: `0` — accepted, `1` — failure.

---

## 📖 How to cite a standalone monograph

```bibtex
@misc{isaev2026t08,
  author = {Isaev, Iskhak Khamzatovich},
  title  = {The K3 Stand: Neron--Severi Rank 20. Standalone Theorem
            Monograph 8/16},
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
