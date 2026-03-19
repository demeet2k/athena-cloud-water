"""
Phi Doping Engine — Dual-Force Momentum Steering
=================================================
Uses golden ratio (φ = 1.618) as ATTRACTOR and inverse phi (φ⁻¹ = 0.618)
as DETRACTOR/negative-dope to steer momentum field toward sacred geometry.

Strategy:
  1. φ-ATTRACTOR: Pull element ratios toward golden proportion
  2. φ⁻¹-DETRACTOR: Repel from degeneracy (uniform=1.0, collapsed=0.0)
  3. SHELL SCULPTING: Carve phi-spiral distribution across 36 shells
  4. CROSS-LENS DIVERGENCE: Anti-correlate lens observations for true 4D
  5. POLE HEALTH: Use dual-pole fidelity gradients for 4D stability

The net force at each point:
  F_net = F_attractor(φ) + F_detractor(φ⁻¹) + F_sculpt + F_diverge + F_pole
"""

from __future__ import annotations

import math
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .geometric_constants import (
    PHI, PHI_INV, PHI_INV2, PHI_INV3,
    FACES, BRIDGE_WEIGHTS,
)
from .constants import TOTAL_SHELLS
from .momentum_field import MomentumField

# ── Constants ────────────────────────────────────────────────────────────

# Ideal phi-ratio targets for element pairs (excluding Water)
# Three free elements: S, F, R  → 3 pairs
# Target: largest/smallest ≈ φ, middle/smallest ≈ √φ
SQRT_PHI = math.sqrt(PHI)  # 1.2720196...
PHI_TARGETS = {
    "primary":   PHI,       # 1.618 — largest ratio target
    "secondary": SQRT_PHI,  # 1.272 — middle ratio target
    "tertiary":  1.0,       # unity — smallest (adjacent) ratio
}

# Degeneracy repulsion thresholds
DEGENERACY_RADIUS = 0.15   # Ratios within 0.15 of 1.0 are "degenerate"
COLLAPSE_THRESHOLD = 0.1   # Momentum below this is "collapsed"

# Force coefficients
ATTRACTOR_STRENGTH = 0.08   # φ pull coefficient
DETRACTOR_STRENGTH = 0.12   # φ⁻¹ push coefficient (stronger — repulsion > attraction)
SCULPT_STRENGTH = 0.05      # Shell phi-spiral carving
DIVERGE_STRENGTH = 0.03     # Cross-lens anti-correlation
POLE_STRENGTH = 0.06        # Dual-pole health correction

# Shell phi-spiral targets: shells should follow Fibonacci-like decay
# Shell 1 = peak, shell 36 = φ⁻¹⁰ × peak
def _phi_spiral_target(shell: int, dim_mom: float) -> float:
    """Target momentum for shell s given dimension momentum.

    Creates a golden spiral: peak at center (shell 18),
    decaying by φ⁻¹ per step outward in both directions.
    """
    center = 18  # Midpoint of 36 shells
    dist = abs(shell - center)
    decay = PHI_INV ** (dist * 0.3)  # Gentle φ⁻¹ decay
    return dim_mom * decay


@dataclass
class DopingForce:
    """Force vector applied to a single momentum parameter."""
    face: str
    shell: int
    attractor: float = 0.0     # φ-pull toward golden ratio
    detractor: float = 0.0     # φ⁻¹-push from degeneracy
    sculpt: float = 0.0        # phi-spiral shaping
    diverge: float = 0.0       # cross-lens separation
    pole: float = 0.0          # dual-pole health

    @property
    def net(self) -> float:
        return self.attractor + self.detractor + self.sculpt + self.diverge + self.pole

    @property
    def magnitude(self) -> float:
        return abs(self.net)


