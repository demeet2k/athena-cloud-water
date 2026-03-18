"""
Meta-Telemetry — Universal Tool Instrumentation Standard
=========================================================
The missing nervous system layer: instruments ALL 81 tools with
persistent usage tracking, outcome logging, cross-tool dependency
detection, and self-improvement signals.

DESIGN: Every tool call flows through telemetry decorators that:
  1. Record WHAT was called, WHEN, with WHAT parameters
  2. Track SUCCESS/FAILURE rates per tool
  3. Detect PATTERNS in tool usage sequences
  4. Compute COUPLING between tools (which tools predict which)
  5. Measure HEALTH metrics (latency, error rate, staleness)
  6. Feed observations to the Meta-Observer for strategy evolution

This module is the implementation of the missing Phase C (12D Observation)
applied to the tool ecosystem itself.

USAGE:
    from meta_telemetry import Telemetry, instrument

    telemetry = Telemetry.instance()

    # Decorator approach:
    @instrument("query_shell")
    def query_shell(shell: int) -> str: ...

    # Manual approach:
    with telemetry.observe("query_brain_network", {"component": "all"}) as obs:
        result = do_query()
        obs.set_result(result, success=True)
"""

import json
import time
import hashlib
import threading
import sqlite3
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps
from contextlib import contextmanager


# ──────────────────────────────────────────────────────────────
#  Telemetry Event Model
# ──────────────────────────────────────────────────────────────

@dataclass
class ToolEvent:
    """A single tool invocation event."""
    event_id: str
    tool_name: str
    timestamp: str
    parameters: str          # JSON-encoded parameters
    duration_ms: float
    success: bool
    error: str = ""
    result_size: int = 0     # length of result string
    caller_context: str = "" # what called this tool (if known)
    session_id: str = ""     # group related calls
    sequence_position: int = 0  # position in call sequence


@dataclass
class ToolHealth:
    """Aggregated health metrics for a single tool."""
    tool_name: str
    total_calls: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    last_called: str = ""
    last_error: str = ""
    success_rate: float = 1.0
    staleness_hours: float = 0.0  # hours since last call
    # Usage pattern
    calls_last_hour: int = 0
    calls_last_day: int = 0
    # Parameter patterns
    most_common_params: str = "[]"  # JSON


@dataclass
class ToolCoupling:
    """Detected coupling between two tools."""
    tool_a: str
    tool_b: str
    co_occurrence_count: int = 0  # how often called in same session
    sequence_count: int = 0      # how often A precedes B
    avg_gap_ms: float = 0.0      # average time between A and B
    correlation: float = 0.0     # statistical correlation


# ──────────────────────────────────────────────────────────────
#  Resonance Monitor (from agency_gateway.json spec)
# ──────────────────────────────────────────────────────────────

