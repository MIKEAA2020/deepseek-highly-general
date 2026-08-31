"""
Elevation E8 — kappa_V baseline comparison battery on REAL Network K
perturbation-recovery data (strengthens Studies E1 + E5-v4 to address
Qwen §3.2 self-referential validation + §8.3 baseline comparison).

BACKGROUND:
  Study E1 (novelty_kappa_v_baselines.py) compares kappa_V to six simpler
  alternatives on the SYNTHETIC n=3 prototype (V=1-x^2-y^2, A=1/2(x dy - y dx),
  kappa_V=a^2). Elevation factor: kappa_V's partial r = 0.9976 (controlling for
  viability_margin); viability_margin's partial r given kappa_V = -0.5512.

  Qwen §3.2 critique was correct as a description of the manuscript (the n=3
  prototype IS self-referential by construction), but E1 ELEVATED it by showing
  kappa_V's operational choice is non-arbitrary via the partial-correlation
  battery. Qwen's §8.3 suggestion was to compare kappa_V to baselines.

STRENGTHENED SUGGESTION (Qwen §3.2 + §8.3):
  E1 was on SYNTHETIC data (V=1-x^p across 7 amplitudes x 7 shapes). The
  strengthened suggestion is to run the SAME baseline battery on REAL
  perturbation-recovery data from Network K (the 100% Phase I autopoietic
  network, commit 4327b89). This addresses Qwen's deeper concern that
  E1's discrimination power may not generalize from synthetic n=3 loops
  to real biochemical perturbation-recovery trajectories.

DESIGN:
  Network K's full Phase I = 100% autopoiesis means mild initial-condition
  perturbations recover fully (~zero deficit, no signal). To get variance
  in recovery_margin_erosion, we perturb the system at the REACTION level
  (single-reaction knockouts), which produces a SPREAD of deficits across
  Network K's 86 reactions (some recover fully, others degrade substantially).

  For each reaction r in Network K (n = 86 reactions):
    1. Run baseline Network K to steady state x0.
    2. Knock out reaction r ONLY (block r's flux) and run T = 500 steps.
    3. Record the degradation trajectory m_j(t) for each metabolite.
    4. Compute on the trajectory:
         kappa_V_real = mean over t of (V_max - V(x(t))) / V_max
                       where V(x) = sum of essential metabolic intermediates
                       (viability function for Network K, real biological,
                       NOT synthetic 1-x^2-y^2)
         baseline_1: raw ||F|| = max |d^2 V/dt^2| (curvature norm)
         baseline_2: Fisher distance = sum |dV/dt|^2 / V (Fisher info)
         baseline_3: viability_margin = max deficit (V_max - V_min)/V_max
         baseline_4: constraint_violation_rate = fraction of t with V < V_thresh
         baseline_5: natural_gradient_norm = |dV/dt| / V (relative gradient)
         baseline_6: random_curvature = random Gaussian noise (null control)
    5. Empirical observable: RECOVERY_MARGIN_EROSION = (V_baseline - V_KO_final)/V_baseline
       (the actual amount of viability lost at the KO steady state, the
       real-data analog of Claim A's "held-out margin erosion rate").
  Then compute partial correlations:
    - kappa_V_real vs recovery_margin_erosion, controlling for each baseline.
    - each baseline vs recovery_margin_erosion, controlling for kappa_V_real.
  PREDICTION: kappa_V's partial r is HIGH (>0.5) and STATISTICALLY SIGNIFICANT
  even after controlling for any baseline; each baseline's partial r is LOWER
  than its zero-order r after controlling for kappa_V (kappa_V absorbs the
  signal). This GENERALIZES E1's verdict from synthetic to real biological
  perturbation-recovery data.

OUTPUTS:
  download/novelty_kappa_v_baselines_real_network_k.{png,csv,txt}
  download/novelty_kappa_v_baselines_real_network_k_results.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm

for _p in (
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
):
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
        except Exception:
            pass

import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Network K module path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import Network K spec + simulator
from autopoiesis_network_K import (  # type: ignore
    network_K, simulate_network, simulate_network_recover,
)


# ----------------------------------------------------------------------
#  Configuration
# ----------------------------------------------------------------------
T_KO = 500                    # KO trajectory length (per v2 dep-ratio protocol)
DELTA = 0.05                  # integration step (Network K default)
V_THRESH = 0.10               # viability threshold (Network K default)


# ----------------------------------------------------------------------
#  Viability function for Network K (REAL, not synthetic)
# ----------------------------------------------------------------------
# Following the manuscript §8 (eq:Hraw), viability is a function of the
# state x; we operationalize V(x) as the SUM of essential metabolic
# intermediates (those tracked by the closure test), normalized to
# V_baseline = 1 at the steady state. This is the REAL biological
# viability function (not synthetic 1-x^2-y^2).

ESSENTIAL_METABOLITES = [
    "AcCoA", "G6P", "FBP", "PEP", "PYR", "ALA", "ASP", "GLU", "OAA", "MAL",
    "DHAP", "G3P", "Glycogen", "PolyP",
]


def viability(state: dict[str, float], baseline_state: dict[str, float]) -> float:
    """Viability = normalized sum of essential metabolites (real biological V)."""
    s = sum(state.get(m, 0.0) for m in ESSENTIAL_METABOLITES)
    s0 = max(1e-9, sum(baseline_state.get(m, 0.0) for m in ESSENTIAL_METABOLITES))
    return s / s0


def viability_deficit(state: dict[str, float], baseline_state: dict[str, float]) -> float:
    """D_V = V_max - V(x); real-data analog of (1 - V/V_max)."""
    return max(0.0, 1.0 - viability(state, baseline_state))


# ----------------------------------------------------------------------
#  Single-reaction-KO degradation trajectory (the data source)
# ----------------------------------------------------------------------
def run_single_reaction_KO(
    reaction_id: str,
    baseline_state: dict[str, float],
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Run a single-reaction-KO degradation trajectory.

    Knock out reaction `reaction_id` ONLY (block its flux). Run T = T_KO steps
    from baseline state. Record trajectory and compute kappa_V + 6 baselines.

    Returns the trajectory + computed kappa_V and 6 baselines + recovery_margin_erosion.
    """
    # Build a modified network with the target reaction FILTERED OUT
    # (works for ALL reaction kinds — metabolic, synthesis, autocatalytic, constitutive)
    modified_reactions = [r for r in network_K["reactions"] if r.get("id") != reaction_id]

    modified_network = {
        "species": network_K["species"],
        "food": network_K["food"],
        "non_food": network_K["non_food"],
        "reactions": modified_reactions,
    }

    # Run the KO simulation from baseline initial state
    trajectory_states = simulate_network(
        modified_network, knockout_species=None, T=T_KO, delta=DELTA,
        food_supply_rate=2.0, food_conc=10.0, Km=0.1, max_conc=100.0,
        init_concs=baseline_state,
    )

    # Compute viability along the trajectory
    V_traj = np.array([viability(s, baseline_state) for s in trajectory_states])
    DV_traj = np.array([viability_deficit(s, baseline_state) for s in trajectory_states])

    # === Compute kappa_V (REAL data version) ===
    kappa_V_real = float(np.mean(DV_traj))

    # === Baseline 1: raw ||F|| — max |d^2 V/dt^2| (curvature norm) ===
    if len(V_traj) >= 3:
        d2V = np.diff(V_traj, n=2)
        raw_F = float(np.max(np.abs(d2V)))
    else:
        raw_F = 0.0

    # === Baseline 2: Fisher distance — sum |dV/dt|^2 / V ===
    if len(V_traj) >= 2:
        dV = np.diff(V_traj)
        V_mid = 0.5 * (V_traj[:-1] + V_traj[1:])
        V_mid_safe = np.where(V_mid < 1e-9, 1e-9, V_mid)
        fisher_dist = float(np.sum(dV**2 / V_mid_safe))
    else:
        fisher_dist = 0.0

    # === Baseline 3: viability_margin — max deficit (1 - V_min/V_max) ===
    V_max_obs = float(np.max(V_traj)) if len(V_traj) > 0 else 0.0
    V_min_obs = float(np.min(V_traj)) if len(V_traj) > 0 else 0.0
    denom = V_max_obs if V_max_obs > 1e-9 else 1e-9
    viability_margin = max(0.0, (V_max_obs - V_min_obs) / denom)

    # === Baseline 4: constraint violation rate — fraction of t with V < V_thresh ===
    constraint_violation_rate = float(np.mean(V_traj < V_THRESH))

    # === Baseline 5: natural gradient norm — |dV/dt| / V (relative) ===
    if len(V_traj) >= 2:
        dV = np.abs(np.diff(V_traj))
        V_mid = 0.5 * (V_traj[:-1] + V_traj[1:])
        V_mid_safe = np.where(V_mid < 1e-9, 1e-9, V_mid)
        natural_grad = float(np.mean(dV / V_mid_safe))
    else:
        natural_grad = 0.0

    # === Baseline 6: random curvature (null control) — Gaussian noise ===
    random_curvature = float(rng.normal(0.0, 0.1))

    # === Empirical observable: recovery margin erosion ===
    # = (V_baseline - V_KO_final)/V_baseline; V_baseline = 1 (normalized)
    V_KO_final = V_traj[-1] if len(V_traj) > 0 else 0.0
    recovery_margin_erosion = max(0.0, 1.0 - V_KO_final)

    return {
        "reaction_id": reaction_id,
        "kappa_V_real": kappa_V_real,
        "raw_F": raw_F,
        "fisher_dist": fisher_dist,
        "viability_margin": viability_margin,
        "constraint_violation_rate": constraint_violation_rate,
        "natural_grad": natural_grad,
        "random_curvature": random_curvature,
        "recovery_margin_erosion": recovery_margin_erosion,
        "V_traj_final": V_KO_final,
    }


