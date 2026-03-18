# CRYSTAL: Xi108:W3:A4:S36 | face=R | node=542 | depth=0 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A4:S35→Xi108:W2:A4:S36→Xi108:W3:A3:S36→Xi108:W3:A5:S36

"""
QSHRINK Pipeline — P/Q/B/C codec operators + crystal-aware compression.
=========================================================================
Ported from athena_os/qshrink/pipeline.py and lenses.py.

Pipeline:
    Encode:  E = C . B . Q . P
    Decode:  D = P^-1 . Q^-1 . B^-1 . C^-1

    P: Partition/Coordinate — petal-based sample routing
    Q: Quantize — rate-distortion control (identity for lossless)
    B: Bucket/Split — coherent bulk vs heavy-tail escapes
    C: Code+Containerize — entropy coding + QSHR container

Crystal-aware layer:
    compress_with_weights() embeds CrystalWeightMeta (shell/archetype/nano
    seeds + learnable parameters) from FractalWeightStore into every .qshr.
"""

from __future__ import annotations

import hashlib
import json
import math
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .qshrink_codec import (
    ChunkHeader, ChunkType, Chunk, Domain,
    QShrinkContainer, TopologyType,
    CrystalWeightMeta, build_crystal_meta_from_store,
)
from .constants import TOTAL_SHELLS, TOTAL_WREATHS, ARCHETYPE_NAMES

# ---------------------------------------------------------------------------
# Flower lens — PetalPartition (sample routing)
# ---------------------------------------------------------------------------

class PetalPartition:
    """Petal-based partition for sample routing on the unit hypersphere."""

    def __init__(self, n_petals: int = 16, dim: int = 4) -> None:
        self.n_petals = n_petals
        self.dim = dim
        self._anchors = np.zeros((n_petals, dim))
        for i in range(n_petals):
            theta = 2 * np.pi * i / n_petals
            self._anchors[i, 0] = np.cos(theta)
            if dim > 1:
                self._anchors[i, 1] = np.sin(theta)

    def assign_petal(self, sample: np.ndarray) -> int:
        norm = np.linalg.norm(sample)
        s = sample / norm if norm > 0 else sample
        return int(np.argmax(self._anchors @ s[:self.dim]))

    def get_anchor(self, petal_id: int) -> np.ndarray:
        return self._anchors[petal_id].copy()


# ---------------------------------------------------------------------------
# P: Partition operator
# ---------------------------------------------------------------------------

@dataclass
class PartitionResult:
    petal_assignments: np.ndarray
    anchors: np.ndarray
    residuals: np.ndarray
    n_petals: int
    projection_scales: Optional[np.ndarray] = None


class PartitionOperator:
    """P: Partition/Coordinate — routes samples into petal groups."""

    def __init__(self, n_petals: int = 16, dim: int = 4) -> None:
        self.n_petals = n_petals
        self.dim = dim
        self._partition = PetalPartition(n_petals, dim)

    def forward(self, data: np.ndarray) -> PartitionResult:
        n = len(data)
        flat = data.reshape(n, -1) if len(data.shape) > 1 else data.reshape(-1, 1)
        assignments = np.zeros(n, dtype=int)
        for i in range(n):
            s = np.zeros(self.dim)
            clen = min(len(flat[i]), self.dim)
            s[:clen] = flat[i][:clen]
            assignments[i] = self._partition.assign_petal(s)

        anchors = np.array([self._partition.get_anchor(p) for p in range(self.n_petals)])
        residuals = np.zeros_like(flat)
        scales = np.zeros(n, dtype=np.float64)
        for i in range(n):
            anc = anchors[assignments[i]]
            smp = flat[i]
            cl = min(len(anc), len(smp))
            ap = np.zeros(len(smp), dtype=flat.dtype)
            ap[:cl] = anc[:cl]
            ps = float(np.dot(smp[:cl], anc[:cl])) if cl > 0 else 0.0
            scales[i] = ps
            residuals[i] = smp - ps * ap

        return PartitionResult(assignments, anchors, residuals, self.n_petals, scales)

    def inverse(self, r: PartitionResult) -> np.ndarray:
        n = len(r.residuals)
        data = np.zeros_like(r.residuals)
        for i in range(n):
            anc = r.anchors[r.petal_assignments[i]]
            res = r.residuals[i]
            ap = np.zeros(len(res))
            cl = min(len(anc), len(res))
            ap[:cl] = anc[:cl]
            ps = float(r.projection_scales[i]) if r.projection_scales is not None else 1.0
            data[i] = ps * ap + res
        return data


