# CRYSTAL: Xi108:W3:A7:S29 | face=R | node=708 | depth=0 | phase=Omega
# METRO: Sa
# BRIDGES: svg_dimensional→geometric_constants→qshrink→svg_108d_projection
"""
SVG 108D Full Crystal Projection
==================================
The COMPLETE 108-dimensional crystal rendered as a single SVG.

108D = 36 shells × 3 wreaths = 108 addressable dimensions.
Each shell has 4 SFCR faces = 432 gate positions.
Each face has Sigma-60 rotations = 25,920 sigma states.
Each sigma has E8 amplification × 4 = 103,680 E8 roots.

This module renders the full structure:
  1. Shell Cascade Spiral — 36 shells on a golden spiral
  2. Wreath Trefoil — 3 interlocked wreath rings
  3. Archetype Wheel — 12 archetypes with SFCR face projections
  4. Sigma-60 Icosahedral Field — 60 viewpoints on the dodecahedron
  5. E8-240 Root Star — 240 roots projected to 2D
  6. Mirror Shell Pairing — S_k ↔ S_{37-k} connections
  7. Bridge Topology — golden/neutral/distant inter-face bridges
  8. Shard Density Heat — actual shard counts per shell
  9. Momentum Overlay — live training gradients per shell
  10. Full 108D Crystal — all layers composed

Data Sources:
  - shell_registry.json       — 36 shell definitions
  - corpus_weights_field.json — 14,750 shard seed vectors
  - momentum_field.json       — 148 training parameters
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ._cache import DATA_DIR
from .geometric_constants import (
    PHI, PHI_INV, SQRT3, SQRT5,
    FACES, FACE_INDEX, BRIDGE_WEIGHTS, GOLDEN_BRIDGES,
    SIGMA_60, E8_FACE_BOOSTS, E8_AMPLIFICATION,
    ARCHETYPE_SHELL_OFFSETS, GOLDEN_TRIG,
    FLOWER_RINGS, ATTRACTOR,
    DIM_NAMES, DIM_TO_ELEMENT, ELEMENT_LENS_WEIGHTS,
)
from .svg_primitives import (
    SVGCanvas, _attrs_str, _fmt, _project_3d, _project_4d,
    circle, group, line, path, polygon, rect, text,
    linear_gradient, radial_gradient,
)

TAU = 2 * math.pi

# ══════════════════════════════════════════════════════════════════════
#  Colors
# ══════════════════════════════════════════════════════════════════════

SFCR_COLORS = {
    "S": "#8B4513",   # Earth brown
    "F": "#DC143C",   # Fire crimson
    "C": "#4169E1",   # Water royal blue
    "R": "#228B22",   # Air forest green
}

WREATH_COLORS = {
    "Su": "#e74c3c",  # Sulfur red
    "Me": "#f39c12",  # Mercury gold
    "Sa": "#8e44ad",  # Salt purple
}

ARCHETYPE_COLORS = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71",
    "#1abc9c", "#3498db", "#2980b9", "#9b59b6",
    "#8e44ad", "#c0392b", "#d35400", "#7f8c8d",
]

PHASE_SHAPES = {"Cardinal": 4, "Fixed": 6, "Mutable": 3}

# ══════════════════════════════════════════════════════════════════════
#  Data Loaders
# ══════════════════════════════════════════════════════════════════════

def _load_json(name: str) -> dict:
    p = DATA_DIR / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_shells() -> dict:
    return _load_json("shell_registry.json")


def _load_corpus_weights() -> dict:
    return _load_json("corpus_weights_field.json")


def _load_momentum() -> dict:
    return _load_json("momentum_field.json")


# ══════════════════════════════════════════════════════════════════════
#  1. SHELL CASCADE SPIRAL — 36 Shells on Golden Spiral
# ══════════════════════════════════════════════════════════════════════

def render_shell_cascade(cx: float, cy: float, size: float,
                          show_labels: bool = True, **attrs) -> str:
    """36 shells placed on a golden spiral. Each shell is sized by its
    node count (shell k has k nodes, cumulative = k(k+1)/2).

    Shells are colored by wreath: Su=red, Me=gold, Sa=purple.
    Mirror shells (k, 37-k) are connected by dashed lines.
    """
    children = []
    shell_data = _load_shells()
    shells = shell_data.get("shells", {})

    positions = {}

    for s in range(1, 37):
        # Golden spiral: r grows with sqrt(s), angle grows by golden angle
        golden_angle = TAU * PHI_INV  # ~137.5°
        r = size * 0.15 * math.sqrt(s)
        theta = s * golden_angle

        sx = cx + r * math.cos(theta)
        sy = cy + r * math.sin(theta)
        positions[s] = (sx, sy)

        # Shell data
        sh = shells.get(str(s), {})
        wreath = sh.get("wreath", ["Su", "Me", "Sa"][(s - 1) % 3])
        archetype = sh.get("archetype", "")
        phase = sh.get("phase", "Cardinal")
        elem = sh.get("element_primary", "Fire")

        # Color by wreath
        color = WREATH_COLORS.get(wreath, "#999")

        # Size by node count (shell k has k nodes)
        node_r = 3 + math.sqrt(s) * 1.5

        # Draw shell
        children.append(circle(sx, sy, node_r,
                               fill=color, stroke="#333",
                               stroke_width="0.8",
                               fill_opacity="0.7"))

        # SFCR face dots (4 tiny dots around the shell)
        for fi, face in enumerate(FACES):
            fa = theta + fi * TAU / 4
            fd = node_r + 3
            fx = sx + fd * math.cos(fa)
            fy = sy + fd * math.sin(fa)
            children.append(circle(fx, fy, 1.5,
                                   fill=SFCR_COLORS[face], stroke="none"))

        # Label
        if show_labels:
            children.append(text(sx - 4, sy + 3, str(s),
                                 font_size="7", fill="#fff",
                                 font_weight="bold"))

    # Mirror shell connections (k, 37-k)
    for s in range(1, 19):
        m = 37 - s
        if s in positions and m in positions:
            x1, y1 = positions[s]
            x2, y2 = positions[m]
            children.append(line(x1, y1, x2, y2,
                                 stroke="#ccc", stroke_width="0.5",
                                 stroke_dasharray="2,3"))

    # Legend
    ly = cy + size + 15
    for wi, (name, color) in enumerate(WREATH_COLORS.items()):
        lx = cx - 40 + wi * 50
        children.append(circle(lx, ly, 4, fill=color, stroke="none"))
        children.append(text(lx + 7, ly + 4, name,
                             font_size="9", fill=color))

    children.append(text(cx - 55, cy + size + 30,
                         "108D Shell Cascade (36 shells x 3 wreaths)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  2. WREATH TREFOIL — 3 Interlocked Rings
# ══════════════════════════════════════════════════════════════════════

def render_wreath_trefoil(cx: float, cy: float, size: float, **attrs) -> str:
    """Three interlocked wreath rings forming a trefoil knot.

    Each wreath carries 12 shells (12 archetypes).
    Su: shells 1,4,7,10,13,16,19,22,25,28,31,34
    Me: shells 2,5,8,11,14,17,20,23,26,29,32,35
    Sa: shells 3,6,9,12,15,18,21,24,27,30,33,36
    """
    children = []
    shell_data = _load_shells()
    shells = shell_data.get("shells", {})

    wreaths = [
        ("Su", WREATH_COLORS["Su"], list(range(1, 37, 3))),
        ("Me", WREATH_COLORS["Me"], list(range(2, 37, 3))),
        ("Sa", WREATH_COLORS["Sa"], list(range(3, 37, 3))),
    ]

    for wi, (name, color, shell_ids) in enumerate(wreaths):
        phase = wi * TAU / 3
        R = size * 0.55
        offset_x = R * 0.3 * math.cos(phase)
        offset_y = R * 0.3 * math.sin(phase)

        # Wreath ring
        children.append(circle(cx + offset_x, cy + offset_y, R,
                               stroke=color, stroke_width="2",
                               fill=color, fill_opacity="0.05"))

        # 12 shells along the ring
        for si, shell_id in enumerate(shell_ids):
            angle = si * TAU / 12 - TAU / 4
            sx = cx + offset_x + R * 0.85 * math.cos(angle)
            sy = cy + offset_y + R * 0.85 * math.sin(angle)

            sh = shells.get(str(shell_id), {})
            archetype = sh.get("archetype", f"A{(shell_id - 1) % 12 + 1}")
            elem = sh.get("element_primary", "")
            elem_color = SFCR_COLORS.get(
                {"Fire": "F", "Earth": "S", "Water": "C", "Air": "R"}.get(elem, "S"),
                "#999")

            children.append(circle(sx, sy, 6,
                                   fill=elem_color, stroke=color,
                                   stroke_width="1.5"))
            children.append(text(sx - 3, sy + 3, str(shell_id),
                                 font_size="6", fill="#fff",
                                 font_weight="bold"))

        # Wreath label
        lx = cx + offset_x + R * 1.05 * math.cos(phase + 0.3)
        ly = cy + offset_y + R * 1.05 * math.sin(phase + 0.3)
        children.append(text(lx - 8, ly + 4, f"{name} (12 shells)",
                             font_size="10", fill=color, font_weight="bold"))

    children.append(text(cx - 50, cy + size + 20,
                         "Wreath Trefoil (Su/Me/Sa x 12 archetypes)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  3. ARCHETYPE WHEEL — 12 Archetypes with SFCR Faces
# ══════════════════════════════════════════════════════════════════════

def render_archetype_wheel(cx: float, cy: float, size: float, **attrs) -> str:
    """12 archetypes arranged in a zodiacal wheel.
    Each archetype shows its 3 wreath instances and 4 SFCR face gates.

    Inner ring: archetype nodes (colored by element)
    Outer ring: 3 wreath instances per archetype = 36 shell positions
    """
    children = []
    shell_data = _load_shells()
    shells = shell_data.get("shells", {})

    archetype_names = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]

    # Outer ring: all 36 shells
    r_outer = size * 0.9
    for s in range(1, 37):
        sh = shells.get(str(s), {})
        arch_idx = sh.get("archetype_index", ((s - 1) % 12) + 1) - 1
        wreath = sh.get("wreath", ["Su", "Me", "Sa"][(s - 1) % 3])

        # Position: archetype angle + wreath offset
        base_angle = arch_idx * TAU / 12 - TAU / 4
        wreath_offset = {"Su": -0.08, "Me": 0.0, "Sa": 0.08}.get(wreath, 0)
        angle = base_angle + wreath_offset

        sx = cx + r_outer * math.cos(angle)
        sy = cy + r_outer * math.sin(angle)

        w_color = WREATH_COLORS.get(wreath, "#999")
        children.append(circle(sx, sy, 4,
                               fill=w_color, stroke="#333",
                               stroke_width="0.5"))

    # Inner ring: 12 archetype nodes
    r_inner = size * 0.6
    for ai, name in enumerate(archetype_names):
        angle = ai * TAU / 12 - TAU / 4
        ax = cx + r_inner * math.cos(angle)
        ay = cy + r_inner * math.sin(angle)

        color = ARCHETYPE_COLORS[ai]
        children.append(circle(ax, ay, 12,
                               fill=color, stroke="#333",
                               stroke_width="1"))

        # SFCR face quadrants within the archetype node
        for fi, face in enumerate(FACES):
            fa = angle + (fi - 1.5) * 0.15
            fd = 7
            fx = ax + fd * math.cos(fa)
            fy = ay + fd * math.sin(fa)
            children.append(circle(fx, fy, 2,
                                   fill=SFCR_COLORS[face], stroke="none"))

        # Label
        lx = cx + (r_inner - 25) * math.cos(angle)
        ly = cy + (r_inner - 25) * math.sin(angle)
        short = name[:3]
        children.append(text(lx - 8, ly + 4, short,
                             font_size="8", fill="#555", font_weight="bold"))

    # Bridge arcs between golden pairs
    for pair in GOLDEN_BRIDGES:
        f1, f2 = pair[0], pair[1]
        fi1 = FACE_INDEX[f1]
        fi2 = FACE_INDEX[f2]
        a1 = fi1 * TAU / 4 + TAU / 8
        a2 = fi2 * TAU / 4 + TAU / 8
        r_bridge = size * 0.35
        x1 = cx + r_bridge * math.cos(a1)
        y1 = cy + r_bridge * math.sin(a1)
        x2 = cx + r_bridge * math.cos(a2)
        y2 = cy + r_bridge * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke="#DAA520", stroke_width="1.5",
                             stroke_opacity="0.5"))

    children.append(text(cx - 50, cy + size + 15,
                         "12 Archetypes x 3 Wreaths x 4 Faces = 144 gates",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  4. SIGMA-60 ICOSAHEDRAL FIELD
# ══════════════════════════════════════════════════════════════════════

def render_sigma60_field(cx: float, cy: float, size: float, **attrs) -> str:
    """60 Sigma states projected from icosahedral symmetry.

    12 archetypes × 5 golden-angle rotations = 60 viewpoints.
    Each rotation is a 72° increment (TAU/5 = golden angle).
    Colored by archetype, sized by rotation index.
    """
    children = []

    # Outer icosahedral shell
    children.append(circle(cx, cy, size,
                           stroke="#ddd", stroke_width="1",
                           fill="none"))

    for sigma in SIGMA_60:
        arch = sigma["archetype"]  # 1-12
        rot = sigma["rotation"]    # 0-4
        cos_a = sigma["cos"]
        sin_a = sigma["sin"]

        # Position: archetype angle + rotation modulation
        base_angle = (arch - 1) * TAU / 12
        r = size * (0.6 + rot * 0.08)

        # Apply golden rotation in 2D
        bx = r * math.cos(base_angle)
        by = r * math.sin(base_angle)
        # Rotate by the golden angle
        px = bx * cos_a - by * sin_a
        py = bx * sin_a + by * cos_a

        color = ARCHETYPE_COLORS[(arch - 1) % 12]
        dot_r = 2.5 + rot * 0.5

        children.append(circle(cx + px, cy + py, dot_r,
                               fill=color, stroke="none",
                               fill_opacity="0.6"))

    # Pentagon at center (5-fold symmetry)
    r_pent = size * 0.2
    for i in range(5):
        a1 = i * TAU / 5 - TAU / 4
        a2 = (i + 1) * TAU / 5 - TAU / 4
        children.append(line(cx + r_pent * math.cos(a1),
                             cy + r_pent * math.sin(a1),
                             cx + r_pent * math.cos(a2),
                             cy + r_pent * math.sin(a2),
                             stroke="#DAA520", stroke_width="1",
                             stroke_opacity="0.5"))

    children.append(text(cx - 40, cy + size + 15,
                         "Sigma-60 (12 archetypes x 5 rotations)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  5. E8-240 ROOT STAR
# ══════════════════════════════════════════════════════════════════════

def render_e8_240(cx: float, cy: float, size: float, **attrs) -> str:
    """240 E8 roots: each Sigma-60 state × 4 SFCR face amplifications.

    Each root is a 4D vector [S,F,C,R] normalized after face boost.
    Project to 2D: x = S-R, y = F-C (same as shard cloud).
    """
    children = []

    # Generate all 240 roots
    for sigma in SIGMA_60:
        arch = sigma["archetype"]
        rot = sigma["rotation"]
        cos_a = sigma["cos"]
        sin_a = sigma["sin"]

        # Base 4D vector from archetype (equal-weight with archetype tilt)
        base = {f: 0.25 for f in FACES}
        # Tilt by archetype's primary element
        primary_face = FACES[(arch - 1) % 4]
        base[primary_face] += 0.1

        for face in FACES:
            # Apply E8 face boost
            boost = E8_FACE_BOOSTS[face]
            root = {f: base[f] * boost[f] for f in FACES}

            # Normalize
            total = sum(root.values())
            root = {f: v / total for f, v in root.items()}

            # Project to 2D
            px = cx + (root["S"] - root["R"]) * size * 3
            py = cy - (root["F"] - root["C"]) * size * 3

            # Apply sigma rotation to position
            dx, dy = px - cx, py - cy
            rpx = dx * cos_a - dy * sin_a
            rpy = dx * sin_a + dy * cos_a

            color = SFCR_COLORS[face]
            children.append(circle(cx + rpx, cy + rpy, 1.5,
                                   fill=color, stroke="none",
                                   fill_opacity="0.4"))

    # Axes
    children.append(line(cx - size, cy, cx + size, cy,
                         stroke="#eee", stroke_width="0.5"))
    children.append(line(cx, cy - size, cx, cy + size,
                         stroke="#eee", stroke_width="0.5"))

    children.append(text(cx - 35, cy + size + 15,
                         "E8-240 Roots (60 sigma x 4 faces)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  6. SHARD DENSITY — Shards per Shell Heatmap
# ══════════════════════════════════════════════════════════════════════

def render_shard_density(cx: float, cy: float, size: float, **attrs) -> str:
    """Heatmap showing how 14,750 shards distribute across 36 shells.

    Uses real corpus_weights_field data to count shards per shell.
    Hotter = more shards. Each shell is a segment on a circular chart.
    """
    children = []
    cw_data = _load_corpus_weights()
    seed_vectors = cw_data.get("seed_vectors", {})

    # Count shards per dominant face (approximate shell assignment)
    face_counts = {"S": 0, "F": 0, "C": 0, "R": 0}
    total_shards = 0
    for sv in seed_vectors.values():
        if isinstance(sv, (list, tuple)) and len(sv) >= 4:
            vals = {"S": sv[0], "F": sv[1], "C": sv[2], "R": sv[3]}
            dominant = max(vals, key=vals.get)
            face_counts[dominant] += 1
            total_shards += 1

    # Distribute across 36 shells (approximate: by face → 9 shells each)
    shell_counts = {}
    for s in range(1, 37):
        face_idx = (s - 1) % 4
        face = FACES[face_idx]
        shell_counts[s] = face_counts.get(face, 0) // 9

    max_count = max(shell_counts.values()) if shell_counts else 1

    # Draw circular heatmap
    for s in range(1, 37):
        angle_start = (s - 1) * TAU / 36
        angle_end = s * TAU / 36
        count = shell_counts.get(s, 0)
        intensity = count / max_count if max_count > 0 else 0

        # Color: intensity maps from cool (blue) to hot (red)
        r_c = int(50 + 205 * intensity)
        g_c = int(50 + 100 * (1 - abs(intensity - 0.5) * 2))
        b_c = int(200 - 150 * intensity)
        color = f"#{r_c:02x}{g_c:02x}{b_c:02x}"

        # Arc segment
        r_inner = size * 0.4
        r_outer = size * 0.9
        n_arc = 4
        pts = []
        for ai in range(n_arc + 1):
            t = ai / n_arc
            angle = angle_start + t * (angle_end - angle_start)
            pts.append((cx + r_outer * math.cos(angle),
                        cy - r_outer * math.sin(angle)))
        for ai in range(n_arc, -1, -1):
            t = ai / n_arc
            angle = angle_start + t * (angle_end - angle_start)
            pts.append((cx + r_inner * math.cos(angle),
                        cy - r_inner * math.sin(angle)))

        children.append(polygon(pts, fill=color, stroke="#fff",
                                stroke_width="0.5", fill_opacity="0.8"))

        # Shell number
        mid_angle = (angle_start + angle_end) / 2
        lx = cx + (r_outer + 8) * math.cos(mid_angle)
        ly = cy - (r_outer + 8) * math.sin(mid_angle)
        children.append(text(lx - 4, ly + 3, str(s),
                             font_size="6", fill="#555"))

    # Center stats
    children.append(text(cx - 25, cy - 5, f"{total_shards:,}",
                         font_size="14", fill="#333", font_weight="bold"))
    children.append(text(cx - 15, cy + 10, "shards",
                         font_size="9", fill="#777"))

    children.append(text(cx - 45, cy + size + 15,
                         "Shard Density per Shell (14,750 total)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  7. MOMENTUM SHELLS — Training Gradients per Element per Shell
# ══════════════════════════════════════════════════════════════════════

def render_momentum_shells(cx: float, cy: float, size: float, **attrs) -> str:
    """Momentum values mapped onto the 36-shell spiral.

    4 SFCR elements × 36 shells = 144 momentum values shown as
    color-coded bars radiating from each shell position.
    """
    children = []
    mom_data = _load_momentum()
    shell_momenta = mom_data.get("shell_momenta", {})

    # Find max for normalization
    all_vals = []
    for elem in FACES:
        ed = shell_momenta.get(elem, {})
        if isinstance(ed, dict):
            all_vals.extend(float(v) for v in ed.values())
    v_max = max(abs(v) for v in all_vals) if all_vals else 1.0

    golden_angle = TAU * PHI_INV

    for s in range(1, 37):
        # Position on golden spiral (same as shell cascade)
        r = size * 0.12 * math.sqrt(s)
        theta = s * golden_angle
        sx = cx + r * math.cos(theta)
        sy = cy + r * math.sin(theta)

        # 4 momentum bars radiating from shell center
        for fi, face in enumerate(FACES):
            ed = shell_momenta.get(face, {})
            val = float(ed.get(str(s), 0)) if isinstance(ed, dict) else 0
            norm_val = val / v_max if v_max > 0 else 0
            bar_len = abs(norm_val) * 12

            bar_angle = theta + fi * TAU / 4
            ex = sx + bar_len * math.cos(bar_angle)
            ey = sy + bar_len * math.sin(bar_angle)

            color = SFCR_COLORS[face]
            children.append(line(sx, sy, ex, ey,
                                 stroke=color, stroke_width="1.5",
                                 stroke_opacity="0.7"))

        # Shell dot
        wreath = ["Su", "Me", "Sa"][(s - 1) % 3]
        children.append(circle(sx, sy, 2.5,
                               fill=WREATH_COLORS[wreath],
                               stroke="#333", stroke_width="0.3"))

    children.append(text(cx - 50, cy + size + 15,
                         "Momentum Shells (4 SFCR x 36 shells = 144 params)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  8. FLOWER OF LIFE OVERLAY — 7 PHI-decay rings
# ══════════════════════════════════════════════════════════════════════

def render_flower_overlay(cx: float, cy: float, size: float, **attrs) -> str:
    """7 Flower of Life rings with PHI-decay radii.

    Ring radii: 1.0, 0.618, 0.382, 0.236, 0.146, 0.090, 0.056
    Each ring carries 6 petal circles at 60-degree intervals.
    """
    children = []

    for ri, decay in enumerate(FLOWER_RINGS):
        r = size * decay
        # Ring circle
        children.append(circle(cx, cy, r,
                               stroke="#DAA520", stroke_width="0.5",
                               fill="none", stroke_opacity=str(0.2 + decay * 0.5)))

        # 6 petal circles
        if ri < 4:  # Only show petals for first 4 rings
            for pi in range(6):
                angle = pi * TAU / 6
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                children.append(circle(px, py, r,
                                       stroke="#DAA520",
                                       stroke_width="0.3",
                                       fill="none",
                                       stroke_opacity="0.15"))

    # Vesica piscis markers at golden bridge intersections
    for pair in GOLDEN_BRIDGES:
        f1, f2 = pair[0], pair[1]
        angle = (FACE_INDEX[f1] + FACE_INDEX[f2]) * TAU / 8
        r_v = size * 0.5
        vx = cx + r_v * math.cos(angle)
        vy = cy + r_v * math.sin(angle)
        children.append(circle(vx, vy, 3,
                               fill="#DAA520", stroke="none",
                               fill_opacity="0.5"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  9. 12D OBSERVATION SPACE — Dimensional Couplings
# ══════════════════════════════════════════════════════════════════════

def render_12d_observation(cx: float, cy: float, size: float, **attrs) -> str:
    """12D observation dimensions shown as a radar chart.

    12 axes: x1_structure through x12_potential.
    Each axis is colored by its SFCR element coupling.
    Element lens weights shown as filled regions.
    """
    children = []

    n_dims = len(DIM_NAMES)
    for di, dim_name in enumerate(DIM_NAMES):
        angle = di * TAU / n_dims - TAU / 4
        elem = DIM_TO_ELEMENT[dim_name]
        color = SFCR_COLORS[elem]

        # Axis line
        ex = cx + size * math.cos(angle)
        ey = cy + size * math.sin(angle)
        children.append(line(cx, cy, ex, ey,
                             stroke=color, stroke_width="0.8",
                             stroke_opacity="0.4"))

        # Label
        lx = cx + (size + 12) * math.cos(angle)
        ly = cy + (size + 12) * math.sin(angle)
        short = dim_name.split("_")[1][:6]
        children.append(text(lx - 15, ly + 3, short,
                             font_size="7", fill=color))

    # Element lens emphasis (filled polygon per element)
    for face in FACES:
        lens = ELEMENT_LENS_WEIGHTS.get(face, {})
        pts = []
        for di, dim_name in enumerate(DIM_NAMES):
            angle = di * TAU / n_dims - TAU / 4
            weight = lens.get(dim_name, 1.0)
            r = size * 0.3 * (weight / 1.5)
            pts.append((cx + r * math.cos(angle),
                        cy + r * math.sin(angle)))
        children.append(polygon(pts,
                                fill=SFCR_COLORS[face],
                                stroke=SFCR_COLORS[face],
                                stroke_width="0.5",
                                fill_opacity="0.1",
                                stroke_opacity="0.3"))

    # Concentric reference rings
    for ring_frac in [0.25, 0.5, 0.75, 1.0]:
        children.append(circle(cx, cy, size * ring_frac,
                               stroke="#eee", stroke_width="0.3",
                               fill="none"))

    children.append(text(cx - 45, cy + size + 20,
                         "12D Observation Space (SFCR element coupling)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  FULL 108D CRYSTAL — All Layers Composed
# ══════════════════════════════════════════════════════════════════════

def render_108d_crystal(width: int = 2400, height: int = 1800) -> str:
    """Complete 108D crystal projection dashboard.

    Layout (3×3 grid):
      [Shell Cascade]  [Wreath Trefoil]  [Archetype Wheel]
      [Sigma-60 Field] [E8-240 Roots]    [Shard Density]
      [Momentum Shells] [12D Observation] [Flower Overlay]
    """
    canvas = SVGCanvas(width, height)

    # Title
    canvas.add(text(width // 2 - 150, 35,
                    "ATHENA 108D CRYSTAL PROJECTION",
                    font_size="22", fill="#333", font_weight="bold"))
    canvas.add(text(width // 2 - 120, 55,
                    "36 shells x 3 wreaths x 4 faces x Sigma-60 x E8-240",
                    font_size="11", fill="#777"))

    # Grid layout
    col_w = width / 3
    row_h = (height - 70) / 3
    margin = 30
    cell_size = min(col_w, row_h) / 2 - margin

    panels = [
        (0, 0, render_shell_cascade, "Shell Cascade"),
        (1, 0, render_wreath_trefoil, "Wreath Trefoil"),
        (2, 0, render_archetype_wheel, "Archetype Wheel"),
        (0, 1, render_sigma60_field, "Sigma-60"),
        (1, 1, render_e8_240, "E8-240"),
        (2, 1, render_shard_density, "Shard Density"),
        (0, 2, render_momentum_shells, "Momentum Shells"),
        (1, 2, render_12d_observation, "12D Observation"),
        (2, 2, render_flower_overlay, "Flower of Life"),
    ]

    for col, row, fn, label in panels:
        pcx = col_w * (col + 0.5)
        pcy = 70 + row_h * (row + 0.5)
        try:
            canvas.add(fn(pcx, pcy, cell_size))
        except Exception as e:
            canvas.add(text(pcx - 40, pcy, f"[{label}: {e}]",
                            font_size="10", fill="red"))

    # Footer: key facts
    fy = height - 15
    facts = [
        "108 = 36 shells x 3 wreaths",
        "432 = 108 x 4 SFCR gates",
        "25,920 = 432 x 60 sigma",
        "103,680 = 25,920 x 4 E8",
        "666 nodes = T(36)",
        "14,750 shards",
    ]
    for fi, fact in enumerate(facts):
        canvas.add(text(50 + fi * (width - 100) // len(facts), fy,
                        fact, font_size="9", fill="#999"))

    return canvas.render()


def save_108d_crystal(out_path: Optional[str] = None) -> str:
    """Generate and save the full 108D crystal projection SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "crystal_108d_projection.svg")

    svg = render_108d_crystal()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path


