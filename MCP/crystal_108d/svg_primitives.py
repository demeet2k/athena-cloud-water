# CRYSTAL: Xi108:W3:A7:S21 | face=R | node=700 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→mcp
"""
SVG Primitives — Pure Mathematical SVG Generation Engine
=========================================================
Zero-dependency SVG generation using nothing but math and XML strings.
Every function returns valid SVG XML. Composites build on primitives
using golden ratio, sacred geometry, and fractal recursion.

This is the visual manifestation layer of the crystal — turning
mathematical truth into geometric form.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from .geometric_constants import PHI, PHI_INV, SQRT3, SQRT5

TAU = 2 * math.pi


# ══════════════════════════════════════════════════════════════════════
#  Attribute Helpers
# ══════════════════════════════════════════════════════════════════════

def _attrs_str(attrs: Dict[str, Any]) -> str:
    """Convert keyword attrs to SVG attribute string."""
    parts = []
    for k, v in attrs.items():
        # Convert Python underscores to SVG hyphens (e.g. stroke_width -> stroke-width)
        key = k.replace("_", "-")
        parts.append(f'{key}="{v}"')
    return " ".join(parts)


def _fmt(n: float) -> str:
    """Format a float for SVG (trim trailing zeros)."""
    return f"{n:.4f}".rstrip("0").rstrip(".")


# ══════════════════════════════════════════════════════════════════════
#  SVGCanvas — Document Container
# ══════════════════════════════════════════════════════════════════════

class SVGCanvas:
    """Accumulates SVG elements and renders a complete SVG document."""

    def __init__(self, width: int = 800, height: int = 800,
                 viewBox: Optional[str] = None,
                 background: Optional[str] = None):
        self.width = width
        self.height = height
        self.viewBox = viewBox or f"0 0 {width} {height}"
        self.defs: List[str] = []
        self.elements: List[str] = []
        if background:
            self.elements.append(
                rect(0, 0, width, height, fill=background)
            )

    def add(self, element_str: str) -> "SVGCanvas":
        """Append an SVG element string."""
        self.elements.append(element_str)
        return self

    def add_def(self, def_str: str) -> "SVGCanvas":
        """Append to <defs> block (gradients, patterns, etc.)."""
        self.defs.append(def_str)
        return self

    def render(self) -> str:
        """Produce complete SVG document string."""
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="{self.viewBox}">',
        ]
        if self.defs:
            parts.append("  <defs>")
            for d in self.defs:
                parts.append(f"    {d}")
            parts.append("  </defs>")
        for e in self.elements:
            parts.append(f"  {e}")
        parts.append("</svg>")
        return "\n".join(parts)

    def save(self, path: str) -> None:
        """Write SVG to disk."""
        from pathlib import Path as P
        p = P(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.render(), encoding="utf-8")

    @property
    def element_count(self) -> int:
        return len(self.elements)


# ══════════════════════════════════════════════════════════════════════
#  Primitives — Atomic SVG Elements
# ══════════════════════════════════════════════════════════════════════

def circle(cx: float, cy: float, r: float, **attrs) -> str:
    """SVG circle element."""
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    return f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}"{extra}/>'


def rect(x: float, y: float, w: float, h: float,
         rx: float = 0, **attrs) -> str:
    """SVG rect element with optional rounded corners."""
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    rx_str = f' rx="{_fmt(rx)}"' if rx > 0 else ""
    return (f'<rect x="{_fmt(x)}" y="{_fmt(y)}" '
            f'width="{_fmt(w)}" height="{_fmt(h)}"{rx_str}{extra}/>')


def line(x1: float, y1: float, x2: float, y2: float, **attrs) -> str:
    """SVG line element."""
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    return (f'<line x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
            f'x2="{_fmt(x2)}" y2="{_fmt(y2)}"{extra}/>')


def polyline(points: List[Tuple[float, float]], **attrs) -> str:
    """SVG polyline element."""
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points)
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    return f'<polyline points="{pts}"{extra}/>'


def polygon(points: List[Tuple[float, float]], **attrs) -> str:
    """SVG polygon element."""
    pts = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points)
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    return f'<polygon points="{pts}"{extra}/>'


def path(d: str, **attrs) -> str:
    """SVG path element with arbitrary path data."""
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    return f'<path d="{d}"{extra}/>'


def text(x: float, y: float, content: str, **attrs) -> str:
    """SVG text element."""
    a = _attrs_str(attrs)
    extra = f" {a}" if a else ""
    return f'<text x="{_fmt(x)}" y="{_fmt(y)}"{extra}>{content}</text>'


def group(children: List[str], transform: str = "", **attrs) -> str:
    """SVG group element wrapping children."""
    a = _attrs_str(attrs)
    parts = []
    t = f' transform="{transform}"' if transform else ""
    extra = f" {a}" if a else ""
    parts.append(f"<g{t}{extra}>")
    for c in children:
        parts.append(f"  {c}")
    parts.append("</g>")
    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════════
#  Gradients
# ══════════════════════════════════════════════════════════════════════

def linear_gradient(gid: str, stops: List[Tuple[str, str]],
                    x1: str = "0%", y1: str = "0%",
                    x2: str = "100%", y2: str = "0%") -> str:
    """SVG linear gradient definition. stops = [(offset, color), ...]."""
    parts = [f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">']
    for offset, color in stops:
        parts.append(f'  <stop offset="{offset}" stop-color="{color}"/>')
    parts.append("</linearGradient>")
    return "\n".join(parts)


def radial_gradient(gid: str, stops: List[Tuple[str, str]],
                    cx: str = "50%", cy: str = "50%", r: str = "50%") -> str:
    """SVG radial gradient definition."""
    parts = [f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">']
    for offset, color in stops:
        parts.append(f'  <stop offset="{offset}" stop-color="{color}"/>')
    parts.append("</radialGradient>")
    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════════
#  Transform Wrappers
# ══════════════════════════════════════════════════════════════════════

def rotate(element: str, angle: float,
           cx: float = 0, cy: float = 0) -> str:
    """Wrap element in a rotation transform."""
    return group([element], transform=f"rotate({_fmt(angle)},{_fmt(cx)},{_fmt(cy)})")


def scale(element: str, sx: float, sy: Optional[float] = None) -> str:
    """Wrap element in a scale transform."""
    sy_val = sy if sy is not None else sx
    return group([element], transform=f"scale({_fmt(sx)},{_fmt(sy_val)})")


def translate(element: str, dx: float, dy: float) -> str:
    """Wrap element in a translation."""
    return group([element], transform=f"translate({_fmt(dx)},{_fmt(dy)})")


def reflect(element: str, axis: str = "x") -> str:
    """Reflect element across x or y axis (around origin)."""
    if axis == "y":
        return group([element], transform="scale(-1,1)")
    return group([element], transform="scale(1,-1)")


# ══════════════════════════════════════════════════════════════════════
#  Composite Constructions — Sacred Geometry & Fractals
# ══════════════════════════════════════════════════════════════════════

def regular_polygon(cx: float, cy: float, r: float, n: int, **attrs) -> str:
    """Regular n-gon inscribed in circle of radius r."""
    points = []
    for i in range(n):
        angle = TAU * i / n - math.pi / 2  # start at top
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points.append((px, py))
    return polygon(points, **attrs)


def concentric_circles(cx: float, cy: float, r_outer: float,
                       n: int = 5, ratio: float = PHI_INV, **attrs) -> str:
    """N concentric circles with radius decaying by ratio."""
    children = []
    r = r_outer
    for _ in range(n):
        children.append(circle(cx, cy, r, **attrs))
        r *= ratio
    return group(children)


def star_polygon(cx: float, cy: float, r_outer: float,
                 r_inner: float, n: int = 5, **attrs) -> str:
    """Star polygon with n points."""
    points = []
    for i in range(2 * n):
        angle = TAU * i / (2 * n) - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        points.append((px, py))
    return polygon(points, **attrs)


def golden_spiral(cx: float, cy: float, turns: int = 5,
                  scale_factor: float = 100.0, **attrs) -> str:
    """Golden spiral via connected quarter-circle arcs (Fibonacci approximation)."""
    # Build Fibonacci radii
    fib = [1, 1]
    for _ in range(turns * 4):
        fib.append(fib[-1] + fib[-2])

    d_parts = []
    x, y = cx, cy
    angle_start = 0.0

    for i in range(min(turns * 4, len(fib))):
        r = fib[i] * scale_factor / fib[-1]
        # Quarter circle arc
        sweep_angle = math.pi / 2
        end_angle = angle_start + sweep_angle
        ex = x + r * (math.cos(end_angle) - math.cos(angle_start))
        ey = y + r * (math.sin(end_angle) - math.sin(angle_start))

        if i == 0:
            d_parts.append(f"M {_fmt(x)} {_fmt(y)}")

        d_parts.append(f"A {_fmt(r)} {_fmt(r)} 0 0 1 {_fmt(ex)} {_fmt(ey)}")
        x, y = ex, ey
        angle_start = end_angle

    d = " ".join(d_parts)
    defaults = {"fill": "none", "stroke": "#333", "stroke_width": "2"}
    defaults.update(attrs)
    return path(d, **defaults)


def flower_of_life(cx: float, cy: float, r: float,
                   rings: int = 2, **attrs) -> str:
    """Flower of Life — overlapping circles at 60° intervals."""
    defaults = {"fill": "none", "stroke": "#333", "stroke_width": "1"}
    defaults.update(attrs)
    children = [circle(cx, cy, r, **defaults)]  # center circle

    for ring in range(1, rings + 1):
        ring_r = r * ring
        n_circles = 6 * ring
        for i in range(n_circles):
            angle = TAU * i / n_circles
            px = cx + ring_r * math.cos(angle)
            py = cy + ring_r * math.sin(angle)
            children.append(circle(px, py, r, **defaults))

    return group(children)


def metatron_cube(cx: float, cy: float, r: float, **attrs) -> str:
    """Metatron's Cube — 13 circles + all connecting lines."""
    defaults_c = {"fill": "none", "stroke": "#333", "stroke_width": "1"}
    defaults_l = {"stroke": "#999", "stroke_width": "0.5"}
    defaults_c.update(attrs)

    # 13 positions: center + inner 6 + outer 6
    positions = [(cx, cy)]
    for i in range(6):
        angle = TAU * i / 6
        positions.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    for i in range(6):
        angle = TAU * i / 6 + TAU / 12
        positions.append((cx + r * 2 * math.cos(angle), cy + r * 2 * math.sin(angle)))

    children = []
    # Draw all connecting lines
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[j]
            children.append(line(x1, y1, x2, y2, **defaults_l))
    # Draw circles on top
    for px, py in positions:
        children.append(circle(px, py, r * 0.15, **defaults_c))

    return group(children)


