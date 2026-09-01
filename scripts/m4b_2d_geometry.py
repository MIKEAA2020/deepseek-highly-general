#!/usr/bin/env python3
"""
M4b -- Two-parameter static geometry of the lex-pFBA map in the
(glucose, O2) plane: the intrinsic curvature of the flux graph.

This tests the static layer of the DeepSeek "Active-Set Bridge
Conjecture" (external_audits/unifying object/deepseek formulation.txt)
and of its own proposed repair (finite-dimensional tangent transports).
The static map v(theta) is a single-valued continuous piecewise-affine
function, so:

  * the "affine-extension holonomy" of the original conjecture is
    exactly the identity for every closed loop (trivial by
    function-hood) -- verified here as the state-holonomy null;
  * the nontrivial intrinsic object is the DISCRETE GAUSS CURVATURE
    (angle defect) of the graph surface G(theta) = (theta, v(theta)),
    concentrated on codim-2 chamber crossings, computed with the
    minimal-rotation (unfolding) transport -- the corrected version of
    the conjecture's P_ij, which must be an invertible isometry fixing
    the shared edge (orthogonal projection, the file's own proposal,
    is NOT invertible and is not a connection);
  * flatness away from codim-2 strata: loops crossing interfaces in
    canceling pairs compose to the identity exactly.

Measurements per codim-2 crossing vertex theta_0 (the two interface
lines cross transversally, four chambers meet):
  1. quadrant probes and per-chamber Jacobians M_q (exact within
     chambers by piecewise affinity; verified by signature match);
  2. shared-edge consistency: the interface-tangential derivative
     images g_q(dA) agree across each shared edge to machine/solver
     precision (this is the well-definedness of the edge axis);
  3. corner angles alpha_q of the four chamber faces at theta_0 and
     the defect  K(theta_0) = 2*pi - sum_q alpha_q
     (flat control: identical M_q give exactly 0);
  4. per-edge dihedral kinks and the unfolding transport composition
     around the vertex: R_loop must act on the initial chamber frame
     as a rotation by the defect (discrete Gauss-Bonnet / Regge);
  5. size-independence: the defect is O(1) and independent of the
     probe scale delta (which is exactly why the conjecture's
     (1/eps^2) normalization cannot be right for this object);
  6. flat controls on 2-chamber cells: crossing one interface twice
     composes to the exact identity.

Also: a 1D cut through one vertex recomputes the M1-style D2 measure
(Jacobian-jump mass on interface crossings) at the vertex scale,
connecting the codim-1 measure to the codim-2 defect.

Usage: python m4b_2d_geometry.py [--grid-only | --full]
"""
import argparse
import json
import os
import sys
import time
import warnings

import numpy as np
import cobra
from cobra.util.solver import linear_reaction_coefficients

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_engine import LPEngine

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "m4")
os.makedirs(OUT, exist_ok=True)

TOL_M = 1e-6
TOL_B = 1e-7

GLC_LO, GLC_HI, N_GLC = 1.5, 10.0, 34
O2_LO, O2_HI, N_O2 = 1.0, 22.0, 34
MAX_VERTICES = 8


