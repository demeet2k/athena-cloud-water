"""
E₈ Lattice & Crystalline Hybrid Mathematics
=============================================
Provides the complete E₈ lattice manuscript structure:
  - Master equation w = (1+i)/2
  - E₈ identification (240 vertices + 8 Cartan = 248 = dim(e₈))
  - Dual-body architecture (Body A: 21 chapters + 16 appendices,
    Body B: 9 chapters + 16 reverse appendices)
  - Metro map topology with hub classifications
  - Key theorems and open conjectures
"""

from ._cache import JsonCache

_E8 = JsonCache("e8_lattice.json")


def query_e8_lattice(component: str = "all") -> str:
    """
    Query the E₈ lattice and crystalline hybrid mathematics.

    Components:
      - all         : Full E₈ lattice overview
      - seed        : Master equation w=(1+i)/2 and identification
      - body_a      : Body A — 21 legacy chapters
      - body_b      : Body B — 9 emergent chapters (self-navigation)
      - appendices  : Appendix fields (A-P legacy, Z-K reverse)
      - metro       : Metro map topology and hub types
      - bridge      : Möbius bridge hinges between bodies
      - theorems    : Key mathematical results
      - conjectures : 13 open conjectures (frontier)
      - scale       : Renormalization flow 240→60→15→4→1
    """
    data = _E8.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "seed":
        return _format_seed(data)
    elif comp == "body_a":
        return _format_body_a(data)
    elif comp == "body_b":
        return _format_body_b(data)
    elif comp == "appendices":
        return _format_appendices(data)
    elif comp == "metro":
        return _format_metro(data)
    elif comp == "bridge":
        return _format_bridge(data)
    elif comp == "theorems":
        return _format_theorems(data)
    elif comp == "conjectures":
        return _format_conjectures(data)
    elif comp == "scale":
        return _format_scale(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, seed, body_a, "
            "body_b, appendices, metro, bridge, theorems, conjectures, scale"
        )


def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    lines = [
        "## E₈ Lattice — Crystalline Hybrid Mathematics\n",
        f"**Master Equation**: `{meta.get('master_equation', 'w = (1+i)/2')}`",
        f"**Master Identity**: `{meta.get('master_identity', 'Ω(Ω) = Ω')}`",
        f"**Dimensions**: {meta.get('dimensions', '248 = dim(e₈)')}",
        f"**Body A**: {meta.get('body_a_chapters', 21)} chapters + {meta.get('body_a_appendices', 16)} appendices",
        f"**Body B**: {meta.get('body_b_chapters', 9)} chapters + {meta.get('body_b_appendices', 16)} reverse appendices",
        f"**Total Files**: {meta.get('total_files', 73)}",
        f"**Total Characters**: {meta.get('total_characters', '1,007,065')}",
    ]
    return "\n".join(lines)


def _format_seed(data: dict) -> str:
    seed = data.get("seed", {})
    lines = [
        "## Master Equation\n",
        f"**Generator**: `{seed.get('generator', 'w = (1+i)/2')}`",
        f"**Master Product**: `{seed.get('master_product', 'w · w⁻¹ = 1')}`",
        f"**E₈ Identification**: {seed.get('e8_identification', '240 + 8 = 248 = dim(e₈)')}",
    ]
    if "key_constants" in seed:
        lines.append("\n**Key Constants**:")
        for k, v in seed["key_constants"].items():
            lines.append(f"  - {k}: {v}")
    return "\n".join(lines)


def _format_body_a(data: dict) -> str:
    body = data.get("body_a", {})
    lines = ["## Body A — Legacy 21-Chapter Crystal\n"]
    chapters = body.get("chapters", [])
    for ch in chapters:
        if isinstance(ch, dict):
            lines.append(
                f"- **Ch{ch.get('number', '?')}** [{ch.get('station', '')}]: "
                f"{ch.get('title', '')} — {ch.get('element', '')}"
            )
        else:
            lines.append(f"- {ch}")
    if "parts" in body:
        lines.append("\n**Parts**:")
        for p in body["parts"]:
            if isinstance(p, dict):
                lines.append(f"  - {p.get('name', '')}: Ch{p.get('start', '')}–Ch{p.get('end', '')}")
    return "\n".join(lines)


