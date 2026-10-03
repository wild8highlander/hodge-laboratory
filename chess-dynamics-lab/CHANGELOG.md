# Changelog — chess-dynamics-lab

All notable changes of the program are documented here.
The format follows Keep a Changelog; the project is versioned as X.Y.Z.

## [2.2.0] — 2026-10-01

The **error-corpus program**: v2.1.0 closed with three named targets —
the residual 337 KPK errors, the KRK hot-spot at 3.30%, and whole-game
adjudication through the E9 trajectory model.  v2.2.0 attacks all
three.  The nonlinear basis grows a third append-only family —
**interaction hinge nodes** `max(0, x_a − ka) · max(0, x_b − kb)`
(basis spec v2; v1 payloads load bit-identically) — the KRK specialist
is promoted, and the referee joins the frozen artifacts.  One strict
denial, one elimination, one new epoch; zero new dependencies.

### Added
- **Interaction hinge nodes (basis v2)** (`outcome/nonlinear.py`):
  `ihinge(a, ka, b, kb) = max(0, x_a − ka) · max(0, x_b − kb)` — a
  product of two hinge crests, a localized conjunction cell; 16 nodes
  frozen for KPK from TRAIN-split residual-error diagnostics (deep
  pawn-race, boxed-defender and edge-defence cells; every knot inside
  the live range).  `NonlinearBasis` carries the new family through
  names / expansion / JSON (v1 round-trips unchanged);
  `attach_routes` now MERGES into the existing `nonlinear` block, so
  promoting a second specialist never clobbers the first.
- **E13 — interaction hinges on the residual corpus**
  (`python3 -m outcome interact`): two arms on the identical E8
  protocol against the *frozen production route* — `ihinge` (uniform)
  and `ihinge_w` (error-corpus weights: train-split residual hard
  errors carry weight 1 + 4.0; valid/test never weighted; the
  ensemble/softmax heads accept `sample_weight`, bit-identical when
  None).  **PROMOTION DENIED**: ihinge matches accuracy (0.8332) and
  improves log loss microscopically (0.3746 → 0.3738) with the re-mine
  337 → 323, but fails the strict double gate; the weighted arm
  REGRESSES (0.8138, mine 380) — hard-example upweighting overfits the
  boundary.  Certificate `results/outcome_interaction_e13.json`.
- **E14 — the KRK specialist** (`python3 -m outcome nonlinear --kind
  krk`): the frozen KRK schedule (18 hinges + 10 crosses, pointed at
  the rook-next-to-king / boxed-defender / deep-mate signature of the
  3.30% residual) trained through the same E11 machinery;
  **PROMOTED**: krk test accuracy 0.9655 → **1.0000**, log loss
  0.0675 → 0.0014, hard errors 66 → **0** on the seeded mine; pooled
  accuracy 0.9588 → **0.9658**, log loss 0.0944 → 0.0812; the corpus
  re-mined 710 → 644 rows.  Certificate
  `results/outcome_specialist_krk_e14.json`.
- **Epoch VIII — whole-game adjudication**
  (`outcome/adjudicate.py`, `python3 -m outcome adjudicate`): a
  four-arm referee panel (exact / state / trajectory_gated /
  trajectory_final_only) calls the Result header of whole games from
  the first t+1 oracle-space entries; adjudication curves over
  cutoffs; verdict-flip stability; skip accounting for games that
  never reach a frozen domain.  Certificate **E15**:
  `results/outcome_adjudication_e15.json` — final-entry log loss
  gated 0.0000 vs state 0.1132; accuracy 1.0000 everywhere; 5 of 29
  games honestly skipped (no oracle entries).
- Tests 164 → **181** (interaction basis + v1 compat + route merge +
  sample weights + E13 smoke: 10; the E15 referee: 7); CI gains the
  `interact --smoke` and `adjudicate` steps.
- Docs: README sections 8.11–8.13 and the frozen constants E13–E15;
  outcome/results/tests READMEs; version 2.2.0.

### Changed
- The E12 real-game audit re-frozen against the E14 router: game-level
  model log loss 0.1274 → 0.1132 (the KRK specialist flows through).
