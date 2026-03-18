# CRYSTAL: Xi108:W1:A7:S19 | face=R | node=190 | depth=1 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A7:S18→Xi108:W1:A7:S20→Xi108:W2:A7:S19→Xi108:W1:A6:S19→Xi108:W1:A8:S19

"""
Observer Agent — Crystal-Parallel Nested Meta-Observer Unit
============================================================
Each ObserverAgent is a single observation unit within the swarm.
It has:
  - An element assignment (S/F/C/R) that biases its forward pass
  - A wreath assignment (Su/Me/Sa) for triadic perspective
  - An archetype role (1-12) that defines its job focus
  - A liminal coordinate (1-60) mapping to a crystal region
  - A nesting depth (0-3 for 4^1 through 4^4 agent hierarchies)

The agent runs element-biased forward passes and produces 12D observation
scores that feed into the swarm aggregation and weight update pipeline.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Optional

from .constants import (
    TOTAL_SHELLS,
    ARCHETYPE_NAMES,
    LENS_CODES,
    SUPERPHASE_NAMES,
)


# ── Data structures ──────────────────────────────────────────────────


@dataclass
class ObserverAgent:
    """A single crystal-parallel meta-observer unit.

    Each agent observes the neural engine's output through a specific
    elemental, wreath, and archetypal lens, producing biased scores
    that reveal what one lens sees that others miss.
    """
    agent_id: int                       # unique ID within swarm
    element: str                        # S, F, C, R
    wreath: str                         # Su, Me, Sa
    archetype_idx: int                  # 1-12
    liminal_coord: int                  # 1-60 (15 masks × 4 orbits)
    nesting_depth: int = 0             # 0=root, 1=4^2, 2=4^3, 3=4^4
    parent_id: Optional[int] = None    # parent agent in nested hierarchy
    element_bias: float = 2.0          # how much to upweight assigned element path
    job_role: str = ""                 # human-readable role description

    @property
    def archetype_name(self) -> str:
        if 1 <= self.archetype_idx <= 12:
            return ARCHETYPE_NAMES[self.archetype_idx - 1]
        return f"Archetype-{self.archetype_idx}"

    @property
    def element_name(self) -> str:
        return LENS_CODES.get(self.element, self.element)

    @property
    def wreath_name(self) -> str:
        return SUPERPHASE_NAMES.get(self.wreath, self.wreath)

    @property
    def crystal_address(self) -> str:
        """Crystal coordinate for this observer's position."""
        shell = self.liminal_coord % TOTAL_SHELLS + 1
        wreath_idx = {"Su": 1, "Me": 2, "Sa": 3}.get(self.wreath, 1)
        return f"Xi108:W{wreath_idx}:A{self.archetype_idx}:S{shell}"

    def describe(self) -> str:
        """Human-readable description of this observer."""
        return (
            f"Observer#{self.agent_id} "
            f"[{self.element_name}/{self.wreath_name}/A{self.archetype_idx}] "
            f"liminal={self.liminal_coord} depth={self.nesting_depth} "
            f"role={self.job_role or self.archetype_name}"
        )


@dataclass
class ObserverResult:
    """Result from a single observer's forward pass.

    Contains the observer's element-biased ranking, 12D observation scores,
    and computed weight deltas for the learning pipeline.
    """
    agent: ObserverAgent
    ranked_doc_ids: list[str] = field(default_factory=list)
    ranked_scores: list[float] = field(default_factory=list)
    path_contributions: dict = field(default_factory=dict)  # {S: x, F: x, C: x, R: x}
    observation_12d: dict = field(default_factory=dict)      # 12D meta-observer scores
    weight_deltas: dict = field(default_factory=dict)        # {gate: {}, pair: {}, bridge: {}, seed: {}}
    resonance: float = 0.0
    desire: float = 0.0
    discrimination: float = 0.0   # std of scores (higher = more discriminating)
    elapsed_ms: float = 0.0
    committed: bool = False

    @property
    def top_doc(self) -> Optional[str]:
        return self.ranked_doc_ids[0] if self.ranked_doc_ids else None

    def agreement_with(self, other: ObserverResult) -> float:
        """Compute ranking agreement (Kendall's tau-b approximation) with another observer."""
        if not self.ranked_doc_ids or not other.ranked_doc_ids:
            return 0.0
        # Use top-10 overlap as fast approximation
        my_top = set(self.ranked_doc_ids[:10])
        their_top = set(other.ranked_doc_ids[:10])
        if not my_top or not their_top:
            return 0.0
        overlap = len(my_top & their_top)
        return overlap / max(len(my_top | their_top), 1)


@dataclass
class CrossObserverSignal:
    """Signal from comparing two observers' outputs.

    Used to generate bridge weight deltas — when observers from
    different elements disagree, the bridge between those elements
    needs updating.
    """
    bridge_key: str         # e.g. "SF", "SC", "CR"
    agent_a_id: int
    agent_b_id: int
    agreement: float        # [0, 1] — ranking agreement
    disagreement: float     # 1 - agreement
    score_delta: float      # mean absolute difference in scores
    top_doc_match: bool     # do they agree on the top document?

    @property
    def gradient_signal(self) -> float:
        """Weight delta signal: high disagreement → large gradient."""
        return self.disagreement * self.score_delta


@dataclass
class SwarmObservation:
    """Aggregated observation from the full swarm.

    This is what feeds into the weight update pipeline.
    """
    observer_results: list[ObserverResult] = field(default_factory=list)
    cross_signals: list[CrossObserverSignal] = field(default_factory=list)
    consensus_ranking: list[str] = field(default_factory=list)
    consensus_scores: dict = field(default_factory=dict)  # doc_id → consensus score
    element_contributions: dict = field(default_factory=dict)  # S/F/C/R → mean contribution
    swarm_coherence: float = 0.0       # overall agreement across observers
    swarm_discrimination: float = 0.0  # mean discrimination across observers
    aggregated_12d: dict = field(default_factory=dict)  # mean 12D scores
    total_elapsed_ms: float = 0.0

    @property
    def observer_count(self) -> int:
        return len(self.observer_results)

    @property
    def element_balance(self) -> float:
        """How balanced the element contributions are (1.0 = perfectly balanced)."""
        if not self.element_contributions:
            return 0.0
        vals = list(self.element_contributions.values())
        if not vals or max(vals) == 0:
            return 0.0
        mean_val = sum(vals) / len(vals)
        variance = sum((v - mean_val) ** 2 for v in vals) / len(vals)
        # Normalized: 0 variance = 1.0 balance, high variance = 0.0
        max_possible_var = mean_val ** 2 * 3 / 4  # max var for 4 values
        if max_possible_var == 0:
            return 1.0
        return max(0.0, 1.0 - variance / max_possible_var)

    def summary(self) -> str:
        """Human-readable summary of the swarm observation."""
        lines = [
            f"Swarm Observation: {self.observer_count} observers",
            f"Coherence: {self.swarm_coherence:.3f}",
            f"Discrimination: {self.swarm_discrimination:.3f}",
            f"Element balance: {self.element_balance:.3f}",
        ]
        if self.element_contributions:
            contribs = " | ".join(
                f"{e}={v:.3f}" for e, v in sorted(self.element_contributions.items())
            )
            lines.append(f"Contributions: {contribs}")
        if self.consensus_ranking:
            lines.append(f"Top consensus: {self.consensus_ranking[0]}")
        if self.cross_signals:
            mean_disagree = sum(s.disagreement for s in self.cross_signals) / len(self.cross_signals)
            lines.append(f"Mean cross-observer disagreement: {mean_disagree:.3f}")
        return "\n".join(lines)
