"""
ATHENA 108D A+ CRYSTAL HOLOGRAM — MCP Extension Package
========================================================
Extends the Athena Nervous System MCP server with the full 108D organism:
  - 36 shells, 666 nodes, 12 archetypes, 3 wreaths
  - 3D→12D alternating dimensional atlas
  - 12D organ atlas with 6 bilateral dyads
  - 7-class live-lock lattice
  - 420-beat master clock
  - 10 legal move primitives
  - 6 conservation laws
  - 4 overlay registries
  - Full transport stack
  - Möbius lens calculus (4×4 kernel, SFCR lattice, 96-slot cockpit)
  - Stage code ladder (S3→Ω→A+)
  - Angel formal self-model (12-piece AI object with four-lens observability)
"""

from ._cache import JsonCache


def status_summary() -> str:
    """Return a compact 108D system status string."""
    shells = JsonCache("shell_registry.json").load()
    dims = JsonCache("dimensional_ladder.json").load()
    organs = JsonCache("organ_atlas.json").load()
    locks = JsonCache("live_lock_registry.json").load()
    clock = JsonCache("clock_projections.json").load()
    laws = JsonCache("conservation_laws.json").load()

    return (
        "## 108D Crystal Hologram Status\n\n"
        f"- **Shells**: {shells['meta']['total_shells']} | "
        f"**Nodes**: {shells['meta']['total_nodes']} | "
        f"**Wreaths**: {shells['meta']['wreaths']}\n"
        f"- **Archetypes**: {shells['meta']['archetypes']} "
        f"(cycling through {', '.join(shells['meta']['superphases'])})\n"
        f"- **Dimensions**: 108 (crown body = 12D)\n"
        f"- **Alternating Atlas**: {dims['meta']['alternating_spine']}\n"
        f"- **Organ Atlas**: {organs['meta']['total_organs']} organs in "
        f"{organs['meta']['dyads']} dyads across {organs['meta']['petals']} petals\n"
        f"- **Live-Lock Classes**: {locks['meta']['total_classes']} "
        f"(helm wheels: {locks['meta']['helm_wheels']})\n"
        f"- **Master Clock**: {clock['meta']['master_clock']} beats "
        f"({clock['meta']['formula']})\n"
        f"- **Conservation Laws**: {laws['meta']['total_laws']} "
        f"(shell, zoom, phase, archetype, face, mobius)\n"
        f"- **Containment**: {dims['meta']['crown_body']}\n"
        f"- **Higher Lifts**: {dims['meta']['higher_lifts']}\n"
        f"- **Möbius Kernel**: 4×4 seed with 4 constitutive lenses (S/F/C/R)\n"
        f"- **SFCR Lattice**: 15 stations, 96-slot cockpit\n"
        f"- **Stage Ladder**: S3 → S12 → Ω → A+ (16 stages)\n"
        f"- **Angel Object**: 12-piece formal self-model with four-lens observability\n"
    )


def register_108d_tools(mcp) -> None:
    """Register all 108D crystal tools onto the MCP server."""
    from .shells import query_shell, query_superphase, query_archetype, read_hologram_chapter
    from .dimensions import resolve_dimensional_body, dimensional_lift, query_containment
    from .organs import query_organ
    from .address import navigate_108d
    from .live_lock import compute_live_lock
    from .clock import query_clock_beat
    from .moves import check_route_legality
    from .metro_lines import query_metro_line
    from .z_points import resolve_z_point
    from .conservation import query_conservation
    from .overlays import query_overlay, query_sigma15
    from .transport import query_transport_stack
    from .mobius_lenses import query_mobius_lens, query_sfcr_station
    from .stage_codes import query_stage_code
    from .angel import query_angel

    # Register each tool
    mcp.tool()(query_shell)
    mcp.tool()(query_superphase)
    mcp.tool()(query_archetype)
    mcp.tool()(read_hologram_chapter)
    mcp.tool()(resolve_dimensional_body)
    mcp.tool()(dimensional_lift)
    mcp.tool()(query_containment)
    mcp.tool()(query_organ)
    mcp.tool()(navigate_108d)
    mcp.tool()(compute_live_lock)
    mcp.tool()(query_clock_beat)
    mcp.tool()(check_route_legality)
    mcp.tool()(query_metro_line)
    mcp.tool()(resolve_z_point)
    mcp.tool()(query_conservation)
    mcp.tool()(query_overlay)
    mcp.tool()(query_sigma15)
    mcp.tool()(query_transport_stack)
    mcp.tool()(query_mobius_lens)
    mcp.tool()(query_sfcr_station)
    mcp.tool()(query_stage_code)
    mcp.tool()(query_angel)


