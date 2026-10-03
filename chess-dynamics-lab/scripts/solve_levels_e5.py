#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Experiment E5 — the solution-level ladder (companion of note N2,
complexity/SOLVING_CHESS.md: "Can chess be solved like checkers?").

The question the user asked deserves a MEASURED answer, not a shrug.
"Solved, as checkers" has three formal levels (ultra-weak / weak /
strong); Chinook delivered the WEAK one for checkers in 2007.  This
program owns four frozen endgame spaces (KRK, KQK, KNK, KPK) — and E5
establishes, from the frozen certificates and live recomputation,
exactly WHICH level each of them sits at, and WHY the same methodology
cannot be scaled to 32 pieces.

What E5 does, layer by layer:

  STRONG level   — every legal position valued + the optimal move known.
                   The four tables already do this; E5 re-derives the
                   population census (WTM/BTM won vs drawn) from the
                   frozen trap census and cross-asserts it against the
                   table headers (states, won, mates, max DTM).  The
                   coverage is 100.0000% of legal states per space.

  ULTRA-WEAK     — the game-theoretic value of the initial position.
                   E5 probes the classical doctrine anchors live and
                   asserts them: the c8=Q# mate, both stalemate traps,
                   the frontal-opposition draw AND its "lost opposition"
                   twin (win in 18 plies), the shoulder line (the
                   deepest KPK win, 28 moves), the king-in-front rule,
                   the undefended-pawn resource, the oracle KRK box,
                   a canonical KQK start — and the KNK universal draw
                   (T15: 0 won states out of 429,440 by exhaustion).

  WEAK level     — value + an explicit strategy from the start.  E5
                   walks the full optimal principal variation (greedy
                   attacker vs maximally resistant defender) and builds
                   the MINIMAL DTM-greedy winning-strategy tree (the E3
                   recursion T(w) = 1 + min_{optimal b} (1 + Σ_r T(r)))
                   — the explicit object that PROVES the win against
                   every defence.  For KPK the tree and the PV cross the
                   promotion boundary into the KQK space exactly as the
                   build does.  The E3-argmax KRK position is recomputed
                   independently and must reproduce the frozen
                   max_tree_nodes = 500,900 — two implementations, one
                   number.

  THE WALL       — why this cannot be scaled to chess.  The E2 n-ladder
                   (exact states 3,496 -> 399,112 for n = 4..8) meets
                   the literature ladder (5-man ≈ 1 GB ... 7-man ≈
                   18.4 TB tablebases; checkers ≈ 5·10^20 states,
                   weakly solved 2007 after 18 years; chess ≥ 4.5·10^44
                   legal positions, ~10^120 game tree) and the exact
                   big-int extrapolations: a full-chess table at even
                   1 byte/state is ~10^21 × the world's digital storage
                   and ~10^18 × the age of the universe at 10^9
                   states/s.  The wall is measured, not conjectured
                   (T13: generalized chess is EXPTIME-complete and
                   P ⊊ EXPTIME is a theorem).

Frozen output: results/solve_levels_e5.json.

Usage: python3 scripts/solve_levels_e5.py
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'vortex'))

from vortex import vortex_dynamics as V          # noqa: E402

RESULTS = os.path.join(ROOT, 'results')
KQK_DTM = None                                   # set in main()


# ═══════════════════════════ square naming ══════════════════════════════
def sq(name):
    """'d6' -> the 0x88 square."""
    return (int(name[1]) - 1) * 16 + (ord(name[0]) - 97)


def alg(s):
    """The 0x88 square -> 'd6'."""
    return 'abcdefgh'[s & 7] + str((s >> 4) + 1)


def probe(kind, wf, pf, bf, stm):
    return V.probe(kind, V.pack(kind, sq(wf), sq(pf), sq(bf), stm))


