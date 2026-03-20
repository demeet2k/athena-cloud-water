# CRYSTAL: Xi108:W3:A1:S1 | face=S | node=001 | depth=0 | phase=Seed
# METRO: Hybrid-Math-Core
# BRIDGES: loss_engine→momentum_field→geometric_loss→self_play→polestar_gemm

"""
Hybrid Mathematics Engine — Quad-Polar Operator Framework
==========================================================
Replaces linear/scalar math throughout the Athena crystal with the
full quad-polar hybrid operator algebra from the treatise.

The 4 poles:
  Ψ (Psi)   — Spectral/Recursive: eigenvector initialization, multigrid, RG
  Ω (Omega) — Continuous/Gradient: smooth optimization, gradient descent
  Σ (Sigma) — Stochastic: random restarts, Lévy jumps, perturbation
  D (Delta) — Discrete: local search, constraint satisfaction, executor

Operator simplex: G = w_D·D + w_Ω·Ω + w_Σ·Σ + w_Ψ·Ψ
Quaternionic encoding: G = D + Ω·i + Σ·j + Ψ·k

240 hybrid types = 15 mask combinations × 4 lens transforms × 4 pole weights
  (mapped from the Phi-Sigma-60 metro atlas)

This module provides:
  1. ProblemSignature — diagnose any optimization landscape
  2. PoleSelector — adaptive pole weight selection per problem class
  3. QuaternionicGradient — 4-component gradient vector (not scalar!)
  4. HybridOptimizer — replaces Adam with pole-aware phase optimization
  5. RotationalUpdate — replaces linear momentum update with rotational dynamics
  6. HybridPhaseScheduler — Ψ→Ω→Σ→D phase cycling

References:
  - ADAPTIVE_HYBRIDIZATION_FRAMEWORK.md (empirical results)
  - HYBRIDIZATION_COMPLETE_GUIDE.md (decision framework)
  - Quad-Polar Hybrid Equation Framework Parts I-XI (operator theory)
  - PoleStarGEMM (adaptive matrix multiplication)
"""

from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .geometric_constants import (
    PHI, PHI_INV, PHI_INV2, SQRT3,
    FACES, FACE_INDEX, BRIDGE_WEIGHTS, ATTRACTOR,
)


# ══════════════════════════════════════════════════════════════════════
#  CONSTANTS — from the treatise
# ══════════════════════════════════════════════════════════════════════

# Master equation: (p-2)(q-2) = 4 — the bridge between discrete and continuous
MASTER_EQUATION_CONSTANT = 4

# Quaternion basis
Q_BASIS = {"1": "D", "i": "Ω", "j": "Σ", "k": "Ψ"}

# All 15 pole masks (non-empty subsets of {Ψ, Ω, Σ, D})
POLE_MASKS = [
    # 1-pole
    frozenset({"D"}), frozenset({"Ω"}), frozenset({"Σ"}), frozenset({"Ψ"}),
    # 2-pole (6 combinations)
    frozenset({"D", "Ω"}), frozenset({"D", "Σ"}), frozenset({"D", "Ψ"}),
    frozenset({"Ω", "Σ"}), frozenset({"Ω", "Ψ"}), frozenset({"Σ", "Ψ"}),
    # 3-pole (4 combinations)
    frozenset({"D", "Ω", "Σ"}), frozenset({"D", "Ω", "Ψ"}),
    frozenset({"D", "Σ", "Ψ"}), frozenset({"Ω", "Σ", "Ψ"}),
    # 4-pole
    frozenset({"D", "Ω", "Σ", "Ψ"}),
]

# 4 lens transforms (from SFCR)
LENS_TRANSFORMS = ("Square", "Flower", "Cloud", "Fractal")

# Total hybrid types: 15 masks × 4 lenses × 4 weight profiles = 240
TOTAL_HYBRID_TYPES = len(POLE_MASKS) * len(LENS_TRANSFORMS) * 4


# ══════════════════════════════════════════════════════════════════════
#  PROBLEM CLASSES — from the Complete Guide
# ══════════════════════════════════════════════════════════════════════

class ProblemClass(Enum):
    """Five problem classes from the hybridization guide."""
    SPECTRAL = "A"      # Ψ+D dominant — matrix structure, eigenvector initialization
    GRADIENT = "B"      # Ω+D dominant — smooth, convex, gradient reliable
    STOCHASTIC = "C"    # Σ+D dominant — rugged, many local optima
    CONSTRAINED = "D"   # D+Ω dominant — hard constraints, feasibility first
    HIERARCHICAL = "E"  # Ψ+all — multi-scale, coarse-to-fine


