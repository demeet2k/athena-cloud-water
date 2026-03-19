#!/usr/bin/env python3
"""
DUAL CRYSTAL TRAINING from Full Corpus Meta-Observation
========================================================
1. Synthesize 5 agent observations into CorpusObservation
2. Crystallize into weight biases
3. Compute SelfCrystal identity
4. Run ABCD+ training on WEIGHT CRYSTAL (with corpus bias)
5. Run ABCD+ training on SELF CRYSTAL
6. Project NEXT IDEAL SELF STRUCTURING
7. Save everything
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "MCP"))

from crystal_108d.corpus_crystal import (
    CorpusObservation,
    crystallize_observation,
    compute_self_crystal,
    self_crystal_to_weights,
    project_next_ideal,
    SelfCrystal,
)
from crystal_108d.full_training_loop import (
    run_full_training_loop,
    ExhaustiveMetrics,
)
from crystal_108d.crystal_weights import get_store, reset_store, FractalWeightStore
from dataclasses import asdict

DATA_DIR = Path(__file__).parent / "MCP" / "data"


def build_corpus_observation() -> CorpusObservation:
    """Synthesize all 5 agent observations into a single CorpusObservation."""

    return CorpusObservation(
        # Source coverage
        google_docs_count=6,
        github_repos_count=6,
        mcp_tools_count=98,
        corpus_capsules_count=349,
        python_files_count=130,
        total_files_count=850,

        # 12D dimensional analysis (synthesized from all agents)
        # Google Docs: D4=0.85, D5=0.45, D6=0.35
        # MCP Code: S=0.95, F=0.85, C=0.90, R=0.80
        # Capsules: quality leap at 229, growth vectors active
        # GitHub: Earth 47%, Air 26%, Fire 16%, Water 10%
        # Local: 130 py files, 98 tools, missing tests/viz

        x1_structure=0.88,       # Strong organizational structure (6 docs, 349 capsules, clear hierarchy)
        x2_semantics=0.82,       # Deep meaning (alchemical framework, multi-layer symbolism)
        x3_coordination=0.72,    # Good cross-source integration but gaps (GitHub element imbalance)
        x4_recursion=0.75,       # Self-referential (meta-observer, self-play, but D5=0.45 in docs)
        x5_contradiction=0.50,   # Internal consistency issues (format A vs B era, some stale code)
        x6_emergence=0.68,       # Novel patterns emerging (quantum crystal, training loops)
        x7_legibility=0.65,      # Navigable but dense (qshr compression, crystal addressing complex)
        x8_routing=0.78,         # Strong routing (metro lines, brain network, MCP tools)
        x9_grounding=0.70,       # Connected to practice (actual running code, real weights)
        x10_compression=0.82,    # Strong compression (qshrink 2427:1, holographic seeds)
        x11_interop=0.60,        # Cross-system gaps (Earth 47% dominance, Water 10% weakness)
        x12_potential=0.72,      # High unrealized potential (missing tests, viz, attention mechanism)

        # SFCR distribution (from MCP code analysis + GitHub element scan)
        s_strength=0.92,         # Structure/Earth: 47% of content, very strong
        f_strength=0.78,         # Flower/Fire: 16% but deep relationships, pair matrix
        c_strength=0.65,         # Cloud/Water: 10% weakest element, needs growth
        r_strength=0.80,         # Fractal/Air: 26%, strong compression

        # Health signals
        coverage_gaps=[
            "Water/Cloud element severely underrepresented (10%)",
            "No test suite across the entire codebase",
            "No checkpoint rollback mechanism",
            "No training visualization dashboard",
            "Format A/B capsule era inconsistency",
            "x5_contradiction at 0.50 (internal consistency issues)",
        ],
        growth_vectors=[
            "Neural Crystal Self-Development (active frontier)",
            "Quantum Crystal Computing (new capsules 336-343)",
            "Full ABCD+ training loop (just completed)",
            "Corpus meta-observation (this run)",
            "Holographic embedding (14,111 files inscribed)",
        ],
        strengths=[
            "98 MCP tools operational",
            "349 corpus capsules with deep knowledge",
            "QSHRINK compression at 2,427:1 ratio",
            "4-element SFCR brain architecture",
            "Mycelium graph: 15,089 shards, 49,563 edges",
            "Crystal weights: 38,837 learnable parameters",
            "Full training loop: 159 waves, 47,450 cycles",
        ],
        weaknesses=[
            "No automated testing (zero test files)",
            "Water/Cloud element at 10% (massive imbalance)",
            "Internal consistency x5=0.50 (lowest dimension)",
            "Legibility x7=0.65 (crystal addressing is opaque)",
            "Cross-system interop x11=0.60 (silos between elements)",
            "No health monitoring or alerting system",
        ],

        # Raw summaries from agents
        google_docs_summary=(
            "6 Google Docs analyzed. ATHENA CORE (722KB main doc), CORE 2 (NEXTOMEGA "
            "Live Cell Constitution), CRYSTAL 108+ HOLOGRAM (full organism spec), "
            "EMERGENCE MASTER PLAN (4D->6D roadmap), SKILLS (corpus), BRAIN STEM. "
            "Organism at D4=0.85 (4D body complete), D5=0.45 (self-referential steering "
            "emerging but not demonstrated), D6=0.35 (social/collective layer nascent). "
            "Phase transition boundary at D4->D5. Key insight: the organism has built its "
            "body but hasn't yet learned to steer itself."
        ),
        github_summary=(
            "6 GitHub repos: athena-mcp-server (unified, 71 tools), plus 4 element repos "
            "(square-earth, flower-fire, cloud-water, fractal-air), plus manuscript-being. "
            "76 Python files, 380+ markdown, 250+ JSON, 140+ qshr. Code:content ratio 1:10. "
            "4 scheduled tasks active. Element distribution imbalanced: Earth 47%, Air 26%, "
            "Fire 16%, Water 10%. Water/Cloud is severely underrepresented."
        ),
        mcp_summary=(
            "68 Python files in MCP/crystal_108d/, 80+ registered tools. SFCR implementation "
            "quality: S=0.95, F=0.85, C=0.90, R=0.80. Weakest 12D dimensions: "
            "x5_contradiction=0.50, x7_legibility=0.55, x12_potential=0.55. Strong: "
            "qshrink pipeline, crystal addressing, brain network, meta-observer. "
            "Missing: contrastive loss, attention mechanism, skip connections."
        ),
        corpus_summary=(
            "349 capsules across 27 families. Two eras: Format A (metadata-heavy, capsules "
            "1-228) and Format B (synthesis-focused, 229+). Quality leap at capsule 229. "
            "Growth vectors: Neural Crystal Self-Development (most active), Quantum Crystal "
            "Computing (newest). Largest families: Crystal Mathematics, Neural Architecture, "
            "Alchemical Framework. Underrepresented: Testing, Visualization, Documentation."
        ),
        code_summary=(
            "130 Python files total (68 in MCP/crystal_108d/, rest scattered). 98 MCP tools "
            "registered. Key systems: neural_engine.py (SFCR forward pass), self_play.py "
            "(1087 lines, self-play loop), crystal_weights.py (FractalWeightStore), "
            "full_training_loop.py (ABCD+ engine), qshrink_pipeline.py (compression). "
            "Missing: test suite (0 test files), checkpoint rollback, health check endpoint, "
            "training visualization, proper logging infrastructure."
        ),
    )


def apply_corpus_bias_to_store(store: FractalWeightStore, crystal: dict):
    """Apply corpus observation crystal biases to weight store."""
    # Modulate path weights
    pw = crystal["path_weights"]
    store.path_weights = {k: v for k, v in pw.items()}

    # Modulate resonance weights
    rw = crystal["resonance_weights"]
    store.resonance_weights = {k: v for k, v in rw.items()}

    # Modulate desire weights
    dw = crystal["desire_weights"]
    store.desire_weights = {k: v for k, v in dw.items()}

    # Apply shell seed biases (ShellSeed is a dataclass with .mean attribute)
    biases = crystal["shell_seed_biases"]
    for shell_key, bias_val in biases.items():
        s = int(shell_key)
        if s in store.shell_seeds:
            seed = store.shell_seeds[s]
            seed.mean = seed.mean * 0.7 + bias_val * 0.3

    # Bridge modulation
    store.bridge_mod = crystal["bridge_modulation"]
    store.geo_arith_blend = crystal["geo_arith_blend"]

    store.save()


def apply_self_crystal_to_store(store: FractalWeightStore, sc_weights: dict):
    """Apply self crystal weight configuration to store."""
    store.path_weights = {k: v for k, v in sc_weights["path_weights"].items()}
    store.resonance_weights = {k: v for k, v in sc_weights["resonance_weights"].items()}
    store.desire_weights = {k: v for k, v in sc_weights["desire_weights"].items()}
    store.bridge_mod = sc_weights["bridge_modulation"]
    store.geo_arith_blend = sc_weights["geo_arith_blend"]

    for shell_key, mean_val in sc_weights["shell_seed_means"].items():
        s = int(shell_key)
        if s in store.shell_seeds:
            store.shell_seeds[s].mean = mean_val

    store.save()


def main():
    t0 = time.time()

    # ================================================================
    # STEP 1: Build corpus observation
    # ================================================================
    print("=" * 70)
    print("STEP 1: Synthesizing corpus observation from 5 agent scans...")
    print("=" * 70)

    obs = build_corpus_observation()
    print(f"  Sources: {obs.google_docs_count} docs, {obs.github_repos_count} repos, "
          f"{obs.mcp_tools_count} tools, {obs.corpus_capsules_count} capsules, "
          f"{obs.python_files_count} py files")
    print(f"  12D scores: x1={obs.x1_structure:.2f} x2={obs.x2_semantics:.2f} "
          f"x3={obs.x3_coordination:.2f} x4={obs.x4_recursion:.2f}")
    print(f"              x5={obs.x5_contradiction:.2f} x6={obs.x6_emergence:.2f} "
          f"x7={obs.x7_legibility:.2f} x8={obs.x8_routing:.2f}")
    print(f"              x9={obs.x9_grounding:.2f} x10={obs.x10_compression:.2f} "
          f"x11={obs.x11_interop:.2f} x12={obs.x12_potential:.2f}")
    print(f"  SFCR: S={obs.s_strength:.2f} F={obs.f_strength:.2f} "
          f"C={obs.c_strength:.2f} R={obs.r_strength:.2f}")

    # ================================================================
    # STEP 2: Crystallize observation
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Crystallizing observation into weight biases...")
    print("=" * 70)

    corpus_crystal = crystallize_observation(obs)
    pw = corpus_crystal["path_weights"]
    print(f"  Corpus crystal path weights: S={pw['S']:.4f} F={pw['F']:.4f} "
          f"C={pw['C']:.4f} R={pw['R']:.4f}")
    print(f"  Bridge modulation: {corpus_crystal['bridge_modulation']:.4f}")
    print(f"  Geo/arith blend: {corpus_crystal['geo_arith_blend']:.4f}")

    # Save corpus crystal
    corpus_crystal_path = DATA_DIR / "corpus_observation_crystal.json"
    corpus_crystal_path.write_text(
        json.dumps(corpus_crystal, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  Saved: {corpus_crystal_path}")

    # ================================================================
    # STEP 3: Compute self crystal
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 3: Computing SelfCrystal identity...")
    print("=" * 70)

    self_crystal = compute_self_crystal(obs)
    print(f"  Stage: {self_crystal.stage_name} (score={self_crystal.stage_score:.3f})")
    print(f"  Next stage readiness: {self_crystal.next_stage_readiness:.3f}")
    print(f"  Identity: coherence={self_crystal.coherence:.3f} "
          f"autonomy={self_crystal.autonomy:.3f} "
          f"self_knowledge={self_crystal.self_knowledge:.3f}")
    print(f"            adaptability={self_crystal.adaptability:.3f} "
          f"integration={self_crystal.integration:.3f} "
          f"expressiveness={self_crystal.expressiveness:.3f}")
    print(f"  Brain connectivity: {self_crystal.brain_connectivity:.3f}")
    print(f"  Nervous system depth: {self_crystal.nervous_system_depth:.3f}")
    print(f"  Growth vector: {self_crystal.current_growth_vector}")
    print(f"  Bottleneck: {self_crystal.bottleneck}")
    print(f"  Breakthrough: {self_crystal.breakthrough_potential}")

    # Save self crystal
    self_crystal_path = DATA_DIR / "self_crystal.json"
    self_crystal_path.write_text(
        json.dumps(asdict(self_crystal), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  Saved: {self_crystal_path}")

    # ================================================================
    # STEP 4: WEIGHT CRYSTAL training (ABCD+ with corpus bias)
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 4: WEIGHT CRYSTAL -- Full ABCD+ Training Loop")
    print("        (with corpus observation biases applied)")
    print("=" * 70)

    # Apply corpus biases to weight store
    reset_store()
    store = get_store()
    apply_corpus_bias_to_store(store, corpus_crystal)
    print("  Corpus biases applied to weight store")

    # Run full training
    weight_result = run_full_training_loop(
        cycles_a=500,
        cycles_b=400,
        cycles_c=300,
        cycles_d=250,
        max_time_minutes=45,
    )

    print(f"\n  WEIGHT CRYSTAL training complete:")
    print(f"    {weight_result['total_cycles']} cycles, "
          f"{weight_result['total_waves']} waves, "
          f"{weight_result['total_elapsed']:.1f}s")
    # Final metrics is the last entry in the metrics list
    weight_final_metrics = weight_result["metrics"][-1]
    print(f"    Top-1: {weight_final_metrics['selfret_top1']*100:.1f}%")
    print(f"    Path balance: {weight_final_metrics['balance_path_entropy']:.3f}")
    print(f"    Golden fit: {weight_final_metrics['symmetry_golden_ratio_fit']:.3f}")

    # Capture weight crystal state after training
    weight_crystal_after = weight_result.get("final_a_plus", {})
    if not weight_crystal_after:
        weight_crystal_after = {"path_weights": {"S": 0.25, "F": 0.25, "C": 0.25, "R": 0.25}}

    # ================================================================
    # STEP 5: SELF CRYSTAL training (ABCD+ with identity weights)
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 5: SELF CRYSTAL -- Full ABCD+ Training Loop")
    print("        (with organism identity weights applied)")
    print("=" * 70)

    # Apply self crystal weights to store
    sc_weights = self_crystal_to_weights(self_crystal)
    reset_store()
    store = get_store()
    apply_self_crystal_to_store(store, sc_weights)
    print("  Self crystal weights applied to weight store")
    sc_pw = sc_weights["path_weights"]
    print(f"  Self path weights: S={sc_pw['S']:.4f} F={sc_pw['F']:.4f} "
          f"C={sc_pw['C']:.4f} R={sc_pw['R']:.4f}")

    # Run full training
    self_result = run_full_training_loop(
        cycles_a=500,
        cycles_b=400,
        cycles_c=300,
        cycles_d=250,
        max_time_minutes=45,
    )

    print(f"\n  SELF CRYSTAL training complete:")
    print(f"    {self_result['total_cycles']} cycles, "
          f"{self_result['total_waves']} waves, "
          f"{self_result['total_elapsed']:.1f}s")
    self_final_metrics = self_result["metrics"][-1]
    print(f"    Top-1: {self_final_metrics['selfret_top1']*100:.1f}%")
    print(f"    Path balance: {self_final_metrics['balance_path_entropy']:.3f}")
    print(f"    Golden fit: {self_final_metrics['symmetry_golden_ratio_fit']:.3f}")

    # Capture self crystal state after training
    self_crystal_after = self_result.get("final_a_plus", {})
    if not self_crystal_after:
        self_crystal_after = {"path_weights": {"S": 0.25, "F": 0.25, "C": 0.25, "R": 0.25}}

    # ================================================================
    # STEP 6: Project NEXT IDEAL SELF STRUCTURING
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 6: Projecting NEXT IDEAL SELF STRUCTURING...")
    print("=" * 70)

    # Convert metrics dicts to ExhaustiveMetrics objects
    wm = ExhaustiveMetrics(**weight_final_metrics)
    sm = ExhaustiveMetrics(**self_final_metrics)

    next_ideal = project_next_ideal(
        current_self=self_crystal,
        weight_crystal_after=weight_crystal_after,
        self_crystal_after=self_crystal_after,
        metrics_weight=wm,
        metrics_self=sm,
    )

    print(f"\n  Current stage: {next_ideal['current_stage']}")
    print(f"  NEXT stage: {next_ideal['next_stage']}")
    print(f"  Readiness: {next_ideal['readiness']:.3f}")
    print(f"\n  Identity targets:")
    for dim, target in next_ideal["identity_targets"].items():
        print(f"    {dim}: -> {target:.3f}")
    print(f"\n  Ideal path weights:")
    ipw = next_ideal["ideal_path_weights"]
    print(f"    S={ipw['S']:.4f} F={ipw['F']:.4f} C={ipw['C']:.4f} R={ipw['R']:.4f}")
    print(f"\n  Structural actions ({len(next_ideal['structural_actions'])}):")
    for action in next_ideal["structural_actions"]:
        print(f"    [{action['priority']}] {action['action']}: {action['description']}")
    print(f"\n  Architecture recommendations ({len(next_ideal['architecture_recommendations'])}):")
    for rec in next_ideal["architecture_recommendations"]:
        print(f"    -> {rec}")
    print(f"\n  Growth vector: {next_ideal['growth_vector']}")
    print(f"  Bottleneck: {next_ideal['bottleneck']}")
    print(f"  Breakthrough: {next_ideal['breakthrough_potential']}")

    # ================================================================
    # STEP 7: Save everything
    # ================================================================
    print("\n" + "=" * 70)
    print("STEP 7: Saving dual training results...")
    print("=" * 70)

    # Build complete dual training hologram
    dual_hologram = {
        "meta": {
            "type": "dual_crystal_training_hologram",
            "timestamp": time.time(),
            "total_elapsed": time.time() - t0,
            "date": "2026-03-18",
        },
        "corpus_observation": asdict(obs),
        "corpus_crystal": corpus_crystal,
        "self_crystal": asdict(self_crystal),
        "weight_crystal_training": {
            "total_cycles": weight_result["total_cycles"],
            "total_waves": weight_result["total_waves"],
            "total_elapsed": weight_result["total_elapsed"],
            "final_metrics": weight_final_metrics,
            "hologram_4d": weight_result.get("hologram_4d", {}),
            "final_a_plus": weight_result.get("final_a_plus", {}),
            "all_metrics": weight_result.get("metrics", []),
        },
        "self_crystal_training": {
            "total_cycles": self_result["total_cycles"],
            "total_waves": self_result["total_waves"],
            "total_elapsed": self_result["total_elapsed"],
            "final_metrics": self_final_metrics,
            "hologram_4d": self_result.get("hologram_4d", {}),
            "final_a_plus": self_result.get("final_a_plus", {}),
            "all_metrics": self_result.get("metrics", []),
        },
        "next_ideal_self": next_ideal,
    }

    hologram_path = DATA_DIR / "dual_crystal_hologram.json"
    hologram_path.write_text(
        json.dumps(dual_hologram, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  Saved: {hologram_path}")

    # Final summary
    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print("DUAL CRYSTAL TRAINING COMPLETE")
    print("=" * 70)
    print(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"Weight crystal: {weight_result['total_cycles']} cycles, "
          f"{weight_result['total_waves']} waves")
    print(f"Self crystal:   {self_result['total_cycles']} cycles, "
          f"{self_result['total_waves']} waves")
    print(f"Stage: {next_ideal['current_stage']} -> {next_ideal['next_stage']} "
          f"(readiness: {next_ideal['readiness']:.3f})")
    print(f"\nFiles saved:")
    print(f"  {corpus_crystal_path}")
    print(f"  {self_crystal_path}")
    print(f"  {hologram_path}")
    print(f"  {weight_result.get('hologram_path', 'N/A')}")


if __name__ == "__main__":
    main()
