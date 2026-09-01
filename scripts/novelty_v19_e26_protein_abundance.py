#!/usr/bin/env python3
"""
Study E26 (manuscript round v19): protein-abundance mechanistic test.

Motivation (user-directed review of E24/E25): now that the
kappa_V -- transcript-response association is established and
platform-robust, the next scientific question is WHY it exists.
The earlier lineage hypothesis -- heavy-flux-perturbation genes are
regulated post-translationally while small-perturbation genes rely on
transcriptional compensation (retracted as an artifact at n=15 in
v14b, but testable properly now) -- is re-examined with protein data:

  [P-paxdb]   PaxDb v6.1 integrated whole-organism proteome (511145,
              3,747 proteins, 91% coverage): baseline abundance --
              (a) does kappa_V track protein abundance at all?
              (b) does protein abundance MEDIATE the kappa_V ->
                  transcript association (beyond mRNA level)?
              (c) EFFECT MODIFICATION: is the association
                  concentrated in low-abundance enzymes (where
                  transcription must act to move capacity) and
                  absent in high-abundance ones (buffered by mass
                  action / long half-lives)?
  [P-protfc]  GSE64021 PeptideRaw (tandem-MS spectral counts, matched
              M-C vs MOPS carbon starvation, 1/2/4/6 h): does the
              kappa_V -> response association EXTEND TO PROTEIN
              fold-changes (r(kappa, max|log2 dP|))?
  [P-tp]      transcript-protein coupling, stratified by kappa_V:
              H_compensation  -- high-kappa transcripts are
                                 IMPLEMENTED (protein follows RNA);
              H_buffering     -- high-kappa transcripts are signal
                                 without implementation (protein
                                 decoupled);
              measured as r(signed dT, signed dP) per kappa_V
              tertile and the |dP|/|dT| implementation ratio.

kappa_V values are taken UNCHANGED from the E22 artifact; the
transcript metrics are the E24 (M3D carbon exhaustion, n=433) and
E25 (GSE64021 RNA-seq carbon starvation, n=241) primary metrics.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

DL = Path("/home/z/my-project/download")
M3D = Path("/home/z/my-project/data/m3d/E_coli_v4_Build_6")
GSE = Path("/home/z/my-project/data/gse64021")

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


def partial_r(x, y, covars):
    """Partial correlation of x,y controlling the (n,k) covar matrix."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    C = np.asarray(covars, float)
    if C.ndim == 1:
        C = C[:, None]
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(C).all(axis=1)
    x, y, C = x[ok], y[ok], C[ok]
    X = np.column_stack([np.ones(len(x)), C])
    bx, *_ = np.linalg.lstsq(X, x, rcond=None)
    by, *_ = np.linalg.lstsq(X, y, rcond=None)
    rx, ry = x - X @ bx, y - X @ by
    if rx.std() == 0 or ry.std() == 0:
        return {"pearson_r": float("nan"), "pearson_p": float("nan"),
                "n": int(len(x))}
    r, p = stats.pearsonr(rx, ry)
    return {"pearson_r": float(r), "pearson_p": float(p), "n": int(len(x))}


# ==================================================== panel (kappa_V fixed)
e22 = pd.read_csv(DL / "novelty_v15_reaction_sampling_e22.csv")
e22 = e22.set_index("gene_bnumber")
panel_kv = e22["kappa_V_max"].astype(float)
logkv_panel = np.log10(panel_kv)

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
exh_max = pd.concat(
    [expr[v].mean(axis=1) - ref_mean for v in STAT.values()],
    axis=1).abs().max(axis=1)

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
except Exception:
    pass
gse_tags = {"MOPS_1h": "MOPS_1h.csv", "MOPS_2h": "MOPS_2h.csv",
            "MOPS_4h": "MOPS_4h.csv", "MOPS_6h": "MOPS_6h.csv",
            "MC_1h": "MC_1h.csv", "MC_2h": "MC_2h.csv",
            "MC_4h": "MC_4h.csv", "MC_6h": "MC_6h.csv"}
