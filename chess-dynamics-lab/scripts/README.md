# scripts/ — the publication utilities

## termux_push.sh — one-command GitHub publication

Creates the repository under your GitHub account and pushes the whole laboratory in a
single run. Works in Android (Termux), Linux and macOS.

```bash
bash scripts/termux_push.sh
```

### What it does

1. checks the environment: `git`, plus either the `gh` CLI (authenticated) or the
   `GH_TOKEN` environment variable (a classic token with the `repo` scope);
2. sets the git identity if missing (`GH_USER` / `GH_USER@users.noreply.github.com`);
3. initializes the repository (branch `main`) and makes the initial commit if the tree
   is dirty;
4. creates `https://github.com/<GH_USER>/<GH_REPO>` via `gh repo create` or the REST
   API (a 422 "already exists" is treated as reuse, not as an error);
5. pushes `main` and prints the CI/Pages pointers.

### Configuration

| Variable | Default | Meaning |
|---|---|---|
| `GH_USER` | `wild8highlander` | the GitHub account |
| `GH_REPO` | `chess-dynamics-lab` | the repository name |
| `GH_TOKEN` | — | a personal access token (only needed when `gh` is absent) |

The token is sent **only** to `github.com`. Read the script before running it — it is
80 lines of plain bash with `set -euo pipefail` semantics.

### After the push

- the `ci` workflow verifies the protocol on Python 3.9/3.11/3.13, the deep perft, the
  pytest suite, the self-play determinism and the polyglot battery in all seven
  languages;
- the `pages` workflow deploys the landing (`docs/`) and the web laboratory
  (`/lab/`) to GitHub Pages.

The step-by-step guide with screenshots-level detail lives in
[../INSTRUCTION.md](../INSTRUCTION.md).

© 2026 Isaev Iskhak Khamzatovich. All rights reserved. See [../LICENSE](../LICENSE).

## build_knk_kpk_tables.py — the KNK/KPK retrograde bases

Builds the two newest frozen certificates and verifies them in one run:

```bash
python3 scripts/build_knk_kpk_tables.py both    # or: knk | kpk
```

- **KNK** (K+N vs K) — the negative control: the retrograde build must
  discover zero mates (a checking knight attacks none of the king's eight
  neighbours, so the lone white king can never cover all escape squares).
  The run asserts `won = 0, mates = 0` and freezes 429440 states.
- **KPK** (K+P vs K) — retrograde with pawn single/double pushes and the
  promotion boundary: a promotion child is a KQK state, and its exact DTM
  is inherited from the frozen KQK certificate. Queen promotion is
  DTM-sufficient (move-set domination over R/B; N/B under-promotions land
  in mate-less KNK/KBK), so a Q-only table is exact.

Both runs finish with an independent Bellman pass over ALL states
(properties, not values) and hand-verified spot probes
(`b6/c7/a8 → 1`, `b6/c7/a7 → draw`, the opposition draw `d6/e6/d8`, …).

## export_web_tables.py — the web payload

Reads the four frozen certificates, hard-gates every statistic against the
FROZEN constants (a mismatch aborts the export), and writes
`web/chess-oracle/assets/data/tables.js` (a `<script>` global, so the oracle
works offline from `file://` in Termux) plus `manifest.json` with SHA-256
checksums for the in-app integrity panel.

```bash
python3 scripts/export_web_tables.py
```

## vortex_e4.py — the E4 vortex calibration (T16)

Draws seeded stratified samples from the four frozen endgames
(kind × side-to-move × won/drawn), builds the T16 vortex field for each,
integrates the metric particle ensemble and classifies the state **from the
flow only**; the flow class is compared with the table verdict. Freezes the
ODE constants (`FROZEN_VORTEX`), the agreement matrix (must be 100%), the
capture margins, exact per-class state counts, doctrine anchors and a ±20%
robustness scan into `results/vortex_e4.json`.

```bash
python3 scripts/vortex_e4.py 150     # samples per class; must end with E4 PASSED
```

