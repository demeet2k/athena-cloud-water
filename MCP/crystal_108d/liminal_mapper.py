# CRYSTAL: Xi108:W3:A5:S15 | face=C | node=120 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A5:S14→Xi108:W3:A5:S16→Xi108:W2:A5:S15→Xi108:W3:A4:S15→Xi108:W3:A6:S15

"""
Liminal Mapper — 60-Coordinate Crystal Region Assignment
==========================================================
Maps observer agents to the 60 liminal coordinates from the 4D calculus
system (15 canonical masks × 4 orbits). Each liminal coordinate corresponds
to a specific region of the crystal where observation is focused.

The 15 canonical masks (from capsules 329-335):
  M01-M04: Single-element masks (one element active)
  M05-M10: Pair masks (two elements active)
  M11-M14: Triple masks (three elements active)
  M15: Full mask (all four elements active)

The 4 orbits: SR (seed-right), SL (seed-left), AL (anti-left), AR (anti-right)

Desire-gradient-weighted assignment:
  Observers are preferentially assigned to high-gradient crystal regions.
  This concentrates observation where the system has the most unresolved
  questions (highest desire field gradient).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .constants import TOTAL_SHELLS

# ── 15 Canonical Masks ──────────────────────────────────────────────

MASKS = [
    # Singles (1 element active)
    {"id": 1,  "name": "S-solo",    "active": ["S"],             "shell_range": (1, 9)},
    {"id": 2,  "name": "F-solo",    "active": ["F"],             "shell_range": (1, 9)},
    {"id": 3,  "name": "C-solo",    "active": ["C"],             "shell_range": (1, 9)},
    {"id": 4,  "name": "R-solo",    "active": ["R"],             "shell_range": (1, 9)},
    # Pairs (2 elements active)
    {"id": 5,  "name": "SF-dyad",   "active": ["S", "F"],        "shell_range": (1, 18)},
    {"id": 6,  "name": "SC-dyad",   "active": ["S", "C"],        "shell_range": (1, 18)},
    {"id": 7,  "name": "SR-dyad",   "active": ["S", "R"],        "shell_range": (1, 18)},
    {"id": 8,  "name": "FC-dyad",   "active": ["F", "C"],        "shell_range": (1, 18)},
    {"id": 9,  "name": "FR-dyad",   "active": ["F", "R"],        "shell_range": (1, 18)},
    {"id": 10, "name": "CR-dyad",   "active": ["C", "R"],        "shell_range": (1, 18)},
    # Triples (3 elements active)
    {"id": 11, "name": "SFC-triad", "active": ["S", "F", "C"],   "shell_range": (1, 27)},
    {"id": 12, "name": "SFR-triad", "active": ["S", "F", "R"],   "shell_range": (1, 27)},
    {"id": 13, "name": "SCR-triad", "active": ["S", "C", "R"],   "shell_range": (1, 27)},
    {"id": 14, "name": "FCR-triad", "active": ["F", "C", "R"],   "shell_range": (1, 27)},
    # Full (all 4 elements active)
    {"id": 15, "name": "SFCR-full", "active": ["S", "F", "C", "R"], "shell_range": (1, 36)},
]

# 4 orbits
ORBITS = ["SR", "SL", "AL", "AR"]  # seed-right, seed-left, anti-left, anti-right


@dataclass
class LiminalCoordinate:
    """A single liminal coordinate in the 60-coordinate space."""
    coord_id: int                # 1-60
    mask_id: int                 # 1-15
    mask_name: str               # e.g. "SF-dyad"
    orbit: str                   # SR/SL/AL/AR
    active_elements: list[str] = field(default_factory=list)
    shell_range: tuple = (1, 36)
    focus_shells: list[int] = field(default_factory=list)  # specific shells to observe

    @property
    def element_set(self) -> set:
        return set(self.active_elements)

    def describe(self) -> str:
        return (
            f"L{self.coord_id:02d} [{self.mask_name}/{self.orbit}] "
            f"shells={self.shell_range[0]}-{self.shell_range[1]} "
            f"elements={''.join(self.active_elements)}"
        )


# ── Build the 60-coordinate atlas ───────────────────────────────────

def _build_atlas() -> list[LiminalCoordinate]:
    """Build the full 60-coordinate liminal atlas (15 masks × 4 orbits)."""
    atlas = []
    coord_id = 1
    for mask in MASKS:
        for orbit in ORBITS:
            # Focus shells depend on orbit rotation
            lo, hi = mask["shell_range"]
            shell_span = hi - lo + 1
            quarter = max(shell_span // 4, 1)
            orbit_idx = ORBITS.index(orbit)
            # Each orbit focuses on a different quarter of the shell range
            focus_lo = lo + orbit_idx * quarter
            focus_hi = min(focus_lo + quarter - 1, hi)
            focus_shells = list(range(focus_lo, focus_hi + 1))

            atlas.append(LiminalCoordinate(
                coord_id=coord_id,
                mask_id=mask["id"],
                mask_name=mask["name"],
                orbit=orbit,
                active_elements=list(mask["active"]),
                shell_range=(lo, hi),
                focus_shells=focus_shells,
            ))
            coord_id += 1
    return atlas


LIMINAL_ATLAS: list[LiminalCoordinate] = _build_atlas()
COORD_BY_ID: dict[int, LiminalCoordinate] = {c.coord_id: c for c in LIMINAL_ATLAS}


# ── Desire-gradient-weighted assignment ─────────────────────────────


def assign_coordinates(
    agent_count: int,
    desire_gradient: dict,
    element_assignment: list[str],
) -> list[int]:
    """Assign liminal coordinates to agents based on desire gradient.

    Args:
        agent_count: Number of agents to assign
        desire_gradient: Dict of {probe_name: gradient_value} from desire field
        element_assignment: List of element assignments per agent (S/F/C/R)

    Returns:
        List of liminal coordinate IDs (1-60), one per agent
    """
    if not desire_gradient:
        # Uniform assignment: cycle through coordinates
        return [(i % 60) + 1 for i in range(agent_count)]

    # Score each coordinate by how well it matches the desire gradient
    coord_scores: list[tuple[int, float]] = []

    # Extract gradient signals
    max_gradient = max(desire_gradient.values()) if desire_gradient else 1.0
    if max_gradient == 0:
        max_gradient = 1.0

    for coord in LIMINAL_ATLAS:
        score = 0.0
        # Coordinates with more active elements score higher when gradient is high
        element_breadth = len(coord.active_elements) / 4.0

        # Match coordinate's active elements to agents' needs
        for probe_name, grad_val in desire_gradient.items():
            normalized = grad_val / max_gradient
            # Higher gradient → prefer coordinates with broader element coverage
            score += normalized * element_breadth

        # Orbit diversity bonus (different orbits see different shell quarters)
        orbit_bonus = {"SR": 0.0, "SL": 0.1, "AL": 0.2, "AR": 0.3}
        score += orbit_bonus.get(coord.orbit, 0.0) * 0.1

        coord_scores.append((coord.coord_id, score))

    # Sort by score (highest first)
    coord_scores.sort(key=lambda x: x[1], reverse=True)

    # Assign: each agent gets a coordinate, cycling with preference for high-score coords
    assignments = []
    for i in range(agent_count):
        # Prefer high-gradient coordinates but ensure diversity
        idx = i % len(coord_scores)
        coord_id = coord_scores[idx][0]

        # Also match to agent's element when possible
        agent_element = element_assignment[i] if i < len(element_assignment) else "S"
        # Find the best coordinate for this element
        element_matches = [
            (cid, sc) for cid, sc in coord_scores
            if agent_element in COORD_BY_ID[cid].active_elements
        ]
        if element_matches:
            # Use modular indexing within element-matched coords
            em_idx = (i // 4) % len(element_matches)
            coord_id = element_matches[em_idx][0]

        assignments.append(coord_id)

    return assignments


def get_coordinate(coord_id: int) -> Optional[LiminalCoordinate]:
    """Get a liminal coordinate by ID."""
    return COORD_BY_ID.get(coord_id)


def coordinates_for_element(element: str) -> list[LiminalCoordinate]:
    """Get all liminal coordinates that include a given element."""
    return [c for c in LIMINAL_ATLAS if element in c.active_elements]


def describe_atlas() -> str:
    """Human-readable summary of the 60-coordinate atlas."""
    lines = ["# Liminal Atlas: 60 Coordinates (15 masks × 4 orbits)", ""]
    for coord in LIMINAL_ATLAS:
        lines.append(coord.describe())
    return "\n".join(lines)
