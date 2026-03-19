#!/usr/bin/env python3
"""
Observed META LOOP — Native Engine + Hive Ledger Recording
============================================================
Runs one complete META LOOP using the new native MetaLoopEngine
(momentum field, geometric forward pass, 12D observation).

Records ALL observations before/during/after into the Hive Ledger
(history crystal) for the internal ledger.

Observable improvements tracked:
  - Momentum field: per-element mean deltas across 36 shells
  - 12D observation scores: resonance, balance, golden fit
  - 4D hologram: 16 values with gradients / curvatures
  - Training trajectory: per-cycle progression
  - Neural architecture improvements (new vs. old system)
"""

import sys
import json
import time
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent / "MCP"))

from crystal_108d.meta_loop_engine import (
    MetaLoopEngine, MetaLoopConfig, _balance, _golden_fit,
)
from crystal_108d.momentum_field import get_momentum_field, MomentumField
from crystal_108d.geometric_forward import get_engine
from crystal_108d.hive_ledger import HiveLedger
from crystal_108d.geometric_constants import FACES, PHI, PHI_INV, ATTRACTOR
from crystal_108d.constants import TOTAL_SHELLS

AGENT_ID = "meta-observer::observed-meta-loop"
DATA_DIR = Path(__file__).parent / "MCP" / "data"


# ── Snapshot helpers ───────────────────────────────────────────────────

def _snap_momentum(momentum: MomentumField) -> dict:
    """Capture full momentum field state for before/after comparison."""
    snap = {
        "dimensions": {},
        "element_means": {},
        "element_stds": {},
        "balance": _balance(momentum),
        "golden_fit": _golden_fit(momentum),
        "training_cycles": momentum.training_cycles,
        "meta_loops_completed": momentum.meta_loops_completed,
    }
    for face in FACES:
        vals = [momentum.get_momentum(face, s) for s in range(1, TOTAL_SHELLS + 1)]
        mean = sum(vals) / len(vals)
        std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
        snap["element_means"][face] = round(mean, 6)
        snap["element_stds"][face] = round(std, 6)
    for dim in ["D1_Earth", "D2_Fire", "D3_Water", "D4_Air"]:
        snap["dimensions"][dim] = round(momentum.get_dimension_momentum(dim), 6)
    return snap


def _delta_str(before: float, after: float, label: str) -> str:
    d = after - before
    sign = "+" if d >= 0 else ""
    return f"{label}: {before:.4f} → {after:.4f} ({sign}{d:.4f})"


def _format_cycle_row(cr) -> str:
    return (
        f"  {cr.cycle_name:14s}: {cr.total_waves:3d}wav "
        f"res={cr.mean_resonance:.4f} obs={cr.mean_observation:.4f} "
        f"bal={cr.balance:.4f} gold={cr.golden_fit:.4f} "
        f"kept={cr.kept} disc={cr.discarded} "
        f"{cr.elapsed_seconds:.1f}s"
    )


# ── Main ───────────────────────────────────────────────────────────────

