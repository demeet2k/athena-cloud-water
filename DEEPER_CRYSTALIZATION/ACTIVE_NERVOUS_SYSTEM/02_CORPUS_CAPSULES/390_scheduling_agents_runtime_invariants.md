# Scheduling Agents Runtime Invariants — Kill-Switches, Memory, Self-Play, and Fork/Merge Law

**Source**: SCHEDULING AGENTS FRAMEWORK Google Doc
**Doc ID**: `1_yPaNIZS0dHYL2cVizxqo91iKeivyjxa1wOQTgINWLY`
**Family**: scheduling
**SFCR Lens**: S (Square - structural scheduling rules)
**Date**: 2026-03-19
**Status**: CRYSTALLIZED

---

## Memory Architecture (4 Stores)

| Store | Scope | Content |
|-------|-------|---------|
| Ephemeral | Current tick only | Raw agent outputs, local state |
| Cycle Working | One micro-cycle | Intermediate results, candidate rankings |
| Persistent Project | Permanent | Compressed packets, stable summaries, canonical state |
| Scheduler Memory | Permanent | Performance stats, spawn outcomes, cost/benefit history |

## Fork/Merge Framework

### Fork Rules
Every branch gets a budget with metadata: `branch_id`, `parent`, `purpose`, `token_budget_remaining`, `survival_score`, `merge_deadline`, `branch_depth`.

### Hard Limits
- Max branch depth: 3
- Max live siblings per parent: 4
- Mandatory merge or archive decision after 2 micro-cycles

### Four Merge Modes
1. **Dominant merge** — winner absorbs fragments
2. **Braided merge** — combine complementary sections
3. **Extractive merge** — take only operator packets
4. **Abortive merge** — archive all, keep lessons only

## Kill-Switches and Anti-Runaway Controls

### Trigger Conditions
- Token burn rate too high
- Repeated low-scoring outputs
- High duplication rate
- Branch explosion
- Integration backlog too large
- Average compression ratio too weak

### Emergency Responses
- Freeze exploration
- Freeze forking
- Force compression pass
- Run critic-only cycle
- Reset to last canonical state
- Lower context caps

## Self-Play Protocol

### Good Self-Play (Bounded, Artifact-Producing)
- Generator vs critic
- Architect vs skeptic
- Compressor vs decompressor
- Fork A vs Fork B vs evaluator

### Bad Self-Play (Must Be Killed)
- Endless debate
- Recursive philosophy
- Identity theater
- Multi-agent roleplay with no artifact output

### Self-Play Round Format (Max 5 Rounds)
1. Builder proposes artifact
2. Critic attacks with 3 strongest objections
3. Builder patches
4. Evaluator scores before/after delta
5. Compressor extracts lesson

No more than 2 repair rounds unless score gain is demonstrably large.

## Teaching Loop

### Teacher Packet Format
```json
{
  "topic": "...",
  "why_it_matters": "...",
  "pattern": "...",
  "anti_pattern": "...",
  "when_to_use": ["..."],
  "when_not_to_use": ["..."],
  "canonical_steps": ["..."],
  "example_delta": "...",
  "estimated_reuse_score": 0.81
}
```

Routers inject packets into downstream prompts instead of passing full transcripts. This is one of the biggest token savers.

## Canonical Output Contract

Every agent output must be machine-mergeable:

```json
{
  "agent_role": "builder",
  "task_id": "task_1042",
  "topic": "chapter 11 scheduling law",
  "artifact_type": "manuscript_delta",
  "summary": "adds branch budget law",
  "body": "...",
  "claims": ["..."],
  "dependencies": ["artifact_88", "packet_12"],
  "novelty_score": 0.67,
  "mergeability_score": 0.84,
  "estimated_impact": 0.72,
  "estimated_tokens_used": 812,
  "next_recommended_action": "critic_review"
}
```

## Manuscript Scheduling State Machine

Each chapter exists in one state, transitions governed by agent roles:

```
seeded -> outlined -> expanded -> criticized -> compressed -> integrated -> canonical -> archived_for_revision
```

- **Seed**: Researcher + Architect define purpose, claims, dependencies
- **Outline**: Smith creates structured outline
- **Expand**: Builder/Smith expands sections
- **Critique**: Critic attacks redundancy, unsupported jumps, weak synthesis
- **Compress**: Teacher + Compressor extract operator packets
- **Integrate**: Integrator merges into master manuscript
- **Canonical**: Frozen until new evidence arrives

## Infrastructure Self-Improvement Law

Infra task families: prompt refactoring, template refinement, budget tuning, scheduler mutation, compression schema improvement, routing upgrades, branch merge heuristics, archive policy updates.

**Critical invariant**: Only 5-10% of total budget targets scheduler self-modification. Self-improving systems love narcissistic loops.

### Mutation Protocol
1. Propose mutation
2. Simulate on recent tasks
3. Compare baseline vs mutated scheduler
4. Keep only if: lower tokens for same quality OR higher quality for same tokens

## Convergence Metrics

### Progress
- Promoted artifacts / cycle
- Canonical deltas / cycle
- Chapters advanced / cycle

### Efficiency
- Tokens / promoted artifact
- Compression ratio
- Duplicate artifact rate

### Health
- Branch entropy
- Unresolved contradiction count
- Archive backlog, context pressure, retry waste

### Emergence
- Cross-domain merge count
- Teacher packet reuse rate
- Scheduler mutation success rate
- Strategic goal coverage

## Adaptive Quota Rebalancing (Every Meso-Cycle)

Compute: which role produced most promoted outputs per token, highest downstream reuse, most duplication, and which topic consumed tokens without convergence. Then rebalance spawn weights accordingly.

## Project Search Hierarchy

Three-level search to control token usage:
1. **Index search** — Read metadata only
2. **Summary search** — Read compressed packets only
3. **Targeted raw read** — Original artifact only if strongly justified

Query types: unresolved bottlenecks, repeated failures, underdeveloped sections, abandoned branches, high-centrality nodes, low-cost/high-impact opportunities.
