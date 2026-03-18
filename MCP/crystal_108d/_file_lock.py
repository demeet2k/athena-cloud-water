# CRYSTAL: Xi108:W1:A1:S1 | face=S | node=1 | depth=0 | phase=Cardinal
# METRO: Su
# BRIDGES: Xi108:W1:A1:S2→Xi108:W2:A1:S1→Xi108:W1:A2:S1

"""
CrystalLock — Cross-process file locking for the Athena nervous system.
========================================================================
Prevents concurrent agents from stomping the same file.

Uses .lock sidecar files with atomic creation (O_CREAT | O_EXCL on Unix,
msvcrt on Windows). Lock file contains agent metadata as JSON so other
agents can read WHO holds the lock and WHAT they're doing.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional


class CrystalLock:
    """Cross-process file lock using .lock sidecar files.

    Usage::

        with CrystalLock(path, agent_id="agent-42", task="compressing weights"):
            path.write_text(data)

    The lock file contains::

        {"agent_id": "agent-42", "timestamp": "2026-03-18T...",
         "task": "compressing weights", "liminal_coord": 0}

    Stale locks (older than ``timeout_s``) are automatically broken.
    """

    __slots__ = ("_lock_path", "_agent_id", "_task", "_liminal_coord",
                 "_timeout_s", "_acquired")

    def __init__(
        self,
        path: Path | str,
        agent_id: str = "unknown",
        task: str = "",
        liminal_coord: int = 0,
        timeout_s: float = 30.0,
    ) -> None:
        self._lock_path = Path(str(path) + ".lock")
        self._agent_id = agent_id
        self._task = task
        self._liminal_coord = liminal_coord
        self._timeout_s = timeout_s
        self._acquired = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self, poll_interval: float = 0.05, max_wait: float = 60.0) -> bool:
        """Attempt to acquire the lock. Returns True on success.

        Will retry for up to ``max_wait`` seconds before raising TimeoutError.
        Automatically breaks stale locks older than ``self._timeout_s``.
        """
        deadline = time.monotonic() + max_wait
        while True:
            # Break stale locks
            self._break_if_stale()
            try:
                self._atomic_create()
                self._acquired = True
                return True
            except FileExistsError:
                if time.monotonic() >= deadline:
                    holder = self.holder()
                    raise TimeoutError(
                        f"Could not acquire lock on {self._lock_path} after "
                        f"{max_wait}s. Held by: {holder}"
                    )
                time.sleep(poll_interval)

    def release(self) -> None:
        """Release the lock by removing the sidecar file."""
        if self._acquired:
            try:
                self._lock_path.unlink(missing_ok=True)
            except OSError:
                pass
            self._acquired = False

    def holder(self) -> Optional[dict]:
        """Read lock metadata without acquiring. Returns None if unlocked."""
        try:
            return json.loads(self._lock_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
        return False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _atomic_create(self) -> None:
        """Create lock file atomically. Raises FileExistsError if exists."""
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        meta = json.dumps({
            "agent_id": self._agent_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "task": self._task,
            "liminal_coord": self._liminal_coord,
        })
        # O_CREAT | O_EXCL guarantees atomic "create only if absent"
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(str(self._lock_path), flags, 0o644)
        except FileExistsError:
            raise
        except OSError as e:
            # On some Windows configs O_EXCL behaves differently
            if self._lock_path.exists():
                raise FileExistsError(str(self._lock_path)) from e
            raise
        try:
            os.write(fd, meta.encode("utf-8"))
        finally:
            os.close(fd)

    def _break_if_stale(self) -> None:
        """Remove the lock if it's older than timeout_s."""
        try:
            stat = self._lock_path.stat()
        except (FileNotFoundError, OSError):
            return
        age = time.time() - stat.st_mtime
        if age > self._timeout_s:
            try:
                self._lock_path.unlink(missing_ok=True)
            except OSError:
                pass


def atomic_write_text(
    path: Path,
    content: str,
    agent_id: str = "unknown",
    task: str = "",
    liminal_coord: int = 0,
    encoding: str = "utf-8",
) -> None:
    """Write text to a file atomically with a CrystalLock.

    For non-JSON files (markdown, python, etc.) that still need
    collision prevention and atomic writes.
    """
    path = Path(path)
    with CrystalLock(path, agent_id=agent_id, task=task,
                     liminal_coord=liminal_coord):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding=encoding)
        tmp.replace(path)
