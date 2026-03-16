"""Smoke tests for all crystal_108d tools — each called with known-good inputs."""

from crystal_108d.shells import query_shell, query_superphase, query_archetype, read_hologram_chapter
from crystal_108d.dimensions import resolve_dimensional_body, dimensional_lift, query_containment
from crystal_108d.organs import query_organ
from crystal_108d.address import navigate_108d
from crystal_108d.live_lock import compute_live_lock
from crystal_108d.clock import query_clock_beat
from crystal_108d.moves import check_route_legality
from crystal_108d.metro_lines import query_metro_line
from crystal_108d.z_points import resolve_z_point
from crystal_108d.conservation import query_conservation
from crystal_108d.overlays import query_overlay, query_sigma15
from crystal_108d.transport import query_transport_stack
from crystal_108d.mobius_lenses import query_mobius_lens, query_sfcr_station
from crystal_108d.stage_codes import query_stage_code
from crystal_108d.angel import query_angel


class TestShellTools:
    def test_query_shell(self):
        result = query_shell(1)
        assert "Shell 1" in result
        assert len(result) > 50

    def test_query_shell_last(self):
        result = query_shell(36)
        assert "Shell 36" in result

    def test_query_shell_invalid(self):
        result = query_shell(0)
        assert "Invalid" in result or "invalid" in result.lower()

    def test_query_superphase_sulfur(self):
        result = query_superphase("sulfur")
        assert "Sulfur" in result

    def test_query_superphase_code(self):
        result = query_superphase("Me")
        assert "Mercury" in result

    def test_query_archetype(self):
        result = query_archetype(1)
        assert "Apex Seed" in result

    def test_query_archetype_all_wreaths(self):
        result = query_archetype(7)
        assert "3" in result  # appears in 3 shells

    def test_read_hologram_chapter(self):
        result = read_hologram_chapter(1)
        assert "Chapter 1" in result

    def test_read_hologram_chapter_last(self):
        result = read_hologram_chapter(21)
        assert "Chapter 21" in result


class TestDimensionTools:
    def test_resolve_3d(self):
        result = resolve_dimensional_body(3)
        assert "3D" in result

    def test_resolve_12d(self):
        result = resolve_dimensional_body(12)
        assert "12D" in result

    def test_dimensional_lift(self):
        result = dimensional_lift(4, 12)
        assert "4D" in result
        assert "12D" in result

    def test_query_containment(self):
        result = query_containment(12)
        assert "Weave" in result or "B_12" in result


class TestOrganTool:
    def test_query_by_name(self):
        result = query_organ("Identity")
        assert "Identity" in result

    def test_query_by_dyad_index(self):
        result = query_organ("1")
        assert "Dyad" in result

    def test_query_crown_closure(self):
        result = query_organ("7")
        assert "Crown" in result or "Petal" in result


class TestNavigationTools:
    def test_navigate_by_shell(self):
        result = navigate_108d(shell=5)
        assert "Shell 5" in result

    def test_navigate_by_address(self):
        result = navigate_108d(address="Xi108:S5")
        assert "Shell 5" in result

    def test_navigate_by_wreath(self):
        result = navigate_108d(wreath="Su")
        assert "Sulfur" in result or "Su" in result


class TestLiveLockTool:
    def test_compute(self):
        result = compute_live_lock("3", "5")
        assert "Lock" in result or "lock" in result.lower()


class TestClockTool:
    def test_beat_0(self):
        result = query_clock_beat(0)
        assert "Beat 0" in result

    def test_beat_210(self):
        result = query_clock_beat(210)
        assert "Beat 210" in result


class TestMovesTool:
    def test_list_primitives(self):
        result = check_route_legality("list")
        assert "STEP_SHELL" in result

    def test_check_route(self):
        route = '[{"type": "STEP_SHELL", "from": 1, "to": 2, "delta": 1}]'
        result = check_route_legality(route)
        assert "Legality" in result or "Move" in result