def tesseract_projection(cx: float, cy: float, size: float, **attrs) -> str:
    """4D hypercube projected to 2D — 16 vertices, 32 edges."""
    defaults = {"stroke": "#333", "stroke_width": "1.5", "fill": "none"}
    defaults.update(attrs)

    # Inner and outer cubes (2D projection)
    s_out = size
    s_in = size * PHI_INV  # inner cube scaled by golden ratio

    # Outer cube vertices (rotated 45° for visual interest)
    outer = []
    for i in range(8):
        x = s_out * (1 if i & 1 else -1)
        y = s_out * (1 if i & 2 else -1)
        z = s_out * (1 if i & 4 else -1)
        # Simple isometric projection
        px = cx + (x - z) * 0.7071
        py = cy + (y - (x + z) * 0.3536)
        outer.append((px, py))

    inner = []
    for i in range(8):
        x = s_in * (1 if i & 1 else -1)
        y = s_in * (1 if i & 2 else -1)
        z = s_in * (1 if i & 4 else -1)
        px = cx + (x - z) * 0.7071
        py = cy + (y - (x + z) * 0.3536)
        inner.append((px, py))

    children = []
    # Cube edges (connect vertices differing by 1 bit)
    for verts in [outer, inner]:
        for i in range(8):
            for bit in [1, 2, 4]:
                j = i ^ bit
                if j > i:
                    children.append(line(verts[i][0], verts[i][1],
                                         verts[j][0], verts[j][1], **defaults))

    # Connecting edges between inner and outer cubes
    conn_attrs = dict(defaults)
    conn_attrs["stroke"] = "#999"
    conn_attrs["stroke_width"] = "1"
    for i in range(8):
        children.append(line(outer[i][0], outer[i][1],
                             inner[i][0], inner[i][1], **conn_attrs))

    return group(children)


