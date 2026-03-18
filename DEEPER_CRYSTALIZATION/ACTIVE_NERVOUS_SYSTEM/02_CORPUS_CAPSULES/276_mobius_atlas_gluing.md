# Mobius Atlas Gluing -- Involution sigma(x,y) = (y,x) and Quotient

The Mobius character is modeled as nontrivial orientation-reversing chart gluing, not poetic looping. Two chart copies U+ = X x Y x {+} and U- = X x Y x {-} are glued by involution J(x,y,+) = (sigma(x,y), -) where sigma(x,y) = (y,x). The Mobius carrier is the quotient M_4 = (U+ union U-) / ~ with (x,y,+) ~ (y,x,-). This exchanges visible axes and reverses orientation cleanly.

## Key Objects
- sigma(x,y) = (y,x): canonical involution
- J(x,y,epsilon) = (y,x,-epsilon): atlas gluing map
- M_4 = (Z_4^2 x {+,-}) / ~: Mobius carrier quotient
- sigma^2 = id: involutive property
- Under gluing: Square swaps axes, Flower preserves z and flips sign of w, Cloud maps F_{z,w} to F_{z,-w}

## Key Laws
- Theorem 3 (Mobius-Flower compatibility): under sigma(x,y)=(y,x), Flower coordinates transform by (z,w) -> (z,-w)
- Mobius involution is involutive, explicit, and interacts cleanly with Flower relation structure
- sigma^2 = id required; all lens maps must be compatible with J
- Non-orientability encodes: inside/outside distinction is local, not global

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_mobius_lenses.md`
