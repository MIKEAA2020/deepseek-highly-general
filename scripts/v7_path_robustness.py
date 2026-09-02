#!/usr/bin/env python3
"""
V7 -- path robustness: does the one-chamber (value-layer-empty) property
of the E24 trajectory persist on other parameter paths?

The completed-round evaluation's residual risk #1 / recommendation #2:
"Run a second trajectory (e.g., oxygen limitation or acetate switch)
using the same engine to see whether the one-chamber property persists.
If value kinks appear, assess whether they contribute to the
correlation."

Design: the V6 protocol is frozen (engine, seed 20240901, iJO1366, panel,
statistics); only the TRAJECTORY (and its matched response) varies.

  P0 (control)  glucose decline, o2 declining in excess (E22 anchors)
                -> V6 reproduction; response: E24 carbon-depletion maxFC
  P1            OXYGEN LIMITATION at fixed glucose (q_glc = 5):
                q_o2 22 -> 1; crosses the respiratory chamber boundary
                (~q_o2 10-11 at q_glc 5); response: M3D M9_WT_anaerobic
                vs M9_WT (matched oxygen contrast)
  P2            ACETATE SWITCH at fixed o2 (q_o2 = 22): glucose
                5 -> 0 while acetate uptake ramps 0 -> 10 (the MOPS
                glucose -> acetate carbon switch, stylized);
                response: M3D WT_MOPS_acetate vs WT_MOPS_glucose

Per path: value-kink census (anchor/design corners vs interior chamber
crossings), Theorem-C coupling check at every kink, uptake-shadow-price
jumps (chamber markers), value/flux strain mass ratio, and the layer
arms against the matched response:

  A     kappa_mu       flux strain, all events (the locked metric)
  B1    kappa_vg_all   flux strain gated to all value-kink times
  B1b   kappa_vg_int   flux strain gated to INTERIOR-kink times  [TEST]
  B2    kappa_c        c-attribution of the value strain (Theorem C(ii))
  B3int kappa_dual_int shadow-price jumps at interior kinks        [TEST]
  B3all kappa_dual_all shadow-price jumps at all kinks (V6-comparable)
  ctrl  kappa_V_lex    V5 engine control
  plus a cross-response arm (P1/P2 predictors vs the E24 carbon response)

Outputs: download/deepseek_bridge/v7_path_robustness.{json,csv,png}
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
stat_cols = ["fc_m3d_stationary_135min", "fc_m3d_stationary_330min",
             "fc_m3d_stationary_480min", "fc_m3d_stationary_720min"]
y_carbon = e24[stat_cols].abs().max(axis=1).values          # E24 response
y_acetate = e24["fc_m3d_acetate"].abs().values              # P2 response

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
ANA = [f"M9_WT_anaerobic_r{i}" for i in range(1, 5)]
AER = [f"M9_WT_r{i}" for i in range(1, 4)]
fc_ana = (expr[ANA].mean(axis=1) - expr[AER].mean(axis=1)).reindex(e24.index)
y_anaerobic = fc_ana.abs().values                              # P1 response

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
i_glc, i_o2, i_ac = (eng.index["EX_glc__D_e"], eng.index["EX_o2_e"],
                     eng.index["EX_ac_e"])

# gene -> reactions map (cobra authoritative, as E22/V5/V6)
gene_rxns = {}
for r in model.reactions:
    for g in r.genes:
        gene_rxns.setdefault(g.id, []).append(eng.index[r.id])
panel_genes = list(e24.index)


# ------------------------------------------------------------ paths
PATHS = {
    "P0_glucose_decline": {
        "anchors_glc": [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0],
        "anchors_o2": [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0],
        "anchors_ac": [0.0] * 8,
        "response": "E24 carbon-depletion maxFC (M3D stationary)",
        "y": y_carbon},
    "P1_oxygen_limitation": {
        "anchors_glc": [5.0] * 8,
        "anchors_o2": [22.0, 19.0, 16.0, 13.0, 10.0, 7.0, 4.0, 1.0],
        "anchors_ac": [0.0] * 8,
        "response": "M3D M9_WT_anaerobic vs M9_WT (matched O2 contrast)",
        "y": y_anaerobic},
    "P2_acetate_switch": {
        "anchors_glc": [5.0, 4.2, 3.4, 2.7, 2.0, 1.4, 0.8, 0.0],
        "anchors_o2": [22.0] * 8,
        "anchors_ac": [0.0, 2.0, 4.0, 5.5, 7.0, 8.5, 9.5, 10.0],
        "response": "M3D WT_MOPS_acetate vs WT_MOPS_glucose (matched "
                    "carbon-switch contrast)",
        "y": y_acetate},
}

REFINE = 8


def trajectory(pa):
    T = []
    a_g, a_o, a_a = pa["anchors_glc"], pa["anchors_o2"], pa["anchors_ac"]
    for k in range(7):
        for j in range(REFINE):
            f = j / REFINE
            T.append((a_g[k] + f * (a_g[k + 1] - a_g[k]),
                      a_o[k] + f * (a_o[k + 1] - a_o[k]),
                      a_a[k] + f * (a_a[k + 1] - a_a[k])))
    T.append((a_g[-1], a_o[-1], a_a[-1]))
    return T


def solve_traj(T):
    Vs, mus = [], []
    for g, o, ac in T:
        lb, ub = eng.lb0.copy(), eng.ub0.copy()
        lb[i_glc] = -g
        lb[i_o2] = -o
        lb[i_ac] = -ac
        out = eng.solve_lex(lb, ub, bi)
        if out is None:
            raise RuntimeError(f"infeasible at ({g},{o},{ac})")
        Vs.append(out[0])
        mus.append(out[1])
    return np.array(Vs), np.array(mus)


def stage1(g, o, ac):
    """Stage-1-only solve with full bound marginals (exact Phi, duals)."""
    lb, ub = eng.lb0.copy(), eng.ub0.copy()
    lb[i_glc] = -g
    lb[i_o2] = -o
    lb[i_ac] = -ac
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
    m_up = np.abs(res.upper.marginals)
    m_lo = np.abs(res.lower.marginals)
    per = np.zeros(R)
    for i in range(3 * R):
        r = i % R
        per[r] = max(per[r], m_up[i], m_lo[i])
    return per


# =====================================================================
out = {"experiment": "V7 path robustness: does the one-chamber "
                     "(value-layer-empty) property persist across "
                     "trajectories? (completed-round evaluation, "
                     "residual risk 1 / recommendation 2)",
       "engine": "lex-pFBA (seed 20240901), iJO1366, V6 protocol frozen; "
                 "only the trajectory and its matched response vary",
       "paths": {}}

summary_rows = []
fig_data = {}

for pname, pa in PATHS.items():
    print(f"\n===== {pname} =====", flush=True)
    T = trajectory(pa)
    Vs, mus = solve_traj(T)
    N = len(T)
    tt = np.linspace(0, 1, N)
    dt = float(tt[1] - tt[0])
    anchor_idx = set(k * REFINE for k in range(8))

    # ---- value-kink census
    d2mu = np.abs(mus[2:] - 2 * mus[1:-1] + mus[:-2]) / dt
    kink_idx = [i + 1 for i in range(N - 2) if d2mu[i] > 1e-8]
    kcl = []
    for i in kink_idx:
        if kcl and i - kcl[-1][-1] <= 2:
            kcl[-1].append(i)
        else:
            kcl.append([i])
    kink_rows = []
    dual_per_rxn_int = np.zeros(R)
    dual_per_rxn_all = np.zeros(R)
    for cl in kcl:
        i0 = cl[int(np.argmax([d2mu[i - 1] for i in cl]))]
        t_k = tt[i0]
        is_at_anchor = any(abs(i - a) <= 1 for i in cl for a in anchor_idx)
        if 2 <= i0 <= N - 3:
            sL = (mus[i0 - 1] - mus[i0 - 2]) / dt
            sR = (mus[i0 + 2] - mus[i0 + 1]) / dt
            dphi = float(sR - sL)
            sl_v = (Vs[i0 - 1] - Vs[i0 - 2]) / dt
            sr_v = (Vs[i0 + 2] - Vs[i0 + 1]) / dt
            dv = sr_v - sl_v
            cT = float(c_bio @ dv)
            l1jump = float(np.abs(dv).sum())
            resL = stage1(*T[i0 - 2])
            resR = stage1(*T[i0 + 2])
            dy = marg_per_reaction(resR) - marg_per_reaction(resL)
            dy_sup = np.where(np.abs(dy) > 1e-9)[0]
            dy_uptake = [float(dy[i_glc]), float(dy[i_o2]),
                         float(dy[i_ac])]
            dual_jump_L1 = float(np.abs(dy[dy_sup]).sum()) if len(dy_sup) \
                else 0.0
            dual_ids = [eng.rxn_ids[i] for i in dy_sup][:12]
            dual_per_rxn_all += np.abs(dy)
            # Chamber classification: the parameters ARE the uptake
            # bounds, so grad Phi = (y_glc, y_o2, y_ac). A kink is a
            # DESIGN CORNER iff it sits at a trajectory anchor AND the
            # uptake shadow prices are continuous across it (jump = 0
            # to machine precision, as on the P0 single-chamber path);
            # it is a CHAMBER CROSSING iff the uptake shadow prices
            # jump (position near an anchor does NOT make a crossing a
            # design corner: P1's q_o2 ~ 6.25 boundary is 2 grid points
            # from an anchor yet carries a real dual jump).
            uptake_dual_jump_max = float(np.max(np.abs(dy_uptake)))
            is_design = is_at_anchor and uptake_dual_jump_max <= 1e-9
        else:
            dphi = cT = l1jump = dual_jump_L1 = 0.0
            dual_ids = []
            dy_sup = []
            dy_uptake = None
            dy = np.zeros(R)
            uptake_dual_jump_max = 0.0
            is_design = is_at_anchor
        kink_rows.append({
            "grid_index": i0, "t": float(t_k), "t_phys": list(T[i0]),
            "is_design_corner": bool(is_design),
            "is_chamber_crossing": bool(not is_design),
            "is_at_anchor_position": bool(is_at_anchor),
            "uptake_dual_jump_max": uptake_dual_jump_max,
            "delta_phi_slope": dphi,
            "flux_L1_slope_jump": l1jump,
            "cT_jump": cT,
            "coupling_err": abs(dphi - cT),
            "n_reactions_in_dual_jump": int(len(dy_sup)),
            "dual_uptake_jump": dy_uptake,
            "dual_jump_L1": dual_jump_L1,
            "dual_jump_rxn_ids": dual_ids})
        if not is_design:
            dual_per_rxn_int += np.abs(dy)
        print(f"[{pname}] kink t={t_k:.3f} "
              f"{'design' if is_design else 'CROSSING'}"
              f" dPhi'={dphi:+.3e} cT={cT:+.3e} "
              f"err={abs(dphi - cT):.1e} "
              f"dual(y_glc,y_o2,y_ac)={dy_uptake}", flush=True)

    n_cross = sum(1 for r in kink_rows if r["is_chamber_crossing"])
    value_strain_total = sum(abs(r["delta_phi_slope"]) for r in kink_rows)
    flux_strain_total = float(
        np.abs(Vs[2:] - 2 * Vs[1:-1] + Vs[:-2]).sum() / dt)

    # ---- predictors
    D2 = np.abs(Vs[2:] - 2 * Vs[1:-1] + Vs[:-2]) / dt     # (N-2, R)
    disp = (Vs - Vs[0])
    kv_lex = (disp ** 2).max(0)

    gate_all = np.zeros(N - 2, bool)
    gate_int = np.zeros(N - 2, bool)
    for r in kink_rows:
        i0 = r["grid_index"]
        for j in range(max(0, i0 - 2), min(N - 2, i0 + 1)):
            gate_all[j] = True
            if r["is_chamber_crossing"]:
                gate_int[j] = True
    D2_vg_all = D2 * gate_all[:, None]
    D2_vg_int = D2 * gate_int[:, None]

    c_per_rxn = np.abs(c_bio) * value_strain_total

    rows = []
    for gne in panel_genes:
        ridx = gene_rxns.get(gne, [])
        if not ridx:
            rows.append({"gene": gne, "kappa_mu": 0.0, "kappa_vg_all": 0.0,
                         "kappa_vg_int": 0.0, "kappa_dual_int": 0.0,
                         "kappa_dual_all": 0.0, "kappa_c": 0.0,
                         "kappa_v_lex": 0.0, "n_rxns": 0})
            continue
        rows.append({
            "gene": gne,
            "kappa_mu": float(D2[:, ridx].max()),
            "kappa_vg_all": float(D2_vg_all[:, ridx].max()),
            "kappa_vg_int": float(D2_vg_int[:, ridx].max()),
            "kappa_dual_int": float(dual_per_rxn_int[ridx].max()),
            "kappa_dual_all": float(dual_per_rxn_all[ridx].max()),
            "kappa_c": float(c_per_rxn[ridx].max()),
            "kappa_v_lex": float(kv_lex[ridx].max()),
            "n_rxns": len(ridx)})
    df = pd.DataFrame(rows).set_index("gene")

    y = pa["y"]
    preds = {
        "A kappa_mu (flux, all events)":
            (np.log10(df["kappa_mu"]).values, df["kappa_mu"].values),
        "B1 kappa_vg (value-gated, all kinks)":
            (np.log10(df["kappa_vg_all"]).values, df["kappa_vg_all"].values),
        "B1b kappa_vg (interior kinks only)":
            (np.log10(df["kappa_vg_int"]).values, df["kappa_vg_int"].values),
        "B2 kappa_c (c-attribution)":
            (np.log10(df["kappa_c"]).values, df["kappa_c"].values),
        "B3int kappa_dual (interior kinks)":
            (np.log10(df["kappa_dual_int"]).values,
             df["kappa_dual_int"].values),
        "B3all kappa_dual (all kinks, V6-comparable)":
            (np.log10(df["kappa_dual_all"]).values,
             df["kappa_dual_all"].values),
        "kappa_V_lex (engine control)":
            (np.log10(df["kappa_v_lex"]).values, df["kappa_v_lex"].values),
    }
    arms = {}
    for name, (logv, rawv) in preds.items():
        nz = rawv > 0
        r_nz = corr_stats(logv[nz], y[nz], label=f"{name} [nonzero]")
        arms[name] = {"n_nonzero": int(nz.sum()), "nonzero": r_nz}
        print(f"[{pname}] {name}: n_nonzero={int(nz.sum())} "
              f"r={r_nz.get('pearson_r')}", flush=True)

    # cross-response arm: this path's flux predictor vs the E24 response
    nz = df["kappa_mu"].values > 0
    if pname != "P0_glucose_decline":
        arms["A kappa_mu vs E24 carbon response (cross)"] = {
            "n_nonzero": int(nz.sum()),
            "nonzero": corr_stats(np.log10(df["kappa_mu"].values[nz]),
                                  y_carbon[nz],
                                  label="cross-response [nonzero]")}

    partials = {}
    for name, col in (("A kappa_mu", "kappa_mu"),
                      ("B1b kappa_vg_int", "kappa_vg_int"),
                      ("B3int kappa_dual", "kappa_dual_int")):
        v = df[col].values
        nz = v > 0
        if nz.sum() >= 5:
            pr = partial_r(np.log10(v[nz]), y[nz], z[nz])
            partials[name] = round(float(pr[0]), 4)
            print(f"[{pname}] partial r({col} | ref level) = "
                  f"{pr[0]:+.4f} (p={pr[1]:.2g})", flush=True)

    out["paths"][pname] = {
        "trajectory_anchors": {"q_glc": pa["anchors_glc"],
                               "q_o2": pa["anchors_o2"],
                               "q_ac": pa["anchors_ac"]},
        "matched_response": pa["response"],
        "value_kink_census": {
            "n_grid_points": N, "refine": REFINE,
            "n_value_kinks_total": len(kink_rows),
            "n_design_corners": len(kink_rows) - n_cross,
            "n_chamber_crossings": n_cross,
            "classification_rule": "design corner = kink at a "
                                   "trajectory anchor with uptake "
                                   "shadow prices continuous (jump "
                                   "<= 1e-9); chamber crossing = "
                                   "uptake shadow prices jump (the "
                                   "parameters are the uptake bounds, "
                                   "so grad Phi = (y_glc, y_o2, y_ac))",
            "value_strain_total": value_strain_total,
            "flux_strain_total": flux_strain_total,
            "value_over_flux_mass_ratio":
                value_strain_total / flux_strain_total,
            "kinks": kink_rows},
        "arms": arms,
        "partial_r_given_ref_level": partials}

    for name in ("A kappa_mu (flux, all events)",
                 "B1b kappa_vg (interior kinks only)",
                 "B3int kappa_dual (interior kinks)"):
        a = arms[name]
        summary_rows.append({
            "path": pname, "arm": name,
            "n_nonzero": a["n_nonzero"],
            "r": a["nonzero"].get("pearson_r"),
            "response": pa["response"]})
    df.to_csv(os.path.join(OUT, f"v7_{pname}.csv"), index_label="gene")
    fig_data[pname] = {"tt": tt, "mus": mus, "kink_rows": kink_rows,
                       "n_cross": n_cross, "df": df, "y": y}

# =====================================================================
# Figure: 3 rows (paths) x 2 cols (value trajectory; arm bars)
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

fig, axes = plt.subplots(3, 2, figsize=(11.5, 11.0),
                         constrained_layout=True)
titles = {"P0_glucose_decline": "P0 glucose decline (V6 control)",
          "P1_oxygen_limitation": "P1 oxygen limitation (q$_{glc}$=5)",
          "P2_acetate_switch": "P2 acetate switch (q$_{O2}$=22)"}
for row, pname in enumerate(PATHS):
    fd = fig_data[pname]
    ax = axes[row, 0]
    ax.plot(fd["tt"], fd["mus"], "-", lw=1.8, color="#1f4e79")
    for r in fd["kink_rows"]:
        col = "#c00000" if r["is_chamber_crossing"] else "#7f7f7f"
        ax.axvline(r["t"], color=col,
                   lw=1.6 if r["is_chamber_crossing"] else 0.8,
                   ls="-" if r["is_chamber_crossing"] else ":")
    ax.set_xlabel("t along trajectory")
    ax.set_ylabel(r"$\Phi(t)$")
    ax.set_title(f"({chr(97 + row)}1) {titles[pname]}: "
                 f"{fd['n_cross']} chamber crossings")
    ax = axes[row, 1]
    names = ["A $\\kappa^\\mu$\n(flux)",
             "B1b $\\kappa^{vg}$\n(interior)",
             "B3int $\\kappa^{dual}$\n(interior)",
             "B2 $\\kappa^{c}$"]
    cols = ["kappa_mu", "kappa_vg_int", "kappa_dual_int", "kappa_c"]
    rs_ = []
    for c in cols:
        v = fd["df"][c].values
        nz = v > 0
        if nz.sum() > 3:
            rr_ = stats.pearsonr(np.log10(v[nz]), fd["y"][nz])[0]
        else:
            rr_ = np.nan
        rs_.append(rr_)
    ax.bar(range(4), rs_, color=["#1f4e79", "#548235", "#bf9000",
                                 "#7f7f7f"])
    for i, (r_, c) in enumerate(zip(rs_, cols)):
        nz = (fd["df"][c].values > 0).sum()
        ax.text(i, 0.02 if not np.isfinite(r_) else r_ + 0.015,
                f"{'nan' if not np.isfinite(r_) else f'{r_:+.3f}'}\n"
                f"(n={int(nz)})", ha="center", fontsize=8.5)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(range(4))
    ax.set_xticklabels(names, fontsize=8.5)
    ax.set_ylabel("Pearson r (matched response)")
    ax.set_title(f"({chr(97 + row)}2) layer arms")
fig.suptitle("V7 - path robustness: value-kink census and layer arms "
             "across three trajectories", fontsize=11)
fig.savefig(os.path.join(OUT, "v7_path_robustness.png"), dpi=170)
plt.close(fig)

pd.DataFrame(summary_rows).to_csv(
    os.path.join(OUT, "v7_path_robustness.csv"), index=False)
with open(os.path.join(OUT, "v7_path_robustness.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)

print(f"\n[V7] wall time {time.time() - t0:.0f} s; artifacts in {OUT}",
      flush=True)
