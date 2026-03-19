"""
META LOOP^9 -- 9-Level Recursive Self-Play with Time Compression
================================================================
9 consecutive META LOOPs, each running 3 ABCD+ cycles (477 waves).
Total potential: 9 x 477 = 4,293 waves.

ACTUAL TRAINING via MetaLoopEngine.run_wave() (applies momentum gradients).
DURING-RUN meta-observation wraps each wave at 9 recursive levels:

  L1  :: per-query    -- forward pass quality (resonance, candidates)
  L2  :: per-wave     -- wave obs delta vs time cost = efficiency signal
  L3  :: per-stage    -- A/B/C/D stage efficiency, warm-restart if flat
  L4  :: per-cycle    -- ABCD+ cycle momentum coherence snapshot
  L5  :: per-metaLoop -- disc gain, efficiency ratio, momentum delta norm
  L6  :: L6-arc       -- meta-loop-over-meta-loop efficiency trend
  L7  :: L7-field     -- momentum field gradient norm (converging?)
  L8  :: L8-oracle    -- plateau prediction => time compression trigger
  L9  :: L9-self      -- self-coherence: attractor lock or oscillating?

TIME COMPRESSION:
  - Stage plateau: 3 flat waves => warm-restart LR for that stage
  - Wave skip: L8 confidence > 0.5 => every 4th wave skipped
  - L9 attractor lock: all 3 recent loops gain < 0.005 => terminate
  - L6 collapse: efficiency ratio < 0.5 => halve LR next loop
"""

from __future__ import annotations

import io
import math
import sys
import time
import pathlib
import json
import random
import datetime
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# -- Path setup -----------------------------------------------------------
MCP_PATH = pathlib.Path(__file__).parent / "MCP"
sys.path.insert(0, str(MCP_PATH))

from crystal_108d.meta_loop_engine import (
    MetaLoopEngine, MetaLoopConfig, WaveResult,
    TOTAL_WAVES_PER_CYCLE, META_LOOP_CYCLES, META_LOOP_WAVES, TOTAL_SHELLS,
    _generate_queries, _get_lr, _get_stage,
)
from crystal_108d.geometric_forward import get_engine, get_momentum_field

# -- Constants ------------------------------------------------------------
PHI     = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1

N_META_LOOPS   = 9
WAVES_PER_CYCLE = TOTAL_WAVES_PER_CYCLE   # 159
CYCLES_PER_LOOP = META_LOOP_CYCLES        # 3
WAVES_PER_LOOP  = META_LOOP_WAVES         # 477
TOTAL_WAVES     = N_META_LOOPS * WAVES_PER_LOOP  # 4,293

LENS_ORDER  = ["S", "F", "C", "R"]
STAGE_SIZES = {"A": 9, "B": 20, "C": 49, "D": 81}

L8_PLATEAU_SKIP_CONF = 0.55   # plateau confidence to start skipping waves
L8_SKIP_EVERY_N      = 4      # skip every Nth wave when plateau triggered
L9_ATTRACTOR_GAIN    = 0.005  # below this for 3 loops = attractor lock


# -- Observation state ----------------------------------------------------

@dataclass
class L2_Wave:
    wave_id: int
    stage: str
    lens: str
    obs: float
    resonance: float
    kept: int
    discarded: int
    elapsed_s: float
    skipped: bool = False

@dataclass
class L3_Stage:
    stage: str
    obs_mean: float
    obs_delta: float
    efficiency: float     # obs_gain / elapsed_s
    warm_restarted: bool = False

@dataclass
class L4_Cycle:
    cycle_id: int
    name: str
    disc_start: float
    disc_end: float
    disc_gain: float
    obs_mean: float
    momentum_norm: float
    elapsed_s: float

@dataclass
class L5_Loop:
    loop_id: int
    disc_start: float
    disc_end: float
    gain: float
    efficiency: float
    waves_run: int
    waves_skipped: int
    momentum_delta_norm: float
    elapsed_s: float