class ResonanceMonitor:
    """
    Implements the 8-dimensional resonance score from the agency spec:
    R_k = [truth, coherence, novelty, compression, safety, utility, vitality, convergence]

    With diagnostic rules for anomaly detection.
    """

    DIMENSIONS = ["truth", "coherence", "novelty", "compression",
                  "safety", "utility", "vitality", "convergence"]

    DIAGNOSTIC_RULES = [
        {"condition": lambda r: r["novelty"] > 0.8 and r["coherence"] < 0.3,
         "risk": "hallucination", "action": "increase grounding checks"},
        {"condition": lambda r: r["coherence"] > 0.8 and r["novelty"] < 0.2,
         "risk": "stagnation", "action": "trigger mutation strategy"},
        {"condition": lambda r: r["compression"] > 0.9 and r["truth"] < 0.5,
         "risk": "over_compression", "action": "expand detail level"},
        {"condition": lambda r: r["vitality"] < 0.2,
         "risk": "system_fatigue", "action": "reduce workload or restart"},
        {"condition": lambda r: r["safety"] < 0.3,
         "risk": "boundary_violation", "action": "enforce corridor constraints"},
        {"condition": lambda r: r["convergence"] < 0.2 and r["utility"] > 0.7,
         "risk": "divergent_utility", "action": "anchor to core objective"},
    ]

    def compute(self, events: list[ToolEvent], health: dict[str, ToolHealth]) -> dict:
        """Compute current resonance vector from recent events and health."""
        if not events:
            return {d: 0.5 for d in self.DIMENSIONS}

        total = len(events)
        successes = sum(1 for e in events if e.success)
        unique_tools = len(set(e.tool_name for e in events))
        total_tools = 81  # known total

        scores = {
            # Truth: are tools returning valid results?
            "truth": successes / max(total, 1),

            # Coherence: are tools being used in consistent patterns?
            "coherence": self._compute_coherence(events),

            # Novelty: how many different tools being used?
            "novelty": min(1.0, unique_tools / max(total_tools * 0.3, 1)),

            # Compression: signal density (short calls with good results)
            "compression": self._compute_compression(events),

            # Safety: no errors, no violations
            "safety": 1.0 - (sum(1 for e in events if not e.success) / max(total, 1)),

            # Utility: are results being used? (proxy: result_size > 0)
            "utility": sum(1 for e in events if e.result_size > 100) / max(total, 1),

            # Vitality: system responsiveness (low latency)
            "vitality": self._compute_vitality(events),

            # Convergence: are we getting better over time?
            "convergence": self._compute_convergence(events),
        }

        return scores

    def diagnose(self, scores: dict) -> list[dict]:
        """Run diagnostic rules and return any triggered alerts."""
        alerts = []
        for rule in self.DIAGNOSTIC_RULES:
            try:
                if rule["condition"](scores):
                    alerts.append({
                        "risk": rule["risk"],
                        "action": rule["action"],
                        "scores": {k: round(v, 3) for k, v in scores.items()},
                    })
            except Exception:
                pass
        return alerts

    def _compute_coherence(self, events: list[ToolEvent]) -> float:
        """Measure consistency of tool usage patterns."""
        if len(events) < 3:
            return 0.5
        # Compute entropy of tool distribution — lower entropy = more coherent
        tool_counts = defaultdict(int)
        for e in events:
            tool_counts[e.tool_name] += 1
        total = sum(tool_counts.values())
        entropy = -sum(
            (c/total) * math.log2(c/total) for c in tool_counts.values()
        )
        max_entropy = math.log2(len(tool_counts))
        return 1.0 - (entropy / max(max_entropy, 1))

    def _compute_compression(self, events: list[ToolEvent]) -> float:
        """Signal density: useful results per unit time."""
        if not events:
            return 0.5
        useful = sum(1 for e in events if e.success and e.result_size > 50)
        total_time = sum(e.duration_ms for e in events)
        if total_time == 0:
            return 0.5
        return min(1.0, (useful * 1000) / total_time)

    def _compute_vitality(self, events: list[ToolEvent]) -> float:
        """System responsiveness — low latency = high vitality."""
        if not events:
            return 0.5
        durations = [e.duration_ms for e in events]
        avg = sum(durations) / len(durations)
        # < 100ms = 1.0, > 10s = 0.0
        return max(0.0, min(1.0, 1.0 - (avg - 100) / 10000))

    def _compute_convergence(self, events: list[ToolEvent]) -> float:
        """Are success rates improving over time?"""
        if len(events) < 10:
            return 0.5
        mid = len(events) // 2
        early = events[:mid]
        late = events[mid:]
        early_rate = sum(1 for e in early if e.success) / len(early)
        late_rate = sum(1 for e in late if e.success) / len(late)
        # Positive change = converging
        return min(1.0, max(0.0, 0.5 + (late_rate - early_rate)))


# ──────────────────────────────────────────────────────────────
#  Self-Healing Engine (from agency_gateway.json spec)
# ──────────────────────────────────────────────────────────────

