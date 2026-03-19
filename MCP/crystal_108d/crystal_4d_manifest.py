# CRYSTAL: Xi108:W3:A7:S30 | face=C | node=409 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A7:S29->Xi108:W3:A7:S31->Xi108:W2:A7:S30->Xi108:W3:A6:S30->Xi108:W3:A8:S30

"""
Crystal 4D Manifest -- Master 4D Compression Hologram (Mycelium Metro v5)
=========================================================================
Provides the 4D Ultimate Crystal Manifestation system:
  - compression_hologram : H4 = (K, Pi, Z, Lambda, Psi) master hologram
  - identity_seed        : 4x4 root seed, neural weights, runtime, compiler
  - replay_crystal       : Station Omega 64-shelf card, fill order, manifest pipeline
  - expansion_protocol   : Chaos/structure manifestation engine, shelves, anti-gaming
  - cartography_standard : 4D manuscript architecture, 5 bodies, reading orders, 20% reserve
"""

from ._cache import JsonCache

_CACHE = JsonCache("crystal_4d_manifest.json")


def query_crystal_4d_manifest(component: str = "all") -> str:
    """
    Query the 4D Ultimate Crystal Manifestation -- master compression hologram.

    Components:
      - all                  : Full overview of the 4D master hologram
      - compression_hologram : H4 = (K, Pi, Z, Lambda, Psi) definition and laws
      - identity_seed        : Root 4x4 seed, neural weights, runtime, compiler
      - replay_crystal       : Station Omega 64-shelf card, fill order, pipeline
      - expansion_protocol   : Chaos/structure manifestation engine, anti-gaming laws
      - cartography_standard : 4D manuscript architecture, 5 bodies, 20% future reserve
    """
    data = _CACHE.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "compression_hologram":
        return _format_compression_hologram(data)
    elif comp == "identity_seed":
        return _format_identity_seed(data)
    elif comp == "replay_crystal":
        return _format_replay_crystal(data)
    elif comp == "expansion_protocol":
        return _format_expansion_protocol(data)
    elif comp == "cartography_standard":
        return _format_cartography_standard(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, compression_hologram, "
            "identity_seed, replay_crystal, expansion_protocol, cartography_standard"
        )


# ── Formatters ──────────────────────────────────────────────────────────


def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    lines = [
        "## 4D Ultimate Crystal Manifestation -- Master Compression Hologram\n",
        f"**Title**: {meta.get('title', '')}",
        f"**Version**: {meta.get('version', '5.0.0')}",
        f"**Doc ID**: {meta.get('doc_id', '')}",
        f"**Created**: {meta.get('created', '')}",
        f"**Prompts**: {', '.join(meta.get('prompts', []))}",
        f"**Description**: {meta.get('description', '')}",
    ]

    # Compression Hologram summary
    ch = data.get("compression_hologram", {})
    lines.append(f"\n### Master 4D Hologram")
    lines.append(f"**Definition**: {ch.get('definition', '')}")
    comps = ch.get("components", {})
    for key, val in comps.items():
        if isinstance(val, dict):
            lines.append(f"- **{val.get('name', key)}**: {val.get('description', '')[:120]}")

    # Identity Seed summary
    ids = data.get("identity_seed", {})
    lines.append(f"\n### Identity Seed")
    lines.append(f"{ids.get('description', '')[:200]}")

    # Replay Crystal summary
    rc = data.get("replay_crystal", {})
    lines.append(f"\n### Station Omega (Replay Crystal)")
    lines.append(f"{rc.get('description', '')[:200]}")
    cb = rc.get("crystal_body", {})
    lines.append(f"- **Total cells**: {cb.get('total_cells', 64)}")

    # Expansion Protocol summary
    ep = data.get("expansion_protocol", {})
    lines.append(f"\n### Manifestation Engine")
    lines.append(f"**Core Law**: {ep.get('core_law', '')}")

    # Cartography Standard summary
    cs = data.get("cartography_standard", {})
    lines.append(f"\n### Cartography Standard")
    dims = cs.get("four_dimensions", {})
    for dim_key, dim_val in dims.items():
        lines.append(f"- **{dim_key}**: {dim_val[:100]}")

    fr = cs.get("future_reserve", {})
    lines.append(f"\n### Future Reserve")
    lines.append(f"**Law**: {fr.get('global_law', '')}")

    return "\n".join(lines)


