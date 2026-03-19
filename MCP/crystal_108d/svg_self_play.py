# CRYSTAL: Xi108:W3:A7:S24 | face=R | node=703 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: primitives→scorer→challenges→self_play→mcp
"""
SVG Self-Play Engine — Generate, Score, Improve, Record
========================================================
The core self-play loop for SVG skill improvement:
  1. Pick a challenge (or receive one)
  2. Generate SVG using the reference function
  3. Score the output
  4. Apply improvement strategies (perturb, rebuild, simplify)
  5. Record results to sandbox metadata + hive ledger
  6. Save best SVG to disk

Integrates with the existing 15D observation system so SVG improvement
feeds the organism's self-becoming cycle.
"""

import json
import logging
import math
import random
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ._cache import DATA_DIR
from .svg_challenges import (
    SVGChallenge, catalog, get_challenge, progressive_challenges,
    random_challenge, save_catalog,
)
from .svg_primitives import (
    SVGCanvas, circle, concentric_circles, checkered_grid, crystal_4d,
    crystal_lattice, dimensional_containment, dodecahedron,
    flower_of_life, fractal_tree, golden_spiral, icosahedron,
    koch_snowflake, line_grid, metatron_cube, mobius_strip, phi_grid,
    radial_burst, rect, regular_polygon, sfcr_crystal, sierpinski_triangle,
    sigma60_field, spiral_of_theodorus, sri_yantra, star_polygon,
    tesseract_projection, vesica_piscis, weave_wheel,
)
from .svg_scorer import SVGScore, SVGScorer, get_scorer

_log = logging.getLogger(__name__)

ARENA_DIR = DATA_DIR / "svg_arena"
OUTPUT_DIR = ARENA_DIR / "outputs"
HISTORY_FILE = ARENA_DIR / "history.json"


# ══════════════════════════════════════════════════════════════════════
#  Data Classes
# ══════════════════════════════════════════════════════════════════════

@dataclass
class SVGAttempt:
    """One generation attempt within a round."""
    attempt_id: int = 0
    challenge_id: str = ""
    svg_str: str = ""
    score: Optional[SVGScore] = None
    generation_time_ms: float = 0.0
    strategy: str = "initial"     # initial|perturb|rebuild|simplify
    parent_attempt_id: int = -1


@dataclass
class SVGRound:
    """Complete round: one challenge, multiple attempts."""
    round_id: int = 0
    challenge: Optional[SVGChallenge] = None
    attempts: List[SVGAttempt] = field(default_factory=list)
    best_score: float = 0.0
    best_svg: str = ""
    improvement_trajectory: List[float] = field(default_factory=list)
    timestamp: str = ""


# ══════════════════════════════════════════════════════════════════════
#  Reference Function Dispatch
# ══════════════════════════════════════════════════════════════════════

# Map of reference function names to actual callables
_REFERENCE_FNS = {
    "circle": circle,
    "rect": rect,
    "regular_polygon": regular_polygon,
    "line_grid": line_grid,
    "concentric_circles": concentric_circles,
    "star_polygon": star_polygon,
    "radial_burst": radial_burst,
    "checkered_grid": checkered_grid,
    "vesica_piscis": vesica_piscis,
    "flower_of_life": flower_of_life,
    "metatron_cube": metatron_cube,
    "sri_yantra": sri_yantra,
    "fractal_tree": fractal_tree,
    "spiral_of_theodorus": spiral_of_theodorus,
    "koch_snowflake": koch_snowflake,
    "sierpinski_triangle": sierpinski_triangle,
    "tesseract_projection": tesseract_projection,
    "crystal_lattice": crystal_lattice,
    "phi_grid": phi_grid,
    "golden_spiral": golden_spiral,
    # 3D/4D dimensional projections
    "dodecahedron": dodecahedron,
    "icosahedron": icosahedron,
    "mobius_strip": mobius_strip,
    "sfcr_crystal": sfcr_crystal,
    "crystal_4d": crystal_4d,
    "sigma60_field": sigma60_field,
    "dimensional_containment": dimensional_containment,
    "weave_wheel": weave_wheel,
}


