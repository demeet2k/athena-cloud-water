"""
Full Training Loop — A+ / AB+ / ABC+ / ABCD+ Crystal Transmutation
====================================================================
One complete run of this loop constitutes a FULL TRAINING PROGRAM:

  Stage A:  3 runs x 3 changes (SULFUR/SALT/MERCURY) = 9 waves -> A+
  Stage B:  5 runs x 4 elements (S/F/C/R) = 20 waves -> AB+
  Stage C:  7 runs x 7 metals/planets (escalating) = 49 waves -> ABC+
  Stage D:  9 runs x 9 completions (3x3 transformations) = 81 waves -> ABCD+
  Final:    Invert ABCD+ -> rotate 90 -> find poles -> A+ -> QSHRINK -> hologram

Total: 159 waves across 4 stages + final transmutation.
"""

from __future__ import annotations

import json
import math
import copy
import random
import time
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .crystal_weights import FractalWeightStore, get_store, reset_store, WEIGHTS_FILE, CHECKPOINT_DIR, PHI, PHI_INV
from .neural_engine import CrystalNeuralEngine, get_engine
from .self_play import (
    SelfPlayConfig, SelfPlayLoop, _generate_queries,
    _score_12d, _compute_weight_deltas, _apply_weight_deltas,
    _get_lr, _get_phase, _measure_capability, _std,
    LENS_ORDER, DIM_NAMES,
    PHASE_WARMUP, PHASE_EXPLORE, PHASE_EXPLOIT, PHASE_REFINE,
)
from .n3_alchemy import (
    WREATHS, _wreath_biased_queries, _snapshot_weights,
    WeightSnapshot, create_holographic_crystal, rewire_weights_to_a_plus,
)
from .constants import TOTAL_SHELLS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DEFINITIONS: Elements, Metals/Planets, 3x3 Completion Matrix
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ELEMENTS = {
    "S": {"name": "Square/Earth", "element": "Earth", "shells": list(range(13, 25)),
           "lr_mult": 1.0, "explore_bias": 0.25, "exploit_bias": 0.45},
    "F": {"name": "Flower/Fire", "element": "Fire", "shells": list(range(1, 13)),
           "lr_mult": 1.3, "explore_bias": 0.35, "exploit_bias": 0.35},
    "C": {"name": "Cloud/Water", "element": "Water", "shells": list(range(13, 25)),
           "lr_mult": 0.9, "explore_bias": 0.30, "exploit_bias": 0.40},
    "R": {"name": "Fractal/Air", "element": "Air", "shells": list(range(25, 37)),
           "lr_mult": 0.8, "explore_bias": 0.20, "exploit_bias": 0.40},
}

# 7 Classical metals/planets with alchemical correspondences
METALS = [
    {"metal": "Lead",      "planet": "Saturn",  "symbol": "Pb", "lr_mult": 0.5, "principle": "restriction",
     "shells": list(range(1, 6)),   "explore": 0.15, "exploit": 0.55},
    {"metal": "Tin",       "planet": "Jupiter", "symbol": "Sn", "lr_mult": 0.8, "principle": "expansion",
     "shells": list(range(6, 12)),  "explore": 0.30, "exploit": 0.40},
    {"metal": "Iron",      "planet": "Mars",    "symbol": "Fe", "lr_mult": 1.5, "principle": "force",
     "shells": list(range(12, 18)), "explore": 0.40, "exploit": 0.30},
    {"metal": "Gold",      "planet": "Sun",     "symbol": "Au", "lr_mult": 1.0, "principle": "perfection",
     "shells": list(range(18, 24)), "explore": 0.25, "exploit": 0.45},
    {"metal": "Copper",    "planet": "Venus",   "symbol": "Cu", "lr_mult": 1.2, "principle": "harmony",
     "shells": list(range(24, 30)), "explore": 0.35, "exploit": 0.35},
    {"metal": "Quicksilver","planet": "Mercury","symbol": "Hg", "lr_mult": 0.7, "principle": "fluidity",
     "shells": list(range(30, 36)), "explore": 0.20, "exploit": 0.45},
    {"metal": "Silver",    "planet": "Moon",    "symbol": "Ag", "lr_mult": 0.9, "principle": "reflection",
     "shells": list(range(1, 37)),  "explore": 0.25, "exploit": 0.40},  # full spectrum
]

# 3x3 completion matrix: each change x each change
COMPLETION_MATRIX = []
for outer in ["SULFUR", "SALT", "MERCURY"]:
    for inner in ["SULFUR", "SALT", "MERCURY"]:
        COMPLETION_MATRIX.append({
            "outer": outer,
            "inner": inner,
            "name": f"{outer[:3]}x{inner[:3]}",
            "shells": WREATHS[outer]["shells"] if outer == inner
                      else sorted(set(WREATHS[outer]["shells"]) | set(WREATHS[inner]["shells"])),
            "lr_mult": WREATHS[outer]["lr_mult"] * WREATHS[inner]["lr_mult"],
            "explore": (WREATHS[outer]["explore_bias"] + WREATHS[inner]["explore_bias"]) / 2,
            "exploit": (WREATHS[outer]["exploit_bias"] + WREATHS[inner]["exploit_bias"]) / 2,
        })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  EXHAUSTIVE METRICS SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class ExhaustiveMetrics:
    """Complete metric snapshot for meta-observer consumption."""

    # ── Identity ──
    stage: str                    # A/B/C/D/FINAL
    timestamp: float
    total_cycles_so_far: int

    # ── Discrimination Metrics ──
    discrimination_global: float          # std of all merged scores
    discrimination_per_path: dict         # {S: x, F: x, C: x, R: x}
    discrimination_per_wreath: dict       # {Su: x, Me: x, Sa: x}
    discrimination_top_bottom_gap: float  # max - min merged score
    discrimination_top5_spread: float     # std of top-5 scores
    discrimination_gini: float            # Gini coefficient of score distribution

    # ── Convergence Metrics ──
    convergence_rate: float               # delta_metric / delta_cycles
    convergence_stability: float          # 1 - std(recent_deltas) / mean(recent_deltas)
    convergence_plateau_detected: bool    # <0.1% change over last 500 cycles
    convergence_phase_transitions: int    # count of detected phase transitions

    # ── Balance Metrics ──
    balance_path_entropy: float           # H(path_weights) / H_max — 1.0 = perfect balance
    balance_path_gini: float              # Gini of path weights — 0 = perfect equality
    balance_resonance_entropy: float      # H(resonance_weights) / H_max
    balance_desire_entropy: float         # H(desire_weights) / H_max
    balance_sfcr_contribution: dict       # actual % each path contributes to final scores

    # ── Compression Metrics ──
    compression_seed_fidelity: float      # 1 - mean(|full - decompressed| / full)
    compression_archetype_fidelity: float
    compression_nano_fidelity: float
    compression_information_ratio: float  # bits_in_seed / bits_in_full

    # ── Symmetry Metrics ──
    symmetry_path_deviation: float        # distance from equal (0.25, 0.25, 0.25, 0.25)
    symmetry_wreath_deviation: float      # deviation of shell means across wreaths
    symmetry_golden_ratio_fit: float      # how close key ratios are to PHI

    # ── Resonance Metrics ──
    resonance_mean: float
    resonance_std: float
    resonance_best: float
    resonance_worst: float
    resonance_improvement_rate: float     # delta_resonance / delta_cycles

    # ── Desire Metrics ──
    desire_alignment_strength: float      # how strongly align dominates
    desire_exploration_ratio: float       # explore / (explore + exploit_equiv)
    desire_zpa_pull: float                # zero-point attractor strength

    # ── Information Theory ──
    info_weight_entropy: float            # entropy of weight distribution
    info_effective_dimensionality: float  # participation ratio of weights
    info_sparsity: float                  # fraction of near-zero weights

    # ── Health Metrics ──
    health_gradient_magnitude: float      # avg |delta| per cycle
    health_gradient_consistency: float    # cosine similarity of consecutive deltas
    health_weight_explosion: bool         # any weight > 100x initial
    health_weight_collapse: bool          # any learnable param < 0.001
    health_nan_detected: bool
    health_commitment_rate: float         # fraction of cycles that commit

    # ── Self-Retrieval Performance ──
    selfret_top1: float                   # top-1 self-retrieval accuracy
    selfret_top3: float
    selfret_top5: float
    selfret_mean_rank: float              # average rank of correct doc
    selfret_mean_discrimination: float    # avg gap between correct and mean-wrong

    # ── Stage-Specific ──
    stage_kept: int
    stage_discarded: int
    stage_neutral: int
    stage_elapsed_seconds: float
    stage_cycles: int
    stage_waves: int


