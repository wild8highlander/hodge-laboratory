# complexity/ — the EXPTIME Barrier Laboratory

This module answers a big question with precise tools:

> *Generalized chess on an n×n board is EXPTIME-complete. If someone found
> a polynomial algorithm for it, that would mean P = EXPTIME and a collapse
> of complexity classes.*

**The answer.** That scenario is not unlikely — it is **logically
impossible**: `P ⊊ EXPTIME` is a *theorem* (deterministic time hierarchy,
Hartmanis–Stearns 1965), and generalized chess is EXPTIME-complete
(Fraenkel–Lichtenstein 1981). What IS possible — and what this module
builds, measures and freezes — is:

1. **T14(ii) — polynomial islands.** For a *fixed* number of pieces `k`
   the state space is `O(n^{2k})` — polynomial in `n`. The generalized
   retrograde analyzer here reproduces the frozen 8×8 KRK table
   **bit-exactly** (0 mismatches over 2^22 indices) and scales n = 4..8
   (3,496 → 399,112 states, max DTM 7 → 16 moves).
2. **T14(i) — polynomial myopia.** The three-layer `ParticleSolver`
   (threat-field pressure + Lagrangian energy, lexicographic tie-break)
   picks a move in `O(n^4 k^2)` — measured 0.54–0.66 ms per move on
   n = 4..8. It **never looks at any DTM table**.
3. **T14(iii) — the tunnel argument.** Families of position pairs exist
   where the win-preserving move differs only in a configuration
   `2^Θ(m)` plies deep; no polynomial-horizon solver can distinguish
   them. The measured consequence on ordinary 8×8 KRK: the greedy
   particle move **loses the win in 17.56% of won positions** (KQK:
   4.38%), paying on average +2.95 plies against the optimum, being
   optimal in only ~30% of positions.

The full argument, with proofs and the experiment protocol, is the
research paper **“The Particle Limit”**
(`monograph/pdf/{ru,en}/particle_limit.pdf`, DOCX alongside).

## Files

| File | Purpose |
|------|---------|
| `generalized_chess.py` | `ParticleSolver` (polynomial move chooser), generalized n×n retrograde DTM (KRK/KQK), state↔Position bridges, selftest, demo |
| `experiment_particles_vs_oracle.py` | **E1**: greedy particle moves vs exact DTM oracle on samples of won WTM positions |
| `experiment_scaling.py` | **E2**: retrograde/particle/alpha-beta scaling across board sizes n = 4..8 + bit-exact n=8 validation |
| `experiment_certificates.py` | **E3**: exact big-int minimal winning-strategy tree sizes (certificate explosion), n = 4..8, KRK/KQK |
| `P_VS_NP.md` | Note N1: can this program settle P vs NP? — the honest answer (criterion formalization, untouchability argument, three barriers, the certification trilemma) |
| `SOLVING_CHESS.md` | Note N2: can chess be solved like checkers? — the honest answer (the ultra-weak/weak/strong taxonomy, Chinook 2007, E5's solution-level ladder, the measured wall, what would count) |
| `make_plots.py` | 600 dpi figures (English labels) into `reports/plots/complexity/` |

## Commands

```bash
python3 complexity/generalized_chess.py --selftest       # sanity suite
python3 complexity/generalized_chess.py --demo           # one oracle-checked game
python3 complexity/experiment_particles_vs_oracle.py --sample 5000   # E1 (~1 min)
python3 complexity/experiment_scaling.py --max-n 8       # E2 (~1 min)
python3 complexity/experiment_certificates.py --max-n 8 --plot   # E3 (~1 min)
python3 scripts/solve_levels_e5.py                               # E5 (~1 min)
python3 complexity/make_plots.py                         # figures
```

## Frozen results (see `results/`)

* `complexity_particles_vs_oracle.json` — E1: KRK save-rate 0.82440,
  KQK save-rate 0.95620; optimal-rate 0.3030 / 0.2648; mean ΔDTM
  +2.9452 / +2.3301 plies; depth tables; example lost positions.
* `complexity_scaling.json` — E2: states follow n²(n²−1)(n²−2);
  n=8 verification **0 mismatches PASS**.
* `complexity_certificates.json` — E3: minimal winning-strategy trees grow
  exponentially in n (log₁₀‖T‖ ≈ 0.91·n for KRK, ≈ 0.60·n for KQK) while the
  DTM table is O(n⁶); at n = 8 the smallest exact explicit KRK certificate
  (500,900 nodes, hardest position DTM 31 plies) already exceeds the whole
  table (399,112 states). Polynomial / exact / explicit — pick two.
* `solve_levels_e5.json` — E5 (note N2): the solution-level ladder. Strong:
  100% coverage per space (1,528,356 states total). Ultra-weak: 11 classical
  doctrine anchors asserted live (c8=Q#, both stalemate traps, the opposition
  draw and its lost twin — win in 18, the shoulder line — 28 moves). Weak:
  explicit minimal strategy trees from canonical starts (KRK 2,496 nodes /
  KQK 132 / KPK 6,558 — 0.04–2% of the space) with the E3 argmax certificate
  reproduced independently: 500,900 = 500,900. The wall: a full-chess table
  ≈ 3.21·10²¹ × world storage, ≈ 10¹⁸ × the age of the universe.

All numbers are reproducible from a clean checkout; the experiments use
the frozen `results/dtm_krk.json.gz` / `dtm_kqk.json.gz` tables as the
oracle and nothing else.

## Two bug classes the bit-exact check caught (lesson)

1. **Phantom pieces**: reusing a `board` array across state triples leaves
   stale pieces from the previous triple — they block lines and change
   attack sets. Fix: a fresh board per triple.
2. **Moving-king legality**: when testing whether the black king's move
   is legal, the *old* king square must be vacated first, or the phantom
   king blocks the rook line and illegal moves become legal.

Both were caught by the `n = 8 vs frozen table: 0 mismatches` gate —
an example of the project doctrine: freeze a certificate, then make any
new code prove itself against it.

## The browser side of the barrier (web link)

The generalized-board half of this module is live in `web/chess-particles/`:
a board-size selector (8×8, 6×6, 5×5, 4×4) loads KRK demo presets verified
won by `retro_dtm_nxn` (4×4: 9 plies, 5×5: 13, 6×6: 17), and a complexity
card re-enumerates the exact KRK state space of every n in the browser
(`krkSpace(n)`, the same enumeration semantics as `experiment_scaling.py`)
against the frozen E2 rows — states and edges match digit-for-digit,
including the degenerate 0x88 king-move tail for n < 8. The exponential
wall stays in the piece count k: on the web the board grows, the O(n⁶)
polynomial is visible, and T14 can be watched, not just cited.