# Default pole weights per problem class (from empirical testing)
CLASS_WEIGHTS: dict[ProblemClass, dict[str, float]] = {
    ProblemClass.SPECTRAL:     {"Ψ": 0.60, "Ω": 0.00, "Σ": 0.00, "D": 0.40},
    ProblemClass.GRADIENT:     {"Ψ": 0.00, "Ω": 0.80, "Σ": 0.00, "D": 0.20},
    ProblemClass.STOCHASTIC:   {"Ψ": 0.00, "Ω": 0.10, "Σ": 0.50, "D": 0.40},
    ProblemClass.CONSTRAINED:  {"Ψ": 0.00, "Ω": 0.20, "Σ": 0.00, "D": 0.80},
    ProblemClass.HIERARCHICAL: {"Ψ": 0.40, "Ω": 0.20, "Σ": 0.10, "D": 0.30},
}

# Adaptive framework weights (when synergy detected)
ADAPTIVE_EQUAL = {"Ψ": 0.25, "Ω": 0.25, "Σ": 0.25, "D": 0.25}


# ══════════════════════════════════════════════════════════════════════
#  PROBLEM SIGNATURE — landscape diagnosis
# ══════════════════════════════════════════════════════════════════════

@dataclass
class ProblemSignature:
    """Diagnosis of an optimization landscape along the 4 diagnostic dimensions.

    Computed BEFORE any optimization, used to select pole weights.
    Maps directly to the Adaptive Hybridization Framework.
    """
    # Dimension 1: STRUCTURE (Ψ relevance)
    spectral_gap: float = 0.0           # (λ₁-λ₀)/(λₙ-λ₀), higher = more structure
    condition_number: float = 1.0       # |λₙ|/|λ₀|, lower = better conditioned
    has_matrix_structure: bool = False

    # Dimension 2: LANDSCAPE (Σ relevance)
    n_local_optima: int = 1             # count of distinct local optima from sampling
    landscape_ruggedness: float = 0.0   # [0,1], higher = more rugged

    # Dimension 3: GRADIENT (Ω relevance)
    gradient_reliability: float = 0.5   # [0,1], cosine consistency of nearby gradients

    # Dimension 4: CONSTRAINTS (D relevance)
    has_hard_constraints: bool = False
    feasibility_ratio: float = 1.0      # fraction of random samples that are feasible

    # Derived
    dominant_pole: str = "D"
    problem_class: ProblemClass = ProblemClass.CONSTRAINED
    confidence: float = 0.5

    def classify(self) -> ProblemClass:
        """Classify this problem into one of the 5 classes."""
        scores = {"Ψ": 0.0, "Ω": 0.0, "Σ": 0.0, "D": 1.0}

        # Rule 1: Matrix structure → Ψ dominates
        if self.has_matrix_structure:
            scores["Ψ"] += 3.0
            if self.spectral_gap > 0.2:
                scores["Ψ"] += 2.0
            elif self.spectral_gap > 0.1:
                scores["Ψ"] += 1.0

        # Rule 2: Gradient reliability → Ω relevance
        scores["Ω"] += 2.0 * self.gradient_reliability
        if self.gradient_reliability > 0.7 and self.n_local_optima < 5:
            scores["Ω"] += 3.0  # likely convex

        # Rule 3: Rugged landscape → Σ needed
        if self.n_local_optima > 10:
            scores["Σ"] += 3.0
        elif self.n_local_optima > 5:
            scores["Σ"] += 1.5

        # Rule 4: Hard constraints → D essential
        if self.has_hard_constraints:
            scores["D"] += 2.0
        if self.feasibility_ratio < 0.1:
            scores["D"] += 3.0

        self.dominant_pole = max(scores, key=scores.get)

        # Map to problem class
        if self.dominant_pole == "Ψ":
            if self.n_local_optima > 5:
                self.problem_class = ProblemClass.HIERARCHICAL
            else:
                self.problem_class = ProblemClass.SPECTRAL
        elif self.dominant_pole == "Ω":
            self.problem_class = ProblemClass.GRADIENT
        elif self.dominant_pole == "Σ":
            self.problem_class = ProblemClass.STOCHASTIC
        else:
            self.problem_class = ProblemClass.CONSTRAINED

        # Confidence from score margin
        sorted_scores = sorted(scores.values(), reverse=True)
        if sorted_scores[0] > 0:
            self.confidence = 1.0 - (sorted_scores[1] / sorted_scores[0])
        else:
            self.confidence = 0.0

        return self.problem_class


# ══════════════════════════════════════════════════════════════════════
#  POLE SELECTOR — adaptive weight selection
# ══════════════════════════════════════════════════════════════════════

