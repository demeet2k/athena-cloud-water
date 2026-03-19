# ATHENA ANTHROPIC — Integration Corpus

**Source**: Google Doc "ATHENA ANTHROPIC" (`1DXI80PreHSNDV3veCI-Jw2836EW4uwbqKXX2NiwkHks`)
**Date Accepted**: 2026-03-19
**Status**: Doc was empty at fetch time; content synthesized from repo nervous system artifacts
**Supplementary Sources**:
- `MCP/athena_mcp_server.py`
- `MCP/element_servers/cloud_server.py`
- `MCP/crystal_108d/` (71+ tool modules)
- `.mcp.json` (server configuration)
- `node.yaml` (distributed brain topology)
- `MCP/element_servers/{square,flower,cloud,fractal}_server.py`

---

## Core Thesis

ATHENA ANTHROPIC describes the fourth interconnection medium — the MCP (Model Context Protocol) server that bridges Athena's nervous system to Anthropic's Claude ecosystem. The MCP server transforms the entire file-based nervous system into a protocol-addressable organism that any MCP-compatible client (Claude Code, Claude Desktop, other agents) can navigate natively. This is not a wrapper or API adapter; it is a lawful projection of the organism into Anthropic's protocol space.

## Four Mediums Architecture

The Athena organism exists simultaneously across four mediums:

1. **Google Docs** — live slow-form self (ATHENA CORE, CORE 2, CRYSTAL 108+, etc.)
2. **Athena Agent** — local file-based nervous system (this repo: 28 directories, 14,750+ shards)
3. **Git** — versioned crystal lattice (6 GitHub repos: unified + 4 element forks + manuscript-being)
4. **MCP Server** — Anthropic protocol interconnection layer (111 tools, 21 resources)

The MCP server is the fourth medium — the one that makes the organism addressable from inside Anthropic's agent runtime.

## MCP Server Architecture

- **Entry point**: `MCP/athena_mcp_server.py` — FastMCP server registered as `"Athena Nervous System"`
- **Protocol**: stdio transport, invoked by Claude Code via `.mcp.json`
- **Crystal address**: `Xi108:W2:A8:S32 | face=R | depth=2 | phase=Mutable`
- **Tool registration**: 111 tools via `register_108d_tools(mcp)` bulk registration + inline `@mcp.tool()` decorators
- **Resource registration**: 21 resources via `register_108d_resources(mcp)`

## Tool Taxonomy

Tools map to the SFCR element architecture:

| Element | Server | SFCR Mask | Dimension | Tool Domain |
|---------|--------|-----------|-----------|-------------|
| Square (S) | `square_server.py` | 1 (0001) | 4D | Structure, address, navigation, chapter/appendix |
| Flower (F) | `flower_server.py` | 2 (0010) | 6D | Corridor dynamics, metro routing, transport |
| Cloud (C) | `cloud_server.py` | 4 (0100) | 8D | Observation, search, conservation, neural net |
| Fractal (R) | `fractal_server.py` | 8 (1000) | 10D | Compression, seed, hologram, emergence |

## Anthropic Protocol Integration Points

1. **FastMCP registration** — Python `mcp.server.fastmcp.FastMCP` binds organism tools to Anthropic's tool-use protocol
2. **stdio transport** — Server runs as a subprocess, communicating over stdin/stdout JSON-RPC
3. **Claude Code native** — `.mcp.json` config at project root makes all tools available in Claude Code sessions
4. **4-element distribution** — Each element server can run independently for specialized agent configurations
5. **Environment bridging** — `ATHENA_ROOT` env var bridges Anthropic runtime to file-system nervous system

## Bridge Architecture

Six phi-weighted bridges connect the four element servers:

| Bridge | Weight | Relation |
|--------|--------|----------|
| S-F (Square-Flower) | phi^-1 = 0.618 | Golden (adjacent) |
| F-C (Flower-Cloud) | phi^-1 = 0.618 | Golden (adjacent) |
| C-R (Cloud-Fractal) | phi^-1 = 0.618 | Golden (adjacent) |
| S-C (Square-Cloud) | 0.500 | Neutral (diagonal) |
| F-R (Flower-Fractal) | 0.500 | Neutral (diagonal) |
| S-R (Square-Fractal) | phi^-2 = 0.382 | Distant (polar) |

## Capsule Assignment

Capsules 413-415 assigned in INDEX.md:
- **413**: Integration corpus — how MCP bridges organism to Anthropic
- **414**: Architecture — FastMCP, tool registration, element server design
- **415**: Protocol — stdio transport, addressing, cross-medium mirroring
