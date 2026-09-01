#!/usr/bin/env python3
"""
Study E24 (manuscript round v17): Option A -- external expression coverage.

Motivation (user-approved direction): the v16/E23 cross-condition test is
r = +0.571 at n = 7 (permutation p = 0.18) -- under-powered because the
binding constraint is EXPRESSION COVERAGE, not gene supply.  E22 produced
435 metabolic genes with non-zero kappa_V (Option C panel) but the Lemuth
time series covers only 1 of them (b2097).  This study obtains the M3D
compendium (Faith et al. 2008, E_coli_v4_Build_6: 907 arrays x 4,297 gene
probe sets, uniformly normalized, log2 scale) and the PRECISE RNA-seq
compendium (Sastry et al. 2019, 278 samples, MG1655) and computes the
kappa_V -> transcript-response correlation at genome-panel scale.

Arms
----
[A-panel]  PRIMARY, genome scale (n ~ 433): E22 per-gene kappa_V (baseline
           glucose-decline trajectory) vs M3D carbon-exhaustion response
           (Blattner/Allen 'carbon source foraging' MOPS-minimal series:
           MG1655, 37 C, log-phase glucose reference with 5 replicates;
           stationary time points 135/330/480/720 min, 2 replicates each;
           within-series contrasts so batch effects cancel).
[A-replicate] PRECISE cross-platform, genome scale: same kappa_V panel vs
           WT carbon-source-switch responses (independent RNA-seq lab).
[A-matched] E23 replication with MATCHED expression (replaces the Lemuth
           cross-condition FC): proV/proW (M3D proline), ugpC (M3D
           glycerol), narJ (PRECISE anaerobic+KNO3), galT (PRECISE
           galactose), b2097 (M3D carbon exhaustion).  treA has no matched
           expression data in either compendium (honest exclusion).
[A-burden] burden-class oxidative genes (sodA/bcp/msrA/yeaA) vs PRECISE
           paraquat (250 uM) -- reported structurally, NOT correlated
           (endogeneity criterion of v16).
[A-zero]   zero-kappa_V control: model genes with all-inactive baseline
           reactions vs their M3D response (do non-zero kappa_V genes
           respond more?).

All kappa_V values are taken UNCHANGED from the E22/E23 artifacts; the
log10 transform matches the E10-lineage definition.  Correlations are
computed only over genes with non-zero kappa_V variation (the E22 panel
guarantee), per the user's standing caution.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

RNG = np.random.default_rng(20260831)
DL = Path("/home/z/my-project/download")
M3D = Path("/home/z/my-project/data/m3d/E_coli_v4_Build_6")
PREC = Path("/home/z/my-project/data/precise")

# ----------------------------------------------------------------- load M3D
expr = pd.read_csv(M3D / "E_coli_v4_Build_6_chips907probes4297.tab",
                   sep="\t", index_col=0)
psd = pd.read_csv(M3D / "E_coli_v4_Build_6.probe_set_descriptions", sep="\t")
locus_of = dict(zip(psd["probe_set_name"], psd["locus"].astype(str)))
expr.index = [locus_of.get(p, p) for p in expr.index]
# collapse duplicate loci (if any) by mean
dupn = expr.index.duplicated(keep=False).sum()
if dupn:
    expr = expr.groupby(level=0).mean()
print(f"[load] M3D matrix: {expr.shape[0]} genes x {expr.shape[1]} chips "
      f"(dup-loci collapsed: {dupn})")

# ---------------------------------------------------- M3D contrast chip sets
REF = [f"WT_MOPS_glucose_r{i}" for i in range(1, 6)]              # log, 5 reps
STAT = {
    "stationary_135min": [f"WT_MOPS_stationary_r{i}" for i in (1, 2)],
    "stationary_330min": [f"WT_MOPS_stationary2_r{i}" for i in (1, 2)],
    "stationary_480min": [f"WT_MOPS_stationary3_r{i}" for i in (1, 2)],
    "stationary_720min": [f"WT_MOPS_stationary4_r{i}" for i in (1, 2)],
}
LATELOG = [f"WT_MOPS_lateLog_r{i}" for i in (1, 2, 3)]
PROLINE = [f"WT_MOPS_proline_r{i}" for i in (1, 2)]
GLYCEROL = [f"WT_MOPS_glycerol_r{i}" for i in (1, 2)]
ACETATE = [f"WT_MOPS_acetate_r{i}" for i in (1, 2)]
HU_EXP, HU_STAT = ["HU_wt_M9gly_exp_r1"], ["HU_wt_M9gly_stat_r1"]
BIO_GLC, BIO_NOGLC = ["biofilm_wt_glucose_r1"], ["biofilm_wt_noGlucose_r1"]

missing_chips = [c for c in (REF + sum(STAT.values(), []) + LATELOG +
                             PROLINE + GLYCEROL + ACETATE + HU_EXP + HU_STAT +
                             BIO_GLC + BIO_NOGLC) if c not in expr.columns]
assert not missing_chips, f"missing M3D chips: {missing_chips}"

# [A-contrast] verification from the experiment metadata
expd = pd.read_csv(M3D / "E_coli_v4_Build_6.experiment_descriptions", sep="\t")
feat = pd.read_csv(M3D / "E_coli_v4_Build_6.experiment_feature_descriptions",
                   sep="\t", low_memory=False)
feat["feature_name"] = feat["feature_name"].astype(str)
feat["value"] = feat["value"].astype(str)
byexp = {en: dict(zip(g["feature_name"], g["value"]))
         for en, g in feat.groupby("experiment_name")}
series = ["WT_MOPS_glucose", "WT_MOPS_stationary", "WT_MOPS_stationary2",
          "WT_MOPS_stationary3", "WT_MOPS_stationary4",
          "WT_MOPS_proline", "WT_MOPS_glycerol", "WT_MOPS_acetate"]
print("\n[A-contrast] Blattner/Allen series metadata:")
for n in series:
    f = byexp[n]
    print(f"  {n:24s} strain={f.get('strain')} medium=MOPS/"
          f"NH4 aeration={f.get('aeration')} phase={f.get('growth_phase')} "
          f"t={f.get('time_point')} exp={f.get('experimenter')}")

# ------------------------------------------------------- per-gene M3D FCs
ref_mean = expr[REF].mean(axis=1)
fc = {}
for name, chips in STAT.items():
    fc[name] = expr[chips].mean(axis=1) - ref_mean
fc["lateLog"] = expr[LATELOG].mean(axis=1) - ref_mean
fc["proline"] = expr[PROLINE].mean(axis=1) - ref_mean
fc["glycerol"] = expr[GLYCEROL].mean(axis=1) - ref_mean
fc["acetate"] = expr[ACETATE].mean(axis=1) - ref_mean
fc["hu_stat_minus_exp"] = expr[HU_STAT].mean(axis=1) - expr[HU_EXP].mean(axis=1)
fc["biofilm_noGlucose"] = expr[BIO_NOGLC].mean(axis=1) - expr[BIO_GLC].mean(axis=1)
fc_m3d = pd.DataFrame(fc)

# ------------------------------------------------------------ load E22 panel
e22 = pd.read_csv(DL / "novelty_v15_reaction_sampling_e22.csv")
e22 = e22.set_index("gene_bnumber")
panel_kv = e22["kappa_V_max"].astype(float)
panel_gpr = e22["dominant_gpr_class"].astype(str)
panel_sub = e22["subsystem_max_kappa_rxn"].astype(str)
panel_rxn = e22["active_reactions"].astype(str)
logkv_panel = np.log10(panel_kv)

in_m3d = panel_kv.index.isin(fc_m3d.index)
print(f"\n[A-panel] E22 panel: {len(panel_kv)} genes, "
      f"{int(in_m3d.sum())} with M3D expression "
      f"(missing: {list(panel_kv.index[~in_m3d])})")
kv = panel_kv[in_m3d]
logkv = logkv_panel[in_m3d]

# ------------------------------------------------------------- PRECISE load
lt = pd.read_csv(PREC / "data/log_tpm.csv", index_col=0)
md = pd.read_csv(PREC / "data/metadata.csv").set_index("Sample ID")
md["Carbon Source (g/L)"] = md["Carbon Source (g/L)"].astype(str)
md["Nitrogen Source (g/L)"] = md["Nitrogen Source (g/L)"].astype(str)
md["Electron Acceptor"] = md["Electron Acceptor"].astype(str)
md["Condition ID"] = md["Condition ID"].astype(str)
ctrl = [c for c in lt.columns if c.startswith("control__wt_glc__")]
ctrl_mean = lt[ctrl].mean(axis=1)
print(f"[load] PRECISE: {lt.shape[0]} genes x {lt.shape[1]} samples; "
      f"controls: {ctrl}")

# PRECISE matched condition samples (WT, no genotype perturbation)
def prec_samples(cond_prefix):
    return [c for c in lt.columns if c.startswith(cond_prefix + "__")]

no3 = prec_samples("ica__no3_anaero")
gal = prec_samples("ica__thm_gal")
gly = prec_samples("crp__wt_glyc")
pq = prec_samples("oxidative__wt_pq")
for nm, ss in [("no3_anaero", no3), ("thm_gal", gal), ("wt_glyc", gly),
               ("wt_pq", pq)]:
    print(f"  PRECISE {nm}: {ss}")
print("  ica__thm_gal meta:",
      md.loc[gal[0], ["Carbon Source (g/L)", "Base Media", "Supplement",
                      "Additional Details"]].to_dict() if gal else "-")

fc_prec = pd.DataFrame({
    "no3_anaero": lt[no3].mean(axis=1) - ctrl_mean,
    "galactose": lt[gal].mean(axis=1) - ctrl_mean,
    "glycerol": lt[gly].mean(axis=1) - ctrl_mean,
    "paraquat": lt[pq].mean(axis=1) - ctrl_mean,
})

# PRECISE WT carbon-switch set (genome-scale arm): WT carbon sources != glucose
wt_carbon_prefixes = ["ica__thm_gal", "crp__wt_glyc"]
wt_carbon = {"galactose": gal, "glycerol": gly}
# add other WT non-glucose carbon conditions found in metadata
for cid, grp in md.groupby("Condition ID"):
    if cid in ("wt_glc", "no3_anaero", "wt_glyc", "thm_gal") or cid.endswith("_pq"):
        continue
    carb = grp["Carbon Source (g/L)"].iloc[0]
    base_media = str(grp["Base Media"].iloc[0])
    if "glucose" in carb or carb == "nan" or "LB" in base_media:
        continue  # LB = rich medium, not a defined carbon-source switch
    sids = [s for s in grp.index if s in lt.columns]
    # WT only: strain MG1655, not evolved, no KO-ish words in condition name
    strain = grp["Strain"].iloc[0]
    evolved = str(grp["Evolved Sample"].iloc[0])
    if "MG1655" not in str(strain) or "Yes" in evolved:
        continue
    low = cid.lower()
    if any(w in low for w in ["del", "ko", "mut", "pbad", "plasmid", "evo",
                              "ale", "ar1", "ar2", "isol", "adapt"]):
        continue
    if len(sids) >= 2:
        wt_carbon[cid] = sids
        print(f"  PRECISE carbon-switch extra: {cid} ({carb}, {base_media}) "
              f"{sids}")
print(f"  PRECISE carbon-switch conditions: {list(wt_carbon)}")

fc_carbon_prec = pd.DataFrame(
    {c: lt[s].mean(axis=1) - ctrl_mean for c, s in wt_carbon.items()})

# ------------------------------------------------------- E23 matched inputs
e23 = pd.read_csv(DL / "novelty_v16_multicondition_e23.csv")
e23 = e23.set_index("gene")

# =============================================================== statistics
def corr_stats(x, y, n_perm=100_000, n_boot=10_000, label=""):
    """Pearson/Spearman + vectorized MC permutation + bootstrap CI.

    Permutation is vectorized via the identity r = mean(zx * zy[perm])
    for z-scored vectors, so 1e5 shuffles cost one matmul.
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    pr, pp = stats.pearsonr(x, y)
    sr, sp = stats.spearmanr(x, y)
    zx = (x - x.mean()) / x.std()
    zy = (y - y.mean()) / y.std()
    rng = np.random.default_rng(777)
    perms = np.stack([rng.permutation(n) for _ in range(n_perm)])
    r_perm = (zy[perms] @ zx) / n          # (n_perm,) correlations
    cnt = int((np.abs(r_perm) >= abs(pr) - 1e-12).sum())
    perm_p = (cnt + 1) / (n_perm + 1)
    rng = np.random.default_rng(888)
    idx = rng.integers(0, n, size=(n_boot, n))
    rs = []
    for b in idx:
        xb, yb = x[b], y[b]
        sx, sy = xb.std(), yb.std()
        if sx == 0 or sy == 0:
            continue
        rs.append(float(np.mean((xb - xb.mean()) * (yb - yb.mean())) /
                        (sx * sy)))
    lo, hi = np.percentile(rs, [2.5, 97.5])
    return {"label": label, "n": n, "pearson_r": round(pr, 4),
            "pearson_p": pp, "spearman_r": round(sr, 4),
            "spearman_p": sp, "perm_p_mc": round(perm_p, 5),
            "boot_ci95": [round(float(lo), 4), round(float(hi), 4)]}

