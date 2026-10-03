#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export theorem content to JSON for the docx-js generator."""
import json
import os
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
from content_theorems_1 import THEOREMS_PART1  # noqa: E402
from content_theorems_2 import THEOREMS_PART2  # noqa: E402
from content_theorems_3 import THEOREMS_PART3  # noqa: E402

out = os.path.join(os.path.dirname(SRC), 'build', 'docx_data.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
data = {'theorems': THEOREMS_PART1 + THEOREMS_PART2 + THEOREMS_PART3}
with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print('exported %d theorems -> %s' % (len(data['theorems']), out))
