#!/usr/bin/env python3
"""
V6 -- the layer-decision experiment (the follow-up audit's "direct
computation").

The follow-up audit (advice item 3) asks: "For the empirical
association, test both: the Hessian measure D^2 Phi contracted with the
viability field, [and] the Monge-Ampere atom mass. See which one better
reproduces or improves the E24 correlation. ... This needs direct
computation."

Design: keep the V5 protocol frozen (engine, seed, physiology,
trajectory, panel, response, statistics) and add the value-layer arms:

  A  kappa_mu        (flux layer, all events; the V5 predictor)
  B1 kappa_vg        (value-GATED flux strain: second-difference mass
                     restricted to the times where the VALUE trajectory
                     Phi(t) kinks -- the flux strain co-located with the
                     value layer's event set)
  B2 kappa_c         (per-reaction c-attribution of the value strain:
                     |c_r| * value strain -- with the sparse FBA
                     objective this is supported only on the biomass
                     reaction, i.e. structurally degenerate per gene)
  B3 kappa_dual      (the 1-D shadow of the MA layer: at each interior
                     Phi-kink, the jump of the full bound-marginal
                     (shadow price) vector of the stage-1 LP, attributed
                     per reaction and per gene)

Also recorded on the same trajectory:
  - the value-kink census (anchor/path-corner kinks vs interior
    chamber crossings), with per-kink coupling check
    |Delta Phi' - c^T Delta v'| (Theorem C) and the inequality
    |Delta Phi'| <= ||c||_inf * ||Delta v'||_1;
  - the value/flux strain mass ratio (the V1 decoupling on the E24
    trajectory);
  - the within-layer rank identity rho(kappa_mu, kappa_V_lex).

Outputs: download/deepseek_bridge/v6_layer_decision.{json,csv,png}
"""
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import linprog

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")
os.makedirs(OUT, exist_ok=True)
DL = os.path.join(BASE, "download")
M3D = os.path.join(BASE, "data", "m3d", "E_coli_v4_Build_6")

t0 = time.time()


def corr_stats(x, y, n_perm=100_000, n_boot=10_000, label=""):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3 or x.std() == 0 or y.std() == 0:
        return {"label": label, "n": n, "pearson_r": None,
                "n_note": "degenerate predictor (n<3 or zero variance)"}
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


# ------------------------------------------------------------- panel
e24 = pd.read_csv(os.path.join(DL, "novelty_v17_option_a_e24.csv"))
e24 = e24.set_index("gene_bnumber")
e22 = pd.read_csv(
    os.path.join(DL, "novelty_v15_reaction_sampling_e22.csv"))
e22 = e22.set_index("gene_bnumber")
stat_cols = ["fc_m3d_stationary_135min", "fc_m3d_stationary_330min",
             "fc_m3d_stationary_480min", "fc_m3d_stationary_720min"]
max_fc = e24[stat_cols].abs().max(axis=1)
kv_e22 = e22["kappa_V_max"].astype(float).reindex(e24.index)
y = max_fc.values

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
z = ref_level.values

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
bio_genes = [g.id for g in model.reactions.get_by_id(bio_id).genes]
rng = np.random.default_rng(20240901)     # M-series tie-break protocol
W = rng.uniform(0.5, 1.5, len(model.reactions))
eng = LPEngine(model, W, c_bio)
bi = eng.index[bio_id]
R = eng.R
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


def stage1(g, o):
    """Stage-1-only solve with full bound marginals (exact Phi, duals)."""
    lb, ub = eng.lb0.copy(), eng.ub0.copy()
    lb[i_glc] = -g
    lb[i_o2] = -o
    fub = np.maximum(ub, 0.0)
    rub = np.maximum(-lb, 0.0)
    vlb = np.concatenate([lb, np.zeros(R), np.zeros(R)])
    vub = np.concatenate([ub, fub, rub])
    c1 = np.zeros(3 * R)
    c1[:R] = -eng.c_bio
    res = linprog(c1, A_eq=eng.A_eq, b_eq=eng.b_eq0,
                  bounds=np.column_stack((vlb, vub)),
                  method="highs", options={"presolve": True})
    return res


def marg_per_reaction(res):
    """Map all 3R bound marginals back to reactions (max abs)."""
    m_up = np.abs(res.upper.marginals)
    m_lo = np.abs(res.lower.marginals)
    per = np.zeros(R)
    for i in range(3 * R):
        r = i % R
        per[r] = max(per[r], m_up[i], m_lo[i])
    return per


# gene -> reactions map (cobra authoritative, as E22/V5)
gene_rxns = {}
for r in model.reactions:
    for g in r.genes:
        gene_rxns.setdefault(g.id, []).append(eng.index[r.id])
panel_genes = list(e24.index)

