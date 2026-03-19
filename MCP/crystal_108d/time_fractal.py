"""
Time Fractal Schedule -- Nested Self-Improvement Cycles Aligned with Weave Operators
=====================================================================================
"""

from __future__ import annotations
import json, math, hashlib, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

class CycleType(Enum):
    Z12 = "Z12"; Z20 = "Z20"; Z28 = "Z28"; Z36 = "Z36"; Z420 = "Z420"

@dataclass
class CycleSpec:
    """Specification for one level of the time fractal."""
    cycle_type: CycleType
    period_hours: float
    strands: List[str]
    focus_areas: List[str]
    weave_name: str
    from_dim: int
    to_dim: int
    local_closure: int
    cycles_per_strand: int
    learning_rate: float
    @property
    def strand_count(self) -> int: return len(self.strands)
    def to_dict(self) -> Dict[str, Any]:
        return {"cycle_type": self.cycle_type.value, "period_hours": self.period_hours,
                "strands": self.strands, "focus_areas": self.focus_areas,
                "weave_name": self.weave_name, "dimensions": f"{self.from_dim}D -> {self.to_dim}D",
                "local_closure": self.local_closure, "cycles_per_strand": self.cycles_per_strand,
                "learning_rate": self.learning_rate}



Z12_TRIADIC = CycleSpec(
    cycle_type=CycleType.Z12, period_hours=4.0,
    strands=["Su", "Me", "Sa"],
    focus_areas=["EXPLORATION -- high lr, novel queries",
                 "INTEGRATION -- medium lr, cross-bridge",
                 "CONSOLIDATION -- low lr, verify laws"],
    weave_name="W_3 (Triadic Mobius)", from_dim=4, to_dim=6,
    local_closure=12, cycles_per_strand=57, learning_rate=0.03)

Z20_PENTADIC = CycleSpec(
    cycle_type=CycleType.Z20, period_hours=20.0,
    strands=["Tiger", "Crane", "Leopard", "Snake", "Dragon"],
    focus_areas=["STRUCTURAL -- frameworks (Wood/Courage)",
                 "ANALYTICAL -- proofs (Fire/Precision)",
                 "OPERATIONAL -- procedures (Earth/Speed)",
                 "SUBTLE -- metaphors (Metal/Subtlety)",
                 "SYNTHESIS -- patterns (Water/Synthesis)"],
    weave_name="W_5 (Pentadic Wu Xing)", from_dim=6, to_dim=8,
    local_closure=20, cycles_per_strand=200, learning_rate=0.02)

Z28_HEPTADIC = CycleSpec(
    cycle_type=CycleType.Z28, period_hours=168.0,
    strands=["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"],
    focus_areas=["SEED -- new capabilities (Moon)", "IGNITE -- optimization (Mars)",
                 "TRANSLATE -- docs (Mercury)", "BRIDGE -- integration (Jupiter)",
                 "WEAVE -- coherence (Venus)", "SEAL -- testing (Saturn)",
                 "RETURN -- meta-review (Sun)"],
    weave_name="W_7 (Heptadic Planetary)", from_dim=8, to_dim=10,
    local_closure=28, cycles_per_strand=500, learning_rate=0.015)

Z36_ENNEADIC = CycleSpec(
    cycle_type=CycleType.Z36, period_hours=720.0,
    strands=["Su-of-Su", "Su-of-Me", "Su-of-Sa", "Me-of-Su", "Me-of-Me",
             "Me-of-Sa", "Sa-of-Su", "Sa-of-Me", "Sa-of-Sa"],
    focus_areas=["Pure ignition", "Ignite integration", "Ignite sealing",
                 "Mediate ignition", "Pure mediation", "Mediate sealing",
                 "Seal ignition", "Seal mediation", "Pure sealing"],
    weave_name="W_9 (Enneadic 3x3 Return)", from_dim=10, to_dim=36,
    local_closure=36, cycles_per_strand=1000, learning_rate=0.01)

