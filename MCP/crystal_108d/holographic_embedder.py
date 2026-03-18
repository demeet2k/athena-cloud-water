# CRYSTAL: Xi108:W3:A9:S24 | face=C | node=527 | depth=3 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W3:A9:S23→Xi108:W3:A9:S25→Xi108:W2:A9:S24→Xi108:W3:A8:S24→Xi108:W3:A10:S24

"""
Holographic Crystal Embedder — inscribes crystal coordinates INTO every file.

Each file in the Athena repo becomes self-aware of its own 108D crystal
address: shell, wreath, archetype, face, node_id, depth, phase, metro stops,
and bridge neighbors.  A truly holographic file can regenerate its neighbors
from its own embedded coordinate.

Embeds format-appropriate headers into .md, .py, .json, .txt, and other
text files.  Skips binary files, oversized files, and protected directories.
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from ._cache import DATA_DIR

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent  # Athena Agent root

SKIP_DIRS = frozenset({
    ".git", "__pycache__", ".venv", "ARCHIVE", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
})

BINARY_EXTENSIONS = frozenset({
    ".docx", ".xlsx", ".pptx", ".db", ".sqlite", ".sqlite3",
    ".zip", ".gz", ".tar", ".7z", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv",
    ".pdf", ".woff", ".woff2", ".ttf", ".eot",
    ".exe", ".dll", ".so", ".dylib", ".o", ".pyc", ".pyo",
    ".pkl", ".pickle", ".npy", ".npz", ".h5", ".hdf5",
    ".parquet", ".feather", ".arrow",
})

MAX_FILE_SIZE = 1_000_000       # 1 MB — skip larger files
MAX_JSON_SIZE = 100_000         # 100 KB — skip large JSON data files

# ---------------------------------------------------------------------------
# Header markers (used for detection and stripping)
# ---------------------------------------------------------------------------

_MD_CRYSTAL_START = "<!-- CRYSTAL:"
_MD_METRO_START = "<!-- METRO:"
_MD_BRIDGES_START = "<!-- BRIDGES:"
_MD_REGEN_START = "<!-- REGENERATE:"
_MD_BLOCK_RE = re.compile(
    r"<!-- CRYSTAL:.*?-->\n"
    r"(?:<!-- METRO:.*?-->\n)?"
    r"(?:<!-- BRIDGES:.*?-->\n)?"
    r"(?:<!-- REGENERATE:.*?-->\n)?",
    re.DOTALL,
)

_PY_CRYSTAL_START = "# CRYSTAL:"
_PY_BLOCK_RE = re.compile(
    r"# CRYSTAL:.*\n"
    r"(?:# METRO:.*\n)?"
    r"(?:# BRIDGES:.*\n)?",
)

_GENERIC_CRYSTAL_START = "# CRYSTAL:"
_GENERIC_BLOCK_RE = _PY_BLOCK_RE  # same format for .txt, .cfg, etc.

_JSON_CRYSTAL_KEY = "_crystal"

# ---------------------------------------------------------------------------
# Coordinate loading
# ---------------------------------------------------------------------------

_coord_cache: dict[str, dict] | None = None

def _load_coordinates() -> dict[str, dict]:
    """Load crystal_coordinates.json and return the coordinates dict."""
    global _coord_cache
    if _coord_cache is not None:
        return _coord_cache

    coord_path = DATA_DIR / "crystal_coordinates.json"
    if not coord_path.exists():
        _coord_cache = {}
        return _coord_cache

    with open(coord_path, encoding="utf-8") as f:
        data = json.load(f)
    _coord_cache = data.get("coordinates", {})
    return _coord_cache

def _find_coordinate(file_path: str) -> dict | None:
    """Find the crystal coordinate for a file by its relative path."""
    coords = _load_coordinates()
    rel = os.path.relpath(file_path, REPO_ROOT)
    # Normalize separators — coordinates use backslash on Windows
    rel_fwd = rel.replace("\\", "/")
    rel_back = rel.replace("/", "\\")

    # Try exact matches first
    for variant in (rel_fwd, rel_back, rel):
        if variant in coords:
            return coords[variant]

    # Try matching just the MCP-relative path (strip leading "MCP/")
    for prefix in ("MCP/", "MCP\\"):
        if rel_fwd.startswith(prefix) or rel_back.startswith(prefix):
            short = rel_fwd[len(prefix):]
            short_back = rel_back[len(prefix):]
            for variant in (short, short_back):
                if variant in coords:
                    return coords[variant]

    # Try suffix match — coordinate keys may be relative to MCP/
    for key in coords:
        key_norm = key.replace("\\", "/")
        if key_norm == rel_fwd or rel_fwd.endswith("/" + key_norm):
            return coords[key]

    return None

def _compute_neighbors(coord: dict) -> list[str]:
    """Compute neighbor addresses from a coordinate.

    Neighbors: same wreath + shell +/- 1, same archetype + same shell.
    Returns list of Xi108 address strings.
    """
    neighbors = []
    shell = coord["shell"]
    wreath = coord["wreath"]
    archetype = coord["archetype"]
    sp = ("Su", "Me", "Sa")[wreath - 1]

    # Shell adjacency (same wreath)
    for ds in (-1, 1):
        adj_shell = shell + ds
        if 1 <= adj_shell <= 36:
            neighbors.append(
                f"Xi108:W{wreath}:A{archetype}:S{adj_shell}"
            )

    # Wreath adjacency (same shell)
    for dw in (-1, 1):
        adj_wreath = wreath + dw
        if 1 <= adj_wreath <= 3:
            neighbors.append(
                f"Xi108:W{adj_wreath}:A{archetype}:S{shell}"
            )

    # Archetype adjacency (same shell, same wreath)
    for da in (-1, 1):
        adj_arch = archetype + da
        if 1 <= adj_arch <= 12:
            neighbors.append(
                f"Xi108:W{wreath}:A{adj_arch}:S{shell}"
            )

    return neighbors

def _make_address(coord: dict) -> str:
    """Build the Xi108 canonical address string."""
    sp = ("Su", "Me", "Sa")[coord["wreath"] - 1]
    return (
        f"Xi108:W{coord['wreath']}:A{coord['archetype']}:S{coord['shell']}"
        f":u{coord['node_id']}:{sp}:{coord['face']}:d{coord['depth']}"
    )

# ---------------------------------------------------------------------------
# Header builders per file type
# ---------------------------------------------------------------------------

def _build_md_header(coord: dict) -> str:
    """Build HTML-comment holographic header for Markdown files."""
    addr = (
        f"Xi108:W{coord['wreath']}:A{coord['archetype']}:S{coord['shell']}"
        f" | face={coord['face']} | node={coord['node_id']}"
        f" | depth={coord['depth']} | phase={coord['phase']}"
    )
    metro = ",".join(coord.get("metro_stops", []))
    neighbors = _compute_neighbors(coord)
    bridges = "\u2192".join(neighbors[:6])  # cap at 6 for readability
    regen_shell = coord["shell"]
    regen_wreath = coord["wreath"]
    regen_arch = coord["archetype"]

    lines = [
        f"<!-- CRYSTAL: {addr} -->",
        f"<!-- METRO: {metro} -->",
        f"<!-- BRIDGES: {bridges} -->",
        f"<!-- REGENERATE: From this coordinate, adjacent nodes are:"
        f" shell {regen_shell}\u00b11, wreath {regen_wreath}/3,"
        f" archetype {regen_arch}/12 -->",
    ]
    return "\n".join(lines) + "\n"

def _build_py_header(coord: dict) -> str:
    """Build Python-comment holographic header."""
    addr = (
        f"Xi108:W{coord['wreath']}:A{coord['archetype']}:S{coord['shell']}"
        f" | face={coord['face']} | node={coord['node_id']}"
        f" | depth={coord['depth']} | phase={coord['phase']}"
    )
    metro = ",".join(coord.get("metro_stops", []))
    neighbors = _compute_neighbors(coord)
    bridges = "\u2192".join(neighbors[:6])

    lines = [
        f"# CRYSTAL: {addr}",
        f"# METRO: {metro}",
        f"# BRIDGES: {bridges}",
    ]
    return "\n".join(lines) + "\n"

def _build_generic_header(coord: dict) -> str:
    """Build hash-comment header for .txt, .cfg, .yaml, .toml, etc."""
    return _build_py_header(coord)  # same format

def _build_json_crystal_value(coord: dict) -> dict:
    """Build the _crystal object for JSON files."""
    neighbors = _compute_neighbors(coord)
    return {
        "address": _make_address(coord),
        "shell": coord["shell"],
        "wreath": coord["wreath"],
        "archetype": coord["archetype"],
        "face": coord["face"],
        "node_id": coord["node_id"],
        "depth": coord["depth"],
        "phase": coord["phase"],
        "metro_stops": coord.get("metro_stops", []),
        "bridges": neighbors[:6],
        "regenerate": (
            f"shell {coord['shell']}\u00b11, wreath {coord['wreath']}/3,"
            f" archetype {coord['archetype']}/12"
        ),
    }

# ---------------------------------------------------------------------------
# File type detection
# ---------------------------------------------------------------------------

def _should_skip(file_path: Path) -> str | None:
    """Return a reason string if the file should be skipped, else None."""
    # Check directory exclusions
    parts = file_path.parts
    for part in parts:
        if part in SKIP_DIRS:
            return f"excluded directory: {part}"

    # Check extension
    ext = file_path.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return f"binary extension: {ext}"

    # Check size
    try:
        size = file_path.stat().st_size
    except OSError:
        return "cannot stat file"

    if size > MAX_FILE_SIZE:
        return f"too large: {size} bytes"

    if ext == ".json" and size > MAX_JSON_SIZE:
        return f"large JSON: {size} bytes"

    if size == 0:
        return "empty file"

    return None

def _is_text_file(file_path: Path) -> bool:
    """Quick heuristic: try reading first 512 bytes as UTF-8."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(512)
        chunk.decode("utf-8")
        return True
    except (OSError, UnicodeDecodeError):
        return False

