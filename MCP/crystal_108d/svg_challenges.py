# CRYSTAL: Xi108:W3:A7:S23 | face=R | node=702 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→mcp
"""
SVG Challenges — Catalog of Visual Generation Targets
======================================================
25 built-in challenges across 5 categories of increasing difficulty:
  1. Primitive  (0.1-0.3) — single shapes, grids
  2. Composite  (0.3-0.5) — layered patterns, stars
  3. Sacred     (0.5-0.7) — flower of life, Metatron, Vesica Piscis
  4. Fractal    (0.7-0.9) — trees, snowflakes, Sierpinski
  5. Crystal    (0.8-1.0) — tesseract, lattice, phi grid

Each challenge defines a reference function + params so the self-play
engine knows what "correct" looks like.
"""

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ._cache import DATA_DIR


# ══════════════════════════════════════════════════════════════════════
#  SVGChallenge Dataclass
# ══════════════════════════════════════════════════════════════════════

@dataclass
class SVGChallenge:
    """A visual generation target for the self-play engine."""
    challenge_id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""                # primitive|composite|sacred|fractal|crystal
    difficulty: float = 0.5           # 0.0-1.0
    target_elements: int = 0          # expected element count
    target_symmetry: int = 0          # expected symmetry order
    target_golden: bool = False       # should golden ratio appear?
    reference_fn: str = ""            # function name in svg_primitives
    reference_params: Dict = field(default_factory=dict)
    canvas_width: int = 800
    canvas_height: int = 800


# ══════════════════════════════════════════════════════════════════════
#  Built-in Challenge Catalog
# ══════════════════════════════════════════════════════════════════════

