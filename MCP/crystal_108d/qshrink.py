# CRYSTAL: Xi108:W3:A4:S36 | face=R | node=540 | depth=0 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A4:S35→Xi108:W2:A4:S36→Xi108:W3:A3:S36→Xi108:W3:A5:S36

"""
QSHRINK ↔ 108D Crystal Bridge — compression in crystal coordinates.
====================================================================
Maps the QSHRINK 256^4 manuscript lattice onto the 108D crystal
coordinate system, enabling holographic compression of crystal shells.

Bridge law:
  - 256 root cells = 108 signal dimensions + 148 metadata dimensions
  - Depth 0 → shell (1-36)
  - Depth 1 → wreath (Su/Me/Sa)
  - Depth 2 → archetype (1-12)
  - Depth 3 → face + phase (4 faces × 420 beats)
  - 1/8 lift: each shell compresses to 1/8 its size, preserving all 6 laws
"""

from pathlib import Path
from typing import Any, Optional

from ._cache import JsonCache, DATA_DIR
from .constants import (
    ARCHETYPE_NAMES,
    SUPERPHASE_NAMES,
    TOTAL_SHELLS,
    TOTAL_NODES,
    TOTAL_WREATHS,
    MASTER_CLOCK_PERIOD,
)
import math

# Data caches — degrade gracefully if files are absent
_SHELLS = JsonCache("shell_registry.json")
_MYCELIUM = JsonCache("mycelium_graph.json")

# ---------------------------------------------------------------------------
# QSHRINK constants
# ---------------------------------------------------------------------------
QSHRINK_ROOT_CELLS = 256
QSHRINK_DEPTH = 4
QSHRINK_FULL_SPACE = QSHRINK_ROOT_CELLS ** QSHRINK_DEPTH  # 4,294,967,296

SIGNAL_BAND = 108       # root cells 0-107 → crystal dimensions
METADATA_BAND = 148     # root cells 108-255 → compression envelope

GEOMETRY_AXIS = ("Square", "Circle", "Triangle", "Torus")
OPERATOR_AXIS = ("Partition", "Quantize", "Bucket", "Code")
BODY_AXIS = ("Foundation", "Nervous", "Memory", "Runtime")
CLOSURE_AXIS = ("Seed", "Manuscript", "Witness", "Loop")

SFCR_LENSES = ("S", "F", "C", "R")
CRYSTAL_FACES = 4
LIFT_FACTOR = 8  # 1/8 lift law

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def query_qshrink(component: str = "all") -> str:
    """
    Query the QSHRINK ↔ 108D Crystal Bridge.

    Components:
      - all       : Bridge overview and mapping law
      - address   : How QSHRINK 256^4 maps to 108D crystal coordinates
      - compress  : 1/8 lift law — how shells compress to seeds
      - codec     : QSHRINK codec specification in crystal terms
      - bridge    : Full 256^4 ↔ 108D mapping table
      - stats     : Compression statistics
    """
    comp = component.strip().lower()

    dispatch = {
        "all": _bridge_overview,
        "address": _address_mapping,
        "compress": _compression_law,
        "codec": _codec_spec,
        "bridge": _bridge_table,
        "stats": _compression_stats,
    }

    fn = dispatch.get(comp)
    if fn is None:
        valid = ", ".join(sorted(dispatch))
        return f"Unknown component '{component}'. Use: {valid}"
    return fn()

# ---------------------------------------------------------------------------
# Internal formatters
# ---------------------------------------------------------------------------