- `outcome/nonlinear.py` BASIS_SPEC_VERSION → v2 (append-only; the
  frozen E11 route loads with identical predictions).

### Honest negatives (frozen, not hidden)
- E13: interaction hinge nodes are the right *shape* for the residual
  (mine 337 → 323) but do not move test accuracy — denied; error-
  weighting is actively harmful (mine 380).  The KPK residual frontier
  (337 states) remains the program's open target.

## [2.1.0] — 2026-10-01

The **nonlinear specialist head** (Epoch VII) and the **real-game
pipeline** (Epoch IV completed): the E10 falsification corpus named KPK
as the hot-spot of the linear model, and v2.1.0 answers with a
hinge+cross basis, a gated router and an honest promotion rule — plus a
zero-dependency PGN layer that feeds actual games (classical scores,
engine self-play, tablebase walks) through the player-context layer.
Zero new dependencies; the model file format moves to v3 (v1/v2 still
load).

### Added
- **Epoch VII — the nonlinear specialist head** (`outcome/nonlinear.py`):
  an APPEND-ONLY basis of 48 hinge crests `max(0, x − knot)` (knots
  frozen inside the measured KPK ranges — no dead columns) plus 10
  explicit pairwise crosses, expanding 67 → 125 coordinates for the
  specialist; a `GatedPredictor` routes only the promoted slice, every
  other domain keeps the frozen global head; the A/B runs on the
  identical E8 protocol (same sampler, seed and hash split) with the
  strict promotion rule (win on BOTH accuracy and log loss over the
  untouched test split); resumable via `--checkpoint` (arms cached as
  JSON); certificate **E11** in `results/outcome_nonlinear_e11.json`;
  `python3 -m outcome nonlinear`.
- **E11 verdict — hypothesis CONFIRMED and PROMOTED**: kpk test
  accuracy 0.7684 → 0.8332, log loss 0.5037 → 0.3746, ECE 0.0305 →
  0.0120; hard errors on the seeded hot-spot population 443 → 337;
  pooled (5 domains) accuracy 0.9458 → 0.9588, log loss 0.1205 →
  0.0944. The production model file carries the `nonlinear` block
  (format v3) and `evaluate` reproduces the new certificate
  bit-for-bit; the falsification corpus was re-mined (816 → 710 rows,
  kpk hard-error rate 22.15% → 16.85%, other domains unchanged).
- **The zero-dependency PGN layer** (`outcome/pgn.py`): header
  parsing (with escapes), tokenizer (comments, nested variations, NAGs,
  move numbers), SAN reader over the certified legality machinery
  (castling, en passant with flag checks, promotions, file/rank/
  full-square disambiguation, `PGNError` with the offending ply) and a
  canonical SAN writer that round-trips through the reader; FEN-header
  starts supported.
- **The E12 real-game audit** (`outcome/realgames.py` +
  `data/games/`): every game replays ply by ply; positions inside the
  oracle space are scored against three arms — exact (the theorem),
  model (the router), model+context (the Elo water-filling blend read
  from PGN headers); games without ratings are verified to be strict
  no-ops; result/board consistency is flagged; certificate **E12** in
  `results/outcome_realgames_e12.json`;
  `python3 -m outcome games data/games`.
- **The frozen game corpus** `data/games/`: three public-domain
  classical scores (Réti–Tartakower 1910, Morphy–Brunswick & Isouard
  1858, Anderssen–Kieseritzky 1851), deterministic engine self-play
  games, and 24 tablebase walks with known terminal results carrying
  SIMULATED, labeled Elo headers (aligned / independent alignment);
  regenerated by `scripts/build_game_corpus.py`.
- **E12 verdict — an honest negative result**: on theory-governed walk
  positions the model-vs-exact agreement is 1.0000 (508 entries), and
  the Elo prior measurably WORSENS the game-level log loss (0.1274 →
  0.2103) — the context layer must stay off where exact theory governs,
  and the audit now quantifies that cost instead of assuming it away.
- CLI: `nonlinear` (A/B + promotion + corpus re-mine) and `games`
  (the E12 audit) commands; CI smoke steps for both.

