#!/usr/bin/env python3
"""
M4c -- The regime dial: smoothing / coarse-graining crossover of the
second-difference scaling law on the FBA flux map.

Context.  The "root cause" analysis under evaluation states that the
smooth curvature bridge is falsified (M4a: dynamic commutator slope
1.00, not 2) and that the smooth geometric kappa_V must be treated as
"a conceptual ancestor or a separate regime, not the limit object".
The Active-Set Bridge v2 (Theorem N) proved the pointwise eps->0 limit
is blocked (atomicity obstruction).  What neither record contains is
the MECHANISM and the LAW of the "separate regime": under what
conditions does the flux map look smooth with an eps^2 second-order
law, and when does it look discrete with an eps^1 law?

Theorem R (verified here).  Let v(t) be the 1D restriction of the
lex-pFBA flux map along a line in the (glc, O2) plane (a continuous
piecewise-affine function with slope jumps Delta_e at events t_e),
and let v_sigma = v * phi_sigma be its Gaussian mollification at scale
sigma (a model of finite measurement resolution, ensemble averaging
over expression noise, or explicit regularization).  Then:

  (i) [convolution identity]  v_sigma'' = (D^2 v) * phi_sigma
       = sum_e Delta_e phi_sigma(. - t_e)   exactly;
  (ii) [second difference]    D(eps, sigma) := v_sigma(t0+eps)
       - 2 v_sigma(t0) + v_sigma(t0-eps)
       = sum_e Delta_e K(t0 - t_e; eps, sigma),
       K(d; eps, sigma) = int_{-eps}^{eps} (eps - |u|) phi_sigma(d+u) du;
  (iii) [dial law]  for eps << sigma: D ~ eps^2 ||v_sigma''(t0)||
       (slope 2 -- the smooth/Riemannian regime);  for eps >> sigma:
       D -> sum_e Delta_e (eps - |t0 - t_e|)_+  (slope 1 -- the
       discrete/kink regime);  crossover at eps ~ sigma.

Predictions adjudicated by the data:
  slope(log D vs log eps) ~ 2 for eps <= sigma/3   -> smooth regime real
  slope ~ 1 for eps >= 3 sigma                     -> discrete regime
  crossover eps* ~ O(sigma)                        -> the dial
  D(eps, sigma) matches the analytic K-sum          -> Theorem R(i)
  wall-free base point: D ~ 0 (locality)            -> curvature is
                                                      carried by the
                                                      smeared walls

Design: 1D cut through the M4b codim-2 vertex theta0 = (1.692, 1.480)
along dB (the same locus where M4b found 11 events carrying 100% of
the D2 mass).  Event census by operational-signature bisection at
2e-5 resolution; slope jumps by per-segment least squares (the map is
exactly affine within chambers, M1 residuals <= 8e-14).  v_sigma by
5-point Gauss-Hermite quadrature (15 lex solves per triple).

Usage: python m4c_regime_dial.py
"""
import csv
import json
import os
import sys
import time
import warnings

import numpy as np
import cobra
from cobra.util.solver import linear_reaction_coefficients
from scipy.stats import norm as N01

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_engine import LPEngine

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "m4")
os.makedirs(OUT, exist_ok=True)

# ---- locus (M4b vertex, cell [2,3], defect -7.1469 deg) ----------------
THETA0 = np.array([1.6920021856564074, 1.4795937877603242])
DB = np.array([0.6473547604531503, -0.7621888310114787])
TOL_M, TOL_B = 1e-6, 1e-7
NOISE_FLOOR = 3e-7          # censored below (LP noise x sqrt(R))

# ---- grids ---------------------------------------------------------------
SPAN, N_CUT = 0.4, 161                       # dt = 0.005
SIGMAS = [0.003, 0.01, 0.03, 0.1]
def eps_grid(sigma):
    lo = max(4e-4, 0.03 * sigma)
    return np.logspace(np.log10(lo), np.log10(0.8), 12)
CTRL_SIGMA = 0.03
DENSITY_SIGMAS = [0.005, 0.02, 0.05]

