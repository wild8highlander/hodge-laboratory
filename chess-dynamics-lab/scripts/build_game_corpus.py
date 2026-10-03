#!/usr/bin/env python3
"""scripts/build_game_corpus.py — freeze the E12 real-game corpus.

Generates the laboratory-side games of ``data/games/`` (the classical
human scores live there as frozen public-domain files):

* tablebase walks — seeded DTM-optimal / best-defence / random walks
  through the frozen domains (Epoch V machinery), written as PGN with
  the root FEN header and the TRUE terminal result;
* engine self-play — deterministic alpha-beta games from the starting
  position.

Walk games carry SIMULATED Elo headers with a documented alignment knob
(EloAlignment header):

    aligned      the higher rating sits with the side that actually
                 wins (draws: equal ratings);
    independent  the rating advantage is assigned to a random side, so
                 the prior contradicts the theory half of the time.

Both classes are needed: the first measures the best case of the Epoch
IV prior, the second its honest cost when ratings know nothing about
the position.  Everything is bit-reproducible (fixed seeds).

    python3 scripts/build_game_corpus.py [--out data/games]
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import pgn as PGN                              # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402
from outcome import trajectory as TR                        # noqa: E402

WALK_PLAN = (('kpk', 12), ('krk', 6), ('kqk', 6))
ENGINE_GAMES = 2
ENGINE_DEPTH = 3
ENGINE_PLIES = 30
RESULT_TEXT = {T.WHITE_WIN: '1-0', T.DRAW: '1/2-1/2', T.BLACK_WIN: '0-1'}


def walk_headers(root_fen, result, elo, alignment):
    return {
        'Event': 'Tablebase walk (laboratory)',
        'Site': 'chess-dynamics-lab',
        'Date': '2026.10.01',
        'White': 'Walk-White', 'Black': 'Walk-Black',
        'Result': result,
        'WhiteElo': str(elo[0]), 'BlackElo': str(elo[1]),
        'TimeControl': '600+0',
        'SetUp': '1', 'FEN': root_fen,
        'Source': 'tablebase-walk', 'EloAlignment': alignment,
    }


def build_walks(seed):
    games = []
    for ki, (kind, n) in enumerate(WALK_PLAN):
        lines = TR.sample_lines([kind], n, seed=seed,
                                horizon=TR.DEFAULT_HORIZON)
        for i, line in enumerate(lines):
            fens = [s['fen'] for s in line['steps']]
            sans = PGN.moves_between(fens)
            result = RESULT_TEXT[line['final_cls']]
            alignment = 'aligned' if (len(games) % 2 == 0) \
                else 'independent'
            rng = random.Random(line['game_id'] ^ 0x5EED)
            if alignment == 'aligned':
                elo = {T.WHITE_WIN: (1650, 1400),
                       T.BLACK_WIN: (1400, 1650),
                       T.DRAW: (1500, 1500)}[line['final_cls']]
            else:
                elo = (1650, 1400) if rng.randrange(2) else (1400, 1650)
            games.append(PGN.Game(walk_headers(fens[0], result, elo,
                                               alignment),
                                  fens[0], sans))
    return games


def build_engine_games():
    """Deterministic alpha-beta self-play from the starting position."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'game_player', os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'engine', 'game_player.py'))
    gp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gp)
    games = []
    for gi in range(ENGINE_GAMES):
        pos = D.start_position()
        sans = []
        for _ in range(ENGINE_PLIES):
            if not pos.legal_moves():
                break
            m, _score, _nodes = D.search_best_move(pos, ENGINE_DEPTH)
            sans.append(PGN.san_of_move(pos, m))
            pos.make(m)
        headers = {
            'Event': 'Engine self-play (laboratory)',
            'Site': 'chess-dynamics-lab',
            'Date': '2026.10.01',
            'White': 'AlphaBeta-W', 'Black': 'AlphaBeta-B',
            'Result': '*',
            'TimeControl': '-',
            'Source': 'engine',
        }
        games.append(PGN.Game(headers, D.START_FEN, sans))
    return games


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/games')
    ap.add_argument('--seed', type=int, default=2026)
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    walks = build_walks(args.seed)
    engines = build_engine_games()

    by_kind = {}
    for g in walks:
        by_kind.setdefault(g.headers['FEN'] and _root_kind(g), []).append(g)
    written = []
    for kind, gs in sorted(by_kind.items()):
        path = os.path.join(args.out, 'walks_%s.pgn' % kind)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(PGN.write_pgn(gs))
        written.append((path, len(gs)))
    path = os.path.join(args.out, 'engine_selfplay.pgn')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(PGN.write_pgn(engines))
    written.append((path, len(engines)))
    for path, n in written:
        print('frozen %-44s %d games' % (path, n))
    return 0


def _root_kind(game):
    """Walk file grouping key: the root position's frozen domain."""
    from outcome import tablebase_api as T2
    pos = D.Position().set_fen(game.start_fen)
    return T2.detect_domain(pos) or 'kk'


if __name__ == '__main__':
    raise SystemExit(main())
