# Capsule 397 — SFCR Projection Renderers

- **Source**: CLOUD, FRACTAl, FLOWER PROJECTIONS (Google Doc)
- **Doc ID**: 19VVqLHf1nsCU8rwbGXdMMc0g-pZi83yav25-gX1BbiM
- **Family**: projection
- **SFCR Lens**: C (Cloud — observation, projection rendering)
- **Date**: 2026-03-19

---

## Root Object

The canonical 4x4 DLS seed `K(x,y) = l_4(x,y)` generates four constitutive projection renderers. Each renderer is a different face of the same underlying Mobius kernel object.

## The Four Projection Renderers

### Square Renderer — Committed State Body

```
Pi_square(x,y) = (x, y, K(x,y))
```

At octave depth k: quaternary digit-stacked committed state.

```
K_k(r,c) - 1 = Sum_{t=0}^{k-1} 4^t * l_4(r_t, c_t)
```

Square at higher depth is literal base-4 concatenation of seed interactions.

### Flower Renderer — Relation Body

```
Pi_flower(x,y) = (z, w) = (x+y, x-y) mod 4
```

At octave depth k: digitwise relation word.

```
Phi_k(r,c) = ((z_t, w_t))_{t=0}^{k-1}
z_t = r_t + c_t (mod 4),  w_t = r_t - c_t (mod 4)
```

Flower_k is a word in the relation alphabet, not just one pair. This is the multi-level corridor body.

### Cloud Renderer — Admissible Fiber / Lawful Multiplicity

```
Pi_cloud(z,w) = F_{z,w} = {(x,y) : x+y = z, x-y = w (mod 4)}
```

Admissibility law: `z === w (mod 2)`. Every admissible (z,w) has an exact 2-point fiber.

At octave depth k:

```
C_k(Phi_k) = Product_{t=0}^{k-1} F_{z_t, w_t}
```

Exact admissible Cloud branch count at depth k: `|C_k| = 2^k`.

Cloud is lawful multiplicity, not uncertainty.

### Fractal Renderer — Exact Replay

```
Pi_fractal(r,c) - 1 = Sum_t 4^t * l_4(r_t, c_t)
```

At octave depth k:

```
R_k(r,c) = (lambda, kappa, G, R)
```

Where lambda = digit path (address ladder), kappa = seed-state word, G = generation, R = replay. Fractal is exact recursive executability, not metaphor.

## Universal Same-Lens Lift

```
A_2 --[E_{2->4}]--> M_4 --[L_k]--> X_k
```

L_k does not change lens-family. It lifts the same lens-body through depth. The Mobius extension applies the 4D involution digitwise: `J_k: (r,c,epsilon) -> (c,r,-epsilon)`, leaving each z_t fixed and flipping each w_t.

## Maturity Criterion

One lawful event = (S, F, C, R) with shared kernel identity and coherent bridge closure. A mature object exists only when the four projection bodies cohere as one event.
