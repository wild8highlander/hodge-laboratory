#!/usr/bin/env python3
"""outcome/nonlinear.py — the nonlinear specialist head (Epoch VII, E11).

E10 (the falsification corpus) identified the KPK domain as the main
hot-spot of the frozen E8 model: 22.15% hard errors against the exact
oracle (KRK 3.30%, KQK 0.35%, KNK/KBK 0.00%).  The reason is structural,
not statistical: the KPK outcome boundary is famously NONLINEAR — the
rule of the square, key squares, king opposition and the tempo of the
pawn race are conjunctions of conditions, and a linear softmax over
phase-space coordinates can only carve hyperplanes.

This module adds the missing nonlinearity in the most conservative,
fully auditable way:

1.  NONLINEAR BASIS (zero-dependency, deterministic).  Three families of
    derived coordinates are APPENDED to the 67 raw phase-space features:

        hinge(name, knot)  = max(0, x_name - knot)      (piecewise-linear,
                                                          MARS-style crests)
        cross(a, b)        = x_a * x_b                  (explicit pairwise
                                                          interactions)
        ihinge(a, ka,      = max(0, x_a - ka)           (INTERACTION HINGE
                b, kb)       * max(0, x_b - kb)      NODES, basis v2 /
                                                      the E13 upgrade: a
                                                      product of two crests
                                                      is a localized
                                                      conjunction cell —
                                                      it switches on only
                                                      in a corner of the
                                                      phase space, which is
                                                      exactly the shape of
                                                      a rule-of-the-square
                                                      or boxed-king
                                                      condition)

    The KPK knot schedule is frozen from measured feature ranges
    (every knot sits inside the live population, no dead columns).
    The basis reads ONLY raw phase-space coordinates — never labels,
    never tablebase values — so the no-leakage rule of features.py is
    inherited by construction.

2.  GATED ROUTING.  The production predictor becomes a router: the
    KPK slice is answered by a dedicated specialist (same recipe as
    the E8 production head: bootstrap ensemble of hard-target softmax
    models + per-domain temperature calibration on the valid split),
    every other domain and all out-of-domain positions keep the frozen
    global model.  Specialists never see another domain's rows, so a
    specialist can only change its own slice.

3.  HONEST PROMOTION.  The specialist replaces the KPK route of the
    production model file ONLY if it improves BOTH accuracy and log
    loss on the untouched KPK test split (and the decision, the A/B
    numbers and the basis spec are frozen in the E11 certificate).
    After promotion the E10 falsification corpus is re-mined, so the
    regression benchmark reflects the new predictor exactly.
"""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from outcome import features as F                           # noqa: E402
from outcome import model as M                              # noqa: E402

BASIS_SPEC_VERSION = ('nonlinear-basis v2 (hinge + cross + interaction'
                      ' hinge, append-only)')

# ── the frozen KPK basis (knots from the measured ranges, see E11) ──────
KPK_HINGES = (
    ('promotion_dist_min_white', (1, 2, 3, 4, 5)),
    ('king_dist_chebyshev', (2, 3, 4, 5, 6)),
    ('king_dist_manhattan', (3, 5, 7, 9, 11)),
    ('edge_dist_black', (1, 2)),
    ('edge_dist_white', (1, 2)),
    ('strongest_dist_own_king_white', (2, 3, 4, 5)),
    ('strongest_dist_enemy_king_white', (2, 3, 4, 5)),
    ('king_freedom_black', (2, 4, 6)),
    ('king_freedom_white', (2, 4, 6)),
    ('mobility_white', (3, 5, 7, 9, 11)),
    ('mobility_black', (2, 4, 6)),
    ('threat_coverage_white', (5, 7, 9)),
    ('threat_coverage_black', (4, 6)),
    ('center_dist_black', (1, 2)),
)

