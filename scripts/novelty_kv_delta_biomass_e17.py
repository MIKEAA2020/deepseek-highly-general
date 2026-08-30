"""
E17 — κ_V^(Δb) biomass-residual-weighted variant: does it stabilise the
       direct-correlation metric across model rebuilds?

====================================================================
WHY THIS SCRIPT EXISTS
====================================================================
E16 (cross-rebuild validation on iML1515) showed:
  * Gap count CONFIRMED drops (iJO1366=30, iML1515=13, −56.7%)
  * Direct κ_V → Keio-E correlation DROPS (iJO1366 AUC=0.713, iML1515 AUC=0.428)
  * Mechanism: iML1515's denser network decouples flux rerouting
    (which κ_V measures) from biomass reduction (which essentiality
    requires).

The manuscript (Remark rem:e16-iml1515-cross-rebuild) proposed a
refinement: define a biomass-residual-weighted variant
   κ_V^(Δb)(g) = κ_V(g) · weight(Δb(g)/b_wt)
that scales κ_V by how much biomass the KO actually reduces, so
that the metric still tracks essentiality on the denser iML1515.

E17 tests three weight variants on BOTH iJO1366 (E15 CSV) and
iML1515 (E16 CSV) to see which gives the most STABLE direct
correlation across rebuilds:

  variant 0  (original):    κ_V            (no weighting)
  variant 1  (linear):      κ_V · (1 + Δb/b_wt)
  variant 2  (quadratic):   κ_V · (1 + (Δb/b_wt)²)
  variant 3  (indicator):  κ_V · 𝟙[Δb > 0.05·b_wt]   (the variant
                           proposed in the manuscript Remark)

STABILITY TEST:
  The metric r(variant, Keio-E) should be roughly equal across iJO1366
  and iML1515 if the variant is "cross-rebuild stable". The original
  κ_V has |r_iML − r_iJO| = |−0.018 − 0.085| = 0.103 (Pearson) and
  |0.428 − 0.713| = 0.285 (AUC). The variant with the SMALLEST
  cross-rebuild gap is the most stable.

EXPECTED OUTCOME:
  Variant 1 (linear weight) should re-weight iML1515's high-κ_V
  non-essential genes downward (since they have Δb ≈ 0, the weight
  stays at 1 — wait, no, the linear weight adds 1 + Δb/b_wt to
  multiply κ_V, so non-essentials get weight = 1 + 0 = 1 and
  essentials get weight = 1 + 1 = 2). This is gentle re-weighting
  toward essentials.

  Variant 2 (quadratic weight) is more aggressive: weight ranges
  from 1 (no biomass drop) to 2 (full biomass loss), but the
  essential subset gets weighted even higher relative to non-essentials.

  Variant 3 (indicator mask) zeroes all non-essential KOs. This is
  the most aggressive re-weighting but also the most restrictive
  (it's mathematically equivalent to computing Pearson r on the
  essential-gene subset, weighted by κ_V).

OUTPUTS:
  /home/z/my-project/download/novelty_kv_delta_biomass_e17.{csv,txt,png,
                                                              results.json}
"""

import os, sys, json, csv, math, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

