#!/usr/bin/env python3
"""
Phase 1 verification: enumerate the 15 mapped metabolic genes from the v13
patched E10 CSV, and pull their κ_V trajectories, per-gene max Δb, max
|log2 FC|, mapping status (which iJO1366 reactions), and check basic
biological sanity for the post-translational-regulation hypothesis.

Outputs:
  /home/z/my-project/download/v14b_mapped15_audit.{csv,txt,json}
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

PATCHED_CSV = Path("/tmp/my-project/download/novelty_real_time_series_e10.csv")
PATCHED_JSON = Path("/tmp/my-project/download/novelty_real_time_series_e10_results.json")
OUT_CSV  = Path("/home/z/my-project/download/v14b_mapped15_audit.csv")
OUT_TXT  = Path("/home/z/my-project/download/v14b_mapped15_audit.txt")
OUT_JSON = Path("/home/z/my-project/download/v14b_mapped15_audit.json")

print("Loading patched E10 CSV (15 MAPPED + 77 GLOBAL)...")
df = pd.read_csv(PATCHED_CSV)
print(f"  rows: {len(df)}, genes: {df.gene.nunique()}")
print(f"  MAPPED genes: {df[df.mapping_status.str.startswith('MAPPED')].gene.nunique()}")
print(f"  GLOBAL genes: {df[~df.mapping_status.str.startswith('MAPPED')].gene.nunique()}")

# Get the 15 MAPPED genes and their mapping details
df_mapped = df[df.mapping_status.str.startswith("MAPPED")].copy()
mapped_summary = (
    df_mapped.groupby("gene")
    .agg(
        b_number=("mapping_status", "first"),
        max_kappa_V=("kappa_V_predicted", "max"),
        max_abs_log2_FC=("abs_log2_FC", "max"),
        n_timepoints=("time_point", "count"),
    )
    .reset_index()
)
# Clean the b_number / reaction info
def parse_mapping(s):
    # e.g. "MAPPED to b3450 -> ['G3PSabcpp', 'GLYC2Pabcpp'] (via Keio fallback: ugpC -> b3450)"
    # or   "MAPPED to b2097 -> ['FBA']"
    parts = s.split("->")
    bnum_part = parts[0].strip().replace("MAPPED to ", "")
    rxns_part = parts[1].split("(")[0].strip() if len(parts) > 1 else ""
    fallback = "(via Keio fallback" in s
    return bnum_part, rxns_part, fallback

mapped_summary[["b_number", "reactions", "via_keio_fallback"]] = (
    mapped_summary["b_number"].apply(lambda s: pd.Series(parse_mapping(s)))
)
print("\nThe 15 MAPPED metabolic genes (from v13 patched E10):")
print(mapped_summary[["gene", "b_number", "reactions", "via_keio_fallback", "max_kappa_V", "max_abs_log2_FC"]].to_string(index=False))

# Compute the per-gene-max Pearson r on n=15 subset
x = np.log10(mapped_summary["max_kappa_V"].values.astype(float).clip(min=1e-12))
y = mapped_summary["max_abs_log2_FC"].values.astype(float)
r, p = pearsonr(x, y)
rho, p_rho = spearmanr(x, y)
print(f"\nMAPPED-only (n=15) per-gene-max Pearson r = {r:+.4f} (p={p:.4f})")
print(f"MAPPED-only (n=15) per-gene-max Spearman ρ = {rho:+.4f} (p={p_rho:.4f})")

# Fisher-z 95% CI
def fisher_z_ci(r, n, alpha=0.05):
    if abs(r) >= 1: return float("nan"), float("nan")
    z = 0.5 * np.log((1 + r) / (1 - r))
    se = 1.0 / np.sqrt(n - 3)
    from scipy.stats import norm
    zlo = z - norm.ppf(1 - alpha/2) * se
    zhi = z + norm.ppf(1 - alpha/2) * se
    rlo = (np.exp(2 * zlo) - 1) / (np.exp(2 * zlo) + 1)
    rhi = (np.exp(2 * zhi) - 1) / (np.exp(2 * zhi) + 1)
    return float(rlo), float(rhi)
lo, hi = fisher_z_ci(r, len(mapped_summary))
print(f"  95% CI: [{lo:+.4f}, {hi:+.4f}]")

# Also break out the per-gene full 8-timepoint κ_V trajectories and FC trajectories
print("\nPer-gene 8-timepoint trajectories (κ_V, |log2 FC|):")
for gene in mapped_summary["gene"]:
    sub = df_mapped[df_mapped.gene == gene].sort_values("time_point")
    kV = sub.kappa_V_predicted.values
    fc = sub.abs_log2_FC.values
    bnum = mapped_summary[mapped_summary.gene == gene].b_number.values[0]
    rxns = mapped_summary[mapped_summary.gene == gene].reactions.values[0]
    print(f"  {gene:6s} ({bnum:7s}) {rxns:50s}")
    print(f"    κ_V (T1..T8): {np.array2string(kV, precision=4, separator=', ')}")
    print(f"    |FC| (T1..T8): {np.array2string(fc, precision=3, separator=', ')}")

# Save
mapped_summary.to_csv(OUT_CSV, index=False)
with open(OUT_TXT, "w") as f:
    f.write(f"MAPPED-only (n=15) per-gene-max Pearson r = {r:+.4f} (p={p:.4f})\n")
    f.write(f"MAPPED-only (n=15) per-gene-max Spearman ρ = {rho:+.4f} (p={p_rho:.4f})\n")
    f.write(f"95% CI: [{lo:+.4f}, {hi:+.4f}]\n\n")
    f.write(mapped_summary[["gene", "b_number", "reactions", "via_keio_fallback", "max_kappa_V", "max_abs_log2_FC"]].to_string(index=False))
with open(OUT_JSON, "w") as f:
    json.dump({
        "n_mapped": int(len(mapped_summary)),
        "pearson_r": float(r),
        "pearson_p": float(p),
        "spearman_rho": float(rho),
        "spearman_p": float(p_rho),
        "ci_95": [float(lo), float(hi)],
        "genes": mapped_summary.to_dict(orient="records"),
    }, f, indent=2, default=str)
print(f"\nWrote: {OUT_CSV}\nWrote: {OUT_TXT}\nWrote: {OUT_JSON}")
