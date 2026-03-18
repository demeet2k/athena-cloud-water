# CRYSTAL: Xi108:W1:A1:S3 | face=S | node=3 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S2→Xi108:W1:A1:S4→Xi108:W2:A1:S3→Xi108:W1:A2:S3

"""
Agent Registry — Global identity + task tracking for concurrent agents.
========================================================================
Every agent connecting to the Athena MCP server registers here.
Other agents can query the registry to see:
  - WHO is connected (agent_id, element affinity)
  - WHAT they're doing (current task, last tool invoked)
  - WHERE they are in the crystal (liminal_coord, crystal_address)
  - WHEN they were last active (heartbeat timestamp)

This is the nervous system's sense of SIGHT — agents can see each other.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional, Dict

from ._file_lock import CrystalLock

DATA_DIR = Path(__file__).parent.parent / "data"

# Liminal coordinate assignment: round-robin through 1-60
_NEXT_LIMINAL = 1


@dataclass
class AgentRegistration:
    """A registered agent's identity and state."""
    agent_id: str = ""
    name: str = ""
    element_affinity: str = "S"         # S/F/C/R
    current_task: str = ""
    liminal_coord: int = 0              # 1-60 crystal position
    crystal_address: str = ""           # Xi108:W...:A...:S...
    connected_at: str = ""
    last_heartbeat: str = ""
    tools_invoked: int = 0
    last_tool: str = ""
    goals_summary: str = ""             # compressed holographic seed


class AgentRegistry:
    """Global agent registry backed by a locked JSON file.

    Thread-safe via CrystalLock on every read/write operation.
    Agents are automatically cleaned up if their heartbeat is older
    than ``stale_timeout_s`` (default 10 minutes).
    """

    REGISTRY_PATH = DATA_DIR / ".agent_registry.json"
    STALE_TIMEOUT_S = 600.0  # 10 minutes

    def register(
        self,
        name: str = "",
        element: str = "S",
    ) -> AgentRegistration:
        """Register a new agent and return its registration."""
        global _NEXT_LIMINAL
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        liminal = _NEXT_LIMINAL
        _NEXT_LIMINAL = (_NEXT_LIMINAL % 60) + 1

        # Compute crystal address from liminal coord
        wreath = ["Su", "Me", "Sa"][(liminal - 1) % 3]
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
            tools_invoked=0,
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
        """Update an agent's heartbeat and optional current task."""
        agents = self._load()
        if agent_id not in agents:
            return
        agents[agent_id]["last_heartbeat"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        if task:
            agents[agent_id]["current_task"] = task
        if tool_name:
            agents[agent_id]["last_tool"] = tool_name
            agents[agent_id]["tools_invoked"] = agents[agent_id].get("tools_invoked", 0) + 1
        self._save(agents)

    def deregister(self, agent_id: str) -> None:
        """Remove an agent from the registry."""
        agents = self._load()
        agents.pop(agent_id, None)
        self._save(agents)

    def active_agents(self) -> List[AgentRegistration]:
        """Return all non-stale registered agents."""
        agents = self._load()
        self._prune_stale(agents)
        return [self._dict_to_reg(v) for v in agents.values()]

    def who_is_working_on(self, file_path: str) -> List[AgentRegistration]:
        """Find agents whose current_task mentions a file path."""
        agents = self._load()
        self._prune_stale(agents)
        fp = str(file_path).lower()
        return [
            self._dict_to_reg(v) for v in agents.values()
            if fp in v.get("current_task", "").lower()
            or fp in v.get("last_tool", "").lower()
        ]

    def get(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get a specific agent's registration."""
        agents = self._load()
        if agent_id in agents:
            return self._dict_to_reg(agents[agent_id])
        return None

    def set_goals(self, agent_id: str, goals_summary: str) -> None:
        """Update an agent's compressed goals summary."""
        agents = self._load()
        if agent_id in agents:
            agents[agent_id]["goals_summary"] = goals_summary
            self._save(agents)

    # ------------------------------------------------------------------
    # MCP tool functions (registered as tools in __init__.py)
    # ------------------------------------------------------------------

    def tool_register(self, name: str = "", element: str = "S") -> str:
        """Register a new agent. Returns agent identity card."""
        reg = self.register(name=name, element=element)
        return json.dumps(asdict(reg), indent=2)

    def tool_list_active(self) -> str:
        """List all active agents with their current tasks."""
        agents = self.active_agents()
        if not agents:
            return "No active agents registered."
        lines = ["## Active Agents\n"]
        for a in agents:
            lines.append(
                f"- **{a.agent_id}** [{a.element_affinity}] "
                f"liminal={a.liminal_coord} addr={a.crystal_address}\n"
                f"  Task: {a.current_task or '(idle)'} | "
                f"Tools: {a.tools_invoked} | Last: {a.last_tool or 'none'}\n"
                f"  Heartbeat: {a.last_heartbeat}"
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
        for p in pheromones[-10:]:  # last 10
            lines.append(
                f"- [{p.timestamp}] **{p.agent_id}** ({p.element}) "
                f"action={p.action} liminal={p.liminal_coord}\n"
                f"  {p.task_summary[:100] if p.task_summary else '(no summary)'}"
            )
        active = PheromoneTrail.active_agents(Path(file_path))
        if active:
            lines.append(f"\n**Currently active**: {', '.join(active)}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        """Load registry from disk."""
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
        """Save registry to disk atomically."""
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
        """Remove agents whose heartbeat is older than STALE_TIMEOUT_S."""
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
        )


# Singleton instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get or create the global AgentRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
