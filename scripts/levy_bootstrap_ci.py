#!/usr/bin/env python3
"""
Bootstrap 95% CI on the fitted 3/2 exponent from the L\'evy first-passage
Monte-Carlo (14 amplitudes, 4000 seeds each). Resamples the 14 (a, std)
pairs with replacement B=10000 times, refits log-log beta each time, and
reports the 2.5/97.5 percentile band.
"""
import numpy as np

# Data from download/levy_stable_3half_derivation.csv
data = np.array([
    [0.1,                  0.012132368613276056],
    [0.20769230769230768,  0.034204555352842496],
    [0.3153846153846154,   0.06443186578237886],
    [0.423076923076923,    0.09932728639326141],
    [0.5307692307692308,   0.138335041248532],
    [0.6384615384615384,   0.18367045820073716],
    [0.7461538461538461,   0.2302787234001843],
    [0.8538461538461538,   0.2814545104701529],
    [0.9615384615384615,   0.335040679425979],
    [1.0692307692307692,   0.39628676271799407],
    [1.176923076923077,    0.4573934962704173],
    [1.2846153846153847,   0.5192654976751626],
    [1.3923076923076922,   0.5874967604094761],
    [1.5,                  0.6490968410040019],
])

a = data[:, 0]
std = data[:, 1]
log_a = np.log(a)
log_std = np.log(std)

# Point estimate
A = np.vstack([log_a, np.ones_like(log_a)]).T
beta_hat, log_C = np.linalg.lstsq(A, log_std, rcond=None)[0]
print(f"Point estimate: beta_hat = {beta_hat:.6f}")

# Bootstrap
rng = np.random.default_rng(20240829)
B = 10000
boot_betas = np.empty(B)
n = len(a)
for b in range(B):
    idx = rng.integers(0, n, size=n)
    ab = log_a[idx]
    sb = log_std[idx]
    A_b = np.vstack([ab, np.ones_like(ab)]).T
    try:
        beta_b, _ = np.linalg.lstsq(A_b, sb, rcond=None)[0]
        boot_betas[b] = beta_b
    except Exception:
        boot_betas[b] = np.nan

boot_betas = boot_betas[~np.isnan(boot_betas)]
lo = float(np.percentile(boot_betas, 2.5))
hi = float(np.percentile(boot_betas, 97.5))
mean_b = float(np.mean(boot_betas))
std_b = float(np.std(boot_betas, ddof=1))

print(f"Bootstrap (B={B}):")
print(f"  mean   = {mean_b:.6f}")
print(f"  std    = {std_b:.6f}")
print(f"  95% CI = [{lo:.4f}, {hi:.4f}]")
print(f"  Theoretical 3/2 = 1.5000  -> inside CI? {lo <= 1.5 <= hi}")

# Two-sided test against theoretical 3/2 = 1.5
z = (beta_hat - 1.5) / std_b
print(f"  z-stat vs 1.5: {z:.4f}  (two-sided p ~ {2 * (1 - 0.5*(1 + np.tanh(z/np.sqrt(2)/np.sqrt(2)*2))):.4f})")

# Also report a simpler CI using analytical standard error of the slope
# SE(beta) = sigma_resid / sqrt(sum((x_i - x_bar)^2))
x_bar = log_a.mean()
ss_xx = np.sum((log_a - x_bar) ** 2)
residuals = log_std - (beta_hat * log_a + log_C)
ss_res = np.sum(residuals ** 2)
sigma2 = ss_res / (n - 2)  # residual variance
se_beta = np.sqrt(sigma2 / ss_xx)
print(f"\nAnalytical (OLS) SE(beta) = {se_beta:.6f}")
t_stat = (beta_hat - 1.5) / se_beta
print(f"  t-stat vs 1.5: {t_stat:.4f}  (df={n-2})")
# 95% CI on slope using t_{n-2, 0.975}
from scipy import stats
t_crit = stats.t.ppf(0.975, df=n - 2)
ci_lo = beta_hat - t_crit * se_beta
ci_hi = beta_hat + t_crit * se_beta
print(f"  95% t-CI (df={n-2}) = [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"  Theoretical 3/2 = 1.5000  -> inside CI? {ci_lo <= 1.5 <= ci_hi}")