def _crystal_mandala(cx: float, cy: float, size: float) -> str:
    """Composite: flower of life + phi grid + concentric circles."""
    from .svg_primitives import group
    children = [
        flower_of_life(cx, cy, size * 0.25, rings=2,
                       stroke="#6a5acd", stroke_opacity="0.5"),
        phi_grid(size * 2, size * 2, divisions=4,
                 stroke="#c0a040", stroke_opacity="0.4"),
        concentric_circles(cx, cy, size, n=5,
                           stroke="#333", stroke_width="0.8"),
    ]
    return group(children)


_REFERENCE_FNS["_crystal_mandala"] = _crystal_mandala


def _generate_reference(challenge: SVGChallenge) -> str:
    """Generate reference SVG for a challenge."""
    fn = _REFERENCE_FNS.get(challenge.reference_fn)
    if fn is None:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800"></svg>'

    canvas = SVGCanvas(challenge.canvas_width, challenge.canvas_height)
    element_str = fn(**challenge.reference_params)
    canvas.add(element_str)
    return canvas.render()


# ══════════════════════════════════════════════════════════════════════
#  Improvement Strategies (v2: intelligent, weakness-targeted)
# ══════════════════════════════════════════════════════════════════════

from .geometric_constants import PHI, PHI_INV


def _perturb_svg(svg_str: str, magnitude: float = 0.03) -> str:
    """Add small random perturbations to numeric attributes.
    v2: Much smaller magnitude to preserve structure."""
    def _jitter(match):
        val = float(match.group())
        delta = val * magnitude * (random.random() * 2 - 1)
        return f"{val + delta:.4f}".rstrip("0").rstrip(".")

    def _perturb_attrs(match):
        attr_val = match.group(1)
        perturbed = re.sub(r"-?\d+\.?\d*", _jitter, attr_val)
        return f'="{perturbed}"'

    return re.sub(r'="([^"]*\d[^"]*)"', _perturb_attrs, svg_str)


def _rebuild_svg(challenge: SVGChallenge, magnitude: float = 0.05) -> str:
    """Re-generate with slightly modified parameters.
    v2: Smaller magnitude, preserve structural params."""
    params = dict(challenge.reference_params)
    # Only modify continuous params, never discrete structure
    structural = {"n", "depth", "rows", "cols", "rings", "divisions",
                  "lattice_type", "fill", "stroke", "stroke_width",
                  "stroke_opacity"}
    for k, v in params.items():
        if k in structural:
            continue
        if isinstance(v, (int, float)):
            delta = v * magnitude * (random.random() * 2 - 1)
            if isinstance(v, int):
                params[k] = int(v + delta)
            else:
                params[k] = v + delta

    fn = _REFERENCE_FNS.get(challenge.reference_fn)
    if fn is None:
        return _generate_reference(challenge)

    canvas = SVGCanvas(challenge.canvas_width, challenge.canvas_height)
    canvas.add(fn(**params))
    return canvas.render()


def _inject_golden(svg_str: str, canvas_w: int = 800,
                   canvas_h: int = 800) -> str:
    """Inject golden ratio guide lines into the SVG for phi adherence boost."""
    # Add subtle phi-grid overlay before closing </svg>
    lines = []
    x = 0.0
    for _ in range(3):
        x = x + (canvas_w - x) * PHI_INV
        lines.append(
            f'  <line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{canvas_h}" '
            f'stroke="#c0a040" stroke-width="0.5" stroke-opacity="0.3"/>'
        )
    y = 0.0
    for _ in range(3):
        y = y + (canvas_h - y) * PHI_INV
        lines.append(
            f'  <line x1="0" y1="{y:.1f}" x2="{canvas_w}" y2="{y:.1f}" '
            f'stroke="#c0a040" stroke-width="0.5" stroke-opacity="0.3"/>'
        )
    overlay = "\n".join(lines)
    return svg_str.replace("</svg>", f"{overlay}\n</svg>")


