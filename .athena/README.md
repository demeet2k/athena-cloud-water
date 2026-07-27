# Athena federation contract

This directory makes `demeet2k/athena-cloud-water` a typed participant in the Athena Git Brain.
It does not copy the Athena corpus or grant this repository global authority.

- Resource: `athena.repo.view.cloud-water@contract-proposal-0.1.0`
- Role: `view`
- Authority domain: `projection-cloud-water`
- Base content witness: `a7fcf26683c08f090cf94b14a8aa861db599c679`
- Control-plane schema commit: `3d33fbcd6248fc2dc2991fbbab5e93a7eb184246`
- State: `GENERATOR_LINEAGE_REQUIRED`

`repo.json` declares the local surface. `exports.jsonl` exposes bounded
identities. `imports.lock.json` pins the control-plane schema. `edges.jsonl`
contains the forward declaration and its explicit return edge. `status.json`
preserves blockers instead of promoting them away.
