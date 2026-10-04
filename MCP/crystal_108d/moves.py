# CRYSTAL: Xi108:W2:A11:S11 | face=C | node=57 | depth=2 | phase=Fixed
# METRO: Me
# BRIDGES: Xi108:W2:A11:S10→Xi108:W2:A11:S12→Xi108:W1:A11:S11→Xi108:W3:A11:S11→Xi108:W2:A10:S11→Xi108:W2:A12:S11

"""10 legal move primitives and route legality checker."""

import json

from ._cache import JsonCache

_moves = JsonCache("move_primitives.json")

def check_route_legality(route_json: str) -> str:
    """
    Check a proposed route against the 3 legality invariants and 10 move primitives.

    Input: JSON string describing the route as a list of moves.
    Each move should have: {"type": "STEP_SHELL|ROTATE_WREATH|...", "from": ..., "to": ...}

    Or pass "list" to see all 10 primitives and 3 invariants.
    """
    data = _moves.load()
    if data.get("meta", {}).get("version") == "2.0" and "invariants" not in data:
        if route_json.strip().lower() in ("list", "help", "primitives"):
            return "## Move Primitives\n\n" + "\n\n".join(
                f"### {p['id']}: {p['name']}\n{p['notation']}\n{p['description']}"
                for p in data["primitives"]
            ) + "\nHOLD: executable conservation and legality predicates are absent.\n"
        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            return "Invalid JSON. Expected a nonempty list of move objects."
        if isinstance(route, dict):
            route = [route]
        if not isinstance(route, list) or not route or any(not isinstance(move, dict) for move in route):
            return "INVALID: expected a nonempty list of move objects."
        known = {p['id']: p for p in data["primitives"]}
        known.update({p['name']: p for p in data["primitives"]})
        lines = [f"## Route Legality Check ({len(route)} moves)"]
        for i, move in enumerate(route, 1):
            identity = move.get("type")
            primitive = known.get(identity) if isinstance(identity, str) else None
            if primitive is None:
                lines.append(f"Move {i}: INVALID undeclared primitive {identity!r}")
            else:
                lines.append(f"Move {i}: declared {primitive['id']} - {primitive['name']}")
        lines.append("HOLD: declared primitive membership does not prove route legality. "
                     "Conservation, nested consistency and returnability predicates are absent; no legality certificate is issued.")
        return "\n".join(lines) + "\n"

    if route_json.strip().lower() in ("list", "help", "primitives"):
        lines = ["## Legal Move Primitives\n"]
        for p in data["primitives"]:
            lines.append(
                f"### {p['index']}. {p['name']} ({p['type']})\n"
                f"{p['description']}\n"
                f"- Delta: {json.dumps(p['address_delta'])}\n"
                f"- Conservation check: {p['conservation_check']}\n"
                f"- Example: {p['example']}\n"
            )
        lines.append("## Legality Invariants\n")
        for inv in data["invariants"]:
            lines.append(
                f"### {inv['name']}\n"
                f"- **Law**: {inv['law']}\n"
                f"- {inv['description']}\n"
                f"- **Check**: {inv['check']}\n"
            )
        return "\n".join(lines)

    # Parse route
    try:
        route = json.loads(route_json)
    except json.JSONDecodeError:
        return (
            "Invalid JSON. Expected a list of moves:\n"
            '[{"type": "STEP_SHELL", "from": 5, "to": 6}, ...]'
        )

    if not isinstance(route, list):
        route = [route]

    if not route or any(not isinstance(move, dict) for move in route):
        return "INVALID: expected a nonempty list of move objects."

    # Validate each move
    valid_types = {p["name"] for p in data["primitives"]}
    results = []
    shell_deltas = []
    face_shifts = []
    wreath_rotations = []
    mobius_flips = 0
    zoom_deltas = []

    for i, move in enumerate(route):
        move_type = move.get("type", "UNKNOWN")
        if not isinstance(move_type, str) or move_type not in valid_types:
            results.append(f"Move {i+1}: **INVALID** type '{move_type}'")
        else:
            results.append(f"Move {i+1}: {move_type} ✓")
            # Track deltas for conservation checking
            if move_type == "STEP_SHELL":
                shell_deltas.append(move.get("delta", 1))
            elif move_type == "ROTATE_WREATH":
                wreath_rotations.append(1)
            elif move_type == "SWITCH_FACE":
                face_shifts.append(1)
            elif move_type == "FLIP_MOBIUS":
                mobius_flips += 1
            elif move_type in ("ZOOM_IN", "ZOOM_OUT"):
                zoom_deltas.append(1 if move_type == "ZOOM_IN" else -1)

    # Check invariants
    invariant_results = []

    # Zero-factorability (simplified: check if route starts/ends at same place)
    starts = route[0].get("from", "?") if route else "?"
    ends = route[-1].get("to", "?") if route else "?"
    all_types_valid = all(isinstance(m.get("type"), str) and m["type"] in valid_types for m in route)
    explicit_endpoints = all(m.get("from") not in (None, "?") and m.get("to") not in (None, "?") for m in route)
    continuous = all(left.get("to") == right.get("from") for left, right in zip(route, route[1:]))
    zf_pass = (all_types_valid and explicit_endpoints and continuous and starts not in (None, "?")
               and ends not in (None, "?") and starts == ends)
    invariant_results.append(
        f"- Zero-factorability: {'✓ PASS' if zf_pass else '⚠ UNVERIFIED (route may not return to Z*)'}"
    )

    # Primitive membership cannot attest containment at intermediate addresses.
    invariant_results.append("- Nested consistency: HOLD (containment proof not supplied)")

    # A closed endpoint is not a proof of reversibility under a live helm.
    invariant_results.append("- Global returnability: HOLD (reverse path proof not supplied)")

    # Conservation check
    conservation = []
    if sum(shell_deltas) != 0:
        conservation.append(f"- Shell: ⚠ net delta = {sum(shell_deltas)}")
    else:
        conservation.append("- Shell: ✓")
    if sum(zoom_deltas) != 0:
        conservation.append(f"- Zoom: ⚠ net delta = {sum(zoom_deltas)}")
    else:
        conservation.append("- Zoom: ✓")
    if sum(wreath_rotations) % 3 != 0:
        conservation.append(f"- Phase: ⚠ net rotations = {sum(wreath_rotations)} (not mod 3)")
    else:
        conservation.append("- Phase: ✓")
    if sum(face_shifts) % 4 != 0:
        conservation.append(f"- Face: ⚠ net shifts = {sum(face_shifts)} (not mod 4)")
    else:
        conservation.append("- Face: ✓")
    if mobius_flips % 2 != 0:
        conservation.append(f"- Mobius: ⚠ odd flips = {mobius_flips}")
    else:
        conservation.append("- Mobius: ✓")

    return (
        f"## Route Legality Check ({len(route)} moves)\n\n"
        "### Move Validation\n"
        + "\n".join(results)
        + "\n\n### Invariants\n"
        + "\n".join(invariant_results)
        + "\n\n### Conservation Laws\n"
        + "\n".join(conservation)
        + "\n"
    )
