"""
Export chart data from the four phase modules to plain JSON for the website.

Imports (read-only) the phase modules and dumps arrays of plain floats/ints to

    math-verification-web/src/data/ym-data.json

for use by the website chart components:

  Phase 2  proof/cluster_expansion.py  KP convergence scan, beta_0^rig,
           polymer size histogram
  Phase 3  proof/rg_flow.py            exact RG trajectory + mass gap
  Phase 4  proof/su3_complete.py       SU(3) mass gap log 3 + irrep dims
  Phase 5  proof/os_axioms.py          OS correlator, OS3 form z-scores,
           mean plaquette (MC, seed 20261018, equil 500, meas 3000)

Values computed inline in the modules' verification mains (beta_0 bisection,
the RG demo trajectory, the OS3 per-form z-scores, the OS4 correlator) are
replicated here by CALLING the modules' public functions; no module is edited.

Run:  python scripts/export_visual_data.py     (MC takes about 2 minutes)
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "proof"))

import cluster_expansion as phase2  # noqa: E402
import rg_flow as phase3            # noqa: E402
import su3_complete as phase4       # noqa: E402
import os_axioms as phase5          # noqa: E402

OUT_PATH = os.path.join(REPO, "math-verification-web", "src", "data",
                        "ym-data.json")

# --- tuning constants (match the modules' verification mains) --------------
POLYMER_SIZE = 6        # max polymer size in run_cluster_verification / __main__
KP_POINTS = 80          # kpScan grid resolution
KP_BETA_MAX = 0.03      # kpScan grid upper end
TRAJ_START = 0.5        # RG demo start coupling (rg_flow.run_rg_verification RG4)
TRAJ_MIN = 1e-6         # flow stops once beta drops below this
TRAJ_CAP = 30           # max number of RG steps
SEED = 20261018         # os_axioms.run_os_verification default seed
N_EQUIL = 500
N_MEAS = 3000
BETAS = (1.0, 2.0)

LOG2 = math.log(2.0)


def build_phase2() -> dict:
    """KP convergence scan, rigorous beta_0, polymer size histogram."""
    print("[phase 2] enumerating closed polymers up to size "
          f"{POLYMER_SIZE} ...", flush=True)
    counter, elapsed = phase2.enumerate_polymers(POLYMER_SIZE)
    beta0, fval = phase2.find_beta0(counter, POLYMER_SIZE)
    print(f"[phase 2] {sum(counter.values())} polymers in {elapsed:.1f}s; "
          f"beta0rig = {beta0:.10f} (A + tail = {fval:.6f})")

    hist: dict[int, int] = {}
    for (n, _w), cnt in counter.items():
        hist[n] = hist.get(n, 0) + int(cnt)

    grid = np.linspace(0.0, KP_BETA_MAX, KP_POINTS)
    kp_beta: list[float] = []
    kp_vals: list[float | None] = []
    gap_beta: list[float] = []
    gap_vals: list[float] = []
    for b in grid:
        beta = float(b)
        if beta == 0.0:
            # r_fund(0) is 0/0; by continuity A = 0 and tail = 0 at beta = 0.
            a_sum, tail = 0.0, 0.0
        else:
            _, a_sum = phase2.kp_sums(counter, beta, POLYMER_SIZE)
            tail = phase2.tail_bound(beta, POLYMER_SIZE)
        total = a_sum + tail
        kp_beta.append(beta)
        # tail is +inf once x = e(D-1) 5^(2/3) r >= 1 (beyond the
        # strong-coupling region): the bound is vacuous there, charted as null.
        kp_vals.append(total if math.isfinite(total) else None)
        if 0.0 < total < 1.0:
            gap_beta.append(beta)
            gap_vals.append(-math.log(total))   # KP bound Delta >= -log(A+tail)

    return {
        "beta0rig": float(beta0),
        "N": int(POLYMER_SIZE),
        "kpScan": {"beta": kp_beta, "kp": kp_vals},
        "gapBound": {"beta": gap_beta, "gap": gap_vals},
        "polymerSizes": {"size": sorted(int(s) for s in hist),
                         "count": [hist[s] for s in sorted(hist)]},
    }


def build_phase3() -> dict:
    """Exact RG trajectory from the module's demo start down to beta < 1e-6."""
    beta = TRAJ_START
    betas = [beta]
    steps = list(range(TRAJ_CAP + 1))
    while betas[-1] >= TRAJ_MIN and len(betas) < len(steps):
        beta = phase3.beta_prime(beta)
        betas.append(beta)
    gaps = [float(phase3.mass_gap(b)) for b in betas]
    print(f"[phase 3] trajectory: {len(betas)} steps, "
          f"beta {betas[0]:.6e} -> {betas[-1]:.6e}, "
          f"gap {gaps[0]:.6f} -> {gaps[-1]:.6f}")
    return {
        "trajectory": {"step": [int(i) for i in range(len(betas))],
                       "beta": [float(b) for b in betas],
                       "gap": gaps},
    }