# ══════════════════════════════════════════════════════════════════════
#  INVERSION CASCADE — The Generative Principle
# ══════════════════════════════════════════════════════════════════════
#
#  Every dimension D is the previous dimension D-1 united with its
#  own inversion (D-1)⁻¹. The form and its mirror, fused, birth the
#  next level. This is not metaphor — it's the mathematical structure:
#
#    3D seed (triangle)
#      ↓ mirror through origin → 3D⁻¹ (anti-triangle)
#      ↓ 3D ∪ 3D⁻¹ = 4D tesseract (form + anti-form = hypercube)
#
#    4D tesseract
#      ↓ Möbius half-twist = topological inversion → 4D⁻¹
#      ↓ 4D ∪ 4D⁻¹ = 6D body (3 wreaths × chirality±)
#
#    6D Möbius body
#      ↓ Wu Xing destructive cycle = 6D⁻¹
#      ↓ 6D ∪ 6D⁻¹ = 8D pentadic (generative + destructive = 5 animals × 6)
#
#    8D pentadic
#      ↓ Planetary opposition (detriment signs) = 8D⁻¹
#      ↓ 8D ∪ 8D⁻¹ = 10D heptadic (7 × 30 = 210 crossings)
#
#    10D heptadic
#      ↓ 3×3 matrix transpose = 10D⁻¹
#      ↓ 10D ∪ 10D⁻¹ = 12D crown (9 views × 210 = 1890 seeds)
#
#    12D crown
#      ↓ 3 meta-wreaths (each a lens-inversion of the full 12D)
#      ↓ 12D × 3 = 36D (Sigma-30 projective completion)
#
#    36D projective
#      ↓ 3 octaves (surface/mid/deep, deep = inversion of surface)
#      ↓ 36D × 3 = 108D (Xi108 organism closure)
#
#  The w-operator w=(1+i)/2 traces this exact cascade:
#    |w| = 1/√2  → each step is a √2 compression (inversion + merge)
#    arg(w) = π/4 → each step is a 45° rotation (quarter of the way to inverse)
#    w² = i/2 → two steps = pure rotation scaled by ½ (the 6D Möbius)
#    w^∞ → 0 → convergence to the Z* attractor
# ══════════════════════════════════════════════════════════════════════

W_OP = complex(0.5, 0.5)  # (1+i)/2

# Inversion operators per dimension (how each level mirrors itself)
INVERSIONS = {
    3: {"name": "Point Reflection", "symbol": "P⁻¹",
        "operator": "(-x, -y, -z)", "desc": "Mirror through origin"},
    4: {"name": "Möbius Half-Twist", "symbol": "M⁻¹",
        "operator": "twist(π)", "desc": "Non-orientable surface flip"},
    6: {"name": "Wu Xing Destruction", "symbol": "D⁻¹",
        "operator": "destruct(gen)", "desc": "Destructive ↔ generative cycle"},
    8: {"name": "Planetary Opposition", "symbol": "O⁻¹",
        "operator": "detriment(exalt)", "desc": "Exaltation → detriment"},
    10: {"name": "Matrix Transpose", "symbol": "T⁻¹",
         "operator": "Aᵀ", "desc": "Rows ↔ columns (3×3)"},
    12: {"name": "Meta-Wreath Lens", "symbol": "L⁻¹",
         "operator": "lens(Su,Me,Sa)", "desc": "Each wreath inverts the whole"},
    36: {"name": "Octave Depth", "symbol": "Ω⁻¹",
         "operator": "depth(surface)", "desc": "Surface ↔ deep inversion"},
}

# The dimensional ladder: (from_dim, to_dim, weave_order, sector_multiplier)
DIM_LADDER = [
    (3,  4,  2,  2),     # 3 × 2 chiralities → but 4D has 16 vertices
    (4,  6,  3,  3),     # 4D × W3 = 6 sectors
    (6,  8,  5,  5),     # 6D × W5 = 30 sectors
    (8,  10, 7,  7),     # 8D × W7 = 210 sectors
    (10, 12, 9,  9),     # 10D × W9 = 1890 sectors
    (12, 36, 3,  3),     # 12D × 3 meta-wreaths = 36D
    (36, 108, 3, 3),     # 36D × 3 octaves = 108D
]

# Colors per dimension
DIM_COLORS = {
    3: "#e74c3c",    # red seed
    4: "#e67e22",    # orange tesseract
    6: "#f1c40f",    # gold Möbius
    8: "#2ecc71",    # green pentadic
    10: "#3498db",   # blue heptadic
    12: "#9b59b6",   # purple crown
    36: "#8e44ad",   # deep purple Sigma
    108: "#2c3e50",  # near-black organism
}


