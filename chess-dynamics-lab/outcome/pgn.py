#!/usr/bin/env python3
"""outcome/pgn.py — zero-dependency PGN ingestion (Epoch IV, real games).

Epoch IV (the player-context layer) was designed on synthetic priors;
this module connects it to REAL games.  A PGN file carries three things
the laboratory needs:

    headers   Event/Site/Date/White/Black/Result and — for the context
              layer — WhiteElo/BlackElo (and TimeControl);
    movetext  Standard Algebraic Notation (SAN) with move numbers,
              comments {...}, variations (...), NAGs $n;
    result    1-0 / 0-1 / 1/2-1/2 / *  (the ground truth to audit).

Everything is replayed through the ``dynamics`` legality machinery —
the same move generator the C1-C9 protocol certifies — so a game either
replays legally ply by ply or the module raises ``PGNError`` with the
offending ply.  There is no dependency, no regex beyond ``str`` methods,
and no silent recovery: a corrupt score is an error, not a shrug.

The writer side (``san_of_move`` with its disambiguation logic and
``write_pgn``) lets the laboratory EXPORT games too — the E12 corpus
mixes human classics with laboratory-generated games, and every export
round-trips through the reader in the tests.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402

START_FEN = D.START_FEN

# piece letter -> absolute code (SAN)
SAN_PIECE = {'K': 6, 'Q': 5, 'R': 4, 'B': 3, 'N': 2, 'P': 1}
PIECE_SAN = {v: k for k, v in SAN_PIECE.items()}

RESULTS = ('1-0', '0-1', '1/2-1/2', '*')

MOVE_RESULT_TOKENS = {'1-0', '0-1', '1/2-1/2', '*'}


class PGNError(ValueError):
    """A PGN score the legality machinery cannot replay."""


class Game:
    """One replayable game: headers, start FEN, SAN plies, parsed moves."""

    def __init__(self, headers=None, start_fen=START_FEN, sans=None):
        self.headers = dict(headers or {})
        self.start_fen = start_fen
        self.sans = list(sans or [])
        self.moves = []              # filled by replay()

    @property
    def result(self):
        return self.headers.get('Result', '*')

    def result_cls(self):
        """Result header -> outcome class (None for '*' / unknown)."""
        return result_cls(self.result)

    def replay(self):
        """Replay to the end; returns [pos_0, pos_1, ..., pos_n] (pos_k is
        the position AFTER k plies).  Fills self.moves."""
        pos = D.Position().set_fen(self.start_fen)
        positions = [pos]
        moves = []
        for i, san in enumerate(self.sans):
            m = san_to_move(pos, san)
            moves.append(m)
            pos.make(m)
            positions.append(pos)
        self.moves = moves
        return positions

    def to_json(self):
        return {'headers': self.headers, 'start_fen': self.start_fen,
                'sans': self.sans}


# ── the reader ───────────────────────────────────────────────────────────
def _strip_movetext(text):
    """Comments, rest-of-line comments, nested variations, NAGs."""
    out = []
    depth = 0                                   # variation nesting
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if depth == 0 and c == '{':             # comment to the next '}'
            j = text.find('}', i + 1)
            if j < 0:
                break                           # unterminated: stop eating
            i = j + 1
            out.append(' ')
            continue
        if depth == 0 and c == ';':             # rest-of-line comment
            j = text.find('\n', i)
            i = n if j < 0 else j
            continue
        if c == '(':                            # variation (nestable)
            depth += 1
            i += 1
            continue
        if c == ')':
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth > 0:
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def _clean_san(token):
    """Strip move numbers already split off, annotations and e.p. marks."""
    t = token
    while t and t[-1] in '!?':
        t = t[:-1]
    if t.endswith(' e.p.') or t.endswith('e.p.'):
        t = t[:-5] if t.endswith(' e.p.') else t[:-4]
    elif t.endswith(' ep') or t.endswith('ep'):
        t = t[:-3] if t.endswith(' ep') else t[:-2]
    return t.strip()


def _tokenize(movetext):
    for raw in movetext.split():
        token = raw.strip()
        if not token:
            continue
        if token[0] == '$':                     # NAG annotation
            continue
        if token in ('e.p.', 'ep'):             # stray en-passant marks
            continue
        if token in MOVE_RESULT_TOKENS:
            yield token
            continue
        # move numbers: '1.' '23...' '1.Nf3' fused forms
        while token and token[0].isdigit():
            j = 0
            while j < len(token) and (token[j].isdigit() or token[j] == '.'):
                j += 1
            token = token[j:]
        if not token:
            continue
        if token in MOVE_RESULT_TOKENS:
            yield token
            continue
        token = _clean_san(token)
        if token:
            yield token


def parse_headers(lines):
    """[Key "Value"] lines -> dict (values unescaped)."""
    headers = {}
    for line in lines:
        s = line.strip()
        if not (s.startswith('[') and s.endswith(']')):
            continue
        body = s[1:-1].strip()
        if ' ' not in body:
            continue
        key, _, rest = body.partition(' ')
        rest = rest.strip()
        if len(rest) >= 2 and rest.startswith('"') and rest.endswith('"'):
            value = rest[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        else:
            value = rest
        headers[key] = value
    return headers


def read_pgn(text):
    """PGN text -> [Game].  Multi-game files are supported; each game's
    movetext is split from the next header block automatically."""
    games = []
    headers = {}
    header_lines, move_lines = [], []
    in_moves = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('['):
            if in_moves:                        # next game begins
                games.append(_finish_game(headers, header_lines, move_lines))
                headers, header_lines, move_lines = {}, [], []
                in_moves = False
            header_lines.append(s)
        elif s:
            in_moves = True
            move_lines.append(s)
    if header_lines or move_lines:
        games.append(_finish_game(headers, header_lines, move_lines))
    return games


def _finish_game(headers, header_lines, move_lines):
    hdr = parse_headers(header_lines)
    hdr.update(headers)
    start_fen = hdr.get('FEN') or START_FEN
    stripped = _strip_movetext('\n'.join(move_lines))
    sans, result = [], None
    for tok in _tokenize(stripped):
        if tok in MOVE_RESULT_TOKENS:
            result = tok
            break
        sans.append(tok)
    game = Game(hdr, start_fen, sans)
    if result:
        game.headers.setdefault('Result', result)
    return game


def read_pgn_file(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return read_pgn(fh.read())


# ── SAN -> move ──────────────────────────────────────────────────────────
def san_to_move(pos, san):
    """Standard Algebraic Notation -> the unique legal move, or PGNError."""
    t = san.strip()
    while t and t[-1] in '!?+#':
        t = t[:-1]
    if t.endswith(' e.p.') or t.endswith('e.p.'):
        t = t[:-5] if t.endswith(' e.p.') else t[:-4]
    elif t.endswith(' ep') or t.endswith('ep'):
        t = t[:-3] if t.endswith(' ep') else t[:-2]
    t = t.strip()
    if not t:
        raise PGNError('empty SAN %r' % (san,))
    if t in ('O-O', '0-0', 'OO'):
        return _castle(pos, 'king')
    if t in ('O-O-O', '0-0-0', 'OOO'):
        return _castle(pos, 'queen')
    # grammar: ([KQRBN])?([a-h])?([1-8])?(x)?([a-h][1-8])(=?([QRBN]))?
    piece, from_file, from_rank, is_capture, dest, promo = \
        _parse_san_shape(t)
    candidates = []
    for m in pos.legal_moves():
        fr, to = D.m_from(m), D.m_to(m)
        pr = D.m_promo(m)
        if to != dest:
            continue
        code = abs(pos.board[fr])
        if code == 1:                           # pawn
            if piece is not None and piece != 1:
                continue
            if is_capture and from_file is None:
                continue                        # pawn captures name the file
            if from_file is not None and (fr & 7) != from_file:
                continue
            if from_rank is not None and (fr >> 4) != from_rank:
                continue
            if pr and promo is not None and pr != promo:
                continue
            if pr and promo is None:
                continue                        # promotion must be named
            if not pr and promo is not None:
                continue
            candidates.append(m)
        else:
            if piece is None or code != piece:
                continue
            if from_file is not None and (fr & 7) != from_file:
                continue
            if from_rank is not None and (fr >> 4) != from_rank:
                continue
            candidates.append(m)
    if not candidates:
        raise PGNError('illegal or unmatched SAN %r (%s to move, FEN %s)'
                       % (san, 'White' if pos.side == 1 else 'Black',
                          pos.to_fen()))
    if len(candidates) > 1:
        raise PGNError('ambiguous SAN %r matches %d legal moves (%s)'
                       % (san, len(candidates), pos.to_fen()))
    return candidates[0]


def _castle(pos, side):
    king = D.WK if pos.side == 1 else D.BK
    for m in pos.legal_moves():
        if D.m_flag(m) == D.FLAG_CASTLE and pos.board[D.m_from(m)] == king:
            to_file = D.m_to(m) & 7
            if (side == 'king' and to_file == 6) or \
               (side == 'queen' and to_file == 2):
                return m
    raise PGNError('illegal castling %r (FEN %s)'
                   % ('O-O' if side == 'king' else 'O-O-O', pos.to_fen()))


def _parse_san_shape(t):
    """SAN token (annotations already stripped) ->
    (piece, from_file, from_rank, is_capture, dest, promo).

    Parsed from the END: promotion suffix, destination square, 'x',
    optional one-character disambiguation (a file or a rank), optional
    piece letter, and the rare full-square disambiguation ('Qh4e1')."""
    orig = t
    promo = None
    if len(t) >= 2 and t[-1] in 'QRBN' and \
            (t[-2] == '=' or t[-2] in '12345678'):
        promo = SAN_PIECE[t[-1]]
        t = t[:-1]
        if t.endswith('='):
            t = t[:-1]
    if len(t) < 2 or t[-2] not in 'abcdefgh' or t[-1] not in '12345678':
        raise PGNError('cannot parse SAN %r' % (orig,))
    dest = D.name_sq(t[-2:])
    t = t[:-2]
    is_capture = t.endswith('x')
    if is_capture:
        t = t[:-1]
    from_file = from_rank = None
    # the rare full-square disambiguation comes before the single one
    if len(t) >= 3 and t[0] in 'KQRBN' and t[-2] in 'abcdefgh' \
            and t[-1] in '12345678':
        from_file = ord(t[-2]) - ord('a')
        from_rank = int(t[-1]) - 1
        t = t[:-2]
    elif t and t[-1] in 'abcdefgh':
        from_file = ord(t[-1]) - ord('a')
        t = t[:-1]
    elif t and t[-1] in '12345678':
        from_rank = int(t[-1]) - 1
        t = t[:-1]
    piece = None
    if t and t[0] in 'KQRBN':
        piece = SAN_PIECE[t[0]]
        t = t[1:]
    if t:
        raise PGNError('cannot parse SAN %r' % (orig,))
    if piece is None and from_rank is not None and from_file is None:
        raise PGNError('pawn move with a rank disambiguation %r' % (orig,))
    return piece, from_file, from_rank, is_capture, dest, promo


# ── move -> SAN (the writer side) ────────────────────────────────────────
def san_of_move(pos, m):
    """The canonical SAN of a legal move in `pos` (with +/# suffix)."""
    fr, to = D.m_from(m), D.m_to(m)
    flag = D.m_flag(m)
    piece = pos.board[fr]
    code = abs(piece)
    captured = pos.board[to] != D.EMPTY or flag == D.FLAG_EP
    if flag == D.FLAG_CASTLE:
        core = 'O-O' if (to & 7) == 6 else 'O-O-O'
    elif code == 1:
        core = ''
        if captured:
            core += 'abcdefgh'[fr & 7] + 'x'
        core += D.sq_name(to)
        if D.m_promo(m):
            core += '=' + PIECE_SAN[D.m_promo(m)]
    else:
        core = PIECE_SAN[code]
        others = [o for o in pos.legal_moves()
                  if o != m and abs(pos.board[D.m_from(o)]) == code
                  and D.m_to(o) == to]
        if others:
            same_file = any((D.m_from(o) & 7) == (fr & 7) for o in others)
            same_rank = any((D.m_from(o) >> 4) == (fr >> 4) for o in others)
            if not same_file:
                core += 'abcdefgh'[fr & 7]
            elif not same_rank:
                core += str((fr >> 4) + 1)
            else:
                core += D.sq_name(fr)
        if captured:
            core += 'x'
        core += D.sq_name(to)
    undo = pos.make(m)
    if pos.in_check():
        core += '#' if not pos.legal_moves() else '+'
    pos.unmake(undo)
    return core


# ── the writer ───────────────────────────────────────────────────────────
HEADER_ORDER = ('Event', 'Site', 'Date', 'Round', 'White', 'Black',
                'Result', 'WhiteElo', 'BlackElo', 'TimeControl',
                'SetUp', 'FEN', 'Source')


def write_pgn(games, wrap=78):
    """[Game] -> PGN text (wrapped movetext, canonical header order)."""
    out = []
    for game in games:
        keys = [k for k in HEADER_ORDER if k in game.headers]
        keys += [k for k in sorted(game.headers) if k not in HEADER_ORDER]
        for k in keys:
            v = str(game.headers[k]).replace('\\', '\\\\').replace('"', '\\"')
            out.append('[%s "%s"]' % (k, v))
        pos = D.Position().set_fen(game.start_fen)
        tokens = []
        num = pos.fullmove
        for san in game.sans:
            if pos.side == 1:
                tokens.append('%d.' % num)
            tokens.append(san)
            pos.make(san_to_move(pos, san))
            if pos.side == 1:
                num += 1
        if game.headers.get('Result'):
            tokens.append(game.headers['Result'])
        line, length = [], 0
        for tok in tokens:
            add = len(tok) + (1 if line else 0)
            if line and length + add > wrap:
                out.append(' '.join(line))
                line, length = [tok], len(tok)
            else:
                line.append(tok)
                length += add
        if line:
            out.append(' '.join(line))
        out.append('')
    return '\n'.join(out) + '\n'


def game_from_sans(start_fen, sans, headers=None):
    """Build a Game and validate it by full replay (raises PGNError)."""
    game = Game(headers or {}, start_fen, sans)
    game.replay()
    return game


def moves_between(fens):
    """Consecutive FENs -> SAN list: the unique legal move joining each
    pair (used to freeze laboratory walks into PGN form)."""
    sans = []
    for a, b in zip(fens, fens[1:]):
        pa = D.Position().set_fen(a)
        found = None
        for m in pa.legal_moves():
            undo = pa.make(m)
            ok = pa.to_fen() == b
            pa.unmake(undo)
            if ok:
                if found is not None:
                    raise PGNError('two legal moves join %s -> %s' % (a, b))
                found = m
        if found is None:
            raise PGNError('no legal move joins %s -> %s' % (a, b))
        sans.append(san_of_move(D.Position().set_fen(a), found))
    return sans


# ── result helpers ───────────────────────────────────────────────────────
def result_cls(result):
    """'1-0' -> WHITE_WIN, '0-1' -> BLACK_WIN, '1/2-1/2' -> DRAW, else None."""
    return {'1-0': T.WHITE_WIN, '0-1': T.BLACK_WIN,
            '1/2-1/2': T.DRAW}.get(result)


def terminal_state(pos):
    """'checkmate' | 'stalemate' | None (the game is still open)."""
    if pos.legal_moves():
        return None
    return 'checkmate' if pos.in_check() else 'stalemate'


def verify_game(game):
    """Full replay + result consistency.  Returns a report dict."""
    positions = game.replay()
    final = positions[-1]
    term = terminal_state(final)
    cls = game.result_cls()
    consistent = None
    if term == 'checkmate' and cls is not None:
        winner = T.WHITE_WIN if final.side == -1 else T.BLACK_WIN
        consistent = (winner == cls)
    elif term == 'stalemate' and cls is not None:
        consistent = (cls == T.DRAW)
    return {'plies': len(game.sans),
            'final_fen': final.to_fen(),
            'terminal': term,
            'result_cls': cls,
            'result_consistent': consistent}
