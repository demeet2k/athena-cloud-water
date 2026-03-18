"""
N^3 Alchemical Self-Play — Three Changes: SULFUR, SALT, MERCURY
================================================================
Runs 3 deep cultivation waves, each biased toward one wreath:
  Wave 1 (SULFUR / Su / wreath 1, shells 1-12): Fire/transformation — high LR, aggressive exploration
  Wave 2 (SALT   / Me / wreath 2, shells 13-24): Earth/crystallization — medium LR, structure-building
  Wave 3 (MERCURY/ Sa / wreath 3, shells 25-36): Water/dissolution — adaptive LR, integration/refinement

After each wave, snapshots the learnable parameters.
Returns all 3 snapshots + final combined state.
"""

from __future__ import annotations

import json
import math
import copy
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from .crystal_weights import FractalWeightStore, get_store, CHECKPOINT_DIR, PHI, PHI_INV
from .neural_engine import CrystalNeuralEngine, get_engine
from .self_play import (
    SelfPlayConfig, SelfPlayLoop, _generate_queries,
    _score_12d, _compute_weight_deltas, _apply_weight_deltas,
    _get_lr, _get_phase, _measure_capability, _std,
    LENS_ORDER, DIM_NAMES, PHASE_WARMUP, PHASE_EXPLORE,
    PHASE_EXPLOIT, PHASE_REFINE,
)
from .constants import TOTAL_SHELLS


# ── Wreath definitions ───────────────────────────────────────────────

WREATHS = {
    "SULFUR": {
        "name": "SULFUR",
        "symbol": "Su",
        "wreath": 1,
        "shells": list(range(1, 13)),
        "element": "Fire",
        "principle": "transformation",
        "lr_mult": 1.5,       # aggressive — burn through old patterns
        "explore_bias": 0.40,  # high exploration
        "exploit_bias": 0.30,
    },
    "SALT": {
        "name": "SALT",
        "symbol": "Me",
        "wreath": 2,
        "shells": list(range(13, 25)),
        "element": "Earth",
        "principle": "crystallization",
        "lr_mult": 1.0,       # steady — build structure
        "explore_bias": 0.25,
        "exploit_bias": 0.45,
    },
    "MERCURY": {
        "name": "MERCURY",
        "symbol": "Sa",
        "wreath": 3,
        "shells": list(range(25, 37)),
        "element": "Air",
        "principle": "dissolution",
        "lr_mult": 0.7,       # gentle — dissolve and integrate
        "explore_bias": 0.20,
        "exploit_bias": 0.35,
    },
}


@dataclass
class WeightSnapshot:
    """Complete snapshot of all learnable parameters at a moment."""
    change: str               # SULFUR / SALT / MERCURY
    cycle_count: int
    path_weights: dict
    resonance_weights: dict
    desire_weights: dict
    bridge_modulation: float
    geo_arith_blend: float
    shell_seed_means: dict    # {shell_num: mean_value}
    discrimination: float
    resonance_best: float
    timestamp: float


@dataclass
class AlchemicalReport:
    """Full report from N^3 alchemical cultivation."""
    snapshots: list           # 3 WeightSnapshots (one per change)
    total_cycles: int
    total_elapsed: float
    final_weights: dict       # the combined final state
    meta_log: list[str]