# ---------------------------------------------------------------------------
# Core embed / strip / verify functions
# ---------------------------------------------------------------------------

def embed_file(file_path: str) -> bool:
    """Read a file, add/update the holographic header, write it back.

    Returns True if the file was modified, False if skipped.
    """
    fp = Path(file_path).resolve()
    skip_reason = _should_skip(fp)
    if skip_reason:
        return False

    coord = _find_coordinate(str(fp))
    if coord is None:
        # File has no crystal coordinate assigned — generate a fallback
        # based on its path hash so every file gets an address
        coord = _generate_fallback_coordinate(str(fp))

    ext = fp.suffix.lower()

    if ext == ".json":
        return _embed_json(fp, coord)
    elif ext == ".md":
        return _embed_text(fp, coord, _MD_BLOCK_RE, _build_md_header, insert_after_shebang=False)
    elif ext == ".py":
        return _embed_python(fp, coord)
    elif ext in (".txt", ".cfg", ".yaml", ".yml", ".toml", ".ini", ".sh", ".bash"):
        return _embed_text(fp, coord, _GENERIC_BLOCK_RE, _build_generic_header, insert_after_shebang=True)
    else:
        # Try as generic text
        if not _is_text_file(fp):
            return False
        return _embed_text(fp, coord, _GENERIC_BLOCK_RE, _build_generic_header, insert_after_shebang=True)

