"""HODGE-INPUT v1 — the input grammar (WP1) and its parser.

The decision problem VER-HODGE(C_i, p) takes a (variety, Hodge
class) pair packed as a JSON document.  The grammar has FOUR input
levels:

  Level 0  the variety is a Fermat stand: identified by the pair
           (N, m) — Fermat curve/hypersurface data where the exact
           layer is fully computable (census, Shioda/Gamma layer);
  Level 1  the variety is given by an EQUATION with rational (or
           one-parameter rational) coefficients — the Dwork pencil
           is the first instance;
  Level 2  full intersections / general smooth hypersurfaces;
  Level 3  arbitrary projective varieties with certified Hodge
           classes (out of scope for v1.8 — the parser REJECTS
           level-3 documents with NOT-DETERMINED, never with a
           fabricated verdict).

The asymmetric output contract: a run ends in ALGEBRAIC_CERTIFICATE
or NOT_DETERMINED.  The parser never emits a verdict that the input
level cannot support.

A parsed document is CANONICALIZED (key order, normalized
fractions) and hashed (sha256) — the hash is the provenance record
that the claim registry and the Lean layer cite.
"""

from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from . import VERDICT_CERTIFICATE, VERDICT_NOT_DETERMINED

SCHEMA_VERSION = "HODGE-INPUT v1"

LEVEL_NAMES = {
    0: "fermat-stand",
    1: "equation-pencil",
    2: "general-hypersurface",
    3: "arbitrary-certified",
}


class InputError(ValueError):
    """Malformed HODGE-INPUT document (grammar violation)."""


# ──────────────────────────────────────────────────────────────────────
# Primitive parsers
# ──────────────────────────────────────────────────────────────────────

def _parse_q(v: Any, path: str) -> Fraction:
    """A rational number: int, 'p/q' string, or [p, q] pair."""
    if isinstance(v, bool):
        raise InputError(f"{path}: booleans are not rationals")
    if isinstance(v, int):
        return Fraction(v)
    if isinstance(v, str):
        s = v.strip()
        m = re.fullmatch(r"(-?\d+)\s*/\s*(\d+)", s)
        if m:
            fr = Fraction(int(m.group(1)), int(m.group(2)))
            return fr
        m = re.fullmatch(r"-?\d+", s)
        if m:
            return Fraction(int(s))
        raise InputError(f"{path}: not a rational literal: {v!r}")
    if isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) for x in v):
        if v[1] == 0:
            raise InputError(f"{path}: zero denominator")
        return Fraction(v[0], v[1])
    raise InputError(f"{path}: not a rational: {v!r}")


def _q_json(fr: Fraction) -> Any:
    """Canonical JSON form of a rational: int when integral."""
    if fr.denominator == 1:
        return int(fr)
    return f"{fr.numerator}/{fr.denominator}"


def _require(doc: Dict, key: str, path: str):
    if key not in doc:
        raise InputError(f"{path}: missing required key '{key}'")
    return doc[key]


# ──────────────────────────────────────────────────────────────────────
# The parser
# ──────────────────────────────────────────────────────────────────────

