"""
Crystal-Internal Weight Storage — Fractal Compressed Neural Weights
====================================================================
Maps the Athena neural network weights INTO the 108D crystal coordinate
system using QSHRINK addressing and the 1/8 lift compression cascade.

Instead of 22MB+ flat JSON externally, weights are stored at crystal
coordinates with fractal compression:
  Full (~38K weights) → 1/8 seed (36 shells) → 1/64 micro (12 archetypes) → 1/512 nano (4 values)

Each weight is addressable by crystal coordinate. Decompression regenerates
approximate weights from seeds using the holographic equation:
  w * Compress(S_k) + (1-w) * Template(Archetype(S_k))
"""

from __future__ import annotations

import json
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

from ._cache import JsonCache, DATA_DIR
from .constants import (
    TOTAL_SHELLS,
    TOTAL_NODES,
    TOTAL_WREATHS,
    ARCHETYPE_NAMES,
    LENS_CODES,
    MASTER_CLOCK_PERIOD,
)
from .qshrink import (
    QSHRINK_ROOT_CELLS,
    SIGNAL_BAND,
    METADATA_BAND,
    LIFT_FACTOR,
    SFCR_LENSES,
)

# Golden ratio constants (from brain.py)
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1  # 0.618...

# Element → SFCR face mapping
ELEMENT_TO_FACE = {"Earth": "S", "Fire": "F", "Water": "C", "Air": "R"}
FACE_TO_ELEMENT = {v: k for k, v in ELEMENT_TO_FACE.items()}

# Legacy data paths
NEURAL_NET_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "DEEPER_CRYSTALIZATION"
    / "ACTIVE_NERVOUS_SYSTEM"
    / "13_DEEPER_NEURAL_NET"
    / "09_RUNTIME"
)

WEIGHTS_FILE = DATA_DIR / "crystal_weights.json"
CHECKPOINT_DIR = DATA_DIR / "self_play_checkpoints"


# ── Data structures ──────────────────────────────────────────────────


@dataclass
class CrystalWeight:
    """A single weight stored at a crystal coordinate."""
    coordinate: str       # e.g. "Xi108:W2:A4:S15:F"
    shell: int            # 1-36
    wreath: int           # 1-3
    archetype: int        # 1-12
    face: str             # S/F/C/R
    value: float          # the weight value
    count: int = 1        # number of pairs contributing to this weight
    source: str = ""      # "gate", "pair", "bridge"


@dataclass
class ShellSeed:
    """1/8 compressed: per-shell weight summary."""
    shell: int
    wreath: str           # Su/Me/Sa
    mean: float
    std: float
    count: int
    min_val: float
    max_val: float
    element_dist: dict    # {"Fire": 0.3, "Water": 0.2, ...}
    gate_means: dict      # {"G00": 7.5, "G01": 6.2, ...}


@dataclass
class ArchetypeSeed:
    """1/64 compressed: per-archetype summary across 3 wreaths."""
    archetype: int
    name: str
    mean: float
    std: float
    count: int
    shells: list          # [s_su, s_me, s_sa]
    wreath_means: dict    # {"Su": 5.2, "Me": 5.0, "Sa": 4.8}


@dataclass
class NanoSeed:
    """1/512 compressed: global weight distribution."""
    global_mean: float
    global_std: float
    skew: float
    kurtosis: float
    total_count: int
    element_means: dict   # {"Fire": 5.5, "Water": 4.8, ...}
    gate_means: dict      # {"G00": 7.5, ...}


# ── FractalWeightStore ───────────────────────────────────────────────