### Changed
- Model file format v3 (`outcome_model.json`): the optional
  `nonlinear` block of gated specialist routes; v1/v2 files still load.
- The falsification corpus `counterexamples/` re-mined against the
  promoted router (E10′: 710 rows; krk 3.30% / kqk 0.35% / kpk 16.85% /
  knk 0 / kbk 0 hard-error rates).
- Tests 124 → 164 (the basis, the router, the payload round-trip, the
  PGN layer, the corpus replay, the audit honesty checks); CI runs the
  nonlinear smoke and the real-games audit.

## [2.0.0] — 2026-10-01

The **Outcome Dynamics program grows to epochs IV–VI** and the exact
foundation gets its maximum honesty pass: every frozen DTM certificate is
rebuilt from an empty table and compared byte-for-byte, a fifth domain
(KBK, the diagonal negative control) joins the family, and the
distillation program receives an A/B-tested target scheme, a bootstrap
ensemble, per-domain calibration, a dedicated Move Impact module, a
Bayesian player-context layer, a trajectory model and a falsification
engine. Zero new dependencies — the whole stack stays pure Python.

### Added
- **Epoch IV — the player-context layer** (`outcome/context.py`): a
  documented Bayesian prior over the model layer (Elo rating gap →
  expected score, water-filling redistribution, optional clock prior at
  30 Elo per doubled ratio, clamped ±150); strict no-op without rating
  input; the exact layer is never blended; the **whole-game split rule**
  `split_of_game` (splitmix64 over the game id) for leak-free
  game-level training; `python3 -m outcome context "<FEN>" --rating-white …`.
- **Epoch V — the trajectory model** (`outcome/trajectory.py`): seeded
  optimal-play walks over the frozen certificates (DTM-optimal attack,
  best defence, seeded wander on draws; KPK promotions followed INTO
  KQK — 231 domain crossings in the certificate run); a gated pooling
  unit (3 gate parameters) with a linear head forecasts the line's final
  outcome; the **forecast curve** ablation (gated vs final-only twin)
  shows history beats the last position at every horizon (t=0: 0.6364 vs
  0.4788); drift surprise rate halved (0.0892 vs 0.2188); certificate
  frozen in `results/outcome_trajectory.json` (E9);
  `python3 -m outcome trajectory`.
- **Epoch VI — the falsification engine** (`outcome/falsify.py` +
  `counterexamples/`): mines the states where the frozen model
  disagrees with the exact oracle (`hard_error` / `low_confidence` /
  `dtm_error`), freezes the curated corpus (CSV + summary JSON +
  generated README; 816 rows at the full run) as a regression benchmark;
  certificate E10; `python3 -m outcome falsify`.
- **Move Impact module** (`outcome/impact.py`): the counterfactual
  surface promoted to a first-class instrument — per-move ΔP(win),
  ΔP(draw), child entropy, exact child DTM and the **pace** (DTM plies
  gained/squandered), move categories (field_flip / swing / quiet),
  robustness index, quiet share, best-move agreement (honestly `None`
  on degenerate won parents); `python3 -m outcome impact "<FEN>"`.
- **KBK domain** (`results/dtm_kbk.json.gz` + `scripts/build_kbk_table.py`):
  K+B vs K, the diagonal negative control — won = mates = 0, the
  insufficient-material theorem proved by exhaustive computation
  (417,228 states, 3,946,992 edges, Bellman-verified). Also fixes the
  v1.5.0 `KeyError` on lone-bishop positions in `detect_domain`.
- **E7 rebuild provenance** (`scripts/rebuild_dtm_tables.py` +
  `results/dtm_rebuild_e7.json`): the whole frozen DTM family rebuilt
  from empty tables; KRK/KQK/KNK/KPK came out **BIT-IDENTICAL**
  (values byte-for-byte, stats as dicts); KBK added and frozen.
- **CI steps** for the falsification and trajectory smokes.

