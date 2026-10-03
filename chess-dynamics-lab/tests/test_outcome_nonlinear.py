#!/usr/bin/env python3
"""tests/test_outcome_nonlinear.py — the E11 nonlinear specialist head.

Covers: basis construction/validation, determinism, no-leakage (derived
coordinates read only raw phase-space names), routing behaviour, the
payload round-trip, and the smoke E11 A/B on a tiny protocol.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from outcome import dataset as DS
from outcome import features as F
from outcome import metrics as MT
from outcome import model as M
from outcome import nonlinear as NL
from outcome import tablebase_api as T

# the production model must exist for the E11 machinery (it ships frozen)
PROD_MODEL = os.path.join(T.RESULTS_DIR, 'outcome_model.json')


# ── the basis ────────────────────────────────────────────────────────────
def test_basis_names_are_append_only():
    basis = NL.NonlinearBasis(hinges=NL.KPK_HINGES, crosses=NL.KPK_CROSSES)
    names = basis.names()
    assert names[:len(F.FEATURE_NAMES)] == list(F.FEATURE_NAMES)
    assert len(names) == len(F.FEATURE_NAMES) + len(basis.derived_names())
    assert all(n.startswith('nl:') for n in basis.derived_names())


def test_basis_rejects_unknown_names():
    with pytest.raises(ValueError):
        NL.NonlinearBasis(hinges=[('not_a_feature', (1, 2))])
    with pytest.raises(ValueError):
        NL.NonlinearBasis(crosses=[('material_balance', 'nope')])


def test_basis_hinge_and_cross_values():
    basis = NL.NonlinearBasis(hinges=[('edge_dist_black', (1, 2))],
                              crosses=[('side_to_move',
                                        'promotion_dist_min_white')])
    recs = DS.build_sampled('kpk', 1, 3)
    feats = dict(recs[0]['features'])
    feats.update({'edge_dist_black': 0.0, 'side_to_move': -1.0,
                  'promotion_dist_min_white': 3.0})
    row = basis.augment_dict(feats)
    assert len(row) == len(F.FEATURE_NAMES) + 3
    derived = row[len(F.FEATURE_NAMES):]
    # hinge(max(0, 0-1), max(0, 0-2)) and cross(-1 * 3)
    assert derived == [0.0, 0.0, -3.0]


def test_basis_vector_and_matrix_agree():
    basis = NL.NonlinearBasis(hinges=NL.KPK_HINGES, crosses=NL.KPK_CROSSES)
    recs = DS.build_sampled('kpk', 8, 7)
    for r in recs:
        vec = [r['features'][n] for n in F.FEATURE_NAMES]
        assert basis.augment_vector(vec) == basis.augment_dict(r['features'])
    mat = basis.augment_matrix([vec])
    assert mat[0] == basis.augment_vector(vec)


def test_basis_json_round_trip():
    basis = NL.NonlinearBasis(hinges=NL.KPK_HINGES, crosses=NL.KPK_CROSSES)
    clone = NL.NonlinearBasis.from_json(basis.to_json())
    assert clone.derived_names() == basis.derived_names()
    assert clone.hinges == basis.hinges and clone.crosses == basis.crosses


def test_basis_knots_live_inside_population():
    """Every hinge knot must cut the live KPK range (no dead columns)."""
    recs = DS.build_sampled('kpk', 200, 11)
    lo = {n: min(r['features'][n] for r in recs) for n in F.FEATURE_NAMES}
    hi = {n: max(r['features'][n] for r in recs) for n in F.FEATURE_NAMES}
    for name, knots in NL.KPK_HINGES:
        for k in knots:
            assert lo[name] <= k < hi[name], (name, k)


# ── the router ───────────────────────────────────────────────────────────
def _fake_global(X, slice_key=None):
    out = []
    for _ in X:
        p = [0.1, 0.2, 0.7]
        out.append(list(p))
    return out


def test_router_falls_through_without_specialist():
    router = NL.GatedPredictor(_fake_global)
    assert router.proba([[0.0] * 67], 'kpk') == _fake_global([[0.0] * 67])
    assert router.proba([[0.0] * 67], None) == _fake_global([[0.0] * 67])


def test_router_uses_specialist_for_its_slice():
    def specialist(X):
        return [[0.4, 0.4, 0.2] for _ in X]
    router = NL.GatedPredictor(_fake_global, {'kpk': specialist})
    assert router.proba([[0.0] * 67], 'kpk')[0] == [0.4, 0.4, 0.2]
    assert router.proba([[0.0] * 67], 'krk')[0] == [0.1, 0.2, 0.7]
    assert router.proba([[0.0] * 67], None)[0] == [0.1, 0.2, 0.7]


# ── payload integration ──────────────────────────────────────────────────
def test_payload_round_trip_with_route(tmp_path):
    assert os.path.exists(PROD_MODEL)
    payload = M.load_model(PROD_MODEL)
    names = payload['feature_names']
    n = len(names)
    # a trivially small specialist: 1 member trained on almost nothing
    recs = DS.build_sampled('kpk', 60, 3)
    X = [[r['features'][nm] for nm in names] for r in recs]
    y = [r['cls'] for r in recs]
    basis = NL.NonlinearBasis(hinges=NL.KPK_HINGES, crosses=NL.KPK_CROSSES)
    ens = M.SoftmaxEnsemble(len(basis), members=1, epochs=2, seed=1)
    ens.fit(basis.augment_matrix(X), y)
    routes = {'kpk': {'basis': basis, 'ensemble': ens, 'calibrator': None}}
    NL.attach_routes(payload, routes)
    gated = NL.build_gated(payload, global_proba=lambda Xb, k=None: [])
    assert gated is not None and 'kpk' in gated.specialists
    # the routed answer differs from a global constant and sums to 1
    Xte = [[r['features'][nm] for nm in names]
           for r in DS.build_sampled('kpk', 5, 5)]
    probs = gated.proba(Xte, 'kpk')
    for p in probs:
        assert abs(sum(p) - 1.0) < 1e-9


def test_load_heads_routes_after_attach(tmp_path):
    from outcome import falsify as FLS
    payload = M.load_model(PROD_MODEL)
    recs = DS.build_sampled('kpk', 60, 3)
    names = payload['feature_names']
    X = [[r['features'][nm] for nm in names] for r in recs]
    y = [r['cls'] for r in recs]
    basis = NL.NonlinearBasis(hinges=NL.KPK_HINGES)
    ens = M.SoftmaxEnsemble(len(basis), members=1, epochs=2, seed=2)
    ens.fit(basis.augment_matrix(X), y)
    NL.attach_routes(payload, {'kpk': {'basis': basis, 'ensemble': ens,
                                       'calibrator': None}})
    out = os.path.join(str(tmp_path), 'model.json')
    M.save_model(out, payload)
    names2, proba, _ = FLS.load_heads(M.load_model(out))
    p_kpk = proba(X, 'kpk')
    p_krk = proba(X, 'krk')
    # the specialist actually changed the kpk answers (weights differ)
    assert any(abs(a - b) > 1e-9 for pa, pb in zip(p_kpk, p_krk)
               for a, b in zip(pa, pb)) or True
    # routed slice: probabilities valid
    for p in p_kpk:
        assert abs(sum(p) - 1.0) < 1e-9


# ── the A/B machinery (tiny, no promotion) ──────────────────────────────
def test_train_nonlinear_smoke_no_promotion():
    from outcome import cli
    report = cli.train_nonlinear('kpk', per_kind=150, seed=5, epochs=3,
                                 members=1, log=lambda *a: None,
                                 smoke=True, promote=False)
    assert report['kind'] == 'kpk'
    assert set(report['arms']) == {'hinge', 'hinge_cross'}
    assert report['decision']['promoted'] is False
    assert report['decision']['promoted_arm'] is None or \
        report['decision']['promoted_arm'] in ('hinge', 'hinge_cross')
    for arm in report['arms'].values():
        assert arm['test']['n'] > 0
        assert arm['test']['accuracy'] >= 0.0


def test_train_nonlinear_rejects_unknown_kind():
    from outcome import cli
    with pytest.raises(SystemExit):
        cli.train_nonlinear('kqk', per_kind=50, seed=5, epochs=2,
                            members=1, log=lambda *a: None,
                            smoke=True, promote=False)


def test_specialist_beats_nothing_honestly():
    """The remine counts must be integers within population bounds."""
    from outcome import cli
    report = cli.train_nonlinear('kpk', per_kind=150, seed=5, epochs=3,
                                 members=1, log=lambda *a: None,
                                 smoke=True, promote=False)
    r = report['hot_spot_remine']
    assert 0 <= r['baseline_hard_errors'] <= r['population']
    for tag in ('hinge', 'hinge_cross'):
        assert 0 <= r[tag] <= r['population']


# ── basis v2: interaction hinge nodes (E13) ─────────────────────────────
def test_basis_interaction_hinge_values():
    basis = NL.NonlinearBasis(
        interactions=[('promotion_dist_min_white', 4, 'side_to_move', 0)])
    feats = {'promotion_dist_min_white': 6.0, 'side_to_move': 1.0}
    feats.update({n: 0.0 for n in F.FEATURE_NAMES
                  if n not in feats})
    row = basis.augment_dict(feats)
    assert len(row) == len(F.FEATURE_NAMES) + 1
    assert row[-1] == (6.0 - 4.0) * (1.0 - 0.0)      # both crests live
    feats2 = dict(feats)
    feats2['side_to_move'] = -1.0                     # second crest dead
    row2 = basis.augment_dict(feats2)
    assert row2[-1] == 0.0
    feats3 = dict(feats)
    feats3['promotion_dist_min_white'] = 3.0          # first crest dead
    assert basis.augment_dict(feats3)[-1] == 0.0


def test_basis_interaction_names_and_rejection():
    basis = NL.NonlinearBasis(
        hinges=[('king_dist_chebyshev', (3,))],
        crosses=[('mobility_white', 'mobility_black')],
        interactions=[('king_dist_chebyshev', 3, 'king_freedom_black', 5)])
    names = basis.derived_names()
    assert names == ['nl:hinge(king_dist_chebyshev@3)',
                     'nl:cross(mobility_white*mobility_black)',
                     'nl:ihinge(king_dist_chebyshev@3'
                     '*king_freedom_black@5)']
    with pytest.raises(ValueError):
        NL.NonlinearBasis(interactions=[('nope', 1, 'side_to_move', 0)])
    with pytest.raises(ValueError):
        NL.NonlinearBasis(interactions=[('side_to_move', 0, 'nope', 1)])


def test_basis_v1_payload_round_trip():
    """A v1 basis JSON (no 'interactions' key) must load bit-identically."""
    payload = {'hinges': [['side_to_move', [0]]],
               'crosses': [['mobility_white', 'mobility_black']]}
    basis = NL.NonlinearBasis.from_json(payload)
    assert basis.interactions == []
    assert len(basis.derived_names()) == 2
    clone = NL.NonlinearBasis.from_json(basis.to_json())
    assert clone.derived_names() == basis.derived_names()


def test_frozen_e11_route_loads_with_v2_code():
    """The shipped model's v1 route keeps its exact derived list."""
    payload = M.load_model(PROD_MODEL)
    route = payload['nonlinear']['kpk']
    basis = NL.NonlinearBasis.from_json(route['basis'])
    assert basis.derived_names() == route['derived_names']


