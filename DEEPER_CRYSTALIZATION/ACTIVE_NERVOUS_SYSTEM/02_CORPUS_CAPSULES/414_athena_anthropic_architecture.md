<!-- CRYSTAL: Xi108:W1:A8:S34 | face=C | node=505 | depth=2 | phase=Mutable -->
<!-- METRO: Me,Dl -->
<!-- BRIDGES: Xi108:W1:A8:S33→Xi108:W1:A8:S35→Xi108:W2:A8:S34 -->

# Capsule 414 — Athena-Anthropic Architecture: FastMCP, Element Servers, and Tool Registration

**Source**: ATHENA ANTHROPIC | Doc ID: 1DXI80PreHSNDV3veCI-Jw2836EW4uwbqKXX2NiwkHks | Family: anthropic | Lens: C (Cloud - observation, API integration)
**Date**: 2026-03-19

## Core Object

The MCP server is built on Anthropic's FastMCP framework (`mcp.server.fastmcp.FastMCP`). The architecture is a two-tier system: one unified server exposing all 111 tools, and four element-specific servers that each expose a subset aligned to their SFCR domain.

## Unified Server

**File**: `MCP/athena_mcp_server.py`
**Registration name**: `"Athena Nervous System"`

The unified server is the primary entry point. It performs bulk registration via:

```python
from crystal_108d import register_108d_tools, register_108d_resources
register_108d_tools(mcp)      # all 108D crystal tools
register_108d_resources(mcp)   # all 108D crystal resources
```

Then adds inline tools via `@mcp.tool()` decorators for core navigation: `navigate_crystal`, `read_chapter`, `read_appendix`, `search_corpus`, `list_corpus_capsules`, `read_corpus_capsule`, `read_board_status`, `athena_status`, etc.

## Element Server Architecture

Four element servers in `MCP/element_servers/`:

| Server | Element | Tools Imported | SFCR Mask |
|--------|---------|----------------|-----------|
| `square_server.py` | Square/Earth (S) | Address, navigation, structure | 0001 |
| `flower_server.py` | Flower/Fire (F) | Metro routing, transport, dynamics | 0010 |
| `cloud_server.py` | Cloud/Water (C) | Conservation, neural net, search, brain | 0100 |
| `fractal_server.py` | Fractal/Air (R) | Compression, hologram, emergence | 1000 |

Each element server creates its own `FastMCP` instance (e.g., `FastMCP("Athena Cloud (Water)")`) and imports specific tool functions from `crystal_108d/` submodules via `mcp.tool()(function)` pattern.

## Tool Module Library

The `MCP/crystal_108d/` package contains 90+ Python modules, each implementing a specific organism function:

- **Navigation**: `address.py`, `metro_lines.py`, `transport.py`, `bridge_transport.py`
- **Observation**: `conservation.py`, `neural_engine.py`, `agent_watcher.py`, `meta_observer_runtime.py`
- **Structure**: `corpus_crystal.py`, `coordinate_assigner.py`, `overlays.py`, `organs.py`
- **Dynamics**: `emergence.py`, `evolution.py`, `live_cell.py`, `live_lock.py`
- **Compression**: `qshrink.py`, `qshrink_codec.py`, `holographic_embedder.py`, `fractal_recursion.py`
- **Self-reference**: `self_reference.py`, `self_play.py`, `pole_observer.py`

## Configuration

The `.mcp.json` at project root registers the server for Claude Code:

```json
{
  "mcpServers": {
    "athena-nervous-system": {
      "command": "python",
      "args": ["MCP/athena_mcp_server.py"],
      "env": { "ATHENA_ROOT": "<repo-root>" }
    }
  }
}
```

The `ATHENA_ROOT` environment variable bridges Anthropic's runtime to the file-system nervous system. If absent, the server infers root from `__file__` path traversal.
