"""
Stage Code Table — Ω Lookup Appendix A0.
Stage ladder from S3 seed through S12 crown to Ω and A+ absolute.

Source: MOBIUS LENSES.docx / Ω LOOKUP APPENDIX A0
"""

from ._cache import JsonCache

_stages = JsonCache("stage_codes.json")


def query_stage_code(code: str = "all") -> str:
    """Query a stage code (S3, S4, S4M, S5Σ, S6M, S8, S12, Ω, A+, etc.) or 'all' for the full ladder.
    Also: 'zeros' for zero families, 'hubs' for hub lattice, 'sigma60' for metro packet."""
    d = _stages.load()
    code = code.strip()

    # Special queries
    if code.lower() in ("zeros", "zero", "z"):
        zf = d["zero_families"]
        lines = ["## Zero Families\n"]
        for k, v in zf.items():
            lines.append(f"**{v['notation']}** ({v['name']}): scope={v['scope']}, {v['function']}")
        return "\n".join(lines)

    if code.lower() in ("hubs", "hub"):
        hl = d["hub_lattice"]
        lines = [f"## {hl['name']}\n"]
        for h in hl["hubs"]:
            label = h.get("zero", h.get("hub", ""))
            lines.append(f"  {h['position']:>5}  {label:>6}  {h['function']}")
        return "\n".join(lines)

    if code.lower() in ("sigma60", "sigma", "metro", "packet"):
        sm = d["sigma_60_metro"]
        lines = [f"## {sm['name']}\n"]
        lines.append(f"**Structure**: {sm['structure']}")
        lines.append(f"**Quadrants**: {', '.join(sm['quadrants'])}")
        lines.append(f"**Lens Masks**: {sm['lens_masks']}")
        lines.append(f"**Total States**: {sm['total_states']}")
        lines.append("\n### Four Odd Fields")
        for dim, desc in sm["four_odd_fields"].items():
            lines.append(f"  **{dim}**: {desc}")
        return "\n".join(lines)

    if code.lower() == "all":
        m = d["meta"]
        lines = ["## Stage Code Ladder\n"]
        lines.append(f"**Ladder**: `{m['ladder']}`")
        lines.append(f"**Liminal Coordinate**: `{m['liminal_coordinate']}`\n")
        for s in d["stages"]:
            dim_str = f"{s['dimension']}D" if s["dimension"] else "∞"
            lines.append(f"  **{s['code']:>5}** [{dim_str:>4}] {s['body_type']:>20}  {s['description']}")
        return "\n".join(lines)

    # Match specific code
    code_upper = code.upper().replace("OMEGA", "Ω").replace("APLUS", "A+")
    for s in d["stages"]:
        if s["code"].upper() == code_upper or s["code"] == code:
            lines = [f"## Stage {s['code']} — {s['object']}\n"]
            dim_str = f"{s['dimension']}D" if s['dimension'] else "Beyond-dimensional"
            lines.append(f"**Dimension**: {dim_str}")
            lines.append(f"**Body Type**: {s['body_type']}")
            lines.append(f"**Description**: {s['description']}")
            lines.append(f"**Carrier**: {s['carrier']}")
            return "\n".join(lines)

    return f"Stage code '{code}' not found. Available: {', '.join(s['code'] for s in d['stages'])}. Also: all, zeros, hubs, sigma60."