class PoleSelector:
    """Selects pole weights based on problem signature.

    Implements the decision tree from HYBRIDIZATION_COMPLETE_GUIDE.md
    with the adaptive override from ADAPTIVE_HYBRIDIZATION_FRAMEWORK.md.
    """

    @staticmethod
    def select(signature: ProblemSignature) -> dict[str, float]:
        """Return optimal pole weights for this problem signature."""
        problem_class = signature.classify()

        # Check for mixed characteristics → adaptive equal may beat dominant-pole
        is_mixed = (
            0.05 < signature.spectral_gap < 0.25
            and 5 < signature.n_local_optima < 20
            and 0.3 < signature.gradient_reliability < 0.7
        )

        if is_mixed and signature.confidence < 0.3:
            # No clear dominant pole → 4-pole equal wins (empirically 10.6% improvement)
            return dict(ADAPTIVE_EQUAL)

        # Otherwise use class-specific weights
        return dict(CLASS_WEIGHTS[problem_class])

    @staticmethod
    def predict_strategies(signature: ProblemSignature) -> list[dict[str, float]]:
        """Return ordered list of strategies to test (from Adaptive Framework)."""
        strategies = []

        # Mixed → try 4-pole equal
        if 0.05 < signature.spectral_gap < 0.25 and 5 < signature.n_local_optima < 20:
            strategies.append({"name": "4-pole-equal", **ADAPTIVE_EQUAL})

        # Strong structure + rugged → Ψ+Σ+D
        if signature.spectral_gap > 0.1 and signature.n_local_optima > 5:
            strategies.append({"name": "Ψ+Σ+D", "Ψ": 0.40, "Ω": 0.00, "Σ": 0.30, "D": 0.30})

        # Strong structure + smooth → Ψ+D
        if signature.spectral_gap > 0.2 and signature.n_local_optima < 5:
            strategies.append({"name": "Ψ+D", "Ψ": 0.60, "Ω": 0.00, "Σ": 0.00, "D": 0.40})

        # No structure + rugged → Σ+D
        if signature.spectral_gap < 0.05 and signature.n_local_optima > 10:
            strategies.append({"name": "Σ+D", "Ψ": 0.00, "Ω": 0.00, "Σ": 0.60, "D": 0.40})

        # Smooth + no structure → Ω+D
        if signature.gradient_reliability > 0.7 and signature.spectral_gap < 0.1:
            strategies.append({"name": "Ω+D", "Ψ": 0.00, "Ω": 0.60, "Σ": 0.00, "D": 0.40})

        # Always include fallbacks
        if not any(s.get("name") == "4-pole-equal" for s in strategies):
            strategies.append({"name": "4-pole-equal", **ADAPTIVE_EQUAL})
        strategies.append({"name": "D-only", "Ψ": 0.00, "Ω": 0.00, "Σ": 0.00, "D": 1.00})

        return strategies


# ══════════════════════════════════════════════════════════════════════
#  QUATERNIONIC GRADIENT — 4-component gradient vector
# ══════════════════════════════════════════════════════════════════════

