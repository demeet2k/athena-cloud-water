# CRYSTAL: Xi108:W2:A5:S19 | face=S | node=175 | depth=2 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W2:A5:S18→Xi108:W2:A5:S20→Xi108:W1:A5:S19→Xi108:W3:A5:S19→Xi108:W2:A4:S19→Xi108:W2:A6:S19

"""
Meta Observer Swarm Protocol
==============================
Provides the 57-cycle meta-observation swarm synthesis directive:
  - Core identity and mission
  - 6 phases per cycle (Ingest, 4-Element Synthesis, 12D Observation,
    A+ Upgrade, Observation Ledger, Swarm Emission)
  - 4-element deep synthesis (Earth/Fire/Water/Air)
  - 12-dimensional observation schema
  - Positive/negative ledger structure
  - Swarm coordination protocol
"""

from ._cache import JsonCache

_META_OBS = JsonCache("meta_observer_swarm.json")

def query_meta_observer(component: str = "all") -> str:
    """
    Query the 57-cycle meta-observer swarm protocol.

    Components:
      - all          : Full protocol overview
      - identity     : Core identity and mission
      - phases       : 6 phases per cycle (A-F)
      - elements     : 4-element deep synthesis (Earth/Fire/Water/Air)
      - dimensions   : 12-dimensional observation schema
      - ledger       : Positive/negative observation ledger structure
      - swarm        : Swarm emission and coordination rules
      - rules        : High-level orchestration rules
      - termination  : Cycle completion and termination conditions
    """
    data = _META_OBS.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "identity":
        return _format_identity(data)
    elif comp == "phases":
        return _format_phases(data)
    elif comp == "elements":
        return _format_elements(data)
    elif comp == "dimensions":
        return _format_dimensions(data)
    elif comp == "ledger":
        return _format_ledger(data)
    elif comp == "swarm":
        return _format_swarm(data)
    elif comp == "rules":
        return _format_rules(data)
    elif comp == "termination":
        return _format_termination(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, identity, phases, "
            "elements, dimensions, ledger, swarm, rules, termination"
        )

def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    mission = data.get("mission", meta.get("mission", meta.get("description", "Unknown")))
    lines = [
        "## Meta Observer Swarm Protocol\n",
        f"**Title**: {meta.get('title', 'Meta Observer Swarm')}",
        f"**Mission**: {mission}",
        f"**Version**: {meta.get('version', '?')}",
        f"**Source**: {meta.get('source', '?')}",
        f"**Key Insight**: {meta.get('key_insight', 'N/A')}",
    ]
    return "\n".join(lines)

def _format_identity(data: dict) -> str:
    ident = data.get("identity", {})
    lines = ["## Meta Observer — Core Identity\n"]
    lines.append(f"**Role**: {ident.get('role', 'Central observing intelligence')}")
    if "tracks" in ident:
        lines.append("\n**Tracks**:")
        for t in ident["tracks"]:
            lines.append(f"  - {t}")
    if "principles" in ident:
        lines.append("\n**Principles**:")
        for p in ident["principles"]:
            lines.append(f"  - {p}")
    return "\n".join(lines)

def _format_phases(data: dict) -> str:
    phases = data.get("phases", [])
    lines = ["## Cycle Phases (A-F)\n"]
    for p in phases:
        lines.append(f"### Phase {p.get('code', '?')} — {p.get('name', '?')}")
        lines.append(p.get("description", ""))
        lines.append("")
    return "\n".join(lines)

def _format_elements(data: dict) -> str:
    elems = data.get("four_element_synthesis", {})
    lines = ["## 4-Element Deep Synthesis\n"]
    for name, desc in elems.items():
        lines.append(f"### {name}")
        if isinstance(desc, dict):
            lines.append(f"**Focus**: {desc.get('focus', '')}")
            if "keywords" in desc:
                lines.append(f"**Keywords**: {', '.join(desc['keywords'])}")
        else:
            lines.append(str(desc))
        lines.append("")
    return "\n".join(lines)

def _format_dimensions(data: dict) -> str:
    dims = data.get("twelve_dimensions", [])
    lines = ["## 12-Dimensional Observation Schema\n"]
    for i, d in enumerate(dims, 1):
        if isinstance(d, dict):
            lines.append(f"{i}. **{d.get('name', '?')}**: {d.get('description', '')}")
        else:
            lines.append(f"{i}. {d}")
    return "\n".join(lines)

def _format_ledger(data: dict) -> str:
    ledger = data.get("observation_ledger", {})
    lines = ["## Observation Ledger Structure\n"]
    for category in ["positive", "negative", "open"]:
        items = ledger.get(category, [])
        lines.append(f"### {category.title()}")
        for item in items:
            lines.append(f"  - {item}")
        lines.append("")
    return "\n".join(lines)

def _format_swarm(data: dict) -> str:
    swarm = data.get("swarm_emission", {})
    lines = ["## Swarm Emission Protocol\n"]
    if "instruction_types" in swarm:
        lines.append("**Instruction Types**:")
        for t in swarm["instruction_types"]:
            lines.append(f"  - {t}")
    if "communication_medium" in swarm:
        lines.append(f"\n**Medium**: {swarm['communication_medium']}")
    return "\n".join(lines)

def _format_rules(data: dict) -> str:
    rules = data.get("rules", [])
    lines = ["## High-Level Orchestration Rules\n"]
    for r in rules:
        if isinstance(r, dict):
            lines.append(f"### {r.get('number', '?')}. {r.get('name', '?')}")
            lines.append(r.get("description", ""))
        else:
            lines.append(f"- {r}")
        lines.append("")
    return "\n".join(lines)

def _format_termination(data: dict) -> str:
    term = data.get("termination", {})
    return (
        "## Termination Conditions\n\n"
        f"**Cycle Count**: {term.get('cycle_count', 57)}\n"
        f"**Condition**: {term.get('condition', 'Full bounded cycle count completed')}\n"
        f"**Early Exit**: {term.get('early_exit', 'Not permitted')}"
    )
