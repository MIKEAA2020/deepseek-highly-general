#!/usr/bin/env python3
"""
Verification battery for the audit "deepseek stengthen highly general
bridge.txt" (DeepSeek's response to the M4c / root-cause evaluation).

The audit proposes five "strengthening routes" for the bridge and a
recommended target theorem

    kappa_geom = lim_{sigma->0} kappa_flux * phi_sigma   (weak conv.)

This script adjudicates the checkable mathematical content on three
fronts:

V1  Real-network value-function carrier (Route 3, corrected).
    DeepSeek claims v(theta) = grad Phi(theta) "under suitable
    conditions".  For constraint/RHS parameterization this is false
    (dimensional mismatch alone: v in R^m, grad Phi in R^d).  The TRUE
    statement of the value-function route is: Phi (stage-1 biomass
    optimum) is itself piecewise linear with atomic D^2 Phi (shadow-
    price jumps, Danskin), single-valued WITHOUT any tie-breaking --
    arguably the canonical curvature carrier.  We re-run the M4c cut
    on iML1515 recording Phi(t):
      (a) Phi piecewise-affine between the M4c v-events (residuals);
      (b) which of the 12 v-events kink Phi (objective-moving events
          vs mask-type events), and the Phi atom sizes;
      (c) Danskin check: bound-marginal (shadow price) prediction of
          the segment slopes of Phi vs finite differences;
      (d) flux-jump norm vs value-jump scatter (the two carriers are
          NOT proportional: mask-type events reroute flux with no
          value kink -- the RC6/Kochanowski pattern).

V2  Refinement prototype (Routes 1+2, corrected) -- the joint limit.
    A family of parametric LPs (value function = max of n affine
    functions = LP with theta in the RHS, constraint matrix fixed --
    the same structural class as uptake-bound FBA) whose constraint /
    tangency mesh h_n -> 0 while Phi_n -> f smooth concave.  We verify
    numerically:
      (a) REFINEMENT limit: the atomic measures D^2(Phi_n|cut) converge
          to the smooth curvature density u^T Hess f u (L1/W1 -> 0);
          rate in h.
      (b) SIGMA limit at fixed n: mu_n * phi_sigma -> atomic as
          sigma -> 0 (the audit's limit direction picks the ATOMIC
          object, not a smooth density -- Theorem N's obstruction);
      (c) the joint limit: fixed sigma >> h_n converges to the smooth
          density (the corrected theorem).
    Proof of the prototype theorem is in the evaluation document; the
    script supplies the machine check.

V3  sigma->0 inversion on the MEASURED real-network measure (M4c cut
    event census): as sigma -> 0 the family mu*phi_sigma converges
    weakly to the atomic measure mu (mass collapses onto the 12
    events; density at wall-free points -> 0 exponentially; hat tests
    on events -> atom masses), and its distance to any FIXED smooth
    density stays bounded away from 0.  Hence the audit's headline
    formula lim_{sigma->0} ... = kappa_geom dvol_g is falsified on the
    measured object; the defensible statement is the resolution
    statement (Theorem R / M4c) at fixed sigma.

Outputs: download/deepseek_bridge/{v1_value_function.{json,csv,png},
v2_refinement.{json,csv,png}, v3_sigma_limit.{json,csv,png}}
"""
import csv
import json
import os
import sys
import time
import warnings

import numpy as np

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")
os.makedirs(OUT, exist_ok=True)

t_start = time.time()


def save_json(obj, name):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=1)


