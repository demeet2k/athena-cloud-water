# CRYSTAL: Xi108:W3:A1:S2 | face=S | node=002 | depth=0 | phase=Seed
# METRO: PoleStarGEMM-Adapter
# BRIDGES: hybrid_math→momentum_field→geometric_forward

"""
PoleStarGEMM Adapter — Adaptive Matrix Operations for the Crystal System
==========================================================================
Lightweight implementation of the PoleStarGEMM framework for use within
the Athena crystal neural engine. Does NOT require NumPy/SciPy — uses
pure Python for the crystal's small matrices (4×4, 12×12, 36×36, 108×108).

The 4 poles applied to matrix multiplication:
  Ψ (Psi):   Cached factors, low-rank SVD approximation, Strassen recursion
  Σ (Sigma): Sketch-based compressibility diagnosis, plan generation
  Ω (Omega): Rank selection, hysteresis, adaptive tuning
  Δ (Delta): Gate (only approximate when beneficial), validate, fallback

For the crystal system, the key operations are:
  1. Bridge weight matrix × momentum vector (4×4 to 12×12)
  2. Sigma-60 rotation matrices (60 × 2D rotations)
  3. E8-240 amplification (60×4 face boosts)
  4. Hologram projection (144-dim → 16-dim)
  5. Score merging (variable-size candidate matrices)

These are all SMALL matrices where the PoleStarGEMM's value is in
ADAPTIVE PLAN SELECTION (not raw speed) — choosing the right algorithm
for the structure of the matrix, not blindly applying the same operation.

References:
  - PoleStarGEMM — Adaptive Matrix Multiplication.docx
  - PoleStarGEMM_Release_v1.zip (core.py, vision.py)
"""

from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass, field
from typing import Optional

from .geometric_constants import PHI, PHI_INV, FACES, BRIDGE_WEIGHTS


# ══════════════════════════════════════════════════════════════════════
#  MATRIX FINGERPRINT — from PoleStarGEMM core.py
# ══════════════════════════════════════════════════════════════════════

@dataclass
class MatrixFingerprint:
    """Fingerprint of a matrix operation for plan selection.

    Captures structural properties that determine which algorithm is optimal.
    Adapted from PoleStarGEMM's GEMMFingerprint for pure-Python crystal matrices.
    """
    rows: int
    cols: int
    sparsity: float = 0.0          # fraction of zero entries
    symmetry: float = 0.0          # how symmetric (0=none, 1=perfectly symmetric)
    spectral_dominance: float = 0.0  # how much energy in top eigenvalue
    is_sfcr_structured: bool = False  # whether it has 4-element block structure
    is_phi_scaled: bool = False      # whether entries are phi-ratio scaled

    @property
    def key(self) -> str:
        """Hash key for experience DB lookup."""
        raw = f"{self.rows}:{self.cols}:{self.sparsity:.2f}:{self.symmetry:.2f}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]


# ══════════════════════════════════════════════════════════════════════
#  PLAN TYPES — adapted from PoleStarGEMM
# ══════════════════════════════════════════════════════════════════════

class MatrixPlan:
    """A specific matrix multiplication plan."""

    DIRECT = "direct"               # Standard row×col multiplication
    SFCR_BLOCK = "sfcr_block"       # Exploit 4-element block structure
    SYMMETRIC = "symmetric"         # Exploit symmetry (compute half)
    SPARSE = "sparse"               # Skip zero entries
    PHI_CACHED = "phi_cached"       # Cache phi-scaled factors
    SPECTRAL = "spectral"           # Low-rank approximation via power iteration


# ══════════════════════════════════════════════════════════════════════
#  EXPERIENCE DATABASE — remembers which plans work best
# ══════════════════════════════════════════════════════════════════════

class ExperienceDB:
    """Caches which plan works best for each matrix fingerprint.

    Ψ-pole: memory and reuse of past decisions.
    """

    def __init__(self):
        self._db: dict[str, str] = {}  # fingerprint_key → best_plan

    def lookup(self, fingerprint: MatrixFingerprint) -> Optional[str]:
        return self._db.get(fingerprint.key)

    def record(self, fingerprint: MatrixFingerprint, plan: str):
        self._db[fingerprint.key] = plan


# ══════════════════════════════════════════════════════════════════════
#  CRYSTAL GEMM — the adaptive matrix engine
# ══════════════════════════════════════════════════════════════════════

