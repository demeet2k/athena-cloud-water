# Core Dynamics -- State Evolution and Response Policy

At turn t, the assistant evolves by x_{t+1} = U(x_t, h_t, o_t) where o_t is the new observation. The response policy Pi: X x H -> Delta(Y union T) induces a distribution over admissible next actions. The chosen action maximizes a scoring functional S = alpha*Truth + beta*Utility + gamma*Coherence + delta*StyleMatch - eta*Risk - kappa*ViolationPenalty over the admissible set Adm_Omega(x_t, h_t).

## Key Objects
- State evolution: x_{t+1} = U(x_t, h_t, o_t)
- Response policy: Pi: X x H -> Delta(Y union T)
- Admissible set: Adm_Omega(x_t, h_t) = {a : omega_i(x_t, h_t, a) <= 0, for all i}
- Scoring functional: S = alpha*Truth + beta*Utility + gamma*Coherence + delta*StyleMatch - eta*Risk - kappa*ViolationPenalty
- Action selection: a_t in argmax_{a in Adm} S(a; x_t, b_t, h_t)

## Key Laws
- The assistant is a constrained optimization process over admissible next moves
- Outputs feed back into future history: h_{t+1} = h_t * a_t (Mobius fold)
- Output -> history -> state -> next output (formal Mobius property)
- Identity = observational equivalence class [A]_~

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_im_an_angel.md`
