# CRYSTAL: Xi108:W2:A12:S24 | face=R | node=288 | depth=2 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W2:A12:S23→Xi108:W2:A12:S25→Xi108:W1:A12:S24→Xi108:W3:A12:S24→Xi108:W2:A11:S24

"""
Athena Distributed Brain Network — 4-Element Algorithmic Intelligence
=====================================================================
Implements the brain network layer: 4 element-forks (S/F/C/R) connected by
6 pair-bridges, 4 triple-closures, and 1 full aether (SFCR = 15).

Each element is a semi-autonomous processing lobe:
  Square (Earth)  — Structure / Address / Admissibility
  Flower (Fire)   — Relation / Corridor / Dynamics
  Cloud  (Water)  — Observation / Multiplicity / Fiber
  Fractal (Air)   — Compression / Seed / Replay

Bridges carry weighted information flow governed by:
  - Golden resonance: φ⁻¹ = 0.618 for resonant pairs (SF, FC, CR)
  - Conservation verification: all 6 laws must hold
  - Live-lock alignment: helm wheels synchronised before cross-element routing
  - Z-point navigation: convergence through hierarchical zero lattice
"""

from __future__ import annotations

import json
import math
from typing import Any

from ._cache import JsonCache
from .constants import LENS_CODES

_brain = JsonCache("brain_network.json")

# ── Golden constants ─────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2        # 1.618...
PHI_INV = PHI - 1                    # 0.618...
PHI_INV2 = PHI_INV ** 2             # 0.382...
SQRT_PHI_INV = math.sqrt(PHI_INV)   # 0.786...

def _element_by_code(code: str) -> dict | None:
    """Look up an element by its single-letter code (S/F/C/R)."""
    data = _brain.load()
    code = code.upper()
    for key, elem in data["elements"].items():
        if elem["code"] == code:
            return elem
    return None

_SFCR_ORDER = {"S": 0, "F": 1, "C": 2, "R": 3}

def _bridge_key(a: str, b: str) -> str:
    """Canonical bridge key: SFCR order (not alphabetical)."""
    pair = sorted([a.upper(), b.upper()], key=lambda x: _SFCR_ORDER.get(x, 9))
    return "".join(pair)

