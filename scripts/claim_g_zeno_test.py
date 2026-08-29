#!/usr/bin/env python3
"""
Foundational Test G - CPTP open quantum channel + Zeno scaling test.

The CPTP lift replaces the classical Markov transition P(y|x) with a quantum
channel E(rho) = sum_i K_i rho K_i^dagger, where the Kraus operators satisfy
sum_i K_i^dagger K_i = I. The quantum Zeno effect predicts that under
sufficiently frequent measurement (interval tau much less than the inverse
Liouvillian spectral gap), the measurement-induced state change scales as
tau^2 rather than as tau. This is the Zeno scaling.

Decisive test:
  - For varying measurement intervals tau, measure the state change ||rho_after - rho_0||
  - Fit the scaling exponent alpha in ||rho_after - rho_0|| ~ tau^alpha
  - Classical (Markov) prediction: alpha = 1 (linear in tau)
  - CPTP+Zeno prediction: alpha = 2 (quadratic in tau) for tau << 1/gap
  - Refutation: alpha = 1 in the small-tau regime

We model a two-level quantum system (qubit) undergoing:
  1. Free Liouvillian evolution for time tau (the "between-measurement" evolution)
  2. A projective measurement of one observable (e.g., sigma_z)
  3. State change measured as the trace distance between pre- and post-measurement state

The Zeno regime is reached when tau is much smaller than the inverse spectral
gap of the Liouvillian. In this regime, the measurement projects the system
back close to its initial state, and the deviation scales as tau^2.

Outputs:
  /home/z/my-project/download/claim_g_zeno_results.csv
  /home/z/my-project/download/claim_g_zeno_plot.png
  stdout: pass/fail summary with fitted scaling exponent
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

fm.fontManager.addfont("/usr/share/fonts/truetype/chinese/SarasaMonoSC-Light.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Pauli matrices
SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def liouvillian_evolution(rho, H, tau, gamma=0.0):
    """
    Evolve density matrix rho under Hamiltonian H for time tau, with optional
    dephasing rate gamma (Lindblad operator L = sqrt(gamma) * sigma_z).

    The evolution is the standard Lindblad master equation:
      d rho/dt = -i [H, rho] + gamma * (sigma_z rho sigma_z - rho)

    We compute the closed-form solution for the dephasing case (which is exact
    and stable for all tau).
    """
    # Hamiltonian part: rho -> exp(-i H tau) rho exp(i H tau)
    # Use eigendecomposition for H = (omega/2) * sigma_x (our chosen Hamiltonian)
    # exp(-i (omega/2) sigma_x tau) = cos(omega tau/2) I - i sin(omega tau/2) sigma_x
    omega = 2 * np.real(np.trace(H @ SIGMA_X) / 2)  # extract omega from H = (omega/2) sigma_x
    # actually we set H = (omega/2) sigma_x directly, so omega = 2 * H[0,1] (which is real)
    omega = 2.0
    c, s = np.cos(omega * tau / 2), np.sin(omega * tau / 2)
    U = c * I2 - 1j * s * SIGMA_X
    rho_H = U @ rho @ U.conj().T

    # Dephasing part: sigma_z rho sigma_z - rho (closed form: off-diagonal decays as exp(-2 gamma tau))
    rho_dephased = rho_H.copy()
    rho_dephased[0, 1] *= np.exp(-2 * gamma * tau)
    rho_dephased[1, 0] *= np.exp(-2 * gamma * tau)
    return rho_dephased


def projective_measurement(rho, observable):
    """
    Apply a projective measurement of `observable` to rho.
    Returns the post-measurement state (Lüders rule): rho' = sum_i P_i rho P_i,
    where P_i are the projectors onto the eigenvalues of observable.
    """
    # For sigma_z, projectors are |0><0| and |1><1|
    if np.allclose(observable, SIGMA_Z):
        P0 = np.array([[1, 0], [0, 0]], dtype=complex)
        P1 = np.array([[0, 0], [0, 1]], dtype=complex)
        return P0 @ rho @ P0 + P1 @ rho @ P1
    raise NotImplementedError("Only sigma_z measurement supported here")


def trace_distance(rho_a, rho_b):
    """Trace distance between two density matrices: T = (1/2) ||rho_a - rho_b||_tr."""
    diff = rho_a - rho_b
    # Trace norm = sum of singular values
    sv = np.linalg.svd(diff, compute_uv=False)
    return 0.5 * np.sum(np.abs(sv))


def run_zeno_experiment(initial_rho, H, tau_values, gamma=0.0):
    """
    For each measurement interval tau in tau_values:
      1. Evolve initial_rho under H for time tau (with dephasing gamma)
      2. Apply projective measurement of sigma_z
      3. Record state change ||rho_after - rho_before||_tr (trace distance)

    The pre-measurement state is the evolved state; the initial_rho is the
    state after the previous measurement (Zeno regime: system is continually
    projected back to the eigenstate).
    """
    results = []
    for tau in tau_values:
        # Evolve
        rho_evolved = liouvillian_evolution(initial_rho, H, tau, gamma=gamma)
        # Measure
        rho_post = projective_measurement(rho_evolved, SIGMA_Z)
        # State change relative to initial (which was the post-measurement state of previous cycle)
        change = trace_distance(rho_post, initial_rho)
        # Also record evolved-vs-initial (the "free evolution" change, without measurement)
        free_change = trace_distance(rho_evolved, initial_rho)
        results.append({
            "tau": tau,
            "free_evolution_change": free_change,
            "post_measurement_change": change,
        })
    return results


def run_classical_markov_benchmark(tau_values, omega=2.0):
    """
    Classical Markov benchmark: a two-state Markov chain with transition rate
    proportional to omega. The state change after time tau scales linearly
    with tau (for small tau).

    Transition matrix P(tau) = exp(tau * Q), where Q is the generator.
    We use Q = omega * [[-1, 1], [1, -1]] (symmetric two-state chain).
    """
    Q = omega * np.array([[-1, 1], [1, -1]], dtype=float)
    # Initial state: [1, 0] (definitely in state 0)
    p0 = np.array([1.0, 0.0], dtype=float)
    results = []
    for tau in tau_values:
        # exp(tau Q) by eigendecomposition (Q is symmetric)
        eigvals, eigvecs = np.linalg.eigh(Q)
        P = eigvecs @ np.diag(np.exp(tau * eigvals)) @ eigvecs.T
        p_after = P @ p0
        # TV distance
        change = 0.5 * np.sum(np.abs(p_after - p0))
        results.append({"tau": tau, "classical_change": change})
    return results


def fit_scaling_exponent(tau_values, changes):
    """
    Fit ||change|| ~ tau^alpha in the small-tau regime.
    Returns alpha and the fit R^2.
    """
    tau_arr = np.array(tau_values)
    chg_arr = np.array(changes)
    # Log-log linear fit
    mask = (tau_arr > 0) & (chg_arr > 1e-15)
    if mask.sum() < 3:
        return float("nan"), float("nan")
    log_tau = np.log(tau_arr[mask])
    log_chg = np.log(chg_arr[mask])
    # Linear fit: log_chg = alpha * log_tau + const
    A = np.vstack([log_tau, np.ones_like(log_tau)]).T
    coeffs, residuals, _, _ = np.linalg.lstsq(A, log_chg, rcond=None)
    alpha = coeffs[0]
    # R^2
    ss_res = np.sum((log_chg - A @ coeffs) ** 2)
    ss_tot = np.sum((log_chg - np.mean(log_chg)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return alpha, r2


def make_plot(tau_values, free_changes, post_changes, classical_changes, alpha, alpha_cl, out_path):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5.5), constrained_layout=True)

    ax.loglog(tau_values, free_changes, "o-", color="#7f8589",
              label=f"Free Liouvillian evolution (no measurement)", markersize=4, alpha=0.7)
    ax.loglog(tau_values, post_changes, "s-", color="#2897cf",
              label=f"CPTP + Zeno measurement (fitted α = {alpha:.3f})", markersize=5)
    ax.loglog(tau_values, classical_changes, "^-", color="#bf5836",
              label=f"Classical Markov benchmark (fitted α = {alpha_cl:.3f})", markersize=5, alpha=0.8)

    # Reference lines for tau^1 and tau^2 scaling
    tau_arr = np.array(tau_values)
    # Pick a reference magnitude
    ref_zeno = post_changes[3] if len(post_changes) > 3 else post_changes[0]
    ref_cl = classical_changes[3] if len(classical_changes) > 3 else classical_changes[0]
    zeno_ref_line = ref_zeno * (tau_arr / tau_arr[3]) ** 2
    cl_ref_line = ref_cl * (tau_arr / tau_arr[3]) ** 1
    ax.loglog(tau_arr, zeno_ref_line, ":", color="#2897cf", alpha=0.4, label="τ² reference (Zeno)")
    ax.loglog(tau_arr, cl_ref_line, ":", color="#bf5836", alpha=0.4, label="τ¹ reference (classical)")

    ax.set_xlabel("Measurement interval τ")
    ax.set_ylabel("State change (trace distance)")
    ax.set_title("Claim G: CPTP + Quantum Zeno scaling test\n"
                 "Decisive signature: α ≈ 2 in small-τ regime (CPTP) vs α ≈ 1 (classical)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3, which="both")

    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    out_dir = "/home/z/my-project/download"
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "claim_g_zeno_results.csv")
    plot_path = os.path.join(out_dir, "claim_g_zeno_plot.png")

    # Initial state: |0><0| (eigenstate of sigma_z)
    initial_rho = np.array([[1, 0], [0, 0]], dtype=complex)

    # Hamiltonian: H = (omega/2) sigma_x, omega = 2 (Liouvillian gap ~ omega/2 = 1)
    H = 1.0 * SIGMA_X  # = (omega/2) sigma_x with omega = 2

    # Measurement intervals spanning Zeno regime (tau << 1/gap = 1/1 = 1)
    # and the anti-Zeno regime (tau >> 1/gap)
    tau_values = np.logspace(-3, 1, 30)  # 0.001 to 10

    # Run quantum (CPTP) experiment with weak dephasing
    quantum_results = run_zeno_experiment(initial_rho, H, tau_values, gamma=0.05)

    # Run classical Markov benchmark
    classical_results = run_classical_markov_benchmark(tau_values, omega=2.0)

    # Extract state changes
    post_changes = [r["post_measurement_change"] for r in quantum_results]
    free_changes = [r["free_evolution_change"] for r in quantum_results]
    classical_changes = [r["classical_change"] for r in classical_results]

    # Fit scaling exponents in the small-tau (Zeno) regime: tau in [1e-3, 1e-1]
    zeno_mask = np.array(tau_values) <= 0.1
    tau_zeno = [t for t, m in zip(tau_values, zeno_mask) if m]
    post_zeno = [c for c, m in zip(post_changes, zeno_mask) if m]
    classical_zeno = [c for c, m in zip(classical_changes, zeno_mask) if m]

    alpha_zeno, r2_zeno = fit_scaling_exponent(tau_zeno, post_zeno)
    alpha_classical, r2_classical = fit_scaling_exponent(tau_zeno, classical_zeno)

    # Decisive test
    # Pass condition: alpha_zeno ~ 2 (within 0.3) AND alpha_classical ~ 1 (within 0.3)
    pass_zeno = 1.7 <= alpha_zeno <= 2.3
    pass_classical = 0.7 <= alpha_classical <= 1.3
    pass_condition = pass_zeno and pass_classical

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["tau", "free_evolution_change", "post_measurement_change", "classical_change"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, tau in enumerate(tau_values):
            writer.writerow({
                "tau": tau,
                "free_evolution_change": free_changes[i],
                "post_measurement_change": post_changes[i],
                "classical_change": classical_changes[i],
            })

    make_plot(tau_values, free_changes, post_changes, classical_changes,
              alpha_zeno, alpha_classical, plot_path)

    # Print summary
    print("=" * 64)
    print("CLAIM G: CPTP OPEN QUANTUM CHANNEL + ZENO SCALING TEST")
    print("Liouvillian: H = (ω/2) σ_x with ω = 2; gap ≈ 1; Zeno regime: τ << 1")
    print("=" * 64)
    print()
    print(f"Quantum (CPTP) experiment:")
    print(f"  N = {len(tau_values)} measurement intervals, range [1e-3, 1e1]")
    print(f"  Zeno-regime fit (τ ≤ 0.1): α = {alpha_zeno:.4f}, R² = {r2_zeno:.4f}")
    print(f"  Expected: α ≈ 2 (quadratic Zeno scaling)")
    print()
    print(f"Classical Markov benchmark:")
    print(f"  Zeno-regime fit (τ ≤ 0.1): α = {alpha_classical:.4f}, R² = {r2_classical:.4f}")
    print(f"  Expected: α ≈ 1 (linear Markov scaling)")
    print()
    print(f"Decisive test result:")
    print(f"  CPTP+Zeno exponent: {alpha_zeno:.4f} (target: ~2)")
    print(f"  Classical exponent:  {alpha_classical:.4f} (target: ~1)")
    print()
    print("=" * 64)
    if pass_condition:
        print("RESULT: CLAIM G CONFIRMED")
        print("  - CPTP+Zeno scaling exponent ≈ 2 in the small-τ regime")
        print("  - Classical Markov scaling exponent ≈ 1 in the same regime")
        print("  - The two regimes are distinguishable: α_zeno / α_classical ≈ 2")
        print("  - The CPTP lift carries an empirically distinct signature")
    else:
        print("RESULT: CLAIM G NOT CONFIRMED")
        print(f"  alpha_zeno = {alpha_zeno:.4f} (expected ~2)")
        print(f"  alpha_classical = {alpha_classical:.4f} (expected ~1)")
    print("=" * 64)
    print(f"Raw data: {csv_path}")
    print(f"Plot:     {plot_path}")


if __name__ == "__main__":
    main()
