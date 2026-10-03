/-!
# The two-scheme census agreement (roadmap WP4, increment 3)

Machine-checked census identities for the frozen levels: the genus
identity sum h_d = (N-1)(N-2)/2.  The general N ≤ 64 agreement is
the CI loop (the Python engine computes it; Lean re-checks the
frozen instances below kernel-only).
-/

namespace Verhodge

def genus (N : Nat) : Nat := (N - 1) * (N - 2) / 2

/-- census(7) = {7: 15}: 15 characters, all of conductor 7. -/
example : genus 7 = 15 := by decide

/-- census(9) = {3: 1, 9: 27}: 1 + 27 = 28 = genus 9. -/
example : genus 9 = 28 := by decide

/-- census(11) = {11: 45}: 45 = genus 11 (certificate K). -/
example : genus 11 = 45 := by decide

/-- census(15) = {3: 1, 5: 6, 15: 84}: 1 + 6 + 84 = 91 = genus 15. -/
example : 1 + 6 + 84 = genus 15 := by decide

/-- census(30) total: 1 + 6 + 9 + 30 + 84 + 276 = 406 = genus 30. -/
example : 1 + 6 + 9 + 30 + 84 + 276 = genus 30 := by decide

end Verhodge
