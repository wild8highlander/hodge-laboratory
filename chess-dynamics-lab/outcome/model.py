#!/usr/bin/env python3
"""outcome/model.py — the distillation models (Epochs III+V, zero-dependency).

Two heads, exactly as the program prescribes:

Head B (outcome distribution)   softmax regression  x -> (P_W, P_D, P_L)
Head A (value / DTM regression) ridge regression     x -> DTM in plies

Both are textbook full-batch gradient descent in pure Python:

*  no numpy, no sklearn — the whole laboratory stays zero-dependency;
*  zero initialisation + full-batch steps + fixed hyperparameters =>
   bit-reproducible weights on every machine (the repo's determinism law);
*  L2 regularisation (never on the bias) and standardisation of the
   inputs fitted on the train split only — no test statistics ever touch
   the preprocessing, which keeps the calibration metrics honest.

v2 additions (the E8 distillation upgrade):

*  ORACLE-SHAPED SOFT TARGETS  — a mate in 3 is phase-space far from a
   draw, a mate in 30 sits near the draw boundary; the target therefore
   leaks a distance-aware mass eps(d) = 0.5·d/(d+tau) from the win class
   to the draw class (SOFT_TAU plies), and draw states shed a small
   symmetric mass SOFT_EPS_DRAW.  The report A/B-tests hard vs soft.
*  SOFTMAX ENSEMBLE  — bootstrap-resampled members (splitmix64-seeded,
   bit-reproducible) averaged at prediction: variance reduction without
   any dependency.
*  TEMPERATURE CALIBRATION  — per-domain tau fitted on the VALID split
   only (deterministic grid + golden refine on log loss), applied at
   inference; honest calibration without touching the test split.

v3 additions (the E11 nonlinear upgrade, outcome/nonlinear.py):

*  NONLINEAR SPECIALIST ROUTES — the payload may carry a 'nonlinear'
   block: per-kind specialists (hinge+cross basis expansion + their own
   ensemble + calibrator).  load_heads-style consumers route slices
   through the specialist; every other slice keeps the global head.

The 3-class head is deliberate: inside the frozen endgame domains the
black_win class receives no support (White cannot lose KRK/KQK/KNK/KPK/KBK),
so its probability is correctly driven to ~0 there, while the very same
code trains unchanged on full-chess data in Epoch IV.
"""
import json
import math
import os

MODEL_FORMAT = 'chess-dynamics-lab outcome model v3'
MODEL_FORMATS = (MODEL_FORMAT,
                 'chess-dynamics-lab outcome model v2',
                 'chess-dynamics-lab outcome model v1')

# ── E8 soft-target constants (frozen in the certificate recipe) ────────
SOFT_TAU = 8.0            # plies scale of the distance-aware smoothing
SOFT_EPS_DRAW = 0.04      # symmetric mass shed by the draw class

# class index convention (identical to tablebase_api): 0=black 1=draw 2=white
BLACK_WIN, DRAW, WHITE_WIN = 0, 1, 2


def soft_targets(cls_index, dtm_plies=None, tau=SOFT_TAU,
                 eps_draw=SOFT_EPS_DRAW):
    """Oracle-shaped soft target distribution for one training state.

    Won states: mass 1 - eps on the true class, eps = 0.5·d/(d+tau) on
    draw — a long mate is 'nearer' a draw in phase space.  Draw states:
    a symmetric eps_draw/2 to each win class.  Losses (never present in
    the frozen domains): hard one-hot."""
    t = [0.0, 0.0, 0.0]
    if cls_index == WHITE_WIN and dtm_plies is not None and dtm_plies >= 0:
        eps = 0.5 * dtm_plies / (dtm_plies + tau)
        t[WHITE_WIN] = 1.0 - eps
        t[DRAW] = eps
    elif cls_index == DRAW:
        t[DRAW] = 1.0 - eps_draw
        t[BLACK_WIN] = eps_draw / 2.0
        t[WHITE_WIN] = eps_draw / 2.0
    else:
        t[cls_index] = 1.0
    return t


# ── preprocessing ────────────────────────────────────────────────────────
class Standardizer:
    """Per-feature mean/std fitted on the train split only."""

    def __init__(self, means=None, stds=None):
        self.means = means
        self.stds = stds

    def fit(self, X):
        n = len(X)
        d = len(X[0])
        means = [0.0] * d
        for row in X:
            for j in range(d):
                means[j] += row[j]
        means = [m / n for m in means]
        stds = [0.0] * d
        for row in X:
            for j in range(d):
                dv = row[j] - means[j]
                stds[j] += dv * dv
        stds = [math.sqrt(s / n) for s in stds]
        stds = [s if s > 1e-9 else 1.0 for s in stds]
        self.means, self.stds = means, stds
        return self

    def transform(self, X):
        mu, sd = self.means, self.stds
        out = []
        for row in X:
            out.append([(row[j] - mu[j]) / sd[j] for j in range(len(mu))])
        return out

    def to_json(self):
        return {'means': self.means, 'stds': self.stds}

    @classmethod
    def from_json(cls, payload):
        return cls(payload['means'], payload['stds'])


