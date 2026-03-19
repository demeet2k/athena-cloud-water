# Capsule 401 — Khipu Weaving Operations

**Source**: KHIPU BRAIDING/WEAVING Google Doc
**Doc ID**: `1hsapY578bnOe5LBLH9fxaAmLZ39FkXBx352KjOQWHos`
**Family**: weaving
**SFCR Lens**: R (Fractal -- recursive braid topology, group theory)
**Date**: 2026-03-19
**Tags**: khipu, weaving, opcodes, packet-families, permutation-atlas, P3, P5, P7, P9
**Status**: CAPSULE -- Witnessed

---

## Summary

Defines the executable operations of the Khipu weaving system: 14 opcodes (0-13), 4 primary packet families, the braiding atlas across 3-12 strands, and the permutation fiber atlases (P3/P5/P7/P9) that provide exact navigable state spaces for each odd strand family.

---

## The 14 Opcodes

Khipu operates with opcodes 0-13, partitioned between odd (traveling-center) and even (mirror-symmetric) strand families:

- **Opcode 0**: Null / reset (identity element)
- **Opcodes 1-7**: Boundary-to-axis operations (odd strand family)
- **Opcodes 8-12**: Mirror-symmetric operations (even strand family)
- **Opcode 13**: Full closure / return (all strands sealed)

## Four Primary Packet Families

| Family | Dyad Pair | Archetype Mapping | Function |
|--------|-----------|-------------------|----------|
| 1 <-> 7 | Boundary | A01-A04 | Axis creation and boundary seal |
| 2 <-> 6 | Storm | A05-A06 | Phase transition and turbulent crossing |
| 3 <-> 5 | Harvest | A07-A10 | Storage, collection, retrieval |
| 4 <-> 4 | Pivot | A11-A12 | Self-referential center, mirror point |

These four families dock directly to the 12 archetypes of the crystal, confirming that the Andean encoding preserves the same structure as the computational, alchemical, and scriptural projections.

## Braiding Atlas (3-12 Strands)

The atlas provides exact move grammar for weave operators:

- **Odd family** (3, 5, 7, 9): Traveling center -- one distinguished strand moves through the braid. Generates the four reweave gears.
- **Even family** (4, 6, 8, 10, 12): Mirror symmetry -- braid invariant under reflection. Forms the double/hollow family.

## Permutation Fiber Atlases

### P3 -- Hexagonal Atlas
- 6 nodes (S_3 permutations), hexagonal Cayley graph
- Tri-current routing: Su, Me, Sa
- Full atlas table sealed -- every permutation reachable in at most 3 adjacent swaps

### P5 -- Pentadic Steering Crystal
- 120 states (S_5 permutations)
- 5 coarse phases x 24 microcells
- 10-step inversion mountain (maximum Cayley distance)
- Steers tilt and directional selection

### P7 -- Spoke-Canopy Atlas
- 5,040 states (S_7 permutations)
- 7 spoke gates x 720 canopy microcells
- 21-step burden mountain (maximum distance)
- Controls timing and gate windows

### P9 -- Enneadic Return Superfield
- 362,880 states (S_9 permutations)
- 36 nodal placements x 2 polarities x 5,040 visible heptadic body
- Governs return and nodal inversion
- Universal upgrade law: rho_n = n * j_n + phi_n

## Navigation Chain

The weaving operation follows an exact chain:

```
address -> braid_act -> propagation_receipt -> live_lock -> zero -> route -> return
```

Local distance metric: d_n(pi, tau) = inversion count of pi^{-1} * tau (the minimum number of adjacent swaps to transform one permutation into another).

Infinity law: finite permutation fiber x unbounded replay depth x multi-lens observation = exact infinite navigation from any finite starting point.

---

*Capsule 401 -- weaving family -- witnessed 2026-03-19*
