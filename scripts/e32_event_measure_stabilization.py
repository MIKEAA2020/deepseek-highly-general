#!/usr/bin/env python3
"""
E32 -- event-measure stabilization (Glivenko-Cantelli-type).

The E32 proposal (bridge-strength audit, Route 5's statistical form of
Conjecture RA): "over random cuts/panels (the M4b grid, the M1 sweeps,
the E24 panel), do the empirical event point measures stabilize in
bounded-Lipschitz distance as the panel grows (Glivenko-Cantelli-type)?
This is Route 5's mean-field instinct made falsifiable with existing
data."

Design (three sources, one common question):

  Arm A (M4b two-parameter plane, iML1515, 34x34 signature census):
     random straight cuts through the (glc, O2) box; events = active-set
     (signature) changes along the cut.
       A1 (d=1): pooled event-location measure on the normalized cut
           coordinate s in [0,1], panel = number of cuts n;
           d_BL(mu_n, mu_pool) decay + split-half + permutation null
           (uniform locations, per-cut counts kept) + iid-GC asymptotic
           prediction.  The null-vs-measured gap quantifies the event
           CLUSTERING along cuts (dependence: effective sample size).
       A2 (d=2): pooled event locations in the normalized (glc, O2)
           box; exact W1 by transport LP (atoms capped by subsampling);
           rate vs the d=2 rate sqrt(log n / n).

  Arm B (M1 sweeps, 13 parameter families, plain-FBA 250/121-point
     trajectories): per-sweep flux-layer event point measure on the
     normalized sweep coordinate t in [0,1] (per-interval atoms
     mass = sum_r |D2 v_r| / dt, above the 1e-6 noise floor; per-sweep
     normalization -- each sweep contributes one mean-field measure);
     panel = number of sweeps k; bootstrap decay of
     d_BL(mu_k, mu_13) + split-half + null.  Value layer (growth kinks)
     as a secondary census.  HONEST scope: 13 sweeps is a small panel;
     the outcome is band-width-limited by construction.

  Arm C (E24, frozen V5/V6 protocol):
       C1 (gene panel, d=1): the per-gene kappa^mu distribution
           (424 nonzero of 433) as a point measure on the log10 kappa
           axis; random gene panels of size m; decay vs m + null +
           the del Barrio-Gine-Uzet asymptotic constant
           C = int sqrt(F(1-F)) dx computed from the population.
           Secondary: the association r(panel_m) stabilization with
           the Fisher SD 1/sqrt(m-3) (the V5 bootstrap CI is the m=433
           endpoint of this curve).
       C2 (trajectory, the L1-reconstruction regime of Theorem B'(iv)):
           re-run the declared TB0 lex engine once on the frozen
           57-point E24 trajectory; population event point measure =
           per-interval atoms (mass = sum_r |D2 v_r|/dt at interval
           midpoints, total 288.77); panel growth = random grid
           thinning:
             (a) uniform thinning (the naive statistical view; drops
                 design anchors -- expect structural non-stabilization
                 at small m: the honest finding),
             (b) anchor-preserving thinning (the designed-panel view;
                 8 physiology anchors always kept),
           measured: d_BL of the normalized measure + relative total
           mass error (the B'(iii) one-signed-regime TV statement).

Metric: all domains normalized to diameter < 2, so the bounded-
Lipschitz metric equals W1 (Kantorovich-Rubinstein); 1D W1 is exact
(CDF integral), 2D W1 by exact transport LP.

Outputs: download/deepseek_bridge/e32_event_measure_stabilization
         .{json,csv,png}.  Runtime ~4-6 min (one 57-solve lex run).
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
from scipy.sparse import csr_matrix

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")
DL = os.path.join(BASE, "download")
M1M3 = os.path.join(DL, "m1_m3")
M4 = os.path.join(DL, "m4")
os.makedirs(OUT, exist_ok=True)

t0 = time.time()
RNG = np.random.default_rng(20260902)
B_REPS = 200          # bootstrap reps for 1D curves
B_REPS_2D = 60        # reps for the LP-based 2D curve
N_CUT_POOL = 4000     # pre-generated random cuts (arm A)
N_CUT_SAMPLES = 800   # signature samples along each cut
ATOM_CAP_2D = 200     # max atoms per measure in the 2D LP


# ------------------------------------------------------------ W1 helpers
def w1_1d(xa, wa, xb, wb):
    """Exact W1 between two weighted atomic measures on the line.

    Atoms may repeat (pre-summed internally). Total masses must be
    equal up to tol (caller normalizes).
    """
    xa = np.asarray(xa, float); wa = np.asarray(wa, float)
    xb = np.asarray(xb, float); wb = np.asarray(wb, float)
    ia = np.argsort(xa); ib = np.argsort(xb)
    xa, wa = xa[ia], wa[ia]; xb, wb = xb[ib], wb[ib]
    if wa.sum() <= 0 or wb.sum() <= 0:
        return float("nan")
    wa = wa / wa.sum(); wb = wb / wb.sum()
    # merge CDFs
    xs = np.concatenate([xa, xb])
    order = np.concatenate([np.full(len(xa), 0), np.full(len(xb), 1)])
    vals = np.concatenate([wa, wb])
    o = np.argsort(xs, kind="mergesort")
    xs, side, vals = xs[o], order[o], vals[o]
    cdf_a = np.cumsum(np.where(side == 0, vals, 0.0))
    cdf_b = np.cumsum(np.where(side == 1, vals, 0.0))
    gap = np.abs(cdf_a - cdf_b)
    edges = np.concatenate([xs, [np.inf]])
    dx = np.diff(edges)
    # the interval beyond the last atom carries gap = 0 mathematically
    # (both CDFs = 1); force dx = 0 there to kill float-residue * inf
    dx[-1] = 0.0
    return float(np.sum(gap * dx))


def gc_constant_1d(x_pop, w_pop):
    """del Barrio-Gine-Uzet: sqrt(n) E[W1(nu_n, nu)] -> C, with
    C = int_R sqrt(F(t)(1-F(t))) dt  (population-level constant)."""
    x = np.asarray(x_pop, float); w = np.asarray(w_pop, float)
    o = np.argsort(x)
    x, w = x[o], w[o]
    w = w / w.sum()
    F = np.cumsum(w)                     # F right after each atom
    c = np.sqrt(np.maximum(F * (1.0 - F), 0.0))
    dx = np.diff(np.concatenate([[-np.inf], x, [np.inf]]))
    # only the intervals BETWEEN atoms carry the integrand
    dx_in = dx[1:-1]
    return float(np.sum(c[:-1] * dx_in))  # integrand uses F after atom i


def w1_2d_lp(A, wa, B, wb, cap=ATOM_CAP_2D, rng=None):
    """Exact W1 (transport LP, HiGHS) between two 2D atomic measures,
    subsampled to <= cap atoms when larger (unbiased for unweighted
    or equal-mass-normalized measures)."""
    rng = rng or np.random.default_rng(0)
    A = np.asarray(A, float); wa = np.asarray(wa, float)
    B = np.asarray(B, float); wb = np.asarray(wb, float)
    if wa.sum() <= 0 or wb.sum() <= 0:
        return float("nan")
    wa = wa / wa.sum(); wb = wb / wb.sum()
    if len(A) > cap:
        idx = rng.choice(len(A), cap, replace=False)
        A, wa = A[idx], wa[idx] / cap * len(A)
    if len(B) > cap:
        idx = rng.choice(len(B), cap, replace=False)
        B, wb = B[idx], wb[idx] / cap * len(B)
    n, m = len(A), len(B)
    if n == 0 or m == 0:
        return float("nan")
    D = np.sqrt(np.maximum(
        (A[:, None, 0] - B[None, :, 0]) ** 2 +
        (A[:, None, 1] - B[None, :, 1]) ** 2, 0.0))
    # vars: P[i, j] >= 0, row sums wa, col sums wb
    rows, cols, data = [], [], []
    for i in range(n):
        for j in range(m):
            rows.append(i); cols.append(i * m + j); data.append(1.0)
    for j in range(m):
        for i in range(n):
            rows.append(n + j); cols.append(i * m + j); data.append(1.0)
    A_eq = csr_matrix((data, (rows, cols)), shape=(n + m, n * m))
    b_eq = np.concatenate([wa, wb])
    res = linprog(D.ravel(), A_eq=A_eq, b_eq=b_eq, method="highs")
    return float(res.fun) if res.success else float("nan")


def decay_curve(sampler, pop, sizes, reps, pop_atoms=None):
    """mean/sd of d_BL(mu_n, pop) over bootstrap reps, per panel size."""
    out = []
    for n in sizes:
        vals = []
        for _ in range(reps):
            mu = sampler(n)
            vals.append(w1_1d(*mu, *pop))
        vals = np.array([v for v in vals if np.isfinite(v)])
        out.append((int(n), float(vals.mean()), float(vals.std())))
    return out


def loglog_slope(points):
    """tail slope of (n, y) in log-log, using the last 3 finite pts."""
    pts = [(n, y) for n, y in points if np.isfinite(y) and y > 0]
    if len(pts) < 3:
        return float("nan")
    pts = pts[-3:]
    x = np.log([p[0] for p in pts]); y = np.log([p[1] for p in pts])
    b = np.polyfit(x, y, 1)[0]
    return float(b)


results = {"experiment": "E32 event-measure stabilization "
            "(Glivenko-Cantelli type; Route 5 / Conjecture RA statistical form)",
           "metric": "bounded-Lipschitz = W1 (domains normalized to unit "
                     "diameter; 1D exact, 2D transport LP)",
           "sources": {}}
rows_csv = []   # (arm, subarm, n, mean_bl, sd_bl, null_mean, note)


# =================================================================
# ARM A -- M4b two-parameter plane, random cuts
# =================================================================
print("[E32] Arm A: M4b random cuts ...", flush=True)
d = np.load(os.path.join(M4, "m4b_grid.npz"), allow_pickle=True)
SIG = d["SIG"]
glc_ax, o2_ax = d["glc_ax"].astype(float), d["o2_ax"].astype(float)
ng, no = len(glc_ax), len(o2_ax)
# normalize the box to [0,1]^2 (glc -> x, o2 -> y); cell centers
gx = (np.arange(ng) + 0.5) / ng
gy = (np.arange(no) + 0.5) / no
BOX = (glc_ax.min(), glc_ax.max(), o2_ax.min(), o2_ax.max())


def box_to_unit(x, y):
    u = (x - BOX[0]) / (BOX[1] - BOX[0])
    v = (y - BOX[2]) / (BOX[3] - BOX[2])
    return u, v


def sig_at(u, v):
    """signature at unit coords (nearest cell)."""
    i = np.clip((u * ng).astype(int), 0, ng - 1)
    j = np.clip((v * no).astype(int), 0, no - 1)
    return SIG[i, j]


def gen_cut_events(rng):
    """One random straight cut: uniform anchor + angle, clipped to the
    unit box; sample N points; events at signature changes.
    Returns (s_positions, xy_positions)."""
    while True:
        a = rng.uniform(0.05, 0.95, 2)
        th = rng.uniform(0, np.pi)
        dvec = np.array([np.cos(th), np.sin(th)])
        # clip the line a + t*dvec to [0,1]^2
        ts = []
        for k in range(2):
            if abs(dvec[k]) > 1e-12:
                for bound in (0.0, 1.0):
                    t = (bound - a[k]) / dvec[k]
                    p = a + t * dvec
                    if -1e-12 <= p[0] <= 1 + 1e-12 and \
                       -1e-12 <= p[1] <= 1 + 1e-12:
                        ts.append(t)
        if len(ts) >= 2:
            break
    t_lo, t_hi = min(ts), max(ts)
    if t_hi - t_lo < 1e-3:
        return np.array([]), np.zeros((0, 2))
    s = np.linspace(t_lo, t_hi, N_CUT_SAMPLES)
    pts = a[None, :] + s[:, None] * dvec[None, :]
    u = np.clip(pts[:, 0], 0, 1 - 1e-9)
    v = np.clip(pts[:, 1], 0, 1 - 1e-9)
    sig = sig_at(u, v)
    chg = np.nonzero(sig[1:] != sig[:-1])[0]
    s_mid = 0.5 * (s[1:] + s[:-1])[chg]
    s_mid = (s_mid - t_lo) / (t_hi - t_lo)          # normalized coord
    xy = 0.5 * (pts[1:] + pts[:-1])[chg]
    return s_mid, xy


cut_rng = np.random.default_rng(20260902)
cut_s, cut_xy, cut_len = [], [], []
for _ in range(N_CUT_POOL):
    s_ev, xy_ev = gen_cut_events(cut_rng)
    cut_s.append(s_ev)
    cut_xy.append(xy_ev)
n_ev_per_cut = np.array([len(s) for s in cut_s])
all_s = np.concatenate(cut_s)
all_xy = np.concatenate(cut_xy)
print(f"[E32]   cut pool: {N_CUT_POOL} cuts, {len(all_s)} events "
      f"(mean {n_ev_per_cut.mean():.2f}/cut, max {n_ev_per_cut.max()})",
      flush=True)

# --- A1: pooled event-location measure on the cut coordinate (d=1)
pop_s = (all_s, np.ones(len(all_s)))
# null population: large iid uniform sample (the null decay curve must
# measure sampling noise against ITS OWN limit, not bias vs the real
# event distribution)
null_pop_s = (np.random.default_rng(20260903).uniform(0, 1, 25000),
              np.ones(25000))


def sample_cuts_1d(n, rng, null=False):
    idx = rng.choice(N_CUT_POOL, n, replace=False)
    if null:
        s = np.concatenate([rng.uniform(0, 1, n_ev_per_cut[i])
                            for i in idx])
    else:
        s = np.concatenate([cut_s[i] for i in idx])
    return (s, np.ones(len(s)))


a1_sizes = [2, 4, 8, 16, 32, 64, 128, 256]
a1 = decay_curve(lambda n: sample_cuts_1d(n, RNG), pop_s,
                 a1_sizes, B_REPS)
a1_null = decay_curve(lambda n: sample_cuts_1d(n, RNG, null=True),
                      null_pop_s, a1_sizes, B_REPS)
# iid-GC prediction with the pooled-atom count n * mean_events_per_cut
C_pop = gc_constant_1d(*pop_s)
a1_pred = [(n, C_pop / np.sqrt(n * n_ev_per_cut.mean()))
           for n in a1_sizes]
# split-half (two disjoint n/2 pools)
a1_split = []
for n in a1_sizes:
    vals = []
    for _ in range(B_REPS):
        idx = RNG.choice(N_CUT_POOL, n, replace=False)
        h1, h2 = idx[: n // 2], idx[n // 2:]
        s1 = np.concatenate([cut_s[i] for i in h1])
        s2 = np.concatenate([cut_s[i] for i in h2])
        vals.append(w1_1d(s1, np.ones(len(s1)), s2, np.ones(len(s2))))
    vals = np.array([v for v in vals if np.isfinite(v)])
    a1_split.append((n, float(vals.mean()), float(vals.std())))
for (n, m, s), (_, mn, _), (_, pn) in zip(a1, a1_null, a1_pred):
    rows_csv.append(("A1_cuts_d1", "one_sample", n, m, s, mn,
                     f"iid_gc_pred={pn:.5f}"))
for n, m, s in a1_split:
    rows_csv.append(("A1_cuts_d1", "split_half", n, m, s, np.nan,
                     "two disjoint n/2 pools"))
results["sources"]["A_m4b_random_cuts"] = {
    "plane": "iML1515 (glc, O2) 34x34 signature census",
    "n_boundary_edges_full_grid": int((np.diff(SIG, axis=0) != 0).sum() +
                                      (np.diff(SIG, axis=1) != 0).sum()),
    "cut_pool": N_CUT_POOL,
    "events_total": int(len(all_s)),
    "events_per_cut_mean": float(n_ev_per_cut.mean()),
    "events_per_cut_max": int(n_ev_per_cut.max()),
    "A1_d1": {"sizes": a1_sizes, "bl_mean": [m for _, m, _ in a1],
              "bl_sd": [s for _, _, s in a1],
              "null_mean": [m for _, m, _ in a1_null],
              "iid_gc_pred": [p for _, p in a1_pred],
              "gc_constant_pop": C_pop,
              "split_half": a1_split,
              "loglog_tail_slope": loglog_slope(
                  [(n, m) for n, m, _ in a1]),
              "null_loglog_tail_slope": loglog_slope(
                  [(n, m) for n, m, _ in a1_null]),
              "null_ratio_at_max_n": float(
                  a1[-1][1] / a1_null[-1][1])},
}

# --- A2: pooled event locations in the 2D box (d=2, transport LP)
# null reference: 400 iid uniform atoms (both sides capped by the LP
# atom cap; the reference's own noise sets the large-n floor)
null_ref_xy = np.random.default_rng(20260905).uniform(
    0, 1, (400, 2))
a2_sizes = [4, 16, 64, 256]
a2, a2_null = [], []
for n in a2_sizes:
    vm, vs, vmn = [], [], []
    for rep in range(B_REPS_2D):
        idx = RNG.choice(N_CUT_POOL, n, replace=False)
        xy = np.concatenate([cut_xy[i] for i in idx])
        if rep < B_REPS_2D // 2:
            vm.append(w1_2d_lp(xy, np.ones(len(xy)), all_xy,
                               np.ones(len(all_xy)), rng=RNG))
            xyn = RNG.uniform(0, 1, (len(xy), 2))
            vmn.append(w1_2d_lp(xyn, np.ones(len(xyn)), null_ref_xy,
                                np.ones(400), rng=RNG))
        else:
            xy2 = np.concatenate(
                [cut_xy[i] for i in RNG.choice(N_CUT_POOL, n,
                                                replace=False)])
            vs.append(w1_2d_lp(xy, np.ones(len(xy)), xy2,
                               np.ones(len(xy2)), rng=RNG))
    vm = np.array([v for v in vm if np.isfinite(v)])
    vmn = np.array([v for v in vmn if np.isfinite(v)])
    vs = np.array([v for v in vs if np.isfinite(v)])
    a2.append((n, float(vm.mean()), float(vm.std())))
    a2_null.append((n, float(vmn.mean()), float(vmn.std())))
    rows_csv.append(("A2_cuts_d2_LP", "one_sample", n, vm.mean(),
                     vm.std(), vmn.mean(), "half reps; split-half sd "
                     + f"{vs.mean():.5f}"))
results["sources"]["A_m4b_random_cuts"]["A2_d2"] = {
    "sizes": a2_sizes, "bl_mean": [m for _, m, _ in a2],
    "bl_sd": [s for _, _, s in a2],
    "null_mean": [m for _, m, _ in a2_null],
    "reference_rate": "sqrt(log n / n) (d=2)",
}
_a1r = results["sources"]["A_m4b_random_cuts"]["A1_d1"]
print(f"[E32]   A1 tail slope {_a1r['loglog_tail_slope']:.3f} vs null "
      f"{_a1r['null_loglog_tail_slope']:.3f}; "
      f"null ratio at max n {_a1r['null_ratio_at_max_n']:.2f}",
      flush=True)


# =================================================================
# ARM B -- M1 sweeps (13 parameter families), sweep panels
# =================================================================
print("[E32] Arm B: M1 sweep panels ...", flush=True)
sweep_files = sorted([f for f in os.listdir(M1M3)
                      if f.startswith("m1_") and f.endswith(".npz")])
sweep_names, sweep_measures, sweep_counts = [], [], []
for f in sweep_files:
    dd = np.load(os.path.join(M1M3, f), allow_pickle=True)
    V, g, t = dd["V"], dd["growth"], dd["t"]
    name = f[3:-4]
    tt = (t - t[0]) / (t[-1] - t[0])
    # canonical 1D atom of Definition def:mu: the PWL slope jump at
    # each interior node, mass = sum_r |s_right - s_left|  (exact for
    # any spacing; on uniform grids equals |D2 v|/dt)
    dif = np.diff(tt)
    sL = (V[1:-1] - V[:-2]) / dif[:-1, None]
    sR = (V[2:] - V[1:-1]) / dif[1:, None]
    mass = np.abs(sR - sL).sum(1)
    keep = mass > 1e-6
    pos = tt[1:-1][keep]
    w = mass[keep]
    if w.sum() > 0:
        w = w / w.sum()
    sweep_names.append(name)
    sweep_measures.append((pos, w))
    # value layer: growth kink census (same node slope-jump rule)
    gL = (g[1:-1] - g[:-2]) / dif[:-1]
    gR = (g[2:] - g[1:-1]) / dif[1:]
    gmass = np.abs(gR - gL)
    sweep_counts.append({"flux_events": int(keep.sum()),
                         "flux_mass": float(mass[keep].sum()),
                         "growth_kinks": int((gmass > 1e-6).sum())})
n_sweeps = len(sweep_names)
print("[E32]   " + "; ".join(
    f"{n}:{c['flux_events']}/{c['growth_kinks']}"
    for n, c in zip(sweep_names, sweep_counts)), flush=True)

# population: mean of per-sweep normalized measures (mean-field pool)
grid_t = np.linspace(0, 1, 2001)
def pool_measure(idxs):
    """mean measure over sweeps idxs, on the common grid (histogram
    atoms at grid midpoints, mass 0 sweeps contribute nothing)."""
    acc = np.zeros(len(grid_t) - 1)
    for i in idxs:
        pos, w = sweep_measures[i]
        if len(pos) == 0:
            continue
        h, _ = np.histogram(pos, bins=grid_t, weights=w)
        acc += h / max(len(idxs), 1)
    centers = 0.5 * (grid_t[1:] + grid_t[:-1])
    keep = acc > 0
    return centers[keep], acc[keep]

popB = pool_measure(range(n_sweeps))
b_sizes = [1, 2, 3, 4, 6, 8, 10, 12]
b_curve, b_null = [], []
for k in b_sizes:
    vm, vn = [], []
    nrep = B_REPS * 2
    for _ in range(nrep):
        # without-replacement subsets for all k <= 12 (the k=13 full
        # panel is the population; sampling mode must not switch
        # mid-curve)
        idxs = RNG.choice(n_sweeps, k, replace=False)
        mu = pool_measure(idxs)
        vm.append(w1_1d(*mu, *popB))
        # null: uniform atoms, same atom counts
        nulls = []
        for i in idxs:
            n0 = sweep_counts[i]["flux_events"]
            if n0 > 0:
                nulls.append((RNG.uniform(0, 1, n0),
                              np.ones(n0) / n0))
        accn = np.zeros(len(grid_t) - 1)
        for pos, w in nulls:
            h, _ = np.histogram(pos, bins=grid_t, weights=w)
            accn += h / len(idxs)
        keep = accn > 0
        cn = 0.5 * (grid_t[1:] + grid_t[:-1])
        u_ref = np.linspace(0, 1, 5001)[1:-1]
        vn.append(w1_1d(cn[keep], accn[keep],
                        u_ref, np.ones(len(u_ref)) / len(u_ref)))
    vm = np.array([v for v in vm if np.isfinite(v)])
    vn = np.array([v for v in vn if np.isfinite(v)])
    b_curve.append((k, float(vm.mean()), float(vm.std())))
    b_null.append((k, float(vn.mean()), float(vn.std())))
    rows_csv.append(("B_sweep_panels_d1", "bootstrap_vs_full13", k,
                     vm.mean(), vm.std(), vn.mean(),
                     "panel-limited: 13 sweeps total"))
results["sources"]["B_m1_sweep_panels"] = {
    "sweeps": {n: c for n, c in zip(sweep_names, sweep_counts)},
    "noise_floor": 1e-6,
    "population_atoms": int(len(popB[0])),
    "curve": {"sizes": b_sizes, "bl_mean": [m for _, m, _ in b_curve],
              "bl_sd": [s for _, _, s in b_curve],
              "null_mean": [m for _, m, _ in b_null]},
    "loglog_tail_slope": loglog_slope([(k, m) for k, m, _ in b_curve]),
    "null_loglog_tail_slope": loglog_slope(
        [(k, m) for k, m, _ in b_null]),
    "note": "k = 13 (the population itself) is excluded from the "
            "curve; subsets are without replacement",
}


# =================================================================
# ARM C1 -- E24 gene panel (kappa distribution + association)
# =================================================================
print("[E32] Arm C1: E24 gene panel ...", flush=True)
v5 = pd.read_csv(os.path.join(DL, "deepseek_bridge",
                              "v5_e24_recalibration.csv"))
kappa = v5["kappa_mu_max"].values
gene_ids = v5["gene_bnumber"].values
nz = kappa > 0
logk = np.log10(kappa[nz])
popC = (logk, np.ones(len(logk)))
C_popC = gc_constant_1d(*popC)
c1_sizes = [8, 16, 32, 64, 128, 256, 424]
c1_curve, c1_null, c1_pred = [], [], []
# null population: large uniform sample on the same support
u_lo, u_hi = float(logk.min()), float(logk.max())
null_ref_c1 = np.random.default_rng(20260904).uniform(
    u_lo, u_hi, 20000)
for m in c1_sizes:
    vm, vn = [], []
    for _ in range(B_REPS if m < 424 else 1):
        idx = RNG.choice(len(logk), m, replace=(m > len(logk) // 2))
        if m == 424:
            idx = np.arange(len(logk))
        vm.append(w1_1d(logk[idx], np.ones(m), *popC))
        vn.append(w1_1d(RNG.uniform(u_lo, u_hi, m), np.ones(m),
                        null_ref_c1, np.ones(20000)))
    vm = np.array(vm); vn = np.array(vn)
    c1_curve.append((m, float(vm.mean()), float(vm.std())))
    c1_null.append((m, float(vn.mean()), float(vn.std())))
    c1_pred.append((m, C_popC / np.sqrt(m)))
    rows_csv.append(("C1_gene_panel_d1", "log10_kappa_dist", m,
                     vm.mean(), vm.std(), vn.mean(),
                     f"bgu_asymptotic={C_popC / np.sqrt(m):.5f}"))

# association stabilization: r(panel_m) vs full r=+0.3954
e24p = pd.read_csv(os.path.join(DL, "novelty_v17_option_a_e24.csv"))
e24p = e24p.set_index("gene_bnumber")
stat_cols = [c for c in e24p.columns
             if c.startswith("fc_m3d_stationary")]
y_map = e24p[stat_cols].abs().max(axis=1)
y_all = np.array([y_map.get(g, np.nan) for g in gene_ids])
ok = nz & np.isfinite(y_all) & (y_all > 0)
# V5/V8 convention: pearson(log10 kappa, y_all) on the nonzero panel
r_full = stats.pearsonr(np.log10(kappa[ok]), y_all[ok])[0]
print(f"[E32]   C1 r_full check: {r_full:.4f} (V5 reference +0.3954)",
      flush=True)
c1_r = []
for m in c1_sizes:
    if m > ok.sum():
        continue
    rs = []
    for _ in range(B_REPS if m < ok.sum() else 1):
        idx = RNG.choice(np.nonzero(ok)[0], m,
                         replace=(m > ok.sum() // 2))
        rs.append(stats.pearsonr(np.log10(kappa[idx]),
                                 y_all[idx])[0])
    rs = np.array(rs)
    c1_r.append((m, float(rs.mean()), float(rs.std()),
                 1.0 / np.sqrt(max(m - 3, 1))))
    rows_csv.append(("C1_gene_panel_assoc", "r_stabilization", m,
                     rs.mean(), rs.std(), np.nan,
                     f"fisher_sd_pred={1 / np.sqrt(max(m - 3, 1)):.5f}"))
results["sources"]["C1_e24_gene_panel"] = {
    "n_genes_total": int(len(kappa)),
    "n_nonzero": int(nz.sum()),
    "axis": "log10(kappa_mu)",
    "gc_constant_pop": C_popC,
    "curve": {"sizes": c1_sizes, "bl_mean": [m for _, m, _ in c1_curve],
              "bl_sd": [s for _, _, s in c1_curve],
              "null_mean": [m for _, m, _ in c1_null],
              "bgu_asymptotic": [p for _, p in c1_pred]},
    "association": {"r_full_nonzero": float(r_full),
                    "r_curve": c1_r,
                    "note": "Fisher SD 1/sqrt(m-3) is the classical "
                            "GC-rate prediction for r"},
}


# =================================================================
# ARM C2 -- E24 trajectory (L1-reconstruction regime of Thm B'(iv))
# =================================================================
print("[E32] Arm C2: E24 trajectory (one TB0 engine run) ...",
      flush=True)
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
rng0 = np.random.default_rng(20240901)
W0 = rng0.uniform(0.5, 1.5, len(model.reactions))
eng = LPEngine(model, W0, c_bio)
bi = eng.index[list(co.keys())[0].id]
i_glc, i_o2 = eng.index["EX_glc__D_e"], eng.index["EX_o2_e"]

q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_o2 = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]
REFINE = 8
T = []
for k in range(7):
    for j in range(REFINE):
        f = j / REFINE
        T.append((q_glc[k] + f * (q_glc[k + 1] - q_glc[k]),
                  q_o2[k] + f * (q_o2[k + 1] - q_o2[k])))
T.append((q_glc[-1], q_o2[-1]))
npts = len(T)
Vs, mus = [], []
for g, o in T:
    lb, ub = eng.lb0.copy(), eng.ub0.copy()
    lb[i_glc] = -g
    lb[i_o2] = -o
    v, mu, s2 = eng.solve_lex(lb, ub, bi)
    Vs.append(v); mus.append(mu)
Vs = np.array(Vs); mus = np.array(mus)
tt = np.linspace(0, 1, npts)
print(f"[E32]   engine done ({time.time() - t0:.0f}s); "
      f"total D2 mass check", flush=True)


def traj_measure(Vs_sub, tt_sub):
    """Canonical 1D atoms: PWL slope jumps at interior nodes,
    mass = sum_r |s_right - s_left|  (exact for ANY grid spacing;
    on the uniform full grid equals the V5 per-interval |D2|/dt)."""
    N = len(tt_sub)
    if N < 3:
        return np.array([]), np.array([])
    dif = np.diff(tt_sub)
    sL = (Vs_sub[1:-1] - Vs_sub[:-2]) / dif[:-1, None]
    sR = (Vs_sub[2:] - Vs_sub[1:-1]) / dif[1:, None]
    mass = np.abs(sR - sL).sum(1)
    keep = mass > 1e-6
    pos = tt_sub[1:-1][keep]
    return pos, mass[keep]


pop_pos, pop_mass = traj_measure(Vs, tt)
pop_total = pop_mass.sum()
print(f"[E32]   C2 population: {len(pop_pos)} atoms, total mass "
      f"{pop_total:.4f} (V5 8x reference 288.7689)", flush=True)
popC2 = (pop_pos, pop_mass / pop_total)
anchor_idx = set(range(0, npts, REFINE)) | {npts - 1}
c2_sizes = [6, 8, 12, 16, 20, 29, 43, 57]


def thin(m, keep_anchors, rng):
    if keep_anchors:
        inter = [i for i in range(npts) if i not in anchor_idx]
        n_extra = max(m - len(anchor_idx), 0)
        extra = rng.choice(inter, min(n_extra, len(inter)),
                           replace=False)
        idx = sorted(anchor_idx | set(int(e) for e in extra))
    else:
        idx = sorted(rng.choice(npts, m, replace=False))
    idx = np.array(idx)
    return idx


c2a, c2b, c2a_mass, c2b_mass, c2a_vk, c2b_vk = [], [], [], [], [], []
for m in c2_sizes:
    for keep_a, curve, massc, vk in ((False, c2a, c2a_mass, c2a_vk),
                                      (True, c2b, c2b_mass, c2b_vk)):
        vals, tmass, vks = [], [], []
        for _ in range(B_REPS if m < npts else 1):
            idx = thin(m, keep_a, RNG)
            pos, mass = traj_measure(Vs[idx], tt[idx])
            if len(pos) == 0 or mass.sum() <= 0:
                vals.append(np.nan); tmass.append(np.nan)
                vks.append(0); continue
            vals.append(w1_1d(pos, mass / mass.sum(), *popC2))
            tmass.append(abs(mass.sum() - pop_total) / pop_total)
            # value-layer kink census on the thinned grid (node
            # slope-jump rule, spacing-robust)
            dif = np.diff(tt[idx])
            gL = (mus[idx][1:-1] - mus[idx][:-2]) / dif[:-1]
            gR = (mus[idx][2:] - mus[idx][1:-1]) / dif[1:]
            gm = np.abs(gR - gL)
            vks.append(int((gm > 1e-6).sum()))
        vals = np.array([v for v in vals if np.isfinite(v)])
        tm = np.array([v for v in tmass if np.isfinite(v)])
        curve.append((int(len(idx)), float(vals.mean()), float(vals.std())))
        massc.append((int(len(idx)), float(tm.mean()), float(tm.std())))
        vk.append((int(len(idx)), float(np.mean(vks))))
for (m, mm, ss), (_, tm, _), (_, vk) in zip(c2a, c2a_mass, c2a_vk):
    rows_csv.append(("C2_traj_thin_uniform", "bl_shape", m, mm, ss,
                     np.nan, f"rel_mass_err={tm:.4f} valkinks={vk:.1f}"))
for (m, mm, ss), (_, tm, _), (_, vk) in zip(c2b, c2b_mass, c2b_vk):
    rows_csv.append(("C2_traj_thin_anchor", "bl_shape", m, mm, ss,
                     np.nan, f"rel_mass_err={tm:.4f} valkinks={vk:.1f}"))
# null: m uniform atoms vs the 55-atom uniform reference (pure
# sampling decay; the measured curve adds resolution/censoring)
u_ref55 = np.linspace(0.02, 0.98, 55)
c2_null = []
for m in c2_sizes:
    vals = []
    for _ in range(B_REPS):
        pos = RNG.uniform(0, 1, max(m - 2, 3))
        vals.append(w1_1d(pos, np.ones(len(pos)) / len(pos),
                          u_ref55, np.ones(55) / 55))
    c2_null.append((m, float(np.mean(vals)), float(np.std(vals))))
results["sources"]["C2_e24_trajectory"] = {
    "engine": "TB0 declared lex-pFBA, frozen E24 protocol, 57 points",
    "population": {"n_atoms": int(len(pop_pos)),
                   "total_mass": float(pop_total)},
    "total_mass_4x_8x_v5_reference": 288.76892303855567,
    "uniform_thinning": {"sizes": c2_sizes,
                         "bl_mean": [m for _, m, _ in c2a],
                         "bl_sd": [s for _, _, s in c2a],
                         "rel_mass_err_mean": [m for _, m, _ in c2a_mass],
                         "value_kinks_mean": [v for _, v in c2a_vk]},
    "anchor_thinning": {"sizes": c2_sizes,
                        "bl_mean": [m for _, m, _ in c2b],
                        "bl_sd": [s for _, _, s in c2b],
                        "rel_mass_err_mean": [m for _, m, _ in c2b_mass],
                        "value_kinks_mean": [v for _, v in c2b_vk]},
    "null_bl_mean": [m for _, m, _ in c2_null],
    "reference_rate": "O(h) L1-reconstruction (Thm B'(iv))",
}


# =================================================================
# Interpretation + outputs
# =================================================================
def verdict(slope_meas, slope_null, ratio_final, plateau_eps=0.15):
    if not np.isfinite(slope_meas):
        return "INCONCLUSIVE"
    if abs(slope_meas) < 0.25:
        return "PLATEAU (no stabilization at measured scale)"
    if slope_meas < slope_null - 0.15:
        return "STABILIZES FASTER THAN GC"
    if slope_meas > slope_null + 0.15:
        return ("STABILIZES SLOWER THAN GC (clustered / structured "
                "events)" if ratio_final < 5 else
                "DOES NOT STABILIZE")
    return "STABILIZES AT GC RATE"


A1 = results["sources"]["A_m4b_random_cuts"]["A1_d1"]
B = results["sources"]["B_m1_sweep_panels"]
C1 = results["sources"]["C1_e24_gene_panel"]
C2 = results["sources"]["C2_e24_trajectory"]
results["verdicts"] = {
    "A1_m4b_cuts_d1": verdict(A1["loglog_tail_slope"],
                              A1["null_loglog_tail_slope"],
                              A1["null_ratio_at_max_n"]),
    "A2_m4b_cuts_d2": "decays with the panel; reference-noise "
                        "floor at large n (capped LP atoms); "
                        "consistent with the d=2 GC rate",
    "B_m1_sweep_panels": ("STABILIZES; tail faster than iid-GC = "
                         "finite-population correction (without-"
                         "replacement from 13 heterogeneous sweeps; "
                         "FPC sqrt((13-k)/12); mid-range "
                         "heterogeneity penalty ~1.5x the uniform "
                         "null; panel-limited by construction"),
    "C1_e24_gene_panel": verdict(
        loglog_slope(list(zip(C1["curve"]["sizes"][:-1],
                             C1["curve"]["bl_mean"][:-1]))),
        loglog_slope(list(zip(C1["curve"]["sizes"][:-1],
                             C1["curve"]["null_mean"][:-1]))),
        1.0),
    "C2_e24_trajectory": ("uniform thinning: structural anchor effect "
                          "at small m; anchor-preserving: resolution-"
                          "limited stabilization (see curves)"),
}
results["runtime_s"] = round(time.time() - t0, 1)

with open(os.path.join(OUT, "e32_event_measure_stabilization.json"),
          "w") as f:
    json.dump(results, f, indent=1)
df = pd.DataFrame(rows_csv, columns=[
    "arm", "subarm", "panel_size", "bl_mean", "bl_sd", "null_mean",
    "note"])
df.to_csv(os.path.join(OUT, "e32_event_measure_stabilization.csv"),
          index=False)

# ---------------- figure ----------------
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

fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
ax = axes[0, 0]
ax.errorbar(a1_sizes, [m for _, m, _ in a1], yerr=[s for _, _, s in a1],
            marker="o", ms=4, capsize=2, label="measured (pooled cuts)")
ax.plot(a1_sizes, [m for _, m, _ in a1_null], "s--", ms=4,
        label="null (uniform locations)")
ax.plot(a1_sizes, [p for _, p in a1_pred], ":", label="iid GC $C/\\sqrt{n}$")
ax.plot([n for n, _, _ in a1_split], [m for _, m, _ in a1_split], "^-",
        ms=4, label="split-half (disjoint)")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xlabel("panel size $n$ (random cuts)")
ax.set_ylabel("$d_{BL}$")
ax.set_title("(a) M4b plane: random cuts (event locations, $d{=}1$)")
ax.legend(fontsize=7)

ax = axes[0, 1]
ax.errorbar(b_sizes, [m for _, m, _ in b_curve],
            yerr=[s for _, _, s in b_curve], marker="o", ms=4,
            capsize=2, label="measured (bootstrap panels)")
ax.plot(b_sizes, [m for _, m, _ in b_null], "s--", ms=4,
        label="null (uniform)")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xlabel("panel size $k$ (sweeps, of 13)")
ax.set_ylabel("$d_{BL}$")
ax.set_title("(b) M1 sweeps: mean-field event measure")
ax.legend(fontsize=7)

ax = axes[1, 0]
ax.errorbar(c1_sizes[:-1], [m for _, m, _ in c1_curve][:-1],
            yerr=[s for _, _, s in c1_curve][:-1], marker="o", ms=4,
            capsize=2, label="measured ($\\kappa$ distribution)")
ax.plot(c1_sizes[:-1], [m for _, m, _ in c1_null][:-1], "s--", ms=4,
        label="null (uniform)")
ax.plot(c1_sizes[:-1], [p for _, p in c1_pred][:-1], ":",
        label="BGU asymptotic $C/\\sqrt{m}$")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xlabel("panel size $m$ (genes, of 424)")
ax.set_ylabel("$d_{BL}$ on $\\log_{10}\\kappa^\\mu$")
ax.set_title("(c) E24 panel: $\\kappa^\\mu$ distribution")
ax.legend(fontsize=7)

ax = axes[1, 1]
ax.errorbar(c2_sizes, [m for _, m, _ in c2a], yerr=[s for _, _, s in c2a],
            marker="o", ms=4, capsize=2, label="uniform thinning")
ax.plot(c2_sizes, [m for _, m, _ in c2_null], "s--", ms=4,
        label="null (uniform atoms)")
# the anchor-preserving curve is EXACTLY zero at every m >= 8 (a
# log axis cannot show 0): draw its total-mass error instead, and
# annotate the exactness
ax.plot(c2_sizes, [max(e, 1e-5) for _, e, _ in c2b_mass], "^-",
        ms=4, label="anchor-preserving (total-mass error; BL $\\equiv$ 0)")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xlabel("panel size $m$ (grid points, of 57)")
ax.set_ylabel("$d_{BL}$ / relative mass error")
ax.set_title("(d) E24 trajectory: $L^1$-reconstruction regime")
ax.annotate("anchor-preserving: $d_{BL}\\equiv0$, mass error $\\equiv0$,"
            "\\n4 value kinks $\\equiv4$ at every $m\\geq8$ (design exact)",
            xy=(0.97, 0.05), xycoords="axes fraction", ha="right",
            fontsize=7, style="italic")
ax.legend(fontsize=7)
fig.suptitle("E32: event-measure stabilization across growing panels "
             "(bounded-Lipschitz $= W_1$)", fontsize=11)
fig.savefig(os.path.join(OUT, "e32_event_measure_stabilization.png"),
            dpi=170)
print(f"[E32] done in {time.time() - t0:.0f}s -> "
      f"{OUT}/e32_event_measure_stabilization.{{json,csv,png}}",
      flush=True)
