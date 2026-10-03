#!/usr/bin/env python3
"""outcome/tablebase_api.py — the exact outcome oracle (Epoch I, v2).

A thin, self-contained API over the five frozen retrograde certificates
``results/dtm_{krk,kqk,knk,kpk,kbk}.json.gz``:

    kind   strong side   packed space (22 bits)
    KRK    White R       wk | wp<<7 | bk<<14 | stm<<21
    KQK    White Q       (7-bit 0x88 squares; stm: 0 = White to move,
    KNK    White N        1 = Black to move)
    KPK    White P
    KBK    White B       (v2: the diagonal negative control)

The blob byte semantics: 0..63 = White mates in that many plies against
best defence, 200 = drawn / outside the enumerated space.

This module answers, for any 4/3/2-piece position with White as the strong
side, the game-theoretic question (Task I of the program):

    exact outcome  WIN / DRAW  (+ exact DTM in plies when won)

Legality is reconstructed independently of the blob (the blob cannot
distinguish 'legal draw' from 'never enumerated'): a packed state is legal
iff the kings do not touch, the pieces do not overlap and — when it is
White to move — the black king is not en prise.  Pawn domains restrict the
pawn to ranks 2..7 (the builders' census universe).

Every number returned by this module is either read from the frozen
Bellman-verified certificate or derived from board geometry — nothing is
hardcoded, so a corrupt table is detected by the tests, not assumed away.
"""
import base64
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402

# 'kbk' is APPENDED so that the splitmix64 split indices of the four
# v1 domains (KINDS_INDEX) are preserved bit-for-bit — old datasets and
# frozen models keep their exact train/valid/test membership.
KINDS = ('krk', 'kqk', 'knk', 'kpk', 'kbk')
KIND_PIECE_CHAR = {'krk': 'R', 'kqk': 'Q', 'knk': 'N', 'kpk': 'P',
                   'kbk': 'B'}
KIND_PIECE_CODE = {'krk': D.WR, 'kqk': D.WQ, 'knk': D.WN, 'kpk': D.WP,
                   'kbk': D.WB}

# outcome classes (from White's perspective)
BLACK_WIN, DRAW, WHITE_WIN = 0, 1, 2
CLASS_NAMES = ('black_win', 'draw', 'white_win')

SIZE = 1 << 22
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'results')

_TABLE_CACHE = {}


def _knight_attacks(sq):
    out = []
    for off in D.KNIGHT_OFFS:
        s = sq + off
        if not (s & 0x88):
            out.append(s)
    return out


def _pawn_attacks_white(sq):
    out = []
    for off in (15, 17):
        s = sq + off
        if not (s & 0x88):
            out.append(s)
    return out


def black_en_prise(kind, wk, wp, bk):
    """Is the black king attacked by the strong piece (=> WTM illegal)?

    Mirrors vortex.black_en_prise: the white king is placed on the board
    too because it can block a slider's attack ray."""
    if kind == 'knk':
        return bk in _knight_attacks(wp)
    if kind == 'kpk':
        return bk in _pawn_attacks_white(wp)
    board = [D.EMPTY] * 128
    board[wk], board[wp], board[bk] = D.WK, KIND_PIECE_CODE[kind], D.BK
    return bk in D.piece_attack_squares(board, wp, blocking=True)


def load_table(kind, results_dir=None):
    """Load and cache one frozen certificate: {'dtm': bytearray, 'stats': dict}."""
    if kind in _TABLE_CACHE:
        return _TABLE_CACHE[kind]
    if kind not in KINDS:
        raise ValueError('unknown endgame kind: %r' % (kind,))
    path = os.path.join(results_dir or RESULTS_DIR, 'dtm_%s.json.gz' % kind)
    with open(path, 'r', encoding='utf-8') as fh:
        payload = json.load(fh)
    raw = gzip.decompress(base64.b64decode(payload['dtm_blob_b64']))
    if len(raw) != SIZE:
        raise ValueError('%s: blob size %d != %d' % (kind, len(raw), SIZE))
    entry = {'dtm': bytearray(raw), 'stats': payload['stats'],
             'bellman_verified': payload['bellman_verified'],
             'packing': payload.get('packing', '')}
    _TABLE_CACHE[kind] = entry
    return entry


def pack(kind, wk, wp, bk, stm):
    """22-bit packed state; stm is 0 (White to move) or 1 (Black to move)."""
    return wk | (wp << 7) | (bk << 14) | (stm << 21)


def unpack(state):
    return state & 127, (state >> 7) & 127, (state >> 14) & 127, (state >> 21) & 1


def kings_adjacent(a, b):
    return max(abs((a & 7) - (b & 7)), abs((a >> 4) - (b >> 4))) <= 1


def pawn_rank_ok(wp):
    """The KPK builders enumerate the pawn on ranks 2..7 (0x88 rank 1..6)."""
    return 1 <= (wp >> 4) <= 6


def on_board(sq):
    """0x88 on-board test (7-bit packed squares can hold off-board values)."""
    return not (sq & 0x88)


def is_legal_state(kind, wk, wp, bk, stm):
    """Legality of a packed-space state, reconstructed from geometry."""
    if not (on_board(wk) and on_board(wp) and on_board(bk)):
        return False
    if wk == wp or wk == bk or wp == bk:
        return False
    if kings_adjacent(wk, bk):
        return False
    if kind == 'kpk' and not pawn_rank_ok(wp):
        return False
    if stm == 0 and black_en_prise(kind, wk, wp, bk):
        return False
    return True


