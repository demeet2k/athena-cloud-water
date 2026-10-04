# CRYSTAL: Xi108:W1:A8:S14 | face=R | node=105 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W1:A8:S13→Xi108:W1:A8:S15→Xi108:W2:A8:S14→Xi108:W1:A7:S14→Xi108:W1:A9:S14

"""4 overlay registries (lens, alchemy, animal, completion) and Sigma-15."""

from ._cache import JsonCache
from .registry_sources import query_registry, _catalog

_overlays = JsonCache("overlay_registries.json")

def _legacy_query_overlay(data: dict, registry: str, index: int = 0) -> str:
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

def _legacy_query_sigma15(data: dict, sigma: int) -> str:
    """
    Get a Sigma-15 lens combination by mask index (1-15).

    The 15 nonempty subsets of {S, F, C, R} form the observation field.
    Sigma-15 x 4 quadrants = Sigma-60 (the full 5D transform field).

    Mask 15 (SFCR) = complete local pattern / local aether.
    """
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


def query_overlay(registry: str, index: int = 0) -> str:
    """Read the current catalog or explicit archive:<registry>; index is 1-based."""
    if type(index) is not int or index < 0:
        return 'Invalid overlay index: expected a nonnegative integer.'
    def render(data, component):
        if index and component.lower() in ('all', 'overview'):
            return 'HOLD: an entry index requires a specific overlay registry.'
        return _legacy_query_overlay(data, component, index)
    def catalog(data, component):
        if index:
            return 'HOLD: current overlay catalog has no legacy registry-entry index mapping.'
        return _catalog('overlay_registries.json', data, component)
    return query_registry('overlay_registries.json', _overlays, registry, render, catalog)


def query_sigma15(sigma: int, source: str = 'json') -> str:
    """Read a descriptive Sigma mask; source='archive' explicitly selects reviewed QSHR."""
    if type(sigma) is not int or not 1 <= sigma <= 15:
        return 'Invalid Sigma index: expected integer 1-15.'
    if source not in ('json', 'archive'):
        return 'Invalid source: expected json or archive.'
    selector = 'archive:all' if source == 'archive' else f'mask:{sigma}'
    return query_registry('overlay_registries.json', _overlays, selector,
                          lambda data, component: _legacy_query_sigma15(data, sigma))
