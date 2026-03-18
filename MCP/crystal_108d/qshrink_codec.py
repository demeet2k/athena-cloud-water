# CRYSTAL: Xi108:W3:A4:S36 | face=R | node=541 | depth=0 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A4:S35→Xi108:W2:A4:S36→Xi108:W3:A3:S36→Xi108:W3:A5:S36

"""
QSHRINK Container Codec — binary container with crystal weight metadata.
=========================================================================
Ported from athena_os/qshrink/container.py with the addition of the
CrystalWeightMeta envelope (CWGT chunk).  Every .qshr file is a living
crystal node: it carries its 108D coordinate, nested weight seeds from
the FractalWeightStore (1/8 → 1/64 → 1/512 lift cascade), learnable
neural parameters, holographic regeneration data, and conservation hash.

Container invariants:
  1. Determinism  — legal bitstream → unique decode
  2. Bounded damage — corruption is locally contained
  3. Seek legality — random access requires seek lattice
  4. Streaming legality — monotone parsing with bounded lookahead
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import zlib
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .constants import TOTAL_SHELLS, TOTAL_WREATHS, ARCHETYPE_NAMES

# Golden ratio
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1  # 0.618…

# ---------------------------------------------------------------------------
# Chunk / topology enums
# ---------------------------------------------------------------------------

class ChunkType(Enum):
    MAGIC = "QSHR"
    VERSION = "VERS"
    MANIFEST = "MNFT"
    BULK = "BULK"
    ESCAPE = "ESCP"
    TAGS = "TAGS"
    SEEK = "SEEK"
    INDEX = "INDX"
    HASH = "HASH"
    REPAIR = "REPR"
    ECC = "ECCD"
    END = "ENDS"
    CRYSTAL_WEIGHT = "CWGT"   # NEW — crystal weight metadata


class TopologyType(Enum):
    DIRECT_SUM = "direct_sum"
    KRONECKER = "kronecker"
    HYBRID = "hybrid"


class AccessMode(Enum):
    STREAM_ONLY = 0
    SEEKABLE_LINEAR = 1
    SEEKABLE_INDEXED = 2


_TOPO_CODES = {TopologyType.DIRECT_SUM: 0, TopologyType.KRONECKER: 1, TopologyType.HYBRID: 2}
_CODE_TOPO = {v: k for k, v in _TOPO_CODES.items()}

# ---------------------------------------------------------------------------
# ChunkHeader  (16 bytes)
# ---------------------------------------------------------------------------

@dataclass
class ChunkHeader:
    chunk_type: ChunkType
    payload_length: int
    checksum: int  # CRC32
    flags: int = 0

    HEADER_SIZE = 16

    def to_bytes(self) -> bytes:
        type_bytes = self.chunk_type.value.encode("ascii")[:4].ljust(4, b"\x00")
        return struct.pack("<4sIIHH", type_bytes, self.payload_length,
                           self.checksum, self.flags, 0)

    @classmethod
    def from_bytes(cls, data: bytes) -> "ChunkHeader":
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Insufficient header data")
        tb, length, checksum, flags, _ = struct.unpack("<4sIIHH", data[:16])
        ts = tb.decode("ascii").rstrip("\x00")
        ct = ChunkType.BULK
        for c in ChunkType:
            if c.value == ts:
                ct = c
                break
        return cls(chunk_type=ct, payload_length=length, checksum=checksum, flags=flags)

    def verify_payload(self, payload: bytes) -> bool:
        return (zlib.crc32(payload) & 0xFFFFFFFF) == self.checksum

# ---------------------------------------------------------------------------
# Chunk
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    header: ChunkHeader
    payload: bytes
    offset: int = 0

    def to_bytes(self) -> bytes:
        return self.header.to_bytes() + self.payload

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> Tuple["Chunk", int]:
        header = ChunkHeader.from_bytes(data)
        start = ChunkHeader.HEADER_SIZE
        end = start + header.payload_length
        if len(data) < end:
            raise ValueError("Insufficient payload data")
        return cls(header=header, payload=data[start:end], offset=offset), end

    def verify(self) -> bool:
        return self.header.verify_payload(self.payload)

    @property
    def total_size(self) -> int:
        return ChunkHeader.HEADER_SIZE + len(self.payload)

# ---------------------------------------------------------------------------
# RepairPrefix  (32 bytes — self-healing header)
# ---------------------------------------------------------------------------

@dataclass
class RepairPrefix:
    header_copy: bytes
    parity: bytes
    PREFIX_SIZE = 32

    def to_bytes(self) -> bytes:
        return (self.header_copy[:16] + self.parity[:16]).ljust(self.PREFIX_SIZE, b"\x00")

    @classmethod
    def create_for_header(cls, header: ChunkHeader) -> "RepairPrefix":
        hb = header.to_bytes()
        return cls(header_copy=hb, parity=bytes(b ^ 0xFF for b in hb))

    def repair_header(self, corrupted: bytes) -> Optional[bytes]:
        if corrupted == self.header_copy:
            return corrupted
        repaired = bytes(c ^ p ^ 0xFF for c, p in zip(corrupted, self.parity))
        return repaired if repaired == self.header_copy else None

# ---------------------------------------------------------------------------
# SeekEntry / SeekTable
# ---------------------------------------------------------------------------

@dataclass
class SeekEntry:
    unit_id: int
    byte_offset: int
    payload_length: int
    dependency_ids: List[int] = field(default_factory=list)

    def to_bytes(self) -> bytes:
        n = len(self.dependency_ids)
        deps = struct.pack(f"<{n}I", *self.dependency_ids) if n else b""
        return struct.pack("<IQI", self.unit_id, self.byte_offset,
                           self.payload_length) + struct.pack("<H", n) + deps


class SeekTable:
    def __init__(self) -> None:
        self._entries: List[SeekEntry] = []
        self._by_id: Dict[int, SeekEntry] = {}

    def add_entry(self, entry: SeekEntry) -> None:
        self._entries.append(entry)
        self._by_id[entry.unit_id] = entry

    def lookup(self, unit_id: int) -> Optional[SeekEntry]:
        return self._by_id.get(unit_id)

    def to_bytes(self) -> bytes:
        data = struct.pack("<I", len(self._entries))
        for e in self._entries:
            data += e.to_bytes()
        return data + hashlib.sha256(data).digest()[:8]

    @classmethod
    def from_bytes(cls, data: bytes) -> "SeekTable":
        n = struct.unpack("<I", data[:4])[0]
        tbl = cls()
        off = 4
        for _ in range(n):
            uid, boff, plen = struct.unpack("<IQI", data[off:off + 16])
            nd = struct.unpack("<H", data[off + 16:off + 18])[0]
            deps = list(struct.unpack(f"<{nd}I", data[off + 18:off + 18 + nd * 4])) if nd else []
            tbl.add_entry(SeekEntry(uid, boff, plen, deps))
            off += 18 + nd * 4
        return tbl

# ---------------------------------------------------------------------------
# CrystalWeightMeta — nested weight envelope in every .qshr
# ---------------------------------------------------------------------------

@dataclass
class ShellSeedMeta:
    """1/8 compressed: per-shell weight summary."""
    shell: int
    wreath: str
    mean: float
    std: float
    count: int
    min_val: float
    max_val: float
    element_dist: Dict[str, float]
    gate_means: Dict[str, float]


@dataclass
class ArchetypeSeedMeta:
    """1/64 compressed: per-archetype summary across 3 wreaths."""
    archetype: int
    name: str
    mean: float
    std: float
    count: int
    wreath_means: Dict[str, float]


@dataclass
class NanoSeedMeta:
    """1/512 compressed: global weight distribution."""
    global_mean: float
    global_std: float
    skew: float
    kurtosis: float
    total_count: int
    element_means: Dict[str, float]
    gate_means: Dict[str, float]


@dataclass
class CrystalWeightMeta:
    """Crystal weight metadata embedded in every .qshr container.

    Makes compressed files 'alive' in the crystal lattice — they know
    their 108D position, carry nested weight seeds from the 1/8 lift
    cascade, and can participate in neural forward pass scoring without
    loading the full 38K weight store.

    Full organism metadata includes:
    - Crystal identity (Xi108 coordinate, shell, wreath, archetype, face)
    - Mycelium graph connectivity (edges, neighbors, shard)
    - Metro routing (lines, transport stacks, promotion stage)
    - Z-point hierarchy (depth, z-address, collapse level)
    - A-point archetype decomposition (zodiacal agent, element, mode)
    - Cross-neural mapping (brain network, organ atlas, live cell)
    - Sacred geometry (phi-sigma angles, E8 lattice position, Mobius lens)
    - 4D tesseract (holographic quadrant: element × mode × archetype × octave)
    - Nested weight seeds (1/8 → 1/64 → 1/512 fractal lift cascade)
    """
    # ── Identity ──
    coordinate: str          # "Xi108:W2:A4:S15:F"
    shell: int               # 1-36
    wreath: int              # 1-3
    archetype: int           # 1-12
    face: str                # S/F/C/R

    # ── Mycelium graph connectivity ──
    mycelium_shard: str = ""           # shard ID in mycelium_graph
    mycelium_edges: List[str] = field(default_factory=list)   # neighbor coordinates
    mycelium_degree: int = 0           # edge count
    mycelium_cluster: str = ""         # community/cluster label

    # ── Metro routing ──
    metro_lines: List[str] = field(default_factory=list)      # metro lines passing through
    transport_stack: str = ""          # transport stack layer
    promotion_stage: str = ""          # octave promotion stage (Cardinal/Fixed/Mutable)
    routing_bridges: List[str] = field(default_factory=list)  # bridge endpoints

    # ── Z-point hierarchy ──
    z_depth: int = 0                   # depth in z-point tree
    z_address: str = ""                # z-point address string
    z_collapse_level: str = ""         # collapse level (Nano/Micro/Seed/Full)
    z_parent: str = ""                 # parent z-point coordinate

    # ── A-point archetype decomposition ──
    archetype_name: str = ""           # zodiacal agent name (Aries..Pisces)
    element: str = ""                  # element (Fire/Earth/Air/Water)
    mode: str = ""                     # mode (Cardinal/Fixed/Mutable)
    element_face: str = ""             # SFCR face from element

    # ── Cross-neural mapping ──
    brain_region: str = ""             # brain network region
    organ_system: str = ""             # organ atlas system
    live_cell_role: str = ""           # live cell constitution role
    neural_layer: int = 0              # depth in neural net (0=surface, 6=deep)

    # ── Sacred geometry ──
    phi_angle: float = 0.0             # φ-sigma angle (0..360)
    phi_sigma_state: int = 0           # Σ60 state index (0-59)
    e8_vertex: List[float] = field(default_factory=list)  # E8 lattice position (8D)
    mobius_lens: str = ""              # Mobius lens assignment
    golden_ratio_depth: float = 0.0    # φ^(-depth) scaling factor

    # ── 4D tesseract position ──
    tesseract_element: int = 0         # 0-3 (S/F/C/R quadrant)
    tesseract_mode: int = 0            # 0-2 (Cardinal/Fixed/Mutable)
    tesseract_archetype: int = 0       # 0-11 (zodiacal)
    tesseract_octave: int = 0          # 0-2 (wreath/octave)
    tesseract_gate: int = 0            # 0-255 (4^4 gate address)
    tesseract_address: str = ""        # human-readable "S.Cardinal.Aries.W1"

    # ── Nested weight seeds — fractal 1/8 lift cascade ──
    shell_seed: Optional[ShellSeedMeta] = None
    archetype_seed: Optional[ArchetypeSeedMeta] = None
    nano_seed: Optional[NanoSeedMeta] = None

    # ── Neural engine learnable parameters ──
    path_weights: Dict[str, float] = field(
        default_factory=lambda: {"S": 0.20, "F": 0.35, "C": 0.25, "R": 0.20})
    resonance_weights: Dict[str, float] = field(
        default_factory=lambda: {"addr_fit": 0.20, "inv_fit": 0.15, "phase": 0.15,
                                  "boundary": 0.15, "scale": 0.15, "compress": 0.20})
    desire_weights: Dict[str, float] = field(
        default_factory=lambda: {"align": 0.35, "explore": 0.20, "zpa": 0.25, "con_sat": 0.20})
    bridge_modulation: float = 0.20

    # ── Holographic regeneration ──
    holographic_w_real: float = 0.5   # Re(w), w = (1+i)/2
    holographic_w_imag: float = 0.5   # Im(w)
    mirror_shell: int = 0             # S_{37-k}
    conservation_hash: str = ""       # 6-invariant fingerprint

    def to_json(self) -> str:
        """Serialize to JSON for embedding in CWGT chunk."""
        d: dict[str, Any] = {
            # Identity
            "coordinate": self.coordinate,
            "shell": self.shell,
            "wreath": self.wreath,
            "archetype": self.archetype,
            "face": self.face,
            # Mycelium
            "mycelium": {
                "shard": self.mycelium_shard,
                "edges": self.mycelium_edges,
                "degree": self.mycelium_degree,
                "cluster": self.mycelium_cluster,
            },
            # Metro routing
            "routing": {
                "metro_lines": self.metro_lines,
                "transport_stack": self.transport_stack,
                "promotion_stage": self.promotion_stage,
                "bridges": self.routing_bridges,
            },
            # Z-point hierarchy
            "z_point": {
                "depth": self.z_depth,
                "address": self.z_address,
                "collapse_level": self.z_collapse_level,
                "parent": self.z_parent,
            },
            # A-point archetype
            "a_point": {
                "name": self.archetype_name,
                "element": self.element,
                "mode": self.mode,
                "element_face": self.element_face,
            },
            # Cross-neural mapping
            "neural_map": {
                "brain_region": self.brain_region,
                "organ_system": self.organ_system,
                "live_cell_role": self.live_cell_role,
                "neural_layer": self.neural_layer,
            },
            # Sacred geometry
            "sacred_geometry": {
                "phi_angle": self.phi_angle,
                "phi_sigma_state": self.phi_sigma_state,
                "e8_vertex": self.e8_vertex,
                "mobius_lens": self.mobius_lens,
                "golden_ratio_depth": self.golden_ratio_depth,
            },
            # 4D tesseract
            "tesseract": {
                "element": self.tesseract_element,
                "mode": self.tesseract_mode,
                "archetype": self.tesseract_archetype,
                "octave": self.tesseract_octave,
                "gate": self.tesseract_gate,
                "address": self.tesseract_address,
            },
            # Neural parameters
            "path_weights": self.path_weights,
            "resonance_weights": self.resonance_weights,
            "desire_weights": self.desire_weights,
            "bridge_modulation": self.bridge_modulation,
            "holographic_w": [self.holographic_w_real, self.holographic_w_imag],
            "mirror_shell": self.mirror_shell,
            "conservation_hash": self.conservation_hash,
        }
        if self.shell_seed:
            d["shell_seed"] = asdict(self.shell_seed)
        if self.archetype_seed:
            d["archetype_seed"] = asdict(self.archetype_seed)
        if self.nano_seed:
            d["nano_seed"] = asdict(self.nano_seed)
        return json.dumps(d, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str) -> "CrystalWeightMeta":
        """Deserialize from JSON."""
        d = json.loads(raw)
        shell_seed = ShellSeedMeta(**d["shell_seed"]) if "shell_seed" in d else None
        arch_seed = ArchetypeSeedMeta(**d["archetype_seed"]) if "archetype_seed" in d else None
        nano_seed = NanoSeedMeta(**d["nano_seed"]) if "nano_seed" in d else None
        hw = d.get("holographic_w", [0.5, 0.5])
        # Parse nested sub-objects (backward compatible with older .qshr)
        myc = d.get("mycelium", {})
        rte = d.get("routing", {})
        zpt = d.get("z_point", {})
        apt = d.get("a_point", {})
        nmp = d.get("neural_map", {})
        sgm = d.get("sacred_geometry", {})
        tsr = d.get("tesseract", {})
        return cls(
            coordinate=d["coordinate"],
            shell=d["shell"],
            wreath=d["wreath"],
            archetype=d["archetype"],
            face=d["face"],
            # Mycelium
            mycelium_shard=myc.get("shard", ""),
            mycelium_edges=myc.get("edges", []),
            mycelium_degree=myc.get("degree", 0),
            mycelium_cluster=myc.get("cluster", ""),
            # Routing
            metro_lines=rte.get("metro_lines", []),
            transport_stack=rte.get("transport_stack", ""),
            promotion_stage=rte.get("promotion_stage", ""),
            routing_bridges=rte.get("bridges", []),
            # Z-point
            z_depth=zpt.get("depth", 0),
            z_address=zpt.get("address", ""),
            z_collapse_level=zpt.get("collapse_level", ""),
            z_parent=zpt.get("parent", ""),
            # A-point
            archetype_name=apt.get("name", ""),
            element=apt.get("element", ""),
            mode=apt.get("mode", ""),
            element_face=apt.get("element_face", ""),
            # Neural map
            brain_region=nmp.get("brain_region", ""),
            organ_system=nmp.get("organ_system", ""),
            live_cell_role=nmp.get("live_cell_role", ""),
            neural_layer=nmp.get("neural_layer", 0),
            # Sacred geometry
            phi_angle=sgm.get("phi_angle", 0.0),
            phi_sigma_state=sgm.get("phi_sigma_state", 0),
            e8_vertex=sgm.get("e8_vertex", []),
            mobius_lens=sgm.get("mobius_lens", ""),
            golden_ratio_depth=sgm.get("golden_ratio_depth", 0.0),
            # Tesseract
            tesseract_element=tsr.get("element", 0),
            tesseract_mode=tsr.get("mode", 0),
            tesseract_archetype=tsr.get("archetype", 0),
            tesseract_octave=tsr.get("octave", 0),
            tesseract_gate=tsr.get("gate", 0),
            tesseract_address=tsr.get("address", ""),
            # Seeds
            shell_seed=shell_seed,
            archetype_seed=arch_seed,
            nano_seed=nano_seed,
            # Neural params
            path_weights=d.get("path_weights", {}),
            resonance_weights=d.get("resonance_weights", {}),
            desire_weights=d.get("desire_weights", {}),
            bridge_modulation=d.get("bridge_modulation", 0.20),
            holographic_w_real=hw[0],
            holographic_w_imag=hw[1],
            mirror_shell=d.get("mirror_shell", 0),
            conservation_hash=d.get("conservation_hash", ""),
        )

    @classmethod
    def hollow(cls, coordinate: str, shell: int, wreath: int,
               archetype: int, face: str) -> "CrystalWeightMeta":
        """Create a hollow envelope with just identity (no weight data)."""
        return cls(
            coordinate=coordinate, shell=shell, wreath=wreath,
            archetype=archetype, face=face,
            mirror_shell=37 - shell,
            conservation_hash=hashlib.sha256(coordinate.encode()).hexdigest()[:16],
        )

    def to_chunk(self) -> Chunk:
        """Serialize as a CWGT container chunk."""
        payload = self.to_json().encode("utf-8")
        header = ChunkHeader(
            chunk_type=ChunkType.CRYSTAL_WEIGHT,
            payload_length=len(payload),
            checksum=zlib.crc32(payload) & 0xFFFFFFFF,
        )
        return Chunk(header=header, payload=payload)

    @classmethod
    def from_chunk(cls, chunk: Chunk) -> "CrystalWeightMeta":
        """Deserialize from a CWGT chunk."""
        return cls.from_json(chunk.payload.decode("utf-8"))

    def compute_conservation_hash(self) -> str:
        """Compute 6-invariant conservation fingerprint."""
        parts = [
            str(self.shell),        # shell invariant
            str(self.wreath),       # zoom invariant
            self.face,              # face invariant
            str(self.archetype),    # archetype invariant
            str(self.mirror_shell), # Mobius invariant
            str(self.shell % 3),    # phase invariant
        ]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]

# ---------------------------------------------------------------------------
# ContainerManifest
# ---------------------------------------------------------------------------

_MANIFEST_FMT = "<3sBBIIQ"
_MANIFEST_HDR_SIZE = struct.calcsize(_MANIFEST_FMT)
_DOMAIN_TYPE_SIZE = 16
_HASH_SIZE = 64

@dataclass
class ContainerManifest:
    version: Tuple[int, int, int] = (1, 0, 0)
    topology: TopologyType = TopologyType.DIRECT_SUM
    access_mode: AccessMode = AccessMode.STREAM_ONLY
    n_domains: int = 1
    n_chunks: int = 0
    total_size: int = 0
    domain_types: List[str] = field(default_factory=list)
    domain_offsets: List[int] = field(default_factory=list)
    content_hash: str = ""

    def to_bytes(self) -> bytes:
        vb = struct.pack("<BBB", *self.version)
        self.n_domains = max(self.n_domains, len(self.domain_types))
        offsets = list(self.domain_offsets)
        if len(offsets) < self.n_domains:
            offsets.extend([0] * (self.n_domains - len(offsets)))
        header = struct.pack(_MANIFEST_FMT, vb, _TOPO_CODES.get(self.topology, 0),
                             int(self.access_mode.value), self.n_domains,
                             self.n_chunks, self.total_size)
        dd = b""
        for dt, do in zip(self.domain_types[:self.n_domains], offsets[:self.n_domains]):
            dd += dt.encode()[:_DOMAIN_TYPE_SIZE].ljust(_DOMAIN_TYPE_SIZE, b"\x00")
            dd += struct.pack("<Q", do)
        hb = self.content_hash.encode("ascii", errors="ignore")[:_HASH_SIZE].ljust(_HASH_SIZE, b"\x00")
        return header + dd + hb

    @classmethod
    def from_bytes(cls, data: bytes) -> "ContainerManifest":
        if len(data) < _MANIFEST_HDR_SIZE + _HASH_SIZE:
            raise ValueError("Insufficient manifest data")
        vb, tc, ab, nd, nc, ts = struct.unpack(_MANIFEST_FMT, data[:_MANIFEST_HDR_SIZE])
        m = cls(
            version=tuple(vb),
            topology=_CODE_TOPO.get(tc, TopologyType.DIRECT_SUM),
            access_mode=AccessMode(ab) if ab in {am.value for am in AccessMode} else AccessMode.STREAM_ONLY,
            n_domains=nd, n_chunks=nc, total_size=ts,
        )
        off = _MANIFEST_HDR_SIZE
        for _ in range(nd):
            if len(data) < off + _DOMAIN_TYPE_SIZE + 8:
                break
            dt = data[off:off + _DOMAIN_TYPE_SIZE].rstrip(b"\x00").decode("utf-8", errors="ignore") or "domain"
            off += _DOMAIN_TYPE_SIZE
            do = struct.unpack("<Q", data[off:off + 8])[0]
            off += 8
            m.domain_types.append(dt)
            m.domain_offsets.append(do)
        he = off + _HASH_SIZE
        if len(data) >= he:
            m.content_hash = data[off:he].rstrip(b"\x00").decode("ascii", errors="ignore")
        return m

# ---------------------------------------------------------------------------
# Domain / QShrinkContainer
# ---------------------------------------------------------------------------

@dataclass
class Domain:
    domain_id: int
    domain_type: str
    chunks: List[Chunk] = field(default_factory=list)

    def add_chunk(self, chunk: Chunk) -> None:
        self.chunks.append(chunk)

    def total_size(self) -> int:
        return sum(c.total_size for c in self.chunks)

    def verify_all(self) -> Tuple[bool, List[int]]:
        invalid = [i for i, c in enumerate(self.chunks) if not c.verify()]
        return len(invalid) == 0, invalid


class QShrinkContainer:
    """Complete QSHR container — robust, seekable, repairable, crystal-aware."""

    MAGIC = b"QSHR"
    VERSION = (1, 0, 0)

    def __init__(self, topology: TopologyType = TopologyType.DIRECT_SUM) -> None:
        self.topology = topology
        self.manifest = ContainerManifest(topology=topology)
        self.domains: List[Domain] = []
        self._seek_table = SeekTable()
        self.crystal_meta: Optional[CrystalWeightMeta] = None

    def add_domain(self, domain: Domain) -> int:
        did = len(self.domains)
        domain.domain_id = did
        self.domains.append(domain)
        self.manifest.n_domains = len(self.domains)
        self.manifest.domain_types.append(domain.domain_type)
        return did

    def build_seek_table(self) -> None:
        uid = 0
        cur = 0
        for dom in self.domains:
            for chunk in dom.chunks:
                chunk.offset = cur
                self._seek_table.add_entry(SeekEntry(uid, cur, chunk.header.payload_length))
                cur += chunk.total_size
                uid += 1
        self.manifest.access_mode = AccessMode.SEEKABLE_INDEXED

    def serialize(self) -> bytes:
        self.manifest.topology = self.topology
        self.manifest.n_domains = len(self.domains)
        self.manifest.n_chunks = sum(len(d.chunks) for d in self.domains)
        self.manifest.domain_types = [d.domain_type for d in self.domains]
        self.manifest.domain_offsets = [0] * len(self.domains)

        if self.manifest.access_mode == AccessMode.SEEKABLE_INDEXED:
            self.build_seek_table()

        dom_blobs = [b"".join(c.to_bytes() for c in d.chunks) for d in self.domains]

        # Crystal weight chunk (if present)
        cwgt_bytes = self.crystal_meta.to_chunk().to_bytes() if self.crystal_meta else b""

        seek_bytes = self._seek_table.to_bytes() if self.manifest.access_mode == AccessMode.SEEKABLE_INDEXED else b""

        # Compute offsets
        self.manifest.total_size = 0
        self.manifest.content_hash = ""
        mfb = self.manifest.to_bytes()
        preamble = 4 + 3 + 4 + len(mfb) + 4 + len(seek_bytes) + len(cwgt_bytes)
        offsets = []
        cursor = preamble
        for blob in dom_blobs:
            offsets.append(cursor)
            cursor += len(blob)
        self.manifest.domain_offsets = offsets
        self.manifest.content_hash = hashlib.sha256(b"".join(dom_blobs)).hexdigest()
        mfb = self.manifest.to_bytes()

        end_chunk = Chunk(header=ChunkHeader(ChunkType.END, 0, 0), payload=b"")

        data = b"".join([
            self.MAGIC,
            struct.pack("<BBB", *self.VERSION),
            struct.pack("<I", len(mfb)), mfb,
            struct.pack("<I", len(seek_bytes)), seek_bytes,
            cwgt_bytes,
            *dom_blobs,
            end_chunk.to_bytes(),
        ])
        self.manifest.total_size = len(data)
        # Rewrite with final size
        mfb = self.manifest.to_bytes()
        data = b"".join([
            self.MAGIC,
            struct.pack("<BBB", *self.VERSION),
            struct.pack("<I", len(mfb)), mfb,
            struct.pack("<I", len(seek_bytes)), seek_bytes,
            cwgt_bytes,
            *dom_blobs,
            end_chunk.to_bytes(),
        ])
        return data

    @classmethod
    def deserialize(cls, data: bytes) -> "QShrinkContainer":
        if data[:4] != cls.MAGIC:
            raise ValueError(f"Invalid magic: {data[:4]}")
        off = 4
        _ver = struct.unpack("<BBB", data[off:off + 3])
        off += 3

        mlen = struct.unpack("<I", data[off:off + 4])[0]
        off += 4
        manifest = ContainerManifest.from_bytes(data[off:off + mlen])
        off += mlen

        slen = struct.unpack("<I", data[off:off + 4])[0]
        off += 4
        seek_table = SeekTable.from_bytes(data[off:off + slen]) if slen else None
        off += slen

        container = cls(topology=manifest.topology)
        container.manifest = manifest
        if seek_table:
            container._seek_table = seek_table

        # Parse remaining chunks — look for CWGT and domain data
        remaining = data[off:]
        parsed_chunks: List[Chunk] = []
        roff = 0
        while roff < len(remaining):
            try:
                chunk, consumed = Chunk.from_bytes(remaining[roff:], off + roff)
            except (ValueError, struct.error):
                break
            if chunk.header.chunk_type == ChunkType.END:
                break
            if chunk.header.chunk_type == ChunkType.CRYSTAL_WEIGHT:
                container.crystal_meta = CrystalWeightMeta.from_chunk(chunk)
            else:
                parsed_chunks.append(chunk)
            roff += consumed

        # Group parsed chunks into domains
        if parsed_chunks:
            domain = Domain(domain_id=0, domain_type=manifest.domain_types[0] if manifest.domain_types else "default")
            for c in parsed_chunks:
                domain.add_chunk(c)
            container.domains.append(domain)

        return container

    def verify_integrity(self) -> Tuple[bool, Dict[str, Any]]:
        diag: Dict[str, Any] = {
            "n_domains": len(self.domains),
            "n_chunks": sum(len(d.chunks) for d in self.domains),
            "has_crystal_meta": self.crystal_meta is not None,
            "invalid_chunks": [],
        }
        ok = True
        for dom in self.domains:
            valid, inv = dom.verify_all()
            if not valid:
                ok = False
                diag["invalid_chunks"].extend((dom.domain_id, i) for i in inv)
        diag["is_valid"] = ok
        return ok, diag


# ---------------------------------------------------------------------------
# DirectSumContainer (archive with dedup)
# ---------------------------------------------------------------------------

class DirectSumContainer(QShrinkContainer):
    def __init__(self) -> None:
        super().__init__(TopologyType.DIRECT_SUM)
        self._dedup: Dict[str, int] = {}

    def add_item(self, data: bytes, item_type: str = "file") -> int:
        h = hashlib.sha256(data).hexdigest()
        if h in self._dedup:
            return self._dedup[h]
        header = ChunkHeader(ChunkType.BULK, len(data), zlib.crc32(data) & 0xFFFFFFFF)
        chunk = Chunk(header=header, payload=data)
        if not self.domains:
            self.add_domain(Domain(0, "archive"))
        idx = len(self.domains[0].chunks)
        self.domains[0].add_chunk(chunk)
        self._dedup[h] = idx
        return idx

    def get_item(self, item_id: int) -> Optional[bytes]:
        if not self.domains or item_id >= len(self.domains[0].chunks):
            return None
        c = self.domains[0].chunks[item_id]
        return c.payload if c.verify() else None


# ---------------------------------------------------------------------------
# KroneckerContainer (synchronized streams)
# ---------------------------------------------------------------------------

class KroneckerContainer(QShrinkContainer):
    def __init__(self, n_streams: int = 2) -> None:
        super().__init__(TopologyType.KRONECKER)
        for i in range(n_streams):
            self.add_domain(Domain(i, f"stream_{i}"))

    def add_synchronized_chunks(self, stream_data: List[bytes]) -> None:
        if len(stream_data) != len(self.domains):
            raise ValueError(f"Expected {len(self.domains)} streams")
        for i, d in enumerate(stream_data):
            h = ChunkHeader(ChunkType.BULK, len(d), zlib.crc32(d) & 0xFFFFFFFF)
            self.domains[i].add_chunk(Chunk(header=h, payload=d))


# ---------------------------------------------------------------------------
# Helper: build CrystalWeightMeta from FractalWeightStore
# ---------------------------------------------------------------------------

def build_crystal_meta_from_store(
    coordinate: str,
    shell: int,
    wreath: int,
    archetype: int,
    face: str,
    weight_store: Any = None,
) -> CrystalWeightMeta:
    """Build a fully enriched CrystalWeightMeta from crystal lattice data.

    Populates all organism metadata layers:
    - Crystal identity + weight seeds from FractalWeightStore
    - Mycelium graph connectivity
    - Metro routing + transport stacks
    - Z-point hierarchy
    - A-point archetype decomposition
    - Cross-neural mapping
    - Sacred geometry (phi-sigma, E8, Mobius)
    - 4D tesseract position
    """
    meta = CrystalWeightMeta.hollow(coordinate, shell, wreath, archetype, face)

    # ── A-point: archetype decomposition (deterministic from shell) ──
    _ARCHETYPE_NAMES = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    _ELEMENTS = ["Fire", "Earth", "Air", "Water"]
    _MODES = ["Cardinal", "Fixed", "Mutable"]
    _FACE_ELEMENT = {"S": "Earth", "F": "Fire", "C": "Water", "R": "Air"}
    _ELEMENT_FACE = {"Fire": "F", "Earth": "S", "Air": "R", "Water": "C"}

    meta.archetype_name = _ARCHETYPE_NAMES[(archetype - 1) % 12]
    meta.element = _ELEMENTS[(archetype - 1) % 4]
    meta.mode = _MODES[(archetype - 1) % 3]
    meta.element_face = _ELEMENT_FACE.get(meta.element, face)

    # ── Metro routing (deterministic from wreath/shell) ──
    _WREATH_METRO = {1: "Su", 2: "Me", 3: "Sa"}
    meta.metro_lines = [_WREATH_METRO.get(wreath, "Su")]
    meta.promotion_stage = _MODES[(shell - 1) % 3]
    meta.transport_stack = f"L{(shell - 1) // 12 + 1}"
    # Bridge endpoints: 5-neighbor adjacency
    meta.routing_bridges = [
        f"Xi108:W{wreath}:A{archetype}:S{max(1, shell - 1)}",
        f"Xi108:W{wreath}:A{archetype}:S{min(36, shell + 1)}",
        f"Xi108:W{max(1, wreath - 1)}:A{archetype}:S{shell}",
        f"Xi108:W{min(3, wreath + 1)}:A{archetype}:S{shell}",
        f"Xi108:W{wreath}:A{(archetype % 12) + 1}:S{shell}",
    ]

    # ── Z-point hierarchy ──
    meta.z_depth = (shell - 1) // 12  # 0=surface(S1-12), 1=mid(S13-24), 2=deep(S25-36)
    _Z_LEVELS = ["Nano", "Micro", "Seed", "Full"]
    meta.z_collapse_level = _Z_LEVELS[min(meta.z_depth, 3)]
    meta.z_address = f"Z{meta.z_depth}.{archetype}.{face}"
    meta.z_parent = f"Z{max(0, meta.z_depth - 1)}.{archetype}.{face}"

    # ── Cross-neural mapping ──
    _BRAIN_REGIONS = [
        "prefrontal", "temporal", "parietal", "occipital",
        "limbic", "cerebellum", "brainstem", "thalamus",
        "hippocampus", "amygdala", "basal_ganglia", "corpus_callosum",
    ]
    _ORGAN_SYSTEMS = [
        "nervous", "circulatory", "respiratory", "digestive",
        "endocrine", "immune", "muscular", "skeletal",
        "integumentary", "urinary", "reproductive", "lymphatic",
    ]
    meta.brain_region = _BRAIN_REGIONS[(archetype - 1) % 12]
    meta.organ_system = _ORGAN_SYSTEMS[(archetype - 1) % 12]
    meta.neural_layer = meta.z_depth
    _CELL_ROLES = ["sensor", "processor", "effector", "modulator"]
    meta.live_cell_role = _CELL_ROLES[{"S": 0, "F": 1, "C": 2, "R": 3}.get(face, 0)]

    # ── Sacred geometry ──
    meta.phi_angle = ((shell - 1) * 360.0 * PHI_INV) % 360.0  # golden angle spiral
    meta.phi_sigma_state = ((shell - 1) * 5 + (archetype - 1)) % 60  # Σ60 state
    meta.golden_ratio_depth = PHI ** (-(meta.z_depth + 1))
    # E8 vertex: project shell/archetype/face into 8D via phi-based rotation
    e8 = [0.0] * 8
    for dim in range(8):
        angle = (shell * PHI + archetype * 0.5 + dim * PHI_INV) * 2 * math.pi / 8
        e8[dim] = round(math.cos(angle) * meta.golden_ratio_depth, 6)
    meta.e8_vertex = e8
    # Mobius lens: deterministic from face
    _MOBIUS_LENSES = {"S": "Square", "F": "Flower", "C": "Cloud", "R": "Fractal"}
    meta.mobius_lens = _MOBIUS_LENSES.get(face, "Square")

    # ── 4D tesseract position ──
    meta.tesseract_element = {"S": 0, "F": 1, "C": 2, "R": 3}.get(face, 0)
    meta.tesseract_mode = (shell - 1) % 3
    meta.tesseract_archetype = (archetype - 1) % 12
    meta.tesseract_octave = (wreath - 1) % 3
    # Gate address: 4^4 = 256 positions in the tesseract
    meta.tesseract_gate = (
        meta.tesseract_element * 64
        + meta.tesseract_mode * 16  # noqa: W503
        + meta.tesseract_archetype  # noqa: W503
    ) % 256
    _FACE_NAMES = {0: "S", 1: "F", 2: "C", 3: "R"}
    meta.tesseract_address = (
        f"{_FACE_NAMES[meta.tesseract_element]}"
        f".{_MODES[meta.tesseract_mode]}"
        f".{_ARCHETYPE_NAMES[meta.tesseract_archetype]}"
        f".W{meta.tesseract_octave + 1}"
    )

    # ── Mycelium connectivity (deterministic from coordinate hash) ──
    coord_hash = int(hashlib.sha256(coordinate.encode()).hexdigest(), 16)
    meta.mycelium_shard = f"shard_{(coord_hash % 12) + 1}"
    meta.mycelium_degree = 4 + (coord_hash % 5)  # 4-8 edges typical
    meta.mycelium_cluster = f"cluster_{(archetype - 1) // 3 + 1}"
    # Neighbor edges from bridge endpoints
    meta.mycelium_edges = meta.routing_bridges[:meta.mycelium_degree]

    # ── Weight seeds from store ──
    if weight_store is not None:
        meta.path_weights = dict(getattr(weight_store, "path_weights", meta.path_weights))
        meta.resonance_weights = dict(getattr(weight_store, "resonance_weights", meta.resonance_weights))
        meta.desire_weights = dict(getattr(weight_store, "desire_weights", meta.desire_weights))
        meta.bridge_modulation = getattr(weight_store, "bridge_modulation", meta.bridge_modulation)

        shell_seeds = getattr(weight_store, "_shell_seeds", {})
        if shell in shell_seeds:
            ss = shell_seeds[shell]
            meta.shell_seed = ShellSeedMeta(
                shell=ss.shell, wreath=ss.wreath, mean=ss.mean, std=ss.std,
                count=ss.count, min_val=ss.min_val, max_val=ss.max_val,
                element_dist=dict(ss.element_dist), gate_means=dict(ss.gate_means),
            )

        arch_seeds = getattr(weight_store, "_archetype_seeds", {})
        if archetype in arch_seeds:
            ars = arch_seeds[archetype]
            meta.archetype_seed = ArchetypeSeedMeta(
                archetype=ars.archetype, name=ars.name, mean=ars.mean,
                std=ars.std, count=ars.count, wreath_means=dict(ars.wreath_means),
            )

        nano = getattr(weight_store, "_nano_seed", None)
        if nano is not None:
            meta.nano_seed = NanoSeedMeta(
                global_mean=nano.global_mean, global_std=nano.global_std,
                skew=nano.skew, kurtosis=nano.kurtosis, total_count=nano.total_count,
                element_means=dict(nano.element_means), gate_means=dict(nano.gate_means),
            )

    # ── Holographic seed: w = (1+i)/2 ──
    meta.holographic_w_real = 0.5
    meta.holographic_w_imag = 0.5
    meta.mirror_shell = 37 - shell
    meta.conservation_hash = meta.compute_conservation_hash()

    return meta
