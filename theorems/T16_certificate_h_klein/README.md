<!-- T16 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T16 · Certificate H + Klein

<p align="center">
  <img src="../assets/heroes/t16.svg" width="800" alt="T16 Cert. H + Klein — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part3.svg" width="640" alt="Part III ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-III_%C2%B7_The_certificates_of_the_progra-F4A261) ![theorem](https://img.shields.io/badge/theorem-16_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Cert. H + Klein** — vol_h = 1125 = √disc; SNF (1,1,5,5,15,15,15,15); j = −3375

## The statement

$$\operatorname{vol}_h=1125,\qquad \mathrm{SNF}=(1,1,5,5,15,15,15,15)$$

The emblem above is alive: it encodes the seven-fold Klein rosette inside a laurel seal — j = −3375 — the same motif that
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

Certificate H seals the K3 arithmetic: vol_h=1125=√disc, the SNF spectrum (1,1,5,5,15,15,15,15), and j=−3375. The monograph produces all three from the quartic layer, and the Klein entry supplies the seven-fold rosette — j=−3375 is the Klein invariant. These are exactly the numbers the SNF engine (T22) reproduces bit-for-bit at the top of the tower.

Part III — The certificates of the program. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t16.svg" width="640" alt="T16 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T15 · Certificate G**](T15_certificate_g/) | [⌂ the index](../README.md) | [**T17 · Hurwitz N=7**](T17_certificate_i_hurwitz/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | Certificates → H; Stands → Klein |
| Lean block | `stand_disc, klein_integers` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t16.png"><img src="../assets/covers/t16.png" width="324" alt="T16 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
seven-fold Klein rosette inside a laurel seal. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t16.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t16.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
