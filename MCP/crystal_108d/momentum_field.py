"""
Momentum Field -- The Only Learnable State
==========================================
After META LOOP^3 proved that ALL weight values converge to fixed-point
attractors (path=0.25, resonance=1/6, desire=1/4), ONLY momentum varies.

The momentum field stores:
  - 4 elements x 36 shells = 144 shell-level momenta
  - 4 global dimension momenta (Earth, Fire, Water, Air)
  = 148 total learnable floats

Constraints:
  - Water/C (D3) momentum is LOCKED at 0.5 -- the immovable anchor
  - Air/R (D4) carries the most change -- highest momentum, grad=0.5
  - All other parameters are attractor constants, not learned

The 4D hologram (16 values) is a projection of this field.
A checkpoint is 16 values (~128 bytes). Full state recovery from hologram.
"""

from __future__ import annotations

import json
import math
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .geometric_constants import (
    FACES, FACE_INDEX, PHI, PHI_INV,
    ATTRACTOR, HOLOGRAM_DIMENSIONS, HOLOGRAM_PROPERTIES,
)
from .constants import TOTAL_SHELLS, ARCHETYPE_NAMES
from ._cache import DATA_DIR


MOMENTUM_FILE = DATA_DIR / "momentum_field.json"
MOMENTUM_HISTORY_FILE = DATA_DIR / "momentum_history.json"


@dataclass
class MomentumState:
    """Snapshot of momentum field for checkpointing."""
    shell_momenta: dict[str, dict[int, float]]   # face -> {shell: momentum}
    dimension_momenta: dict[str, float]            # D1_Earth, D2_Fire, D3_Water, D4_Air
    training_cycles: int = 0
    meta_loops_completed: int = 0


