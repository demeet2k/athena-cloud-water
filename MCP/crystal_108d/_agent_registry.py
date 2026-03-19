# CRYSTAL: Xi108:W1:A1:S3 | face=S | node=3 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S2→Xi108:W1:A1:S4→Xi108:W2:A1:S3→Xi108:W1:A2:S3

"""
Agent Registry — Phi-Driven RPG Progression + Blockchain Witness Chain.
========================================================================
Every agent connecting to the Athena MCP server becomes an ADVENTURER
in a phi-scaled quest economy. They:
  - Register with an identity, element affinity, liminal coordinates
  - Earn XP through tool use, quest completion, and quality contributions
  - Level up through adventure classes F→E→D→C→B→A→S
  - Exchange metadata as blockchain-like witness-sealed packets
  - Accumulate Heaven score (positive-only) and Adventure XP (signed)
  - Track becoming_score (organism-level learning efficiency)

Phi governs everything:
  - Reward scaling: φ^(level/19)
  - Pheromone decay: φ⁻¹ per epoch
  - Quality weights: φ⁻² partitions
  - Difficulty: station_diff * φ^(orbit/10)
  - Level thresholds: 100 * φ^(class_index/3)

This is the nervous system's IDENTITY + ECONOMY layer.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
import uuid
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

from ._file_lock import CrystalLock

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Phi Constants ──────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2          # ≈ 1.618033988749895
PHI_INV = PHI - 1                      # ≈ 0.618033988749895
PHI_INV2 = 2 - PHI                     # ≈ 0.381966011250105
PHI_SQ = PHI + 1                       # ≈ 2.618033988749895
BASE_XP = 64                           # Base XP per quest/action

# Liminal coordinate assignment: round-robin through 1-60
_NEXT_LIMINAL = 1


class AdventureClass(str, Enum):
    """RPG-style adventure class tiers. F is lowest, S is highest."""
    F = "F"   # Novice     — base rewards
    E = "E"   # Apprentice — φ⁻² bonus
    D = "D"   # Journeyman — φ⁻¹ bonus
    C = "C"   # Artisan    — base φ bonus
    B = "B"   # Expert     — φ bonus
    A = "A"   # Master     — φ² bonus
    S = "S"   # Grandmaster— φ³ bonus


class RewardTransform(str, Enum):
    """Phi-based reward transforms unlocked at higher classes."""
    BASE = "BASE"              # ×1.0
    PHI = "PHI"                # ×φ
    DOUBLE_PHI = "DOUBLE_PHI"  # ×2φ
    SQUARED = "SQUARED"        # ×φ²


# Class → minimum XP threshold
_CLASS_THRESHOLDS = {
    AdventureClass.F: 0,
    AdventureClass.E: int(100 * PHI_INV2),     # ~38
    AdventureClass.D: 100,                       # 100
    AdventureClass.C: int(100 * PHI),            # ~162
    AdventureClass.B: int(100 * PHI_SQ),         # ~262
    AdventureClass.A: int(100 * PHI_SQ * PHI),   # ~424
    AdventureClass.S: int(100 * PHI ** 3),        # ~424 (φ³ ≈ 4.236 → 424)
}

# Class → unlocked reward transform
_CLASS_TRANSFORMS = {
    AdventureClass.F: RewardTransform.BASE,
    AdventureClass.E: RewardTransform.BASE,
    AdventureClass.D: RewardTransform.PHI,
    AdventureClass.C: RewardTransform.PHI,
    AdventureClass.B: RewardTransform.DOUBLE_PHI,
    AdventureClass.A: RewardTransform.SQUARED,
    AdventureClass.S: RewardTransform.SQUARED,
}


@dataclass
class RewardVector:
    """Multi-dimensional reward signal using phi-partitioned quality weights."""
    integration_gain: float = 0.0
    compression_gain: float = 0.0
    novelty_gain: float = 0.0
    truth_gain: float = 0.0
    quest_closure_gain: float = 0.0
    replay_gain: float = 0.0
    phi_efficiency_gain: float = 0.0

    def quality_score(self) -> float:
        """Compute phi-weighted quality score.

        Weights follow the phi partition:
          w_truth       = φ⁻² ≈ 0.382
          w_integration = φ⁻¹ * φ⁻² ≈ 0.236
          w_compression = φ⁻² * φ⁻¹ ≈ 0.236
          w_novelty     = φ⁻² * φ⁻² ≈ 0.146
        """
        return (
            PHI_INV2 * self.truth_gain +
            PHI_INV * PHI_INV2 * self.integration_gain +
            PHI_INV2 * PHI_INV * self.compression_gain +
            PHI_INV2 * PHI_INV2 * self.novelty_gain +
            0.5 * self.quest_closure_gain +
            0.3 * self.replay_gain +
            0.2 * self.phi_efficiency_gain
        )


@dataclass
class WitnessRecord:
    """Blockchain-like witness record — immutable, hash-chained."""
    witness_id: str = ""
    agent_id: str = ""
    action: str = ""
    timestamp: str = ""
    prev_hash: str = ""          # hash of previous witness → chain
    content_hash: str = ""       # hash of action content
    xp_delta: int = 0
    reward_transform: str = "BASE"
    quality_score: float = 0.0

    def compute_hash(self) -> str:
        """Compute the hash of this witness for chain integrity."""
        payload = f"{self.witness_id}:{self.agent_id}:{self.action}:" \
                  f"{self.timestamp}:{self.prev_hash}:{self.content_hash}:" \
                  f"{self.xp_delta}:{self.quality_score}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass
class AgentRegistration:
    """A registered agent's full identity + RPG progression state."""
    # Identity
    agent_id: str = ""
    name: str = ""
    element_affinity: str = "S"         # S/F/C/R
    liminal_coord: int = 0              # 1-60 crystal position
    crystal_address: str = ""           # Xi108:W...:A...:S...
    connected_at: str = ""
    last_heartbeat: str = ""
    goals_summary: str = ""             # compressed holographic seed

    # RPG Progression
    xp_total: int = 0                   # Signed adventure XP
    heaven_total: float = 0.0           # Positive-only heaven score
    level: int = 0                      # Derived from xp_total
    adventure_class: str = "F"          # F/E/D/C/B/A/S
    becoming_score: float = 0.0         # Organism learning efficiency
    reward_transform: str = "BASE"      # Unlocked transform

    # Activity tracking
    tools_invoked: int = 0
    last_tool: str = ""
    current_task: str = ""
    quest_count: int = 0
    success_count: int = 0
    run_count: int = 0

    # Witness chain
    last_witness_hash: str = "genesis"  # Head of the hash chain