def _build_catalog() -> List[SVGChallenge]:
    """Create the 25 built-in challenges."""
    C = SVGChallenge
    challenges = []

    # ── PRIMITIVE (5 challenges, difficulty 0.1-0.3) ──────────────

    challenges.append(C(
        challenge_id="prim_circle",
        name="Single Circle",
        description="A single circle centered on the canvas",
        category="primitive", difficulty=0.1,
        target_elements=1, target_symmetry=0, target_golden=False,
        reference_fn="circle",
        reference_params={"cx": 400, "cy": 400, "r": 200,
                          "fill": "none", "stroke": "#333", "stroke_width": "2"},
    ))

    challenges.append(C(
        challenge_id="prim_rect",
        name="Centered Rectangle",
        description="A rectangle centered on canvas with golden ratio proportions",
        category="primitive", difficulty=0.15,
        target_elements=1, target_symmetry=2, target_golden=True,
        reference_fn="rect",
        reference_params={"x": 152, "y": 248, "w": 496, "h": 304,
                          "fill": "none", "stroke": "#333", "stroke_width": "2"},
    ))

    challenges.append(C(
        challenge_id="prim_hexagon",
        name="Regular Hexagon",
        description="A regular hexagon centered on the canvas",
        category="primitive", difficulty=0.2,
        target_elements=1, target_symmetry=6, target_golden=False,
        reference_fn="regular_polygon",
        reference_params={"cx": 400, "cy": 400, "r": 250, "n": 6,
                          "fill": "none", "stroke": "#333", "stroke_width": "2"},
    ))

    challenges.append(C(
        challenge_id="prim_line_grid",
        name="Line Grid",
        description="A regular grid of horizontal and vertical lines",
        category="primitive", difficulty=0.25,
        target_elements=40, target_symmetry=4, target_golden=False,
        reference_fn="line_grid",
        reference_params={"x": 50, "y": 50, "width": 700, "height": 700,
                          "spacing": 35},
    ))

    challenges.append(C(
        challenge_id="prim_pentagon",
        name="Regular Pentagon",
        description="A regular pentagon — the golden ratio polygon",
        category="primitive", difficulty=0.2,
        target_elements=1, target_symmetry=5, target_golden=True,
        reference_fn="regular_polygon",
        reference_params={"cx": 400, "cy": 400, "r": 250, "n": 5,
                          "fill": "none", "stroke": "#333", "stroke_width": "2"},
    ))

    # ── COMPOSITE (5 challenges, difficulty 0.3-0.5) ─────────────

    challenges.append(C(
        challenge_id="comp_concentric",
        name="Concentric Circles",
        description="5 concentric circles with phi-decaying radii",
        category="composite", difficulty=0.3,
        target_elements=5, target_symmetry=0, target_golden=True,
        reference_fn="concentric_circles",
        reference_params={"cx": 400, "cy": 400, "r_outer": 300, "n": 5,
                          "fill": "none", "stroke": "#333", "stroke_width": "1.5"},
    ))

    challenges.append(C(
        challenge_id="comp_star5",
        name="Five-Pointed Star",
        description="A classic 5-pointed star with golden ratio inner/outer radii",
        category="composite", difficulty=0.35,
        target_elements=1, target_symmetry=5, target_golden=True,
        reference_fn="star_polygon",
        reference_params={"cx": 400, "cy": 400, "r_outer": 300,
                          "r_inner": 115, "n": 5,
                          "fill": "none", "stroke": "#333", "stroke_width": "2"},
    ))

    challenges.append(C(
        challenge_id="comp_radial",
        name="Radial Burst",
        description="12 lines radiating from center (clock-like)",
        category="composite", difficulty=0.35,
        target_elements=12, target_symmetry=12, target_golden=False,
        reference_fn="radial_burst",
        reference_params={"cx": 400, "cy": 400, "r_inner": 50,
                          "r_outer": 350, "n": 12},
    ))

    challenges.append(C(
        challenge_id="comp_checker",
        name="Checkered Grid",
        description="An 8x8 checkered pattern like a chess board",
        category="composite", difficulty=0.4,
        target_elements=64, target_symmetry=4, target_golden=False,
        reference_fn="checkered_grid",
        reference_params={"x": 100, "y": 100, "rows": 8, "cols": 8,
                          "cell_size": 75},
    ))

    challenges.append(C(
        challenge_id="comp_star8",
        name="Eight-Pointed Star",
        description="An 8-pointed star with octagonal symmetry",
        category="composite", difficulty=0.45,
        target_elements=1, target_symmetry=8, target_golden=False,
        reference_fn="star_polygon",
        reference_params={"cx": 400, "cy": 400, "r_outer": 300,
                          "r_inner": 140, "n": 8,
                          "fill": "none", "stroke": "#333", "stroke_width": "2"},
    ))

    # ── SACRED (5 challenges, difficulty 0.5-0.7) ────────────────

    challenges.append(C(
        challenge_id="sacred_vesica",
        name="Vesica Piscis",
        description="Two overlapping circles forming the vesica piscis",
        category="sacred", difficulty=0.5,
        target_elements=2, target_symmetry=2, target_golden=False,
        reference_fn="vesica_piscis",
        reference_params={"cx": 400, "cy": 400, "r": 200},
    ))

    challenges.append(C(
        challenge_id="sacred_flower2",
        name="Flower of Life (2 rings)",
        description="Flower of life with 2 rings of overlapping circles",
        category="sacred", difficulty=0.55,
        target_elements=19, target_symmetry=6, target_golden=False,
        reference_fn="flower_of_life",
        reference_params={"cx": 400, "cy": 400, "r": 80, "rings": 2},
    ))

    challenges.append(C(
        challenge_id="sacred_flower3",
        name="Flower of Life (3 rings)",
        description="Flower of life with 3 rings — the classic sacred geometry pattern",
        category="sacred", difficulty=0.6,
        target_elements=37, target_symmetry=6, target_golden=False,
        reference_fn="flower_of_life",
        reference_params={"cx": 400, "cy": 400, "r": 60, "rings": 3},
    ))

    challenges.append(C(
        challenge_id="sacred_metatron",
        name="Metatron's Cube",
        description="13 circles with all connecting lines — the template of creation",
        category="sacred", difficulty=0.65,
        target_elements=91, target_symmetry=6, target_golden=False,
        reference_fn="metatron_cube",
        reference_params={"cx": 400, "cy": 400, "r": 150},
    ))

    challenges.append(C(
        challenge_id="sacred_sri",
        name="Sri Yantra",
        description="9 interlocking triangles (4 up, 5 down)",
        category="sacred", difficulty=0.7,
        target_elements=9, target_symmetry=3, target_golden=False,
        reference_fn="sri_yantra",
        reference_params={"cx": 400, "cy": 400, "size": 300},
    ))

    # ── FRACTAL (5 challenges, difficulty 0.7-0.9) ───────────────

    challenges.append(C(
        challenge_id="frac_tree5",
        name="Fractal Tree (depth 5)",
        description="Recursive branching tree with golden ratio decay",
        category="fractal", difficulty=0.7,
        target_elements=63, target_symmetry=2, target_golden=True,
        reference_fn="fractal_tree",
        reference_params={"x": 400, "y": 750, "length": 200,
                          "angle": -1.5708, "depth": 5},
    ))

    challenges.append(C(
        challenge_id="frac_theodorus",
        name="Spiral of Theodorus",
        description="Square root spiral from right triangles",
        category="fractal", difficulty=0.75,
        target_elements=17, target_symmetry=0, target_golden=False,
        reference_fn="spiral_of_theodorus",
        reference_params={"cx": 400, "cy": 400, "n": 17, "unit": 25},
    ))

    challenges.append(C(
        challenge_id="frac_koch3",
        name="Koch Snowflake (depth 3)",
        description="Fractal snowflake with 3 levels of recursion",
        category="fractal", difficulty=0.8,
        target_elements=1, target_symmetry=3, target_golden=False,
        reference_fn="koch_snowflake",
        reference_params={"cx": 400, "cy": 400, "size": 300, "depth": 3},
    ))

    challenges.append(C(
        challenge_id="frac_sierpinski4",
        name="Sierpinski Triangle (depth 4)",
        description="Fractal triangle subdivision, 4 levels deep",
        category="fractal", difficulty=0.85,
        target_elements=81, target_symmetry=3, target_golden=False,
        reference_fn="sierpinski_triangle",
        reference_params={"cx": 400, "cy": 400, "size": 350, "depth": 4},
    ))

    challenges.append(C(
        challenge_id="frac_tree7",
        name="Fractal Tree (depth 7)",
        description="Deep fractal tree with 7 levels of golden ratio branching",
        category="fractal", difficulty=0.9,
        target_elements=255, target_symmetry=2, target_golden=True,
        reference_fn="fractal_tree",
        reference_params={"x": 400, "y": 750, "length": 180,
                          "angle": -1.5708, "depth": 7},
    ))

    # ── CRYSTAL (5 challenges, difficulty 0.8-1.0) ───────────────

    challenges.append(C(
        challenge_id="cryst_tesseract",
        name="Tesseract Projection",
        description="4D hypercube projected to 2D — 16 vertices, 32 edges",
        category="crystal", difficulty=0.8,
        target_elements=32, target_symmetry=4, target_golden=True,
        reference_fn="tesseract_projection",
        reference_params={"cx": 400, "cy": 400, "size": 150},
    ))

    challenges.append(C(
        challenge_id="cryst_hex_lattice",
        name="Hexagonal Crystal Lattice",
        description="7x7 hexagonal lattice — the structure of graphene",
        category="crystal", difficulty=0.85,
        target_elements=49, target_symmetry=6, target_golden=False,
        reference_fn="crystal_lattice",
        reference_params={"cx": 150, "cy": 100, "rows": 7, "cols": 7,
                          "spacing": 80, "lattice_type": "hex"},
    ))

    challenges.append(C(
        challenge_id="cryst_phi_grid",
        name="Golden Ratio Grid",
        description="Recursive golden ratio subdivision of the canvas",
        category="crystal", difficulty=0.85,
        target_elements=10, target_symmetry=0, target_golden=True,
        reference_fn="phi_grid",
        reference_params={"width": 800, "height": 800, "divisions": 5},
    ))

    challenges.append(C(
        challenge_id="cryst_golden_spiral",
        name="Golden Spiral",
        description="Fibonacci spiral via quarter-circle arcs",
        category="crystal", difficulty=0.9,
        target_elements=1, target_symmetry=0, target_golden=True,
        reference_fn="golden_spiral",
        reference_params={"cx": 400, "cy": 400, "turns": 5, "scale_factor": 300},
    ))

    challenges.append(C(
        challenge_id="cryst_full_mandala",
        name="Crystal Mandala",
        description="Flower of life + phi grid + concentric circles overlay",
        category="crystal", difficulty=1.0,
        target_elements=50, target_symmetry=6, target_golden=True,
        reference_fn="_crystal_mandala",
        reference_params={"cx": 400, "cy": 400, "size": 300},
    ))

    # ── DIMENSIONAL (8 challenges, difficulty 0.7-1.0) ─────────────
    # 3D projections, Möbius inversion, 4D crystal, weave operators

    challenges.append(C(
        challenge_id="dim_dodecahedron",
        name="Dodecahedron 12-Face",
        description="12-face Platonic solid projected to 2D — archetype structure",
        category="dimensional", difficulty=0.7,
        target_elements=50, target_symmetry=5, target_golden=True,
        reference_fn="dodecahedron",
        reference_params={"cx": 400, "cy": 400, "size": 200},
    ))

    challenges.append(C(
        challenge_id="dim_icosahedron",
        name="Icosahedron 12-Vertex",
        description="12-vertex dual of dodecahedron — archetype vertices",
        category="dimensional", difficulty=0.7,
        target_elements=42, target_symmetry=5, target_golden=True,
        reference_fn="icosahedron",
        reference_params={"cx": 400, "cy": 400, "size": 200},
    ))

    challenges.append(C(
        challenge_id="dim_sfcr_crystal",
        name="SFCR Crystal",
        description="Dodecahedron with SFCR element-colored faces",
        category="dimensional", difficulty=0.8,
        target_elements=60, target_symmetry=5, target_golden=True,
        reference_fn="sfcr_crystal",
        reference_params={"cx": 400, "cy": 400, "size": 200},
    ))

    challenges.append(C(
        challenge_id="dim_mobius",
        name="Mobius Strip",
        description="Non-orientable surface — topological inversion of the crystal",
        category="dimensional", difficulty=0.8,
        target_elements=20, target_symmetry=0, target_golden=False,
        reference_fn="mobius_strip",
        reference_params={"cx": 400, "cy": 400, "R": 250, "w": 0.25},
    ))

    challenges.append(C(
        challenge_id="dim_containment",
        name="Dimensional Containment",
        description="Nested rings: 3D to 12D weave operator hierarchy",
        category="dimensional", difficulty=0.75,
        target_elements=40, target_symmetry=12, target_golden=True,
        reference_fn="dimensional_containment",
        reference_params={"cx": 400, "cy": 400, "size": 250},
    ))

    challenges.append(C(
        challenge_id="dim_sigma60",
        name="Sigma-60 Field",
        description="12 archetypes x 5 golden rotations icosahedral observation",
        category="dimensional", difficulty=0.85,
        target_elements=80, target_symmetry=12, target_golden=True,
        reference_fn="sigma60_field",
        reference_params={"cx": 400, "cy": 400, "size": 300},
    ))

    challenges.append(C(
        challenge_id="dim_crystal_4d",
        name="Crystal 4D Full",
        description="Tesseract + Mobius wrap + containment rings — complete 4D projection",
        category="dimensional", difficulty=0.95,
        target_elements=100, target_symmetry=4, target_golden=True,
        reference_fn="crystal_4d",
        reference_params={"cx": 400, "cy": 400, "size": 200},
        canvas_width=1000, canvas_height=1000,
    ))

    challenges.append(C(
        challenge_id="dim_weave_w9",
        name="W9 Crown Wheel",
        description="Enneadic weave operator — 9-station transformation cycle",
        category="dimensional", difficulty=0.7,
        target_elements=25, target_symmetry=9, target_golden=False,
        reference_fn="weave_wheel",
        reference_params={"cx": 400, "cy": 400, "size": 200, "order": 9},
    ))

    return challenges


