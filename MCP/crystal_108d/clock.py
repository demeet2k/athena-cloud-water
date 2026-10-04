# CRYSTAL: Xi108:W2:A11:S11 | face=C | node=63 | depth=2 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W2:A11:S10→Xi108:W2:A11:S12→Xi108:W1:A11:S11→Xi108:W3:A11:S11→Xi108:W2:A10:S11→Xi108:W2:A12:S11

"""420-beat master clock and projection logic."""

import hashlib
import json
import re
from ._cache import DATA_DIR, JsonCache

_clock = JsonCache("clock_projections.json")

MAX_CURRENT_CLOCK_BYTES = 65536


def _unique_clock_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate source field: {key}")
        result[key] = value
    return result


def _current_clock_catalog(beat):
    """Fresh bounded current JSON read; IDs and hours are not execution beats."""
    try:
        path = DATA_DIR / "clock_projections.json"
        with path.open("rb") as stream:
            raw = stream.read(MAX_CURRENT_CLOCK_BYTES + 1)
        if len(raw) > MAX_CURRENT_CLOCK_BYTES:
            raise ValueError("current clock catalog exceeds supported size")
        data = json.loads(raw, object_pairs_hook=_unique_clock_fields)
        if not isinstance(data, dict) or set(data) != {"meta", "clocks", "containment", "master_period_days"}:
            raise ValueError("current clock catalog root signature is unsupported")
        if data["meta"] != {"type": "clock_projections", "version": "2.0"}:
            raise ValueError("current clock source family/version conflicts")
        clocks = data["clocks"]
        if not isinstance(clocks, dict) or not clocks:
            raise ValueError("source clock catalog must be a nonempty object")
        for identity, record in clocks.items():
            if not isinstance(identity, str) or re.fullmatch(r"Z[1-9][0-9]{0,5}", identity) is None:
                raise ValueError("source clock identity is unsupported")
            if not isinstance(record, dict) or set(record) != {"period_hours", "strands", "wreath", "weave"}:
                raise ValueError("source clock record signature is unsupported")
            if any(type(record[key]) is not int or record[key] < 1 for key in ("period_hours", "strands")):
                raise ValueError("clock period_hours and strands must be positive integers")
            if any(not isinstance(record[key], str) or not record[key].strip() for key in ("wreath", "weave")):
                raise ValueError("clock wreath and weave descriptions must be nonempty text")
        if (not isinstance(data["containment"], str) or not data["containment"].strip()
                or type(data["master_period_days"]) is not int or data["master_period_days"] < 1):
            raise ValueError("source containment and master period declarations are invalid")
        lines = [f"## Current Clock Catalog (requested Beat {beat})",
                 "Source IDs and period_hours are catalog declarations; no execution beat mapping is supplied."]
        for identity, record in clocks.items():
            lines += [f"### {identity}", f"- Period: {record['period_hours']} hours",
                      f"- Strands: {record['strands']}", f"- Wreath: {record['wreath']}",
                      f"- Weave: {record['weave']}"]
        lines += [f"**Source-declared containment**: `{data['containment']}`",
                  f"**Source-declared master period**: {data['master_period_days']} days",
                  f"**Source Selection**: current JSON `{path.name}`",
                  f"**Catalog Snapshot SHA256**: `{hashlib.sha256(raw).hexdigest()}`",
                  "HOLD: current source supplies no beat origin/mapping, projection phases, visible-shell law or execution gate state. "
                  "Containment text is source-declared, not a verified timing identity. Use explicit archive only for the historical MODEL; no runtime certificate is issued."]
        return "\n".join(lines) + "\n"
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        return f"HOLD: current clock source is unavailable, malformed or conflicts with its catalog contract ({exc})."


def query_clock_beat(beat: int, source: str = "current") -> str:
    """Read the current clock IDs, hour periods and descriptive catalog.

    Current JSON does not define execution beat mapping or projection state;
    those requests HOLD. Source='archive' selects the explicit archive
    historical 420-beat MODEL, never a live execution gate or certificate.
    """
    if source == "archive":
        from .core_archive import render_core_archive
        return render_core_archive("clock_projections.json", lambda data: _render_archive_clock(data, beat), beat)
    if source != "current":
        return "HOLD: source must be current or explicit archive."
    if type(beat) is not int:
        return "Invalid current clock beat: expected an integer; no execution mapping is supplied."
    return _current_clock_catalog(beat)


def _render_archive_clock(data: dict, beat: int) -> str:
    """
    Get the projection state at any beat of the 420-beat master clock.

    Returns: which projection phase is active for each wheel (3D/4D/5D/7D),
    visible shells, and edge-window state.

    Beat range: 0-419 (wraps via modulo).
    """
    supercycle_position = beat % 1260
    beat = beat % 420  # Master-cycle position

    projections = data["projections"]

    # 3D current wheel (period 140)
    tau3 = projections["tau_3"]
    tau3_phase = None
    for phase in tau3["phases"]:
        if phase["beat_range"][0] <= beat <= phase["beat_range"][1]:
            tau3_phase = phase
            break

    # 4D barycentric (period 105)
    b4 = projections["b_4"]
    b4_quadrant = beat % 105
    b4_face_idx = min(beat // 105, 3)
    b4_face = b4["faces"][b4_face_idx]

    # 5D tilt (period 84)
    tau5 = projections["tau_5"]
    tau5_segment_idx = min(beat // 84, 4)
    tau5_animal = tau5["segments"][tau5_segment_idx]

    # 7D timing (period 60)
    tau7 = projections["tau_7"]
    tau7_gate_idx = min(beat // 60, 6)
    tau7_gate = tau7["gates"][tau7_gate_idx]

    # Visible shells (approximate)
    visible_shells = beat * 36 // 420

    # Edge window (simplified: open when all projections align at boundaries)
    is_boundary = (beat % 60 == 0) and (beat % 84 == 0) and (beat % 105 == 0) and (beat % 140 == 0)

    lines = [
        f"## Archive Clock MODEL at Beat {beat}/420\n",
        f"### 3D Current Wheel (τ₃, period 140)",
        f"- Current: **{tau3_phase['current']}** ({tau3_phase['function']})",
        f"- Phase range: beats {tau3_phase['beat_range'][0]}-{tau3_phase['beat_range'][1]}",
        f"",
        f"### 4D Barycentric Tilt (b₄, period 105)",
        f"- Face: **{b4_face}**",
        f"- Quadrant position: {b4_quadrant}/105",
        f"",
        f"### 5D Tilt/Gear Wheel (τ₅, period 84)",
        f"- Animal: **{tau5_animal}**",
        f"- Segment: {tau5_segment_idx + 1}/5",
        f"",
        f"### 7D Timing Wheel (τ₇, period 60)",
        f"- Gate: **{tau7_gate}**",
        f"- Gate index: {tau7_gate_idx + 1}/7",
        f"",
        f"### Summary",
        f"- Visible shells: {visible_shells}/36",
        f"- Model boundary intersection: {'**OPEN**' if is_boundary else 'closed'}",
        f"- Supercycle position: {supercycle_position}/1260",
        f"- Crown reset in: {420 - beat} beats",
    ]
    return "\n".join(lines) + "\nMODEL: boundary alignment only; no live execution gate state is measured.\n"
