# results/ — the frozen certificates

The data files of the program. They are **inputs to the verification**, not artefacts:
the protocol and the tests load them and compare against the live computation. A
mismatch is a bug by definition — and by convention the implementation is fixed, not
the file.

## Files

| File | Size | Content |
|---|---|---|
| `dtm_krk.json.gz` | ~124 KB | the KRK retrograde base: DTM per packed state (22 bits: `wk | wq<<7 | bk<<14 | stm<<21`), 399112 realizable states, 4447032 edges, max DTM 32 plies = 16 moves |
| `dtm_kqk.json.gz` | ~103 KB | the KQK base: 368452 states, 4869496 edges, max DTM 20 plies = 10 moves |
| `dtm_knk.json.gz` | ~6 KB | the KNK base — the **negative control**: 429440 states, 3521256 edges, **won = 0, mates = 0** (a knight mate does not exist — T15 proved by exhaustion; the web integrity gate re-proves it on every load) |
| `dtm_kpk.json.gz` | ~117 KB | the KPK base: 331352 states, 2125630 edges, 222558 won, **mates = 0** (every KPK mate is delivered after promotion), max DTM 56 plies = 28 moves; the promotion boundary inherits exact DTM values from the frozen KQK certificate |
| `dtm_kbk.json.gz` | ~6 KB | the KBK base (v2) — the **diagonal negative control**: 417228 states, 3946992 edges, **won = 0, mates = 0** (a lone-bishop mate does not exist — the insufficient-material theorem proved by exhaustion; two geometries, one verdict with KNK) |
| `knight_tour.json` | ~2 KB | the closed Warnsdorff knight tour from f5: 64 squares, closure d6→f5 |
| `baseline_c1_c9.json` | ~6 KB | the frozen protocol values: perft chain, censuses, mobility, field mass, anomaly, energy, splitmix64 vectors, node counts, base statistics, Bellman 0 |
| `vortex_e4.json` | ~6 KB | the E4 report (T16): frozen ODE constants, 1800/1800 flow-vs-table agreement with capture separation 1.000/0.000, exact per-class state counts (KRK/KQK WTM-drawn = 0), doctrine anchors, ±20% robustness 8×480/480 |
| `trap_census.json` | **T17** — the exhaustive move-class census over all four frozen endgames: traps (draw→loss), slack (win→draw), waste (win kept, DTM grows) per side and class; the population twin of sampled E1. The census universe equals the builders' exactly (the KPK pawn lives on ranks 2–7) — cross-asserted against the table headers by E5 |
| `solve_levels_e5.json` | **E5** — the solution-level ladder (companion of `complexity/SOLVING_CHESS.md`, note N2): strong coverage 100% per space, 11 live-asserted doctrine anchors, explicit weak certificates (PV + minimal strategy trees, E3 argmax reproduced independently: 500,900 = 500,900), exact deepest-state argmax per side, and the measured wall to 32 pieces |
| `outcome_distillation.json` | **E8** — the tablebase distillation certificate (epochs I–III, v2 recipe): 100,000 states sampled from the five frozen domains (seed 2026, splitmix64 hash split 70/15/10), the 67-coordinate phase space, the hard-vs-soft target A/B, the 3-member bootstrap ensemble + per-domain temperature calibration; pooled test accuracy 0.9458 (majority 0.5092), log loss 0.1205, Brier 0.0731, ECE 0.0066; the per-domain table and the 7-group layer ablation map; the A/B verdict (soft targets falsified) is frozen in the recipe |
| `outcome_model.json` | the frozen outcome model distilled from E8: ensemble + single softmax + ridge weights, feature standardisers, the calibration layer, the training recipe (kinds, seed, epochs, members), the training envelope (the honesty guard behind the extrapolation flag) and the frozen metrics; `python3 -m outcome evaluate` re-derives them bit-for-bit |
| `outcome_trajectory.json` | **E9** — the trajectory certificate (epoch V): 1,250 seeded lines (horizon 40, whole-game split, 231 KPK→KQK domain crossings); the gated history-pooling model vs the final-only twin as forecast curves (t=0: 0.6364 vs 0.4788; t=20: 1.0000 vs 0.9394) and the drift surprise rates (0.0892 vs 0.2188) |
| `outcome_nonlinear_e11.json` | **E11** — the nonlinear specialist head (epoch VII, v2.1.0): the hinge+cross basis (67 → 125 coordinates), the gated router A/B on the identical E8 protocol; kpk test acc 0.7684 → 0.8332, log loss 0.5037 → 0.3746; hard errors 443 → 337; the promotion decision and the re-mined corpus counts |
| `outcome_realgames_e12.json` | **E12** — the real-game audit (epoch IV, re-frozen after E14): 29 games / 508 oracle entries scored at game level against the Result header for the exact / model / model+context arms; the no-op honesty checks and the measured cost of the Elo prior on theory-governed positions |
| `outcome_interaction_e13.json` | **E13** — interaction hinge nodes on the residual KPK corpus (epoch VII, v2.2.0): basis v2 (67 → 141), error-corpus weighted arm; ihinge acc 0.8332 / logloss 0.3738 / mine 337→323, ihinge_w regresses; PROMOTION DENIED (the honest negative) |
| `outcome_specialist_krk_e14.json` | **E14** — the KRK specialist (epoch VII): the 3.30% hot-spot eliminated — krk test acc 0.9655 → 1.0000, logloss 0.0675 → 0.0014, hard errors 66 → 0; PROMOTED, pooled 0.9588 → 0.9658 |
| `outcome_adjudication_e15.json` | **E15** — whole-game adjudication (epoch VIII): the four-arm referee over 29 games / 508 entries; final-entry logloss gated 0.0000 vs state 0.1132; flips 0.0000; 5 games honestly skipped |
| `dtm_rebuild_e7.json` | **E7** — the rebuild provenance: every frozen DTM certificate re-derived from an empty table by the checked-in builders; KRK/KQK/KNK/KPK compared **BIT-IDENTICAL** (values byte-for-byte after gzip decompression, stats as dicts), KBK built and frozen |

