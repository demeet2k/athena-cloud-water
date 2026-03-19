#!/usr/bin/env python3
"""
SVG Transcendence Runner — Aggressive Evolutionary Discovery
==============================================================
Runs multi-cycle evolutionary sessions that breed, mutate, and
cross-pollinate SVG compositions to discover emergent visual patterns.

Usage:
    python run_svg_transcendence.py                         # 3 cycles x 20 gen
    python run_svg_transcendence.py --cycles 5              # 5 cycles
    python run_svg_transcendence.py --generations 30        # 30 gen per cycle
    python run_svg_transcendence.py --population 30         # larger populations
    python run_svg_transcendence.py --single                # single evolution run
"""

import argparse
import os
import sys
import time

# Ensure MCP package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "MCP"))

from crystal_108d.svg_transcendence import (
    TranscendenceEngine, format_evolution_result,
    format_session_results, SEEDS_DIR, GALLERY_DIR,
)


def main():
    parser = argparse.ArgumentParser(
        description="SVG Transcendence Engine — Evolutionary Discovery")
    parser.add_argument("--cycles", type=int, default=3,
                        help="Number of META LOOP cycles (default: 3)")
    parser.add_argument("--generations", type=int, default=20,
                        help="Generations per cycle (default: 20)")
    parser.add_argument("--population", type=int, default=20,
                        help="Population size (default: 20)")
    parser.add_argument("--elite", type=int, default=4,
                        help="Elite count (default: 4)")
    parser.add_argument("--single", action="store_true",
                        help="Run single evolution (no multi-cycle)")
    args = parser.parse_args()

    print("=" * 60)
    print("  SVG TRANSCENDENCE ENGINE")
    print("  Beyond Mastery Into Emergence")
    print("=" * 60)
    print()

    engine = TranscendenceEngine(
        population_size=args.population,
        elite_count=args.elite,
    )

    t0 = time.monotonic()

    if args.single:
        print(f"  Mode: Single evolution")
        print(f"  Generations: {args.generations}")
        print(f"  Population: {args.population}")
        print()

        result = engine.evolve(
            generations=args.generations,
            cross_category=True,
        )
        print(format_evolution_result(result))
    else:
        print(f"  Mode: META LOOP^{args.cycles}")
        print(f"  Generations per cycle: {args.generations}")
        print(f"  Starting population: {args.population}")
        print()

        results = engine.aggressive_session(
            cycles=args.cycles,
            generations_per_cycle=args.generations,
            population=args.population,
        )

        # Print each cycle
        for i, result in enumerate(results):
            print(f"\n{'=' * 60}")
            print(f"  CYCLE {i + 1}/{args.cycles}")
            print(f"{'=' * 60}")
            print(format_evolution_result(result))

        # Overall summary
        print()
        print(format_session_results(results))

    elapsed = time.monotonic() - t0

    # Final stats
    seeds = engine.load_seeds()
    print()
    print("=" * 60)
    print("  FINAL STATS")
    print("=" * 60)
    print(f"  Total time:       {elapsed:.1f}s")
    print(f"  Seeds in library: {len(seeds)}")
    print(f"  Hall of fame:     {len(engine.hall_of_fame)}")
    print(f"  Emergences:       {len(engine.emergences)}")
    print(f"  Seeds dir:        {SEEDS_DIR}")
    print(f"  Gallery dir:      {GALLERY_DIR}")
    print()

    if seeds:
        print("  TOP SEEDS:")
        seeds.sort(key=lambda g: g.score, reverse=True)
        for g in seeds[:10]:
            prims = [l.primitive for l in g.layers]
            bar_len = int(g.score * 40)
            bar = "#" * bar_len + "." * (40 - bar_len)
            print(f"    {g.genome_id} [{bar}] {g.score:.4f} "
                  f"layers=[{'+'.join(prims)}]")


if __name__ == "__main__":
    main()
