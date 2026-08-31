#!/usr/bin/env python3
"""
Compare v10 indicator-mask correlation on:
  (A) ORIGINAL E10 CSV (1 MAPPED + 91 GLOBAL, backup at novelty_real_time_series_e10_v1_backup.csv)
  (B) PATCHED E10 CSV  (15 MAPPED + 77 GLOBAL, current at novelty_real_time_series_e10.csv)

For each CSV, compute:
  1. Pearson r(log10 κ_V_orig, |log2 FC|) over all 736 gene-T pairs
  2. Pearson r(log10 max κ_V_orig, max |log2 FC|) per-gene max over all 92 genes
  3. Same with v10 time-level mask applied (kV_v10 = κ_V_orig * indicator_T,
     indicator_T = 𝟙[Δb(t) > 0.05 * b_wt])
  4. Per-gene max on MAPPED-only subset
  5. Per-gene max on GLOBAL-only subset (may be NaN if constant vector)

Outputs:
  /home/z/my-project/download/e10_v10_orig_vs_patched_comparison.{csv,txt,json}
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

DOWNLOAD = Path("/tmp/my-project/download")
ORIG_CSV = DOWNLOAD / "novelty_real_time_series_e10_v1_backup.csv"
NEW_CSV = DOWNLOAD / "novelty_real_time_series_e10.csv"
JSON_IN = DOWNLOAD / "novelty_real_time_series_e10_results.json"

OUT_CSV = Path("/home/z/my-project/download/e10_v10_orig_vs_patched_comparison.csv")
OUT_TXT = Path("/home/z/my-project/download/e10_v10_orig_vs_patched_comparison.txt")
OUT_JSON = Path("/home/z/my-project/download/e10_v10_orig_vs_patched_comparison.json")


def _safe_log10(x, eps=1e-12):
    return np.log10(np.where(x > 0, x, eps))


def _pearson(x, y):
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3 or np.std(x[mask]) < 1e-15 or np.std(y[mask]) < 1e-15:
        return float("nan"), float("nan")
    r, p = pearsonr(x[mask], y[mask])
    return float(r), float(p)


def _spearman(x, y):
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3 or np.std(x[mask]) < 1e-15 or np.std(y[mask]) < 1e-15:
        return float("nan"), float("nan")
    rho, p = spearmanr(x[mask], y[mask])
    return float(rho), float(p)


def compute_metrics(csv_path: Path, j: dict, label: str) -> dict:
    df = pd.read_csv(csv_path)
    bio_per_T = j["iJO1366"]["biomass_per_T"]
    b_wt = j["iJO1366"]["baseline_biomass_T1"]
    delta_b_per_T = {t: b_wt - bio for t, bio in bio_per_T.items()}
    # v10 time-level mask (threshold = 0.05 * b_wt)
    indicator_T = {t: float(delta_b_per_T[t] > 0.05 * b_wt) for t in bio_per_T}
    df = df.copy()
    df["indicator_T"] = df["time_point"].map(indicator_T)
    df["kV_v10"] = df["kappa_V_predicted"] * df["indicator_T"]
    # All-pairs correlations
    x_orig = df["kappa_V_predicted"].values.astype(float)
    x_v10 = df["kV_v10"].values.astype(float)
    y = df["abs_log2_FC"].values.astype(float)
    r_all_orig, _ = _pearson(_safe_log10(x_orig), y)
    r_all_v10, _ = _pearson(_safe_log10(x_v10), y)
    rho_all_orig, _ = _spearman(x_orig, y)
    rho_all_v10, _ = _spearman(x_v10, y)
    # Per-gene max — ALL genes
    gmax_orig = df.groupby("gene")["kappa_V_predicted"].max()
    gmax_v10 = df.groupby("gene")["kV_v10"].max()
    gmax_fc = df.groupby("gene")["abs_log2_FC"].max()
    r_g_orig, _ = _pearson(_safe_log10(gmax_orig.values), gmax_fc.values)
    r_g_v10, _ = _pearson(_safe_log10(gmax_v10.values), gmax_fc.values)
    rho_g_orig, _ = _spearman(gmax_orig.values, gmax_fc.values)
    rho_g_v10, _ = _spearman(gmax_v10.values, gmax_fc.values)
    # Per-gene max on MAPPED-only subset
    df_mapped = df[df["mapping_status"].str.startswith("MAPPED")]
    n_mapped = df_mapped["gene"].nunique()
    if n_mapped >= 3:
        gmax_orig_m = df_mapped.groupby("gene")["kappa_V_predicted"].max()
        gmax_v10_m = df_mapped.groupby("gene")["kV_v10"].max()
        gmax_fc_m = df_mapped.groupby("gene")["abs_log2_FC"].max()
        r_gm_orig, _ = _pearson(_safe_log10(gmax_orig_m.values), gmax_fc_m.values)
        r_gm_v10, _ = _pearson(_safe_log10(gmax_v10_m.values), gmax_fc_m.values)
        rho_gm_orig, _ = _spearman(gmax_orig_m.values, gmax_fc_m.values)
        rho_gm_v10, _ = _spearman(gmax_v10_m.values, gmax_fc_m.values)
    else:
        r_gm_orig = r_gm_v10 = rho_gm_orig = rho_gm_v10 = float("nan")
    # Per-gene max on GLOBAL-only subset
    df_global = df[~df["mapping_status"].str.startswith("MAPPED")]
    n_global = df_global["gene"].nunique()
    gmax_orig_g = df_global.groupby("gene")["kappa_V_predicted"].max()
    gmax_v10_g = df_global.groupby("gene")["kV_v10"].max()
    gmax_fc_g = df_global.groupby("gene")["abs_log2_FC"].max()
    r_gg_orig, _ = _pearson(_safe_log10(gmax_orig_g.values), gmax_fc_g.values)
    r_gg_v10, _ = _pearson(_safe_log10(gmax_v10_g.values), gmax_fc_g.values)
    rho_gg_orig, _ = _spearman(gmax_orig_g.values, gmax_fc_g.values)
    rho_gg_v10, _ = _spearman(gmax_v10_g.values, gmax_fc_g.values)
    return {
        "label": label,
        "csv_path": str(csv_path),
        "n_genes": int(df["gene"].nunique()),
        "n_mapped": int(n_mapped),
        "n_global": int(n_global),
        "indicator_T_at_0.05": {t: int(indicator_T[t]) for t in sorted(indicator_T)},
        "r_all_pairs_orig": r_all_orig,
        "r_all_pairs_v10": r_all_v10,
        "delta_r_all_pairs": r_all_v10 - r_all_orig,
        "rho_all_pairs_orig": rho_all_orig,
        "rho_all_pairs_v10": rho_all_v10,
        "r_per_gene_max_all_orig": r_g_orig,
        "r_per_gene_max_all_v10": r_g_v10,
        "delta_r_per_gene_max_all": r_g_v10 - r_g_orig,
        "rho_per_gene_max_all_orig": rho_g_orig,
        "rho_per_gene_max_all_v10": rho_g_v10,
        "r_per_gene_max_MAPPED_orig": r_gm_orig,
        "r_per_gene_max_MAPPED_v10": r_gm_v10,
        "rho_per_gene_max_MAPPED_orig": rho_gm_orig,
        "rho_per_gene_max_MAPPED_v10": rho_gm_v10,
        "r_per_gene_max_GLOBAL_orig": r_gg_orig,
        "r_per_gene_max_GLOBAL_v10": r_gg_v10,
        "rho_per_gene_max_GLOBAL_orig": rho_gg_orig,
        "rho_per_gene_max_GLOBAL_v10": rho_gg_v10,
    }


def main():
    if not ORIG_CSV.exists():
        print(f"ERROR: backup CSV not found at {ORIG_CSV}", file=sys.stderr)
        return 2
    if not NEW_CSV.exists():
        print(f"ERROR: patched CSV not found at {NEW_CSV}", file=sys.stderr)
        return 2
    with JSON_IN.open() as f:
        j = json.load(f)
    print("=" * 78)
    print("v10 indicator-mask correlation: ORIGINAL (1 MAPPED) vs PATCHED (15 MAPPED)")
    print("=" * 78)
    orig = compute_metrics(ORIG_CSV, j, "ORIGINAL (1 MAPPED + 91 GLOBAL)")
    new = compute_metrics(NEW_CSV, j, "PATCHED (15 MAPPED + 77 GLOBAL)")
    rows = [orig, new]
    res = pd.DataFrame(rows)
    # Print summary
    print(f"\n{'metric':50s} {'ORIGINAL':>14s} {'PATCHED':>14s} {'Δ (P-O)':>14s}")
    print(f"{'-'*50} {'-'*14} {'-'*14} {'-'*14}")
    metrics = [
        ("n_genes", orig["n_genes"], new["n_genes"]),
        ("n_mapped", orig["n_mapped"], new["n_mapped"]),
        ("n_global", orig["n_global"], new["n_global"]),
        ("r_all_pairs_orig (no mask)", orig["r_all_pairs_orig"], new["r_all_pairs_orig"]),
        ("r_all_pairs_v10 (with mask)", orig["r_all_pairs_v10"], new["r_all_pairs_v10"]),
        ("rho_all_pairs_orig", orig["rho_all_pairs_orig"], new["rho_all_pairs_orig"]),
        ("rho_all_pairs_v10", orig["rho_all_pairs_v10"], new["rho_all_pairs_v10"]),
        ("r_per_gene_max_ALL_orig", orig["r_per_gene_max_all_orig"], new["r_per_gene_max_all_orig"]),
        ("r_per_gene_max_ALL_v10", orig["r_per_gene_max_all_v10"], new["r_per_gene_max_all_v10"]),
        ("rho_per_gene_max_ALL_orig", orig["rho_per_gene_max_all_orig"], new["rho_per_gene_max_all_orig"]),
        ("rho_per_gene_max_ALL_v10", orig["rho_per_gene_max_all_v10"], new["rho_per_gene_max_all_v10"]),
        ("r_per_gene_max_MAPPED_orig", orig["r_per_gene_max_MAPPED_orig"], new["r_per_gene_max_MAPPED_orig"]),
        ("r_per_gene_max_MAPPED_v10", orig["r_per_gene_max_MAPPED_v10"], new["r_per_gene_max_MAPPED_v10"]),
        ("r_per_gene_max_GLOBAL_orig", orig["r_per_gene_max_GLOBAL_orig"], new["r_per_gene_max_GLOBAL_orig"]),
        ("r_per_gene_max_GLOBAL_v10", orig["r_per_gene_max_GLOBAL_v10"], new["r_per_gene_max_GLOBAL_v10"]),
    ]
    for name, o, n in metrics:
        if isinstance(o, (int, float)) and isinstance(n, (int, float)):
            delta = n - o
            print(f"  {name:48s} {o:>+14.4f} {n:>+14.4f} {delta:>+14.4f}")
        else:
            print(f"  {name:48s} {o:>14} {n:>14} {'':>14}")
    # Save outputs
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(OUT_CSV, index=False)
    with OUT_TXT.open("w") as f:
        f.write("v10 indicator-mask correlation comparison\n")
        f.write("ORIGINAL = E10 with 1 MAPPED (b2097) + 91 GLOBAL\n")
        f.write("PATCHED  = E10 with 15 MAPPED (1 + 14 via Keio fallback) + 77 GLOBAL\n")
        f.write("v10 time-level mask: indicator_T = 1[Δb(t) > 0.05 * b_wt]; b_wt = 0.4847\n")
        f.write("indicator_T vector (T1..T8): " + str(orig["indicator_T_at_0.05"]) + "\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'metric':48s} {'ORIGINAL':>14s} {'PATCHED':>14s} {'Δ':>14s}\n")
        f.write("-" * 80 + "\n")
        for name, o, n in metrics:
            if isinstance(o, (int, float)) and isinstance(n, (int, float)):
                delta = n - o
                f.write(f"  {name:46s} {o:>+14.4f} {n:>+14.4f} {delta:>+14.4f}\n")
            else:
                f.write(f"  {name:46s} {o:>14} {n:>14}\n")
        f.write("\n")
        f.write("Note: per_gene_max_GLOBAL on ORIGINAL subset (n=91) returns NaN\n")
        f.write("  because all 91 unmapped genes share the identical global-biomass-deficit^2\n")
        f.write("  κ_V trajectory. After max-over-T, all 91 values are equal -> constant\n")
        f.write("  vector -> Pearson/Spearman undefined.\n")
        f.write("Note: per_gene_max_GLOBAL on PATCHED subset (n=77) may also be NaN\n")
        f.write("  for the same reason (the remaining 77 genes still all share the global\n")
        f.write("  biomass-deficit^2 κ_V trajectory).\n")
    # JSON
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
    OUT_JSON.write_text(json.dumps(_clean({
        "b_wt_T1": j["iJO1366"]["baseline_biomass_T1"],
        "biomass_per_T": j["iJO1366"]["biomass_per_T"],
        "delta_b_per_T": {t: j["iJO1366"]["baseline_biomass_T1"] - bio
                          for t, bio in j["iJO1366"]["biomass_per_T"].items()},
        "indicator_T_at_0.05": {t: int(v) for t, v in orig["indicator_T_at_0.05"].items()},
        "original": orig,
        "patched": new,
    }), indent=2))
    print(f"\nWrote: {OUT_CSV}")
    print(f"Wrote: {OUT_TXT}")
    print(f"Wrote: {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