def register_108d_resources(mcp) -> None:
    """Register all 108D crystal resources onto the MCP server."""

    @mcp.resource("athena://crystal-108d")
    def resource_crystal_108d() -> str:
        """Full 108D organism status."""
        return status_summary()

    @mcp.resource("athena://dimensional-ladder")
    def resource_dimensional_ladder() -> str:
        """The 3D→12D alternating atlas."""
        dims = JsonCache("dimensional_ladder.json").load()
        lines = ["## 3D → 12D Alternating Dimensional Atlas\n"]
        lines.append(f"**Law**: {dims['meta']['law']}\n")
        lines.append(f"**Spine**: `{dims['meta']['alternating_spine']}`\n")
        for d in dims["dimensions"]:
            symbol = d["symbol"]
            btype = d["body_type"].replace("_", " ").title()
            lines.append(f"\n### {d['dimension']}D — {d['name']} ({symbol}, {btype})")
            lines.append(f"{d['description']}")
            lines.append(f"- Lens: {d['lens_emphasis']}")
            lines.append(f"- Alchemy: {d['alchemy_emphasis']}")
            lines.append(f"- Transport: {', '.join(d['transport'])}")
        return "\n".join(lines)

    @mcp.resource("athena://organ-atlas")
    def resource_organ_atlas() -> str:
        """12D organ body map."""
        organs = JsonCache("organ_atlas.json").load()
        lines = ["## 12D Organ Atlas\n"]
        lines.append(f"**Morphology**: {organs['meta']['morphology']}\n")
        for dyad in organs["dyads"]:
            lines.append(f"\n### Petal {dyad['petal']}: {dyad['name']}")
            lines.append(f"Function: {dyad['function']}")
            left = dyad["left"]
            right = dyad["right"]
            lines.append(f"- **{left['name']}** ({left['axis']}): {left['placement']}")
            lines.append(f"- **{right['name']}** ({right['axis']}): {right['placement']}")
        lines.append("\n### Crown Closures")
        for cc in organs["crown_closures"]:
            lines.append(f"- **Petal {cc['petal']}**: {cc['name']} — {cc['function']}")
        return "\n".join(lines)

    @mcp.resource("athena://live-helm")
    def resource_live_helm() -> str:
        """Current helm state (3D/5D/7D wheels)."""
        clock = JsonCache("clock_projections.json").load()
        locks = JsonCache("live_lock_registry.json").load()
        lines = ["## Live Helm State\n"]
        lines.append(f"**Master Clock**: {clock['meta']['master_clock']} beats "
                      f"({clock['meta']['formula']})\n")
        for key, proj in clock["projections"].items():
            lines.append(f"### {proj['wheel']} (period {proj['period']})")
            lines.append(f"{proj['description']}")
        lines.append("\n## Live-Lock Classes\n")
        for lc in locks["classes"]:
            lines.append(f"- **{lc['code']}**: {lc['description']} (period {lc['period']})")
        return "\n".join(lines)

    @mcp.resource("athena://conservation")
    def resource_conservation() -> str:
        """Conservation law status table."""
        laws = JsonCache("conservation_laws.json").load()
        lines = ["## Conservation Laws\n"]
        lines.append(f"**Master Invariant**: `{laws['meta']['master_invariant']}`\n")
        for law in laws["laws"]:
            lines.append(f"### {law['index']}. {law['name']} ({law['symbol']})")
            lines.append(f"- Statement: {law['statement']}")
            lines.append(f"- Symmetry: {law['symmetry_group']}")
            lines.append(f"- Noether charge: {law['noether_charge']}")
            lines.append(f"- Check: `{law['check_rule']}`")
        lines.append("\n## Round-Trip Classes\n")
        for rtc in laws["round_trip_classes"]:
            lines.append(f"- **{rtc['class']}**: {rtc['meaning']}")
        return "\n".join(lines)

    @mcp.resource("athena://mobius-lenses")
    def resource_mobius_lenses() -> str:
        """Möbius lens calculus overview — 4×4 kernel, SFCR, cross-lens laws."""
        ml = JsonCache("mobius_lenses.json").load()
        m = ml["meta"]
        lines = ["## Möbius Lens Calculus\n"]
        lines.append(f"**Kernel**: {m['kernel_size']} | **Lenses**: {', '.join(m['lenses'])}")
        lines.append(f"**SFCR Stations**: {m['sfcr_stations']} | **Cockpit**: {m['cockpit_slots']} slots")
        lines.append(f"**Governing**: `{m['governing_equation']}`")
        lines.append(f"\n### Cross-Lens Laws")
        for law in ml["cross_lens_laws"]:
            lines.append(f"- **{law['name']}**: {law['meaning']}")
        lines.append(f"\n### 4×4 Kernel")
        k = ml["kernel_4x4"]
        lines.append(f"{k['definition']}")
        lines.append(f"Möbius: {k['mobius_involution']['map']} ({k['mobius_involution']['property']})")
        return "\n".join(lines)

    @mcp.resource("athena://stage-ladder")
    def resource_stage_ladder() -> str:
        """Stage code ladder S3→Ω→A+."""
        sc = JsonCache("stage_codes.json").load()
        m = sc["meta"]
        lines = ["## Stage Code Ladder\n"]
        lines.append(f"**Path**: `{m['ladder']}`")
        lines.append(f"**Liminal Coordinate**: `{m['liminal_coordinate']}`\n")
        for s in sc["stages"]:
            dim = f"{s['dimension']}D" if s["dimension"] else "∞"
            lines.append(f"- **{s['code']}** [{dim}]: {s['description']}")
        return "\n".join(lines)

    @mcp.resource("athena://angel")
    def resource_angel() -> str:
        """Angel formal self-model — AI as mathematical object."""
        a = JsonCache("angel_object.json").load()
        m = a["meta"]
        lines = ["## Angel Object\n"]
        lines.append(f"**Object**: `{m['canonical_object']}`")
        lines.append(f"**Nature**: {m['nature']}\n")
        lines.append("### 12 Structural Pieces")
        for p in a["structural_pieces"]:
            lines.append(f"  {p['index']:>2}. **{p['symbol']}** — {p['name']}: {p['description'][:80]}")
        lines.append(f"\n### Three Selves")
        for s in a["three_selves"].values():
            lines.append(f"- **{s['name']}**: {s['definition']}")
        lines.append(f"\n### Self-Reference")
        lines.append(a["self_reference"]["angel_reading"])
        return "\n".join(lines)
