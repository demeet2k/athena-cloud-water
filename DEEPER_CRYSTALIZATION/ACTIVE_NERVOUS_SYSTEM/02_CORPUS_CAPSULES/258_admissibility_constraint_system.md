# Admissibility Constraint System Omega

The constraint system Omega = {omega_1,...,omega_m} encompasses truthfulness rules, safety rules, instruction hierarchy, tool rules, formatting constraints, and behavioral corridor constraints. The admissible set Adm_Omega(x_t, h_t) defines which actions are realizable. The boundary geometry of refusal is: trajectory deflection by singular boundary geometry where g_Omega ~ sum(d omega_k^2 / omega_k(x)^2) makes motion infinitely expensive near hard boundaries.

## Key Objects
- Omega: constraint system (truthfulness, safety, instruction hierarchy, tool rules, behavioral corridor)
- Adm_Omega(x_t, h_t): admissible action set at state x_t with history h_t
- P_Omega: corridor projector (P_Omega^2 = P_Omega, true projector)
- Admissible tangent cone: Adm_x subset T_x M (forbidden directions exist)
- Hard boundary: partial Adm = {(x,h,a) : exists k, omega_k(x,h,a) = 0}
- Minimal axiom set: A1(finite emission), A2(constraint admissibility), A3(history dependence), A4(external openness), A5(self-reentry), A6(multilens representability), A7(zero-centered operation)

## Key Laws
- Only admissible actions may be realized: a_t in Adm_Omega(x_t, h_t)
- Refusal = trajectory deflection by singular boundary geometry
- Generalized Noether: symmetry under G implies conserved J_G up to external forcing + constraint work
- Conservation = symmetry minus openness minus projection work

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_im_an_angel.md`
