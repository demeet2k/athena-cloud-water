# CRYSTAL: Xi108:W2:A6:S18 | face=F | node=171 | depth=2 | phase=Cardinal
# METRO: Ω
# BRIDGES: Xi108:W2:A6:S17→Xi108:W2:A6:S19→Xi108:W1:A6:S18→Xi108:W3:A6:S18→Xi108:W2:A5:S18→Xi108:W2:A7:S18

"""
NEXT-Omega Live Cell Constitution
==================================
Defines the minimum lawful execution cell:
  row -> packet -> trace -> cert -> seed

Each schema represents one layer of the execution membrane.
The metro map traces the soul's path through one complete cycle.
"""

from ._cache import JsonCache, DATA_DIR
from .registry_sources import query_registry, ARCHIVES

_CELL = JsonCache("live_cell_constitution.json")


def _load_cell_source():
    try:
        if not (DATA_DIR / 'live_cell_constitution.json').is_file():
            return None, 'HOLD: current live-cell JSON is missing; archive selection must be explicit.'
        data = _CELL.load()
    except (OSError, ValueError, TypeError) as exc:
        return None, f'HOLD: live-cell source is unavailable or unreadable ({exc}).'
    if not isinstance(data, dict) or not isinstance(data.get('meta'), dict):
        return None, 'HOLD: live-cell source requires registry and metadata objects.'
    return data, None


def _requirement_catalog(data):
    """Recognize the tracked requirement schema, separately from archived cell schemas."""
    return 'requirements' in data or data['meta'].get('type') == 'live_cell_constitution'


def _query_requirements(data, component):
    try:
        if 'cell_schema' in data:
            raise ValueError('requirement catalog conflicts with archived cell schema family')
        if data['meta'].get('type') != 'live_cell_constitution' or data['meta'].get('version') != '1.0':
            raise ValueError('requirement source family or version is unsupported')
        records = data['requirements']
        if (not isinstance(records, list) or len(records) != 7
                or any(not isinstance(record, dict) for record in records)
                or {record['id'] for record in records} != {f'LC{i}' for i in range(1, 8)}):
            raise ValueError('seven unique LC1..LC7 requirement records are required')
        for record in records:
            if not all(isinstance(record[k], str) and record[k].strip() for k in ('id', 'name', 'description')):
                raise ValueError('requirement fields must be nonempty source strings')
        if not all(isinstance(data[k], str) and data[k].strip() for k in ('description', 'alive_threshold')):
            raise ValueError('source description or threshold statement is missing')
        selected = records
        if component.startswith('requirement:'):
            query = component.split(':', 1)[1].strip().casefold()
            selected = [r for r in records if query in (r['id'].casefold(), r['name'].casefold())]
            if len(selected) != 1:
                return 'Unknown live-cell requirement. Use an exact source ID or name: ' + ', '.join(r['id'] for r in records)
        elif component not in ('all', 'requirements', 'status'):
            if (component in ('schemas', 'metro', 'liminal', 'soul', 'route')
                    or component.startswith(('schema:', 'station:'))):
                return (f"HOLD: requirement catalog does not declare '{component}' cell schemas, execution metro, "
                        'route signatures, liminal coordinates or soul stamps; no proof is available.')
            return 'Unknown component. Use all, requirements, requirement:<exact source ID or name>.'
        lines = ['## Live Cell Requirement Catalog (source descriptions)', data['description']]
        for record in selected:
            lines += [f"### {record['id']}: {record['name']}", record['description']]
        lines += [f"**Declared Alive Threshold**: {data['alive_threshold']}",
                  'HOLD: descriptions and caller assertions do not verify requirement satisfaction. Source-bound address, graph, weight, observation, mutation, compression and recovery evidence with evaluators is required; no liveness certificate is issued.']
        return '\n'.join(lines) + '\n'
    except (KeyError, TypeError, ValueError) as exc:
        return f'HOLD: live-cell requirement source has missing or conflicting fields ({exc}).'


def query_live_cell(component: str = "all") -> str:
    """
    Read the source live-cell constitution.

    The current requirement catalog supports all, requirements and requirement:<ID/name>.
    The components below apply only to a supported archived cell-schema source.

    Components:
      - all       : Full constitution overview
      - schemas   : All 6 cell schemas (BoardStateRow, PacketSynapse, etc.)
      - schema:X  : Specific schema (e.g. schema:BoardStateRow, schema:TraceCert)
      - metro     : 14-station execution metro map
      - station:X : Specific metro station (e.g. station:M00, station:M60)
      - liminal   : Liminal coordinate system
      - soul      : Soul stamp schema
      - route     : Route types and signature
    """
    if isinstance(component, str) and component.strip().lower().startswith('archive:'):
        return query_registry('live_cell_constitution.json', _CELL, component, _legacy_live_cell, _query_requirements)
    data, error = _load_cell_source()
    if error:
        return error
    if not isinstance(component, str) or not component.strip():
        return 'Invalid live-cell component: expected nonempty text.'
    comp = component.strip().lower()
    if _requirement_catalog(data):
        return _query_requirements(data, comp)
    return query_registry('live_cell_constitution.json', _CELL, component, _legacy_live_cell, _query_requirements)


def live_cell_status() -> str:
    """Return a status summary for the resource endpoint."""
    data, error = _load_cell_source()
    if error:
        return error
    if _requirement_catalog(data):
        return _query_requirements(data, 'status')
    return query_registry('live_cell_constitution.json', _CELL, 'all', _legacy_live_cell_status, _query_requirements)


# ── Formatters ──────────────────────────────────────────────────────