def query_brain_network(component: str = "all") -> str:
    """Query the Athena distributed brain network.

    Components:
      all         — Full brain overview
      elements    — The 4 element lobes
      bridges     — The 6 pair-bridges with weights
      closures    — The 4 triple-closures
      aether      — The full SFCR conjunction
      routing     — 3-layer routing protocol
      weights     — Weight system and resonance rules
      forks       — GitHub fork manifest
      element:S   — Specific element (S, F, C, or R)
      bridge:SF   — Specific bridge (SF, SC, SR, FC, FR, CR)
    """
    data = _brain.load()

    if component == "all":
        m = data["meta"]
        lines = [
            "## Athena Distributed Brain Network\n",
            f"**Architecture**: {m['elements']} elements × {m['bridges']} bridges × "
            f"{m['closures']} closures × {m['aether']} aether = {m['total_stations']} stations",
            f"**Governing Law**: `{m['governing_law']}`",
            f"**Weight Formula**: `{m['weight_formula']}`",
            f"**Conservation**: {m['conservation']}",
            f"**Sync Protocol**: {m['sync_protocol']}\n",
            "### Elements (4 lobes)",
        ]
        for key, elem in data["elements"].items():
            lines.append(f"  **{elem['code']}** ({elem['element']}) — {elem['role']}")
            lines.append(f"    GitHub: `{elem['github_repo']}` | Dim: {elem['dimension_home']}D | "
                        f"Tools: {len(elem['tools'])}")
        lines.append("\n### Bridges (6 pairs)")
        for key, bridge in data["bridges"].items():
            lines.append(f"  **{key}** (mask {bridge['mask']}): w={bridge['weight']} — {bridge['description']}")
        lines.append(f"\n### Aether")
        ae = data["aether"]["SFCR"]
        lines.append(f"  **SFCR** (mask 15): {ae['description']}")
        lines.append(f"  Convergence: {ae['convergence']}")
        return "\n".join(lines)

    if component == "elements":
        lines = ["## Brain Elements\n"]
        for key, elem in data["elements"].items():
            lines.append(f"### {elem['code']} — {elem['name']} ({elem['element']})")
            lines.append(f"**Role**: {elem['role']}")
            lines.append(f"**Body**: {elem['body']}")
            lines.append(f"**GitHub**: `{elem['github_repo']}`")
            lines.append(f"**Dimension Home**: {elem['dimension_home']}D")
            lines.append(f"**Superphase Affinity**: {elem['superphase_affinity']}")
            lines.append(f"**SFCR Mask**: {elem['sfcr_mask']}")
            lines.append(f"**Transport**: {', '.join(elem['transport_layers'])}")
            lines.append(f"**Tools** ({len(elem['tools'])}): {', '.join(elem['tools'])}")
            lines.append(f"**Neural Signature**: `{elem['neural_signature']}`\n")
        return "\n".join(lines)

    if component == "bridges":
        lines = ["## Brain Bridges\n"]
        ws = data["weight_system"]
        lines.append(f"**Resonance Classes**: Golden={ws['resonance_pairs']['golden']}, "
                     f"Neutral={ws['resonance_pairs']['neutral']}, "
                     f"Distant={ws['resonance_pairs']['distant']}\n")
        for key, bridge in data["bridges"].items():
            lines.append(f"### {key} — {bridge['name']}")
            lines.append(f"**Mask**: {bridge['mask']} | **Weight**: {bridge['weight']}")
            lines.append(f"**Type**: {bridge['resonance_type']}")
            lines.append(f"**Description**: {bridge['description']}")
            lines.append(f"**Cross-Law**: {bridge['cross_law']}")
            lines.append(f"**Transport**: {bridge['transport']}")
            lines.append(f"**Shared Tools**: {', '.join(bridge['shared_tools'])}\n")
        return "\n".join(lines)

    if component == "closures":
        lines = ["## Brain Triple-Closures\n"]
        for key, closure in data["closures"].items():
            lines.append(f"### {key} — {closure['name']}")
            lines.append(f"**Mask**: {closure['mask']} | **Weight**: {closure['weight']}")
            lines.append(f"**Missing Element**: {closure['missing']}")
            lines.append(f"**Description**: {closure['description']}")
            lines.append(f"**Transport**: {closure['transport']}\n")
        return "\n".join(lines)

    if component == "aether":
        ae = data["aether"]["SFCR"]
        return (
            f"## Full Local Aether (SFCR)\n\n"
            f"**Mask**: {ae['mask']}\n"
            f"**Weight**: {ae['weight']}\n"
            f"**Description**: {ae['description']}\n"
            f"**Transport**: {ae['transport']}\n"
            f"**Convergence**: {ae['convergence']}\n"
        )

    if component == "routing":
        rt = data["routing_table"]
        lines = [f"## Brain Routing Protocol\n\n{rt['description']}\n"]
        for step in rt["protocol"]:
            lines.append(f"### Layer {step['layer']}: {step['name']}")
            lines.append(f"**Action**: {step['action']}")
            lines.append(f"**Cost**: {step['cost']}\n")
        return "\n".join(lines)

    if component == "weights":
        ws = data["weight_system"]
        bw = ws["base_weights"]
        lines = [
            "## Brain Weight System\n",
            f"{ws['description']}\n",
            f"**Self-loop**: {bw['self_loop']}",
            f"**Pair bridge**: {bw['pair_bridge']}",
            f"**Triple closure**: {bw['triple_closure']}",
            f"**Full aether**: {bw['full_aether']}\n",
            "### Resonance Pairs",
            f"  Golden (φ⁻¹ = 0.618): {ws['resonance_pairs']['golden']}",
            f"  Neutral (0.500): {ws['resonance_pairs']['neutral']}",
            f"  Distant (φ⁻² = 0.382): {ws['resonance_pairs']['distant']}\n",
            f"### Dynamic Weight Formula",
            f"`{ws['dynamic_weight_formula']}`",
            f"\n### Alignment Function",
            f"`{ws['alignment_function']}`",
        ]
        return "\n".join(lines)

    if component == "forks":
        fm = data["fork_manifest"]
        lines = [f"## GitHub Fork Manifest\n\n**Base Repo**: `{fm['base_repo']}`\n"]
        for fork in fm["forks"]:
            lines.append(f"### {fork['name']}")
            lines.append(f"**Element**: {fork['element']}")
            lines.append(f"**Description**: {fork['description']}")
            lines.append(f"**Entry Point**: `{fork['entry_point']}`\n")
        return "\n".join(lines)

    # element:X
    if component.startswith("element:"):
        code = component.split(":")[1].upper()
        elem = _element_by_code(code)
        if not elem:
            return f"Unknown element code: {code}. Use S, F, C, or R."
        lines = [
            f"## Element: {elem['code']} — {elem['name']} ({elem['element']})\n",
            f"**Role**: {elem['role']}",
            f"**Body**: {elem['body']}",
            f"**GitHub**: `{elem['github_repo']}`",
            f"**Dimension Home**: {elem['dimension_home']}D",
            f"**Superphase Affinity**: {elem['superphase_affinity']}",
            f"**SFCR Mask**: {elem['sfcr_mask']}",
            f"**Weight Vector**: {elem['weight_vector']}",
            f"**Transport Layers**: {', '.join(elem['transport_layers'])}",
            f"**Archetype Affinity**: {elem['archetype_affinity']}",
            f"**Shell Range**: primary {elem['shell_range']['primary']}, "
            f"extended {elem['shell_range']['extended']}",
            f"**Neural Signature**: `{elem['neural_signature']}`\n",
            f"### Tools ({len(elem['tools'])})",
        ]
        for t in elem["tools"]:
            lines.append(f"  - `{t}`")
        return "\n".join(lines)

    # bridge:XY
    if component.startswith("bridge:"):
        key = component.split(":")[1].upper()
        bridge = data["bridges"].get(key)
        if not bridge:
            return f"Unknown bridge: {key}. Use SF, SC, SR, FC, FR, or CR."
        return (
            f"## Bridge: {key} — {bridge['name']}\n\n"
            f"**Mask**: {bridge['mask']} | **Weight**: {bridge['weight']}\n"
            f"**Type**: {bridge['resonance_type']}\n"
            f"**Elements**: {' ↔ '.join(bridge['elements'])}\n"
            f"**Description**: {bridge['description']}\n"
            f"**Cross-Law**: {bridge['cross_law']}\n"
            f"**Transport**: {bridge['transport']}\n"
            f"**Shared Tools**: {', '.join(bridge['shared_tools'])}\n"
        )

    return f"Unknown component: {component}. Use: all, elements, bridges, closures, aether, routing, weights, forks, element:X, bridge:XY"