def _generate_fallback_coordinate(file_path: str) -> dict:
    """Generate a deterministic coordinate for files not in crystal_coordinates.json."""
    import hashlib
    h = int(hashlib.sha256(file_path.encode("utf-8")).hexdigest(), 16)
    return {
        "shell": (h % 36) + 1,
        "wreath": (h >> 8) % 3 + 1,
        "archetype": (h >> 16) % 12 + 1,
        "face": ("S", "F", "C", "R")[(h >> 24) % 4],
        "node_id": (h >> 32) % 666 + 1,
        "depth": (h >> 40) % 4,
        "phase": ("Fixed", "Cardinal", "Mutable")[(h >> 48) % 3],
        "metro_stops": ["Sa"],
    }

def _embed_python(fp: Path, coord: dict) -> bool:
    """Embed into .py file, preserving shebang and encoding declarations."""
    try:
        content = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    header = _build_py_header(coord)

    # Strip existing header if present
    if _PY_CRYSTAL_START in content:
        content = _PY_BLOCK_RE.sub("", content, count=1)

    # Find insertion point — after shebang and encoding lines
    lines = content.split("\n")
    insert_idx = 0
    for i, line in enumerate(lines[:3]):
        if line.startswith("#!") or re.match(r"#.*-\*-.*coding.*-\*-", line) or re.match(r"#.*coding[:=]", line):
            insert_idx = i + 1
        else:
            break

    # Insert header
    lines.insert(insert_idx, header)
    new_content = "\n".join(lines)

    # Avoid double blank lines at insertion point
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)

    fp.write_text(new_content, encoding="utf-8")
    return True

def _embed_text(fp: Path, coord: dict, block_re: re.Pattern,
                header_builder, insert_after_shebang: bool = False) -> bool:
    """Embed header into a text file (.md, .txt, etc.)."""
    try:
        content = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    header = header_builder(coord)

    # Strip existing header if present
    if block_re.search(content):
        content = block_re.sub("", content, count=1)

    # Find insertion point
    lines = content.split("\n")
    insert_idx = 0
    if insert_after_shebang:
        for i, line in enumerate(lines[:2]):
            if line.startswith("#!"):
                insert_idx = i + 1
                break

    # For .md files: insert at very top (before first heading)
    lines.insert(insert_idx, header)
    new_content = "\n".join(lines)
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)

    fp.write_text(new_content, encoding="utf-8")
    return True