def probe_state(kind, wk, wp, bk, stm, results_dir=None):
    """Exact game-theoretic value of one state.

    Returns a dict:
        legal        bool
        outcome      'white_win' | 'draw' | 'illegal'
        cls          WHITE_WIN / DRAW  (BLACK_WIN never occurs in these domains)
        dtm_plies    int >= 0 when White mates, else None
    """
    legal = is_legal_state(kind, wk, wp, bk, stm)
    if not legal:
        return {'legal': False, 'outcome': 'illegal', 'cls': None, 'dtm_plies': None}
    tbl = load_table(kind, results_dir)
    raw = tbl['dtm'][pack(kind, wk, wp, bk, stm)]
    value = -1 if raw >= 200 else raw
    if value >= 0:
        return {'legal': True, 'outcome': 'white_win', 'cls': WHITE_WIN,
                'dtm_plies': value}
    return {'legal': True, 'outcome': 'draw', 'cls': DRAW, 'dtm_plies': None}


def detect_domain(pos):
    """Which frozen domain (if any) does a dynamics.Position belong to?

    A position is inside the program's oracle space iff it holds exactly
    two kings and exactly one additional white piece of kind R/Q/N/P/B.
    (v1.5.0 raised a KeyError on the lone-bishop shape — fixed in v2 by
    the KBK certificate.)"""
    counts = {}
    wk = bk = None
    strong = []
    for sq in D.SQUARES:
        p = pos.board[sq]
        if p == D.EMPTY:
            continue
        a = abs(p)
        counts[a] = counts.get(a, 0) + 1
        if a == 6:
            if p > 0:
                wk = sq
            else:
                bk = sq
        elif p > 0 and a in (1, 2, 3, 4, 5):
            strong.append((a, sq))            # the strong-side white piece
        else:
            return None                       # black non-king material
    if counts.get(6, 0) != 2 or len(strong) != 1:
        return None
    code, sq = strong[0]
    kind = {D.WR: 'krk', D.WQ: 'kqk', D.WN: 'knk', D.WP: 'kpk',
            D.WB: 'kbk'}[code]
    return kind


def classify_fen(fen, results_dir=None):
    """FEN -> exact outcome, when the position lies in a frozen domain.

    Returns {'domain': kind|None, 'legal': ..., 'outcome': ..., 'cls': ...,
             'dtm_plies': ...}.  Positions outside the oracle space get
    domain None and outcome 'unknown' — the caller falls back to the
    statistical layer (Outcome Field)."""
    pos = D.Position().set_fen(fen)
    kind = detect_domain(pos)
    if kind is None:
        return {'domain': None, 'legal': True, 'outcome': 'unknown',
                'cls': None, 'dtm_plies': None}
    wk = pos.king_sq(1)
    bk = pos.king_sq(-1)
    wp = None
    for sq in D.SQUARES:
        p = pos.board[sq]
        if p == KIND_PIECE_CODE[kind]:
            wp = sq
            break
    stm = 0 if pos.side == 1 else 1
    if not is_legal_state(kind, wk, wp, bk, stm):
        return {'domain': kind, 'legal': False, 'outcome': 'illegal',
                'cls': None, 'dtm_plies': None}
    res = probe_state(kind, wk, wp, bk, stm, results_dir)
    res['domain'] = kind
    return res


def state_to_fen(kind, wk, wp, bk, stm):
    """Reconstruct a FEN for a packed-space state (frozen-domain shape)."""
    rows = []
    for rank in range(7, -1, -1):
        row, placed = '', 0
        cells = {}
        if wk >> 4 == rank:
            cells[wk & 7] = 'K'
        if bk >> 4 == rank:
            cells[bk & 7] = 'k'
        if wp >> 4 == rank:
            cells[wp & 7] = KIND_PIECE_CHAR[kind]
        for file in range(8):
            if file in cells:
                if placed:
                    row += str(placed)
                    placed = 0
                row += cells[file]
            else:
                placed += 1
        if placed:
            row += str(placed)
        rows.append(row)
    side = 'w' if stm == 0 else 'b'
    return '%s %s - - 0 1' % ('/'.join(rows), side)


def census_kind(kind, results_dir=None):
    """Live re-count of the legal state population of a domain.

    The builder's frozen stats claim an exact number of realizable states;
    this routine re-derives that number from geometry alone.  A mismatch
    is a bug by definition (the repo convention: fix the code, not the file)."""
    table = load_table(kind, results_dir)
    n_legal = 0
    n_won = 0
    for wk in D.SQUARES:
        for wp in D.SQUARES:
            if wp == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wp:
                    continue
                if kings_adjacent(wk, bk):
                    continue
                if kind == 'kpk' and not pawn_rank_ok(wp):
                    continue
                for stm in (0, 1):
                    if stm == 0 and black_en_prise(kind, wk, wp, bk):
                        continue
                    n_legal += 1
                    raw = table['dtm'][pack(kind, wk, wp, bk, stm)]
                    if raw < 200:
                        n_won += 1
    return {'legal_states': n_legal, 'won_states': n_won}
