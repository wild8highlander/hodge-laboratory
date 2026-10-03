# vortex — the vortex-value correspondence (T16)

The vortex layer re-encodes the frozen DTM certificates as the **topology of a
planar flow** on the 8×8 board, so that the outcome of a perfect game becomes
literally visible — and machine-classifiable — in the particle dynamics:

| Game value (side to move) | Flow topology | The metric ensemble |
|---|---|---|
| **WIN 100%** (strong side to move, won) | a descending spiral **sink**: descent currents into the mating squares | every trajectory captured: `capture_fraction = 1.000` |
| **DRAW** (a drawing resource exists) | **closed orbits**: no forced current anywhere — pure vortex rotation | nothing is ever captured: `capture_fraction = 0.000` |
| **LOSS** (weak side to move, won for the opponent) | the same net, but **every defence feeds it**: all targets descend | the defender is swept in: `capture_fraction = 1.000` |
| mate on the board | the **terminal sink**: no moves, no currents | captured by definition |

## The field (per state)

* **vortices** — fixed-circulation rotation centres at the three pieces
  (circulation Γ = 0.9): pure rotation, the "eternal swirl" of drawn
  positions;
* **currents** — one per legal move, classified by the child value read from
  the frozen table (child value **excludes** the move ply; a KPK promotion
  child is valued through the frozen KQK certificate exactly as in the table
  build, T15):
  * `escape` — the child is drawn (or the piece is captured): J = 0, the
    drawing resource is a closed orbit;
  * `descent` — the child is won with a smaller value: J = d − v ≥ 1, the
    Lyapunov ladder down to the mate;
  * `neutral` — the child is won without progress: the weak current
    J = 0.5 (still inside the basin);
  * `trap` — a blunder direction of the *defender* in a drawn position:
    J = 1 — the snare that experiment E1 measures independently
    (17.56% of greedy ParticleSolver moves fall into exactly such currents).

## The two fields (an honest separation)

* the **metric field** (the classifier) carries only the *forced* currents of
  perfect play (descents + neutrals) and integrates the **damped gradient
  flow of the lower envelope of cones** `U(x) = min_t J·|x − c_t|` — a
  potential whose *only* minima are the targets themselves, so no spurious
  equilibria exist and every trajectory ends at some target;
* the **visual field** (the web animation) adds the vortices with an
  in-basin swirl suppression (`swirl` → `1/(1 + 3·basin)`): captured
  trajectories spiral (the eye of the storm collapses onto the sink), while
  drawn positions keep closed orbits forever.

## The classifier reads ONLY the flow

`classify_by_flow` never probes the table at classification time:

* mover strong: descents exist → **WIN** (gate: measured
  `capture_fraction ≥ 0.98`), else **DRAW**;
* mover weak: an escape exists → **DRAW**, else descents → **LOSS**
  (same capture gate);
* mate on the board → the terminal **LOSS**;
* a structural DRAW whose measured field captured everything raises —
  the layer refuses to lie.

## Experiment E4 — the frozen calibration

`scripts/vortex_e4.py` draws seeded stratified samples from all four frozen
endgames (KRK/KQK/KNK/KPK × WTM/BTM × won/drawn), builds the field, integrates
the metric ensemble and compares the flow-only class with the table verdict:

```
agreement: 1800/1800 = 100.00%
margins:   won/loss capture_fraction >= 1.000, drawn <= 0.000
robustness: 8 perturbations (kappa/zeta/gamma/j_neutral ±20%) — 480/480 each
anchors:   mate-krk, deepest-krk, mate-kqk, deepest-kqk, deepest-kpk,
           krk-box-wtm, krk-box-btm, knk-rotation — all OK
```

The exact per-class state counts are themselves frozen results — notably:

* **KRK and KQK have NO drawn states with the strong side to move** — every
  legal WTM state is won (175 168 of 175 168 in KRK, 144 508 of 144 508 in
  KQK); the draw exists only as a defender-to-move resource (22 244 + 23 048
  states) or a capture;
* KNK has no won states at all (T15) — the whole space is closed orbits;
* KPK has all four classes (124 954 / 93 518 / 97 604 / 126 340).

The report lands in `results/vortex_e4.json` together with the frozen ODE
constants (`FROZEN_VORTEX`).

## The JS port

`web/chess-oracle/assets/js/vortex.js` is a faithful port (same constants,
same lattice, same classifier); `vortex_view.js` renders the visual storm —
golden descent arrows, crimson traps, silver dashed escapes, dashed vortex
rings and a glowing particle ensemble converging into (or orbiting forever
outside) the mating net. The oracle's **вихрь** button turns the layer on;
the badge names the outcome, the *Вихрь* tab shows the live metrics.

## Files

| File | Content |
|---|---|
| `vortex/vortex_dynamics.py` | the field, the metric ODE, the flow classifier |
| `scripts/vortex_e4.py` | the E4 calibration experiment (freezes the constants) |
| `tests/test_vortex.py` | 12 pytest tests (doctrine fields, separation, agreement) |
| `results/vortex_e4.json` | the frozen report |
| `web/chess-oracle/assets/js/vortex.js` | the JS port (math) |
| `web/chess-oracle/assets/js/vortex_view.js` | the JS visual layer (canvas) |

## Reproduction

```bash
python3 scripts/vortex_e4.py 150        # ~6 min, must end with E4 PASSED
python3 -m pytest tests/test_vortex.py  # 12 tests
node web/chess-oracle/tests/node_harness.js   # 49 checks incl. the vortex block
```

## Statement (T16)

For every state of the four frozen endgames, the vortex field built from the
DTM certificate satisfies: the state is won for the side to move **iff** the
flow contains descent currents and the metric ensemble is captured in full;
drawn **iff** a drawing resource exists and no forced current reaches the
defender's orbits; lost **iff** every defence is a current into the same net.
The correspondence is exact (E4: 1800/1800), separable with margin
(1.000/0.000) and robust (±20% constant perturbations keep 100%).