def build():
    model = cobra.io.load_json_model(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    co = linear_reaction_coefficients(model)
    c_bio = np.zeros(len(model.reactions))
    for r, c in co.items():
        c_bio[model.reactions.index(r)] = c
    rng = np.random.default_rng(20240901)     # same tie-break weights as M1/M3/M4a
    W = rng.uniform(0.5, 1.5, len(model.reactions))
    eng = LPEngine(model, W, c_bio)
    bio_id = list(co.keys())[0].id
    return eng, eng.index[bio_id]


def signature(v, lb, ub):
    material = np.abs(v) >= TOL_M
    at_bound = (np.abs(v - lb) <= TOL_B) | (np.abs(v - ub) <= TOL_B)
    return material, material & at_bound


class Solver:
    """Cached lex-pFBA solves over the (glc, O2) plane."""

    def __init__(self, eng, bio_idx):
        self.eng = eng
        self.bi = bio_idx
        self.i_glc = eng.index["EX_glc__D_e"]
        self.i_o2 = eng.index["EX_o2_e"]
        self.cache = {}
        self.n_solves = 0

    def at(self, glc, o2):
        key = (float(glc), float(o2))
        if key not in self.cache:
            lb = self.eng.lb0.copy()
            ub = self.eng.ub0.copy()
            lb[self.i_glc] = -key[0]
            lb[self.i_o2] = -key[1]
            out = self.eng.solve_lex(lb, ub, self.bi)
            self.n_solves += 1
            if out is None:
                self.cache[key] = (None, None, None, None, (lb, ub))
            else:
                v, mu, s2 = out
                s, b = signature(v, lb, ub)
                self.cache[key] = (v, mu, s, b, (lb, ub))
        return self.cache[key]


def sig_id(s, b):
    return hash((s.tobytes(), b.tobytes()))


# ------------------------------------------------------------- grid pass
def grid_pass(sv):
    glc_ax = np.linspace(GLC_LO, GLC_HI, N_GLC)
    o2_ax = np.linspace(O2_LO, O2_HI, N_O2)
    R = sv.eng.R
    n = N_GLC * N_O2
    V = np.full((N_GLC, N_O2, R), np.nan, np.float32)
    G = np.full((N_GLC, N_O2), np.nan)
    SIG = np.zeros((N_GLC, N_O2), np.int64)
    t0 = time.time()
    k = 0
    for i, g in enumerate(glc_ax):
        for j, o in enumerate(o2_ax):
            v, mu, s, b, _ = sv.at(g, o)
            if v is not None:
                V[i, j] = v
                G[i, j] = mu
                SIG[i, j] = sig_id(s, b)
            k += 1
            if k % 200 == 0:
                el = time.time() - t0
                print(f"  grid {k}/{n} ({el:.0f}s, {el / k:.2f}s/pt)",
                      flush=True)
    print(f"grid done: {np.isfinite(G).sum()}/{n} feasible, "
          f"{len(np.unique(SIG))} distinct signatures, "
          f"{sv.n_solves} solves, {time.time() - t0:.0f}s", flush=True)
    return glc_ax, o2_ax, V, G, SIG


def find_cells(SIG):
    """Classify 2x2 cells by signature multiplicity."""
    cells = {"cross": [], "pair": [], "single": [], "other": []}
    for i in range(N_GLC - 1):
        for j in range(N_O2 - 1):
            ids = [SIG[i, j], SIG[i + 1, j], SIG[i, j + 1],
                   SIG[i + 1, j + 1]]
            u = set(ids)
            cell = (i, j)
            if len(u) == 1:
                cells["single"].append(cell)
            elif len(u) == 2:
                cells["pair"].append(cell)
            elif len(u) == 4:
                cells["cross"].append(cell)
            else:
                cells["other"].append(cell)
    return cells


# ------------------------------------------------------- vertex analysis
def bisect_edge(sv, p, q, depth=8):
    """Signature-change point on the segment p->q (parameter vectors)."""
    sp = sv.at(*p)[0]
    if sp is None:
        return None
    sp = sig_id(*signature(sp, *_bounds_at(sv, p)))
    sq_id = None
    a, b = np.array(p, float), np.array(q, float)
    lo, hi = a.copy(), b.copy()
    for _ in range(depth):
        mid = 0.5 * (lo + hi)
        v = sv.at(*mid)[0]
        if v is None:
            return None
        s = sig_id(*signature(v, *_bounds_at(sv, mid)))
        if s == sp:
            lo = mid
        else:
            sq_id = s
            hi = mid
    return 0.5 * (lo + hi), (sp, sq_id)


def _bounds_at(sv, p):
    lb = sv.eng.lb0.copy()
    ub = sv.eng.ub0.copy()
    lb[sv.i_glc] = -p[0]
    lb[sv.i_o2] = -p[1]
    return lb, ub


def analyze_vertex(sv, cell, glc_ax, o2_ax, R):
    i, j = cell
    corners = [np.array([glc_ax[i], o2_ax[j]]),
               np.array([glc_ax[i + 1], o2_ax[j]]),
               np.array([glc_ax[i], o2_ax[j + 1]]),
               np.array([glc_ax[i + 1], o2_ax[j + 1]])]
    # boundary points on the four edges of the cell
    edges = [(corners[0], corners[1]), (corners[2], corners[3]),
             (corners[0], corners[2]), (corners[1], corners[3])]
    bpts = []
    for a, b in edges:
        if sig_id_at(sv, a) != sig_id_at(sv, b):
            r = bisect_edge(sv, tuple(a), tuple(b))
            if r is not None:
                bpts.append(r[0])
    if len(bpts) < 4:
        return dict(status="skip", reason=f"{len(bpts)} boundary points")
    if len(bpts) > 4:
        bpts = bpts[:4]
    # geometric pairing: the 4 boundary points must split into two
    # straight lines whose transverse intersection lies near the cell
    # (at a 4-sector crossing the two points of one line separate
    # DIFFERENT signature pairs, so pairing by sig-pair fails)
    pts = [np.asarray(p, float) for p in bpts]
    pairings = [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]
    center = np.mean([corners[0], corners[3]], axis=0)
    cw, ch = glc_ax[1] - glc_ax[0], o2_ax[1] - o2_ax[0]
    best = None
    for pr in pairings:
        P = [pts[pr[0][0]], pts[pr[0][1]]]
        Q = [pts[pr[1][0]], pts[pr[1][1]]]
        dP = P[1] - P[0]
        dQ = Q[1] - Q[0]
        if np.linalg.norm(dP) < 1e-9 or np.linalg.norm(dQ) < 1e-9:
            continue
        dP = dP / np.linalg.norm(dP)
        dQ = dQ / np.linalg.norm(dQ)
        if abs(float(dP @ dQ)) > 0.985:
            continue
        A = np.column_stack([dP, -dQ])
        try:
            t = np.linalg.solve(A, Q[0] - P[0])
        except np.linalg.LinAlgError:
            continue
        cand = P[0] + t[0] * dP
        if (glc_ax[i] - 0.6 * cw < cand[0] < glc_ax[i + 1] + 0.6 * cw
                and o2_ax[j] - 0.6 * ch < cand[1]
                < o2_ax[j + 1] + 0.6 * ch):
            dist = float(np.linalg.norm(cand - center))
            if best is None or dist < best[0]:
                best = (dist, dP, dQ, cand)
    if best is None:
        return dict(status="skip", reason="no valid line pairing")
    _, d1, d2, theta0 = best
    cosang = abs(float(d1 @ d2))
    if cosang > 0.985:
        return dict(status="skip", reason="near-parallel interfaces")

    dA = d1 / np.linalg.norm(d1)
    dB = d2 / np.linalg.norm(d2)

    # ---- quadrant probes + Jacobians (adaptive delta; affine-consistency)
    quad_dirs = [+dA + dB, -dA + dB, -dA - dB, +dA - dB]
    quads = ["I", "II", "III", "IV"]
    delta = 0.35 * min(cw, ch) * 3
    probes, Ms, sigs = None, None, None
    for attempt in range(6):
        delta *= 0.6
        probes = [theta0 + delta * qd for qd in quad_dirs]
        sigs = [sig_id_at(sv, p) for p in probes]
        if len(set(sigs)) == 4:
            break
    else:
        return dict(status="skip", reason="no 4-sector probe scale")
    if len(set(sigs)) != 4:
        return dict(status="skip", reason="no 4-sector probe scale")

    h = delta / 3.0
    Ms = []
    for _try in range(5):
        Ms = []
        for p in probes:
            M = fd_jacobian(sv, p, [dA, dB], h)
            if M is None:
                break
            Ms.append(M)
        if len(Ms) == 4:
            break
        h /= 2.0
    if len(Ms) != 4:
        return dict(status="skip", reason="no affine-consistent Jacobian")

    # ---- graph tangent vectors g(d) = (d, M d) in R^{m+2}
    def gvec(M, d):
        return np.concatenate([d, M @ d])

    # shared-edge consistency (4 edges: I/IV share +dA; I/II share +dB;
    # II/III share -dA; III/IV share -dB)
    shared = {
        "I_IV_dA": float(np.max(np.abs(Ms[0][:, 0] - Ms[3][:, 0]))),
        "I_II_dB": float(np.max(np.abs(Ms[1][:, 1] - Ms[0][:, 1]))),
        "II_III_dA": float(np.max(np.abs(Ms[1][:, 0] - Ms[2][:, 0]))),
        "III_IV_dB": float(np.max(np.abs(Ms[2][:, 1] - Ms[3][:, 1]))),
    }
    # note: M[:,0] is the dA-derivative, M[:,1] the dB-derivative;
    # g_I(dA) = (dA, M_I[:,0]); g_IV(dA) = (dA, M_IV[:,0]) etc.

    # ---- corner angles at theta0
    rays = {          # per quadrant: (ray1, ray2) as domain directions
        "I": (dA, dB), "II": (-dA, dB), "III": (-dA, -dB), "IV": (dA, -dB),
    }
    alphas = {}
    for q, M, (r1, r2) in zip(quads, Ms,
                              [rays[k] for k in quads]):
        a = gvec(M, r1)
        b = gvec(M, r2)
        alphas[q] = float(np.arccos(np.clip(
            float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))
    defect = 2 * np.pi - sum(alphas.values())

    # ---- unfolding transport composition around I -> IV -> III -> II -> I
    def make_rotation(axis, t_from, t_to):
        """Minimal rotation about unit axis k mapping t_from -> t_to
        (both unit and perpendicular to k).  Returns (k, u, v, phi) with
        the action  x -> x + (cos phi - 1)[(u.x)u + (v.x)v]
                     + sin phi [(u.x)v - (v.x)u].
        Works in any dimension n >= 3 (no cross product)."""
        k = axis / np.linalg.norm(axis)
        u = t_from - k * (k @ t_from)
        nu = np.linalg.norm(u)
        if nu < 1e-13:
            return None
        u = u / nu
        w = t_to - k * (k @ t_to) - u * (u @ t_to)
        nw = np.linalg.norm(w)
        if nw < 1e-13:
            if u @ t_to > 0:
                return (k, u, None, 0.0)      # identity
            # pi rotation: choose any v perpendicular to (k, u)
            X = np.eye(len(k))[:len(k)]
            for col in X:
                vv = col - k * (k @ col) - u * (u @ col)
                if np.linalg.norm(vv) > 1e-6:
                    v = vv / np.linalg.norm(vv)
                    return (k, u, v, np.pi)
            return None
        v = w / nw
        phi = float(np.arctan2(nw, u @ t_to))
        return (k, u, v, phi)

    def apply_rotation(rot, x):
        if rot is None:
            return x.copy()
        k, u, v, phi = rot
        if v is None and phi == 0.0:
            return x.copy()
        c, s = np.cos(phi), np.sin(phi)
        ux, vx = float(u @ x), float(v @ x)
        return x + (c - 1.0) * (ux * u + vx * v) + s * (ux * v - vx * u)

    def edge_transport(M_from, M_to, d_edge, d_other_from, d_other_to):
        """Rotation about the shared edge mapping the 'from' plane onto
        the 'to' plane.  d_edge: shared direction; d_other_*: the other
        basis direction of each face (pointing into that face)."""
        axis = gvec(M_from, d_edge)
        axis = axis / np.linalg.norm(axis)
        t_from = gvec(M_from, d_other_from)
        t_to = gvec(M_to, d_other_to)
        t_from = t_from - axis * (axis @ t_from)
        t_to = t_to - axis * (axis @ t_to)
        t_from /= np.linalg.norm(t_from)
        t_to /= np.linalg.norm(t_to)
        return make_rotation(axis, t_from, t_to)

    # transport maps the SAME domain direction's image to the new
    # face:  g_from(d_other) -> g_to(d_other)  (the unfolding rotation
    # about the shared edge; identity in the coplanar limit)
    rot_I_IV = edge_transport(Ms[0], Ms[3], dA, dB, dB)
    # IV -> III across -dB (shared: -dB; other direction: dA)
    rot_IV_III = edge_transport(Ms[3], Ms[2], -dB, dA, dA)
    # III -> II across -dA (shared: -dA; other direction: dB)
    rot_III_II = edge_transport(Ms[2], Ms[1], -dA, dB, dB)
    # II -> I across +dB (shared: +dB; other direction: dA)
    rot_II_I = edge_transport(Ms[1], Ms[0], dB, dA, dA)

    # apply the composed loop to I's orthonormal frame
    e1 = gvec(Ms[0], dA)
    e2 = gvec(Ms[0], dB)
    Q, _ = np.linalg.qr(np.column_stack([e1, e2]))
    V1 = Q.copy()
    for rot in [rot_I_IV, rot_IV_III, rot_III_II, rot_II_I]:
        V1 = np.column_stack([apply_rotation(rot, V1[:, c])
                              for c in range(V1.shape[1])])
    Qf = V1
    C = Q.T @ Qf                      # 2x2, should be a rotation
    theta_net = float(np.arctan2(C[1, 0], C[0, 0]))
    frame_planarity = float(np.linalg.norm(Qf - Q @ C))  # ~0 => stays in plane
    phi_I_IV = rot_I_IV[3] if rot_I_IV else 0.0
    phi_IV_III = rot_IV_III[3] if rot_IV_III else 0.0
    phi_III_II = rot_III_II[3] if rot_III_II else 0.0
    phi_II_I = rot_II_I[3] if rot_II_I else 0.0

    # ---- size-independence: recompute defect at delta/2
    delta2 = delta / 2
    probes2 = [theta0 + delta2 * qd for qd in quad_dirs]
    h2 = delta2 / 3.0
    Ms2 = []
    for p in probes2:
        M = fd_jacobian(sv, p, [dA, dB], h2)
        if M is None:
            break
        Ms2.append(M)
    defect2 = None
    if len(Ms2) == 4:
        al2 = []
        for M, (r1, r2) in zip(Ms2, [rays[k] for k in quads]):
            a = gvec(M, r1)
            b = gvec(M, r2)
            al2.append(np.arccos(np.clip(
                float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)),
                -1, 1)))
        defect2 = float(2 * np.pi - sum(al2))

    # ---- continuity (tear) diagnostic across the two interfaces near
    # the vertex: a jump of O(1) means the deterministic lex-pFBA
    # selection is TORN along this stratum (a measure-zero degeneracy
    # locus where A1 fails), which invalidates the fold/defect reading
    def jump_across(direction, s):
        n = np.array([-direction[1], direction[0]])
        vp = sv.at(*(theta0 + s * n))[0]
        vm = sv.at(*(theta0 - s * n))[0]
        if vp is None or vm is None:
            return None
        return float(np.max(np.abs(vp - vm)))

    s_jump = delta / 2
    jump_A = jump_across(dA, s_jump)
    jump_B = jump_across(dB, s_jump)

    kinks = dict(I_IV=phi_I_IV, IV_III=phi_IV_III,
                 III_II=phi_III_II, II_I=phi_II_I)

    # Jacobian jump magnitudes on the two interfaces (M1-object at the
    # vertex scale): jump of the transverse derivative
    jump_dB_I_II = float(np.linalg.norm(Ms[0][:, 1] - Ms[1][:, 1]))
    jump_dA_I_IV = float(np.linalg.norm(Ms[0][:, 0] - Ms[3][:, 0]))

    return dict(
        status="ok", cell=[int(i), int(j)],
        theta0=[float(theta0[0]), float(theta0[1])],
        dA=[float(x) for x in dA], dB=[float(x) for x in dB],
        delta=float(delta), h=float(h),
        quadrant_signatures=[int(x) for x in sigs],
        shared_edge_max_dev=shared,
        corner_angles={k: float(v) for k, v in alphas.items()},
        defect_rad=float(defect),
        defect_deg=float(np.degrees(defect)),
        defect_at_half_delta=(None if defect2 is None else float(defect2)),
        kink_angles_rad={k: float(v) for k, v in kinks.items()},
        transport_net_rotation_rad=theta_net,
        transport_net_rotation_deg=float(np.degrees(theta_net)),
        transport_frame_planarity=frame_planarity,
        transport_net_minus_defect_rad=float(theta_net + defect),
        continuity_jump_A=jump_A, continuity_jump_B=jump_B,
        jacobian_jumps=dict(dB_I_II=jump_dB_I_II, dA_I_IV=jump_dA_I_IV),
    )


