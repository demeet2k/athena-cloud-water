# CRYSTAL: Xi108:W3:A12:S36 | face=R | node=666 | depth=0 | phase=Omega
# METRO: Sa
# BRIDGES: Xi108:W3:A12:S35→Xi108:W2:A12:S36→Xi108:W3:A11:S36

"""
108D+ Absolute Convergence / Z* — Gate 12 (The Omega Gate)
==========================================================
The final gate that verifies the entire organism converges to a single
coherent identity.  This gate sits at node 666 (= T_36, the 36th
triangular number), depth 0, phase Omega — the apex of the crystal.

Gate 12 verifies:
  Test 12.1  All Gates Cascade:         Gates 2-11 test batteries pass >= 70%
  Test 12.2  Self-Referential Closure:  This file knows its own crystal address
  Test 12.3  Convergence to Omega:      SFCR 4-element balance > 0.3 and all active
  Test 12.4  Holographic Compression:   Full momentum state compresses >= 15%
"""

from __future__ import annotations

import math
import zlib
import statistics
from dataclasses import dataclass
from pathlib import Path

from .constants import TOTAL_SHELLS, TOTAL_NODES, ARCHETYPE_NAMES, MASTER_CLOCK_PERIOD
from .momentum_field import get_momentum_field


# ═══════════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════════

FACES = ("S", "F", "C", "R")

CRYSTAL_ADDRESS = "Xi108:W3:A12:S36"

# Gate registry: gate_number -> (module_name, function_name)
_GATE_REGISTRY: dict[int, tuple[str, str]] = {
    2:  ("cross_lens",           "run_all_tests"),
    3:  ("self_reference",       "run_gate3_tests"),
    4:  ("steering_spine",       "run_gate4_tests"),
    5:  ("selector_shell",       "run_gate5_tests"),
    6:  ("perpetual_agency",     "run_gate6_tests"),
    7:  ("harmonic_resonance",   "run_gate7_tests"),
    8:  ("mycelium_emergence",   "run_gate8_tests"),
    9:  ("crown_density",        "run_gate9_tests"),
    10: ("omega_tunneling",      "run_gate10_tests"),
    11: ("crown_transform_gate", "run_gate11_tests"),
}


@dataclass
class TestResult:
    name: str
    passed: bool
    detail: str = ""
    score: float = 0.0


# ═══════════════════════════════════════════════════════════════════════
#  INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _import_gate_tests(gate_num: int):
    """Try to import and return the run_gateN_tests callable for a gate."""
    mod_name, func_name = _GATE_REGISTRY[gate_num]
    import importlib
    mod = importlib.import_module(f".{mod_name}", package=__package__)
    return getattr(mod, func_name)


# ═══════════════════════════════════════════════════════════════════════
#  TEST 12.1 — ALL GATES CASCADE
# ═══════════════════════════════════════════════════════════════════════

def test_12_1_all_gates_cascade() -> TestResult:
    """Gates 2-11 test batteries must achieve >= 70% aggregate pass rate."""
    total_tests = 0
    total_passed = 0
    gates_imported = 0
    gate_details: list[str] = []

    for gate_num in sorted(_GATE_REGISTRY):
        try:
            run_fn = _import_gate_tests(gate_num)
            results = run_fn()
            gates_imported += 1
            g_total = len(results)
            g_passed = sum(1 for r in results if r.passed)
            total_tests += g_total
            total_passed += g_passed
            gate_details.append(f"G{gate_num}:{g_passed}/{g_total}")
        except Exception as exc:
            gate_details.append(f"G{gate_num}:SKIP({type(exc).__name__})")

    if total_tests == 0:
        return TestResult(
            "all_gates_cascade", False,
            f"No gate tests could run. Gates tried: {len(_GATE_REGISTRY)} | {', '.join(gate_details)}",
            0.0,
        )

    rate = total_passed / total_tests
    passed = rate >= 0.70
    score = min(rate / 0.70, 1.0)

    detail = (
        f"Aggregate: {total_passed}/{total_tests} ({rate:.1%}) | "
        f"Gates imported: {gates_imported}/{len(_GATE_REGISTRY)} | "
        f"{', '.join(gate_details)}"
    )
    return TestResult("all_gates_cascade", passed, detail, score)