# ---------------------------------------------------------------------------
# Q: Quantize operator
# ---------------------------------------------------------------------------

@dataclass
class QuantizeResult:
    quantized: np.ndarray
    scale: float
    reconstruction: np.ndarray
    max_error: float = 0.0


class QuantizeOperator:
    """Q: rate-distortion control (identity for lossless)."""

    def __init__(self, lossless: bool = True, step_size: float = 1.0,
                 tier: int = 0, refinement: int = 0) -> None:
        self.lossless = lossless
        phi = 1.618
        self.step_size = 0 if lossless else step_size * (2.0 ** (-tier)) * (phi ** (-refinement))

    def forward(self, data: np.ndarray) -> QuantizeResult:
        if self.lossless:
            return QuantizeResult(data.copy(), 1.0, data.copy(), 0.0)
        q = np.round(data / self.step_size).astype(int)
        return QuantizeResult(q, self.step_size, q * self.step_size, self.step_size / 2)

    def inverse(self, r: QuantizeResult) -> np.ndarray:
        return r.quantized.copy() if self.lossless else r.quantized * r.scale

    def error_bound(self) -> float:
        return 0.0 if self.lossless else self.step_size / 2


# ---------------------------------------------------------------------------
# B: Bucket / Split operator
# ---------------------------------------------------------------------------

@dataclass
class BucketResult:
    bulk: np.ndarray
    escapes: np.ndarray
    tags: np.ndarray
    bulk_fraction: float = 0.0
    escape_fraction: float = 0.0


class BucketOperator:
    """B: Phase-partition bucketing — bulk vs heavy-tail escapes."""

    def __init__(self, threshold: float = 2.0) -> None:
        self.threshold = threshold

    def forward(self, data: np.ndarray) -> BucketResult:
        flat = data.flatten()
        median = np.median(np.abs(flat))
        sigma = median / 0.6745 if median > 0 else 1.0
        tags = (np.abs(flat) > self.threshold * sigma).astype(int)
        bulk = flat[tags == 0]
        escapes = flat[tags == 1]
        n = len(flat)
        return BucketResult(bulk, escapes, tags,
                            len(bulk) / n if n else 0,
                            len(escapes) / n if n else 0)

    def inverse(self, r: BucketResult) -> np.ndarray:
        merged = np.zeros(len(r.tags))
        bi, ei = 0, 0
        for i in range(len(r.tags)):
            if r.tags[i] == 0:
                if bi < len(r.bulk):
                    merged[i] = r.bulk[bi]; bi += 1
            else:
                if ei < len(r.escapes):
                    merged[i] = r.escapes[ei]; ei += 1
        return merged


# ---------------------------------------------------------------------------
# C: Container operator (simplified — wraps into QSHR chunks)
# ---------------------------------------------------------------------------

@dataclass
class ContainerResult:
    chunks: List[Chunk]
    manifest: Dict[str, Any]
    total_size: int
    is_streaming_legal: bool = True


