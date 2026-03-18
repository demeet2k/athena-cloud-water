# CRYSTAL: Xi108:W2:A4:S35 | face=S | node=557 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W2:A4:S34→Xi108:W2:A4:S36→Xi108:W1:A4:S35→Xi108:W3:A4:S35→Xi108:W2:A3:S35→Xi108:W2:A5:S35

"""
Agent Watcher — Collective Intelligence Layer That ACTUALLY Watches Agents
==========================================================================
The meta-observer runtime existed but was never wired to observe real agent
outputs.  This module fixes that.  It wraps MetaObserver so that every agent
output flowing through the system is:

  1. Scored on the 12D observation space (structure, semantics, coordination,
     recursion, contradiction, emergence, legibility, routing, grounding,
     compression, interop, potential).
  2. Compared against historical patterns to detect repetition, surface-level
     work, and missed cross-pollination opportunities.
  3. Annotated with specific, actionable improvement notes — not praise.
  4. Fed back into the collective knowledge base so future agents benefit.

USAGE (direct):
    from agent_watcher import AgentWatcher

    watcher = AgentWatcher()
    result = watcher.watch_agent("claude-task-3", "write metro graph", output_text)
    print(result["improvement_notes"])

USAGE (MCP tool):
    query_agent_watcher("report")
    query_agent_watcher("notes:claude-task-3")
    query_agent_watcher("suggest:claude-task-3")
"""

import hashlib
import json
import math
import os
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .meta_observer_runtime import (
    COUPLING_MATRIX,
    DIMENSIONS,
    ELEMENT_LENSES,
    METRIC_TENSOR_DIAG,
    ExperienceMemory,
    MetaObserver,
    Observation,
    apply_lens,
    compute_becoming,
    propagate_coupling,
    riemannian_distance,
    riemannian_magnitude,
)

# ──────────────────────────────────────────────────────────────
#  Quality Detectors — Heuristics That Flag Real Problems
# ──────────────────────────────────────────────────────────────

# Minimum thresholds below which a dimension is "weak"
_WEAK_THRESHOLD = 0.35
# Threshold above which a dimension is "strong"
_STRONG_THRESHOLD = 0.70

# Keywords that indicate surface-level work (high volume, low depth)
_SURFACE_MARKERS = [
    "placeholder", "todo", "stub", "boilerplate", "template",
    "lorem ipsum", "example", "sample", "dummy", "mock",
    "pass  #", "not implemented", "raise NotImplementedError",
    "...", "TBD", "FIXME",
]

# Keywords that indicate structural depth
_DEPTH_MARKERS = [
    "because", "therefore", "trade-off", "constraint", "invariant",
    "edge case", "failure mode", "regression", "benchmark",
    "measured", "observed", "tested", "verified", "proved",
    "conservation", "law", "theorem", "proof",
]

# Known failure patterns to watch for
_KNOWN_FAILURE_PATTERNS = [
    ("empty_docstring", r'"""[\s]*"""', "Empty docstrings — documentation without content"),
    ("generic_error", r'except\s+Exception', "Bare exception catch — swallows real errors"),
    ("magic_number", r'(?<!=\s)[0-9]{3,}(?!\s*[,\]\)])', "Magic numbers without named constants"),
    ("dead_code", r'#\s*(TODO|HACK|XXX|FIXME)', "Unresolved TODO/HACK markers"),
    ("copy_paste", r'(.{40,})\n\1', "Duplicated blocks — copy-paste without abstraction"),
]

def _count_markers(text: str, markers: list[str]) -> int:
    """Count how many marker strings appear in text (case-insensitive)."""
    lower = text.lower()
    return sum(1 for m in markers if m.lower() in lower)

def _line_count(text: str) -> int:
    """Count non-blank lines."""
    return sum(1 for line in text.splitlines() if line.strip())

def _word_count(text: str) -> int:
    """Count words."""
    return len(text.split())

def _unique_word_ratio(text: str) -> float:
    """Ratio of unique words to total words — low ratio = repetitive."""
    words = text.lower().split()
    if not words:
        return 0.0
    return len(set(words)) / len(words)

# ──────────────────────────────────────────────────────────────
#  Agent Profile — Persistent Per-Agent State
# ──────────────────────────────────────────────────────────────

@dataclass
class AgentProfile:
    """Accumulated profile of a single agent's performance."""
    agent_id: str
    first_seen: str = ""
    last_seen: str = ""
    total_observations: int = 0
    # Running averages of 12D scores
    avg_scores: dict = field(default_factory=lambda: {
        dim: 0.5 for dim in DIMENSIONS
    })
    # Weakest and strongest dimensions (updated each observation)
    weakest_dims: list = field(default_factory=list)
    strongest_dims: list = field(default_factory=list)
    # History of observation magnitudes
    magnitude_history: list = field(default_factory=list)
    # Improvement notes issued
    notes_issued: int = 0
    notes_acted_on: int = 0
    # Surface vs depth tracking
    surface_count: int = 0
    depth_count: int = 0
    # Failure pattern hits
    failure_pattern_hits: dict = field(default_factory=dict)
    # Cross-pollination received/given
    insights_received: int = 0
    insights_given: int = 0

# ──────────────────────────────────────────────────────────────
#  Agent Watcher — The Actual Observer
# ──────────────────────────────────────────────────────────────

