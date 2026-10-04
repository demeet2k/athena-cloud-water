# CRYSTAL: Xi108:W2:A11:S11 | face=C | node=63 | depth=2 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W2:A11:S10→Xi108:W2:A11:S12→Xi108:W1:A11:S11→Xi108:W3:A11:S11→Xi108:W2:A10:S11→Xi108:W2:A12:S11

"""3D-12D alternating atlas and containment logic."""

from ._cache import JsonCache

_dims = JsonCache("dimensional_ladder.json")

def resolve_dimensional_body(dimension: int) -> str:
    """
    Get the full body/field description for any dimension 3-12.

    Returns: body type (even/odd), name, description, lens emphasis,
    alchemy emphasis, completion view, transport stack, and crown pair (for odd fields).

    Dimensions: 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    """
    data = _dims.load()
    if "levels" in data and "dimensions" not in data:
        entry = next((d for d in data["levels"] if d["dimension"] == dimension), None)
        if entry is None:
            return f"Dimension {dimension} not found. Valid: {[d['dimension'] for d in data['levels']]}"
        lines = [f"## {entry['dimension']}D - {entry['name']}", entry['description']]
        if "gates" in entry:
            lines.append("Gates: " + ", ".join(entry["gates"]))
        lines.append("Sequence lock: " + data["sequence_lock"])
        return "\n".join(lines) + "\n"
    dim_entry = None
    for d in data["dimensions"]:
        if d["dimension"] == dimension:
            dim_entry = d
            break

    if not dim_entry:
        valid = [d["dimension"] for d in data["dimensions"]]
        return f"Dimension {dimension} not found. Valid: {valid}"

    lines = [
        f"## {dim_entry['dimension']}D — {dim_entry['name']}",
        f"**Symbol**: {dim_entry['symbol']}",
        f"**Body Type**: {dim_entry['body_type'].replace('_', ' ').title()}",
        f"\n{dim_entry['description']}\n",
        f"- **Lens Emphasis**: {dim_entry['lens_emphasis']}",
        f"- **Alchemy Emphasis**: {dim_entry['alchemy_emphasis']}",
        f"- **Animal Mask**: {dim_entry['animal_mask']}",
        f"- **Completion View**: {dim_entry['completion_view']}",
        f"- **Transport**: {', '.join(dim_entry['transport'])}",
    ]

    if "crown_pair" in dim_entry:
        cp = dim_entry["crown_pair"]
        lines.append(f"\n**Crown Pair**:")
        lines.append(f"- A+: {cp['A_plus']}")
        lines.append(f"- Z+: {cp['Z_plus']}")

    if "timing_wheel" in dim_entry:
        lines.append(f"\n**Timing Wheel**: {' → '.join(dim_entry['timing_wheel'])}")

    if "nine_views" in dim_entry:
        lines.append(f"\n**Nine Completion Views**:")
        for i, v in enumerate(dim_entry["nine_views"], 1):
            lines.append(f"  {i}. {v}")

    if "relay_layers" in dim_entry:
        lines.append(f"\n**Relay Layers**: {' ↔ '.join(dim_entry['relay_layers'])}")

    if dim_entry.get("is_crown"):
        lines.append(f"\n**Operational Axes**: {', '.join(dim_entry['operational_axes'])}")
        lines.append(f"\n**Canonical**: {dim_entry['canonical_one_line']}")

    return "\n".join(lines) + "\n"

def dimensional_lift(from_dim: int, to_dim: int) -> str:
    """
    Trace the odd/even integration chain between two dimensions.

    Shows each intermediate body/field and what becomes visible at each step.
    Example: dimensional_lift(4, 12) traces E4 -> O5 -> E6 -> O7 -> E8 -> O9 -> E10 -> O11 -> E12
    """
    data = _dims.load()
    if "levels" in data and "dimensions" not in data:
        low, high = sorted((from_dim, to_dim))
        levels = [d for d in data["levels"] if low <= d["dimension"] <= high]
        if not levels:
            return f"No dimensions found in range {low}-{high}."
        return "\n".join([
            f"## Dimensional Lift: {low}D -> {high}D",
            "Sequence lock: " + data["sequence_lock"],
            *[f"- {d['dimension']}D: {d['name']} - {d['description']}" for d in levels],
            "HOLD: v2 lists levels; it does not attest odd/even transport or containment edges.",
        ]) + "\n"

    if from_dim > to_dim:
        from_dim, to_dim = to_dim, from_dim

    dims_in_range = [
        d for d in data["dimensions"]
        if from_dim <= d["dimension"] <= to_dim
    ]

    if not dims_in_range:
        return f"No dimensions found in range {from_dim}-{to_dim}."

    lines = [f"## Dimensional Lift: {from_dim}D → {to_dim}D\n"]
    lines.append(f"**Law**: {data['meta']['law']}\n")

    for i, d in enumerate(dims_in_range):
        arrow = " → " if i < len(dims_in_range) - 1 else ""
        prefix = "↗" if d["body_type"] == "odd_field" else "■"
        lines.append(
            f"{prefix} **{d['dimension']}D** ({d['symbol']}): "
            f"{d['name']}"
        )
        lines.append(f"  Transport: {', '.join(d['transport'])}")
        if "crown_pair" in d:
            lines.append(f"  A+: {d['crown_pair']['A_plus']}")
        if arrow:
            lines.append(f"  {'│':>4}")

    return "\n".join(lines) + "\n"

def query_containment(shell_or_dimension: int) -> str:
    """
    Get the weave containment chain.

    If given a dimension (3-12), shows how many sub-bodies nest inside.
    Shows the full B_12 = W_9(B_10) = ... expansion.
    """
    data = _dims.load()
    if "containment_chain" not in data:
        return "HOLD: containment_chain is absent from the current dimensional registry.\n"
    chain = data["containment_chain"]

    lines = [
        "## Weave Containment Law\n",
        f"**Law**: {chain['law']}\n",
        "### Chain:",
    ]
    for link in chain["links"]:
        lines.append(
            f"- {link['body']} = {link['weave']}({link['contains']}) "
            f"→ {link['sub_body_count']} sub-bodies at {link['dimension']}D"
        )

    lines.append("\n### Expanded from 12D:")
    for body, count in chain["expanded_from_12d"].items():
        lines.append(f"- {count} × {body}")

    lines.append(
        "\n**One 12D crown body resolves to**: "
        "9 B_10, 63 B_8, 315 B_6, 945 B_4, 1890 B_3"
    )

    return "\n".join(lines) + "\n"
