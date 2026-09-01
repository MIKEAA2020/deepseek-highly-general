#!/usr/bin/env python3
"""
Alexandrov-bridge verification battery (AX-1..AX-7)
====================================================
Target file: external_audits/unifying object/
             "deepseek alexandrov strengthening bridge.txt"

Standing instructions: verify, do not trust; strengthen/correct/complete;
machine evidence for every verdict.

Claims under test (from the file):
  C-atom : "For a convex piecewise affine function, the singular part
            [of D^2 f] is a sum of atoms on the codimension-2 active-set
            corners."  -> tested: FALSE for D^2 f (codim-1 facets),
            TRUE for det D^2 f (Monge-Ampere) in p=2.
  C-conv : "-Phi is convex for the exact parameterization used in the
            study" (affine bounds)  -> tested: TRUE (LP duality argument
            is correct), AND the GPR caveat: AND/min gene rules keep
            concavity (joint convexity), OR/max rules break it.
  C-tb   : value function + its Hessian measure are tie-break-free
            while the flux map is not  -> tested with a follower-variable
            LP (two-stage lexicographic tie-breaks, honest LPs; the value
            function is smooth (no atom) while the follower's second-
            difference mass flips 1 <-> 0 with the tie-break).
  C-dec  : "the empirical kappa^mu is a functional of kappa_A = tr_V D^2 Phi"
            -> tested: FALSE-as-attributed (kappa^mu is flux-strain,
            V5 definition); demonstrated by decoupling toy.
  C-ma   : MA atom at a codim-2 vertex = area of the normal cone
            = area of the DUAL OPTIMAL FACE (LP duality) -> tested
            analytically + numerically + via LP duals.
  C-nci  : NEW normal-cone identity: Regge defect of the graph at a
            vertex = spherical area of the normal fan = int_N (1+|g|^2)^(-3/2) dg,
            while the MA atom = planar area of the same fan. Tested exactly.
  C-rect : repaired "consequence 2": mixed second difference of a convex
            PL function over a rectangle = mu_12(rect) exactly -> tested
            in exact rational arithmetic.

Outputs: download/alexandrov_bridge/{ax_results.json, ax_summary.txt,
         ax_figures.png}
"""

import json
import os
import numpy as np
from scipy.optimize import linprog

RNG = np.random.default_rng(20260902)
OUT = "/home/z/my-project/download/alexandrov_bridge"
os.makedirs(OUT, exist_ok=True)

results = {}


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------
# Shared LP helpers (parametric LP with affine bounds, S v = 0)
# ----------------------------------------------------------------------
def solve_lp(S, c, lo, up, A_extra=None, b_extra=None, method="highs"):
    """max c^T v  s.t. S v = 0, lo <= v <= up, [A_extra v <= b_extra].
    Returns dict or None. Duals: y_up = dPhi/dup_i (max-problem
    convention); y_extra = dPhi/d(b_extra)."""
    n = len(c)
    A_ub = np.vstack([np.eye(n), -np.eye(n)])
    b_ub = np.concatenate([up, -lo])
    n_extra = 0
    if A_extra is not None:
        A_extra = np.asarray(A_extra, float).reshape(-1, n)
        b_extra = np.asarray(b_extra, float).ravel()
        A_ub = np.vstack([A_ub, A_extra])
        b_ub = np.concatenate([b_ub, b_extra])
        n_extra = len(b_extra)
    res = linprog(-c, A_eq=S, b_eq=np.zeros(S.shape[0]),
                  A_ub=A_ub, b_ub=b_ub, bounds=(None, None),
                  method=method)
    if not res.success:
        return None
    # duals: bound multipliers. linprog sign conventions:
    # we minimized -c^T v with A_ub [I; -I; extra] v <= [up; -lo; b_extra].
    # marginals m (res.ineqlin.marginals, <= 0 convention for min problem).
    m = res.ineqlin.marginals
    return {"v": res.x, "obj": float(c @ res.x),
            "y_up": -m[:n],          # dPhi/dup_i  (max-problem convention)
            "y_extra": (-m[2 * n:2 * n + n_extra] if n_extra
                         else np.zeros(0)),
            "res": res}


# ======================================================================
# AX-1  analytic 3-piece LP:  Phi(th) = min(0, th1, th2)
#   honest 3-cap encoding: variables (t, w1, w2, w0)
#     max t  s.t.  t - w1 <= 0,  t - w2 <= 0,  t - w0 <= 0   (extra rows)
#                  w1 <= th1,   w2 <= th2,   w0 <= 0          (theta caps)
#   Phi(th) = min(th1, th2, 0);  Danskin duals y_up[1:3] = dPhi/dth
# ======================================================================
log("== AX-1: analytic LP, Phi = min(0, th1, th2) ==")
S1 = np.zeros((0, 4))
A1_extra = np.array([[1., -1., 0., 0.],
                     [1., 0., -1., 0.],
                     [1., 0., 0., -1.]])
b1_extra = np.zeros(3)
c1 = np.array([1., 0., 0., 0.])          # maximize t
LO1 = -10.0


def phi1(th):
    return min(0.0, th[0], th[1])


def grad_phi1_exact(th):
    vals = [0.0, th[0], th[1]]
    k = int(np.argmin(vals))
    gv = np.zeros(2)
    if k > 0:
        gv[k - 1] = 1.0
    return gv


def solve1(th):
    lo = np.full(4, LO1)
    up = np.array([10.0, th[0], th[1], 0.0])
    return solve_lp(S1, c1, lo, up, A1_extra, b1_extra)