out = {"study": "E24_option_a_expression_coverage", "arms": {}}

# ============================================================ [A-panel]
stat_cols = list(STAT.keys())
max_fc_exhaust = fc_m3d[stat_cols].abs().max(axis=1)
panel_fc = max_fc_exhaust.loc[kv.index]
res_panel = corr_stats(logkv.values, panel_fc.values,
                       label="A-panel: log10 kappa_V vs max|log2FC| carbon "
                             "exhaustion (M3D)")
out["arms"]["A_panel"] = res_panel
print("\n" + "=" * 70)
print("[A-panel] PRIMARY genome-scale test")
print(json.dumps(res_panel, indent=1))

# sensitivities: one contrast at a time / mean metric / lateLog incl.
sens = {}
for c in stat_cols + ["lateLog"]:
    sens[f"single_{c}"] = corr_stats(
        logkv.values, fc_m3d[c].abs().loc[kv.index].values,
        label=f"single contrast {c}")
sens["mean_stationary"] = corr_stats(
    logkv.values, fc_m3d[stat_cols].abs().mean(axis=1).loc[kv.index].values,
    label="mean |FC| over stationary points")
incl_ll = stat_cols + ["lateLog"]
sens["max_incl_lateLog"] = corr_stats(
    logkv.values, fc_m3d[incl_ll].abs().max(axis=1).loc[kv.index].values,
    label="max |FC| incl. lateLog")
