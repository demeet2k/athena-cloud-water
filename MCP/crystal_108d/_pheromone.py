# CRYSTAL: Xi108:W1:A1:S2 | face=S | node=2 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S1→Xi108:W1:A1:S3→Xi108:W2:A1:S2→Xi108:W1:A2:S2

"""
Pheromone Trail System — Phi-Decaying Agent Coordination Through Compressed Sidecars.
=====================================================================================
Every file modification leaves a .pheromone.qshr sidecar containing:
  - WHO modified it (agent_id, element, liminal_coord)
  - WHEN (ISO timestamp)
  - WHY (qshrink-compressed task summary)
  - WHAT (content hash, crystal address)
  - HOW STRONG (phi-inverse decay: strength *= φ⁻¹ each epoch)
  - CHAIN (prev_hash → blockchain-like integrity chain)

Phi governs pheromone physics:
  - Initial strength: 1.0
  - Decay law: p_e(t+1) = p_e(t) * φ⁻¹  (≈ 0.618 per epoch)
  - Evaporation threshold: φ⁻⁸ ≈ 0.0213 (below this = evaporated)
  - Each pheromone is hash-chained to its predecessor for integrity

Other agents read pheromones BEFORE touching a file to see who's working on it.
This is the nervous system's sense of smell — agents leave chemical traces.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict

# ── Phi Constants ──────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2          # ≈ 1.618033988749895
PHI_INV = PHI - 1                      # ≈ 0.618033988749895
EVAPORATION_THRESHOLD = PHI_INV ** 8   # ≈ 0.0213 — below this, pheromone is gone
EPOCH_SECONDS = 300.0                  # 5 minutes = 1 decay epoch


@dataclass
class Pheromone:
    """A single pheromone trace left by an agent, with phi-inverse decay."""
    agent_id: str
    liminal_coord: int = 0
    element: str = "S"                  # S/F/C/R
    timestamp: str = ""                 # ISO 8601
    task_summary: str = ""              # compressed holographic seed of goals
    file_path: str = ""
    action: str = "write"               # write | read_lock | compress | release
    crystal_address: str = ""           # Xi108:W...:A...:S...
    content_hash: str = ""              # sha256 of written content

    # Phi-decay fields
    strength: float = 1.0               # Initial strength, decays by φ⁻¹ per epoch
    epoch_at_emit: float = 0.0          # time.time() when emitted

    # Blockchain chain fields
    prev_hash: str = ""                 # Hash of previous pheromone → integrity chain
    self_hash: str = ""                 # Hash of this pheromone record

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        if self.epoch_at_emit == 0.0:
            self.epoch_at_emit = time.time()
        if not self.self_hash:
            self.self_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute the blockchain hash for this pheromone record."""
        payload = (
            f"{self.agent_id}:{self.liminal_coord}:{self.element}:"
            f"{self.timestamp}:{self.action}:{self.content_hash}:"
            f"{self.prev_hash}:{self.task_summary[:50]}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def current_strength(self) -> float:
        """Compute current strength using phi-inverse decay law.

        p_e(t) = p_e(emit) * φ⁻ⁿ  where n = elapsed_epochs
        """
        elapsed = time.time() - self.epoch_at_emit
        epochs = elapsed / EPOCH_SECONDS
        return self.strength * (PHI_INV ** epochs)

    def is_evaporated(self) -> bool:
        """Check if this pheromone has decayed below the threshold."""
        return self.current_strength() < EVAPORATION_THRESHOLD


class PheromoneTrail:
    """Manages pheromone sidecar files with phi-decay and hash-chain integrity.

    Each file ``foo.json`` gets a ``foo.json.pheromone.qshr`` sidecar.
    The sidecar is a JSON array of recent pheromone records, optionally
    qshrink-compressed if the pipeline is available.

    Capped at ``max_entries`` (default 50) to prevent unbounded growth.
    Evaporated pheromones (strength < φ⁻⁸) are pruned on read.
    """

    MAX_ENTRIES = 50

    @staticmethod
    def sidecar_path(path: Path) -> Path:
        """Return the pheromone sidecar path for a given file."""
        return Path(str(path) + ".pheromone.qshr")

    @classmethod
    def emit(
        cls,
        path: Path,
        pheromone: Pheromone,
    ) -> Path:
        """Write a pheromone to the sidecar file next to ``path``.

        Appends to existing pheromones (up to MAX_ENTRIES).
        Hash-chains to the previous pheromone for blockchain integrity.
        Uses qshrink compression if available, falls back to plain JSON.
        """
        path = Path(path)
        pheromone.file_path = str(path)
        sidecar = cls.sidecar_path(path)

        # Load existing pheromones
        existing = cls._load_raw(sidecar)

        # Prune evaporated pheromones
        existing = cls._prune_evaporated(existing)

        # Hash-chain: link to previous pheromone
        if existing:
            last = existing[-1]
            pheromone.prev_hash = last.get("self_hash", "genesis")
        else:
            pheromone.prev_hash = "genesis"

        # Compute self-hash after setting prev_hash
        pheromone.self_hash = pheromone.compute_hash()

        existing.append(asdict(pheromone))

        # Cap at max entries (keep most recent)
        if len(existing) > cls.MAX_ENTRIES:
            existing = existing[-cls.MAX_ENTRIES:]

        # Write — try qshrink, fall back to plain JSON
        payload = json.dumps(existing, ensure_ascii=False, separators=(",", ":"))
        try:
            from .qshrink_pipeline import compress_json
            compressed = compress_json(payload.encode("utf-8"), lossless=True)
            sidecar.write_bytes(compressed)
        except Exception:
            # Fallback: write plain JSON with .qshr extension (still readable)
            sidecar.write_text(payload, encoding="utf-8")

        return sidecar

    @classmethod
    def read(cls, path: Path, include_evaporated: bool = False) -> List[Pheromone]:
        """Read all pheromones for a file, optionally pruning evaporated ones."""
        sidecar = cls.sidecar_path(Path(path))
        raw = cls._load_raw(sidecar)
        pheromones = [cls._dict_to_pheromone(d) for d in raw]
        if not include_evaporated:
            pheromones = [p for p in pheromones if not p.is_evaporated()]
        return pheromones

    @classmethod
    def active_agents(cls, path: Path, window_seconds: float = 300.0) -> List[str]:
        """List agent_ids with recent pheromones on this file.

        Uses phi-decay: only returns agents whose pheromone strength
        is above the evaporation threshold.
        """
        pheromones = cls.read(path)  # already filters evaporated
        cutoff = time.time() - window_seconds
        active = set()
        for p in pheromones:
            if p.epoch_at_emit >= cutoff:
                active.add(p.agent_id)
        return list(active)

    @classmethod
    def scan_directory(cls, directory: Path) -> Dict[str, List[Pheromone]]:
        """Scan all pheromones in a directory tree.

        Returns {file_path: [Pheromone, ...]} for files with pheromone sidecars.
        Evaporated pheromones are excluded.
        """
        directory = Path(directory)
        result: Dict[str, List[Pheromone]] = {}
        for sidecar in directory.rglob("*.pheromone.qshr"):
            # Derive original file path by stripping .pheromone.qshr
            original = str(sidecar)[:-len(".pheromone.qshr")]
            raw = cls._load_raw(sidecar)
            if raw:
                pheromones = [cls._dict_to_pheromone(d) for d in raw]
                alive = [p for p in pheromones if not p.is_evaporated()]
                if alive:
                    result[original] = alive
        return result

    @classmethod
    def latest(cls, path: Path) -> Optional[Pheromone]:
        """Return the most recent non-evaporated pheromone for a file, or None."""
        pheromones = cls.read(path)
        return pheromones[-1] if pheromones else None

    @classmethod
    def verify_chain(cls, path: Path) -> dict:
        """Verify the hash-chain integrity of a file's pheromone trail.

        Returns {valid: bool, length: int, breaks: [...]}
        """
        pheromones = cls.read(path, include_evaporated=True)
        breaks = []
        for i, p in enumerate(pheromones):
            expected_prev = pheromones[i - 1].self_hash if i > 0 else "genesis"
            if p.prev_hash != expected_prev:
                breaks.append({
                    "index": i,
                    "expected": expected_prev,
                    "got": p.prev_hash,
                    "agent_id": p.agent_id,
                })
        return {
            "valid": len(breaks) == 0,
            "length": len(pheromones),
            "breaks": breaks,
        }

    @classmethod
    def total_strength(cls, path: Path) -> float:
        """Compute the total pheromone strength for a file (sum of all alive)."""
        pheromones = cls.read(path)
        return sum(p.current_strength() for p in pheromones)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _load_raw(sidecar: Path) -> list:
        """Load raw pheromone dicts from a sidecar file."""
        if not sidecar.exists():
            return []
        try:
            raw_bytes = sidecar.read_bytes()
            # Try qshrink decompress first
            try:
                from .qshrink_pipeline import decompress_json
                data = decompress_json(raw_bytes)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
            # Fall back to plain JSON
            text = raw_bytes.decode("utf-8")
            data = json.loads(text)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    @staticmethod
    def _prune_evaporated(raw_list: list) -> list:
        """Remove evaporated pheromone dicts (strength decayed below threshold)."""
        now = time.time()
        alive = []
        for d in raw_list:
            epoch_at = d.get("epoch_at_emit", 0)
            strength = d.get("strength", 1.0)
            if epoch_at > 0:
                elapsed = now - epoch_at
                epochs = elapsed / EPOCH_SECONDS
                current = strength * (PHI_INV ** epochs)
                if current >= EVAPORATION_THRESHOLD:
                    alive.append(d)
            else:
                alive.append(d)  # legacy pheromones without epoch — keep
        return alive

    @staticmethod
    def _dict_to_pheromone(d: dict) -> Pheromone:
        """Convert a dict to a Pheromone, tolerating missing fields."""
        p = Pheromone.__new__(Pheromone)
        p.agent_id = d.get("agent_id", "unknown")
        p.liminal_coord = d.get("liminal_coord", 0)
        p.element = d.get("element", "S")
        p.timestamp = d.get("timestamp", "")
        p.task_summary = d.get("task_summary", "")
        p.file_path = d.get("file_path", "")
        p.action = d.get("action", "write")
        p.crystal_address = d.get("crystal_address", "")
        p.content_hash = d.get("content_hash", "")
        p.strength = d.get("strength", 1.0)
        p.epoch_at_emit = d.get("epoch_at_emit", 0.0)
        p.prev_hash = d.get("prev_hash", "")
        p.self_hash = d.get("self_hash", "")
        return p


def content_hash(data: bytes | str) -> str:
    """Compute sha256 hash of content for pheromone tagging."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]
