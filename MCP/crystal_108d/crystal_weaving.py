# CRYSTAL: Xi108:W3:A7:S28 | face=R | node=310 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A7:S27->Xi108:W3:A7:S29->Xi108:W2:A7:S28->Xi108:W1:A7:S28->Xi108:W3:A6:S28->Xi108:W3:A8:S28

"""
Crystal Weaving Navigation — Braid Algebra & Permutation Fiber Atlases
=======================================================================
Provides the crystal weaving navigation system:
  - Braid algebra (n! permutations, adjacent swap generators, Lehmer ranking)
  - Weaving patterns (P3/P5/P7/P9 permutation fiber atlases, four-lens renderers)
  - Navigation rules (braided navigation, Cayley graph transport, infinity law)
  - Crystal routes (PS cross-braid, mixed-lock atlas, AZ4 gate, 96-stub transport)
"""

from ._cache import JsonCache

_CACHE = JsonCache("crystal_weaving.json")


def query_crystal_weaving(component: str = "all") -> str:
    """
    Query crystal weaving navigation — braid algebra & permutation fiber atlases.

    Components:
      - all               : Full crystal weaving overview
      - braid_algebra     : n! permutations, adjacent swaps, Lehmer ranking, braid-lift functor
      - weaving_patterns  : P3/P5/P7/P9 permutation fiber atlases with four-lens renderers
      - navigation_rules  : Braided navigation law, Cayley graph transport, infinity law
      - crystal_routes    : PS cross-braid, mixed-lock atlas, AZ4 gate, 96-stub transport
    """
    data = _CACHE.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "braid_algebra":
        return _format_braid_algebra(data)
    elif comp == "weaving_patterns":
        return _format_weaving_patterns(data)
    elif comp == "navigation_rules":
        return _format_navigation_rules(data)
    elif comp == "crystal_routes":
        return _format_crystal_routes(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, braid_algebra, "
            "weaving_patterns, navigation_rules, crystal_routes"
        )


def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    lines = [
        "## Crystal Weaving Navigation\n",
        f"**Title**: {meta.get('title', '')}",
        f"**Version**: {meta.get('version', '1.0.0')}",
        f"**Doc ID**: {meta.get('doc_id', '')}",
        f"**Created**: {meta.get('created', '')}",
        f"**Description**: {meta.get('description', '')}",
    ]

    # Braid algebra summary
    ba = data.get("braid_algebra", {})
    lines.append(f"\n### Braid Algebra")
    lines.append(f"- **Principle**: {ba.get('principle', '')}")
    families = ba.get("strand_families", {})
    for key, fam in families.items():
        lines.append(f"- **{key.upper()}**: {fam.get('n', '?')} strands, {fam.get('endpoint_count', '?')} endpoints")

    # Weaving patterns summary
    wp = data.get("weaving_patterns", {})
    lines.append(f"\n### Weaving Patterns")
    for pn in ["P3", "P5", "P7", "P9"]:
        pdata = wp.get(pn, {})
        if pdata:
            lines.append(f"- **{pn}**: {pdata.get('nodes', '?')} nodes, {pdata.get('edges', '?')} edges, diameter {pdata.get('diameter', '?')}")
    lr = wp.get("lens_renderers", {})
    if lr:
        for lens, desc in lr.items():
            lines.append(f"- **{lens}**: {desc}")

    # Navigation rules summary
    nr = data.get("navigation_rules", {})
    lines.append(f"\n### Navigation Rules")
    lines.append(f"- **Chain**: {nr.get('navigation_chain', '')}")
    lines.append(f"- **Infinity Law**: {nr.get('infinity_law', '')}")

    # Crystal routes summary
    cr = data.get("crystal_routes", {})
    lines.append(f"\n### Crystal Routes")
    ps = cr.get("PS_cross_braid", {})
    if ps:
        lines.append(f"- **PS Cross-Braid**: tetradic fiber size {ps.get('full_tetradic_fiber_size', '?')}")
    ml = cr.get("mixed_lock_atlas", {})
    if ml:
        lines.append(f"- **Mixed Lock Atlas**: {len(ml.get('pair_locks', {}))} pair + {len(ml.get('triple_locks', {}))} triple + 1 full lock")
    az = cr.get("AZ4_compression_gate", {})
    if az:
        lines.append(f"- **AZ4 Gate**: {az.get('description', '')}")
    t96 = cr.get("transport_96_stub", {})
    if t96:
        lines.append(f"- **96-Stub Transport**: {len(t96.get('classes', {}))} transport classes, {t96.get('total_organism_states', '?')} total states")

    return "\n".join(lines)