class SelfHealingEngine:
    """
    Implements the 5 self-healing laws from the agency gateway spec:
    1. Missing Output Recovery
    2. Contradiction Recovery
    3. Noise Collapse
    4. Stagnation Break
    5. Ledger Integrity
    """

    def __init__(self, telemetry: 'Telemetry'):
        self.telemetry = telemetry
        self.healing_log: list[dict] = []

    def diagnose_and_heal(self, health: dict[str, ToolHealth],
                           resonance: dict, alerts: list[dict]) -> list[dict]:
        """Run all 5 healing laws and return actions taken."""
        actions = []

        # Law 1: Missing Output Recovery
        for name, h in health.items():
            if h.total_calls > 5 and h.success_rate < 0.5:
                actions.append({
                    "law": "missing_output_recovery",
                    "tool": name,
                    "action": f"Tool {name} failing {1-h.success_rate:.0%} of the time. "
                             f"Last error: {h.last_error}. Recommend: check JSON data integrity.",
                    "severity": "high",
                })

        # Law 2: Contradiction Recovery
        # Detect if tools return contradictory results (same query, different answers)
        # This requires query-level tracking — flag for future implementation
        if resonance.get("truth", 1) < 0.5 and resonance.get("coherence", 1) > 0.7:
            actions.append({
                "law": "contradiction_recovery",
                "action": "High coherence but low truth — consistent errors detected. "
                         "Recommend: validate JSON source data.",
                "severity": "critical",
            })

        # Law 3: Noise Collapse
        total_events = sum(h.total_calls for h in health.values())
        useful_events = sum(h.success_count for h in health.values())
        if total_events > 100 and useful_events / max(total_events, 1) < 0.3:
            actions.append({
                "law": "noise_collapse",
                "action": f"Signal-to-noise ratio critical: {useful_events}/{total_events} "
                         f"({useful_events/total_events:.0%}) useful. Throttle low-value queries.",
                "severity": "high",
            })

        # Law 4: Stagnation Break
        if resonance.get("convergence", 1) < 0.3 and resonance.get("novelty", 1) < 0.3:
            actions.append({
                "law": "stagnation_break",
                "action": "Low convergence + low novelty = stagnation. "
                         "Recommend: catalyst mutation — try new tool combinations.",
                "severity": "medium",
            })

        # Law 5: Ledger Integrity
        # Check if telemetry DB itself is healthy
        try:
            self.telemetry._check_db_integrity()
        except Exception as e:
            actions.append({
                "law": "ledger_integrity",
                "action": f"Telemetry database integrity issue: {e}. "
                         f"Recommend: snapshot + restore.",
                "severity": "critical",
            })

        # Log all healing actions
        for a in actions:
            a["timestamp"] = datetime.now(timezone.utc).isoformat()
            self.healing_log.append(a)

        return actions


# ──────────────────────────────────────────────────────────────
#  Core Telemetry Engine (Singleton)
# ──────────────────────────────────────────────────────────────

