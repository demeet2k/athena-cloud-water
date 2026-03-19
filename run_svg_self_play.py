#!/usr/bin/env python3
"""
SVG Self-Play Runner — Standalone Training Script
===================================================
Runs SVG generation self-play sessions with configurable rounds,
categories, and difficulty progression. Prints improvement trajectory
and saves outputs to MCP/data/svg_arena/.

Usage:
    python run_svg_self_play.py                    # 10 progressive rounds
    python run_svg_self_play.py --rounds 20        # 20 rounds
    python run_svg_self_play.py --category sacred  # sacred geometry only
    python run_svg_self_play.py --all              # all 25 challenges
"""

import argparse
import os
import sys
import time

# Ensure MCP package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "MCP"))

from crystal_108d.svg_challenges import catalog, save_catalog
from crystal_108d.svg_self_play import SVGSelfPlayEngine, ARENA_DIR, OUTPUT_DIR


def main():
    parser = argparse.ArgumentParser(description="SVG Self-Play Improvement Runner")
    parser.add_argument("--rounds", type=int, default=10,
                        help="Number of rounds to run (default: 10)")
    parser.add_argument("--category", type=str, default="",
                        help="Filter by category: primitive|composite|sacred|fractal|crystal")
    parser.add_argument("--progressive", action="store_true", default=True,
                        help="Increase difficulty progressively (default: true)")
    parser.add_argument("--no-progressive", dest="progressive", action="store_false",
                        help="Random difficulty order")
    parser.add_argument("--attempts", type=int, default=5,
                        help="Max attempts per challenge (default: 5)")
    parser.add_argument("--all", action="store_true",
                        help="Run all 25 challenges")
    args = parser.parse_args()

    print("=" * 60)
    print("  SVG SELF-PLAY IMPROVEMENT ENGINE")
    print("=" * 60)
    print()

    # Save challenge catalog
    save_catalog()
    print(f"Challenge catalog saved to {ARENA_DIR / 'challenges.json'}")
    print(f"Total challenges available: {len(catalog())}")
    print()

    engine = SVGSelfPlayEngine(max_attempts=args.attempts)

    if args.all:
        challenges = catalog()
        rounds = len(challenges)
    else:
        challenges = None
        rounds = args.rounds

    t0 = time.monotonic()

    if challenges:
        # Run all challenges explicitly
        results = []
        for ch in challenges:
            rnd = engine.run_round(ch)
            results.append(rnd)
            _print_round(rnd)
        engine._save_history()
    else:
        results = engine.run_session(
            rounds=rounds,
            progressive=args.progressive,
            category=args.category or None,
        )
        for rnd in results:
            _print_round(rnd)

    elapsed = time.monotonic() - t0

    # Summary
    print()
    print("=" * 60)
    print("  SESSION SUMMARY")
    print("=" * 60)
    if results:
        scores = [r.best_score for r in results]
        print(f"  Rounds completed:  {len(results)}")
        print(f"  Best score:        {max(scores):.4f}")
        print(f"  Average score:     {sum(scores)/len(scores):.4f}")
        print(f"  Worst score:       {min(scores):.4f}")
        print(f"  Total time:        {elapsed:.1f}s")
        print(f"  Outputs directory: {OUTPUT_DIR}")
        print()

        # Improvement trajectory
        print("  IMPROVEMENT TRAJECTORY:")
        for rnd in results:
            traj = rnd.improvement_trajectory
            ch_name = rnd.challenge.name if rnd.challenge else "?"
            bar_len = int(rnd.best_score * 40)
            bar = "#" * bar_len + "." * (40 - bar_len)
            print(f"    {ch_name:30s} [{bar}] {rnd.best_score:.3f}")
    else:
        print("  No rounds completed.")
    print()


def _print_round(rnd):
    """Print a single round result."""
    ch = rnd.challenge
    ch_name = ch.name if ch else "?"
    ch_cat = ch.category if ch else "?"
    ch_diff = ch.difficulty if ch else 0
    traj = rnd.improvement_trajectory
    improvement = traj[-1] - traj[0] if len(traj) > 1 else 0

    print(f"  Round {rnd.round_id:3d} | {ch_name:30s} | "
          f"cat={ch_cat:10s} | d={ch_diff:.2f} | "
          f"score={rnd.best_score:.3f} | delta={improvement:+.3f} | "
          f"attempts={len(rnd.attempts)}")


if __name__ == "__main__":
    main()
