"""Explicit authenticated core archive routes, clock MODEL and HOLD boundaries."""
import functools
from pathlib import Path
import pytest
import test_tools as original_tests
from crystal_108d import clock, conservation, dimensions, emergence, moves, organs, shells, stage_codes
from crystal_108d import registry_sources

TOOLS = {
    "query_archetype": shells.query_archetype,
    "query_containment": dimensions.query_containment,
    "query_organ": organs.query_organ,
    "check_route_legality": moves.check_route_legality,
    "query_stage_code": stage_codes.query_stage_code,
    "query_emergence": emergence.query_emergence,
    "query_clock_beat": clock.query_clock_beat,
    "query_conservation": conservation.query_conservation,
}

# Reuse all 14 reviewed existing assertions unchanged, selecting real pinned assets.
@pytest.mark.parametrize("class_name,test_name", [
    ("TestShellTools", "test_query_archetype"),
    ("TestDimensionTools", "test_query_containment"),
    ("TestOrganTool", "test_query_by_dyad_index"),
    ("TestOrganTool", "test_query_crown_closure"),
    ("TestMovesTool", "test_list_primitives"),
    ("TestStageCodeTool", "test_specific"),
    ("TestStageCodeTool", "test_s12"),
    ("TestStageCodeTool", "test_zeros"),
    ("TestEmergenceTool", "test_phase_by_name"),
    ("TestEmergenceTool", "test_lenses"),
    ("TestEmergenceTool", "test_lens_at"),
    ("TestEmergenceTool", "test_bodies"),
    ("TestClockTool", "test_beat_0"),
    ("TestClockTool", "test_beat_210"),
])
def test_original_assertions_on_explicit_archive(monkeypatch, class_name, test_name):
    for name, fn in TOOLS.items():
        monkeypatch.setattr(original_tests, name, functools.partial(fn, source="archive"))
    getattr(getattr(original_tests, class_name)(), test_name)()

@pytest.mark.parametrize("fn,selector", [
    (shells.query_archetype, 1), (dimensions.query_containment, 12),
    (organs.query_organ, "1"), (moves.check_route_legality, "list"),
    (stage_codes.query_stage_code, "S12"), (emergence.query_emergence, "lens:6D"),
    (clock.query_clock_beat, 0), (conservation.query_conservation, "laws"),
])
def test_archive_provenance_and_no_runtime_certificate(fn, selector):
    result = fn(selector, source="archive")
    assert "explicit archive namespace" in result
    assert registry_sources.PINNED_COMMIT in result
    assert "Archive SHA256" in result and "Decoded Payload SHA256" in result
    assert "HOLD:" in result and "no runtime certificate is issued" in result

@pytest.mark.parametrize("beat", [0, 60, 84, 105, 140, 210, 419, 420, 840, 1259, 1260, -1])
def test_clock_model_floor_intersection_and_supercycle(beat):
    result = clock.query_clock_beat(beat, source="archive")
    master = beat % 420
    assert f"Visible shells: {master * 36 // 420}/36" in result
    expected = "**OPEN**" if all(master % period == 0 for period in (60, 84, 105, 140)) else "closed"
    assert f"Model boundary intersection: {expected}" in result
    assert f"Supercycle position: {beat % 1260}/1260" in result
    assert "MODEL" in result and "no live execution gate state is measured" in result

@pytest.mark.parametrize("beat", [True, 1.5, "420", None])
def test_clock_invalid_types_hold_before_source_read(monkeypatch, beat):
    monkeypatch.setattr(registry_sources, "load_archive", lambda _: pytest.fail("invalid selector read source"))
    assert "Invalid" in clock.query_clock_beat(beat, source="archive")

@pytest.mark.parametrize("motion", ["{}", '{"shell_deltas":[1,-1]}',
    '{"shell_deltas":[],"wreath_rotations":[],"face_shifts":[],"archetype_shifts":[],"mobius_flips":0,"zoom_deltas":[]}'])
def test_archive_conservation_never_certifies_motion(motion):
    result = conservation.query_conservation(motion, source="archive")
    assert result.startswith("HOLD:") and "no certificate" in result
    assert "state and replay hashes" in result
    assert "PASS" not in result and "CONSERVED" not in result


def test_archive_does_not_run_route_checker():
    result = moves.check_route_legality('[{"type":"STEP_SHELL","from":1,"to":1}]', source="archive")
    assert result.startswith("HOLD:") and "no certificate" in result


def test_missing_and_tampered_archive_hold(monkeypatch, tmp_path):
    original = registry_sources.DATA_DIR
    monkeypatch.setattr(registry_sources, "DATA_DIR", tmp_path)
    assert shells.query_archetype(1, source="archive").startswith("HOLD:")
    source = original / "shell_registry.qshr"
    blob = bytearray(source.read_bytes())
    blob[-1] ^= 1
    (tmp_path / source.name).write_bytes(blob)
    result = shells.query_archetype(1, source="archive")
    assert result.startswith("HOLD:") and "hash" in result