class Telemetry:
    """
    Universal telemetry collector for the entire MCP tool ecosystem.
    Thread-safe singleton that persists to SQLite.

    Makes every tool self-aware by tracking:
      - Call frequency, latency, success/failure
      - Parameter patterns (what queries are most common)
      - Tool coupling (which tools are used together)
      - Session-level sequences (tool call ordering)
      - Resonance scoring (8D health vector)
      - Self-healing diagnostics
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls, db_path: str = None) -> 'Telemetry':
        """Get or create the singleton telemetry instance."""
        with cls._lock:
            if cls._instance is None:
                if db_path is None:
                    db_path = str(
                        Path(__file__).parent.parent / "data" / "telemetry.db"
                    )
                cls._instance = cls(db_path)
            return cls._instance

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._session_id = hashlib.md5(
            f"{time.time()}:{id(self)}".encode()
        ).hexdigest()[:12]
        self._sequence_counter = 0
        self._recent_events: list[ToolEvent] = []
        self._max_recent = 500
        self.resonance = ResonanceMonitor()
        self.healer = SelfHealingEngine(self)

        # Initialize DB
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._db_lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._db_lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS tool_events (
                    event_id TEXT PRIMARY KEY,
                    tool_name TEXT,
                    timestamp TEXT,
                    parameters TEXT,
                    duration_ms REAL,
                    success INTEGER,
                    error TEXT,
                    result_size INTEGER,
                    caller_context TEXT,
                    session_id TEXT,
                    sequence_position INTEGER
                );

                CREATE TABLE IF NOT EXISTS tool_health (
                    tool_name TEXT PRIMARY KEY,
                    total_calls INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    avg_duration_ms REAL DEFAULT 0,
                    p95_duration_ms REAL DEFAULT 0,
                    last_called TEXT,
                    last_error TEXT,
                    success_rate REAL DEFAULT 1.0,
                    most_common_params TEXT DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS tool_coupling (
                    tool_a TEXT,
                    tool_b TEXT,
                    co_occurrence_count INTEGER DEFAULT 0,
                    sequence_count INTEGER DEFAULT 0,
                    avg_gap_ms REAL DEFAULT 0,
                    PRIMARY KEY (tool_a, tool_b)
                );

                CREATE TABLE IF NOT EXISTS resonance_log (
                    timestamp TEXT,
                    session_id TEXT,
                    truth REAL, coherence REAL, novelty REAL,
                    compression REAL, safety REAL, utility REAL,
                    vitality REAL, convergence REAL,
                    alerts TEXT
                );

                CREATE TABLE IF NOT EXISTS healing_log (
                    timestamp TEXT,
                    law TEXT,
                    tool TEXT,
                    action TEXT,
                    severity TEXT
                );

                CREATE TABLE IF NOT EXISTS improvement_insights (
                    insight_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    insight_type TEXT,
                    tool_name TEXT,
                    description TEXT,
                    evidence TEXT,
                    priority TEXT,
                    applied INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_events_tool ON tool_events(tool_name);
                CREATE INDEX IF NOT EXISTS idx_events_session ON tool_events(session_id);
                CREATE INDEX IF NOT EXISTS idx_events_ts ON tool_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_resonance_ts ON resonance_log(timestamp);
            """)
            self.conn.commit()

    # ──────────────────────────────────────────────────────
    #  Event Recording
    # ──────────────────────────────────────────────────────

    def record_event(self, event: ToolEvent):
        """Record a tool invocation event."""
        with self._db_lock:
            self.conn.execute("""
                INSERT OR REPLACE INTO tool_events VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                event.event_id, event.tool_name, event.timestamp,
                event.parameters, event.duration_ms, int(event.success),
                event.error, event.result_size, event.caller_context,
                event.session_id, event.sequence_position,
            ))
            self._update_health(event)
            self._update_coupling(event)
            self.conn.commit()

        # Keep in memory for resonance
        self._recent_events.append(event)
        if len(self._recent_events) > self._max_recent:
            self._recent_events = self._recent_events[-self._max_recent:]

    def _update_health(self, event: ToolEvent):
        """Update aggregated health for a tool."""
        row = self.conn.execute(
            "SELECT * FROM tool_health WHERE tool_name=?", (event.tool_name,)
        ).fetchone()

        if row:
            total = row["total_calls"] + 1
            successes = row["success_count"] + (1 if event.success else 0)
            failures = row["failure_count"] + (0 if event.success else 1)
            avg_dur = (row["avg_duration_ms"] * row["total_calls"] + event.duration_ms) / total
            self.conn.execute("""
                UPDATE tool_health SET
                    total_calls=?, success_count=?, failure_count=?,
                    avg_duration_ms=?, last_called=?,
                    last_error=CASE WHEN ? THEN last_error ELSE ? END,
                    success_rate=?
                WHERE tool_name=?
            """, (
                total, successes, failures, avg_dur,
                event.timestamp, int(event.success), event.error,
                successes / max(total, 1), event.tool_name,
            ))
        else:
            self.conn.execute("""
                INSERT INTO tool_health (tool_name, total_calls, success_count,
                    failure_count, avg_duration_ms, last_called, last_error, success_rate)
                VALUES (?, 1, ?, ?, ?, ?, ?, ?)
            """, (
                event.tool_name,
                1 if event.success else 0,
                0 if event.success else 1,
                event.duration_ms, event.timestamp,
                "" if event.success else event.error,
                1.0 if event.success else 0.0,
            ))

    def _update_coupling(self, event: ToolEvent):
        """Track tool-to-tool coupling from session sequences."""
        # Find recent events in same session
        session_events = [
            e for e in self._recent_events[-20:]
            if e.session_id == event.session_id and e.tool_name != event.tool_name
        ]

        for prev in session_events:
            tools = tuple(sorted([prev.tool_name, event.tool_name]))
            # Update co-occurrence
            row = self.conn.execute(
                "SELECT * FROM tool_coupling WHERE tool_a=? AND tool_b=?",
                tools
            ).fetchone()

            gap_ms = abs(
                datetime.fromisoformat(event.timestamp).timestamp() -
                datetime.fromisoformat(prev.timestamp).timestamp()
            ) * 1000

            if row:
                new_count = row["co_occurrence_count"] + 1
                new_gap = (row["avg_gap_ms"] * row["co_occurrence_count"] + gap_ms) / new_count
                seq = row["sequence_count"] + (1 if prev.tool_name == tools[0] else 0)
                self.conn.execute("""
                    UPDATE tool_coupling SET co_occurrence_count=?, sequence_count=?, avg_gap_ms=?
                    WHERE tool_a=? AND tool_b=?
                """, (new_count, seq, new_gap, *tools))
            else:
                self.conn.execute("""
                    INSERT INTO tool_coupling VALUES (?,?,1,?,?)
                """, (*tools, 1 if prev.tool_name == tools[0] else 0, gap_ms))

    # ──────────────────────────────────────────────────────
    #  Context Manager for Manual Instrumentation
    # ──────────────────────────────────────────────────────

    @contextmanager
    def observe(self, tool_name: str, parameters: dict = None,
                caller: str = ""):
        """
        Context manager for observing a tool call.

        Usage:
            with telemetry.observe("query_shell", {"shell": 5}) as obs:
                result = query_shell(5)
                obs.set_result(result, success=True)
        """
        self._sequence_counter += 1
        obs = _ObservationContext(
            tool_name=tool_name,
            parameters=parameters or {},
            session_id=self._session_id,
            sequence_position=self._sequence_counter,
            caller_context=caller,
        )
        try:
            yield obs
        except Exception as e:
            obs.set_result("", success=False, error=str(e))
            raise
        finally:
            event = obs.finalize()
            self.record_event(event)

    # ──────────────────────────────────────────────────────
    #  Health & Insights
    # ──────────────────────────────────────────────────────

    def get_health(self, tool_name: str = None) -> dict:
        """Get health metrics for one or all tools."""
        with self._db_lock:
            if tool_name:
                row = self.conn.execute(
                    "SELECT * FROM tool_health WHERE tool_name=?", (tool_name,)
                ).fetchone()
                return dict(row) if row else {}
            else:
                rows = self.conn.execute(
                    "SELECT * FROM tool_health ORDER BY total_calls DESC"
                ).fetchall()
                return {r["tool_name"]: dict(r) for r in rows}

    def get_couplings(self, min_count: int = 2) -> list[dict]:
        """Get detected tool couplings."""
        with self._db_lock:
            rows = self.conn.execute("""
                SELECT * FROM tool_coupling
                WHERE co_occurrence_count >= ?
                ORDER BY co_occurrence_count DESC
            """, (min_count,)).fetchall()
            return [dict(r) for r in rows]

    def compute_resonance(self) -> dict:
        """Compute current 8D resonance vector."""
        health = self.get_health()
        health_objects = {
            name: ToolHealth(tool_name=name, **{k: v for k, v in h.items() if k != 'tool_name'})
            for name, h in health.items()
        }
        scores = self.resonance.compute(self._recent_events, health_objects)
        alerts = self.resonance.diagnose(scores)

        # Log resonance
        with self._db_lock:
            self.conn.execute("""
                INSERT INTO resonance_log VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                datetime.now(timezone.utc).isoformat(), self._session_id,
                scores["truth"], scores["coherence"], scores["novelty"],
                scores["compression"], scores["safety"], scores["utility"],
                scores["vitality"], scores["convergence"],
                json.dumps(alerts),
            ))
            self.conn.commit()

        return {"scores": scores, "alerts": alerts}

    def run_self_healing(self) -> list[dict]:
        """Run self-healing diagnostics and return actions."""
        health = self.get_health()
        health_objects = {
            name: ToolHealth(tool_name=name, **{k: v for k, v in h.items() if k != 'tool_name'})
            for name, h in health.items()
        }
        resonance = self.resonance.compute(self._recent_events, health_objects)
        alerts = self.resonance.diagnose(resonance)

        actions = self.healer.diagnose_and_heal(health_objects, resonance, alerts)

        # Log healing actions
        with self._db_lock:
            for a in actions:
                self.conn.execute("""
                    INSERT INTO healing_log VALUES (?,?,?,?,?)
                """, (a["timestamp"], a["law"], a.get("tool", ""),
                      a["action"], a["severity"]))
            self.conn.commit()

        return actions

    def generate_improvement_insights(self) -> list[dict]:
        """
        Analyze all accumulated data and generate actionable improvement insights.
        This is the meta-observer's deepest function: looking at the tool ecosystem
        and finding where to improve.
        """
        insights = []
        health = self.get_health()
        couplings = self.get_couplings()

        # Insight 1: Most-failing tools
        for name, h in health.items():
            if h.get("total_calls", 0) > 3 and h.get("success_rate", 1) < 0.7:
                insights.append({
                    "type": "reliability",
                    "tool": name,
                    "description": f"{name} has {h['success_rate']:.0%} success rate "
                                  f"({h['failure_count']} failures). Check JSON data or parameter validation.",
                    "priority": "high",
                    "evidence": json.dumps(h),
                })

        # Insight 2: Slowest tools
        for name, h in health.items():
            if h.get("avg_duration_ms", 0) > 5000:
                insights.append({
                    "type": "performance",
                    "tool": name,
                    "description": f"{name} averages {h['avg_duration_ms']:.0f}ms. "
                                  f"Consider caching or indexing.",
                    "priority": "medium",
                    "evidence": json.dumps(h),
                })

        # Insight 3: Never-used tools (registered but not called)
        all_tools = set(h for h in health.keys())
        if len(all_tools) < 81:
            missing = 81 - len(all_tools)
            insights.append({
                "type": "coverage",
                "tool": "*",
                "description": f"{missing} tools have never been called. "
                              f"Consider: are they discoverable? Do agents know about them?",
                "priority": "low",
                "evidence": "",
            })

        # Insight 4: Strong couplings (tools always used together)
        for c in couplings[:5]:
            if c["co_occurrence_count"] > 10:
                insights.append({
                    "type": "coupling",
                    "tool": f"{c['tool_a']} + {c['tool_b']}",
                    "description": f"{c['tool_a']} and {c['tool_b']} co-occur "
                                  f"{c['co_occurrence_count']} times. Consider: merge, pipeline, or compound tool.",
                    "priority": "medium",
                    "evidence": json.dumps(c),
                })

        # Insight 5: Isolated tools (high use, no coupling)
        coupled_tools = set()
        for c in couplings:
            coupled_tools.add(c["tool_a"])
            coupled_tools.add(c["tool_b"])
        for name, h in health.items():
            if h.get("total_calls", 0) > 10 and name not in coupled_tools:
                insights.append({
                    "type": "isolation",
                    "tool": name,
                    "description": f"{name} called {h['total_calls']} times but never co-occurs "
                                  f"with other tools. It may be operating in a silo.",
                    "priority": "low",
                    "evidence": "",
                })

        # Store insights
        with self._db_lock:
            for ins in insights:
                iid = hashlib.md5(
                    f"{ins['type']}:{ins['tool']}:{time.time()}".encode()
                ).hexdigest()[:16]
                self.conn.execute("""
                    INSERT OR IGNORE INTO improvement_insights VALUES (?,?,?,?,?,?,?,0)
                """, (iid, datetime.now(timezone.utc).isoformat(),
                      ins["type"], ins.get("tool", ""), ins["description"],
                      ins.get("evidence", ""), ins["priority"]))
            self.conn.commit()

        return insights

    def full_report(self) -> dict:
        """
        Generate a comprehensive meta-observation report.
        This is the system observing itself.
        """
        health = self.get_health()
        couplings = self.get_couplings()
        resonance = self.compute_resonance()
        healing = self.run_self_healing()
        insights = self.generate_improvement_insights()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session": self._session_id,
            "total_events_recorded": sum(h.get("total_calls", 0) for h in health.values()),
            "tools_observed": len(health),
            "tools_total": 81,
            "coverage": f"{len(health)/81:.0%}",
            "health_summary": {
                name: {
                    "calls": h.get("total_calls", 0),
                    "success_rate": f"{h.get('success_rate', 1):.0%}",
                    "avg_ms": f"{h.get('avg_duration_ms', 0):.0f}",
                }
                for name, h in sorted(
                    health.items(), key=lambda x: x[1].get("total_calls", 0), reverse=True
                )[:10]
            },
            "resonance": resonance,
            "couplings_detected": len(couplings),
            "top_couplings": couplings[:5],
            "healing_actions": healing,
            "improvement_insights": insights,
        }

    def _check_db_integrity(self):
        """Verify database integrity."""
        with self._db_lock:
            result = self.conn.execute("PRAGMA integrity_check").fetchone()
            if result[0] != "ok":
                raise RuntimeError(f"DB integrity check failed: {result[0]}")