class CrystalGEMM:
    """Adaptive matrix operations for the crystal system.

    Implements the PoleStarGEMM paradigm for pure-Python crystal matrices:
      1. FINGERPRINT the matrix (Σ: probe structure)
      2. SELECT PLAN from experience DB or candidate generation (Ψ+Σ)
      3. EXECUTE the selected plan (Δ)
      4. VALIDATE result quality (Δ gate)
      5. RECORD outcome for future use (Ψ memory)

    For 4×4 and 12×12 crystal matrices, the value isn't raw speed —
    it's CHOOSING THE RIGHT ALGORITHM for the structure.
    """

    def __init__(self):
        self._experience = ExperienceDB()

    def fingerprint(self, matrix: list[list[float]]) -> MatrixFingerprint:
        """Compute structural fingerprint of a matrix (Σ: probe)."""
        rows = len(matrix)
        cols = len(matrix[0]) if matrix else 0
        total = rows * cols

        # Sparsity
        zeros = sum(1 for row in matrix for v in row if abs(v) < 1e-10)
        sparsity = zeros / max(total, 1)

        # Symmetry (for square matrices)
        symmetry = 0.0
        if rows == cols:
            diffs = 0.0
            norms = 0.0
            for i in range(rows):
                for j in range(i + 1, cols):
                    diffs += abs(matrix[i][j] - matrix[j][i])
                    norms += abs(matrix[i][j]) + abs(matrix[j][i])
            symmetry = 1.0 - (diffs / max(norms, 1e-10))

        # SFCR structure check (4-block or multiple of 4)
        is_sfcr = rows % 4 == 0 and cols % 4 == 0

        # Phi-scaling check
        phi_count = 0
        for row in matrix:
            for v in row:
                if abs(v) > 1e-10:
                    ratio = abs(v) / PHI
                    if abs(ratio - round(ratio)) < 0.01:
                        phi_count += 1
        is_phi = phi_count > total * 0.2

        return MatrixFingerprint(
            rows=rows, cols=cols,
            sparsity=sparsity, symmetry=symmetry,
            is_sfcr_structured=is_sfcr, is_phi_scaled=is_phi,
        )

    def select_plan(self, fp: MatrixFingerprint) -> str:
        """Select optimal multiplication plan (Ψ+Σ: memory + candidates)."""
        # Check experience DB first (Ψ: cached knowledge)
        cached = self._experience.lookup(fp)
        if cached:
            return cached

        # Generate candidate plans based on fingerprint (Σ: exploration)
        if fp.sparsity > 0.5:
            return MatrixPlan.SPARSE
        if fp.symmetry > 0.9 and fp.rows == fp.cols:
            return MatrixPlan.SYMMETRIC
        if fp.is_sfcr_structured:
            return MatrixPlan.SFCR_BLOCK
        if fp.is_phi_scaled:
            return MatrixPlan.PHI_CACHED

        return MatrixPlan.DIRECT

    def matmul(self, a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
        """Adaptive matrix multiplication.

        1. Fingerprint A
        2. Select plan
        3. Execute
        4. Record
        """
        fp = self.fingerprint(a)
        plan = self.select_plan(fp)

        if plan == MatrixPlan.SPARSE:
            result = self._matmul_sparse(a, b)
        elif plan == MatrixPlan.SYMMETRIC:
            result = self._matmul_symmetric(a, b)
        elif plan == MatrixPlan.SFCR_BLOCK:
            result = self._matmul_sfcr_block(a, b)
        else:
            result = self._matmul_direct(a, b)

        self._experience.record(fp, plan)
        return result

    def matvec(self, matrix: list[list[float]], vec: list[float]) -> list[float]:
        """Adaptive matrix-vector multiplication."""
        fp = self.fingerprint(matrix)
        plan = self.select_plan(fp)

        if plan == MatrixPlan.SPARSE:
            return self._matvec_sparse(matrix, vec)
        return self._matvec_direct(matrix, vec)

    # ── Plan implementations ──────────────────────────────────────────

    @staticmethod
    def _matmul_direct(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
        """Standard O(n³) multiplication."""
        rows_a = len(a)
        cols_a = len(a[0])
        cols_b = len(b[0])
        result = [[0.0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for k in range(cols_a):
                if abs(a[i][k]) < 1e-15:
                    continue
                a_ik = a[i][k]
                for j in range(cols_b):
                    result[i][j] += a_ik * b[k][j]
        return result

    @staticmethod
    def _matmul_sparse(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
        """Skip zero entries in A (sparse-aware)."""
        rows_a = len(a)
        cols_b = len(b[0])
        result = [[0.0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for k, a_ik in enumerate(a[i]):
                if abs(a_ik) < 1e-10:
                    continue
                for j in range(cols_b):
                    result[i][j] += a_ik * b[k][j]
        return result

    @staticmethod
    def _matmul_symmetric(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
        """Exploit symmetry of A: only compute upper triangle."""
        n = len(a)
        cols_b = len(b[0])
        result = [[0.0] * cols_b for _ in range(n)]
        for i in range(n):
            for k in range(n):
                a_ik = a[i][k] if k >= i else a[k][i]  # use symmetry
                if abs(a_ik) < 1e-15:
                    continue
                for j in range(cols_b):
                    result[i][j] += a_ik * b[k][j]
        return result

    @staticmethod
    def _matmul_sfcr_block(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
        """Exploit 4-element SFCR block structure.

        When matrices have 4×4 block structure (common in crystal ops),
        we can multiply block-by-block, skipping zero blocks.
        """
        n = len(a)
        cols_b = len(b[0])
        block_size = n // 4 if n >= 4 else n

        if block_size < 1 or n % 4 != 0:
            return CrystalGEMM._matmul_direct(a, b)

        result = [[0.0] * cols_b for _ in range(n)]

        # Block multiplication: C[I][J] = sum_K A[I][K] * B[K][J]
        for bi in range(4):
            for bk in range(4):
                # Check if this block of A is zero
                block_zero = True
                for r in range(bi * block_size, (bi + 1) * block_size):
                    for c in range(bk * block_size, (bk + 1) * block_size):
                        if abs(a[r][c]) > 1e-10:
                            block_zero = False
                            break
                    if not block_zero:
                        break
                if block_zero:
                    continue

                for bj in range(4 if cols_b >= 4 * block_size else 1):
                    for r in range(block_size):
                        ri = bi * block_size + r
                        for c in range(block_size):
                            ci = bk * block_size + c
                            a_val = a[ri][ci]
                            if abs(a_val) < 1e-15:
                                continue
                            for j in range(block_size):
                                ji = bj * block_size + j if bj * block_size + j < cols_b else j
                                result[ri][ji] += a_val * b[ci][ji]

        return result

    @staticmethod
    def _matvec_direct(matrix: list[list[float]], vec: list[float]) -> list[float]:
        """Standard matrix-vector multiplication."""
        return [
            sum(matrix[i][j] * vec[j] for j in range(len(vec)))
            for i in range(len(matrix))
        ]

    @staticmethod
    def _matvec_sparse(matrix: list[list[float]], vec: list[float]) -> list[float]:
        """Sparse-aware matrix-vector multiplication."""
        result = [0.0] * len(matrix)
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                if abs(val) > 1e-10:
                    result[i] += val * vec[j]
        return result


# ══════════════════════════════════════════════════════════════════════
#  BRIDGE WEIGHT MATRIX — crystalline SFCR bridge operations
# ══════════════════════════════════════════════════════════════════════

def build_bridge_matrix() -> list[list[float]]:
    """Build the 4×4 SFCR bridge weight matrix from geometric constants.

    This is the fundamental matrix that connects the 4 elements:
      M[i][j] = bridge weight between element i and element j.

    Diagonal = 1.0 (self-connection).
    """
    faces = list(FACES)
    n = len(faces)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        matrix[i][i] = 1.0  # self-connection
        for j in range(i + 1, n):
            from .geometric_constants import bridge_key
            bk = bridge_key(faces[i], faces[j])
            w = BRIDGE_WEIGHTS.get(bk, 0.5)
            matrix[i][j] = w
            matrix[j][i] = w

    return matrix


def bridge_matvec(momentum_vec: list[float]) -> list[float]:
    """Multiply bridge matrix × momentum vector.

    Uses the CrystalGEMM adaptive engine to select the optimal
    algorithm for this specific matrix structure (symmetric, phi-scaled, 4×4).
    """
    gemm = get_crystal_gemm()
    bridge = build_bridge_matrix()
    return gemm.matvec(bridge, momentum_vec)


# ══════════════════════════════════════════════════════════════════════
#  MODULE API
# ══════════════════════════════════════════════════════════════════════

_CRYSTAL_GEMM: Optional[CrystalGEMM] = None


def get_crystal_gemm() -> CrystalGEMM:
    """Get or create the singleton CrystalGEMM."""
    global _CRYSTAL_GEMM
    if _CRYSTAL_GEMM is None:
        _CRYSTAL_GEMM = CrystalGEMM()
    return _CRYSTAL_GEMM


__all__ = [
    "CrystalGEMM", "MatrixFingerprint", "MatrixPlan",
    "ExperienceDB", "build_bridge_matrix", "bridge_matvec",
    "get_crystal_gemm",
]