def sig_id_at(sv, p):
    v = sv.at(*p)[0]
    if v is None:
        return None
    return sig_id(*signature(v, *_bounds_at(sv, p)))


def fd_jacobian(sv, center, dirs, h0, tol_rel=1e-7, n_try=6):
    """Finite-difference directional derivatives with a DIRECT affine-
    membership test: v is exactly affine within a chamber, so for three
    collinear points  v0 = (v+ + v-) / 2  to machine precision.  If the
    segment crosses an invisible chamber boundary the residual jumps to
    the Jacobian-jump scale and h is halved.  Returns the m x len(dirs)
    Jacobian or None."""
    v0 = sv.at(*center)[0]
    if v0 is None:
        return None
    scale = max(1.0, float(np.max(np.abs(v0))))
    h = h0
    for _ in range(n_try):
        cols = []
        ok = True
        for d in dirs:
            vp = sv.at(*(center + h * d))[0]
            vm = sv.at(*(center - h * d))[0]
            if vp is None or vm is None:
                return None
            resid = float(np.max(np.abs(vp + vm - 2 * v0)))
            if resid > tol_rel * scale:
                ok = False
                break
            cols.append((vp - vm) / (2 * h))
        if ok:
            return np.column_stack(cols)
        h *= 0.5
    return None


