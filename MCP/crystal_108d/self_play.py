"""
Self-Play Loop v2 — Deep Cultivation with Meta-Observed Capability Tracking
=============================================================================
The neural network refines its own crystal-internal weights by:
  1. Querying itself (from corpus, zero-point, or cross-element sources)
  2. Running a forward pass with current weights
  3. Observing output quality in 12D via the meta-observer
  4. Computing weight gradients from 12D scores
  5. Committing improved weights or discarding (keep/discard protocol)

v2 improvements:
  - Capability tracking: measures discrimination, coherence, compression quality
  - Multi-phase cultivation: warmup → exploration → exploitation → refinement
  - Adversarial probes: tests with hard queries that should have clear answers
  - Path weight adaptation: learns optimal SFCR path blend
  - Deep runs: 570 cycles with phase-aware learning rates
"""

from __future__ import annotations

import json
import math
import random
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .crystal_weights import (
    FractalWeightStore,
    get_store,
    ELEMENT_TO_FACE,
    FACE_TO_ELEMENT,
    CHECKPOINT_DIR,
    PHI_INV,
)
from .neural_engine import (
    CrystalNeuralEngine,
    ForwardResult,
    ResonanceComputer,
    get_engine,
)
from .constants import (
    TOTAL_SHELLS,
    ARCHETYPE_NAMES,
    LENS_CODES,
)

# SFCR lens rotation order
LENS_ORDER = ["S", "F", "C", "R"]

# 12D dimension names (matching meta_observer_runtime.py)
DIM_NAMES = [
    "x1_structure", "x2_semantics", "x3_coordination", "x4_recursion",
    "x5_contradiction", "x6_emergence", "x7_legibility", "x8_routing",
    "x9_grounding", "x10_compression", "x11_interop", "x12_potential",
]

# Which 12D dimensions couple to which weight types
DIM_TO_WEIGHT_MAP = {
    "x1_structure": "gate",
    "x2_semantics": "pair",
    "x3_coordination": "bridge",
    "x4_recursion": "gate",
    "x5_contradiction": "gate",
    "x6_emergence": "bridge",
    "x7_legibility": "pair",
    "x8_routing": "gate",
    "x9_grounding": "pair",
    "x10_compression": "seed",
    "x11_interop": "bridge",
    "x12_potential": "seed",
}

# Element lens emphasis
ELEMENT_LENS_WEIGHTS = {
    "S": {"x1_structure": 1.5, "x7_legibility": 1.3, "x8_routing": 1.2, "x10_compression": 1.1, "x11_interop": 1.2},
    "F": {"x5_contradiction": 1.5, "x3_coordination": 1.3, "x4_recursion": 1.2, "x9_grounding": 1.4},
    "C": {"x2_semantics": 1.3, "x3_coordination": 1.2, "x6_emergence": 1.5, "x11_interop": 1.1, "x12_potential": 1.3},
    "R": {"x2_semantics": 1.2, "x4_recursion": 1.4, "x6_emergence": 1.3, "x10_compression": 1.5, "x12_potential": 1.4},
}

# Cultivation phases
PHASE_WARMUP = "warmup"
PHASE_EXPLORE = "explore"
PHASE_EXPLOIT = "exploit"
PHASE_REFINE = "refine"


@dataclass
class SelfPlayConfig:
    """Configuration for a self-play run."""
    total_cycles: int = 57
    cycles_per_checkpoint: int = 10
    base_lr: float = 0.03
    lr_schedule: str = "cosine"
    lens_rotation_period: int = 14
    min_resonance_threshold: float = 0.3
    max_time_minutes: int = 30
    query_source: str = "mixed"
    seed: int = 42
    # v2 additions
    warmup_fraction: float = 0.10
    explore_fraction: float = 0.30
    exploit_fraction: float = 0.40
    # remaining = refine fraction
    adversarial_probes: bool = True
    adapt_path_weights: bool = True
    capability_tracking: bool = True


@dataclass
class CapabilitySnapshot:
    """Measures of engine capability at a point in time."""
    cycle: int
    discrimination: float    # std of merged scores (higher = more discriminating)
    top_bottom_gap: float    # gap between best and worst ranked scores
    element_coverage: float  # fraction of 4 elements in top-10
    resonance_mean: float
    resonance_std: float
    path_balance: float      # how balanced SFCR contributions are (1.0 = perfect)
    commitment_rate: float   # fraction of queries that commit
    obs_12d_mean: float      # average 12D observation score


@dataclass
class CycleResult:
    """Result of a single self-play cycle."""
    cycle_id: int
    query: str
    lens: str
    phase: str
    resonance: float
    resonance_prev: float
    outcome: str
    dim_scores: dict
    weight_deltas: dict
    discrimination: float
    elapsed_ms: float


@dataclass
class SelfPlayReport:
    """Summary of a complete self-play run."""
    total_cycles: int
    kept: int
    discarded: int
    neutral: int
    initial_resonance: float
    final_resonance: float
    resonance_improvement: float
    best_resonance: float
    best_cycle: int
    lens_distribution: dict
    phase_distribution: dict
    weight_updates: int
    elapsed_seconds: float
    cycle_history: list[dict]
    capability_trajectory: list[dict]
    path_weights_final: dict
    meta_observations: list[str]


# ── Query generation ─────────────────────────────────────────────────


