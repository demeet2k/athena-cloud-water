"""36-shell mega-cascade logic and shell queries."""

from ._cache import JsonCache
from .constants import SUPERPHASE_NAMES

_shells = JsonCache("shell_registry.json")
_hologram = JsonCache("hologram_chapters.json")


def query_shell(shell_number: int) -> str:
    """
    Query a specific shell (1-36) in the 108D mega-cascade.

    Returns: archetype, wreath, superphase, node count, mirror shell,
    dimension first visible, and action description.
    """
    data = _shells.load()
    if shell_number < 1 or shell_number > 36:
        return f"Invalid shell {shell_number}. Must be 1-36."

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
    tag_lower = tag.lower()

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
    if index < 1 or index > 12:
        return f"Invalid archetype index {index}. Must be 1-12."

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
    Read an ATHENA CRYSTAL 108+ HOLOGRAM chapter (1-21).

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
    if chapter < 1 or chapter > 21:
        return f"Invalid chapter {chapter}. Must be 1-21."

    ch = data["chapters"][chapter - 1]
    return (
        f"## 108D Hologram — Chapter {ch['chapter']}: {ch['title']}\n\n"
        f"**Summary**: {ch['summary']}\n\n"
        f"**Key Concepts**: {', '.join(ch['key_concepts'])}\n\n"
        f"**Earth Invariant**: {ch['earth_invariant']}\n\n"
        f"**Four Projections**: {', '.join(data['meta']['four_projections'])}\n\n"
        f"**Shared Invariants**: {data['meta']['shared_invariants']}\n"
    )
