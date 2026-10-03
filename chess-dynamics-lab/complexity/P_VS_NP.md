# Can This Program Settle P vs NP? — An Honest Answer

chess-dynamics-lab · complexity note N1 · author: Isaev Iskhak Khamzatovich

> **The question.** "Can all of this prove **or refute** P = NP — or the
> polynomial-algorithm scenario for generalized chess? Even a refutation
> would be enough. After all, P = NP would be proved only by an exact
> polynomial algorithm for an NP-complete problem, or by an approximation
> sufficient for an exact solution."

## 0. The verdict in four lines

1. **The chess-specific scenario is REFUTED — rigorously, unconditionally.**
   A polynomial-time exact algorithm for generalized chess does not exist,
   for *any* algorithm, particle-based or otherwise: generalized chess is
   EXPTIME-complete (Fraenkel–Lichtenstein 1981) and `P ⊊ EXPTIME` is a
   *theorem* (deterministic time hierarchy, Hartmanis–Stearns 1965). This is
   theorem **T13** of the companion paper *The Particle Limit*
   (`monograph/pdf/{ru,en}/particle_limit.pdf`).
2. **P vs NP itself is out of reach of chess in BOTH directions** — and this
   is not a confession of weakness but a structural fact (§2). No chess
   experiment, however large, can prove or refute P = NP.
3. What the program *can* and *does* do is **measure the exact shape of the
   wall**: polynomial islands (E2), the measurable price of polynomiality
   (E1), and the certificate explosion (E3, this note).
4. The user's criterion is **correct and is adopted here as a proposition**
   (§1), with one clarification about the word "approximation" (§4).

## 1. The criterion, formalized

**Proposition (P = NP certificate criterion).** The following are
equivalent:

- `P = NP`;
- there is a polynomial-time algorithm deciding SAT (or CLIQUE, or 3-COLOR,
  or any other NP-complete language) exactly — zero error on every input;
- there is a polynomial-time procedure that, for every satisfiable CNF
  formula, *outputs* a satisfying assignment (a self-contained witness),
  together with a **proof of correctness** of that procedure.

The equivalence of the first two bullets is the definition of NP-completeness
(SAT is NP-hard, and SAT ∈ P iff P = NP). The third bullet is the
constructive form: if P = NP, Levin's universal search makes such a solver
effective (with a brutal constant), and conversely a certified constructive
solver puts SAT in P.

**The "approximation sufficient for an exact solution" clause.** Such a
phrase can mean two things, and the difference is everything:

- *an approximation with a correctness proof* — i.e., a procedure that is
  provably exact on all instances. Then it **is** the second bullet: an
  exact polynomial algorithm. Nothing new is being asked.
- *an approximation that is empirically exact* — high success rate, no proof.
  Then it proves **nothing** about P vs NP, no matter how convincing the
  benchmarks. Our own ParticleSolver is the standing counterexample-in-kind:
  it is fully polynomial, it looks excellent on shallow positions — and E1
  measured exactly where the exactness ends (§5).

This disambiguation is not pedantry: the entire history of failed P = NP
attempts is a history of empirically exact-looking procedures without
correctness proofs.

## 2. Why chess cannot touch P vs NP — in either direction

Let `CHESS-WIN` = { generalized n×n chess positions from which White wins
with perfect play }. Fraenkel–Lichtenstein (1981): `CHESS-WIN` is
**EXPTIME-complete**.

**Claim (untouchability).** With current proof technology, chess cannot
settle P vs NP, because either outcome would first settle an *open*
EXPTIME question:

- If someone proved `CHESS-WIN ∈ NP`, then, NP being closed under
  polynomial-time many-one preimages, every EXPTIME language would fall in
  NP; together with the trivial `NP ⊆ EXPTIME` this gives the identity
  **NP = EXPTIME** — which would also collapse `NP ⊆ PSPACE ⊆ EXPTIME` into
  PSPACE = EXPTIME. No known theorem forbids this; it is open.
- Symmetrically, proving `CHESS-WIN ∉ NP` would prove **NP ≠ EXPTIME** —
  equally open (the same collapse argument blocks it).