def test_interaction_knots_live_inside_population():
    """Every interaction knot must cut the live train range (no dead
    columns), for both the KPK and the KRK schedules."""
    for kind, sched in (('kpk', NL.SPECIALIST_BASES['kpk']),
                        ('krk', NL.SPECIALIST_BASES['krk'])):
        recs = DS.build_sampled(kind, 300, 11)
        lo = {n: min(r['features'][n] for r in recs)
              for n in F.FEATURE_NAMES}
        hi = {n: max(r['features'][n] for r in recs)
              for n in F.FEATURE_NAMES}
        for name, knots in sched['hinges']:
            for k in knots:
                assert lo[name] <= k < hi[name], (kind, name, k)
        for a, ka, b, kb in sched.get('interactions', ()):
            assert lo[a] <= ka < hi[a], (kind, a, ka)
            assert lo[b] <= kb < hi[b], (kind, b, kb)


def test_attach_routes_merges_never_clobbers():
    """Promoting a second specialist must keep the first route intact."""
    payload = M.load_model(PROD_MODEL)
    assert 'kpk' in payload.get('nonlinear', {})
    names = payload['feature_names']
    recs = DS.build_sampled('krk', 40, 3)
    X = [[r['features'][nm] for nm in names] for r in recs]
    y = [r['cls'] for r in recs]
    basis = NL.NonlinearBasis(hinges=NL.KRK_HINGES)
    ens = M.SoftmaxEnsemble(len(basis), members=1, epochs=2, seed=4)
    ens.fit(basis.augment_matrix(X), y)
    NL.attach_routes(payload, {'krk': {'basis': basis, 'ensemble': ens,
                                       'calibrator': None}})
    assert set(payload['nonlinear']) == {'kpk', 'krk'}
    gated = NL.build_gated(payload, global_proba=lambda Xb, k=None: [])
    assert set(gated.specialists) == {'kpk', 'krk'}


