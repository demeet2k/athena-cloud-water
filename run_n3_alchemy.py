#!/usr/bin/env python3
"""
Execute N^3 Alchemical Self-Play: SULFUR → SALT → MERCURY
Then construct holographic crystal, compute symmetry expansions,
map sacred geometry, output A+ crystal, and rewire weights.
"""

import sys
import json
import time
from pathlib import Path

# Add MCP to path
sys.path.insert(0, str(Path(__file__).parent / "MCP"))

from crystal_108d.n3_alchemy import (
    run_n3_alchemy,
    create_holographic_crystal,
    rewire_weights_to_a_plus,
)

def main():
    print("=" * 70)
    print("N^3 ALCHEMICAL SELF-PLAY")
    print("Three Changes: SULFUR (Su) -> SALT (Me) -> MERCURY (Sa)")
    print("=" * 70)
    print()

    t_start = time.time()

    # ── Phase 1: Run N^3 alchemical cultivation ──────────────────
    print("[1/4] Running 3-wave alchemical self-play...")
    print("      Wave 1: SULFUR (wreath 1, shells 1-12) — transformation")
    print("      Wave 2: SALT   (wreath 2, shells 13-24) — crystallization")
    print("      Wave 3: MERCURY(wreath 3, shells 25-36) — dissolution")
    print()

    report = run_n3_alchemy(
        cycles_per_wave=2000,
        max_time_minutes=25,
    )

    print(f"\n[1/4] COMPLETE: {report.total_cycles} cycles in {report.total_elapsed:.1f}s")
    print(f"      Snapshots captured: {len(report.snapshots)}")
    for snap in report.snapshots:
        print(f"        {snap['change']}: disc={snap['discrimination']:.4f}, "
              f"res={snap['resonance_best']:.4f}, "
              f"pw={json.dumps({k: round(v, 3) for k, v in snap['path_weights'].items()})}")
    print()

    # Print meta log
    print("--- Meta-Observer Log ---")
    for line in report.meta_log:
        print(line)
    print("--- End Log ---\n")

    # ── Phase 2: Create holographic crystal ──────────────────────
    print("[2/4] Creating holographic crystal...")
    print("      Combining 3 snapshots with golden-ratio blending")
    print("      Inverting through midpoint")
    print("      Rotating 90° for 4 SFCR face projections")
    print("      Computing Sigma-60 icosahedral symmetry")
    print("      Expanding to 240 (4×60) and 720 (3×240)")
    print("      Mapping sacred geometry: nexus + zero-point + aether")
    print()

    crystal = create_holographic_crystal(report.snapshots, report.final_weights)

    print(f"      Sigma-60 states: {len(crystal['sigma_60'])}")
    print(f"      240 expansion: {crystal['expansion_240']['count']}")
    print(f"      720 expansion: {crystal['expansion_720']['count']}")
    print(f"      Nexus points: {crystal['sacred_geometry']['nexus_points']['total_nexus']}")
    print()

    # Print A+ crystal
    a_plus = crystal["a_plus_crystal"]
    print("[3/4] A+ CRYSTAL computed:")
    print(f"      Path weights:  {json.dumps({k: round(v, 4) for k, v in a_plus['path_weights'].items()})}")
    print(f"      Resonance:     {json.dumps({k: round(v, 4) for k, v in a_plus['resonance_weights'].items()})}")
    print(f"      Desire:        {json.dumps({k: round(v, 4) for k, v in a_plus['desire_weights'].items()})}")
    print(f"      Bridge mod:    {a_plus['bridge_modulation']:.4f}")
    print(f"      Geo blend:     {a_plus['geo_arith_blend']:.4f}")
    print()

    # Print zero-point and aether
    zp = crystal["sacred_geometry"]["zero_point"]
    ae = crystal["sacred_geometry"]["aether_point"]
    print("      Zero-point (absolute balance):")
    print(f"        Path weights: {json.dumps({k: round(v, 4) for k, v in zp['path_weights'].items()})}")
    print("      Aether point (unseen potential):")
    print(f"        Path weights: {json.dumps({k: round(v, 4) for k, v in ae['path_weights'].items()})}")
    print()

    # Print face projections
    print("      4 SFCR Face Projections:")
    for face, fdata in crystal["faces"].items():
        print(f"        {face} ({fdata['element']}): "
              f"{json.dumps({k: round(v, 4) for k, v in fdata['path_weights'].items()})}")
    print()

    # Print golden nexus pairs
    print("      Cross-element nexus points:")
    for cn in crystal["sacred_geometry"]["nexus_points"]["cross_element_nexus"]:
        golden_mark = " [GOLDEN]" if cn["golden"] else ""
        print(f"        {cn['pair']}: {json.dumps({k: round(v, 4) for k, v in cn['nexus_path_weights'].items()})}{golden_mark}")
    print()

    # ── Phase 3: Rewire weights ──────────────────────────────────
    print("[4/4] REWIRING neural weights to A+ crystal...")
    result = rewire_weights_to_a_plus(a_plus)
    print(f"      {result}")
    print()

    # ── Save full crystal to JSON ────────────────────────────────
    crystal_path = Path(__file__).parent / "MCP" / "data" / "a_plus_crystal.json"
    # Remove large arrays for JSON storage (keep summaries)
    save_crystal = dict(crystal)
    save_crystal["sigma_60"] = crystal["sigma_60"][:12]  # first 12 as sample
    save_crystal["sigma_60_note"] = f"Showing 12 of {len(crystal['sigma_60'])} total sigma-60 states"

    with open(crystal_path, "w", encoding="utf-8") as f:
        json.dump(save_crystal, f, indent=2, default=str)
    print(f"      Full A+ crystal saved to: {crystal_path}")

    total_time = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"N^3 ALCHEMY COMPLETE")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Total cycles: {report.total_cycles}")
    print(f"  3 changes applied: SULFUR -> SALT -> MERCURY")
    print(f"  Holographic crystal: 60 -> 240 -> 720 symmetry states")
    print(f"  Sacred geometry: {crystal['sacred_geometry']['nexus_points']['total_nexus']} nexus points")
    print(f"  A+ crystal weights APPLIED to neural engine")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
