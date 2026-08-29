#!/usr/bin/env python3
"""
Robustness extension of the T iteration simulation.

This script extends the simulation in `t_iteration_simulation.py` along two
axes requested by the user:

  Axis 1 — Higher-dimensional base spaces.
    The base space is now X = [0,1]^d for d in {2, 3, 4, 5}. Each optic f_i
    is implemented as a continuous forward map f_i : X -> X that contracts
    uniformly toward an interior fixed point. The contraction ratio of the
    canonical T is independent of d (it is the product of per-coordinate
    contraction factors), so the test is whether the *Bregman-regularized
    contraction behavior* persists as the dimension grows — i.e. whether
    the Hausdorff-distance geometric tail remains measurable.

  Axis 2 — Non-contraction optics (multiple simultaneous expansions).
    We replace not one but k of the seven optics with expansion maps
    (determinant > 1 in the linear part) and ask: how many expansions can
    the Bregman regularization absorb before the iteration stops contracting?
    Three expansion profiles are tested:
       k = 1  : only f_2 is replaced (control from the previous script).
       k = 3  : f_2, f_4, f_6 are replaced (alternating).
       k = 7  : every optic is replaced (fully expansive T).
    For each profile we sweep lambda in {0.0, 0.3, 0.5, 0.7, 0.9}.

Outputs:
  - download/t_iteration_robustness_convergence_plot.png
    One 4 x 3 panel grid (rows = dimensions 2..5, columns = profiles 1/3/7).
  - download/t_iteration_robustness_trajectory_d3.png
    Trajectory snapshots in 3-D (projection onto first 3 coords).
  - download/t_iteration_robustness_results.csv
    Per-configuration final distance, fitted q, R^2, verdict.
"""

import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (register 3D projection)
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
# d-dimensional optics.
#
# Each canonical optic is an affine contraction toward an interior fixed
# point. To make the per-coordinate contraction factors match across
# dimensions, the linear part is alpha * I (uniform shrinkage), and the
# translation is (1 - alpha) * c for a per-optic center c in (0,1)^d. A
# small nonlinear perturbation is added to break coordinate-axis symmetry
# so the contraction is not axis-aligned (matches the d=2 script's style).
#
# Expansion variants multiply the linear part by a factor > 1 along the
# first coordinate only, keeping the rest contractive — this is the
# minimal d-dimensional extension of the d=2 control's f2 expansion.
# ----------------------------------------------------------------------------

# Centers and contraction factors per optic (chosen to mirror the d=2
# script so the canonical profile at d=2 reproduces the previously
# confirmed contraction there).
_OPTIC_PARAMS = [
    # (alpha, center seed)
    (0.60, 0.125),   # f1 RAF
    (0.50, 0.700),   # f2 RPSI
    (0.55, 0.725),   # f3 IFS
    (0.65, 0.500),   # f4 Noether
    (0.70, 0.250),   # f5 Perturbation
    (0.50, 0.800),   # f6 WCIG
    (0.55, 0.450),   # f7 Fisher-Rao
]


def _center(i, d):
    """Per-optic center in (0,1)^d, derived deterministically from a seed."""
    seed = _OPTIC_PARAMS[i][1]
    # Use a fixed LCG so the center is the same across runs / dimensions
    # for a given optic, but distinct coordinates.
    rng = np.random.RandomState(int(seed * 1e6) + i)
    c = rng.rand(d)
    # Bias toward interior so the fixed point stays inside [0,1]^d.
    return 0.15 + 0.70 * c


def make_optic(i, d, expand=False):
    """Build optic i in dimension d.

    If expand=False, returns a contractive affine map with mild nonlinear
    perturbation; if expand=True, returns an expansion along the first
    coordinate (factor 1.15) with the remaining coordinates still contractive.
    """
    alpha, _ = _OPTIC_PARAMS[i]
    c = _center(i, d)

    if expand:
        # First coordinate multiplied by 1.15, others by alpha.
        scales = np.full(d, alpha)
        scales[0] = 1.15
    else:
        scales = np.full(d, alpha)

    # Precompute the affine part
    def f(p):
        p = np.asarray(p, dtype=float)
        # nonlinear perturbation: small sinusoidal modulation
        # (kept identical across coordinates so the contraction factor is
        # bounded by max(alpha, 1.15) plus an O(eps) term; eps is small
        # enough that the contraction constant remains numerically alpha
        # for the contractive optics and 1.15 for the expansion optic).
        eps = 0.03
        if p.ndim == 1:
            mod = eps * np.sin(np.pi * p)
        else:
            mod = eps * np.sin(np.pi * p)
        # affine + perturbation, then clamp to [0,1]^d for compactness
        out = scales * p + (1.0 - scales) * c + mod * (scales < 1.0)
        return np.clip(out, 0.0, 1.0)
    return f