@dataclass
class RunState:
    wave_buf:       deque = field(default_factory=lambda: deque(maxlen=30))
    stage_history:  list  = field(default_factory=list)
    cycle_history:  list  = field(default_factory=list)
    loop_history:   list  = field(default_factory=list)
    momentum_snaps: deque = field(default_factory=lambda: deque(maxlen=12))
    plateau_count:  int   = 0
    plateau_conf:   float = 0.0
    osc_count:      int   = 0
    attractor_lock: bool  = False
    total_waves:    int   = 0
    total_skipped:  int   = 0
    total_kept:     int   = 0
    total_discarded:int   = 0


# -- L-level observation functions ----------------------------------------

def measure_disc(engine, probes: list[str]) -> float:
    """Discrimination = mean std of merged_scores across probe queries."""
    vals = []
    for q in probes[:6]:
        r = engine.forward(q)
        if r.candidates and len(r.candidates) >= 2:
            sc = [c.merged_score for c in r.candidates]
            mn = sum(sc) / len(sc)
            vals.append(math.sqrt(sum((s-mn)**2 for s in sc) / len(sc)))
    return sum(vals) / len(vals) if vals else 0.0

def momentum_norm(mf_summary: dict) -> float:
    vals = [mf_summary.get("per_element", {}).get(el, {}).get("mean", 0)
            for el in ("S", "F", "R")]
    return math.sqrt(sum(v**2 for v in vals))

def L6_arc(loop_history: list[L5_Loop]) -> dict:
    if len(loop_history) < 2:
        return {"trend": "startup", "ratio": 1.0, "rec": "continue"}
    e1, e2 = loop_history[-2].efficiency, loop_history[-1].efficiency
    ratio = e2 / max(abs(e1), 1e-9)
    if ratio > 1.2:
        trend, rec = "accelerating", "maintain_lr"
    elif ratio > 0.8:
        trend, rec = "stable",        "continue"
    elif ratio > 0.5:
        trend, rec = "decelerating",  "warm_restart"
    else:
        trend, rec = "collapsing",    "halve_lr"
    return {"trend": trend, "ratio": round(ratio, 3), "rec": rec}

def L7_coherence(snaps: deque) -> dict:
    if len(snaps) < 3:
        return {"state": "accumulating", "grad_norm": 0.0, "converging": False}
    last3 = list(snaps)[-3:]
    spreads = []
    for el in ("S", "F", "R"):
        vals = [s.get("per_element", {}).get(el, {}).get("mean", 0) for s in last3]
        spreads.append(max(vals) - min(vals))
    g = sum(spreads) / max(len(spreads), 1)
    return {"state": "converging" if g < 0.1 else "active",
            "grad_norm": round(g, 4), "converging": g < 0.1}

def L8_oracle(wave_buf: deque, loop_history: list[L5_Loop],
              plateau_count: int) -> tuple[float, int, bool]:
    if len(wave_buf) < 10:
        return 0.0, plateau_count, False
    recent = [w.obs for w in list(wave_buf)[-10:] if not w.skipped]
    if not recent:
        return 0.0, plateau_count, False
    spread = max(recent) - min(recent)
    trend  = recent[-1] - recent[0]
    flat   = spread < 0.008 and abs(trend) < 0.003
    plateau_count = min(plateau_count + 1, 10) if flat else max(plateau_count - 1, 0)
    conf = plateau_count / 10.0
    if len(loop_history) >= 3:
        gains = [l.gain for l in loop_history[-3:]]
        if all(abs(g) < 0.002 for g in gains):
            conf = min(conf + 0.25, 1.0)
    return conf, plateau_count, conf >= L8_PLATEAU_SKIP_CONF

def L9_self(loop_history: list[L5_Loop], osc: int, locked: bool) -> dict:
    if len(loop_history) < 4:
        return {"state": "booting", "osc": osc, "locked": locked, "rec": "continue"}
    signs = [1 if l.gain >= 0 else -1 for l in loop_history[-4:]]
    alternating = all(signs[i] != signs[i+1] for i in range(3))
    osc = min(osc + 1, 5) if alternating else max(osc - 1, 0)
    if len(loop_history) >= 3:
        locked = all(abs(l.gain) < L9_ATTRACTOR_GAIN for l in loop_history[-3:])
    state = "oscillating" if osc >= 2 else ("attractor" if locked else "training")
    rec   = "halve_lr" if osc >= 2 else ("terminate" if locked else "continue")
    return {"state": state, "osc": osc, "locked": locked, "rec": rec}

