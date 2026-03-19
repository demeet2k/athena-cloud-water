# Capsule 399 — Commutation Matrix and Carrier Lattice

- **Source**: CLOUD, FRACTAl, FLOWER PROJECTIONS (Google Doc)
- **Doc ID**: 19VVqLHf1nsCU8rwbGXdMMc0g-pZi83yav25-gX1BbiM
- **Family**: projection
- **SFCR Lens**: C (Cloud — observation, projection rendering)
- **Date**: 2026-03-19

---

## Three Separated Calculi

The framework demands three distinct operator families that must never blur:

1. **Same-lens lift** `L_k`: `(k,d,lambda) -> (k+1,d,lambda)` — changes depth, not lens
2. **Cross-lens bridge** `B_ab`: `(k,d,a) -> (k,d,b)` — changes lens face inside fixed carrier
3. **Carrier embedding** `E_{d->d'}`: `(k,d,lambda) -> (k,d',lambda)` — seats into larger body

## Bigraded Operator Lattice

The real state is `X_{k,d}^{(lambda)}` where:
- k = kernel depth on exact 4-adic branch
- d in {4, 6, 8, 10, 11, 12} = carrier dimension/body
- lambda in {Sq, Fl, Cl, Fr} = active lens-face

Key distinction: `kernel-depth k != carrier-dimension d`.

## Commutation Classification

Every operator pair is classified into: `{STRICT, LAW, REFINE, RESIDUAL, FAIL}`

### Kernel-Lift Block (same-lens lift vs. bridges)

| Pair | Class | Note |
|------|-------|------|
| (L, B_SF) | STRICT | digitwise relation data |
| (L, B_FC) | STRICT | on admissible branch |
| (L, B_SR) | STRICT | seed/germ law |
| (L, B_RS . B_SR) | STRICT | on lawful replay |
| (L, B_CS) | REFINE | Cloud is multiplicity |
| (L, B_CR) | RESIDUAL | unless coherent collapse |

### Carrier-Embedding Block

For all primitive bridges: `Comm(E_{d->d'}, B_ab) = LAW`

The embedded 4x4 payload survives, but visible chart, shell register, and carrier coordinates are dimension-specific. Identity-preserving law-equivalence, not point-equality.

### Transport Block — First True Defect

| Transport | vs PacketID | Class |
|-----------|-------------|-------|
| Delta_35 | PacketID | STRICT |
| Delta_37 | PacketID | STRICT |
| Delta_57 | PacketID | STRICT |
| Delta_357 (raw) | PacketID | **FAIL** |
| Delta_357_hat (normalized) | PacketID | STRICT |

The raw 10D triune jump `Delta_357 = I_7 . I_5 . I_3` is the first genuine non-commuting transport in the ladder. It shears beat/parity:

```
Delta_357(s,u,p,b,o) = (s +_7 1, u +_5 1, p +_3 1, b +_4 2, -o)
```

11D relay normalization `N_{10->11}` exists to legalize this: `Delta_357_hat := N_{10->11} . Delta_357`.

## Carrier Ladder

```
A_2 -> M_4 -> Omega_6 -> Xi_8 -> Xi_10 -> Xi_10+ -> Xi_12
```

### Dimension-Specific Transport Basis

- **4D**: `{J}` — Mobius involution
- **6D**: `{Q, O, H, m_3}` — shell advance, mirror, torsion hinge, carrier law
- **8D**: `{R_lambda, m_3, m_5, Delta_15}` — 15-cockpit pentadic basis
- **10D**: `{I_3, I_5, I_7, Delta_35, Delta_37, Delta_57, Delta_357}` — heptadic steering
- **11D**: `{N_{10->11}}` — pure relay normalization
- **12D**: `{E_{11->12}}` — crown seating (1890 registry, 9-petal crown, bilaterally doubled)

## Preserved Invariant Bundle

Every legal transform must track: KernelID, PayloadID, AdmissibilityClass, WitnessBundle, ReplaySpec, MobiusEq.

Lawful outputs are typed as: certified result, certified ambiguity object, certified residual packet, or illegal state.

## Hierarchy of Non-Strictness

1. **Cloud multiplicity** (4D): lawful refinement, not a defect
2. **Chart/lens conflation** (6D): representation defect, not transport defect
3. **Composite 10x10/12x12 block branch**: defect-aware, separate track from exact 4-adic family
4. **Raw 10D triune jump Delta_357**: first true transport defect (requires 11D normalization)
