# CRYSTAL: Xi108:W2:A7:S16 | face=R | node=124 | depth=2 | phase=Cardinal
# METRO: Sa,Dl
# BRIDGES: Xi108:W2:A7:S15→Xi108:W2:A7:S17→Xi108:W1:A7:S16→Xi108:W3:A7:S16→Xi108:W2:A6:S16→Xi108:W2:A8:S16

"""
Dimensional Emergence Path
===========================
Formalizes the 3D -> 4D -> ... -> 12D -> A+ emergence sequence.
Each phase describes HOW a lower-dimensional body weaves into its
successor, WHAT lens upgrades occur, and WHICH transport layers unlock.
"""

from ._cache import JsonCache

_EMERGENCE = JsonCache("dimensional_emergence.json")


def _query_v2_emergence(data, comp):
    try:
        sequence = data['emergence_sequence']
        if not isinstance(sequence, list) or not sequence:
            raise ValueError('source sequence must be nonempty')
        description = data['description']
        if not isinstance(description, str) or not description.strip():
            raise ValueError('source description is missing')
        pairs = []
        for record in sequence:
            if not all(isinstance(record[k], str) and record[k].strip() for k in ('from', 'to', 'mechanism')):
                raise ValueError('transition description is incomplete')
            gates = record['gates']
            if (not isinstance(gates, list) or not gates or any(type(g) is not int or g < 1 for g in gates)
                    or len(set(gates)) != len(gates)):
                raise ValueError('gate IDs must be unique positive integers')
            pair = f"{record['from']}->{record['to']}".lower()
            if pair in pairs or (pairs and sequence[len(pairs)-1]['to'] != record['from']):
                raise ValueError('sequence has duplicate or discontinuous transitions')
            pairs.append(pair)
        selected = list(enumerate(sequence, 1))
        if comp.startswith('phase:'):
            query = comp.split(':', 1)[1].strip()
            if query.isascii() and query.isdecimal():
                normalized = query.lstrip('0') or '0'
                if len(normalized) > len(str(len(sequence))):
                    return f'Invalid source sequence position. Use 1-{len(sequence)}.'
                position = int(normalized)
                if not 1 <= position <= len(sequence):
                    return f'Invalid source sequence position. Use 1-{len(sequence)}.'
                selected = [(position, sequence[position-1])]
            else:
                query = query.replace(' ', '')
                if query not in pairs:
                    return 'HOLD: no exact source transition matches this selector; partial endpoints and legacy phase mappings are unavailable.'
                position = pairs.index(query) + 1
                selected = [(position, sequence[position-1])]
        elif comp not in ('all', 'phases', 'status'):
            if comp in ('kernel', 'lenses', 'bodies') or comp.startswith('lens:'):
                return f"HOLD: v2 does not declare '{comp}' kernel embedding, lens upgrade or body directory fields."
            return f"Unknown component '{comp}'. Use all, phases, phase:<source position or exact pair>."
        lines = ['## Dimensional Emergence (source sequence)', description]
        for position, record in selected:
            lines += [f"### Source sequence position {position}: {record['from']} -> {record['to']}",
                      f"- **Mechanism**: {record['mechanism']}", f"- **Declared Gates**: {record['gates']}"]
        lines.append('HOLD: source descriptions do not establish kernel embedding, lens upgrades, transport readiness or body directories; positions are not legacy phase identities.')
        return '\n'.join(lines) + '\n'
    except (KeyError, TypeError, ValueError) as exc:
        return f'HOLD: emergence registry has missing or conflicting source fields ({exc}).'


def query_emergence(component: str = "all", source: str = "current") -> str:
    """
    Read the source dimensional emergence path.

    V2 exposes sequence positions or exact from->to pairs; unsupported proofs HOLD.
    The component descriptions below refer to valid legacy registries.

    Components:
      - all         : Full emergence overview
      - phases      : All 7 emergence phases
      - phase:N     : Specific phase by index (1-7) or name (e.g. phase:4D->6D)
      - kernel      : Kernel embedding law and chain
      - lenses      : Cross-lens upgrade sequence by stage
      - lens:STAGE  : Lens state at a specific stage (e.g. lens:6D)
      - bodies      : Body directory mapping

    Source: current (default), or explicit archive for pinned historical
    descriptions and clock MODEL only. Archive results never certify runtime.
    """
    if source == "archive":
        from .core_archive import render_core_archive
        return render_core_archive("dimensional_emergence.json", lambda data: _render_query_emergence(data, component), component)
    if source != "current":
        return "HOLD: source must be current or explicit archive."
    try:
        data = _EMERGENCE.load()
    except (OSError, ValueError, TypeError) as exc:
        return f'HOLD: emergence source is unavailable or unreadable ({exc}).'
    return _render_query_emergence(data, component)


