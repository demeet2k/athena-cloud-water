"""6 conservation laws and motion checking."""

import json

from ._cache import JsonCache

_laws = JsonCache("conservation_laws.json")


def query_conservation(motion_json: str) -> str:
    """
    Check the 6 conservation laws against a proposed motion, or list all laws.

    Pass 'list' to see all 6 laws and round-trip classes.

    For checking, pass JSON: {"shell_deltas": [1,-1], "wreath_rotations": [1,1,1],
    "face_shifts": [1,1,1,1], "mobius_flips": 2, "zoom_deltas": [1,-1]}
    """
    data = _laws.load()

    if motion_json.strip().lower() in ("list", "help", "laws"):
        lines = ["## 6 Conservation Laws\n"]
        lines.append(f"**Master**: `{data['meta']['master_invariant']}`\n")
        for law in data["laws"]:
            lines.append(
                f"### {law['index']}. {law['name']} ({law['symbol']})\n"
                f"- Statement: {law['statement']}\n"
                f"- {law['description']}\n"
                f"- Symmetry: {law['symmetry_group']}\n"
                f"- Noether charge: {law['noether_charge']}\n"
                f"- Check: `{law['check_rule']}`\n"
            )
        lines.append("## Round-Trip Classes\n")
        for rtc in data["round_trip_classes"]:
            lines.append(f"- **{rtc['class']}**: {rtc['meaning']}")
        lines.append("\n## Illegal Loss Tests\n")
        for test in data["illegal_loss_tests"]:
            lines.append(f"- {test}")
        return "\n".join(lines) + "\n"

    # Parse motion
    try:
        motion = json.loads(motion_json)
    except json.JSONDecodeError:
        return (
            "Invalid JSON. Expected:\n"
            '{"shell_deltas": [...], "wreath_rotations": [...], '
            '"face_shifts": [...], "mobius_flips": N, "zoom_deltas": [...]}'
        )

    results = []
    all_pass = True

    # Law 1: Shell
    shell_net = sum(motion.get("shell_deltas", []))
    if shell_net == 0:
        results.append("1. Shell Conservation: ✓ PASS (net Δl = 0)")
    else:
        results.append(f"1. Shell Conservation: ✗ FAIL (net Δl = {shell_net})")
        all_pass = False

    # Law 2: Zoom
    zoom_net = sum(motion.get("zoom_deltas", []))
    if zoom_net == 0:
        results.append("2. Zoom Conservation: ✓ PASS (net Δσ = 0)")
    else:
        results.append(f"2. Zoom Conservation: ✗ FAIL (net Δσ = {zoom_net})")
        all_pass = False

    # Law 3: Phase
    wreath_net = sum(motion.get("wreath_rotations", []))
    if wreath_net % 3 == 0:
        results.append(f"3. Phase Conservation: ✓ PASS (Δr = {wreath_net} ≡ 0 mod 3)")
    else:
        results.append(f"3. Phase Conservation: ✗ FAIL (Δr = {wreath_net} ≢ 0 mod 3)")
        all_pass = False

    # Law 4: Archetype
    arch_net = sum(motion.get("archetype_shifts", []))
    if arch_net % 12 == 0:
        results.append(f"4. Archetype Conservation: ✓ PASS (Δa = {arch_net} ≡ 0 mod 12)")
    else:
        results.append(f"4. Archetype Conservation: ✗ FAIL (Δa = {arch_net} ≢ 0 mod 12)")
        all_pass = False

    # Law 5: Face
    face_net = sum(motion.get("face_shifts", []))
    if face_net % 4 == 0:
        results.append(f"5. Face Conservation: ✓ PASS (Δλ = {face_net} ≡ 0 mod 4)")
    else:
        results.append(f"5. Face Conservation: ✗ FAIL (Δλ = {face_net} ≢ 0 mod 4)")
        all_pass = False

    # Law 6: Mobius
    flips = motion.get("mobius_flips", 0)
    if flips % 2 == 0:
        results.append(f"6. Mobius Conservation: ✓ PASS ({flips} flips, even)")
    else:
        results.append(f"6. Mobius Conservation: ✗ FAIL ({flips} flips, odd)")
        all_pass = False

    # Determine class
    if all_pass:
        cert_class = "exact"
    elif sum(1 for r in results if "FAIL" in r) <= 1:
        cert_class = "law_equivalent (minor deviation)"
    else:
        cert_class = "residualized or illegal (multiple violations)"

    return (
        f"## Conservation Law Check\n\n"
        + "\n".join(results)
        + f"\n\n**Overall**: {'ALL PASS ✓' if all_pass else 'VIOLATIONS DETECTED ✗'}\n"
        f"**Cert Class**: {cert_class}\n"
    )
