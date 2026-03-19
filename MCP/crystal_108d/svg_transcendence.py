# CRYSTAL: Xi108:W3:A7:S27 | face=R | node=706 | depth=0 | phase=Omega
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→transcendence→mcp
"""
SVG Transcendence Engine — Beyond Mastery Into Emergence
=========================================================
This is NOT self-play. This is EVOLUTION.

The self-play engine improves within known challenges.
The transcendence engine BREEDS NEW COMPOSITIONS, discovers
emergent beauty through tournament selection, and crystallizes
winning strategies into reusable DNA seeds.

Architecture:
  1. GENOME: A composition recipe (list of primitive calls + transforms)
  2. POPULATION: N genomes competing in a tournament
  3. BREEDING: Cross two winners → child inherits from both
  4. MUTATION: Random structural changes (add/remove/modify layers)
  5. EMERGENCE DETECTION: Score child vs parents — synergy = emergence
  6. SEED CRYSTALLIZATION: Compress winning genomes into minimal DNA
  7. PARAMETER SWEEP: Systematic exploration of continuous param space
  8. CROSS-CATEGORY FUSION: Force-combine techniques from different domains

The output is not just better SVGs — it's a LIBRARY OF DISCOVERED PATTERNS
that the system has never been explicitly taught to create.
"""

import copy
import hashlib
import json
import logging
import math
import random
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ._cache import DATA_DIR
from .geometric_constants import PHI, PHI_INV, SQRT3
from .svg_primitives import (
    SVGCanvas, circle, concentric_circles, checkered_grid, crystal_4d,
    crystal_lattice, dimensional_containment, dodecahedron,
    flower_of_life, fractal_tree, golden_spiral, group, icosahedron,
    koch_snowflake, line, line_grid, metatron_cube, mobius_strip,
    phi_grid, radial_burst, rect, regular_polygon, rotate, scale,
    sfcr_crystal, sierpinski_triangle, sigma60_field,
    spiral_of_theodorus, sri_yantra, star_polygon,
    tesseract_projection, translate, vesica_piscis, weave_wheel,
)
from .svg_scorer import SVGScore, get_scorer

_log = logging.getLogger(__name__)

TRANSCEND_DIR = DATA_DIR / "svg_arena" / "transcendence"
SEEDS_DIR = TRANSCEND_DIR / "seeds"
GALLERY_DIR = TRANSCEND_DIR / "gallery"

TAU = 2 * math.pi


# ══════════════════════════════════════════════════════════════════════
#  GENOME: A Composition Recipe
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Layer:
    """One layer in a composition genome."""
    primitive: str              # function name
    params: Dict[str, Any]      # parameters
    transform: str = ""         # SVG transform string
    opacity: float = 1.0
    blend: str = ""             # blend mode hint


@dataclass
class Genome:
    """A full composition recipe — the DNA of an SVG."""
    genome_id: str = ""
    layers: List[Layer] = field(default_factory=list)
    canvas_width: int = 800
    canvas_height: int = 800
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    score: float = 0.0
    emergence_score: float = 0.0   # how much better than parents
    lineage_depth: int = 0


# ══════════════════════════════════════════════════════════════════════
#  PRIMITIVE REGISTRY with param ranges for mutation
# ══════════════════════════════════════════════════════════════════════