def sri_yantra(cx: float, cy: float, size: float, **attrs) -> str:
    """Sri Yantra — 9 interlocking triangles (4 up, 5 down)."""
    defaults = {"fill": "none", "stroke": "#333", "stroke_width": "1.5"}
    defaults.update(attrs)

    children = []
    # Upward triangles (4) at different scales
    up_scales = [1.0, 0.75, 0.5, 0.3]
    for s in up_scales:
        r = size * s
        pts = []
        for i in range(3):
            angle = TAU * i / 3 - math.pi / 2  # point up
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        children.append(polygon(pts, **defaults))

    # Downward triangles (5) at different scales
    down_scales = [0.95, 0.7, 0.48, 0.28, 0.15]
    for s in down_scales:
        r = size * s
        pts = []
        for i in range(3):
            angle = TAU * i / 3 + math.pi / 2  # point down
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        children.append(polygon(pts, **defaults))

    return group(children)


def crystal_lattice(cx: float, cy: float, rows: int = 5, cols: int = 5,
                    spacing: float = 40.0, lattice_type: str = "hex",
                    **attrs) -> str:
    """Crystal lattice — hex, square, or triangular."""
    defaults = {"fill": "#333", "r": "3"}
    defaults.update(attrs)
    dot_r = float(defaults.pop("r", "3"))

    children = []
    for row in range(rows):
        for col in range(cols):
            if lattice_type == "hex":
                x = cx + col * spacing + (row % 2) * spacing / 2
                y = cy + row * spacing * SQRT3 / 2
            elif lattice_type == "triangular":
                x = cx + col * spacing + (row % 2) * spacing / 2
                y = cy + row * spacing * SQRT3 / 2
                # Add connecting lines for triangular
            else:  # square
                x = cx + col * spacing
                y = cy + row * spacing
            children.append(circle(x, y, dot_r, **defaults))

    return group(children)


def phi_grid(width: float, height: float, divisions: int = 5,
             **attrs) -> str:
    """Golden ratio division grid lines."""
    defaults = {"stroke": "#c0a040", "stroke_width": "1", "stroke_opacity": "0.6"}
    defaults.update(attrs)

    children = []
    # Vertical golden lines
    x = 0.0
    for _ in range(divisions):
        x_line = x + (width - x) * PHI_INV
        children.append(line(x_line, 0, x_line, height, **defaults))
        x = x_line
    # Horizontal golden lines
    y = 0.0
    for _ in range(divisions):
        y_line = y + (height - y) * PHI_INV
        children.append(line(0, y_line, width, y_line, **defaults))
        y = y_line

    return group(children)


def fractal_tree(x: float, y: float, length: float, angle: float,
                 depth: int, ratio: float = PHI_INV, **attrs) -> str:
    """Recursive fractal tree with golden ratio branching."""
    defaults = {"stroke": "#333", "stroke_width": "1.5"}
    defaults.update(attrs)

    if depth <= 0 or length < 1:
        return ""

    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)
    elements = [line(x, y, x2, y2, **defaults)]

    branch_angle = math.pi / 6  # 30 degrees
    new_len = length * ratio

    left = fractal_tree(x2, y2, new_len, angle - branch_angle,
                        depth - 1, ratio, **attrs)
    right = fractal_tree(x2, y2, new_len, angle + branch_angle,
                         depth - 1, ratio, **attrs)
    if left:
        elements.append(left)
    if right:
        elements.append(right)

    return group(elements)