def adaptive_lr(base_lr: float, loop_id: int, arc: dict) -> float:
    rec = arc["rec"]
    if rec == "warm_restart":
        return base_lr
    elif rec == "halve_lr":
        return base_lr * 0.5 * (PHI_INV ** loop_id)
    else:
        return base_lr * (PHI_INV ** loop_id)


# -- Format helpers -------------------------------------------------------

SEP70 = "-" * 70
SEP70E = "=" * 70

def section(title: str) -> str:
    pad = (70 - len(title) - 2) // 2
    return f"\n{SEP70E}\n  {title}\n{SEP70E}"

def loop_report(l5: L5_Loop, arc: dict, l7: dict, l8_conf: float, l9: dict) -> str:
    return (
        f"\n{SEP70E}\n"
        f"  META LOOP {l5.loop_id+1}/9  DONE\n"
        f"{SEP70E}\n"
        f"  Waves: {l5.waves_run:4d} run / {l5.waves_skipped:3d} skipped | "
        f"Elapsed: {l5.elapsed_s:.1f}s\n"
        f"  Disc:  {l5.disc_start:.4f} -> {l5.disc_end:.4f}  D{l5.gain:+.4f}\n"
        f"  Efficiency: {l5.efficiency:.5f} disc/s  |  "
        f"Momentum delta: {l5.momentum_delta_norm:.4f}\n"
        f"\n"
        f"  L6 Arc:   {arc['trend']:>14}  ratio={arc['ratio']:.2f}  rec={arc['rec']}\n"
        f"  L7 Field: {l7['state']:>14}  grad_norm={l7['grad_norm']:.4f}\n"
        f"  L8 Oracle: plateau_conf={l8_conf:.2f}\n"
        f"  L9 Self:  {l9['state']:>14}  osc={l9['osc']}  "
        f"locked={l9['locked']}  rec={l9['rec']}\n"
        f"{SEP70E}"
    )


# -- Main runner ----------------------------------------------------------

