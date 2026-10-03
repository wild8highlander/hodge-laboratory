#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  COMPLEXITY LABORATORY · experiment_particles_vs_oracle.py
  Experiment E1: the polynomial particle solver AGAINST the exact retrograde
  DTM oracle, on the frozen 8x8 KRK and KQK tables.

  chess-dynamics-lab · author: Isaev Iskhak Khamzatovich · exclusive license

  QUESTION (T14-i). The ParticleSolver is a polynomial-time move chooser
  (O(n^4) per move, no DTM knowledge). If a polynomial heuristic is all one
  can afford, how much of the win does it actually keep?

  PROTOCOL. Sample N won White-to-move positions from the frozen table.
  For each position:
      p0        — the exact DTM of the position (plies, white to move);
      m_part    — the particle solver's greedy move;
      d_part    — exact DTM after m_part (black to move); -1 = draw/lost;
      d_opt     — min over ALL legal moves of the exact DTM after the move
                  (the true optimal continuation value);
  and record:
      saved     — d_part >= 0   (the greedy move keeps the forced win);
      delta     — d_part - d_opt (how much slower the greedy win is);
      equal     — d_part == d_opt (the greedy move was optimal).
  Reported per depth bucket of p0 (in moves) — the "particle horizon" view:
  errors concentrate where the reason is not locally visible.

  USAGE:
      python3 complexity/experiment_particles_vs_oracle.py [--sample 5000]
      → results/complexity_particles_vs_oracle.json + console table
═══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dynamics import (  # noqa: E402
    SQUARES, pack_state, unpack_state, load_dtm_cache, dtm_state_of,
    move_to_uci, Position,
)
from generalized_chess import (  # noqa: E402
    ParticleSolver, position_from_state, state_of_position,
)

RESULTS = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'results')


def enumerate_won_wtm(dtm):
    """All won White-to-move states (packed ints) of a frozen table."""
    out = []
    for wk in SQUARES:
        for wp in SQUARES:
            if wp == wk:
                continue
            for bk in SQUARES:
                if bk == wk or bk == wp:
                    continue
                s = pack_state(wk, wp, bk, 0)
                if dtm[s] >= 0:
                    out.append(s)
    return out


def optimal_child_dtm(pos, dtm):
    """min exact DTM over all legal moves (value of the optimal continuation).
    Returns None if no legal move reaches a won state (should not happen for
    a won White-to-move position)."""
    best = None
    for m in pos.legal_moves():
        undo = pos.make(m)
        st = state_of_position(pos)
        d = dtm_state_of(dtm, *st) if st is not None else -2
        pos.unmake(undo)
        if d >= 0 and (best is None or d < best):
            best = d
    return best