tpm, pep = {}, {}
for tag, fn in gse_tags.items():
    d = pd.read_csv(GSE / fn, sep="\t")
    d["Gene"] = d["Gene"].astype(str).str.strip()
    idx = [name_to_b.get(g, g) for g in d["Gene"]]
    tpm[tag] = pd.Series(d["mRNATPM"].values, index=idx)
    pep[tag] = pd.Series(pd.to_numeric(d["PeptideRaw"], errors="coerce"
                                       ).values, index=idx)
tpm = pd.DataFrame(tpm).groupby(level=0).mean()
pep = pd.DataFrame(pep).groupby(level=0).mean()
log2t = np.log2(tpm + 1.0)
fcT = pd.DataFrame({t: log2t[f"MC_{t}"] - log2t[f"MOPS_{t}"]
                    for t in ("1h", "2h", "4h", "6h")})
fcT_max = fcT.abs().max(axis=1)
log2p = np.log2(pep + 1.0)
fcP = pd.DataFrame({t: log2p[f"MC_{t}"] - log2p[f"MOPS_{t}"]
                    for t in ("1h", "2h", "4h", "6h")})
fcP_max = fcP.abs().max(axis=1, skipna=True)

# ================================================================== PaxDB
pax = pd.read_csv("/home/z/my-project/data/paxdb/"
                  "511145-WHOLE_ORGANISM-integrated.txt", sep="\t",
                  comment="#", names=["gene_name", "string_id", "abundance"])
pax["bnum"] = pax["string_id"].str.split(".").str[-1]
pax = pax.set_index("bnum")["abundance"].astype(float)
log_pax = np.log10(pax)

results = {"study": "E26_protein_abundance", "arms": {}}

# ------------------------------------------ [P-paxdb] baseline association
genes_pax = [g for g in panel_kv.index if g in log_pax.index]
results["arms"]["paxdb-kappaV-baseline"] = report(
    "paxdb-kappaV-baseline",
    corr_stats(logkv_panel.loc[genes_pax], log_pax.loc[genes_pax],
               label="log10 kappa_V vs log10 PaxDB ppm"))
print(f"[P-paxdb] panel coverage in PaxDB: {len(genes_pax)}/435")

# ----------------------------------- [P-paxdb-confound] mediation control
genes_all = [g for g in panel_kv.index
             if g in exh_max.index and g in log_pax.index
             and np.isfinite(exh_max.get(g, np.nan))
             and np.isfinite(log_pax.get(g, np.nan))]
x = logkv_panel.loc[genes_all].values
y = exh_max.loc[genes_all].values
mlevel = ref_mean.loc[genes_all].values        # mRNA level (E24 control)
pab = log_pax.loc[genes_all].values            # protein abundance
r_mrna_prot = stats.pearsonr(mlevel, pab)
results["paxdb_confound"] = {
    "n": len(genes_all),
    "r_mRNAlevel_vs_proteinAbundance": float(r_mrna_prot[0]),
    "p_mRNAlevel_vs_proteinAbundance": float(r_mrna_prot[1]),
    "partial_kappaT_given_mRNA": partial_r(x, y, mlevel),
    "partial_kappaT_given_mRNA_and_protein": partial_r(x, y,
                                                       np.column_stack(
                                                           [mlevel, pab])),
}
print(f"[P-paxdb-confound] r(mRNA level, protein abundance) = "
      f"{r_mrna_prot[0]:+.3f}")
print(f"  partial r(kappa, T | mRNA)         = "
      f"{results['paxdb_confound']['partial_kappaT_given_mRNA']['pearson_r']:+.3f}")
print(f"  partial r(kappa, T | mRNA, protein)= "
      f"{results['paxdb_confound']['partial_kappaT_given_mRNA_and_protein']['pearson_r']:+.3f}")

# ------------------------------------ [P-paxdb-strata] effect modification
ab = log_pax.loc[genes_all]
q1, q2 = ab.quantile([1 / 3, 2 / 3])
strata = {"low-abundance": ab <= q1, "mid-abundance": (ab > q1) & (ab <= q2),
          "high-abundance": ab > q2}
