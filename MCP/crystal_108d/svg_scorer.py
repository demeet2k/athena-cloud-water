# CRYSTAL: Xi108:W3:A7:S22 | face=R | node=701 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→mcp
"""
SVG Scorer — Multi-Dimensional Quality Assessment (v2)
=======================================================
v2 UPGRADES (Cycle 2 self-play improvement):
  - Parses polygon/polyline VERTICES for symmetry + golden ratio detection
  - Parses path commands for arc/curve complexity scoring
  - Measures inter-vertex distances for golden ratio adherence
  - Better bounding box via vertex extraction
  - Structural complexity metric (total geometric information density)
  - Handles single-element composites (polygons with many vertices)

Scoring dimensions:
  - Geometric accuracy (element count, bounding box, centroid)
  - Structural quality (symmetry, golden ratio, balance)
  - Complexity metrics (path richness, diversity, vertex richness, transform depth)
  - Efficiency (information density per byte)
"""

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .geometric_constants import PHI, PHI_INV

TAU = 2 * math.pi

# SVG element tags we care about
_SHAPE_TAGS = {"circle", "rect", "line", "polyline", "polygon", "path",
               "ellipse", "text", "image", "use"}


# ══════════════════════════════════════════════════════════════════════
#  SVGScore — Quality Assessment Dataclass
# ══════════════════════════════════════════════════════════════════════

@dataclass
class SVGScore:
    """Multi-dimensional quality score for an SVG rendering."""

    # Geometric accuracy
    element_count_accuracy: float = 0.0    # 0-1
    bounding_box_accuracy: float = 0.0     # 0-1
    centroid_accuracy: float = 0.0         # 0-1

    # Structural quality
    symmetry_score: float = 0.0            # 0-1
    golden_ratio_adherence: float = 0.0    # 0-1
    balance_score: float = 0.0             # 0-1

    # Complexity
    path_complexity: float = 0.0           # 0-1
    element_diversity: float = 0.0         # 0-1
    transform_depth: float = 0.0           # 0-1

    # Efficiency
    svg_byte_size: int = 0
    compression_ratio: float = 0.0         # 0-1

    # Composite
    total_score: float = 0.0

    # Timing (filled externally)
    generation_time_ms: float = 0.0

    def to_15d(self, improvement_delta: float = 0.0) -> List[float]:
        """Map SVG scores to 15D observation vector."""
        inv_size = min(1.0, 1000.0 / max(1, self.svg_byte_size))
        inv_time = min(1.0, 100.0 / max(0.1, self.generation_time_ms))
        elem_rate = min(1.0, (self.element_count_accuracy * 20) /
                        max(0.1, self.generation_time_ms) * 100)
        return [
            self.element_count_accuracy,    # x1_structure
            self.balance_score,             # x2_semantics
            self.symmetry_score,            # x3_coordination
            self.transform_depth,           # x4_recursion
            self.element_diversity,         # x5_contradiction
            self.golden_ratio_adherence,    # x6_emergence
            self.path_complexity,           # x7_legibility
            self.centroid_accuracy,         # x8_routing
            self.bounding_box_accuracy,     # x9_grounding
            self.compression_ratio,         # x10_compression
            self.total_score,               # x11_interop
            min(1.0, max(0.0, 0.5 + improvement_delta)),  # x12_potential
            inv_size,                       # x13_resource_efficiency
            inv_time,                       # x14_latency
            elem_rate,                      # x15_throughput
        ]


# ══════════════════════════════════════════════════════════════════════
#  SVGScorer — Analysis Engine (v2: vertex-aware)
# ══════════════════════════════════════════════════════════════════════

