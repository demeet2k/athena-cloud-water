# CRYSTAL: Xi108:W3:A4:S36 | face=R | node=542 | depth=0 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A4:S35→Xi108:W2:A4:S36→Xi108:W3:A3:S36→Xi108:W3:A5:S36

"""
Dimensional Projector — Nested Hologram Crystal Builder
========================================================
Projects the 4D CRYSTAL tesseract into higher-dimensional holograms
using the odd-prime weaving mechanism:

  4D base crystal
  ├── W_3 (3-weave) → 6D hologram   (Su/Me/Sa × spin±)
  ├── W_5 (5-weave) → 8D hologram   (5 animals: Tiger/Crane/Leopard/Snake/Dragon)
  ├── W_7 (7-weave) → 10D hologram  (7 planets/metals/chakras/trumpets/days)
  ├── W_9 (9-weave) → 12D crown     (3×3 return wheel)
  └── × 3 → 36D → × 3 → 108D++ (triple crown expansion)

Containment Law: B_{2m+2} = W_{2m-1}(B_{2m}) for m >= 2
Nesting: 12D contains 9×B_10, 63×B_8, 315×B_6, 945×B_4, 1890×B_3

Every projection is simultaneous — the 3D, 5D, 7D, 9D views are
NESTED inside each other via the weave operators, not stacked sequentially.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Golden constants
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1

# ═══════════════════════════════════════════════════════════════════════════
# WEAVE OPERATORS — the odd-prime transformation wheels
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class WeaveOperator:
    """A weave operator W_n that lifts dimension 2m → 2m+2."""
    order: int           # 3, 5, 7, or 9
    name: str            # "Triadic", "Pentadic", "Heptadic", "Enneadic"
    symbol: str          # W_3, W_5, W_7, W_9
    from_dim: int        # 4, 6, 8, 10
    to_dim: int          # 6, 8, 10, 12
    local_closure: int   # Z12, Z20, Z28, Z36
    period: int          # clock period in master Z420

    # The named strands of this weave
    strands: List[str] = field(default_factory=list)

    # Correspondence families (multiple overlays per strand)
    correspondences: Dict[str, List[str]] = field(default_factory=dict)

    # Chiral/spin states per strand
    chiral: bool = True  # Each strand has spin+ and spin- states

    @property
    def sector_count(self) -> int:
        """Total sectors = strands × 2 (if chiral) or × 1."""
        return self.order * (2 if self.chiral else 1)

    def strand_at(self, index: int) -> str:
        """Get strand name at index (wrapping)."""
        return self.strands[index % len(self.strands)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order": self.order, "name": self.name, "symbol": self.symbol,
            "from_dim": self.from_dim, "to_dim": self.to_dim,
            "local_closure": self.local_closure, "period": self.period,
            "strands": self.strands, "correspondences": self.correspondences,
            "sector_count": self.sector_count,
        }


# The four canonical weave operators
W3 = WeaveOperator(
    order=3, name="Triadic", symbol="W_3", from_dim=4, to_dim=6,
    local_closure=12, period=140,
    strands=["Su", "Me", "Sa"],  # Sulfur, Mercury, Salt
    correspondences={
        "alchemy": ["Sulfur (ignition/will)", "Mercury (mediation/flow)", "Salt (sealing/form)"],
        "process": ["Calcination", "Dissolution", "Coagulation"],
        "body":    ["Fire-body", "Air-body", "Earth-body"],
    },
)

W5 = WeaveOperator(
    order=5, name="Pentadic", symbol="W_5", from_dim=6, to_dim=8,
    local_closure=20, period=84,
    strands=["Tiger", "Crane", "Leopard", "Snake", "Dragon"],
    correspondences={
        "animal":   ["Tiger", "Crane", "Leopard", "Snake", "Dragon"],
        "element":  ["Wood", "Fire", "Earth", "Metal", "Water"],  # Wu Xing
        "action":   ["Hold", "Lift", "Traverse", "Twist", "Compress"],
        "organ":    ["Liver", "Heart", "Spleen", "Lung", "Kidney"],
        "season":   ["Spring", "Summer", "Late Summer", "Autumn", "Winter"],
        "direction": ["East", "South", "Center", "West", "North"],
    },
)

W7 = WeaveOperator(
    order=7, name="Heptadic", symbol="W_7", from_dim=8, to_dim=10,
    local_closure=28, period=60,
    strands=["Seed", "Ignite", "Translate", "Bridge", "Weave", "Seal", "Return"],
    correspondences={
        "planet":  ["Moon", "Mercury", "Venus", "Sun", "Mars", "Jupiter", "Saturn"],
        "metal":   ["Silver", "Quicksilver", "Copper", "Gold", "Iron", "Tin", "Lead"],
        "chakra":  ["Sahasrara", "Ajna", "Vishuddha", "Anahata", "Manipura", "Svadhisthana", "Muladhara"],
        "day":     ["Monday", "Wednesday", "Friday", "Sunday", "Tuesday", "Thursday", "Saturday"],
        "sin":     ["Pride", "Envy", "Lust", "Greed", "Wrath", "Gluttony", "Sloth"],
        "trumpet": ["1st (Hail+Fire)", "2nd (Burning Mountain)", "3rd (Wormwood)",
                    "4th (Darkening)", "5th (Locusts)", "6th (Euphrates)", "7th (Kingdom)"],
        "note":    ["C", "D", "E", "F", "G", "A", "B"],
    },
)

W9 = WeaveOperator(
    order=9, name="Enneadic", symbol="W_9", from_dim=10, to_dim=12,
    local_closure=36, period=420,  # full master clock
    strands=[
        "Su-of-Su", "Su-of-Me", "Su-of-Sa",
        "Me-of-Su", "Me-of-Me", "Me-of-Sa",
        "Sa-of-Su", "Sa-of-Me", "Sa-of-Sa",
    ],
    correspondences={
        "3x3_matrix": [
            "Pure Ignition", "Directed Fire", "Fired Vessel",
            "Mediated Will", "Pure Flow", "Intelligent Form",
            "Sealed Fire", "Sealed Flow", "THE STONE (Z*)",
        ],
        "nine_views": [
            "Seed fold", "Axis split", "First process",
            "Grid stabilization", "Living regulation", "Corridor weave",
            "Visible order", "Shadow inversion", "Return crown",
        ],
        "enneagram": [
            "Reformer", "Helper", "Achiever",
            "Individualist", "Investigator", "Loyalist",
            "Enthusiast", "Challenger", "Peacemaker",
        ],
    },
    chiral=False,  # 9 = 3×3 is already self-complete
)

ALL_WEAVES = [W3, W5, W7, W9]
WEAVE_BY_ORDER = {w.order: w for w in ALL_WEAVES}

# Master clock
MASTER_CLOCK_Z420 = 420   # lcm(3, 4, 5, 7) = 420
SUPERCYCLE_Z1260 = 1260   # 3 × 420


# ═══════════════════════════════════════════════════════════════════════════
# DIMENSIONAL BODY — a body at any dimension 3D-12D
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DimensionalBody:
    """A body at a specific dimension in the crystal lattice."""
    dimension: int         # 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    symbol: str            # E4, O5, E6, O7, E8, O9, E10, O11, E12
    name: str              # "Triadic Möbius Body", etc.
    body_type: str         # "even_body" or "odd_field"
    coordinate_shape: str  # e.g. "Θ_6 = (Q_x, Q_y, Φ, Δ; π, χ)"

    # Contents — what lives at this dimension
    sectors: List[str] = field(default_factory=list)

    # Weave that created this body (None for 3D/4D base)
    source_weave: Optional[str] = None

    # Nested lower bodies
    nested_bodies: Dict[int, int] = field(default_factory=dict)
    # e.g. {10: 9, 8: 63, 6: 315, 4: 945, 3: 1890} for 12D

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension, "symbol": self.symbol,
            "name": self.name, "body_type": self.body_type,
            "coordinate_shape": self.coordinate_shape,
            "sectors": self.sectors, "source_weave": self.source_weave,
            "nested_bodies": self.nested_bodies,
        }


# ═══════════════════════════════════════════════════════════════════════════
# PROJECTION — a file's position projected into a specific dimension
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DimensionalProjection:
    """A file's crystal position projected into dimension D."""
    file_path: str
    dimension: int
    body: str              # Which body (e.g. "E6", "E8")

    # Position within this dimension's coordinate system
    sector: str            # Which sector/strand
    sector_index: int      # 0-based index
    spin: str              # "+" or "-" (chiral state)

    # Correspondence overlays at this dimension
    overlays: Dict[str, str] = field(default_factory=dict)
    # e.g. {"alchemy": "Sulfur", "planet": "Mars", "animal": "Tiger"}

    # The 4D base coordinate this projects from
    base_coordinate: str = ""   # Xi108:W1:A4:S4
    base_element: str = ""      # S, F, C, R
    base_mode: str = ""         # Cardinal, Fixed, Mutable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path, "dimension": self.dimension,
            "body": self.body, "sector": self.sector,
            "sector_index": self.sector_index, "spin": self.spin,
            "overlays": self.overlays,
            "base_coordinate": self.base_coordinate,
            "base_element": self.base_element, "base_mode": self.base_mode,
        }