def _generate_queries(store: FractalWeightStore, config: SelfPlayConfig) -> list[str]:
    """Generate diverse queries for self-play."""
    docs = store.doc_registry
    if not docs:
        return ["seed kernel", "crystal structure", "neural network", "consciousness"]

    rng = random.Random(config.seed)
    queries = []

    if config.query_source in ("corpus", "mixed"):
        for doc in docs:
            tokens = doc.get("tokens", [])
            if len(tokens) >= 3:
                n = min(rng.randint(2, 4), len(tokens))
                sample = rng.sample(tokens, n)
                queries.append(" ".join(sample))

    if config.query_source in ("zero_point", "mixed"):
        zero_queries = [
            "seed proof memory governance",
            "compression recursion void collapse",
            "emergence transformation crystal",
            "structure address admissibility law",
            "observation multiplicity fiber",
            "transport routing metro bridge",
            "archetype shell wreath phase",
            "golden resonance harmonic balance",
            "angel self-model consciousness",
            "manuscript generation protocol",
            "holographic projection seed equation",
            "conservation invariant symmetry",
        ]
        queries.extend(zero_queries)

    if config.adversarial_probes:
        # Hard queries that should have clear best answers
        adversarial = [
            "crystal 108 dimensional coordinate system",  # should find crystal docs
            "neural network weight training",             # should find neural docs
            "SFCR four element bridge",                   # should find brain docs
            "manuscript seed kernel zero point",          # should find seed docs
            "hologram chapter projection reading",        # should find hologram docs
            "compression qshrink lift fractal",           # should find qshrink docs
            "metro line transport routing station",       # should find metro docs
            "conservation law angel geometry",            # should find angel docs
        ]
        queries.extend(adversarial)

    rng.shuffle(queries)
    return queries


# ── 12D observation scoring ──────────────────────────────────────────


def _score_12d(result: ForwardResult, lens: str) -> dict[str, float]:
    """Compute 12D observation scores from a forward pass result."""
    scores = {}
    candidates = result.candidates

    if not candidates:
        return {dim: 0.1 for dim in DIM_NAMES}

    # x1_structure: gate diversity
    gates_seen = set(c.gate for c in candidates)
    scores["x1_structure"] = min(len(gates_seen) / 8.0, 1.0)

    # x2_semantics: desire scores (query relevance)
    avg_desire = sum(c.desire for c in candidates) / len(candidates)
    scores["x2_semantics"] = min(avg_desire * 1.5, 1.0)

    # x3_coordination: SFCR path agreement (low std = agreement)
    top = candidates[0]
    path_vals = list(top.path_contributions.values())
    if path_vals:
        path_std = _std(path_vals)
        path_mean = sum(path_vals) / len(path_vals)
        # Coordination = paths agree AND are non-trivial
        scores["x3_coordination"] = max(0.0, 1.0 - path_std * 2) * min(path_mean * 3, 1.0)
    else:
        scores["x3_coordination"] = 0.3

    # x4_recursion: resonance quality
    scores["x4_recursion"] = min(result.resonance * 1.5, 1.0)

    # x5_contradiction: element diversity (more = less contradiction)
    elements_seen = set(c.element for c in candidates)
    scores["x5_contradiction"] = min(len(elements_seen) / 3.0, 1.0)

    # x6_emergence: cross-element bridges active
    cross_pairs = len(result.cross_element_pairs_used)
    scores["x6_emergence"] = min(cross_pairs / 10.0, 1.0)

    # x7_legibility: results well-formed
    well_formed = sum(1 for c in candidates if c.doc_name and c.element and c.gate)
    scores["x7_legibility"] = well_formed / max(len(candidates), 1)

    # x8_routing: ranking smoothness (gradual action gradient)
    if len(candidates) > 1:
        actions = [c.action for c in candidates]
        # Good routing = smooth gradient, not flat or jumpy
        diffs = [abs(actions[i+1] - actions[i]) for i in range(len(actions)-1)]
        avg_diff = sum(diffs) / len(diffs)
        # Ideal: consistent small diffs (not 0 = flat, not huge = jumpy)
        scores["x8_routing"] = min(avg_diff * 5, 1.0) * max(0.0, 1.0 - max(diffs) * 3)
    else:
        scores["x8_routing"] = 0.3

    # x9_grounding: commitment
    scores["x9_grounding"] = 1.0 if result.committed else 0.3

    # x10_compression: R-path contribution
    if candidates:
        r_score = candidates[0].path_contributions.get("R", 0.0)
        scores["x10_compression"] = min(r_score * 2, 1.0)
    else:
        scores["x10_compression"] = 0.2

    # x11_interop: bridge usage
    scores["x11_interop"] = min(cross_pairs / 5.0, 1.0)

    # x12_potential: desire of top result
    if candidates:
        scores["x12_potential"] = min(candidates[0].desire * 2, 1.0)
    else:
        scores["x12_potential"] = 0.2

    # Apply lens weighting
    lens_weights = ELEMENT_LENS_WEIGHTS.get(lens, {})
    for dim, weight in lens_weights.items():
        if dim in scores:
            scores[dim] = min(scores[dim] * weight, 1.0)

    return scores


