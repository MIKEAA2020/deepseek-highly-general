#!/usr/bin/env python3
"""
Target 5 extension - Stress test of Claim D's heavy-tail index eta_k.

The original Claim D operationalization uses eta_k drawn from a single
heavy-tailed distribution (Student-t, df=3, scale=0.01) at one amplitude
(a=0.3) with one seed. This script stress-tests the heavy-tail index by
sweeping:

  - Tail-index axis: df in {1.5, 2, 2.5, 3, 4, 5, 7, 10, 20, 50, inf}
    (df=inf corresponds to a Gaussian, the light-tailed limit; df=1.5
    lies in the infinite-variance regime, alpha=1.5 < 2)
  - Noise-scale axis: sigma in {0.005, 0.01, 0.02, 0.05, 0.10}
  - Monte-Carlo axis: N_runs = 200 independent seeds per (df, sigma) cell

For each cell we report:
  - mean K_pred (first k with sum F_k > 1, averaged over seeds)
  - mean K_obs (first k with V_max,k < exp(-1), averaged over seeds)
  - mean relative error |K_obs - K_pred| / max(K_pred, 1)
  - fraction of seeds with verdict CONFIRMED (rel_err < 0.15)
  - std(K_obs) (stability of the observed threshold under resampling)

Theory:
  For heavy-tailed noise with tail index alpha = df (Student-t), the
  variance of eta_k is finite iff df > 2 and the mean is finite iff df > 1.
  The cumulative sum sum_k F_k has mean k * mu (mu = a*kappa_V + C*a^{3/2})
  and variance growing as k * Var(eta) for finite variance, and faster
  for infinite variance. The bound sum F_k > 1 is hit at
  K ~ 1/mu  (deterministic part)  +  heavy-tail fluctuations.

  Stress verdicts (per cell, N_runs=200):
    ROBUST        if frac_conf >= 0.95
    ACCEPTABLE    if 0.80 <= frac_conf < 0.95
    DEGRADED      if 0.50 <= frac_conf < 0.80
    BROKEN        if frac_conf < 0.50
    UNDEFINED     if df <= 1.0 (infinite-mean regime, K_pred ill-defined)

The decisive stress-test prediction: the original Claim D result (df=3,
sigma=0.01, single seed) should reproduce at the operating scale
(N_runs=200, frac_confirmed -> 1.0). The boundary of the heavy-tail
regime where the prediction breaks down (df -> 1) is mapped.

Outputs:
  /home/z/my-project/download/claim_d_heavytail_stress.png   (3-panel)
  /home/z/my-project/download/claim_d_heavytail_stress.csv   (per-cell)
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from scipy.stats import t as student_t, norm

# Font setup (project convention)
fm.fontManager.addfont("/usr/share/fonts/truetype/chinese/SarasaMonoSC-Light.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

SLATE = "#3d5764"
ACCENT = "#2897cf"
RUST = "#bf5836"


# ---------------------------------------------------------------------------
# Prototype primitives (same as claims_a_e_operationalization.py)
# ---------------------------------------------------------------------------

def kappa_V(a):
    """Per-loop viability-weighted curvature (n=3 or n=4, radially symmetric)."""
    return a ** 2


def per_loop_fatigue(a, C_fatigue, eta):
    """F_k = a * kappa_V(a) + C * a^{3/2} + eta_k."""
    return a * kappa_V(a) + C_fatigue * (a ** 1.5) + eta


def single_run_K_pred_obs(a, C_fatigue, df, sigma_eta, K_max, rng):
    """One Monte-Carlo run: return (K_pred, K_obs, rel_err, verdict_label).

    eta_k distribution:
      - df finite and > 0: Student-t(df, scale=sigma_eta)
      - df == inf: Gaussian(0, sigma_eta)
    """
    if np.isinf(df):
        eta = rng.normal(0, sigma_eta, size=K_max)
    else:
        eta = student_t.rvs(df=df, scale=sigma_eta, size=K_max,
                            random_state=rng)

    F_per_loop = per_loop_fatigue(a, C_fatigue, eta)
    F_cum = np.cumsum(F_per_loop)

    # K_pred: first k with sum F_k > 1
    above_pred = F_cum > 1.0
    if above_pred.any():
        K_pred = int(np.argmax(above_pred) + 1)
    else:
        K_pred = np.inf

    # K_obs: first k with V_max,k < exp(-1)
    V_max = np.zeros(K_max + 1)
    V_max[0] = 1.0
    for k in range(K_max):
        V_max[k + 1] = V_max[k] * (1.0 - F_per_loop[k])
    V_fail = np.exp(-1.0)
    above_obs = V_max < V_fail
    K_obs = int(np.argmax(above_obs)) if above_obs.any() else np.inf

    # Verdict (matches claims_a_e_operationalization.py: rel_err < 0.15)
    if np.isinf(K_pred) and np.isinf(K_obs):
        verdict = "REFUTED"
        rel_err = np.nan
    elif np.isinf(K_pred) or np.isinf(K_obs):
        verdict = "REFUTED"
        rel_err = np.nan
    else:
        rel_err = abs(K_obs - K_pred) / max(K_pred, 1)
        if rel_err < 0.15:
            verdict = "CONFIRMED"
        elif rel_err < 0.30:
            verdict = "WEAK"
        else:
            verdict = "REFUTED"

    return K_pred, K_obs, rel_err, verdict


def verdict_label_for_df(df):
    """Per-cell aggregate label (UNDEFINED for df <= 1)."""
    if df <= 1.0:
        return "UNDEFINED"
    return ""  # filled in by aggregate


def aggregate_cell(a, C_fatigue, df, sigma_eta, K_max, N_runs, master_seed):
    """Run N_runs Monte-Carlo draws at fixed (df, sigma); return summary."""
    if df <= 1.0:
        # Infinite-mean regime; K_pred is ill-defined.
        return {
            "df": df, "sigma": sigma_eta,
            "K_pred_mean": np.nan, "K_obs_mean": np.nan,
            "rel_err_mean": np.nan, "frac_confirmed": 0.0,
            "K_obs_std": np.nan, "verdict": "UNDEFINED",
            "n_runs": 0,
        }

    ssr = np.random.SeedSequence(master_seed)
    child_seeds = ssr.spawn(N_runs)
    K_preds, K_obss, rel_errs, confirms = [], [], [], []
    for cs in child_seeds:
        rng = np.random.default_rng(cs)
        Kp, Ko, re, v = single_run_K_pred_obs(
            a, C_fatigue, df, sigma_eta, K_max, rng)
        if np.isfinite(Kp) and np.isfinite(Ko):
            K_preds.append(Kp)
            K_obss.append(Ko)
            rel_errs.append(re)
            confirms.append(1 if v == "CONFIRMED" else 0)
        else:
            # If the run never crosses within K_max, mark as not-confirmed.
            confirms.append(0)
            rel_errs.append(np.nan)

    K_preds = np.array(K_preds, dtype=float)
    K_obss = np.array(K_obss, dtype=float)
    rel_errs = np.array(rel_errs, dtype=float)
    frac = float(np.mean(confirms))

    if frac >= 0.95:
        agg_v = "ROBUST"
    elif frac >= 0.80:
        agg_v = "ACCEPTABLE"
    elif frac >= 0.50:
        agg_v = "DEGRADED"
    else:
        agg_v = "BROKEN"

    return {
        "df": df, "sigma": sigma_eta,
        "K_pred_mean": float(np.mean(K_preds)) if len(K_preds) else np.nan,
        "K_obs_mean": float(np.mean(K_obss)) if len(K_obss) else np.nan,
        "rel_err_mean": float(np.nanmean(rel_errs)),
        "frac_confirmed": frac,
        "K_obs_std": float(np.std(K_obss)) if len(K_obss) else np.nan,
        "verdict": agg_v,
        "n_runs": N_runs,
    }


def main():
    out_dir = "/home/z/my-project/download"
    os.makedirs(out_dir, exist_ok=True)

    # Stress-test configuration
    a = 0.3
    C_fatigue = 0.05
    K_max = 200  # extend to 200 so K~25 has headroom and the df=1.5 noise can cross
    N_runs = 200
    master_seed = 20240904

    # df axis (the heavy-tail index). df=inf is Gaussian (light tail).
    df_axis = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0, 20.0, 50.0, np.inf]
    sigma_axis = [0.005, 0.01, 0.02, 0.05, 0.10]

    print("=== Claim D heavy-tail index eta_k stress test ===")
    print(f"  a = {a}, C_fatigue = {C_fatigue}, K_max = {K_max}, "
          f"N_runs = {N_runs} per cell")
    print(f"  df_axis = {df_axis}")
    print(f"  sigma_axis = {sigma_axis}")
    print()

    # Run grid
    grid = {}  # (df_i, sigma_j) -> summary dict
    for i, df in enumerate(df_axis):
        for j, sg in enumerate(sigma_axis):
            s = aggregate_cell(a, C_fatigue, df, sg, K_max, N_runs,
                                master_seed + i * 100 + j)
            grid[(i, j)] = s
            df_str = "inf" if np.isinf(df) else f"{df:.1f}"
            print(f"  df={df_str:>4}  sigma={sg:.3f}  "
                  f"K_pred={s['K_pred_mean']:6.2f}  "
                  f"K_obs={s['K_obs_mean']:6.2f}  "
                  f"rel_err={s['rel_err_mean']:.3f}  "
                  f"frac_conf={s['frac_confirmed']:.3f}  "
                  f"-> {s['verdict']}")

    # Reference cell (original Claim D configuration): df=3, sigma=0.01
    ref = grid[(df_axis.index(3.0), sigma_axis.index(0.01))]
    print()
    print(f"Reference cell (original Claim D config, df=3, sigma=0.01):")
    print(f"  K_pred_mean = {ref['K_pred_mean']:.3f}")
    print(f"  K_obs_mean  = {ref['K_obs_mean']:.3f}")
    print(f"  rel_err_mean = {ref['rel_err_mean']:.4f}")
    print(f"  frac_confirmed = {ref['frac_confirmed']:.3f}  "
          f"(N_runs={ref['n_runs']})")
    print(f"  K_obs_std = {ref['K_obs_std']:.3f}")
    print(f"  verdict: {ref['verdict']}")

    # CSV
    csv_path = os.path.join(out_dir, "claim_d_heavytail_stress.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["df", "sigma", "K_pred_mean", "K_obs_mean",
                    "rel_err_mean", "frac_confirmed", "K_obs_std",
                    "verdict", "n_runs"])
        for (i, j), s in grid.items():
            df = df_axis[i]
            df_str = "inf" if np.isinf(df) else f"{df:.1f}"
            w.writerow([df_str, f"{s['sigma']:.4f}",
                        f"{s['K_pred_mean']:.4f}",
                        f"{s['K_obs_mean']:.4f}",
                        f"{s['rel_err_mean']:.4f}",
                        f"{s['frac_confirmed']:.4f}",
                        (f"{s['K_obs_std']:.4f}"
                         if not np.isnan(s['K_obs_std']) else "nan"),
                        s['verdict'], s['n_runs']])
    print(f"\nResults CSV: {csv_path}")

    # ---- Figure (3 panels) ----
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.0), constrained_layout=True)

    # Panel 1: heatmap of frac_confirmed across (df, sigma)
    ax = axs[0]
    frac_grid = np.full((len(df_axis), len(sigma_axis)), np.nan)
    for (i, j), s in grid.items():
        frac_grid[i, j] = s["frac_confirmed"]
    im = ax.imshow(frac_grid, origin="lower", aspect="auto",
                   cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(sigma_axis)))
    ax.set_xticklabels([f"{s:.3f}" for s in sigma_axis], fontsize=8)
    ax.set_yticks(range(len(df_axis)))
    ax.set_yticklabels([("inf" if np.isinf(d) else f"{d:.1f}")
                        for d in df_axis], fontsize=8)
    ax.set_xlabel(r"Noise scale $\sigma_\eta$", fontsize=10)
    ax.set_ylabel(r"Tail index df (heavy-tail index $\alpha$)",
                  fontsize=10)
    ax.set_title("(a) Fraction of CONFIRMED runs\n"
                 f"(N_runs={N_runs} per cell)", fontsize=10)
    for i in range(len(df_axis)):
        for j in range(len(sigma_axis)):
            v = frac_grid[i, j]
            if np.isnan(v):
                txt = "undef"
            else:
                txt = f"{v:.2f}"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=7.5, color="black")
    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label("frac CONFIRMED", fontsize=9)

    # Panel 2: K_pred vs K_obs across df at sigma=0.01 (operating scale)
    ax = axs[1]
    sigma_idx = sigma_axis.index(0.01)
    Kp_vals = [grid[(i, sigma_idx)]["K_pred_mean"] for i in range(len(df_axis))]
    Ko_vals = [grid[(i, sigma_idx)]["K_obs_mean"] for i in range(len(df_axis))]
    Ko_std = [grid[(i, sigma_idx)]["K_obs_std"] for i in range(len(df_axis))]
    x_labels = ["inf" if np.isinf(d) else f"{d:.1f}"
                for d in df_axis]
    x = np.arange(len(df_axis))
    ax.errorbar(x, Ko_vals, yerr=Ko_std, fmt="o-", color=ACCENT,
                capsize=4, markersize=6, linewidth=1.5,
                label=r"$K_{obs}$ mean $\pm$ std", zorder=3)
    ax.plot(x, Kp_vals, "s--", color=RUST, markersize=6, linewidth=1.5,
            label=r"$K_{pred}$ (theory)", zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=8)
    ax.set_xlabel(r"Tail index df ($\infty$ = Gaussian)", fontsize=10)
    ax.set_ylabel(r"Iteration $K$", fontsize=10)
    ax.set_title("(b) $K_{pred}$ vs $K_{obs}$ across tail index\n"
                 r"at operating scale $\sigma_\eta = 0.01$",
                 fontsize=10)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(alpha=0.3)
    # shade infinite-mean regime (df <= 1) for context
    ax.axvspan(-0.5, -0.5, alpha=0)  # noop, keeps layout consistent

    # Panel 3: frac_confirmed vs df for all sigma (line plot)
    ax = axs[2]
    for j, sg in enumerate(sigma_axis):
        ys = [grid[(i, j)]["frac_confirmed"] for i in range(len(df_axis))]
        ax.plot(x, ys, "o-", linewidth=1.5, markersize=5,
                label=rf"$\sigma_\eta$={sg:.3f}")
    ax.axhline(0.95, color=SLATE, linestyle=":", alpha=0.6,
               label="ROBUST threshold 0.95")
    ax.axhline(0.80, color=SLATE, linestyle="--", alpha=0.4,
               label="ACCEPTABLE threshold 0.80")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=8)
    ax.set_xlabel(r"Tail index df", fontsize=10)
    ax.set_ylabel("frac CONFIRMED", fontsize=10)
    ax.set_title("(c) Stress boundary across tail index and scale\n"
                 f"(N_runs={N_runs} per cell)", fontsize=10)
    ax.set_ylim(-0.05, 1.10)
    ax.legend(fontsize=7.5, loc="lower right", ncol=2)
    ax.grid(alpha=0.3)

    fig.suptitle(
        "Claim D heavy-tail index $\\eta_k$ stress test "
        f"(N_runs={N_runs} per cell, a={a}, C_fatigue={C_fatigue})",
        fontsize=12, color=SLATE, y=1.02)

    fig_path = os.path.join(out_dir, "claim_d_heavytail_stress.png")
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)
    print(f"Figure: {fig_path}")


if __name__ == "__main__":
    main()