results["paxdb_strata"] = {}
print(f"[P-paxdb-strata] tertile cut points: log10 ppm {q1:.2f} / {q2:.2f}")
for name, mask in strata.items():
    gsub = [g for g, m in zip(genes_all, mask) if m]
    results["paxdb_strata"][name] = report(
        f"paxdb-strata-{name}",
        corr_stats(logkv_panel.loc[gsub], exh_max.loc[gsub],
                   label=f"E24 metric in {name} tertile"))

# ------------------------------------------------ [P-protfc] protein FC
genes_prot = [g for g in panel_kv.index
              if np.isfinite(fcP_max.get(g, np.nan))]
print(f"\n[P-protfc] panel genes with matched protein FC: "
      f"{len(genes_prot)}/435")
# apples-to-apples: the TRANSCRIPT association on the SAME gene subset
results["arms"]["transfc-kappaV-on-protein-subset"] = report(
    "transfc-kappaV-on-protein-subset",
    corr_stats(logkv_panel.loc[genes_prot], fcT_max.loc[genes_prot],
               label="transcript max|FC| on the protein subset"))
results["arms"]["m3dtfc-kappaV-on-protein-subset"] = report(
    "m3dtfc-kappaV-on-protein-subset",
    corr_stats(logkv_panel.loc[genes_prot],
               exh_max.reindex(genes_prot),
               label="E24 M3D metric on the protein subset"))
mag_t = float(fcT_max.loc[genes_prot].mean())
mag_p = float(fcP_max.loc[genes_prot].mean())
results["magnitudes_protein_subset"] = {
    "mean_max_abs_dT": mag_t, "mean_max_abs_dP": mag_p,
    "ratio": mag_p / mag_t if mag_t else None}
print(f"  magnitudes on the subset: mean max|dT| = {mag_t:.3f}, "
      f"mean max|dP| = {mag_p:.3f} (ratio {mag_p/mag_t:.3f})")
results["arms"]["protfc-kappaV"] = report(
    "protfc-kappaV",
    corr_stats(logkv_panel.loc[genes_prot], fcP_max.loc[genes_prot],
               label="log10 kappa_V vs protein max|log2FC|"))
# sensitivities: 4h only; genes with >=6 peptides in at least one sample
fcP_4h = fcP["4h"].abs()
g4 = [g for g in panel_kv.index if np.isfinite(fcP_4h.get(g, np.nan))]
results["arms"]["protfc-4h-only"] = report(
    "protfc-4h-only",
    corr_stats(logkv_panel.loc[g4], fcP_4h.loc[g4], label="protein 4h |FC|"))
max_pep = pep.max(axis=1)
gpep = [g for g in genes_prot if max_pep.get(g, 0) >= 6]
results["arms"]["protfc-min6peptides"] = report(
    "protfc-min6peptides",
    corr_stats(logkv_panel.loc[gpep], fcP_max.loc[gpep],
               label=f"protein max|FC|, >=6 peptides (n={len(gpep)})"))
# does the protein FC track the transcript FC (overall coupling)?
bothT = [g for g in fcP_max.index if np.isfinite(fcP_max.get(g, np.nan))
         and np.isfinite(fcT_max.get(g, np.nan))]
results["arms"]["coupling-T-P-overall"] = report(
    "coupling-T-P-overall",
    corr_stats(fcT_max.loc[bothT], fcP_max.loc[bothT],
               label="max|dT| vs max|dP| (all genes)"))

# ------------------------------------------- [P-tp] coupling by kappa strata
# signed per-time coupling, pooled over matched times, per kappa tertile
pool = {k: ([], []) for k in ("low-kappa", "mid-kappa", "high-kappa")}
kq1, kq2 = logkv_panel.loc[genes_prot].quantile([1 / 3, 2 / 3])
ratio_rows = []
for g in genes_prot:
    kv = logkv_panel.loc[g]
    s = ("low-kappa" if kv <= kq1 else
         "mid-kappa" if kv <= kq2 else "high-kappa")
    for t in ("1h", "2h", "4h", "6h"):
        dt, dp = fcT[t].get(g, np.nan), fcP[t].get(g, np.nan)
        if np.isfinite(dt) and np.isfinite(dp):
            pool[s][0].append(dt)
            pool[s][1].append(dp)
    tmax, pmax = fcT_max.get(g, np.nan), fcP_max.get(g, np.nan)
    if np.isfinite(tmax) and np.isfinite(pmax) and tmax > 0:
        ratio_rows.append((g, s, pmax / tmax, tmax, pmax))