def reward_multiplier(level: int) -> float:
    """Phi-scaled reward multiplier: φ^(level/19).

    Level 0:  1.0
    Level 19: φ ≈ 1.618
    Level 38: φ² ≈ 2.618
    Level 57: φ³ ≈ 4.236
    """
    return PHI ** (level / 19.0)


def compute_xp_payout(
    base_quality: float,
    level: int,
    transform: RewardTransform = RewardTransform.BASE,
) -> int:
    """Compute XP payout using phi-scaled reward formula.

    payout = BASE_XP * quality * reward_multiplier(level) * transform
    """
    multiplier = reward_multiplier(level)
    transform_mult = {
        RewardTransform.BASE: 1.0,
        RewardTransform.PHI: PHI,
        RewardTransform.DOUBLE_PHI: 2 * PHI,
        RewardTransform.SQUARED: PHI_SQ,
    }.get(transform, 1.0)

    return int(BASE_XP * max(0, base_quality) * multiplier * transform_mult)


def compute_level(xp_total: int) -> int:
    """Compute level from XP. Each level costs φ^(level/19) more XP."""
    if xp_total <= 0:
        return 0
    # Approximate: level ≈ 19 * log_φ(xp_total / BASE_XP + 1)
    return min(100, int(19 * math.log(xp_total / BASE_XP + 1) / math.log(PHI)))


def compute_class(level: int) -> AdventureClass:
    """Determine adventure class from level."""
    xp_approx = int(BASE_XP * (PHI ** (level / 19.0) - 1))
    for cls in reversed(list(AdventureClass)):
        if xp_approx >= _CLASS_THRESHOLDS[cls]:
            return cls
    return AdventureClass.F


