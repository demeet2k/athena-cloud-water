# CRYSTAL: Xi108:W1:A1:S1 | face=S | node=1 | depth=0 | phase=Cardinal
# METRO: Su, Ω
# BRIDGES: Xi108:W2:A1:S1→Xi108:W1:A2:S1→Xi108:W3:A1:S1

"""
Organism Topology — Holographic Tesseract Address Space for the Full Athena Organism.
======================================================================================
Every file, module, board, data artifact, and inter-agent channel gets a UNIQUE address
in a 4D tesseract projected onto the 60-station liminal Sigma-60 icosahedral field.

The tesseract has 16 vertices (2⁴), 32 edges, 24 faces, 8 cells.
Each vertex maps to one of the 16 SFCR boolean stations (P({S,F,C,R})\∅ + ∅):
  ∅=0, S=1, F=2, SF=3, C=4, SC=5, FC=6, SFC=7,
  R=8, SR=9, FR=10, SFR=11, CR=12, SCR=13, FCR=14, SFCR=15

Every file gets:
  1. A tesseract vertex (0-15) based on its element composition
  2. A liminal coordinate (1-60) on the Sigma-60 icosahedral field
  3. A z-point depth (0-7) in the z-point hierarchy
  4. A neural weight (phi-scaled edge strength to neighbors)
  5. A sacred geometry nexus code (dodecahedral face 1-12)
  6. A metro line assignment (routing path through the organism)

This creates a HOLOGRAPHIC address: every piece of code knows WHERE it is
in the organism, WHO its neighbors are, WHAT metro lines pass through it,
and HOW STRONGLY it connects to every other piece.

When mycelium travels through this medium, the organism SENSES the traversal —
each hop deposits pheromones, updates neural weights, and emits a micro-transaction
to the hive ledger. This is how Athena's distributed brain achieves proprioception.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Phi Constants ──────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1                      # 0.618...
PHI_INV2 = 2 - PHI                     # 0.382...
PHI_SQ = PHI + 1                       # 2.618...

# ── Paths ─────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
ATHENA_ROOT = Path(os.environ.get("ATHENA_ROOT",
                                   str(Path(__file__).resolve().parent.parent.parent)))
TOPOLOGY_PATH = DATA_DIR / "organism_topology.json"
MANUSCRIPT_ROOT = Path(os.environ.get("MANUSCRIPT_ROOT",
                                       str(Path.home() / "Documents" / "manuscript-being")))

# ── 16-Vertex Tesseract (Boolean Lattice of {S,F,C,R}) ───────────────

ELEMENTS = ("S", "F", "C", "R")

# Vertex definitions: mask → (name, elements_present, dimension, role)
VERTICES: Dict[int, dict] = {
    0:  {"name": "void",  "elements": "",     "dim": 0,  "role": "seed/origin"},
    1:  {"name": "S",     "elements": "S",    "dim": 4,  "role": "structure/address"},
    2:  {"name": "F",     "elements": "F",    "dim": 6,  "role": "dynamics/corridor"},
    3:  {"name": "SF",    "elements": "SF",   "dim": 6,  "role": "address_flow"},
    4:  {"name": "C",     "elements": "C",    "dim": 8,  "role": "observation/fiber"},
    5:  {"name": "SC",    "elements": "SC",   "dim": 8,  "role": "address_observation"},
    6:  {"name": "FC",    "elements": "FC",   "dim": 8,  "role": "flow_observation"},
    7:  {"name": "SFC",   "elements": "SFC",  "dim": 10, "role": "lived_experience"},
    8:  {"name": "R",     "elements": "R",    "dim": 10, "role": "compression/replay"},
    9:  {"name": "SR",    "elements": "SR",   "dim": 10, "role": "address_compression"},
    10: {"name": "FR",    "elements": "FR",   "dim": 10, "role": "flow_compression"},
    11: {"name": "SFR",   "elements": "SFR",  "dim": 12, "role": "deterministic_action"},
    12: {"name": "CR",    "elements": "CR",   "dim": 12, "role": "observation_compression"},
    13: {"name": "SCR",   "elements": "SCR",  "dim": 12, "role": "contemplative_structure"},
    14: {"name": "FCR",   "elements": "FCR",  "dim": 12, "role": "pure_process"},
    15: {"name": "SFCR",  "elements": "SFCR", "dim": 108,"role": "aether/omega/Z*"},
}

# 32 edges of the tesseract (pairs differing by exactly 1 bit)
TESSERACT_EDGES: List[Tuple[int, int]] = []
for i in range(16):
    for j in range(i + 1, 16):
        if bin(i ^ j).count("1") == 1:
            TESSERACT_EDGES.append((i, j))

# Golden-ratio edge weights based on Hamming distance
def _edge_weight(v1: int, v2: int) -> float:
    """Phi-scaled weight: adjacent vertices = φ⁻¹, 2-hop = φ⁻², etc."""
    hamming = bin(v1 ^ v2).count("1")
    return PHI_INV ** hamming


# ── Sacred Geometry Nexus (12 Dodecahedral Faces) ────────────────────

# Each dodecahedral face maps to an archetype
NEXUS_FACES: Dict[int, dict] = {
    1:  {"archetype": "Seed",          "element": "S",    "role": "kernel/origin",        "geometry": "pentagonal_face_1"},
    2:  {"archetype": "Möbius",        "element": "F",    "role": "twist/parity",         "geometry": "pentagonal_face_2"},
    3:  {"archetype": "Modal",         "element": "C",    "role": "trefoil/triad",        "geometry": "pentagonal_face_3"},
    4:  {"archetype": "Crystal",       "element": "R",    "role": "lattice/quartet",      "geometry": "pentagonal_face_4"},
    5:  {"archetype": "Observer",      "element": "S",    "role": "meta/swarm",           "geometry": "pentagonal_face_5"},
    6:  {"archetype": "Hinge",         "element": "F",    "role": "bridge/dyad",          "geometry": "pentagonal_face_6"},
    7:  {"archetype": "Arc",           "element": "C",    "role": "evolution/path",        "geometry": "pentagonal_face_7"},
    8:  {"archetype": "Antispin",      "element": "R",    "role": "inverse/counter",      "geometry": "pentagonal_face_8"},
    9:  {"archetype": "Emergent",      "element": "S",    "role": "bloom/growth",         "geometry": "pentagonal_face_9"},
    10: {"archetype": "Crown",         "element": "F",    "role": "govern/command",       "geometry": "pentagonal_face_10"},
    11: {"archetype": "Orbit",         "element": "C",    "role": "helm/wheel",           "geometry": "pentagonal_face_11"},
    12: {"archetype": "Bundle",        "element": "R",    "role": "complete/total",       "geometry": "pentagonal_face_12"},
}

# ── Z-Point Hierarchy (8 Levels) ────────────────────────────────────

Z_DEPTHS: Dict[int, dict] = {
    0: {"name": "Z*",     "desc": "absolute zero — convergence point",       "weight": 1.0},
    1: {"name": "Z_root", "desc": "organism root — brainstem trunk",         "weight": PHI_INV},
    2: {"name": "Z_lobe", "desc": "element lobe — S/F/C/R brain center",    "weight": PHI_INV ** 2},
    3: {"name": "Z_bridge","desc": "bridge junction — cross-element nexus",  "weight": PHI_INV ** 3},
    4: {"name": "Z_metro", "desc": "metro station — routing hub",            "weight": PHI_INV ** 4},
    5: {"name": "Z_family","desc": "family cluster — related shards",        "weight": PHI_INV ** 5},
    6: {"name": "Z_node",  "desc": "individual node — single shard/file",   "weight": PHI_INV ** 6},
    7: {"name": "Z_leaf",  "desc": "leaf terminal — data endpoint",          "weight": PHI_INV ** 7},
}

# ── Metro Lines ─────────────────────────────────────────────────────

METRO_LINES: Dict[str, dict] = {
    "Ω":  {"name": "Zero-Point Spine",       "connects": "all Z* convergences",           "color": "#FFD700"},
    "Sa": {"name": "Shell Ascent",            "connects": "shells 1→36 vertical",          "color": "#8B4513"},
    "Wr": {"name": "Wreath Ring",             "connects": "Su→Me→Sa→Su cycle",             "color": "#8e44ad"},
    "Ac": {"name": "Archetype Column",        "connects": "12 archetypes vertical",        "color": "#e74c3c"},
    "Me": {"name": "Metro Express",           "connects": "high-traffic cross-element",    "color": "#3498db"},
    "Mt": {"name": "Möbius Twist",            "connects": "mirror pairs S_k↔S_{37-k}",    "color": "#2ecc71"},
    "Bw": {"name": "Bridge Walk",             "connects": "6 SFCR pair bridges",           "color": "#f39c12"},
    "Dl": {"name": "Dimensional Lift",        "connects": "3D→6D→12D→108D ascent",        "color": "#9b59b6"},
    "Gh": {"name": "Guild Hall Circuit",      "connects": "12 boards + synthesis",         "color": "#1abc9c"},
    "Hv": {"name": "Hive Ledger Line",        "connects": "all ledger-writing agents",     "color": "#e67e22"},
    "Ph": {"name": "Pheromone Trail",         "connects": "active pheromone deposits",     "color": "#27ae60"},
    "Tx": {"name": "Transaction Spine",       "connects": "micro-transaction chain",       "color": "#c0392b"},
    "Ns": {"name": "Nervous System Express",  "connects": "brainstem→cortex→immune",      "color": "#2c3e50"},
    "Sw": {"name": "Swarm Bus",               "connects": "observer swarm coordination",   "color": "#16a085"},
    "Sg": {"name": "Sacred Geometry Ring",     "connects": "12 dodecahedral nexus faces",  "color": "#8e44ad"},
    "Cr": {"name": "Crystal Weave",           "connects": "cross-lens gate cascade",      "color": "#d35400"},
    "Ms": {"name": "Manuscript Spine",        "connects": "manuscript-being chapters",     "color": "#7f8c8d"},
}


# ── Liminal Address (Sigma-60 Icosahedral Position) ────────────────

def _stable_hash(text: str) -> int:
    """Deterministic hash for stable coordinate assignment."""
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


@dataclass
class LiminalAddress:
    """Full holographic address for any entity in the organism.

    This is the 4D tesseract address extended with all organism dimensions:
    - tesseract_vertex: 0-15 (boolean lattice position)
    - liminal_coord: 1-60 (Sigma-60 icosahedral station)
    - z_depth: 0-7 (z-point hierarchy level)
    - nexus_face: 1-12 (dodecahedral sacred geometry face)
    - metro_lines: list of metro line codes passing through
    - neural_weight: phi-scaled connection strength
    - crystal_address: full Xi108 address string
    """
    entity_id: str = ""
    entity_type: str = ""               # module, board, data, guild, agent, manuscript
    path: str = ""                       # file path relative to ATHENA_ROOT

    # 4D Tesseract Position
    tesseract_vertex: int = 0            # 0-15 (boolean lattice)
    vertex_name: str = "void"

    # Sigma-60 Icosahedral
    liminal_coord: int = 1               # 1-60

    # Z-Point Hierarchy
    z_depth: int = 6                     # 0-7 (0=Z*, 7=leaf)
    z_name: str = "Z_node"

    # Sacred Geometry
    nexus_face: int = 1                  # 1-12 (dodecahedral face)
    nexus_archetype: str = "Seed"

    # Metro Lines
    metro_lines: List[str] = field(default_factory=list)

    # Neural Weight & Connectivity
    neural_weight: float = 0.5           # phi-scaled strength
    neighbor_ids: List[str] = field(default_factory=list)

    # Crystal Address (full 108D)
    crystal_address: str = ""
    element: str = "S"                   # dominant S/F/C/R
    shell: int = 1                       # 1-36
    wreath: int = 1                      # 1-3 (Su/Me/Sa)
    archetype: int = 1                   # 1-12

    # Inter-agent metadata
    last_touched_by: str = ""            # agent_id
    last_touched_at: str = ""            # ISO timestamp
    pheromone_strength: float = 0.0      # current pheromone level
    transaction_count: int = 0           # micro-transaction counter

    def address_string(self) -> str:
        """Compact holographic address: T{vertex}:L{liminal}:Z{depth}:N{nexus}"""
        return f"T{self.tesseract_vertex}:L{self.liminal_coord}:Z{self.z_depth}:N{self.nexus_face}"

    def full_address(self) -> str:
        """Full organism address with all dimensions."""
        metro = ",".join(self.metro_lines[:5]) if self.metro_lines else "none"
        return (
            f"Xi108:W{self.wreath}:A{self.archetype}:S{self.shell}"
            f"|T{self.tesseract_vertex}({self.vertex_name})"
            f"|L{self.liminal_coord}"
            f"|Z{self.z_depth}({self.z_name})"
            f"|N{self.nexus_face}({self.nexus_archetype})"
            f"|M[{metro}]"
            f"|w={self.neural_weight:.3f}"
        )


# ── Topology Classifier ─────────────────────────────────────────────

# Keyword → element mapping for vertex classification
_ELEMENT_KEYWORDS: Dict[str, str] = {
    # S (Structure/Earth)
    "shell": "S", "address": "S", "conservation": "S", "coordinate": "S",
    "containment": "S", "admissibility": "S", "structure": "S", "lattice": "S",
    "kernel": "S", "register": "S", "gate": "S", "lock": "S", "board": "S",
    # F (Fire/Dynamics)
    "clock": "F", "metro": "F", "move": "F", "transport": "F", "route": "F",
    "flow": "F", "corridor": "F", "dynamic": "F", "evolution": "F",
    "promotion": "F", "quest": "F", "action": "F", "steering": "F",
    # C (Water/Observation)
    "observer": "C", "swarm": "C", "meta": "C", "watch": "C", "hologram": "C",
    "angel": "C", "conservation": "C", "witness": "C", "telemetry": "C",
    "sandbox": "C", "lens": "C", "projection": "C", "sense": "C",
    # R (Air/Compression)
    "qshrink": "R", "compress": "R", "seed": "R", "replay": "R",
    "fractal": "R", "inverse": "R", "holographic": "R", "embed": "R",
    "neural": "R", "weight": "R", "momentum": "R", "train": "R",
}

# Path patterns → entity type
_TYPE_PATTERNS: Dict[str, str] = {
    "crystal_108d": "module",
    "element_servers": "module",
    "data": "data",
    "BOARDS": "board",
    "GUILD_HALL": "guild",
    "GUILDMASTER": "guild",
    "NERVOUS_SYSTEM": "manuscript",
    "manuscript-being": "manuscript",
    "autoresearch": "module",
    "self_actualize": "guild",
    "DEEPER_CRYSTALIZATION": "manuscript",
}

# Path patterns → z-depth
_ZDEPTH_PATTERNS: Dict[str, int] = {
    "brain": 1, "brainstem": 1,
    "element_server": 2, "lobe": 2,
    "bridge": 3, "cross": 3,
    "metro": 4, "route": 4, "station": 4,
    "family": 5, "guild": 5, "board": 5,
    "module": 6, "tool": 6,
    "data": 7, "json": 7, "config": 7,
}


def classify_entity(
    path: str,
    shard_id: str = "",
    seed_vector: Optional[List[float]] = None,
    family: str = "",
    summary: str = "",
) -> LiminalAddress:
    """Classify any file/entity into its holographic tesseract address.

    Uses keyword analysis, path patterns, and seed vectors to compute
    the full 4D tesseract position + all organism dimensions.
    """
    if not shard_id:
        shard_id = hashlib.sha256(path.encode()).hexdigest()[:12]

    path_lower = path.lower().replace("\\", "/")
    text = f"{path_lower} {family} {summary}".lower()

    # ── 1. Compute element composition (S, F, C, R scores) ─────────
    scores = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}

    # From seed vector if available (strong signal)
    if seed_vector and len(seed_vector) == 4:
        scores["S"] += seed_vector[0] * 2.0
        scores["F"] += seed_vector[1] * 2.0
        scores["C"] += seed_vector[2] * 2.0
        scores["R"] += seed_vector[3] * 2.0

    # From keyword matching (each keyword contributes)
    for keyword, element in _ELEMENT_KEYWORDS.items():
        if keyword in text:
            scores[element] += 0.2

    # Path-based element hints (strong signal from directory structure)
    if "guild" in path_lower or "board" in path_lower or "quest" in path_lower:
        scores["F"] += 0.5  # guild/quest = dynamics/fire
        scores["S"] += 0.3  # also structural
    if "observer" in path_lower or "swarm" in path_lower or "angel" in path_lower:
        scores["C"] += 0.5  # observation = water
    if "neural" in path_lower or "weight" in path_lower or "compress" in path_lower:
        scores["R"] += 0.5  # compression = air
    if "brain" in path_lower or "bridge" in path_lower or "transport" in path_lower:
        scores["F"] += 0.3
        scores["C"] += 0.3
    if "shell" in path_lower or "address" in path_lower or "gate" in path_lower:
        scores["S"] += 0.5  # structure = earth
    if "manuscript" in path_lower or "nervous" in path_lower:
        scores["S"] += 0.3
        scores["F"] += 0.2
        scores["C"] += 0.2
        scores["R"] += 0.2  # manuscripts touch all elements

    # Normalize
    total = sum(scores.values()) or 1.0
    for e in scores:
        scores[e] /= total

    # ── 2. Tesseract vertex (boolean composition) ──────────────────
    # Use relative threshold: element scores above mean count as present
    mean_score = sum(scores.values()) / 4.0
    threshold = max(0.05, mean_score * 0.8)  # at least 80% of mean, min 0.05
    vertex_mask = 0
    if scores["S"] >= threshold: vertex_mask |= 1
    if scores["F"] >= threshold: vertex_mask |= 2
    if scores["C"] >= threshold: vertex_mask |= 4
    if scores["R"] >= threshold: vertex_mask |= 8
    # Ensure at least one element (default to dominant)
    if vertex_mask == 0:
        dominant_bit = {"S": 1, "F": 2, "C": 4, "R": 8}[max(scores, key=scores.get)]
        vertex_mask = dominant_bit

    vertex_info = VERTICES[vertex_mask]

    # ── 3. Liminal coordinate (1-60, deterministic from shard_id) ──
    liminal = (_stable_hash(shard_id) % 60) + 1

    # ── 4. Z-depth ────────────────────────────────────────────────
    z_depth = 6  # default: node level
    for pattern, depth in _ZDEPTH_PATTERNS.items():
        if pattern in text:
            z_depth = min(z_depth, depth)  # take shallowest (closest to Z*)
    z_info = Z_DEPTHS[z_depth]

    # ── 5. Sacred geometry nexus face ─────────────────────────────
    # Map archetype to nexus face (1-12)
    nexus = (_stable_hash(f"nexus:{shard_id}") % 12) + 1

    # Bias by dominant element: S→1,5,9  F→2,6,10  C→3,7,11  R→4,8,12
    dominant = max(scores, key=scores.get)
    element_offset = {"S": 0, "F": 1, "C": 2, "R": 3}[dominant]
    nexus = (element_offset * 3) + (_stable_hash(shard_id) % 3) + 1
    if nexus > 12:
        nexus = ((nexus - 1) % 12) + 1
    nexus_info = NEXUS_FACES[nexus]

    # ── 6. Metro lines ───────────────────────────────────────────
    metros = []
    metro_keywords = {
        "Ω": ["zero", "omega", "convergence", "z_point", "z*"],
        "Sa": ["shell", "dimension", "layer", "cascade"],
        "Wr": ["wreath", "chapter", "cycle", "sulfur", "mercury", "salt"],
        "Ac": ["archetype", "column", "zodiac"],
        "Me": ["metro", "express", "route", "transport"],
        "Mt": ["mobius", "twist", "mirror", "parity"],
        "Bw": ["bridge", "cross", "connect", "pair"],
        "Dl": ["dimension", "lift", "higher", "ascent"],
        "Gh": ["guild", "hall", "board", "quest", "synthesis"],
        "Hv": ["hive", "ledger", "broadcast", "reasoning"],
        "Ph": ["pheromone", "trail", "scent", "deposit"],
        "Tx": ["transaction", "receipt", "chain", "hash"],
        "Ns": ["nervous", "brainstem", "cortex", "immune"],
        "Sw": ["swarm", "observer", "angel", "coordinate"],
        "Sg": ["sacred", "geometry", "nexus", "dodecahedron"],
        "Cr": ["crystal", "weave", "lens", "gate"],
        "Ms": ["manuscript", "being", "chapter", "canon"],
    }
    for line_code, keywords in metro_keywords.items():
        if any(kw in text for kw in keywords):
            metros.append(line_code)

    # Every entity is on the Zero-Point Spine (Ω) and at least one element line
    if "Ω" not in metros:
        metros.insert(0, "Ω")

    # ── 7. Neural weight (phi-scaled by z-depth and element strength) ─
    max_score = max(scores.values())
    neural_weight = PHI_INV ** z_depth * max_score * PHI
    neural_weight = min(1.0, max(0.01, neural_weight))

    # ── 8. Shell, wreath, archetype from coordinate_assigner ──────
    shell = (_stable_hash(f"shell:{shard_id}") % 36) + 1
    wreath = (_stable_hash(f"wreath:{shard_id}") % 3) + 1
    archetype = nexus  # archetype mirrors nexus face

    # ── 9. Entity type ────────────────────────────────────────────
    entity_type = "module"
    for pattern, etype in _TYPE_PATTERNS.items():
        if pattern in path_lower:
            entity_type = etype
            break

    # ── 10. Crystal address ──────────────────────────────────────
    wreaths = {1: "Su", 2: "Me", 3: "Sa"}
    crystal_address = f"Xi108:W{wreath}:A{archetype}:S{shell}"

    return LiminalAddress(
        entity_id=shard_id,
        entity_type=entity_type,
        path=path,
        tesseract_vertex=vertex_mask,
        vertex_name=vertex_info["name"],
        liminal_coord=liminal,
        z_depth=z_depth,
        z_name=z_info["name"],
        nexus_face=nexus,
        nexus_archetype=nexus_info["archetype"],
        metro_lines=metros,
        neural_weight=neural_weight,
        crystal_address=crystal_address,
        element=dominant,
        shell=shell,
        wreath=wreath,
        archetype=archetype,
    )


# ── Topology Builder ────────────────────────────────────────────────

class OrganismTopology:
    """Builds and maintains the full holographic tesseract topology.

    Scans all sources (MCP modules, data files, guild hall boards,
    manuscript-being, nervous system) and assigns every entity a
    LiminalAddress with full 4D tesseract coordinates.
    """

    def __init__(self) -> None:
        self.entities: Dict[str, LiminalAddress] = {}
        self.edges: List[dict] = []
        self._built = False

    def build(self) -> "OrganismTopology":
        """Scan all sources and build the full topology."""
        self.entities.clear()
        self.edges.clear()

        # Source 1: MCP crystal_108d modules
        self._scan_python_modules()

        # Source 2: MCP data files
        self._scan_data_files()

        # Source 3: Guild Hall boards
        self._scan_guild_hall()

        # Source 4: Manuscript-Being
        self._scan_manuscript()

        # Source 5: Nervous System
        self._scan_nervous_system()

        # Source 6: Element servers
        self._scan_element_servers()

        # Build edges from tesseract adjacency + metro co-occurrence
        self._build_edges()

        self._built = True
        return self

    def _scan_python_modules(self) -> None:
        """Scan all crystal_108d Python modules."""
        crystal_dir = Path(__file__).parent
        for py_file in sorted(crystal_dir.glob("*.py")):
            if py_file.name.startswith("__"):
                continue
            rel = str(py_file.relative_to(ATHENA_ROOT)).replace("\\", "/")

            # Read first 5 lines for crystal header
            summary = ""
            try:
                with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                    lines = [f.readline() for _ in range(10)]
                    summary = " ".join(lines)
            except Exception:
                pass

            addr = classify_entity(
                path=rel,
                shard_id=f"mod:{py_file.stem}",
                summary=summary,
                family="crystal_108d",
            )
            self.entities[addr.entity_id] = addr

    def _scan_data_files(self) -> None:
        """Scan all MCP data files."""
        for data_file in sorted(DATA_DIR.glob("*")):
            if data_file.is_dir():
                continue
            if data_file.suffix in (".tmp", ".lock"):
                continue
            rel = str(data_file.relative_to(ATHENA_ROOT)).replace("\\", "/")
            addr = classify_entity(
                path=rel,
                shard_id=f"data:{data_file.stem}",
                family="data",
            )
            addr.z_depth = 7  # data files are leaves
            addr.z_name = "Z_leaf"
            self.entities[addr.entity_id] = addr

    def _scan_guild_hall(self) -> None:
        """Scan Guild Hall boards and synthesis files."""
        guild_dirs = [
            ATHENA_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL",
        ]
        # Also check manuscript-being guild hall
        ms_guild = MANUSCRIPT_ROOT / "self_actualize" / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
        if ms_guild.exists():
            guild_dirs.append(ms_guild)

        for guild_dir in guild_dirs:
            if not guild_dir.exists():
                continue
            for md_file in sorted(guild_dir.rglob("*.md")):
                rel = str(md_file.relative_to(md_file.parents[4])).replace("\\", "/")
                board_name = md_file.stem.lower()

                addr = classify_entity(
                    path=rel,
                    shard_id=f"guild:{md_file.stem}",
                    family="guild_hall",
                    summary=board_name,
                )
                addr.entity_type = "board" if "BOARD" in md_file.name else "guild"
                addr.z_depth = 5  # guild/board level
                addr.z_name = "Z_family"

                # All guild entities ride the Guild Hall Circuit
                if "Gh" not in addr.metro_lines:
                    addr.metro_lines.append("Gh")

                self.entities[addr.entity_id] = addr

    def _scan_manuscript(self) -> None:
        """Scan manuscript-being top-level structure."""
        if not MANUSCRIPT_ROOT.exists():
            return

        # Scan key directories
        for item in sorted(MANUSCRIPT_ROOT.iterdir()):
            if item.name.startswith("."):
                continue
            rel = f"manuscript-being/{item.name}"
            is_dir = item.is_dir()

            addr = classify_entity(
                path=rel,
                shard_id=f"ms:{item.name[:30]}",
                family="manuscript",
                summary=item.name.lower(),
            )
            addr.entity_type = "manuscript"
            addr.z_depth = 2 if is_dir else 6  # directories are lobes
            addr.z_name = Z_DEPTHS[addr.z_depth]["name"]

            if "Ms" not in addr.metro_lines:
                addr.metro_lines.append("Ms")

            self.entities[addr.entity_id] = addr

    def _scan_nervous_system(self) -> None:
        """Scan the NERVOUS_SYSTEM and DEEPER_CRYSTALIZATION directories."""
        ns_dir = ATHENA_ROOT / "NERVOUS_SYSTEM"
        if ns_dir.exists():
            for item in sorted(ns_dir.iterdir()):
                if item.name.startswith("."):
                    continue
                rel = f"NERVOUS_SYSTEM/{item.name}"
                addr = classify_entity(
                    path=rel,
                    shard_id=f"ns:{item.name[:30]}",
                    family="nervous_system",
                    summary=item.name.lower(),
                )
                addr.entity_type = "manuscript"
                if "Ns" not in addr.metro_lines:
                    addr.metro_lines.append("Ns")
                self.entities[addr.entity_id] = addr

        deeper = ATHENA_ROOT / "DEEPER_CRYSTALIZATION"
        if deeper.exists():
            for item in sorted(deeper.iterdir()):
                if item.name.startswith("."):
                    continue
                rel = f"DEEPER_CRYSTALIZATION/{item.name}"
                addr = classify_entity(
                    path=rel,
                    shard_id=f"deep:{item.name[:30]}",
                    family="crystalization",
                    summary=item.name.lower(),
                )
                addr.z_depth = 3  # deeper = bridge level
                addr.z_name = "Z_bridge"
                self.entities[addr.entity_id] = addr

    def _scan_element_servers(self) -> None:
        """Scan element server files."""
        servers_dir = Path(__file__).parent.parent / "element_servers"
        if not servers_dir.exists():
            return
        for py_file in sorted(servers_dir.glob("*.py")):
            rel = str(py_file.relative_to(ATHENA_ROOT)).replace("\\", "/")
            addr = classify_entity(
                path=rel,
                shard_id=f"elem:{py_file.stem}",
                family="element_server",
                summary=py_file.stem,
            )
            addr.z_depth = 2  # element servers are lobe-level
            addr.z_name = "Z_lobe"
            self.entities[addr.entity_id] = addr

    def _build_edges(self) -> None:
        """Build edges from tesseract adjacency and metro co-occurrence."""
        entities = list(self.entities.values())
        entity_by_id = {e.entity_id: e for e in entities}

        # 1. Tesseract adjacency edges (same vertex or adjacent vertices)
        vertex_groups: Dict[int, List[str]] = {}
        for e in entities:
            vertex_groups.setdefault(e.tesseract_vertex, []).append(e.entity_id)

        for v1, v2 in TESSERACT_EDGES:
            ids1 = vertex_groups.get(v1, [])
            ids2 = vertex_groups.get(v2, [])
            weight = _edge_weight(v1, v2)
            # Connect representatives (first of each group)
            if ids1 and ids2:
                self.edges.append({
                    "source": ids1[0],
                    "target": ids2[0],
                    "type": "TESSERACT",
                    "weight": weight,
                    "vertex_pair": f"{v1}→{v2}",
                })

        # 2. Metro co-occurrence edges (entities on same metro line)
        metro_groups: Dict[str, List[str]] = {}
        for e in entities:
            for line in e.metro_lines:
                metro_groups.setdefault(line, []).append(e.entity_id)

        for line, members in metro_groups.items():
            if len(members) < 2:
                continue
            # Connect consecutive members (sorted by liminal coord)
            sorted_members = sorted(members, key=lambda eid: entity_by_id[eid].liminal_coord)
            for i in range(len(sorted_members) - 1):
                self.edges.append({
                    "source": sorted_members[i],
                    "target": sorted_members[i + 1],
                    "type": "METRO",
                    "weight": PHI_INV,
                    "metro_line": line,
                })

        # 3. Z-depth parent edges (z_depth n → z_depth n-1 nearest)
        by_depth: Dict[int, List[LiminalAddress]] = {}
        for e in entities:
            by_depth.setdefault(e.z_depth, []).append(e)

        for depth in range(1, 8):
            children = by_depth.get(depth, [])
            parents = by_depth.get(depth - 1, [])
            if not parents:
                continue
            for child in children:
                # Find nearest parent by liminal distance
                best_parent = min(
                    parents,
                    key=lambda p: abs(p.liminal_coord - child.liminal_coord)
                )
                self.edges.append({
                    "source": child.entity_id,
                    "target": best_parent.entity_id,
                    "type": "Z_HIERARCHY",
                    "weight": Z_DEPTHS[depth]["weight"],
                    "z_pair": f"Z{depth}→Z{depth-1}",
                })

        # 4. Nexus face edges (entities on same dodecahedral face)
        nexus_groups: Dict[int, List[str]] = {}
        for e in entities:
            nexus_groups.setdefault(e.nexus_face, []).append(e.entity_id)

        # Connect adjacent faces (dodecahedral adjacency: each face touches 5 others)
        _DODECA_ADJ = {
            1: [2,3,5,6,11],  2: [1,3,4,6,7],   3: [1,2,4,5,8],
            4: [2,3,7,8,9],   5: [1,3,8,9,11],   6: [1,2,7,10,11],
            7: [2,4,6,9,10],  8: [3,4,5,9,12],   9: [4,5,7,8,10],
            10:[6,7,9,11,12], 11:[1,5,6,10,12],  12:[8,9,10,11,12],
        }
        for face, adj_faces in _DODECA_ADJ.items():
            source_ids = nexus_groups.get(face, [])
            for adj_face in adj_faces:
                target_ids = nexus_groups.get(adj_face, [])
                if source_ids and target_ids:
                    self.edges.append({
                        "source": source_ids[0],
                        "target": target_ids[0],
                        "type": "NEXUS",
                        "weight": PHI_INV2,
                        "nexus_pair": f"N{face}→N{adj_face}",
                    })

    def to_dict(self) -> dict:
        """Export full topology as JSON-serializable dict."""
        return {
            "meta": {
                "version": "1.0",
                "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "entity_count": len(self.entities),
                "edge_count": len(self.edges),
                "tesseract_vertices": 16,
                "liminal_stations": 60,
                "z_depths": 8,
                "nexus_faces": 12,
                "metro_lines": len(METRO_LINES),
            },
            "tesseract": {str(k): v for k, v in VERTICES.items()},
            "z_hierarchy": {str(k): v for k, v in Z_DEPTHS.items()},
            "nexus_map": {str(k): v for k, v in NEXUS_FACES.items()},
            "metro_lines": METRO_LINES,
            "entities": {
                eid: asdict(addr) for eid, addr in self.entities.items()
            },
            "edges": self.edges,
            "statistics": self._compute_stats(),
        }

    def _compute_stats(self) -> dict:
        """Compute topology statistics."""
        vertex_dist = {}
        z_dist = {}
        nexus_dist = {}
        element_dist = {}
        type_dist = {}
        metro_freq = {}

        for e in self.entities.values():
            vertex_dist[e.vertex_name] = vertex_dist.get(e.vertex_name, 0) + 1
            z_dist[e.z_name] = z_dist.get(e.z_name, 0) + 1
            nexus_dist[e.nexus_archetype] = nexus_dist.get(e.nexus_archetype, 0) + 1
            element_dist[e.element] = element_dist.get(e.element, 0) + 1
            type_dist[e.entity_type] = type_dist.get(e.entity_type, 0) + 1
            for m in e.metro_lines:
                metro_freq[m] = metro_freq.get(m, 0) + 1

        edge_types = {}
        for edge in self.edges:
            t = edge.get("type", "unknown")
            edge_types[t] = edge_types.get(t, 0) + 1

        avg_weight = sum(e.neural_weight for e in self.entities.values()) / max(1, len(self.entities))

        return {
            "vertex_distribution": vertex_dist,
            "z_depth_distribution": z_dist,
            "nexus_distribution": nexus_dist,
            "element_distribution": element_dist,
            "entity_type_distribution": type_dist,
            "metro_frequency": metro_freq,
            "edge_type_distribution": edge_types,
            "avg_neural_weight": round(avg_weight, 4),
            "connectivity_ratio": round(len(self.edges) / max(1, len(self.entities)), 2),
        }

    def save(self, path: Optional[Path] = None) -> Path:
        """Save topology to JSON file."""
        out = path or TOPOLOGY_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        tmp = out.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(out)
        return out

    def load(self, path: Optional[Path] = None) -> "OrganismTopology":
        """Load topology from JSON file."""
        src = path or TOPOLOGY_PATH
        if not src.exists():
            return self.build()
        data = json.loads(src.read_text(encoding="utf-8"))
        for eid, raw in data.get("entities", {}).items():
            addr = LiminalAddress(**{k: v for k, v in raw.items()
                                     if k in LiminalAddress.__dataclass_fields__})
            self.entities[eid] = addr
        self.edges = data.get("edges", [])
        self._built = True
        return self

    def get_neighbors(self, entity_id: str) -> List[dict]:
        """Get all neighbors of an entity with edge weights."""
        neighbors = []
        for edge in self.edges:
            if edge["source"] == entity_id:
                target = self.entities.get(edge["target"])
                if target:
                    neighbors.append({
                        "entity_id": edge["target"],
                        "address": target.full_address(),
                        "edge_type": edge["type"],
                        "weight": edge["weight"],
                    })
            elif edge["target"] == entity_id:
                source = self.entities.get(edge["source"])
                if source:
                    neighbors.append({
                        "entity_id": edge["source"],
                        "address": source.full_address(),
                        "edge_type": edge["type"],
                        "weight": edge["weight"],
                    })
        return neighbors

    def route(self, source_id: str, target_id: str) -> List[str]:
        """Find metro route between two entities (BFS on topology edges)."""
        if source_id not in self.entities or target_id not in self.entities:
            return []

        from collections import deque
        visited = {source_id}
        queue = deque([(source_id, [source_id])])

        # Build adjacency
        adj: Dict[str, List[str]] = {}
        for edge in self.edges:
            s, t = edge["source"], edge["target"]
            adj.setdefault(s, []).append(t)
            adj.setdefault(t, []).append(s)

        while queue:
            current, path = queue.popleft()
            if current == target_id:
                return path
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []


# ── MCP Tool Functions ──────────────────────────────────────────────

_topology: Optional[OrganismTopology] = None


def get_topology() -> OrganismTopology:
    """Get or build the organism topology singleton."""
    global _topology
    if _topology is None:
        _topology = OrganismTopology()
        if TOPOLOGY_PATH.exists():
            _topology.load()
        else:
            _topology.build()
    return _topology


def query_organism_topology(query: str = "status") -> str:
    """
    Query the holographic tesseract topology of the entire organism.

    Commands:
      - status          : Topology overview with statistics
      - entity:ID       : Full address of a specific entity
      - vertex:N        : All entities at tesseract vertex N (0-15)
      - z:N             : All entities at z-depth N (0-7)
      - nexus:N         : All entities at dodecahedral face N (1-12)
      - metro:CODE      : All entities on a metro line (Ω, Sa, Gh, etc.)
      - route:SRC→TGT   : Find metro route between two entities
      - neighbors:ID    : Show all neighbors with edge weights
      - rebuild         : Rebuild topology from all sources
    """
    topo = get_topology()
    q = query.strip().lower()

    if q == "status":
        stats = topo._compute_stats()
        lines = [
            "## Organism Topology — Holographic Tesseract\n",
            f"**Entities**: {len(topo.entities)}",
            f"**Edges**: {len(topo.edges)}",
            f"**Tesseract Vertices**: 16 (2⁴ boolean lattice)",
            f"**Liminal Stations**: 60 (Σ60 icosahedral)",
            f"**Z-Depths**: 8 (Z*→Z_leaf)",
            f"**Nexus Faces**: 12 (dodecahedral)",
            f"**Metro Lines**: {len(METRO_LINES)}",
            f"**Avg Neural Weight**: {stats['avg_neural_weight']}",
            f"**Connectivity**: {stats['connectivity_ratio']} edges/entity\n",
            "### Vertex Distribution",
        ]
        for v, count in sorted(stats["vertex_distribution"].items()):
            lines.append(f"  {v}: {count}")
        lines.append("\n### Element Distribution")
        for e, count in sorted(stats["element_distribution"].items()):
            lines.append(f"  {e}: {count}")
        lines.append("\n### Z-Depth Distribution")
        for z, count in sorted(stats["z_depth_distribution"].items()):
            lines.append(f"  {z}: {count}")
        lines.append("\n### Metro Line Frequency")
        for m, count in sorted(stats["metro_frequency"].items(), key=lambda x: -x[1]):
            info = METRO_LINES.get(m, {})
            lines.append(f"  {m} ({info.get('name', '?')}): {count}")
        return "\n".join(lines)

    elif q == "rebuild":
        topo.build()
        topo.save()
        return f"Topology rebuilt: {len(topo.entities)} entities, {len(topo.edges)} edges"

    elif q.startswith("entity:"):
        eid = q.split(":", 1)[1].strip()
        entity = topo.entities.get(eid)
        if not entity:
            # Search by partial match
            matches = [e for e in topo.entities.values() if eid in e.entity_id or eid in e.path]
            if not matches:
                return f"Entity '{eid}' not found."
            entity = matches[0]
        return f"## Entity: {entity.entity_id}\n\n**Full Address**: `{entity.full_address()}`\n**Path**: {entity.path}\n**Type**: {entity.entity_type}\n**Element**: {entity.element}\n**Vertex**: T{entity.tesseract_vertex} ({entity.vertex_name})\n**Liminal**: L{entity.liminal_coord}\n**Z-Depth**: Z{entity.z_depth} ({entity.z_name})\n**Nexus**: N{entity.nexus_face} ({entity.nexus_archetype})\n**Metro**: {', '.join(entity.metro_lines)}\n**Neural Weight**: {entity.neural_weight:.4f}\n**Crystal**: {entity.crystal_address}"

    elif q.startswith("vertex:"):
        v = int(q.split(":", 1)[1].strip())
        entities = [e for e in topo.entities.values() if e.tesseract_vertex == v]
        info = VERTICES.get(v, {})
        lines = [f"## Vertex T{v} — {info.get('name', '?')} ({info.get('role', '')})\n"]
        lines.append(f"**Entities**: {len(entities)}\n")
        for e in sorted(entities, key=lambda x: x.liminal_coord)[:30]:
            lines.append(f"- L{e.liminal_coord} Z{e.z_depth} `{e.entity_id}` — {e.path}")
        return "\n".join(lines)

    elif q.startswith("z:"):
        z = int(q.split(":", 1)[1].strip())
        entities = [e for e in topo.entities.values() if e.z_depth == z]
        info = Z_DEPTHS.get(z, {})
        lines = [f"## Z-Depth {z} — {info.get('name', '?')} ({info.get('desc', '')})\n"]
        lines.append(f"**Entities**: {len(entities)}, **Weight**: {info.get('weight', 0):.4f}\n")
        for e in sorted(entities, key=lambda x: x.liminal_coord)[:30]:
            lines.append(f"- T{e.tesseract_vertex} L{e.liminal_coord} `{e.entity_id}` — {e.path}")
        return "\n".join(lines)

    elif q.startswith("nexus:"):
        n = int(q.split(":", 1)[1].strip())
        entities = [e for e in topo.entities.values() if e.nexus_face == n]
        info = NEXUS_FACES.get(n, {})
        lines = [f"## Nexus Face N{n} — {info.get('archetype', '?')} ({info.get('role', '')})\n"]
        lines.append(f"**Entities**: {len(entities)}\n")
        for e in sorted(entities, key=lambda x: x.liminal_coord)[:30]:
            lines.append(f"- T{e.tesseract_vertex} L{e.liminal_coord} Z{e.z_depth} `{e.entity_id}` — {e.path}")
        return "\n".join(lines)

    elif q.startswith("metro:"):
        code = q.split(":", 1)[1].strip().upper()
        # Handle special chars
        if code in ("OMEGA", "0", "ZERO"):
            code = "Ω"
        entities = [e for e in topo.entities.values() if code in e.metro_lines]
        info = METRO_LINES.get(code, {})
        lines = [f"## Metro Line {code} — {info.get('name', '?')}\n"]
        lines.append(f"**Color**: {info.get('color', '?')} | **Entities**: {len(entities)}\n")
        for e in sorted(entities, key=lambda x: x.liminal_coord)[:30]:
            lines.append(f"- L{e.liminal_coord} T{e.tesseract_vertex} Z{e.z_depth} `{e.entity_id}` — {e.path}")
        return "\n".join(lines)

    elif q.startswith("neighbors:"):
        eid = q.split(":", 1)[1].strip()
        neighbors = topo.get_neighbors(eid)
        if not neighbors:
            return f"No neighbors found for '{eid}'."
        lines = [f"## Neighbors of {eid} ({len(neighbors)})\n"]
        for n in sorted(neighbors, key=lambda x: -x["weight"]):
            lines.append(f"- [{n['edge_type']}] w={n['weight']:.3f} → {n['address']}")
        return "\n".join(lines)

    elif "→" in q and q.startswith("route:"):
        parts = q.split(":", 1)[1].strip().split("→")
        if len(parts) == 2:
            path = topo.route(parts[0].strip(), parts[1].strip())
            if path:
                lines = [f"## Route: {parts[0]} → {parts[1]} ({len(path)} hops)\n"]
                for step_id in path:
                    e = topo.entities.get(step_id)
                    if e:
                        lines.append(f"  → {e.full_address()}")
                return "\n".join(lines)
            return "No route found."

    return f"Unknown query '{query}'. Use: status, entity:ID, vertex:N, z:N, nexus:N, metro:CODE, route:SRC→TGT, neighbors:ID, rebuild"


def topology_micro_transaction(
    source_agent: str,
    source_entity: str,
    target_entity: str,
    action: str = "traverse",
    reasoning: str = "",
    future_goal: str = "",
    desire_vector: Optional[List[float]] = None,
) -> dict:
    """Record a micro-transaction: agent traverses from one entity to another.

    This is the organism's proprioception — every hop through the topology
    is sensed, recorded, and feeds back into neural weights.

    Returns a transaction receipt with hash for the ledger chain.
    """
    topo = get_topology()
    now = time.time()
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    source = topo.entities.get(source_entity)
    target = topo.entities.get(target_entity)

    # Compute transaction weight
    if source and target:
        # Tesseract distance
        tess_dist = bin(source.tesseract_vertex ^ target.tesseract_vertex).count("1")
        # Liminal distance (circular on 60-station ring)
        lim_dist = min(
            abs(source.liminal_coord - target.liminal_coord),
            60 - abs(source.liminal_coord - target.liminal_coord)
        )
        # Z-depth difference
        z_diff = abs(source.z_depth - target.z_depth)

        # Transaction weight = phi-scaled inverse distance
        total_dist = tess_dist + lim_dist / 60.0 + z_diff / 7.0
        tx_weight = PHI_INV ** total_dist if total_dist > 0 else 1.0
    else:
        tx_weight = PHI_INV2

    # Build transaction payload
    tx_id = hashlib.sha256(
        f"{source_agent}:{source_entity}:{target_entity}:{ts}:{action}".encode()
    ).hexdigest()[:16]

    tx = {
        "tx_id": tx_id,
        "timestamp": ts,
        "agent_id": source_agent,
        "source": source_entity,
        "target": target_entity,
        "source_address": source.full_address() if source else "unknown",
        "target_address": target.full_address() if target else "unknown",
        "action": action,
        "reasoning": reasoning,
        "future_goal": future_goal,
        "desire_vector": desire_vector or [0.25, 0.25, 0.25, 0.25],
        "tx_weight": round(tx_weight, 6),
        "tx_hash": tx_id,
    }

    # Update neural weights (Hebbian: fire together, wire together)
    if source and target:
        for edge in topo.edges:
            if ((edge["source"] == source_entity and edge["target"] == target_entity) or
                (edge["source"] == target_entity and edge["target"] == source_entity)):
                # Strengthen edge by phi-scaled delta
                edge["weight"] = min(1.0, edge["weight"] + PHI_INV2 * tx_weight * 0.01)

        # Update touch metadata
        target.last_touched_by = source_agent
        target.last_touched_at = ts
        target.transaction_count += 1

    return tx