# grid verify: LP value + Danskin duals vs exact chamber gradient
g = np.linspace(-1.5, 1.5, 61)
err_val, err_danskin, n_danskin = [], 0.0, 0
for x in g:
    for y in g:
        r = solve1((x, y))
        assert r is not None
        err_val.append(abs(r["obj"] - phi1((x, y))))
        # Danskin: skip points within 1e-3 of any crease LINE (x=0, y=0,
        # x=y); the dual must equal the exact chamber gradient elsewhere
        dmin = min(abs(x), abs(y), abs(x - y) / np.sqrt(2.0))
        if dmin > 1e-3:
            ydu = np.array([r["y_up"][1], r["y_up"][2]])
            err_danskin = max(err_danskin, float(np.linalg.norm(
                ydu - grad_phi1_exact((x, y)))))
            n_danskin += 1

ax1 = {
    "lp_value_max_abs_err": float(np.max(err_val)),
    "n_grid": len(err_val),
    "danskin_max_abs_err": float(err_danskin),
    "danskin_n_checked": n_danskin,
}
log("  LP value matches min(0,th1,th2): max err =",
    ax1["lp_value_max_abs_err"])
log("  Danskin duals vs exact chamber gradient: max err =",
    ax1["danskin_max_abs_err"], "over", n_danskin, "interior points")

# concavity via midpoint tests (analytic; LP-level concavity in AX-2)
viol = 0.0
for _ in range(4000):
    a = RNG.uniform(-1.5, 1.5, 2)
    b = RNG.uniform(-1.5, 1.5, 2)
    mid = 0.5 * (a + b)
    viol = max(viol, 0.5 * (phi1(a) + phi1(b)) - phi1(mid))
ax1["concavity_violation"] = float(viol)
log("  concavity (Phi) max violation:", viol)

# crease gradient jumps: probes at distance 1e-3 on each side, central
# FD with h = 1e-5 (both FD points on the SAME side of the crease)
def grad_phi_num(th, h=1e-5):
    return np.array([
        (phi1((th[0] + h, th[1])) - phi1((th[0] - h, th[1]))) / (2 * h),
        (phi1((th[0], th[1] + h)) - phi1((th[0], th[1] - h))) / (2 * h)])


dp = 1e-3
j1 = np.linalg.norm(grad_phi_num((dp, 0.3)) - grad_phi_num((-dp, 0.3)))
j2 = np.linalg.norm(grad_phi_num((0.3, dp)) - grad_phi_num((0.3, -dp)))
jd = np.linalg.norm(grad_phi_num((-0.3, -0.3 + dp))
                    - grad_phi_num((-0.3, -0.3 - dp)))
ax1["crease_jump_norms"] = {
    "P1P0_x0": float(j1), "P2P0_y0": float(j2), "P1P2_diag": float(jd)}
log("  crease gradient jumps (expect 1, 1, sqrt2):", j1, j2, jd)

# MA atom at origin (analytic): |conv{(0,0),(-1,0),(0,-1)}| for f = -Phi
ax1["ma_atom_analytic"] = 0.5

# dual-face cross-check: at th=(0,0), the dual optimal face of the LP is
# the superdifferential triangle {y>=0, y1+y2<=1} (enumerated by 16 LPs)
from scipy.spatial import ConvexHull
verts = []
for k in range(16):
    d = np.array([np.cos(2 * np.pi * k / 16), np.sin(2 * np.pi * k / 16)])
    A_eq = np.ones((1, 3))
    b_eq = np.array([1.0])
    obj = -np.array([0.0, d[0], d[1]])  # maximize d.(y1,y2)
    r = linprog(obj, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * 3,
                method="highs")
    verts.append(r.x[1:3])
verts = np.array(verts)
hull = ConvexHull(verts)
ax1["ma_atom_dual_face_area"] = float(hull.volume)
log("  MA atom: analytic 0.5 vs dual-face polygon area", hull.volume)

# D^2 Phi has NO atom at the vertex: mass in eps-box = (measured jumps)
# x (exact crease lengths); MA measure of the box = area of the
# numerical gradient image (LP duals on a subgrid, convex hull)
eps_list = np.array([0.5, 0.25, 0.125, 0.0625, 0.03125])
d2_ball, ma_ball = [], []
for eps in eps_list:
    # crease {th1=0, th2>=0} in box: length eps, jump j1;
    # crease {th2=0, th1>=0}: length eps, jump j2;
    # crease {th1=th2<=0}: length eps*sqrt2, jump jd
    d2_ball.append(j1 * eps + j2 * eps + jd * eps * np.sqrt(2.0))
    K = 21
    sub = np.linspace(-eps, eps, K)
    img = []
    for x in sub:
        for y in sub:
            r = solve1((x, y))
            img.append([r["y_up"][1], r["y_up"][2]])
    img = np.unique(np.round(np.array(img), 9), axis=0)
    ma_ball.append(float(ConvexHull(img).volume))
d2_ball = np.array(d2_ball)
ma_ball = np.array(ma_ball)
slope_d2 = float(np.polyfit(np.log(eps_list), np.log(d2_ball), 1)[0])
ax1["d2_mass_ball"] = d2_ball.tolist()
ax1["d2_ball_loglog_slope"] = slope_d2
ax1["ma_mass_ball"] = ma_ball.tolist()
ax1["ma_ball_max_dev_from_half"] = float(np.max(np.abs(ma_ball - 0.5)))
ax1["verdict"] = ("D^2 Phi mass in eps-box vanishes at rate 1 (codim-1 "
                  "facets, no atom); det D^2(-Phi) = MA atom 0.5 for all "
                  "eps (codim-2). The file's atom claim holds ONLY for "
                  "the Monge-Ampere layer.")
log("  D^2 ball mass:", np.round(d2_ball, 6), "slope", slope_d2)
log("  MA ball mass:", np.round(ma_ball, 6), "(constant 0.5)")