# =====================================================================
# Trajectories + value-kink census
# =====================================================================
out = {"experiment": "V6 layer-decision: which curvature layer "
                     "carries the E24 association (the follow-up "
                     "audit's direct computation)",
       "engine": "lex-pFBA (seed 20240901), iJO1366, E22 physiology "
                 "(identical to V5)"}

REFINE = 8
T = trajectory(REFINE)
Vs, mus = solve_traj(T)
N = len(T)
tt = np.linspace(0, 1, N)
dt = float(tt[1] - tt[0])
anchor_idx = set(k * REFINE for k in range(8))

# second differences of the value trajectory
d2mu = np.abs(mus[2:] - 2 * mus[1:-1] + mus[:-2]) / dt
kink_idx = [i + 1 for i in range(N - 2) if d2mu[i] > 1e-8]
# cluster kinks within 2 grid steps
kcl = []
for i in kink_idx:
    if kcl and i - kcl[-1][-1] <= 2:
        kcl[-1].append(i)
    else:
        kcl.append([i])
kink_rows = []
dual_per_rxn = np.zeros(R)
for cl in kcl:
    i0 = cl[int(np.argmax([d2mu[i - 1] for i in cl]))]
    t_k = tt[i0]
    is_anchor = any(abs(i - a) <= 1 for i in cl for a in anchor_idx)
    # value slope jump from exact grid mus; one-sided pairs (i0-2, i0-1)
    # and (i0+1, i0+2) avoid the kink cell for the peak row i0
    if 2 <= i0 <= N - 3:
        sL = (mus[i0 - 1] - mus[i0 - 2]) / dt
        sR = (mus[i0 + 2] - mus[i0 + 1]) / dt
        dphi = float(sR - sL)
        sl_v = (Vs[i0 - 1] - Vs[i0 - 2]) / dt
        sr_v = (Vs[i0 + 2] - Vs[i0 + 1]) / dt
        dv = sr_v - sl_v
        cT = float(c_bio @ dv)
        l1jump = float(np.abs(dv).sum())
        # dual jump: stage-1 marginals at clean one-side grid points
        resL = stage1(*T[i0 - 2])
        resR = stage1(*T[i0 + 2])
        dy = marg_per_reaction(resR) - marg_per_reaction(resL)
        dy_sup = np.where(np.abs(dy) > 1e-9)[0]
        dy_uptake = [float(dy[i_glc]), float(dy[i_o2])]
        dual_jump_L1 = float(np.abs(dy[dy_sup]).sum()) if len(dy_sup) \
            else 0.0
        dual_ids = [eng.rxn_ids[i] for i in dy_sup][:12]
        dual_per_rxn += np.abs(dy)
    else:
        dphi = cT = l1jump = dual_jump_L1 = 0.0
        dual_ids = []
        dy_sup = []
    kink_rows.append({
        "grid_index": i0, "t": float(t_k), "t_phys": list(T[i0]),
        "is_anchor_corner": bool(is_anchor),
        "delta_phi_slope": dphi,
        "flux_L1_slope_jump": l1jump,
        "cT_jump": cT,
        "coupling_err": abs(dphi - cT),
        "n_reactions_in_dual_jump": int(len(dy_sup)),
        "dual_uptake_jump": dy_uptake if 2 <= i0 <= N - 3 else None,
        "dual_jump_L1": dual_jump_L1,
        "dual_jump_rxn_ids": dual_ids})
    print(f"[V6] kink t={t_k:.3f} anchor={is_anchor} "
          f"dPhi'={dphi:+.3e} fluxL1={l1jump:.3e} cT={cT:+.3e} "
          f"err={abs(dphi - cT):.1e} ndual={len(dy_sup)}",
          flush=True)

n_int = sum(1 for r in kink_rows if not r["is_anchor_corner"])
value_strain_total = sum(abs(r["delta_phi_slope"]) for r in kink_rows)
flux_strain_total = float(np.abs(Vs[2:] - 2 * Vs[1:-1] + Vs[:-2]).sum()
                          / dt)
out["value_kink_census"] = {
    "n_grid_points": N, "refine": REFINE,
    "n_value_kinks_total": len(kink_rows),
    "n_anchor_corner_kinks": len(kink_rows) - n_int,
    "n_interior_chamber_kinks": n_int,
    "value_strain_total": value_strain_total,
    "flux_strain_total": flux_strain_total,
    "value_over_flux_mass_ratio": value_strain_total / flux_strain_total,
    "kinks": kink_rows}
print(f"[V6] value kinks: {len(kink_rows)} total "
      f"({n_int} interior, {len(kink_rows) - n_int} anchor corners); "
      f"value/flux strain ratio = "
      f"{value_strain_total / flux_strain_total:.2e}", flush=True)

