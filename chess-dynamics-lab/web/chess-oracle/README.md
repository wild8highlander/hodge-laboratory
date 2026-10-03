# chess-oracle — play against perfection, watch the proof run

An advanced static web laboratory for four pawnless-and-pawn endgames:
**K+R vs K**, **K+Q vs K**, **K+N vs K** and **K+P vs K**: you play against
the *frozen DTM tablebase* — perfect play by construction — while the
application continuously re-verifies the table against the Bellman
properties with an independent move generator.

No build step, no dependencies, works offline (`file://` or any static
server) — including Termux on a phone.

## What "deepening the proof" means here

The retrograde analyzer (Task 12) certified a Bellman fixpoint over ALL
states in Python and froze it (`results/dtm_*.json.gz`). This app turns
that frozen artifact into a *live process*:

1. **Integrity gate on load** — the payload is checked against the frozen
   build certificate (states 399,112 / edges 4,447,032 / mates 216 /
   max 32 plies for KRK; 368,452 / 4,869,496 / 364 / 20 for KQK;
   429,440 / 3,521,256 / **0 mates** for KNK; 331,352 / 2,125,630 /
   222,558 won / max 56 plies for KPK), the blob is decompressed and
   re-counted; a single mismatch raises `INTEGRITY FAIL` and the oracle
   refuses to play.
2. **Live Bellman audit** — every visited position is re-verified in the
   browser:
   * BTM mate ⇔ no legal moves and in check;
   * WTM won `d` ⇔ a child at `d−1` exists and nothing faster exists;
   * BTM lost `d` ⇔ all children won with max `d−1`, no capture escape;
   * WTM drawn ⇔ no winning child;
   * BTM drawn ⇔ drawing child, or stalemate, or capture escape.
   The counters never hide a failure: one `FAIL` turns the banner red.
3. **Perfect play** — the oracle moves are `argmin DTM` (White) /
   `argmax DTM` (Black) over the table; the meter shows the plies to mate
   and their monotone descent. The 50-move rule is not modelled (the
   classical tables do not model it either) — stated honestly in the UI.
4. **Strategy-tree explorer (E3 live)** — the minimal explicit certificate
   `T(w) = 1 + min_b(1 + Σ_r T(r))` is counted exactly for the current
   position, with the per-level growth profile, next to the implicit
   table size. Polynomial / exact / explicit — pick two.
5. **E1 replay in-browser** — the greedy three-layer ParticleSolver
   (ported 1:1 from `complexity/generalized_chess.py`: material + μ·mobility
   + λ·K3 pressure, μ=0.1, λ=0.25, lexicographic tie-break) makes one move
   per sampled won position; the oracle classifies it. Your browser
   re-measures the frozen save-rate 0.8244 / 0.9562; for KPK it is a live
   measurement only (typical band ≈ 0.7–0.9), and for KNK E1 is
   *undefined by a theorem*, which the panel states instead of pretending.

## The two T15 endgames

**KNK — the negative control.** A knight checking a king attacks none of
the king's eight neighbours: a (±1,±2) offset plus any unit king step is
never again a knight offset. Every escape square would have to be covered
by the lone white king, and the three neighbours of a corner (a7, b7, b8)
have no common cover — so a knight mate does not exist anywhere. The
retrograde build over all 429,440 states discovers zero mates and the
load-time integrity gate re-proves it on every page view. In the app KNK
is the honest mirror of E1: the particles chase a +3 material edge that
the oracle knows is worth nothing.