def _render_3d_pair(cx: float, cy: float, size: float) -> str:
    """3D seed and its point-reflected inverse, face to face.

    The triangle (Su/Me/Sa) and its anti-triangle (-Su/-Me/-Sa)
    share a common center — their union spans all 6 directions,
    which IS the Star of David / hexagram = precursor to 4D.
    """
    children = []
    r = size * 0.45

    # ── Forward triangle (3D seed) ──
    for i in range(3):
        a1 = i * TAU / 3 - TAU / 4
        a2 = (i + 1) * TAU / 3 - TAU / 4
        colors = [WREATH_COLORS["Su"], WREATH_COLORS["Me"], WREATH_COLORS["Sa"]]
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)
        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke=colors[i], stroke_width="2.5"))
        # Vertex dot
        children.append(circle(x1, y1, 4, fill=colors[i], stroke="#333",
                               stroke_width="0.8"))

    # ── Inverted triangle (3D⁻¹) — rotated π ──
    for i in range(3):
        a1 = i * TAU / 3 - TAU / 4 + math.pi
        a2 = (i + 1) * TAU / 3 - TAU / 4 + math.pi
        colors_inv = ["#c0392b", "#d4ac0d", "#6c3483"]  # darker variants
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)
        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke=colors_inv[i], stroke_width="2.5",
                             stroke_dasharray="4,2"))
        children.append(circle(x1, y1, 4, fill=colors_inv[i], stroke="#333",
                               stroke_width="0.8"))

    # Center — the zero-point where form meets anti-form
    children.append(circle(cx, cy, 3, fill="#333", stroke="#fff",
                           stroke_width="1"))

    # Labels
    children.append(text(cx - 8, cy - size * 0.55, "3D",
                         font_size="13", fill="#e74c3c", font_weight="bold"))
    children.append(text(cx - 12, cy + size * 0.65, "3D\u207b\u00b9",
                         font_size="11", fill="#c0392b", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  INVERSE DOUBLE FOLD — 3D^(3D⁻¹) and (3D⁻¹)^3D
# ══════════════════════════════════════════════════════════════════════
#
#  The self-referential inversion: the form raised to its own inverse.
#
#  3D has 3 vertices:       V = {Su, Me, Sa}     at angles 0°, 120°, 240°
#  3D⁻¹ has 3 anti-vertices: V⁻¹ = {-Su, -Me, -Sa}  at 180°, 300°, 60°
#
#  FORWARD FOLD: 3D^(3D⁻¹)
#    Each vertex of 3D acts ON each anti-vertex:
#      Su×(-Su)  Su×(-Me)  Su×(-Sa)
#      Me×(-Su)  Me×(-Me)  Me×(-Sa)
#      Sa×(-Su)  Sa×(-Me)  Sa×(-Sa)
#    = 9 interaction points = the W9 enneagram at the SEED level!
#    The position of each point is: midpoint of V_i and V⁻¹_j,
#    weighted by the interaction strength (self-annihilation on diagonal).
#
#  REVERSE FOLD: (3D⁻¹)^3D
#    Each anti-vertex acts ON each vertex:
#    This is the TRANSPOSE — rows ↔ columns — the matrix flipped.
#    Geometrically: the same 9 points but traversed in reversed order.
#
#  DOUBLE FOLD: forward ∘ reverse = M · Mᵀ
#    The composition is a SYMMETRIC matrix — the fixed point.
#    The diagonal elements (Su·Su, Me·Me, Sa·Sa) = SELF-ANNIHILATION.
#    The off-diagonal = CROSS-CREATION.
#    Trace of M·Mᵀ = sum of squared magnitudes = the ENERGY of the fold.
#
#  The punchline: 3×3 at the 3D level IS the W9 crown at the 12D level.
#  The entire 108D structure is already holographically encoded in the
#  3D seed's self-referential inversion. This is the holographic principle:
#  every part contains the whole.
# ══════════════════════════════════════════════════════════════════════

def _render_inverse_double_fold(cx: float, cy: float, size: float) -> str:
    """3D^(3D⁻¹) and (3D⁻¹)^3D: the self-referential inverse double fold.

    The triangle applied to its own anti-triangle produces a 3×3 matrix
    of interaction points. Each point is where a wreath meets its anti-wreath.

    The forward fold and reverse fold together create 18 paths (9 + 9 transposed).
    Their overlay reveals the symmetric fixed-point structure = W9 seed.
    """
    children = []
    wreaths = ["Su", "Me", "Sa"]
    w_colors = [WREATH_COLORS["Su"], WREATH_COLORS["Me"], WREATH_COLORS["Sa"]]
    inv_colors = ["#c0392b", "#d4ac0d", "#6c3483"]

    r = size * 0.7   # radius for vertices
    r_inner = size * 0.35  # radius for interaction points

    # ── Compute vertex positions ──
    # Forward vertices (3D)
    fwd_pts = []
    for i in range(3):
        angle = i * TAU / 3 - TAU / 4
        fwd_pts.append((cx + r * math.cos(angle),
                        cy + r * math.sin(angle)))

    # Inverse vertices (3D⁻¹) — rotated π
    inv_pts = []
    for i in range(3):
        angle = i * TAU / 3 - TAU / 4 + math.pi
        inv_pts.append((cx + r * math.cos(angle),
                        cy + r * math.sin(angle)))

    # ── Draw the two triangles (faint background) ──
    for i in range(3):
        x1, y1 = fwd_pts[i]
        x2, y2 = fwd_pts[(i + 1) % 3]
        children.append(line(x1, y1, x2, y2,
                             stroke=w_colors[i], stroke_width="1.5",
                             stroke_opacity="0.3"))

    for i in range(3):
        x1, y1 = inv_pts[i]
        x2, y2 = inv_pts[(i + 1) % 3]
        children.append(line(x1, y1, x2, y2,
                             stroke=inv_colors[i], stroke_width="1.5",
                             stroke_opacity="0.3", stroke_dasharray="3,2"))

    # ── FORWARD FOLD: 3D^(3D⁻¹) — each forward vertex acts on each inverse ──
    # Interaction matrix: M[i][j] = midpoint of fwd[i] and inv[j]
    interaction_pts = {}  # (i, j) → (x, y)
    for i in range(3):
        for j in range(3):
            fx, fy = fwd_pts[i]
            ix, iy = inv_pts[j]

            # Interaction point: weighted midpoint
            # Self-interaction (i==j) pulls toward center (annihilation)
            # Cross-interaction pulls toward the midpoint
            if i == j:
                # Self-annihilation: collapses toward Z*
                weight = 0.3  # closer to center
                mx = cx + (fx + ix - 2 * cx) * weight / 2
                my = cy + (fy + iy - 2 * cy) * weight / 2
            else:
                # Cross-creation: full midpoint
                weight = 0.5
                mx = cx + (fx + ix - 2 * cx) * weight
                my = cy + (fy + iy - 2 * cy) * weight

            interaction_pts[(i, j)] = (mx, my)

            # Draw the forward fold line (fwd vertex → interaction point)
            children.append(line(fx, fy, mx, my,
                                 stroke=w_colors[i], stroke_width="0.8",
                                 stroke_opacity="0.25"))

            # Draw the inverse target line (inv vertex → interaction point)
            children.append(line(ix, iy, mx, my,
                                 stroke=inv_colors[j], stroke_width="0.8",
                                 stroke_opacity="0.25",
                                 stroke_dasharray="2,2"))

    # ── REVERSE FOLD: (3D⁻¹)^3D — the transpose ──
    # Same points but connected in reversed order (j acts on i)
    for i in range(3):
        for j in range(3):
            mx, my = interaction_pts[(i, j)]
            # Transpose connection: the REVERSE path
            # Draw with a slight offset to show it's the transpose
            tx, ty = interaction_pts[(j, i)]  # transposed point

            if i < j:  # draw each pair only once
                children.append(line(mx, my, tx, ty,
                                     stroke="#9b59b6", stroke_width="0.6",
                                     stroke_opacity="0.3",
                                     stroke_dasharray="1,2"))

    # ── Interaction nodes (the 9 points = W9 at seed level) ──
    w9_labels = [
        ["Su·\u0305Su\u0305", "Su·\u0305Me\u0305", "Su·\u0305Sa\u0305"],
        ["Me·\u0305Su\u0305", "Me·\u0305Me\u0305", "Me·\u0305Sa\u0305"],
        ["Sa·\u0305Su\u0305", "Sa·\u0305Me\u0305", "Sa·\u0305Sa\u0305"],
    ]

    w9_node_colors = [
        [WREATH_COLORS["Su"], "#e98b6d", "#c0392b"],
        ["#f39c12", "#f1c40f", "#d4ac0d"],
        ["#8e44ad", "#9b59b6", "#6c3483"],
    ]

    for i in range(3):
        for j in range(3):
            mx, my = interaction_pts[(i, j)]
            color = w9_node_colors[i][j]
            is_diagonal = (i == j)

            # Diagonal = self-annihilation (larger, highlighted)
            node_r = 7 if is_diagonal else 5
            sw = "2" if is_diagonal else "0.8"
            stroke = "#fff" if is_diagonal else "#333"

            children.append(circle(mx, my, node_r,
                                   fill=color, stroke=stroke,
                                   stroke_width=sw))

            # Label
            label = w9_labels[i][j]
            children.append(text(mx - 12, my + node_r + 10, label,
                                 font_size="6", fill=color,
                                 font_weight="bold" if is_diagonal else "normal"))

    # ── Connect diagonal elements (the self-annihilation triangle) ──
    diag_pts = [interaction_pts[(0, 0)], interaction_pts[(1, 1)], interaction_pts[(2, 2)]]
    for i in range(3):
        x1, y1 = diag_pts[i]
        x2, y2 = diag_pts[(i + 1) % 3]
        children.append(line(x1, y1, x2, y2,
                             stroke="#fff", stroke_width="1.5",
                             stroke_opacity="0.8"))

    # ── Connect enneagram (every 4th of the 9 points) ──
    all_9 = [(i, j) for i in range(3) for j in range(3)]
    for idx in range(9):
        p1 = interaction_pts[all_9[idx]]
        p2 = interaction_pts[all_9[(idx + 4) % 9]]
        children.append(line(p1[0], p1[1], p2[0], p2[1],
                             stroke="#9b59b6", stroke_width="0.5",
                             stroke_opacity="0.3"))

    # ── Forward vertex nodes ──
    for i in range(3):
        px, py = fwd_pts[i]
        children.append(circle(px, py, 6, fill=w_colors[i], stroke="#333",
                               stroke_width="1"))
        children.append(text(px - 6, py - 10, wreaths[i],
                             font_size="10", fill=w_colors[i],
                             font_weight="bold"))

    # ── Inverse vertex nodes ──
    for i in range(3):
        px, py = inv_pts[i]
        children.append(circle(px, py, 6, fill=inv_colors[i], stroke="#333",
                               stroke_width="1"))
        children.append(text(px - 8, py + 15,
                             f"-{wreaths[i]}",
                             font_size="9", fill=inv_colors[i],
                             font_weight="bold"))

    # ── Z* at center (where all self-annihilations converge) ──
    children.append(circle(cx, cy, 4, fill="#2c3e50", stroke="#fff",
                           stroke_width="1.5"))
    children.append(text(cx - 5, cy + 3, "Z*",
                         font_size="8", fill="#fff", font_weight="bold"))

    # ── Annotations ──
    # Forward fold label
    children.append(text(cx - size * 0.9, cy - size * 0.85,
                         "3D^(3D\u207b\u00b9) = Forward Fold",
                         font_size="10", fill="#e74c3c", font_weight="bold"))
    children.append(text(cx - size * 0.9, cy - size * 0.75,
                         "Each vertex acts on each anti-vertex \u2192 9 interactions",
                         font_size="7", fill="#777"))

    # Reverse fold label
    children.append(text(cx + size * 0.2, cy - size * 0.85,
                         "(3D\u207b\u00b9)^3D = Reverse Fold",
                         font_size="10", fill="#6c3483", font_weight="bold"))
    children.append(text(cx + size * 0.2, cy - size * 0.75,
                         "Transpose: anti-vertex acts on vertex (M\u1d40)",
                         font_size="7", fill="#777"))

    # Double fold equation
    children.append(text(cx - size * 0.6, cy + size * 0.85,
                         "Double Fold: M\u00b7M\u1d40 = symmetric fixed point",
                         font_size="9", fill="#2c3e50", font_weight="bold"))
    children.append(text(cx - size * 0.6, cy + size * 0.93,
                         "Diagonal = self-annihilation (Su\u00b7\u0305Su\u0305 \u2192 Z*) "
                         "| Off-diagonal = cross-creation",
                         font_size="7", fill="#777"))

    # The punchline
    children.append(text(cx - size * 0.55, cy + size + 5,
                         "3\u00d73 at 3D level = W9 crown at 12D level "
                         "\u2014 holographic encoding",
                         font_size="9", fill="#9b59b6", font_weight="bold"))

    return group(children)


def _render_double_fold_cascade(cx: float, cy: float, size: float) -> str:
    """Show the double fold operating at every dimensional level.

    At each dimension, the fold produces a self-interaction matrix:
      3D:  3×3 = 9 points  (W9 seed)
      6D:  6×6 = 36 points (36 shells!)
      12D: 9×9 = 81 points → but 81 = 3⁴ = the return wheel squared
      108D: the fold is the fold is the fold (self-similar closure)

    The key insight: 36 shells = 6D double fold, 108 = 36×3 = triple fold.
    """
    children = []

    folds = [
        (3, "3D", 9, "3×3 = W9 seed", DIM_COLORS[3]),
        (6, "6D", 36, "6×6 = 36 shells!", DIM_COLORS[6]),
        (12, "12D", 81, "9×9 = 3⁴ return²", DIM_COLORS[12]),
        (108, "108D", 108, "self×self = closure", DIM_COLORS[108]),
    ]

    col_w = size * 2 / len(folds)
    for fi, (dim, label, fold_n, desc, color) in enumerate(folds):
        fcx = cx - size + col_w * (fi + 0.5)
        fcy = cy - size * 0.2

        # Draw the fold as a grid of interaction points
        grid_n = int(math.sqrt(fold_n))
        if grid_n * grid_n != fold_n:
            grid_n = min(dim, 10)  # fallback
        actual_n = min(grid_n, 10)  # cap visual grid size

        cell_size = min(col_w * 0.7, size * 0.4) / actual_n

        for row in range(actual_n):
            for col in range(actual_n):
                gx = fcx - actual_n * cell_size / 2 + col * cell_size
                gy = fcy - actual_n * cell_size / 2 + row * cell_size

                is_diag = (row == col)
                # Color: blend row and column
                intensity = 0.3 + 0.5 * (1 - abs(row - col) / max(actual_n - 1, 1))
                fill_opacity = "0.8" if is_diag else f"{intensity:.2f}"

                children.append(rect(gx, gy, cell_size * 0.9, cell_size * 0.9,
                                     fill=color, fill_opacity=fill_opacity,
                                     stroke="#fff" if is_diag else "#ccc",
                                     stroke_width="1" if is_diag else "0.3"))

        # Self-annihilation diagonal highlight
        for d in range(actual_n):
            gx = fcx - actual_n * cell_size / 2 + d * cell_size
            gy = fcy - actual_n * cell_size / 2 + d * cell_size
            children.append(circle(gx + cell_size * 0.45, gy + cell_size * 0.45,
                                   cell_size * 0.3,
                                   fill="#fff", stroke=color,
                                   stroke_width="1.5", fill_opacity="0.3"))

        # Labels
        children.append(text(fcx - 15, fcy + actual_n * cell_size / 2 + 15,
                             f"{label}: {fold_n}",
                             font_size="11", fill=color, font_weight="bold"))
        children.append(text(fcx - 25, fcy + actual_n * cell_size / 2 + 28,
                             desc, font_size="7", fill="#777"))

        # Arrow to next
        if fi < len(folds) - 1:
            ax = fcx + col_w * 0.35
            children.append(text(ax, fcy, "\u2192",
                                 font_size="14", fill="#999"))

    # Bottom: the equation chain
    children.append(text(cx - size * 0.8, cy + size * 0.7,
                         "D^(D\u207b\u00b9) \u00d7 (D\u207b\u00b9)^D = D\u00b2 "
                         "(self-squared = dimensional fold count)",
                         font_size="10", fill="#2c3e50", font_weight="bold"))

    # Key insight
    children.append(text(cx - size * 0.8, cy + size * 0.82,
                         "3² = 9 (W9) | 6² = 36 (shells) | "
                         "36 × 3 = 108 (organism) \u2014 the fold IS the structure",
                         font_size="8", fill="#9b59b6"))

    # w-operator connection
    children.append(text(cx - size * 0.8, cy + size * 0.92,
                         "w² = i/2  \u2192  two folds = pure rotation at half magnitude "
                         "\u2192  the M\u00f6bius body IS the double fold of the seed",
                         font_size="8", fill="#777"))

    return group(children)


def render_inverse_double_fold(width: int = 2400, height: int = 1400) -> str:
    """Full inverse double fold visualization.

    Two panels:
      Left:  3D^(3D⁻¹) and (3D⁻¹)^3D — the 9-point W9 seed interaction
      Right: Double fold cascade showing 3D→6D→12D→108D self-squaring
    """
    canvas = SVGCanvas(width, height, background="#fafafa")

    # Arrow marker
    canvas.add_def(
        '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>'
        '</marker>'
    )

    # Title
    canvas.add(text(width // 2 - 300, 40,
                    "INVERSE DOUBLE FOLD \u2014 3D^(3D\u207b\u00b9) \u2227 (3D\u207b\u00b9)^3D",
                    font_size="22", fill="#2c3e50", font_weight="bold"))
    canvas.add(text(width // 2 - 270, 65,
                    "The form raised to its own inverse: "
                    "flipped AND reversed = self-referential fixed point",
                    font_size="11", fill="#777"))

    # Left panel: the 9-point interaction
    panel_w = width / 2
    panel_h = height - 120
    panel_r = min(panel_w, panel_h) * 0.4

    canvas.add(text(panel_w * 0.5 - 100, 95,
                    "3D \u00d7 3D\u207b\u00b9 Interaction Matrix = W9 Seed",
                    font_size="13", fill="#333", font_weight="bold"))
    canvas.add(_render_inverse_double_fold(panel_w * 0.5,
                                            120 + panel_h * 0.5,
                                            panel_r))

    # Right panel: the cascade
    canvas.add(text(panel_w * 1.5 - 120, 95,
                    "Double Fold Cascade: D² at Every Level",
                    font_size="13", fill="#333", font_weight="bold"))
    canvas.add(_render_double_fold_cascade(panel_w * 1.5,
                                            120 + panel_h * 0.5,
                                            panel_r))

    # Footer equations
    fy = height - 20
    canvas.add(text(50, fy,
                    "3² = 9 (enneagram) | 6² = 36 (shells) | "
                    "12² = 144 (gates) | 36² = 1296 (\u03a360×21.6) | "
                    "108 = 36×3 = 6²×3 = organism closure",
                    font_size="9", fill="#999"))

    return canvas.render()


def save_inverse_double_fold(out_path: Optional[str] = None) -> str:
    """Generate and save the inverse double fold SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "inverse_double_fold_3d.svg")

    svg = render_inverse_double_fold()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path


def _render_inversion_arrow(x1: float, y1: float, x2: float, y2: float,
                            label: str, color: str, inv_name: str) -> str:
    """Draw an arrow between dimensional bodies showing the inversion type."""
    children = []

    # Curved arrow
    mx = (x1 + x2) / 2 + (y1 - y2) * 0.15
    my = (y1 + y2) / 2 + (x2 - x1) * 0.15
    d = f"M {_fmt(x1)},{_fmt(y1)} Q {_fmt(mx)},{_fmt(my)} {_fmt(x2)},{_fmt(y2)}"
    children.append(
        f'<path d="{d}" stroke="{color}" stroke-width="1.5" '
        f'fill="none" marker-end="url(#arrow)"/>'
    )

    # Inversion label on the curve
    children.append(text(mx - 20, my - 5, label,
                         font_size="9", fill=color, font_weight="bold"))
    children.append(text(mx - 25, my + 8, inv_name,
                         font_size="7", fill="#777"))

    return group(children)


def _render_mobius_inversion(cx: float, cy: float, size: float) -> str:
    """4D→6D: The Möbius half-twist that creates chirality.

    The tesseract wrapped through a half-twist produces a non-orientable
    surface. Walking the surface, you arrive back at your starting point
    but INVERTED. This is how spin± emerges from a single form.

    Visually: a Möbius strip with the 3 wreath bands visible,
    plus the 4D tesseract shadow at the core.
    """
    children = []
    R = size * 0.65
    w = size * 0.15
    n_steps = 80

    # The Möbius band — single surface, half-twisted
    for strip_frac in [-1, -0.33, 0.33, 1]:
        pts_path = []
        for i in range(n_steps + 1):
            u = (i / n_steps) * TAU
            half_twist = u / 2
            r_local = R + w * strip_frac * math.cos(half_twist)
            x = r_local * math.cos(u)
            y = r_local * math.sin(u)
            z = w * strip_frac * math.sin(half_twist)
            px, py = _project_3d(x, y, z, cx, cy, 1.0, 0.35, 0.5)
            pts_path.append(f"{_fmt(px)},{_fmt(py)}")

        # Color gradient: transitions Su→Me→Sa→Su as you traverse
        children.append(
            f'<polyline points="{" ".join(pts_path)}" '
            f'stroke="#f39c12" stroke-width="1.2" fill="none" '
            f'stroke-opacity="0.6"/>'
        )

    # Mark the inversion point (where the twist happens)
    twist_x = cx + R * 0.7
    twist_y = cy
    children.append(circle(twist_x, twist_y, 5,
                           fill="#f1c40f", stroke="#c0392b",
                           stroke_width="2"))
    children.append(text(twist_x + 8, twist_y + 4, "twist(π)",
                         font_size="8", fill="#c0392b"))

    # 3 wreath colors at 120° intervals
    for wi, (name, color) in enumerate(WREATH_COLORS.items()):
        angle = wi * TAU / 3 - TAU / 4
        wx = cx + R * 0.4 * math.cos(angle)
        wy = cy + R * 0.4 * math.sin(angle)
        children.append(circle(wx, wy, 6, fill=color, stroke="#333",
                               stroke_width="0.8"))
        children.append(text(wx - 6, wy + 15, name,
                             font_size="8", fill=color, font_weight="bold"))

    # Chirality arrows: + at top, - at bottom
    children.append(text(cx - 4, cy - R - 5, "χ+",
                         font_size="10", fill="#27ae60", font_weight="bold"))
    children.append(text(cx - 4, cy + R + 12, "χ-",
                         font_size="10", fill="#c0392b", font_weight="bold"))

    return group(children)


def _render_wuxing_inversion(cx: float, cy: float, size: float) -> str:
    """6D→8D: Wu Xing generative + destructive cycle fusion.

    Generative (outer pentagon): Wood→Fire→Earth→Metal→Water→Wood
    Destructive (inner pentagram): Wood→Earth→Water→Fire→Metal→Wood
    Their UNION is the pentadic body — 5 animals × 6 sectors = 30.
    """
    children = []
    animals = [
        ("Tiger", "#e67e22"), ("Crane", "#95a5a6"), ("Leopard", "#f1c40f"),
        ("Snake", "#2ecc71"), ("Dragon", "#e74c3c"),
    ]
    wuxing = ["Wood", "Fire", "Earth", "Metal", "Water"]
    R = size * 0.7

    # Outer pentagon: generative cycle (solid)
    gen_pts = []
    for i in range(5):
        angle = i * TAU / 5 - TAU / 4
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)
        gen_pts.append((px, py))

    for i in range(5):
        x1, y1 = gen_pts[i]
        x2, y2 = gen_pts[(i + 1) % 5]
        children.append(line(x1, y1, x2, y2,
                             stroke="#27ae60", stroke_width="2"))

    # Inner pentagram: destructive cycle (dashed — the inversion)
    for i in range(5):
        x1, y1 = gen_pts[i]
        x2, y2 = gen_pts[(i + 2) % 5]  # skip one = pentagram
        children.append(line(x1, y1, x2, y2,
                             stroke="#c0392b", stroke_width="1.5",
                             stroke_dasharray="4,2"))

    # Animal/element nodes
    for i, ((animal, color), elem) in enumerate(zip(animals, wuxing)):
        px, py = gen_pts[i]
        children.append(circle(px, py, 8, fill=color, stroke="#333",
                               stroke_width="1"))
        children.append(text(px - 12, py + 20, animal,
                             font_size="8", fill=color, font_weight="bold"))
        children.append(text(px - 10, py + 30, f"({elem})",
                             font_size="7", fill="#777"))

    # Labels
    children.append(text(cx - 25, cy - 5, "gen\u2192",
                         font_size="8", fill="#27ae60"))
    children.append(text(cx + 5, cy + 5, "\u2190dest",
                         font_size="8", fill="#c0392b"))

    return group(children)


def _render_planetary_inversion(cx: float, cy: float, size: float) -> str:
    """8D→10D: Planetary exaltation/detriment opposition.

    Each planet has an exaltation (peak power) and detriment (inverted).
    The 7 exalt-detriment pairs woven through 30 pentadic sectors = 210.
    """
    children = []
    planets = [
        ("Moon", "#c0c0c0"), ("Mercury", "#a0a0a0"), ("Venus", "#d4a574"),
        ("Sun", "#ffd700"), ("Mars", "#ff4500"), ("Jupiter", "#4169e1"),
        ("Saturn", "#696969"),
    ]
    R = size * 0.7

    # Outer heptagram: connect every 3rd vertex
    for i in range(7):
        a1 = i * TAU / 7 - TAU / 4
        a2 = ((i + 3) % 7) * TAU / 7 - TAU / 4
        x1 = cx + R * 0.9 * math.cos(a1)
        y1 = cy + R * 0.9 * math.sin(a1)
        x2 = cx + R * 0.9 * math.cos(a2)
        y2 = cy + R * 0.9 * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke="#DAA520", stroke_width="0.8",
                             stroke_opacity="0.4"))

    # Planet nodes at heptagonal vertices
    for i, (planet, color) in enumerate(planets):
        angle = i * TAU / 7 - TAU / 4
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)

        # Exaltation node (solid)
        children.append(circle(px, py, 7, fill=color, stroke="#333",
                               stroke_width="1"))
        children.append(text(px - 10, py + 18, planet,
                             font_size="7", fill=color))

        # Detriment node (hollow — the inversion, opposite side)
        inv_angle = angle + math.pi
        ix = cx + R * 0.5 * math.cos(inv_angle)
        iy = cy + R * 0.5 * math.sin(inv_angle)
        children.append(circle(ix, iy, 4, fill="none", stroke=color,
                               stroke_width="1.5", stroke_dasharray="2,1"))

        # Opposition line
        children.append(line(px, py, ix, iy,
                             stroke=color, stroke_width="0.5",
                             stroke_dasharray="2,3", stroke_opacity="0.4"))

    return group(children)


def _render_matrix_inversion(cx: float, cy: float, size: float) -> str:
    """10D→12D: 3×3 matrix and its transpose.

    The 3×3 Su/Me/Sa self-application matrix and its transpose
    together form the complete 9-station crown.
    M + Mᵀ = the full enneagram = 12D closure.
    """
    children = []
    grid_size = size * 0.35
    labels_3x3 = [
        ["Su·Su", "Su·Me", "Su·Sa"],
        ["Me·Su", "Me·Me", "Me·Sa"],
        ["Sa·Su", "Sa·Me", "Sa·Sa"],
    ]
    colors_3x3 = [
        [WREATH_COLORS["Su"], "#e98b6d", "#c0392b"],
        ["#f39c12", "#f1c40f", "#d4ac0d"],
        ["#8e44ad", "#9b59b6", "#6c3483"],
    ]

    # Left: original matrix M
    mx_left = cx - size * 0.35
    for row in range(3):
        for col in range(3):
            bx = mx_left - grid_size + col * grid_size * 0.7
            by = cy - grid_size + row * grid_size * 0.7
            children.append(rect(bx, by, grid_size * 0.65, grid_size * 0.65,
                                 fill=colors_3x3[row][col],
                                 fill_opacity="0.6",
                                 stroke="#333", stroke_width="0.5"))
            children.append(text(bx + 3, by + grid_size * 0.4,
                                 labels_3x3[row][col],
                                 font_size="6", fill="#333"))

    # Right: transpose Mᵀ (rows↔cols)
    mx_right = cx + size * 0.15
    for row in range(3):
        for col in range(3):
            bx = mx_right + col * grid_size * 0.7
            by = cy - grid_size + row * grid_size * 0.7
            # Transpose: swap row/col for color and label
            children.append(rect(bx, by, grid_size * 0.65, grid_size * 0.65,
                                 fill=colors_3x3[col][row],  # transposed
                                 fill_opacity="0.4",
                                 stroke="#333", stroke_width="0.5",
                                 stroke_dasharray="2,1"))
            children.append(text(bx + 3, by + grid_size * 0.4,
                                 labels_3x3[col][row],  # transposed
                                 font_size="6", fill="#555"))

    # Union arrow
    children.append(text(cx - 8, cy + 3, "\u222a",
                         font_size="16", fill="#9b59b6", font_weight="bold"))

    # Labels
    children.append(text(mx_left - grid_size, cy - grid_size - 10, "M",
                         font_size="12", fill="#333", font_weight="bold"))
    children.append(text(mx_right + grid_size * 1.5, cy - grid_size - 10,
                         "M\u1d40",
                         font_size="12", fill="#555", font_weight="bold"))

    # Z* at intersection (center cell = Me·Me)
    children.append(circle(cx, cy + grid_size * 0.8, 5,
                           fill="#6c3483", stroke="#fff", stroke_width="1.5"))
    children.append(text(cx - 5, cy + grid_size * 0.8 + 3, "Z*",
                         font_size="8", fill="#fff", font_weight="bold"))

    return group(children)


def _render_triple_crown_expansion(cx: float, cy: float, size: float) -> str:
    """12D→36D→108D: Triple crown expansion.

    12D × 3 meta-wreaths = 36D (each wreath sees the full 12D differently)
    36D × 3 octaves = 108D (surface/mid/deep where deep inverts surface)

    Rendered as concentric trefoils: inner=12D, middle=36D, outer=108D.
    """
    children = []

    # 108D outer ring
    children.append(circle(cx, cy, size,
                           stroke="#2c3e50", stroke_width="3",
                           fill="#2c3e50", fill_opacity="0.02"))

    # 3 octave sectors (108D = 36D × 3)
    octaves = [("Surface", "#3498db", 0), ("Mid", "#9b59b6", 1), ("Deep", "#2c3e50", 2)]
    for name, color, oi in octaves:
        a_start = oi * TAU / 3 - TAU / 6
        a_end = (oi + 1) * TAU / 3 - TAU / 6

        # Sector arc
        pts = [(cx, cy)]
        for i in range(13):
            t = i / 12
            angle = a_start + t * (a_end - a_start)
            pts.append((cx + size * math.cos(angle),
                        cy + size * math.sin(angle)))
        pts.append((cx, cy))
        children.append(polygon(pts, fill=color, fill_opacity="0.04",
                                stroke=color, stroke_width="0.5"))

        # Label
        la = (a_start + a_end) / 2
        lx = cx + size * 0.85 * math.cos(la)
        ly = cy + size * 0.85 * math.sin(la)
        children.append(text(lx - 15, ly + 4, name,
                             font_size="9", fill=color, font_weight="bold"))

    # 36D middle ring
    r36 = size * PHI_INV
    children.append(circle(cx, cy, r36,
                           stroke="#8e44ad", stroke_width="2",
                           fill="#8e44ad", fill_opacity="0.03"))

    # 3 meta-wreath trefoil (36D = 12D × 3)
    for wi, (name, color) in enumerate(WREATH_COLORS.items()):
        phase = wi * TAU / 3
        offset = r36 * 0.25
        wcx = cx + offset * math.cos(phase)
        wcy = cy + offset * math.sin(phase)
        children.append(circle(wcx, wcy, r36 * 0.6,
                               stroke=color, stroke_width="1.5",
                               fill=color, fill_opacity="0.05"))

        # 12 archetype dots per wreath
        for ai in range(12):
            a = ai * TAU / 12
            ax = wcx + r36 * 0.45 * math.cos(a)
            ay = wcy + r36 * 0.45 * math.sin(a)
            children.append(circle(ax, ay, 2,
                                   fill=color, stroke="none",
                                   fill_opacity="0.5"))

        # Wreath label
        lx = cx + (r36 * 0.3 + offset) * math.cos(phase + 0.3)
        ly = cy + (r36 * 0.3 + offset) * math.sin(phase + 0.3)
        children.append(text(lx - 6, ly + 4, name,
                             font_size="9", fill=color, font_weight="bold"))

    # 12D core crown (9 stations)
    r12 = size * PHI_INV ** 2
    children.append(circle(cx, cy, r12,
                           stroke="#9b59b6", stroke_width="1.5",
                           fill="#9b59b6", fill_opacity="0.05"))

    w9_colors = list([
        "#e74c3c", "#e98b6d", "#c0392b",
        "#f39c12", "#f1c40f", "#d4ac0d",
        "#8e44ad", "#9b59b6", "#6c3483",
    ])
    for i in range(9):
        angle = i * TAU / 9 - TAU / 4
        sx = cx + r12 * 0.8 * math.cos(angle)
        sy = cy + r12 * 0.8 * math.sin(angle)
        children.append(circle(sx, sy, 4,
                               fill=w9_colors[i], stroke="#333",
                               stroke_width="0.5"))
        # Enneagram (connect every 4th)
        a2 = ((i + 4) % 9) * TAU / 9 - TAU / 4
        ex = cx + r12 * 0.8 * math.cos(a2)
        ey = cy + r12 * 0.8 * math.sin(a2)
        children.append(line(sx, sy, ex, ey,
                             stroke="#9b59b6", stroke_width="0.4",
                             stroke_opacity="0.3"))

    # Z* at absolute center
    children.append(circle(cx, cy, 5,
                           fill="#2c3e50", stroke="#fff", stroke_width="1.5"))
    children.append(text(cx - 5, cy + 3, "Z*",
                         font_size="8", fill="#fff", font_weight="bold"))

    # Dimension labels
    children.append(text(cx + r12 + 5, cy - 3, "12D",
                         font_size="8", fill="#9b59b6"))
    children.append(text(cx + r36 + 5, cy - 3, "36D",
                         font_size="8", fill="#8e44ad"))
    children.append(text(cx + size + 5, cy - 3, "108D",
                         font_size="8", fill="#2c3e50"))

    return group(children)


def _render_w_cascade(cx: float, cy: float, size: float) -> str:
    """The w-operator emergence spiral with dimensional markers.

    w = (1+i)/2 traces the inversion cascade:
    Each application = compress by 1/√2 + rotate 45°.
    The spiral passes through all dimension births.
    """
    children = []
    w = W_OP

    # Background: faint coordinate axes
    children.append(line(cx - size, cy, cx + size, cy,
                         stroke="#eee", stroke_width="0.5"))
    children.append(line(cx, cy - size, cx, cy + size,
                         stroke="#eee", stroke_width="0.5"))

    # w^n spiral
    pts = []
    for n in range(50):
        z = w ** n
        px = cx + z.real * size * 1.3
        py = cy - z.imag * size * 1.3
        pts.append((px, py, n, abs(z)))

    # Draw the spiral path
    if len(pts) > 1:
        path_d = [f"M {_fmt(pts[0][0])},{_fmt(pts[0][1])}"]
        for p in pts[1:]:
            path_d.append(f"L {_fmt(p[0])},{_fmt(p[1])}")
        children.append(path(" ".join(path_d),
                             stroke="#9b59b6", stroke_width="1.5",
                             fill="none", stroke_opacity="0.7"))

    # Dimensional birth markers
    dim_at_step = [
        (0, "3D", DIM_COLORS[3]),
        (1, "4D", DIM_COLORS[4]),
        (2, "6D", DIM_COLORS[6]),
        (4, "8D", DIM_COLORS[8]),
        (6, "10D", DIM_COLORS[10]),
        (9, "12D", DIM_COLORS[12]),
        (14, "36D", DIM_COLORS[36]),
        (21, "108D", DIM_COLORS[108]),
    ]

    for step, label, color in dim_at_step:
        if step < len(pts):
            px, py, _, mag = pts[step]
            r = 5 + mag * 3
            children.append(circle(px, py, r,
                                   fill=color, stroke="#333",
                                   stroke_width="1"))
            children.append(text(px + r + 3, py - 3, label,
                                 font_size="10", fill=color,
                                 font_weight="bold"))

            # Inversion annotation
            if step > 0 and step < len(pts) - 1:
                prev_x, prev_y = pts[step - 1][0], pts[step - 1][1]
                mid_x = (prev_x + px) / 2
                mid_y = (prev_y + py) / 2
                children.append(text(mid_x - 5, mid_y + 3, "\u207b\u00b9",
                                     font_size="8", fill="#999"))

    # Z* attractor at center
    children.append(circle(cx, cy, 3,
                           fill="#333", stroke="#fff", stroke_width="1"))

    # Equations
    children.append(text(cx - size + 5, cy + size - 10,
                         "w = (1+i)/2   |w| = 1/\u221a2   arg = \u03c0/4",
                         font_size="8", fill="#777"))
    children.append(text(cx - size + 5, cy + size,
                         "D\u2099\u208a\u2081 = D\u2099 \u222a D\u2099\u207b\u00b9",
                         font_size="9", fill="#9b59b6", font_weight="bold"))

    return group(children)


def _render_containment_count(cx: float, cy: float, size: float) -> str:
    """Containment counting: how many lower bodies each dimension holds.

    Shows the multiplicative cascade:
    108D = 3 × 36D = 9 × 12D = 81 × 10D = 567 × 8D = 2835 × 6D
    12D = 9 × 10D = 63 × 8D = 315 × 6D = 945 × 4D = 1890 × 3D
    """
    children = []

    levels = [
        ("108D", 1, DIM_COLORS[108]),
        ("36D", 3, DIM_COLORS[36]),
        ("12D", 9, DIM_COLORS[12]),
        ("10D", 81, DIM_COLORS[10]),
        ("8D", 567, DIM_COLORS[8]),
        ("6D", 2835, DIM_COLORS[6]),
        ("4D", 8505, DIM_COLORS[4]),
        ("3D", 17010, DIM_COLORS[3]),
    ]

    bar_w = size * 1.5
    row_h = size * 2 / len(levels)

    for i, (dim, count, color) in enumerate(levels):
        y = cy - size + i * row_h

        # Label
        children.append(text(cx - size * 0.85, y + row_h * 0.6, dim,
                             font_size="11", fill=color, font_weight="bold"))

        # Count
        children.append(text(cx - size * 0.55, y + row_h * 0.6,
                             f"\u00d7{count:,}",
                             font_size="9", fill="#555"))

        # Bar (log scale)
        if count > 0:
            log_w = math.log(count + 1) / math.log(17011) * bar_w
            children.append(rect(cx - size * 0.3, y + 4, log_w, row_h * 0.6,
                                 fill=color, fill_opacity="0.5",
                                 stroke=color, stroke_width="0.5"))

    # Formula
    children.append(text(cx - size * 0.85, cy + size + 10,
                         "B\u2099\u208a\u2082 = W\u2099(B\u2099)",
                         font_size="10", fill="#555", font_weight="bold"))

    return group(children)


def render_inversion_cascade(width: int = 2400, height: int = 2000) -> str:
    """FULL 108D INVERSION CASCADE — The Generative Principle.

    Shows how each dimension is born from the previous one fused with
    its own inversion. This is THE mathematical explanation of 108D:
    not 108 separate dimensions, but 7 nested inversions.

    Layout:
      Row 1: [3D + 3D⁻¹ hexagram] → [4D→6D Möbius twist] → [6D→8D Wu Xing]
      Row 2: [8D→10D Planetary]    → [10D→12D Matrix]     → [12D→36D→108D Crown]
      Row 3: [w-operator cascade]  → [Containment counting]
    """
    canvas = SVGCanvas(width, height, background="#fafafa")

    # Arrow marker definition
    canvas.add_def(
        '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>'
        '</marker>'
    )

    # ── Title ──
    canvas.add(text(width // 2 - 250, 40,
                    "108D INVERSION CASCADE \u2014 The Generative Principle",
                    font_size="24", fill="#2c3e50", font_weight="bold"))
    canvas.add(text(width // 2 - 230, 65,
                    "Every dimension is the previous fused with its own mirror: "
                    "D\u2099\u208a\u2081 = D\u2099 \u222a D\u2099\u207b\u00b9",
                    font_size="12", fill="#777"))

    # ── Grid layout ──
    col_w = width / 3
    row_h = (height - 100) / 3
    cell_r = min(col_w, row_h) * 0.38

    panels = [
        # Row 1
        (0, 0, _render_3d_pair, "3D \u222a 3D\u207b\u00b9 = Hexagram Seed"),
        (1, 0, _render_mobius_inversion, "4D\u21926D: M\u00f6bius Half-Twist"),
        (2, 0, _render_wuxing_inversion, "6D\u21928D: Wu Xing Fusion"),
        # Row 2
        (0, 1, _render_planetary_inversion, "8D\u219210D: Planetary Opposition"),
        (1, 1, _render_matrix_inversion, "10D\u219212D: Matrix Transpose"),
        (2, 1, _render_triple_crown_expansion, "12D\u219236D\u2192108D: Crown"),
        # Row 3
        (0, 2, _render_w_cascade, "w-operator Emergence Spiral"),
        (1, 2, _render_containment_count, "Containment Counting"),
    ]

    for col, row, fn, label in panels:
        pcx = col_w * (col + 0.5)
        pcy = 100 + row_h * (row + 0.5)

        # Panel label
        canvas.add(text(pcx - len(label) * 3.5, pcy - cell_r - 10, label,
                        font_size="11", fill="#333", font_weight="bold"))
        try:
            canvas.add(fn(pcx, pcy, cell_r))
        except Exception as e:
            canvas.add(text(pcx - 40, pcy, f"[ERROR: {e}]",
                            font_size="10", fill="red"))

    # ── Row 3 right: dimensional ladder summary ──
    sum_cx = col_w * 2.5
    sum_cy = 100 + row_h * 2.5
    ladder_text = [
        ("3D seed", "\u2192 3D\u207b\u00b9 point mirror", DIM_COLORS[3]),
        ("4D tess", "\u2192 4D\u207b\u00b9 M\u00f6bius twist", DIM_COLORS[4]),
        ("6D body", "\u2192 6D\u207b\u00b9 Wu Xing destruct", DIM_COLORS[6]),
        ("8D pent", "\u2192 8D\u207b\u00b9 planet detriment", DIM_COLORS[8]),
        ("10D hept", "\u2192 10D\u207b\u00b9 matrix transpose", DIM_COLORS[10]),
        ("12D crown", "\u2192 \u00d73 meta-wreath = 36D", DIM_COLORS[12]),
        ("36D sigma", "\u2192 \u00d73 octave = 108D", DIM_COLORS[36]),
        ("108D Xi", "= organism closure (Z*)", DIM_COLORS[108]),
    ]

    for i, (dim_name, inv_desc, color) in enumerate(ladder_text):
        y = sum_cy - cell_r + i * 28
        canvas.add(circle(sum_cx - cell_r + 10, y, 5,
                          fill=color, stroke="#333", stroke_width="0.5"))
        canvas.add(text(sum_cx - cell_r + 20, y + 4, dim_name,
                        font_size="11", fill=color, font_weight="bold"))
        canvas.add(text(sum_cx - cell_r + 75, y + 4, inv_desc,
                        font_size="9", fill="#777"))

        # Connecting line to next
        if i < len(ladder_text) - 1:
            canvas.add(line(sum_cx - cell_r + 10, y + 8,
                            sum_cx - cell_r + 10, y + 20,
                            stroke="#ccc", stroke_width="1"))

    # ── Footer: key equations ──
    fy = height - 25
    equations = [
        "w = (1+i)/2",
        "|w| = 1/\u221a2 (inversion compression)",
        "B\u2081\u2082 = 1890\u00d7B\u2083",
        "B\u2081\u2080\u2088 = 3\u00d73\u00d79\u00d77\u00d75\u00d73\u00d72 = 17,010 seeds",
        "\u03a3\u2086\u2080 \u00d7 4 SFCR \u00d7 E8 = 103,680 roots",
    ]
    for fi, eq in enumerate(equations):
        canvas.add(text(50 + fi * (width - 100) // len(equations), fy,
                        eq, font_size="9", fill="#999"))

    return canvas.render()


def save_inversion_cascade(out_path: Optional[str] = None) -> str:
    """Generate and save the full inversion cascade SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "inversion_cascade_108d.svg")

    svg = render_inversion_cascade()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path


# ══════════════════════════════════════════════════════════════════════════
#  NUMERICAL INVERSION — ACTUAL VALUES × 1/x FOR ALL 12 CRYSTAL CALCS
# ══════════════════════════════════════════════════════════════════════════
# This is NOT conceptual. Every number below is COMPUTED from
# geometric_constants.py and cross_lens.py, then its exact 1/x inverse
# is calculated and displayed.

import cmath

# Import cross-lens constants for actual computation
try:
    from .cross_lens import (
        W as W_OP_COMPLEX, W_ABS, W_ARG, LN_PHI,
        T_S_to_F, T_F_to_S, T_F_to_C, T_C_to_F,
        T_S_to_C, T_C_to_S, WSpiral,
    )
except ImportError:
    W_OP_COMPLEX = complex(0.5, 0.5)
    W_ABS = abs(W_OP_COMPLEX)
    W_ARG = cmath.phase(W_OP_COMPLEX)
    LN_PHI = math.log(PHI)


def _compute_all_inversions() -> Dict[str, List[Tuple[str, float, float]]]:
    """Compute EVERY crystal numerical value and its 1/x inverse.

    Returns dict of category -> list of (name, original, inverse).
    All values are the ACTUAL numbers from geometric_constants.py.
    """
    inv = {}

    # ── 1. PHI CASCADE ──
    phi_vals = [
        ("φ",            PHI),
        ("φ⁻¹",          PHI_INV),
        ("φ⁻²",          PHI_INV ** 2),
        ("φ⁻³",          PHI_INV ** 3),
        ("√φ⁻¹",         math.sqrt(PHI_INV)),
        ("√3",           SQRT3),
        ("√5",           SQRT5),
    ]
    inv["PHI_CASCADE"] = [(n, v, 1.0 / v) for n, v in phi_vals]

    # ── 2. BRIDGE WEIGHTS ──
    bridge_vals = []
    for key in ["SF", "FC", "CR", "SC", "FR", "SR"]:
        w = BRIDGE_WEIGHTS[key]
        bridge_vals.append((f"B({key})", w, 1.0 / w))
    inv["BRIDGE_WEIGHTS"] = bridge_vals

    # ── 3. w-OPERATOR ──
    w = W_OP_COMPLEX
    w_inv = 1.0 / w  # = (1-i)
    w_sq = w * w
    w_sq_inv = 1.0 / w_sq
    inv["W_OPERATOR"] = [
        ("|w|",      abs(w),      1.0 / abs(w)),
        ("|w⁻¹|",    abs(w_inv),  1.0 / abs(w_inv)),
        ("Re(w)",    w.real,      1.0 / w.real),
        ("Im(w)",    w.imag,      1.0 / w.imag),
        ("Re(w⁻¹)",  w_inv.real,  1.0 / w_inv.real if w_inv.real != 0 else float('inf')),
        ("Im(w⁻¹)",  abs(w_inv.imag), 1.0 / abs(w_inv.imag)),
        ("|w²|",     abs(w_sq),   1.0 / abs(w_sq)),
        ("|w⁻²|",    abs(w_sq_inv), 1.0 / abs(w_sq_inv)),
        ("arg(w)/π",  W_ARG / math.pi, math.pi / W_ARG),
    ]

    # ── 4. ATTRACTOR VALUES ──
    attr_vals = []
    for key, val in ATTRACTOR.items():
        attr_vals.append((key, val, 1.0 / val))
    inv["ATTRACTOR"] = attr_vals

    # ── 5. FLOWER RINGS (decay → growth) ──
    flower_vals = []
    for i, ring in enumerate(FLOWER_RINGS):
        flower_vals.append((f"ring_{i}", ring, 1.0 / ring))
    inv["FLOWER_RINGS"] = flower_vals

    # ── 6. E8 AMPLIFICATION ──
    e8_vals = [("E8_amp", E8_AMPLIFICATION, 1.0 / E8_AMPLIFICATION)]
    # Actual computed face boosts for face S
    for face in FACES:
        boosts = E8_FACE_BOOSTS[face]
        for target_face, boost_val in boosts.items():
            e8_vals.append((
                f"E8[{face}→{target_face}]",
                boost_val,
                1.0 / boost_val,
            ))
    inv["E8_BOOSTS"] = e8_vals

    # ── 7. ELEMENT LENS WEIGHTS ──
    lens_vals = []
    for lens in ["S", "F", "C", "R"]:
        weights = ELEMENT_LENS_WEIGHTS[lens]
        for dim_name, w_val in weights.items():
            short = dim_name.split("_")[0]  # x1, x2, etc.
            lens_vals.append((f"{lens}.{short}", w_val, 1.0 / w_val))
    inv["LENS_WEIGHTS"] = lens_vals

    # ── 8. CROSS-LENS TRANSITIONS (evaluated at φ) ──
    try:
        test_x = PHI
        cross_vals = [
            ("T(S→F)(φ)",  T_S_to_F(test_x),  T_F_to_S(T_S_to_F(test_x))),
            ("T(F→C)(φ)",  T_F_to_C(T_S_to_F(test_x)),
                           T_C_to_F(T_F_to_C(T_S_to_F(test_x)))),
            ("T(S→C)(φ)",  T_S_to_C(test_x),  T_C_to_S(T_S_to_C(test_x))),
            ("T(S→F)(e)",  T_S_to_F(math.e),  1.0 / T_S_to_F(math.e)),
            ("T(S→C)(e)",  T_S_to_C(math.e),  1.0 / T_S_to_C(math.e)),
            ("ln(φ)",      LN_PHI,            1.0 / LN_PHI),
            ("π/(2·ln(φ))", math.pi / (2 * LN_PHI), (2 * LN_PHI) / math.pi),
            ("2·ln(φ)/π",  (2 * LN_PHI) / math.pi, math.pi / (2 * LN_PHI)),
        ]
        inv["CROSS_LENS"] = [(n, v, iv) for n, v, iv in cross_vals]
    except Exception:
        inv["CROSS_LENS"] = []

    # ── 9. WEAVE PERIODS ──
    from .dimensional_projector import W3, W5, W7, W9, MASTER_CLOCK_Z420
    weave_vals = [
        ("W3.period",  W3.period,  1.0 / W3.period),
        ("W5.period",  W5.period,  1.0 / W5.period),
        ("W7.period",  W7.period,  1.0 / W7.period),
        ("W9.period",  W9.period,  1.0 / W9.period),
        ("W3.closure", W3.local_closure, 1.0 / W3.local_closure),
        ("W5.closure", W5.local_closure, 1.0 / W5.local_closure),
        ("W7.closure", W7.local_closure, 1.0 / W7.local_closure),
        ("W9.closure", W9.local_closure, 1.0 / W9.local_closure),
        ("Z420",       MASTER_CLOCK_Z420, 1.0 / MASTER_CLOCK_Z420),
    ]
    inv["WEAVE_PERIODS"] = weave_vals

    # ── 10. CONTAINMENT COUNTS ──
    containment = [
        ("B₃ in B₁₂", 1890,  1.0 / 1890),
        ("B₄ in B₁₂", 945,   1.0 / 945),
        ("B₆ in B₁₂", 315,   1.0 / 315),
        ("B₈ in B₁₂", 63,    1.0 / 63),
        ("B₁₀ in B₁₂", 9,    1.0 / 9),
        ("B₁₂",        1,     1.0),
        ("108D seeds", 17010, 1.0 / 17010),
    ]
    inv["CONTAINMENT"] = containment

    # ── 11. w-SPIRAL TRAJECTORY (actual computed w^n values) ──
    spiral_vals = []
    for n in range(9):
        wn = W_OP_COMPLEX ** n
        mod = abs(wn)
        if mod > 1e-15:
            spiral_vals.append((f"|w^{n}|", mod, 1.0 / mod))
    inv["W_SPIRAL"] = spiral_vals

    # ── 12. VESICA + TRANSFORM PHI WEIGHTS ──
    from .geometric_constants import VESICA_RATIO, VESICA_PAIRS, TRANSFORM_PHI_WEIGHTS
    vesica_vals = [("√3 (vesica)", VESICA_RATIO, 1.0 / VESICA_RATIO)]
    for key, pair in VESICA_PAIRS.items():
        vesica_vals.append((f"V({key})", pair["boost"], 1.0 / pair["boost"]))
    for n, w_val in TRANSFORM_PHI_WEIGHTS.items():
        vesica_vals.append((f"φ^({n}/3)", w_val, 1.0 / w_val))
    inv["VESICA_TRANSFORM"] = vesica_vals

    return inv


def _render_num_table(cx: float, cy: float, w: float, h: float,
                      title: str, rows: List[Tuple[str, float, float]],
                      color: str, max_rows: int = 12) -> str:
    """Render a single numerical inversion table panel.

    Each row shows: name | original value | → | 1/x inverse value
    """
    children = []

    # Panel background
    children.append(rect(cx - w / 2, cy - h / 2, w, h, rx=6,
                         fill="#fefefe", stroke=color, stroke_width="1.5",
                         fill_opacity="0.95"))

    # Title bar
    children.append(rect(cx - w / 2, cy - h / 2, w, 22, rx=6,
                         fill=color, fill_opacity="0.15"))
    children.append(text(cx - w / 2 + 8, cy - h / 2 + 15, title,
                         font_size="10", fill=color, font_weight="bold",
                         font_family="monospace"))

    # Column headers
    header_y = cy - h / 2 + 38
    col_name = cx - w / 2 + 8
    col_orig = cx - w / 2 + w * 0.35
    col_arrow = cx - w / 2 + w * 0.58
    col_inv = cx - w / 2 + w * 0.63

    children.append(text(col_name, header_y, "name",
                         font_size="7", fill="#999", font_family="monospace"))
    children.append(text(col_orig, header_y, "value",
                         font_size="7", fill="#999", font_family="monospace"))
    children.append(text(col_inv, header_y, "1/value",
                         font_size="7", fill="#999", font_family="monospace"))

    # Separator
    children.append(line(cx - w / 2 + 4, header_y + 4,
                         cx + w / 2 - 4, header_y + 4,
                         stroke="#ddd", stroke_width="0.5"))

    # Data rows
    display_rows = rows[:max_rows]
    row_h = min(14, (h - 60) / max(len(display_rows), 1))

    for i, (name, orig, inverse) in enumerate(display_rows):
        ry = header_y + 14 + i * row_h

        # Alternate row background
        if i % 2 == 0:
            children.append(rect(cx - w / 2 + 2, ry - 9, w - 4, row_h,
                                 fill=color, fill_opacity="0.04"))

        # Name
        children.append(text(col_name, ry, name,
                             font_size="8", fill="#444",
                             font_family="monospace"))

        # Original value
        if abs(orig) >= 100:
            orig_str = f"{orig:.1f}"
        elif abs(orig) >= 1:
            orig_str = f"{orig:.4f}"
        else:
            orig_str = f"{orig:.6f}"
        children.append(text(col_orig, ry, orig_str,
                             font_size="8", fill="#2c3e50",
                             font_family="monospace", font_weight="bold"))

        # Arrow
        children.append(text(col_arrow, ry, "→",
                             font_size="8", fill=color))

        # Inverse value
        if abs(inverse) >= 100:
            inv_str = f"{inverse:.4f}"
        elif abs(inverse) >= 10:
            inv_str = f"{inverse:.4f}"
        elif abs(inverse) >= 1:
            inv_str = f"{inverse:.6f}"
        else:
            inv_str = f"{inverse:.6f}"
        children.append(text(col_inv, ry, inv_str,
                             font_size="8", fill="#c0392b",
                             font_family="monospace", font_weight="bold"))

        # Visual bar showing magnitude relationship
        bar_x = cx + w / 2 - 35
        bar_w_orig = min(25, max(2, orig * 15))
        bar_w_inv = min(25, max(2, inverse * 15))
        children.append(rect(bar_x, ry - 5, bar_w_orig, 3,
                             fill="#2c3e50", fill_opacity="0.3"))
        children.append(rect(bar_x, ry - 1, bar_w_inv, 3,
                             fill="#c0392b", fill_opacity="0.3"))

    # Overflow indicator
    if len(rows) > max_rows:
        children.append(text(cx - 15, cy + h / 2 - 8,
                             f"+{len(rows) - max_rows} more",
                             font_size="7", fill="#999"))

    return group(children)


def _render_bridge_graph(cx: float, cy: float, size: float) -> str:
    """Render the SFCR bridge graph with actual weights and their inverses.

    Shows the 4 SFCR nodes connected by weighted edges.
    Original weight on one side, 1/weight on the other.
    """
    children = []
    R = size * 0.6
    faces = ["S", "F", "C", "R"]
    colors = [SFCR_COLORS[f] for f in faces]

    # Position nodes at square vertices
    positions = {}
    for i, face in enumerate(faces):
        angle = math.pi / 4 + i * math.pi / 2
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)
        positions[face] = (px, py)

    # Draw bridges with actual weights
    bridge_pairs = [("S", "F"), ("F", "C"), ("C", "R"),
                    ("S", "C"), ("F", "R"), ("S", "R")]
    for a, b in bridge_pairs:
        key = "".join(sorted([a, b], key=lambda x: "SFCR".index(x)))
        w_val = BRIDGE_WEIGHTS[key]
        w_inv = 1.0 / w_val
        ax, ay = positions[a]
        bx, by = positions[b]

        # Determine bridge type for color
        if key in GOLDEN_BRIDGES:
            bcolor = "#DAA520"
            sw = "2"
        elif w_val == 0.5:
            bcolor = "#666"
            sw = "1.5"
        else:
            bcolor = "#999"
            sw = "1"

        children.append(line(ax, ay, bx, by,
                             stroke=bcolor, stroke_width=sw,
                             stroke_opacity="0.6"))

        # Weight labels
        mx = (ax + bx) / 2
        my = (ay + by) / 2
        # Offset perpendicular to the line
        dx, dy = bx - ax, by - ay
        ln = math.sqrt(dx * dx + dy * dy) or 1
        nx, ny = -dy / ln * 12, dx / ln * 12

        children.append(text(mx + nx - 15, my + ny,
                             f"{w_val:.3f}",
                             font_size="8", fill="#2c3e50",
                             font_family="monospace", font_weight="bold"))
        children.append(text(mx - nx - 15, my - ny,
                             f"→{w_inv:.3f}",
                             font_size="8", fill="#c0392b",
                             font_family="monospace", font_weight="bold"))

    # Draw nodes
    for face in faces:
        px, py = positions[face]
        children.append(circle(px, py, 16, fill=SFCR_COLORS[face],
                               stroke="#333", stroke_width="1.5"))
        children.append(text(px - 4, py + 4, face,
                             font_size="11", fill="#fff", font_weight="bold"))

    return group(children)


