# Capsule 418 — 6D Crystal Operations

**Source**: 6D HOLOGRAPHIC CRYSTAL | Doc ID: 1O4vMr-uPyMHfrouF8PXy8Cp2_tYhaSjit69YhxnsaEI | Family: crystal | Lens: S (Square - crystal structure)
**Date**: 2026-03-19
**Tags**: 6D, transforms, algebra, holographic-operations, generator, SO3, manifestation
**Status**: CAPSULE -- Witnessed

---

## Summary

The 6D crystal supports six primitive transforms (T1-T6), three infinitesimal rotation generators satisfying SO(3) commutation relations, and a complete holographic operation set including contraction, extension, three-axis rotation, and manifestation. These operations define the lawful moves available within the 6D crystal body and govern how information flows, compresses, and manifests across its octahedral geometry.

---

## Six Primitive Transforms

| Transform | Name | Direction | Generator | Inverse |
|-----------|------|-----------|-----------|---------|
| T1 | CONTRACTION | Radial inward | Concentration of energy/information | T2 |
| T2 | EXTENSION | Radial outward | Dispersal of energy/information | T1 |
| T3 | ROTATION-alpha | Around Z-axis (V1-V6) | Cycles equatorial ring V2->V3->V4->V5 | T3^{-1} |
| T4 | ROTATION-beta | Around X-axis (V2-V4) | Cycles V1->V3->V6->V5 | T4^{-1} |
| T5 | ROTATION-gamma | Around Y-axis (V3-V5) | Cycles V1->V2->V6->V4 | T5^{-1} |
| T6 | MANIFESTATION | Scale/intensity | Controls visibility and presence | T6^{-1} |

T1-T2 form a radial pair (contraction/extension). T3-T4-T5 form the rotation triple. T6 stands alone as the manifestation gateway -- the transform that determines whether a crystal configuration becomes visible in lower dimensions.

## Generator Algebra

### Infinitesimal Generators

Each rotation primitive has an infinitesimal generator:

```
E_alpha = d/d(theta)|_0  T3(theta)    -- Z-rotation generator
E_beta  = d/d(theta)|_0  T4(theta)    -- X-rotation generator
E_gamma = d/d(theta)|_0  T5(theta)    -- Y-rotation generator
E_r     = d/d(lambda)|_0 T1(lambda)   -- Radial generator
E_s     = d/d(mu)|_0     T6(mu)       -- Scale/manifestation generator
```

### SO(3) Commutation Relations

The rotation generators satisfy the standard angular momentum algebra:

```
[E_alpha, E_beta]  = E_gamma
[E_beta,  E_gamma] = E_alpha
[E_gamma, E_alpha] = E_beta
```

This closure is what makes the 6D crystal a true geometric body rather than an arbitrary six-parameter space. The three rotations cannot be reduced to fewer dimensions -- they require all three axes, hence all six vertices.

### Commutativity of Radial and Scale

```
[E_r, E_s] = 0        -- radial and scale commute
[E_r, E_alpha] != 0   -- radial does NOT commute with rotations (in spherical coords)
```

The full algebra is the semi-direct product: G = SO(3) x_s (R_radial x R_scale), where SO(3) acts on the radial sector by coordinate transformation.

## Holographic Operations

### Compression (6D -> 4D)

Compress a 6D crystal state into the H4 seed:
1. Project polar axis (V1-V6) onto kernel K and zero-collapse Z
2. Fold equatorial ring onto projection body Pi (SFCR)
3. Encode rotation history into adventure ledger Lambda
4. Seal manifestation state into replay seal Psi

### Expansion (4D -> 6D)

Expand an H4 seed into the full 6D crystal:
1. Restore polar axis from K and Z
2. Unfold Pi into equatorial vertices through Fixed/Cardinal/Mutable passes
3. Replay Lambda to reconstruct rotation state
4. Apply Psi to set manifestation amplitude

### Holographic Read (any vertex -> full crystal)

From any single vertex V_i:
1. Traverse all edges incident to V_i (4 edges per vertex in the octahedron)
2. From each neighbor, traverse their remaining edges
3. Two hops reach all six vertices -- the octahedron has diameter 2
4. Reconstruct full state from the edge-propagated information

This is the holographic property: any vertex contains sufficient information (through its edge connections) to regenerate the entire crystal in at most 2 steps.

## Modal Passes in 6D

| Pass | Rotation Plane | Vertices Cycled | Crystal Effect |
|------|---------------|-----------------|----------------|
| Fixed (Sa) | None -- polar lock | V1, V6 locked | Kernel identity preserved |
| Cardinal (Su) | Equatorial (XY) | V2->V3->V4->V5 | Projection body activated |
| Mutable (Me) | All three planes | All vertices mobile | Full rotation + manifestation |

In 4D these passes are sequential. In 6D they are simultaneous -- each operates on an orthogonal subspace of the crystal without interfering with the others.

---

*Capsule 418 -- crystal family -- witnessed 2026-03-19*