def build_phase4() -> dict:
    """SU(3) mass gap and the irrep dimensions checked by the module."""
    gap = float(phase4.su3_mass_gap_beta_zero())
    # The reps verified in su3_complete.run_su3_verification ("[1/7] Dimensions").
    reps_known = [((0, 0), 1), ((1, 0), 3), ((0, 1), 3), ((2, 0), 6),
                  ((0, 2), 6), ((1, 1), 8), ((3, 0), 10), ((0, 3), 10),
                  ((2, 1), 15), ((1, 2), 15), ((4, 0), 15), ((3, 1), 24),
                  ((2, 2), 27)]
    dims = []
    for (p, q), expected in reps_known:
        d = int(phase4.su3_dim(p, q))
        if d != expected:
            raise AssertionError(f"su3_dim({p},{q}) = {d} != {expected}")
        dims.append(d)
    print(f"[phase 4] gapSU3 = {gap!r}, {len(dims)} irrep dims")
    return {"gapSU3": gap, "dims": dims}


def os3_form_zscores(res: dict) -> list[float]:
    """The 35 OS3 quadratic-form z-scores exactly as run_os_verification.

    Same form set and same order: coherent, 3 orientation unit vectors,
    mean-diagonal, then 30 random unit vectors from default_rng(seed + 7)
    (re-seeded per beta, so both betas use the same random forms).
    Sign convention: positive z = positive (reflection-positive) form.
    """
    m = res["M"]
    w = res["W"]                                   # (n, T, 6)
    cross = w[:, 1, :, None] * w[:, 2, None, :]    # (n, 6, 6)
    cross_sym = 0.5 * (cross + np.transpose(cross, (0, 2, 1)))

    def qstats(v: np.ndarray) -> tuple[float, float]:
        q = cross_sym @ v                          # (n, 6)
        val = float(np.mean(q @ v))
        se = float(phase5.binned_se(q @ v))
        return val, se

    forms: dict[str, np.ndarray] = {}
    eye = np.eye(6)
    forms["coherent"] = np.ones(6) / np.sqrt(6)
    for i in range(3):
        forms[f"orientation-{i}"] = eye[i]
    forms["mean-diagonal"] = eye[int(np.argmax(np.diag(m)))]
    rng_f = np.random.default_rng(SEED + 7)
    for i in range(30):
        v = rng_f.normal(size=6)
        forms[f"random-{i}"] = v / np.linalg.norm(v)

    zvals: list[float] = []
    for name, v in forms.items():
        val, se = qstats(v)
        if se <= 0.0:
            raise RuntimeError(f"non-positive standard error for form {name}")
        z = float(val / se)
        if not math.isfinite(z):
            raise RuntimeError(f"non-finite z for form {name}")
        zvals.append(z)
    if len(zvals) != 35:
        raise AssertionError(f"expected 35 OS forms, got {len(zvals)}")
    return zvals


def os4_correlator(w: np.ndarray) -> tuple[list[float], list[float]]:
    """Translation-averaged connected correlator C(t), t = 0..3, and its
    binned SE, normalized exactly as run_os_verification's OS4 check:
    dw = W - <W> per time slice, C(t) = <num_t> / <den>, with
    num_t = mean over measurements and operators of dw_i(s) dw_i(s+t)
    (time average over all 4 origins, periodic wrap)."""
    dw = w - w.mean(axis=0, keepdims=True)
    num_s = [np.mean(np.sum(dw * np.roll(dw, -t, axis=1), axis=-1), axis=1)
             for t in range(phase5.NT)]            # each shape (n,)
    den_s = np.mean(np.sum(dw ** 2, axis=-1), axis=1)   # (n,)
    den_mean = float(np.mean(den_s))
    corr = [float(np.mean(nk)) / den_mean for nk in num_s]
    se = [float(phase5.binned_se(nk)) / den_mean for nk in num_s]
    return corr, se


def build_phase5() -> dict:
    """One matched MC run per beta (seed/equil/meas as run_os_verification),
    producing correlator, OS3 z-scores and mean plaquette from the SAME run."""
    rng = np.random.default_rng(SEED)
    # run_os_verification draws these Haar samples (OS1c) before the beta
    # loop; replaying them keeps the Monte Carlo stream identical to the
    # verified run.
    phase5.beta0_os_matrix_check(rng)

    betas = []
    corr = {"t": [int(t) for t in range(phase5.NT)]}
    osz = {}
    plaq: dict[str, float] = {}
    for beta in BETAS:
        tag = f"beta{beta:g}"
        print(f"[phase 5] MC at beta = {beta} (equil {N_EQUIL}, "
              f"meas {N_MEAS}) ...", flush=True)
        res = phase5.run_beta(beta, rng, N_EQUIL, N_MEAS)
        betas.append(float(beta))
        c, se = os4_correlator(res["W"])
        corr[f"beta{beta:g}"] = c
        corr[f"beta{beta:g}_se"] = se
        osz[f"beta{beta:g}"] = os3_form_zscores(res)
        plaq[f"beta{beta:g}"] = float(res["lat"].mean_plaquette())
        print(f"[phase 5] beta = {beta}: acc = {res['acc']:.3f}, "
              f"C = [{', '.join(f'{x:.4f}' for x in c)}], "
              f"plaq = {plaq[tag]:.4f}")

    return {"betas": betas, "corr": corr, "osz": osz, "plaquette": plaq}


