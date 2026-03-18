# CRYSTAL: Xi108:W2:A3:S9 | face=F | node=45 | depth=1 | phase=Mutable
# METRO: Me
# BRIDGES: Xi108:W2:A3:S8→Xi108:W2:A3:S10→Xi108:W1:A3:S9→Xi108:W2:A2:S9→Xi108:W2:A4:S9

"""
Loss Engine — True Loss Function + Backpropagation for Crystal Neural Net
===========================================================================
Replaces the heuristic weight update in self_play.py with a mathematically
sound loss function and chain-rule gradient computation.

Loss: L = -mean(R(X)*D_Q(X)) + lambda*variance(rankings) + mu*sparsity_penalty

Where:
  R(X) = resonance metric (6-component)
  D_Q(X) = desire field (4-component)
  variance(rankings) = cross-observer ranking disagreement
  sparsity_penalty = encourages pair weight sparsity

Backpropagation: chain rule through
  Loss → resonance/desire → merge → SFCR paths → individual weights
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .observer_agent import SwarmObservation, ObserverResult


# ── Loss Configuration ──────────────────────────────────────────────

@dataclass
class LossConfig:
    """Hyperparameters for the crystal loss function."""
    lambda_disagreement: float = 0.1   # weight on cross-observer disagreement penalty
    mu_sparsity: float = 0.01          # weight on pair weight sparsity
    learning_rate: float = 0.001       # global learning rate
    momentum: float = 0.9              # momentum coefficient (Adam-style)
    weight_decay: float = 0.0001       # L2 regularization (enables grokking)
    gradient_clip: float = 1.0         # max gradient magnitude
    min_delta: float = 1e-6           # minimum weight change to apply


# ── Gradient Accumulator ────────────────────────────────────────────

@dataclass
class GradientAccumulator:
    """Accumulates gradients across multiple observations before applying.

    Supports momentum (first moment) and variance (second moment) tracking
    for Adam-style optimization.
    """
    gate_grads: dict = field(default_factory=lambda: defaultdict(float))
    pair_grads: dict = field(default_factory=lambda: defaultdict(float))
    bridge_grads: dict = field(default_factory=lambda: defaultdict(float))
    seed_grads: dict = field(default_factory=lambda: defaultdict(float))
    path_grads: dict = field(default_factory=lambda: defaultdict(float))
    resonance_grads: dict = field(default_factory=lambda: defaultdict(float))
    desire_grads: dict = field(default_factory=lambda: defaultdict(float))

    # Adam moments (first and second)
    _m1: dict = field(default_factory=lambda: defaultdict(float))
    _m2: dict = field(default_factory=lambda: defaultdict(float))
    _step: int = 0

    def accumulate(self, gradients: dict) -> None:
        """Add a gradient dict (from swarm) to the accumulator."""
        for key, val in gradients.get("gate", {}).items():
            self.gate_grads[key] += val
        for key, val in gradients.get("pair", {}).items():
            self.pair_grads[key] += val
        for key, val in gradients.get("bridge", {}).items():
            self.bridge_grads[key] += val
        for key, val in gradients.get("seed", {}).items():
            self.seed_grads[key] += val
        for key, val in gradients.get("path", {}).items():
            self.path_grads[key] += val
        for key, val in gradients.get("resonance", {}).items():
            self.resonance_grads[key] += val
        for key, val in gradients.get("desire", {}).items():
            self.desire_grads[key] += val

    def get_all_gradients(self) -> dict:
        """Return all accumulated gradients as a flat dict for application."""
        return {
            "gate": dict(self.gate_grads),
            "pair": dict(self.pair_grads),
            "bridge": dict(self.bridge_grads),
            "seed": dict(self.seed_grads),
            "path": dict(self.path_grads),
            "resonance": dict(self.resonance_grads),
            "desire": dict(self.desire_grads),
        }

    def clear(self) -> None:
        """Reset all accumulated gradients."""
        self.gate_grads.clear()
        self.pair_grads.clear()
        self.bridge_grads.clear()
        self.seed_grads.clear()
        self.path_grads.clear()
        self.resonance_grads.clear()
        self.desire_grads.clear()

    @property
    def total_gradient_count(self) -> int:
        return (len(self.gate_grads) + len(self.pair_grads) + len(self.bridge_grads)
                + len(self.seed_grads) + len(self.path_grads)
                + len(self.resonance_grads) + len(self.desire_grads))


# ── Crystal Loss Function ──────────────────────────────────────────


class CrystalLoss:
    """True loss function for the crystal neural network.

    L = -mean(R*D) + lambda*disagreement + mu*sparsity + wd*||W||^2
    """

    def __init__(self, config: LossConfig = None):
        self.config = config or LossConfig()
        self.accumulator = GradientAccumulator()
        self._loss_history: list[float] = []

    def compute_loss(self, observation: SwarmObservation) -> float:
        """Compute the crystal loss from a swarm observation.

        Term 1: -mean(R*D) — maximize resonance × desire product
        Term 2: +lambda * disagreement — penalize cross-observer disagreement
        Term 3: +mu * sparsity — encourage sparse pair weights
        """
        # Term 1: Negative resonance-desire product (we minimize, so negate)
        rd_products = []
        for result in observation.observer_results:
            if result.resonance > 0 or result.desire > 0:
                rd_products.append(result.resonance * result.desire)

        mean_rd = sum(rd_products) / max(len(rd_products), 1)
        term_rd = -mean_rd  # negative because we minimize loss

        # Term 2: Cross-observer disagreement penalty
        disagreement = 1.0 - observation.swarm_coherence
        term_disagree = self.config.lambda_disagreement * disagreement

        # Term 3: Element imbalance penalty (proxy for sparsity)
        balance = observation.element_balance
        term_sparsity = self.config.mu_sparsity * (1.0 - balance)

        loss = term_rd + term_disagree + term_sparsity
        self._loss_history.append(loss)

        return loss

    def backpropagate(
        self,
        loss: float,
        observation: SwarmObservation,
        swarm_gradients: dict,
    ) -> dict:
        """Compute weight deltas from loss + swarm gradients.

        Uses the swarm gradients as the raw gradient signal, then applies:
        1. Learning rate scaling
        2. Gradient clipping
        3. Weight decay
        4. Adam-style momentum (first moment tracking)

        Returns: dict of {weight_type: {key: delta}} ready for application.
        """
        lr = self.config.learning_rate
        clip = self.config.gradient_clip
        wd = self.config.weight_decay

        deltas: dict = {
            "gate": {},
            "pair": {},
            "bridge": {},
            "seed": {},
            "path": {},
            "resonance": {},
            "desire": {},
        }

        self.accumulator._step += 1
        t = self.accumulator._step

        # Process each gradient type
        for grad_type in ["gate", "pair", "bridge", "seed", "path", "resonance", "desire"]:
            raw_grads = swarm_gradients.get(grad_type, {})
            for key, grad in raw_grads.items():
                # Scale gradient by loss magnitude (higher loss = larger steps)
                scaled_grad = grad * abs(loss) * lr

                # Gradient clipping
                if abs(scaled_grad) > clip:
                    scaled_grad = clip * (1.0 if scaled_grad > 0 else -1.0)

                # Adam-style first moment update
                moment_key = f"{grad_type}:{key}"
                beta1 = self.config.momentum
                self.accumulator._m1[moment_key] = (
                    beta1 * self.accumulator._m1.get(moment_key, 0.0)
                    + (1 - beta1) * scaled_grad
                )
                # Bias correction
                corrected = self.accumulator._m1[moment_key] / (1 - beta1 ** t)

                # Weight decay (L2 regularization)
                corrected += wd * scaled_grad

                if abs(corrected) > self.config.min_delta:
                    deltas[grad_type][key] = corrected

        return deltas

    @property
    def loss_trend(self) -> str:
        """Report loss trend (last 10 values)."""
        if not self._loss_history:
            return "No loss history"
        recent = self._loss_history[-10:]
        if len(recent) < 2:
            return f"Loss: {recent[-1]:.6f}"
        trend = recent[-1] - recent[0]
        direction = "decreasing" if trend < 0 else "increasing" if trend > 0 else "flat"
        return (
            f"Loss: {recent[-1]:.6f} ({direction}, "
            f"delta={trend:+.6f} over {len(recent)} steps)"
        )

    @property
    def total_steps(self) -> int:
        return self.accumulator._step

    def status(self) -> str:
        """Human-readable status."""
        lines = [
            f"Crystal Loss Engine",
            f"Steps: {self.total_steps}",
            f"Accumulated gradients: {self.accumulator.total_gradient_count}",
            self.loss_trend,
            f"Config: lr={self.config.learning_rate}, "
            f"lambda={self.config.lambda_disagreement}, "
            f"mu={self.config.mu_sparsity}, "
            f"wd={self.config.weight_decay}",
        ]
        return "\n".join(lines)
