# KC27 Repair Field — Repair Operators, Restoration Grammar, Shamanic Echo

**Source**: KC27 INVERSE REPAIR | **Doc ID**: `11iwlmMouvyW1MTHFme9J7j1uYBINeMqevgV1MqWT6-0` | **Family**: kc27 | **Lens**: R (Fractal - inverse/repair recursion)
**Chapter**: 17 (Book VI) | **Crystal Role**: REPAIR-FLOWER | **Mirror**: Ch11 (Truth Classes and Ambiguity)
**Gate**: 17 — prime, non-recursive: the non-reducible repair unit

---

## Core Function

Ch17 provides the **Repair Operators** — the exact operator suite that maps a naming object from F_fail (Ch16) back into the canonical region. It builds the **Restoration Grammar** (lawful repair sequence) and identifies the **Shamanic Echo**: the invariant residue that persists through every repair, proving canonical identity is recoverable even after deep failure. Mirrors Ch11: where Ch11 identifies ambiguity strata, Ch17 collapses them.

## 9 Repair Operators

| Op | Name | Targets | Confidence |
|----|------|---------|-----------|
| RO_01 | ADDRESS_REISSUE | AB_01, PC_01 | FULL |
| RO_02 | LINEAGE_STITCH | PC_02, AB_02 | DEGRADED (0.92) |
| RO_03 | TYPE_CORRECT | PC_03, AB_03, AB_08, AB_09 | FULL |
| RO_04 | SCALE_PROPAGATE | PC_04, AB_06, AB_07 | FULL |
| RO_05 | PROMOTION_SUSPEND | PC_05, AB_10 | SUSPENDED |
| RO_06 | ZERO_KEY_SALT | PC_06 | FULL |
| RO_07 | WITNESS_RECONSTRUCT | PC_02, AB_05 | DEGRADED (0.87) |
| RO_08 | ROUTE_REDERIVE | AB_04, AB_11 | SUSPENDED |
| RO_09 | COMPRESSION_AUDIT | AB_12 | DEGRADED (0.95) |

Grouped by target Nucleus condition:
- A-repairs (Addressable): RO_01, RO_03, RO_04, RO_06 (4 ops)
- W-repairs (WitnessStable): RO_02, RO_07 (2 ops)
- R-repairs (ReplayBearing): RO_08, RO_09 (2 ops)
- L-repairs (LineageClosed): RO_05 (1 op)

## Restoration Grammar — 5-Phase Pipeline

```
PHASE 1 — TYPE STABILIZATION
  Apply RO_03 if PC_03 or AB_08 or AB_09 detected
  Precondition for Phase 2: type is stable and determinate

PHASE 2 — ADDRESS RECONSTRUCTION
  Apply RO_04, RO_06, RO_01 as needed
  Precondition for Phase 3: Lambda(xi') is valid and unique

PHASE 3 — LINEAGE REPAIR
  Apply RO_02, RO_07 as needed
  Precondition for Phase 4: lineage chain has no structural gaps

PHASE 4 — REPLAY RESTORATION
  Apply RO_08, RO_09 as needed
  Precondition for Phase 5: replay is bearing, route keys current

PHASE 5 — PROMOTION GATE
  CanonicalName = TRUE  -> emit Repair Receipt
  eta = 3              -> apply RO_05, emit ContinuationSeed
  eta < 3              -> escalate to Ch18 (regime assessment)
```

The grammar enforces Nucleus condition dependency: address before witness, witness before replay, replay before promotion.

## The Shamanic Echo

**Canonical Residue** rho(xi) = intersection of all fields invariant under the full repair suite.

**Shamanic Echo Theorem (Th17.1)**: For any xi with eta(xi) >= 1, rho(xi) is non-empty. It always contains:
1. The **origin timestamp** of xi's first naming event
2. The **type class** at origin (even if subsequently corrected)
3. The **zero-key hash** of xi's original payload (pre-transformation)

No operator in the suite erases these three. Repair is transformation, not replacement. The origin whispers through every repair layer.

## Key Theorems

**Repair Convergence (Th17.2)**: Restoration Grammar applied to any xi in F_fail terminates in finite steps — either achieving CanonicalName=TRUE or eta=3 with a ContinuationSeed.

**Operator Independence (Th17.3)**: Within each grammar phase, operators are pairwise independent (order does not matter).

**Degraded Confidence Floor (Th17.4)**: Confidence = product of individual DEGRADED operator confidences. Minimum for RC-A certification: 0.80.

## Key Algorithm: Retroactive Gap Fill (Alg 17.2)

Locates last confirmed anchor before a lineage gap and first anchor after it, derives minimum-edit-distance intermediate state from corpus scan, constructs a Gap Certificate with Jaccard confidence score, and inserts it into the lineage chain.

## Feeds

- Ch18 (escalation when eta < 3 after full repair)
- Ch21 (runtime implements Restoration Grammar)
- AppO (all Repair Receipts and Gap Certificates logged)
