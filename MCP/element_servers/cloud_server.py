"""
ATHENA CLOUD SERVER — Water Element (C)
=======================================
Lawful Multiplicity / Fiber Object

The Cloud lens reveals structured LAWFUL multiplicity — NOT randomness.
Every admissible point has exactly 2 pre-images (Cloud Fiber Theorem).
This is the observation, search, and conservation enforcement body.

Tools: search_everywhere, search_corpus, query_neural_net, query_conservation,
       list_corpus_capsules, read_corpus_capsule, read_board_status,
       read_swarm_element, read_frontier, read_tensor, query_brain_network, route_brain

SFCR Mask: 4 (0100)
Dimension Home: 8D
Superphase Affinity: Mercury
Transport: Z, A, L, Tunnel, Metro, Mycelium, Bus
"""

import os
import sys
import json
import glob as globmod
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_MCP_DIR))

os.environ.setdefault("ATHENA_ROOT", str(_MCP_DIR.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Athena Cloud (Water)")

# ── Register Cloud-specific tools ─────────────────────────────────
from crystal_108d.conservation import query_conservation
from crystal_108d.brain import query_brain_network, route_brain, compute_bridge_weight
from crystal_108d.hologram_reading import query_hologram_rosetta
from crystal_108d.angel_geometry import query_angel_geometry
from crystal_108d.guild_hall import query_synthesis

mcp.tool()(query_conservation)
mcp.tool()(query_brain_network)
mcp.tool()(route_brain)
mcp.tool()(compute_bridge_weight)
mcp.tool()(query_hologram_rosetta)
mcp.tool()(query_angel_geometry)
mcp.tool()(query_synthesis)

# ── Core observation tools ────────────────────────────────────────
ATHENA_ROOT = Path(os.environ["ATHENA_ROOT"])
NS_ROOT = ATHENA_ROOT / "DEEPER_CRYSTALIZATION" / "ACTIVE_NERVOUS_SYSTEM"
CORPUS_DIR = NS_ROOT / "02_CORPUS_CAPSULES"
BOARD_DIR = NS_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"
NEURAL_NET_DIR = NS_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME"
SWARM_DIR = BOARD_DIR / "08_SWARM_RUNTIME"
FRONTIERS_DIR = NS_ROOT / "10_FRONTIERS"


def _read_file(path: Path, limit: int = 500) -> str:
    if not path.exists():
        return f"Not found: {path.name}"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > limit:
        return "\n".join(lines[:limit]) + f"\n\n[…truncated at {limit} lines]"
    return text


@mcp.tool()
def search_everywhere(query: str, max_results: int = 10) -> str:
    """Full-text search across the entire nervous system."""
    query_lower = query.lower()
    results = []
    search_dirs = [NS_ROOT]
    for sd in search_dirs:
        if not sd.exists():
            continue
        for ext in ("*.md", "*.json", "*.txt"):
            for fp in sd.rglob(ext):
                try:
                    text = fp.read_text(encoding="utf-8", errors="replace")
                    if query_lower in text.lower():
                        idx = text.lower().index(query_lower)
                        snippet = text[max(0, idx - 80):idx + 80].replace("\n", " ")
                        results.append(f"- **{fp.relative_to(ATHENA_ROOT)}**: …{snippet}…")
                        if len(results) >= max_results:
                            break
                except Exception:
                    continue
            if len(results) >= max_results:
                break
    if not results:
        return f"No results for '{query}'."
    return f"## Search: '{query}'\n\n" + "\n".join(results)


@mcp.tool()
def search_corpus(query: str) -> str:
    """Search corpus capsules by keyword."""
    if not CORPUS_DIR.exists():
        return "Corpus directory not found."
    query_lower = query.lower()
    hits = []
    for fp in sorted(CORPUS_DIR.glob("*.md")):
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
            if query_lower in text.lower():
                hits.append(f"- {fp.stem}")
        except Exception:
            continue
    if not hits:
        return f"No corpus capsules match '{query}'."
    return f"## Corpus Search: '{query}'\n\n" + "\n".join(hits)


@mcp.tool()
def query_neural_net(query: str = "", index: str = "", max_results: int = 10) -> str:
    """Search the deeper neural network (197 docs, 38,809 edge pairs)."""
    if not NEURAL_NET_DIR.exists():
        return "Neural net directory not found."
    files = sorted(NEURAL_NET_DIR.rglob("*.md"))
    if not query:
        return f"## Neural Net\n\n{len(files)} documents available."
    query_lower = query.lower()
    hits = []
    for fp in files:
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
            if query_lower in text.lower():
                hits.append(f"- {fp.stem}")
                if len(hits) >= max_results:
                    break
        except Exception:
            continue
    return f"## Neural Net Search: '{query}'\n\n{len(hits)} hits:\n" + "\n".join(hits)


@mcp.tool()
def list_corpus_capsules() -> str:
    """List all corpus capsules."""
    if not CORPUS_DIR.exists():
        return "Corpus directory not found."
    capsules = sorted(CORPUS_DIR.glob("*.md"))
    return f"## Corpus Capsules ({len(capsules)})\n\n" + "\n".join(f"- {c.stem}" for c in capsules)


@mcp.tool()
def read_corpus_capsule(capsule_id: str = "") -> str:
    """Read a corpus capsule by ID or filename."""
    if not CORPUS_DIR.exists():
        return "Corpus directory not found."
    matches = [c for c in CORPUS_DIR.glob("*.md") if capsule_id.lower() in c.stem.lower()]
    if not matches:
        return f"Capsule '{capsule_id}' not found."
    return _read_file(matches[0])


@mcp.tool()
def read_board_status() -> str:
    """Read the realtime board status."""
    if not BOARD_DIR.exists():
        return "Board directory not found."
    status_files = sorted(BOARD_DIR.glob("*.md"))
    lines = ["## Board Status\n"]
    for sf in status_files[:5]:
        lines.append(f"### {sf.stem}")
        lines.append(_read_file(sf, limit=30))
    return "\n\n".join(lines)


@mcp.tool()
def read_swarm_element(element: str = "") -> str:
    """Read swarm runtime elements (elementals, councils, ganglia)."""
    if not SWARM_DIR.exists():
        return "Swarm directory not found."
    if not element:
        items = sorted(SWARM_DIR.rglob("*.md"))
        return "## Swarm Elements\n\n" + "\n".join(f"- {i.stem}" for i in items[:20])
    matches = [f for f in SWARM_DIR.rglob("*.md") if element.lower() in f.stem.lower()]
    if not matches:
        return f"Swarm element '{element}' not found."
    return _read_file(matches[0])


@mcp.tool()
def read_frontier(chapter: str = "") -> str:
    """Read frontier evidence bundles."""
    if not FRONTIERS_DIR.exists():
        return "Frontiers directory not found."
    if not chapter:
        items = sorted(FRONTIERS_DIR.rglob("*.md"))
        return "## Frontiers\n\n" + "\n".join(f"- {i.stem}" for i in items[:20])
    matches = [f for f in FRONTIERS_DIR.rglob("*.md") if chapter.lower() in f.stem.lower()]
    if not matches:
        return f"Frontier '{chapter}' not found."
    return _read_file(matches[0])


@mcp.tool()
def read_tensor(tensor_name: str = "") -> str:
    """Read tensor field data."""
    tensor_dir = BOARD_DIR / "04_TENSOR_BOARD"
    if not tensor_dir.exists():
        return "Tensor directory not found."
    if not tensor_name:
        items = sorted(tensor_dir.glob("*.md"))
        return "## Tensor Fields\n\n" + "\n".join(f"- {i.stem}" for i in items)
    matches = [f for f in tensor_dir.glob("*.md") if tensor_name.lower() in f.stem.lower()]
    if not matches:
        return f"Tensor '{tensor_name}' not found."
    return _read_file(matches[0])


# ── Mycelium: Observation & Scoring ───────────────────────────────

@mcp.tool()
def score_candidates(family: str = "", top_n: int = 5) -> str:
    """Rank shards by promotion readiness (truth_status, cert count, edge density)."""
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    truth_order = {"SEED": 0, "DRAFT": 1, "WITNESSED": 2, "CERTIFIED": 3, "CANONICAL": 4}
    shards = data["shards"]
    if family:
        shards = [s for s in shards if s["family"].lower() == family.lower()]
        if not shards:
            return f"No shards in family '{family}'."
    scored = []
    for s in shards:
        sid = s["shard_id"]
        truth_score = truth_order.get(s["truth_status"], 0)
        certs = sum(1 for e in data["edges"] if e["target_shard"] == sid and e["edge_type"] == "CERTIFIES")
        degree = sum(1 for e in data["edges"] if e["source_shard"] == sid or e["target_shard"] == sid)
        total = truth_score * 10 + certs * 5 + degree
        scored.append((total, s, truth_score, certs, degree))
    scored.sort(key=lambda x: -x[0])
    top = scored[:top_n]
    fam_label = f" (family: {family})" if family else ""
    lines = [f"## Promotion Candidates{fam_label} (top {len(top)})\n"]
    for rank, (score, s, ts, certs, deg) in enumerate(top, 1):
        lines.append(
            f"{rank}. **{s['shard_id']}** — score={score}\n"
            f"   Truth: {s['truth_status']} ({ts}) | Certs: {certs} | Degree: {deg} | "
            f"Promotion: {s['promotion_status']}"
        )
    return "\n".join(lines)


@mcp.tool()
def emit_mirror_family(shard_id: str = "") -> str:
    """Show all mirror relations for a shard across mediums."""
    graph_file = _MCP_DIR / "data" / "mycelium_graph.json"
    if not graph_file.exists():
        return "Graph not generated. Run generate_graph.py"
    data = json.loads(graph_file.read_text(encoding="utf-8"))
    mirrors = data.get("mirrors", [])
    if not shard_id:
        if not mirrors:
            return "No mirror edges in graph."
        lines = [f"## All Mirrors ({len(mirrors)})\n"]
        for m in mirrors:
            lines.append(f"- `{m['source_shard']}` ↔ `{m['target_shard']}` ({m.get('metadata', {}).get('mirror_type', '?')})")
        return "\n".join(lines)
    sl = shard_id.lower()
    hits = [m for m in mirrors if sl in m["source_shard"].lower() or sl in m["target_shard"].lower()]
    mirror_edges = [e for e in data["edges"]
                    if e["edge_type"] == "MIRROR"
                    and (sl in e["source_shard"].lower() or sl in e["target_shard"].lower())]
    if not hits and not mirror_edges:
        return f"No mirror relations found for '{shard_id}'."
    lines = [f"## Mirror Family: {shard_id}\n"]
    seen = set()
    for m in hits + mirror_edges:
        pair = (m["source_shard"], m["target_shard"])
        if pair not in seen:
            seen.add(pair)
            lines.append(f"- `{m['source_shard']}` ↔ `{m['target_shard']}`")
    return "\n".join(lines)


# ── Cloud-specific resource ───────────────────────────────────────
@mcp.resource("athena://cloud-water")
def resource_cloud() -> str:
    """Cloud element status — Lawful Multiplicity / Fiber Object."""
    from crystal_108d.brain import brain_status
    return (
        "## Cloud Lobe (Water) — Active\n\n"
        "**SFCR Mask**: 4 (0100)\n"
        "**Dimension Home**: 8D\n"
        "**Role**: Lawful Multiplicity / Fiber Object\n"
        "**Transport**: Z, A, L, Tunnel, Metro, Mycelium, Bus\n"
        "**Tools**: 14 registered\n\n"
        + brain_status()
    )


if __name__ == "__main__":
    mcp.run()