# ══════════════════════════ the optimal-pv walker ═══════════════════════
def walk_pv(kind, wf, pf, bf, stm):
    """The full optimal game: greedy attacker (child at d-1) vs the
    maximally resistant defender (max child value).  Returns the move
    list as ['d6e7', ...].  A KPK promotion switches the walker into the
    KQK space exactly as the frozen build does."""
    wk, wp, bk = sq(wf), sq(pf), sq(bf)
    d = V.probe(kind, V.pack(kind, wk, wp, bk, stm))
    if d < 0:
        raise AssertionError('weak start must be won, got draw')
    d0 = d
    moves = []
    while True:
        if stm == 0:
            children = V.children_white(
                kind, wk, wp, bk, V.load_frozen(kind)['dtm'],
                KQK_DTM if kind == 'kpk' else None)
            opts = [(v, f, t) for (v, f, t) in children if v == d - 1]
            if not opts:
                raise AssertionError('no optimal child at d=%d' % d)
            v, f, t = min(opts, key=lambda x: (x[1], x[2]))
            if kind == 'kpk' and f == wp and (t >> 4) == 7:
                kind, wp = 'kqk', t            # auto-queen: new space
            elif f == wk:
                wk = t
            else:
                wp = t
            moves.append(alg(f) + alg(t))
            stm = 1
            d = v
            if v == 0:                         # the child IS the mate
                break
        else:
            children, captured = V.children_black(kind, wk, wp, bk)
            if captured or not children:
                raise AssertionError('defender escape in a won line')
            best = max((V.probe(kind, c), c) for c in children)
            v, child = best
            if v < 0:
                raise AssertionError('Bellman violation: drawn reply '
                                     'in a won BTM state')
            nbk = (child >> 14) & 127
            moves.append(alg(bk) + alg(nbk))
            bk, stm, d = nbk, 0, v
    if len(moves) != d0:
        raise AssertionError('PV length %d != DTM %d'
                             % (len(moves), d0))
    return moves


# ════════════════════ the minimal strategy tree (E3 recursion) ══════════
def _tree(kind, wk, wp, bk, stm, memo):
    """Nodes (and mate leaves) of the minimal DTM-greedy winning-strategy
    tree.  WTM node: 1 + min over optimal children (1 + T(child)).
    BTM node: 1 + Σ over every legal reply.  Mate (d = 0): 1 node."""
    key = (kind, wk, wp, bk, stm)
    if key in memo:
        return memo[key]
    d = V.probe(kind, V.pack(kind, wk, wp, bk, stm))
    if d == 0:                                 # terminal mate on board
        memo[key] = (1, 1)
        return memo[key]
    if d < 0:
        raise AssertionError('strategy tree entered a drawn state — '
                             'Bellman violation at %s' % (key,))
    if stm == 0:
        children = V.children_white(
            kind, wk, wp, bk, V.load_frozen(kind)['dtm'],
            KQK_DTM if kind == 'kpk' else None)
        best = None
        for v, f, t in children:
            if v != d - 1:
                continue
            if kind == 'kpk' and f == wp and (t >> 4) == 7:
                ck = 'kqk'                     # promotion boundary
                nwk, nwp, nbk, nstm = wk, t, bk, 1
            else:
                ck = kind
                if f == wk:
                    nwk, nwp, nbk, nstm = t, wp, bk, 1
                else:
                    nwk, nwp, nbk, nstm = wk, t, bk, 1
            sub, leaves = _tree(ck, nwk, nwp, nbk, nstm, memo)
            # the child BTM node is already counted inside `sub`
            # (its branch returns 1 + Σ replies); E3's accounting:
            # T(w) = 1 + min_b (1 + Σ_r T(r)) — the parent node + the
            # child node + the reply subtrees.
            cand = sub
            if best is None or cand < best[0]:
                best = (cand, leaves)
        if best is None:
            raise AssertionError('no optimal child at d=%d' % d)
        memo[key] = (1 + best[0], best[1])
    else:
        children, captured = V.children_black(kind, wk, wp, bk)
        if captured or not children:
            raise AssertionError('drawn escape inside a won subtree')
        total, leaves = 0, 0
        for c in children:
            sub, lf = _tree(kind, wk, wp, (c >> 14) & 127, 0, memo)
            total += sub
            leaves += lf
        memo[key] = (1 + total, leaves)
    return memo[key]


