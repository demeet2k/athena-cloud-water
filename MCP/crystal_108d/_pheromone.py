# CRYSTAL: Xi108:W1:A1:S2 | face=S | node=2 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S1→Xi108:W1:A1:S3→Xi108:W2:A1:S2→Xi108:W1:A2:S2

"""
Pheromone Trail System — Agent coordination through compressed metadata sidecars.
==================================================================================
Every file modification leaves a .pheromone.qshr sidecar containing:
  - WHO modified it (agent_id, element, liminal_coord)
  - WHEN (ISO timestamp)
  - WHY (qshrink-compressed task summary)
  - WHAT (content hash, crystal address)

Other agents read pheromones BEFORE touching a file to see who's working on it.
This is the nervous system's sense of smell — agents leave chemical traces.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class Pheromone:
    """A single pheromone trace left by an agent."""
    agent_id: str
    liminal_coord: int = 0
    element: str = "S"                  # S/F/C/R
    timestamp: str = ""                 # ISO 8601
    task_summary: str = ""              # compressed holographic seed of goals
    file_path: str = ""
    action: str = "write"               # write | read_lock | compress | release
    crystal_address: str = ""           # Xi108:W...:A...:S...
    content_hash: str = ""              # sha256 of written content

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")


class PheromoneTrail:
    """Manages pheromone sidecar files for agent coordination.

    Each file ``foo.json`` gets a ``foo.json.pheromone.qshr`` sidecar.
    The sidecar is a JSON array of recent pheromone records, optionally
    qshrink-compressed if the pipeline is available.

    Capped at ``max_entries`` (default 50) to prevent unbounded growth.
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
        Uses qshrink compression if available, falls back to plain JSON.
        """
        path = Path(path)
        pheromone.file_path = str(path)
        sidecar = cls.sidecar_path(path)

        # Load existing pheromones
        existing = cls._load_raw(sidecar)
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
    def read(cls, path: Path) -> List[Pheromone]:
        """Read all pheromones for a file."""
        sidecar = cls.sidecar_path(Path(path))
        raw = cls._load_raw(sidecar)
        return [cls._dict_to_pheromone(d) for d in raw]

    @classmethod
    def active_agents(cls, path: Path, window_seconds: float = 300.0) -> List[str]:
        """List agent_ids with recent pheromones on this file.

        Default window: 5 minutes.
        """
        pheromones = cls.read(path)
        cutoff = time.time() - window_seconds
        active = set()
        for p in pheromones:
            try:
                ts = time.mktime(time.strptime(p.timestamp[:19], "%Y-%m-%dT%H:%M:%S"))
                if ts >= cutoff:
                    active.add(p.agent_id)
            except (ValueError, TypeError):
                continue
        return list(active)

    @classmethod
    def scan_directory(cls, directory: Path) -> Dict[str, List[Pheromone]]:
        """Scan all pheromones in a directory tree.

        Returns {file_path: [Pheromone, ...]} for files with pheromone sidecars.
        """
        directory = Path(directory)
        result: Dict[str, List[Pheromone]] = {}
        for sidecar in directory.rglob("*.pheromone.qshr"):
            # Derive original file path by stripping .pheromone.qshr
            original = str(sidecar)[:-len(".pheromone.qshr")]
            raw = cls._load_raw(sidecar)
            if raw:
                result[original] = [cls._dict_to_pheromone(d) for d in raw]
        return result

    @classmethod
    def latest(cls, path: Path) -> Optional[Pheromone]:
        """Return the most recent pheromone for a file, or None."""
        pheromones = cls.read(path)
        return pheromones[-1] if pheromones else None

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
    def _dict_to_pheromone(d: dict) -> Pheromone:
        """Convert a dict to a Pheromone, tolerating missing fields."""
        return Pheromone(
            agent_id=d.get("agent_id", "unknown"),
            liminal_coord=d.get("liminal_coord", 0),
            element=d.get("element", "S"),
            timestamp=d.get("timestamp", ""),
            task_summary=d.get("task_summary", ""),
            file_path=d.get("file_path", ""),
            action=d.get("action", "write"),
            crystal_address=d.get("crystal_address", ""),
            content_hash=d.get("content_hash", ""),
        )


def content_hash(data: bytes | str) -> str:
    """Compute sha256 hash of content for pheromone tagging."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]