### Changed
- **Phase space v2** (`outcome/features.py`): 40 → **67 coordinates**,
  APPEND-ONLY over the frozen v1 block (old datasets and v1 model files
  stay loadable). New families: pawn structure & promotion geometry
  (doubled/isolated/passed/blocked, promotion distance), strongest-piece
  endgame geometry (distances to both kings, edge/centrality), threat
  field higher moments (peak, coverage, White/Black overlap), king
  freedom, capture availability.
- **Distillation v2** (`outcome/model.py`, certificate E8 in
  `results/outcome_distillation.json`): oracle-shaped soft targets
  (`soft_targets`, τ = 8 plies) A/B-tested against hard one-hot and
  **falsified** (hard 0.9499 acc / 0.1217 logloss vs soft 0.9086 /
  0.3037 — the smoothing blurs the drawn/won boundary); the production
  head is a **3-member bootstrap ensemble** on the winner plus
  **per-domain temperature calibration** fitted on the valid split only
  (deterministic grid + golden refine; valid logloss 0.1243 → 0.1149).
- **Certificate E8**: 100,000 states (20,000 × five domains, seed 2026),
  pooled test accuracy **0.9458** (v1: 0.9305, on a harder task — the
  majority baseline fell 0.6379 → 0.5092 with KBK added), log loss
  0.1205, Brier 0.0731, ECE 0.0066; per domain KRK 0.9655 · KQK 0.9973 ·
  KNK 1.0000 · KPK 0.7684 · KBK 1.0000; DTM head MAE **2.51 plies**
  (v1: 3.18).
- **Outcome Field v0.2** (`outcome/outcome_field.py`): loads the
  ensemble + calibrator, delegates the move surface to `outcome.impact`,
  accepts the Epoch IV context (model layer only), KBK in the exact
  layer, robustness in the panel.
- README section 8 rewritten for epochs I–VI with the new certificates;
  `outcome/README.md`, `results/README.md`, `tests/README.md` updated;
  version bumped to 2.0.0 everywhere.

### Tests
- 92 → **124 pytest tests**: KBK domain + census consistency + the
  KeyError regression, E7 provenance checks, Move Impact (pace, sorted
  surface, robustness), player context (Elo prior, water-filling
  invariants, clock prior, whole-game split stratification), trajectory
  (deterministic optimal walks, domain crossings, model determinism and
  persistence, gated-vs-final contrast), falsification (a deliberately
  broken model must be falsified, corpus round-trip, determinism).

## [1.5.0] — 2026-10-01

The **Outcome Dynamics program (epochs I–III)**: the frozen tablebases stop
being a static certificate and become a supervised benchmark plus the
foundation of a probabilistic outcome predictor. Zero new dependencies —
the whole ML stack is pure Python.

### Added
- **`outcome/` package** — the Outcome Dynamics program, one command line
  (`python3 -m outcome`) over five modules:
  - `tablebase_api.py` (Epoch I): the exact WDL/DTM oracle over the four
    frozen certificates; legality reconstructed from geometry (the blob
    cannot separate legal draws from unenumerated states); `classify_fen`
    for FEN queries, `census_kind` for the live census cross-check.
  - `features.py` (Epoch II): the **phase-space extractor** — 40
    deterministic, tablebase-independent coordinates in five labelled
    groups (material 15, mobility 3, threat fields 8, king geometry 8,
    flow/phase 6); reproduces the frozen constants (mobility 20 → 30
    after 1.e4, field mass 38 per side, E₀ = 0).
  - `dataset.py` (Epoch II): seeded rejection sampling over the packed
    22-bit spaces, uniform and bit-reproducible; full enumeration mode;
    splitmix64-based 70/15/10 hash split (kind-mixed); CSV export.
  - `model.py` (Epoch III): two zero-dependency heads — multinomial
    softmax regression (outcome distribution) and ridge regression (DTM
    in plies); full-batch gradient descent, zero initialisation,
    standardisation fitted on the train split only — bit-reproducible.
  - `metrics.py` (Epoch III): accuracy, log loss, multiclass Brier, ECE,
    macro-F1, reliability tables, confusion, MAE; the majority baseline.
  - `outcome_field.py`: **Outcome Field v0.1** — exact-first P(W/D/L)
    with entropy (bits), criticality (the largest single-move field
    change; the quantitative successor of the T17 trap census), the
    counterfactual move-impact surface, the bare-kings draw rule and an
    honest extrapolation flag for out-of-domain queries.
  - `cli.py`: `analyze` / `export` / `train` / `evaluate` / `report`.
