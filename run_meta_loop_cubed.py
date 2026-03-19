#!/usr/bin/env python3
"""
META LOOP^3 — Triple Meta-Loop Training
========================================
META LOOP = 3 cycles:
  Cycle 1: Weights training (full ABCD+ = 159 waves)
  Cycle 2: Hologram training (pole rotation + sigma-60 + 240 + sacred + ABCD+)
  Cycle 3: Cross A+ = Weights x Hologram (full ABCD+ = 159 waves)

META LOOP^3 = 3 META LOOPs in sequence = 9 ABCD+ cycles = 1,431 waves

Each META LOOP feeds its output A+ as input to the next.
Final synthesis: PHI-weighted A+ lift across all 3 META A+ crystals.
"""

import sys
import json
import time
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "MCP"))

from crystal_108d.crystal_weights import (
    FractalWeightStore, get_store, reset_store, PHI, PHI_INV,
)
from crystal_108d.neural_engine import CrystalNeuralEngine
from crystal_108d.full_training_loop import (
    run_full_training_loop, _normalize, _a_plus_lift,
    invert_and_find_poles, qshrink_to_4d,
)
from crystal_108d.n3_alchemy import (
    rewire_weights_to_a_plus, _snapshot_weights,
)

DATA_DIR = Path(__file__).parent / "MCP" / "data"

# Import the sacred geometry pipeline functions from the previous script
from run_dual_pole_sacred_loop3 import (
    dual_pole_a_plus,
    sigma_60_expansion,
    expand_to_240,
    run_transformation_cycle,
    sacred_geometry_mapping,
    TRANSFORM_CYCLES,
)