def build_T(d, expand_indices=()):
    """Return the composed operator T = f_7 o ... o f_1 in dimension d.

    expand_indices: iterable of optic indices (0..6) to swap for expansions.
    """
    expand_set = set(expand_indices)
    fs = [make_optic(i, d, expand=(i in expand_set)) for i in range(7)]

    def T(p):
        for f in fs:
            p = f(p)
        return p
    return T


# ----------------------------------------------------------------------------
# Bregman-regularized operator and Hausdorff distance (general d).
# ----------------------------------------------------------------------------

def apply_T_reg(K, T, lam=0.0):
    """T_reg(K) = (1-lambda) * T(K) + lambda * proj_K(T(K)).

    For phi = ||.||^2 / 2, the Bregman projection is the nearest point, so
    proj_K is computed via scipy.spatial.distance.cdist.
    """
    TK = T(K)
    if lam <= 0.0:
        return TK
    D = cdist(TK, K)
    idx = D.argmin(axis=1)
    proj = K[idx]
    return (1.0 - lam) * TK + lam * proj


def hausdorff(A, B):
    if len(A) == 0 or len(B) == 0:
        return float('inf')
    D = cdist(A, B)
    return max(D.min(axis=1).max(), D.min(axis=0).max())


def simulate(K0, T, n_iter=40, lam=0.0):
    K = K0.copy()
    dists = []
    snaps = [K.copy()]
    for _ in range(n_iter):
        K_new = apply_T_reg(K, T, lam=lam)
        d = hausdorff(K, K_new)
        dists.append(d)
        snaps.append(K_new.copy())
        K = K_new
    return np.array(dists), snaps


def fit_geometric(dists, skip=5):
    """Fit log(d) = a + b*n on the post-transient tail."""
    out = {'valid': False, 'q': float('nan'), 'r2': float('nan'),
           'slope': float('nan'), 'intercept': float('nan')}
    if len(dists) <= skip + 3:
        return out
    tail = dists[skip:].astype(float)
    if np.any(tail <= 0):
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


def classify(r):
    if not r['valid_fit']:
        if r['final_d'] < 1e-10:
            return 'STRONG-CONVERGED (machine precision; no tail)'
        return 'FIT INVALID (insufficient tail)'
    if r['final_d'] < 1e-10 and r['q'] < 1:
        return 'STRONG-CONVERGED (machine precision; q<1)'
    if r['q'] < 1 and r['r2'] >= 0.9:
        return f"CONFIRMED (q={r['q']:.4f}, R^2={r['r2']:.4f})"
    if r['q'] >= 1:
        return f"NO-CONTRACTION (q={r['q']:.4f} >= 1)"
    return f"WEAK (q={r['q']:.4f}, R^2={r['r2']:.4f})"


# ----------------------------------------------------------------------------
# Starting sets in dimension d.
# ----------------------------------------------------------------------------

def start_grid_d(d, side=3):
    """Regular grid of side^d points in (0.05, 0.95)^d."""
    coords = np.linspace(0.05, 0.95, side)
    mesh = np.meshgrid(*([coords] * d), indexing='ij')
    pts = np.stack([m.flatten() for m in mesh], axis=-1)
    return pts


def start_random_d(d, n=27):
    rng = np.random.RandomState(42)
    return rng.rand(n, d)


def start_corners_d(d):
    """2^d corners of the unit hypercube, inset by 0.05."""
    from itertools import product
    coords = [0.05, 0.95]
    pts = np.array(list(product(coords, repeat=d)), dtype=float)
    return pts


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------

