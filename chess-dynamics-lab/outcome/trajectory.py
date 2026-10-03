#!/usr/bin/env python3
"""outcome/trajectory.py — the trajectory model (Epoch V).

The state-level model of Epoch III answers "what is the field of this
position?".  Epoch V answers the temporal question:

    "how does the field *evolve* along a game line, and does knowing
    the line's history sharpen the forecast?"

Lines are sampled from the frozen certificates by seeded walks:

*  won roots        — the strong side plays the DTM-optimal move
                      (min child DTM on its turn), the weak side plays
                      the best defence (max child DTM); the walk follows
                      exact best play until mate, a domain exit (bare
                      kings) or the horizon;
*  drawn roots      — a seeded random walk with the same horizon: draws
                      have no direction, and pretending otherwise would
                      be dishonest;
*  domain crossings — KPK promotions are followed INTO the KQK
                      certificate, so one line may traverse two domains
                      (the only multi-domain instrument in the repo).

Model (zero-dependency, bit-reproducible): a gated pooling recurrent
unit.  Each step contributes its phase-space vector with a learned gate

    g_t = sigmoid(a0 + a1·(t/T) + a2·(dtm_t/cap))       (3 parameters)

the pooled state is the gate-weighted mean of the (standardised) step
vectors, and a linear softmax head on [pooled, final vector] forecasts
the *final* outcome class of the line.  Full-batch GD with momentum,
L2 on the head only.  The gradient of the gate is exact: pooling is a
weighted mean, so dL/dg_t follows from one scalar projection.

The scientific payload is the ablation the plan demanded:

    gated model   (history pooling)  vs  final-only model (no history)

evaluated as a FORECAST CURVE: accuracy of the outcome forecast made
from the first t plies only.  If the gated curve beats the final-only
curve at small t, history carries information beyond the current
position — that is the whole claim, and it is measured, not asserted.
"""
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import context as CTX                          # noqa: E402
from outcome import dataset as DS                           # noqa: E402
from outcome import features as F                           # noqa: E402
from outcome import metrics as MT                           # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402

DEFAULT_HORIZON = 40          # plies per line
DTM_CAP = 64.0                # gate input normalisation for DTM inputs
FORECAST_TS = (0, 1, 2, 3, 5, 10, 20)


def pos_to_quad(pos):
    """(kind, wk, piece_sq, bk, stm) of a position inside the oracle
    space; ('kk', ...) for bare kings; (None, ...) outside the space."""
    kind = T.detect_domain(pos)
    if kind is None:
        n = sum(1 for sq in D.SQUARES if pos.board[sq] != D.EMPTY)
        if n == 2:
            return 'kk', None, None, None, None
        return None, None, None, None, None
    wk = pos.king_sq(1)
    bk = pos.king_sq(-1)
    piece_sq = None
    for sq in D.SQUARES:
        if pos.board[sq] == T.KIND_PIECE_CODE[kind]:
            piece_sq = sq
            break
    stm = 0 if pos.side == 1 else 1
    return kind, wk, piece_sq, bk, stm


def walk_line(kind, quad, rng, horizon=DEFAULT_HORIZON):
    """One seeded line from a root state, following the frozen values.

    Returns {'root_kind', 'game_id', 'steps', 'final_cls', 'n_plies'}
    where each step is {'kind', 'fen', 'cls', 'dtm', 'stm', 'vec'}."""
    wk, wp, bk, stm = quad
    game_id = T.pack(kind, wk, wp, bk, stm) \
        + DS.KINDS_INDEX[kind] * (1 << 22)
    fen = T.state_to_fen(kind, wk, wp, bk, stm)
    pos = D.Position().set_fen(fen)
    steps = []
    final_cls = None
    for t in range(horizon + 1):
        k, wkq, psq, bkq, stmq = pos_to_quad(pos)
        if k == 'kk':
            final_cls = T.DRAW
            break
        if k is None:
            break                              # left the oracle space
        probe = T.probe_state(k, wkq, psq, bkq, stmq)
        steps.append({'kind': k, 'fen': pos.to_fen(),
                      'cls': probe['cls'], 'dtm': probe['dtm_plies'],
                      'stm': stmq, 'vec': F.extract_vector(pos)})
        if probe['dtm_plies'] == 0:
            final_cls = T.WHITE_WIN            # black is mated: game over
            break
        if t == horizon:
            final_cls = probe['cls']
            break
        # ── gather the children (probe each, then unmake) ────────────
        children = []                          # (move, won, dtm)
        for m in pos.legal_moves():
            undo = pos.make(m)
            ck, cwk, cps, cbk, cstm = pos_to_quad(pos)
            if ck == 'kk':
                children.append((m, False, None))     # piece fell: K vs K
                pos.unmake(undo)
                continue
            if ck is None:
                pos.unmake(undo)
                continue
            cp = T.probe_state(ck, cwk, cps, cbk, cstm)
            pos.unmake(undo)
            if not cp['legal']:
                continue
            won = cp['outcome'] == 'white_win'
            children.append((m, won, cp['dtm_plies'] if won else None))
        if not children:
            final_cls = probe['cls']           # stalemate on the board
            break
        # ── the policy ───────────────────────────────────────────────
        if probe['cls'] == T.WHITE_WIN and stmq == 0:
            won = [c for c in children if c[1]]         # attacker: min DTM
            move = (min(won, key=lambda c: (c[2], D.move_to_uci(c[0])))
                    if won else rng.choice(children))
        elif probe['cls'] == T.WHITE_WIN:
            won = [c for c in children if c[1]]         # defender: max DTM
            move = (max(won, key=lambda c: (c[2], D.move_to_uci(c[0])))
                    if won else rng.choice(children))
        else:
            move = rng.choice(children)        # drawn: seeded wander
        undo = pos.make(move[0])
    return {'root_kind': kind, 'game_id': game_id, 'steps': steps,
            'final_cls': final_cls, 'n_plies': len(steps) - 1}