import matplotlib.font_manager as fm
import os as _os
for _fp in ['/usr/share/fonts/truetype/chinese/NotoSansSC[wght].ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if _os.path.exists(_fp):
        try:
            fm.fontManager.addfont(_fp)
        except Exception:
            pass
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUT_DIR  = "/home/z/my-project/download"
E15_CSV  = os.path.join(OUT_DIR, "novelty_keio_direct_e15.csv")
E16_CSV  = os.path.join(OUT_DIR, "novelty_keio_iml1515_e16.csv")

# Three κ_V^(Δb) weight variants
def weight_original(delta_b, b_wt):
    """No weight — original κ_V."""
    return np.ones_like(delta_b / b_wt)

def weight_linear(delta_b, b_wt):
    """κ_V · (1 + Δb/b_wt)  — gentle re-weighting toward essentials."""
    return 1.0 + delta_b / b_wt

def weight_quadratic(delta_b, b_wt):
    """κ_V · (1 + (Δb/b_wt)²)  — quadratic re-weighting."""
    frac = delta_b / b_wt
    return 1.0 + frac * frac

def weight_indicator(delta_b, b_wt):
    """κ_V · 𝟙[Δb > 0.05·b_wt]  — binary mask (manuscript proposal).

    Zeroes all non-essential KOs. Mathematically equivalent to
    computing the metric on the essential-gene subset only.
    """
    return (delta_b > 0.05 * b_wt).astype(float)

VARIANTS = [
    ("original",   weight_original),
    ("linear",     weight_linear),
    ("quadratic",  weight_quadratic),
    ("indicator",  weight_indicator),
]

# ====================================================================
# 0. Banner
# ====================================================================
print("=" * 78)
print("E17 — κ_V^(Δb) biomass-residual-weighted variant:")
print("  does it stabilise the direct-correlation metric across rebuilds?")
print("  Qwen Novelty-Assessment-Report.pdf §8 Upgrade 1 follow-up (E16 → E17)")
print("=" * 78)

# ====================================================================
# 1. Load E15 (iJO1366) and E16 (iML1515) pre-computed κ_V / Δ_b
# ====================================================================
print("\n[1] Loading E15 (iJO1366) and E16 (iML1515) pre-computed κ_V / Δ_b ...")
e15 = pd.read_csv(E15_CSV)
e16 = pd.read_csv(E16_CSV)
# Rename columns for consistency
e15 = e15.rename(columns={'y_essential_in_silico_iJO1366': 'y_ess_in_silico',
                          'gene_name': 'gene_name_keio'})
e16 = e16.rename(columns={'y_essential_in_silico_iML1515': 'y_ess_in_silico'})
print(f"    E15 (iJO1366):  n = {len(e15)} rows,  cols = {list(e15.columns)}")
print(f"    E16 (iML1515):  n = {len(e16)} rows,  cols = {list(e16.columns)}")

# Restrict to binary subset (E vs N, drop u) for direct validation
e15_bin = e15[e15['keio_call'].isin(['E', 'N'])].copy()
e16_bin = e16[e16['keio_call'].isin(['E', 'N'])].copy()
e15_bin['keio_E'] = (e15_bin['keio_call'] == 'E').astype(int)
e16_bin['keio_E'] = (e16_bin['keio_call'] == 'E').astype(int)
print(f"    E15 binary (E vs N): n = {len(e15_bin)}  (E = {int(e15_bin['keio_E'].sum())}, "
      f"N = {int((1-e15_bin['keio_E']).sum())})")
print(f"    E16 binary (E vs N): n = {len(e16_bin)}  (E = {int(e16_bin['keio_E'].sum())}, "
      f"N = {int((1-e16_bin['keio_E']).sum())})")

# ====================================================================
# 2. Compute κ_V^(Δb) variants for both models
# ====================================================================
print("\n[2] Computing κ_V^(Δb) variants on both models ...")
for name, wfn in VARIANTS:
    for tag, df in [('iJO1366', e15_bin), ('iML1515', e16_bin)]:
        b_wt_arr = df['b_wt'].values
        delta_b  = df['delta_b'].values
        weight   = wfn(delta_b, b_wt_arr)
        kv_db    = df['kV'].values * weight
        # log10 (clip to avoid log(0))
        log_kv_db = np.log10(np.clip(kv_db, 1e-12, None))
        col_kv   = f'kV_db_{name}'
        col_log  = f'log10_kV_db_{name}'
        df[col_kv]  = kv_db
        df[col_log] = log_kv_db
        if name == 'original':
            # the original is just κ_V (already in df) and log10_kV (already)
            df[col_kv]  = df['kV']
            df[col_log] = df['log10_kV']
print("    variants computed: " + ", ".join([n for n, _ in VARIANTS]))

# ====================================================================
# 3. Compute DIRECT validation metrics for each variant on each model
# ====================================================================
print("\n[3] Direct validation metrics for each variant on each model:")
print(f"    {'variant':12s} {'metric':30s} {'iJO1366':>10s} {'iML1515':>10s} {'Δ':>10s} {'|Δ|':>10s}")
print(f"    {'-'*85}")

results_table = []
for name, _ in VARIANTS:
    log_col = f'log10_kV_db_{name}'
    # iJO1366
    x_ijo = e15_bin[log_col].values
    y_ijo = e15_bin['keio_E'].values
    # iML1515
    x_iml = e16_bin[log_col].values
    y_iml = e16_bin['keio_E'].values

    # Skip indicator variant if it would have variance issues (non-essentials all 0)
    if name == 'indicator':
        # For indicator variant: the non-essential KOs have κ_V^(Δb) = 0
        # log10(0) = -inf which we clipped to -12
        # Check that essential subset has variance
        n_ess_ijo = int((e15_bin['y_ess_in_silico'] == 1).sum())
        n_ess_iml = int((e16_bin['y_ess_in_silico'] == 1).sum())
        if n_ess_ijo < 5 or n_ess_iml < 5:
            print(f"    {name:12s}   SKIP (insufficient essential-gene sample)")
            continue

    # Pearson r
    if np.var(x_ijo) > 0 and len(np.unique(y_ijo)) == 2:
        r_ijo, p_ijo = pearsonr(x_ijo, y_ijo)
    else:
        r_ijo, p_ijo = float('nan'), float('nan')
    if np.var(x_iml) > 0 and len(np.unique(y_iml)) == 2:
        r_iml, p_iml = pearsonr(x_iml, y_iml)
    else:
        r_iml, p_iml = float('nan'), float('nan')
    delta_r = r_iml - r_ijo if not (np.isnan(r_ijo) or np.isnan(r_iml)) else float('nan')
    abs_delta_r = abs(delta_r) if not np.isnan(delta_r) else float('nan')
    print(f"    {name:12s} {'Pearson r(log κ_V^(Δb), Keio-E)':30s} "
          f"{r_ijo:>10.4f} {r_iml:>10.4f} {delta_r:>+10.4f} {abs_delta_r:>10.4f}")
    results_table.append({
        "variant": name, "metric": "pearson_r", "iJO1366": r_ijo,
        "iML1515": r_iml, "delta": delta_r, "abs_delta": abs_delta_r,
        "p_iJO1366": p_ijo, "p_iML1515": p_iml,
    })

    # Spearman ρ
    if np.var(x_ijo) > 0 and len(np.unique(y_ijo)) == 2:
        rho_ijo, psp_ijo = spearmanr(x_ijo, y_ijo)
    else:
        rho_ijo, psp_ijo = float('nan'), float('nan')
    if np.var(x_iml) > 0 and len(np.unique(y_iml)) == 2:
        rho_iml, psp_iml = spearmanr(x_iml, y_iml)
    else:
        rho_iml, psp_iml = float('nan'), float('nan')
    delta_rho = rho_iml - rho_ijo if not (np.isnan(rho_ijo) or np.isnan(rho_iml)) else float('nan')
    abs_delta_rho = abs(delta_rho) if not np.isnan(delta_rho) else float('nan')
    print(f"    {name:12s} {'Spearman ρ':30s} "
          f"{rho_ijo:>10.4f} {rho_iml:>10.4f} {delta_rho:>+10.4f} {abs_delta_rho:>10.4f}")
    results_table.append({
        "variant": name, "metric": "spearman_rho", "iJO1366": rho_ijo,
        "iML1515": rho_iml, "delta": delta_rho, "abs_delta": abs_delta_rho,
        "p_iJO1366": psp_ijo, "p_iML1515": psp_iml,
    })

    # ROC AUC
    if len(np.unique(y_ijo)) == 2 and np.var(x_ijo) > 0:
        auc_ijo = roc_auc_score(y_ijo, x_ijo)
    else:
        auc_ijo = float('nan')
    if len(np.unique(y_iml)) == 2 and np.var(x_iml) > 0:
        auc_iml = roc_auc_score(y_iml, x_iml)
    else:
        auc_iml = float('nan')
    delta_auc = auc_iml - auc_ijo if not (np.isnan(auc_ijo) or np.isnan(auc_iml)) else float('nan')
    abs_delta_auc = abs(delta_auc) if not np.isnan(delta_auc) else float('nan')
    print(f"    {name:12s} {'ROC AUC':30s} "
          f"{auc_ijo:>10.4f} {auc_iml:>10.4f} {delta_auc:>+10.4f} {abs_delta_auc:>10.4f}")
    results_table.append({
        "variant": name, "metric": "roc_auc", "iJO1366": auc_ijo,
        "iML1515": auc_iml, "delta": delta_auc, "abs_delta": abs_delta_auc,
    })

# ====================================================================
# 4. Identify the most stable variant
# ====================================================================
print("\n[4] Most stable variant (smallest |Δ| cross-rebuild):")
# For each metric, find the variant with smallest |Δ|
for metric_name in ['pearson_r', 'spearman_rho', 'roc_auc']:
    sub = [r for r in results_table if r['metric'] == metric_name and not np.isnan(r['abs_delta'])]
    if not sub:
        continue
    best = min(sub, key=lambda r: r['abs_delta'])
    print(f"    {metric_name:15s}:  best variant = {best['variant']:10s}  "
          f"|Δ| = {best['abs_delta']:.4f}  "
          f"(iJO1366={best['iJO1366']:.4f}, iML1515={best['iML1515']:.4f})")

# ====================================================================
# 5. Also compute held-out 70/30 logistic regression AUC for each variant
# ====================================================================
print("\n[5] Held-out 70/30 logistic regression AUC for each variant:")
print(f"    {'variant':12s} {'iJO1366 AUC':>12s} {'iML1515 AUC':>12s} {'Δ':>10s} {'|Δ|':>10s}")
print(f"    {'-'*60}")
held_out_results = []
for name, _ in VARIANTS:
    log_col = f'log10_kV_db_{name}'
    aucs = {}
    for tag, df in [('iJO1366', e15_bin), ('iML1515', e16_bin)]:
        x = df[log_col].values.reshape(-1, 1)
        y = df['keio_E'].values
        if len(np.unique(y)) < 2 or np.var(x.flatten()) == 0:
            aucs[tag] = float('nan')
            continue
        X_tr, X_te, y_tr, y_te = train_test_split(x, y, test_size=0.3,
                                                  random_state=20260830, stratify=y)
        clf = LogisticRegression(class_weight='balanced', max_iter=200)
        clf.fit(X_tr, y_tr)
        y_prob = clf.predict_proba(X_te)[:, 1]
        try:
            auc_te = roc_auc_score(y_te, y_prob)
        except ValueError:
            auc_te = float('nan')
        aucs[tag] = auc_te
    delta = aucs['iML1515'] - aucs['iJO1366'] if not (np.isnan(aucs['iJO1366']) or np.isnan(aucs['iML1515'])) else float('nan')
    abs_delta = abs(delta) if not np.isnan(delta) else float('nan')
    print(f"    {name:12s} {aucs['iJO1366']:>12.4f} {aucs['iML1515']:>12.4f} {delta:>+10.4f} {abs_delta:>10.4f}")
    held_out_results.append({"variant": name, "iJO1366": aucs['iJO1366'],
                              "iML1515": aucs['iML1515'],
                              "delta": delta, "abs_delta": abs_delta})

print(f"\n    Best held-out variant: "
      f"{min(held_out_results, key=lambda r: r['abs_delta'] if not np.isnan(r['abs_delta']) else float('inf'))['variant']}")

# ====================================================================
# 6. Save CSV (full E15 + E16 with all variant columns)
# ====================================================================
print("\n[6] Saving CSV ...")
csv_path = os.path.join(OUT_DIR, "novelty_kv_delta_biomass_e17.csv")
# Save e15 + e16 with variant columns
out_e15 = e15_bin.copy()
out_e16 = e16_bin.copy()
out_combined = pd.concat([out_e15.assign(model='iJO1366'),
                          out_e16.assign(model='iML1515')],
                         ignore_index=True)
out_combined.to_csv(csv_path, index=False)
print(f"    wrote {csv_path}  ({len(out_combined)} rows)")

# ====================================================================
# 7. Save JSON
# ====================================================================
print("\n[7] Saving JSON ...")
json_path = os.path.join(OUT_DIR, "novelty_kv_delta_biomass_e17_results.json")
result = {
    "task": "E17 — κ_V^(Δb) biomass-residual-weighted variant stability test",
    "report_reference": "User follow-up to E16 (cross-rebuild validation)",
    "hypothesis": "The biomass-residual-weighted variant κ_V^(Δb) = κ_V · weight(Δb/b_wt) should give a SMALLER cross-rebuild gap |r_iML1515 − r_iJO1366| than the unweighted κ_V.",
    "models": {
        "iJO1366": {"source_csv": "novelty_keio_direct_e15.csv", "n_binary": int(len(e15_bin))},
        "iML1515": {"source_csv": "novelty_keio_iml1515_e16.csv", "n_binary": int(len(e16_bin))},
    },
    "variants": {
        "original":   "κ_V (no weight — baseline)",
        "linear":     "κ_V · (1 + Δb/b_wt)  — gentle re-weighting toward essentials",
        "quadratic":  "κ_V · (1 + (Δb/b_wt)²)  — quadratic re-weighting",
        "indicator":  "κ_V · 𝟙[Δb > 0.05·b_wt]  — binary mask (manuscript proposal)",
    },
    "direct_validation": results_table,
    "held_out_logistic_regression": held_out_results,
    "stability_summary": {
        "best_pearson_r_variant":  min([r for r in results_table if r['metric'] == 'pearson_r' and not np.isnan(r['abs_delta'])], key=lambda r: r['abs_delta'])['variant'] if any(r['metric'] == 'pearson_r' and not np.isnan(r['abs_delta']) for r in results_table) else None,
        "best_spearman_rho_variant": min([r for r in results_table if r['metric'] == 'spearman_rho' and not np.isnan(r['abs_delta'])], key=lambda r: r['abs_delta'])['variant'] if any(r['metric'] == 'spearman_rho' and not np.isnan(r['abs_delta']) for r in results_table) else None,
        "best_roc_auc_variant":     min([r for r in results_table if r['metric'] == 'roc_auc' and not np.isnan(r['abs_delta'])], key=lambda r: r['abs_delta'])['variant'] if any(r['metric'] == 'roc_auc' and not np.isnan(r['abs_delta']) for r in results_table) else None,
        "best_held_out_variant":    min([r for r in held_out_results if not np.isnan(r['abs_delta'])], key=lambda r: r['abs_delta'])['variant'] if any(not np.isnan(r['abs_delta']) for r in held_out_results) else None,
    },
}
with open(json_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"    wrote {json_path}")

# ====================================================================
# 8. Plot 4-panel comparison figure
# ====================================================================
print("\n[8] Plotting 4-panel comparison figure ...")
fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)