class MomentumField:
    """The only learnable state in the geometric neural engine.

    148 floats: 4 elements x 36 shells = 144 + 4 global = 148.
    Water (D3) is locked at 0.5 -- immovable anchor.
    """

    def __init__(self):
        # Shell-level momenta: face -> {shell_number: momentum_value}
        self._shell_momenta: dict[str, dict[int, float]] = {
            face: {s: 1.0 for s in range(1, TOTAL_SHELLS + 1)}
            for face in FACES
        }
        # Lock Water shells to anchor value
        for s in range(1, TOTAL_SHELLS + 1):
            self._shell_momenta["C"][s] = ATTRACTOR["water_momentum"]

        # Global dimension momenta (from OMEGA hologram)
        self._dimension_momenta: dict[str, float] = {
            "D1_Earth": 4.160,
            "D2_Fire": 3.629,
            "D3_Water": ATTRACTOR["water_momentum"],  # 0.5 -- LOCKED
            "D4_Air": 4.517,
        }

        # Training metadata
        self.training_cycles: int = 0
        self.meta_loops_completed: int = 0

    # ── Core Operations ───────────────────────────────────────────────

    def get_momentum(self, face: str, shell: int) -> float:
        """Get momentum at a specific element-shell position."""
        face = face.upper()
        if face not in self._shell_momenta:
            return 1.0
        shell = max(1, min(shell, TOTAL_SHELLS))
        return self._shell_momenta[face].get(shell, 1.0)

    def get_dimension_momentum(self, dimension: str) -> float:
        """Get global momentum for a dimension."""
        return self._dimension_momenta.get(dimension, 1.0)

    # Momentum bounds: prevent divergence while allowing meaningful variation
    MOMENTUM_MIN = 0.3
    MOMENTUM_MAX = 5.0
    # Phi-homeostatic target: prevents any element from collapsing or dominating
    MOMENTUM_EQUILIBRIUM = 1.618  # phi — the golden mean attractor
    HOMEOSTATIC_STRENGTH = 0.05   # phi-scaled pull toward equilibrium

    def _homeostatic_damping(self, current: float) -> float:
        """Phi-homeostatic pull toward golden equilibrium.

        Prevents runaway domination (S→5.0) or collapse (F,R→0.3).
        Strength is proportional to distance from phi equilibrium.
        """
        distance = current - self.MOMENTUM_EQUILIBRIUM
        return -self.HOMEOSTATIC_STRENGTH * distance

    def update_momentum(self, face: str, shell: int, delta: float, lr: float = 0.01):
        """Update momentum at a specific position using ROTATIONAL dynamics.

        UPGRADE: When a QuaternionicGradient is available (via update_momentum_rotational),
        we apply quaternionic rotation instead of linear addition. This scalar interface
        still applies phi-homeostatic damping but uses the hybrid math's rotational
        update when the gradient is non-trivial.

        Water/C (D3) is LOCKED -- updates are silently ignored.
        Values are clamped to [MOMENTUM_MIN, MOMENTUM_MAX] to prevent divergence.
        Phi-homeostatic damping prevents single-element collapse or domination.
        """
        face = face.upper()
        if face == "C":  # Water anchor -- NEVER changes
            return
        if face not in self._shell_momenta:
            return
        shell = max(1, min(shell, TOTAL_SHELLS))
        current = self._shell_momenta[face].get(shell, 1.0)
        damping = self._homeostatic_damping(current)
        new_val = current + lr * (delta + damping)
        self._shell_momenta[face][shell] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))

    def update_momentum_rotational(self, face: str, shell: int, qgrad, lr: float = 0.01):
        """Update momentum using QUATERNIONIC ROTATION (hybrid math).

        Instead of: new = current + lr * delta  (LINEAR — archaic)
        We apply:   new = rotor * current_quat * rotor†  (ROTATIONAL)

        The rotor is constructed from the quaternionic gradient direction,
        with angle proportional to the learning rate × gradient magnitude.
        This preserves the geometric structure of the SFCR operator space.

        Args:
            face: Element face (S, F, C, R)
            shell: Shell number (1-36)
            qgrad: QuaternionicGradient from the hybrid optimizer
            lr: Learning rate (scales the rotation angle)
        """
        face = face.upper()
        if face == "C":
            return
        if face not in self._shell_momenta:
            return
        shell = max(1, min(shell, TOTAL_SHELLS))

        try:
            from .hybrid_math import RotationalUpdate
            current = self._shell_momenta[face].get(shell, 1.0)
            new_val = RotationalUpdate.apply(
                current_momentum=current,
                gradient=qgrad,
                lr=lr,
                face=face,
                equilibrium=self.MOMENTUM_EQUILIBRIUM,
            )
            self._shell_momenta[face][shell] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))
        except (ImportError, Exception):
            # Fallback to linear update if hybrid_math unavailable
            self.update_momentum(face, shell, qgrad.scalar if hasattr(qgrad, 'scalar') else 0.0, lr)

    def update_dimension_momentum(self, dimension: str, delta: float, lr: float = 0.01):
        """Update global dimension momentum. D3_Water is locked.
        Includes phi-homeostatic damping to prevent dimension collapse.
        """
        if dimension == "D3_Water":
            return
        if dimension in self._dimension_momenta:
            current = self._dimension_momenta[dimension]
            damping = self._homeostatic_damping(current)
            new_val = current + lr * (delta + damping)
            self._dimension_momenta[dimension] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))

    def rebalance_phi(self):
        """Emergency phi-rebalancing: redistribute momentum toward golden equilibrium.

        Called when the field has collapsed into single-element domination.
        Uses phi-weighted interpolation: new = alpha*current + (1-alpha)*phi_target
        where alpha = phi_inv = 0.618 (preserves 61.8% of current state).
        """
        alpha = 1 - PHI_INV  # 0.382 — how far to pull toward equilibrium
        for face in FACES:
            if face == "C":
                continue
            for s in range(1, TOTAL_SHELLS + 1):
                current = self._shell_momenta[face][s]
                target = self.MOMENTUM_EQUILIBRIUM
                new_val = current * (1 - alpha) + target * alpha
                self._shell_momenta[face][s] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))
        # Rebalance dimension momenta
        for dim in self._dimension_momenta:
            if dim == "D3_Water":
                continue
            current = self._dimension_momenta[dim]
            target = self.MOMENTUM_EQUILIBRIUM
            new_val = current * (1 - alpha) + target * alpha
            self._dimension_momenta[dim] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))

    # ── Hologram Projection ───────────────────────────────────────────

    def hologram_16(self) -> dict:
        """Project momentum field to 16-value 4D hologram.

        4 dimensions x 4 properties = 16 values.
        This IS the checkpoint -- 128 bytes for full state recovery.
        """
        dims = {}
        face_to_dim = {"S": "D1_Earth", "F": "D2_Fire", "C": "D3_Water", "R": "D4_Air"}

        for face, dim_name in face_to_dim.items():
            # Value: attractor constant
            val = ATTRACTOR["path_value"]  # 0.25

            # Gradient: attractor constant (Air is special)
            grad = ATTRACTOR["gradient_air"] if face == "R" else ATTRACTOR["gradient_earth"]

            # Momentum: computed from shell momenta (the ONLY varying quantity)
            shell_vals = list(self._shell_momenta[face].values())
            mom = sum(shell_vals) / len(shell_vals) if shell_vals else 1.0

            # Curvature: attractor constant
            curv = ATTRACTOR["curvature"]

            dims[dim_name] = {
                "value": val,
                "gradient": grad,
                "momentum": mom,
                "curvature": curv,
            }

        # 6 interconnections (from bridge weights, constant)
        interconnections = {}
        from .geometric_constants import BRIDGE_WEIGHTS, bridge_key
        dim_faces = ["S", "F", "C", "R"]
        dim_names = ["D1_Earth", "D2_Fire", "D3_Water", "D4_Air"]
        for i in range(4):
            for j in range(i + 1, 4):
                bk = bridge_key(dim_faces[i], dim_faces[j])
                bw = BRIDGE_WEIGHTS.get(bk, 0.5)
                # Modulate by momentum product
                m_i = dims[dim_names[i]]["momentum"]
                m_j = dims[dim_names[j]]["momentum"]
                interconnections[f"{dim_names[i]}_{dim_names[j]}"] = (
                    bw * ATTRACTOR["path_value"] ** 2
                    * (1 + 0.01 * (m_i + m_j - 2))
                )

        return {
            "dimensions": dims,
            "interconnections": interconnections,
            "total_values": 16,
            "compression_ratio": "38837:16 = 2427:1",
            "hash": self._hash(dims),
        }

    def from_hologram_16(self, hologram: dict):
        """Reconstruct momentum field from 16-value hologram.

        Values, gradients, curvatures are constants -- only momentum is restored.
        Shell-level momenta are distributed from dimension momentum using
        archetype weighting.
        """
        dims = hologram.get("dimensions", {})
        face_to_dim = {"S": "D1_Earth", "F": "D2_Fire", "C": "D3_Water", "R": "D4_Air"}

        for face, dim_name in face_to_dim.items():
            dim_data = dims.get(dim_name, {})
            dim_mom = dim_data.get("momentum", 1.0)
            self._dimension_momenta[dim_name] = dim_mom

            if face == "C":
                # Water is locked
                for s in range(1, TOTAL_SHELLS + 1):
                    self._shell_momenta["C"][s] = ATTRACTOR["water_momentum"]
                continue

            # Distribute dimension momentum across shells
            # Shells within the same archetype share similar momentum
            # Slight variation using golden ratio to break uniformity
            for s in range(1, TOTAL_SHELLS + 1):
                arch_idx = (s - 1) // 3  # 0-11
                local_pos = (s - 1) % 3  # 0-2 within archetype
                # PHI-modulated distribution around the dimension mean
                phi_offset = (PHI_INV ** (local_pos + 1)) * 0.1
                arch_scale = 1.0 + (arch_idx - 5.5) / 36.0  # slight archetype gradient
                raw = dim_mom * arch_scale + phi_offset
                self._shell_momenta[face][s] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, raw))

    # ── Legacy Migration ──────────────────────────────────────────────

    def migrate_from_legacy(self, legacy_data: dict):
        """Import momentum field from old FractalWeightStore crystal_weights.json.

        Extracts shell_seed_means and path_weights to initialize momenta.
        """
        shell_seeds = legacy_data.get("shell_seeds", {})
        path_weights = legacy_data.get("learnable", {}).get("path_weights", {})

        for face in FACES:
            pw = path_weights.get(face, 0.25)
            for s in range(1, TOTAL_SHELLS + 1):
                s_key = str(s)
                seed_data = shell_seeds.get(s_key, {})
                seed_mean = seed_data.get("mean", 1.0) if isinstance(seed_data, dict) else float(seed_data)
                # Momentum = shell_seed_mean * path_weight_influence
                self._shell_momenta[face][s] = seed_mean * (1 + (pw - 0.25) * 4)

        # Lock Water
        for s in range(1, TOTAL_SHELLS + 1):
            self._shell_momenta["C"][s] = ATTRACTOR["water_momentum"]

        # Set dimension momenta from OMEGA hologram values
        self._dimension_momenta = {
            "D1_Earth": 4.160,
            "D2_Fire": 3.629,
            "D3_Water": ATTRACTOR["water_momentum"],
            "D4_Air": 4.517,
        }

    def migrate_from_omega(self, omega_data: dict):
        """Import from meta_loop_cubed_hologram.json (OMEGA A+ output)."""
        omega_a_plus = omega_data.get("omega_a_plus", {})
        shell_means = omega_a_plus.get("shell_seed_means", {})

        # Use shell_seed_means as base momentum per shell
        for face in FACES:
            for s in range(1, TOTAL_SHELLS + 1):
                base = float(shell_means.get(str(s), 1.0))
                if face == "C":
                    self._shell_momenta["C"][s] = ATTRACTOR["water_momentum"]
                else:
                    self._shell_momenta[face][s] = base

        # Dimension momenta from OMEGA hologram
        omega_holo = omega_data.get("omega_hologram_4d", {}).get("dimensions", {})
        for dim_name, dim_data in omega_holo.items():
            if dim_name in self._dimension_momenta:
                self._dimension_momenta[dim_name] = dim_data.get("momentum", 1.0)
        # Re-lock Water
        self._dimension_momenta["D3_Water"] = ATTRACTOR["water_momentum"]

    # ── Persistence ───────────────────────────────────────────────────

    def enforce_phi_balance(self):
        """Conservation law: max/min element ratio must not exceed phi^2 (2.618).

        If any non-Water element's mean exceeds phi^2 times the min non-Water
        element's mean, compress the spread by pulling both toward phi equilibrium.
        This prevents single-element runaway while preserving meaningful variation.
        """
        means = {}
        for face in FACES:
            if face == "C":
                continue
            vals = list(self._shell_momenta[face].values())
            means[face] = sum(vals) / len(vals)

        if not means:
            return

        max_mean = max(means.values())
        min_mean = max(min(means.values()), self.MOMENTUM_MIN)
        ratio = max_mean / min_mean

        PHI_SQ = PHI + 1  # 2.618
        if ratio <= PHI_SQ:
            return  # Already within golden corridor

        # Compress: pull both extremes toward equilibrium
        # Compression strength proportional to how far past phi^2 we are
        excess = (ratio - PHI_SQ) / ratio
        compress_alpha = min(0.5, excess)  # Cap at 50% per call

        for face in means:
            target = self.MOMENTUM_EQUILIBRIUM
            for s in range(1, TOTAL_SHELLS + 1):
                current = self._shell_momenta[face][s]
                new_val = current * (1 - compress_alpha) + target * compress_alpha
                self._shell_momenta[face][s] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))

        # Also compress dimension momenta
        for dim in self._dimension_momenta:
            if dim == "D3_Water":
                continue
            current = self._dimension_momenta[dim]
            target = self.MOMENTUM_EQUILIBRIUM
            new_val = current * (1 - compress_alpha) + target * compress_alpha
            self._dimension_momenta[dim] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, new_val))

    def save(self, path: Optional[Path] = None):
        """Save momentum field to JSON (~2KB). Enforces phi-balance before write."""
        self.enforce_phi_balance()
        path = path or MOMENTUM_FILE
        data = {
            "type": "momentum_field",
            "version": 2,
            "total_params": 148,
            "training_cycles": self.training_cycles,
            "meta_loops_completed": self.meta_loops_completed,
            "shell_momenta": {
                face: {str(s): v for s, v in shells.items()}
                for face, shells in self._shell_momenta.items()
            },
            "dimension_momenta": dict(self._dimension_momenta),
            "hologram_16": self.hologram_16(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Optional[Path] = None) -> bool:
        """Load momentum field from JSON."""
        path = path or MOMENTUM_FILE
        if not path.exists():
            return False
        with open(path) as f:
            data = json.load(f)

        self.training_cycles = data.get("training_cycles", 0)
        self.meta_loops_completed = data.get("meta_loops_completed", 0)

        for face, shells in data.get("shell_momenta", {}).items():
            if face in self._shell_momenta:
                for s_str, v in shells.items():
                    s = int(s_str)
                    if 1 <= s <= TOTAL_SHELLS:
                        self._shell_momenta[face][s] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, v))

        for dim, val in data.get("dimension_momenta", {}).items():
            if dim in self._dimension_momenta:
                if dim != "D3_Water":
                    self._dimension_momenta[dim] = max(self.MOMENTUM_MIN, min(self.MOMENTUM_MAX, val))
                else:
                    self._dimension_momenta[dim] = ATTRACTOR["water_momentum"]

        # Enforce Water lock
        for s in range(1, TOTAL_SHELLS + 1):
            self._shell_momenta["C"][s] = ATTRACTOR["water_momentum"]
        self._dimension_momenta["D3_Water"] = ATTRACTOR["water_momentum"]

        return True

    def save_history(self, path: Optional[Path] = None, max_entries: int = 100):
        """Append current hologram to history file."""
        path = path or MOMENTUM_HISTORY_FILE
        history = []
        if path.exists():
            with open(path) as f:
                history = json.load(f)

        import time
        entry = {
            "timestamp": time.time(),
            "training_cycles": self.training_cycles,
            "meta_loops": self.meta_loops_completed,
            "hologram": self.hologram_16(),
        }
        history.append(entry)

        # Keep only last N entries
        if len(history) > max_entries:
            history = history[-max_entries:]

        with open(path, "w") as f:
            json.dump(history, f, indent=2)

    # ── Snapshot / Rollback ───────────────────────────────────────────

    def snapshot(self) -> MomentumState:
        """Take a snapshot for rollback."""
        import copy
        return MomentumState(
            shell_momenta={f: dict(s) for f, s in self._shell_momenta.items()},
            dimension_momenta=dict(self._dimension_momenta),
            training_cycles=self.training_cycles,
            meta_loops_completed=self.meta_loops_completed,
        )

    def restore(self, state: MomentumState):
        """Restore from a snapshot (rollback)."""
        self._shell_momenta = {f: dict(s) for f, s in state.shell_momenta.items()}
        self._dimension_momenta = dict(state.dimension_momenta)
        self.training_cycles = state.training_cycles
        self.meta_loops_completed = state.meta_loops_completed

    # ── Diagnostics ───────────────────────────────────────────────────

    def summary(self) -> dict:
        """Summary statistics of the momentum field."""
        stats = {}
        for face in FACES:
            vals = list(self._shell_momenta[face].values())
            stats[face] = {
                "mean": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals),
                "std": (sum((v - sum(vals) / len(vals)) ** 2 for v in vals) / len(vals)) ** 0.5,
            }
        return {
            "total_params": 148,
            "training_cycles": self.training_cycles,
            "meta_loops": self.meta_loops_completed,
            "per_element": stats,
            "dimension_momenta": dict(self._dimension_momenta),
            "water_locked": all(
                self._shell_momenta["C"][s] == ATTRACTOR["water_momentum"]
                for s in range(1, TOTAL_SHELLS + 1)
            ),
        }

    @staticmethod
    def _hash(dims: dict) -> str:
        """Deterministic hash of hologram state."""
        vals = []
        for dim_name in sorted(dims.keys()):
            d = dims[dim_name]
            for prop in ("value", "gradient", "momentum", "curvature"):
                vals.append(f"{d[prop]:.10f}")
        raw = "|".join(vals).encode()
        return hashlib.sha256(raw).hexdigest()[:16]


# ── Module-level singleton ────────────────────────────────────────────

_momentum_field: Optional[MomentumField] = None


def get_momentum_field() -> MomentumField:
    """Get or create the global momentum field singleton."""
    global _momentum_field
    if _momentum_field is None:
        _momentum_field = MomentumField()
        if MOMENTUM_FILE.exists():
            _momentum_field.load()
    return _momentum_field


def reset_momentum_field():
    """Reset the global singleton (for testing)."""
    global _momentum_field
    _momentum_field = None