class SVGScorer:
    """Analyzes SVG quality across multiple dimensions.

    v2: Extracts polygon vertices and path waypoints to detect symmetry
    and golden ratio from internal geometry, not just element positions.
    """

    def score(self, svg_str: str, target_elements: int = 0,
              target_symmetry: int = 0, target_golden: bool = False,
              canvas_width: float = 800, canvas_height: float = 800) -> SVGScore:
        """Score an SVG string."""
        result = SVGScore()
        result.svg_byte_size = len(svg_str.encode("utf-8"))

        elements = self._parse_elements(svg_str)
        n_elements = len(elements)

        # Gather ALL vertices from all elements (the geometric truth)
        all_vertices = []
        for e in elements:
            all_vertices.extend(self._element_vertices(e))

        n_vertices = len(all_vertices)

        # ── Element count accuracy ───────────────────────────────
        if target_elements > 0:
            diff = abs(n_elements - target_elements) / target_elements
            result.element_count_accuracy = max(0.0, 1.0 - diff)
        else:
            result.element_count_accuracy = min(1.0, n_elements / 10.0)

        # ── Bounding box accuracy (uses vertices) ────────────────
        if all_vertices:
            xs = [p[0] for p in all_vertices]
            ys = [p[1] for p in all_vertices]
            bx, by = min(xs), min(ys)
            bw, bh = max(xs) - bx, max(ys) - by
            # Ideal: content fills 40-90% of canvas
            fill_x = bw / canvas_width if canvas_width > 0 else 0
            fill_y = bh / canvas_height if canvas_height > 0 else 0
            # Score peaks at ~62% fill (golden ratio), drops at extremes
            fx = 1.0 - abs(fill_x - PHI_INV) * 1.5
            fy = 1.0 - abs(fill_y - PHI_INV) * 1.5
            result.bounding_box_accuracy = max(0.0, min(1.0, (fx + fy) / 2))
        else:
            result.bounding_box_accuracy = 0.0

        # ── Centroid accuracy ────────────────────────────────────
        if all_vertices:
            cx_actual = sum(p[0] for p in all_vertices) / n_vertices
            cy_actual = sum(p[1] for p in all_vertices) / n_vertices
            cx_target = canvas_width / 2
            cy_target = canvas_height / 2
            dist = math.sqrt((cx_actual - cx_target) ** 2 +
                             (cy_actual - cy_target) ** 2)
            max_dist = math.sqrt(cx_target ** 2 + cy_target ** 2)
            result.centroid_accuracy = max(0.0, 1.0 - dist / max_dist)
        else:
            result.centroid_accuracy = 0.0

        # ── Balance score ────────────────────────────────────────
        if all_vertices and len(all_vertices) >= 4:
            # Quadrant balance: how evenly distributed are vertices?
            cx_m = sum(p[0] for p in all_vertices) / n_vertices
            cy_m = sum(p[1] for p in all_vertices) / n_vertices
            q = [0, 0, 0, 0]
            for px, py in all_vertices:
                qi = (0 if px < cx_m else 1) + (0 if py < cy_m else 2)
                q[qi] += 1
            ideal = n_vertices / 4
            if ideal > 0:
                imbalance = sum(abs(c - ideal) for c in q) / (4 * ideal)
                result.balance_score = max(0.0, 1.0 - imbalance)
            else:
                result.balance_score = result.centroid_accuracy
        else:
            result.balance_score = result.centroid_accuracy

        # ── Symmetry detection (vertex-based) ────────────────────
        detected_sym = self._detect_symmetry_from_vertices(all_vertices,
                                                            canvas_width,
                                                            canvas_height)
        if target_symmetry > 0:
            result.symmetry_score = min(1.0, detected_sym / target_symmetry)
        else:
            result.symmetry_score = min(1.0, detected_sym / 6.0)

        # ── Golden ratio adherence (vertex distances) ────────────
        result.golden_ratio_adherence = self._measure_golden_from_vertices(
            all_vertices, elements, target_golden)

        # ── Path complexity ──────────────────────────────────────
        result.path_complexity = self._measure_path_complexity(svg_str, elements)

        # ── Element diversity ────────────────────────────────────
        types_used = set(e.get("type", "") for e in elements)
        # Also count vertex-rich elements as adding diversity
        vertex_rich = sum(1 for e in elements
                          if e.get("n_points", 0) > 3 or
                          e.get("path_commands", 0) > 3)
        type_score = len(types_used) / 5.0
        rich_score = vertex_rich / 3.0
        result.element_diversity = min(1.0, max(type_score, rich_score))

        # ── Transform depth ──────────────────────────────────────
        result.transform_depth = self._measure_transform_depth(svg_str)

        # ── Compression ratio (geometric info per byte) ──────────
        # Total geometric information = vertices + elements + path commands
        total_commands = sum(e.get("path_commands", 0) for e in elements)
        geo_info = n_vertices + n_elements + total_commands
        kb = result.svg_byte_size / 1024
        if kb > 0:
            result.compression_ratio = min(1.0, geo_info / (kb * 20))
        else:
            result.compression_ratio = 0.0

        # ── Composite score ──────────────────────────────────────
        weights = {
            "element_count_accuracy": 0.12,
            "bounding_box_accuracy": 0.10,
            "centroid_accuracy": 0.10,
            "symmetry_score": 0.18,
            "golden_ratio_adherence": 0.15,
            "balance_score": 0.08,
            "path_complexity": 0.07,
            "element_diversity": 0.05,
            "transform_depth": 0.05,
            "compression_ratio": 0.10,
        }
        total = sum(getattr(result, k) * w for k, w in weights.items())
        result.total_score = total

        return result

    # ── Element Parsing ─────────────────────────────────────────────

    def _parse_elements(self, svg_str: str) -> List[Dict]:
        """Extract element info from SVG XML."""
        elements = []
        try:
            root = ET.fromstring(svg_str)
        except ET.ParseError:
            return elements
        self._walk_tree(root, elements)
        return elements

    def _walk_tree(self, node: ET.Element, elements: List[Dict],
                   depth: int = 0) -> None:
        """Recursively walk SVG tree, extracting shape elements."""
        tag = node.tag.split("}")[-1] if "}" in node.tag else node.tag

        if tag in _SHAPE_TAGS:
            elem = {"type": tag, "depth": depth}
            for attr in ("cx", "cy", "r", "x", "y", "x1", "y1", "x2", "y2",
                         "width", "height", "rx", "ry"):
                val = node.get(attr)
                if val:
                    try:
                        elem[attr] = float(val)
                    except ValueError:
                        pass
            # Path data
            d = node.get("d", "")
            if d:
                elem["path_data"] = d
                elem["path_commands"] = len(re.findall(r"[A-Za-z]", d))
            # Polygon/polyline points — parse into actual vertex list
            pts_str = node.get("points", "")
            if pts_str:
                vertices = self._parse_points(pts_str)
                elem["vertices"] = vertices
                elem["n_points"] = len(vertices)
            elements.append(elem)

        for child in node:
            self._walk_tree(child, elements, depth + 1)

    @staticmethod
    def _parse_points(pts_str: str) -> List[Tuple[float, float]]:
        """Parse SVG points attribute into coordinate list."""
        vertices = []
        # Handle both "x,y x,y" and "x y x y" formats
        nums = re.findall(r"-?\d+\.?\d*", pts_str)
        for i in range(0, len(nums) - 1, 2):
            try:
                vertices.append((float(nums[i]), float(nums[i + 1])))
            except (ValueError, IndexError):
                pass
        return vertices

    # ── Vertex Extraction ───────────────────────────────────────────

    def _element_vertices(self, e: Dict) -> List[Tuple[float, float]]:
        """Extract ALL geometric vertices from an element.

        This is the v2 upgrade — we look INSIDE polygons and paths.
        """
        t = e.get("type", "")

        if t == "circle":
            cx, cy, r = e.get("cx", 0), e.get("cy", 0), e.get("r", 0)
            # Sample 8 points around circle
            pts = [(cx, cy)]
            for i in range(8):
                a = TAU * i / 8
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            return pts

        elif t == "rect":
            x, y = e.get("x", 0), e.get("y", 0)
            w, h = e.get("width", 0), e.get("height", 0)
            return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        elif t == "line":
            return [(e.get("x1", 0), e.get("y1", 0)),
                    (e.get("x2", 0), e.get("y2", 0))]

        elif t in ("polygon", "polyline"):
            # Use parsed vertices directly
            return e.get("vertices", [])

        elif t == "path":
            return self._extract_path_waypoints(e.get("path_data", ""))

        elif t == "text":
            return [(e.get("x", 0), e.get("y", 0))]

        return []

    @staticmethod
    def _extract_path_waypoints(d: str) -> List[Tuple[float, float]]:
        """Extract waypoints from SVG path data string."""
        waypoints = []
        # Find all coordinate pairs after commands
        nums = re.findall(r"-?\d+\.?\d*", d)
        for i in range(0, len(nums) - 1, 2):
            try:
                waypoints.append((float(nums[i]), float(nums[i + 1])))
            except (ValueError, IndexError):
                pass
        return waypoints

    # ── Symmetry Detection (v2: vertex-based) ───────────────────────

    def _detect_symmetry_from_vertices(self, vertices: List[Tuple[float, float]],
                                        canvas_w: float,
                                        canvas_h: float) -> int:
        """Detect rotational symmetry from vertex positions."""
        if len(vertices) < 3:
            return 0

        # Compute centroid
        cx = sum(p[0] for p in vertices) / len(vertices)
        cy = sum(p[1] for p in vertices) / len(vertices)

        # Compute distances from centroid and sort by distance
        radii = []
        for px, py in vertices:
            r = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
            if r > 1e-6:
                radii.append(r)

        if len(radii) < 3:
            return 0

        # Group vertices by similar radius (concentric rings)
        radii_sorted = sorted(radii)
        rings = []
        current_ring = [radii_sorted[0]]
        for r in radii_sorted[1:]:
            if r - current_ring[-1] < current_ring[-1] * 0.15:
                current_ring.append(r)
            else:
                if len(current_ring) >= 2:
                    rings.append(current_ring)
                current_ring = [r]
        if len(current_ring) >= 2:
            rings.append(current_ring)

        if not rings:
            # Try angle-based symmetry on all vertices
            return self._angle_symmetry(vertices, cx, cy)

        # For each ring, detect angular symmetry
        best_sym = 0
        for ring in rings:
            ring_r_mean = sum(ring) / len(ring)
            r_tol = ring_r_mean * 0.2
            # Get vertices in this ring
            ring_verts = [(px, py) for px, py in vertices
                          if abs(math.sqrt((px - cx) ** 2 +
                                           (py - cy) ** 2) - ring_r_mean) < r_tol]
            if len(ring_verts) >= 3:
                sym = self._angle_symmetry(ring_verts, cx, cy)
                best_sym = max(best_sym, sym)

        return best_sym

    def _angle_symmetry(self, verts: List[Tuple[float, float]],
                        cx: float, cy: float) -> int:
        """Check angular regularity of vertices around a center."""
        angles = []
        for px, py in verts:
            dx, dy = px - cx, py - cy
            if abs(dx) > 1e-6 or abs(dy) > 1e-6:
                angles.append(math.atan2(dy, dx))
        angles.sort()
        n = len(angles)
        if n < 3:
            return 0

        # Compute angular gaps
        diffs = []
        for i in range(n):
            d = angles[(i + 1) % n] - angles[i]
            if d < 0:
                d += TAU
            diffs.append(d)

        # Check if gaps are uniform (rotational symmetry = n)
        mean_diff = TAU / n
        tolerance = mean_diff * 0.25
        regular_count = sum(1 for d in diffs if abs(d - mean_diff) < tolerance)

        if regular_count >= n * 0.7:
            return n

        # Check for sub-symmetries (e.g., 12 vertices might have 6-fold sym)
        for divisor in [2, 3, 4, 5, 6]:
            if n % divisor == 0:
                group_size = n // divisor
                expected_gap = TAU / divisor
                tol = expected_gap * 0.25
                # Sample every group_size-th gap
                sub_gaps = [sum(diffs[i * group_size:(i + 1) * group_size])
                            for i in range(divisor)]
                matches = sum(1 for g in sub_gaps if abs(g - expected_gap) < tol)
                if matches >= divisor * 0.7:
                    return divisor

        return max(1, regular_count)

    # ── Golden Ratio (v2: vertex distances) ─────────────────────────

    def _measure_golden_from_vertices(self, vertices: List[Tuple[float, float]],
                                       elements: List[Dict],
                                       target_golden: bool) -> float:
        """Measure golden ratio adherence from vertex geometry."""
        distances = []

        # Collect inter-vertex distances
        sample = vertices[:50]  # cap for performance
        for i in range(len(sample)):
            for j in range(i + 1, min(i + 6, len(sample))):
                dx = sample[i][0] - sample[j][0]
                dy = sample[i][1] - sample[j][1]
                d = math.sqrt(dx * dx + dy * dy)
                if d > 1e-6:
                    distances.append(d)

        # Also collect rect w/h ratios
        for e in elements:
            if e.get("type") == "rect":
                w, h = e.get("width", 0), e.get("height", 0)
                if w > 0 and h > 0:
                    distances.append(max(w, h) / min(w, h))

        # Also collect circle radii
        radii = [e.get("r", 0) for e in elements
                 if e.get("type") == "circle" and e.get("r", 0) > 0]
        distances.extend(radii)

        if len(distances) < 2:
            return 0.3 if target_golden else 0.0

        # Check distance RATIOS for golden ratio
        golden_hits = 0
        total_checks = 0
        dist_sorted = sorted(set(distances))  # deduplicate

        for i in range(len(dist_sorted)):
            for j in range(i + 1, min(i + 8, len(dist_sorted))):
                a, b = dist_sorted[i], dist_sorted[j]
                if a > 1e-6:
                    r = b / a
                    total_checks += 1
                    # Check against PHI, PHI^2, PHI^-1, PHI^-2
                    for target in (PHI, PHI ** 2, PHI_INV, PHI_INV ** 2, 2.0):
                        if abs(r - target) < target * 0.1:
                            golden_hits += 1
                            break

        if total_checks == 0:
            return 0.0
        raw = golden_hits / total_checks
        return min(1.0, raw * 3)  # amplify — finding ANY golden ratios is good

    # ── Path Complexity (v2: command-type aware) ────────────────────

    def _measure_path_complexity(self, svg_str: str,
                                  elements: List[Dict]) -> float:
        """Measure richness of geometric commands."""
        total_commands = 0
        has_arcs = False
        has_curves = False
        n_vertices_total = 0

        for e in elements:
            pc = e.get("path_commands", 0)
            total_commands += pc
            pd = e.get("path_data", "")
            if "A" in pd or "a" in pd:
                has_arcs = True
            if "C" in pd or "c" in pd or "Q" in pd or "q" in pd:
                has_curves = True
            n_pts = e.get("n_points", 0)
            n_vertices_total += n_pts

        # Polygon vertex count also contributes to complexity
        vertex_score = min(1.0, n_vertices_total / 20.0)
        command_score = min(1.0, total_commands / 30.0)
        curve_bonus = 0.2 if has_arcs else 0.0
        curve_bonus += 0.2 if has_curves else 0.0

        return min(1.0, max(vertex_score, command_score) + curve_bonus)

    # ── Transform Depth ─────────────────────────────────────────────

    def _measure_transform_depth(self, svg_str: str) -> float:
        """Measure nesting depth of transform groups."""
        max_depth = 0
        depth = 0
        for match in re.finditer(r"<g[^>]*transform|</g>", svg_str):
            if match.group().startswith("<g"):
                depth += 1
                max_depth = max(max_depth, depth)
            else:
                depth = max(0, depth - 1)
        # Also count ANY group nesting (even without transform)
        g_depth = 0
        g_max = 0
        for match in re.finditer(r"<g[ >]|</g>", svg_str):
            if match.group().startswith("<g"):
                g_depth += 1
                g_max = max(g_max, g_depth)
            else:
                g_depth = max(0, g_depth - 1)
        # Use the better of transform depth or group nesting
        score = max(max_depth / 5.0, g_max / 8.0)
        return min(1.0, score)


# Module-level singleton
_scorer = None

def get_scorer() -> SVGScorer:
    """Get or create the singleton scorer."""
    global _scorer
    if _scorer is None:
        _scorer = SVGScorer()
    return _scorer
