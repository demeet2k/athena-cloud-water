# Self-Development Plan — Perpetual Crystal Self-Improvement

**Crystal Address**: Xi108:W1:A1:S2:F (Adjacent to Seed — Growth Vector)
**Family**: Neural Crystal Self-Development
**Date**: 2026-03-18
**Status**: ACTIVE PLAN — Executable by Scheduled Agents

---

## Phase 1: Foundation Hardening (Week 1 — 2026-03-18 to 2026-03-24)

### 1.1 Token Vocabulary Expansion
**Goal**: Increase from 2,562 → 5,000+ unique terms
- Parse document excerpts more aggressively (bigrams, compound words)
- Add family labels as token features
- Mine the 170+ corpus capsule titles for additional vocabulary
- **Metric**: avg tokens per doc from 36 → 60+

### 1.2 Adam Optimizer Integration
**Goal**: Replace raw SGD-like updates with Adam
- Add `m_t` (momentum) and `v_t` (variance) storage per learnable parameter group
- Store in `crystal_weights.json` under `"optimizer_state"` key
- Default: β₁=0.9, β₂=0.999, ε=1e-8
- **Metric**: faster convergence — same discrimination in 50% fewer cycles

### 1.3 Curriculum Learning v1
**Goal**: Stop random query selection
- Implement difficulty tiers: easy (same-family) → medium (same-wreath) → hard (cross-wreath)
- Self-play phase determines which tier to draw from
- **Metric**: top-1 accuracy on hard queries from current ~70% to >85%

### 1.4 Deep Run: 100,000 cycles
**Goal**: Push evolved weights significantly further
- 100K cycles across 5 progressive waves with curriculum learning
- Expected runtime: 30–45 minutes
- Checkpoint every 1,000 cycles
- **Metric**: top-1 self-retrieval from 88.6% → 95%+

---

## Phase 2: Architecture Enhancement (Week 2 — 2026-03-25 to 2026-03-31)

### 2.1 Crystal-Native Attention
**Goal**: Replace TF-IDF bag-of-words with learned attention
- Implement Q/K/V projections stored at crystal coordinates
- Attention scores become new pair weights (replacing/augmenting static ones)
- Each self-play cycle refines attention projections
- **Metric**: F-path discrimination without pure TF-IDF dominance

### 2.2 Skip Connections Between Shells
**Goal**: Enable gradient flow to distant shells
- Add identity shortcuts: score_k += α * score_{k-3}
- α starts at 0.1, learnable through self-play
- **Metric**: shell-level weight variance decreases (more uniform learning)

### 2.3 S/C/R Path Enrichment
**Goal**: Make non-F paths genuinely useful
- S-path: add structural features (document length, family size, position in index)
- C-path: add neighbor diversity score (how many distinct families in neighbors)
- R-path: add compression ratio features (how well seed predicts full weight)
- **Metric**: F-path weight drops below 60% while accuracy holds or improves

### 2.4 Normalization Layer
**Goal**: Prevent score scale drift during self-play
- Add per-path score normalization (z-score within each path)
- Prevents any single path from dominating by magnitude alone
- **Metric**: score distributions per path have mean≈0, std≈1

---

## Phase 3: Deep Integration (Week 3 — 2026-04-01 to 2026-04-07)

### 3.1 Manuscript Live Sync
**Goal**: Automatically ingest new Google Docs content
- Scheduled agent reads all 6 key Google Docs
- Diffs against last-known content
- Creates corpus capsules for new sections
- Re-imports into weight store
- Runs targeted 1,000-cycle self-play on new entries
- **Metric**: new docs achieve >85% self-retrieval within 1 hour of creation

### 3.2 Cross-Repository Weight Sharing
**Goal**: Sync crystal weights to 4 element repos
- Export path-specific weights to element repos (S→square, F→flower, C→cloud, R→fractal)
- Each element repo runs element-specific self-play
- Merge back via bridge weights
- **Metric**: element repos produce meaningful element-filtered search results

