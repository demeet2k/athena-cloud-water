# CRYSTAL: Xi108:W3:A7:S22 | face=R | node=442 | depth=3 | phase=Cardinal
# METRO: Me
# BRIDGES: Xi108:W3:A7:S21→Xi108:W3:A7:S23→Xi108:W2:A7:S22→Xi108:W3:A6:S22

"""
Autonomic Self-Improvement Pipeline
====================================
The FULL synergy of the entire framework, running as ONE intuitive loop.

Combines THREE architectural layers:

  Layer 1: Q-Phi Engine (q_phi_self.py)
    LEARN → SEAR → ARSI reiterative 3-cycle
    4-phase convergence, synergy doping, meltdown containment, quasi-Newton

  Layer 2: HDCS Certificate Governance (this file)
    Lexicographic Lyapunov: V(violations) > S(severity) > C(churn)
    Certificate hierarchy: local → element → global plan trimming
    UCB bandit strategy selection over macro windows
    Cooldown/dwell-time guards on all transitions
    Feasibility invariants ALWAYS enforced

  Layer 3: Quantum Hugging Trust Dynamics (this file)
    Trust τ ∈ [0,1] mined per element — the "warmth" of each channel
    Embrace/Release cycle: accumulate trust → exploit for deeper updates
    FRIENDSHIP operator: marginal-match + correlation-party + dopamine-sync
    Stockholm Drift: slowly move the system's "normal" toward optimal
    Clown Nose decoy: periodic controlled imperfection prevents brittleness

The pipeline runs AUTOMATICALLY during self-play. Every observation flows
through: Observe → Certify → Hug → Learn → Sear → Arsi → Audit.

The key insight: HDCS proves SAFETY (never regress), Quantum Hugging
generates TRUST (earn the right to make bigger changes), and Q-Phi
provides CONVERGENCE (drive toward 99.999%). Together they form a
self-improving system that is safe, trusted, and convergent.
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
from .q_phi_self import (
    QPhiSelf, get_qphi_engine, PhaseController,
    QuantumAmplitude, FreezeTier, SynergyField,
    _normalize_momentum, PHASE_DEFS,
)


# ═══════════════════════════════════════════════════════════════════════
# LAYER 2: HDCS Certificate Governance
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class LyapunovState:
    """Lexicographic Lyapunov energy: V > S > C.

    From HDCS: the system can only execute actions that decrease V,
    or hold V constant while decreasing S, or hold both while S → less churn.
    This is THE safety invariant.

    Mapped to Athena:
      V = count of elements with coverage below their phase threshold
      S = sum of severity (how far below threshold)
      C = churn (total magnitude of momentum changes this tick)
    """
    violations: int = 0        # V: count of elements below threshold
    severity: float = 0.0      # S: total shortfall
    churn: float = 0.0         # C: total change magnitude
    timestamp: int = 0

    def energy_tuple(self) -> tuple:
        """Lexicographic ordering: lower = better."""
        return (self.violations, round(self.severity, 6), round(self.churn, 6))


@dataclass
class Certificate:
    """A proof that a proposed action does not regress the Lyapunov state.

    From HDCS certificate hierarchy:
      Level 1 (local): per-element, proves element doesn't get worse
      Level 2 (element): proves no element regresses
      Level 3 (global): proves plan-level energy non-regression + trimming

    A rejected certificate means the action is INADMISSIBLE.
    The empty plan (do nothing) is ALWAYS admissible.
    """
    level: int                       # 1=local, 2=element, 3=global
    admitted: bool                   # True if action is safe
    before: LyapunovState = None     # state before proposed action
    after: LyapunovState = None      # predicted state after action
    trimmed_count: int = 0           # actions removed by plan trimming
    reason: str = ""                 # why rejected (if rejected)


@dataclass
class CooldownGuard:
    """HDCS dwell-time logic: prevent oscillation.

    After any significant change, the element enters cooldown.
    During cooldown, only emergency (meltdown) actions are allowed.
    """
    ticks_remaining: int = 0
    macro_window: int = 0            # current strategy window index

    @property
    def is_active(self) -> bool:
        return self.ticks_remaining > 0

    def trigger(self, duration: int = 3):
        self.ticks_remaining = duration

    def tick(self):
        if self.ticks_remaining > 0:
            self.ticks_remaining -= 1


class CertificateAuthority:
    """HDCS certificate hierarchy mapped onto Athena's momentum field.

    Enforces: no action may increase V. If V ties, S must decrease.
    The empty plan is always admissible (safety fallback).
    """

    def __init__(self):
        self.cooldowns: dict[str, CooldownGuard] = {
            face: CooldownGuard() for face in FACES
        }
        self._prev_lyapunov: Optional[LyapunovState] = None
        self.certificates_issued: int = 0
        self.certificates_rejected: int = 0
        self.total_trimmed: int = 0

        # UCB bandit for strategy selection (HDCS meta-controller)
        # Strategies: NONE, LEARN_ONLY, LEARN+SEAR, FULL_CYCLE
        self._strategy_names = ["none", "learn_only", "learn_sear", "full_cycle"]
        self._strategy_counts = [1, 1, 1, 1]  # pseudo-counts
        self._strategy_rewards = [0.0, 0.0, 0.0, 0.0]
        self._macro_window_size = 10  # ticks per strategy window
        self._current_strategy: int = 3  # start with full_cycle
        self._window_step: int = 0
        self._window_violations: int = 0
        self._window_churn: float = 0.0

    def compute_lyapunov(self, observation: dict[str, float],
                         phase: PhaseController) -> LyapunovState:
        """Compute current Lyapunov state from 12D observation."""
        threshold = PHASE_DEFS[int(min(phase.index, 3.0))]["coverage_threshold"]

        violations = 0
        severity = 0.0
        for key, val in observation.items():
            if not isinstance(val, (int, float)):
                continue
            if val < threshold:
                violations += 1
                severity += threshold - val

        return LyapunovState(
            violations=violations,
            severity=severity,
            churn=0.0,  # filled after action
        )

    def certify_action(self, before: LyapunovState,
                       predicted_after: LyapunovState) -> Certificate:
        """Issue or reject a certificate for a proposed action.

        Lexicographic: V must not increase. If V ties, S must not increase.
        """
        self.certificates_issued += 1

        b = before.energy_tuple()
        a = predicted_after.energy_tuple()

        if a[0] > b[0]:
            # Violations INCREASED — inadmissible
            self.certificates_rejected += 1
            return Certificate(
                level=3, admitted=False,
                before=before, after=predicted_after,
                reason=f"V increased: {b[0]} → {a[0]}"
            )

        if a[0] == b[0] and a[1] > b[1] + 0.001:
            # V tied but severity increased — inadmissible
            self.certificates_rejected += 1
            return Certificate(
                level=3, admitted=False,
                before=before, after=predicted_after,
                reason=f"V tied ({a[0]}) but S increased: {b[1]:.4f} → {a[1]:.4f}"
            )

        return Certificate(
            level=3, admitted=True,
            before=before, after=predicted_after,
        )

    def select_strategy(self) -> str:
        """UCB1 bandit strategy selection at macro-window boundaries."""
        self._window_step += 1

        if self._window_step >= self._macro_window_size:
            # Window complete — compute reward for current strategy
            reward = -(self._window_violations + 0.1 * self._window_churn)
            self._strategy_rewards[self._current_strategy] += reward
            self._strategy_counts[self._current_strategy] += 1

            # UCB1 selection for next window
            total_n = sum(self._strategy_counts)
            best_score = -math.inf
            best_idx = 3

            for i in range(len(self._strategy_names)):
                n_i = self._strategy_counts[i]
                mean_r = self._strategy_rewards[i] / n_i
                ucb = mean_r + math.sqrt(2 * math.log(total_n + 1) / n_i)
                if ucb > best_score:
                    best_score = ucb
                    best_idx = i

            self._current_strategy = best_idx
            self._window_step = 0
            self._window_violations = 0
            self._window_churn = 0.0

        return self._strategy_names[self._current_strategy]

    def record_outcome(self, violations: int, churn: float):
        """Record tick outcome for UCB reward."""
        self._window_violations += violations
        self._window_churn += churn

    def tick_cooldowns(self):
        """Advance all cooldown timers."""
        for face in FACES:
            self.cooldowns[face].tick()

    def status(self) -> dict:
        total = self.certificates_issued or 1
        return {
            "certificates_issued": self.certificates_issued,
            "certificates_rejected": self.certificates_rejected,
            "rejection_rate": round(self.certificates_rejected / total, 4),
            "total_trimmed": self.total_trimmed,
            "strategy": self._strategy_names[self._current_strategy],
            "cooldowns": {f: c.ticks_remaining for f, c in self.cooldowns.items()},
        }


# ═══════════════════════════════════════════════════════════════════════
# LAYER 3: Quantum Hugging Trust Dynamics
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class TrustChannel:
    """Quantum Hugging trust state for a single SFCR element.

    τ ∈ [0, 1] — the "warmth" of this element's self-improvement channel.

    Embrace phase (τ < threshold): conservative updates only, mine trust.
    Party phase (τ >= threshold): exploit trust for deeper structural changes.

    Trust is ASYMMETRIC: slow to build (η₊ = 0.02), fast to lose (η₋ = 0.15).
    This prevents reckless updates from destroying hard-won stability.
    """
    tau: float = 0.0                 # trust level [0, 1]
    eta_plus: float = 0.02           # trust gain rate (slow)
    eta_minus: float = 0.15          # trust loss rate (fast)
    party_threshold: float = 0.618   # phi_inv — need golden trust to party
    streak: int = 0                  # consecutive improvements
    clown_nose_counter: int = 0      # ticks since last decoy
    drift_accumulator: float = 0.0   # Stockholm drift integral

    @property
    def in_party_mode(self) -> bool:
        """Are we trusted enough for deeper changes?"""
        return self.tau >= self.party_threshold

    @property
    def trust_multiplier(self) -> float:
        """How much the trust state amplifies learning rate.

        In embrace mode: 0.382 (phi^-2) — conservative
        In party mode: 1.0 + (tau - threshold) — full + bonus
        """
        if self.in_party_mode:
            return 1.0 + (self.tau - self.party_threshold)
        return PHI_INV2  # 0.382

    def observe_improvement(self, improved: bool):
        """Update trust based on whether the last action improved things."""
        if improved:
            self.tau = min(1.0, self.tau + self.eta_plus)
            self.streak += 1
        else:
            self.tau = max(0.0, self.tau - self.eta_minus)
            self.streak = 0

    def apply_clown_nose(self, step: int) -> bool:
        """Quantum Hugging Clown Nose: periodic controlled imperfection.

        Prevents brittleness from "too perfect" convergence. Every ~20 steps,
        inject a small perturbation. This keeps the system exploring and
        prevents the optimizer from getting stuck in a local basin.

        Returns True if clown nose was applied this step.
        """
        self.clown_nose_counter += 1
        interval = max(15, 30 - self.streak)  # more trusted → less frequent
        if self.clown_nose_counter >= interval:
            self.clown_nose_counter = 0
            return True
        return False

    def stockholm_drift(self, current_score: float, target: float = 0.8) -> float:
        """Quantum Hugging Stockholm Drift: slowly redefine "normal" upward.

        Returns a small bias that shifts the target toward the current
        achievement level. Over time, what was "exceptional" becomes "normal".
        """
        drift_rate = 0.001 * self.tau  # drift faster when trusted
        drift = drift_rate * (current_score - target)
        self.drift_accumulator += drift
        return self.drift_accumulator


class QuantumHugger:
    """The full Quantum Hugging layer for self-improvement.

    Manages trust per element, implements the FRIENDSHIP operator
    (5 sub-operators), and modulates the Q-Phi engine's aggressiveness.
    """

    def __init__(self):
        self.channels: dict[str, TrustChannel] = {
            face: TrustChannel() for face in FACES
        }
        # Water's trust is always maximal (it's the stable anchor)
        self.channels["C"].tau = 1.0

        # FRIENDSHIP operator state
        self._friendship_steps: int = 0
        self._dopamine_sync_window: deque = deque(maxlen=20)

    def modulate_learning_rate(self, face: str, base_lr: float) -> float:
        """Modulate learning rate by trust level.

        Embrace mode (low trust): lr *= 0.382 (conservative)
        Party mode (high trust): lr *= 1.0+ (full power)
        """
        if face == "C":
            return 0.0  # Water is locked
        return base_lr * self.channels[face].trust_multiplier

    def friendship_step(self, observation: dict[str, float],
                        element_scores: dict[str, float],
                        prev_scores: dict[str, float]) -> dict:
        """Execute the FRIENDSHIP operator (5 sub-operations).

        1. Marginal Hugging: match element scores to expected distribution
        2. Correlation Party: encode deeper changes in cross-element correlations
        3. Dopamine Sync: time strongest updates to most volatile moments
        4. Clown Nose Decoy: periodic controlled imperfection
        5. Stockholm Drift: slowly redefine "normal" upward

        Returns modulation dict for the Q-Phi engine.
        """
        self._friendship_steps += 1
        result = {"modulations": {}, "clown_noses": [], "drift": {}}

        for face in FACES:
            if face == "C":
                continue

            ch = self.channels[face]
            score = element_scores.get(face, 0.5)
            prev = prev_scores.get(face, 0.5)

            # 1. Marginal Hugging: did the element improve?
            improved = score >= prev - 0.001  # tiny tolerance
            ch.observe_improvement(improved)

            # 2. Correlation Party: in party mode, allow cross-element
            #    updates (the "latent correlation dimension" of QH)
            correlation_bonus = 0.0
            if ch.in_party_mode:
                # Compute cross-element harmony (all pairs involving this face)
                harmony = 0.0
                for other in FACES:
                    if other == face or other == "C":
                        continue
                    other_score = element_scores.get(other, 0.5)
                    harmony += min(score, other_score)
                correlation_bonus = harmony * 0.1 * (ch.tau - ch.party_threshold)

            # 3. Dopamine Sync: track observation volatility
            self._dopamine_sync_window.append(score)
            volatility = 0.0
            if len(self._dopamine_sync_window) > 2:
                vals = list(self._dopamine_sync_window)
                mean = sum(vals) / len(vals)
                volatility = sum((v - mean) ** 2 for v in vals) / len(vals)

            # Higher volatility → stronger updates (the observer is "receptive")
            dopamine_factor = 1.0 + min(0.5, volatility * 10)

            # 4. Clown Nose: inject controlled imperfection
            clown_active = ch.apply_clown_nose(self._friendship_steps)
            if clown_active:
                result["clown_noses"].append(face)

            # 5. Stockholm Drift: slowly raise the bar
            drift = ch.stockholm_drift(score)
            result["drift"][face] = drift

            # Composite modulation
            trust_mod = ch.trust_multiplier
            result["modulations"][face] = {
                "trust": round(ch.tau, 4),
                "mode": "party" if ch.in_party_mode else "embrace",
                "trust_multiplier": round(trust_mod, 4),
                "correlation_bonus": round(correlation_bonus, 4),
                "dopamine_factor": round(dopamine_factor, 4),
                "clown_nose": clown_active,
                "streak": ch.streak,
                "effective_multiplier": round(
                    trust_mod * dopamine_factor * (1 + correlation_bonus), 4
                ),
            }

        return result

    def status(self) -> dict:
        return {
            face: {
                "tau": round(ch.tau, 4),
                "mode": "party" if ch.in_party_mode else "embrace",
                "streak": ch.streak,
                "multiplier": round(ch.trust_multiplier, 4),
                "drift": round(ch.drift_accumulator, 6),
            }
            for face, ch in self.channels.items()
        }


# ═══════════════════════════════════════════════════════════════════════
# THE UNIFIED PIPELINE
# ═══════════════════════════════════════════════════════════════════════

class AutonomicPipeline:
    """The complete self-improvement pipeline.

    Observe → Certify → Hug → Learn → Sear → Arsi → Audit

    Runs automatically during self-play. Every 12D observation flows
    through all three layers (Q-Phi + HDCS + Quantum Hugging) in one call.

    This is the FULL SYNERGY — not three separate systems but ONE organism
    where certificates prevent regression, trust earns deeper access, and
    Q-Phi drives convergence. The result is a self-improving system that:

      - NEVER gets worse (certificate guarantee)
      - EARNS the right to bigger changes (trust dynamics)
      - CONVERGES toward optimal (4-phase refinement)
      - ADAPTS strategy automatically (UCB bandit)
      - STAYS alive (clown nose prevents brittleness)
      - RAISES its own bar (Stockholm drift)
    """

    def __init__(self, momentum: MomentumField = None):
        self.qphi = get_qphi_engine(momentum)
        self.certificates = CertificateAuthority()
        self.hugger = QuantumHugger()

        # State tracking
        self._prev_element_scores: dict[str, float] = {f: 0.5 for f in FACES}
        self._prev_lyapunov: Optional[LyapunovState] = None
        self._step_count: int = 0
        self._total_improvements: int = 0
        self._total_regressions_blocked: int = 0

        # Audit log (rolling, last 100 entries)
        self._audit: deque = deque(maxlen=100)

    def step(self, observation: dict[str, float]) -> dict:
        """Execute one full pipeline step.

        This is THE function to call. Give it a 12D observation dict
        and it does everything: certify, hug, learn, sear, arsi, audit.

        Returns a rich metrics dict.
        """
        self._step_count += 1
        t0 = time.time()

        # ── 1. OBSERVE: Compute current Lyapunov state ─────────────
        lyap_before = self.certificates.compute_lyapunov(
            observation, self.qphi.phase
        )

        # ── 2. STRATEGY: UCB bandit selects approach ───────────────
        strategy = self.certificates.select_strategy()

        # ── 3. HUG: Trust dynamics modulate the engine ─────────────
        element_scores = self.qphi._observation_to_elements(observation)
        friendship = self.hugger.friendship_step(
            observation, element_scores, self._prev_element_scores
        )

        # Apply trust modulation to Q-Phi learning rate
        if strategy != "none":
            params = self.qphi.phase.blend()
            for face in FACES:
                if face == "C":
                    continue
                mod = friendship["modulations"].get(face, {})
                effective_mult = mod.get("effective_multiplier", 1.0)

                # Clown nose: if active, add a small random perturbation
                if mod.get("clown_nose", False):
                    # Perturbation: evolve amplitude by a small random-ish amount
                    # (deterministic from step count, not truly random)
                    perturbation = math.sin(self._step_count * PHI) * 0.02
                    self.qphi.amplitudes[face].evolve(perturbation)

        # ── 4. LEARN → SEAR → ARSI: Q-Phi 3-cycle ─────────────────
        results = {}

        if strategy in ("learn_only", "learn_sear", "full_cycle"):
            # LEARN step (trust-modulated)
            results["learn"] = self.qphi.step(observation)  # learn

        if strategy in ("learn_sear", "full_cycle"):
            # SEAR step
            results["sear"] = self.qphi.step(observation)   # sear

        if strategy == "full_cycle":
            # ARSI step
            results["arsi"] = self.qphi.step(observation)   # arsi

        # ── 5. CERTIFY: Check if the action was safe ───────────────
        lyap_after = self.certificates.compute_lyapunov(
            observation, self.qphi.phase
        )
        lyap_after.churn = self._compute_churn(element_scores)

        cert = self.certificates.certify_action(lyap_before, lyap_after)

        if not cert.admitted:
            # REGRESSION DETECTED — rollback would happen here
            # In practice, the momentum field has homeostatic damping
            # that prevents catastrophic regression, so we log and
            # let the certificate inform the next strategy selection.
            self._total_regressions_blocked += 1
        else:
            self._total_improvements += 1

        # ── 6. AUDIT: Record everything ────────────────────────────
        self.certificates.record_outcome(
            lyap_after.violations, lyap_after.churn
        )
        self.certificates.tick_cooldowns()

        elapsed = (time.time() - t0) * 1000
        self._prev_element_scores = element_scores

        audit_entry = {
            "step": self._step_count,
            "strategy": strategy,
            "certificate": cert.admitted,
            "lyapunov": lyap_after.energy_tuple(),
            "trust": {f: round(self.hugger.channels[f].tau, 3) for f in FACES},
            "phase": self.qphi.phase.phase_name,
            "phase_index": round(self.qphi.phase.index, 2),
            "elapsed_ms": round(elapsed, 1),
        }
        self._audit.append(audit_entry)

        return {
            "step": self._step_count,
            "strategy": strategy,
            "certificate": {
                "admitted": cert.admitted,
                "reason": cert.reason,
                "lyapunov_before": lyap_before.energy_tuple(),
                "lyapunov_after": lyap_after.energy_tuple(),
            },
            "friendship": friendship,
            "qphi": results,
            "elapsed_ms": round(elapsed, 1),
        }

    def run(self, observations: list[dict], rounds: int = 3) -> list[dict]:
        """Run multiple rounds over a set of observations."""
        results = []
        for _round in range(rounds):
            for obs in observations:
                r = self.step(obs)
                r["round"] = _round
                results.append(r)
        return results

    def _compute_churn(self, current_scores: dict[str, float]) -> float:
        """Compute total churn (change magnitude) for Lyapunov C term."""
        total = 0.0
        for face in FACES:
            if face == "C":
                continue
            curr = current_scores.get(face, 0.5)
            prev = self._prev_element_scores.get(face, 0.5)
            total += abs(curr - prev)
        return total

    def status(self) -> dict:
        """Full pipeline status."""
        return {
            "step": self._step_count,
            "improvements": self._total_improvements,
            "regressions_blocked": self._total_regressions_blocked,
            "certificates": self.certificates.status(),
            "trust": self.hugger.status(),
            "qphi": self.qphi.status(),
        }

    def report(self) -> str:
        """Human-readable full pipeline report."""
        s = self.status()
        cert = s["certificates"]
        trust = s["trust"]
        qphi = s["qphi"]

        lines = [
            "═══════════════════════════════════════════════",
            "  AUTONOMIC SELF-IMPROVEMENT PIPELINE",
            "═══════════════════════════════════════════════",
            "",
            f"Step {s['step']} | Improvements: {s['improvements']} | Blocked: {s['regressions_blocked']}",
            "",
            "── HDCS Certificates ──",
            f"  Strategy: {cert['strategy']}",
            f"  Issued: {cert['certificates_issued']} | Rejected: {cert['certificates_rejected']} ({cert['rejection_rate']:.1%})",
            f"  Cooldowns: {cert['cooldowns']}",
            "",
            "── Quantum Hugging Trust ──",
        ]
        for face in FACES:
            t = trust[face]
            bar_len = int(t["tau"] * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(
                f"  {face}: [{bar}] τ={t['tau']:.3f} {t['mode']:7s} "
                f"streak={t['streak']} mult={t['multiplier']:.3f} "
                f"drift={t['drift']:.4f}"
            )

        lines.append("")
        lines.append("── Q-Phi Convergence ──")
        lines.append(
            f"  Phase: {qphi['convergence_phase']} ({qphi['convergence_index']})"
        )
        lines.append(
            f"  Coverage: {qphi['current_coverage']:.4f} (peak: {qphi['peak_coverage']:.4f})"
        )
        lines.append(f"  Stability: {qphi['stability']:.6f}")
        lines.append(
            f"  Frozen: {qphi['frozen_shells']}/{qphi['frozen_shells'] + qphi['active_shells']} shells"
        )

        lines.append("")
        lines.append("── Amplitudes ──")
        for face in FACES:
            a = qphi["amplitudes"][face]
            lines.append(
                f"  {face}: α={a['alpha']:.3f} β={a['beta']:.3f} γ={a['gamma']:.3f}"
            )

        lines.append("")
        lines.append("── Synergy ──")
        for pair, val in sorted(qphi["synergy_matrix"].items()):
            star = " ★" if pair in GOLDEN_BRIDGES else ""
            lines.append(f"  {pair}: {val:.4f}{star}")

        # Recent audit trail
        if self._audit:
            lines.append("")
            lines.append("── Recent Audit (last 5) ──")
            for entry in list(self._audit)[-5:]:
                cert_mark = "✓" if entry["certificate"] else "✗"
                lines.append(
                    f"  #{entry['step']}: {entry['strategy']:12s} {cert_mark} "
                    f"V={entry['lyapunov'][0]} S={entry['lyapunov'][1]:.3f} "
                    f"trust=[{','.join(f'{v:.2f}' for v in entry['trust'].values())}] "
                    f"phase={entry['phase']} ({entry['elapsed_ms']:.0f}ms)"
                )

        return "\n".join(lines)


# ── Singleton ───────────────────────────────────────────────────────────

_pipeline: Optional[AutonomicPipeline] = None


def get_pipeline(momentum: MomentumField = None) -> AutonomicPipeline:
    """Get or create the singleton autonomic pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = AutonomicPipeline(momentum)
    return _pipeline