**KPK — the promotion boundary.** Pawn single/double pushes are internal;
a promotion move leaves the packed space, and its child (a KQK position)
is probed against the frozen KQK certificate. Queen promotion is
DTM-sufficient: the queen move-set dominates rook and bishop (any R/B
strategy can be mimicked while Black's replies only shrink), and N/B
under-promotions land in KNK/KBK — endgames with no mates at all — so
DTM(c8=Q) ≤ DTM(c8=anything) and a Q-only table is exact. The measured
certificate: 222,558 won states, maximum 56 plies = 28 moves, and
**mates = 0 inside KPK** — the final ply of every win belongs to the
queen after promotion. When a promotion happens on the board, the app
honestly switches to the KQK space (selector + note), and Undo restores
KPK.

## Files

| File | Purpose |
|------|---------|
| `index.html` | single-page app (RU/EN i18n, semantic HTML, ARIA labels) |
| `assets/js/chess.js` | minimal 0x88 engine for KRK/KQK/KNK/KPK with auto-queen promotion (subset of dynamics.py) |
| `assets/js/tb.js` | frozen-tablebase loader + cache, integrity gate, probe, promotion-aware `probeAfterMove`, optimal moves |
| `assets/js/particles.js` | faithful port of the three-layer ParticleSolver |
| `assets/js/audit.js` | live Bellman auditor (independent generator) |
| `assets/js/tree.js` | exact minimal strategy-tree counter (E3); the KPK tree crosses the promotion boundary and continues in the KQK space |
| `assets/js/e1.js` | seeded in-browser E1 replay |
| `assets/js/i18n.js`, `assets/js/app.js` | dictionary and controller |
| `assets/data/tables.js` | AUTO-GENERATED frozen payloads, all four endgames (do not edit) |
| `assets/data/manifest.json` | SHA-256 of the sources and the export |
| `tests/node_harness.js` | 57-check node battery: integrity gates, classical spot probes, a full optimal KPK game to mate through promotion, E1 replays, the vortex (T16) block, the trap classification (T17) block |
| `assets/js/traps.js` | the T17 trap layer (math): per-move certificate classes (optimal/waste/slack/trap/resist/fast) + the frozen census constants |
| `assets/js/vortex.js` | the T16 vortex layer (math): field + metric ensemble + flow-only classifier, constants frozen by E4 |
| `assets/js/vortex_view.js` | the T16 visual storm: canvas particles in the vortex field, descent/trap/escape currents, vortex rings, reduced-motion honoured |

## Run

```bash
# from the repository root — any static server works
python3 -m http.server 8000
# open http://localhost:8000/web/chess-oracle/

# or simply open the file directly (data is embedded as a script tag):
xdg-open web/chess-oracle/index.html        # Linux
termux-open web/chess-oracle/index.html     # Termux/Android
```

Regenerate the data after touching the frozen tables:

```bash
python3 scripts/export_web_tables.py
```

## Data flow

```
results/dtm_{krk,kqk,knk,kpk}.json.gz ──export_web_tables.py──▶ assets/data/tables.js
        (frozen certificates)                                          │
                                                                       ▼
                                        integrity gate (stats + blob recount + flag)
                                                                       ▼
                       probe(state) ──▶ optimal moves ──▶ perfect play
                               └──▶ audit.js (Bellman, live) ──▶ PASS/FAIL banner
```

## Verification battery

```bash
node web/chess-oracle/tests/node_harness.js     # 57 checks, ALL CHECKS PASSED
```

Covers: integrity gates of all four tables; the KRK mate-in-1 and the
frozen E1 example; a full optimal KRK game audited ply-by-ply; KNK drawn
everywhere with a graceful E1=∅; the KPK classical doctrine probes
(c8=Q# mate in 1, the Kb6/Pc7/Ka7 stalemate trick, the opposition draw,
the undefended-pawn capture); T(promotion mate-in-1) = 2 exactly; a
cross-boundary audit and optimal-move set; a full optimal KPK game
(dtm ≥ 20 plies) that promotes and mates with zero audit failures; and
the KPK E1 replay (save-rate ≈ 0.735 at seed 42).

## The vortex layer (T16) — the outcome as flow topology

The **вихрь** button turns on the vortex dynamics: the frozen DTM certificate
is re-encoded on the board as vortices (the eternal swirl around the pieces)
plus descent currents (attraction into the mating squares, strength = DTM
decrease). The classification reads **only the flow**:

* **100% WIN** — descent currents exist, every metric trajectory is captured
  (capture_fraction = 1.000): a converging spiral into the mating net;
* **DRAW** — a drawing resource exists, no forced current anywhere: closed
  orbits, capture_fraction = 0.000. In KNK the *whole* space is closed
  orbits — T15 as topology;
* **LOSS** — every defence is a current into the same net: the defender is
  swept in, capture_fraction = 1.000.

The metric ensemble integrates the damped gradient flow of the cone-envelope
potential `U = min_t J·|x − c_t|` (only minima = the targets). The constants
are frozen by experiment E4 (`results/vortex_e4.json`): 1800/1800 agreement
with the tables, capture separation 1.000/0.000, robust to ±20% perturbations.
The same engine in Python lives in `vortex/vortex_dynamics.py`; the two
implementations agree check-by-check (the harness replays the E4 protocol).

## The trap layer (T17) — moves that change the certificate class

The **ловушки** button classifies every legal move of the current position
against the frozen certificate and highlights the class-changing ones right
on the board:

* **crimson — a trap**: the defender holds a draw, but this move walks into
  a lost position (draw → loss). This is the snare the vortex layer marks
  with J = 1 and sampled E1 measures from the other side;
* **amber — a missed win**: the attacker lets the win slip to a draw
  (win → draw) — E1's "lost" class, shown for every move, not just the
  greedy one;
* **dim amber — a wasteful move**: the win is kept but DTM grows by
  ddtm = v − (d−1) plies — E1's "price of greed", computed exactly;
* **emerald — the most resistant defence** (in lost positions: v = d−1).

The Traps tab prints the per-position structure (optimal / wasteful with
its mean price / traps with the mate distance after the blunder), the
frozen population census (`results/trap_census.json`, produced by
`scripts/trap_census.py` over every legal move of every state of all four
endgames) and the frozen sampled-E1 line — sample against population.

Headline frozen facts: in KRK, 59,624 draw→loss traps exist across 21,764
of the 22,244 drawn Black-to-move states (97.8% of them carry at least one
trap; up to 4 in one position; the deepest trap mates 31 plies later).
KNK has exactly zero traps, zero slack and zero waste — T15 restated in
move-class language.

## Honesty guarantees

* The oracle reads only the frozen certificate — it invents nothing.
* Every property shown is either computed in front of you or quoted from
  the frozen results with a pointer to its generator script.
* The app never claims more than the table knows: drawn positions are
  labelled drawn, the 50-move caveat is printed in the Proof tab.
