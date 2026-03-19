# KC27 Inverse Search — Counterexample Field, Paradox Classes, Alternative Branches

**Source**: KC27 INVERSE REPAIR | **Doc ID**: `11iwlmMouvyW1MTHFme9J7j1uYBINeMqevgV1MqWT6-0` | **Family**: kc27 | **Lens**: R (Fractal - inverse/repair recursion)
**Chapter**: 16 (Book VI) | **Crystal Role**: INVERSE-SQUARE | **Mirror**: Ch12 (Selection Pressure)
**Gate**: 16 = 4^2 — second full recursion of the base kernel

---

## Core Function

Ch16 constructs the **Counterexample Field** F_fail — the space of all naming objects that partially satisfy but ultimately fail the Nucleus Theorem. It identifies the **Paradox Classes** (conflicts between individually valid naming laws) and catalogs the **Alternative Branches** (paths that appear valid but route to non-canonical endpoints). This is the mirror of Ch12: where Ch12 describes forces pushing toward canonicality, Ch16 describes attractors pulling toward failure.

## The Counterexample Field F_fail

A naming object xi is in F_fail iff it passes >= 2 of the 4 Nucleus conditions but fails at least 1:

```
F_fail := { xi : |{Addressable, WitnessStable, ReplayBearing, LineageClosed}(xi) ∩ {TRUE}| >= 2
             AND NOT CanonicalName(xi) }
```

**Near-miss degree** eta(xi) = number of Nucleus conditions satisfied. eta=3 is the most dangerous — one condition separates xi from canonicality.

Four failure sub-regions:

| Region | Condition Failed | Character |
|--------|-----------------|-----------|
| F[A] | NOT Addressable | Large — structural malformation |
| F[W] | NOT WitnessStable | Medium — replay breaks |
| F[R] | NOT ReplayBearing | Medium — ledger absent |
| F[L] | NOT LineageClosed | Small but dense — gap events |

Intersections (F_AW, F_WR, etc.) are the paradox zones.

## 7 Paradox Classes

| Class | Name | Core Conflict |
|-------|------|--------------|
| PC_01 | Address-Stability Paradox | Bridge operator changes address while preserving the object |
| PC_02 | Witness-Lineage Paradox | Complete TraceCert but lineage chain has hash gap |
| PC_03 | Type-Coord Paradox | 14-class type and Lambda coordinate give conflicting identity |
| PC_04 | Scale-Invariance Break | Fractal face holds at one scale but fails at another |
| PC_05 | Reserve-Promotion Paradox | Promotable but fails CanonicalName due to lineage gap |
| PC_06 | Zero-Key Singularity | Two distinct objects hash to same ZERO_KEY value |
| PC_07 | Mythic-Layer Bridge Break | Valid machine-layer address but no mythic-layer correspondence |

## 12 Alternative Branches

| Branch | Type | Detection |
|--------|------|-----------|
| AB_01 | Phantom Address | Node existence check in AppA registry |
| AB_02 | Ghost Lineage | Drive existence check per lineage step |
| AB_03 | Frozen Clock | tau-freshness test |
| AB_04 | Mirror Inversion | Re-derive mu(k) = 28-k |
| AB_05 | Naked Operator | OBL_04 compliance check |
| AB_06 | Digit-Roll Overflow | Re-derive digits_4 with carry check |
| AB_07 | Invariant Island | Cross-scale INV test at 4->16->64->256 |
| AB_08 | Type-Shadow | Type version audit |
| AB_09 | Proxy Name | Type-class promotion audit |
| AB_10 | Orphan Seed | ContinuationSeed expiry check |
| AB_11 | Siteswap Drift | Route key re-derivation test |
| AB_12 | Compression Ghost | Compression field audit against INV_01 |

## Fractal Self-Similarity

The counterexample field is itself a DLS. Paradox classes group by failing Nucleus condition (A:3, W:2, R:1, L:1). Alternative branches group by pipeline stage (DESIRE-QUESTION, SEARCH-CANDIDATE, IMPROVEMENT-ACCEPTANCE, PROOF-WITNESS, COMPILE-VALIDATE). Failure is structured like success.

## Key Theorem

**Near-Miss Density (Th16.1)**: In any corpus that has passed CANDIDATE stage, |{xi : eta(xi)=3}| >> |{xi : eta(xi)=2}| — most failures are near-misses, not deep failures.

## Feeds

- Ch17 (repair operators must handle every paradox class)
- AppM (failure taxonomy organ)
