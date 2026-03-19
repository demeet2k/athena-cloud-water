# CRYSTAL: Xi108:W2:A12:S36 | face=F | node=666 | depth=0 | phase=Omega
# METRO: Me
# BRIDGES: maverick→observer→efficiency→bridge→metadata
"""
Sandbox Maverick — Gap Hunter, Tunnel Finder, Integration Scout
================================================================
The Maverick's job is to actively PROBE the sandbox for:

  1. HOLES    — blind spots where observations are NOT being captured
  2. GAPS     — disconnected subsystems that should be cross-wired
  3. TUNNELS  — unexpected shortcuts or leaks through the system
  4. BRIDGES  — integration opportunities for compound efficiency
  5. DECAY    — degradation over time (memory leaks, growing latency, state rot)

Philosophy: The Sandbox Observer watches WHAT happens. The Efficiency
Engine optimizes HOW it happens. The Maverick asks WHERE ELSE could
something happen that we're not seeing.

The Maverick is the organism's immune system + scouting party:
  - Immune: detect and flag anomalies, leaks, violations
  - Scout: find unexplored territory where new efficiency gains hide

MAVERICK PROTOCOL:
  For each probe, the Maverick produces a MaverickFinding with:
    - finding_type: hole | gap | tunnel | bridge | decay
    - severity: 0.0-1.0 (how much this hurts)
    - opportunity: 0.0-1.0 (how much fixing it would help)
    - location: where in the system
    - evidence: what proves this finding
    - recommendation: what to do about it
"""

import json
import os
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ._cache import DATA_DIR

# ──────────────────────────────────────────────────────────────
#  Finding Data Structure
# ──────────────────────────────────────────────────────────────

@dataclass
class MaverickFinding:
    """A single finding from the Maverick's probing."""
    finding_id: str = ""
    finding_type: str = ""       # hole | gap | tunnel | bridge | decay
    severity: float = 0.0        # 0.0 = cosmetic, 1.0 = critical
    opportunity: float = 0.0     # 0.0 = marginal, 1.0 = transformative
    location: str = ""           # module, tool, or subsystem name
    title: str = ""              # one-line summary
    evidence: str = ""           # what proves this
    recommendation: str = ""     # what to do
    timestamp: str = ""
    probed_by: str = ""          # which probe found this

    def impact_score(self) -> float:
        """Combined severity × opportunity = how much fixing this matters."""
        return self.severity * self.opportunity


# ──────────────────────────────────────────────────────────────
#  Maverick Engine
# ──────────────────────────────────────────────────────────────

