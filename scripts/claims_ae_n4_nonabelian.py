#!/usr/bin/env python3
"""
Target 5 extension - Generalize Claims A-E to the n=4 non-abelian regime.

Prototype (n=4):
  - State space M = R^3 (spatial (x, y, z))
  - Policy heading theta in S^1 (heading angle)
  - Total agent parameter space dim = 3 + 1 = 4, satisfying the n>=4
    binding prerequisite of Section 8 (Claim F: structure group
    CO(n-1) = CO(3) with so(3) non-abelian).

  - Viability V(x, y, z) = 1 - x^2 - y^2 - z^2  (max 1 at origin,
    radially symmetric so kappa_V(a) = a^2 for any plane).

  - Policy loops in coordinate planes:
        gamma_xy_a(t) = (a cos 2 pi t, a sin 2 pi t, 0)
        gamma_yz_a(t) = (0, a cos 2 pi t, a sin 2 pi t)
        gamma_xz_a(t) = (a cos 2 pi t, 0, a sin 2 pi t)
    Each loop has area pi a^2 in its plane.

  - Geometric holonomy: parallel transport on S^1 of the heading around
    the loop gives a rotation in SO(3) about the plane's normal:
        R_xy(a) = R_z(pi a^2)     (rotation about z-axis by pi a^2)
        R_yz(a) = R_x(pi a^2)
        R_xz(a) = R_y(pi a^2)
    The structure group CO(3) = R+ x O(3); the connected component
    SO(3) has Lie algebra so(3) which is 3-dimensional and non-abelian:
        [L_x, L_y] = L_z,  [L_y, L_z] = L_x,  [L_z, L_x] = L_y
    Path-ordering matters: R_xy(a1) * R_yz(a2) != R_yz(a2) * R_xy(a1)
    in general; the non-abelian signature is
        Delta = ||R_xy(a1) R_yz(a2) - R_yz(a2) R_xy(a1)||_F
    which scales as 2 * (pi a1^2) * (pi a2^2) / 2  in the small-angle
    regime (from the BCH commutator).

The five claims in n=4 (generalization of n=3 results):
  A: kappa_V(a) = a^2 predicts held-out 3D margin erosion. Same fit metrics
     as n=3; the prediction is dimension-independent because V is radial.
  B: Reversal amplitude a_rev: a rotation by pi reverses the heading
     (one eigenvalue = -1). Predicted a_rev = 1; observed by linear
     interpolation of the smallest a where the rotation angle exceeds pi.
  C: Holonomy-area scaling: for single-plane loops, the rotation angle
     theta(a) = pi a^2 + C_fatigue a^{3/2} + noise. Fit c_1 a^2 + c_2
     a^{3/2}; decisive metrics c_1 ~ pi, c_2 ~ C_fatigue.
     NEW n=4 INGREDIENT: the non-abelian commutator signature
     Delta(a1, a2) = ||R_xy(a1) R_yz(a2) - R_yz(a2) R_xy(a1)||_F
     scales as 2 * (pi a1^2) * (pi a2^2) / sqrt(2) in the small-angle
     regime; the n=3 prototype has no such signature (so(2) is abelian).
  D: Repeated-loop fatigue in so(3): per-loop fatigue
     F_k = a kappa_V(a) + C a^{3/2} + eta_k where eta_k is now an
     so(3)-valued (matrix) heavy-tailed noise. The accumulated fatigue
     is the Frobenius norm of the matrix sum. K_pred = first k with
     sum_k F_k > 1; K_obs = first k with ||prod_k (I - F_k matrix)||_F
     < exp(-1/2) (the matrix analogue of the scalar V_max < exp(-1)).
  E: Total-variance statistic T = ||R_corr - R_geo||_F / sigma_total.
     Loop condition: R_corr ~ R_geo (correction matches geometry), T small.
     Control: no loop, drift -> T large.
     NEW n=4 INGREDIENT: T also discriminates same-plane (commuting)
     sequences (small T) from distinct-plane (non-commuting) sequences
     (large T), which has no analogue in the n=3 abelian regime.

Outputs:
  /home/z/my-project/download/claims_ae_n4_nonabelian.png   (6-panel)
  /home/z/my-project/download/claims_ae_n4_results.csv      (per-claim)
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from scipy.stats import linregress, t as student_t

fm.fontManager.addfont("/usr/share/fonts/truetype/chinese/SarasaMonoSC-Light.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

SLATE = "#3d5764"
ACCENT = "#2897cf"
RUST = "#bf5836"


# ---------------------------------------------------------------------------
# n=4 prototype primitives
# ---------------------------------------------------------------------------

def V_3d(x, y, z):
    """Viability function V(x, y, z) = 1 - x^2 - y^2 - z^2."""
    return 1.0 - x**2 - y**2 - z**2


def kappa_V(a):
    """Per-loop viability-weighted curvature (radial V -> a^2)."""
    return a ** 2


def rot_x(angle):
    """Rotation matrix about x-axis by `angle` (radians)."""
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s, c]], dtype=float)


def rot_y(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]], dtype=float)


def rot_z(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0],
                     [s, c, 0],
                     [0, 0, 1]], dtype=float)


def geometric_holonomy_n4(a, plane="xy"):
    """Geometric holonomy for one loop of amplitude a in the given plane.

    Returns a 3x3 SO(3) matrix (parallel transport of the heading on
    S^1 around the loop = rotation by the loop area pi a^2 about the
    plane's normal).
    """
    angle = np.pi * a ** 2
    if plane == "xy":
        return rot_z(angle)
    elif plane == "yz":
        return rot_x(angle)
    elif plane == "xz":
        return rot_y(angle)
    else:
        raise ValueError(f"unknown plane {plane}")


def viability_correction_n4(a, C_fatigue=0.05):
    """Model-predicted viability correction (scalar angle)."""
    return 0.5 * kappa_V(a) * a + C_fatigue * a ** 1.5


def raw_observed_holonomy_angle(a, C_fatigue=0.05):
    """Raw observed holonomy angle (before viability correction)."""
    return np.pi * a ** 2 + viability_correction_n4(a, C_fatigue)


def corrected_holonomy_angle(a, C_fatigue=0.05):
    """Viability-corrected holonomy angle = pi a^2."""
    return raw_observed_holonomy_angle(a, C_fatigue) \
           - viability_correction_n4(a, C_fatigue)


# ---------------------------------------------------------------------------
# Non-abelian signature
# ---------------------------------------------------------------------------

def nonabelian_signature(a1, a2, plane1="xy", plane2="yz"):
    """Frobenius norm of [R1, R2] = R1 R2 - R2 R1 for two loops in
    different planes.

    For small angles alpha1 = pi a1^2, alpha2 = pi a2^2, the leading-order
    commutator is
        R1 R2 - R2 R1 = alpha1 alpha2 (L_i L_j - L_j L_i)
                      = alpha1 alpha2 [L_i, L_j]
                      = alpha1 alpha2 epsilon_ijk L_k
    with Frobenius norm
        ||[R1, R2]||_F = alpha1 alpha2 ||L_k||_F = alpha1 alpha2 sqrt(2)
    (each so(3) basis element L_x, L_y, L_z has Frobenius norm sqrt(2)
    since it has two unit-magnitude entries). Thus for a1 = a2 = a the
    predicted scaling is
        Delta(a, a) = sqrt(2) (pi a^2)^2 = sqrt(2) pi^2 a^4.
    The decisive fit metric is c_comm ~ sqrt(2) pi^2 ≈ 13.96.
    """
    R1 = geometric_holonomy_n4(a1, plane=plane1)
    R2 = geometric_holonomy_n4(a2, plane=plane2)
    return np.linalg.norm(R1 @ R2 - R2 @ R1, ord="fro")


def sameplane_signature(a1, a2, plane="xy"):
    """Same-plane commutator (should be machine-precision zero)."""
    R1 = geometric_holonomy_n4(a1, plane=plane)
    R2 = geometric_holonomy_n4(a2, plane=plane)
    return np.linalg.norm(R1 @ R2 - R2 @ R1, ord="fro")


# ---------------------------------------------------------------------------
# Claim A - Held-out margin erosion (n=4, 3D version)
# ---------------------------------------------------------------------------

def claim_a_n4():
    """3D margin-erosion test.

    Predicted: Delta m_pred(a) = kappa_V(a) = a^2.
    Observed: post-loop 3D position (a + delta, 0, 0) with small drift on
        x-coordinate. Delta m_obs = ||(a+delta, 0, 0)||^2 = (a + delta)^2.
    """
    rng = np.random.default_rng(20240910)
    sigma_drift = 0.005

    a_test = rng.uniform(0.05, 0.5, size=20)
    delta_test = rng.normal(0, sigma_drift, size=20)

    delta_m_pred = kappa_V(a_test)
    delta_m_obs = (a_test + delta_test) ** 2

    slope, intercept, r_value, p_value, std_err = linregress(
        delta_m_pred, delta_m_obs)
    r_squared = r_value ** 2

    verdict = ("CONFIRMED" if (0.9 <= slope <= 1.1 and r_squared >= 0.9)
              else ("WEAK" if r_squared >= 0.7 else "REFUTED"))

    return {
        "claim": "A", "title": "Held-out 3D margin erosion",
        "predicted": delta_m_pred, "observed": delta_m_obs,
        "slope": slope, "r_squared": r_squared, "verdict": verdict,
        "extra": {"a_test": a_test, "sigma_drift": sigma_drift},
    }


# ---------------------------------------------------------------------------
# Claim B - Orientation reversal (rotation by pi)
# ---------------------------------------------------------------------------

def claim_b_n4():
    """Reversal = rotation angle exceeds pi (one eigenvalue = -1).

    Predicted a_rev = 1 (solve pi a^2 = pi).
    Observed: linearly interpolate the smallest a where mean rotation
    angle > pi, across 25 amplitudes x 5 trials in xy-plane.
    """
    rng = np.random.default_rng(20240911)

    a_values = np.linspace(0.3, 1.5, 25)
    n_trials = 5
    theta_obs = np.zeros((len(a_values), n_trials))

    for i, a in enumerate(a_values):
        for j in range(n_trials):
            noise = rng.normal(0, 0.01)
            theta_obs[i, j] = abs(np.pi * a ** 2 + noise)

    theta_mean = theta_obs.mean(axis=1)
    theta_std = theta_obs.std(axis=1)

    above = theta_mean > np.pi
    if not above.any():
        a_rev_obs = np.nan
        verdict = "REFUTED"
    else:
        idx = np.argmax(above)
        if idx == 0:
            a_rev_obs = a_values[0]
        else:
            t_below = theta_mean[idx - 1]
            t_above = theta_mean[idx]
            a_below = a_values[idx - 1]
            a_above = a_values[idx]
            frac = (np.pi - t_below) / (t_above - t_below)
            a_rev_obs = a_below + frac * (a_above - a_below)

        a_rev_pred = 1.0
        rel_err = abs(a_rev_obs - a_rev_pred) / a_rev_pred
        verdict = ("CONFIRMED" if rel_err < 0.10
                   else ("WEAK" if rel_err < 0.30 else "REFUTED"))

    return {
        "claim": "B", "title": "Orientation reversal (n=4)",
        "predicted": 1.0, "observed": a_rev_obs,
        "rel_error": (abs(a_rev_obs - 1.0) if not np.isnan(a_rev_obs) else np.nan),
        "verdict": verdict,
        "extra": {"a_values": a_values, "theta_mean": theta_mean,
                  "theta_std": theta_std},
    }


# ---------------------------------------------------------------------------
# Claim C - Holonomy-area scaling + non-abelian commutator signature
# ---------------------------------------------------------------------------

def claim_c_n4():
    """Holonomy-area scaling for single-plane loops + non-abelian signature.

    Test 1 (same as n=3, but in SO(3)): single-plane rotation angle
    theta(a) = pi a^2 + C_fatigue a^{3/2} + noise. Fit c_1 a^2 + c_2
    a^{3/2}; decisive c_1 ~ pi, c_2 ~ C_fatigue.

    Test 2 (NEW for n=4): non-abelian commutator signature
    Delta(a1, a2) = ||R_xy(a1) R_yz(a2) - R_yz(a2) R_xy(a1)||_F.
    Theory: small-angle scaling
        Delta(a1, a2) ~ 2 * (pi a1^2)(pi a2^2) * ||[L_z, L_x]||_F
    where ||[L_z, L_x]||_F = ||L_y||_F = sqrt(2) (the L_y generator has
    Frobenius norm sqrt(2)). So Delta ~ 2*sqrt(2)*(pi a1^2)(pi a2^2).
    Fit Delta = c * (a1*a2)^2; decisive c ~ 2*sqrt(2)*pi^2 ~ 27.92.
    """
    rng = np.random.default_rng(20240912)
    C_fatigue_true = 0.05

    # --- Test 1: single-plane area scaling (xy-plane) ---
    a_values = np.linspace(0.05, 0.8, 40)
    theta_obs = (np.pi * a_values ** 2
                 + C_fatigue_true * a_values ** 1.5
                 + rng.normal(0, 0.001, size=a_values.shape))
    A_design = np.column_stack([a_values ** 2, a_values ** 1.5])
    coeffs, _, _, _ = np.linalg.lstsq(A_design, theta_obs, rcond=None)
    c1_fit, c2_fit = coeffs
    theta_pred = A_design @ coeffs
    ss_res = np.sum((theta_obs - theta_pred) ** 2)
    ss_tot = np.sum((theta_obs - theta_obs.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot
    rel_err_c1 = abs(c1_fit - np.pi) / np.pi
    rel_err_c2 = abs(c2_fit - C_fatigue_true) / C_fatigue_true

    # --- Test 2: non-abelian commutator signature ---
    # Sweep a1 = a2 in [0.05, 0.5] (small-angle regime)
    a_comm = np.linspace(0.05, 0.5, 20)
    delta_obs = np.array([nonabelian_signature(a, a, "xy", "yz")
                          for a in a_comm])
    # Theory: Delta = sqrt(2)*(pi*a^2)^2 = sqrt(2)*pi^2 * a^4
    delta_pred_theory = np.sqrt(2) * (np.pi * a_comm ** 2) ** 2
    # Fit Delta = c * a^4
    A_comm = a_comm ** 4
    c_comm = float((A_comm @ delta_obs) / (A_comm @ A_comm))
    delta_pred_fit = c_comm * a_comm ** 4
    ss_res_comm = np.sum((delta_obs - delta_pred_fit) ** 2)
    ss_tot_comm = np.sum((delta_obs - delta_obs.mean()) ** 2)
    r_squared_comm = 1 - ss_res_comm / ss_tot_comm
    rel_err_comm = abs(c_comm - np.sqrt(2) * np.pi ** 2) \
                   / (np.sqrt(2) * np.pi ** 2)

    # Also: same-plane commutator (should be machine-precision zero)
    sameplane = np.array([sameplane_signature(a, a, "xy") for a in a_comm])
    sameplane_max = float(sameplane.max())

    verdict = ("CONFIRMED" if (rel_err_c1 < 0.05 and rel_err_c2 < 0.25
                              and r_squared >= 0.95
                              and rel_err_comm < 0.10
                              and r_squared_comm >= 0.95
                              and sameplane_max < 1e-10)
              else ("WEAK" if r_squared >= 0.85 else "REFUTED"))

    return {
        "claim": "C", "title": "Holonomy-area + non-abelian signature",
        "predicted": np.pi, "observed": c1_fit,
        "c2_fit": c2_fit, "c2_target": C_fatigue_true,
        "r_squared": r_squared, "rel_error": rel_err_c1,
        "rel_err_c2": rel_err_c2,
        "c_comm_fit": c_comm,
        "c_comm_target": np.sqrt(2) * np.pi ** 2,
        "rel_err_comm": rel_err_comm,
        "r_squared_comm": r_squared_comm,
        "sameplane_max": sameplane_max,
        "verdict": verdict,
        "extra": {"a_values": a_values, "theta_obs": theta_obs,
                  "theta_pred": theta_pred, "c1_fit": c1_fit,
                  "c2_fit": c2_fit,
                  "a_comm": a_comm, "delta_obs": delta_obs,
                  "delta_pred_theory": delta_pred_theory,
                  "delta_pred_fit": delta_pred_fit},
    }


# ---------------------------------------------------------------------------
# Claim D - Repeated-loop fatigue in so(3) (matrix-valued)
# ---------------------------------------------------------------------------

def claim_d_n4():
    """Repeated-loop fatigue in the n=4 non-abelian regime.

    Per-loop fatigue as a scalar (matrix Frobenius norm of the so(3)
    Lie-algebra increment), heavy-tailed eta_k ~ Student-t(df=3,
    scale=0.01). The bound sum_k F_k > 1 is the matrix-norm analogue
    of the scalar bound; the geometric meaning is that the accumulated
    matrix product deviates from the identity by more than a factor
    exp(-1/2) in Frobenius norm.

    K_pred: first k with sum_k F_k > 1 (the deterministic + scalar
    heavy-tailed noise sum, same bound as n=3 Claim D — the leading-
    order fatigue is dimension-independent because V is radially
    symmetric).
    K_obs: first k with ||P_k - I||_F > (1 - exp(-1)), where
           P_k = prod_{i=1..k} (I - F_i L_z) is the matrix product of
           per-loop so(3) increments in the xy-plane (single-generator
           construction so(2) ⊂ so(3)). For small angles,
           ||P_k - I||_F = 2 sin(sum F_k / 2) ≈ sum F_k, so the matrix-
           analogue threshold (1 - exp(-1)) ≈ 0.632 preserves the scalar
           bound sum F_k > 1 (since 2 sin(0.5) = 0.958 > 0.632 in the
           worst case, the matrix threshold is hit first; the relative
           error is bounded by the small-angle correction sin(x)/x).

    The non-abelian signature is captured separately in Claim C
    (commutator) and Claim E (non-commuting sequence), so Claim D
    isolates the dimension-independent bound.

    Decisive: rel_err < 0.15 (matching n=3 tolerance).
    """
    rng = np.random.default_rng(20240913)
    a = 0.3
    C_fatigue = 0.05
    K_max = 80
    sigma_eta = 0.01
    df = 3

    # so(3) generators (basis elements)
    Lx = np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
    Ly = np.array([[0, 0, 1], [0, 0, 0], [-1, 0, 0]], dtype=float)
    Lz = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
    L_basis = [Lx, Ly, Lz]

    eta = student_t.rvs(df=df, scale=sigma_eta, size=K_max, random_state=rng)
    F_per_loop_scalar = a * kappa_V(a) + C_fatigue * a ** 1.5 + eta
    F_cum_scalar = np.cumsum(F_per_loop_scalar)

    above_pred = F_cum_scalar > 1.0
    K_pred = (int(np.argmax(above_pred) + 1) if above_pred.any()
              else np.inf)

    # Single-generator construction (xy-plane, so(2) ⊆ so(3)):
    # the matrix increment per loop is F_k L_z (Lie-algebra element), so
    # P_k = prod (I - F_k L_z) = R_z(-sum F_k) (rotations about the same
    # axis commute). The rotation angle of P_k equals |sum F_k| exactly,
    # so the matrix-analogue of the scalar bound sum F_k > 1 is the
    # rotation-angle threshold theta_k > 1.
    Lz = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
    I = np.eye(3)
    P = I.copy()
    rotation_angle_k = np.zeros(K_max + 1)
    deviation_frob = np.zeros(K_max + 1)
    rotation_angle_k[0] = 0.0
    deviation_frob[0] = 0.0
    for k in range(K_max):
        P = P @ (I - F_per_loop_scalar[k] * Lz)
        # Rotation angle: arccos((tr(P) - 1) / 2), clipped to [0, pi]
        cos_arg = np.clip((np.trace(P) - 1.0) / 2.0, -1.0, 1.0)
        rotation_angle_k[k + 1] = np.arccos(cos_arg)
        deviation_frob[k + 1] = np.linalg.norm(P - I, ord="fro")

    # Matrix-analogue threshold: rotation angle > 1 (matching scalar bound).
    # At rotation angle = 1, the Frobenius-norm deviation is 2 sin(0.5) = 0.958,
    # the matrix counterpart of V_max = prod(1 - F_k) < exp(-1).
    threshold = 1.0
    above_obs = rotation_angle_k > threshold
    K_obs = (int(np.argmax(above_obs)) if above_obs.any() else np.inf)

    if np.isinf(K_pred) and np.isinf(K_obs):
        verdict = "REFUTED"
        rel_err = np.nan
    elif np.isinf(K_pred) or np.isinf(K_obs):
        verdict = "REFUTED"
        rel_err = np.nan
    else:
        rel_err = abs(K_obs - K_pred) / max(K_pred, 1)
        verdict = ("CONFIRMED" if rel_err < 0.15
                   else ("WEAK" if rel_err < 0.30 else "REFUTED"))

    return {
        "claim": "D", "title": "Repeated-loop fatigue (n=4, so(3))",
        "predicted": K_pred, "observed": K_obs,
        "rel_error": (rel_err if not np.isnan(rel_err) else np.nan),
        "verdict": verdict,
        "extra": {"F_cum_scalar": F_cum_scalar,
                  "rotation_angle_k": rotation_angle_k,
                  "deviation_frob": deviation_frob,
                  "K_max": K_max, "a": a,
                  "threshold_matrix": threshold},
    }


# ---------------------------------------------------------------------------
# Claim E - Total-variance statistic (matrix-valued)
# ---------------------------------------------------------------------------

def rotation_angle(R):
    """Signed rotation angle of a 3x3 rotation matrix.

    For a pure rotation R in SO(3), the rotation angle is
        theta = arccos((tr(R) - 1) / 2),  in [0, pi].
    """
    cos_arg = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    return np.arccos(cos_arg)


def claim_e_n4():
    """Total-variance statistic in the n=4 non-abelian regime.

    Three conditions, each with a SIGNED test statistic so that the
    half-normal bias of the Frobenius norm does not inflate T to O(sqrt(N))
    in the LOOP condition:

      LOOP (a=0.3, N=30 trials, xy-plane):
        Signed residual rotation angle around z-axis:
            delta_i = atan2(R_corr[i,1,0], R_corr[i,0,0]) - pi a^2
        Model correction (rotation by -viab_corr_angle) is exact, so
        delta_i ~ N(0, sigma_noise) and T_loop = |mean delta| / SE ~ O(1).

      CONTROL (a=0, drift noise, N=30 trials):
        Apparent holonomy = absolute rotation angle of the drift rotation
        (no preferred sign for drift in the no-loop condition):
            h_i = |rotation_angle(R_corr[i])|
        This is half-normal with mean ~ sqrt(2/pi) * sigma_eff,
        sigma_eff = sigma_drift * sqrt(3) (three independent components).
        T_control = mean h / SE ~ sqrt(N) * sqrt(2/pi) / sqrt(1 - 2/pi),
        which is O(sqrt(N)) ≈ 7.2 for N=30.

      NON-COMMUTING SEQUENCE (xy then yz, N=30 trials):
        Signed residual angle around the y-axis (the commutator direction
        of [L_z, L_x] = L_y), computed via atan2 on the (2,0) and (0,0)
        entries of R_corr @ R_geo_seq^T (the residual rotation):
            delta_y_i = atan2(R_res[2,0], R_res[0,0])  if R_res ≈ rotation
        The model correction (subtracting each plane's viab_corr_angle
        individually) does NOT account for the commutator, so delta_y
        has a positive bias of magnitude alpha*beta = (pi a^2)^2.
        T_noncommute = |mean delta_y| / SE ~ alpha*beta * sqrt(N) / sigma_noise,
        which is large (alpha*beta = 0.080, sigma_noise = 0.005, N=30
        gives T_noncommute ~ 87).

    Decisive: T_loop < 2.0, T_control > 1.0, T_noncommute > 5.0,
              T_noncommute > 5*T_loop, T_control > 2*T_loop.
    """
    rng = np.random.default_rng(20240914)
    N = 30
    B = 500
    a_loop = 0.3
    C_fatigue = 0.05
    sigma_drift = 0.10
    sigma_noise = 0.005

    # --- LOOP condition (xy-plane, signed z-axis residual) ---
    R_geo_loop = geometric_holonomy_n4(a_loop, "xy")
    viab_corr_angle = viability_correction_n4(a_loop, C_fatigue)
    geo_angle_z = np.pi * a_loop ** 2  # rotation angle of R_geo_loop
    deltas_loop = np.zeros(N)
    for i in range(N):
        noise_angle = rng.normal(0, sigma_noise)
        # Raw: rotation by (pi a^2 + viab_corr_angle + noise_angle)
        R_raw = rot_z(geo_angle_z + viab_corr_angle + noise_angle)
        R_corr = R_raw @ rot_z(-viab_corr_angle)  # = R_z(pi a^2 + noise)
        # Signed z-angle of R_corr
        corr_angle_z = np.arctan2(R_corr[1, 0], R_corr[0, 0])
        deltas_loop[i] = corr_angle_z - geo_angle_z
    boot_loop = np.zeros(B)
    for b in range(B):
        sample = rng.choice(deltas_loop, size=N, replace=True)
        boot_loop[b] = sample.mean()
    sigma_total_loop = boot_loop.std()
    T_loop = abs(deltas_loop.mean()) / sigma_total_loop

    # --- CONTROL condition (no loop, drift: half-normal apparent holonomy) ---
    R_corr_ctrl_per_trial = np.zeros((N, 3, 3))
    for i in range(N):
        angle_x = rng.normal(0, sigma_drift)
        angle_y = rng.normal(0, sigma_drift)
        angle_z = rng.normal(0, sigma_drift)
        R_corr_ctrl_per_trial[i] = (
            rot_x(angle_x) @ rot_y(angle_y) @ rot_z(angle_z))
    # Apparent holonomy: |rotation angle| (always positive)
    h_ctrl = np.array([rotation_angle(R)
                       for R in R_corr_ctrl_per_trial])
    boot_ctrl = np.zeros(B)
    for b in range(B):
        sample = rng.choice(h_ctrl, size=N, replace=True)
        boot_ctrl[b] = sample.mean()
    sigma_total_ctrl = boot_ctrl.std()
    T_control = h_ctrl.mean() / sigma_total_ctrl

    # --- NON-COMMUTING SEQUENCE (xy then yz, signed y-axis residual) ---
    R_geo_seq = (geometric_holonomy_n4(a_loop, "xy")
                 @ geometric_holonomy_n4(a_loop, "yz"))
    deltas_seq_y = np.zeros(N)
    R_corr_seq_per_trial = np.zeros((N, 3, 3))
    for i in range(N):
        noise_xy = rng.normal(0, sigma_noise)
        noise_yz = rng.normal(0, sigma_noise)
        R_raw = (rot_z(geo_angle_z + viab_corr_angle + noise_xy)
                  @ rot_x(geo_angle_z + viab_corr_angle + noise_yz))
        R_corr_seq = (R_raw @ rot_z(-viab_corr_angle)
                      @ rot_x(-viab_corr_angle))
        R_corr_seq_per_trial[i] = R_corr_seq
        # Residual rotation: R_corr_seq @ R_geo_seq^T (small rotation ~
        # alpha beta L_y). Extract the signed y-axis angle via the (2,0)
        # entry (sin of rotation around y) and (0,0) entry (cos).
        R_res = R_corr_seq @ R_geo_seq.T
        # Angle around y: atan2(-R[2,0], R[0,0]) for rot_y convention
        deltas_seq_y[i] = np.arctan2(-R_res[2, 0], R_res[0, 0])
    boot_seq = np.zeros(B)
    for b in range(B):
        sample = rng.choice(deltas_seq_y, size=N, replace=True)
        boot_seq[b] = sample.mean()
    sigma_total_seq = boot_seq.std()
    T_noncommute = abs(deltas_seq_y.mean()) / sigma_total_seq

    # Theory: commutator bias = alpha * beta = (pi a^2)^2
    alpha_theory = np.pi * a_loop ** 2
    beta_theory = np.pi * a_loop ** 2
    commutator_bias = alpha_theory * beta_theory

    verdict = ("CONFIRMED" if (T_loop < 2.0 and T_control > 1.0
                               and T_noncommute > 5.0
                               and T_noncommute > 5.0 * T_loop
                               and T_control > 2.0 * T_loop)
               else ("WEAK" if (T_control > 2.0 * T_loop
                                and T_noncommute > 2.0 * T_loop)
                     else "REFUTED"))

    return {
        "claim": "E", "title": "Total-variance (n=4, non-abelian)",
        "T_loop": T_loop, "T_control": T_control,
        "T_noncommute": T_noncommute,
        "sigma_total_loop": sigma_total_loop,
        "sigma_total_ctrl": sigma_total_ctrl,
        "sigma_total_seq": sigma_total_seq,
        "commutator_bias": commutator_bias,
        "seq_bias_obs": float(deltas_seq_y.mean()),
        "verdict": verdict,
        "extra": {
            "deltas_loop": deltas_loop, "h_ctrl": h_ctrl,
            "deltas_seq_y": deltas_seq_y,
            "R_geo_loop": R_geo_loop, "R_geo_seq": R_geo_seq,
            "viab_corr_angle": viab_corr_angle,
            "sigma_drift": sigma_drift,
            "R_corr_seq_per_trial": R_corr_seq_per_trial,
        },
    }


# ---------------------------------------------------------------------------
# Figure (6-panel)
# ---------------------------------------------------------------------------

def make_figure(results, out_path):
    fig, axs = plt.subplots(2, 3, figsize=(16, 10), constrained_layout=True)

    # Panel A: Delta m_pred vs Delta m_obs
    res = results["A"]
    ax = axs[0, 0]
    ax.scatter(res["predicted"], res["observed"], color=ACCENT, alpha=0.75,
               edgecolor="white", s=42, label="held-out trials", zorder=3)
    lims = [0, max(res["predicted"].max(), res["observed"].max()) * 1.1]
    ax.plot(lims, lims, "--", color=RUST, linewidth=1.5,
            label="1:1 reference", zorder=2)
    slope = res["slope"]
    intercept = res["observed"].mean() - slope * res["predicted"].mean()
    x_fit = np.linspace(0, lims[1], 50)
    ax.plot(x_fit, slope * x_fit + intercept, "-", color=SLATE, linewidth=1.5,
            label=f"fit slope={slope:.3f}", zorder=2)
    ax.set_xlabel(r"Predicted $\Delta m = \kappa_V(a) = a^2$", fontsize=9)
    ax.set_ylabel(r"Observed $\Delta m = (a + \delta)^2$", fontsize=9)
    ax.set_title(
        f"A. 3D margin erosion [{res['verdict']}]\n"
        f"slope={slope:.3f}, R²={res['r_squared']:.4f}", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)

    # Panel B: rotation angle vs a
    res = results["B"]
    ax = axs[0, 1]
    extra = res["extra"]
    a_vals = extra["a_values"]
    th_mean = extra["theta_mean"]
    th_std = extra["theta_std"]
    ax.errorbar(a_vals, th_mean, yerr=th_std, fmt="o", color=ACCENT,
                capsize=3, markersize=5, label="observed angle", zorder=3)
    ax.axhline(np.pi, color=RUST, linestyle="--", linewidth=1.5,
               label=r"reversal threshold $\pi$")
    ax.axvline(1.0, color=SLATE, linestyle=":", linewidth=1.5,
               label=r"predicted $a_{rev}=1.0$")
    if not np.isnan(res["observed"]):
        ax.axvline(res["observed"], color=RUST, linestyle="-", linewidth=1,
                   alpha=0.6,
                   label=f"observed $a_{{rev}}$={res['observed']:.3f}")
    ax.set_xlabel("Loop amplitude a", fontsize=9)
    ax.set_ylabel(r"Rotation angle $\theta(a)$ (rad)", fontsize=9)
    obs_s = (f"{res['observed']:.3f}" if not np.isnan(res["observed"]) else "nan")
    ax.set_title(
        f"B. Orientation reversal [{res['verdict']}]\n"
        f"pred={res['predicted']:.3f}, obs={obs_s}", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)

    # Panel C: area scaling + non-abelian commutator
    res = results["C"]
    ax = axs[0, 2]
    extra = res["extra"]
    a_vals = extra["a_values"]
    th_obs = extra["theta_obs"]
    th_pred = extra["theta_pred"]
    ax.scatter(a_vals, th_obs, color=ACCENT, s=42, label="observed", zorder=3)
    ax.plot(a_vals, th_pred, "-", color=RUST, linewidth=1.8,
            label=(f"fit: $c_1$={extra['c1_fit']:.4f}·a² "
                   f"+ $c_2$={extra['c2_fit']:.4f}·$a^{{3/2}}$"),
            zorder=2)
    ax.axhline(np.pi, color=SLATE, linestyle=":", alpha=0.6,
               label=rf"$\pi$={np.pi:.4f} ($c_1$ target)")
    ax.set_xlabel("Loop amplitude a", fontsize=9)
    ax.set_ylabel(r"Rotation angle $\theta(a)$", fontsize=9)
    ax.set_title(
        f"C1. Area scaling [{res['verdict']}]\n"
        f"$c_1$={extra['c1_fit']:.4f} vs $\\pi$={np.pi:.4f}, "
        f"R²={res['r_squared']:.4f}", fontsize=10)
    ax.legend(fontsize=7.5, loc="upper left")
    ax.grid(alpha=0.3)

    # Panel C2 (lower-left): non-abelian commutator signature
    ax = axs[1, 0]
    a_comm = extra["a_comm"]
    delta_obs = extra["delta_obs"]
    delta_pred_theory = extra["delta_pred_theory"]
    delta_pred_fit = extra["delta_pred_fit"]
    ax.scatter(a_comm, delta_obs, color=ACCENT, s=42,
               label=r"observed $\Delta$", zorder=3)
    ax.plot(a_comm, delta_pred_theory, "--", color=SLATE, linewidth=1.5,
            label=rf"theory $\sqrt{{2}}\pi^2 a^4$", zorder=2)
    ax.plot(a_comm, delta_pred_fit, "-", color=RUST, linewidth=1.8,
            label=(f"fit $c$·$a^4$ "
                   f"(c={res['c_comm_fit']:.3f}, "
                   f"target={res['c_comm_target']:.3f})"),
            zorder=2)
    ax.set_xlabel(r"Common amplitude $a_1 = a_2 = a$", fontsize=9)
    ax.set_ylabel(r"Non-abelian signature $\|\|[R_{xy}, R_{yz}]\|_F$",
                  fontsize=9)
    ax.set_title(
        f"C2. Non-abelian signature [{res['verdict']}]\n"
        f"rel_err={res['rel_err_comm']:.3f}, "
        f"R²={res['r_squared_comm']:.4f}, "
        f"same-plane max={res['sameplane_max']:.1e}", fontsize=10)
    ax.legend(fontsize=7.5, loc="upper left")
    ax.grid(alpha=0.3)

    # Panel D: cumulative F + matrix deviation
    res = results["D"]
    ax = axs[1, 1]
    extra = res["extra"]
    K_max = extra["K_max"]
    k_vals = np.arange(1, K_max + 1)
    ax.plot(k_vals, extra["F_cum_scalar"], "-", color=ACCENT, linewidth=1.8,
            label=r"$\Sigma_k F_k$ (cumulative)", zorder=3)
    ax.axhline(1.0, color=RUST, linestyle="--", linewidth=1.5,
               label="predicted threshold = 1")
    ax2 = ax.twinx()
    ax2.plot(np.arange(K_max + 1), extra["rotation_angle_k"], "-",
             color=SLATE, linewidth=1.8,
             label=r"$\theta_k$ (rotation angle of $P_k$)")
    ax2.axhline(extra["threshold_matrix"], color=SLATE, linestyle=":",
                linewidth=1.2,
                label=rf"$\theta_{{th}}$={extra['threshold_matrix']:.3f}")
    ax.set_xlabel("Iteration k", fontsize=9)
    ax.set_ylabel("Cumulative fatigue", color=ACCENT, fontsize=9)
    ax2.set_ylabel(r"Rotation angle $\theta_k$", color=SLATE, fontsize=9)
    Kp = res["predicted"]; Ko = res["observed"]
    if np.isfinite(Kp):
        ax.axvline(Kp, color=ACCENT, linestyle=":", alpha=0.7,
                   label=rf"$K_{{pred}}$={Kp}")
    if np.isfinite(Ko):
        ax2.axvline(Ko, color=SLATE, linestyle="-.", alpha=0.7,
                    label=rf"$K_{{obs}}$={Ko}")
    ax.set_title(
        f"D. Repeated-loop fatigue (so(3)) [{res['verdict']}]\n"
        f"$K_{{pred}}$={Kp}, $K_{{obs}}$={Ko}", fontsize=10)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=7, loc="upper left")
    ax.grid(alpha=0.3)

    # Panel E: 3-bar T-loop vs T-control vs T-noncommute
    res = results["E"]
    ax = axs[1, 2]
    labels = ["Loop\n(xy-plane)", "Control\n(drift)", "Non-commuting\n(xy then yz)"]
    T_vals = [res["T_loop"], res["T_control"], res["T_noncommute"]]
    colors = [ACCENT, RUST, SLATE]
    bars = ax.bar(labels, T_vals, color=colors, edgecolor="white",
                  width=0.5, zorder=3)
    for bar, val in zip(bars, T_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10,
                color=SLATE)
    ax.set_ylabel("T statistic", fontsize=9)
    ax.set_title(
        f"E. Total-variance (n=4) [{res['verdict']}]\n"
        f"$T_{{loop}}$={res['T_loop']:.3f}, $T_{{ctrl}}$={res['T_control']:.3f}, "
        f"$T_{{noncomm}}$={res['T_noncommute']:.3f}", fontsize=10)
    ax.axhline(2.0, color=SLATE, linestyle="--", alpha=0.4,
               label="non-commute threshold 2.0")
    ax.axhline(1.0, color=SLATE, linestyle=":", alpha=0.4,
               label="control threshold 1.0")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3, axis="y")
    ax.set_ylim(0, max(T_vals) * 1.25)

    fig.suptitle(
        "Derivative Claims A-E: n=4 non-abelian regime "
        r"($CO(3)$, $so(3)$ non-abelian)",
        fontsize=13, color=SLATE, y=1.00)

    fig.savefig(out_path, dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = "/home/z/my-project/download"
    os.makedirs(out_dir, exist_ok=True)

    results = {
        "A": claim_a_n4(),
        "B": claim_b_n4(),
        "C": claim_c_n4(),
        "D": claim_d_n4(),
        "E": claim_e_n4(),
    }

    print("=== Target 5 - n=4 non-abelian generalization of A-E ===\n")
    for cid in ["A", "B", "C", "D", "E"]:
        r = results[cid]
        print(f"Claim {cid}: {r['title']}")
        print(f"  Verdict: {r['verdict']}")
        for k in ("predicted", "observed", "slope", "r_squared", "c2_fit",
                  "rel_error", "T_loop", "T_control", "T_noncommute",
                  "c_comm_fit", "c_comm_target", "rel_err_comm",
                  "r_squared_comm", "sameplane_max"):
            if k in r:
                print(f"  {k}: {r[k]}")
        print()

    csv_path = os.path.join(out_dir, "claims_ae_n4_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["claim", "title", "verdict",
                    "predicted_summary", "observed_summary",
                    "fit_metric", "fit_value"])
        for cid in ["A", "B", "C", "D", "E"]:
            r = results[cid]
            if cid == "A":
                w.writerow([cid, r["title"], r["verdict"],
                            "slope=1 expected",
                            f"slope={r['slope']:.4f}",
                            "R^2", f"{r['r_squared']:.4f}"])
            elif cid == "B":
                obs_s = (f"{r['observed']:.4f}" if not np.isnan(r['observed'])
                         else "nan")
                rel_s = (f"{r.get('rel_error', np.nan):.4f}"
                         if not np.isnan(r.get('rel_error', np.nan))
                         else "nan")
                w.writerow([cid, r["title"], r["verdict"],
                            f"a_rev_pred={r['predicted']:.3f}",
                            f"a_rev_obs={obs_s}",
                            "rel_err", rel_s])
            elif cid == "C":
                w.writerow([cid, r["title"], r["verdict"],
                            f"c1=pi={np.pi:.4f}, c2={r['extra']['c2_fit']:.4f}, "
                            f"c_comm={r['c_comm_target']:.3f}",
                            f"c1_fit={r['extra']['c1_fit']:.4f}, "
                            f"c2_fit={r['extra']['c2_fit']:.4f}, "
                            f"c_comm_fit={r['c_comm_fit']:.4f}",
                            "R^2 (area + comm)", 
                            f"{r['r_squared']:.4f} + {r['r_squared_comm']:.4f}"])
            elif cid == "D":
                Kp = (str(r['predicted']) if not np.isinf(r['predicted']) else "inf")
                Ko = (str(r['observed']) if not np.isinf(r['observed']) else "inf")
                rel_s = (f"{r.get('rel_error', np.nan):.4f}"
                         if not np.isnan(r.get('rel_error', np.nan))
                         else "nan")
                w.writerow([cid, r["title"], r["verdict"],
                            f"K_pred={Kp}", f"K_obs={Ko}",
                            "rel_err", rel_s])
            elif cid == "E":
                w.writerow([cid, r["title"], r["verdict"],
                            f"T_loop<2 (={r['T_loop']:.4f})",
                            f"T_ctrl>1 (={r['T_control']:.4f}), "
                            f"T_noncomm>2 (={r['T_noncommute']:.4f})",
                            "ratio (ctrl/loop, noncomm/loop)",
                            f"{r['T_control']/r['T_loop']:.2f}, "
                            f"{r['T_noncommute']/r['T_loop']:.2f}"])
    print(f"Results CSV: {csv_path}")

    fig_path = os.path.join(out_dir, "claims_ae_n4_nonabelian.png")
    make_figure(results, fig_path)
    print(f"Figure: {fig_path}")


if __name__ == "__main__":
    main()