# =====================================================================
# Predictors
# =====================================================================
D2 = np.abs(Vs[2:] - 2 * Vs[1:-1] + Vs[:-2]) / dt     # (N-2, R)
disp = (Vs - Vs[0])
kv_lex = (disp ** 2).max(0)

# gated times: grid indices of second differences (i in 1..N-2 maps to
# row i-1 of D2); window +-1 around each kink cluster
gate_all = np.zeros(N - 2, bool)
gate_int = np.zeros(N - 2, bool)
for r in kink_rows:
    i0 = r["grid_index"]
    for j in range(max(0, i0 - 2), min(N - 2, i0 + 1)):
        gate_all[j] = True
        if not r["is_anchor_corner"]:
            gate_int[j] = True
D2_vg_all = D2 * gate_all[:, None]
D2_vg_int = D2 * gate_int[:, None]

# dual-attributed per-reaction strain was accumulated in the kink
# census above (dual_per_rxn, interior kinks only)

# c-attribution per-reaction (|c_r| x value strain at kinks)
c_per_rxn = np.abs(c_bio) * value_strain_total

rows = []
for gne in panel_genes:
    ridx = gene_rxns.get(gne, [])
    if not ridx:
        rows.append({"gene": gne, "kappa_mu": 0.0, "kappa_vg_all": 0.0,
                     "kappa_vg_int": 0.0, "kappa_dual": 0.0,
                     "kappa_c": 0.0, "kappa_v_lex": 0.0, "n_rxns": 0})
        continue
    rows.append({
        "gene": gne,
        "kappa_mu": float(D2[:, ridx].max()),
        "kappa_vg_all": float(D2_vg_all[:, ridx].max()),
        "kappa_vg_int": float(D2_vg_int[:, ridx].max()),
        "kappa_dual": float(dual_per_rxn[ridx].max()),
        "kappa_c": float(c_per_rxn[ridx].max()),
        "kappa_v_lex": float(kv_lex[ridx].max()),
        "n_rxns": len(ridx)})
df = pd.DataFrame(rows).set_index("gene")

preds = {
    "A kappa_mu (flux layer, all events)":
        (np.log10(df["kappa_mu"]).values, df["kappa_mu"].values),
    "B1 kappa_vg (value-gated flux strain)":
        (np.log10(df["kappa_vg_all"]).values, df["kappa_vg_all"].values),
    "B1b kappa_vg interior kinks only":
        (np.log10(df["kappa_vg_int"].values), df["kappa_vg_int"].values),
    "B2 kappa_c (c-attribution)":
        (np.log10(df["kappa_c"]).values, df["kappa_c"].values),
    "B3 kappa_dual (shadow-price jump)":
        (np.log10(df["kappa_dual"]).values, df["kappa_dual"].values),
    "kappa_V_lex (V5 engine control)":
        (np.log10(df["kappa_v_lex"]).values, df["kappa_v_lex"].values),
}
arms = {}
for name, (logv, rawv) in preds.items():
    nz = rawv > 0
    r_all = corr_stats(logv, y, label=f"{name} [all n]")
    r_nz = corr_stats(logv[nz], y[nz], label=f"{name} [nonzero]")
    sp_full = stats.spearmanr(rawv, y)
    arms[name] = {"all": r_all, "nonzero": r_nz,
                  "n_nonzero": int(nz.sum()),
                  "spearman_raw_full_panel": [float(sp_full[0]),
                                              float(sp_full[1])]}
    print(f"[V6] {name}: n_nonzero={int(nz.sum())} "
          f"r(nz)={r_nz.get('pearson_r')} "
          f"spearman(full)={sp_full[0]:+.4f}", flush=True)

# partial r for the primary arms (nonzero subsets)
partials = {}
for name, col in (("A kappa_mu", "kappa_mu"),
                  ("B1 kappa_vg", "kappa_vg_all"),
                  ("B3 kappa_dual", "kappa_dual")):
    v = df[col].values
    nz = v > 0
    pr = partial_r(np.log10(v[nz]), y[nz], z[nz])
    partials[name] = round(float(pr[0]), 4)
    print(f"[V6] partial r({col}, maxFC | ref level) = {pr[0]:+.4f} "
          f"(p={pr[1]:.2g})", flush=True)

# predictor agreement (within-layer rank identity, V5 sanity)
sp_mu_kv = stats.spearmanr(df["kappa_mu"], kv_e22)
sp_mu_lex = stats.spearmanr(df["kappa_mu"], df["kappa_v_lex"])
sp_mu_vg = stats.spearmanr(df["kappa_mu"], df["kappa_vg_all"])
sp_mu_dual = stats.spearmanr(df["kappa_mu"], df["kappa_dual"])