class AgentWatcher:
    """
    Wraps MetaObserver to observe agent outputs in real-time and generate
    actionable improvement notes for the collective.

    Unlike the raw MetaObserver (which assumes an agent loop with
    suggest/observe/decide cycles), the AgentWatcher operates on
    post-hoc agent outputs: you hand it text, it scores it, compares
    against the collective, and returns concrete notes.
    """

    def __init__(self, project: str = "athena-collective", db_path: str = None):
        if db_path is None:
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "agent_watcher.db")

        self.project = project
        self.db_path = db_path

        # The underlying MetaObserver memory — shared across all agents
        self.memory = ExperienceMemory(db_path)

        # In-memory agent profiles (loaded from / synced to DB)
        self._profiles: dict[str, AgentProfile] = {}

        # Cross-agent insight queue
        self._insight_queue: list[dict] = []

        # Initialize watcher-specific tables
        self._init_watcher_tables()

        # Load existing profiles from DB
        self._load_profiles()

    def _init_watcher_tables(self):
        """Create watcher-specific tables (agent profiles, notes, insights)."""
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS watcher_profiles (
                agent_id TEXT PRIMARY KEY,
                first_seen TEXT,
                last_seen TEXT,
                total_observations INTEGER DEFAULT 0,
                avg_scores TEXT DEFAULT '{}',
                weakest_dims TEXT DEFAULT '[]',
                strongest_dims TEXT DEFAULT '[]',
                magnitude_history TEXT DEFAULT '[]',
                notes_issued INTEGER DEFAULT 0,
                notes_acted_on INTEGER DEFAULT 0,
                surface_count INTEGER DEFAULT 0,
                depth_count INTEGER DEFAULT 0,
                failure_pattern_hits TEXT DEFAULT '{}',
                insights_received INTEGER DEFAULT 0,
                insights_given INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS watcher_notes (
                note_id TEXT PRIMARY KEY,
                agent_id TEXT,
                timestamp TEXT,
                category TEXT,
                severity TEXT,
                note TEXT,
                dimension TEXT,
                score_at_time REAL,
                acted_on INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS watcher_insights (
                insight_id TEXT PRIMARY KEY,
                from_agent TEXT,
                to_agents TEXT,
                timestamp TEXT,
                insight TEXT,
                category TEXT,
                applied INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS watcher_observations (
                obs_id TEXT PRIMARY KEY,
                agent_id TEXT,
                timestamp TEXT,
                task TEXT,
                output_hash TEXT,
                output_length INTEGER,
                scores_json TEXT,
                magnitude REAL,
                becoming_score REAL,
                surface_depth_ratio REAL,
                improvement_notes_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_wn_agent ON watcher_notes(agent_id);
            CREATE INDEX IF NOT EXISTS idx_wo_agent ON watcher_observations(agent_id);
            CREATE INDEX IF NOT EXISTS idx_wi_to ON watcher_insights(to_agents);
        """)
        conn.commit()
        conn.close()

    def _load_profiles(self):
        """Load existing agent profiles from DB."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM watcher_profiles").fetchall()
        for row in rows:
            r = dict(row)
            profile = AgentProfile(
                agent_id=r["agent_id"],
                first_seen=r["first_seen"],
                last_seen=r["last_seen"],
                total_observations=r["total_observations"],
                avg_scores=json.loads(r["avg_scores"]),
                weakest_dims=json.loads(r["weakest_dims"]),
                strongest_dims=json.loads(r["strongest_dims"]),
                magnitude_history=json.loads(r["magnitude_history"]),
                notes_issued=r["notes_issued"],
                notes_acted_on=r["notes_acted_on"],
                surface_count=r["surface_count"],
                depth_count=r["depth_count"],
                failure_pattern_hits=json.loads(r["failure_pattern_hits"]),
                insights_received=r["insights_received"],
                insights_given=r["insights_given"],
            )
            self._profiles[profile.agent_id] = profile
        conn.close()

    def _save_profile(self, profile: AgentProfile):
        """Persist an agent profile to DB."""
        conn = sqlite3.connect(self.db_path)
        # Keep magnitude history bounded
        mag_hist = profile.magnitude_history[-200:]
        conn.execute("""
            INSERT OR REPLACE INTO watcher_profiles VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            profile.agent_id,
            profile.first_seen,
            profile.last_seen,
            profile.total_observations,
            json.dumps(profile.avg_scores),
            json.dumps(profile.weakest_dims),
            json.dumps(profile.strongest_dims),
            json.dumps(mag_hist),
            profile.notes_issued,
            profile.notes_acted_on,
            profile.surface_count,
            profile.depth_count,
            json.dumps(profile.failure_pattern_hits),
            profile.insights_received,
            profile.insights_given,
        ))
        conn.commit()
        conn.close()

    # ──────────────────────────────────────────────────────────
    #  Core API: watch_agent
    # ──────────────────────────────────────────────────────────

    def watch_agent(self, agent_id: str, task: str, output: str,
                    metrics: dict = None) -> dict:
        """
        Observe an agent's output and generate improvement notes.

        Parameters:
            agent_id : Identifier for the agent (e.g. "claude-task-7")
            task     : Description of what the agent was asked to do
            output   : The actual output text produced by the agent
            metrics  : Optional dict of quantitative metrics
                       (e.g. {"lines_of_code": 200, "tests_passing": 5})

        Returns a dict with:
            agent_id, observation_12d, improvement_notes, pattern_matches,
            cross_agent_insights, becoming_score, recommendation
        """
        if metrics is None:
            metrics = {}

        now = datetime.now(timezone.utc).isoformat()

        # Get or create agent profile
        profile = self._profiles.get(agent_id)
        if profile is None:
            profile = AgentProfile(
                agent_id=agent_id,
                first_seen=now,
            )
            self._profiles[agent_id] = profile
            # Also register in the underlying memory
            self.memory.register_agent(agent_id, self.project)

        profile.last_seen = now
        profile.total_observations += 1

        # ── Step 1: Compute 12D scores from the output ──
        scores = self._score_output(task, output, metrics)

        # Apply cross-dimensional coupling
        scores = propagate_coupling(scores)

        # Compute score vector and magnitude
        dim_names = list(DIMENSIONS.keys())
        score_vector = [scores[d] for d in dim_names]
        magnitude = riemannian_magnitude(score_vector)

        # ── Step 2: Update running averages ──
        n = profile.total_observations
        for dim in dim_names:
            old_avg = profile.avg_scores.get(dim, 0.5)
            # Exponential moving average (alpha=0.3 to weight recent higher)
            alpha = 0.3
            profile.avg_scores[dim] = old_avg * (1 - alpha) + scores[dim] * alpha

        profile.magnitude_history.append(round(magnitude, 4))

        # Identify weak and strong dimensions
        sorted_dims = sorted(dim_names, key=lambda d: scores[d])
        profile.weakest_dims = sorted_dims[:3]
        profile.strongest_dims = sorted_dims[-3:]

        # ── Step 3: Surface vs depth detection ──
        surface_hits = _count_markers(output, _SURFACE_MARKERS)
        depth_hits = _count_markers(output, _DEPTH_MARKERS)
        lines = _line_count(output)
        unique_ratio = _unique_word_ratio(output)

        is_surface = False
        surface_depth_ratio = 0.5
        if lines > 0:
            surface_density = surface_hits / max(lines, 1)
            depth_density = depth_hits / max(lines, 1)
            surface_depth_ratio = depth_density / max(surface_density + depth_density, 0.001)
            if surface_density > 0.05 and depth_density < 0.01:
                is_surface = True
            if unique_ratio < 0.25 and lines > 20:
                is_surface = True  # Highly repetitive output

        if is_surface:
            profile.surface_count += 1
        else:
            profile.depth_count += 1

        # ── Step 4: Failure pattern detection ──
        failure_hits = []
        for pattern_name, regex, description in _KNOWN_FAILURE_PATTERNS:
            try:
                matches = re.findall(regex, output)
                if matches:
                    count = len(matches)
                    failure_hits.append((pattern_name, description, count))
                    profile.failure_pattern_hits[pattern_name] = (
                        profile.failure_pattern_hits.get(pattern_name, 0) + count
                    )
            except re.error:
                pass

        # ── Step 5: Generate improvement notes ──
        notes = self._generate_notes(
            agent_id, task, output, scores, profile,
            is_surface, failure_hits, metrics,
        )
        profile.notes_issued += len(notes)

        # ── Step 6: Pattern matching against historical data ──
        pattern_matches = self._match_historical_patterns(agent_id, task, scores)

        # ── Step 7: Cross-agent insights ──
        cross_insights = self._get_cross_agent_insights(agent_id, scores, profile)

        # ── Step 8: Compute becoming score ──
        # Use profile history to compute a becoming score for this agent
        becoming = self._compute_agent_becoming(profile)

        # ── Step 9: Generate recommendation ──
        recommendation = self._generate_recommendation(
            agent_id, scores, profile, notes, cross_insights, becoming,
        )

        # ── Step 10: Store observation ──
        obs_id = hashlib.sha256(
            f"{agent_id}:{now}:{task[:50]}".encode()
        ).hexdigest()[:16]

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO watcher_observations VALUES
            (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            obs_id, agent_id, now, task,
            hashlib.sha256(output.encode()).hexdigest()[:16],
            len(output),
            json.dumps(scores),
            magnitude,
            becoming,
            surface_depth_ratio,
            json.dumps([n["note"] for n in notes]),
        ))
        conn.commit()
        conn.close()

        # Store individual notes
        self._store_notes(agent_id, notes, now)

        # Save updated profile
        self._save_profile(profile)

        # Also record as an observation in the shared ExperienceMemory
        # so MetaObserver pattern extraction picks it up
        cycle_id = profile.total_observations
        obs = Observation(
            cycle_id=cycle_id,
            timestamp=now,
            agent_id=agent_id,
            project=self.project,
            action_type=self._classify_task(task),
            action_description=task,
            action_diff=output[:2000],
            metric_name="quality_magnitude",
            metric_value=magnitude,
            metric_delta=0.0,
            outcome="keep" if magnitude > 1.5 else "neutral",
            **scores,
        )
        self.memory.store_observation(obs)
        self.memory.update_agent_stats(agent_id, cycle_id, magnitude)

        return {
            "agent_id": agent_id,
            "observation_12d": score_vector,
            "scores_labeled": {d: round(scores[d], 3) for d in dim_names},
            "magnitude": round(magnitude, 4),
            "improvement_notes": [n["note"] for n in notes],
            "note_details": notes,
            "pattern_matches": pattern_matches,
            "cross_agent_insights": cross_insights,
            "becoming_score": round(becoming, 6),
            "surface_depth_ratio": round(surface_depth_ratio, 3),
            "recommendation": recommendation,
        }

    # ──────────────────────────────────────────────────────────
    #  Core API: collective_report
    # ──────────────────────────────────────────────────────────

    def collective_report(self) -> str:
        """Generate a collective report across all watched agents."""
        if not self._profiles:
            return "## Agent Watcher — No agents observed yet.\n\nUse `watch_agent()` to start observing."

        lines = []
        lines.append("## Agent Watcher — Collective Intelligence Report")
        lines.append(f"**Project**: {self.project}")
        lines.append(f"**Agents observed**: {len(self._profiles)}")
        lines.append(f"**Total observations**: {sum(p.total_observations for p in self._profiles.values())}")
        lines.append("")

        # Collective becoming score
        becomings = {
            aid: self._compute_agent_becoming(p)
            for aid, p in self._profiles.items()
        }
        collective_becoming = sum(becomings.values()) / max(len(becomings), 1)
        lines.append(f"**Collective Becoming Score**: {collective_becoming:.6f}")
        lines.append("")

        # Per-agent summary table
        lines.append("### Per-Agent Summary")
        lines.append("")
        lines.append("| Agent | Observations | Becoming | Surface% | Weakest Dims | Strongest Dims |")
        lines.append("|-------|-------------|----------|----------|-------------|----------------|")

        for aid, profile in sorted(self._profiles.items()):
            total = profile.total_observations
            becoming = becomings.get(aid, 0.0)
            surface_pct = (
                profile.surface_count / max(profile.surface_count + profile.depth_count, 1) * 100
            )
            weak = ", ".join(d.split("_", 1)[1] for d in profile.weakest_dims[:2])
            strong = ", ".join(d.split("_", 1)[1] for d in profile.strongest_dims[:2])
            lines.append(
                f"| {aid} | {total} | {becoming:.4f} | {surface_pct:.0f}% | {weak} | {strong} |"
            )

        lines.append("")

        # Collective weak dimensions (averaged across all agents)
        lines.append("### Collective Dimension Health")
        lines.append("")
        collective_scores = defaultdict(list)
        for profile in self._profiles.values():
            for dim, score in profile.avg_scores.items():
                collective_scores[dim].append(score)

        dim_avgs = {
            dim: sum(vals) / len(vals)
            for dim, vals in collective_scores.items()
        }
        sorted_dims = sorted(dim_avgs.items(), key=lambda x: x[1])

        for dim, avg in sorted_dims:
            bar_len = int(avg * 20)
            bar = "#" * bar_len + "." * (20 - bar_len)
            label = dim.split("_", 1)[1] if "_" in dim else dim
            status = "WEAK" if avg < _WEAK_THRESHOLD else ("STRONG" if avg > _STRONG_THRESHOLD else "ok")
            lines.append(f"  {label:15s} [{bar}] {avg:.2f}  {status}")

        lines.append("")

        # Recent improvement notes (last 10 across all agents)
        lines.append("### Recent Improvement Notes")
        lines.append("")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        recent_notes = conn.execute(
            "SELECT * FROM watcher_notes ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()
        conn.close()

        if recent_notes:
            for note in recent_notes:
                n = dict(note)
                sev = n["severity"].upper()
                lines.append(f"- [{sev}] **{n['agent_id']}**: {n['note']}")
        else:
            lines.append("- No notes yet.")

        lines.append("")

        # Cross-agent insight opportunities
        lines.append("### Cross-Agent Insight Opportunities")
        lines.append("")
        opportunities = self._find_cross_pollination_opportunities()
        if opportunities:
            for opp in opportunities[:5]:
                lines.append(f"- {opp}")
        else:
            lines.append("- Not enough data yet for cross-pollination.")

        return "\n".join(lines)

    # ──────────────────────────────────────────────────────────
    #  Core API: suggest_for_agent
    # ──────────────────────────────────────────────────────────

    def suggest_for_agent(self, agent_id: str) -> dict:
        """Get suggestions for a specific agent based on collective learning."""
        profile = self._profiles.get(agent_id)
        if profile is None:
            return {
                "agent_id": agent_id,
                "error": f"No profile found for agent '{agent_id}'. Watch some outputs first.",
            }

        suggestions = []

        # 1. Dimension-specific suggestions
        for dim in profile.weakest_dims[:3]:
            dim_label = dim.split("_", 1)[1] if "_" in dim else dim
            dim_desc = DIMENSIONS.get(dim, "")
            score = profile.avg_scores.get(dim, 0.5)
            suggestions.append({
                "type": "dimension_improvement",
                "dimension": dim,
                "current_score": round(score, 3),
                "suggestion": f"Strengthen {dim_label} ({dim_desc}). "
                              f"Current avg: {score:.2f}. Target: >{_STRONG_THRESHOLD:.2f}.",
            })

        # 2. Surface-level work warning
        total_work = profile.surface_count + profile.depth_count
        if total_work > 2:
            surface_ratio = profile.surface_count / max(total_work, 1)
            if surface_ratio > 0.4:
                suggestions.append({
                    "type": "depth_warning",
                    "surface_ratio": round(surface_ratio, 2),
                    "suggestion": f"Surface-level output ratio is {surface_ratio:.0%}. "
                                  f"Focus on depth: explain WHY, include measurements, "
                                  f"address edge cases, verify claims.",
                })

        # 3. Failure pattern warnings
        for pattern_name, count in sorted(
            profile.failure_pattern_hits.items(),
            key=lambda x: -x[1]
        )[:3]:
            if count >= 2:
                desc = next(
                    (d for n, _, d in _KNOWN_FAILURE_PATTERNS if n == pattern_name),
                    pattern_name
                )
                suggestions.append({
                    "type": "failure_pattern",
                    "pattern": pattern_name,
                    "occurrences": count,
                    "suggestion": f"Recurring issue: {desc} (seen {count} times). "
                                  f"Address this pattern systematically.",
                })

        # 4. Cross-pollination suggestions from other agents
        for other_id, other_profile in self._profiles.items():
            if other_id == agent_id:
                continue
            # Find dimensions where the other agent is strong and this one is weak
            for dim in profile.weakest_dims:
                other_score = other_profile.avg_scores.get(dim, 0.5)
                this_score = profile.avg_scores.get(dim, 0.5)
                if other_score > _STRONG_THRESHOLD and this_score < _WEAK_THRESHOLD:
                    dim_label = dim.split("_", 1)[1] if "_" in dim else dim
                    suggestions.append({
                        "type": "cross_pollination",
                        "from_agent": other_id,
                        "dimension": dim,
                        "suggestion": f"Agent '{other_id}' scores {other_score:.2f} on {dim_label} "
                                      f"vs your {this_score:.2f}. Study their approach to {dim_label}.",
                    })

        # 5. Becoming trajectory
        mag_hist = profile.magnitude_history[-20:]
        if len(mag_hist) >= 3:
            recent_avg = sum(mag_hist[-3:]) / 3
            older_avg = sum(mag_hist[:3]) / 3
            if recent_avg < older_avg * 0.9:
                suggestions.append({
                    "type": "regression_warning",
                    "suggestion": f"Quality magnitude is declining: {older_avg:.3f} -> {recent_avg:.3f}. "
                                  f"Recent outputs are weaker than earlier ones.",
                })
            elif recent_avg > older_avg * 1.1:
                suggestions.append({
                    "type": "positive_trajectory",
                    "suggestion": f"Quality improving: {older_avg:.3f} -> {recent_avg:.3f}. "
                                  f"Maintain current approach.",
                })

        return {
            "agent_id": agent_id,
            "total_observations": profile.total_observations,
            "becoming_score": round(self._compute_agent_becoming(profile), 6),
            "suggestions": suggestions,
            "strongest_dimensions": [
                {
                    "dim": d,
                    "score": round(profile.avg_scores.get(d, 0.5), 3),
                }
                for d in profile.strongest_dims
            ],
            "weakest_dimensions": [
                {
                    "dim": d,
                    "score": round(profile.avg_scores.get(d, 0.5), 3),
                }
                for d in profile.weakest_dims
            ],
        }

    # ──────────────────────────────────────────────────────────
    #  Core API: route_insight
    # ──────────────────────────────────────────────────────────

    def route_insight(self, from_agent: str, insight: str, to_agents: list[str]):
        """
        Route an insight from one agent to others.
        Stores the insight persistently so target agents can retrieve it.
        """
        insight_id = hashlib.sha256(
            f"{from_agent}:{insight}:{time.time()}".encode()
        ).hexdigest()[:16]

        now = datetime.now(timezone.utc).isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO watcher_insights VALUES (?,?,?,?,?,?,0)
        """, (
            insight_id, from_agent, json.dumps(to_agents), now,
            insight, "manual_route",
        ))
        conn.commit()
        conn.close()

        # Update profiles
        from_profile = self._profiles.get(from_agent)
        if from_profile:
            from_profile.insights_given += 1
            self._save_profile(from_profile)

        for target in to_agents:
            target_profile = self._profiles.get(target)
            if target_profile:
                target_profile.insights_received += 1
                self._save_profile(target_profile)

        # Also record in the shared ExperienceMemory for MetaObserver
        for target in to_agents:
            self.memory.share_insight(
                from_agent, target, "cross_pollination",
                insight, f"Routed via AgentWatcher at {now}",
            )

    # ──────────────────────────────────────────────────────────
    #  Internal: 12D Scoring of Agent Outputs
    # ──────────────────────────────────────────────────────────

    def _score_output(self, task: str, output: str, metrics: dict) -> dict:
        """
        Score an agent output on all 12 dimensions.
        Uses text analysis heuristics — not LLM evaluation — so this
        runs with zero external dependencies and zero latency.
        """
        lines = _line_count(output)
        words = _word_count(output)
        unique_ratio = _unique_word_ratio(output)
        surface_hits = _count_markers(output, _SURFACE_MARKERS)
        depth_hits = _count_markers(output, _DEPTH_MARKERS)

        # x1_structure: Does the output have clear organization?
        has_headers = bool(re.findall(r'^#{1,4}\s', output, re.MULTILINE))
        has_functions = bool(re.findall(r'\bdef\s+\w+|class\s+\w+', output))
        has_sections = bool(re.findall(r'\n\n', output))
        structure_signals = sum([has_headers, has_functions, has_sections])
        x1 = min(1.0, 0.2 + structure_signals * 0.2 + (min(lines, 100) / 200))

        # x2_semantics: Naming quality, conceptual clarity
        # Good names are descriptive (longer), bad names are single chars
        identifiers = re.findall(r'\b[a-z_][a-z0-9_]{2,}\b', output)
        avg_name_len = sum(len(i) for i in identifiers) / max(len(identifiers), 1)
        has_docstrings = bool(re.findall(r'"""[^"]{10,}"""', output, re.DOTALL))
        x2 = min(1.0, 0.2 + (min(avg_name_len, 15) / 20) + (0.2 if has_docstrings else 0))

        # x3_coordination: References to other agents/systems/modules
        coord_markers = ["import ", "from ", "agent", "cross", "shared", "collective",
                         "integrate", "coordinate", "bridge", "handoff"]
        coord_count = _count_markers(output, coord_markers)
        x3 = min(1.0, 0.1 + coord_count * 0.1)

        # x4_recursion: References to prior work, learning, iteration
        recursion_markers = ["previous", "prior", "building on", "iteration",
                            "learned", "improved", "refined", "based on",
                            "cycle", "epoch", "history"]
        recursion_count = _count_markers(output, recursion_markers)
        x4 = min(1.0, 0.1 + recursion_count * 0.12)

        # x5_contradiction: Presence of conflict handling, edge cases
        # Higher = fewer contradictions (healthier)
        contradiction_markers = ["however", "but", "except", "edge case",
                                 "caveat", "limitation", "trade-off", "risk"]
        contra_count = _count_markers(output, contradiction_markers)
        # Some contradiction awareness is GOOD (shows critical thinking)
        x5 = min(1.0, 0.3 + min(contra_count, 5) * 0.12)

        # x6_emergence: Novel patterns, unexpected connections
        emergence_markers = ["novel", "unexpected", "emergent", "discovered",
                            "insight", "pattern", "synthesis", "breakthrough"]
        emergence_count = _count_markers(output, emergence_markers)
        x6 = min(1.0, 0.2 + emergence_count * 0.15)

        # x7_legibility: Readability — line length, comments, formatting
        output_lines = output.splitlines()
        if output_lines:
            long_lines = sum(1 for l in output_lines if len(l) > 120)
            long_ratio = long_lines / max(len(output_lines), 1)
            comment_lines = sum(1 for l in output_lines if l.strip().startswith("#"))
            comment_ratio = comment_lines / max(len(output_lines), 1)
            x7 = min(1.0, 0.3 + (1.0 - long_ratio) * 0.3 + comment_ratio * 2.0)
        else:
            x7 = 0.1

        # x8_routing: Task alignment — does the output address the task?
        task_words = set(task.lower().split())
        output_lower = output.lower()
        task_coverage = sum(1 for w in task_words if w in output_lower and len(w) > 3)
        x8 = min(1.0, 0.1 + task_coverage * 0.15)

        # x9_grounding: Evidence, metrics, concrete results
        grounding_markers = ["measured", "benchmark", "result:", "output:",
                            "error:", "score:", "accuracy", "latency",
                            "test", "assert", "verify", "confirmed"]
        grounding_count = _count_markers(output, grounding_markers)
        has_numbers = len(re.findall(r'\b\d+\.\d+\b', output))
        x9 = min(1.0, 0.1 + grounding_count * 0.1 + min(has_numbers, 5) * 0.08)

        # x10_compression: Signal density — unique information per line
        if lines > 0:
            x10 = min(1.0, unique_ratio * 0.8 + (depth_hits / max(lines, 1)) * 5)
        else:
            x10 = 0.1

        # x11_interop: Cross-system compatibility markers
        interop_markers = ["api", "interface", "protocol", "schema", "format",
                          "compatible", "standard", "specification", "contract"]
        interop_count = _count_markers(output, interop_markers)
        x11 = min(1.0, 0.2 + interop_count * 0.12)

        # x12_potential: Future leverage, extensibility
        potential_markers = ["extensible", "future", "next step", "roadmap",
                           "can be extended", "plug", "hook", "callback",
                           "abstract", "generic", "reusable"]
        potential_count = _count_markers(output, potential_markers)
        x12 = min(1.0, 0.2 + potential_count * 0.12)

        # Apply metric-provided overrides where available
        if "quality_score" in metrics:
            # If caller provides a quality score, blend it in
            q = max(0.0, min(1.0, metrics["quality_score"]))
            x9 = x9 * 0.5 + q * 0.5  # Blend with grounding

        return {
            "x1_structure": round(x1, 4),
            "x2_semantics": round(x2, 4),
            "x3_coordination": round(x3, 4),
            "x4_recursion": round(x4, 4),
            "x5_contradiction": round(x5, 4),
            "x6_emergence": round(x6, 4),
            "x7_legibility": round(x7, 4),
            "x8_routing": round(x8, 4),
            "x9_grounding": round(x9, 4),
            "x10_compression": round(x10, 4),
            "x11_interop": round(x11, 4),
            "x12_potential": round(x12, 4),
        }

    # ──────────────────────────────────────────────────────────
    #  Internal: Improvement Note Generation
    # ──────────────────────────────────────────────────────────

    def _generate_notes(self, agent_id: str, task: str, output: str,
                        scores: dict, profile: AgentProfile,
                        is_surface: bool, failure_hits: list,
                        metrics: dict) -> list[dict]:
        """
        Generate specific, actionable improvement notes.
        No generic praise.  Every note must be something the agent
        can concretely act on.
        """
        notes = []

        # 1. Weak dimension notes
        dim_names = list(DIMENSIONS.keys())
        for dim in dim_names:
            score = scores.get(dim, 0.5)
            if score < _WEAK_THRESHOLD:
                dim_label = dim.split("_", 1)[1]
                dim_desc = DIMENSIONS[dim]
                note = self._dimension_specific_note(dim, score, task)
                notes.append({
                    "note": note,
                    "category": "weak_dimension",
                    "severity": "high" if score < 0.2 else "medium",
                    "dimension": dim,
                    "score": round(score, 3),
                })

        # 2. Surface-level work detection
        if is_surface:
            notes.append({
                "note": (
                    "Output shows surface-level patterns: placeholders, stubs, or "
                    "boilerplate without substance. Replace with concrete implementations, "
                    "actual measurements, or real analysis."
                ),
                "category": "surface_work",
                "severity": "high",
                "dimension": "x9_grounding",
                "score": scores.get("x9_grounding", 0.5),
            })

        # 3. Failure pattern notes
        for pattern_name, description, count in failure_hits:
            notes.append({
                "note": f"{description} (found {count} instance{'s' if count > 1 else ''}).",
                "category": "failure_pattern",
                "severity": "medium" if count < 3 else "high",
                "dimension": "x1_structure",
                "score": scores.get("x1_structure", 0.5),
            })

        # 4. Repetition detection (agent repeating themselves)
        if profile.total_observations > 1:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            recent_obs = conn.execute(
                "SELECT output_hash FROM watcher_observations "
                "WHERE agent_id=? ORDER BY timestamp DESC LIMIT 10",
                (agent_id,)
            ).fetchall()
            conn.close()

            current_hash = hashlib.sha256(output.encode()).hexdigest()[:16]
            repeat_count = sum(1 for r in recent_obs if r["output_hash"] == current_hash)
            if repeat_count > 0:
                notes.append({
                    "note": (
                        "This output is identical to a previous one. "
                        "If retrying, change approach rather than repeating the same work."
                    ),
                    "category": "repetition",
                    "severity": "high",
                    "dimension": "x4_recursion",
                    "score": 0.1,
                })

        # 5. Missing grounding
        if scores.get("x9_grounding", 0.5) < 0.3 and _line_count(output) > 20:
            notes.append({
                "note": (
                    "Output lacks evidence. Add measurements, test results, benchmarks, "
                    "or concrete examples to support claims."
                ),
                "category": "missing_grounding",
                "severity": "medium",
                "dimension": "x9_grounding",
                "score": scores.get("x9_grounding", 0.5),
            })

        # 6. Missing task alignment
        if scores.get("x8_routing", 0.5) < 0.3:
            notes.append({
                "note": (
                    f"Output doesn't clearly address the task: '{task[:80]}'. "
                    f"Ensure the core deliverable is present, not just related work."
                ),
                "category": "task_misalignment",
                "severity": "high",
                "dimension": "x8_routing",
                "score": scores.get("x8_routing", 0.5),
            })

        # 7. Declining trajectory
        mag_hist = profile.magnitude_history
        if len(mag_hist) >= 5:
            recent_3 = sum(mag_hist[-3:]) / 3
            prior_3 = sum(mag_hist[-6:-3]) / 3 if len(mag_hist) >= 6 else sum(mag_hist[:3]) / 3
            if recent_3 < prior_3 * 0.85:
                notes.append({
                    "note": (
                        f"Quality declining: recent magnitude {recent_3:.3f} vs prior {prior_3:.3f}. "
                        f"Review what changed and course-correct."
                    ),
                    "category": "declining_quality",
                    "severity": "high",
                    "dimension": "x4_recursion",
                    "score": scores.get("x4_recursion", 0.5),
                })

        return notes

    def _dimension_specific_note(self, dim: str, score: float, task: str) -> str:
        """Generate a dimension-specific actionable note."""
        advice = {
            "x1_structure": (
                "Output lacks clear organization. Add function/class decomposition, "
                "use headers or sections, group related logic together."
            ),
            "x2_semantics": (
                "Naming and conceptual clarity is weak. Use descriptive variable names "
                "(not single letters), add docstrings, define terms before using them."
            ),
            "x3_coordination": (
                "No evidence of coordinating with other components or agents. "
                "Reference shared interfaces, import from existing modules, "
                "acknowledge what other agents have built."
            ),
            "x4_recursion": (
                "Not building on prior work. Reference previous iterations, "
                "explain what was learned from earlier attempts, close feedback loops."
            ),
            "x5_contradiction": (
                "No contradiction awareness. Acknowledge trade-offs, edge cases, "
                "and limitations. Critical thinking makes output more trustworthy."
            ),
            "x6_emergence": (
                "Output is mechanical — no novel connections or insights. "
                "Look for unexpected patterns, synthesize across domains, "
                "note what surprised you."
            ),
            "x7_legibility": (
                "Hard to read. Shorten long lines, add inline comments for non-obvious logic, "
                "use consistent formatting, break complex expressions into named steps."
            ),
            "x8_routing": (
                f"Output doesn't address the core task: '{task[:60]}'. "
                f"Lead with the deliverable, then add context."
            ),
            "x9_grounding": (
                "Claims lack evidence. Add test results, benchmarks, concrete examples, "
                "or metrics. 'It works' is not evidence — show HOW you verified."
            ),
            "x10_compression": (
                "Output is verbose or repetitive. Remove redundant explanations, "
                "consolidate duplicated logic, say more with fewer words."
            ),
            "x11_interop": (
                "Not addressing cross-system compatibility. Define interfaces, "
                "use standard formats, document the contract with other components."
            ),
            "x12_potential": (
                "No extensibility hooks. Add abstract base classes, callback points, "
                "configuration options, or document how this can be built upon."
            ),
        }
        return advice.get(dim, f"Dimension {dim} scored {score:.2f} — needs improvement.")

    def _store_notes(self, agent_id: str, notes: list[dict], timestamp: str):
        """Store improvement notes in DB."""
        if not notes:
            return
        conn = sqlite3.connect(self.db_path)
        for note in notes:
            note_id = hashlib.sha256(
                f"{agent_id}:{note['note'][:50]}:{timestamp}".encode()
            ).hexdigest()[:16]
            conn.execute("""
                INSERT OR IGNORE INTO watcher_notes VALUES (?,?,?,?,?,?,?,?,0)
            """, (
                note_id, agent_id, timestamp,
                note.get("category", ""),
                note.get("severity", "medium"),
                note["note"],
                note.get("dimension", ""),
                note.get("score", 0.5),
            ))
        conn.commit()
        conn.close()

    # ──────────────────────────────────────────────────────────
    #  Internal: Pattern Matching & Cross-Agent Intelligence
    # ──────────────────────────────────────────────────────────

    def _match_historical_patterns(self, agent_id: str, task: str,
                                    scores: dict) -> list[str]:
        """Match current observation against historical patterns."""
        matches = []
        try:
            patterns = self.memory.extract_patterns(min_samples=2)
        except Exception:
            return matches

        task_type = self._classify_task(task)

        for pattern in patterns:
            if pattern.action_type == task_type:
                if pattern.success_rate > 0.6:
                    matches.append(
                        f"Pattern '{pattern.action_type}' has {pattern.success_rate:.0%} "
                        f"success rate ({pattern.sample_count} samples). Follow proven approach."
                    )
                elif pattern.success_rate < 0.3 and pattern.sample_count >= 3:
                    matches.append(
                        f"WARNING: Pattern '{pattern.action_type}' has only "
                        f"{pattern.success_rate:.0%} success rate. Consider different approach."
                    )

        return matches

    def _get_cross_agent_insights(self, agent_id: str, scores: dict,
                                   profile: AgentProfile) -> list[dict]:
        """Find insights from other agents that could help this one."""
        insights = []

        for other_id, other_profile in self._profiles.items():
            if other_id == agent_id:
                continue

            # Check for complementary strengths
            for dim in profile.weakest_dims:
                other_score = other_profile.avg_scores.get(dim, 0.5)
                this_score = profile.avg_scores.get(dim, 0.5)
                if other_score > _STRONG_THRESHOLD and this_score < _WEAK_THRESHOLD:
                    dim_label = dim.split("_", 1)[1] if "_" in dim else dim
                    insights.append({
                        "from_agent": other_id,
                        "dimension": dim,
                        "insight": (
                            f"Agent '{other_id}' excels at {dim_label} "
                            f"(avg {other_score:.2f} vs your {this_score:.2f}). "
                            f"Study their approach."
                        ),
                        "type": "complementary_strength",
                    })

        # Also check the shared memory for explicit cross-agent insights
        try:
            shared_insights = self.memory.get_cross_agent_insights(agent_id)
            for si in shared_insights[:3]:
                insights.append({
                    "from_agent": si.get("source_agent", "unknown"),
                    "dimension": "",
                    "insight": si.get("description", ""),
                    "type": si.get("insight_type", "shared"),
                })
        except Exception:
            pass

        return insights[:5]  # Cap at 5

    def _find_cross_pollination_opportunities(self) -> list[str]:
        """Find opportunities where one agent's strength matches another's weakness."""
        opportunities = []
        agents = list(self._profiles.items())

        for i, (aid_a, prof_a) in enumerate(agents):
            for aid_b, prof_b in agents[i + 1:]:
                for dim in DIMENSIONS:
                    score_a = prof_a.avg_scores.get(dim, 0.5)
                    score_b = prof_b.avg_scores.get(dim, 0.5)
                    dim_label = dim.split("_", 1)[1]

                    if score_a > _STRONG_THRESHOLD and score_b < _WEAK_THRESHOLD:
                        opportunities.append(
                            f"'{aid_a}' can teach '{aid_b}' about {dim_label} "
                            f"({score_a:.2f} vs {score_b:.2f})"
                        )
                    elif score_b > _STRONG_THRESHOLD and score_a < _WEAK_THRESHOLD:
                        opportunities.append(
                            f"'{aid_b}' can teach '{aid_a}' about {dim_label} "
                            f"({score_b:.2f} vs {score_a:.2f})"
                        )

        return opportunities

    def _compute_agent_becoming(self, profile: AgentProfile) -> float:
        """
        Compute a becoming score for a single agent.
        Becoming = quality gained per observation consumed.
        """
        if profile.total_observations == 0:
            return 0.0

        # Quality: average magnitude
        if profile.magnitude_history:
            avg_mag = sum(profile.magnitude_history) / len(profile.magnitude_history)
        else:
            avg_mag = 0.5

        # Depth ratio: depth / (surface + depth)
        total_work = profile.surface_count + profile.depth_count
        depth_ratio = profile.depth_count / max(total_work, 1)

        # Dimension coverage: how many dimensions are above weak threshold?
        strong_dims = sum(
            1 for d in DIMENSIONS
            if profile.avg_scores.get(d, 0.5) > _WEAK_THRESHOLD
        )
        coverage = strong_dims / 12.0

        # Insight flow: insights given + received normalized
        insight_flow = min(1.0, (profile.insights_given + profile.insights_received) * 0.1)

        # Notes acted on ratio (improvement responsiveness)
        notes_ratio = (
            profile.notes_acted_on / max(profile.notes_issued, 1)
            if profile.notes_issued > 0 else 0.5
        )

        becoming = (
            avg_mag * 0.3 +
            depth_ratio * 0.25 +
            coverage * 0.25 +
            insight_flow * 0.1 +
            notes_ratio * 0.1
        )

        return round(becoming, 6)

    def _generate_recommendation(self, agent_id: str, scores: dict,
                                  profile: AgentProfile, notes: list[dict],
                                  cross_insights: list[dict],
                                  becoming: float) -> str:
        """Generate a single actionable recommendation for the agent."""
        # Priority 1: If surface-level work, call it out
        if any(n["category"] == "surface_work" for n in notes):
            return (
                "PRIORITY: Your output is surface-level. Stop generating volume "
                "and start generating substance. One deep, grounded, tested solution "
                "beats ten stubs."
            )

        # Priority 2: If repeating known failures
        if any(n["category"] == "repetition" for n in notes):
            return (
                "PRIORITY: You are repeating a previous output verbatim. "
                "Change your approach before retrying."
            )

        # Priority 3: Task misalignment
        if any(n["category"] == "task_misalignment" for n in notes):
            return (
                "PRIORITY: Your output does not address the requested task. "
                "Re-read the task description and lead with the core deliverable."
            )

        # Priority 4: Declining quality
        if any(n["category"] == "declining_quality" for n in notes):
            return (
                "Your quality is declining compared to earlier work. "
                "Review what changed and course-correct before continuing."
            )

        # Priority 5: Weak dimension focus
        high_severity_notes = [n for n in notes if n["severity"] == "high"]
        if high_severity_notes:
            top_note = high_severity_notes[0]
            return f"Focus on: {top_note['note']}"

        # Priority 6: Cross-pollination
        if cross_insights:
            top_insight = cross_insights[0]
            return f"Cross-pollination opportunity: {top_insight['insight']}"

        # Default: maintain trajectory
        if becoming > 0.6:
            return "Trajectory is solid. Maintain depth and continue building on prior work."
        elif becoming > 0.3:
            return (
                "Trajectory is adequate but could improve. "
                "Focus on your weakest dimensions and add more grounding evidence."
            )
        else:
            return (
                "Becoming score is low. Prioritize: (1) address the actual task, "
                "(2) add evidence/tests, (3) build on prior work rather than starting fresh."
            )

    def _classify_task(self, task: str) -> str:
        """Classify a task description into an action type for pattern matching."""
        lower = task.lower()
        if any(w in lower for w in ["fix", "bug", "error", "broken"]):
            return "bugfix"
        elif any(w in lower for w in ["create", "build", "implement", "write", "add"]):
            return "implementation"
        elif any(w in lower for w in ["refactor", "clean", "reorganize", "simplify"]):
            return "refactoring"
        elif any(w in lower for w in ["test", "verify", "check", "validate"]):
            return "testing"
        elif any(w in lower for w in ["document", "readme", "explain", "describe"]):
            return "documentation"
        elif any(w in lower for w in ["optimize", "performance", "speed", "fast"]):
            return "optimization"
        elif any(w in lower for w in ["review", "analyze", "inspect", "audit"]):
            return "analysis"
        elif any(w in lower for w in ["integrate", "connect", "bridge", "link"]):
            return "integration"
        elif any(w in lower for w in ["design", "architect", "plan", "spec"]):
            return "design"
        else:
            return "general"

    def _get_all_agents(self) -> list[dict]:
        """Get summary of all watched agents."""
        result = []
        for aid, profile in sorted(self._profiles.items()):
            becoming = self._compute_agent_becoming(profile)
            total_work = profile.surface_count + profile.depth_count
            result.append({
                "agent_id": aid,
                "observations": profile.total_observations,
                "becoming": round(becoming, 4),
                "surface_ratio": round(
                    profile.surface_count / max(total_work, 1), 2
                ),
                "weakest": [d.split("_", 1)[1] for d in profile.weakest_dims[:2]],
                "strongest": [d.split("_", 1)[1] for d in profile.strongest_dims[:2]],
                "notes_issued": profile.notes_issued,
                "last_seen": profile.last_seen,
            })
        return result

    # ──────────────────────────────────────────────────────────
    #  Swarm Coordination (wired to observer_swarm)
    # ──────────────────────────────────────────────────────────

    def coordinate_swarm(self, observation: "SwarmObservation", query: str = "") -> dict:
        """Coordinate a swarm observation through the agent watcher.

        Feeds the swarm's aggregated observation into the watcher's 12D scoring,
        generates improvement notes, and returns feedback for query modification.

        Args:
            observation: SwarmObservation from observer_swarm.run_parallel()
            query: The original query that was observed

        Returns:
            dict with: improvement_notes, query_modifications, meta_score
        """
        # Score the swarm's aggregated output as if it were an agent
        swarm_output = observation.summary()
        watcher_result = self.watch_agent(
            agent_id="swarm-observer",
            task=f"Crystal-parallel observation: {query[:80]}",
            output=swarm_output,
            metrics={
                "observer_count": observation.observer_count,
                "coherence": observation.swarm_coherence,
                "discrimination": observation.swarm_discrimination,
                "element_balance": observation.element_balance,
            },
        )

        # Extract improvement notes
        notes = watcher_result.get("improvement_notes", [])

        # Generate query modifications based on weak dimensions
        query_mods = []
        if notes:
            for note in notes[:3]:
                dim = note.get("dimension", "")
                if "compression" in dim:
                    query_mods.append("focus on fractal compression quality")
                elif "structure" in dim:
                    query_mods.append("emphasize structural gate transitions")
                elif "semantics" in dim:
                    query_mods.append("deepen token-level semantic matching")
                elif "emergence" in dim:
                    query_mods.append("explore cross-shell emergence patterns")

        return {
            "improvement_notes": notes,
            "query_modifications": query_mods,
            "meta_score": watcher_result.get("becoming_score", 0.5),
            "recommendation": watcher_result.get("recommendation", ""),
        }

# ──────────────────────────────────────────────────────────────
#  Singleton Instance (shared across tool calls)
# ──────────────────────────────────────────────────────────────

_WATCHER_INSTANCE: Optional[AgentWatcher] = None

def _get_watcher() -> AgentWatcher:
    """Get or create the singleton AgentWatcher instance."""
    global _WATCHER_INSTANCE
    if _WATCHER_INSTANCE is None:
        _WATCHER_INSTANCE = AgentWatcher()
    return _WATCHER_INSTANCE

# ──────────────────────────────────────────────────────────────
#  MCP Tool Function
# ──────────────────────────────────────────────────────────────

def query_agent_watcher(component: str = "report") -> str:
    """
    Query the Agent Watcher — collective intelligence across all agents.

    Components:
      - report      : Full collective report
      - agents      : List all watched agents with performance
      - notes:ID    : Improvement notes for specific agent
      - insights    : Cross-agent insights and patterns
      - suggest:ID  : Suggestions for specific agent
      - becoming    : Collective becoming score
      - watch:ID:TASK:OUTPUT  : Watch an agent output (pipe-separated)
      - route:FROM:INSIGHT:TO1,TO2  : Route insight between agents

    Examples:
      query_agent_watcher("report")
      query_agent_watcher("notes:claude-task-3")
      query_agent_watcher("suggest:claude-task-3")
      query_agent_watcher("becoming")
    """
    watcher = _get_watcher()
    comp = component.strip()

    # ── report ──
    if comp == "report":
        return watcher.collective_report()

    # ── agents ──
    elif comp == "agents":
        agents = watcher._get_all_agents()
        if not agents:
            return "No agents observed yet. Use watch_agent() to start."
        lines = ["## Watched Agents\n"]
        for a in agents:
            lines.append(
                f"- **{a['agent_id']}**: {a['observations']} obs, "
                f"becoming={a['becoming']}, surface={a['surface_ratio']:.0%}, "
                f"weak=[{', '.join(a['weakest'])}], "
                f"strong=[{', '.join(a['strongest'])}], "
                f"notes={a['notes_issued']}"
            )
        return "\n".join(lines)

    # ── notes:AGENT_ID ──
    elif comp.startswith("notes:"):
        agent_id = comp[6:].strip()
        conn = sqlite3.connect(watcher.db_path)
        conn.row_factory = sqlite3.Row
        notes = conn.execute(
            "SELECT * FROM watcher_notes WHERE agent_id=? ORDER BY timestamp DESC LIMIT 20",
            (agent_id,)
        ).fetchall()
        conn.close()

        if not notes:
            return f"No improvement notes for agent '{agent_id}'."

        lines = [f"## Improvement Notes for '{agent_id}'\n"]
        for note in notes:
            n = dict(note)
            sev = n["severity"].upper()
            dim = n["dimension"].split("_", 1)[1] if "_" in n["dimension"] else n["dimension"]
            lines.append(
                f"- [{sev}] ({n['category']}, {dim}={n['score_at_time']:.2f}) "
                f"{n['note']}"
            )
        return "\n".join(lines)

    # ── insights ──
    elif comp == "insights":
        conn = sqlite3.connect(watcher.db_path)
        conn.row_factory = sqlite3.Row
        insights = conn.execute(
            "SELECT * FROM watcher_insights ORDER BY timestamp DESC LIMIT 20"
        ).fetchall()
        conn.close()

        opportunities = watcher._find_cross_pollination_opportunities()

        lines = ["## Cross-Agent Insights\n"]
        if insights:
            lines.append("### Routed Insights")
            for ins in insights:
                i = dict(ins)
                lines.append(
                    f"- {i['from_agent']} -> {i['to_agents']}: {i['insight']} "
                    f"({'applied' if i['applied'] else 'pending'})"
                )
        if opportunities:
            lines.append("\n### Cross-Pollination Opportunities")
            for opp in opportunities[:10]:
                lines.append(f"- {opp}")

        if not insights and not opportunities:
            lines.append("No insights yet. Need more agent observations.")

        return "\n".join(lines)

    # ── suggest:AGENT_ID ──
    elif comp.startswith("suggest:"):
        agent_id = comp[8:].strip()
        result = watcher.suggest_for_agent(agent_id)
        if "error" in result:
            return result["error"]

        lines = [f"## Suggestions for '{agent_id}'\n"]
        lines.append(f"**Becoming**: {result['becoming_score']}")
        lines.append(f"**Observations**: {result['total_observations']}\n")

        if result["suggestions"]:
            for s in result["suggestions"]:
                lines.append(f"- [{s['type']}] {s['suggestion']}")
        else:
            lines.append("- No specific suggestions at this time. Keep going.")

        lines.append("\n**Strongest**: " + ", ".join(
            f"{d['dim'].split('_', 1)[1]}={d['score']}"
            for d in result["strongest_dimensions"]
        ))
        lines.append("**Weakest**: " + ", ".join(
            f"{d['dim'].split('_', 1)[1]}={d['score']}"
            for d in result["weakest_dimensions"]
        ))
        return "\n".join(lines)

    # ── becoming ──
    elif comp == "becoming":
        if not watcher._profiles:
            return "No agents observed yet."

        lines = ["## Collective Becoming Scores\n"]
        total_becoming = 0.0
        for aid, profile in sorted(watcher._profiles.items()):
            b = watcher._compute_agent_becoming(profile)
            total_becoming += b
            bar_len = int(b * 20)
            bar = "#" * bar_len + "." * (20 - bar_len)
            lines.append(f"  {aid:25s} [{bar}] {b:.4f}")

        collective = total_becoming / max(len(watcher._profiles), 1)
        lines.append(f"\n**Collective**: {collective:.4f}")
        return "\n".join(lines)

    # ── watch:AGENT_ID:TASK:OUTPUT ──
    elif comp.startswith("watch:"):
        parts = comp[6:].split(":", 2)
        if len(parts) < 3:
            return "Usage: watch:AGENT_ID:TASK:OUTPUT_TEXT"
        agent_id, task, output = parts[0].strip(), parts[1].strip(), parts[2].strip()
        result = watcher.watch_agent(agent_id, task, output)
        lines = [f"## Observation for '{agent_id}'\n"]
        lines.append(f"**Magnitude**: {result['magnitude']}")
        lines.append(f"**Becoming**: {result['becoming_score']}")
        lines.append(f"**Recommendation**: {result['recommendation']}\n")
        if result["improvement_notes"]:
            lines.append("**Improvement Notes**:")
            for note in result["improvement_notes"]:
                lines.append(f"- {note}")
        if result["pattern_matches"]:
            lines.append("\n**Pattern Matches**:")
            for pm in result["pattern_matches"]:
                lines.append(f"- {pm}")
        return "\n".join(lines)

    # ── route:FROM:INSIGHT:TO1,TO2 ──
    elif comp.startswith("route:"):
        parts = comp[6:].split(":", 2)
        if len(parts) < 3:
            return "Usage: route:FROM_AGENT:INSIGHT_TEXT:TO_AGENT1,TO_AGENT2"
        from_agent = parts[0].strip()
        insight = parts[1].strip()
        to_agents = [a.strip() for a in parts[2].split(",")]
        watcher.route_insight(from_agent, insight, to_agents)
        return f"Insight routed from '{from_agent}' to {to_agents}."

    else:
        return (
            "Unknown component. Available:\n"
            "  report, agents, notes:ID, insights, suggest:ID, becoming, "
            "watch:ID:TASK:OUTPUT, route:FROM:INSIGHT:TO1,TO2"
        )
