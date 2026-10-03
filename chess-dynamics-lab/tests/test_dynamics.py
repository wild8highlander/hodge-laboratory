# tests for the chess-dynamics-lab core (dynamics.py + engine package)

import json
import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import dynamics as D                                     # noqa: E402


# ── board and move generation ────────────────────────────────────────────
def test_start_position_has_20_moves():
    pos = D.start_position()
    assert len(pos.legal_moves()) == 20


@pytest.mark.parametrize("depth,count", [(1, 20), (2, 400), (3, 8902),
                                         (4, 197281)])
def test_perft(depth, count):
    pos = D.start_position()

    def perft(p, d):
        if d == 0:
            return 1
        n = 0
        for m in p.legal_moves():
            u = p.make(m)
            n += perft(p, d - 1)
            p.unmake(u)
        return n
    assert perft(pos, depth) == count


def test_fen_round_trip():
    for fen in (D.START_FEN,
                "kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1",
                "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
                "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
                "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"):
        pos = D.Position().set_fen(fen)
        assert pos.to_fen() == fen, fen


def test_position_validity_rejects_illegal():
    ok, why = D.Position().set_fen("2k5/5ppp/8/8/8/8/5PPP/2R3K1 w - - 0 1").is_valid()
    assert not ok                       # black in check, white to move
    ok, why = D.Position().set_fen(D.START_FEN).is_valid()
    assert ok


def test_zobrist_incremental_and_unmake():
    pos = D.start_position()
    h0 = pos.hash
    for m in list(pos.legal_moves())[:8]:
        u = pos.make(m)
        assert pos.hash == D.zobrist_hash(pos)
        pos.unmake(u)
        assert pos.hash == h0 and pos.to_fen() == D.START_FEN


def test_splitmix64_is_a_bijection():
    for x in (0, 1, 2**64 - 1, 123456789, 0xDEADBEEF):
        assert D.splitmix64_inverse(D.splitmix64(x)) == x


# ── C1 board algebra ─────────────────────────────────────────────────────
def test_orbit_censuses():
    assert len(D.orbits(D.V4)) == 20
    assert len(D.orbits(D.D4)) == 10
    sizes = sorted(set(len(o) for o in D.orbits(D.V4)))
    assert sizes == [2, 4]


def test_colour_preserving_subgroup():
    # V4 elements preserve (f + r) mod 2; the other four do not
    for name, g in D.V4.items():
        for f in range(8):
            for r in range(8):
                assert (g(f, r)[0] + g(f, r)[1]) % 2 == (f + r) % 2


# ── C2/C3 particle kinematics and mobility ───────────────────────────────
@pytest.mark.parametrize("piece,edges", [(4, 448), (3, 280), (2, 168),
                                         (6, 210), (5, 728)])
def test_move_graph_edge_census(piece, edges):
    assert D.piece_graph_directed(piece) == 2 * edges


def test_knight_bipartite_bishop_two_components():
    bip, color = D.is_bipartite(D.empty_board_graph(2))
    assert bip
    comps = D.graph_components(D.empty_board_graph(3))
    assert sorted(len(c) for c in comps) == [32, 32]


def test_mobility_maxima_and_sums():
    mc = D.mobility_census()
    pieces = ('king', 'knight', 'bishop', 'rook', 'queen')
    assert {k: mc[k]['max'] for k in pieces} == {
        'king': 8, 'knight': 8, 'bishop': 13, 'rook': 14, 'queen': 27}
    assert {k: mc[k]['sum'] for k in pieces} == {
        'king': 420, 'knight': 336, 'bishop': 560, 'rook': 896,
        'queen': 1456}
    assert set(mc['queen']['argmax']) == {'d4', 'e4', 'd5', 'e5'}
    assert mc['bishop_closed_form_ok'] and mc['queen_closed_form_ok']


# ── C4 flow ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize("W,H,a,b,t", [(8, 8, 1, 1, 8), (8, 8, 3, 5, 8),
                                       (8, 8, 2, 2, 4), (48, 48, 1, 1, 48),
                                       (24, 36, 3, 5, 72),
                                       (12, 12, 4, 6, 6)])
