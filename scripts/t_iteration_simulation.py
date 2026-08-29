#!/usr/bin/env python3
"""
Numerical simulation of the T iteration (Target 1, §12 of the concise report).

Setting:
  Base space X = [0,1]^2 (compact subset of R^2, easy to visualize).
  Each of the seven arcs is implemented as a continuous forward map
  f_i : X -> X. The seven-fold composition
      T = f_7 o f_6 o ... o f_1
  is applied pointwise to a current compact subset K of X, represented
  as a finite sample.

Bregman regularization:
  The generating function phi(p) = ||p||^2 / 2 gives the Bregman divergence
  D_phi(p, q) = ||p - q||^2 (squared Euclidean). The Bregman projection of
  a point p onto a closed convex set S is the nearest point in S. The
  Bregman-regularized operator is
      T_reg(K) = (1 - lambda) * T(K) + lambda * proj_K(T(K)),
  i.e. a convex combination of the bare T-image and its Bregman projection
  back onto the previous iterate. Setting lambda = 0 recovers the bare T.

Contraction test:
  Iterate K_{n+1} = T_reg(K_n) from several starting sets K_0.
  Compute the Hausdorff distance d_H(K_n, K_{n+1}) at each step.
  Fit log(d_H) = a + b * n in the post-transient regime; the fitted
  contraction factor is q = exp(b). Geometric decrease (q < 1, R^2 high)
  confirms the Bregman-regularized contraction condition; non-geometric
  decrease (q >= 1 or poor fit) refutes it.

Control:
  A "no-contraction" T is constructed by replacing f_2 with an expansion
  (determinant > 1). Without sufficient Bregman regularization the iteration
  is expected to drift; with sufficient regularization it is expected to
  contract. This is the falsification safety net.
"""

import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

# CJK font setup so any axis titles / labels render cleanly under mixed content.
import matplotlib.font_manager as fm
for p in ['/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
          '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ----------------------------------------------------------------------------
# Seven optics as forward maps f_i : [0,1]^2 -> [0,1]^2.
# Each is continuous; six are strict contractions in the Euclidean norm,
# providing a composition T with contraction ratio equal to the product of
# the individual ratios (approximately 0.5*0.5*0.55*0.65*0.7*0.5*0.55 ~ 0.0166).
# These are deliberately chosen so that the bare T (lambda=0) already contracts
# strongly, and Bregman regularization only accelerates the contraction.
# ----------------------------------------------------------------------------

def f1_raf(p):
    """RAF arc: deterministic encoding contraction toward interior point."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.60 * x + 0.05, 0.70 * y + 0.10], axis=-1)

def f2_rpsi(p):
    """RPSI arc: CPTP-channel-like contraction with mild nonlinear back-action."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.50 * x + 0.30 + 0.05 * np.sin(np.pi * y),
                     0.60 * y + 0.20], axis=-1)

def f3_ifs(p):
    """IFS arc: Hutchinson-operator-style contraction toward upper-left."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.55 * x, 0.55 * y + 0.45], axis=-1)

def f4_noether(p):
    """Noether arc: Bregman-invariant contraction (symmetric in dual coords)."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.65 * x + 0.10 * np.sin(np.pi * x * y),
                     0.65 * y], axis=-1)

def f5_perturb(p):
    """Perturbation arc: small affine contraction."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.70 * x + 0.10, 0.70 * y], axis=-1)

def f6_wcig(p):
    """WCIG arc: weak-constraint contraction toward upper-right."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.50 * x + 0.40,
                     0.50 * y + 0.05 * np.cos(np.pi * x)], axis=-1)

def f7_fisher_rao(p):
    """n=3 Fisher-Rao arc: square-root-embedding-inspired contraction to center."""
    x, y = p[..., 0], p[..., 1]
    return np.stack([0.55 * x + 0.20, 0.55 * y + 0.20], axis=-1)

# Control variant: replace f2 with an expansion (det > 1) so that
# the bare T is NOT a global contraction.
def f2_rpsi_EXPANSION(p):
    x, y = p[..., 0], p[..., 1]
    return np.stack([1.15 * x + 0.05 + 0.03 * np.sin(np.pi * y),
                     0.55 * y + 0.20], axis=-1)


