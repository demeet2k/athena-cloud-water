# 403 — KC27 Promotability Chain (Five-Pass Admissibility Engine)

- **Source:** KC27 3
- **Doc ID:** 1nyDliFZp6oXa1EQURxcY23-BFdO7_sO88264p859cEI
- **Family:** kc27
- **Lens:** S

---

## Governing Law

```
Promotable(x) = KernelClosed(x) AND CellCompilable(x) AND LineageClosed(x) AND MapReplayValid(x)
```

Current status vector: (K,C,L,M,P) = (OPEN, FROZEN, OPEN, BLOCKED, FILTERED)

Crown admission is only downstream of those four passes. Crown claims remain filtered applicants, never governing authorities.

## Exact Pass Matrix

### KernelPass = K1 AND K2 AND K3 AND K4 AND K5

| Sub-pass | Content | Status |
|----------|---------|--------|
| K1 | Canonical 4x4 seed object frozen | Seated |
| K2 | Cloud fiber theorem frozen | Seated |
| K3 | Fractal exactness theorem frozen | Seated |
| K4 | All six pairwise bridge operators frozen | FRONTIER |
| K5 | Four-way Mobius-equivariant closure criterion frozen | FRONTIER |

Root kernel object:
- L4 = [[1,2,3,4],[3,4,1,2],[4,3,2,1],[2,1,4,3]]
- ell4 = L4 - 1
- M4 = (M4, K, Pi_square, Pi_flower, Pi_cloud, Pi_fractal, omega, tau)

Bridge body status:
- B_square-flower, B_flower-cloud, B_square-fractal: near/seated
- B_cloud-square (refinement-bound), B_fractal-flower, B_cloud-fractal: pressure-bearing frontier

K5 requires proving all four lenses descend compatibly under Mobius quotient/gluing law, not just pairwise.

### CellPass = C1 AND C2 AND C3 AND C4

| Sub-pass | Content | Status |
|----------|---------|--------|
| C1 | Row schema frozen | FROZEN |
| C2 | Packet law frozen | FROZEN |
| C3 | Trace/cert law frozen | FROZEN |
| C4 | Continuation-seed law frozen | FROZEN |

Cell is substrate, not active frontier. Cell_live = (Row, Packet, Transition, Trace, Cert, Seed).

### LineagePass = L1 AND L2 AND L3 AND L4

| Sub-pass | Content | Status |
|----------|---------|--------|
| L1 | Manifest bytes materialized | OPEN |
| L2 | Actual replay executed | OPEN |
| L3 | Proof root bound | OPEN |
| L4 | Real replay-closed trace exists | OPEN |

Anti-fake law: not-L2 OR not-L3 => not-L4.

### MapPass = M1 AND M2 AND M3

| Sub-pass | Content | Status |
|----------|---------|--------|
| M1 | Constructive atlas fully specified | Near |
| M2 | Witness transforms replay exactly | BLOCKED |
| M3 | Reweave only applied after closure | Held |

### CrownPass = KernelPass AND CellPass AND LineagePass AND MapPass

## Active Frontier Theorem (Th14.2)

Minimum live frontier: F_live = {K4, K5, L1, L2, L3, L4}

M2 is the first downstream replay gate. Crown held in filter state.

Next lawful scheduler: P1 || P2 -> P3 -> P4 (not linear chapter restatement, not crown-first expansion).

## Core Invariants

- Cloud fiber admissibility: z congruent to w (mod 2)
- Fractal exactness: digitwise ell4 replay
- Mobius equivariance: J(x,y,epsilon) = (y,x,-epsilon)
- Replay-before-promotion
- Identity-preserving transport
- Truth lattice: OK / NEAR / AMBIG / FAIL

## Route Priority

1. P1 Kernel Proof Route: Ch07->Ch08->Ch09->Ch13->Ch14->Ch15->Ch21
2. P2 Lineage Closure Route: Ch14->Ch13->Ch15->Ch21->Ch25->Ch27
3. P3 Map Legality Route: Ch09->Ch19->Ch24->Ch25
4. P4 Claim Filter Route: Ch11->Ch13->Ch15->Ch21->Ch25->Ch27

## Support Spine

AppA (registry/names) | AppI (corridor-checks) | AppN (replays and closes)

Any whole-tome claim that cannot pass registry, corridor, and replay is non-canonical.

## Compression Digest

Kernel Program || C2 Lineage Program inside Cell Substrate -> Map Judge -> Crown Filter