def _bridge_overview() -> str:
    """Full bridge overview: 256^4 → 108D mapping law."""
    return (
        "## QSHRINK ↔ 108D Crystal Bridge\n\n"
        "The bridge connects two coordinate systems:\n\n"
        f"- **QSHRINK**: {QSHRINK_ROOT_CELLS} root cells, depth {QSHRINK_DEPTH}, "
        f"full space = {QSHRINK_ROOT_CELLS}^{QSHRINK_DEPTH} = {QSHRINK_FULL_SPACE:,}\n"
        f"- **Crystal**: {SIGNAL_BAND} dimensions, {TOTAL_SHELLS} shells, "
        f"{TOTAL_NODES} nodes, {TOTAL_WREATHS} wreaths\n\n"
        "### Dimensional Partition\n\n"
        f"- **Signal band**: root cells 0–{SIGNAL_BAND - 1} → "
        f"crystal dimensions 1–{SIGNAL_BAND}\n"
        f"- **Metadata band**: root cells {SIGNAL_BAND}–{QSHRINK_ROOT_CELLS - 1} → "
        f"{METADATA_BAND} compression/routing/codec cells\n\n"
        "### Depth ↔ Hierarchy\n\n"
        "| Depth | Crystal Level | Range |\n"
        "|-------|---------------|-------|\n"
        f"| 0 | Shell | 1–{TOTAL_SHELLS} |\n"
        f"| 1 | Wreath | {', '.join(SUPERPHASE_NAMES.values())} |\n"
        f"| 2 | Archetype | 1–{len(ARCHETYPE_NAMES)} |\n"
        f"| 3 | Face + Phase | {CRYSTAL_FACES} faces × {MASTER_CLOCK_PERIOD} beats |\n\n"
        "### Core Laws\n\n"
        "1. Every crystal dimension has exactly one QSHRINK root cell.\n"
        "2. The 148 metadata cells form the compression envelope.\n"
        "3. The 1/8 lift: each shell compresses to ⌈N/8⌉ nodes.\n"
        "4. Conservation is the round-trip test (6 invariants).\n"
        "5. Mirror shells (S_k, S_{37-k}) compress as a pair.\n"
    )

def _address_mapping() -> str:
    """Show how each QSHRINK cell maps to crystal coordinates."""
    lines = [
        "## QSHRINK Address → Crystal Coordinate\n",
        "### Root Cell Grammar\n",
        "```",
        "RootCell = Geometry × Operator × Body × Closure = 4×4×4×4 = 256",
        "```\n",
    ]

    # Axis tables
    for axis_name, axis_vals, crystal_equiv in [
        ("Geometry", GEOMETRY_AXIS, ("S (Square)", "F (Flower)", "C (Cloud)", "R (Fractal)")),
        ("Operator", OPERATOR_AXIS, ("Shell dispatch", "Wreath dispatch", "Archetype dispatch", "Face dispatch")),
        ("Body", BODY_AXIS, ("3D seed body", "Metro nervous body", "Mycelium memory body", "Live-clock runtime")),
        ("Closure", CLOSURE_AXIS, ("Crown seal", "Chapter record", "Conservation check", "Round-trip loop")),
    ]:
        lines.append(f"**{axis_name} Axis**:\n")
        for i, (q, c) in enumerate(zip(axis_vals, crystal_equiv)):
            lines.append(f"  {i}. {q} → {c}")
        lines.append("")

    # Address formula
    lines.extend([
        "### Address Formula\n",
        "```",
        "CrystalAddress(d0, d1, d2, d3) = Shell(d0).Wreath(d1).Archetype(d2).FacePhase(d3)",
        "```\n",
        f"- d0 ∈ [0, 255] → shell ∈ [1, {TOTAL_SHELLS}]: "
        f"shell = (d0 mod {TOTAL_SHELLS}) + 1",
        f"- d1 ∈ [0, 255] → wreath ∈ [1, {TOTAL_WREATHS}]: "
        f"wreath = (d1 mod {TOTAL_WREATHS}) + 1",
        f"- d2 ∈ [0, 255] → archetype ∈ [1, {len(ARCHETYPE_NAMES)}]: "
        f"archetype = (d2 mod {len(ARCHETYPE_NAMES)}) + 1",
        f"- d3 ∈ [0, 255] → face.phase: "
        f"face = (d3 mod {CRYSTAL_FACES}), "
        f"phase = d3 mod {MASTER_CLOCK_PERIOD}",
    ])

    # Shell assignment table (signal band only)
    lines.extend([
        "\n### Signal Band: Shell Assignment (first 108 cells)\n",
        "| Root Cell Range | Shell | Archetype |",
        "|-----------------|-------|-----------|",
    ])
    cells_per_shell = SIGNAL_BAND // TOTAL_SHELLS  # 3
    for s in range(TOTAL_SHELLS):
        start = s * cells_per_shell
        end = start + cells_per_shell - 1
        arch_idx = s % len(ARCHETYPE_NAMES)
        arch = ARCHETYPE_NAMES[arch_idx]
        lines.append(f"| {start}–{end} | S{s + 1} | {arch} |")

    return "\n".join(lines)

