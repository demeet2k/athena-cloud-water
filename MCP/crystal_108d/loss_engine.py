# CRYSTAL: Xi108:W2:A5:S15 | face=F | node=322 | depth=1 | phase=Fixed
# METRO: Me
# BRIDGES: Xi108:W2:A5:S14→Xi108:W2:A5:S16→Xi108:W1:A5:S15→Xi108:W2:A4:S15→Xi108:W2:A6:S15

"""
Crystal Loss Engine — Quad-Polar Gradient Computation for the SFCR Neural System
==================================================================================
L = -mean(R * D) + lambda * disagreement + mu * (1 - element_balance)

Where:
  R = resonance (geometric quality of match)
  D = discrimination (observer selectivity)
  lambda, mu = regularization weights

Backpropagation uses the HYBRID OPTIMIZER (quad-polar, phase-structured,
landscape-adaptive) instead of flat Adam. Gradients are QUATERNIONIC:
  G = D_component + Ω·i + Σ·j + Ψ·k

The optimizer detects the optimization landscape (spectral gap, ruggedness,
gradient reliability) and selects pole weights adaptively per the
Adaptive Hybridization Framework (240 hybrid types).

Phase cycling: Ψ(init) → D+Ω(intensify) → Σ(diversify) → D+Ω(reinforce) → D(polish)
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .hybrid_math import (
    HybridOptimizer, QuaternionicGradient, LandscapeAnalyzer,
    RotationalUpdate, get_hybrid_optimizer,
)


@dataclass
class LossConfig:
    """Hyperparameters for crystal loss computation."""
    lambda_disagreement: float = 0.1    # weight for cross-observer disagreement penalty
    mu_sparsity: float = 0.5            # weight for element imbalance penalty (strong)
    learning_rate: float = 0.001
    momentum_beta1: float = 0.9         # Adam first moment decay
    momentum_beta2: float = 0.999       # Adam second moment decay
    weight_decay: float = 0.0001
    gradient_clip: float = 1.0
    epsilon: float = 1e-8               # Adam epsilon


class GradientAccumulator:
    """Quad-polar gradient accumulator with landscape-adaptive optimization.

    Wraps the HybridOptimizer to provide:
      - Quaternionic gradient accumulation (4-component, not scalar)
      - Phase-structured optimization (Ψ→Ω→Σ→D cycling)
      - Automatic landscape diagnosis and pole weight adaptation
      - Stuck detection with Σ-diversification
      - Backward-compatible scalar interface

    Replaces the previous flat Adam implementation.
    """

    def __init__(self, config: LossConfig = None):
        self.config = config or LossConfig()
        self._optimizer = HybridOptimizer(
            learning_rate=self.config.learning_rate,
            beta1=self.config.momentum_beta1,
            beta2=self.config.momentum_beta2,
            gradient_clip=self.config.gradient_clip,
            epsilon=self.config.epsilon,
            weight_decay=self.config.weight_decay,
        )
        self._landscape = LandscapeAnalyzer(rediagnose_interval=10)
        self._step: int = 0

    def accumulate(self, key: str, gradient: float, loss: float = 0.0) -> float:
        """Accumulate gradient with quad-polar hybrid optimizer.

        Lifts the scalar gradient into quaternionic space, applies the full
        hybrid optimizer (phase-aware, landscape-adaptive), then projects
        back to a scalar update.

        Returns the actual weight delta to apply (negative = decrease weight).
        """
        self._step += 1

        # Use the hybrid optimizer's scalar interface (lifts → optimizes → projects)
        return self._optimizer.scalar_update(key, gradient, loss)

    def accumulate_quaternionic(
        self, key: str, gradient: QuaternionicGradient, loss: float = 0.0
    ) -> QuaternionicGradient:
        """Accumulate a full quaternionic gradient.

        For new code that can work with 4-component gradients directly.
        Returns the quaternionic update vector.
        """
        self._step += 1
        return self._optimizer.accumulate(key, gradient, loss)

    def observe_landscape(self, scores: dict[str, float], loss: float):
        """Feed observation data to the landscape analyzer.

        Call this each step to enable automatic landscape diagnosis
        and pole weight adaptation.
        """
        self._landscape.observe(scores, loss)
        if self._landscape.should_rediagnose():
            sig = self._landscape.diagnose()
            self._optimizer.diagnose(scores, self._landscape._loss_history)

    def reset(self):
        """Reset accumulator state."""
        self._optimizer.reset()
        self._step = 0

    @property
    def optimizer_status(self) -> dict:
        """Current optimizer diagnostics."""
        return self._optimizer.status()

    @property
    def landscape_signature(self):
        """Current landscape diagnosis."""
        return self._landscape.current


class CrystalLoss:
    """Loss computation and backpropagation for the crystal neural system.

    Computes loss from swarm observations and produces weight deltas
    that can be applied to the MomentumField.
    """

    def __init__(self, config: LossConfig = None):
        self.config = config or LossConfig()
        self.accumulator = GradientAccumulator(self.config)
        self._loss_history: list[float] = []

    def compute_loss(self, swarm_observation) -> float:
        """Compute crystal loss from a swarm observation.

        L = -mean(R * D) + lambda * disagreement + mu * (1 - balance)

        Negative R*D product rewards high resonance with high discrimination.
        Disagreement penalty encourages cross-element consensus.
        Imbalance penalty encourages balanced element usage.
        """
        results = swarm_observation.observer_results
        if not results:
            return 0.0

        # Term 1: -mean(R * D) — reward resonance × discrimination
        rd_products = []
        for r in results:
            rd_products.append(r.resonance * r.discrimination)
        mean_rd = sum(rd_products) / len(rd_products)

        # Term 2: disagreement penalty
        disagreement = 1.0 - swarm_observation.swarm_coherence

        # Term 3: element imbalance penalty
        imbalance = 1.0 - swarm_observation.element_balance

        loss = -mean_rd + self.config.lambda_disagreement * disagreement + self.config.mu_sparsity * imbalance

        self._loss_history.append(loss)
        return loss

    def backpropagate(self, swarm_observation, loss: float) -> dict:
        """Compute weight deltas by backpropagating through the quad-polar operator space.

        Chain rule through:
          loss → R*D product → per-observer scores → momentum weights
          loss → disagreement → bridge weights
          loss → imbalance → path weights

        UPGRADE: Gradients are now QUATERNIONIC (4-component vectors in the
        {D, Ω, Σ, Ψ} operator space). Each element's gradient carries information
        from all 4 poles, weighted by the optimizer's current phase and landscape
        diagnosis. The optimizer adapts pole weights per the Adaptive Hybridization
        Framework (240 hybrid types, 5 problem classes).

        Returns dict of weight deltas: {face: {shell: delta}} for momentum field,
        plus bridge and path deltas, plus quaternionic gradient metadata.
        """
        results = swarm_observation.observer_results
        if not results:
            return {}

        deltas = {
            "momentum": {},     # {face: {shell: delta}}
            "bridge": {},       # {bridge_key: delta}
            "path": {},         # {face: delta}
            "quaternionic": {}, # {face: {shell: QuaternionicGradient}} — full 4D gradient
        }

        # Feed landscape observation for adaptive pole selection
        # Build proxy observation scores from swarm data
        proxy_scores = {}
        for r in results:
            proxy_scores[f"res_{r.agent.element}"] = r.resonance
            proxy_scores[f"disc_{r.agent.element}"] = r.discrimination
        self.accumulator.observe_landscape(proxy_scores, loss)

        # ── Gradient through Term 1: R*D product (QUATERNIONIC) ──
        # Each observer's gradient is lifted into the 4-pole space:
        #   D-component: discrete improvement from local search
        #   Ω-component: continuous gradient from resonance landscape
        #   Σ-component: stochastic escape signal (from discrimination variance)
        #   Ψ-component: spectral alignment (from element structure)
        for r in results:
            face = r.agent.element
            grad_r = -r.discrimination  # d(loss)/d(resonance) = -D

            # Compute per-pole gradient components
            # Ω: gradient direction from continuous resonance field
            omega_signal = grad_r * r.resonance  # resonance × discrimination coupling
            # Σ: stochastic signal from discrimination variance across observers
            sigma_signal = grad_r * (1.0 - swarm_observation.swarm_coherence)
            # Ψ: spectral signal from element structure
            psi_signal = grad_r * (swarm_observation.element_balance - 0.5)

            for i, doc_id in enumerate(r.ranked_doc_ids[:5]):
                try:
                    num = int(doc_id.replace("DOC", "").replace("SHARD", ""))
                except (ValueError, AttributeError):
                    num = hash(doc_id)
                shell = (abs(num) % 36) + 1

                rank_weight = 1.0 / (i + 1)
                scale = rank_weight / max(len(results), 1)

                # Construct quaternionic gradient for this position
                qgrad = QuaternionicGradient(
                    d=grad_r * scale,           # D: discrete component
                    omega=omega_signal * scale,  # Ω: continuous component
                    sigma=sigma_signal * scale,  # Σ: stochastic component
                    psi=psi_signal * scale,      # Ψ: spectral component
                )

                # Accumulate via hybrid optimizer (phase-aware, landscape-adaptive)
                key = f"momentum:{face}:{shell}"
                update = self.accumulator.accumulate_quaternionic(key, qgrad, loss)

                # Scalar delta for momentum field (backward compatible)
                delta = update.weighted_scalar(self.accumulator._optimizer._phase_weights())

                if face not in deltas["momentum"]:
                    deltas["momentum"][face] = {}
                    deltas["quaternionic"][face] = {}
                deltas["momentum"][face][shell] = (
                    deltas["momentum"][face].get(shell, 0.0) + delta
                )
                # Store full quaternionic gradient for advanced consumers
                deltas["quaternionic"].setdefault(face, {})[shell] = update

        # ── Gradient through Term 2: disagreement (QUATERNIONIC) ──
        for signal in swarm_observation.cross_signals:
            grad_bridge = self.config.lambda_disagreement * signal.gradient_signal
            # Bridge gradients are primarily D+Ω (structure + continuous)
            qgrad = QuaternionicGradient(
                d=grad_bridge * 0.5,
                omega=grad_bridge * 0.3,
                sigma=grad_bridge * 0.1,
                psi=grad_bridge * 0.1,
            )
            key = f"bridge:{signal.bridge_key}"
            update = self.accumulator.accumulate_quaternionic(key, qgrad, loss)
            deltas["bridge"][signal.bridge_key] = update.weighted_scalar(
                self.accumulator._optimizer._phase_weights()
            )

        # ── Gradient through Term 3: imbalance (QUATERNIONIC) ──
        contribs = swarm_observation.element_contributions
        if contribs:
            mean_c = sum(contribs.values()) / 4.0
            for face, val in contribs.items():
                imbalance = mean_c - val
                # Imbalance gradients are primarily Ψ+D (spectral rebalancing)
                qgrad = QuaternionicGradient(
                    d=self.config.mu_sparsity * imbalance * 0.4,
                    omega=self.config.mu_sparsity * imbalance * 0.1,
                    sigma=self.config.mu_sparsity * imbalance * 0.1,
                    psi=self.config.mu_sparsity * imbalance * 0.4,
                )
                key = f"path:{face}"
                update = self.accumulator.accumulate_quaternionic(key, qgrad, loss)
                deltas["path"][face] = update.weighted_scalar(
                    self.accumulator._optimizer._phase_weights()
                )

        # ── Weight decay (applied to scalar deltas) ──
        if self.config.weight_decay > 0:
            for face in deltas.get("momentum", {}):
                for shell in deltas["momentum"][face]:
                    deltas["momentum"][face][shell] -= (
                        self.config.weight_decay * deltas["momentum"][face][shell]
                    )

        return deltas

    @property
    def loss_trend(self) -> list[float]:
        """Recent loss values for monitoring."""
        return self._loss_history[-50:]

    @property
    def latest_loss(self) -> float:
        """Most recent loss value."""
        return self._loss_history[-1] if self._loss_history else 0.0

    def summary(self) -> str:
        """Human-readable loss summary with hybrid optimizer status."""
        if not self._loss_history:
            return "No loss computed yet."
        recent = self._loss_history[-10:]
        opt = self.accumulator.optimizer_status
        return (
            f"Loss: {recent[-1]:.6f} "
            f"(mean={sum(recent)/len(recent):.6f}, "
            f"min={min(recent):.6f}, "
            f"max={max(recent):.6f}, "
            f"n={len(self._loss_history)}) | "
            f"Phase={opt.get('phase', '?')} "
            f"Class={opt.get('problem_class', '?')} "
            f"Pole={opt.get('dominant_pole', '?')}"
        )


# Module-level singleton
_LOSS: Optional[CrystalLoss] = None


def get_loss_engine(config: LossConfig = None) -> CrystalLoss:
    """Get or create the singleton CrystalLoss."""
    global _LOSS
    if _LOSS is None or config is not None:
        _LOSS = CrystalLoss(config=config)
    return _LOSS


__all__ = ["CrystalLoss", "LossConfig", "GradientAccumulator", "get_loss_engine"]
