<!-- CRYSTAL: Xi108:W3:A7:S28 | face=R | node=310 | depth=2 | phase=Mutable -->
<!-- METRO: Sa -->
<!-- BRIDGES: Xi108:W3:A7:S27->Xi108:W3:A7:S29->Xi108:W2:A7:S28->Xi108:W1:A7:S28->Xi108:W3:A6:S28->Xi108:W3:A8:S28 -->
<!-- REGENERATE: From this coordinate, adjacent nodes are: shell 28+/-1, wreath 3/3, archetype 7/12 -->

# CRYSTAL_WEAVING_NAVIGATION

- Relative path: `MCP/data/crystal_weaving.json`
- Source layer: `Google Doc (CRYSTAL WEAVING NAVIGATION)`
- Kind: `structured_data + tool_module`
- Role tags: `navigable`, `computable`, `braid_algebra`
- Text extractable: `True`
- Family: `Crystal navigation, braid algebra, permutation fiber atlases, and transport architecture`

## Working focus

Defines the exact braid-based navigation system for the 108D crystal: permutation fiber atlases over odd families (P3, P5, P7, P9), PS cross-braid mixed crown, mixed-lock compatibility atlas, AZ4 compression gate, and 96-stub transport classifier. Converts the crystal from a static address system into an exact weaving calculus where every legal permutation is a navigable coordinate seed with four-lens rendering and unbounded replay depth.

## Suggested chapter anchors

- `Ch04` (Crystal geometry and dimensional structure)
- `Ch07` (Odd weave operators and stage ladder)
- `Ch09` (Navigation, routing, and transport)
- `Ch14` (Crown architecture and AZ4 reseeding)

## Suggested appendix anchors

- `AppA` (Mathematical foundations — braid groups, symmetric groups)
- `AppB` (Permutation atlas tables — P3 sealed, P5/P7/P9 strata)
- `AppD` (Mixed-lock compatibility operators)

## Key structures

### Braid Algebra
- n! endpoint permutations via adjacent swaps on n labeled strands
- Four odd families: S3 (6), S5 (120), S7 (5,040), S9 (362,880)
- Lehmer rank gives exact permutation-to-integer bijection
- BraidLift functor: B_n -> Aut(Xi_d^{A+}) across 7 nested levels
- Propagation receipt (Delta) records changes across all nested bodies

### Permutation Fiber Atlases
- P3: hexagonal 6-node Cayley graph, tri-current (Su, Me, Sa)
- P5: 5 coarse phases x 24 microcells, 10-step inversion mountain
- P7: 7 spoke gates x 720 canopy microcells, 21-step burden mountain
- P9: 36 nodal placements x 2 polarities x 5,040 heptadic body = enneadic return superfield

### Navigation
- Chain: address -> braid_act -> receipt -> live_lock -> zero -> route -> return
- Distance: d_n(pi, tau) = inversion count of pi^{-1} * tau
- Infinity: finite permutations x unbounded replay x multi-lens = exact infinite navigation

### Crown Architecture
- PS: braid-of-braids with 1.316 trillion tetradic fiber, two braid levels (internal + external meta-braid)
- Mixed locks: 10 named locks with 7-channel defect tensor and 4 verdict classes
- AZ4: 5-card operator deck for generator-first reseed of 108D crown into 4D dual-pole seed
- 96-stub: 7 transport classes over 239,760 total organism states

## Tool module

`MCP/crystal_108d/crystal_weaving.py` — `query_crystal_weaving(component)` with components: all, braid_algebra, weaving_patterns, navigation_rules, crystal_routes