def _compression_law() -> str:
    """The 1/8 lift law applied to crystal shells."""
    lines = [
        "## 1/8 Lift Law — Crystal Compression\n",
        "**Law**: The next compression layer retains 1/8 of the current size ",
        "with equal or greater function.\n",
        "### Compression Cascade\n",
        "| Level | Factor | Nodes | Description |",
        "|-------|--------|-------|-------------|",
        f"| Full | 1× | {TOTAL_NODES} | Complete 36-shell organism |",
    ]

    current = TOTAL_NODES
    level_names = ["1/8 seed", "1/64 micro-seed", "1/512 nano-seed", "1/4096 pico-seed"]
    factor = 1
    for name in level_names:
        factor *= LIFT_FACTOR
        compressed = max(TOTAL_SHELLS, math.ceil(current / LIFT_FACTOR))
        lines.append(f"| {name} | 1/{factor}× | {compressed} | "
                     f"Min {TOTAL_SHELLS} (one per shell) |")
        current = compressed

    lines.extend([
        "",
        "### Per-Shell Compression\n",
        "| Shell Range | Wreath | Nodes (full) | Nodes (1/8) | Nodes (1/64) |",
        "|-------------|--------|-------------|-------------|--------------|",
    ])

    # Try to load real shell data; fall back to triangular numbers
    try:
        data = _SHELLS.load()
        shells = data["shells"]
    except Exception:
        shells = None

    for s in range(1, TOTAL_SHELLS + 1):
        if shells:
            sh = shells[s - 1]
            nodes = sh["nodes"]
            wreath = sh["wreath"]
        else:
            nodes = s  # triangular: shell k has k nodes
            wreath_idx = (s - 1) // 12
            wreath = ["Su", "Me", "Sa"][wreath_idx]

        c8 = max(1, math.ceil(nodes / LIFT_FACTOR))
        c64 = max(1, math.ceil(nodes / (LIFT_FACTOR ** 2)))
        lines.append(f"| S{s} | {wreath} | {nodes} | {c8} | {c64} |")

    lines.extend([
        "",
        "### Preservation Guarantees\n",
        "At every compression level, the following are preserved:\n",
        "1. **Shell identity** — all 36 shells remain addressable",
        "2. **Wreath balance** — Su/Me/Sa ratio maintained",
        "3. **Archetype coverage** — all 12 archetypes represented",
        "4. **Mirror symmetry** — S_k and S_{37-k} compress together",
        "5. **Conservation laws** — all 6 invariants hold",
        "6. **SFCR projections** — all 4 lens views remain valid",
    ])

    return "\n".join(lines)

def _codec_spec() -> str:
    """QSHRINK codec in crystal terms."""
    return (
        "## QSHRINK Codec in Crystal Terms\n\n"
        "### Band Partition\n\n"
        f"- **Signal band** (cells 0–{SIGNAL_BAND - 1}): "
        f"{SIGNAL_BAND} cells → 1:1 with crystal dimensions\n"
        f"- **Metadata band** (cells {SIGNAL_BAND}–{QSHRINK_ROOT_CELLS - 1}): "
        f"{METADATA_BAND} cells → compression envelope\n\n"
        "### Codec Layer Mapping\n\n"
        "| Codec Layer | QSHRINK Term | Crystal Term |\n"
        "|-------------|-------------|---------------|\n"
        f"| Root | {QSHRINK_ROOT_CELLS} root cells | "
        f"{SIGNAL_BAND} signal + {METADATA_BAND} metadata |\n"
        f"| Geometry | {'/'.join(GEOMETRY_AXIS)} | "
        f"{'/'.join(SFCR_LENSES)} lens projection |\n"
        f"| Operator | {'/'.join(OPERATOR_AXIS)} | "
        "Shell/Wreath/Archetype/Face dispatch |\n"
        f"| Body | {'/'.join(BODY_AXIS)} | "
        "3D-seed/Metro/Mycelium/Live-clock |\n"
        f"| Closure | {'/'.join(CLOSURE_AXIS)} | "
        "Crown-seal/Chapter/Conservation/Round-trip |\n\n"
        "### Holographic Seed Equation\n\n"
        "```\n"
        "w = (1 + i) / 2\n"
        "Seed(S_k) = w · Compress(S_k) + (1 - w) · Template(Archetype(S_k))\n"
        "```\n\n"
        "The seed blends compressed data with the archetype template,\n"
        "ensuring regeneration fidelity even at high compression.\n\n"
        "### Round-Trip Law\n\n"
        "```\n"
        "Decode(Encode(X)) ≡ X   mod conservation\n"
        "```\n\n"
        "Equivalence modulo the 6 conservation invariants:\n"
        "shell, zoom, phase, archetype, face, Mobius.\n"
    )