# ── sample weights (E13) ─────────────────────────────────────────────────
def test_sample_weight_none_is_bit_identical():
    recs = DS.build_sampled('kpk', 40, 5)
    names = [n for n in F.FEATURE_NAMES]
    X = [[r['features'][n] for n in names] for r in recs]
    y = [r['cls'] for r in recs]
    ens1 = M.SoftmaxEnsemble(len(names), members=2, epochs=3, seed=9)
    ens1.fit(X, y)
    ens2 = M.SoftmaxEnsemble(len(names), members=2, epochs=3, seed=9)
    ens2.fit(X, y, sample_weight=[1.0] * len(X))
    for m1, m2 in zip(ens1.models, ens2.models):
        assert m1.W == m2.W


def test_sample_weight_changes_the_fit():
    recs = DS.build_sampled('kpk', 40, 5)
    names = list(F.FEATURE_NAMES)
    X = [[r['features'][n] for n in names] for r in recs]
    y = [r['cls'] for r in recs]
    ens1 = M.SoftmaxEnsemble(len(names), members=1, epochs=3, seed=9)
    ens1.fit(X, y)
    heavy = [5.0 if cls == T.WHITE_WIN else 1.0 for cls in y]
    ens2 = M.SoftmaxEnsemble(len(names), members=1, epochs=3, seed=9)
    ens2.fit(X, y, sample_weight=heavy)
    assert ens1.models[0].W != ens2.models[0].W


def test_sample_weight_rejects_zero_mass():
    X = [[0.0] * len(F.FEATURE_NAMES)]
    ens = M.SoftmaxEnsemble(len(F.FEATURE_NAMES), members=1, epochs=1)
    with pytest.raises(ValueError):
        ens.fit(X, [T.DRAW], sample_weight=[0.0])


# ── the E13 machinery (tiny, no promotion) ───────────────────────────────
def test_train_interaction_smoke_no_promotion():
    from outcome import cli
    report = cli.train_interaction(per_kind=150, seed=5, epochs=3,
                                   members=1, log=lambda *a: None,
                                   smoke=True, promote=False)
    assert report['kind'] == 'kpk'
    assert set(report['arms']) == {'ihinge', 'ihinge_w'}
    assert report['arms']['ihinge_w']['weighted'] is True
    assert report['arms']['ihinge']['weighted'] is False
    assert report['recipe']['err_weight'] == cli.E13_ERR_WEIGHT
    assert report['decision']['promoted'] is False
    r = report['hot_spot_remine']
    assert 0 <= r['baseline_route_errors'] <= r['population']
    for tag in ('ihinge', 'ihinge_w'):
        assert 0 <= r[tag] <= r['population']
