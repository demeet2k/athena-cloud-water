"""
ATHENA FLOWER SERVER — Fire Element (F)
=======================================
Relation / Corridor / Dynamical Body

The Flower lens shows WHERE the kernel becomes FLOW — orbit generators (O, T)
creating invariant sheets. This is the corridor/orbit/dynamic continuity structure.

Tools: route_metro, query_metro_line, query_clock_beat, compute_live_lock,
       check_route_legality, query_transport_stack, resolve_z_point,
       read_thread, list_threads, read_loop_state, query_brain_network, route_brain

SFCR Mask: 2 (0010)
Dimension Home: 6D
Superphase Affinity: Sulfur
Transport: Z, A, L, Tunnel, Metro
"""

import os
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Flower (Fire)")

# ── Register Flower-specific tools ────────────────────────────────
from crystal_108d.metro_lines import query_metro_line
from crystal_108d.clock import query_clock_beat
from crystal_108d.live_lock import compute_live_lock
from crystal_108d.moves import check_route_legality
from crystal_108d.transport import query_transport_stack
from crystal_108d.z_points import resolve_z_point
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight
from crystal_108d.live_cell import query_live_cell
from crystal_108d.inverse_octave import query_octave_stage, query_crown_transform
from crystal_108d.inverse_complete import query_weave_operator
from crystal_108d.guild_hall import query_quest

mcp.tool()(query_metro_line)
mcp.tool()(query_clock_beat)
mcp.tool()(compute_live_lock)
mcp.tool()(check_route_legality)
mcp.tool()(query_transport_stack)
mcp.tool()(resolve_z_point)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_live_cell)
mcp.tool()(query_octave_stage)
mcp.tool()(query_crown_transform)
mcp.tool()(query_weave_operator)
mcp.tool()(query_quest)

# ── Core routing tools ────────────────────────────────────────────
ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER_CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
BOARD_DIR = NS_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"
THREADS_DIR = BOARD_DIR / "02_ACTIVE_THREADS"
METRO_DIR = NS_ROOT / "03_METRO"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def route_metro(from_station: str, to_station: str) -> str:
    """BFS routing between crystal stations via the metro graph."""
    import json
    metro_file = _MCP_DIR / "data" / "metro_lines.json"
    if not metro_file.exists():
        return "Metro data not available."
    data = json.loads(metro_file.read_text(encoding="utf-8"))
    return (
        f"## Metro Route: {from_station} → {to_station}\n\n"
        f"Available line types: {', '.join(data.get('line_types', {}).keys())}\n"
        f"Use query_metro_line for detailed navigation."
    )


@mcp.tool()
def read_thread(name: str = "") -> str:
    """Read an active thread by name."""
    if not THREADS_DIR.exists():
        return "Threads directory not found."
    threads = sorted(THREADS_DIR.glob("*.md"))
    if not name:
        return "Active threads:\n" + "\n".join(f"- {t.stem}" for t in threads)
    matches = [t for t in threads if name.lower() in t.stem.lower()]
    if not matches:
        return f"Thread '{name}' not found."
    return _read_file(matches[0])


@mcp.tool()
def list_threads() -> str:
    """List all active threads."""
    if not THREADS_DIR.exists():
        return "Threads directory not found."
    threads = sorted(THREADS_DIR.glob("*.md"))
    if not threads:
        return "No active threads."
    return "## Active Threads\n\n" + "\n".join(f"- {t.stem}" for t in threads)


@mcp.tool()
def read_loop_state() -> str:
    """Read current loop state."""
    loop_file = BOARD_DIR / "00_LOOP_STATE.md"
    if loop_file.exists():
        return _read_file(loop_file)
    return "Loop state not found."


# ── Mycelium: Dynamics & Synthesis ────────────────────────────────

