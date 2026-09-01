#!/usr/bin/env python3
"""
V5 -- the audit's "decisive test": re-run E24 with the
measure-theoretic kappa_flux.

The audit ("deepseek stengthen highly general bridge.txt", Recommended
next steps #1): "Re-run E24 with the measure-theoretic kappa_flux. This
is the decisive test. If the empirical association strengthens or
remains robust with the corrected metric, the single-paper route is
secure."

Design: keep EVERYTHING of E24 fixed (panel, trajectory, aggregation,
response variable, statistics) and change only the predictor to the
curvature-measure functional:

  E22 baseline : kappa_V(r)  = max_t (v_r(t) - v_r(T1))^2
                 [squared displacement -- the time-course object]
  corrected    : kappa_mu(r) = sum_t |v_r(t+dt) - 2 v_r(t) + v_r(t-dt)|
                             / dt
                 [L1 mass of the second-difference = total variation of
                 the reaction's slope along the trajectory = the
                 curvature-measure mass carried by r, dt-normalized so
                 the value is resolution-robust (Theorem S: atoms at
                 events; M1: 100% of D2 mass on active-set switches)]

Both are computed on the SAME deterministic lex-pFBA trajectory (the
lex engine removes the plain-FBA vertex degeneracy documented in M1),
so the comparison isolates the DEFINITION change; an engine-matched
kappa_V_lex (E22 definition on the lex trajectory) is also reported to
isolate the ENGINE change.

Trajectory: the exact E22 physiology (q_glc 5.0 -> 1.0, q_O2 22 ->
5.0, 8 anchor points) at 4x and 8x per-segment refinement.  The
trajectory is NOT event-free (total D2 L1 mass 10.3, 440 reactions
with events) -- the recalibration is non-degenerate.

Panel: the E22/E24 panel (433 genes with M3D expression).  Response:
max |log2FC| over the four M3D stationary carbon-exhaustion contrasts
(identical to E24's [A-panel]).  Confound control: partial r given the
M3D log-phase reference expression level (identical to E24).  Deciles,
zero-kappa contrast, permutation p, bootstrap CI -- all identical.

Outputs: download/deepseek_bridge/v5_e24_recalibration.{json,csv,png}
"""
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")
os.makedirs(OUT, exist_ok=True)
DL = os.path.join(BASE, "download")
M3D = os.path.join(BASE, "data", "m3d", "E_coli_v4_Build_6")

t0 = time.time()

# ------------------------------------------------------------- E24 stats
def corr_stats(x, y, n_perm=100_000, n_boot=10_000, label=""):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
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


# ------------------------------------------------------- load E24 panel
# NOTE: the e24 csv rounded kappa_V_max to 6 decimals, which zeroes the
# 94 tiny (1e-13..1e-7) panel values; the E24 statistics were computed
# on the UNROUNDED in-memory values (n=433).  We therefore read kappa
# from the E22 artifact (unrounded) and the responses from e24 (FC
# columns are unaffected by rounding at log2FC scale).
e24 = pd.read_csv(os.path.join(DL, "novelty_v17_option_a_e24.csv"))
e24 = e24.set_index("gene_bnumber")
e22 = pd.read_csv(
    os.path.join(DL, "novelty_v15_reaction_sampling_e22.csv"))
e22 = e22.set_index("gene_bnumber")
stat_cols = ["fc_m3d_stationary_135min", "fc_m3d_stationary_330min",
             "fc_m3d_stationary_480min", "fc_m3d_stationary_720min"]
max_fc = e24[stat_cols].abs().max(axis=1)
kv_e22 = e22["kappa_V_max"].astype(float).reindex(e24.index)
logkv_e22 = np.log10(kv_e22)
print(f"[V5] E24 panel loaded: {len(e24)} genes with M3D response; "
      f"kappa from E22 artifact (unrounded, "
      f"{(kv_e22 > 0).sum()} nonzero)")

# M3D reference level (identical to E24's confound control)
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
ref_level = expr[REF].mean(axis=1).reindex(e24.index)
print(f"[V5] M3D ref level: {ref_level.notna().sum()}/{len(e24)} genes")

# ------------------------------------------------------------- engine
import cobra
from cobra.util.solver import linear_reaction_coefficients
sys.path.insert(0, os.path.join(BASE, "scripts"))
from lp_engine import LPEngine

model = cobra.io.load_json_model(
    os.path.join(BASE, "data", "bigg_models", "iJO1366.json"))
co = linear_reaction_coefficients(model)
c_bio = np.zeros(len(model.reactions))
for r, c in co.items():
    c_bio[model.reactions.index(r)] = c