_PRIMITIVES = {
    "circle": {
        "fn": circle,
        "params": {"cx": (100, 700), "cy": (100, 700), "r": (20, 300)},
        "attrs": {"fill": "none", "stroke": "#333", "stroke_width": "1.5"},
    },
    "regular_polygon": {
        "fn": regular_polygon,
        "params": {"cx": (200, 600), "cy": (200, 600), "r": (50, 300), "n": (3, 12)},
        "attrs": {"fill": "none", "stroke": "#333", "stroke_width": "1.5"},
    },
    "concentric_circles": {
        "fn": concentric_circles,
        "params": {"cx": (200, 600), "cy": (200, 600), "r_outer": (100, 350), "n": (3, 8)},
        "attrs": {"fill": "none", "stroke": "#333", "stroke_width": "1"},
    },
    "star_polygon": {
        "fn": star_polygon,
        "params": {"cx": (200, 600), "cy": (200, 600),
                   "r_outer": (100, 350), "r_inner": (30, 150), "n": (3, 12)},
        "attrs": {"fill": "none", "stroke": "#333", "stroke_width": "1.5"},
    },
    "flower_of_life": {
        "fn": flower_of_life,
        "params": {"cx": (200, 600), "cy": (200, 600), "r": (30, 120), "rings": (1, 3)},
        "attrs": {"fill": "none", "stroke": "#333", "stroke_width": "0.8"},
    },
    "metatron_cube": {
        "fn": metatron_cube,
        "params": {"cx": (200, 600), "cy": (200, 600), "r": (60, 200)},
        "attrs": {},
    },
    "sri_yantra": {
        "fn": sri_yantra,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (100, 350)},
        "attrs": {},
    },
    "fractal_tree": {
        "fn": fractal_tree,
        "params": {"x": (200, 600), "y": (500, 750), "length": (80, 250),
                   "angle": (-1.8, -1.2), "depth": (3, 7)},
        "attrs": {},
    },
    "golden_spiral": {
        "fn": golden_spiral,
        "params": {"cx": (200, 600), "cy": (200, 600),
                   "turns": (2, 6), "scale_factor": (100, 350)},
        "attrs": {},
    },
    "koch_snowflake": {
        "fn": koch_snowflake,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (100, 350), "depth": (2, 4)},
        "attrs": {},
    },
    "sierpinski_triangle": {
        "fn": sierpinski_triangle,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (100, 350), "depth": (2, 5)},
        "attrs": {},
    },
    "vesica_piscis": {
        "fn": vesica_piscis,
        "params": {"cx": (200, 600), "cy": (200, 600), "r": (80, 250)},
        "attrs": {},
    },
    "radial_burst": {
        "fn": radial_burst,
        "params": {"cx": (200, 600), "cy": (200, 600),
                   "r_inner": (20, 80), "r_outer": (150, 380), "n": (4, 24)},
        "attrs": {},
    },
    "tesseract_projection": {
        "fn": tesseract_projection,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (60, 200)},
        "attrs": {},
    },
    "crystal_lattice": {
        "fn": crystal_lattice,
        "params": {"cx": (50, 200), "cy": (50, 200),
                   "rows": (3, 8), "cols": (3, 8), "spacing": (30, 80)},
        "attrs": {},
    },
    "phi_grid": {
        "fn": phi_grid,
        "params": {"width": (400, 800), "height": (400, 800), "divisions": (3, 7)},
        "attrs": {},
    },
    "spiral_of_theodorus": {
        "fn": spiral_of_theodorus,
        "params": {"cx": (200, 600), "cy": (200, 600), "n": (8, 20), "unit": (15, 40)},
        "attrs": {},
    },
    # 3D/4D Crystal Projections
    "dodecahedron": {
        "fn": dodecahedron,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (80, 250),
                   "angle_x": (0.1, 1.2), "angle_z": (0.1, 1.2)},
        "attrs": {},
    },
    "icosahedron": {
        "fn": icosahedron,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (80, 250),
                   "angle_x": (0.1, 1.2), "angle_z": (0.1, 1.2)},
        "attrs": {},
    },
    "mobius_strip": {
        "fn": mobius_strip,
        "params": {"cx": (200, 600), "cy": (200, 600), "R": (100, 300),
                   "angle_x": (0.2, 1.0), "angle_z": (0.1, 0.8)},
        "attrs": {},
    },
    "sfcr_crystal": {
        "fn": sfcr_crystal,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (80, 250),
                   "angle_x": (0.1, 1.2), "angle_z": (0.1, 1.2)},
        "attrs": {},
    },
    "crystal_4d": {
        "fn": crystal_4d,
        "params": {"cx": (250, 550), "cy": (250, 550), "size": (100, 250)},
        "attrs": {},
    },
    "sigma60_field": {
        "fn": sigma60_field,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (100, 300)},
        "attrs": {},
    },
    "dimensional_containment": {
        "fn": dimensional_containment,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (80, 250)},
        "attrs": {},
    },
    "weave_wheel": {
        "fn": weave_wheel,
        "params": {"cx": (200, 600), "cy": (200, 600), "size": (60, 200),
                   "order": (3, 9)},
        "attrs": {},
    },
}