# ── head B: multinomial logistic regression ──────────────────────────────
class SoftmaxRegression:
    """Full-batch softmax regression with momentum and L2 shrinkage."""

    def __init__(self, n_features, n_classes=3, l2=1e-4, lr=0.1,
                 epochs=40, momentum=0.9):
        self.n_features = n_features
        self.n_classes = n_classes
        self.l2 = l2
        self.lr = lr
        self.epochs = epochs
        self.momentum = momentum
        # weights[k] = bias + d coefficients of class k
        self.W = [[0.0] * (n_features + 1) for _ in range(n_classes)]
        self.loss_history = []

    def _forward(self, row):
        """row: standardized features + bias appended.  Returns softmax."""
        W = self.W
        d = len(row)
        logits = [0.0] * self.n_classes
        for k in range(self.n_classes):
            wk = W[k]
            s = wk[0]
            for j in range(1, d + 1):
                s += wk[j] * row[j - 1]
            logits[k] = s
        mx = max(logits)
        exps = [math.exp(v - mx) for v in logits]
        z = sum(exps)
        return [e / z for e in exps]

    def fit(self, X_raw, y, verbose=False, targets=None,
            sample_weight=None):
        """Full-batch GD.  `y` holds class indices; `targets` (optional)
        holds per-sample soft target distributions (E8) and overrides
        the one-hot construction.  `sample_weight` (optional, E13) holds
        a non-negative per-row weight: the loss and the gradient become
        the weighted mean (normalised by the weight sum), which lets an
        experiment emphasise the residual-error corpus without touching
        the protocol.  Both optional paths are bit-reproducible, and the
        default path (both None) is byte-identical to the pre-E13 code."""
        std = Standardizer().fit(X_raw)
        X = std.transform(X_raw)
        n, d = len(X), self.n_features
        K = self.n_classes
        if targets is None:
            targets = [[1.0 if k == yi else 0.0 for k in range(K)]
                       for yi in y]
        W = self.W
        vel = [[0.0] * (d + 1) for _ in range(K)]
        self.loss_history = []
        if sample_weight is not None:
            wsum = float(sum(sample_weight))
            if wsum <= 0.0:
                raise ValueError('sample_weight must sum to a positive value')
        for epoch in range(self.epochs):
            grad = [[0.0] * (d + 1) for _ in range(K)]
            loss = 0.0
            for i in range(n):
                row = X[i]
                p = self._forward(row)
                ti = targets[i]
                wi = 1.0 if sample_weight is None else float(sample_weight[i])
                if wi != 0.0:
                    for k in range(K):
                        if ti[k] > 0.0:
                            loss -= wi * ti[k] * math.log(max(p[k], 1e-15))
                    for k in range(K):
                        gk = grad[k]
                        coeff = wi * (p[k] - ti[k])
                        if coeff == 0.0:
                            continue
                        gk[0] += coeff
                        for j in range(d):
                            gk[j + 1] += coeff * row[j]
            if sample_weight is None:
                inv = 1.0 / n
            else:
                inv = 1.0 / wsum
            for k in range(K):
                gk = grad[k]
                wk = W[k]
                vk = vel[k]
                for j in range(d + 1):
                    gj = gk[j] * inv
                    if j > 0:
                        gj += self.l2 * wk[j]
                    vk[j] = self.momentum * vk[j] - self.lr * gj
                    wk[j] += vk[j]
            loss *= inv
            self.loss_history.append(loss)
            if verbose and (epoch % 5 == 0 or epoch == self.epochs - 1):
                print('    epoch %3d  logloss %.6f' % (epoch, loss))
        self._standardizer = std
        return self

    def predict_proba_raw(self, X_raw):
        X = self._standardizer.transform(X_raw)
        return [self._forward(row) for row in X]

    # ── persistence ──────────────────────────────────────────────────────
    def to_json(self):
        return {'weights': self.W,
                'standardizer': self._standardizer.to_json()}

    @classmethod
    def from_json(cls, payload, n_features, n_classes=3):
        model = cls(n_features, n_classes)
        model.W = [list(w) for w in payload['weights']]
        model._standardizer = Standardizer.from_json(payload['standardizer'])
        return model