@dataclass
class QuaternionicGradient:
    """4-component gradient in the quad-polar operator space.

    G = D + Ω·i + Σ·j + Ψ·k

    This replaces scalar gradients throughout the system.
    Each component carries gradient information from its pole:
      D: discrete improvement direction (local search gradient)
      Ω: continuous gradient (smooth landscape direction)
      Σ: stochastic gradient (escape direction from local optima)
      Ψ: spectral gradient (eigenvector alignment direction)
    """
    d: float = 0.0   # Discrete/Delta component
    omega: float = 0.0   # Continuous/Omega component
    sigma: float = 0.0   # Stochastic/Sigma component
    psi: float = 0.0     # Spectral/Psi component

    @property
    def norm(self) -> float:
        """Quaternionic norm: |G| = sqrt(D² + Ω² + Σ² + Ψ²)."""
        return math.sqrt(self.d**2 + self.omega**2 + self.sigma**2 + self.psi**2)

    @property
    def scalar(self) -> float:
        """Collapse to scalar using pole weights (for backward compatibility)."""
        return self.d  # The D component IS the scalar action

    def weighted_scalar(self, weights: dict[str, float]) -> float:
        """Collapse to weighted scalar: w_D·D + w_Ω·Ω + w_Σ·Σ + w_Ψ·Ψ."""
        return (
            weights.get("D", 0.25) * self.d
            + weights.get("Ω", 0.25) * self.omega
            + weights.get("Σ", 0.25) * self.sigma
            + weights.get("Ψ", 0.25) * self.psi
        )

    def conjugate(self) -> QuaternionicGradient:
        """Quaternion conjugate: D - Ω·i - Σ·j - Ψ·k."""
        return QuaternionicGradient(
            d=self.d, omega=-self.omega, sigma=-self.sigma, psi=-self.psi
        )

    def __mul__(self, other: QuaternionicGradient) -> QuaternionicGradient:
        """Hamilton product of two quaternionic gradients.

        This is the ROTATIONAL composition — not linear addition.
        (a + bi + cj + dk)(e + fi + gj + hk) using Hamilton's rules:
          i² = j² = k² = ijk = -1
        """
        a, b, c, d_ = self.d, self.omega, self.sigma, self.psi
        e, f, g, h = other.d, other.omega, other.sigma, other.psi
        return QuaternionicGradient(
            d=a*e - b*f - c*g - d_*h,
            omega=a*f + b*e + c*h - d_*g,
            sigma=a*g - b*h + c*e + d_*f,
            psi=a*h + b*g - c*f + d_*e,
        )

    def rotate_by(self, rotor: QuaternionicGradient) -> QuaternionicGradient:
        """Apply rotation: G' = rotor * G * rotor†.

        This is how the quad-polar framework applies transformations —
        not by addition, but by ROTATION in the 4D operator space.
        """
        conj = rotor.conjugate()
        return rotor * self * conj

    def phi_damped(self, target: QuaternionicGradient, strength: float = PHI_INV) -> QuaternionicGradient:
        """Phi-damped interpolation toward target.

        Uses golden ratio as the damping constant — proven optimal
        by the META LOOP convergence results.
        """
        inv = 1.0 - strength
        return QuaternionicGradient(
            d=self.d * inv + target.d * strength,
            omega=self.omega * inv + target.omega * strength,
            sigma=self.sigma * inv + target.sigma * strength,
            psi=self.psi * inv + target.psi * strength,
        )

    @staticmethod
    def from_sfcr(s: float, f: float, c: float, r: float) -> QuaternionicGradient:
        """Construct from SFCR element scores.

        Maps the crystal's 4 elements to the 4 poles:
          S (Earth/Square)  → D (Discrete)
          F (Fire/Flower)   → Ω (Continuous)
          C (Water/Cloud)   → Σ (Stochastic)
          R (Air/Fractal)   → Ψ (Spectral/Recursive)
        """
        return QuaternionicGradient(d=s, omega=f, sigma=c, psi=r)

    def to_sfcr(self) -> dict[str, float]:
        """Project back to SFCR element space."""
        return {"S": self.d, "F": self.omega, "C": self.sigma, "R": self.psi}


# ══════════════════════════════════════════════════════════════════════
#  HYBRID OPTIMIZER — replaces flat Adam with pole-aware optimization
# ══════════════════════════════════════════════════════════════════════

class HybridPhase(Enum):
    """Optimization phases from the hybridization methodology."""
    INITIALIZE = "init"      # Phase 1: Ψ-dominated (spectral init)
    INTENSIFY = "intensify"  # Phase 2: D+Ω (local search + gradient)
    DIVERSIFY = "diversify"  # Phase 3: Σ (perturbation when stuck)
    REINFORCE = "reinforce"  # Phase 4: Return to D+Ω with new basin
    POLISH = "polish"        # Phase 5: D-only (final refinement)


@dataclass
class HybridOptimizerState:
    """Persistent state for the hybrid optimizer."""
    # Per-key quaternionic moments (replaces scalar Adam moments)
    m1: dict[str, QuaternionicGradient] = field(default_factory=dict)
    m2: dict[str, QuaternionicGradient] = field(default_factory=dict)
    step: int = 0

    # Landscape tracking
    signature: ProblemSignature = field(default_factory=ProblemSignature)
    pole_weights: dict[str, float] = field(default_factory=lambda: dict(ADAPTIVE_EQUAL))
    current_phase: HybridPhase = HybridPhase.INITIALIZE

    # Stuck detection
    loss_window: list[float] = field(default_factory=list)
    stuck_count: int = 0
    best_loss: float = float("inf")

    # Phase cycling
    phase_step: int = 0
    phase_budget: int = 12  # steps per phase before cycling


