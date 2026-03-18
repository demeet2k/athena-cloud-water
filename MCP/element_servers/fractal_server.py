"""
ATHENA FRACTAL SERVER — Air Element (R)
=======================================
Seed / Replay / Compression Body

The Fractal lens provides the minimal seed with collapse/expand discipline.
Expand(σ) → Sq(Ω), Collapse(Sq) → σ.  Closure: Expand ∘ Collapse ~ id.
This is the TRANSPORTABLE COMPRESSION body — seeds that replicate the whole.

Tools: query_stage_code, query_angel, read_hologram_chapter, query_containment,
       dimensional_lift, resolve_dimensional_body, query_organ, query_mobius_lens,
       query_sfcr_station, athena_status, list_families, query_brain_network, route_brain

SFCR Mask: 8 (1000)
Dimension Home: 10D
Superphase Affinity: Salt
Transport: Z, A, L, Tunnel, Metro, Mycelium, Bus, Plane, ETV
"""

import os
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Fractal (Air)")

# ── Register Fractal-specific tools ───────────────────────────────
from crystal_108d.stage_codes import query_stage_code
from crystal_108d.angel import query_angel
from crystal_108d.shells import read_hologram_chapter
from crystal_108d.dimensions import resolve_dimensional_body, dimensional_lift, query_containment
from crystal_108d.organs import query_organ
from crystal_108d.mobius_lenses import query_mobius_lens, query_sfcr_station
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight, brain_status
from crystal_108d.emergence import query_emergence
from crystal_108d.inverse_seed import query_3d_crystal
from crystal_108d.inverse_complete import query_projection_stack
from crystal_108d.hologram_reading import query_hologram
from crystal_108d.guild_hall import guild_hall_status as _guild_hall_status

mcp.tool()(query_stage_code)
mcp.tool()(query_angel)
mcp.tool()(read_hologram_chapter)
mcp.tool()(resolve_dimensional_body)
mcp.tool()(dimensional_lift)
mcp.tool()(query_containment)
mcp.tool()(query_organ)
mcp.tool()(query_mobius_lens)
mcp.tool()(query_sfcr_station)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_emergence)
mcp.tool()(query_3d_crystal)
mcp.tool()(query_projection_stack)
mcp.tool()(query_hologram)


@mcp.tool()
def fractal_guild_status() -> str:
    """Compressed Guild Hall status from the fractal/seed perspective."""
    return _guild_hall_status()


# ── Core fractal/compression tools ────────────────────────────────
ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER_CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
BOARD_DIR = NS_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def athena_status() -> str:
    """Full system status including 108D summary and brain network."""
    from crystal_108d import status_summary
    return status_summary() + "\n" + brain_status()


@mcp.tool()
def list_families() -> str:
    """List active project families."""
    families_dir = BOARD_DIR / "03_FAMILIES"
    if not families_dir.exists():
        return "Families directory not found."
    families = sorted(families_dir.glob("*.md"))
    if not families:
        return "No active families."
    return "## Active Families\n\n" + "\n".join(f"- {f.stem}" for f in families)


# ── Mycelium: Recursion & Compression ─────────────────────────────