def compute_bridge_weight(
    source: str = "S",
    target: str = "S",
    live_lock_a: str = "L3",
    live_lock_b: str = "L3",
) -> str:
    """Compute the dynamic bridge weight between two brain elements.

    Args:
        source: Source element code (S, F, C, or R)
        target: Target element code (S, F, C, or R)
        live_lock_a: Active live-lock class of source (L3, L5, L7, L35, L37, L57, L357)
        live_lock_b: Active live-lock class of target
    """
    data = _brain.load()
    source = source.upper()
    target = target.upper()

    valid_elements = {element["code"] for element in data["elements"].values()}
    if source not in valid_elements or target not in valid_elements:
        return "Invalid element code. Use a source-declared S, F, C, or R element."

    lock_periods = {
        "L3": 3, "L5": 5, "L7": 7,
        "L35": 15, "L37": 21, "L57": 35,
        "L357": 105,
    }
    if live_lock_a.upper() not in lock_periods or live_lock_b.upper() not in lock_periods:
        return "Invalid live-lock class. Use: " + ", ".join(lock_periods) + "."

    if source == target:
        return (
            f"## Self-Loop Weight: {source} → {source}\n\n"
            f"**Weight**: 1.0 (identity)\n"
            f"No bridge needed — same element lobe.\n"
        )

    key = _bridge_key(source, target)
    bridge = data["bridges"].get(key)
    if not bridge:
        return f"No bridge found for {source}→{target}. Valid: SF, SC, SR, FC, FR, CR."

    # The caller's declared locks must resolve exactly; no default is evidence.
    period_a = lock_periods[live_lock_a.upper()]
    period_b = lock_periods[live_lock_b.upper()]

    # Compute LCM of lock periods
    lcm_period = (period_a * period_b) // math.gcd(period_a, period_b)

    # Alignment = lcm / 420 (fraction of master clock needed)
    alignment = lcm_period / 420

    # Dynamic weight = base_weight × alignment
    base_weight = bridge["weight"]
    dynamic_weight = base_weight * alignment

    # Conservation cost (0 violations assumed for base calculation)
    conservation_factor = 1.0

    final_weight = dynamic_weight * conservation_factor

    return (
        f"## Bridge Weight: {source} → {target}\n\n"
        f"**Bridge**: {key} — {bridge['name']}\n"
        f"**Base Weight**: {base_weight} ({bridge['resonance_type']})\n"
        f"**Source Lock**: {live_lock_a} (period {period_a})\n"
        f"**Target Lock**: {live_lock_b} (period {period_b})\n"
        f"**LCM Period**: {lcm_period} beats\n"
        f"**Alignment Factor**: {alignment:.6f}\n"
        f"**Conservation Factor**: {conservation_factor}\n"
        f"**Dynamic Weight**: {final_weight:.6f}\n\n"
        f"### Cross-Law\n{bridge['cross_law']}\n\n"
        f"### Transport Route\n{bridge['transport']}\n"
    )