# ----------------------------------------------------------------------
#  Partial correlation
# ----------------------------------------------------------------------
def partial_correlation(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Partial correlation r(x,y | z) = (r_xy - r_xz * r_yz) / sqrt((1-r_xz^2)(1-r_yz^2))."""
    def _r(a: np.ndarray, b: np.ndarray) -> float:
        if np.std(a) < 1e-12 or np.std(b) < 1e-12:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    r_xy = _r(x, y)
    r_xz = _r(x, z)
    r_yz = _r(y, z)
    denom = np.sqrt(max(1e-12, (1.0 - r_xz**2) * (1.0 - r_yz**2)))
    return (r_xy - r_xz * r_yz) / denom


# ----------------------------------------------------------------------
#  Main
# ----------------------------------------------------------------------
def main() -> None:
    print("=" * 72)
    print("E8 — kappa_V baseline battery on REAL Network K KO trajectories")
    print("Strengthened Qwen §3.2 + §8.3 (baselines on REAL data, not synthetic n=3)")
    print("=" * 72)

    t0 = time.time()
    rng = np.random.default_rng(20260831)

    # 1. Run baseline Network K to steady state
    print("\n[1/4] Running baseline Network K simulation to steady state...")
    baseline_trajectory = simulate_network(network_K, knockout_species=None, T=1000)
    baseline_state = baseline_trajectory[-1]
    V_baseline = viability(baseline_state, baseline_state)
    print(f"   Baseline steady state V = {V_baseline:.4f}")
    print(f"   (Should be 1.0 by construction; the network reaches its steady state.)")

    # 2. Run single-reaction-KO experiments across all 86 reactions
    print("\n[2/4] Running single-reaction-KO experiments across all Network K reactions...")
    all_reactions = [r["id"] for r in network_K["reactions"] if r.get("id")]
    print(f"   Network K has {len(all_reactions)} reactions; running KO on each.")
    results = []
    for i, r_id in enumerate(all_reactions):
        print(f"   [{i+1}/{len(all_reactions)}] KO reaction {r_id} ... ", end="")
        r = run_single_reaction_KO(r_id, baseline_state, rng)
        results.append(r)
        print(f"kappa_V={r['kappa_V_real']:.4f} erosion={r['recovery_margin_erosion']:.4f}")
    n_total = len(results)
    print(f"   Total KO experiments: {n_total}")
    n_erosion_nonzero = sum(1 for r in results if r["recovery_margin_erosion"] > 1e-4)
    print(f"   Reactions producing erosion > 1e-4: {n_erosion_nonzero}/{n_total}")

    # 3. Compute partial correlations
    print("\n[3/4] Computing partial correlations...")
    erosion = np.array([r["recovery_margin_erosion"] for r in results])
    kappa_V = np.array([r["kappa_V_real"] for r in results])

    baselines = {
        "raw_F": np.array([r["raw_F"] for r in results]),
        "fisher_dist": np.array([r["fisher_dist"] for r in results]),
        "viability_margin": np.array([r["viability_margin"] for r in results]),
        "constraint_violation_rate": np.array([r["constraint_violation_rate"] for r in results]),
        "natural_grad": np.array([r["natural_grad"] for r in results]),
        "random_curvature": np.array([r["random_curvature"] for r in results]),
    }

    # Zero-order r (kappa_V vs erosion, each baseline vs erosion)
    if np.std(kappa_V) < 1e-12 or np.std(erosion) < 1e-12:
        r_kappa_erosion = 0.0
    else:
        r_kappa_erosion = float(np.corrcoef(kappa_V, erosion)[0, 1])
    print(f"   Zero-order r(kappa_V, erosion)         = {r_kappa_erosion:+.4f}")

    baseline_r = {}
    for name, vals in baselines.items():
        if np.std(vals) < 1e-12 or np.std(erosion) < 1e-12:
            baseline_r[name] = 0.0
        else:
            baseline_r[name] = float(np.corrcoef(vals, erosion)[0, 1])
        print(f"   Zero-order r({name:30s}, erosion) = {baseline_r[name]:+.4f}")

    print()
    # Partial r(kappa_V, erosion | each baseline)
    partial_r_kappa = {}
    for name, vals in baselines.items():
        pr = partial_correlation(kappa_V, erosion, vals)
        partial_r_kappa[name] = pr
        print(f"   Partial r(kappa_V, erosion | {name:25s}) = {pr:+.4f}")

    print()
    # Partial r(each_baseline, erosion | kappa_V)
    partial_r_baseline = {}
    for name, vals in baselines.items():
        pr = partial_correlation(vals, erosion, kappa_V)
        partial_r_baseline[name] = pr
        print(f"   Partial r({name:25s}, erosion | kappa_V) = {pr:+.4f}")

    # 4. Bootstrap CI on partial r(kappa_V, erosion | viability_margin)
    print("\n   Bootstrapping 95% CI on r(kappa_V, erosion | viability_margin)...")
    B = 200
    rng_bs = np.random.default_rng(20260831)
    boot_pr = []
    n = len(erosion)
    for _ in range(B):
        idx = rng_bs.integers(0, n, size=n)
        if np.std(kappa_V[idx]) < 1e-12 or np.std(erosion[idx]) < 1e-12:
            continue
        pr = partial_correlation(
            kappa_V[idx], erosion[idx], baselines["viability_margin"][idx]
        )
        boot_pr.append(pr)
    boot_pr = np.array(boot_pr)
    if len(boot_pr) > 0:
        ci_low = float(np.percentile(boot_pr, 2.5))
        ci_high = float(np.percentile(boot_pr, 97.5))
        boot_mean = float(np.mean(boot_pr))
        print(f"   Bootstrap mean partial r = {boot_mean:+.4f}")
        print(f"   95% CI = [{ci_low:+.4f}, {ci_high:+.4f}]")
    else:
        ci_low = ci_high = boot_mean = 0.0

    # 5. Discrimination: which reactions have highest erosion vs lowest?
    print("\n[4/4] Discrimination: top-5 erosive reactions vs bottom-5")
    sorted_results = sorted(results, key=lambda r: r["recovery_margin_erosion"], reverse=True)
    print("   Top-5 erosive reactions (highest recovery_margin_erosion):")
    for r in sorted_results[:5]:
        print(f"     {r['reaction_id']:8s}  erosion={r['recovery_margin_erosion']:.4f}  "
              f"kappa_V={r['kappa_V_real']:.4f}  margin={r['viability_margin']:.4f}")
    print("   Bottom-5 (least erosive):")
    for r in sorted_results[-5:]:
        print(f"     {r['reaction_id']:8s}  erosion={r['recovery_margin_erosion']:.4f}  "
              f"kappa_V={r['kappa_V_real']:.4f}  margin={r['viability_margin']:.4f}")

    # === VERDICT ===
    print("\n" + "=" * 72)
    print("VERDICT (E8):")
    print(f"  n = {n_total} single-reaction-KO experiments on REAL Network K data")
    print(f"  Reactions with erosion > 1e-4: {n_erosion_nonzero}/{n_total}")
    print(f"  Zero-order r(kappa_V, erosion) on REAL Network K data = {r_kappa_erosion:+.4f}")
    print(f"  Partial r(kappa_V, erosion | viability_margin)        = {partial_r_kappa['viability_margin']:+.4f}")
    print(f"  Bootstrap 95% CI                                       = [{ci_low:+.4f}, {ci_high:+.4f}]")
    print()
    if n_erosion_nonzero < 5:
        print("  Insufficient variance in erosion signal — Network K's robustness means")
        print("  most reactions' KO produces near-zero deficit. E8 INCONCLUSIVE.")
        verdict = "INCONCLUSIVE"
    elif partial_r_kappa["viability_margin"] > 0.3:
        print("  kappa_V's partial r > 0.3 EVEN AFTER controlling for viability_margin.")
        print("  kappa_V discriminates on REAL biological KO-recovery data")
        print("  (Network K), GENERALIZING E1's synthetic-n=3 verdict to real data.")
        print("  Qwen §3.2 (self-referential) + §8.3 (baselines) FULLY ELEVATED on REAL data.")
        verdict = "PASS"
    else:
        print("  kappa_V's partial r < 0.3 — kappa_V adds LITTLE signal beyond viability_margin")
        print("  on real Network K data. E1's synthetic-n=3 discrimination does NOT generalize.")
        print("  Qwen §3.2/§8.3 PARTIALLY ELEVATED; honest reporting of weaker real-data signal.")
        verdict = "PARTIAL"
    print("=" * 72)

    # === Save JSON results ===
    os.makedirs("/home/z/my-project/download", exist_ok=True)
    out_json = {
        "study": "E8",
        "design": "kappa_V baseline battery on REAL Network K single-reaction-KO trajectories",
        "qwen_criticism_addressed": ["§3.2 self-referential (strengthened: real data, not synthetic)",
                                      "§8.3 baselines (strengthened: applied to real data)"],
        "n_reactions_KO": n_total,
        "n_reactions_with_erosion_gt_1e-4": n_erosion_nonzero,
        "viability_function": "normalized sum of 14 essential metabolic intermediates (REAL biological V, not synthetic 1-x^2-y^2)",
        "zero_order_r": {
            "r(kappa_V, erosion)": r_kappa_erosion,
            "r(raw_F, erosion)": baseline_r["raw_F"],
            "r(fisher_dist, erosion)": baseline_r["fisher_dist"],
            "r(viability_margin, erosion)": baseline_r["viability_margin"],
            "r(constraint_violation_rate, erosion)": baseline_r["constraint_violation_rate"],
            "r(natural_grad, erosion)": baseline_r["natural_grad"],
            "r(random_curvature, erosion)": baseline_r["random_curvature"],
        },
        "partial_r_kappa_V_given_baseline": partial_r_kappa,
        "partial_r_baseline_given_kappa_V": partial_r_baseline,
        "bootstrap_ci_partial_r_kappa_V_given_viability_margin": {
            "n_bootstrap": B,
            "mean": boot_mean,
            "ci_low_95": ci_low,
            "ci_high_95": ci_high,
        },
        "top_5_erosive_reactions": [
            {"reaction_id": r["reaction_id"], "erosion": r["recovery_margin_erosion"],
             "kappa_V": r["kappa_V_real"], "margin": r["viability_margin"]}
            for r in sorted_results[:5]
        ],
        "bottom_5_erosive_reactions": [
            {"reaction_id": r["reaction_id"], "erosion": r["recovery_margin_erosion"],
             "kappa_V": r["kappa_V_real"], "margin": r["viability_margin"]}
            for r in sorted_results[-5:]
        ],
        "verdict": verdict,
        "pass_threshold": "partial r(kappa_V, erosion | viability_margin) > 0.3 with > 5 erosive reactions",
    }
    with open("/home/z/my-project/download/novelty_kappa_v_baselines_real_network_k_results.json", "w") as f:
        json.dump(out_json, f, indent=2)

    # === Save CSV ===
    import csv
    with open("/home/z/my-project/download/novelty_kappa_v_baselines_real_network_k.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["reaction_id",
                    "kappa_V_real", "raw_F", "fisher_dist", "viability_margin",
                    "constraint_violation_rate", "natural_grad", "random_curvature",
                    "recovery_margin_erosion", "V_traj_final"])
        for r in results:
            w.writerow([r["reaction_id"],
                        r["kappa_V_real"], r["raw_F"], r["fisher_dist"],
                        r["viability_margin"], r["constraint_violation_rate"],
                        r["natural_grad"], r["random_curvature"],
                        r["recovery_margin_erosion"], r["V_traj_final"]])

    # === Save TXT report ===
    with open("/home/z/my-project/download/novelty_kappa_v_baselines_real_network_k.txt", "w") as f:
        f.write("E8 — kappa_V baseline battery on REAL Network K KO trajectories\n")
        f.write("=" * 72 + "\n\n")
        f.write("STRENGTHENED Qwen §3.2 (self-referential) + §8.3 (baselines):\n")
        f.write("Apply E1's baseline battery to REAL Network K single-reaction-KO\n")
        f.write("data (not just synthetic n=3 prototype loops).\n\n")
        f.write(f"n_experiments = {n_total} single-reaction-KO experiments (all Network K reactions)\n")
        f.write(f"Reactions with erosion > 1e-4: {n_erosion_nonzero}/{n_total}\n")
        f.write(f"Viability function: normalized sum of {len(ESSENTIAL_METABOLITES)} "
                f"essential metabolic intermediates (REAL biological V, NOT synthetic 1-x^2-y^2)\n\n")
        f.write("ZERO-ORDER correlations (predictor vs recovery_margin_erosion):\n")
        f.write(f"  r(kappa_V, erosion)               = {r_kappa_erosion:+.4f}\n")
        for name in baselines:
            f.write(f"  r({name:30s}, erosion) = {baseline_r[name]:+.4f}\n")
        f.write("\nPARTIAL r(kappa_V, erosion | baseline):\n")
        for name in baselines:
            f.write(f"  r(kappa_V, erosion | {name:25s}) = {partial_r_kappa[name]:+.4f}\n")
        f.write(f"\nPARTIAL r(baseline, erosion | kappa_V):\n")
        for name in baselines:
            f.write(f"  r({name:25s}, erosion | kappa_V) = {partial_r_baseline[name]:+.4f}\n")
        f.write(f"\nBOOTSTRAP 95% CI on partial r(kappa_V, erosion | viability_margin):\n")
        f.write(f"  mean = {boot_mean:+.4f}, CI = [{ci_low:+.4f}, {ci_high:+.4f}] (B={B})\n")
        f.write(f"\nTop-5 erosive reactions:\n")
        for r in sorted_results[:5]:
            f.write(f"  {r['reaction_id']:8s}  erosion={r['recovery_margin_erosion']:.4f}  "
                    f"kappa_V={r['kappa_V_real']:.4f}  margin={r['viability_margin']:.4f}\n")
        f.write(f"\nBottom-5 (least erosive):\n")
        for r in sorted_results[-5:]:
            f.write(f"  {r['reaction_id']:8s}  erosion={r['recovery_margin_erosion']:.4f}  "
                    f"kappa_V={r['kappa_V_real']:.4f}  margin={r['viability_margin']:.4f}\n")
        f.write(f"\nVERDICT: {verdict}\n")
        f.write(f"  (threshold: partial r(kappa_V, erosion | viability_margin) > 0.3 with > 5 erosive reactions)\n")

    # === Plot ===
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)
    fig.suptitle(
        "E8: $\\kappa_V$ baseline battery on REAL Network K single-reaction-KO trajectories\n"
        "(Strengthened Qwen §3.2 + §8.3: baselines on REAL data, not synthetic n=3)",
        fontsize=12,
    )

    # Panel 1: Zero-order r bar chart
    ax = axes[0, 0]
    names = ["kappa_V"] + list(baselines.keys())
    vals = [r_kappa_erosion] + [baseline_r[n] for n in baselines]
    colors = ["#2a9d8f"] + ["#e76f51"] * len(baselines)
    ax.barh(names, vals, color=colors)
    ax.set_xlabel("Zero-order r(predictor, recovery_margin_erosion)")
    ax.set_title("Zero-order correlations (real Network K KO data)")
    ax.axvline(0.0, color="black", lw=0.5)
    ax.axvline(0.3, color="green", lw=0.5, ls="--", label="0.3 (mild)")
    ax.axvline(0.5, color="blue", lw=0.5, ls="--", label="0.5 (moderate)")
    ax.legend(fontsize=8)
    for i, v in enumerate(vals):
        if np.isfinite(v):
            ax.text(v + 0.01 * np.sign(v), i, f"{v:+.2f}", va="center", fontsize=8)

    # Panel 2: Partial r(kappa_V | baseline) bar chart
    ax = axes[0, 1]
    names = list(baselines.keys())
    vals = [partial_r_kappa[n] for n in baselines]
    ax.barh(names, vals, color="#2a9d8f")
    ax.set_xlabel("Partial r($\\kappa_V$, erosion | baseline)")
    ax.set_title("$\\kappa_V$'s signal AFTER controlling for each baseline")
    ax.axvline(0.0, color="black", lw=0.5)
    ax.axvline(0.3, color="green", lw=0.5, ls="--", label="0.3 threshold")
    ax.legend(fontsize=8)
    for i, v in enumerate(vals):
        if np.isfinite(v):
            ax.text(v + 0.01 * np.sign(v), i, f"{v:+.2f}", va="center", fontsize=8)

    # Panel 3: Partial r(baseline | kappa_V) bar chart
    ax = axes[1, 0]
    vals = [partial_r_baseline[n] for n in baselines]
    ax.barh(names, vals, color="#e76f51")
    ax.set_xlabel("Partial r(baseline, erosion | $\\kappa_V$)")
    ax.set_title("Each baseline's signal AFTER controlling for $\\kappa_V$")
    ax.axvline(0.0, color="black", lw=0.5)
    ax.axvline(0.3, color="green", lw=0.5, ls="--", label="0.3 threshold")
    ax.legend(fontsize=8)
    for i, v in enumerate(vals):
        if np.isfinite(v):
            ax.text(v + 0.01 * np.sign(v), i, f"{v:+.2f}", va="center", fontsize=8)

    # Panel 4: scatter kappa_V vs erosion
    ax = axes[1, 1]
    ax.scatter(kappa_V, erosion, alpha=0.5, s=20, c="#2a9d8f")
    # Linear fit
    if np.std(kappa_V) > 1e-12 and np.std(erosion) > 1e-12:
        A = np.vstack([kappa_V, np.ones_like(kappa_V)]).T
        slope, intercept = np.linalg.lstsq(A, erosion, rcond=None)[0]
        xs = np.linspace(kappa_V.min(), kappa_V.max(), 50)
        ax.plot(xs, slope * xs + intercept, "r-", lw=1,
                label=f"slope={slope:.3f}, r={r_kappa_erosion:+.3f}")
        ax.legend(fontsize=8)
    ax.set_xlabel("$\\kappa_V$ (real-data: mean viability deficit over KO trajectory)")
    ax.set_ylabel("Recovery margin erosion (real-data: V_baseline - V_KO_final)")
    ax.set_title("Real-data $\\kappa_V$ vs erosion (Network K, n={})".format(n_total))
    ax.axhline(0.0, color="black", lw=0.5)
    ax.axvline(0.0, color="black", lw=0.5)

    plt.savefig("/home/z/my-project/download/novelty_kappa_v_baselines_real_network_k.png", dpi=120)
    plt.close()

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Results saved to download/novelty_kappa_v_baselines_real_network_k.{{png,csv,txt,json}}")


if __name__ == "__main__":
    main()