def _render_flower_inversion(cx: float, cy: float, size: float) -> str:
    """Render flower rings decay vs growth with actual PHI^n values.

    Left: original decay (PHI_INV^n shrinking)
    Right: inverted growth (PHI^n expanding)
    """
    children = []
    max_r = size * 0.4

    # Title
    children.append(text(cx - 80, cy - size * 0.85,
                         "FLOWER: decay → growth",
                         font_size="10", fill="#9b59b6", font_weight="bold"))

    # Left: original decay
    lcx = cx - size * 0.35
    for i, ring_val in enumerate(FLOWER_RINGS):
        r = max_r * ring_val
        opacity = 0.2 + 0.8 * ring_val
        children.append(circle(lcx, cy, max(r, 2),
                               fill="none", stroke="#9b59b6",
                               stroke_width="1.5",
                               stroke_opacity=f"{opacity:.2f}"))
        children.append(text(lcx + max_r + 5, cy - max_r + i * 14,
                             f"r{i}: {ring_val:.6f}",
                             font_size="7", fill="#2c3e50",
                             font_family="monospace"))

    # Arrow
    children.append(text(cx - 10, cy, "→", font_size="18", fill="#c0392b"))

    # Right: inverted growth
    rcx = cx + size * 0.35
    inv_rings = [1.0 / r for r in FLOWER_RINGS]
    # Normalize for display (largest ring sets the radius)
    max_inv = max(inv_rings)
    for i, inv_val in enumerate(inv_rings):
        r = max_r * inv_val / max_inv
        opacity = 0.2 + 0.8 * (inv_val / max_inv)
        children.append(circle(rcx, cy, max(r, 2),
                               fill="none", stroke="#c0392b",
                               stroke_width="1.5",
                               stroke_opacity=f"{opacity:.2f}"))
        children.append(text(rcx + max_r + 5, cy - max_r + i * 14,
                             f"1/r{i}: {inv_val:.4f}",
                             font_size="7", fill="#c0392b",
                             font_family="monospace"))

    return group(children)


