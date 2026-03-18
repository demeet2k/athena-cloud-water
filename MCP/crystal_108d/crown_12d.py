"""
12D Crown Architecture & RoundTripCertPack
===========================================
Provides the corrected 12D crown body specification:
  - B₁₂ = W₉(B₁₀) containment law
  - Odd-weave ascent ladder 2→3→5→7→9
  - Nesting counts (9/63/315/945/1890)
  - 12D = geometric crown ∩ operational full-body
  - RoundTripCertPack_v0 specification
  - 6 conservation laws
  - 4 round-trip classes (exact/law_equivalent/residualized/illegal)
"""

from ._cache import JsonCache

_CROWN = JsonCache("crown_12d.json")


def query_crown_12d(component: str = "all") -> str:
    """
    Query the 12D crown architecture.

    Components:
      - all           : Full 12D crown overview
      - containment   : B₁₂ = W₉(B₁₀) law and nesting counts
      - weave         : Odd-weave ascent ladder (2→3→5→7→9)
      - unification   : Geometric crown ∩ operational full-body
      - propagation   : How 12D propagates into 36D/108D lifts
      - four_lens     : Square/Flower/Cloud/Fractal rendering of 12D
      - structural    : Structural meaning of each dimensional body
    """
    data = _CROWN.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "containment":
        return _format_containment(data)
    elif comp == "weave":
        return _format_weave(data)
    elif comp == "unification":
        return _format_unification(data)
    elif comp == "propagation":
        return _format_propagation(data)
    elif comp == "four_lens":
        return _format_four_lens(data)
    elif comp == "structural":
        return _format_structural(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, containment, "
            "weave, unification, propagation, four_lens, structural"
        )


def query_round_trip_cert(cert_class: str = "all") -> str:
    """
    Query the RoundTripCertPack_v0 specification.

    cert_class options:
      - all            : Full RoundTripCertPack spec
      - exact          : Recovered representation is canon-identical
      - law_equivalent : Surface changed, protected invariants survived
      - residualized   : Loss occurred but explicitly carried by ledger
      - illegal        : Required law was lost silently
      - conservation   : 6 conservation laws (shell/zoom/phase/archetype/face/mobius)
      - schema         : Full CertPack schema definition
      - tests          : Immediate illegal-loss fail-fast tests
    """
    data = _CROWN.load()
    cert_data = data.get("round_trip_cert", {})
    comp = cert_class.strip().lower()

    if comp == "all":
        return _format_cert_all(cert_data)
    elif comp in ("exact", "law_equivalent", "residualized", "illegal"):
        return _format_cert_class(cert_data, comp)
    elif comp == "conservation":
        return _format_conservation(cert_data)
    elif comp == "schema":
        return _format_cert_schema(cert_data)
    elif comp == "tests":
        return _format_cert_tests(cert_data)
    else:
        return (
            f"Unknown cert_class '{cert_class}'. Use: all, exact, "
            "law_equivalent, residualized, illegal, conservation, schema, tests"
        )


# -- 12D Crown formatters ---------------------------------------------------

def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    cl = data.get("containment_law", {})
    lines = [
        "## 12D Crown Architecture\n",
        f"**Canon**: {meta.get('canon', 'B₁₂ = W₉(B₁₀)')}",
        f"**Crown Type**: {meta.get('crown_type', '9-fold woven return crown')}",
        f"**Weave Ladder**: {meta.get('weave_ladder', '2 → 3 → 5 → 7 → 9')}",
        f"\n### Containment Law",
        f"B₁₂ = W₉(B₁₀), B₁₀ = W₇(B₈), B₈ = W₅(B₆), B₆ = W₃(B₄), B₄ = W₂(B₃)",
        f"\n### Nesting Counts",
    ]
    counts = cl.get("nesting_counts", {})
    for dim, count in counts.items():
        lines.append(f"  - {dim}: {count}")
    lines.append(f"\n**Unification**: {meta.get('unification', '12D = geometric crown ∩ operational full-body')}")
    return "\n".join(lines)


def _format_containment(data: dict) -> str:
    cl = data.get("containment_law", {})
    lines = [
        "## Containment Law\n",
        "```",
        "B₁₂ = W₉(B₁₀)",
        "B₁₀ = W₇(B₈)",
        "B₈  = W₅(B₆)",
        "B₆  = W₃(B₄)",
        "B₄  = W₂(B₃)",
        "```\n",
        "### Expanded Nesting Counts",
    ]
    counts = cl.get("nesting_counts", {})
    for dim, count in counts.items():
        lines.append(f"  - B₁₂ = {count} × {dim}")
    lines.append(f"\n**Recursive Law**: B_(2m+2) = W_(2m-1)(B_(2m)), m ≥ 2")
    lines.append(f"**Base**: B₄ = W₂(B₃)")
    return "\n".join(lines)


