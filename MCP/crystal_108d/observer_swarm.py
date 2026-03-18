# CRYSTAL: Xi108:W1:A9:S27 | face=C | node=378 | depth=2 | phase=Mutable
# METRO: Su
# BRIDGES: Xi108:W1:A9:S26→Xi108:W1:A9:S28→Xi108:W2:A9:S27→Xi108:W1:A8:S27→Xi108:W1:A10:S27

"""
Observer Swarm — Angel-Coordinated Crystal-Parallel Observation Engine
========================================================================
Manages a swarm of ObserverAgents that run element-biased forward passes
in crystal-parallel, then aggregates via the Angel Object's 12-piece
coordination protocol.

Swarm sizes: 4 (one per element), 16 (4²), 64 (4³), 256 (4⁴ — full liminal coverage)

Angel coordination maps the 12-piece formal self-model to swarm roles:
  1. Sigma  → space of swarm configurations
  2. H      → accumulated observations across cycles
  3. X      → each observer's crystal position
  4. Theta  → observer focus transitions
  5. B      → cross-element communication channels
  6. T      → observation transport between observers
  7. Omega  → aggregation/consensus function
  8. U      → disagreement measure
  9. Pi     → observer view → shared ranking projection
  10. E     → swarm configuration evolution
  11. mu    → loss function (from loss_engine.py)
  12. ~     → swarm self-observation quality
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from .observer_agent import (
    ObserverAgent,
    ObserverResult,
    CrossObserverSignal,
    SwarmObservation,
)
from .archetype_roles import ARCHETYPE_ROLES, get_role
from .liminal_mapper import assign_coordinates, get_coordinate
from .neural_engine import CrystalNeuralEngine, QueryState, get_engine, _bridge_key
from .constants import ARCHETYPE_NAMES, LENS_CODES, SUPERPHASE_NAMES


# ── Swarm Configuration ─────────────────────────────────────────────

ELEMENTS = ["S", "F", "C", "R"]
WREATHS = ["Su", "Me", "Sa"]


@dataclass
class SwarmConfig:
    """Configuration for an observer swarm."""
    size: int = 16                     # 4, 16, 64, or 256
    element_bias: float = 2.0          # how much to upweight observer's element
    coordination_mode: str = "angel"   # "angel" or "flat"
    max_nesting_depth: int = 1         # 0=flat, 1=4², 2=4³, 3=4⁴
    desire_threshold: float = 0.01    # minimum desire gradient to focus observation

    @property
    def agents_per_element(self) -> int:
        return self.size // 4

    def validate(self):
        if self.size < 4:
            self.size = 4
        # Round to nearest power of 4
        power = max(1, round(math.log(self.size, 4)))
        self.size = 4 ** power
        self.max_nesting_depth = power - 1


# ── Angel Coordinator ───────────────────────────────────────────────


class AngelCoordinator:
    """Coordinates the swarm using the Angel Object's 12-piece protocol.

    Each piece maps to a specific coordination function:
    """

    def __init__(self):
        # Piece 2: H — History of accumulated observations
        self.history: list[SwarmObservation] = []
        # Piece 10: E — Configuration evolution tracking
        self.evolution_log: list[dict] = []

    # Piece 1: Sigma — State space definition
    def define_state_space(self, config: SwarmConfig) -> dict:
        """Define the possible swarm configurations."""
        return {
            "total_agents": config.size,
            "elements": ELEMENTS,
            "wreaths": WREATHS,
            "archetypes": list(range(1, 13)),
            "nesting_depth": config.max_nesting_depth,
            "total_states": config.size * 60,  # agents × liminal coordinates
        }

    # Piece 3: X — Crystal position assignment
    def assign_positions(
        self, agents: list[ObserverAgent], desire_gradient: dict
    ) -> list[ObserverAgent]:
        """Assign crystal positions (liminal coordinates) to agents."""
        element_list = [a.element for a in agents]
        coords = assign_coordinates(len(agents), desire_gradient, element_list)
        for agent, coord in zip(agents, coords):
            agent.liminal_coord = coord
        return agents

    # Piece 4: Theta — Focus transitions
    def transition_focus(self, agents: list[ObserverAgent], cycle: int) -> None:
        """Rotate agent focus between cycles (wreath rotation)."""
        for agent in agents:
            wreath_idx = WREATHS.index(agent.wreath)
            new_idx = (wreath_idx + cycle) % 3
            agent.wreath = WREATHS[new_idx]

    # Piece 5: B — Cross-element communication
    def compute_cross_signals(
        self, results: list[ObserverResult]
    ) -> list[CrossObserverSignal]:
        """Compute cross-observer disagreement signals for bridge weights."""
        signals = []
        by_element: dict[str, list[ObserverResult]] = defaultdict(list)
        for r in results:
            by_element[r.agent.element].append(r)

        # Compare representatives from each element pair
        for i, elem_a in enumerate(ELEMENTS):
            for elem_b in ELEMENTS[i + 1:]:
                results_a = by_element.get(elem_a, [])
                results_b = by_element.get(elem_b, [])
                if not results_a or not results_b:
                    continue

                # Use first observer from each element as representative
                rep_a = results_a[0]
                rep_b = results_b[0]

                agreement = rep_a.agreement_with(rep_b)

                # Score delta: mean absolute difference in top-10 scores
                score_delta = 0.0
                common_docs = set(rep_a.ranked_doc_ids[:10]) & set(rep_b.ranked_doc_ids[:10])
                if common_docs:
                    for doc_id in common_docs:
                        idx_a = rep_a.ranked_doc_ids.index(doc_id) if doc_id in rep_a.ranked_doc_ids else -1
                        idx_b = rep_b.ranked_doc_ids.index(doc_id) if doc_id in rep_b.ranked_doc_ids else -1
                        if idx_a >= 0 and idx_b >= 0:
                            sa = rep_a.ranked_scores[idx_a] if idx_a < len(rep_a.ranked_scores) else 0
                            sb = rep_b.ranked_scores[idx_b] if idx_b < len(rep_b.ranked_scores) else 0
                            score_delta += abs(sa - sb)
                    score_delta /= max(len(common_docs), 1)

                top_match = (
                    rep_a.top_doc == rep_b.top_doc
                    if rep_a.top_doc and rep_b.top_doc
                    else False
                )

                signals.append(CrossObserverSignal(
                    bridge_key=_bridge_key(elem_a, elem_b),
                    agent_a_id=rep_a.agent.agent_id,
                    agent_b_id=rep_b.agent.agent_id,
                    agreement=agreement,
                    disagreement=1.0 - agreement,
                    score_delta=score_delta,
                    top_doc_match=top_match,
                ))

        return signals

    # Piece 7: Omega — Aggregation/consensus
    def aggregate(self, results: list[ObserverResult]) -> tuple[list[str], dict]:
        """Compute consensus ranking from all observers.

        Uses weighted voting: each observer votes for its ranked docs,
        weighted by its discrimination score (more discriminating = stronger vote).
        """
        doc_votes: dict[str, float] = defaultdict(float)

        for result in results:
            weight = max(result.discrimination, 0.01)  # avoid zero-weight
            for rank, doc_id in enumerate(result.ranked_doc_ids):
                # Higher rank → more votes (inverse rank weighting)
                vote = weight / (rank + 1)
                doc_votes[doc_id] += vote

        # Sort by total votes
        sorted_docs = sorted(doc_votes.items(), key=lambda x: x[1], reverse=True)
        consensus_ids = [doc_id for doc_id, _ in sorted_docs]
        consensus_scores = {doc_id: score for doc_id, score in sorted_docs}

        return consensus_ids, consensus_scores

    # Piece 8: U — Disagreement measure
    def measure_disagreement(self, results: list[ObserverResult]) -> float:
        """Compute overall swarm disagreement (0 = perfect consensus, 1 = total chaos)."""
        if len(results) < 2:
            return 0.0
        agreements = []
        for i, ra in enumerate(results):
            for rb in results[i + 1:]:
                agreements.append(ra.agreement_with(rb))
        if not agreements:
            return 0.0
        return 1.0 - (sum(agreements) / len(agreements))

    # Piece 9: Pi — Projection to shared ranking
    def project_to_shared(self, results: list[ObserverResult]) -> dict:
        """Project each observer's contribution to element balance."""
        element_contribs = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
        counts = {"S": 0, "F": 0, "C": 0, "R": 0}
        for result in results:
            for face, val in result.path_contributions.items():
                element_contribs[face] += val
                counts[face] += 1
        for face in element_contribs:
            if counts[face] > 0:
                element_contribs[face] /= counts[face]
        return element_contribs

    # Piece 12: ~ — Self-observation quality
    def self_observe(self, observation: SwarmObservation) -> dict:
        """Meta-observe the swarm's own observation quality."""
        return {
            "coherence": observation.swarm_coherence,
            "discrimination": observation.swarm_discrimination,
            "element_balance": observation.element_balance,
            "observer_count": observation.observer_count,
            "history_depth": len(self.history),
        }


