"""Exact source Z-point reads and negative routing checks; no corpus writes."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))
from crystal_108d import z_points


def source():
    return json.loads((ROOT / "MCP/data/z_point_hierarchy.json").read_text(encoding="utf-8"))


class ZPointSourceTests(unittest.TestCase):
    def test_every_actual_record_by_id_name_and_dimension(self):
        data = source()
        self.assertEqual(len(data["z_points"]), 8)
        for point in data["z_points"]:
            for field in ("id", "name", "dimension"):
                with self.subTest(id=point["id"], selector=field):
                    report = z_points.resolve_z_point(" " + point[field].swapcase() + " ")
                    for value in point.values():
                        self.assertIn(value, report)
                    self.assertIn("HOLD", report)
                    self.assertNotIn("tunnel is legal", report)

    def test_overview_retains_all_source_descriptions_and_laws(self):
        data = source()
        for selector in ("all", "hierarchy", "overview"):
            report = z_points.resolve_z_point(selector)
            for point in data["z_points"]:
                self.assertIn(point["description"], report)
            for field in ("description", "convergence_law", "omega_theorem"):
                self.assertIn(data[field], report)
            self.assertIn("declared", report)

    def test_old_categories_and_tunnel_are_not_guessed(self):
        for selector in ("global", "atlas", "Z_E10", "local", "Z_L", "distributed", "Z_D", "tunnel", "unknown"):
            with self.subTest(selector=selector):
                report = z_points.resolve_z_point(selector)
                self.assertTrue(report.startswith("HOLD:"))
                self.assertNotIn("### Z*", report)
                self.assertNotIn("Any two points", report)
        self.assertIn("### Z* - Z* Omega", z_points.resolve_z_point("Z*"))

    def test_no_undeclared_scope_is_accepted(self):
        for selector in ("all", "Z4", "Z*"):
            self.assertTrue(z_points.resolve_z_point(selector, "Q").startswith("HOLD:"))

    def test_invalid_input_types_are_held(self):
        for value in (None, True, 4, 4.5, [], {}, "", "   "):
            self.assertTrue(z_points.resolve_z_point(value).startswith("HOLD:"))
        for value in (None, True, 4, [], {}):
            self.assertTrue(z_points.resolve_z_point("Z4", value).startswith("HOLD:"))

    def test_duplicate_identity_and_ambiguous_selector_are_held(self):
        data = source()
        data["z_points"].append(copy.deepcopy(data["z_points"][0]))
        with patch.object(type(z_points._zpoints), "load", return_value=data):
            self.assertTrue(z_points.resolve_z_point("all").startswith("HOLD:"))
        data = source()
        data["z_points"][1]["dimension"] = "0D"
        with patch.object(type(z_points._zpoints), "load", return_value=data):
            self.assertTrue(z_points.resolve_z_point("0D").startswith("HOLD:"))
            self.assertIn("### Z0", z_points.resolve_z_point("Z0"))

    def test_missing_malformed_and_conflicting_sources_are_held(self):
        for key in ("z_points", "description", "convergence_law", "omega_theorem"):
            data = source()
            del data[key]
            with patch.object(type(z_points._zpoints), "load", return_value=data):
                self.assertTrue(z_points.resolve_z_point("all").startswith("HOLD:"))
        for data in ([], {"meta": []}, {**source(), "z_points": []}, {**source(), "types": []}):
            with patch.object(type(z_points._zpoints), "load", return_value=data):
                self.assertTrue(z_points.resolve_z_point("all").startswith("HOLD:"))
        for value in (None, "", [], 4):
            data = source()
            data["z_points"][0]["id"] = value
            with patch.object(type(z_points._zpoints), "load", return_value=data):
                self.assertTrue(z_points.resolve_z_point("all").startswith("HOLD:"))
        with patch.object(type(z_points._zpoints), "load", side_effect=FileNotFoundError("missing")):
            self.assertTrue(z_points.resolve_z_point("Z4").startswith("HOLD:"))

    def test_valid_legacy_reads_are_preserved(self):
        data = {"hierarchy_law": "legacy hierarchy", "returnability": "legacy return",
                "tunnel_law": "legacy tunnel", "types": [{"code": "global", "symbol": "Z*",
                "scope": "global", "description": "legacy absolute zero",
                "properties": ["legacy property"], "reachable_from": "legacy stations"}]}
        with patch.object(type(z_points._zpoints), "load", return_value=data):
            self.assertIn("legacy hierarchy", z_points.resolve_z_point("all"))
            self.assertIn("legacy stations", z_points.resolve_z_point("global"))
            self.assertIn("legacy tunnel", z_points.resolve_z_point("tunnel"))


if __name__ == "__main__":
    unittest.main()