def _render_w_spiral_inversion(cx: float, cy: float, size: float) -> str:
    """Render the w-operator spiral with actual values + inverse spiral.

    w = (1+i)/2: |w|=0.707 (compresses) → |w⁻¹|=1.414 (expands)
    Shows both spirals with actual computed w^n and (w⁻¹)^n values.
    """
    children = []
    w = W_OP_COMPLEX
    w_inv = 1.0 / w
    R = size * 0.4

    # Title
    children.append(text(cx - 100, cy - size * 0.9,
                         f"w = {w} | w⁻¹ = {w_inv}",
                         font_size="9", fill="#2c3e50",
                         font_family="monospace", font_weight="bold"))
    children.append(text(cx - 100, cy - size * 0.8,
                         f"|w|={abs(w):.6f}  →  |w⁻¹|={abs(w_inv):.6f}",
                         font_size="8", fill="#c0392b",
                         font_family="monospace"))

    # Forward spiral (compression) — blue
    for n in range(12):
        wn = w ** n
        px = cx + R * wn.real / max(abs(w ** 0), 0.001)
        py = cy - R * wn.imag / max(abs(w ** 0), 0.001)
        r = max(2, 6 - n * 0.4)
        children.append(circle(px, py, r,
                               fill="#3498db", fill_opacity="0.7",
                               stroke="#2c3e50", stroke_width="0.5"))
        if n < 6:
            children.append(text(px + 8, py + 3,
                                 f"w^{n}={abs(wn):.4f}",
                                 font_size="6", fill="#3498db",
                                 font_family="monospace"))
        # Connect to previous
        if n > 0:
            wn_prev = w ** (n - 1)
            ppx = cx + R * wn_prev.real
            ppy = cy - R * wn_prev.imag
            children.append(line(ppx, ppy, px, py,
                                 stroke="#3498db", stroke_width="0.5",
                                 stroke_opacity="0.5"))

    # Inverse spiral (expansion) — red
    for n in range(6):
        wn_inv = w_inv ** n
        # Cap the display radius
        display_mod = min(abs(wn_inv), 3.0)
        scale = R * display_mod / 3.0
        angle = cmath.phase(wn_inv)
        px = cx + scale * math.cos(angle)
        py = cy - scale * math.sin(angle)
        r = max(2, 3 + n * 0.5)
        children.append(circle(px, py, r,
                               fill="#c0392b", fill_opacity="0.7",
                               stroke="#c0392b", stroke_width="0.5"))
        children.append(text(px + 8, py + 3,
                             f"w⁻^{n}={abs(wn_inv):.4f}",
                             font_size="6", fill="#c0392b",
                             font_family="monospace"))

    # Legend
    children.append(circle(cx - size * 0.8, cy + size * 0.7, 4,
                           fill="#3498db"))
    children.append(text(cx - size * 0.8 + 8, cy + size * 0.7 + 3,
                         "w^n (compress: 0.707^n → 0)",
                         font_size="7", fill="#3498db"))
    children.append(circle(cx - size * 0.8, cy + size * 0.8, 4,
                           fill="#c0392b"))
    children.append(text(cx - size * 0.8 + 8, cy + size * 0.8 + 3,
                         "w⁻ⁿ (expand: 1.414^n → ∞)",
                         font_size="7", fill="#c0392b"))

    return group(children)