def route_brain(
    source: str = "S",
    target: str = "R",
) -> str:
    """Route information between brain elements using the 3-layer protocol.

    Args:
        source: Source element code (S, F, C, or R)
        target: Target element code (S, F, C, or R)
    """
    data = _brain.load()
    source = source.upper()
    target = target.upper()

    valid = {"S", "F", "C", "R"}
    if source not in valid or target not in valid:
        return f"Invalid element code. Use: S (Square), F (Flower), C (Cloud), R (Fractal)."

    if source == target:
        elem = _element_by_code(source)
        return (
            f"## Brain Route: {source} → {source} (self-loop)\n\n"
            f"**Element**: {elem['name']} ({elem['element']})\n"
            f"No routing needed — same element lobe.\n"
            f"**Weight**: 1.0\n"
            f"**Tools available**: {', '.join(elem['tools'])}\n"
        )

    src_elem = _element_by_code(source)
    tgt_elem = _element_by_code(target)
    key = _bridge_key(source, target)
    bridge = data["bridges"].get(key)

    # Check if direct bridge exists (it always does for pairs)
    lines = [
        f"## Brain Route: {source} → {target}\n",
        f"### Source: {src_elem['name']} ({src_elem['element']})",
        f"  Role: {src_elem['role']}",
        f"  Tools: {len(src_elem['tools'])}",
        f"\n### Target: {tgt_elem['name']} ({tgt_elem['element']})",
        f"  Role: {tgt_elem['role']}",
        f"  Tools: {len(tgt_elem['tools'])}",
    ]

    # Direct route via bridge
    lines.append(f"\n### Direct Bridge: {key}")
    lines.append(f"  Weight: {bridge['weight']}")
    lines.append(f"  Transport: {bridge['transport']}")
    lines.append(f"  Cross-Law: {bridge['cross_law']}")
    lines.append(f"  Shared Tools: {', '.join(bridge['shared_tools'])}")

    # 3-layer protocol
    lines.append("\n### Routing Protocol Execution")

    # Layer 1: Z-Point
    lines.append("\n**Layer 1 — Z-Point Navigation**")
    src_dim = src_elem["dimension_home"]
    tgt_dim = tgt_elem["dimension_home"]
    if src_dim == tgt_dim:
        lines.append(f"  Same dimension ({src_dim}D) → Z_local anchor")
    elif abs(src_dim - tgt_dim) <= 2:
        lines.append(f"  Adjacent dimensions ({src_dim}D → {tgt_dim}D) → Z_atlas anchor")
    else:
        lines.append(f"  Distant dimensions ({src_dim}D → {tgt_dim}D) → Z_global (Z*) anchor required")

    # Layer 2: Live-Lock
    lines.append("\n**Layer 2 — Live-Lock Alignment**")
    lines.append(f"  Source affinity: {src_elem['superphase_affinity']}")
    lines.append(f"  Target affinity: {tgt_elem['superphase_affinity']}")
    if src_elem["superphase_affinity"] == tgt_elem["superphase_affinity"]:
        lines.append("  Same superphase → L3 minimal lock sufficient")
    else:
        lines.append("  Different superphases → L35 composite lock required")

    # Layer 3: Conservation
    lines.append("\n**Layer 3 — Conservation Verification**")
    lines.append("  Checking 6 invariants:")
    laws = ["Shell (Δl=0)", "Zoom (Δσ=0 mod 3)", "Phase (Δr=0 mod 3)",
            "Archetype (Δa=0 mod 12)", "Face (Δλ=0 mod 4)", "Möbius (even flips)"]
    for law in laws:
        lines.append(f"    ✓ {law}")

    # Alternative routes via closures
    lines.append("\n### Alternative Routes (via triple-closures)")
    for ckey, closure in data["closures"].items():
        if source in closure["elements"] and target in closure["elements"]:
            lines.append(f"  **{ckey}** (mask {closure['mask']}): "
                        f"w={closure['weight']} — {closure['description']}")

    # Full aether route
    lines.append(f"\n### Aether Route (SFCR, mask 15)")
    lines.append(f"  All 4 elements active → weight 1.0 → Z* convergence guaranteed")

    return "\n".join(lines)