KPK_CROSSES = (
    ('promotion_dist_min_white', 'king_dist_chebyshev'),
    ('promotion_dist_min_white', 'edge_dist_black'),
    ('promotion_dist_min_white', 'strongest_dist_own_king_white'),
    ('king_dist_chebyshev', 'edge_dist_black'),
    ('side_to_move', 'promotion_dist_min_white'),
    ('side_to_move', 'king_dist_chebyshev'),
    ('in_check_black', 'king_dist_chebyshev'),
    ('mobility_white', 'mobility_black'),
    ('king_freedom_white', 'king_freedom_black'),
    ('threat_coverage_white', 'threat_coverage_black'),
)

# ── the E13 interaction-hinge schedule (corpus-driven, train-only) ────
# Knots chosen from the TRAIN-split residual error diagnostics of the
# promoted E11 specialist (17.12% train hard errors): the errors live
# in the deep pawn-race cells (promotion_dist 3..5 crossed with king
# distances 3..7), the boxed-defender cells (king distance crossed
# with low defender freedom) and the edge-defence cells.  Every knot
# sits strictly inside the live train range of its coordinate (the
# E11 no-dead-columns rule), and the diagnostics read no labels of
# the valid/test splits.
KPK_INTERACTIONS = (
    # rule of the square: deep pawn x king distance
    ('promotion_dist_min_white', 3, 'king_dist_chebyshev', 3),
    ('promotion_dist_min_white', 4, 'king_dist_chebyshev', 3),
    ('promotion_dist_min_white', 5, 'king_dist_chebyshev', 4),
    ('promotion_dist_min_white', 4, 'king_dist_manhattan', 5),
    ('promotion_dist_min_white', 5, 'king_dist_manhattan', 7),
    # tempo: deep pawn x side to move (hinge(0) is the WTM indicator)
    ('promotion_dist_min_white', 4, 'side_to_move', 0),
    ('promotion_dist_min_white', 5, 'side_to_move', 0),
    # boxed defender: king distance x defender freedom
    ('king_dist_chebyshev', 3, 'king_freedom_black', 5),
    ('king_dist_chebyshev', 4, 'king_freedom_black', 7),
    ('king_dist_manhattan', 5, 'king_freedom_black', 4),
    # edge defence: defender/attacker on the rim x running distance
    ('edge_dist_black', 1, 'king_dist_manhattan', 5),
    ('edge_dist_white', 1, 'king_dist_manhattan', 5),
    # open-field regime where both kings roam (the (5,5)/(8,8) cells)
    ('king_freedom_white', 5, 'king_freedom_black', 5),
    # attacker far from its own pawn x running distance
    ('strongest_dist_own_king_white', 3, 'king_dist_manhattan', 5),
    # kinetic cells
    ('mobility_white', 7, 'mobility_black', 4),
    ('threat_coverage_white', 7, 'threat_coverage_black', 5),
)

# ── the E14 KRK schedule (corpus-driven, train-only) ──────────────────
# KRK train errors (3.25%) are ~99% "win called draw" and their
# signature is unambiguous: the rook is already next to the black king
# (strongest_dist_enemy_king_white 1..2), the defender king is boxed
# (king_freedom_black <= 4, mobility_black <= 4) and often in check,
# with elevated king-zone pressure — late-stage deep mates where a
# linear response saturates too early and tips into the draw class.
KRK_HINGES = (
    ('strongest_dist_enemy_king_white', (1, 2, 3)),
    ('strongest_dist_own_king_white', (2, 4, 6)),
    ('strongest_edge_dist_white', (1, 2)),
    ('strongest_center_dist_white', (1, 2)),
    ('king_dist_chebyshev', (3, 4, 5)),
    ('king_dist_manhattan', (5, 7, 9)),
    ('edge_dist_black', (1, 2)),
    ('edge_dist_white', (1, 2)),
    ('center_dist_black', (1, 2)),
    ('king_freedom_black', (2, 4)),
    ('king_freedom_white', (3, 5)),
    ('mobility_black', (2, 3, 4)),
    ('mobility_white', (13, 16, 19)),
    ('threat_mass_white', (14, 17, 19)),
    ('threat_coverage_white', (14, 17, 19)),
    ('threat_coverage_black', (5, 7)),
    ('king_zone_pressure_black', (2, 4)),
    ('king_zone_pressure_white', (1,)),
)