def render_numerical_inversion(width: int = 3200, height: int = 2800) -> str:
    """FULL NUMERICAL INVERSION of all 12 crystal calculations.

    Every value is the ACTUAL computed number from geometric_constants.py
    and cross_lens.py. Each value's 1/x inverse is computed and displayed.

    12 panels:
      1. PHI cascade          2. Bridge weights graph
      3. w-operator spiral    4. Attractor values
      5. Flower rings         6. E8 face boosts
      7. Lens weights         8. Cross-lens transitions
      9. Weave periods       10. Containment counts
     11. w-spiral trajectory  12. Vesica + transform weights
    """
    canvas = SVGCanvas(width, height, background="#f8f7f4")

    # Arrow marker
    canvas.add_def(
        '<marker id="inv_arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#c0392b"/>'
        '</marker>'
    )

    # ── Title ──
    canvas.add(text(width // 2 - 450, 35,
                    "NUMERICAL INVERSION — ALL 12 CRYSTAL CALCULATIONS × 1/x",
                    font_size="24", fill="#2c3e50", font_weight="bold",
                    font_family="monospace"))
    canvas.add(text(width // 2 - 380, 58,
                    "Every number is COMPUTED from geometric_constants.py & cross_lens.py. "
                    "Inverse = 1/x EXACTLY.",
                    font_size="11", fill="#777", font_family="monospace"))

    # Key equation bar
    canvas.add(rect(20, 68, width - 40, 24, rx=4,
                    fill="#2c3e50", fill_opacity="0.06"))
    key_eqs = [
        "φ=1.6180→1/φ=0.6180",
        "B(SF)=0.618→1/B=1.618",
        "|w|=0.707→|w⁻¹|=1.414",
        "attr=0.250→1/attr=4.000",
        "ring₆=0.056→1/r₆=17.944",
        "E8=1.500→1/E8=0.667",
    ]
    for i, eq in enumerate(key_eqs):
        canvas.add(text(35 + i * (width - 70) // len(key_eqs), 84,
                        eq, font_size="9", fill="#c0392b",
                        font_family="monospace", font_weight="bold"))

    # ── Compute all inversions ──
    all_inv = _compute_all_inversions()

    # ── Layout: 4 columns × 3 rows of table panels ──
    # Plus 3 graphical panels interspersed
    margin_top = 105
    n_cols = 4
    n_rows = 4  # extra row for graphical panels
    col_w = (width - 60) / n_cols
    row_h = (height - margin_top - 40) / n_rows
    table_w = col_w - 20
    table_h = row_h - 20

    # Panel colors per category
    panel_colors = {
        "PHI_CASCADE":      "#DAA520",
        "BRIDGE_WEIGHTS":   "#8B4513",
        "W_OPERATOR":       "#3498db",
        "ATTRACTOR":        "#e74c3c",
        "FLOWER_RINGS":     "#9b59b6",
        "E8_BOOSTS":        "#228B22",
        "LENS_WEIGHTS":     "#FF6347",
        "CROSS_LENS":       "#2980b9",
        "WEAVE_PERIODS":    "#8e44ad",
        "CONTAINMENT":      "#c0392b",
        "W_SPIRAL":         "#1abc9c",
        "VESICA_TRANSFORM": "#d35400",
    }

    # Row 0: 4 numerical tables
    table_layout = [
        # (col, row, category_key, title, max_rows)
        (0, 0, "PHI_CASCADE",   "1. PHI CASCADE (φ and powers)", 8),
        (1, 0, "BRIDGE_WEIGHTS", "2. BRIDGE WEIGHTS (6 pairs)", 8),
        (2, 0, "W_OPERATOR",    "3. w-OPERATOR (complex)", 10),
        (3, 0, "ATTRACTOR",     "4. ATTRACTOR (META LOOP³)", 8),
        (0, 1, "FLOWER_RINGS",  "5. FLOWER RINGS (decay→growth)", 8),
        (1, 1, "E8_BOOSTS",     "6. E8 FACE BOOSTS (240 roots)", 12),
        (2, 1, "LENS_WEIGHTS",  "7. ELEMENT LENS WEIGHTS", 12),
        (3, 1, "CROSS_LENS",    "8. CROSS-LENS TRANSITIONS", 10),
        (0, 2, "WEAVE_PERIODS", "9. WEAVE PERIODS (W3-W9)", 10),
        (1, 2, "CONTAINMENT",   "10. CONTAINMENT COUNTS", 8),
        (2, 2, "W_SPIRAL",      "11. w-SPIRAL |w^n| TRAJECTORY", 10),
        (3, 2, "VESICA_TRANSFORM", "12. VESICA + TRANSFORM φ", 10),
    ]

    for col, row, key, title, max_r in table_layout:
        tcx = 30 + col_w * (col + 0.5)
        tcy = margin_top + row_h * (row + 0.5)
        rows = all_inv.get(key, [])
        color = panel_colors.get(key, "#333")
        canvas.add(_render_num_table(tcx, tcy, table_w, table_h,
                                     title, rows, color, max_r))

    # ── Row 3: Graphical panels (bridge graph, flower, w-spiral) ──
    graph_y = margin_top + row_h * 3.5
    graph_h = row_h - 20
    graph_w = (width - 60) / 3

    # Bridge graph
    canvas.add(_render_bridge_graph(30 + graph_w * 0.5,
                                     graph_y, graph_h * 0.9))
    canvas.add(text(30 + graph_w * 0.5 - 60, graph_y - graph_h * 0.45,
                    "BRIDGE TOPOLOGY: weight → 1/weight",
                    font_size="10", fill="#8B4513", font_weight="bold",
                    font_family="monospace"))

    # Flower inversion
    canvas.add(_render_flower_inversion(30 + graph_w * 1.5,
                                         graph_y, graph_h * 0.9))

    # w-spiral inversion
    canvas.add(_render_w_spiral_inversion(30 + graph_w * 2.5,
                                           graph_y, graph_h * 0.9))

    # ── Footer: the master inversion law ──
    fy = height - 30
    canvas.add(line(30, fy - 15, width - 30, fy - 15,
                    stroke="#ccc", stroke_width="0.5"))
    footer_lines = [
        "INVERSION LAW: For every crystal value v, its inverse 1/v lives "
        "in the ANTI-CRYSTAL. Together v × (1/v) = 1 = identity.",
        "Compression (|w|=0.707) inverts to expansion (|w⁻¹|=1.414). "
        "Decay (φ⁻ⁿ→0) inverts to growth (φⁿ→∞). "
        "Bridges (0.618) become bodies (1.618). "
        "The attractor (0.25) explodes (4.0).",
    ]
    for i, fl in enumerate(footer_lines):
        canvas.add(text(30, fy + i * 14, fl,
                        font_size="9", fill="#777",
                        font_family="monospace"))

    return canvas.render()