class _ObservationContext:
    """Internal context for observe() context manager."""

    def __init__(self, tool_name: str, parameters: dict,
                 session_id: str, sequence_position: int,
                 caller_context: str):
        self.tool_name = tool_name
        self.parameters = parameters
        self.session_id = session_id
        self.sequence_position = sequence_position
        self.caller_context = caller_context
        self._start = time.monotonic()
        self._success = True
        self._error = ""
        self._result_size = 0

    def set_result(self, result: Any, success: bool = True, error: str = ""):
        """Set the result of the observed operation."""
        self._success = success
        self._error = error
        if isinstance(result, str):
            self._result_size = len(result)
        elif result is not None:
            self._result_size = len(str(result))

    def finalize(self) -> ToolEvent:
        """Create the final event record."""
        duration = (time.monotonic() - self._start) * 1000
        return ToolEvent(
            event_id=hashlib.md5(
                f"{self.tool_name}:{self.session_id}:{self.sequence_position}:{time.time()}".encode()
            ).hexdigest()[:16],
            tool_name=self.tool_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            parameters=json.dumps(self.parameters, default=str)[:1000],
            duration_ms=duration,
            success=self._success,
            error=self._error,
            result_size=self._result_size,
            caller_context=self.caller_context,
            session_id=self.session_id,
            sequence_position=self.sequence_position,
        )


