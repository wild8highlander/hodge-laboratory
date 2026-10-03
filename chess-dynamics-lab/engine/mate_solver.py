#!/usr/bin/env python3
"""engine/mate_solver.py — the particle-driven mate-in-N solver (CLI).

    python3 engine/mate_solver.py --fen "FEN" --depth 5
    python3 engine/mate_solver.py --suite          # frozen problem suite
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402


def solve(fen, depth=5):
    """Solve a mate-in-N problem; returns a JSON-ready dict."""
    pos = D.Position().set_fen(fen)
    valid, why = pos.is_valid()
    if not valid:
        return {'fen': fen, 'error': 'illegal position: %s' % why}
    plies, pv, nodes = D.mate_search(pos, depth)
    return {
        'fen': fen,
        'mate_plies': plies,
        'mate_in_moves': None if plies is None else (plies + 1) // 2,
        'pv_uci': [D.move_to_uci(m) for m in pv],
        'nodes': nodes,
    }


def suite():
    out = []
    for label, fen, plies in (
            ('morphy_m2', D.MATE_MORPHY_FEN, D.MATE_MORPHY_PLIES),
            ('ladder_m2', D.MATE_LADDER_FEN, D.MATE_LADDER_PLIES),
            ('nr_m1', D.MATE_NR_FEN, D.MATE_NR_PLIES)):
        r = solve(fen, depth=max(4, plies + 1))
        r['label'] = label
        r['expected_plies'] = plies
        r['ok'] = r['mate_plies'] == plies
        out.append(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='Mate-in-N particle solver')
    ap.add_argument('--fen', help='position (side to move delivers mate)')
    ap.add_argument('--depth', type=int, default=5)
    ap.add_argument('--suite', action='store_true')
    args = ap.parse_args(argv)
    if args.suite:
        print(json.dumps(suite(), indent=1))
    elif args.fen:
        print(json.dumps(solve(args.fen, args.depth), indent=1))
    else:
        ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