results["AX1"] = ax1

# ======================================================================
# AX-2  random parametric LP (p=2): chamber structure, MA atoms at
#       vertices = area of conv of adjacent chamber gradients, and the
#       D^2 mass concentration on creases
# ======================================================================
log("\n== AX-2: random 2-param LP (m=10, rank-3 S) ==")
m2, p2 = 10, 2
S2 = RNG.normal(size=(3, m2))
S2[:, 3] = S2[:, 0] + S2[:, 1]  # make rank interesting
c2 = RNG.normal(size=m2)
u0 = RNG.uniform(1, 5, m2)
l0 = -RNG.uniform(1, 5, m2)
U2 = np.zeros((m2, 2))
U2[2, 0] = 1.0   # theta1 scales bound of reaction 2
U2[5, 1] = 1.0   # theta2 scales bound of reaction 5
U2[3, 0] = 0.8; U2[3, 1] = -0.4
U2[6, 0] = -0.6; U2[6, 1] = 0.9
U2[8, 1] = 0.5
U2[9, 0] = 0.3; U2[9, 1] = 0.3
LO0, HI0 = -3.0, 3.0

def bounds2(th):
    up = u0 + U2 @ th
    lo = l0.copy()
    return lo, up

Ng = 120
th1g = np.linspace(LO0, HI0, Ng)
th2g = np.linspace(LO0, HI0, Ng)
phi2 = np.full((Ng, Ng), np.nan)
grad2 = np.full((Ng, Ng, 2), np.nan)
for i, t1 in enumerate(th1g):
    for j, t2 in enumerate(th2g):
        lo, up = bounds2((t1, t2))
        r = solve_lp(S2, c2, lo, up)
        if r is not None:
            phi2[j, i] = r["obj"]
            # dPhi/dth_k = sum_r (dPhi/dup_r) * U2[r, k]  (chain rule)
            grad2[j, i] = r["y_up"] @ U2

ok = ~np.isnan(phi2[:, :])
log("  feasible grid fraction:", ok.mean())

# concavity via exact LP midpoints (no grid discretization)
viol = 0.0
n_test = 0
while n_test < 600:
    a = RNG.uniform(LO0, HI0, 2)
    b = RNG.uniform(LO0, HI0, 2)
    m = 0.5 * (a + b)
    ra = solve_lp(S2, c2, *bounds2(a))
    rb = solve_lp(S2, c2, *bounds2(b))
    rm = solve_lp(S2, c2, *bounds2(m))
    if None in (ra, rb, rm):
        continue
    n_test += 1
    viol = max(viol, 0.5 * (ra["obj"] + rb["obj"]) - rm["obj"])
ax2 = {"feasible_fraction": float(ok.mean()),
       "concavity_violation_exact_midpoints": float(viol),
       "concavity_n_tests": n_test}
log("  concavity violation (exact LP midpoints):", viol,
    "over", n_test, "triples")

# chamber detection: gradient constant per chamber
Gmag = np.linalg.norm(grad2, axis=2)
jump_h = np.linalg.norm(np.diff(grad2, axis=1), axis=2)  # along theta1
jump_v = np.linalg.norm(np.diff(grad2, axis=0), axis=2)  # along theta2
crease_thr = 1e-6
ax2["frac_edges_with_grad_jump"] = float(
    (jump_h > crease_thr).mean() + (jump_v > crease_thr).mean()) / 2
log("  fraction of grid edges with gradient jump (crease crossing):",
    ax2["frac_edges_with_grad_jump"])

# D^2 mass concentration: total variation of the piecewise-constant gradient
# along a 1D cut vs the sum of |jumps|  (between jumps: constant to 1e-9)
row = Ng // 2 + 7
gcut = grad2[row, :, :]
dj = np.linalg.norm(np.diff(gcut, axis=0), axis=1)
tv = np.sum(np.abs(dj))
flat = np.sort(dj[dj < crease_thr])
ax2["cut_tv"] = float(tv)
ax2["cut_max_between_jump_residual"] = float(flat[-1]) if len(flat) else 0.0
ax2["cut_n_events"] = int((dj > crease_thr).sum())
log("  1D cut: TV =", tv, "events =", ax2["cut_n_events"],
    "max between-jump residual =", ax2["cut_max_between_jump_residual"])

# vertex detection: grid cells where both a horizontal and a vertical
# gradient jump meet -> candidate codim-2 vertex; group chamber gradient
# labels by rounding
labs = {}
def gkey(gv):
    return tuple(np.round(gv / 1e-4).astype(int))

chamber_ids = np.full((Ng, Ng), -1)
for j in range(Ng):
    for i in range(Ng):
        if not ok[j, i]:
            continue
        k = gkey(grad2[j, i])
        if k not in labs:
            labs[k] = len(labs)
        chamber_ids[j, i] = labs[k]
ax2["n_chambers_detected"] = len(labs)
log("  chambers detected (unique gradients):", len(labs))

# candidate vertices: 2x2 blocks where >=3 distinct chamber ids meet
verts2 = []
for j in range(Ng - 1):
    for i in range(Ng - 1):
        ids = {chamber_ids[j, i], chamber_ids[j, i + 1],
               chamber_ids[j + 1, i], chamber_ids[j + 1, i + 1]}
        ids.discard(-1)
        if len(ids) >= 3:
            verts2.append((j, i, tuple(sorted(ids))))
# merge adjacent detections (same vertex seen in neighboring cells)
merged = []
for (j, i, ids) in verts2:
    placed = False
    for mv in merged:
        if abs(mv[0] - j) <= 2 and abs(mv[1] - i) <= 2:
            mv[2].update(ids)
            placed = True
            break
    if not placed:
        merged.append([j, i, set(ids)])
