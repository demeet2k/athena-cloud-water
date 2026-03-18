#!/usr/bin/env python3
"""
Execute the FULL TRAINING LOOP: ABCD+ Crystal Transmutation
  Stage A: 3 runs x 3 changes = 9 waves
  Stage B: 5 runs x 4 elements = 20 waves
  Stage C: 7 runs x 7 metals/planets = 49 waves (escalating)
  Stage D: 9 runs x 9 completions (3x3) = 81 waves
  Final: Invert + Rotate + Poles + QSHRINK + Hologram
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "MCP"))

from crystal_108d.full_training_loop import run_full_training_loop


def main():
    t0 = time.time()

    result = run_full_training_loop(
        cycles_a=500,    # 9 waves x 500 = 4,500 cycles
        cycles_b=400,    # 20 waves x 400 = 8,000 cycles
        cycles_c=300,    # 49 waves x 300 = 14,700 cycles
        cycles_d=250,    # 81 waves x 250 = 20,250 cycles
        max_time_minutes=45,  # hard cap
    )

    print(f"\n\nDone. {result['total_cycles']} cycles, "
          f"{result['total_waves']} waves, "
          f"{result['total_elapsed']:.1f}s")
    print(f"Hologram saved to: {result['hologram_path']}")


if __name__ == "__main__":
    main()
