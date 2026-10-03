# Can Chess Be Solved Like Checkers? — An Honest Answer

chess-dynamics-lab · complexity note N2 · author: Isaev Iskhak Khamzatovich

> **The question.** "Решить шахматы, как шашки" — to solve chess the way
> checkers were solved: a *mathematical proof* of how the game ends under
> perfect play by both sides from the very start, plus a strategy that
> guarantees it. Not a stronger engine — a theorem. What exactly do the
> levels of solving mean, what did Chinook actually prove in 2007, and
> where does this program stand?

## 0. The verdict in five lines

1. **"Solved" has three formal levels** (§1): *ultra-weak* (the value of
   the initial position), *weak* (value + a strategy from the initial
   position), *strong* (every position valued + optimal play everywhere).
   Checkers: **weakly solved** — a draw (Schaeffer et al., *Science*,
   2007). Chess: **not even ultra-weak** — the popular "draw" is a
   belief, not a theorem.
2. **This program owns four STRONG solutions** — of three-piece
   subspaces. KRK, KQK, KNK, KPK: every legal state valued, the optimal
   move recoverable everywhere, Bellman verified over all 1,528,356
   states (E5, §3). The weak level is delivered too: explicit minimal
   strategy trees from canonical starts, the largest 6,558 nodes —
   0.02–2% of the respective space.
3. **The methodology is exactly Chinook's** — retrograde endgame
   databases plus proof search — exercised at the scale where it is
   exact and every claim is frozen.
4. **The wall to 32 pieces is measured, not conjectured** (§4): the E2
   ladder, the E3 certificate explosion, and the E5 storage/time
   extrapolation — a full-chess table at a generous 1 byte/state needs
   ~4.8·10⁴⁴ bytes ≈ **3.2·10²¹ × the world's digital storage**, or
   ~1.5·10²⁸ years at 10⁹ states/s ≈ **10¹⁸ × the age of the universe**.
5. Therefore "solve chess like checkers" is **not an engineering
   scale-up** of anything known today; it awaits a mathematics that does
   not yet exist (§5) — for example, a general draw invariant for
   32-piece play.

## 1. The three levels, formalized

For a two-player zero-sum game with perfect information and no chance
(the chess frame; draw is a possible outcome), define:

- **Ultra-weak solution**: the game-theoretic value of the *initial
  position* is known — White wins, Black wins, or draw.
- **Weak solution**: the value of the initial position **and** a
  strategy for the side(s) that can achieve it.
- **Strong solution**: for **every** legal position, its value is known
  and an optimal move is available in each.

Checkers (English draughts) is **weakly** solved: Schaeffer et al.
announced in 2007 that with perfect play by both sides the game is a
draw — neither side can force a win. Crucially, that is *not* a claim
that a human always draws; it is the statement that a perfect opponent
cannot be beaten. Other draughts families (Russian, international) are
different games and are not covered. Chess sits below even the
ultra-weak rung: all three outcomes are still formally live hypotheses.

## 2. What Chinook actually did — and what this program repeats

Chinook's proof is **retrograde endgame databases + forward proof-tree
search**: databases for every position with at most eight pieces (with
selective 9- and 10-piece blocks along the proof tree — the 10-piece
block alone ≈ 3.9·10¹³ positions), then a prover that only needed to
resolve positions *above* the database horizon. Eighteen years of
computation (1989–2007) over a state space of ≈ 5·10²⁰.

That is precisely the architecture of this laboratory, at the scale
where exhaustiveness is affordable:

| Chinook ingredient | This program |
|---|---|
| retrograde endgame databases | `results/dtm_{krk,kqk,knk,kpk}.json.gz` — 4 frozen bases, 1,528,356 states, Bellman 0 violations |
| proof search above the DB horizon | E5 weak level: minimal DTM-greedy strategy trees from canonical starts |
| the final verdict ("draw") | KNK: the universal draw **proved by exhaustion** (T15: 0 won states in 429,440; a knight mate does not exist) |
| doctrine cross-checks | KPK anchors: c8=Q# mate-in-1, both stalemate traps, the frontal-opposition draw d6/e6/d8 **wtm** and its lost-opposition twin **btm** (win in 18 plies), the shoulder line a3/g2/a5 (deepest win, 28 moves), the undefended-pawn resource |

