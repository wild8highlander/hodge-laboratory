<!-- T14 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T14 · Certificate F

<p align="center">
  <img src="../assets/heroes/t14.svg" width="800" alt="T14 Certificate F — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part3.svg" width="640" alt="Part III ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-III_%C2%B7_The_certificates_of_the_progra-F4A261) ![theorem](https://img.shields.io/badge/theorem-14_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Certificate F** — rationalization: 2ε < 1/Q²; Q=256; LLL: 4X²−7; negative test 4π²

## The statement

$$Q=256,\qquad 4X^2-7$$

The emblem above is alive: it encodes the draughtsman's compass and set square with a parabola arc — 4X² − 7 — the same motif that
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

Certificate F rationalizes: with Q=256 and 2ε<1/Q², a near-integer is forced to be one. The monograph runs the LLL argument on 4X²−7, exhibits the negative test 4π² — where rationalization correctly refuses — and codifies when the laboratory may round and when it must not. The compass motif is the draughtsman's rule: exactness is a policy, not an accident.

Part III — The certificates of the program. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t14.svg" width="640" alt="T14 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T13 · Certificate E**](T13_certificate_e/) | [⌂ the index](../README.md) | [**T15 · Certificate G**](T15_certificate_g/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | Certificates → F |
| Lean block | `klein_integers` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t14.png"><img src="../assets/covers/t14.png" width="324" alt="T14 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
draughtsman's compass and set square with a parabola arc. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t14.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t14.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
