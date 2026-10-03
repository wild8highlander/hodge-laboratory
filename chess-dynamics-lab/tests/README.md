# tests/ — the pytest suite

181 tests over the core, the engine package, the frozen baseline, the
vortex layer, the E5 solution ladder and the outcome program (epochs
I–VII + the real-game pipeline). Run:

```bash
python3 -m pytest tests/ -q          # fast, ~30 s
python3 -m pytest tests/             # verbose
```

## Coverage

| Group | Tests | What is pinned |
|---|---|---|
| move generation | 8 | perft(1..4), the divide(3) split, castling rights, en-passant edge cases, promotion, legality under check |
| board algebra (C1) | 3 | V4 orbits 20, D4 orbits 10 (Burnside), color parity |
| graph censuses (C2) | 3 | edge counts R448/B280/N168/K210/Q728 |
| mobility (C3) | 3 | sums 420/336/560/896/1456, maxima, the 105 ceiling |
| flow (C4) | 3 | t\* identities over a case grid, the damped path ratio 1.0 (γ = π⁴/256) |
| fields (C6) | 3 | mass 38/38, equivariance 0 violations pawnless, anomaly 176 |
| energy (C7) | 2 | mobility 20 → 30 after 1.e4, E determinism |
| mates (C8) | 5 | Morphy 3 plies (key a1a6), ladder, NR-in-1, retro stats KRK/KQK, Bellman spot |
| zobrist (C9) | 3 | splitmix64 vectors, the inverse round-trip, incremental = full over a playout |
| knight tour (C10) | 2 | 64 unique squares, closure d6→f5 |
| engine package | 3 | self-play determinism, the analyzer read-out, the facade |
| baseline | 3 | `results/baseline_c1_c9.json` matches the live protocol |
| vortex (E4) | 12 | table integrity, flow-vs-table agreement, capture separation, robustness |
| E5 ladder | 6 | solution-level statistics, strategy trees, the wall arithmetic |
| **outcome oracle (Epoch I)** | 12 | classical exact values (box mate, mate in 1, the KPK win/draw doctrines), legality and illegality, domain detection, FEN round-trips, the live KNK census vs the frozen stats |
| **outcome features (Epoch II)** | 6 | the frozen constants (mobility 20/20 → 30, field mass 38/38, E₀ = 0), determinism, schema and group integrity, king-zone pressure |
| **outcome model (Epoch III)** | 11 | deterministic sampling and legality, kind-aware hash split, softmax convergence/reproducibility/persistence, ridge fits linear data, metric bounds, calibration table |
| **Outcome Field v0.1** | 9 | exact-first sources, entropy 0 in exact domains, illegal positions reported honestly, bare-kings draw, the trap detector (criticality 1.0 at the critical move), the extrapolation flag, the frozen-certificate re-evaluation |
| **KBK domain (v2)** | 6 | the all-draw blob scan over the whole certificate, legality shapes, classical corner positions, domain detection (the v1.5.0 KeyError regression), KINDS append-only order |
| **E7 provenance (v2)** | 3 | the rebuild artifact: all_ok, per-domain bit-identity flags, the KBK stats (won = mates = 0, 417228 states) |
| **Move Impact (v2)** | 5 | the mate-in-1 pace economics (max pace = 1), argmin child DTM = parent − 1, full robustness on draws, surface completeness and sort order, the honest `None` agreement on degenerate ΔW |
| **player context (Epoch IV)** | 8 | Elo expectation bounds/symmetry, strict no-op rules, monotonicity in the prior, the water-filling draw-share stability, strong-prior extremes without division by zero, the clock prior, whole-game split determinism and 70/15/10 stratification |
| **trajectory model (Epoch V)** | 6 | the DTM-optimal walk reaches mate exactly, walk determinism, KPK→KQK domain crossings, whole-game split grouping, gated fit determinism + persistence, the gated-vs-final contrast |
| **falsification (Epoch VI)** | 3 | a deliberately broken model is falsified, the corpus CSV/JSON/README round-trip, mining determinism |
| **nonlinear head (Epoch VII)** | 11 | basis append-only naming and validation (unknown names rejected), hinge/cross values on real records, vector/matrix agreement, JSON round-trip, every knot inside the live KPK population, router fall-through and slice routing, payload route round-trip through `load_heads`, the tiny-protocol A/B (no promotion), unknown-kind rejection, re-mine bounds |
| **PGN layer (E12)** | 14 | header parsing with escapes, multi-game files, comment/variation/NAG stripping, FEN-header starts, castling both sides, e.p. flag, promotions, file/rank disambiguation, illegal/ambiguous SAN rejection, annotation tolerance, writer suffixes, corpus round-trips, `moves_between`/terminal states, result helpers |
| **nonlinear basis v2 (E13/E14)** | 10 | interaction-hinge values/names/rejection, v1 payload round-trip bit-compat, frozen E11 route identity, interaction knots inside live ranges (kpk+krk), attach-merge keeps both routes, sample weights bit-identical when None / effective when set / zero-mass rejection, E13 smoke |
| **adjudication (E15)** | 7 | oracle-step extraction on a walk game, four-arm adjudication rows + classical-skip honesty, cutoff clamping, curve/final shapes, corpus accounting + run-to-run determinism, dim-mismatch guard, empty-corpus guard |
| **real games (E12)** | 7 | the no-rating no-op contract, ratings → PlayerContext, bad headers ignored, audit rows on a walk game (blend moves toward the prior), audit honesty on E10 hard-error states, corpus end-to-end aggregation, CLI smoke |

## Principles

- The suite reads the **frozen baseline** and compares against the live computation —
  the theory and the executable share one source of truth.
- No network, no fixtures beyond `results/`, runs on the standard library + pytest.
- A test that cannot fail honestly is not included (the theorem T12 honesty rule).
