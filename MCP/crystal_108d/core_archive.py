"""Explicit pinned archive descriptions and a clock MODEL, never runtime proof."""
import struct
import zlib
from . import registry_sources


def render_core_archive(filename, renderer, selector):
    """Read one fixed allowlisted source; canonical JsonCache is never consulted."""
    if filename == "clock_projections.json":
        if type(selector) is not int:
            return "Invalid archive model beat: expected an integer."
    elif filename == "shell_registry.json":
        from .shells import _index
        if _index(selector, 12) is None:
            return "Invalid archive archetype. Use 1-12."
    elif filename == "dimensional_ladder.json":
        if type(selector) is not int or not 3 <= selector <= 108:
            return "Invalid archive dimension: expected integer 3-108."
    elif not isinstance(selector, str) or not selector.strip() or len(selector) > 4096:
        return "Invalid archive selector: expected bounded nonempty text."
    if filename == "move_primitives.json" and selector.strip().lower() not in ("list", "help", "primitives"):
        return "HOLD: archive move descriptions do not establish measured route legality; no certificate is issued."
    if filename == "conservation_laws.json" and selector.strip().lower() not in ("list", "help", "laws"):
        return ("HOLD: conservation requires all measured inputs, including archetype_shifts, "
                "closed-path witness, state and replay hashes. Archive laws are descriptive; no certificate is issued.")
    try:
        data, provenance = registry_sources.load_archive(filename)
        body = renderer(data)
        evidence = "MODEL" if filename == "clock_projections.json" else "ARCHIVE_DESCRIPTION"
        return (f"**Evidence class**: {evidence}; explicit archive namespace.\n"
                + body + "\n\n" + provenance
                + "HOLD: archive integrity and formulas are not measured state, liveness, execution, round-trip or conservation proof. "
                "Source instructions are descriptive only; no runtime certificate is issued.\n")
    except (OSError, KeyError, TypeError, ValueError, AttributeError, IndexError, RecursionError, struct.error, zlib.error) as exc:
        return f"HOLD: explicit core archive is unavailable, malformed or conflicts with its pin ({exc})."