def _inject_symmetry_ring(svg_str: str, cx: float = 400, cy: float = 400,
                           r: float = 250, n: int = 6) -> str:
    """Add n evenly-spaced marker dots for symmetry boost."""
    import math
    dots = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        dots.append(
            f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="2" '
            f'fill="#666" fill-opacity="0.3"/>'
        )
    overlay = "\n".join(dots)
    return svg_str.replace("</svg>", f"{overlay}\n</svg>")


def _simplify_svg(svg_str: str) -> str:
    """Reduce precision and remove empty groups."""
    def _reduce(match):
        val = float(match.group())
        return f"{val:.2f}".rstrip("0").rstrip(".")

    result = re.sub(r'="([^"]*)"',
                    lambda m: '="' + re.sub(r"-?\d+\.\d{3,}", _reduce,
                                            m.group(1)) + '"',
                    svg_str)
    result = re.sub(r"<g>\s*</g>", "", result)
    return result


def _diagnose_weakness(score) -> str:
    """Identify the weakest scoring dimension to target next."""
    dims = {
        "golden": score.golden_ratio_adherence,
        "symmetry": score.symmetry_score,
        "balance": score.balance_score,
        "bbox": score.bounding_box_accuracy,
        "centroid": score.centroid_accuracy,
        "path": score.path_complexity,
        "diversity": score.element_diversity,
        "transform": score.transform_depth,
        "compression": score.compression_ratio,
    }
    return min(dims, key=dims.get)


# ══════════════════════════════════════════════════════════════════════
#  SVG Self-Play Engine (v2: weakness-targeted improvement)
# ══════════════════════════════════════════════════════════════════════