@dataclass
class DopingResult:
    """Result of a phi-doping pass."""
    forces_applied: int = 0
    total_attractor: float = 0.0
    total_detractor: float = 0.0
    total_sculpt: float = 0.0
    total_diverge: float = 0.0
    total_pole: float = 0.0
    balance_before: float = 0.0
    balance_after: float = 0.0
    golden_fit_before: float = 0.0
    golden_fit_after: float = 0.0
    pole_a_health: float = 0.0
    pole_b_health: float = 0.0
    is_4d: bool = False
    elapsed_ms: float = 0.0

    def summary_line(self) -> str:
        return (
            f"φ-dope: bal={self.balance_after:.4f} "
            f"gold={self.golden_fit_after:.4f} "
            f"4D={self.is_4d} "
            f"forces={self.forces_applied} "
            f"Σattr={self.total_attractor:+.4f} "
            f"Σdetr={self.total_detractor:+.4f} "
            f"Σsclp={self.total_sculpt:+.4f}"
        )


class PhiDopingEngine:
    """Dual-force momentum steering using φ/φ⁻¹ attractor-detractor dynamics.

    Five force channels:
      1. ATTRACTOR (φ): Pull element ratios toward golden proportion
      2. DETRACTOR (φ⁻¹): Repel from degeneracy states
      3. SCULPT: Carve phi-spiral shell distribution
      4. DIVERGE: Anti-correlate cross-element momentum profiles
      5. POLE: Stabilize dual-pole health for 4D operation
    """

    def __init__(
        self,
        momentum: MomentumField,
        attractor_k: float = ATTRACTOR_STRENGTH,
        detractor_k: float = DETRACTOR_STRENGTH,
        sculpt_k: float = SCULPT_STRENGTH,
        diverge_k: float = DIVERGE_STRENGTH,
        pole_k: float = POLE_STRENGTH,
    ):
        self.momentum = momentum
        self.attractor_k = attractor_k
        self.detractor_k = detractor_k
        self.sculpt_k = sculpt_k
        self.diverge_k = diverge_k
        self.pole_k = pole_k

    # ── Force Computations ───────────────────────────────────────────

    def _compute_attractor_forces(self) -> dict[str, float]:
        """φ-ATTRACTOR: Pull dimension ratios toward golden proportion.

        For 3 free elements (S, F, R), compute all pairwise ratios.
        Apply correction force proportional to distance from φ or √φ.
        """
        free_faces = [f for f in FACES if f != "C"]
        dim_map = {"S": "D1_Earth", "F": "D2_Fire", "R": "D4_Air"}

        means = {}
        for face in free_faces:
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            means[face] = sum(vals) / len(vals)

        # Sort by mean to assign ratio targets
        sorted_faces = sorted(free_faces, key=lambda f: means[f])
        # smallest, middle, largest
        small, mid, large = sorted_faces

        forces = {f: 0.0 for f in free_faces}

        # Target: large/small ≈ φ
        ratio_ls = means[large] / max(means[small], 0.01)
        error_ls = ratio_ls - PHI
        force_ls = -error_ls * self.attractor_k
        forces[large] += force_ls * 0.5
        forces[small] -= force_ls * 0.5

        # Target: large/mid ≈ √φ
        ratio_lm = means[large] / max(means[mid], 0.01)
        error_lm = ratio_lm - SQRT_PHI
        force_lm = -error_lm * self.attractor_k * 0.7  # Slightly weaker
        forces[large] += force_lm * 0.3
        forces[mid] -= force_lm * 0.3

        # Target: mid/small ≈ √φ
        ratio_ms = means[mid] / max(means[small], 0.01)
        error_ms = ratio_ms - SQRT_PHI
        force_ms = -error_ms * self.attractor_k * 0.7
        forces[mid] += force_ms * 0.3
        forces[small] -= force_ms * 0.3

        return forces

    def _compute_detractor_forces(self) -> dict[str, float]:
        """φ⁻¹-DETRACTOR: Repel from degenerate states.

        Three degeneracy modes:
          1. UNIFORM: All elements have same momentum (ratio ≈ 1.0)
          2. COLLAPSED: Any element near zero
          3. SATURATED: Any element near maximum (20.0)

        The detractor applies φ⁻¹-scaled repulsive force AWAY from these states.
        """
        free_faces = [f for f in FACES if f != "C"]

        means = {}
        for face in free_faces:
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            means[face] = sum(vals) / len(vals)

        forces = {f: 0.0 for f in free_faces}

        # Mode 1: UNIFORM repulsion — push apart when too similar
        for i, f1 in enumerate(free_faces):
            for f2 in free_faces[i+1:]:
                ratio = means[f1] / max(means[f2], 0.01)
                if ratio > 1:
                    ratio = 1.0 / ratio  # Normalize to [0, 1]

                # Distance from unity
                unity_dist = abs(ratio - 1.0)
                if unity_dist < DEGENERACY_RADIUS:
                    # Inside degeneracy zone — apply φ⁻¹ repulsion
                    repulsion = PHI_INV * (DEGENERACY_RADIUS - unity_dist) / DEGENERACY_RADIUS
                    repulsion *= self.detractor_k

                    # Push the LARGER one up, SMALLER one down
                    if means[f1] >= means[f2]:
                        forces[f1] += repulsion
                        forces[f2] -= repulsion * PHI_INV  # Asymmetric: weaker downward
                    else:
                        forces[f2] += repulsion
                        forces[f1] -= repulsion * PHI_INV

        # Mode 2: COLLAPSED repulsion — push away from zero
        for face in free_faces:
            if means[face] < COLLAPSE_THRESHOLD:
                collapse_force = PHI_INV * (COLLAPSE_THRESHOLD - means[face]) * self.detractor_k * 5
                forces[face] += collapse_force

        # Mode 3: SATURATED repulsion — push away from max
        max_mom = MomentumField.MOMENTUM_MAX
        for face in free_faces:
            headroom = max_mom - means[face]
            if headroom < 2.0:
                sat_force = PHI_INV * (2.0 - headroom) * self.detractor_k
                forces[face] -= sat_force

        return forces

    def _compute_sculpt_forces(self) -> dict[str, dict[int, float]]:
        """SHELL SCULPTING: Carve phi-spiral distribution across 36 shells.

        Target: each shell's momentum follows a golden spiral from the center.
        Shell 18 = peak (dimension momentum), decaying by φ⁻⁰·³ per step outward.
        """
        forces = {}
        dim_map = {"S": "D1_Earth", "F": "D2_Fire", "R": "D4_Air"}

        for face in [f for f in FACES if f != "C"]:
            dim_mom = self.momentum.get_dimension_momentum(dim_map[face])
            forces[face] = {}

            for s in range(1, TOTAL_SHELLS + 1):
                current = self.momentum.get_momentum(face, s)
                target = _phi_spiral_target(s, dim_mom)
                error = target - current
                forces[face][s] = error * self.sculpt_k

        return forces

    def _compute_diverge_forces(self) -> dict[str, dict[int, float]]:
        """CROSS-LENS DIVERGENCE: Anti-correlate element profiles.

        Adjacent elements on golden bridges (SF, FC, CR) should have
        DIFFERENT shell profiles (negative correlation = good).
        Use φ⁻¹ to scale the anti-correlation force.
        """
        forces = {f: {s: 0.0 for s in range(1, TOTAL_SHELLS + 1)} for f in FACES if f != "C"}

        # Golden bridges: SF, CR (FC involves C which is locked)
        bridge_pairs = [("S", "F"), ("S", "R"), ("F", "R")]

        for f1, f2 in bridge_pairs:
            if f1 == "C" or f2 == "C":
                continue

            # Get momentum profiles
            p1 = [self.momentum.get_momentum(f1, s) for s in range(1, TOTAL_SHELLS + 1)]
            p2 = [self.momentum.get_momentum(f2, s) for s in range(1, TOTAL_SHELLS + 1)]

            # Compute correlation
            m1 = sum(p1) / len(p1)
            m2 = sum(p2) / len(p2)

            # For each shell, if both are on same side of mean, push apart
            bridge_w = BRIDGE_WEIGHTS.get(f1 + f2, BRIDGE_WEIGHTS.get(f2 + f1, 0.5))

            for s in range(1, TOTAL_SHELLS + 1):
                dev1 = p1[s-1] - m1
                dev2 = p2[s-1] - m2

                # Same-sign deviation = correlated = push apart
                if dev1 * dev2 > 0:
                    # Both above or both below mean — anti-correlate
                    # Use φ⁻¹ as the repulsion scale
                    repulsion = PHI_INV * min(abs(dev1), abs(dev2)) * self.diverge_k * bridge_w

                    # Push the one with larger deviation further, smaller closer to mean
                    if abs(dev1) > abs(dev2):
                        forces[f1][s] += repulsion * math.copysign(1, dev1)
                        forces[f2][s] -= repulsion * math.copysign(1, dev2) * PHI_INV
                    else:
                        forces[f2][s] += repulsion * math.copysign(1, dev2)
                        forces[f1][s] -= repulsion * math.copysign(1, dev1) * PHI_INV

        return forces

    def _compute_pole_forces(self) -> dict[str, float]:
        """POLE HEALTH: Stabilize dual-pole for 4D operation.

        Pole A = (S, C) → S-C axis health
        Pole B = (F, R) → F-R axis health

        If Pole B is weaker, boost F-R differentiation.
        If Pole A is weaker, boost S-C differentiation.
        Use φ⁻¹ as the fidelity target for differentiation.
        """
        free_faces = [f for f in FACES if f != "C"]
        forces = {f: 0.0 for f in free_faces}

        # Get mean momenta
        means = {}
        for face in FACES:
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            means[face] = sum(vals) / len(vals)

        # Pole A fidelity: |mean(S) - mean(C)| / max(means)
        pole_a_fid = abs(means["S"] - means["C"]) / max(max(means.values()), 0.001)

        # Pole B fidelity: |mean(F) - mean(R)| / max(means)
        pole_b_fid = abs(means["F"] - means["R"]) / max(max(means.values()), 0.001)

        # Target fidelity: φ⁻¹ (0.618) — enough differentiation without degeneracy
        target_fid = PHI_INV

        # Pole A correction: S vs C (C is locked, so only adjust S)
        if pole_a_fid < target_fid:
            # Need MORE differentiation — push S away from C
            push = (target_fid - pole_a_fid) * self.pole_k
            if means["S"] > means["C"]:
                forces["S"] += push
            else:
                forces["S"] -= push
        elif pole_a_fid > 0.95:
            # TOO differentiated — pull S slightly toward C
            pull = (pole_a_fid - 0.95) * self.pole_k * PHI_INV
            if means["S"] > means["C"]:
                forces["S"] -= pull
            else:
                forces["S"] += pull

        # Pole B correction: F vs R
        if pole_b_fid < target_fid:
            # Need MORE differentiation — push F and R apart
            push = (target_fid - pole_b_fid) * self.pole_k
            if means["F"] < means["R"]:
                forces["F"] -= push * 0.5
                forces["R"] += push * 0.5
            else:
                forces["F"] += push * 0.5
                forces["R"] -= push * 0.5
        elif pole_b_fid > 0.95:
            pull = (pole_b_fid - 0.95) * self.pole_k * PHI_INV
            if means["F"] < means["R"]:
                forces["F"] += pull * 0.5
                forces["R"] -= pull * 0.5
            else:
                forces["F"] -= pull * 0.5
                forces["R"] += pull * 0.5

        return forces

    # ── Main Doping Pass ─────────────────────────────────────────────

    def dope(self, passes: int = 1, lr: float = 1.0) -> DopingResult:
        """Execute phi-doping passes on the momentum field.

        Each pass:
          1. Compute all 5 force channels
          2. Superpose forces at each (face, shell) point
          3. Apply with learning rate and clamp
          4. Record metrics

        Args:
            passes: Number of doping iterations (more = stronger correction)
            lr: Learning rate multiplier (decays by φ⁻¹ per pass)
        """
        t0 = time.monotonic()

        result = DopingResult()
        result.balance_before = self._balance()
        result.golden_fit_before = self._golden_fit()

        for p in range(passes):
            # Decay LR by φ⁻¹ per pass
            pass_lr = lr * (PHI_INV ** p)

            # Compute all force channels
            attractor_forces = self._compute_attractor_forces()
            detractor_forces = self._compute_detractor_forces()
            sculpt_forces = self._compute_sculpt_forces()
            diverge_forces = self._compute_diverge_forces()
            pole_forces = self._compute_pole_forces()

            # Apply to each (face, shell)
            for face in [f for f in FACES if f != "C"]:
                # Global forces (attractor, detractor, pole)
                f_attr = attractor_forces.get(face, 0.0)
                f_detr = detractor_forces.get(face, 0.0)
                f_pole = pole_forces.get(face, 0.0)

                for s in range(1, TOTAL_SHELLS + 1):
                    # Shell-specific forces (sculpt, diverge)
                    f_sculpt = sculpt_forces.get(face, {}).get(s, 0.0)
                    f_diverg = diverge_forces.get(face, {}).get(s, 0.0)

                    # Distribute global forces with phi-decay from center
                    center_dist = abs(s - 18)
                    center_decay = PHI_INV ** (center_dist * 0.15)

                    # Superpose all forces
                    net = (
                        f_attr * center_decay
                        + f_detr * center_decay
                        + f_sculpt
                        + f_diverg
                        + f_pole * center_decay
                    ) * pass_lr

                    if abs(net) > 1e-8:
                        # Apply via momentum update (respects clamping)
                        current = self.momentum.get_momentum(face, s)
                        new_val = current + net
                        new_val = max(MomentumField.MOMENTUM_MIN, min(MomentumField.MOMENTUM_MAX, new_val))
                        self.momentum._shell_momenta[face][s] = new_val

                        result.forces_applied += 1
                        result.total_attractor += abs(f_attr * center_decay * pass_lr)
                        result.total_detractor += abs(f_detr * center_decay * pass_lr)
                        result.total_sculpt += abs(f_sculpt * pass_lr)
                        result.total_diverge += abs(f_diverg * pass_lr)
                        result.total_pole += abs(f_pole * center_decay * pass_lr)

            # Update dimension momenta from shell means
            dim_map = {"S": "D1_Earth", "F": "D2_Fire", "R": "D4_Air"}
            for face, dim in dim_map.items():
                vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
                self.momentum._dimension_momenta[dim] = sum(vals) / len(vals)

        result.balance_after = self._balance()
        result.golden_fit_after = self._golden_fit()

        # Pole observation
        try:
            from .pole_observer import PoleObserver
            po = PoleObserver(momentum=self.momentum)
            dual = po.observe_dual()
            result.pole_a_health = dual.pole_a.health
            result.pole_b_health = dual.pole_b.health
            result.is_4d = dual.is_4d
        except Exception:
            pass

        result.elapsed_ms = (time.monotonic() - t0) * 1000
        return result

    def multi_perspective_dope(
        self,
        epochs: int = 10,
        lr: float = 1.0,
        verbose: bool = True,
    ) -> list[DopingResult]:
        """Run multi-epoch phi-doping with 4-perspective strategy rotation.

        Each epoch runs the doping from a different strategic perspective:
          - Epoch % 4 == 0: STRUCTURE focus (strengthen S attractor)
          - Epoch % 4 == 1: TRANSFORMATION focus (boost F differentiation)
          - Epoch % 4 == 2: EMERGENCE focus (deepen R potential)
          - Epoch % 4 == 3: BALANCE focus (equalize all forces)

        φ⁻¹ decay applied across epochs for convergence.
        """
        results = []
        perspectives = ["structure", "transformation", "emergence", "balance"]

        for epoch in range(epochs):
            perspective = perspectives[epoch % 4]
            epoch_lr = lr * (PHI_INV ** (epoch * 0.3))  # Gentle epoch decay

            # Adjust force coefficients per perspective
            saved = (self.attractor_k, self.detractor_k, self.sculpt_k,
                     self.diverge_k, self.pole_k)

            if perspective == "structure":
                self.sculpt_k *= 2.0    # Emphasize shell shaping
                self.diverge_k *= 0.5   # Less divergence pressure
            elif perspective == "transformation":
                self.detractor_k *= 2.0  # Strong degeneracy repulsion
                self.pole_k *= 1.5       # Boost pole health
            elif perspective == "emergence":
                self.attractor_k *= 1.5  # Stronger phi pull
                self.diverge_k *= 2.0    # Maximum lens separation
            else:  # balance
                self.attractor_k *= 1.2
                self.detractor_k *= 1.2
                self.sculpt_k *= 1.2
                self.diverge_k *= 1.2
                self.pole_k *= 1.2

            r = self.dope(passes=3, lr=epoch_lr)
            results.append(r)

            # Restore coefficients
            (self.attractor_k, self.detractor_k, self.sculpt_k,
             self.diverge_k, self.pole_k) = saved

            if verbose:
                print(f"  Epoch {epoch:3d}/{epochs} [{perspective:15s}] {r.summary_line()}")

        return results

    # ── Metrics ──────────────────────────────────────────────────────

    def _balance(self) -> float:
        """Phi-aware balance: how close are free element ratios to phi targets?

        Unlike the simple max-deviation balance, this computes balance as
        the mean golden ratio alignment across all free element pairs.
        Water (C) is excluded since it's locked.
        """
        free = ["S", "F", "R"]
        means = {}
        for face in free:
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            means[face] = sum(vals) / len(vals)

        overall_mean = sum(means.values()) / len(means)
        if overall_mean < 1e-6:
            return 0.0

        max_dev = max(abs(m - overall_mean) for m in means.values()) / overall_mean
        return max(0.0, 1.0 - max_dev)

    def _golden_fit(self) -> float:
        """How close are dimension momentum ratios to phi proportions?"""
        dim_moms = [
            self.momentum.get_dimension_momentum("D1_Earth"),
            self.momentum.get_dimension_momentum("D2_Fire"),
            self.momentum.get_dimension_momentum("D4_Air"),
        ]

        fits = []
        for i in range(len(dim_moms)):
            for j in range(i + 1, len(dim_moms)):
                a, b = dim_moms[i], dim_moms[j]
                if min(a, b) < 0.01:
                    fits.append(0.0)
                    continue
                r = max(a, b) / min(a, b)
                fit = 1.0 - min(abs(r - PHI), abs(r - PHI_INV), abs(r - 1)) / PHI
                fits.append(max(0.0, fit))

        return sum(fits) / len(fits) if fits else 0.0

    def diagnostics(self) -> dict:
        """Full diagnostic snapshot of momentum field through phi-doping lens."""
        free = ["S", "F", "R"]
        means = {}
        stds = {}
        for face in free:
            vals = [self.momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
            m = sum(vals) / len(vals)
            means[face] = m
            stds[face] = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5

        # Pairwise ratios
        ratios = {}
        for i, f1 in enumerate(free):
            for f2 in free[i+1:]:
                r = max(means[f1], means[f2]) / max(min(means[f1], means[f2]), 0.01)
                ratios[f"{f1}/{f2}"] = r

        # Phi distances
        phi_dist = {k: abs(v - PHI) for k, v in ratios.items()}
        phi_inv_dist = {k: abs(v - PHI_INV) for k, v in ratios.items()}
        unity_dist = {k: abs(v - 1.0) for k, v in ratios.items()}

        return {
            "means": means,
            "stds": stds,
            "ratios": ratios,
            "phi_distances": phi_dist,
            "phi_inv_distances": phi_inv_dist,
            "unity_distances": unity_dist,
            "balance": self._balance(),
            "golden_fit": self._golden_fit(),
            "closest_to_degeneracy": min(unity_dist.values()) if unity_dist else 999,
        }