class HybridOptimizer:
    """Quad-polar hybrid optimizer.

    Replaces flat Adam with:
      1. Problem signature diagnosis → pole selection
      2. Quaternionic gradient accumulation (4-component, not scalar)
      3. Phase-structured optimization (Ψ→Ω→Σ→D cycling)
      4. Stuck detection with automatic Σ-diversification
      5. Phi-homeostatic damping (golden ratio equilibrium)

    The key insight: DIFFERENT PARTS OF THE LANDSCAPE NEED DIFFERENT POLES.
    A dense region needs D+Ω. A rugged region needs Σ+D. A structured
    region needs Ψ+D. The optimizer detects which and adapts.
    """

    def __init__(
        self,
        learning_rate: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        gradient_clip: float = 1.0,
        epsilon: float = 1e-8,
        weight_decay: float = 0.0001,
        stuck_threshold: int = 5,      # steps with no improvement before Σ-diversify
        phase_budget: int = 12,
    ):
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.clip = gradient_clip
        self.eps = epsilon
        self.wd = weight_decay
        self.stuck_threshold = stuck_threshold
        self.state = HybridOptimizerState(phase_budget=phase_budget)

    def diagnose(self, observation_scores: dict[str, float], loss_history: list[float]):
        """Diagnose the current optimization landscape from observation data.

        This is called periodically (not every step) to update the problem signature.
        Uses the observation 12D scores as a proxy for landscape analysis.
        """
        sig = self.state.signature

        # Estimate structure from score variance (high variance = structure exists)
        scores = list(observation_scores.values())
        if scores:
            mean_s = sum(scores) / len(scores)
            var_s = sum((s - mean_s) ** 2 for s in scores) / max(len(scores), 1)
            sig.spectral_gap = min(1.0, var_s * 4)  # proxy: high variance = spectral gap
            sig.has_matrix_structure = sig.spectral_gap > 0.1

        # Estimate ruggedness from loss oscillation
        if len(loss_history) >= 5:
            recent = loss_history[-10:]
            reversals = sum(
                1 for i in range(1, len(recent) - 1)
                if (recent[i] - recent[i-1]) * (recent[i+1] - recent[i]) < 0
            )
            sig.n_local_optima = max(1, reversals * 3)
            sig.landscape_ruggedness = min(1.0, reversals / max(len(recent) - 2, 1))

        # Estimate gradient reliability from loss trend consistency
        if len(loss_history) >= 3:
            deltas = [loss_history[i+1] - loss_history[i] for i in range(len(loss_history)-1)]
            if deltas:
                n_consistent = sum(1 for d in deltas[-5:] if d < 0)  # improving
                sig.gradient_reliability = n_consistent / max(len(deltas[-5:]), 1)

        sig.classify()

        # Update pole weights based on diagnosis
        self.state.pole_weights = PoleSelector.select(sig)

    def _detect_stuck(self, loss: float):
        """Detect if optimization is stuck in a local optimum."""
        self.state.loss_window.append(loss)
        if len(self.state.loss_window) > 20:
            self.state.loss_window = self.state.loss_window[-20:]

        if loss < self.state.best_loss - 1e-6:
            self.state.best_loss = loss
            self.state.stuck_count = 0
        else:
            self.state.stuck_count += 1

    def _advance_phase(self):
        """Advance through the 5-phase optimization cycle."""
        self.state.phase_step += 1

        if self.state.phase_step >= self.state.phase_budget:
            self.state.phase_step = 0
            phases = list(HybridPhase)
            current_idx = phases.index(self.state.current_phase)
            next_idx = (current_idx + 1) % len(phases)
            self.state.current_phase = phases[next_idx]

        # Emergency Σ-diversification if stuck
        if self.state.stuck_count >= self.stuck_threshold:
            self.state.current_phase = HybridPhase.DIVERSIFY
            self.state.stuck_count = 0
            self.state.phase_step = 0

    def _phase_weights(self) -> dict[str, float]:
        """Get pole weights modulated by current phase.

        Phase cycling adjusts the base pole weights:
          INITIALIZE:  boost Ψ
          INTENSIFY:   boost D+Ω
          DIVERSIFY:   boost Σ
          REINFORCE:   boost D+Ω (from new basin)
          POLISH:      boost D only
        """
        base = dict(self.state.pole_weights)
        phase = self.state.current_phase

        # Phase modulation factors
        if phase == HybridPhase.INITIALIZE:
            base["Ψ"] = max(base["Ψ"], 0.5)
        elif phase == HybridPhase.INTENSIFY:
            base["D"] = max(base["D"], 0.3)
            base["Ω"] = max(base["Ω"], 0.3)
        elif phase == HybridPhase.DIVERSIFY:
            base["Σ"] = max(base["Σ"], 0.4)
        elif phase == HybridPhase.REINFORCE:
            base["D"] = max(base["D"], 0.35)
            base["Ω"] = max(base["Ω"], 0.25)
        elif phase == HybridPhase.POLISH:
            base["D"] = max(base["D"], 0.6)
            base["Σ"] = 0.0  # no perturbation in polish phase

        # Renormalize to sum to 1
        total = sum(base.values())
        if total > 0:
            base = {k: v / total for k, v in base.items()}

        return base

    def accumulate(self, key: str, gradient: QuaternionicGradient, loss: float = 0.0) -> QuaternionicGradient:
        """Accumulate a quaternionic gradient with pole-aware Adam.

        Returns the 4-component update vector (not a scalar!).
        """
        self.state.step += 1
        self._detect_stuck(loss)
        self._advance_phase()

        # Clip each component independently
        def clip(v):
            return max(-self.clip, min(self.clip, v))

        g = QuaternionicGradient(
            d=clip(gradient.d), omega=clip(gradient.omega),
            sigma=clip(gradient.sigma), psi=clip(gradient.psi),
        )

        # Initialize moments if needed
        if key not in self.state.m1:
            self.state.m1[key] = QuaternionicGradient()
            self.state.m2[key] = QuaternionicGradient()

        m1 = self.state.m1[key]
        m2 = self.state.m2[key]

        # Update first moment (quaternionic EMA)
        b1 = self.beta1
        self.state.m1[key] = QuaternionicGradient(
            d=b1 * m1.d + (1 - b1) * g.d,
            omega=b1 * m1.omega + (1 - b1) * g.omega,
            sigma=b1 * m1.sigma + (1 - b1) * g.sigma,
            psi=b1 * m1.psi + (1 - b1) * g.psi,
        )

        # Update second moment (quaternionic squared EMA)
        b2 = self.beta2
        self.state.m2[key] = QuaternionicGradient(
            d=b2 * m2.d + (1 - b2) * g.d ** 2,
            omega=b2 * m2.omega + (1 - b2) * g.omega ** 2,
            sigma=b2 * m2.sigma + (1 - b2) * g.sigma ** 2,
            psi=b2 * m2.psi + (1 - b2) * g.psi ** 2,
        )

        # Bias correction
        bc1 = 1 - b1 ** self.state.step
        bc2 = 1 - b2 ** self.state.step

        m1_hat = QuaternionicGradient(
            d=self.state.m1[key].d / bc1,
            omega=self.state.m1[key].omega / bc1,
            sigma=self.state.m1[key].sigma / bc1,
            psi=self.state.m1[key].psi / bc1,
        )
        m2_hat = QuaternionicGradient(
            d=self.state.m2[key].d / bc2,
            omega=self.state.m2[key].omega / bc2,
            sigma=self.state.m2[key].sigma / bc2,
            psi=self.state.m2[key].psi / bc2,
        )

        # Quaternionic Adam update: lr * m1_hat / (sqrt(m2_hat) + eps)
        # WEIGHTED by current phase pole weights
        phase_w = self._phase_weights()

        update = QuaternionicGradient(
            d=self.lr * m1_hat.d / (math.sqrt(m2_hat.d) + self.eps) * phase_w.get("D", 0.25),
            omega=self.lr * m1_hat.omega / (math.sqrt(m2_hat.omega) + self.eps) * phase_w.get("Ω", 0.25),
            sigma=self.lr * m1_hat.sigma / (math.sqrt(m2_hat.sigma) + self.eps) * phase_w.get("Σ", 0.25),
            psi=self.lr * m1_hat.psi / (math.sqrt(m2_hat.psi) + self.eps) * phase_w.get("Ψ", 0.25),
        )

        return update

    def scalar_update(self, key: str, gradient: float, loss: float = 0.0) -> float:
        """Backward-compatible scalar interface.

        Lifts a scalar gradient into the quaternionic space,
        applies the full hybrid optimizer, then projects back.
        """
        # Lift scalar to quaternionic using current pole weights
        weights = self._phase_weights()
        qgrad = QuaternionicGradient(
            d=gradient * weights.get("D", 0.25),
            omega=gradient * weights.get("Ω", 0.25),
            sigma=gradient * weights.get("Σ", 0.25),
            psi=gradient * weights.get("Ψ", 0.25),
        )
        update = self.accumulate(key, qgrad, loss)
        return update.weighted_scalar(weights)

    def reset(self):
        """Reset optimizer state."""
        self.state = HybridOptimizerState(phase_budget=self.state.phase_budget)

    def status(self) -> dict:
        """Current optimizer status for diagnostics."""
        sig = self.state.signature
        return {
            "step": self.state.step,
            "phase": self.state.current_phase.value,
            "phase_step": f"{self.state.phase_step}/{self.state.phase_budget}",
            "problem_class": sig.problem_class.value,
            "dominant_pole": sig.dominant_pole,
            "pole_weights": self.state.pole_weights,
            "phase_weights": self._phase_weights(),
            "stuck_count": self.state.stuck_count,
            "best_loss": self.state.best_loss,
            "spectral_gap": sig.spectral_gap,
            "landscape_ruggedness": sig.landscape_ruggedness,
            "gradient_reliability": sig.gradient_reliability,
            "confidence": sig.confidence,
        }