def run_piece(piece_char, sample_size, seed):
    """Run the E1 protocol for one endgame table ('R' or 'Q').
    NOTE: load_dtm_cache expects the piece CODE (4=rook, 5=queen)."""
    piece_code = 5 if piece_char == 'Q' else 4
    loaded = load_dtm_cache(piece_code)
    if loaded is None:
        raise SystemExit('frozen table results/dtm_%s not found'
                         % ('kqk' if piece_char == 'Q' else 'krk'))
    dtm, dstats = loaded
    print('— %s: oracle loaded (%d states, max %d moves), sampling...'
          % (piece_char, dstats['states'], dstats['max_moves']))

    t0 = time.time()
    won = enumerate_won_wtm(dtm)
    rng = random.Random(seed)
    if len(won) > sample_size:
        sample = rng.sample(won, sample_size)
    else:
        sample = won
    print('  won WTM states: %d, sampled: %d' % (len(won), len(sample)))

    solver = ParticleSolver(n=8)
    buckets = {}          # depth(moves) -> [n, n_saved, n_equal, deltas]
    deltas = []           # all delta values (saved only)
    d0_list = []          # depth of every sampled position
    lost_examples = []    # (d0, fen_before, uci, fen_after)
    n_saved = n_equal = 0
    max_delta = 0
    t_eval = time.time()

    for idx, s in enumerate(sample):
        wk, wp, bk, stm = unpack_state(s)
        pos = position_from_state(wk, wp, bk, stm,
                                  piece=5 if piece_char == 'Q' else 4)
        if pos is None:
            continue
        d0 = dtm[s]
        d0_moves = (d0 + 1) // 2
        d0_list.append(d0_moves)

        m = solver.choose_move(pos)
        if m is None:
            continue
        uci = move_to_uci(m)
        fen_before = pos.to_fen()
        pos.make(m)
        st1 = state_of_position(pos)
        d_part = dtm_state_of(dtm, *st1) if st1 is not None else -2
        fen_after = pos.to_fen()
        # rebuild the pre-move position for the optimal-move scan
        pos = position_from_state(wk, wp, bk, stm,
                                  piece=5 if piece_char == 'Q' else 4)
        d_opt = optimal_child_dtm(pos, dtm)

        b = buckets.setdefault(d0_moves, [0, 0, 0, []])
        b[0] += 1
        if d_part >= 0:
            n_saved += 1
            b[1] += 1
            delta = d_part - (d_opt if d_opt is not None else 0)
            if delta > max_delta:
                max_delta = delta
            deltas.append(delta)
            b[3].append(delta)
            if d_part == d_opt:
                n_equal += 1
                b[2] += 1
        elif len(lost_examples) < 8:
            lost_examples.append({
                'dtm_before_moves': d0_moves,
                'fen_before': fen_before,
                'particle_move': uci,
                'fen_after': fen_after,
            })
        if (idx + 1) % 1000 == 0:
            print('   %5d/%d positions evaluated (%.0f pos/s)'
                  % (idx + 1, len(sample),
                     (idx + 1) / (time.time() - t_eval)))

    elapsed = time.time() - t0
    n = sum(b[0] for b in buckets.values())
    depth_table = []
    for d in sorted(buckets):
        cnt_, cnt_saved, cnt_equal, ds = buckets[d]
        depth_table.append({
            'depth_moves': d,
            'positions': cnt_,
            'saved': cnt_saved,
            'save_rate': round(cnt_saved / cnt_, 4),
            'optimal_rate': round(cnt_equal / cnt_, 4),
            'mean_delta': (round(sum(ds) / len(ds), 3) if ds else None),
        })

    res = {
        'piece': piece_char,
        'sample_size': len(sample),
        'evaluated': n,
        'seed': seed,
        'won_wtm_states': len(won),
        'oracle': {'states': dstats['states'], 'max_moves': dstats['max_moves']},
        'saved': n_saved,
        'lost': n - n_saved,
        'save_rate': round(n_saved / n, 5) if n else None,
        'optimal_rate': round(n_equal / n, 5) if n else None,
        'mean_delta_plies': (round(sum(deltas) / len(deltas), 4)
                             if deltas else None),
        'max_delta_plies': max_delta if deltas else None,
        'mean_dtm_moves': round(sum(d0_list) / len(d0_list), 4),
        'elapsed_seconds': round(elapsed, 1),
        'depth_table': depth_table,
        'lost_examples': lost_examples,
    }
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=5000)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    print('═' * 78)
    print('E1 · PARTICLE SOLVER vs EXACT DTM ORACLE (8x8 frozen tables)')
    print('═' * 78)
    out = {
        'experiment': 'E1 particles vs oracle',
        'solver': 'ParticleSolver (three-layer greedy, no DTM knowledge)',
        'sample': args.sample, 'seed': args.seed,
        'results': {},
    }
    for piece_char in ('R', 'Q'):
        res = run_piece(piece_char, args.sample, args.seed)
        out['results'][piece_char] = res
        print()
        print('  %s: save_rate=%.4f  optimal_rate=%.4f  mean ΔDTM=%s plies  '
              'max ΔDTM=%s' % (piece_char, res['save_rate'],
                               res['optimal_rate'], res['mean_delta_plies'],
                               res['max_delta_plies']))
        print('  %-11s %9s %8s %8s %10s' % ('depth', 'positions', 'saved',
                                            'optimal', 'mean Δ'))
        for row in res['depth_table']:
            print('  %-11s %9d %8d %8.4f %10s'
                  % ('%d mv' % row['depth_moves'], row['positions'],
                     row['saved'], row['save_rate'],
                     row['mean_delta'] if row['mean_delta'] is not None
                     else '—'))
        if res['lost_examples']:
            print('  example losses (greedy loses a won position):')
            for ex in res['lost_examples'][:3]:
                print('    DTM %2d mv: %s ; greedy %s → %s'
                      % (ex['dtm_before_moves'], ex['fen_before'],
                         ex['particle_move'], ex['fen_after']))
        print()

    path = os.path.join(RESULTS, 'complexity_particles_vs_oracle.json')
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print('written:', path)
    print('E1 DONE')


if __name__ == '__main__':
    main()