# =====================================================================
# V1 -- value-function carrier on the real network (iML1515, M4c cut)
# =====================================================================
def run_v1():
    import cobra
    from cobra.util.solver import linear_reaction_coefficients
    from scipy.optimize import linprog
    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from lp_engine import LPEngine

    # locus: identical to M4c (the M4b codim-2 vertex, dB direction)
    THETA0 = np.array([1.6920021856564074, 1.4795937837603242])
    DB = np.array([0.6473547604531503, -0.7621888310114787])
    SPAN, N_GRID = 0.4, 161            # full M4c span

    # M4c event record (measured, committed): 12 events on the cut
    ev = np.genfromtxt(
        os.path.join(BASE, "download", "m4", "m4c_cut_events.csv"),
        delimiter=",", names=True)
    t_events = np.atleast_1d(ev["t_event"])
    jump_norm = np.atleast_1d(ev["jump_L2"])

    model = cobra.io.load_json_model(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    co = linear_reaction_coefficients(model)
    c_bio = np.zeros(len(model.reactions))
    for r, c in co.items():
        c_bio[model.reactions.index(r)] = c
    bio_id = list(co.keys())[0].id
    rng = np.random.default_rng(20240901)      # same tie-break as M1/M4*
    W = rng.uniform(0.5, 1.5, len(model.reactions))
    eng = LPEngine(model, W, c_bio)
    bi = eng.index[bio_id]
    i_glc, i_o2 = eng.index["EX_glc__D_e"], eng.index["EX_o2_e"]
    R = eng.R

    cache = {}
    n_solves = [0]

    def solve_at(t):
        key = round(float(t), 12)
        if key in cache:
            return cache[key]
        p = THETA0 + t * DB
        lb, ub = eng.lb0.copy(), eng.ub0.copy()
        lb[i_glc] = -p[0]
        lb[i_o2] = -p[1]
        out = eng.solve_lex(lb, ub, bi)
        n_solves[0] += 1
        if out is None:
            raise RuntimeError(f"infeasible at t={t}")
        cache[key] = out[1]
        return out[1]

    def phi_at(t):
        return solve_at(t)

    # ---- (a) grid + piecewise affinity of Phi on the v-event partition
    ts = np.linspace(-SPAN, SPAN, N_GRID)
    phi_grid = np.array([phi_at(t) for t in ts])

    bounds = np.concatenate([[-SPAN], t_events, [SPAN]])
    seg_res = []
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        if b - a < 1e-9:
            continue
        m = (ts >= a + 1e-12) & (ts <= b - 1e-12)
        if m.sum() < 3:
            continue
        x, y = ts[m], phi_grid[m]
        A = np.column_stack([x, np.ones_like(x)])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ coef
        rel = np.max(np.abs(pred - y)) / max(1e-12, np.max(np.abs(y)))
        seg_res.append({"t_lo": float(a), "t_hi": float(b),
                        "n_pts": int(m.sum()), "slope": float(coef[0]),
                        "max_rel_resid": float(rel)})
    worst = max(s["max_rel_resid"] for s in seg_res)

    # ---- (b) per-event Phi atoms with ADAPTIVE probe spacing
    #  probe distance scaled to the local event gap so tight clusters
    #  (slivers) are resolved individually; pairs closer than the
    #  achievable resolution are reported with their net (cluster) atom.
    def gap_window(te, k):
        gaps = []
        if k > 0:
            gaps.append(te - t_events[k - 1])
        if k < len(t_events) - 1:
            gaps.append(t_events[k + 1] - te)
        g = min(gaps) if gaps else 2 * SPAN
        d = min(2e-4, 0.25 * g)
        return max(d, 5e-8), min(2e-4, 0.5 * g)

    probe_rows = []
    for k, (te, jn) in enumerate(zip(t_events, jump_norm)):
        d1, d2 = gap_window(te, k)
        xl, xr = max(te - 2 * d2, -SPAN + 1e-9), max(te - d1, -SPAN + 1e-9)
        yl, yr = min(te + d1, SPAN - 1e-9), min(te + 2 * d2, SPAN - 1e-9)
        if xr - xl < 1e-10 or yr - yl < 1e-10:
            d1 = d2 = 2e-5
            xl, xr = te - 2 * d1, te - d1
            yl, yr = te + d1, te + 2 * d1
        s_left = (phi_at(xr) - phi_at(xl)) / (xr - xl)
        s_right = (phi_at(yr) - phi_at(yl)) / (yr - yl)
        probe_rows.append({
            "t_event": float(te), "jump_L2_flux": float(jn),
            "probe_d": float(d1),
            "slope_left": float(s_left), "slope_right": float(s_right),
            "delta_phi_slope": float(s_right - s_left)})

    # noise scale: VARIATION of repeated FD slopes in a deep chamber
    # interior (LP mu noise ~1e-13 over 2e-4 windows -> ~5e-10)
    t_flat = -0.25
    base = (phi_at(t_flat + 3e-4) - phi_at(t_flat + 1e-4)) / 2e-4
    noise = []
    for j in range(4):
        s = (phi_at(t_flat + 3e-4 + 1e-6 * j) -
             phi_at(t_flat + 1e-4 + 1e-6 * j)) / 2e-4
        noise.append(abs(s - base))
    mu_noise = 1e-13
    for r in probe_rows:
        r["res_floor"] = mu_noise / r["probe_d"]
    noise_scale = max(max(noise), 1e-12)

    def atom_flag(r):
        # absolute threshold justified by: LP mu reproducibility ~1.5e-14
        # (segment-fit residuals 4e-13 relative), FD slope resolution at
        # probe distance d ~ 1e-13/d <= 1e-9 for d >= 1e-4; adaptive-d
        # probes for tight pairs carry a documented res_floor.  Atoms
        # below 1e-9 are sub-resolution; cluster C atoms are ~1e-3.
        return abs(r["delta_phi_slope"]) > max(1e-9, 20 * r["res_floor"])

    kinked = [r for r in probe_rows if atom_flag(r)]
    n_phi_kinks = len(kinked)

    # ---- cluster-level nets (the physically meaningful atoms)
    #  cluster = events within 1e-3 of each other
    clusters = []
    cur = [0]
    for k in range(1, len(t_events)):
        if t_events[k] - t_events[k - 1] < 1e-3:
            cur.append(k)
        else:
            clusters.append(cur)
            cur = [k]
    clusters.append(cur)
    cl_rows = []
    for cl in clusters:
        t0, t1 = t_events[cl[0]], t_events[cl[-1]]
        # net slope change across the cluster at generous probes
        d = max(2e-4, 1.5 * (t1 - t0))
        xl, xr = t0 - 2 * d, t0 - d
        yl, yr = t1 + d, t1 + 2 * d
        s_l = (phi_at(xr) - phi_at(xl)) / (xr - xl)
        s_r = (phi_at(yr) - phi_at(yl)) / (yr - yl)
        cl_rows.append({
            "t_lo": float(t0), "t_hi": float(t1), "n_events": len(cl),
            "max_flux_jump": float(max(jump_norm[cl])),
            "net_delta_phi": float(s_r - s_l),
            "net_is_real": bool(abs(s_r - s_l) > 1e-9)})

    # ---- (c) Danskin: bound-marginal (r-copy) shadow prices vs FD
    def shadow_prices(glc, o2, h=1e-4):
        """FD 2-sided shadow prices + LP marginals (r-copy upper)."""
        def stage1(g, o):
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
        r_p = stage1(glc + h, o2)
        r_m = stage1(glc - h, o2)
        y_glc_fd = (r_m.fun - r_p.fun) / (2 * h)  # obj = -Phi
        r_p2, r_m2 = stage1(glc, o2 + h), stage1(glc, o2 - h)
        y_o2_fd = (r_m2.fun - r_p2.fun) / (2 * h)
        res0 = stage1(glc, o2)
        # duals live on the r-copy of the duplicated uptake bound
        y_glc_lp = -float(res0.upper.marginals[i_glc + 2 * R])
        y_o2_lp = -float(res0.upper.marginals[i_o2 + 2 * R])
        n_solves[0] += 5
        return (float(y_glc_fd), float(y_o2_fd), y_glc_lp, y_o2_lp)

    danskin = []
    for tc in (-0.25, -0.05, 0.012, 0.03, 0.2):
        p = THETA0 + tc * DB
        gfd, ofd, glp, olp = shadow_prices(p[0], p[1])
        pred_cut = glp * DB[0] + olp * DB[1]
        danskin.append({
            "t_center": tc, "y_glc_fd": gfd, "y_o2_fd": ofd,
            "y_glc_lp": glp, "y_o2_lp": olp,
            "danskin_rel_err": abs(glp - gfd) / max(abs(gfd), 1e-12),
            "cut_slope_from_prices": float(pred_cut)})
    dan_err = [d["danskin_rel_err"] for d in danskin]

    # ---- (d) scatter data
    scatter = [{"t_event": r["t_event"],
                "jump_L2_flux": r["jump_L2_flux"],
                "abs_delta_phi": abs(r["delta_phi_slope"])}
               for r in probe_rows]

    # figure
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

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0),
                             constrained_layout=True)
    ax = axes[0]
    ax.plot(ts, phi_grid, "-", lw=1.8, color="#1f4e79")
    for r in probe_rows:
        if atom_flag(r):
            ax.axvline(r["t_event"], color="#c00000", lw=1.1, alpha=0.85)
        else:
            ax.axvline(r["t_event"], color="#7f7f7f", lw=0.8, ls=":",
                       alpha=0.7)
    ax.set_xlabel("t along M4c cut (through codim-2 vertex)")
    ax.set_ylabel(r"$\Phi(t)$ = stage-1 biomass optimum")
    ax.set_title(f"(a) value function; red: {n_phi_kinks} real "
                 f"$\\Phi$-atoms / {len(t_events)} v-events")
    ax = axes[1]
    jn = np.array([r["jump_L2_flux"] for r in probe_rows])
    dp = np.array([abs(r["delta_phi_slope"]) for r in probe_rows])
    ax.loglog(jn, np.maximum(dp, 1e-13), "o", ms=6, color="#595959")
    floors = np.array([max(8 * noise_scale, 20 * r["res_floor"])
                       for r in probe_rows])
    ax.loglog(jn, floors, "x", ms=5, color="#c00000",
              label="resolution floor per event")
    ax.set_xlabel(r"$\|$flux jump$\|_2$ (codim-1 carrier)")
    ax.set_ylabel(r"$|\Delta\Phi'|$ (value carrier)")
    ax.set_title("(b) decoupling of the two carriers")
    ax.legend(fontsize=8, loc="upper left")
    ax = axes[2]
    ax.semilogy(range(len(seg_res)),
                np.maximum([s["max_rel_resid"] for s in seg_res], 1e-17),
                "o-", ms=4, color="#1f4e79")
    ax.set_xlabel("v-event partition segment index")
    ax.set_ylabel("max rel. affine-fit residual of $\\Phi$")
    ax.set_title(f"(c) $\\Phi$ piecewise-affine (worst {worst:.1e})")
    fig.suptitle("V1 - value-function carrier on the M4c cut (iML1515)",
                 fontsize=11)
    fig.savefig(os.path.join(OUT, "v1_value_function.png"), dpi=170)
    plt.close(fig)

    with open(os.path.join(OUT, "v1_value_function.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(probe_rows[0].keys()))
        w.writeheader()
        for r in probe_rows:
            w.writerow(r)

    out = {
        "experiment": "V1 value-function carrier (Route 3 corrected)",
        "model": "iML1515", "cut": "M4c cut (M4b codim-2 vertex, dB)",
        "n_lex_solves": n_solves[0],
        "phi_piecewise_affine": {
            "n_segments": len(seg_res),
            "worst_rel_resid": float(worst)},
        "v_events_total": int(len(t_events)),
        "phi_atoms_real": int(n_phi_kinks),
        "phi_noise_scale": float(noise_scale),
        "atoms": [{k: r[k] for k in ("t_event", "jump_L2_flux",
                                     "delta_phi_slope")}
                  for r in kinked],
        "clusters": cl_rows,
        "danskin_check": danskin,
        "danskin_max_rel_err": float(max(dan_err)),
        "scatter": scatter,
        "verdict": {
            "v_equals_grad_phi": "FALSE for constraint/RHS "
            "parameterization (v in R^m vs grad Phi in R^d; the gradient "
            "map is the DUAL y in R^d)",
            "canonical_carrier": "Phi = c.v* is single-valued WITHOUT "
            "tie-breaking; D^2 Phi (shadow-price jumps) is the canonical "
            "atomic measure, tie-break-independent; the flux measure "
            "D^2 v needs the lex machine and has a FINER event set",
            "danskin": "y from r-copy bound marginals matches FD to "
                       f"{max(dan_err):.1e} (rel)"}}
    save_json(out, "v1_value_function.json")
    print(f"[V1] solves={n_solves[0]}  segments={len(seg_res)} "
          f"worst_resid={worst:.2e}")
    print(f"[V1] real Phi atoms {n_phi_kinks}/{len(t_events)} of "
          f"v-events; noise={noise_scale:.2e}")
    for c in cl_rows:
        print(f"[V1] cluster [{c['t_lo']:+.5f},{c['t_hi']:+.5f}] "
              f"n={c['n_events']} maxfluxjump={c['max_flux_jump']:.1f} "
              f"net dPhi'={c['net_delta_phi']:+.2e} "
              f"real={c['net_is_real']}")
    for d in danskin:
        print(f"[V1] Danskin t={d['t_center']:+.3f} "
              f"y_glc fd/lp {d['y_glc_fd']:.6f}/{d['y_glc_lp']:.6f} "
              f"y_o2 fd/lp {d['y_o2_fd']:.6f}/{d['y_o2_lp']:.6f} "
              f"cut-slope {d['cut_slope_from_prices']:.6f}")
    return out


# =====================================================================
# V2 -- refinement prototype (Routes 1+2 corrected)
# =====================================================================
def run_v2():
    rng = np.random.default_rng(20260901)

    # concave smooth limit value function with non-constant curvature
    def f(theta):
        return 2.0 - 0.5 * np.sum(theta ** 2, -1) \
            - 0.1 * np.sum(theta ** 4, -1)

    def grad_f(theta):
        return -theta - 0.4 * theta ** 3

    # Phi_n = MIN of tangent planes at n^2 tangency points (each plane
    # lies above the concave f; the pointwise min converges DOWN to f).
    # This is the value function of a parametric LP with a FIXED
    # constraint matrix and theta entering the RHS affinely
    # (min z s.t. z >= a_i.theta + b_i), the same structural class as
    # uptake-bound FBA.  Refining the tangency mesh h -> 0 is a genuine
    # refinement of the LP family (nested outer approximations).
    def make_phi_n(n):
        g = np.linspace(-1.0, 1.0, n)
        P = np.stack(np.meshgrid(g, g, indexing="ij"), -1).reshape(-1, 2)
        A = grad_f(P)                      # plane slopes  (n^2, 2)
        B = f(P) - np.sum(A * P, -1)       # plane offsets (n^2,)
        return A, B

    # ---- cut design: random lines through the domain
    K_CUTS = 40
    TT = np.linspace(-0.62, 0.62, 2401)

    def cut_points():
        a = rng.uniform(-0.3, 0.3, 2)
        ang = rng.uniform(0, np.pi)
        u = np.array([np.cos(ang), np.sin(ang)])
        pts = a[None, :] + TT[:, None] * u[None, :]
        inside = (np.abs(pts) <= 0.98).all(-1)   # core of the domain
        return a, u, pts, inside

    cuts = [cut_points() for _ in range(K_CUTS)]

    def atoms_on_cut(A, B, a, u, inside):
        """Exact 1D restriction g_n(t) = min_i (alpha_i t + beta_i);
        breakpoints solved exactly; atoms = slope jumps."""
        alpha = A @ u                       # (n^2,)
        beta = A @ a + B                    # (n^2,)
        # active pieces along the grid: argmin of alpha*t+beta
        vals = alpha[None, :] * TT[:, None] + beta[None, :]
        idx = np.argmin(vals, -1)           # (T,)
        chg = np.nonzero(np.diff(idx) != 0)[0]
        atoms = []
        for k in chg:
            i, j = idx[k], idx[k + 1]
            if alpha[i] == alpha[j]:
                continue
            tb = (beta[j] - beta[i]) / (alpha[i] - alpha[j])
            # keep atoms inside the core of the domain
            p = a + tb * u
            if np.max(np.abs(p)) > 0.98:
                continue
            atoms.append((tb, alpha[j] - alpha[i]))
        return np.array(atoms) if atoms else np.zeros((0, 2))

    B_BINS = 120
    bins = np.linspace(-0.62, 0.62, B_BINS + 1)

    def target_density(pts, inside, u):
        # u^T Hess f u along the cut (Hess = -I - 1.2 diag(theta^2))
        return -(u[0] ** 2 + u[1] ** 2) - 1.2 * (
            pts[:, 0] ** 2 * u[0] ** 2 + pts[:, 1] ** 2 * u[1] ** 2)

    DT = TT[1] - TT[0]

    def binned_atoms(at, target):
        """atoms are a measure (positions, masses); target is a density
        on the TT grid -> Riemann sum x DT."""
        mn, _ = np.histogram(at[:, 0], bins=bins, weights=at[:, 1])
        mstar, _ = np.histogram(TT, bins=bins, weights=target)
        return mn, mstar * DT

    def binned_dens(dens, target):
        """both sides are densities on the TT grid."""
        mn, _ = np.histogram(TT, bins=bins, weights=dens)
        mstar, _ = np.histogram(TT, bins=bins, weights=target)
        return mn * DT, mstar * DT

    # ---- (a) refinement limit: weak convergence must be tested at a
    # scale COARSER than the mesh (test functions >> h): adaptive bins
    n_grid = [4, 8, 16, 32, 64, 128]
    rows = []
    for n in n_grid:
        h = 2.0 / (n - 1)
        nb = max(2, int(np.ceil(1.24 / (4 * h))))    # bins ~ 4h wide
        bns = np.linspace(-0.62, 0.62, nb + 1)
        A, B = make_phi_n(n)
        l1s, w1s, mratios = [], [], []
        for a, u, pts, inside in cuts[:25]:
            at = atoms_on_cut(A, B, a, u, inside)
            if at.size == 0:
                continue
            mn, _ = np.histogram(at[:, 0], bins=bns, weights=at[:, 1])
            mstar, _ = np.histogram(TT, bins=bns,
                                    weights=target_density(pts, inside, u))
            mstar = mstar * DT
            tot = np.abs(mstar).sum()
            l1 = np.abs(mn - mstar).sum() / tot
            cw_n = np.cumsum(np.abs(mn))
            cw_s = np.cumsum(np.abs(mstar))
            if cw_n[-1] > 0 and cw_s[-1] > 0:
                # unnormalized W1 (masses are comparable, no rescaling)
                w1 = np.trapezoid(np.abs(cw_n - cw_s), bns[:-1]) / \
                    (bns[-1] - bns[0])
                w1n = np.trapezoid(np.abs(cw_n / cw_n[-1] -
                                          cw_s / cw_s[-1]), bns[:-1]) / \
                    (bns[-1] - bns[0])
            else:
                w1 = w1n = np.nan
            l1s.append(l1)
            w1s.append(w1n)
            mratios.append(np.abs(mn).sum() / tot)
        rows.append({"n": n, "h": h, "n_bins": nb, "L1_mean":
                     float(np.mean(l1s)), "L1_med": float(np.median(l1s)),
                     "W1_mean": float(np.nanmean(w1s)),
                     "W1_abs_mean": float(np.nanmean(w1)),
                     "mass_ratio": float(np.mean(mratios))})
        print(f"[V2a] n={n:4d} h={h:.4f} bins={nb:3d} "
              f"L1={np.mean(l1s):.4f} W1={np.nanmean(w1s):.4f} "
              f"mass_ratio={np.mean(mratios):.3f}")
    hs = np.array([r["h"] for r in rows])
    l1m = np.array([r["L1_med"] for r in rows])
    ok = (l1m > 0) & (l1m < 0.9)          # exclude the unresolved plateau
    alpha_rate = float(np.polyfit(np.log(hs[ok]), np.log(l1m[ok]), 1)[0])

    # ---- (b) sigma -> 0 at fixed n (the audit's limit direction)
    n_fixed = 32
    A, B = make_phi_n(n_fixed)
    a, u, pts, inside = cuts[0]
    at = atoms_on_cut(A, B, a, u, inside)
    target = target_density(pts, inside, u)
    sigmas = [0.3, 0.1, 0.06, 0.03, 0.015, 0.007, 0.003]
    sig_rows = []
    for sg in sigmas:
        dens = np.zeros_like(TT)
        for te, m in at:
            dens += m * np.exp(-0.5 * ((TT - te) / sg) ** 2) / \
                (sg * np.sqrt(2 * np.pi))
        mn, mstar = binned_dens(dens, target)
        l1_smooth = np.abs(mn - mstar).sum() / np.abs(mstar).sum()
        w = 0.01
        near = np.zeros_like(TT, bool)
        for te, _ in at:
            near |= np.abs(TT - te) <= w
        frac = dens[near].sum() / dens.sum()
        sig_rows.append({"sigma": sg, "L1_to_smooth": float(l1_smooth),
                         "mass_frac_near_atoms_w0.04": float(frac)})
        print(f"[V2b] sigma={sg:.3f} L1_to_smooth={l1_smooth:.4f} "
              f"near-atom mass frac={frac:.4f}")

    # ---- (c) joint limit: fixed sigma (>> h), n -> inf
    sg_fix = 0.05
    joint_rows = []
    for n in n_grid:
        A, B = make_phi_n(n)
        l1s = []
        for a, u, pts, inside in cuts[:25]:
            at = atoms_on_cut(A, B, a, u, inside)
            if at.size == 0:
                continue
            dens = np.zeros_like(TT)
            for te, m in at:
                dens += m * np.exp(-0.5 * ((TT - te) / sg_fix) ** 2) / \
                    (sg_fix * np.sqrt(2 * np.pi))
            mn, mstar = binned_dens(
                dens, target_density(pts, inside, u))
            l1s.append(np.abs(mn - mstar).sum() / np.abs(mstar).sum())
        joint_rows.append({"n": n, "h": 2.0 / (n - 1), "sigma": sg_fix,
                           "L1_mean": float(np.mean(l1s))})
        print(f"[V2c] n={n:4d} sigma={sg_fix} L1={np.mean(l1s):.4f}")

    # figure
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
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0),
                             constrained_layout=True)
    ax = axes[0]
    ax.loglog([r["h"] for r in rows], [r["L1_med"] for r in rows],
              "o-", color="#1f4e79", label="binned L1 (median of cuts)")
    ax.loglog(hs, 0.9 * hs ** alpha_rate, "--", color="#c00000",
              label=f"fit $h^{{\\alpha}}$, $\\alpha$={alpha_rate:.2f}")
    ax.set_xlabel("constraint/tangency mesh $h$")
    ax.set_ylabel("L1 distance to smooth curvature density")
    ax.set_title("(a) refinement: $\\mu_n \\Rightarrow u^\\top H_f u$")
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.semilogx([r["sigma"] for r in sig_rows],
                [r["L1_to_smooth"] for r in sig_rows], "o-",
                color="#c00000", label="$\\|$ smoothed $-$ smooth$\\|_1$")
    ax.semilogx([r["sigma"] for r in sig_rows],
                [r["mass_frac_near_atoms_w0.04"] for r in sig_rows],
                "s--", color="#1f4e79",
                label="mass frac near atoms (w=0.04)")
    ax.set_xlabel("$\\sigma$ (at fixed $n=32$)")
    ax.set_ylabel("value")
    ax.set_ylim(0, 1.05)
    ax.set_title("(b) $\\sigma\\!\\to\\!0$ at fixed $n$: atomic")
    ax.legend(fontsize=8, loc="center left")
    ax = axes[2]
    ax.semilogx([r["h"] for r in joint_rows],
                [r["L1_mean"] for r in joint_rows], "o-",
                color="#548235", label=f"$\\sigma$ fixed = {sg_fix}")
    ax.set_xlabel("mesh $h$ ($\\sigma \\gg h$)")
    ax.set_ylabel("L1 distance to smooth density")
    ax.set_title("(c) joint limit: smoothed refined $\\to$ smooth")
    ax.legend(fontsize=8)
    fig.suptitle("V2 - refinement prototype (parametric-LP value "
                 "functions, Routes 1+2 corrected)", fontsize=11)
    fig.savefig(os.path.join(OUT, "v2_refinement.png"), dpi=170)
    plt.close(fig)

    with open(os.path.join(OUT, "v2_refinement.csv"), "w",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "panel", "n", "h", "n_bins", "sigma", "L1_mean", "L1_med",
            "W1_mean", "W1_abs_mean", "mass_ratio", "L1_to_smooth",
            "mass_frac_near_atoms_w0.04"])
        w.writeheader()
        for r in rows:
            w.writerow({"panel": "a_refinement", **r})
        for r in sig_rows:
            w.writerow({"panel": "b_sigma_fixed_n", "n": n_fixed,
                        "h": 2.0 / (n_fixed - 1), **r})
        for r in joint_rows:
            w.writerow({"panel": "c_joint", **r})

    save_json({
        "experiment": "V2 refinement prototype (min-of-tangent-planes "
                      "parametric LP family; theta in RHS, fixed "
                      "constraint matrix, nested refinement)",
        "f": "2 - 0.5|theta|^2 - 0.1 sum theta_i^4 (concave, non-const "
             "curvature)",
        "refinement_limit": rows, "L1_rate_alpha": alpha_rate,
        "sigma_limit_fixed_n": sig_rows, "n_fixed": n_fixed,
        "joint_limit_fixed_sigma": joint_rows,
        "verdict": {
            "refinement": "atomic measures converge weakly to the smooth "
                          "curvature density (L1 ~ h^alpha, alpha = "
                          f"{alpha_rate:.2f})",
            "sigma_to_0": "at fixed n the sigma->0 limit is the ATOMIC "
                          "measure (the audit's limit direction)",
            "joint": "at fixed sigma >> h the smoothed refined object "
                     "converges to the smooth density (corrected "
                     "theorem)"}},
        "v2_refinement.json")
    return {"alpha": alpha_rate, "rows": rows, "sig": sig_rows,
            "joint": joint_rows}