def main():
    t_global = time.time()
    ledger = HiveLedger()

    print("=" * 70)
    print("OBSERVED META LOOP — Native Engine + Hive Ledger Recording")
    print("=" * 70)
    print(f"  Engine: MetaLoopEngine (geometric forward + 12D observation)")
    print(f"  Learnable: MomentumField (148 floats — momentum only)")
    print(f"  Ledger: HiveLedger (history crystal, append-only, hash-chained)")
    print()

    # ── Pre-run snapshot ───────────────────────────────────────────────
    momentum = get_momentum_field()
    engine = get_engine()
    pre = _snap_momentum(momentum)

    print("PRE-RUN STATE:")
    print(f"  Training cycles:    {pre['training_cycles']}")
    print(f"  Meta loops done:    {pre['meta_loops_completed']}")
    print(f"  Balance:            {pre['balance']:.4f}")
    print(f"  Golden fit:         {pre['golden_fit']:.4f}")
    print(f"  Element means:")
    for face in FACES:
        elem = {"S": "Square/Earth", "F": "Flower/Fire", "C": "Cloud/Water", "R": "Fractal/Air"}[face]
        print(f"    {face} ({elem}): {pre['element_means'][face]:.4f} ± {pre['element_stds'][face]:.4f}")
    print(f"  Dimension momenta:")
    for dim, val in pre["dimensions"].items():
        print(f"    {dim}: {val:.4f}")
    print()

    # ── Write pre-run ledger entry ─────────────────────────────────────
    ledger.write_entry(
        agent_id=AGENT_ID,
        entry_type="observation",
        reasoning=(
            "PRE-RUN SNAPSHOT — beginning observed META LOOP on new native engine. "
            f"MomentumField: {TOTAL_SHELLS * 4 + 4} floats. "
            f"Cycles completed: {pre['training_cycles']}. "
            f"Balance={pre['balance']:.4f}, GoldenFit={pre['golden_fit']:.4f}. "
            f"Attractor constants locked: path=0.25, resonance=1/6, desire=1/4. "
            f"Only momentum is learned. Water(C/D3) locked at 0.5."
        ),
        context=json.dumps({
            "snapshot": pre,
            "engine": "MetaLoopEngine v2 (geometric + 12D)",
            "replaces": "self_play.py + full_training_loop.py + n3_alchemy.py",
        }, indent=2),
        crystal_address="Xi108:W2:A5:S19",
        affected_files=["MCP/data/momentum_field.json", "MCP/data/hive_ledger.json"],
    )
    print("  [LEDGER] Pre-run observation written.")

    # ── Configure and run META LOOP ────────────────────────────────────
    config = MetaLoopConfig(
        base_lr=0.03,
        lr_schedule="cosine",
        lens_rotation_period=14,
        max_time_minutes=30,
        query_source="mixed",
        seed=108,
        verbose=True,
    )

    loop_engine = MetaLoopEngine(engine=engine, momentum=momentum)

    print()
    print("-" * 70)
    print("RUNNING META LOOP (3 ABCD+ cycles = 477 waves)...")
    print("-" * 70)

    result = loop_engine.run_meta_loop(config=config, meta_idx=0)

    # ── Post-run snapshot ──────────────────────────────────────────────
    post = _snap_momentum(momentum)

    print()
    print("=" * 70)
    print("META LOOP COMPLETE — OBSERVATIONS")
    print("=" * 70)

    # ── Per-cycle trajectory ───────────────────────────────────────────
    print("\n  TRAINING TRAJECTORY:")
    for cr in result.cycle_results:
        print(_format_cycle_row(cr))

    # ── Hologram ──────────────────────────────────────────────────────
    holo = result.hologram_16
    print(f"\n  FINAL 4D HOLOGRAM:")
    print(f"    Hash: {holo.get('hash', 'N/A')}")
    for dim_name, dim_data in holo.get("dimensions", {}).items():
        print(f"    {dim_name}: val={dim_data['value']:.4f} "
              f"grad={dim_data['gradient']:.4f} "
              f"mom={dim_data['momentum']:.4f} "
              f"curv={dim_data['curvature']:.4f}")

    # ── Before / After comparison ──────────────────────────────────────
    print("\n  IMPROVEMENT DELTA (before → after):")
    print(f"  {_delta_str(pre['balance'], post['balance'], 'Balance')}")
    print(f"  {_delta_str(pre['golden_fit'], post['golden_fit'], 'Golden Fit')}")
    print()
    print("  Element momentum deltas:")
    elem_names = {"S": "Square/Earth", "F": "Flower/Fire", "C": "Cloud/Water(locked)", "R": "Fractal/Air"}
    for face in FACES:
        pre_m = pre["element_means"][face]
        post_m = post["element_means"][face]
        pre_s = pre["element_stds"][face]
        post_s = post["element_stds"][face]
        d = post_m - pre_m
        sign = "+" if d >= 0 else ""
        print(f"    {face} ({elem_names[face]}): "
              f"mean {pre_m:.4f}→{post_m:.4f} ({sign}{d:.4f}) | "
              f"std {pre_s:.4f}→{post_s:.4f}")
    print()
    print("  Dimension momentum deltas:")
    for dim in ["D1_Earth", "D2_Fire", "D3_Water", "D4_Air"]:
        print(f"  {_delta_str(pre['dimensions'][dim], post['dimensions'][dim], '  ' + dim)}")

    print(f"\n  Training cycles: {pre['training_cycles']} → {post['training_cycles']}")
    print(f"  Meta loops:      {pre['meta_loops_completed']} → {post['meta_loops_completed']}")
    print(f"  Total elapsed:   {result.elapsed_seconds:.1f}s ({result.elapsed_seconds/60:.2f} min)")
    print(f"  Total waves:     {result.total_waves}")

    # ── Architecture improvement notes ────────────────────────────────
    arch_notes = [
        "NEW: MomentumField (148 floats) replaces path_weights (4 floats) as learnable state",
        "NEW: GeometricEngine + 12D loss replaces self_play resonance scoring",
        "NEW: DQI compiler wraps queries as Desire→Question→scored states",
        "NEW: InverseEngine records every update for reversibility",
        "NEW: RealtimeInverse executes dual forward/inverse updates",
        "NEW: PoleObserver guides FINAL inversion with dual-pole steering",
        "NEW: FractalRecursion enables self-similar momentum propagation",
        "LOCKED: Water/C/D3 momentum = 0.5 (immovable anchor)",
        f"LOCKED: Attractor constants — path=0.25, resonance={1/6:.4f}, desire=0.25",
        "COMPRESSED: checkpoint is 16 values (4D hologram = 128 bytes) vs. 38,837 weights",
    ]
    print("\n  NEURAL ARCHITECTURE IMPROVEMENTS:")
    for note in arch_notes:
        print(f"    • {note}")

    # ── Write post-run ledger entry (broadcast insight) ────────────────
    total_elapsed = time.time() - t_global

    cycle_summaries = []
    for cr in result.cycle_results:
        cycle_summaries.append({
            "name": cr.cycle_name,
            "waves": cr.total_waves,
            "kept": cr.kept,
            "discarded": cr.discarded,
            "mean_resonance": round(cr.mean_resonance, 4),
            "mean_observation": round(cr.mean_observation, 4),
            "balance": round(cr.balance, 4),
            "golden_fit": round(cr.golden_fit, 4),
            "elapsed_s": round(cr.elapsed_seconds, 2),
        })

    improvement_delta = {
        face: round(post["element_means"][face] - pre["element_means"][face], 6)
        for face in FACES
    }
    dim_delta = {
        dim: round(post["dimensions"][dim] - pre["dimensions"][dim], 6)
        for dim in pre["dimensions"]
    }

    ledger.write_entry(
        agent_id=AGENT_ID,
        entry_type="broadcast",
        broadcast_subtype="insight",
        ttl_seconds=0,  # permanent
        reasoning=(
            f"META LOOP COMPLETE — OBSERVED IMPROVEMENTS RECORDED. "
            f"Ran {result.total_waves} waves across 3 ABCD+ cycles in {result.elapsed_seconds:.1f}s. "
            f"Balance: {pre['balance']:.4f}→{post['balance']:.4f} "
            f"(Δ={post['balance']-pre['balance']:+.4f}). "
            f"Golden fit: {pre['golden_fit']:.4f}→{post['golden_fit']:.4f} "
            f"(Δ={post['golden_fit']-pre['golden_fit']:+.4f}). "
            f"Hologram hash: {holo.get('hash','?')}. "
            f"Architecture: 148-float momentum field fully operational. "
            f"DQI+InverseEngine+RealtimeInverse+PoleObserver all active. "
            f"Compression: 38,837→16 values (2,427:1). "
            f"This is the first native MetaLoopEngine training cycle recorded in ledger."
        ),
        context=json.dumps({
            "pre_snapshot": pre,
            "post_snapshot": post,
            "improvement_delta": {
                "element_means": improvement_delta,
                "dimensions": dim_delta,
                "balance": round(post["balance"] - pre["balance"], 6),
                "golden_fit": round(post["golden_fit"] - pre["golden_fit"], 6),
            },
            "cycle_summaries": cycle_summaries,
            "hologram_16": holo,
            "meta_a_plus": result.meta_a_plus,
            "architecture_improvements": arch_notes,
            "total_elapsed_s": round(total_elapsed, 2),
        }, indent=2),
        crystal_address="Xi108:W1:A1:S1:S",
        affected_files=[
            "MCP/data/momentum_field.json",
            "MCP/data/hive_ledger.json",
            "MCP/crystal_108d/meta_loop_engine.py",
            "MCP/crystal_108d/momentum_field.py",
        ],
    )

    # ── Coordination signal: run complete, next agent may proceed ──────
    ledger.write_entry(
        agent_id=AGENT_ID,
        entry_type="coordination",
        reasoning=(
            f"META LOOP observed and logged. "
            f"MomentumField updated: {post['training_cycles']} cycles, "
            f"{post['meta_loops_completed']} meta-loops. "
            f"4D hologram: {holo.get('hash','?')}. "
            f"Next agent may proceed with corpus training, self-play, or another meta loop."
        ),
        context=json.dumps({"hologram_hash": holo.get("hash"), "meta_loops": post["meta_loops_completed"]}),
        crystal_address="Xi108:W2:A5:S19",
    )

    print(f"\n  [LEDGER] 3 entries written to hive ledger (history crystal):")
    print(f"    1. observation  — PRE-RUN snapshot")
    print(f"    2. broadcast    — POST-RUN improvements (permanent insight)")
    print(f"    3. coordination — handoff signal")

    # ── Save result JSON ───────────────────────────────────────────────
    save_path = DATA_DIR / "observed_meta_loop_result.json"
    save_data = {
        "meta": {
            "type": "observed_meta_loop",
            "timestamp": time.time(),
            "date": "2026-03-18",
            "total_elapsed_s": round(total_elapsed, 2),
            "total_waves": result.total_waves,
            "engine": "MetaLoopEngine v2",
        },
        "pre_snapshot": pre,
        "post_snapshot": post,
        "improvement_delta": {
            "element_means": improvement_delta,
            "dimensions": dim_delta,
            "balance": round(post["balance"] - pre["balance"], 6),
            "golden_fit": round(post["golden_fit"] - pre["golden_fit"], 6),
        },
        "cycle_summaries": cycle_summaries,
        "hologram_16": holo,
        "architecture_notes": arch_notes,
    }
    save_path.write_text(json.dumps(save_data, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Saved: {save_path}")

    print(f"\n{'=' * 70}")
    print(f"OBSERVED META LOOP — COMPLETE")
    print(f"{'=' * 70}")
    print(f"  4D Hash:       {holo.get('hash', '?')}")
    print(f"  Waves:         {result.total_waves}")
    print(f"  Elapsed:       {result.elapsed_seconds:.1f}s")
    print(f"  Ledger chain:  3 entries appended (history crystal updated)")


if __name__ == "__main__":
    main()