out["arms"] = arms
out["partial_r_given_ref_level"] = partials
out["predictor_agreement"] = {
    "spearman_kappamu_vs_kappaVE22": [float(sp_mu_kv[0]), float(sp_mu_kv[1])],
    "spearman_kappamu_vs_kappaVlex": [float(sp_mu_lex[0]),
                                      float(sp_mu_lex[1])],
    "spearman_kappamu_vs_kappa_vg": [float(sp_mu_vg[0]),
                                     float(sp_mu_vg[1])],
    "spearman_kappamu_vs_kappa_dual": [float(sp_mu_dual[0]),
                                       float(sp_mu_dual[1])]}
out["layer_decision"] = {
    "biomass_reaction_genes": bio_genes,
    "kappa_c_n_nonzero": int((df["kappa_c"].values > 0).sum()),
    "note": "kappa_c is structurally degenerate: the sparse FBA "
            "objective attributes the value strain to the biomass "
            "pseudo-reaction alone, which carries no GPR -- per-gene "
            "attribution from the value layer is impossible "
            "(Theorem C, sparse-objective corollary)"}

# =====================================================================
# Figure + outputs
# =====================================================================
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
ax.plot(tt, mus, "-", lw=1.8, color="#1f4e79")
for r in kink_rows:
    col = "#c00000" if not r["is_anchor_corner"] else "#7f7f7f"
    ax.axvline(r["t"], color=col, lw=1.2 if not r["is_anchor_corner"]
               else 0.8, ls="-" if not r["is_anchor_corner"] else ":")
ax.set_xlabel("t along E22 carbon-depletion trajectory")
ax.set_ylabel(r"$\Phi(t)$ (stage-1 biomass optimum)")
ax.set_title(f"(a) value trajectory: {len(kink_rows)} kinks "
             f"({n_int} interior)")
ax = axes[1]
names = ["A $\\kappa^\\mu$\n(flux, all events)",
         "B1 $\\kappa^{vg}$\n(value-gated)",
         "B3 $\\kappa^{dual}$\n(shadow-price)",
         "B2 $\\kappa^{c}$\n(c-attribution)"]
cols = ["kappa_mu", "kappa_vg_all", "kappa_dual", "kappa_c"]
rs_ = []
for c in cols:
    v = df[c].values
    nz = v > 0
    if nz.sum() > 3:
        rr_ = stats.pearsonr(np.log10(v[nz]), y[nz])[0]
    else:
        rr_ = np.nan
    rs_.append(rr_)
bars = ax.bar(range(4), rs_, color=["#1f4e79", "#548235", "#bf9000",
                                    "#7f7f7f"])
for i, (r_, c) in enumerate(zip(rs_, cols)):
    nz = (df[c].values > 0).sum()
    ax.text(i, 0.02 if not np.isfinite(r_) else r_ + 0.015,
            f"{'nan' if not np.isfinite(r_) else f'{r_:+.3f}'}\n"
            f"(n={int(nz)})", ha="center", fontsize=8.5)
ax.axhline(0, color="k", lw=0.6)
ax.set_xticks(range(4))
ax.set_xticklabels(names, fontsize=8.5)
ax.set_ylabel("Pearson r (nonzero panel)")
ax.set_title("(b) the layer decision")
ax = axes[2]
m = df["kappa_mu"].values > 0
ax.scatter(np.log10(df["kappa_mu"].values[m]),
           np.log10(np.maximum(df["kappa_vg_all"].values[m], 1e-12)),
           s=9, alpha=0.45, color="#548235", edgecolors="none",
           label=r"$\kappa^{vg}$ (value-gated)")
ax.scatter(np.log10(df["kappa_mu"].values[m]),
           np.log10(np.maximum(df["kappa_dual"].values[m], 1e-12)),
           s=9, alpha=0.45, color="#bf9000", edgecolors="none",
           label=r"$\kappa^{dual}$")
ax.set_xlabel(r"$\log_{10}\,\kappa^\mu$")
ax.set_ylabel(r"value-layer arms ($\log_{10}$)")
ax.set_title("(c) value arms vs flux layer")
ax.legend(fontsize=8, loc="upper left")
fig.suptitle("V6 - layer decision: which curvature object carries the "
             "E24 association", fontsize=11)
fig.savefig(os.path.join(OUT, "v6_layer_decision.png"), dpi=170)
plt.close(fig)

df.join(kv_e22.rename("kappa_V_E22")).to_csv(
    os.path.join(OUT, "v6_layer_decision.csv"),
    index_label="gene_bnumber")
with open(os.path.join(OUT, "v6_layer_decision.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)

print(f"[V6] wall time {time.time() - t0:.0f} s; artifacts in {OUT}",
      flush=True)
