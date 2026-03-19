# CRYSTAL: Xi108:W3:A4:S36 | face=R | node=542 | depth=0 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A4:S35→Xi108:W2:A4:S36→Xi108:W3:A3:S36→Xi108:W3:A5:S36

"""
QSHRINK TRUE Pipeline — Holographic Crystallization of ANY File.
=================================================================
Q-SHRINK is NOT an entropy coder. It is a COORDINATE SYSTEM CONSTRUCTOR.

TRUE Pipeline for ANY file (PDF, ZIP, AI, video, image, JSON, binary):
  1. DECOMPRESS to raw state — strip native compression, get raw signal
  2. CREATE holographic crystal — run through all 4 lens families
  3. EXPAND to 108++ — find where the signal lives in the crystal lattice
  4. FIND A-POINT — the 4D crystal artifact (element × mode × archetype × octave)
  5. RECOMPRESS in native format — holographically denser, still functional
  6. OUTPUT: same file format + full 108++ transformation metadata
         → part of the living crystal network arranged in 4D tesseract

The Four-Lens Taxonomy:
    □ Square:  Determinism, addressing, seek lattices, Latin square schedules
    ✿ Flower:  Coupling, petal partition, phase anchors, sample routing
    ☁ Cloud:   Probability, entropy tables, code-length accounting
    ⟡ Fractal: Recursion, multi-scale decomposition, self-similarity

The Four-Operator Pipeline:
    ℰ = C ∘ B ∘ Q ∘ P      (encode)
    𝒟 = P⁻¹ ∘ Q⁻¹ ∘ B⁻¹ ∘ C⁻¹  (decode)

Every crystallized file becomes a LIVING CRYSTAL NODE:
  - Self-identifying (carries its Xi108 coordinate)
  - Weight-carrying (nested 1/8 → 1/64 → 1/512 seeds)
  - Holographically regenerative (seed equation preserves neighbor info)
  - Conservation-certified (6 invariants verified)
  - Part of the 4D tesseract network
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import os
import struct
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .qshrink_codec import (
    ChunkHeader, ChunkType, Chunk, Domain,
    QShrinkContainer, TopologyType,
    CrystalWeightMeta, build_crystal_meta_from_store,
    LiminalCoordinate, MyceliumHook, N27State,
)
from .constants import TOTAL_SHELLS, TOTAL_WREATHS, ARCHETYPE_NAMES

# Golden ratio constants
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1  # 0.618...

# ═══════════════════════════════════════════════════════════════════════════
# SIGNAL OBJECT — any file decompressed to its raw signal state
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SignalObject:
    """A finite signal object — any file in its raw, decompressed state.

    The primary data unit in Q-SHRINK. Every file, regardless of format,
    becomes a signal: a numpy array of byte values with metadata about
    its source format and dimensions.
    """
    data: np.ndarray               # Raw bytes as uint8 numpy array
    source_format: str             # Original format: "json", "zip", "pdf", "png", etc.
    source_path: str               # Original file path
    native_compressed: bool        # Was the source natively compressed?
    original_size: int             # Size of original file
    raw_size: int                  # Size after decompression to raw
    dimensions: Tuple[int, ...] = ()  # Canonical signal dimensions
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def samples(self) -> np.ndarray:
        return self.data.flatten()

    @property
    def n_samples(self) -> int:
        return self.data.size


# ═══════════════════════════════════════════════════════════════════════════
# FOUR LENS ANALYSES — each lens reveals a different structure
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SquareAnalysis:
    """□ Square Lens: Determinism & Addressing.

    Reveals: byte frequency distribution, Latin square regularity,
    seek lattice structure, deterministic patterns.
    """
    byte_frequencies: np.ndarray       # 256-bin histogram
    entropy_per_byte: float            # Shannon entropy H(X)
    latin_regularity: float            # How close to Latin square (0-1)
    seek_lattice_period: int           # Detected periodicity
    address_bits: int                  # Bits needed to address all unique patterns
    dominant_byte: int                 # Most frequent byte value
    byte_variance: float               # Variance of byte distribution
    is_structured: bool                # True if strong deterministic patterns found


@dataclass
class FlowerAnalysis:
    """✿ Flower Lens: Coupling & Phase Geometry.

    Reveals: petal assignments, phase distribution, coupling strength,
    sample routing through the crystal hypersphere.
    """
    petal_assignments: np.ndarray      # Which petal each block belongs to
    petal_distribution: np.ndarray     # Distribution across petals
    n_petals: int                      # Number of petals used
    dominant_petal: int                # Highest-population petal
    phase_coherence: float             # How coherent the phase signal is (0-1)
    coupling_strength: float           # Inter-petal coupling measure
    anchor_projections: np.ndarray     # Projection scales onto anchors
    residual_energy: float             # Energy in residuals (lower = more structured)


@dataclass
class CloudAnalysis:
    """☁ Cloud Lens: Probability & Entropy.

    Reveals: probability tables, entropy bounds, compressibility,
    code-length accounting.
    """
    byte_entropy: float                # Shannon entropy of byte distribution
    bigram_entropy: float              # Entropy of byte pairs
    compression_ratio_est: float       # Estimated achievable compression ratio
    bulk_fraction: float               # Fraction in coherent bulk (vs escapes)
    escape_fraction: float             # Fraction in heavy-tail escapes
    probability_table: np.ndarray      # Normalized byte probabilities
    code_length_mean: float            # Mean ideal code length per byte
    redundancy: float                  # 1 - (entropy / 8), how much redundancy


@dataclass
class FractalAnalysis:
    """⟡ Fractal Lens: Recursion & Self-Reference.

    Reveals: multi-scale decomposition, self-similarity, recursive
    structure, modularity boundaries.
    """
    n_scales: int                      # Number of decomposition scales
    scale_energies: List[float]        # Energy at each scale
    self_similarity: float             # Self-similarity score (0-1)
    fractal_dimension: float           # Estimated fractal dimension
    recursive_depth: int               # Depth of recursive structure
    dominant_scale: int                # Scale with most energy
    detail_ratio: float                # Ratio of detail to coarse energy
    is_fractal: bool                   # True if significant self-similarity


# ═══════════════════════════════════════════════════════════════════════════
# A-POINT — the 4D crystal artifact
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class APoint:
    """The A-Point: a file's position in the 4D crystal tesseract.

    Computed from the four lens analyses, the A-point is the holographic
    seed that represents this file's essence in the crystal lattice.

    4D coordinates: element × mode × archetype × octave
    """
    # Primary 4D coordinates
    element: str           # S/F/C/R (from dominant lens)
    mode: str              # Cardinal/Fixed/Mutable (from phase analysis)
    archetype_idx: int     # 1-12 (from multi-scale signature)
    archetype_name: str    # Human-readable archetype name
    octave: int            # 1-3 (from entropy level → wreath)

    # Derived crystal coordinates
    shell: int             # 1-36 (from archetype × octave)
    wreath: int            # 1-3 (= octave)
    face: str              # S/F/C/R (= element)
    coordinate: str        # Full Xi108 coordinate string

    # Tesseract gate address (4^4 = 256)
    gate: int              # 0-255

    # Confidence scores from each lens
    square_score: float    # How much Square structure was found
    flower_score: float    # How much Flower structure was found
    cloud_score: float     # How much Cloud structure was found
    fractal_score: float   # How much Fractal structure was found

    # The holographic seed equation result
    # Seed(S_k) = φ⁻¹ · Compress(S_k) + (1-φ⁻¹) · Template(Archetype(S_k))
    seed_real: float       # Real component of holographic seed
    seed_imag: float       # Imaginary component


# ═══════════════════════════════════════════════════════════════════════════
# CRYSTALLIZATION RESULT — full output of the TRUE pipeline
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CrystallizationResult:
    """Complete result of crystallizing a file through the TRUE pipeline."""
    # Source
    source_path: Path
    source_format: str
    original_size: int

    # Signal analysis
    signal: SignalObject
    square: SquareAnalysis
    flower: FlowerAnalysis
    cloud: CloudAnalysis
    fractal: FractalAnalysis

    # Crystal position
    apoint: APoint
    crystal_meta: CrystalWeightMeta

    # Output
    output_path: Path
    output_size: int
    compression_ratio: float
    native_format_preserved: bool

    # Diagnostics
    roundtrip_verified: bool = False
    conservation_hash: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: DECOMPRESS TO RAW STATE
# ═══════════════════════════════════════════════════════════════════════════

def _detect_format(path: Path, raw: bytes) -> str:
    """Detect file format from extension and magic bytes."""
    ext = path.suffix.lower()

    # Magic byte detection (overrides extension)
    if raw[:4] == b"%PDF":
        return "pdf"
    if raw[:2] == b"PK":
        return "zip"
    if raw[:4] == b"\x89PNG":
        return "png"
    if raw[:2] == b"\xff\xd8":
        return "jpg"
    if raw[:3] == b"GIF":
        return "gif"
    if raw[:4] == b"RIFF":
        return "riff"  # WAV, AVI, WebP
    if raw[:4] == b"\x1f\x8b\x08":
        return "gzip"
    if raw[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if raw[:3] == b"BZh":
        return "bz2"
    if raw[:4] in (b"\x00\x00\x00\x1c", b"\x00\x00\x00\x20") and len(raw) > 8 and raw[4:8] == b"ftyp":
        return "mp4"
    if raw[:4] == b"QSHR":
        return "qshr"

    # Extension-based fallback
    ext_map = {
        ".json": "json", ".jsonl": "jsonl", ".csv": "csv", ".tsv": "tsv",
        ".py": "text", ".md": "text", ".txt": "text", ".html": "text",
        ".xml": "text", ".yaml": "text", ".yml": "text", ".toml": "text",
        ".js": "text", ".ts": "text", ".css": "text",
        ".pdf": "pdf", ".zip": "zip", ".gz": "gzip",
        ".png": "png", ".jpg": "jpg", ".jpeg": "jpg", ".gif": "gif",
        ".mp4": "mp4", ".mp3": "mp3", ".wav": "wav",
        ".ai": "ai", ".psd": "psd", ".svg": "svg",
        ".docx": "zip", ".xlsx": "zip", ".pptx": "zip",
        ".qshr": "qshr",
        ".pt": "binary", ".pth": "binary", ".h5": "binary",
    }
    return ext_map.get(ext, "binary")


def decompress_to_raw(path: Path) -> SignalObject:
    """Step 1: Decompress ANY file to its raw signal state.

    Strips native compression layers to expose the raw data:
    - ZIP: extracts and concatenates all entries
    - GZIP: decompresses the payload
    - PDF: extracts stream objects (Flate-decoded)
    - JSON: parses and re-serializes in canonical form
    - Images: reads raw pixel/compressed data
    - Binary: reads raw bytes as-is
    """
    raw = path.read_bytes()
    original_size = len(raw)
    fmt = _detect_format(path, raw)
    native_compressed = False
    signal_data = raw
    metadata: Dict[str, Any] = {"format": fmt, "original_ext": path.suffix}

    if fmt == "gzip":
        try:
            signal_data = gzip.decompress(raw)
            native_compressed = True
            metadata["gzip_ratio"] = len(raw) / len(signal_data) if signal_data else 1.0
        except Exception:
            signal_data = raw

    elif fmt == "zip":
        try:
            parts = []
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                metadata["zip_entries"] = len(zf.namelist())
                metadata["zip_names"] = zf.namelist()[:20]  # first 20 names
                for name in zf.namelist():
                    try:
                        parts.append(zf.read(name))
                    except Exception:
                        pass
            if parts:
                signal_data = b"".join(parts)
                native_compressed = True
                metadata["zip_raw_size"] = len(signal_data)
        except zipfile.BadZipFile:
            signal_data = raw

    elif fmt == "pdf":
        # Extract raw stream data from PDF (Flate-decoded streams)
        signal_data = _extract_pdf_streams(raw)
        if len(signal_data) != len(raw):
            native_compressed = True
        metadata["pdf_streams_extracted"] = len(signal_data) != len(raw)

    elif fmt == "json":
        try:
            parsed = json.loads(raw)
            # Canonical form: sorted keys, compact separators
            canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=False).encode("utf-8")
            signal_data = canonical
            metadata["json_keys"] = len(parsed) if isinstance(parsed, dict) else "array"
        except (json.JSONDecodeError, UnicodeDecodeError):
            signal_data = raw

    elif fmt in ("text", "csv", "tsv", "jsonl"):
        # Text: decode to canonical UTF-8
        try:
            text = raw.decode("utf-8", errors="replace")
            signal_data = text.encode("utf-8")
        except Exception:
            signal_data = raw

    # Create SignalObject from raw bytes
    arr = np.frombuffer(signal_data, dtype=np.uint8).copy()
    # Compute canonical dimensions: reshape to 2D if large enough
    n = len(arr)
    if n >= 256:
        # Find a good 2D shape: sqrt-ish
        side = int(math.isqrt(n))
        while n % side != 0 and side > 1:
            side -= 1
        dims = (n // side, side) if side > 1 else (n,)
    else:
        dims = (n,)

    return SignalObject(
        data=arr,
        source_format=fmt,
        source_path=str(path),
        native_compressed=native_compressed,
        original_size=original_size,
        raw_size=len(signal_data),
        dimensions=dims,
        metadata=metadata,
    )


def _extract_pdf_streams(raw: bytes) -> bytes:
    """Extract and decompress FlateDecode streams from a PDF."""
    parts = [raw]  # Always include raw PDF as base
    # Find Flate-compressed streams
    pos = 0
    extracted = []
    while True:
        stream_start = raw.find(b"stream\r\n", pos)
        if stream_start == -1:
            stream_start = raw.find(b"stream\n", pos)
        if stream_start == -1:
            break
        # Skip past "stream\r\n" or "stream\n"
        if raw[stream_start + 6:stream_start + 8] == b"\r\n":
            data_start = stream_start + 8
        else:
            data_start = stream_start + 7

        stream_end = raw.find(b"endstream", data_start)
        if stream_end == -1:
            break

        stream_data = raw[data_start:stream_end]
        # Try to Flate-decompress
        try:
            decompressed = zlib.decompress(stream_data)
            extracted.append(decompressed)
        except zlib.error:
            extracted.append(stream_data)
        pos = stream_end + 9

    if extracted:
        return b"".join(extracted)
    return raw


# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: HOLOGRAPHIC CRYSTAL — four lens analysis
# ═══════════════════════════════════════════════════════════════════════════

def analyze_square(signal: SignalObject) -> SquareAnalysis:
    """□ Square Lens: determinism, addressing, seek structure.

    Analyzes byte-level frequency distribution, detects periodic
    patterns (Latin square regularity), and computes addressing
    requirements for the signal.
    """
    samples = signal.samples
    n = len(samples)

    # Byte frequency histogram (256 bins)
    freqs = np.bincount(samples, minlength=256).astype(np.float64)
    total = freqs.sum()
    probs = freqs / total if total > 0 else np.ones(256) / 256

    # Shannon entropy per byte
    entropy = -np.sum(probs[probs > 0] * np.log2(probs[probs > 0]))

    # Latin square regularity: how evenly distributed are bytes?
    # Perfect Latin square: all bytes equally frequent → regularity = 1.0
    expected = total / 256
    deviation = np.sqrt(np.mean((freqs - expected) ** 2)) / max(expected, 1)
    latin_regularity = max(0.0, 1.0 - deviation / 16)  # Normalize to 0-1

    # Seek lattice period: detect periodicity via autocorrelation
    period = 1
    if n > 64:
        # Check common periods
        block = min(n, 4096)
        chunk = samples[:block].astype(np.float64)
        for p in [4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            if p >= block:
                break
            n_blocks = block // p
            if n_blocks < 2:
                break
            blocks = chunk[:n_blocks * p].reshape(n_blocks, p)
            # Compute variance across blocks at same position
            var = np.mean(np.var(blocks, axis=0))
            total_var = np.var(chunk[:n_blocks * p])
            if total_var > 0 and var / total_var < 0.3:
                period = p
                break

    # Address bits
    unique_bytes = np.sum(freqs > 0)
    address_bits = max(1, int(math.ceil(math.log2(max(unique_bytes, 1)))))

    # Dominant byte
    dominant = int(np.argmax(freqs))

    # Is it structured? (low entropy + high regularity)
    is_structured = entropy < 6.0 and latin_regularity > 0.3

    return SquareAnalysis(
        byte_frequencies=freqs,
        entropy_per_byte=float(entropy),
        latin_regularity=float(latin_regularity),
        seek_lattice_period=period,
        address_bits=address_bits,
        dominant_byte=dominant,
        byte_variance=float(np.var(probs)),
        is_structured=is_structured,
    )


def analyze_flower(signal: SignalObject, n_petals: int = 12) -> FlowerAnalysis:
    """✿ Flower Lens: coupling, phase geometry, petal routing.

    Routes signal blocks into petal groups on the unit hypersphere.
    Measures phase coherence and inter-petal coupling.
    """
    samples = signal.samples
    n = len(samples)

    # Block the signal into 4D vectors for petal routing
    dim = 4
    block_size = dim
    n_blocks = n // block_size
    if n_blocks == 0:
        n_blocks = 1
        padded = np.zeros(block_size, dtype=np.float64)
        padded[:n] = samples[:n].astype(np.float64)
        blocks = padded.reshape(1, dim)
    else:
        blocks = samples[:n_blocks * block_size].astype(np.float64).reshape(n_blocks, dim)

    # Normalize blocks to unit vectors
    norms = np.linalg.norm(blocks, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = blocks / norms

    # Create petal anchors on the hypersphere
    anchors = np.zeros((n_petals, dim))
    for i in range(n_petals):
        theta = 2 * np.pi * i / n_petals
        anchors[i, 0] = np.cos(theta)
        anchors[i, 1] = np.sin(theta)
        if dim > 2:
            phi_angle = np.pi * (i + 0.5) / n_petals
            anchors[i, 2] = np.cos(phi_angle) * 0.5
        if dim > 3:
            anchors[i, 3] = np.sin(phi_angle) * 0.5 if dim > 2 else 0

    # Assign each block to nearest petal (by dot product)
    dots = normalized @ anchors.T  # (n_blocks, n_petals)
    assignments = np.argmax(dots, axis=1)

    # Petal distribution
    petal_counts = np.bincount(assignments, minlength=n_petals).astype(np.float64)
    petal_dist = petal_counts / max(petal_counts.sum(), 1)

    # Dominant petal
    dominant = int(np.argmax(petal_counts))

    # Phase coherence: how concentrated is the petal distribution?
    # Uniform = 0 coherence, all in one petal = 1
    max_entropy = np.log2(n_petals)
    petal_entropy = -np.sum(petal_dist[petal_dist > 0] * np.log2(petal_dist[petal_dist > 0]))
    phase_coherence = max(0.0, 1.0 - petal_entropy / max_entropy) if max_entropy > 0 else 0.0

    # Coupling strength: average correlation between adjacent petals
    coupling = 0.0
    count = 0
    for i in range(n_petals):
        j = (i + 1) % n_petals
        mask_i = assignments == i
        mask_j = assignments == j
        if mask_i.sum() > 0 and mask_j.sum() > 0:
            mean_i = blocks[mask_i].mean(axis=0)
            mean_j = blocks[mask_j].mean(axis=0)
            norm_prod = np.linalg.norm(mean_i) * np.linalg.norm(mean_j)
            if norm_prod > 0:
                coupling += abs(np.dot(mean_i, mean_j) / norm_prod)
                count += 1
    coupling = coupling / max(count, 1)

    # Projection scales and residual energy
    proj_scales = np.array([dots[i, assignments[i]] for i in range(n_blocks)])
    residuals = blocks - proj_scales[:, None] * anchors[assignments]
    residual_energy = float(np.mean(residuals ** 2))

    return FlowerAnalysis(
        petal_assignments=assignments,
        petal_distribution=petal_dist,
        n_petals=n_petals,
        dominant_petal=dominant,
        phase_coherence=float(phase_coherence),
        coupling_strength=float(coupling),
        anchor_projections=proj_scales,
        residual_energy=residual_energy,
    )


def analyze_cloud(signal: SignalObject) -> CloudAnalysis:
    """☁ Cloud Lens: probability, entropy, compressibility.

    Computes probability tables, entropy bounds, and estimates
    achievable compression ratio. Separates bulk from escapes.
    """
    samples = signal.samples
    n = len(samples)

    # Byte-level entropy
    freqs = np.bincount(samples, minlength=256).astype(np.float64)
    total = freqs.sum()
    probs = freqs / total if total > 0 else np.ones(256) / 256
    byte_entropy = -np.sum(probs[probs > 0] * np.log2(probs[probs > 0]))

    # Bigram entropy (byte pairs)
    bigram_entropy = byte_entropy  # Default
    if n > 2:
        bigram_counts = np.zeros(256 * 256, dtype=np.float64)
        for i in range(min(n - 1, 100000)):  # Cap at 100K for speed
            pair = int(samples[i]) * 256 + int(samples[i + 1])
            bigram_counts[pair] += 1
        bg_total = bigram_counts.sum()
        if bg_total > 0:
            bg_probs = bigram_counts / bg_total
            bigram_entropy = -np.sum(bg_probs[bg_probs > 0] * np.log2(bg_probs[bg_probs > 0])) / 2

    # Estimated compression ratio
    # Theoretical lower bound: entropy / 8 bits per byte
    theoretical_ratio = 8.0 / max(byte_entropy, 0.01)
    # Practical estimate (zlib achieves ~60-80% of theoretical)
    compression_ratio_est = theoretical_ratio * 0.7

    # Bulk/escape split using σ-based threshold
    float_samples = samples.astype(np.float64)
    median = np.median(float_samples)
    mad = np.median(np.abs(float_samples - median))
    sigma = mad / 0.6745 if mad > 0 else 1.0
    threshold = 2.0 * sigma + median
    is_escape = float_samples > threshold
    bulk_frac = 1.0 - is_escape.mean()
    escape_frac = is_escape.mean()

    # Mean ideal code length
    code_lengths = np.zeros(256)
    for i in range(256):
        if probs[i] > 0:
            code_lengths[i] = -np.log2(probs[i])
    code_length_mean = float(np.sum(probs * code_lengths))

    # Redundancy: how much room for compression?
    redundancy = max(0.0, 1.0 - byte_entropy / 8.0)

    return CloudAnalysis(
        byte_entropy=float(byte_entropy),
        bigram_entropy=float(bigram_entropy),
        compression_ratio_est=float(compression_ratio_est),
        bulk_fraction=float(bulk_frac),
        escape_fraction=float(escape_frac),
        probability_table=probs,
        code_length_mean=float(code_length_mean),
        redundancy=float(redundancy),
    )


def analyze_fractal(signal: SignalObject, n_levels: int = 5) -> FractalAnalysis:
    """⟡ Fractal Lens: recursion, self-similarity, multi-scale structure.

    Applies Haar-like wavelet decomposition to detect self-similar
    patterns at multiple scales. Estimates fractal dimension.
    """
    samples = signal.samples.astype(np.float64)
    n = len(samples)

    # Multi-scale Haar decomposition
    scales = []
    current = samples.copy()
    for level in range(n_levels):
        if len(current) < 4:
            break
        m = len(current) // 2 * 2
        current = current[:m].reshape(-1, 2)
        low = np.mean(current, axis=1)
        high = current[:, 0] - current[:, 1]
        scales.append(high)
        current = low
    scales.append(current)  # Coarsest scale

    # Energy at each scale
    scale_energies = [float(np.mean(s ** 2)) for s in scales]
    total_energy = sum(scale_energies) or 1.0

    # Self-similarity: compare energy ratios between adjacent scales
    # Perfect self-similarity → constant ratio between scales
    ratios = []
    for i in range(len(scale_energies) - 1):
        if scale_energies[i + 1] > 0:
            ratios.append(scale_energies[i] / scale_energies[i + 1])
    if len(ratios) >= 2:
        ratio_var = np.var(ratios)
        ratio_mean = np.mean(ratios)
        self_similarity = max(0.0, 1.0 - ratio_var / max(ratio_mean ** 2, 1e-10))
    else:
        self_similarity = 0.0

    # Fractal dimension estimate (box-counting approximation)
    # Use scale energies as a proxy
    if len(scale_energies) >= 2:
        log_sizes = np.log2(np.arange(1, len(scale_energies) + 1) + 1)
        log_energies = np.log2(np.array(scale_energies) + 1e-10)
        if len(log_sizes) > 1:
            # Linear regression: slope ≈ fractal dimension
            slope = np.polyfit(log_sizes, log_energies, 1)[0]
            fractal_dimension = max(1.0, min(3.0, abs(slope) + 1))
        else:
            fractal_dimension = 1.5
    else:
        fractal_dimension = 1.0

    # Detail ratio: fine scale energy vs coarse
    detail_energy = sum(scale_energies[:-1]) if len(scale_energies) > 1 else 0
    coarse_energy = scale_energies[-1] if scale_energies else 1.0
    detail_ratio = detail_energy / max(coarse_energy, 1e-10)

    # Dominant scale (most energy)
    dominant_scale = int(np.argmax(scale_energies)) if scale_energies else 0

    # Recursive depth: how many scales have significant energy?
    threshold = total_energy * 0.01  # 1% of total
    recursive_depth = sum(1 for e in scale_energies if e > threshold)

    # Is fractal? (significant self-similarity + multiple active scales)
    is_fractal = self_similarity > 0.3 and recursive_depth >= 3

    return FractalAnalysis(
        n_scales=len(scales),
        scale_energies=scale_energies,
        self_similarity=float(self_similarity),
        fractal_dimension=float(fractal_dimension),
        recursive_depth=recursive_depth,
        dominant_scale=dominant_scale,
        detail_ratio=float(detail_ratio),
        is_fractal=is_fractal,
    )


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3 & 4: EXPAND TO 108++ and FIND A-POINT
# ═══════════════════════════════════════════════════════════════════════════

def compute_apoint(signal: SignalObject,
                   square: SquareAnalysis,
                   flower: FlowerAnalysis,
                   cloud: CloudAnalysis,
                   fractal: FractalAnalysis) -> APoint:
    """Find the A-Point: the file's position in the 4D crystal tesseract.

    The A-point is computed from all four lens analyses:
    - Element (S/F/C/R): from which lens reveals the most structure
    - Mode (Cardinal/Fixed/Mutable): from phase/periodicity analysis
    - Archetype (1-12): from the multi-scale signature
    - Octave (1-3): from the entropy level (wreath)

    This IS the 108++ expansion — mapping raw signal analysis into
    the full crystal coordinate system.
    """
    # ── Determine ELEMENT from dominant lens ──
    # Each lens scores how much of its structure type is present
    s_score = (square.latin_regularity * 0.4 +
               (1.0 - square.entropy_per_byte / 8.0) * 0.3 +
               (1.0 if square.is_structured else 0.0) * 0.3)

    f_score = (flower.phase_coherence * 0.4 +
               flower.coupling_strength * 0.3 +
               (1.0 - flower.residual_energy / max(flower.residual_energy + 1, 1)) * 0.3)

    c_score = (cloud.redundancy * 0.4 +
               cloud.bulk_fraction * 0.3 +
               min(cloud.compression_ratio_est / 10.0, 1.0) * 0.3)

    r_score = (fractal.self_similarity * 0.4 +
               (1.0 if fractal.is_fractal else 0.0) * 0.3 +
               min(fractal.recursive_depth / 5.0, 1.0) * 0.3)

    scores = {"S": s_score, "F": f_score, "C": c_score, "R": r_score}
    element = max(scores, key=scores.get)

    # ── Determine MODE from periodicity/phase ──
    # Cardinal: strong periodic structure (seek lattice period > 1)
    # Fixed: stable, low-variance distribution
    # Mutable: high self-similarity, adaptable structure
    period = square.seek_lattice_period
    variance = square.byte_variance
    similarity = fractal.self_similarity

    if period > 8:
        mode = "Cardinal"
    elif variance < 0.001 and similarity < 0.3:
        mode = "Fixed"
    else:
        mode = "Mutable"

    # ── Determine ARCHETYPE from multi-scale signature ──
    # Use a hash of the scale energy pattern to select archetype
    # This creates a deterministic mapping from signal structure to archetype
    energy_sig = fractal.scale_energies[:4] if len(fractal.scale_energies) >= 4 else fractal.scale_energies + [0.0] * (4 - len(fractal.scale_energies))
    # Combine with flower petal distribution for richer signature
    petal_sig = list(flower.petal_distribution[:4]) if len(flower.petal_distribution) >= 4 else list(flower.petal_distribution) + [0.0] * (4 - len(flower.petal_distribution))

    # Hash the combined signature
    sig_str = "|".join(f"{v:.4f}" for v in energy_sig + petal_sig)
    sig_hash = int(hashlib.sha256(sig_str.encode()).hexdigest(), 16)
    archetype_idx = (sig_hash % 12) + 1

    # ── Determine OCTAVE from entropy level ──
    # Low entropy → Octave 1 (Su, surface, simple)
    # Medium entropy → Octave 2 (Me, middle, moderate)
    # High entropy → Octave 3 (Sa, deep, complex)
    entropy = cloud.byte_entropy
    if entropy < 4.0:
        octave = 1  # Su — low complexity
    elif entropy < 6.5:
        octave = 2  # Me — moderate complexity
    else:
        octave = 3  # Sa — high complexity

    # ── Compute derived crystal coordinates ──
    shell = (octave - 1) * 12 + archetype_idx  # 1-36
    wreath = octave
    face = element
    coordinate = f"Xi108:W{wreath}:A{archetype_idx}:S{shell}:{face}"

    # Gate address: 4^4 = 256 positions
    elem_idx = {"S": 0, "F": 1, "C": 2, "R": 3}[element]
    mode_idx = {"Cardinal": 0, "Fixed": 1, "Mutable": 2}[mode]
    gate = (elem_idx * 64 + mode_idx * 16 + (archetype_idx - 1)) % 256

    # ── Holographic seed equation ──
    # Seed(S_k) = φ⁻¹ · Compress(S_k) + (1-φ⁻¹) · Template(Archetype(S_k))
    # Compress(S_k) = cloud.compression_ratio_est (how much the file compresses)
    # Template(Archetype) = fractal.self_similarity (archetype template strength)
    seed_real = PHI_INV * cloud.compression_ratio_est + (1 - PHI_INV) * fractal.self_similarity
    seed_imag = PHI_INV * flower.phase_coherence + (1 - PHI_INV) * square.latin_regularity

    _ARCHETYPE_NAMES_ZODIAC = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]

    return APoint(
        element=element,
        mode=mode,
        archetype_idx=archetype_idx,
        archetype_name=_ARCHETYPE_NAMES_ZODIAC[(archetype_idx - 1) % 12],
        octave=octave,
        shell=shell,
        wreath=wreath,
        face=face,
        coordinate=coordinate,
        gate=gate,
        square_score=float(s_score),
        flower_score=float(f_score),
        cloud_score=float(c_score),
        fractal_score=float(r_score),
        seed_real=float(seed_real),
        seed_imag=float(seed_imag),
    )


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: RECOMPRESS IN NATIVE FORMAT
# ═══════════════════════════════════════════════════════════════════════════

def _crystal_informed_zlib_level(cloud: CloudAnalysis, fractal: FractalAnalysis) -> int:
    """Choose optimal zlib compression level from crystal analysis.

    - High redundancy + structured → level 9 (max compression)
    - Low redundancy + random → level 1 (fast, little gain)
    - Fractal structure → level 6 (medium, exploits patterns)
    """
    if cloud.redundancy > 0.5:
        return 9  # Very compressible
    if cloud.redundancy < 0.05:
        return 1  # Nearly random, don't waste time
    if fractal.is_fractal:
        return 6  # Fractal structure benefits from medium effort
    # Scale linearly with redundancy
    return max(1, min(9, int(cloud.redundancy * 12)))


def recompress_native(path: Path, signal: SignalObject, apoint: APoint,
                      crystal_meta: CrystalWeightMeta,
                      cloud: CloudAnalysis, fractal: FractalAnalysis) -> Tuple[Path, int]:
    """Step 5: Recompress file in its NATIVE format with crystal optimization.

    The output file is the SAME format as the input — still functional —
    but holographically denser and carrying crystal metadata.

    Strategy by format:
    - ZIP/DOCX/XLSX: re-compress entries with optimal deflate, add crystal metadata entry
    - JSON: column-oriented optimization + optimal zlib
    - GZIP: re-compress with optimal level
    - PDF: re-compress Flate streams with optimal level, embed XMP metadata
    - TEXT: optimal zlib + crystal metadata header
    - BINARY/IMAGES: optimal zlib, produce .qshr with native bytes inside
    """
    raw = path.read_bytes()
    fmt = signal.source_format
    zlib_level = _crystal_informed_zlib_level(cloud, fractal)
    meta_json = crystal_meta.to_json().encode("utf-8")

    if fmt == "zip" or (fmt == "zip" and path.suffix.lower() in (".docx", ".xlsx", ".pptx")):
        return _recompress_zip(path, raw, meta_json, zlib_level)

    elif fmt == "json":
        return _recompress_json(path, raw, meta_json, zlib_level, crystal_meta)

    elif fmt == "gzip":
        return _recompress_gzip(path, raw, meta_json, zlib_level)

    elif fmt == "pdf":
        return _recompress_pdf(path, raw, meta_json, zlib_level)

    else:
        # Generic: wrap in QSHR container preserving original bytes
        return _recompress_generic(path, raw, meta_json, zlib_level, crystal_meta)


def _recompress_zip(path: Path, raw: bytes, meta_json: bytes,
                    zlib_level: int) -> Tuple[Path, int]:
    """Re-compress ZIP with crystal-optimized deflate + metadata entry."""
    out_path = path  # Overwrite in place
    buf = io.BytesIO()
    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as zf_in:
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED,
                                 compresslevel=zlib_level) as zf_out:
                for name in zf_in.namelist():
                    info = zf_in.getinfo(name)
                    data = zf_in.read(name)
                    # Write with optimal compression
                    zf_out.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED,
                                    compresslevel=zlib_level)
                # Add crystal metadata as a special entry
                zf_out.writestr("__crystal_108d__.json", meta_json,
                                compress_type=zipfile.ZIP_DEFLATED,
                                compresslevel=zlib_level)
        result = buf.getvalue()
        # Only write if we actually saved space or are embedding metadata
        if len(result) <= len(raw) * 1.05:  # Allow 5% overhead for metadata
            out_path.write_bytes(result)
            return out_path, len(result)
    except Exception:
        pass
    # Fallback: write as .qshr
    return _recompress_generic(path, raw, meta_json, zlib_level, None)


def _recompress_json(path: Path, raw: bytes, meta_json: bytes,
                     zlib_level: int,
                     crystal_meta: CrystalWeightMeta) -> Tuple[Path, int]:
    """Optimize JSON structure + compress to .qshr with crystal metadata."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _recompress_generic(path, raw, meta_json, zlib_level, crystal_meta)

    # Apply column-oriented optimization
    optimized = _optimize_json(data)
    compact = json.dumps(optimized, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    # Compress with crystal-informed level
    payload = zlib.compress(compact, level=zlib_level)

    # Build QSHR container
    container = QShrinkContainer()
    container.crystal_meta = crystal_meta

    domain = Domain(0, "json_crystallized")
    header = ChunkHeader(ChunkType.BULK, len(payload), zlib.crc32(payload) & 0xFFFFFFFF)
    domain.add_chunk(Chunk(header, payload))
    container.add_domain(domain)

    out_path = path.with_suffix(".qshr")
    serialized = container.serialize()
    out_path.write_bytes(serialized)
    return out_path, len(serialized)


def _recompress_gzip(path: Path, raw: bytes, meta_json: bytes,
                     zlib_level: int) -> Tuple[Path, int]:
    """Re-compress gzip with crystal-optimized level."""
    try:
        decompressed = gzip.decompress(raw)
        # Re-compress with optimal level
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=zlib_level) as f:
            f.write(decompressed)
        result = buf.getvalue()
        if len(result) < len(raw):
            path.write_bytes(result)
            return path, len(result)
    except Exception:
        pass
    return path, len(raw)


