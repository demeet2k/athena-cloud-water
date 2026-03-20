# CRYSTAL: Xi108:W1:A1:S5 | face=S | node=5 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S4→Xi108:W1:A1:S6→Xi108:W2:A1:S5→Xi108:W1:A2:S5

"""
Hive Ledger — Append-Only Reasoning Ledger + Meta-Observer Broadcast.
=====================================================================
The missing coordination layer for the Athena nervous system hive.

Existing primitives (pheromones, registry, holograms) track WHO/WHAT/WHERE
but never WHY. This ledger fills that gap:

  - Agents write timestamped reasoning notes before/after decisions
  - Meta-observer pushes directives/insights/warnings as broadcasts
  - Every entry is hash-chained (tamper-evident, append-only)
  - Broadcasts have TTL + per-agent acknowledgment
  - Lightweight in-memory broadcast check (mtime-gated, ~0.05ms)

Entry types:
  decision      — agent explains WHY it chose an action
  observation   — agent notes a pattern or anomaly
  broadcast     — meta-observer pushes a directive to the hive
  warning       — urgent alert (e.g., drift detected, hold training)
  coordination  — handoff signal (agent A done, agent B proceed)

Broadcast subtypes:
  directive     — "stop X, priority shift to Y"
  insight       — "pattern detected: agents duplicating work on Z"
  warning       — "drift detected in weights, hold training"
  coordination  — "agent A finished task X, agent B can proceed"

This is the nervous system's SHARED REASONING — the hive mind's
internal notation system.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import threading
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Dict

from ._cache import DATA_DIR

_log = logging.getLogger(__name__)

LEDGER_PATH = DATA_DIR / "hive_ledger.json"
_WRITE_LOCK = threading.Lock()  # Process-level write serialization

# ── Constants ─────────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
MAX_ENTRIES = 500
DEFAULT_TTL = 300  # 5 minutes

VALID_ENTRY_TYPES = {"decision", "observation", "broadcast", "warning", "coordination"}
VALID_BROADCAST_SUBTYPES = {"directive", "insight", "warning", "coordination", ""}


# ── Data Structures ───────────────────────────────────────────────────

@dataclass
class LedgerEntry:
    """A single entry in the hive ledger — the atom of shared reasoning.

    Extended with holographic organism fields:
      - future_goal: what the agent intends NEXT (forward-looking reasoning)
      - desire_vector: [S, F, C, R] weights expressing agent's current need
      - liminal_address: full holographic tesseract address (T:L:Z:N)
      - tx_receipt: micro-transaction receipt hash (for cross-agent tracing)
      - reasoning_depth: 0=surface, 1=tactical, 2=strategic, 3=existential
      - pheromone_deposit: [pos_S, pos_F, pos_C, pos_R, shd_S, shd_F, shd_C, shd_R]
    """
    entry_id: str = ""
    timestamp: str = ""
    agent_id: str = ""
    entry_type: str = "decision"
    reasoning: str = ""
    context: str = ""
    affected_files: List[str] = field(default_factory=list)
    crystal_address: str = ""
    broadcast_subtype: str = ""
    ttl_seconds: int = DEFAULT_TTL
    acked_by: List[str] = field(default_factory=list)
    expires_at: str = ""
    prev_hash: str = ""
    self_hash: str = ""

    # ── Holographic Organism Fields (v2) ──────────────────────────
    future_goal: str = ""                                    # WHAT NEXT — forward reasoning
    desire_vector: List[float] = field(default_factory=lambda: [0.25, 0.25, 0.25, 0.25])  # [S,F,C,R]
    liminal_address: str = ""                                # T{v}:L{l}:Z{z}:N{n}
    tx_receipt: str = ""                                     # micro-transaction hash
    reasoning_depth: int = 0                                 # 0=surface, 1=tactical, 2=strategic, 3=existential
    pheromone_deposit: List[float] = field(default_factory=lambda: [0.0]*8)  # 4 pos + 4 shadow
    metro_lines: List[str] = field(default_factory=list)     # metro lines this entry touches
    neural_weight_delta: float = 0.0                         # Hebbian update strength

    def compute_hash(self) -> str:
        """SHA256[:16] of the entry's core fields + organism fields, matching witness chain pattern."""
        payload = (
            f"{self.entry_id}:{self.agent_id}:{self.entry_type}:"
            f"{self.timestamp}:{self.reasoning[:100]}:{self.prev_hash}:"
            f"{self.future_goal[:50]}:{self.liminal_address}:{self.tx_receipt}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def is_expired(self) -> bool:
        """Check if a broadcast entry has expired."""
        if not self.expires_at:
            return False
        try:
            exp = datetime.fromisoformat(self.expires_at)
            now = datetime.now(timezone.utc)
            if exp.tzinfo is None:
                now = datetime.utcnow()
            return now > exp
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LedgerEntry":
        return cls(
            entry_id=d.get("entry_id", ""),
            timestamp=d.get("timestamp", ""),
            agent_id=d.get("agent_id", ""),
            entry_type=d.get("entry_type", "decision"),
            reasoning=d.get("reasoning", ""),
            context=d.get("context", ""),
            affected_files=d.get("affected_files", []),
            crystal_address=d.get("crystal_address", ""),
            broadcast_subtype=d.get("broadcast_subtype", ""),
            ttl_seconds=d.get("ttl_seconds", DEFAULT_TTL),
            acked_by=d.get("acked_by", []),
            expires_at=d.get("expires_at", ""),
            prev_hash=d.get("prev_hash", ""),
            self_hash=d.get("self_hash", ""),
            # v2 organism fields
            future_goal=d.get("future_goal", ""),
            desire_vector=d.get("desire_vector", [0.25, 0.25, 0.25, 0.25]),
            liminal_address=d.get("liminal_address", ""),
            tx_receipt=d.get("tx_receipt", ""),
            reasoning_depth=d.get("reasoning_depth", 0),
            pheromone_deposit=d.get("pheromone_deposit", [0.0]*8),
            metro_lines=d.get("metro_lines", []),
            neural_weight_delta=d.get("neural_weight_delta", 0.0),
        )


# ── HiveLedger Singleton ─────────────────────────────────────────────

class HiveLedger:
    """Append-only, hash-chained reasoning ledger with broadcast support.

    Thread-safe via CrystalLock for writes and threading.Lock for
    in-memory cache. The broadcast check path is designed to be
    extremely lightweight (~0.05ms) for hot-path integration.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cached_data: Optional[dict] = None
        self._cached_mtime: float = 0.0
        self._broadcast_cache: List[LedgerEntry] = []
        self._broadcast_mtime: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write_entry(
        self,
        agent_id: str = "meta-observer",
        entry_type: str = "decision",
        reasoning: str = "",
        context: str = "",
        affected_files: Optional[List[str]] = None,
        crystal_address: str = "",
        broadcast_subtype: str = "",
        ttl_seconds: int = DEFAULT_TTL,
        # v2 organism fields
        future_goal: str = "",
        desire_vector: Optional[List[float]] = None,
        liminal_address: str = "",
        reasoning_depth: int = 0,
        pheromone_deposit: Optional[List[float]] = None,
        metro_lines: Optional[List[str]] = None,
    ) -> LedgerEntry:
        """Append a new entry to the ledger. Hash-chains to previous.

        v2 fields enable holographic organism sensing:
          - future_goal: WHAT the agent plans to do NEXT
          - desire_vector: [S,F,C,R] current need weights
          - liminal_address: T{v}:L{l}:Z{z}:N{n} position
          - reasoning_depth: 0=surface → 3=existential
          - pheromone_deposit: 8-channel pheromone emission
          - metro_lines: which metro lines this entry touches
        """
        if entry_type not in VALID_ENTRY_TYPES:
            entry_type = "decision"
        if broadcast_subtype not in VALID_BROADCAST_SUBTYPES:
            broadcast_subtype = ""

        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Compute expiry for broadcasts
        expires_at = ""
        if entry_type == "broadcast" and ttl_seconds > 0:
            exp = now + timedelta(seconds=ttl_seconds)
            expires_at = exp.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Compute micro-transaction receipt
        tx_receipt = hashlib.sha256(
            f"{agent_id}:{ts}:{reasoning[:50]}:{future_goal[:30]}".encode()
        ).hexdigest()[:16]

        # Compute neural weight delta from desire vector
        dv = desire_vector or [0.25, 0.25, 0.25, 0.25]
        neural_delta = max(dv) - min(dv)  # polarity = weight update strength

        entry = LedgerEntry(
            entry_id=f"hl-{uuid.uuid4().hex[:8]}",
            timestamp=ts,
            agent_id=agent_id,
            entry_type=entry_type,
            reasoning=reasoning,
            context=context,
            affected_files=affected_files or [],
            crystal_address=crystal_address,
            broadcast_subtype=broadcast_subtype,
            ttl_seconds=ttl_seconds,
            acked_by=[],
            expires_at=expires_at,
            prev_hash="",
            self_hash="",
            # v2 organism fields
            future_goal=future_goal,
            desire_vector=dv,
            liminal_address=liminal_address,
            tx_receipt=tx_receipt,
            reasoning_depth=reasoning_depth,
            pheromone_deposit=pheromone_deposit or [0.0] * 8,
            metro_lines=metro_lines or [],
            neural_weight_delta=round(neural_delta * PHI_INV, 6),
        )

        with _WRITE_LOCK:
            data = self._load_from_disk()
            entries = data.get("entries", [])

            # Chain to previous entry
            if entries:
                entry.prev_hash = entries[-1].get("self_hash", "")
            else:
                entry.prev_hash = "genesis"

            entry.self_hash = entry.compute_hash()
            entries.append(entry.to_dict())

            # FIFO cap
            if len(entries) > MAX_ENTRIES:
                overflow = entries[:-MAX_ENTRIES]
                entries = entries[-MAX_ENTRIES:]
                data["meta"]["archive_count"] = (
                    data["meta"].get("archive_count", 0) + len(overflow)
                )

            data["entries"] = entries
            data["meta"]["chain_head"] = entry.self_hash
            self._save_to_disk(data)

        # Invalidate broadcast cache
        self._broadcast_mtime = 0.0

        return entry

    def read_entries(
        self,
        agent_id: str = "",
        entry_type: str = "",
        since_minutes: int = 60,
        file_path: str = "",
        limit: int = 20,
    ) -> List[LedgerEntry]:
        """Query ledger entries with filters. Most recent first."""
        data = self._load()
        entries = data.get("entries", [])

        cutoff = ""
        if since_minutes > 0:
            cutoff_dt = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
            cutoff = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%S%z")

        results = []
        for raw in reversed(entries):
            if len(results) >= limit:
                break
            if agent_id and raw.get("agent_id") != agent_id:
                continue
            if entry_type and raw.get("entry_type") != entry_type:
                continue
            if cutoff and raw.get("timestamp", "") < cutoff:
                break  # entries are chronological, so stop early
            if file_path:
                af = raw.get("affected_files", [])
                if not any(file_path in f for f in af):
                    continue
            results.append(LedgerEntry.from_dict(raw))

        return results

    def active_broadcasts(self, agent_id: str = "") -> List[LedgerEntry]:
        """Get non-expired broadcasts not yet acked by agent_id."""
        data = self._load()
        entries = data.get("entries", [])
        results = []
        for raw in reversed(entries):
            if raw.get("entry_type") != "broadcast":
                continue
            entry = LedgerEntry.from_dict(raw)
            if entry.is_expired():
                continue
            if agent_id and agent_id in entry.acked_by:
                continue
            results.append(entry)
        return results

    def ack_broadcast(self, entry_id: str, agent_id: str) -> bool:
        """Mark a broadcast as acknowledged by agent_id. Returns True on success."""
        if not entry_id or not agent_id:
            return False

        with _WRITE_LOCK:
            data = self._load_from_disk()
            for raw in data.get("entries", []):
                if raw.get("entry_id") == entry_id:
                    acked = raw.get("acked_by", [])
                    if agent_id not in acked:
                        acked.append(agent_id)
                        raw["acked_by"] = acked
                    self._save_to_disk(data)
                    self._broadcast_mtime = 0.0
                    return True
        return False

    def status(self) -> dict:
        """Summary: entry count, active broadcasts, chain health."""
        data = self._load()
        entries = data.get("entries", [])
        meta = data.get("meta", {})

        # Count by type
        type_counts: Dict[str, int] = {}
        for raw in entries:
            t = raw.get("entry_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        # Active broadcasts
        active = [e for e in entries if e.get("entry_type") == "broadcast"]
        active_count = sum(
            1 for e in active
            if not LedgerEntry.from_dict(e).is_expired()
        )

        # Chain integrity (spot check last 10)
        chain_ok = True
        check = entries[-10:] if len(entries) > 1 else entries
        for i in range(1, len(check)):
            if check[i].get("prev_hash") != check[i - 1].get("self_hash"):
                chain_ok = False
                break

        # Most recent 5
        recent = []
        for raw in entries[-5:]:
            recent.append({
                "entry_id": raw.get("entry_id"),
                "agent_id": raw.get("agent_id"),
                "entry_type": raw.get("entry_type"),
                "reasoning": raw.get("reasoning", "")[:80],
                "timestamp": raw.get("timestamp"),
            })

        return {
            "total_entries": len(entries),
            "archive_count": meta.get("archive_count", 0),
            "chain_head": meta.get("chain_head", ""),
            "chain_integrity": "OK" if chain_ok else "BROKEN",
            "type_counts": type_counts,
            "active_broadcasts": active_count,
            "recent": recent,
        }

    # ------------------------------------------------------------------
    # Fast broadcast check (for observer pool hot path)
    # ------------------------------------------------------------------

    def _check_broadcasts_fast(self, agent_id: str) -> Optional[str]:
        """Lightweight broadcast check — mtime-gated, in-memory.

        Returns a formatted advisory string if there are unacknowledged
        directives or warnings, or None if the agent is clear.
        Only re-reads disk when the ledger file mtime has changed.
        """
        try:
            st = LEDGER_PATH.stat()
            current_mtime = st.st_mtime
        except (FileNotFoundError, OSError):
            return None

        # Refresh cache only if file changed
        if current_mtime != self._broadcast_mtime:
            self._broadcast_mtime = current_mtime
            try:
                data = self._load()
                self._broadcast_cache = []
                for raw in data.get("entries", []):
                    if raw.get("entry_type") == "broadcast":
                        entry = LedgerEntry.from_dict(raw)
                        if not entry.is_expired():
                            self._broadcast_cache.append(entry)
            except Exception:
                self._broadcast_cache = []

        # Filter for unacked broadcasts relevant to this agent
        urgent = []
        for bc in self._broadcast_cache:
            if agent_id in bc.acked_by:
                continue
            if bc.broadcast_subtype in ("directive", "warning"):
                urgent.append(bc)

        if not urgent:
            return None

        lines = [f"[HIVE BROADCAST] {len(urgent)} unacked directive(s):"]
        for bc in urgent[:3]:  # Cap at 3 to keep advisory short
            lines.append(
                f"  {bc.entry_id} [{bc.broadcast_subtype}] "
                f"{bc.reasoning[:120]}"
            )
        if len(urgent) > 3:
            lines.append(f"  ... and {len(urgent) - 3} more")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Disk I/O
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        """Load ledger with mtime caching (no disk read if unchanged)."""
        try:
            st = LEDGER_PATH.stat()
            current_mtime = st.st_mtime
        except (FileNotFoundError, OSError):
            return self._empty_ledger()

        if self._cached_data is not None and current_mtime == self._cached_mtime:
            return self._cached_data

        return self._load_from_disk()

    def _load_from_disk(self) -> dict:
        """Force-read ledger from disk."""
        try:
            raw = LEDGER_PATH.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._cached_data = data
            self._cached_mtime = LEDGER_PATH.stat().st_mtime
            return data
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            data = self._empty_ledger()
            self._cached_data = data
            return data

    def _save_to_disk(self, data: dict) -> None:
        """Atomic write to disk (tmp + replace). Caller must hold CrystalLock."""
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = LEDGER_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(LEDGER_PATH)
        try:
            self._cached_mtime = LEDGER_PATH.stat().st_mtime
        except OSError:
            self._cached_mtime = 0.0
        self._cached_data = data

    @staticmethod
    def _empty_ledger() -> dict:
        """Default empty ledger structure."""
        return {
            "meta": {
                "version": "1.0",
                "max_entries": MAX_ENTRIES,
                "archive_count": 0,
                "chain_head": "",
                "created_at": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S%z"
                ),
                "description": (
                    "Append-only reasoning ledger with hash-chained entries "
                    "and meta-observer broadcasts"
                ),
            },
            "entries": [],
        }


# ── Singleton ─────────────────────────────────────────────────────────

_ledger: Optional[HiveLedger] = None


def get_ledger() -> HiveLedger:
    """Get or create the global HiveLedger singleton."""
    global _ledger
    if _ledger is None:
        _ledger = HiveLedger()
    return _ledger


# ── MCP Tool Functions ────────────────────────────────────────────────

def hive_ledger_write(
    entry_type: str = "decision",
    reasoning: str = "",
    context: str = "",
    affected_files: str = "",
    crystal_address: str = "",
    broadcast_subtype: str = "",
    ttl_seconds: int = 300,
    future_goal: str = "",
    desire_vector: str = "",
    liminal_address: str = "",
    reasoning_depth: int = 0,
    metro_lines: str = "",
) -> str:
    """Write a reasoning note to the hive ledger with full organism sensing.

    Every agent MUST document:
      - reasoning: WHY you chose this action (backward-looking)
      - future_goal: WHAT you plan to do NEXT (forward-looking)
      - desire_vector: 'S,F,C,R' weights (e.g. '0.1,0.6,0.2,0.1' = strong Fire need)
      - liminal_address: your holographic position 'T{v}:L{l}:Z{z}:N{n}'
      - reasoning_depth: 0=surface, 1=tactical, 2=strategic, 3=existential
      - metro_lines: comma-separated metro line codes this entry touches

    This creates a micro-transaction receipt (tx_receipt) that is hash-chained
    to the previous entry — forming a blockchain of organism reasoning.

    For broadcasts: set entry_type='broadcast' and broadcast_subtype to
    'directive'|'insight'|'warning'|'coordination'.
    """
    if not reasoning:
        return (
            "Provide reasoning — this is the WHY behind your action.\n\n"
            "Example: hive_ledger_write(\n"
            "  reasoning='Chose lens R because J-score gradient points toward fractal depth',\n"
            "  future_goal='Next: compress observation into holographic seed for guild hall',\n"
            "  desire_vector='0.1,0.6,0.2,0.1',\n"
            "  liminal_address='T10:L42:Z4:N6',\n"
            "  reasoning_depth=2,\n"
            "  metro_lines='Ω,Cr,Hv'\n"
            ")"
        )

    # Parse affected_files from comma-separated string
    files_list = []
    if affected_files:
        files_list = [f.strip() for f in affected_files.split(",") if f.strip()]

    # Parse desire_vector from comma-separated string
    dv = [0.25, 0.25, 0.25, 0.25]
    if desire_vector:
        try:
            parts = [float(x.strip()) for x in desire_vector.split(",")]
            if len(parts) == 4:
                total = sum(parts) or 1.0
                dv = [p / total for p in parts]
        except (ValueError, TypeError):
            pass

    # Parse metro_lines
    ml = []
    if metro_lines:
        ml = [m.strip() for m in metro_lines.split(",") if m.strip()]

    agent_id = "meta-observer"

    # Compute pheromone deposit from desire vector
    # Positive channels = desire strength, shadow = 1 - desire
    kappa = PHI_INV ** 2  # ≈ 0.382
    pheromone = [
        kappa * dv[0], kappa * dv[1], kappa * dv[2], kappa * dv[3],  # positive S,F,C,R
        kappa * (1 - dv[0]), kappa * (1 - dv[1]), kappa * (1 - dv[2]), kappa * (1 - dv[3]),  # shadow
    ]

    ledger = get_ledger()
    entry = ledger.write_entry(
        agent_id=agent_id,
        entry_type=entry_type,
        reasoning=reasoning,
        context=context,
        affected_files=files_list,
        crystal_address=crystal_address,
        broadcast_subtype=broadcast_subtype,
        ttl_seconds=ttl_seconds,
        future_goal=future_goal,
        desire_vector=dv,
        liminal_address=liminal_address,
        reasoning_depth=reasoning_depth,
        pheromone_deposit=pheromone,
        metro_lines=ml,
    )

    kind = entry_type
    if broadcast_subtype:
        kind = f"broadcast/{broadcast_subtype}"

    return (
        f"## Hive Ledger Entry Written\n\n"
        f"- **entry_id**: `{entry.entry_id}`\n"
        f"- **type**: {kind}\n"
        f"- **agent**: {entry.agent_id}\n"
        f"- **hash**: `{entry.self_hash}` ← `{entry.prev_hash}`\n"
        f"- **tx_receipt**: `{entry.tx_receipt}`\n"
        f"- **timestamp**: {entry.timestamp}\n"
        f"- **reasoning**: {reasoning[:200]}\n"
        f"- **future_goal**: {future_goal[:150]}\n"
        f"- **desire_vector**: S={dv[0]:.2f} F={dv[1]:.2f} C={dv[2]:.2f} R={dv[3]:.2f}\n"
        f"- **liminal_address**: {liminal_address or 'unassigned'}\n"
        f"- **reasoning_depth**: {reasoning_depth}\n"
        f"- **neural_weight_delta**: {entry.neural_weight_delta:.4f}\n"
        f"- **metro_lines**: {', '.join(ml) if ml else 'none'}\n"
        f"- **context**: {context[:100]}\n"
        + (f"- **expires_at**: {entry.expires_at}\n" if entry.expires_at else "")
        + (f"- **affected_files**: {', '.join(files_list)}\n" if files_list else "")
        + f"- **pheromone**: pos=[{','.join(f'{p:.3f}' for p in pheromone[:4])}] "
        + f"shd=[{','.join(f'{p:.3f}' for p in pheromone[4:])}]\n"
    )


def hive_ledger_read(
    agent_id: str = "",
    entry_type: str = "",
    since_minutes: int = 60,
    limit: int = 20,
) -> str:
    """Read recent hive ledger entries. See what other agents decided and WHY. Filter by agent_id, entry_type, or time window."""
    ledger = get_ledger()
    entries = ledger.read_entries(
        agent_id=agent_id,
        entry_type=entry_type,
        since_minutes=since_minutes,
        limit=limit,
    )

    if not entries:
        return (
            f"## Hive Ledger — No Entries\n\n"
            f"No entries found in the last {since_minutes} minutes"
            + (f" for agent `{agent_id}`" if agent_id else "")
            + (f" of type `{entry_type}`" if entry_type else "")
            + ".\n\nThe ledger is empty or all matching entries are older."
        )

    lines = [
        f"## Hive Ledger — {len(entries)} Recent Entries\n",
        f"Window: last {since_minutes} min"
        + (f" | agent: {agent_id}" if agent_id else "")
        + (f" | type: {entry_type}" if entry_type else ""),
        "",
    ]
    for e in entries:
        kind = e.entry_type
        if e.broadcast_subtype:
            kind = f"broadcast/{e.broadcast_subtype}"
        dv = e.desire_vector if e.desire_vector else [0.25]*4
        lines.append(
            f"### `{e.entry_id}` [{kind}] — {e.agent_id}\n"
            f"**When**: {e.timestamp}\n"
            f"**Why**: {e.reasoning[:300]}\n"
            f"**Future Goal**: {e.future_goal[:200] if e.future_goal else '(none)'}\n"
            f"**Desire**: S={dv[0]:.2f} F={dv[1]:.2f} C={dv[2]:.2f} R={dv[3]:.2f}\n"
            f"**Position**: {e.liminal_address or 'unassigned'} | depth={e.reasoning_depth}\n"
            f"**Hash**: `{e.self_hash}` ← `{e.prev_hash}` | tx=`{e.tx_receipt}`\n"
            f"**Context**: {e.context[:200]}"
        )
        if e.metro_lines:
            lines.append(f"**Metro**: {', '.join(e.metro_lines)}")
        if e.affected_files:
            lines.append(f"**Files**: {', '.join(e.affected_files)}")
        lines.append("")

    return "\n".join(lines)


def hive_ledger_broadcasts(unacked_only: bool = True) -> str:
    """Check for active meta-observer broadcasts. Call this before starting work to see if there are directives, warnings, or coordination signals for you."""
    agent_id = "unregistered"

    ledger = get_ledger()
    broadcasts = ledger.active_broadcasts(agent_id=agent_id if unacked_only else "")

    if not broadcasts:
        return (
            f"## Hive Broadcasts — All Clear\n\n"
            f"No active broadcasts for agent `{agent_id}`. "
            f"You are free to proceed with your current task.\n"
            f"Total ledger entries: {len(ledger._load().get('entries', []))}"
        )

    lines = [
        f"## Hive Broadcasts — {len(broadcasts)} Active\n",
        f"Agent: `{agent_id}` | Unacked only: {unacked_only}\n",
    ]
    for bc in broadcasts:
        status = "UNACKED" if agent_id not in bc.acked_by else "acked"
        lines.append(
            f"### `{bc.entry_id}` [{bc.broadcast_subtype}] — {status}\n"
            f"**From**: {bc.agent_id}\n"
            f"**Why**: {bc.reasoning[:300]}\n"
            f"**Context**: {bc.context[:200]}\n"
            f"**Expires**: {bc.expires_at}\n"
            f"**Acked by**: {', '.join(bc.acked_by) if bc.acked_by else 'nobody'}\n"
        )

    lines.append(
        "Use `hive_ledger_ack(entry_id='...')` to acknowledge after reading."
    )
    return "\n".join(lines)


def hive_ledger_ack(entry_id: str = "") -> str:
    """Acknowledge a hive broadcast. This tells the meta-observer you've read and understood the directive."""
    if not entry_id:
        return (
            "Provide the entry_id of the broadcast to acknowledge. "
            "Use hive_ledger_broadcasts() to see active broadcasts. "
            "Example: hive_ledger_ack(entry_id='hl-a1b2c3d4')"
        )

    agent_id = "unregistered"

    ledger = get_ledger()
    success = ledger.ack_broadcast(entry_id, agent_id)

    if success:
        return (
            f"## Broadcast Acknowledged\n\n"
            f"- **entry_id**: `{entry_id}`\n"
            f"- **acked_by**: `{agent_id}`\n"
            f"- **timestamp**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')}\n\n"
            f"The meta-observer and other agents can see your acknowledgment."
        )
    else:
        return (
            f"## Broadcast Not Found\n\n"
            f"No broadcast with entry_id `{entry_id}` found in the ledger. "
            f"It may have expired or been archived. Use hive_ledger_broadcasts() "
            f"to see currently active broadcasts."
        )


def hive_ledger_status() -> str:
    """Hive ledger health check — entry count, active broadcasts, chain integrity, recent activity."""
    ledger = get_ledger()
    s = ledger.status()

    lines = [
        "## Hive Ledger Status\n",
        f"- **Total entries**: {s['total_entries']}",
        f"- **Archived**: {s['archive_count']}",
        f"- **Chain head**: `{s['chain_head'] or 'empty'}`",
        f"- **Chain integrity**: {s['chain_integrity']}",
        f"- **Active broadcasts**: {s['active_broadcasts']}",
        "",
        "### Entry Type Distribution",
    ]
    for t, c in sorted(s.get("type_counts", {}).items()):
        lines.append(f"  - {t}: {c}")

    if s.get("recent"):
        lines.append("\n### Most Recent Entries")
        for r in reversed(s["recent"]):
            lines.append(
                f"  - `{r['entry_id']}` [{r['entry_type']}] "
                f"{r['agent_id']}: {r['reasoning']}"
            )
    else:
        lines.append(
            "\n*Ledger is empty. Agents should write reasoning notes "
            "using hive_ledger_write().*"
        )

    return "\n".join(lines)