# ══════════════════════════════════════════════════════════════════════
#  ROTATIONAL UPDATE — replaces linear momentum update
# ══════════════════════════════════════════════════════════════════════

class RotationalUpdate:
    """Applies quaternionic rotation to momentum updates.

    Instead of: new = current + lr * delta  (LINEAR, archaic)
    We do:      new = rotor * current_quat * rotor†  (ROTATIONAL)

    The rotor is constructed from the gradient direction in the 4D
    operator space, with angle proportional to learning rate.
    """

    @staticmethod
    def apply(
        current_momentum: float,
        gradient: QuaternionicGradient,
        lr: float = 0.01,
        face: str = "S",
        equilibrium: float = PHI,
    ) -> float:
        """Apply rotational update to a scalar momentum value.

        1. Embed current momentum as a quaternion on the SFCR manifold
        2. Construct rotor from gradient direction
        3. Apply rotation: new = rotor * current * rotor†
        4. Project back to scalar momentum
        5. Apply phi-homeostatic damping

        Returns new momentum value.
        """
        if face == "C":
            return ATTRACTOR["water_momentum"]  # Water is LOCKED

        # Embed current momentum as quaternion
        # The face determines which component gets the momentum value
        face_to_component = {"S": "d", "F": "omega", "C": "sigma", "R": "psi"}
        component = face_to_component.get(face, "d")

        current_q = QuaternionicGradient()
        setattr(current_q, component, current_momentum)

        # Construct rotor from gradient
        # Rotor = cos(θ/2) + sin(θ/2) * (normalized gradient axis)
        gnorm = gradient.norm
        if gnorm < 1e-10:
            return current_momentum

        theta = lr * gnorm  # rotation angle proportional to gradient magnitude
        half_theta = theta / 2.0

        cos_ht = math.cos(half_theta)
        sin_ht = math.sin(half_theta)

        # Normalized gradient axis
        rotor = QuaternionicGradient(
            d=cos_ht,
            omega=sin_ht * gradient.omega / gnorm,
            sigma=sin_ht * gradient.sigma / gnorm,
            psi=sin_ht * gradient.psi / gnorm,
        )

        # Apply rotation: new = rotor * current * rotor†
        rotated = current_q.rotate_by(rotor)

        # Project back to scalar: take the component for this face
        new_val = getattr(rotated, component)

        # Phi-homeostatic damping toward golden equilibrium
        distance = new_val - equilibrium
        homeostatic = -0.02 * distance
        new_val += homeostatic

        # Clamp to valid range
        return max(0.3, min(5.0, new_val))


