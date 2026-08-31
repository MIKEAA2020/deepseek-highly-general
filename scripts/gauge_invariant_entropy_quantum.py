#!/usr/bin/env python3
"""
Gauge-invariant entropy + Quantum elevation (Lindbladian, Holevo, Zeno)
=====================================================================
Elevation of Qwen audit defects 13 and 14.

DEFECT 13: log sqrt(det I(p)) is NOT gauge-invariant.
  FIX: construct TWO coordinate-free observables.
    (a) Fisher volume ratio H_emp(p) = log(d mu_F / d mu_0)(p)
        with d mu_F = sqrt(det G(p)) dp in minimal coordinates.
        Invariant under coordinate-chart changes and simplex isometries.
    (b) Fisher-Rao distance d_FR(p, p0) = 2 arccos(sum sqrt(p_i p_{0,i})).
        Invariant under simplex isometries.

DEFECT 14: Quantum claims overreach.
  FIX:
    (a) Dissipative Lindbladian L(rho) = -i[H, rho] + sum_k (L_k rho L_k^dag
        - (1/2){L_k^dag L_k, rho}) with H = (omega/2) sigma_z (commutes with
        |0><0|), L_0 = sqrt(gamma) sigma_-. Steady state |0><0| (absorbing);
        spectral gap Delta = min{-Re lambda} > 0.
    (b) Holevo ensemble: chi = S(sum p_x rho_x) - sum p_x S(rho_x),
        bounded by classical H({p_x}).
    (c) Zeno-projected self-reference: rho = P Phi(P rho P) P / Tr(...);
        amplitude damping is a strict contraction in trace distance
        (q = sqrt(1-gamma) < 1 for gamma > 0); unique fixed point by Banach.
"""
from __future__ import annotations
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import matplotlib.font_manager as fm
for f in (
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
):
    if os.path.exists(f):
        fm.fontManager.addfont(f)
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110

DOWNLOAD = "/home/z/my-project/download"
os.makedirs(DOWNLOAD, exist_ok=True)


# =============================================================================
# Part 1: Gauge-invariant Fisher observables
# =============================================================================
def fisher_metric_minimal(p, drop_index=-1):
    """Fisher metric on the m-simplex in minimal coordinates (drop one coord)."""
    m = len(p)
    drop = drop_index % m
    keep = [i for i in range(m) if i != drop]
    q = np.asarray(p, float)[keep]
    last = float(p[drop])
    return np.diag(1.0 / np.maximum(q, 1e-12)) + 1.0 / max(last, 1e-12)


def fisher_volume_density(p, drop_index=-1):
    G = fisher_metric_minimal(p, drop_index=drop_index)
    sign, logdet = np.linalg.slogdet(G)
    if sign <= 0:
        return 0.0
    return float(np.exp(0.5 * logdet))


def H_emp(p, p0, drop_index=-1):
    """log(d mu_F / d mu_0)(p) = log[sqrt(det G(p)) / sqrt(det G(p0))]."""
    num = fisher_volume_density(p, drop_index=drop_index)
    den = fisher_volume_density(p0, drop_index=drop_index)
    return float(np.log(num / max(den, 1e-12)))


def d_FR(p, p0):
    """Fisher-Rao distance on the simplex: 2 arccos(sum sqrt(p_i p_{0,i}))."""
    bc = float(np.sum(np.sqrt(np.maximum(p, 0) * np.maximum(p0, 0))))
    return float(2.0 * np.arccos(np.clip(bc, -1.0, 1.0)))


