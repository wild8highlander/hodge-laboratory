# Chess Particle Dynamics — A Certifiable Laboratory

**`chess-dynamics-lab` · 2026**

*Author and copyright holder: **Isaev Iskhak Khamzatovich** (Исаев Исхак Хамзатович)*
*Individual exclusive license — see [LICENSE](LICENSE). Derived from the methodology of the [hodge-laboratory](https://github.com/wild8highlander/hodge-laboratory) program.*

A chess game is described here as the **dynamics of a system of particles**. Every
piece is a particle: it emits a **threat field** (the potential layer **K3**), carries a
**Lagrangian energy** (the energy layer **TORUS**) and moves in a **discrete flow with
memory and terminations** (the flow layer **KLEIN**). Every metaphor of classical chess
language receives an exact definition, every definition becomes a theorem, and every
theorem becomes an executable check of the protocol **C1–C9** — reproducible by a single
command on any machine, from a server to an Android phone under Termux.

```text
verdict: ALL CHECKS PASSED   (protocol C1–C9)
verdict: 10/10               (polyglot battery C1–C10, seven languages)
```

---

## Contents

1. [What is inside](#1-what-is-inside)
2. [Quick start](#2-quick-start)
3. [The three-layer particle model](#3-the-three-layer-particle-model)
4. [The twelve theorems T01–T12](#4-the-twelve-theorems-t0112)
5. [The protocol C1–C9](#5-the-protocol-c1c9)
6. [The polyglot core: seven languages](#6-the-polyglot-core-seven-languages)
7. [The engine package](#7-the-engine-package)
8. [The Outcome Dynamics program (epochs I–VIII)](#8-the-outcome-dynamics-program-epochs-i-viii)
9. [The web laboratory](#9-the-web-laboratory)
10. [Monographs (PDF/DOCX × RU/EN)](#10-monographs-pdfdocx--ruen)
11. [Frozen constants](#11-frozen-constants)
12. [Repository layout](#12-repository-layout)
13. [Publishing your fork](#14-publishing-your-fork)
14. [Development and CI](#15-development-and-ci)
15. [Citation and license](#16-citation-and-license)

---

## 1. What is inside

| Component | Description |
|---|---|
| [`dynamics.py`](dynamics.py) | **The single-file laboratory**: 0x88 board with full legal generation (castling, en passant, promotion), the three-layer particle model, retrograde KRK/KQK bases, alpha-beta search, the protocol C1–C9, plots, CLI |
| [`large_board_lab.jl`](large_board_lab.jl) | **The Julia large-board laboratory (single file, zero packages)**: the generalized n×n particle dynamics verified on big matrices up to **112×112** — interactive RU/EN menu, T1–T9 test battery, the MAIN test issuing the **partial-policy verdict** (an ensemble of named policies: particle / pressure / mobility / material / random, per-policy verdicts + consensus + coverage), exact retrograde oracle, four 600-dpi charts (PNG+SVG) written by a built-in PNG encoder, reports in TXT/JSON/CSV/MD |
| [`engine/`](engine/README.md) | The importable package: `particles.py` (three-layer facade), `mate_solver.py`, `game_player.py` (with `--selfplay`), `analyzer.py` |
| [`outcome/`](outcome/README.md) | **The Outcome Dynamics program (epochs I–VIII)**: the exact WDL/DTM oracle over the frozen certificates, the 40-coordinate phase-space feature extractor, deterministic dataset machinery, the zero-dependency tablebase distillation benchmark and **Outcome Field v0.1** — P(W/D/L) + entropy + criticality + the counterfactual move-impact surface |
| [`polyglot/`](polyglot/README.md) | The same 10-check battery **C1–C10 in seven languages** — Python, C, Rust, Go, Julia, JavaScript, Java — printing a byte-identical verdict `10/10` |
| [`tests/`](tests/README.md) | 181 pytest tests over the core, the engine, the frozen baseline, the vortex layer, the E5 solution ladder and the outcome program |
| [`results/`](results/README.md) | The frozen certificates: KRK/KQK/KNK/KPK DTM bases, the knight tour, `baseline_c1_c9.json`, the E4 vortex report, the T17 trap census, the E5 solution-level ladder, the outcome distillation certificate and the frozen outcome model |
| [`vortex/`](vortex/README.md) | **T16 — the vortex-value correspondence**: the DTM certificate re-encoded as a planar flow (vortices + descent currents); the outcome of a perfect game becomes the topology of particle trajectories — E4: 1800/1800 agreement, capture separation 1.000/0.000 |
| [`reports/`](reports/README.md) | The protocol plots (600 dpi) |
| [`monograph/`](monograph/README.md) | **14 titles / 56 files**: the main monograph + 12 theorem monographs + the research paper «The Particle Limit», each in RU and EN, each in PDF and DOCX |
| [`web/chess-particles/`](web/README.md) | The web laboratory: glowing particle pieces on a canvas board, the threat-field heatmap and its Θ-flow animation, the Lagrangian panel, the t\* billiard, and an **honestly computed** browser protocol |
| [`docs/`](docs/README.md) | The GitHub Pages landing |
| [`scripts/`](scripts/README.md) | `termux_push.sh` — one-command publication of the repository |
| [`.github/workflows/`](.github/workflows/ci.yml) | CI: the protocol on three Python versions + the polyglot battery in all seven languages + web sanity; Pages deployment |

---

## 2. Quick start

The laboratory has **zero dependencies** — the core runs on the Python standard
library alone (matplotlib is optional, only for the plots).

```bash
git clone https://github.com/wild8highlander/chess-dynamics-lab.git
cd chess-dynamics-lab

python3 dynamics.py --report          # the full protocol C1–C9 + the verdict
python3 dynamics.py --run C5          # one check (perft identities)
python3 dynamics.py --run C5 --deep   # adds perft(5) = 4865609 and the divide table
python3 dynamics.py --plots reports/plots   # regenerate the 600 dpi plots
python3 -m pytest tests/ -q           # 181 tests
```

Position analysis, mate solving and self-play:

```bash
python3 dynamics.py --analyze "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3" --depth 4
python3 dynamics.py --mate "kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1"   # the Morphy mate: key a1a6
python3 engine/game_player.py --selfplay --depth 4               # a deterministic game
```

The Outcome Dynamics program (epochs I–VIII, see section 8):

```bash
python3 -m outcome analyze "R5k1/8/6K1/8/8/8/8/8 b - - 0 1" --moves
python3 -m outcome export --kind krk --limit 20000 --out results/outcome/dataset_krk.csv
python3 -m outcome train --per-kind 20000 --epochs 40 --ablation
python3 -m outcome evaluate                                        # re-check the frozen model
python3 -m outcome report --smoke                                  # the CI-sized experiment
python3 -m outcome nonlinear --per-kind 20000                      # E11: the nonlinear KPK head
python3 -m outcome interact --per-kind 20000                       # E13: interaction hinges on the residual corpus
python3 -m outcome nonlinear --kind krk --per-kind 20000           # E14: the KRK specialist
python3 -m outcome games data/games                                # E12: real games through Epoch IV
python3 -m outcome adjudicate data/games                           # E15: whole-game referee (the E9 model)
```

### 2.1 The Julia large-board laboratory (112×112)

`large_board_lab.jl` is the big-matrix companion of `dynamics.py`: the same
three-layer particle dynamics (K3 threat fields + TORUS energy + KLEIN
determinism) and the same retrograde oracle, generalized to n×n boards and
verified at sizes the 0x88 core cannot reach. It needs **only Julia ≥ 1.6** —
no packages, no downloads; the PNG writer (zlib fixed-Huffman deflate), the
rasterizer and the bitmap font are inside the file.

```bash
julia large_board_lab.jl                 # interactive menu (RU/EN, switch with L)
julia large_board_lab.jl --lang=en       # headless full laboratory run
julia large_board_lab.jl --selftest      # 1-minute sanity battery
julia large_board_lab.jl --test=main --playouts=128   # the MAIN test only
julia large_board_lab.jl --test=main --policy=all     # all five policies
julia large_board_lab.jl --test=check --expect=draw   # explicit draw check
julia large_board_lab.jl --quick         # fast smoke preset
```

Menu map: **1** full laboratory run · **2–6** individual tests T1–T5 ·
**7** the MAIN test — the **partial-policy verdict**: which outcome the
dynamics implies at n = 112 (draw / WHITE WIN / BLACK WIN). The default
ensemble `PARTICLE + PRESSURE + MOBILITY` plays paired playouts on identical
sampled starts; the verdict reports per-policy × scenario shares, per-policy
pooled verdicts with tiers (`F` forced — Wilson CI floor > 50%, `L` leaning —
plurality ≥ 75%, `I` inconclusive), a consensus class (unanimous / majority /
split) and honest coverage (sampled starts and plies vs the scenario
state-space estimate). Evidence ladder per `complexity/SOLVING_CHESS.md`:
FULL > WEAK > ULTRA-WEAK > **PARTIAL POLICY** — the test never claims more
than the last rung · **8** explicit outcome check (particle policy) ·
**9** the flow showcase · **C** every parameter (board size, playouts,
μ/λ weights, policy ensemble, seed, DPI, figure size, output dir) ·
**L** language.

Every run writes a folder `results/large_board_lab/run_<timestamp>/` with the
text log, `report.json` (the `main_test` block carries `verdict_class`,
`consensus`, per-policy `policies[]` and `coverage`), `main_playouts.csv`,
`policy_matrix.csv` (policy × scenario matrix), `trap_census.csv`,
`summary.md` and four charts in two formats each (`chart1_scaling`,
`chart2_outcomes` — per-policy bars, `chart3_flow_112x112`,
`chart4_dtm_growth` — PNG at 600 dpi + SVG vector).
A sample frozen run ships in `results/large_board_lab/`.

Expected output of `--report` (times are for a laptop; a phone is several times slower):

```text
  C1 board algebra: V4/D4 orbit census + Burnside            [PASS]  (0.02s)
  C2 particle kinematics: move-graph census                  [PASS]  (0.01s)
  C3 mobility census: closed forms and maxima                [PASS]  (0.00s)
  C4 flow termination t* + damped billiard                   [PASS]  (0.01s)
  C5 perft identities 20/400/8902/197281                     [PASS]  (1.9s)
  C6 threat fields: D4-equivariance + attack sum             [PASS]  (0.05s)
  C7 Lagrangian energy: E0 = 20, after e4 = 30               [PASS]  (0.00s)
  C8 mate certificates: retro DTM + tactical suite           [PASS]  (1.2s)
  C9 Zobrist incrementality + splitmix64 bijection           [PASS]  (0.3s)
verdict: ALL CHECKS PASSED
```

---

## 3. The three-layer particle model

### Layer K3 — the potential layer (threat fields)

Every piece-particle emits a field on the board: **Θ(c)** = the number of particles of
side *s* attacking the square *c*. Theorem T04 proves the additivity of the field
(`ΣΘ(c) = Σa(π)` — a discrete Fubini theorem), its equivariance under the board group
D4 for pawnless positions, and computes the exact **pawn anomaly**: the pawn is an
"oriented particle", and its orientation breaks the symmetry in exactly
**176 = 88 + 88** pairs (g, c) in the initial position. The field mass of the initial
position is **38** per side.

### Layer TORUS — the energy layer (the Lagrangian)

A position carries the energy

```text
E = [M(w) − M(b)] + μ · [m(w) − m(b)],   μ = 0.1
```

where *M* is the material in pawn units and *m* the mobility (the number of legal
moves). The energy is integral in hundredths, deterministic, and the search minimizes
exactly it. Theorem T05 pins the certificates: the initial mobility is 20 per side;
after **1.e4** the White mobility is **30** (the e2-e4 pawn opened the f1-bishop
diagonal, the d1-queen diagonal and the g1-knight square), i.e. the White kinetic term
is **+1.0**. The kinetic ceiling of a standard set is 105 moves (T03).

### Layer KLEIN — the flow layer (terminations, damping, memory)

A game is a discrete flow on the torus of the board. Theorem T06 gives the exact
termination time of an undamped trajectory,

```text
t* = lcm( W / gcd(a, W),  H / gcd(b, H) ),
```

and the total path of the **damped billiard** with the damping coefficient
**γ = π⁴/256**: the path ratio `path / (|v0|/(1−γ))` converges to **1.000000** (check
C4 verifies it to 1e-9 over 700 cases). The flow carries memory — Zobrist hashing
generated by splitmix64 (theorem T09: 1562 keys, bijection with an explicit inverse,
incremental identity, the birthday bound 0.027 for a billion positions).

---

## 4. The twelve theorems T01–T12

Each theorem is released as a standalone monograph (RU/EN × PDF/DOCX, see
[monograph/](monograph/README.md)) and is closed by an executable protocol check.

| Theorem | Subject | Key constants | Check |
|---|---|---|---|
| **T01** | Board algebra: the symmetry group and orbit censuses | V4 orbits 20 (8×2+12×4), D4 orbits 10 (Burnside) | C1 |
| **T02** | Particle kinematics: move-graph censuses | edges R448 / B280 / N168 / K210 / Q728 | C2 |
| **T03** | Mobility: kinetic invariants | sums K420/N336/B560/R896/Q1456, maxima 8/8/13/14/27 | C3 |
| **T04** | Threat fields: additivity, equivariance, the pawn anomaly | field mass 38 per side; anomaly 176 = 88+88 | C6 |
| **T05** | The position Lagrangian: particle energy | μ = 0.1; m=20 → 30 after 1.e4; kinetic +1.0 | C7 |
| **T06** | Flow termination t\* and the damped billiard | t\* = lcm(·); γ = π⁴/256; path ratio → 1 | C4 |
| **T07** | The closed knight tour (Warnsdorff) | 64 moves from f5, closure d6→f5, no backtracking | C10 |
| **T08** | Perft identities | 20 / 400 / 8902 / 197281 / 4865609 | C5 |
| **T09** | Zobrist hashing: splitmix64 bijectivity and incrementality | 1562 keys; sm(1)=0x910A2DEC89025CC1; birthday 0.027 | C9 |
| **T10** | Alpha-beta: correctness, bounds, determinism | nodes 79/731/3345/19753 (gain ×256.8 at depth 5) | C8 |
| **T11** | Mate certificates: retrograde KRK/KQK + tactics | KRK 16 moves, KQK 10 moves; Bellman 0 violations | C8 |
| **T12** | The state space and the consolidated protocol | 22-bit endgame packing; failure isolation; ALL CHECKS PASSED | C1–C9 |

---

## 5. The protocol C1–C9

The protocol is the executable form of the whole theory. Design principles (theorem
T12):

- **failure isolation** — every check runs inside an exception catch; one FAIL never
  hides the others;
- **reproducibility** — deterministic search, fixed seeds; the verdict is identical on
  any machine (x86 servers and ARM phones alike);
- **cross-language agreement** — the polyglot battery C1–C10 prints byte-identical
  verdict lines in all seven languages.

| Check | Content | Theorem |
|---|---|---|
| C1 | V4/D4 orbit census + Burnside | T01 |
| C2 | move-graph edge censuses | T02 |
| C3 | mobility sums and maxima | T03 |
| C4 | t\* termination + damped billiard | T06 |
| C5 | perft identities (+ `--deep`: perft(5) and the divide(3) table) | T08 |
| C6 | threat-field equivariance + attack sum + anomaly | T04 |
| C7 | Lagrangian energy certificates | T05 |
| C8 | retrograde DTM bases (Bellman over all states) + the tactical suite | T10, T11 |
| C9 | Zobrist incrementality + the splitmix64 round-trip | T09 |

The tactical suite inside C8: the Morphy mate (`a1a6`, 3 plies, PV
`a1a6 b7a6 b6b7`, 46 nodes), the two-rook ladder (`b1b7 h8g8 a2a8`, 3 plies, 49 nodes)
and the knight-and-rook mate in one (`g1g8`, 1 node).

---

## 6. The polyglot core: seven languages

The same battery **C1–C10** is implemented independently in seven languages. Each
backend prints the same line format — `[PASS] Cn note` — and the final line
`verdict: 10/10`. Bit-identical reference constants (perft, censuses, splitmix64
vectors) guarantee that a mismatch of any single backend is caught by comparing the
output.

```bash
bash polyglot/run_all.sh    # runs every available backend, prints the summary table
```

| Language | File | Verified |
|---|---|---|
| Python | `polyglot/python/chess_core.py` | locally, 10/10 |
| C | `polyglot/c/chess_core.c` | locally (gcc -O2), 10/10 |
| JavaScript | `polyglot/javascript/chess_core.js` | locally (node, BigInt), 10/10 |
| Rust | `polyglot/rust/chess_core.rs` | GitHub Actions CI |
| Go | `polyglot/go/chess_core.go` | GitHub Actions CI |
| Julia | `polyglot/julia/chess_core.jl` | GitHub Actions CI |
| Java | `polyglot/java/ChessCore.java` | GitHub Actions CI |

The endgame packing of the retrograde bases is **22 bits**:
`wk | wq<<7 | bk<<14 | stm<<21` (7-bit 0x88 squares).

---

## 7. The engine package

```bash
python3 engine/particles.py --fen "<FEN>"    # the three-layer read-out of a position
python3 engine/mate_solver.py --fen "<FEN>" --max 6
python3 engine/game_player.py --selfplay --depth 4
python3 engine/analyzer.py --fen "<FEN>" --depth 4
```

The search: negamax with an (α, β) window, quiescence, MVV-LVA ordering with a kinetic
centralization bonus, the mate distance encoding `−MATE + ply`, the 50-move rule — all
under a **total move order**, hence bit-reproducible (theorem T10). The mate solver
performs iterative deepening and reconstructs the full PV with the most resistant
defender replies.

---

## 8. The Outcome Dynamics program (epochs I–VIII)

The engine answers *what is the best move*. The outcome program answers a
different question: **what is the probability distribution of the game's
result from this position** — and it refuses to guess when it cannot
know. It is built in eight epochs, each strictly certified:

```text
    Epoch I    exact foundation   frozen DTM bases  ->  exact WDL/DTM oracle
    Epoch II   phase space        position  ->  67 measured coordinates
    Epoch III  distillation       coordinates  ->  calibrated P(W/D/L) model
                                  exact labels  ->  honesty benchmark (E8)
    Epoch IV   player context     who is at the board  ->  Bayesian prior
                                  real games  ->  the E12 audit
    Epoch V    trajectories       lines of play  ->  forecast curves (E9)
    Epoch VI   falsification      the field vs itself  ->  counterexamples (E10)
    Epoch VII  nonlinear head     the E10 hot-spots  ->  specialists (E11/E13/E14)
    Epoch VIII adjudication      whole games  ->  the E9 referee (E15)
```

### 8.1 Epoch I — the exact outcome oracle (`outcome/tablebase_api.py`)

Every legal state of the five frozen domains
(KRK/KQK/KNK/KPK/**KBK**) gets its game-theoretic value — WIN (with the
exact DTM in plies) or DRAW — read from the Bellman-verified
certificates.  Legality is reconstructed from board geometry alone (the
blob cannot distinguish a legal draw from a never-enumerated state), and
`census_kind()` re-derives the builder's state census from scratch: a
mismatch is a bug by definition.

v2 adds the **KBK diagonal negative control** (`K+B vs K`, the
insufficient-material theorem proved by exhaustive computation — won =
mates = 0) and fixes a v1.5.0 defect: lone-bishop positions used to
raise a `KeyError` in domain detection.  The KNK knight and KBK bishop
controls now make the "no forced win" family *structural*: two different
board geometries (knight offsets, diagonal rays), the same computed
verdict of zero mates.

Every certificate is re-derivable: `scripts/rebuild_dtm_tables.py`
rebuilds the whole frozen family from an empty table and compares the
values byte-for-byte (certificate **E7**, frozen in
`results/dtm_rebuild_e7.json`; all four pre-existing domains came out
BIT-IDENTICAL).

```python
from outcome import tablebase_api as T
T.classify_fen('3k4/8/4K3/4P3/8/8/8/8 w - - 0 1')
#  {'domain': 'kpk', 'outcome': 'white_win', 'dtm_plies': 21, ...}
```

### 8.2 Epoch II — the phase space (`outcome/features.py`)

Every position maps to a **67-coordinate phase-space point** (spec v2,
APPEND-ONLY over the frozen v1 block of 40).  Each coordinate is a
deterministic measurement from one of the particle layers: the scalar
material census (15), the kinetic mobility term (3), the K3 threat
fields — masses, king-zone pressure, hanging pieces plus the v2 higher
moments: field peak, coverage and the White/Black overlap (13), king
geometry and king freedom (10), pawn structure and promotion geometry
(10), strongest-piece endgame geometry (8) and the flow/phase block —
Lagrangian energy, side to move, capture availability (8).  Two honesty
rules hold by construction: **no feature ever reads a tablebase value**
(no label leakage), and the extractor reproduces the frozen constants
(mobility 20 → 30 after 1.e4, field mass 38 per side, E₀ = 0).

### 8.3 Epoch III — tablebase distillation (`outcome/model.py`, `outcome/metrics.py`)

The exact certificates become a supervised benchmark: 100,000 sampled
states (20,000 per domain across the five domains, seeded rejection
sampling, deterministic across machines), a 70/15/10 hash split, and
zero-dependency heads trained on the phase-space coordinates:

- **Head B — outcome distribution**: multinomial softmax regression
  (67 features → P(W/D/L), full-batch GD, bit-reproducible), trained
  twice in an A/B: hard one-hot targets vs oracle-shaped soft targets;
- **Head A — DTM regression**: ridge regression predicting the exact
  mate distance in plies over the won states;
- **the production head**: a 3-member bootstrap ensemble on the A/B
  winner plus a per-domain temperature calibration fitted on the valid
  split only.

The benchmark deliberately reports **calibration, not just accuracy**:
log loss, Brier score, ECE, macro-F1 and the reliability table, against
the majority/material-only/mobility-only baselines and a per-layer
ablation — the objective map of *which layer of the dynamics actually
predicts outcomes* (frozen in `results/outcome_distillation.json`).

```text
E8 · outcome distillation (seed 2026, 100,000 states, 67 features, certificate E8)
  pooled test      accuracy 0.9458 · log loss 0.1205 · Brier 0.0731 · ECE 0.0066
  majority base    accuracy 0.5092  (the KBK domain doubled the draw mass)
  per domain       KRK 0.9655 · KQK 0.9973 · KNK 1.0000 · KPK 0.7684
                   · KBK 1.0000 (negative control II)
  DTM head         MAE 2.51 plies (mean baseline 6.14; v1: 3.18)
  layer ablation   material 0.9099 · flow 0.8115 · mobility 0.7403
                   threat (K3) 0.6812 · geometry 0.5663 · pawn 0.5651
                   king 0.5443 · full model 0.9458
```

The A/B verdict is a falsification, and it is frozen as such: the
oracle-shaped soft targets (distance-aware smoothing of won states
toward draw) LOSE to plain one-hot targets on both accuracy (0.9086 vs
0.9499) and log loss (0.3037 vs 0.1217) — the smoothing blurs exactly
the drawn/won boundary where accuracy lives.  The recipe records the
verdict; the production ensemble trains on the winner.

The v2 feature families pay for themselves: with the task made harder
(the draw-majority baseline fell from 0.6379 to 0.5092), accuracy still
rose from 0.9305 to 0.9458, the DTM head improved from 3.18 to 2.51
plies, and the ECE fell to 0.0066 — while KPK, the hardest domain,
improved from 0.7431 to 0.7684.  The ablation keeps its shape: material
carries most of the signal, the flow block is the strongest single
non-material layer, and no single layer approaches the full model.

### 8.4 Outcome Field (`outcome/outcome_field.py`)

The user-facing object: instead of a scalar evaluation, every position
gets the field **F(x) = (P_white, P_draw, P_black)** plus derived
quantities — the Shannon entropy of the field ("how unresolved is this
position?"), the **criticality** (the largest single-move change of the
field: 1.0 means the position is one blunder away from a different
outcome — the quantitative successor of the T17 trap census), the
**robustness index** (the share of moves that keep the outcome class)
and the **counterfactual move-impact surface** for every legal move,
delegated to the dedicated `outcome.impact` module.

Three prediction sources, strictly ordered: **exact** (frozen domains —
entropy 0, no approximation), **model** (the frozen E8 ensemble +
calibration, with out-of-domain queries **flagged as extrapolations**)
and **context** (the Epoch IV Bayesian prior, blended into the model
layer only — a theorem has no prior).

```text
$ python3 -m outcome analyze "8/3K4/8/8/8/8/8/kR6 b - - 0 1" --moves
 OUTCOME FIELD 
 FEN          8/3K4/8/8/8/8/8/kR6 b - - 0 1
 domain       KRK · exact frozen tablebase
 outcome      DRAW
 field        P(white) 0.000   P(draw) 1.000   P(black) 0.000
 entropy      0.000 bit
 criticality  1.000   (critical move: a1a2)
──────────────────────────────────────────────────────────────
 MOVE IMPACT  (ΔP white win; worst first)
   a1a2    W 1.000  D 0.000  L 0.000   ΔW +1.000  H 0.00   <-- FIELD FLIP
   a1b1    W 0.000  D 1.000  L 0.000   ΔW +0.000  H 0.00
```

The drawn position is one trap away from a loss: 1...Ka2? walks into the
mating net while 1...Kxb1! holds — the surface quantifies exactly what
the T17 census counted exhaustively.

### 8.5 The Move Impact module (`outcome/impact.py`)

The counterfactual surface became a first-class instrument in v2.  For
every legal move it measures the child field, **ΔP(white win)**,
**ΔP(draw)**, the child entropy, the exact child DTM and — on won lines
— the **pace**: `dtm_parent − dtm_child`, the tempo economics of the
endgame in plies gained or squandered.  Moves are classified
(`field_flip` / `swing` / `quiet`), and the aggregate block reports the
**robustness index**, the **quiet share** and the cross-check of the
field against the oracle (`best_move_agreement`, honestly `None` when
the ΔW column is degenerate on a won parent).

```text
$ python3 -m outcome impact "6k1/R7/6K1/8/8/8/8/8 w - - 0 1" --max-moves 30
 MOVE IMPACT — counterfactual surface of 6k1/R7/6K1/8/8/8/8/8 w - - 0 1
  parent mate in 1 plies
   g6h6    W 1.000  D 0.000  L 0.000   ΔW +0.000  H 0.00  pace -15
   a7a8    W 1.000  D 0.000  L 0.000   ΔW +0.000  H 0.00  pace +1
   a7a6    W 1.000  D 0.000  L 0.000   ΔW +0.000  H 0.00  pace -3
  robustness  1.0   quiet share 1.0   best-move agreement None
```

On a won parent every ΔW is 0 (a theorem does not waver), so the signal
lives in the **pace** column: `a7a8#` is the unique pace +1 move (mate
next ply), every king step squanders up to 15 plies of tempo — and the
agreement metric is honestly `None` instead of a coin flip.

### 8.6 Epoch IV — the player-context layer (`outcome/context.py`)

The exact layer is a theorem; the MODEL layer is a forecast of
*practical conversion* — and conversion depends on who is at the board.
Epoch IV adds a Bayesian prior, documented and never fitted:

```text
s' = (1−w)·s_model + w·s_elo,   s_elo = 1/(1+10^(−ΔR/400))
```

redistributed by water-filling (win buckets first, the draw share stays
untouched while the shift is small), with an optional clock prior
(30 Elo per doubled time ratio, clamped ±150).  Honesty rules: no player
database, `w = 0` (a strict no-op) without rating input, the exact layer
is never blended, and the whole-game split rule
(`split_of_game`) is provided so that future game-level training can
never leak neighbouring plies across the split boundary.

```text
$ python3 -m outcome context \
      "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" \
      --rating-white 2400 --rating-black 1800
 domain      full chess · distilled outcome model · player context · Elo 2400 vs 1800
 outcome     WHITE WINS
 field       P(white) 0.992   P(draw) 0.000   P(black) 0.008
 entropy     0.065 bit
 WARNING     outside the model training domain (tablebase-only training data):
             the probabilities are an EXTRAPOLATION, not a calibrated forecast
 context      player context · Elo 2400 vs 1800, clock shift +0
              model expected score 0.496 -> blended 0.622 (weight 0.25)
```

Full-chess queries are extrapolations and say so; the context prior
still moves the practical expectation (0.496 → 0.622 for a 600-point
gap) without ever touching an exact-layer answer.

### 8.7 Epoch V — the trajectory model (`outcome/trajectory.py`)

Lines are sampled from the frozen certificates by seeded walks: the
strong side plays DTM-optimal moves, the defender plays best defence,
drawn roots wander randomly, and **KPK promotions are followed into the
KQK certificate** — one line may traverse two domains.  The model is a
gated pooling unit: each step contributes its phase-space vector with a
learned gate `g_t = sigmoid(a0 + a1·(t/T) + a2·(dtm_t/cap))`, and a
linear head on [pooled, final] forecasts the line's final outcome.  Its
ablation twin (`pool='final'`) sees only the last position.

The forecast curve is the scientific payload — accuracy of the forecast
made from the first t plies only (certificate E9, 1,250 lines, 231
domain crossings, whole-game split):

```text
E9 · trajectory forecast (gated vs final-only, test games)
  t=0    0.6364  vs 0.4788     <- history helps BEFORE any move is played
  t=3    0.7879  vs 0.5939
  t=10   0.9333  vs 0.7455
  t=20   1.0000  vs 0.9394
  drift surprise rate  0.0892 vs 0.2188   <- half the alarms
```

The claim "history carries information beyond the current position" is
measured, not asserted: the gated model wins at every horizon and
halves the drift-alarm rate.

### 8.8 Epoch VI — the falsification engine (`outcome/falsify.py`)

The program turns against itself: the engine mines the states where the
frozen model disagrees with the exact oracle — `hard_error` (wrong
argmax), `low_confidence` (P(true) < 0.5), `dtm_error` (ridge off by
more than 4 plies) — and freezes them into the curated corpus
`counterexamples/` (CSV + summary JSON + generated README).  The corpus
doubles as a regression benchmark: the next model version must shrink
it without breaking the E8 certificate.

```text
E10 · falsification corpus (2,000 states per domain, seed 2026)
  krk  66 hard errors (3.30%)      kpk  443 hard errors (22.15%)
  kqk   7 hard errors (0.35%)      knk    0 (0.00%)   kbk  0 (0.00%)
  corpus rows: 816  (all hard errors + top-60 miscalibrations per domain)
```

The two negative controls survive falsification with zero errors — the
computed theorems are unfalsified; KPK remains the honest frontier of
the linear model, now with a named, downloadable list of its failures.

### 8.9 Epoch VII — the nonlinear specialist head (`outcome/nonlinear.py`)

E10 named KPK as the hot-spot (22.15% hard errors), and the reason is
structural: the KPK outcome boundary is famously NONLINEAR — the rule
of the square, key squares, opposition and the tempo of the pawn race
are conjunctions of conditions a linear softmax can only approximate
with hyperplanes.  Epoch VII adds the missing nonlinearity in the most
auditable way possible: two families of derived coordinates APPENDED to
the 67 base features — **hinges** `max(0, x − knot)` (piecewise-linear
crests, 48 of them, every knot frozen inside the measured KPK range so
no dead columns exist) and **crosses** `x_a · x_b` (10 explicit
pairwise interactions: pawn-rank × king geometry, tempo × pawn-rank,
mobility × mobility …).  The basis reads only raw phase-space
coordinates — the no-leakage rule is inherited by construction.

The predictor becomes a **router**: the KPK slice is answered by a
dedicated specialist (same recipe as production: 3-member hard-target
ensemble + temperature calibration on the valid split), every other
domain keeps the frozen global head untouched.  The A/B runs on the
identical E8 protocol (same sampler, same seed, same hash split), and
the promotion rule is strict — the specialist must win on BOTH accuracy
and log loss over the untouched test split, or it is denied:

```text
E11 · nonlinear specialist head (kpk, 20,000 states, seed 2026, certificate E11)
  global head (E8)   test acc 0.7684 · logloss 0.5037 · ECE 0.0305
  hinge arm          test acc 0.8286 · logloss 0.3751 · ECE 0.0120
  hinge_cross arm    test acc 0.8332 · logloss 0.3746 · ECE 0.0120  <- PROMOTED
  hot-spot re-mine   hard errors 443 -> 337 of 2,000 seeded states
  pooled (5 domains) acc 0.9458 -> 0.9588 · logloss 0.1205 -> 0.0944
  corpus (E10')      816 -> 710 rows · kpk hard-error rate 22.15% -> 16.85%
                     (krk/kqk/knk/kbk rates unchanged — the router is airtight)
```

After promotion the production model file carries the `nonlinear` block
and `python3 -m outcome evaluate` reproduces the new pooled certificate
bit-for-bit; the falsification corpus is re-mined so the regression
benchmark reflects the promoted predictor.  Where E8's A/B *falsified*
the soft-target hypothesis, E11 *confirms* the nonlinear-basis one —
the honest bookkeeping works in both directions.  (The basis grew a
third family in v2.2.0 — see 8.11.)

```bash
python3 -m outcome nonlinear --per-kind 20000        # A/B + promotion + corpus re-mine
python3 -m outcome nonlinear --no-promote            # A/B only, never rewrite the model
python3 -m outcome nonlinear --checkpoint /tmp/ck    # resumable (arms cached as JSON)
```

### 8.10 Real games through Epoch IV (`outcome/pgn.py`, `outcome/realgames.py`)

Epoch IV was designed on priors; v2.1.0 connects it to actual games.
A zero-dependency **PGN layer** replays Standard Algebraic Notation
through the certified legality machinery — headers, comments,
variations, NAGs, move numbers, castling, en passant, promotions and
disambiguation (`Nbd7`, `R1e2`, `Qh4e1`), with a SAN writer that
round-trips through the reader.  A corrupt score raises `PGNError` with
the offending ply — never a silent recovery.

The frozen corpus `data/games/` mixes three sources with an explicit
honesty contract: **human-classical** public-domain scores (Réti –
Tartakower 1910, Morphy – Brunswick & Isouard 1858, Anderssen –
Kieseritzky 1851 — no Elo headers, so the context prior must be a
strict no-op on them), **engine** self-play games, and **tablebase
walks** — 24 seeded Epoch V lines whose terminal result is known from
the certificates, carrying SIMULATED, clearly labeled Elo headers with
a documented alignment knob (aligned / independent), so the context
A/B has signal without fabricating player data.

The audit scores three arms against the actual result at every oracle
entry of every game — exact (the theorem), model (the E11 router),
model+context (the water-filling blend):

```text
E12 · real-game audit (29 games, 508 oracle entries, certificate E12)
  position level     model-vs-exact agreement 1.0000 over 508 entries
                     (optimal/best-defence lines stay away from the boundary)
  game-level logloss exact 0.0000 · model 0.1274 · model+context 0.2103
  honesty checks     no-rating games verified strict no-ops; result/board
                     consistency flagged (0 flagged); argmax drift 0.0000
  negative result    on theory-governed walks the Elo prior only destroys
                     information — the context layer belongs where theory
                     is absent, and the audit measures that cost instead
                     of assuming it away
```

```bash
python3 -m outcome games data/games                  # the E12 certificate
python3 scripts/build_game_corpus.py                 # regenerate the walks
```

### 8.11 Interaction hinge nodes on the residual corpus (`outcome/nonlinear.py` v2)

E11 left 337 hard errors on the seeded KPK mine — the *residual
frontier*.  v2.2.0 answers them with a third basis family, the
**interaction hinge node**:

```text
    ihinge(a, ka, b, kb) = max(0, x_a − ka) · max(0, x_b − kb)
```

a product of two hinge crests — a *localized conjunction cell* that
switches on only in a corner of phase space, the exact shape of the
rule of the square, the boxed king and the edge-defence conditions
endgame theory puts on the KPK boundary (a plain cross `x_a · x_b` is
everywhere active; an ihinge is silent outside its cell, so the linear
head can tune the corner without moving the rest of the map).  The
basis spec becomes **v2** (`hinge + cross + interaction hinge,
append-only`); v1 payloads load bit-identically, so the promoted E11
route keeps its exact predictions across the upgrade.

The E13 A/B is **corpus-driven**: the 16 interaction knots were frozen
from TRAIN-split residual-error diagnostics (deep pawn-race cells
`promotion_dist 3..5 × king_dist 3..7`, boxed-defender cells
`king_dist × king_freedom_black`, edge-defence cells `edge ×
manhattan`), never from valid/test labels, and every knot sits strictly
inside the live range (no dead columns).  Two arms on the identical E8
protocol, against the *frozen production route* as baseline:

* `ihinge` — the full v2 basis (67 + 74 = 141 coordinates), uniform targets;
* `ihinge_w` — the same basis with **error-corpus weights**: the
  production route labels the TRAIN split, and every residual hard
  error carries weight `1 + 4.0` (valid/test rows are never weighted).

```text
E13 · interaction hinge nodes (kpk, 20,000 states, seed 2026, certificate E13)
  production route (E11)  test acc 0.8332 · logloss 0.3746 · mine 337
  ihinge arm              test acc 0.8332 · logloss 0.3738 · mine 323
  ihinge_w arm            test acc 0.8138 · logloss 0.3996 · mine 380
  decision                PROMOTION DENIED (no arm wins BOTH gate metrics)
```

The honest reading: the interaction nodes *are* the right shape for the
residual (the re-mine drops 337 -> 323 and the log loss improves
microscopically), but they do not move test accuracy, and the strict
double gate denies them — exactly as the rule demands.  The second
finding is the useful negative: **error-weighting backfires** —
upweighting the hard train rows by 5x overfits the boundary and
*increases* the residual mine to 380.  Both results are frozen in the
certificate and the corpus is left re-mined from the still-standing E11
route (644 rows; krk cleaned by E14 below, kpk 337 unchanged).

```bash
python3 -m outcome interact --per-kind 20000         # E13 A/B + promotion rule
python3 -m outcome interact --err-weight 2.0         # a softer residual emphasis
```

### 8.12 The KRK specialist (`outcome/nonlinear.py`, E14)

The second E10 hot-spot — KRK's 3.30% hard-error rate — gets the same
specialist treatment.  The error signature is unambiguous: the train
residuals are ~99% *wins called draws*, living where the rook is already
next to the black king (`strongest_dist_enemy_king_white` 1–2), the
defender king is boxed (`king_freedom_black` <= 4, `mobility_black`
<= 4) and often in check with elevated king-zone pressure — late-stage
deep mates where a linear response saturates too early and tips into
the draw class.  The frozen KRK schedule (18 hinges + 10 crosses, knots
from TRAIN ranges and residual diagnostics) points the basis exactly
there: hinges on rook-king geometry at knots 1/2/3, defender freedom at
2/4, mobility at 2/3/4, and crosses like
`strongest_dist_enemy × king_freedom_black` and
`king_zone_pressure_black × king_dist_manhattan`.

```text
E14 · krk specialist head (krk, 20,000 states, seed 2026, certificate E14)
  global head (E8)        test acc 0.9655 · logloss 0.0675 · mine 66
  hinge arm (67 + 43)     test acc 1.0000 · logloss 0.0033 · mine 0
  hinge_cross (67 + 53)   test acc 1.0000 · logloss 0.0014 · mine 0  <- PROMOTED
  pooled (5 domains)      acc 0.9588 -> 0.9658 · logloss 0.0944 -> 0.0812
  corpus (E10')           710 -> 644 rows · krk hard errors 66 -> 0
```

The KRK hot-spot is **eliminated**: 3.30% -> 0.00% on the seeded mine,
perfect test accuracy with better calibration, while the airtight
router keeps the other four domains byte-identical (kpk stays 0.8332 —
E13's denial held).  The E12 audit re-run against the new router
improves the game-level model log loss 0.1274 -> 0.1132; the
falsification corpus is re-mined to 644 rows.  The production model now
routes two specialists (kpk, krk) over the frozen global head.

### 8.13 Whole-game adjudication — the E9 referee (`outcome/adjudicate.py`, E15)

Epoch VIII closes the loop: the E12 audit replays real games, the E9
trajectory model forecasts a line's final outcome from its prefix, and
`adjudicate.py` joins them into a **referee panel**.  Four arms must
call the actual result of each whole game from the first t+1
oracle-space entries: `exact` (the position oracle at the cutoff — the
upper bound that honestly may disagree with the future at early
cutoffs), `state` (the frozen state model at the cutoff position — the
E12 arm, no history), `trajectory_gated` (the E9 gated model over the
whole prefix — history counts) and `trajectory_final_only` (the E9
no-history twin — the control).  The adjudication curve scores each
arm against the Result header at game level:

```text
E15 · whole-game adjudication (29 games, 508 oracle entries, certificate E15)
  scoreable games       24 (5 skipped: the classics never reach a frozen
                          domain — the referee judges only where the
                          certificates speak, and says so)
  final-entry logloss   exact 0.0000 · trajectory_gated 0.0000 ·
                        trajectory_final_only 0.0000 · state 0.1132
  accuracy              1.0000 on every arm at every cutoff (the walks
                        live deep in decided territory, in-distribution)
  verdict stability     0.0000 flips per oracle step (gated) — the call
                        never wobbles once made
```

The quantitative payload is the log-loss gap: on the same 508 entries
the state model stays uncertain about *deep* mates (P(win) < 1), while
the trajectory referee — having seen the line — commits with
certainty.  Adjudication is a pure evaluation of frozen artifacts (no
retraining), hence bit-reproducible; the gate's time axis is the
oracle-entry ordinal and the DTM input is the exact oracle value, both
stated in the certificate.  The honest boundary is recorded with equal
care: without oracle-space entries (any full-chess game before it
simplifies to a frozen domain) the referee abstains rather than
guesses.

```bash
python3 -m outcome adjudicate data/games             # the E15 referee certificate
python3 -m outcome adjudicate game.pgn --model m.json --trajectory t.json
```

---

## 9. The web laboratory

`web/chess-particles/index.html` is a single-page static application (no build tools)
in the visual language of the hodge-flow-chess laboratory: dark navy, gold, violet and
teal particles.

- **Live flow** — glowing particle pieces (gold = White, violet = Black) driven by a
  seeded PRNG; every move is a legal move of a real 0x88 engine running in the browser;
  a threat-field heatmap toggle (Θ(c)) plus the **Θ-flow animation** (glowing quanta
  streaming along every attacker→target incidence, crossfading between positions);
  the Lagrangian panel updating every ply;
  manual play by clicking; the damped t\* billiard card.
- **Theory** — the twelve theorem cards with the frozen constants.
- **Protocol C** — the checks **genuinely computed in the browser** over the page's own
  engine: C1 orbit censuses, C2 edge censuses, C3 mobility, C4 t\* over 700 cases, C5
  perft(1..3) = 20/400/8902 (deep: perft(4) = 197281), C6 the field mass 38 and the
  anomaly 176, C7 energy 20→30, C8 the Morphy mate by DFS, C9 splitmix64 in BigInt with
  the inverse round-trip 1..2000, C10 the closed Warnsdorff knight tour. FAIL is
  possible and displayed honestly — nothing is hardcoded.
- **About** — the program, the author, the license.

Full RU/EN interface with a language pill and `localStorage` persistence.

---

## 10. Monographs (PDF/DOCX × RU/EN)

Everything lives under [`monograph/`](monograph/README.md):

```text
monograph/
├── pdf/ru/   main_monograph.pdf + t01..t12 + particle_limit (14 files)
├── pdf/en/   main_monograph.pdf + t01..t12 + particle_limit (14 files)
├── docx/ru/  main_monograph.docx + t01..t12 + particle_limit (14 files)
├── docx/en/  main_monograph.docx + t01..t12 + particle_limit (14 files)
└── src/      the LaTeX/docx-js generators and the content modules
```

- **Main monograph** — *«Динамика шахматных частиц: сертифицируемая лаборатория» /
  Chess Particle Dynamics: A Certifiable Laboratory*: 12 chapters, 2 appendices
  (the consolidated constants table; the reproduction guide), 5 figures, a
  bibliography (Shannon, Zobrist, Knuth–Moore, Thompson, Schwenk, Tromp,
  hodge-laboratory).
- **12 theorem monographs** — each with the problem statement, the theorem, the proof,
  the protocol tables, the summary and the verification commands.
- **Research paper** — *«Предел частиц» / The Particle Limit*: generalized chess,
  EXPTIME and polynomial myopia. Theorem T13 (no polynomial algorithm for
  EXPTIME-complete generalized chess can exist — P ⊊ EXPTIME is a theorem, not a
  conjecture) and Theorem T14 (the particle horizon: fixed piece counts give
  polynomial oracles; the greedy particle solver is a polynomial approximator
  whose measured price is a 17.56% loss rate on KRK), with the E1/E2 experiments.

---

## 11. Frozen constants

The baseline `results/baseline_c1_c9.json` pins every number the theory claims:

```text
orbits        V4 20 (8 diag ×2 + 12 off-diag ×4) · D4 10 (Burnside)
edges         rook 448 · bishop 280 · knight 168 · king 210 · queen 728
mobility      sums K420/N336/B560/R896/Q1456 · maxima 8/8/13/14/27 (queen)
field         mass 38 per side (initial) · pawn anomaly 176 = 88 + 88
energy        E0 = 0 (balanced) · mobility 20 → 30 after 1.e4 (μ = 0.1 → +1.0)
flow          t* = lcm(W/gcd(a,W), H/gcd(b,H)) · γ = π⁴/256 · path ratio 1.000000
knight tour   64 moves from f5 · closure d6→f5 · all knight steps
perft         20 / 400 / 8902 / 197281 / 4865609
zobrist       1562 keys · seed 0x1234567890ABCDEF · sm(1) = 0x910A2DEC89025CC1
              sm(2) = 0x975835DE1C9756CE · sm(3) = 0x1D0B14E4DB018FED
              birthday bound: n(n−1)/2⁶⁵ → 0.0271 at n = 10⁹
search        nodes 79 / 731 / 3345 / 19753 (depths 2–5) vs 421/9323/206604/5072213
KRK           399112 states · 4447032 edges · 376868 won · 216 mates · max DTM 32 plies = 16 moves
KQK           368452 states · 4869496 edges · 345404 won · 364 mates · max DTM 20 plies = 10 moves
KNK           429440 states · 3521256 edges · 0 won · 0 mates — a knight mate does not exist (T15)
KPK           331352 states · 2125630 edges · 222558 won · 0 mates · max DTM 56 plies = 28 moves
              (promotion boundary = the frozen KQK certificate; mates only after promotion)
KBK           417228 states · 3946992 edges · 0 won · 0 mates — a lone-bishop mate does
              not exist (T15b, v2): the diagonal negative control
Bellman       0 violations over all states of all five bases; the whole frozen family
              rebuilt from empty tables and compared byte-for-byte (E7 provenance:
              all four pre-existing domains BIT-IDENTICAL)
E4 vortex     1800/1800 flow-vs-table agreement · capture 1.000/0.000 separation
              robust ±20% · constants Γ 0.9 · κ 3.2 · ζ 2.0 · j_neutral 0.5
              KRK/KQK WTM-drawn class is EMPTY: every strong-side-to-move
              state is won (175168/175168 in KRK, 144508/144508 in KQK)
T17 traps     census over every legal move of every state (trap_census.json):
              KRK 59,624 draw→loss traps in 21,764 of 22,244 drawn BTM states
              (97.8%, max 4 in one position, deepest mate 31 plies after the
              blunder); KQK 32,896 traps; KPK 173,786 (max 7, deepest 55 plies);
              KNK — exactly 0 traps / 0 slack / 0 waste (T15 in move classes);
              KRK WTM won: 2,759,996 wasteful moves, mean waste 5.886 plies
              (max 28) — the exact population behind sampled E1
n×n presets   KRK demos verified won by retro_dtm_nxn: 4×4 in 9 plies,
              5×5 in 13, 6×6 in 17 (web presets + verify_nxn_presets.py)
E5 levels     four subspaces solved STRONGLY (1,528,356 states, 100%
              coverage); ultra-weak: 11 doctrine anchors asserted live;
              weak: explicit strategy trees — KRK 2,496 / KQK 132 /
              KPK 6,558 nodes (0.04–2% of the space); E3 argmax
              reproduced independently: 500,900 = 500,900; the wall:
              a full-chess table ≈ 3.21·10²¹ × world storage
              (solve_levels_e5.json · note N2 complexity/SOLVING_CHESS.md)
mates         Morphy a1a6 (3 plies, 46 nodes) · ladder b1b7 (3, 49) · NR g1g8 (1, 1)
E6 outcome    v1.5.0 distillation (superseded by E8, kept for history):
              80,000 states · 40 features · pooled test accuracy 0.9305
              · log loss 0.1647 · ECE 0.0101 · DTM MAE 3.18 plies
E8 outcome    v2.0.0 distillation of the frozen certificates into the phase
              space (seed 2026 · 100,000 states = 20,000 × KRK/KQK/KNK/KPK/KBK ·
              70/15/10 splitmix64 hash split · 67 features · zero dependencies ·
              hard-vs-soft A/B · 3-member bootstrap ensemble · per-domain
              temperature calibration on the valid split):
              pooled test accuracy 0.9458 · log loss 0.1205 · Brier 0.0731 ·
              ECE 0.0066 (majority baseline 0.5092); per domain: KRK 0.9655,
              KQK 0.9973, KNK 1.0000, KPK 0.7684, KBK 1.0000 (control II);
              DTM head MAE 2.51 plies vs 6.14 mean baseline;
              A/B verdict: oracle-shaped soft targets FALSIFIED (hard acc
              0.9499 / logloss 0.1217 vs soft 0.9086 / 0.3037);
              layer ablation: material 0.9099 > flow 0.8115 > mobility 0.7403
              > threat K3 0.6812 > geometry 0.5663 ≈ pawn 0.5651 > king 0.5443
              (outcome_distillation.json · outcome_model.json · section 8)
E9 trajectory 1,250 seeded lines (horizon 40, whole-game split, 231 domain
              crossings KPK→KQK); gated history-pooling model vs final-only
              twin: t=0 0.6364 vs 0.4788 · t=3 0.7879 vs 0.5939 · t=10
              0.9333 vs 0.7455 · t=20 1.0000 vs 0.9394; drift surprise rate
              0.0892 vs 0.2188 — history halves the drift alarms
              (outcome_trajectory.json · section 8.7)
E10 falsify   the model vs the oracle, 2,000 states per domain (seed 2026):
              krk 66 hard errors (3.30%) · kqk 7 (0.35%) · kpk 443 (22.15%)
              · knk 0 · kbk 0 — the negative controls are unfalsified;
              corpus 816 rows (counterexamples/ · section 8.8)
E11 nonlinear the Epoch VII specialist head on the E10 hot-spot (seed 2026,
              20,000 kpk states, E8 protocol): hinge+cross basis 67 -> 125
              coordinates, gated router; kpk test acc 0.7684 -> 0.8332,
              logloss 0.5037 -> 0.3746, ECE 0.0305 -> 0.0120; hard errors
              443 -> 337 on the seeded hot-spot population; PROMOTED:
              pooled 0.9458 -> 0.9588, logloss 0.1205 -> 0.0944; the
              falsification corpus re-mined to 710 rows, kpk rate 16.85%
              (outcome_nonlinear_e11.json · outcome_model.json · section 8.9)
E12 realgames 29 games (3 human-classical + 2 engine + 24 tablebase walks),
              508 oracle entries scored at game level vs the Result header:
              exact 0.0000 · model 0.1132 · model+context 0.1966 log loss
              (re-run after the E14 promotion); model-vs-exact agreement
              1.0000 on walk entries; no-rating games verified strict
              no-ops; the Elo prior measured as a net LOSS on
              theory-governed positions (the honest negative result of
              the context A/B)
              (outcome_realgames_e12.json · data/games/ · section 8.10)
E13 interact  interaction hinge nodes max(0,x_a-ka)·max(0,x_b-kb) on the
              residual KPK corpus (basis v2, 67 -> 141 coordinates, knots
              frozen from TRAIN-split residual diagnostics): ihinge arm
              acc 0.8332 (= route) · logloss 0.3738 (< 0.3746) · mine
              337 -> 323; error-weighted arm REGRESSES (acc 0.8138,
              mine 380 — upweighting hard rows overfits the boundary);
              PROMOTION DENIED by the strict double gate — the honest
              negative result, frozen with the same care as E8's
              (outcome_interaction_e13.json · section 8.11)
E14 krk spec  the second hot-spot eliminated: KRK specialist (18 hinges
              + 10 crosses pointed at the rook-next-to-king / boxed-
              defender / deep-mate cells), E8 protocol: krk test acc
              0.9655 -> 1.0000 · logloss 0.0675 -> 0.0014 · ECE 0.0117
              -> 0.0014; hard errors 66 -> 0 on the seeded mine
              (3.30% -> 0.00%); PROMOTED: pooled 0.9588 -> 0.9658,
              logloss 0.0944 -> 0.0812; corpus re-mined 710 -> 644 rows
              (outcome_specialist_krk_e14.json · outcome_model.json ·
              section 8.12)
E15 adjudicate whole-game referee: 4 arms (exact / state / trajectory
              gated / trajectory final-only) call the Result header from
              the first t+1 oracle entries of 29 games (508 entries, 24
              scoreable); final-entry logloss gated 0.0000 vs state
              0.1132; accuracy 1.0000 everywhere; verdict flips 0.0000;
              5 games honestly skipped (no oracle-space entries)
              (outcome_adjudication_e15.json · section 8.13)
```

Both tablebase maxima — **16 moves for KRK** and **10 moves for KQK** — coincide with
the classical published values: an external cross-check that self-verification cannot
provide.

---

## 12. Repository layout

```text
chess-dynamics-lab/
├── dynamics.py            the single-file laboratory (protocol C1–C9, CLI)
├── engine/                particles.py · mate_solver.py · game_player.py · analyzer.py
├── outcome/               the Outcome Dynamics program (epochs I–VIII):
│                          tablebase_api.py · features.py · dataset.py ·
│                          model.py · metrics.py · outcome_field.py ·
│                          impact.py · context.py · trajectory.py ·
│                          falsify.py · nonlinear.py · pgn.py ·
│                          realgames.py · adjudicate.py · cli.py
├── data/games/            the E12 real-game corpus: public-domain classics +
│                          engine self-play + tablebase walks (PGN)
├── counterexamples/       the Epoch VI falsification corpus (re-mined
│                          after the E14 promotion): counterexamples.csv ·
│                          summary.json · README.md
├── polyglot/              python/ c/ rust/ go/ julia/ javascript/ java/ + run_all.sh
├── complexity/            the EXPTIME barrier lab: ParticleSolver, generalized n×n
│                          retrograde, experiments E1/E2, notes N1 (P vs NP) and
│                          N2 (solving chess like checkers) — see complexity/README.md
├── tests/                 181 pytest tests
├── results/               dtm_{krk,kqk,knk,kpk,kbk}.json.gz · dtm_rebuild_e7.json ·
│                          knight_tour.json · baseline_c1_c9.json ·
│                          complexity_particles_vs_oracle.json ·
│                          complexity_scaling.json · complexity_certificates.json ·
│                          vortex_e4.json · trap_census.json · solve_levels_e5.json ·
│                          outcome_distillation.json · outcome_model.json ·
│                          outcome_trajectory.json · outcome_nonlinear_e11.json ·
│                          outcome_interaction_e13.json ·
│                          outcome_specialist_krk_e14.json ·
│                          outcome_realgames_e12.json ·
│                          outcome_adjudication_e15.json
├── reports/plots/         5 protocol plots + complexity/ (2 barrier-study plots, 600 dpi)
├── monograph/             pdf/{ru,en}/ · docx/{ru,en}/ · src/ (generators)
├── vortex/                the T16 vortex-value correspondence (vortex_dynamics.py)
├── web/chess-particles/   the browser laboratory (index.html + assets)
├── web/chess-oracle/      the endgame oracle: 4 DTM spaces, tree, traps, vortex
├── docs/                  the GitHub Pages landing
├── scripts/               termux_push.sh · build_knk_kpk_tables.py · build_kbk_table.py ·
│                          rebuild_dtm_tables.py · export_web_tables.py ·
│                          vortex_e4.py · trap_census.py · verify_nxn_presets.py ·
│                          solve_levels_e5.py · build_game_corpus.py
├── .github/workflows/     ci.yml · pages.yml
├── CITATION.cff · LICENSE · INSTRUCTION.md · CHANGELOG.md
├── CONTRIBUTING.md · SECURITY.md · SUPPORT.md · CODE_OF_CONDUCT.md
└── pyproject.toml · .gitignore
```

---

## 13. Publishing your fork

```bash
bash scripts/termux_push.sh
```

The script checks the environment (git + `gh` or `GH_TOKEN`), makes the initial
commit, creates the repository `wild8highlander/chess-dynamics-lab` under your account
(override with `GH_USER`/`GH_REPO`) and pushes `main`. The CI then verifies the
protocol and the polyglot battery automatically; the Pages workflow deploys `docs/`
and the web laboratory.

---

## 14. Development and CI

- **CI** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): the full protocol on
  Python 3.9/3.11/3.13, deep perft, the pytest suite, the outcome dynamics smoke
  experiment (epochs I–VIII), the self-play determinism check,
  the polyglot battery in all seven languages (gcc, node, rustc, go, julia, javac), and
  a Node sanity run of the web core (`verdict: 10/10`).
- **Tests**: `python3 -m pytest tests/ -q` — 92 tests over the move generation, the
  censuses, the flow, the mates, the bases, the hashes, the frozen baseline, the
  exact outcome oracle, the phase-space extractor, the distillation heads and the
  Outcome Field.
- **Local verification matrix**: Python, C and JavaScript are verified locally;
  Rust, Go, Julia and Java are verified by CI on every push (theorem T12(iv)).

---

## 15. Citation and license

Cite via [CITATION.cff](CITATION.cff):

```text
Isaev I. Kh. Chess Particle Dynamics: A Certifiable Laboratory.
The chess-dynamics-lab program, 2026.
https://github.com/wild8highlander/chess-dynamics-lab
```

**Individual exclusive license**: all rights belong to Isaev Iskhak Khamzatovich. Any
use, distribution, derivative work, or use in machine-learning systems requires the
author's direct written permission. See [LICENSE](LICENSE).

© 2026 Isaev Iskhak Khamzatovich / Исаев Исхак Хамзатович. All rights reserved.
