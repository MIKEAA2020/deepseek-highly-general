#!/usr/bin/env python3
"""
V8 -- tie-break robustness of kappa^mu.

Review round (2026-09-02, residual risk 1 / advice 1): "Tie-break
dependence of kappa^mu. The metric is declared under lexicographic
selection, but the manuscript should still include a short robustness
table showing the empirical correlation is stable across reasonable
tie-break variants."

Design: freeze EVERYTHING of the V5/V6 protocol (iJO1366, E22
physiology anchors, 8x refinement = 57 grid points, E24 panel of 433
genes, M3D carbon-depletion maxFC response, reference-level confound
control, identical statistics) and vary ONLY the stage-3 lexicographic
tie-break of the engine:

  TB0 (declared)    : w ~ U(0.5, 1.5), seed 20240901  [the locked metric;
                      must reproduce V5/V6 r = +0.3954 digit-exactly]
  TB1 (fresh seed)  : w ~ U(0.5, 1.5), seed 20240902  [same family,
                      independent draw]
  TB2 (family swap) : w ~ LogNormal(0, 1) clipped to [0.05, 20],
                      seed 20240903                [different
                      distribution family, ~13x wider dynamic range]
  TB3 (rule swap)   : stage-3 objective on the split variables,
                      min sum_r w_r (f_r + r_r)  [= weighted |v|
                      selection] with TB0's weights [structurally
                      different rule: absolute-flux instead of
                      signed-flux selection]
  TB4 (adversarial) : max w . v -- the far end of the stage-2-pinned
                      optimal face -- with TB0's weights

Mechanistic diagnostics per variant (why the result is what it is):
  - where the tie-break binds: grid points with
    ||v_k(t) - v_0(t)||_inf > 1e-9 (stage 3 active), and the max norm;
  - value-layer / pFBA-layer invariance (prop:alex, Theorem C): stage-1
    biomass mu and stage-2 L1 s2 must agree across variants to solver
    tolerance -- the tie-break-freeness of the value layer, measured;
  - per-gene predictor agreement: Spearman rho(kappa_k, kappa_0) on the
    panel, and the count of genes whose kappa changes at all;
  - the association itself: r (nonzero panel), partial r given the M3D
    reference level, n_nonzero, analytic p.

Outputs: download/deepseek_bridge/v8_tiebreak_robustness.{json,csv,png}
Runtime: ~5-8 min (5 engines x 57 grid points x 3 LP stages).
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


# ------------------------------------------------------------- statistics
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
e24 = pd.read_csv(os.path.join(DL, "novelty_v17_option_a_e24.csv"))
e24 = e24.set_index("gene_bnumber")
stat_cols = ["fc_m3d_stationary_135min", "fc_m3d_stationary_330min",
             "fc_m3d_stationary_480min", "fc_m3d_stationary_720min"]
max_fc = e24[stat_cols].abs().max(axis=1)
panel_genes = list(e24.index)
y_all = max_fc.values

expr = pd.read_csv(
    os.path.join(M3D, "E_coli_v4_Build_6_chips907probes4297.tab"),
    sep="\t", index_col=0)
psd = pd.read_csv(
    os.path.join(M3D, "E_coli_v4_Build_6.probe_set_descriptions"),
    sep="\t")
locus_of = dict(zip(psd["probe_set_name"], psd["locus"].astype(str)))
expr.index = [locus_of.get(p, p) for p in expr.index]
if expr.index.duplicated(keep=False).sum():
    expr = expr.groupby(level=0).mean()
REF = [f"WT_MOPS_glucose_r{i}" for i in range(1, 6)]
ref_level = expr[REF].mean(axis=1).reindex(e24.index)
z_all = ref_level.values
print(f"[V8] panel loaded: {len(panel_genes)} genes; "
      f"ref level {np.isfinite(z_all).sum()}/{len(panel_genes)}")

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


class TBEngine(LPEngine):
    """LPEngine with a configurable stage-3 tie-break objective.

    Stages 1 and 2 are IDENTICAL to LPEngine.solve_lex (they are
    tie-break-free by construction: biomass and L1 are pinned before
    any weights enter). Only the stage-3 objective varies:
      mode='signed' : min w . v              [the declared rule]
      mode='abs'    : min sum_r w_r (f_r+r_r) [weighted |v| selection]
      mode='max'    : min (-w) . v            [far end of the face]
    """

    def __init__(self, model_, weights, bio_coeffs, mode="signed"):
        super().__init__(model_, weights, bio_coeffs)
        self.mode = mode

    def solve_lex(self, lb, ub, bio_idx, mu_tol=1e-9, pin_rel=1e-9):
        R = self.R
        fub = np.maximum(ub, 0.0)
        rub = np.maximum(-lb, 0.0)
        vlb = np.concatenate([lb, np.zeros(R), np.zeros(R)])
        vub = np.concatenate([ub, fub, rub])

        # stage 1: max c_bio . v   (identical across all variants)
        c1 = np.zeros(3 * R)
        c1[:R] = -self.c_bio
        res = self._lp(c1, np.column_stack((vlb, vub)))
        if not res.success:
            return None
        mu = float(res.x[bio_idx])

        # stage 2: min sum(f+r), v_bio >= mu - tol (identical)
        vlb2 = vlb.copy()
        vlb2[bio_idx] = max(vlb2[bio_idx],
                            mu - mu_tol * max(1.0, abs(mu)))
        c2 = np.concatenate([np.zeros(R), np.ones(R), np.ones(R)])
        res = self._lp(c2, np.column_stack((vlb2, vub)))
        if not res.success:
            return None
        s2 = float(res.fun)

        # stage 3: the tie-break (variant objective)
        c3 = np.zeros(3 * R)
        if self.mode == "signed":
            c3[:R] = self.w
        elif self.mode == "abs":
            c3[R:2 * R] = self.w
            c3[2 * R:3 * R] = self.w
        elif self.mode == "max":
            c3[:R] = -self.w
        else:
            raise ValueError(self.mode)
        b_ub = np.array([s2 + pin_rel * max(1.0, abs(s2))])
        res = self._lp(c3, np.column_stack((vlb2, vub)), A_ub=self.A_ub,
                       b_ub=b_ub)
        if not res.success:
            return None
        return res.x[:R].copy(), mu, s2


# tie-break variants
rng0 = np.random.default_rng(20240901)     # declared (M-series protocol)
W0 = rng0.uniform(0.5, 1.5, len(model.reactions))
rng1 = np.random.default_rng(20240902)
W1 = rng1.uniform(0.5, 1.5, len(model.reactions))
rng2 = np.random.default_rng(20240903)
W2 = np.clip(rng2.lognormal(0.0, 1.0, len(model.reactions)), 0.05, 20.0)

VARIANTS = [
    ("TB0_declared", W0, "signed"),
    ("TB1_fresh_seed_same_family", W1, "signed"),
    ("TB2_lognormal_family", W2, "signed"),
    ("TB3_absflux_rule", W0, "abs"),
    ("TB4_adversarial_max", W0, "max"),
]

bi_holder = {}


def build_engine(W, mode):
    eng = TBEngine(model, W, c_bio, mode=mode)
    return eng


eng_ref = build_engine(W0, "signed")
bi = eng_ref.index[bio_id]
i_glc, i_o2 = eng_ref.index["EX_glc__D_e"], eng_ref.index["EX_o2_e"]
bi_holder["i"] = bi

# E22 physiology anchors, 8x refinement (the V5/V6 primary trajectory)
q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_o2 = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]
REFINE = 8


def trajectory(refine):
    T = []
    for k in range(7):
        for j in range(refine):
            f = j / refine
            T.append((q_glc[k] + f * (q_glc[k + 1] - q_glc[k]),
                      q_o2[k] + f * (q_o2[k + 1] - q_o2[k])))
    T.append((q_glc[-1], q_o2[-1]))
    return T


T = trajectory(REFINE)
npts = len(T)
print(f"[V8] trajectory: {npts} grid points at {REFINE}x refinement")


def solve_all(eng):
    Vs, mus, s2s = [], [], []
    for g, o in T:
        lb, ub = eng.lb0.copy(), eng.ub0.copy()
        lb[i_glc] = -g
        lb[i_o2] = -o
        out = eng.solve_lex(lb, ub, bi)
        if out is None:
            raise RuntimeError(f"infeasible at ({g},{o})")
        Vs.append(out[0])
        mus.append(out[1])
        s2s.append(out[2])
    return np.array(Vs), np.array(mus), np.array(s2s)


def per_reaction_kappa(Vs):
    dt_steps = np.diff(np.linspace(0, 1, len(Vs)))
    dt = float(dt_steps[0])
    D2 = np.abs(Vs[2:] - 2 * Vs[1:-1] + Vs[:-2]).sum(0) / dt
    return D2, dt


# gene -> reactions map (cobra authoritative, as E22/V5)
gene_rxns = {}
for r in model.reactions:
    for g in r.genes:
        gene_rxns.setdefault(g.id, []).append(eng_ref.index[r.id])


def gene_panel(D2):
    vals = np.zeros(len(panel_genes))
    for i, g in enumerate(panel_genes):
        ridx = gene_rxns.get(g, [])
        if ridx:
            vals[i] = D2[ridx].max()
    return vals


# ----------------------------------------------------------- run arms
arms = {}
base = None
for name, W, mode in VARIANTS:
    eng = build_engine(W, mode)
    Vs, mus, s2s = solve_all(eng)
    D2, dt = per_reaction_kappa(Vs)
    kap = gene_panel(D2)
    arm = {"weights_mode": mode,
           "total_D2_mass": float(D2.sum()),
           "n_rxns_D2_gt_1e-8": int((D2 > 1e-8).sum()),
           "kappa": kap}
    if base is None:
        base = {"Vs": Vs, "mus": mus, "s2s": s2s, "kap": kap}
        # control: reproduce V5 to the digit
        nz = kap > 0
        r_ctrl = stats.pearsonr(np.log10(kap[nz]), y_all[nz])
        arm["control_reproduce_V5"] = {
            "n_nonzero": int(nz.sum()),
            "r_nonzero": round(float(r_ctrl[0]), 4),
            "p": float(r_ctrl[1])}
        print(f"[V8] {name} (control): n_nonzero={int(nz.sum())}, "
              f"r={r_ctrl[0]:+.4f} (V5 artifact: +0.3954)")
    else:
        dv = np.abs(Vs - base["Vs"]).max(axis=1)     # per grid point
        binding = dv > 1e-9
        arm["traj_max_vdiff_inf"] = float(dv.max())
        arm["n_grid_points_tiebreak_binds"] = int(binding.sum())
        arm["binding_grid_indices"] = [int(i) for i in
                                       np.where(binding)[0]]
        arm["value_layer_mu_maxdiff"] = float(
            np.abs(mus - base["mus"]).max())
        arm["pfba_layer_s2_maxdiff"] = float(
            np.abs(s2s - base["s2s"]).max())
        both = base["kap"] + kap
        nz = both > 0
        sp = stats.spearmanr(base["kap"][nz], kap[nz])
        arm["spearman_vs_declared"] = [float(sp[0]), float(sp[1])]
        arm["n_genes_kappa_changed"] = int(
            (np.abs(kap - base["kap"]) > 1e-12).sum())
    arms[name] = arm
    print(f"[V8] {name}: total D2={D2.sum():.4f}, "
          f"rxns D2>1e-8: {(D2 > 1e-8).sum()}")

# ---------------------------------------------- the association per arm
assoc = {}
for name, W, mode in VARIANTS:
    kap = arms[name]["kappa"]
    nz = kap > 0
    x = np.log10(kap[nz])
    yv = y_all[nz]
    zv = z_all[nz]
    pr = stats.pearsonr(x, yv)
    sr = stats.spearmanr(kap[nz], yv)
    part = partial_r(x, yv, zv)
    assoc[name] = {
        "n_nonzero": int(nz.sum()),
        "pearson_r": round(float(pr[0]), 4),
        "pearson_p": float(pr[1]),
        "spearman_r": round(float(sr[0]), 4),
        "partial_r_given_reflevel": round(float(part[0]), 4),
        "partial_p": float(part[1])}
    print(f"[V8] {name}: n={int(nz.sum())}, r={pr[0]:+.4f} "
          f"(p={pr[1]:.2g}), partial={part[0]:+.4f}")

# ------------------------------------------------------------- outputs
out = {
    "experiment": "V8 tie-break robustness of kappa^mu (review residual "
                  "risk 1 / advice 1: the declared lexicographic "
                  "selection is one of a family; measure the family)",
    "engine": "lex-pFBA iJO1366, E22 physiology, 8x refinement (57 "
              "points), V5/V6 protocol frozen; ONLY the stage-3 "
              "tie-break varies",
    "variants": {
        "TB0_declared": "w ~ U(0.5,1.5) seed 20240901, min w.v "
                        "(the locked metric)",
        "TB1_fresh_seed_same_family": "w ~ U(0.5,1.5) seed 20240902, "
                                      "min w.v",
        "TB2_lognormal_family": "w ~ LogN(0,1) clipped [0.05,20] seed "
                                "20240903, min w.v",
        "TB3_absflux_rule": "min sum w_r(f_r+r_r) = weighted |v| "
                            "selection, TB0 weights",
        "TB4_adversarial_max": "max w.v (far end of the pinned face), "
                               "TB0 weights"},
    "association": assoc,
    "arms": {k: {kk: vv for kk, vv in v.items() if kk != "kappa"}
             for k, v in arms.items()},
    "verdict": {}}

rs = [assoc[n]["pearson_r"] for n, _, _ in VARIANTS]
out["verdict"] = {
    "declared_r": rs[0],
    "variant_rs": rs[1:],
    "max_abs_deviation_from_declared": round(
        float(np.max(np.abs(np.array(rs[1:]) - rs[0]))), 4),
    "value_layer_invariance_max_mu_diff": max(
        arms[n].get("value_layer_mu_maxdiff", 0.0)
        for n, _, _ in VARIANTS[1:]),
    "tiebreak_binds_total_grid_points": {
        n: arms[n].get("n_grid_points_tiebreak_binds", 0)
        for n, _, _ in VARIANTS[1:]}}

with open(os.path.join(OUT, "v8_tiebreak_robustness.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)

rows = []
for i, g in enumerate(panel_genes):
    row = {"gene_bnumber": g}
    for name, _, _ in VARIANTS:
        row[name] = float(arms[name]["kappa"][i])
    rows.append(row)
pd.DataFrame(rows).set_index("gene_bnumber").to_csv(
    os.path.join(OUT, "v8_tiebreak_robustness.csv"))

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

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2),
                         constrained_layout=True)
ax = axes[0]
names_short = ["TB0 declared", "TB1 fresh seed", "TB2 LogN family",
               "TB3 |v| rule", "TB4 max w.v"]
cols = ["#1f4e79", "#548235", "#c00000", "#bf8f00", "#7030a0"]
rs_pl = [assoc[n]["pearson_r"] for n, _, _ in VARIANTS]
ax.bar(range(len(rs_pl)), rs_pl, color=cols)
for i, r_ in enumerate(rs_pl):
    ax.text(i, r_ + 0.008, f"{r_:+.3f}", ha="center", fontsize=9)
ax.axhline(rs_pl[0], color="#1f4e79", lw=1.0, ls="--", alpha=0.7)
ax.set_xticks(range(len(rs_pl)))
ax.set_xticklabels(names_short, fontsize=8.5, rotation=12)
ax.set_ylabel("Pearson r (nonzero panel)")
ax.set_ylim(0.3, 0.45)
ax.set_title("(a) association across tie-break variants")
ax = axes[1]
base_k = base["kap"]
m = base_k > 0
for (name, _, _), c in zip(VARIANTS[1:], cols[1:]):
    kap = arms[name]["kappa"]
    ax.scatter(np.log10(base_k[m]), np.log10(kap[m] + (kap[m] <= 0)),
               s=7, alpha=0.35, color=c, edgecolors="none",
               label=name.split("_")[0])
ax.set_xlabel(r"$\log_{10}\,\kappa^\mu$ (declared TB0)")
ax.set_ylabel(r"$\log_{10}\,\kappa^\mu$ (variant)")
ax.legend(fontsize=7.5, loc="upper left")
ax.set_title("(b) per-gene predictor agreement")
ax = axes[2]
lab = [n.split("_")[0] for n, _, _ in VARIANTS[1:]]
binds = [arms[n].get("n_grid_points_tiebreak_binds", 0)
         for n, _, _ in VARIANTS[1:]]
ax.bar(range(len(binds)), binds, color=cols[1:])
for i, b_ in enumerate(binds):
    ax.text(i, b_ + 0.2, str(b_), ha="center", fontsize=9)
ax.set_xticks(range(len(binds)))
ax.set_xticklabels(lab, fontsize=9)
ax.set_ylabel("grid points where stage 3 binds")
ax.set_title("(c) where the tie-break matters (of 57)")
fig.suptitle("V8 - tie-break robustness: the association is a property "
             "of the lexicographic protocol class, not of one rule",
             fontsize=11)
fig.savefig(os.path.join(OUT, "v8_tiebreak_robustness.png"), dpi=170)
plt.close(fig)

print(f"[V8] wall time {time.time() - t0:.0f} s; artifacts in {OUT}")
print(f"[V8] VERDICT: declared r={rs[0]:+.4f}; variants "
      f"{['%+.4f' % r for r in rs[1:]]}; value-layer mu invariant to "
      f"{out['verdict']['value_layer_invariance_max_mu_diff']:.1e}")
