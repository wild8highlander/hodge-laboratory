<!-- T09 · generated from scripts/theorems_data.py — edit there, regenerate everywhere -->

# T09 · Errata E8

<p align="center">
  <img src="../assets/heroes/t09.svg" width="800" alt="T09 Errata E8 — animated hero card">
</p>

<p align="center">
  <img src="../assets/ribbons/part2.svg" width="640" alt="Part II ribbon">
</p>

<p align="center">

![part](https://img.shields.io/badge/part-II_%C2%B7_The_calibration_stands-457B9D) ![theorem](https://img.shields.io/badge/theorem-9_/_22-8B5CF6) ![formats](https://img.shields.io/badge/formats-EN%2BRU_%C2%B7_PDF%2BDOCX-1284BA) ![proof](https://img.shields.io/badge/proof-complete_%C2%B7_first_principles-2EA043) ![hero+minimap](https://img.shields.io/badge/hero%2Bminimap-animated-E63946)

</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../assets/divider-flow-dark.svg">
    <img alt="divider" src="../assets/divider-flow-light.svg" width="640">
  </picture>
</p>

> **Errata E8** — 36 even (Arf=0) / 28 odd (Arf=1) on genus 3 — full enumeration

## The statement

$$36\ \text{even}\ (\mathrm{Arf}=0)\;/\;28\ \text{odd}\ (\mathrm{Arf}=1)$$

The emblem above is alive: it encodes the eight-fold star lattice of roots and nodes — the E8 root system — the same motif that
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

The errata stand enumerates all 64 theta characteristics on genus 3: 36 even (Arf=0) and 28 odd (Arf=1), each produced and classified by an exhaustive integer walk. The monograph documents the enumeration, cross-checks it against the E8 root-system structure, and seals the count that certificates B–H depend on. It is the program's proof that exhaustive and structural counting agree.

Part II — The calibration stands. Read it in any
order: the monograph is self-sufficient, and every cross-reference below is
navigation, not a prerequisite.

## 🔗 The logical place

<p align="center">
  <img src="../assets/minimaps/t09.svg" width="640" alt="T09 dependency minimap — animated">
</p>

The map is animated: prerequisites flow in from the left, dependents carry
the result onward to the right. The full graph of all 22 theorems lives in
[the collection index](../README.md#-the-dependency-graph).

| ⟵ [**T08 · K3 stand**](T08_k3_stand/) | [⌂ the index](../README.md) | [**T10 · Certificate B**](T10_certificate_b/) ⟶ |
|:---|:---:|---:|

## 🔬 Verification

| Channel | Entry |
|---|---|
| Laboratory | Stands → Errata (enumeration) |
| Lean block | `errata_e8` |
| Exit codes | `0` — accepted · `1` — failure |

Numerically the theorem is verified at 35–70 digits of precision; exactly —
by integer arithmetic or the Lean 4 kernel, whichever the block above names.

## 🖼 The cover

<p align="center">
  <a href="../assets/covers/t09.png"><img src="../assets/covers/t09.png" width="324" alt="T09 engraved cover"></a>
</p>

Academic Engraving: parchment, sepia linework, gold accents — the emblem of
eight-fold star lattice of roots and nodes. Sized for the PDF title page; embed it as
shown in the [collection index](../README.md#-monograph-covers):

```latex
\titlepage
\includegraphics[width=0.72\textwidth]{../assets/covers/t09.png}
```

[![read · EN](https://img.shields.io/badge/read_%C2%B7_EN-monograph_EN.pdf-2EA043)](monograph_EN.pdf) [![read · RU](https://img.shields.io/badge/read_%C2%B7_RU-monograph_RU.pdf-457B9D)](monograph_RU.pdf) [![cover](https://img.shields.io/badge/cover-engraved_emblem-D4A017)](../assets/covers/t09.png)

---

<p align="center">
  <img src="../assets/flow-strip.gif" width="640" alt="animated flow strip">
</p>

<p align="center"><sub>HODGE LABORATORY · THE THEOREM MONOGRAPHS ·
<a href="../README.md#-standalone-theorem-monographs">the collection</a> ·
22 studies · 88 documents</sub></p>
