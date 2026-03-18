# CRYSTAL: Xi108:W2:A1:S1 | face=S | node=1 | depth=0 | phase=Fixed
# METRO: Me
# BRIDGES: Xi108:W2:A1:S2→Xi108:W2:A1:S36→Xi108:W1:A1:S1→Xi108:W2:A12:S1→Xi108:W2:A2:S1

"""
Archetype Roles — 12 Job Definitions for Crystal-Parallel Observers
=====================================================================
Each archetype emerges from crossing 4 elements × 3 modes (structural,
relational, recursive). The 12 archetypes define specific observation
roles within the swarm:

  Element × Mode → Archetype:
    S×structural = Apex Seed (A1)        — Foundation scanner
    S×relational = Crystal Quartet (A4)  — Structural connector
    S×recursive  = Change/Arc Heptad (A7) — Transformation tracker
    F×structural = Möbius Axle (A2)      — Relation mapper
    F×relational = Observer Pentad (A5)  — Perspective holder
    F×recursive  = Antispin Octad (A8)   — Contradiction detector
    C×structural = Modal Trefoil (A3)    — Pattern recognizer
    C×relational = Dyadic Hinge Hexad (A6) — Bridge builder
    C×recursive  = Emergent Ennead (A9)  — Emergence sensor
    R×structural = Deca-Cascade Crown (A10) — Scale navigator
    R×relational = Odd-Orbit Hendecad (A11) — Compression auditor
    R×recursive  = Dodecad Bundle (A12)  — Seed emitter

The 12D observation schema maps each archetype to its emphasized dimensions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .constants import ARCHETYPE_NAMES, LENS_CODES

# 12D dimension names
DIM_NAMES = [
    "x1_structure", "x2_semantics", "x3_coordination", "x4_recursion",
    "x5_contradiction", "x6_emergence", "x7_legibility", "x8_routing",
    "x9_grounding", "x10_compression", "x11_interop", "x12_potential",
]


@dataclass
class ArchetypeRole:
    """Definition of one archetype's observation job within the swarm."""
    archetype_idx: int           # 1-12
    name: str                    # Human-readable name
    element_affinity: str        # Primary element (S/F/C/R)
    mode: str                    # structural / relational / recursive
    job_description: str         # What this observer looks for
    emphasized_dims: list[str] = field(default_factory=list)  # Which 12D dims to upweight
    dim_weights: dict = field(default_factory=dict)  # dim_name → weight multiplier
    observation_focus: str = ""  # One-line focus directive
    wreath_affinity: str = ""    # Natural wreath (Su/Me/Sa) — empty = no preference

    def describe(self) -> str:
        return (
            f"A{self.archetype_idx} {self.name} "
            f"[{LENS_CODES.get(self.element_affinity, '?')}/{self.mode}] — "
            f"{self.job_description}"
        )


# ── The 12 Archetype Role Definitions ────────────────────────────────