# 5-point Gauss-Hermite (weight e^{-x^2}); sum(w) = sqrt(pi)
GH_X = np.array([-2.020182487018488, -0.9585724640867485, 0.0,
                 0.9585724640867485, 2.020182487018488])
GH_W = np.array([0.0199532420588448, 0.3936193231522412,
                 0.9453087204829419,
                 0.3936193231522412, 0.0199532420588448])
SQ2 = np.sqrt(2.0)


# ---------------------------------------------------------------- engine
def build():
    model = cobra.io.load_json_model(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    co = linear_reaction_coefficients(model)
    c_bio = np.zeros(len(model.reactions))
    for r, c in co.items():
        c_bio[model.reactions.index(r)] = c
    rng = np.random.default_rng(20240901)     # same tie-break weights as M1/M3/M4a/M4b
    W = rng.uniform(0.5, 1.5, len(model.reactions))
    eng = LPEngine(model, W, c_bio)
    bio_id = list(co.keys())[0].id
    return eng, eng.index[bio_id]


class Solver:
    """Cached lex-pFBA solves on the (glc, O2) plane (as M4b)."""

    def __init__(self, eng, bio_idx):
        self.eng = eng
        self.bi = bio_idx
        self.i_glc = eng.index["EX_glc__D_e"]
        self.i_o2 = eng.index["EX_o2_e"]
        self.cache = {}
        self.n_solves = 0

    def at(self, glc, o2):
        key = (round(float(glc), 12), round(float(o2), 12))
        if key not in self.cache:
            lb = self.eng.lb0.copy()
            ub = self.eng.ub0.copy()
            lb[self.i_glc] = -key[0]
            lb[self.i_o2] = -key[1]
            out = self.eng.solve_lex(lb, ub, self.bi)
            self.n_solves += 1
            if out is None:
                self.cache[key] = None
            else:
                self.cache[key] = out[0].copy()
        return self.cache[key]

    def at_t(self, t):
        p = THETA0 + t * DB
        return self.at(p[0], p[1])

    def sig_at_t(self, t):
        p = THETA0 + t * DB
        v = self.at(p[0], p[1])
        lb = self.eng.lb0.copy()
        ub = self.eng.ub0.copy()
        lb[self.i_glc] = -p[0]
        lb[self.i_o2] = -p[1]
        material = np.abs(v) >= TOL_M
        atb = (np.abs(v - lb) <= TOL_B) | (np.abs(v - ub) <= TOL_B)
        return hash((material.tobytes(), (material & atb).tobytes()))


# -------------------------------------------------------- analytic kernel
def K_closed(d, eps, sigma):
    """K(d) = int_{-eps}^{eps} (eps-|u|) phi_sigma(d+u) du, closed form."""
    phi = lambda s: N01.pdf(s, 0.0, sigma)
    Phi = lambda s: N01.cdf(s, 0.0, sigma)
    a, b, c = d - eps, d, d + eps
    # int_a^b (c0 + s) phi ds = c0 (Phi(b)-Phi(a)) - sigma^2 (phi(b)-phi(a))
    # int_b^c (c1 - s) phi ds = c1 (Phi(c)-Phi(b)) + sigma^2 (phi(c)-phi(b))
    t1 = (eps - d) * (Phi(b) - Phi(a)) - sigma ** 2 * (phi(b) - phi(a))
    t2 = (eps + d) * (Phi(c) - Phi(b)) + sigma ** 2 * (phi(c) - phi(b))
    return t1 + t2


def _selftest_K():
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(300):
        d = rng.uniform(-1, 1)
        eps = rng.uniform(1e-4, 1.0)
        sigma = rng.uniform(1e-3, 0.5)
        u = np.linspace(-eps, eps, 20001)
        quad = np.trapezoid((eps - np.abs(u)) * N01.pdf(d + u, 0, sigma), u)
        closed = K_closed(d, eps, sigma)
        if abs(quad) < 1e-6:
            continue          # deep tail: both ~0, quadrature-limited
        worst = max(worst, abs(quad - closed) / max(abs(quad), 1e-10))
    return worst


# ------------------------------------------------------------- event census
def refine_boundaries(sv, lo, hi, slo, shi, out, depth=0):
    """Collect ALL signature-change points in (lo, hi) by bisection.
    slo/shi: signatures at lo/hi. Handles sliver chambers (a mid sample
    matching neither side splits the interval recursively)."""
    if hi - lo < 1e-6 or depth > 40:
        out.append(0.5 * (lo + hi))
        return
    mid = 0.5 * (lo + hi)
    sm = sv.sig_at_t(mid)
    if sm == slo:
        refine_boundaries(sv, mid, hi, sm, shi, out, depth + 1)
    elif sm == shi:
        refine_boundaries(sv, lo, mid, slo, sm, out, depth + 1)
    else:                       # third (sliver) chamber inside
        refine_boundaries(sv, lo, mid, slo, sm, out, depth + 1)
        refine_boundaries(sv, mid, hi, sm, shi, out, depth + 1)


def cut_and_events(sv):
    ts = np.linspace(-SPAN, SPAN, N_CUT)
    vs = np.array([sv.at_t(t) for t in ts])
    if np.any(~np.isfinite(vs).all(axis=1)):
        raise RuntimeError("infeasible point on cut")
    sigs = [sv.sig_at_t(t) for t in ts]
    # refine every grid-step where the signature changes
    events = []
    for k in range(N_CUT - 1):
        if sigs[k] != sigs[k + 1]:
            refine_boundaries(sv, ts[k], ts[k + 1], sigs[k], sigs[k + 1],
                              events)
    events = np.array(sorted(events))
    # per-segment slopes from dedicated interior samples (the map is
    # exactly affine within a chamber; LSQ on 3-5 interior points)
    edges = np.concatenate([[-SPAN], events, [SPAN]])
    slopes = []
    for a, b in zip(edges[:-1], edges[1:]):
        w = b - a
        if w > 0.01:
            fr = [0.12, 0.3, 0.5, 0.7, 0.88]
        elif w > 0.002:
            fr = [0.25, 0.5, 0.75]
        else:
            fr = [0.3, 0.7]
        tt = np.array([a + f * w for f in fr])
        vv = np.array([sv.at_t(t) for t in tt])
        A = np.column_stack([tt, np.ones(len(tt))])
        coef, *_ = np.linalg.lstsq(A, vv, rcond=None)
        slopes.append(coef[0])          # (R,) vector slope
    jumps = np.array([slopes[j + 1] - slopes[j]
                      for j in range(len(slopes) - 1)])   # one per event
    telesc = slopes[-1] - slopes[0] - jumps.sum(axis=0)
    return ts, vs, events, slopes, jumps, telesc


# ------------------------------------------------------------- smoothed map
def v_sigma(sv, t, sigma):
    """v * phi_sigma at t via 5-point Gauss-Hermite (needs 5 lex solves)."""
    acc = np.zeros(sv.eng.R)
    for x, w in zip(GH_X, GH_W):
        vv = sv.at_t(t + SQ2 * sigma * x)
        if vv is None:
            return None
        acc += (w / np.sqrt(np.pi)) * vv
    return acc


def D_machine(sv, t0, eps, sigma):
    vp = v_sigma(sv, t0 + eps, sigma)
    v0 = v_sigma(sv, t0, sigma)
    vm = v_sigma(sv, t0 - eps, sigma)
    if vp is None or v0 is None or vm is None:
        return None
    return float(np.linalg.norm(vp - 2 * v0 + vm))


def D_analytic(events, jumps, t0, eps, sigma):
    acc = np.zeros(jumps.shape[1])
    for te, dj in zip(events, jumps):
        acc = acc + dj * K_closed(t0 - te, eps, sigma)
    return float(np.linalg.norm(acc))


# ------------------------------------------------------------------- plots
def make_fig_scaling(scal_rows, dial):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.2, 5.6), constrained_layout=True)
    colors = {0.003: "#1f77b4", 0.01: "#d62728", 0.03: "#2ca02c",
              0.1: "#9467bd"}
    for sig in SIGMAS:
        d = dial[sig]
        ed = np.array(d["eps_grid"])
        dd = np.array(d["D_grid"])
        ax.loglog(ed, dd, "-", lw=1.4, color=colors[sig],
                  label=f"exact convolution, sigma={sig}")
        rows = [r for r in scal_rows
                if r["sigma"] == sig and r["t_base"] == 0.0
                and r["D_machine"] and r["D_machine"] > NOISE_FLOOR]
        if rows:
            ep = np.array([r["eps"] for r in rows])
            dm = np.array([r["D_machine"] for r in rows])
            ax.loglog(ep, dm, "o", ms=4.5, color=colors[sig], mfc="none",
                      mec=colors[sig], label=f"machine (GH), sigma={sig}")
        ax.axvline(sig, ls=":", lw=0.9, color=colors[sig], alpha=0.5)
    # slope guides anchored to data range
    xr = np.array([0.0008, 0.006])
    ax.loglog(xr, 60 * (xr / 0.006) ** 2, "k:", lw=1.2, alpha=0.8)
    ax.text(0.0011, 60 * (0.0011 / 0.006) ** 2 * 1.6, "slope 2 (smooth)",
            fontsize=8.5, rotation=32, color="k", alpha=0.75)
    xr = np.array([0.12, 0.8])
    ax.loglog(xr, 0.28 * (xr / 0.12), "k:", lw=1.2, alpha=0.8)
    ax.text(0.25, 0.28 * (0.25 / 0.12) * 1.5, "slope 1 (discrete)",
            fontsize=8.5, rotation=15, color="k", alpha=0.75)
    txt = "\n".join(
        f"sigma={s}: slope(eps<s/3)="
        f"{d['slope_small'] if d['slope_small'] is not None else float('nan'):.3f}, "
        f"slope(eps>3s)={d['slope_large']:.3f}, "
        f"eps*={d['eps_star'] if d['eps_star'] is not None else float('nan'):.4g}"
        for s, d in dial.items())
    ax.text(0.02, 0.02, txt, transform=ax.transAxes, fontsize=7.6,
            va="bottom", ha="left", family="monospace",
            bbox=dict(fc="white", ec="0.6", alpha=0.85, boxstyle="round,pad=0.3"))
    ax.set_xlabel("perturbation step eps (log scale)")
    ax.set_ylabel(r"$\Vert v_\sigma(t_0+\epsilon)-2v_\sigma(t_0)+v_\sigma(t_0-\epsilon)\Vert_2$")
    ax.set_title("M4c regime dial: second-difference scaling vs smoothing scale\n"
                 "iML1515 (glc, O2) cut through the M4b codim-2 vertex "
                 "(dotted verticals: eps = sigma)")
    ax.legend(fontsize=6.8, ncol=2, loc="upper left")
    fig.savefig(os.path.join(OUT, "fig_m4c_scaling.png"), dpi=200)
    plt.close(fig)