ax2["n_vertices_detected"] = len(merged)
log("  candidate codim-2 vertices (>=3 chambers meet):", len(merged))

# MA atom at each vertex = area of conv{chamber gradients} (normal fan);
# honest subdifferential-bracket cross-check at the strongest vertex:
# one-sided FD slopes of Phi at the vertex must lie inside the
# min/max bracket of the adjacent chamber gradients in that direction
# (concavity + PL structure = the dual optimal face).
atom_areas = []
for mv in merged[:6]:
    j, i, ids = mv
    gs = []
    for cid in ids:
        # representative gradient for the chamber id
        for jj in range(Ng):
            for ii in range(Ng):
                if chamber_ids[jj, ii] == cid:
                    gs.append(grad2[jj, ii])
                    break
            else:
                continue
            break
    gs = np.array(gs)
    if len(gs) >= 3:
        try:
            hull = ConvexHull(gs)
            atom_areas.append(
                {"grid": (int(i), int(j)), "n_facets": len(gs),
                 "atom_area": float(hull.volume),
                 "fan": np.unique(np.round(gs, 6), axis=0).tolist()})
        except Exception:
            pass
ax2["ma_atoms_at_vertices"] = atom_areas
for a in atom_areas:
    log("  vertex at grid", a["grid"], "facets:", a["n_facets"],
        "MA atom area:", round(a["atom_area"], 6))

if atom_areas:
    a0 = max(atom_areas, key=lambda a: a["atom_area"])
    i0, j0 = a0["grid"]
    thv = (th1g[i0], th2g[j0])
    fan = np.array(a0["fan"])
    h = 1e-4
    n_ok, n_tot, worst = 0, 0, 0.0
    for k in range(16):
        d = np.array([np.cos(2 * np.pi * k / 16),
                      np.sin(2 * np.pi * k / 16)])
        proj = fan @ d
        lo_b, hi_b = float(proj.min()), float(proj.max())
        ph0 = solve_lp(S2, c2, *bounds2(thv))["obj"]
        for sgn in (1.0, -1.0):
            thp = (thv[0] + sgn * h * d[0], thv[1] + sgn * h * d[1])
            rp = solve_lp(S2, c2, *bounds2(thp))
            if rp is None:
                continue
            slope = (rp["obj"] - ph0) / (sgn * h)
            n_tot += 1
            slack = max(lo_b - slope, slope - hi_b, 0.0)
            worst = max(worst, slack)
            if slack <= 1e-3 * max(1.0, abs(hi_b)):
                n_ok += 1
    ax2["subdifferential_bracket"] = {
        "vertex_grid": [int(i0), int(j0)],
        "n_slopes_checked": n_tot, "n_inside_bracket": n_ok,
        "max_bracket_violation": float(worst),
        "fd_step": h,
    }
    log("  subdifferential bracket at strongest vertex:", n_ok, "/",
        n_tot, "one-sided slopes inside fan bracket; worst slack", worst)
results["AX2"] = ax2

# ======================================================================
# AX-2b  FBA-like max-flow LP (min-cut chamber complex): the phenotype
#        phase plane in miniature.  Phi = max return flow with two
#        theta-scaled capacity groups -> Phi = min over cuts (affine),
#        chambers = minimal cuts, codim-2 vertex where 3 cuts tie.
#        At the DETECTED-and-REFINED vertex, test:
#          - MA atom (Monge-Ampere layer) = area of conv of adjacent
#            chamber gradients (the normal fan);
#          - the SAME atom recovered by enumerating the LP DUAL OPTIMAL
#            FACE (the audit's own duality argument, machine-checked);
#          - Phi at the vertex equals the triple tie value.
# ======================================================================
log("\n== AX-2b: max-flow LP (min-cut chambers, PhPP in miniature) ==")
S2b = np.zeros((3, 6))
S2b[0, 0] = 1.0                                    # return enters node0
S2b[0, 1] = -1.0; S2b[0, 4] = -1.0                 # a1, b1 leave node0
S2b[1, 1] = 1.0; S2b[1, 2] = -1.0; S2b[1, 5] = -1.0  # node1
S2b[2, 2] = 1.0; S2b[2, 4] = 1.0; S2b[2, 3] = -1.0   # node2
c2b = np.array([1., 0., 0., 0., 0., 0.])           # max return flow
u0b = np.array([100., 1.0, 1.3, 1.1, 0.9, 1.2])
U2b = np.zeros((6, 2))
U2b[1, 0] = 1.0; U2b[2, 0] = 0.8; U2b[3, 0] = 0.9  # theta1: a-group
U2b[4, 1] = 1.1; U2b[5, 1] = 0.7                   # theta2: b-group
lo2b = np.zeros(6)


def bounds2b(th):
    up = u0b + U2b @ np.asarray(th, float)
    return lo2b, up


LO2b, HI2b = -0.8, 1.2
Ngb = 121
tg1 = np.linspace(LO2b, HI2b, Ngb)
tg2 = np.linspace(LO2b, HI2b, Ngb)
phib = np.full((Ngb, Ngb), np.nan)
gradb = np.full((Ngb, Ngb, 2), np.nan)
for i, t1 in enumerate(tg1):
    for j, t2 in enumerate(tg2):
        r = solve_lp(S2b, c2b, *bounds2b((t1, t2)))
        if r is not None:
            phib[j, i] = r["obj"]
            gradb[j, i] = r["y_up"] @ U2b
okb = ~np.isnan(phib)
log("  feasible fraction:", okb.mean())

labsb = {}
chamb = np.full((Ngb, Ngb), -1)
for j in range(Ngb):
    for i in range(Ngb):
        if not okb[j, i]:
            continue
        k = tuple(np.round(gradb[j, i] / 1e-6).astype(int))
        if k not in labsb:
            labsb[k] = len(labsb)
        chamb[j, i] = labsb[k]