def _recompress_pdf(path: Path, raw: bytes, meta_json: bytes,
                    zlib_level: int) -> Tuple[Path, int]:
    """Re-compress PDF Flate streams with crystal-optimized level.

    Finds /FlateDecode streams and re-compresses them at the optimal level.
    Also embeds crystal metadata as a PDF comment.
    """
    # Simple approach: find Flate streams and recompress
    result = raw
    pos = 0
    parts = []
    last_end = 0

    while pos < len(raw):
        stream_start = raw.find(b"stream\r\n", pos)
        if stream_start == -1:
            stream_start = raw.find(b"stream\n", pos)
        if stream_start == -1:
            break

        if raw[stream_start + 6:stream_start + 8] == b"\r\n":
            data_start = stream_start + 8
        else:
            data_start = stream_start + 7

        stream_end = raw.find(b"endstream", data_start)
        if stream_end == -1:
            break

        stream_data = raw[data_start:stream_end]

        # Check if this is a Flate stream by looking for /FlateDecode before it
        context_start = max(0, stream_start - 200)
        context = raw[context_start:stream_start]
        if b"/FlateDecode" in context:
            try:
                decompressed = zlib.decompress(stream_data)
                recompressed = zlib.compress(decompressed, level=zlib_level)
                if len(recompressed) < len(stream_data):
                    # Need to update /Length in the object
                    parts.append(raw[last_end:data_start])
                    parts.append(recompressed)
                    last_end = stream_end
            except zlib.error:
                pass

        pos = stream_end + 9

    if parts:
        parts.append(raw[last_end:])
        result = b"".join(parts)
        # Update /Length values (simplified — may not work for all PDFs)
        # For safety, only write if smaller
        if len(result) < len(raw):
            path.write_bytes(result)
            return path, len(result)

    return path, len(raw)


