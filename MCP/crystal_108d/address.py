# CRYSTAL: Xi108:W1:A8:S2 | face=R | node=3 | depth=0 | phase=Fixed
# METRO: □
# BRIDGES: Xi108:W1:A8:S1→Xi108:W1:A8:S3→Xi108:W2:A8:S2→Xi108:W1:A7:S2→Xi108:W1:A9:S2

"""Extended 108D address grammar parser."""

import re

from ._cache import JsonCache

_shells = JsonCache("shell_registry.json")
_dims = JsonCache("dimensional_ladder.json")

def parse_108d_address(address: str) -> dict | None:
    """
    Parse extended 108D address format:
    Xi108:W{r}:A{a}:S{l}:u{u}:sigma{s}:lambda{lam}:pi{p}:iota{i}

    Also accepts shorthand like: Xi108:Su:1:5 (wreath:archetype:shell)
    """
    # Source-listed face address: Xi108:W2:A2:S5:S.
    m = re.fullmatch(r"Xi108:W(\d+):A(\d+):S(\d+):([SFCR])", address)
    if m:
        return {"wreath": int(m.group(1)), "archetype": int(m.group(2)),
                "shell": int(m.group(3)), "face": m.group(4)}

    # Full format
    m = re.fullmatch(
        r"Xi108:W(\d+):A(\d+):S(\d+):u(\d+):"
        r"(Su|Me|Sa):(L\d+|L\d{2,3}):(Q|O|Z|E10|AP|KZ|Core):([\w-]+)",
        address
    )
    if m:
        return {
            "wreath": int(m.group(1)),
            "archetype": int(m.group(2)),
            "shell": int(m.group(3)),
            "unit": int(m.group(4)),
            "superphase": m.group(5),
            "live_lock": m.group(6),
            "portal": m.group(7),
            "instance": m.group(8),
        }

    # Shorthand: Xi108:Su:3:15
    m = re.fullmatch(r"Xi108:(Su|Me|Sa):(\d+):(\d+)", address)
    if m:
        return {
            "superphase": m.group(1),
            "archetype": int(m.group(2)),
            "shell": int(m.group(3)),
        }

    # Minimal: Xi108:S{shell}
    m = re.fullmatch(r"Xi108:S(\d+)", address)
    if m:
        return {"shell": int(m.group(1))}

    return None

def navigate_108d(
    shell: int = 0,
    archetype: str = "",
    wreath: str = "",
    dimension: int = 0,
    face: str = "",
    address: str = ""
) -> str:
    """
    Navigate the full 108D address space.

    Can query by:
    - shell number (1-36)
    - archetype name or index (1-12)
    - wreath/superphase (Su/Me/Sa or sulfur/mercury/salt)
    - dimension (3-108)
    - face/lens (S/F/C/R)
    - full 108D address string (Xi108:W1:A1:S1:u1:Su:L3:Q:seed)

    Returns the resolved location with all metadata.
    """
    shells_data = _shells.load()
    dims_data = _dims.load()

    parsed = {}

    # If address string provided, parse it
    if address:
        parsed = parse_108d_address(address)
        if not parsed:
            return (
                f"Could not parse 108D address '{address}'.\n"
                "Formats:\n"
                "  Xi108:W1:A1:S1:u1:Su:L3:Q:seed (full)\n"
                "  Xi108:Su:3:15 (shorthand: wreath:archetype:shell)\n"
                "  Xi108:S5 (minimal: shell only)"
            )
        shell = parsed.get("shell", shell)
        face = parsed.get("face", face)
        if "archetype" in parsed:
            archetype = str(parsed["archetype"])
        if "superphase" in parsed:
            wreath = parsed["superphase"]

    if isinstance(shells_data["shells"], dict):
        return _navigate_v2(shells_data, dims_data, shell, archetype, wreath, dimension, face, parsed)

    lines = ["## 108D Navigation Result\n"]

    # Resolve by shell
    if shell > 0:
        if shell < 1 or shell > 36:
            return f"Shell {shell} out of range (1-36)."
        s = shells_data["shells"][shell - 1]
        lines.append(f"### Shell {s['number']} — {s['archetype_name']}")
        lines.append(f"- Nodes: {s['nodes']} (cumulative: {s['cumulative']}/666)")
        lines.append(f"- Wreath: {s['wreath']}")
        lines.append(f"- Archetype: #{s['archetype_index']} ({s['archetype_name']})")
        lines.append(f"- Mirror: S{s['mirror']}")
        lines.append(f"- Dimension: {s['dimension_first']}D")
        lines.append(f"- Action: {s['action']}")

    # Resolve by archetype
    elif archetype:
        arch_lower = archetype.lower()
        matched = []
        if arch_lower.isdigit():
            idx = int(arch_lower)
            matched = [s for s in shells_data["shells"] if s["archetype_index"] == idx]
        else:
            matched = [s for s in shells_data["shells"]
                       if arch_lower in s["archetype_name"].lower()]
        if not matched:
            return f"Archetype '{archetype}' not found."
        name = matched[0]["archetype_name"]
        lines.append(f"### Archetype: {name}")
        for s in matched:
            lines.append(f"- S{s['number']} ({s['wreath']}): {s['nodes']} nodes, {s['dimension_first']}D")

    # Resolve by wreath
    elif wreath:
        w_lower = wreath.lower()
        for key, val in shells_data["wreaths"].items():
            if w_lower in (key, val["code"].lower()):
                lines.append(f"### Wreath: {key.title()} ({val['code']})")
                lines.append(f"- Shells: {val['shells']}")
                lines.append(f"- Nodes: {val['node_count']}")
                lines.append(f"- Function: {val['function']}")
                break
        else:
            return f"Wreath '{wreath}' not found. Use: sulfur/Su, mercury/Me, salt/Sa"

    # Resolve by dimension
    elif dimension > 0:
        for d in dims_data["dimensions"]:
            if d["dimension"] == dimension:
                lines.append(f"### {d['dimension']}D — {d['name']} ({d['symbol']})")
                lines.append(f"- Type: {d['body_type']}")
                lines.append(f"- Transport: {', '.join(d['transport'])}")
                lines.append(f"- Lens: {d['lens_emphasis']}")
                break
        else:
            return f"Dimension {dimension} not in 3-12 atlas."

    else:
        return (
            "Provide at least one parameter:\n"
            "- shell (1-36)\n"
            "- archetype (name or 1-12)\n"
            "- wreath (Su/Me/Sa)\n"
            "- dimension (3-12)\n"
            "- address (Xi108:...)"
        )

    return "\n".join(lines) + "\n"