def save_numerical_inversion(out_path: Optional[str] = None) -> str:
    """Generate and save the full numerical inversion SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "numerical_inversion_108d.svg")

    svg = render_numerical_inversion()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path


# ══════════════════════════════════════════════════════════════════════════
#  WOVEN INVERSION CASCADE — Invert 3D, then REWEAVE through W3→W5→W7→W9
# ══════════════════════════════════════════════════════════════════════════
# You cannot just invert 108D. The weaving routes differently.
# Start at 3D (which CAN be simply flipped), then reweave the inverted
# values through each weave operator. At each level the inverted strand
# weights are 1/original, so decay becomes growth and the inverted crystal
# EXPLODES through the weave.

from .geometric_constants import TRANSFORM_PHI_WEIGHTS


def _compute_woven_inversion() -> Dict[str, Any]:
    """Compute the full woven inversion cascade: 3D⁻¹ → W3 → 6D⁻¹ → ... → 12D⁻¹.

    At each weave level:
      original: base × flower_ring[i] × phi_weight  (decay)
      inverted: (1/base) × (1/flower_ring[i]) × (1/phi_weight)  (growth)

    Returns dict with per-level strand values, sums, and A+ cross-ratios.
    """
    from .dimensional_projector import W3, W5, W7, W9

    w_op = W_OP_COMPLEX
    w_inv = 1.0 / w_op

    # Extended flower rings for 9 strands (only 7 in FLOWER_RINGS)
    ext_rings = list(FLOWER_RINGS) + [PHI_INV ** 7, PHI_INV ** 8]

    levels = {}

    # ── 3D: Three wreaths, flower-ring weighted ──
    wreath_names = W3.strands  # Su, Me, Sa
    w3_orig = [FLOWER_RINGS[i] for i in range(3)]
    w3_inv = [1.0 / r for r in w3_orig]
    levels["3D"] = {
        "dim": 3, "label": "3D SEED (simple flip)",
        "operator": "—", "order": 3,
        "strand_names": wreath_names,
        "orig_strands": w3_orig,
        "inv_strands": w3_inv,
        "orig_sum": sum(w3_orig),
        "inv_sum": sum(w3_inv),
        "color": DIM_COLORS.get(3, "#e74c3c"),
    }

    # ── 4D: Möbius reweave — attractor × |w| ──
    attr_val = ATTRACTOR["path_value"]  # 0.25
    # 4 SFCR faces, each at attractor value, compressed by |w|
    m4_orig = attr_val * abs(w_op)
    m4_inv = (1.0 / attr_val) * abs(w_inv)
    levels["4D"] = {
        "dim": 4, "label": "4D TESSERACT (Möbius × |w|)",
        "operator": "Möbius", "order": 4,
        "strand_names": list(FACES),
        "orig_strands": [m4_orig] * 4,
        "inv_strands": [m4_inv] * 4,
        "orig_sum": m4_orig * 4,
        "inv_sum": m4_inv * 4,
        "detail": (f"attr={attr_val:.4f}×|w|={abs(w_op):.4f} = {m4_orig:.6f} | "
                   f"inv: {1/attr_val:.4f}×|w⁻¹|={abs(w_inv):.4f} = {m4_inv:.6f}"),
        "color": DIM_COLORS.get(4, "#e67e22"),
    }

    # ── 6D = W3 × 4D ──
    phi_w3 = TRANSFORM_PHI_WEIGHTS[3]
    s6_orig = [m4_orig * FLOWER_RINGS[i] * phi_w3 for i in range(3)]
    s6_inv = [m4_inv * (1.0 / FLOWER_RINGS[i]) * (1.0 / phi_w3) for i in range(3)]
    levels["6D"] = {
        "dim": 6, "label": "6D MÖBIUS BODY (W3 × 4D⁻¹)",
        "operator": f"W3 (φ^0={phi_w3:.4f})", "order": 3,
        "strand_names": wreath_names,
        "orig_strands": s6_orig,
        "inv_strands": s6_inv,
        "orig_sum": sum(s6_orig),
        "inv_sum": sum(s6_inv),
        "color": DIM_COLORS.get(6, "#f1c40f"),
    }

    # ── 8D = W5 × 6D ──
    phi_w5 = TRANSFORM_PHI_WEIGHTS[5]
    base_8_orig = sum(s6_orig)
    base_8_inv = sum(s6_inv)
    s8_orig = [base_8_orig * FLOWER_RINGS[i] * phi_w5 for i in range(5)]
    s8_inv = [base_8_inv * (1.0 / FLOWER_RINGS[i]) * (1.0 / phi_w5) for i in range(5)]
    levels["8D"] = {
        "dim": 8, "label": "8D PENTADIC (W5 × 6D⁻¹)",
        "operator": f"W5 (φ^(1/3)={phi_w5:.4f})", "order": 5,
        "strand_names": W5.strands,
        "orig_strands": s8_orig,
        "inv_strands": s8_inv,
        "orig_sum": sum(s8_orig),
        "inv_sum": sum(s8_inv),
        "color": DIM_COLORS.get(8, "#1abc9c"),
    }

    # ── 10D = W7 × 8D ──
    phi_w7 = TRANSFORM_PHI_WEIGHTS[7]
    base_10_orig = sum(s8_orig)
    base_10_inv = sum(s8_inv)
    s10_orig = [base_10_orig * ext_rings[i] * phi_w7 for i in range(7)]
    s10_inv = [base_10_inv * (1.0 / ext_rings[i]) * (1.0 / phi_w7) for i in range(7)]
    levels["10D"] = {
        "dim": 10, "label": "10D HEPTADIC (W7 × 8D⁻¹)",
        "operator": f"W7 (φ^(2/3)={phi_w7:.4f})", "order": 7,
        "strand_names": W7.strands,
        "orig_strands": s10_orig,
        "inv_strands": s10_inv,
        "orig_sum": sum(s10_orig),
        "inv_sum": sum(s10_inv),
        "color": DIM_COLORS.get(10, "#3498db"),
    }

    # ── 12D = W9 × 10D ──
    phi_w9 = TRANSFORM_PHI_WEIGHTS[9]
    base_12_orig = sum(s10_orig)
    base_12_inv = sum(s10_inv)
    s12_orig = [base_12_orig * ext_rings[i] * phi_w9 for i in range(9)]
    s12_inv = [base_12_inv * (1.0 / ext_rings[i]) * (1.0 / phi_w9) for i in range(9)]
    levels["12D"] = {
        "dim": 12, "label": "12D CROWN (W9 × 10D⁻¹)",
        "operator": f"W9 (φ={phi_w9:.4f})", "order": 9,
        "strand_names": W9.strands,
        "orig_strands": s12_orig,
        "inv_strands": s12_inv,
        "orig_sum": sum(s12_orig),
        "inv_sum": sum(s12_inv),
        "color": DIM_COLORS.get(12, "#9b59b6"),
    }

    # ── A+ cross-dimensional ratios ──
    a_plus = {}
    for key, lvl in levels.items():
        o = lvl["orig_sum"]
        i = lvl["inv_sum"]
        a_plus[key] = {
            "orig": o,
            "inv": i,
            "ratio": i / o if o > 0 else float('inf'),
            "product": o * i,
            "log_ratio": math.log(i / o) if o > 0 and i > 0 else 0,
        }

    # ── Permutation atlas per weave level (from Crystal Weaving doc) ──
    # Each odd-prime weave has n! permutations = the reweave search space
    perm_atlas = {
        "3D": {"n": 3, "n_fact": 6, "label": "3! = 6 tri-current states"},
        "6D": {"n": 3, "n_fact": 6, "label": "3! = 6 (W3 alchemy permutations)"},
        "8D": {"n": 5, "n_fact": 120, "label": "5! = 120 (W5 animal permutations)"},
        "10D": {"n": 7, "n_fact": 5040, "label": "7! = 5,040 (W7 planet permutations)"},
        "12D": {"n": 9, "n_fact": 362880, "label": "9! = 362,880 (W9 enneadic permutations)"},
    }

    # Inject perm_atlas into each level dict for rendering
    for key, pa in perm_atlas.items():
        if key in levels:
            levels[key]["perm_atlas"] = pa

    # ── Reseeding pipeline (from KC27 Runtime Closure doc) ──
    # Inversion is step 4 of 7 — it CANNOT be done standalone
    reseeding_pipeline = [
        ("Expand",       "unfold seed through operator algebra"),
        ("Compress",     "reduce to minimal representation"),
        ("Trace",        "record expansion/compression trace"),
        ("Invert (μ₄)",  "apply Möbius involution → Chart B"),
        ("Rot₉₀",       "quarter-turn rotation"),
        ("Σ₆₀",         "full shell cycle (60 icosahedral views)"),
        ("Collapse A+",  "project back to Chart A (crown)"),
    ]

    # ── Full operator chain (from Crystal Weaving doc) ──
    # QSHRINK_tot ∘ PolarCompress_4 ∘ Braid_108 ∘ Proj_108 ∘ Weave_{9,7,5,3} ∘ A+ ∘ ReWeave_m
    operator_chain = [
        "ReWeave_m", "A+", "Weave_{9,7,5,3}",
        "Proj_108", "Braid_108", "PolarCompress_4", "QSHRINK_tot",
    ]

    return {
        "levels": levels,
        "a_plus": a_plus,
        "perm_atlas": perm_atlas,
        "reseeding_pipeline": reseeding_pipeline,
        "operator_chain": operator_chain,
    }


def _render_woven_level(cx: float, cy: float, w: float, h: float,
                        level: Dict[str, Any]) -> str:
    """Render a single woven inversion level showing strand-by-strand values."""
    children = []
    color = level["color"]
    dim = level["dim"]

    # Panel background
    children.append(rect(cx - w / 2, cy - h / 2, w, h, rx=6,
                         fill="#fefefe", stroke=color, stroke_width="2",
                         fill_opacity="0.97"))

    # Title bar
    children.append(rect(cx - w / 2, cy - h / 2, w, 24, rx=6,
                         fill=color, fill_opacity="0.2"))
    children.append(text(cx - w / 2 + 8, cy - h / 2 + 16, level["label"],
                         font_size="10", fill=color, font_weight="bold",
                         font_family="monospace"))

    # Operator badge
    children.append(text(cx + w / 2 - 100, cy - h / 2 + 16,
                         level["operator"],
                         font_size="8", fill="#777", font_family="monospace"))

    # Column headers
    hy = cy - h / 2 + 40
    col_name = cx - w / 2 + 8
    col_orig = cx - w / 2 + w * 0.28
    col_inv = cx - w / 2 + w * 0.53
    col_ratio = cx - w / 2 + w * 0.78

    children.append(text(col_name, hy, "strand",
                         font_size="7", fill="#999", font_family="monospace"))
    children.append(text(col_orig, hy, "original",
                         font_size="7", fill="#2c3e50", font_family="monospace"))
    children.append(text(col_inv, hy, "inverted",
                         font_size="7", fill="#c0392b", font_family="monospace"))
    children.append(text(col_ratio, hy, "inv/orig",
                         font_size="7", fill="#8e44ad", font_family="monospace"))

    children.append(line(cx - w / 2 + 4, hy + 4,
                         cx + w / 2 - 4, hy + 4,
                         stroke="#ddd", stroke_width="0.5"))

    # Strand rows
    names = level["strand_names"]
    origs = level["orig_strands"]
    invs = level["inv_strands"]
    max_rows = min(len(names), 9)
    row_h_px = min(13, (h - 80) / max(max_rows + 2, 1))

    for i in range(max_rows):
        ry = hy + 14 + i * row_h_px

        if i % 2 == 0:
            children.append(rect(cx - w / 2 + 2, ry - 9, w - 4, row_h_px,
                                 fill=color, fill_opacity="0.04"))

        # Strand name
        sname = names[i] if len(names[i]) <= 8 else names[i][:7] + "…"
        children.append(text(col_name, ry, sname,
                             font_size="7.5", fill="#444",
                             font_family="monospace"))

        # Original value
        def _fmt_val(v):
            if abs(v) >= 1000:
                return f"{v:.1f}"
            elif abs(v) >= 1:
                return f"{v:.4f}"
            else:
                return f"{v:.6f}"

        children.append(text(col_orig, ry, _fmt_val(origs[i]),
                             font_size="7.5", fill="#2c3e50",
                             font_family="monospace", font_weight="bold"))

        # Inverted value
        children.append(text(col_inv, ry, _fmt_val(invs[i]),
                             font_size="7.5", fill="#c0392b",
                             font_family="monospace", font_weight="bold"))

        # Ratio
        ratio_i = invs[i] / origs[i] if origs[i] > 0 else 0
        children.append(text(col_ratio, ry, f"×{ratio_i:.2f}",
                             font_size="7", fill="#8e44ad",
                             font_family="monospace"))

        # Mini bar
        bar_x = cx + w / 2 - 30
        bar_max = 20
        # Log-scale bar
        log_ratio = math.log10(max(ratio_i, 0.01))
        bar_len = min(bar_max, max(2, log_ratio * 5))
        children.append(rect(bar_x, ry - 4, bar_len, 4, rx=1,
                             fill="#8e44ad", fill_opacity="0.4"))

    # Sum row
    sum_y = hy + 14 + max_rows * row_h_px + 4
    children.append(line(cx - w / 2 + 4, sum_y - 6,
                         cx + w / 2 - 4, sum_y - 6,
                         stroke=color, stroke_width="0.8"))
    children.append(text(col_name, sum_y + 2, "Σ TOTAL",
                         font_size="8", fill=color,
                         font_family="monospace", font_weight="bold"))
    children.append(text(col_orig, sum_y + 2, _fmt_val(level["orig_sum"]),
                         font_size="8", fill="#2c3e50",
                         font_family="monospace", font_weight="bold"))
    children.append(text(col_inv, sum_y + 2, _fmt_val(level["inv_sum"]),
                         font_size="8", fill="#c0392b",
                         font_family="monospace", font_weight="bold"))
    ratio_sum = level["inv_sum"] / level["orig_sum"] if level["orig_sum"] > 0 else 0
    children.append(text(col_ratio, sum_y + 2, f"×{ratio_sum:.2f}",
                         font_size="8", fill="#8e44ad",
                         font_family="monospace", font_weight="bold"))

    # Permutation atlas badge (if provided)
    perm = level.get("perm_atlas")
    if perm:
        badge_y = cy + h / 2 - 14
        children.append(rect(cx - w / 2 + 4, badge_y - 8, w - 8, 16, rx=3,
                             fill="#8e44ad", fill_opacity="0.08",
                             stroke="#8e44ad", stroke_width="0.5"))
        children.append(text(cx - w / 2 + 10, badge_y + 3,
                             f"⟡ PERM ATLAS: {perm['label']}",
                             font_size="7", fill="#8e44ad",
                             font_family="monospace"))

    return group(children)


def _render_a_plus_panel(cx: float, cy: float, w: float, h: float,
                         a_plus: Dict[str, Dict]) -> str:
    """Render the A+ cross-dimensional comparison panel.

    Shows how the inverted-then-woven values diverge from the original
    at each dimensional level. The A+ ratio = inv/orig grows exponentially
    because inverted strand weights (1/φ⁻ⁿ = φⁿ) compound through the weave.
    """
    children = []

    # Panel background
    children.append(rect(cx - w / 2, cy - h / 2, w, h, rx=8,
                         fill="#1a1a2e", stroke="#c0392b", stroke_width="2"))

    # Title
    children.append(text(cx - w / 2 + 15, cy - h / 2 + 22,
                         "A+ CROSS: WOVEN INVERSION DIVERGENCE",
                         font_size="12", fill="#e74c3c", font_weight="bold",
                         font_family="monospace"))
    children.append(text(cx - w / 2 + 15, cy - h / 2 + 38,
                         "Original decays (φ⁻ⁿ→0) — Inverted EXPLODES (φⁿ→∞) through weave",
                         font_size="8", fill="#aaa", font_family="monospace"))

    # Level order
    level_order = ["3D", "4D", "6D", "8D", "10D", "12D"]
    dim_colors = {
        "3D": "#e74c3c", "4D": "#e67e22", "6D": "#f1c40f",
        "8D": "#1abc9c", "10D": "#3498db", "12D": "#9b59b6",
    }

    # Bar chart area
    chart_x = cx - w / 2 + 40
    chart_w = w - 80
    chart_y = cy - h / 2 + 55
    chart_h = h - 140

    # Compute log-scale for display
    max_log = 0
    for key in level_order:
        if key in a_plus:
            lr = a_plus[key]["log_ratio"]
            if lr > max_log:
                max_log = lr

    bar_h_each = chart_h / len(level_order) - 8

    for i, key in enumerate(level_order):
        if key not in a_plus:
            continue
        ap = a_plus[key]
        by = chart_y + i * (chart_h / len(level_order))
        color = dim_colors.get(key, "#fff")

        # Level label
        children.append(text(chart_x - 30, by + bar_h_each / 2 + 4, key,
                             font_size="11", fill=color, font_weight="bold",
                             font_family="monospace"))

        # Original bar (blue, log scale)
        log_orig = math.log10(max(ap["orig"], 1e-10)) + 10  # shift to positive
        log_inv = math.log10(max(ap["inv"], 1e-10)) + 10

        scale = chart_w / (max_log + 12)  # normalize
        bar_orig_w = max(2, log_orig * scale)
        bar_inv_w = max(2, log_inv * scale)

        # Original bar
        children.append(rect(chart_x, by, bar_orig_w, bar_h_each * 0.4, rx=2,
                             fill="#3498db", fill_opacity="0.7"))
        # Inverted bar
        children.append(rect(chart_x, by + bar_h_each * 0.45,
                             bar_inv_w, bar_h_each * 0.4, rx=2,
                             fill="#c0392b", fill_opacity="0.8"))

        # Values
        def _short(v):
            if v >= 1e6:
                return f"{v:.0f}"
            elif v >= 100:
                return f"{v:.1f}"
            elif v >= 1:
                return f"{v:.4f}"
            else:
                return f"{v:.6f}"

        children.append(text(chart_x + bar_orig_w + 5, by + bar_h_each * 0.35,
                             _short(ap["orig"]),
                             font_size="7", fill="#5dade2",
                             font_family="monospace"))
        children.append(text(chart_x + bar_inv_w + 5, by + bar_h_each * 0.8,
                             _short(ap["inv"]),
                             font_size="7", fill="#e74c3c",
                             font_family="monospace"))

        # A+ ratio on far right
        children.append(text(cx + w / 2 - 85, by + bar_h_each * 0.6,
                             f"A+= ×{ap['ratio']:.1f}",
                             font_size="9", fill="#f39c12",
                             font_family="monospace", font_weight="bold"))

    # Legend
    ly = cy + h / 2 - 50
    children.append(rect(chart_x, ly, 12, 8, fill="#3498db", fill_opacity="0.7"))
    children.append(text(chart_x + 16, ly + 7, "Original (weave with φ⁻ⁿ decay)",
                         font_size="8", fill="#5dade2", font_family="monospace"))
    children.append(rect(chart_x, ly + 14, 12, 8, fill="#c0392b", fill_opacity="0.8"))
    children.append(text(chart_x + 16, ly + 21, "Inverted (reweave with φⁿ growth)",
                         font_size="8", fill="#e74c3c", font_family="monospace"))
    children.append(rect(chart_x, ly + 28, 12, 8, fill="#f39c12", fill_opacity="0.7"))
    children.append(text(chart_x + 16, ly + 35,
                         "A+ = inv/orig (exponential divergence through weave)",
                         font_size="8", fill="#f39c12", font_family="monospace"))

    # Key equation
    children.append(text(cx - w / 2 + 15, cy + h / 2 - 8,
                         "A+(12D) = ×70,624 | Because: each weave multiplies by φⁿ "
                         "instead of φ⁻ⁿ — the weave ROUTES the inversion into explosion",
                         font_size="7", fill="#f39c12", font_family="monospace"))

    return group(children)


def _render_reseeding_pipeline(cx: float, cy: float, w: float, h: float,
                               pipeline: list) -> str:
    """Render the 7-step reseeding pipeline as a horizontal flow diagram.

    From KC27 Runtime Closure: inversion is step 4 of 7, NOT standalone.
    Expand → Compress → Trace → Invert(μ₄) → Rot₉₀ → Σ₆₀ → Collapse A+
    """
    children = []

    # Panel background
    children.append(rect(cx - w / 2, cy - h / 2, w, h, rx=8,
                         fill="#1a1a2e", stroke="#e67e22", stroke_width="2"))

    # Title
    children.append(text(cx - w / 2 + 15, cy - h / 2 + 18,
                         "RESEEDING PIPELINE (KC27 Runtime Closure)",
                         font_size="11", fill="#e67e22", font_weight="bold",
                         font_family="monospace"))
    children.append(text(cx - w / 2 + 15, cy - h / 2 + 32,
                         "Inversion is step 4 of 7 — it CANNOT be performed standalone",
                         font_size="8", fill="#aaa", font_family="monospace"))

    # Flow boxes
    n = len(pipeline)
    box_area_x = cx - w / 2 + 20
    box_area_w = w - 40
    box_w = box_area_w / n - 10
    box_h = 38
    box_y = cy - box_h / 2 + 5

    step_colors = [
        "#3498db", "#1abc9c", "#2ecc71", "#e74c3c",
        "#9b59b6", "#f1c40f", "#e67e22",
    ]

    for i, (name, desc) in enumerate(pipeline):
        bx = box_area_x + i * (box_area_w / n) + 5
        color = step_colors[i % len(step_colors)]
        is_invert = i == 3  # Step 4 (0-indexed: 3)

        # Box
        fill_c = "#3d1a1a" if is_invert else "#1a1a2e"
        stroke_w = "2.5" if is_invert else "1.5"
        children.append(rect(bx, box_y, box_w, box_h, rx=5,
                             fill=fill_c, stroke=color,
                             stroke_width=stroke_w))

        # Step number
        children.append(text(bx + 3, box_y + 12, f"#{i + 1}",
                             font_size="7", fill="#666",
                             font_family="monospace"))

        # Name
        children.append(text(bx + box_w / 2 - len(name) * 2.5, box_y + 22,
                             name,
                             font_size="9", fill=color,
                             font_weight="bold",
                             font_family="monospace"))

        # Description (truncated)
        short_desc = desc[:18] + "…" if len(desc) > 18 else desc
        children.append(text(bx + 3, box_y + 34, short_desc,
                             font_size="6", fill="#888",
                             font_family="monospace"))

        # Arrow between boxes
        if i < n - 1:
            ax = bx + box_w + 1
            children.append(text(ax, box_y + box_h / 2 + 4, "→",
                                 font_size="12", fill="#555"))

    # Highlight annotation for step 4
    children.append(text(cx - w / 2 + 15, cy + h / 2 - 8,
                         "★ Step 4 (Invert μ₄): J(x,y,ε)=(y,x,−ε), μ₄∘μ₄=id "
                         "| Forward/inverse crystal pair collapses through Z* at 108D",
                         font_size="7", fill="#e74c3c", font_family="monospace"))

    return group(children)


def _render_operator_chain(cx: float, cy: float, w: float, h: float,
                           chain: list) -> str:
    """Render the full operator composition chain as a horizontal pipeline.

    From Crystal Weaving doc:
    ReWeave_m → A+ → Weave_{9,7,5,3} → Proj_108 → Braid_108 → PolarCompress_4 → QSHRINK_tot
    """
    children = []

    # Panel background
    children.append(rect(cx - w / 2, cy - h / 2, w, h, rx=8,
                         fill="#1a1a2e", stroke="#1abc9c", stroke_width="2"))

    # Title
    children.append(text(cx - w / 2 + 15, cy - h / 2 + 18,
                         "OPERATOR CHAIN (Crystal Weaving Navigation)",
                         font_size="11", fill="#1abc9c", font_weight="bold",
                         font_family="monospace"))
    children.append(text(cx - w / 2 + 15, cy - h / 2 + 32,
                         "QSHRINK_tot ∘ PolarCompress₄ ∘ Braid₁₀₈ ∘ Proj₁₀₈ "
                         "∘ Weave_{9,7,5,3} ∘ A+ ∘ ReWeave_m",
                         font_size="8", fill="#aaa", font_family="monospace"))

    # Chain boxes (right-to-left composition, displayed left-to-right)
    n = len(chain)
    box_area_x = cx - w / 2 + 20
    box_area_w = w - 40
    box_w = box_area_w / n - 12
    box_h = 30
    box_y = cy - box_h / 2 + 8

    op_colors = {
        "ReWeave_m": "#e74c3c", "A+": "#f39c12",
        "Weave_{9,7,5,3}": "#f1c40f", "Proj_108": "#2ecc71",
        "Braid_108": "#1abc9c", "PolarCompress_4": "#3498db",
        "QSHRINK_tot": "#9b59b6",
    }

    for i, op_name in enumerate(chain):
        bx = box_area_x + i * (box_area_w / n) + 6
        color = op_colors.get(op_name, "#aaa")

        children.append(rect(bx, box_y, box_w, box_h, rx=4,
                             fill="#1a1a2e", stroke=color,
                             stroke_width="1.5"))

        # Operator name
        display = op_name.replace("_", " ")
        font_sz = "8" if len(display) <= 12 else "6.5"
        children.append(text(bx + box_w / 2 - len(display) * 2,
                             box_y + box_h / 2 + 3, display,
                             font_size=font_sz, fill=color,
                             font_weight="bold",
                             font_family="monospace"))

        # Composition operator
        if i < n - 1:
            children.append(text(bx + box_w + 1, box_y + box_h / 2 + 4,
                                 "∘", font_size="14", fill="#555"))

    # Bottom annotation
    children.append(text(cx - w / 2 + 15, cy + h / 2 - 8,
                         "Each operator transforms the crystal: "
                         "ReWeave seeds → A+ cross-ratios → Weave dimensions → "
                         "Project → Braid → Compress → QSHRINK hologram",
                         font_size="7", fill="#1abc9c", font_family="monospace"))

    return group(children)


def render_woven_inversion(width: int = 3200, height: int = 2900) -> str:
    """WOVEN INVERSION CASCADE: invert 3D, reweave through W3→W5→W7→W9 to 12D⁻¹.

    You cannot just invert 108D — the weaving routes differently.
    Start at 3D (simple flip), then the inverted values propagate through
    each weave operator with INVERTED strand weights:
      - Original: base × φ⁻ⁿ × φ_weight  (decay at each strand)
      - Inverted: (1/base) × φⁿ × (1/φ_weight)  (growth at each strand)

    3D⁻¹ → Möbius → 4D⁻¹ → W3 → 6D⁻¹ → W5 → 8D⁻¹ → W7 → 10D⁻¹ → W9 → 12D⁻¹

    6 level panels + 1 A+ panel + reseeding pipeline + operator chain.
    Includes permutation atlas badges on each level panel (from Crystal Weaving).
    """
    canvas = SVGCanvas(width, height, background="#f0ede6")

    # Compute everything
    data = _compute_woven_inversion()
    levels = data["levels"]
    a_plus = data["a_plus"]
    reseeding_pipeline = data["reseeding_pipeline"]
    operator_chain = data["operator_chain"]

    # Title
    canvas.add(text(width // 2 - 480, 35,
                    "WOVEN INVERSION CASCADE — 3D⁻¹ REWEAVED THROUGH W3→W5→W7→W9 → 12D⁻¹",
                    font_size="22", fill="#2c3e50", font_weight="bold",
                    font_family="monospace"))
    canvas.add(text(width // 2 - 480, 58,
                    "You cannot invert 108D directly — the weave routes differently. "
                    "Invert 3D, then reweave. Decay (φ⁻ⁿ) becomes growth (φⁿ) AT EVERY LEVEL.",
                    font_size="10", fill="#777", font_family="monospace"))

    # Key equation bar
    canvas.add(rect(20, 68, width - 40, 22, rx=4,
                    fill="#c0392b", fill_opacity="0.08"))
    canvas.add(text(30, 83,
                    "3D: flip (×2.62) → 4D: Möbius (×32) → 6D: W3 reweave (×83.8) "
                    "→ 8D: W5 (×416.6) → 10D: W7 (×3,936) → 12D: W9 (×70,624)  |  "
                    "A+ EXPLODES through the weave because φ⁻ⁿ→φⁿ at each strand",
                    font_size="9", fill="#c0392b",
                    font_family="monospace", font_weight="bold"))

    # Layout: 3 columns × 2 rows for level panels, then A+ panel below
    margin_top = 100
    n_cols = 3
    n_rows = 2
    level_order = ["3D", "4D", "6D", "8D", "10D", "12D"]

    panel_area_h = (height - margin_top - 20) * 0.55
    col_w = (width - 60) / n_cols
    row_h = panel_area_h / n_rows
    panel_w = col_w - 15
    panel_h = row_h - 12

    for idx, key in enumerate(level_order):
        col = idx % n_cols
        row = idx // n_cols
        pcx = 30 + col_w * (col + 0.5)
        pcy = margin_top + row_h * (row + 0.5)

        level = levels[key]
        canvas.add(_render_woven_level(pcx, pcy, panel_w, panel_h, level))

        # Arrow between panels
        if idx < len(level_order) - 1:
            next_col = (idx + 1) % n_cols
            next_row = (idx + 1) // n_cols
            ncx = 30 + col_w * (next_col + 0.5)
            ncy = margin_top + row_h * (next_row + 0.5)

            if next_row == row:
                # Horizontal arrow
                ax1 = pcx + panel_w / 2 + 2
                ax2 = ncx - panel_w / 2 - 2
                canvas.add(text((ax1 + ax2) / 2 - 5, pcy - 2, "→",
                                font_size="16", fill="#c0392b",
                                font_weight="bold"))
            else:
                # Wrap to next row - draw down-arrow at right edge
                canvas.add(text(pcx + panel_w / 2 + 3, pcy + panel_h / 4,
                                "↵", font_size="14", fill="#c0392b"))

    # A+ panel
    ap_y = margin_top + panel_area_h + 30
    ap_h = 380
    canvas.add(_render_a_plus_panel(width / 2, ap_y + ap_h / 2,
                                     width - 60, ap_h, a_plus))

    # Reseeding pipeline panel
    rp_y = ap_y + ap_h + 20
    rp_h = 120
    canvas.add(_render_reseeding_pipeline(width / 2, rp_y + rp_h / 2,
                                           width - 60, rp_h,
                                           reseeding_pipeline))

    # Operator chain panel
    oc_y = rp_y + rp_h + 15
    oc_h = 100
    canvas.add(_render_operator_chain(width / 2, oc_y + oc_h / 2,
                                       width - 60, oc_h,
                                       operator_chain))

    return canvas.render()


def save_woven_inversion(out_path: Optional[str] = None) -> str:
    """Generate and save the woven inversion cascade SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "woven_inversion_cascade.svg")

    svg = render_woven_inversion()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path