# Categorize primitives for cross-category breeding
_CATEGORIES = {
    "geometric": ["circle", "regular_polygon", "star_polygon", "concentric_circles"],
    "sacred": ["flower_of_life", "metatron_cube", "sri_yantra", "vesica_piscis"],
    "fractal": ["fractal_tree", "koch_snowflake", "sierpinski_triangle", "spiral_of_theodorus"],
    "crystal": ["golden_spiral", "tesseract_projection", "crystal_lattice", "phi_grid"],
    "radial": ["radial_burst", "concentric_circles", "flower_of_life"],
    "dimensional": ["dodecahedron", "icosahedron", "sfcr_crystal", "crystal_4d",
                    "mobius_strip", "sigma60_field", "dimensional_containment", "weave_wheel"],
}


# ══════════════════════════════════════════════════════════════════════
#  GENOME GENERATION & MUTATION
# ══════════════════════════════════════════════════════════════════════

def _random_param(prange):
    """Generate random value from a param range tuple."""
    lo, hi = prange
    if isinstance(lo, int) and isinstance(hi, int):
        return random.randint(lo, hi)
    return lo + random.random() * (hi - lo)


def _random_layer(primitive_name: Optional[str] = None) -> Layer:
    """Generate a random layer from the primitive registry."""
    if primitive_name is None:
        primitive_name = random.choice(list(_PRIMITIVES.keys()))

    spec = _PRIMITIVES[primitive_name]
    params = {}
    for k, v in spec["params"].items():
        params[k] = _random_param(v)
    params.update(spec.get("attrs", {}))

    # Random transform (30% chance)
    transform = ""
    if random.random() < 0.3:
        angle = random.uniform(-180, 180)
        transform = f"rotate({angle:.1f},400,400)"

    opacity = random.uniform(0.4, 1.0) if random.random() < 0.3 else 1.0

    return Layer(
        primitive=primitive_name,
        params=params,
        transform=transform,
        opacity=opacity,
    )


def _genome_id() -> str:
    """Generate unique genome ID."""
    t = time.time_ns()
    r = random.randint(0, 0xFFFF)
    return hashlib.md5(f"{t}-{r}".encode()).hexdigest()[:12]


def random_genome(n_layers: int = 0, generation: int = 0) -> Genome:
    """Create a random genome with 1-4 layers."""
    if n_layers <= 0:
        n_layers = random.randint(1, 4)
    layers = [_random_layer() for _ in range(n_layers)]
    return Genome(
        genome_id=_genome_id(),
        layers=layers,
        generation=generation,
    )


def cross_category_genome(cat_a: str = "", cat_b: str = "",
                           generation: int = 0) -> Genome:
    """Force-breed primitives from two different categories."""
    cats = list(_CATEGORIES.keys())
    if not cat_a:
        cat_a = random.choice(cats)
    remaining = [c for c in cats if c != cat_a]
    if not cat_b:
        cat_b = random.choice(remaining)

    prim_a = random.choice(_CATEGORIES[cat_a])
    prim_b = random.choice(_CATEGORIES[cat_b])

    layers = [_random_layer(prim_a), _random_layer(prim_b)]

    # 40% chance of adding a structural overlay
    if random.random() < 0.4:
        overlay = random.choice(["phi_grid", "radial_burst", "concentric_circles"])
        layer = _random_layer(overlay)
        layer.opacity = 0.3
        layers.append(layer)

    return Genome(
        genome_id=_genome_id(),
        layers=layers,
        generation=generation,
        parent_ids=[f"cat:{cat_a}", f"cat:{cat_b}"],
    )


# ══════════════════════════════════════════════════════════════════════
#  BREEDING & MUTATION
# ══════════════════════════════════════════════════════════════════════