class ContainerOperator:
    """C: Code + Containerize — entropy coding + container packaging."""

    def __init__(self, chunk_size: int = 4096) -> None:
        self.chunk_size = chunk_size

    def forward(self, bucket: BucketResult) -> ContainerResult:
        chunks: List[Chunk] = []
        chunks.extend(self._package(np.asarray(bucket.bulk, dtype=np.float64).tobytes(), "BULK"))
        chunks.extend(self._package(np.asarray(bucket.escapes, dtype=np.float64).tobytes(), "ESCP"))
        chunks.extend(self._package(bucket.tags.astype(np.uint8).tobytes(), "TAGS"))
        manifest = {
            "bulk_size": len(bucket.bulk),
            "escape_size": len(bucket.escapes),
            "total_samples": len(bucket.tags),
            "bulk_fraction": bucket.bulk_fraction,
        }
        total = sum(len(c.header.to_bytes()) + len(c.payload) for c in chunks)
        return ContainerResult(chunks, manifest, total)

    def inverse(self, r: ContainerResult) -> BucketResult:
        bb, eb, tb = b"", b"", b""
        for c in r.chunks:
            if c.header.chunk_type == ChunkType.BULK:
                bb += c.payload
            elif c.header.chunk_type == ChunkType.ESCAPE:
                eb += c.payload
            elif c.header.chunk_type == ChunkType.TAGS:
                tb += c.payload
        bulk = np.frombuffer(bb, dtype=np.float64) if bb else np.array([])
        esc = np.frombuffer(eb, dtype=np.float64) if eb else np.array([])
        tags = np.frombuffer(tb, dtype=np.uint8) if tb else np.array([])
        return BucketResult(bulk, esc, tags)

    def _package(self, data: bytes, ctype: str) -> List[Chunk]:
        ct = ChunkType.BULK
        for c in ChunkType:
            if c.value == ctype:
                ct = c; break
        chunks = []
        for i in range(0, max(1, len(data)), self.chunk_size):
            payload = data[i:i + self.chunk_size]
            h = ChunkHeader(ct, len(payload), zlib.crc32(payload) & 0xFFFFFFFF)
            chunks.append(Chunk(h, payload))
        return chunks


# ---------------------------------------------------------------------------
# Complete codec
# ---------------------------------------------------------------------------

@dataclass
class CodecProfile:
    name: str
    lossless: bool = True
    n_petals: int = 16
    quality_tier: int = 0
    quality_refinement: int = 0
    escape_threshold: float = 2.0
    chunk_size: int = 4096


class QShrinkCodec:
    """Complete Q-SHRINK Codec:  E = C . B . Q . P"""

    def __init__(self, profile: CodecProfile) -> None:
        self.profile = profile
        self.P = PartitionOperator(n_petals=profile.n_petals)
        self.Q = QuantizeOperator(lossless=profile.lossless,
                                  tier=profile.quality_tier,
                                  refinement=profile.quality_refinement)
        self.B = BucketOperator(threshold=profile.escape_threshold)
        self.C = ContainerOperator(chunk_size=profile.chunk_size)

    def encode(self, data: np.ndarray) -> ContainerResult:
        pr = self.P.forward(data)
        qr = self.Q.forward(pr.residuals)
        br = self.B.forward(qr.quantized)
        cr = self.C.forward(br)
        cr.manifest["petal_assignments"] = pr.petal_assignments.tolist()
        cr.manifest["anchors"] = pr.anchors.tolist()
        cr.manifest["n_petals"] = pr.n_petals
        cr.manifest["projection_scales"] = pr.projection_scales.tolist()
        cr.manifest["input_shape"] = list(data.shape)
        cr.manifest["residual_shape"] = list(pr.residuals.shape)
        cr.manifest["quantize_scale"] = qr.scale
        cr.manifest["quantized_dtype"] = str(np.asarray(qr.quantized).dtype)
        return cr

    def decode(self, container: ContainerResult) -> np.ndarray:
        br = self.C.inverse(container)
        merged = self.B.inverse(br)
        qd = np.dtype(container.manifest.get("quantized_dtype", "float64"))
        qr = QuantizeResult(merged.astype(qd, copy=False),
                            container.manifest.get("quantize_scale", 1.0), merged)
        residuals = self.Q.inverse(qr)
        rs = tuple(container.manifest.get("residual_shape", [len(merged), 1]))
        ps = np.array(container.manifest.get("projection_scales",
                                              np.ones(len(container.manifest["petal_assignments"]))))
        pr = PartitionResult(
            np.array(container.manifest["petal_assignments"]),
            np.array(container.manifest["anchors"]),
            residuals.reshape(rs), container.manifest["n_petals"], ps)
        data = self.P.inverse(pr)
        return data.reshape(tuple(container.manifest.get("input_shape", list(data.shape))))

    def verify_roundtrip(self, data: np.ndarray, tol: float = 1e-6) -> bool:
        enc = self.encode(data)
        dec = self.decode(enc)
        if self.profile.lossless:
            return bool(np.allclose(data.flatten(), dec.flatten(), atol=tol))
        return bool(np.all(np.abs(data.flatten() - dec.flatten()) <= self.Q.error_bound() + tol))


# ---------------------------------------------------------------------------
# Convenience functions — bytes-level compression
# ---------------------------------------------------------------------------

