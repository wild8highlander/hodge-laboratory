#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  COMPLEXITY LABORATORY · experiment_certificates.py
  Experiment E3: CERTIFICATE EXPLOSION — the exact price of an exact answer.

  chess-dynamics-lab · author: Isaev Iskhak Khamzatovich · exclusive license

  QUESTION (the P vs NP criterion). "P = NP would be proved only by an exact
  polynomial algorithm for an NP-complete problem — or by an approximation
  sufficient for an exact solution." Can THIS program (particles + tables)
  produce such an object, at least for chess? The honest answer has three
  measured faces:

    (1) EXPLICIT certificate — the full winning-strategy tree (every White
        move against every Black reply): counted here EXACTLY, big-int
        arithmetic. It explodes exponentially in the win depth even for
        THREE pieces (KRK/KQK).
    (2) IMPLICIT certificate — the DTM table: polynomial for a fixed piece
        count, O(n^6) for KRK/KQK ("polynomial islands", T14-ii), but it
        self-destructs when the piece count grows with n (T13/T14-iii:
        the tunnel argument; generalized chess is EXPTIME-complete).
    (3) POLYNOMIAL approximation — the ParticleSolver: always polynomial,
        measurably NOT exact (E1: loses 17.56% / 4.38% of the wins).

  THE TRILEMMA (measured, not conjectured): polynomial / exact / explicit —
  pick any two. An object that is all three for generalized chess would put
  EXPTIME-complete win detection into P, contradicting the deterministic
  time hierarchy (Hartmanis–Stearns 1965): P ⊊ EXPTIME is a THEOREM.

  Chess itself cannot settle P vs NP: chess-win is EXPTIME-complete, so
  chess-win ∈ NP would imply the OPEN identity NP = EXPTIME, and
  chess-win ∉ NP would imply NP ≠ EXPTIME — both out of reach of current
  techniques. What this program CAN do is measure the exact shape of the
  wall. E3 measures one face of it.

  METHOD. For every won White-to-move state w (dtm[w] = D plies) the minimal
  DTM-greedy strategy tree is counted exactly on the UNFOLDED tree:

      T(w) = 1 + min_{b : dtm[b] = D-1} ( 1 + Σ_{r ∈ replies(b)} T(r) )

  b runs over White's optimal moves (Bellman: dtm[w] = D forces the best
  child to dtm[b] = D-1 and forbids anything faster), r over ALL legal Black
  replies (Black resists with everything it has). Shared subpositions are
  counted once per occurrence — the TREE, not the DAG; the COMPUTATION is
  memoised, so it costs O(#states · branching) while the counted VALUES
  stay exact integers. The White choice is minimised over optimal moves,
  so the measurement yields the SMALLEST explicit exact certificate —
  a lower bound on what any certifier could achieve.

  MEASURED (see results/complexity_certificates.json): the minimal tree
  grows exponentially in n — log10 T ≈ 0.91·n for KRK (base ≈ 8, the
  king's maximal branching) and ≈ 0.60·n for KQK (base ≈ 4) — while the
  implicit DTM table is polynomial, n^6. At the classical board the two
  are already comparable (KRK n = 8: 5.0·10^5 tree nodes vs 4.0·10^5
  table states), and for every larger n the explicit certificate loses
  by an ever-widening margin: ~10^0.4 extra orders of magnitude per +1
  of n.

  Verification asymmetry: checking ONE line of play costs O(D) moves;
  checking the COMPLETE certificate costs Θ(T(w)) nodes. This gap between
  polynomial checking of a single witness line and the exponential size of
  the full witness is exactly the shape of the wall that separates exact
  play from polynomial descriptions.

  USAGE:
      python3 complexity/experiment_certificates.py [--max-n 8] [--pieces RQ] [--plot]
      → results/complexity_certificates.json + console table
        (+ reports/plots/complexity/certificates.png with --plot)
═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dynamics import unpack_state  # noqa: E402  (wk, wq, bk, stm)
from generalized_chess import (  # noqa: E402
    _board3, _children_white_n, _children_black_n,
    retro_dtm_nxn, squares_n,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, 'results')
PLOTS = os.path.join(ROOT, 'reports', 'plots', 'complexity')


def state_to_fen(wk, wq, bk, stm, code):
    """FEN of a KRK/KQK position on the 8x8 frame (all states use n<=8)."""
    sym = 'R' if code == 4 else 'Q'
    grid = {wk: 'K', wq: sym, bk: 'k'}
    rows = []
    for r in range(7, -1, -1):
        row, emp = '', 0
        for f in range(8):
            ch = grid.get(16 * r + f)
            if ch is None:
                emp += 1
            else:
                if emp:
                    row += str(emp)
                    emp = 0
                row += ch
        if emp:
            row += str(emp)
        rows.append(row)
    return '/'.join(rows) + (' w - - 0 1' if stm == 0 else ' b - - 0 1')


def analyze(n, code, piece_name, log=print):
    """Full E3 pass for one (n, piece): exact minimal strategy-tree sizes."""
    t0 = time.time()
    dtm, stats = retro_dtm_nxn(n, code)
    valid = set(squares_n(n))
    sys.setrecursionlimit(20000)
    memo = {}

    def tree_size(s):
        v = memo.get(s)
        if v is not None:
            return v
        wk, wq, bk, _stm = unpack_state(s)
        D = dtm[s]
        board = _board3(wk, wq, bk, code)
        best = None
        for b in _children_white_n(wk, wq, bk, code, board):
            if dtm[b] != D - 1:
                continue                       # keep only optimal moves
            bwk, bwq, bbk, _ = unpack_state(b)
            bboard = _board3(bwk, bwq, bbk, code)
            replies, captured = _children_black_n(
                bwk, bwq, bbk, code, bboard, valid)
            assert not captured, 'a won BTM state cannot offer a capture'
            total = 1                          # the Black-to-move node b
            for r in replies:
                assert dtm[r] >= 0, 'every reply of a won BTM state is won'
                total += tree_size(r)
            if best is None or total < best:
                best = total                   # minimal certificate choice
        assert best is not None, 'Bellman: an optimal move must exist'
        val = 1 + best                         # the White-to-move node w
        memo[s] = val
        return val

    won_wtm = 0
    max_tree = 0
    argmax = None
    log10s = []
    for s in range(1 << 22):
        if not (s >> 21) and dtm[s] > 0:
            won_wtm += 1
            t = tree_size(s)
            log10s.append(math.log10(t))
            if t > max_tree:
                max_tree, argmax = t, s

    # states whose unfolded tree already exceeds the whole DTM table
    over_table = sum(1 for v in memo.values() if v > stats['states'])

    # verification walk on the hardest state: optimal line, best resistance
    line = [argmax]
    s = argmax
    while dtm[s] > 0:
        wk, wq, bk, _ = unpack_state(s)
        D = dtm[s]
        board = _board3(wk, wq, bk, code)
        best_b, best_r, best_rdtm = None, None, -1
        for b in _children_white_n(wk, wq, bk, code, board):
            if dtm[b] != D - 1:
                continue
            bwk, bwq, bbk, _ = unpack_state(b)
            bboard = _board3(bwk, bwq, bbk, code)
            replies, _cap = _children_black_n(bwk, bwq, bbk, code, bboard,
                                              valid)
            worst = max(dtm[r] for r in replies) if replies else 0
            if best_b is None or len(replies) < len(best_replies) or \
               (len(replies) == len(best_replies) and worst > best_rdtm):
                best_b, best_replies, best_rdtm = b, replies, worst
        assert best_b is not None
        line.append(best_b)
        if not best_replies:
            break                              # checkmate delivered
        s = max(best_replies, key=lambda r: dtm[r])
        line.append(s)
    assert dtm[line[-1]] == 0 and (line[-1] >> 21) == 1, 'line ends in mate'
    assert len(line) - 1 == dtm[argmax], 'line length equals DTM'

    row = {
        'n': n,
        'piece': piece_name,
        'states': stats['states'],
        'edges': stats['edges'],
        'won_wtm_states': won_wtm,
        'max_dtm_plies': stats['max_plies'],
        'max_dtm_moves': stats['max_moves'],
        'max_tree_nodes': str(max_tree),
        'log10_max_tree': round(math.log10(max_tree), 3),
        'median_log10_tree': round(sorted(log10s)[len(log10s) // 2], 3),
        'log10_states': round(math.log10(stats['states']), 3),
        'tree_over_states': str(max_tree // max(1, stats['states'])),
        'states_over_tree_exponent': round(
            math.log10(max_tree) - math.log10(stats['states']), 3),
        'trees_larger_than_table': over_table,
        'strategy_dag_states_computed': len(memo),
        'argmax_fen': state_to_fen(*unpack_state(argmax)[:3],
                                   unpack_state(argmax)[3], code),
        'one_line_plies': dtm[argmax],
        'elapsed_seconds': round(time.time() - t0, 1),
    }
    log(f"  KRK/KQK n={n} {piece_name}: states={stats['states']:>7} "
        f"maxDTM={stats['max_moves']:>2}m  "
        f"max|T|={max_tree:.3e} (10^{row['log10_max_tree']:.2f})  "
        f"ratio={row['tree_over_states'][:12]}")
    return row


def make_plot(rows, out_png):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.4), dpi=600,
                           constrained_layout=True)
    marks = {'R': 'o-', 'Q': 's--'}
    colors = {'R': '#1f3a5f', 'Q': '#7a5aa0'}
    for piece in ('R', 'Q'):
        pts = [r for r in rows if r['piece'] == piece]
        if not pts:
            continue
        xs = [r['n'] for r in pts]
        ax.plot(xs, [r['log10_max_tree'] for r in pts], marks[piece],
                color=colors[piece], lw=2.0, ms=6,
                label=f'minimal strategy tree, K+{piece} vs K (exact)')
        ax.plot(xs, [r['log10_states'] for r in pts], marks[piece],
                color=colors[piece], lw=1.1, ms=4, alpha=0.45,
                label=f'DTM table size, K+{piece} vs K (O(n$^6$))')
    ax.set_xlabel('board size n')
    ax.set_ylabel(r'size, $\log_{10}$')
    ax.set_title('E3 · certificate explosion: the exact explicit certificate\n'
                 'grows exponentially in the win depth; the implicit table '
                 'stays O(n$^6$)')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc='upper left')
    fig.savefig(out_png)
    plt.close(fig)
    print(f'  plot -> {out_png}')


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='E3: exact minimal winning-strategy tree sizes (KRK/KQK)')
    ap.add_argument('--max-n', type=int, default=8)
    ap.add_argument('--pieces', type=str, default='RQ',
                    help='subset of "RQ"')
    ap.add_argument('--plot', action='store_true')
    args = ap.parse_args(argv)

    print('E3 · certificate explosion (exact big-int strategy trees)')
    rows = []
    for piece_name in ('R', 'Q'):
        code = 4 if piece_name == 'R' else 5
        if piece_name not in args.pieces.upper():
            continue
        for n in range(4, args.max_n + 1):
            rows.append(analyze(n, code, piece_name))

    out = {
        'experiment': 'E3 certificate explosion',
        'definition': ('T(w) = 1 + min_{b: dtm[b]=dtm[w]-1} '
                       '(1 + sum_{r in replies(b)} T(r)); minimal '
                       'DTM-greedy winning-strategy tree counted exactly '
                       'on the unfolded tree (tree, not DAG), memoised '
                       'computation, big-int values'),
        'criterion_note': ("an 'approximation sufficient for an exact "
                           "solution' would be an exact polynomial "
                           "algorithm; for EXPTIME-complete generalized "
                           "chess it is excluded by the time hierarchy "
                           "(T13); for 3-piece endgames the implicit table "
                           "is polynomial (T14-ii) while the explicit "
                           "certificate explodes (this experiment)"),
        'verification_asymmetry': ('one line of play: O(DTM) plies; the '
                                   'complete certificate: Theta(max_tree) '
                                   'nodes — witness checking is polynomial, '
                                   'witness writing is exponential'),
        'rows': rows,
        'verdicts': {},
        'note': ('The explicit exact certificate is exponential in the win '
                 'depth even for 3 pieces; the implicit DTM table is '
                 'polynomial only while the piece count stays fixed; the '
                 'particle approximation is polynomial but measurably '
                 'inexact (E1). Polynomial / exact / explicit — pick two. '
                 'All three simultaneously would collapse EXPTIME to P, '
                 'contradicting Hartmanis–Stearns (1965).'),
    }
    for piece_name in ('R', 'Q'):
        pts = [r for r in rows if r['piece'] == piece_name]
        if pts:
            top = max(pts, key=lambda r: r['log10_max_tree'])
            out['verdicts'][piece_name] = {
                'hardest': f"n={top['n']}",
                'max_tree_nodes': top['max_tree_nodes'],
                'log10_max_tree': top['log10_max_tree'],
                'log10_states': top['log10_states'],
                'exponent_gap_orders_of_magnitude':
                    top['states_over_tree_exponent'],
            }

    os.makedirs(RESULTS, exist_ok=True)
    out_path = os.path.join(RESULTS, 'complexity_certificates.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'  results -> {out_path}')

    if args.plot:
        make_plot(rows, os.path.join(PLOTS, 'certificates.png'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
