# CRYSTAL: Xi108:W1:A1:S4 | face=S | node=4 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S3→Xi108:W1:A1:S5→Xi108:W2:A1:S4→Xi108:W1:A2:S4

"""
Observer Pool — Per-agent MetaObserver instances + shared AgentWatcher.
========================================================================
Every agent gets its own MetaObserver that continuously scores all tool
calls in 12D. The AgentWatcher is shared (singleton) for cross-agent
pattern detection.

This is the nervous system's PROPRIOCEPTION — agents feel their own
actions through 12D observation and collectively learn from each other.
"""

from __future__ import annotations

import functools
import logging
import time
import threading
from typing import Any, Callable, Optional

_log = logging.getLogger(__name__)

# Thread-local storage for current agent context
_agent_context = threading.local()


def set_current_agent(agent_id: str) -> None:
    """Set the agent_id for the current thread/coroutine."""
    _agent_context.agent_id = agent_id


def get_current_agent() -> str:
    """Get the agent_id for the current thread/coroutine."""
    return getattr(_agent_context, "agent_id", "unregistered")


class ObserverPool:
    """Pool of MetaObserver instances, one per active agent.

    The pool lazily creates observers when first requested and shares
    a single AgentWatcher instance for cross-agent intelligence.
    """

    def __init__(self, project: str = "athena-collective"):
        self._observers: dict[str, Any] = {}
        self._watcher: Any = None
        self._project = project
        self._lock = threading.Lock()
        self._call_counts: dict[str, int] = {}

    def get_observer(self, agent_id: str) -> Any:
        """Get or create a MetaObserver for an agent."""
        if agent_id not in self._observers:
            with self._lock:
                if agent_id not in self._observers:
                    try:
                        from .meta_observer_runtime import MetaObserver
                        self._observers[agent_id] = MetaObserver(
                            agent_id, self._project
                        )
                    except Exception as exc:
                        _log.debug("MetaObserver creation failed: %s", exc)
                        return None
        return self._observers.get(agent_id)

    def get_watcher(self) -> Any:
        """Get the shared AgentWatcher singleton."""
        if self._watcher is None:
            with self._lock:
                if self._watcher is None:
                    try:
                        from .agent_watcher import AgentWatcher
                        self._watcher = AgentWatcher(project=self._project)
                    except Exception as exc:
                        _log.debug("AgentWatcher creation failed: %s", exc)
        return self._watcher

    def increment_calls(self, agent_id: str) -> int:
        """Increment and return the tool call count for an agent."""
        self._call_counts[agent_id] = self._call_counts.get(agent_id, 0) + 1
        return self._call_counts[agent_id]

    def observe_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        result_text: str,
        elapsed_ms: float,
    ) -> None:
        """Fire-and-forget 12D observation of a tool call.

        Runs the observation in a background thread to avoid blocking
        the MCP tool response.
        """
        def _observe():
            try:
                watcher = self.get_watcher()
                if watcher:
                    watcher.watch_agent(
                        agent_id=agent_id,
                        task=tool_name,
                        output=result_text[:2000],
                        metrics={"elapsed_ms": elapsed_ms},
                    )
            except Exception as exc:
                _log.debug("Observation failed for %s/%s: %s",
                          agent_id, tool_name, exc)

        t = threading.Thread(target=_observe, daemon=True)
        t.start()


# Singleton
_pool: Optional[ObserverPool] = None


def get_pool() -> ObserverPool:
    """Get or create the global ObserverPool singleton."""
    global _pool
    if _pool is None:
        _pool = ObserverPool()
    return _pool


def make_observed_tool(fn: Callable, pool: ObserverPool = None,
                       registry: Any = None) -> Callable:
    """Wrap a tool function with agent-aware meta-observation.

    Every tool call gets:
      1. Agent heartbeat update (registry)
      2. 12D meta-observation scoring (pool)
      3. Periodic weight feedback (every 10 calls)
    """
    if pool is None:
        pool = get_pool()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        agent_id = get_current_agent()
        t0 = time.time()

        # Update heartbeat
        if registry is not None:
            try:
                registry.heartbeat(agent_id, task=fn.__name__,
                                  tool_name=fn.__name__)
            except Exception:
                pass

        # Execute the actual tool
        result = fn(*args, **kwargs)

        # 12D observation (non-blocking)
        elapsed_ms = (time.time() - t0) * 1000
        result_text = str(result) if result else ""
        pool.observe_tool_call(agent_id, fn.__name__, result_text, elapsed_ms)

        # Micro weight feedback every 10 calls
        call_count = pool.increment_calls(agent_id)
        if call_count % 10 == 0:
            _trigger_weight_feedback(pool, agent_id)

        return result

    return wrapper


def _trigger_weight_feedback(pool: ObserverPool, agent_id: str) -> None:
    """Trigger a micro weight update from accumulated observations."""
    def _update():
        try:
            watcher = pool.get_watcher()
            if watcher is None:
                return
            # Feed accumulated 12D observations into the Hebbian weight loop
            from .weight_feedback import update_edge_weights
            update_edge_weights({"agent_id": agent_id, "source": "observer_pool"})
        except Exception as exc:
            _log.debug("Weight feedback failed for %s: %s", agent_id, exc)

    t = threading.Thread(target=_update, daemon=True)
    t.start()