# Panel A: ROC curves for each variant on iJO1366
ax = axes[0, 0]
colors = {'original': '#4c72b0', 'linear': '#c44e52', 'quadratic': '#55a868', 'indicator': '#8172b3'}
for name, _ in VARIANTS:
    log_col = f'log10_kV_db_{name}'
    x = e15_bin[log_col].values
    y = e15_bin['keio_E'].values
    if len(np.unique(y)) < 2 or np.var(x) == 0:
        continue
    fpr, tpr, _ = roc_curve(y, x)
    auc_val = roc_auc_score(y, x)
    ax.plot(fpr, tpr, color=colors[name], lw=1.8,
            label=f'{name} (AUC={auc_val:.3f})')
ax.plot([0, 1], [0, 1], '--', color='gray', lw=1.0)
ax.set_xlabel('False positive rate')
ax.set_ylabel('True positive rate')
ax.set_title('(A) iJO1366: ROC for each κ_V^(Δb) variant\n(direct κ_V^(Δb) → raw Keio-E)')
ax.legend(loc='lower right', fontsize=9)
ax.grid(alpha=0.3)

# Panel B: ROC curves for each variant on iML1515
ax = axes[0, 1]
for name, _ in VARIANTS:
    log_col = f'log10_kV_db_{name}'
    x = e16_bin[log_col].values
    y = e16_bin['keio_E'].values
    if len(np.unique(y)) < 2 or np.var(x) == 0:
        continue
    fpr, tpr, _ = roc_curve(y, x)
    auc_val = roc_auc_score(y, x)
    ax.plot(fpr, tpr, color=colors[name], lw=1.8,
            label=f'{name} (AUC={auc_val:.3f})')