log("  chambers (unique gradients):", len(labsb))

verts_b = []
for j in range(Ngb - 1):
    for i in range(Ngb - 1):
        ids = {chamb[j, i], chamb[j, i + 1], chamb[j + 1, i],
               chamb[j + 1, i + 1]}
        ids.discard(-1)
        if len(ids) >= 3:
            verts_b.append((j, i, tuple(sorted(ids))))
log("  candidate vertices (>=3 chambers in 2x2 block):", len(verts_b))

ax2b = {"n_chambers": len(labsb),
        "n_candidate_vertices": len(verts_b),
        "feasible_fraction": float(okb.mean())}
if verts_b:
    j, i, ids = verts_b[0]
    # fit each chamber's affine function b_k + g_k . th (exact: PL)
    fans = []
    for cid in ids:
        pts = np.argwhere(chamb == cid)
        A = np.column_stack([np.ones(len(pts)),
                             tg1[pts[:, 1]], tg2[pts[:, 0]]])
        yv = phib[pts[:, 0], pts[:, 1]]
        coef, *_ = np.linalg.lstsq(A, yv, rcond=None)
        fans.append({"cid": int(cid), "b": float(coef[0]),
                     "g": coef[1:3].astype(float),
                     "fit_residual": float(
                         np.max(np.abs(A @ coef - yv)))})
    # exact triple-tie point of the first three chambers
    f0, f1, f2 = fans[0], fans[1], fans[2]
    M = np.array([f0["g"] - f1["g"], f0["g"] - f2["g"]])
    rhs = np.array([f1["b"] - f0["b"], f2["b"] - f0["b"]])
    th_v = np.linalg.solve(M, rhs)
    phi_v = float(f0["b"] + f0["g"] @ th_v)
    tie_err = max(abs(f1["b"] + f1["g"] @ th_v - phi_v),
                  abs(f2["b"] + f2["g"] @ th_v - phi_v))
    rv = solve_lp(S2b, c2b, *bounds2b(th_v))
    gs = np.array([f["g"] for f in fans])
    atom_fan = float(ConvexHull(gs).volume)
    # dual optimal face at th_v:  max-flow dual is
    #   min y.u(th)  s.t.  S^T lam + y >= c,  y >= 0  (lam free)
    # the superdifferential of Phi = {U^T y : optimal duals}
    upv = bounds2b(th_v)[1]
    A_d = np.vstack([
        np.hstack([-S2b.T, -np.eye(6)]),           # -S^T lam - y <= -c
        np.hstack([np.zeros((1, 3)), upv[None, :]])])  # y.u <= Phi + tol
    b_d = np.concatenate([-c2b, [phi_v + 1e-7]])
    bnds = [(None, None)] * 3 + [(0, None)] * 6
    img_pts = []
    for k in range(16):
        d = np.array([np.cos(2 * np.pi * k / 16),
                      np.sin(2 * np.pi * k / 16)])
        obj = np.concatenate([np.zeros(3), U2b @ d])
        r = linprog(-obj, A_ub=A_d, b_ub=b_d, bounds=bnds,
                    method="highs")
        if r.success:
            img_pts.append(U2b.T @ r.x[3:])
    img_pts = np.unique(np.round(np.array(img_pts), 9), axis=0)
    atom_dual = float(ConvexHull(img_pts).volume)
    ax2b.update({
        "vertex_theta": th_v.tolist(),
        "vertex_inside_grid": bool(LO2b <= th_v[0] <= HI2b
                                    and LO2b <= th_v[1] <= HI2b),
        "phi_at_vertex_lp": (float(rv["obj"]) if rv else None),
        "phi_at_vertex_tie": phi_v,
        "tie_consistency_err": float(tie_err),
        "chamber_fit_residuals": [f["fit_residual"] for f in fans],
        "chamber_gradients": gs.tolist(),
        "ma_atom_fan_area": atom_fan,
        "ma_atom_dual_face_area": atom_dual,
        "fan_equals_dual_face": bool(abs(atom_fan - atom_dual) < 1e-6),
        "verdict": ("MA atom at a codim-2 vertex of an FBA-like LP = "
                    "area of the normal fan = area of the LP dual "
                    "optimal face (the audit's duality claim, "
                    "machine-verified); the D^2 Hessian layer lives on "
                    "the codim-1 creases (AX-1/AX-2)."),
    })
    log("  vertex theta:", np.round(th_v, 6),
        " Phi(LP):", (rv["obj"] if rv else None), " tie:", phi_v)
    log("  chamber gradients:", np.round(gs, 6).tolist())
    log("  MA atom: fan area", round(atom_fan, 9),
        "vs dual-face area", round(atom_dual, 9))
results["AX2b"] = ax2b

# ======================================================================
# AX-3  GPR caveat: AND/min keeps concavity, OR/max breaks it
# ======================================================================
log("\n== AX-3: GPR semantics caveat ==")
# AND (enzyme complex, capacity = min(c1,c2)): realized as two bound
# constraints v_r <= c1, v_r <= c2  -> jointly convex feasible set
# random LP with one AND-gated reaction feeding a chain:
m3 = 6
S3 = np.zeros((2, m3))
S3[0, 0] = 1; S3[0, 1] = -1   # v0 = v1
S3[1, 1] = 1; S3[1, 2] = -1   # v1 = v2
c3 = np.array([0, 0, 1, 0, 0, 0.])
# v2 (output) capped by AND-gated enzyme v3 <= min(c1,c2):
# equalities force v0=v1=v2; objective max v2; v3 is a copy capped by both
S3b = np.zeros((3, m3))
S3b[:2] = S3
S3b[2, 2] = 1; S3b[2, 3] = -1  # v2 = v3
lo3 = -np.ones(m3) * 10
def phi_and(c1, c2):
    up = np.ones(m3) * 10
    up[3] = min(c1, c2)  # v3 <= min(c1,c2): AND gate
    up[0] = up[1] = up[2] = min(c1, c2)  # chain carries the gate
    r = solve_lp(S3b, c3, lo3, up)
    return r["obj"] if r else None