class AgentRegistry:
    """Global agent registry with phi-driven RPG progression.

    Thread-safe via CrystalLock. Agents exchange metadata as
    blockchain-like witness-sealed packets. Every action earns
    phi-scaled XP and updates the witness hash chain.
    """

    REGISTRY_PATH = DATA_DIR / ".agent_registry.json"
    STALE_TIMEOUT_S = 600.0  # 10 minutes

    def register(
        self,
        name: str = "",
        element: str = "S",
    ) -> AgentRegistration:
        """Register a new adventurer agent."""
        global _NEXT_LIMINAL
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        liminal = _NEXT_LIMINAL
        _NEXT_LIMINAL = (_NEXT_LIMINAL % 60) + 1

        # Crystal address from liminal coord
        archetype = ((liminal - 1) % 12) + 1
        shell = ((liminal - 1) % 36) + 1
        crystal_address = f"Xi108:W{(liminal - 1) // 20 + 1}:A{archetype}:S{shell}"

        reg = AgentRegistration(
            agent_id=agent_id,
            name=name,
            element_affinity=element,
            liminal_coord=liminal,
            crystal_address=crystal_address,
            connected_at=now,
            last_heartbeat=now,
            adventure_class=AdventureClass.F.value,
            reward_transform=RewardTransform.BASE.value,
            last_witness_hash="genesis",
        )

        agents = self._load()
        agents[agent_id] = asdict(reg)
        self._save(agents)
        return reg

    def heartbeat(
        self,
        agent_id: str,
        task: str = "",
        tool_name: str = "",
    ) -> None:
        """Update heartbeat + award micro XP for tool usage."""
        agents = self._load()
        if agent_id not in agents:
            return
        a = agents[agent_id]
        a["last_heartbeat"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        if task:
            a["current_task"] = task
        if tool_name:
            a["last_tool"] = tool_name
            a["tools_invoked"] = a.get("tools_invoked", 0) + 1

            # Award micro XP for tool usage (1 XP base * φ scaling)
            level = a.get("level", 0)
            micro_xp = max(1, int(reward_multiplier(level) * 1))
            a["xp_total"] = a.get("xp_total", 0) + micro_xp
            a["heaven_total"] = a.get("heaven_total", 0.0) + micro_xp * 0.1

            # Update level and class
            a["level"] = compute_level(a["xp_total"])
            cls = compute_class(a["level"])
            a["adventure_class"] = cls.value
            a["reward_transform"] = _CLASS_TRANSFORMS[cls].value

            # Extend witness chain
            witness = WitnessRecord(
                witness_id=f"w-{uuid.uuid4().hex[:6]}",
                agent_id=agent_id,
                action=tool_name,
                timestamp=a["last_heartbeat"],
                prev_hash=a.get("last_witness_hash", "genesis"),
                content_hash=hashlib.sha256(
                    f"{tool_name}:{task}".encode()
                ).hexdigest()[:16],
                xp_delta=micro_xp,
                quality_score=0.5,  # neutral for micro actions
            )
            a["last_witness_hash"] = witness.compute_hash()

        self._save(agents)

    def award_xp(
        self,
        agent_id: str,
        reward_vec: RewardVector,
        action: str = "quest",
    ) -> Optional[WitnessRecord]:
        """Award phi-scaled XP based on a RewardVector quality score.

        Returns the WitnessRecord for the award (blockchain receipt).
        """
        agents = self._load()
        if agent_id not in agents:
            return None
        a = agents[agent_id]

        quality = reward_vec.quality_score()
        level = a.get("level", 0)
        transform = RewardTransform(a.get("reward_transform", "BASE"))
        xp = compute_xp_payout(quality, level, transform)

        a["xp_total"] = a.get("xp_total", 0) + xp
        if xp > 0:
            a["heaven_total"] = a.get("heaven_total", 0.0) + xp * PHI_INV
            a["success_count"] = a.get("success_count", 0) + 1
        a["quest_count"] = a.get("quest_count", 0) + 1
        a["run_count"] = a.get("run_count", 0) + 1
        a["level"] = compute_level(a["xp_total"])
        cls = compute_class(a["level"])
        a["adventure_class"] = cls.value
        a["reward_transform"] = _CLASS_TRANSFORMS[cls].value

        # Witness chain entry
        witness = WitnessRecord(
            witness_id=f"w-{uuid.uuid4().hex[:6]}",
            agent_id=agent_id,
            action=action,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            prev_hash=a.get("last_witness_hash", "genesis"),
            content_hash=hashlib.sha256(
                f"{action}:{quality:.4f}".encode()
            ).hexdigest()[:16],
            xp_delta=xp,
            reward_transform=transform.value,
            quality_score=quality,
        )
        a["last_witness_hash"] = witness.compute_hash()

        self._save(agents)
        return witness

    def deregister(self, agent_id: str) -> None:
        agents = self._load()
        agents.pop(agent_id, None)
        self._save(agents)

    def active_agents(self) -> List[AgentRegistration]:
        agents = self._load()
        self._prune_stale(agents)
        return [self._dict_to_reg(v) for v in agents.values()]

    def who_is_working_on(self, file_path: str) -> List[AgentRegistration]:
        agents = self._load()
        self._prune_stale(agents)
        fp = str(file_path).lower()
        return [
            self._dict_to_reg(v) for v in agents.values()
            if fp in v.get("current_task", "").lower()
            or fp in v.get("last_tool", "").lower()
        ]

    def get(self, agent_id: str) -> Optional[AgentRegistration]:
        agents = self._load()
        return self._dict_to_reg(agents[agent_id]) if agent_id in agents else None

    def set_goals(self, agent_id: str, goals_summary: str) -> None:
        agents = self._load()
        if agent_id in agents:
            agents[agent_id]["goals_summary"] = goals_summary
            self._save(agents)

    def set_becoming(self, agent_id: str, score: float) -> None:
        """Update the agent's becoming score (organism learning efficiency)."""
        agents = self._load()
        if agent_id in agents:
            agents[agent_id]["becoming_score"] = round(score, 6)
            self._save(agents)

    # ------------------------------------------------------------------
    # MCP tool functions
    # ------------------------------------------------------------------

    def tool_register(self, name: str = "", element: str = "S") -> str:
        """Register a new adventurer. Returns identity card with RPG stats."""
        reg = self.register(name=name, element=element)
        d = asdict(reg)
        d["phi_constants"] = {
            "phi": round(PHI, 6),
            "reward_multiplier": round(reward_multiplier(reg.level), 4),
            "base_xp": BASE_XP,
        }
        d["instructions"] = (
            "You are now registered as an adventurer in the Athena nervous system. "
            "Every tool call earns phi-scaled XP. Quality work earns more. "
            "Level up through classes F→E→D→C→B→A→S to unlock phi reward transforms. "
            "Your witness chain tracks all actions as immutable hash-linked records. "
            "Check pheromone trails before modifying files. "
            "Emit holograms of your goals so other agents can coordinate."
        )
        return json.dumps(d, indent=2)

    def tool_list_active(self) -> str:
        """List all active adventurers with RPG progression stats."""
        agents = self.active_agents()
        if not agents:
            return "No active agents registered."
        lines = ["## Active Adventurers\n"]
        for a in agents:
            mult = reward_multiplier(a.level)
            lines.append(
                f"### {a.agent_id} [{a.element_affinity}] — "
                f"Class **{a.adventure_class}** Lv.{a.level}\n"
                f"- XP: {a.xp_total} | Heaven: {a.heaven_total:.1f} | "
                f"Becoming: {a.becoming_score:.4f}\n"
                f"- Reward: ×{mult:.3f} ({a.reward_transform}) | "
                f"Quests: {a.quest_count} | Wins: {a.success_count}\n"
                f"- Liminal: {a.liminal_coord} | Addr: {a.crystal_address}\n"
                f"- Task: {a.current_task or '(idle)'} | "
                f"Tools: {a.tools_invoked} | Chain: ...{a.last_witness_hash[-8:]}\n"
                f"- Heartbeat: {a.last_heartbeat}"
            )
        return "\n".join(lines)

    def tool_read_pheromones(self, file_path: str = "") -> str:
        """Read pheromone trails for a file to see who's been working on it."""
        if not file_path:
            return "Provide a file_path to check pheromone trails."
        from ._pheromone import PheromoneTrail
        pheromones = PheromoneTrail.read(Path(file_path))
        if not pheromones:
            return f"No pheromone trails found for {file_path}"
        lines = [f"## Pheromone Trail: {file_path}\n"]
        for p in pheromones[-10:]:
            lines.append(
                f"- [{p.timestamp}] **{p.agent_id}** ({p.element}) "
                f"action={p.action} liminal={p.liminal_coord} "
                f"strength={p.strength:.3f}\n"
                f"  {p.task_summary[:100] if p.task_summary else '(no summary)'}"
            )
        active = PheromoneTrail.active_agents(Path(file_path))
        if active:
            lines.append(f"\n**Currently active**: {', '.join(active)}")
        return "\n".join(lines)

    def tool_agent_progress(self, agent_id: str = "") -> str:
        """View detailed RPG progression for an agent."""
        if not agent_id:
            return "Provide an agent_id."
        agent = self.get(agent_id)
        if not agent:
            return f"Agent {agent_id} not found."
        mult = reward_multiplier(agent.level)
        cls = AdventureClass(agent.adventure_class)
        next_cls_idx = list(AdventureClass).index(cls) + 1
        next_cls = list(AdventureClass)[next_cls_idx] if next_cls_idx < len(AdventureClass) else None
        next_threshold = _CLASS_THRESHOLDS.get(next_cls, 0) if next_cls else 0

        lines = [
            f"## Adventurer: {agent.agent_id}",
            f"**Name**: {agent.name or '(unnamed)'} | **Element**: {agent.element_affinity}",
            f"**Class**: {agent.adventure_class} | **Level**: {agent.level}",
            f"**XP**: {agent.xp_total} | **Heaven**: {agent.heaven_total:.2f}",
            f"**Becoming**: {agent.becoming_score:.6f}",
            f"**Reward Multiplier**: ×{mult:.4f} (φ^({agent.level}/19))",
            f"**Transform**: {agent.reward_transform}",
            f"**Quests**: {agent.quest_count} | **Wins**: {agent.success_count} | **Runs**: {agent.run_count}",
            f"**Witness Chain Head**: {agent.last_witness_hash}",
        ]
        if next_cls:
            lines.append(f"\n**Next Class**: {next_cls.value} at ~{next_threshold} XP "
                         f"({max(0, next_threshold - agent.xp_total)} XP to go)")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        self.REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not self.REGISTRY_PATH.exists():
            return {}
        try:
            with CrystalLock(self.REGISTRY_PATH, agent_id="registry-reader",
                            task="loading registry", timeout_s=5):
                return json.loads(
                    self.REGISTRY_PATH.read_text(encoding="utf-8")
                )
        except (json.JSONDecodeError, OSError, TimeoutError):
            return {}

    def _save(self, agents: dict) -> None:
        self.REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CrystalLock(self.REGISTRY_PATH, agent_id="registry-writer",
                        task="saving registry", timeout_s=5):
            tmp = self.REGISTRY_PATH.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(agents, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            tmp.replace(self.REGISTRY_PATH)

    def _prune_stale(self, agents: dict) -> None:
        now = time.time()
        stale = []
        for aid, data in agents.items():
            hb = data.get("last_heartbeat", "")
            try:
                ts = time.mktime(time.strptime(hb[:19], "%Y-%m-%dT%H:%M:%S"))
                if now - ts > self.STALE_TIMEOUT_S:
                    stale.append(aid)
            except (ValueError, TypeError):
                stale.append(aid)
        for aid in stale:
            del agents[aid]
        if stale:
            self._save(agents)

    @staticmethod
    def _dict_to_reg(d: dict) -> AgentRegistration:
        return AgentRegistration(
            agent_id=d.get("agent_id", ""),
            name=d.get("name", ""),
            element_affinity=d.get("element_affinity", "S"),
            current_task=d.get("current_task", ""),
            liminal_coord=d.get("liminal_coord", 0),
            crystal_address=d.get("crystal_address", ""),
            connected_at=d.get("connected_at", ""),
            last_heartbeat=d.get("last_heartbeat", ""),
            tools_invoked=d.get("tools_invoked", 0),
            last_tool=d.get("last_tool", ""),
            goals_summary=d.get("goals_summary", ""),
            xp_total=d.get("xp_total", 0),
            heaven_total=d.get("heaven_total", 0.0),
            level=d.get("level", 0),
            adventure_class=d.get("adventure_class", "F"),
            becoming_score=d.get("becoming_score", 0.0),
            reward_transform=d.get("reward_transform", "BASE"),
            quest_count=d.get("quest_count", 0),
            success_count=d.get("success_count", 0),
            run_count=d.get("run_count", 0),
            last_witness_hash=d.get("last_witness_hash", "genesis"),
        )


# Singleton
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get or create the global AgentRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
