# CRYSTAL: Xi108:W2:A8:S14 | face=R | node=99 | depth=2 | phase=Cardinal
# METRO: Me
# BRIDGES: Xi108:W2:A8:S13→Xi108:W2:A8:S15→Xi108:W1:A8:S14→Xi108:W3:A8:S14→Xi108:W2:A7:S14→Xi108:W2:A9:S14

"""Major metro lines navigation."""

from ._cache import JsonCache

_metro = JsonCache("metro_lines.json")

def query_metro_line(line_type: str, index: int = 0) -> str:
    """
    Navigate metro lines of the 108D organism.

    Line types:
      - 'shell_ascent': The 36-station vertical ascent
      - 'wreath' + index 0-2: Sulfur(0), Mercury(1), Salt(2) rails
      - 'archetype_column' + index 1-12: Archetype vertical columns
      - 'qo_pillar': Q and O Mobius pillars
      - 'arc' + index 0-6: The 7 arcs with chapter/lane mappings
      - 'all': Overview of all line types

    Example: query_metro_line("archetype_column", 7) for the Change/Arc Heptad column
    """
    data = _metro.load()
    lt = line_type.lower().strip()
    if "lines" in data and "shell_ascent" not in data:
        declared = data["lines"]
        if lt in ("all", "overview"):
            selected = declared
        elif lt == "wreath":
            wreath_lines = [line for line in declared if line["type"] == "wreath"]
            if not 0 <= index < len(wreath_lines):
                return f"Wreath index must be 0-{len(wreath_lines) - 1}."
            selected = [wreath_lines[index]]
        elif lt in ("shell_ascent", "archetype_column", "archetype", "column", "qo_pillar", "pillar", "mobius", "arc"):
            # A named Mobius line exists, but the old Q/O pillar pair does not.
            # Prefer the actual line ID only when it names a source record.
            selected = [line for line in declared if line["id"].lower() == lt]
            if not selected:
                return (f"HOLD: {line_type.title()} legacy mapping is absent from the current metro registry.\n"
                        "Query a declared line ID or code; no legacy route is inferred.\n")
        else:
            selected = [line for line in declared
                        if lt in (line["id"].lower(), line.get("code", "").lower(), line["name"].lower())]
            if not selected:
                return f"Unknown metro line '{line_type}'. Available IDs: " + ", ".join(line["id"] for line in declared)
        return "## Metro Lines\n\n" + "\n\n".join(
            f"### {line['id']}: {line['name']}\n"
            f"Type: {line['type']}\nStations: {line['stations']}\n{line['description']}"
            for line in selected
        ) + "\nHOLD: station membership alone does not verify route legality or source identity consistency.\n"

    if lt == "all" or lt == "overview":
        lines = ["## Metro Line Overview\n"]
        lines.append(f"- Shell Ascent: {data['shell_ascent']['stations']} stations")
        lines.append(f"- Wreath Lines: {len(data['wreath_lines'])}")
        lines.append(f"- Archetype Columns: {len(data['archetype_columns'])}")
        lines.append(f"- Q/O Pillars: 2 (spanning all 36 shells)")
        lines.append(f"- Arcs: {len(data['arcs'])}")
        lines.append(f"\nAll converge at Z*.")
        return "\n".join(lines)

    if lt == "shell_ascent":
        sa = data["shell_ascent"]
        return (
            f"## Shell Ascent Line\n\n"
            f"- **Stations**: {sa['stations']}\n"
            f"- **Law**: {sa['law']}\n"
            f"- **Direction**: {sa['direction']}\n"
            f"- **Return**: {sa['return']}\n"
        )

    if lt == "wreath":
        if index < 0 or index >= len(data["wreath_lines"]):
            return f"Wreath index must be 0-{len(data['wreath_lines'])-1}."
        w = data["wreath_lines"][index]
        return (
            f"## Wreath Line: {w['name']} ({w['code']})\n\n"
            f"- **Superphase**: {w['superphase']}\n"
            f"- **Shells**: {w['shells']}\n"
            f"- **Function**: {w['function']}\n"
            f"- **Chapter Mapping**: {', '.join(w['chapter_mapping'])}\n"
        )

    if lt in ("archetype_column", "archetype", "column"):
        if index < 1 or index > 12:
            return "Archetype column index must be 1-12."
        col = data["archetype_columns"][index - 1]
        return (
            f"## Archetype Column #{col['index']}: {col['name']}\n\n"
            f"- **Shells**: {col['shells']} (one per wreath)\n"
            f"- **Function**: {col['function']}\n"
            f"- **Vertical continuity**: Same archetype identity across Su/Me/Sa\n"
        )

    if lt in ("qo_pillar", "pillar", "mobius"):
        qo = data["qo_pillars"]
        q = qo["Q_pillar"]
        o = qo["O_pillar"]
        return (
            f"## Q/O Mobius Pillars\n\n"
            f"### {q['name']}\n"
            f"- {q['function']}\n"
            f"- Spans: {q['spans']}\n\n"
            f"### {o['name']}\n"
            f"- {o['function']}\n"
            f"- Spans: {o['spans']}\n\n"
            f"**Mobius Law**: {qo['mobius_law']}\n"
        )

    if lt == "arc":
        if index < 0 or index >= len(data["arcs"]):
            return f"Arc index must be 0-{len(data['arcs'])-1}."
        arc = data["arcs"][index]
        return (
            f"## Arc α={arc['alpha']} (ρ={arc['rho']})\n\n"
            f"- **Chapters**: {', '.join(arc['chapters'])}\n"
            f"- **Lanes**: {', '.join(arc['lanes'])}\n"
        )

    return (
        f"Unknown line type '{line_type}'. Use:\n"
        "  shell_ascent, wreath (0-2), archetype_column (1-12), "
        "qo_pillar, arc (0-6), all"
    )