## trap_census.py — the T17 exhaustive move-class census

Walks every legal state of the four frozen endgames (KRK, KQK, KNK, KPK)
and classifies every legal move by comparing the child value v with the
parent value d: `trap` (draw→loss, the defender's blunder), `slack`
(win→draw), `waste` (win kept, ddtm = v−(d−1) plies), `optimal`
(v = d−1), `optimal_def`/`accel` (the defender's resistance). KPK
promotion children are valued through the frozen KQK certificate; states
outside a space are excluded, with the census universe equal to the
builders' exactly — the KPK pawn lives on ranks 2–7 (a first draft also
counted 55,920 impossible rank-8 pawn states as drawn; caught by the E5
cross-assert against the table header and fixed on 2026-09-30 — the trap
headline numbers were never affected, only the drawn-state denominators).
The aggregates freeze to
`results/trap_census.json` and are embedded in `web/chess-oracle/
assets/js/traps.js`. KNK comes out all-zero — T15 restated in move-class
language. Runtime ≈ 17 s.

```bash
python3 scripts/trap_census.py        # -> results/trap_census.json (T17 CENSUS PASSED)
```

## solve_levels_e5.py — the E5 solution-level ladder (note N2)

Answers "can chess be solved like checkers?" with measurements instead
of shrugs (`complexity/SOLVING_CHESS.md` is the prose companion). On the
four frozen spaces the script establishes, layer by layer:

- **strong** — the population census per space, cross-asserted against
  the frozen table headers (states, won, mates, max DTM): coverage is
  100% by construction and 1,528,356 states in total;
- **ultra-weak** — eleven classical doctrine anchors probed live and
  asserted (c8=Q# mate-in-1, both stalemate traps, the frontal
  opposition draw d6/e6/d8 wtm vs its lost twin btm — win in 18 plies,
  the shoulder line a3/g2/a5 — the 56-ply deepest win, the king-in-front
  rule, the undefended-pawn resource, the KRK/KQK canonical starts), plus
  the KNK universal draw (0 won states in 429,440 — T15);
- **weak** — for canonical starts: the full optimal principal variation
  (greedy attacker vs maximally resistant defender, length = DTM,
  ending in mate) and the minimal DTM-greedy winning-strategy tree (the
  E3 recursion, with KPK promotion children crossing into the KQK space
  exactly as the build does). Cross-check: the E3 argmax position
  (a8/c2/d3 w, DTM 31) must reproduce the frozen 500,900 nodes — two
  independent implementations, one number;
- **deepest** — exact argmax scans of all four tables per side to move;
- **the wall** — the exact E2 n-ladder meets the literature ladder
  (5/6/7/8-man tablebase sizes, checkers ≈ 5·10²⁰ weakly solved in 2007,
  chess ≥ 4.5·10⁴⁴) and exact big-int extrapolations: a full-chess table
  at 1 B/state ≈ 3.21·10²¹ × world storage and 1.53·10²⁸ years at
  10⁹ states/s.

Freezes to `results/solve_levels_e5.json`; ends with `E5 PASSED`.

```bash
python3 scripts/solve_levels_e5.py    # -> results/solve_levels_e5.json
```

## verify_nxn_presets.py — the web n×n presets and the E2 recount

Verifies with the exact retrograde oracle `retro_dtm_nxn` that the
chess-particles KRK presets for the generalized boards are legal and won
(4×4: 9 plies, 5×5: 13, 6×6: 17), and recounts the exact KRK state/edge
counts for n = 4..8 with the same enumeration semantics as the frozen E2
experiment — including the degenerate 0x88 king-move tail for n < 8 —
matching `results/complexity_scaling.json` digit-for-digit. The same
enumeration runs live in the browser (`krkSpace(n)`) and is pinned by the
node tests.

```bash
python3 scripts/verify_nxn_presets.py # -> PRESET/COUNT VERIFICATION: PASS
```
