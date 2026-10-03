#!/usr/bin/env python3
"""outcome/impact.py — the Move Impact module (the counterfactual surface).

Plan section §16 asked for a *dedicated* instrument that answers, for
every legal move of a position, the counterfactual question:

    "if I play this, what happens to the Outcome Field?"

v1.5.0 answered it with an ad-hoc list inside outcome_field; v2 promotes
the surface to a first-class module with its own derived quantities:

    d_white_win   ΔP(White wins) across the move (the v1 quantity)
    d_draw        ΔP(Draw) across the move
    entropy_child H(F) of the child field, in bits — how unresolved the
                  position becomes after the move
    dtm_child     the exact DTM of the child, when the child lies in a
                  frozen domain (None otherwise)
    pace          dtm_parent − dtm_child on won lines: plies gained or
                  squandered against best defence (the tempo economics
                  of the endgame)
    category      'field_flip'  |ΔP(W)| ≥ 0.5 — the outcome class flips
                  'swing'       |ΔP(W)| ≥ 0.15 — a large, honest swing
                  'quiet'       everything else

Aggregate quantities (the scientific payload):

    robustness_index   share of legal moves that preserve the parent's
                       outcome class — 1.0 = the decision is stable under
                       any single move, 0.0 = every move loses the class
    best_move_agreement  on exact won parents: does the argmax ΔP(W)
                       move coincide with the argmin child DTM move?
                       (a cross-check of the surface against the oracle)
    quiet_share        share of quiet moves (decision fatigue indicator)

The module never mutates the position it is given and never reads the
tables through anything but the OutcomeField passed in — the exact-first
hierarchy of the program is preserved by construction.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402

FLIP_THRESHOLD = 0.5
SWING_THRESHOLD = 0.15


def entropy_bits(probs):
    """Shannon entropy of the outcome field, in bits.

    Lives here (the field-utility module) so that outcome_field and
    impact can share it without a circular import."""
    h = 0.0
    for p in probs:
        if p > 0.0:
            h -= p * math.log2(p)
    return h


def _classify(d_white_win):
    if d_white_win is None:
        return 'unknown'
    a = abs(d_white_win)
    if a >= FLIP_THRESHOLD:
        return 'field_flip'
    if a >= SWING_THRESHOLD:
        return 'swing'
    return 'quiet'


def move_impact_surface(field, pos, max_moves=None):
    """The counterfactual impact surface of every legal move.

    `field` is an OutcomeField (exact-first oracle + model), `pos` a
    dynamics.Position at the root.  Returns a list of row dicts sorted
    by descending |d_white_win| (unknowns last)."""
    parent_probs = None
    parent_dtm = None
    exact = field._exact(pos)
    if exact is not None:
        kind, probe = exact
        if probe['legal']:
            parent_probs = [0.0, 0.0, 0.0]
            parent_probs[T.WHITE_WIN if probe['outcome'] == 'white_win'
                         else T.DRAW] = 1.0
            parent_dtm = probe['dtm_plies']
        else:
            return []                     # illegal root: nothing to compare
    else:
        parent_probs, _ = field._model_probs(pos)
    if parent_probs is None:
        return []                         # no oracle at all for the root

    parent_class = max(range(3), key=lambda k: parent_probs[k])
    p_win = parent_probs[T.WHITE_WIN]
    p_draw = parent_probs[T.DRAW]

    rows = []
    moves = pos.legal_moves()
    if max_moves:
        moves = moves[:max_moves]
    for m in moves:
        undo = pos.make(m)
        child = field._exact(pos)
        if child is not None:
            kind, probe = child
            if probe['legal']:
                cprobs = [0.0, 0.0, 0.0]
                cprobs[T.WHITE_WIN if probe['outcome'] == 'white_win'
                       else T.DRAW] = 1.0
                cdtm = probe['dtm_plies']
            else:
                cprobs, cdtm = None, None
        else:
            cprobs, _ = field._model_probs(pos)
            cdtm = None
        pos.unmake(undo)

        uci = D.move_to_uci(m)
        if cprobs is None:
            rows.append({'uci': uci, 'probs': None, 'd_white_win': None,
                         'd_draw': None, 'entropy_child': None,
                         'dtm_child': None, 'pace': None,
                         'category': 'unknown'})
            continue
        d_w = cprobs[T.WHITE_WIN] - p_win
        d_d = cprobs[T.DRAW] - p_draw
        pace = None
        if parent_dtm is not None and parent_dtm >= 0:
            if cdtm is not None and cdtm >= 0:
                pace = parent_dtm - cdtm
            else:
                pace = None               # won -> drawn: the field flipped
        rows.append({'uci': uci, 'probs': cprobs,
                     'd_white_win': round(d_w, 6),
                     'd_draw': round(d_d, 6),
                     'entropy_child': round(entropy_bits(cprobs), 6),
                     'dtm_child': cdtm, 'pace': pace,
                     'category': _classify(d_w)})

    rows.sort(key=lambda e: (e['d_white_win'] is None,
                             -(e['d_white_win'] if e['d_white_win']
                               is not None else 0.0)))
    return rows


def robustness_index(rows, parent_probs):
    """Share of evaluated moves that preserve the parent outcome class."""
    parent_class = max(range(3), key=lambda k: parent_probs[k])
    ev = [r for r in rows if r['probs'] is not None]
    if not ev:
        return None
    keep = sum(1 for r in ev
               if max(range(3), key=lambda k: r['probs'][k]) == parent_class)
    return round(keep / len(ev), 6)


def best_move_agreement(rows, parent_dtm):
    """On exact won parents: argmax ΔP(W) == argmin child DTM?

    Honest degeneracy rule: on a won parent every move keeps P(W)=1, so
    all ΔW are 0 and the argmax is meaningless — the metric returns None
    instead of a coin flip.  The pace column carries the signal there."""
    if parent_dtm is None or parent_dtm < 0:
        return None
    ev = [r for r in rows if r['probs'] is not None]
    if not ev:
        return None
    if max(abs(r['d_white_win']) for r in ev) < 1e-12:
        return None
    by_field = max(ev, key=lambda r: r['d_white_win'])
    with_dtm = [r for r in ev if r['dtm_child'] is not None]
    if not with_dtm:
        return None
    by_dtm = min(with_dtm, key=lambda r: r['dtm_child'])
    return by_field['uci'] == by_dtm['uci']


def summarize(rows, parent_probs, parent_dtm=None):
    """The aggregate impact block for one position (JSON-ready)."""
    ev = [r for r in rows if r['probs'] is not None]
    cats = {}
    paces = [r['pace'] for r in ev if r['pace'] is not None]
    for r in ev:
        cats[r['category']] = cats.get(r['category'], 0) + 1
    return {
        'n_moves': len(rows),
        'evaluated': len(ev),
        'categories': cats,
        'quiet_share': round(cats.get('quiet', 0) / len(ev), 6) if ev else None,
        'robustness_index': robustness_index(rows, parent_probs),
        'best_move_agreement': best_move_agreement(rows, parent_dtm),
        'max_pace': max(paces) if paces else None,
        'optimal_pace_moves': sum(1 for p in paces if p == 1),
    }


def ascii_table(rows, limit=12):
    """The MOVE IMPACT panel: one line per move, |ΔW| descending."""
    lines = []
    for r in rows[:limit]:
        if r['probs'] is None:
            lines.append('   %-6s  (no oracle for the child position)'
                         % r['uci'])
            continue
        d = r['d_white_win']
        pace = ''
        if r['pace'] is not None and r['pace'] != 0:
            pace = '  pace %+d' % r['pace']
        mark = ''
        if r['category'] == 'field_flip':
            mark = '   <-- FIELD FLIP'
        elif r['category'] == 'swing':
            mark = '   <-- swing'
        lines.append('   %-6s  W %.3f  D %.3f  L %.3f   ΔW %+.3f  '
                     'H %.2f%s%s'
                     % (r['uci'], r['probs'][T.WHITE_WIN],
                        r['probs'][T.DRAW], r['probs'][T.BLACK_WIN],
                        d, r['entropy_child'], pace, mark))
    if len(rows) > limit:
        lines.append('   ... %d more moves' % (len(rows) - limit))
    return lines
