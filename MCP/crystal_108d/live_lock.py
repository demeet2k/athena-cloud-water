# CRYSTAL: Xi108:W1:A4:S8 | face=R | node=36 | depth=0 | phase=Fixed
# METRO: T
# BRIDGES: Xi108:W1:A4:S7→Xi108:W1:A4:S9→Xi108:W2:A4:S8→Xi108:W1:A3:S8→Xi108:W1:A5:S8

"""7-class live-lock lattice."""

import math

from ._cache import JsonCache

_locks = JsonCache("live_lock_registry.json")

def compute_live_lock(address_a: str, address_b: str) -> str:
    """
    Find the nearest common live-lock between two addresses or shell numbers.

    The nearest common live-lock is the minimal lock class that satisfies
    all active helm constraints for both addresses.

    Input: shell numbers (e.g. "5", "28") or lock class codes (e.g. "L3", "L57").
    """
    data = _locks.load()
    if "classes" not in data:
        if "locks" in data:
            return (
                "HOLD: current registry tracks active locks; it has no live-lock class lattice.\n"
                f"Active locks: {len(data['locks'])}\n"
                f"Max concurrent: {data['max_concurrent']}\n"
                f"Timeout seconds: {data['timeout_seconds']}\n"
                "No common class computed and no lock acquired.\n"
            )
        return "HOLD: live-lock registry contains no supported schema.\n"
    classes = data["classes"]

    # Parse inputs — accept shell numbers or lock codes
    def _resolve_lock(addr: str) -> set[int]:
        addr = addr.strip().upper()
        # If it's a lock code
        for lc in classes:
            if addr == lc["code"].upper():
                return set(lc["divisors"])
        # If it's a shell number, derive required divisors
        if addr.isdigit():
            shell = int(addr)
            divisors = set()
            if shell % 3 == 0:
                divisors.add(3)
            if shell % 5 == 0:
                divisors.add(5)
            if shell % 7 == 0:
                divisors.add(7)
            if not divisors:
                divisors.add(3)  # Default to L3
            return divisors
        return {3}  # Default

    divs_a = _resolve_lock(address_a)
    divs_b = _resolve_lock(address_b)

    # Common lock = union of required divisors
    common_divs = divs_a | divs_b
    common_divs_sorted = sorted(common_divs)

    # Find matching class
    matched = None
    for lc in classes:
        if set(lc["divisors"]) == common_divs:
            matched = lc
            break

    if not matched:
        # Find minimal containing class
        for lc in sorted(classes, key=lambda x: len(x["divisors"])):
            if common_divs.issubset(set(lc["divisors"])):
                matched = lc
                break

    if not matched:
        matched = classes[-1]  # L357 as fallback

    return (
        f"## Nearest Common Live-Lock\n\n"
        f"- **Address A**: {address_a} → divisors {divs_a}\n"
        f"- **Address B**: {address_b} → divisors {divs_b}\n"
        f"- **Common Lock**: **{matched['code']}**\n"
        f"- **Helm**: {matched['helm']}\n"
        f"- **Period**: {matched['period']} beats\n"
        f"- **Description**: {matched['description']}\n"
        f"- **Resonance Band**: {matched['resonance_band']}\n"
    )