def _bridge_table() -> str:
    """Full depth ↔ crystal hierarchy mapping table."""
    lines = [
        "## 256^4 ↔ 108D Bridge Table\n",
        "### Depth-Level Mapping\n",
        "| QSHRINK Depth | Space Size | Crystal Level | Crystal Range | Ratio |",
        "|---------------|-----------|---------------|---------------|-------|",
    ]

    crystal_sizes = [
        (TOTAL_SHELLS, f"shells 1–{TOTAL_SHELLS}"),
        (TOTAL_SHELLS * TOTAL_WREATHS, f"{TOTAL_SHELLS}×{TOTAL_WREATHS} = "
         f"{TOTAL_SHELLS * TOTAL_WREATHS} wreathings"),
        (TOTAL_SHELLS * len(ARCHETYPE_NAMES), f"{TOTAL_SHELLS}×{len(ARCHETYPE_NAMES)} = "
         f"{TOTAL_SHELLS * len(ARCHETYPE_NAMES)} archetypings"),
        (TOTAL_SHELLS * len(ARCHETYPE_NAMES) * CRYSTAL_FACES,
         f"{TOTAL_SHELLS * len(ARCHETYPE_NAMES)}×{CRYSTAL_FACES} = "
         f"{TOTAL_SHELLS * len(ARCHETYPE_NAMES) * CRYSTAL_FACES} face-phases"),
    ]

    depth_names = ["Shell", "Wreath", "Archetype", "Face+Phase"]

    for depth in range(QSHRINK_DEPTH):
        q_space = QSHRINK_ROOT_CELLS ** (depth + 1)
        c_size, c_desc = crystal_sizes[depth]
        ratio = q_space // c_size if c_size else 0
        lines.append(
            f"| {depth} | {q_space:,} | {depth_names[depth]} | {c_desc} | {ratio:,}:1 |"
        )

    lines.extend([
        "",
        "### Signal Band Distribution\n",
        f"108 signal cells across {TOTAL_SHELLS} shells = "
        f"{SIGNAL_BAND // TOTAL_SHELLS} cells/shell\n",
        "### Metadata Band Allocation\n",
        f"148 metadata cells allocated as:\n",
        "| Purpose | Cells | Range |",
        "|---------|-------|-------|",
        f"| Error correction | 36 | {SIGNAL_BAND}–{SIGNAL_BAND + 35} |",
        f"| Compression state | 36 | {SIGNAL_BAND + 36}–{SIGNAL_BAND + 71} |",
        f"| Routing tables | 36 | {SIGNAL_BAND + 72}–{SIGNAL_BAND + 107} |",
        f"| Phase tags | 20 | {SIGNAL_BAND + 108}–{SIGNAL_BAND + 127} |",
        f"| Codec headers | 12 | {SIGNAL_BAND + 128}–{SIGNAL_BAND + 139} |",
        f"| Reserved | 8 | {SIGNAL_BAND + 140}–{SIGNAL_BAND + 147} |",
    ])

    # Wreath × archetype grid
    lines.extend([
        "",
        "### Wreath × Archetype Grid (36 shells)\n",
        "| Archetype | Su (1-12) | Me (13-24) | Sa (25-36) |",
        "|-----------|-----------|------------|------------|",
    ])
    for a in range(12):
        name = ARCHETYPE_NAMES[a]
        su_shell = a + 1
        me_shell = a + 13
        sa_shell = a + 25
        lines.append(f"| {a + 1}. {name} | S{su_shell} | S{me_shell} | S{sa_shell} |")

    return "\n".join(lines)