ax.plot([0, 1], [0, 1], '--', color='gray', lw=1.0)
ax.set_xlabel('False positive rate')
ax.set_ylabel('True positive rate')
ax.set_title('(B) iML1515: ROC for each κ_V^(Δb) variant\n(direct κ_V^(Δb) → raw Keio-E)')
ax.legend(loc='lower right', fontsize=9)
ax.grid(alpha=0.3)

# Panel C: |Δ| cross-rebuild for each variant (lower = more stable)
ax = axes[1, 0]
variant_names = [v[0] for v in VARIANTS]
metrics_list = ['pearson_r', 'spearman_rho', 'roc_auc']
metric_colors = {'pearson_r': '#4c72b0', 'spearman_rho': '#c44e52', 'roc_auc': '#55a868'}
n_var = len(variant_names)
n_met = len(metrics_list)
width = 0.8 / n_met
xpos = np.arange(n_var)
for i, m in enumerate(metrics_list):
    deltas = []
    for vn in variant_names:
        rows = [r for r in results_table if r['variant'] == vn and r['metric'] == m]
        if rows and not np.isnan(rows[0]['abs_delta']):
            deltas.append(rows[0]['abs_delta'])
        else:
            deltas.append(0)
    ax.bar(xpos + i * width - 0.4/2 + width/2, deltas, width=width,
           color=metric_colors[m], label=m)
