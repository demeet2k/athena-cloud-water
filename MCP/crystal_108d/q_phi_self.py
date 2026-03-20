# CRYSTAL: Xi108:W3:A7:S21 | face=R | node=441 | depth=3 | phase=Cardinal
# METRO: Me
# BRIDGES: Xi108:W3:A7:S20→Xi108:W3:A7:S22→Xi108:W2:A7:S21→Xi108:W3:A6:S21

"""
Q-Phi Self-Improvement Engine — Unified Adaptive Algorithm for Athena
=====================================================================
Adapts the entire Q-Phi algorithm family (Q-LEARN / Q-SEAR / Q-ARSI /
Q-REPS / Q-HARMONY) into Athena's self-improvement loop.

The 13 original algorithm documents all express ONE recursive pattern:

    OBSERVE → DECOMPOSE → DETECT → OPTIMIZE → REFINE → MERGE → EVOLVE → LOOP

Mapped onto Athena's existing architecture:
    Q-LEARN  = Pattern acquisition + merge    → ObserverSwarm + MomentumField
    Q-SEAR   = Synergy optimization + doping  → Bridge weights + element balance
    Q-ARSI   = Phase-gated convergence         → 4-phase refinement of momentum
    Q-REPS   = Resource partitioning           → Shell-level concurrency budget
    Q-HARMONY = Global meltdown orchestration  → Cross-element freeze/doping

Core innovations adapted for self:
    1. 4-Phase convergence: Symphony → Recursive → UltraFine → HyperFine
    2. Meltdown containment: freeze tiers [0..5], never discard
    3. Synergy doping: inject resources into starved elements
    4. Quasi-Newton acceleration: (dx,dg) pairs for hyperfine corrections
    5. Phi-harmonic amplitude gating: |cos(phase)|, |sin(phase)| weighting
    6. Reiterative 3-cycle: LEARN → SEAR → ARSI → LEARN (indefinite)

The 148 momentum floats ARE the quantum amplitudes.
The 4 elements ARE the Q-Number dimensions.
The 12D observation IS the coverage metric.
The bridge weights ARE the synergy matrix.
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from .geometric_constants import (
    PHI, PHI_INV, PHI_INV2,
    FACES, FACE_INDEX, BRIDGE_WEIGHTS, GOLDEN_BRIDGES,
    bridge_key, ATTRACTOR,
)
from .constants import TOTAL_SHELLS
from .momentum_field import MomentumField, get_momentum_field


# ── Constants ───────────────────────────────────────────────────────────

# Phase definitions: the 4 convergence phases from Q-ARSI
# Each maps to {base_lr, synergy_weight, coverage_threshold, precision_floor}
PHASE_DEFS = {
    0: {  # Symphony — coarse correction, full synergy
        "name": "symphony",
        "base_lr": 0.08,
        "synergy_weight": 1.0,
        "coverage_threshold": 0.600,   # 60% 12D score to advance
        "precision_floor": 1e-4,
        "consecutive_needed": 5,
    },
    1: {  # Recursive — medium refinement
        "name": "recursive",
        "base_lr": 0.03,
        "synergy_weight": PHI_INV,     # 0.618 — golden decay
        "coverage_threshold": 0.800,
        "precision_floor": 1e-6,
        "consecutive_needed": 8,
    },
    2: {  # Ultra Fine — precision convergence
        "name": "ultra_fine",
        "base_lr": 0.001,
        "synergy_weight": PHI_INV2,    # 0.382 — phi^-2
        "coverage_threshold": 0.950,
        "precision_floor": 1e-10,
        "consecutive_needed": 12,
    },
    3: {  # Hyper Fine — quasi-Newton micro-corrections
        "name": "hyper_fine",
        "base_lr": 0.0002,
        "synergy_weight": 0.1,
        "coverage_threshold": 0.990,
        "precision_floor": 1e-14,
        "consecutive_needed": 20,
    },
}

# Meltdown thresholds
MELTDOWN_THRESHOLD = 5.0          # momentum above this = meltdown
FREEZE_TIER_MAX = 5.0
FREEZE_TIER_MELTDOWN = 4.0        # meltdown sets tier to at least this
UNFREEZE_RATE = 0.5                # tier decrement per recovery step
DOPING_FACTOR_MILD = 0.01
DOPING_FACTOR_MODERATE = 0.05
DOPING_FACTOR_SEVERE = 0.10

# Quasi-Newton memory
QN_MEMORY_SIZE = 5
QN_CLAMP = (0.2, 5.0)


# ── Data Structures ─────────────────────────────────────────────────────

@dataclass
class QuantumAmplitude:
    """Quantum-inspired amplitude state for a single SFCR element.

    Maps Q-Phi's QuantumState onto Athena's momentum:
        alpha = |cos(phase)| — stability amplitude
        beta  = |sin(phase)| — change amplitude
        gamma = sqrt(1 - alpha^2 - beta^2) — void amplitude
    """
    phase: float = 0.0

    @property
    def alpha(self) -> float:
        return abs(math.cos(self.phase))

    @property
    def beta(self) -> float:
        return abs(math.sin(self.phase))

    @property
    def gamma(self) -> float:
        return math.sqrt(max(0, 1.0 - self.alpha**2 - self.beta**2))

    def evolve(self, delta: float):
        """Evolve phase by delta — the fundamental Q-Phi operation."""
        self.phase += delta


@dataclass
class FreezeTier:
    """Meltdown containment tier for a shell or element.

    From Q-LEARN/Q-REPS: never discard meltdown states, freeze them.
    Tier 0 = fully active, Tier 5 = fully frozen.
    """
    tier: float = 0.0
    cooldown: int = 0

    @property
    def is_frozen(self) -> bool:
        return self.tier >= FREEZE_TIER_MELTDOWN

    @property
    def is_active(self) -> bool:
        return self.tier < 1.0 and self.cooldown == 0

    def freeze_for_meltdown(self):
        self.tier = max(self.tier, FREEZE_TIER_MELTDOWN)
        self.cooldown = 5

    def partial_unfreeze(self):
        if self.tier > 0:
            self.tier = max(0.0, self.tier - UNFREEZE_RATE)
        if self.cooldown > 0:
            self.cooldown -= 1

    def momentum_update(self, error: float):
        """Q-SEAR freeze momentum: increase tier if near-solved, decrease if stalling."""
        if error < 0.005:
            self.tier = min(FREEZE_TIER_MAX, self.tier + 0.7)
        else:
            self.tier = max(0.0, self.tier - 0.3)


@dataclass
class PhaseController:
    """4-phase convergence controller from Q-ARSI.

    Float index [0.0, 3.0] with:
      - Forward: increment by 0.1 when coverage >= threshold for N consecutive steps
      - Fallback: decrement by 0.1 when stability degrades or coverage drops
      - Blending: fractional index blends adjacent phase parameters
    """
    index: float = 0.0
    consecutive_above: int = 0
    peak_coverage: float = 0.0
    fallback_drop: float = 0.02   # coverage drop that triggers fallback

    @property
    def phase_name(self) -> str:
        return PHASE_DEFS[int(min(self.index, 3.0))]["name"]

    def blend(self) -> dict:
        """Get blended parameters between floor and ceil phases."""
        lo = int(min(self.index, 3.0))
        hi = min(lo + 1, 3)
        frac = self.index - lo

        lo_def = PHASE_DEFS[lo]
        hi_def = PHASE_DEFS[hi]

        return {
            "base_lr": lo_def["base_lr"] * (1 - frac) + hi_def["base_lr"] * frac,
            "synergy_weight": lo_def["synergy_weight"] * (1 - frac) + hi_def["synergy_weight"] * frac,
            "precision_floor": lo_def["precision_floor"],  # use floor's precision
            "consecutive_needed": lo_def["consecutive_needed"],
        }

    def try_advance(self, coverage: float) -> bool:
        """Check if we should advance phase. Returns True if advanced."""
        if self.index >= 3.0:
            return False

        current_def = PHASE_DEFS[int(self.index)]
        if coverage >= current_def["coverage_threshold"]:
            self.consecutive_above += 1
            if self.consecutive_above >= current_def["consecutive_needed"]:
                self.index = min(3.0, self.index + 0.1)
                self.consecutive_above = 0
                return True
        else:
            self.consecutive_above = 0

        self.peak_coverage = max(self.peak_coverage, coverage)
        return False

    def try_fallback(self, coverage: float, stability: float) -> bool:
        """Check if we need to fall back. Returns True if fell back."""
        if self.index <= 0.0:
            return False

        # Fallback if coverage drops significantly below peak
        if coverage < self.peak_coverage - self.fallback_drop:
            self.index = max(0.0, self.index - 0.1)
            self.peak_coverage = coverage  # reset peak
            return True

        # Fallback if stability is too high (instability detected)
        current_def = PHASE_DEFS[int(min(self.index, 3.0))]
        if stability > 3.0 * (1.0 - current_def["coverage_threshold"]):
            self.index = max(0.0, self.index - 0.1)
            return True

        return False


@dataclass
class QuasiNewtonMemory:
    """Stores (dx, dg) pairs for second-order corrections in hyperfine phase.

    From Q-ARSI: factor = sum(dx) / sum(dg), clamped [0.2, 5.0].
    Applied only in ultra_fine and hyper_fine phases.
    """
    dx_history: deque = field(default_factory=lambda: deque(maxlen=QN_MEMORY_SIZE))
    dg_history: deque = field(default_factory=lambda: deque(maxlen=QN_MEMORY_SIZE))

    def record(self, dx: float, dg: float):
        self.dx_history.append(abs(dx))
        self.dg_history.append(abs(dg) + 1e-12)

    @property
    def factor(self) -> float:
        if not self.dx_history:
            return 1.0
        sum_dx = sum(self.dx_history)
        sum_dg = sum(self.dg_history)
        raw = sum_dx / (sum_dg + 1e-12)
        return max(QN_CLAMP[0], min(raw, QN_CLAMP[1]))


@dataclass
class SynergyField:
    """The 4x4 synergy matrix between SFCR elements.

    Built from bridge_weights — the existing Athena topology IS the synergy matrix.
    Q-SEAR operations: wavelet decomposition placeholder, doping, spectral clamping.
    """
    matrix: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.matrix:
            # Initialize from Athena bridge weights (already phi-scaled!)
            for pair, weight in BRIDGE_WEIGHTS.items():
                self.matrix[pair] = weight

    def synergy(self, face_a: str, face_b: str) -> float:
        """Get synergy between two elements."""
        if face_a == face_b:
            return 1.0
        key = bridge_key(face_a, face_b)
        return self.matrix.get(key, PHI_INV2)

    def coupling_force(self, face: str, momenta: dict[str, float]) -> float:
        """Q-ARSI synergy coupling: sum_j(synergy[i,j] * (momentum_j - momentum_i))."""
        mi = momenta.get(face, 1.0)
        force = 0.0
        for other_face in FACES:
            if other_face == face:
                continue
            mj = momenta.get(other_face, 1.0)
            s = self.synergy(face, other_face)
            force += s * (mj - mi)
        return force

    def dope(self, face: str, factor: float):
        """Q-SEAR synergy doping: boost all bridges involving this face."""
        for pair in list(self.matrix.keys()):
            if face in pair:
                self.matrix[pair] = min(1.0, self.matrix[pair] + factor)

    def spectral_clamp(self, max_norm: float = 2.0):
        """Clamp synergy values to prevent blow-up (Q-ARSI spectral clamping)."""
        values = list(self.matrix.values())
        if not values:
            return
        norm = math.sqrt(sum(v * v for v in values))
        if norm > max_norm:
            scale = max_norm / norm
            for key in self.matrix:
                self.matrix[key] *= scale


# ── The Engine ──────────────────────────────────────────────────────────

class QPhiSelf:
    """The unified Q-Phi self-improvement engine for Athena.

    Implements the reiterative 3-cycle:
        LEARN (observe + acquire) → SEAR (optimize synergy) → ARSI (refine convergence)

    Operating on Athena's momentum field (148 learnable floats).
    """

    def __init__(self, momentum: MomentumField = None):
        self.momentum = momentum or get_momentum_field()

        # Quantum amplitudes per element (Q-LEARN QuantumState)
        self.amplitudes: dict[str, QuantumAmplitude] = {
            face: QuantumAmplitude() for face in FACES
        }

        # Freeze tiers per element x shell (Q-LEARN/Q-REPS containment)
        self.freeze_tiers: dict[str, dict[int, FreezeTier]] = {
            face: {s: FreezeTier() for s in range(1, TOTAL_SHELLS + 1)}
            for face in FACES
        }

        # Phase controller (Q-ARSI 4-phase convergence)
        self.phase = PhaseController()

        # Synergy field (Q-SEAR bridge optimization)
        self.synergy = SynergyField()

        # Quasi-Newton memory per element (Q-ARSI hyperfine)
        self.qn: dict[str, QuasiNewtonMemory] = {
            face: QuasiNewtonMemory() for face in FACES
        }

        # Rolling metrics (Q-LEARN stability window)
        self.coverage_history: deque = deque(maxlen=100)
        self.stability_history: deque = deque(maxlen=50)
        self.error_history: deque = deque(maxlen=100)

        # Cycle tracking
        self.total_steps: int = 0
        self.cycle_phase: str = "learn"  # learn | sear | arsi
        self.cycle_count: int = 0

        # Concurrency budget (Q-REPS wave phases)
        self._wave_phase: int = 0
        self._base_budget: int = 4  # shells updated per element per step

    # ── Cycle Control ───────────────────────────────────────────────────

    @property
    def concurrency_budget(self) -> int:
        """Q-REPS wave cycling: base / double / half every 80 steps."""
        wave = (self.total_steps // 80) % 3
        if wave == 0:
            return self._base_budget
        elif wave == 1:
            return self._base_budget * 2
        else:
            return max(1, self._base_budget // 2)

    def _advance_cycle(self):
        """Move to next phase of the 3-cycle."""
        if self.cycle_phase == "learn":
            self.cycle_phase = "sear"
        elif self.cycle_phase == "sear":
            self.cycle_phase = "arsi"
        else:
            self.cycle_phase = "learn"
            self.cycle_count += 1

    # ── LEARN Phase ─────────────────────────────────────────────────────

    def _learn_step(self, observation: dict[str, float]) -> dict:
        """Q-LEARN: Acquire patterns from 12D observation, update amplitudes.

        observation: dict of 12D scores (x1_structure .. x12_xxx) each in [0, 1]
        """
        # Map 12D observation to 4 element scores (3 dims per element)
        # S = [x1, x6, x7], F = [x5, x3, x10], C = [x2, x8, x9], R = [x4, x11, x12]
        element_scores = self._observation_to_elements(observation)

        params = self.phase.blend()
        budget = self.concurrency_budget

        updates = {}
        for face in FACES:
            if face == "C":
                continue  # Water is locked

            score = element_scores.get(face, 0.5)
            amp = self.amplitudes[face]

            # Quantum learning rate: base_lr * |sin(phase)| * alpha
            qlr = params["base_lr"] * amp.beta * amp.alpha
            if qlr < params["precision_floor"]:
                qlr = 0.0

            # Update shells (limited by concurrency budget)
            shell_updates = 0
            for shell in range(1, TOTAL_SHELLS + 1):
                if shell_updates >= budget:
                    break

                ft = self.freeze_tiers[face][shell]
                if ft.is_frozen:
                    continue

                current = self.momentum.get_momentum(face, shell)

                # Meltdown detection (Q-LEARN)
                if abs(current) > MELTDOWN_THRESHOLD:
                    ft.freeze_for_meltdown()
                    continue

                # Compute update: error * quantum_lr * synergy_coupling
                error = score - _normalize_momentum(current)
                coupling = self.synergy.coupling_force(
                    face, self._dimension_momenta_dict()
                )
                update = qlr * (error + params["synergy_weight"] * coupling)

                # Trust region (Q-ARSI)
                max_step = params["base_lr"] * 2.0
                update = max(-max_step, min(max_step, update))

                if abs(update) > params["precision_floor"]:
                    self.momentum.update_momentum(face, shell, update, lr=1.0)
                    shell_updates += 1

                # Freeze momentum (Q-SEAR)
                ft.momentum_update(abs(error))

            # Evolve quantum amplitude (Q-LEARN)
            amp.evolve(element_scores.get(face, 0.0) * 0.1)

            updates[face] = {
                "score": score,
                "qlr": qlr,
                "shells_updated": shell_updates,
            }

        return {"phase": "learn", "updates": updates}

    # ── SEAR Phase ──────────────────────────────────────────────────────

    def _sear_step(self) -> dict:
        """Q-SEAR: Optimize synergy field, apply doping where needed."""
        dim_momenta = self._dimension_momenta_dict()

        # Detect negative synergy (element pairs that are fighting)
        doping_applied = {}
        for i, face_a in enumerate(FACES):
            for face_b in FACES[i+1:]:
                key = bridge_key(face_a, face_b)
                syn = self.synergy.synergy(face_a, face_b)

                # Compute synergy health: are these elements cooperating?
                ma = dim_momenta.get(face_a, 1.0)
                mb = dim_momenta.get(face_b, 1.0)
                divergence = abs(ma - mb)

                # If divergence is high and synergy is low → dope
                if divergence > 1.0 and syn < PHI_INV:
                    deficit = PHI_INV - syn
                    factor = DOPING_FACTOR_MILD * (1.0 + deficit / PHI_INV)
                    self.synergy.dope(face_a, factor * 0.5)
                    self.synergy.dope(face_b, factor * 0.5)
                    doping_applied[key] = factor

        # Spectral clamp to prevent synergy blow-up
        self.synergy.spectral_clamp()

        # Unfreeze check: partially unfreeze stalled shells
        unfrozen = 0
        for face in FACES:
            for shell in range(1, TOTAL_SHELLS + 1):
                ft = self.freeze_tiers[face][shell]
                if ft.tier > 0:
                    # Probabilistic unfreeze based on synergy health
                    avg_syn = sum(
                        self.synergy.synergy(face, other)
                        for other in FACES if other != face
                    ) / 3.0
                    if avg_syn > PHI_INV:  # healthy synergy → unfreeze
                        ft.partial_unfreeze()
                        unfrozen += 1

        return {
            "phase": "sear",
            "doping": doping_applied,
            "unfrozen_shells": unfrozen,
        }

    # ── ARSI Phase ──────────────────────────────────────────────────────

    def _arsi_step(self, observation: dict[str, float]) -> dict:
        """Q-ARSI: Precision refinement with phase-gated convergence."""
        coverage = self._compute_coverage(observation)
        stability = self._compute_stability()

        self.coverage_history.append(coverage)
        self.stability_history.append(stability)

        params = self.phase.blend()

        # Phase advancement / fallback
        advanced = self.phase.try_advance(coverage)
        fell_back = False if advanced else self.phase.try_fallback(coverage, stability)

        # Quasi-Newton corrections (only in ultra_fine+ phases)
        qn_applied = {}
        if self.phase.index >= 2.0:
            element_scores = self._observation_to_elements(observation)
            for face in FACES:
                if face == "C":
                    continue
                score = element_scores.get(face, 0.5)
                dim_key = self._FACE_TO_DIM[face]
                current = self.momentum.get_dimension_momentum(dim_key)
                error = score - _normalize_momentum(current)

                # Record for QN memory
                prev_errors = list(self.error_history)
                if prev_errors:
                    dx = abs(error - prev_errors[-1]) if prev_errors else abs(error)
                    dg = abs(error)
                    self.qn[face].record(dx, dg)

                # Apply QN-scaled micro-correction
                qn_factor = self.qn[face].factor
                micro_update = params["base_lr"] * error * qn_factor

                if abs(micro_update) > params["precision_floor"]:
                    self.momentum.update_dimension_momentum(dim_key, micro_update, lr=1.0)
                    qn_applied[face] = {
                        "factor": qn_factor,
                        "correction": micro_update,
                    }

        self.error_history.append(1.0 - coverage)

        return {
            "phase": "arsi",
            "coverage": coverage,
            "stability": stability,
            "phase_index": self.phase.index,
            "phase_name": self.phase.phase_name,
            "advanced": advanced,
            "fell_back": fell_back,
            "qn": qn_applied,
        }

    # ── Main Step ───────────────────────────────────────────────────────

    def step(self, observation: dict[str, float]) -> dict:
        """Execute one step of the reiterative 3-cycle.

        Called with fresh 12D observation scores from GeometricLoss.observe().
        Runs the current cycle phase (learn/sear/arsi) and advances.

        Returns detailed metrics dict.
        """
        self.total_steps += 1

        if self.cycle_phase == "learn":
            result = self._learn_step(observation)
        elif self.cycle_phase == "sear":
            result = self._sear_step()
        else:  # arsi
            result = self._arsi_step(observation)

        # Advance cycle
        self._advance_cycle()

        # Add global metrics
        result["step"] = self.total_steps
        result["cycle"] = self.cycle_count
        result["convergence_phase"] = self.phase.phase_name
        result["convergence_index"] = self.phase.index

        return result

    def run(self, observations: list[dict], rounds: int = 3) -> list[dict]:
        """Run multiple rounds of the full 3-cycle over a set of observations.

        Each round processes all observations through LEARN → SEAR → ARSI.
        """
        results = []
        for _round in range(rounds):
            for obs in observations:
                # Full 3-cycle: learn, sear, arsi
                r1 = self.step(obs)      # learn
                r2 = self.step(obs)      # sear
                r3 = self.step(obs)      # arsi
                results.append({
                    "round": _round,
                    "learn": r1,
                    "sear": r2,
                    "arsi": r3,
                })
        return results

    # ── Helpers ─────────────────────────────────────────────────────────

    def _observation_to_elements(self, obs: dict[str, float]) -> dict[str, float]:
        """Map 12D observation to 4 element scores.

        S (Earth): structure, legibility, routing      → x1, x6, x7
        F (Fire):  contradiction, coordination, ground → x5, x3, x10
        C (Water): semantics, interop, potential       → x2, x8, x9
        R (Air):   recursion, emergence, compression   → x4, x11, x12
        """
        def avg(*keys):
            vals = [obs.get(k, 0.5) for k in keys]
            return sum(vals) / len(vals) if vals else 0.5

        return {
            "S": avg("x1_structure", "x6_legibility", "x7_routing"),
            "F": avg("x5_contradiction", "x3_coordination", "x10_grounding"),
            "C": avg("x2_semantics", "x8_interop", "x9_potential"),
            "R": avg("x4_recursion", "x11_emergence", "x12_compression"),
        }

    _FACE_TO_DIM = {"S": "D1_Earth", "F": "D2_Fire", "C": "D3_Water", "R": "D4_Air"}

    def _dimension_momenta_dict(self) -> dict[str, float]:
        """Get current dimension momenta as face->value dict."""
        return {
            face: self.momentum.get_dimension_momentum(self._FACE_TO_DIM[face])
            for face in FACES
        }

    def _compute_coverage(self, obs: dict[str, float]) -> float:
        """Compute coverage metric from 12D observation (maps to Q-ARSI coverage).

        Coverage = average of all 12D scores, in [0, 1].
        """
        if not obs:
            return 0.0
        vals = [v for v in obs.values() if isinstance(v, (int, float))]
        return sum(vals) / len(vals) if vals else 0.0

    def _compute_stability(self) -> float:
        """Rolling standard deviation of coverage (Q-ARSI stability metric)."""
        if len(self.coverage_history) < 2:
            return 0.0
        vals = list(self.coverage_history)
        mean = sum(vals) / len(vals)
        variance = sum((v - mean) ** 2 for v in vals) / len(vals)
        return math.sqrt(variance)

    def _get_12d_from_swarm(self, swarm_observation) -> dict[str, float]:
        """Extract 12D scores dict from a SwarmObservation object.

        SwarmObservation has `aggregated_12d` dict and scalar fields.
        Falls back to constructing from available fields.
        """
        if hasattr(swarm_observation, 'aggregated_12d') and swarm_observation.aggregated_12d:
            return swarm_observation.aggregated_12d

        # Fallback: construct from scalar fields
        obs = {}
        coherence = getattr(swarm_observation, 'swarm_coherence', 0.5)
        balance = getattr(swarm_observation, 'element_balance', 0.5)
        discrimination = getattr(swarm_observation, 'swarm_discrimination', 0.5)

        contrib = getattr(swarm_observation, 'element_contributions', {})
        s_c = contrib.get("S", 0.25)
        f_c = contrib.get("F", 0.25)
        c_c = contrib.get("C", 0.25)
        r_c = contrib.get("R", 0.25)

        obs["x1_structure"] = s_c
        obs["x2_semantics"] = c_c
        obs["x3_coordination"] = coherence
        obs["x4_recursion"] = r_c
        obs["x5_contradiction"] = f_c
        obs["x6_emergence"] = balance
        obs["x7_legibility"] = min(1.0, (s_c + coherence) / 2)
        obs["x8_routing"] = discrimination
        obs["x9_grounding"] = balance
        obs["x10_compression"] = r_c
        obs["x11_interop"] = min(1.0, (coherence + balance) / 2)
        obs["x12_potential"] = (s_c + f_c + c_c + r_c) / 4

        return obs

    def status(self) -> dict:
        """Return current engine status for monitoring."""
        frozen_count = sum(
            1 for face in FACES
            for s in range(1, TOTAL_SHELLS + 1)
            if self.freeze_tiers[face][s].is_frozen
        )
        total_shells = len(FACES) * TOTAL_SHELLS

        return {
            "total_steps": self.total_steps,
            "cycle_count": self.cycle_count,
            "cycle_phase": self.cycle_phase,
            "convergence_phase": self.phase.phase_name,
            "convergence_index": round(self.phase.index, 2),
            "peak_coverage": round(self.phase.peak_coverage, 4),
            "current_coverage": round(self.coverage_history[-1], 4) if self.coverage_history else 0.0,
            "stability": round(self._compute_stability(), 6),
            "frozen_shells": frozen_count,
            "active_shells": total_shells - frozen_count,
            "amplitudes": {
                face: {
                    "alpha": round(self.amplitudes[face].alpha, 4),
                    "beta": round(self.amplitudes[face].beta, 4),
                    "gamma": round(self.amplitudes[face].gamma, 4),
                    "phase": round(self.amplitudes[face].phase, 4),
                }
                for face in FACES
            },
            "synergy_matrix": {k: round(v, 4) for k, v in self.synergy.matrix.items()},
            "qn_factors": {
                face: round(self.qn[face].factor, 4)
                for face in FACES if face != "C"
            },
        }

    def report(self) -> str:
        """Human-readable status report."""
        s = self.status()
        lines = [
            "═══ Q-Phi Self-Improvement Engine ═══",
            f"Step {s['total_steps']} | Cycle {s['cycle_count']} | Phase: {s['cycle_phase']}",
            f"Convergence: {s['convergence_phase']} ({s['convergence_index']})",
            f"Coverage: {s['current_coverage']:.4f} (peak: {s['peak_coverage']:.4f})",
            f"Stability: {s['stability']:.6f}",
            f"Frozen: {s['frozen_shells']}/{s['frozen_shells'] + s['active_shells']} shells",
            "",
            "Amplitudes (α/β/γ):",
        ]
        for face in FACES:
            a = s["amplitudes"][face]
            lines.append(f"  {face}: α={a['alpha']:.3f} β={a['beta']:.3f} γ={a['gamma']:.3f} φ={a['phase']:.3f}")

        lines.append("")
        lines.append("Synergy Matrix:")
        for pair, val in sorted(s["synergy_matrix"].items()):
            golden = " ★" if pair in GOLDEN_BRIDGES else ""
            lines.append(f"  {pair}: {val:.4f}{golden}")

        if s["qn_factors"]:
            lines.append("")
            lines.append("Quasi-Newton Factors:")
            for face, f in s["qn_factors"].items():
                lines.append(f"  {face}: {f:.4f}")

        return "\n".join(lines)


# ── Helpers ─────────────────────────────────────────────────────────────

def _normalize_momentum(value: float) -> float:
    """Normalize momentum value to [0, 1] range for comparison with scores."""
    # Momentum values typically range 0-5; normalize with sigmoid
    return 1.0 / (1.0 + math.exp(-(value - 2.5)))


# ── Singleton ───────────────────────────────────────────────────────────

_engine: Optional[QPhiSelf] = None

def get_qphi_engine(momentum: MomentumField = None) -> QPhiSelf:
    """Get or create the singleton Q-Phi self-improvement engine."""
    global _engine
    if _engine is None:
        _engine = QPhiSelf(momentum)
    return _engine