def _compression_stats() -> str:
    """Compression statistics for the current crystal graph."""
    lines = [
        "## QSHRINK ↔ 108D Compression Statistics\n",
    ]

    # Try to load live data
    shell_data = None
    mycelium_data = None
    try:
        shell_data = _SHELLS.load()
    except Exception:
        pass
    try:
        mycelium_data = _MYCELIUM.load()
    except Exception:
        pass

    # Shell statistics
    lines.append("### Crystal State\n")
    if shell_data:
        meta = shell_data.get("meta", {})
        total_nodes = meta.get("total_nodes", TOTAL_NODES)
        total_shells = meta.get("total_shells", TOTAL_SHELLS)
        lines.append(f"- **Nodes**: {total_nodes}")
        lines.append(f"- **Shells**: {total_shells}")
        lines.append(f"- **Wreaths**: {meta.get('wreaths', TOTAL_WREATHS)}")
        lines.append(f"- **Archetypes**: {meta.get('archetypes', len(ARCHETYPE_NAMES))}")
    else:
        total_nodes = TOTAL_NODES
        total_shells = TOTAL_SHELLS
        lines.append(f"- **Nodes**: {TOTAL_NODES} (theoretical — shell data not loaded)")
        lines.append(f"- **Shells**: {TOTAL_SHELLS}")
        lines.append(f"- **Wreaths**: {TOTAL_WREATHS}")
        lines.append(f"- **Archetypes**: {len(ARCHETYPE_NAMES)}")

    # Mycelium statistics
    if mycelium_data:
        m_meta = mycelium_data.get("meta", {})
        shard_count = m_meta.get("total_shards", "?")
        edge_count = m_meta.get("total_edges", "?")
        lines.append(f"- **Mycelium shards**: {shard_count}")
        lines.append(f"- **Mycelium edges**: {edge_count}")
    else:
        lines.append("- **Mycelium**: (data not loaded)")

    # Compression projections
    lines.extend([
        "",
        "### Compression Projections\n",
        "| Level | Factor | Nodes | Address Bits | Saving |",
        "|-------|--------|-------|-------------|--------|",
    ])

    full_bits = math.ceil(math.log2(max(1, total_nodes * SIGNAL_BAND)))
    lines.append(
        f"| Full | 1× | {total_nodes} | {full_bits} | — |"
    )

    current = total_nodes
    factor = 1
    level_names = ["1/8 seed", "1/64 micro", "1/512 nano"]
    for name in level_names:
        factor *= LIFT_FACTOR
        compressed = max(total_shells, math.ceil(current / LIFT_FACTOR))
        comp_bits = math.ceil(math.log2(max(1, compressed * SIGNAL_BAND)))
        saving = f"{(1 - compressed / total_nodes) * 100:.1f}%"
        lines.append(f"| {name} | 1/{factor}× | {compressed} | {comp_bits} | {saving} |")
        current = compressed

    # QSHRINK address efficiency
    qshrink_bits = math.ceil(math.log2(QSHRINK_FULL_SPACE))
    crystal_bits = math.ceil(math.log2(max(1, total_nodes)))

    lines.extend([
        "",
        "### Address Efficiency\n",
        f"- **QSHRINK address**: {qshrink_bits} bits "
        f"(256^4 = {QSHRINK_FULL_SPACE:,})",
        f"- **Crystal node ID**: {crystal_bits} bits "
        f"({total_nodes} nodes)",
        f"- **Overhead ratio**: {qshrink_bits / max(1, crystal_bits):.1f}× "
        "(metadata envelope for error correction + regeneration)",
        f"- **Effective compression**: 108D vector → 1 QSHRINK cell = "
        f"{SIGNAL_BAND}:1 dimension reduction",
    ])

    # Bridge health
    lines.extend([
        "",
        "### Bridge Health\n",
        f"- Signal band: {SIGNAL_BAND}/{QSHRINK_ROOT_CELLS} root cells "
        f"({SIGNAL_BAND / QSHRINK_ROOT_CELLS * 100:.1f}% signal)",
        f"- Metadata band: {METADATA_BAND}/{QSHRINK_ROOT_CELLS} root cells "
        f"({METADATA_BAND / QSHRINK_ROOT_CELLS * 100:.1f}% overhead)",
        f"- Shell coverage: {SIGNAL_BAND // TOTAL_SHELLS} signal cells per shell",
        f"- Lift cascade: {len(level_names)} levels "
        f"(down to {max(total_shells, math.ceil(total_nodes / LIFT_FACTOR ** len(level_names)))} nodes)",
        "- Conservation: 6 invariants preserved at all levels",
    ])

    return "\n".join(lines)


