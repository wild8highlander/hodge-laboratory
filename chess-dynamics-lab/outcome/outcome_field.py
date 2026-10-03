#!/usr/bin/env python3
"""outcome/outcome_field.py — Outcome Field v0.2.

The central scientific object of the program: instead of a scalar
evaluation, every position maps to the outcome field

    F(x) = ( P(White wins), P(Draw), P(Black wins) )  +  uncertainty

Three prediction sources, strictly ordered (the Hybrid Oracle):

1.  EXACT — when the position lies in a frozen tablebase domain (now
    including the KBK diagonal negative control) the outcome is a
    theorem, probabilities are 0/1 and the entropy is 0.  The exact
    layer is never approximated away.
2.  MODEL — otherwise the phase-space vector feeds the frozen E8
    distillation model (results/outcome_model.json): softmax ensemble
    + oracle-shaped soft targets + the pooled temperature of the
    calibration layer.  The output is a calibrated distribution with
    an honest uncertainty.
3.  CONTEXT (Epoch IV) — an optional Bayesian player-context prior
    (rating gap, clock) is blended into the MODEL layer only.  The
    exact layer is never blended: a theorem has no prior.

Derived quantities
------------------
    entropy       H(F) in bits — "how unresolved is this position?"
    criticality   max over legal moves of |ΔP(white win)| — the largest
                  single-move collapse of the field
    move impact   the full counterfactual surface, delegated to the
                  dedicated outcome.impact module (v2)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import features as F                           # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402
from outcome import model as M                              # noqa: E402
from outcome import impact as IMP                           # noqa: E402
from outcome.impact import entropy_bits                     # noqa: E402,F401
from outcome import context as CTX                          # noqa: E402

DEFAULT_MODEL_PATH = os.path.join(T.RESULTS_DIR, 'outcome_model.json')

VERSION = '0.2'


class OutcomeField:
    """FEN -> (P_W, P_D, P_L) + entropy + criticality + move impact."""

    def __init__(self, model_path=None):
        path = model_path or DEFAULT_MODEL_PATH
        self.model_payload = None
        self._head = None
        self._ensemble = None
        self._calibrator = None
        self._names = None
        if os.path.exists(path):
            self.model_payload = M.load_model(path)
            self._names = self.model_payload['feature_names']
            payload = self.model_payload
            if payload.get('ensemble'):
                self._ensemble = M.SoftmaxEnsemble.from_json(
                    payload['ensemble'], len(self._names))
            elif payload.get('softmax'):
                self._head = M.SoftmaxRegression.from_json(
                    payload['softmax'], len(self._names))
            if payload.get('calibrator'):
                self._calibrator = M.TemperatureCalibrator.from_json(
                    payload['calibrator'])

    # ── the statistical layer ────────────────────────────────────────────
    def _model_probs(self, pos):
        """Model prediction; returns (probs, extrapolated)."""
        if self.model_payload is None:
            return None, False
        vec = F.extract_vector(pos, self._names)
        if self._ensemble is not None:
            probs = self._ensemble.predict_proba_raw([vec])[0]
        elif self._head is not None:
            probs = self._head.predict_proba_raw([vec])[0]
        else:
            return None, False
        probs = [float(p) for p in probs]
        # the pooled temperature of the E8 calibration layer; per-domain
        # taus live in the metrics layer where the slice is known
        if self._calibrator is not None:
            probs = self._calibrator.transform(probs)
        # extrapolation guard: outside the training envelope the model is
        # not calibrated - flag it honestly instead of faking confidence
        extrapolated = False
        envelope = self.model_payload.get('train_envelope') or {}
        if envelope:
            feats = F.vector_dict(vec, self._names)
            for name, (lo, hi) in envelope.items():
                if feats[name] < lo - 0.5 or feats[name] > hi + 0.5:
                    extrapolated = True
                    break
        return probs, extrapolated

    # ── the exact layer ──────────────────────────────────────────────────
    def _exact(self, pos):
        # bare kings: the classical insufficient-material theorem -
        # K vs K is a draw without any tablebase
        n_pieces = sum(1 for sq in D.SQUARES if pos.board[sq] != D.EMPTY)
        if n_pieces == 2:
            return 'kk', {'legal': True, 'outcome': 'draw',
                          'cls': T.DRAW, 'dtm_plies': None}
        kind = T.detect_domain(pos)
        if kind is None:
            return None
        wk = pos.king_sq(1)
        bk = pos.king_sq(-1)
        wp = None
        for sq in D.SQUARES:
            if pos.board[sq] == T.KIND_PIECE_CODE[kind]:
                wp = sq
                break
        stm = 0 if pos.side == 1 else 1
        probe = T.probe_state(kind, wk, wp, bk, stm)
        return kind, probe

    # ── public API ───────────────────────────────────────────────────────
    def predict(self, fen, with_moves=False, max_moves=64, context=None):
        """The Outcome Field of one position.

        `context` (optional, Epoch IV) is a player-context dict; see
        outcome.context.  It blends the MODEL layer only — the exact
        layer is never negotiated.  Probabilities are ordered
        (black_win, draw, white_win) to match CLASS_NAMES."""
        pos = D.Position().set_fen(fen)
        out = {'fen': pos.to_fen(), 'source': None, 'outcome': 'unknown',
               'domain': None, 'dtm_plies': None, 'probs': None,
               'entropy_bits': None, 'criticality': None,
               'uncertainty': None, 'extrapolation': False, 'moves': None,
               'context': None}

        exact = self._exact(pos)
        if exact is not None:
            kind, probe = exact
            out['domain'] = kind
            if not probe['legal']:
                out['source'] = 'exact'
                out['outcome'] = 'illegal'
                return out
            out['source'] = 'exact'
            out['outcome'] = probe['outcome']
            out['dtm_plies'] = probe['dtm_plies']
            probs = [0.0, 0.0, 0.0]
            probs[T.WHITE_WIN if probe['outcome'] == 'white_win' else T.DRAW] = 1.0
            out['probs'] = probs
            out['entropy_bits'] = 0.0
            out['uncertainty'] = 0.0
        else:
            probs, extrapolated = self._model_probs(pos)
            if probs is None:
                return out
            out['source'] = 'model'
            out['extrapolation'] = extrapolated
            if context is not None:
                ctx = CTX.PlayerContext.from_dict(context)
                probs, blend = CTX.blend(probs, ctx)
                out['context'] = blend
            best = max(range(3), key=lambda k: probs[k])
            out['outcome'] = T.CLASS_NAMES[best]
            out['probs'] = probs
            out['entropy_bits'] = round(entropy_bits(probs), 6)
            out['uncertainty'] = round(1.0 - max(probs), 6)

        if with_moves:
            pos = D.Position().set_fen(fen)
            rows = IMP.move_impact_surface(self, pos, max_moves)
            # v1 panel narrative: the biggest field LOSS first
            rows.sort(key=lambda e: (e['d_white_win'] is None,
                                     e['d_white_win'] if e['d_white_win']
                                     is not None else 0.0))
            out['moves'] = rows
            crit = 0.0
            worst = None
            for mv in rows:
                if mv['d_white_win'] is None:
                    continue
                delta = abs(mv['d_white_win'])
                if delta > crit:
                    crit, worst = delta, mv['uci']
            out['criticality'] = round(crit, 6)
            out['critical_move'] = worst
            out['impact_summary'] = IMP.summarize(rows, out['probs'],
                                                  out['dtm_plies']
                                                  if out['source'] == 'exact'
                                                  else None)
        return out

    # ── the ASCII panel (the interface of the plan §17) ──────────────────
    def panel(self, fen, with_moves=True, max_moves=12, context=None):
        out = self.predict(fen, with_moves=with_moves, max_moves=max_moves,
                           context=context)
        if out['probs'] is None:
            lines = ['Outcome Field v%s — no oracle for this position and '
                     'no frozen model found.' % VERSION,
                     'Run  python3 -m outcome train  first, or supply '
                     '--model.']
            return out, '\n'.join(lines)
        pw, pd, pl = out['probs'][T.WHITE_WIN], out['probs'][T.DRAW], \
            out['probs'][T.BLACK_WIN]
        lines = []
        lines.append('─' * 62)
        lines.append(' OUTCOME FIELD v%s' % VERSION)
        lines.append('─' * 62)
        lines.append(' FEN          %s' % out['fen'])
        if out['source'] == 'exact':
            src = ('%s · bare kings, insufficient material'
                   % out['domain'].upper()) if out['domain'] == 'kk' else (
                '%s · exact frozen tablebase' % out['domain'].upper())
        else:
            src = 'full chess · distilled outcome model'
            if out.get('context'):
                src += ' · %s' % out['context']['label']
        lines.append(' domain      %s' % src)
        if out['outcome'] == 'illegal':
            lines.append(' outcome     ILLEGAL POSITION')
            lines.append('─' * 62)
            return out, '\n'.join(lines)
        if out['outcome'] == 'white_win':
            text = 'WHITE WINS'
        elif out['outcome'] == 'draw':
            text = 'DRAW'
        else:
            text = 'BLACK WINS'
        if out['dtm_plies'] is not None:
            text += ' · mate in %d plies' % out['dtm_plies']
        lines.append(' outcome     %s' % text)
        lines.append(' field       P(white) %.3f   P(draw) %.3f   '
                     'P(black) %.3f' % (pw, pd, pl))
        lines.append(' entropy     %.3f bit' % (out['entropy_bits'] or 0.0))
        if out.get('extrapolation'):
            lines.append(' WARNING     outside the model training domain '
                         '(tablebase-only training data):')
            lines.append('             the probabilities are an '
                         'EXTRAPOLATION, not a calibrated forecast')
        if out.get('context'):
            b = out['context']
            lines.append(' context      %s' % b['label'])
            lines.append('              model expected score %.3f -> '
                         'blended %.3f (weight %.2f)'
                         % (b['model_expected'], b['blended_expected'],
                            b['weight']))
        if out['criticality'] is not None:
            lines.append(' criticality  %.3f   (critical move: %s)'
                         % (out['criticality'], out['critical_move'] or '—'))
            s = out.get('impact_summary') or {}
            if s.get('robustness_index') is not None:
                lines.append(' robustness   %.2f of moves keep the outcome '
                             'class · quiet share %.2f'
                             % (s['robustness_index'],
                                s.get('quiet_share') or 0.0))
        lines.append('─' * 62)
        if out['moves']:
            lines.append(' MOVE IMPACT  (ΔP white win; worst first)')
            lines.extend(IMP.ascii_table(out['moves'], limit=max_moves))
            lines.append('─' * 62)
        return out, '\n'.join(lines)