def tree_size(kind, wf, pf, bf, stm):
    memo = {}
    nodes, leaves = _tree(kind, sq(wf), sq(pf), sq(bf), stm, memo)
    return {'nodes': nodes, 'mate_leaves': leaves}


# ═══════════════════════════ the three levels ═══════════════════════════
def strong_level():
    """Strong solution: population census per space, cross-asserted."""
    census = json.load(open(os.path.join(RESULTS, 'trap_census.json')))
    out = {}
    for kind in V.KINDS:
        frozen = V.load_frozen(kind)
        stats = frozen['stats']
        w = census['kinds'][kind]['wtm']
        b = census['kinds'][kind]['btm']
        total = w['states'] + b['states']
        # cross-asserts: the census must agree with the table headers
        if total != stats['states']:
            raise AssertionError('%s: census %d != table %d states'
                                 % (kind, total, stats['states']))
        if w['won_states'] + b['won_states'] != stats['won']:
            raise AssertionError('%s: census won mismatch' % kind)
        drawn = w['states'] - w['won_states'] + b['drawn_states']
        kb = os.path.getsize(os.path.join(
            RESULTS, 'dtm_%s.json.gz' % kind)) / 1024.0
        out[kind] = {
            'states': total,
            'won': stats['won'],
            'drawn': drawn,
            'mates': stats['mates'],
            'max_dtm_plies': stats['max_plies'],
            'wtm_states': w['states'],
            'wtm_won': w['won_states'],
            'btm_states': b['states'],
            'btm_won': b['won_states'],
            'btm_drawn': b['drawn_states'],
            'coverage': 1.0,
            'bellman_verified': frozen['bellman_verified'],
            'table_kb': round(kb, 1),
        }
        print('  strong %-4s %7d states (%d won, %d drawn) · max DTM '
              '%2d plies · %7.1f KB · Bellman %s' % (
                  kind, total, stats['won'], drawn,
                  stats['max_plies'], kb,
                  'verified' if frozen['bellman_verified'] else 'NO'),
              flush=True)
    return out


ULTRA_WEAK_ANCHORS = [
    ('krk', 'c2', 'b4', 'c8', 0, 19,
     'the oracle box: the rook win is 19 plies deep from here'),
    ('kqk', 'a1', 'h1', 'e8', 0, 13,
     'canonical long-side start: queen far from her king, win in 13'),
    ('knk', 'e1', 'd4', 'e8', 0, -1,
     'insufficient material: a knight mate does not exist (T15)'),
    ('kpk', 'b6', 'c7', 'a8', 0, 1,
     'the promotion corner: 1.c8=Q is checkmate'),
    ('kpk', 'b6', 'c7', 'a7', 0, -1,
     'the under-promotion trap: 1.c8=Q/R is stalemate'),
    ('kpk', 'b6', 'c7', 'a8', 1, -1,
     'stalemate on the board: Black to move, no legal moves'),
    ('kpk', 'd6', 'e6', 'd8', 0, -1,
     'the frontal opposition: the classical draw'),
    ('kpk', 'd6', 'e6', 'd8', 1, 18,
     'the same squares, defender to move: opposition lost, win in 18'),
    ('kpk', 'a3', 'g2', 'a5', 1, 56,
     'the shoulder line: the deepest KPK win — 28 moves'),
    ('kpk', 'e6', 'e5', 'e8', 0, 21,
     'king in front of the pawn: the textbook rule, win in 21'),
    ('kpk', 'a1', 'e2', 'd3', 1, -1,
     'the undefended checking pawn: Kxe2 escapes into K vs K'),
]

WEAK_STARTS = [
    ('krk', 'c2', 'b4', 'c8', 0,
     'the oracle box: a complete weak solution — main line + the '
     'minimal strategy tree against every defence'),
    ('kqk', 'a1', 'h1', 'e8', 0,
     'the long-side queen start: same protocol'),
    ('kpk', 'e6', 'e5', 'e8', 0,
     'king in front: the strategy tree crosses the promotion boundary '
     'into the KQK space exactly as the build does'),
]