def spiral_of_theodorus(cx: float, cy: float, n: int = 17,
                        unit: float = 30.0, **attrs) -> str:
    """Spiral of Theodorus — square root spiral from right triangles."""
    defaults = {"fill": "none", "stroke": "#333", "stroke_width": "1"}
    defaults.update(attrs)

    children = []
    angle = 0.0
    for k in range(1, n + 1):
        r = math.sqrt(k) * unit
        r_next = math.sqrt(k + 1) * unit
        # Right triangle: hypotenuse = sqrt(k+1), base = sqrt(k), height = 1
        d_angle = math.atan2(1, math.sqrt(k))

        x1 = cx + r * math.cos(angle)
        y1 = cy + r * math.sin(angle)
        x2 = cx  # center
        y2 = cy
        x3 = cx + r_next * math.cos(angle + d_angle)
        y3 = cy + r_next * math.sin(angle + d_angle)

        children.append(polygon([(x2, y2), (x1, y1), (x3, y3)], **defaults))
        angle += d_angle

    return group(children)


def koch_snowflake(cx: float, cy: float, size: float,
                   depth: int = 4, **attrs) -> str:
    """Koch snowflake fractal."""
    defaults = {"fill": "none", "stroke": "#333", "stroke_width": "1"}
    defaults.update(attrs)

    def _koch_points(p1, p2, d):
        if d == 0:
            return [p1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        a = (p1[0] + dx / 3, p1[1] + dy / 3)
        b = (p1[0] + 2 * dx / 3, p1[1] + 2 * dy / 3)
        # Peak of equilateral triangle
        peak = (
            a[0] + (b[0] - a[0]) * 0.5 - (b[1] - a[1]) * SQRT3 / 2,
            a[1] + (b[1] - a[1]) * 0.5 + (b[0] - a[0]) * SQRT3 / 2,
        )
        pts = []
        pts.extend(_koch_points(p1, a, d - 1))
        pts.extend(_koch_points(a, peak, d - 1))
        pts.extend(_koch_points(peak, b, d - 1))
        pts.extend(_koch_points(b, p2, d - 1))
        return pts

    # Start with equilateral triangle
    verts = []
    for i in range(3):
        angle = TAU * i / 3 - math.pi / 2
        verts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))

    all_pts = []
    for i in range(3):
        all_pts.extend(_koch_points(verts[i], verts[(i + 1) % 3], depth))

    return polygon(all_pts, **defaults)


def sierpinski_triangle(cx: float, cy: float, size: float,
                        depth: int = 5, **attrs) -> str:
    """Sierpinski triangle fractal via recursive subdivision."""
    defaults = {"fill": "#333", "stroke": "none"}
    defaults.update(attrs)

    def _sierpinski(ax, ay, bx, by, ccx, ccy, d):
        if d == 0:
            return [polygon([(ax, ay), (bx, by), (ccx, ccy)], **defaults)]
        # Midpoints
        mx_ab = (ax + bx) / 2
        my_ab = (ay + by) / 2
        mx_bc = (bx + ccx) / 2
        my_bc = (by + ccy) / 2
        mx_ca = (ccx + ax) / 2
        my_ca = (ccy + ay) / 2
        elems = []
        elems.extend(_sierpinski(ax, ay, mx_ab, my_ab, mx_ca, my_ca, d - 1))
        elems.extend(_sierpinski(mx_ab, my_ab, bx, by, mx_bc, my_bc, d - 1))
        elems.extend(_sierpinski(mx_ca, my_ca, mx_bc, my_bc, ccx, ccy, d - 1))
        return elems

    # Equilateral triangle vertices
    top = (cx, cy - size)
    left = (cx - size * SQRT3 / 2, cy + size / 2)
    right = (cx + size * SQRT3 / 2, cy + size / 2)

    elements = _sierpinski(top[0], top[1], left[0], left[1],
                           right[0], right[1], depth)
    return group(elements)


def vesica_piscis(cx: float, cy: float, r: float, **attrs) -> str:
    """Vesica Piscis — two overlapping circles, distance = r."""
    defaults = {"fill": "none", "stroke": "#333", "stroke_width": "1.5"}
    defaults.update(attrs)
    return group([
        circle(cx - r / 2, cy, r, **defaults),
        circle(cx + r / 2, cy, r, **defaults),
    ])


def radial_burst(cx: float, cy: float, r_inner: float,
                 r_outer: float, n: int = 12, **attrs) -> str:
    """Radial burst — n lines radiating from center."""
    defaults = {"stroke": "#333", "stroke_width": "1.5"}
    defaults.update(attrs)
    children = []
    for i in range(n):
        angle = TAU * i / n
        x1 = cx + r_inner * math.cos(angle)
        y1 = cy + r_inner * math.sin(angle)
        x2 = cx + r_outer * math.cos(angle)
        y2 = cy + r_outer * math.sin(angle)
        children.append(line(x1, y1, x2, y2, **defaults))
    return group(children)


def checkered_grid(x: float, y: float, rows: int, cols: int,
                   cell_size: float, color1: str = "#fff",
                   color2: str = "#333") -> str:
    """Checkered grid pattern."""
    children = []
    for r in range(rows):
        for c in range(cols):
            fill = color1 if (r + c) % 2 == 0 else color2
            children.append(rect(x + c * cell_size, y + r * cell_size,
                                 cell_size, cell_size, fill=fill))
    return group(children)