class TestMetroTool:
    def test_overview(self):
        result = query_metro_line("all")
        assert "Metro" in result or "Shell" in result

    def test_wreath_line(self):
        result = query_metro_line("wreath", 0)
        assert "Sulfur" in result or "Su" in result

    def test_archetype_column(self):
        result = query_metro_line("archetype_column", 1)
        assert "Archetype" in result or "Apex" in result


class TestZPointTool:
    def test_hierarchy(self):
        result = resolve_z_point("all")
        assert "Z" in result

    def test_global(self):
        result = resolve_z_point("global")
        assert "Z*" in result or "Global" in result or "global" in result.lower()


class TestConservationTool:
    def test_list_laws(self):
        result = query_conservation("list")
        assert "Conservation" in result or "Shell" in result

    def test_check_motion(self):
        motion = '{"shell_deltas": [1, -1], "zoom_deltas": [0], "wreath_rotations": [0], "face_shifts": [0], "mobius_flips": 0}'
        result = query_conservation(motion)
        assert "PASS" in result


class TestOverlayTools:
    def test_overview(self):
        result = query_overlay("all")
        assert "Overlay" in result or "Registry" in result

    def test_lens_registry(self):
        result = query_overlay("lens")
        assert "Square" in result

    def test_sigma15(self):
        result = query_sigma15(15)
        assert "SFCR" in result


class TestTransportTool:
    def test_full_stack(self):
        result = query_transport_stack(0)
        assert "Transport" in result

    def test_dimension_3(self):
        result = query_transport_stack(3)
        assert "3D" in result


class TestMobiusLensTools:
    def test_overview(self):
        result = query_mobius_lens("all")
        assert "Möbius" in result or "Lens" in result

    def test_kernel(self):
        result = query_mobius_lens("kernel")
        assert "Kernel" in result or "4×4" in result

    def test_square(self):
        result = query_mobius_lens("square")
        assert "Square" in result

    def test_flower(self):
        result = query_mobius_lens("flower")
        assert "Flower" in result

    def test_cloud(self):
        result = query_mobius_lens("cloud")
        assert "Cloud" in result

    def test_fractal(self):
        result = query_mobius_lens("fractal")
        assert "Fractal" in result

    def test_laws(self):
        result = query_mobius_lens("laws")
        assert "Law" in result or "Kernel" in result

    def test_lattice(self):
        result = query_mobius_lens("lattice")
        assert "SFCR" in result or "15" in result

    def test_cockpit(self):
        result = query_mobius_lens("cockpit")
        assert "96" in result or "Cockpit" in result

    def test_sfcr_station(self):
        result = query_sfcr_station("SF")
        assert "SF" in result

    def test_sfcr_by_mask(self):
        result = query_sfcr_station("15")
        assert "SFCR" in result


class TestStageCodeTool:
    def test_all(self):
        result = query_stage_code("all")
        assert "Stage" in result or "S3" in result

    def test_specific(self):
        result = query_stage_code("S4")
        assert "4D" in result

    def test_s12(self):
        result = query_stage_code("S12")
        assert "12D" in result or "Crown" in result

    def test_zeros(self):
        result = query_stage_code("zeros")
        assert "Z" in result

    def test_sigma60(self):
        result = query_stage_code("sigma60")
        assert "60" in result


class TestAngelTool:
    def test_overview(self):
        result = query_angel("all")
        assert "Angel" in result

    def test_pieces(self):
        result = query_angel("pieces")
        assert "12" in result or "Σ" in result or "Token" in result

    def test_observability(self):
        result = query_angel("observability")
        assert "Square" in result or "probe" in result.lower()

    def test_selves(self):
        result = query_angel("selves")
        assert "Hidden" in result or "Canonical" in result

    def test_modes(self):
        result = query_angel("modes")
        assert "committed" in result.lower() or "flowing" in result.lower()