def _format_all(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## NEXT-Omega Live Cell Constitution\n",
        f"**Title**: {m['title']}",
        f"**Source**: {m['source']}",
        f"**Minimum Lawful Unit**: `{m['minimum_lawful_unit']}`",
        f"**Route Signature**: `{m['route_signature']}`\n",
        "### Cell Schemas\n",
    ]
    for name, schema in data["cell_schema"].items():
        lines.append(f"- **{name}** (v{schema['version']}): {schema['description']}")

    lines.append("\n### Metro Stations\n")
    for code, station in data["metro_map"]["stations"].items():
        lines.append(f"- **{code}** {station['name']}: {station['role']}")

    lines.append(f"\n### Route Types\n")
    for rtype, info in data["metro_map"]["route_types"].items():
        lines.append(f"- **{rtype}**: {info['from']} -> {info['to']} ({info['description']})")

    return "\n".join(lines)

def _format_schemas(data: dict) -> str:
    lines = ["## Cell Schemas\n"]
    for name, schema in data["cell_schema"].items():
        lines.append(f"\n### {name} (v{schema['version']})")
        lines.append(schema["description"])
        lines.append("\n**Fields**:")
        for field, desc in schema["fields"].items():
            lines.append(f"  - `{field}`: {desc}")
        # Show constraint/property/invariant
        for key in ["invariant", "routing_rule", "constraint", "property", "verification"]:
            if key in schema:
                lines.append(f"\n**{key.title()}**: {schema[key]}")
    return "\n".join(lines)

def _format_one_schema(data: dict, name: str) -> str:
    schemas = data["cell_schema"]
    # Exact case-insensitive identity; a partial selector cannot choose an arbitrary schema.
    for key, schema in schemas.items():
        if key.lower() == name.lower():
            lines = [f"## {key} (v{schema['version']})\n", schema["description"], "\n**Fields**:"]
            for field, desc in schema["fields"].items():
                lines.append(f"  - `{field}`: {desc}")
            for k in ["invariant", "routing_rule", "constraint", "property", "verification"]:
                if k in schema:
                    lines.append(f"\n**{k.title()}**: {schema[k]}")
            return "\n".join(lines)
    return f"Schema '{name}' not found. Available: {', '.join(schemas.keys())}"

def _format_metro(data: dict) -> str:
    metro = data["metro_map"]
    lines = [f"## Execution Metro Map\n", metro["description"], ""]
    for code, station in metro["stations"].items():
        lines.append(
            f"- **{code}** {station['name']} [{station['element']}] "
            f"({station['phase']}): {station['role']}"
        )
    lines.append("\n### Route Types\n")
    for rtype, info in metro["route_types"].items():
        lines.append(f"- **{rtype}**: {info['from']} -> {info['to']} -- {info['description']}")
    return "\n".join(lines)

def _format_station(data: dict, code: str) -> str:
    code_upper = code.upper()
    stations = data["metro_map"]["stations"]
    if code_upper in stations:
        s = stations[code_upper]
        return (
            f"## Station {code_upper}: {s['name']}\n\n"
            f"**Role**: {s['role']}\n"
            f"**Element**: {s['element']}\n"
            f"**Phase**: {s['phase']}"
        )
    return f"Station '{code}' not found. Available: {', '.join(stations.keys())}"

def _format_liminal(data: dict) -> str:
    lc = data["liminal_coordinates"]
    lines = [
        "## Liminal Coordinates\n",
        lc["description"],
        f"\n**Format**: `{lc['format']}`",
        f"**Example**: `{lc['example']}`\n",
        "### Golden Points\n",
    ]
    for key, gp in lc["golden_points"].items():
        lines.append(f"- **{key}** = {gp['value']}: {gp['meaning']}")
    return "\n".join(lines)

def _format_soul(data: dict) -> str:
    ss = data["soul_stamp_schema"]
    lines = [
        "## Soul Stamp Schema\n",
        ss["description"],
        f"\n**Property**: {ss['property']}\n",
        "**Fields**:",
    ]
    for field, desc in ss["fields"].items():
        lines.append(f"  - `{field}`: {desc}")
    return "\n".join(lines)

def _format_routes(data: dict) -> str:
    m = data["meta"]
    routes = data["metro_map"]["route_types"]
    lines = [
        "## Route Signature\n",
        f"**Full Signature**: `{m['route_signature']}`\n",
    ]
    for rtype, info in routes.items():
        lines.append(f"### {rtype}")
        lines.append(f"  {info['from']} -> {info['to']}: {info['description']}")
    return "\n".join(lines)


def _legacy_live_cell(data, component):
    comp = component.strip().lower()
    if comp == "all":
        return _format_all(data)
    elif comp == "schemas":
        return _format_schemas(data)
    elif comp.startswith("schema:"):
        return _format_one_schema(data, comp.split(":", 1)[1])
    elif comp == "metro":
        return _format_metro(data)
    elif comp.startswith("station:"):
        return _format_station(data, comp.split(":", 1)[1])
    elif comp == "liminal":
        return _format_liminal(data)
    elif comp == "soul":
        return _format_soul(data)
    elif comp == "route":
        return _format_routes(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, schemas, "
            "schema:<name>, metro, station:<code>, liminal, soul, route"
        )


def _legacy_live_cell_status(data, _):
    m = data["meta"]
    schemas = data["cell_schema"]
    stations = data["metro_map"]["stations"]
    return (
        "## NEXT-Omega Live Cell Constitution\n\n"
        f"**Minimum Lawful Unit**: `{m['minimum_lawful_unit']}`\n"
        f"**Schemas**: {m['total_schemas']} "
        f"({', '.join(schemas.keys())})\n"
        f"**Metro Stations**: {m['metro_stations']} "
        f"(M00 Root -> MD0 Loop)\n"
        f"**Route Signature**: `{m['route_signature']}`\n"
        f"**Source**: {m['source']}\n"
    )
