<!-- T05 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T05 · Theorem 2: Γ-normalization

<p align="center">
  <img src="../assets/heroes/t05.svg" width="800" alt="T05 Γ-normalization — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part1.svg" width="640" alt="Part I ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-I_%C2%B7_The_foundation_of_the_cyclotom-E63946) ![theorem](https://img.shields.io/badge/theorem-5_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Γ-normalization** — denominator N; fractional parts of π; radicals b_Ch(15), b_Ch(30)

## The statement

$$b_{\mathrm{Ch}}(15)=\frac{7-\sqrt{5}-\sqrt{30-6\sqrt{5}}}{8}$$

The emblem above is alive: it encodes the nested concentric measuring circles with golden dividers — the same motif that
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

Normalization chooses the denominator N and lands on exact algebra: the fractional parts of π obey b_Ch(15)=(7−√5−√(30−6√5))/8 and b_Ch(30)=(9−√5−√(30+6√5))/8. The monograph derives the radicals, proves the minimal polynomials they satisfy, and wires the results into the Chern-class arithmetic of the torus stand. The b_Ch plot of the laboratory is this theorem drawn as a curve.

Part I — The foundation of the cyclotomic stand N=15/30. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t05.svg" width="640" alt="T05 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T04 · Riemann identity**](T04_riemann_relations/) | [⌂ the index](../README.md) | [**T06 · Polarization**](T06_polarization_indices/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | the N=15/30 stand; the b_Ch plot |
| Lean block | `bch_radicals` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t05.png"><img src="../assets/covers/t05.png" width="324" alt="T05 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
nested concentric measuring circles with golden dividers. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t05.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t05.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
