"""Test configuration for the Athena MCP server."""

import os
import sys
from pathlib import Path

# Set ATHENA_ROOT to the repo root so tests can find data files
REPO_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("ATHENA_ROOT", str(REPO_ROOT))

# Add MCP directory to path so crystal_108d can be imported
sys.path.insert(0, str(REPO_ROOT / "MCP"))