def test_current_selectors_never_use_archive(monkeypatch):
    monkeypatch.setattr(registry_sources, "load_archive", lambda _: pytest.fail("implicit archive selection"))
    for fn, selector in [(shells.query_archetype, 1), (dimensions.query_containment, 12),
                         (organs.query_organ, "1"), (moves.check_route_legality, "list"),
                         (stage_codes.query_stage_code, "S12"), (emergence.query_emergence, "lens:6D"),
                         (clock.query_clock_beat, 0), (conservation.query_conservation, "laws")]:
        assert "explicit archive namespace" not in fn(selector)


def test_current_clock_reads_actual_catalog_and_holds_missing_model():
    import hashlib
    raw = (clock.DATA_DIR / "clock_projections.json").read_bytes()
    result = clock.query_clock_beat(420)
    for identity, period in [("Z12", 4), ("Z20", 20), ("Z28", 168), ("Z36", 720), ("Z420", 2160)]:
        assert f"### {identity}" in result
        assert f"Period: {period} hours" in result
    assert "Beat 420" in result
    assert "90 days" in result
    assert hashlib.sha256(raw).hexdigest() in result
    assert "HOLD:" in result and "no beat origin/mapping" in result
    assert "not a verified timing identity" in result
    assert "Visible shells:" not in result and "OPEN" not in result
    assert "Supercycle position:" not in result
    assert "Archive Clock MODEL" not in result


@pytest.mark.parametrize("mutation", [
    lambda d: d["meta"].update(type="foreign_clock"),
    lambda d: d["meta"].update(version="3.0"),
    lambda d: d["clocks"]["Z12"].update(period_hours=True),
    lambda d: d["clocks"]["Z12"].update(period_hours=0),
    lambda d: d["clocks"]["Z12"].update(strands=1.5),
    lambda d: d["clocks"]["Z12"].update(weave=""),
    lambda d: d.update(master_period_days=False),
    lambda d: d["clocks"].update(foreign=d["clocks"]["Z12"]),
])
def test_current_clock_rejects_wrong_namespace_and_field_types(monkeypatch, tmp_path, mutation):
    import json
    data = json.loads((clock.DATA_DIR / "clock_projections.json").read_bytes())
    mutation(data)
    (tmp_path / "clock_projections.json").write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(clock, "DATA_DIR", tmp_path)
    assert clock.query_clock_beat(0).startswith("HOLD:")


def test_current_clock_missing_oversized_and_duplicate_sources_hold(monkeypatch, tmp_path):
    monkeypatch.setattr(clock, "DATA_DIR", tmp_path)
    assert clock.query_clock_beat(0).startswith("HOLD:")
    path = tmp_path / "clock_projections.json"
    path.write_bytes(b" " * (clock.MAX_CURRENT_CLOCK_BYTES + 1))
    assert "exceeds" in clock.query_clock_beat(0)
    path.write_text('{"meta":{},"meta":{}}', encoding="utf-8")
    assert "duplicate" in clock.query_clock_beat(0)


@pytest.mark.parametrize("beat", [True, 1.5, "0", None])
def test_current_clock_rejects_invalid_beat_types(beat):
    assert "Invalid" in clock.query_clock_beat(beat)


@pytest.mark.parametrize("fn,selector", [(shells.query_archetype, 1), (clock.query_clock_beat, 0),
                                          (stage_codes.query_stage_code, "S12")])
def test_wrong_source_namespace_never_falls_back(fn, selector):
    assert fn(selector, source="archive:../../x").startswith("HOLD:")


@pytest.mark.parametrize("fn,selector", [
    (shells.query_archetype, 1), (dimensions.query_containment, 12),
    (organs.query_organ, "1"), (moves.check_route_legality, "list"),
    (stage_codes.query_stage_code, "S12"), (emergence.query_emergence, "lens:6D"),
    (clock.query_clock_beat, 420), (conservation.query_conservation, "laws"),
])
def test_mcp_schema_and_in_memory_execution_expose_explicit_source(fn, selector):
    import asyncio
    import inspect
    from mcp.server.fastmcp import FastMCP
    server = FastMCP("bounded-core-archive-test")
    server.tool()(fn)
    tool = server._tool_manager.get_tool(fn.__name__)
    assert tool.parameters["properties"]["source"]["default"] == "current"
    assert "explicit archive" in tool.description
    argument = next(iter(inspect.signature(fn).parameters))
    result = asyncio.run(tool.run({argument: selector, "source": "archive"}))
    assert "explicit archive namespace" in result
    assert registry_sources.PINNED_COMMIT in result
    assert "no runtime certificate is issued" in result