DIMENSIONS = [2, 3, 4, 5]
EXPANSION_PROFILES = {
    'canonical (k=0)':  (),
    'k=1 expansion  (f2)':                 (1,),
    'k=3 expansions (f2,f4,f6)':           (1, 3, 5),
    'k=7 expansion  (all optics)':         (0, 1, 2, 3, 4, 5, 6),
}
LAM_VALUES = [0.0, 0.3, 0.5, 0.7, 0.9]
N_ITER = 40

np.random.seed(42)

# Pre-build starting sets per dimension.
starting_sets_by_dim = {}
for d in DIMENSIONS:
    starting_sets_by_dim[d] = {
        f'grid {3**d if d<=3 else 27}':  start_grid_d(d, side=3 if d <= 3 else 2)[:27] if d > 3 else start_grid_d(d, side=3),
        'random 27':                      start_random_d(d, 27),
        f'corners {2**d}':                start_corners_d(d),
    }

# Storage
results = {}  # key -> dict
all_dists_for_plot = {}  # (d, profile, start, lam) -> distances

for d in DIMENSIONS:
    for pname, expand_idx in EXPANSION_PROFILES.items():
        T = build_T(d, expand_indices=expand_idx)
        for sname, K0 in starting_sets_by_dim[d].items():
            for lam in LAM_VALUES:
                key = f"d={d}|{pname}|{sname}|lam={lam}"
                dists, _ = simulate(K0, T, n_iter=N_ITER, lam=lam)
                fit = fit_geometric(dists, skip=5)
                r = {
                    'distances': dists,
                    'final_d': float(dists[-1]),
                    'q': fit['q'],
                    'r2': fit['r2'],
                    'valid_fit': fit['valid'],
                }
                results[key] = r
                all_dists_for_plot[(d, pname, sname, lam)] = dists


# ----------------------------------------------------------------------------
# CSV
# ----------------------------------------------------------------------------
csv_path = "/home/z/my-project/download/t_iteration_robustness_results.csv"
with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['dimension', 'profile', 'starting_set', 'lambda', 'n_iter',
                'final_distance', 'fitted_q', 'r2', 'valid_fit', 'verdict'])
    for key, r in results.items():
        parts = key.split('|')
        d_str, pname, sname, lam_str = parts
        d_val = int(d_str.split('=')[1])
        lam_val = float(lam_str.split('=')[1])
        verdict = classify(r)
        w.writerow([d_val, pname, sname, lam_val, N_ITER,
                    f"{r['final_d']:.6e}",
                    f"{r['q']:.6f}" if r['valid_fit'] else "n/a",
                    f"{r['r2']:.6f}" if r['valid_fit'] else "n/a",
                    r['valid_fit'], verdict])


# ----------------------------------------------------------------------------
# Convergence plot: 4 (rows = d) x 3 (cols = profiles k=1, k=3, k=7)
# canonical is summarized separately in the CSV; the figure focuses on the
# expansion profiles because those are the new test axis.
# ----------------------------------------------------------------------------
plot_path = "/home/z/my-project/download/t_iteration_robustness_convergence_plot.png"
profile_cols = ['k=1 expansion  (f2)',
                'k=3 expansions (f2,f4,f6)',
                'k=7 expansion  (all optics)']

cmap = plt.get_cmap('tab10')
linestyles = {0.0: '-', 0.3: '--', 0.5: '-.', 0.7: ':', 0.9: (0, (3, 1, 1, 1))}

fig, axes = plt.subplots(len(DIMENSIONS), len(profile_cols),
                         figsize=(18, 14), constrained_layout=True)

for ri, d in enumerate(DIMENSIONS):
    for ci, pname in enumerate(profile_cols):
        ax = axes[ri, ci]
        color_idx = 0
        for sname in starting_sets_by_dim[d]:
            for lam in LAM_VALUES:
                dists = all_dists_for_plot[(d, pname, sname, lam)]
                ax.plot(range(1, N_ITER + 1), dists,
                        label=f"{sname}, λ={lam}",
                        color=cmap(color_idx % 10),
                        linestyle=linestyles.get(lam, '-'),
                        linewidth=1.4, alpha=0.85, marker='o', markersize=2.5)
                color_idx += 1
        ax.set_yscale('log')
        ax.set_xlabel('Iteration n')
        ax.set_ylabel(r'$d_H(K_n, K_{n+1})$')
        ax.set_title(f'd = {d}   |   {pname}')
        ax.grid(True, alpha=0.3, which='both')
        if ri == 0 and ci == 0:
            ax.legend(fontsize=6, loc='upper right', ncol=2)