def line_grid(x: float, y: float, width: float, height: float,
              spacing: float = 20.0, **attrs) -> str:
    """Regular grid of horizontal and vertical lines."""
    defaults = {"stroke": "#ccc", "stroke_width": "0.5"}
    defaults.update(attrs)
    children = []
    # Verticals
    cx = x
    while cx <= x + width:
        children.append(line(cx, y, cx, y + height, **defaults))
        cx += spacing
    # Horizontals
    cy = y
    while cy <= y + height:
        children.append(line(x, cy, x + width, cy, **defaults))
        cy += spacing
    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  3D PROJECTION UTILITIES
# ══════════════════════════════════════════════════════════════════════

def _project_3d(x: float, y: float, z: float,
                cx: float, cy: float, scale: float = 1.0,
                angle_x: float = 0.4, angle_z: float = 0.6) -> Tuple[float, float]:
    """Project 3D point to 2D using isometric-like rotation.

    angle_x: rotation around X axis (tilt)
    angle_z: rotation around Z axis (spin)
    """
    # Rotate around Z
    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    rx = x * cos_z - y * sin_z
    ry = x * sin_z + y * cos_z
    rz = z

    # Rotate around X (tilt toward viewer)
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    fy = ry * cos_x - rz * sin_x
    fz = ry * sin_x + rz * cos_x

    return (cx + rx * scale, cy - fz * scale)


def _project_4d(x: float, y: float, z: float, w: float,
                cx: float, cy: float, scale: float = 1.0,
                angle_xw: float = 0.5, angle_yz: float = 0.3) -> Tuple[float, float]:
    """Project 4D point to 2D by rotating in XW and YZ planes, then projecting."""
    # Rotate in XW plane
    cos_a, sin_a = math.cos(angle_xw), math.sin(angle_xw)
    rx = x * cos_a - w * sin_a
    rw = x * sin_a + w * cos_a

    # Rotate in YZ plane
    cos_b, sin_b = math.cos(angle_yz), math.sin(angle_yz)
    ry = y * cos_b - z * sin_b
    rz = y * sin_b + z * cos_b

    # Perspective projection from 4D→2D using w distance
    d = 3.0  # view distance
    perspective = d / (d + rw * 0.3)
    return (cx + rx * scale * perspective, cy - (ry + rz * 0.5) * scale * perspective)


# ══════════════════════════════════════════════════════════════════════
#  DODECAHEDRON — 12 Faces / 20 Vertices / 30 Edges
# ══════════════════════════════════════════════════════════════════════

def _dodecahedron_vertices() -> List[Tuple[float, float, float]]:
    """Compute the 20 vertices of a unit dodecahedron.

    Uses the standard construction: 8 cube vertices + 12 edge-midpoints
    scaled by phi.
    """
    verts = []
    # 8 cube vertices: (±1, ±1, ±1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                verts.append((sx, sy, sz))

    # 4 vertices on each coordinate plane: (0, ±phi, ±1/phi), cyclic
    for sx in (-1, 1):
        for sy in (-1, 1):
            verts.append((0, sx * PHI, sy * PHI_INV))
            verts.append((sx * PHI_INV, 0, sy * PHI))
            verts.append((sx * PHI, sy * PHI_INV, 0))

    return verts


def _dodecahedron_edges(verts: List[Tuple[float, float, float]]) -> List[Tuple[int, int]]:
    """Compute edges: pairs of vertices at distance 2/phi apart."""
    edge_len_sq = (2.0 * PHI_INV) ** 2
    eps = 0.1
    edges = []
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            dx = verts[i][0] - verts[j][0]
            dy = verts[i][1] - verts[j][1]
            dz = verts[i][2] - verts[j][2]
            d_sq = dx * dx + dy * dy + dz * dz
            if abs(d_sq - edge_len_sq) < eps:
                edges.append((i, j))
    return edges


def _dodecahedron_faces(verts: List[Tuple[float, float, float]],
                         edges: List[Tuple[int, int]]) -> List[List[int]]:
    """Compute the 12 pentagonal faces of the dodecahedron.

    Each face is a cycle of 5 vertices. Uses adjacency-list walk.
    """
    from collections import defaultdict
    adj = defaultdict(set)
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)

    faces = []
    seen_face_keys = set()

    for start in range(len(verts)):
        neighbors = sorted(adj[start])
        for n1 in neighbors:
            for n2 in neighbors:
                if n2 <= n1:
                    continue
                if n2 not in adj[n1]:
                    # n1 and n2 are both neighbors of start but not of each other
                    # Try to find the face cycle
                    # Walk: start → n1 → ? → ? → n2 → start
                    common_n1 = adj[n1] - {start}
                    common_n2 = adj[n2] - {start}
                    for c1 in common_n1:
                        for c2 in common_n2:
                            if c2 in adj[c1] and c1 != c2:
                                face = [start, n1, c1, c2, n2]
                                key = frozenset(face)
                                if len(key) == 5 and key not in seen_face_keys:
                                    seen_face_keys.add(key)
                                    faces.append(face)
    return faces[:12]