bio_id = list(co.keys())[0].id
rng = np.random.default_rng(20240901)     # M-series tie-break protocol
W = rng.uniform(0.5, 1.5, len(model.reactions))
eng = LPEngine(model, W, c_bio)
bi = eng.index[bio_id]
i_glc, i_o2 = eng.index["EX_glc__D_e"], eng.index["EX_o2_e"]

q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_o2 = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]


def trajectory(refine):
    T = []
    for k in range(7):
        for j in range(refine):
            f = j / refine
            T.append((q_glc[k] + f * (q_glc[k + 1] - q_glc[k]),
                      q_o2[k] + f * (q_o2[k + 1] - q_o2[k])))
    T.append((q_glc[-1], q_o2[-1]))
    return T


def solve_traj(T):
    Vs, mus = [], []
    for g, o in T:
        lb, ub = eng.lb0.copy(), eng.ub0.copy()
        lb[i_glc] = -g
        lb[i_o2] = -o
        out = eng.solve_lex(lb, ub, bi)
        if out is None:
            raise RuntimeError(f"infeasible at ({g},{o})")
        Vs.append(out[0])
        mus.append(out[1])
    return np.array(Vs), np.array(mus)


def per_reaction_objects(Vs):
    """kappa_mu (measure mass, dt-normalized) and kappa_V (E22 def)."""
    dt_steps = np.diff(np.linspace(0, 1, len(Vs)))   # uniform in t
    dt = float(dt_steps[0])
    D2 = np.abs(Vs[2:] - 2 * Vs[1:-1] + Vs[:-2]).sum(0) / dt
    disp = (Vs - Vs[0])
    kv = (disp ** 2).max(0)
    return D2, kv, dt


# ---- gene -> reactions map (cobra authoritative, as E22)
gene_rxns = {}
for r in model.reactions:
    for g in r.genes:
        gene_rxns.setdefault(g.id, []).append(eng.index[r.id])

panel_genes = list(e24.index)

results = {}
for refine in (4, 8):
    T = trajectory(refine)
    Vs, mus = solve_traj(T)
    D2, kv, dt = per_reaction_objects(Vs)
    print(f"[V5] refine={refine}: {len(T)} pts, dt={dt:.4f}, "
          f"total D2 mass={D2.sum():.3f}, "
          f"n rxns with D2>1e-8: {(D2 > 1e-8).sum()}")
    # 3-pt collinearity (affinity) residual for the census
    res = max(np.abs(Vs[k + 1] - 0.5 * (Vs[k] + Vs[k + 2])).max()
              for k in range(len(Vs) - 2))
    rows = []
    for g in panel_genes:
        ridx = gene_rxns.get(g, [])
        if not ridx:
            rows.append({"gene": g, "kappa_mu_max": 0.0,
                         "kappa_mu_sum": 0.0, "kappa_mu_own": 0.0,
                         "kappa_v_lex": 0.0, "n_rxns": 0})
            continue
        d2g = D2[ridx]
        kvg = kv[ridx]
        rows.append({
            "gene": g,
            "kappa_mu_max": float(d2g.max()),
            "kappa_mu_sum": float(d2g.sum()),
            "kappa_mu_own": float(d2g.max()),   # same as max (own-rxns)
            "kappa_v_lex": float(kvg.max()),
            "n_rxns": len(ridx)})
    df = pd.DataFrame(rows).set_index("gene")
    results[refine] = {"df": df, "total_D2": float(D2.sum()),
                       "n_events_rxns": int((D2 > 1e-8).sum()),
                       "affine_resid": float(res), "dt": dt}

# ------------------------------------------------------- statistics
out = {"experiment": "V5 E24 recalibration with the measure-theoretic "
                     "kappa (the audit's decisive test)",
       "engine": "lex-pFBA (seed 20240901), iJO1366, E22 physiology",
       "predictors": {
           "kappa_V_E22": "E22 artifact (plain FBA, squared displacement)",
           "kappa_V_lex": "E22 definition on the deterministic lex "
                          "trajectory (engine control)",
           "kappa_mu": "measure mass: sum_t |D2|/dt per reaction, "
                       "per-gene max (definition change)"}}

df8 = results[8]["df"]
df4 = results[4]["df"]

preds = {
    "kappa_V_E22 (baseline)": (logkv_e22.values, kv_e22.values),
    "kappa_V_lex (engine ctrl)": (np.log10(df8["kappa_v_lex"]).values,
                                  df8["kappa_v_lex"].values),
    "kappa_mu max (4x)": (np.log10(df8["kappa_mu_max"]).values,
                          df8["kappa_mu_max"].values),
    "kappa_mu sum (4x ctrl)": (np.log10(df8["kappa_mu_sum"]).values,
                               df8["kappa_mu_sum"].values),
}
y = max_fc.values

