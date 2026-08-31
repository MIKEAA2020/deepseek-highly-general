#!/usr/bin/env python3
"""
Study E27 (manuscript round v20): protein-layer replication of the E26
finding with the Schmidt et al. 2016 condition-dependent quantitative
proteome ("The quantitative and condition-dependent Escherichia coli
proteome", Nat Biotechnol 34:104-110; data: PRIDE PXD000498; processed
supplementary tables via PMC4888949 / Europe PMC).

Motivation (user-directed, post-v19 review): the E26 verdict named "a
targeted replicate proteomics experiment (e.g. the Schmidt et al.
condition-dependent format)" as the natural follow-up, because the E26
protein test rested on GSE64021 single-shot spectral counts (n=169,
no replicates, compressed dynamic range, noise attenuating protein
correlations toward zero).  E27 performs that replication.

Dataset choice (evaluated, honest): PRECISE 2.0 (= PRECISE-1K, the
expanded SBRG RNA-seq compendium) was also evaluated per the user's
"Schmidt 2016 or PRECISE 2.0" instruction.  A metadata scan of all
1,035 PRECISE-1K samples (data/schmidt2016/precise1k_metadata_qc_scan.csv)
finds NO carbon-depletion condition (the only starvation-like samples
are Fe- and N-starvation, non-carbon classes already covered by E25's
controls), so it cannot replicate the carbon-exhaustion contrast; the
transcript side is already replicated on two platforms (E24 M3D, E25
GSE64021).  The protein side is the decisive gap -> Schmidt 2016.

Schmidt data used (data/schmidt2016/):
  - Table S8 (dataset 2, BW25113, biological TRIPlicATES, SafeQuant
    label-free quantification): per-protein fold-change (medianRatio)
    vs. the glucose reference for 22 conditions + q-values + CVs;
    2,058 proteins, b-number mapping via Table S6 (2,284 with b-numbers;
    spot checks aceA->b4015, rpoB->b3987, gapA->P0A9B2->b1779,
    groL->b4143 all OK).
  - Table S7 (dataset 1, no replicates) as a cross-dataset sensitivity.

Condition classes (mirroring the E24/E25 classes):
  EXHAUSTION (primary, the E24 class): stationary phase 1 day / 3 days
    (glucose batch culture harvested 1/3 days into stationary phase,
    i.e. after carbon exhaustion) vs. exponential glucose.
  LIMITATION (chemostat gradient): glucose-limited chemostat
    mu = 0.5 / 0.35 / 0.20 / 0.12 h^-1 (severity gradient, the protein
    analog of E25's starvation-depth gradient).
  SWITCH (11): glycerol+AA, acetate, fumarate, glucosamine, glycerol,
    pyruvate, xylose, mannose, galactose, succinate, fructose.
  STRESS-on-glucose: 50 mM NaCl (OSM), 42 C, pH 6.
  NULL (internal): Glucose.2 -- an independent glucose batch culture
    vs. the glucose reference (same-medium control).
  OUT: LB (rich medium).

Tests (E26 metrics, UNCHANGED definitions):
  [R-coverage]     panel coverage + mapping verification.
  [R-internal-null] Glucose.2 noise floor + kappa correlation.
  [R-protfc]       PRIMARY: r(log10 kappa_V, protein max|log2FC| over
                   the exhaustion pair) on the Schmidt-covered panel,
                   vs. the transcript associations (E24/E25 metrics) on
                   the SAME gene subset (apples-to-apples), plus the
                   E26 GSE spectral-count protein metric on the same
                   subset (three-way contrast).
  [R-chemostat]    per-mu r + max over the 4 chemostat conditions.
  [R-switch]       per-switch r + max over 11 switches.
  [R-stress]       per-stress r + max over the 3 glucose-matched
                   stresses; LB reported out of class.
  [R-tp]           transcript-protein coupling by kappa_V tertile
                   (signed dT at the argmax time point vs. signed dP at
                   the argmax stationary condition; cross-experiment --
                   stated as such).
  [R-stability]    within the top kappa tertile: r(kappa, protein
                   max|FC|) (E26 found -0.427 with spectral counts).
  [R-ratio]        |dP|/|dT| implementation ratio by tertile + MWU.
  [R-zero]         zero-kappa control: protein response, panel vs.
                   iJO1366 genes outside the panel (E24 [A-zero] /
                   E25 [S-zero] convention).

kappa_V values are taken UNCHANGED from the E22 artifact; the E24/E25
transcript metrics are recomputed with the E26 script's exact code.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DL = Path("/home/z/my-project/download")
M3D = Path("/home/z/my-project/data/m3d/E_coli_v4_Build_6")
GSE = Path("/home/z/my-project/data/gse64021")
SCH = Path("/home/z/my-project/data/schmidt2016")

# ==================================================================== stats
def corr_stats(x, y, n_perm=100_000, n_boot=10_000, label=""):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    pr, pp = stats.pearsonr(x, y)
    sr, sp = stats.spearmanr(x, y)
    zx = (x - x.mean()) / x.std()
    zy = (y - y.mean()) / y.std()
    rng = np.random.default_rng(777)
    perms = np.stack([rng.permutation(n) for _ in range(min(n_perm, 20000))])
    r_perm = (zy[perms] @ zx) / n
    cnt = int((np.abs(r_perm) >= abs(pr) - 1e-12).sum())
    perm_p = (cnt + 1) / (perms.shape[0] + 1)
    idx = rng.integers(0, n, size=(n_boot, n))
    rb = [np.corrcoef(x[row], y[row])[0, 1] for row in idx
          if x[row].std() > 0 and y[row].std() > 0]
    rb = np.asarray(rb)
    lo, hi = (float(np.percentile(rb, 2.5)), float(np.percentile(rb, 97.5))
              if len(rb) else (np.nan, np.nan))
    return {"label": label, "n": int(n), "pearson_r": float(pr),
            "pearson_p": float(pp), "spearman_r": float(sr),
            "spearman_p": float(sp), "perm_p_mc": float(perm_p),
            "boot_ci95": [lo, hi]}


def report(tag, res):
    print(f"  [{tag}] n={res['n']:4d}  r={res['pearson_r']:+.4f} "
          f"(p={res['pearson_p']:.2e})  rho={res['spearman_r']:+.4f} "
          f"(p={res['spearman_p']:.2e})  perm_p={res['perm_p_mc']:.4f} "
          f"CI=[{res['boot_ci95'][0]:+.3f},{res['boot_ci95'][1]:+.3f}]")
    return res


# ==================================================== panel (kappa_V fixed)
e22 = pd.read_csv(DL / "novelty_v15_reaction_sampling_e22.csv")
e22 = e22.set_index("gene_bnumber")
panel_kv = e22["kappa_V_max"].astype(float)
logkv_panel = np.log10(panel_kv)
print(f"[panel] E22 kappa_V panel: {len(panel_kv)} genes "
      f"(unchanged from E22/E23/E24/E25/E26)")

# ================================= transcript metric 1: E24 M3D exhaustion
expr = pd.read_csv(M3D / "E_coli_v4_Build_6_chips907probes4297.tab",
                   sep="\t", index_col=0)
psd = pd.read_csv(M3D / "E_coli_v4_Build_6.probe_set_descriptions", sep="\t")
locus_of = dict(zip(psd["probe_set_name"], psd["locus"].astype(str)))
expr.index = [locus_of.get(p, p) for p in expr.index]
if expr.index.duplicated(keep=False).any():
    expr = expr.groupby(level=0).mean()
REF = [f"WT_MOPS_glucose_r{i}" for i in range(1, 6)]
STAT = {
    "t135": [f"WT_MOPS_stationary_r{i}" for i in (1, 2)],
    "t330": [f"WT_MOPS_stationary2_r{i}" for i in (1, 2)],
    "t480": [f"WT_MOPS_stationary3_r{i}" for i in (1, 2)],
    "t720": [f"WT_MOPS_stationary4_r{i}" for i in (1, 2)],
}
ref_mean = expr[REF].mean(axis=1)
signed_fc = pd.DataFrame({t: expr[v].mean(axis=1) - ref_mean
                          for t, v in STAT.items()})
exh_max = signed_fc.abs().max(axis=1)
exh_signed = pd.Series([signed_fc.loc[g].iloc[np.argmax(
    np.abs(signed_fc.loc[g].values))] if g in signed_fc.index else np.nan
    for g in panel_kv.index], index=panel_kv.index)
print(f"[E24] M3D exhaustion metric available for "
      f"{int(exh_max.reindex(panel_kv.index).notna().sum())}/435 panel genes")

# ================================= transcript metric 2: E25 GSE starvation
gi = pd.read_csv("/home/z/my-project/data/precise/data/gene_info.csv",
                 index_col=0)
name_to_b = {str(r["gene_name"]).strip(): b for b, r in gi.iterrows()}
try:
    import cobra
    model = cobra.io.load_json_model(
        "/home/z/my-project/data/bigg_models/iJO1366.json")
    for g in model.genes:
        if g.name:
            name_to_b.setdefault(str(g.name).strip(), g.id)
    model_genes = {g.id for g in model.genes}
except Exception:
    model_genes = set()
gse_tags = {"MOPS_1h": "MOPS_1h.csv", "MOPS_2h": "MOPS_2h.csv",
            "MOPS_4h": "MOPS_4h.csv", "MOPS_6h": "MOPS_6h.csv",
            "MC_1h": "MC_1h.csv", "MC_2h": "MC_2h.csv",
            "MC_4h": "MC_4h.csv", "MC_6h": "MC_6h.csv"}
tpm = {}
for tag, fn in gse_tags.items():
    d = pd.read_csv(GSE / fn, sep="\t")
    d["Gene"] = d["Gene"].astype(str).str.strip()
    idx = [name_to_b.get(g, g) for g in d["Gene"]]
    tpm[tag] = pd.Series(d["mRNATPM"].values, index=idx)
tpm = pd.DataFrame(tpm).groupby(level=0).mean()
log2t = np.log2(tpm + 1.0)
fcT = pd.DataFrame({t: log2t[f"MC_{t}"] - log2t[f"MOPS_{t}"]
                    for t in ("1h", "2h", "4h", "6h")})
fcT_max = fcT.abs().max(axis=1)
fcT_signed = pd.Series([fcT.loc[g].iloc[np.argmax(np.abs(fcT.loc[g].values))]
                         if g in fcT.index else np.nan
                         for g in panel_kv.index], index=panel_kv.index)

# ============================== Schmidt 2016 protein fold-changes (Table S8)
s8 = pd.read_csv(SCH / "schmidt2016_s8_fc.csv")
mp = pd.read_csv(SCH / "schmidt2016_s6_map.csv")
bnum_of = dict(zip(mp["uniprot"], mp["bnum"]))
s8["bnum"] = s8["uniprot"].map(bnum_of).fillna("")
# gene-name fallback for rows whose S6 b-number is missing
s8["bnum"] = [b if isinstance(b, str) and b else name_to_b.get(g, "")
              for b, g in zip(s8["bnum"], s8["gene_name"])]
s8 = s8.set_index("bnum")
# 4 duplicate-bnum rows (clpB double-listed, bioD under two accessions):
# average paralogs/duplicates (same convention as E26's duplicate probes)
s8 = s8.groupby(level=0).mean(numeric_only=True)

FC = {c.split("medianRatio_")[1].split("_vs_Glucose")[0]:
      np.log2(pd.to_numeric(s8[c], errors="coerce"))
      for c in s8.columns if c.startswith("medianRatio_")}
QV = {c.split("qvalue_")[1].split("_vs_Glucose")[0]:
      pd.to_numeric(s8[c], errors="coerce")
      for c in s8.columns if c.startswith("qvalue_")}
CV = {c.split("cv_")[1]: pd.to_numeric(s8[c], errors="coerce")
      for c in s8.columns if c.startswith("cv_")}

CONDS = {
    "exhaustion": ["Statday", "Stat.3days"],
    "limitation": ["Chemstat.0.5", "Chemstat.0.35", "Chemstat.0.2",
                   "Chemstat.02"],           # mu = 0.5/0.35/0.20/0.12
    "switch": ["Glycerin.AA", "Acetate", "Fumarate", "Glucoseamine",
               "Glycerol", "Pyruvate", "Xylose", "Mannose", "Galactose",
               "Succinate", "Fructose"],
    "stress_glucose": ["OSM", "42.C", "pH6"],
    "null": ["Glucose.2"],
    "out": ["LB"],
}
NICE = {"Statday": "stationary 1 day", "Stat.3days": "stationary 3 days",
        "Chemstat.0.5": "chemostat mu=0.5", "Chemstat.0.35": "chemostat mu=0.35",
        "Chemstat.0.2": "chemostat mu=0.20", "Chemstat.02": "chemostat mu=0.12",
        "Glycerin.AA": "glycerol+AA", "Glucoseamine": "glucosamine",
        "Glucose.2": "glucose (batch 2)", "42.C": "42C", "OSM": "NaCl 50mM",
        "pH6": "pH 6"}

results = {"study": "E27_schmidt_replication",
           "data": {"source": "Schmidt et al. 2016 Nat Biotechnol "
                    "(PRIDE PXD000498; supplementary tables via PMC4888949/"
                    "Europe PMC)", "table": "S8 (dataset 2, BW25113, "
                    "biological triplicates)", "n_proteins": int(len(s8))},
           "arms": {}, "per_condition": {}}

# ---------------------------------------------------------------- [R-coverage]
genes_S = [g for g in panel_kv.index if g in s8.index
           and np.isfinite(FC["Statday"].get(g, np.nan))]
print(f"\n[R-coverage] panel genes with Schmidt protein data: "
      f"{len(genes_S)}/435 (E26 spectral-count subset: 169)")
results["coverage"] = {"panel_genes_with_schmidt": len(genes_S),
                       "panel_total": 435,
                       "e26_spectral_count_subset": 169,
                       "n_proteins_S8": int(len(s8))}
logkv_S = logkv_panel.loc[genes_S]

# ------------------------------------------------- [R-internal-null] batch 2
all_genes = [g for g in s8.index if np.isfinite(FC["Statday"].get(g, np.nan))]
med_abs = {c: float(np.nanmedian(np.abs(FC[c].loc[all_genes])))
           for c in sum(CONDS.values(), [])}
print(f"\n[R-internal-null] Glucose.2 (independent batch) median|log2FC| = "
      f"{med_abs['Glucose.2']:.3f} vs stationary "
      f"{med_abs['Statday']:.3f}/{med_abs['Stat.3days']:.3f}, "
      f"switch median "
      f"{np.median([med_abs[c] for c in CONDS['switch']]):.3f}")
results["internal_null"] = {
    "median_abs_log2fc_per_condition": med_abs,
    "glucose2_r_on_panel": corr_stats(
        logkv_S, FC["Glucose.2"].loc[genes_S].abs(),
        label="kappa vs |log2FC| glucose batch-2 (internal null)")}

# ------------------------------------------------------------ [R-protfc] MAIN
fcP_exh = pd.concat([FC[c].loc[genes_S].abs() for c in CONDS["exhaustion"]],
                    axis=1).max(axis=1)
fcP_exh_signed = pd.Series([FC["Statday"].loc[g] if
                            abs(FC["Statday"].loc[g]) >=
                            abs(FC["Stat.3days"].loc[g]) else
                            FC["Stat.3days"].loc[g] for g in genes_S],
                           index=genes_S)
print("\n[R-protfc] PRIMARY protein test (exhaustion class, n=%d):"
      % len(genes_S))
results["arms"]["schmidt-protfc-exhaustion"] = report(
    "schmidt-protfc-exhaustion",
    corr_stats(logkv_S, fcP_exh, label="log10 kappa_V vs Schmidt protein "
               "max|log2FC| (stationary 1d/3d)"))
# apples-to-apples transcript associations on the SAME subset
results["arms"]["e24-transfc-on-schmidt-subset"] = report(
    "e24-transfc-on-schmidt-subset",
    corr_stats(logkv_S, exh_max.reindex(genes_S),
               label="E24 M3D exhaustion metric on the Schmidt subset"))
results["arms"]["e25-transfc-on-schmidt-subset"] = report(
    "e25-transfc-on-schmidt-subset",
    corr_stats(logkv_S, fcT_max.reindex(genes_S),
               label="E25 GSE starvation metric on the Schmidt subset"))
# E26 GSE spectral-count protein metric on the same subset (three-way)
e26 = pd.read_csv(DL / "novelty_v19_e26_protein_abundance.csv",
                  index_col=0) if (DL / "novelty_v19_e26_protein_abundance"
                                   ".csv").exists() else None
if e26 is not None:
    gse_p = e26["gse_protein_maxfc"].astype(float)
    sub = [g for g in genes_S if np.isfinite(gse_p.get(g, np.nan))]
    results["arms"]["e26-gse-protfc-on-schmidt-subset"] = report(
        "e26-gse-protfc-on-schmidt-subset",
        corr_stats(logkv_panel.loc[sub], gse_p.loc[sub],
                   label="E26 GSE spectral-count protein metric on the "
                         "Schmidt subset (n=%d)" % len(sub)))
# magnitudes on the same genes
mag = {"schmidt_protein_max": float(fcP_exh.mean()),
       "e24_transcript_max": float(exh_max.reindex(genes_S).mean()),
       "e25_transcript_max": float(fcT_max.reindex(genes_S).mean())}
mag["ratio_protein_e24"] = mag["schmidt_protein_max"] / mag["e24_transcript_max"]
results["magnitudes_schmidt_subset"] = mag
print(f"  magnitudes: protein {mag['schmidt_protein_max']:.2f} vs "
      f"E24 transcript {mag['e24_transcript_max']:.2f} "
      f"(ratio {mag['ratio_protein_e24']:.3f})")

# sensitivities: q<0.05; low-CV; excl b2097; dataset-1 (S7) stationary
q_any = ((QV["Statday"].loc[genes_S] < 0.05) |
         (QV["Stat.3days"].loc[genes_S] < 0.05))
gq = [g for g in genes_S if q_any.loc[g]]
results["arms"]["schmidt-protfc-q05"] = report(
    "schmidt-protfc-q05",
    corr_stats(logkv_panel.loc[gq], fcP_exh.loc[gq],
               label=f"significant FCs only (q<0.05, n={len(gq)})"))
cv_mean = pd.concat([CV["Stat.1day"].loc[genes_S],
                     CV["Stat.3days"].loc[genes_S]], axis=1).mean(axis=1)
gl = [g for g in genes_S if np.isfinite(cv_mean.get(g, np.nan))
      and cv_mean[g] <= 20.0]
results["arms"]["schmidt-protfc-lowcv"] = report(
    "schmidt-protfc-lowcv",
    corr_stats(logkv_panel.loc[gl], fcP_exh.loc[gl],
               label=f"mean triplicate CV<=20% (n={len(gl)})"))
gno = [g for g in genes_S if g != "b2097"]
results["arms"]["schmidt-protfc-excl-b2097"] = report(
    "schmidt-protfc-excl-b2097",
    corr_stats(logkv_panel.loc[gno], fcP_exh.loc[gno],
               label=f"excl. b2097 (n={len(gno)})"))
s7 = pd.read_csv(SCH / "schmidt2016_s7_fc.csv")
s7["bnum"] = s7["uniprot"].map(bnum_of).fillna("")
s7["bnum"] = [b if isinstance(b, str) and b else name_to_b.get(g, "")
              for b, g in zip(s7["bnum"], s7["gene_name"])]
s7 = s7.set_index("bnum").groupby(level=0).mean(numeric_only=True)
fcS7 = pd.concat([np.log2(s7[c]) for c in
                  ("medianRatio_stationary 1 day_vs_glucose",
                   "medianRatio_stationary 3 days_vs_glucose")],
                 axis=1).abs().max(axis=1, skipna=True)
g7 = [g for g in genes_S if np.isfinite(fcS7.get(g, np.nan))]
results["arms"]["schmidt-s7-protfc"] = report(
    "schmidt-s7-protfc",
    corr_stats(logkv_panel.loc[g7], fcS7.loc[g7],
               label=f"dataset-1 (Table S7) stationary (n={len(g7)})"))

# ------------------------------------------- per-condition r profile (all 22)
print("\n[R-profile] per-condition r(log10 kappa, |log2FC|) on the panel:")
for cls, clist in CONDS.items():
    for c in clist:
        res = corr_stats(logkv_S, FC[c].loc[genes_S].abs(),
                         label=NICE.get(c, c))
        results["per_condition"][f"{cls}:{c}"] = res
        print(f"  {cls:15s} {NICE.get(c, c):22s} "
              f"r={res['pearson_r']:+.3f} (p={res['pearson_p']:.1e}) "
              f"median|FC|={med_abs[c]:.2f}")
# class-level max metrics
class_max = {}
for cls in ("exhaustion", "limitation", "switch", "stress_glucose"):
    cm = pd.concat([FC[c].loc[genes_S].abs() for c in CONDS[cls]],
                   axis=1).max(axis=1)
    class_max[cls] = cm
    results["arms"][f"schmidt-protfc-{cls}-max"] = report(
        f"schmidt-protfc-{cls}-max", corr_stats(logkv_S, cm,
        label=f"max|log2FC| over the {cls} class"))

# chemostat severity gradient ordering
grad = [results["per_condition"][f"limitation:{c}"]["pearson_r"]
        for c in ("Chemstat.0.5", "Chemstat.0.35", "Chemstat.0.2",
                  "Chemstat.02")]
print(f"  chemostat gradient (mu=0.5->0.12): "
      f"{['%+.3f' % g for g in grad]}")

# ------------------------------------------------------ [R-tp] coupling tiers
print("\n[R-tp] transcript-protein coupling by kappa tertile "
      "(cross-experiment pairing; dT = E24 argmax-time signed log2FC, "
      "dP = Schmidt argmax-stationary signed log2FC):")
kq1, kq2 = logkv_S.quantile([1 / 3, 2 / 3])
results["tp_coupling_by_kappa"] = {}
ratio_rows = []
for g in genes_S:
    kv = logkv_S.loc[g]
    s = ("low-kappa" if kv <= kq1 else
         "mid-kappa" if kv <= kq2 else "high-kappa")
    dt, dp = exh_signed.get(g, np.nan), fcP_exh_signed.loc[g]
    if np.isfinite(dt) and np.isfinite(dp):
        ratio_rows.append((g, s, abs(dp), abs(dt)))
rat = pd.DataFrame(ratio_rows, columns=["gene", "stratum", "absdP",
                                        "absdT"])
for s in ("low-kappa", "mid-kappa", "high-kappa"):
    gsub = [g for g, st in zip(rat["gene"], rat["stratum"]) if st == s]
    results["tp_coupling_by_kappa"][s] = report(
        f"tp-coupling-{s}",
        corr_stats(exh_signed.loc[gsub], fcP_exh_signed.loc[gsub],
                   label=f"signed dT vs dP, {s}"))
    rr = rat[rat["stratum"] == s]
    results["tp_coupling_by_kappa"][f"{s}_ratio"] = {
        "n": int(len(rr)),
        "mean_dP": float(rr["absdP"].mean()),
        "mean_dT": float(rr["absdT"].mean()),
        "mean_ratio": float((rr["absdP"] / rr["absdT"]).mean())}
    print(f"  {s}: |dP|/|dT| mean "
          f"{results['tp_coupling_by_kappa'][f'{s}_ratio']['mean_ratio']:.3f}"
          f"  (n={len(rr)})")
hi = (rat["stratum"] == "high-kappa")
lo = (rat["stratum"] == "low-kappa")
mwu_r = stats.mannwhitneyu((rat.loc[hi, "absdP"] / rat.loc[hi, "absdT"]),
                           (rat.loc[lo, "absdP"] / rat.loc[lo, "absdT"]),
                           alternative="greater")
results["implementation_ratio_test"] = {
    "high_mean": float((rat.loc[hi, "absdP"] / rat.loc[hi, "absdT"]).mean()),
    "low_mean": float((rat.loc[lo, "absdP"] / rat.loc[lo, "absdT"]).mean()),
    "n_high": int(hi.sum()), "n_low": int(lo.sum()),
    "mannwhitney_p_one_sided_high_gt_low": float(mwu_r.pvalue)}
print(f"[R-ratio] |dP|/|dT| high {results['implementation_ratio_test']['high_mean']:.3f} "
      f"vs low {results['implementation_ratio_test']['low_mean']:.3f} "
      f"(MWU p={mwu_r.pvalue:.3g})")
# E25-GSE signed dT variant
sub = [g for g in genes_S if np.isfinite(fcT_signed.get(g, np.nan))]
results["arms"]["tp-coupling-gse-dT"] = report(
    "tp-coupling-gse-dT",
    corr_stats(fcT_signed.loc[sub], fcP_exh_signed.loc[sub],
               label=f"E25 GSE signed dT vs Schmidt dP (n={len(sub)})"))

# ------------------------------------------------- [R-stability] top tertile
top = [g for g, kv in logkv_S.items() if kv > kq2]
results["arms"]["stability-top-tertile"] = report(
    "stability-top-tertile",
    corr_stats(logkv_S.loc[top], fcP_exh.loc[top],
               label="within top kappa tertile: kappa vs protein max|FC|"))
# transcript within-stratum gradient for the same tertile (E26: -0.004)
results["arms"]["stability-top-tertile-transcript"] = report(
    "stability-top-tertile-transcript",
    corr_stats(logkv_S.loc[top], exh_max.reindex(top),
               label="within top kappa tertile: kappa vs E24 transcript"))
# protein vs transcript magnitude within each stratum (E26 comparison)
e26_tp = {"low": (+0.088, None), "mid": (+0.164, None),
          "high": (+0.212, None)}
results["e26_reference"] = {
    "coupling_low_mid_high": [e26_tp[s][0] for s in ("low", "mid", "high")],
    "stability_top_tertile_r": -0.427}

# ------------------------------------------------------------ [R-zero] control
zero_genes = sorted(model_genes - set(panel_kv.index)) if model_genes else []
zS = [g for g in zero_genes if g in s8.index
      and np.isfinite(FC["Statday"].get(g, np.nan))]
zresp = pd.concat([FC[c].loc[zS].abs() for c in CONDS["exhaustion"]],
                  axis=1).max(axis=1)
presp = fcP_exh
mwu_z = stats.mannwhitneyu(presp.dropna(), zresp.dropna(),
                            alternative="greater")
results["zero_control"] = {
    "n_zero_genes_model": len(zero_genes), "n_zero_with_schmidt": len(zS),
    "panel_mean_max_fc": float(presp.mean()),
    "zero_mean_max_fc": float(zresp.mean()),
    "mannwhitney_p_one_sided_panel_gt_zero": float(mwu_z.pvalue)}
print(f"\n[R-zero] protein exhaustion max|FC|: panel {presp.mean():.3f} vs "
      f"zero-kappa {zresp.mean():.3f} (MWU p={mwu_z.pvalue:.2e}, "
      f"n_zero={len(zS)})")
# deciles
dec = pd.qcut(logkv_S.rank(method="first"), 10, labels=False)
top_d, bot_d = logkv_S.index[dec == 9], logkv_S.index[dec == 0]
mwu_d = stats.mannwhitneyu(fcP_exh.loc[top_d], fcP_exh.loc[bot_d],
                           alternative="greater")
results["deciles"] = {
    "top_decile_mean": float(fcP_exh.loc[top_d].mean()),
    "bottom_decile_mean": float(fcP_exh.loc[bot_d].mean()),
    "mannwhitney_p_one_sided": float(mwu_d.pvalue)}
print(f"[R-dec] protein deciles: top {fcP_exh.loc[top_d].mean():.3f} vs "
      f"bottom {fcP_exh.loc[bot_d].mean():.3f} (MWU p={mwu_d.pvalue:.2e})")

# ============================================================== artifacts
csv = pd.DataFrame({
    "kappa_V_max": panel_kv,
    "schmidt_prot_exh_maxfc": fcP_exh.reindex(panel_kv.index),
    "schmidt_prot_exh_signed": fcP_exh_signed.reindex(panel_kv.index),
    "schmidt_prot_lim_maxfc": class_max["limitation"].reindex(
        panel_kv.index),
    "schmidt_prot_switch_maxfc": class_max["switch"].reindex(
        panel_kv.index),
    "schmidt_prot_stress_maxfc": class_max["stress_glucose"].reindex(
        panel_kv.index),
    "e24_m3d_exh_maxfc": exh_max.reindex(panel_kv.index),
    "e25_gse_trans_maxfc": fcT_max.reindex(panel_kv.index),
}).join(e26[["gse_protein_maxfc"]] if e26 is not None else None)
csv.to_csv(DL / "novelty_v20_e27_schmidt_replication.csv")
with open(DL / "novelty_v20_e27_schmidt_replication_results.json", "w") as f:
    json.dump(results, f, indent=2)
lines = ["Study E27 (v20) Schmidt-2016 protein-layer replication"]
for tag, res in results["arms"].items():
    lines.append(f"[{tag}] n={res['n']} r={res['pearson_r']:+.4f} "
                 f"p={res['pearson_p']:.3e}")
for k, res in results["per_condition"].items():
    lines.append(f"[{k}] r={res['pearson_r']:+.4f} p={res['pearson_p']:.3e}")
(DL / "novelty_v20_e27_schmidt_replication.txt").write_text("\n".join(lines))
print("\n[artifacts] written: novelty_v20_e27_schmidt_replication"
      "{.csv,_results.json,.txt}")
