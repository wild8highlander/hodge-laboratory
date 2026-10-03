/-!
# The Smith normal form specification (roadmap WP4, increment 2)

The spec against which the Python engine's outputs are checked:
the divisibility chain and the certificate-H flagship identities.
The complexity claims stay OUTSIDE Lean (the ledger's jurisdiction).
-/

namespace Verhodge

/-- Divisibility inside the certificate-H tuple. -/
example : (5 : Nat) ∣ 15 ∧ 15 ∣ 15 := by decide

/-- The product of the invariant factors: 1*1*5*5*15^4 = 1265625. -/
example : 1 * 1 * 5 * 5 * 15 * 15 * 15 * 15 = 1265625 := by decide

/-- 1265625 = 1125^2 — the volume-discriminant agreement. -/
example : 1125 * 1125 = 1265625 := by decide

/-- 3^4 * 5^6 factorization agreement. -/
example : 3^4 * 5^6 = 1265625 := by decide

end Verhodge