ARCHETYPE_ROLES: dict[int, ArchetypeRole] = {
    # ── Square/Earth family (S) ── structural foundation ──
    1: ArchetypeRole(
        archetype_idx=1,
        name="Apex Seed",
        element_affinity="S",
        mode="structural",
        job_description="Scan for foundational structure: gate transitions, shell "
                        "proximity, and crystal address validity. Verify the skeleton.",
        emphasized_dims=["x1_structure", "x7_legibility", "x8_routing"],
        dim_weights={"x1_structure": 2.0, "x7_legibility": 1.5, "x8_routing": 1.5,
                     "x9_grounding": 1.2},
        observation_focus="Is the structural foundation correct and complete?",
        wreath_affinity="Su",
    ),
    4: ArchetypeRole(
        archetype_idx=4,
        name="Crystal Quartet",
        element_affinity="S",
        mode="relational",
        job_description="Scan for structural connections: cross-chapter links, "
                        "cross-appendix bridges, and gate-to-gate transition paths.",
        emphasized_dims=["x1_structure", "x3_coordination", "x11_interop"],
        dim_weights={"x1_structure": 1.5, "x3_coordination": 2.0, "x11_interop": 1.5},
        observation_focus="Are structural connections well-formed and reachable?",
        wreath_affinity="Me",
    ),
    7: ArchetypeRole(
        archetype_idx=7,
        name="Change/Arc Heptad",
        element_affinity="S",
        mode="recursive",
        job_description="Track transformations: how structure changes across shells, "
                        "which gate transitions are most active, where evolution happens.",
        emphasized_dims=["x1_structure", "x4_recursion", "x6_emergence"],
        dim_weights={"x1_structure": 1.3, "x4_recursion": 2.0, "x6_emergence": 1.5},
        observation_focus="Where is structural evolution most active?",
        wreath_affinity="Sa",
    ),

    # ── Flower/Fire family (F) ── relational dynamics ──
    2: ArchetypeRole(
        archetype_idx=2,
        name="Möbius Axle",
        element_affinity="F",
        mode="structural",
        job_description="Map relations: token overlap networks, pair weight topology, "
                        "and element affinity patterns. Build the relation graph.",
        emphasized_dims=["x2_semantics", "x3_coordination", "x9_grounding"],
        dim_weights={"x2_semantics": 2.0, "x3_coordination": 1.5, "x9_grounding": 1.5},
        observation_focus="What is the topology of the relation network?",
        wreath_affinity="Su",
    ),
    5: ArchetypeRole(
        archetype_idx=5,
        name="Observer Pentad",
        element_affinity="F",
        mode="relational",
        job_description="Hold multiple perspectives simultaneously: compare how the "
                        "same query looks from different element lenses. Detect bias.",
        emphasized_dims=["x2_semantics", "x5_contradiction", "x12_potential"],
        dim_weights={"x2_semantics": 1.5, "x5_contradiction": 2.0, "x12_potential": 1.5},
        observation_focus="Where do different perspectives contradict or complement?",
        wreath_affinity="Me",
    ),
    8: ArchetypeRole(
        archetype_idx=8,
        name="Antispin Octad",
        element_affinity="F",
        mode="recursive",
        job_description="Detect contradictions: where pair weights disagree with gate "
                        "weights, where element affinities conflict, where the crystal "
                        "holds unresolved tension.",
        emphasized_dims=["x5_contradiction", "x4_recursion", "x6_emergence"],
        dim_weights={"x5_contradiction": 2.0, "x4_recursion": 1.5, "x6_emergence": 1.3},
        observation_focus="Where are the contradictions and unresolved tensions?",
        wreath_affinity="Sa",
    ),

    # ── Cloud/Water family (C) ── observational fields ──
    3: ArchetypeRole(
        archetype_idx=3,
        name="Modal Trefoil",
        element_affinity="C",
        mode="structural",
        job_description="Recognize patterns: neighborhood density, clustering structure, "
                        "and shell-level statistical signatures.",
        emphasized_dims=["x2_semantics", "x6_emergence", "x11_interop"],
        dim_weights={"x2_semantics": 1.5, "x6_emergence": 2.0, "x11_interop": 1.5},
        observation_focus="What patterns emerge from the neighborhood structure?",
        wreath_affinity="Su",
    ),
    6: ArchetypeRole(
        archetype_idx=6,
        name="Dyadic Hinge Hexad",
        element_affinity="C",
        mode="relational",
        job_description="Build bridges: identify where cross-element, cross-wreath, "
                        "and cross-shell connections are missing or weak.",
        emphasized_dims=["x3_coordination", "x6_emergence", "x8_routing"],
        dim_weights={"x3_coordination": 2.0, "x6_emergence": 1.5, "x8_routing": 1.5},
        observation_focus="Where are bridges missing or weak?",
        wreath_affinity="Me",
    ),
    9: ArchetypeRole(
        archetype_idx=9,
        name="Emergent Ennead",
        element_affinity="C",
        mode="recursive",
        job_description="Sense emergence: detect when new patterns form from the "
                        "interaction of existing elements. Track phase transitions.",
        emphasized_dims=["x6_emergence", "x12_potential", "x4_recursion"],
        dim_weights={"x6_emergence": 2.0, "x12_potential": 1.5, "x4_recursion": 1.3},
        observation_focus="Is emergence happening? What is trying to be born?",
        wreath_affinity="Sa",
    ),

    # ── Fractal/Air family (R) ── compression/scale ──
    10: ArchetypeRole(
        archetype_idx=10,
        name="Deca-Cascade Crown",
        element_affinity="R",
        mode="structural",
        job_description="Navigate scale: verify that shell seeds, archetype seeds, "
                        "and nano seeds are consistent across compression levels.",
        emphasized_dims=["x10_compression", "x1_structure", "x7_legibility"],
        dim_weights={"x10_compression": 2.0, "x1_structure": 1.5, "x7_legibility": 1.3},
        observation_focus="Is multi-scale coherence maintained across compression?",
        wreath_affinity="Su",
    ),
    11: ArchetypeRole(
        archetype_idx=11,
        name="Odd-Orbit Hendecad",
        element_affinity="R",
        mode="relational",
        job_description="Audit compression: measure reconstruction error, seed fidelity, "
                        "and information loss at each 1/8 lift step.",
        emphasized_dims=["x10_compression", "x9_grounding", "x11_interop"],
        dim_weights={"x10_compression": 1.5, "x9_grounding": 2.0, "x11_interop": 1.5},
        observation_focus="How much information is lost at each compression level?",
        wreath_affinity="Me",
    ),
    12: ArchetypeRole(
        archetype_idx=12,
        name="Dodecad Bundle",
        element_affinity="R",
        mode="recursive",
        job_description="Emit seeds: compress observation traces to 1/8 size, verify "
                        "that compressed seeds can regenerate the full observation.",
        emphasized_dims=["x10_compression", "x12_potential", "x4_recursion"],
        dim_weights={"x10_compression": 1.5, "x12_potential": 2.0, "x4_recursion": 1.5},
        observation_focus="Can the observation be compressed and recovered?",
        wreath_affinity="Sa",
    ),
}


def get_role(archetype_idx: int) -> ArchetypeRole:
    """Get the role definition for a given archetype index (1-12)."""
    return ARCHETYPE_ROLES.get(archetype_idx, ARCHETYPE_ROLES[1])


def get_role_for_element_mode(element: str, mode: str) -> ArchetypeRole:
    """Get the archetype role for a given element + mode combination."""
    for role in ARCHETYPE_ROLES.values():
        if role.element_affinity == element and role.mode == mode:
            return role
    return ARCHETYPE_ROLES[1]


def element_roles(element: str) -> list[ArchetypeRole]:
    """Get all 3 roles for a given element (structural, relational, recursive)."""
    return [r for r in ARCHETYPE_ROLES.values() if r.element_affinity == element]


def describe_all() -> str:
    """Human-readable summary of all 12 archetype roles."""
    lines = ["# 12 Archetype Observer Roles", ""]
    for idx in sorted(ARCHETYPE_ROLES):
        role = ARCHETYPE_ROLES[idx]
        lines.append(role.describe())
    return "\n".join(lines)
