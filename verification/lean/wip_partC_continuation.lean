
/-- Conductor form: `conductor N a b = d` says exactly that the triple
    gcd is `N / d` (for `d ∣ N`, `0 < N`). -/
theorem conductor_eq (N d a b : Nat) (hd : d ∣ N) (hN : 0 < N) :
    conductor N a b = d ↔ Nat.gcd (Nat.gcd a b) N = N / d := by
  have hd1 : 0 < d := by
    rcases Nat.eq_zero_or_pos d with h0 | h0
    · rw [h0, Nat.zero_dvd] at hd
      omega
    · exact h0
  constructor
  · intro h1
    have hgd : Nat.gcd (Nat.gcd a b) N ∣ N := Nat.gcd_dvd_right _ _
    have h2 : N = Nat.gcd (Nat.gcd a b) N * (N / Nat.gcd (Nat.gcd a b) N) :=
      Nat.mul_div_cancel' hgd
    rw [h1] at h2
    have h3 : d * (N / d) = Nat.gcd (Nat.gcd a b) N * d := by
      rw [Nat.mul_div_cancel' hd, h2]
    exact (Nat.mul_left_cancel hd1 h3).symm
  · intro h2
    have hg1 : 0 < Nat.gcd (Nat.gcd a b) N := by
      rcases Nat.eq_zero_or_pos (Nat.gcd a b) with h0 | h0
      · rw [h0, Nat.gcd_zero_left]
        exact hN
      · by_contra hz
        have hdv : Nat.gcd (Nat.gcd a b) N ∣ N := Nat.gcd_dvd_right _ _
        rw [hz] at hdv
        obtain ⟨c, hc⟩ := hdv
        rw [Nat.mul_zero] at hc
        omega
    have hN2 : N = d * Nat.gcd (Nat.gcd a b) N := by
      rw [h2, Nat.mul_div_cancel' hd]
    have hgd : Nat.gcd (Nat.gcd a b) N ∣ N := ⟨d, by rw [hN2, Nat.mul_comm]⟩
    have h4 : Nat.gcd (Nat.gcd a b) N * (N / Nat.gcd (Nat.gcd a b) N) = N :=
      Nat.mul_div_cancel' hgd
    rw [hN2] at h4
    exact Nat.mul_left_cancel hg1
      (by rw [h4, hN2, Nat.mul_comm d (Nat.gcd (Nat.gcd a b) N)])

/-- The scaling lemma: the conductor-`d` conditions at degree `N`
    (with `m = N/d`) are exactly the coprime conditions at level `d`. -/
theorem condCount_scale (N d : Nat) (hd : d ∣ N) (hN : 0 < N) :
    ∀ x y : Nat,
      (0 < (N / d) * x ∧ (N / d) * x < N ∧ 0 < (N / d) * y ∧ (N / d) * y < N
        ∧ ((N / d) * x + (N / d) * y) % N ≠ 0
        ∧ conductor N ((N / d) * x) ((N / d) * y) = d)
        ↔ (0 < x ∧ x < d ∧ 0 < y ∧ y < d ∧ (x + y) % d ≠ 0
          ∧ Nat.gcd (Nat.gcd x y) d = 1) := by
  have hmd : N / d * d = N := Nat.mul_div_cancel' hd
  have hmpos : 0 < N / d := by
    rcases Nat.eq_zero_or_pos (N / d) with h0 | h0
    · rw [h0, Nat.zero_mul] at hmd
      omega
    · exact h0
  have hmuly : ∀ y, 0 < (N / d) * y ↔ 0 < y := by
    intro y
    constructor
    · intro h
      rcases Nat.eq_zero_or_pos y with h0 | h0
      · rw [h0, Nat.mul_zero] at h
        omega
      · exact h0
    · intro h
      have h2 : (N / d) * 1 ≤ (N / d) * y := Nat.mul_le_mul_left _ h
      omega
  have hmulb : ∀ y, (N / d) * y < N ↔ y < d := by
    intro y
    constructor
    · intro h
      by_contra hz
      have h2 : (N / d) * d ≤ (N / d) * y := Nat.mul_le_mul_left _ hz
      omega
    · intro h
      by_contra hz
      have h2 : (N / d) * d ≤ (N / d) * y := Nat.mul_le_mul_left _ (by omega)
      omega
  have hdvdms : ∀ s, (N / d) * d ∣ (N / d) * s ↔ d ∣ s := by
    intro s
    constructor
    · rintro ⟨c, hc⟩
      rw [Nat.mul_assoc] at hc
      exact ⟨c, Nat.mul_left_cancel hmpos hc⟩
    · rintro ⟨c, hc⟩
      exact ⟨c, by rw [hc, Nat.mul_assoc]⟩
  intro x y
  constructor
  · rintro ⟨h1, h2, h3, h4, h5, h6⟩
    have hgx : Nat.gcd (Nat.gcd ((N / d) * x) ((N / d) * y)) N
        = (N / d) * Nat.gcd (Nat.gcd x y) d := by
      rw [Nat.gcd_mul_left, hmd, Nat.gcd_mul_left]
    have hcond : Nat.gcd (Nat.gcd ((N / d) * x) ((N / d) * y)) N = N / d :=
      (conductor_eq N d ((N / d) * x) ((N / d) * y) hd hN).1 h6
    have h1c : Nat.gcd (Nat.gcd x y) d = 1 :=
      Nat.mul_left_cancel hmpos
        (by rw [hgx.symm.trans hcond, Nat.mul_one (N / d)])
    have hmodne : (x + y) % d ≠ 0 := by
      intro hc
      rw [← hmd, ← Nat.mul_add (N / d) x y] at h5
      exact h5 (Nat.dvd_iff_mod_eq_zero.mp ((hdvdms (x + y)).2 hc))
    exact ⟨(hmuly x).1 h1, (hmulb x).1 h2, (hmuly y).1 h3, (hmulb y).1 h4, hmodne, h1c⟩
  · rintro ⟨h1, h2, h3, h4, h5, h6⟩
    have hgx : Nat.gcd (Nat.gcd ((N / d) * x) ((N / d) * y)) N
        = (N / d) * Nat.gcd (Nat.gcd x y) d := by
      rw [Nat.gcd_mul_left, hmd, Nat.gcd_mul_left]
    have hmodne : ((N / d) * x + (N / d) * y) % N ≠ 0 := by
      intro hc
      rw [← hmd, ← Nat.mul_add (N / d) x y] at hc
      have hdvd : (N / d) * d ∣ (N / d) * (x + y) := Nat.dvd_iff_mod_eq_zero.mpr hc
      have hdy : d ∣ x + y := (hdvdms (x + y)).1 hdvd
      exact h5 (Nat.dvd_iff_mod_eq_zero.mp hdy)
    exact ⟨(hmuly x).2 h1, (hmulb x).2 h2, (hmuly y).2 h3, (hmulb y).2 h4, hmodne,
      (conductor_eq N d ((N / d) * x) ((N / d) * y) hd hN).2 (by
        rw [hgx, h6, Nat.mul_one])⟩

/-- The scaling bijection: at degree `N` with `d ∣ N`, the characters of
    conductor `d` are `(N/d)·(x, y)` over the coprime pairs `(x, y)` at
    level `d` — so the executable bucket equals the coprime count. -/
theorem condCount_eq_coprime (N d : Nat) (hd : d ∣ N) (hN : 0 < N) :
    condCount N d = coprimeSum d := by
  have hmd : N / d * d = N := Nat.mul_div_cancel' hd
  have hmpos : 0 < N / d := by
    rcases Nat.eq_zero_or_pos (N / d) with h0 | h0
    · rw [h0, Nat.zero_mul] at hmd
      omega
    · exact h0
  have hmdiv : N / (N / d) = d := by
    have h1 : (N / d) * (N / (N / d)) = N :=
      Nat.mul_div_cancel' ⟨d, by rw [hmd, Nat.mul_comm]⟩
    exact Nat.mul_left_cancel hmpos (by rw [h1, hmd])
  unfold condCount coprimeSum
  have hS : ∀ a : Nat,
      sumTo (fun b => if 0 < a ∧ a < N ∧ 0 < b ∧ b < N ∧ (a + b) % N ≠ 0
            ∧ conductor N a b = d then 1 else 0) N
        = if N / d ∣ a then
            sumTo (fun y => if 0 < (a / (N / d)) ∧ (a / (N / d)) < d ∧ 0 < y ∧ y < d
                ∧ ((a / (N / d)) + y) % d ≠ 0
                ∧ Nat.gcd (Nat.gcd (a / (N / d)) y) d = 1 then 1 else 0) d
          else 0 := by
    intro a
    by_cases hma : N / d ∣ a
    · obtain ⟨x, rfl⟩ := hma
      rw [if_pos rfl]
      rw [sumTo_congr
          (fun b => if 0 < (N / d) * x ∧ (N / d) * x < N ∧ 0 < b ∧ b < N
              ∧ ((N / d) * x + b) % N ≠ 0 ∧ conductor N ((N / d) * x) b = d
            then 1 else 0)
          (fun b => if N / d ∣ b then
            if 0 < x ∧ x < d ∧ 0 < (b / (N / d)) ∧ (b / (N / d)) < d
              ∧ (x + (b / (N / d))) % d ≠ 0
              ∧ Nat.gcd (Nat.gcd x (b / (N / d))) d = 1 then 1 else 0
          else 0) N
          (fun b _ => by
            by_cases hdv : N / d ∣ b
            · obtain ⟨y, rfl⟩ := hdv
              rw [if_pos hdv, Nat.mul_div_cancel_left y hmpos]
              by_cases hR : 0 < x ∧ x < d ∧ 0 < y ∧ y < d ∧ (x + y) % d ≠ 0
                ∧ Nat.gcd (Nat.gcd x y) d = 1
              · rw [if_pos ((condCount_scale N d hd hN x y).2 hR), if_pos hR]
              · rw [if_neg (fun hc => hR ((condCount_scale N d hd hN x y).1 hc)),
                  if_neg hR]
            · rw [if_neg hdv, if_neg (fun hc => hdv (by
                have h1 := (conductor_eq N d ((N / d) * x) b hd hN).1 hc.2.2.2.2
                have h2 : Nat.gcd (Nat.gcd ((N / d) * x) b) N ∣ b := by
                  have h3 : Nat.gcd (Nat.gcd ((N / d) * x) b) N ∣ Nat.gcd ((N / d) * x) b :=
                    Nat.gcd_dvd_left _ _
                  rw [h1] at h3
                  exact Nat.dvd_trans h3 (Nat.gcd_dvd_right _ _)
                exact hdv h2))],
        sumTo_mul_div (N / d)
          (fun y => if 0 < x ∧ x < d ∧ 0 < y ∧ y < d ∧ (x + y) % d ≠ 0
              ∧ Nat.gcd (Nat.gcd x y) d = 1 then 1 else 0) hmpos N, hmdiv]
    · rw [if_neg hma]
      rw [sumTo_head_zero _ N (fun b _ => by
        rw [if_neg (fun hc => hma (by
          have h1 := (conductor_eq N d a b hd hN).1 hc.2.2.2.2
          have h2 : Nat.gcd (Nat.gcd a b) N ∣ a := Nat.gcd_dvd_left _ _
          rw [h1] at h2
          exact Nat.dvd_trans h2 (Nat.gcd_dvd_left _ _)))])]
  rw [hS, sumTo_mul_div (N / d)
      (fun x => sumTo (fun y => if 0 < x ∧ x < d ∧ 0 < y ∧ y < d ∧ (x + y) % d ≠ 0
          ∧ Nat.gcd (Nat.gcd x y) d = 1 then 1 else 0) d) hmpos N, hmdiv]
