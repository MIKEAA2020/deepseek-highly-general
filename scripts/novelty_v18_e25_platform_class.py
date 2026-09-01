#!/usr/bin/env python3
"""
Study E25 (manuscript round v18): platform-vs-class disambiguation.

Motivation (user-directed review of E24): the E24 dissociation changed
platform AND perturbation class together --
  microarray (M3D)  x carbon-EXHAUSTION  -> r = +0.374 (p ~ 1e-15)
  RNA-seq  (PRECISE) x carbon-SWITCH     -> r = -0.054 (NS)
so the null has two readings (platform artifact vs class specificity).
E25 completes the 2x2 matrix with the two missing cells:

  [S1-array-switch]  microarray x carbon-SWITCH: the SAME Blattner/Allen
      MOPS series contains log-phase growth on alternative sole carbon
      sources (glycerol 11 mM, acetate 17 mM, proline 6.7 mM) vs the
      log-phase glucose reference (5 reps) -- same platform, lab, medium,
      strain; only the carbon source changes.
  [S2-seq-depletion] RNA-seq x carbon-DEPLETION: GEO GSE64021 (Su lab,
      UNC Charlotte; MG1655; directional RNA-seq + tandem-MS proteome)
      resuspends LB-grown cells in MOPS WITHOUT glucose ("M-C") vs the
      MOPS+glucose control, sampled 1/2/4/6 h -- glucose REMOVAL, the
      depletion class, on the RNA-seq platform that gave the null.

Discriminating predictions:
  H_class    (specific to depletion): r(S1) ~ 0  AND  r(S2) > 0
  H_platform (microarray artifact):   r(S1) > 0  AND  r(S2) ~ 0

Non-carbon stress controls (generic-stress specificity, same platforms):
  [S1b] M3D heat-shock (50 C, 10 min), acid shock (pH 2, 10 min),
        ciprofloxacin (10 min) -- all in MOPS + glucose, log phase.
  [S2b] GSE64021 phosphorus starvation (M-P = MOPS minus KH2PO4).
  [S2c] GSE64021 heat shock (HS = MOPS + glucose at 48 C), matched times.

All kappa_V values are taken UNCHANGED from the E22 artifact; log10
transform matches the E10-lineage definition; per-gene max|log2FC|
response metric matches E10/E24.  Correlations run over genes with
non-zero kappa_V variation only (the E22 panel guarantee).
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

RNG = np.random.default_rng(20260831)
DL = Path("/home/z/my-project/download")
M3D = Path("/home/z/my-project/data/m3d/E_coli_v4_Build_6")
GSE = Path("/home/z/my-project/data/gse64021")

# ==================================================================== stats
def corr_stats(x, y, n_perm=100_000, n_boot=10_000, label=""):
    """Pearson/Spearman + vectorized MC permutation + bootstrap CI."""
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
    r_perm = (zy[perms] @ zx) / n
    cnt = int((np.abs(r_perm) >= abs(pr) - 1e-12).sum())
    perm_p = (cnt + 1) / (n_perm + 1)
    idx = rng.integers(0, n, size=(n_boot, n))
    rb = []
    for row in idx:
        xb, yb = x[row], y[row]
        if xb.std() > 0 and yb.std() > 0:
            rb.append(np.corrcoef(xb, yb)[0, 1])
    rb = np.asarray(rb)
    lo, hi = (np.percentile(rb, 2.5), np.percentile(rb, 97.5)
              if len(rb) else (np.nan, np.nan))
    return {"label": label, "n": int(n), "pearson_r": float(pr),
            "pearson_p": float(pp), "spearman_r": float(sr),
            "spearman_p": float(sp), "perm_p_mc": float(perm_p),
            "boot_ci95": [float(lo), float(hi)]}


def fisher_z_test(r1, n1, r2, n2):
    """Two-sample z-test for difference of independent correlations."""
    z1, z2 = np.arctanh(r1), np.arctanh(r2)
    se = np.sqrt(1.0 / (n1 - 3) + 1.0 / (n2 - 3))
    zstat = (z1 - z2) / se
    p = 2 * (1 - stats.norm.cdf(abs(zstat)))
    return {"z": float(zstat), "p": float(p),
            "r1": float(r1), "n1": int(n1), "r2": float(r2), "n2": int(n2)}


def report(tag, res):
    print(f"  [{tag}] n={res['n']:4d}  r={res['pearson_r']:+.4f} "
          f"(p={res['pearson_p']:.2e})  rho={res['spearman_r']:+.4f} "
          f"(p={res['spearman_p']:.2e})  perm_p={res['perm_p_mc']:.4f} "
          f"CI=[{res['boot_ci95'][0]:+.3f},{res['boot_ci95'][1]:+.3f}]")
    return res


# ==================================================== load E22 panel (fixed)
e22 = pd.read_csv(DL / "novelty_v15_reaction_sampling_e22.csv")
e22 = e22.set_index("gene_bnumber")
panel_kv = e22["kappa_V_max"].astype(float)
logkv_panel = np.log10(panel_kv)
panel_gpr = e22["dominant_gpr_class"].astype(str)

# ====================================================== load M3D (as E24)
expr = pd.read_csv(M3D / "E_coli_v4_Build_6_chips907probes4297.tab",
                   sep="\t", index_col=0)
psd = pd.read_csv(M3D / "E_coli_v4_Build_6.probe_set_descriptions", sep="\t")
locus_of = dict(zip(psd["probe_set_name"], psd["locus"].astype(str)))
expr.index = [locus_of.get(p, p) for p in expr.index]
if expr.index.duplicated(keep=False).any():
    expr = expr.groupby(level=0).mean()
print(f"[load] M3D matrix: {expr.shape[0]} genes x {expr.shape[1]} chips")

REF = [f"WT_MOPS_glucose_r{i}" for i in range(1, 6)]       # log, 5 reps
SWITCH = {
    "glycerol": [f"WT_MOPS_glycerol_r{i}" for i in (1, 2)],
    "acetate": [f"WT_MOPS_acetate_r{i}" for i in (1, 2)],
    "proline": [f"WT_MOPS_proline_r{i}" for i in (1, 2)],
}
STRESS_M3D = {
    "heatShock": ["WT_MOPS_heatShock_r1"],
    "acidShock": [f"WT_MOPS_acidShock_r{i}" for i in (1, 2)],
    "cipro": ["WT_MOPS_cipro_r1", "WT_MOPS_cipro2_r1"],
}
need = (REF + sum(SWITCH.values(), []) + sum(STRESS_M3D.values(), []))
missing = [c for c in need if c not in expr.columns]
assert not missing, f"missing M3D chips: {missing}"

ref_mean = expr[REF].mean(axis=1)
fc_m3d = pd.DataFrame({
    **{f"array_switch_{k}": expr[v].mean(axis=1) - ref_mean
       for k, v in SWITCH.items()},
    **{f"array_stress_{k}": expr[v].mean(axis=1) - ref_mean
       for k, v in STRESS_M3D.items()},
})
fc_m3d["array_switch_max"] = fc_m3d[[
    "array_switch_glycerol", "array_switch_acetate",
    "array_switch_proline"]].abs().max(axis=1)
fc_m3d["array_stress_max"] = fc_m3d[[
    "array_stress_heatShock", "array_stress_acidShock",
    "array_stress_cipro"]].abs().max(axis=1)

in_m3d = panel_kv.index.isin(fc_m3d.index)
print(f"[S1] panel coverage in M3D: {int(in_m3d.sum())}/{len(panel_kv)} "
      f"(absent: {list(panel_kv.index[~in_m3d])})")

# ==================================================== load GSE64021 (RNA-seq)
gse_files = {
    "MOPS_1h": "MOPS_1h.csv", "MOPS_2h": "MOPS_2h.csv",
    "MOPS_4h": "MOPS_4h.csv", "MOPS_6h": "MOPS_6h.csv",
    "MC_1h": "MC_1h.csv", "MC_2h": "MC_2h.csv",
    "MC_4h": "MC_4h.csv", "MC_6h": "MC_6h.csv",
    "MC_1h_PE": "MC_1h_PE.csv", "MC_2h_PE": "MC_2h_PE.csv",
    "MP_1h": "MP_1h.csv", "MP_2h": "MP_2h.csv",
    "MP_4h": "MP_4h.csv", "MP_6h": "MP_6h.csv",
    "HS_1h": "HS_1h.csv", "HS_2h": "HS_2h.csv", "HS_4h": "HS_4h.csv",
}
# gene-name -> b-number map (PRECISE gene_info; local, b-number index)
gi = pd.read_csv("/home/z/my-project/data/precise/data/gene_info.csv",
                 index_col=0)
name_to_b = {}
for bnum, row in gi.iterrows():
    name_to_b[str(row["gene_name"]).strip()] = bnum
# also allow the model's own genes (iJO1366 synonyms not in PRECISE)
try:
    import cobra
    model = cobra.io.load_json_model(
        "/home/z/my-project/data/bigg_models/iJO1366.json")
    for g in model.genes:
        if g.name:
            name_to_b.setdefault(str(g.name).strip(), g.id)
    model_src = "iJO1366 cobrapy"
except Exception:
    model_src = "unavailable"
print(f"[load] gene-name->b-number map: {len(name_to_b)} names "
      f"(PRECISE gene_info + {model_src})")

tpm = {}
unmapped_rows, dup_names = [], 0
for tag, fn in gse_files.items():
    d = pd.read_csv(GSE / fn, sep="\t")
    d["Gene"] = d["Gene"].astype(str).str.strip()
    ser = {}
    for gene, val in zip(d["Gene"], d["mRNATPM"]):
        b = name_to_b.get(gene)
        if b is None:
            unmapped_rows.append((tag, gene))
            continue
        if b in ser:
            dup_names += 1
        ser[b] = float(val)      # duplicates: last wins (rare, reported)
    tpm[tag] = pd.Series(ser)
tpm = pd.DataFrame(tpm)
print(f"[load] GSE64021 TPM matrix: {tpm.shape[0]} genes x {tpm.shape[1]} "
      f"samples; unmapped rows: {len(set(g for _, g in unmapped_rows))}; "
      f"duplicate-name overwrites: {dup_names}")

log2t = np.log2(tpm + 1.0)
fc_gse = pd.DataFrame({
    f"seq_carbonstarve_{t}": log2t[f"MC_{t}"] - log2t[f"MOPS_{t}"]
    for t in ("1h", "2h", "4h", "6h")})
fc_gse["seq_carbonstarve_max"] = fc_gse[
    [f"seq_carbonstarve_{t}" for t in ("1h", "2h", "4h", "6h")]
].abs().max(axis=1)
# sensitivity: PE libraries merged into MC 1h/2h
log2t_pe = log2t.copy()
log2t_pe["MC_1h"] = (log2t["MC_1h"] + log2t["MC_1h_PE"]) / 2
log2t_pe["MC_2h"] = (log2t["MC_2h"] + log2t["MC_2h_PE"]) / 2
fc_gse["seq_carbonstarve_max_PEmerged"] = pd.concat([
    log2t_pe["MC_1h"] - log2t_pe["MOPS_1h"],
    log2t_pe["MC_2h"] - log2t_pe["MOPS_2h"],
    log2t_pe["MC_4h"] - log2t_pe["MOPS_4h"],
    log2t_pe["MC_6h"] - log2t_pe["MOPS_6h"]], axis=1).abs().max(axis=1)
# non-carbon controls
fc_gse["seq_phosphorus_max"] = pd.concat([
    log2t[f"MP_{t}"] - log2t[f"MOPS_{t}"]
    for t in ("1h", "2h", "4h", "6h")], axis=1).abs().max(axis=1)
fc_gse["seq_heatshock_max"] = pd.concat([
    log2t[f"HS_{t}"] - log2t[f"MOPS_{t}"]
    for t in ("1h", "2h", "4h")], axis=1).abs().max(axis=1)
# mean-metric sensitivities
fc_gse["seq_carbonstarve_mean"] = fc_gse[
    [f"seq_carbonstarve_{t}" for t in ("1h", "2h", "4h", "6h")]
].abs().mean(axis=1)
fc_gse["seq_carbonstarve_6h_only"] = fc_gse["seq_carbonstarve_6h"]

in_gse = panel_kv.index.isin(fc_gse.index)
print(f"[S2] panel coverage in GSE64021: {int(in_gse.sum())}/{len(panel_kv)} "
      f"(absent: {list(panel_kv.index[~in_gse])})")

# ============================================================= correlations
results = {"study": "E25_platform_vs_class", "arms": {},
           "panel": {"E22_panel_size": int(len(panel_kv)),
                     "with_m3d_expression": int(in_m3d.sum()),
                     "with_gse_expression": int(in_gse.sum())}}

print("\n[S1] M3D microarray x carbon-SWITCH (same platform as the positive):")
kv1 = logkv_panel[in_m3d]
for k in ("glycerol", "acetate", "proline"):
    results["arms"][f"array-switch-{k}"] = report(
        f"array-switch-{k}",
        corr_stats(kv1, fc_m3d[f"array_switch_{k}"].abs().loc[kv1.index],
                   label=f"array switch {k} (|FC|)"))
results["arms"]["array-switch-MAX(primary)"] = report(
    "array-switch-MAX(primary)",
    corr_stats(kv1, fc_m3d.loc[kv1.index, "array_switch_max"],
               label="array switch MAX"))
for k in ("glycerol", "acetate", "proline"):
    results["arms"][f"array-switch-{k}-SIGNED"] = report(
        f"array-switch-{k}-SIGNED",
        corr_stats(kv1, fc_m3d[f"array_switch_{k}"].loc[kv1.index],
                   label=f"array switch {k} (signed)"))

print("\n[S1b] M3D microarray x non-carbon stress (same platform, generic stress):")
for k in ("heatShock", "acidShock", "cipro"):
    results["arms"][f"array-stress-{k}"] = report(
        f"array-stress-{k}",
        corr_stats(kv1, fc_m3d[f"array_stress_{k}"].abs().loc[kv1.index],
                   label=f"array stress {k} (|FC|)"))
results["arms"]["array-stress-MAX"] = report(
    "array-stress-MAX",
    corr_stats(kv1, fc_m3d.loc[kv1.index, "array_stress_max"],
               label="array stress MAX"))
for k in ("heatShock", "acidShock", "cipro"):
    results["arms"][f"array-stress-{k}-SIGNED"] = report(
        f"array-stress-{k}-SIGNED",
        corr_stats(kv1, fc_m3d[f"array_stress_{k}"].loc[kv1.index],
                   label=f"array stress {k} (signed)"))

print("\n[S2] GSE64021 RNA-seq x carbon-DEPLETION (same platform as the null):")
kv2 = logkv_panel[in_gse]
for t in ("1h", "2h", "4h", "6h"):
    results["arms"][f"seq-carbonstarve-{t}"] = report(
        f"seq-carbonstarve-{t}",
        corr_stats(kv2, fc_gse[f"seq_carbonstarve_{t}"].abs().loc[kv2.index],
                   label=f"carbonstarve {t} (|FC|)"))
for t in ("1h", "2h", "4h", "6h"):
    results["arms"][f"seq-carbonstarve-{t}-SIGNED"] = report(
        f"seq-carbonstarve-{t}-SIGNED",
        corr_stats(kv2, fc_gse[f"seq_carbonstarve_{t}"].loc[kv2.index],
                   label=f"carbonstarve {t} (signed)"))
for col, tag in [
        ("seq_carbonstarve_max", "seq-carbonstarve-MAX(primary)"),
        ("seq_carbonstarve_max_PEmerged", "seq-carbonstarve-MAX-PEmerged"),
        ("seq_carbonstarve_mean", "seq-carbonstarve-mean"),
        ("seq_carbonstarve_6h_only", "seq-carbonstarve-6h-only")]:
    results["arms"][tag] = report(
        tag, corr_stats(kv2, fc_gse.loc[kv2.index, col], label=tag))

print("\n[S2b/c] GSE64021 RNA-seq x non-carbon (phosphorus starvation, heat):")
for col, tag in [("seq_phosphorus_max", "seq-phosphorus-MAX"),
                 ("seq_heatshock_max", "seq-heatshock-MAX")]:
    results["arms"][tag] = report(
        tag, corr_stats(kv2, fc_gse.loc[kv2.index, col], label=tag))

# ---- per-time resolution for the non-carbon RNA-seq controls ------------
# |FC| convention (matches E24); signed variants kept separately.
for t in ("1h", "2h", "4h"):
    results["arms"][f"seq-heatshock-{t}"] = report(
        f"seq-heatshock-{t}",
        corr_stats(kv2, (log2t[f"HS_{t}"] - log2t[f"MOPS_{t}"]).abs()
                   .loc[kv2.index], label=f"heatshock {t} (|FC|)"))
    results["arms"][f"seq-heatshock-{t}-SIGNED"] = report(
        f"seq-heatshock-{t}-SIGNED",
        corr_stats(kv2, (log2t[f"HS_{t}"] - log2t[f"MOPS_{t}"])
                   .loc[kv2.index], label=f"heatshock {t} (signed)"))
for t in ("1h", "2h", "4h", "6h"):
    results["arms"][f"seq-phosphorus-{t}"] = report(
        f"seq-phosphorus-{t}",
        corr_stats(kv2, (log2t[f"MP_{t}"] - log2t[f"MOPS_{t}"]).abs()
                   .loc[kv2.index], label=f"phosphorus {t} (|FC|)"))

# ---- RNA-seq zero-inflation sensitivities (TPM=0 -> big |log2FC|) -------
# (a) pseudocount 0.5 instead of 1; (b) restrict to genes with TPM>=1 in
# BOTH members of every contrast used by the MAX metric (measurable FC).
log2t_pc = np.log2(tpm + 0.5)
fc_pc = pd.concat([
    log2t_pc[f"MC_{t}"] - log2t_pc[f"MOPS_{t}"]
    for t in ("1h", "2h", "4h", "6h")], axis=1).abs().max(axis=1)
results["arms"]["seq-carbonstarve-MAX-pseudocount0.5"] = report(
    "seq-carbonstarve-MAX-pseudocount0.5",
    corr_stats(kv2, fc_pc.loc[kv2.index], label="pseudocount 0.5"))
ok = np.ones(len(tpm), bool)
for t in ("1h", "2h", "4h", "6h"):
    ok &= (tpm[f"MC_{t}"].values >= 1) & (tpm[f"MOPS_{t}"].values >= 1)
measurable = pd.Series(ok, index=tpm.index)
sub = [g for g in kv2.index if measurable.get(g, False)]
results["arms"]["seq-carbonstarve-MAX-TPMfilter"] = report(
    "seq-carbonstarve-MAX-TPMfilter",
    corr_stats(logkv_panel.loc[sub],
               fc_gse.loc[sub, "seq_carbonstarve_max"],
               label=f"TPM>=1 in both, n={len(sub)}"))

# ---- does the MOPS control arm itself exhaust by 6h? --------------------
# |MOPS_6h - MOPS_1h| tracks growth-phase progression inside the control;
# if high-kappa genes move there too, the 6h wash-out is a control-arm
# contamination (both arms carbon-limited), not a failure of the signal.
results["arms"]["seq-MOPScontrol-own-timecourse"] = report(
    "seq-MOPScontrol-own-timecourse",
    corr_stats(kv2, (log2t["MOPS_6h"] - log2t["MOPS_1h"]).abs()
               .loc[kv2.index], label="MOPS 6h vs 1h (|FC|)"))

# ===================================== E24 anchors + 2x2 discrimination tests
e24 = json.load(open(DL / "novelty_v17_option_a_e24_results.json"))
r_array_depl = e24["arms"]["A_panel"]["pearson_r"]
n_array_depl = e24["arms"]["A_panel"]["n"]
r_seq_switch = e24["arms"]["A_replicate_precise"]["pearson_r"]
n_seq_switch = e24["arms"]["A_replicate_precise"]["n"]
r_array_switch = results["arms"]["array-switch-MAX(primary)"]["pearson_r"]
n_array_switch = results["arms"]["array-switch-MAX(primary)"]["n"]
r_seq_depl = results["arms"]["seq-carbonstarve-MAX(primary)"]["pearson_r"]
n_seq_depl = results["arms"]["seq-carbonstarve-MAX(primary)"]["n"]

print("\n[2x2] platform x class matrix (per-gene max|log2FC| metric):")
print(f"                     carbon-depletion   carbon-switch")
print(f"  microarray (M3D)   {r_array_depl:+.4f} (n={n_array_depl})   "
      f"{r_array_switch:+.4f} (n={n_array_switch})")
print(f"  RNA-seq            {r_seq_depl:+.4f} (n={n_seq_depl})   "
      f"{r_seq_switch:+.4f} (n={n_seq_switch})")

results["matrix_2x2"] = {
    "microarray_depletion": {"r": r_array_depl, "n": n_array_depl,
                             "source": "E24 A-panel"},
    "microarray_switch": {"r": r_array_switch, "n": n_array_switch,
                          "source": "E25 S1"},
    "rnaseq_depletion": {"r": r_seq_depl, "n": n_seq_depl,
                         "source": "E25 S2 GSE64021"},
    "rnaseq_switch": {"r": r_seq_switch, "n": n_seq_switch,
                      "source": "E24 A-replicate PRECISE"},
    "class_effect_switch_array_vs_depletion_array": fisher_z_test(
        r_array_switch, n_array_switch, r_array_depl, n_array_depl),
    "class_effect_depletion_seq_vs_switch_seq": fisher_z_test(
        r_seq_depl, n_seq_depl, r_seq_switch, n_seq_switch),
    "platform_effect_depletion": fisher_z_test(
        r_seq_depl, n_seq_depl, r_array_depl, n_array_depl),
    "platform_effect_switch": fisher_z_test(
        r_array_switch, n_array_switch, r_seq_switch, n_seq_switch),
}
for k, v in results["matrix_2x2"].items():
    if isinstance(v, dict) and "z" in v:
        print(f"  {k}: z={v['z']:+.2f}  p={v['p']:.3g}")

# ===================== common-set 2x2 (removes gene-set coverage confound)
# The four cells above rest on different gene sets (M3D 433 vs GSE 241).
# Restrict ALL FOUR cells to the genes covered by BOTH platforms so the
# platform/class comparisons are within one fixed gene set.
common = [g for g in panel_kv.index
          if g in fc_m3d.index and g in fc_gse.index]
kvc = logkv_panel.loc[common]
print(f"\n[S-common] common gene set (M3D AND GSE64021 coverage): "
      f"n = {len(common)}")

# recompute the E24 exhaustion metric on the common set (same definition)
STAT = {
    "stationary_135min": [f"WT_MOPS_stationary_r{i}" for i in (1, 2)],
    "stationary_330min": [f"WT_MOPS_stationary2_r{i}" for i in (1, 2)],
    "stationary_480min": [f"WT_MOPS_stationary3_r{i}" for i in (1, 2)],
    "stationary_720min": [f"WT_MOPS_stationary4_r{i}" for i in (1, 2)],
}
exh = pd.DataFrame({k: expr[v].mean(axis=1) - ref_mean
                    for k, v in STAT.items()})
exh_max = exh.abs().max(axis=1)
c_array_depl = report("common-array-DEPLETION",
                      corr_stats(kvc, exh_max.loc[common],
                                 label="common array depletion"))
c_array_switch = report("common-array-SWITCH",
                        corr_stats(kvc,
                                   fc_m3d.loc[common, "array_switch_max"],
                                   label="common array switch"))
c_seq_depl = report("common-RNAseq-DEPLETION",
                    corr_stats(kvc,
                               fc_gse.loc[common, "seq_carbonstarve_max"],
                               label="common seq depletion"))
# PRECISE switch (RNA-seq) on the common set: recompute from PRECISE
lt = pd.read_csv("/home/z/my-project/data/precise/data/log_tpm.csv",
                 index_col=0)
md = pd.read_csv("/home/z/my-project/data/precise/data/metadata.csv"
                 ).set_index("Sample ID")
md["Carbon Source (g/L)"] = md["Carbon Source (g/L)"].astype(str)
md["Condition ID"] = md["Condition ID"].astype(str)
ctrl = [c for c in lt.columns if c.startswith("control__wt_glc__")]
ctrl_mean = lt[ctrl].mean(axis=1)
wt_carbon = {}
for cid, grp in md.groupby("Condition ID"):
    if cid in ("wt_glc", "no3_anaero", "wt_glyc", "thm_gal") \
            or cid.endswith("_pq"):
        continue
    carb = grp["Carbon Source (g/L)"].iloc[0]
    base = str(grp["Base Media"].iloc[0])
    if "glucose" in carb or carb == "nan" or "LB" in base:
        continue
    sids = [s for s in grp.index if s in lt.columns]
    strain, evolved = grp["Strain"].iloc[0], str(grp["Evolved Sample"].iloc[0])
    if "MG1655" not in str(strain) or "Yes" in evolved:
        continue
    low = cid.lower()
    if any(w in low for w in ["del", "ko", "mut", "pbad", "plasmid", "evo",
                              "ale", "ar1", "ar2", "isol", "adapt"]):
        continue
    if len(sids) >= 2:
        wt_carbon[cid] = sids
fc_prec_common = pd.DataFrame(
    {c: lt[s].mean(axis=1) - ctrl_mean for c, s in wt_carbon.items()})
prec_switch_max = fc_prec_common.abs().max(axis=1)
c_seq_switch = report("common-RNAseq-SWITCH(PRECISE)",
                      corr_stats(kvc, prec_switch_max.loc[common],
                                 label="common seq switch PRECISE"))

common_matrix = {
    "n_common": int(len(common)),
    "microarray_depletion": c_array_depl,
    "microarray_switch": c_array_switch,
    "rnaseq_depletion": c_seq_depl,
    "rnaseq_switch_precise": c_seq_switch,
    "class_effect_array": fisher_z_test(
        c_array_switch["pearson_r"], c_array_switch["n"],
        c_array_depl["pearson_r"], c_array_depl["n"]),
    "class_effect_rnaseq": fisher_z_test(
        c_seq_depl["pearson_r"], c_seq_depl["n"],
        c_seq_switch["pearson_r"], c_seq_switch["n"]),
    "platform_effect_depletion": fisher_z_test(
        c_seq_depl["pearson_r"], c_seq_depl["n"],
        c_array_depl["pearson_r"], c_array_depl["n"]),
    "platform_effect_switch": fisher_z_test(
        c_array_switch["pearson_r"], c_array_switch["n"],
        c_seq_switch["pearson_r"], c_seq_switch["n"]),
}
print(f"  common-set matrix:      depletion   switch")
print(f"    microarray (M3D)     {c_array_depl['pearson_r']:+.4f}      "
      f"{c_array_switch['pearson_r']:+.4f}")
print(f"    RNA-seq              {c_seq_depl['pearson_r']:+.4f}      "
      f"{c_seq_switch['pearson_r']:+.4f}")
for k, v in common_matrix.items():
    if isinstance(v, dict) and "z" in v:
        print(f"    {k}: z={v['z']:+.2f}  p={v['p']:.3g}")
results["matrix_2x2_common_set"] = common_matrix

# ============================================ deciles of the primary new cell
order = np.argsort(kvc.values)
dec = int(np.ceil(0.1 * len(common)))
top_i = kvc.index[order[-dec:]]
bot_i = kvc.index[order[:dec]]
resp = fc_gse.loc[common, "seq_carbonstarve_max"]
mwu_dec = stats.mannwhitneyu(resp.loc[top_i].dropna(),
                             resp.loc[bot_i].dropna(), alternative="greater")
results["seq_depletion_deciles"] = {
    "n_decile": int(dec),
    "top_decile_mean_fc": float(resp.loc[top_i].mean()),
    "bottom_decile_mean_fc": float(resp.loc[bot_i].mean()),
    "mannwhitney_p_one_sided": float(mwu_dec.pvalue)}
print(f"\n[S-dec] RNA-seq depletion deciles: top {resp.loc[top_i].mean():.3f} "
      f"vs bottom {resp.loc[bot_i].mean():.3f} (MWU p={mwu_dec.pvalue:.2e})")

# ============================================ zero-kappa control on GSE64021
zero_genes = [g for g in e22.index if e22.loc[g, "kappa_V_max"] == 0.0] \
    if "kappa_V_max" in e22 else []
if not zero_genes:
    # all E22 rows have non-zero kappa by construction; use iJO1366 genes
    # whose baseline reactions are all inactive (the E24 [A-zero] control)
    all_model_genes = set()
    try:
        import cobra
        model = cobra.io.load_json_model(
            "/home/z/my-project/data/bigg_models/iJO1366.json")
        all_model_genes = {g.id for g in model.genes}
    except Exception:
        pass
    zero_genes = sorted(all_model_genes - set(panel_kv.index))
    n_zero = len(zero_genes)
    zero_in_gse = [g for g in zero_genes if g in fc_gse.index]
    panel_resp = fc_gse.loc[kv2.index, "seq_carbonstarve_max"]
    zero_resp = fc_gse.loc[zero_in_gse, "seq_carbonstarve_max"]
    mwu = stats.mannwhitneyu(panel_resp.dropna(), zero_resp.dropna(),
                             alternative="greater")
    results["zero_control_gse"] = {
        "n_zero_kappa_genes_model": int(n_zero),
        "n_zero_with_gse": int(len(zero_in_gse)),
        "panel_mean_max_fc": float(panel_resp.mean()),
        "zero_mean_max_fc": float(zero_resp.mean()),
        "panel_median": float(panel_resp.median()),
        "zero_median": float(zero_resp.median()),
        "mannwhitney_p_one_sided_panel_gt_zero": float(mwu.pvalue)}
    print(f"\n[S-zero] RNA-seq zero-kappa control: panel mean "
          f"{panel_resp.mean():.3f} vs zero-kappa mean "
          f"{zero_resp.mean():.3f} (MWU p={mwu.pvalue:.2e}, "
          f"n_zero={len(zero_in_gse)})")

# ============================================================== artifacts
csv = pd.DataFrame({
    "kappa_V_max": panel_kv,
    "gpr_class": panel_gpr,
}).join(fc_m3d, how="left").join(fc_gse, how="left")
csv.to_csv(DL / "novelty_v18_e25_platform_class.csv")

png_spec = {
    "matrix": [[r_array_depl, r_array_switch], [r_seq_depl, r_seq_switch]],
    "matrix_common": [[c_array_depl["pearson_r"], c_array_switch["pearson_r"]],
                      [c_seq_depl["pearson_r"], c_seq_switch["pearson_r"]]],
    "switch_conditions_array": {
        k: results["arms"][f"array-switch-{k}"]["pearson_r"]
        for k in ("glycerol", "acetate", "proline")},
    "starve_times_seq": {
        t: results["arms"][f"seq-carbonstarve-{t}"]["pearson_r"]
        for t in ("1h", "2h", "4h", "6h")},
    "non_carbon_controls": {
        "array-heat": results["arms"]["array-stress-heatShock"]["pearson_r"],
        "array-acid": results["arms"]["array-stress-acidShock"]["pearson_r"],
        "array-cipro": results["arms"]["array-stress-cipro"]["pearson_r"],
        "seq-phosphorus": results["arms"]["seq-phosphorus-MAX"]["pearson_r"],
        "seq-heatshock": results["arms"]["seq-heatshock-MAX"]["pearson_r"]},
}
results["plot_data"] = png_spec
with open(DL / "novelty_v18_e25_platform_class_results.json", "w") as f:
    json.dump(results, f, indent=2)

txt = [f"Study E25 (v18) platform-vs-class disambiguation",
       f"panel: E22 kappa_V, {len(panel_kv)} genes "
       f"({int(in_m3d.sum())} with M3D, {int(in_gse.sum())} with GSE64021 "
       f"expression)", ""]
for tag, res in results["arms"].items():
    txt.append(f"[{tag}] n={res['n']} r={res['pearson_r']:+.4f} "
               f"p={res['pearson_p']:.3e} rho={res['spearman_r']:+.4f} "
               f"perm_p={res['perm_p_mc']:.4f} "
               f"CI=[{res['boot_ci95'][0]:+.3f},{res['boot_ci95'][1]:+.3f}]")
(DL / "novelty_v18_e25_platform_class.txt").write_text("\n".join(txt))
print("\n[artifacts] written: novelty_v18_e25_platform_class"
      "{.csv,_results.json,.txt}")
