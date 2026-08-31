#!/usr/bin/env python3
"""Figure for Study E27 (v20): Schmidt-2016 protein-layer replication.

Panels:
  (a) per-condition r(log10 kappa_V, |log2FC|) profile across all 22
      Schmidt conditions, colored by perturbation class, with the
      independent-batch (Glucose.2) technical baseline marked;
  (b) the apples-to-apples three-way contrast on the Schmidt-covered
      panel: E24 transcript, E25 transcript, E26 protein (spectral
      counts), E27 protein (quantitative triplicates);
  (c) mean response magnitude by kappa tertile: transcript (E24) graded
      vs protein (Schmidt) flat;
  (d) the primary scatter: kappa vs protein max|log2FC| (null) with the
      transcript association annotated for contrast.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DL = Path("/home/z/my-project/download")
res = json.load(open(DL / "novelty_v20_e27_schmidt_replication_results.json"))
csv = pd.read_csv(DL / "novelty_v20_e27_schmidt_replication.csv",
                  index_col=0)

CLS_COLOR = {"exhaustion": "#c0392b", "limitation": "#e67e22",
             "switch": "#16a085", "stress_glucose": "#8e44ad",
             "null": "#7f8c8d", "out": "#bdc3c7"}
NICE = {"Statday": "stationary 1 day", "Stat.3days": "stationary 3 days",
        "Chemstat.0.5": "chemostat mu=0.5", "Chemstat.0.35": "chemostat mu=0.35",
        "Chemstat.0.2": "chemostat mu=0.20", "Chemstat.02": "chemostat mu=0.12",
        "Glycerin.AA": "glycerol+AA", "Glucoseamine": "glucosamine",
        "Glucose.2": "glucose (batch 2)", "42.C": "42C", "OSM": "NaCl 50mM",
        "pH6": "pH 6"}

fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.5),
                         constrained_layout=True)

# ------------------------------------------------ (a) per-condition profile
ax = axes[0, 0]
rows = []
for key, r in res["per_condition"].items():
    cls, cond = key.split(":", 1)
    rows.append((NICE.get(cond, cond), cls, r["pearson_r"],
                 r["pearson_p"], r["boot_ci95"]))
rows.sort(key=lambda t: (["exhaustion", "limitation", "stress_glucose",
                          "switch", "out", "null"].index(t[1]), t[2]))
y = np.arange(len(rows))
for i, (name, cls, r, p, ci) in enumerate(rows):
    ax.barh(i, r, color=CLS_COLOR[cls], alpha=0.85,
            edgecolor="black", linewidth=0.4)
    ax.plot([ci[0], ci[1]], [i, i], color="black", lw=0.8)
    if p < 0.05:
        ax.text(r + (0.012 if r >= 0 else -0.012), i, "*",
                ha="left" if r >= 0 else "right", va="center", fontsize=9)
ax.set_yticks(y)
ax.set_yticklabels([t[0] for t in rows], fontsize=8.5)
ax.axvline(0, color="black", lw=0.8)
base = res["internal_null"]["glucose2_r_on_panel"]["pearson_r"]
ax.axvline(base, color="#7f8c8d", ls=":", lw=1.4)
ax.text(base - 0.01, len(rows) - 0.4, "batch-2\nbaseline", fontsize=7.5,
        ha="right", color="#7f8c8d")
ax.set_xlabel(r"$r(\log_{10}\kappa_V,\ |\log_2\Delta P|)$", fontsize=10)
ax.set_title("(a) Schmidt 2016 protein layer, per condition", fontsize=11)
ax.set_xlim(-0.28, 0.28)
handles = [plt.Rectangle((0, 0), 1, 1, color=CLS_COLOR[c])
           for c in ("exhaustion", "limitation", "switch", "stress_glucose",
                     "null", "out")]
ax.legend(handles, ["carbon exhaustion", "carbon limitation (chemostat)",
                    "carbon switch", "stress on glucose", "batch null",
                    "LB (out)"], fontsize=7.5, loc="lower right",
          framealpha=0.9)

# ------------------------------------------- (b) three-way contrast, same x
ax = axes[0, 1]
arms = res["arms"]
items = [("E24 transcript\n(M3D exhaustion)", arms["e24-transfc-on-schmidt-subset"], "#2c3e50"),
         ("E25 transcript\n(GSE starvation)", arms["e25-transfc-on-schmidt-subset"], "#2c3e50"),
         ("E26 protein\n(GSE spectral counts)", arms["e26-gse-protfc-on-schmidt-subset"], "#c0392b"),
         ("E27 protein\n(Schmidt triplicate)", arms["schmidt-protfc-exhaustion"], "#c0392b")]
x = np.arange(len(items))
for i, (lab, r, col) in enumerate(items):
    ax.bar(i, r["pearson_r"], 0.62, color=col, alpha=0.45 if "trans" in lab.lower() or "E24" in lab or "E25" in lab else 0.9,
           edgecolor=col, linewidth=1.2)
    ax.errorbar(i, r["pearson_r"],
                yerr=[[max(0, r["pearson_r"] - r["boot_ci95"][0])],
                      [max(0, r["boot_ci95"][1] - r["pearson_r"])]],
                fmt="none", ecolor="black", capsize=4, lw=1)
    ax.text(i, r["pearson_r"] + (0.03 if r["pearson_r"] >= 0 else -0.05),
            f"r={r['pearson_r']:+.3f}\np={r['pearson_p']:.1e}\nn={r['n']}",
            ha="center", fontsize=8.5)
ax.axhline(0, color="black", lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels([t[0] for t in items], fontsize=8.5)
ax.set_ylabel("Pearson $r$ with $\\log_{10}\\kappa_V$", fontsize=10)
ax.set_title("(b) same Schmidt-covered genes: transcript vs. protein", fontsize=11)
ax.set_ylim(-0.25, 0.62)

# -------------------------------------------- (c) tertile magnitude profile
ax = axes[1, 1]
tk = res["tp_coupling_by_kappa"]
strata = ("low-kappa", "mid-kappa", "high-kappa")
dT = [tk[f"{s}_ratio"]["mean_dT"] for s in strata]
dP = [tk[f"{s}_ratio"]["mean_dP"] for s in strata]
x = np.arange(3)
ax.bar(x - 0.19, dT, 0.34, color="#2c3e50", alpha=0.75,
       label="transcript $|\\Delta T|$ (E24, $\\log_2$)")
ax.bar(x + 0.19, dP, 0.34, color="#c0392b", alpha=0.85,
       label="protein $|\\Delta P|$ (Schmidt, $\\log_2$)")
for i, s in enumerate(strata):
    c = tk[s]
    ax.text(x[i], max(dT[i], dP[i]) + 0.07,
            f"r(dT,dP)={c['pearson_r']:+.2f}\np={c['pearson_p']:.1e}",
            ha="center", fontsize=8)
    ax.text(x[i] - 0.19, dT[i] + 0.015, f"{dT[i]:.2f}", ha="center", fontsize=8)
    ax.text(x[i] + 0.19, dP[i] + 0.015, f"{dP[i]:.2f}", ha="center", fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels(["low tertile", "mid tertile", "high tertile"], fontsize=9.5)
ax.set_ylabel("mean max $|\\log_2$ fold-change$", fontsize=10)
ax.set_ylim(0, 2.5)
ax.legend(fontsize=8.5, loc="upper left")
ax.set_title("(c) graded transcript, $\\kappa$-flat protein", fontsize=11)

# ------------------------------------------------------- (d) primary scatter
ax = axes[1, 0]
sub = csv.dropna(subset=["kappa_V_max", "schmidt_prot_exh_maxfc"])
kv = np.log10(sub["kappa_V_max"])
pv = sub["schmidt_prot_exh_maxfc"]
ok = np.isfinite(kv) & np.isfinite(pv)
kv, pv = kv[ok], pv[ok]
ax.scatter(kv, pv, s=14, alpha=0.45, color="#c0392b", edgecolor="none")
b1, b0 = np.polyfit(kv, pv, 1)
xs = np.linspace(kv.min(), kv.max(), 50)
ax.plot(xs, b0 + b1 * xs, color="black", lw=1.5)
prim = arms["schmidt-protfc-exhaustion"]
stab = arms["stability-top-tertile"]
top_cut = float(np.quantile(kv, 2 / 3))
ax.axvline(top_cut, color="#7f8c8d", ls=":", lw=1)
ax.text(top_cut + 0.02, 7.5, "top $\\kappa_V$ tertile", fontsize=8,
        color="#7f8c8d")
ax.text(0.03, 0.95,
        f"all genes: $r={prim['pearson_r']:+.3f}$ ($p={prim['pearson_p']:.2f}$, n={prim['n']})\n"
        f"top tertile: $r={stab['pearson_r']:+.3f}$ ($p={stab['pearson_p']:.2f}$) [E26 spectral: $-0.427$]\n"
        f"same genes, transcript: $r=+{arms['e24-transfc-on-schmidt-subset']['pearson_r']:.3f}$",
        transform=ax.transAxes, va="top", fontsize=8.5,
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="#cccccc"))
ax.set_xlabel("$\\log_{10}\\kappa_V$", fontsize=10)
ax.set_ylabel("protein max $|\\log_2\\Delta P|$ (stationary)", fontsize=10)
ax.set_title("(d) primary protein test: null replicated", fontsize=11)

fig.suptitle("E27: protein-layer replication with the Schmidt et al. 2016 "
             "condition-dependent proteome (22 conditions, BW25113, "
             "triplicates; 366/435 panel genes)", fontsize=12)
out = DL / "novelty_v20_e27_schmidt_replication.png"
fig.savefig(out, dpi=180)
print(f"[figure] {out}")