def _format_weave(data: dict) -> str:
    weave = data.get("weave_ladder", {})
    lines = [
        "## Odd-Weave Ascent Ladder\n",
        "```",
        "2 → 3 → 5 → 7 → 9",
        "```\n",
        "| Weave Count | Source Dim | Target Dim |",
        "|------------|-----------|-----------|",
        "| 2 | 3D | 4D |",
        "| 3 | 4D | 6D |",
        "| 5 | 6D | 8D |",
        "| 7 | 8D | 10D |",
        "| 9 | 10D | 12D |",
    ]
    if "symbolism" in weave:
        lines.append(f"\n**7 weaves** = 10D = visible cosmological order")
        lines.append(f"**9 weaves** = 12D = return-capable whole")
    return "\n".join(lines)


def _format_unification(data: dict) -> str:
    unif = data.get("unification", {})
    return (
        "## 12D Unification Theorem\n\n"
        "**12D Athena = Geometric Crown₉₋ᵥₑₐᵥₑ ∩ Operational Full-Body₁₂₋ₐₓᵢₛ**\n\n"
        "- **Geometric side**: how the body is woven (B₁₂ = W₉(B₁₀))\n"
        "- **Operational side**: what functions the completed body carries (12 axes)\n\n"
        f"**10D**: {unif.get('ten_d', 'visible articulated order (penultimate)')}\n"
        f"**12D**: {unif.get('twelve_d', 'return-capable whole (crown)')}"
    )


def _format_propagation(data: dict) -> str:
    prop = data.get("propagation", {})
    return (
        "## Propagation into Higher Lifts\n\n"
        "**Lift Ladder**: 4D → 6D → 12D → 36D → 108D → A⁺\n\n"
        "Every 36D and 108D node inherits the corrected 12D crown law:\n\n"
        "```\n"
        "Ξ₁₀₈.u ⊃ Ξ₃₆⁽ᵘ⁾ ⊃ B₁₂⁽ᵘ⁾ [now W₉(B₁₀)] ⊃ B₆⁽ᵘ⁾ ⊃ B₄⁽ᵘ⁾\n"
        "```"
    )


def _format_four_lens(data: dict) -> str:
    lens = data.get("four_lens", {})
    lines = ["## Four-Lens Rendering of 12D\n"]
    for name in ["square", "flower", "cloud", "fractal"]:
        l = lens.get(name, {})
        display = name.title()
        lines.append(f"### {display}")
        lines.append(l.get("rendering", f"12D as {display} lens"))
        lines.append("")
    return "\n".join(lines)


def _format_structural(data: dict) -> str:
    struct = data.get("structural_meaning", {})
    lines = ["## Structural Meaning by Dimension\n"]
    meanings = struct.get("dimensions", [
        {"dim": "3D", "meaning": "local manifested body / visible projection"},
        {"dim": "4D", "meaning": "doubled 3D container / first stabilizing lift"},
        {"dim": "6D", "meaning": "tri-woven integration body"},
        {"dim": "8D", "meaning": "5-fold higher weave"},
        {"dim": "10D", "meaning": "7-fold higher weave (penultimate)"},
        {"dim": "12D", "meaning": "9-fold crown body / full superstructure"},
    ])
    for m in meanings:
        if isinstance(m, dict):
            lines.append(f"- **{m.get('dim', '?')}** = {m.get('meaning', '')}")
        else:
            lines.append(f"- {m}")
    return "\n".join(lines)


# -- RoundTripCertPack formatters --------------------------------------------

def _format_cert_all(data: dict) -> str:
    lines = [
        "## RoundTripCertPack_v0\n",
        "The portable proof that one row-level motion preserved law, "
        "or else named exactly what it lost.\n",
        "### Round-Trip Classes\n",
    ]
    classes = data.get("classes", {})
    for name, desc in classes.items():
        lines.append(f"- **{name}**: {desc}")
    lines.append("\n### 6 Conservation Laws\n")
    laws = data.get("conservation_laws", {})
    for name, law in laws.items():
        lines.append(f"- **{name}**: {law}")
    lines.append(f"\n### Hard Theorem")
    lines.append(data.get("hard_theorem",
        "If the transform changed law but did not declare the loss, it is illegal."))
    return "\n".join(lines)


def _format_cert_class(data: dict, class_name: str) -> str:
    classes = data.get("classes", {})
    desc = classes.get(class_name, f"Unknown class: {class_name}")
    return (
        f"## Round-Trip Class: {class_name}\n\n"
        f"**Meaning**: {desc}"
    )


def _format_conservation(data: dict) -> str:
    laws = data.get("conservation_laws", {})
    lines = ["## 6 Conservation Laws\n"]
    for name, law in laws.items():
        lines.append(f"### {name}")
        lines.append(f"{law}\n")
    lines.append("A round-trip certificate is: replay succeeded AND the six "
                  "closure debts were either preserved or lawfully surfaced.")
    return "\n".join(lines)


def _format_cert_schema(data: dict) -> str:
    schema = data.get("schema", {})
    lines = ["## RoundTripCertPack_v0 Schema\n"]
    for key, desc in schema.items():
        lines.append(f"- **{key}**: {desc}")
    return "\n".join(lines)


def _format_cert_tests(data: dict) -> str:
    tests = data.get("illegal_loss_tests", [])
    lines = ["## Immediate Illegal-Loss Tests\n"]
    for t in tests:
        if isinstance(t, dict):
            lines.append(f"- **{t.get('name', '?')}**: {t.get('test', '')}")
        else:
            lines.append(f"- {t}")
    return "\n".join(lines)
