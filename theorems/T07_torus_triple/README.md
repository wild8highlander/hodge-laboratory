<!-- T07 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T07 · The torus triple and the corrections

<p align="center">
  <img src="../assets/heroes/t07.svg" width="800" alt="T07 Torus triple — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part2.svg" width="640" alt="Part II ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-II_%C2%B7_The_calibration_stands-457B9D) ![theorem](https://img.shields.io/badge/theorem-7_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Torus triple** — (4, 1, 4π²); δ=π/4; γ=δ⁴; Δ_Ch = 39.4880 — all from first principles

## The statement

$$\Delta_{\mathrm{Ch}}=\lambda_0-\tfrac{R}{4}+\tfrac{\delta^2}{2}-\tfrac{\delta^5}{k},\qquad \delta=\tfrac{\pi}{4}$$

The emblem above is alive: it encodes the engraved torus with fine hatching and cross-section rings — the same motif that
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

The torus stand calibrates the entire laboratory against numbers known independently: the triple (4, 1, 4π²), δ=π/4, γ=δ⁴, and the Chern discrimant Δ_Ch=39.4880… all emerge from first principles. The monograph walks the arithmetic from the flat metric to the discriminant, producing the reference values that every deeper stand must reproduce before it may claim anything new.

Part II — The calibration stands. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t07.svg" width="640" alt="T07 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T06 · Polarization**](T06_polarization_indices/) | [⌂ the index](../README.md) | [**T08 · K3 stand**](T08_k3_stand/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | Stands → Torus |
| Lean block | `—` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t07.png"><img src="../assets/covers/t07.png" width="324" alt="T07 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
engraved torus with fine hatching and cross-section rings. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t07.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t07.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
