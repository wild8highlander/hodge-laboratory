# monograph/ — the document corpus (28 files × RU/EN × PDF/DOCX)

The printed body of the program: the main monograph, twelve theorem monographs and
the research paper «Предел частиц» / The Particle Limit, each in **Russian and
English**, each in **PDF and DOCX** — 56 documents in total.

```text
monograph/
├── pdf/ru/   main_monograph.pdf · t01_board_algebra.pdf … t12_state_space_protocol.pdf · particle_limit.pdf
├── pdf/en/   main_monograph.pdf · t01_board_algebra.pdf … t12_state_space_protocol.pdf · particle_limit.pdf
├── docx/ru/  main_monograph.docx · t01..t12 · particle_limit.docx
├── docx/en/  main_monograph.docx · t01..t12 · particle_limit.docx
├── src/      the generators (python + tex + js) and the content modules
└── build/    the intermediates (git-ignored in releases)
```

## The main monograph — «Динамика шахматных частиц» / Chess Particle Dynamics

12 chapters: the introduction (positions → particles), the board algebra, the move
graphs, mobility, the threat fields, the Lagrangian, the flow and the billiard, the
knight tour, the perft certification, the Zobrist memory, the alpha-beta search, the
mate certificates and the consolidated protocol; 2 appendices (the consolidated
constants table of 19 rows; the reproduction guide including Termux); 5 figures; a
bibliography (Shannon 1950, Zobrist 1970, Knuth–Moore 1975, Thompson 1986, Schwenk
1991, Tromp 2016, hodge-laboratory 2025).

## The research paper — «Предел частиц» / The Particle Limit

`particle_limit.{pdf,docx}` (RU/EN). Generalized chess, EXPTIME and polynomial
myopia: **T13** — a polynomial algorithm for EXPTIME-complete generalized chess
cannot exist (P ⊊ EXPTIME is the Hartmanis–Stearns time hierarchy, so the
"if someone found" scenario is logically inconsistent); **T14** — the particle
horizon: for fixed piece counts the retrograde oracle is polynomial in n
(the generalized analyzer reproduces the frozen 8×8 table bit-exactly), and the
three-layer `ParticleSolver` is a polynomial approximator whose price is
measured on 10,000 won positions (17.56% losses on KRK, 4.38% on KQK, mean
+2.95 plies against the optimum). Experiments E1/E2 live in `complexity/`.

## The theorem monographs T01–T12

Each follows the same six-part structure: problem statement → theorem → proof →
protocol data (tables) → summary of what is proved → verification commands. The
contents and the constants match `results/baseline_c1_c9.json` and the live protocol —
one source of truth.

| Monograph | Subject |
|---|---|
| T01 board_algebra | D4/V4 group action, orbit censuses 10/20, Burnside |
| T02 particle_kinematics | move-graph edge censuses R448/B280/N168/K210/Q728 |
| T03 mobility_census | sums 420/336/560/896/1456, maxima, the 105 ceiling |
| T04 threat_fields | additivity, D4-equivariance, the pawn anomaly 176 |
| T05 lagrangian_energy | E = [M] + μ[m], μ = 0.1; the 20 → 30 certificates |
| T06 flow_termination | t\* = lcm(W/gcd(a,W), H/gcd(b,H)); the damped billiard γ = π⁴/256 |
| T07 knight_discovery | the closed Warnsdorff tour from f5, closure d6→f5 |
| T08 perft_identities | 20/400/8902/197281/4865609 + the divide(3) table |
| T09 zobrist_incrementality | splitmix64 bijectivity, 1562 keys, the birthday bound |
| T10 alphabeta_bounds | correctness, the Knuth–Moore bounds, determinism, ×256.8 |
| T11 mate_certificates | KRK/KQK retrograde bases, Bellman 0, the tactical suite |
| T12 state_space_protocol | the state space, C1–C9 mapping, isolation, 7-language verdicts |

## Production pipelines

- **PDF** (src/gen_tex.py, src/gen_main_tex.py): content modules → LaTeX
  (polyglossia, DejaVu, amsthm-like certificate bars) → `tectonic` → body; covers
  rendered from HTML (Template 03 vertical anchor for the theorems, Template 04
  symmetric for the main) via Playwright → merged as page 0 by pypdf with metadata;
  QA via pdf_qa.
- **DOCX** (src/gen_docx.js, src/gen_docx_main.js): the same content modules →
  docx-js: R5 academic covers (16838 exact wrapper, percentage meta tables), the
  three-section page numbering (cover hidden / TOC roman / body arabic), the TOC field
  + placeholder post-processing (`add_toc_placeholders.py`), footer format patches
  (`patch_docx_footers.py`), LaTeX math → Unicode TextRuns with real super/subscripts;
  checked by `postcheck.py` (0 errors across all 26 files).

Rebuilding:

```bash
cd monograph/src
python3 gen_tex.py            # all 24 theorem PDFs
python3 gen_main_tex.py       # the main monograph PDFs
node gen_docx.js              # all 24 theorem DOCX
node gen_docx_main.js         # the main monograph DOCX
```

© 2026 Isaev Iskhak Khamzatovich. All rights reserved. See [../LICENSE](../LICENSE).