# ── head A: ridge regression for the DTM value ───────────────────────────
class RidgeRegression:
    """Full-batch ridge regression (the DTM head), target standardised."""

    def __init__(self, n_features, l2=1e-3, lr=0.05, epochs=60, momentum=0.9):
        self.n_features = n_features
        self.l2 = l2
        self.lr = lr
        self.epochs = epochs
        self.momentum = momentum
        self.w = [0.0] * (n_features + 1)      # bias + coefficients
        self.loss_history = []

    def fit(self, X_raw, y_raw, verbose=False):
        xstd = Standardizer().fit(X_raw)
        X = xstd.transform(X_raw)
        y_mean = sum(y_raw) / len(y_raw)
        y_std = math.sqrt(sum((v - y_mean) ** 2 for v in y_raw) / len(y_raw))
        if y_std < 1e-9:
            y_std = 1.0
        y = [(v - y_mean) / y_std for v in y_raw]
        n, d = len(X), self.n_features
        w = self.w
        vel = [0.0] * (d + 1)
        self.loss_history = []
        for epoch in range(self.epochs):
            grad = [0.0] * (d + 1)
            loss = 0.0
            for i in range(n):
                row = X[i]
                pred = w[0]
                for j in range(d):
                    pred += w[j + 1] * row[j]
                err = pred - y[i]
                loss += err * err
                grad[0] += err
                for j in range(d):
                    grad[j + 1] += err * row[j]
            inv = 1.0 / n
            for j in range(d + 1):
                gj = grad[j] * inv
                if j > 0:
                    gj += self.l2 * w[j]
                vel[j] = self.momentum * vel[j] - self.lr * gj
                w[j] += vel[j]
            self.loss_history.append(loss * inv)
            if verbose and (epoch % 10 == 0 or epoch == self.epochs - 1):
                print('    epoch %3d  mse %.6f' % (epoch, loss * inv))
        self._xstd = xstd
        self._y_mean, self._y_std = y_mean, y_std
        return self

    def predict_raw(self, X_raw):
        X = self._xstd.transform(X_raw)
        w = self.w
        out = []
        for row in X:
            pred = w[0]
            for j in range(self.n_features):
                pred += w[j + 1] * row[j]
            pred = pred * self._y_std + self._y_mean
            out.append(pred)
        return out

    def to_json(self):
        return {'weights': self.w, 'x_standardizer': self._xstd.to_json(),
                'y_mean': self._y_mean, 'y_std': self._y_std}

    @classmethod
    def from_json(cls, payload, n_features):
        model = cls(n_features)
        model.w = list(payload['weights'])
        model._xstd = Standardizer.from_json(payload['x_standardizer'])
        model._y_mean = payload['y_mean']
        model._y_std = payload['y_std']
        return model


# ── temperature calibration (E8) ─────────────────────────────────────────
class TemperatureCalibrator:
    """Per-slice temperature scaling, fitted on the VALID split only.

    p -> p^(1/tau) / normalisation (log-prob scaling).  tau is found by a
    deterministic coarse grid + golden-section refine minimising the
    validation log loss — pure Python, bit-reproducible.  A slice keeps
    its tau only if it improves that slice's log loss; otherwise tau = 1
    (honest no-op)."""

    GRID = (0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.5, 1.75, 2.0,
            2.5, 3.0, 4.0)

    def __init__(self, global_tau=1.0, slice_taus=None, before=None,
                 after=None):
        self.global_tau = global_tau
        self.slice_taus = dict(slice_taus or {})
        self.before = before
        self.after = after

    @staticmethod
    def _scale(probs, tau):
        if tau == 1.0:
            return list(probs)
        logs = [math.log(max(p, 1e-15)) / tau for p in probs]
        mx = max(logs)
        exps = [math.exp(v - mx) for v in logs]
        z = sum(exps)
        return [e / z for e in exps]

    @staticmethod
    def _logloss(y_true, probs):
        total = 0.0
        for t, p in zip(y_true, probs):
            total -= math.log(max(p[t], 1e-15))
        return total / max(len(y_true), 1)

    def transform(self, probs, slice_key=None):
        tau = self.slice_taus.get(slice_key, self.global_tau) \
            if slice_key else self.global_tau
        return self._scale(probs, tau)

    def fit(self, y_true, probs, slice_keys):
        """Grid + golden refine per slice and globally; keeps a tau only
        when it beats tau = 1 on the same data."""
        def best_tau(idx):
            yt = [y_true[i] for i in idx]
            pt = [probs[i] for i in idx]
            base = self._logloss(yt, pt)

            def ll(tau):
                return self._logloss(yt, [self._scale(p, tau) for p in pt])
            grid = min(self.GRID, key=lambda t: (ll(t), t))
            lo, hi = grid / 1.125 ** 2, grid * 1.125 ** 2
            phi = (math.sqrt(5.0) - 1.0) / 2.0
            a, b = lo, hi
            c, dd = b - phi * (b - a), a + phi * (b - a)
            fc, fd = ll(c), ll(dd)
            for _ in range(24):
                if fc < fd:
                    b, dd, fd = dd, c, fc
                    c = b - phi * (b - a)
                    fc = ll(c)
                else:
                    a, c, fc = c, dd, fd
                    dd = a + phi * (b - a)
                    fd = ll(dd)
            tau = (a + b) / 2.0
            refined = ll(tau)
            if refined < base - 1e-9:
                return tau, base, refined
            return 1.0, base, base

        per_slice = {}
        for key in sorted(set(slice_keys)):
            idx = [i for i, s in enumerate(slice_keys) if s == key]
            if len(idx) < 30:                 # too small to calibrate honestly
                continue
            tau, _before, _after = best_tau(idx)
            per_slice[key] = tau
        gtau, gbefore, gafter = best_tau(list(range(len(y_true))))
        # honest "after": apply the chosen scheme (slice tau where fitted,
        # global tau elsewhere) to the whole validation set
        applied = []
        for i, s in enumerate(slice_keys):
            applied.append(self._scale(probs[i], per_slice.get(s, gtau)))
        after_all = self._logloss(y_true, applied)
        self.before = round(gbefore, 6)
        self.after = round(min(gafter, after_all), 6)
        self.global_tau = gtau
        self.slice_taus = per_slice
        return self

    def to_json(self):
        return {'global_tau': self.global_tau,
                'slice_taus': self.slice_taus,
                'valid_logloss_before': self.before,
                'valid_logloss_after': self.after}

    @classmethod
    def from_json(cls, payload):
        return cls(payload.get('global_tau', 1.0),
                   payload.get('slice_taus') or {},
                   payload.get('valid_logloss_before'),
                   payload.get('valid_logloss_after'))


