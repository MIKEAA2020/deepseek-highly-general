#!/usr/bin/env python3
"""E24 pre-analysis 3: dump full condition descriptions of candidate
matched-contrast experiments in M3D v4 Build 6."""
import pandas as pd

BASE = "/home/z/my-project/data/m3d/E_coli_v4_Build_6"
exp = pd.read_csv(f"{BASE}/E_coli_v4_Build_6.experiment_descriptions", sep="\t")
feat = pd.read_csv(f"{BASE}/E_coli_v4_Build_6.experiment_feature_descriptions",
                   sep="\t", low_memory=False)
feat["feature_name"] = feat["feature_name"].astype(str)
feat["value"] = feat["value"].astype(str)

# Aggregate per-experiment features into a dict
byexp = {}
for en, grp in feat.groupby("experiment_name"):
    byexp[en] = dict(zip(grp["feature_name"], grp["value"]))

CANDIDATES = [
    "WT_MOPS_glucose", "WT_MOPS_proline", "WT_MOPS_glycerol",
    "WT_MOPS_stationary", "WT_MOPS_stationary2", "WT_MOPS_stationary3",
    "WT_MOPS_stationary4",
    "HU_wt_M9gly_exp", "HU_wt_M9gly_stat", "WT_MOPS_galactose",
    "M9_WT_anaerobic", "fnr_wtAnaerobic", "M9_K_fnr_anaerobic",
    "cybr_N", "cybr_N_log", "cybr_N_stat", "cybr_KNO_N",
    "biofilm_wt_glucose", "biofilm_wt_noGlucose",
    "carbonSourceForaging", "W3110_wt_luxS_glucose",
    "MG1655_t405_aerobic", "MG1655_t150_anaerobic",
    "rb_wt_stationary", "rb_del_rpoS_stationary",
    "WT_MOPS_fumarate", "WT_MOPS_succinate", "WT_MOPS_acetate",
    "WT_MOPS_pyruvate", "WT_MOPS_lactate", "WT_MOPS_galactonate",
]

names = set(exp["experiment_name"].unique())
print("=== all WT_MOPS_* and M9_WT_* experiments ===")
print(sorted(n for n in names if n.startswith("WT_MOPS") or
             (n.startswith("M9_") and "_WT" in n)))
print()
print("=== all cybr_* experiments ===")
print(sorted(n for n in names if n.startswith("cybr")))
print()
print("=== all MG1655_t* experiments ===")
print(sorted(n for n in names if n.startswith("MG1655_t"))[:30])

for name in CANDIDATES:
    if name not in names:
        continue
    row = exp[exp["experiment_name"] == name].iloc[0]
    chips = exp[exp["experiment_name"] == name]["chip_name"].tolist()
    f = byexp.get(name, {})
    print(f"\n### {name}  ({len(chips)} chips: {chips[:6]})")
    keys = ["strain", "culture_type", "aeration", "glucose", "glycerol",
            "proline", "carbon_source", "growth_phase", "time_point",
            "culture_temperature", "limitation", "medium", "note",
            "note2", "description", "perturbation", "experimenter",
            "structured_metadata", "carbonSourceForaging"]
    for k in keys:
        if k in f and str(f[k]).strip() not in ("", "nan"):
            print(f"   {k}: {str(f[k])[:200]}")
    # any feature with interesting names
    extra = [k for k in f if k not in keys and any(
        w in k.lower() for w in ["carbon", "nitrogen", "sodium", "phosph",
        "limit", "phase", "osmo", "ammonium", "casamino", "mops", "yeast"])]
    for k in extra[:12]:
        if str(f[k]).strip() not in ("", "nan"):
            print(f"   {k}: {str(f[k])[:160]}")
    # description first 300 chars
    print(f"   [desc]: {row['description'][:400]}")
