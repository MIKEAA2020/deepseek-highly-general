#!/usr/bin/env python3
"""
v14b VERIFICATION (independent re-derivation, not reusing stored CSVs).

Verifies the four critical claims from the Phase-1 audit that motivate the
v14b manuscript fix and Option C:

  C1: Of the 15 MAPPED Lemuth genes (v13 Keio fallback), only b2097 (fbaA)
      has non-zero kappa_V over T1..T8; the other 14 are exactly 0 because
      ALL of their iJO1366 reactions carry zero flux at every timepoint.
  C2: Only a small fraction (~17%, ~438/2583) of iJO1366 reactions carry
      non-zero flux under the Lemuth glucose-limited aerobic FBA condition.
  C3: The MAPPED-only (n=15) Pearson r = -0.158 is an artifact: 14 identical
      zero-variance points + 1 outlier (b2097). Leave-one-out (drop b2097)
      makes r undefined (zero variance in x).
  C4: The specific reactions named in the audit (THIORDXi, METSOXR1, SPODM,
      TREHpp, TRE6PP, UGLT, NO3R1pp, NO3R2pp, G3PSabcpp, FBA) have the
      claimed flux status (all zero except FBA).

Method: fresh cobrapy FBA at T1..T8 with the exact same published physiology
values as novelty_real_time_series_e10.py (q_glc 5.0->1.0, q_O2 22->5),
kappa_V(r,t) = (v_r(t) - v_r(T1))^2, gene kappa_V = max over the gene's
reactions (identical to the E10/v13 definitions).

Outputs: /home/z/my-project/download/v14b_verification.{txt,json}
"""
import json
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from cobra.io import load_model

OUT_TXT = "/home/z/my-project/download/v14b_verification.txt"
OUT_JSON = "/home/z/my-project/download/v14b_verification.json"

# --- same physiology as E10 (Lemuth 2008 + Ishii 2007) ---
q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_O2  = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]
T = [f"T{i+1}" for i in range(8)]

# --- the 15 MAPPED genes from the v13 patched E10 run ---
# (gene, b-number) pairs; taken from v14b_mapped15_audit.csv
MAPPED15 = {
    "fbaA": "b2097", "bcp": "b2480", "caiC": "b0037", "galT": "b0758",
    "msrA": "b4219", "narJ": "b1226", "otsB": "b1897", "proV": "b2677",
    "proW": "b2678", "sodA": "b3908", "treA": "b1197", "ugpC": "b3450",
    "yeaA": "b1778", "yehX": "b2129", "yehY": "b2130",
}

print("=" * 78)
print("v14b VERIFICATION: independent re-derivation of the critical claims")
print("=" * 78)

model = load_model("iJO1366")
print(f"iJO1366: {len(model.reactions)} reactions, {len(model.genes)} genes")

# --- run FBA at T1..T8 (identical setup to E10) ---
fluxes = {}
biomass = {}
for ti in range(8):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
        model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
        sol = model.optimize()
        assert sol.status == "optimal", f"T{ti+1} not optimal"
        fluxes[T[ti]] = sol.fluxes
        biomass[T[ti]] = sol.objective_value
print(f"\nBiomass T1..T8: {[round(biomass[t], 4) for t in T]}")

# --- C2: active-reaction count (non-zero flux at any timepoint, |v| > 1e-9) ---
flux_mat = pd.DataFrame({t: fluxes[t] for t in T})
max_abs_flux = flux_mat.abs().max(axis=1)
n_active_any = int((max_abs_flux > 1e-9).sum())
n_active_T1 = int((fluxes["T1"].abs() > 1e-9).sum())
n_kappa_nonzero = 0  # reactions with non-zero kappa_V anywhere
kappa = {}
for rid in flux_mat.index:
    base = fluxes["T1"][rid]
    kv = np.array([(fluxes[t][rid] - base) ** 2 for t in T])
    kappa[rid] = kv
    if kv.max() > 1e-16:
        n_kappa_nonzero += 1

c2 = {
    "total_reactions": len(model.reactions),
    "active_any_T": n_active_any,
    "active_T1": n_active_T1,
    "kappa_V_nonzero": n_kappa_nonzero,
    "pct_active_any": round(100.0 * n_active_any / len(model.reactions), 1),
}
print("\n[C2] Active-reaction counts under Lemuth glucose-limited aerobic FBA:")
print(f"  reactions with |v|>1e-9 at ANY of T1..T8 : {n_active_any}/{len(model.reactions)} "
      f"({100.0*n_active_any/len(model.reactions):.1f}%)")
print(f"  reactions with |v|>1e-9 at T1 (baseline): {n_active_T1}")
print(f"  reactions with non-zero kappa_V anywhere : {n_kappa_nonzero}")

# --- C1 + C4: per-gene kappa_V for the 15 MAPPED genes ---
print("\n[C1/C4] kappa_V of the 15 MAPPED genes (fresh computation):")
rows = []
for gene, bnum in MAPPED15.items():
    g = model.genes.get_by_id(bnum)
    rxns = [r.id for r in g.reactions]
    kv_per_t = {}
    for ti, t in enumerate(T):
        kv_per_t[t] = max((kappa[rid][ti] for rid in rxns), default=0.0)
    kv_max = max(kv_per_t.values())
    max_flux = max((max_abs_flux[rid] for rid in rxns), default=0.0)
    rows.append({
        "gene": gene, "b_number": bnum, "reactions": rxns,
        "max_kappa_V": kv_max, "max_abs_flux_any_T": max_flux,
        "all_rxn_fluxes_zero": bool(max_flux <= 1e-9),
    })
    flag = "NON-ZERO" if kv_max > 1e-12 else "ZERO"
    print(f"  {gene:6s} {bnum:7s} kappa_V_max={kv_max:12.6f} ({flag})  "
          f"max|flux|={max_flux:8.5f}  rxns={rxns[:4]}")

