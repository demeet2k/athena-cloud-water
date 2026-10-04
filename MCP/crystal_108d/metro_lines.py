# CRYSTAL: Xi108:W2:A8:S14 | face=R | node=99 | depth=2 | phase=Cardinal
# METRO: Me
# BRIDGES: Xi108:W2:A8:S13→Xi108:W2:A8:S15→Xi108:W1:A8:S14→Xi108:W3:A8:S14→Xi108:W2:A7:S14→Xi108:W2:A9:S14

"""Major metro lines navigation."""

from ._cache import JsonCache

_metro = JsonCache("metro_lines.json")

def _query_metro_line(line_type: str, index: int = 0) -> str:
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
    if not isinstance(data, dict):
        return 'HOLD: metro registry root must be an object.'
    if "lines" in data and any(key in data for key in ("shell_ascent", "wreath_lines", "archetype_columns", "qo_pillars", "arcs")):
        return 'HOLD: conflicting legacy and declared metro schemas.'
    if "lines" in data:
        return _query_declared_lines(data, lt, index, line_type)

    if not any(key in data for key in ('shell_ascent', 'wreath_lines', 'archetype_columns', 'qo_pillars', 'arcs')):
        return 'HOLD: metro source schema is absent.'

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


def _query_declared_lines(data, lt, index, line_type):
    meta, declared = data.get('meta'), data['lines']
    if (not isinstance(meta, dict) or meta.get('type') != 'metro_lines'
            or not isinstance(meta.get('version'), str) or not meta['version'].strip()
            or type(meta.get('total_lines')) is not int
            or not isinstance(declared, list) or not declared
            or meta['total_lines'] != len(declared)):
        return 'HOLD: metro registry metadata or declared line census is missing or conflicting.'
    aliases = {}
    wreath_ids = set()
    for number, line in enumerate(declared):
        if (not isinstance(line, dict)
                or any(not isinstance(line.get(key), str) or not line[key].strip()
                       for key in ('id', 'code', 'name', 'type', 'description'))
                or not isinstance(line.get('stations'), list) or not line['stations']
                or any(type(station) is not int or station < 1 for station in line['stations'])):
            return 'HOLD: metro line record is missing or malformed.'
        for token in {line[key].strip().lower() for key in ('id', 'code', 'name')}:
            if token in ('all', 'overview', 'wreath'):
                return f'HOLD: metro source identifier {token!r} conflicts with a reserved selector.'
            if token in aliases and aliases[token] != number:
                return f"HOLD: ambiguous metro source identifier '{token}'."
            aliases[token] = number
        if line['type'] == 'wreath':
            identity = line.get('wreath')
            if type(identity) is not int or identity < 1 or identity in wreath_ids:
                return 'HOLD: missing or conflicting declared wreath identities.'
            wreath_ids.add(identity)
    if lt == 'wreath':
        wreath_lines = [line for line in declared if line['type'] == 'wreath']
        if index >= len(wreath_lines):
            return f'HOLD: Wreath index must be 0-{len(wreath_lines) - 1} in declared source order.'
        selected = [wreath_lines[index]]
    else:
        if index != 0:
            return f'HOLD: {line_type.strip().title()} index {index} is unsupported; a source line ID, code, name or overview requires index 0. No indexed route is inferred.'
        if lt in ('all', 'overview'):
            selected = declared
        elif lt in aliases:
            selected = [declared[aliases[lt]]]
        elif lt in ('shell_ascent', 'archetype_column', 'archetype', 'column', 'qo_pillar', 'pillar', 'mobius', 'arc'):
            return (f'HOLD: {line_type.title()} legacy mapping is absent from the current metro registry.\n'
                    'Query a declared line ID or code; no legacy route is inferred.\n')
        else:
            return f"HOLD: Unknown metro line '{line_type}'. Available IDs: " + ', '.join(line['id'] for line in declared)
    return '## Metro Lines\n\n' + '\n\n'.join(
        f"### {line['id']}: {line['name']}\n"
        f"Type: {line['type']}\nStations: {line['stations']}\n{line['description']}"
        for line in selected
    ) + '\nHOLD: station membership alone does not verify route legality or source identity consistency.\n'


def query_metro_line(line_type: str, index: int = 0) -> str:
    """Read one unambiguous declared source route, or preserve valid legacy reads."""
    if not isinstance(line_type, str) or not line_type.strip():
        return 'HOLD: metro line selector must be a nonempty string.'
    if type(index) is not int or index < 0:
        return 'HOLD: metro index must be a nonnegative integer (bool is not an index).'
    lt = line_type.strip().lower()
    if lt in ('all', 'overview', 'shell_ascent', 'qo_pillar', 'pillar', 'mobius') and index != 0:
        return f'HOLD: {line_type.strip().title()} index {index} is unsupported; this metro selector requires index 0.'
    try:
        return _query_metro_line(line_type, index)
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        return f'HOLD: metro source is missing, malformed or conflicting ({exc}).'