def _wreath_biased_queries(
    store: FractalWeightStore,
    wreath_shells: list[int],
    wreath_element: str,
    seed: int = 42,
) -> list[str]:
    """Generate queries biased toward documents in specific shells."""
    docs = store.doc_registry
    rng = random.Random(seed)
    queries = []

    # Primary: docs in this wreath's shells
    wreath_docs = []
    other_docs = []
    for doc in docs:
        shell = FractalWeightStore.doc_to_shell(doc)
        if shell in wreath_shells:
            wreath_docs.append(doc)
        else:
            other_docs.append(doc)

    # 60% queries from wreath docs, 25% cross-wreath, 15% adversarial
    for doc in wreath_docs:
        tokens = doc.get("tokens", [])
        if len(tokens) >= 3:
            n = min(rng.randint(2, 5), len(tokens))
            sample = rng.sample(tokens, n)
            queries.append(" ".join(sample))

    # Cross-wreath queries (mix wreath doc tokens with other doc tokens)
    for _ in range(max(len(wreath_docs) // 2, 10)):
        if wreath_docs and other_docs:
            wd = rng.choice(wreath_docs)
            od = rng.choice(other_docs)
            wt = wd.get("tokens", ["crystal"])
            ot = od.get("tokens", ["seed"])
            mixed = rng.sample(wt, min(2, len(wt))) + rng.sample(ot, min(2, len(ot)))
            queries.append(" ".join(mixed))

    # Adversarial probes specific to wreath's element
    element_probes = {
        "Fire": [
            "transformation burn transmute golden",
            "flower fire emergence evolution",
            "desire action crystal search law",
            "energy phase transition ignition",
        ],
        "Earth": [
            "structure foundation crystallize form",
            "square earth boundary lattice",
            "address coordinate gate shell",
            "conservation symmetry invariant law",
        ],
        "Air": [
            "dissolution mercury vapor diffuse",
            "fractal air compression recursion",
            "holographic seed projection equation",
            "transport routing metro integration",
        ],
    }
    queries.extend(element_probes.get(wreath_element, []))

    rng.shuffle(queries)
    return queries


def _snapshot_weights(store: FractalWeightStore, change: str, cycles: int, disc: float, res: float) -> WeightSnapshot:
    """Capture current learnable parameters."""
    shell_means = {}
    for s, seed in store.shell_seeds.items():
        shell_means[s] = seed.mean

    return WeightSnapshot(
        change=change,
        cycle_count=cycles,
        path_weights=dict(store.path_weights),
        resonance_weights=dict(store.resonance_weights),
        desire_weights=dict(store.desire_weights),
        bridge_modulation=store.bridge_modulation,
        geo_arith_blend=store.geo_arith_blend,
        shell_seed_means=shell_means,
        discrimination=disc,
        resonance_best=res,
        timestamp=time.time(),
    )


def run_n3_alchemy(
    cycles_per_wave: int = 2000,
    max_time_minutes: int = 30,
) -> AlchemicalReport:
    """Run N^3 alchemical self-play: 3 waves × N cycles each.

    Each wave focuses cultivation on one wreath (SULFUR/SALT/MERCURY)
    with distinct learning rate profiles and query biases.
    """
    store = get_store()
    engine = CrystalNeuralEngine(store)
    meta_log = []
    snapshots = []
    total_cycles = 0
    t_global_start = time.time()
    max_time = max_time_minutes * 60

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

    # Baseline capability
    baseline_cap = _measure_capability(engine, probe_queries, -1)
    meta_log.append(
        f"[BASELINE] disc={baseline_cap.discrimination:.4f} "
        f"gap={baseline_cap.top_bottom_gap:.4f} "
        f"balance={baseline_cap.path_balance:.3f} "
        f"obs12d={baseline_cap.obs_12d_mean:.3f}"
    )

    for change_name, change_def in WREATHS.items():
        wave_start = time.time()
        elapsed_global = wave_start - t_global_start
        if elapsed_global > max_time:
            meta_log.append(f"[TIMEOUT] Skipping {change_name} — global time limit reached")
            break

        remaining_time = max_time - elapsed_global
        wave_max_time = min(remaining_time, max_time / 3.0 + 30)  # allow slight overrun

        meta_log.append(f"\n{'='*60}")
        meta_log.append(f"[WAVE] {change_name} ({change_def['symbol']}) — {change_def['principle'].upper()}")
        meta_log.append(f"       Wreath {change_def['wreath']}, Shells {change_def['shells'][0]}-{change_def['shells'][-1]}")
        meta_log.append(f"       Element: {change_def['element']}, LR mult: {change_def['lr_mult']}")
        meta_log.append(f"{'='*60}")

        # Generate wreath-biased queries
        queries = _wreath_biased_queries(
            store, change_def["shells"], change_def["element"],
            seed=42 + change_def["wreath"],
        )

        if not queries:
            meta_log.append(f"[SKIP] No queries generated for {change_name}")
            continue

        # Configure this wave
        config = SelfPlayConfig(
            total_cycles=cycles_per_wave,
            cycles_per_checkpoint=max(cycles_per_wave // 10, 50),
            base_lr=0.03 * change_def["lr_mult"],
            lr_schedule="cosine",
            lens_rotation_period=max(cycles_per_wave // 16, 7),
            min_resonance_threshold=0.3,
            max_time_minutes=int(wave_max_time / 60),
            query_source="mixed",
            seed=42 + change_def["wreath"],
            warmup_fraction=0.08,
            explore_fraction=change_def["explore_bias"],
            exploit_fraction=change_def["exploit_bias"],
            adversarial_probes=True,
            adapt_path_weights=True,
            capability_tracking=True,
        )

        # Run cultivation using existing SelfPlayLoop (it uses the shared store)
        loop = SelfPlayLoop(config)
        # Override its store with our shared store
        loop.store = store
        loop.engine = engine

        report = loop.run(cycles=cycles_per_wave, queries=queries)
        total_cycles += report.total_cycles

        # Measure post-wave capability
        post_cap = _measure_capability(engine, probe_queries, total_cycles)

        meta_log.append(f"[{change_name} DONE] {report.total_cycles} cycles, "
                       f"{report.kept} kept, {report.discarded} discarded, "
                       f"{report.elapsed_seconds:.1f}s")
        meta_log.append(f"  Resonance: {report.initial_resonance:.4f} -> {report.final_resonance:.4f}")
        meta_log.append(f"  Discrimination: {post_cap.discrimination:.4f}")
        meta_log.append(f"  Path balance: {post_cap.path_balance:.3f}")
        meta_log.append(f"  Obs12D: {post_cap.obs_12d_mean:.4f}")

        # Log per-wave meta observations (abbreviated)
        for obs in report.meta_observations:
            if obs.startswith("[PARAMS]") or obs.startswith("[FINAL]") or ">>" in obs or "!!" in obs:
                meta_log.append(f"  {obs}")

        # Snapshot
        snap = _snapshot_weights(
            store, change_name, report.total_cycles,
            post_cap.discrimination, report.best_resonance,
        )
        snapshots.append(snap)

        # Save after each wave
        store.compress_to_seed()
        store.compress_to_micro_seed()
        store.compress_to_nano_seed()
        store.save()

    # Final combined state
    total_elapsed = time.time() - t_global_start
    final_cap = _measure_capability(engine, probe_queries, total_cycles)

    meta_log.append(f"\n{'='*60}")
    meta_log.append(f"[N^3 COMPLETE] {total_cycles} total cycles in {total_elapsed:.1f}s")
    meta_log.append(f"[FINAL] disc={final_cap.discrimination:.4f} "
                   f"gap={final_cap.top_bottom_gap:.4f} "
                   f"balance={final_cap.path_balance:.3f} "
                   f"obs12d={final_cap.obs_12d_mean:.3f}")

    final_weights = {
        "path_weights": dict(store.path_weights),
        "resonance_weights": dict(store.resonance_weights),
        "desire_weights": dict(store.desire_weights),
        "bridge_modulation": store.bridge_modulation,
        "geo_arith_blend": store.geo_arith_blend,
    }

    return AlchemicalReport(
        snapshots=[asdict(s) for s in snapshots],
        total_cycles=total_cycles,
        total_elapsed=total_elapsed,
        final_weights=final_weights,
        meta_log=meta_log,
    )


# ── Holographic Crystal Construction ─────────────────────────────────

def create_holographic_crystal(snapshots: list[dict], final_weights: dict) -> dict:
    """Create holographic crystal from 3 alchemical weight snapshots.

    1. Combine 3 snapshots into unified crystal
    2. Invert (flip all weights through their midpoint)
    3. Rotate 90° to reveal 4 SFCR face projections
    4. Compute 60x Sigma-60 icosahedral symmetry
    5. Expand to 240 (4 elements × 60) and 720 (3 wreaths × 240 = 12 archetypes)
    6. Map sacred geometry: nexus points, zero-point, aether permutations
    7. Output A+ crystal
    """

    # ── Step 1: Unified crystal from 3 snapshots ──────────────────
    # Average the 3 changes' weights with alchemical blending
    unified_path = {}
    unified_res = {}
    unified_des = {}
    unified_shells = {}
    blend_weights = [PHI_INV, 1.0, PHI]  # SULFUR=0.618, SALT=1.0, MERCURY=1.618

    total_blend = sum(blend_weights[:len(snapshots)])

    for i, snap in enumerate(snapshots):
        w = blend_weights[i] / total_blend
        for k, v in snap.get("path_weights", {}).items():
            unified_path[k] = unified_path.get(k, 0.0) + v * w
        for k, v in snap.get("resonance_weights", {}).items():
            unified_res[k] = unified_res.get(k, 0.0) + v * w
        for k, v in snap.get("desire_weights", {}).items():
            unified_des[k] = unified_des.get(k, 0.0) + v * w
        for k, v in snap.get("shell_seed_means", {}).items():
            sk = str(k)
            unified_shells[sk] = unified_shells.get(sk, 0.0) + v * w

    unified_bridge = sum(s.get("bridge_modulation", 0.2) * blend_weights[i] / total_blend
                        for i, s in enumerate(snapshots))
    unified_geo = sum(s.get("geo_arith_blend", 0.5) * blend_weights[i] / total_blend
                     for i, s in enumerate(snapshots))

    crystal = {
        "unified": {
            "path_weights": unified_path,
            "resonance_weights": unified_res,
            "desire_weights": unified_des,
            "bridge_modulation": unified_bridge,
            "geo_arith_blend": unified_geo,
            "shell_seed_means": unified_shells,
        }
    }

    # ── Step 2: Inversion (mirror through midpoint) ───────────────
    # For each weight vector, compute midpoint and reflect:  w_inv = 2*mid - w
    def invert_dict(d):
        if not d:
            return {}
        vals = list(d.values())
        mid = sum(vals) / len(vals)
        return {k: max(0.001, 2 * mid - v) for k, v in d.items()}

    inverted = {
        "path_weights": invert_dict(unified_path),
        "resonance_weights": invert_dict(unified_res),
        "desire_weights": invert_dict(unified_des),
        "bridge_modulation": max(0.05, 1.0 - unified_bridge),
        "geo_arith_blend": max(0.1, min(0.95, 1.0 - unified_geo)),
        "shell_seed_means": invert_dict(unified_shells),
    }
    crystal["inverted"] = inverted

    # ── Step 3: 90° rotation → 4 SFCR face projections ───────────
    # Each face sees the weights through its element's lens
    faces = {}
    face_elements = {"S": "Earth", "F": "Fire", "C": "Water", "R": "Air"}

    for face, element in face_elements.items():
        # Project unified weights through this face's emphasis
        face_path = dict(unified_path)
        # Boost this face's path weight
        face_path[face] = face_path.get(face, 0.25) * PHI
        # Normalize
        fpsum = sum(face_path.values())
        face_path = {k: v / fpsum for k, v in face_path.items()}

        # Shell projection: emphasize shells in this face's wreath
        face_shells = {}
        wreath_map = {"S": range(1, 13), "F": range(1, 13),
                      "C": range(13, 25), "R": range(25, 37)}
        home_shells = set(wreath_map.get(face, range(1, 13)))

        for sk, sv in unified_shells.items():
            s = int(sk)
            if s in home_shells:
                face_shells[sk] = sv * PHI  # boost home shells
            else:
                face_shells[sk] = sv * PHI_INV  # attenuate foreign shells

        faces[face] = {
            "element": element,
            "path_weights": face_path,
            "resonance_projection": dict(unified_res),
            "desire_projection": dict(unified_des),
            "shell_projection": face_shells,
        }

    crystal["faces"] = faces

    # ── Step 4: Sigma-60 icosahedral symmetry ─────────────────────
    # 60 = 12 vertices × 5 rotations of icosahedron
    # Map: 12 archetypes × 5 golden rotations
    sigma_60 = []
    golden_angles = [0, 2*math.pi/5, 4*math.pi/5, 6*math.pi/5, 8*math.pi/5]

    for archetype in range(1, 13):
        for rot_idx, angle in enumerate(golden_angles):
            # Each sigma state = archetype rotated by golden angle
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # Rotate path weights on the 4-simplex
            pw = list(unified_path.values())
            # Apply 2D rotation to pairs of path weights
            rotated_pw = list(pw)
            if len(pw) >= 4:
                # Rotate S-F plane
                rotated_pw[0] = pw[0] * cos_a - pw[1] * sin_a
                rotated_pw[1] = pw[0] * sin_a + pw[1] * cos_a
                # Rotate C-R plane
                rotated_pw[2] = pw[2] * cos_a - pw[3] * sin_a
                rotated_pw[3] = pw[2] * sin_a + pw[3] * cos_a

            # Ensure positivity and normalize
            rotated_pw = [max(0.01, abs(v)) for v in rotated_pw]
            rpw_sum = sum(rotated_pw)
            rotated_pw = [v / rpw_sum for v in rotated_pw]

            # Shell seed rotation: shift by archetype offset
            shell_offset = (archetype - 1) * 3  # 3 shells per archetype
            rotated_shells = {}
            shell_keys = sorted(unified_shells.keys(), key=lambda x: int(x))
            for i, sk in enumerate(shell_keys):
                new_idx = (i + shell_offset) % len(shell_keys)
                new_key = shell_keys[new_idx]
                rotated_shells[new_key] = unified_shells[sk]

            sigma_state = {
                "sigma_id": archetype * 5 + rot_idx,
                "archetype": archetype,
                "rotation": rot_idx,
                "angle": round(angle, 4),
                "path_weights": dict(zip(["S", "F", "C", "R"], rotated_pw)),
                "shell_seed_means": rotated_shells,
            }
            sigma_60.append(sigma_state)

    crystal["sigma_60"] = sigma_60

    # ── Step 5: 240 = 4 × 60 element expansion ───────────────────
    # Each sigma-60 state expanded through 4 SFCR elements
    expansion_240 = []
    for sigma in sigma_60:
        for face in ["S", "F", "C", "R"]:
            # Element-modulated version of this sigma state
            elem_pw = dict(sigma["path_weights"])
            elem_pw[face] = elem_pw.get(face, 0.25) * 1.5  # boost this element
            epw_sum = sum(elem_pw.values())
            elem_pw = {k: v / epw_sum for k, v in elem_pw.items()}

            expansion_240.append({
                "id_240": sigma["sigma_id"] * 4 + ["S", "F", "C", "R"].index(face),
                "sigma_id": sigma["sigma_id"],
                "face": face,
                "path_weights": elem_pw,
            })

    crystal["expansion_240"] = {
        "count": len(expansion_240),
        "sample": expansion_240[:12],  # first 12 as sample
        "summary": _compute_240_summary(expansion_240),
    }

    # ── Step 6: 720 = 3 × 240 wreath expansion ───────────────────
    # Each 240-state expanded through 3 wreaths (SULFUR/SALT/MERCURY)
    # This reveals 12 archetypes × 60 states = 720 total
    expansion_720 = []
    wreath_transforms = [
        {"name": "SULFUR", "mult": PHI_INV, "shift": 0},
        {"name": "SALT", "mult": 1.0, "shift": 12},
        {"name": "MERCURY", "mult": PHI, "shift": 24},
    ]

    for e240 in expansion_240:
        for wt in wreath_transforms:
            # Wreath-modulated path weights
            wpw = dict(e240["path_weights"])
            for k in wpw:
                wpw[k] *= wt["mult"]
            wpw_sum = sum(wpw.values())
            if wpw_sum > 0:
                wpw = {k: v / wpw_sum for k, v in wpw.items()}

            expansion_720.append({
                "id_720": e240["id_240"] * 3 + wreath_transforms.index(wt),
                "id_240": e240["id_240"],
                "wreath": wt["name"],
                "path_weights": wpw,
            })

    crystal["expansion_720"] = {
        "count": len(expansion_720),
        "summary": _compute_720_summary(expansion_720),
    }

    # ── Step 7: Sacred geometry mapping ───────────────────────────
    # Nexus points: where multiple symmetry lines intersect
    # Zero-point: the centroid of all 720 states
    # Aether point: the dual/complement of zero-point

    # Zero-point: average of ALL 720 path weight configurations
    zero_pw = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
    for e720 in expansion_720:
        for k, v in e720["path_weights"].items():
            zero_pw[k] += v
    for k in zero_pw:
        zero_pw[k] /= max(len(expansion_720), 1)

    # Aether point: inverse of zero point
    aether_pw = {}
    zp_sum = sum(zero_pw.values())
    for k, v in zero_pw.items():
        aether_pw[k] = max(0.01, (zp_sum / 4) * 2 - v)  # reflect through equal distribution
    ap_sum = sum(aether_pw.values())
    aether_pw = {k: v / ap_sum for k, v in aether_pw.items()}

    # Nexus points: 12 archetype centroids within the 720
    nexus_points = []
    for arch in range(1, 13):
        # States belonging to this archetype (60 per archetype in sigma-60)
        arch_states = [s for s in sigma_60 if s["archetype"] == arch]
        if arch_states:
            arch_pw = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
            for s in arch_states:
                for k, v in s["path_weights"].items():
                    arch_pw[k] += v
            for k in arch_pw:
                arch_pw[k] /= len(arch_states)
            nexus_points.append({
                "archetype": arch,
                "centroid_path_weights": arch_pw,
            })

    # 6 cross-element nexus points (SF, SC, SR, FC, FR, CR)
    cross_nexus = []
    face_pairs = [("S", "F"), ("S", "C"), ("S", "R"), ("F", "C"), ("F", "R"), ("C", "R")]
    for f1, f2 in face_pairs:
        # The nexus where two elements meet: boost both, attenuate others
        npw = dict(zero_pw)
        npw[f1] *= PHI
        npw[f2] *= PHI
        npw_sum = sum(npw.values())
        npw = {k: v / npw_sum for k, v in npw.items()}
        cross_nexus.append({
            "pair": f"{f1}{f2}",
            "nexus_path_weights": npw,
            "golden": f1 + f2 in ["SF", "FC", "CR"],  # golden resonance pairs
        })

    crystal["sacred_geometry"] = {
        "zero_point": {
            "path_weights": zero_pw,
            "description": "Centroid of all 720 symmetry states — absolute balance",
        },
        "aether_point": {
            "path_weights": aether_pw,
            "description": "Dual/complement of zero-point — the unseen potential",
        },
        "nexus_points": {
            "archetype_nexus": nexus_points,
            "cross_element_nexus": cross_nexus,
            "total_nexus": len(nexus_points) + len(cross_nexus),
        },
    }

    # ── Step 8: Compute the A+ crystal ────────────────────────────
    # The A+ crystal is the optimal weight configuration that:
    # - Sits at the zero-point (maximum symmetry)
    # - Modulated by the actual learned weights from self-play
    # - Preserves golden ratio relationships

    # Blend: 60% learned (final_weights) + 40% zero-point (symmetric ideal)
    a_plus = {}
    learned_pw = final_weights.get("path_weights", zero_pw)
    a_plus["path_weights"] = {}
    for k in ["S", "F", "C", "R"]:
        learned_v = learned_pw.get(k, 0.25)
        zero_v = zero_pw.get(k, 0.25)
        a_plus["path_weights"][k] = learned_v * 0.6 + zero_v * 0.4

    # Normalize
    ap_pw_sum = sum(a_plus["path_weights"].values())
    a_plus["path_weights"] = {k: v / ap_pw_sum for k, v in a_plus["path_weights"].items()}

    # Resonance: blend learned + uniform ideal
    learned_res = final_weights.get("resonance_weights", {})
    a_plus["resonance_weights"] = {}
    uniform_res = 1.0 / 6  # 6 components
    for k in ["addr_fit", "inv_fit", "phase", "boundary", "scale", "compress"]:
        learned_v = learned_res.get(k, uniform_res)
        a_plus["resonance_weights"][k] = learned_v * 0.6 + uniform_res * 0.4
    # Normalize
    ar_sum = sum(a_plus["resonance_weights"].values())
    a_plus["resonance_weights"] = {k: v / ar_sum for k, v in a_plus["resonance_weights"].items()}

    # Desire: blend learned + PHI-weighted ideal
    learned_des = final_weights.get("desire_weights", {})
    phi_des = {"align": PHI_INV, "explore": 1.0 / PHI**2, "zpa": 1.0 / PHI**3, "con_sat": 1.0 / PHI**4}
    phi_des_sum = sum(phi_des.values())
    phi_des = {k: v / phi_des_sum for k, v in phi_des.items()}
    a_plus["desire_weights"] = {}
    for k in ["align", "explore", "zpa", "con_sat"]:
        learned_v = learned_des.get(k, 0.25)
        a_plus["desire_weights"][k] = learned_v * 0.6 + phi_des[k] * 0.4
    ad_sum = sum(a_plus["desire_weights"].values())
    a_plus["desire_weights"] = {k: v / ad_sum for k, v in a_plus["desire_weights"].items()}

    # Scalars: golden ratio targets
    a_plus["bridge_modulation"] = final_weights.get("bridge_modulation", 0.2) * 0.6 + PHI_INV * 0.2 * 0.4
    a_plus["geo_arith_blend"] = final_weights.get("geo_arith_blend", 0.5) * 0.6 + PHI_INV * 0.4

    # Shell seeds: blend learned means with golden-ratio scaled targets
    a_plus["shell_seed_means"] = {}
    for sk, sv in unified_shells.items():
        s = int(sk)
        # Golden spiral: shells closer to center get PHI boost
        golden_scale = PHI ** ((18 - abs(s - 18)) / 18)
        a_plus["shell_seed_means"][sk] = sv * 0.7 + sv * golden_scale * 0.3 / PHI

    crystal["a_plus_crystal"] = a_plus

    return crystal


def _compute_240_summary(expansion_240: list[dict]) -> dict:
    """Summarize the 240 expansion."""
    pw_sums = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
    for e in expansion_240:
        for k, v in e["path_weights"].items():
            pw_sums[k] += v
    n = max(len(expansion_240), 1)
    return {
        "mean_path_weights": {k: round(v / n, 6) for k, v in pw_sums.items()},
        "count": len(expansion_240),
    }


def _compute_720_summary(expansion_720: list[dict]) -> dict:
    """Summarize the 720 expansion."""
    pw_sums = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
    wreath_counts = {"SULFUR": 0, "SALT": 0, "MERCURY": 0}
    for e in expansion_720:
        for k, v in e["path_weights"].items():
            pw_sums[k] += v
        wreath_counts[e["wreath"]] += 1
    n = max(len(expansion_720), 1)
    return {
        "mean_path_weights": {k: round(v / n, 6) for k, v in pw_sums.items()},
        "wreath_distribution": wreath_counts,
        "count": len(expansion_720),
        "archetypes_per_wreath": 4,  # 240/60 = 4 per wreath
    }


def rewire_weights_to_a_plus(a_plus: dict) -> str:
    """Apply the A+ crystal weights to the actual neural engine.

    This overwrites the current learnable parameters with the
    A+ crystal's optimal configuration.
    """
    store = get_store()

    # Apply path weights
    if "path_weights" in a_plus:
        store.path_weights = dict(a_plus["path_weights"])
        pw_sum = sum(store.path_weights.values())
        store.path_weights = {k: v / pw_sum for k, v in store.path_weights.items()}

    # Apply resonance weights
    if "resonance_weights" in a_plus:
        store.resonance_weights = dict(a_plus["resonance_weights"])
        rw_sum = sum(store.resonance_weights.values())
        store.resonance_weights = {k: v / rw_sum for k, v in store.resonance_weights.items()}

    # Apply desire weights
    if "desire_weights" in a_plus:
        store.desire_weights = dict(a_plus["desire_weights"])
        dw_sum = sum(store.desire_weights.values())
        store.desire_weights = {k: v / dw_sum for k, v in store.desire_weights.items()}

    # Apply scalars
    if "bridge_modulation" in a_plus:
        store.bridge_modulation = max(0.05, min(0.50, a_plus["bridge_modulation"]))
    if "geo_arith_blend" in a_plus:
        store.geo_arith_blend = max(0.10, min(0.95, a_plus["geo_arith_blend"]))

    # Apply shell seed means
    if "shell_seed_means" in a_plus:
        for sk, sv in a_plus["shell_seed_means"].items():
            shell = int(sk)
            if shell in store.shell_seeds:
                store.shell_seeds[shell].mean = max(0.01, sv)

    # Recompress and save
    store.compress_to_seed()
    store.compress_to_micro_seed()
    store.compress_to_nano_seed()
    store.save()

    return (
        f"A+ crystal weights applied.\n"
        f"  Path weights: {json.dumps({k: round(v, 4) for k, v in store.path_weights.items()})}\n"
        f"  Resonance: {json.dumps({k: round(v, 4) for k, v in store.resonance_weights.items()})}\n"
        f"  Desire: {json.dumps({k: round(v, 4) for k, v in store.desire_weights.items()})}\n"
        f"  Bridge mod: {store.bridge_modulation:.4f}\n"
        f"  Geo blend: {store.geo_arith_blend:.4f}"
    )