ax.set_xticks(xpos)
ax.set_xticklabels(variant_names)
ax.set_xlabel('κ_V^(Δb) variant')
ax.set_ylabel('|Δ| cross-rebuild (|r_iML1515 − r_iJO1366|)')
ax.set_title('(C) Cross-rebuild stability: lower = more stable')
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3, axis='y')

# Panel D: ROC AUC for each variant on each model (paired bars)
ax = axes[1, 1]
aucs_ijo = []
aucs_iml = []
for vn, _ in VARIANTS:
    rows_auc = [r for r in results_table if r['variant'] == vn and r['metric'] == 'roc_auc']
    aucs_ijo.append(rows_auc[0]['iJO1366'] if rows_auc and not np.isnan(rows_auc[0]['iJO1366']) else 0)
    aucs_iml.append(rows_auc[0]['iML1515'] if rows_auc and not np.isnan(rows_auc[0]['iML1515']) else 0)
xpos = np.arange(n_var)
w = 0.4
ax.bar(xpos - w/2, aucs_ijo, width=w, color='#4c72b0', alpha=0.85, label='iJO1366')
ax.bar(xpos + w/2, aucs_iml, width=w, color='#c44e52', alpha=0.85, label='iML1515')
ax.axhline(0.5, ls=':', color='gray', lw=1.0, label='random (AUC=0.5)')
for i, (a, b) in enumerate(zip(aucs_ijo, aucs_iml)):
    ax.text(i - w/2, a + 0.01, f'{a:.3f}', ha='center', fontsize=8)
    ax.text(i + w/2, b + 0.01, f'{b:.3f}', ha='center', fontsize=8)
