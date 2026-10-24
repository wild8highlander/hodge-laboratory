<!-- T02 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T02 · Closed period form

<p align="center">
  <img src="../assets/heroes/t02.svg" width="800" alt="T02 Period form — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part1.svg" width="640" alt="Part I ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-I_%C2%B7_The_foundation_of_the_cyclotom-E63946) ![theorem](https://img.shields.io/badge/theorem-2_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Period form** — P = (1/N)ζ^{ra+sb}Ω_{a,b}; Ω = Γ(a/N)Γ(b/N)/Γ((a+b)/N)

## The statement

$$\Omega_{a,b}=\frac{\Gamma(a/N)\,\Gamma(b/N)}{\Gamma\!\left(\tfrac{a+b}{N}\right)},\qquad P=\tfrac{1}{N}\,\zeta^{ra+sb}\,\Omega_{a,b}$$

The emblem above is alive: it encodes the engraved circle with chords and radiating arc segments — period measurement — the same motif that
appears on the engraved cover and in the interactive vitrine.

## 🗂 In this folder

| File | Content |
|---|---|
| [`monograph_EN.pdf`](monograph_EN.pdf) | the full monograph — English (LaTeX/tectonic) |
| [`monograph_RU.pdf`](monograph_RU.pdf) | the full monograph — Russian (LaTeX/tectonic) |
| [`monograph_EN.docx`](monograph_EN.docx) | Word edition, native OMML equations — English |
| [`monograph_RU.docx`](monograph_RU.docx) | Word edition, native OMML equations — Russian |
| [`latex/en/monograph.tex`](latex/en/monograph.tex) | LaTeX source — English |
| [`latex/ru/monograph.tex`](latex/ru/monograph.tex) | LaTeX source — Russian |

The DOCX editions are generated from the same LaTeX sources, so the four
documents never diverge in content — a proof edited once appears identically
everywhere. Every monograph follows the uniform six-block scheme: setting,
statement, complete proof, protocol data, summary of what is proved,
and the reproduction guide.

## 📐 The theorem in the program

Every period of the Fermat curve is a phase times one Gamma-ratio: P=(1/N)·ζ^{ra+sb}·Ω_{a,b} with Ω=Γ(a/N)Γ(b/N)/Γ((a+b)/N). The monograph derives the closed form from the beta integral, tabulates the Ω-inventory for N=15/30, and shows why this single formula generates every numerical period the program later verifies to 35–70 digits. It is the closed period form that makes all downstream numerics honest rather than heuristic.

Part I — The foundation of the cyclotomic stand N=15/30. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t02.svg" width="640" alt="T02 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T01 · Genus formula**](T01_genus_fermat/) | [⌂ the index](../README.md) | [**T03 · Γ-identities**](T03_gamma_identities/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | V2/V3/V4; designer |
| Lean block | `—` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t02.png"><img src="../assets/covers/t02.png" width="324" alt="T02 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
engraved circle with chords and radiating arc segments. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t02.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t02.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
