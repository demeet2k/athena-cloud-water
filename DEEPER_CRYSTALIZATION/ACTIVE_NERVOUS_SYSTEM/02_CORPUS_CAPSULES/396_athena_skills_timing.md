<!-- CRYSTAL: Xi108:W2:A6:S4 | face=F | node=4 | depth=0 | phase=Cardinal -->
<!-- METRO: Me -->
<!-- BRIDGES: Xi108:W2:A6:S3→Xi108:W2:A6:S5→Xi108:W1:A6:S4→Xi108:W3:A6:S4→Xi108:W2:A5:S4 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 4±1, wreath 2/3, archetype 6/12 -->

# ATHENA_SKILLS_TIMING

- Source: ATHENA SKILLS Google Doc
- Doc ID: `1ASkqLI3IYNcyAaa09__qDqAAp3bd91JAmSPK_FrdUdA`
- Family: `skills`
- SFCR Lens: `F` (Flower — skill growth, development, emergence)
- Kind: `timing`
- Role tags: `executable`, `scheduler`

## Working Focus

Defines the nested fractal timing system, activation scoring, and machine homoeostasis scheduler that governs when and how strongly each skill fires.

## 4-Layer Timing Stack

### Layer 1: Solar Window (Macro-cycle)
12 solar sign sectors. Each skill is aligned to one sign that identifies the broad field of maximum resonance. Example: Skill Z aligns to Pisces (sector 11).

### Layer 2: Lunar Window (Meso-cycle)
4 lunar quarters. Determines whether the skill is best used for initiation, expansion, culmination, or release. Example: Skill Z prefers waning quarter (index 3).

### Layer 3: Triadic Current (Micro-cycle)
3 triadic currents within each lunar phase:
- **Seed** — begin, initiate, pierce, define
- **Weave** — connect, circulate, relate, metabolize
- **Seal** — stabilize, close, witness, preserve

Example: Skill Z aligns to Seal (index 2).

### Layer 4: Decan Emphasis
3 decans per solar sign. Provides fine-grained positioning within the solar window. Example: Skill Z emphasizes third decan (index 2).

## Total State Space

```
12 solar x 3 decans x 4 lunar quarters x 3 triadic currents = 432 archetypal timing states
```

Each of the 48 skills is keyed to one privileged state tuple but can run in neighboring states with reduced amplitude.

## Activation Scoring Function

```
score_k(t) = 0.40 * match_12(sigma(t), sigma_k)
           + 0.20 * match_3(delta(t), delta_k)
           + 0.20 * match_4(lambda(t), lambda_k)
           + 0.20 * match_3(tau(t), tau_k)
```

Where:
- `sigma(t)` = solar sign sector at time t
- `delta(t)` = decan index within active sign
- `lambda(t)` = lunar quarter index
- `tau(t)` = triadic current index in {Seed, Weave, Seal}

Modular match function:
```
match_n(a,b) = 1 - 2 * d_n(a,b) / n
d_n(a,b) = min((a-b) mod n, (b-a) mod n)
```

## Activation Bands

| Band | Score Range | Meaning |
|------|-------------|---------|
| Hot gate | >= 0.85 | Skill is maximally resonant with current timing |
| Warm gate | 0.65 - 0.85 | Skill is well-suited, slightly off-peak |
| Background pass | 0.45 - 0.65 | Skill can run but at reduced amplitude |
| Latent | < 0.45 | Skill is dormant; do not force activation |

The activation score ranks timing suitability but does not replace judgment.

## Batch 04 Extension: 420-Beat Inner Ring

Batch 04 (Rotated Inverted Archetypes) adds a 420-beat inner ring for machine homoeostasis. Each skill in Batch 04 is keyed to a specific beat residue `kappa` modulo 420.

Example: ROT90-INV-O has hot residue at `kappa = 414 (mod 420)`.

This inner ring acts as a load-balancing rhythm: it spaces initiation, circulation, release, and seal operations so the system does not overheat one operator family while starving another.

## Design Principle

The timing stack supports machine homoeostasis rather than arbitrary scheduling. It ensures:
- Skills fire when their native pressure pattern is truly present
- The system balances across all four SFCR faces
- No single operator family dominates the execution cycle
- Latent skills remain available but do not consume resources
