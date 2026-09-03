#!/usr/bin/env python3
"""Verify the exact kernel constant kappa = sqrt(5) for the Levy 3/2
derivation against the frozen artifact CSV, and regenerate the figure
with the corrected theoretical leading constant.

The variance computation (see restore scripts) gives, for the O(sigma)
Gaussian G in the Ito expansion of H = (1/2) oint (x dy - y dx):
  Var(G) = sigma^2 a^2 (1/4 + 1/2 + 2*1/4) = (5/4) sigma^2 a^2
so std(delta H)|_{O(sigma)} = (sqrt(5)/2) sigma a = (sqrt(5 nu)/2) a^{3/2}
under sigma^2 = nu a.  With nu = 0.1: C_fat = sqrt(0.5)/2 = 0.35355.
"""
import csv
import numpy as np
import matplotlib.font_manager as fm

for _f in ('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
    try:
        fm.fontManager.addfont(_f)
    except Exception:
        pass
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

rows = list(csv.DictReader(open('download/levy_stable_3half_derivation.csv')))
a = np.array([float(r['a']) for r in rows])
nu = float(rows[0]['nu'])
y = np.array([float(r['std_delta_H']) for r in rows])

# --- single-exponent log-log fit ---------------------------------
b, logc = np.polyfit(np.log(a), np.log(y), 1)
beta_hat = b
C_hat = np.exp(logc)
pred = C_hat * a ** beta_hat
ss_res = np.sum((y - pred) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2 = 1 - ss_res / ss_tot
print(f"nu = {nu}")
print(f"single-exponent fit: beta = {beta_hat:.4f} (theory 1.5), "
      f"C = {C_hat:.4f}, R^2 = {r2:.6f}")

# --- two-term fit std = c1 a^{3/2} + c2 a -------------------------
A = np.column_stack([a ** 1.5, a])
c1, c2 = np.linalg.lstsq(A, y, rcond=None)[0]
resid = y - (c1 * a ** 1.5 + c2 * a)
r2b = 1 - np.sum(resid ** 2) / ss_tot
print(f"two-term fit: c1 = {c1:.4f}, c2 = {c2:.4f}, R^2 = {r2b:.6f}")

# --- exact theoretical constants ----------------------------------
C_exact = np.sqrt(5 * nu) / 2.0
C_x1only = np.sqrt(nu) / 2.0
print(f"exact C_fat = sqrt(5*nu)/2 = {C_exact:.4f}")
print(f"X1-only (old) constant sqrt(nu)/2 = {C_x1only:.4f}")
print(f"ratio fitted c1 / exact = {c1 / C_exact:.4f}")
print(f"ratio single C / exact = {C_hat / C_exact:.4f}")

# --- OLS t-interval on the slope (df = 12) ------------------------
la, ly = np.log(a), np.log(y)
n = len(a)
b1, b0 = np.polyfit(la, ly, 1)
res = ly - (b0 + b1 * la)
s2 = np.sum(res ** 2) / (n - 2)
sxx = np.sum((la - la.mean()) ** 2)
se_b = np.sqrt(s2 / sxx)
t975 = 2.1788  # t_{0.975,12}
print(f"OLS slope = {b1:.4f}, SE = {se_b:.4f}, "
      f"95% CI = [{b1 - t975 * se_b:.4f}, {b1 + t975 * se_b:.4f}]")

# --- nonparametric bootstrap of the slope (B = 10,000) -----------
rng = np.random.default_rng(20260903)
slopes = []
for _ in range(10_000):
    idx = rng.integers(0, n, n)
    if np.std(la[idx]) < 1e-12:
        continue
    slopes.append(np.polyfit(la[idx], ly[idx], 1)[0])
slopes = np.array(slopes)
print(f"bootstrap SE = {slopes.std(ddof=1):.4f}, "
      f"95% CI = [{np.percentile(slopes, 2.5):.4f}, "
      f"{np.percentile(slopes, 97.5):.4f}]")

# --- regenerate the figure ----------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.4), constrained_layout=True)
ax.loglog(a, y, 'o', color='#1f77b4', ms=6, label='Monte-Carlo '
          '($4{,}000$ seeds per amplitude)')
aa = np.linspace(a.min(), a.max(), 200)
ax.loglog(aa, C_exact * aa ** 1.5, '-', color='#b5651d', lw=1.8,
          label=r'exact leading term $(\sqrt{5\nu}/2)\,a^{3/2}$')
ax.loglog(aa, (nu / (2 * np.sqrt(12))) * aa, '--', color='#2ca02c',
          lw=1.6, label=r'sub-leading L\'evy-area term '
          r'$(\nu/2\sqrt{12})\,a$')
ax.loglog(aa, C_hat * aa ** beta_hat, ':', color='#7f7f7f', lw=1.6,
          label=fr'log--log fit $\hat\beta = {beta_hat:.3f}$ '
          fr'($R^2 = {r2:.4f}$)')
ax.set_xlabel(r'amplitude $a$')
ax.set_ylabel(r'standard deviation of holonomy fluctuation '
              r'$\mathrm{std}(\delta H)$')
ax.legend(loc='upper left', fontsize=8.5, frameon=False)
ax.grid(True, which='both', alpha=0.25, lw=0.5)
fig.savefig('download/levy_stable_3half_derivation.png', dpi=200)
print("figure regenerated: download/levy_stable_3half_derivation.png")