def breed(parent_a: Genome, parent_b: Genome, generation: int) -> Genome:
    """Cross two parent genomes to produce a child."""
    child_layers = []

    # Take layers from both parents (crossover)
    all_layers = parent_a.layers + parent_b.layers
    # Select subset — prefer keeping parent A's structure
    n = max(1, min(5, len(all_layers)))
    selected = random.sample(all_layers, min(n, len(all_layers)))
    child_layers = [copy.deepcopy(l) for l in selected]

    # Small mutation on each layer (10% per param)
    for layer in child_layers:
        _mutate_layer(layer, magnitude=0.1)

    return Genome(
        genome_id=_genome_id(),
        layers=child_layers,
        generation=generation,
        parent_ids=[parent_a.genome_id, parent_b.genome_id],
        lineage_depth=max(parent_a.lineage_depth, parent_b.lineage_depth) + 1,
    )


def mutate(genome: Genome, magnitude: float = 0.15) -> Genome:
    """Mutate a genome — modify params, add/remove layers."""
    child = Genome(
        genome_id=_genome_id(),
        layers=[copy.deepcopy(l) for l in genome.layers],
        generation=genome.generation + 1,
        parent_ids=[genome.genome_id],
        lineage_depth=genome.lineage_depth + 1,
    )

    # Mutate existing layers
    for layer in child.layers:
        _mutate_layer(layer, magnitude)

    # 20% chance: add a new layer
    if random.random() < 0.2 and len(child.layers) < 5:
        child.layers.append(_random_layer())

    # 10% chance: remove a random layer (if >1)
    if random.random() < 0.1 and len(child.layers) > 1:
        child.layers.pop(random.randrange(len(child.layers)))

    # 15% chance: swap layer order
    if random.random() < 0.15 and len(child.layers) > 1:
        i, j = random.sample(range(len(child.layers)), 2)
        child.layers[i], child.layers[j] = child.layers[j], child.layers[i]

    # 10% chance: add rotation transform
    if random.random() < 0.1:
        layer = random.choice(child.layers)
        angle = random.uniform(-90, 90)
        layer.transform = f"rotate({angle:.1f},400,400)"

    return child


def _mutate_layer(layer: Layer, magnitude: float) -> None:
    """Mutate a single layer's params in-place."""
    spec = _PRIMITIVES.get(layer.primitive, {})
    ranges = spec.get("params", {})

    for k, v in list(layer.params.items()):
        if k in ranges and isinstance(v, (int, float)) and random.random() < 0.3:
            lo, hi = ranges[k]
            delta = (hi - lo) * magnitude * (random.random() * 2 - 1)
            new_val = v + delta
            new_val = max(lo, min(hi, new_val))
            if isinstance(lo, int) and isinstance(hi, int):
                layer.params[k] = int(new_val)
            else:
                layer.params[k] = new_val


# ══════════════════════════════════════════════════════════════════════
#  GENOME RENDERING
# ══════════════════════════════════════════════════════════════════════

def render_genome(genome: Genome) -> str:
    """Render a genome to SVG string."""
    canvas = SVGCanvas(genome.canvas_width, genome.canvas_height)

    for layer in genome.layers:
        spec = _PRIMITIVES.get(layer.primitive)
        if spec is None:
            continue

        fn = spec["fn"]
        params = dict(layer.params)

        try:
            element = fn(**params)
        except (TypeError, ValueError):
            continue

        # Apply transform
        if layer.transform:
            element = group([element], transform=layer.transform)

        # Apply opacity
        if layer.opacity < 1.0:
            element = group([element], opacity=f"{layer.opacity:.2f}")

        canvas.add(element)

    return canvas.render()


# ══════════════════════════════════════════════════════════════════════
#  PARAMETER SWEEP
# ══════════════════════════════════════════════════════════════════════