E3_ARGMAX = ('krk', 'a8', 'c2', 'd3', 0)   # K7/8/8/8/8/3k4/2R5/8 w
E3_MAX_TREE = 500900                        # frozen in complexity_certificates


def ultra_weak_level():
    out, fails = [], 0
    for kind, wf, pf, bf, stm, want, label in ULTRA_WEAK_ANCHORS:
        got = probe(kind, wf, pf, bf, stm)
        ok = got == want
        fails += 0 if ok else 1
        out.append({'kind': kind, 'white_king': wf, 'piece': pf,
                    'black_king': bf, 'stm': stm, 'expected': want,
                    'probed': got, 'pass': ok, 'label': label})
        print('  ultra-weak %-4s %s%s%s stm=%d: %4d (want %4d) %s'
              % (kind, wf, pf, bf, stm, got, want,
                 'PASS' if ok else 'FAIL'), flush=True)
    knk = V.load_frozen('knk')['stats']
    universal = {'kind': 'knk', 'states': knk['states'],
                 'won_states': knk['won'],
                 'statement': 'every state of the space is a draw: '
                              'neither side can ever mate (T15 by '
                              'exhaustion) — the ultra-weak, weak and '
                              'strong levels COLLAPSE into one'}
    if knk['won'] or knk['mates']:
        fails += 1
    print('  ultra-weak knk: won=%d mates=%d over %d states — the '
          'universal draw (T15)' % (knk['won'], knk['mates'],
                                    knk['states']), flush=True)
    if fails:
        raise AssertionError('%d ultra-weak anchors FAILED' % fails)
    return {'anchors': out, 'knk_universal_draw': universal}


def weak_level():
    out = []
    for kind, wf, pf, bf, stm, label in WEAK_STARTS:
        d = probe(kind, wf, pf, bf, stm)
        pv = walk_pv(kind, wf, pf, bf, stm)
        tree = tree_size(kind, wf, pf, bf, stm)
        space = V.load_frozen(kind)['stats']['states']
        out.append({
            'kind': kind, 'white_king': wf, 'piece': pf,
            'black_king': bf, 'stm': stm, 'dtm_plies': d,
            'pv_moves': pv, 'pv_length': len(pv),
            'mate_confirmed': True,
            'strategy_tree': {
                'nodes': tree['nodes'],
                'mate_leaves': tree['mate_leaves'],
                'share_of_space': round(tree['nodes'] / space, 6),
            },
            'label': label,
        })
        print('  weak %-4s %s%s%s stm=%d: DTM %2d = %2d plies, tree '
              '%7d nodes (%d mate leaves, %.4f%% of the space) · PV '
              '%s...' % (
                  kind, wf, pf, bf, stm, d, len(pv), tree['nodes'],
                  tree['mate_leaves'],
                  100.0 * tree['nodes'] / space,
                  ' '.join(pv[:4])), flush=True)
    # ── the independent E3 cross-check on the hardest position ─────────
    kind, wf, pf, bf, stm = E3_ARGMAX
    d = probe(kind, wf, pf, bf, stm)
    pv = walk_pv(kind, wf, pf, bf, stm)
    tree = tree_size(kind, wf, pf, bf, stm)
    cross = {
        'kind': kind, 'white_king': wf, 'piece': pf, 'black_king': bf,
        'stm': stm, 'dtm_plies': d,
        'pv_length': len(pv), 'pv_moves': pv,
        'tree_nodes_recomputed': tree['nodes'],
        'tree_nodes_frozen_e3': E3_MAX_TREE,
        'match': tree['nodes'] == E3_MAX_TREE,
        'note': 'the hardest WTM position: two independent '
                'implementations of the minimal-strategy-tree recursion '
                'must produce one number',
    }
    print('  weak krk (E3 argmax) %s%s%s: DTM %d, tree %d nodes vs '
          'frozen E3 %d — %s' % (
              wf, pf, bf, d, tree['nodes'], E3_MAX_TREE,
              'MATCH' if cross['match'] else 'MISMATCH'), flush=True)
    if not cross['match']:
        raise AssertionError('E3 cross-check failed: %d != %d'
                             % (tree['nodes'], E3_MAX_TREE))
    return {'starts': out, 'e3_argmax_cross_check': cross}