def _render_query_emergence(data: dict, component: str = "all") -> str:
    """
    Read the source dimensional emergence path.

    V2 exposes sequence positions or exact from->to pairs; unsupported proofs HOLD.
    The component descriptions below refer to valid legacy registries.

    Components:
      - all         : Full emergence overview
      - phases      : All 7 emergence phases
      - phase:N     : Specific phase by index (1-7) or name (e.g. phase:4D->6D)
      - kernel      : Kernel embedding law and chain
      - lenses      : Cross-lens upgrade sequence by stage
      - lens:STAGE  : Lens state at a specific stage (e.g. lens:6D)
      - bodies      : Body directory mapping
    """
    if not isinstance(data, dict) or not isinstance(data.get('meta'), dict):
        return 'HOLD: emergence source requires a registry object and metadata object.'
    if not isinstance(component, str) or not component.strip():
        return 'Invalid emergence component: expected nonempty text.'
    comp = component.strip().lower()
    if data.get('meta', {}).get('version') == '2.0' or 'emergence_sequence' in data:
        return _query_v2_emergence(data, comp)

    if comp == "all":
        return _format_all(data)
    elif comp == "phases":
        return _format_phases(data)
    elif comp.startswith("phase:"):
        return _format_one_phase(data, comp.split(":", 1)[1])
    elif comp == "kernel":
        return _format_kernel(data)
    elif comp == "lenses":
        return _format_lenses(data)
    elif comp.startswith("lens:"):
        return _format_lens_at(data, comp.split(":", 1)[1])
    elif comp == "bodies":
        return _format_bodies(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, phases, "
            "phase:<N or name>, kernel, lenses, lens:<stage>, bodies"
        )

def emergence_status() -> str:
    """Return a status summary for the resource endpoint."""
    try:
        data = _EMERGENCE.load()
    except (OSError, ValueError, TypeError) as exc:
        return f'HOLD: emergence source is unavailable or unreadable ({exc}).'
    if not isinstance(data, dict) or not isinstance(data.get('meta'), dict):
        return 'HOLD: emergence source requires a registry object and metadata object.'
    if data.get('meta', {}).get('version') == '2.0' or 'emergence_sequence' in data:
        return _query_v2_emergence(data, 'status')
    m = data["meta"]
    return (
        "## Dimensional Emergence Path\n\n"
        f"**Path**: `{m['path']}`\n"
        f"**Governing Law**: {m['governing_law']}\n"
        f"**Kernel Embedding**: {m['kernel_embedding_law']}\n"
        f"**Phases**: {m['total_phases']}\n"
        f"**Source**: {m['source']}\n"
    )

# ── Formatters ──────────────────────────────────────────────────────

def _format_all(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## Dimensional Emergence Path\n",
        f"**Path**: `{m['path']}`",
        f"**Governing Law**: {m['governing_law']}",
        f"**Kernel Embedding**: {m['kernel_embedding_law']}\n",
        "### Emergence Phases\n",
    ]
    for phase in data["emergence_phases"]:
        lines.append(
            f"  {phase['index']}. **{phase['from']} -> {phase['to']}** "
            f"({phase['name']}): {phase['mechanism']}"
        )

    lines.append("\n### Kernel Embedding Chain\n")
    for step in data["kernel_embedding"]["chain"]:
        lines.append(f"  - {step['dimension']}D: {step['embedding']}")

    lines.append(f"\n**Expansion**: {data['kernel_embedding']['expansion_factor']}")
    return "\n".join(lines)