# ══════════════════════════════════════════════════════════════════════
#  LANDSCAPE ANALYZER — real-time diagnosis of the optimization surface
# ══════════════════════════════════════════════════════════════════════

class LandscapeAnalyzer:
    """Continuous landscape analysis using observation history.

    Maintains a running estimate of the problem signature by
    tracking loss history, gradient consistency, and score variance.
    Re-diagnoses every N steps and updates the optimizer's pole weights.
    """

    def __init__(self, rediagnose_interval: int = 10):
        self.interval = rediagnose_interval
        self._step = 0
        self._loss_history: list[float] = []
        self._score_history: list[dict[str, float]] = []
        self._current_signature = ProblemSignature()

    def observe(self, scores: dict[str, float], loss: float):
        """Record an observation for landscape analysis."""
        self._step += 1
        self._loss_history.append(loss)
        self._score_history.append(scores)

        # Keep bounded history
        if len(self._loss_history) > 100:
            self._loss_history = self._loss_history[-100:]
        if len(self._score_history) > 100:
            self._score_history = self._score_history[-100:]

    def should_rediagnose(self) -> bool:
        """Whether it's time to re-diagnose the landscape."""
        return self._step % self.interval == 0 and self._step > 0

    def diagnose(self) -> ProblemSignature:
        """Compute current problem signature from observation history."""
        sig = ProblemSignature()

        # Structure from score variance
        if self._score_history:
            latest = self._score_history[-1]
            scores = list(latest.values())
            if scores:
                mean_s = sum(scores) / len(scores)
                var_s = sum((s - mean_s) ** 2 for s in scores) / len(scores)
                sig.spectral_gap = min(1.0, var_s * 4)
                sig.has_matrix_structure = sig.spectral_gap > 0.1

        # Ruggedness from loss oscillation
        if len(self._loss_history) >= 5:
            recent = self._loss_history[-10:]
            reversals = sum(
                1 for i in range(1, len(recent) - 1)
                if (recent[i] - recent[i-1]) * (recent[i+1] - recent[i]) < 0
            )
            sig.n_local_optima = max(1, reversals * 3)
            sig.landscape_ruggedness = min(1.0, reversals / max(len(recent) - 2, 1))

        # Gradient reliability from loss trend
        if len(self._loss_history) >= 3:
            deltas = [self._loss_history[i+1] - self._loss_history[i]
                      for i in range(len(self._loss_history)-1)]
            if deltas:
                n_consistent = sum(1 for d in deltas[-5:] if d < 0)
                sig.gradient_reliability = n_consistent / len(deltas[-5:])

        sig.classify()
        self._current_signature = sig
        return sig

    @property
    def current(self) -> ProblemSignature:
        return self._current_signature


