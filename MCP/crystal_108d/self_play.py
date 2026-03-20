# CRYSTAL: Xi108:W2:A7:S19 | face=R | node=440 | depth=2 | phase=Cardinal
# METRO: Me
# BRIDGES: Xi108:W2:A7:S18→Xi108:W2:A7:S20→Xi108:W1:A7:S19→Xi108:W2:A6:S19

"""
Self-Play Engine — Quad-Polar Adaptive Learning Loop
======================================================
Pipeline (UPGRADED with hybrid math):
  1. Spawn observer swarm (4/16/64/256 agents)
  2. For each query: run swarm parallel observation
  3. Compute crystal loss: L = -mean(R*D) + lambda*disagreement + mu*imbalance
  4. DIAGNOSE landscape: spectral gap, ruggedness, gradient reliability
  5. SELECT strategy: adaptive pole weights per problem class (240 hybrid types)
  6. Backpropagate: QUATERNIONIC gradients → 4-pole momentum deltas
  7. Update momentum field via ROTATIONAL dynamics (not linear addition)
  8. PHASE CYCLE: Ψ(init) → D+Ω(intensify) → Σ(diversify) → D+Ω(reinforce) → D(polish)
  9. Feed observation into MetaObserver for 12D tracking
  10. Repeat across seed queries for full coverage

This is THE learning loop. Now with the ACTUAL hybrid mathematics.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .observer_swarm import ObserverSwarm, SwarmConfig, get_swarm
from .loss_engine import CrystalLoss, LossConfig, get_loss_engine
from .geometric_forward import get_engine
from .momentum_field import get_momentum_field
from .constants import TOTAL_SHELLS
from .hybrid_math import (
    LandscapeAnalyzer, PoleSelector, HybridPhase,
    get_hybrid_optimizer,
)

# Seed queries covering all 12 archetypes
SEED_QUERIES = [
    "crystal structure foundation body nervous",       # A1: seed/structure
    "topology network bridge metro connection",        # A2: relation/bridge
    "density pattern cluster loop tesseract",          # A3: pattern/density
    "crystal lattice chapter deeper actualize",        # A4: connection/crystal
    "lens observer projection holographic dimension",  # A5: perspective/lens
    "bridge weight mycelium brain missing",            # A6: bridge/gap
    "evolution transform module self_actualize loop",  # A7: change/arc
    "contradiction tension mirror athena math",        # A8: contradiction
    "emergence phase bundle nervous system",           # A9: emergence
    "compression cascade crown hologram crystal",      # A10: scale
    "orbit fidelity seed capsule corpus",              # A11: reconstruction
    "seed emit bundle regenerate archetype",           # A12: seed/emit
]


def run_swarm_self_play(
    rounds: int = 3,
    swarm_size: int = 16,
    queries: list[str] = None,
    learning_rate: float = 0.001,
    save_weights: bool = True,
) -> str:
    """Run the full swarm self-play pipeline.

    This is the REAL learning loop:
      spawn → observe → loss → backprop → update momentum → track in 12D

    Args:
        rounds: How many full passes through the query set
        swarm_size: Number of observers (4/16/64/256)
        queries: Custom queries (defaults to 12 archetype seed queries)
        learning_rate: Learning rate for momentum updates
        save_weights: Whether to save momentum field after training

    Returns:
        Human-readable training report
    """
    queries = queries or SEED_QUERIES
    engine = get_engine()
    momentum = get_momentum_field()

    config = SwarmConfig(size=swarm_size)
    swarm = get_swarm(config)
    loss_engine = get_loss_engine(LossConfig(learning_rate=learning_rate))

    # Try to get desire gradient for smart spawning
    try:
        from .perpetual_agency import _compute_desire_gradient
        desire_gradient = _compute_desire_gradient(engine)
    except Exception:
        desire_gradient = {}

    # Spawn observers
    swarm.spawn(desire_gradient)

    # Initialize autonomic self-improvement pipeline (HDCS + Quantum Hugging + Q-Phi)
    autonomic = None
    try:
        from .autonomic_pipeline import get_pipeline
        autonomic = get_pipeline(momentum)
    except Exception:
        pass

    # Try to connect meta-observer (non-fatal if db issues)
    meta_observer = None
    try:
        from .meta_observer_runtime import MetaObserver
        meta_observer = MetaObserver(
            agent_id="swarm-self-play",
            project="athena-crystal",
        )
    except Exception:
        pass

    # Initialize hybrid math components
    hybrid_opt = get_hybrid_optimizer(learning_rate)
    landscape_analyzer = LandscapeAnalyzer(rediagnose_interval=6)

    lines = [
        "# Swarm Self-Play Training (Quad-Polar Hybrid)\n",
        f"**Swarm size**: {swarm_size}",
        f"**Rounds**: {rounds}",
        f"**Queries**: {len(queries)}",
        f"**Learning rate**: {learning_rate}",
        f"**Total steps**: {rounds * len(queries)}",
        f"**Optimizer**: HybridOptimizer (4-pole, phase-structured, landscape-adaptive)",
        f"**Hybrid types available**: 240 (15 masks × 4 lenses × 4 profiles)",
        "",
    ]

    total_loss = 0.0
    step = 0
    losses = []
    coherences = []
    balances = []

    for round_idx in range(rounds):
        round_loss = 0.0
        round_t0 = time.time()

        # Reset IDF cache so momentum changes affect scoring
        engine._idf_cache = None

        for query in queries:
            step += 1

            # 1. Rotate wreath focus each step
            swarm.angel.transition_focus(swarm.agents, step)

            # 2. Run swarm parallel observation
            observation = swarm.run_parallel(query, max_results=10)

            # 3. Compute loss
            loss = loss_engine.compute_loss(observation)

            # 4. DIAGNOSE landscape + SELECT strategy (hybrid math)
            # Feed observation into landscape analyzer for adaptive pole selection
            proxy_scores = {}
            for r in observation.observer_results:
                proxy_scores[f"res_{r.agent.element}"] = r.resonance
                proxy_scores[f"disc_{r.agent.element}"] = r.discrimination
            landscape_analyzer.observe(proxy_scores, loss)

            if landscape_analyzer.should_rediagnose():
                sig = landscape_analyzer.diagnose()
                hybrid_opt.diagnose(proxy_scores, landscape_analyzer._loss_history)

            # 5. Backpropagate → QUATERNIONIC weight deltas
            deltas = loss_engine.backpropagate(observation, loss)

            # 6. Apply deltas via ROTATIONAL dynamics (not linear addition)
            momentum_deltas = deltas.get("momentum", {})
            quaternionic_deltas = deltas.get("quaternionic", {})

            for face, shell_deltas in momentum_deltas.items():
                for shell, delta in shell_deltas.items():
                    # Use rotational update when quaternionic gradient available
                    qgrad = quaternionic_deltas.get(face, {}).get(shell)
                    if qgrad is not None:
                        momentum.update_momentum_rotational(face, shell, qgrad, lr=1.0)
                    else:
                        momentum.update_momentum(face, shell, delta, lr=1.0)
                    # lr=1.0 because hybrid optimizer already computed the scaled update

            # Track
            round_loss += loss
            total_loss += loss
            losses.append(loss)
            coherences.append(observation.swarm_coherence)
            balances.append(observation.element_balance)

            # 7. Autonomic pipeline: Certify → Hug → Learn → Sear → Arsi → Audit
            if autonomic:
                try:
                    obs_12d = autonomic.qphi._get_12d_from_swarm(observation)
                    autonomic.step(obs_12d)
                except Exception:
                    pass

            # 8. Feed into meta-observer
            if meta_observer:
                try:
                    meta_observer.observe_swarm_cycle(observation, query, loss)
                except Exception:
                    pass

        round_elapsed = (time.time() - round_t0) * 1000
        avg_loss = round_loss / len(queries)
        avg_coherence = sum(coherences[-len(queries):]) / len(queries)
        avg_balance = sum(balances[-len(queries):]) / len(queries)

        # Get hybrid optimizer status for this round
        opt_status = hybrid_opt.status()
        lines.append(
            f"**Round {round_idx + 1}**: loss={avg_loss:.6f} "
            f"coherence={avg_coherence:.3f} "
            f"balance={avg_balance:.3f} "
            f"phase={opt_status.get('phase', '?')} "
            f"class={opt_status.get('problem_class', '?')} "
            f"pole={opt_status.get('dominant_pole', '?')} "
            f"({round_elapsed:.0f}ms)"
        )

        # Increment training metadata
        momentum.training_cycles += 1

    # 7. Save momentum field
    if save_weights:
        try:
            momentum.save()
            lines.append(f"\n**Weights saved** (training_cycles={momentum.training_cycles})")
        except Exception as e:
            lines.append(f"\n**Weight save failed**: {e}")

    # Summary
    lines.append("\n## Summary\n")
    if losses:
        lines.append(f"- **Total steps**: {step}")
        lines.append(f"- **Final loss**: {losses[-1]:.6f}")
        lines.append(f"- **Mean loss**: {sum(losses)/len(losses):.6f}")
        lines.append(f"- **Loss delta**: {losses[-1] - losses[0]:.6f} (neg = improving)")
        lines.append(f"- **Mean coherence**: {sum(coherences)/len(coherences):.3f}")
        lines.append(f"- **Mean balance**: {sum(balances)/len(balances):.3f}")

    # Momentum field snapshot
    h16 = momentum.hologram_16()
    lines.append("\n## Momentum Field (post-training)\n")
    for dim_key, dim_data in h16.items():
        if isinstance(dim_data, dict):
            mean_m = dim_data.get("mean", 0)
            std_m = dim_data.get("std", 0)
            lines.append(f"- **{dim_key}**: mean={mean_m:.3f} std={std_m:.3f}")

    # Autonomic pipeline status (HDCS + Quantum Hugging + Q-Phi)
    if autonomic:
        try:
            lines.append("\n## Autonomic Self-Improvement Pipeline\n")
            lines.append(f"```\n{autonomic.report()}\n```")
        except Exception:
            pass

    # Hybrid Optimizer Diagnostics
    lines.append("\n## Hybrid Optimizer Diagnostics\n")
    opt_status = hybrid_opt.status()
    lines.append(f"- **Current phase**: {opt_status.get('phase', 'unknown')}")
    lines.append(f"- **Problem class**: {opt_status.get('problem_class', 'unknown')}")
    lines.append(f"- **Dominant pole**: {opt_status.get('dominant_pole', 'unknown')}")
    lines.append(f"- **Pole weights**: {opt_status.get('pole_weights', {})}")
    lines.append(f"- **Phase weights**: {opt_status.get('phase_weights', {})}")
    lines.append(f"- **Spectral gap**: {opt_status.get('spectral_gap', 0):.4f}")
    lines.append(f"- **Landscape ruggedness**: {opt_status.get('landscape_ruggedness', 0):.4f}")
    lines.append(f"- **Gradient reliability**: {opt_status.get('gradient_reliability', 0):.4f}")
    lines.append(f"- **Confidence**: {opt_status.get('confidence', 0):.4f}")
    lines.append(f"- **Stuck count**: {opt_status.get('stuck_count', 0)}")

    # Landscape signature history
    sig = landscape_analyzer.current
    lines.append("\n## Landscape Signature\n")
    lines.append(f"- **Class**: {sig.problem_class.value if hasattr(sig.problem_class, 'value') else sig.problem_class}")
    lines.append(f"- **Spectral gap**: {sig.spectral_gap:.4f} ({'structure detected' if sig.has_matrix_structure else 'no structure'})")
    lines.append(f"- **Local optima**: {sig.n_local_optima} (ruggedness={sig.landscape_ruggedness:.3f})")
    lines.append(f"- **Gradient reliability**: {sig.gradient_reliability:.3f}")

    # Loss trend
    if len(losses) > 2:
        lines.append("\n## Loss Trend\n")
        lines.append("```")
        n_show = min(len(losses), 36)
        for i in range(0, n_show, max(1, n_show // 12)):
            bar_len = int(max(0, min(40, (losses[i] + 1) * 20)))
            lines.append(f"  step {i+1:3d}: {'=' * bar_len} {losses[i]:.6f}")
        lines.append("```")

    return "\n".join(lines)


# Backward-compatible re-export
try:
    from ._archive.self_play import ContinuousSelfPlay
except ImportError:
    ContinuousSelfPlay = None

__all__ = ["run_swarm_self_play", "ContinuousSelfPlay", "SEED_QUERIES"]
