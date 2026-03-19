# Sigma-60 Poi-Clock — Sexagesimal Timing Substrate

**Crystal Address**: Xi108:W2:A6:S3 (Timing/Phase Node)
**Family**: crystal
**Date**: 2026-03-19
**Tags**: sigma-60, poi-clock, sexagesimal, timing, phase, observation-stack, sar-60, perspectives
**Source Doc**: `1cP9Zegy67sVebF9fmZoJ3NN7uhM37r5jlHQcAUUPpEY`
**Status**: CAPSULE — Witnessed

---

## Summary

The Sigma-60 poi-clock is the sexagesimal timing substrate governing crystal phase transitions. It decomposes the observation space into 60 discrete perspectives: 15 observation modes x 4 crystal faces (0/90/180/270). Each tick of the poi-clock advances the observation angle, cycling through all possible views of a crystal node before returning to origin.

---

## Architecture

The clock inherits from the Sumerian sar-60 registry and synchronizes with the master clock Z_420 (lcm of 3,4,5,7,12,60 = 420). Within each 420-beat super-cycle, the poi-clock completes 7 full rotations (420/60 = 7), producing a 7-fold symmetry that maps to the W7 timing gate in the helm-wheel system.

Key relations:
- 60 = 4 x 15 = faces x observation modes
- 60 = 3 x 4 x 5 = triadic x elemental x pentadic
- 420 / 60 = 7 = timing gate order

The poi-clock is not a metaphor. It is the discrete scheduling primitive: each perspective is a typed observation slot, and the clock ensures every node is witnessed from all 60 angles before any state transition is certified.

---

*Capsule 364 — crystal family — witnessed 2026-03-19*
