"""
Geometric Loss -- 12D Observation as Native Loss Function
==========================================================
The 12D meta-observer IS the loss function. Not a separate logging
system but the actual feedback signal that drives momentum updates.

Maps 12D observation dimensions to SFCR momentum gradients:
  Structure/Legibility/Routing -> S (Earth) momentum
  Contradiction/Coordination/Grounding -> F (Fire) momentum
  Semantics/Interop/Potential -> C (Water) momentum [LOCKED at 0.5]
  Recursion/Emergence/Compression -> R (Air) momentum

Keep/discard from observation improvement.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .geometric_constants import (
    FACES, ATTRACTOR, DIM_NAMES, DIM_TO_ELEMENT, ELEMENT_LENS_WEIGHTS, LENS_ORDER,
)
from .geometric_forward import ForwardResult
from .momentum_field import MomentumField
from .hybrid_math import QuaternionicGradient


@dataclass
class Observation12D:
    """12-dimensional observation of a forward pass result."""
    scores: dict[str, float] = field(default_factory=dict)  # dim_name -> score [0, 1]
    lens: str = "S"
    total_score: float = 0.0
    resonance: float = 0.0
    commitment_rate: float = 0.0


class GeometricLoss:
    """12D observation as the native loss function.

    Observes a ForwardResult, computes 12D scores, and derives
    momentum gradients for each SFCR element x shell.
    """

    def observe(self, result: ForwardResult, lens: str = "S") -> Observation12D:
        """Compute 12D observation from a forward pass result."""
        scores = {}
        candidates = result.candidates or []

        # x1_structure: gate diversity in top results
        if candidates:
            gates = set(c.gate for c in candidates)
            scores["x1_structure"] = min(1.0, len(gates) / 8.0)
        else:
            scores["x1_structure"] = 0.0

        # x2_semantics: average desire score (token alignment)
        if candidates:
            scores["x2_semantics"] = sum(c.desire for c in candidates) / len(candidates)
        else:
            scores["x2_semantics"] = 0.0

        # x3_coordination: SFCR path agreement (how many elements in top results)
        if candidates:
            elements = set(c.element for c in candidates)
            scores["x3_coordination"] = len(elements) / 4.0
        else:
            scores["x3_coordination"] = 0.0

        # x4_recursion: resonance quality
        scores["x4_recursion"] = result.resonance

        # x5_contradiction: element diversity (high = some tension = good)
        if candidates:
            face_counts = {}
            for c in candidates:
                face_counts[c.element] = face_counts.get(c.element, 0) + 1
            # Shannon entropy normalized
            total = sum(face_counts.values())
            entropy = 0.0
            for count in face_counts.values():
                p = count / total
                if p > 0:
                    entropy -= p * math.log2(p)
            scores["x5_contradiction"] = entropy / 2.0  # max log2(4)=2
        else:
            scores["x5_contradiction"] = 0.0

        # x6_emergence: cross-element bridge usage
        cross_pairs = result.cross_element_pairs_used or []
        scores["x6_emergence"] = min(1.0, len(cross_pairs) / 5.0)

        # x7_legibility: results are well-formed (have names, elements)
        if candidates:
            well_formed = sum(1 for c in candidates if c.doc_name and c.element != "unknown")
            scores["x7_legibility"] = well_formed / len(candidates)
        else:
            scores["x7_legibility"] = 0.0

        # x8_routing: ranking smoothness (score distribution)
        if len(candidates) > 1:
            merged = [c.merged_score for c in candidates]
            spread = max(merged) - min(merged)
            scores["x8_routing"] = min(1.0, spread * 2)  # want spread
        else:
            scores["x8_routing"] = 0.0

        # x9_grounding: commitment
        scores["x9_grounding"] = 1.0 if result.committed else 0.0

        # x10_compression: R-path contribution (fractal/compression quality)
        if candidates:
            r_contrib = sum(c.path_contributions.get("R", 0) for c in candidates)
            scores["x10_compression"] = min(1.0, r_contrib / max(len(candidates), 1))
        else:
            scores["x10_compression"] = 0.0

        # x11_interop: bridge usage coverage
        if cross_pairs:
            unique_bridges = set(p.split(":")[0] for p in cross_pairs if ":" in p)
            scores["x11_interop"] = len(unique_bridges) / 6.0  # max 6 bridges
        else:
            scores["x11_interop"] = 0.0

        # x12_potential: desire score of top result
        if candidates:
            scores["x12_potential"] = candidates[0].desire
        else:
            scores["x12_potential"] = 0.0

        # Apply lens weighting
        lens_weights = ELEMENT_LENS_WEIGHTS.get(lens, {})
        weighted_total = 0.0
        weight_sum = 0.0
        for dim in DIM_NAMES:
            w = lens_weights.get(dim, 1.0)
            weighted_total += w * scores.get(dim, 0.0)
            weight_sum += w
        total = weighted_total / max(weight_sum, 1.0)

        return Observation12D(
            scores=scores,
            lens=lens,
            total_score=total,
            resonance=result.resonance,
            commitment_rate=1.0 if result.committed else 0.0,
        )

    def momentum_gradient(self, obs: Observation12D, face: str, shell: int) -> float:
        """Compute SCALAR momentum gradient (backward compatible).

        Calls momentum_gradient_quaternionic and projects to scalar.
        """
        qgrad = self.momentum_gradient_quaternionic(obs, face, shell)
        return qgrad.weighted_scalar({"D": 0.4, "Ω": 0.2, "Σ": 0.15, "Ψ": 0.25})

    def momentum_gradient_quaternionic(
        self, obs: Observation12D, face: str, shell: int
    ) -> QuaternionicGradient:
        """Compute QUATERNIONIC momentum gradient for a specific element-shell position.

        Maps 12D observation to a 4-component gradient in the quad-polar operator space:
          D-component:  discrete improvement signal (attractor-relative balance)
          Ω-component:  continuous gradient (smooth interpolation toward equilibrium)
          Σ-component:  stochastic escape signal (from observation variance)
          Ψ-component:  spectral alignment signal (from cross-element structure)

        Water (C) always returns zero quaternion (locked).

        Uses attractor-relative gradient: each element's gradient is computed
        relative to the MEAN across ALL elements (not a fixed 0.5 baseline).
        """
        if face == "C":
            return QuaternionicGradient()  # Water is locked — zero quaternion

        # Gather all dimensions that couple to this element
        relevant_dims = [dim for dim, elem in DIM_TO_ELEMENT.items() if elem == face]
        if not relevant_dims:
            return QuaternionicGradient()

        # Compute this element's mean observation score
        dim_scores = [obs.scores.get(dim, 0.0) for dim in relevant_dims]
        mean_score = sum(dim_scores) / len(dim_scores)

        # Compute GLOBAL mean across ALL non-Water dimensions for baseline
        all_non_water_dims = [dim for dim, elem in DIM_TO_ELEMENT.items() if elem != "C"]
        all_scores = [obs.scores.get(dim, 0.0) for dim in all_non_water_dims]
        global_mean = sum(all_scores) / max(len(all_scores), 1)

        # ── D-component: discrete attractor-relative balance ──
        # How far this element deviates from global mean
        d_gradient = (global_mean - mean_score) * 0.5

        # ── Ω-component: continuous gradient toward phi equilibrium ──
        # Pull toward golden mean (1.618) not path_value (0.25) which is below floor.
        # This prevents single-element collapse: strong pull when far from phi.
        from .momentum_field import get_momentum_field
        mf = get_momentum_field()
        current_momentum = mf.get_momentum(face, max(1, shell))
        attractor_target = mf.MOMENTUM_EQUILIBRIUM  # phi = 1.618
        omega_gradient = (attractor_target - current_momentum) * 0.03

        # ── Σ-component: stochastic escape signal ──
        # High when this element's scores have high variance (rugged landscape)
        if len(dim_scores) > 1:
            score_var = sum((s - mean_score) ** 2 for s in dim_scores) / len(dim_scores)
            sigma_gradient = score_var * (global_mean - mean_score)
        else:
            sigma_gradient = 0.0

        # ── Ψ-component: spectral alignment ──
        # Cross-element structure signal — from the full 12D observation pattern
        # Measures how this element's dimensions relate to the overall structure
        psi_gradient = 0.0
        for dim in relevant_dims:
            score = obs.scores.get(dim, 0.0)
            # Spectral contribution: alignment with the dominant observation direction
            psi_gradient += (score - global_mean) * (obs.total_score - 0.5)
        psi_gradient /= max(len(relevant_dims), 1)

        # Scale by commitment (committed observations have stronger signal)
        commitment_boost = 1.2 if obs.commitment_rate > 0 else 1.0

        return QuaternionicGradient(
            d=d_gradient * commitment_boost,
            omega=omega_gradient * commitment_boost,
            sigma=sigma_gradient * commitment_boost,
            psi=psi_gradient * commitment_boost,
        )

    def should_keep(self, obs_before: Observation12D, obs_after: Observation12D) -> bool:
        """Decide whether to keep a momentum update.

        Keep if total observation score improved.
        """
        return obs_after.total_score >= obs_before.total_score

    def compute_all_gradients(self, obs: Observation12D) -> dict[str, float]:
        """Compute scalar gradients for all 4 elements (C is always 0)."""
        return {face: self.momentum_gradient(obs, face, 1) for face in FACES}

    def compute_all_gradients_quaternionic(self, obs: Observation12D) -> dict[str, QuaternionicGradient]:
        """Compute QUATERNIONIC gradients for all 4 elements.

        Returns a dict of face → QuaternionicGradient with full 4-pole
        gradient information for each SFCR element.
        """
        return {face: self.momentum_gradient_quaternionic(obs, face, 1) for face in FACES}
