#!/usr/bin/env python3
"""engine/analyzer.py — position analysis: fields, mobility, energy (CLI).

    python3 engine/analyzer.py --fen "FEN" [--json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402
from particles import ThreeLayerModel                       # noqa: E402


def analyze(fen):
    """Full analysis report of a position (JSON-ready dict)."""
    pos = D.Position().set_fen(fen)
    valid, why = pos.is_valid()
    layers = ThreeLayerModel().analyze(pos)
    return {
        'fen': pos.to_fen(),
        'valid': valid,
        'validity': why,
        'side_to_move': 'white' if pos.side == 1 else 'black',
        'in_check': pos.in_check(pos.side) if valid else None,
        'zobrist': '0x%016X' % pos.hash,
        'energy': {
            'energy_white_view': layers['torus']['energy_white_view'],
            'mobility_white': layers['torus']['mobility_white'],
            'mobility_black': layers['torus']['mobility_black'],
            'material_white': layers['torus']['material_white'],
            'material_black': layers['torus']['material_black'],
        },
        'threat_field': {
            'mass_white': layers['K3']['threat_mass']['white'],
            'mass_black': layers['K3']['threat_mass']['black'],
            'grid_white': layers['K3']['grid_white'],
        },
        'flow': layers['klein'],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description='Position analyzer')
    ap.add_argument('--fen', default=D.START_FEN)
    args = ap.parse_args(argv)
    print(json.dumps(analyze(args.fen), indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
