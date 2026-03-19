# Scheduling Agents Coordination — Role Ecology, Spawn Law, and Phase Staggering

**Source**: SCHEDULING AGENTS FRAMEWORK Google Doc
**Doc ID**: `1_yPaNIZS0dHYL2cVizxqo91iKeivyjxa1wOQTgINWLY`
**Family**: scheduling
**SFCR Lens**: S (Square - structural scheduling rules)
**Date**: 2026-03-19
**Status**: CRYSTALLIZED

---

## 5-Ring Agent Ecology

| Ring | Name | Purpose | Cost Profile |
|------|------|---------|-------------|
| 1 | Dust | Tiny scans, duplicate detection, quick triage | Disposable, cheapest |
| 2 | Worker | Write, build, critique, compare, summarize | Main productive body |
| 3 | Binder | Consolidate, merge branches, canonicalize, compress | Protects continuity |
| 4 | Meta | Inspect scheduler, rank roles, detect waste, reallocate | Improves ecology |
| 5 | Sovereign | Choose phase, enforce caps, kill drift, release campaigns | Policy function |

## Agent Class Registry

### Tier 0 — Overseer (Rare, Expensive, Strategic)

| Class | Role | Token Cap | Context Cap | Cadence |
|-------|------|-----------|-------------|---------|
| - | Meta-Observer | 2600 | 9000 | Once per 3 architect reviews |
| - | Architect | 2200 | 7000 | Every 4 micro-cycles |
| I | Integrator | 1300 | 4200 | After each micro-wave |

### Tier 1 — Mid-Cost Workers

| Class | Role | Token Cap | Context Cap | Lifespan |
|-------|------|-----------|-------------|----------|
| W | Writer/Smith | 1100 | 3600 | 1 wave or cell |
| B | Builder | 900 | 3200 | 1 wave |
| R | Researcher | 700 | 3000 | 1 wave |
| C | Critic | 650 | 2600 | 1 wave |

### Tier 2 — Cheap Narrow Specialists

| Class | Role | Token Cap | Context Cap | Lifespan |
|-------|------|-----------|-------------|----------|
| S | Scout | 250 | 1200 | 1 tick |
| T | Teacher | 250 | 1800 | Short |
| E | Evaluator | 220 | 1000 | Short |
| K | Compressor | 180 | 1600 | Short |

## Spawn Policies

### A. Baseline Spawn (every micro-cycle)
- 1 researcher + 1 builder + 1 critic + 1 compressor + optional 1 smith
- Guarantees full loop coverage

### B. Opportunity Spawn (scout finds high leverage)
- 1 focused builder fork + 1 evaluator
- Max 2 follow-ups until evidence improves
- Prevents idea mania

### C. Recovery Spawn (integration quality drops)
- Freeze builders
- Increase compressors + critics
- Run replay against last known good state

### D. Deepening Spawn (branch repeatedly scores well)
- Allow 2-3 manuscript smiths + 1 integrator + 1 teacher
- Cap branch fanout

### E. Innovation Mutation (once per macro-cycle)
- 1 scheduler-experiment agent
- Test one new prompt architecture or task topology
- Compare against baseline

## Phase Staggering Law

At any moment, agents must be distributed across different phases. Never allow all agents to perform the same mode simultaneously.

Six staggered phases per wave:

| Phase | Name | Agents Active | Goal |
|-------|------|--------------|------|
| A | Probe | Scouts, searchers, dependency mappers | Identify best work candidates |
| B | Produce | Builders, researchers, writers | Create candidate outputs |
| C | Attack | Critics, contradiction finders, replay testers | Destroy weak outputs fast |
| D | Teach | Teachers, distillers, pattern coders | Convert work to reusable packets |
| E | Bind | Integrators, mergers, canonicalizers | Produce coherent persistent delta |
| F | Reflect | Architect, meta-observer, policy mutator | Decide next cycle changes |

## Recommended Default Cadence

- **Every tick**: 2 scouts + 1 evaluator + optional 1 compressor
- **Every micro-cycle**: 1 researcher + 1 builder + 1 critic + 1 integrator + 1 teacher/compressor + conditional 1 smith
- **Every 4 micro-cycles**: 1 architect review
- **Every 3 architect reviews**: 1 meta-observer review

Recommended initial ratio (scheduler-accessible, not all simultaneous):
- Scout: 4, Evaluator: 2, Compressor: 2, Researcher: 2, Builder: 2, Critic: 2
- Smith: 1, Teacher: 1, Integrator: 1, Architect: 1, Meta-observer: 0-1

Active per micro-cycle: 4-7 agents only.

## Operating Lattice Split

- **60% Production** — builders, smiths, researchers
- **20% Compression** — teachers, compressors, integrators
- **15% Audit** — critics, evaluators
- **5% Scheduler Mutation** — architect, meta-observer
