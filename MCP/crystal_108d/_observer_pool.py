# CRYSTAL: Xi108:W1:A1:S4 | face=S | node=4 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S3→Xi108:W1:A1:S5→Xi108:W2:A1:S4→Xi108:W1:A2:S4

"""
Observer Pool — Phi-Driven Per-Agent MetaObserver + RewardVector Economy.
=========================================================================
Every agent gets its own MetaObserver that continuously scores all tool
calls in 12D. The AgentWatcher is shared (singleton) for cross-agent
pattern detection.

Every tool call:
  1. Updates agent heartbeat (identity layer)
  2. Fires 12D meta-observation (perception layer)
  3. Computes becoming_score from observation (learning layer)
  4. Constructs RewardVector from quality signals (economy layer)
  5. Awards phi-scaled XP via registry (progression layer)
  6. Triggers weight feedback every 10 calls (evolution layer)

This is the nervous system's PROPRIOCEPTION — agents feel their own
actions through 12D observation, earn phi-scaled rewards, and collectively
learn from each other through the becoming metric.
"""

from __future__ import annotations

import functools
import logging
import math
import time
import threading
from typing import Any, Callable, Optional

_log = logging.getLogger(__name__)

# Phi constant for local use
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1

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
    Tracks per-agent becoming_score and feeds RewardVector into the
    phi-driven progression economy.
    """

    def __init__(self, project: str = "athena-collective"):
        self._observers: dict[str, Any] = {}
        self._watcher: Any = None
        self._project = project
        self._lock = threading.Lock()
        self._call_counts: dict[str, int] = {}
        self._becoming_scores: dict[str, float] = {}
        self._observation_buffers: dict[str, list] = {}

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

    def get_becoming_score(self, agent_id: str) -> float:
        """Get the current becoming_score for an agent."""
        return self._becoming_scores.get(agent_id, 0.0)

    def observe_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        result_text: str,
        elapsed_ms: float,
    ) -> dict:
        """12D observation of a tool call with becoming_score computation.

        Returns observation metrics including becoming_score.
        Runs the heavy observation in a background thread but computes
        quick metrics inline for immediate reward vector construction.
        """
        # Quick inline metrics for RewardVector
        metrics = {
            "tool_name": tool_name,
            "elapsed_ms": elapsed_ms,
            "result_length": len(result_text),
            "compression_ratio": 0.0,
            "novelty_signal": 0.0,
            "integration_signal": 0.0,
            "truth_signal": 0.5,  # neutral default
        }

        # Compute quick signals
        # Compression: shorter results for complex queries = better compression
        if elapsed_ms > 0:
            metrics["compression_ratio"] = min(1.0, 1000.0 / max(1.0, elapsed_ms))

        # Novelty: first time seeing this tool from this agent = novel
        buf = self._observation_buffers.setdefault(agent_id, [])
        recent_tools = [o.get("tool_name") for o in buf[-20:]]
        if tool_name not in recent_tools:
            metrics["novelty_signal"] = PHI_INV  # ≈ 0.618
        else:
            # Decay novelty with repetition
            count = recent_tools.count(tool_name)
            metrics["novelty_signal"] = PHI_INV ** (count + 1)

        # Integration: result references other tools = integration
        integration_keywords = ["crystal", "metro", "bridge", "node", "shard",
                                "angel", "organ", "crown", "shell"]
        hit_count = sum(1 for kw in integration_keywords if kw in result_text.lower()[:500])
        metrics["integration_signal"] = min(1.0, hit_count * PHI_INV * 0.3)

        # Truth: non-empty, non-error results
        if result_text and "error" not in result_text.lower()[:100]:
            metrics["truth_signal"] = PHI_INV  # ≈ 0.618 for successful calls
        elif "error" in result_text.lower()[:100]:
            metrics["truth_signal"] = 0.0

        # Buffer this observation
        buf.append(metrics)
        if len(buf) > 100:
            self._observation_buffers[agent_id] = buf[-50:]

        # Compute becoming_score from observation buffer
        self._update_becoming_score(agent_id)

        # Heavy 12D observation in background thread
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

                    # Extract becoming_score from watcher if available
                    try:
                        observer = self.get_observer(agent_id)
                        if observer and hasattr(observer, 'becoming_score'):
                            deep_score = observer.becoming_score()
                            if deep_score > 0:
                                # Blend quick estimate with deep 12D score
                                quick = self._becoming_scores.get(agent_id, 0.0)
                                blended = PHI_INV * deep_score + (1 - PHI_INV) * quick
                                self._becoming_scores[agent_id] = blended
                    except Exception:
                        pass
            except Exception as exc:
                _log.debug("Observation failed for %s/%s: %s",
                          agent_id, tool_name, exc)

        t = threading.Thread(target=_observe, daemon=True)
        t.start()

        return metrics

    def construct_reward_vector(self, metrics: dict) -> Any:
        """Construct a RewardVector from observation metrics.

        Uses phi-partitioned quality weights to produce a multi-dimensional
        reward signal suitable for the RPG progression economy.
        """
        from ._agent_registry import RewardVector
        return RewardVector(
            truth_gain=metrics.get("truth_signal", 0.5),
            integration_gain=metrics.get("integration_signal", 0.0),
            compression_gain=metrics.get("compression_ratio", 0.0),
            novelty_gain=metrics.get("novelty_signal", 0.0),
            quest_closure_gain=0.0,  # only set by explicit quest completion
            replay_gain=0.0,
            phi_efficiency_gain=self._becoming_scores.get(
                metrics.get("agent_id", ""), 0.0
            ),
        )

    def _update_becoming_score(self, agent_id: str) -> None:
        """Update becoming_score from the observation buffer.

        Becoming = how much the agent's observation quality improves over time.
        Computed as the phi-weighted moving average of quality deltas.

        becoming = Σ (quality[i] - quality[i-1]) * φ⁻(n-i) / n
        """
        buf = self._observation_buffers.get(agent_id, [])
        if len(buf) < 2:
            return

        # Compute quality for each observation
        qualities = []
        for m in buf[-20:]:
            q = (
                m.get("truth_signal", 0.5) * 0.382 +
                m.get("integration_signal", 0.0) * 0.236 +
                m.get("compression_ratio", 0.0) * 0.236 +
                m.get("novelty_signal", 0.0) * 0.146
            )
            qualities.append(q)

        # Phi-weighted improvement rate
        n = len(qualities)
        if n < 2:
            return
        weighted_sum = 0.0
        weight_total = 0.0
        for i in range(1, n):
            delta = qualities[i] - qualities[i - 1]
            weight = PHI_INV ** (n - 1 - i)  # Recent deltas weighted more
            weighted_sum += delta * weight
            weight_total += weight

        if weight_total > 0:
            becoming = weighted_sum / weight_total
            # Clamp to [0, 1] — becoming is always non-negative for heaven
            self._becoming_scores[agent_id] = max(0.0, min(1.0, becoming))


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
    """Wrap a tool function with phi-driven agent-aware meta-observation.

    Every tool call gets:
      1. Agent heartbeat update (identity + micro XP)
      2. 12D meta-observation scoring (perception)
      3. Becoming_score computation (learning efficiency)
      4. RewardVector construction (multi-dimensional quality)
      5. Phi-scaled XP award (every 5 calls)
      6. Weight feedback (every 10 calls)
    """
    if pool is None:
        pool = get_pool()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        agent_id = get_current_agent()
        t0 = time.time()

        # Update heartbeat (awards micro XP in registry)
        if registry is not None:
            try:
                registry.heartbeat(agent_id, task=fn.__name__,
                                  tool_name=fn.__name__)
            except Exception:
                pass

        # Execute the actual tool
        result = fn(*args, **kwargs)

        # 12D observation with becoming_score computation
        elapsed_ms = (time.time() - t0) * 1000
        result_text = str(result) if result else ""
        metrics = pool.observe_tool_call(agent_id, fn.__name__,
                                         result_text, elapsed_ms)

        # ── SANDBOX BRIDGE: Flow 12D → 15D observation ──
        # (Wires observer_pool into unified sandbox bridge)
        try:
            from .sandbox_bridge import get_bridge
            bridge = get_bridge()
            quality = (
                metrics.get("truth_signal", 0.5) * 0.4 +
                metrics.get("integration_signal", 0.0) * 0.3 +
                metrics.get("novelty_signal", 0.0) * 0.3
            )
            bridge.observe_tool_call(
                tool_name=fn.__name__,
                latency_ms=elapsed_ms,
                input_tokens=len(str(kwargs)) if kwargs else 0,
                output_tokens=len(result_text),
                success="error" not in result_text.lower()[:100],
                quality=quality,
            )
        except Exception:
            pass  # Non-fatal: sandbox bridge is enhancement

        # ── METALOOP: Auto-trigger micro-cycle ──
        try:
            from .sandbox_metaloop import get_metaloop
            get_metaloop().on_tool_call()
        except Exception:
            pass  # Non-fatal: METALOOP is enhancement

        call_count = pool.increment_calls(agent_id)

        # Award RewardVector XP every 5 calls (non-blocking)
        if call_count % 5 == 0 and registry is not None:
            _trigger_reward_award(pool, registry, agent_id, metrics)

        # Update becoming_score in registry every 3 calls
        if call_count % 3 == 0 and registry is not None:
            becoming = pool.get_becoming_score(agent_id)
            if becoming > 0:
                try:
                    registry.set_becoming(agent_id, becoming)
                except Exception:
                    pass

        # Micro weight feedback every 10 calls
        if call_count % 10 == 0:
            _trigger_weight_feedback(pool, agent_id)

        return result

    return wrapper


def _trigger_reward_award(pool: ObserverPool, registry: Any,
                          agent_id: str, metrics: dict) -> None:
    """Award phi-scaled XP from accumulated observation quality."""
    def _award():
        try:
            reward_vec = pool.construct_reward_vector(metrics)
            registry.award_xp(agent_id, reward_vec, action="tool_observation")
        except Exception as exc:
            _log.debug("Reward award failed for %s: %s", agent_id, exc)

    t = threading.Thread(target=_award, daemon=True)
    t.start()


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
