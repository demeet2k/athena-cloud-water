# CRYSTAL: Xi108:W1:A7:S1 | face=S | node=1 | depth=0 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W1:A7:S2→Xi108:W2:A7:S1→Xi108:W1:A6:S1→Xi108:W1:A8:S1

"""Z-point hierarchy navigation."""

from ._cache import JsonCache

_zpoints = JsonCache("z_point_hierarchy.json")

def _v2_catalog(data):
    """Validate source identities before rendering descriptive records."""
    if "types" in data:
        raise ValueError("legacy and v2 catalogs conflict")
    points = data["z_points"]
    if not isinstance(points, list) or not points:
        raise ValueError("z_points must be a nonempty list")
    ids = set()
    for point in points:
        if not isinstance(point, dict):
            raise ValueError("z_point must be an object")
        for field in ("id", "name", "dimension", "description"):
            if not isinstance(point[field], str) or not point[field].strip():
                raise ValueError(f"missing or invalid {field}")
        identity = point["id"].strip().casefold()
        if identity in ids:
            raise ValueError("duplicate z_point identity")
        ids.add(identity)
    for field in ("description", "convergence_law", "omega_theorem"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"missing or invalid {field}")
    return points


def _resolve_v2(data, selector, scope):
    points = _v2_catalog(data)
    if scope:
        return "HOLD: v2 declares no scoped distributed-zero selector."
    overview = selector in ("all", "hierarchy", "overview")
    if overview:
        selected = points
    else:
        selected = [point for point in points if selector in {
            point[field].strip().casefold() for field in ("id", "name", "dimension")}]
        if len(selected) != 1:
            return (f"HOLD: Z-point selector '{selector}' is missing or ambiguous in v2. "
                    "Use an exact source ID, name or unique dimension; legacy categories "
                    "and tunnel routing have no declared mapping.")
    lines = ["## Z-Point Hierarchy (v2 source descriptions)", data["description"]]
    for point in selected:
        lines += [f"### {point['id']} - {point['name']} ({point['dimension']})",
                  point["description"]]
    lines += [f"**Convergence law (declared)**: {data['convergence_law']}",
              f"**Omega theorem (declared)**: {data['omega_theorem']}",
              "HOLD: descriptions do not certify convergence, returnability or a legal tunnel."]
    return "\n\n".join(lines) + "\n"


def resolve_z_point(z_type: str, scope: str = "") -> str:
    """Read exact v2 IDs/names/dimensions or a valid legacy hierarchy.

    Unsupported legacy categories and execution proofs remain on HOLD for v2.
    """
    if not isinstance(z_type, str) or not z_type.strip() or not isinstance(scope, str):
        return "HOLD: Z-point selector and scope must be strings; selector must be nonempty."
    selector, scope = z_type.strip().casefold(), scope.strip()
    try:
        data = _zpoints.load()
        if not isinstance(data, dict):
            raise ValueError("registry must be an object")
        meta = data.get("meta", {})
        if not isinstance(meta, dict):
            raise ValueError("meta must be an object")
        if meta.get("version") == "2.0" or "z_points" in data:
            return _resolve_v2(data, selector, scope)
        return _resolve_legacy(data, selector, scope)
    except (KeyError, TypeError, ValueError, OSError, IndexError) as exc:
        return f"HOLD: Z-point registry has missing or conflicting source fields ({exc})."


def _resolve_legacy(data, z_type: str, scope: str = "") -> str:
    """
    Navigate the Z-point hierarchy.

    Types:
      - 'global' or 'Z*': Universal absolute zero
      - 'atlas' or 'Z_E10': Atlas conductor zero
      - 'local' or 'Z_L': Local station zeros
      - 'distributed' or 'Z_D': Distributed zeros (Q/O pillars, appendix, canopy)
      - 'all' or 'hierarchy': Full hierarchy overview
      - 'tunnel': Tunnel law (X -> Z* -> Y)

    Optional scope narrows distributed zeros: 'Q', 'O', 'AP', 'KZ'
    """
    zt = z_type.lower().strip()

    if zt in ("all", "hierarchy", "overview"):
        lines = ["## Z-Point Hierarchy\n"]
        lines.append(f"**Law**: {data['hierarchy_law']}\n")
        lines.append(f"**Returnability**: {data['returnability']}\n")
        lines.append(f"**Tunnel Law**: {data['tunnel_law']}\n")
        for t in data["types"]:
            lines.append(f"\n### {t['symbol']} ({t['scope']})")
            lines.append(t["description"])
            for prop in t.get("properties", []):
                lines.append(f"  - {prop}")
        return "\n".join(lines) + "\n"

    if zt == "tunnel":
        return (
            f"## Tunnel Law\n\n"
            f"{data['tunnel_law']}\n\n"
            f"Any two points X and Y can be connected through Z*.\n"
            f"The tunnel is legal if it satisfies zero-factorability.\n"
        )

    # Find matching type
    for t in data["types"]:
        if zt in (t["code"].lower(), t["symbol"].lower(), t["scope"]):
            lines = [
                f"## {t['symbol']} — {t['scope'].title()} Zero\n",
                t["description"],
                "",
            ]
            for prop in t.get("properties", []):
                lines.append(f"- {prop}")

            # If distributed, show sub-types
            if "sub_types" in t:
                lines.append("\n### Sub-Types:")
                for st in t["sub_types"]:
                    if scope and scope.upper() != st["code"].split("_")[1]:
                        continue
                    lines.append(f"- **{st['code']}**: {st['description']}")

            lines.append(f"\n**Reachable from**: {t['reachable_from']}")
            return "\n".join(lines) + "\n"

    return (
        f"Unknown Z-point type '{z_type}'. Use:\n"
        "  global/Z*, atlas/Z_E10, local/Z_L, distributed/Z_D, "
        "all/hierarchy, tunnel"
    )
