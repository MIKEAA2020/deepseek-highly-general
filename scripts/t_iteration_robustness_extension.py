#!/usr/bin/env python3
"""
Extension of the T iteration robustness simulation along two new axes
requested by the user.

  Axis 1 — Higher-dimensional sweep.
    Dimensions extended from {2, 3, 4, 5} to {2, 3, 5, 10, 20}. The
    per-coordinate contraction factor is held d-independent, isolating
    the ambient-dimension effect on the Bregman-regularized tail. For
    d = 10 and d = 20 the regular-grid and hypercube-corner starting
    sets are replaced by a deterministic low-discrepancy (Halton)
    sample and a deterministic 8-corner subsample, respectively,
    keeping the point-cloud size tractable (capping N at ~27) so the
    Hausdorff computation stays O(N^2 * d).

  Axis 2 — Rotated ("structured-noise") expansion profiles.
    The previous simulation's expansion optic multiplied the FIRST
    coordinate by 1.15 while leaving other coordinates contractive
    — an axis-aligned expansion. Here we add two new profiles in
    which the expansion is applied along a rotated direction:
        k = 3 rotated  (f_2, f_4, f_6 simultaneously rotated-expanded)
        k = 7 rotated  (every optic rotated-expanded, fully adversarial)
    The linear part of each rotated-expanded optic is
        L = R @ diag(1.15, alpha, alpha, ..., alpha) @ R^T
    where R is the product of consecutive Givens rotations
    (k, k+1 plane) at angle theta = pi/4. This rotates the expansion
    direction uniformly across all d coordinates, breaking the
    axis-aligned symmetry that the Bregman projection may have
    exploited. The fixed point of each rotated optic is still its
    interior center c_i (because L @ c + (I - L) @ c = c for any L),
    so the composition T still has a well-defined fixed point; the
    question is whether the rotated profile produces more WEAK
    (q < 1, R^2 < 0.9) verdicts than the axis-aligned one.

Outputs:
  - download/t_iteration_robustness_extension_axis_aligned.png
    6 x 3 panel grid: rows = d in {2, 3, 5, 10, 20}, cols = canonical,
    k=3 axis, k=7 axis. (The canonical column is the baseline for the
    same starting sets and lambdas.)
  - download/t_iteration_robustness_extension_rotated.png
    6 x 2 panel grid: rows = d, cols = k=3 rotated, k=7 rotated.
  - download/t_iteration_robustness_extension_results.csv
    Per-configuration summary across all 5 dimensions x 5 profiles
    x 3 starting sets x 5 lambdas = 375 configurations.
"""

import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.stats import qmc