def sample_lines(kinds, n_per_kind, seed=DS.DEFAULT_SEED,
                 horizon=DEFAULT_HORIZON, log=None):
    """Seeded trajectory sample per kind; roots come from the same
    rejection sampler as the state datasets (deterministic)."""
    lines = []
    for ki, kind in enumerate(kinds):
        t0 = time.time()
        quads = DS.sample_states(kind, n_per_kind, seed + 104729 * ki)
        for qi, quad in enumerate(quads):
            rng = random.Random((seed + 104729 * ki) * 2625271 + qi)
            lines.append(walk_line(kind, quad, rng, horizon))
        if log:
            won = sum(1 for L in lines[-len(quads):]
                      if L['final_cls'] == T.WHITE_WIN)
            avg = sum(L['n_plies'] for L in lines[-len(quads):]) \
                / max(len(quads), 1)
            log('  %-4s %d lines  (%.1f%% end in mate, avg %.1f plies) '
                '%.1fs' % (kind, len(quads), 100.0 * won / max(len(quads), 1),
                           avg, time.time() - t0))
    return lines


# ── the model ────────────────────────────────────────────────────────────
def _sigmoid(v):
    if v >= 0:
        return 1.0 / (1.0 + math.exp(-v))
    e = math.exp(v)
    return e / (1.0 + e)


def _softmax3(z):
    mx = max(z)
    exps = [math.exp(v - mx) for v in z]
    s = sum(exps)
    return [e / s for e in exps]


def gate_features(steps):
    """Per-step gate inputs [t/T, dtm/cap]: absolute (not per-line) so a
    prefix forecast sees exactly the same inputs as the full line."""
    G = []
    for t, st in enumerate(steps):
        dtm = st['dtm'] if st['dtm'] is not None else -1
        G.append([t / float(DEFAULT_HORIZON), dtm / DTM_CAP])
    return G


def build_sequences(lines):
    """Lines -> model sequences {'X', 'G', 'y', 'game_id', 'root_kind'}."""
    seqs = []
    for L in lines:
        X = [st['vec'] for st in L['steps']]
        seqs.append({'X': X, 'G': gate_features(L['steps']),
                     'y': L['final_cls'], 'game_id': L['game_id'],
                     'root_kind': L['root_kind']})
    return seqs


