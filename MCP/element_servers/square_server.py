"""
ATHENA SQUARE SERVER — Earth Element (S)
========================================
Structure / Address / Admissibility Body

The Square lens fixes WHERE the object is, WHAT state it carries, and WHAT law
generated it.  This is the discrete admissibility ledger — the visible board grid.

Tools: navigate_crystal, navigate_108d, query_shell, query_superphase,
       query_archetype, read_chapter, read_appendix, query_overlay,
       query_sigma15, read_manifest, query_brain_network, route_brain

SFCR Mask: 1 (0001)
Dimension Home: 4D
Superphase Affinity: Salt
Transport: Z, A
"""

import os
import sys
from pathlib import Path

# Ensure MCP/ is on the path
_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Square (Earth)")

# ── Register Square-specific tools ────────────────────────────────
from crystal_108d.shells import query_shell, query_superphase, query_archetype
from crystal_108d.address import navigate_108d
from crystal_108d.overlays import query_overlay, query_sigma15
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight
from crystal_108d.hologram_reading import query_hologram
from crystal_108d.inverse_seed import query_4d_seed
from crystal_108d.angel_geometry import query_angel_conservation
from crystal_108d.guild_hall import query_promotion_membrane

mcp.tool()(query_shell)
mcp.tool()(query_superphase)
mcp.tool()(query_archetype)
mcp.tool()(navigate_108d)
mcp.tool()(query_overlay)
mcp.tool()(query_sigma15)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_hologram)
mcp.tool()(query_4d_seed)
mcp.tool()(query_angel_conservation)
mcp.tool()(query_promotion_membrane)

# ── Import core tools from main server (read-only navigation) ─────
from crystal_108d import status_summary

ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER_CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
CHAPTERS_DIR = NS_ROOT / "04_CHAPTERS"
APPENDICES_DIR = NS_ROOT / "05_APPENDICES"
RUNTIME_DIR = NS_ROOT / "06_RUNTIME"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def navigate_crystal(address: str) -> str:
    """Navigate the 4D crystal by address (e.g., Ch01<0000>.S1.a)."""
    import re
    m = re.match(r"(Ch\d{2}|App[A-P])<(\d{4})>\.([SFCR])(\d)\.([a-d])", address)
    if not m:
        return f"Invalid crystal address: {address}"
    tile, digits, face, level, atom = m.groups()
    if tile.startswith("Ch"):
        base = CHAPTERS_DIR
    else:
        base = APPENDICES_DIR
    matches = list(base.glob(f"*{tile}*"))
    if not matches:
        return f"Tile {tile} not found."
    return _read_file(matches[0])


@mcp.tool()
def read_chapter(code: str = "Ch01") -> str:
    """Read a chapter tile (Ch01–Ch21)."""
    matches = list(CHAPTERS_DIR.glob(f"*{code}*"))
    if not matches:
        return f"Chapter {code} not found."
    return _read_file(matches[0])


@mcp.tool()
def read_appendix(code: str = "AppA") -> str:
    """Read an appendix hub (AppA–AppP)."""
    matches = list(APPENDICES_DIR.glob(f"*{code}*"))
    if not matches:
        return f"Appendix {code} not found."
    return _read_file(matches[0])


@mcp.tool()
def read_manifest(name: str = "") -> str:
    """Read runtime manifests."""
    if not RUNTIME_DIR.exists():
        return "Runtime directory not found."
    manifests = sorted(RUNTIME_DIR.glob("*.md"))
    if not name:
        return "Available manifests:\n" + "\n".join(f"- {m.stem}" for m in manifests)
    matches = [m for m in manifests if name.lower() in m.stem.lower()]
    if not matches:
        return f"Manifest '{name}' not found."
    return _read_file(matches[0])


# ── Mycelium: Structure & Verification ────────────────────────────

