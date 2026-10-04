# CRYSTAL: Xi108:W1:A9:S9 | face=S | node=45 | depth=0 | phase=Fixed
# METRO: T
# BRIDGES: Xi108:W1:A9:S8→Xi108:W1:A9:S10→Xi108:W2:A9:S9→Xi108:W1:A8:S9→Xi108:W1:A10:S9

"""
Stage Code Table — Ω Lookup Appendix A0.
Stage ladder from S3 seed through S12 crown to Ω and A+ absolute.

Source: MOBIUS LENSES.docx / Ω LOOKUP APPENDIX A0
"""

from ._cache import JsonCache

_stages = JsonCache("stage_codes.json")


def _query_v2_stage(data, code):
    try:
        stages = data['stages']
        if not isinstance(stages, dict) or set(stages) != {'A', 'B', 'C', 'D', 'FINAL'}:
            raise ValueError('source stage identities are missing or undeclared')
        for stage in stages.values():
            if (type(stage['waves']) is not int or stage['waves'] < 1
                    or not all(isinstance(stage[k], str) and stage[k].strip() for k in ('description', 'focus'))):
                raise ValueError('stage record is incomplete')
        total, cycles, meta_total = (data[k] for k in ('total_per_cycle', 'meta_loop_cycles', 'total_per_meta_loop'))
        if any(type(n) is not int or n < 1 for n in (total, cycles, meta_total)):
            raise ValueError('source cycle totals must be positive integers')
        if code.upper() not in stages and code.lower() != 'all':
            return f"HOLD: v2 has no source mapping for '{code}'. Declared Stage codes: {', '.join(stages)}; legacy dimension codes, zero families, hub lattice and sigma60 are absent."
        selected = stages.items() if code.lower() == 'all' else [(code.upper(), stages[code.upper()])]
        lines = ['## Source Stage Codes']
        for key, stage in selected:
            lines += [f"### Stage {key}", f"- **Waves**: {stage['waves']}",
                      f"- **Description**: {stage['description']}", f"- **Focus**: {stage['focus']}"]
        base_sum = sum(stage['waves'] for key, stage in stages.items() if key != 'FINAL')
        full_sum = base_sum + stages['FINAL']['waves']
        lines += [f'**Declared Total per Cycle**: {total}', f'**Declared Meta-loop Cycles**: {cycles}',
                  f'**Declared Total per Meta-loop**: {meta_total}',
                  f'**Record Sums**: A+B+C+D = {base_sum}; including FINAL = {full_sum}.']
        if total != full_sum or meta_total != total * cycles:
            lines.append('HOLD: source totals do not establish whether FINAL is included in cycle accounting; no execution schedule is certified.')
        return '\n'.join(lines) + '\n'
    except (KeyError, TypeError, ValueError) as exc:
        return f'HOLD: stage registry has missing or conflicting source fields ({exc}).'


def query_stage_code(code: str = "all", source: str = "current") -> str:
    """Read v2 A/B/C/D/FINAL source stages or all; unsupported legacy selectors HOLD.
    For a valid legacy registry, query a stage code (S3, S4, S4M, S5Σ, S6M, S8, S12, Ω, A+, etc.) or 'all' for the full ladder.
    Also: 'zeros' for zero families, 'hubs' for hub lattice, 'sigma60' for metro packet.

    Source: current (default), or explicit archive for pinned historical
    descriptions and clock MODEL only. Archive results never certify runtime.
    """
    if source == "archive":
        from .core_archive import render_core_archive
        return render_core_archive("stage_codes.json", lambda data: _render_query_stage_code(data, code), code)
    if source != "current":
        return "HOLD: source must be current or explicit archive."
    try:
        d = _stages.load()
    except (OSError, ValueError, TypeError) as exc:
        return f'HOLD: stage source is unavailable or unreadable ({exc}).'
    return _render_query_stage_code(d, code)


def _render_query_stage_code(d: dict, code: str = "all") -> str:
    """Read v2 A/B/C/D/FINAL source stages or all; unsupported legacy selectors HOLD.
    For a valid legacy registry, query a stage code (S3, S4, S4M, S5Σ, S6M, S8, S12, Ω, A+, etc.) or 'all' for the full ladder.
    Also: 'zeros' for zero families, 'hubs' for hub lattice, 'sigma60' for metro packet."""
    if not isinstance(d, dict) or not isinstance(d.get('meta'), dict):
        return 'HOLD: stage source requires a registry object and metadata object.'
    if not isinstance(code, str) or not code.strip():
        return 'Invalid stage code: expected nonempty text.'
    code = code.strip()
    if d.get('meta', {}).get('version') == '2.0' or isinstance(d.get('stages'), dict):
        return _query_v2_stage(d, code)

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
