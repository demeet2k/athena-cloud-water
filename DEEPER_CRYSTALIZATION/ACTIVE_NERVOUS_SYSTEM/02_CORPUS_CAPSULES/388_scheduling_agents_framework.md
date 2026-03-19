# Scheduling Agents Framework — Pulse-Based Ecology and Token Economy

**Source**: SCHEDULING AGENTS FRAMEWORK Google Doc
**Doc ID**: `1_yPaNIZS0dHYL2cVizxqo91iKeivyjxa1wOQTgINWLY`
**Family**: scheduling
**SFCR Lens**: S (Square - structural scheduling rules)
**Date**: 2026-03-19
**Status**: CRYSTALLIZED

---

## Core Law

The scheduler is not a queue. It is a **resource-governed evolutionary crystal** and an **entropy management engine**. The fundamental equation:

```
Perpetual progress = high-value deltas surviving / token entropy
```

The system must maximize useful project progress per token, continuity across cycles, high-impact self-improvement discovery, and cross-agent teaching. It must minimize duplicate work, context bloat, recursive chatter, fork divergence without merge, and runaway token burn.

## 7-Layer Architecture

1. **Pulse Layer** — Global cadence determining what work is allowed now
2. **Budget Layer** — Hard token budgets per agent and per wave
3. **Role Layer** — Distinct agent species with different cost profiles
4. **Spawn Layer** — Nested staggered loop logic for agent creation
5. **Selection Layer** — Scoring, ranking, deduplication, promotion, rejection
6. **Compression Layer** — Summaries, deltas, merges, witness bundles
7. **Memory Layer** — Stable working memory, task lineage, manuscript state

## Impact Density (Core Scheduling Metric)

```
ImpactDensity = (ExpectedImpact * Mergeability * StrategicRelevance * NoveltyWeight)
              / (ExpectedTokens * DuplicationRiskPenalty * DriftPenalty)
```

Agents are spawned only if their projected impact density exceeds threshold.

## Token Budget Structure

Five buckets with recommended initial split:

| Bucket | Allocation | Purpose |
|--------|-----------|---------|
| Exploration | 20% | Scouts, speculative work |
| Exploitation | 35% | Building on known good directions |
| Integration | 20% | Merge, compression, canonicalization |
| Audit | 15% | Criticism, replay, quality checks |
| Mutation | 10% | Scheduler improvements, role experiments |

Hard caps at every level:
- Agent: `prompt_cap`, `context_cap`, `output_cap`, `retry_cap`
- Wave: `wave_cap`, `promotion_cap`, `survivor_cap`
- Cycle: `cycle_cap`, `branch_cap`, `archive_cap`

## Nested Temporal Cycles (5 Scales)

| Scale | Name | Duration | Purpose |
|-------|------|----------|---------|
| T0 | Pulse Tick | 1 decision | Cheap local motion |
| T1 | Wave | 4-12 ticks | Produce scored survivors |
| T2 | Cell Cycle | Several waves | Deepen one topic area |
| T3 | Campaign | Several cells | Sustained strategic theme |
| T4 | Epoch | Largest | Retune whole ecology |

## Perpetual Pulse Engine

Six-phase rotation preventing synchronized waste:

```
P = [SCAN, BUILD, CRITIQUE, DISTILL, MERGE, REFLECT]
```

Each pulse changes spawn weights. SCAN amplifies scouts; BUILD amplifies builders; CRITIQUE amplifies critics; DISTILL amplifies teachers/compressors; MERGE amplifies integrators; REFLECT activates architect + meta-observer.

## The 10 Token-Saving Laws

1. Most agents must be short-lived and narrow
2. Every wave must end in compression
3. Only promoted outputs enter persistent memory
4. Agents teach via packets, never full transcripts
5. Branch count must be capped
6. Scheduler self-improvement gets only a small budget
7. Integration must happen frequently, not at the end
8. Exploration and exploitation separated by pulse
9. Use impact density, not subjective excitement
10. Most outputs should die

## Compression Law

Every artifact must exist in 4 forms:

| Form | Compression Ratio |
|------|------------------|
| Raw | 1:1 (original) |
| Working summary | 10:1 |
| Canonical packet | 40:1 |
| Index metadata | 200:1 |

**Anti-bloat invariant**: No agent may read more than 2 raw artifacts, 5 working summaries, or 12 canonical packets.

## Promotion Gates

5 gates (all must pass sufficient threshold):

1. **Local usefulness** — Does it help the current task?
2. **Novelty** — Is it actually new?
3. **Mergeability** — Can it fit existing architecture?
4. **Compression-worthiness** — Can it survive as a small packet?
5. **Strategic leverage** — Will it unlock future work?

Scoring: `0.30*impact + 0.20*novelty + 0.20*mergeability + 0.15*compression_worth + 0.15*strategic_fit`

## Starter Config

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
```