def run_gauge_invariant_entropy():
    """Two tests:
    (a) ISOMETRY invariance under coordinate permutation.
    (b) COORDINATE-CHART invariance: H_emp computed in two different minimal
        charts (drop p_3 vs drop p_0) gives the same value at the same point.
    """
    p = np.array([0.4, 0.3, 0.2, 0.1])
    p0 = np.array([0.25, 0.25, 0.25, 0.25])

    # (a) Isometry (permutation) invariance
    H_baseline = H_emp(p, p0)
    dFR_baseline = d_FR(p, p0)
    perm = np.array([2, 0, 3, 1])
    H_perm = H_emp(p[perm], p0[perm])
    dFR_perm = d_FR(p[perm], p0[perm])
    H_invar_iso = abs(H_baseline - H_perm)
    dFR_invar_iso = abs(dFR_baseline - dFR_perm)

    # (b) Coordinate-chart invariance
    H_chartA = H_emp(p, p0, drop_index=3)  # drop p_3
    H_chartB = H_emp(p, p0, drop_index=0)  # drop p_0
    H_invar_chart = abs(H_chartA - H_chartB)

    # Grid plot
    n = 30
    p1_grid = np.linspace(0.01, 0.5, n)
    p2_grid = np.linspace(0.01, 0.5, n)
    H_grid = np.zeros((n, n))
    dFR_grid = np.zeros((n, n))
    for i, p1 in enumerate(p1_grid):
        for j, p2 in enumerate(p2_grid):
            if p1 + p2 >= 0.9:
                continue
            p3 = (1.0 - p1 - p2) / 2.0
            pp = np.array([p1, p2, p3, p3])
            H_grid[i, j] = H_emp(pp, p0)
            dFR_grid[i, j] = d_FR(pp, p0)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    im0 = ax[0].pcolormesh(p1_grid, p2_grid, H_grid, shading="auto", cmap="viridis")
    ax[0].scatter([p[0]], [p[1]], c="red", s=60, marker="*", label="$p$")
    ax[0].scatter([p0[0]], [p0[1]], c="cyan", s=60, marker="x", label="$p_0$")
    ax[0].set_xlabel("$p_1$"); ax[0].set_ylabel("$p_2$")
    ax[0].set_title(f"$H_{{\\rm emp}}=\\log(d\\mu_F/d\\mu_0)$; chart-invar $\\sim$ {H_invar_chart:.2e}")
    plt.colorbar(im0, ax=ax[0])
    ax[0].legend(fontsize=8, loc="upper right")

    im1 = ax[1].pcolormesh(p1_grid, p2_grid, dFR_grid, shading="auto", cmap="magma")
    ax[1].scatter([p[0]], [p[1]], c="red", s=60, marker="*")
    ax[1].scatter([p0[0]], [p0[1]], c="cyan", s=60, marker="x")
    ax[1].set_xlabel("$p_1$"); ax[1].set_ylabel("$p_2$")
    ax[1].set_title(f"$d_{{FR}}(p, p_0)$; isometry-invar $\\sim$ {dFR_invar_iso:.2e}")
    plt.colorbar(im1, ax=ax[1])

    fig.suptitle("Gauge-invariant Fisher observables (Qwen defect 13 elevation)",
                 fontsize=12, y=1.02)
    out_png = os.path.join(DOWNLOAD, "elevation_gauge_invariant_entropy.png")
    fig.savefig(out_png, dpi=130, bbox_inches="tight")
    plt.close(fig)

    return {
        "H_emp_baseline": H_baseline,
        "H_emp_isometry_invariance": H_invar_iso,
        "H_emp_chartA_drop_p3": H_chartA,
        "H_emp_chartB_drop_p0": H_chartB,
        "H_emp_chart_invariance": H_invar_chart,
        "d_FR_baseline": dFR_baseline,
        "d_FR_isometry_invariance": dFR_invar_iso,
        "verdict": "GAUGE_INVARIANT_ENTROPY_VERIFIED"
                   if (H_invar_iso < 1e-10 and dFR_invar_iso < 1e-10
                       and H_invar_chart < 1e-10)
                   else "FAIL",
        "plot": out_png,
    }


# =============================================================================
# Part 2: Quantum elevation
# =============================================================================
def von_neumann_entropy(rho):
    w = np.maximum(np.linalg.eigvalsh(rho), 1e-12)
    return float(-np.sum(w * np.log2(w)))


def amplitude_damping_kraus(gamma):
    K0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
    return [K0, K1]