class TrajectoryModel:
    """Gated pooling over the steps of a line + linear softmax head.

    pool='gated' — the full model (history counts, gate-weighted);
    pool='final' — the ablation twin: only the final step is used, the
                   rest of the line is ignored (no history)."""

    def __init__(self, dim, pool='gated', epochs=30, lr=0.3, momentum=0.9,
                 l2=1e-4):
        self.dim = dim
        self.pool = pool
        self.epochs = epochs
        self.lr = lr
        self.momentum = momentum
        self.l2 = l2
        self.a = [0.0, 0.0, 0.0]               # gate: bias, t/T, dtm/cap
        self.W = [[0.0] * (2 * dim + 1) for _ in range(3)]
        self.mu, self.sd = None, None          # step standardisation
        self.loss_history = []

    # ── internals ────────────────────────────────────────────────────
    def _fit_standardizer(self, seqs):
        n = sum(len(s['X']) for s in seqs)
        d = self.dim
        mu = [0.0] * d
        for s in seqs:
            for row in s['X']:
                for j in range(d):
                    mu[j] += row[j]
        mu = [m / n for m in mu]
        sd = [0.0] * d
        for s in seqs:
            for row in s['X']:
                for j in range(d):
                    dv = row[j] - mu[j]
                    sd[j] += dv * dv
        sd = [math.sqrt(v / n) for v in sd]
        self.mu, self.sd = mu, [v if v > 1e-9 else 1.0 for v in sd]

    def _std(self, row):
        return [(row[j] - self.mu[j]) / self.sd[j] for j in range(self.dim)]

    def _gates(self, G):
        if self.pool == 'final':
            return [0.0] * (len(G) - 1) + [1.0]
        return [_sigmoid(self.a[0] + self.a[1] * g[0] + self.a[2] * g[1])
                for g in G]

    def _pool(self, Z, gates):
        gt = sum(gates)
        if gt <= 1e-12:
            gates = [1.0] * len(Z)
            gt = float(len(Z))
        pooled = [0.0] * self.dim
        for z, g in zip(Z, gates):
            w = g / gt
            for j in range(self.dim):
                pooled[j] += w * z[j]
        return pooled, gt, gates

    def _logits(self, pooled, final):
        flat = pooled + final + [1.0]
        out = []
        for k in range(3):
            wk = self.W[k]
            s = 0.0
            for j in range(len(flat)):
                s += wk[j] * flat[j]
            out.append(s)
        return out

    # ── training (full-batch GD, deterministic) ──────────────────────
    def fit(self, seqs, verbose=False):
        if self.mu is None:
            self._fit_standardizer(seqs)
        d2 = 2 * self.dim + 1
        va = [0.0, 0.0, 0.0]
        vW = [[0.0] * d2 for _ in range(3)]
        self.loss_history = []
        n = len(seqs)
        for epoch in range(self.epochs):
            ga = [0.0, 0.0, 0.0]
            gW = [[0.0] * d2 for _ in range(3)]
            loss = 0.0
            for s in seqs:
                Z = [self._std(row) for row in s['X']]
                gates = self._gates(s['G'])
                pooled, gt, gates = self._pool(Z, gates)
                final = Z[-1]
                probs = _softmax3(self._logits(pooled, final))
                y = s['y']
                loss -= math.log(max(probs[y], 1e-15))
                dpool = [0.0] * self.dim
                for k in range(3):
                    coeff = probs[k] - (1.0 if k == y else 0.0)
                    if coeff == 0.0:
                        continue
                    wk = self.W[k]
                    gk = gW[k]
                    for j in range(self.dim):
                        dpool[j] += coeff * wk[j]       # backprop to pooling
                        gk[j] += coeff * pooled[j]      # head grad (pooled)
                        gk[self.dim + j] += coeff * final[j]
                    gk[d2 - 1] += coeff
                if self.pool == 'gated':
                    for tix, z in enumerate(Z):
                        g = gates[tix]
                        dg = 0.0
                        for j in range(self.dim):
                            dg += (z[j] - pooled[j]) * dpool[j]
                        dg /= gt
                        gi = g * (1.0 - g)
                        ga[0] += dg * gi
                        ga[1] += dg * gi * s['G'][tix][0]
                        ga[2] += dg * gi * s['G'][tix][1]
            inv = 1.0 / n
            for k in range(3):
                gk, wk, vk = gW[k], self.W[k], vW[k]
                for j in range(d2):
                    gj = gk[j] * inv
                    if j < d2 - 1:
                        gj += self.l2 * wk[j]
                    vk[j] = self.momentum * vk[j] - self.lr * gj
                    wk[j] += vk[j]
            for i in range(3):
                va[i] = self.momentum * va[i] - self.lr * ga[i] * inv
                self.a[i] += va[i]
            self.loss_history.append(loss * inv)
            if verbose and (epoch % 5 == 0 or epoch == self.epochs - 1):
                print('    epoch %3d  logloss %.6f' % (epoch, loss * inv))
        return self

    # ── inference ────────────────────────────────────────────────────
    def predict_steps(self, X, G):
        """Forecast probabilities from an explicit (prefix) step list."""
        if self.mu is None:
            raise RuntimeError('trajectory model is not fitted')
        Z = [self._std(row) for row in X]
        gates = self._gates(G)
        pooled, _gt, _gates = self._pool(Z, gates)
        return _softmax3(self._logits(pooled, Z[-1]))

    def predict_prefix(self, X, G, t):
        """The forecast made after the first t+1 plies of the line."""
        k = min(t, len(X) - 1)
        return self.predict_steps(X[:k + 1], G[:k + 1])

    # ── persistence ──────────────────────────────────────────────────
    def to_json(self):
        return {'pool': self.pool, 'dim': self.dim, 'epochs': self.epochs,
                'lr': self.lr, 'momentum': self.momentum, 'l2': self.l2,
                'gate': self.a, 'head': self.W, 'mu': self.mu, 'sd': self.sd,
                'loss_history': self.loss_history}

    @classmethod
    def from_json(cls, payload):
        model = cls(payload['dim'], pool=payload['pool'],
                    epochs=payload['epochs'], lr=payload['lr'],
                    momentum=payload['momentum'], l2=payload['l2'])
        model.a = list(payload['gate'])
        model.W = [list(w) for w in payload['head']]
        model.mu, model.sd = list(payload['mu']), list(payload['sd'])
        model.loss_history = list(payload.get('loss_history', []))
        return model