def _format_phases(data: dict) -> str:
    lines = ["## Emergence Phases\n"]
    for phase in data["emergence_phases"]:
        lines.append(f"\n### Phase {phase['index']}: {phase['name']}")
        lines.append(f"**{phase['from']} -> {phase['to']}**\n")
        lines.append(f"- **Mechanism**: {phase['mechanism']}")
        lines.append(f"- **Lens State**: {phase['lens_state']}")
        lines.append(f"- **Body Gained**: {phase['body_gained']}")
        lines.append(f"- **Transport**: {', '.join(phase['transport_gained'])}")
        lines.append(f"- **Key Object**: {phase['key_object']}")
        if phase.get("directory"):
            lines.append(f"- **Directory**: {phase['directory']}")
        lines.append(f"\n{phase['description']}")
    return "\n".join(lines)

def _format_one_phase(data: dict, query: str) -> str:
    phases = data["emergence_phases"]
    # Try index
    try:
        idx = int(query)
        for p in phases:
            if p["index"] == idx:
                return _render_phase(p)
        return f"Phase index {idx} not found. Use 1-{len(phases)}."
    except ValueError:
        pass

    # Try name/dimension match
    q = query.upper().replace(" ", "")
    for p in phases:
        key = f"{p['from']}->{p['to']}".replace(" ", "")
        if q in key or q in p["name"].upper().replace(" ", ""):
            return _render_phase(p)

    return f"Phase '{query}' not found. Use index 1-7 or dimension pair like '4D->6D'."

def _render_phase(phase: dict) -> str:
    lines = [
        f"## Phase {phase['index']}: {phase['name']}",
        f"**{phase['from']} -> {phase['to']}**\n",
        f"**Mechanism**: {phase['mechanism']}",
        f"**Lens State**: {phase['lens_state']}",
        f"**Body Gained**: {phase['body_gained']}",
        f"**Transport Gained**: {', '.join(phase['transport_gained'])}",
        f"**Key Object**: {phase['key_object']}",
    ]
    if phase.get("directory"):
        lines.append(f"**Directory**: {phase['directory']}")
    lines.append(f"\n{phase['description']}")
    return "\n".join(lines)

def _format_kernel(data: dict) -> str:
    ke = data["kernel_embedding"]
    lines = [
        "## Kernel Embedding Law\n",
        f"**Law**: {ke['law']}",
        f"**Expansion Factor**: {ke['expansion_factor']}\n",
        "### Embedding Chain\n",
    ]
    for step in ke["chain"]:
        lines.append(f"  - **{step['dimension']}D**: {step['embedding']}")
    return "\n".join(lines)

def _format_lenses(data: dict) -> str:
    lines = ["## Cross-Lens Upgrade Sequence\n"]
    lines.append("| Stage | Square | Flower | Cloud | Fractal | Combined |")
    lines.append("|-------|--------|--------|-------|---------|----------|")
    for row in data["cross_lens_upgrade_sequence"]:
        lines.append(
            f"| {row['stage']} | {row['square']} | {row['flower']} | "
            f"{row['cloud']} | {row['fractal']} | {row['combined']} |"
        )
    return "\n".join(lines)

def _format_lens_at(data: dict, stage: str) -> str:
    stage_upper = stage.upper()
    for row in data["cross_lens_upgrade_sequence"]:
        if row["stage"].upper() == stage_upper:
            return (
                f"## Lens State at {row['stage']}\n\n"
                f"- **Square**: {row['square']}\n"
                f"- **Flower**: {row['flower']}\n"
                f"- **Cloud**: {row['cloud']}\n"
                f"- **Fractal**: {row['fractal']}\n"
                f"- **Combined**: {row['combined']}"
            )
    stages = [r["stage"] for r in data["cross_lens_upgrade_sequence"]]
    return f"Stage '{stage}' not found. Available: {', '.join(stages)}"

def _format_bodies(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## Body Directories\n",
        "Local nervous system directories containing dimensional body documents:\n",
    ]
    for dim, dirname in m["body_directories"].items():
        lines.append(f"- **{dim}**: `ACTIVE_NERVOUS_SYSTEM/{dirname}/`")
    lines.append(
        "\nUse `read_dimensional_body(dimension, document)` to explore these."
    )
    return "\n".join(lines)