class FractalWeightStore:
    """Stores neural net weights IN the crystal coordinate system.

    Weights are addressed by crystal coordinates and compressed using
    the 1/8 lift law from QSHRINK.
    """

    # Default learnable parameters (evolved by self-play)
    DEFAULT_PATH_WEIGHTS = {"S": 0.20, "F": 0.35, "C": 0.25, "R": 0.20}
    DEFAULT_RESONANCE_WEIGHTS = {
        "addr_fit": 0.20, "inv_fit": 0.15, "phase": 0.15,
        "boundary": 0.15, "scale": 0.15, "compress": 0.20,
    }
    DEFAULT_DESIRE_WEIGHTS = {
        "align": 0.35, "explore": 0.20, "zpa": 0.25, "con_sat": 0.20,
    }
    DEFAULT_BRIDGE_MODULATION = 0.20  # max bridge boost factor

    def __init__(self):
        # Full weight store (populated on import or decompress)
        self._gate_weights: dict[str, dict[str, CrystalWeight]] = {}  # gate→gate→weight
        self._pair_weights: dict[str, CrystalWeight] = {}  # "DOCxxxx:DOCyyyy"→weight
        self._doc_registry: list[dict] = []  # imported document metadata

        # Compressed seeds
        self._shell_seeds: dict[int, ShellSeed] = {}      # shell→seed
        self._archetype_seeds: dict[int, ArchetypeSeed] = {}  # archetype→seed
        self._nano_seed: Optional[NanoSeed] = None

        # Learnable parameters (evolved by self-play)
        self.path_weights = dict(self.DEFAULT_PATH_WEIGHTS)
        self.resonance_weights = dict(self.DEFAULT_RESONANCE_WEIGHTS)
        self.desire_weights = dict(self.DEFAULT_DESIRE_WEIGHTS)
        self.bridge_modulation = self.DEFAULT_BRIDGE_MODULATION
        self.geo_arith_blend = 0.60  # geometric vs arithmetic blend

        # Metadata
        self._version = "v2.0"
        self._active_level = "empty"  # "full", "seed", "micro", "nano", "empty"
        self._last_updated = ""
        self._total_weights = 0
        self._import_stats: dict = {}

    # ── Coordinate computation ────────────────────────────────────

    @staticmethod
    def doc_to_shell(doc: dict) -> int:
        """Map a document to a crystal shell based on its element and gate."""
        element = doc.get("element", "Earth")
        gate_str = doc.get("gate", "G00")
        gate_num = int(gate_str[1:]) if gate_str.startswith("G") else 0

        # Map element to wreath band: Fire/Water → Su(1-12), Earth → Me(13-24), Air → Sa(25-36)
        if element in ("Fire", "Water"):
            base = 0
        elif element == "Earth":
            base = 12
        else:  # Air
            base = 24

        # Gate maps to archetype position within the band
        archetype_pos = gate_num % 12
        shell = base + archetype_pos + 1
        return max(1, min(TOTAL_SHELLS, shell))

    @staticmethod
    def doc_to_coordinate(doc: dict) -> str:
        """Generate crystal coordinate for a document."""
        shell = FractalWeightStore.doc_to_shell(doc)
        wreath = ((shell - 1) // 12) + 1  # 1-3
        archetype = ((shell - 1) % 12) + 1  # 1-12
        element = doc.get("element", "Earth")
        face = ELEMENT_TO_FACE.get(element, "S")
        return f"Xi108:W{wreath}:A{archetype}:S{shell}:{face}"

    @staticmethod
    def gate_to_coordinate(src_gate: str, dst_gate: str) -> str:
        """Map a gate matrix cell to a crystal coordinate."""
        src_num = int(src_gate[1:]) if src_gate.startswith("G") else 0
        dst_num = int(dst_gate[1:]) if dst_gate.startswith("G") else 0
        root_cell = src_num * 16 + dst_num  # 0-255

        if root_cell < SIGNAL_BAND:
            # Signal band → crystal dimension
            shell = (root_cell % TOTAL_SHELLS) + 1
            wreath = ((shell - 1) // 12) + 1
            archetype = ((shell - 1) % 12) + 1
            face = SFCR_LENSES[root_cell % 4]
        else:
            # Metadata band → compression envelope
            meta_idx = root_cell - SIGNAL_BAND
            shell = (meta_idx % TOTAL_SHELLS) + 1
            wreath = ((shell - 1) // 12) + 1
            archetype = ((shell - 1) % 12) + 1
            face = SFCR_LENSES[meta_idx % 4]

        return f"Xi108:W{wreath}:A{archetype}:S{shell}:{face}"

    @staticmethod
    def shell_to_wreath_name(shell: int) -> str:
        """Map shell number to wreath name."""
        idx = (shell - 1) // 12
        return ["Su", "Me", "Sa"][min(idx, 2)]

    # ── Import from legacy ────────────────────────────────────────

    def import_from_legacy(self, neural_net_dir: Path = None) -> dict:
        """Import weights from the existing flat JSON neural net files.

        Returns import statistics.
        """
        if neural_net_dir is None:
            neural_net_dir = NEURAL_NET_DIR

        stats = {
            "docs_imported": 0,
            "gate_weights_imported": 0,
            "pair_weights_imported": 0,
            "total_weights": 0,
        }

        # 1. Import element registry and enrich tokens from all text fields
        registry_path = neural_net_dir / "01_element_registry.json"
        if registry_path.exists():
            self._doc_registry = json.loads(registry_path.read_text(encoding="utf-8"))
            # Enrich tokens from name, display_name, excerpt, family
            import re
            stops = {"the", "and", "for", "with", "this", "that", "from", "into",
                     "are", "was", "were", "been", "being", "have", "has", "had",
                     "not", "but", "what", "how", "when", "where", "who", "which",
                     "its", "all", "can", "will", "one", "two", "each", "then",
                     "than", "also", "more", "some", "such", "only", "other",
                     "does", "did", "these", "those", "about", "would", "could",
                     "should", "just", "like", "over", "between", "both", "our",
                     "most", "any", "may", "much", "very", "own", "same", "after"}
            for doc in self._doc_registry:
                existing_tokens = set(doc.get("tokens", []))
                for field in ("name", "display_name", "excerpt", "family_label"):
                    text = doc.get(field, "")
                    if text:
                        words = re.findall(r'[a-z][a-z0-9_]+', text.lower())
                        for w in words:
                            if w not in stops and len(w) > 2:
                                existing_tokens.add(w)
                doc["tokens"] = list(existing_tokens)
            stats["docs_imported"] = len(self._doc_registry)

        # 2. Import gate matrix
        gate_path = neural_net_dir / "03_operator_gate_matrix.json"
        if gate_path.exists():
            gate_data = json.loads(gate_path.read_text(encoding="utf-8"))
            gate_keys = [f"G{i:02d}" for i in range(16)]

            for src_gate in gate_keys:
                if src_gate not in gate_data:
                    continue
                self._gate_weights[src_gate] = {}
                for dst_gate in gate_keys:
                    cell = gate_data[src_gate].get(dst_gate, {})
                    count = cell.get("count", 0)
                    avg_score = cell.get("avg_score", 0.0)
                    if count > 0:
                        coord = self.gate_to_coordinate(src_gate, dst_gate)
                        self._gate_weights[src_gate][dst_gate] = CrystalWeight(
                            coordinate=coord,
                            shell=int(coord.split(":S")[1].split(":")[0]),
                            wreath=int(coord.split(":W")[1].split(":")[0]),
                            archetype=int(coord.split(":A")[1].split(":")[0]),
                            face=coord.split(":")[-1],
                            value=avg_score,
                            count=count,
                            source="gate",
                        )
                        stats["gate_weights_imported"] += 1

        # 3. Import pair matrix (streaming to avoid loading 22MB at once)
        pair_path = neural_net_dir / "02_ordered_pair_matrix.json"
        if pair_path.exists():
            pair_data = json.loads(pair_path.read_text(encoding="utf-8"))

            # Build doc lookup for coordinate computation
            doc_lookup = {}
            for doc in self._doc_registry:
                doc_lookup[doc["id"]] = doc

            for pair in pair_data:
                src_id = pair.get("src", "")
                dst_id = pair.get("dst", "")
                score = pair.get("score", 0)
                if src_id == dst_id:
                    continue  # skip self-pairs

                src_doc = doc_lookup.get(src_id, {})
                dst_doc = doc_lookup.get(dst_id, {})

                src_shell = self.doc_to_shell(src_doc) if src_doc else 1
                dst_element = dst_doc.get("element", "Earth") if dst_doc else "Earth"
                dst_face = ELEMENT_TO_FACE.get(dst_element, "S")

                wreath = ((src_shell - 1) // 12) + 1
                archetype = ((src_shell - 1) % 12) + 1
                coord = f"Xi108:W{wreath}:A{archetype}:S{src_shell}:{dst_face}"

                pair_key = f"{src_id}:{dst_id}"
                self._pair_weights[pair_key] = CrystalWeight(
                    coordinate=coord,
                    shell=src_shell,
                    wreath=wreath,
                    archetype=archetype,
                    face=dst_face,
                    value=float(score),
                    count=1,
                    source="pair",
                )
                stats["pair_weights_imported"] += 1

        stats["total_weights"] = stats["gate_weights_imported"] + stats["pair_weights_imported"]
        self._total_weights = stats["total_weights"]
        self._active_level = "full"
        self._last_updated = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        self._import_stats = stats

        # Auto-compress after import
        self.compress_to_seed()
        self.compress_to_micro_seed()
        self.compress_to_nano_seed()

        return stats

    # ── Compression cascade (1/8 lift law) ────────────────────────

    def compress_to_seed(self) -> dict[int, ShellSeed]:
        """Compress full weights to 1/8 seed: per-shell summaries."""
        shell_values: dict[int, list[float]] = defaultdict(list)
        shell_elements: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        shell_gates: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

        # Aggregate pair weights by shell
        for pair_key, cw in self._pair_weights.items():
            shell_values[cw.shell].append(cw.value)
            # Infer element from face
            element = FACE_TO_ELEMENT.get(cw.face, "Earth")
            shell_elements[cw.shell][element] += 1

        # Aggregate gate weights by shell
        for src_gate, dst_gates in self._gate_weights.items():
            for dst_gate, cw in dst_gates.items():
                shell_gates[cw.shell][src_gate].append(cw.value)
                shell_values[cw.shell].append(cw.value)

        # Build shell seeds
        self._shell_seeds = {}
        for shell in range(1, TOTAL_SHELLS + 1):
            values = shell_values.get(shell, [0.0])
            if not values:
                values = [0.0]

            n = len(values)
            mean = sum(values) / n
            variance = sum((v - mean) ** 2 for v in values) / max(n - 1, 1)
            std = math.sqrt(variance)

            # Element distribution (normalize)
            elem_counts = shell_elements.get(shell, {})
            total_elem = sum(elem_counts.values()) or 1
            elem_dist = {e: c / total_elem for e, c in elem_counts.items()}

            # Gate means
            gate_data = shell_gates.get(shell, {})
            gate_means = {}
            for g, vals in gate_data.items():
                gate_means[g] = sum(vals) / len(vals) if vals else 0.0

            self._shell_seeds[shell] = ShellSeed(
                shell=shell,
                wreath=self.shell_to_wreath_name(shell),
                mean=mean,
                std=std,
                count=n,
                min_val=min(values),
                max_val=max(values),
                element_dist=elem_dist,
                gate_means=gate_means,
            )

        if self._active_level == "empty":
            self._active_level = "seed"

        return self._shell_seeds

    def compress_to_micro_seed(self) -> dict[int, ArchetypeSeed]:
        """Compress 1/8 seed to 1/64 micro-seed: per-archetype summaries."""
        if not self._shell_seeds:
            self.compress_to_seed()

        self._archetype_seeds = {}
        for arch in range(1, 13):
            # Each archetype spans 3 shells (one per wreath)
            su_shell = arch
            me_shell = arch + 12
            sa_shell = arch + 24

            shells = [su_shell, me_shell, sa_shell]
            seeds = [self._shell_seeds.get(s) for s in shells]
            seeds = [s for s in seeds if s is not None]

            if not seeds:
                continue

            total_count = sum(s.count for s in seeds)
            weighted_mean = sum(s.mean * s.count for s in seeds) / max(total_count, 1)

            # Pooled std
            if total_count > 1:
                pooled_var = sum(
                    (s.count - 1) * s.std ** 2 + s.count * (s.mean - weighted_mean) ** 2
                    for s in seeds
                ) / max(total_count - 1, 1)
                pooled_std = math.sqrt(pooled_var)
            else:
                pooled_std = 0.0

            wreath_means = {}
            for s in seeds:
                wreath_means[s.wreath] = s.mean

            self._archetype_seeds[arch] = ArchetypeSeed(
                archetype=arch,
                name=ARCHETYPE_NAMES[arch - 1],
                mean=weighted_mean,
                std=pooled_std,
                count=total_count,
                shells=shells,
                wreath_means=wreath_means,
            )

        return self._archetype_seeds

    def compress_to_nano_seed(self) -> NanoSeed:
        """Compress 1/64 micro-seed to 1/512 nano-seed: global distribution."""
        if not self._archetype_seeds:
            self.compress_to_micro_seed()

        all_means = [s.mean for s in self._archetype_seeds.values()]
        all_counts = [s.count for s in self._archetype_seeds.values()]

        if not all_means:
            self._nano_seed = NanoSeed(0, 0, 0, 0, 0, {}, {})
            return self._nano_seed

        total_count = sum(all_counts)
        global_mean = sum(m * c for m, c in zip(all_means, all_counts)) / max(total_count, 1)

        # Global std from archetype seeds
        if len(all_means) > 1:
            global_var = sum((m - global_mean) ** 2 for m in all_means) / (len(all_means) - 1)
            global_std = math.sqrt(global_var)
        else:
            global_std = 0.0

        # Skewness
        if global_std > 0 and len(all_means) > 2:
            skew = sum(((m - global_mean) / global_std) ** 3 for m in all_means) / len(all_means)
        else:
            skew = 0.0

        # Kurtosis
        if global_std > 0 and len(all_means) > 3:
            kurt = sum(((m - global_mean) / global_std) ** 4 for m in all_means) / len(all_means) - 3
        else:
            kurt = 0.0

        # Element means from shell seeds
        element_totals: dict[str, list[float]] = defaultdict(list)
        for seed in self._shell_seeds.values():
            for elem, frac in seed.element_dist.items():
                if frac > 0:
                    element_totals[elem].append(seed.mean)
        element_means = {e: sum(v) / len(v) for e, v in element_totals.items() if v}

        # Gate means from shell seeds
        gate_totals: dict[str, list[float]] = defaultdict(list)
        for seed in self._shell_seeds.values():
            for g, m in seed.gate_means.items():
                gate_totals[g].append(m)
        gate_means = {g: sum(v) / len(v) for g, v in gate_totals.items() if v}

        self._nano_seed = NanoSeed(
            global_mean=global_mean,
            global_std=global_std,
            skew=skew,
            kurtosis=kurt,
            total_count=total_count,
            element_means=element_means,
            gate_means=gate_means,
        )
        return self._nano_seed

    # ── Decompression (holographic seed equation) ─────────────────

    def decompress_from_seed(self, shell: int) -> dict[str, float]:
        """Regenerate approximate pair weights for a shell from its seed.

        Uses the holographic seed equation:
          Seed(S_k) = w * Compress(S_k) + (1-w) * Template(Archetype(S_k))

        where w = phi_inv (golden ratio weight favoring compressed data).
        """
        seed = self._shell_seeds.get(shell)
        if seed is None:
            return {}

        archetype = ((shell - 1) % 12) + 1
        arch_seed = self._archetype_seeds.get(archetype)

        if arch_seed is None:
            # No archetype template — use pure shell seed
            return {"mean": seed.mean, "std": seed.std, "count": seed.count}

        # Holographic blend: w * shell_data + (1-w) * archetype_template
        w = PHI_INV  # 0.618... — favor the compressed shell data
        blended_mean = w * seed.mean + (1 - w) * arch_seed.mean
        blended_std = w * seed.std + (1 - w) * arch_seed.std

        return {
            "mean": blended_mean,
            "std": blended_std,
            "count": seed.count,
            "shell_contribution": w,
            "archetype_contribution": 1 - w,
            "reconstruction_error": abs(seed.mean - blended_mean),
        }

    def get_weight(self, shell: int, face: str, gate: str = None) -> float:
        """Get a weight at a crystal coordinate, decompressing if needed."""
        # Try full weights first
        if gate and gate in self._gate_weights:
            for dst, cw in self._gate_weights[gate].items():
                if cw.shell == shell and cw.face == face:
                    return cw.value

        # Fall back to seed decompression
        if shell in self._shell_seeds:
            decomp = self.decompress_from_seed(shell)
            return decomp.get("mean", 0.0)

        return 0.0

    def set_weight(self, shell: int, face: str, value: float, source: str = "self_play"):
        """Update a weight at a crystal coordinate."""
        wreath = ((shell - 1) // 12) + 1
        archetype = ((shell - 1) % 12) + 1
        coord = f"Xi108:W{wreath}:A{archetype}:S{shell}:{face}"

        # Update shell seed directly
        if shell in self._shell_seeds:
            seed = self._shell_seeds[shell]
            # Exponential moving average update
            alpha = 0.1
            seed.mean = (1 - alpha) * seed.mean + alpha * value
            seed.count += 1

        self._last_updated = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    def get_gate_weight(self, src_gate: str, dst_gate: str) -> float:
        """Get a specific gate-to-gate transition weight."""
        if src_gate in self._gate_weights and dst_gate in self._gate_weights[src_gate]:
            return self._gate_weights[src_gate][dst_gate].value
        return 0.0

    def get_shell_seed(self, shell: int) -> Optional[ShellSeed]:
        """Get the seed for a specific shell."""
        return self._shell_seeds.get(shell)

    def get_archetype_seed(self, archetype: int) -> Optional[ArchetypeSeed]:
        """Get the seed for a specific archetype."""
        return self._archetype_seeds.get(archetype)

    # ── Persistence ───────────────────────────────────────────────

    def save(self, path: Path = None) -> None:
        """Save crystal weights to JSON file."""
        if path is None:
            path = WEIGHTS_FILE

        data = {
            "meta": {
                "version": self._version,
                "active_level": self._active_level,
                "total_weights": self._total_weights,
                "last_updated": self._last_updated,
                "import_stats": self._import_stats,
            },
            "shell_seeds": {},
            "archetype_seeds": {},
            "nano_seed": None,
            "gate_matrix": {},
        }

        # Shell seeds (always saved — they're small)
        for shell, seed in self._shell_seeds.items():
            data["shell_seeds"][str(shell)] = {
                "shell": seed.shell,
                "wreath": seed.wreath,
                "mean": round(seed.mean, 6),
                "std": round(seed.std, 6),
                "count": seed.count,
                "min": round(seed.min_val, 6),
                "max": round(seed.max_val, 6),
                "element_dist": {k: round(v, 4) for k, v in seed.element_dist.items()},
                "gate_means": {k: round(v, 4) for k, v in seed.gate_means.items()},
            }

        # Archetype seeds
        for arch, seed in self._archetype_seeds.items():
            data["archetype_seeds"][str(arch)] = {
                "archetype": seed.archetype,
                "name": seed.name,
                "mean": round(seed.mean, 6),
                "std": round(seed.std, 6),
                "count": seed.count,
                "shells": seed.shells,
                "wreath_means": {k: round(v, 4) for k, v in seed.wreath_means.items()},
            }

        # Nano seed
        if self._nano_seed:
            data["nano_seed"] = {
                "global_mean": round(self._nano_seed.global_mean, 6),
                "global_std": round(self._nano_seed.global_std, 6),
                "skew": round(self._nano_seed.skew, 6),
                "kurtosis": round(self._nano_seed.kurtosis, 6),
                "total_count": self._nano_seed.total_count,
                "element_means": {k: round(v, 4) for k, v in self._nano_seed.element_means.items()},
                "gate_means": {k: round(v, 4) for k, v in self._nano_seed.gate_means.items()},
            }

        # Learnable parameters
        data["learnable"] = {
            "path_weights": {k: round(v, 6) for k, v in self.path_weights.items()},
            "resonance_weights": {k: round(v, 6) for k, v in self.resonance_weights.items()},
            "desire_weights": {k: round(v, 6) for k, v in self.desire_weights.items()},
            "bridge_modulation": round(self.bridge_modulation, 6),
            "geo_arith_blend": round(self.geo_arith_blend, 6),
        }

        # Gate matrix (compact: only non-zero)
        for src_gate, dst_gates in self._gate_weights.items():
            gate_entry = {}
            for dst_gate, cw in dst_gates.items():
                gate_entry[dst_gate] = {
                    "value": round(cw.value, 4),
                    "count": cw.count,
                    "coord": cw.coordinate,
                }
            if gate_entry:
                data["gate_matrix"][src_gate] = gate_entry

        # Compact doc registry (only fields needed for forward pass)
        if self._doc_registry:
            compact_docs = []
            for doc in self._doc_registry:
                compact_docs.append({
                    "id": doc.get("id", ""),
                    "display_name": doc.get("display_name", doc.get("name", ""))[:120],
                    "element": doc.get("element", "Earth"),
                    "secondary_element": doc.get("secondary_element", ""),
                    "gate": doc.get("gate", "G00"),
                    "family": doc.get("family", ""),
                    "chapters": doc.get("chapters", []),
                    "appendices": doc.get("appendices", []),
                    "tokens": doc.get("tokens", [])[:120],
                    "scores": doc.get("scores", {}),
                })
            data["doc_registry"] = compact_docs

        # Atomic write via temp file
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp_path.replace(path)

    def load(self, path: Path = None) -> bool:
        """Load crystal weights from JSON file. Returns True if loaded."""
        if path is None:
            path = WEIGHTS_FILE

        if not path.exists():
            return False

        data = json.loads(path.read_text(encoding="utf-8"))
        meta = data.get("meta", {})
        self._version = meta.get("version", "v1.0")
        self._active_level = meta.get("active_level", "seed")
        self._total_weights = meta.get("total_weights", 0)
        self._last_updated = meta.get("last_updated", "")
        self._import_stats = meta.get("import_stats", {})

        # Load shell seeds
        self._shell_seeds = {}
        for key, sd in data.get("shell_seeds", {}).items():
            shell = int(key)
            self._shell_seeds[shell] = ShellSeed(
                shell=sd["shell"],
                wreath=sd["wreath"],
                mean=sd["mean"],
                std=sd["std"],
                count=sd["count"],
                min_val=sd.get("min", 0.0),
                max_val=sd.get("max", 0.0),
                element_dist=sd.get("element_dist", {}),
                gate_means=sd.get("gate_means", {}),
            )

        # Load archetype seeds
        self._archetype_seeds = {}
        for key, ad in data.get("archetype_seeds", {}).items():
            arch = int(key)
            self._archetype_seeds[arch] = ArchetypeSeed(
                archetype=ad["archetype"],
                name=ad["name"],
                mean=ad["mean"],
                std=ad["std"],
                count=ad["count"],
                shells=ad["shells"],
                wreath_means=ad.get("wreath_means", {}),
            )

        # Load nano seed
        ns = data.get("nano_seed")
        if ns:
            self._nano_seed = NanoSeed(
                global_mean=ns["global_mean"],
                global_std=ns["global_std"],
                skew=ns["skew"],
                kurtosis=ns["kurtosis"],
                total_count=ns["total_count"],
                element_means=ns.get("element_means", {}),
                gate_means=ns.get("gate_means", {}),
            )

        # Load gate matrix
        self._gate_weights = {}
        for src_gate, dst_gates in data.get("gate_matrix", {}).items():
            self._gate_weights[src_gate] = {}
            for dst_gate, gd in dst_gates.items():
                coord = gd.get("coord", f"Xi108:W1:A1:S1:S")
                parts = coord.split(":")
                shell = int(parts[3][1:]) if len(parts) > 3 else 1
                wreath = int(parts[1][1:]) if len(parts) > 1 else 1
                archetype = int(parts[2][1:]) if len(parts) > 2 else 1
                face = parts[4] if len(parts) > 4 else "S"

                self._gate_weights[src_gate][dst_gate] = CrystalWeight(
                    coordinate=coord,
                    shell=shell,
                    wreath=wreath,
                    archetype=archetype,
                    face=face,
                    value=gd["value"],
                    count=gd.get("count", 1),
                    source="gate",
                )

        # Load learnable parameters
        lp = data.get("learnable", {})
        if lp:
            self.path_weights = lp.get("path_weights", dict(self.DEFAULT_PATH_WEIGHTS))
            self.resonance_weights = lp.get("resonance_weights", dict(self.DEFAULT_RESONANCE_WEIGHTS))
            self.desire_weights = lp.get("desire_weights", dict(self.DEFAULT_DESIRE_WEIGHTS))
            self.bridge_modulation = lp.get("bridge_modulation", self.DEFAULT_BRIDGE_MODULATION)
            self.geo_arith_blend = lp.get("geo_arith_blend", 0.60)

        # Load doc registry
        self._doc_registry = data.get("doc_registry", [])

        return True

    # ── Query helpers ─────────────────────────────────────────────

    def shell_coordinates(self) -> list[int]:
        """Return list of all shells with seeds."""
        return sorted(self._shell_seeds.keys())

    def gate_coordinates(self) -> list[tuple[str, str]]:
        """Return list of all (src_gate, dst_gate) pairs with weights."""
        coords = []
        for src, dsts in self._gate_weights.items():
            for dst in dsts:
                coords.append((src, dst))
        return coords

    # ── Pair weight unfreezing & update (swarm integration) ──────

    _pair_frozen: bool = True  # Default: pair weights frozen (legacy behavior)
    _pair_update_count: int = 0
    _doc_bias_offsets: dict = {}  # per-document learnable bias offsets

    def unfreeze_pair_weights(self) -> None:
        """Unfreeze pair weights so they can be updated by the swarm."""
        self._pair_frozen = False

    def freeze_pair_weights(self) -> None:
        """Re-freeze pair weights (stop learning)."""
        self._pair_frozen = True

    @property
    def pair_weights_frozen(self) -> bool:
        return self._pair_frozen

    def update_pair_weight(self, src_id: str, dst_id: str, delta: float) -> bool:
        """Update a single pair weight by delta. Returns True if applied.

        Only works if pair weights are unfrozen. The delta is clipped
        to prevent extreme weight changes.
        """
        if self._pair_frozen:
            return False

        key = f"{src_id}:{dst_id}"
        rev_key = f"{dst_id}:{src_id}"

        # Clip delta
        delta = max(-1.0, min(1.0, delta))

        if key in self._pair_weights:
            self._pair_weights[key].value += delta
            self._pair_update_count += 1
            return True
        elif rev_key in self._pair_weights:
            self._pair_weights[rev_key].value += delta
            self._pair_update_count += 1
            return True
        return False

    def update_doc_bias(self, doc_id: str, delta: float) -> None:
        """Update per-document learnable bias offset.

        These are lightweight (197 params) alternatives to updating
        all 38K pair weights — one bias per document that shifts all
        its pair weights simultaneously.
        """
        current = self._doc_bias_offsets.get(doc_id, 0.0)
        self._doc_bias_offsets[doc_id] = current + max(-0.5, min(0.5, delta))

    def get_doc_bias(self, doc_id: str) -> float:
        """Get per-document bias offset."""
        return self._doc_bias_offsets.get(doc_id, 0.0)

    def get_learnable_count(self) -> int:
        """Report how many weights are actually being updated.

        Counts: shell seed means (36) + gate matrix entries (~225)
                + pair weights (if unfrozen) + doc bias offsets
                + path/resonance/desire weights
        """
        count = 0
        count += len(self._shell_seeds)  # shell seed means
        for src, dsts in self._gate_weights.items():
            count += len(dsts)  # gate matrix entries
        if not self._pair_frozen:
            count += len(self._pair_weights)  # pair weights (unfrozen)
        count += len(self._doc_bias_offsets)  # per-doc biases
        count += len(self.path_weights)  # 4 path weights
        count += len(self.resonance_weights)  # 6 resonance weights
        count += len(self.desire_weights)  # 4 desire weights
        count += 2  # bridge_modulation + geo_arith_blend
        return count

    def apply_swarm_deltas(self, deltas: dict) -> dict:
        """Apply weight deltas from the swarm loss engine.

        Handles: gate, pair, bridge, seed, path, resonance, desire weight types.
        Returns summary of what was applied.
        """
        summary = {"applied": 0, "skipped": 0}

        # Gate weight deltas
        for key, delta in deltas.get("gate", {}).items():
            parts = key.split(":")
            if len(parts) == 2:
                src, dst = parts
                if src in self._gate_weights and dst in self._gate_weights[src]:
                    self._gate_weights[src][dst].value += delta
                    summary["applied"] += 1
                else:
                    summary["skipped"] += 1

        # Pair weight deltas (via doc bias offsets, always available)
        for doc_id, delta in deltas.get("pair", {}).items():
            self.update_doc_bias(doc_id, delta)
            summary["applied"] += 1

        # Bridge modulation delta
        for key, delta in deltas.get("bridge", {}).items():
            # Aggregate bridge deltas into the modulation factor
            self.bridge_modulation = max(0.05, min(0.5,
                self.bridge_modulation + delta * 0.1))
            summary["applied"] += 1

        # Seed deltas
        for key, delta in deltas.get("seed", {}).items():
            # Apply to nano seed if available
            if self._nano_seed:
                self._nano_seed.global_mean += delta
                summary["applied"] += 1

        # Path weight deltas
        for face, delta in deltas.get("path", {}).items():
            if face in self.path_weights:
                self.path_weights[face] = max(0.05, min(0.60,
                    self.path_weights[face] + delta))
                summary["applied"] += 1
        # Renormalize path weights
        total_pw = sum(self.path_weights.values())
        if total_pw > 0:
            self.path_weights = {k: v / total_pw for k, v in self.path_weights.items()}

        # Resonance weight deltas
        for key, delta in deltas.get("resonance", {}).items():
            if key in self.resonance_weights:
                self.resonance_weights[key] = max(0.05, min(0.40,
                    self.resonance_weights[key] + delta))
                summary["applied"] += 1
        # Renormalize
        total_rw = sum(self.resonance_weights.values())
        if total_rw > 0:
            self.resonance_weights = {k: v / total_rw for k, v in self.resonance_weights.items()}

        # Desire weight deltas
        for key, delta in deltas.get("desire", {}).items():
            if key in self.desire_weights:
                self.desire_weights[key] = max(0.05, min(0.50,
                    self.desire_weights[key] + delta))
                summary["applied"] += 1
        total_dw = sum(self.desire_weights.values())
        if total_dw > 0:
            self.desire_weights = {k: v / total_dw for k, v in self.desire_weights.items()}

        self._last_updated = time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        return summary

    @property
    def active_level(self) -> str:
        return self._active_level

    @property
    def total_weights(self) -> int:
        return self._total_weights

    @property
    def doc_registry(self) -> list[dict]:
        return self._doc_registry

    @property
    def shell_seeds(self) -> dict[int, ShellSeed]:
        return self._shell_seeds

    @property
    def archetype_seeds(self) -> dict[int, ArchetypeSeed]:
        return self._archetype_seeds

    @property
    def nano_seed(self) -> Optional[NanoSeed]:
        return self._nano_seed


# ── Singleton store ──────────────────────────────────────────────────

_STORE: Optional[FractalWeightStore] = None


def get_store() -> FractalWeightStore:
    """Get or create the singleton FractalWeightStore."""
    global _STORE
    if _STORE is None:
        _STORE = FractalWeightStore()
        if not _STORE.load():
            # No saved weights — import from legacy
            _STORE.import_from_legacy()
            _STORE.save()
    return _STORE


def reset_store() -> None:
    """Reset the singleton (for testing / reimport)."""
    global _STORE
    _STORE = None


# ── MCP tool entry point ─────────────────────────────────────────────


def query_crystal_weights(coordinate: str = "all", level: str = "seed") -> str:
    """Query neural network weights stored inside the crystal coordinate system.

    Components:
      - all         : Overview of crystal weight state
      - shell:N     : Shell seed N (1-36)
      - archetype:N : Archetype seed N (1-12)
      - gate:GXX    : Gate matrix row GXX
      - nano        : Global nano-seed distribution
      - stats       : Compression statistics
      - decompress:N: Decompressed weights for shell N
    """
    store = get_store()
    comp = coordinate.strip().lower()

    if comp == "all":
        return _format_all(store)
    if comp == "nano":
        return _format_nano(store)
    if comp == "stats":
        return _format_stats(store)
    if comp.startswith("shell:"):
        try:
            shell = int(comp.split(":")[1])
            return _format_shell(store, shell)
        except (ValueError, IndexError):
            return "Usage: shell:N where N is 1-36"
    if comp.startswith("archetype:"):
        try:
            arch = int(comp.split(":")[1])
            return _format_archetype(store, arch)
        except (ValueError, IndexError):
            return "Usage: archetype:N where N is 1-12"
    if comp.startswith("gate:"):
        gate = comp.split(":")[1].upper()
        return _format_gate(store, gate)
    if comp.startswith("decompress:"):
        try:
            shell = int(comp.split(":")[1])
            return _format_decompress(store, shell)
        except (ValueError, IndexError):
            return "Usage: decompress:N where N is 1-36"

    return (
        f"Unknown component '{coordinate}'. "
        "Use: all, shell:N, archetype:N, gate:GXX, nano, stats, decompress:N"
    )


def _format_all(store: FractalWeightStore) -> str:
    lines = [
        "## Crystal-Internal Neural Weights\n",
        f"**Active Level**: {store.active_level}",
        f"**Total Weights**: {store.total_weights:,}",
        f"**Shell Seeds**: {len(store.shell_seeds)} / {TOTAL_SHELLS}",
        f"**Archetype Seeds**: {len(store.archetype_seeds)} / 12",
        f"**Nano Seed**: {'present' if store.nano_seed else 'absent'}",
        f"**Gate Matrix**: {sum(len(d) for d in store._gate_weights.values())} cells",
        f"**Last Updated**: {store._last_updated}\n",
        "### Compression Cascade (1/8 Lift Law)\n",
        "| Level | Size | Description |",
        "|-------|------|-------------|",
        f"| Full | {store.total_weights:,} | All pair + gate weights |",
        f"| 1/8 seed | {len(store.shell_seeds)} | Per-shell summaries |",
        f"| 1/64 micro | {len(store.archetype_seeds)} | Per-archetype averages |",
        f"| 1/512 nano | {'4' if store.nano_seed else '0'} | Global distribution |",
    ]

    if store.nano_seed:
        ns = store.nano_seed
        lines.extend([
            f"\n### Nano Seed (Global Distribution)\n",
            f"- **Mean**: {ns.global_mean:.4f}",
            f"- **Std**: {ns.global_std:.4f}",
            f"- **Skew**: {ns.skew:.4f}",
            f"- **Kurtosis**: {ns.kurtosis:.4f}",
            f"- **Total Count**: {ns.total_count:,}",
        ])

    # Shell seed overview
    if store.shell_seeds:
        lines.extend(["\n### Shell Seeds (1/8 compressed)\n",
                       "| Shell | Wreath | Mean | Std | Count |",
                       "|-------|--------|------|-----|-------|"])
        for s in sorted(store.shell_seeds.keys()):
            seed = store.shell_seeds[s]
            lines.append(f"| S{s} | {seed.wreath} | {seed.mean:.3f} | {seed.std:.3f} | {seed.count} |")

    return "\n".join(lines)


def _format_shell(store: FractalWeightStore, shell: int) -> str:
    seed = store.get_shell_seed(shell)
    if not seed:
        return f"No seed for shell {shell}."
    lines = [
        f"## Shell Seed S{shell}\n",
        f"**Wreath**: {seed.wreath}",
        f"**Mean**: {seed.mean:.6f}",
        f"**Std**: {seed.std:.6f}",
        f"**Count**: {seed.count}",
        f"**Range**: [{seed.min_val:.3f}, {seed.max_val:.3f}]",
    ]
    if seed.element_dist:
        lines.append(f"\n**Element Distribution**:")
        for e, frac in sorted(seed.element_dist.items()):
            lines.append(f"  - {e}: {frac:.1%}")
    if seed.gate_means:
        lines.append(f"\n**Gate Means**:")
        for g, m in sorted(seed.gate_means.items()):
            lines.append(f"  - {g}: {m:.4f}")
    return "\n".join(lines)


def _format_archetype(store: FractalWeightStore, arch: int) -> str:
    seed = store.get_archetype_seed(arch)
    if not seed:
        return f"No seed for archetype {arch}."
    lines = [
        f"## Archetype Seed A{arch}: {seed.name}\n",
        f"**Mean**: {seed.mean:.6f}",
        f"**Std**: {seed.std:.6f}",
        f"**Count**: {seed.count}",
        f"**Shells**: S{seed.shells[0]}, S{seed.shells[1]}, S{seed.shells[2]}",
    ]
    if seed.wreath_means:
        lines.append(f"\n**Wreath Means**:")
        for w, m in seed.wreath_means.items():
            lines.append(f"  - {w}: {m:.4f}")
    return "\n".join(lines)


def _format_gate(store: FractalWeightStore, gate: str) -> str:
    if gate not in store._gate_weights:
        return f"No gate data for {gate}."
    lines = [f"## Gate Matrix Row: {gate}\n",
             "| Target | Weight | Count | Coordinate |",
             "|--------|--------|-------|------------|"]
    for dst, cw in sorted(store._gate_weights[gate].items()):
        lines.append(f"| {dst} | {cw.value:.4f} | {cw.count} | `{cw.coordinate}` |")
    return "\n".join(lines)


def _format_nano(store: FractalWeightStore) -> str:
    ns = store.nano_seed
    if not ns:
        return "No nano seed computed."
    lines = [
        "## Nano Seed (1/512 — Global Distribution)\n",
        f"**Global Mean**: {ns.global_mean:.6f}",
        f"**Global Std**: {ns.global_std:.6f}",
        f"**Skew**: {ns.skew:.6f}",
        f"**Kurtosis**: {ns.kurtosis:.6f}",
        f"**Total Count**: {ns.total_count:,}",
    ]
    if ns.element_means:
        lines.append("\n**Element Means**:")
        for e, m in sorted(ns.element_means.items()):
            lines.append(f"  - {e}: {m:.4f}")
    if ns.gate_means:
        lines.append("\n**Gate Means**:")
        for g, m in sorted(ns.gate_means.items()):
            lines.append(f"  - {g}: {m:.4f}")
    return "\n".join(lines)


def _format_stats(store: FractalWeightStore) -> str:
    lines = [
        "## Crystal Weight Compression Statistics\n",
        f"**Import Stats**: {json.dumps(store._import_stats, indent=2)}",
    ]

    if store.shell_seeds:
        all_means = [s.mean for s in store.shell_seeds.values()]
        all_counts = [s.count for s in store.shell_seeds.values()]
        lines.extend([
            f"\n### Shell Seed Statistics",
            f"- **Shells with data**: {len(store.shell_seeds)}",
            f"- **Total entries across shells**: {sum(all_counts):,}",
            f"- **Mean of means**: {sum(all_means) / len(all_means):.4f}",
            f"- **Min mean**: {min(all_means):.4f} (S{min(store.shell_seeds, key=lambda s: store.shell_seeds[s].mean)})",
            f"- **Max mean**: {max(all_means):.4f} (S{max(store.shell_seeds, key=lambda s: store.shell_seeds[s].mean)})",
        ])

    # Compression ratio
    full_size = store.total_weights
    seed_size = len(store.shell_seeds)
    micro_size = len(store.archetype_seeds)
    if full_size > 0:
        lines.extend([
            f"\n### Compression Ratios",
            f"- Full → Seed: {full_size:,} → {seed_size} ({full_size / max(seed_size, 1):.0f}:1)",
            f"- Seed → Micro: {seed_size} → {micro_size} ({seed_size / max(micro_size, 1):.1f}:1)",
            f"- Micro → Nano: {micro_size} → 4 ({micro_size / 4:.1f}:1)",
            f"- Full → Nano: {full_size:,} → 4 ({full_size / 4:.0f}:1)",
        ])

    return "\n".join(lines)


def _format_decompress(store: FractalWeightStore, shell: int) -> str:
    result = store.decompress_from_seed(shell)
    if not result:
        return f"Cannot decompress shell {shell} — no seed data."
    lines = [
        f"## Decompressed Weights for Shell S{shell}\n",
        f"**Blended Mean**: {result['mean']:.6f}",
        f"**Blended Std**: {result['std']:.6f}",
        f"**Count**: {result['count']}",
        f"**Shell Contribution (φ⁻¹)**: {result.get('shell_contribution', 'N/A')}",
        f"**Archetype Contribution**: {result.get('archetype_contribution', 'N/A')}",
        f"**Reconstruction Error**: {result.get('reconstruction_error', 'N/A')}",
    ]
    return "\n".join(lines)
