#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLEXITY LABORATORY · make_plots.py
600 dpi figures for the EXPTIME barrier study (English labels — the
repository documentation is English; the Russian paper regenerates its own
Russian-labelled copies via monograph/src/gen_paper_tex.py).

    python3 complexity/make_plots.py
    → reports/plots/complexity/{error_vs_depth,scaling}.png

chess-dynamics-lab · author: Isaev Iskhak Khamzatovich · exclusive license
"""

import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm          # noqa: E402
for _f in ('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
    if os.path.exists(_f):
        fm.fontManager.addfont(_f)

import matplotlib.pyplot as plt               # noqa: E402

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, 'results')
OUT = os.path.join(ROOT, 'reports', 'plots', 'complexity')

NAVY = '#162032'
GOLD = '#8B7E5A'
TEAL = '#2E8B8B'
PURPLE = '#6B4E9B'
RED = '#B03A3A'


def load(name):
    with open(os.path.join(RESULTS, name)) as f:
        return json.load(f)


def plot_error_vs_depth(e1):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2),
                             constrained_layout=True)
    for ax, key, title in ((axes[0], 'R', 'KRK (rook)'),
                           (axes[1], 'Q', 'KQK (queen)')):
        res = e1['results'][key]
        rows = res['depth_table']
        d = [r['depth_moves'] for r in rows]
        save = [100 * r['save_rate'] for r in rows]
        opt = [100 * r['optimal_rate'] for r in rows]
        ax.plot(d, save, 'o-', color=NAVY, lw=2, ms=5,
                label='greedy keeps the win (save rate)')
        ax.plot(d, opt, 's--', color=GOLD, lw=2, ms=5,
                label='greedy move is optimal')
        ax.axhline(100, color=RED, lw=1, ls=':', alpha=0.7)
        ax.set_xlabel('DTM depth of the sampled position (moves)')
        ax.set_ylabel('% of positions')
        ax.set_title('%s · sampled %d won WTM positions'
                     % (title, res['evaluated']))
        ax.set_ylim(0, 105)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, loc='lower left')
    fig.suptitle('E1 · polynomial particle solver vs exact DTM oracle: '
                 'a greedy O(n^4) move loses 17.6% of KRK wins (and 4.4% '
                 'of KQK wins)', fontsize=11)
    path = os.path.join(OUT, 'error_vs_depth.png')
    fig.savefig(path, dpi=600)
    plt.close(fig)
    print('written:', path)


def plot_scaling(e2):
    rows = e2['rows']
    ns = [r['n'] for r in rows]
    states = [r['states'] for r in rows]
    theory = [r['states_theory_n6'] for r in rows]
    retro = [r['retro_seconds'] for r in rows]
    part = [r['particle']['mean_ms'] for r in rows]
    ab = [r['alphabeta_d6']['mean_ms'] for r in rows]
    dtm = [r['max_dtm_moves'] for r in rows]

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2),
                             constrained_layout=True)
    ax = axes[0]
    ax.plot(ns, states, 'o-', color=NAVY, lw=2,
            label='KRK states (measured)')
    ax.plot(ns, theory, 's--', color=GOLD, lw=2,
            label=r'$n^2(n^2-1)(n^2-2)\sim n^6$')
    ax.set_yscale('log')
    ax.set_xlabel('board size n')
    ax.set_ylabel('states')
    ax.set_title('fixed k=3: state space ~ n^6 (polynomial)')
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=8)

    ax = axes[1]
    ax.plot(ns, retro, 'o-', color=PURPLE, lw=2,
            label='retrograde build (once)')
    ax.plot(ns, ab, 's-', color=RED, lw=2,
            label='alpha-beta move, depth 6')
    ax.plot(ns, part, '^-', color=TEAL, lw=2,
            label='particle solver move (greedy)')
    ax.set_yscale('log')
    ax.set_xlabel('board size n')
    ax.set_ylabel('time (s for retrograde; ms for moves)')
    ax.set_title('times: O(n^6) preprocessing vs O(n^4) per move')
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=8)

    ax = axes[2]
    ax.plot(ns, dtm, 'o-', color=NAVY, lw=2)
    for n, d in zip(ns, dtm):
        ax.annotate('%d' % d, (n, d), textcoords='offset points',
                    xytext=(4, 4), fontsize=8)
    ax.set_xlabel('board size n')
    ax.set_ylabel('max DTM (moves)')
    ax.set_title('the DTM horizon grows with n\n'
                 '(8x8 KRK: 16 moves, Bellman-verified)')
    ax.grid(alpha=0.25)
    fig.suptitle('E2 · scaling with the board size: for a fixed piece count '
                 'everything is polynomial in n — the exponential wall is '
                 'the number of pieces', fontsize=11)
    path = os.path.join(OUT, 'scaling.png')
    fig.savefig(path, dpi=600)
    plt.close(fig)
    print('written:', path)


def main():
    os.makedirs(OUT, exist_ok=True)
    e1 = load('complexity_particles_vs_oracle.json')
    e2 = load('complexity_scaling.json')
    plot_error_vs_depth(e1)
    plot_scaling(e2)
    print('PLOTS DONE')


if __name__ == '__main__':
    main()
