# CRYSTAL: Xi108:W1:A10:S4 | face=F | node=8 | depth=0 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W1:A10:S3→Xi108:W1:A10:S5→Xi108:W2:A10:S4→Xi108:W1:A9:S4→Xi108:W1:A11:S4

"""6 conservation laws and motion checking."""

import json

from ._cache import JsonCache

_laws = JsonCache("conservation_laws.json")


def _v2_law_report(data):
    try:
        laws = data['laws']
        if not isinstance(laws, list) or {law['id'] for law in laws} != {f'CL{i}' for i in range(1, 7)} or len(laws) != 6:
            raise ValueError('six unique source law IDs are required')
        lines = ['## Conservation Laws (source descriptions)']
        for law in laws:
            if not all(isinstance(law[key], str) and law[key].strip() for key in ('id', 'name', 'statement', 'invariant')):
                raise ValueError('law descriptions must be nonempty strings')
            lines += [f"### {law['id']}: {law['name']}", f"- Statement: {law['statement']}",
                      f"- Source Invariant: `{law['invariant']}`"]
        frequency = data['verification_frequency']
        if not isinstance(frequency, str) or not frequency.strip():
            raise ValueError('verification frequency description is missing')
        lines += [f'**Declared Verification Frequency**: {frequency}',
                  'HOLD: descriptions supply no executable evaluator, measured state or proof. Legacy delta/parity checks do not verify these v2 invariants.']
        return '\n'.join(lines) + '\n'
    except (KeyError, TypeError, ValueError) as exc:
        return f'HOLD: conservation registry has missing or conflicting source fields ({exc}).'


def _motion_error(motion):
    if not isinstance(motion, dict) or not motion:
        return 'Invalid motion: expected a nonempty JSON object with explicit measurements.'
    return None


def _legacy_motion_error(motion):
    fields = ('shell_deltas', 'zoom_deltas', 'wreath_rotations', 'archetype_shifts', 'face_shifts')
    for field in fields:
        values = motion.get(field)
        if not isinstance(values, list) or not values:
            return f'Invalid motion: {field} must be an explicit nonempty numeric list.'
        if any(type(v) is not int for v in values):
            return f'Invalid motion: {field} requires integer deltas (booleans and fractional or nonfinite values are invalid).'
    flips = motion.get('mobius_flips')
    if type(flips) is not int or flips < 0:
        return 'Invalid motion: mobius_flips must be an explicit nonnegative integer.'
    return None


def query_conservation(motion_json: str) -> str:
    """
    Read conservation laws, or check explicit supported legacy-v1 measurements.

    The v2 catalog is descriptive; motion evaluation returns HOLD without an evaluator.

    Pass 'list' to see source laws (legacy registries also declare round-trip classes).

    For checking, pass JSON: {"shell_deltas": [1,-1], "wreath_rotations": [1,1,1],
    "face_shifts": [1,1,1,1], "archetype_shifts": [0],
    "mobius_flips": 2, "zoom_deltas": [1,-1]}
    """
    try:
        data = _laws.load()
    except (OSError, ValueError, TypeError) as exc:
        return f'HOLD: conservation source is unavailable or unreadable ({exc}).'
    if not isinstance(data, dict) or not isinstance(data.get('meta'), dict):
        return 'HOLD: conservation source requires a registry object and metadata object.'

    if not isinstance(motion_json, str) or not motion_json.strip():
        return 'Invalid motion: expected JSON text or list/help/laws.'
    listing = motion_json.strip().lower() in ('list', 'help', 'laws')
    meta = data.get('meta')
    v2 = (not isinstance(meta, dict) or meta.get('version') == '2.0'
          or (isinstance(data.get('laws'), list)
              and any(isinstance(law, dict) and 'id' in law for law in data['laws'])))
    if listing and v2:
        return _v2_law_report(data)
    if listing:
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
            '"archetype_shifts": [...], "face_shifts": [...], '
            '"mobius_flips": N, "zoom_deltas": [...]}'
        )

    error = _motion_error(motion)
    if error:
        return error
    if v2:
        return _v2_law_report(data)
    if meta.get('version') != '1.0':
        return 'HOLD: no supported legacy conservation version is declared.'
    # Do not apply the archived predicates to an unknown or incomplete registry.
    try:
        laws = data['laws']
        if (not isinstance(laws, list) or len(laws) != 6
                or any(type(law['index']) is not int for law in laws)
                or {law['index'] for law in laws} != set(range(1, 7))
                or not all(isinstance(law['check_rule'], str) and law['check_rule'].strip() for law in laws)
                or not isinstance(data['meta']['master_invariant'], str)):
            return 'HOLD: legacy conservation predicate registry is incomplete or unknown.'
    except (KeyError, TypeError):
        return 'HOLD: legacy conservation predicate registry is incomplete or unknown.'
    error = _legacy_motion_error(motion)
    if error:
        return error

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