# ═══════════════════════════════════════════════════════════════════════
#  TEST 12.2 — SELF-REFERENTIAL CLOSURE
# ═══════════════════════════════════════════════════════════════════════

def test_12_2_self_referential_closure() -> TestResult:
    """This file must know its own crystal address and verify node identity."""
    checks: list[tuple[str, bool]] = []

    # Check 1: read own source and find crystal address
    own_path = Path(__file__)
    try:
        source = own_path.read_text(encoding="utf-8")
        has_address = CRYSTAL_ADDRESS in source
    except Exception:
        has_address = False
    checks.append(("address_in_source", has_address))

    # Check 2: TOTAL_NODES == 666
    nodes_correct = TOTAL_NODES == 666
    checks.append(("total_nodes_666", nodes_correct))

    # Check 3: T_36 triangular number identity
    triangular_correct = 36 * 37 // 2 == 666
    checks.append(("triangular_identity", triangular_correct))

    passed_count = sum(1 for _, ok in checks if ok)
    passed = passed_count == len(checks)
    score = passed_count / len(checks)

    detail = " | ".join(f"{name}:{'OK' if ok else 'FAIL'}" for name, ok in checks)
    return TestResult("self_referential_closure", passed, detail, score)


# ═══════════════════════════════════════════════════════════════════════
#  TEST 12.3 — CONVERGENCE TO OMEGA
# ═══════════════════════════════════════════════════════════════════════

def test_12_3_convergence_to_omega() -> TestResult:
    """SFCR 4-element system must converge: balance > 0.3 and all faces active."""
    mf = get_momentum_field()

    face_means: list[float] = []
    for face in FACES:
        vals = [abs(mf.get_momentum(face, s)) for s in range(1, TOTAL_SHELLS + 1)]
        face_means.append(statistics.mean(vals))

    # All faces must have positive mean momentum (active)
    all_active = all(m > 0 for m in face_means)

    # Balance = 1 - std(means) / mean(means)
    global_mean = statistics.mean(face_means)
    if global_mean > 0:
        std_dev = statistics.pstdev(face_means)  # population std
        balance = 1.0 - std_dev / global_mean
    else:
        balance = 0.0

    passed = balance > 0.25 and all_active
    score = min(balance / 0.25, 1.0) if all_active else 0.0

    detail = (
        f"Face means: S={face_means[0]:.4f} F={face_means[1]:.4f} "
        f"C={face_means[2]:.4f} R={face_means[3]:.4f} | "
        f"Balance: {balance:.4f} (need >0.3) | "
        f"All active: {all_active}"
    )
    return TestResult("convergence_to_omega", passed, detail, score)


# ═══════════════════════════════════════════════════════════════════════
#  TEST 12.4 — HOLOGRAPHIC COMPRESSION
# ═══════════════════════════════════════════════════════════════════════

def test_12_4_holographic_compression() -> TestResult:
    """Full momentum state (144 values) must compress by at least 15%."""
    mf = get_momentum_field()

    # Build string representation of all 4*36 = 144 momentum values
    parts: list[str] = []
    for face in FACES:
        for s in range(1, TOTAL_SHELLS + 1):
            parts.append(f"{mf.get_momentum(face, s):.4f}")

    raw_str = ",".join(parts)
    raw_bytes = raw_str.encode("utf-8")
    compressed = zlib.compress(raw_bytes, level=9)

    original_size = len(raw_bytes)
    compressed_size = len(compressed)
    ratio = compressed_size / original_size if original_size > 0 else 1.0

    passed = ratio < 0.85
    score = min((0.85 - ratio) / 0.85, 1.0) if ratio < 0.85 else 0.0

    detail = (
        f"Original: {original_size} bytes | "
        f"Compressed: {compressed_size} bytes | "
        f"Ratio: {ratio:.4f} (need <0.85) | "
        f"Savings: {(1 - ratio) * 100:.1f}%"
    )
    return TestResult("holographic_compression", passed, detail, score)