## Both maxima match the classical tablebases

The maxima — **16 moves (KRK)** and **10 moves (KQK)** — agree with the published
tablebase values that have been known for decades. This is the external cross-check
that self-verification cannot provide. The bases additionally carry an internal
certificate: the Bellman optimality equation verified over **every** state with zero
violations. The two newer bases carry the same internal certificate plus classical
doctrine spot checks (opposition draws, the c8=Q# corner, stalemate traps), and KNK
adds an external one of its own: the published result that K+N vs K is a draw.

## Regeneration

```bash
python3 dynamics.py --run C8                    # rebuilds KRK/KQK, compares with the files
python3 dynamics.py --run C5 --deep             # re-freezes the perft chain
python3 scripts/build_knk_kpk_tables.py both    # rebuilds KNK/KPK (Bellman + spot probes)
python3 scripts/build_kbk_table.py              # rebuilds KBK (the diagonal control)
python3 scripts/rebuild_dtm_tables.py           # E7: rebuild ALL five + provenance (~1 min)
python3 scripts/export_web_tables.py            # re-exports the DTM spaces to the web oracle
python3 scripts/vortex_e4.py 150                # rebuilds the E4 vortex report (~6 min)
python3 scripts/trap_census.py                  # rebuilds the T17 census (~1 min)
python3 scripts/solve_levels_e5.py              # rebuilds the E5 ladder report (~1 min)
python3 -m outcome report --per-kind 20000      # rebuilds E8 + the frozen model (~9 min)
python3 -m outcome trajectory                   # rebuilds E9 (~6 min)
python3 -m outcome nonlinear --per-kind 20000   # rebuilds E11 + promotes (~5 min)
python3 -m outcome games data/games             # rebuilds E12 (~1 min)
python3 -m outcome interact --per-kind 20000    # rebuilds E13 + promotion rule (~5 min)
python3 -m outcome nonlinear --kind krk --per-kind 20000   # rebuilds E14 (~5 min)
python3 -m outcome adjudicate data/games        # rebuilds E15 (~1 min)
python3 -m outcome falsify --per-kind 2000      # rebuilds E10 -> counterexamples/ (~1 min)
python3 -m outcome evaluate                     # re-check the frozen model on its test split
```

The files are written by the core itself (`dynamics.py`), so any regeneration is
reproducible bit-for-bit (fixed seeds, deterministic ordering).

## Format

The DTM files are gzip-compressed JSON with the header:

```json
{
  "piece": "R",
  "packing": "wk | wq<<7 | bk<<14 | stm<<21 (7-bit 0x88 squares)",
  "states": 399112,
  "edges": 4447032,
  "won": 376868,
  "mates": 216,
  "max_plies": 32,
  "dtm": [ ... per-state ply counts, -1 = not won ... ]
}
```

© 2026 Isaev Iskhak Khamzatovich. All rights reserved. See [../LICENSE](../LICENSE).
