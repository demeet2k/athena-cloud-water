# Flower Lens -- Orbit/Tunnel Generators and Invariant Sheets

The Flower lens converts the kernel into flow. The Flower chart map is Phi(x,y) = (z,w) = (x+y, x-y) mod 4. Two primitive flow generators exist: orbit generator O(x,y) = (x+1, y-1) mod 4 and tunnel generator T(x,y) = (x+1, y+1) mod 4. These produce two exact invariant sheet families: O_z = {(x,y) : x+y = z mod 4} and T_w = {(x,y) : x-y = w mod 4}. Flower is the object's corridor/orbit/dynamic continuity structure.

## Key Objects
- Phi(x,y) = (z,w) = (x+y, x-y) mod 4: Flower chart map
- O(x,y) = (x+1, y-1) mod 4: orbit generator (preserves z)
- T(x,y) = (x+1, y+1) mod 4: tunnel generator (preserves w)
- O_z: orbit invariant sheets (constant z = x+y)
- T_w: tunnel invariant sheets (constant w = x-y)
- Pi_Fl(x,y) = ((x,y), z, w, O_z, T_w, omega^Fl_{x,y})

## Key Laws
- Flower = orbital law of the same geometry (how the board is traversed)
- Square = committed board geometry; Flower = orbital law of that geometry
- At 6x6: triadic Mobius crossing m_3(i,b,o) = (i+1 mod 3, b+2 mod 4, -o)
- Flower equivariance: Phi(y,x) = (z, -w) under Mobius involution

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_mobius_lenses.md`