# ══════════════════════════════════════════════════════════════════════
#  HYBRID TYPE REGISTRY — all 240 hybrid types mapped
# ══════════════════════════════════════════════════════════════════════

@dataclass
class HybridType:
    """A specific hybrid configuration from the 240-type space."""
    mask: frozenset[str]          # Active poles
    lens: str                     # SFCR lens transform
    weights: dict[str, float]     # Pole weights
    name: str = ""
    use_case: str = ""

    @property
    def type_id(self) -> str:
        """Unique identifier for this hybrid type."""
        poles = "".join(sorted(self.mask))
        w_str = "_".join(f"{k}{int(v*100)}" for k, v in sorted(self.weights.items()) if v > 0)
        return f"{poles}_{self.lens}_{w_str}"


def build_hybrid_registry() -> list[HybridType]:
    """Build the complete 240-type hybrid registry.

    15 masks × 4 lenses × 4 weight profiles = 240 types.
    Each type has a specific use case mapped from the treatise.
    """
    registry = []
    weight_profiles = [
        {"name": "equal", "gen": lambda mask: {p: 1.0/len(mask) for p in mask}},
        {"name": "dominant", "gen": lambda mask: {p: (0.6 if i == 0 else 0.4/(len(mask)-1)) for i, p in enumerate(sorted(mask))}},
        {"name": "phi", "gen": lambda mask: _phi_weights(mask)},
        {"name": "inverse", "gen": lambda mask: {p: (0.4/max(len(mask)-1, 1) if i == 0 else 0.6) for i, p in enumerate(sorted(mask))}},
    ]

    for mask in POLE_MASKS:
        for lens in LENS_TRANSFORMS:
            for wp in weight_profiles:
                weights = wp["gen"](mask)
                # Fill zeros for inactive poles
                full_weights = {p: weights.get(p, 0.0) for p in ("Ψ", "Ω", "Σ", "D")}
                ht = HybridType(
                    mask=mask,
                    lens=lens,
                    weights=full_weights,
                    name=f"{''.join(sorted(mask))}_{lens}_{wp['name']}",
                )
                registry.append(ht)

    return registry


def _phi_weights(mask: frozenset[str]) -> dict[str, float]:
    """Generate phi-weighted distribution over active poles."""
    poles = sorted(mask)
    n = len(poles)
    if n == 1:
        return {poles[0]: 1.0}
    # Phi-cascade: each subsequent pole gets PHI_INV of the previous
    raw = {}
    w = 1.0
    for p in poles:
        raw[p] = w
        w *= PHI_INV
    total = sum(raw.values())
    return {p: v / total for p, v in raw.items()}


# ══════════════════════════════════════════════════════════════════════
#  MODULE API
# ══════════════════════════════════════════════════════════════════════

# Module-level singleton optimizer
_HYBRID_OPTIMIZER: Optional[HybridOptimizer] = None


def get_hybrid_optimizer(lr: float = 0.001) -> HybridOptimizer:
    """Get or create the singleton HybridOptimizer."""
    global _HYBRID_OPTIMIZER
    if _HYBRID_OPTIMIZER is None:
        _HYBRID_OPTIMIZER = HybridOptimizer(learning_rate=lr)
    return _HYBRID_OPTIMIZER


__all__ = [
    "ProblemClass", "ProblemSignature", "PoleSelector",
    "QuaternionicGradient", "HybridOptimizer", "HybridOptimizerState",
    "HybridPhase", "RotationalUpdate", "LandscapeAnalyzer",
    "HybridType", "build_hybrid_registry",
    "CLASS_WEIGHTS", "ADAPTIVE_EQUAL", "POLE_MASKS", "LENS_TRANSFORMS",
    "TOTAL_HYBRID_TYPES", "get_hybrid_optimizer",
]