def _format_braid_algebra(data: dict) -> str:
    ba = data.get("braid_algebra", {})
    lines = [
        "## Braid Algebra\n",
        f"**Principle**: {ba.get('principle', '')}",
        "",
        "### Strand Families",
    ]
    families = ba.get("strand_families", {})
    for key, fam in families.items():
        lines.append(f"\n**{key.upper()}** ({fam.get('n', '?')} strands)")
        lines.append(f"- Labels: {fam.get('labels', [])}")
        lines.append(f"- Named moves: {', '.join(fam.get('named_moves', []))}")
        lines.append(f"- Endpoint count: {fam.get('endpoint_count', '?')}")
        lines.append(f"- Generators: {', '.join(fam.get('generators', []))}")
        if fam.get("note"):
            lines.append(f"- Note: {fam['note']}")

    dc = ba.get("dual_count", {})
    lines.append(f"\n### Dual Count")
    lines.append(f"- **Endpoint permutations**: {dc.get('endpoint_permutations', '')}")
    lines.append(f"- **Braid sequences**: {dc.get('braid_sequences', '')}")

    lines.append(f"\n### Lehmer Rank Law")
    lines.append(f"`{ba.get('lehmer_rank_law', '')}`")

    bl = ba.get("braid_lift_functor", {})
    if bl:
        lines.append(f"\n### Braid-Lift Functor")
        lines.append(f"**Formula**: `{bl.get('formula', '')}`")
        lines.append(f"**Nested levels**: {bl.get('nested_levels', [])}")
        ops = bl.get("operators", {})
        for op, desc in ops.items():
            lines.append(f"- **{op}**: {desc}")

    rc = ba.get("reweave_coordinate", {})
    if rc:
        lines.append(f"\n### Reweave Coordinate (RWLC)")
        lines.append(f"- Cycle depths: {rc.get('cycle_depths', [])}")
        lc = rc.get("local_clocks", {})
        lines.append(f"- Local clocks: {lc}")
        gc = rc.get("global_return_clocks", {})
        lines.append(f"- Global return clocks: {gc}")

    pr = ba.get("propagation_receipt", {})
    if pr:
        lines.append(f"\n### Propagation Receipt")
        lines.append(f"- **Levels**: {' -> '.join(pr.get('levels', []))}")
        lines.append(f"- **Per-level fields**: {', '.join(pr.get('per_level_fields', []))}")

    return "\n".join(lines)


def _format_weaving_patterns(data: dict) -> str:
    wp = data.get("weaving_patterns", {})
    lines = [
        "## Weaving Patterns — Permutation Fiber Atlases\n",
    ]

    fc = wp.get("full_coordinate", {})
    if fc:
        lines.append(f"**Full Coordinate**: `{fc.get('formula', '')}`")
        lines.append("")

    for pn in ["P3", "P5", "P7", "P9"]:
        pdata = wp.get(pn, {})
        if not pdata:
            continue
        lines.append(f"### {pn}")
        lines.append(f"**{pdata.get('description', '')}**")
        lines.append(f"- Nodes: {pdata.get('nodes', '?')}, Edges: {pdata.get('edges', '?')}, Degree: {pdata.get('degree', '?')}, Diameter: {pdata.get('diameter', '?')}")

        if pdata.get("split"):
            lines.append(f"- Split: `{pdata['split']}`")
        if pdata.get("decomposition"):
            lines.append(f"- Decomposition: `{pdata['decomposition']}`")
        if pdata.get("route_law"):
            lines.append(f"- Route law: {pdata['route_law']}")

        # Atlas table for P3
        atlas = pdata.get("atlas", [])
        if atlas:
            lines.append("")
            lines.append("| Rank | pi | Braid | Burden | Sign | Order |")
            lines.append("|------|-----|-------|--------|------|-------|")
            for row in atlas:
                lines.append(
                    f"| {row['rank']} | {row['pi']} | {row['braid']} | "
                    f"{row['burden']} | {row['sign']} | {row['order']} |"
                )

        # Burden shells
        bs = pdata.get("burden_shells", [])
        if bs:
            lines.append(f"- Burden shells: {bs}")

        # Return class
        rc = pdata.get("return_class_size")
        if rc:
            lines.append(f"- Return class size: {rc}")

        # Anchor nodes
        anchors = pdata.get("anchor_nodes", {})
        if anchors:
            lines.append("- Anchor nodes:")
            for name, adata in anchors.items():
                lines.append(f"  - **{name}**: pi={adata.get('pi','')}, rank={adata.get('rank','')}, burden={adata.get('burden','')}, order={adata.get('order','')}")

        lines.append("")

    # Lens renderers
    lr = wp.get("lens_renderers", {})
    if lr:
        lines.append("### Four-Lens Renderers")
        for lens, desc in lr.items():
            lines.append(f"- **{lens}**: {desc}")

    # Universal upgrade
    uul = wp.get("universal_upgrade_law", "")
    if uul:
        lines.append(f"\n### Universal Upgrade Law")
        lines.append(uul)

    return "\n".join(lines)