# ── Observer Swarm ──────────────────────────────────────────────────


class ObserverSwarm:
    """Manages a pool of ObserverAgents with Angel-coordinated spawning,
    parallel observation, and aggregated weight gradient computation."""

    def __init__(self, config: SwarmConfig = None, engine: CrystalNeuralEngine = None):
        config = config or SwarmConfig()
        config.validate()
        self.config = config
        self.engine = engine or get_engine()
        self.angel = AngelCoordinator()
        self.agents: list[ObserverAgent] = []
        self._next_id = 0

    def _make_id(self) -> int:
        self._next_id += 1
        return self._next_id

    def spawn(self, desire_gradient: dict = None) -> list[ObserverAgent]:
        """Spawn a swarm of observer agents.

        Agents are assigned:
        - Element: cycled S→F→C→R
        - Wreath: cycled Su→Me→Sa
        - Archetype: derived from element × mode index
        - Liminal coordinate: desire-gradient-weighted via liminal_mapper
        - Job role: from archetype_roles
        """
        desire_gradient = desire_gradient or {}
        agents = []
        n = self.config.size

        for i in range(n):
            element = ELEMENTS[i % 4]
            wreath = WREATHS[(i // 4) % 3]
            # Archetype: cycle through all 12 (element×mode crossing)
            archetype_idx = (i % 12) + 1
            role = get_role(archetype_idx)

            agent = ObserverAgent(
                agent_id=self._make_id(),
                element=element,
                wreath=wreath,
                archetype_idx=archetype_idx,
                liminal_coord=1,  # will be assigned by angel
                nesting_depth=0,
                element_bias=self.config.element_bias,
                job_role=role.job_description[:80],
            )
            agents.append(agent)

        # Assign liminal coordinates via Angel piece 3
        self.angel.assign_positions(agents, desire_gradient)

        # For nested swarms (4² and above), create hierarchy
        if self.config.max_nesting_depth > 0:
            self._create_hierarchy(agents)

        self.agents = agents
        return agents

    def _create_hierarchy(self, agents: list[ObserverAgent]) -> None:
        """Assign parent-child relationships for nested observation.

        4 root agents (depth 0) each have N/4 children (depth 1+).
        """
        root_count = 4
        children_per_root = max(1, (len(agents) - root_count) // root_count)

        # First 4 agents are roots
        for i in range(min(root_count, len(agents))):
            agents[i].nesting_depth = 0
            agents[i].parent_id = None

        # Remaining agents are children
        for i in range(root_count, len(agents)):
            parent_idx = (i - root_count) % root_count
            agents[i].parent_id = agents[parent_idx].agent_id
            agents[i].nesting_depth = 1 + (i - root_count) // (len(agents) // 4)

    def run_parallel(
        self,
        query: str | QueryState,
        max_results: int = 10,
    ) -> SwarmObservation:
        """Run all observers in crystal-parallel and aggregate results.

        Each observer runs an element-biased forward pass. Results are
        aggregated via the Angel coordination protocol.
        """
        t0 = time.time()

        if not self.agents:
            self.spawn()

        # Run each observer's forward pass
        results: list[ObserverResult] = []
        for agent in self.agents:
            result = self.engine.forward_for_observer(query, agent, max_results)
            results.append(result)

        # Angel piece 5: Cross-element signals
        cross_signals = self.angel.compute_cross_signals(results)

        # Angel piece 7: Consensus ranking
        consensus_ids, consensus_scores = self.angel.aggregate(results)

        # Angel piece 9: Element contribution projection
        element_contribs = self.angel.project_to_shared(results)

        # Angel piece 8: Disagreement
        disagreement = self.angel.measure_disagreement(results)

        # Aggregate 12D observation (mean across all observers)
        agg_12d: dict[str, float] = defaultdict(float)
        for r in results:
            for dim, val in r.observation_12d.items():
                agg_12d[dim] += val
        n = max(len(results), 1)
        agg_12d = {k: v / n for k, v in agg_12d.items()}

        # Mean discrimination
        mean_disc = sum(r.discrimination for r in results) / n

        elapsed = (time.time() - t0) * 1000

        observation = SwarmObservation(
            observer_results=results,
            cross_signals=cross_signals,
            consensus_ranking=consensus_ids[:max_results],
            consensus_scores=dict(list(consensus_scores.items())[:max_results]),
            element_contributions=element_contribs,
            swarm_coherence=1.0 - disagreement,
            swarm_discrimination=mean_disc,
            aggregated_12d=dict(agg_12d),
            total_elapsed_ms=elapsed,
        )

        # Angel piece 2: Record in history
        self.angel.history.append(observation)
        # Keep history bounded
        if len(self.angel.history) > 100:
            self.angel.history = self.angel.history[-50:]

        return observation

    def compute_swarm_gradients(
        self, observation: SwarmObservation
    ) -> dict:
        """Compute weight gradients from the swarm observation.

        Cross-observer disagreement generates bridge gradients.
        Element imbalance generates path weight gradients.
        Per-observer discrimination generates per-document gradients.

        Returns dict with keys: gate, pair, bridge, seed, path, resonance, desire
        """
        gradients: dict = {
            "gate": {},
            "pair": {},
            "bridge": {},
            "seed": {},
            "path": {},
            "resonance": {},
            "desire": {},
        }

        # 1. Bridge gradients from cross-observer disagreement
        for signal in observation.cross_signals:
            key = signal.bridge_key
            # High disagreement → increase bridge weight (encourage communication)
            gradients["bridge"][key] = signal.gradient_signal * 0.1

        # 2. Path weight gradients from element imbalance
        contribs = observation.element_contributions
        if contribs:
            mean_contrib = sum(contribs.values()) / 4.0
            for face, val in contribs.items():
                # Push underrepresented elements up, overrepresented down
                gradients["path"][face] = (mean_contrib - val) * 0.05

        # 3. Pair weight gradients from per-observer disagreement
        # For each doc that appears in multiple observers' top-10,
        # compute gradient based on score variance across observers
        doc_scores_per_observer: dict[str, list[float]] = defaultdict(list)
        for result in observation.observer_results:
            for i, doc_id in enumerate(result.ranked_doc_ids[:10]):
                score = result.ranked_scores[i] if i < len(result.ranked_scores) else 0.0
                doc_scores_per_observer[doc_id].append(score)

        for doc_id, scores in doc_scores_per_observer.items():
            if len(scores) > 1:
                mean_s = sum(scores) / len(scores)
                variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
                # High variance → this doc needs its pair weights adjusted
                if variance > 0.01:
                    gradients["pair"][doc_id] = -variance * 0.01  # reduce high-variance docs

        # 4. Seed gradients from compression quality across observers
        for result in observation.observer_results:
            if result.agent.element == "R":  # Fractal observers measure compression
                for dim, val in result.observation_12d.items():
                    if "compression" in dim:
                        gradients["seed"]["compression_quality"] = val * 0.02

        return gradients

    def status(self) -> str:
        """Human-readable status of the swarm."""
        lines = [
            f"Observer Swarm: {len(self.agents)} agents ({self.config.size} configured)",
            f"Coordination: {self.config.coordination_mode}",
            f"Nesting depth: {self.config.max_nesting_depth}",
            f"History: {len(self.angel.history)} observations",
        ]
        if self.agents:
            elem_counts = defaultdict(int)
            for a in self.agents:
                elem_counts[a.element] += 1
            counts = " | ".join(f"{e}={c}" for e, c in sorted(elem_counts.items()))
            lines.append(f"Element distribution: {counts}")
        if self.angel.history:
            last = self.angel.history[-1]
            lines.append(f"Last coherence: {last.swarm_coherence:.3f}")
            lines.append(f"Last discrimination: {last.swarm_discrimination:.3f}")
            lines.append(f"Last element balance: {last.element_balance:.3f}")
        return "\n".join(lines)


# ── Module-level singleton ──────────────────────────────────────────

_SWARM: Optional[ObserverSwarm] = None


def get_swarm(config: SwarmConfig = None) -> ObserverSwarm:
    """Get or create the singleton ObserverSwarm."""
    global _SWARM
    if _SWARM is None or config is not None:
        _SWARM = ObserverSwarm(config=config)
    return _SWARM


# ── MCP Tool Entry Points ──────────────────────────────────────────


def spawn_observer_swarm(
    size: int = 16,
    element_bias: float = 2.0,
) -> str:
    """Spawn a crystal-parallel observer swarm.

    Creates N observer agents (4/16/64/256), each assigned an element (S/F/C/R),
    wreath (Su/Me/Sa), archetype role (1-12), and liminal coordinate (1-60).
    Agents are spawned with desire-gradient-weighted positioning.

    Args:
        size: Number of observers (4, 16, 64, or 256)
        element_bias: How much to upweight each observer's assigned element path (default 2.0)
    """
    from .perpetual_agency import _compute_desire_gradient

    config = SwarmConfig(size=size, element_bias=element_bias)
    swarm = get_swarm(config)

    engine = get_engine()
    try:
        desire_gradient = _compute_desire_gradient(engine)
    except Exception:
        desire_gradient = {}

    agents = swarm.spawn(desire_gradient)

    lines = [
        f"## Observer Swarm Spawned\n",
        f"**Agents**: {len(agents)} ({len(agents) // 4} per element)",
        f"**Nesting depth**: {config.max_nesting_depth}",
        f"**Element bias**: {element_bias}x",
        "",
        "### Agent Distribution\n",
    ]

    # Group by element
    by_element: dict[str, list] = {"S": [], "F": [], "C": [], "R": []}
    for a in agents:
        by_element[a.element].append(a)

    for elem in "SFCR":
        group = by_element[elem]
        lines.append(f"**{LENS_CODES[elem]}** ({len(group)} agents):")
        for a in group[:4]:
            lines.append(f"  - {a.describe()}")
        if len(group) > 4:
            lines.append(f"  ... and {len(group) - 4} more")
        lines.append("")

    return "\n".join(lines)


def run_swarm_observation(
    query: str = "seed kernel crystal",
    swarm_size: int = 16,
    max_results: int = 10,
) -> str:
    """Run a crystal-parallel swarm observation on a query.

    Each observer runs an element-biased forward pass, then results are
    aggregated via the Angel coordination protocol. Returns consensus
    ranking, cross-observer signals, and element balance.

    Args:
        query: The query to observe
        swarm_size: Number of observers (4/16/64/256)
        max_results: Maximum ranked results to return
    """
    config = SwarmConfig(size=swarm_size)
    swarm = get_swarm(config)

    if not swarm.agents:
        swarm.spawn()

    observation = swarm.run_parallel(query, max_results=max_results)

    lines = [
        f"## Swarm Observation\n",
        f"**Query**: {query[:80]}",
        f"**Observers**: {observation.observer_count}",
        f"**Coherence**: {observation.swarm_coherence:.3f}",
        f"**Discrimination**: {observation.swarm_discrimination:.4f}",
        f"**Element Balance**: {observation.element_balance:.3f}",
        f"**Elapsed**: {observation.total_elapsed_ms:.0f}ms",
        "",
    ]

    # Element contributions
    lines.append("### Element Contributions\n")
    for elem in "SFCR":
        val = observation.element_contributions.get(elem, 0.0)
        bar = "=" * int(val * 40)
        lines.append(f"  {elem} ({LENS_CODES[elem]:7s}): {bar} {val:.3f}")

    # Consensus ranking
    lines.append("\n### Consensus Ranking\n")
    for i, doc_id in enumerate(observation.consensus_ranking[:max_results]):
        score = observation.consensus_scores.get(doc_id, 0.0)
        lines.append(f"  {i+1}. {doc_id} (score={score:.4f})")

    # Cross-observer signals
    if observation.cross_signals:
        lines.append("\n### Cross-Observer Signals\n")
        lines.append("| Bridge | Agreement | Disagreement | Score Delta | Top Match |")
        lines.append("|--------|-----------|--------------|-------------|-----------|")
        for sig in observation.cross_signals:
            match = "Yes" if sig.top_doc_match else "No"
            lines.append(
                f"| {sig.bridge_key} | {sig.agreement:.3f} | "
                f"{sig.disagreement:.3f} | {sig.score_delta:.4f} | {match} |"
            )

    # Aggregated 12D
    if observation.aggregated_12d:
        lines.append("\n### Aggregated 12D Observation\n")
        for dim, val in sorted(observation.aggregated_12d.items()):
            bar = "=" * int(val * 30)
            lines.append(f"  {dim:20s}: {bar} {val:.3f}")

    return "\n".join(lines)


def query_swarm_status() -> str:
    """Query the current observer swarm status.

    Shows: agent count, element distribution, last observation coherence,
    history depth, and Angel coordinator state.
    """
    swarm = get_swarm()
    return swarm.status()
