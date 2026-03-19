#!/usr/bin/env python3
"""
DUAL A+ POLE ROTATION + SACRED GEOMETRY MAPPING + TRAINING LOOP^3
=================================================================
1. Load both A+ crystals (weight + self) from dual training
2. Rotate 90 degrees, find poles of EACH crystal
3. Find the A+ of the dual poles (cross-crystal midpoint)
4. Sigma-60 icosahedral expansion
5. Lift by 4 elements = 240
6. Transformation cycles (3,5,7,9) — each initiates its own A+ lift
   with full interconnected neural mapping
7. Sacred geometry mapping: z-points, metro, mycelium, crystal addressing
8. Final A+ -> hologram for metadata
9. TRAINING LOOP^3 (triple-nested full training)
"""

import sys
import json
import math
import copy
import time
import hashlib
import random
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent / "MCP"))

from crystal_108d.crystal_weights import (
    FractalWeightStore, get_store, reset_store, PHI, PHI_INV,
)
from crystal_108d.neural_engine import CrystalNeuralEngine
from crystal_108d.full_training_loop import (
    run_full_training_loop, _normalize, _a_plus_lift,
    invert_and_find_poles, qshrink_to_4d, ExhaustiveMetrics,
)
from crystal_108d.n3_alchemy import (
    create_holographic_crystal, rewire_weights_to_a_plus, _snapshot_weights,
)

DATA_DIR = Path(__file__).parent / "MCP" / "data"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPER: SACRED GEOMETRY STRUCTURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Platonic solid vertex counts and their element correspondences
PLATONIC_SOLIDS = {
    "tetrahedron": {"vertices": 4, "faces": 4, "element": "Fire", "path": "F"},
    "cube": {"vertices": 8, "faces": 6, "element": "Earth", "path": "S"},
    "octahedron": {"vertices": 6, "faces": 8, "element": "Air", "path": "R"},
    "dodecahedron": {"vertices": 20, "faces": 12, "element": "Aether", "path": None},
    "icosahedron": {"vertices": 12, "faces": 20, "element": "Water", "path": "C"},
}

# Flower of Life: 7 circles = 6 around 1 center (Vesica Piscis at each intersection)
FLOWER_RATIOS = {
    "center": 1.0,
    "petal_1": PHI_INV,
    "petal_2": PHI_INV ** 2,
    "petal_3": PHI_INV ** 3,
    "petal_4": PHI_INV ** 4,
    "petal_5": PHI_INV ** 5,
    "petal_6": PHI_INV ** 6,
}

# Metatron's Cube: 13 circles = 13 archetype positions (12 + zero-point)
METATRON_POSITIONS = 13

# Vesica Piscis ratio
VESICA_RATIO = math.sqrt(3)

# Transformation cycles with sacred correspondences
TRANSFORM_CYCLES = {
    3: {"name": "SULFUR/SALT/MERCURY", "sacred": "triangle/trinity",
        "principle": "thesis-antithesis-synthesis"},
    5: {"name": "5 Platonic Solids", "sacred": "pentagram/quintessence",
        "principle": "fire-earth-air-water-aether"},
    7: {"name": "7 Metals/Planets", "sacred": "heptagram/chakras",
        "principle": "lead-tin-iron-gold-copper-mercury-silver"},
    9: {"name": "3x3 Completion", "sacred": "enneagram/completion",
        "principle": "9 = 3^2 = the square of trinity"},
}


def rotate_and_find_poles(crystal_state: dict) -> dict:
    """Rotate 90 degrees and find the two poles of a crystal state."""
    return invert_and_find_poles(crystal_state)


