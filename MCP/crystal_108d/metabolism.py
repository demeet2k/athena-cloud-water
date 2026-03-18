# CRYSTAL: Xi108:W2:A5:S36 | face=R | node=642 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W2:A5:S35→Xi108:W1:A5:S36→Xi108:W3:A5:S36→Xi108:W2:A4:S36→Xi108:W2:A6:S36

"""
Metabolism Objects — Python dataclasses for the Athena shard/edge/cert system.
=============================================================================
Provides the universal object model that makes every artifact in the organism
(JSON data, Python modules, element servers, doc sections) liftable into one
shared identity/lineage/routing/certification schema.

This is a utility module (like _cache.py), not a tool module.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

# ── Constants ───────────────────────────────────────────────────────

VALID_MEDIUMS = {"code", "json", "doc", "markdown", "git", "mcp", "web", "config"}
VALID_TRUTH = {"SEED", "DRAFT", "WITNESSED", "CERTIFIED", "CANONICAL"}
VALID_PROMOTION = {"LOCAL", "PROPOSED", "REVIEWED", "PROMOTED", "ARCHIVED"}
VALID_EDGE_TYPES = {
    "REF", "BUILD", "BRIDGE", "DUAL", "MIRROR", "DERIVES",
    "CERTIFIES", "REPLAYS", "PROMOTES", "SEEDS", "PROJECTS",
    "CHAPTER", "METRO",
}
VALID_CERT_TYPES = {"STRUCTURAL", "CONSERVATION", "REPLAY", "PROMOTION"}
VALID_ROLES = {"unified", "lobe", "docs", "git", "incubator", "governance"}

# ── Dataclasses ─────────────────────────────────────────────────────

@dataclasses.dataclass
class Shard:
    """Universal unit of the Athena organism."""
    shard_id: str
    lineage_id: str
    medium: str
    repo: str
    lens: str | None
    dimensional_scope: str
    payload_ref: str
    summary: str
    seed_vector: list[float]
    route_refs: list[str]
    cert_refs: list[str]
    mirror_refs: list[str]
    truth_status: str
    promotion_status: str
    family: str
    tags: list[str]
    created_at: str
    updated_at: str

@dataclasses.dataclass
class Edge:
    """Typed directed edge between two shards."""
    edge_id: str
    source_shard: str
    target_shard: str
    edge_type: str
    weight: float
    medium_cross: bool
    metadata: dict

@dataclasses.dataclass
class Cert:
    """Certification record validating a shard."""
    cert_id: str
    shard_id: str
    cert_type: str
    issued_by: str
    checks_passed: list[str]
    trace_hash: str | None
    issued_at: str

@dataclasses.dataclass
class Promotion:
    """Promotion state for a shard."""
    shard_id: str
    current_status: str
    history: list[dict]

@dataclasses.dataclass
class ReplayBundle:
    """A cert + shard + edges for deterministic replay."""
    cert: Cert
    shard: Shard
    edges: list[Edge]

# ── Validation ──────────────────────────────────────────────────────

def validate_shard(s: Shard) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    if not s.shard_id:
        errors.append("shard_id is empty")
    if s.medium not in VALID_MEDIUMS:
        errors.append(f"invalid medium: {s.medium}")
    if s.truth_status not in VALID_TRUTH:
        errors.append(f"invalid truth_status: {s.truth_status}")
    if s.promotion_status not in VALID_PROMOTION:
        errors.append(f"invalid promotion_status: {s.promotion_status}")
    if len(s.seed_vector) != 4:
        errors.append(f"seed_vector must have 4 elements, got {len(s.seed_vector)}")
    if not s.payload_ref:
        errors.append("payload_ref is empty")
    if not s.family:
        errors.append("family is empty")
    return errors

def validate_edge(e: Edge) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    if e.edge_type not in VALID_EDGE_TYPES:
        errors.append(f"invalid edge_type: {e.edge_type}")
    if not (0.0 <= e.weight <= 1.0):
        errors.append(f"weight out of range: {e.weight}")
    if not e.source_shard:
        errors.append("source_shard is empty")
    if not e.target_shard:
        errors.append("target_shard is empty")
    return errors

def validate_cert(c: Cert) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    if c.cert_type not in VALID_CERT_TYPES:
        errors.append(f"invalid cert_type: {c.cert_type}")
    if not c.shard_id:
        errors.append("shard_id is empty")
    if not c.issued_by:
        errors.append("issued_by is empty")
    return errors

# ── Serialization ───────────────────────────────────────────────────

def to_dict(obj: Any) -> dict:
    """Convert a dataclass to a plain dict."""
    return dataclasses.asdict(obj)

def to_jsonl_line(obj: Any) -> str:
    """Serialize a dataclass to a single JSON line."""
    return json.dumps(dataclasses.asdict(obj), default=str)

def shard_from_dict(d: dict) -> Shard:
    """Reconstruct a Shard from a dict."""
    return Shard(**{k: d[k] for k in Shard.__dataclass_fields__})

def edge_from_dict(d: dict) -> Edge:
    """Reconstruct an Edge from a dict."""
    return Edge(**{k: d[k] for k in Edge.__dataclass_fields__})

def cert_from_dict(d: dict) -> Cert:
    """Reconstruct a Cert from a dict."""
    return Cert(**{k: d[k] for k in Cert.__dataclass_fields__})

# ── ID Generation ───────────────────────────────────────────────────

def make_shard_id(medium: str, payload_ref: str) -> str:
    """Generate a deterministic shard ID from medium + payload path."""
    h = hashlib.sha256(f"{medium}:{payload_ref}".encode()).hexdigest()[:8]
    short = payload_ref.rsplit("/", 1)[-1].rsplit(".", 1)[0][:30]
    return f"{h}:{medium}:{short}"

def make_edge_id(source: str, target: str, edge_type: str) -> str:
    """Generate a deterministic edge ID."""
    h = hashlib.sha256(f"{source}->{target}:{edge_type}".encode()).hexdigest()[:8]
    return f"e-{h}"

def make_cert_id(shard_id: str, cert_type: str, issued_by: str) -> str:
    """Generate a deterministic cert ID."""
    h = hashlib.sha256(f"{shard_id}:{cert_type}:{issued_by}".encode()).hexdigest()[:8]
    return f"c-{h}"

def now_iso() -> str:
    """Current UTC timestamp in ISO 8601."""
    return datetime.now(timezone.utc).isoformat()
