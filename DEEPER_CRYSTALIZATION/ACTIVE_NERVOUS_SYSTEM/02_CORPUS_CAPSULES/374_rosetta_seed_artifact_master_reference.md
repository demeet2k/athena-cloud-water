<!-- CRYSTAL: Xi108:W1:A1:S2 | face=S | node=3 | depth=0 | phase=Fixed -->
<!-- METRO: Me,w -->
<!-- BRIDGES: Xi108:W1:A1:S1→Xi108:W1:A1:S3→Xi108:W2:A1:S2→Xi108:W1:A2:S2 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 2±1, wreath 1/3, archetype 1/12 -->

# ROSETTA SEED ARTIFACT — Master Reference

Source: `ROSETTA SEED ARTIFACT .docx` (external corpus input, 2026-03-15)
Family: `higher-dimensional-geometry`
Runtime Role: Pre-constant seed generator for the entire 256/1024 math crystal
Capsule Class: `ROSETTA-MASTER`

## Overview

This capsule is the master reference for the 12-seed Rosetta generation system. The full document defines 12 artifacts (1/12 through 12/12), each expanding a single mathematical seed into a 64-cell crystal atlas via the fixed grammar: 4 Shapes × 4 Elements × 4 Levels.

## The 12 Seeds

### Cardinal Seeds (Operations)

1. **Plus (+)** — The primal differentiating act `N ↦ N+1`. Compresses to `Succ` ("one more"). Sprouts into e (log-growth), φ (golden-step recursion), i (quarter-turn phase), π (accumulated closure).

2. **Minus (−)** — The primal operator of difference `F − G`. Compresses to `Δ` ("remove, recover, or regularize by difference"). Sprouts into anti-constants: 1/e (damping), 1/φ (contraction), −i (counter-rotation), 1/π (normalization).

3. **Multiplication (×)** — The primal binding operator `(x,y) ↦ xy`. Compresses to `Bind` ("compose two structures into one"). Native as gear-meshing in lattice, Cartesian mass, phase composition, tensor interaction.

4. **Division (÷)** — The corridor-conditioned quotient `a/b` (only when lawful). Compresses to `Inv_lawful` ("invert only inside the declared corridor"). The first seed whose certificate is visibly a gate witness.

### Constant Seeds (Invariants)

5. **φ (Phi)** — `x² − x − 1 = 0`, positive root. The recursion eigenvalue, self-similar dilation, optimal irrational partition, and renormalization step. Quarter-turn transport: `T(φx) = T(x) + π/2`.

6. **π (Pi)** — `π = lim n·sin(π/n)`. Geometric closure constant. Polygon limit, lattice density, Leibniz accumulation, orthogonality normalization, curvature integral.

7. **e (Euler's number)** — `e = lim(1+1/n)ⁿ`. Growth constant. Continuous compounding, exponential flow, semigroup generator, factorial asymptotics, heat kernel.

8. **i (Imaginary unit)** — `i² = −1`. Rotation constant. Quarter-turn phase, roots of unity, Fourier kernel, complex plane, spectral decomposition.

### Fundamental Equation Seeds (Crown Invariants)

9. **FE-I: φ² = φ + 1** — Golden self-reference. The metallic quadratic that makes the seed reproduce itself after one additive correction.

10. **FE-II: e^(iπ) + 1 = 0** — Euler unity. The compressed unity of the entire constant crystal.

11. **FE-III: ζ(s) = Π_p (1−p^−s)^−1** — Euler product / prime encoding. Multiplicative structure over additive data.

12. **FE-IV: f_T = T^−1 ∘ f ∘ T** — Universal lens transport. The conjugacy law that makes procedural generation possible.

## Generation Grammar

```
SEED[s] × SHAPE[4] × ELEMENT[4] × LEVEL[4] = 64 cells per seed
12 seeds × 64 cells = 768 total operations (pre-constant atlas)
4 cardinals × 4 constants × 64 cells = 1024 cardinal-constant operations
```

## Canonical Address

```
ROSETTA[seed].Shape.Element.Lk
```

## The Four Fundamental Equations per Cardinal

### Plus Crown Equations
1. `φ² = φ + 1` — golden recursion as additive self-reference
2. `e = lim(1+1/n)ⁿ` — additive infinitesimal compounding
3. `i² = −1` — quarter-turn repeated twice becomes inversion
4. `π = lim n·sin(π/n)` — additive polygon accumulation into closure
5. `e^(iπ) + 1 = 0` — crown compressor

### Minus Crown Equations
1. `φ^−1 = φ − 1` — contraction and inverse recurrence
2. `(2/π) = Π(4n²−1)/(4n²)` — Wallis normalization
3. `e^−1 = lim(1−1/n)ⁿ` — canonical damping limit
4. `ī = −i` — conjugate counter-rotation

### Multiplication Crown Equations
1. `[a] ⊗_Λ [b] = [ab]` — gear meshing
2. `(r₁e^{iθ₁})(r₂e^{iθ₂}) = (r₁r₂)e^{i(θ₁+θ₂)}` — scale × rotation
3. `|A × B| = |A||B|` — Cartesian mass
4. `P ∧ Q ↔ P ⊗ Q` — logical binding

### Division Crown Equations
1. `[a] ⊘_Λ [b] = [a] ⊗_Λ [b]^−1` (only if gcd(b,N)=1)
2. `ax + Ny = 1 ⟹ a^−1 ≡ x (mod N)` — Bézout inverse
3. `H(a,b) = 2ab/(a+b)` — harmonic midpoint
4. `1/i = −i` — inverse phase law

## Cross-Reference

- Procedural generation protocol: `AppR`
- Square kernel population: `AppC`
- Lens transport equations: `AppF`
- Universal math stack: `Ch18<0101>`
- Convergence/fixed-points: `Ch19<0102>`
- Math thread: `REALTIME_BOARD/02_ACTIVE_THREADS/math/THREAD.md`