@mcp.tool()
def normalize_shard(shard_id: str = "") -> str:
    """Verify structural invariants of a shard (ID format, required fields, seed_vector, payload_ref)."""
    import json
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    if not shard_id:
        total = len(data["shards"])
        errors = []
        for s in data["shards"]:
            if not s.get("shard_id"):
                errors.append("Missing shard_id")
            if not s.get("payload_ref"):
                errors.append(f"{s.get('shard_id', '?')}: missing payload_ref")
            if len(s.get("seed_vector", [])) != 4:
                errors.append(f"{s.get('shard_id', '?')}: seed_vector != 4 elements")
        if errors:
            return f"## Structural Check ({total} shards)\n\n**{len(errors)} issues**:\n" + "\n".join(f"- {e}" for e in errors)
        return f"## Structural Check\n\nAll {total} shards pass structural invariants."
    matches = [s for s in data["shards"] if shard_id.lower() in s["shard_id"].lower()]
    if not matches:
        return f"Shard '{shard_id}' not found."
    lines = []
    for s in matches:
        checks = []
        checks.append(f"shard_id: {'OK' if s.get('shard_id') else 'MISSING'}")
        checks.append(f"medium: {'OK' if s.get('medium') else 'MISSING'}")
        checks.append(f"payload_ref: {'OK' if s.get('payload_ref') else 'MISSING'}")
        checks.append(f"seed_vector: {'OK (len=4)' if len(s.get('seed_vector', [])) == 4 else 'BAD'}")
        checks.append(f"family: {'OK' if s.get('family') else 'MISSING'}")
        checks.append(f"truth_status: {s.get('truth_status', 'MISSING')}")
        checks.append(f"promotion_status: {s.get('promotion_status', 'MISSING')}")
        lines.append(f"### {s['shard_id']}\n" + "\n".join(f"- {c}" for c in checks))
    return "\n\n".join(lines)


@mcp.tool()
def verify_invariants(shard_id: str = "") -> str:
    """Verify conservation checks on a shard's edge neighborhood."""
    import json
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    if not shard_id:
        # Global invariant check
        shard_ids = {s["shard_id"] for s in data["shards"]}
        orphan_edges = []
        for e in data["edges"]:
            if e["source_shard"] not in shard_ids:
                orphan_edges.append(f"Edge {e['edge_id']}: source {e['source_shard']} not in graph")
            if e["target_shard"] not in shard_ids:
                orphan_edges.append(f"Edge {e['edge_id']}: target {e['target_shard']} not in graph")
        if orphan_edges:
            return f"## Invariant Check\n\n**{len(orphan_edges)} orphan edges**:\n" + "\n".join(f"- {o}" for o in orphan_edges[:20])
        return f"## Invariant Check\n\nAll {len(data['edges'])} edges reference valid shards. No orphans."
    matches = [s for s in data["shards"] if shard_id.lower() in s["shard_id"].lower()]
    if not matches:
        return f"Shard '{shard_id}' not found."
    lines = []
    for s in matches:
        sid = s["shard_id"]
        in_edges = [e for e in data["edges"] if e["target_shard"] == sid]
        out_edges = [e for e in data["edges"] if e["source_shard"] == sid]
        in_types = {}
        for e in in_edges:
            in_types[e["edge_type"]] = in_types.get(e["edge_type"], 0) + 1
        out_types = {}
        for e in out_edges:
            out_types[e["edge_type"]] = out_types.get(e["edge_type"], 0) + 1
        lines.append(
            f"### {sid}\n"
            f"- Incoming: {len(in_edges)} ({', '.join(f'{k}:{v}' for k, v in in_types.items()) or 'none'})\n"
            f"- Outgoing: {len(out_edges)} ({', '.join(f'{k}:{v}' for k, v in out_types.items()) or 'none'})\n"
            f"- Degree: {len(in_edges) + len(out_edges)}\n"
            f"- Weight sum (in): {sum(e['weight'] for e in in_edges):.3f}\n"
            f"- Weight sum (out): {sum(e['weight'] for e in out_edges):.3f}"
        )
    return "\n\n".join(lines)


# ── Square-specific resource ──────────────────────────────────────
@mcp.resource("athena://square-earth")
def resource_square() -> str:
    """Square element status — Structure / Address / Admissibility."""
    from crystal_108d.brain import brain_status
    return (
        "## Square Lobe (Earth) — Active\n\n"
        "**SFCR Mask**: 1 (0001)\n"
        "**Dimension Home**: 4D\n"
        "**Role**: Structure / Address / Admissibility Body\n"
        "**Transport**: Z, A\n"
        "**Tools**: 12 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
