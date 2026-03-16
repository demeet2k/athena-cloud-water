"""4 overlay registries (lens, alchemy, animal, completion) and Sigma-15."""

from ._cache import JsonCache

_overlays = JsonCache("overlay_registries.json")


def query_overlay(registry: str, index: int = 0) -> str:
    """
    Query any of the 4 overlay registries.

    Registries:
      - '4_lens' or 'lens': Four lens overlay (S/F/C/R)
      - '7_alchemy' or 'alchemy': Seven alchemical stages
      - '5_animal' or 'animal': Five animal spirits
      - '9_completion' or 'completion': Nine completion gates
      - 'all': Overview of all registries

    Index (optional): specific entry within the registry (1-based).
    """
    data = _overlays.load()
    reg = registry.lower().strip()

    # Map aliases
    alias_map = {
        "lens": "4_lens", "4_lens": "4_lens", "4lens": "4_lens",
        "alchemy": "7_alchemy", "7_alchemy": "7_alchemy", "7alchemy": "7_alchemy",
        "animal": "5_animal", "5_animal": "5_animal", "5animal": "5_animal",
        "completion": "9_completion", "9_completion": "9_completion", "9completion": "9_completion",
    }

    if reg in ("all", "overview"):
        lines = ["## Overlay Registries Overview\n"]
        for key in ["4_lens", "7_alchemy", "5_animal", "9_completion"]:
            r = data[key]
            lines.append(f"### {r['name']} ({r['count']} entries)")
            for e in r["entries"]:
                name = e.get("name", e.get("code", "?"))
                lines.append(f"  - {name}")
        return "\n".join(lines) + "\n"

    reg_key = alias_map.get(reg)
    if not reg_key or reg_key not in data:
        return (
            f"Unknown registry '{registry}'. Use:\n"
            "  4_lens/lens, 7_alchemy/alchemy, 5_animal/animal, "
            "9_completion/completion, all"
        )

    r = data[reg_key]

    if index > 0:
        entries = r["entries"]
        if index < 1 or index > len(entries):
            return f"Index {index} out of range (1-{len(entries)})."
        e = entries[index - 1]
        return f"## {r['name']} — Entry {index}\n\n" + "\n".join(
            f"- **{k}**: {v}" for k, v in e.items()
        ) + "\n"

    # Show entire registry
    lines = [f"## {r['name']}\n"]
    if "source" in r:
        lines.append(f"**Source**: {r['source']}\n")
    for e in r["entries"]:
        name = e.get("name", e.get("code", "?"))
        idx = e.get("index", e.get("mask", ""))
        desc_parts = []
        for k, v in e.items():
            if k not in ("name", "code", "index", "mask"):
                desc_parts.append(f"{k}: {v}")
        lines.append(f"### {idx}. {name}")
        for dp in desc_parts:
            lines.append(f"  - {dp}")
    return "\n".join(lines) + "\n"


def query_sigma15(sigma: int) -> str:
    """
    Get a Sigma-15 lens combination by mask index (1-15).

    The 15 nonempty subsets of {S, F, C, R} form the observation field.
    Sigma-15 x 4 quadrants = Sigma-60 (the full 5D transform field).

    Mask 15 (SFCR) = complete local pattern / local aether.
    """
    data = _overlays.load()
    combos = data["4_lens"]["sigma_15_combinations"]

    if sigma < 1 or sigma > 15:
        return f"Sigma index must be 1-15. Got {sigma}."

    combo = combos[sigma - 1]
    return (
        f"## Sigma-15 #{combo['mask']}: {combo['name']}\n\n"
        f"- **Lenses**: {', '.join(combo['lenses'])}\n"
        f"- **Mask**: {combo['mask']} (binary: {combo['mask']:04b})\n"
        f"- **Sigma-60 expansion**: 4 quadrants × this combination\n"
        f"- **Is aether**: {'Yes (SFCR = complete local pattern)' if combo['mask'] == 15 else 'No'}\n"
    )