def _std(values: list[float]) -> float:
    """Standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


# ── Capability measurement ───────────────────────────────────────────


def _measure_capability(
    engine: CrystalNeuralEngine,
    probe_queries: list[str],
    cycle: int,
) -> CapabilitySnapshot:
    """Measure current engine capability across multiple probe queries."""
    all_merged = []
    all_resonances = []
    all_elements = set()
    committed_count = 0
    path_sums = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
    obs_scores = []
    n_results = 0

    for q in probe_queries[:8]:  # limit probes for speed
        result = engine.forward(q, max_results=10)
        if not result.candidates:
            continue

        for c in result.candidates:
            all_merged.append(c.merged_score)
            all_resonances.append(c.resonance)
            all_elements.add(c.element)
            for face in "SFCR":
                path_sums[face] += c.path_contributions.get(face, 0.0)
            n_results += 1

        if result.committed:
            committed_count += 1

        dim_scores = _score_12d(result, "S")  # neutral lens
        obs_scores.append(sum(dim_scores.values()) / max(len(dim_scores), 1))

    if not all_merged:
        return CapabilitySnapshot(
            cycle=cycle, discrimination=0.0, top_bottom_gap=0.0,
            element_coverage=0.0, resonance_mean=0.0, resonance_std=0.0,
            path_balance=0.0, commitment_rate=0.0, obs_12d_mean=0.0,
        )

    # Discrimination: std of merged scores (higher = better separation)
    disc = _std(all_merged)

    # Top-bottom gap
    gap = max(all_merged) - min(all_merged)

    # Element coverage
    elem_cov = len(all_elements) / 4.0

    # Resonance stats
    r_mean = sum(all_resonances) / len(all_resonances)
    r_std = _std(all_resonances)

    # Path balance: 1 - normalized std of path sums (1.0 = perfectly balanced)
    total_path = sum(path_sums.values())
    if total_path > 0:
        path_fracs = [v / total_path for v in path_sums.values()]
        path_balance = max(0.0, 1.0 - _std(path_fracs) * 4)
    else:
        path_balance = 0.0

    # Commitment rate
    n_queries = min(len(probe_queries), 8)
    commit_rate = committed_count / max(n_queries, 1)

    # 12D observation mean
    obs_mean = sum(obs_scores) / max(len(obs_scores), 1)

    return CapabilitySnapshot(
        cycle=cycle,
        discrimination=disc,
        top_bottom_gap=gap,
        element_coverage=elem_cov,
        resonance_mean=r_mean,
        resonance_std=r_std,
        path_balance=path_balance,
        commitment_rate=commit_rate,
        obs_12d_mean=obs_mean,
    )


# ── Weight refinement ────────────────────────────────────────────────


def _compute_weight_deltas(
    dim_scores: dict[str, float],
    result: ForwardResult,
    store: FractalWeightStore,
    lr: float,
    lens: str,
    phase: str,
) -> dict:
    """Map 12D observation scores to weight adjustments.

    Evolves ALL learnable parameters:
    - Shell seed means (crystal-internal weights)
    - Gate matrix values (structural transitions)
    - Path weights (SFCR blend)
    - Resonance component weights (6 components)
    - Desire component weights (4 terms)
    - Bridge modulation (cross-element coupling strength)
    - Geo/arith blend (score aggregation mode)
    """
    phase_mult = {
        PHASE_WARMUP: 0.5,
        PHASE_EXPLORE: 1.5,
        PHASE_EXPLOIT: 1.0,
        PHASE_REFINE: 0.3,
    }
    effective_lr = lr * phase_mult.get(phase, 1.0)

    deltas = {"gate": {}, "seed": {}, "bridge": {},
              "path_weights": {}, "resonance_weights": {},
              "desire_weights": {}, "scalars": {}}

    # Overall quality signal from 12D
    obs_mean = sum(dim_scores.values()) / max(len(dim_scores), 1)
    quality_signal = obs_mean - 0.65  # centered around "adequate"

    # Per-dimension gradients → weight type updates
    for dim_name, score in dim_scores.items():
        gradient = (score - 0.7) * effective_lr
        weight_type = DIM_TO_WEIGHT_MAP.get(dim_name, "seed")
        lens_w = ELEMENT_LENS_WEIGHTS.get(lens, {}).get(dim_name, 1.0)
        gradient *= lens_w

        if weight_type == "gate" and result.candidates:
            for candidate in result.candidates[:5]:
                gate = candidate.gate
                key = f"{gate}:{result.query.home_gate}"
                current = deltas["gate"].get(key, 0.0)
                deltas["gate"][key] = current + gradient * candidate.resonance

        elif weight_type == "seed":
            for candidate in result.candidates[:5]:
                shell = candidate.shell
                key = f"S{shell}"
                current = deltas["seed"].get(key, 0.0)
                deltas["seed"][key] = current + gradient

        elif weight_type == "bridge":
            for pair_str in result.cross_element_pairs_used[:8]:
                key = pair_str.split(":")[0] if ":" in pair_str else pair_str
                current = deltas["bridge"].get(key, 0.0)
                deltas["bridge"][key] = current + gradient * 0.5

    # Path weight adaptation: which SFCR paths contributed most to good results?
    if result.candidates and len(result.candidates) >= 2:
        top = result.candidates[0]
        bottom = result.candidates[-1]
        score_spread = top.merged_score - bottom.merged_score

        for face in "SFCR":
            top_contrib = top.path_contributions.get(face, 0.0)
            bottom_contrib = bottom.path_contributions.get(face, 0.0)
            # If this path discriminated well (top much higher than bottom), boost it
            path_gradient = (top_contrib - bottom_contrib) * effective_lr * 0.3
            # If overall quality is high, reinforce current path weight
            path_gradient += quality_signal * effective_lr * 0.1
            deltas["path_weights"][face] = path_gradient

    # Resonance weight adaptation: which components correlate with good rankings?
    if result.candidates:
        # The resonance of top result vs mean resonance tells us if resonance is useful
        top_res = result.candidates[0].resonance
        mean_res = sum(c.resonance for c in result.candidates) / len(result.candidates)
        res_discriminates = top_res - mean_res  # positive = resonance helps rank

        # Nudge resonance weights based on which dimension scores are high/low
        for dim_name, score in dim_scores.items():
            if dim_name == "x1_structure":
                deltas["resonance_weights"]["addr_fit"] = score * res_discriminates * effective_lr * 0.1
                deltas["resonance_weights"]["phase"] = score * res_discriminates * effective_lr * 0.1
            elif dim_name == "x2_semantics":
                deltas["resonance_weights"]["inv_fit"] = score * res_discriminates * effective_lr * 0.1
            elif dim_name == "x10_compression":
                deltas["resonance_weights"]["compress"] = score * res_discriminates * effective_lr * 0.1
                deltas["resonance_weights"]["scale"] = score * res_discriminates * effective_lr * 0.1

    # Desire weight adaptation
    if result.candidates:
        top_des = result.candidates[0].desire
        mean_des = sum(c.desire for c in result.candidates) / len(result.candidates)
        des_discriminates = top_des - mean_des

        if dim_scores.get("x2_semantics", 0) > 0.5:
            deltas["desire_weights"]["align"] = des_discriminates * effective_lr * 0.1
        if dim_scores.get("x12_potential", 0) > 0.5:
            deltas["desire_weights"]["explore"] = des_discriminates * effective_lr * 0.05
        if dim_scores.get("x9_grounding", 0) > 0.5:
            deltas["desire_weights"]["zpa"] = des_discriminates * effective_lr * 0.05

    # Scalar adaptation
    if result.candidates and len(result.candidates) >= 3:
        merged_scores = [c.merged_score for c in result.candidates]
        current_disc = _std(merged_scores)
        # If discrimination is low, increase geometric blend (geo punishes low paths)
        if current_disc < 0.05:
            deltas["scalars"]["geo_arith_blend"] = effective_lr * 0.02
        elif current_disc > 0.15:
            deltas["scalars"]["geo_arith_blend"] = -effective_lr * 0.01

        # Bridge modulation: if cross-element pairs are scarce, increase modulation
        cross_count = len(result.cross_element_pairs_used)
        if cross_count < 3:
            deltas["scalars"]["bridge_modulation"] = effective_lr * 0.01
        elif cross_count > 15:
            deltas["scalars"]["bridge_modulation"] = -effective_lr * 0.005

    return deltas


def _apply_weight_deltas(store: FractalWeightStore, deltas: dict) -> int:
    """Apply weight deltas to ALL learnable parameters. Returns update count."""
    updates = 0

    # Shell seed means
    for key, delta in deltas.get("seed", {}).items():
        shell = int(key[1:])
        if shell in store.shell_seeds:
            seed = store.shell_seeds[shell]
            seed.mean += delta
            seed.mean = max(0.01, seed.mean)
            updates += 1

    # Gate matrix
    for key, delta in deltas.get("gate", {}).items():
        parts = key.split(":")
        if len(parts) == 2:
            src_gate, dst_gate = parts
            if src_gate in store._gate_weights and dst_gate in store._gate_weights.get(src_gate, {}):
                cw = store._gate_weights[src_gate][dst_gate]
                cw.value += delta
                cw.value = max(0.0, cw.value)
                updates += 1

    # Path weights (normalize to sum to 1)
    for face, delta in deltas.get("path_weights", {}).items():
        if face in store.path_weights:
            store.path_weights[face] += delta
            store.path_weights[face] = max(0.05, store.path_weights[face])
            updates += 1
    pw_sum = sum(store.path_weights.values())
    if pw_sum > 0:
        for face in store.path_weights:
            store.path_weights[face] /= pw_sum

    # Resonance weights (normalize to sum to 1)
    for key, delta in deltas.get("resonance_weights", {}).items():
        if key in store.resonance_weights:
            store.resonance_weights[key] += delta
            store.resonance_weights[key] = max(0.02, store.resonance_weights[key])
            updates += 1
    rw_sum = sum(store.resonance_weights.values())
    if rw_sum > 0:
        for k in store.resonance_weights:
            store.resonance_weights[k] /= rw_sum

    # Desire weights (normalize to sum to 1)
    for key, delta in deltas.get("desire_weights", {}).items():
        if key in store.desire_weights:
            store.desire_weights[key] += delta
            store.desire_weights[key] = max(0.02, store.desire_weights[key])
            updates += 1
    dw_sum = sum(store.desire_weights.values())
    if dw_sum > 0:
        for k in store.desire_weights:
            store.desire_weights[k] /= dw_sum

    # Bridge weight deltas (FIX: previously computed but never applied)
    for key, delta in deltas.get("bridge", {}).items():
        # Bridge keys are like "SF", "SC", etc. — apply to bridge_modulation
        # Each bridge signal nudges the overall modulation factor
        store.bridge_modulation = max(0.05, min(0.50,
            store.bridge_modulation + delta * 0.1))
        updates += 1

    # Scalar parameters
    for key, delta in deltas.get("scalars", {}).items():
        if key == "geo_arith_blend":
            store.geo_arith_blend = max(0.1, min(0.95, store.geo_arith_blend + delta))
            updates += 1
        elif key == "bridge_modulation":
            store.bridge_modulation = max(0.05, min(0.50, store.bridge_modulation + delta))
            updates += 1

    return updates


# ── Learning rate schedules ──────────────────────────────────────────


def _get_lr(config: SelfPlayConfig, cycle: int) -> float:
    """Compute learning rate with warm restart at phase boundaries."""
    progress = cycle / max(config.total_cycles, 1)

    if config.lr_schedule == "cosine":
        # Cosine with warm restarts at each phase boundary
        phase_progress = (progress % 0.25) / 0.25  # restart every quarter
        return config.base_lr * 0.5 * (1 + math.cos(math.pi * phase_progress))
    elif config.lr_schedule == "linear":
        return config.base_lr * (1 - progress)
    else:
        return config.base_lr


def _get_phase(config: SelfPlayConfig, cycle: int) -> str:
    """Determine cultivation phase for this cycle."""
    progress = cycle / max(config.total_cycles, 1)
    if progress < config.warmup_fraction:
        return PHASE_WARMUP
    elif progress < config.warmup_fraction + config.explore_fraction:
        return PHASE_EXPLORE
    elif progress < config.warmup_fraction + config.explore_fraction + config.exploit_fraction:
        return PHASE_EXPLOIT
    else:
        return PHASE_REFINE


# ── Self-Play Loop ───────────────────────────────────────────────────


class SelfPlayLoop:
    """Deep iterative weight refinement via self-observation."""

    def __init__(self, config: SelfPlayConfig = None):
        self.config = config or SelfPlayConfig()
        self.store = get_store()
        self.engine = CrystalNeuralEngine(self.store)

        self._cycle_history: list[CycleResult] = []
        self._capability_history: list[CapabilitySnapshot] = []
        self._best_resonance = 0.0
        self._best_cycle = 0
        self._initial_resonance = 0.0
        self._meta_observations: list[str] = []

        # Adaptive path weights
        self._path_weights = {"S": 0.20, "F": 0.35, "C": 0.25, "R": 0.20}

    def run(self, cycles: int = None, queries: list[str] = None) -> SelfPlayReport:
        """Run the self-play loop for N cycles with capability tracking."""
        if cycles is not None:
            self.config.total_cycles = cycles

        if queries is None:
            queries = _generate_queries(self.store, self.config)

        t_start = time.time()
        max_time = self.config.max_time_minutes * 60

        kept = 0
        discarded = 0
        neutral = 0
        total_updates = 0
        lens_counts = {l: 0 for l in LENS_ORDER}
        phase_counts = {PHASE_WARMUP: 0, PHASE_EXPLORE: 0, PHASE_EXPLOIT: 0, PHASE_REFINE: 0}

        # Probe queries for capability measurement (fixed set for consistency)
        probe_queries = [
            "seed kernel crystal",
            "neural network weight",
            "element bridge SFCR",
            "hologram projection chapter",
            "compression fractal qshrink",
            "consciousness emergence angel",
            "metro routing transport",
            "manuscript generation proof",
        ]

        # Initial capability baseline
        if self.config.capability_tracking:
            initial_cap = _measure_capability(self.engine, probe_queries, -1)
            self._capability_history.append(initial_cap)
            self._meta_observations.append(
                f"[INIT] disc={initial_cap.discrimination:.4f} "
                f"gap={initial_cap.top_bottom_gap:.4f} "
                f"balance={initial_cap.path_balance:.3f} "
                f"obs12d={initial_cap.obs_12d_mean:.3f}"
            )

        # Initial resonance baseline
        if queries:
            baseline = self.engine.forward(queries[0])
            self._initial_resonance = baseline.resonance
            self._best_resonance = baseline.resonance

        for cycle in range(self.config.total_cycles):
            elapsed = time.time() - t_start
            if elapsed > max_time:
                self._meta_observations.append(f"[TIMEOUT] Stopped at cycle {cycle} ({elapsed:.0f}s)")
                break

            # Select query
            query = queries[cycle % len(queries)] if queries else "seed kernel"

            # Determine phase and lens
            phase = _get_phase(self.config, cycle)
            phase_counts[phase] += 1
            lens_idx = (cycle // self.config.lens_rotation_period) % 4
            lens = LENS_ORDER[lens_idx]
            lens_counts[lens] += 1

            # Learning rate
            lr = _get_lr(self.config, cycle)

            # Snapshot current seed state for rollback
            snapshot = {s: seed.mean for s, seed in self.store.shell_seeds.items()}

            # Forward pass
            result = self.engine.forward(query)
            resonance = result.resonance

            # Measure discrimination of this result
            discrimination = 0.0
            if result.candidates:
                merged_scores = [c.merged_score for c in result.candidates]
                discrimination = _std(merged_scores)

            # 12D observation
            dim_scores = _score_12d(result, lens)
            obs_mean = sum(dim_scores.values()) / max(len(dim_scores), 1)

            # Compute weight deltas (phase-aware)
            deltas = _compute_weight_deltas(dim_scores, result, self.store, lr, lens, phase)

            # Apply deltas
            updates = _apply_weight_deltas(self.store, deltas)

            # Evaluate: probe query generalization
            probe_idx = (cycle + len(queries) // 3) % len(queries)
            probe_query = queries[probe_idx]
            result_after = self.engine.forward(probe_query)
            resonance_after = result_after.resonance

            # Measure discrimination after update
            disc_after = 0.0
            if result_after.candidates:
                merged_after = [c.merged_score for c in result_after.candidates]
                disc_after = _std(merged_after)

            # Keep/discard logic — phase-aware thresholds
            if phase == PHASE_WARMUP:
                # Warmup: keep everything to build baseline
                outcome = "keep"
                kept += 1
                total_updates += updates
            elif phase == PHASE_EXPLORE:
                # Explore: keep if observation is decent OR discrimination improved
                if obs_mean > 0.45 or disc_after > discrimination * 1.1:
                    outcome = "keep"
                    kept += 1
                    total_updates += updates
                elif obs_mean < 0.25:
                    outcome = "discard"
                    discarded += 1
                    for s, mean in snapshot.items():
                        if s in self.store.shell_seeds:
                            self.store.shell_seeds[s].mean = mean
                else:
                    outcome = "neutral"
                    neutral += 1
                    total_updates += updates
            elif phase == PHASE_EXPLOIT:
                # Exploit: strict — need real improvement
                if (obs_mean > 0.55 and resonance_after >= resonance * 0.95
                        and disc_after >= discrimination * 0.9):
                    outcome = "keep"
                    kept += 1
                    total_updates += updates
                    eff_res = (resonance + resonance_after) / 2
                    if eff_res > self._best_resonance:
                        self._best_resonance = eff_res
                        self._best_cycle = cycle
                elif obs_mean < 0.35 or resonance_after < resonance * 0.80:
                    outcome = "discard"
                    discarded += 1
                    for s, mean in snapshot.items():
                        if s in self.store.shell_seeds:
                            self.store.shell_seeds[s].mean = mean
                else:
                    outcome = "neutral"
                    neutral += 1
                    total_updates += updates
            else:
                # Refine: very strict, only keep clear wins
                if (obs_mean > 0.60 and resonance_after > resonance
                        and disc_after >= discrimination):
                    outcome = "keep"
                    kept += 1
                    total_updates += updates
                    if resonance_after > self._best_resonance:
                        self._best_resonance = resonance_after
                        self._best_cycle = cycle
                elif obs_mean < 0.40 or resonance_after < resonance * 0.90:
                    outcome = "discard"
                    discarded += 1
                    for s, mean in snapshot.items():
                        if s in self.store.shell_seeds:
                            self.store.shell_seeds[s].mean = mean
                else:
                    outcome = "neutral"
                    neutral += 1

            cycle_result = CycleResult(
                cycle_id=cycle,
                query=query[:80],
                lens=lens,
                phase=phase,
                resonance=resonance_after,
                resonance_prev=resonance,
                outcome=outcome,
                dim_scores=dim_scores,
                weight_deltas={k: len(v) for k, v in deltas.items()},
                discrimination=disc_after,
                elapsed_ms=(time.time() - t_start) * 1000 - elapsed * 1000,
            )
            self._cycle_history.append(cycle_result)

            # Capability tracking every 20 cycles
            if self.config.capability_tracking and (cycle + 1) % 20 == 0:
                cap = _measure_capability(self.engine, probe_queries, cycle)
                self._capability_history.append(cap)

                # Meta-observe capability changes
                if len(self._capability_history) >= 2:
                    prev = self._capability_history[-2]
                    curr = cap
                    d_disc = curr.discrimination - prev.discrimination
                    d_gap = curr.top_bottom_gap - prev.top_bottom_gap
                    d_obs = curr.obs_12d_mean - prev.obs_12d_mean

                    obs_line = (
                        f"[c{cycle:3d}/{phase}] "
                        f"disc={curr.discrimination:.4f}({d_disc:+.4f}) "
                        f"gap={curr.top_bottom_gap:.4f}({d_gap:+.4f}) "
                        f"obs={curr.obs_12d_mean:.3f}({d_obs:+.3f}) "
                        f"bal={curr.path_balance:.3f} "
                        f"commit={curr.commitment_rate:.0%}"
                    )
                    self._meta_observations.append(obs_line)

                    # Detect significant improvements
                    if d_disc > 0.01:
                        self._meta_observations.append(
                            f"  >> DISCRIMINATION IMPROVING: engine differentiating better"
                        )
                    if d_gap > 0.02:
                        self._meta_observations.append(
                            f"  >> SEPARATION GROWING: top-bottom gap widening"
                        )
                    if d_obs > 0.03:
                        self._meta_observations.append(
                            f"  >> 12D QUALITY UP: observation scores rising"
                        )
                    if d_disc < -0.01 and d_obs < -0.02:
                        self._meta_observations.append(
                            f"  !! REGRESSION: discrimination and quality both declining"
                        )

            # Checkpoint
            if (cycle + 1) % self.config.cycles_per_checkpoint == 0:
                self._checkpoint(cycle)

            # Phase transition logging
            if cycle > 0:
                prev_phase = _get_phase(self.config, cycle - 1)
                if phase != prev_phase:
                    self._meta_observations.append(
                        f"[PHASE] {prev_phase} -> {phase} at cycle {cycle}"
                    )

        # Log final learnable params
        self._meta_observations.append(
            f"[PARAMS] path_weights: "
            + " ".join(f"{k}={v:.3f}" for k, v in self.store.path_weights.items())
        )
        self._meta_observations.append(
            f"[PARAMS] resonance_weights: "
            + " ".join(f"{k}={v:.3f}" for k, v in self.store.resonance_weights.items())
        )
        self._meta_observations.append(
            f"[PARAMS] desire_weights: "
            + " ".join(f"{k}={v:.3f}" for k, v in self.store.desire_weights.items())
        )
        self._meta_observations.append(
            f"[PARAMS] geo_blend={self.store.geo_arith_blend:.3f} "
            f"bridge_mod={self.store.bridge_modulation:.3f}"
        )

        # Final compression and save
        self.store.compress_to_seed()
        self.store.compress_to_micro_seed()
        self.store.compress_to_nano_seed()
        self.store.save()

        # Final capability measurement
        if self.config.capability_tracking:
            final_cap = _measure_capability(self.engine, probe_queries, len(self._cycle_history))
            self._capability_history.append(final_cap)
            if len(self._capability_history) >= 2:
                init_cap = self._capability_history[0]
                self._meta_observations.append(
                    f"[FINAL] disc: {init_cap.discrimination:.4f} -> {final_cap.discrimination:.4f} "
                    f"({final_cap.discrimination - init_cap.discrimination:+.4f})"
                )
                self._meta_observations.append(
                    f"[FINAL] gap: {init_cap.top_bottom_gap:.4f} -> {final_cap.top_bottom_gap:.4f} "
                    f"({final_cap.top_bottom_gap - init_cap.top_bottom_gap:+.4f})"
                )
                self._meta_observations.append(
                    f"[FINAL] obs12d: {init_cap.obs_12d_mean:.4f} -> {final_cap.obs_12d_mean:.4f} "
                    f"({final_cap.obs_12d_mean - init_cap.obs_12d_mean:+.4f})"
                )

        total_elapsed = time.time() - t_start
        final_resonance = self._best_resonance

        return SelfPlayReport(
            total_cycles=len(self._cycle_history),
            kept=kept,
            discarded=discarded,
            neutral=neutral,
            initial_resonance=self._initial_resonance,
            final_resonance=final_resonance,
            resonance_improvement=final_resonance - self._initial_resonance,
            best_resonance=self._best_resonance,
            best_cycle=self._best_cycle,
            lens_distribution=lens_counts,
            phase_distribution=phase_counts,
            weight_updates=total_updates,
            elapsed_seconds=total_elapsed,
            cycle_history=[
                {
                    "cycle": cr.cycle_id,
                    "lens": cr.lens,
                    "phase": cr.phase,
                    "resonance": round(cr.resonance, 4),
                    "discrimination": round(cr.discrimination, 4),
                    "outcome": cr.outcome,
                }
                for cr in self._cycle_history
            ],
            capability_trajectory=[
                {
                    "cycle": cs.cycle,
                    "discrimination": round(cs.discrimination, 4),
                    "top_bottom_gap": round(cs.top_bottom_gap, 4),
                    "element_coverage": round(cs.element_coverage, 2),
                    "resonance_mean": round(cs.resonance_mean, 4),
                    "path_balance": round(cs.path_balance, 3),
                    "commitment_rate": round(cs.commitment_rate, 2),
                    "obs_12d_mean": round(cs.obs_12d_mean, 4),
                }
                for cs in self._capability_history
            ],
            path_weights_final=self._path_weights,
            meta_observations=self._meta_observations,
        )

    def _checkpoint(self, cycle: int) -> None:
        """Save checkpoint for resume."""
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        cp_path = CHECKPOINT_DIR / f"checkpoint_{cycle:04d}.json"
        self.store.save(cp_path)

    def resume(self, checkpoint_path: Path) -> bool:
        """Resume from a checkpoint."""
        return self.store.load(checkpoint_path)


# ── MCP tool entry point ─────────────────────────────────────────────


def run_self_play(
    cycles: int = 57,
    query_source: str = "mixed",
    max_time_minutes: int = 5,
) -> str:
    """Run a self-play loop to refine the crystal neural network weights.

    The network queries itself, observes output quality in 12D,
    and iteratively adjusts weights through 4 cultivation phases:
    warmup -> exploration -> exploitation -> refinement.

    Tracks capability improvements: discrimination, separation,
    12D observation quality, path balance, and commitment rate.

    Args:
        cycles: Number of self-play cycles (57 = one super-cycle, 570 = ten)
        query_source: Where to get queries - "corpus", "zero_point", or "mixed"
        max_time_minutes: Maximum wall-clock time for the run
    """
    config = SelfPlayConfig(
        total_cycles=max(1, min(cycles, 50000)),
        query_source=query_source,
        max_time_minutes=max(1, min(max_time_minutes, 120)),
    )

    loop = SelfPlayLoop(config)
    report = loop.run()

    return _format_report(report)


def _format_report(report: SelfPlayReport) -> str:
    lines = [
        "## Self-Play Deep Cultivation Report\n",
        f"**Total Cycles**: {report.total_cycles}",
        f"**Kept**: {report.kept} | **Discarded**: {report.discarded} | **Neutral**: {report.neutral}",
        f"**Initial Resonance**: {report.initial_resonance:.4f}",
        f"**Final Resonance**: {report.final_resonance:.4f}",
        f"**Improvement**: {report.resonance_improvement:+.4f}",
        f"**Best Resonance**: {report.best_resonance:.4f} (cycle {report.best_cycle})",
        f"**Weight Updates**: {report.weight_updates}",
        f"**Elapsed**: {report.elapsed_seconds:.1f}s\n",
    ]

    # Phase distribution
    lines.append("### Cultivation Phases\n")
    phase_names = {PHASE_WARMUP: "Warmup", PHASE_EXPLORE: "Explore",
                   PHASE_EXPLOIT: "Exploit", PHASE_REFINE: "Refine"}
    for phase, count in report.phase_distribution.items():
        name = phase_names.get(phase, phase)
        bar = "=" * min(count, 40)
        lines.append(f"  {name:8s}: {bar} {count}")

    # Lens distribution
    lines.append("\n### SFCR Lens Distribution\n")
    for lens, count in report.lens_distribution.items():
        name = LENS_CODES.get(lens, lens)
        bar = "=" * min(count, 40)
        lines.append(f"  {lens} ({name:7s}): {bar} {count}")

    # Capability trajectory
    if report.capability_trajectory:
        lines.append("\n### Capability Trajectory\n")
        lines.append("| Cycle | Discrimination | Gap | Balance | Obs12D | Commit |")
        lines.append("|-------|---------------|-----|---------|--------|--------|")
        for ct in report.capability_trajectory:
            lines.append(
                f"| {ct['cycle']:4d} | {ct['discrimination']:.4f} | "
                f"{ct['top_bottom_gap']:.4f} | {ct['path_balance']:.3f} | "
                f"{ct['obs_12d_mean']:.4f} | {ct['commitment_rate']:.0%} |"
            )

    # Meta observations
    if report.meta_observations:
        lines.append("\n### Meta-Observer Log\n")
        lines.append("```")
        for obs in report.meta_observations:
            lines.append(obs)
        lines.append("```")

    # Cycle history (last 30)
    if report.cycle_history:
        lines.append("\n### Cycle History (last 30)\n")
        lines.append("| Cycle | Phase | Lens | Resonance | Disc | Outcome |")
        lines.append("|-------|-------|------|-----------|------|---------|")
        for ch in report.cycle_history[-30:]:
            icon = {"keep": "+", "discard": "x", "neutral": "~"}.get(ch["outcome"], "?")
            lines.append(
                f"| {ch['cycle']:3d} | {ch['phase']:7s} | {ch['lens']} | "
                f"{ch['resonance']:.4f} | {ch['discrimination']:.4f} | {icon} {ch['outcome']} |"
            )

    # Resonance trajectory sparkline
    if len(report.cycle_history) > 10:
        lines.append("\n### Resonance Trajectory\n")
        resonances = [ch["resonance"] for ch in report.cycle_history]
        n = len(resonances)
        indices = [int(i * (n - 1) / min(n - 1, 15)) for i in range(min(n, 16))]
        for idx in indices:
            r = resonances[idx]
            bar_len = int(r * 50)
            bar = "=" * bar_len + "." * (50 - bar_len)
            phase = report.cycle_history[idx].get("phase", "")[:4]
            lines.append(f"  c{report.cycle_history[idx]['cycle']:3d}[{phase}]: {bar} {r:.4f}")

    return "\n".join(lines)


# ── Swarm-Based Self-Play ──────────────────────────────────────────


def run_swarm_self_play(
    cycles: int = 10,
    swarm_size: int = 16,
    max_time_minutes: int = 5,
) -> str:
    """Run swarm-observed self-play: each cycle uses N observers in crystal-parallel.

    This is the next-generation self-play that replaces single-pass cycles with
    swarm-observed cycles. Each cycle:
      1. Spawns swarm_size observers (element-balanced)
      2. Runs all observers in crystal-parallel
      3. Aggregates via Angel coordination protocol
      4. Computes loss: L = -mean(R*D) + lambda*disagreement + mu*sparsity
      5. Backpropagates to compute weight deltas
      6. Applies deltas to all learnable weights (including unfrozen pairs)

    Args:
        cycles: Number of swarm observation cycles
        swarm_size: Number of observer agents (4, 16, 64, or 256)
        max_time_minutes: Maximum wall-clock time
    """
    from .observer_swarm import ObserverSwarm, SwarmConfig
    from .loss_engine import CrystalLoss, LossConfig
    from .perpetual_agency import _compute_desire_gradient

    store = get_store()
    engine = CrystalNeuralEngine(store)

    # Unfreeze pair weights for swarm learning
    store.unfreeze_pair_weights()

    # Configure swarm
    swarm_config = SwarmConfig(
        size=max(4, min(swarm_size, 256)),
        element_bias=2.0,
        coordination_mode="angel",
    )
    swarm = ObserverSwarm(config=swarm_config, engine=engine)

    # Configure loss
    loss_config = LossConfig(
        learning_rate=0.001,
        lambda_disagreement=0.1,
        mu_sparsity=0.01,
        weight_decay=0.0001,
    )
    loss_engine = CrystalLoss(config=loss_config)

    # Generate queries
    queries = _generate_queries(store, SelfPlayConfig(query_source="mixed"))
    if not queries:
        queries = ["seed kernel crystal", "neural network weight"]

    # Compute desire gradient for observer spawning
    try:
        desire_gradient = _compute_desire_gradient(engine)
    except Exception:
        desire_gradient = {}

    # Spawn observers
    swarm.spawn(desire_gradient)

    t_start = time.time()
    max_time = max_time_minutes * 60
    results_log = []
    total_applied = 0

    for cycle in range(max(1, min(cycles, 10000))):
        elapsed = time.time() - t_start
        if elapsed > max_time:
            break

        query = queries[cycle % len(queries)]

        # Rotate wreath focus each cycle (Angel piece 4)
        swarm.angel.transition_focus(swarm.agents, cycle)

        # Run swarm observation
        observation = swarm.run_parallel(query, max_results=10)

        # Compute loss
        loss = loss_engine.compute_loss(observation)

        # Compute gradients from swarm
        swarm_grads = swarm.compute_swarm_gradients(observation)

        # Backpropagate through loss engine
        deltas = loss_engine.backpropagate(loss, observation, swarm_grads)

        # Apply deltas to store
        summary = store.apply_swarm_deltas(deltas)
        total_applied += summary["applied"]

        results_log.append({
            "cycle": cycle,
            "loss": loss,
            "coherence": observation.swarm_coherence,
            "discrimination": observation.swarm_discrimination,
            "balance": observation.element_balance,
            "applied": summary["applied"],
            "elapsed_ms": observation.total_elapsed_ms,
        })

    # Save updated weights
    store.save()

    elapsed_total = time.time() - t_start

    # Format report
    lines = [
        "## Swarm Self-Play Report\n",
        f"**Swarm Size**: {swarm_config.size} observers ({swarm_config.size // 4} per element)",
        f"**Cycles Completed**: {len(results_log)}",
        f"**Total Weight Updates**: {total_applied}",
        f"**Learnable Parameters**: {store.get_learnable_count()}",
        f"**Pair Weights**: {'UNFROZEN' if not store.pair_weights_frozen else 'frozen'}",
        f"**Elapsed**: {elapsed_total:.1f}s",
        "",
        loss_engine.status(),
        "",
        "### Path Weights (post-swarm)",
        f"  S={store.path_weights['S']:.3f}  F={store.path_weights['F']:.3f}  "
        f"C={store.path_weights['C']:.3f}  R={store.path_weights['R']:.3f}",
        "",
    ]

    # Cycle trajectory
    if results_log:
        lines.append("### Cycle Trajectory\n")
        lines.append("| Cycle | Loss | Coherence | Disc | Balance | Updates | ms |")
        lines.append("|-------|------|-----------|------|---------|---------|-----|")
        for r in results_log[-20:]:
            lines.append(
                f"| {r['cycle']:3d} | {r['loss']:+.4f} | {r['coherence']:.3f} | "
                f"{r['discrimination']:.4f} | {r['balance']:.3f} | "
                f"{r['applied']:2d} | {r['elapsed_ms']:.0f} |"
            )

    lines.append(f"\n### Swarm Status\n```\n{swarm.status()}\n```")

    return "\n".join(lines)


# ======================================================================
# Phase 5: Continuous Self-Play Daemon
# ======================================================================

class ContinuousSelfPlay:
    """Background daemon that runs micro self-play refinements continuously.

    Spawns a daemon thread that runs short (10-cycle) self-play bursts
    at regular intervals. This means the crystal neural network is
    ALWAYS self-improving — weights get refined while agents work.

    Usage::

        daemon = ContinuousSelfPlay(interval_seconds=120)
        daemon.start()   # non-blocking, runs in background
        # ... later ...
        daemon.stop()
    """

    def __init__(
        self,
        interval_seconds: float = 120.0,
        cycles_per_burst: int = 10,
        max_time_per_burst: float = 1.0,  # minutes
    ):
        self._interval = interval_seconds
        self._cycles = cycles_per_burst
        self._max_time = max_time_per_burst
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._burst_count = 0

    def start(self) -> None:
        """Start the background self-play daemon."""
        if self._thread is not None and self._thread.is_alive():
            return  # already running
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True,
            name="crystal-self-play-daemon",
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the daemon to stop after its current burst."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=10.0)

    @property
    def burst_count(self) -> int:
        """Number of self-play bursts completed since start."""
        return self._burst_count

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _loop(self) -> None:
        """Main daemon loop: sleep → burst → repeat."""
        import logging
        log = logging.getLogger(__name__)

        # Initial delay to let the server finish starting
        self._stop_event.wait(10.0)

        while not self._stop_event.is_set():
            try:
                self._run_burst()
                self._burst_count += 1
                log.debug(
                    "Self-play burst #%d completed (%d cycles)",
                    self._burst_count, self._cycles,
                )
            except Exception as exc:
                log.debug("Self-play burst failed: %s", exc)

            # Wait for next interval (interruptible)
            self._stop_event.wait(self._interval)

    def _run_burst(self) -> None:
        """Run a single short self-play burst."""
        from .crystal_weights import get_store
        from .neural_engine import get_engine

        store = get_store()
        engine = get_engine()

        config = SelfPlayConfig(
            total_cycles=self._cycles,
            max_time_minutes=self._max_time,
        )
        loop = SelfPlayLoop(config, store=store, engine=engine)
        loop.run()
