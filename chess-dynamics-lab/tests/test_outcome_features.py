#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the phase-space feature extractor (Epoch II): the frozen
constants of theorems T04/T05, determinism, group integrity."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from outcome import features as F               # noqa: E402
import dynamics as D                            # noqa: E402


def test_feature_schema():
    # v2 spec is APPEND-ONLY over the frozen v1 block of 40 coordinates
    assert len(F.FEATURE_NAMES) == 67
    assert len(F.FEATURE_NAMES[:40]) == 40
    assert F.FEATURE_NAMES[40:] == F.V2_NAMES
    assert len(set(F.FEATURE_NAMES)) == len(F.FEATURE_NAMES)
    for group, names in F.FEATURE_GROUPS.items():
        assert names, group
        assert all(n in F.FEATURE_NAMES for n in names)
    # every v2 name lands in exactly one group
    members = [n for names in F.FEATURE_GROUPS.values() for n in names]
    assert len(members) == len(set(members)) == len(F.FEATURE_NAMES)


def test_start_position_frozen_constants():
    # theorems T04/T05: mobility 20 per side, field mass 38 per side,
    # balanced material, zero energy
    pos = D.start_position()
    f = F.extract_features(pos)
    assert f['mobility_white'] == 20.0 and f['mobility_black'] == 20.0
    assert f['threat_mass_white'] == 38.0 and f['threat_mass_black'] == 38.0
    assert f['material_balance'] == 0.0
    assert f['energy'] == 0.0
    assert f['piece_count_total'] == 32.0
    assert f['side_to_move'] == 1.0
    assert f['pawns_white'] == 8.0 and f['pawns_black'] == 8.0
    assert f['king_dist_chebyshev'] == 7.0        # e1 vs e8
    assert f['in_check_white'] == 0.0 and f['in_check_black'] == 0.0


def test_after_e4_kinetic_certificate():
    # T05: after 1.e4 the White mobility is 30, the kinetic term +1.0
    pos = D.start_position()
    move = [m for m in pos.legal_moves()
            if D.move_to_uci(m) == 'e2e4'][0]
    pos.make(move)
    f = F.extract_features(pos)
    assert f['mobility_white'] == 30.0
    assert abs(f['energy'] - 1.0) < 1e-9
    assert f['side_to_move'] == -1.0


def test_extraction_is_deterministic():
    v1 = F.extract_vector(D.start_position())
    v2 = F.extract_vector(D.start_position())
    assert v1 == v2
    assert all(isinstance(x, float) for x in v1)
    assert len(v1) == len(F.FEATURE_NAMES)


def test_vector_dict_round_trip():
    pos = D.start_position()
    vec = F.extract_vector(pos)
    d = F.vector_dict(vec)
    assert d == F.extract_features(pos)


def test_king_zone_pressure_detects_threat():
    # a rook reaching the enemy king zone must light up the pressure there
    pos = D.Position().set_fen('6k1/R7/8/8/8/8/8/6K1 b - - 0 1')
    f = F.extract_features(pos)
    # the a7 rook attacks g7 inside the black king zone (g8 + neighbours)
    assert f['king_zone_pressure_black'] >= 1.0
    # the black king is far from the white king zone
    assert f['king_zone_pressure_white'] == 0.0
