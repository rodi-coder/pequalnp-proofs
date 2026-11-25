import Mathlib
import PEqualNP.Defs

theorem PEqualNP.Outside.L_meta_12247 : (¬ (∀ s : ℕ, PEqualNP.MetaComplexity.HasCircuitSize 6 (fun x : Fin 6 → Bool => Nat.testBit (4269834240 * 2 ^ 32 + 2147516416) (∑ i : Fin 6, if x i then 2 ^ (i : ℕ) else 0)) s → ∃ C : PEqualNP.CircuitLowerBounds.Circuit, PEqualNP.MetaComplexity.Monotone2 C ∧ C.size ≤ s ∧ ∀ x : Fin 6 → Bool, C.eval (List.ofFn x) = Nat.testBit (4269834240 * 2 ^ 32 + 2147516416) (∑ i : Fin 6, if x i then 2 ^ (i : ℕ) else 0))) := by
  sorry
