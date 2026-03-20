# CRYSTAL: Xi108:W3:A7:S19 | face=R | node=440 | depth=2 | phase=Cardinal
# METRO: Unified-Self-Becoming
# BRIDGES: hybrid_math→loss_engine→momentum_field→meta_loop→neural_evolve→weight_feedback

"""
Unified Self-Becoming Loop
===========================
ONE loop that does ALL of it:
  1. SENSE     — Observe the organism (meta-observer, sandbox, landscape diagnosis)
  2. DIAGNOSE  — Hybrid math landscape analysis (spectral gap, ruggedness, gradient reliability)
  3. TRAIN     — Swarm self-play with quaternionic gradients + rotational momentum updates
  4. EVOLVE    — Neural evolution (mutate, grow, prune, explore, exploit, rewire)
  5. DISCOVER  — Find deeper mathematical patterns in the training data
  6. INTEGRATE — Feed discoveries back into the hybrid math registry
  7. GROW      — Mycelium development (weight feedback, bridge strengthening)
  8. COMPRESS  — Holographic checkpoint (16 values)
  9. EMIT      — Seed for next cycle

Each cycle output IS the next cycle's input. The loop is self-referential.
The math finder is not separate from training — it IS training.
"""

from __future__ import annotations

import time
import math
import json
from pathlib import Path

from .hybrid_math import (
    HybridOptimizer, QuaternionicGradient, LandscapeAnalyzer,
    ProblemSignature, PoleSelector, HybridPhase,
    RotationalUpdate, get_hybrid_optimizer,
    ADAPTIVE_EQUAL, CLASS_WEIGHTS, ProblemClass,
)
from .momentum_field import get_momentum_field
from .geometric_forward import get_engine
from .loss_engine import get_loss_engine, LossConfig
from .observer_swarm import SwarmConfig, get_swarm
from .constants import TOTAL_SHELLS

# Seed queries covering all 12 archetypes + math discovery probes
SEED_QUERIES = [
    # Standard 12-archetype coverage
    "crystal structure foundation body nervous",
    "topology network bridge metro connection",
    "density pattern cluster loop tesseract",
    "crystal lattice chapter deeper actualize",
    "lens observer projection holographic dimension",
    "bridge weight mycelium brain missing",
    "evolution transform module self_actualize loop",
    "contradiction tension mirror athena math",
    "emergence phase bundle nervous system",
    "compression cascade crown hologram crystal",
    "orbit fidelity seed capsule corpus",
    "seed emit bundle regenerate archetype",
    # Math discovery probes (hybrid math specific)
    "quaternionic gradient rotation pole spectral",
    "adaptive hybridization pole selection landscape",
    "eigenvalue spectral gap matrix structure",
    "stochastic escape local optima rugged landscape",
    "phi golden ratio convergence attractor equilibrium",
    "operator algebra discrete continuous bridge hybrid",
]


