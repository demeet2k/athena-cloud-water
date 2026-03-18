# Square Lens -- Contract / Address / Admissibility

The Square lens is the formal contract face of the kernel object. The Square projection is Pi_Sq(x,y) = (x, y, K(x,y)). More fully, S(x,y) = ((x,y), K(x,y), Sigma_{x,y}, omega^Sq_{x,y}) where Sigma_{x,y} is the local contract and omega^Sq is the square witness. Square is the discrete admissibility ledger: it fixes WHERE the object is, WHAT state it carries, and WHAT exact law generated it. Square is the cockpit of commitment.

## Key Objects
- Pi_Sq(x,y) = (x, y, K(x,y)): square projection
- S(x,y): full square object with contract and witness
- Sigma_{x,y}: local contract
- omega^Sq_{x,y}: square witness
- At 6x6: explicit committed board with exact row/column permutations, diagonal closure, pairing skeleton, coherent sector stamp

## Key Laws
- Square = committed board geometry (the cockpit of commitment)
- Square is not merely "the visible grid" but the fully committed discrete board
- Exact admissible pairing skeleton required
- Square equivariance under Mobius: Pi_Sq(J(x,y,epsilon)) relates to Pi_Sq(y,x,-epsilon)

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_mobius_lenses.md`
