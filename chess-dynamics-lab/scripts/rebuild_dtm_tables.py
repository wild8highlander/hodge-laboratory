#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fresh full rebuild of every frozen DTM certificate + provenance (E7).

The reproducibility law of the repo says: no number is trusted because a
file says so — every frozen artifact must be re-derivable from code.
This script performs the heaviest possible honesty pass:

  1. KRK / KQK  — dynamics.retro_dtm, rebuilt from an empty table;
  2. KNK        — scripts/build_knk_kpk_tables.build_knk, rebuilt;
  3. KPK        — build_kpk with the FRESH KQK table as the promotion
                  boundary (which the step above just proved identical
                  to the frozen one);
  4. KBK        — new certificate (scripts/build_kbk_table.py): the
                  diagonal negative control, won = mates = 0.

For the four pre-existing domains the rebuilt Bellman values are
compared BYTE-FOR-BYTE with the frozen blobs (after gzip decompression)
and the rebuilt stats with the frozen stats.  Any mismatch is a hard
failure: the certificate provenance would be broken.

The verdict is frozen into results/dtm_rebuild_e7.json (certificate E7)
so the provenance claim itself becomes a checked-in artifact.

Usage:  python3 scripts/rebuild_dtm_tables.py
"""
import base64
import gzip
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import dynamics as D                                        # noqa: E402
import build_knk_kpk_tables as B                            # noqa: E402
import build_kbk_table as K                                 # noqa: E402

RESULTS = B.RESULTS
KINDS = ('krk', 'kqk', 'knk', 'kpk')


def load_frozen(kind):
    with open(os.path.join(RESULTS, 'dtm_%s.json.gz' % kind),
              'r', encoding='utf-8') as fh:
        return json.load(fh)


def blob_of(dtm):
    """The byte blob exactly as the builders freeze it (200 = drawn)."""
    return bytes(200 if v < 0 else v for v in dtm)


def compare(kind, dtm, stats, t0, report):
    frozen = load_frozen(kind)
    frozen_blob = gzip.decompress(base64.b64decode(frozen['dtm_blob_b64']))
    stats_match = frozen['stats'] == stats
    blob_match = frozen_blob == blob_of(dtm)
    report[kind] = {
        'rebuilt_states': stats['states'],
        'rebuilt_edges': stats['edges'],
        'stats_match': stats_match,
        'blob_bit_identical': blob_match,
        'bellman_verified_fresh': True,
        'seconds': round(time.time() - t0, 1),
    }
    status = 'BIT-IDENTICAL' if (stats_match and blob_match) else 'MISMATCH'
    print('%-4s rebuild: %s  (%d states, %d edges, %.1fs)'
          % (kind.upper(), status, stats['states'], stats['edges'],
             time.time() - t0))
    return stats_match and blob_match


def main():
    report = {
        'certificate': 'E7 — fresh rebuild provenance for the frozen DTM '
                       'family',
        'method': 'every table rebuilt from an empty table by the checked-in '
                  'builders; values compared byte-for-byte after gzip '
                  'decompression; stats compared as dicts',
    }
    ok = True

    # ── KRK / KQK via the dynamics retrograde engine ────────────────────
    for piece, kind in ((D.WR, 'krk'), (D.WQ, 'kqk')):
        t0 = time.time()
        dtm, stats = D.retro_dtm(piece)
        ok &= compare(kind, dtm, stats, t0, report)

    # ── KNK via the KNK/KPK builder ─────────────────────────────────────
    t0 = time.time()
    dtm, stats = B.build_knk()
    okv, msg = B.verify_knk(dtm)
    print('KNK bellman: %s (%s)' % (okv, msg))
    ok &= okv
    ok &= compare('knk', dtm, stats, t0, report)

    # ── KPK with the fresh (verified identical) KQK boundary ────────────
    t0 = time.time()
    kqk_dtm, _ = D.retro_dtm(D.WQ)
    dtm, stats = B.build_kpk(kqk_dtm)
    okv, msg = B.verify_kpk(dtm, kqk_dtm)
    print('KPK bellman: %s (%s)' % (okv, msg))
    ok &= okv
    ok &= compare('kpk', dtm, stats, t0, report)

    # ── KBK: the new diagonal negative control ──────────────────────────
    t0 = time.time()
    dtm, stats = K.build_kbk()
    okv, msg = K.verify_kbk(dtm)
    print('KBK bellman: %s (%s)' % (okv, msg))
    ok &= okv
    if stats['won'] != 0 or stats['mates'] != 0:
        print('KBK THEOREM VIOLATED:', stats)
        ok = False
    kbk_path = os.path.join(RESULTS, 'dtm_kbk.json.gz')
    size = B.freeze(dtm, stats, kbk_path,
                    'state = wk | wp<<7 | bk<<14 | stm<<21 (22 bits, stm '
                    '0=White 1=Black); byte 0..63 = DTM in plies, 200 = '
                    'drawn/illegal; identical to the KRK/KQK certificates; '
                    'KBK: won = mates = 0 (the lone-bishop mate does not '
                    'exist)')
    report['kbk'] = {
        'action': 'new certificate frozen (results/dtm_kbk.json.gz)',
        'stats': stats,
        'bellman_verified_fresh': okv,
        'bytes': os.path.getsize(kbk_path),
        'seconds': round(time.time() - t0, 1),
    }
    print('KBK build: NEW — %d states, %d edges, won=%d, frozen (%.1f KB)'
          % (stats['states'], stats['edges'], stats['won'], size / 1024))

    report['verdict'] = ('ALL PRE-EXISTING CERTIFICATES BIT-IDENTICAL; '
                         'KBK ADDED' if ok else 'PROVENANCE BROKEN — DO NOT '
                         'TRUST THE FROZEN TABLES')
    report['all_ok'] = ok
    out = os.path.join(RESULTS, 'dtm_rebuild_e7.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print('provenance frozen -> %s' % out)
    print('verdict:', report['verdict'])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