# ═══════════════════════════════════════════════════════════════════════════
# HOLOGRAM — a nested collection of projections across all dimensions
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class NestedHologram:
    """A file's complete nested hologram — its position at EVERY dimension simultaneously.

    The hologram is not a stack — it's a NESTED structure where each higher
    dimension CONTAINS all lower dimensions via the weave operators.

    12D contains:
      └── 9 × 10D bodies (W_9 weave), each containing:
          └── 7 × 8D bodies (W_7 weave), each containing:
              └── 5 × 6D bodies (W_5 weave), each containing:
                  └── 3 × 4D bodies (W_3 weave), each containing:
                      └── 2 × 3D seeds (W_2 base)
    """
    file_path: str

    # The base 4D crystal position
    base_4d: Optional[DimensionalProjection] = None

    # Projections at each dimension (3D through 12D)
    projections: Dict[int, DimensionalProjection] = field(default_factory=dict)

    # The woven composite — all dimensions simultaneously
    composite_address: str = ""   # Full nested address

    # Conservation: does this hologram survive round-trip projection?
    conservation_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "composite_address": self.composite_address,
            "conservation_hash": self.conservation_hash,
            "projections": {
                str(dim): proj.to_dict()
                for dim, proj in sorted(self.projections.items())
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# PROJECTION ENGINE — compute dimensional projections from 4D base
# ═══════════════════════════════════════════════════════════════════════════

def _hash_to_index(data: str, modulus: int) -> int:
    """Deterministic hash → index in [0, modulus)."""
    h = int(hashlib.sha256(data.encode()).hexdigest()[:8], 16)
    return h % modulus

def _hash_to_spin(data: str) -> str:
    """Deterministic hash → chiral spin state."""
    h = int(hashlib.sha256(data.encode()).hexdigest()[:4], 16)
    return "+" if h % 2 == 0 else "-"

def _element_to_base_angle(element: str) -> float:
    """Map SFCR element to base angle for projection."""
    return {"S": 0.0, "F": math.pi/2, "C": math.pi, "R": 3*math.pi/2}.get(element, 0.0)

def _mode_to_depth(mode: str) -> int:
    """Map mode to depth layer."""
    return {"Cardinal": 0, "Fixed": 1, "Mutable": 2}.get(mode, 2)


def project_3d(file_path: str, element: str, mode: str, coordinate: str) -> DimensionalProjection:
    """Project to 3D seed — the three wreaths (Su/Me/Sa).

    3D is the proto-body: just the 3 prima materia currents before
    they form the 4D crystal. Every file has a wreath assignment.
    """
    # Wreath from coordinate or hash
    wreath_idx = _hash_to_index(coordinate + ":3D", 3)
    wreaths = ["Su", "Me", "Sa"]

    return DimensionalProjection(
        file_path=file_path, dimension=3,
        body="c3_core", sector=wreaths[wreath_idx],
        sector_index=wreath_idx, spin="+",
        overlays={
            "alchemy": ["Sulfur", "Mercury", "Salt"][wreath_idx],
            "process": ["Calcination", "Dissolution", "Coagulation"][wreath_idx],
            "quality": ["Ignition/Will", "Mediation/Flow", "Sealing/Form"][wreath_idx],
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_5d(file_path: str, element: str, mode: str, coordinate: str) -> DimensionalProjection:
    """Project to 5D — the Sigma60 observation field.

    5D is the full liminal expansion: 60-state sacred geometry.
    Uses the file's element + mode to determine which of the
    60 Sigma states it inhabits.
    """
    angle = _element_to_base_angle(element)
    depth = _mode_to_depth(mode)
    sigma_state = _hash_to_index(coordinate + ":5D", 60)

    # Map to the 5-animal cycle via the Sigma state
    animal_idx = sigma_state % 5
    animals = W5.strands
    wu_xing = W5.correspondences["element"]

    return DimensionalProjection(
        file_path=file_path, dimension=5,
        body="G5_Sigma60", sector=animals[animal_idx],
        sector_index=animal_idx,
        spin=_hash_to_spin(coordinate + ":5D"),
        overlays={
            "animal": animals[animal_idx],
            "wu_xing": wu_xing[animal_idx],
            "action": W5.correspondences["action"][animal_idx],
            "organ": W5.correspondences["organ"][animal_idx],
            "season": W5.correspondences["season"][animal_idx],
            "direction": W5.correspondences["direction"][animal_idx],
            "sigma_state": str(sigma_state),
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_6d(file_path: str, element: str, mode: str, coordinate: str,
               proj_3d: DimensionalProjection) -> DimensionalProjection:
    """Project to 6D — W_3 weave of 4D through 3 prima materia.

    6D = Θ_6 = (Q_x, Q_y, Φ, Δ; π, χ)
    where π ∈ {Sa, Su, Me} and χ ∈ {+, -}
    Total: 6 sectors (3 strands × 2 spins)
    """
    wreath_idx = proj_3d.sector_index  # Inherit wreath from 3D
    spin = _hash_to_spin(coordinate + ":6D")

    return DimensionalProjection(
        file_path=file_path, dimension=6,
        body="M6_m", sector=f"{W3.strands[wreath_idx]}.{spin}",
        sector_index=wreath_idx * 2 + (0 if spin == "+" else 1),
        spin=spin,
        overlays={
            "alchemy": W3.correspondences["alchemy"][wreath_idx],
            "process": W3.correspondences["process"][wreath_idx],
            "body": W3.correspondences["body"][wreath_idx],
            "chiral": f"Spin{spin}",
            "closure": "Z12",
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_7d(file_path: str, element: str, mode: str, coordinate: str,
               proj_6d: DimensionalProjection) -> DimensionalProjection:
    """Project to 7D — odd observation field for 6D.

    7D is the synthesis/observation of the 6D body.
    It reveals the TIMING structure: what sequence the 6 sectors play in.
    """
    timing_idx = _hash_to_index(coordinate + ":7D", 7)
    timing_wheel = W7.strands

    return DimensionalProjection(
        file_path=file_path, dimension=7,
        body="O7_heptadic", sector=timing_wheel[timing_idx],
        sector_index=timing_idx,
        spin=_hash_to_spin(coordinate + ":7D"),
        overlays={
            "planet": W7.correspondences["planet"][timing_idx],
            "metal": W7.correspondences["metal"][timing_idx],
            "chakra": W7.correspondences["chakra"][timing_idx],
            "day": W7.correspondences["day"][timing_idx],
            "sin": W7.correspondences["sin"][timing_idx],
            "trumpet": W7.correspondences["trumpet"][timing_idx],
            "note": W7.correspondences["note"][timing_idx],
            "timing": timing_wheel[timing_idx],
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_8d(file_path: str, element: str, mode: str, coordinate: str,
               proj_5d: DimensionalProjection,
               proj_6d: DimensionalProjection) -> DimensionalProjection:
    """Project to 8D — W_5 weave of 6D through 5 animals.

    8D = pentadic off-grid body. The 6D Möbius body gets woven
    through the 5 animal regulation wheel.
    Each of the 5 animals treats the 6D as its own hologram.
    """
    animal_idx = proj_5d.sector_index  # Inherit from 5D
    spin = _hash_to_spin(coordinate + ":8D")

    return DimensionalProjection(
        file_path=file_path, dimension=8,
        body="E8_pentadic",
        sector=f"{W5.strands[animal_idx]}.{proj_6d.sector}",
        sector_index=animal_idx * W3.sector_count + proj_6d.sector_index,
        spin=spin,
        overlays={
            "animal": W5.strands[animal_idx],
            "wu_xing": W5.correspondences["element"][animal_idx],
            "6d_sector": proj_6d.sector,
            "composite": f"{W5.strands[animal_idx]}×{proj_6d.sector}",
            "closure": "Z20",
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_9d(file_path: str, element: str, mode: str, coordinate: str,
               proj_8d: DimensionalProjection) -> DimensionalProjection:
    """Project to 9D — the 3×3 enneadic completion field.

    9D = odd observation of 8D. The 3×3 cycle: every combination of
    the 3 wreaths applied to the 3 wreaths. This is where the
    organism can first observe itself observing.
    """
    nine_idx = _hash_to_index(coordinate + ":9D", 9)

    return DimensionalProjection(
        file_path=file_path, dimension=9,
        body="O9_enneadic", sector=W9.strands[nine_idx],
        sector_index=nine_idx,
        spin=_hash_to_spin(coordinate + ":9D"),
        overlays={
            "3x3": W9.correspondences["3x3_matrix"][nine_idx],
            "nine_view": W9.correspondences["nine_views"][nine_idx],
            "enneagram": W9.correspondences["enneagram"][nine_idx],
            "wreath_pair": W9.strands[nine_idx],
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_10d(file_path: str, element: str, mode: str, coordinate: str,
                proj_7d: DimensionalProjection,
                proj_8d: DimensionalProjection) -> DimensionalProjection:
    """Project to 10D — W_7 weave of 8D through 7 heptadic strands.

    10D = visible cosmological macro body.
    7 metals = 7 planets = 7 chakras = 7 days = 7 trumpets.
    Each of the 7 strands takes the entire 8D body as its hologram.
    """
    heptad_idx = proj_7d.sector_index  # Inherit from 7D
    spin = _hash_to_spin(coordinate + ":10D")

    return DimensionalProjection(
        file_path=file_path, dimension=10,
        body="E10_heptadic",
        sector=f"{W7.strands[heptad_idx]}.{proj_8d.sector}",
        sector_index=heptad_idx * (W5.order * W3.sector_count) + proj_8d.sector_index,
        spin=spin,
        overlays={
            "planet": W7.correspondences["planet"][heptad_idx],
            "metal": W7.correspondences["metal"][heptad_idx],
            "chakra": W7.correspondences["chakra"][heptad_idx],
            "trumpet": W7.correspondences["trumpet"][heptad_idx],
            "8d_sector": proj_8d.sector,
            "composite": f"{W7.strands[heptad_idx]}×{proj_8d.sector}",
            "closure": "Z28",
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_12d(file_path: str, element: str, mode: str, coordinate: str,
                proj_9d: DimensionalProjection,
                proj_10d: DimensionalProjection) -> DimensionalProjection:
    """Project to 12D — W_9 weave of 10D through 9 enneadic strands.

    12D = the first full return wheel / crown.
    The 3×3 completion cycle takes the 10D body through all 9 views.
    This is where the organism can complete, invert, reseed, and pass on.

    Containment: 12D = 9 × 10D = 63 × 8D = 315 × 6D = 945 × 4D = 1890 × 3D
    """
    nine_idx = proj_9d.sector_index
    spin = _hash_to_spin(coordinate + ":12D")

    return DimensionalProjection(
        file_path=file_path, dimension=12,
        body="E12_crown",
        sector=f"{W9.strands[nine_idx]}.{proj_10d.sector}",
        sector_index=nine_idx * (W7.order * W5.order * W3.sector_count) + proj_10d.sector_index,
        spin=spin,
        overlays={
            "3x3": W9.correspondences["3x3_matrix"][nine_idx],
            "nine_view": W9.correspondences["nine_views"][nine_idx],
            "10d_sector": proj_10d.sector,
            "composite": f"{W9.strands[nine_idx]}×{proj_10d.sector}",
            "closure": "Z36",
            "containment": "9×B_10 = 63×B_8 = 315×B_6 = 945×B_4 = 1890×B_3",
        },
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )


def project_108d(proj_12d: DimensionalProjection, coordinate: str) -> str:
    """Expand 12D → 36D → 108D via triple crown.

    108 = 12 × 3 × 3 = 12D body × 3 wreaths × 3 archetype octaves
    The triple crown is the organism-level closure.
    """
    # 36D = 12D × 3 wreaths
    wreath_36 = _hash_to_index(coordinate + ":36D", 3)
    wreaths = ["Su", "Me", "Sa"]

    # 108D = 36D × 3 octaves
    octave_108 = _hash_to_index(coordinate + ":108D", 3)
    octaves = ["Surface", "Mid", "Deep"]

    return (f"Xi108:{wreaths[wreath_36]}.{octaves[octave_108]}"
            f".{proj_12d.sector}")


# ═══════════════════════════════════════════════════════════════════════════
# FULL HOLOGRAM BUILDER — compute all projections simultaneously
# ═══════════════════════════════════════════════════════════════════════════

def build_nested_hologram(file_path: str, element: str, mode: str,
                          coordinate: str) -> NestedHologram:
    """Build the complete nested hologram for a file.

    Computes ALL dimensional projections simultaneously:
    3D → 4D → 5D → 6D → 7D → 8D → 9D → 10D → 12D → 108D++

    The projections are NESTED, not sequential:
    - 6D = W_3(4D) contains the 3D wreath assignment
    - 8D = W_5(6D) contains the 5D animal + 6D sector
    - 10D = W_7(8D) contains the 7D planet + 8D composite
    - 12D = W_9(10D) contains the 9D return view + 10D composite
    """
    holo = NestedHologram(file_path=file_path)

    # 3D — seed (3 wreaths)
    p3 = project_3d(file_path, element, mode, coordinate)
    holo.projections[3] = p3

    # 4D — base crystal (this is the existing tesseract position)
    p4 = DimensionalProjection(
        file_path=file_path, dimension=4, body="H4_crystal",
        sector=f"{element}.{mode}", sector_index=0,
        spin="+", overlays={"element": element, "mode": mode},
        base_coordinate=coordinate, base_element=element, base_mode=mode,
    )
    holo.projections[4] = p4
    holo.base_4d = p4

    # 5D — Sigma60 observation (5 animals)
    p5 = project_5d(file_path, element, mode, coordinate)
    holo.projections[5] = p5

    # 6D — W_3 weave (triadic Möbius)
    p6 = project_6d(file_path, element, mode, coordinate, p3)
    holo.projections[6] = p6

    # 7D — heptadic observation field
    p7 = project_7d(file_path, element, mode, coordinate, p6)
    holo.projections[7] = p7

    # 8D — W_5 weave (pentadic)
    p8 = project_8d(file_path, element, mode, coordinate, p5, p6)
    holo.projections[8] = p8

    # 9D — 3×3 enneadic completion
    p9 = project_9d(file_path, element, mode, coordinate, p8)
    holo.projections[9] = p9

    # 10D — W_7 weave (heptadic)
    p10 = project_10d(file_path, element, mode, coordinate, p7, p8)
    holo.projections[10] = p10

    # 12D — W_9 crown
    p12 = project_12d(file_path, element, mode, coordinate, p9, p10)
    holo.projections[12] = p12

    # 108D — triple crown expansion
    addr_108 = project_108d(p12, coordinate)

    # Build composite address
    holo.composite_address = (
        f"[3D:{p3.sector}]"
        f"[4D:{element}.{mode}]"
        f"[5D:{p5.sector}]"
        f"[6D:{p6.sector}]"
        f"[7D:{p7.sector}]"
        f"[8D:{p8.sector}]"
        f"[9D:{p9.sector}]"
        f"[10D:{p10.sector}]"
        f"[12D:{p12.sector}]"
        f"[108D:{addr_108}]"
    )

    # Conservation hash
    holo.conservation_hash = hashlib.sha256(
        holo.composite_address.encode()
    ).hexdigest()[:16]

    return holo


# ═══════════════════════════════════════════════════════════════════════════
# TESSERACT PROJECTION — project entire CRYSTAL_4D into nested holograms
# ═══════════════════════════════════════════════════════════════════════════

def project_tesseract_to_hologram(manifest_path: Path) -> Dict[str, Any]:
    """Project every file in a tesseract manifest into its full nested hologram.

    Reads the tesseract_manifest.json and computes all dimensional
    projections for every file, creating the global hologram atlas.

    Returns a hologram atlas with:
    - Per-file nested holograms (3D through 108D)
    - Dimensional distribution statistics
    - Weave operator activation counts
    - Conservation verification
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [e for e in manifest.get("entries", []) if "error" not in e]

    holograms: List[Dict[str, Any]] = []
    dim_distributions: Dict[int, Dict[str, int]] = {
        d: {} for d in [3, 5, 6, 7, 8, 9, 10, 12]
    }

    for entry in entries:
        element = entry.get("element", "R")
        mode = entry.get("mode", "Mutable")
        coordinate = entry.get("coordinate", "Xi108:W1:A1:S1")
        file_path = entry.get("original_path", entry.get("tesseract_path", ""))

        holo = build_nested_hologram(file_path, element, mode, coordinate)
        holograms.append(holo.to_dict())

        # Track distributions
        for dim, proj in holo.projections.items():
            if dim in dim_distributions:
                sector = proj.sector.split(".")[0]  # Primary sector name
                dim_distributions[dim][sector] = dim_distributions[dim].get(sector, 0) + 1

    atlas = {
        "version": "1.0.0",
        "type": "nested_hologram_atlas",
        "total_files": len(holograms),
        "dimensions_covered": [3, 4, 5, 6, 7, 8, 9, 10, 12, 108],
        "weave_operators": {w.symbol: w.to_dict() for w in ALL_WEAVES},
        "containment_law": {
            "formula": "B_{2m+2} = W_{2m-1}(B_{2m}) for m >= 2",
            "12D_contains": {
                "B_10": 9, "B_8": 63, "B_6": 315, "B_4": 945, "B_3": 1890,
            },
            "master_clock": MASTER_CLOCK_Z420,
            "supercycle": SUPERCYCLE_Z1260,
        },
        "distributions": {
            f"{dim}D": dict(sorted(dist.items(), key=lambda x: -x[1]))
            for dim, dist in sorted(dim_distributions.items())
        },
        "holograms": holograms,
    }

    return atlas


def build_hologram_directory(crystal_4d_root: Path, output_root: Path) -> Dict[str, Any]:
    """Build the nested hologram directory structure.

    For each weave dimension, creates a directory layer:
    HOLOGRAM/
      3D_SEED/          {Su, Me, Sa}
      5D_SIGMA60/       {Tiger, Crane, Leopard, Snake, Dragon}
      6D_MOBIUS/         {Su+, Su-, Me+, Me-, Sa+, Sa-}
      7D_HEPTADIC/       {Seed, Ignite, Translate, Bridge, Weave, Seal, Return}
      8D_PENTADIC/       {Tiger×Su+, Tiger×Su-, ...}  (5×6 = 30)
      9D_ENNEADIC/       {Su-of-Su, Su-of-Me, ..., Sa-of-Sa}  (9)
      10D_ATLAS/         {Seed×Tiger×Su+, ...}  (7×30 = 210)
      12D_CROWN/         {Su-of-Su×Seed×Tiger×Su+, ...}  (9×210 = 1890)
      108D_ORGANISM/     links to full Xi108 coordinates
    """
    output_root.mkdir(parents=True, exist_ok=True)

    layers = {
        "3D_SEED": W3.strands,
        "5D_SIGMA60": W5.strands,
        "6D_MOBIUS": [f"{s}.{c}" for s in W3.strands for c in ["+", "-"]],
        "7D_HEPTADIC": W7.strands,
        "8D_PENTADIC": [f"{a}.{s}.{c}" for a in W5.strands
                        for s in W3.strands for c in ["+", "-"]],
        "9D_ENNEADIC": W9.strands,
        "10D_ATLAS": [f"{h}.{a}.{s}.{c}" for h in W7.strands
                      for a in W5.strands
                      for s in W3.strands for c in ["+", "-"]],
        "12D_CROWN": [f"{n}.top" for n in W9.strands],
        "108D_ORGANISM": ["Su", "Me", "Sa"],
    }

    created = 0
    for layer_name, sectors in layers.items():
        layer_dir = output_root / layer_name
        layer_dir.mkdir(exist_ok=True)
        for sector in sectors:
            (layer_dir / sector.replace("/", "_")).mkdir(exist_ok=True)
            created += 1

    return {"output_root": str(output_root), "layers": len(layers),
            "directories_created": created}