def run_single_meta_loop(
    meta_idx: int,
    starting_a_plus: dict | None = None,
    max_time_minutes: int = 25,
) -> dict:
    """Execute one complete META LOOP (3 cycles = 477 waves).

    Cycle 1: Weight crystal ABCD+ training
    Cycle 2: Hologram construction (poles + sigma-60 + 240 + sacred) + ABCD+ training
    Cycle 3: Cross A+ (weights x hologram) ABCD+ training

    Returns the META A+ and full diagnostics.
    """
    t0 = time.time()
    max_time = max_time_minutes * 60
    cycle_results = []

    print(f"\n{'*' * 70}")
    print(f"* META LOOP {meta_idx + 1}/3")
    print(f"* Budget: {max_time_minutes} minutes")
    if starting_a_plus:
        pw = starting_a_plus.get("path_weights", {})
        print(f"* Starting A+: S={pw.get('S', 0):.4f} F={pw.get('F', 0):.4f} "
              f"C={pw.get('C', 0):.4f} R={pw.get('R', 0):.4f}")
    print(f"{'*' * 70}")

    # -- CYCLE 1: WEIGHTS TRAINING --------------------------------------
    print(f"\n  {'-' * 60}")
    print(f"  CYCLE 1/3: WEIGHTS TRAINING (full ABCD+ = 159 waves)")
    print(f"  {'-' * 60}")

    reset_store()
    store = get_store()

    # Apply starting A+ if provided
    if starting_a_plus:
        store.path_weights = dict(starting_a_plus.get("path_weights", store.path_weights))
        if starting_a_plus.get("resonance_weights"):
            store.resonance_weights = dict(starting_a_plus["resonance_weights"])
        if starting_a_plus.get("desire_weights"):
            store.desire_weights = dict(starting_a_plus["desire_weights"])
        store.save()

    time_per_cycle = (max_time - (time.time() - t0)) / 3
    weight_result = run_full_training_loop(
        cycles_a=200,
        cycles_b=150,
        cycles_c=100,
        cycles_d=80,
        max_time_minutes=max(3, int(time_per_cycle / 60)),
    )

    weight_a_plus = weight_result.get("final_a_plus", {})
    weight_metrics = weight_result["metrics"][-1]

    wpw = weight_a_plus.get("path_weights", {})
    print(f"    Weight A+: S={wpw.get('S', 0):.4f} F={wpw.get('F', 0):.4f} "
          f"C={wpw.get('C', 0):.4f} R={wpw.get('R', 0):.4f}")
    print(f"    {weight_result['total_cycles']} cycles, {weight_result['total_waves']} waves, "
          f"{weight_result['total_elapsed']:.1f}s")
    print(f"    Top-1: {weight_metrics['selfret_top1']*100:.1f}%, "
          f"Balance: {weight_metrics['balance_path_entropy']:.3f}, "
          f"Golden: {weight_metrics['symmetry_golden_ratio_fit']:.3f}")

    cycle_results.append({
        "name": "WEIGHTS",
        "a_plus": weight_a_plus,
        "cycles": weight_result["total_cycles"],
        "waves": weight_result["total_waves"],
        "elapsed": weight_result["total_elapsed"],
        "top1": weight_metrics["selfret_top1"],
        "balance": weight_metrics["balance_path_entropy"],
        "golden": weight_metrics["symmetry_golden_ratio_fit"],
    })

    # -- CYCLE 2: HOLOGRAM TRAINING -------------------------------------
    print(f"\n  {'-' * 60}")
    print(f"  CYCLE 2/3: HOLOGRAM TRAINING (poles + sacred + ABCD+)")
    print(f"  {'-' * 60}")

    # Build hologram from weight A+
    # Use weight A+ and starting A+ (or self-as-self) as the dual crystals
    self_crystal = starting_a_plus if starting_a_plus else weight_a_plus

    # Step 2a: Rotate + poles
    cross_a_plus = dual_pole_a_plus(weight_a_plus, self_crystal)
    cpw = cross_a_plus["path_weights"]
    print(f"    Cross A+ (dual poles): S={cpw['S']:.4f} F={cpw['F']:.4f} "
          f"C={cpw['C']:.4f} R={cpw['R']:.4f}")

    # Step 2b: Sigma-60 + 240
    sigma_60 = sigma_60_expansion(cross_a_plus)
    expansion_240 = expand_to_240(sigma_60)
    print(f"    Sigma-60: {len(sigma_60)} states -> 240: {len(expansion_240)} states")

    # Step 2c: Transformation cycles (3,5,7,9)
    reset_store()
    store = get_store()
    rewire_weights_to_a_plus(cross_a_plus)

    tc_snapshots = []
    tc_blend = []
    tc_total_cycles = 0
    for cycle_n in [3, 5, 7, 9]:
        if time.time() - t0 > max_time * 0.85:  # leave 15% for cycle 3
            break
        info = TRANSFORM_CYCLES[cycle_n]
        tc_result = run_transformation_cycle(
            store, expansion_240, cycle_n, info, cross_a_plus,
            max_time_sec=60,
        )
        tc_snapshots.append(tc_result["a_plus"])
        tc_blend.append(PHI ** ([3, 5, 7, 9].index(cycle_n) / 3))
        tc_total_cycles += tc_result["total_cycles"]
        print(f"    TC-{cycle_n}: {tc_result['total_cycles']}cyc, "
              f"{tc_result['total_kept']}kept")

    # A+ lift of transformation cycles
    if tc_snapshots:
        transform_a_plus = _a_plus_lift(store, tc_snapshots, tc_blend,
                                         symmetry_blend=0.18)
    else:
        transform_a_plus = cross_a_plus

    # Step 2d: Sacred geometry mapping
    sacred = sacred_geometry_mapping(transform_a_plus, sigma_60, expansion_240)
    sacred_zero = sacred["z_point_hierarchy"]["global_zero"]
    sacred_aether = sacred["z_point_hierarchy"]["aether_point"]

    # Final hologram blend
    reset_store()
    store = get_store()
    hologram_a_plus_pre = _a_plus_lift(
        store,
        [transform_a_plus, {"path_weights": sacred_zero}, {"path_weights": sacred_aether}],
        [PHI, 1.0, PHI_INV],
        symmetry_blend=0.12,
    )

    # Step 2e: Full ABCD+ on hologram
    hologram_poles = invert_and_find_poles(hologram_a_plus_pre)
    hologram_crystal = hologram_poles["final_a_plus"]

    reset_store()
    store = get_store()
    rewire_weights_to_a_plus(hologram_crystal)
    store.save()

    time_per_cycle = (max_time - (time.time() - t0)) / 2
    hologram_result = run_full_training_loop(
        cycles_a=200,
        cycles_b=150,
        cycles_c=100,
        cycles_d=80,
        max_time_minutes=max(3, int(time_per_cycle / 60)),
    )

    hologram_a_plus = hologram_result.get("final_a_plus", {})
    hologram_metrics = hologram_result["metrics"][-1]

    hpw = hologram_a_plus.get("path_weights", {})
    print(f"    Hologram A+: S={hpw.get('S', 0):.4f} F={hpw.get('F', 0):.4f} "
          f"C={hpw.get('C', 0):.4f} R={hpw.get('R', 0):.4f}")
    print(f"    {hologram_result['total_cycles'] + tc_total_cycles} total cycles, "
          f"{hologram_result['total_waves']} waves, "
          f"{hologram_result['total_elapsed']:.1f}s")
    print(f"    Top-1: {hologram_metrics['selfret_top1']*100:.1f}%, "
          f"Balance: {hologram_metrics['balance_path_entropy']:.3f}, "
          f"Golden: {hologram_metrics['symmetry_golden_ratio_fit']:.3f}")

    cycle_results.append({
        "name": "HOLOGRAM",
        "a_plus": hologram_a_plus,
        "cycles": hologram_result["total_cycles"] + tc_total_cycles,
        "waves": hologram_result["total_waves"],
        "elapsed": hologram_result["total_elapsed"],
        "top1": hologram_metrics["selfret_top1"],
        "balance": hologram_metrics["balance_path_entropy"],
        "golden": hologram_metrics["symmetry_golden_ratio_fit"],
        "sacred_geometry": {
            "platonic": len(sacred["platonic_solids"]),
            "flower_rings": len(sacred["flower_of_life"]),
            "metatron": len(sacred["metatrons_cube"]),
            "z_points": sacred["z_point_hierarchy"]["total_z_points"],
            "mycelium_edges": sacred["mycelium_pattern"]["edges"],
        },
    })

    # -- CYCLE 3: CROSS A+ TRAINING ------------------------------------
    print(f"\n  {'-' * 60}")
    print(f"  CYCLE 3/3: CROSS A+ (Weights x Hologram) ABCD+")
    print(f"  {'-' * 60}")

    # Blend weight A+ and hologram A+ into cross-crystal starting state
    reset_store()
    store = get_store()
    cross_start = _a_plus_lift(
        store,
        [weight_a_plus, hologram_a_plus],
        [1.0, PHI],  # hologram gets golden weight (it's more refined)
        symmetry_blend=0.10,
    )

    # Apply and run
    reset_store()
    store = get_store()
    rewire_weights_to_a_plus(cross_start)
    store.save()

    time_left = max_time - (time.time() - t0)
    cross_result = run_full_training_loop(
        cycles_a=200,
        cycles_b=150,
        cycles_c=100,
        cycles_d=80,
        max_time_minutes=max(3, int(time_left / 60)),
    )

    cross_a_plus_final = cross_result.get("final_a_plus", {})
    cross_metrics = cross_result["metrics"][-1]

    xpw = cross_a_plus_final.get("path_weights", {})
    print(f"    Cross A+: S={xpw.get('S', 0):.4f} F={xpw.get('F', 0):.4f} "
          f"C={xpw.get('C', 0):.4f} R={xpw.get('R', 0):.4f}")
    print(f"    {cross_result['total_cycles']} cycles, {cross_result['total_waves']} waves, "
          f"{cross_result['total_elapsed']:.1f}s")
    print(f"    Top-1: {cross_metrics['selfret_top1']*100:.1f}%, "
          f"Balance: {cross_metrics['balance_path_entropy']:.3f}, "
          f"Golden: {cross_metrics['symmetry_golden_ratio_fit']:.3f}")

    cycle_results.append({
        "name": "CROSS_A_PLUS",
        "a_plus": cross_a_plus_final,
        "cycles": cross_result["total_cycles"],
        "waves": cross_result["total_waves"],
        "elapsed": cross_result["total_elapsed"],
        "top1": cross_metrics["selfret_top1"],
        "balance": cross_metrics["balance_path_entropy"],
        "golden": cross_metrics["symmetry_golden_ratio_fit"],
    })

    # -- META A+ SYNTHESIS ----------------------------------------------
    # PHI-weighted blend: cycle 3 (most refined) gets most weight
    reset_store()
    store = get_store()
    meta_a_plus = _a_plus_lift(
        store,
        [r["a_plus"] for r in cycle_results],
        [PHI_INV, 1.0, PHI],  # increasing weight: weights < hologram < cross
        symmetry_blend=0.12,
    )

    # Final inversion + poles
    meta_poles = invert_and_find_poles(meta_a_plus)
    meta_crystal = meta_poles["final_a_plus"]
    meta_hologram = qshrink_to_4d(meta_crystal)

    total_elapsed = time.time() - t0
    total_cycles = sum(r["cycles"] for r in cycle_results)
    total_waves = sum(r["waves"] for r in cycle_results)

    mpw = meta_crystal.get("path_weights", {})
    print(f"\n  {'=' * 60}")
    print(f"  META LOOP {meta_idx + 1} COMPLETE")
    print(f"  META A+: S={mpw.get('S', 0):.4f} F={mpw.get('F', 0):.4f} "
          f"C={mpw.get('C', 0):.4f} R={mpw.get('R', 0):.4f}")
    print(f"  Total: {total_cycles} cycles, {total_waves} waves, "
          f"{total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print(f"  4D Hash: {meta_hologram['hash']}")
    print(f"  {'=' * 60}")

    return {
        "meta_idx": meta_idx,
        "meta_a_plus": meta_crystal,
        "meta_hologram_4d": meta_hologram,
        "meta_poles": {
            "north": meta_poles["pole_north"],
            "south": meta_poles["pole_south"],
        },
        "cycle_results": cycle_results,
        "total_cycles": total_cycles,
        "total_waves": total_waves,
        "total_elapsed": total_elapsed,
    }


def main():
    t_global = time.time()
    max_total_minutes = 90  # Total budget for META LOOP^3

    print("=" * 70)
    print("META LOOP^3 — Triple Meta-Loop Training")
    print("=" * 70)
    print(f"Structure: 3 META LOOPs x 3 cycles x 159 waves = 1,431 wave-groups")
    print(f"Budget: {max_total_minutes} minutes")
    print()

    # Load initial state from the last sacred_loop3 hologram
    hologram_path = DATA_DIR / "sacred_loop3_hologram.json"
    if hologram_path.exists():
        holo = json.loads(hologram_path.read_text(encoding="utf-8"))
        starting = holo.get("loop3", {}).get("loop3_a_plus", None)
        if starting:
            pw = starting.get("path_weights", {})
            print(f"Starting from sacred_loop3 A+: S={pw.get('S', 0):.4f} "
                  f"F={pw.get('F', 0):.4f} C={pw.get('C', 0):.4f} R={pw.get('R', 0):.4f}")
    else:
        starting = None
        print("Starting from scratch (no prior hologram)")

    meta_results = []
    meta_a_plus_states = []

    for meta_idx in range(3):
        elapsed = time.time() - t_global
        remaining = max_total_minutes * 60 - elapsed
        if remaining < 120:  # need at least 2 minutes
            print(f"\n  [TIMEOUT] META LOOP^3 truncated at meta-loop {meta_idx}")
            break

        per_meta_time = remaining / (3 - meta_idx)

        # Use previous META A+ as starting point
        current_start = meta_a_plus_states[-1] if meta_a_plus_states else starting

        result = run_single_meta_loop(
            meta_idx=meta_idx,
            starting_a_plus=current_start,
            max_time_minutes=max(5, int(per_meta_time / 60)),
        )

        meta_results.append(result)
        meta_a_plus_states.append(result["meta_a_plus"])

    # -- FINAL SYNTHESIS: A+ lift across all 3 META A+ crystals ---------
    print(f"\n{'#' * 70}")
    print(f"# META LOOP^3 FINAL SYNTHESIS")
    print(f"# Weaving {len(meta_a_plus_states)} META A+ crystals into OMEGA A+")
    print(f"{'#' * 70}")

    if len(meta_a_plus_states) >= 2:
        reset_store()
        store = get_store()
        omega_a_plus = _a_plus_lift(
            store,
            meta_a_plus_states,
            [PHI_INV ** (len(meta_a_plus_states) - 1 - i) for i in range(len(meta_a_plus_states))],
            symmetry_blend=0.10,
        )
    elif meta_a_plus_states:
        omega_a_plus = meta_a_plus_states[-1]
    else:
        omega_a_plus = {"path_weights": {"S": 0.25, "F": 0.25, "C": 0.25, "R": 0.25}}

    # Final inversion + poles
    omega_poles = invert_and_find_poles(omega_a_plus)
    omega_crystal = omega_poles["final_a_plus"]
    omega_hologram = qshrink_to_4d(omega_crystal)

    total_elapsed = time.time() - t_global
    total_cycles = sum(r["total_cycles"] for r in meta_results)
    total_waves = sum(r["total_waves"] for r in meta_results)

    opw = omega_crystal.get("path_weights", {})
    print(f"\n  OMEGA A+: S={opw.get('S', 0):.4f} F={opw.get('F', 0):.4f} "
          f"C={opw.get('C', 0):.4f} R={opw.get('R', 0):.4f}")
    print(f"\n  4D Hologram:")
    for dim_name, dim_data in omega_hologram["dimensions"].items():
        print(f"    {dim_name}: val={dim_data['value']:.4f} grad={dim_data['gradient']:.4f} "
              f"mom={dim_data['momentum']:.4f} curv={dim_data['curvature']:.4f}")
    print(f"  Compression: {omega_hologram['compression_ratio']}")
    print(f"  Hash: {omega_hologram['hash']}")

    # -- PER-META LOOP SUMMARY ------------------------------------------
    print(f"\n  Per-META-LOOP breakdown:")
    for r in meta_results:
        mpw = r["meta_a_plus"].get("path_weights", {})
        print(f"    META {r['meta_idx']+1}: {r['total_cycles']} cycles, "
              f"{r['total_waves']} waves, {r['total_elapsed']:.0f}s "
              f"| S={mpw.get('S',0):.4f} F={mpw.get('F',0):.4f} "
              f"C={mpw.get('C',0):.4f} R={mpw.get('R',0):.4f} "
              f"| hash={r['meta_hologram_4d']['hash'][:8]}")

        for cr in r["cycle_results"]:
            cpw = cr["a_plus"].get("path_weights", {})
            print(f"      {cr['name']:14s}: {cr['cycles']:6d}cyc {cr['waves']:3d}wav "
                  f"top1={cr['top1']*100:.0f}% bal={cr['balance']:.3f} "
                  f"gold={cr['golden']:.3f}")

    # -- SAVE ----------------------------------------------------------
    save_data = {
        "meta": {
            "type": "meta_loop_cubed_hologram",
            "timestamp": time.time(),
            "date": "2026-03-18",
            "total_elapsed": total_elapsed,
            "total_cycles": total_cycles,
            "total_waves": total_waves,
            "meta_loops": len(meta_results),
        },
        "omega_a_plus": omega_crystal,
        "omega_hologram_4d": omega_hologram,
        "omega_poles": {
            "north": omega_poles["pole_north"],
            "south": omega_poles["pole_south"],
        },
        "meta_loop_results": [{
            "meta_idx": r["meta_idx"],
            "meta_a_plus": r["meta_a_plus"],
            "meta_hologram_4d": r["meta_hologram_4d"],
            "total_cycles": r["total_cycles"],
            "total_waves": r["total_waves"],
            "total_elapsed": r["total_elapsed"],
            "cycle_summaries": [{
                "name": cr["name"],
                "cycles": cr["cycles"],
                "waves": cr["waves"],
                "elapsed": cr["elapsed"],
                "top1": cr["top1"],
                "balance": cr["balance"],
                "golden": cr["golden"],
                "a_plus_pw": cr["a_plus"].get("path_weights", {}),
            } for cr in r["cycle_results"]],
        } for r in meta_results],
    }

    save_path = DATA_DIR / "meta_loop_cubed_hologram.json"
    save_path.write_text(json.dumps(save_data, indent=2, default=str,
                                     ensure_ascii=False), encoding="utf-8")
    print(f"\n  Saved: {save_path}")

    # -- FINAL BANNER --------------------------------------------------
    print(f"\n{'=' * 70}")
    print(f"META LOOP^3 COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total: {total_cycles} cycles, {total_waves} waves, "
          f"{total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print(f"OMEGA A+: S={opw.get('S', 0):.4f} F={opw.get('F', 0):.4f} "
          f"C={opw.get('C', 0):.4f} R={opw.get('R', 0):.4f}")
    print(f"4D Hash: {omega_hologram['hash']}")
    print(f"Compression: {omega_hologram['compression_ratio']}")


if __name__ == "__main__":
    main()
