#!/usr/bin/env python3
"""E24 pre-analysis 2: enumerate M3D experiment names and perturbation
features to identify condition-matched experiment groups."""
import pandas as pd
from collections import Counter

BASE = "/home/z/my-project/data/m3d/E_coli_v4_Build_6"

feat = pd.read_csv(f"{BASE}/E_coli_v4_Build_6.experiment_feature_descriptions",
                   sep="\t", low_memory=False)
feat["feature_name"] = feat["feature_name"].astype(str)
feat["value"] = feat["value"].astype(str)
exp = pd.read_csv(f"{BASE}/E_coli_v4_Build_6.experiment_descriptions", sep="\t")

names = exp["experiment_name"].unique()

# M3D naming: {condition}_{treatment}_{series}_{rep}; group by first token
prefixes = Counter()
for n in names:
    p = n.split("_")[0]
    prefixes[p] += 1

print("=== top-60 experiment-name prefixes ===")
for p, c in prefixes.most_common(60):
    print(f"{p:30s} {c}")

print()
print("=== perturbation feature values (top 40) ===")
pert = feat[feat["feature_name"] == "perturbation"]
print(pert["value"].value_counts().head(40).to_string())

print()
print("=== strain values (top 15) ===")
print(feat[feat["feature_name"] == "strain"]["value"]
      .value_counts().head(15).to_string())

print()
print("=== growth_phase values ===")
print(feat[feat["feature_name"] == "growth_phase"]["value"]
      .value_counts().head(15).to_string())

print()
print("=== experiments with anaerobic aeration ===")
ana = feat[(feat["feature_name"] == "aeration") &
           (feat["value"].str.contains("anaerobic", na=False))]
print("n exps:", ana["experiment_name"].nunique())
print(sorted(ana["experiment_name"].unique())[:40])

print()
print("=== fed-batch experiments ===")
fb = feat[(feat["feature_name"] == "culture_type") &
          (feat["value"].str.contains("fed_batch", na=False))]
print(sorted(fb["experiment_name"].unique()))

print()
print("=== glycerol experiments ===")
gly = feat[(feat["feature_name"] == "glycerol")]
print(sorted(gly["experiment_name"].unique()))

print()
print("=== experiments whose name mentions key conditions ===")
for kw in ["galact", "trehal", "proline", "osmo", "salt", "NaCl",
           "oxidat", "peroxide", "paraquat", "nitrate", "anaerob",
           "starv", "statio", "glucose", "limit", "nutri", "carbon"]:
    hits = sorted(n for n in names if kw.lower() in n.lower())
    print(f"--- {kw}: {len(hits)}")
    print("   ", hits[:14])