def compute_exhaustive_metrics(
    engine: CrystalNeuralEngine,
    store: FractalWeightStore,
    stage: str,
    total_cycles: int,
    stage_stats: dict,
    prev_metrics: Optional["ExhaustiveMetrics"] = None,
) -> ExhaustiveMetrics:
    """Compute ALL metrics for the current engine state."""

    probe_queries = [
        "seed kernel crystal", "neural network weight",
        "element bridge SFCR", "hologram projection chapter",
        "compression fractal qshrink", "consciousness emergence angel",
        "metro routing transport", "manuscript generation proof",
        "transformation fire desire", "structure earth boundary",
        "dissolution water cloud", "recursion air fractal",
    ]

    # ── Discrimination ──
    all_merged = []
    all_resonances = []
    path_contribs = {"S": [], "F": [], "C": [], "R": []}
    wreath_scores = {"Su": [], "Me": [], "Sa": []}
    committed = 0
    total_probes = 0

    for q in probe_queries:
        result = engine.forward(q, max_results=20)
        total_probes += 1
        if result.committed:
            committed += 1
        for c in result.candidates:
            all_merged.append(c.merged_score)
            all_resonances.append(c.resonance)
            for face in "SFCR":
                path_contribs[face].append(c.path_contributions.get(face, 0.0))
            # Map shell to wreath
            if c.shell <= 12:
                wreath_scores["Su"].append(c.merged_score)
            elif c.shell <= 24:
                wreath_scores["Me"].append(c.merged_score)
            else:
                wreath_scores["Sa"].append(c.merged_score)

    disc_global = _std(all_merged) if all_merged else 0.0
    disc_per_path = {f: _std(v) for f, v in path_contribs.items()}
    disc_per_wreath = {w: _std(v) if v else 0.0 for w, v in wreath_scores.items()}
    gap = (max(all_merged) - min(all_merged)) if all_merged else 0.0
    top5_spread = _std(sorted(all_merged, reverse=True)[:5]) if len(all_merged) >= 5 else 0.0

    # Gini coefficient
    gini = _gini(all_merged)

    # ── Self-retrieval ──
    top1, top3, top5, mean_rank, mean_disc_gap = _self_retrieval_test(engine, store)

    # ── Balance ──
    pw = list(store.path_weights.values())
    rw = list(store.resonance_weights.values())
    dw = list(store.desire_weights.values())

    balance_path_entropy = _normalized_entropy(pw)
    balance_path_gini = _gini(pw)
    balance_res_entropy = _normalized_entropy(rw)
    balance_des_entropy = _normalized_entropy(dw)

    # Actual SFCR contribution (from probes)
    sfcr_totals = {f: sum(v) for f, v in path_contribs.items()}
    sfcr_sum = sum(sfcr_totals.values()) or 1.0
    sfcr_pct = {f: v / sfcr_sum for f, v in sfcr_totals.items()}

    # ── Compression ──
    seed_fid = _seed_fidelity(store)
    arch_fid = _archetype_fidelity(store)
    nano_fid = _nano_fidelity(store)
    info_ratio = 36 / max(store._total_weights, 1)  # seed params / full params

    # ── Symmetry ──
    sym_path = math.sqrt(sum((v - 0.25)**2 for v in pw))
    shell_means_by_wreath = {"Su": [], "Me": [], "Sa": []}
    for s, seed in store.shell_seeds.items():
        wname = store.shell_to_wreath_name(s)
        shell_means_by_wreath[wname].append(seed.mean)
    wreath_avgs = {w: (sum(v)/len(v) if v else 0) for w, v in shell_means_by_wreath.items()}
    sym_wreath = _std(list(wreath_avgs.values()))

    # Golden ratio fit: check if key ratios approximate PHI
    golden_fit = _golden_ratio_fit(store)

    # ── Information theory ──
    weight_entropy = _weight_entropy(store)
    eff_dim = _effective_dimensionality(store)
    sparsity = _sparsity(store)

    # ── Health ──
    grad_mag = stage_stats.get("avg_gradient_magnitude", 0.0)
    grad_consist = stage_stats.get("gradient_consistency", 0.0)
    explosion = any(v > 50 for v in pw) or any(seed.mean > 500 for seed in store.shell_seeds.values())
    collapse = any(v < 0.001 for v in pw) or any(v < 0.001 for v in rw)
    nan_detected = any(math.isnan(v) for v in pw + rw + dw)

    # ── Convergence ──
    conv_rate = stage_stats.get("convergence_rate", 0.0)
    conv_stability = stage_stats.get("convergence_stability", 0.0)
    plateau = stage_stats.get("plateau_detected", False)
    phase_transitions = stage_stats.get("phase_transitions", 0)

    # ── Resonance ──
    r_mean = sum(all_resonances) / max(len(all_resonances), 1) if all_resonances else 0.0
    r_std = _std(all_resonances) if all_resonances else 0.0
    r_best = max(all_resonances) if all_resonances else 0.0
    r_worst = min(all_resonances) if all_resonances else 0.0
    r_improve_rate = (r_mean - (prev_metrics.resonance_mean if prev_metrics else r_mean)) / max(total_cycles, 1)

    # ── Desire ──
    des_align = store.desire_weights.get("align", 0.25)
    des_explore = store.desire_weights.get("explore", 0.25)
    des_zpa = store.desire_weights.get("zpa", 0.25)

    return ExhaustiveMetrics(
        stage=stage,
        timestamp=time.time(),
        total_cycles_so_far=total_cycles,
        # Discrimination
        discrimination_global=disc_global,
        discrimination_per_path=disc_per_path,
        discrimination_per_wreath=disc_per_wreath,
        discrimination_top_bottom_gap=gap,
        discrimination_top5_spread=top5_spread,
        discrimination_gini=gini,
        # Convergence
        convergence_rate=conv_rate,
        convergence_stability=conv_stability,
        convergence_plateau_detected=plateau,
        convergence_phase_transitions=phase_transitions,
        # Balance
        balance_path_entropy=balance_path_entropy,
        balance_path_gini=balance_path_gini,
        balance_resonance_entropy=balance_res_entropy,
        balance_desire_entropy=balance_des_entropy,
        balance_sfcr_contribution=sfcr_pct,
        # Compression
        compression_seed_fidelity=seed_fid,
        compression_archetype_fidelity=arch_fid,
        compression_nano_fidelity=nano_fid,
        compression_information_ratio=info_ratio,
        # Symmetry
        symmetry_path_deviation=sym_path,
        symmetry_wreath_deviation=sym_wreath,
        symmetry_golden_ratio_fit=golden_fit,
        # Resonance
        resonance_mean=r_mean,
        resonance_std=r_std,
        resonance_best=r_best,
        resonance_worst=r_worst,
        resonance_improvement_rate=r_improve_rate,
        # Desire
        desire_alignment_strength=des_align,
        desire_exploration_ratio=des_explore / max(des_explore + des_align, 0.01),
        desire_zpa_pull=des_zpa,
        # Information
        info_weight_entropy=weight_entropy,
        info_effective_dimensionality=eff_dim,
        info_sparsity=sparsity,
        # Health
        health_gradient_magnitude=grad_mag,
        health_gradient_consistency=grad_consist,
        health_weight_explosion=explosion,
        health_weight_collapse=collapse,
        health_nan_detected=nan_detected,
        health_commitment_rate=committed / max(total_probes, 1),
        # Self-retrieval
        selfret_top1=top1,
        selfret_top3=top3,
        selfret_top5=top5,
        selfret_mean_rank=mean_rank,
        selfret_mean_discrimination=mean_disc_gap,
        # Stage
        stage_kept=stage_stats.get("kept", 0),
        stage_discarded=stage_stats.get("discarded", 0),
        stage_neutral=stage_stats.get("neutral", 0),
        stage_elapsed_seconds=stage_stats.get("elapsed", 0.0),
        stage_cycles=stage_stats.get("cycles", 0),
        stage_waves=stage_stats.get("waves", 0),
    )