plt.savefig(plot_path, dpi=130)
plt.close()


# ----------------------------------------------------------------------------
# 3-D trajectory plot for d=3, canonical profile, lambda=0.5, grid start.
# Shows iterates collapsing to the fixed point in 3-D space.
# ----------------------------------------------------------------------------
traj_path = "/home/z/my-project/download/t_iteration_robustness_trajectory_d3.png"
d_traj = 3
T_traj = build_T(d_traj, expand_indices=())
K0_traj = start_grid_d(d_traj, side=3)
K_traj = K0_traj.copy()
snaps = [K_traj.copy()]
for _ in range(6):
    K_traj = apply_T_reg(K_traj, T_traj, lam=0.5)
    snaps.append(K_traj.copy())

fig = plt.figure(figsize=(18, 10), constrained_layout=True)
for idx in range(7):
    ax = fig.add_subplot(2, 4, idx + 1, projection='3d')
    S = snaps[idx]
    ax.scatter(S[:, 0], S[:, 1], S[:, 2], c='steelblue', s=25, alpha=0.75,
               depthshade=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)
    ax.set_title(f'n = {idx}')
    ax.set_xlabel('x0')
    ax.set_ylabel('x1')
    ax.set_zlabel('x2')
plt.savefig(traj_path, dpi=130)
plt.close()


# ----------------------------------------------------------------------------
# Summary to stdout
# ----------------------------------------------------------------------------
print("=" * 90)
print("  T ITERATION ROBUSTNESS SIMULATION - SUMMARY")
print("=" * 90)
print()
print("Axes tested:")
print("  * Dimension:        d in {2, 3, 4, 5}")
print("  * Expansion profile: k in {0 (canonical), 1, 3, 7}")
print("  * Bregman lambda:   {0.0, 0.3, 0.5, 0.7, 0.9}")
print()

# Verdict counts per (dimension, profile)
print(f"  {'(d, profile)':42s}  {'configs':>7s}  {'CONFIRMED':>9s}  "
      f"{'STRONG':>7s}  {'WEAK':>5s}  {'NO-CONTRACTION':>15s}")
for d in DIMENSIONS:
    for pname in EXPANSION_PROFILES:
        keys = [k for k in results
                if k.startswith(f"d={d}|{pname}|")]
        confirmed = 0
        strong = 0
        weak = 0
        no_cont = 0
        for k in keys:
            v = classify(results[k])
            if v.startswith('CONFIRMED'):
                confirmed += 1
            elif v.startswith('STRONG'):
                strong += 1
            elif v.startswith('WEAK'):
                weak += 1
            elif v.startswith('NO-CONTRACTION'):
                no_cont += 1
        print(f"  ({d}, {pname:37s})  {len(keys):7d}  {confirmed:9d}  "
              f"{strong:7d}  {weak:5d}  {no_cont:15d}")
print()

# Highest-lambda (best chance to contract under Bregman) results per (d, profile)
print("Per-(d, profile) at the strongest Bregman lambda = 0.9:")
print(f"  {'(d, profile)':42s}  {'starting set':>12s}  "
      f"{'q':>8s}  {'R^2':>6s}  {'final d_H':>12s}  verdict")
for d in DIMENSIONS:
    for pname in EXPANSION_PROFILES:
        for sname in starting_sets_by_dim[d]:
            k = f"d={d}|{pname}|{sname}|lam=0.9"
            r = results[k]
            v = classify(r)
            q_str = f"{r['q']:8.4f}" if r['valid_fit'] else "    n/a"
            r2_str = f"{r['r2']:6.3f}" if r['valid_fit'] else "  n/a"
            print(f"  ({d}, {pname:37s})  {sname:>12s}  "
                  f"{q_str}  {r2_str}  {r['final_d']:12.2e}  {v}")
print()

print("Generated:")
print(f"  {plot_path}")
print(f"  {traj_path}")
print(f"  {csv_path}")
