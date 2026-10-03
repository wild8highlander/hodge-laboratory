# data/games/ — the E12 real-game corpus

The frozen corpus behind the E12 certificate (`results/outcome_realgames_e12.json`):
real games flowing through the Epoch IV player-context layer. Three sources
with an explicit honesty contract:

| File | Source | Games | What it is |
|---|---|---|---|
| `reti_tartakower_1910.pgn` | human-classical | 1 | Réti – Tartakower, Vienna 1910 (public domain) |
| `morphy_brunswick_1858.pgn` | human-classical | 1 | Morphy – Duke of Brunswick & Count Isouard, Paris 1858 ("the Opera Game", public domain) |
| `anderssen_kieseritzky_1851.pgn` | human-classical | 1 | Anderssen – Kieseritzky, London 1851 ("the Immortal Game", public domain) |
| `engine_selfplay.pgn` | engine | 2 | deterministic alpha-beta self-play (`engine/game_player.py`) |
| `walks_kpk.pgn` / `walks_krk.pgn` / `walks_kqk.pgn` | tablebase-walk | 24 | seeded optimal-play lines through the frozen domains (Epoch V machinery), terminal result known from the certificates |

## The honesty contract

* **human-classical** games carry **no Elo headers** — the context prior
  must be a strict no-op on them; the audit verifies that instead of
  trusting the promise. They never enter a frozen domain (both sides
  keep heavy material), which is exactly why they exercise the parser
  end-to-end.
* **tablebase-walk** games start from a frozen-domain FEN (`SetUp "1"`,
  `FEN "..."`) and carry **SIMULATED** Elo headers with the documented
  `EloAlignment` knob: `aligned` (the higher rating sits with the
  winning side) or `independent` (assigned at random). No real player
  data is used or implied.
* The Result header of a walk equals the exact certificate outcome of
  the line; the audit flags any game whose board contradicts its
  result instead of silently fixing it.

## Regeneration

```bash
python3 scripts/build_game_corpus.py          # re-freezes walks + engine games (seed 2026)
python3 -m outcome games data/games           # the E12 audit
```

The three classical scores are frozen files: they are verified by full
legal replay in the test suite (`tests/test_outcome_pgn.py`).