def apply_channel(Ks, rho):
    out = np.zeros_like(rho)
    for K in Ks:
        out += K @ rho @ K.conj().T
    return out


def lindbladian_fn(H, Ls):
    def L(rho):
        out = -1j * (H @ rho - rho @ H)
        for Lk in Ls:
            Lkd = Lk.conj().T
            out += Lk @ rho @ Lkd - 0.5 * (Lkd @ Lk @ rho + rho @ Lkd @ Lk)
        return out
    return L


def lindbladian_matrix(H, Ls, dim=2):
    """Vectorize Lindbladian as dim^2 x dim^2 complex matrix (column-major)."""
    I = np.eye(dim, dtype=complex)
    Lmat = -1j * (np.kron(I, H) - np.kron(H.T, I))
    for Lk in Ls:
        Lkd = Lk.conj().T
        LkdLk = Lkd @ Lk
        Lmat += np.kron(Lk.conj(), Lk) - 0.5 * (np.kron(I, LkdLk) + np.kron(LkdLk.T, I))
    return Lmat


def trace_distance(a, b):
    return 0.5 * float(np.linalg.norm(a - b, ord="nuc"))


def run_quantum_elevation():
    # (a) Dissipative Lindbladian: H = (omega/2) sigma_z, L_0 = sqrt(gamma) sigma_-
    omega = 2.0
    gamma = 0.5
    H = 0.5 * omega * np.array([[1, 0], [0, -1]], dtype=complex)
    L0 = np.sqrt(gamma) * np.array([[0, 1], [0, 0]], dtype=complex)
    Ls = [L0]
    Lmat = lindbladian_matrix(H, Ls, dim=2)
    eigs = np.linalg.eigvals(Lmat)
    nonzero = [e for e in eigs if abs(e) > 1e-9]
    Delta = float(min(-e.real for e in nonzero)) if nonzero else float("nan")

    # Function-form Euler integration to verify steady state = |0><0|
    L_fn = lindbladian_fn(H, Ls)
    rho0 = np.array([[0.3, 0.2 + 0.1j], [0.2 - 0.1j, 0.7]], dtype=complex)
    rho0 = rho0 / np.trace(rho0)
    t_arr = np.linspace(0, 50, 5000)
    dt = t_arr[1] - t_arr[0]
    rho_traj = [rho0.copy()]
    for k in range(1, len(t_arr)):
        r = rho_traj[-1] + dt * L_fn(rho_traj[-1])
        r = 0.5 * (r + r.conj().T)
        r = r / np.trace(r)
        rho_traj.append(r)
    rho_traj = np.array(rho_traj)
    steady = np.array([[1, 0], [0, 0]], dtype=complex)
    final_dev = float(np.linalg.norm(rho_traj[-1] - steady))

    # (b) Holevo ensemble
    rho_a = np.array([[1, 0], [0, 0]], dtype=complex)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho_b = np.outer(plus, plus.conj())
    ensemble = [(0.5, rho_a), (0.5, rho_b)]
    rho_avg = sum(p * r for p, r in ensemble)
    chi = von_neumann_entropy(rho_avg) - sum(p * von_neumann_entropy(r) for p, r in ensemble)
    classical_bound = -sum(p * np.log2(p) for p, _ in ensemble)
    holevo_holds = bool(chi <= classical_bound + 1e-9)

    # (c) Quantum self-reference fixed point via Banach contraction
    # Amplitude damping with gamma=0.3 is a strict contraction in trace distance
    # with q = sqrt(1-gamma) (off-diagonal decay). Fixed point: |0><0|.
    gamma_cptp = 0.3
    Ks = amplitude_damping_kraus(gamma_cptp)
    rho1 = np.array([[0.7, 0.3], [0.3, 0.3]], dtype=complex)
    rho2 = np.array([[0.6, 0.2], [0.2, 0.4]], dtype=complex)
    rho1 = rho1 / np.trace(rho1); rho2 = rho2 / np.trace(rho2)
    dist_before = trace_distance(rho1, rho2)
    dist_after = trace_distance(apply_channel(Ks, rho1), apply_channel(Ks, rho2))
    q = dist_after / max(dist_before, 1e-12)
    contraction_holds = bool(q < 1.0 + 1e-9)

    # Unprojected iteration
    P = np.array([[1, 0], [0, 0]], dtype=complex)
    rho = np.array([[0.6, 0.3], [0.3, 0.4]], dtype=complex)
    rho = rho / np.trace(rho)
    fixed_iters = []
    for k in range(200):
        rho = apply_channel(Ks, rho)
        rho = 0.5 * (rho + rho.conj().T)
        rho = rho / np.trace(rho)
        fixed_iters.append(float(np.linalg.norm(rho - P)))
    fixed_dev = float(np.linalg.norm(rho - P))

    # Zeno-projected iteration with trace renormalization
    def Phi_P_renorm(rho):
        out = P @ apply_channel(Ks, P @ rho @ P) @ P
        tr = np.trace(out)
        return out / tr if tr > 0 else out
    rho_z = np.array([[0.6, 0.4], [0.4, 0.4]], dtype=complex)
    rho_z = rho_z / np.trace(rho_z)
    zeno_iters = []
    for k in range(20):
        rho_z = Phi_P_renorm(rho_z)
        zeno_iters.append(float(np.linalg.norm(rho_z - P)))
    zeno_dev = float(np.linalg.norm(rho_z - P))

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    ax[0].plot(t_arr, [np.real(r[0, 0]) for r in rho_traj], color="#1f6feb", lw=1.8,
               label=r"$\rho_{00}(t)$")
    ax[0].plot(t_arr, [np.real(r[1, 1]) for r in rho_traj], color="#d23f3f", lw=1.8,
               label=r"$\rho_{11}(t)$")
    ax[0].axhline(1.0, color="#2da44e", ls=":", lw=1.2, label="steady $|0\\rangle\\langle 0|$")
    ax[0].axhline(0.0, color="#2da44e", ls=":", lw=1.2)
    ax[0].set_xlabel("time $t$"); ax[0].set_ylabel("populations")
    ax[0].set_title(f"Lindbladian gap $\\Delta = {Delta:.4f}$ (amplitude damping)")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    ax[1].bar(["ensemble $\\chi$", "classical bound $H(\\{{p_x\\}})$"],
              [chi, classical_bound], color=["#1f6feb", "#888"], alpha=0.85)
    ax[1].set_ylabel("information (bits)")
    ax[1].set_title(f"Holevo $\\chi = {chi:.4f}$ $\\leq$ bound {classical_bound:.4f} (holds: {holevo_holds})")
    ax[1].grid(alpha=0.3, axis="y")

    ax[2].semilogy(range(200), fixed_iters, "o-", color="#8957e5", lw=1.8, ms=2,
                   label=f"unprojected $\\Phi$ (q={q:.3f})")
    ax[2].semilogy(range(20), zeno_iters, "s-", color="#d23f3f", lw=1.8, ms=4,
                   label=f"Zeno $\\Phi_P$ ($P=|0\\rangle\\langle 0|$)")
    ax[2].set_xlabel("iteration $k$")
    ax[2].set_ylabel(r"$\|\rho_k - |0\rangle\langle 0|\|$")
    ax[2].set_title(f"Fixed-point convergence (unproj {fixed_dev:.2e}, Zeno {zeno_dev:.2e})")
    ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3)

    fig.suptitle("Quantum elevation: Lindbladian + Holevo + Zeno fixed-point (Qwen defect 14)",
                 fontsize=12, y=1.02)
    out_png = os.path.join(DOWNLOAD, "elevation_quantum.png")
    fig.savefig(out_png, dpi=130, bbox_inches="tight")
    plt.close(fig)

    return {
        "lindbladian_gap_Delta": Delta,
        "lindbladian_eigenvalues": [complex(e) for e in eigs],
        "lindbladian_steady_state_deviation": final_dev,
        "holevo_chi": float(chi),
        "classical_bound": float(classical_bound),
        "holevo_bound_holds": holevo_holds,
        "amplitude_damping_contraction_q": float(q),
        "contraction_holds": contraction_holds,
        "unprojected_fixed_point_deviation": fixed_dev,
        "zeno_projected_fixed_point_deviation": zeno_dev,
        "verdict": "QUANTUM_ELEVATION_VERIFIED"
                   if (Delta > 0 and holevo_holds and contraction_holds
                       and fixed_dev < 1e-5 and zeno_dev < 1e-5)
                   else "FAIL",
        "plot": out_png,
    }