# --------------------------------------------------------------------------
# Validation + summary
# --------------------------------------------------------------------------

def audit(node, path: str = "$") -> tuple[int, int, list[str]]:
    """Walk the structure: every number must be finite, no foreign types.
    Returns (n_numbers, n_nulls, issues)."""
    nums = nulls = 0
    issues: list[str] = []
    if isinstance(node, dict):
        for key, val in node.items():
            n, u, bad = audit(val, f"{path}.{key}")
            nums += n
            nulls += u
            issues += bad
    elif isinstance(node, list):
        for i, val in enumerate(node):
            n, u, bad = audit(val, f"{path}[{i}]")
            nums += n
            nulls += u
            issues += bad
    elif node is None:
        nulls += 1
    elif isinstance(node, bool):
        issues.append(f"{path}: unexpected bool")
    elif isinstance(node, str):
        pass                              # informational strings (e.g. generated)
    elif isinstance(node, (int, float)):
        nums += 1
        if not math.isfinite(float(node)):
            issues.append(f"{path}: non-finite {node!r}")
    else:
        issues.append(f"{path}: unexpected type {type(node).__name__}")
    return nums, nulls, issues


def main() -> int:
    data = {
        "generated": date.today().isoformat(),
        "phase2": build_phase2(),
        "phase3": build_phase3(),
        "phase4": build_phase4(),
        "phase5": build_phase5(),
    }

    # --- validate: strict serialization (allow_nan=False rejects inf/nan),
    #     JSON round-trip, and a full finite-number audit ---
    blob = json.dumps(data, allow_nan=False, indent=2)
    roundtrip = json.loads(blob)
    if roundtrip != data:
        raise AssertionError("JSON round-trip changed the data")
    nums, nulls, issues = audit(data)
    if issues:
        raise AssertionError("invalid values: " + "; ".join(issues[:5]))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(blob)
        fh.write("\n")
    size = os.path.getsize(OUT_PATH)

    # --- summary (ASCII only) ---
    p2, p3, p4, p5 = (data["phase2"], data["phase3"], data["phase4"],
                      data["phase5"])
    hist = ", ".join(f"size {s}: {c}"
                     for s, c in zip(p2["polymerSizes"]["size"],
                                     p2["polymerSizes"]["count"]))
    traj_beta = p3["trajectory"]["beta"]
    print()
    print("SUMMARY")
    print(f"  beta0rig            = {p2['beta0rig']:.10f}  (N = {p2['N']})")
    print(f"  polymers            = {sum(p2['polymerSizes']['count'])}  ({hist})")
    print(f"  kpScan              = {len(p2['kpScan']['beta'])} points, "
          f"{sum(1 for v in p2['kpScan']['kp'] if v is None)} null "
          f"(vacuous tail beyond beta0rig), "
          f"kp max finite = {max(v for v in p2['kpScan']['kp'] if v is not None):.6f}")
    print(f"  gapBound region     = {len(p2['gapBound']['beta'])} points, "
          f"beta {p2['gapBound']['beta'][0]:.6f} .. "
          f"{p2['gapBound']['beta'][-1]:.6f}, "
          f"gap {p2['gapBound']['gap'][0]:.6f} .. "
          f"{p2['gapBound']['gap'][-1]:.6f}")
    print(f"  trajectory          = {len(traj_beta)} steps from "
          f"{traj_beta[0]:.6e} to {traj_beta[-1]:.6e} "
          f"(gap {p3['trajectory']['gap'][0]:.6f} -> "
          f"{p3['trajectory']['gap'][-1]:.6f})")
    print(f"  gapSU3              = {p4['gapSU3']!r}")
    print(f"  su3 dims            = {p4['dims']}")
    for beta in p5["betas"]:
        tag = f"beta{beta:g}"
        c = p5["corr"][tag]
        se = p5["corr"][f"{tag}_se"]
        print(f"  corr {tag:<7}       = [" +
              ", ".join(f"{v:.6f}" for v in c) + "]")
        print(f"  corr {tag:<7} se    = [" +
              ", ".join(f"{v:.6f}" for v in se) + "]")
        z = p5["osz"][tag]
        print(f"  osz  {tag:<7}       = {len(z)} forms, "
              f"min {min(z):.3f}, max {max(z):.3f}")
        print(f"  plaq {tag:<7}       = {p5['plaquette'][tag]:.6f}")
    print(f"  numbers / nulls     = {nums} finite numbers, {nulls} nulls")
    print(f"  json file           = {OUT_PATH}")
    print(f"  json size           = {size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