def make_fig_density(events, jumps, jnorm, dens_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2),
                             constrained_layout=True)
    ts = np.linspace(-0.25, 0.25, 801)
    ax = axes[0]
    for sig in DENSITY_SIGMAS:
        acc = np.zeros((len(ts), jumps.shape[1]))
        for te, dj in zip(events, jumps):
            acc += np.outer(N01.pdf(ts - te, 0.0, sig), dj)
        kap = np.linalg.norm(acc, axis=1)
        ax.semilogy(ts, np.maximum(kap, 1e-16), lw=1.3,
                    label=f"sigma={sig}")
    for te, jn in zip(events, jnorm):
        if jn > 1e-6:
            ax.semilogy([te, te], [max(jn, 1e-12), max(jn, 1e-12)],
                        "k|", ms=6, alpha=0.45)
    ax.set_xlabel("t along cut (through vertex)")
    ax.set_ylabel(r"$\kappa_\sigma(t)=\Vert(v\sigma)''(t)\Vert_2$")
    ax.set_title("smeared curvature density = measure * gaussian\n"
                 "(stems: kink jumps Delta_e)")
    ax.legend(fontsize=7.5)
    ax = axes[1]
    for sig in SIGMAS:
        rows = [r for r in dens_rows if r["sigma"] == sig]
        ep = np.array([r["eps"] for r in rows])
        re = np.array([r["rel_err"] for r in rows])
        ax.semilogx(ep, re, "o-", ms=3.5, lw=1.0, label=f"sigma={sig}")
    ax.set_xlabel("perturbation step eps (log scale)")
    ax.set_ylabel("|machine - theory| / theory")
    ax.set_title("Theorem R convolution identity: machine vs analytic\n"
                 "(censored points excluded)")
    ax.legend(fontsize=7.5)
    ax.set_ylim(-0.05, 1.05)
    fig.savefig(os.path.join(OUT, "fig_m4c_density.png"), dpi=200)
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    t_start = time.time()
    k_err = _selftest_K()
    print(f"K closed-form self-test worst rel err (quad-limited tail "
          f"skipped): {k_err:.2e}")
    assert k_err < 5e-3

    eng, bio_idx = build()
    sv = Solver(eng, bio_idx)

    print("cut + event census ...")
    ts, vs, events, slopes, jumps, telesc = cut_and_events(sv)
    jnorm = np.linalg.norm(jumps, axis=1)
    print(f"  events: {len(events)}  kinked(|D|>1e-6): {(jnorm > 1e-6).sum()}"
          f"  max|Delta|: {jnorm.max():.3f}")
    print(f"  telescoping residual: {np.abs(telesc).max():.2e}")

    # wall-free control base: widest event-free gap in (0.05, 0.38)
    inner = [e for e in events if 0.05 < e < 0.38]
    pts = [0.05] + inner + [0.38]
    gaps = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    ga, gb = max(gaps, key=lambda g: g[1] - g[0])
    t_ctrl = 0.5 * (ga + gb)
    clearance = min(t_ctrl - ga, gb - t_ctrl)
    print(f"  control base t={t_ctrl:.3f} (clearance {clearance:.3f})")

    # ---------------- scaling law (machine GH + exact convolution)
    scal_rows, dens_rows = [], []
    slopes_tab = {}
    crossover = {}
    machine_recs = {}
    for sig in SIGMAS:
        eps_g = eps_grid(sig)
        dm0 = da0 = None
        rec = []
        for eps in eps_g:
            dm = D_machine(sv, 0.0, eps, sig)
            da = D_analytic(events, jumps, 0.0, eps, sig)
            rel = abs(dm - da) / max(da, 1e-300) if dm is not None else np.nan
            rec.append((eps, dm, da))
            scal_rows.append(dict(sigma=sig, eps=float(eps), t_base=0.0,
                                  D_machine=dm, D_analytic=da,
                                  rel_err=float(rel)))
            dens_rows.append(dict(sigma=sig, eps=float(eps),
                                  rel_err=float(rel) if dm and dm > NOISE_FLOOR
                                  else None))
            if dm0 is None and dm is not None and dm > NOISE_FLOOR:
                dm0, da0 = dm, da
        machine_recs[sig] = rec
        # slopes (machine, censored-aware)
        def fit(mask_key):
            xs = np.array([e for e, dm, da in rec
                           if mask_key(e) and dm and dm > NOISE_FLOOR])
            ys = np.array([dm for e, dm, da in rec
                           if mask_key(e) and dm and dm > NOISE_FLOOR])
            if len(xs) < 2:
                return None, 0
            return float(np.polyfit(np.log(xs), np.log(ys), 1)[0]), len(xs)
        s_small, n1 = fit(lambda e: e <= sig / 3.0)
        s_large, n2 = fit(lambda e: e >= 3.0 * sig)
        slopes_tab[sig] = (s_small, s_large)
        # density check at t0: D(eps_min)/eps_min^2 vs ||v_sigma''(t0)||
        if dm0 is not None:
            e_min = rec[0][0]
            kap0 = float(np.linalg.norm(
                sum(dj * N01.pdf(0.0 - te, 0.0, sig)
                    for te, dj in zip(events, jumps))))
            dens_rel = abs(dm0 / e_min ** 2 - kap0) / kap0 if kap0 > 0 else None
            print(f"  sigma={sig}: machine slope_small={s_small} (n={n1}) "
                  f"slope_large={s_large} (n={n2}) "
                  f"density-check rel={dens_rel if dens_rel is None else round(dens_rel, 4)}")
        else:
            print(f"  sigma={sig}: all censored")

    # ---------------- dense analytic dial (exact convolution, no LP cost)
    # NOTE: the 5-point GH machine object is itself piecewise affine in t
    # (kinks translated to nodes), so it cannot probe eps << node spacing
    # ~ sigma; the dial is therefore read from the EXACT convolution of
    # the machine-measured measure, and the GH points serve as an
    # independent validation of the identity wherever eps >= sigma/2.
    dial = {}
    for sig in SIGMAS:
        ed = np.logspace(np.log10(sig / 300.0), np.log10(0.8), 24)
        dd = np.array([D_analytic(events, jumps, 0.0, e, sig) for e in ed])
        good = dd > 0
        def fslope(mask):
            m = mask & good
            xs, ys = ed[m], dd[m]
            if xs.size < 2:
                return None
            return float(np.polyfit(np.log(xs), np.log(ys), 1)[0])
        s_sm = fslope(ed <= sig / 3.0)
        s_lg = fslope(ed >= 3.0 * sig)
        loc = np.diff(np.log(dd[good])) / np.diff(np.log(ed[good]))
        star = None
        for i in range(len(loc)):
            if loc[i] <= 1.5 and (i == 0 or loc[i - 1] > 1.5):
                eg = ed[good]
                star = float(np.sqrt(eg[i] * eg[i + 1]))
                break
        dial[sig] = dict(slope_small=s_sm, slope_large=s_lg,
                         eps_star=star,
                         eps_star_over_sigma=(star / sig if star else None),
                         eps_grid=[float(x) for x in ed],
                         D_grid=[float(x) for x in dd])
        ratio = f"{star / sig:.3f}" if star else "n/a"
        print(f"  EXACT dial sigma={sig}: slope_small={s_sm:.4f} "
              f"slope_large={s_lg:.4f} eps*={star} (eps*/sigma={ratio})")

    # ---------------- machine-vs-exact validation stats
    validation = {}
    for sig in SIGMAS:
        rels = [abs(dm - da) / da for e, dm, da in machine_recs[sig]
                if dm is not None and dm > NOISE_FLOOR and e >= 0.5 * sig
                and da > 0]
        validation[sig] = dict(
            n_valid=len(rels),
            median_rel=float(np.median(rels)) if rels else None,
            max_rel=float(np.max(rels)) if rels else None)
        print(f"  validation sigma={sig}: n={len(rels)} "
              f"median rel={validation[sig]['median_rel']}")

    # ---------------- sliver-cluster record (E31 structure)
    order = np.argsort(events)
    groups, cur = [], [order[0]]
    for a, b in zip(order[:-1], order[1:]):
        if events[b] - events[a] < 2e-3:
            cur.append(b)
        else:
            groups.append(cur)
            cur = [b]
    groups.append(cur)
    sliver = []
    for g in groups:
        if len(g) < 2:
            continue
        net = jumps[g].sum(axis=0)
        sliver.append(dict(
            t_center=float(np.mean(events[g])),
            n_events=len(g),
            width=float(events[g[-1]] - events[g[0]]),
            max_jump_L2=float(np.max(np.linalg.norm(jumps[g], axis=1))),
            net_jump_L2=float(np.linalg.norm(net))))
    print(f"  sliver clusters: {len(sliver)}")

    # ---------------- locality control
    ctrl = []
    for eps in np.logspace(np.log10(0.0008), np.log10(0.8), 10):
        dm = D_machine(sv, t_ctrl, eps, CTRL_SIGMA)
        da = D_analytic(events, jumps, t_ctrl, eps, CTRL_SIGMA)
        ctrl.append(dict(eps=float(eps), D_machine=dm, D_analytic=da))
    ctrl_max_below = max([c["D_machine"] for c in ctrl
                          if c["eps"] + 3 * CTRL_SIGMA < clearance] or [0])
    print(f"  control: max D below reach = {ctrl_max_below:.2e}")

    # ---------------- outputs
    with open(os.path.join(OUT, "m4c_cut_events.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_event", "jump_L2", "slope_left_L2", "slope_right_L2",
                    "kinked"])
        sl = np.linalg.norm(slopes, axis=1)
        for i, (te, dj) in enumerate(zip(events, jumps)):
            w.writerow([float(te), float(np.linalg.norm(dj)),
                        float(sl[i]), float(sl[i + 1]),
                        bool(np.linalg.norm(dj) > 1e-6)])
    with open(os.path.join(OUT, "m4c_scaling.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sigma", "eps", "t_base",
                                          "D_machine", "D_analytic", "rel_err"])
        w.writeheader()
        for r in scal_rows:
            w.writerow(r)

    summary = dict(
        experiment="M4c regime dial (smoothing crossover of the "
                   "second-difference scaling law)",
        model="iML1515",
        locus=dict(theta0=[float(THETA0[0]), float(THETA0[1])],
                   direction=[float(DB[0]), float(DB[1])],
                   span=SPAN, n_points=N_CUT),
        theorem_R=dict(
            statement="v_sigma'' = (D^2 v) * phi_sigma; D(eps,sigma) = "
                      "sum_e Delta_e K(t0-t_e; eps, sigma); slope 2 for "
                      "eps<<sigma, slope 1 for eps>>sigma, crossover "
                      "eps~sigma",
            kernel_selftest_rel_err=float(k_err)),
        event_census=dict(
            n_events=int(len(events)),
            n_kinked=int((jnorm > 1e-6).sum()),
            n_mask=int((jnorm <= 1e-6).sum()),
            max_jump_L2=float(jnorm.max()),
            telescoping_residual=float(np.abs(telesc).max())),
        dial_exact={str(s): {k: v for k, v in d.items()
                             if k not in ("eps_grid", "D_grid")}
                    for s, d in dial.items()},
        slopes_machine={str(s): dict(slope_small=v[0], slope_large=v[1])
                        for s, v in slopes_tab.items()},
        validation_machine_vs_exact={str(s): v for s, v in validation.items()},
        gh_resolution_finding=(
            "A fixed-node Gauss-Hermite evaluation of v_sigma is itself a "
            "piecewise-affine function of t (each node translates the kinks "
            "of v), so it cannot probe eps below the node spacing ~ sigma: "
            "the machine D vanishes exactly for eps below the distance from "
            "the base point to the nearest node-translated kink, while the "
            "exact convolution gives the eps^2 law. The regime dial is "
            "therefore read from the exact convolution of the "
            "machine-measured measure; the GH points validate the identity "
            "at eps >= sigma/2 (and also truncate Gaussian tails beyond "
            "~3sigma, which sets the control's machine floor). This is "
            "Theorem N's atomicity manifesting at the numerical level: "
            "discretized smoothing does not remove the atoms unless the "
            "kernel itself is resolved."),
        sliver_clusters=sliver,
        control=dict(t_ctrl=float(t_ctrl), clearance=float(clearance),
                     sigma=CTRL_SIGMA,
                     max_D_below_reach=float(ctrl_max_below),
                     note="machine values additionally truncated by GH "
                          "tail cutoff (~3 sigma); exact values in rows",
                     rows=ctrl),
        quadrature="5-point Gauss-Hermite per machine evaluation",
        n_lex_solves=int(sv.n_solves),
        runtime_s=round(time.time() - t_start, 1),
    )
    with open(os.path.join(OUT, "m4c_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    make_fig_scaling(scal_rows, dial)
    make_fig_density(events, jumps, jnorm,
                     [r for r in dens_rows if r["rel_err"] is not None])
    print(json.dumps({k: summary[k] for k in
                      ("event_census", "dial_exact", "validation_machine_vs_exact",
                       "sliver_clusters", "control")},
                     indent=2))
    print(f"done: {sv.n_solves} lex solves, {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
