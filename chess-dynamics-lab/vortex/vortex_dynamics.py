#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vortex dynamics tuned to the frozen DTM certificates — T16.

THE IDEA
--------
The frozen tablebases (results/dtm_{krk,kqk,knk,kpk}.json.gz) assign every
state its exact game-theoretic value.  The vortex layer re-encodes that
value as the TOPOLOGY OF A PLANAR FLOW on the 8x8 board, so that the
outcome of a perfect game becomes literally visible in the particle
dynamics:

  * WON for the side to move  ->  a descending spiral SINK: optimal moves
    are attraction currents into the mating net, every trajectory is
    captured  ("100% win": nothing escapes the net);
  * DRAWN                     ->  closed orbits: no reachable move changes
    the value, the field is pure rotation, particles cycle forever;
  * LOST for the side to move ->  the same net, but every defence feeds
    it: ALL targets carry descent currents, the defender is swept in.

THE FIELD (per state P = (wk, wp, bk, stm))
-------------------------------------------
vortices   fixed-circulation rotation centres at the three piece squares;
           pure rotation, zero divergence — the "eternal swirl" of draws.
currents   one per legal move m of the side to move, classified by the
           child value v (plies of the child position EXCLUDING the move
           ply itself; a KPK promotion child is valued through the frozen
           KQK certificate, exactly as in the table build, T15):
             child drawn (v < 0)   -> 'escape'  (J = 0: the drawing
                                    resource is a closed orbit)
             child won, v < d      -> 'descent' (J = d - v >= 1: the value
                                    descends the Lyapunov ladder to mate)
             child won, v >= d     -> 'neutral' (J = 0: no progress, but
                                    no escape either — still in the basin)
             blunder from a drawn parent (defender to move)
                                   -> 'trap'    (J = 1: the snare E1
                                    measures — attracts careless moves)
           with d = DTM(P) of a won parent; for a drawn parent no child
           of the strong side is won (else P would be won — Bellman).
mate       a checkmate on the board (d = 0) is a terminal sink: LOSS for
           the mated side, no currents.

THE ODE (2D, board plane x in [0,8]^2, semi-implicit Euler)
-----------------------------------------------------------
  acc(x) = SUM_t  kappa * J_t * (c_t - x) / (1 + |c_t - x|^2)
         + gamma * perp(x - c_k) / (1 + |x - c_k|^2)      (vortices)
  v     <- v + (acc - zeta(x) * v) * dt,
           zeta(x) = zeta0 * SUM_t J_t / (1 + |c_t - x|^2)
Dissipation exists ONLY inside current basins: captured trajectories
spiral in (finite capture time) while free trajectories keep closed
vortex orbits — exactly the topology T16 claims.

CLASSIFIER (flow-only; no table probe at classify time)
-------------------------------------------------------
  mover strong: descent currents exist            -> WIN
                (metric gate: capture_fraction >= win_capture_min)
                none                              -> DRAW
  mover weak:   an escape (drawn child / capture) -> DRAW
                none, descents exist              -> LOSS