# ── the experiment (certificate E9) ──────────────────────────────────────
def forecast_curve(model, seqs, ts=FORECAST_TS):
    """Accuracy of the forecast made from the first t plies only."""
    out = {}
    for t in ts:
        y_true, probs_all = [], []
        for s in seqs:
            probs_all.append(model.predict_prefix(s['X'], s['G'], t))
            y_true.append(s['y'])
        y_pred = [max(range(3), key=lambda k: p[k]) for p in probs_all]
        out[str(t)] = {'accuracy': round(MT.accuracy(y_true, y_pred), 6),
                       'log_loss': round(MT.log_loss(y_true, probs_all), 6),
                       'n': len(y_true)}
    return out


def surprise_rate(model, seqs):
    """Share of steps where the running forecast drops below 0.5 for the
    true final class — the drift alarm rate along the line."""
    flagged = total = 0
    for s in seqs:
        y = s['y']
        for t in range(len(s['X'])):
            probs = model.predict_prefix(s['X'], s['G'], t)
            total += 1
            if probs[y] < 0.5:
                flagged += 1
    return round(flagged / max(total, 1), 6)


def train_and_report(kinds, n_per_kind, seed=DS.DEFAULT_SEED,
                     horizon=DEFAULT_HORIZON, epochs=30, log=None):
    """The full Epoch V experiment: sample -> split by game -> fit the
    gated model and its final-only twin -> forecast curves -> drift."""
    log = log or print
    t0 = time.time()
    log('[1/4] sampling trajectory lines (horizon %d, seed %d)...'
        % (horizon, seed))
    lines = sample_lines(kinds, n_per_kind, seed, horizon, log)
    seqs = build_sequences(lines)
    splits = {'train': [], 'valid': [], 'test': []}
    for s in seqs:
        splits[CTX.split_of_game(s['game_id'])].append(s)
    log('  whole-game split: train %d / valid %d / test %d'
        % (len(splits['train']), len(splits['valid']),
           len(splits['test'])))
    dim = len(F.FEATURE_NAMES)

    log('[2/4] fitting the gated trajectory model...')
    gated = TrajectoryModel(dim, pool='gated', epochs=epochs)
    gated.fit(splits['train'], verbose=True)
    log('[4/4]... fitting the final-only twin (no-history ablation)...')
    finalonly = TrajectoryModel(dim, pool='final', epochs=epochs)
    finalonly.fit(splits['train'])

    log('[4/4] forecast curves on the test games...')
    curve_gated = forecast_curve(gated, splits['test'])
    curve_final = forecast_curve(finalonly, splits['test'])
    for t in FORECAST_TS:
        log('  t=%-2d  gated %.4f   final-only %.4f'
            % (t, curve_gated[str(t)]['accuracy'],
               curve_final[str(t)]['accuracy']))
    drift = {
        'gated': surprise_rate(gated, splits['test']),
        'final_only': surprise_rate(finalonly, splits['test']),
    }
    finals = {}
    for s in seqs:
        finals[s['y']] = finals.get(s['y'], 0) + 1
    report = {
        'program': 'Outcome Dynamics — trajectory model (epoch V)',
        'recipe': {'kinds': list(kinds), 'n_per_kind': n_per_kind,
                   'seed': seed, 'horizon': horizon, 'epochs': epochs,
                   'split': 'whole-game splitmix64(game_id) 70/15/10',
                   'feature_spec': F.FEATURE_SPEC},
        'model_gated': gated.to_json(),
        'model_final_only': finalonly.to_json(),
        'dataset': {
            'lines': len(seqs),
            'final_class_counts': {T.CLASS_NAMES[k]: v
                                   for k, v in sorted(finals.items())},
            'splits': {k: len(v) for k, v in splits.items()},
            'domain_crossings': sum(
                1 for L in lines
                if len(set(st['kind'] for st in L['steps'])) > 1),
        },
        'forecast_curve_gated': curve_gated,
        'forecast_curve_final_only': curve_final,
        'drift_surprise_rate': drift,
        'runtime_seconds': round(time.time() - t0, 1),
    }
    return report