- **Experiment E6** — the tablebase distillation certificate
  (`results/outcome_distillation.json`, seed 2026, 80,000 states):
  pooled test accuracy **0.9305** (majority 0.6379), log loss 0.1647,
  Brier 0.1012, **ECE 0.0101**; KRK 0.9861, KQK 0.9959, KNK 1.0000
  (negative control), KPK 0.7431; DTM-head MAE 3.18 plies vs 6.14 mean
  baseline; the layer ablation map — material 0.8871, **threat (K3)
  0.7056**, flow 0.6548, mobility 0.6545, king 0.6379: the threat field
  carries real outcome information beyond material, and the full model
  beats every single-layer approximation.
- **`results/outcome_model.json`** — the frozen model (weights,
  standardisers, recipe, training envelope, metrics); `python3 -m outcome
  evaluate` re-derives the frozen metrics bit-for-bit on any machine.
- **38 new pytest tests** (54 → 92): oracle probes against classical
  positions, the live KNK census cross-check, feature determinism and
  frozen-constant reproduction, model/metric properties, Outcome Field
  trap detection and extrapolation honesty.
- **CI**: the outcome dynamics smoke experiment (`python3 -m outcome
  report --smoke`) joins the python-core job.

### Changed
- README: new section 8 (The Outcome Dynamics program), renumbered
  sections 9–16, quick-start commands, repository layout, frozen-constant
  block E6, test counts; `pyproject.toml` and `CITATION.cff` to 1.5.0.

## [1.4.0] — 2026-09-30

The MAIN test T7 becomes the **partial-policy verdict**: an explicit ensemble
of named policies instead of a single solver, with honest evidence framing.

### Added
- **Policy ensemble in `large_board_lab.jl`** — five named move-selection
  policies: `PARTICLE` (the three-layer solver, μ/λ), `PRESSURE` (pure K3,
  λ = 1), `MOBILITY` (pure kinetic, μ = 1), `MATERIAL` (pure captures) and
  `RANDOM` (seeded uniform legal mover). Selected via `--policy=a,b,c|all`,
  the menu parameter editor (**C → 19**) or the default
  `PARTICLE + PRESSURE + MOBILITY`.
- **Paired playouts** — every policy faces the identical sampled starts
  (position seed independent of the policy), so per-policy outcome shares are
  directly comparable.
- **Partial-policy verdict machinery in T7**: a per policy × scenario outcome
  table, per-policy pooled verdicts with tiers (`F` forced — Wilson CI floor
  > 50%, `L` leaning — plurality ≥ 75%, `I` inconclusive), a consensus class
  (unanimous / majority / split), the pooled verdict with 95% Wilson CIs, and
  an honest coverage block (unique sampled starts and total plies vs the
  KXK state-space estimate ≈ n²·(n²−1)·(n²−2)·2 — at n = 112 the sampling
  share is printed as ≈ 3e-11). Evidence ladder: FULL > WEAK > ULTRA-WEAK >
  PARTIAL POLICY.
- **Reports**: `policy_matrix.csv` (policy × scenario matrix with tiers),
  the `policy` column in `main_playouts.csv`, new `main_test` JSON block
  fields (`verdict_class`, `consensus`, `evidence_ladder`, `policies[]`,
  `coverage`), a bilingual policy-ensemble section in `summary.md`.
- **Chart 2** now plots per-policy outcome bars with Wilson whiskers
  (fallback to per-scenario bars for single-policy runs).

### Fixed
- The built-in rasterizer crashed on empty text (`text_width` reducing over
  an empty glyph sequence) — `ptext!` now short-circuits empty strings.
- T8's honest-disclaimer wording is now single-policy accurate (the ensemble
  wording stays in T7).

## [1.3.0] — 2026-09-30