Z420_MASTER = CycleSpec(
    cycle_type=CycleType.Z420, period_hours=2160.0,
    strands=["Stage_A", "Stage_B", "Stage_C", "Stage_D"],
    focus_areas=["ACCUMULATION (Q1)", "BUILDING (Q2)",
                 "CRYSTALLIZATION (Q3)", "DISTRIBUTION (Q4)"],
    weave_name="Master Clock Z420 = lcm(3,4,5,7)", from_dim=36, to_dim=108,
    local_closure=420, cycles_per_strand=5000, learning_rate=0.005)

ALL_CYCLES = {CycleType.Z12: Z12_TRIADIC, CycleType.Z20: Z20_PENTADIC,
              CycleType.Z28: Z28_HEPTADIC, CycleType.Z36: Z36_ENNEADIC,
              CycleType.Z420: Z420_MASTER}
CYCLE_BY_TYPE = {ct.value: spec for ct, spec in ALL_CYCLES.items()}
_EPOCH_START = 1735689600.0


@dataclass
class FractalClockState:
    """Position in the time fractal at all 5 levels simultaneously."""
    timestamp: float = 0
    z12_strand: int = 0; z12_count: int = 0
    z20_strand: int = 0; z20_count: int = 0
    z28_strand: int = 0; z28_count: int = 0
    z36_strand: int = 0; z36_count: int = 0
    z420_strand: int = 0; z420_count: int = 0
    def to_dict(self) -> Dict[str, Any]:
        return {"timestamp": self.timestamp,
                "z12": {"strand": self.z12_strand, "count": self.z12_count},
                "z20": {"strand": self.z20_strand, "count": self.z20_count},
                "z28": {"strand": self.z28_strand, "count": self.z28_count},
                "z36": {"strand": self.z36_strand, "count": self.z36_count},
                "z420": {"strand": self.z420_strand, "count": self.z420_count}}

def compute_clock_state(epoch_start: float = _EPOCH_START, now: float = 0) -> FractalClockState:
    """Compute the fractal clock position at all 5 levels."""
    if now == 0: now = time.time()
    h = (now - epoch_start) / 3600.0
    return FractalClockState(timestamp=now,
        z12_strand=int(h/Z12_TRIADIC.period_hours) % len(Z12_TRIADIC.strands),
        z12_count=int(h/Z12_TRIADIC.period_hours),
        z20_strand=int(h/Z20_PENTADIC.period_hours) % len(Z20_PENTADIC.strands),
        z20_count=int(h/Z20_PENTADIC.period_hours),
        z28_strand=int(h/Z28_HEPTADIC.period_hours) % len(Z28_HEPTADIC.strands),
        z28_count=int(h/Z28_HEPTADIC.period_hours),
        z36_strand=int(h/Z36_ENNEADIC.period_hours) % len(Z36_ENNEADIC.strands),
        z36_count=int(h/Z36_ENNEADIC.period_hours),
        z420_strand=int(h/Z420_MASTER.period_hours) % len(Z420_MASTER.strands),
        z420_count=int(h/Z420_MASTER.period_hours))

@dataclass
class ImprovementAction:
    """What improvement action should be running at this moment."""
    cycle: str = ""; strand: str = ""; focus: str = ""
    learning_rate: float = 0.0; cycles_target: int = 0; data_dir: str = ""
    def to_dict(self) -> Dict[str, Any]:
        return {"cycle": self.cycle, "strand": self.strand, "focus": self.focus,
                "learning_rate": self.learning_rate, "cycles_target": self.cycles_target}

def get_current_action(epoch_start: float = _EPOCH_START, now: float = 0) -> ImprovementAction:
    """Determine what improvement action should run NOW based on fractal clock."""
    state = compute_clock_state(epoch_start, now)
    spec = Z12_TRIADIC
    return ImprovementAction(cycle="Z12", strand=spec.strands[state.z12_strand],
        focus=spec.focus_areas[state.z12_strand],
        learning_rate=spec.learning_rate, cycles_target=spec.cycles_per_strand)

