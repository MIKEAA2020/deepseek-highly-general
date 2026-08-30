#!/usr/bin/env python3
"""
E10 threshold sensitivity sweep on the time-level indicator mask.

Original v10 κ_V definition uses indicator_T = 𝟙[Δb(t) > 0.05·b_wt], applied
uniformly to ALL 92 genes at each time point. This script sweeps the threshold
τ ∈ {0.001, 0.01, 0.05, 0.10, 0.15, 0.20, 0.25} and reports how:
  - the indicator_T vector (over T1..T8) changes,
  - Pearson r(log10 κ_V, |log2 FC|) over all 736 gene-T pairs,
  - Spearman ρ(κ_V, |log2 FC|) over all 736 gene-T pairs,
  - per-gene-max Pearson r and Spearman ρ over 92 genes,
  - per-gene-max on UNMAPPED-only subset (91 genes after the 1 MAPPED gene b2097).

Data sources:
  /tmp/my-project/download/novelty_real_time_series_e10.csv
  /tmp/my-project/download/novelty_real_time_series_e10_results.json

Outputs:
  /home/z/my-project/download/e10_threshold_sensitivity.csv
  /home/z/my-project/download/e10_threshold_sensitivity.txt
  /home/z/my-project/download/e10_threshold_sensitivity.png
  /home/z/my-project/download/e10_threshold_sensitivity.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

CSV_IN = Path("/tmp/my-project/download/novelty_real_time_series_e10.csv")
JSON_IN = Path("/tmp/my-project/download/novelty_real_time_series_e10_results.json")
OUT_DIR = Path("/home/z/my-project/download")

THRESHOLDS = [0.001, 0.01, 0.05, 0.10, 0.15, 0.20, 0.25]


def _safe_log10(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """log10 with offset to handle zeros (indicator-weighted κ_V has many)."""
    return np.log10(np.where(x > 0, x, eps))


def _pearson(x: np.ndarray, y: np.ndarray):
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3 or np.std(x[mask]) < 1e-15 or np.std(y[mask]) < 1e-15:
        return float("nan"), float("nan")
    r, p = pearsonr(x[mask], y[mask])
    return float(r), float(p)


def _spearman(x: np.ndarray, y: np.ndarray):
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3 or np.std(x[mask]) < 1e-15 or np.std(y[mask]) < 1e-15:
        return float("nan"), float("nan")
    rho, p = spearmanr(x[mask], y[mask])
    return float(rho), float(p)


def main() -> int:
    df = pd.read_csv(CSV_IN)
    with JSON_IN.open() as f:
        j = json.load(f)
    bio_per_T = j["iJO1366"]["biomass_per_T"]
    b_wt = j["iJO1366"]["baseline_biomass_T1"]
    delta_b_per_T = {t: b_wt - bio for t, bio in bio_per_T.items()}

    print("=" * 78)
    print("E10 THRESHOLD SENSITIVITY SWEEP")
    print("Time-level indicator mask:  indicator_T = 𝟙[Δb(t) > τ · b_wt]")
    print("=" * 78)
    print(f"b_wt (T1) = {b_wt:.6f}")
    print(f"Δb per T:")
    for t in sorted(bio_per_T):
        print(f"  {t}: biomass = {bio_per_T[t]:.6f}  Δb = {delta_b_per_T[t]:+.6f}")

    # Verify mapping-status counts
    n_mapped = df["mapping_status"].str.startswith("MAPPED").sum() // 8
    n_global = df["mapping_status"].str.startswith("GLOBAL").sum() // 8
    n_total_genes = df["gene"].nunique()
    print(f"\nGene counts: MAPPED={n_mapped}  UNMAPPED(GLOBAL)={n_global}  TOTAL={n_total_genes}")

    rows = []
    indicator_table = {}
    for tau in THRESHOLDS:
        thr = tau * b_wt
        ind_T = {t: float(delta_b_per_T[t] > thr) for t in bio_per_T}
        indicator_table[tau] = ind_T
        n_active_T = int(sum(ind_T.values()))
        # Apply mask
        df_tau = df.copy()
        df_tau["indicator_T"] = df_tau["time_point"].map(ind_T)
        df_tau["kV_v10"] = df_tau["kappa_V_predicted"] * df_tau["indicator_T"]
        # All-pairs correlation
        x_orig = df_tau["kappa_V_predicted"].values.astype(float)
        x_new = df_tau["kV_v10"].values.astype(float)
        y = df_tau["abs_log2_FC"].values.astype(float)
        r_orig, p_orig = _pearson(_safe_log10(x_orig), y)
        r_new, p_new = _pearson(_safe_log10(x_new), y)
        rho_orig, _ = _spearman(x_orig, y)
        rho_new, _ = _spearman(x_new, y)
        # Per-gene max (all 92)
        gene_max_orig = df_tau.groupby("gene")["kappa_V_predicted"].max()
        gene_max_new = df_tau.groupby("gene")["kV_v10"].max()
        gene_max_fc = df_tau.groupby("gene")["abs_log2_FC"].max()
        r_g_orig, _ = _pearson(_safe_log10(gene_max_orig.values), gene_max_fc.values)
        r_g_new, _ = _pearson(_safe_log10(gene_max_new.values), gene_max_fc.values)
        rho_g_orig, _ = _spearman(gene_max_orig.values, gene_max_fc.values)
        rho_g_new, _ = _spearman(gene_max_new.values, gene_max_fc.values)
        # Per-gene max on UNMAPPED-only subset (drop the 1 MAPPED gene b2097)
        df_unmapped = df_tau[~df_tau["mapping_status"].str.startswith("MAPPED")]
        gene_max_new_u = df_unmapped.groupby("gene")["kV_v10"].max()
        gene_max_orig_u = df_unmapped.groupby("gene")["kappa_V_predicted"].max()
        gene_max_fc_u = df_unmapped.groupby("gene")["abs_log2_FC"].max()
        r_g_orig_u, _ = _pearson(_safe_log10(gene_max_orig_u.values), gene_max_fc_u.values)
        r_g_new_u, _ = _pearson(_safe_log10(gene_max_new_u.values), gene_max_fc_u.values)
        rho_g_orig_u, _ = _spearman(gene_max_orig_u.values, gene_max_fc_u.values)
        rho_g_new_u, _ = _spearman(gene_max_new_u.values, gene_max_fc_u.values)
        rows.append({
            "tau": tau,
            "threshold_abs": thr,
            "n_active_T": n_active_T,
            "indicator_T": ",".join(f"{int(ind_T[t])}" for t in sorted(ind_T)),
            "r_all_orig": r_orig, "r_all_v10": r_new,
            "rho_all_orig": rho_orig, "rho_all_v10": rho_new,
            "r_gene_all_orig": r_g_orig, "r_gene_all_v10": r_g_new,
            "rho_gene_all_orig": rho_g_orig, "rho_gene_all_v10": rho_g_new,
            "r_gene_unmapped_orig": r_g_orig_u, "r_gene_unmapped_v10": r_g_new_u,
            "rho_gene_unmapped_orig": rho_g_orig_u, "rho_gene_unmapped_v10": rho_g_new_u,
            "n_unmapped_genes": int(len(gene_max_new_u)),
        })
    res = pd.DataFrame(rows)
    # Print
    print(f"\nIndicator T vectors by threshold (1 = mask ON, 0 = mask OFF):")
    print(f"  {'tau':>6s} {'threshold':>10s}  T1 T2 T3 T4 T5 T6 T7 T8  n_active")
    for r in rows:
        print(f"  {r['tau']:>6.3f} {r['threshold_abs']:>10.4f}  "
              f"{r['indicator_T'].replace(',', ' ')}    {r['n_active_T']}/8")
    print()
    print(f"All-pairs (n=736) correlations:")
    print(f"  {'tau':>6s}  r_orig      r_v10       Δr          ρ_orig    ρ_v10     Δρ")
    for r in rows:
        print(f"  {r['tau']:>6.3f}  {r['r_all_orig']:+.4f}  {r['r_all_v10']:+.4f}  "
              f"{r['r_all_v10']-r['r_all_orig']:+.4f}    "
              f"{r['rho_all_orig']:+.4f}  {r['rho_all_v10']:+.4f}  "
              f"{r['rho_all_v10']-r['rho_all_orig']:+.4f}")
    print()
    print(f"Per-gene max (ALL 92 genes) correlations:")
    print(f"  {'tau':>6s}  r_orig      r_v10       Δr          ρ_orig    ρ_v10     Δρ")
    for r in rows:
        print(f"  {r['tau']:>6.3f}  {r['r_gene_all_orig']:+.4f}  {r['r_gene_all_v10']:+.4f}  "
              f"{r['r_gene_all_v10']-r['r_gene_all_orig']:+.4f}    "
              f"{r['rho_gene_all_orig']:+.4f}  {r['rho_gene_all_v10']:+.4f}  "
              f"{r['rho_gene_all_v10']-r['rho_gene_all_orig']:+.4f}")
    print()
    print(f"Per-gene max (UNMAPPED-ONLY, n={rows[0]['n_unmapped_genes']} genes) correlations:")
    print(f"  {'tau':>6s}  r_orig      r_v10       Δr          ρ_orig    ρ_v10     Δρ")
    for r in rows:
        print(f"  {r['tau']:>6.3f}  {r['r_gene_unmapped_orig']:+.4f}  "
              f"{r['r_gene_unmapped_v10']:+.4f}  "
              f"{r['r_gene_unmapped_v10']-r['r_gene_unmapped_orig']:+.4f}    "
              f"{r['rho_gene_unmapped_orig']:+.4f}  {r['rho_gene_unmapped_v10']:+.4f}  "
              f"{r['rho_gene_unmapped_v10']-r['rho_gene_unmapped_orig']:+.4f}")

    # Save CSV + TXT + JSON
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_DIR / "e10_threshold_sensitivity.csv", index=False)
    # TXT report
    with (OUT_DIR / "e10_threshold_sensitivity.txt").open("w") as f:
        f.write("E10 threshold sensitivity sweep (time-level mask)\n")
        f.write(f"b_wt (T1) = {b_wt:.6f}\n")
        f.write(f"Δb per T: {delta_b_per_T}\n\n")
        f.write("Indicator T vectors:\n")
        for r in rows:
            f.write(f"  tau={r['tau']:.3f}  thr={r['threshold_abs']:.4f}  "
                    f"T1..T8 = {r['indicator_T']}  n_active={r['n_active_T']}/8\n")
        f.write("\nAll-pairs (n=736) correlations:\n")
        f.write("tau, r_orig, r_v10, Δr, ρ_orig, ρ_v10, Δρ\n")
        for r in rows:
            f.write(f"{r['tau']}, {r['r_all_orig']:+.4f}, {r['r_all_v10']:+.4f}, "
                    f"{r['r_all_v10']-r['r_all_orig']:+.4f}, "
                    f"{r['rho_all_orig']:+.4f}, {r['rho_all_v10']:+.4f}, "
                    f"{r['rho_all_v10']-r['rho_all_orig']:+.4f}\n")
        f.write("\nPer-gene max (ALL 92 genes) correlations:\n")
        for r in rows:
            f.write(f"  tau={r['tau']:.3f}  r_orig={r['r_gene_all_orig']:+.4f}  "
                    f"r_v10={r['r_gene_all_v10']:+.4f}  "
                    f"Δr={r['r_gene_all_v10']-r['r_gene_all_orig']:+.4f}  "
                    f"ρ_orig={r['rho_gene_all_orig']:+.4f}  "
                    f"ρ_v10={r['rho_gene_all_v10']:+.4f}  "
                    f"Δρ={r['rho_gene_all_v10']-r['rho_gene_all_orig']:+.4f}\n")
        f.write("\nPer-gene max (UNMAPPED-ONLY) correlations:\n")
        for r in rows:
            f.write(f"  tau={r['tau']:.3f}  r_orig={r['r_gene_unmapped_orig']:+.4f}  "
                    f"r_v10={r['r_gene_unmapped_v10']:+.4f}  "
                    f"Δr={r['r_gene_unmapped_v10']-r['r_gene_unmapped_orig']:+.4f}  "
                    f"ρ_orig={r['rho_gene_unmapped_orig']:+.4f}  "
                    f"ρ_v10={r['rho_gene_unmapped_v10']:+.4f}  "
                    f"Δρ={r['rho_gene_unmapped_v10']-r['rho_gene_unmapped_orig']:+.4f}\n")
    # JSON — cast numpy/pandas types to native Python, handle NaN
    def _clean(obj):
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_clean(v) for v in obj]
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return None if not np.isfinite(obj) else float(obj)
        if isinstance(obj, float):
            return None if not np.isfinite(obj) else obj
        return obj
    (OUT_DIR / "e10_threshold_sensitivity.json").write_text(json.dumps(_clean({
        "b_wt_T1": b_wt,
        "biomass_per_T": bio_per_T,
        "delta_b_per_T": delta_b_per_T,
        "gene_counts": {"mapped": n_mapped, "unmapped": n_global, "total": n_total_genes},
        "thresholds": THRESHOLDS,
        "indicator_T_by_tau": indicator_table,
        "note_unmapped_per_gene_nan": (
            "Per-gene-max on UNMAPPED-only subset returns NaN because all "
            "91 unmapped genes share the identical global-biomass-deficit^2 "
            "κ_V trajectory. After taking max over T1-T8, all 91 genes have "
            "the same max κ_V value, so Pearson/Spearman correlation with "
            "their (varying) max |log2 FC| values is mathematically undefined."
        ),
        "results": rows,
    }), indent=2))
    print(f"\nWrote: {OUT_DIR}/e10_threshold_sensitivity.{{csv,txt,json}}")

    # Plot
    try:
        import os
        font_paths = [
            '/usr/share/fonts/truetype/chinese/NotoSansSC[wght].ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ]
        import matplotlib.font_manager as fm
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    fm.fontManager.addfont(fp)
                except Exception:
                    pass
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
        taus = res["tau"].values
        # Panel 1: All-pairs
        ax = axes[0, 0]
        ax.plot(taus, res["r_all_orig"], 'o-', label="orig", color="#888")
        ax.plot(taus, res["r_all_v10"], 's-', label="v10 mask", color="#1b9e77")
        ax.axhline(0, color='k', lw=0.5, alpha=0.3)
        ax.set_xlabel("threshold τ (× b_wt)")
        ax.set_ylabel("Pearson r(log10 κ_V, |log2 FC|)")
        ax.set_title(f"All-pairs (n=736)")
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        # Panel 2: Per-gene max ALL 92
        ax = axes[0, 1]
        ax.plot(taus, res["r_gene_all_orig"], 'o-', label="orig", color="#888")
        ax.plot(taus, res["r_gene_all_v10"], 's-', label="v10 mask", color="#7570b3")
        ax.axhline(0, color='k', lw=0.5, alpha=0.3)
        ax.set_xlabel("threshold τ (× b_wt)")
        ax.set_ylabel("Pearson r(log10 max κ_V, max |log2 FC|)")
        ax.set_title(f"Per-gene max (ALL {n_total_genes} genes)")
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        # Panel 3: Per-gene max UNMAPPED-only
        ax = axes[1, 0]
        ax.plot(taus, res["r_gene_unmapped_orig"], 'o-', label="orig (no mask)", color="#888")
        ax.plot(taus, res["r_gene_unmapped_v10"], 's-', label="v10 mask", color="#d95f02")
        ax.axhline(0, color='k', lw=0.5, alpha=0.3)
        ax.set_xlabel("threshold τ (× b_wt)")
        ax.set_ylabel("Pearson r (UNMAPPED-only subset)")
        ax.set_title(f"Per-gene max (UNMAPPED-only, n={n_global})")
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        # Panel 4: n_active_T
        ax = axes[1, 1]
        ax.step(taus, res["n_active_T"], 'o-', where='mid', color="#1b9e77")
        ax.set_xlabel("threshold τ (× b_wt)")
        ax.set_ylabel("# T-points with mask ON (out of 8)")
        ax.set_title("Indicator coverage")
        ax.set_ylim(-0.3, 8.5)
        ax.grid(True, alpha=0.3)
        fig.suptitle("E10 threshold sensitivity: time-level indicator mask 𝟙[Δb(t) > τ·b_wt]",
                     fontsize=12)
        fig.savefig(OUT_DIR / "e10_threshold_sensitivity.png", dpi=140)
        print(f"Wrote: {OUT_DIR}/e10_threshold_sensitivity.png")
    except Exception as e:
        print(f"WARN: plot failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
