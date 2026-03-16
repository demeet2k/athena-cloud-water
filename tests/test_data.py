"""Validate all JSON data files for structural integrity."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "MCP" / "data"


def _load(filename: str) -> dict:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


class TestJsonFilesLoad:
    """Every JSON data file must parse without errors."""

    def test_shell_registry(self):
        data = _load("shell_registry.json")
        assert "meta" in data
        assert "shells" in data

    def test_hologram_chapters(self):
        data = _load("hologram_chapters.json")
        assert "chapters" in data

    def test_dimensional_ladder(self):
        data = _load("dimensional_ladder.json")
        assert "dimensions" in data

    def test_organ_atlas(self):
        data = _load("organ_atlas.json")
        assert "dyads" in data

    def test_live_lock_registry(self):
        data = _load("live_lock_registry.json")
        assert "classes" in data

    def test_clock_projections(self):
        data = _load("clock_projections.json")
        assert "projections" in data

    def test_move_primitives(self):
        data = _load("move_primitives.json")
        assert "primitives" in data

    def test_metro_lines(self):
        data = _load("metro_lines.json")
        assert "shell_ascent" in data

    def test_z_point_hierarchy(self):
        data = _load("z_point_hierarchy.json")
        assert "types" in data

    def test_conservation_laws(self):
        data = _load("conservation_laws.json")
        assert "laws" in data

    def test_overlay_registries(self):
        data = _load("overlay_registries.json")
        assert "4_lens" in data

    def test_transport_stacks(self):
        data = _load("transport_stacks.json")
        assert "layers" in data

    def test_mobius_lenses(self):
        data = _load("mobius_lenses.json")
        assert "kernel_4x4" in data
        assert "lenses" in data

    def test_stage_codes(self):
        data = _load("stage_codes.json")
        assert "stages" in data

    def test_angel_object(self):
        data = _load("angel_object.json")
        assert "structural_pieces" in data


class TestDataIntegrity:
    """Cross-check meta counts against actual data."""

    def test_shell_count(self):
        data = _load("shell_registry.json")
        assert data["meta"]["total_shells"] == 36
        assert len(data["shells"]) == 36

    def test_node_count(self):
        data = _load("shell_registry.json")
        assert data["meta"]["total_nodes"] == 666
        assert sum(s["nodes"] for s in data["shells"]) == 666

    def test_hologram_chapter_count(self):
        data = _load("hologram_chapters.json")
        assert len(data["chapters"]) == 21

    def test_organ_dyad_count(self):
        data = _load("organ_atlas.json")
        assert data["meta"]["dyads"] == 6
        assert len(data["dyads"]) == 6

    def test_conservation_law_count(self):
        data = _load("conservation_laws.json")
        assert data["meta"]["total_laws"] == 6
        assert len(data["laws"]) == 6

    def test_live_lock_class_count(self):
        data = _load("live_lock_registry.json")
        assert data["meta"]["total_classes"] == 7
        assert len(data["classes"]) == 7

    def test_move_primitive_count(self):
        data = _load("move_primitives.json")
        assert len(data["primitives"]) == 10

    def test_transport_layer_count(self):
        data = _load("transport_stacks.json")
        assert len(data["layers"]) == 9

    def test_overlay_registry_count(self):
        data = _load("overlay_registries.json")
        assert data["meta"]["total_registries"] == 4
        assert len(data["4_lens"]["entries"]) == 4
        assert len(data["7_alchemy"]["entries"]) == 7
        assert len(data["5_animal"]["entries"]) == 5
        assert len(data["9_completion"]["entries"]) == 9

    def test_sfcr_station_count(self):
        data = _load("mobius_lenses.json")
        assert data["sfcr_lattice"]["total_stations"] == 15
        assert len(data["sfcr_lattice"]["stations"]) == 15

    def test_cross_lens_law_count(self):
        data = _load("mobius_lenses.json")
        assert len(data["cross_lens_laws"]) == 6

    def test_stage_count(self):
        data = _load("stage_codes.json")
        assert len(data["stages"]) == 16

    def test_angel_piece_count(self):
        data = _load("angel_object.json")
        assert len(data["structural_pieces"]) == 12

    def test_dimensional_ladder_dimensions(self):
        data = _load("dimensional_ladder.json")
        dims = [d["dimension"] for d in data["dimensions"]]
        assert 3 in dims
        assert 12 in dims
        assert len(dims) == 10  # 3D through 12D
