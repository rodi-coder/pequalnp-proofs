import Mathlib
import PEqualNP.Defs

theorem PEqualNP.Outside.L_gct_236 : (∀ (s : Fin 3 → ℝ) (g : Fin 3 → Polynomial ℝ), (∀ i, s i = 1 ∨ s i = -1) → (∀ i, (g i).support.card ≤ 3) → ((Finset.univ : Finset (Fin 3)).sum fun i => Polynomial.C (s i) * g i ^ 3) ≠ 0 → ∀ x : ℝ, 0 < x → Polynomial.rootMultiplicity x ((Finset.univ : Finset (Fin 3)).sum fun i => Polynomial.C (s i) * g i ^ 3) ≤ 14) := by
  sorry