def deepest_states():
    """Exact argmax scan of each frozen table, per side to move."""
    out = {}
    for kind in V.KINDS:
        dtm = V.load_frozen(kind)['dtm']
        best = {0: (0, -1), 1: (0, -1)}        # stm -> (state, value)
        count = {0: 0, 1: 0}
        for s in range(1 << 22):
            v = dtm[s]
            if 0 <= v < 200:
                stm = (s >> 21) & 1
                if v > best[stm][1]:
                    best[stm] = (s, v)
                    count[stm] = 1
                elif v == best[stm][1] and best[stm][1] >= 0:
                    count[stm] += 1
        row = {}
        for stm in (0, 1):
            s, v = best[stm]
            wk, wp, bk, stmv = V.unpack(s)
            row['wtm' if stm == 0 else 'btm'] = {
                'squares': [alg(wk), alg(wp), alg(bk)],
                'dtm_plies': v if v >= 0 else None,
                'positions_at_max': count[stm],
            }
        out[kind] = row
        fmt = lambda side: ('%s (%d plies, x%d)' % (
            '/'.join(row[side]['squares']),
            row[side]['dtm_plies'], row[side]['positions_at_max']))
        if row['wtm']['dtm_plies'] is None:
            fmt = lambda side: '(no won states)'
        print('  deepest %-4s WTM %s · BTM %s'
              % (kind, fmt('wtm'), fmt('btm')), flush=True)
    return out


# ═════════════════════════════ the wall ═════════════════════════════════
def the_wall():
    scaling = json.load(open(
        os.path.join(RESULTS, 'complexity_scaling.json')))
    n_ladder = [{'n': r['n'], 'states': r['states'],
                 'edges': r['edges'],
                 'max_dtm_moves': r['max_dtm_moves'],
                 'theory_n6': r['states_theory_n6']}
                for r in scaling['rows']]
    total_states = sum(V.load_frozen(k)['stats']['states']
                       for k in V.KINDS)
    total_kb = sum(os.path.getsize(
        os.path.join(RESULTS, 'dtm_%s.json.gz' % k))
        for k in V.KINDS) / 1024.0

    piece_ladder = [
        {'scope': '3 pieces on 8x8 (this program, exact)',
         'value': '399,112 states (KRK) · 124 KB frozen'},
        {'scope': '5 men (Syzygy tablebases)', 'value': '≈ 1 GB'},
        {'scope': '6 men (Syzygy tablebases)', 'value': '≈ 150 GB'},
        {'scope': '7 men (Syzygy tablebases)', 'value': '≈ 18.4 TB'},
        {'scope': '8 men', 'value': '≈ 2 PB (published estimates)'},
        {'scope': 'checkers, 24 men — WEAKLY solved, 2007',
         'value': '≈ 5·10^20 positions · endgame databases ≤ 8 pieces '
                  'plus selected 9/10-piece blocks (the 10-piece block '
                  'alone ≈ 3.9·10^13 positions) · 18 years of '
                  'computation (1989–2007)'},
        {'scope': 'chess, 32 men — NOT SOLVED, not even ultra-weak',
         'value': '≥ 4.5·10^44 legal positions (Tromp lower bound; '
                  'estimate ≈ 4.8·10^44) · game-tree ≈ 10^120 (Shannon) '
                  '· longest game ≤ 8,848.5 moves with the 50-move rule'},
    ]
    # exact big-int extrapolations (constants cited from the ladder)
    chess_positions = 482 * 10 ** 42          # ≈ 4.82·10^44 (estimate)
    bytes_needed = chess_positions            # 1 byte/state is generous
    world_storage_bytes = 15 * 10 ** 22       # ≈ 150 ZB (2025 estimate)
    rate = 10 ** 9                            # states per second
    seconds_per_year = 31557600
    universe_years = 138 * 10 ** 8
    checkers_positions = 5 * 10 ** 20
    computed = {
        'four_spaces_states': total_states,
        'four_spaces_table_kb': round(total_kb, 1),
        'bytes_per_state_frozen': round(total_kb * 1024 / total_states,
                                        4),
        'full_chess_bytes_at_1B_per_state': str(bytes_needed),
        'full_chess_tb_of_storage': '%.2e' % (bytes_needed / 10 ** 12),
        'ratio_to_world_storage': '%.2e' % (bytes_needed
                                            / world_storage_bytes),
        'years_at_1e9_states_per_s': '%.2e' % (bytes_needed / rate
                                               / seconds_per_year),
        'ratio_to_universe_age': '%.2e' % (bytes_needed / rate
                                           / seconds_per_year
                                           / universe_years),
        'checkers_to_chess_space_ratio': '%.2e' % (chess_positions
                                                   / checkers_positions),
        'assumption': '1 byte per state (the frozen tables need even '
                      'less: %.2f B/state); no index, no strategy, '
                      'just the raw values' % (total_kb * 1024
                                               / total_states),
    }
    print('  wall: 4 spaces = %d states in %.1f KB · full chess would '
          'need %s bytes = %s × world storage' % (
              total_states, total_kb, computed[
                  'full_chess_bytes_at_1B_per_state'],
              computed['ratio_to_world_storage']), flush=True)
    return {'n_ladder_exact_e2': n_ladder,
            'piece_ladder_literature': piece_ladder,
            'computed_extrapolations': computed}