# =====================================================================
# V3 -- sigma->0 inversion on the MEASURED real-network measure
# =====================================================================
def run_v3():
    ev = np.genfromtxt(
        os.path.join(BASE, "download", "m4", "m4c_cut_events.csv"),
        delimiter=",", names=True)
    t_events = np.atleast_1d(ev["t_event"])
    jnorm = np.atleast_1d(ev["jump_L2"])
    total_mass = jnorm.sum()

    tt = np.linspace(-0.2, 0.2, 8001)
    sigmas = [0.1, 0.03, 0.01, 0.003, 0.001, 3e-4, 1e-4]
    w_fixed = 0.01                     # fixed neighborhood half-width

    t0_wallfree = -0.05                # clearance ~0.052 from events
    rows = []
    hats = []
    for sg in sigmas:
        dens = np.zeros_like(tt)
        for te, jn in zip(t_events, jnorm):
            dens += jn * np.exp(-0.5 * ((tt - te) / sg) ** 2) / \
                (sg * np.sqrt(2 * np.pi))
        # (a) mass fraction within fixed w of the event set
        near = np.zeros_like(tt, bool)
        for te in t_events:
            near |= np.abs(tt - te) <= w_fixed
        frac = dens[near].sum() / dens.sum()
        # (b) density at wall-free point / peak
        peak = dens.max()
        val_free = np.interp(t0_wallfree, tt, dens)
        # (c) hat test on the largest atom vs the smoothest family
        # member (sigma=0.3 proxy)
        i_max = int(np.argmax(jnorm))
        psi = np.exp(-0.5 * ((tt - t_events[i_max]) / 0.02) ** 2)
        psi /= psi.max()
        integ = np.trapezoid(psi * dens, tt)
        rows.append({"sigma": sg,
                     "mass_frac_near_events_w0.01": float(frac),
                     "density_at_wallfree_over_peak":
                         float(val_free / peak),
                     "hat_test_on_max_atom": float(integ),
                     "max_atom_mass": float(jnorm[i_max])})
    # smooth proxy: the sigma=0.3 family member (the "smoothest" honest
    # candidate with the same total mass)
    sg_proxy = 0.3
    dens_proxy = np.zeros_like(tt)
    for te, jn in zip(t_events, jnorm):
        dens_proxy += jn * np.exp(-0.5 * ((tt - te) / sg_proxy) ** 2) / \
            (sg_proxy * np.sqrt(2 * np.pi))
    psi = np.exp(-0.5 * ((tt - t_events[i_max]) / 0.02) ** 2)
    psi /= psi.max()
    hat_proxy = float(np.trapezoid(psi * dens_proxy, tt))

    # weak-limit tests: fixed Lipschitz bumps at events vs between
    bump_tests = []
    for te, jn in zip(t_events[:6], jnorm[:6]):
        psi = np.exp(-0.5 * ((tt - te) / 0.02) ** 2)
        psi /= psi.max()               # |psi|<=1, Lip <= 1/0.02*...
        row = {"t_event": float(te), "atom_mass": float(jn)}
        for sg in (0.03, 0.003, 3e-4):
            dens = np.zeros_like(tt)
            for te2, jn2 in zip(t_events, jnorm):
                dens += jn2 * np.exp(-0.5 * ((tt - te2) / sg) ** 2) / \
                    (sg * np.sqrt(2 * np.pi))
            row[f"int_psi_dmu_sigma_{sg}"] = float(
                np.trapezoid(psi * dens, tt))
        row["int_psi_dmu_atomic"] = float(jn)
        row["int_psi_dsmooth_proxy"] = float(
            np.trapezoid(psi * dens_proxy, tt))
        bump_tests.append(row)

    # figure
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
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.0),
                             constrained_layout=True)
    ax = axes[0]
    for sg in (0.1, 0.03, 0.01, 0.003, 3e-4):
        dens = np.zeros_like(tt)
        for te, jn in zip(t_events, jnorm):
            dens += jn * np.exp(-0.5 * ((tt - te) / sg) ** 2) / \
                (sg * np.sqrt(2 * np.pi))
        ax.semilogy(tt, np.maximum(dens, 1e-12), lw=1.2,
                    label=f"$\\sigma$={sg}")
    for te in t_events:
        ax.axvline(te, color="k", lw=0.5, alpha=0.35)
    ax.set_yscale("log")
    ax.set_xlabel("t along M4c cut")
    ax.set_ylabel(r"$\kappa_\sigma(t)=\sum_e\|\Delta_e\|\,\varphi_\sigma$")
    ax.set_title("(a) the family sharpens onto the 12 atoms")
    ax.legend(fontsize=7)
    ax = axes[1]
    ax.semilogx([r["sigma"] for r in rows],
                [r["mass_frac_near_events_w0.01"] for r in rows],
                "o-", color="#1f4e79")
    ax.set_xlabel("$\\sigma$")
    ax.set_ylabel(f"mass fraction within w={w_fixed} of events")
    ax.set_ylim(0, 1.02)
    ax.set_title("(b) mass collapses onto the event set")
    ax = axes[2]
    ax.loglog([r["sigma"] for r in rows],
              np.maximum([r["density_at_wallfree_over_peak"]
                          for r in rows], 1e-16), "o-", color="#c00000")
    ax.set_xlabel("$\\sigma$")
    ax.set_ylabel(r"$\kappa_\sigma(t_0)/\kappa_\sigma^{peak}$"
                  r"  ($t_0$ wall-free)")
    ax.set_title("(c) wall-free density vanishes (exp in $1/\sigma$)")
    fig.suptitle("V3 - the audit's $\\sigma\\!\\to\\!0$ limit picks the "
                 "ATOMIC measure (measured M4c event set)", fontsize=11)
    fig.savefig(os.path.join(OUT, "v3_sigma_limit.png"), dpi=170)
    plt.close(fig)

    with open(os.path.join(OUT, "v3_sigma_limit.csv"), "w",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    frac_last = rows[-1]["mass_frac_near_events_w0.01"]
    free_last = rows[-1]["density_at_wallfree_over_peak"]
    save_json({
        "experiment": "V3 sigma->0 limit direction on the measured "
                      "M4c event measure",
        "events": {"n": int(len(t_events)), "total_L2_mass":
                   float(total_mass)},
        "sigma_ladder": rows,
        "hat_test_on_max_atom_vs_smooth_proxy": {
            "atom_mass": float(jnorm[i_max]),
            "sigma_0.003": rows[3]["hat_test_on_max_atom"],
            "sigma_3e-4": rows[5]["hat_test_on_max_atom"],
            "smooth_proxy_sigma0.3": hat_proxy},
        "bump_tests": bump_tests,
        "verdict": {
            "weak_limit": f"as sigma->0 the family converges weakly to "
                          f"the ATOMIC measure (mass near events "
                          f"{frac_last:.3f} at fixed w; wall-free "
                          f"density/peak {free_last:.1e})",
            "audit_formula": "kappa_geom = lim_{sigma->0} kappa_flux*"
                             "phi_sigma therefore selects the atomic "
                             "object = Theorem N's obstruction, NOT a "
                             "smooth density; the defensible statement "
                             "is the fixed-sigma resolution statement "
                             "(Theorem R / M4c)"}},
        "v3_sigma_limit.json")
    print(f"[V3] final sigma: near-event mass {frac_last:.4f}, "
          f"wall-free/peak {free_last:.2e}")
    print(f"[V3] hat test: atom {jnorm[i_max]:.1f} | sigma=3e-4 "
          f"{rows[5]['hat_test_on_max_atom']:.1f} | smooth proxy "
          f"{hat_proxy:.1f}")
    return rows


if __name__ == "__main__":
    print("=" * 70)
    v1 = run_v1()
    print("-" * 70)
    v2 = run_v2()
    print("-" * 70)
    v3 = run_v3()
    print("=" * 70)
    print(f"total wall time {time.time() - t_start:.0f} s")