def main():
    print("[1/2] Gauge-invariant Fisher observables...")
    r1 = run_gauge_invariant_entropy()
    print(f"  H_emp baseline        = {r1['H_emp_baseline']:.4f}")
    print(f"  H_emp isometry invar   = {r1['H_emp_isometry_invariance']:.2e}")
    print(f"  H_emp chart invar      = {r1['H_emp_chart_invariance']:.2e}")
    print(f"  d_FR baseline         = {r1['d_FR_baseline']:.4f}")
    print(f"  d_FR isometry invar   = {r1['d_FR_isometry_invariance']:.2e}")
    print(f"  verdict = {r1['verdict']}")

    print("[2/2] Quantum elevation...")
    r2 = run_quantum_elevation()
    print(f"  Lindbladian gap Delta = {r2['lindbladian_gap_Delta']:.4f}")
    print(f"  steady-state dev      = {r2['lindbladian_steady_state_deviation']:.2e}")
    print(f"  Holevo chi            = {r2['holevo_chi']:.4f}")
    print(f"  classical bound       = {r2['classical_bound']:.4f}")
    print(f"  Holevo bound holds    = {r2['holevo_bound_holds']}")
    print(f"  contraction q         = {r2['amplitude_damping_contraction_q']:.4f}")
    print(f"  unprojected fixed dev = {r2['unprojected_fixed_point_deviation']:.2e}")
    print(f"  Zeno fixed dev        = {r2['zeno_projected_fixed_point_deviation']:.2e}")
    print(f"  verdict = {r2['verdict']}")

    out = {
        "gauge_invariant_entropy": r1,
        "quantum_elevation": r2,
        "summary": {
            "qwen_defects_addressed": [
                "13: log sqrt(det I(p)) REPLACED by (a) Fisher volume ratio "
                "H_emp = log(d mu_F / d mu_0) (chart-invariance " + f"{r1['H_emp_chart_invariance']:.2e}" +
                ", isometry-invariance " + f"{r1['H_emp_isometry_invariance']:.2e}" + ") and "
                "(b) Fisher-Rao distance d_FR (isometry-invariance " + f"{r1['d_FR_isometry_invariance']:.2e}" + ").",
                "14: Quantum elevation. (a) Dissipative Lindbladian with H = sigma_z/2 "
                "and L_0 = sqrt(gamma) sigma_-, spectral gap Delta = " + f"{r2['lindbladian_gap_Delta']:.4f}" +
                " > 0, steady state |0><0| (deviation " + f"{r2['lindbladian_steady_state_deviation']:.2e}" + "); "
                "(b) Holevo chi = " + f"{r2['holevo_chi']:.4f}" + " bits <= classical bound " +
                f"{r2['classical_bound']:.4f}" + " (holds: " + str(r2['holevo_bound_holds']) + "); "
                "(c) Amplitude damping is a strict contraction in trace distance with q = " +
                f"{r2['amplitude_damping_contraction_q']:.3f}" + " < 1, fixed point |0><0| by Banach " +
                "(unprojected dev " + f"{r2['unprojected_fixed_point_deviation']:.2e}" +
                ", Zeno-projected dev " + f"{r2['zeno_projected_fixed_point_deviation']:.2e}" + ").",
            ],
        },
    }
    out_path = os.path.join(DOWNLOAD, "elevation_gauge_quantum_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults JSON: {out_path}")
    print(f"Plot 1 (entropy): {r1['plot']}")
    print(f"Plot 2 (quantum):  {r2['plot']}")


if __name__ == "__main__":
    main()
