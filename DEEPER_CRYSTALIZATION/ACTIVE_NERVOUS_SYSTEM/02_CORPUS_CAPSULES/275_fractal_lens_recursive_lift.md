# Fractal Lens -- Recursive Base-4 Lift Law

The Fractal lens is the exact recursive germ of the seed. For base-4 digit expansions r = (r_{m-1}...r_0)_4 and c = (c_{m-1}...c_0)_4, the lift law is: L_{4^m}(r,c) - 1 = sum_{t=0}^{m-1} 4^t * l_4(r_t, c_t). The digit in position t is exactly l_4(r_t, c_t). Fractal is not "self-similarity" as metaphor but exact recursive executability: address ladder, state word, generation law, and replay law.

## Key Objects
- L_{4^m}(r,c) - 1 = sum_{t=0}^{m-1} 4^t * l_4(r_t, c_t): base-4 lift law
- lambda(r,c) = ((r_{m-1},c_{m-1}), ..., (r_0,c_0)): address ladder
- kappa(r,c) = (l_4(r_{m-1},c_{m-1}), ..., l_4(r_0,c_0)): state word
- G: generation law; R: replay law
- Pi_Fr(r,c) = (lambda(r,c), kappa(r,c), G, R, omega^Fr_{r,c})

## Key Laws
- Theorem 2 (Fractal exactness): every value of L_{4^m} is the quaternary concatenation of seed interactions along the address ladder
- Axiom 4 (Fractal replay): every mature object must admit exact or typed replay from its recursive germ and witness shell
- Fractal = exact recursive executability, not metaphor
- Expand o Collapse ~ id (replay closure for lawful states)

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_mobius_lenses.md`