def _gini(values: list[float]) -> float:
    """Gini coefficient (0 = perfect equality, 1 = maximum inequality)."""
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_v = sorted(values)
    n = len(sorted_v)
    cumsum = sum((i + 1) * v for i, v in enumerate(sorted_v))
    return (2 * cumsum) / (n * sum(sorted_v)) - (n + 1) / n


def _normalized_entropy(probs: list[float]) -> float:
    """Entropy normalized to [0, 1] where 1 = uniform."""
    total = sum(probs)
    if total == 0 or len(probs) == 0:
        return 0.0
    normed = [p / total for p in probs if p > 0]
    h = -sum(p * math.log2(p) for p in normed)
    h_max = math.log2(len(probs))
    return h / h_max if h_max > 0 else 0.0


def _self_retrieval_test(engine: CrystalNeuralEngine, store: FractalWeightStore) -> tuple:
    """Test self-retrieval: each doc queries with its own tokens, check if it's #1."""
    docs = store.doc_registry
    if not docs:
        return 0.0, 0.0, 0.0, 50.0, 0.0

    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    ranks = []
    disc_gaps = []
    tested = 0

    rng = random.Random(108)
    sample = rng.sample(docs, min(len(docs), 40))  # sample for speed

    for doc in sample:
        tokens = doc.get("tokens", [])
        if len(tokens) < 3:
            continue
        query_tokens = rng.sample(tokens, min(3, len(tokens)))
        query = " ".join(query_tokens)
        result = engine.forward(query, max_results=20)

        doc_id = doc.get("id", "")
        tested += 1
        found_rank = None

        for i, c in enumerate(result.candidates):
            if c.doc_id == doc_id:
                found_rank = i + 1
                break

        if found_rank is None:
            found_rank = 50
        ranks.append(found_rank)

        if found_rank == 1:
            top1_hits += 1
        if found_rank <= 3:
            top3_hits += 1
        if found_rank <= 5:
            top5_hits += 1

        # Discrimination gap
        if result.candidates and found_rank <= len(result.candidates):
            correct_score = result.candidates[found_rank - 1].merged_score
            other_scores = [c.merged_score for i, c in enumerate(result.candidates) if i != found_rank - 1]
            if other_scores:
                disc_gaps.append(correct_score - sum(other_scores) / len(other_scores))

    n = max(tested, 1)
    return (
        top1_hits / n,
        top3_hits / n,
        top5_hits / n,
        sum(ranks) / n,
        sum(disc_gaps) / max(len(disc_gaps), 1),
    )


def _seed_fidelity(store: FractalWeightStore) -> float:
    """How well do shell seeds reconstruct full weights?"""
    if not store.shell_seeds:
        return 0.0
    means = [s.mean for s in store.shell_seeds.values()]
    if not means:
        return 0.0
    overall_mean = sum(means) / len(means)
    deviations = [abs(m - overall_mean) / max(overall_mean, 0.01) for m in means]
    return max(0.0, 1.0 - sum(deviations) / len(deviations))


def _archetype_fidelity(store: FractalWeightStore) -> float:
    """How well do archetype seeds summarize shell seeds?"""
    if not store._archetype_seeds or not store.shell_seeds:
        return 0.0
    errors = []
    for arch_id, arch in store._archetype_seeds.items():
        # Shells in this archetype
        arch_shells = [(arch_id - 1) * 3 + w + 1 for w in range(3)]
        for s in arch_shells:
            if s in store.shell_seeds:
                error = abs(store.shell_seeds[s].mean - arch.mean) / max(arch.mean, 0.01)
                errors.append(error)
    return max(0.0, 1.0 - sum(errors) / max(len(errors), 1))


def _nano_fidelity(store: FractalWeightStore) -> float:
    """How well does nano seed summarize everything?"""
    if not store._nano_seed or not store.shell_seeds:
        return 0.0
    nano_mean = store._nano_seed.global_mean
    errors = [abs(s.mean - nano_mean) / max(nano_mean, 0.01) for s in store.shell_seeds.values()]
    return max(0.0, 1.0 - sum(errors) / max(len(errors), 1))