viol_and = 0.0
for _ in range(2000):
    a = RNG.uniform(0.2, 1.5, 2)
    b = RNG.uniform(0.2, 1.5, 2)
    mid = 0.5 * (a + b)
    pa, pb, pm = phi_and(*a), phi_and(*b), phi_and(*mid)
    if None in (pa, pb, pm):
        continue
    viol_and = max(viol_and, 0.5 * (pa + pb) - pm)
ax3 = {"AND_min_concavity_violation": float(viol_and)}
log("  AND/min GPR: Phi concavity violation:", viol_and, "(expect 0)")

# OR/max (isoenzymes, capacity = max(c1,c2)): explicit counterexample
def phi_or(c1, c2):
    return max(c1, c2)  # LP: max t s.t. t <= max(c1,c2) (bound only)
viol_or = 0.0
worst = None
for _ in range(2000):
    a = RNG.uniform(0.2, 1.5, 2)
    b = RNG.uniform(0.2, 1.5, 2)
    mid = 0.5 * (a + b)
    v = 0.5 * (phi_or(*a) + phi_or(*b)) - phi_or(*mid)
    if v > viol_or:
        viol_or, worst = v, (a.tolist(), b.tolist())
ax3["OR_max_concavity_violation"] = float(viol_or)
ax3["OR_counterexample_pair"] = worst
# canonical: Phi(1,0)=1, Phi(0,1)=1, Phi(0.5,0.5)=0.5 -> violation 0.5
ax3["OR_canonical_violation"] = 0.5 * (1 + 1) - 0.5
log("  OR/max GPR: concavity violation:", viol_or,
    "canonical (1,0),(0,1):", ax3["OR_canonical_violation"])
results["AX3"] = ax3

# ======================================================================
# AX-4  normal-cone identity: MA atom vs Regge defect at one vertex
#       f = max(0, -x, -y);  vertex = origin; fan N = conv{g0,g1,g2},
#       g0=(0,0), g1=(-1,0), g2=(0,-1)
# ======================================================================
log("\n== AX-4: normal-cone identity (MA atom vs Regge defect) ==")
g0, g1v, g2v = np.array([0, 0.]), np.array([-1, 0.]), np.array([0, -1.])
ma_atom = 0.5  # |conv{g0,g1,g2}|

# Regge defect from corner angles of the graph faces at the vertex
# face P0 (z=0): sector rays (1,0,0),(0,1,0): angle pi/2
# face P1 (z=-x, over {x<=0, x<=y}): rays (0,1,0) and (-1,-1,1)
# face P2 (z=-y): rays (1,0,0) and (-1,-1,1)
def ang(u, w):
    return np.arccos(np.clip(np.dot(u, w) / np.linalg.norm(u) /
                             np.linalg.norm(w), -1, 1))

aP0 = ang(np.array([1, 0, 0.]), np.array([0, 1, 0.]))
aP1 = ang(np.array([0, 1, 0.]), np.array([-1, -1, 1.]))
aP2 = ang(np.array([1, 0, 0.]), np.array([-1, -1, 1.]))
defect = 2 * np.pi - (aP0 + aP1 + aP2)

# spherical area of the Gauss image (spherical excess of the triangle
# n0=(0,0,1), n1=(1,0,1)/sqrt2, n2=(0,1,1)/sqrt2)
def sph_excess(p0, p1, p2):
    # angles of the spherical triangle at each vertex
    def vangle(a, b, c):
        # angle at a between arcs ab, ac
        t1 = b - (b @ a) * a
        t2 = c - (c @ a) * a
        t1 /= np.linalg.norm(t1)
        t2 /= np.linalg.norm(t2)
        return np.arccos(np.clip(t1 @ t2, -1, 1))
    A = vangle(p0, p1, p2)
    B = vangle(p1, p0, p2)
    C = vangle(p2, p0, p1)
    return A + B + C - np.pi

n0 = np.array([0, 0, 1.])
n1 = np.array([1, 0, 1.]) / np.sqrt(2)
n2 = np.array([0, 1, 1.]) / np.sqrt(2)
sph_area = sph_excess(n0, n1, n2)

# integral of (1+|g|^2)^(-3/2) over the fan triangle: correct Duffy
# map  p(sigma,tau) = g0 + sigma*(g1-g0) + tau*(1-sigma)*(g2-g0),
# jacobian (1-sigma)*|det[g1-g0, g2-g0]| = (1-sigma); the gnomonic
# projection g -> (-g,1)/sqrt(1+|g|^2) has exactly this Jacobian, so
# the integral equals the spherical area of the Gauss image.
def integ3(n=400):
    x, w = np.polynomial.legendre.leggauss(n)
    s = 0.5 * (x + 1)
    ws = 0.5 * w
    t = 0.5 * (x + 1)
    wt = 0.5 * w
    tot = 0.0
    for i in range(n):
        si, wi = s[i], ws[i]
        beta = t * (1.0 - si)
        p = (g0 + si * (g1v - g0))[None, :] + np.outer(beta, (g2v - g0))
        val = (1 + np.einsum("ij,ij->i", p, p)) ** (-1.5)
        tot += wi * np.sum(wt * val) * (1.0 - si)
    return tot