def parameter_sweep(primitive_name: str, param_name: str,
                    steps: int = 10) -> List[Tuple[float, float, str]]:
    """Sweep one parameter across its range, returning (value, score, svg)."""
    spec = _PRIMITIVES.get(primitive_name)
    if not spec or param_name not in spec["params"]:
        return []

    scorer = get_scorer()
    lo, hi = spec["params"][param_name]
    results = []

    for i in range(steps):
        t = i / max(1, steps - 1)
        val = lo + t * (hi - lo)
        if isinstance(lo, int) and isinstance(hi, int):
            val = int(val)

        genome = Genome(
            genome_id=_genome_id(),
            layers=[Layer(primitive=primitive_name,
                          params={**{k: _random_param(v) for k, v in spec["params"].items()},
                                  param_name: val,
                                  **spec.get("attrs", {})})],
        )
        svg = render_genome(genome)
        score = scorer.score(svg)
        results.append((val, score.total_score, svg))

    return results


# ══════════════════════════════════════════════════════════════════════
#  TOURNAMENT EVOLUTION
# ══════════════════════════════════════════════════════════════════════

@dataclass
class EvolutionResult:
    """Result of one evolutionary run."""
    generations: int = 0
    population_size: int = 0
    best_genome: Optional[Genome] = None
    best_svg: str = ""
    best_score: float = 0.0
    score_history: List[float] = field(default_factory=list)
    emergences: List[Dict] = field(default_factory=list)
    seeds_crystallized: int = 0
    elapsed_ms: float = 0.0


