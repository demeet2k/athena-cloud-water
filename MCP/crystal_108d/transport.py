"""Transport stack per dimension."""

from ._cache import JsonCache

_transport = JsonCache("transport_stacks.json")


def query_transport_stack(dimension: int) -> str:
    """
    Get the full transport stack available at a given dimension (3-12).

    Transport layers unlock progressively:
      3D: Z only
      4D: + A (Aether)
      5D: + L (Liminal/Live-Lock)
      6D: + Tunnel
      7D: + Metro
      8D: + Mycelium
      9D: + Bus
      10D: + Plane
      11D: + ETV (Edge-Time Vector)
      12D: All layers under crown lock

    Pass 0 to see the full stack overview.
    """
    data = _transport.load()

    if dimension == 0:
        lines = ["## Full Transport Stack\n"]
        lines.append(f"**Total Layers**: {len(data['layers'])}\n")
        lines.append(f"**Bus Spine**: {data['meta']['bus_spine']}")
        lines.append(f"**Tunnel Law**: {data['meta']['tunnel_law']}")
        lines.append(f"**Graph Isomorphism**: {data['meta']['graph_isomorphism']}")
        lines.append(f"**Planes**: {', '.join(data['meta']['plane_registry'])}\n")
        for layer in data["layers"]:
            lines.append(
                f"### {layer['index']}. {layer['code']} — {layer['name']}\n"
                f"{layer['description']}\n"
                f"Available from: {layer['available_from_dim']}D\n"
            )
        return "\n".join(lines)

    dim_str = str(dimension)
    if dim_str not in data["per_dimension"]:
        valid = sorted(data["per_dimension"].keys(), key=int)
        return f"Dimension {dimension} not available. Valid: {', '.join(valid)}"

    dim_data = data["per_dimension"][dim_str]
    available = dim_data["available"]

    lines = [
        f"## Transport Stack at {dimension}D\n",
        f"**Description**: {dim_data['description']}\n",
        f"**Active Layers** ({len(available)}/{len(data['layers'])}):\n",
    ]

    for layer in data["layers"]:
        if layer["code"] in available:
            lines.append(f"  ✓ **{layer['code']}** — {layer['name']}")
            if "spine" in layer:
                lines.append(f"    Spine: {' ↔ '.join(layer['spine'])}")
            if "planes" in layer:
                lines.append(f"    Planes: {', '.join(layer['planes'])}")
            if "hub_family" in layer:
                lines.append(f"    Hubs: {', '.join(layer['hub_family'])}")
        else:
            lines.append(f"  ○ {layer['code']} — {layer['name']} (locked)")

    return "\n".join(lines) + "\n"