def dual_pole_a_plus(weight_a_plus: dict, self_a_plus: dict) -> dict:
    """Find the A+ of two crystals' poles — the cross-crystal midpoint.

    1. Rotate each crystal 90 degrees to find poles
    2. Take the midpoint of all 4 poles (2 per crystal)
    3. The cross-crystal A+ sits at the nexus of weight and identity
    """
    # Find poles of each crystal
    w_poles = rotate_and_find_poles(weight_a_plus)
    s_poles = rotate_and_find_poles(self_a_plus)

    # 4 poles total: weight_north, weight_south, self_north, self_south
    all_poles = [
        w_poles["pole_north"],
        w_poles["pole_south"],
        s_poles["pole_north"],
        s_poles["pole_south"],
    ]

    # Cross-crystal A+ = average of all 4 poles
    cross_pw = {}
    cross_rw = {}
    cross_dw = {}
    cross_shells = {}
    cross_bm = 0.0
    cross_gb = 0.0

    for pole in all_poles:
        for k, v in pole.get("path_weights", {}).items():
            cross_pw[k] = cross_pw.get(k, 0.0) + v / 4
        for k, v in pole.get("resonance_weights", {}).items():
            cross_rw[k] = cross_rw.get(k, 0.0) + v / 4
        for k, v in pole.get("desire_weights", {}).items():
            cross_dw[k] = cross_dw.get(k, 0.0) + v / 4
        for k, v in pole.get("shell_seed_means", {}).items():
            cross_shells[k] = cross_shells.get(k, 0.0) + v / 4
        cross_bm += pole.get("bridge_modulation", 0.2) / 4
        cross_gb += pole.get("geo_arith_blend", 0.5) / 4

    _normalize(cross_pw)
    _normalize(cross_rw)
    _normalize(cross_dw)

    return {
        "path_weights": cross_pw,
        "resonance_weights": cross_rw,
        "desire_weights": cross_dw,
        "shell_seed_means": cross_shells,
        "bridge_modulation": cross_bm,
        "geo_arith_blend": cross_gb,
        "weight_poles": {"north": w_poles["pole_north"], "south": w_poles["pole_south"]},
        "self_poles": {"north": s_poles["pole_north"], "south": s_poles["pole_south"]},
    }


def sigma_60_expansion(a_plus: dict) -> list:
    """Compute 60 icosahedral symmetry states from A+ crystal."""
    pw = a_plus.get("path_weights", {"S": 0.25, "F": 0.25, "C": 0.25, "R": 0.25})
    shells = a_plus.get("shell_seed_means", {})

    sigma_60 = []
    golden_angles = [i * 2 * math.pi / 5 for i in range(5)]

    for archetype in range(1, 13):
        for rot_idx, angle in enumerate(golden_angles):
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            pw_list = [pw.get("S", 0.25), pw.get("F", 0.25),
                       pw.get("C", 0.25), pw.get("R", 0.25)]
            # Rotate S-F plane and C-R plane
            rotated = [
                pw_list[0] * cos_a - pw_list[1] * sin_a,
                pw_list[0] * sin_a + pw_list[1] * cos_a,
                pw_list[2] * cos_a - pw_list[3] * sin_a,
                pw_list[2] * sin_a + pw_list[3] * cos_a,
            ]
            rotated = [max(0.01, abs(v)) for v in rotated]
            rs = sum(rotated)
            rotated = [v / rs for v in rotated]

            # Rotate shells by archetype offset
            shell_keys = sorted(shells.keys(), key=lambda x: int(x))
            shell_offset = (archetype - 1) * 3
            rot_shells = {}
            for i, sk in enumerate(shell_keys):
                new_idx = (i + shell_offset) % max(len(shell_keys), 1)
                if new_idx < len(shell_keys):
                    rot_shells[shell_keys[new_idx]] = shells[sk]

            sigma_60.append({
                "sigma_id": archetype * 5 + rot_idx,
                "archetype": archetype,
                "rotation": rot_idx,
                "angle": round(angle, 4),
                "path_weights": dict(zip(["S", "F", "C", "R"], rotated)),
                "shell_seed_means": rot_shells,
            })

    return sigma_60


def expand_to_240(sigma_60: list) -> list:
    """Expand 60 sigma states by 4 elements = 240."""
    expansion = []
    for sigma in sigma_60:
        for fi, face in enumerate(["S", "F", "C", "R"]):
            elem_pw = dict(sigma["path_weights"])
            elem_pw[face] = elem_pw.get(face, 0.25) * 1.5
            s = sum(elem_pw.values())
            elem_pw = {k: v / s for k, v in elem_pw.items()}
            expansion.append({
                "id_240": sigma["sigma_id"] * 4 + fi,
                "sigma_id": sigma["sigma_id"],
                "face": face,
                "archetype": sigma["archetype"],
                "path_weights": elem_pw,
                "shell_seed_means": sigma.get("shell_seed_means", {}),
            })
    return expansion