class SVGSelfPlayEngine:
    """Runs self-play improvement loops on SVG generation challenges.

    v2: Intelligent improvement loop that diagnoses weaknesses and
    applies targeted strategies instead of random perturbation.
    """

    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts
        self.scorer = get_scorer()
        self.rounds: List[SVGRound] = []
        self._round_counter = 0
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        ARENA_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _score_svg(self, svg: str, challenge: SVGChallenge):
        return self.scorer.score(
            svg,
            target_elements=challenge.target_elements,
            target_symmetry=challenge.target_symmetry,
            target_golden=challenge.target_golden,
            canvas_width=challenge.canvas_width,
            canvas_height=challenge.canvas_height,
        )

    def run_round(self, challenge: Optional[SVGChallenge] = None) -> SVGRound:
        """Run one complete self-play round with intelligent improvement."""
        if challenge is None:
            challenge = random_challenge()

        self._round_counter += 1
        rnd = SVGRound(
            round_id=self._round_counter,
            challenge=challenge,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        best_score_val = 0.0
        best_svg = ""
        best_score_obj = None

        for i in range(self.max_attempts):
            t0 = time.monotonic()

            if i == 0:
                # Attempt 0: Reference generation (baseline)
                strategy = "initial"
                svg = _generate_reference(challenge)
            elif i == 1 and best_score_obj:
                # Attempt 1: Diagnose weakness and target it
                weakness = _diagnose_weakness(best_score_obj)
                if weakness == "golden":
                    strategy = "golden_inject"
                    svg = _inject_golden(best_svg, challenge.canvas_width,
                                         challenge.canvas_height)
                elif weakness == "symmetry" and challenge.target_symmetry > 0:
                    strategy = "symmetry_inject"
                    svg = _inject_symmetry_ring(
                        best_svg, challenge.canvas_width / 2,
                        challenge.canvas_height / 2, n=challenge.target_symmetry)
                else:
                    strategy = "rebuild"
                    svg = _rebuild_svg(challenge, magnitude=0.03)
            elif i == 2:
                # Attempt 2: Golden + symmetry combo
                strategy = "golden+symmetry"
                svg = _inject_golden(best_svg, challenge.canvas_width,
                                     challenge.canvas_height)
                if challenge.target_symmetry > 0:
                    svg = _inject_symmetry_ring(
                        svg, challenge.canvas_width / 2,
                        challenge.canvas_height / 2,
                        n=challenge.target_symmetry)
            elif i == 3:
                # Attempt 3: Micro-perturbation of current best
                strategy = "micro_perturb"
                svg = _perturb_svg(best_svg, magnitude=0.01)
            else:
                # Attempt 4+: Simplify for compression boost
                strategy = "simplify"
                svg = _simplify_svg(best_svg)

            gen_time = (time.monotonic() - t0) * 1000

            score = self._score_svg(svg, challenge)
            score.generation_time_ms = gen_time

            attempt = SVGAttempt(
                attempt_id=i,
                challenge_id=challenge.challenge_id,
                svg_str=svg,
                score=score,
                generation_time_ms=gen_time,
                strategy=strategy,
                parent_attempt_id=i - 1 if i > 0 else -1,
            )
            rnd.attempts.append(attempt)
            rnd.improvement_trajectory.append(score.total_score)

            if score.total_score > best_score_val:
                best_score_val = score.total_score
                best_svg = svg
                best_score_obj = score

        rnd.best_score = best_score_val
        rnd.best_svg = best_svg
        self.rounds.append(rnd)

        # Save best SVG
        self._save_best(challenge.challenge_id, best_svg)

        return rnd

    def run_session(self, rounds: int = 10,
                    progressive: bool = True,
                    category: Optional[str] = None) -> List[SVGRound]:
        """Run multiple rounds."""
        results = []
        if progressive:
            challenges = progressive_challenges(rounds)
        else:
            challenges = [random_challenge(category=category) for _ in range(rounds)]

        for challenge in challenges:
            rnd = self.run_round(challenge)
            results.append(rnd)
            _log.info("Round %d [%s]: %.3f (attempts=%d)",
                      rnd.round_id, challenge.name,
                      rnd.best_score, len(rnd.attempts))

        self._save_history()
        return results

    def _save_best(self, challenge_id: str, svg_str: str) -> None:
        """Save best SVG for a challenge."""
        out = OUTPUT_DIR / f"{challenge_id}_best.svg"
        out.write_text(svg_str, encoding="utf-8")

    def _save_history(self) -> None:
        """Save round history to JSON."""
        history = {
            "meta": {
                "total_rounds": len(self.rounds),
                "best_overall": max((r.best_score for r in self.rounds), default=0.0),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "rounds": [],
        }
        for rnd in self.rounds:
            history["rounds"].append({
                "round_id": rnd.round_id,
                "challenge_id": rnd.challenge.challenge_id if rnd.challenge else "",
                "challenge_name": rnd.challenge.name if rnd.challenge else "",
                "best_score": rnd.best_score,
                "attempts": len(rnd.attempts),
                "improvement_trajectory": rnd.improvement_trajectory,
                "timestamp": rnd.timestamp,
            })
        HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def get_history(self, last_n: int = 10) -> Dict:
        """Load and return recent history."""
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if last_n > 0:
                data["rounds"] = data["rounds"][-last_n:]
            return data
        return {"meta": {"total_rounds": 0}, "rounds": []}

    def get_best(self, challenge_id: str) -> Optional[str]:
        """Retrieve the best SVG for a challenge."""
        p = OUTPUT_DIR / f"{challenge_id}_best.svg"
        if p.exists():
            return p.read_text(encoding="utf-8")
        return None


# Module-level singleton
_engine: Optional[SVGSelfPlayEngine] = None


def get_engine(max_attempts: int = 5) -> SVGSelfPlayEngine:
    """Get or create the singleton self-play engine."""
    global _engine
    if _engine is None:
        _engine = SVGSelfPlayEngine(max_attempts=max_attempts)
    return _engine