def parse_hodge_input(raw: Any) -> Dict:
    """Parse and validate a HODGE-INPUT v1 document.

    Accepts a JSON string or an already-loaded dict.  Returns the
    normalized document (canonical form + provenance hash).
    """
    if isinstance(raw, (str, bytes)):
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as e:
            raise InputError(f"invalid JSON: {e}") from e
    elif isinstance(raw, dict):
        doc = raw
    else:
        raise InputError("document must be a JSON string or a dict")

    if not isinstance(doc, dict):
        raise InputError("top level must be an object")

    out: Dict[str, Any] = {}
    out["schema"] = str(_require(doc, "schema", "$"))
    if out["schema"] != SCHEMA_VERSION:
        raise InputError(f"schema must be {SCHEMA_VERSION!r}, "
                         f"got {out['schema']!r}")

    # ---- variety -----------------------------------------------------
    var = _require(doc, "variety", "$")
    if not isinstance(var, dict):
        raise InputError("variety: must be an object")
    kind = str(_require(var, "kind", "variety"))

    if kind == "fermat-stand":
        n = _require(var, "N", "variety")
        m = _require(var, "m", "variety")
        if not isinstance(n, int) or isinstance(n, bool) or n < 3:
            raise InputError("variety.N: integer >= 3 required")
        if not isinstance(m, int) or isinstance(m, bool) or m < 1:
            raise InputError("variety.m: positive integer required")
        # a Fermat STAND is Level 0; N carries the cyclotomic level
        level = 0
        out["variety"] = {
            "kind": "fermat-stand", "level": level,
            "N": n, "m": m,
        }
    elif kind == "dwork-pencil":
        psi_raw = _require(var, "psi", "variety")
        psi = _parse_q(psi_raw, "variety.psi")
        if psi == 0:
            # the Fermat fiber itself — still Level 1 (an equation),
            # but flagged: singular fibers psi^5 = 1 are pre-screened
            pass
        level = 1
        out["variety"] = {
            "kind": "dwork-pencil", "level": level,
            "psi": _q_json(psi),
            "singular_fiber": bool(psi ** 5 == 1),
        }
    elif kind == "hypersurface":
        # Level 2: general equation with rational coefficients
        deg = _require(var, "degree", "variety")
        coeffs = _require(var, "coefficients", "variety")
        if not isinstance(deg, int) or isinstance(deg, bool) or deg < 1:
            raise InputError("variety.degree: positive integer required")
        if not isinstance(coeffs, dict):
            raise InputError("variety.coefficients: object required")
        norm = {str(k): _q_json(_parse_q(v, f"variety.coefficients.{k}"))
                for k, v in sorted(coeffs.items())}
        level = 2
        out["variety"] = {
            "kind": "hypersurface", "level": level,
            "degree": deg, "coefficients": norm,
        }
    elif kind == "arbitrary-certified":
        # Level 3: accepted ONLY with proof_ref; verdict stays
        # NOT_DETERMINED downstream (never a fabricated certificate)
        pref = _require(var, "proof_ref", "variety")
        if not isinstance(pref, str) or not pref:
            raise InputError("variety.proof_ref: non-empty string required")
        level = 3
        out["variety"] = {
            "kind": "arbitrary-certified", "level": level,
            "proof_ref": pref,
        }
    else:
        raise InputError(f"variety.kind: unknown kind {kind!r}")

    # ---- hodge_class --------------------------------------------------
    hc = _require(doc, "hodge_class", "$")
    if not isinstance(hc, dict):
        raise InputError("hodge_class: must be an object")
    basis = str(_require(hc, "basis", "hodge_class"))
    if basis not in ("gamma-monomial", "line-combination", "cycle",
                     "residue-form", "symbolic"):
        raise InputError(f"hodge_class.basis: unknown basis {basis!r}")
    hout: Dict[str, Any] = {"basis": basis}
    if "data" in hc:
        hout["data"] = hc["data"]
    if "level" in hc:
        hl = hc["level"]
        if not isinstance(hl, int) or isinstance(hl, bool):
            raise InputError("hodge_class.level: integer required")
        hout["level"] = hl
    out["hodge_class"] = hout

    # ---- verification request ----------------------------------------
    ver = _require(doc, "verification", "$")
    if not isinstance(ver, dict):
        raise InputError("verification: must be an object")
    vout: Dict[str, Any] = {}
    typ = str(_require(ver, "type", "verification"))
    if typ not in ("census", "exact-layer", "snf", "rank",
                   "cycle-certificate", "gross-normalization",
                   "period", "point-count"):
        raise InputError(f"verification.type: unknown type {typ!r}")
    vout["type"] = typ
    if "params" in ver:
        if not isinstance(ver["params"], dict):
            raise InputError("verification.params: object required")
        vout["params"] = {
            str(k): _q_json(_parse_q(v, f"verification.params.{k}"))
            if isinstance(v, (int, str, list)) and not isinstance(v, bool)
            else v
            for k, v in sorted(ver["params"].items())
        }
    vout["dps"] = int(ver.get("dps", 40))
    out["verification"] = vout

    # ---- provenance (optional) ----------------------------------------
    if "provenance" in doc:
        prov = doc["provenance"]
        if not isinstance(prov, dict):
            raise InputError("provenance: must be an object")
        out["provenance"] = {str(k): prov[k] for k in sorted(prov)}

    return canonicalize(out)


def canonicalize(doc: Dict) -> Dict:
    """Canonical form: sorted keys, normalized numbers."""
    return json.loads(json.dumps(doc, sort_keys=True, separators=(",", ":")))


def provenance_hash(doc: Dict) -> str:
    """sha256 of the canonical form — the Lean-auditable record."""
    canon = json.dumps(canonicalize(doc), sort_keys=True,
                       separators=(",", ":")).encode()
    return hashlib.sha256(canon).hexdigest()


# ──────────────────────────────────────────────────────────────────────
# Level gating — the honest dispatch table
# ──────────────────────────────────────────────────────────────────────

SUPPORTED = {
    # (variety kind, verification type) -> runner name
    ("fermat-stand", "census"): "run_census",
    ("fermat-stand", "exact-layer"): "run_exact_layer",
    ("fermat-stand", "gross-normalization"): "run_gross",
    ("fermat-stand", "snf"): "run_snf_stand",
    ("dwork-pencil", "period"): "run_dwork_period",
    ("dwork-pencil", "point-count"): "run_dwork_pointcount",
}


def dispatch(doc: Dict) -> Tuple[Optional[str], str]:
    """Return (runner, verdict-class) honoring the asymmetric contract.

    A supported pair yields ('run_...', 'ALGEBRAIC_CERTIFICATE' on
    success).  An unsupported pair yields (None, 'NOT_DETERMINED') —
    the parser NEVER promises a verdict the level cannot carry.
    """
    kind = doc["variety"]["kind"]
    typ = doc["verification"]["type"]
    runner = SUPPORTED.get((kind, typ))
    if runner is None:
        return None, VERDICT_NOT_DETERMINED
    return runner, VERDICT_CERTIFICATE
