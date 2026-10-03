#!/usr/bin/env python3
"""outcome/features.py — the phase-space feature extractor (Epoch II, v2).

Maps a chess position to a point in a fixed-length phase space
(Chess Phase Space).  Every feature is a deterministic, tablebase-
independent measurement built from the three particle layers of
``dynamics.py``:

    material    M(w), M(b), per-type censuses              (scalar layer)
    mobility    legal-move kinetic terms m(w), m(b)        (layer TORUS)
    threat      Theta(c) field masses, peaks, coverage,    (layer K3)
                king-zone pressure, field overlap
    king        geometric king distances / centralization  (board algebra)
    pawn        pawn structure: doubled / isolated /       (board algebra)
                passed / promotion geometry
    geometry    strongest-piece distances to both kings,   (board algebra)
                edge / centrality of the attacker
    flow        Lagrangian energy, clocks, side to move,   (layer KLEIN)
                capture availability

SPEC v2 is APPEND-ONLY: the first 40 coordinates are byte-for-byte the
v1 list (frozen in the E6 certificate), and v2 appends 27 more.  Old
CSV exports and v1 model files therefore remain loadable, while the
ablation study of the new epoch can test whether the added families
(pawn structure, endgame geometry, field higher moments) carry outcome
information that the original 40 coordinates missed.

Two honesty rules are enforced by construction:

1.  No feature reads any frozen tablebase value, so a model trained on
    these features cannot leak the label it is supposed to predict —
    the distillation benchmark stays meaningful.
2.  Every feature is symmetric in definition (White/Black) and the
    extraction is invariant to FEN round-tripping; the tests pin both
    properties.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402

FEATURE_SPEC = 'phase-space v2 — 67 coordinates (v1: 40, append-only)'

FEATURE_NAMES = [
    # ── v1 block (frozen, do not reorder) ────────────────────────────────
    # material (scalar layer)
    'material_balance', 'material_white', 'material_black',
    'pawns_white', 'pawns_black',
    'knights_white', 'knights_black',
    'bishops_white', 'bishops_black',
    'rooks_white', 'rooks_black',
    'queens_white', 'queens_black',
    'bishop_pair_white', 'bishop_pair_black',
    # mobility (kinetic term, layer TORUS)
    'mobility_white', 'mobility_black', 'mobility_balance',
    # threat field (layer K3)
    'threat_mass_white', 'threat_mass_black', 'threat_mass_balance',
    'king_zone_pressure_white', 'king_zone_pressure_black',
    'king_zone_pressure_balance',
    'hanging_white', 'hanging_black',
    # king geometry
    'king_dist_chebyshev', 'king_dist_manhattan',
    'edge_dist_white', 'edge_dist_black',
    'center_dist_white', 'center_dist_black',
    'in_check_white', 'in_check_black',
    # flow / phase (layers TORUS + KLEIN)
    'energy', 'side_to_move', 'piece_count_total',
    'halfmove_clock', 'castling_any', 'en_passant_any',
    # ── v2 block (append-only additions) ─────────────────────────────────
    # pawn structure
    'pawns_doubled_white', 'pawns_doubled_black',
    'pawns_isolated_white', 'pawns_isolated_black',
    'passed_pawns_white', 'passed_pawns_black',
    'promotion_dist_min_white', 'promotion_dist_min_black',
    'promotion_blocked_white', 'promotion_blocked_black',
    # strongest-piece (endgame) geometry
    'strongest_dist_enemy_king_white', 'strongest_dist_enemy_king_black',
    'strongest_dist_own_king_white', 'strongest_dist_own_king_black',
    'strongest_edge_dist_white', 'strongest_edge_dist_black',
    'strongest_center_dist_white', 'strongest_center_dist_black',
    # threat-field higher moments
    'threat_peak_white', 'threat_peak_black',
    'threat_field_overlap',
    'threat_coverage_white', 'threat_coverage_black',
    # king freedom (geometric mobility of the kings)
    'king_freedom_white', 'king_freedom_black',
    # capture availability (pseudo-legal, field-derived)
    'capture_available_white', 'capture_available_black',
]

FEATURE_GROUPS = {
    'material': ['material_balance', 'material_white', 'material_black',
                 'pawns_white', 'pawns_black', 'knights_white', 'knights_black',
                 'bishops_white', 'bishops_black', 'rooks_white', 'rooks_black',
                 'queens_white', 'queens_black',
                 'bishop_pair_white', 'bishop_pair_black'],
    'mobility': ['mobility_white', 'mobility_black', 'mobility_balance'],
    'threat':   ['threat_mass_white', 'threat_mass_black', 'threat_mass_balance',
                 'king_zone_pressure_white', 'king_zone_pressure_black',
                 'king_zone_pressure_balance', 'hanging_white', 'hanging_black',
                 'threat_peak_white', 'threat_peak_black',
                 'threat_field_overlap',
                 'threat_coverage_white', 'threat_coverage_black'],
    'king':     ['king_dist_chebyshev', 'king_dist_manhattan',
                 'edge_dist_white', 'edge_dist_black',
                 'center_dist_white', 'center_dist_black',
                 'in_check_white', 'in_check_black',
                 'king_freedom_white', 'king_freedom_black'],
    'pawn':     ['pawns_doubled_white', 'pawns_doubled_black',
                 'pawns_isolated_white', 'pawns_isolated_black',
                 'passed_pawns_white', 'passed_pawns_black',
                 'promotion_dist_min_white', 'promotion_dist_min_black',
                 'promotion_blocked_white', 'promotion_blocked_black'],
    'geometry': ['strongest_dist_enemy_king_white',
                 'strongest_dist_enemy_king_black',
                 'strongest_dist_own_king_white',
                 'strongest_dist_own_king_black',
                 'strongest_edge_dist_white', 'strongest_edge_dist_black',
                 'strongest_center_dist_white', 'strongest_center_dist_black'],
    'flow':     ['energy', 'side_to_move', 'piece_count_total',
                 'halfmove_clock', 'castling_any', 'en_passant_any',
                 'capture_available_white', 'capture_available_black'],
}

# the layer-labelled view used by the ablation report
GROUP_TITLES = {
    'material': 'scalar material layer',
    'mobility': 'kinetic layer (TORUS, mu-term)',
    'threat':   'potential layer (K3 threat fields + higher moments)',
    'king':     'king geometry (board algebra)',
    'pawn':     'pawn structure & promotion geometry',
    'geometry': 'strongest-piece endgame geometry',
    'flow':     'flow / phase layer (KLEIN + Lagrangian)',
}

V2_NAMES = FEATURE_NAMES[40:]          # the v2 append block, in order

_CENTER = tuple(D.name_sq(s) for s in ('d4', 'e4', 'd5', 'e5'))
_KING_DIRS = D.KING_DIRS


def _chebyshev(a, b):
    return max(abs((a & 7) - (b & 7)), abs((a >> 4) - (b >> 4)))


def _manhattan(a, b):
    return abs((a & 7) - (b & 7)) + abs((a >> 4) - (b >> 4))


def _edge_dist(sq):
    f, r = sq & 7, sq >> 4
    return min(f, 7 - f, r, 7 - r)


def _center_dist(sq):
    return min(_chebyshev(sq, c) for c in _CENTER)


def _king_zone(king_sq):
    zone = [king_sq]
    for off in _KING_DIRS:
        s = king_sq + off
        if not (s & 0x88):
            zone.append(s)
    return zone


def _count_types(pos, side):
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    bishops = 0
    for sq in D.SQUARES:
        p = pos.board[sq]
        if p == D.EMPTY or (p > 0) != (side > 0):
            continue
        a = abs(p)
        if a in counts:
            counts[a] += 1
        if a == 3:
            bishops += 1
    return counts, bishops >= 2


def _field_mass(theta):
    return sum(theta[sq] for sq in D.SQUARES)


def _strongest_sq(pos, side):
    """Square of the side's strongest non-king piece (king itself when
    bare — the coordinate then degrades gracefully to a king distance)."""
    best_sq, best_code = None, 0
    for sq in D.SQUARES:
        p = pos.board[sq]
        if p == D.EMPTY or (p > 0) != (side > 0) or abs(p) == 6:
            continue
        if abs(p) > best_code:
            best_code, best_sq = abs(p), sq
    if best_sq is None:
        return pos.king_sq(side)
    return best_sq


def _pawn_structure(pos):
    """(doubled, isolated, passed, promo_dist, blocked) per side.

    All counts are geometric: no move generation, no tablebase."""
    wpawns, bpawns = [], []
    for sq in D.SQUARES:
        p = pos.board[sq]
        if p == D.WP:
            wpawns.append(sq)
        elif p == D.BP:
            bpawns.append(sq)
    out = {}
    for side, pawns in ((1, wpawns), (-1, bpawns)):
        files = {}
        for sq in pawns:
            files.setdefault(sq & 7, []).append(sq)
        doubled = sum(max(0, len(v) - 1) for v in files.values())
        isolated = 0
        for f, v in files.items():
            if not (files.get(f - 1) or files.get(f + 1)):
                isolated += len(v)
        if side == 1:
            enemy = bpawns
            passed = [sq for sq in pawns
                      if not any(abs((e & 7) - (sq & 7)) <= 1 and
                                 (e >> 4) > (sq >> 4)
                                 for e in enemy)]
            promo = 7 - max((sq >> 4) for sq in pawns) if pawns else 7
            blocked = 0
            for sq in pawns:
                f, r = sq & 7, sq >> 4
                path = [16 * rr + f for rr in range(r + 1, 8)]
                if any(pos.board[s] != D.EMPTY for s in path):
                    blocked += 1
        else:
            enemy = wpawns
            passed = [sq for sq in pawns
                      if not any(abs((e & 7) - (sq & 7)) <= 1 and
                                 (e >> 4) < (sq >> 4)
                                 for e in enemy)]
            promo = min((sq >> 4) for sq in pawns) if pawns else 7
            blocked = 0
            for sq in pawns:
                f, r = sq & 7, sq >> 4
                path = [16 * rr + f for rr in range(0, r)]
                if any(pos.board[s] != D.EMPTY for s in path):
                    blocked += 1
        out[side] = (float(doubled), float(isolated), float(len(passed)),
                     float(promo), float(blocked))
    return out


def extract_features(pos):
    """Position -> {feature name: float} (the phase-space point)."""
    b = pos.board

    mw = D.material(pos, 1)
    mb = D.material(pos, -1)
    mob_w = D.mobility(pos, 1)
    mob_b = D.mobility(pos, -1)

    cw, bw_pair = _count_types(pos, 1)
    cb, bb_pair = _count_types(pos, -1)

    theta_w = D.threat_field(pos, 1)
    theta_b = D.threat_field(pos, -1)
    mass_w = _field_mass(theta_w)
    mass_b = _field_mass(theta_b)

    wk = pos.king_sq(1)
    bk = pos.king_sq(-1)
    zone_w = _king_zone(wk)
    zone_b = _king_zone(bk)
    kz_w = sum(theta_b[sq] for sq in zone_w)   # danger to the White king
    kz_b = sum(theta_w[sq] for sq in zone_b)   # danger to the Black king

    hang_w = hang_b = 0
    cap_w = cap_b = 0
    for sq in D.SQUARES:
        p = b[sq]
        if p == D.EMPTY:
            continue
        if p > 0:
            if pos.attacked(sq, -1) and not pos.attacked(sq, 1):
                hang_w += 1
            if theta_w[sq] > 0:
                cap_b = 1                       # a black piece can be captured
        else:
            if pos.attacked(sq, 1) and not pos.attacked(sq, -1):
                hang_b += 1
            if theta_b[sq] > 0:
                cap_w = 1

    # threat-field higher moments (v2)
    peak_w = max(theta_w[s] for s in D.SQUARES)
    peak_b = max(theta_b[s] for s in D.SQUARES)
    overlap = sum(min(theta_w[s], theta_b[s]) for s in D.SQUARES)
    cov_w = sum(1 for s in D.SQUARES if theta_w[s] > 0)
    cov_b = sum(1 for s in D.SQUARES if theta_b[s] > 0)

    # king freedom: neighbour squares on-board, not own-occupied,
    # not attacked by the enemy field (geometric, no legality machinery)
    def _king_freedom(king_sq, own_white, enemy_theta):
        n = 0
        for off in _KING_DIRS:
            s = king_sq + off
            if s & 0x88:
                continue
            if own_white and b[s] > 0:
                continue
            if not own_white and b[s] < 0:
                continue
            if enemy_theta[s] == 0:
                n += 1
        return float(n)

    kf_w = _king_freedom(wk, True, theta_b)
    kf_b = _king_freedom(bk, False, theta_w)

    ps = _pawn_structure(pos)

    sw_sq = _strongest_sq(pos, 1)
    sb_sq = _strongest_sq(pos, -1)

    f = {
        # ── v1 block ─────────────────────────────────────────────────────
        'material_balance': float(mw - mb),
        'material_white': float(mw),
        'material_black': float(mb),
        'pawns_white': float(cw[1]),
        'pawns_black': float(cb[1]),
        'knights_white': float(cw[2]),
        'knights_black': float(cb[2]),
        'bishops_white': float(cw[3]),
        'bishops_black': float(cb[3]),
        'rooks_white': float(cw[4]),
        'rooks_black': float(cb[4]),
        'queens_white': float(cw[5]),
        'queens_black': float(cb[5]),
        'bishop_pair_white': 1.0 if bw_pair else 0.0,
        'bishop_pair_black': 1.0 if bb_pair else 0.0,
        'mobility_white': float(mob_w),
        'mobility_black': float(mob_b),
        'mobility_balance': float(mob_w - mob_b),
        'threat_mass_white': float(mass_w),
        'threat_mass_black': float(mass_b),
        'threat_mass_balance': float(mass_w - mass_b),
        'king_zone_pressure_white': float(kz_w),
        'king_zone_pressure_black': float(kz_b),
        'king_zone_pressure_balance': float(kz_b - kz_w),
        'hanging_white': float(hang_w),
        'hanging_black': float(hang_b),
        'king_dist_chebyshev': float(_chebyshev(wk, bk)),
        'king_dist_manhattan': float(_manhattan(wk, bk)),
        'edge_dist_white': float(_edge_dist(wk)),
        'edge_dist_black': float(_edge_dist(bk)),
        'center_dist_white': float(_center_dist(wk)),
        'center_dist_black': float(_center_dist(bk)),
        'in_check_white': 1.0 if pos.attacked(wk, -1) else 0.0,
        'in_check_black': 1.0 if pos.attacked(bk, 1) else 0.0,
        'energy': float(D.energy(pos, 1)),
        'side_to_move': float(pos.side),
        'piece_count_total': float(sum(cw.values()) + sum(cb.values()) + 2),
        'halfmove_clock': float(pos.halfmove),
        'castling_any': 1.0 if pos.castling else 0.0,
        'en_passant_any': 1.0 if pos.ep >= 0 else 0.0,
        # ── v2 block ─────────────────────────────────────────────────────
        'pawns_doubled_white': ps[1][0],
        'pawns_doubled_black': ps[-1][0],
        'pawns_isolated_white': ps[1][1],
        'pawns_isolated_black': ps[-1][1],
        'passed_pawns_white': ps[1][2],
        'passed_pawns_black': ps[-1][2],
        'promotion_dist_min_white': ps[1][3],
        'promotion_dist_min_black': ps[-1][3],
        'promotion_blocked_white': ps[1][4],
        'promotion_blocked_black': ps[-1][4],
        'strongest_dist_enemy_king_white': float(_chebyshev(sw_sq, bk)),
        'strongest_dist_enemy_king_black': float(_chebyshev(sb_sq, wk)),
        'strongest_dist_own_king_white': float(_chebyshev(sw_sq, wk)),
        'strongest_dist_own_king_black': float(_chebyshev(sb_sq, bk)),
        'strongest_edge_dist_white': float(_edge_dist(sw_sq)),
        'strongest_edge_dist_black': float(_edge_dist(sb_sq)),
        'strongest_center_dist_white': float(_center_dist(sw_sq)),
        'strongest_center_dist_black': float(_center_dist(sb_sq)),
        'threat_peak_white': float(peak_w),
        'threat_peak_black': float(peak_b),
        'threat_field_overlap': float(overlap),
        'threat_coverage_white': float(cov_w),
        'threat_coverage_black': float(cov_b),
        'king_freedom_white': kf_w,
        'king_freedom_black': kf_b,
        'capture_available_white': float(cap_w),
        'capture_available_black': float(cap_b),
    }
    return f


def extract_vector(pos, names=None):
    """Position -> list of floats aligned with FEATURE_NAMES (or `names`)."""
    f = extract_features(pos)
    return [f[n] for n in (names or FEATURE_NAMES)]


def vector_dict(vec, names=None):
    """Inverse helper: aligned vector -> name-keyed dict."""
    return {n: v for n, v in zip(names or FEATURE_NAMES, vec)}