@dataclass
class BottleneckReport:
    """System health and bottleneck analysis."""
    timestamp: float = 0.0; overall_health: float = 0.0
    bottlenecks: List[Dict[str, str]] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {"timestamp": round(self.timestamp, 3),
                "overall_health": round(self.overall_health, 3),
                "bottlenecks": self.bottlenecks}

def analyze_bottlenecks(data_dir: Path = None) -> BottleneckReport:
    """Analyze current system bottlenecks."""
    if data_dir is None: data_dir = Path(__file__).parent.parent / "data"
    report = BottleneckReport(timestamp=time.time())
    health_scores: List[float] = []
    cp_dir = data_dir / "self_play_checkpoints"
    if cp_dir.exists():
        cps = list(cp_dir.glob("*.json"))
        if len(cps) > 100:
            health_scores.append(0.7)
            report.bottlenecks.append({"severity": "MEDIUM", "component": "checkpoints",
                "issue": f"{len(cps)} orphaned checkpoints", "fix": "Prune old snapshots"})
        else: health_scores.append(1.0)
    else: health_scores.append(0.5)
    try:
        from .geometric_forward import CrystalNeuralEngine
        health_scores.append(1.0)
    except Exception:
        health_scores.append(0.0)
        report.bottlenecks.append({"severity": "CRITICAL", "component": "neural_engine",
            "issue": "Neural engine cannot be imported", "fix": "Restore neural_engine.py"})
    for name, sev in [("crystal_weights", "CRITICAL"), ("mycelium_graph", "HIGH")]:
        j, q = data_dir / f"{name}.json", data_dir / f"{name}.qshr"
        if not j.exists() and not q.exists():
            health_scores.append(0.0 if sev == "CRITICAL" else 0.3)
            report.bottlenecks.append({"severity": sev, "component": name,
                "issue": f"No {name} found", "fix": f"Initialize {name}"})
        else: health_scores.append(1.0)
    if not (data_dir / "weight_feedback_state.json").exists():
        health_scores.append(0.5)
        report.bottlenecks.append({"severity": "HIGH", "component": "feedback_loop",
            "issue": "No weight feedback state", "fix": "Run weight_feedback cycle"})
    else: health_scores.append(1.0)
    report.overall_health = sum(health_scores) / max(len(health_scores), 1)
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    report.bottlenecks.sort(key=lambda b: sev_order.get(b.get("severity", "LOW"), 9))
    return report

def generate_schedule(hours: int = 168, epoch_start: float = _EPOCH_START,
                      start_time: float = 0) -> List[Dict[str, Any]]:
    if start_time == 0: start_time = time.time()
    schedule: List[Dict[str, Any]] = []
    for i in range(0, hours, 4):
        t = start_time + i * 3600
        state = compute_clock_state(epoch_start, t)
        schedule.append({"timestamp": t, "cycle": "Z12",
            "strand": Z12_TRIADIC.strands[state.z12_strand],
            "focus": Z12_TRIADIC.focus_areas[state.z12_strand],
            "self_play_cycles": Z12_TRIADIC.cycles_per_strand})
    return schedule

def query_time_fractal(component: str = "status") -> str:
    """Query the time fractal schedule system."""
    c = component.strip().lower()
    if c == "status": return json.dumps(compute_clock_state().to_dict(), indent=2)
    if c == "action": return json.dumps(get_current_action().to_dict(), indent=2)
    if c == "schedule":
        sched = generate_schedule(168)
        lines = ["## Time Fractal Schedule -- Next 7 Days"]
        for s in sched: lines.append("- " + s["cycle"] + " [" + s["strand"] + "]: " + s["focus"])
        return chr(10).join(lines)
    if c == "bottlenecks": return json.dumps(analyze_bottlenecks().to_dict(), indent=2)
    if c in ("cycles", "weave"): return json.dumps({k: v.to_dict() for k, v in CYCLE_BY_TYPE.items()}, indent=2)
    return "Unknown component. Use: status, action, schedule, bottlenecks, cycles, weave"