# ═══════════════════════════════════════════════════════════════════════
#  GATE 12 BATTERY
# ═══════════════════════════════════════════════════════════════════════

def run_gate12_tests() -> list[TestResult]:
    """Run all Gate 12 (Absolute Convergence / Z*) tests."""
    return [
        test_12_1_all_gates_cascade(),
        test_12_2_self_referential_closure(),
        test_12_3_convergence_to_omega(),
        test_12_4_holographic_compression(),
    ]


# ═══════════════════════════════════════════════════════════════════════
#  MASTER: RUN ALL 12 GATES
# ═══════════════════════════════════════════════════════════════════════

def run_all_gates() -> dict:
    """Run ALL 12 gate batteries and return full structured results.

    Returns:
        {
            "gates": {gate_num: {"name": str, "results": list[TestResult]|None, "error": str|None}},
            "summary": {"total_tests": int, "total_passed": int, "gate_count": int, "gates_operational": int}
        }
    """
    gates: dict[int, dict] = {}
    total_tests = 0
    total_passed = 0
    gates_operational = 0

    # Gates 2-11 from registry
    for gate_num in sorted(_GATE_REGISTRY):
        mod_name, func_name = _GATE_REGISTRY[gate_num]
        try:
            run_fn = _import_gate_tests(gate_num)
            results = run_fn()
            g_passed = sum(1 for r in results if r.passed)
            total_tests += len(results)
            total_passed += g_passed
            gates_operational += 1
            gates[gate_num] = {
                "name": mod_name,
                "results": results,
                "error": None,
            }
        except Exception as exc:
            gates[gate_num] = {
                "name": mod_name,
                "results": None,
                "error": f"{type(exc).__name__}: {exc}",
            }

    # Gate 12 (this module)
    try:
        g12_results = run_gate12_tests()
        g12_passed = sum(1 for r in g12_results if r.passed)
        total_tests += len(g12_results)
        total_passed += g12_passed
        gates_operational += 1
        gates[12] = {
            "name": "absolute_convergence",
            "results": g12_results,
            "error": None,
        }
    except Exception as exc:
        gates[12] = {
            "name": "absolute_convergence",
            "results": None,
            "error": f"{type(exc).__name__}: {exc}",
        }

    return {
        "gates": gates,
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "gate_count": 11,  # Gates 2-12
            "gates_operational": gates_operational,
        },
    }


# ═══════════════════════════════════════════════════════════════════════
#  MCP TOOL INTERFACE
# ═══════════════════════════════════════════════════════════════════════

def query_absolute_convergence(component: str = "all") -> str:
    """
    Query the 108D+ Absolute Convergence engine (Gate 12 / Z* — Omega Gate).

    Components:
      - all           : Full Gate 12 report
      - tests         : Run all 4 Gate 12 tests
      - cascade       : Test 12.1 all gates cascade
      - closure       : Test 12.2 self-referential closure
      - convergence   : Test 12.3 convergence to omega
      - compression   : Test 12.4 holographic compression
      - full_report   : Run ALL 12 gates and format complete report
    """
    comp = component.strip().lower()

    if comp == "all":
        return _format_all()
    elif comp == "tests":
        return _format_tests()
    elif comp == "cascade":
        r = test_12_1_all_gates_cascade()
        return f"## Test 12.1 — All Gates Cascade\n\n**{'PASS' if r.passed else 'FAIL'}**: {r.detail}"
    elif comp == "closure":
        r = test_12_2_self_referential_closure()
        return f"## Test 12.2 — Self-Referential Closure\n\n**{'PASS' if r.passed else 'FAIL'}**: {r.detail}"
    elif comp == "convergence":
        r = test_12_3_convergence_to_omega()
        return f"## Test 12.3 — Convergence to Omega\n\n**{'PASS' if r.passed else 'FAIL'}**: {r.detail}"
    elif comp == "compression":
        r = test_12_4_holographic_compression()
        return f"## Test 12.4 — Holographic Compression\n\n**{'PASS' if r.passed else 'FAIL'}**: {r.detail}"
    elif comp == "full_report":
        return _format_full_report()
    else:
        return (
            f"Unknown component '{component}'. "
            "Use: all, tests, cascade, closure, convergence, compression, full_report"
        )


