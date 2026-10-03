#!/usr/bin/env python3
"""engine/game_player.py — alpha-beta game player with particle ordering.

    python3 engine/game_player.py --depth 3 --moves "e2e4 e7e5"
    python3 engine/game_player.py --selfplay --depth 3 --plies 12
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402


def best_move(fen=None, depth=3, moves=''):
    """Returns the UCI string of the best move (or None if game over)."""
    pos = D.Position().set_fen(fen) if fen else D.start_position()
    for u in (moves or '').split():
        pos.make(D.uci_to_move(pos, u))
    m, score, nodes = D.search_best_move(pos, depth)
    return D.move_to_uci(m) if m else None


def selfplay(depth=3, plies=20, fen=None):
    """Play a short deterministic game against itself."""
    pos = D.Position().set_fen(fen) if fen else D.start_position()
    game = [pos.to_fen()]
    for _ in range(plies):
        moves = pos.legal_moves()
        if not moves:
            break
        m, score, _ = D.search_best_move(pos, depth)
        pos.make(m)
        game.append(D.move_to_uci(m))
    game.append(pos.to_fen())
    return game


def main(argv=None):
    ap = argparse.ArgumentParser(description='Alpha-beta particle player')
    ap.add_argument('--fen', default=None)
    ap.add_argument('--depth', type=int, default=3)
    ap.add_argument('--moves', default='')
    ap.add_argument('--selfplay', action='store_true')
    ap.add_argument('--plies', type=int, default=20)
    args = ap.parse_args(argv)
    if args.selfplay:
        print(json.dumps(selfplay(args.depth, args.plies, args.fen),
                         indent=1))
    else:
        pos = D.Position().set_fen(args.fen) if args.fen else D.start_position()
        for u in args.moves.split():
            pos.make(D.uci_to_move(pos, u))
        m, score, nodes = D.search_best_move(pos, args.depth)
        print(json.dumps({
            'fen': pos.to_fen(),
            'best': D.move_to_uci(m) if m else None,
            'score_cp': score, 'depth': args.depth, 'nodes': nodes,
        }, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
