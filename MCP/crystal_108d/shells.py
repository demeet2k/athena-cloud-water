# CRYSTAL: Xi108:W1:A10:S5 | face=C | node=12 | depth=0 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W1:A10:S4→Xi108:W1:A10:S6→Xi108:W2:A10:S5→Xi108:W1:A9:S5→Xi108:W1:A11:S5

"""36-shell mega-cascade logic and shell queries."""

from ._cache import JsonCache
from .constants import SUPERPHASE_NAMES

_shells = JsonCache("shell_registry.json")
_hologram = JsonCache("hologram_chapters.json")


def _index(value, limit):
    """Accept integers and decimal integer strings, without lossy coercion."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    if isinstance(value, str):
        value = value.strip()
        if (not value.isascii() or not value.isdecimal()
                or len(value.lstrip("0")) > len(str(limit))):
            return None
        value = int(value.lstrip("0") or "0")
    return value if 1 <= value <= limit else None


def _validated_v2(data):
    """Check declared identities and catalog membership before reporting them."""
    shells, archetypes, wreaths = data['shells'], data['archetypes'], data['wreaths']
    if not all(isinstance(catalog, dict) for catalog in (shells, archetypes, wreaths)):
        raise ValueError('v2 shell catalogs must be dictionaries')
    for key, shell in shells.items():
        number = _index(key, 36)
        if number is None or type(shell['shell_id']) is not int or shell['shell_id'] != number:
            raise ValueError('shell key and identity conflict')
        if (type(shell['archetype_index']) is not int or type(shell['wreath_index']) is not int
                or type(shell['mirror_shell']) is not int
                or not isinstance(shell['neighbors'], list)
                or any(type(n) is not int for n in shell['neighbors'])):
            raise ValueError('shell indices must be integers')
        a = archetypes[str(shell['archetype_index'])]
        w = wreaths[str(shell['wreath_index'])]
        if (shell['archetype'] != a['name'] or shell['wreath'] != w['name']
                or shell['phase'] != a['phase'] or shell['element_primary'] != a['element']):
            raise ValueError('shell and catalog fields conflict')
        if str(shell['mirror_shell']) not in shells or any(str(n) not in shells for n in shell['neighbors']):
            raise ValueError('shell reference is missing')
        if (not isinstance(shell['faces'], dict)
                or any(not isinstance(record, dict) for record in shell['faces'].values())):
            raise ValueError('shell faces and face records must be dictionaries')
        if set(shell['faces']) != set(data['meta']['faces']):
            raise ValueError('declared faces conflict')
        for face, record in shell['faces'].items():
            expected = f"Xi108:W{shell['wreath_index']}:A{shell['archetype_index']}:S{number}:{face}"
            if record['address'] != expected or not isinstance(record['gate'], str):
                raise ValueError('face address and shell identity conflict')
    for catalog, field, count in ((archetypes, 'archetype_index', 12), (wreaths, 'wreath_index', 3)):
        if set(catalog) != {str(i) for i in range(1, count + 1)}:
            raise ValueError('catalog identities are missing or undeclared')
        for key, record in catalog.items():
            members = record['shells']
            actual = [v['shell_id'] for v in shells.values() if v[field] == int(key)]
            if (not isinstance(members, list) or any(type(n) is not int for n in members)
                    or len(set(members)) != len(members) or set(members) != set(actual)):
                raise ValueError('catalog shell membership conflicts')
    if set(shells) != {str(i) for i in range(1, 37)}:
        raise ValueError('shell identities are missing or undeclared')
    return shells, archetypes, wreaths


def _v2_report(data, kind, selector):
    try:
        shells, archetypes, wreaths = _validated_v2(data)
        if kind == 'shell':
            s = shells[str(selector)]
            w = wreaths[str(s['wreath_index'])]
            lines = [f"## Shell {s['shell_id']} - {s['archetype']}",
                     f"- **Archetype**: #{s['archetype_index']} - {s['archetype']}",
                     f"- **Wreath**: {s['wreath']} ({w['quality']})",
                     f"- **Phase**: {s['phase']}", f"- **Primary Element**: {s['element_primary']}",
                     f"- **Mirror Shell**: S{s['mirror_shell']}", f"- **Neighbors**: {s['neighbors']}"]
            lines += [f"- **Face {face}**: {r['address']} (gate {r['gate']})" for face, r in s['faces'].items()]
        elif kind == 'archetype':
            a = archetypes[str(selector)]
            lines = [f"## Archetype #{selector} - {a['name']}",
                     f"- **Phase**: {a['phase']}", f"- **Element**: {a['element']}",
                     f"Appears in {len(a['shells'])} source-declared shells:"]
            lines += [f"- **S{n}**: {shells[str(n)]['wreath']}, mirror S{shells[str(n)]['mirror_shell']}" for n in a['shells']]
        else:
            matches = [w for w in wreaths.values() if selector in (w['name'].lower(), SUPERPHASE_NAMES.get(w['name'], '').lower())]
            if len(matches) != 1:
                return f"Unknown superphase '{selector}'. Use: sulfur/Su, mercury/Me, salt/Sa"
            w = matches[0]
            lines = [f"## Superphase: {SUPERPHASE_NAMES.get(w['name'], w['name'])} ({w['name']})",
                     f"- **Quality**: {w['quality']}", f"- **Shells**: {w['shells']}"]
            lines += [f"- S{n}: {shells[str(n)]['archetype']}" for n in w['shells']]
        return '\n'.join(lines) + '\n\nHOLD: v2 does not declare legacy node counts, cumulative counts, dimension visibility or action laws.\n'
    except (KeyError, TypeError, ValueError) as exc:
        return f"HOLD: shell registry has missing or conflicting source fields ({exc})."


def query_shell(shell_number: int) -> str:
    """
    Query a specific shell (1-36) in the 108D mega-cascade.

    Returns: archetype, wreath, superphase, node count, mirror shell,
    dimension first visible, and action description.
    """
    data = _shells.load()
    parsed = _index(shell_number, 36)
    if parsed is None:
        return f"Invalid shell {shell_number}. Must be 1-36."

    shell_number = parsed
    if (data.get("meta", {}).get("version") == "2.0"
            or isinstance(data.get("shells"), dict)):
        return _v2_report(data, "shell", shell_number)

    shell = data["shells"][shell_number - 1]
    wreath_info = None
    for w_name, w_data in data["wreaths"].items():
        if shell["wreath"] == w_data["code"]:
            wreath_info = w_data
            break

    wreath_desc = f"{wreath_info['code']} ({wreath_info['function']})" if wreath_info else shell["wreath"]

    return (
        f"## Shell {shell['number']} — {shell['archetype_name']}\n\n"
        f"- **Nodes**: {shell['nodes']} (cumulative: {shell['cumulative']}/666)\n"
        f"- **Wreath**: {wreath_desc}\n"
        f"- **Archetype**: #{shell['archetype_index']} — {shell['archetype_name']}\n"
        f"- **Mirror Shell**: S{shell['mirror']}\n"
        f"- **Dimension First Visible**: {shell['dimension_first']}D\n"
        f"- **Action**: {shell['action']}\n"
    )

def query_superphase(tag: str) -> str:
    """
    Query a superphase/wreath current: 'sulfur' (or 'Su'), 'mercury' (or 'Me'), 'salt' (or 'Sa').

    Returns: shell range, node count, function, archetype list.
    """
    data = _shells.load()
    if not isinstance(tag, str) or not tag.strip():
        return "Invalid superphase. Use: sulfur/Su, mercury/Me, salt/Sa"
    tag_lower = tag.strip().lower()
    if (data.get("meta", {}).get("version") == "2.0"
            or isinstance(data.get("shells"), dict)):
        return _v2_report(data, "wreath", tag_lower)

    # Normalize tag
    wreath_key = None
    for key, val in data["wreaths"].items():
        if tag_lower in (key, val["code"].lower()):
            wreath_key = key
            break

    if not wreath_key:
        return (
            f"Unknown superphase '{tag}'. "
            "Use: sulfur/Su, mercury/Me, salt/Sa"
        )

    w = data["wreaths"][wreath_key]
    shells_in_wreath = [s for s in data["shells"] if s["wreath"] == w["code"]]
    archetypes = [s["archetype_name"] for s in shells_in_wreath]

    return (
        f"## Superphase: {wreath_key.title()} ({w['code']})\n\n"
        f"- **Shells**: {w['shells'][0]}-{w['shells'][-1]}\n"
        f"- **Node Count**: {w['node_count']}\n"
        f"- **Function**: {w['function']}\n"
        f"- **Phase**: {w['superphase']}\n"
        f"- **Archetypes in Order**:\n"
        + "\n".join(f"  {i+1}. S{s['number']}: {s['archetype_name']}"
                    for i, s in enumerate(shells_in_wreath))
        + "\n"
    )

def query_archetype(index: int) -> str:
    """
    Query an archetype (1-12) across all three wreaths.

    Returns: archetype name, all shells carrying this archetype,
    and their wreath/superphase context.
    """
    data = _shells.load()
    parsed = _index(index, 12)
    if parsed is None:
        return f"Invalid archetype index {index}. Must be 1-12."

    index = parsed
    if (data.get("meta", {}).get("version") == "2.0"
            or isinstance(data.get("shells"), dict)):
        return _v2_report(data, "archetype", index)

    shells = [s for s in data["shells"] if s["archetype_index"] == index]
    name = shells[0]["archetype_name"]

    lines = [f"## Archetype #{index} — {name}\n"]
    lines.append(f"Appears in {len(shells)} shells (once per wreath):\n")
    for s in shells:
        wreath_name = SUPERPHASE_NAMES.get(s["wreath"], s["wreath"])
        lines.append(
            f"- **S{s['number']}** ({wreath_name}): "
            f"{s['nodes']} nodes, dim {s['dimension_first']}D, "
            f"mirror S{s['mirror']}"
        )
    return "\n".join(lines) + "\n"

def read_hologram_chapter(chapter: int) -> str:
    """
    Read a source-declared chapter (v2: 1-27; legacy: 1-21).

    These are the 21 chapters of the full 108D A+ organism specification:
      1: Inherited Body Diagnosis
      2: Numerical Mega-Cascade Law
      3: Shell Archetype Law
      4: Crystal Address Grammar
      5: Z-Point Hierarchy
      6: Live-Lock Lattice
      7: Major Metro Lines
      8: Legal Move Primitives & Route Legality
      9: Master Clock & 420-Beat Timing Law
      10: Odd-Dimensional Helm Wheels
      11: Vector Siteswap & Throw Law
      12: Global Conservation & Local Asymmetry Law
      13: Embodied Appendix Field (A->P)
      14: Reverse Canopy Field (K->Z)
      15: Q/O Mobius Pillars & Torsion Law
      16: E10 Atlas Conductor
      17: Crown Reset & Master Return Law
      18: Scheduled Route Construction & Live Routing Law
      19: Triune Mega-Weave & Current Law
      20: Nested Body Preservation Engine
      21: Final Canonical One-Line Definition & A+ Crown Seal
    """
    data = _hologram.load()
    v2 = data.get('meta', {}).get('version') == '2.0'
    limit = 27 if v2 else 21
    parsed = _index(chapter, limit)
    if parsed is None:
        return f"Invalid chapter {chapter}. Must be 1-{limit}."
    chapter = parsed
    if v2:
        try:
            chapters = data['chapters']
            ids = [record['id'] for record in chapters]
            if (any(type(n) is not int for n in ids) or len(set(ids)) != len(ids)
                    or set(ids) != set(range(1, limit + 1))):
                raise ValueError('chapter identities are missing, duplicated or undeclared')
            ch = next(record for record in chapters if record['id'] == chapter)
            return (f"## 108D Hologram - Chapter {ch['id']}: {ch['name']}\n\n"
                    f"**Description**: {ch['description']}\n\n"
                    f"**Source Mirror Law**: {data['mirror_law']}\n\n"
                    "HOLD: v2 does not declare legacy key concepts, Earth invariants, four projections or shared invariants.\n")
        except (KeyError, TypeError, ValueError) as exc:
            return f"HOLD: hologram registry has missing or conflicting source fields ({exc})."

    ch = data["chapters"][chapter - 1]
    return (
        f"## 108D Hologram — Chapter {ch['chapter']}: {ch['title']}\n\n"
        f"**Summary**: {ch['summary']}\n\n"
        f"**Key Concepts**: {', '.join(ch['key_concepts'])}\n\n"
        f"**Earth Invariant**: {ch['earth_invariant']}\n\n"
        f"**Four Projections**: {', '.join(data['meta']['four_projections'])}\n\n"
        f"**Shared Invariants**: {data['meta']['shared_invariants']}\n"
    )