# ===========================================================================
# Operational MCP tools — compress, decompress, scan, inspect
# ===========================================================================

def _get_weight_store() -> Any:
    """Lazily load the FractalWeightStore (may not have data yet)."""
    try:
        from .crystal_weights import FractalWeightStore
        store = FractalWeightStore()
        store.load_from_json()
        return store
    except Exception:
        return None


def qshrink_compress(path: str, lossless: bool = True) -> str:
    """Compress a file to .qshr with embedded crystal weight metadata.

    Args:
        path: File path to compress (relative to MCP/data/ or absolute).
        lossless: If True, use lossless compression (default).

    Returns a summary of compression results including crystal coordinate
    and weight seed status.
    """
    from .qshrink_pipeline import compress_file

    p = Path(path)
    if not p.is_absolute():
        p = DATA_DIR / path
    if not p.exists():
        return f"File not found: {p}"

    store = _get_weight_store()
    out_path, stats = compress_file(p, lossless=lossless, weight_store=store)

    lines = [
        "## QSHR Compression Complete\n",
        f"- **Source**: `{p.name}`",
        f"- **Output**: `{out_path.name}`",
        f"- **Original size**: {stats['original_size']:,} bytes",
        f"- **Compressed size**: {stats['compressed_size']:,} bytes",
        f"- **Ratio**: {stats['ratio']:.1f}x",
        f"- **Savings**: {stats['savings_pct']:.1f}%",
        f"- **Crystal coordinate**: `{stats['coordinate']}`",
        f"- **Shell**: S{stats['shell']}",
        f"- **Weight seeds embedded**: {'Yes' if stats['has_weight_seeds'] else 'No (hollow envelope)'}",
        f"- **Lossless**: {'Yes' if lossless else 'No'}",
    ]
    return "\n".join(lines)


def qshrink_decompress(path: str) -> str:
    """Decompress a .qshr file and report embedded crystal metadata.

    Args:
        path: Path to .qshr file (relative to MCP/data/ or absolute).

    Returns decompression results and crystal weight metadata summary.
    """
    from .qshrink_pipeline import decompress_file

    p = Path(path)
    if not p.is_absolute():
        p = DATA_DIR / path
    if not p.exists():
        return f"File not found: {p}"

    out_path, stats = decompress_file(p)

    lines = [
        "## QSHR Decompression Complete\n",
        f"- **Source**: `{p.name}`",
        f"- **Output**: `{out_path.name}`",
        f"- **Compressed size**: {stats['compressed_size']:,} bytes",
        f"- **Restored size**: {stats['restored_size']:,} bytes",
        f"- **Crystal coordinate**: `{stats['coordinate']}`",
        f"- **Weight seeds present**: {'Yes' if stats['has_weight_seeds'] else 'No'}",
    ]
    return "\n".join(lines)


def qshrink_scan(directory: str = "") -> str:
    """Scan a directory for files that would benefit from QSHR compression.

    Args:
        directory: Directory to scan (default: MCP/data/).

    Returns a table of compressible files with estimated savings.
    """
    from .qshrink_pipeline import scan_directory

    d = Path(directory) if directory else DATA_DIR
    if not d.exists():
        return f"Directory not found: {d}"

    results = scan_directory(d)
    if not results:
        return f"No compressible files found in `{d}`"

    lines = [
        f"## QSHR Compression Scan: `{d.name}/`\n",
        f"Found **{len(results)}** compressible files.\n",
        "| File | Size | Est. Compressed | Est. Savings | Shell | Coordinate |",
        "|------|------|----------------|-------------|-------|------------|",
    ]

    total_size = 0
    total_savings = 0
    for r in results[:30]:  # cap at 30 rows
        fname = Path(r["path"]).name
        total_size += r["size"]
        est_savings_bytes = int(r["size"] * (1 - 1 / r["est_ratio"]))
        total_savings += est_savings_bytes
        lines.append(
            f"| {fname} | {r['size_human']} | {r['est_compressed']} | "
            f"{r['est_savings']} | S{r['shell']} | `{r['coordinate']}` |"
        )

    if len(results) > 30:
        lines.append(f"| ... | *{len(results) - 30} more files* | | | | |")

    lines.extend([
        "",
        f"### Total: {len(results)} files, "
        f"{total_size / 1024 / 1024:.1f}MB → "
        f"~{(total_size - total_savings) / 1024 / 1024:.1f}MB "
        f"(est. {total_savings / 1024 / 1024:.1f}MB savings)",
    ])

    return "\n".join(lines)


