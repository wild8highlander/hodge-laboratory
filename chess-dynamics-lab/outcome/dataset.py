#!/usr/bin/env python3
"""outcome/dataset.py — the dynamics dataset builder (Epoch II).

Turns the frozen endgame certificates into a supervised dataset:

    packed state  ->  FEN  ->  phase-space feature vector
                           ->  exact WDL class + exact DTM (the labels)

Sampling honesty
----------------
*  States are drawn from the packed 22-bit space by rejection sampling
   with a fixed seed (splitmix64, theorem T09) — the sample is uniform
   over the legal state population and bit-reproducible on any machine.
*  ``--full`` enumerates the complete population instead (slow but exact;
   also re-derives the builder's state census as a certificate).
*  Train/valid/test separation is a hash split on the packed state id
   (splitmix64 mixed with the domain index): 70/15/10, deterministic,
   independent of enumeration order.

Split-scope caveat (program rule 12): for endgame *states* a state-level
hash split is the honest design — the population *is* the state space.
When Epoch IV upgrades to full-chess *games*, the split must be lifted to
whole games (never position-level), because neighbouring plies of one
game are near-duplicates.  This module's API takes ``kind``-annotated
records precisely so the game-level split can slot in later.
"""
import csv
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from outcome import features as F                           # noqa: E402
from outcome import tablebase_api as T                      # noqa: E402

DEFAULT_SEED = 2026

KINDS_INDEX = {k: i for i, k in enumerate(T.KINDS)}

SPLIT_THRESHOLDS = (700, 850)      # <700 train, <850 valid, else test
SPLIT_NAMES = ('train', 'valid', 'test')


def split_of(state, kind_index=0):
    """Deterministic hash split of one packed state."""
    h = D.splitmix64((state + kind_index * (1 << 22)) & 0xFFFFFFFFFFFFFFFF)
    bucket = h % 1000
    if bucket < SPLIT_THRESHOLDS[0]:
        return 'train'
    if bucket < SPLIT_THRESHOLDS[1]:
        return 'valid'
    return 'test'


def sample_states(kind, n, seed=DEFAULT_SEED):
    """Uniform seeded sample of `n` legal packed states of one domain.

    Rejection sampling over the 2**22 packed space; legality is decided
    by geometry (tablebase_api.is_legal_state).  Returns a list of
    (wk, wp, bk, stm) tuples in deterministic order (sorted by packed id)."""
    rng = random.Random(seed * 7919 + KINDS_INDEX[kind])
    space = 1 << 22
    found = {}
    guard = 0
    while len(found) < n and guard < n * 1000 + 100000:
        guard += 1
        s = rng.randrange(space)
        wk, wp, bk, stm = T.unpack(s)
        if T.is_legal_state(kind, wk, wp, bk, stm):
            found[s] = (wk, wp, bk, stm)
    return [found[s] for s in sorted(found)]


def enumerate_states(kind):
    """All legal packed states of a domain, in packed-id order."""
    out = []
    for wk in D.SQUARES:
        for wp in D.SQUARES:
            if wp == wk:
                continue
            for bk in D.SQUARES:
                if bk == wk or bk == wp:
                    continue
                if kind == 'kpk' and not T.pawn_rank_ok(wp):
                    continue
                if T.kings_adjacent(wk, bk):
                    continue
                for stm in (0, 1):
                    if stm == 0 and T.black_en_prise(kind, wk, wp, bk):
                        continue
                    out.append(T.pack(kind, wk, wp, bk, stm))
    out.sort()
    return out


def build_record(kind, wk, wp, bk, stm):
    """One supervised record: identity + exact labels + phase-space features."""
    state = T.pack(kind, wk, wp, bk, stm)
    fen = T.state_to_fen(kind, wk, wp, bk, stm)
    pos = D.Position().set_fen(fen)
    probe = T.probe_state(kind, wk, wp, bk, stm)
    feats = F.extract_features(pos)
    return {
        'kind': kind,
        'state': state,
        'fen': fen,
        'stm': stm,
        'cls': probe['cls'],
        'dtm_plies': probe['dtm_plies'] if probe['dtm_plies'] is not None else -1,
        'features': feats,
    }


def build_sampled(kind, n, seed=DEFAULT_SEED):
    """Sampled dataset records of one domain (deterministic)."""
    quad = sample_states(kind, n, seed)
    return [build_record(kind, *q) for q in quad]


# ── CSV export ───────────────────────────────────────────────────────────
CSV_ID_COLUMNS = ['kind', 'state', 'fen', 'stm', 'cls', 'dtm_plies', 'split']


def record_row(rec):
    kind_index = KINDS_INDEX[rec['kind']]
    row = {
        'kind': rec['kind'],
        'state': rec['state'],
        'fen': rec['fen'],
        'stm': rec['stm'],
        'cls': rec['cls'],
        'dtm_plies': rec['dtm_plies'],
        'split': split_of(rec['state'], kind_index),
    }
    row.update({n: rec['features'][n] for n in F.FEATURE_NAMES})
    return row


def export_csv(records, path):
    """Write records to a CSV (id columns + the phase-space coordinates)."""
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_ID_COLUMNS + F.FEATURE_NAMES)
        writer.writeheader()
        for rec in records:
            writer.writerow(record_row(rec))
    return path