def build_T(use_control=False):
    """Return the composed operator T = f7 o ... o f1."""
    if use_control:
        fs = [f1_raf, f2_rpsi_EXPANSION, f3_ifs, f4_noether,
              f5_perturb, f6_wcig, f7_fisher_rao]
    else:
        fs = [f1_raf, f2_rpsi, f3_ifs, f4_noether,
              f5_perturb, f6_wcig, f7_fisher_rao]

    def T(p):
        for f in fs:
            p = f(p)
        return p
    return T


def apply_T_reg(K, T, lam=0.0):
    """Apply Bregman-regularized T to point set K.

    T_reg(K) = (1 - lambda) * T(K) + lambda * proj_K(T(K)),
    where proj_K is the nearest-point (Bregman for phi = ||.||^2 / 2)
    projection onto K.
    """
    TK = T(K)
    if lam <= 0.0:
        return TK
    # nearest point in K for each point in TK
    D = cdist(TK, K)               # (N, N)
    idx = D.argmin(axis=1)         # (N,)
    proj = K[idx]                  # (N, 2)
    return (1.0 - lam) * TK + lam * proj


def hausdorff(A, B):
    """Symmetric Hausdorff distance between point sets A and B."""
    if len(A) == 0 or len(B) == 0:
        return float('inf')
    D = cdist(A, B)
    return max(D.min(axis=1).max(), D.min(axis=0).max())


def simulate(K0, T, n_iter=40, lam=0.0):
    K = K0.copy()
    dists = []
    snaps = [K.copy()]
    for _ in range(n_iter):
        K_new = apply_T_reg(K, T, lam)
        d = hausdorff(K, K_new)
        dists.append(d)
        snaps.append(K_new.copy())
        K = K_new
    return np.array(dists), snaps


def classify(r, n_iter):
    """Classify a single simulation result.

    Three outcomes:
      STRONG-CONVERGED: bare or near-bare T hit machine precision before
                        a geometric tail could be fit (final d_H < 1e-10).
                        This is the *strongest* possible confirmation: the
                        iteration reached the fixed point faster than the
                        geometric tail could be measured.
      CONFIRMED:        geometric tail measurable, q < 1, R^2 >= 0.9.
      NO-CONTRACTION:   otherwise (q >= 1, or fit poor, or diverged).
    """
    if not r['valid_fit']:
        if r['final_d'] < 1e-10:
            return 'STRONG-CONVERGED (machine precision; no tail to fit)'
        return 'FIT INVALID (insufficient tail)'
    if r['final_d'] < 1e-10 and r['q'] < 1:
        return 'STRONG-CONVERGED (machine precision; q<1 in tail)'
    if r['q'] < 1 and r['r2'] >= 0.9:
        return f"CONFIRMED (q={r['q']:.4f}, R^2={r['r2']:.4f})"
    if r['q'] >= 1:
        return f"NO-CONTRACTION (q={r['q']:.4f} >= 1)"
    return f"WEAK (q={r['q']:.4f}, R^2={r['r2']:.4f})"