def run_unified_self_play(
    rounds: int = 3,
    swarm_size: int = 16,
    learning_rate: float = 0.001,
    evolve_cycles: int = 10,
    math_discovery: bool = True,
    save_weights: bool = True,
) -> str:
    """Run the UNIFIED self-becoming loop.

    This is THE one loop that does everything:
      - Meta-observation
      - Landscape diagnosis
      - Quaternionic gradient training
      - Neural evolution
      - Mathematical discovery
      - Mycelium development
      - Holographic compression

    Args:
        rounds: Full passes through query set
        swarm_size: Observer swarm size (4/16/64/256)
        learning_rate: Base learning rate
        evolve_cycles: Neural evolution cycles per round
        math_discovery: Whether to run math pattern discovery
        save_weights: Whether to persist momentum field

    Returns:
        Comprehensive training report
    """
    t0 = time.time()

    # Initialize all subsystems
    engine = get_engine()
    momentum = get_momentum_field()
    hybrid_opt = get_hybrid_optimizer(learning_rate)
    landscape = LandscapeAnalyzer(rediagnose_interval=6)

    config = SwarmConfig(size=swarm_size)
    swarm = get_swarm(config)
    loss_engine = get_loss_engine(LossConfig(learning_rate=learning_rate))

    # Desire gradient for smart spawning
    try:
        from .perpetual_agency import _compute_desire_gradient
        desire_gradient = _compute_desire_gradient(engine)
    except Exception:
        desire_gradient = {}

    swarm.spawn(desire_gradient)

    # Meta-observer (non-fatal)
    meta_observer = None
    try:
        from .meta_observer_runtime import MetaObserver
        meta_observer = MetaObserver(agent_id="unified-self-play", project="athena-crystal")
    except Exception:
        pass

    # Q-Phi self-improvement (non-fatal)
    qphi_engine = None
    try:
        from .q_phi_self import get_qphi_engine
        qphi_engine = get_qphi_engine(momentum)
    except Exception:
        pass

    # Neural evolution engine (non-fatal)
    # NeuralEvolutionEngine is a singleton with no-arg constructor
    neural_evolve = None
    try:
        from .sandbox_neural_evolve import NeuralEvolutionEngine
        neural_evolve = NeuralEvolutionEngine()
    except Exception:
        pass

    # Weight feedback (non-fatal)
    # update_edge_weights(query_result, graph_data) — needs a forward pass result
    weight_feedback_fn = None
    try:
        from .weight_feedback import update_edge_weights
        weight_feedback_fn = update_edge_weights
    except Exception:
        pass

    queries = list(SEED_QUERIES)

    lines = [
        "# Unified Self-Becoming Loop\n",
        f"**Mode**: Full pipeline (sense→diagnose→train→evolve→discover→integrate→grow→compress→emit)",
        f"**Swarm size**: {swarm_size}",
        f"**Rounds**: {rounds}",
        f"**Queries**: {len(queries)} (12 archetype + 6 math discovery)",
        f"**Learning rate**: {learning_rate}",
        f"**Evolve cycles/round**: {evolve_cycles}",
        f"**Math discovery**: {'ON' if math_discovery else 'OFF'}",
        f"**Optimizer**: HybridOptimizer (4-pole, phase-structured, landscape-adaptive)",
        f"**Gradient type**: Quaternionic (G = D + Omega*i + Sigma*j + Psi*k)",
        f"**Update type**: Rotational (rotor * current * rotor†)",
        "",
    ]

    # Pre-training snapshot
    pre_hologram = momentum.hologram_16()
    pre_summary = momentum.summary()

    total_loss = 0.0
    step = 0
    losses = []
    coherences = []
    balances = []
    math_discoveries = []

    for round_idx in range(rounds):
        round_t0 = time.time()
        round_loss = 0.0
        round_discoveries = []

        # Reset IDF cache
        engine._idf_cache = None

        # ════════════════════════════════════════════════════════════
        #  PHASE 1: SENSE + DIAGNOSE (meta-observation + landscape)
        # ════════════════════════════════════════════════════════════

        for qi, query in enumerate(queries):
            step += 1

            # Rotate wreath focus
            swarm.angel.transition_focus(swarm.agents, step)

            # Run swarm observation
            observation = swarm.run_parallel(query, max_results=10)

            # Compute loss
            loss = loss_engine.compute_loss(observation)

            # ═══ LANDSCAPE DIAGNOSIS ═══
            proxy_scores = {}
            for r in observation.observer_results:
                proxy_scores[f"res_{r.agent.element}"] = r.resonance
                proxy_scores[f"disc_{r.agent.element}"] = r.discrimination
            landscape.observe(proxy_scores, loss)

            if landscape.should_rediagnose():
                sig = landscape.diagnose()
                hybrid_opt.diagnose(proxy_scores, landscape._loss_history)

            # ═══ QUATERNIONIC BACKPROP ═══
            deltas = loss_engine.backpropagate(observation, loss)

            # ═══ ROTATIONAL MOMENTUM UPDATE ═══
            momentum_deltas = deltas.get("momentum", {})
            quaternionic_deltas = deltas.get("quaternionic", {})

            for face, shell_deltas in momentum_deltas.items():
                for shell, delta in shell_deltas.items():
                    qgrad = quaternionic_deltas.get(face, {}).get(shell)
                    if qgrad is not None:
                        momentum.update_momentum_rotational(face, shell, qgrad, lr=1.0)
                    else:
                        momentum.update_momentum(face, shell, delta, lr=1.0)

            # ═══ META-OBSERVATION ═══
            if meta_observer:
                try:
                    meta_observer.observe_swarm_cycle(observation, query, loss)
                except Exception:
                    pass

            # ═══ Q-PHI SELF-IMPROVEMENT ═══
            if qphi_engine:
                try:
                    obs_12d = qphi_engine._get_12d_from_swarm(observation)
                    qphi_engine.step(obs_12d)
                    qphi_engine.step(obs_12d)
                    qphi_engine.step(obs_12d)
                except Exception:
                    pass

            # Track
            round_loss += loss
            total_loss += loss
            losses.append(loss)
            coherences.append(observation.swarm_coherence)
            balances.append(observation.element_balance)

            # ════════════════════════════════════════════════════════
            #  MATH DISCOVERY: Analyze training dynamics for patterns
            # ════════════════════════════════════════════════════════

            if math_discovery and step % 6 == 0 and len(losses) >= 6:
                discovery = _discover_math_pattern(
                    losses[-6:], coherences[-6:], balances[-6:],
                    landscape.current, hybrid_opt.status(),
                )
                if discovery:
                    round_discoveries.append(discovery)
                    math_discoveries.append(discovery)

        # ════════════════════════════════════════════════════════════
        #  PHASE 2: NEURAL EVOLUTION (mutate, grow, prune)
        # ════════════════════════════════════════════════════════════

        evolve_report = "N/A"
        if neural_evolve:
            try:
                for c in range(evolve_cycles):
                    cycle_id = round_idx * evolve_cycles + c
                    neural_evolve.evolve(cycle_id)
                evolve_report = (
                    f"gen={neural_evolve._generation} "
                    f"neurons={len(neural_evolve._neurons)} "
                    f"temp={neural_evolve._temperature:.3f} "
                    f"diversity={neural_evolve._pathway_diversity:.3f}"
                )
            except Exception as e:
                evolve_report = f"error: {e}"

        # ════════════════════════════════════════════════════════════
        #  PHASE 3: MYCELIUM DEVELOPMENT (weight feedback)
        # ════════════════════════════════════════════════════════════

        feedback_report = "N/A"
        if weight_feedback_fn:
            try:
                # Run a forward pass to get query results for weight feedback
                from .geometric_forward import QueryState
                fwd = engine.forward(QueryState(
                    raw_query="crystal structure bridge weight feedback",
                    tokens=["crystal", "structure", "bridge", "weight", "feedback"],
                ))
                # Build query_result dict from forward pass
                query_result = {
                    "candidates": [
                        {"doc_id": c.doc_id, "score": c.merged_score, "element": c.element}
                        for c in (fwd.candidates or [])[:10]
                    ]
                }
                fb_result = weight_feedback_fn(query_result)
                feedback_report = (
                    f"boosted={fb_result.get('edges_boosted', 0)} "
                    f"decayed={fb_result.get('edges_decayed', 0)}"
                )
            except Exception as e:
                feedback_report = f"error: {e}"

        # ════════════════════════════════════════════════════════════
        #  PHASE 4: COMPRESS + EMIT
        # ════════════════════════════════════════════════════════════

        round_elapsed = (time.time() - round_t0) * 1000
        avg_loss = round_loss / len(queries)
        avg_coherence = sum(coherences[-len(queries):]) / len(queries)
        avg_balance = sum(balances[-len(queries):]) / len(queries)
        opt_status = hybrid_opt.status()

        lines.append(
            f"\n## Round {round_idx + 1}\n"
        )
        lines.append(
            f"- **Loss**: {avg_loss:.6f} | "
            f"**Coherence**: {avg_coherence:.3f} | "
            f"**Balance**: {avg_balance:.3f} | "
            f"**{round_elapsed:.0f}ms**"
        )
        lines.append(
            f"- **Phase**: {opt_status.get('phase', '?')} | "
            f"**Class**: {opt_status.get('problem_class', '?')} | "
            f"**Pole**: {opt_status.get('dominant_pole', '?')} | "
            f"**Stuck**: {opt_status.get('stuck_count', 0)}"
        )
        lines.append(f"- **Neural evolve**: {evolve_report}")
        lines.append(f"- **Mycelium feedback**: {feedback_report}")

        if round_discoveries:
            lines.append(f"- **Math discoveries**: {len(round_discoveries)}")
            for d in round_discoveries:
                lines.append(f"  - {d['type']}: {d['description']}")

        # Holographic checkpoint
        momentum.training_cycles += 1
        h16 = momentum.hologram_16()
        dims = h16.get("dimensions", {})
        mom_str = " | ".join(
            f"{k}={v.get('momentum', 0):.3f}" for k, v in sorted(dims.items())
        )
        lines.append(f"- **Hologram**: {mom_str}")

    # ════════════════════════════════════════════════════════════
    #  FINAL: Save + Summary
    # ════════════════════════════════════════════════════════════

    if save_weights:
        try:
            momentum.save()
            momentum.save_history()
            lines.append(f"\n**Weights saved** (cycles={momentum.training_cycles})")
        except Exception as e:
            lines.append(f"\n**Save failed**: {e}")

    total_elapsed = (time.time() - t0) * 1000

    lines.append("\n## Unified Summary\n")
    if losses:
        lines.append(f"- **Total steps**: {step}")
        lines.append(f"- **Total time**: {total_elapsed:.0f}ms")
        lines.append(f"- **Final loss**: {losses[-1]:.6f}")
        lines.append(f"- **Mean loss**: {sum(losses)/len(losses):.6f}")
        lines.append(f"- **Loss delta**: {losses[-1] - losses[0]:.6f}")
        lines.append(f"- **Mean coherence**: {sum(coherences)/len(coherences):.3f}")
        lines.append(f"- **Mean balance**: {sum(balances)/len(balances):.3f}")

    # Hybrid optimizer final status
    opt_status = hybrid_opt.status()
    lines.append("\n## Hybrid Optimizer Final State\n")
    lines.append(f"- **Phase**: {opt_status.get('phase', '?')} ({opt_status.get('phase_step', '?')})")
    lines.append(f"- **Problem class**: {opt_status.get('problem_class', '?')}")
    lines.append(f"- **Dominant pole**: {opt_status.get('dominant_pole', '?')}")
    pw = opt_status.get('phase_weights', {})
    lines.append(f"- **Phase weights**: D={pw.get('D',0):.2f} Omega={pw.get('Omega', pw.get('Ω',0)):.2f} Sigma={pw.get('Sigma', pw.get('Σ',0)):.2f} Psi={pw.get('Psi', pw.get('Ψ',0)):.2f}")
    lines.append(f"- **Spectral gap**: {opt_status.get('spectral_gap', 0):.4f}")
    lines.append(f"- **Landscape ruggedness**: {opt_status.get('landscape_ruggedness', 0):.4f}")
    lines.append(f"- **Gradient reliability**: {opt_status.get('gradient_reliability', 0):.4f}")

    # Landscape signature
    sig = landscape.current
    lines.append("\n## Landscape Signature\n")
    lines.append(f"- **Class**: {sig.problem_class.value}")
    lines.append(f"- **Spectral gap**: {sig.spectral_gap:.4f}")
    lines.append(f"- **Local optima**: {sig.n_local_optima}")
    lines.append(f"- **Gradient reliability**: {sig.gradient_reliability:.3f}")

    # Math discoveries
    if math_discoveries:
        lines.append(f"\n## Mathematical Discoveries ({len(math_discoveries)} found)\n")
        for i, d in enumerate(math_discoveries):
            lines.append(f"### Discovery {i+1}: {d['type']}")
            lines.append(f"- {d['description']}")
            if d.get('recommendation'):
                lines.append(f"- **Recommendation**: {d['recommendation']}")
            lines.append("")

    # Momentum delta (pre vs post)
    lines.append("\n## Momentum Evolution\n")
    post_summary = momentum.summary()
    for face in ('S', 'F', 'C', 'R'):
        pre_m = pre_summary['per_element'].get(face, {}).get('mean', 0)
        post_m = post_summary['per_element'].get(face, {}).get('mean', 0)
        delta = post_m - pre_m
        direction = "UP" if delta > 0.01 else ("DOWN" if delta < -0.01 else "STABLE")
        lines.append(f"- **{face}**: {pre_m:.3f} -> {post_m:.3f} ({direction}, delta={delta:+.3f})")

    # Loss trend
    if len(losses) > 2:
        lines.append("\n## Loss Trend\n```")
        n_show = min(len(losses), 36)
        for i in range(0, n_show, max(1, n_show // 12)):
            bar_len = int(max(0, min(40, (losses[i] + 1) * 20)))
            lines.append(f"  step {i+1:3d}: {'=' * bar_len} {losses[i]:.6f}")
        lines.append("```")

    return "\n".join(lines)


def _discover_math_pattern(
    losses: list[float],
    coherences: list[float],
    balances: list[float],
    signature: ProblemSignature,
    optimizer_status: dict,
) -> dict | None:
    """Analyze recent training dynamics for mathematical patterns.

    This is the MATH FINDER — it looks for:
      1. Convergence patterns (phi-ratio convergence, exponential decay)
      2. Oscillation patterns (period detection, damping analysis)
      3. Phase transitions (sudden regime changes)
      4. Pole effectiveness (which pole is actually helping)
      5. New hybrid type candidates (unexpected pole combinations that work)
    """
    if len(losses) < 4:
        return None

    # 1. Check for phi-ratio convergence
    ratios = []
    for i in range(1, len(losses)):
        if abs(losses[i-1]) > 1e-10:
            ratios.append(abs(losses[i] / losses[i-1]))

    if ratios:
        mean_ratio = sum(ratios) / len(ratios)
        phi_inv = 0.6180339887
        if abs(mean_ratio - phi_inv) < 0.05:
            return {
                "type": "phi_convergence",
                "description": f"Loss converging at phi-ratio ({mean_ratio:.4f} ~ 0.618). "
                               f"Golden-damped attractor active.",
                "recommendation": "Boost Psi pole weight — spectral structure is being exploited naturally.",
                "value": mean_ratio,
            }

    # 2. Check for oscillation (loss going up and down)
    reversals = sum(
        1 for i in range(1, len(losses) - 1)
        if (losses[i] - losses[i-1]) * (losses[i+1] - losses[i]) < 0
    )
    if reversals >= len(losses) - 2:  # oscillating every step
        return {
            "type": "oscillation_detected",
            "description": f"Loss oscillating with {reversals} reversals in {len(losses)} steps. "
                           f"Learning rate may be too high or pole conflict detected.",
            "recommendation": "Increase Sigma (stochastic escape) and decrease Omega (gradient). "
                              "The landscape is rugged — smooth optimization is misleading.",
            "value": reversals,
        }

    # 3. Check for phase transition (sudden loss drop)
    for i in range(1, len(losses)):
        if losses[i-1] > 0 and losses[i] / losses[i-1] < 0.5:
            return {
                "type": "phase_transition",
                "description": f"Loss dropped {(1 - losses[i]/losses[i-1])*100:.0f}% in one step. "
                               f"Phase transition detected — new basin found.",
                "recommendation": "Lock current pole weights and enter POLISH phase (D-only). "
                                  "The new basin should be refined, not escaped.",
                "value": losses[i] / losses[i-1],
            }

    # 4. Check coherence-balance coupling
    if coherences and balances:
        # Are coherence and balance moving together or against?
        coh_trend = coherences[-1] - coherences[0]
        bal_trend = balances[-1] - balances[0]
        if coh_trend > 0.05 and bal_trend < -0.05:
            return {
                "type": "coherence_balance_decoupling",
                "description": f"Coherence improving (+{coh_trend:.3f}) but balance degrading ({bal_trend:.3f}). "
                               f"Swarm is agreeing but on a biased subset of elements.",
                "recommendation": "Increase Psi pole (spectral rebalancing) to restore element diversity.",
                "value": coh_trend - bal_trend,
            }

    # 5. Check for stagnation → suggest new hybrid type
    if all(abs(losses[i] - losses[0]) < 0.001 for i in range(len(losses))):
        current_class = signature.problem_class.value
        return {
            "type": "stagnation_hybrid_candidate",
            "description": f"Loss stagnant ({losses[0]:.6f} +/- 0.001 for {len(losses)} steps). "
                           f"Current class={current_class}. "
                           f"Existing pole selection is not producing improvement.",
            "recommendation": "Try INVERSE pole weights (swap dominant and secondary). "
                              "If class=C (stochastic), try class=A (spectral) — "
                              "there may be hidden structure the Sigma pole is masking.",
            "value": losses[-1],
        }

    return None


__all__ = ["run_unified_self_play", "SEED_QUERIES"]