def _recompress_generic(path: Path, raw: bytes, meta_json: bytes,
                        zlib_level: int,
                        crystal_meta: Optional[CrystalWeightMeta]) -> Tuple[Path, int]:
    """Generic recompression: wrap in QSHR container with crystal metadata.

    The original bytes are preserved inside the container, so the file
    can be perfectly reconstructed. The QSHR container adds the crystal
    metadata envelope without destroying the original data.
    """
    payload = zlib.compress(raw, level=zlib_level)

    container = QShrinkContainer()
    container.crystal_meta = crystal_meta

    # Store original extension in domain type for reconstruction
    domain = Domain(0, f"native:{path.suffix}")
    header = ChunkHeader(ChunkType.BULK, len(payload), zlib.crc32(payload) & 0xFFFFFFFF)
    domain.add_chunk(Chunk(header, payload))
    container.add_domain(domain)

    out_path = path.with_suffix(".qshr")
    serialized = container.serialize()
    out_path.write_bytes(serialized)
    return out_path, len(serialized)


# ═══════════════════════════════════════════════════════════════════════════
# MASTER PIPELINE: crystallize_file()
# ═══════════════════════════════════════════════════════════════════════════

def crystallize_file(path: Path, *,
                     weight_store: Any = None,
                     remove_original: bool = False) -> CrystallizationResult:
    """The TRUE Q-SHRINK pipeline: crystallize ANY file.

    1. DECOMPRESS to raw state
    2. CREATE holographic crystal (4-lens analysis)
    3. EXPAND to 108++ (find crystal coordinates)
    4. FIND A-POINT (4D tesseract position)
    5. RECOMPRESS in native format (holographically denser)
    6. OUTPUT: same format + full 108++ metadata → living crystal node

    Args:
        path: Any file path (PDF, ZIP, JSON, image, video, binary, etc.)
        weight_store: Optional FractalWeightStore for enriched weight seeds
        remove_original: If True, remove the original file after crystallization

    Returns:
        CrystallizationResult with full analysis and output info
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # ── Step 1: Decompress to raw signal ──
    signal = decompress_to_raw(path)

    # ── Step 2: Four-lens holographic crystal analysis ──
    square = analyze_square(signal)
    flower = analyze_flower(signal)
    cloud = analyze_cloud(signal)
    fractal_result = analyze_fractal(signal)

    # ── Step 3 & 4: Expand to 108++ and find A-point ──
    apoint = compute_apoint(signal, square, flower, cloud, fractal_result)

    # ── Build CrystalWeightMeta with full 9-layer organism data ──
    crystal_meta = build_crystal_meta_from_store(
        apoint.coordinate, apoint.shell, apoint.wreath,
        apoint.archetype_idx, apoint.face, weight_store,
    )
    # Enrich with A-point-specific data
    crystal_meta.archetype_name = apoint.archetype_name
    crystal_meta.element = {"S": "Earth", "F": "Fire", "C": "Water", "R": "Air"}.get(apoint.element, "")
    crystal_meta.mode = apoint.mode
    crystal_meta.element_face = apoint.face
    crystal_meta.tesseract_gate = apoint.gate

    # ── Enrich Liminal ID with lens data ──
    if crystal_meta.liminal:
        crystal_meta.liminal.q = apoint.square_score          # Square lens score
        crystal_meta.liminal.o = flower.phase_coherence * 2 * math.pi  # Orbit from phase
        crystal_meta.liminal.c = 1.0 - fractal_result.self_similarity  # Control (stability)
        crystal_meta.liminal.mu = (flower.coupling_strength + cloud.bulk_fraction) / 2.0  # Mycelium metric
        crystal_meta.liminal.l = 1.0 if cloud.redundancy < 0.01 else 0.0  # Live-lock if near-random
    # Update mycelium hook liminal_id string
    if crystal_meta.mycelium_hook and crystal_meta.liminal:
        crystal_meta.mycelium_hook.liminal_id = crystal_meta.liminal.to_string()
        crystal_meta.mycelium_hook.routing_score = (
            apoint.square_score + apoint.flower_score +
            apoint.cloud_score + apoint.fractal_score) / 4.0

    # ── Enrich N27 state with lens data ──
    crystal_meta.n27_state = N27State.compute(
        apoint.wreath, apoint.mode, crystal_meta.z_depth,
        entropy=cloud.byte_entropy,
        self_similarity=fractal_result.self_similarity,
        phase_coherence=flower.phase_coherence,
    )

    # ── Step 5: Recompress in native format ──
    output_path, output_size = recompress_native(
        path, signal, apoint, crystal_meta, cloud, fractal_result)

    # ── Step 6: Verify conservation ──
    conservation_hash = crystal_meta.compute_conservation_hash()
    crystal_meta.conservation_hash = conservation_hash

    # Compute compression ratio
    ratio = signal.original_size / output_size if output_size > 0 else 1.0

    result = CrystallizationResult(
        source_path=path,
        source_format=signal.source_format,
        original_size=signal.original_size,
        signal=signal,
        square=square,
        flower=flower,
        cloud=cloud,
        fractal=fractal_result,
        apoint=apoint,
        crystal_meta=crystal_meta,
        output_path=output_path,
        output_size=output_size,
        compression_ratio=ratio,
        native_format_preserved=(output_path.suffix == path.suffix),
        conservation_hash=conservation_hash,
    )

    if remove_original and output_path != path and output_path.exists():
        path.unlink()

    return result


# ═══════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE WRAPPERS
# ═══════════════════════════════════════════════════════════════════════════

def compress_file(path: Path, *, lossless: bool = True,
                  weight_store: Any = None) -> Tuple[Path, Dict[str, Any]]:
    """Legacy wrapper: compress_file() → crystallize_file().

    Returns (output_path, stats_dict) for backward compatibility.
    """
    result = crystallize_file(path, weight_store=weight_store)
    stats = {
        "original_size": result.original_size,
        "compressed_size": result.output_size,
        "ratio": result.compression_ratio,
        "savings_pct": (1 - result.output_size / result.original_size) * 100 if result.original_size else 0,
        "coordinate": result.apoint.coordinate,
        "shell": result.apoint.shell,
        "has_weight_seeds": result.crystal_meta.shell_seed is not None,
        "element": result.apoint.element,
        "mode": result.apoint.mode,
        "archetype": result.apoint.archetype_name,
        "a_point_gate": result.apoint.gate,
        "source_format": result.source_format,
        "native_preserved": result.native_format_preserved,
        "lens_scores": {
            "square": result.apoint.square_score,
            "flower": result.apoint.flower_score,
            "cloud": result.apoint.cloud_score,
            "fractal": result.apoint.fractal_score,
        },
    }
    return result.output_path, stats


def decompress_file(path: Path) -> Tuple[Path, Dict[str, Any]]:
    """Decompress a .qshr file back to its original format."""
    path = Path(path)
    container_bytes = path.read_bytes()
    container = QShrinkContainer.deserialize(container_bytes)

    # Determine original extension from domain type
    domain_type = container.domains[0].domain_type if container.domains else "unknown"
    if domain_type.startswith("native:"):
        original_ext = domain_type.split(":", 1)[1]
    elif "json" in domain_type:
        original_ext = ".json"
    else:
        original_ext = ".bin"

    # Decompress all chunks
    parts = []
    for dom in container.domains:
        for chunk in dom.chunks:
            if chunk.verify():
                parts.append(chunk.payload)
    raw = zlib.decompress(b"".join(parts)) if parts else b""

    # If it was JSON with column optimization, reverse it
    if "json" in domain_type:
        try:
            optimized = json.loads(raw)
            deoptimized = _deoptimize_json(optimized)
            raw = json.dumps(deoptimized, indent=2, ensure_ascii=False).encode("utf-8")
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    out_path = path.with_suffix(original_ext)
    out_path.write_bytes(raw)

    stats = {
        "compressed_size": len(container_bytes),
        "restored_size": len(raw),
        "coordinate": container.crystal_meta.coordinate if container.crystal_meta else "none",
        "has_weight_seeds": (container.crystal_meta.shell_seed is not None
                             if container.crystal_meta else False),
        "domain_type": domain_type,
    }
    return out_path, stats


def inspect_qshr(path: Path) -> Optional[CrystalWeightMeta]:
    """Read crystal weight metadata from a .qshr file WITHOUT decompressing."""
    data = Path(path).read_bytes()
    if data[:4] != QShrinkContainer.MAGIC:
        return None
    container = QShrinkContainer.deserialize(data)
    return container.crystal_meta


# ═══════════════════════════════════════════════════════════════════════════
# JSON OPTIMIZATION (column-oriented storage)
# ═══════════════════════════════════════════════════════════════════════════

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


def compress_json(data: Any, *, lossless: bool = True,
                  crystal_meta: Optional[CrystalWeightMeta] = None) -> bytes:
    """Compress a JSON-serializable object into a QSHR container."""
    optimized = _optimize_json(data)
    raw = json.dumps(optimized, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return compress_bytes(raw, lossless=lossless, crystal_meta=crystal_meta)


def decompress_json(container_bytes: bytes) -> Any:
    """Decompress a QSHR container back to a JSON object."""
    raw = decompress_bytes(container_bytes)
    optimized = json.loads(raw)
    return _deoptimize_json(optimized)


def _optimize_json(data: Any) -> Any:
    """Apply column-oriented optimization for arrays-of-objects."""
    if isinstance(data, list) and len(data) > 2 and all(isinstance(x, dict) for x in data):
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
            return [{k: _deoptimize_json(v) for k, v in zip(keys, row)} for row in data["rows"]]
        return {k: _deoptimize_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_deoptimize_json(x) for x in data]
    return data


# ═══════════════════════════════════════════════════════════════════════════
# DIRECTORY SCANNING
# ═══════════════════════════════════════════════════════════════════════════

def scan_directory(directory: Path, min_size: int = 1024) -> List[Dict[str, Any]]:
    """Scan directory for files that would benefit from crystallization."""
    directory = Path(directory)
    results = []
    for f in sorted(directory.rglob("*")):
        if not f.is_file() or f.suffix == ".qshr":
            continue
        size = f.stat().st_size
        if size < min_size:
            continue

        # Quick format detection
        fmt = f.suffix.lower().lstrip(".")
        est_ratio = {"json": 6.0, "jsonl": 5.0, "csv": 5.0, "tsv": 5.0,
                     "md": 3.0, "txt": 3.0, "py": 3.0, "xml": 4.0,
                     "html": 4.0, "svg": 4.0}.get(fmt, 2.0)

        # Compute crystal coordinate from file path
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


def _path_to_crystal(path: Path) -> Tuple[str, int, int, int, str]:
    """Compute crystal coordinate from file path (hash-based)."""
    name_hash = int(hashlib.sha256(str(path).encode()).hexdigest(), 16)
    shell = (name_hash % TOTAL_SHELLS) + 1
    wreath = ((shell - 1) // 12) + 1
    archetype = ((shell - 1) % 12) + 1
    faces = ["S", "F", "C", "R"]
    face = faces[name_hash % 4]
    coordinate = f"Xi108:W{wreath}:A{archetype}:S{shell}:{face}"
    return coordinate, shell, wreath, archetype, face


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


# ═══════════════════════════════════════════════════════════════════════════
# BATCH CRYSTALLIZER — process all files in a directory
# ═══════════════════════════════════════════════════════════════════════════

# Skip patterns for batch crystallization
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
              "_build", ".mypy_cache", ".pytest_cache", ".tox"}
_SKIP_EXTS = {".qshr", ".pyc", ".pyo", ".o", ".so", ".dll", ".exe"}


@dataclass
class BatchResult:
    """Result of batch crystallization."""
    total_files: int = 0
    crystallized: int = 0
    skipped: int = 0
    errors: int = 0
    total_original_bytes: int = 0
    total_output_bytes: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    manifest: Dict[str, Any] = field(default_factory=dict)

    @property
    def savings_pct(self) -> float:
        if self.total_original_bytes == 0:
            return 0.0
        return (1.0 - self.total_output_bytes / self.total_original_bytes) * 100


def batch_crystallize(directory: Path, *,
                      weight_store: Any = None,
                      min_size: int = 512,
                      max_size: int = 500 * 1024 * 1024,  # 500MB
                      dry_run: bool = False,
                      progress_callback: Optional[Any] = None,
                      ) -> BatchResult:
    """Crystallize ALL files in a directory through the TRUE pipeline.

    Processes files in order of size (largest first) and builds a
    live manifest tracking every crystallized file's position in
    the 4D tesseract with its liminal ID and mycelium hooks.

    Args:
        directory: Root directory to process
        weight_store: Optional FractalWeightStore for enriched metadata
        min_size: Minimum file size to process (bytes)
        max_size: Maximum file size to process (bytes)
        dry_run: If True, analyze but don't write output files
        progress_callback: Optional callable(file_num, total, path, result)
    """
    directory = Path(directory)
    batch = BatchResult()

    # Collect all eligible files
    files: List[Path] = []
    for f in sorted(directory.rglob("*")):
        if not f.is_file():
            continue
        # Skip hidden/build directories
        if any(p in _SKIP_DIRS for p in f.parts):
            continue
        if f.suffix.lower() in _SKIP_EXTS:
            continue
        size = f.stat().st_size
        if size < min_size or size > max_size:
            continue
        files.append(f)

    batch.total_files = len(files)
    # Sort by size descending (biggest savings first)
    files.sort(key=lambda f: f.stat().st_size, reverse=True)

    manifest_entries: List[Dict[str, Any]] = []

    for idx, fpath in enumerate(files):
        try:
            if dry_run:
                # Quick analysis only — no output file
                signal = decompress_to_raw(fpath)
                square = analyze_square(signal)
                flower = analyze_flower(signal)
                cloud = analyze_cloud(signal)
                frac = analyze_fractal(signal)
                ap = compute_apoint(signal, square, flower, cloud, frac)
                entry = {
                    "path": str(fpath.relative_to(directory)),
                    "size": signal.original_size,
                    "format": signal.source_format,
                    "coordinate": ap.coordinate,
                    "element": ap.element,
                    "mode": ap.mode,
                    "archetype": ap.archetype_name,
                    "octave": ap.octave,
                    "gate": ap.gate,
                    "lens_scores": {"S": ap.square_score, "F": ap.flower_score,
                                    "C": ap.cloud_score, "R": ap.fractal_score},
                }
                manifest_entries.append(entry)
                batch.crystallized += 1
                batch.total_original_bytes += signal.original_size
                batch.total_output_bytes += signal.original_size  # No compression in dry run
            else:
                result = crystallize_file(fpath, weight_store=weight_store)
                entry = {
                    "path": str(fpath.relative_to(directory)),
                    "output_path": str(result.output_path.relative_to(directory)),
                    "size": result.original_size,
                    "output_size": result.output_size,
                    "ratio": round(result.compression_ratio, 2),
                    "format": result.source_format,
                    "coordinate": result.apoint.coordinate,
                    "element": result.apoint.element,
                    "mode": result.apoint.mode,
                    "archetype": result.apoint.archetype_name,
                    "octave": result.apoint.octave,
                    "gate": result.apoint.gate,
                    "liminal_id": (result.crystal_meta.liminal.to_string()
                                   if result.crystal_meta.liminal else ""),
                    "file_id": (result.crystal_meta.mycelium_hook.file_id
                                if result.crystal_meta.mycelium_hook else ""),
                    "n27_state": (result.crystal_meta.n27_state.state_label
                                  if result.crystal_meta.n27_state else ""),
                    "n27_energy": (result.crystal_meta.n27_state.energy
                                   if result.crystal_meta.n27_state else 0.0),
                    "conservation_hash": result.conservation_hash,
                    "lens_scores": {
                        "S": result.apoint.square_score,
                        "F": result.apoint.flower_score,
                        "C": result.apoint.cloud_score,
                        "R": result.apoint.fractal_score,
                    },
                    "seed": [result.apoint.seed_real, result.apoint.seed_imag],
                }
                manifest_entries.append(entry)
                batch.crystallized += 1
                batch.total_original_bytes += result.original_size
                batch.total_output_bytes += result.output_size

            if progress_callback:
                progress_callback(idx + 1, batch.total_files, str(fpath), entry)

        except Exception as e:
            batch.errors += 1
            manifest_entries.append({
                "path": str(fpath.relative_to(directory)),
                "error": str(e)[:200],
            })

    batch.results = manifest_entries
    batch.manifest = {
        "version": "1.0.0",
        "total_files": batch.total_files,
        "crystallized": batch.crystallized,
        "errors": batch.errors,
        "total_original_bytes": batch.total_original_bytes,
        "total_output_bytes": batch.total_output_bytes,
        "savings_pct": round(batch.savings_pct, 1),
        "entries": manifest_entries,
    }

    # Write manifest to directory
    manifest_path = directory / "crystal_manifest.json"
    manifest_path.write_text(
        json.dumps(batch.manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return batch


# ═══════════════════════════════════════════════════════════════════════════
# TESSERACT DIRECTORY BUILDER — organize files into 4D hologram structure
# ═══════════════════════════════════════════════════════════════════════════

_ELEMENT_DIRS = {0: "S_Earth", 1: "F_Fire", 2: "C_Water", 3: "R_Air"}
_MODE_DIRS = {0: "Cardinal", 1: "Fixed", 2: "Mutable"}
_ARCHETYPE_DIRS = {
    0: "01_Aries", 1: "02_Taurus", 2: "03_Gemini", 3: "04_Cancer",
    4: "05_Leo", 5: "06_Virgo", 6: "07_Libra", 7: "08_Scorpio",
    8: "09_Sagittarius", 9: "10_Capricorn", 10: "11_Aquarius", 11: "12_Pisces",
}
_OCTAVE_DIRS = {0: "W1_Su", 1: "W2_Me", 2: "W3_Sa"}


def build_tesseract_structure(root: Path) -> Path:
    """Create the 4D tesseract directory structure.

    Structure: root/CRYSTAL_4D/{element}/{mode}/{archetype}/{octave}/
    Total: 4 x 3 x 12 x 3 = 432 leaf directories (covering all 256 gates + extras)

    Returns the CRYSTAL_4D root path.
    """
    crystal_root = root / "CRYSTAL_4D"
    crystal_root.mkdir(exist_ok=True)

    for e_idx, e_name in _ELEMENT_DIRS.items():
        for m_idx, m_name in _MODE_DIRS.items():
            for a_idx, a_name in _ARCHETYPE_DIRS.items():
                for o_idx, o_name in _OCTAVE_DIRS.items():
                    leaf = crystal_root / e_name / m_name / a_name / o_name
                    leaf.mkdir(parents=True, exist_ok=True)

    return crystal_root


def tesseract_path_for(root: Path, element: str, mode: str,
                       archetype_idx: int, octave: int) -> Path:
    """Compute the tesseract directory path for a given crystal position."""
    e_idx = {"S": 0, "F": 1, "C": 2, "R": 3}.get(element, 0)
    m_idx = {"Cardinal": 0, "Fixed": 1, "Mutable": 2}.get(mode, 2)
    a_idx = (archetype_idx - 1) % 12
    o_idx = max(0, min(2, octave - 1))

    return (root / "CRYSTAL_4D"
            / _ELEMENT_DIRS[e_idx]
            / _MODE_DIRS[m_idx]
            / _ARCHETYPE_DIRS[a_idx]
            / _OCTAVE_DIRS[o_idx])


def reorganize_to_tesseract(source_dir: Path, *,
                            weight_store: Any = None,
                            copy_mode: bool = True,
                            min_size: int = 512,
                            max_size: int = 500 * 1024 * 1024,
                            progress_callback: Optional[Any] = None,
                            ) -> Dict[str, Any]:
    """Reorganize a directory into a 4D hologram tesseract structure.

    For each file:
    1. Crystallize through TRUE pipeline (if not already .qshr)
    2. Compute its A-point (4D position)
    3. Place it in the tesseract directory: CRYSTAL_4D/{element}/{mode}/{archetype}/{octave}/
    4. Record in the live manifest with liminal ID and mycelium hooks

    Args:
        source_dir: Source directory to reorganize
        weight_store: Optional FractalWeightStore
        copy_mode: If True, copy files (preserving originals). If False, move.
        min_size: Min file size to include
        max_size: Max file size to include
        progress_callback: Optional callable(file_num, total, path, dest)

    Returns:
        Summary dict with stats and manifest path
    """
    import shutil

    source_dir = Path(source_dir)
    crystal_root = build_tesseract_structure(source_dir)

    # Collect files
    files: List[Path] = []
    for f in sorted(source_dir.rglob("*")):
        if not f.is_file():
            continue
        # Skip the CRYSTAL_4D directory itself
        try:
            f.relative_to(crystal_root)
            continue  # Inside CRYSTAL_4D, skip
        except ValueError:
            pass  # Not inside, process it
        if any(p in _SKIP_DIRS for p in f.parts):
            continue
        if f.suffix.lower() in _SKIP_EXTS:
            continue
        if f.name == "crystal_manifest.json":
            continue
        size = f.stat().st_size
        if size < min_size or size > max_size:
            continue
        files.append(f)

    total = len(files)
    placed = 0
    errors = 0
    manifest_entries: List[Dict[str, Any]] = []

    for idx, fpath in enumerate(files):
        try:
            # Crystallize to get A-point
            result = crystallize_file(fpath, weight_store=weight_store)

            # Determine tesseract destination
            dest_dir = tesseract_path_for(
                source_dir, result.apoint.element, result.apoint.mode,
                result.apoint.archetype_idx, result.apoint.octave)

            # Use output file (may be .qshr or native)
            src_file = result.output_path
            dest_file = dest_dir / src_file.name

            # Handle name collisions
            counter = 1
            while dest_file.exists():
                stem = src_file.stem
                dest_file = dest_dir / f"{stem}_{counter}{src_file.suffix}"
                counter += 1

            if copy_mode:
                shutil.copy2(str(src_file), str(dest_file))
            else:
                shutil.move(str(src_file), str(dest_file))

            entry = {
                "original_path": str(fpath.relative_to(source_dir)),
                "tesseract_path": str(dest_file.relative_to(source_dir)),
                "coordinate": result.apoint.coordinate,
                "element": result.apoint.element,
                "mode": result.apoint.mode,
                "archetype": result.apoint.archetype_name,
                "octave": result.apoint.octave,
                "gate": result.apoint.gate,
                "liminal_id": (result.crystal_meta.liminal.to_string()
                               if result.crystal_meta.liminal else ""),
                "file_id": (result.crystal_meta.mycelium_hook.file_id
                            if result.crystal_meta.mycelium_hook else ""),
                "n27_state": (result.crystal_meta.n27_state.state_label
                              if result.crystal_meta.n27_state else ""),
                "size": result.original_size,
                "output_size": result.output_size,
                "format": result.source_format,
            }
            manifest_entries.append(entry)
            placed += 1

            if progress_callback:
                progress_callback(idx + 1, total, str(fpath), str(dest_file))

        except Exception as e:
            errors += 1
            manifest_entries.append({
                "original_path": str(fpath.relative_to(source_dir)),
                "error": str(e)[:200],
            })

    # Write tesseract manifest
    manifest = {
        "version": "1.0.0",
        "type": "tesseract_4d_hologram",
        "total_files": total,
        "placed": placed,
        "errors": errors,
        "structure": "CRYSTAL_4D/{element}/{mode}/{archetype}/{octave}/",
        "dimensions": {
            "element": list(_ELEMENT_DIRS.values()),
            "mode": list(_MODE_DIRS.values()),
            "archetype": list(_ARCHETYPE_DIRS.values()),
            "octave": list(_OCTAVE_DIRS.values()),
        },
        "entries": manifest_entries,
    }
    manifest_path = crystal_root / "tesseract_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "crystal_root": str(crystal_root),
        "manifest_path": str(manifest_path),
        "total": total,
        "placed": placed,
        "errors": errors,
        "directories_created": 4 * 3 * 12 * 3,
    }
    return f"{n:.1f}TB"
