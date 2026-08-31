#!/usr/bin/env python3
"""
Compute Fisher-z 95% CI and two-tailed p-values for the v12 and v13
per-gene Pearson r values on E10 (n=92 Lemuth genes).

Used to correct the manuscript v13 paragraph:
  - v12 r = +0.1024 (gene-level mask, τ=0.005..0.20)
  - v13 r = +0.0838 (Keio b-number fallback patched E10, 15 MAPPED + 77 GLOBAL)

The manuscript v13 paragraph incorrectly claimed r_v13 = +0.1472, which is
actually the delta from the unmasked baseline (-0.0633), not the absolute r.
"""
import numpy as np
from scipy.stats import norm, pearsonr


def fisher_z_ci(r: float, n: int, alpha: float = 0.05):
    """Return (lo, hi) 95% CI for r via Fisher z-transform."""
    if abs(r) >= 1.0:
        return float("nan"), float("nan")
    z = 0.5 * np.log((1 + r) / (1 - r))
    se = 1.0 / np.sqrt(n - 3)
    zlo = z - norm.ppf(1 - alpha / 2) * se
    zhi = z + norm.ppf(1 - alpha / 2) * se
    # inverse Fisher
    rlo = (np.exp(2 * zlo) - 1) / (np.exp(2 * zlo) + 1)
    rhi = (np.exp(2 * zhi) - 1) / (np.exp(2 * zhi) + 1)
    return float(rlo), float(rhi)


def two_tailed_p(r: float, n: int):
    """Two-tailed p-value for Pearson r under H0: rho=0."""
    if abs(r) >= 1.0:
        return float("nan")
    z = 0.5 * np.log((1 + r) / (1 - r))
    se = 1.0 / np.sqrt(n - 3)
    return 2.0 * (1.0 - norm.cdf(abs(z) / se))


N = 92
print("Fisher-z 95% CI and two-tailed p for E10 per-gene max Pearson r")
print("=" * 72)
print(f"{'variant':<35} {'r':>8} {'n':>4} {'CI low':>9} {'CI high':>9} {'p (2-tail)':>11}")
print("-" * 72)
for label, r in [
    ("unmasked (baseline)", -0.0633),
    ("v12 gene-level mask", +0.1024),
    ("v13 Keio b-number fallback", +0.0838),
    ("v13 MAPPED-only (n=15)", -0.1579),
]:
    if "MAPPED-only" in label:
        n_use = 15
    else:
        n_use = N
    lo, hi = fisher_z_ci(r, n_use)
    p = two_tailed_p(r, n_use)
    print(f"{label:<35} {r:+8.4f} {n_use:>4} {lo:+9.4f} {hi:+9.4f} {p:>11.4f}")

# deltas
print("\nDelta table (vs unmasked baseline r = -0.0633):")
print(f"  v12 - unmasked = +0.1024 - (-0.0633) = {0.1024 - (-0.0633):+.4f}")
print(f"  v13 - unmasked = +0.0838 - (-0.0633) = {0.0838 - (-0.0633):+.4f}")
print(f"  v13 - v12      = +0.0838 - (+0.1024) = {0.0838 - 0.1024:+.4f}  (v13 is WEAKER than v12)")

print("\nKey correction to manuscript v13 paragraph:")
print(f"  Manuscript claims: r_v13 = +0.1472  (WRONG — that is the delta, not the r)")
print(f"  Actual:             r_v13 = +0.0838  (delta from unmasked = +0.1472)")
print(f"  Manuscript claims:  Δ above v12 = +0.045 (STRENGTHENED)")
print(f"  Actual:             Δ above v12 = -0.019 (slightly weaker, but sign flip preserved)")
