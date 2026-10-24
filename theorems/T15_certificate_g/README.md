<!-- T15 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T15 · Certificate G

<p align="center">
  <img src="../assets/heroes/t15.svg" width="800" alt="T15 Certificate G — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part3.svg" width="640" alt="Part III ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-III_%C2%B7_The_certificates_of_the_progra-F4A261) ![theorem](https://img.shields.io/badge/theorem-15_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Certificate G** — λ_{m,n}=(2π)²|mτ−n|²/(Im τ)²; CM fractions 16π²/d, 4π²/d; π/15, π/30

## The statement

$$\lambda_{m,n}=(2\pi)^2\,\frac{\lvert m\tau-n\rvert^2}{(\operatorname{Im}\tau)^2}$$

The emblem above is alive: it encodes the surveyor's lattice with marked diagonal distances — λ_{m,n} — the same motif that
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

Certificate G computes the spectral gap exactly: λ_{m,n}=(2π)²|mτ−n|²/(Im τ)², with CM fractions 16π²/d and 4π²/d — and the π/15, π/30 of the 15/30 stand. The monograph derives the formula, tabulates the gap ladder, and fixes the lattice metric that the SNF layer inherits. The surveyor's lattice of the motif is the distance structure made visible.

Part III — The certificates of the program. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t15.svg" width="640" alt="T15 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T14 · Certificate F**](T14_certificate_f/) | [⌂ the index](../README.md) | [**T16 · Cert. H + Klein**](T16_certificate_h_klein/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | Certificates → G; designer d |
| Lean block | `—` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t15.png"><img src="../assets/covers/t15.png" width="324" alt="T15 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
surveyor's lattice with marked diagonal distances. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t15.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t15.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