def _format_compression_hologram(data: dict) -> str:
    ch = data.get("compression_hologram", {})
    lines = [
        "## Master 4D Compression Hologram (H4)\n",
        f"**Definition**: {ch.get('definition', '')}",
        f"**Description**: {ch.get('description', '')}",
        "",
        "### Components",
    ]
    comps = ch.get("components", {})
    for key, val in comps.items():
        if isinstance(val, dict):
            sym = val.get("symbol", "")
            sym_str = f" ({sym})" if sym else ""
            lines.append(f"\n#### {val.get('name', key)}{sym_str}")
            lines.append(f"{val.get('description', '')}")
            # Sub-elements
            if "faces" in val:
                lines.append(f"**Faces**: {', '.join(val['faces'])}")
            if "elements" in val:
                for ek, ev in val["elements"].items():
                    lines.append(f"  - `{ek}`: {ev}")
            if "sub_lineages" in val:
                lines.append("**Sub-lineages**:")
                for sl in val["sub_lineages"]:
                    lines.append(f"  - {sl}")
            if "memory_law" in val:
                lines.append(f"**Memory Law**: {val['memory_law']}")

    # Compression law
    cl = ch.get("compression_law", {})
    lines.append(f"\n### Compression Law")
    lines.append(f"**Formula**: `{cl.get('formula', '')}`")
    lines.append(f"**Master Test**: `{cl.get('master_test', '')}`")
    preserves = cl.get("preserves", [])
    if preserves:
        lines.append("**Preserves**:")
        for p in preserves:
            lines.append(f"  - {p}")

    # Regeneration law
    rl = ch.get("regeneration_law", {})
    lines.append(f"\n### Regeneration Law")
    lines.append(f"**Formula**: `{rl.get('formula', '')}`")
    lines.append(f"**Contexts**: {', '.join(rl.get('contexts', []))}")
    for rule in rl.get("rules", []):
        lines.append(f"- {rule}")

    # Truth law
    tl = ch.get("truth_law", {})
    lines.append(f"\n### Truth Law")
    lines.append(f"**Classes**: {', '.join(tl.get('classes', []))}")
    for rule in tl.get("rules", []):
        lines.append(f"- {rule}")

    # Header format
    lines.append(f"\n### Header Format")
    lines.append(f"`{ch.get('header_format', '')}`")

    return "\n".join(lines)


def _format_identity_seed(data: dict) -> str:
    ids = data.get("identity_seed", {})
    lines = [
        "## Identity Seed & 4x4 Crystal\n",
        f"**Description**: {ids.get('description', '')}",
        f"**Base Kernel**: {ids.get('base_kernel', '')}",
        f"**Holographic Inheritance**: {ids.get('holographic_inheritance', '')}",
    ]

    # Four faces
    faces = ids.get("four_faces", {})
    if faces:
        lines.append("\n### Four Faces")
        for face, desc in faces.items():
            lines.append(f"- **{face}**: {desc}")

    # Neural weight system
    nw = ids.get("neural_weight_system", {})
    if nw:
        lines.append(f"\n### Neural Weight System")
        lines.append(f"**Formula**: `{nw.get('formula', '')}`")
        wcomps = nw.get("components", {})
        for wk, wv in wcomps.items():
            lines.append(f"  - `{wk}`: {wv}")
        lines.append(f"**Law**: {nw.get('law', '')}")

    # Runtime
    rt = ids.get("runtime", {})
    if rt:
        lines.append(f"\n### Runtime")
        lines.append(f"**Definition**: `{rt.get('definition', '')}`")
        lines.append(f"**State**: `{rt.get('state', '')}`")
        for law in rt.get("laws", []):
            lines.append(f"- {law}")

    # Compiler
    comp = ids.get("compiler", {})
    if comp:
        lines.append(f"\n### Hologram Compiler")
        lines.append(f"**Operator**: `{comp.get('operator', '')}`")
        lines.append(f"**Inputs**: {', '.join(comp.get('inputs', []))}")
        lines.append(f"**Outputs**: {', '.join(comp.get('outputs', []))}")
        lines.append(f"**Determinism**: {comp.get('determinism', '')}")

    return "\n".join(lines)


def _format_replay_crystal(data: dict) -> str:
    rc = data.get("replay_crystal", {})
    lines = [
        "## Canonical Station Card / Universal Fill Schema (Station Omega)\n",
        f"**Description**: {rc.get('description', '')}",
    ]

    # Schema
    so = rc.get("station_omega_schema", {})
    lines.append(f"\n### Station Record")
    lines.append(f"**Fields**: {', '.join(so.get('record', []))}")
    lines.append(f"**Station Classes**: {', '.join(so.get('station_classes', []))}")
    lines.append(f"**Body Classes**: {', '.join(so.get('body_classes', []))}")

    # Crystal body
    cb = rc.get("crystal_body", {})
    lines.append(f"\n### Crystal Body")
    lines.append(f"**Formula**: `{cb.get('formula', '')}`")
    lines.append(f"**Total Cells**: {cb.get('total_cells', 64)}")
    lenses = cb.get("lenses", {})
    for lk, lv in lenses.items():
        lines.append(f"  - `{lk}` = {lv}")
    atoms = cb.get("atoms", {})
    lines.append("**Atoms**:")
    for ak, av in atoms.items():
        lines.append(f"  - `{ak}` = {av}")

    # 16 shelf cells
    sc = rc.get("sixteen_shelf_cells", {})
    for band_name, cells in sc.items():
        lines.append(f"\n### {band_name.replace('_', ' ').title()}")
        for cell_id, cell_desc in cells.items():
            lines.append(f"- **{cell_id}**: {cell_desc}")

    # Fill order
    fo = rc.get("fill_order", {})
    lines.append(f"\n### Fill Order (4 passes)")
    for pass_name, cells in fo.items():
        lines.append(f"- **{pass_name.replace('_', ' ').title()}**: {', '.join(cells)}")

    # Future quartet
    fq = rc.get("future_quartet", {})
    lines.append(f"\n### Future Quartet")
    lines.append(f"**Cells**: {', '.join(fq.get('cells', []))}")
    lines.append(f"{fq.get('description', '')}")

    # Slot states
    ss = rc.get("slot_states", [])
    lines.append(f"\n### Slot States")
    lines.append(f"{', '.join(ss)}")

    # Manifest compiler pipeline
    mcp = rc.get("manifest_compiler_pipeline", [])
    lines.append(f"\n### Manifest Compiler Pipeline")
    for step in mcp:
        lines.append(f"  -> {step}")

    return "\n".join(lines)