def test_tstar(W, H, a, b, t):
    assert D.tstar(W, H, a, b) == t
    steps, cells = D.simulate_torus_flow(W, H, a, b)
    assert steps == t and len(cells) == t


def test_billiard_total_path():
    gamma = D.GAMMA_TORUS
    n, path, refl, rest, ratio = D.simulate_billiard(8, 8, 3, 2, gamma)
    assert rest and abs(ratio - 1.0) < 1e-9


# ── C5/C6/C7 ─────────────────────────────────────────────────────────────
def test_energy_values():
    pos = D.start_position()
    assert D.mobility(pos, 1) == 20
    pos.make(D.uci_to_move(pos, "e2e4"))
    assert D.mobility(pos, 1) == 30


def test_threat_field_equivariance_pawnless():
    pos = D.Position().set_fen(D.PAWNLESS_FEN)
    # the engine-level check lives in the protocol; here a single mirror
    ok, det = D._c6_threat_fields()
    assert ok


def test_attack_sum_identity():
    pos = D.start_position()
    f, p = D.attack_sum_identity(pos, 1)
    assert f == p == 38


# ── C8 mate machinery ────────────────────────────────────────────────────
def test_morphy_mate_in_two():
    pos = D.Position().set_fen(D.MATE_MORPHY_FEN)
    plies, pv, nodes = D.mate_search(pos, 4)
    assert plies == 3
    assert D.move_to_uci(pv[0]) == "a1a6"


def test_ladder_mate_in_two():
    pos = D.Position().set_fen(D.MATE_LADDER_FEN)
    plies, pv, _ = D.mate_search(pos, 4)
    assert plies == 3


def test_retro_cache_stats():
    dtm, stats = D.load_dtm_cache(4)
    assert {k: stats[k] for k in D.DTM_EXPECTED['KRK']} == D.DTM_EXPECTED['KRK']
    dtm, stats = D.load_dtm_cache(5)
    assert {k: stats[k] for k in D.DTM_EXPECTED['KQK']} == D.DTM_EXPECTED['KQK']


def test_retro_known_positions():
    dtm_q, _ = D.load_dtm_cache(5)
    b6, c7, c8 = (D.name_sq(s) for s in ('b6', 'c7', 'c8'))
    assert D.dtm_state_of(dtm_q, b6, c7, c8, 1) == 0        # mate on board
    assert D.dtm_state_of(dtm_q, b6, D.name_sq('a7'), c8, 0) == 1


# ── C9 hashing ───────────────────────────────────────────────────────────
def test_protocol_c9():
    ok, det = D._c9_zobrist_incrementality()
    assert ok and det['playout_positions'] > 1000


# ── engine package ───────────────────────────────────────────────────────
def test_engine_modules_import_and_run():
    sys.path.insert(0, os.path.join(ROOT, 'engine'))
    import particles
    import mate_solver
    import analyzer
    import game_player

    layers = particles.ThreeLayerModel().analyze(D.start_position())
    assert layers['K3']['threat_mass']['white'] == 38
    assert layers['torus']['mobility_white'] == 20
    assert layers['klein']['tstar_8x8_king_rook_step'] == 8

    out = mate_solver.solve(D.MATE_MORPHY_FEN, depth=4)
    assert out['mate_in_moves'] == 2

    rep = analyzer.analyze(D.START_FEN)
    assert rep['energy']['energy_white_view'] is not None

    best = game_player.best_move(depth=2)
    assert best is not None


# ── protocol sanity ──────────────────────────────────────────────────────
def test_protocol_fast_checks_pass():
    for code in ('C1', 'C2', 'C3', 'C4', 'C6', 'C7', 'C9'):
        fn = dict((c, f) for c, _, f in D.PROTOCOL)[code]
        ok, _ = fn()
        assert ok, code


def test_baseline_file_matches_protocol():
    path = os.path.join(ROOT, 'results', 'baseline_c1_c9.json')
    with open(path) as f:
        baseline = json.load(f)
    for code, entry in baseline['protocol'].items():
        assert entry['verdict'] == 'PASS', code