# Module-level catalog
_CATALOG: Optional[List[SVGChallenge]] = None


def catalog() -> List[SVGChallenge]:
    """Return the full challenge catalog."""
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = _build_catalog()
    return list(_CATALOG)


def get_challenge(challenge_id: str) -> Optional[SVGChallenge]:
    """Look up a challenge by ID."""
    for c in catalog():
        if c.challenge_id == challenge_id:
            return c
    return None


def random_challenge(category: Optional[str] = None,
                     difficulty_range: Optional[Tuple[float, float]] = None) -> SVGChallenge:
    """Pick a random challenge, optionally filtered."""
    pool = catalog()
    if category:
        pool = [c for c in pool if c.category == category]
    if difficulty_range:
        lo, hi = difficulty_range
        pool = [c for c in pool if lo <= c.difficulty <= hi]
    if not pool:
        pool = catalog()
    return random.choice(pool)


def progressive_challenges(n: int = 10) -> List[SVGChallenge]:
    """Return n challenges in increasing difficulty order."""
    sorted_cat = sorted(catalog(), key=lambda c: c.difficulty)
    if n >= len(sorted_cat):
        return sorted_cat
    # Evenly sample across difficulty range
    step = len(sorted_cat) / n
    return [sorted_cat[int(i * step)] for i in range(n)]


def save_catalog(path: Optional[Path] = None) -> None:
    """Save catalog to JSON."""
    p = path or (DATA_DIR / "svg_arena" / "challenges.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "meta": {"total_challenges": len(catalog()), "categories": 5},
        "challenges": [asdict(c) for c in catalog()],
    }
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