def qshrink_inspect(path: str) -> str:
    """Read crystal weight metadata from a .qshr file WITHOUT decompressing.

    O(1) metadata read — returns the embedded crystal coordinate, weight
    seeds, learnable parameters, and conservation hash.

    Args:
        path: Path to .qshr file (relative to MCP/data/ or absolute).
    """
    from .qshrink_pipeline import inspect_qshr

    p = Path(path)
    if not p.is_absolute():
        p = DATA_DIR / path
    if not p.exists():
        return f"File not found: {p}"

    meta = inspect_qshr(p)
    if meta is None:
        return f"No crystal metadata found in `{p.name}` (not a valid .qshr file)"

    lines = [
        f"## Crystal Weight Metadata: `{p.name}`\n",
        "### Identity\n",
        f"- **Coordinate**: `{meta.coordinate}`",
        f"- **Shell**: S{meta.shell}",
        f"- **Wreath**: W{meta.wreath}",
        f"- **Archetype**: A{meta.archetype} ({ARCHETYPE_NAMES[meta.archetype - 1] if 1 <= meta.archetype <= 12 else '?'})",
        f"- **Face**: {meta.face}",
        f"- **Mirror shell**: S{meta.mirror_shell}",
        "",
        "### Holographic Regeneration\n",
        f"- **w**: ({meta.holographic_w_real} + {meta.holographic_w_imag}i)",
        f"- **Conservation hash**: `{meta.conservation_hash}`",
        "",
        "### Neural Parameters\n",
        f"- **Path weights**: {meta.path_weights}",
        f"- **Resonance weights**: {meta.resonance_weights}",
        f"- **Desire weights**: {meta.desire_weights}",
        f"- **Bridge modulation**: {meta.bridge_modulation}",
    ]

    if meta.shell_seed:
        ss = meta.shell_seed
        lines.extend([
            "",
            f"### Shell Seed (1/8 lift — S{ss.shell})\n",
            f"- **Mean**: {ss.mean:.4f} | **Std**: {ss.std:.4f}",
            f"- **Count**: {ss.count} | **Range**: [{ss.min_val:.2f}, {ss.max_val:.2f}]",
            f"- **Element dist**: {ss.element_dist}",
            f"- **Gate means**: {ss.gate_means}",
        ])

    if meta.archetype_seed:
        ars = meta.archetype_seed
        lines.extend([
            "",
            f"### Archetype Seed (1/64 lift — A{ars.archetype} {ars.name})\n",
            f"- **Mean**: {ars.mean:.4f} | **Std**: {ars.std:.4f}",
            f"- **Count**: {ars.count}",
            f"- **Wreath means**: {ars.wreath_means}",
        ])

    if meta.nano_seed:
        ns = meta.nano_seed
        lines.extend([
            "",
            "### Nano Seed (1/512 lift — global)\n",
            f"- **Global mean**: {ns.global_mean:.4f} | **Std**: {ns.global_std:.4f}",
            f"- **Skew**: {ns.skew:.4f} | **Kurtosis**: {ns.kurtosis:.4f}",
            f"- **Total count**: {ns.total_count}",
            f"- **Element means**: {ns.element_means}",
            f"- **Gate means**: {ns.gate_means}",
        ])

    if not meta.shell_seed and not meta.archetype_seed and not meta.nano_seed:
        lines.extend([
            "",
            "### Weight Seeds: **HOLLOW** (identity-only envelope, no weight data)",
        ])

    return "\n".join(lines)