So `CHESS-WIN` sits one floor above the P-vs-NP front line. Both directions
require climbing through an open identity first. This is a structural
obstruction, not a matter of effort or computing power: no finite chess
computation is evidence about P vs NP beyond anecdote, because complexity
separations are statements about *all* algorithms on *infinite* input
families.

**Contrast with the EXPTIME question — why THAT one was answerable.** For
the polynomial-algorithm scenario on generalized chess, the obstruction
vanishes, because one side is *already proven*: the deterministic time
hierarchy gives `P ⊊ EXPTIME` unconditionally. Combine:

- `CHESS-WIN` EXPTIME-complete ⇒ a polynomial exact solver would put
  EXPTIME ⊆ P;
- `P ⊊ EXPTIME` (Hartmanis–Stearns) ⇒ contradiction.

Hence **no** polynomial exact solver exists — theorem T13. This is the
refutation the question asked for, and it is unconditional: it does not
depend on whether P equals NP, on heuristics, or on any measurement. Our
three-layer particle model is covered by the same theorem a fortiori: if
someone "upgraded" the particles into an exact polynomial solver for
generalized chess, they would have contradicted a proven hierarchy theorem,
not discovered an algorithm.

## 3. Why "refute P = NP" is beyond today's mathematics altogether

Even ignoring chess, no known technique can prove `P ≠ NP`. Three formal
barriers are proven about the *proof techniques themselves*:

1. **Relativization** (Baker–Gill–Solovay 1975): there exist oracles A and B
   with `P^A = NP^A` and `P^B ≠ NP^B`. Any argument that relativizes
   (every diagonalization argument — including the time hierarchy theorems!)
   is therefore powerless to separate P from NP.
2. **Natural proofs** (Razborov–Rudich 1997): a property of Boolean
   functions that is polynomially checkable, satisfied by a random function,
   and useful for lower bounds cannot exist unless strong pseudorandom
   generators fail — i.e., a successful "natural" lower-bound argument would
   itself break cryptography.
3. **Algebrization** (Aaronson–Wigderson 2008): the algebraic generalization
   of relativization is likewise blocked for the known techniques.

To refute P = NP one needs a superpolynomial lower bound for *some* problem
in NP. For the canonical candidate, SAT, no superpolynomial lower bound is
known in the general model — not even super-linear ones are available there.
A chess engine, however instrumented, produces data; a separation requires a
proof about all machines. The gap between those categories is precisely what
the three barriers formalize.

## 4. What the program measures — the certification trilemma

The three experiments of `complexity/` give the phenomenon its exact,
frozen, reproducible shape. Define the three desirable properties of a
solving artifact: **polynomial** (runs in poly(n) time), **exact** (zero
error), **explicit** (the certificate is a self-contained object one can
check without re-deriving the whole theory).

| Artifact (experiment) | Polynomial | Exact | Explicit | Measured cost |
|---|---|---|---|---|
| DTM table, fixed 3 pieces (E2) | ✔ `O(n^6)` | ✔ | — implicit | 3,496 → 399,112 states for n = 4..8; n = 8 bit-exact vs frozen table |
| DTM table, k = Θ(n) pieces (T13/T14-iii) | ✘ | ✔ | — | `~n^{2k}` states; DTM horizon grows; EXPTIME-complete game |
| ParticleSolver (E1) | ✔ `O(n^4 k^2)`/move | ✘ | — | loses 17.56% of KRK wins, 4.38% of KQK; mean +2.95 / +2.33 plies vs optimum; optimal in ~30% |
| Minimal strategy tree (E3) | ✘ | ✔ | ✔ | exponential in n: base ≈ 8 (KRK), ≈ 4 (KQK); see table below |

**E3 — the certificate explosion (new, exact big-int measurement).** For
every won White-to-move state w of KRK/KQK on n×n we counted exactly the
*minimal* DTM-greedy winning-strategy tree

```
T(w) = 1 + min_{b : dtm[b] = dtm[w] − 1} ( 1 + Σ_{r ∈ replies(b)} T(r) )
```