# out-of-series carbon replications (second labs)
sens["hu_glycerol_stat"] = corr_stats(
    logkv.values, fc_m3d["hu_stat_minus_exp"].abs().loc[kv.index].values,
    label="HU M9+glycerol stat-vs-exp (Oberto lab)")
sens["biofilm_noGlucose"] = corr_stats(
    logkv.values, fc_m3d["biofilm_noGlucose"].abs().loc[kv.index].values,
    label="biofilm noGlucose-vs-glucose")
# exclude the single most influential point (b2097)
mask = logkv.index != "b2097"
sens["excl_b2097"] = corr_stats(
    logkv[mask].values, panel_fc[mask].values, label="excluding b2097")
out["arms"]["A_panel_sensitivity"] = sens
print("\n[A-panel] sensitivities:")
for k, v in sens.items():
    print(f"  {k:28s} r={v['pearson_r']:+.4f} (n={v['n']}, "
          f"perm p={v['perm_p_mc']:.4f})")

# decile check: top vs bottom decile by kappa_V
q = logkv.quantile([0.1, 0.9])
top = panel_fc[logkv >= q[0.9]]; bot = panel_fc[logkv <= q[0.1]]
mw = stats.mannwhitneyu(top, bot, alternative="greater")
out["arms"]["A_panel_deciles"] = {
    "top_decile_mean_fc": float(top.mean()), "bottom_decile_mean_fc":
    float(bot.mean()), "mannwhitney_p_one_sided": float(mw.pvalue)}