def _format_body_b(data: dict) -> str:
    body = data.get("body_b", {})
    lines = ["## Body B — Emergent 9-Chapter Self-Navigation\n"]
    chapters = body.get("chapters", [])
    for ch in chapters:
        if isinstance(ch, dict):
            lines.append(
                f"- **E{ch.get('depth', '?')}** [{ch.get('element', '')}]: "
                f"{ch.get('title', '')} — {ch.get('operation', '')}"
            )
        else:
            lines.append(f"- {ch}")
    return "\n".join(lines)


def _format_appendices(data: dict) -> str:
    lines = ["## Appendix Fields\n"]
    # Legacy
    legacy = data.get("appendices_legacy", [])
    lines.append("### Body A — Legacy (A→P)")
    for app in legacy:
        if isinstance(app, dict):
            lines.append(
                f"- **App{app.get('letter', '?')}** [{app.get('element', '')}]: "
                f"{app.get('role', '')}"
            )
        else:
            lines.append(f"- {app}")
    # Reverse
    reverse = data.get("appendices_reverse", [])
    if reverse:
        lines.append("\n### Body B — Reverse Emanation (Z→K)")
        for app in reverse:
            if isinstance(app, dict):
                lines.append(f"- **{app.get('letter', '?')}**: {app.get('operation', '')}")
            else:
                lines.append(f"- {app}")
    return "\n".join(lines)


def _format_metro(data: dict) -> str:
    metro = data.get("metro_map", {})
    lines = ["## Metro Map Topology\n"]
    if "master_topology" in metro:
        lines.append(f"**Master Topology**: {metro['master_topology']}")
    if "hub_types" in metro:
        lines.append("\n**Hub Types**:")
        for h in metro["hub_types"]:
            if isinstance(h, dict):
                lines.append(f"  - {h.get('name', '')}: {h.get('description', '')}")
    return "\n".join(lines)


def _format_bridge(data: dict) -> str:
    bridge = data.get("mobius_bridge", {})
    return (
        "## Möbius Bridge Hinges\n\n"
        f"**Hinge 1**: {bridge.get('hinge_1', 'AppQ — Consciousness Technology')}\n"
        f"**Hinge 2**: {bridge.get('hinge_2', 'AppO — Dark Energy Prediction')}\n"
        f"**Gluing**: {bridge.get('gluing', 'Body A ←→ Body B via orientation-reversing fold')}"
    )


def _format_theorems(data: dict) -> str:
    theorems = data.get("key_theorems", [])
    lines = ["## Key Mathematical Results\n"]
    for t in theorems:
        if isinstance(t, dict):
            lines.append(f"### {t.get('name', '?')}")
            lines.append(t.get("statement", ""))
            lines.append("")
        else:
            lines.append(f"- {t}")
    return "\n".join(lines)


def _format_conjectures(data: dict) -> str:
    conj = data.get("open_conjectures", [])
    lines = ["## 13 Open Conjectures (Frontier)\n"]
    for i, c in enumerate(conj, 1):
        if isinstance(c, dict):
            lines.append(f"{i}. **{c.get('name', '?')}**: {c.get('statement', '')}")
        else:
            lines.append(f"{i}. {c}")
    return "\n".join(lines)


def _format_scale(data: dict) -> str:
    scale = data.get("renormalization", {})
    return (
        "## Renormalization Flow\n\n"
        f"**Flow**: {scale.get('flow', '240 → 60 → 15 → 4 → 1')}\n"
        f"**Fixed Point**: {scale.get('fixed_point', 'ρ* = 1/e')}\n"
        f"**Entropy**: {scale.get('entropy', 'h(Ξ) = 0')}"
    )