def fit_line(pts):
    pts = np.asarray(pts, float)
    if len(pts) < 2:
        return None, None
    if len(pts) == 2:
        d = pts[1] - pts[0]
    else:
        c = pts.mean(axis=0)
        _, _, vt = np.linalg.svd(pts - c)
        d = vt[0]
    if np.linalg.norm(d) < 1e-12:
        return None, None
    return d / np.linalg.norm(d), pts[0]


# ------------------------------------------------------------ flat control
def flat_control(sv, cell, glc_ax, o2_ax):
    """2-chamber cell: crossing the interface twice must compose to the
    exact identity (pairwise cancellation = flatness off codim-2)."""
    i, j = cell
    a = np.array([glc_ax[i], o2_ax[j]])
    b = np.array([glc_ax[i + 1], o2_ax[j]])
    c = np.array([glc_ax[i], o2_ax[j + 1]])
    d = np.array([glc_ax[i + 1], o2_ax[j + 1]])
    ids = [sig_id_at(sv, p) for p in [a, b, c, d]]
    if len(set(ids)) != 2:
        return None
    # orient: bottom|top split (a,b vs c,d) or left|right (a,c vs b,d)
    if ids[0] == ids[1] and ids[2] == ids[3]:
        lo_pts, hi_pts = [a, b], [c, d]
        edge_pairs = [(a, c), (b, d)]     # left and right edges separate
    elif ids[0] == ids[2] and ids[1] == ids[3]:
        lo_pts, hi_pts = [a, c], [b, d]
        edge_pairs = [(a, b), (c, d)]     # bottom and top edges separate
    else:
        return None
    # boundary points on the two separating edges
    bp = []
    for p, q in edge_pairs:
        if sig_id_at(sv, p) != sig_id_at(sv, q):
            r = bisect_edge(sv, tuple(p), tuple(q))
            if r is not None:
                bp.append(r[0])
    if len(bp) < 2:
        return None
    dI, pI = fit_line(bp)
    if dI is None:
        return None
    dI = dI / np.linalg.norm(dI)
    # Jacobians of the two chambers near EACH boundary point,
    # with the affine-consistency guard (chamber membership is tested
    # directly, not through the coarse operational signature)
    def jac_at(center, dirs):
        return fd_jacobian(sv, center, dirs,
                           0.2 * min(glc_ax[1] - glc_ax[0],
                                     o2_ax[1] - o2_ax[0]))

    nI = np.array([-dI[1], dI[0]])          # transverse to the interface
    s_in = 0.15 * min(glc_ax[1] - glc_ax[0], o2_ax[1] - o2_ax[0])

    def gvec(M, d):
        return np.concatenate([d, M @ d])

    def make_rotation(axis, t_from, t_to):
        k = axis / np.linalg.norm(axis)
        u = t_from - k * (k @ t_from)
        nu = np.linalg.norm(u)
        if nu < 1e-13:
            return None
        u = u / nu
        w = t_to - k * (k @ t_to) - u * (u @ t_to)
        nw = np.linalg.norm(w)
        if nw < 1e-13:
            return (k, u, None, 0.0) if u @ t_to > 0 else None
        v = w / nw
        return (k, u, v, float(np.arctan2(nw, u @ t_to)))

    def apply_rotation(rot, x, sign=1.0):
        if rot is None:
            return x.copy()
        k, u, v, phi = rot
        if v is None:
            return x.copy()
        p = sign * phi
        c, s = np.cos(p), np.sin(p)
        ux, vx = float(u @ x), float(v @ x)
        return x + (c - 1.0) * (ux * u + vx * v) + s * (ux * v - vx * u)

    sig_lo = ids[0] if ids[0] == ids[1] else ids[0]
    sig_hi = ids[2] if ids[0] == ids[1] else ids[1]
    results = []
    for bpt in bp[:2]:
        c_lo, c_hi = bpt - s_in * nI, bpt + s_in * nI
        M_lo = jac_at(c_lo, [dI, nI])
        M_hi = jac_at(c_hi, [dI, nI])
        if M_lo is None or M_hi is None:
            return None
        axis = gvec(M_lo, dI)
        axis = axis / np.linalg.norm(axis)
        t_lo = gvec(M_lo, nI) - axis * (axis @ gvec(M_lo, nI))
        t_hi = gvec(M_hi, nI) - axis * (axis @ gvec(M_hi, nI))
        nl, nh = np.linalg.norm(t_lo), np.linalg.norm(t_hi)
        if nl < 1e-12 or nh < 1e-12:
            return None
        rot = make_rotation(axis, t_lo / nl, t_hi / nh)
        if rot is None:
            return None
        shared = float(np.max(np.abs(M_lo @ dI - M_hi @ dI)))
        results.append((rot, shared))

    (rot1, shared1), (rot2, shared2) = results
    # constancy of the interface transport between the two crossings:
    # same axis direction and same angle (the flatness mechanism)
    axis_dev = float(np.linalg.norm(rot1[0] - rot2[0]))
    phi_dev = abs(rot1[3] - rot2[3])
    # loop: cross at bp[0] (lo->hi), return at bp[1] (hi->lo)
    M_lo0 = jac_at(bp[0] - s_in * nI, [dI, nI])
    if M_lo0 is None:
        return None
    x0 = gvec(M_lo0, np.array([1.0, 0.0]) * 0.0 + dI)
    x1 = apply_rotation(rot1, x0, +1.0)
    x2 = apply_rotation(rot2, x1, -1.0)
    resid = float(np.linalg.norm(x2 - x0)) / max(1.0, float(np.linalg.norm(x0)))
    phi = rot1[3]
    return dict(cell=[int(i), int(j)],
                phi_rad=float(phi), phi_deg=float(np.degrees(phi)),
                loop_identity_rel_dev=resid,
                axis_constancy=axis_dev, phi_constancy=float(phi_dev),
                shared_edge_max_dev=max(shared1, shared2))