def _golden_ratio_fit(store: FractalWeightStore) -> float:
    """How close are key weight ratios to PHI or PHI_INV?"""
    pw = store.path_weights
    ratios = []
    keys = list(pw.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = pw[keys[i]], pw[keys[j]]
            if min(a, b) > 0.01:
                r = max(a, b) / min(a, b)
                # Distance to nearest golden ratio
                dist_phi = abs(r - PHI)
                dist_phi_inv = abs(r - 1.0 / PHI_INV) if PHI_INV > 0 else 99
                dist_1 = abs(r - 1.0)
                min_dist = min(dist_phi, dist_phi_inv, dist_1)
                ratios.append(max(0.0, 1.0 - min_dist / PHI))
    return sum(ratios) / max(len(ratios), 1)


def _weight_entropy(store: FractalWeightStore) -> float:
    """Entropy of the full weight distribution."""
    if not store.shell_seeds:
        return 0.0
    means = [max(s.mean, 0.001) for s in store.shell_seeds.values()]
    total = sum(means)
    probs = [m / total for m in means]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _effective_dimensionality(store: FractalWeightStore) -> float:
    """Participation ratio: how many dimensions are 'active'."""
    if not store.shell_seeds:
        return 0.0
    means = [s.mean for s in store.shell_seeds.values()]
    sq_sum = sum(m**2 for m in means)
    sum_sq = sum(means)**2
    return sum_sq / max(sq_sum, 0.001)


def _sparsity(store: FractalWeightStore) -> float:
    """Fraction of weights near zero."""
    all_params = (
        list(store.path_weights.values()) +
        list(store.resonance_weights.values()) +
        list(store.desire_weights.values()) +
        [store.bridge_modulation, store.geo_arith_blend]
    )
    near_zero = sum(1 for v in all_params if abs(v) < 0.01)
    return near_zero / max(len(all_params), 1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WAVE RUNNER — executes a single cultivation wave
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _run_wave(
    store: FractalWeightStore,
    engine: CrystalNeuralEngine,
    wave_name: str,
    cycles: int,
    shells: list[int],
    element: str,
    lr_mult: float,
    explore_bias: float,
    exploit_bias: float,
    max_time_sec: float,
    seed: int = 42,
) -> dict:
    """Run a single cultivation wave. Returns stats dict."""
    t0 = time.time()

    queries = _wreath_biased_queries(store, shells, element, seed=seed)
    if not queries:
        queries = _generate_queries(store, SelfPlayConfig(seed=seed))

    config = SelfPlayConfig(
        total_cycles=cycles,
        cycles_per_checkpoint=max(cycles // 5, 50),
        base_lr=0.03 * lr_mult,
        lr_schedule="cosine",
        lens_rotation_period=max(cycles // 16, 5),
        max_time_minutes=int(max_time_sec / 60) + 1,
        query_source="mixed",
        seed=seed,
        warmup_fraction=0.08,
        explore_fraction=explore_bias,
        exploit_fraction=exploit_bias,
        adversarial_probes=True,
        adapt_path_weights=True,
        capability_tracking=False,  # we track our own metrics
    )

    loop = SelfPlayLoop(config)
    loop.store = store
    loop.engine = engine

    report = loop.run(cycles=cycles, queries=queries)

    elapsed = time.time() - t0
    return {
        "wave": wave_name,
        "cycles": report.total_cycles,
        "kept": report.kept,
        "discarded": report.discarded,
        "neutral": report.neutral,
        "resonance_init": report.initial_resonance,
        "resonance_final": report.final_resonance,
        "elapsed": elapsed,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  A+ LIFT — weave multiple snapshots into an A+ crystal
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _a_plus_lift(
    store: FractalWeightStore,
    snapshots: list[dict],
    blend_weights: list[float],
    symmetry_blend: float = 0.35,
) -> dict:
    """Weave multiple weight snapshots into a single A+ crystal and apply.

    blend_weights: relative importance of each snapshot
    symmetry_blend: how much to blend toward the symmetric ideal (0-1)
    """
    total_blend = sum(blend_weights[:len(snapshots)])
    if total_blend == 0:
        total_blend = 1.0

    # Weighted average of all snapshots
    unified = {"path_weights": {}, "resonance_weights": {}, "desire_weights": {},
               "shell_seed_means": {}, "bridge_modulation": 0.0, "geo_arith_blend": 0.0}

    for i, snap in enumerate(snapshots):
        w = blend_weights[i] / total_blend if i < len(blend_weights) else 1.0 / total_blend
        for k, v in snap.get("path_weights", {}).items():
            unified["path_weights"][k] = unified["path_weights"].get(k, 0.0) + v * w
        for k, v in snap.get("resonance_weights", {}).items():
            unified["resonance_weights"][k] = unified["resonance_weights"].get(k, 0.0) + v * w
        for k, v in snap.get("desire_weights", {}).items():
            unified["desire_weights"][k] = unified["desire_weights"].get(k, 0.0) + v * w
        for k, v in snap.get("shell_seed_means", {}).items():
            sk = str(k)
            unified["shell_seed_means"][sk] = unified["shell_seed_means"].get(sk, 0.0) + v * w
        unified["bridge_modulation"] += snap.get("bridge_modulation", 0.2) * w
        unified["geo_arith_blend"] += snap.get("geo_arith_blend", 0.5) * w

    # Blend with symmetric ideal
    s = symmetry_blend
    learned_frac = 1.0 - s

    a_plus = {}

    # Path weights: blend toward uniform
    a_plus["path_weights"] = {}
    for k in ["S", "F", "C", "R"]:
        a_plus["path_weights"][k] = unified["path_weights"].get(k, 0.25) * learned_frac + 0.25 * s
    _normalize(a_plus["path_weights"])

    # Resonance: blend toward uniform
    a_plus["resonance_weights"] = {}
    uniform_r = 1.0 / 6
    for k in ["addr_fit", "inv_fit", "phase", "boundary", "scale", "compress"]:
        a_plus["resonance_weights"][k] = unified["resonance_weights"].get(k, uniform_r) * learned_frac + uniform_r * s
    _normalize(a_plus["resonance_weights"])

    # Desire: blend toward PHI-weighted ideal
    phi_des = {"align": PHI_INV, "explore": 1.0/PHI**2, "zpa": 1.0/PHI**3, "con_sat": 1.0/PHI**4}
    _normalize(phi_des)
    a_plus["desire_weights"] = {}
    for k in ["align", "explore", "zpa", "con_sat"]:
        a_plus["desire_weights"][k] = unified["desire_weights"].get(k, 0.25) * learned_frac + phi_des[k] * s
    _normalize(a_plus["desire_weights"])

    # Scalars
    a_plus["bridge_modulation"] = unified["bridge_modulation"] * learned_frac + PHI_INV * 0.2 * s
    a_plus["geo_arith_blend"] = unified["geo_arith_blend"] * learned_frac + PHI_INV * s

    # Shell seeds
    a_plus["shell_seed_means"] = {}
    for sk, sv in unified["shell_seed_means"].items():
        shell_num = int(sk)
        golden_scale = PHI ** ((18 - abs(shell_num - 18)) / 18)
        a_plus["shell_seed_means"][sk] = sv * learned_frac + sv * golden_scale / PHI * s

    # Apply to store
    rewire_weights_to_a_plus(a_plus)

    return a_plus


def _normalize(d: dict):
    """Normalize dict values to sum to 1."""
    total = sum(d.values())
    if total > 0:
        for k in d:
            d[k] /= total


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  QSHRINK 4D COMPRESSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def qshrink_to_4d(crystal_state: dict) -> dict:
    """Compress a full crystal state to its tightest 4D interconnected arrangement.

    The 4 dimensions correspond to the 4 SFCR elements:
      D1 (S/Earth): structural coherence
      D2 (F/Fire): relational intensity
      D3 (C/Water): observational depth
      D4 (R/Air): compressive efficiency

    Each dimension stores: value, gradient, momentum, curvature = 4 numbers.
    Total: 4 dims x 4 numbers = 16 values = the absolute minimum.
    """
    pw = crystal_state.get("path_weights", {})
    rw = crystal_state.get("resonance_weights", {})
    dw = crystal_state.get("desire_weights", {})
    shells = crystal_state.get("shell_seed_means", {})
    bm = crystal_state.get("bridge_modulation", 0.2)
    gb = crystal_state.get("geo_arith_blend", 0.5)

    # Compute shell averages per wreath
    su_shells = [shells.get(str(s), 5.0) for s in range(1, 13)]
    me_shells = [shells.get(str(s), 5.0) for s in range(13, 25)]
    sa_shells = [shells.get(str(s), 5.0) for s in range(25, 37)]

    su_mean = sum(su_shells) / max(len(su_shells), 1)
    me_mean = sum(me_shells) / max(len(me_shells), 1)
    sa_mean = sum(sa_shells) / max(len(sa_shells), 1)

    # D1: S/Earth — structural coherence
    d1_value = pw.get("S", 0.25)
    d1_gradient = rw.get("addr_fit", 0.16) + rw.get("phase", 0.16)  # structural resonance
    d1_momentum = me_mean  # Earth wreath shell strength
    d1_curvature = dw.get("con_sat", 0.05)  # constraint satisfaction

    # D2: F/Fire — relational intensity
    d2_value = pw.get("F", 0.25)
    d2_gradient = rw.get("scale", 0.2) + rw.get("compress", 0.2)  # scale+compress
    d2_momentum = su_mean  # Fire wreath shell strength
    d2_curvature = dw.get("align", 0.35)  # alignment

    # D3: C/Water — observational depth
    d3_value = pw.get("C", 0.25)
    d3_gradient = rw.get("inv_fit", 0.15) + rw.get("boundary", 0.05)  # conservation
    d3_momentum = bm  # bridge modulation (cross-element flow)
    d3_curvature = dw.get("explore", 0.2)  # exploration

    # D4: R/Air — compressive efficiency
    d4_value = pw.get("R", 0.25)
    d4_gradient = gb  # geometric/arithmetic blend
    d4_momentum = sa_mean  # Air wreath shell strength
    d4_curvature = dw.get("zpa", 0.25)  # zero-point attractor

    hologram_4d = {
        "dimensions": {
            "D1_Earth": {"value": d1_value, "gradient": d1_gradient, "momentum": d1_momentum, "curvature": d1_curvature},
            "D2_Fire":  {"value": d2_value, "gradient": d2_gradient, "momentum": d2_momentum, "curvature": d2_curvature},
            "D3_Water": {"value": d3_value, "gradient": d3_gradient, "momentum": d3_momentum, "curvature": d3_curvature},
            "D4_Air":   {"value": d4_value, "gradient": d4_gradient, "momentum": d4_momentum, "curvature": d4_curvature},
        },
        "interconnections": {
            # 6 cross-dimensional connections (4 choose 2)
            "D1_D2": d1_value * d2_value * PHI,    # Earth-Fire
            "D1_D3": d1_value * d3_value,           # Earth-Water
            "D1_D4": d1_value * d4_value * PHI_INV, # Earth-Air (golden complement)
            "D2_D3": d2_value * d3_value * PHI,     # Fire-Water (golden)
            "D2_D4": d2_value * d4_value,           # Fire-Air
            "D3_D4": d3_value * d4_value * PHI,     # Water-Air (golden)
        },
        "total_values": 16,
        "compression_ratio": f"38837:16 = {38837/16:.0f}:1",
        "hash": hashlib.sha256(json.dumps(crystal_state, sort_keys=True, default=str).encode()).hexdigest()[:16],
    }

    return hologram_4d


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  INVERSION + ROTATION + POLE FINDING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def invert_and_find_poles(crystal_state: dict) -> dict:
    """Invert ABCD+, rotate 90 degrees, find the two poles, extract A+."""

    pw = crystal_state.get("path_weights", {})
    rw = crystal_state.get("resonance_weights", {})
    dw = crystal_state.get("desire_weights", {})

    # ── Inversion: reflect all weights through their midpoint ──
    def _invert(d):
        vals = list(d.values())
        mid = sum(vals) / max(len(vals), 1)
        inv = {k: max(0.001, 2 * mid - v) for k, v in d.items()}
        _normalize(inv)
        return inv

    inv_pw = _invert(pw)
    inv_rw = _invert(rw)
    inv_dw = _invert(dw)
    inv_bm = max(0.05, 1.0 - crystal_state.get("bridge_modulation", 0.2))
    inv_gb = max(0.1, min(0.95, 1.0 - crystal_state.get("geo_arith_blend", 0.5)))

    inverted = {
        "path_weights": inv_pw,
        "resonance_weights": inv_rw,
        "desire_weights": inv_dw,
        "bridge_modulation": inv_bm,
        "geo_arith_blend": inv_gb,
        "shell_seed_means": crystal_state.get("shell_seed_means", {}),
    }

    # ── 90-degree rotation: swap axis pairs ──
    # In 4D SFCR space, 90-degree rotation swaps S<->C and F<->R
    pole_north = {
        "path_weights": {"S": pw.get("C", 0.25), "F": pw.get("R", 0.25),
                         "C": pw.get("S", 0.25), "R": pw.get("F", 0.25)},
        "description": "North pole: S<->C, F<->R rotation",
    }

    pole_south = {
        "path_weights": {"S": inv_pw.get("C", 0.25), "F": inv_pw.get("R", 0.25),
                         "C": inv_pw.get("S", 0.25), "R": inv_pw.get("F", 0.25)},
        "description": "South pole: inverted S<->C, F<->R rotation",
    }

    # ── The A+ is the midpoint between the two poles ──
    a_plus_pw = {}
    for k in ["S", "F", "C", "R"]:
        a_plus_pw[k] = (pole_north["path_weights"][k] + pole_south["path_weights"][k]) / 2
    _normalize(a_plus_pw)

    # Blend A+ resonance: 50% original + 50% inverted
    a_plus_rw = {}
    for k in rw:
        a_plus_rw[k] = (rw.get(k, 0.16) + inv_rw.get(k, 0.16)) / 2
    _normalize(a_plus_rw)

    a_plus_dw = {}
    for k in dw:
        a_plus_dw[k] = (dw.get(k, 0.25) + inv_dw.get(k, 0.25)) / 2
    _normalize(a_plus_dw)

    final_a_plus = {
        "path_weights": a_plus_pw,
        "resonance_weights": a_plus_rw,
        "desire_weights": a_plus_dw,
        "bridge_modulation": (crystal_state.get("bridge_modulation", 0.2) + inv_bm) / 2,
        "geo_arith_blend": (crystal_state.get("geo_arith_blend", 0.5) + inv_gb) / 2,
        "shell_seed_means": crystal_state.get("shell_seed_means", {}),
    }

    return {
        "inverted": inverted,
        "pole_north": pole_north,
        "pole_south": pole_south,
        "final_a_plus": final_a_plus,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN TRAINING LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_full_training_loop(
    cycles_a: int = 500,
    cycles_b: int = 400,
    cycles_c: int = 300,
    cycles_d: int = 250,
    max_time_minutes: int = 45,
) -> dict:
    """Execute the complete ABCD+ training loop.

    Stage A: 3 runs x 3 changes = 9 waves  (9 x cycles_a)
    Stage B: 5 runs x 4 elements = 20 waves (20 x cycles_b)
    Stage C: 7 runs x 7 metals = 49 waves  (49 x cycles_c)
    Stage D: 9 runs x 9 completions = 81 waves (81 x cycles_d)
    Final:   Invert + rotate + poles + QSHRINK + hologram
    """
    store = get_store()
    engine = CrystalNeuralEngine(store)

    t_global = time.time()
    max_time = max_time_minutes * 60
    total_cycles = 0
    all_metrics = []
    meta_log = []
    all_snapshots = {"A": [], "B": [], "C": [], "D": []}

    def _time_left():
        return max_time - (time.time() - t_global)

    def _log(msg):
        meta_log.append(msg)
        print(msg)

    _log(f"{'#'*70}")
    _log(f"# FULL TRAINING LOOP — ABCD+ Crystal Transmutation")
    _log(f"# Stages: A(9 waves) -> B(20 waves) -> C(49 waves) -> D(81 waves)")
    _log(f"# Total planned waves: 159")
    _log(f"# Max time: {max_time_minutes} minutes")
    _log(f"{'#'*70}\n")

    # ━━ STAGE A: 3 runs x 3 changes = 9 waves ━━━━━━━━━━━━━━━━━━━━━
    _log(f"\n{'='*60}")
    _log(f"STAGE A: THREE CHANGES x THREE RUNS = 9 waves")
    _log(f"{'='*60}")

    stage_a_stats = {"kept": 0, "discarded": 0, "neutral": 0, "elapsed": 0, "cycles": 0, "waves": 0}

    for run_idx in range(3):
        for change_name, change_def in WREATHS.items():
            if _time_left() < 10:
                _log(f"  [TIMEOUT] Stage A truncated at wave {stage_a_stats['waves']}")
                break

            wave_name = f"A.{run_idx+1}.{change_name}"
            _log(f"  [{wave_name}] {change_def['principle']} (shells {change_def['shells'][0]}-{change_def['shells'][-1]})")

            stats = _run_wave(
                store, engine, wave_name, cycles_a,
                change_def["shells"], change_def["element"],
                change_def["lr_mult"], change_def["explore_bias"], change_def["exploit_bias"],
                max_time_sec=min(_time_left(), 120),
                seed=42 + run_idx * 10 + change_def["wreath"],
            )

            stage_a_stats["kept"] += stats["kept"]
            stage_a_stats["discarded"] += stats["discarded"]
            stage_a_stats["neutral"] += stats["neutral"]
            stage_a_stats["elapsed"] += stats["elapsed"]
            stage_a_stats["cycles"] += stats["cycles"]
            stage_a_stats["waves"] += 1
            total_cycles += stats["cycles"]

            _log(f"    -> {stats['cycles']}cyc, {stats['kept']}kept, res={stats['resonance_final']:.4f} ({stats['elapsed']:.1f}s)")

    # A+ snapshot
    snap_a = _snapshot_weights(store, "A+", total_cycles, 0, 0).copy() if hasattr(_snapshot_weights(store, "A+", total_cycles, 0, 0), 'copy') else asdict(_snapshot_weights(store, "A+", total_cycles, 0, 0))
    all_snapshots["A"].append(snap_a)

    # A+ LIFT
    _log(f"\n  >> A+ LIFT: Compressing 9 waves into A+ crystal")
    a_plus = _a_plus_lift(store, [snap_a], [1.0], symmetry_blend=0.30)

    # Metrics after Stage A
    metrics_a = compute_exhaustive_metrics(engine, store, "A", total_cycles, stage_a_stats)
    all_metrics.append(metrics_a)
    _log(f"  >> A+ METRICS: top1={metrics_a.selfret_top1:.1%} disc={metrics_a.discrimination_global:.4f} "
         f"bal={metrics_a.balance_path_entropy:.3f}")

    # ━━ STAGE B: 5 runs x 4 elements = 20 waves ━━━━━━━━━━━━━━━━━━━
    _log(f"\n{'='*60}")
    _log(f"STAGE B: FOUR ELEMENTS x FIVE RUNS = 20 waves")
    _log(f"{'='*60}")

    stage_b_stats = {"kept": 0, "discarded": 0, "neutral": 0, "elapsed": 0, "cycles": 0, "waves": 0}

    for run_idx in range(5):
        for face, elem_def in ELEMENTS.items():
            if _time_left() < 10:
                _log(f"  [TIMEOUT] Stage B truncated at wave {stage_b_stats['waves']}")
                break

            wave_name = f"B.{run_idx+1}.{face}"
            _log(f"  [{wave_name}] {elem_def['name']} (run {run_idx+1}/5)")

            stats = _run_wave(
                store, engine, wave_name, cycles_b,
                elem_def["shells"], elem_def["element"],
                elem_def["lr_mult"], elem_def["explore_bias"], elem_def["exploit_bias"],
                max_time_sec=min(_time_left(), 90),
                seed=100 + run_idx * 10 + ["S","F","C","R"].index(face),
            )

            stage_b_stats["kept"] += stats["kept"]
            stage_b_stats["discarded"] += stats["discarded"]
            stage_b_stats["neutral"] += stats["neutral"]
            stage_b_stats["elapsed"] += stats["elapsed"]
            stage_b_stats["cycles"] += stats["cycles"]
            stage_b_stats["waves"] += 1
            total_cycles += stats["cycles"]

            _log(f"    -> {stats['cycles']}cyc, {stats['kept']}kept, res={stats['resonance_final']:.4f}")

    snap_b = asdict(_snapshot_weights(store, "B+", total_cycles, 0, 0))
    all_snapshots["B"].append(snap_b)

    # AB+ LIFT: weave A+ and B+ with golden ratio weighting
    _log(f"\n  >> AB+ LIFT: Weaving A+ and B+ into AB+ crystal")
    ab_plus = _a_plus_lift(store, [snap_a, snap_b], [PHI_INV, PHI], symmetry_blend=0.25)

    metrics_b = compute_exhaustive_metrics(engine, store, "B", total_cycles, stage_b_stats, metrics_a)
    all_metrics.append(metrics_b)
    _log(f"  >> AB+ METRICS: top1={metrics_b.selfret_top1:.1%} disc={metrics_b.discrimination_global:.4f} "
         f"bal={metrics_b.balance_path_entropy:.3f}")

    # ━━ STAGE C: 7 runs x 7 metals = 49 waves (ESCALATING) ━━━━━━━━
    _log(f"\n{'='*60}")
    _log(f"STAGE C: SEVEN METALS/PLANETS x SEVEN RUNS = 49 waves")
    _log(f"  Each run ESCALATES in intensity (dimensional scale)")
    _log(f"{'='*60}")

    stage_c_stats = {"kept": 0, "discarded": 0, "neutral": 0, "elapsed": 0, "cycles": 0, "waves": 0}

    for run_idx in range(7):
        # Escalating intensity: each run multiplies LR by (1 + run_idx * 0.15)
        intensity = 1.0 + run_idx * 0.15
        _log(f"\n  --- Run {run_idx+1}/7 (intensity={intensity:.2f}x) ---")

        for metal_def in METALS:
            if _time_left() < 10:
                _log(f"  [TIMEOUT] Stage C truncated at wave {stage_c_stats['waves']}")
                break

            wave_name = f"C.{run_idx+1}.{metal_def['symbol']}"
            effective_lr = metal_def["lr_mult"] * intensity

            stats = _run_wave(
                store, engine, wave_name, cycles_c,
                metal_def["shells"], "Fire",  # default element context
                effective_lr, metal_def["explore"], metal_def["exploit"],
                max_time_sec=min(_time_left(), 60),
                seed=200 + run_idx * 20 + METALS.index(metal_def),
            )

            stage_c_stats["kept"] += stats["kept"]
            stage_c_stats["discarded"] += stats["discarded"]
            stage_c_stats["neutral"] += stats["neutral"]
            stage_c_stats["elapsed"] += stats["elapsed"]
            stage_c_stats["cycles"] += stats["cycles"]
            stage_c_stats["waves"] += 1
            total_cycles += stats["cycles"]

            _log(f"    [{wave_name}] {metal_def['metal']}/{metal_def['planet']}: "
                 f"{stats['cycles']}cyc, {stats['kept']}kept ({stats['elapsed']:.1f}s)")

    snap_c = asdict(_snapshot_weights(store, "C+", total_cycles, 0, 0))
    all_snapshots["C"].append(snap_c)

    # ABC+ LIFT
    _log(f"\n  >> ABC+ LIFT: Weaving A+ + B+ + C+ into ABC+ crystal")
    abc_plus = _a_plus_lift(store, [snap_a, snap_b, snap_c],
                            [PHI_INV**2, PHI_INV, PHI], symmetry_blend=0.20)

    metrics_c = compute_exhaustive_metrics(engine, store, "C", total_cycles, stage_c_stats, metrics_b)
    all_metrics.append(metrics_c)
    _log(f"  >> ABC+ METRICS: top1={metrics_c.selfret_top1:.1%} disc={metrics_c.discrimination_global:.4f} "
         f"bal={metrics_c.balance_path_entropy:.3f}")

    # ━━ STAGE D: 9 runs x 9 completions (3x3) = 81 waves ━━━━━━━━━
    _log(f"\n{'='*60}")
    _log(f"STAGE D: 3x3 COMPLETION MATRIX x NINE RUNS = 81 waves")
    _log(f"{'='*60}")

    stage_d_stats = {"kept": 0, "discarded": 0, "neutral": 0, "elapsed": 0, "cycles": 0, "waves": 0}

    for run_idx in range(9):
        comp = COMPLETION_MATRIX[run_idx % len(COMPLETION_MATRIX)]
        _log(f"\n  --- Run {run_idx+1}/9: {comp['name']} ---")

        for comp_def in COMPLETION_MATRIX:
            if _time_left() < 10:
                _log(f"  [TIMEOUT] Stage D truncated at wave {stage_d_stats['waves']}")
                break

            wave_name = f"D.{run_idx+1}.{comp_def['name']}"

            stats = _run_wave(
                store, engine, wave_name, cycles_d,
                comp_def["shells"], "Fire",
                comp_def["lr_mult"], comp_def["explore"], comp_def["exploit"],
                max_time_sec=min(_time_left(), 45),
                seed=300 + run_idx * 30 + COMPLETION_MATRIX.index(comp_def),
            )

            stage_d_stats["kept"] += stats["kept"]
            stage_d_stats["discarded"] += stats["discarded"]
            stage_d_stats["neutral"] += stats["neutral"]
            stage_d_stats["elapsed"] += stats["elapsed"]
            stage_d_stats["cycles"] += stats["cycles"]
            stage_d_stats["waves"] += 1
            total_cycles += stats["cycles"]

            _log(f"    [{wave_name}]: {stats['cycles']}cyc, {stats['kept']}kept")

    snap_d = asdict(_snapshot_weights(store, "D+", total_cycles, 0, 0))
    all_snapshots["D"].append(snap_d)

    # ABCD+ LIFT
    _log(f"\n  >> ABCD+ LIFT: Weaving A+ + B+ + C+ + D+ into ABCD+ crystal")
    abcd_plus = _a_plus_lift(store, [snap_a, snap_b, snap_c, snap_d],
                             [PHI_INV**3, PHI_INV**2, PHI_INV, PHI], symmetry_blend=0.15)

    metrics_d = compute_exhaustive_metrics(engine, store, "D", total_cycles, stage_d_stats, metrics_c)
    all_metrics.append(metrics_d)
    _log(f"  >> ABCD+ METRICS: top1={metrics_d.selfret_top1:.1%} disc={metrics_d.discrimination_global:.4f} "
         f"bal={metrics_d.balance_path_entropy:.3f}")

    # ━━ FINAL: Invert + Rotate + Poles + QSHRINK + Hologram ━━━━━━━
    _log(f"\n{'='*60}")
    _log(f"FINAL: INVERSION + ROTATION + POLES + QSHRINK + HOLOGRAM")
    _log(f"{'='*60}")

    # Invert ABCD+ and find poles
    pole_result = invert_and_find_poles(abcd_plus)
    _log(f"  Inverted ABCD+")
    _log(f"  North pole: {json.dumps({k: round(v, 4) for k, v in pole_result['pole_north']['path_weights'].items()})}")
    _log(f"  South pole: {json.dumps({k: round(v, 4) for k, v in pole_result['pole_south']['path_weights'].items()})}")

    # Apply the final A+ (midpoint of poles)
    final_a_plus = pole_result["final_a_plus"]
    _log(f"  Final A+ (pole midpoint): {json.dumps({k: round(v, 4) for k, v in final_a_plus['path_weights'].items()})}")

    rewire_weights_to_a_plus(final_a_plus)
    _log(f"  >> Weights rewired to final A+ crystal")

    # QSHRINK to 4D
    hologram_4d = qshrink_to_4d(final_a_plus)
    _log(f"\n  QSHRINK 4D Hologram:")
    for dim_name, dim_data in hologram_4d["dimensions"].items():
        _log(f"    {dim_name}: val={dim_data['value']:.4f} grad={dim_data['gradient']:.4f} "
             f"mom={dim_data['momentum']:.4f} curv={dim_data['curvature']:.4f}")
    _log(f"  Compression: {hologram_4d['compression_ratio']}")
    _log(f"  Hash: {hologram_4d['hash']}")

    # Final metrics
    final_stats = {"kept": 0, "discarded": 0, "neutral": 0, "elapsed": time.time() - t_global,
                   "cycles": total_cycles, "waves": sum(s.get("waves", 0) for s in
                   [stage_a_stats, stage_b_stats, stage_c_stats, stage_d_stats])}
    metrics_final = compute_exhaustive_metrics(engine, store, "FINAL", total_cycles, final_stats, metrics_d)
    all_metrics.append(metrics_final)

    # Save hologram
    total_elapsed = time.time() - t_global

    hologram_legacy = {
        "meta": {
            "type": "ABCD+_hologram",
            "version": "1.0",
            "timestamp": time.time(),
            "total_cycles": total_cycles,
            "total_waves": final_stats["waves"],
            "total_elapsed_seconds": total_elapsed,
            "stages": ["A(9)", "B(20)", "C(49)", "D(81)"],
        },
        "abcd_plus": abcd_plus,
        "inversion": {
            "pole_north": pole_result["pole_north"],
            "pole_south": pole_result["pole_south"],
        },
        "final_a_plus": final_a_plus,
        "hologram_4d": hologram_4d,
        "metrics_trajectory": [asdict(m) for m in all_metrics],
        "snapshots": {stage: snaps for stage, snaps in all_snapshots.items()},
    }

    holo_path = DATA_DIR / "abcd_plus_hologram.json"
    with open(holo_path, "w", encoding="utf-8") as f:
        json.dump(hologram_legacy, f, indent=2, default=str)

    _log(f"\n{'='*60}")
    _log(f"HOLOGRAM STORED: {holo_path}")
    _log(f"{'='*60}")

    # ━━ EXHAUSTIVE FINAL REPORT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    _log(f"\n{'#'*70}")
    _log(f"# EXHAUSTIVE METRICS REPORT")
    _log(f"{'#'*70}")

    _log(f"\n## Improvement Trajectory")
    _log(f"{'Stage':<8} {'Top1':>8} {'Top3':>8} {'Top5':>8} {'Disc':>8} {'Gap':>8} {'Balance':>8} {'Golden':>8}")
    _log(f"{'-----':<8} {'----':>8} {'----':>8} {'----':>8} {'----':>8} {'---':>8} {'-------':>8} {'------':>8}")
    for m in all_metrics:
        _log(f"{m.stage:<8} {m.selfret_top1:>7.1%} {m.selfret_top3:>7.1%} {m.selfret_top5:>7.1%} "
             f"{m.discrimination_global:>8.4f} {m.discrimination_top_bottom_gap:>8.4f} "
             f"{m.balance_path_entropy:>8.3f} {m.symmetry_golden_ratio_fit:>8.3f}")

    _log(f"\n## Health Indicators")
    for m in all_metrics:
        flags = []
        if m.health_weight_explosion: flags.append("EXPLOSION")
        if m.health_weight_collapse: flags.append("COLLAPSE")
        if m.health_nan_detected: flags.append("NaN")
        if m.convergence_plateau_detected: flags.append("PLATEAU")
        status = " | ".join(flags) if flags else "HEALTHY"
        _log(f"  {m.stage}: commit={m.health_commitment_rate:.0%} sparsity={m.info_sparsity:.2f} "
             f"eff_dim={m.info_effective_dimensionality:.1f} [{status}]")

    _log(f"\n## Compression Quality")
    for m in all_metrics:
        _log(f"  {m.stage}: seed={m.compression_seed_fidelity:.3f} "
             f"arch={m.compression_archetype_fidelity:.3f} "
             f"nano={m.compression_nano_fidelity:.3f}")

    _log(f"\n## Path Weight Evolution")
    for m in all_metrics:
        sfcr = m.balance_sfcr_contribution
        _log(f"  {m.stage}: S={sfcr.get('S',0):.3f} F={sfcr.get('F',0):.3f} "
             f"C={sfcr.get('C',0):.3f} R={sfcr.get('R',0):.3f} "
             f"(entropy={m.balance_path_entropy:.3f} gini={m.balance_path_gini:.3f})")

    _log(f"\n## Final State")
    _log(f"  Total cycles:  {total_cycles}")
    _log(f"  Total waves:   {final_stats['waves']}")
    _log(f"  Total time:    {total_elapsed:.1f}s ({total_elapsed/60:.1f}min)")
    _log(f"  Self-retrieval: top1={metrics_final.selfret_top1:.1%} top3={metrics_final.selfret_top3:.1%}")
    _log(f"  Discrimination: {metrics_final.discrimination_global:.4f}")
    _log(f"  Path balance:   {metrics_final.balance_path_entropy:.3f}")
    _log(f"  Golden fit:     {metrics_final.symmetry_golden_ratio_fit:.3f}")
    _log(f"  4D Hologram:    {hologram_4d['compression_ratio']}")

    return {
        "total_cycles": total_cycles,
        "total_waves": final_stats["waves"],
        "total_elapsed": total_elapsed,
        "metrics": [asdict(m) for m in all_metrics],
        "hologram_4d": hologram_4d,
        "final_a_plus": final_a_plus,
        "hologram_path": str(holo_path),
        "meta_log": meta_log,
    }