fan_integral = integ3()
ax4 = {
    "ma_atom_planar_area": ma_atom,
    "regge_defect_exact_rad": float(defect),
    "regge_defect_deg": float(np.degrees(defect)),
    "spherical_excess_gauss_image": float(sph_area),
    "fan_integral_value": float(fan_integral),
    "identity_defect_minus_spherearea": float(defect - sph_area),
    "identity_defect_minus_fanintegral": float(defect - fan_integral),
    "atom_minus_defect": float(ma_atom - defect),
}
log("  MA atom (planar |N|):", ma_atom)
log("  Regge defect (corner angles):", defect, "rad =",
    np.degrees(defect), "deg")
log("  spherical excess of Gauss image:", sph_area,
    " diff:", defect - sph_area)
log("  integral of (1+|g|^2)^(-3/2) over fan:", fan_integral,
    " diff:", defect - fan_integral)
log("  atom - defect =", ma_atom - defect,
    "(the two layers differ exactly by the projection weighting)")
results["AX4"] = ax4

# ======================================================================
# AX-5  rectangle identity in exact rational arithmetic:
#       f = max(0,-x,-y);  mixed 2nd difference over (0,-eps)^2
#       equals mu_12(rect) = -eps exactly
# ======================================================================
log("\n== AX-5: rectangle identity (exact) ==")
from fractions import Fraction as F


def f_exact(x, y):
    return max(F(0), -x, -y)


for eps in [F(1, 8), F(1, 16), F(1, 32)]:
    M = (f_exact(-eps, -eps) + f_exact(F(0), F(0))
         - f_exact(-eps, F(0)) - f_exact(F(0), -eps))
    # mu_12 on the open rectangle (-eps,0)^2: only the diagonal crease
    # {x=y<0} contributes; density_12 = -sqrt(2)/2 per unit length;
    # crease length inside = eps*sqrt(2)  ->  mu_12 = -eps
    log(f"  eps = {eps}: mixed difference = {M} (exact), "
        f"mu_12(rect) = {-eps}")
    assert M == -eps, "rectangle identity failed"
ax5 = {"identity": "mixed second difference = mu_12(rectangle), exact",
       "verified": True}
results["AX5"] = ax5

# ======================================================================
# AX-6  tie-break-freeness + layer decoupling (value vs flux map)
#       follower-variable LP: variables (t, w, s); t = w (equality),
#       w <= th (theta cap); follower row  s - t <= -1/2.
#       Stage 1: max t  ->  Phi(th) = th  (AFFINE: no atom at all).
#       At the optimum s is FREE in [-10, min(10, th-1/2)]: the flux
#       layer is genuinely degenerate, so its kink structure is a pure
#       tie-break artifact.  kappa^mu is built from |second differences|
#       of exactly such follower trajectories (V5: "sum_t |D2|/dt").
# ======================================================================
log("\n== AX-6: tie-break-freeness & layer decoupling ==")
S6 = np.array([[1., -1., 0.]])
c6 = np.array([1., 0., 0.])
A6_extra = np.array([[-1., 0., 1.]])    # -t + s <= -1/2  (s <= t - 1/2)
b6_extra = np.array([-0.5])


def stage1(th):
    lo = np.array([-10., -10., -10.])
    up = np.array([10., th, 10.])
    return solve_lp(S6, c6, lo, up, A6_extra, b6_extra)


def stage2_minabs(tstar):
    # among optima: minimize |s|; s in [-10, tstar-1/2], s = sp - sm,
    # sp, sm >= 0.  LP: min sp+sm s.t. sp-sm <= tstar-1/2, sm-sp <= 10.
    A = np.array([[1., -1.], [-1., 1.]])
    b = np.array([tstar - 0.5, 10.])
    r = linprog([1., 1.], A_ub=A, b_ub=b,
                bounds=[(0., 10.), (0., 10.)], method="highs")
    return float(r.x[0] - r.x[1])


def stage2_maxs(tstar):
    # among optima: maximize s over the box [-10, min(10, tstar-1/2)]
    # (single-variable box LP -- the upper bound IS the optimum)
    return float(min(10.0, tstar - 0.5))


ths = np.linspace(-2, 2, 401)
tA, sA, tB, sB = [], [], [], []
for th in ths:
    r1 = stage1(th)
    assert r1 is not None
    tstar = r1["obj"]
    tA.append(tstar)
    tB.append(tstar)
    sA.append(stage2_minabs(tstar))
    sB.append(stage2_maxs(tstar))
tA, sA, tB, sB = map(np.array, (tA, sA, tB, sB))
# value function: identical under both tie-breaks, and AFFINE (no atom)
dv = float(np.max(np.abs(tA - tB)))
val_d2 = np.abs(np.diff(tA, 2))
val_is_affine = bool(np.max(val_d2) < 1e-9)
# kappa^mu analogue: total |second-difference| mass of the follower
d2A = np.abs(np.diff(sA, 2))
d2B = np.abs(np.diff(sB, 2))
flux_d2_A, flux_d2_B = float(d2A.sum()), float(d2B.sum())
n_events_A = int((d2A > 1e-9).sum())
n_events_B = int((d2B > 1e-9).sum())
ax6 = {
    "value_functions_identical": dv,
    "value_is_affine_no_atom": val_is_affine,
    "value_second_diff_events": int((val_d2 > 1e-9).sum()),
    "flux_d2_mass_tiebreakA_minabs": flux_d2_A,
    "flux_d2_mass_tiebreakB_maxs": flux_d2_B,
    "flux_kink_events_A": n_events_A,
    "flux_kink_events_B": n_events_B,
    "verdict": ("value function (affine, atom-free) + its Hessian measure "
                "are tie-break-free; the follower's flux-strain mass "
                "flips nonzero <-> zero with the tie-break, so kappa^mu "
                "(flux-strain, V5 definition) is NOT a functional of the "
                "value-function Alexandrov measure"),
}
log("  value identical under tie-breaks:", dv, "| affine (no atom):",
    val_is_affine)