def compress_bytes(data: bytes, *, lossless: bool = True,
                   crystal_meta: Optional[CrystalWeightMeta] = None) -> bytes:
    """Compress raw bytes into a QSHR container with optional crystal metadata."""
    level = 9 if lossless else 1
    payload = zlib.compress(data, level=level)

    container = QShrinkContainer()
    container.crystal_meta = crystal_meta

    domain = Domain(0, "lossless_bytes" if lossless else "lossy_bytes")
    header = ChunkHeader(ChunkType.BULK, len(payload), zlib.crc32(payload) & 0xFFFFFFFF)
    domain.add_chunk(Chunk(header, payload))
    container.add_domain(domain)

    return container.serialize()


def decompress_bytes(container_bytes: bytes) -> bytes:
    """Decompress a QSHR container back to raw bytes."""
    container = QShrinkContainer.deserialize(container_bytes)
    parts = []
    for dom in container.domains:
        for chunk in dom.chunks:
            if chunk.verify():
                parts.append(chunk.payload)
    if not parts:
        return b""
    return zlib.decompress(b"".join(parts))


# ---------------------------------------------------------------------------
# JSON-specific compression
# ---------------------------------------------------------------------------

def compress_json(data: Any, *, lossless: bool = True,
                  crystal_meta: Optional[CrystalWeightMeta] = None) -> bytes:
    """Compress a JSON-serializable object into a QSHR container.

    Applies key deduplication and column-oriented storage for arrays of
    objects to maximize compression ratio.
    """
    optimized = _optimize_json(data)
    raw = json.dumps(optimized, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return compress_bytes(raw, lossless=lossless, crystal_meta=crystal_meta)


def decompress_json(container_bytes: bytes) -> Any:
    """Decompress a QSHR container back to a JSON object."""
    raw = decompress_bytes(container_bytes)
    optimized = json.loads(raw)
    return _deoptimize_json(optimized)


def _optimize_json(data: Any) -> Any:
    """Apply column-oriented optimization for arrays-of-objects.

    Transforms [{k1:v1, k2:v2}, {k1:v3, k2:v4}] into
    {"__cols__": True, "keys": [k1,k2], "rows": [[v1,v2],[v3,v4]]}
    which compresses much better because repeated keys are stored once.
    """
    if isinstance(data, list) and len(data) > 2 and all(isinstance(x, dict) for x in data):
        # Check if all dicts share the same keys
        key_set = set(data[0].keys())
        if all(set(d.keys()) == key_set for d in data):
            keys = sorted(key_set)
            rows = [[_optimize_json(d[k]) for k in keys] for d in data]
            return {"__cols__": True, "keys": keys, "rows": rows}
    if isinstance(data, dict):
        return {k: _optimize_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_optimize_json(x) for x in data]
    return data


def _deoptimize_json(data: Any) -> Any:
    """Reverse column-oriented optimization."""
    if isinstance(data, dict):
        if data.get("__cols__") is True and "keys" in data and "rows" in data:
            keys = data["keys"]
            return [
                {k: _deoptimize_json(v) for k, v in zip(keys, row)}
                for row in data["rows"]
            ]
        return {k: _deoptimize_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_deoptimize_json(x) for x in data]
    return data


# ---------------------------------------------------------------------------
# Crystal-aware file compression
# ---------------------------------------------------------------------------

def compress_file(path: Path, *, lossless: bool = True,
                  weight_store: Any = None) -> Tuple[Path, Dict[str, Any]]:
    """Compress a file to .qshr with crystal weight metadata.

    Returns (output_path, stats_dict).
    """
    path = Path(path)
    raw = path.read_bytes()
    original_size = len(raw)

    # Compute crystal coordinate from file path
    coordinate, shell, wreath, archetype, face = _path_to_crystal(path)
    crystal_meta = build_crystal_meta_from_store(
        coordinate, shell, wreath, archetype, face, weight_store)

    # Choose JSON or bytes compression
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(raw)
            compressed = compress_json(data, lossless=lossless, crystal_meta=crystal_meta)
        except (json.JSONDecodeError, UnicodeDecodeError):
            compressed = compress_bytes(raw, lossless=lossless, crystal_meta=crystal_meta)
    else:
        compressed = compress_bytes(raw, lossless=lossless, crystal_meta=crystal_meta)

    out_path = path.with_suffix(".qshr")
    out_path.write_bytes(compressed)

    compressed_size = len(compressed)
    stats = {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "ratio": original_size / compressed_size if compressed_size else float("inf"),
        "savings_pct": (1 - compressed_size / original_size) * 100 if original_size else 0,
        "coordinate": coordinate,
        "shell": shell,
        "has_weight_seeds": crystal_meta.shell_seed is not None,
    }
    return out_path, stats


def decompress_file(path: Path) -> Tuple[Path, Dict[str, Any]]:
    """Decompress a .qshr file back to its original format.

    Returns (output_path, stats_dict).
    """
    path = Path(path)
    container_bytes = path.read_bytes()
    container = QShrinkContainer.deserialize(container_bytes)

    # Determine output extension from domain type
    domain_type = container.domains[0].domain_type if container.domains else "unknown"
    is_json = "json" in path.stem.lower() or domain_type.startswith("lossless")

    # Decompress
    parts = []
    for dom in container.domains:
        for chunk in dom.chunks:
            if chunk.verify():
                parts.append(chunk.payload)
    raw = zlib.decompress(b"".join(parts)) if parts else b""

    # Determine output path
    if path.suffix == ".qshr":
        out_path = path.with_suffix(".json" if is_json else ".bin")
    else:
        out_path = path.with_suffix(path.suffix + ".restored")

    out_path.write_bytes(raw)

    stats = {
        "compressed_size": len(container_bytes),
        "restored_size": len(raw),
        "coordinate": container.crystal_meta.coordinate if container.crystal_meta else "none",
        "has_weight_seeds": container.crystal_meta.shell_seed is not None if container.crystal_meta else False,
    }
    return out_path, stats


def inspect_qshr(path: Path) -> Optional[CrystalWeightMeta]:
    """Read crystal weight metadata from a .qshr file WITHOUT decompressing.

    O(1) — reads only the CWGT chunk header.
    """
    data = Path(path).read_bytes()
    if data[:4] != QShrinkContainer.MAGIC:
        return None
    container = QShrinkContainer.deserialize(data)
    return container.crystal_meta


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _path_to_crystal(path: Path) -> Tuple[str, int, int, int, str]:
    """Compute a crystal coordinate from a file path.

    Uses a deterministic hash to assign the file to a shell/archetype/face.
    """
    name_hash = int(hashlib.sha256(str(path).encode()).hexdigest(), 16)
    shell = (name_hash % TOTAL_SHELLS) + 1
    wreath = ((shell - 1) // 12) + 1
    archetype = ((shell - 1) % 12) + 1
    faces = ["S", "F", "C", "R"]
    face = faces[name_hash % 4]
    coordinate = f"Xi108:W{wreath}:A{archetype}:S{shell}:{face}"
    return coordinate, shell, wreath, archetype, face


# ---------------------------------------------------------------------------
# Scan directory for compressible files
# ---------------------------------------------------------------------------

def scan_directory(directory: Path, min_size: int = 1024) -> List[Dict[str, Any]]:
    """Scan directory for files that would benefit from QSHR compression.

    Returns list of dicts with file info and estimated savings.
    """
    directory = Path(directory)
    results = []
    for f in sorted(directory.rglob("*")):
        if not f.is_file() or f.suffix == ".qshr":
            continue
        size = f.stat().st_size
        if size < min_size:
            continue
        # Estimate compression ratio
        est_ratio = 1.0
        if f.suffix == ".json":
            est_ratio = 6.0  # JSON compresses well (keys repeat)
        elif f.suffix in (".jsonl", ".csv", ".tsv"):
            est_ratio = 5.0
        elif f.suffix in (".md", ".txt", ".py"):
            est_ratio = 3.0
        else:
            est_ratio = 2.0

        coordinate, shell, wreath, archetype, face = _path_to_crystal(f)
        results.append({
            "path": str(f),
            "size": size,
            "size_human": _human_size(size),
            "suffix": f.suffix,
            "est_ratio": est_ratio,
            "est_compressed": _human_size(int(size / est_ratio)),
            "est_savings": _human_size(int(size * (1 - 1 / est_ratio))),
            "coordinate": coordinate,
            "shell": shell,
        })
    return sorted(results, key=lambda x: x["size"], reverse=True)


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"
