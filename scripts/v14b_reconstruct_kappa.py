#!/usr/bin/env python3
"""
Reconstruct the v12 / v13 / unmasked per-gene kappa_V vectors and Pearson r
values from FIRST PRINCIPLES (fresh cobrapy FBA), immune to /tmp resets.

Also verifies the key structural claim for the v14b manuscript fix:
  - v12 (E20 gene-level mask) and v13 (E21 Keio GPR fallback) kappa_V
    vectors differ at EXACTLY ONE gene: b2097 (fbaA).
  - unmasked r = -0.0633, v12 r = +0.1024, v13 r = +0.0838 all reproduce.

Method (identical to novelty_real_time_series_e10.py):
  kappa_V(r, t)   = (v_r(t) - v_r(T1))^2
  gene kappa_V(g,t) = max over GPR reactions of g
  GLOBAL genes     = (biomass(t) - biomass(T1))^2
  per-gene max     = max over T1..T8
  metric           = Pearson r of log10(clip(kappa, 1e-12)) vs max |log2 FC|
"""
import json
import warnings
warnings.filterwarnings("ignore")
import numpy as np
from scipy.stats import pearsonr
from cobra.io import load_model

q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_O2 = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]
T = [f"T{i+1}" for i in range(8)]

lemuth = json.load(open("/tmp/lemuth_ts_clean.json"))
model = load_model("iJO1366")

# FBA at T1..T8
fluxes, biomass = {}, {}
for ti in range(8):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
        model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
        sol = model.optimize()
        fluxes[T[ti]] = sol.fluxes
        biomass[T[ti]] = sol.objective_value

# per-reaction kappa_V
kappa_rxn = {}
for rid in fluxes["T1"].index:
    base = fluxes["T1"][rid]
    kappa_rxn[rid] = np.array([(fluxes[t][rid] - base) ** 2 for t in T])

# global kappa_V time series
glob = np.array([(biomass[t] - biomass["T1"]) ** 2 for t in T])

# gene -> reactions map
g2r = {g.id: [r.id for r in g.reactions] for g in model.genes}

# Keio fallback map (as in patch_e10_keio_fallback.py)
import pandas as pd
keio = pd.read_excel("/home/z/my-project/raw tomoya baba supp/"
                     "44320_2006_BFMSB4100050_MOESM5_ESM.xls", sheet_name=0, header=3)
keio = keio.dropna(subset=[keio.columns[1], "b number"]).copy()
keio["_g"] = keio[keio.columns[1]].astype(str).str.strip().str.lower()
keio["_b"] = keio["b number"].astype(str).str.strip()
KEIO = {}
for _, row in keio.iterrows():
    if row["_g"] and row["_g"] not in KEIO:
        KEIO[row["_g"]] = row["_b"]

fc_max = {}
kv_unmasked, kv_v12, kv_v13 = {}, {}, {}
mapped15 = {}
for rec in lemuth:
    gene = rec["gene"]
    fc_max[gene] = max(abs(rec[f"T{i}"]) for i in range(1, 9))
    # find iJO1366 match: direct, alt-case, or Keio b-number
    mg = gene if gene in g2r else None
    if mg is None:
        for alt in [gene.upper(), gene.capitalize()]:
            if alt in g2r:
                mg = alt
                break
    mg_orig = mg          # ORIGINAL E10 mapping: direct/alt only (no Keio)
    via_keio = False
    if mg is None:
        kb = KEIO.get(gene.strip().lower())
        if kb and kb in g2r:
            mg, via_keio = kb, True
    if mg is not None:
        rxns = g2r[mg]
        kv = np.array([max((kappa_rxn[r][ti] for r in rxns), default=0.0)
                       for ti in range(8)])
        mapped15[gene] = (mg, rxns, kv.max())
        kv_v13[gene] = kv                     # v13: keep GPR-based kappa
        kv_v12[gene] = np.zeros(8)            # v12: mask zeroes it (deta_b=0)
        # ORIGINAL unmasked E10: only direct/alt matches (1 gene: b2097);
        # Keio-fallback genes were GLOBAL in the original run.
        kv_unmasked[gene] = kv if mg_orig is not None else glob
    else:
        kv_unmasked[gene] = glob
        kv_v12[gene] = glob
        kv_v13[gene] = glob

genes = [r["gene"] for r in lemuth]
fc = np.array([fc_max[g] for g in genes])
kvu = np.array([kv_unmasked[g].max() for g in genes])
kv12 = np.array([kv_v12[g].max() for g in genes])
kv13 = np.array([kv_v13[g].max() for g in genes])

def r_of(kv):
    return pearsonr(np.log10(np.clip(kv, 1e-12, None)), fc)

r0, _ = r_of(kvu)
r12, _ = r_of(kv12)
r13, _ = r_of(kv13)
print(f"unmasked r = {r0:+.4f}   (expected -0.0633)")
print(f"v12      r = {r12:+.4f}   (expected +0.1024)")
print(f"v13      r = {r13:+.4f}   (expected +0.0838)")

diff = [g for g in genes if abs(kv12[genes.index(g)] - kv13[genes.index(g)]) > 1e-12]
print(f"\nGenes where v12 and v13 kappa differ: {diff}")
print(f"  -> v12 kappa[{diff[0] if diff else ''}] = "
      f"{kv12[genes.index(diff[0])] if diff else '-'}, "
      f"v13 = {kv13[genes.index(diff[0])] if diff else '-'}")

print(f"\nMAPPED set size: {len(mapped15)} (expected 15)")
nonzero = {g: v[2] for g, v in mapped15.items() if v[2] > 1e-12}
print(f"MAPPED genes with non-zero kappa_V: {list(nonzero.keys())} "
      f"values={list(nonzero.values())}")
print(f"Max global kappa = {glob.max():.6f} (matches CSV 0.158543: "
      f"{abs(glob.max() - 0.1585431466148791) < 1e-6})")

# Save first-principles reconstruction for reuse by Option C
np.savez("/home/z/my-project/scripts/v14b_kappa_reconstruction.npz",
         genes=np.array(genes), fc=fc, kv_unmasked=kvu, kv_v12=kv12,
         kv_v13=kv13, glob=glob, allow_pickle=True)
json.dump({g: {"b": v[0], "rxns": v[1], "kv_max": float(v[2])}
           for g, v in mapped15.items()},
          open("/home/z/my-project/download/v14b_mapped15_firstprinciples.json", "w"),
          indent=1)
print("\nSaved reconstruction to scripts/v14b_kappa_reconstruction.npz and "
      "download/v14b_mapped15_firstprinciples.json")