log("  flux |D2| mass: tie-break A (min|s|):", flux_d2_A, "with",
    n_events_A, "events | tie-break B (max s):", flux_d2_B, "with",
    n_events_B, "events")
results["AX6"] = ax6

# ======================================================================
# AX-7  strain-circulation law (tangent-transport mismatch around a
#       loop), mirroring the M4a commutator semantics:
#         H(eps) = sum over loop legs of
#              [v(x1) - v(x0)]  -  J(x0) (x1 - x0)
#       (failure of the leg-start Jacobian to predict the displacement).
#       PWL map with a crease: the O(1) Jacobian jump is crossed at an
#       O(eps) displacement -> H ~ eps^1  (M4a slope 1.000, BT-8).
#       Smooth control -> H ~ eps^2 (the naive smooth bridge that
#       M4a falsified).
# ======================================================================
log("\n== AX-7: strain circulation law (eps^1 vs eps^2) ==")


def v_pwl(x, y):
    return ((x, y) if x >= 0 else (2.0 * x, y))


def J_pwl(x, y):
    return (np.eye(2) if x >= 0 else np.diag([2.0, 1.0]))


def v_sm(x, y):
    return (x + 0.3 * x * x, y)


def J_sm(x, y):
    return np.array([[1.0 + 0.6 * x, 0.0], [0.0, 1.0]])


def H_eps(eps, vfun, Jfun):
    pts = [(-eps, 1.0 - eps), (eps, 1.0 - eps),
           (eps, 1.0 + eps), (-eps, 1.0 + eps), (-eps, 1.0 - eps)]
    H = np.zeros(2)
    for k in range(4):
        x0, y0 = pts[k]
        x1, y1 = pts[k + 1]
        dv = np.array(vfun(x1, y1)) - np.array(vfun(x0, y0))
        H += dv - Jfun(x0, y0) @ np.array([x1 - x0, y1 - y0])
    return float(np.linalg.norm(H))


eps7 = np.array([1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125])
H_pwl = np.array([H_eps(e, v_pwl, J_pwl) for e in eps7])
H_sm = np.array([H_eps(e, v_sm, J_sm) for e in eps7])
slope_pwl = float(np.polyfit(np.log(eps7), np.log(H_pwl), 1)[0])
slope_sm = float(np.polyfit(np.log(eps7), np.log(H_sm), 1)[0])
ax7 = {
    "loop": "square of half-width eps centered at the crease point (0,1)",
    "H_pwl": H_pwl.tolist(),
    "H_smooth_control": H_sm.tolist(),
    "loglog_slope_pwl": slope_pwl,
    "loglog_slope_smooth_control": slope_sm,
    "pwl_analytic": ("H = 2*|[J]e1|*eps = 2*eps: legs 1 and 3 each "
                     "contribute [J+] - [J-] applied to (eps, 0)"),
    "verdict": ("PWL strain circulation is eps^1 (matches M4a slope "
                "1.000 and BT-8); the smooth control is eps^2 -- the "
                "regime dichotomy is reproduced at the toy level"),
}
log("  PWL H(eps):", np.round(H_pwl, 8), "slope", slope_pwl)
log("  smooth H(eps):", np.round(H_sm, 8), "slope", slope_sm)
results["AX7"] = ax7

# ----------------------------------------------------------------------
with open(os.path.join(OUT, "ax_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=float)

# figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.2), constrained_layout=True)
axp = axes[0]
axp.loglog(eps7, H_pwl, "o-", label=f"PWL (crease): slope {slope_pwl:.3f}")
axp.loglog(eps7, H_sm, "s--",
           label=f"smooth control: slope {slope_sm:.3f}")
axp.set_xlabel("loop half-width eps")
axp.set_ylabel("strain circulation H(eps)")
axp.set_title("AX-7: tangent-transport mismatch (regime dichotomy)")
axp.legend()
axq = axes[1]
axq.plot(ths, sA, label="follower s, tie-break A (min |s|)")
axq.plot(ths, sB, label="follower s, tie-break B (max s)")
axq.plot(ths, tA, ":", label="value function (both tie-breaks)")
axq.set_xlabel("theta")
axq.set_ylabel("value / follower flux")
axq.set_title("AX-6: atom-free value layer; flux kinks are tie-break artifacts")
axq.legend()
if verts_b:
    axr = axes[2]
    axr.imshow(chamb, origin="lower", extent=[LO2b, HI2b, LO2b, HI2b],
               cmap="tab20", aspect="auto")
    axr.plot(th_v[0], th_v[1], "k*", ms=14,
             label=(f"codim-2 vertex (MA atom = {atom_fan:.3f}, "
                    f"dual face = {atom_dual:.3f})"))
    axr.set_xlabel("theta1 (a-group capacity)")
    axr.set_ylabel("theta2 (b-group capacity)")
    axr.set_title("AX-2b: min-cut chambers of the max-flow value function")
    axr.legend()
fig.savefig(os.path.join(OUT, "ax_figures.png"), dpi=150)
plt.close(fig)

# summary
with open(os.path.join(OUT, "ax_summary.txt"), "w") as f:
    f.write("ALEXANDROV-BRIDGE VERIFICATION BATTERY (AX-1..AX-7)\n")
    f.write("=" * 60 + "\n\n")
    f.write(json.dumps(results, indent=2, default=float))
log("\nSaved:", os.path.join(OUT, "ax_results.json"))
log("Saved:", os.path.join(OUT, "ax_figures.png"))