KRK_CROSSES = (
    ('strongest_dist_enemy_king_white', 'king_freedom_black'),
    ('strongest_dist_enemy_king_white', 'edge_dist_black'),
    ('strongest_dist_own_king_white', 'king_dist_manhattan'),
    ('king_zone_pressure_black', 'king_dist_manhattan'),
    ('in_check_black', 'strongest_dist_enemy_king_white'),
    ('mobility_white', 'mobility_black'),
    ('threat_coverage_white', 'king_freedom_black'),
    ('side_to_move', 'king_dist_manhattan'),
    ('king_dist_chebyshev', 'edge_dist_black'),
    ('mobility_black', 'edge_dist_black'),
)

# the frozen specialist schedules: a kind needs an explicit, reviewed
# basis before a specialist route can be trained for it (E11 froze KPK,
# the E10 hot-spot; E14 added KRK, the second hot-spot at 3.30%; other
# kinds follow only after their own A/B).
SPECIALIST_BASES = {
    'kpk': {'hinges': KPK_HINGES, 'crosses': KPK_CROSSES,
            'interactions': KPK_INTERACTIONS},
    'krk': {'hinges': KRK_HINGES, 'crosses': KRK_CROSSES},
}


def _check_name(name):
    if name not in F.FEATURE_NAMES:
        raise ValueError('nonlinear basis: %r is not a raw phase-space '
                         'coordinate (no leakage allowed)' % (name,))


class NonlinearBasis:
    """A frozen list of hinge + cross + interaction-hinge coordinates.

    v1 payloads carry no 'interactions' key and load unchanged (empty
    interaction block, bit-identical derived list), so the E11 route of
    a v3 model file keeps its exact predictions across the upgrade."""

    def __init__(self, hinges=(), crosses=(), interactions=()):
        self.hinges = [(n, tuple(k)) for n, k in hinges]
        self.crosses = [(a, b) for a, b in crosses]
        self.interactions = [(a, ka, b, kb) for a, ka, b, kb in interactions]
        for n, _ in self.hinges:
            _check_name(n)
        for a, b in self.crosses:
            _check_name(a)
            _check_name(b)
        for a, _ka, b, _kb in self.interactions:
            _check_name(a)
            _check_name(b)

    # ── naming (frozen order = feature order) ────────────────────────────
    def derived_names(self):
        out = []
        for name, knots in self.hinges:
            for k in knots:
                out.append('nl:hinge(%s@%g)' % (name, k))
        for a, b in self.crosses:
            out.append('nl:cross(%s*%s)' % (a, b))
        for a, ka, b, kb in self.interactions:
            out.append('nl:ihinge(%s@%g*%s@%g)' % (a, ka, b, kb))
        return out

    def names(self):
        """Full augmented coordinate list: base 67 + derived, in order."""
        return list(F.FEATURE_NAMES) + self.derived_names()

    def __len__(self):
        return len(F.FEATURE_NAMES) + len(self.derived_names())

    # ── the expansion itself ─────────────────────────────────────────────
    def augment_dict(self, feats):
        """Feature-name dict -> augmented vector (base block + derived)."""
        row = [feats[n] for n in F.FEATURE_NAMES]
        for name, knots in self.hinges:
            x = feats[name]
            for k in knots:
                row.append(x - k if x > k else 0.0)
        for a, b in self.crosses:
            row.append(feats[a] * feats[b])
        for a, ka, b, kb in self.interactions:
            xa = feats[a] - ka
            xb = feats[b] - kb
            row.append((xa if xa > 0.0 else 0.0) * (xb if xb > 0.0 else 0.0))
        return row

    def augment_vector(self, vec):
        """Base-aligned vector -> augmented vector."""
        return self.augment_dict(F.vector_dict(vec))

    def augment_matrix(self, X_base):
        """List of base-aligned vectors -> list of augmented vectors."""
        return [self.augment_vector(v) for v in X_base]

    # ── persistence ──────────────────────────────────────────────────────
    def to_json(self):
        return {'version': BASIS_SPEC_VERSION,
                'hinges': [[n, list(k)] for n, k in self.hinges],
                'crosses': [list(p) for p in self.crosses],
                'interactions': [[a, ka, b, kb]
                                 for a, ka, b, kb in self.interactions]}

    @classmethod
    def from_json(cls, payload):
        return cls(payload['hinges'], payload['crosses'],
                   payload.get('interactions', ()))