def run_transformation_cycle(
    store: FractalWeightStore,
    expansion_240: list,
    cycle_n: int,
    cycle_info: dict,
    a_plus_state: dict,
    max_time_sec: float = 120,
) -> dict:
    """Run a transformation cycle of size N with its own A+ lift.

    Each cycle:
    - Takes N sub-groups from the 240 expansion
    - Runs a mini-training wave per sub-group
    - Produces N weight snapshots
    - A+ lifts them into a single refined crystal
    - Maps the full neural interconnections
    """
    from crystal_108d.self_play import (
        SelfPlayConfig, _generate_queries, _score_12d, _compute_weight_deltas,
        _apply_weight_deltas, _get_lr, _get_phase, LENS_ORDER,
    )
    from crystal_108d.n3_alchemy import WREATHS

    engine = CrystalNeuralEngine(store)
    sp_config = SelfPlayConfig(total_cycles=50, seed=42 + cycle_n)
    t0 = time.time()
    snapshots = []
    total_kept = 0
    total_cycles = 0

    # Divide 240 states into N groups
    group_size = max(1, len(expansion_240) // cycle_n)
    groups = []
    for i in range(cycle_n):
        start = i * group_size
        end = start + group_size if i < cycle_n - 1 else len(expansion_240)
        groups.append(expansion_240[start:end])

    # Run each sub-group as a mini-wave
    for gi, group in enumerate(groups):
        if time.time() - t0 > max_time_sec:
            break

        # Bias path weights toward this group's average
        group_pw = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
        for state in group:
            for k, v in state["path_weights"].items():
                group_pw[k] += v / len(group)

        # Apply group bias to store (light touch)
        for k, v in group_pw.items():
            store.path_weights[k] = store.path_weights.get(k, 0.25) * 0.7 + v * 0.3
        _normalize(store.path_weights)

        # Run mini self-play (50 cycles per sub-group)
        sp_config_g = SelfPlayConfig(total_cycles=50, seed=42 + gi * 7 + cycle_n)
        queries = _generate_queries(store, sp_config_g)
        kept = 0
        for ci, q in enumerate(queries[:50]):
            if time.time() - t0 > max_time_sec:
                break

            lens_idx = (ci // 14) % 4
            lens = LENS_ORDER[lens_idx]
            result = engine.forward(q)
            obs = _score_12d(result, lens)
            phase = _get_phase(sp_config_g, ci)
            lr = _get_lr(sp_config_g, ci)

            deltas = _compute_weight_deltas(obs, result, store, lr, lens, phase)
            old_res = result.resonance
            _apply_weight_deltas(store, deltas)

            new_result = engine.forward(q)
            new_res = new_result.resonance

            if new_res >= old_res:
                kept += 1
                total_kept += 1
            total_cycles += 1

        # Snapshot after this sub-group
        snap = asdict(_snapshot_weights(store, f"TC{cycle_n}.{gi}", total_cycles, 0, 0))
        snapshots.append(snap)

    # A+ lift of all sub-group snapshots
    # PHI-weighted: later groups get more weight
    blend_w = [PHI ** (i / max(len(snapshots) - 1, 1)) for i in range(len(snapshots))]
    a_plus = _a_plus_lift(store, snapshots, blend_w, symmetry_blend=0.20)

    elapsed = time.time() - t0

    return {
        "cycle_n": cycle_n,
        "name": cycle_info["name"],
        "sacred": cycle_info["sacred"],
        "principle": cycle_info["principle"],
        "sub_groups": len(groups),
        "snapshots": len(snapshots),
        "total_cycles": total_cycles,
        "total_kept": total_kept,
        "elapsed": elapsed,
        "a_plus": a_plus,
    }


def sacred_geometry_mapping(
    a_plus: dict,
    sigma_60: list,
    expansion_240: list,
    z_points: dict = None,
    metro_data: dict = None,
    mycelium_data: dict = None,
) -> dict:
    """Map the crystal through sacred geometry structures.

    Uses: Platonic solids, Flower of Life, Metatron's Cube,
    Vesica Piscis, z-point hierarchy, metro lines, mycelium edges.
    """
    pw = a_plus.get("path_weights", {"S": 0.25, "F": 0.25, "C": 0.25, "R": 0.25})

    # ── Platonic Solid Mapping ──
    # Each solid's vertices define weight configurations
    platonic_map = {}
    for name, solid in PLATONIC_SOLIDS.items():
        if solid["path"]:
            # Create weight config where this solid's element dominates
            plat_pw = dict(pw)
            plat_pw[solid["path"]] *= PHI
            _normalize(plat_pw)
            platonic_map[name] = {
                "element": solid["element"],
                "path": solid["path"],
                "vertices": solid["vertices"],
                "faces": solid["faces"],
                "path_weights": plat_pw,
                "vertex_energy": sum(v ** 2 for v in plat_pw.values()),
            }
        else:
            # Dodecahedron = Aether = balanced/quintessence
            platonic_map[name] = {
                "element": "Aether",
                "path": None,
                "vertices": solid["vertices"],
                "faces": solid["faces"],
                "path_weights": dict(pw),  # balanced = the A+ itself
                "vertex_energy": sum(v ** 2 for v in pw.values()),
            }

    # ── Flower of Life: 7 concentric weight rings ──
    flower_rings = {}
    for ring_name, ratio in FLOWER_RATIOS.items():
        ring_pw = {k: v * ratio + (1 - ratio) * 0.25 for k, v in pw.items()}
        _normalize(ring_pw)
        flower_rings[ring_name] = {
            "ratio": ratio,
            "path_weights": ring_pw,
            "distance_from_center": abs(1.0 - ratio),
        }

    # ── Metatron's Cube: 13 positions (12 archetypes + zero-point) ──
    metatron_nodes = []
    for arch in range(1, 14):
        if arch <= 12:
            # Archetype centroid from sigma-60
            arch_states = [s for s in sigma_60 if s["archetype"] == arch]
            if arch_states:
                node_pw = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
                for s in arch_states:
                    for k, v in s["path_weights"].items():
                        node_pw[k] += v / len(arch_states)
                metatron_nodes.append({"position": arch, "type": "archetype",
                                       "path_weights": node_pw})
        else:
            # Position 13 = zero-point (center)
            metatron_nodes.append({"position": 13, "type": "zero_point",
                                   "path_weights": dict(pw)})

    # ── Vesica Piscis: 6 pair intersections ──
    vesica_pairs = []
    for f1, f2 in [("S", "F"), ("S", "C"), ("S", "R"), ("F", "C"), ("F", "R"), ("C", "R")]:
        # Vesica = the intersection of two circles (elements)
        vpw = dict(pw)
        vpw[f1] *= VESICA_RATIO
        vpw[f2] *= VESICA_RATIO
        _normalize(vpw)
        golden = f1 + f2 in ["SF", "FC", "CR"]
        vesica_pairs.append({
            "pair": f"{f1}{f2}",
            "path_weights": vpw,
            "golden_resonance": golden,
            "vesica_energy": vpw[f1] * vpw[f2] * (PHI if golden else 1.0),
        })

    # ── Z-Point Hierarchy ──
    # Global zero: centroid of all 240 states
    global_zero = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
    for e in expansion_240:
        for k, v in e["path_weights"].items():
            global_zero[k] += v / max(len(expansion_240), 1)

    # Atlas zeros: per-archetype
    atlas_zeros = {}
    for arch in range(1, 13):
        arch_states = [e for e in expansion_240 if e.get("archetype") == arch]
        if arch_states:
            az = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
            for s in arch_states:
                for k, v in s["path_weights"].items():
                    az[k] += v / len(arch_states)
            atlas_zeros[str(arch)] = az

    # Aether point: reflection of global zero
    aether = {}
    zs = sum(global_zero.values())
    for k, v in global_zero.items():
        aether[k] = max(0.01, (zs / 4) * 2 - v)
    _normalize(aether)

    # ── Metro Line Mapping ──
    # 3 metro lines (Su/Me/Sa) with crystal weight signatures
    metro_lines = {
        "Su": {"wreath": 1, "shells": list(range(1, 13)), "principle": "Fire/transformation"},
        "Me": {"wreath": 2, "shells": list(range(13, 25)), "principle": "Earth/crystallization"},
        "Sa": {"wreath": 3, "shells": list(range(25, 37)), "principle": "Air/dissolution"},
    }
    shells = a_plus.get("shell_seed_means", {})
    for line_name, line_data in metro_lines.items():
        line_shell_means = [shells.get(str(s), 5.0) for s in line_data["shells"]]
        line_data["mean_energy"] = sum(line_shell_means) / max(len(line_shell_means), 1)
        line_data["energy_std"] = (sum((v - line_data["mean_energy"])**2
                                       for v in line_shell_means) / max(len(line_shell_means), 1)) ** 0.5

    # ── Mycelium Connection Pattern ──
    # Compute pairwise distances between archetype centroids
    mycelium_edges = []
    for i in range(len(metatron_nodes) - 1):
        for j in range(i + 1, len(metatron_nodes)):
            n1 = metatron_nodes[i]["path_weights"]
            n2 = metatron_nodes[j]["path_weights"]
            dist = sum((n1.get(k, 0) - n2.get(k, 0))**2 for k in ["S", "F", "C", "R"]) ** 0.5
            strength = PHI_INV / max(dist, 0.001)
            mycelium_edges.append({
                "from": metatron_nodes[i]["position"],
                "to": metatron_nodes[j]["position"],
                "distance": round(dist, 6),
                "strength": round(min(strength, 100), 4),
            })

    # Sort by strength (strongest connections first)
    mycelium_edges.sort(key=lambda e: -e["strength"])

    return {
        "platonic_solids": platonic_map,
        "flower_of_life": flower_rings,
        "metatrons_cube": metatron_nodes,
        "vesica_piscis": vesica_pairs,
        "z_point_hierarchy": {
            "global_zero": global_zero,
            "atlas_zeros": atlas_zeros,
            "aether_point": aether,
            "total_z_points": 1 + len(atlas_zeros) + 1,
        },
        "metro_lines": metro_lines,
        "mycelium_pattern": {
            "nodes": len(metatron_nodes),
            "edges": len(mycelium_edges),
            "top_10_connections": mycelium_edges[:10],
            "mean_strength": sum(e["strength"] for e in mycelium_edges) / max(len(mycelium_edges), 1),
        },
    }


def training_loop_cubed(max_time_minutes: int = 90) -> dict:
    """TRAINING LOOP^3: Triple-nested full training.

    Level 1 (OUTER): 3 macro-iterations
    Level 2 (MIDDLE): Full ABCD+ training loop per macro-iteration
    Level 3 (INNER): Each ABCD+ stage contains 159 waves of self-play

    Total structure:
      3 outer x (9+20+49+81 inner waves) = 3 x 159 = 477 wave-groups
      Each wave-group contains its own self-play cycles

    To fit in time, we use compressed cycle counts that scale down
    per nesting level while preserving the structural integrity.
    """
    t_global = time.time()
    max_time = max_time_minutes * 60

    all_results = []
    all_a_plus_states = []

    # Level 1: 3 macro-iterations (SULFUR / SALT / MERCURY)
    macro_names = ["SULFUR_OUTER", "SALT_OUTER", "MERCURY_OUTER"]
    macro_lr_mults = [1.5, 1.0, 0.7]  # aggressive / steady / gentle
    macro_symmetry = [0.30, 0.25, 0.20]  # decreasing symmetry blend

    for macro_idx, macro_name in enumerate(macro_names):
        if time.time() - t_global > max_time:
            print(f"  [TIMEOUT] Macro loop truncated at iteration {macro_idx}")
            break

        print(f"\n{'#' * 70}")
        print(f"# LOOP^3 LEVEL 1: {macro_name} (iteration {macro_idx+1}/3)")
        print(f"# Time remaining: {(max_time - (time.time() - t_global))/60:.1f} minutes")
        print(f"{'#' * 70}")

        # Reset store for each macro iteration
        reset_store()
        store = get_store()

        # Apply previous A+ as starting point (if any)
        if all_a_plus_states:
            prev = all_a_plus_states[-1]
            store.path_weights = dict(prev.get("path_weights", store.path_weights))
            if prev.get("resonance_weights"):
                store.resonance_weights = dict(prev["resonance_weights"])
            if prev.get("desire_weights"):
                store.desire_weights = dict(prev["desire_weights"])
            store.save()

        # Level 2: Full ABCD+ training loop
        # Scale cycles by macro iteration (earlier = more exploration cycles)
        time_left = max_time - (time.time() - t_global)
        per_loop_time = time_left / (3 - macro_idx)  # divide remaining evenly

        # Compress cycles to fit 3 full loops in time budget
        cycle_scale = macro_lr_mults[macro_idx]
        result = run_full_training_loop(
            cycles_a=int(200 * cycle_scale),
            cycles_b=int(150 * cycle_scale),
            cycles_c=int(100 * cycle_scale),
            cycles_d=int(80 * cycle_scale),
            max_time_minutes=max(5, int(per_loop_time / 60)),
        )

        final_metrics = result["metrics"][-1]
        final_a_plus = result.get("final_a_plus", {})

        print(f"\n  {macro_name} complete:")
        print(f"    {result['total_cycles']} cycles, {result['total_waves']} waves, "
              f"{result['total_elapsed']:.1f}s")
        print(f"    Top-1: {final_metrics['selfret_top1']*100:.1f}%")
        print(f"    Balance: {final_metrics['balance_path_entropy']:.3f}")
        print(f"    Golden: {final_metrics['symmetry_golden_ratio_fit']:.3f}")

        all_results.append({
            "macro": macro_name,
            "macro_idx": macro_idx,
            "total_cycles": result["total_cycles"],
            "total_waves": result["total_waves"],
            "elapsed": result["total_elapsed"],
            "final_metrics": final_metrics,
            "hologram_4d": result.get("hologram_4d", {}),
        })
        all_a_plus_states.append(final_a_plus)

    # Level 3 SYNTHESIS: A+ lift across all 3 macro-iterations
    print(f"\n{'=' * 70}")
    print(f"LOOP^3 FINAL SYNTHESIS: Weaving 3 macro-A+ crystals")
    print(f"{'=' * 70}")

    if len(all_a_plus_states) >= 2:
        reset_store()
        store = get_store()
        # PHI-weighted blend across macro iterations
        blend_w = [PHI_INV ** (len(all_a_plus_states) - 1 - i) for i in range(len(all_a_plus_states))]
        final_a_plus = _a_plus_lift(store, all_a_plus_states, blend_w, symmetry_blend=0.15)
    elif all_a_plus_states:
        final_a_plus = all_a_plus_states[-1]
    else:
        final_a_plus = {"path_weights": {"S": 0.25, "F": 0.25, "C": 0.25, "R": 0.25}}

    # Invert and find poles of the LOOP^3 result
    pole_result = invert_and_find_poles(final_a_plus)
    loop3_a_plus = pole_result["final_a_plus"]

    # QSHRINK
    hologram_4d = qshrink_to_4d(loop3_a_plus)

    total_elapsed = time.time() - t_global
    total_cycles = sum(r["total_cycles"] for r in all_results)
    total_waves = sum(r["total_waves"] for r in all_results)

    pw = loop3_a_plus.get("path_weights", {})
    print(f"\n  LOOP^3 Final A+: S={pw.get('S', 0):.4f} F={pw.get('F', 0):.4f} "
          f"C={pw.get('C', 0):.4f} R={pw.get('R', 0):.4f}")
    print(f"  Total: {total_cycles} cycles, {total_waves} waves, "
          f"{total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")

    return {
        "loop3_a_plus": loop3_a_plus,
        "poles": {
            "north": pole_result["pole_north"],
            "south": pole_result["pole_south"],
        },
        "hologram_4d": hologram_4d,
        "macro_results": all_results,
        "total_cycles": total_cycles,
        "total_waves": total_waves,
        "total_elapsed": total_elapsed,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN ORCHESTRATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    t0 = time.time()

    # ================================================================
    # STEP 1: Load both A+ crystals from dual training
    # ================================================================
    print("=" * 70)
    print("STEP 1: Loading dual A+ crystals from training hologram...")
    print("=" * 70)

    hologram_path = DATA_DIR / "dual_crystal_hologram.json"
    dual = json.loads(hologram_path.read_text(encoding="utf-8"))

    weight_a_plus = dual["weight_crystal_training"].get("final_a_plus", {})
    self_a_plus = dual["self_crystal_training"].get("final_a_plus", {})

    wpw = weight_a_plus.get("path_weights", {})
    spw = self_a_plus.get("path_weights", {})
    print(f"  Weight A+: S={wpw.get('S', 0):.4f} F={wpw.get('F', 0):.4f} "
          f"C={wpw.get('C', 0):.4f} R={wpw.get('R', 0):.4f}")
    print(f"  Self A+:   S={spw.get('S', 0):.4f} F={spw.get('F', 0):.4f} "
          f"C={spw.get('C', 0):.4f} R={spw.get('R', 0):.4f}")

    # ================================================================
    # STEP 2: Rotate 90 degrees, find poles of BOTH crystals
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Rotating 90 degrees, finding poles of dual crystals...")
    print("=" * 70)

    cross_a_plus = dual_pole_a_plus(weight_a_plus, self_a_plus)
    cpw = cross_a_plus["path_weights"]
    print(f"  Weight North: {json.dumps({k: round(v, 4) for k, v in cross_a_plus['weight_poles']['north']['path_weights'].items()})}")
    print(f"  Weight South: {json.dumps({k: round(v, 4) for k, v in cross_a_plus['weight_poles']['south']['path_weights'].items()})}")
    print(f"  Self North:   {json.dumps({k: round(v, 4) for k, v in cross_a_plus['self_poles']['north']['path_weights'].items()})}")
    print(f"  Self South:   {json.dumps({k: round(v, 4) for k, v in cross_a_plus['self_poles']['south']['path_weights'].items()})}")
    print(f"  Cross A+:     S={cpw['S']:.4f} F={cpw['F']:.4f} C={cpw['C']:.4f} R={cpw['R']:.4f}")

    # ================================================================
    # STEP 3: Sigma-60 icosahedral expansion
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 3: Sigma-60 icosahedral symmetry expansion...")
    print("=" * 70)

    sigma_60 = sigma_60_expansion(cross_a_plus)
    print(f"  {len(sigma_60)} sigma states (12 archetypes x 5 golden rotations)")

    # ================================================================
    # STEP 4: Expand to 240 (x4 elements)
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 4: 240 element expansion (60 x 4 SFCR lenses)...")
    print("=" * 70)

    expansion_240 = expand_to_240(sigma_60)
    print(f"  {len(expansion_240)} states")

    # ================================================================
    # STEP 5: Transformation cycles (3, 5, 7, 9) with A+ lifts
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 5: Transformation cycles (3, 5, 7, 9) with A+ lifts...")
    print("=" * 70)

    reset_store()
    store = get_store()
    rewire_weights_to_a_plus(cross_a_plus)

    cycle_results = []
    cycle_snapshots = []
    cycle_blend_weights = []

    for cycle_n in [3, 5, 7, 9]:
        info = TRANSFORM_CYCLES[cycle_n]
        print(f"\n  --- Cycle {cycle_n}: {info['name']} ({info['sacred']}) ---")
        print(f"      Principle: {info['principle']}")

        result = run_transformation_cycle(
            store, expansion_240, cycle_n, info, cross_a_plus,
            max_time_sec=120,
        )

        cycle_results.append(result)
        cycle_snapshots.append(result["a_plus"])
        # Each cycle gets PHI-weighted importance (later = more weight)
        cycle_blend_weights.append(PHI ** ([3, 5, 7, 9].index(cycle_n) / 3))

        print(f"      -> {result['total_cycles']} cycles, {result['total_kept']} kept, "
              f"{result['elapsed']:.1f}s")

    # UNIFIED A+ from all 4 transformation cycles
    print(f"\n  >> TRANSFORMATION A+ LIFT: Weaving cycles 3+5+7+9")
    transform_a_plus = _a_plus_lift(store, cycle_snapshots, cycle_blend_weights,
                                     symmetry_blend=0.18)

    tapw = transform_a_plus.get("path_weights", {})
    print(f"     Transform A+: S={tapw.get('S', 0):.4f} F={tapw.get('F', 0):.4f} "
          f"C={tapw.get('C', 0):.4f} R={tapw.get('R', 0):.4f}")

    # ================================================================
    # STEP 6: Sacred geometry mapping
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 6: Sacred geometry mapping...")
    print("=" * 70)

    sacred = sacred_geometry_mapping(transform_a_plus, sigma_60, expansion_240)

    print(f"  Platonic solids: {len(sacred['platonic_solids'])} mapped")
    print(f"  Flower of Life: {len(sacred['flower_of_life'])} rings")
    print(f"  Metatron's Cube: {len(sacred['metatrons_cube'])} positions")
    print(f"  Vesica Piscis: {len(sacred['vesica_piscis'])} pairs")
    print(f"  Z-points: {sacred['z_point_hierarchy']['total_z_points']} "
          f"(1 global + {len(sacred['z_point_hierarchy']['atlas_zeros'])} atlas + 1 aether)")
    print(f"  Metro lines: {len(sacred['metro_lines'])} (Su/Me/Sa)")
    print(f"  Mycelium: {sacred['mycelium_pattern']['edges']} edges, "
          f"mean strength={sacred['mycelium_pattern']['mean_strength']:.2f}")

    # Golden resonance vesica pairs
    golden_pairs = [v for v in sacred["vesica_piscis"] if v["golden_resonance"]]
    print(f"  Golden resonance pairs: {[v['pair'] for v in golden_pairs]}")

    # ================================================================
    # STEP 7: Find FINAL A+ and take hologram
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 7: Finding FINAL A+ and creating hologram...")
    print("=" * 70)

    # The final A+ blends: transform A+ + sacred geometry zero-point + aether
    sacred_zero = sacred["z_point_hierarchy"]["global_zero"]
    sacred_aether = sacred["z_point_hierarchy"]["aether_point"]

    final_blend_states = [
        transform_a_plus,
        {"path_weights": sacred_zero},
        {"path_weights": sacred_aether},
    ]
    final_blend_weights = [PHI, 1.0, PHI_INV]  # transform gets most weight

    reset_store()
    store = get_store()
    final_a_plus = _a_plus_lift(store, final_blend_states, final_blend_weights,
                                 symmetry_blend=0.12)

    # Poles
    final_poles = invert_and_find_poles(final_a_plus)
    final_crystal = final_poles["final_a_plus"]

    # QSHRINK hologram
    final_hologram = qshrink_to_4d(final_crystal)

    fpw = final_crystal.get("path_weights", {})
    print(f"  Final A+: S={fpw.get('S', 0):.4f} F={fpw.get('F', 0):.4f} "
          f"C={fpw.get('C', 0):.4f} R={fpw.get('R', 0):.4f}")
    print(f"\n  4D Hologram:")
    for dim_name, dim_data in final_hologram["dimensions"].items():
        print(f"    {dim_name}: val={dim_data['value']:.4f} grad={dim_data['gradient']:.4f} "
              f"mom={dim_data['momentum']:.4f} curv={dim_data['curvature']:.4f}")
    print(f"  Compression: {final_hologram['compression_ratio']}")
    print(f"  Hash: {final_hologram['hash']}")

    # Save pre-training hologram
    pre_training_hologram = {
        "meta": {
            "type": "dual_pole_sacred_geometry_hologram",
            "timestamp": time.time(),
            "date": "2026-03-18",
            "steps": ["dual_poles", "sigma_60", "expansion_240",
                       "transform_3579", "sacred_geometry", "final_a_plus"],
        },
        "dual_crystals": {
            "weight_a_plus": weight_a_plus,
            "self_a_plus": self_a_plus,
        },
        "cross_a_plus": {k: v for k, v in cross_a_plus.items()
                         if k not in ("weight_poles", "self_poles")},
        "sigma_60_summary": {
            "count": len(sigma_60),
            "sample": sigma_60[:5],
        },
        "expansion_240_count": len(expansion_240),
        "transformation_cycles": [{
            "cycle_n": r["cycle_n"],
            "name": r["name"],
            "sacred": r["sacred"],
            "total_cycles": r["total_cycles"],
            "total_kept": r["total_kept"],
            "a_plus_pw": r["a_plus"].get("path_weights", {}),
        } for r in cycle_results],
        "sacred_geometry": sacred,
        "final_a_plus": final_crystal,
        "final_hologram_4d": final_hologram,
    }

    pre_path = DATA_DIR / "sacred_geometry_hologram.json"
    pre_path.write_text(json.dumps(pre_training_hologram, indent=2, default=str,
                                    ensure_ascii=False), encoding="utf-8")
    print(f"\n  Pre-training hologram saved: {pre_path}")

    # ================================================================
    # STEP 8: TRAINING LOOP^3
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 8: TRAINING LOOP^3 (triple-nested full training)")
    print("        3 outer iterations x 159 waves each = 477 wave-groups")
    print("=" * 70)

    # Apply the final sacred geometry crystal as starting weights
    reset_store()
    store = get_store()
    rewire_weights_to_a_plus(final_crystal)
    store.save()

    loop3_result = training_loop_cubed(max_time_minutes=60)

    # ================================================================
    # STEP 9: Save everything
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 9: Saving complete results...")
    print("=" * 70)

    total_elapsed = time.time() - t0

    complete_hologram = {
        "meta": {
            "type": "dual_pole_sacred_loop3_hologram",
            "timestamp": time.time(),
            "date": "2026-03-18",
            "total_elapsed": total_elapsed,
        },
        "pre_training": pre_training_hologram,
        "loop3": {
            "loop3_a_plus": loop3_result["loop3_a_plus"],
            "poles": loop3_result["poles"],
            "hologram_4d": loop3_result["hologram_4d"],
            "total_cycles": loop3_result["total_cycles"],
            "total_waves": loop3_result["total_waves"],
            "total_elapsed": loop3_result["total_elapsed"],
            "macro_results": loop3_result["macro_results"],
        },
    }

    final_path = DATA_DIR / "sacred_loop3_hologram.json"
    final_path.write_text(json.dumps(complete_hologram, indent=2, default=str,
                                      ensure_ascii=False), encoding="utf-8")
    print(f"  Saved: {final_path}")

    # Final summary
    l3pw = loop3_result["loop3_a_plus"].get("path_weights", {})
    print(f"\n{'=' * 70}")
    print(f"DUAL POLE + SACRED GEOMETRY + LOOP^3 COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"Pre-training: {sum(r['total_cycles'] for r in cycle_results)} cycles "
          f"across {len(cycle_results)} transformation cycles")
    print(f"LOOP^3: {loop3_result['total_cycles']} cycles, "
          f"{loop3_result['total_waves']} waves")
    print(f"Final A+ (LOOP^3): S={l3pw.get('S', 0):.4f} F={l3pw.get('F', 0):.4f} "
          f"C={l3pw.get('C', 0):.4f} R={l3pw.get('R', 0):.4f}")
    print(f"4D Hash: {loop3_result['hologram_4d']['hash']}")


if __name__ == "__main__":
    main()