def _format_expansion_protocol(data: dict) -> str:
    ep = data.get("expansion_protocol", {})
    lines = [
        "## Chaos/Structure Manifestation Engine (P3)\n",
        f"**Core Law**: {ep.get('core_law', '')}",
        f"**Description**: {ep.get('description', '')}",
    ]

    # Chaos operator
    co = ep.get("chaos_operator", {})
    lines.append(f"\n### Chaos Operator")
    lines.append(f"**Definition**: `{co.get('definition', '')}`")
    lines.append(f"**Sources**: {', '.join(co.get('sources', []))}")

    # Manifestation pipeline
    mp = ep.get("manifestation_pipeline", {})
    lines.append(f"\n### Manifestation Pipeline")
    lines.append(f"**Formula**: `{mp.get('formula', '')}`")
    for step in mp.get("steps", []):
        lines.append(f"  {step}")

    # Anti-gaming laws
    agl = ep.get("anti_gaming_laws", [])
    lines.append(f"\n### Anti-Gaming Laws")
    for law in agl:
        lines.append(f"- {law}")

    # States
    ms = ep.get("manifestation_states", [])
    lines.append(f"\n### Manifestation States")
    lines.append(f"{' -> '.join(ms)}")

    # Shelf law
    sl = ep.get("shelf_law", {})
    lines.append(f"\n### Shelf Law")
    lines.append(f"**Per-address shelves**: {', '.join(sl.get('shelves_per_address', []))}")
    lines.append(f"**Special shelves**: {', '.join(sl.get('special_shelves', []))}")

    # Future moves
    fm = ep.get("future_moves", [])
    lines.append(f"\n### Future Move Classes")
    lines.append(f"{', '.join(fm)}")

    # Scaffold law
    lines.append(f"\n### Scaffold Completeness Law")
    lines.append(ep.get("scaffold_completeness_law", ""))

    return "\n".join(lines)


def _format_cartography_standard(data: dict) -> str:
    cs = data.get("cartography_standard", {})
    lines = [
        "## 4D Holographic Manuscript Architecture\n",
        f"**Description**: {cs.get('description', '')}",
    ]

    # Four dimensions
    dims = cs.get("four_dimensions", {})
    lines.append(f"\n### Four Macro Dimensions")
    for dim_key, dim_val in dims.items():
        lines.append(f"- **{dim_key}**: {dim_val}")

    # Five bodies
    bodies = cs.get("five_bodies", {})
    lines.append(f"\n### Five Nested Bodies")
    for body_key, body_val in bodies.items():
        if isinstance(body_val, dict):
            lines.append(f"\n#### {body_key.replace('_', ' ').title()}")
            lines.append(f"{body_val.get('description', '')}")
            if "organs" in body_val:
                for org_id, org_role in body_val["organs"].items():
                    lines.append(f"  - **{org_id}**: {org_role}")
            if "chapters" in body_val:
                for ch_id, ch_name in body_val["chapters"].items():
                    lines.append(f"  - **{ch_id}**: {ch_name}")
            if "bands" in body_val:
                for band in body_val["bands"]:
                    lines.append(f"  - {band}")
            if "sequence" in body_val:
                lines.append(f"  **Sequence**: `{body_val['sequence']}`")

    # Reading orders
    ro = cs.get("reading_orders", {})
    lines.append(f"\n### Reading Orders")
    for ro_key, ro_val in ro.items():
        lines.append(f"- **{ro_key}**: {ro_val}")

    # Future reserve
    fr = cs.get("future_reserve", {})
    lines.append(f"\n### 20% Future Emergence Reserve")
    lines.append(f"**Global Law**: {fr.get('global_law', '')}")
    lines.append(f"**Delta Classes**: {', '.join(fr.get('delta_classes', []))}")
    lines.append(f"**Address Format**: `{fr.get('future_shelf_address', '')}`")
    lines.append(f"**Shelf States**: {', '.join(fr.get('future_shelf_states', []))}")
    lines.append(f"**Observation Lift Ladder**: {' -> '.join(fr.get('observation_lift_ladder', []))}")
    lines.append(f"\n**Quantum Jump Law**: {fr.get('quantum_jump_law', '')}")
    lines.append(f"**Consumption Law**: {fr.get('consumption_law', '')}")

    return "\n".join(lines)