**E5 — the solution-level ladder** (`scripts/solve_levels_e5.py`,
frozen into `results/solve_levels_e5.json`) establishes which level each
space sits at:

- **Strong** (100% coverage, live-cross-asserted against the table
  headers): KRK 399,112 states (376,868 won / 22,244 drawn); KQK 368,452
  (345,404 / 23,048); KNK 429,440 (0 / 429,440 — every state drawn);
  KPK 331,352 (222,558 / 108,794). An interesting asymmetry, frozen by
  E4/T16 earlier and visible here again: in KRK and KQK the strong side
  has **no drawn states at all when it is to move** (175,168/175,168
  and 144,508/144,508 won).
- **Ultra-weak**: 11 doctrine anchors probed live and asserted
  (§2 table); KNK collapses all three levels into one — a universal
  draw.
- **Weak**: full optimal principal variations (greedy attacker vs
  maximally resistant defender, length = DTM exactly, ending in mate)
  and the *minimal winning-strategy tree* — the explicit object that
  proves the win against every defence:

  | start | DTM | PV plies | tree nodes | mate leaves | share of space |
  |---|---|---|---|---|---|
  | KRK c2/b4/c8 w (the oracle box) | 19 | 19 | 2,496 | 446 | 0.63% |
  | KQK a1/h1/e8 w (long side) | 13 | 13 | 132 | 27 | 0.036% |
  | KPK e6/e5/e8 w (king in front) | 21 | 21 | 6,558 | 1,085 | 1.98% |

  The KPK tree and line cross the promotion boundary into the KQK space
  exactly as the build does. The hardest KRK position (a8/c2/d3 w, DTM
  31 plies) is recomputed **independently of E3** and reproduces the
  frozen certificate: **500,900 = 500,900** — two implementations, one
  number. Even the deepest wins have tiny explicit certificates from a
  fixed start: a weak solution of a subspace is *cheap*; it is the
  *whole space* where certificates explode (E3).

- **Deepest states** (exact argmax per space and side): KRK 31 plies
  WTM (×916 positions) / 32 plies BTM (×3,056); KQK 19/20; KPK 55/56 —
  the shoulder-line family a3/g2/a5 holds just **4** BTM positions at
  the 56-ply maximum.

## 3. Why chess resists: the measured wall

Three independent measurements, one conclusion.

**Positions and tree.** Chess has ≥ 4.5·10⁴⁴ legal positions (Tromp's
2021 lower bound; estimate ≈ 4.8·10⁴⁴) and a game-tree complexity
≈ 10¹²⁰ (Shannon 1950). The rule set that must be honored to the letter
for a *proof* (not an approximation): castling rights, en passant,
promotion choice, threefold repetition, the fifty-move rule (which caps
the longest game at ≈ 8,848.5 moves ≈ 17,697 plies). Checkers, by
comparison: ≈ 5·10²⁰ positions — a factor of
**9.6·10²³ fewer** states than chess.

**The E2 n-ladder (exact).** KRK on n×n grows n²(n²−1)(n²−2)-like:
3,496 states at n = 4 → 399,112 at n = 8 — polynomial in the *board*,
bit-exact against the frozen table at n = 8. The exponential wall is
the *piece count* k, not the board.

**The E3 certificate explosion (exact).** Even where the DTM *table*
is affordable, the *explicit* minimal winning-strategy certificate
grows exponentially in n (base ≈ 8 for KRK): at n = 8 the hardest
KRK certificate (500,900 nodes) already exceeds the entire 399,112-state
table. Polynomial / exact / explicit — pick two (the trilemma of N1).

**The E5 storage/time extrapolation (exact big-int).** At a generous
1 byte/state — the frozen tables actually need 0.28 B/state after
packing and gzip — a full-chess table is:

