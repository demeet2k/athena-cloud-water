"""Z-point hierarchy navigation."""

from ._cache import JsonCache

_zpoints = JsonCache("z_point_hierarchy.json")


def resolve_z_point(z_type: str, scope: str = "") -> str:
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
    data = _zpoints.load()
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