# ── gated routing ────────────────────────────────────────────────────────
class GatedPredictor:
    """Slice-routed predictor: specialists override the global model.

    proba(X, slice_key) keeps the load_heads convention: one batch per
    domain kind.  A kind without a specialist (and every out-of-domain
    call, slice_key=None) falls through to the frozen global model, so
    the router can only change the slices it explicitly owns.  The
    global head is called with (X, slice_key) and adapters make both
    the 1-arg and the 2-arg conventions work."""

    def __init__(self, global_proba, specialists=None):
        self.global_proba = _adapt_global(global_proba)
        self.specialists = dict(specialists or {})

    def proba(self, X, slice_key=None):
        fn = self.specialists.get(slice_key)
        if fn is not None:
            return fn(X)
        return self.global_proba(X, slice_key)


def _adapt_global(fn):
    """Normalise a global head to the (X, slice_key) calling convention."""
    try:
        sig = inspect.signature(fn)
        positional = [
            p for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        required = [p for p in positional if p.default is p.empty]
    except (TypeError, ValueError):          # builtins without signatures
        return lambda X, slice_key=None: fn(X)
    if len(required) >= 2:
        return fn
    return lambda X, slice_key=None: fn(X)


def _specialist_fn(ensemble, calibrator, slice_key, basis):
    """Closed-over specialist prediction: basis expansion + ensemble
    + its own temperature.  Callers pass RAW base-aligned vectors; the
    specialist owns its augmentation."""
    def fn(X):
        X_aug = basis.augment_matrix(X) if basis is not None else X
        probs = ensemble.predict_proba_raw(X_aug)
        if calibrator is not None:
            probs = [calibrator.transform(p, slice_key) for p in probs]
        return probs
    return fn


# ── payload integration (model file v3) ─────────────────────────────────
def attach_routes(payload, routes):
    """Attach {kind: {'basis': basis, 'ensemble': ens, 'calibrator': cal}}
    to a model payload as the 'nonlinear' block (in place).

    The attach MERGES into any existing block, so promoting a second
    specialist (E14 krk after E13 kpk) never clobbers the first route;
    attaching the same kind twice replaces that route only."""
    block = dict(payload.get('nonlinear') or {})
    for kind, route in sorted(routes.items()):
        block[kind] = {
            'basis': route['basis'].to_json(),
            'derived_names': route['basis'].derived_names(),
            'ensemble': route['ensemble'].to_json(),
            'calibrator': route['calibrator'].to_json()
            if route.get('calibrator') else None,
        }
    payload['nonlinear'] = block
    return payload


def build_gated(payload, global_proba):
    """GatedPredictor from a model payload (None when no nonlinear block)."""
    block = payload.get('nonlinear')
    if not block:
        return None
    specialists = {}
    for kind, route in block.items():
        basis = NonlinearBasis.from_json(route['basis'])
        n_feat = len(F.FEATURE_NAMES) + len(route['derived_names'])
        ens = M.SoftmaxEnsemble.from_json(route['ensemble'], n_feat)
        cal = M.TemperatureCalibrator.from_json(route['calibrator']) \
            if route.get('calibrator') else None
        specialists[kind] = _specialist_fn(ens, cal, kind, basis)
    return GatedPredictor(global_proba, specialists)


def load_ensemble_from_block(route):
    """Rebuild one specialist ensemble from its payload route."""
    n_derived = len(route['derived_names'])
    n_feat = len(F.FEATURE_NAMES) + n_derived
    return M.SoftmaxEnsemble.from_json(route['ensemble'], n_feat)