ratio = pd.DataFrame(ratio_rows, columns=["gene", "stratum", "ratio",
                                           "tmax", "pmax"])
print(f"\n[P-tp] kappa tertile cut points: log10 kappa {kq1:.2f} / {kq2:.2f}")
results["tp_coupling_by_kappa"] = {}
for s, (dts, dps) in pool.items():
    if len(dts) >= 10:
        results["tp_coupling_by_kappa"][s] = report(
            f"tp-coupling-{s}",
            corr_stats(np.array(dts), np.array(dps),
                       label=f"signed dT vs dP, {s}"))
    rr = ratio[ratio["stratum"] == s]["ratio"]
    results["tp_coupling_by_kappa"][f"{s}_impl_ratio"] = {
        "n_genes": int(len(rr)), "mean_ratio": float(rr.mean()),
        "median_ratio": float(rr.median())}
    print(f"  {s}: |dP|/|dT| implementation ratio mean {rr.mean():.3f} "
          f"median {rr.median():.3f} (n={len(rr)})")

# protein response by kappa tertile (the buffering prediction: high-kappa
# proteins should move LESS if post-translationally buffered)
for s in ("low-kappa", "mid-kappa", "high-kappa"):
    gs = [g for g, st in zip(ratio["gene"], ratio["stratum"]) if st == s]
    if len(gs) >= 10:
        results["tp_coupling_by_kappa"][f"protfc-{s}"] = report(
            f"protfc-{s}", corr_stats(logkv_panel.loc[gs],
                                      fcP_max.loc[gs],
                                      label=f"protein max|FC| in {s}"))
        results["tp_coupling_by_kappa"][f"transfc-{s}"] = report(
            f"transfc-{s}", corr_stats(logkv_panel.loc[gs],
                                       fcT_max.loc[gs],
                                       label=f"transcript max|FC| in {s}"))

# MWU: implementation ratio high vs low kappa
hi = ratio[ratio["stratum"] == "high-kappa"]["ratio"]
lo = ratio[ratio["stratum"] == "low-kappa"]["ratio"]
if len(hi) >= 5 and len(lo) >= 5:
    mwu = stats.mannwhitneyu(hi, lo, alternative="greater")
    results["implementation_ratio_test"] = {
        "high_mean": float(hi.mean()), "low_mean": float(lo.mean()),
        "n_high": int(len(hi)), "n_low": int(len(lo)),
        "mannwhitney_p_one_sided_high_gt_low": float(mwu.pvalue)}
    print(f"[P-ratio] |dP|/|dT|: high-kappa {hi.mean():.3f} vs low-kappa "
          f"{lo.mean():.3f} (MWU p={mwu.pvalue:.3g})")

# ============================================================== artifacts
csv = pd.DataFrame({
    "kappa_V_max": panel_kv,
    "paxdb_ppm": pax.reindex(panel_kv.index),
    "m3d_exhaustion_maxfc": exh_max.reindex(panel_kv.index),
    "gse_transcript_maxfc": fcT_max.reindex(panel_kv.index),
    "gse_protein_maxfc": fcP_max.reindex(panel_kv.index),
    "gse_protein_4h_fc": fcP["4h"].abs().reindex(panel_kv.index),
})
csv.to_csv(DL / "novelty_v19_e26_protein_abundance.csv")
with open(DL / "novelty_v19_e26_protein_abundance_results.json", "w") as f:
    json.dump(results, f, indent=2)
lines = ["Study E26 (v19) protein-abundance mechanistic test"]
for tag, res in results["arms"].items():
    lines.append(f"[{tag}] n={res['n']} r={res['pearson_r']:+.4f} "
                 f"p={res['pearson_p']:.3e}")
(DL / "novelty_v19_e26_protein_abundance.txt").write_text("\n".join(lines))
print("\n[artifacts] written: novelty_v19_e26_protein_abundance"
      "{.csv,_results.json,.txt}")
