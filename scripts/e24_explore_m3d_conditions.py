#!/usr/bin/env python3
"""E24 pre-analysis: explore M3D v4 Build 6 condition space to define
condition classes matched to the E10/E22/E23 FBA designs.

Outputs a summary of available features/classes so the E24 expression
response variables can be defined soundly.
"""
import pandas as pd
from collections import Counter

BASE = "/home/z/my-project/data/m3d/E_coli_v4_Build_6"

feat = pd.read_csv(f"{BASE}/E_coli_v4_Build_6.experiment_feature_descriptions",
                   sep="\t", low_memory=False)
feat["feature_name"] = feat["feature_name"].astype(str)
feat["value"] = feat["value"].astype(str)
feat["feature_type"] = feat["feature_type"].astype(str)
exp = pd.read_csv(f"{BASE}/E_coli_v4_Build_6.experiment_descriptions", sep="\t")

print("experiments:", exp["experiment_name"].nunique(),
      "chips:", len(exp), "features rows:", len(feat))
print("feature names:", feat["feature_name"].nunique())
print()

# What features exist
vc = feat["feature_name"].value_counts()
print("=== top-40 feature names ===")
print(vc.head(40).to_string())

print()
print("=== culture_type ===")
sub = feat[feat["feature_name"] == "culture_type"]
print(sub["value"].value_counts().to_string())

print()
print("=== limitation-type features ===")
for fn in feat["feature_name"].unique():
    if fn == fn and "limit" in str(fn).lower():
        s = feat[feat["feature_name"] == fn]
        print(f"-- {fn}:")
        print(s["value"].value_counts().head(12).to_string())
        print()

print()
print("=== aeration ===")
print(feat[feat["feature_name"] == "aeration"]["value"].value_counts().to_string())

print()
print("=== carbon sources mentioned as features (top 30) ===")
carb = feat[feat["feature_type"] == "real"]
known = {"glucose", "galactose", "glycerol", "trehalose", "proline",
         "glycerol-2-phosphate", "glycerol 2-phosphate", "nitrate",
         "sodium nitrate", "KNO3", "sucrose", "lactose", "pyruvate",
         "acetate", "fructose", "arabinose", "maltose", "ribose",
         "gluconate", "mannitol", "sorbitol", "xylose"}
featn = feat.copy()
featn["fl"] = featn["feature_name"].str.lower()
hits = featn[featn["fl"].isin(known)]
for k, grp in hits.groupby("feature_name"):
    n_exp = grp["experiment_name"].nunique()
    vals = grp["value"].astype(str).unique()[:4]
    print(f"{k:25s} exps={n_exp:4d} values={list(vals)}")

print()
print("=== stress features ===")
stress_kw = ["stress", "shock", "osmotic", "salt", "NaCl", "oxidative",
             "peroxide", "paraquat", "superoxide", "H2O2", "sodium chloride"]
mask = featn["fl"].apply(lambda x: any(k.lower() in str(x).lower() for k in stress_kw))
if mask.any():
    for k, grp in featn[mask].groupby("feature_name"):
        print(f"{k}: exps={grp['experiment_name'].nunique()}, "
              f"values={list(grp['value'].astype(str).unique()[:5])}")

print()
print("=== growth phase / stationary ===")
mask = featn["fl"].apply(lambda x: any(k in str(x).lower() for k in
                         ["phase", "stationary", "time_point", "hour"]))
if mask.any():
    for k, grp in featn[mask].groupby("feature_name"):
        print(f"{k}: exps={grp['experiment_name'].nunique()}")

# Nitrogen-source features (for proline)
print()
print("=== nitrogen source features ===")
mask = featn["fl"].apply(lambda x: "nitrogen" in str(x).lower() or
                         str(x).lower() in {"proline", "nh4cl", "ammonium"})
if mask.any():
    for k, grp in featn[mask].groupby("feature_name"):
        print(f"{k}: exps={grp['experiment_name'].nunique()}, "
              f"values={list(grp['value'].astype(str).unique()[:5])}")

print()
print("=== chemostat experiments: how many, which limitation ===")
chem_exps = set(sub[sub["value"].str.contains("chemostat", case=False, na=False)]
                ["experiment_name"])
print("chemostat experiments:", len(chem_exps))
lim = feat[(feat["feature_name"].str.contains("limitation", case=False, na=False)) &
           (feat["experiment_name"].isin(chem_exps))]
if len(lim):
    for k, grp in lim.groupby("feature_name"):
        print(f"{k}:")
        print(grp["value"].value_counts().head(10).to_string())