(the smallest explicit object that proves the win against *every* Black
defence). Bellman consistency is asserted; the hardest line is walked and
verified to end in mate at exactly DTM plies.

| n | KRK states | KRK max DTM | KRK min ‖T‖ | KQK states | KQK max DTM | KQK min ‖T‖ |
|---|---|---|---|---|---|---|
| 4 | 3,496 | 7 | 116 | 2,996 | 4 | 14 |
| 5 | 17,528 | 10 | 1,340 | 15,464 | 6 | 52 |
| 6 | 60,800 | 12 | 10,240 | 54,720 | 7 | 216 |
| 7 | 168,260 | 14 | 75,760 | 153,640 | 8 | 1,068 |
| 8 | 399,112 | 16 | **500,900** | 368,452 | 10 | 3,626 |

Reading: `log10 ‖T‖ ≈ 0.91·n` for KRK (base ≈ 8 — the king's maximal
branching) and `≈ 0.60·n` for KQK, versus the table's polynomial `n^6`. At
the classical board the smallest exact explicit certificate (500,900 nodes
for the hardest KRK position, DTM 31 plies) already *exceeds the entire DTM
table* (399,112 states) — and for every larger n the explicit certificate
falls further behind by ~10^0.4 additional orders of magnitude per +1 of n.
Meanwhile the verification asymmetry is stark: checking *one* line of play
costs O(DTM) plies; checking the *complete* certificate costs Θ(‖T‖).

**The trilemma.** Polynomial / exact / explicit — the measured artifacts
achieve any two, never three. An artifact with all three for generalized
chess would collapse EXPTIME into P and contradict the hierarchy theorem.
The trilemma is the empirical silhouette of T13.

## 5. What would actually settle P vs NP

- **Proving P = NP** requires exhibiting the object of §1: an exact
  polynomial algorithm for an NP-complete problem **with a correctness
  proof**. No amount of empirical perfection substitutes for the proof.
- **Proving P ≠ NP** requires a superpolynomial lower bound for one NP
  problem, obtained by a technique that defeats all three barriers of §3.
  This is why the problem has resisted every attempt since 1971.
- **What chess contributes** is neither bullet — it contributes the only
  thing it honestly can: a fully certified microcosm in which the
  exactness-polynomiality tension is not discussed but *measured* (E1–E3),
  plus one unconditional impossibility theorem for the generalized game
  (T13). That is the maximal yield available to any chess-based program,
  and this program delivers it with frozen, reproducible numbers.

## 6. Reproduction

```bash
python3 complexity/experiment_certificates.py --max-n 8 --plot   # E3 (~1 min)
python3 complexity/experiment_particles_vs_oracle.py --sample 5000  # E1
python3 complexity/experiment_scaling.py --max-n 8               # E2
python3 complexity/generalized_chess.py --selftest               # sanity
```

E3 uses only the generalized retrograde analyzer (validated bit-exact
against the frozen 8×8 tables) and asserts Bellman consistency at every
step; all values are exact integers stored as strings in
`results/complexity_certificates.json`.

## 7. References

- A. S. Fraenkel, D. Lichtenstein. *Computing a perfect strategy for n×n
  chess requires time exponential in n.* J. Combin. Theory A 31 (1981).
- J. Hartmanis, R. E. Stearns. *On the computational complexity of
  algorithms.* Trans. AMS 117 (1965).
- T. Baker, J. Gill, R. Solovay. *Relativizations of the P =? NP question.*
  SIAM J. Comput. 4 (1975).
- A. A. Razborov, S. Rudich. *Natural proofs.* J. Comput. Syst. Sci. 55
  (1997).
- S. Aaronson, S. Wigderson. *Algebrization: a new barrier in complexity
  theory.* TOCT 1 (2008).
- L. A. Levin. *Universal search problems.* Probl. Pered. Inf. 9 (1973).
- This program: T13/T14 in *The Particle Limit*; experiments E1–E3;
  frozen tables `results/dtm_krk.json.gz`, `results/dtm_kqk.json.gz`.