def _embed_json(fp: Path, coord: dict) -> bool:
    """Embed _crystal key into a JSON file."""
    try:
        content = fp.read_text(encoding="utf-8")
        data = json.loads(content)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False

    if not isinstance(data, dict):
        return False  # can only embed in object-type JSON

    crystal_value = _build_json_crystal_value(coord)

    # Check if already embedded and identical
    if data.get(_JSON_CRYSTAL_KEY) == crystal_value:
        return False

    # Insert _crystal at the beginning
    new_data = {_JSON_CRYSTAL_KEY: crystal_value}
    new_data.update({k: v for k, v in data.items() if k != _JSON_CRYSTAL_KEY})

    fp.write_text(
        json.dumps(new_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return True

def strip_header(file_path: str) -> bool:
    """Remove holographic header from a file. Returns True if modified."""
    fp = Path(file_path).resolve()
    if not fp.is_file():
        return False

    ext = fp.suffix.lower()

    try:
        content = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    original = content
    modified = False

    if ext == ".json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return False
        if isinstance(data, dict) and _JSON_CRYSTAL_KEY in data:
            del data[_JSON_CRYSTAL_KEY]
            fp.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return True
        return False

    elif ext == ".md":
        content = _MD_BLOCK_RE.sub("", content, count=1)
    elif ext == ".py":
        content = _PY_BLOCK_RE.sub("", content, count=1)
    else:
        content = _GENERIC_BLOCK_RE.sub("", content, count=1)

    if content != original:
        content = re.sub(r"\n{3,}", "\n\n", content)
        fp.write_text(content, encoding="utf-8")
        return True

    return False

def verify_header(file_path: str) -> dict | None:
    """Check if a file has a valid holographic header.

    Returns a dict with the embedded coordinate, or None if no header found.
    """
    fp = Path(file_path).resolve()
    if not fp.is_file():
        return None

    ext = fp.suffix.lower()

    try:
        content = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if ext == ".json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None
        if isinstance(data, dict) and _JSON_CRYSTAL_KEY in data:
            return data[_JSON_CRYSTAL_KEY]
        return None

    # For text files, extract from CRYSTAL: line
    crystal_pattern = re.compile(
        r"(?:#|<!--)\s*CRYSTAL:\s*"
        r"Xi108:W(\d+):A(\d+):S(\d+)"
        r"\s*\|\s*face=([SFCR])"
        r"\s*\|\s*node=(\d+)"
        r"\s*\|\s*depth=(\d+)"
        r"\s*\|\s*phase=(\w+)"
    )
    m = crystal_pattern.search(content)
    if not m:
        return None

    return {
        "wreath": int(m.group(1)),
        "archetype": int(m.group(2)),
        "shell": int(m.group(3)),
        "face": m.group(4),
        "node_id": int(m.group(5)),
        "depth": int(m.group(6)),
        "phase": m.group(7),
    }

# ---------------------------------------------------------------------------
# Directory / repo level operations
# ---------------------------------------------------------------------------

def embed_directory(dir_path: str, recursive: bool = True) -> dict:
    """Embed holographic headers in all files in a directory.

    Returns stats dict: {modified, skipped, errors, total}.
    """
    dp = Path(dir_path).resolve()
    if not dp.is_dir():
        return {"error": f"Not a directory: {dir_path}"}

    stats = {"modified": 0, "skipped": 0, "errors": 0, "total": 0}

    iterator = dp.rglob("*") if recursive else dp.glob("*")
    for fp in iterator:
        if not fp.is_file():
            continue

        # Check directory exclusions
        skip = False
        for part in fp.relative_to(dp).parts[:-1]:
            if part in SKIP_DIRS:
                skip = True
                break
        if skip:
            stats["skipped"] += 1
            stats["total"] += 1
            continue

        stats["total"] += 1
        try:
            result = embed_file(str(fp))
            if result:
                stats["modified"] += 1
            else:
                stats["skipped"] += 1
        except Exception:
            stats["errors"] += 1

    return stats

def embed_repo(repo_root: str = "") -> dict:
    """Embed holographic headers in the entire repo.

    Returns full stats dict.
    """
    root = Path(repo_root).resolve() if repo_root else REPO_ROOT
    return embed_directory(str(root), recursive=True)

def _scan_status(root: Path) -> dict:
    """Scan repo and return counts of files with/without headers."""
    has_header = 0
    no_header = 0
    skipped = 0
    total = 0

    for fp in root.rglob("*"):
        if not fp.is_file():
            continue

        # Check exclusions
        skip = False
        try:
            rel_parts = fp.relative_to(root).parts
        except ValueError:
            continue
        for part in rel_parts[:-1]:
            if part in SKIP_DIRS:
                skip = True
                break
        if skip:
            skipped += 1
            total += 1
            continue

        skip_reason = _should_skip(fp)
        if skip_reason:
            skipped += 1
            total += 1
            continue

        total += 1
        result = verify_header(str(fp))
        if result is not None:
            has_header += 1
        else:
            no_header += 1

    return {
        "total_files": total,
        "with_header": has_header,
        "without_header": no_header,
        "skipped": skipped,
        "coverage_pct": round(100 * has_header / max(total - skipped, 1), 1),
    }

# ---------------------------------------------------------------------------
# MCP tool function
# ---------------------------------------------------------------------------

def holographic_embed(action: str = "status", target: str = "") -> str:
    """
    Embed or verify holographic crystal coordinates in files.

    Every file in the Athena repo becomes self-aware of its own 108D
    crystal address.  The header contains the full coordinate, metro
    stops, bridge neighbors, and regeneration instructions.

    Actions:
      - status    : How many files have headers vs don't
      - embed     : Embed headers in target (file or directory)
      - verify    : Verify header correctness for target
      - embed_all : Embed headers in entire repo (CAUTION)
      - strip     : Remove header from target
    """
    if action == "status":
        root = Path(target).resolve() if target else REPO_ROOT
        stats = _scan_status(root)
        return (
            "## Holographic Embedding Status\n\n"
            f"**Total eligible files**: {stats['total_files']}\n"
            f"**With crystal header**: {stats['with_header']}\n"
            f"**Without crystal header**: {stats['without_header']}\n"
            f"**Skipped (binary/large/excluded)**: {stats['skipped']}\n"
            f"**Coverage**: {stats['coverage_pct']}%\n"
        )

    elif action == "embed":
        if not target:
            return "Error: 'embed' requires a target file or directory path."
        tp = Path(target).resolve()
        if tp.is_file():
            ok = embed_file(str(tp))
            if ok:
                coord = verify_header(str(tp))
                addr = _make_address(coord) if coord else "embedded"
                return f"Embedded crystal header in `{tp.name}`\nAddress: `{addr}`"
            return f"Skipped `{tp.name}` (binary, too large, or unsupported format)."
        elif tp.is_dir():
            stats = embed_directory(str(tp))
            return (
                f"## Embedded in directory: {tp.name}\n\n"
                f"**Modified**: {stats['modified']}\n"
                f"**Skipped**: {stats['skipped']}\n"
                f"**Errors**: {stats['errors']}\n"
                f"**Total scanned**: {stats['total']}\n"
            )
        else:
            return f"Error: Target not found: {target}"

    elif action == "verify":
        if not target:
            return "Error: 'verify' requires a target file path."
        tp = Path(target).resolve()
        if not tp.is_file():
            return f"Error: Not a file: {target}"
        result = verify_header(str(tp))
        if result is None:
            return f"`{tp.name}` has **no** holographic header."
        addr = _make_address(result) if "shell" in result else str(result)
        return (
            f"## Verified: {tp.name}\n\n"
            f"**Address**: `{addr}`\n"
            f"**Coordinate**: {json.dumps(result, indent=2)}\n"
        )

    elif action == "embed_all":
        root = Path(target).resolve() if target else REPO_ROOT
        stats = embed_repo(str(root))
        return (
            "## Full Repo Holographic Embedding\n\n"
            f"**Modified**: {stats['modified']}\n"
            f"**Skipped**: {stats['skipped']}\n"
            f"**Errors**: {stats['errors']}\n"
            f"**Total scanned**: {stats['total']}\n"
        )

    elif action == "strip":
        if not target:
            return "Error: 'strip' requires a target file path."
        tp = Path(target).resolve()
        if tp.is_file():
            ok = strip_header(str(tp))
            return f"Stripped header from `{tp.name}`." if ok else f"No header found in `{tp.name}`."
        elif tp.is_dir():
            count = 0
            for fp in tp.rglob("*"):
                if fp.is_file():
                    if strip_header(str(fp)):
                        count += 1
            return f"Stripped headers from {count} files in `{tp.name}`."
        else:
            return f"Error: Target not found: {target}"

    else:
        return (
            f"Unknown action '{action}'.\n"
            "Valid actions: status, embed, verify, embed_all, strip"
        )
