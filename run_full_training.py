#!/usr/bin/env python3
"""Run one ABCD+ cycle with the supported native momentum training engine.

The former full_training_loop/crystal_weights engine is absent from this
checkout. This entrypoint uses MetaLoopEngine, which replaces that engine;
its output is the native momentum hologram, not a legacy weight hologram.
"""

import argparse
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "MCP"))


def positive_minutes(value):
    minutes = float(value)
    if not math.isfinite(minutes) or minutes <= 0:
        raise argparse.ArgumentTypeError("minutes must be finite and positive")
    return minutes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check native imports without training or writing data")
    parser.add_argument("--max-time-minutes", type=positive_minutes, default=45,
                        help="cooperative time budget checked between waves")
    args = parser.parse_args(argv)
    from crystal_108d.meta_loop_engine import MetaLoopEngine, MetaLoopConfig
    if args.check:
        print("Native MetaLoopEngine ready; legacy weight trainer is not used.")
        return 0
    results = MetaLoopEngine().run(MetaLoopConfig(depth=1, max_time_minutes=args.max_time_minutes))
    print(json.dumps([asdict(result) for result in results], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