The Julia large-board laboratory: the generalized particle dynamics verified
on big matrices up to 112×112, as one self-contained file.

### Added
- **`large_board_lab.jl`** — a single-file Julia laboratory (Base + `Printf`,
  `Dates` only; no packages). Interactive RU/EN menu with a language switcher,
  box-drawing UI, a knight/particle banner and a one-line progress bar with
  ETA. Board sizes up to n = 127 (default **112×112** = 12,544 cells).
- **Test battery T1–T9**: T1 board census (closed forms vs generated graphs,
  directed counts for R/B/N/K and the queen identity, n = 8…112);
  T2 legality battery (10 invariant checks on seeded playouts, incl. the
  K3 field identity and Zobrist incrementality); T3 oracle self-verification
  (structural winning-move chains + the Rh8# landmark); T4 trap census — the
  E1 link, particle blunders measured against the exact DTM oracle
  (win→draw flips, resistance quality of the losing side); T5 scaling
  benchmark to n = 112 (log-log slope ≈ 2.7, polynomial per T14);
  T7 **MAIN TEST** — the solution probe: which outcome the particle dynamics
  implies at n = 112 (draw / WHITE WIN / BLACK WIN, Wilson 95% CIs, honest
  policy-verdict disclaimer referencing `complexity/SOLVING_CHES­S.md`);
  T8 explicit outcome check (`--expect=draw|white|black`);
  T9 flow showcase (K3 field + rook trajectories on 112×112).
- **Exact retrograde oracle** for K+R / K+Q vs K on n×n boards (Bellman
  layered propagation over the packed state space, verified bit-consistent
  with the 8×8 landmarks; n ≤ 13 guard).
- **Zero-dependency charting**: a built-in PNG encoder (zlib fixed-Huffman
  deflate + LZ77 + CRC32/Adler-32) and an SVG writer; four charts × two
  formats at **600 dpi** (7200×4800): scaling log-log with O(n²)/O(n⁴)
  references, outcome bars with Wilson CI whiskers, the 112×112 K3 flow
  heatmap with trajectories and colorbar, and the max-DTM power fit.
  Glyphs: embedded 32×32 bitmap font (ASCII + Cyrillic) rasterized from
  DejaVu Sans (Bitstream Vera license).
- **Reports per run**: `log.txt`, `report.json`, `main_playouts.csv`,
  `trap_census.csv`, `summary.md` in `results/large_board_lab/run_<stamp>/`.
- CI step `julia large_board_lab.jl --selftest`; README §2.1; a frozen
  showcase run in `results/large_board_lab/`.

## [1.2.0] — 2026-09-30

The solution-level ladder: what "solved like checkers" means, measured on
the frozen certificates.

### Added
- **Experiment E5** (`scripts/solve_levels_e5.py` → `results/
  solve_levels_e5.json`): which of the three solving levels (ultra-weak /
  weak / strong, Allis's taxonomy) each frozen endgame space sits at.
  Strong: 100% coverage per space, cross-asserted against the table
  headers (1,528,356 states total). Ultra-weak: 11 classical doctrine
  anchors probed live and asserted (c8=Q#, both stalemate traps, the
  frontal-opposition draw vs its lost twin — win in 18 plies, the
  shoulder line — the deepest win in 28 moves, the king-in-front rule,
  the undefended-pawn resource). Weak: full optimal principal
  variations plus the minimal DTM-greedy winning-strategy trees from
  canonical starts (KRK 2,496 nodes / KQK 132 / KPK 6,558 — 0.04–2% of
  the space), with the E3 argmax certificate reproduced independently:
  **500,900 = 500,900**. Deepest states: exact argmax scans per side
  (KRK 31/32 plies ×916/×3,056 positions; KPK 55/56 ×6/×4). The wall:
  exact big-int extrapolation — a full-chess table at 1 B/state ≈
  3.21·10²¹ × world storage, 1.53·10²⁸ years at 10⁹ states/s.
- **Note N2** (`complexity/SOLVING_CHESS.md`): "Can chess be solved like
  checkers? — an honest answer": the formal three-level taxonomy,
  Chinook's 2007 weak solution mapped ingredient-by-ingredient onto this
  program's architecture, what does NOT count as a solution
  (Stockfish/AlphaZero strength, subgame tablebases, human matches,
  consensus beliefs), and what would actually count (exhaustion at
  4.8·10⁴⁴ states — off every hardware curve; or a general draw
  invariant for 32-piece play — an open problem of mathematics).
- **pytest battery extended to 54** (`tests/test_solve_levels.py`):
  coverage, anchors, PV/tree agreement, the E3 cross-check, live
  re-probes, deepest-vs-header consistency.

### Fixed
- **T17 trap census universe** (`scripts/trap_census.py`,
  `results/trap_census.json`): the census now enumerates exactly the
  builders' state universe — the KPK pawn is restricted to ranks 2–7,
  matching `build_kpk`. A first draft counted 55,920 impossible rank-8
  pawn states (all drawn) on top of the real space; caught by the E5
  cross-assert against the frozen table header on 2026-09-30. The
  headline trap counts were never affected (phantom states have no won
  neighbours): KRK 59,624 / KQK 32,896 / KPK 173,786 traps, deepest 55
  plies — all unchanged; only the KPK drawn-state denominators shrank
  (98,380 → 70,420 BTM drawn, optimal_share 0.1831 → 0.2143). The web
  FROZEN census (`web/chess-oracle/assets/js/traps.js`) updated
  accordingly; node harness re-run: ALL CHECKS PASSED.
- `complexity/README.md`: removed a duplicated "browser side" section.

## [1.1.0] — 2026-09-30

The endgame family grows to four certificates, and the threat field learns to move.

### Added
- **Two new frozen bases** (`results/`): `dtm_knk.json.gz` — the negative control
  (429440 states, **won = 0, mates = 0**: a knight mate does not exist, the
  classical insufficient-material draw certified by exhaustion — T15); and
  `dtm_kpk.json.gz` — the KPK base (331352 states, 222558 won, **no in-space
  mates**, max DTM 56 plies = 28 moves) built with the **promotion boundary**:
  a promotion child inherits its exact DTM from the frozen KQK certificate
  (queen promotion is DTM-sufficient by move-set domination; N/B
  under-promotions land in mate-less KNK/KBK). Both carry an independent
  Bellman pass over all states plus classical doctrine spot checks
  (`scripts/build_knk_kpk_tables.py`).
- **chess-oracle**: the endgame selector now offers K+N vs K and K+P vs K; the
  engine (`chess.js`) gained knights, pawns and auto-queen promotion; the
  probing layer (`tb.js`) gained the promotion-aware `probeAfterMove` and a
  table cache; the strategy-tree explorer threads the kpk→kqk space through
  the recursion, so the explicit certificate crosses the promotion boundary
  exactly; a promotion on the board honestly switches the app into the KQK
  space (with an Undo path back); KNK is presented as what it is — a theorem
  (∞ everywhere, E1 undefined, the T15 note in the meter panel).
- **Node battery extended to 41 checks** (`web/chess-oracle/tests/node_harness.js`):
  integrity gates of all four tables, the KPK doctrine probes, T(promotion
  mate-in-1) = 2 exactly, a full optimal KPK game to mate through promotion
  with zero audit failures, and the live KPK E1 replay.
- **chess-particles — Θ-flow animation**: a second field mode in which one
  glowing quantum streams along every attacker→target incidence of Θ(c)
  (gold — White attackers, cyan — Black), golden-ratio phase stagger, additive
  blending, a smooth crossfade of the whole field between positions,
  `prefers-reduced-motion` honoured; new toggle + legend + RU/EN strings.

### Verified
- node harness: 41/41 ALL CHECKS PASSED; browser E2E: KPK autoplay promoted
  and mated with 24 positions audited, 0 failures; protocol C1–C10 still
  10/10 in the browser; pytest 36 passed; no console errors, no mobile
  overflow in either application.

## [1.0.0] — 2026-09-30

The initial public release of the program. Everything below shipped together.

### Added
- **Core**: `dynamics.py` — the single-file laboratory: 0x88 board with full legal
  move generation (castling, en passant, promotion, checks), the three-layer particle
  model (K3 threat fields, TORUS Lagrangian, KLEIN flow with t* termination and the
  damped billiard γ = π⁴/256), D4/V4 group algebra, graph censuses, alpha-beta search
  with quiescence and MVV-LVA ordering, the mate solver with PV, retrograde KRK/KQK
  bases (22-bit packing, CSR predecessors, Bellman verification), Zobrist hashing over
  splitmix64 with an explicit inverse, protocol C1–C9, plots, CLI
  (`--report --run Ck --deep --analyze --mate --play --plots`).
- **Engine package**: `engine/particles.py`, `engine/mate_solver.py`,
  `engine/game_player.py` (with deterministic self-play), `engine/analyzer.py`.
- **Polyglot core**: the C1–C10 battery in seven languages (Python, C, Rust, Go,
  Julia, JavaScript, Java) with a byte-identical verdict; `polyglot/run_all.sh`.
- **Results**: the KRK and KQK DTM bases (gzip JSON), the closed knight tour, the
  frozen `baseline_c1_c9.json`.
- **Monographs**: the main monograph «Chess Particle Dynamics» (12 chapters,
  2 appendices, 5 figures) and the 12 theorem monographs T01–T12 — each in RU and EN,
  each in PDF (Template 03/04 covers, tectonic) and DOCX (R5 covers, docx-js, TOC
  field + placeholders); LaTeX and JS generators under `monograph/src/`.
- **Web laboratory**: `web/chess-particles/` — canvas particles, threat-field heatmap,
  Lagrangian panel, t* billiard card, 12 theory cards, the honestly computed browser
  protocol C1–C10, RU/EN i18n.
- **Docs**: the GitHub Pages landing (`docs/`), the publication guide
  (`INSTRUCTION.md`), the one-command push script (`scripts/termux_push.sh`).
- **CI**: the protocol on three Python versions, deep perft, the pytest suite, the
  self-play determinism, the seven-language polyglot battery, the Node sanity run of
  the web core; the Pages deployment workflow.

### Verified
- protocol C1–C9: ALL CHECKS PASSED (local, all Python versions);
- polyglot: 10/10 in Python, C, JavaScript locally; Rust/Go/Julia/Java in CI;
- pytest: 36 passed;
- KRK max DTM 16 moves, KQK max DTM 10 moves — matching the classical tablebases;
  Bellman: 0 violations over all states;
- perft 20/400/8902/197281/4865609; the divide(3) table matches the reference.

[1.0.0]: https://github.com/wild8highlander/chess-dynamics-lab/releases/tag/v1.0.0

## [1.1.0] — T17 traps + generalized n×n boards

### Added
- **chess-oracle · T17 «ловушки»**: a button + tab that classify every legal
  move against the frozen certificate (optimal / wasteful with the exact
  ddtm / missed wins / draw→loss traps / most resistant defence), highlight
  the class-changing moves on the board (crimson / amber / dim amber /
  emerald), and print the frozen population census next to the frozen
  sampled-E1 line (`scripts/trap_census.py` → `results/trap_census.json`).
- **chess-particles · n×n boards (T14)**: a board-size selector (8×8, 6×6,
  5×5, 4×4) with KRK demo presets verified won by the exact retrograde
  oracle; the engine, threat fields, Θ-flow, Lagrangian panel, billiard and
  the t\* velocity cap all follow the board size; a complexity card
  re-enumerates the exact KRK state space live (`krkSpace(n)`) against the
  frozen E2 rows — digit-for-digit on every n.
- `scripts/trap_census.py`, `scripts/verify_nxn_presets.py`,
  `results/trap_census.json`; node batteries extended to 57 (oracle) and
  the T14 block (particles); E2E browser checks + screenshots.

### Verified
- pytest 48/48 · dynamics.py --report ALL CHECKS PASSED ·
  node_harness 57/57 · test_web_engine ALL (incl. krkSpace = E2 bit-exact) ·
  trap_census T17 PASSED · verify_nxn_presets PASS ·
  E2E: no console/page errors, mobile 390px without overflow on both apps.