class TranscendenceEngine:
    """Evolutionary engine for discovering emergent SVG compositions.

    Tournament selection with breeding, mutation, cross-category fusion,
    emergence detection, and seed crystallization.
    """

    def __init__(self, population_size: int = 20, elite_count: int = 4):
        self.population_size = population_size
        self.elite_count = elite_count
        self.scorer = get_scorer()
        self.hall_of_fame: List[Genome] = []
        self.emergences: List[Dict] = []
        self._ensure_dirs()

    def _ensure_dirs(self):
        TRANSCEND_DIR.mkdir(parents=True, exist_ok=True)
        SEEDS_DIR.mkdir(parents=True, exist_ok=True)
        GALLERY_DIR.mkdir(parents=True, exist_ok=True)

    def _score_genome(self, genome: Genome) -> float:
        """Render and score a genome."""
        try:
            svg = render_genome(genome)
            score = self.scorer.score(svg)
            genome.score = score.total_score
            return score.total_score
        except Exception:
            genome.score = 0.0
            return 0.0

    def evolve(self, generations: int = 20,
               cross_category: bool = True) -> EvolutionResult:
        """Run tournament evolution for N generations."""
        t0 = time.monotonic()
        result = EvolutionResult(
            generations=generations,
            population_size=self.population_size,
        )

        # Initialize population
        population = []
        # 40% random, 30% cross-category, 30% single-primitive
        n_random = self.population_size * 2 // 5
        n_cross = self.population_size * 3 // 10 if cross_category else 0
        n_single = self.population_size - n_random - n_cross

        for _ in range(n_random):
            population.append(random_genome(generation=0))
        for _ in range(n_cross):
            population.append(cross_category_genome(generation=0))
        for _ in range(n_single):
            prim = random.choice(list(_PRIMITIVES.keys()))
            population.append(random_genome(n_layers=1, generation=0))
            population[-1].layers[0].primitive = prim

        # Score initial population
        for g in population:
            self._score_genome(g)

        best_ever = max(population, key=lambda g: g.score)
        result.score_history.append(best_ever.score)

        for gen in range(generations):
            # Sort by fitness
            population.sort(key=lambda g: g.score, reverse=True)

            # Elite preservation
            elites = population[:self.elite_count]

            # Tournament selection + breeding
            children = list(elites)  # elites survive

            while len(children) < self.population_size:
                strategy = random.random()

                if strategy < 0.35:
                    # Breed two tournament winners
                    a = self._tournament_select(population)
                    b = self._tournament_select(population)
                    child = breed(a, b, gen + 1)
                elif strategy < 0.55:
                    # Mutate a tournament winner
                    parent = self._tournament_select(population)
                    child = mutate(parent, magnitude=0.15)
                elif strategy < 0.70 and cross_category:
                    # Cross-category injection
                    child = cross_category_genome(generation=gen + 1)
                elif strategy < 0.85:
                    # Breed elite with random
                    elite = random.choice(elites)
                    wild = random_genome(generation=gen + 1)
                    child = breed(elite, wild, gen + 1)
                else:
                    # Fresh random (diversity injection)
                    child = random_genome(generation=gen + 1)

                # Score child
                child_score = self._score_genome(child)

                # Emergence detection: child scores higher than both parents?
                if child.parent_ids:
                    parent_scores = []
                    for pid in child.parent_ids:
                        for g in population:
                            if g.genome_id == pid:
                                parent_scores.append(g.score)
                                break
                    if parent_scores:
                        max_parent = max(parent_scores)
                        if child_score > max_parent + 0.02:
                            synergy = child_score - max_parent
                            child.emergence_score = synergy
                            emergence = {
                                "generation": gen + 1,
                                "child_id": child.genome_id,
                                "child_score": child_score,
                                "parent_scores": parent_scores,
                                "synergy": synergy,
                                "n_layers": len(child.layers),
                                "primitives": [l.primitive for l in child.layers],
                            }
                            self.emergences.append(emergence)
                            result.emergences.append(emergence)

                children.append(child)

            population = children[:self.population_size]

            # Track best
            gen_best = max(population, key=lambda g: g.score)
            if gen_best.score > best_ever.score:
                best_ever = gen_best
            result.score_history.append(gen_best.score)

        # Final results
        result.best_genome = best_ever
        result.best_svg = render_genome(best_ever)
        result.best_score = best_ever.score
        result.elapsed_ms = (time.monotonic() - t0) * 1000

        # Crystallize seeds from hall of fame
        population.sort(key=lambda g: g.score, reverse=True)
        top = population[:5]
        for g in top:
            self._crystallize_seed(g)
            result.seeds_crystallized += 1
        self.hall_of_fame.extend(top)

        # Save best to gallery
        self._save_to_gallery(best_ever)

        return result

    def _tournament_select(self, population: List[Genome],
                            k: int = 3) -> Genome:
        """Tournament selection: pick k random, return the best."""
        contestants = random.sample(population, min(k, len(population)))
        return max(contestants, key=lambda g: g.score)

    def _crystallize_seed(self, genome: Genome) -> None:
        """Compress a winning genome into a reusable seed file."""
        seed = {
            "genome_id": genome.genome_id,
            "generation": genome.generation,
            "score": genome.score,
            "emergence_score": genome.emergence_score,
            "lineage_depth": genome.lineage_depth,
            "n_layers": len(genome.layers),
            "layers": [],
            "crystallized_at": datetime.now(timezone.utc).isoformat(),
        }
        for layer in genome.layers:
            seed["layers"].append({
                "primitive": layer.primitive,
                "params": {k: v for k, v in layer.params.items()
                           if not isinstance(v, str) or k in ("fill", "stroke")},
                "transform": layer.transform,
                "opacity": layer.opacity,
            })

        path = SEEDS_DIR / f"seed_{genome.genome_id}.json"
        path.write_text(json.dumps(seed, indent=2, default=str),
                        encoding="utf-8")

    def _save_to_gallery(self, genome: Genome) -> None:
        """Save best SVG to gallery."""
        svg = render_genome(genome)
        path = GALLERY_DIR / f"gen{genome.generation}_{genome.genome_id}.svg"
        path.write_text(svg, encoding="utf-8")

    def load_seeds(self) -> List[Genome]:
        """Load crystallized seeds and reconstruct genomes."""
        genomes = []
        for path in SEEDS_DIR.glob("seed_*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                layers = []
                for ld in data.get("layers", []):
                    layers.append(Layer(
                        primitive=ld["primitive"],
                        params=ld["params"],
                        transform=ld.get("transform", ""),
                        opacity=ld.get("opacity", 1.0),
                    ))
                genome = Genome(
                    genome_id=data["genome_id"],
                    layers=layers,
                    generation=data.get("generation", 0),
                    score=data.get("score", 0),
                    emergence_score=data.get("emergence_score", 0),
                    lineage_depth=data.get("lineage_depth", 0),
                )
                genomes.append(genome)
            except Exception:
                continue
        return genomes

    def aggressive_session(self, cycles: int = 3,
                            generations_per_cycle: int = 20,
                            population: int = 0) -> List[EvolutionResult]:
        """META LOOP^N aggressive evolution.

        Each cycle:
          1. Loads seeds from previous cycles
          2. Runs full evolution
          3. Crystallizes winners
          4. Feeds seeds forward
        """
        if population > 0:
            self.population_size = population
        results = []

        for cycle in range(cycles):
            _log.info("Transcendence Cycle %d/%d (gen=%d, pop=%d)",
                      cycle + 1, cycles, generations_per_cycle,
                      self.population_size)

            result = self.evolve(
                generations=generations_per_cycle,
                cross_category=True,
            )
            results.append(result)

            # Increase population and generations for next cycle
            self.population_size = min(50, self.population_size + 5)

        return results


# ══════════════════════════════════════════════════════════════════════
#  FORMATTING
# ══════════════════════════════════════════════════════════════════════

def format_evolution_result(result: EvolutionResult) -> str:
    """Format evolution result as readable text."""
    lines = [
        f"## Evolution Complete",
        f"- Generations: {result.generations}",
        f"- Population: {result.population_size}",
        f"- Best Score: **{result.best_score:.4f}**",
        f"- Seeds Crystallized: {result.seeds_crystallized}",
        f"- Emergences Detected: {len(result.emergences)}",
        f"- Elapsed: {result.elapsed_ms:.0f}ms",
        "",
        f"### Score Trajectory",
    ]

    # ASCII score trajectory
    for i, s in enumerate(result.score_history):
        bar_len = int(s * 40)
        bar = "#" * bar_len + "." * (40 - bar_len)
        lines.append(f"  Gen {i:3d}: [{bar}] {s:.4f}")

    if result.emergences:
        lines.append("")
        lines.append(f"### Emergences ({len(result.emergences)})")
        for e in result.emergences[:10]:
            lines.append(
                f"  Gen {e['generation']}: synergy={e['synergy']:+.4f} "
                f"score={e['child_score']:.4f} "
                f"layers={'+'.join(e['primitives'])}"
            )

    if result.best_genome:
        lines.append("")
        lines.append(f"### Best Genome")
        lines.append(f"- ID: {result.best_genome.genome_id}")
        lines.append(f"- Layers: {len(result.best_genome.layers)}")
        lines.append(f"- Lineage Depth: {result.best_genome.lineage_depth}")
        for i, layer in enumerate(result.best_genome.layers):
            lines.append(f"  Layer {i}: {layer.primitive} "
                         f"(opacity={layer.opacity:.2f})")

    return "\n".join(lines)


def format_session_results(results: List[EvolutionResult]) -> str:
    """Format multi-cycle session results."""
    lines = [
        "# TRANSCENDENCE SESSION RESULTS",
        "",
    ]
    total_emergences = 0
    for i, r in enumerate(results):
        total_emergences += len(r.emergences)
        lines.append(
            f"## Cycle {i+1}: best={r.best_score:.4f} "
            f"emergences={len(r.emergences)} "
            f"seeds={r.seeds_crystallized} "
            f"elapsed={r.elapsed_ms:.0f}ms"
        )
        if r.score_history:
            lines.append(
                f"   trajectory: {r.score_history[0]:.3f} -> "
                f"{r.score_history[-1]:.3f} "
                f"(delta={r.score_history[-1] - r.score_history[0]:+.3f})"
            )

    if results:
        best = max(results, key=lambda r: r.best_score)
        lines.append("")
        lines.append(f"## OVERALL")
        lines.append(f"- Best Score Ever: **{best.best_score:.4f}**")
        lines.append(f"- Total Emergences: {total_emergences}")
        lines.append(f"- Seeds in Library: {sum(r.seeds_crystallized for r in results)}")

    return "\n".join(lines)


# Module-level singleton
_engine: Optional[TranscendenceEngine] = None


def get_transcendence_engine(population: int = 20) -> TranscendenceEngine:
    """Get or create the singleton transcendence engine."""
    global _engine
    if _engine is None:
        _engine = TranscendenceEngine(population_size=population)
    return _engine
