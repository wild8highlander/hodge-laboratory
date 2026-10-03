#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the E7 rebuild provenance: every frozen DTM certificate must
be re-derivable, and the provenance artifact must say so."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

RESULTS = os.path.join(ROOT, 'results')


def _load(name):
    with open(os.path.join(RESULTS, name), 'r', encoding='utf-8') as fh:
        return json.load(fh)


def test_provenance_all_ok():
    rep = _load('dtm_rebuild_e7.json')
    assert rep['all_ok'] is True
    assert 'BIT-IDENTICAL' in rep['verdict']
    assert 'KBK ADDED' in rep['verdict']


def test_provenance_preexisting_domains_bit_identical():
    rep = _load('dtm_rebuild_e7.json')
    for kind in ('krk', 'kqk', 'knk', 'kpk'):
        entry = rep[kind]
        assert entry['stats_match'], kind
        assert entry['blob_bit_identical'], kind
        assert entry['bellman_verified_fresh'], kind
        assert entry['rebuilt_states'] > 0


def test_provenance_kbk_new_certificate():
    rep = _load('dtm_rebuild_e7.json')
    kbk = rep['kbk']
    assert kbk['bellman_verified_fresh'] is True
    assert kbk['stats']['won'] == 0
    assert kbk['stats']['mates'] == 0
    assert kbk['stats']['states'] == 417228