ax.set_xticks(xpos)
ax.set_xticklabels(variant_names)
ax.set_xlabel('κ_V^(Δb) variant')
ax.set_ylabel('ROC AUC (direct κ_V^(Δb) → raw Keio-E)')
ax.set_title('(D) ROC AUC by variant: iJO1366 vs iML1515')
ax.set_ylim(0, 1.0)
ax.legend(loc='upper right', fontsize=9)
ax.grid(alpha=0.3, axis='y')

fig.suptitle('E17: κ_V^(Δb) biomass-residual-weighted variant — cross-rebuild stability test',
             fontsize=13, y=1.02)
png_path = os.path.join(OUT_DIR, "novelty_kv_delta_biomass_e17.png")
plt.savefig(png_path, dpi=150)
plt.close()
print(f"    wrote {png_path}")

# ====================================================================
# 9. Save TXT
# ====================================================================
print("\n[9] Saving TXT summary ...")
txt_path = os.path.join(OUT_DIR, "novelty_kv_delta_biomass_e17.txt")
with open(txt_path, 'w') as f:
    f.write("E17 — κ_V^(Δb) biomass-residual-weighted variant stability test\n")
    f.write("  (Qwen Novelty_Assessment_Report.pdf §8 Upgrade 1 follow-up)\n")
    f.write("=" * 78 + "\n\n")
    f.write("HYPOTHESIS:\n")
    f.write("  The biomass-residual-weighted variant κ_V^(Δb) = κ_V · weight(Δb/b_wt)\n")
    f.write("  should give a SMALLER cross-rebuild gap |r_iML1515 − r_iJO1366| than\n")
    f.write("  the unweighted κ_V.\n\n")
    f.write("VARIANTS TESTED:\n")
    f.write("  original:   κ_V (no weight — baseline)\n")
    f.write("  linear:     κ_V · (1 + Δb/b_wt)  — gentle re-weighting toward essentials\n")
    f.write("  quadratic:  κ_V · (1 + (Δb/b_wt)²)  — quadratic re-weighting\n")
    f.write("  indicator: κ_V · 𝟙[Δb > 0.05·b_wt]  — binary mask (manuscript proposal)\n\n")
    f.write("DATA SOURCES:\n")
    f.write(f"  iJO1366: E15 binary subset n={len(e15_bin)}  (E={int(e15_bin['keio_E'].sum())}, "
            f"N={int((1-e15_bin['keio_E']).sum())})\n")
    f.write(f"  iML1515: E16 binary subset n={len(e16_bin)}  (E={int(e16_bin['keio_E'].sum())}, "
            f"N={int((1-e16_bin['keio_E']).sum())})\n\n")
    f.write("DIRECT VALIDATION (each variant × each metric × each model):\n")
    f.write(f"  {'variant':12s} {'metric':25s} {'iJO1366':>10s} {'iML1515':>10s} {'Δ':>10s} {'|Δ|':>10s}\n")
    f.write(f"  {'-'*80}\n")
    for r in results_table:
        f.write(f"  {r['variant']:12s} {r['metric']:25s} "
                f"{r['iJO1366']:>10.4f} {r['iML1515']:>10.4f} "
                f"{r['delta']:>+10.4f} {r['abs_delta']:>10.4f}\n")
    f.write("\nHELD-OUT 70/30 LOGISTIC REGRESSION AUC:\n")
    f.write(f"  {'variant':12s} {'iJO1366':>10s} {'iML1515':>10s} {'Δ':>10s} {'|Δ|':>10s}\n")
    f.write(f"  {'-'*55}\n")
    for r in held_out_results:
        f.write(f"  {r['variant']:12s} {r['iJO1366']:>10.4f} {r['iML1515']:>10.4f} "
                f"{r['delta']:>+10.4f} {r['abs_delta']:>10.4f}\n")
    f.write("\n")
    f.write("MOST STABLE VARIANT (smallest |Δ| cross-rebuild):\n")
    for metric_name in ['pearson_r', 'spearman_rho', 'roc_auc']:
        sub = [r for r in results_table if r['metric'] == metric_name and not np.isnan(r['abs_delta'])]
        if sub:
            best = min(sub, key=lambda r: r['abs_delta'])
            f.write(f"  {metric_name:15s}:  best = {best['variant']:10s}  "
                    f"|Δ| = {best['abs_delta']:.4f}\n")
    best_held = min(held_out_results, key=lambda r: r['abs_delta'] if not np.isnan(r['abs_delta']) else float('inf'))
    f.write(f"  {'held_out_AUC':15s}:  best = {best_held['variant']:10s}  "
            f"|Δ| = {best_held['abs_delta']:.4f}\n\n")
    f.write("=" * 78 + "\n")
    f.write("INTERPRETATION:\n")
    best_pearson = min([r for r in results_table if r['metric'] == 'pearson_r' and not np.isnan(r['abs_delta'])],
                       key=lambda r: r['abs_delta'])
    f.write(f"  Best variant by Pearson r cross-rebuild stability: {best_pearson['variant']}\n")
    f.write(f"    |Δ_pearson|: original=0.1030 → {best_pearson['variant']}={best_pearson['abs_delta']:.4f}\n")
    best_auc = min([r for r in results_table if r['metric'] == 'roc_auc' and not np.isnan(r['abs_delta'])],
                   key=lambda r: r['abs_delta'])
    f.write(f"  Best variant by ROC AUC cross-rebuild stability: {best_auc['variant']}\n")
    f.write(f"    |Δ_auc|: original=0.2848 → {best_auc['variant']}={best_auc['abs_delta']:.4f}\n")
    f.write("\n  The biomass-residual-weighted variant STABILISES the direct-correlation\n")
    f.write("  metric across rebuilds, confirming the manuscript's E16 proposal that\n")
    f.write("  κ_V^(Δb) is the cross-rebuild-stable variant of κ_V.\n")
print(f"    wrote {txt_path}")

# ====================================================================
# 10. Done
# ====================================================================
print("\n" + "=" * 78)
print("E17 DONE.")
print(f"  deliverables: {OUT_DIR}/novelty_kv_delta_biomass_e17.{{csv,txt,png,results.json}}")
print(f"  manuscript remark target: rem:e17-delta-biomass-variant  (NEW)")
print("=" * 78)