import matplotlib.font_manager as fm
for p in ['/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
          '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(p):
        fm.fontManager.addfont(p)
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ----------------------------------------------------------------------------
# Optic parameters (same as the original robustness script).
# ----------------------------------------------------------------------------
_OPTIC_PARAMS = [
    (0.60, 0.125),   # f1 RAF
    (0.50, 0.700),   # f2 RPSI
    (0.55, 0.725),   # f3 IFS
    (0.65, 0.500),   # f4 Noether
    (0.70, 0.250),   # f5 Perturbation
    (0.50, 0.800),   # f6 WCIG
    (0.55, 0.450),   # f7 Fisher-Rao
]


def _center(i, d):
    seed = _OPTIC_PARAMS[i][1]
    rng = np.random.RandomState(int(seed * 1e6) + i)
    c = rng.rand(d)
    return 0.15 + 0.70 * c


def build_rotation(d, theta=np.pi / 4):
    """Product of consecutive Givens rotations in (k, k+1) plane."""
    R = np.eye(d)
    for k in range(d - 1):
        G = np.eye(d)
        c, s = np.cos(theta), np.sin(theta)
        G[k, k] = c
        G[k, k + 1] = -s
        G[k + 1, k] = s
        G[k + 1, k + 1] = c
        R = R @ G
    return R


def make_optic(i, d, expand=False, rotated=False):
    """Build optic i in dimension d.

    expand : if True, the optic's linear part has eigenvalues
             {1.15, alpha, alpha, ...} instead of {alpha, alpha, ...}.
    rotated : if True (and expand=True), the expansion direction is
             rotated by R @ diag(...) @ R^T where R is a product of
             consecutive Givens rotations at theta = pi/4.
    """
    alpha, _ = _OPTIC_PARAMS[i]
    c = _center(i, d)

    if expand:
        # eigenvalues of L: 1.15 along direction 0, alpha along others
        evals = np.full(d, alpha)
        evals[0] = 1.15
        if rotated:
            R = build_rotation(d, theta=np.pi / 4)
            L = R @ np.diag(evals) @ R.T
        else:
            L = np.diag(evals)
    else:
        L = np.diag(np.full(d, alpha))

    # Precompute the affine translation (I - L) @ c
    bias = (np.eye(d) - L) @ c

    def f(p):
        p = np.asarray(p, dtype=float)
        # f(p) = L @ p + bias + small structured perturbation
        # The perturbation is sinusoidal in each coordinate (deterministic,
        # small amplitude), present in both axis-aligned and rotated
        # variants — it is the "structured noise" component.
        eps = 0.03
        mod = eps * np.sin(np.pi * p)
        out = p @ L.T + bias + mod
        return np.clip(out, 0.0, 1.0)
    return f


def build_T(d, profile):
    """profile is (name, expand_indices, rotated_flag)."""
    name, expand_idx, rotated = profile
    expand_set = set(expand_idx)
    fs = [make_optic(i, d,
                     expand=(i in expand_set),
                     rotated=rotated)
          for i in range(7)]

    def T(p):
        for f in fs:
            p = f(p)
        return p
    return T


# ----------------------------------------------------------------------------
# Bregman-regularized operator, Hausdorff distance, fitting, classification.
# ----------------------------------------------------------------------------
def apply_T_reg(K, T, lam=0.0):
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
    for _ in range(n_iter):
        K_new = apply_T_reg(K, T, lam=lam)
        d = hausdorff(K, K_new)
        dists.append(d)
        K = K_new
    return np.array(dists)


def fit_geometric(dists, skip=5):
    out = {'valid': False, 'q': float('nan'), 'r2': float('nan')}
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
    out.update({'valid': True, 'q': q, 'r2': float(r2)})
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
# Starting sets in dimension d (with high-dimension safeguards).
# ----------------------------------------------------------------------------
def start_halton_d(d, n=27):
    """Halton low-discrepancy points in [0.05, 0.95]^d."""
    sampler = qmc.Halton(d=d, seed=42)
    pts = sampler.random(n)
    return 0.05 + 0.90 * pts


def start_random_d(d, n=27):
    rng = np.random.RandomState(42)
    return rng.rand(n, d)


def start_corners_d(d, k=8):
    """k deterministic corners of [0.05, 0.95]^d."""
    rng = np.random.RandomState(123)
    n_corners = min(k, 2 ** d)
    indices = rng.choice(2 ** d, size=n_corners, replace=False)
    pts = np.zeros((n_corners, d))
    for i, idx in enumerate(indices):
        for b in range(d):
            pts[i, b] = 0.05 if (idx >> b) & 1 == 0 else 0.95
    return pts


# ----------------------------------------------------------------------------
# Run.
# ----------------------------------------------------------------------------
DIMENSIONS = [2, 3, 5, 10, 20]

PROFILES = [
    # (display name, expand_indices, rotated_flag)
    ('canonical',                       (),                    False),
    ('k=3 axis',                         (1, 3, 5),             False),
    ('k=7 axis',                         (0, 1, 2, 3, 4, 5, 6), False),
    ('k=3 rotated',                      (1, 3, 5),             True),
    ('k=7 rotated',                      (0, 1, 2, 3, 4, 5, 6), True),
]

LAM_VALUES = [0.0, 0.3, 0.5, 0.7, 0.9]
N_ITER = 40

np.random.seed(42)

# Starting sets per dimension
starting_sets_by_dim = {}
for d in DIMENSIONS:
    starting_sets_by_dim[d] = {
        'halton 27':   start_halton_d(d, n=27),
        'random 27':   start_random_d(d, n=27),
        'corners 8':   start_corners_d(d, k=8),
    }

results = {}
all_dists = {}

for d in DIMENSIONS:
    for pname, expand_idx, rotated in PROFILES:
        T = build_T(d, (pname, expand_idx, rotated))
        for sname, K0 in starting_sets_by_dim[d].items():
            for lam in LAM_VALUES:
                key = f"d={d}|{pname}|{sname}|lam={lam}"
                dists = simulate(K0, T, n_iter=N_ITER, lam=lam)
                fit = fit_geometric(dists, skip=5)
                r = {
                    'distances': dists,
                    'final_d': float(dists[-1]),
                    'q': fit['q'],
                    'r2': fit['r2'],
                    'valid_fit': fit['valid'],
                }
                results[key] = r
                all_dists[(d, pname, sname, lam)] = dists


# ----------------------------------------------------------------------------
# CSV.
# ----------------------------------------------------------------------------
csv_path = "/home/z/my-project/download/t_iteration_robustness_extension_results.csv"
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
# Convergence plots.
# ----------------------------------------------------------------------------
cmap = plt.get_cmap('tab10')
linestyles = {0.0: '-', 0.3: '--', 0.5: '-.', 0.7: ':', 0.9: (0, (3, 1, 1, 1))}

# Plot 1: axis-aligned profiles (canonical, k=3 axis, k=7 axis)
axis_profiles = ['canonical', 'k=3 axis', 'k=7 axis']
plot1 = "/home/z/my-project/download/t_iteration_robustness_extension_axis_aligned.png"
fig, axes = plt.subplots(len(DIMENSIONS), len(axis_profiles),
                         figsize=(18, 22), constrained_layout=True)
for ri, d in enumerate(DIMENSIONS):
    for ci, pname in enumerate(axis_profiles):
        ax = axes[ri, ci]
        color_idx = 0
        for sname in starting_sets_by_dim[d]:
            for lam in LAM_VALUES:
                dists = all_dists[(d, pname, sname, lam)]
                ax.plot(range(1, N_ITER + 1), dists,
                        label=f"{sname}, λ={lam}",
                        color=cmap(color_idx % 10),
                        linestyle=linestyles.get(lam, '-'),
                        linewidth=1.3, alpha=0.85, marker='o', markersize=2.5)
                color_idx += 1
        ax.set_yscale('log')
        ax.set_xlabel('Iteration n')
        ax.set_ylabel(r'$d_H(K_n, K_{n+1})$')
        ax.set_title(f'd = {d}   |   {pname}')
        ax.grid(True, alpha=0.3, which='both')
        if ri == 0 and ci == 0:
            ax.legend(fontsize=6, loc='upper right', ncol=2)
plt.savefig(plot1, dpi=130)
plt.close()

# Plot 2: rotated profiles
rot_profiles = ['k=3 rotated', 'k=7 rotated']
plot2 = "/home/z/my-project/download/t_iteration_robustness_extension_rotated.png"
fig, axes = plt.subplots(len(DIMENSIONS), len(rot_profiles),
                         figsize=(13, 22), constrained_layout=True)
for ri, d in enumerate(DIMENSIONS):
    for ci, pname in enumerate(rot_profiles):
        ax = axes[ri, ci]
        color_idx = 0
        for sname in starting_sets_by_dim[d]:
            for lam in LAM_VALUES:
                dists = all_dists[(d, pname, sname, lam)]
                ax.plot(range(1, N_ITER + 1), dists,
                        label=f"{sname}, λ={lam}",
                        color=cmap(color_idx % 10),
                        linestyle=linestyles.get(lam, '-'),
                        linewidth=1.3, alpha=0.85, marker='o', markersize=2.5)
                color_idx += 1
        ax.set_yscale('log')
        ax.set_xlabel('Iteration n')
        ax.set_ylabel(r'$d_H(K_n, K_{n+1})$')
        ax.set_title(f'd = {d}   |   {pname}')
        ax.grid(True, alpha=0.3, which='both')
        if ri == 0 and ci == 0:
            ax.legend(fontsize=6, loc='upper right', ncol=2)
plt.savefig(plot2, dpi=130)
plt.close()


# ----------------------------------------------------------------------------
# Summary to stdout.
# ----------------------------------------------------------------------------
print("=" * 95)
print("  T ITERATION ROBUSTNESS EXTENSION — SUMMARY")
print("=" * 95)
print()
print("Axes tested:")
print(f"  * Dimension:        d in {DIMENSIONS}")
print("  * Profile:          {[p[0] for p in PROFILES]}")
print(f"  * Bregman lambda:   {LAM_VALUES}")
print(f"  * Total configs:    {len(DIMENSIONS) * len(PROFILES) * 3 * len(LAM_VALUES)}")
print()

# Verdict counts per (dimension, profile)
print(f"  {'(d, profile)':28s}  {'configs':>7s}  {'CONFIRMED':>9s}  "
      f"{'STRONG':>7s}  {'WEAK':>5s}  {'NO-CONTRACTION':>15s}")
for d in DIMENSIONS:
    for pname, _, _ in PROFILES:
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
        print(f"  ({d}, {pname:23s})  {len(keys):7d}  {confirmed:9d}  "
              f"{strong:7d}  {weak:5d}  {no_cont:15d}")
print()

# Aggregate totals per profile
print("Aggregate per profile (across all dimensions):")
print(f"  {'profile':28s}  {'configs':>7s}  {'CONFIRMED':>9s}  "
      f"{'STRONG':>7s}  {'WEAK':>5s}  {'NO-CONTRACTION':>15s}")
for pname, _, _ in PROFILES:
    keys = [k for k in results if f"|{pname}|" in k]
    confirmed = strong = weak = no_cont = 0
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
    print(f"  {pname:28s}  {len(keys):7d}  {confirmed:9d}  "
          f"{strong:7d}  {weak:5d}  {no_cont:15d}")
print()

# Highest-lambda q values per (d, profile)
print("Per-(d, profile) at the strongest Bregman lambda = 0.9:")
print(f"  {'(d, profile)':28s}  {'start':>10s}  {'q':>8s}  {'R^2':>6s}  "
      f"{'final d_H':>12s}  verdict")
for d in DIMENSIONS:
    for pname, _, _ in PROFILES:
        for sname in starting_sets_by_dim[d]:
            k = f"d={d}|{pname}|{sname}|lam=0.9"
            r = results[k]
            v = classify(r)
            q_str = f"{r['q']:8.4f}" if r['valid_fit'] else "    n/a"
            r2_str = f"{r['r2']:6.3f}" if r['valid_fit'] else "  n/a"
            print(f"  ({d}, {pname:23s})  {sname:>10s}  "
                  f"{q_str}  {r2_str}  {r['final_d']:12.2e}  {v}")
print()

print("Generated:")
print(f"  {plot1}")
print(f"  {plot2}")
print(f"  {csv_path}")