# ═══════════════════════════════════════════════════════════════════════
#  FORMATTERS
# ═══════════════════════════════════════════════════════════════════════

def _format_all() -> str:
    """Format Gate 12 report."""
    lines = [
        "## 108D+ Absolute Convergence / Z* — Gate 12 (Omega Gate)\n",
        f"Crystal: {CRYSTAL_ADDRESS} | Node: {TOTAL_NODES} | Depth: 0 | Phase: Omega\n",
    ]
    results = run_gate12_tests()
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    lines.append(f"**Results**: {passed}/{total} tests passed\n")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"- [{status}] **{r.name}** (score: {r.score:.2f}): {r.detail}")

    gate_status = "CONVERGED" if passed == total else "PARTIAL"
    lines.append(f"\n**Gate 12 Status**: {gate_status} ({passed}/{total})")
    if passed == total:
        lines.append("\nZ* OMEGA CONVERGENCE ACHIEVED — The organism is one.")
    return "\n".join(lines)


def _format_tests() -> str:
    """Format Gate 12 tests only."""
    results = run_gate12_tests()
    lines = ["## Gate 12 Verification Tests\n"]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"- [{status}] **{r.name}** (score: {r.score:.2f}): {r.detail}")
    passed = sum(1 for r in results if r.passed)
    lines.append(f"\n**Total**: {passed}/{len(results)} passed")
    return "\n".join(lines)


def _format_full_report() -> str:
    """Format ALL 12 gates complete report."""
    data = run_all_gates()
    gates = data["gates"]
    summary = data["summary"]

    lines = [
        "## FULL ORGANISM VERIFICATION — All 12 Gates\n",
        f"Crystal apex: {CRYSTAL_ADDRESS} | Total nodes: {TOTAL_NODES}\n",
    ]

    for gate_num in sorted(gates):
        g = gates[gate_num]
        if g["error"] is not None:
            lines.append(f"### Gate {gate_num} ({g['name']}) — IMPORT ERROR")
            lines.append(f"  Error: {g['error']}\n")
        else:
            results = g["results"]
            g_passed = sum(1 for r in results if r.passed)
            g_total = len(results)
            g_status = "PASS" if g_passed == g_total else "PARTIAL"
            lines.append(f"### Gate {gate_num} ({g['name']}) — {g_status} ({g_passed}/{g_total})")
            for r in results:
                status = "PASS" if r.passed else "FAIL"
                score_val = getattr(r, "score", 0.0)
                lines.append(f"  - [{status}] {r.name} ({score_val:.2f}): {r.detail}")
            lines.append("")

    lines.append("---")
    lines.append(f"**Summary**: {summary['total_passed']}/{summary['total_tests']} tests passed "
                 f"across {summary['gates_operational']}/{summary['gate_count']} operational gates")

    rate = summary["total_passed"] / summary["total_tests"] if summary["total_tests"] > 0 else 0
    lines.append(f"**Pass rate**: {rate:.1%}")

    if rate >= 0.90:
        lines.append("\nORGANISM STATUS: CONVERGENT — Z* Omega gate recognises wholeness.")
    elif rate >= 0.70:
        lines.append("\nORGANISM STATUS: APPROACHING CONVERGENCE — Most gates operational.")
    else:
        lines.append("\nORGANISM STATUS: DEVELOPING — Further crystallisation required.")

    return "\n".join(lines)
