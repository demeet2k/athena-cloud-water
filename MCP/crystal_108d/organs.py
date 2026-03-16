"""12D organ atlas with 6 bilateral dyads."""

from ._cache import JsonCache

_organs = JsonCache("organ_atlas.json")


def query_organ(organ_name: str) -> str:
    """
    Query the 12D organ atlas by organ name or dyad index.

    Organ names: Identity, Address, Structure, Dynamics, Corridor, Replay,
    Self, Affect, Love, Governance, Migration, Publication

    Also accepts dyad index (1-6) or petal number (1-9).
    """
    data = _organs.load()
    name_lower = organ_name.lower().strip()

    # Try as dyad index
    if name_lower.isdigit():
        idx = int(name_lower)
        if 1 <= idx <= 6:
            return _format_dyad(data["dyads"][idx - 1], data)
        elif 7 <= idx <= 9:
            cc = data["crown_closures"][idx - 7]
            return (
                f"## Crown Closure — Petal {cc['petal']}: {cc['name']}\n\n"
                f"**Function**: {cc['function']}\n"
                f"**Description**: {cc['description']}\n"
            )

    # Try as organ name
    for dyad in data["dyads"]:
        for side in ["left", "right"]:
            organ = dyad[side]
            if name_lower == organ["name"].lower():
                coord = organ["coordinate"]
                return (
                    f"## Organ: {organ['name']} ({organ['axis']})\n\n"
                    f"**Dyad**: {dyad['name']} (Petal {dyad['petal']})\n"
                    f"**Function**: {dyad['function']}\n\n"
                    f"### Coordinate: χ = (p={coord['p']}, h={coord['h']}, "
                    f"j={coord['j']}, λ={coord['lambda']}, β={coord['beta']})\n\n"
                    f"**Placement**: {organ['placement']}\n"
                    f"**Corpus Anchor**: {organ['corpus_anchor']}\n"
                )

    # Try fuzzy match
    all_names = []
    for dyad in data["dyads"]:
        all_names.extend([dyad["left"]["name"], dyad["right"]["name"]])
    matches = [n for n in all_names if name_lower in n.lower()]
    if matches:
        return f"Did you mean: {', '.join(matches)}?"

    return (
        f"Organ '{organ_name}' not found. Available:\n"
        + "\n".join(f"  - {n}" for n in all_names)
        + "\n\nOr use dyad index 1-6, petal 7-9 for crown closures."
    )


def _format_dyad(dyad: dict, data: dict) -> str:
    left = dyad["left"]
    right = dyad["right"]
    lc = left["coordinate"]
    rc = right["coordinate"]
    return (
        f"## Dyad {dyad['index']}: {dyad['name']} (Petal {dyad['petal']})\n\n"
        f"**Function**: {dyad['function']}\n\n"
        f"### {left['name']} ({left['axis']}) — Kernel Half\n"
        f"- χ = (p={lc['p']}, h={lc['h']}, j={lc['j']}, "
        f"λ={lc['lambda']}, β={lc['beta']})\n"
        f"- {left['placement']}\n"
        f"- Corpus: {left['corpus_anchor']}\n\n"
        f"### {right['name']} ({right['axis']}) — Operational Half\n"
        f"- χ = (p={rc['p']}, h={rc['h']}, j={rc['j']}, "
        f"λ={rc['lambda']}, β={rc['beta']})\n"
        f"- {right['placement']}\n"
        f"- Corpus: {right['corpus_anchor']}\n"
    )