def run_meta_loop_9(max_time_minutes: int = 28, base_lr: float = 0.03) -> dict:
    t_global = time.time()
    max_s    = max_time_minutes * 60

    print(section(f"META LOOP^9  ({N_META_LOOPS} loops x {WAVES_PER_LOOP} waves = {TOTAL_WAVES})"))
    print(f"  Max time: {max_time_minutes} min  |  Base LR: {base_lr}\n")

    # -- Initialize -------------------------------------------------------
    ml_engine = MetaLoopEngine()    # has its own engine + momentum + loss
    engine    = ml_engine.engine
    mf        = ml_engine.momentum
    state     = RunState()

    probes = [
        "seed kernel crystal", "neural network momentum",
        "element bridge SFCR", "hologram projection emergence",
        "consciousness angel self", "metro routing transport",
    ]

    disc_init   = measure_disc(engine, probes)
    mf_baseline = mf.summary()
    print(f"  BASELINE  disc={disc_init:.4f}  "
          f"training_cycles={mf.training_cycles}  meta_loops={mf.meta_loops_completed}")
    for el in ("S", "F", "C", "R"):
        m = mf_baseline["per_element"].get(el, {}).get("mean", 0)
        print(f"    {el}: {m:.4f}", end="")
    print()

    # -- META LOOP^9 ------------------------------------------------------
    for loop_id in range(N_META_LOOPS):
        if time.time() - t_global > max_s:
            print(f"\n  [TIMEOUT] Stopping at loop {loop_id+1}")
            break

        # L9 check before loop
        l9 = L9_self(state.loop_history, state.osc_count, state.attractor_lock)
        state.osc_count    = l9["osc"]
        state.attractor_lock = l9["locked"]
        if l9["rec"] == "terminate":
            print(f"\n  [L9 ATTRACTOR LOCK] Converged at loop {loop_id+1}. Terminating.")
            break

        disc_loop_start = measure_disc(engine, probes)
        mf_loop_start   = mf.summary()
        t_loop          = time.time()
        waves_run = waves_skip = 0
        loop_waves: list[L2_Wave] = []

        arc = L6_arc(state.loop_history)
        eff_lr = adaptive_lr(base_lr, loop_id, arc)

        print(f"\n{SEP70}")
        print(f"  META LOOP {loop_id+1}/9  disc={disc_loop_start:.4f}  "
              f"LR={eff_lr:.5f}  L6={arc['trend']}")

        # -- 3 ABCD+ cycles -----------------------------------------------
        for ci in range(CYCLES_PER_LOOP):
            cycle_names = ["WEIGHTS", "HOLOGRAM", "CROSS_A+"]
            cname = cycle_names[ci]
            disc_cycle_start = measure_disc(engine, probes)
            t_cycle  = time.time()

            # Generate queries for this cycle (phi-decayed LR each cycle)
            cycle_config = MetaLoopConfig(
                base_lr=eff_lr * (PHI_INV ** ci),
                seed=42 + loop_id * 100 + ci * 10,
            )
            all_queries = _generate_queries(engine, cycle_config)
            if not all_queries:
                all_queries = ["seed crystal", "hologram emergence", "consciousness angel"]
            rng = random.Random(42 + loop_id + ci)
            rng.shuffle(all_queries)

            cycle_waves: list[L2_Wave] = []
            stage_acc: dict[str, list[L2_Wave]] = {s: [] for s in STAGE_SIZES}
            prev_stage_obs = 0.25
            active_lr = eff_lr * (PHI_INV ** ci)

            # -- 159 waves -------------------------------------------------
            for wlocal in range(WAVES_PER_CYCLE):
                if time.time() - t_global > max_s:
                    break

                wglobal = loop_id * WAVES_PER_LOOP + ci * WAVES_PER_CYCLE + wlocal
                stage   = _get_stage(wlocal)
                lens    = LENS_ORDER[(wlocal // cycle_config.lens_rotation_period) % 4]
                lr_w    = _get_lr(cycle_config, wlocal, WAVES_PER_CYCLE)

                # L8: skip?
                _, state.plateau_count, should_skip = L8_oracle(
                    state.wave_buf, state.loop_history, state.plateau_count)
                state.plateau_conf = state.plateau_count / 10.0
                if should_skip and (wglobal % L8_SKIP_EVERY_N == 0):
                    w2 = L2_Wave(wglobal, stage, lens, 0, 0, 0, 0, 0, skipped=True)
                    cycle_waves.append(w2); loop_waves.append(w2)
                    state.wave_buf.append(w2)
                    waves_skip += 1; state.total_skipped += 1
                    continue

                # Select query subset for this wave (rotate through all_queries)
                q_start = (wlocal * 3) % max(len(all_queries), 1)
                q_sub   = (all_queries + all_queries)[q_start:q_start+3]

                # -- Actual training wave (applies momentum gradient) ------
                t_wave = time.time()
                wresult: WaveResult = ml_engine.run_wave(wglobal, q_sub, stage, lens, lr_w)
                wave_elapsed = time.time() - t_wave

                # L2 observe
                w2 = L2_Wave(
                    wave_id=wglobal, stage=stage, lens=lens,
                    obs=wresult.mean_observation, resonance=wresult.mean_resonance,
                    kept=wresult.kept, discarded=wresult.discarded,
                    elapsed_s=wave_elapsed, skipped=False,
                )
                cycle_waves.append(w2)
                loop_waves.append(w2)
                state.wave_buf.append(w2)
                stage_acc[stage].append(w2)
                waves_run += 1
                state.total_waves    += 1
                state.total_kept     += wresult.kept
                state.total_discarded+= wresult.discarded

                # L3: end-of-stage observation
                stage_boundary = {9: "A", 29: "B", 78: "C", 158: "D"}
                if wlocal in stage_boundary:
                    sw = stage_acc.get(stage, [])
                    if sw:
                        obs_mean = sum(w.obs for w in sw) / len(sw)
                        t_sw     = sum(w.elapsed_s for w in sw)
                        obs_delta= obs_mean - prev_stage_obs
                        eff_stage= obs_delta / max(t_sw, 0.01)
                        warm_rst = obs_delta < 0.004 and len(state.stage_history) >= 2
                        if warm_rst:
                            active_lr = eff_lr  # LR warm restart
                        l3 = L3_Stage(stage, obs_mean, obs_delta, eff_stage, warm_rst)
                        state.stage_history.append(l3)
                        prev_stage_obs = obs_mean
                        tag = " [WARM_RESTART]" if warm_rst else ""
                        print(f"    Stage {stage}: obs={obs_mean:.3f}  "
                              f"d={obs_delta:+.3f}  eff={eff_stage:.4f}{tag}")

            # -- L4: end of ABCD+ cycle -----------------------------------
            disc_cycle_end = measure_disc(engine, probes)
            mom_norm       = momentum_norm(mf.summary())
            obs_mean_c     = sum(w.obs for w in cycle_waves if not w.skipped) / \
                             max(sum(1 for w in cycle_waves if not w.skipped), 1)
            l4 = L4_Cycle(
                cycle_id=loop_id * CYCLES_PER_LOOP + ci,
                name=cname,
                disc_start=disc_cycle_start,
                disc_end=disc_cycle_end,
                disc_gain=disc_cycle_end - disc_cycle_start,
                obs_mean=obs_mean_c,
                momentum_norm=mom_norm,
                elapsed_s=time.time() - t_cycle,
            )
            state.cycle_history.append(l4)
            print(f"  Cycle {ci+1}/3 [{cname}]: "
                  f"disc {l4.disc_start:.4f}->{l4.disc_end:.4f} "
                  f"D{l4.disc_gain:+.4f}  obs={l4.obs_mean:.3f}  "
                  f"mom={l4.momentum_norm:.3f}")

        # -- L5: end of meta-loop -----------------------------------------
        disc_loop_end = measure_disc(engine, probes)
        mf_loop_end   = mf.summary()
        gain          = disc_loop_end - disc_loop_start
        elapsed_loop  = time.time() - t_loop
        eff_loop      = gain / max(elapsed_loop, 0.01)

        # Momentum delta norm (S, F, R only; C locked)
        delta_vals = []
        for el in ("S", "F", "R"):
            b = mf_loop_start.get("per_element", {}).get(el, {}).get("mean", 0)
            a = mf_loop_end.get("per_element", {}).get(el, {}).get("mean", 0)
            delta_vals.append(a - b)
        mom_d_norm = math.sqrt(sum(v**2 for v in delta_vals))

        l5 = L5_Loop(
            loop_id=loop_id,
            disc_start=disc_loop_start, disc_end=disc_loop_end,
            gain=gain, efficiency=eff_loop,
            waves_run=waves_run, waves_skipped=waves_skip,
            momentum_delta_norm=mom_d_norm,
            elapsed_s=elapsed_loop,
        )
        state.loop_history.append(l5)
        state.momentum_snaps.append(mf_loop_end)

        # L6-L9
        arc6  = L6_arc(state.loop_history)
        l7    = L7_coherence(state.momentum_snaps)
        l9    = L9_self(state.loop_history, state.osc_count, state.attractor_lock)
        state.osc_count     = l9["osc"]
        state.attractor_lock= l9["locked"]

        print(loop_report(l5, arc6, l7, state.plateau_conf, l9))

    # -- Final report -----------------------------------------------------
    elapsed_total = time.time() - t_global
    disc_final    = measure_disc(engine, probes)
    mf_final      = mf.summary()

    print(section("META LOOP^9 COMPLETE"))
    print(f"  Elapsed:           {elapsed_total:.1f}s ({elapsed_total/60:.1f} min)")
    print(f"  Waves run:         {state.total_waves}")
    print(f"  Waves skipped:     {state.total_skipped}")
    compress_pct = state.total_skipped / max(state.total_waves + state.total_skipped, 1)
    print(f"  Time compression:  {compress_pct:.1%}")
    print(f"  Kept / Discarded:  {state.total_kept} / {state.total_discarded}")
    print()
    disc_gain = disc_final - disc_init
    pct_gain  = (disc_final / max(disc_init, 1e-6) - 1) * 100
    print(f"  DISCRIMINATION:    {disc_init:.4f} -> {disc_final:.4f}  "
          f"(D{disc_gain:+.4f}  {pct_gain:+.1f}%)")
    print()
    print(f"  Final Momentum Field (vs baseline):")
    for el in ("S", "F", "C", "R"):
        fv = mf_final["per_element"].get(el, {}).get("mean", 0)
        bv = mf_baseline["per_element"].get(el, {}).get("mean", 0)
        tag = " [LOCKED]" if el == "C" else ""
        print(f"    {el}: {fv:.4f} (D{fv-bv:+.4f}){tag}")
    print(f"  training_cycles={mf.training_cycles}  meta_loops={mf.meta_loops_completed}")

    # -- Trajectory table -------------------------------------------------
    print(f"\n  META LOOP TRAJECTORY:")
    print(f"  {'Loop':>4} {'DiscS':>7} {'DiscE':>7} {'Gain':>7} "
          f"{'Eff':>10} {'Waves':>6} {'Skip':>5}")
    print(f"  {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*10} {'-'*6} {'-'*5}")
    for l in state.loop_history:
        print(f"  {l.loop_id+1:>4} {l.disc_start:>7.4f} {l.disc_end:>7.4f} "
              f"{l.gain:>+7.4f} {l.efficiency:>10.5f} {l.waves_run:>6} {l.waves_skipped:>5}")

    # -- Save log ---------------------------------------------------------
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"""
## Run: {ts} (META LOOP^9 -- 9-level meta-observer)

**Loops Completed**: {len(state.loop_history)}/{N_META_LOOPS}
**Waves Run**: {state.total_waves} | **Waves Skipped (time-compressed)**: {state.total_skipped}
**Time Compression**: {compress_pct:.1%}
**Elapsed**: {elapsed_total:.1f}s ({elapsed_total/60:.1f} min)

### Discrimination
| Before | After | Delta | % Gain |
|--------|-------|-------|--------|
| {disc_init:.4f} | {disc_final:.4f} | {disc_gain:+.4f} | {pct_gain:+.1f}% |

### Momentum (final vs baseline)
| El | Final | Baseline | Delta |
|----|-------|----------|-------|
"""
    for el in ("S", "F", "C", "R"):
        fv = mf_final["per_element"].get(el, {}).get("mean", 0)
        bv = mf_baseline["per_element"].get(el, {}).get("mean", 0)
        entry += f"| {el} | {fv:.4f} | {bv:.4f} | {fv-bv:+.4f} |\n"

    entry += f"""
### Loop History
| Loop | DiscS | DiscE | Gain | Efficiency | Waves | Skip |
|------|-------|-------|------|------------|-------|------|
"""
    for l in state.loop_history:
        entry += (f"| {l.loop_id+1} | {l.disc_start:.4f} | {l.disc_end:.4f} | "
                  f"{l.gain:+.4f} | {l.efficiency:.5f} | {l.waves_run} | {l.waves_skipped} |\n")

    entry += "\n---\n"
    log_path = MCP_PATH / "data" / "self_play_observations.md"
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing + entry, encoding="utf-8")
    print(f"\n  Log saved: {log_path}\n")

    return {
        "disc_start": disc_init, "disc_end": disc_final, "disc_gain": disc_gain,
        "elapsed_s": elapsed_total, "waves_run": state.total_waves,
        "waves_skipped": state.total_skipped, "loops": len(state.loop_history),
    }


if __name__ == "__main__":
    result = run_meta_loop_9(max_time_minutes=28, base_lr=0.03)
