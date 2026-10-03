# outcome/ — the Outcome Dynamics program (epochs I–VIII)

The engine (`dynamics.py`, `engine/`) answers *what is the best move*.
This package answers a different question: **what is the probability
distribution of the game's result from a position** — and it refuses to
guess where it cannot know.

The eight epochs, each certified:

| Epoch | Layer | Module | What it does |
|---|---|---|---|
| **I** | exact foundation | `tablebase_api.py` | exact WDL + DTM over the five frozen certificates (KRK/KQK/KNK/KPK/KBK); legality from geometry; live census cross-check; E7 rebuild provenance |
| **II** | phase space | `features.py` · `dataset.py` | 67 deterministic, tablebase-independent coordinates (v2, append-only); seeded sampling + splitmix64 hash splits + CSV export |
| **III** | distillation | `model.py` · `metrics.py` | zero-dependency softmax / ridge heads; hard-vs-soft target A/B; bootstrap ensemble; per-domain temperature calibration; calibration-first benchmark (E8) |
| **IV** | player context | `context.py` | Bayesian Elo/clock prior over the model layer; the whole-game split rule |
| **V** | trajectories | `trajectory.py` | seeded optimal-play lines; gated pooling model; forecast curves vs the no-history twin (E9) |
| **VI** | falsification | `falsify.py` | the model vs the oracle: the curated `counterexamples/` corpus (E10, re-mined after E11) |
| **VII** | nonlinear head | `nonlinear.py` | basis v2: hinge + cross + interaction-hinge nodes; gated specialist router; honest promotion (E11 kpk / E13 residual / E14 krk) |
| — | real games | `pgn.py` · `realgames.py` | zero-dependency PGN/SAN replay over the certified legality machinery; real games scored through the exact/model/context arms (E12) |
| **VIII** | adjudication | `adjudicate.py` | whole-game referee: four arms call the Result header from the oracle-space prefix of a game (E15) |

On top sits **Outcome Field v0.2** (`outcome_field.py`): the exact-first
outcome field F(x) = (P_white, P_draw, P_black) with entropy, criticality
and the counterfactual move-impact surface (`impact.py`).

## Quick start

```bash
# the Outcome Field panel of a position (exact oracle in tablebase domains)
python3 -m outcome analyze "8/3K4/8/8/8/8/8/kR6 b - - 0 1" --moves

# the dedicated counterfactual impact surface (pace economics included)
python3 -m outcome impact "6k1/R7/6K1/8/8/8/8/8 w - - 0 1" --max-moves 30

# the player-context prior (model layer only; exact answers untouched)
python3 -m outcome context "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" \
    --rating-white 2400 --rating-black 1800

# export the dynamics dataset (FEN + 67 features + exact labels + split)
python3 -m outcome export --kind krk --limit 20000 --out ds_krk.csv

# train and freeze the outcome model (A/B targets + ensemble + calibration)
python3 -m outcome train --per-kind 20000 --epochs 30 --members 3 --ablation

# re-check the frozen model on its deterministic test split
python3 -m outcome evaluate

# the full E8 certificate (sample -> A/B -> ensemble -> calibrate -> report)
python3 -m outcome report --per-kind 20000 --out results/outcome_distillation.json
python3 -m outcome report --smoke                    # CI-sized: ~1 minute

# the Epoch V trajectory certificate (E9)
python3 -m outcome trajectory --per-kind 250

# the Epoch VI falsification corpus (E10) -> counterexamples/
python3 -m outcome falsify --per-kind 2000

# the Epoch VII nonlinear specialist head (E11: A/B + promotion)
python3 -m outcome nonlinear --per-kind 20000

# the E12 real-game audit over the bundled corpus
python3 -m outcome games data/games
```

## The honesty rules

1. **Exact first.** Positions inside a frozen domain are answered by the
   Bellman-verified certificate; the model is never consulted there.
2. **No label leakage.** No feature ever reads a tablebase value.
3. **No fake confidence.** Out-of-domain model answers are flagged as
   extrapolations; the context layer never touches an exact answer;
   calibration is fitted on the valid split only.
4. **Everything is re-derivable.** `scripts/rebuild_dtm_tables.py`
   rebuilds the whole frozen family and compares byte-for-byte (E7);
   `evaluate` reproduces the E8 certificate bit-for-bit.

See the repository README, section 8, for the full story and the
frozen numbers.