def dodecahedron(cx: float, cy: float, size: float,
                 face_colors: Optional[List[str]] = None,
                 angle_x: float = 0.4, angle_z: float = 0.6,
                 **attrs) -> str:
    """Dodecahedron (12 faces) projected to 2D.

    The 12 faces correspond to the 12 archetypes. If face_colors is
    provided, each face gets its own fill color.
    """
    defaults = {"stroke": "#333", "stroke_width": "1.2", "fill": "none"}
    defaults.update(attrs)

    verts_3d = _dodecahedron_vertices()
    edges = _dodecahedron_edges(verts_3d)
    faces = _dodecahedron_faces(verts_3d, edges)

    # Project all vertices
    pts = [_project_3d(v[0], v[1], v[2], cx, cy, size, angle_x, angle_z)
           for v in verts_3d]

    children = []

    # Draw faces (if colors provided)
    if face_colors and faces:
        for fi, face_verts in enumerate(faces):
            color = face_colors[fi % len(face_colors)]
            face_tuples = [(pts[v][0], pts[v][1]) for v in face_verts]
            fa = dict(defaults)
            fa["fill"] = color
            fa["fill_opacity"] = "0.3"
            children.append(polygon(face_tuples, **fa))

    # Draw edges
    for i, j in edges:
        children.append(line(pts[i][0], pts[i][1],
                             pts[j][0], pts[j][1], **defaults))

    # Draw vertices as small circles
    for p in pts:
        children.append(circle(p[0], p[1], size * 0.03,
                               fill="#333", stroke="none"))

    return group(children)