@mcp.tool()
def lift_shard(shard_id: str = "", target_dimension: str = "6D") -> str:
    """Project a shard into a higher dimensional scope."""
    import json
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    if not shard_id:
        return "Provide a shard_id to lift."
    matches = [s for s in data["shards"] if shard_id.lower() in s["shard_id"].lower()]
    if not matches:
        return f"Shard '{shard_id}' not found."
    s = matches[0]
    current_dim = s.get("dimensional_scope", "4D")
    projections = [e for e in data["edges"] if e["source_shard"] == s["shard_id"] and e["edge_type"] == "PROJECTS"]
    derives = [e for e in data["edges"] if e["source_shard"] == s["shard_id"] and e["edge_type"] == "DERIVES"]
    lines = [
        f"## Dimensional Lift: {s['shard_id']}\n",
        f"**Current Scope**: {current_dim} → **Target**: {target_dimension}",
        f"**Medium**: {s['medium']} | **Family**: {s['family']}",
        f"**Seed Vector**: [{', '.join(f'{v:.2f}' for v in s['seed_vector'])}]",
        f"\n### Lift Projection\n",
        f"The shard at {current_dim} can be lifted to {target_dimension} by:",
        f"1. Preserving seed_vector invariants across the lift",
        f"2. Extending edge neighborhood into the target dimension",
        f"3. Applying the kernel embedding law: dim(kernel) <= dim(target)",
    ]
    if projections:
        lines.append(f"\n### Existing Projections ({len(projections)})\n")
        for e in projections:
            lines.append(f"- → `{e['target_shard']}` (w={e['weight']})")
    if derives:
        lines.append(f"\n### Derived Shards ({len(derives)})\n")
        for e in derives:
            lines.append(f"- → `{e['target_shard']}` (w={e['weight']})")
    return "\n".join(lines)


@mcp.tool()
def compress_recursive_family(family: str = "") -> str:
    """Compress a family's shard graph into a seed summary."""
    import json
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    if not family:
        stats = data["graph_stats"]
        lines = ["## Family Compression Index\n"]
        for fam, count in sorted(stats["family_sizes"].items(), key=lambda x: -x[1]):
            fam_shards = [s for s in data["shards"] if s["family"] == fam]
            fam_edges = [e for e in data["edges"]
                         if any(s["shard_id"] in (e["source_shard"], e["target_shard"]) for s in fam_shards)]
            density = len(fam_edges) / max(count * (count - 1), 1)
            lines.append(f"- **{fam}**: {count} shards, {len(fam_edges)} edges, density={density:.3f}")
        return "\n".join(lines)
    fam_shards = [s for s in data["shards"] if s["family"].lower() == family.lower()]
    if not fam_shards:
        return f"Family '{family}' not found."
    fam_ids = {s["shard_id"] for s in fam_shards}
    internal_edges = [e for e in data["edges"]
                      if e["source_shard"] in fam_ids and e["target_shard"] in fam_ids]
    external_edges = [e for e in data["edges"]
                      if (e["source_shard"] in fam_ids) != (e["target_shard"] in fam_ids)]
    mediums = set(s["medium"] for s in fam_shards)
    avg_sv = [0.0, 0.0, 0.0, 0.0]
    for s in fam_shards:
        for i, v in enumerate(s.get("seed_vector", [0, 0, 0, 0])):
            avg_sv[i] += v
    avg_sv = [v / len(fam_shards) for v in avg_sv]
    lines = [
        f"## Seed Summary: {family}\n",
        f"**Shards**: {len(fam_shards)} | **Mediums**: {', '.join(mediums)}",
        f"**Internal Edges**: {len(internal_edges)} | **External Edges**: {len(external_edges)}",
        f"**Average Seed Vector**: [{', '.join(f'{v:.3f}' for v in avg_sv)}]",
        f"\n### Compressed Representation\n",
        f"```",
        f"family: {family}",
        f"cardinality: {len(fam_shards)}",
        f"mediums: {sorted(mediums)}",
        f"seed: [{', '.join(f'{v:.3f}' for v in avg_sv)}]",
        f"internal_density: {len(internal_edges) / max(len(fam_shards) * (len(fam_shards)-1), 1):.4f}",
        f"boundary_edges: {len(external_edges)}",
        f"```",
    ]
    return "\n".join(lines)


# ── Fractal-specific resource ─────────────────────────────────────
@mcp.resource("athena://fractal-air")
def resource_fractal() -> str:
    """Fractal element status — Seed / Replay / Compression."""
    return (
        "## Fractal Lobe (Air) — Active\n\n"
        "**SFCR Mask**: 8 (1000)\n"
        "**Dimension Home**: 10D\n"
        "**Role**: Seed / Replay / Compression Body\n"
        "**Transport**: Z, A, L, Tunnel, Metro, Mycelium, Bus, Plane, ETV\n"
        "**Tools**: 14 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