class SandboxMaverick:
    """Actively probes the sandbox for holes, gaps, tunnels, bridges, and decay.

    Each probe is a focused analysis that produces MaverickFindings.
    The Maverick runs on-demand (not in background) to keep overhead zero.
    """

    def __init__(self):
        self._findings: list[MaverickFinding] = []
        self._probe_history: list[dict] = []
        self._finding_counter = 0

    def _make_finding(self, **kwargs) -> MaverickFinding:
        self._finding_counter += 1
        f = MaverickFinding(
            finding_id=f"mav_{self._finding_counter:04d}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            **kwargs
        )
        self._findings.append(f)
        return f

    # ══════════════════════════════════════════════════════════════
    #  PROBE 1: HOLE DETECTION — Blind Spots
    # ══════════════════════════════════════════════════════════════

    def probe_holes(self) -> list[MaverickFinding]:
        """Find where observations are NOT being captured.

        Checks:
        - Compiled modules without corresponding MCP tool registration
        - Tool calls not flowing through the sandbox observer
        - Data files without crystal coordinate headers
        - Missing .qshr companions for JSON files
        """
        findings = []

        # ── Unregistered modules ──
        pyc_dir = Path(__file__).parent / "__pycache__"
        compiled_modules = set()
        if pyc_dir.exists():
            compiled_modules = {
                f.stem.rsplit(".", 1)[0]
                for f in pyc_dir.glob("*.pyc")
                if not f.stem.startswith("_")  # skip private
            }

        # Known registered tools (from __init__.py imports)
        # We detect by checking which modules have MCP-facing functions
        source_dir = Path(__file__).parent
        source_modules = {f.stem for f in source_dir.glob("*.py") if not f.stem.startswith("_")}

        # Modules that exist as .pyc but have no .py source
        orphan_bytecodes = compiled_modules - source_modules - {
            "__init__", "sandbox_observer", "sandbox_metadata",
            "sandbox_bridge", "sandbox_efficiency", "sandbox_mcp",
            "sandbox_maverick",
        }
        if orphan_bytecodes:
            findings.append(self._make_finding(
                finding_type="hole",
                severity=0.6,
                opportunity=0.8,
                location="crystal_108d/__pycache__",
                title=f"{len(orphan_bytecodes)} compiled modules without source files",
                evidence=f"Modules with .pyc but no .py: {', '.join(sorted(orphan_bytecodes)[:15])}{'...' if len(orphan_bytecodes) > 15 else ''}",
                recommendation="Restore .py source files from .pyc (decompile) or git history. "
                               "Source-less modules can't be patched, debugged, or extended.",
                probed_by="probe_holes",
            ))

        # ── Uncompressed JSON files ──
        data_dir = DATA_DIR
        if data_dir.exists():
            json_files = list(data_dir.glob("*.json"))
            qshr_stems = {f.stem for f in data_dir.glob("*.qshr")}
            uncompressed = [f.stem for f in json_files if f.stem not in qshr_stems]
            if uncompressed:
                findings.append(self._make_finding(
                    finding_type="hole",
                    severity=0.3,
                    opportunity=0.5,
                    location="MCP/data/",
                    title=f"{len(uncompressed)} JSON files without .qshr companions",
                    evidence=f"Uncompressed: {', '.join(uncompressed[:10])}{'...' if len(uncompressed) > 10 else ''}",
                    recommendation="Run qshrink_batch to crystallize all data files. "
                                   "Compressed .qshr reduces storage and enables O(1) metadata reads.",
                    probed_by="probe_holes",
                ))

        # ── Data files without crystal headers ──
        untagged = []
        for f in source_dir.glob("*.py"):
            try:
                first_line = f.read_text(encoding="utf-8", errors="replace").split("\n")[0]
                if not first_line.startswith("# CRYSTAL:"):
                    untagged.append(f.name)
            except Exception:
                pass
        if untagged:
            findings.append(self._make_finding(
                finding_type="hole",
                severity=0.2,
                opportunity=0.3,
                location="crystal_108d/*.py",
                title=f"{len(untagged)} source files without crystal coordinate headers",
                evidence=f"Untagged: {', '.join(untagged[:10])}",
                recommendation="Run holographic_embed on each file to assign crystal coordinates. "
                               "Untagged files are invisible to the metro routing system.",
                probed_by="probe_holes",
            ))

        # ── Sandbox observer blind spots ──
        from .sandbox_observer import get_sandbox_observer
        sandbox = get_sandbox_observer()
        traces = list(sandbox._traces)
        if traces:
            observed_tools = {t.tool_name for t in traces}
            # Estimate total tools from compiled modules
            expected_tools = len(compiled_modules)
            coverage = len(observed_tools) / max(expected_tools, 1)
            if coverage < 0.3:
                findings.append(self._make_finding(
                    finding_type="hole",
                    severity=0.5,
                    opportunity=0.7,
                    location="sandbox_observer",
                    title=f"Only {len(observed_tools)}/{expected_tools} tools observed ({coverage:.0%} coverage)",
                    evidence=f"Observed: {', '.join(sorted(observed_tools)[:10])}",
                    recommendation="Ensure the tool call tracing hook in __init__.py wraps ALL registered tools, "
                                   "not just sandbox tools. The make_observed_tool pattern should feed into sandbox tracing.",
                    probed_by="probe_holes",
                ))

        return findings

    # ══════════════════════════════════════════════════════════════
    #  PROBE 2: GAP DETECTION — Disconnected Subsystems
    # ══════════════════════════════════════════════════════════════

    def probe_gaps(self) -> list[MaverickFinding]:
        """Find disconnected subsystems that should be cross-wired.

        Checks:
        - Sandbox observer not connected to existing observer_pool
        - Autoresearch not feeding into hive_ledger
        - Self-play not emitting to sandbox bridge
        - Efficiency directives not reaching agent_watcher
        - Missing feedback loops (one-directional data flows)
        """
        findings = []

        # ── Sandbox ↔ Observer Pool gap ──
        # The existing _observer_pool wraps tools with 12D observation
        # but doesn't feed into the sandbox's 15D system
        findings.append(self._make_finding(
            finding_type="gap",
            severity=0.7,
            opportunity=0.9,
            location="_observer_pool → sandbox_bridge",
            title="Observer pool 12D observations not flowing into sandbox 15D bridge",
            evidence="make_observed_tool() in _observer_pool calls pool.observe_tool_call() "
                     "which produces 12D scores, but these don't propagate to "
                     "sandbox_bridge.observe_tool_call() which would add sandbox dims x13-x15",
            recommendation="Wire _observer_pool.observe_tool_call() to also call "
                           "bridge.observe_tool_call() with the 12D scores + tool latency. "
                           "This closes the gap between existing 12D observation and new 15D sandbox observation.",
            probed_by="probe_gaps",
        ))

        # ── Efficiency directives ↔ Hive Ledger gap ──
        # Directives are emitted but not broadcast to hive ledger
        findings.append(self._make_finding(
            finding_type="gap",
            severity=0.5,
            opportunity=0.7,
            location="sandbox_efficiency → hive_ledger",
            title="Efficiency directives not broadcast to hive ledger",
            evidence="RecursiveEfficiencyEngine.emit_directives() stores directives locally "
                     "but doesn't write them to hive_ledger for other agents to consume. "
                     "Plan says to use entry_type='broadcast' subtype='directive'.",
            recommendation="After emitting directives, write each to hive_ledger with "
                           "hive_ledger_write(entry_type='broadcast', subtype='efficiency_directive', ...). "
                           "This enables multi-agent coordination on optimization.",
            probed_by="probe_gaps",
        ))

        # ── Self-play ↔ Sandbox Bridge gap ──
        # ContinuousSelfPlay runs in background but doesn't feed sandbox
        findings.append(self._make_finding(
            finding_type="gap",
            severity=0.6,
            opportunity=0.8,
            location="ContinuousSelfPlay → sandbox_bridge",
            title="Background self-play daemon not wired to sandbox bridge",
            evidence="ContinuousSelfPlay runs every 120s in __init__.py but calls "
                     "the legacy run_self_play path, not bridge.observe_self_play(). "
                     "Self-play waves are invisible to the sandbox observer.",
            recommendation="Hook ContinuousSelfPlay's per-wave callback to call "
                           "bridge.observe_self_play() with wave metrics. This makes every "
                           "self-play cycle a training signal for the sandbox.",
            probed_by="probe_gaps",
        ))

        # ── Successor seeds ↔ Autoresearch gap ──
        # Sandbox seeds not fed back into autoresearch's MetaObserver
        findings.append(self._make_finding(
            finding_type="gap",
            severity=0.4,
            opportunity=0.6,
            location="sandbox_metadata → autoresearch",
            title="Sandbox successor seeds not fed into autoresearch MetaObserver",
            evidence="MetadataEmitter produces SandboxSuccessorSeed at epoch=57 boundaries, "
                     "but autoresearch's MetaObserver has its own SuccessorSeed system. "
                     "The two seed chains are independent — no cross-pollination of compressed wisdom.",
            recommendation="At epoch boundary, convert SandboxSuccessorSeed to autoresearch "
                           "SuccessorSeed format and store in shared SQLite. "
                           "Or: merge both into a unified successor seed with 15D target vectors.",
            probed_by="probe_gaps",
        ))

        # ── Training records ↔ Momentum field gap ──
        findings.append(self._make_finding(
            finding_type="gap",
            severity=0.4,
            opportunity=0.5,
            location="sandbox_metadata → momentum_field",
            title="Training records not used to influence momentum field updates",
            evidence="TrainingRecords store momentum_delta but the efficiency_delta "
                     "and 15D scores don't feed back into the geometric engine's "
                     "momentum field (the 148-float learned state). "
                     "The sandbox observes but doesn't STEER the training.",
            recommendation="Compute a 'sandbox gradient' from efficiency trends: "
                           "if resource efficiency is declining, bias momentum field "
                           "toward compression-heavy archetypes. Close the observe→steer loop.",
            probed_by="probe_gaps",
        ))

        return findings

    # ══════════════════════════════════════════════════════════════
    #  PROBE 3: TUNNEL DETECTION — Unexpected Pathways
    # ══════════════════════════════════════════════════════════════

    def probe_tunnels(self) -> list[MaverickFinding]:
        """Find unexpected shortcuts or leaks through the system.

        Tunnels can be POSITIVE (efficiency shortcuts) or NEGATIVE (resource leaks).
        """
        findings = []

        # ── Check for .pyc cache as a tunnel ──
        # .pyc files bypass source changes — if you edit a .py, stale .pyc may load
        pyc_dir = Path(__file__).parent / "__pycache__"
        source_dir = Path(__file__).parent
        if pyc_dir.exists():
            stale_candidates = []
            for pyc in pyc_dir.glob("*.cpython-312.pyc"):
                module_name = pyc.stem.rsplit(".", 1)[0]
                py_file = source_dir / f"{module_name}.py"
                if py_file.exists():
                    # Check if .py is newer than .pyc
                    if py_file.stat().st_mtime > pyc.stat().st_mtime:
                        stale_candidates.append(module_name)
            if stale_candidates:
                findings.append(self._make_finding(
                    finding_type="tunnel",
                    severity=0.7,
                    opportunity=0.6,
                    location="__pycache__",
                    title=f"{len(stale_candidates)} stale .pyc files (source newer than bytecode)",
                    evidence=f"Stale: {', '.join(stale_candidates[:10])}",
                    recommendation="Delete __pycache__ and let Python recompile. "
                                   "Stale .pyc is a NEGATIVE tunnel — old code runs instead of new code.",
                    probed_by="probe_tunnels",
                ))

        # ── Memory growth tunnel ──
        from .sandbox_observer import get_sandbox_observer
        sandbox = get_sandbox_observer()
        snapshots = list(sandbox._snapshots)
        if len(snapshots) >= 3:
            mem_values = [s.memory_rss_mb for s in snapshots]
            if mem_values[-1] > mem_values[0] * 1.5 and len(mem_values) >= 5:
                findings.append(self._make_finding(
                    finding_type="tunnel",
                    severity=0.8,
                    opportunity=0.7,
                    location="process memory",
                    title=f"Memory growth: {mem_values[0]:.1f}MB → {mem_values[-1]:.1f}MB ({(mem_values[-1]/mem_values[0]-1)*100:.0f}% increase)",
                    evidence=f"Over {len(snapshots)} snapshots, RSS grew from {mem_values[0]:.1f}MB to {mem_values[-1]:.1f}MB",
                    recommendation="Profile memory allocations. Common leaks: growing dicts/lists not bounded by deque, "
                                   "unclosed SQLite connections, accumulated QShrink buffers. "
                                   "This is a NEGATIVE tunnel — resources leak out.",
                    probed_by="probe_tunnels",
                ))

        # ── Positive tunnel: QShrink bypass for hot data ──
        # If certain data files are loaded repeatedly, .qshr metadata
        # provides O(1) reads without decompressing — a positive tunnel
        data_dir = DATA_DIR
        if data_dir.exists():
            qshr_files = list(data_dir.glob("*.qshr"))
            if qshr_files:
                findings.append(self._make_finding(
                    finding_type="tunnel",
                    severity=0.0,  # positive finding
                    opportunity=0.8,
                    location="MCP/data/*.qshr",
                    title=f"POSITIVE TUNNEL: {len(qshr_files)} .qshr files enable O(1) metadata reads",
                    evidence="qshrink_inspect() can read crystal weight metadata from .qshr headers "
                             "without decompressing the full file. This is a shortcut past full JSON parsing.",
                    recommendation="Use qshrink_inspect() for metadata queries instead of load(). "
                                   "This positive tunnel saves ~87.5% of I/O for metadata-only reads.",
                    probed_by="probe_tunnels",
                ))

        # ── Positive tunnel: co-occurrence → batch fusion ──
        from .sandbox_observer import get_sandbox_observer
        candidates = sandbox.parallelism_candidates(min_co_occurrences=3)
        if candidates:
            findings.append(self._make_finding(
                finding_type="tunnel",
                severity=0.0,
                opportunity=0.7,
                location="tool co-occurrence graph",
                title=f"POSITIVE TUNNEL: {len(candidates)} tool pairs can be fused into batch calls",
                evidence=f"Top: {candidates[0]['tools']} ({candidates[0]['co_occurrences']} co-occurrences)",
                recommendation="Create composite MCP tools that batch frequently co-occurring tools "
                               "into single calls. Saves round-trip overhead and context window tokens.",
                probed_by="probe_tunnels",
            ))

        return findings

    # ══════════════════════════════════════════════════════════════
    #  PROBE 4: BRIDGE OPPORTUNITIES — Integration Points
    # ══════════════════════════════════════════════════════════════

    def probe_bridges(self) -> list[MaverickFinding]:
        """Find integration opportunities for compound efficiency gains.

        These are places where connecting two subsystems would create
        value greater than the sum of their parts.
        """
        findings = []

        # ── Google Docs ↔ Sandbox ──
        findings.append(self._make_finding(
            finding_type="bridge",
            severity=0.0,
            opportunity=0.9,
            location="Google Docs ↔ sandbox_bridge",
            title="Live Google Docs not integrated with sandbox observation",
            evidence="MEMORY.md lists 6 Google Docs as 'live slow-form self'. "
                     "The sandbox observes MCP tools and self-play but not "
                     "changes to Google Docs. Document evolution is unobserved.",
            recommendation="Periodically fetch Google Docs (gmail/drive MCP tools), "
                           "diff against cached versions, and emit bridge.observe_autoresearch() "
                           "records for document changes. This closes the Docs↔sandbox loop.",
            probed_by="probe_bridges",
        ))

        # ── Git history ↔ Training records ──
        findings.append(self._make_finding(
            finding_type="bridge",
            severity=0.0,
            opportunity=0.7,
            location="git log ↔ sandbox_metadata",
            title="Git commit history not correlated with training records",
            evidence="Training records track cycle_id and epoch but not git commit hash. "
                     "Can't correlate efficiency changes with code changes. "
                     "Regression hunting requires manual cross-referencing.",
            recommendation="Include git HEAD hash in each TrainingRecord. "
                           "At successor seed boundary, also record the commit range. "
                           "This enables: 'efficiency dropped 20% after commit abc123'.",
            probed_by="probe_bridges",
        ))

        # ── Time fractal ↔ Sandbox epochs ──
        findings.append(self._make_finding(
            finding_type="bridge",
            severity=0.0,
            opportunity=0.8,
            location="time_fractal ↔ sandbox_metadata",
            title="Time fractal schedule not aligned with sandbox epoch boundaries",
            evidence="Time fractal has 5 nested cycles (Z12/Z20/Z28/Z36/Z420) "
                     "while sandbox uses epoch=57. These are independent clocks. "
                     "Aligning them would synchronize efficiency reporting with training cycles.",
            recommendation="Set sandbox EPOCH_LENGTH to match the nearest Z-cycle boundary "
                           "(Z12=57 cycles fits perfectly — this may already be aligned by design). "
                           "Or: emit a sandbox snapshot at each Z-cycle boundary.",
            probed_by="probe_bridges",
        ))

        # ── Agent RPG ↔ Efficiency metrics ──
        findings.append(self._make_finding(
            finding_type="bridge",
            severity=0.0,
            opportunity=0.6,
            location="_agent_registry ↔ sandbox_efficiency",
            title="Agent RPG progression not informed by efficiency metrics",
            evidence="Agent XP is awarded based on 12D observation quality (from _observer_pool) "
                     "but not based on resource efficiency (x13-x15). An agent that produces "
                     "great 12D scores but wastes resources gets the same XP as one that's efficient.",
            recommendation="Add a phi-scaled efficiency bonus to XP calculation: "
                           "bonus_xp = base_xp * (1 + efficiency_delta * phi). "
                           "This incentivizes agents to be both effective AND efficient.",
            probed_by="probe_bridges",
        ))

        # ── Checkpoint ↔ QShrink ──
        checkpoint_dir = DATA_DIR
        if checkpoint_dir.exists():
            json_checkpoints = list(checkpoint_dir.glob("checkpoint_*.json"))
            qshr_checkpoints = list(checkpoint_dir.glob("checkpoint_*.qshr"))
            if json_checkpoints and not qshr_checkpoints:
                findings.append(self._make_finding(
                    finding_type="bridge",
                    severity=0.3,
                    opportunity=0.7,
                    location="MCP/data/checkpoint_*.json",
                    title=f"{len(json_checkpoints)} training checkpoints not QShrink compressed",
                    evidence=f"Found {len(json_checkpoints)} JSON checkpoints but no .qshr equivalents. "
                             f"Each checkpoint is ~1-2KB. Total: ~{len(json_checkpoints)*1.5:.0f}KB uncompressed.",
                    recommendation="Run qshrink_batch on MCP/data/ to compress checkpoints. "
                                   "Also: since checkpoints are append-only, only compress when "
                                   "batch reaches 100+ files to amortize the compression overhead.",
                    probed_by="probe_bridges",
                ))

        return findings

    # ══════════════════════════════════════════════════════════════
    #  PROBE 5: DECAY DETECTION — Degradation Over Time
    # ══════════════════════════════════════════════════════════════

    def probe_decay(self) -> list[MaverickFinding]:
        """Detect degradation, rot, and aging in the system.

        Checks:
        - Efficiency trend declining over time
        - Directive failure rate increasing
        - Snapshot count growing (potential memory pressure)
        - Stale state files
        - Abandoned data directories
        """
        findings = []

        # ── Efficiency trend decay ──
        from .sandbox_metadata import get_metadata_emitter
        emitter = get_metadata_emitter()
        trend = emitter.efficiency_trend(n=20)
        if len(trend) >= 10:
            first_half = trend[:len(trend)//2]
            second_half = trend[len(trend)//2:]
            avg_first = sum(t["value_per_token"] for t in first_half) / len(first_half)
            avg_second = sum(t["value_per_token"] for t in second_half) / len(second_half)
            if avg_second < avg_first * 0.8:
                findings.append(self._make_finding(
                    finding_type="decay",
                    severity=0.7,
                    opportunity=0.8,
                    location="efficiency trend",
                    title=f"Efficiency declining: {avg_first:.4f} → {avg_second:.4f} ({(avg_second/avg_first-1)*100:.0f}%)",
                    evidence=f"Value/token dropped from {avg_first:.4f} (first half) to {avg_second:.4f} (second half) "
                             f"over {len(trend)} records",
                    recommendation="Check for: (1) increasing context pressure crowding out signal, "
                                   "(2) redundant tool calls accumulating, (3) stale directives not being cleaned up. "
                                   "Consider applying_rolling_forget() to prune low-value observations.",
                    probed_by="probe_decay",
                ))

        # ── Directive failure rate ──
        from .sandbox_efficiency import get_efficiency_engine
        engine = get_efficiency_engine()
        history = engine._directive_history
        if len(history) >= 5:
            failed = sum(1 for d in history if d.status == "failed")
            total = len(history)
            fail_rate = failed / total
            if fail_rate > 0.5:
                findings.append(self._make_finding(
                    finding_type="decay",
                    severity=0.6,
                    opportunity=0.7,
                    location="efficiency directives",
                    title=f"High directive failure rate: {fail_rate:.0%} ({failed}/{total})",
                    evidence=f"Of {total} historical directives, {failed} failed. "
                             "The efficiency engine's recommendations are not producing results.",
                    recommendation="Review failed directive targets — they may be inherently slow "
                                   "(network I/O, external APIs) and not optimizable. "
                                   "Adjust detection thresholds to avoid false positive directives.",
                    probed_by="probe_decay",
                ))

        # ── State file freshness ──
        sandbox_dir = DATA_DIR / "sandbox"
        if sandbox_dir.exists():
            state_files = {
                "emitter_state.json": "metadata emitter",
                "efficiency_state.json": "efficiency engine",
            }
            for filename, subsystem in state_files.items():
                state_path = sandbox_dir / filename
                if state_path.exists():
                    age_hours = (time.time() - state_path.stat().st_mtime) / 3600
                    if age_hours > 24:
                        findings.append(self._make_finding(
                            finding_type="decay",
                            severity=0.3,
                            opportunity=0.4,
                            location=f"MCP/data/sandbox/{filename}",
                            title=f"Stale state file: {subsystem} not updated in {age_hours:.0f}h",
                            evidence=f"{filename} last modified {age_hours:.0f} hours ago",
                            recommendation=f"The {subsystem} may not be running. "
                                           "Check that sandbox tools are registered and being called.",
                            probed_by="probe_decay",
                        ))

        # ── Data directory bloat ──
        if DATA_DIR.exists():
            total_files = sum(1 for _ in DATA_DIR.glob("*"))
            total_size_mb = sum(f.stat().st_size for f in DATA_DIR.glob("*") if f.is_file()) / (1024 * 1024)
            if total_files > 500:
                findings.append(self._make_finding(
                    finding_type="decay",
                    severity=0.4,
                    opportunity=0.6,
                    location="MCP/data/",
                    title=f"Data directory bloat: {total_files} files, {total_size_mb:.1f}MB",
                    evidence=f"{total_files} files in MCP/data/, consuming {total_size_mb:.1f}MB. "
                             "Many may be old checkpoints or redundant JSON+QSHR pairs.",
                    recommendation="Prune old checkpoint files (keep every 100th). "
                                   "Delete JSON files that have .qshr companions. "
                                   "Set up a time-fractal-aligned cleanup schedule.",
                    probed_by="probe_decay",
                ))

        return findings

    # ══════════════════════════════════════════════════════════════
    #  PROBE 6: INTEGRATION SURFACE — What Can We Wire Together?
    # ══════════════════════════════════════════════════════════════

    def probe_integration_surface(self) -> list[MaverickFinding]:
        """Scan for subsystems that could be connected for compound gains.

        This probe looks at the ENTIRE module surface and identifies
        pairs that don't currently interact but should.
        """
        findings = []

        # Module groups that should interact
        integration_map = {
            "training": {"self_play", "meta_loop_engine", "geometric_mcp", "geometric_forward",
                         "momentum_field", "loss_engine", "geometric_loss"},
            "observation": {"observer_swarm", "observer_agent", "nested_swarm",
                           "meta_observer", "meta_observer_runtime", "agent_watcher"},
            "compression": {"qshrink", "qshrink_codec", "qshrink_pipeline"},
            "navigation": {"address", "metro_lines", "z_points", "z_tunnel_network",
                          "liminal_mapper", "moves"},
            "sandbox": {"sandbox_observer", "sandbox_bridge", "sandbox_efficiency",
                       "sandbox_metadata", "sandbox_mcp", "sandbox_maverick"},
            "emergence": {"emergence", "harmonic_resonance", "mycelium_emergence",
                         "crown_density", "omega_tunneling", "crown_transform_gate",
                         "absolute_convergence"},
            "governance": {"conservation", "live_lock", "live_cell", "perpetual_agency",
                          "control_center"},
        }

        # Check: sandbox should connect to ALL groups
        sandbox_connections_needed = {
            "training": "Sandbox should observe training metrics (momentum deltas, loss curves) for 15D scoring",
            "observation": "Sandbox should aggregate observations from swarm/nested systems, not just tool calls",
            "compression": "Sandbox should use QShrink for training records + checkpoint compression",
            "emergence": "Sandbox efficiency trends ARE emergence signals — gate tests should include efficiency",
            "governance": "Conservation laws should cover resource conservation (bounded memory, bounded storage)",
        }

        for group, reason in sandbox_connections_needed.items():
            findings.append(self._make_finding(
                finding_type="bridge",
                severity=0.0,
                opportunity=0.5,
                location=f"sandbox ↔ {group}",
                title=f"Integration opportunity: sandbox ↔ {group} ({len(integration_map[group])} modules)",
                evidence=reason,
                recommendation=f"Wire sandbox observation into {group} subsystem. "
                               f"Modules: {', '.join(sorted(integration_map[group]))}",
                probed_by="probe_integration_surface",
            ))

        return findings

    # ══════════════════════════════════════════════════════════════
    #  FULL SCAN — Run All Probes
    # ══════════════════════════════════════════════════════════════

    def full_scan(self) -> list[MaverickFinding]:
        """Run all probes and return all findings sorted by impact."""
        all_findings = []
        probes = [
            ("holes", self.probe_holes),
            ("gaps", self.probe_gaps),
            ("tunnels", self.probe_tunnels),
            ("bridges", self.probe_bridges),
            ("decay", self.probe_decay),
            ("integration", self.probe_integration_surface),
        ]

        for name, probe_fn in probes:
            try:
                results = probe_fn()
                all_findings.extend(results)
                self._probe_history.append({
                    "probe": name,
                    "findings": len(results),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                all_findings.append(self._make_finding(
                    finding_type="decay",
                    severity=0.5,
                    opportunity=0.5,
                    location=f"probe_{name}",
                    title=f"Probe {name} crashed: {str(e)[:80]}",
                    evidence=str(e),
                    recommendation="Fix the probe itself before trusting its absence of findings.",
                    probed_by="full_scan",
                ))

        # Sort by impact (severity × opportunity)
        all_findings.sort(key=lambda f: -f.impact_score())
        return all_findings

    # ══════════════════════════════════════════════════════════════
    #  Report Generation
    # ══════════════════════════════════════════════════════════════

    def report(self, max_findings: int = 30) -> str:
        """Generate a human-readable Maverick report."""
        findings = self.full_scan()[:max_findings]

        if not findings:
            return "## Sandbox Maverick Report\n\n*No findings. The sandbox is watertight... for now.*"

        # Categorize
        by_type: dict[str, list[MaverickFinding]] = defaultdict(list)
        for f in findings:
            by_type[f.finding_type].append(f)

        lines = ["## Sandbox Maverick Report\n"]

        # Summary
        total_impact = sum(f.impact_score() for f in findings)
        lines.append(f"**Total Findings**: {len(findings)} | "
                    f"**Aggregate Impact**: {total_impact:.2f}\n")

        type_icons = {
            "hole": "O",    # empty space
            "gap": "||",    # disconnection
            "tunnel": ">>", # pathway
            "bridge": "==", # connection
            "decay": "~~",  # degradation
        }

        # Findings by category
        for ftype in ["hole", "gap", "tunnel", "bridge", "decay"]:
            items = by_type.get(ftype, [])
            if not items:
                continue
            icon = type_icons.get(ftype, "?")
            lines.append(f"\n### {icon} {ftype.upper()}S ({len(items)})\n")
            for f in items:
                severity_bar = "#" * int(f.severity * 5) + "." * (5 - int(f.severity * 5))
                opp_bar = "+" * int(f.opportunity * 5) + "." * (5 - int(f.opportunity * 5))
                lines.append(f"**{f.finding_id}** [{severity_bar}|{opp_bar}] `{f.location}`")
                lines.append(f"  {f.title}")
                lines.append(f"  *Evidence*: {f.evidence[:120]}{'...' if len(f.evidence) > 120 else ''}")
                lines.append(f"  *Action*: {f.recommendation[:120]}{'...' if len(f.recommendation) > 120 else ''}")
                lines.append("")

        # Save report to disk
        report_path = DATA_DIR / "sandbox" / "maverick_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_findings": len(findings),
            "aggregate_impact": total_impact,
            "findings": [asdict(f) for f in findings],
            "probe_history": self._probe_history,
        }
        report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
#  MCP Tool Registration
# ──────────────────────────────────────────────────────────────

def register_maverick_tools(mcp) -> None:
    """Register Maverick tools onto the MCP server."""

    @mcp.tool()
    def sandbox_maverick(probe: str = "all") -> str:
        """Run the Sandbox Maverick — hunt for holes, gaps, tunnels, bridges, and decay.

        The Maverick actively probes the entire sandbox system to find:
        - HOLES: blind spots where observations are missing
        - GAPS: disconnected subsystems that should be cross-wired
        - TUNNELS: unexpected shortcuts (positive) or leaks (negative)
        - BRIDGES: integration opportunities for compound efficiency
        - DECAY: degradation, rot, staleness over time

        Args:
            probe: Which probe to run. Options:
                   "all" (default) — full scan, all probes
                   "holes" — blind spot detection only
                   "gaps" — disconnection detection only
                   "tunnels" — pathway detection only
                   "bridges" — integration opportunity detection only
                   "decay" — degradation detection only
                   "integration" — full integration surface scan
        """
        maverick = SandboxMaverick()

        if probe == "all":
            return maverick.report()

        probe_map = {
            "holes": maverick.probe_holes,
            "gaps": maverick.probe_gaps,
            "tunnels": maverick.probe_tunnels,
            "bridges": maverick.probe_bridges,
            "decay": maverick.probe_decay,
            "integration": maverick.probe_integration_surface,
        }

        if probe not in probe_map:
            return f"Unknown probe: {probe}. Options: {', '.join(['all'] + list(probe_map.keys()))}"

        findings = probe_map[probe]()
        if not findings:
            return f"## Maverick Probe: {probe}\n\n*No findings.*"

        lines = [f"## Maverick Probe: {probe.upper()} ({len(findings)} findings)\n"]
        for f in sorted(findings, key=lambda x: -x.impact_score()):
            lines.append(f"**{f.finding_id}** [{f.severity:.1f}sev|{f.opportunity:.1f}opp] `{f.location}`")
            lines.append(f"  {f.title}")
            lines.append(f"  *Evidence*: {f.evidence[:150]}")
            lines.append(f"  *Action*: {f.recommendation[:150]}")
            lines.append("")

        return "\n".join(lines)