# ──────────────────────────────────────────────────────────────
#  Decorator for Automatic Instrumentation
# ──────────────────────────────────────────────────────────────

def instrument(tool_name: str = None):
    """
    Decorator that automatically instruments a tool function.

    Usage:
        @instrument("query_shell")
        def query_shell(shell: int = 1) -> str:
            ...

    Or without name (uses function name):
        @instrument()
        def query_shell(shell: int = 1) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        name = tool_name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = Telemetry.instance()
            start = time.monotonic()
            try:
                result = func(*args, **kwargs)
                duration = (time.monotonic() - start) * 1000
                event = ToolEvent(
                    event_id=hashlib.md5(
                        f"{name}:{time.time()}:{id(result)}".encode()
                    ).hexdigest()[:16],
                    tool_name=name,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    parameters=json.dumps(kwargs or {}, default=str)[:1000],
                    duration_ms=duration,
                    success=True,
                    result_size=len(result) if isinstance(result, str) else 0,
                    session_id=telemetry._session_id,
                    sequence_position=telemetry._sequence_counter,
                )
                telemetry._sequence_counter += 1
                telemetry.record_event(event)
                return result
            except Exception as e:
                duration = (time.monotonic() - start) * 1000
                event = ToolEvent(
                    event_id=hashlib.md5(
                        f"{name}:{time.time()}:err".encode()
                    ).hexdigest()[:16],
                    tool_name=name,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    parameters=json.dumps(kwargs or {}, default=str)[:1000],
                    duration_ms=duration,
                    success=False,
                    error=str(e)[:500],
                    session_id=telemetry._session_id,
                    sequence_position=telemetry._sequence_counter,
                )
                telemetry._sequence_counter += 1
                telemetry.record_event(event)
                raise

        return wrapper
    return decorator


# ──────────────────────────────────────────────────────────────
#  MCP Tool Interface — query_telemetry
# ──────────────────────────────────────────────────────────────

def query_telemetry(component: str = "report") -> str:
    """
    Query the meta-telemetry system — the meta-observer observing all tools.

    Components:
      - report      : Full self-observation report (health, resonance, healing, insights)
      - health      : Tool health metrics (success rates, latency, call counts)
      - resonance   : 8D resonance vector (truth, coherence, novelty, etc.)
      - couplings   : Detected tool-to-tool couplings
      - healing     : Self-healing diagnostics and actions
      - insights    : Improvement recommendations
      - events      : Recent tool events (last 20)
    """
    telemetry = Telemetry.instance()
    comp = component.strip().lower()

    if comp == "report":
        report = telemetry.full_report()
        return _format_report(report)
    elif comp == "health":
        health = telemetry.get_health()
        return _format_health(health)
    elif comp == "resonance":
        res = telemetry.compute_resonance()
        return _format_resonance(res)
    elif comp == "couplings":
        couplings = telemetry.get_couplings()
        return _format_couplings(couplings)
    elif comp == "healing":
        actions = telemetry.run_self_healing()
        return _format_healing(actions)
    elif comp == "insights":
        insights = telemetry.generate_improvement_insights()
        return _format_insights(insights)
    elif comp == "events":
        events = telemetry._recent_events[-20:]
        return _format_events(events)
    else:
        return (
            f"Unknown component '{component}'. Use: report, health, resonance, "
            "couplings, healing, insights, events"
        )


def _format_report(report: dict) -> str:
    lines = [
        "## Meta-Telemetry Full Report\n",
        f"**Timestamp**: {report['timestamp']}",
        f"**Session**: {report['session']}",
        f"**Events Recorded**: {report['total_events_recorded']}",
        f"**Tools Observed**: {report['tools_observed']} / {report['tools_total']} ({report['coverage']})",
        "",
        "### Top Tools by Usage",
    ]
    for name, h in report.get("health_summary", {}).items():
        lines.append(f"  - **{name}**: {h['calls']} calls, {h['success_rate']} success, {h['avg_ms']}ms avg")

    lines.append("\n### Resonance Vector")
    res = report.get("resonance", {})
    scores = res.get("scores", {})
    for dim, val in scores.items():
        bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
        lines.append(f"  {dim:>12s}: {bar} {val:.3f}")

    alerts = res.get("alerts", [])
    if alerts:
        lines.append("\n### ⚠ Alerts")
        for a in alerts:
            lines.append(f"  - **{a['risk']}**: {a['action']}")

    healing = report.get("healing_actions", [])
    if healing:
        lines.append("\n### Self-Healing Actions")
        for h in healing:
            lines.append(f"  - [{h['severity']}] {h['law']}: {h['action']}")

    insights = report.get("improvement_insights", [])
    if insights:
        lines.append(f"\n### Improvement Insights ({len(insights)})")
        for ins in insights[:10]:
            lines.append(f"  - [{ins['priority']}] {ins['type']}: {ins['description']}")

    return "\n".join(lines)


def _format_health(health: dict) -> str:
    if not health:
        return "No tool health data yet. Tools need to be instrumented and called."
    lines = ["## Tool Health Metrics\n"]
    for name, h in sorted(health.items(), key=lambda x: x[1].get("total_calls", 0), reverse=True):
        lines.append(
            f"- **{name}**: {h.get('total_calls', 0)} calls, "
            f"{h.get('success_rate', 1):.0%} success, "
            f"{h.get('avg_duration_ms', 0):.0f}ms avg"
        )
    return "\n".join(lines)


def _format_resonance(res: dict) -> str:
    lines = ["## 8D Resonance Vector\n"]
    scores = res.get("scores", {})
    for dim, val in scores.items():
        bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
        lines.append(f"  {dim:>12s}: {bar} {val:.3f}")
    alerts = res.get("alerts", [])
    if alerts:
        lines.append("\n**Alerts**:")
        for a in alerts:
            lines.append(f"  - ⚠ {a['risk']}: {a['action']}")
    return "\n".join(lines)


def _format_couplings(couplings: list) -> str:
    if not couplings:
        return "No tool couplings detected yet. Need more tool usage data."
    lines = ["## Tool Couplings (co-occurrence patterns)\n"]
    for c in couplings[:20]:
        lines.append(
            f"- **{c['tool_a']}** ↔ **{c['tool_b']}**: "
            f"{c['co_occurrence_count']} co-occurrences, "
            f"{c.get('avg_gap_ms', 0):.0f}ms avg gap"
        )
    return "\n".join(lines)


def _format_healing(actions: list) -> str:
    if not actions:
        return "## Self-Healing: All Clear ✓\nNo healing actions required."
    lines = ["## Self-Healing Actions Required\n"]
    for a in actions:
        lines.append(f"- [{a['severity'].upper()}] **{a['law']}**: {a['action']}")
    return "\n".join(lines)


def _format_insights(insights: list) -> str:
    if not insights:
        return "## Insights: None yet\nNeed more tool usage data to generate insights."
    lines = [f"## Improvement Insights ({len(insights)})\n"]
    for ins in insights:
        lines.append(f"### [{ins['priority'].upper()}] {ins['type']}")
        if ins.get("tool"):
            lines.append(f"**Tool**: {ins['tool']}")
        lines.append(f"{ins['description']}\n")
    return "\n".join(lines)


def _format_events(events: list) -> str:
    if not events:
        return "No recent events recorded."
    lines = [f"## Recent Tool Events (last {len(events)})\n"]
    for e in events:
        status = "✓" if e.success else "✗"
        lines.append(
            f"- {status} **{e.tool_name}** ({e.duration_ms:.0f}ms) "
            f"— {e.parameters[:80]}"
        )
    return "\n".join(lines)
