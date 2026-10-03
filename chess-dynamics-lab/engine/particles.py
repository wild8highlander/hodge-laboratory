#!/usr/bin/env python3
"""engine/particles.py — the Three-Layer Particle Model (library wrapper).

Layer K3    (potential)  : threat fields emitted by the particles;
Layer TORUS (kinetic)    : Lagrangian energy and mobility;
Layer KLEIN (flow)       : discrete move flow t* and the damped billiard.

The heavy lifting is done by the single-file laboratory `dynamics.py`;
this module provides the object-oriented facade and a CLI:

    python3 engine/particles.py --fen "FEN"
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dynamics as D                                        # noqa: E402


class ThreeLayerModel:
    """Facade over the three particle layers of the monograph."""

    def __init__(self, gamma=None):
        self.gamma = gamma if gamma is not None else D.GAMMA_TORUS

    # ── Layer K3: threat fields ──────────────────────────────────────────
    def threat_field(self, pos, side):
        return D.threat_field(pos, side)

    def field_grid(self, pos, side):
        """8x8 grid (rank 8 first) of the K3 field of `side`."""
        theta = self.threat_field(pos, side)
        return [[theta[16 * r + f] for f in range(8)]
                for r in range(7, -1, -1)]

    # ── Layer TORUS: Lagrangian energy ───────────────────────────────────
    def energy(self, pos, side=1):
        return D.energy(pos, side)

    # ── Layer KLEIN: discrete flow ───────────────────────────────────────
    def tstar(self, a, b, W=8, H=8):
        return D.tstar(W, H, a, b)

    def billiard(self, a, b, W=8, H=8, steps=120):
        return D.simulate_billiard(W, H, a, b, self.gamma, max_steps=steps)

    # ── combined report ──────────────────────────────────────────────────
    def analyze(self, pos):
        theta_w = D.threat_field(pos, 1)
        theta_b = D.threat_field(pos, -1)
        return {
            'K3': {
                'threat_mass': {
                    'white': sum(theta_w[sq] for sq in D.SQUARES),
                    'black': sum(theta_b[sq] for sq in D.SQUARES)},
                'grid_white': self.field_grid(pos, 1),
            },
            'torus': {
                'mobility_white': D.mobility(pos, 1),
                'mobility_black': D.mobility(pos, -1),
                'material_white': D.material(pos, 1),
                'material_black': D.material(pos, -1),
                'energy_white_view': round(D.energy(pos, 1), 4),
            },
            'klein': {
                'tstar_8x8_king_rook_step': D.tstar(8, 8, 1, 1),
                'tstar_8x8_knight_step': D.tstar(8, 8, 1, 2),
                'gamma': self.gamma,
            },
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description='Three-layer particle model')
    ap.add_argument('--fen', default=D.START_FEN)
    args = ap.parse_args(argv)
    pos = D.Position().set_fen(args.fen)
    print(json.dumps(ThreeLayerModel().analyze(pos), indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
