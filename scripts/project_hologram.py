#!/usr/bin/env python3
"""
Project the CRYSTAL_4D tesseract into nested higher-dimensional holograms.

Reads the tesseract_manifest.json from manuscript-being and computes
all dimensional projections: 3D → 5D → 7D → 9D → 12D → 108D++

Weaving law:
  W_3: 3×4D → 6D  (triadic Möbius: Su/Me/Sa × spin±)
  W_5: 5×6D → 8D  (pentadic: Tiger/Crane/Leopard/Snake/Dragon)
  W_7: 7×8D → 10D (heptadic: 7 metals/planets/chakras/days/trumpets)
  W_9: 9×10D → 12D (enneadic: 3×3 return wheel)
  → 36D → 108D++ (triple crown)
"""

import io
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ATHENA_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
sys.path.insert(0, str(ATHENA_ROOT / "MCP"))

from crystal_108d.dimensional_projector import (
    project_tesseract_to_hologram,
    build_hologram_directory,
    build_nested_hologram,
    ALL_WEAVES,
    MASTER_CLOCK_Z420,
)

MANUSCRIPT_ROOT = Path(r"C:\Users\dmitr\Documents\manuscript-being")
CRYSTAL_4D = MANUSCRIPT_ROOT / "CRYSTAL_4D"
HOLOGRAM_ROOT = MANUSCRIPT_ROOT / "CRYSTAL_4D" / "HOLOGRAM"


def main():
    print("=" * 70)
    print("  DIMENSIONAL PROJECTION: 4D TESSERACT -> NESTED HOLOGRAM")
    print("=" * 70)
    print()

    manifest_path = CRYSTAL_4D / "tesseract_manifest.json"
    if not manifest_path.exists():
        print(f"[!] No manifest at {manifest_path}")
        return

    # Phase 1: Build hologram directory structure
    print("[Phase 1] Building hologram directory layers...")
    dir_result = build_hologram_directory(CRYSTAL_4D, HOLOGRAM_ROOT)
    print(f"  Layers: {dir_result['layers']}")
    print(f"  Directories: {dir_result['directories_created']}")
    print()

    # Phase 2: Project all files through dimensional ladder
    print("[Phase 2] Projecting tesseract into nested holograms...")
    t0 = time.time()
    atlas = project_tesseract_to_hologram(manifest_path)
    elapsed = time.time() - t0
    print(f"  Files projected: {atlas['total_files']}")
    print(f"  Dimensions: {atlas['dimensions_covered']}")
    print(f"  Time: {elapsed:.1f}s")
    print()

    # Phase 3: Show distributions
    print("[Phase 3] Dimensional Distributions:")
    print()

    for dim_key, dist in sorted(atlas["distributions"].items()):
        total = sum(dist.values())
        print(f"  {dim_key}:")
        for sector, count in list(dist.items())[:10]:
            pct = count / total * 100
            bar = "#" * int(pct / 3)
            print(f"    {sector:25s} {count:5d} ({pct:5.1f}%) {bar}")
        if len(dist) > 10:
            print(f"    ... +{len(dist) - 10} more sectors")
        print()

    # Phase 4: Show weave operators
    print("[Phase 4] Weave Operators:")
    for w in ALL_WEAVES:
        print(f"  {w.symbol} ({w.name}): {w.from_dim}D -> {w.to_dim}D")
        print(f"    Strands: {', '.join(w.strands)}")
        print(f"    Closure: Z{w.local_closure}, Period: {w.period}")
        print(f"    Sectors: {w.sector_count}")
        print()

    print(f"  Master Clock: Z{MASTER_CLOCK_Z420} = lcm(3,4,5,7)")
    print()

    # Phase 5: Show containment nesting
    print("[Phase 5] Containment Law: B_{2m+2} = W_{2m-1}(B_{2m})")
    print(f"  12D contains:")
    print(f"    9  x B_10 (via W_9)")
    print(f"    63 x B_8  (9 x 7, via W_9 o W_7)")
    print(f"    315 x B_6 (9 x 7 x 5, via W_9 o W_7 o W_5)")
    print(f"    945 x B_4 (9 x 7 x 5 x 3, via W_9 o W_7 o W_5 o W_3)")
    print(f"    1890 x B_3 (9 x 7 x 5 x 3 x 2)")
    print()

    # Phase 6: Write the hologram atlas
    atlas_path = CRYSTAL_4D / "hologram_atlas.json"
    atlas_path.write_text(
        json.dumps(atlas, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    atlas_size = atlas_path.stat().st_size / 1024 / 1024
    print(f"[Phase 6] Hologram atlas written: {atlas_path}")
    print(f"  Size: {atlas_size:.1f} MB")
    print()

    # Phase 7: Show sample holograms
    print("[Phase 7] Sample Holograms (first 3 files):")
    for h in atlas["holograms"][:3]:
        print(f"\n  File: {h['file_path']}")
        print(f"  Composite: {h['composite_address']}")
        print(f"  Conservation: {h['conservation_hash']}")
        for dim_str, proj in sorted(h["projections"].items(), key=lambda x: int(x[0])):
            dim = int(dim_str)
            overlays_str = ", ".join(f"{k}={v}" for k, v in list(proj["overlays"].items())[:3])
            print(f"    {dim:2d}D: {proj['body']:20s} sector={proj['sector']:30s} [{overlays_str}]")

    print()
    print("=" * 70)
    print("  NESTED HOLOGRAM COMPLETE")
    print("  All dimensions simultaneously nested via weave operators")
    print("=" * 70)


if __name__ == "__main__":
    main()