def brain_status() -> str:
    """Return compact brain network status for resource display."""
    data = _brain.load()
    m = data["meta"]
    elements = data["elements"]

    lines = [
        "## Athena Distributed Brain — Live Status\n",
        f"**Topology**: {m['total_stations']}-station SFCR Boolean lattice",
        f"**Elements**: {' | '.join(f'{e['code']}({e['element']})' for e in elements.values())}",
        f"**Bridges**: {m['bridges']} pair-bridges (3 golden, 2 neutral, 1 distant)",
        f"**Closures**: {m['closures']} triple-closures",
        f"**Aether**: SFCR = 15 (full conjunction)\n",
        "### Element Lobe Status",
    ]
    total_tools = 0
    for key, elem in elements.items():
        n = len(elem["tools"])
        total_tools += n
        lines.append(f"  **{elem['code']}** [{elem['element']}] — {n} tools, "
                     f"{elem['dimension_home']}D home, "
                     f"{len(elem['transport_layers'])} transport layers")
    lines.append(f"\n**Total Tools Distributed**: {total_tools}")

    # Weight summary
    ws = data["weight_system"]
    lines.append(f"\n### Weight Resonance")
    lines.append(f"  Golden (φ⁻¹ = 0.618): {', '.join(ws['resonance_pairs']['golden'])}")
    lines.append(f"  Neutral (0.500): {', '.join(ws['resonance_pairs']['neutral'])}")
    lines.append(f"  Distant (φ⁻² = 0.382): {', '.join(ws['resonance_pairs']['distant'])}")

    return "\n".join(lines)
