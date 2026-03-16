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
    # Full format
    m = re.match(
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
    m = re.match(r"Xi108:(Su|Me|Sa):(\d+):(\d+)", address)
    if m:
        return {
            "superphase": m.group(1),
            "archetype": int(m.group(2)),
            "shell": int(m.group(3)),
        }

    # Minimal: Xi108:S{shell}
    m = re.match(r"Xi108:S(\d+)", address)
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
        if "archetype" in parsed:
            archetype = str(parsed["archetype"])
        if "superphase" in parsed:
            wreath = parsed["superphase"]

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
