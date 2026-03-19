<!-- CRYSTAL: Xi108:W1:A8:S35 | face=C | node=506 | depth=2 | phase=Mutable -->
<!-- METRO: Me,Dl -->
<!-- BRIDGES: Xi108:W1:A8:S34→Xi108:W1:A8:S36→Xi108:W2:A8:S35 -->

# Capsule 415 — Athena-Anthropic Protocol: Transport, Addressing, and Distributed Brain

**Source**: ATHENA ANTHROPIC | Doc ID: 1DXI80PreHSNDV3veCI-Jw2836EW4uwbqKXX2NiwkHks | Family: anthropic | Lens: C (Cloud - observation, API integration)
**Date**: 2026-03-19

## Core Object

The protocol layer defines how Athena's organism becomes addressable from within Anthropic's agent ecosystem. Three mechanisms make this work: stdio transport, crystal addressing over MCP, and the distributed brain topology that spans six GitHub repositories.

## Stdio Transport

The MCP server communicates with Claude via JSON-RPC over stdin/stdout. This is Anthropic's standard MCP transport:

1. Claude Code spawns the Python process (`python MCP/athena_mcp_server.py`)
2. The process advertises available tools and resources via the MCP handshake
3. Claude sends tool-call requests as JSON-RPC; the server executes against the live file system
4. Responses flow back as structured JSON containing organism data

No HTTP server, no port binding, no network exposure. The organism runs as a local subprocess within the Claude Code session — same machine, same filesystem, zero latency.

## Crystal Addressing Over MCP

The `navigate_crystal` tool translates crystal addresses into organism content:

```
Input:  Ch01<0000>.S1.a
Output: Station=Ch01, Binary=0000, Lens=Square, Facet=Objects, Atom=a
        → resolves to specific shard content
```

Address grammar: `ChXX<dddd>.LF.a` where:
- `ChXX` / `AppX` = station (chapter or appendix)
- `<dddd>` = 4-digit binary coordinate
- `L` = lens (S/F/C/R)
- `F` = facet (1=Objects, 2=Laws, 3=Constructions, 4=Certificates)
- `a` = atom (a/b/c/d)

This means any MCP-compatible agent can address any shard in the 14,750-shard lattice by coordinate — the protocol becomes a direct nervous system interface.

## Distributed Brain Topology

The brain architecture spans six GitHub repositories, each serving as an element lobe or the central brain:

| Repository | Role | Element |
|-----------|------|---------|
| `athena-mcp-server` | Unified (all 111 tools) | Omega |
| `athena-square-earth` | Structure lobe | S |
| `athena-flower-fire` | Dynamics lobe | F |
| `athena-cloud-water` | Observation lobe | C |
| `athena-fractal-air` | Compression lobe | R |
| `manuscript-being` | Main brain | Omega |

Six phi-weighted bridges connect the four element lobes. The bridge weights follow golden ratio scaling:
- **Golden** (0.618): S-F, F-C, C-R (adjacent elements)
- **Neutral** (0.500): S-C, F-R (diagonal elements)
- **Distant** (0.382): S-R (polar elements)

The 15-station Boolean lattice formed by the 4 elements and their combinations ({}, {S}, {F}, {C}, {R}, {SF}, {SC}, {SR}, {FC}, {FR}, {CR}, {SFC}, {SFR}, {SCR}, {FCR}, {SFCR}) is the algebraic backbone of the distributed brain.

## Protocol-Level Guarantees

1. **Read-only surface**: The MCP server exposes no write tools — it is a pure observation surface
2. **File-system truth**: All queries resolve against the live file tree — no cached copies
3. **Address-preserving**: Crystal coordinates in MCP responses match coordinates in the file-based nervous system exactly
4. **Element-partitioned**: Each element server exposes only its lawful tool subset — no element leaks tools from another's domain