arms = {}
for name, (logv, rawv) in preds.items():
    nz = rawv > 0
    r_all = corr_stats(logv.values if hasattr(logv, "values") else logv,
                       y, label=f"{name} [all n]")
    r_nz = corr_stats((logv.values if hasattr(logv, "values") else logv)[nz],
                      y[nz], label=f"{name} [nonzero]")
    sp_full = stats.spearmanr(rawv, y)
    arms[name] = {"all": r_all, "nonzero": r_nz,
                  "n_nonzero": int(nz.sum()),
                  "spearman_raw_full_panel": [float(sp_full[0]),
                                              float(sp_full[1])]}
    print(f"[V5] {name}: n_nonzero={int(nz.sum())} "
          f"r(nz)={r_nz['pearson_r']:+.4f} "
          f"(p={r_nz['pearson_p']:.2g})  "
          f"spearman(full)={sp_full[0]:+.4f}")

# refinement robustness (4x vs 8x) for the primary measure predictor
r_4x = corr_stats(np.log10(df4["kappa_mu_max"]).values, y,
                  label="kappa_mu max [4x refinement, all n]")
arms["kappa_mu max (8x)"] = r_4x
r_8x_val = arms["kappa_mu max (4x)"]["all"]["pearson_r"]
print(f"[V5] refinement robustness: 8x r={r_8x_val:+.4f} "
      f"vs 4x r={r_4x['pearson_r']:+.4f}")

# ---- confound control (partial given reference level) for the primary
z = ref_level.values
x_mu = np.log10(df8["kappa_mu_max"]).values
x_mu_nz = x_mu[df8["kappa_mu_max"].values > 0]
y_nz = y[df8["kappa_mu_max"].values > 0]
z_nz = z[df8["kappa_mu_max"].values > 0]
pr_part = partial_r(x_mu_nz, y_nz, z_nz)
r_xz = stats.pearsonr(x_mu_nz, z_nz)
arms["confound_control"] = {
    "r_kappamu_vs_reflevel": round(float(r_xz[0]), 4),
    "r_fc_vs_reflevel": round(float(
        stats.pearsonr(y_nz, z_nz)[0]), 4),
    "partial_r_kappamu_fc_given_reflevel": round(float(pr_part[0]), 4),
    "partial_p": float(pr_part[1])}
print(f"[V5] partial r(kappa_mu, maxFC | ref level) = "
      f"{pr_part[0]:+.4f} (p={pr_part[1]:.2g})")

# ---- deciles for the primary
kv_mu = df8["kappa_mu_max"]
lmu = np.log10(kv_mu)
q = lmu[kv_mu > 0].quantile([0.1, 0.9])
inb = kv_mu > 0
top = max_fc[inb & (lmu >= q[0.9])]
bot = max_fc[inb & (lmu <= q[0.1])]
mw = stats.mannwhitneyu(top, bot, alternative="greater")
arms["deciles"] = {"top_decile_mean_fc": float(top.mean()),
                   "bottom_decile_mean_fc": float(bot.mean()),
                   "mannwhitney_p_one_sided": float(mw.pvalue)}
print(f"[V5] deciles (kappa_mu): top {top.mean():.3f} vs bottom "
      f"{bot.mean():.3f} (MWU p={mw.pvalue:.2g})")

# ---- zero-kappa contrast (does kappa_mu=0 respond less?)
zero_mu = kv_mu <= 0
arms["zero_contrast"] = {
    "n_zero": int(zero_mu.sum()),
    "mean_fc_zero": float(max_fc[zero_mu].mean()),
    "mean_fc_nonzero": float(max_fc[~zero_mu].mean()),
    "mwu_p": float(stats.mannwhitneyu(max_fc[~zero_mu],
                                      max_fc[zero_mu]).pvalue)}
print(f"[V5] zero-kappa_mu: n={int(zero_mu.sum())}, mean|FC| "
      f"{max_fc[zero_mu].mean():.3f} vs nonzero "
      f"{max_fc[~zero_mu].mean():.3f}")

# ---- predictor cross-correlations (how much does the metric change?)
sp_mu_kv = stats.spearmanr(df8["kappa_mu_max"], kv_e22)
sp_mu_kvlex = stats.spearmanr(df8["kappa_mu_max"],
                              df8["kappa_v_lex"])
sp_kvlex_kv = stats.spearmanr(df8["kappa_v_lex"], kv_e22)
arms["predictor_agreement"] = {
    "spearman_kappamu_vs_kappaVE22": [float(sp_mu_kv[0]),
                                      float(sp_mu_kv[1])],
    "spearman_kappamu_vs_kappaVlex": [float(sp_mu_kvlex[0]),
                                      float(sp_mu_kvlex[1])],
    "spearman_kappaVlex_vs_kappaVE22": [float(sp_kvlex_kv[0]),
                                        float(sp_kvlex_kv[1])]}
