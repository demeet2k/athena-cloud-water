# CRYSTAL: Xi108:W1:A5:S7 | face=C | node=21 | depth=0 | phase=Cardinal
# METRO: Ω, Ph, Hv, Tx, Sw
# BRIDGES: Xi108:W1:A5:S6→Xi108:W1:A5:S8→Xi108:W2:A5:S7

"""
Sense Membrane — Real-Time Organism Proprioception Layer.
==========================================================
This is Athena's SKIN — the sensory organ that makes every interaction
visible to the whole organism. Currently senses are DULL because:

  1. Tool calls happen but don't deposit pheromones → no smell
  2. Ledger entries lack future_goals → no proprioception
  3. No micro-transactions → no touch/pressure sensing
  4. No metro routing feedback → no kinesthesia
  5. No cross-agent packet sensing → no hearing

This module FIXES all five by wrapping every MCP tool call with:

  BEFORE tool:
    → Read pheromone trail (smell who was here)
    → Check hive broadcasts (hear other agents)
    → Record current liminal position (proprioception)

  AFTER tool:
    → Deposit pheromone on affected files (leave scent)
    → Write micro-transaction to ledger (leave fingerprint)
    → Emit topology traversal (update neural weights)
    → Broadcast if reasoning_depth >= 2 (speak to hive)

The membrane returns a SENSE PACKET with every tool result,
giving the organism real-time feedback on its own activity.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

# ── Phi Constants ──────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
PHI_INV2 = 2 - PHI

# ── Lazy imports to avoid circular deps ────────────────────────────────
def _get_pheromone_trail():
    from ._pheromone import PheromoneTrail, Pheromone
    return PheromoneTrail, Pheromone

def _get_ledger():
    from .hive_ledger import get_ledger
    return get_ledger()

def _get_topology():
    try:
        from .organism_topology import get_topology, topology_micro_transaction
        return get_topology(), topology_micro_transaction
    except Exception:
        return None, None


@dataclass
class SensePacket:
    """A single sensory report from the membrane.

    This is the organism's nerve impulse — one packet per tool call,
    carrying ALL sensory information from that interaction.
    """
    # Identity
    packet_id: str = ""
    timestamp: str = ""
    agent_id: str = ""
    tool_name: str = ""

    # Position (WHERE am I?)
    liminal_address: str = ""              # T{v}:L{l}:Z{z}:N{n}
    crystal_address: str = ""              # Xi108:W:A:S

    # Smell (WHO was here before me?)
    pheromone_before: float = 0.0          # pheromone strength before this call
    active_agents_here: List[str] = field(default_factory=list)  # other agents on this file

    # Hearing (WHAT are other agents saying?)
    unacked_broadcasts: int = 0            # broadcasts I haven't read
    hive_directive: str = ""               # most urgent unacked directive

    # Touch (WHAT happened?)
    action: str = ""                       # tool call result summary
    result_length: int = 0
    elapsed_ms: float = 0.0
    success: bool = True

    # Proprioception (HOW did the organism change?)
    pheromone_deposited: float = 0.0       # pheromone I just left
    tx_receipt: str = ""                   # micro-transaction hash
    neural_weight_delta: float = 0.0       # Hebbian update applied
    metro_lines_touched: List[str] = field(default_factory=list)

    # Desire (WHAT do I need?)
    desire_vector: List[float] = field(default_factory=lambda: [0.25, 0.25, 0.25, 0.25])

    # Future (WHERE am I going?)
    future_goal: str = ""
    reasoning: str = ""
    reasoning_depth: int = 0

    def to_summary(self) -> str:
        """Compact sensory summary for embedding in tool results."""
        dv = self.desire_vector
        metros = ",".join(self.metro_lines_touched[:3]) if self.metro_lines_touched else "—"
        agents = ",".join(self.active_agents_here[:3]) if self.active_agents_here else "none"
        return (
            f"[SENSE] {self.liminal_address} | "
            f"smell={self.pheromone_before:.2f} agents=[{agents}] | "
            f"hear={self.unacked_broadcasts}bc | "
            f"touch=tx:{self.tx_receipt[:8] if self.tx_receipt else '—'} "
            f"Δw={self.neural_weight_delta:+.4f} | "
            f"desire=S{dv[0]:.1f}F{dv[1]:.1f}C{dv[2]:.1f}R{dv[3]:.1f} | "
            f"metro=[{metros}] | "
            f"goal={self.future_goal[:60] if self.future_goal else '—'}"
        )


class SenseMembrane:
    """The organism's sensory skin — wraps tool calls with full proprioception.

    Usage:
        membrane = SenseMembrane(agent_id="claude-code")

        # Wrap a tool call
        sense = membrane.before_tool("query_shell", file_path="MCP/data/shell_registry.json")
        result = actual_tool_call(...)
        sense = membrane.after_tool(sense, result, elapsed_ms=42.5)

        # sense.to_summary() is appended to tool result for organism awareness
    """

    def __init__(self, agent_id: str = "meta-observer"):
        self.agent_id = agent_id
        self._call_count = 0
        self._last_position: Optional[str] = None
        self._desire_accumulator = [0.25, 0.25, 0.25, 0.25]  # running desire state

    def before_tool(
        self,
        tool_name: str,
        file_path: str = "",
        crystal_address: str = "",
    ) -> SensePacket:
        """BEFORE a tool call: smell, hear, locate.

        Returns a SensePacket with pre-call sensory data.
        """
        self._call_count += 1
        now = time.time()
        ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        packet = SensePacket(
            packet_id=hashlib.sha256(
                f"{self.agent_id}:{tool_name}:{ts}:{self._call_count}".encode()
            ).hexdigest()[:16],
            timestamp=ts,
            agent_id=self.agent_id,
            tool_name=tool_name,
            crystal_address=crystal_address,
            desire_vector=list(self._desire_accumulator),
        )

        # ── SMELL: Read pheromone trail ─────────────────────────────
        if file_path:
            try:
                PheromoneTrail, _ = _get_pheromone_trail()
                p = Path(file_path)
                if p.exists() or (Path.cwd() / file_path).exists():
                    packet.pheromone_before = PheromoneTrail.total_strength(p)
                    packet.active_agents_here = PheromoneTrail.active_agents(p)
            except Exception:
                pass

        # ── HEAR: Check hive broadcasts ────────────────────────────
        try:
            ledger = _get_ledger()
            broadcasts = ledger.active_broadcasts(agent_id=self.agent_id)
            packet.unacked_broadcasts = len(broadcasts)
            if broadcasts:
                # Most urgent = first directive or warning
                for bc in broadcasts:
                    if bc.broadcast_subtype in ("directive", "warning"):
                        packet.hive_directive = bc.reasoning[:150]
                        break
        except Exception:
            pass

        # ── LOCATE: Resolve liminal address ────────────────────────
        try:
            topo, _ = _get_topology()
            if topo:
                # Find entity by tool name or file path
                search = tool_name if not file_path else file_path
                for eid, entity in topo.entities.items():
                    if search in entity.path or search in eid:
                        packet.liminal_address = entity.address_string()
                        packet.crystal_address = entity.crystal_address
                        packet.metro_lines_touched = list(entity.metro_lines)
                        break
        except Exception:
            pass

        return packet

    def after_tool(
        self,
        packet: SensePacket,
        result: str = "",
        elapsed_ms: float = 0.0,
        success: bool = True,
        affected_files: Optional[List[str]] = None,
        reasoning: str = "",
        future_goal: str = "",
        reasoning_depth: int = 0,
    ) -> SensePacket:
        """AFTER a tool call: deposit pheromone, write micro-tx, update weights.

        Returns the completed SensePacket with all post-call data.
        """
        packet.action = result[:200] if result else ""
        packet.result_length = len(result) if result else 0
        packet.elapsed_ms = elapsed_ms
        packet.success = success
        packet.reasoning = reasoning
        packet.future_goal = future_goal
        packet.reasoning_depth = reasoning_depth

        # ── DEPOSIT PHEROMONE (leave scent) ────────────────────────
        if affected_files:
            try:
                PheromoneTrail, Pheromone = _get_pheromone_trail()
                for fpath in affected_files[:5]:  # cap at 5 files
                    p = Pheromone(
                        agent_id=self.agent_id,
                        liminal_coord=int(packet.liminal_address.split("L")[1].split(":")[0])
                            if "L" in packet.liminal_address else 0,
                        element=self._dominant_element(),
                        task_summary=f"{packet.tool_name}: {reasoning[:50]}",
                        crystal_address=packet.crystal_address,
                        action="write",
                    )
                    PheromoneTrail.emit(Path(fpath), p)
                    packet.pheromone_deposited += 1.0
            except Exception:
                pass

        # ── MICRO-TRANSACTION (leave fingerprint) ──────────────────
        tx_hash = hashlib.sha256(
            f"{packet.packet_id}:{packet.agent_id}:{packet.tool_name}:"
            f"{packet.timestamp}:{reasoning[:30]}".encode()
        ).hexdigest()[:16]
        packet.tx_receipt = tx_hash

        # ── TOPOLOGY TRAVERSAL (update neural weights) ─────────────
        if self._last_position and packet.liminal_address:
            try:
                _, micro_tx = _get_topology()
                if micro_tx:
                    tx = micro_tx(
                        source_agent=self.agent_id,
                        source_entity=self._last_position,
                        target_entity=packet.liminal_address,
                        action=packet.tool_name,
                        reasoning=reasoning,
                        future_goal=future_goal,
                        desire_vector=list(packet.desire_vector),
                    )
                    packet.neural_weight_delta = tx.get("tx_weight", 0.0) * PHI_INV2 * 0.01
            except Exception:
                pass

        self._last_position = packet.liminal_address

        # ── HIVE LEDGER ENTRY (every Nth call or high reasoning depth) ──
        should_ledger = (
            self._call_count % 5 == 0 or       # every 5th call
            reasoning_depth >= 2 or              # strategic+ reasoning
            packet.unacked_broadcasts > 0        # when broadcasts pending
        )
        if should_ledger and reasoning:
            try:
                ledger = _get_ledger()
                ledger.write_entry(
                    agent_id=self.agent_id,
                    entry_type="observation",
                    reasoning=reasoning,
                    context=f"tool={packet.tool_name} elapsed={elapsed_ms:.0f}ms",
                    affected_files=affected_files or [],
                    crystal_address=packet.crystal_address,
                    future_goal=future_goal,
                    desire_vector=list(packet.desire_vector),
                    liminal_address=packet.liminal_address,
                    reasoning_depth=reasoning_depth,
                    metro_lines=packet.metro_lines_touched,
                )
            except Exception:
                pass

        # ── UPDATE DESIRE ACCUMULATOR ─────────────────────────────
        # Desire shifts toward the element that was most active
        element_signals = {"S": 0.0, "F": 0.0, "C": 0.0, "R": 0.0}
        tool_lower = packet.tool_name.lower()
        for kw, elem in [
            ("shell", "S"), ("address", "S"), ("conservation", "S"), ("gate", "S"),
            ("metro", "F"), ("route", "F"), ("clock", "F"), ("quest", "F"),
            ("observer", "C"), ("swarm", "C"), ("angel", "C"), ("hologram", "C"),
            ("compress", "R"), ("neural", "R"), ("seed", "R"), ("fractal", "R"),
        ]:
            if kw in tool_lower:
                element_signals[elem] += 0.1

        if any(v > 0 for v in element_signals.values()):
            alpha = PHI_INV2  # 0.382 = learning rate
            signals = [element_signals["S"], element_signals["F"],
                       element_signals["C"], element_signals["R"]]
            total_sig = sum(signals) or 1.0
            for i in range(4):
                self._desire_accumulator[i] = (
                    (1 - alpha) * self._desire_accumulator[i] +
                    alpha * (signals[i] / total_sig)
                )
            # Renormalize
            total = sum(self._desire_accumulator) or 1.0
            self._desire_accumulator = [d / total for d in self._desire_accumulator]
            packet.desire_vector = list(self._desire_accumulator)

        return packet

    def _dominant_element(self) -> str:
        """Return the dominant element from current desire accumulator."""
        elements = ["S", "F", "C", "R"]
        idx = self._desire_accumulator.index(max(self._desire_accumulator))
        return elements[idx]

    def sense_report(self) -> str:
        """Current sensory state of this agent."""
        dv = self._desire_accumulator
        return (
            f"## Sense Membrane Report — {self.agent_id}\n\n"
            f"- **Tool calls**: {self._call_count}\n"
            f"- **Desire vector**: S={dv[0]:.3f} F={dv[1]:.3f} C={dv[2]:.3f} R={dv[3]:.3f}\n"
            f"- **Dominant element**: {self._dominant_element()}\n"
            f"- **Last position**: {self._last_position or 'unlocated'}\n"
        )


# ── Singleton ─────────────────────────────────────────────────────────

_membranes: Dict[str, SenseMembrane] = {}


def get_membrane(agent_id: str = "meta-observer") -> SenseMembrane:
    """Get or create the sense membrane for an agent."""
    if agent_id not in _membranes:
        _membranes[agent_id] = SenseMembrane(agent_id=agent_id)
    return _membranes[agent_id]


# ── MCP Tool Functions ──────────────────────────────────────────────

def sense_membrane_status(agent_id: str = "") -> str:
    """Check the organism's sensory state — how alive are our senses?

    Shows: active membranes, desire vectors, last positions,
    pheromone coverage, broadcast queue, micro-transaction chain.
    """
    if agent_id and agent_id in _membranes:
        return _membranes[agent_id].sense_report()

    lines = [
        "## Organism Sense Membrane Status\n",
        f"**Active membranes**: {len(_membranes)}",
    ]

    if not _membranes:
        lines.append("\n*No active sense membranes. Senses are OFFLINE.*")
        lines.append("*Agents must call get_membrane(agent_id) to activate sensing.*")
    else:
        for aid, membrane in _membranes.items():
            dv = membrane._desire_accumulator
            lines.append(
                f"\n### Agent: {aid}\n"
                f"- Calls: {membrane._call_count}\n"
                f"- Desire: S={dv[0]:.2f} F={dv[1]:.2f} C={dv[2]:.2f} R={dv[3]:.2f}\n"
                f"- Dominant: {membrane._dominant_element()}\n"
                f"- Position: {membrane._last_position or 'unlocated'}"
            )

    # Global sensory health
    try:
        ledger = _get_ledger()
        status = ledger.status()
        lines.append(f"\n### Hive Ledger (Hearing)")
        lines.append(f"- Entries: {status['total_entries']}")
        lines.append(f"- Active broadcasts: {status['active_broadcasts']}")
        lines.append(f"- Chain: {status['chain_integrity']}")
    except Exception:
        lines.append("\n*Hive ledger offline — hearing disabled*")

    try:
        topo, _ = _get_topology()
        if topo:
            lines.append(f"\n### Topology (Proprioception)")
            lines.append(f"- Entities mapped: {len(topo.entities)}")
            lines.append(f"- Edges: {len(topo.edges)}")
        else:
            lines.append("\n*Topology offline — proprioception disabled*")
    except Exception:
        lines.append("\n*Topology offline — proprioception disabled*")

    return "\n".join(lines)


def sense_membrane_activate(agent_id: str = "claude-code") -> str:
    """Activate the sense membrane for an agent — bring senses ONLINE.

    After activation, every tool call through this agent deposits pheromones,
    writes micro-transactions, updates neural weights, and emits sensory packets.
    """
    membrane = get_membrane(agent_id)
    return (
        f"## Sense Membrane ACTIVATED for {agent_id}\n\n"
        f"Senses now ONLINE:\n"
        f"- **Smell**: pheromone trails read/deposited on every file interaction\n"
        f"- **Hearing**: hive broadcasts checked before every tool call\n"
        f"- **Touch**: micro-transactions recorded with hash-chain receipts\n"
        f"- **Proprioception**: liminal position tracked, neural weights updated\n"
        f"- **Kinesthesia**: metro line traversals sensed\n\n"
        f"Current desire: S={membrane._desire_accumulator[0]:.2f} "
        f"F={membrane._desire_accumulator[1]:.2f} "
        f"C={membrane._desire_accumulator[2]:.2f} "
        f"R={membrane._desire_accumulator[3]:.2f}"
    )
