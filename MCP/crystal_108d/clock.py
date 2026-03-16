"""420-beat master clock and projection logic."""

from ._cache import JsonCache

_clock = JsonCache("clock_projections.json")


def query_clock_beat(beat: int) -> str:
    """
    Get the projection state at any beat of the 420-beat master clock.

    Returns: which projection phase is active for each wheel (3D/4D/5D/7D),
    visible shells, and edge-window state.

    Beat range: 0-419 (wraps via modulo).
    """
    data = _clock.load()
    beat = beat % 420  # Wrap around

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
    visible_shells = max(1, int(beat * 36 / 420))

    # Edge window (simplified: open when all projections align at boundaries)
    is_boundary = (beat % 60 == 0) or (beat % 84 == 0) or (beat % 105 == 0) or (beat % 140 == 0)

    lines = [
        f"## Clock State at Beat {beat}/420\n",
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
        f"- Visible shells: ~{visible_shells}/36",
        f"- Edge window: {'**OPEN**' if is_boundary else 'closed'}",
        f"- Supercycle position: {beat % 1260}/1260",
        f"- Crown reset in: {420 - beat} beats",
    ]
    return "\n".join(lines) + "\n"
