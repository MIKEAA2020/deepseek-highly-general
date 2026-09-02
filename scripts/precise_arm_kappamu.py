#!/usr/bin/env python3
"""
PRECISE-arm replication with the LOCKED metric kappa^mu.

The completed-round evaluation's step 3: "concurrently run the
PRECISE-arm replication" during Layer-1 porting. The v17/E24 round ran
the PRECISE carbon-switch arm with the OLD E22 kappa_V predictor
(r = -0.054, n = 433, NS); the recalibrated flux-layer metric kappa^mu
(V5/V6) has never been tested against PRECISE. This script closes that
gap: kappa^mu (from the frozen V6 run, iJO1366/E22 trajectory) versus

  - the E24 carbon-depletion response (M3D stationary; reproduction
    anchor, expected r = +0.3954),
  - the M3D microarray carbon-switch arms (glycerol / acetate /
    proline vs glucose, same platform),
  - the PRECISE RNA-seq carbon-switch arms (10 WT non-glucose carbon
    conditions, cross-platform),
each with permutation p, bootstrap CI, and a reference-level partial.

Outputs: download/deepseek_bridge/precise_arm_kappamu.{json,txt}
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")
DL = os.path.join(BASE, "download")
M3D = os.path.join(BASE, "data", "m3d", "E_coli_v4_Build_6")

v6 = pd.read_csv(os.path.join(DL, "deepseek_bridge",
                              "v6_layer_decision.csv"))
v6 = v6.set_index("gene_bnumber")
kmu = v6["kappa_mu"].astype(float)
logkmu = np.log10(kmu)

e24 = pd.read_csv(os.path.join(DL, "novelty_v17_option_a_e24.csv"))
e24 = e24.set_index("gene_bnumber")
stat_cols = ["fc_m3d_stationary_135min", "fc_m3d_stationary_330min",
             "fc_m3d_stationary_480min", "fc_m3d_stationary_720min"]
y_carbon = e24[stat_cols].abs().max(axis=1)

m3d_switch = {k: e24[f"fc_m3d_{k}"].abs()
              for k in ("glycerol", "acetate", "proline")}
m3d_switch_max = e24[["fc_m3d_glycerol", "fc_m3d_acetate",
                      "fc_m3d_proline"]].abs().max(axis=1)

prec_cols = ["fc_prec_galactose", "fc_prec_glycerol", "fc_prec_arg_sbt",
             "fc_prec_cytd_rib", "fc_prec_leu_glcr", "fc_prec_phe_acgam",
             "fc_prec_tyr_glcn", "fc_prec_ura_pyr", "fc_prec_wt_ac",
             "fc_prec_wt_fru"]
prec_switch = {c.replace("fc_prec_", ""): e24[c].abs() for c in prec_cols}
prec_max = e24["fc_prec_max_carbon_switch"].abs()

expr = pd.read_csv(
    os.path.join(M3D, "E_coli_v4_Build_6_chips907probes4297.tab"),
    sep="\t", index_col=0)
psd = pd.read_csv(os.path.join(M3D, "E_coli_v4_Build_6.probe_set_descriptions"),
                  sep="\t")
locus_of = dict(zip(psd["probe_set_name"], psd["locus"].astype(str)))
expr.index = [locus_of.get(p, p) for p in expr.index]
if expr.index.duplicated(keep=False).sum():
    expr = expr.groupby(level=0).mean()
REF = [f"WT_MOPS_glucose_r{i}" for i in range(1, 6)]
z = expr[REF].mean(axis=1).reindex(kmu.index).values


def corr_stats(x, y, n_perm=100_000, n_boot=10_000, label=""):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3 or x.std() == 0 or y.std() == 0:
        return {"label": label, "n": n, "pearson_r": None,
                "n_note": "degenerate"}
    pr, pp = stats.pearsonr(x, y)
    sr, sp = stats.spearmanr(x, y)
    zx = (x - x.mean()) / x.std()
    zy = (y - y.mean()) / y.std()
    rng = np.random.default_rng(777)
    perms = np.stack([rng.permutation(n) for _ in range(n_perm)])
    r_perm = (zy[perms] @ zx) / n
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
            "pearson_p": float(pp), "spearman_r": round(sr, 4),
            "spearman_p": float(sp), "perm_p_mc": round(perm_p, 5),
            "boot_ci95": [round(float(lo), 4), round(float(hi), 4)]}


def partial_r(x, y, z):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    z = np.asarray(z, float)
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[ok], y[ok], z[ok]
    bx = np.polyfit(z, x, 1)
    rx = x - np.polyval(bx, z)
    by = np.polyfit(z, y, 1)
    ry = y - np.polyval(by, z)
    return stats.pearsonr(rx, ry)


RESPONSES = {
    "E24 carbon-depletion maxFC (M3D stationary)": y_carbon,
    "M3D microarray carbon-switch glycerol": m3d_switch["glycerol"],
    "M3D microarray carbon-switch acetate": m3d_switch["acetate"],
    "M3D microarray carbon-switch proline": m3d_switch["proline"],
    "M3D microarray carbon-switch MAX": m3d_switch_max,
    "PRECISE RNA-seq carbon-switch galactose": prec_switch["galactose"],
    "PRECISE RNA-seq carbon-switch glycerol": prec_switch["glycerol"],
    "PRECISE RNA-seq carbon-switch acetate (wt_ac)": prec_switch["wt_ac"],
    "PRECISE RNA-seq carbon-switch fructose (wt_fru)": prec_switch["wt_fru"],
    "PRECISE RNA-seq carbon-switch MAX (10 WT conditions)": prec_max,
}

out = {"experiment": "PRECISE-arm replication with the locked metric "
                     "kappa^mu (V6 run, iJO1366/E22 trajectory)",
       "predictor": "log10 kappa^mu, n=433 panel (424 nonzero)",
       "prior_art": "v17/E24 PRECISE carbon-switch arm with the OLD E22 "
                    "kappa_V predictor: r = -0.0543 (n=433, p=0.26, NS)",
       "arms": {}, "partials": {}}

lines = ["PRECISE-arm replication with the locked metric kappa^mu",
         "=" * 64,
         "predictor: log10 kappa^mu (V6 frozen run; 433-gene panel)",
         "prior art (v17, OLD kappa_V predictor): r = -0.0543 "
         "(n=433, NS)", ""]
for name, resp in RESPONSES.items():
    yv = resp.reindex(kmu.index).values
    res = corr_stats(logkmu.values, yv, label=name)
    out["arms"][name] = res
    pr = partial_r(logkmu.values, yv, z)
    out["partials"][name] = [round(float(pr[0]), 4), float(pr[1])]
    print(f"{name:55s} n={res['n']:4d} r={res['pearson_r']:+.4f} "
          f"p={res['pearson_p']:.2e} partial={pr[0]:+.4f}", flush=True)
    lines.append(f"[{name}] n={res['n']} r={res['pearson_r']:+.4f} "
                 f"(p={res['pearson_p']:.2e}) "
                 f"spearman={res['spearman_r']:+.4f} "
                 f"perm_p={res['perm_p_mc']} CI={res['boot_ci95']} "
                 f"partial_r(reflevel)={pr[0]:+.4f} (p={pr[1]:.2g})")

with open(os.path.join(OUT, "precise_arm_kappamu.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)
with open(os.path.join(OUT, "precise_arm_kappamu.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"\nartifacts in {OUT}")