def icosahedron(cx: float, cy: float, size: float,
                vertex_labels: Optional[List[str]] = None,
                angle_x: float = 0.4, angle_z: float = 0.6,
                **attrs) -> str:
    """Icosahedron (12 vertices = 12 archetypes, 20 faces) projected to 2D.

    Dual of the dodecahedron — each vertex maps to one archetype.
    """
    defaults = {"stroke": "#333", "stroke_width": "1.2", "fill": "none"}
    defaults.update(attrs)

    # 12 vertices of a unit icosahedron
    verts_3d = []
    # Top and bottom
    verts_3d.append((0, 1, 0))
    verts_3d.append((0, -1, 0))

    # Two rings of 5 vertices each
    angle_offset_top = 0
    angle_offset_bot = math.pi / 5
    y_top = math.atan(0.5)
    y_bot = -y_top

    for i in range(5):
        a = angle_offset_top + i * TAU / 5
        verts_3d.append((math.cos(a) * math.cos(y_top),
                         math.sin(y_top),
                         math.sin(a) * math.cos(y_top)))
    for i in range(5):
        a = angle_offset_bot + i * TAU / 5
        verts_3d.append((math.cos(a) * math.cos(y_bot),
                         math.sin(y_bot),
                         math.sin(a) * math.cos(y_bot)))

    # Edges: distance ~1.05 for unit icosahedron
    edge_len = 2 * math.sin(TAU / 10)
    eps = 0.15
    edges = []
    for i in range(12):
        for j in range(i + 1, 12):
            dx = verts_3d[i][0] - verts_3d[j][0]
            dy = verts_3d[i][1] - verts_3d[j][1]
            dz = verts_3d[i][2] - verts_3d[j][2]
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            if abs(d - edge_len) < eps:
                edges.append((i, j))

    # Project
    pts = [_project_3d(v[0], v[1], v[2], cx, cy, size, angle_x, angle_z)
           for v in verts_3d]

    children = []
    for i, j in edges:
        children.append(line(pts[i][0], pts[i][1],
                             pts[j][0], pts[j][1], **defaults))

    # Vertices with archetype labels
    for vi, p in enumerate(pts):
        children.append(circle(p[0], p[1], size * 0.05,
                               fill="#c66", stroke="#333", stroke_width="0.8"))
        if vertex_labels and vi < len(vertex_labels):
            children.append(text(p[0] + size * 0.06, p[1] - size * 0.04,
                                 vertex_labels[vi],
                                 font_size="10", fill="#333"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  MÖBIUS STRIP — The Topological Inversion
# ══════════════════════════════════════════════════════════════════════

def mobius_strip(cx: float, cy: float, R: float, w: float = 0.3,
                 n_steps: int = 60, n_strips: int = 8,
                 angle_x: float = 0.5, angle_z: float = 0.3,
                 **attrs) -> str:
    """Möbius strip projected to 2D — non-orientable surface.

    R: major radius, w: half-width of strip (fraction of R).
    The strip has a half-twist, making it single-sided.
    """
    defaults = {"stroke": "#333", "stroke_width": "0.8", "fill": "none"}
    defaults.update(attrs)

    children = []
    half_w = R * w

    # Generate strip mesh
    for s in range(n_strips):
        t_frac = (s / n_strips) * 2 - 1  # -1 to 1 across width
        pts_path = []
        for i in range(n_steps + 1):
            u = (i / n_steps) * TAU
            half_twist = u / 2  # the Möbius half-twist
            r_local = R + half_w * t_frac * math.cos(half_twist)
            x = r_local * math.cos(u)
            y = r_local * math.sin(u)
            z = half_w * t_frac * math.sin(half_twist)
            px, py = _project_3d(x, y, z, cx, cy, 1.0, angle_x, angle_z)
            pts_path.append(f"{_fmt(px)},{_fmt(py)}")

        children.append(f'<polyline points="{" ".join(pts_path)}" '
                        f'{_attrs_str(defaults)}/>')

    # Cross-section lines (connecting strips at intervals)
    for i in range(0, n_steps, n_steps // 12):
        u = (i / n_steps) * TAU
        half_twist = u / 2
        edge_pts = []
        for s in range(n_strips):
            t_frac = (s / n_strips) * 2 - 1
            r_local = R + half_w * t_frac * math.cos(half_twist)
            x = r_local * math.cos(u)
            y = r_local * math.sin(u)
            z = half_w * t_frac * math.sin(half_twist)
            px, py = _project_3d(x, y, z, cx, cy, 1.0, angle_x, angle_z)
            edge_pts.append(f"{_fmt(px)},{_fmt(py)}")

        cross_attrs = dict(defaults)
        cross_attrs["stroke"] = "#999"
        cross_attrs["stroke_width"] = "0.5"
        children.append(f'<polyline points="{" ".join(edge_pts)}" '
                        f'{_attrs_str(cross_attrs)}/>')

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  DIMENSIONAL CONTAINMENT — Weave Operator Visualization
# ══════════════════════════════════════════════════════════════════════

def dimensional_containment(cx: float, cy: float, size: float,
                             **attrs) -> str:
    """Nested containment rings: 3D→4D→6D→8D→10D→12D.

    Each ring is a weave operator level (W3, W5, W7, W9).
    Ring radius follows PHI scaling. Labels show dimension and
    containment multiplier.
    """
    defaults = {"stroke": "#333", "stroke_width": "1.5", "fill": "none"}
    defaults.update(attrs)

    levels = [
        {"dim": "3D", "label": "c3 seed", "color": "#e74c3c", "n": 3},
        {"dim": "4D", "label": "E4 base", "color": "#e67e22", "n": 4},
        {"dim": "6D", "label": "W3 Mobius", "color": "#f1c40f", "n": 6},
        {"dim": "8D", "label": "W5 penta", "color": "#2ecc71", "n": 8},
        {"dim": "10D", "label": "W7 hepta", "color": "#3498db", "n": 10},
        {"dim": "12D", "label": "W9 crown", "color": "#9b59b6", "n": 12},
    ]

    children = []
    n_levels = len(levels)

    for i, level in enumerate(levels):
        # PHI-scaled radius: innermost is smallest
        r = size * PHI_INV ** (n_levels - 1 - i)
        color = level["color"]

        # Ring circle
        children.append(circle(cx, cy, r,
                               stroke=color, stroke_width="2",
                               fill=color, fill_opacity="0.08"))

        # Evenly-spaced dots on ring (count = dimension number)
        for j in range(level["n"]):
            angle = j * TAU / level["n"]
            px = cx + r * math.cos(angle)
            py = cy - r * math.sin(angle)
            children.append(circle(px, py, 3,
                                   fill=color, stroke="none"))

        # Label
        children.append(text(cx + r + 8, cy + 4,
                             f'{level["dim"]} {level["label"]}',
                             font_size="10", fill=color))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  SFCR CRYSTAL — 4-Element Crystal with Colored Faces
# ══════════════════════════════════════════════════════════════════════

SFCR_COLORS = {
    "S": "#8B4513",   # Earth brown
    "F": "#DC143C",   # Fire red
    "C": "#4169E1",   # Water blue
    "R": "#228B22",   # Air green
}

ARCHETYPE_FACES = ["S", "F", "C", "R", "S", "F", "C", "R", "S", "F", "C", "R"]


def sfcr_crystal(cx: float, cy: float, size: float,
                 angle_x: float = 0.4, angle_z: float = 0.6,
                 **attrs) -> str:
    """SFCR-colored dodecahedron: 12 faces mapped to 4 elements.

    Each face is colored by its archetype's SFCR element assignment:
    S=Earth(brown), F=Fire(red), C=Water(blue), R=Air(green).
    """
    face_colors = [SFCR_COLORS[f] for f in ARCHETYPE_FACES]
    return dodecahedron(cx, cy, size, face_colors=face_colors,
                        angle_x=angle_x, angle_z=angle_z, **attrs)


# ══════════════════════════════════════════════════════════════════════
#  CRYSTAL 4D — Tesseract with Möbius Inversion Overlay
# ══════════════════════════════════════════════════════════════════════

def crystal_4d(cx: float, cy: float, size: float,
               show_mobius: bool = True, show_containment: bool = True,
               **attrs) -> str:
    """Full 4D crystal projection: tesseract + Möbius twist + containment.

    Combines:
    1. 4D tesseract (16 vertices, 32 edges) with SFCR coloring
    2. Möbius strip overlay (the inversion/twist topology)
    3. Dimensional containment rings (3D→12D weave hierarchy)
    """
    children = []

    # Containment rings (background)
    if show_containment:
        children.append(dimensional_containment(cx, cy, size * 1.8))

    # Tesseract core with SFCR coloring
    # 16 vertices of 4D hypercube at (±1,±1,±1,±1)
    verts_4d = []
    for i in range(16):
        x = 1 if i & 1 else -1
        y = 1 if i & 2 else -1
        z = 1 if i & 4 else -1
        w = 1 if i & 8 else -1
        verts_4d.append((x, y, z, w))

    pts = [_project_4d(v[0], v[1], v[2], v[3], cx, cy, size * 0.5)
           for v in verts_4d]

    # Edges: connect vertices differing by exactly 1 coordinate
    edge_defaults = {"stroke_width": "1.2"}
    edge_colors = ["#8B4513", "#DC143C", "#4169E1", "#228B22"]  # SFCR
    for i in range(16):
        for bit in range(4):
            j = i ^ (1 << bit)
            if j > i:
                color = edge_colors[bit]
                children.append(line(pts[i][0], pts[i][1],
                                     pts[j][0], pts[j][1],
                                     stroke=color, **edge_defaults))

    # Vertex dots
    for i, p in enumerate(pts):
        # Color by dominant SFCR element based on sign pattern
        signs = verts_4d[i]
        face_idx = sum(1 for s in signs if s > 0) % 4
        color = edge_colors[face_idx]
        children.append(circle(p[0], p[1], 3,
                               fill=color, stroke="#333", stroke_width="0.5"))

    # Möbius overlay (the inversion topology)
    if show_mobius:
        children.append(mobius_strip(cx, cy, size * 0.7, w=0.15,
                                    n_steps=48, n_strips=6,
                                    stroke="#9b59b6", stroke_width="0.5",
                                    stroke_opacity="0.6"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  SIGMA-60 — Icosahedral 60-View Field
# ══════════════════════════════════════════════════════════════════════

def sigma60_field(cx: float, cy: float, size: float, **attrs) -> str:
    """Sigma-60 observation field: 12 archetypes × 5 golden rotations.

    Renders as 12 radial spokes (archetypes) each with 5 dots (rotations)
    arranged on an icosahedral projection.
    """
    defaults = {"stroke": "#333", "stroke_width": "0.8"}
    defaults.update(attrs)

    children = []
    face_cycle = ["S", "F", "C", "R"]

    for arch in range(12):
        # Each archetype at 30° intervals
        base_angle = arch * TAU / 12
        color = SFCR_COLORS[face_cycle[arch % 4]]

        # Spoke line
        x1 = cx + size * 0.15 * math.cos(base_angle)
        y1 = cy - size * 0.15 * math.sin(base_angle)
        x2 = cx + size * math.cos(base_angle)
        y2 = cy - size * math.sin(base_angle)
        children.append(line(x1, y1, x2, y2,
                             stroke=color, stroke_width="1.5"))

        # 5 golden-rotation dots along spoke
        for rot in range(5):
            # PHI-spaced along the spoke
            t = 0.3 + 0.7 * (rot / 4)
            golden_offset = rot * TAU / 5 * 0.05  # subtle spiral
            r = size * t
            angle = base_angle + golden_offset
            px = cx + r * math.cos(angle)
            py = cy - r * math.sin(angle)
            dot_r = 2.5 + rot * 0.5
            children.append(circle(px, py, dot_r,
                                   fill=color, stroke="#fff",
                                   stroke_width="0.5"))

    # Archetype labels
    for arch in range(12):
        angle = arch * TAU / 12
        lx = cx + (size + 15) * math.cos(angle)
        ly = cy - (size + 15) * math.sin(angle)
        children.append(text(lx - 5, ly + 4, f"A{arch + 1}",
                             font_size="9", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  WEAVE WHEEL — Odd-Prime Transformation Operators
# ══════════════════════════════════════════════════════════════════════

def weave_wheel(cx: float, cy: float, size: float,
                order: int = 3, **attrs) -> str:
    """Visualize a weave operator W_n as a rotating wheel.

    order: 3, 5, 7, or 9 (the odd-prime weave operators).
    Shows the transformation cycle and containment structure.
    """
    defaults = {"stroke": "#333", "stroke_width": "1.5", "fill": "none"}
    defaults.update(attrs)

    colors = {3: "#e74c3c", 5: "#2ecc71", 7: "#3498db", 9: "#9b59b6"}
    color = colors.get(order, "#333")

    children = []

    # Outer ring
    children.append(circle(cx, cy, size, stroke=color, stroke_width="2",
                           fill=color, fill_opacity="0.05"))

    # Inner nodes at each station
    for i in range(order):
        angle = i * TAU / order - TAU / 4  # start from top
        px = cx + size * 0.8 * math.cos(angle)
        py = cy + size * 0.8 * math.sin(angle)

        children.append(circle(px, py, size * 0.08,
                               fill=color, stroke="#fff", stroke_width="1"))

        # Station label
        children.append(text(px - 3, py + 4, str(i + 1),
                             font_size="9", fill="#fff",
                             font_weight="bold"))

    # Transformation arrows (connect each station to next)
    for i in range(order):
        a1 = i * TAU / order - TAU / 4
        a2 = ((i + 1) % order) * TAU / order - TAU / 4
        r = size * 0.8
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)
        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)

        # Curved arrow via path
        mx = cx + r * 1.05 * math.cos((a1 + a2) / 2)
        my = cy + r * 1.05 * math.sin((a1 + a2) / 2)
        d = f"M {_fmt(x1)},{_fmt(y1)} Q {_fmt(mx)},{_fmt(my)} {_fmt(x2)},{_fmt(y2)}"
        children.append(path(d, stroke=color, stroke_width="1",
                             fill="none"))

    # Center label
    children.append(text(cx - 8, cy + 4, f"W{order}",
                         font_size="14", fill=color,
                         font_weight="bold"))

    return group(children)