def _navigate_v2(shells_data, dims_data, shell, archetype, wreath, dimension, face, parsed):
    """Read actual v2 records without inventing v1 node/dimension metadata."""
    records = list(shells_data["shells"].values())
    if dimension > 0 and (shell or archetype or wreath or face):
        return "HOLD: current registries do not map shell/archetype/wreath/face selectors to dimensions."

    if face and face not in shells_data["meta"]["faces"]:
        return f"INVALID face {face!r}. Valid: {shells_data['meta']['faces']}"
    if shell != 0:
        entry = shells_data["shells"].get(str(shell))
        if entry is None:
            return f"Shell {shell} out of range or absent from source registry."
        if parsed.get("wreath", entry["wreath_index"]) != entry["wreath_index"]:
            return "INVALID: address wreath conflicts with the source shell record."
        if archetype and archetype.lower() not in (str(entry["archetype_index"]), entry["archetype"].lower()):
            return "INVALID: address archetype conflicts with the source shell record."
        if wreath and wreath.lower() != entry["wreath"].lower():
            return "INVALID: address superphase conflicts with the source shell record."
        selected = [entry]
    elif archetype:
        selected = [entry for entry in records
                    if archetype.lower() in (str(entry["archetype_index"]), entry["archetype"].lower())]
    elif wreath:
        selected = [entry for entry in records if wreath.lower() == entry["wreath"].lower()]
    elif dimension > 0:
        from .dimensions import resolve_dimensional_body
        return resolve_dimensional_body(dimension)
    else:
        return "Provide a shell, archetype, wreath, dimension or source-listed address."
    if wreath:
        selected = [entry for entry in selected if wreath.lower() == entry["wreath"].lower()]
    if not selected:
        return "No source shell records match the requested archetype or wreath."
    lines = ["## 108D Navigation Result"]
    for entry in selected:
        lines.extend([f"### Shell {entry['shell_id']} - {entry['archetype']}",
                      f"Wreath: {entry['wreath']}", f"Archetype: #{entry['archetype_index']}",
                      f"Mirror: S{entry['mirror_shell']}", f"Neighbors: {entry['neighbors']}"])
        for code, location in entry["faces"].items():
            if not face or code == face:
                lines.append(f"Face {code}: {location['address']} (gate {location['gate']})")
    if any(key in parsed for key in ("unit", "live_lock", "portal", "instance")):
        lines.append("HOLD: source shell registry does not attest unit/live-lock/portal/instance mappings.")
    return "\n".join(lines) + "\n"
