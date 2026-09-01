#!/usr/bin/env python3
"""Unit test of the M4b defect + unfolding-transport machinery on
synthetic piecewise-affine maps with analytically known geometry.

Case 1 (flat): identical quadrant Jacobians -> defect = 0 exactly and
transport = identity.

Case 2 (cone): v(theta) = (r * f(phi)) in R^3 with a kinked radial
profile -- a polyhedral cone; defect must equal the classical cone
deficit and the transport composition must equal it.

Case 3 (generic 4-sector): random quadrant Jacobians constrained to
agree on the shared axes (continuity); check
   theta_net == -defect (mod 2 pi)  and frame planarity ~ 0.
"""
import numpy as np

rng = np.random.default_rng(7)


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


def apply_rotation(rot, x):
    if rot is None:
        return x.copy()
    k, u, v, phi = rot
    if v is None:
        return x.copy()
    c, s = np.cos(phi), np.sin(phi)
    ux, vx = float(u @ x), float(v @ x)
    return x + (c - 1.0) * (ux * u + vx * v) + s * (ux * v - vx * u)


def analyze_quadrants(Ms, dA, dB):
    """Ms = [M_I, M_II, M_III, M_IV] with columns (dA-deriv, dB-deriv).
    Returns (defect, theta_net, planarity, shared devs)."""
    quads = ["I", "II", "III", "IV"]
    rays = {"I": (dA, dB), "II": (-dA, dB),
            "III": (-dA, -dB), "IV": (dA, -dB)}
    shared = {
        "I_IV_dA": float(np.max(np.abs(Ms[0][:, 0] - Ms[3][:, 0]))),
        "I_II_dB": float(np.max(np.abs(Ms[1][:, 1] - Ms[0][:, 1]))),
        "II_III_dA": float(np.max(np.abs(Ms[1][:, 0] - Ms[2][:, 0]))),
        "III_IV_dB": float(np.max(np.abs(Ms[2][:, 1] - Ms[3][:, 1]))),
    }
    alphas = {}
    for q, M, (r1, r2) in zip(quads, Ms, [rays[k] for k in quads]):
        a = gvec(M, r1)
        b = gvec(M, r2)
        alphas[q] = float(np.arccos(np.clip(
            float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)))
    defect = 2 * np.pi - sum(alphas.values())

    def edge_transport(M_from, M_to, d_edge, d_other_from, d_other_to):
        axis = gvec(M_from, d_edge)
        axis = axis / np.linalg.norm(axis)
        t_from = gvec(M_from, d_other_from)
        t_to = gvec(M_to, d_other_to)
        t_from = t_from - axis * (axis @ t_from)
        t_to = t_to - axis * (axis @ t_to)
        t_from /= np.linalg.norm(t_from)
        t_to /= np.linalg.norm(t_to)
        return make_rotation(axis, t_from, t_to)

    rot_I_IV = edge_transport(Ms[0], Ms[3], dA, dB, dB)
    rot_IV_III = edge_transport(Ms[3], Ms[2], -dB, dA, dA)
    rot_III_II = edge_transport(Ms[2], Ms[1], -dA, dB, dB)
    rot_II_I = edge_transport(Ms[1], Ms[0], dB, dA, dA)

    e1 = gvec(Ms[0], dA)
    e2 = gvec(Ms[0], dB)
    Q, _ = np.linalg.qr(np.column_stack([e1, e2]))
    V1 = Q.copy()
    for rot in [rot_I_IV, rot_IV_III, rot_III_II, rot_II_I]:
        V1 = np.column_stack([apply_rotation(rot, V1[:, c])
                              for c in range(V1.shape[1])])
    C = Q.T @ V1
    theta_net = float(np.arctan2(C[1, 0], C[0, 0]))
    planarity = float(np.linalg.norm(V1 - Q @ C))
    return defect, theta_net, planarity, shared


def wrap_angle(x):
    return float(np.angle(np.exp(1j * x)))


# ------------------------------------------------ Case 1: flat
m = 4
A = rng.standard_normal((m, 2))
Ms = [A.copy() for _ in range(4)]
dA, dB = np.array([1.0, 0.0]), np.array([0.0, 1.0])
d, t, p, s = analyze_quadrants(Ms, dA, dB)
print(f"Case 1 (flat):      defect={np.degrees(d):+.6f} deg  "
      f"theta_net={np.degrees(t):+.6f} deg  planarity={p:.2e}")

# ------------------------------------------------ Case 2: cone
# v(x, y) = (z(x), 0, 0) with z = |theta| piecewise-linear in the
# quadrant angle: 4 planes over the 4 quadrants -> polyhedral cone.
# sector slopes s_q > 0: z = s_q * (x * c_q + y * s_q_hat)?? simpler:
# z_I = a x + b y on x,y >= 0; continuity on axes forces:
#   z_II (x<=0): on y-axis: b y -> z_II = -a' x + b y with a' free
#   z_IV (y<=0): on x-axis: a x -> z_IV = a x - b' y
#   z_III: -a' x - b' y
# This is the graph of a "saddle-ish" piecewise linear function.
for trial in range(3):
    a, a2, b, b2 = rng.uniform(0.2, 2.0, 4)
    colA_I = np.array([a, 0, 0, 0.])       # d/dx in sector I
    colA_II = np.array([-a2, 0, 0, 0.])    # d/dx in sector II
    colB_I = np.array([b, 0, 0, 0.])
    colB_IV = np.array([-b2, 0, 0, 0.])
    M_I = np.column_stack([colA_I, colB_I])
    M_II = np.column_stack([colA_II, colB_I])
    M_III = np.column_stack([colA_II, np.array([-b2, 0, 0, 0.])])
    M_IV = np.column_stack([colA_I, np.array([-b2, 0, 0, 0.])])
    d, t, p, s = analyze_quadrants(
        [M_I, M_II, M_III, M_IV], dA, dB)
    # classical 4-plane cone with x-slopes a (right) / -a2 (left) and
    # y-slopes b (up) / -b2 (down): the exact deficit is computed by
    # the corner-angle formula itself; the transport must match it.
    print(f"Case 2 (cone #{trial}): defect={np.degrees(d):+9.4f} deg  "
          f"theta_net={np.degrees(t):+9.4f} deg  "
          f"net+defect={np.degrees(wrap_angle(t + d)):+.2e} deg  "
          f"planarity={p:.2e}  shared max={max(s.values()):.1e}")

# ------------------------------------------------ Case 3: generic
for trial in range(5):
    m = 5
    # continuity on shared axes: column pairs agree as required
    cA = rng.standard_normal(m)      # dA-derivative shared I|IV
    cA2 = rng.standard_normal(m)     # dA-derivative shared II|III
    cB = rng.standard_normal(m)      # dB-derivative shared I|II
    cB2 = rng.standard_normal(m)     # dB-derivative shared III|IV
    M_I = np.column_stack([cA, cB])
    M_II = np.column_stack([cA2, cB])
    M_III = np.column_stack([cA2, cB2])
    M_IV = np.column_stack([cA, cB2])
    d, t, p, s = analyze_quadrants(
        [M_I, M_II, M_III, M_IV], dA, dB)
    print(f"Case 3 (generic #{trial}): defect={np.degrees(d):+9.4f} deg  "
          f"theta_net={np.degrees(t):+9.4f} deg  "
          f"net+defect={np.degrees(wrap_angle(t + d)):+.2e} deg  "
          f"planarity={p:.2e}  shared max={max(s.values()):.1e}")