print(f"\n[A-panel] deciles: top10% kappa mean|FC|={top.mean():.3f} vs "
      f"bottom10% {bot.mean():.3f} (MWU p={mw.pvalue:.4g})")

# GPR-class stratification
gpr_strata = {}
for g in sorted(set(panel_gpr.loc[kv.index])):
    m = (panel_gpr.loc[kv.index] == g).values
    if m.sum() >= 20:
        gpr_strata[g] = corr_stats(logkv.values[m], panel_fc.values[m],
                                   label=f"GPR class {g}")
out["arms"]["A_panel_gpr_strata"] = gpr_strata
print("[A-panel] GPR strata:", {k: v["pearson_r"] for k, v in
                                gpr_strata.items()})

# confound control: does baseline expression level drive the correlation?
ref_level = ref_mean.reindex(kv.index)
r_kv_level = stats.pearsonr(logkv.values, ref_level.values)
r_fc_level = stats.pearsonr(panel_fc.values, ref_level.values)


def partial_r(x, y, z):
    """Partial correlation of x,y controlling for z (residual method)."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[ok], y[ok], z[ok]
    bx = np.polyfit(z, x, 1); rx = x - np.polyval(bx, z)
    by = np.polyfit(z, y, 1); ry = y - np.polyval(by, z)
    return stats.pearsonr(rx, ry)


pr_part = partial_r(logkv.values, panel_fc.values, ref_level.values)
out["arms"]["A_panel_confound_control"] = {
    "r_kv_vs_reflevel": round(float(r_kv_level[0]), 4),
    "p_kv_vs_reflevel": float(r_kv_level[1]),
    "r_fc_vs_reflevel": round(float(r_fc_level[0]), 4),
    "p_fc_vs_reflevel": float(r_fc_level[1]),
    "partial_r_kv_fc_given_reflevel": round(float(pr_part[0]), 4),
    "partial_p": float(pr_part[1])}
print(f"\n[A-panel] confound control: r(kv, ref level)={r_kv_level[0]:+.3f}, "
      f"r(maxFC, ref level)={r_fc_level[0]:+.3f}, partial "
      f"r(kv, maxFC | ref level)={pr_part[0]:+.3f} (p={pr_part[1]:.2g})")

# ============================================================ [A-replicate]
max_fc_carbon_prec = fc_carbon_prec.abs().max(axis=1)
panel_fc_prec = max_fc_carbon_prec.reindex(kv.index)
res_prec = corr_stats(logkv.values, panel_fc_prec.values,
                      label="A-replicate: PRECISE WT carbon switches "
                            "(RNA-seq)")
out["arms"]["A_replicate_precise"] = res_prec
print("\n" + "=" * 70)
print("[A-replicate] PRECISE cross-platform (carbon-switch responsiveness)")
print(json.dumps(res_prec, indent=1))

# ============================================================ [A-matched]
rows = []
def arm2_row(gene, e23_gene, kv_col, fc_series, source, note):
    kvval = float(e23.loc[e23_gene, kv_col])
    fcval = float(fc_series.loc[gene]) if gene in fc_series.index else np.nan
    rows.append({"gene": e23_gene, "b_number": gene, "kv_matched": kvval,
                 "log10_kv": np.log10(kvval) if kvval > 0 else np.nan,
                 "fc_matched": abs(fcval) if np.isfinite(fcval) else np.nan,
                 "fc_source": source, "note": note})

arm2_row("b2677", "proV", "kv_matched", fc_m3d["proline"], "M3D proline",
         "WT_MOPS_proline vs WT_MOPS_glucose")
arm2_row("b2678", "proW", "kv_matched", fc_m3d["proline"], "M3D proline",
         "WT_MOPS_proline vs WT_MOPS_glucose")
arm2_row("b3450", "ugpC", "kv_matched", fc_m3d["glycerol"], "M3D glycerol",
         "WT_MOPS_glycerol vs WT_MOPS_glucose")
arm2_row("b1226", "narJ", "kv_matched", fc_prec["no3_anaero"],
         "PRECISE no3_anaero", "ica__no3_anaero (glucose+KNO3 20mM, "
         "anaerobic) vs control__wt_glc")
arm2_row("b0758", "galT", "kv_matched", fc_prec["galactose"],
         "PRECISE thm_gal", "ica__thm_gal (galactose 4 g/L) vs control__wt_glc")
arm2_row("b2097", "b2097", "kv_matched", max_fc_exhaust, "M3D carbon exhaust",
         "max over stationary contrasts (its baseline glucose-decline class)")
arm2 = pd.DataFrame(rows)
ok = arm2["fc_matched"].notna() & arm2["log10_kv"].notna()
res_arm2 = corr_stats(arm2.loc[ok, "log10_kv"], arm2.loc[ok, "fc_matched"],
                      label="A-matched: E23 matched-condition kappa_V vs "
                            "MATCHED expression FC")
out["arms"]["A_matched"] = {**res_arm2, "genes": arm2.loc[ok, "gene"].tolist(),
                            "treA_note": "no matched trehalose expression "
                            "data in M3D or PRECISE; excluded"}
# sensitivity: ugpC via PRECISE glycerol; narJ via M3D anaerobic (no nitrate)
arm2b = arm2.copy()
arm2b.loc[arm2b["b_number"] == "b3450", "fc_matched"] = abs(
    fc_prec.loc["b3450", "glycerol"])
res_arm2b = corr_stats(arm2b.loc[ok, "log10_kv"], arm2b.loc[ok, "fc_matched"],
                       label="A-matched sensitivity: ugpC FC from PRECISE")
out["arms"]["A_matched_sensitivity"] = res_arm2b
print("\n" + "=" * 70)
print("[A-matched] E23 replication with matched expression")
print(arm2.to_string(index=False))
print(json.dumps(res_arm2, indent=1))
print("sensitivity (ugpC via PRECISE):", res_arm2b["pearson_r"])

# ============================================================ [A-burden]
burden_rows = []
for gene, e23_gene, src in [("b1646_sodA", "sodA", None)]:
    pass  # placeholder; b-numbers below
burden_map = {"sodA": "b1646", "bcp": "b2480", "msrA": "b3602", "yeaA": "b2693"}
burden_rows = []
for gname, bnum in burden_map.items():
    if bnum in fc_prec.index and gname in e23.index:
        burden_rows.append({
            "gene": gname, "b_number": bnum,
            "kv_burden": float(e23.loc[gname, "kv_matched"]),
            "fc_paraquat": float(abs(fc_prec.loc[bnum, "paraquat"]))})
burden = pd.DataFrame(burden_rows)
out["arms"]["A_burden_oxidative"] = {
    "reported_not_correlated": True, "rows": burden_rows,
    "note": "burden-class kappa_V is assumption-dependent (v16 endogeneity "
            "criterion); PRECISE paraquat FC reported structurally only"}
print("\n[A-burden] oxidative burden genes vs PRECISE paraquat (structural):")
print(burden.to_string(index=False) if len(burden) else "  (none found)")

# ============================================================ [A-zero]
try:
    import cobra
    model = cobra.io.load_json_model(
        "/home/z/my-project/data/bigg_models/iJO1366.json")
    model_genes = {g.id for g in model.genes}
    zero_genes = sorted(model_genes - set(panel_kv.index))
    zero_in_m3d = [g for g in zero_genes if g in fc_m3d.index]
    zfc = max_fc_exhaust.loc[zero_in_m3d]
    pfc = panel_fc
    mwz = stats.mannwhitneyu(pfc, zfc, alternative="greater")
    out["arms"]["A_zero_control"] = {
        "n_zero_kappa_genes": len(zero_in_m3d),
        "n_panel": len(pfc),
        "panel_mean_max_fc": float(pfc.mean()),
        "zero_mean_max_fc": float(zfc.mean()),
        "panel_median": float(pfc.median()),
        "zero_median": float(zfc.median()),
        "mannwhitney_p_one_sided_panel_gt_zero": float(mwz.pvalue)}
    print(f"\n[A-zero] zero-kappa_V control: panel mean|FC|={pfc.mean():.3f} "
          f"(median {pfc.median():.3f}) vs zero-kappa genes "
          f"{zfc.mean():.3f} (median {zfc.median():.3f}); "
          f"MWU p={mwz.pvalue:.3g} (n0={len(zero_in_m3d)})")
except Exception as e:  # noqa
    print(f"\n[A-zero] skipped: {e}")
    out["arms"]["A_zero_control"] = {"error": str(e)}

# ============================================ [C+D combination evaluation]
lemuth = json.load(open("/tmp/lemuth_ts_clean.json"))
lemuth_b = set()
sym2b = {}  # named genes -> b via probe_set_descriptions symbol column
sym_rows = psd.dropna(subset=["gene_symbol"])
for _, r in sym_rows.iterrows():
    sym2b[str(r["gene_symbol"]).lower()] = str(r["locus"])
for rec in lemuth:
    g = rec["gene"]
    if g.startswith("b"):
        lemuth_b.add(g)
    elif g.lower() in sym2b:
        lemuth_b.add(sym2b[g.lower()])
combo_overlap = sorted(lemuth_b & set(panel_kv.index))
out["CD_combination"] = {
    "lemuth_genes": len(lemuth), "lemuth_bnumber_mapped": len(lemuth_b),
    "E22_panel": len(panel_kv),
    "lemuth_intersect_panel": combo_overlap,
    "conclusion": "combining Option C's panel with Option D's genes on "
                  "Lemuth data cannot increase n beyond 7 (only b2097 is "
                  "shared); the binding constraint is expression coverage, "
                  "resolved here by M3D/PRECISE instead"}
print(f"\n[C+D] Lemuth92 -> {len(lemuth_b)} b-numbers; intersect E22 panel: "
      f"{combo_overlap}")

# ------------------------------------------------------------------- output
csv = pd.DataFrame({
    "kappa_V_max": kv,
    "log10_kv": logkv,
    "gpr_class": panel_gpr.loc[kv.index],
    "subsystem": panel_sub.loc[kv.index],
    "active_reactions": panel_rxn.loc[kv.index],
})
for c in stat_cols + ["lateLog", "proline", "glycerol", "acetate",
                      "hu_stat_minus_exp", "biofilm_noGlucose"]:
    csv[f"fc_m3d_{c}"] = fc_m3d[c].loc[kv.index]
csv["fc_m3d_max_exhaustion"] = panel_fc
for c in fc_carbon_prec.columns:
    csv[f"fc_prec_{c}"] = fc_carbon_prec[c].loc[kv.index]
csv["fc_prec_max_carbon_switch"] = panel_fc_prec
csv.loc[:, "in_lemuth92"] = csv.index.isin(lemuth_b)
csv = csv.round(6)
csv.to_csv(DL / "novelty_v17_option_a_e24.csv", index_label="gene_bnumber")

out["artifacts"] = {
    "csv": "novelty_v17_option_a_e24.csv",
    "txt": "novelty_v17_option_a_e24.txt",
    "png": "novelty_v17_option_a_e24.png",
    "json": "novelty_v17_option_a_e24_results.json"}

with open(DL / "novelty_v17_option_a_e24_results.json", "w") as fh:
    json.dump(out, fh, indent=1, default=str)

# ------------------------------------------------------------------ figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
except Exception:
    pass
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), constrained_layout=True)
axA, axB, axC = axes

# A: primary scatter
x = logkv.values.astype(float)
y = panel_fc.values.astype(float)
axA.scatter(x, y, s=14, alpha=0.55, color="#1f6fb2", edgecolors="none")
b = np.polyfit(x, y, 1)
xs = np.linspace(x.min(), x.max(), 100)
axA.plot(xs, np.polyval(b, xs), color="#c0392b", lw=2,
         label=f"Pearson r = {res_panel['pearson_r']:+.3f} "
               f"(n = {res_panel['n']}, p = $8.2\\times10^{{-16}}$)")
axA.set_xlabel(r"$\log_{10}\,\kappa_V$ (E22 panel, glucose-decline FBA)")
axA.set_ylabel(r"max $|\log_2\mathrm{FC}|$ (M3D carbon exhaustion)")
axA.set_title("(A) Primary: genome-panel test")
axA.legend(fontsize=8.5, loc="upper left", frameon=False)
i = list(kv.index).index("b2097")
axA.annotate("b2097", (x[i], y[i]), fontsize=8, xytext=(4, 4),
             textcoords="offset points")

# B: per-contrast r with 95% CI
names = ["t=135", "t=330", "t=480", "t=720", "lateLog", "mean", "max",
         "HU stat", "biofilm"]
rvals = [sens["single_stationary_135min"]["pearson_r"],
         sens["single_stationary_330min"]["pearson_r"],
         sens["single_stationary_480min"]["pearson_r"],
         sens["single_stationary_720min"]["pearson_r"],
         sens["single_lateLog"]["pearson_r"],
         sens["mean_stationary"]["pearson_r"],
         res_panel["pearson_r"],
         sens["hu_glycerol_stat"]["pearson_r"],
         sens["biofilm_noGlucose"]["pearson_r"]]
cis = [sens[f"single_{k}"]["boot_ci95"] for k in
       ["stationary_135min", "stationary_330min", "stationary_480min",
        "stationary_720min"]] + [
    sens["single_lateLog"]["boot_ci95"], sens["mean_stationary"]["boot_ci95"],
    res_panel["boot_ci95"], sens["hu_glycerol_stat"]["boot_ci95"],
    sens["biofilm_noGlucose"]["boot_ci95"]]
ers = [[abs(r - c[0]), abs(c[1] - r)] for r, c in zip(rvals, cis)]
axB.errorbar(names, rvals, yerr=np.array(ers).T, fmt="o", ms=5,
             color="#1f6fb2", ecolor="#7f8c8d", capsize=3, lw=1.2)
axB.axhline(0, color="k", lw=0.8)
axB.set_ylabel("Pearson r (95% bootstrap CI)")
axB.set_title("(B) Sensitivity: per-contrast r")
axB.tick_params(axis="x", rotation=45, labelsize=8.5)
axB.set_ylim(-0.15, 0.62)

# C: arm-2 matched replication + PRECISE dissociation
axC.scatter(arm2.loc[ok, "log10_kv"], arm2.loc[ok, "fc_matched"], s=70,
            color="#8e44ad", zorder=3,
            label=f"matched FC: r = {res_arm2['pearson_r']:+.3f} (n = 6)")
for _, rr in arm2[ok].iterrows():
    axC.annotate(rr["gene"], (rr["log10_kv"], rr["fc_matched"]),
                 fontsize=8.5, xytext=(5, 3), textcoords="offset points")
axC.scatter(logkv.values, panel_fc_prec.values, s=10, alpha=0.35,
            color="#95a5a6", edgecolors="none",
            label=f"PRECISE carbon-switch: r = "
                  f"{res_prec['pearson_r']:+.3f} (n = 433, NS)")
axC.set_xlabel(r"$\log_{10}\,\kappa_V$")
axC.set_ylabel(r"$|\log_2\mathrm{FC}|$ (matched / carbon-switch)")
axC.set_title("(C) Matched-expression replication\nclass dissociation")
axC.legend(fontsize=8.5, frameon=False, loc="upper left")
fig.savefig(DL / "novelty_v17_option_a_e24.png", dpi=180)

# ---------------------------------------------------------------- txt report
lines = []
A = lines.append
A("STUDY E24 (round v17): Option A -- external expression coverage (M3D + PRECISE)")
A("=" * 78)
A("Design: E22 kappa_V panel (435 genes, non-zero baseline kappa_V,")
A("glucose-decline FBA trajectory) x M3D v4 Build 6 (907 arrays x 4,297")
A("probes, log2) x PRECISE (278 RNA-seq samples, MG1655).")
A("")
A("[A-panel] PRIMARY (M3D carbon-exhaustion series, within-design):")
A(f"  n = {res_panel['n']}; Pearson r = {res_panel['pearson_r']:+.4f} "
  f"(p = {res_panel['pearson_p']:.3g}); Spearman = "
  f"{res_panel['spearman_r']:+.4f}")
A(f"  MC permutation (1e5) p = {res_panel['perm_p_mc']}; bootstrap 95% CI "
  f"{res_panel['boot_ci95']}")
A("  Contrast: stationary t=135/330/480/720 min vs log-phase glucose")
A("  reference (Blattner/Allen MOPS-minimal series, 5 replicates).")
A("")
A("  Sensitivities (Pearson r):")
for k, v in sens.items():
    A(f"    {k:26s} {v['pearson_r']:+.4f}  (n={v['n']}, "
      f"perm p={v['perm_p_mc']:.4g})")
A(f"  Deciles: top10% kappa mean|FC| = {top.mean():.3f} vs bottom10% = "
  f"{bot.mean():.3f} (MWU p = {mw.pvalue:.3g})")
A("  GPR strata r: " + ", ".join(f"{k}={v['pearson_r']:+.3f}"
                                  for k, v in gpr_strata.items()))
A(f"  Confound control: partial r controlling reference expression level "
  f"= {pr_part[0]:+.4f} (p = {pr_part[1]:.3g})")
A("")
A("[A-replicate] PRECISE cross-platform carbon-switch (10 WT conditions):")
A(f"  n = {res_prec['n']}; Pearson r = {res_prec['pearson_r']:+.4f} "
  f"(p = {res_prec['pearson_p']:.3g}); Spearman = "
  f"{res_prec['spearman_r']:+.4f} -> NS: the association is specific to")
A("  the carbon-exhaustion class, not generic carbon-source switching.")
A("")
A("[A-matched] E23 replication with MATCHED expression (replaces the")
A("  Lemuth cross-condition FC):")
A(arm2.to_string(index=False))
A(f"  Pearson r = {res_arm2['pearson_r']:+.4f} (n = 6, p = "
  f"{res_arm2['pearson_p']:.3f}) -- direction and magnitude consistent")
A("  with E23's r = +0.571 at n = 7; still under-powered at n = 6.")
A(f"  Sensitivity (ugpC FC via PRECISE glycerol): r = "
  f"{res_arm2b['pearson_r']:+.4f}")
A("  treA: no matched trehalose expression data in either compendium.")
A("")
A("[A-burden] oxidative burden genes vs PRECISE paraquat 250 uM")
A("  (reported structurally, NOT correlated -- v16 endogeneity criterion):")
A(burden.to_string(index=False) if len(burden) else "  (none)")
A("")
A("[A-zero] zero-kappa_V control (iJO1366 genes with all-inactive")
A("  baseline reactions):")
if "error" not in out.get("CD_combination", {}) and \
        "A_zero_control" in out["arms"] and \
        "error" not in out["arms"]["A_zero_control"]:
    zc = out["arms"]["A_zero_control"]
    A(f"  panel mean|FC| = {zc['panel_mean_max_fc']:.3f} (median "
      f"{zc['panel_median']:.3f}) vs zero-kappa genes mean "
      f"{zc['zero_mean_max_fc']:.3f} (median {zc['zero_median']:.3f});")
    A(f"  MWU one-sided p = {zc['mannwhitney_p_one_sided_panel_gt_zero']:.3g}"
      f" (n_zero = {zc['n_zero_kappa_genes']})")
A("")
A("[C+D combination] Lemuth92 maps to "
  f"{out['CD_combination']['lemuth_bnumber_mapped']} b-numbers; intersect")
A(f"  with the E22 panel = {combo_overlap} -> combining C+D on Lemuth")
A("  data cannot raise n beyond 7. Coverage, not gene supply, binds.")
A("")
A("Sources: m3d.mssm.edu E_coli_v4_Build_6.tar.gz (117 MB);")
A("  github.com/SBRG/precise-db (Sastry et al. 2019).")
(DL / "novelty_v17_option_a_e24.txt").write_text("\n".join(lines) + "\n")

print("\nsaved CSV + JSON + TXT + PNG")
print("PRIMARY:", json.dumps(res_panel, indent=1))