| quantity | value |
|---|---|
| full-chess table, 1 B/state | 4.82·10⁴⁴ B = 4.82·10³² TB |
| world digital storage (2025, ≈ 150 ZB) | × **3.21·10²¹** over |
| at 10⁹ states/s | 1.53·10²⁸ years = × **1.11·10¹⁸** the age of the universe |
| 7-man tablebases (Syzygy), for scale | ≈ 18.4 TB; 6-man ≈ 150 GB; 5-man ≈ 1 GB; 8-man ≈ 2 PB (estimates) |

And storage is the *cheap* part: it buys values, not strategies; the
strategy objects grow like E3's certificates say they do.

## 4. What does NOT count as a solution

- **Stockfish / AlphaZero beating everyone** — measured playing
  strength, not a proof over the game tree; no value, no strategy
  certificate.
- **7-man (and even future 8-man) tablebases** — strong solutions of
  *subspaces with few pieces*, exactly like this program's four bases;
  they leave the 25+ piece ocean untouched.
- **A world-champion match won by a machine** — an empirical event,
  not a theorem.
- **"Everybody knows it's a draw"** — the consensus expectation for
  chess is precisely an *ultra-weak claim without a proof*; before 2007
  the same was true of checkers, and the proof settled it only there.

## 5. What would count — and what this program honestly contributes

Solving chess would require one of:

1. **A weak/strong proof by exhaustion** — 4.8·10⁴⁴ states through
   retrograde analysis + a proof tree from the initial position. The E5
   numbers above show this is off every conceivable hardware curve; no
   algorithmic constant fixes a 10²¹ storage overrun.
2. **A general mathematical invariant** — e.g., a *draw certificate*
   for the initial position that does not enumerate the space: a compact
   object plus a proof that every White plan is met by a Black resource
   (the way T15 proves KNK: "no knight mate exists" is exactly such an
   invariant, at subspace scale). For 32 pieces, no such invariant is
   known; inventing one is an open problem of mathematics, not of
   engineering.
3. Nothing in between is visible: T13 already forbids the lazy route
   (generalized chess is EXPTIME-complete and P ⊊ EXPTIME is a theorem),
   and E3 shows explicit certificates are the wrong currency at scale.

**What this program contributes** is the only honest currency a
chess-based program has: a fully certified microcosm in which all three
solution levels are *simultaneously attained and separated* (KNK: all
three collapse into a proved draw; KRK/KQK/KPK: strong tables + weak
trees + ultra-weak doctrine anchors), the Chinook methodology exercised
end-to-end at exact scale, and the wall to the full game measured —
ladder by ladder, certificate by certificate, byte by byte — instead of
asserted.

## 6. Reproduction

```bash
python3 scripts/solve_levels_e5.py          # E5 (~1 min): the ladder
python3 complexity/experiment_certificates.py --max-n 8 --plot   # E3
python3 complexity/experiment_scaling.py --max-n 8               # E2
python3 scripts/vortex_e4.py 150                                 # E4
python3 -m pytest tests/ -q                                      # battery
```

E5 reads only the frozen `results/dtm_*.json.gz`, the frozen
`results/trap_census.json` / `complexity_scaling.json`, and asserts
every doctrine anchor, every census cross-total, and the E3 certificate
(500,900 nodes) live.

## 7. References

- J. Schaeffer, N. Burch, Y. Björnsson et al. *Checkers is solved.*
  Science 317 (2007) 1518–1522 — the weak solution: perfect play draws.
- M. L. Allis. *Searching for solutions in games and artificial
  intelligence.* PhD thesis, Rijksuniversiteit Limburg (1994) — the
  ultra-weak / weak / strong solution taxonomy.
- C. E. Shannon. *Programming a computer for playing chess.* Philos.
  Mag. 41 (1950) — the 10¹²⁰ game-tree estimate.
- J. Tromp. *Chess positions.* (2021) — ≥ 4.5·10⁴⁴ legal positions; the
  8,848.5-move bound under the fifty-move rule.
- A. S. Fraenkel, D. Lichtenstein. *Computing a perfect strategy for
  n×n chess requires time exponential in n.* J. Combin. Theory A 31
  (1981) — T13's EXPTIME-completeness.
- This program: E1–E5; T13–T17; frozen tables
  `results/dtm_{krk,kqk,knk,kpk}.json.gz`;
  `results/solve_levels_e5.json`; note N1 (`P_VS_NP.md`).