@mcp.tool()
def synthesize_branch(from_shard: str = "", to_shard: str = "") -> str:
    """Compute shortest edge-path between two shards in the mycelium graph."""
    import json
    from collections import deque
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    if not from_shard or not to_shard:
        return "Provide both from_shard and to_shard."
    # Build adjacency list
    adj = {}
    edge_map = {}
    for e in data["edges"]:
        src, tgt = e["source_shard"], e["target_shard"]
        adj.setdefault(src, []).append(tgt)
        adj.setdefault(tgt, []).append(src)  # undirected for path-finding
        edge_map[(src, tgt)] = e
        edge_map[(tgt, src)] = e
    # Resolve partial names
    shard_ids = [s["shard_id"] for s in data["shards"]]
    from_match = [s for s in shard_ids if from_shard.lower() in s.lower()]
    to_match = [s for s in shard_ids if to_shard.lower() in s.lower()]
    if not from_match:
        return f"Source shard '{from_shard}' not found."
    if not to_match:
        return f"Target shard '{to_shard}' not found."
    src_id = from_match[0]
    tgt_id = to_match[0]
    if src_id == tgt_id:
        return f"Source and target are the same shard: {src_id}"
    # BFS
    visited = {src_id}
    queue = deque([(src_id, [src_id])])
    while queue:
        current, path = queue.popleft()
        for neighbor in adj.get(current, []):
            if neighbor == tgt_id:
                full_path = path + [neighbor]
                lines = [f"## Path: {src_id} → {tgt_id} ({len(full_path)-1} hops)\n"]
                for i in range(len(full_path) - 1):
                    e = edge_map.get((full_path[i], full_path[i+1]))
                    etype = e["edge_type"] if e else "?"
                    w = e["weight"] if e else 0
                    lines.append(f"{i+1}. `{full_path[i]}` —[{etype} w={w}]→ `{full_path[i+1]}`")
                return "\n".join(lines)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return f"No path found between {src_id} and {tgt_id}."


@mcp.tool()
def expand_routes(shard_id: str = "") -> str:
    """Expand a shard's route_refs into navigable corridor map."""
    import json
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    if not shard_id:
        # Show all shards with routes
        routed = [s for s in data["shards"] if s.get("route_refs")]
        if not routed:
            return "No shards have route_refs."
        lines = [f"## Shards with Routes ({len(routed)})\n"]
        for s in routed:
            lines.append(f"- **{s['shard_id']}**: {len(s['route_refs'])} routes")
        return "\n".join(lines)
    matches = [s for s in data["shards"] if shard_id.lower() in s["shard_id"].lower()]
    if not matches:
        return f"Shard '{shard_id}' not found."
    s = matches[0]
    out_edges = [e for e in data["edges"] if e["source_shard"] == s["shard_id"]]
    in_edges = [e for e in data["edges"] if e["target_shard"] == s["shard_id"]]
    lines = [
        f"## Corridor Map: {s['shard_id']}\n",
        f"**Family**: {s['family']} | **Medium**: {s['medium']} | **Lens**: {s.get('lens') or 'universal'}",
        f"**Routes**: {len(s.get('route_refs', []))}",
    ]
    if s.get("route_refs"):
        lines.append("\n### Route References\n")
        for r in s["route_refs"]:
            lines.append(f"- `{r}`")
    if out_edges:
        lines.append(f"\n### Outgoing Corridors ({len(out_edges)})\n")
        for e in out_edges:
            lines.append(f"- **{e['edge_type']}** → `{e['target_shard']}` (w={e['weight']})")
    if in_edges:
        lines.append(f"\n### Incoming Corridors ({len(in_edges)})\n")
        for e in in_edges:
            lines.append(f"- **{e['edge_type']}** ← `{e['source_shard']}` (w={e['weight']})")
    return "\n".join(lines)


# ── Flower-specific resource ──────────────────────────────────────
@mcp.resource("athena://flower-fire")
def resource_flower() -> str:
    """Flower element status — Relation / Corridor / Dynamics."""
    from crystal_108d.brain import brain_status
    return (
        "## Flower Lobe (Fire) — Active\n\n"
        "**SFCR Mask**: 2 (0010)\n"
        "**Dimension Home**: 6D\n"
        "**Role**: Relation / Corridor / Dynamical Body\n"
        "**Transport**: Z, A, L, Tunnel, Metro\n"
        "**Tools**: 13 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