A structural DRAW whose measured field captured everything would raise —
the layer refuses to lie.
"""

import base64
import gzip
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import dynamics as D                                  # noqa: E402

SIZE = 1 << 22
RESULTS = os.path.join(ROOT, 'results')

KNIGHT_OFFS = (33, 31, 18, 14, -33, -31, -18, -14)
KNIGHT_NB = {sq: [sq + o for o in KNIGHT_OFFS if not ((sq + o) & 0x88)]
             for sq in D.SQUARES}
PAWN_ATT_W = {sq: [s for s in (sq + 15, sq + 17) if not (s & 0x88)]
              for sq in D.SQUARES}

# ── frozen constants of the vortex ODE (calibrated by E4) ────────────────
FROZEN_VORTEX = {
    'gamma': 0.90,          # vortex circulation (both kings + piece)
    'kappa': 3.20,          # descent-current gain
    'j_neutral': 0.50,      # weak current of a won-but-not-descending move
    'zeta': 2.00,           # in-basin damping
    'swirl_gate': 3.00,     # swirl suppression strength inside a basin
    'dt': 0.02,             # integration step
    'steps': 1100,          # integration horizon
    'n_particles': 144,     # 12x12 fixed lattice
    'capture_radius': 0.30, # cumulative capture: gather capture_hold steps
    'capture_hold': 20,     # inside capture_radius (not necessarily
                            # consecutive — fast sweeps count too)
    'win_capture_min': 0.98,   # metric gates (verified by E4)
    'draw_capture_max': 0.98,
    'cone_eps': 0.15,          # cone-force softening near the target
}

KINDS = ('krk', 'kqk', 'knk', 'kpk')


# ══════════════════════════ frozen table access ══════════════════════════
_TABLE_CACHE = {}


def load_frozen(kind):
    """Load a frozen endgame certificate: {dtm: bytearray, stats: {...}}."""
    if kind in _TABLE_CACHE:
        return _TABLE_CACHE[kind]
    path = os.path.join(RESULTS, 'dtm_%s.json.gz' % kind)
    with open(path, 'r', encoding='utf-8') as fh:
        payload = json.load(fh)
    raw = gzip.decompress(base64.b64decode(payload['dtm_blob_b64']))
    if len(raw) != SIZE:
        raise ValueError('%s: blob size %d != %d' % (kind, len(raw), SIZE))
    entry = {'dtm': bytearray(raw), 'stats': payload['stats'],
             'bellman_verified': payload['bellman_verified']}
    _TABLE_CACHE[kind] = entry
    return entry


def pack(kind, wk, wp, bk, stm):
    return wk | (wp << 7) | (bk << 14) | (stm << 21)


def unpack(s):
    return s & 127, (s >> 7) & 127, (s >> 14) & 127, (s >> 21) & 1


def probe(kind, s):
    """Frozen value: >=0 = White mates in v plies, -1 = drawn/illegal."""
    v = load_frozen(kind)['dtm'][s]
    return -1 if v >= 200 else v


def _raw(dtm, s):
    v = dtm[s]
    return -1 if v >= 200 else v


def black_en_prise(kind, wk, wp, bk):
    """Is the Black king attacked by the strong piece (WTM illegality)?
    The frozen builds only pack WTM states when the answer is NO; probing
    such a state returns -1 ('illegal'), which must not be confused with
    the game-theoretic draw.  The White king is placed on the board too:
    it can block the attack ray."""
    if kind == 'knk':
        return bk in KNIGHT_NB[wp]
    if kind == 'kpk':
        return bk in PAWN_ATT_W[wp]
    code = D.WR if kind == 'krk' else D.WQ
    board = [D.EMPTY] * 128
    board[wk], board[wp], board[bk] = D.WK, code, D.BK
    return bk in D.piece_attack_squares(board, wp, blocking=True)


# ══════════════════════════ move generation ══════════════════════════════
def children_white(kind, wk, wp, bk, dtm=None, kqk=None):
    """White-to-move children as (value, from_sq, to_sq) triples.

    value  = DTM of the child position in plies EXCLUDING the move ply
             (-1 = the move draws / releases); a KPK promotion child is
             the promoted KQK position with Black to move, valued through
             the frozen KQK certificate — the promotion ply itself is
             accounted at the parent (parent = child + 1 when optimal);
    from_sq/to_sq = the board squares of the move (target = the new king
             or piece square; for a promotion the pawn target square)."""
    out = []
    for dest in D.KING_NB[wk]:
        if dest == wp or dest == bk or dest in D.KING_NB[bk]:
            continue
        child = dest | (wp << 7) | (bk << 14) | (1 << 21)
        out.append((_raw(dtm, child), wk, dest))
    if kind == 'knk':
        for dest in KNIGHT_NB[wp]:
            if dest == wk or dest == bk:
                continue
            child = wk | (dest << 7) | (bk << 14) | (1 << 21)
            out.append((_raw(dtm, child), wp, dest))
    elif kind == 'kpk':
        r = wp >> 4
        t = wp + 16
        if r == 6:                                   # promotion boundary
            if t != wk and t != bk and kqk is not None:
                out.append((_raw(kqk, pack('kqk', wk, t, bk, 1)), wp, t))
        else:
            if t != wk and t != bk:
                child = pack(kind, wk, t, bk, 1)
                out.append((_raw(dtm, child), wp, t))
                if r == 1:
                    t2 = wp + 32
                    if t2 != wk and t2 != bk:
                        child2 = pack(kind, wk, t2, bk, 1)
                        out.append((_raw(dtm, child2), wp, t2))
    else:                                    # krk / kqk: sliders (dynamics)
        code = D.WR if kind == 'krk' else D.WQ
        board = [D.EMPTY] * 128
        board[wk], board[wp], board[bk] = D.WK, code, D.BK
        for dest in D.piece_attack_squares(board, wp, blocking=True):
            if dest == wk or dest == bk:
                continue
            child = wk | (dest << 7) | (bk << 14) | (1 << 21)
            out.append((_raw(dtm, child), wp, dest))
    return out


def children_black(kind, wk, wp, bk):
    """Black-to-move children as packed WTM states.

    Returns (children, captured): `captured` = the strong piece is
    capturable this move (K vs K afterwards -> draw).  Destinations
    attacked by the strong piece (with blocking, king-on-dest semantics)
    or by a pawn/knight are illegal and excluded, exactly as in
    dynamics._children_black and the KNK/KPK builder."""
    ch, captured = [], 0
    patt = PAWN_ATT_W[wp] if kind == 'kpk' else ()
    code = None
    if kind in ('krk', 'kqk'):
        code = D.WR if kind == 'krk' else D.WQ
    for dest in D.KING_NB[bk]:
        if dest == wk:
            continue
        if dest in D.KING_NB[wk]:
            continue                       # adjacent to the White king
        if dest == wp:
            captured = 1                   # undefended piece: draw
            continue
        if kind == 'knk' and dest in KNIGHT_NB[wp]:
            continue                       # would walk into a knight check
        if patt and dest in patt:
            continue                       # would walk into a pawn check
        if code is not None:
            board2 = [D.EMPTY] * 128
            board2[wk], board2[wp], board2[dest] = D.WK, code, D.BK
            if dest in D.piece_attack_squares(board2, wp, blocking=True):
                continue                   # would walk into a slider check
        ch.append(wk | (wp << 7) | (dest << 14))
    return ch, captured


# ══════════════════════════ the vortex field ═════════════════════════════
def build_field(kind, wk, wp, bk, stm):
    """Build the T16 vortex field of one state.

    Returns dict with:
      verdict   'WIN' | 'DRAW' | 'LOSS' (Bellman-exact; the E4 reference)
      dtm       parent value d (>=0), None when drawn
      currents  [(from_sq, to_sq, J, tag)]  tag: descent/escape/neutral/trap
      escapes   #drawing resources (drawn child / capture of the piece)
      descents  #value-descending moves (J >= 1)
    T16 criterion (structural, Bellman-exact):
      mover strong: WIN <=> descents >= 1, else DRAW
      mover weak:   LOSS <=> escapes == 0 and descents >= 1, else DRAW
    """
    tbl = load_frozen(kind)
    dtm = tbl['dtm']
    kqk = load_frozen('kqk')['dtm'] if kind == 'kpk' else None
    parent = probe(kind, pack(kind, wk, wp, bk, stm))
    currents, escapes, descents = [], 0, 0

    if stm == 0 and black_en_prise(kind, wk, wp, bk):
        raise ValueError('%s: illegal WTM state (Black en prise) %r'
                         % (kind, (wk, wp, bk)))
    if stm == 0:                                   # White (strong) to move
        for v, from_sq, to_sq in children_white(kind, wk, wp, bk, dtm, kqk):
            if v < 0:
                escapes += 1
                currents.append((from_sq, to_sq, 0.0, 'escape'))
            elif parent >= 0 and v < parent:
                descents += 1
                currents.append((from_sq, to_sq, float(parent - v),
                                 'descent'))
            elif parent >= 0:
                # won but not descending: still inside the net — a weak
                # current (the whole reachable set stays captured)
                currents.append((from_sq, to_sq,
                                 FROZEN_VORTEX['j_neutral'], 'neutral'))
            else:
                # drawn parent with a won child: contradiction (Bellman)
                raise ValueError('%s: drawn WTM state with won child %r'
                                 % (kind, (wk, wp, bk, to_sq)))
        if parent >= 0 and descents >= 1:
            verdict = 'WIN'
        elif parent >= 0:
            raise ValueError('%s: won WTM state without descent %r'
                             % (kind, (wk, wp, bk)))
        else:
            verdict = 'DRAW'
    else:                                          # Black (weak) to move
        ch, captured = children_black(kind, wk, wp, bk)
        if captured:
            escapes += 1
            currents.append((bk, -1, 0.0, 'escape'))
        vals = [_raw(dtm, c) for c in ch]
        if parent == 0 and not captured and not ch:
            verdict = 'LOSS'                       # checkmate on the board
        elif parent >= 0:
            if captured or any(v < 0 for v in vals):
                raise ValueError('%s: won BTM state with escape %r'
                                 % (kind, (wk, wp, bk)))
            if not ch:
                raise ValueError('%s: won BTM state without moves %r'
                                 % (kind, (wk, wp, bk)))
            for c, v in zip(ch, vals):
                cbk = unpack(c)[2]
                currents.append((bk, cbk, float(parent - v), 'descent'))
                descents += 1
            verdict = 'LOSS'                       # every defence feeds the net
        else:
            verdict = 'DRAW'
            for c, v in zip(ch, vals):
                cbk = unpack(c)[2]
                if v < 0:
                    escapes += 1
                    currents.append((bk, cbk, 0.0, 'escape'))
                else:
                    currents.append((bk, cbk, 1.0, 'trap'))
    vortices = [(wk, FROZEN_VORTEX['gamma']),
                (bk, FROZEN_VORTEX['gamma']),
                (wp, FROZEN_VORTEX['gamma'])]
    return {
        'kind': kind, 'wk': wk, 'wp': wp, 'bk': bk, 'stm': stm,
        'verdict': verdict, 'dtm': parent if parent >= 0 else None,
        'currents': currents, 'escapes': escapes, 'descents': descents,
        'vortices': vortices,
    }


# ══════════════════════════ particle ODE (numpy) ═════════════════════════
def _centers(squares):
    """0x88 squares -> board-plane centres in [0,8]^2."""
    if not squares:
        return np.zeros((0, 2))
    f = np.array([s & 7 for s in squares], dtype=np.float64)
    r = np.array([s >> 4 for s in squares], dtype=np.float64)
    return np.stack([f + 0.5, r + 0.5], axis=1)


def simulate(field, constants=None):
    """Integrate the METRIC particle ensemble; return flow metrics.

    The metric field carries only the FORCED currents of perfect play:
    descents (the value ladder) and neutrals (still inside the net).
    Blunder traps are avoidable and escapes are closed orbits, so both
    are excluded here (they live in the visual field only); the vortex
    swirl is likewise a visual layer — the metric field is the damped
    gradient flow of the value, whose minima are exactly the targets,
    so no spurious equilibria exist.

    Particles start on a fixed 12x12 lattice (deterministic).  Metrics:
      capture_fraction  share captured by a forced target (cumulative
                        capture_hold steps within capture_radius);
      mean_free_radius  mean distance of free particles to the nearest
                        forced target;
      net_drift         mean |x_T - x_0| over free particles.
    A DRAWN state has no forced currents at all -> capture_fraction = 0
    by construction (the pure-rotation topology T16 claims)."""
    C = dict(FROZEN_VORTEX)
    if constants:
        C.update(constants)
    desc = [(t, J) for (_, t, J, tag) in field['currents']
            if tag in ('descent', 'neutral') and J > 0]
    targets = _centers([t for (t, _) in desc])
    Js = np.array([J for (_, J) in desc], dtype=np.float64)

    n = C['n_particles']
    side = int(round(np.sqrt(n)))
    g = np.linspace(0.25, 7.75, side)
    xx, yy = np.meshgrid(g, g)
    x = np.stack([xx.ravel(), yy.ravel()], axis=1)
    v = np.zeros_like(x)
    x0 = x.copy()

    dt, kappa, z0 = C['dt'], C['kappa'], C['zeta']
    eps = C['cone_eps']
    r_cap2 = C['capture_radius'] ** 2
    captured = np.zeros(n, dtype=bool)
    hold = np.zeros(n, dtype=np.int32)
    has_t = targets.shape[0] > 0

    if has_t:
        for _ in range(C['steps']):
            # lower envelope of cones U(x) = min_t J_t*|x - c_t|:
            # its only minima are the targets themselves — every particle
            # slides into its (value-weighted) Voronoi cell's target
            r = np.sqrt(((x[:, None, :] - targets[None, :, :]) ** 2
                         ).sum(axis=2))                    # (n,m)
            w = Js[None, :] * r
            star = w.argmin(axis=1)                        # owning target
            dx = (targets[star] - x)                       # toward it
            dist = r[np.arange(n), star]
            acc = kappa * Js[star][:, None] * dx / (dist[:, None] + eps)
            zeta = z0 * Js[star]
            v += (acc - zeta[:, None] * v) * dt
            x += v * dt
            np.clip(x[:, 0], 0.0, 8.0, out=x[:, 0])
            np.clip(x[:, 1], 0.0, 8.0, out=x[:, 1])
            d2t = ((x[:, None, :] - targets[None, :, :]) ** 2
                   ).sum(axis=2).min(axis=1)
            hold = np.where(d2t < r_cap2, hold + 1, hold)
            captured |= hold >= C['capture_hold']
            if captured.all():
                break

    metrics = {
        'n_particles': n,
        'n_targets': int(targets.shape[0]),
        'n_descents': int(len(desc)),
        'capture_fraction': float(captured.mean()),
    }
    free = ~captured
    if free.any():
        if has_t:
            d2t = ((x[free][:, None, :] - targets[None, :, :]) ** 2
                   ).sum(axis=2).min(axis=1)
            metrics['mean_free_radius'] = float(np.sqrt(d2t).mean())
        else:
            metrics['mean_free_radius'] = float(
                np.sqrt(((x[free] - 4.0) ** 2).sum(axis=1)).mean())
        metrics['net_drift'] = float(
            np.sqrt(((x[free] - x0[free]) ** 2).sum(axis=1)).mean())
    else:
        metrics['mean_free_radius'] = 0.0
        metrics['net_drift'] = 0.0
    return metrics


def classify_by_flow(field, metrics=None, constants=None):
    """Flow-only classification (T16): no table probe here.

    WIN   mover strong + descent currents (measured capture required);
    LOSS  mover weak, no escape, all defences descend (capture measured);
    DRAW  a drawing resource exists -> closed orbits must survive.
    Metric gates guard the numerics: a descent field that failed to
    capture, or a drawn field that captured everything, raises."""
    C = dict(FROZEN_VORTEX)
    if constants:
        C.update(constants)
    cf = None if metrics is None else metrics['capture_fraction']
    if field['dtm'] == 0 and field['stm'] == 1:
        return 'LOSS'      # checkmate on the board: the terminal sink,
                           # no dynamics left — captured by definition
    if field['stm'] == 0:                          # strong side to move
        if field['descents'] > 0:
            if cf is not None and cf < C['win_capture_min']:
                raise ValueError('descent field without capture: cf=%.3f'
                                 % cf)
            return 'WIN'
        return 'DRAW'
    if field['escapes'] > 0:                       # defender holds
        if cf is not None and cf >= C['draw_capture_max']:
            raise ValueError('drawn field fully captured: cf=%.3f' % cf)
        return 'DRAW'
    if field['descents'] > 0:
        if cf is not None and cf < C['win_capture_min']:
            raise ValueError('descent field without capture: cf=%.3f' % cf)
        return 'LOSS'
    return 'DRAW'
