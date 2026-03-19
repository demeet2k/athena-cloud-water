# 404 — KC27 C2 Replay Lineage (First Honest Proving Ladder)

- **Source:** KC27 3
- **Doc ID:** 1nyDliFZp6oXa1EQURxcY23-BFdO7_sO88264p859cEI
- **Family:** kc27
- **Lens:** S

---

## The C2 Lineage Ladder

The first honest runtime specialization is the C2 proving ladder. The first admissible runtime specialization is not a vague "system" but the already-frozen live cell. The first honest proving lineage is not general lineage in the abstract; it is the C2 ladder:

```
MAN.C2.HAWL.001.v1 -> GoldenReplayGateTest -> D_proof -> ReplayClosedTrace_v1
```

This is the unique canonical path from manifest to closed trace.

## RuntimeCard Rt_C2

```
C2_Actualize: manifest -> replay -> proof-bind -> trace-close
```

## Lineage Pass Body (L1-L4)

| Step | Artifact | Description | Current State |
|------|----------|-------------|---------------|
| L1 | Manifest bytes | MAN.C2.HAWL.001.v1 materialized in store | NEAR / RESIDUALIZED |
| L2 | Actual replay | GoldenReplayGateTest executed with receipts | DEFER_NEAR |
| L3 | Proof root bound | D_proof index bind completed | Absent |
| L4 | Replay-closed trace | ReplayClosedTrace_v1 emitted | Absent |

**Anti-fake law:** No replay without store-backed manifest. No closed trace without replay and proof-bind. No Crown reuse of C2 until replay receipts exist.

```
not-L2 OR not-L3 => not-L4
```

## Cert Burden

Three non-negotiable constraints on C2 lineage closure:

1. **No replay without store-backed manifest** — L1 must precede L2. The manifest bytes must exist in store, not just be declared.
2. **No closed trace without replay and proof-bind** — L2 AND L3 must both be satisfied before L4 can be claimed. This is the anti-fake law.
3. **No Crown reuse of C2 until replay receipts exist** — Crown cannot cite C2 closure until the full ladder has been climbed with store-backed evidence at each step.

## GoldenReplayGateTest

The golden replay gate test is the exact criterion for L2 satisfaction:
- Input: canonical seed or lineage manifest
- Output: exact/typed replay verdict + receipts
- Law: seed identity and declared truth class must survive execution

A runtime is replay-honest if and only if the seed identity and declared truth class survive execution.

## Cell Substrate (Frozen)

The C2 lineage operates inside the already-frozen cell substrate:

```
Cell_live = (Row, Packet, Transition, Trace, Cert, Seed)
```

Cell is substrate, not frontier. The cell pass is already FROZEN:
- C1: row schema frozen
- C2: packet law frozen
- C3: trace/cert law frozen
- C4: continuation-seed law frozen

## Parallel Front Law (Th14.2)

Kernel Program || C2 Lineage Program is the unique highest-yield active decomposition of the current frontier.

The two programs advance in parallel:
- **Kernel Program**: close K4 (six bridge operators) and K5 (four-way Mobius closure)
- **C2 Lineage Program**: materialize L1, execute L2, bind L3, emit L4

Map evaluation (M2) is postponed until both programs' necessary burdens are satisfied. Crown adjudication remains last.

## Next Lineage Seeds

```
LineageSeed: Materialize MAN.C2.HAWL.001.v1, execute GoldenReplayGateTest,
             bind D_proof, emit ReplayClosedTrace_v1
```

The next legal lineage extraction is not "closure theater" -- it is the four concrete artifacts L1 through L4.

## Proof Replay Anchors

- GoldenReplayGateTest
- TraceCert
- ProofIndexRootBind
- ReplayClosedTrace_v1
- WitnessPacket
- CertPacket