### 3.3 Holographic Projection Engine
**Goal**: Implement the 148D+ projection formally
- Extend crystal coordinates to include learnable parameter dimensions (109–148)
- Each self-play run updates positions in the extended manifold
- Holographic seed equation applies to the full 148D space
- **Metric**: compression cascade works at 148D (seed = 18.5D → micro = 2.3D)

### 3.4 Deep Run: 500,000 cycles
**Goal**: Massive deep cultivation with all enhancements
- All Phase 1+2 improvements active
- Curriculum learning at hard/adversarial tier
- Expected runtime: 2–3 hours
- **Metric**: top-1 >97%, discrimination gap >0.5

---

## Phase 4: Emergence (Week 4+ — 2026-04-08 onward)

### 4.1 Multi-Agent Self-Play
**Goal**: Multiple engine instances play against each other
- Engine A generates queries, Engine B answers
- Compare answers against ground truth
- Both engines update from the outcome
- **Metric**: adversarial accuracy >90%

### 4.2 Meta-Learning (Learning to Learn)
**Goal**: Learn optimal learning rate schedules
- Track which LR schedules produced best improvement per phase
- Store optimal schedules as meta-weights
- Future self-play runs use learned schedules
- **Metric**: same improvement in 30% fewer cycles

### 4.3 Knowledge Distillation
**Goal**: Compress full model into nano-seed that still works
- Teacher: full 38K-weight model at 95%+ accuracy
- Student: 4-value nano-seed with learned decompression
- Train student to mimic teacher rankings
- **Metric**: nano-seed model achieves >80% accuracy (vs teacher's >95%)

### 4.4 Perpetual Motion
**Goal**: The system improves itself indefinitely without human intervention
- Scheduled agents run cultivation cycles
- New manuscript content is auto-ingested
- Architecture improvements are proposed by the weekly reviewer agent
- Human only intervenes for major structural decisions
- **Metric**: monotonic improvement in self-retrieval over 30-day window

---

## Internal Schedule — Concrete Cadence

### Every 6 Hours: CULTIVATE
```bash
# Run 5,000 self-play cycles with current best weights
run_self_play(cycles=5000, query_source="curriculum", max_time_minutes=30)
```

### Every 12 Hours: INGEST
```bash
# Scan Google Docs for updates
# Create corpus capsules for new content
# Re-import weights
# Run targeted self-play on new entries
```

### Daily: AUDIT
```bash
# Verify compression fidelity: seed vs full reconstruction error
# Check weight distribution health (no collapse, no explosion)
# Log metrics to meta-observer
```

### Weekly: ARCHITECT
```bash
# Full system analysis
# Weight distribution report
# Propose architecture changes
# Generate holographic crystal capsule update
```

### Monthly: EVOLVE
```bash
# Major structural review
# Consider architecture upgrades (attention, skip connections, etc.)
# Run 500K+ deep cultivation
# Update self-development plan
```

---

## Success Criteria

| Metric | Current | Week 1 | Week 2 | Week 3 | Week 4+ |
|---|---|---|---|---|---|
| Top-1 Self-Retrieval | 88.6% | 95% | 97% | 98% | 99%+ |
| Token Vocabulary | 2,562 | 5,000 | 5,000 | 6,000+ | 8,000+ |
| F-Path Dominance | 79.6% | 75% | <60% | <50% | balanced |
| Discrimination Gap | 0.39 | 0.45 | 0.50 | 0.55 | 0.60+ |
| Total Self-Play Cycles | 40K | 140K | 340K | 840K | 2M+ |
| Corpus Size | 197 docs | 200+ | 220+ | 250+ | 300+ |
| Auto-Ingest Working | No | No | No | Yes | Yes |

---

*This plan is self-modifying. Each weekly ARCHITECT review updates the plan based on observed progress. The crystal doesn't follow a fixed roadmap — it learns what to learn next.*