print(f"[V5] predictor agreement: rho(kappa_mu, kappa_V_E22) = "
      f"{sp_mu_kv[0]:+.3f}; rho(kappa_mu, kappa_V_lex) = "
      f"{sp_mu_kvlex[0]:+.3f}; rho(kappa_V_lex, kappa_V_E22) = "
      f"{sp_kvlex_kv[0]:+.3f}")

out["arms"] = arms
out["trajectory"] = {
    "refine_4": {k: v for k, v in results[4].items() if k != "df"},
    "refine_8": {k: v for k, v in results[8].items() if k != "df"}}
out["verdict"] = {
    "decisive_test": "report after statistics below"}

# ------------------------------------------------------------- figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for fp in ("/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.1),
                         constrained_layout=True)
ax = axes[0]
m = df8["kappa_mu_max"].values > 0
ax.scatter(x_mu[m], y[m], s=9, alpha=0.45, color="#1f4e79",
           edgecolors="none")
if m.sum() > 5:
    b1, b0 = np.polyfit(x_mu[m], y[m], 1)
    xx = np.linspace(x_mu[m].min(), x_mu[m].max(), 50)
    ax.plot(xx, b0 + b1 * xx, "-", color="#c00000", lw=1.8)
    ax.text(0.04, 0.95,
            f"r = {arms['kappa_mu max (4x)']['nonzero']['pearson_r']:+.3f}"
            f"  (n = {int(m.sum())})",
            transform=ax.transAxes, va="top", fontsize=9)
ax.set_xlabel(r"$\log_{10}\,\kappa^\mu$ (measure mass, per-gene max)")
ax.set_ylabel(r"max $|\log_2\mathrm{FC}|$ (M3D carbon exhaustion)")
ax.set_title("(a) measure-theoretic predictor")
ax = axes[1]
names = ["kappa_V_E22", "kappa_V_lex", "kappa_mu"]
rs = [arms["kappa_V_E22 (baseline)"]["nonzero"]["pearson_r"],
      arms["kappa_V_lex (engine ctrl)"]["nonzero"]["pearson_r"],
      arms["kappa_mu max (4x)"]["nonzero"]["pearson_r"]]
ns = [arms["kappa_V_E22 (baseline)"]["n_nonzero"],
      arms["kappa_V_lex (engine ctrl)"]["n_nonzero"],
      arms["kappa_mu max (4x)"]["n_nonzero"]]
bars = ax.bar(range(3), rs, color=["#7f7f7f", "#548235", "#1f4e79"])
for i, (r_, n_) in enumerate(zip(rs, ns)):
    ax.text(i, r_ + 0.012, f"{r_:+.3f}\n(n={n_})", ha="center",
            fontsize=8.5)
ax.set_xticks(range(3))
ax.set_xticklabels(["E22 $\\kappa_V$\n(baseline)", "$\\kappa_V$ lex\n"
                    "(engine ctrl)", "$\\kappa^\\mu$\n(measure)"],
                   fontsize=9)
ax.set_ylabel("Pearson r (nonzero panel)")
ax.set_title("(b) the decisive comparison")
ax.axhline(0, color="k", lw=0.6)
ax = axes[2]
ax.scatter(np.log10(kv_e22.values)[m], x_mu[m], s=9, alpha=0.45,
           color="#595959", edgecolors="none")
ax.set_xlabel(r"$\log_{10}\,\kappa_V$ (E22 artifact)")
ax.set_ylabel(r"$\log_{10}\,\kappa^\mu$")
ax.set_title(f"(c) predictor agreement "
             f"rho = {sp_mu_kv[0]:+.2f}")
fig.suptitle("V5 - E24 recalibration: measure-theoretic "
             r"$\kappa^\mu$ vs the E22 time-course $\kappa_V$",
             fontsize=11)
fig.savefig(os.path.join(OUT, "v5_e24_recalibration.png"), dpi=170)
plt.close(fig)

# ------------------------------------------------------------- outputs
df8.join(kv_e22.rename("kappa_V_E22")).to_csv(
    os.path.join(OUT, "v5_e24_recalibration.csv"),
    index_label="gene_bnumber")

out["verdict"] = {
    "baseline_reproduced": arms["kappa_V_E22 (baseline)"]["nonzero"]
    ["pearson_r"],
    "measure_theoretic_r": arms["kappa_mu max (4x)"]["nonzero"]
    ["pearson_r"],
    "engine_control_r": arms["kappa_V_lex (engine ctrl)"]["nonzero"]
    ["pearson_r"],
    "note": "see the evaluation document for the interpretation"}
with open(os.path.join(OUT, "v5_e24_recalibration.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)

print(f"[V5] wall time {time.time() - t0:.0f} s; artifacts in "
      f"{OUT}")