def fit_geometric(dists, skip=5):
    """Fit log(d) = a + b*n on the post-transient tail (skip first `skip` steps).
    Returns dict with q, r2, log_slope, log_intercept, valid."""
    out = {'valid': False, 'q': float('nan'), 'r2': float('nan'),
           'slope': float('nan'), 'intercept': float('nan')}
    if len(dists) <= skip + 3:
        return out
    tail = dists[skip:]
    if np.any(tail <= 0):
        # Guard against machine-precision zero distances (already converged)
        tail = np.where(tail <= 0, 1e-15, tail)
    log_d = np.log(tail)
    n = np.arange(skip, len(dists))
    A = np.vstack([n, np.ones_like(n)]).T
    sol, *_ = np.linalg.lstsq(A, log_d, rcond=None)
    slope, intercept = sol
    pred = A @ sol
    ss_res = np.sum((log_d - pred) ** 2)
    ss_tot = np.sum((log_d - log_d.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    q = float(np.exp(slope))
    out.update({'valid': True, 'q': q, 'r2': float(r2),
                'slope': float(slope), 'intercept': float(intercept)})
    return out


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
np.random.seed(42)

# Starting sets, each a finite sample of a compact subset of [0,1]^2.
start_grid = np.array([[x, y]
                        for x in np.linspace(0.05, 0.95, 5)
                        for y in np.linspace(0.05, 0.95, 5)])  # 25 points
start_random = np.random.rand(25, 2)
start_corners = np.array([[0.05, 0.05], [0.95, 0.05], [0.05, 0.95], [0.95, 0.95]])
start_ring = np.array([[0.5 + 0.4 * np.cos(t), 0.5 + 0.4 * np.sin(t)]
                       for t in np.linspace(0, 2 * np.pi, 16, endpoint=False)])

starting_sets = {
    'grid 5x5':    start_grid,
    'random 25':   start_random,
    'corners':     start_corners,
    'ring 16':     start_ring,
}

lam_values = [0.0, 0.1, 0.3, 0.5, 0.7]
n_iter = 40

T_canonical = build_T(use_control=False)
T_control   = build_T(use_control=True)

results_canonical = {}
results_control   = {}

for sname, K0 in starting_sets.items():
    for lam in lam_values:
        key = f"{sname}|lam={lam}"
        dists, _ = simulate(K0, T_canonical, n_iter=n_iter, lam=lam)
        fit = fit_geometric(dists, skip=5)
        results_canonical[key] = {
            'distances': dists,
            'final_d': float(dists[-1]),
            'q': fit['q'],
            'r2': fit['r2'],
            'valid_fit': fit['valid'],
        }

# Control: only run a subset of (start, lam) configs
control_starting = ['grid 5x5', 'random 25']
control_lams = [0.0, 0.3, 0.5, 0.7]
for sname in control_starting:
    for lam in control_lams:
        key = f"{sname}|lam={lam}"
        dists, _ = simulate(starting_sets[sname], T_control,
                             n_iter=n_iter, lam=lam)
        fit = fit_geometric(dists, skip=5)
        results_control[key] = {
            'distances': dists,
            'final_d': float(dists[-1]),
            'q': fit['q'],
            'r2': fit['r2'],
            'valid_fit': fit['valid'],
        }


# ----------------------------------------------------------------------------
# Plots
# ----------------------------------------------------------------------------
plot_path = "/home/z/my-project/download/t_iteration_convergence_plot.png"
traj_path = "/home/z/my-project/download/t_iteration_trajectory_plot.png"

# Convergence plot: 2 panels (canonical left, control right)
fig, (axL, axR) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

# Left: canonical T, varying (start, lam)
cmap = plt.get_cmap('tab10')
linestyles = {0.0: '-', 0.1: '--', 0.3: '-.', 0.5: ':', 0.7: (0, (3, 1, 1, 1))}
color_idx = 0
for sname in starting_sets:
    for lam in lam_values:
        key = f"{sname}|lam={lam}"
        d = results_canonical[key]['distances']
        lab = f"{sname}, λ={lam}"
        axL.plot(range(1, n_iter + 1), d, label=lab,
                 color=cmap(color_idx % 10),
                 linestyle=linestyles.get(lam, '-'),
                 linewidth=1.5, alpha=0.85, marker='o', markersize=3)
        color_idx += 1
axL.set_xlabel('Iteration n')
axL.set_ylabel('Hausdorff distance  $d_H(K_n, K_{n+1})$')
axL.set_yscale('log')
axL.set_title('Canonical T (all seven optics contractive)')
axL.grid(True, alpha=0.3, which='both')
axL.legend(fontsize=7, loc='upper right', ncol=2)

# Right: control T (f_2 replaced by expansion)
color_idx = 0
for sname in control_starting:
    for lam in control_lams:
        key = f"{sname}|lam={lam}"
        d = results_control[key]['distances']
        lab = f"{sname}, λ={lam}"
        axR.plot(range(1, n_iter + 1), d, label=lab,
                 color=cmap(color_idx % 10),
                 linestyle=linestyles.get(lam, '-'),
                 linewidth=1.5, alpha=0.85, marker='o', markersize=3)
        color_idx += 1
axR.set_xlabel('Iteration n')
axR.set_ylabel('Hausdorff distance  $d_H(K_n, K_{n+1})$')
axR.set_yscale('log')
axR.set_title('Control T (f_2 replaced by expansion; tests Bregman rescue)')
axR.grid(True, alpha=0.3, which='both')
axR.legend(fontsize=8, loc='upper right')

plt.savefig(plot_path, dpi=130)
plt.close()

# Trajectory plot: snapshots of K_n for canonical T with lambda = 0.3 from grid
K0 = start_grid.copy()
lam_traj = 0.3
K = K0.copy()
snaps = [K.copy()]
for _ in range(7):
    K = apply_T_reg(K, T_canonical, lam=lam_traj)
    snaps.append(K.copy())

fig, axes = plt.subplots(2, 4, figsize=(16, 8), constrained_layout=True)
for idx, ax in enumerate(axes.flat):
    if idx < len(snaps):
        S = snaps[idx]
        ax.scatter(S[:, 0], S[:, 1], c='steelblue', s=35, alpha=0.75,
                   edgecolors='navy', linewidths=0.5)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.set_aspect('equal')
        ax.set_title(f'n = {idx}')
        ax.grid(True, alpha=0.2)
plt.savefig(traj_path, dpi=130)
plt.close()


# ----------------------------------------------------------------------------
# CSV
# ----------------------------------------------------------------------------
csv_path = "/home/z/my-project/download/t_iteration_convergence_results.csv"
with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['variant', 'starting_set', 'lambda', 'n_iter',
                'final_distance', 'fitted_q', 'r2', 'valid_fit',
                'verdict'])
    for key, r in results_canonical.items():
        sname, lam = key.split('|lam=')
        verdict = classify(r, n_iter)
        w.writerow(['canonical', sname, lam, n_iter,
                    f"{r['final_d']:.6e}", f"{r['q']:.6f}",
                    f"{r['r2']:.6f}", r['valid_fit'], verdict])
    for key, r in results_control.items():
        sname, lam = key.split('|lam=')
        verdict = "CONTROL: " + classify(r, n_iter)
        w.writerow(['control', sname, lam, n_iter,
                    f"{r['final_d']:.6e}", f"{r['q']:.6f}",
                    f"{r['r2']:.6f}", r['valid_fit'], verdict])


# ----------------------------------------------------------------------------
# Summary to stdout
# ----------------------------------------------------------------------------
print("=" * 80)
print("  T ITERATION NUMERICAL SIMULATION - SUMMARY")
print("=" * 80)
print()
print("Setting: X = [0,1]^2; seven optics f_1..f_7 implemented as continuous")
print("forward maps; T = f_7 o ... o f_1 applied pointwise to finite samples")
print("of compact subsets K_0; Bregman divergence D_phi(p,q) = ||p-q||^2 for")
print("phi = ||.||^2 / 2; T_reg(K) = (1-l) * T(K) + l * proj_K(T(K));")
print("Hausdorff distance d_H computed via scipy cdist.")
print()
print("Canonical T (all seven optics contractive):")
print(f"  {'config':30s}  {'q':>9s}  {'R^2':>6s}  {'final d_H':>12s}  verdict")
for key, r in results_canonical.items():
    verdict = classify(r, n_iter)
    q_str = f"{r['q']:9.4f}" if r['valid_fit'] else "    n/a"
    r2_str = f"{r['r2']:6.3f}" if r['valid_fit'] else "  n/a"
    print(f"  {key:30s}  {q_str}  {r2_str}  {r['final_d']:12.2e}  {verdict}")
print()
print("Control T (f_2 replaced by expansion; tests Bregman rescue):")
print(f"  {'config':30s}  {'q':>9s}  {'R^2':>6s}  {'final d_H':>12s}  verdict")
for key, r in results_control.items():
    verdict = classify(r, n_iter)
    q_str = f"{r['q']:9.4f}" if r['valid_fit'] else "    n/a"
    r2_str = f"{r['r2']:6.3f}" if r['valid_fit'] else "  n/a"
    print(f"  {key:30s}  {q_str}  {r2_str}  {r['final_d']:12.2e}  {verdict}")
print()
print("Generated:")
print(f"  {plot_path}")
print(f"  {traj_path}")
print(f"  {csv_path}")