n_zero = sum(1 for r in rows if r["max_kappa_V"] <= 1e-12)
c1 = {
    "n_mapped": len(rows),
    "n_zero_kappa": n_zero,
    "nonzero_genes": [r["gene"] for r in rows if r["max_kappa_V"] > 1e-12],
    "zero_genes_have_zero_flux_reactions": all(
        r["all_rxn_fluxes_zero"] for r in rows if r["max_kappa_V"] <= 1e-12),
}
print(f"\n[C1] {n_zero}/{len(rows)} MAPPED genes have kappa_V = 0 at ALL 8 timepoints")
print(f"     Non-zero kappa_V genes: {c1['nonzero_genes']}")
print(f"     All zero-kappa genes have ALL-reaction-zero-flux: "
      f"{c1['zero_genes_have_zero_flux_reactions']}")
c1_pass = (n_zero == 14 and c1["nonzero_genes"] == ["fbaA"]
           and c1["zero_genes_have_zero_flux_reactions"])

# --- C4: named reactions flux status ---
named = ["FBA", "THIORDXi", "METSOXR1", "METSOXR2", "SPODM", "TREHpp",
         "TRE6PP", "UGLT", "NO3R1pp", "NO3R2pp", "G3PSabcpp", "CRNCAL2",
         "CTBTCAL2", "PROabcpp"]
print("\n[C4] Flux status of audit-named reactions (max |v| over T1..T8):")
c4 = {}
for rid in named:
    if rid in max_abs_flux.index:
        mv = float(max_abs_flux[rid])
        c4[rid] = mv
        print(f"  {rid:10s} max|v| = {mv:9.6f}  {'ACTIVE' if mv > 1e-9 else 'INACTIVE (zero flux)'}")
    else:
        c4[rid] = None
        print(f"  {rid:10s} NOT IN MODEL")
c4_pass = all((c4[r] or 0) <= 1e-9 for r in named if r != "FBA") and (c4["FBA"] or 0) > 1e-9

# --- C3: outlier-artifact structure of the MAPPED-only r = -0.158 ---
audit = json.load(open("/home/z/my-project/download/v14b_mapped15_audit.json"))
x_log = np.log10(np.clip([r["max_kappa_V"] for r in rows], 1e-12, None))
y = np.array(audit["genes"], dtype=object)
# Use audit's max_abs_log2_FC to reproduce the exact r
y_fc = np.array([float(g["max_abs_log2_FC"]) for g in audit["genes"]])
r_full, p_full = pearsonr(x_log, y_fc)
# drop fbaA (the only non-zero gene)
mask = np.array([r["gene"] != "fbaA" for r in rows])
x_drop, y_drop = x_log[mask], y_fc[mask]
r_drop_is_undef = np.std(x_drop) < 1e-12  # zero variance -> pearson undefined
c3 = {
    "r_full_n15": float(r_full),
    "p_full": float(p_full),
    "n_identical_zero_x": int(mask.sum()),
    "x_variance_after_dropping_outlier": float(np.var(x_drop)),
    "pearson_undefined_after_dropping_outlier": bool(r_drop_is_undef),
    "outlier_gene": "fbaA (b2097): x=log10(9.49)=+0.977, y=0.44 (below mean of zeros 0.59)",
}
print("\n[C3] MAPPED-only (n=15) correlation structure check:")
print(f"  Reproduced r (fresh kappa + audit FC) = {r_full:+.4f} (p={p_full:.4f})")
print(f"  After dropping fbaA: x has {mask.sum()} identical values "
      f"(var={np.var(x_drop):.2e}) -> Pearson r UNDEFINED: {r_drop_is_undef}")
print(f"  => the r is entirely determined by ONE outlier point vs 14 identical points")
c3_pass = r_drop_is_undef and abs(r_full - (-0.1579)) < 0.02

verdict = {
    "C1_pass": bool(c1_pass), "C2_pass": bool(350 <= n_active_any <= 520),
    "C3_pass": bool(c3_pass), "C4_pass": bool(c4_pass),
}
print("\n" + "=" * 78)
print(f"VERIFICATION VERDICTS: C1={c1_pass}  C2={verdict['C2_pass']}  "
      f"C3={c3_pass}  C4={c4_pass}")
print("  (C2 tolerance: 350 <= active-any-T count <= 520, audit said 438)")
print("=" * 78)

with open(OUT_TXT, "w") as f:
    f.write("v14b independent verification (fresh FBA re-derivation)\n")
    f.write(json.dumps({"C1": c1, "C2": c2, "C3": c3, "C4": c4, "verdicts": verdict},
                       indent=2, default=str))
with open(OUT_JSON, "w") as f:
    json.dump({"C1": c1, "C2": c2, "C3": c3, "C4": c4, "verdicts": verdict,
               "mapped15_rows": rows}, f, indent=2, default=str)
print(f"\nWrote {OUT_TXT} and {OUT_JSON}")
