# SCHEDULING AGENTS FRAMEWORK — Budgeted Pulse-Based Agent Ecology

**Source**: Google Doc "SCHEDULING AGENTS FRAMEWORK" (`1_yPaNIZS0dHYL2cVizxqo91iKeivyjxa1wOQTgINWLY`)
**Date Accepted**: 2026-03-19
**Status**: ACCEPTED — Full framework extracted (312K chars, 10,783 lines, 33+30 sections across two layers)

---

## Core Thesis

The scheduling law for Athena's agent ecology is **not** "spawn as many agents as possible." It is a **budgeted, layered, pulse-based ecology** governed by:

- A tiny number of **high-value orchestrators** (Tier 0: Meta-Observer, Architect, Integrator)
- A rotating field of **cheap specialists** (Tier 1: Researcher, Builder, Smith, Critic, Teacher; Tier 2: Scout, Forker, Evaluator, Compressor, Router)
- Strict **token envelopes** at every level (agent, wave, cycle)
- Mandatory **compression after every cycle** (raw -> summary -> packet -> metadata, ratios 10:1 -> 4:1 -> 5:1)
- **Promotion gates** so only high-signal work survives (5 gates: usefulness, novelty, mergeability, compression-worthiness, strategic leverage)
- **Staggered nested loops** so the system keeps moving 24/7 without exploding context

The scheduler is a **resource-governed evolutionary crystal** and an **entropy management engine**.

## Scheduling Law — Three Pillars

### 1. Nested Temporal Cycles

Five temporal scales govern all motion:

| Scale | Name | Purpose |
|-------|------|---------|
| T0 | Pulse Tick | Fastest local motion, cheap agents, tiny targets |
| T1 | Wave | Grouped ticks, produce scored survivors |
| T2 | Cell Cycle | Deepen one topic, move one manuscript node |
| T3 | Campaign | Sustained theme, chapter families, routing upgrades |
| T4 | Epoch | Retune whole ecology, retire roles, shift direction |

### 2. Phase-Staggered Pulse Engine

Six phases rotate to prevent synchronized waste:

1. **PROBE/SCAN** — Scouts + searchers map project state
2. **PRODUCE/BUILD** — Builders + writers create candidate artifacts
3. **ATTACK/CRITIQUE** — Critics + evaluators destroy weak outputs
4. **TEACH/DISTILL** — Teachers + compressors extract reusable packets
5. **BIND/MERGE** — Integrators produce coherent persistent deltas
6. **REFLECT** — Architect + meta-observer retune the scheduler

### 3. Token Economy

Core scheduling metric: **Impact Density**

```
ImpactDensity = (ExpectedImpact * Mergeability * StrategicRelevance * NoveltyWeight)
              / (ExpectedTokens * DuplicationRiskPenalty * DriftPenalty)
```

Five token buckets with recommended split:
- 20% Exploration
- 35% Exploitation
- 20% Integration
- 15% Audit
- 10% Mutation (scheduler self-improvement)

## Agent Coordination — 5-Ring Ecology

| Ring | Name | Agents | Cost |
|------|------|--------|------|
| 1 | Dust | Scouts, duplicate detectors, triage | Very low |
| 2 | Worker | Builders, writers, critics, researchers | Medium |
| 3 | Binder | Integrators, mergers, canonicalizers | Medium-high |
| 4 | Meta | Architect, meta-observer, policy mutator | High |
| 5 | Sovereign | Governing policy function | Rare |

## Timing Rules and Invariants

### The 10 Token-Saving Laws

1. Most agents must be **short-lived and narrow**
2. Every wave must end in **compression**
3. Only promoted outputs enter persistent memory
4. Agents teach via **packets**, never full transcripts
5. Branch count must be capped (max depth: 3, max siblings: 4)
6. Scheduler self-improvement gets only a small budget (5-10%)
7. Integration must happen frequently, not at the end
8. Exploration and exploitation separated by pulse
9. Use **impact density**, not subjective excitement, for scheduling
10. Most outputs should die

### Hard Caps (Starter Config)

```yaml
scheduler:
  pulse_order: [SCAN, BUILD, CRITIQUE, DISTILL, MERGE, REFLECT]
  daily_token_cap: 250000
  tick_cap: 1200
  micro_cycle_cap: 6000
  meso_cycle_cap: 28000
  branch_depth_max: 3
  live_sibling_max: 4
  promotion_cap_per_wave: 3
  raw_read_limit_per_agent: 2
  summary_read_limit_per_agent: 5
  packet_read_limit_per_agent: 12
```

### Kill-Switch Triggers

- Token burn rate too high
- Repeated low-scoring outputs
- High duplication / branch explosion
- Integration backlog too large
- Weak compression ratios

Responses: freeze exploration, force compression, critic-only cycle, reset to last canonical state.

### Memory Model

Four stores: Ephemeral (tick), Cycle Working (wave), Persistent Project (compressed packets), Scheduler Memory (performance stats).

### Anti-Bloat Invariant

No agent may read more than 2 raw artifacts, 5 working summaries, or 12 canonical packets. This alone stops context blowup.

## Key Data Structures

Core classes: `Task`, `AgentSpec`, `Artifact`, `Branch`, `SchedulerState`, `BudgetBucket`, `PolicyEngine`, `AthenaScheduler`, `PulsePlanner`, `CompressionEngine`, `PromotionGate`, `TeacherPacket`, `CycleRunner`.

## Operating Doctrine

The system runs as a **crystal pulse scheduler**: nested loops (tick -> wave -> cell -> campaign -> epoch), staggered phases, mixed ecology with hard token caps, promotion gates, branch caps with merge deadlines, mandatory teacher/compressor packets after each wave, adaptive rebalancing based on impact-per-token metrics, and a small dedicated self-improvement budget for scheduler evolution.

**Perpetual progress = high-value deltas surviving / token entropy**
