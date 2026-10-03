# chess-dynamics-lab · outcome — the Outcome Dynamics program (epochs I–VIII)
"""Exact outcome oracle, phase-space features, distillation, player
context, trajectory model, move impact, the falsification engine, the
nonlinear specialist heads and the whole-game referee.

Public API:

    tablebase_api   the exact WDL/DTM oracle over the frozen certificates
                    (KRK / KQK / KNK / KPK / KBK)
    features        the phase-space feature extractor (v2: 67 coordinates,
                    append-only over the frozen v1 block; no label leakage)
    dataset         deterministic sampled datasets with hash splits
    model           zero-dependency softmax/ridge heads, oracle-shaped
                    soft targets, bootstrap ensemble, temperature
                    calibration (E8)
    metrics         accuracy / logloss / Brier / ECE / macro-F1 / calibration
    outcome_field   Outcome Field v0.2 (exact-first probabilities, entropy,
                    criticality, context hook)
    impact          the counterfactual Move Impact surface (dedicated module)
    context         the Epoch IV Bayesian player-context layer + the
                    whole-game split rule
    trajectory      the Epoch V trajectory model and forecast curves
    falsify         the Epoch VI falsification engine (counterexamples/)
    nonlinear       the Epoch VII specialist heads (basis v2, E11/E13/E14)
    pgn / realgames the Epoch IV real-game pipeline (E12)
    adjudicate      the Epoch VIII whole-game referee (E15)

Command line:  python3 -m outcome --help
"""

VERSION = '2.2.0'

from outcome.tablebase_api import (BLACK_WIN, DRAW, WHITE_WIN, CLASS_NAMES,
                                   KINDS, classify_fen, probe_state)
from outcome.features import (FEATURE_NAMES, FEATURE_GROUPS, FEATURE_SPEC,
                              extract_features)
from outcome.outcome_field import OutcomeField

__all__ = ['VERSION', 'BLACK_WIN', 'DRAW', 'WHITE_WIN', 'CLASS_NAMES',
           'KINDS', 'classify_fen', 'probe_state', 'FEATURE_NAMES',
           'FEATURE_GROUPS', 'FEATURE_SPEC', 'extract_features',
           'OutcomeField']
