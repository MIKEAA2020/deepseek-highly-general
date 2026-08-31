#!/usr/bin/env python3
"""E24 pre-analysis 4: verify remaining contrast details in M3D + PRECISE
data formats, probe->b-number uniqueness, and panel coverage."""
import pandas as pd

M3D = "/home/z/my-project/data/m3d/E_coli_v4_Build_6"
PREC = "/home/z/my-project/data/precise"

exp = pd.read_csv(f"{M3D}/E_coli_v4_Build_6.experiment_descriptions", sep="\t")
feat = pd.read_csv(f"{M3D}/E_coli_v4_Build_6.experiment_feature_descriptions",
                   sep="\t", low_memory=False)
feat["feature_name"] = feat["feature_name"].astype(str)
feat["value"] = feat["value"].astype(str)
names = set(exp["experiment_name"].unique())

print("=== M9_* experiments (Covert series) ===")
print(sorted(n for n in names if n.startswith("M9_")))
print()
print("=== fnr_* / kang series ===")
print(sorted(n for n in names if n.startswith("fnr_")))
print()
print("=== biofilm_* ===")
print(sorted(n for n in names if n.startswith("biofilm_")))

# cybr details
byexp = {}
for en, grp in feat.groupby("experiment_name"):
    byexp[en] = dict(zip(grp["feature_name"], grp["value"]))
print()
print("=== cybr series details ===")
for n in ["cybr_N", "cybr_O", "cybr_N_log", "cybr_N_stat", "cybr_O_log",
          "cybr_O_stat"]:
    f = byexp.get(n, {})
    keys = ["strain", "aeration", "glucose", "growth_phase", "time_point",
            "culture_type", "experimenter", "note", "note2",
            "ammonium_chloride", "limitation"]
    print(f"-- {n}: chips={exp[exp['experiment_name']==n]['chip_name'].tolist()}")
    for k in keys:
        if k in f and str(f[k]).strip() not in ("", "nan"):
            print(f"     {k}: {str(f[k])[:150]}")

# probe uniqueness
psd = pd.read_csv(f"{M3D}/E_coli_v4_Build_6.probe_set_descriptions", sep="\t")
print()
print("=== probe_set_descriptions ===")
print("rows:", len(psd), "unique locus:", psd["locus"].nunique())
dup = psd[psd["locus"].duplicated(keep=False)].sort_values("locus")
print("loci with >1 probe set:", dup["locus"].nunique())
print(dup.head(8).to_string())

# E22 panel coverage
e22 = pd.read_csv("/home/z/my-project/download/"
                  "novelty_v15_reaction_sampling_e22.csv")
panel = set(e22["gene_bnumber"])
m3d_genes = set(psd["locus"].dropna().astype(str))
print()
print("=== E22 panel coverage in M3D ===")
print("panel:", len(panel), "| in M3D:", len(panel & m3d_genes),
      "| missing:", sorted(panel - m3d_genes)[:10])

# Expression matrix format
print()
print("=== M3D expression matrix header ===")
with open(f"{M3D}/E_coli_v4_Build_6_chips907probes4297.tab") as fh:
    head = fh.readline().rstrip("\n").split("\t")
print("cols:", len(head), "first 5:", head[:5])
print("row count check: 4297 probes + header expected")

# PRECISE details
print()
print("=== PRECISE KNO3 / galactose / oxidative samples ===")
md = pd.read_csv(f"{PREC}/data/metadata.csv")
kno3 = md[md["Electron Acceptor"].astype(str).str.contains("KNO3", na=False)]
print(kno3[["Sample ID", "Study", "Condition ID", "Carbon Source (g/L)",
            "Culture Type", "Growth Rate (1/hr)"]].to_string())
gal = md[md["Carbon Source (g/L)"].astype(str).str.contains("galactose", na=False)]
print(gal[["Sample ID", "Study", "Condition ID", "Carbon Source (g/L)",
           "Base Media", "Growth Rate (1/hr)"]].to_string())
gly = md[md["Carbon Source (g/L)"].astype(str).str.contains("glycerol", na=False)]
print(gly[["Sample ID", "Study", "Condition ID", "Carbon Source (g/L)",
           "Base Media"]].head(8).to_string())
ox = md[md["Study"] == "Oxidative"]
print(ox[["Sample ID", "Condition ID", "Carbon Source (g/L)",
          "Supplement", "Additional Details"]].to_string())

print()
print("=== PRECISE log_tpm.csv format ===")
lt = pd.read_csv(f"{PREC}/data/log_tpm.csv", index_col=0, nrows=3)
print("shape (first rows):", lt.shape, "| index name:", lt.index.name)
print("sample cols:", list(lt.columns[:4]))
gi = pd.read_csv(f"{PREC}/data/gene_info.csv", index_col=0)
print("gene_info cols:", list(gi.columns), "n:", len(gi))
print(gi.head(3).to_string())
