# web/ — the browser laboratories

## chess-particles — the particle laboratory

`chess-particles/index.html` — a single-page, build-free application (pure HTML/CSS/JS)
in the visual language of the hodge-flow-chess laboratory: dark navy `#0A1120`, gold
`#C9A96A`, violet `#9D7BD8`, teal `#3FC9AD`; Playfair Display / Inter / JetBrains Mono;
aurora blobs; sidebar navigation on the desktop, bottom tabs on mobile.

### Sections

1. **Live flow** — a canvas board (8×8 by default, **n×n generalized boards
   6×6 / 5×5 / 4×4** from the complexity module) where pieces are glowing
   particles (gold = White, violet = Black):
   - a real 0x88 chess engine **running in the browser**: full legal generation
     (castling, en passant, promotion, pins, checks, mate/stalemate);
   - *auto flow*: the engine plays a seeded deterministic game at an adjustable speed;
     each move animates as a flying particle with a trail;
   - the threat-field heatmap toggle: Θ(c) over all squares, gold → teal scale;
   - the **Θ-flow animation**: an animated field mode in which one glowing quantum
     streams along every attacker→target incidence (gold — White attackers,
     cyan — Black), with a golden-ratio phase stagger and a smooth crossfade of
     the whole field between positions; honours `prefers-reduced-motion`;
   - the Lagrangian panel: material and mobility bars, E = [M(w)−M(b)] + μ[m(w)−m(b)]
     with μ = 0.1, updating every ply;
   - manual play: click a particle, click a highlighted square;
   - the t\* billiard card: the damped particle on the board geometry with
     γ = π⁴/256, the formula t\* = lcm(W/gcd(a,W), H/gcd(b,H)) and the path ratio;
     the geometry and the ±(n−1) velocity cap follow the selected board size;
   - **the board-size selector (T14)**: generalized n×n boards loading a KRK
     demo preset verified WON by the exact retrograde oracle
     (`scripts/verify_nxn_presets.py`: 4×4 in 9 plies, 5×5 in 13, 6×6 in 17);
     castling stays an 8×8 privilege, pawn promotion/double-push ranks adapt;
   - **the complexity card**: the exact K+R vs K state space of the selected
     board, re-enumerated live in the browser (`krkSpace(n)`) against the
     frozen E2 rows (`results/complexity_scaling.json`) — states and edges
     match digit-for-digit for every n (including the degenerate 0x88 edge
     tail for n < 8), with the O(n⁶) scaling note: the exponential wall of
     generalized chess lives in the piece count, not the board size.
2. **Theory** — the twelve theorem cards T01–T12 with the frozen constants and the
   key formulas in JetBrains Mono.
3. **Protocol C** — the battery C1–C10 **genuinely computed in the browser** over the
   page's own engine; every row prints the expected value, the computed value, the
   honest [PASS]/[FAIL] badge and the runtime; the summary line `verdict: N/10`.
   Nothing is hardcoded: C5 recomputes perft 20/400/8902 in your tab (the deep button
   adds perft(4) = 197281), C8 solves the Morphy mate by DFS, C9 verifies splitmix64
   in BigInt including the inverse round-trip over 1..2000, C10 runs the Warnsdorff
   tour and verifies the closure d6→f5.
4. **About** — the program, the author, the license, the links.

Full RU/EN interface (the language pill, `localStorage`, `<html lang>` updates).

### Honest-verification note

The FAIL state is reachable and displayed honestly: the checks are implementations,
not strings. The CI (`.github/workflows/ci.yml`, job `web`) runs the same core from
Node and asserts `verdict: 10/10` — if the browser engine ever regresses, CI fails.

### Files

```text
web/chess-particles/
├── index.html            the markup: 4 sections, 72 i18n keys
├── assets/css/style.css  the design system (hodge-flow-chess base + app layer)
└── assets/js/app.js      the engine, the particles, the protocol, i18n (~2000 lines)
```

## chess-oracle — play against perfection

`chess-oracle/index.html` — the advanced endgame laboratory built on the frozen
DTM tables (`results/dtm_*.json.gz`, embedded as `assets/data/tables.js`):

- **perfect play**: the oracle moves are DTM-optimal by construction
  (argmin/argmax over the table); you may defend with Black, attack with
  White, watch perfect-vs-perfect autoplay, or face the three-layer
  ParticleSolver instead of the oracle;
- **four endgames**: KRK and KQK (the classical certificates), **KNK** —
  the negative control whose integrity gate re-proves on every load that
  a knight mate does not exist (won = mates = 0 over 429,440 states) —
  and **KPK**, whose promotion moves inherit exact DTM values from the
  frozen KQK certificate; a promotion on the board honestly switches the
  app into the KQK space (Undo restores KPK);
- **live Bellman audit**: every visited position is re-verified in the
  browser by an independent move generator (mate ⇔ no moves + check;
  won d ⇔ a child at d−1 and none faster; lost d ⇔ all children won,
  max d−1, no capture escape; drawn ⇔ no winning child / stalemate /
  capture) — the frozen proof becomes a running process, one FAIL turns
  the banner red;
- **integrity gate on load**: stats + blob re-count + bellman flag against
  the frozen certificate (399,112 / 4,447,032 / 216 / 32 for KRK);
- **strategy-tree explorer**: the exact minimal explicit certificate T(w)
  (E3) with per-level growth, next to the O(n⁶) table size — the
  trilemma made tangible;
- **in-browser E1 replay**: the greedy particle solver re-measured against
  the oracle (frozen reference: save-rate 0.8244 / 0.9562; KPK — live
  measurement; KNK — E1 undefined by a theorem, and the panel says so);
- **position editor**: any legal KRK/KQK/KNK/KPK setup, probed against the
  matching table (the endgame follows the placed piece);
- **vortex dynamics (T16)**: the **вихрь** toggle re-encodes the certificate
  as a planar flow — vortices at the pieces, descent currents into the
  mating squares — and classifies the outcome **from the flow only**:
  a converging spiral = 100% win, closed orbits = draw (KNK is nothing
  but closed orbits), every defence swept into the net = loss; constants
  frozen by E4 (1800/1800 agreement, capture separation 1.000/0.000);
- RU/EN i18n, mobile-friendly, works offline from `file://` (Termux).

Details: `chess-oracle/README.md`. Node harness for the JS core:
`node web/chess-oracle/tests/node_harness.js` (verdict: ALL CHECKS PASSED).

## Running locally

Open `index.html` in any modern browser — no server, no build step. Or:

```bash
cd web/chess-particles && python3 -m http.server 8000
# http://localhost:8000
```

The pure core is testable from Node (no DOM needed):

```bash
node -e "global.window={localStorage:{getItem:()=>null,setItem:()=>{}}};
require('./assets/js/app.js');
const CDL=global.window.CDL; console.log(CDL.runProtocol(false).map(r=>r.code+':'+r.pass).join(' '));"
```

© 2026 Isaev Iskhak Khamzatovich. All rights reserved. See [../LICENSE](../LICENSE).