# ── bootstrap ensemble (E8) ─────────────────────────────────────────────
class SoftmaxEnsemble:
    """Uniformly-weighted bag of SoftmaxRegression members.

    Bootstrap resamples are drawn from a seeded RNG (splitmix64-mixed
    member index) so the whole ensemble is bit-reproducible.  Members
    may be trained against soft targets (E8)."""

    def __init__(self, n_features, n_classes=3, members=3, l2=1e-4,
                 lr=0.1, epochs=40, momentum=0.9, seed=0):
        self.n_features = n_features
        self.n_classes = n_classes
        self.members = members
        self.l2, self.lr = l2, lr
        self.epochs, self.momentum = epochs, momentum
        self.seed = seed
        self.models = []

    def fit(self, X_raw, y, targets=None, sample_weight=None, verbose=False):
        import random
        n = len(X_raw)
        self.models = []
        for m in range(self.members):
            rng = random.Random((self.seed + 7919 * m) & 0xFFFFFFFFFFFFFFFF)
            idx = [rng.randrange(n) for _ in range(n)]
            Xb = [X_raw[i] for i in idx]
            yb = [y[i] for i in idx]
            tb = [targets[i] for i in idx] if targets is not None else None
            wb = ([sample_weight[i] for i in idx]
                  if sample_weight is not None else None)
            model = SoftmaxRegression(self.n_features, self.n_classes,
                                      l2=self.l2, lr=self.lr,
                                      epochs=self.epochs,
                                      momentum=self.momentum)
            model.fit(Xb, yb, targets=tb, sample_weight=wb)
            self.models.append(model)
            if verbose:
                print('    member %d final logloss %.6f'
                      % (m, model.loss_history[-1]))
        return self

    def predict_proba_raw(self, X_raw):
        if not self.models:
            raise RuntimeError('ensemble is not fitted')
        per = [mdl.predict_proba_raw(X_raw) for mdl in self.models]
        out = []
        for i in range(len(X_raw)):
            acc = [0.0] * self.n_classes
            for probs in per:
                for k in range(self.n_classes):
                    acc[k] += probs[i][k]
            out.append([v / len(per) for v in acc])
        return out

    def to_json(self):
        return {'members': self.members, 'seed': self.seed,
                'models': [m.to_json() for m in self.models]}

    @classmethod
    def from_json(cls, payload, n_features, n_classes=3):
        ens = cls(n_features, n_classes, members=payload['members'],
                  seed=payload['seed'])
        ens.models = [SoftmaxRegression.from_json(mp, n_features, n_classes)
                      for mp in payload['models']]
        return ens


# ── model file I/O ───────────────────────────────────────────────────────
def save_model(path, payload):
    payload = dict(payload)
    payload['format'] = MODEL_FORMAT
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    return path


def load_model(path):
    with open(path, 'r', encoding='utf-8') as fh:
        payload = json.load(fh)
    if payload.get('format') not in MODEL_FORMATS:
        raise ValueError('not an outcome model file: %r' % (path,))
    return payload