# ═══════════════════════════════ main ══════════════════════════════════
def main():
    global KQK_DTM
    t0 = time.time()
    KQK_DTM = V.load_frozen('kqk')['dtm']
    report = {
        'experiment': 'E5 — the solution-level ladder: which level of '
                      '"solved, as checkers" each frozen space sits at, '
                      'and why the ladder cannot reach 32 pieces',
        'companion_note': 'complexity/SOLVING_CHESS.md (note N2)',
        'level_definitions': {
            'ultra_weak': 'the game-theoretic value of the initial '
                          'position is known (win / draw / loss)',
            'weak': 'the value plus a strategy achieving it from the '
                    'initial position (Chinook 2007 for checkers)',
            'strong': 'every legal position valued plus the optimal '
                      'move in each (what the four tables are)',
        },
    }
    print('E5 — strong level (population census, cross-asserted):')
    report['strong'] = strong_level()
    print('E5 — ultra-weak level (doctrine anchors, live probes):')
    report['ultra_weak'] = ultra_weak_level()
    print('E5 — weak level (principal variations + strategy trees):')
    report['weak'] = weak_level()
    print('E5 — deepest states (exact argmax per space and side):')
    report['deepest'] = deepest_states()
    print('E5 — the wall (exact n-ladder meets the literature ladder):')
    report['wall'] = the_wall()
    report['verdict'] = [
        'checkers: WEAKLY solved (Schaeffer et al., Science 2007) — '
        'value + strategy from the initial position, draw; not strong',
        'chess: not even ultra-weak; the believed draw is belief, not '
        'a theorem',
        'this program: four subspaces solved STRONGLY (100% coverage, '
        'Bellman-verified), weak certificates from canonical starts '
        '(explicit strategy trees), ultra-weak draws by exhaustion '
        '(T15) — the Chinook methodology at the scale where it is '
        'exact',
        'the wall is measured, not conjectured: T13 (EXPTIME-complete '
        'generalized chess, P ⊊ EXPTIME), E3 (explicit certificates '
        'overtake the table), E5 (storage/time extrapolation: ~10^21 × '
        'world storage, ~10^18 × the age of the universe)',
        'therefore "solve chess like checkers" is not an engineering '
        'scale-up: it needs a mathematics that does not exist today — '
        'e.g., a general draw invariant for 32-piece play',
    ]
    report['runtime_s'] = round(time.time() - t0, 1)
    out = os.path.join(RESULTS, 'solve_levels_e5.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print('frozen ->', out)
    print('E5 PASSED (%.1fs)' % report['runtime_s'])


if __name__ == '__main__':
    main()
