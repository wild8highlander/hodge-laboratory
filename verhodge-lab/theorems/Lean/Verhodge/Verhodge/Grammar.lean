/-!
# HODGE-INPUT v1 — the input grammar as inductive types (roadmap WP4, increment 1)

The Lean layer machine-checks the DISCRETE part of the grammar: the
level taxonomy and the malformed-document rejection.  The Python
parser (verhodge/input_schema.py) is the executable reference; this
file is the auditable specification of what it accepts.

No axioms, no Mathlib: kernel-only.
-/

namespace Verhodge

/-- The four input levels of HODGE-INPUT v1. -/
inductive Level where
  | fermatStand          : Level   -- Level 0
  | equationPencil       : Level   -- Level 1
  | generalHypersurface  : Level   -- Level 2
  | arbitraryCertified   : Level   -- Level 3

/-- The verification request types accepted by the dispatch table. -/
inductive VerifType where
  | census | exactLayer | snf | rank | cycleCertificate
  | grossNormalization | period | pointCount

/-- A Hodge class basis name. -/
inductive Basis where
  | gammaMonomial | lineCombination | cycle | residueForm | symbolic

/-- Grammar validity: the pairing (variety kind, verification type)
    is either in the dispatch table or the verdict is NOT_DETERMINED. -/
inductive Verdict where
  | algebraicCertificate : Verdict
  | notDetermined        : Verdict

/-- The dispatch: Level 0 pairs supported by the v1.8 runners. -/
def dispatch : Level → VerifType → Verdict
  | Level.fermatStand, VerifType.census              => Verdict.algebraicCertificate
  | Level.fermatStand, VerifType.exactLayer          => Verdict.algebraicCertificate
  | Level.fermatStand, VerifType.snf                 => Verdict.algebraicCertificate
  | Level.fermatStand, VerifType.grossNormalization  => Verdict.algebraicCertificate
  | Level.equationPencil, VerifType.period           => Verdict.algebraicCertificate
  | Level.equationPencil, VerifType.pointCount       => Verdict.algebraicCertificate
  | _, _                                             => Verdict.notDetermined

/-- THE ASYMMETRIC CONTRACT: level-3 inputs never yield a
    certificate, only NOT_DETERMINED. -/
theorem level3_never_certified (t : VerifType) :
    dispatch Level.arbitraryCertified t = Verdict.notDetermined := by
  cases t <;> rfl

/-- The malformed N (N < 3) is rejected by construction: the grammar
    type does not contain it (N : Nat with a hypothesis N ≥ 3). -/
structure FermatStandInput where
  N : Nat
  m : Nat
  hN : N ≥ 3
  hm : m ≥ 1

end Verhodge