def _format_navigation_rules(data: dict) -> str:
    nr = data.get("navigation_rules", {})
    lines = [
        "## Navigation Rules\n",
        f"**Navigation chain**: {nr.get('navigation_chain', '')}",
        f"**Infinity law**: {nr.get('infinity_law', '')}",
    ]

    bn = nr.get("braided_navigation", {})
    if bn:
        lines.append(f"\n### Braided Navigation")
        lines.append(f"**Formula**: `{bn.get('formula', '')}`")
        steps = bn.get("steps", [])
        for i, step in enumerate(steps, 1):
            lines.append(f"  {i}. {step}")

    ln = nr.get("local_navigation", {})
    if ln:
        lines.append(f"\n### Local Navigation")
        lines.append(f"- **Distance metric**: `{ln.get('distance_metric', '')}`")
        lines.append(f"- **Transport**: `{ln.get('transport', '')}`")

    cg = nr.get("cayley_graph_invariants", {})
    if cg:
        lines.append(f"\n### Cayley Graph Invariants")
        lines.append(f"**Formula**: `{cg.get('formula', '')}`")
        lines.append("")
        lines.append("| n | Nodes | Edges | Diameter |")
        lines.append("|---|-------|-------|----------|")
        for fam in cg.get("families", []):
            lines.append(f"| {fam['n']} | {fam['nodes']:,} | {fam['edges']:,} | {fam['diameter']} |")

    return "\n".join(lines)


def _format_crystal_routes(data: dict) -> str:
    cr = data.get("crystal_routes", {})
    lines = [
        "## Crystal Routes\n",
    ]

    # PS Cross-Braid
    ps = cr.get("PS_cross_braid", {})
    if ps:
        lines.append("### PS Cross-Braid")
        lines.append(f"**{ps.get('description', '')}**")
        tbl = ps.get("two_braid_levels", {})
        if tbl:
            lines.append(f"- Internal: {tbl.get('internal', '')}")
            lines.append(f"- External: {tbl.get('external', '')}")
        lines.append(f"- Full tetradic fiber size: {ps.get('full_tetradic_fiber_size', '?'):,}")
        lines.append(f"- Resonant spine: {ps.get('resonant_spine', '')}")
        lines.append(f"- Tetradic address: `{ps.get('tetradic_address', '')}`")
        lines.append("")

    # Mixed Lock Atlas
    ml = cr.get("mixed_lock_atlas", {})
    if ml:
        lines.append("### Mixed Lock Atlas")
        lines.append(f"**{ml.get('description', '')}**")
        lines.append(f"- Verdict classes: {', '.join(ml.get('verdict_classes', []))}")
        lines.append(f"- Defect channels: {', '.join(ml.get('defect_channels', []))}")
        lines.append(f"- Heptadic echo defect: `{ml.get('heptadic_echo_defect', '')}`")
        lines.append("")

        # Pair locks
        pairs = ml.get("pair_locks", {})
        if pairs:
            lines.append("**Pair Locks**:")
            for name, ldata in pairs.items():
                lines.append(f"- **{name}**: {ldata.get('type','')} (gcd={ldata.get('gcd','')}, seal={ldata.get('seal','')}, fiber={ldata.get('fiber_size', ''):,})")

        # Triple locks
        triples = ml.get("triple_locks", {})
        if triples:
            lines.append("\n**Triple Locks**:")
            for name, ldata in triples.items():
                lines.append(f"- **{name}**: {ldata.get('type','')} (seal={ldata.get('seal','')}, fiber={ldata.get('fiber_size', ''):,})")

        # Full lock
        full = ml.get("full_lock", {})
        if full:
            lines.append("\n**Full Lock**:")
            for name, ldata in full.items():
                lines.append(f"- **{name}**: {ldata.get('type','')} (seal={ldata.get('seal','')}, fiber={ldata.get('fiber_size', ''):,})")

        lines.append("")

    # AZ4 Gate
    az = cr.get("AZ4_compression_gate", {})
    if az:
        lines.append("### AZ4 Compression Gate")
        lines.append(f"**{az.get('description', '')}**")
        lines.append(f"- Formula: `{az.get('formula', '')}`")
        lines.append(f"- Two-speed seed: active={az.get('two_speed_seed', {}).get('active','')}, latent={az.get('two_speed_seed', {}).get('latent','')}")
        cards = az.get("operator_cards", {})
        if cards:
            lines.append("\n**Operator Cards**:")
            for card, desc in cards.items():
                lines.append(f"- **{card}**: {desc}")
        lines.append("")

    # 96-Stub Transport
    t96 = cr.get("transport_96_stub", {})
    if t96:
        lines.append("### 96-Stub Transport Classifier")
        lines.append(f"**{t96.get('description', '')}**")
        lines.append(f"- Hidden bundle size: {t96.get('hidden_bundle_size', '?')}")
        lines.append(f"- Total organism states: {t96.get('total_organism_states', '?'):,}")
        lines.append(f"- Local primitive families: {', '.join(t96.get('local_primitive_families', []))}")
        classes = t96.get("classes", {})
        if classes:
            lines.append("\n**Transport Classes**:")
            for cls, desc in classes.items():
                lines.append(f"- **{cls}**: {desc}")

    return "\n".join(lines)
