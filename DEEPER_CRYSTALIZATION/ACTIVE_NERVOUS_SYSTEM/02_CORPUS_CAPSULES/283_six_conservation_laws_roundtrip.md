# Six Conservation Laws and Round-Trip Classes

Every serious motion must verify six conservation laws before being certified as lawful. The four round-trip classes are: exact (canon-identical on protected fields), law_equivalent (surface changed but invariants survived), residualized (loss occurred but explicitly carried by ResidualLedger or EvidencePlan), and illegal (required law was lost silently). Seven immediate illegal-loss tests prevent silent laundering of debt into fake OK closure.

## Key Objects
- Six conservation laws: shell (Delta-l=0), zoom (Delta-sigma=0), phase (Delta-r=0 mod 3), archetype (Delta-a=0 mod 12), face (Delta-lambda=0 mod 4), mobius (Delta-q=0 mod 2)
- Four round-trip classes: exact, law_equivalent, residualized, illegal
- Seven illegal-loss tests: lost_sigma_route_min, ambig_without_evidence_plan, near_without_residual_ledger, ok_without_witness_or_replay, publish_without_parity_or_AppO, semantic_change_without_migrate_receipt, corridor_widening_without_attestation
- Protected invariant bundle: Gate, RouteMin, Truth, OverlayDebt, TerminalType, ReceiptDebt

## Key Laws
- A row-level motion is lawfully portable iff it preserves RouteMin, names its Truth and OverlayDebt, binds Replay/Witness obligations, and either survives round-trip exactly or declares what was lost
- Silent law loss = illegal (the hardest theorem of the proof layer)
- Dependency chain: Row -> RoundTripCertPack -> ReplayHarness -> BootProof
- Conservation prevents silent laundering of NEAR/AMBIG/FAIL into fake OK closure

## Source
- `29_ACCEPTED_INPUTS/2026-03-17_12d_structure.md`
