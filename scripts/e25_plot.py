#!/usr/bin/env python3
"""E25 figure: 2x2 platform x class matrix + per-condition correlation bars."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for f in ["/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
    try:
        fm.fontManager.addfont(f)
    except Exception:
        pass
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

R = json.load(open(
    "/home/z/my-project/download/novelty_v18_e25_platform_class_results.json"))
arms = R["arms"]
cm = R["matrix_2x2_common_set"]

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(11.5, 4.6), constrained_layout=True,
    gridspec_kw={"width_ratios": [1.0, 1.35]})

# ---- panel A: the 2x2 matrix (common gene set, n=240) --------------------
M = np.array([[cm["microarray_depletion"]["pearson_r"],
               cm["microarray_switch"]["pearson_r"]],
              [cm["rnaseq_depletion"]["pearson_r"],
               cm["rnaseq_switch_precise"]["pearson_r"]]])
im = ax1.imshow(M, cmap="RdYlBu_r", vmin=-0.5, vmax=0.5, aspect="auto")
ax1.set_xticks([0, 1], ["carbon\ndepletion", "carbon\nswitch"])
ax1.set_yticks([0, 1], ["microarray\n(M3D)", "RNA-seq\n(GSE64021/PRECISE)"])
labels = {
    (0, 0): ("E24 primary", cm["microarray_depletion"]),
    (0, 1): ("E25 S1", cm["microarray_switch"]),
    (1, 0): ("E25 S2", cm["rnaseq_depletion"]),
    (1, 1): ("E24 A-replicate", cm["rnaseq_switch_precise"]),
}
for (i, j), (tag, res) in labels.items():
    ax1.text(j, i - 0.13, f"r = {res['pearson_r']:+.3f}", ha="center",
             va="center", fontsize=11, fontweight="bold", color="black")
    ax1.text(j, i + 0.16, f"p = {res['pearson_p']:.1e}\n({tag})",
             ha="center", va="center", fontsize=7.5, color="black")
ax1.set_title(f"A  platform × class matrix, |log2FC| metric\n"
              f"common gene set n = {cm['n_common']}", fontsize=10)
cb = fig.colorbar(im, ax=ax1, shrink=0.85, pad=0.02)
cb.set_label("Pearson r (log$_{10}\\kappa_V$ vs max|log2FC|)", fontsize=8)

# ---- panel B: every condition, per-condition |FC| r ----------------------
conds = [
    ("M3D carbon exhaustion\nt=480 min (E24)", 0.40, "#1f77b4"),
    ("M3D switch glycerol", arms["array-switch-glycerol"]["pearson_r"],
     "#7fb3d5"),
    ("M3D switch acetate", arms["array-switch-acetate"]["pearson_r"],
     "#7fb3d5"),
    ("M3D switch proline", arms["array-switch-proline"]["pearson_r"],
     "#7fb3d5"),
    ("M3D heat 50C 10min", arms["array-stress-heatShock"]["pearson_r"],
     "#d62728"),
    ("M3D acid pH2 10min", arms["array-stress-acidShock"]["pearson_r"],
     "#d62728"),
    ("M3D cipro 10min", arms["array-stress-cipro"]["pearson_r"], "#d62728"),
    ("GSE carbon-starve 1h", arms["seq-carbonstarve-1h"]["pearson_r"],
     "#2ca02c"),
    ("GSE carbon-starve 2h", arms["seq-carbonstarve-2h"]["pearson_r"],
     "#2ca02c"),
    ("GSE carbon-starve 4h", arms["seq-carbonstarve-4h"]["pearson_r"],
     "#2ca02c"),
    ("GSE carbon-starve 6h", arms["seq-carbonstarve-6h"]["pearson_r"],
     "#2ca02c"),
    ("GSE phosphorus max", arms["seq-phosphorus-MAX"]["pearson_r"],
     "#ff9896"),
    ("GSE heat shock 4h", arms["seq-heatshock-4h"]["pearson_r"], "#9467bd"),
    ("PRECISE carbon switch\n(E24, n=433)", -0.054, "#8c564b"),
]
names = [c[0] for c in conds]
vals = [c[1] for c in conds]
cols = [c[2] for c in conds]
y = np.arange(len(conds))
ax2.barh(y, vals, color=cols, edgecolor="black", linewidth=0.4)
ax2.set_yticks(y, names, fontsize=7.5)
ax2.axvline(0, color="black", lw=0.8)
for yy, v, c in zip(y, vals, conds):
    p = c[1]
    ax2.text(v + (0.012 if v >= 0 else -0.012), yy, f"{v:+.2f}",
             va="center", ha="left" if v >= 0 else "right", fontsize=7)
ax2.set_xlabel("Pearson r  (log$_{10}\\kappa_V$ vs per-condition |log2FC|)",
               fontsize=8.5)
ax2.set_xlim(-0.12, 0.50)
ax2.set_title("B  per-condition associations by platform and class",
              fontsize=10)
ax2.invert_yaxis()
ax2.grid(axis="x", alpha=0.25, lw=0.4)

out = "/home/z/my-project/download/novelty_v18_e25_platform_class.png"
fig.savefig(out, dpi=200)
print("saved", out)
