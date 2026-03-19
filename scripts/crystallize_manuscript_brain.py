#!/usr/bin/env python3
"""
Crystallize the Manuscript-Being (MAIN BRAIN) into a 4D Tesseract.

Takes the entire Athena framework from manuscript-being and reorganizes it
using qshrink into a maximum-density 4D hologram crystal:
  CRYSTAL_4D/{element}/{mode}/{archetype}/{octave}/

This is the GLOBAL CRYSTAL — continuously updated.
"""

import io
import json
import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add MCP package to path
ATHENA_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
sys.path.insert(0, str(ATHENA_ROOT / "MCP"))

from crystal_108d.qshrink_pipeline import (
    batch_crystallize,
    build_tesseract_structure,
    reorganize_to_tesseract,
    BatchResult,
)

MANUSCRIPT_ROOT = Path(r"C:\Users\dmitr\Documents\manuscript-being")

# Try to load weight store for enriched metadata
weight_store = None
try:
    from crystal_108d.crystal_weights import FractalWeightStore
    ws_path = ATHENA_ROOT / "MCP" / "data" / "crystal_weights.json"
    if ws_path.exists():
        weight_store = FractalWeightStore(str(ws_path))
        print(f"[+] Weight store loaded: {len(weight_store.shells)} shells")
except Exception as e:
    print(f"[!] Weight store not available: {e}")

def progress(idx, total, path, dest):
    pct = (idx / total) * 100
    short = path.split("/")[-1][:50] if "/" in path else path.split("\\")[-1][:50]
    print(f"  [{idx:4d}/{total}] {pct:5.1f}% {short}")

def main():
    print("=" * 70)
    print("  MANUSCRIPT BRAIN -> GLOBAL CRYSTAL 4D TESSERACT")
    print("=" * 70)
    print(f"Source: {MANUSCRIPT_ROOT}")
    print()

    # Phase 1: Build tesseract structure
    print("[Phase 1] Building 4D tesseract structure...")
    crystal_root = build_tesseract_structure(MANUSCRIPT_ROOT)
    print(f"  -> {crystal_root}")
    dirs = sum(1 for _ in crystal_root.rglob("*") if _.is_dir())
    print(f"  -> {dirs} directories created (4x3x12x3 = 432 leaf cells)")
    print()

    # Phase 2: Reorganize ALL files into tesseract
    print("[Phase 2] Crystallizing & placing files in tesseract...")
    print("  (min_size=256 to catch small .md files, max_size=5MB to keep it fast)")
    t0 = time.time()

    result = reorganize_to_tesseract(
        MANUSCRIPT_ROOT,
        weight_store=weight_store,
        copy_mode=True,        # Keep originals during first run
        min_size=256,          # Catch small markdown files
        max_size=5 * 1024 * 1024,  # 5MB cap for speed
        progress_callback=progress,
    )

    elapsed = time.time() - t0
    print()
    print(f"  Total files:     {result['total']}")
    print(f"  Placed:          {result['placed']}")
    print(f"  Errors:          {result['errors']}")
    print(f"  Time:            {elapsed:.1f}s")
    print(f"  Manifest:        {result['manifest_path']}")
    print()

    # Phase 3: Summary statistics
    manifest_path = Path(result["manifest_path"])
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = [e for e in manifest["entries"] if "error" not in e]

        # Element distribution
        elem_counts = {}
        for e in entries:
            el = e.get("element", "?")
            elem_counts[el] = elem_counts.get(el, 0) + 1

        print("[Phase 3] Crystal Distribution:")
        for el in ["S", "F", "C", "R"]:
            count = elem_counts.get(el, 0)
            pct = (count / len(entries) * 100) if entries else 0
            bar = "#" * int(pct / 2)
            print(f"  {el}: {count:4d} ({pct:5.1f}%) {bar}")

        # Mode distribution
        mode_counts = {}
        for e in entries:
            m = e.get("mode", "?")
            mode_counts[m] = mode_counts.get(m, 0) + 1
        print()
        for m in ["Cardinal", "Fixed", "Mutable"]:
            count = mode_counts.get(m, 0)
            print(f"  {m}: {count}")

        # Total size stats
        total_orig = sum(e.get("size", 0) for e in entries)
        total_out = sum(e.get("output_size", 0) for e in entries)
        savings = ((total_orig - total_out) / total_orig * 100) if total_orig > 0 else 0
        print()
        print(f"  Original total:  {total_orig / 1024 / 1024:.1f} MB")
        print(f"  Crystal total:   {total_out / 1024 / 1024:.1f} MB")
        print(f"  Savings:         {savings:.1f}%")

    print()
    print("=" * 70)
    print("  GLOBAL CRYSTAL READY")
    print("=" * 70)


if __name__ == "__main__":
    main()