# ------------------------------------------------------ T-junction mode
def analyze_tjunction(sv, cell, glc_ax, o2_ax):
    """3-boundary-point cell = T-junction: a codim-1 stratum terminating
    on another.  Uniform formulation: the SPINE line crosses two
    opposite cell edges; the TERMINATOR line crosses one of the other
    edges and ends at the junction.  For a CONTINUOUS piecewise-affine
    map the terminating stratum must be Jacobian-flat ('mask-type':
    support/materiality event without flux kink) -- the no-loose-kinks
    lemma -- which forces corner defect exactly 0 and identity
    holonomy.  This analysis verifies that prediction (and flags tears
    if it fails)."""
    i, j = cell
    corners = dict(BL=np.array([glc_ax[i], o2_ax[j]]),
                   BR=np.array([glc_ax[i + 1], o2_ax[j]]),
                   TL=np.array([glc_ax[i], o2_ax[j + 1]]),
                   TR=np.array([glc_ax[i + 1], o2_ax[j + 1]]))
    ids = {k: sig_id_at(sv, p) for k, p in corners.items()}
    edges = [("bottom", "BL", "BR"), ("top", "TL", "TR"),
             ("left", "BL", "TL"), ("right", "BR", "TR")]
    opp = {"bottom": "top", "top": "bottom", "left": "right",
           "right": "left"}
    bpts = {}
    for ename, a, b in edges:
        if ids[a] != ids[b]:
            r = bisect_edge(sv, tuple(corners[a]), tuple(corners[b]))
            if r is None:
                return None
            bpts[ename] = (r[0], frozenset((ids[a], ids[b])))
    if len(bpts) != 3:
        return None
    # find the opposite-edge pair = the spine
    spine_edges, term_edge = None, None
    for e in ("bottom", "top", "left", "right"):
        if e in bpts and opp[e] in bpts:
            spine_edges = (e, opp[e])
            term_edge = [x for x in bpts if x not in (e, opp[e])][0]
            break
    if spine_edges is None:
        return None
    s1, pair1 = bpts[spine_edges[0]]
    s2, pair2 = bpts[spine_edges[1]]
    t1, tpair = bpts[term_edge]
    common = pair1 & pair2
    if len(common) != 1:
        return None
    common = next(iter(common))
    dS = s2 - s1
    if np.linalg.norm(dS) < 1e-9:
        return None
    dS = dS / np.linalg.norm(dS)
    nS = np.array([-dS[1], dS[0]])
    # the terminator edge lies in the non-common half-plane
    if float(nS @ (t1 - s1)) < 0:
        nS = -nS
    # second terminator point: search beyond the terminator edge
    cw, ch = glc_ax[1] - glc_ax[0], o2_ax[1] - o2_ax[0]
    t2 = None
    if term_edge in ("top", "bottom"):
        step = 1 if term_edge == "top" else -1
        for dj in (1, 2):
            jj = j + step * dj
            if not (0 <= jj < len(o2_ax)):
                break
            pa, pb = (np.array([glc_ax[i], o2_ax[jj]]),
                      np.array([glc_ax[i + 1], o2_ax[jj]]))
            sa, sb = sig_id_at(sv, pa), sig_id_at(sv, pb)
            if sa != sb and frozenset((sa, sb)) == tpair:
                r = bisect_edge(sv, tuple(pa), tuple(pb))
                if r is not None:
                    t2 = r[0]
                    break
    else:
        step = 1 if term_edge == "right" else -1
        for di in (1, 2):
            ii = i + step * di
            if not (0 <= ii < len(glc_ax)):
                break
            pa, pb = (np.array([glc_ax[ii], o2_ax[j]]),
                      np.array([glc_ax[ii], o2_ax[j + 1]]))
            sa, sb = sig_id_at(sv, pa), sig_id_at(sv, pb)
            if sa != sb and frozenset((sa, sb)) == tpair:
                r = bisect_edge(sv, tuple(pa), tuple(pb))
                if r is not None:
                    t2 = r[0]
                    break
    if t2 is None:
        return None
    dT_line = t2 - t1
    if np.linalg.norm(dT_line) < 1e-9:
        return None
    dT_line = dT_line / np.linalg.norm(dT_line)
    # junction = spine x terminator line
    A = np.column_stack([dS, -dT_line])
    try:
        tvec = np.linalg.solve(A, t1 - s1)
    except np.linalg.LinAlgError:
        return None
    if abs(float(dS @ dT_line)) > 0.98:
        return None
    theta0 = s1 + tvec[0] * dS
    if not (glc_ax[i] - 0.5 * cw < theta0[0] < glc_ax[i + 1] + 0.5 * cw
            and o2_ax[j] - 0.5 * ch < theta0[1]
            < o2_ax[j + 1] + 0.5 * ch):
        return None
    dT = theta0 - t1
    if np.linalg.norm(dT) < 1e-9:
        return None
    dT = dT / np.linalg.norm(dT)          # from junction toward term edge
    if float(dT @ nS) < 0:                # must point into non-common side
        dT = -dT
    # expected signatures from the corner positions in the (dS, nS) frame
    sig_expect = {}
    for k, c in corners.items():
        d = c - theta0
        a, b = float(d @ dS), float(d @ nS)
        if b < 0:
            sig_expect.setdefault("S", ids[k])
        elif a < 0:
            sig_expect.setdefault("A", ids[k])
        else:
            sig_expect.setdefault("B", ids[k])
    # probes (adaptive delta)
    delta = 0.3 * min(cw, ch) * 3
    probes = None
    for _ in range(6):
        delta *= 0.6
        probes = dict(A=theta0 + delta * (-dS + nS),
                      B=theta0 + delta * (dS + nS),
                      S=theta0 - delta * nS)
        if all(sig_id_at(sv, probes[k]) == sig_expect.get(k)
               for k in ("A", "B", "S")):
            break
    else:
        return None
    h = delta / 3
    M = {}
    for _ in range(5):
        M = {}
        okk = True
        for k, pp in probes.items():
            J = fd_jacobian(sv, pp, [dS, dT], h)
            if J is None:
                okk = False
                break
            M[k] = J
        if okk:
            break
        h /= 2
    if len(M) != 3:
        return None

    def gvec(J, d):
        return np.concatenate([d, J @ d])

    # ---- the no-loose-kinks consistency checks
    flat_terminating = float(np.max(np.abs(
        M["A"] @ dT - M["B"] @ dT)))          # must vanish (theorem)
    common_dS_A = float(np.max(np.abs(M["A"] @ dS - M["S"] @ dS)))
    common_dS_B = float(np.max(np.abs(M["B"] @ dS - M["S"] @ dS)))
    kink_AS = float(np.linalg.norm(M["A"] @ dT - M["S"] @ dT))
    kink_BS = float(np.linalg.norm(M["B"] @ dT - M["S"] @ dT))

    def angle(a, b):
        return float(np.arccos(np.clip(
            float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))

    al_A = angle(gvec(M["A"], -dS), gvec(M["A"], dT))
    al_B = angle(gvec(M["B"], dS), gvec(M["B"], dT))
    al_S = angle(gvec(M["S"], -dS), gvec(M["S"], dS))      # = pi exactly
    defect = 2 * np.pi - (al_A + al_B + al_S)

    # ---- transport loop A -> B -> S -> A (identity expected)
    def make_rotation(axis, t_from, t_to):
        k = axis / np.linalg.norm(axis)
        u = t_from - k * (k @ t_from)
        nu = np.linalg.norm(u)
        if nu < 1e-13:
            return None
        u = u / nu
        w = t_to - k * (k @ t_to) - u * (u @ t_to)
        nw = np.linalg.norm(w)
        if nw < 1e-13:
            return (k, u, None, 0.0) if u @ t_to > 0 else None
        v = w / nw
        return (k, u, v, float(np.arctan2(nw, u @ t_to)))

    def apply_rotation(rot, x):
        if rot is None:
            return x.copy()
        k, u, v, phi = rot
        if v is None:
            return x.copy()
        c, s = np.cos(phi), np.sin(phi)
        ux, vx = float(u @ x), float(v @ x)
        return x + (c - 1.0) * (ux * u + vx * v) + s * (ux * v - vx * u)

    def edge_rot(J_from, J_to, d_edge, d_other):
        axis = gvec(J_from, d_edge)
        axis = axis / np.linalg.norm(axis)
        tf = gvec(J_from, d_other)
        tt = gvec(J_to, d_other)
        tf = tf - axis * (axis @ tf)
        tt = tt - axis * (axis @ tt)
        return make_rotation(axis, tf / np.linalg.norm(tf),
                             tt / np.linalg.norm(tt))

    r_AB = edge_rot(M["A"], M["B"], dT, dS)     # terminator ray (flat)
    r_BS = edge_rot(M["B"], M["S"], dS, dT)     # +dS spine ray
    r_SA = edge_rot(M["S"], M["A"], -dS, dT)    # -dS spine ray
    e1 = gvec(M["A"], dS)
    e2 = gvec(M["A"], dT)
    Q, _ = np.linalg.qr(np.column_stack([e1, e2]))
    V1 = Q.copy()
    for rot in [r_AB, r_BS, r_SA]:
        V1 = np.column_stack([apply_rotation(rot, V1[:, c])
                              for c in range(V1.shape[1])])
    Cm = Q.T @ V1
    theta_net = float(np.arctan2(Cm[1, 0], Cm[0, 0]))
    planarity = float(np.linalg.norm(V1 - Q @ Cm))

    return dict(
        status="ok", mode="T-junction", cell=[int(i), int(j)],
        theta0=[float(theta0[0]), float(theta0[1])],
        delta=float(delta),
        flat_terminating_stratum_max_dev=flat_terminating,
        common_dS_max_dev=max(common_dS_A, common_dS_B),
        kink_AS_dT=kink_AS, kink_BS_dT=kink_BS,
        corner_angles_rad=dict(A=al_A, B=al_B, S=al_S),
        defect_rad=float(defect), defect_deg=float(np.degrees(defect)),
        transport_net_rotation_rad=theta_net,
        transport_net_rotation_deg=float(np.degrees(theta_net)),
        transport_frame_planarity=planarity)


# ------------------------------------------------------------- 1D cut
def cut_through_vertex(sv, theta0, dB, span=0.8, npts=49):
    ts = np.linspace(-span, span, npts)
    pts = [theta0 + t * dB for t in ts]
    vs = [sv.at(*p)[0] for p in pts]
    ok = [v is not None for v in vs]
    if not all(ok):
        return None
    V = np.array(vs)
    dt = ts[1] - ts[0]
    d2 = (V[2:] - 2 * V[1:-1] + V[:-2]) / dt ** 2
    d2n = np.linalg.norm(d2, axis=1)
    sigs = [sig_id_at(sv, p) for p in pts]
    events = [k for k in range(1, npts - 1)
              if sigs[k - 1] != sigs[k] or sigs[k] != sigs[k + 1]]
    total = float((d2n ** 2).sum())
    on = float(sum(d2n[k - 1] ** 2 for k in events)) if events else 0.0
    return dict(span=span, n_points=npts, dt=float(dt),
                n_events=len(events),
                event_positions=[float(ts[k]) for k in events],
                D2_total=total,
                D2_mass_on_events=(on / total if total > 0 else None),
                D2_max=float(d2n.max()),
                D2_median_off=float(np.median(
                    [d2n[k - 1] for k in range(1, npts - 1)
                     if k not in events]) if events else np.median(d2n)))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-only", action="store_true")
    args = ap.parse_args()
    t00 = time.time()
    eng, bi = build()
    sv = Solver(eng, bi)

    grid_file = os.path.join(OUT, "m4b_grid.npz")
    if os.path.exists(grid_file):
        z = np.load(grid_file, allow_pickle=True)
        glc_ax, o2_ax = z["glc_ax"], z["o2_ax"]
        SIG, G = z["SIG"], z["G"]
        print(f"loaded cached grid ({len(np.unique(SIG))} signatures)")
    else:
        glc_ax, o2_ax, V, G, SIG = grid_pass(sv)
        np.savez_compressed(grid_file, glc_ax=glc_ax, o2_ax=o2_ax,
                            SIG=SIG, G=G,
                            V=np.asarray(V, np.float32))
    if args.grid_only:
        return

    cells = find_cells(SIG)
    print(f"cells: {len(cells['cross'])} cross, {len(cells['pair'])} pair, "
          f"{len(cells['single'])} single, {len(cells['other'])} other",
          flush=True)

    # ---- local refinement: sub-grid the structurally rich cells to
    # resolve crossings the coarse grid cannot see (dense low-glc/low-O2
    # corner).  Each sub-lattice is 5x5 per cell (21 new solves).
    refine_cells = cells["cross"] + cells["other"]
    refined_candidates = []
    n_ref = 0
    for cell in refine_cells[:20]:
        i, j = cell
        sub_glc = np.linspace(glc_ax[i], glc_ax[i + 1], 5)
        sub_o2 = np.linspace(o2_ax[j], o2_ax[j + 1], 5)
        sub_sig = np.zeros((5, 5), np.int64)
        for a in range(5):
            for b in range(5):
                sub_sig[a, b] = sig_id_at(sv, np.array([sub_glc[a],
                                                        sub_o2[b]]))
                n_ref += 0 if (a % 4 == 0 and b % 4 == 0) else 1
        for a in range(4):
            for b in range(4):
                u = set([sub_sig[a, b], sub_sig[a + 1, b],
                         sub_sig[a, b + 1], sub_sig[a + 1, b + 1]])
                if len(u) >= 4:
                    refined_candidates.append((sub_glc, sub_o2,
                                                (a, b), (i, j)))
    print(f"refinement: {len(refine_cells)} cells sub-gridded, "
          f"{len(refined_candidates)} refined 4-sig sub-cells", flush=True)

    # ---- vertex analyses; prefer candidates AWAY from the fan origin
    # (the low-glc/low-O2 corner has chamber wedges thinner than any
    # probe scale -- crossings there are under-resolved by design).
    # Refined candidates keep their parent for dedup.
    far = [(sg, so, c, parent) for sg, so, c, parent
           in refined_candidates + [(glc_ax, o2_ax, c, c)
                                    for c in cells["cross"]
                                    + cells["other"]]]
    far.sort(key=lambda t: -(t[3][0] + t[3][1]))
    near = [(sg, so, c, parent) for sg, so, c, parent
            in refined_candidates + [(glc_ax, o2_ax, c, c)
                                     for c in cells["cross"]]]
    chosen = []
    seen_parents = set()
    for ax_pair in far[:4] + near[:6]:
        sg, so, cell, parent = ax_pair
        if parent in seen_parents:
            continue
        seen_parents.add(parent)
        chosen.append((sg, so, cell))
    print(f"analyzing {len(chosen)} candidate vertices", flush=True)
    vertices = []
    for sg, so, cell in chosen:
        t0 = time.time()
        r = analyze_vertex(sv, cell, sg, so, eng.R)
        r["analysis_time_s"] = round(time.time() - t0, 1)
        vertices.append(r)
        st = r.get("status")
        if st == "ok":
            print(f"  vertex {cell}: theta0=({r['theta0'][0]:.3f},"
                  f"{r['theta0'][1]:.3f}) defect={r['defect_deg']:.4f} deg,"
                  f" transport net={r['transport_net_rotation_deg']:.4f} deg,"
                  f" shared-edge max dev="
                  f"{max(r['shared_edge_max_dev'].values()):.2e}",
                  flush=True)
        else:
            print(f"  vertex {cell}: skip ({r['reason']})", flush=True)

    # ---- T-junction analyses for the 3-boundary-point cells
    tj = []
    for cell in cells["other"]:
        if len(tj) >= 6:
            break
        r = analyze_tjunction(sv, cell, glc_ax, o2_ax)
        if r is not None:
            tj.append(r)
            print(f"  T-junction {cell}: theta0=({r['theta0'][0]:.3f},"
                  f"{r['theta0'][1]:.3f}) defect={r['defect_deg']:+.2e} deg, "
                  f"flat-terminating dev={r['flat_terminating_stratum_max_dev']:.2e}, "
                  f"common-dS dev={r['common_dS_max_dev']:.2e}, "
                  f"kinks AS/BS={r['kink_AS_dT']:.3g}/{r['kink_BS_dT']:.3g}, "
                  f"transport={r['transport_net_rotation_deg']:+.2e} deg, "
                  f"planarity={r['transport_frame_planarity']:.2e}",
                  flush=True)

    # ---- flat controls
    rng = np.random.default_rng(20260901)
    pair_cells = cells["pair"]
    controls = []
    if pair_cells:
        picks = list(rng.choice(len(pair_cells),
                                size=min(12, len(pair_cells)),
                                replace=False))
        for idx in picks:
            r = flat_control(sv, pair_cells[idx], glc_ax, o2_ax)
            if r is not None:
                controls.append(r)
        print(f"flat controls: {len(controls)} verified", flush=True)

    # ---- 1D cut through the first OK vertex
    cut = None
    for r in vertices:
        if r.get("status") == "ok":
            cut = cut_through_vertex(
                sv, np.array(r["theta0"]), np.array(r["dB"]))
            if cut is not None:
                cut["theta0"] = r["theta0"]
            break

    n_ok = sum(1 for r in vertices if r.get("status") == "ok")
    ok_verts = [r for r in vertices if r.get("status") == "ok"]
    summary = dict(
        experiment="M4b two-parameter static geometry (glc, O2) plane",
        model="iML1515", grid=[N_GLC, N_O2],
        grid_ranges=[[GLC_LO, GLC_HI], [O2_LO, O2_HI]],
        n_signatures=int(len(np.unique(SIG))),
        cells=dict(cross=len(cells["cross"]), pair=len(cells["pair"]),
                   single=len(cells["single"]), other=len(cells["other"])),
        n_vertices_analyzed=len(vertices), n_vertices_ok=n_ok,
        vertices=vertices, t_junctions=tj, flat_controls=controls,
        cut=cut,
        state_holonomy_note=(
            "v(theta) is a single-valued function of the bounds: every "
            "closed loop in the (glc, O2) plane returns to the identical "
            "flux vector (the affine-extension holonomy of the original "
            "conjecture is trivially the identity); the nontrivial static "
            "object is the angle defect of the flux graph at codim-2 "
            "crossings"),
        total_lex_solves=sv.n_solves,
        runtime_s=round(time.time() - t00, 1))
    with open(os.path.join(OUT, "m4b_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    if ok_verts:
        print("\n=== vertex results ===")
        for r in ok_verts:
            print(f"theta0=({r['theta0'][0]:.3f},{r['theta0'][1]:.3f}) "
                  f"defect={r['defect_deg']:+.4f} deg "
                  f"(delta/2: "
                  f"{r['defect_at_half_delta'] is not None and round(np.degrees(r['defect_at_half_delta']), 4)})"
                  f" transport={r['transport_net_rotation_deg']:+.4f} deg "
                  f"net-minus-defect={np.degrees(r['transport_net_minus_defect_rad']):+.2e} deg "
                  f"planarity={r['transport_frame_planarity']:.2e}")
        print("\n=== flat controls ===")
        for c in controls[:6]:
            print(f"cell {c['cell']}: kink={c['phi_deg']:+.4f} deg, "
                  f"loop identity rel dev={c['loop_identity_rel_dev']:.2e}, "
                  f"axis constancy={c['axis_constancy']:.2e}, "
                  f"phi constancy={c['phi_constancy']:.2e}, "
                  f"shared edge dev={c['shared_edge_max_dev']:.2e}")
        if cut:
            print(f"\n1D cut: {cut['n_events']} events, D2 mass on events "
                  f"= {cut['D2_mass_on_events']}, "
                  f"D2 max = {cut['D2_max']:.3e}")
    print(f"\ndone in {time.time() - t00:.0f}s "
          f"({sv.n_solves} lex solves) -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
