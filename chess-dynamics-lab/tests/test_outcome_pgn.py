#!/usr/bin/env python3
"""tests/test_outcome_pgn.py — the zero-dependency PGN layer (E12).

Covers: header parsing, tokenization (comments / variations / NAGs /
move numbers), SAN parsing (castling, e.p., promotion, disambiguation),
the SAN writer round-trip, the bundled corpus replay, result helpers
and the result/board consistency check.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

import dynamics as D
from outcome import pgn as P

DATA_GAMES = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'data', 'games')


# ── headers & tokenizer ──────────────────────────────────────────────────
def test_parse_headers_basic_and_escapes():
    text = '[Event "Test \\"quoted\\" open"]\n[Result "1-0"]\n'
    hdr = P.parse_headers(text.splitlines())
    assert hdr['Result'] == '1-0'
    assert hdr['Event'] == 'Test "quoted" open'


def test_read_pgn_multi_game():
    text = (
        '[Event "A"]\n[Result "1-0"]\n\n1. e4 e5 2. Nf3 1-0\n\n'
        '[Event "B"]\n[Result "*"]\n\n1. d4 *\n')
    games = P.read_pgn(text)
    assert len(games) == 2
    assert games[0].headers['Event'] == 'A'
    assert games[0].sans == ['e4', 'e5', 'Nf3']
    assert games[1].sans == ['d4']


def test_comments_variations_nags_movenums_stripped():
    text = ('[Result "*"]\n\n1. e4! {the best} (1. d4 d5 (1... Nf6 $3)) '
            '$1 1... e5 ; trailing comment\n2. Nf3 *\n')
    game = P.read_pgn(text)[0]
    assert game.sans == ['e4', 'e5', 'Nf3']


def test_fen_header_start_is_honoured():
    text = ('[SetUp "1"]\n[FEN "8/P7/8/8/8/8/k6K/8 w - - 0 1"]\n\n'
            '1. a8=Q *\n')
    game = P.read_pgn(text)[0]
    assert game.start_fen.startswith('8/P7')
    positions = game.replay()
    assert abs(positions[-1].board[D.name_sq('a8')]) == 5   # a queen


# ── SAN parsing ──────────────────────────────────────────────────────────
def test_san_castling_king_and_queen_side():
    pos = D.start_position()
    pos.make(P.san_to_move(pos, 'e4'))
    pos.make(P.san_to_move(pos, 'e5'))
    m = P.san_to_move(pos, 'Nf3')
    assert D.m_from(m) == D.name_sq('g1')
    # reach a castling position by direct FEN
    pos = D.Position().set_fen('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
    assert D.m_flag(P.san_to_move(pos, 'O-O')) == D.FLAG_CASTLE
    assert D.m_flag(P.san_to_move(pos, 'O-O-O')) == D.FLAG_CASTLE
    pos = D.Position().set_fen('r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
    assert D.m_flag(P.san_to_move(pos, '0-0')) == D.FLAG_CASTLE
    assert D.m_flag(P.san_to_move(pos, '0-0-0')) == D.FLAG_CASTLE


def test_san_en_passant_flag():
    pos = D.Position().set_fen(
        'rnbqkbnr/ppp1pppp/8/8/3pP3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 2')
    m = P.san_to_move(pos, 'dxe3')
    assert D.m_flag(m) == D.FLAG_EP


def test_san_promotions_all_pieces():
    pos = D.Position().set_fen('8/P7/8/8/8/8/k6K/8 w - - 0 1')
    for letter, code in (('Q', 5), ('R', 4), ('B', 3), ('N', 2)):
        m = P.san_to_move(pos, 'a8=%s' % letter)
        assert D.m_promo(m) == code


def test_san_disambiguation_file_rank_square():
    pos = D.Position().set_fen('k7/8/8/8/8/2N1N3/8/K7 w - - 0 1')
    assert D.m_from(P.san_to_move(pos, 'Ncd5')) == D.name_sq('c3')
    assert D.m_from(P.san_to_move(pos, 'Ned5')) == D.name_sq('e3')
    pos = D.Position().set_fen('k7/8/8/4N3/8/8/8/K3N3 w - - 0 1')
    assert D.m_from(P.san_to_move(pos, 'N1f3')) == D.name_sq('e1')
    assert D.m_from(P.san_to_move(pos, 'N5f3')) == D.name_sq('e5')


def test_san_rejects_illegal_and_ambiguous():
    pos = D.start_position()
    with pytest.raises(P.PGNError):
        P.san_to_move(pos, 'Ke2')           # illegal (own pawns / check)
    pos = D.Position().set_fen('k7/8/8/8/8/2N1N3/8/K7 w - - 0 1')
    with pytest.raises(P.PGNError):
        P.san_to_move(pos, 'Nd5')           # ambiguous without a file


def test_san_annotations_and_ep_suffix_tolerated():
    pos = D.Position().set_fen(
        'rnbqkbnr/ppp1pppp/8/8/3pP3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 2')
    m1 = P.san_to_move(pos, 'dxe3!')
    m2 = P.san_to_move(pos, 'dxe3+!?')
    m3 = P.san_to_move(pos, 'dxe3 e.p.')
    assert m1 == m2 == m3


# ── the writer ───────────────────────────────────────────────────────────
def test_san_writer_matches_input_and_suffixes():
    pos = D.Position().set_fen('k7/8/8/8/8/2N1N3/8/K7 w - - 0 1')
    san = P.san_of_move(pos, P.san_to_move(pos, 'Ncd5'))
    assert san == 'Ncd5'
    # check suffix
    pos = D.Position().set_fen('7k/8/8/8/8/8/8/K5R1 w - - 0 1')
    san = P.san_of_move(pos, P.san_to_move(pos, 'Rg8'))
    assert san == 'Rg8+'


def test_write_pgn_round_trip_on_corpus():
    for path in sorted(glob.glob(os.path.join(DATA_GAMES, '*.pgn'))):
        games = P.read_pgn_file(path)
        text = P.write_pgn(games)
        again = P.read_pgn(text)
        assert [g.sans for g in again] == [g.sans for g in games], path
        assert [g.headers.get('Result') for g in again] == \
            [g.headers.get('Result') for g in games]


def test_moves_between_and_terminal_state():
    pos = D.Position().set_fen('6k1/5ppp/8/8/8/8/8/K2R4 w - - 0 1')
    assert P.terminal_state(pos) is None
    san = P.san_of_move(pos, P.san_to_move(pos, 'Rd8'))
    assert san == 'Rd8#'                     # the back-rank mate
    pos.make(P.san_to_move(pos, 'Rd8'))
    assert P.terminal_state(pos) == 'checkmate'
    pos = D.Position().set_fen('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1')
    assert P.terminal_state(pos) == 'stalemate'


# ── the bundled corpus ───────────────────────────────────────────────────
def test_corpus_replays_legally():
    files = sorted(glob.glob(os.path.join(DATA_GAMES, '*.pgn')))
    assert len(files) >= 5                        # 3 classical + walks +
    n_games = 0
    for path in files:
        for game in P.read_pgn_file(path):
            report = P.verify_game(game)
            n_games += 1
            if report['terminal'] == 'checkmate':
                assert report['result_consistent'] is True, path
    assert n_games >= 25                          # the frozen E12 corpus


def test_classical_games_end_in_mate_with_correct_result():
    for name, result in (('reti_tartakower_1910.pgn', '1-0'),
                         ('morphy_brunswick_1858.pgn', '1-0'),
                         ('anderssen_kieseritzky_1851.pgn', '1-0')):
        game = P.read_pgn_file(os.path.join(DATA_GAMES, name))[0]
        report = P.verify_game(game)
        assert report['terminal'] == 'checkmate'
        assert game.result == result
        assert report['result_consistent'] is True


def test_result_helpers():
    assert P.result_cls('1-0') == 2
    assert P.result_cls('0-1') == 0
    assert P.result_cls('1/2-1/2') == 1
    assert P.result_cls('*') is None
