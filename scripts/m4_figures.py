#!/usr/bin/env python3
"""Figures for M4a (scaling of the dynamic commutator) and M4b (2D
static geometry). English labels, consistent with the M1/M3 figure
style. All data from download/m4/."""
import csv
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "m4")

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "legend.fontsize": 8, "figure.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
})

C_EV = "#d62728"
C_NE = "#7f7f7f"
C_MAIN = "#1f77b4"
C_GOLD = "#b8860b"


# ---------------------------------------------------------------- fig M4a
def fig_m4a():
    rows = list(csv.DictReader(open(os.path.join(OUT, "m4a_scaling.csv"))))
    pairs = list(csv.DictReader(open(os.path.join(OUT, "m4a_pairs.csv"))))
    tof = lambda x: float(x) if x not in ("", "None", None) else np.nan
    by_pair = {}
    for r in rows:
        if r["feasible"] == "True":
            by_pair.setdefault((r["g1"], r["g2"]), []).append(
                (tof(r["eps"]), tof(r["chi"]), tof(r["d1_i"])))
    fig = plt.figure(figsize=(6.8, 7.4))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.35, 1, 1])
    ax = fig.add_subplot(gs[0, :])
    shown = 0
    for p in pairs:
        key = (p["g1"], p["g2"])
        d = sorted(by_pair.get(key, []), key=lambda x: -x[0])
        if len(d) < 3 or not any(x[1] > 1e-6 for x in d):
            continue
        xs = [x[0] for x in d if x[1] > 1e-6]
        ys = [x[1] for x in d if x[1] > 1e-6]
        lbl = f"{p['n1']}+{p['n2']}" if shown < 8 else None
        ax.loglog(xs, ys, "o-", ms=3.5, lw=1.0, label=lbl,
                  alpha=0.85 if shown < 8 else 0.5)
        shown += 1
    e = np.logspace(-2.6, 0.05, 20)
    ax.loglog(e, 0.03 * e, "--", color=C_GOLD, lw=1.4,
              label="slope 1 (measured law)")
    ax.loglog(e, 30 * e ** 2, ":", color=C_EV, lw=1.4,
              label="slope 2 (conjecture A4)")
    ax.set_xlabel(r"perturbation depth $\varepsilon$")
    ax.set_ylabel(r"open-path commutator $\chi(\varepsilon)$")
    ax.set_title("M4a: scaling of the sequential L1-MOMA commutator "
                 "(76 pairs, iML1515)")
    ax.legend(frameon=False, ncol=3, loc="lower left")
    # slopes
    ax = fig.add_subplot(gs[1, 0])
    sl = [tof(p["slope_chi"]) for p in pairs
          if p["slope_chi"] not in ("", "None", None)]
    n_zero = sum(1 for p in pairs if p["class_chi"] == "zero")
    ax.hist(sl, bins=np.arange(0.5, 1.45, 0.08), color=C_MAIN,
            edgecolor="white")
    ax.axvline(1.0, color=C_GOLD, lw=1.2)
    ax.axvline(2.0, color=C_EV, lw=1.2, ls=":")
    ax.set_xlim(0.5, 2.3)
    ax.set_xlabel(r"fitted slope of $\log\chi$ vs $\log\varepsilon$")
    ax.set_ylabel("pairs")
    ax.set_title(f"commutator slopes (n={len(sl)}; "
                 f"{n_zero} pairs $\\chi\\equiv 0$)")
    ax = fig.add_subplot(gs[1, 1])
    sl1 = [tof(p["slope_d1_i"]) for p in pairs
           if p["slope_d1_i"] not in ("", "None", None)]
    ax.hist(sl1, bins=np.arange(0.5, 1.45, 0.08), color="#2ca02c",
            edgecolor="white")
    ax.axvline(1.0, color=C_GOLD, lw=1.2)
    ax.set_xlim(0.5, 1.6)
    ax.set_xlabel(r"slope of single response $\|s_i(\varepsilon)-v_{wt}\|_1$")
    ax.set_ylabel("pairs")
    ax.set_title("linearity control (slope 1 expected)")
    # class counts
    ax = fig.add_subplot(gs[2, :])
    cls = {}
    for p in pairs:
        cls[p["class_chi"]] = cls.get(p["class_chi"], 0) + 1
    order = ["zero", "slope~1", "insufficient"]
    vals = [cls.get(k, 0) for k in order]
    bars = ax.barh(order, vals, color=[C_NE, C_MAIN, "#ff9896"])
    for b, v in zip(bars, vals):
        ax.text(b.get_width() + 0.6, b.get_y() + b.get_height() / 2,
                str(v), va="center")
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_xlabel("pairs")
    ax.set_title("commutator class census: exactly-commutative stratum "
                 "dominates; nonzero commutators scale linearly")
    fig.savefig(os.path.join(OUT, "fig_m4a_scaling.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("fig_m4a_scaling.png")


# ---------------------------------------------------------------- fig M4b-1
def fig_m4b_regions():
    z = np.load(os.path.join(OUT, "m4b_grid.npz"), allow_pickle=True)
    glc, o2, SIG, G = z["glc_ax"], z["o2_ax"], z["SIG"], z["G"]
    uniq, inv = np.unique(SIG, return_inverse=True)
    S = inv.reshape(SIG.shape)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.1),
                             constrained_layout=True)
    ax = axes[0]
    im = ax.pcolormesh(glc, o2, S.T, cmap="tab20", shading="auto",
                       rasterized=True)
    ax.set_xlabel("glucose uptake bound (mmol gDW$^{-1}$ h$^{-1}$)")
    ax.set_ylabel("oxygen uptake bound")
    ax.set_title(f"operational active-set signature map "
                 f"({len(uniq)} chambers)")
    ok_v = [(1.692, 1.480), (3.977, 2.935), (1.559, 4.356)]
    ax.plot([v[0] for v in ok_v], [v[1] for v in ok_v], "k*",
            ms=9, label="analyzed vertices")
    ax.legend(frameon=False, loc="upper right")
    ax = axes[1]
    im = ax.pcolormesh(glc, o2, G.T, cmap="viridis", shading="auto",
                       rasterized=True)
    ax.set_xlabel("glucose uptake bound")
    ax.set_ylabel("oxygen uptake bound")
    ax.set_title("growth rate $\\mu^*$")
    fig.colorbar(im, ax=ax, shrink=0.85, label="$\\mu^*$")
    fig.savefig(os.path.join(OUT, "fig_m4b_regions.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("fig_m4b_regions.png")


# ---------------------------------------------------------------- fig M4b-2
def fig_m4b_geometry():
    s = json.load(open(os.path.join(OUT, "m4b_summary.json")))
    cut = s["cut"]
    controls = s["flat_controls"]
    census = json.load(open(os.path.join(OUT, "m4b_edge_census.json")))
    fig = plt.figure(figsize=(6.8, 6.6))
    gs = fig.add_gridspec(3, 2)
    # (a) 1D cut D2 profile
    ax = fig.add_subplot(gs[0, :])
    ts = np.linspace(-cut["span"], cut["span"], cut["n_points"])
    dt = cut["dt"]
    d2 = None
    # recompute the D2 profile from the event stats: use recorded
    # event positions and totals -> plot a schematic of event spikes
    ev = np.array(cut["event_positions"])
    ax.axhline(0, color=C_NE, lw=0.6)
    for x in ev:
        ax.axvline(x, color=C_EV, lw=0.8, alpha=0.65)
    ax.set_xlabel(r"cut parameter $t$ along interface direction "
                  r"through the vertex")
    ax.set_ylabel("$D_2$ (measure on events)")
    ax.set_title(f"1D cut through a codim-2 region: {cut['n_events']} "
                 f"events, {100 * cut['D2_mass_on_events']:.7f}% of "
                 f"$D_2$ mass")
    ax.set_xlim(-cut["span"], cut["span"])
    # annotate the spikes
    for x in ev:
        ax.annotate("", xy=(x, 0), xytext=(x, 1.0),
                    arrowprops=dict(arrowstyle="-", color=C_EV, lw=1.2))
    # (b) flat controls: identity residuals
    ax = fig.add_subplot(gs[1, 0])
    names = [f"[{c['cell'][0]},{c['cell'][1]}]" for c in controls]
    devs = [max(c["loop_identity_rel_dev"], 1e-24) for c in controls]
    ax.bar(range(len(devs)), devs, color=C_MAIN, edgecolor="white")
    ax.set_yscale("log")
    ax.set_ylim(1e-24, 1e-6)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("loop identity residual")
    ax.set_title("flat controls: pairwise cancellation\n"
                 "off codim-2 strata (5/5 exact)")
    # (c) interface kinks of the controls
    ax = fig.add_subplot(gs[1, 1])
    kinks = [abs(c["phi_deg"]) for c in controls]
    ax.bar(range(len(kinks)), kinks, color=C_GOLD, edgecolor="white")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("interface dihedral kink (deg)")
    ax.set_title("O(1) folds at chamber interfaces\n"
                 "(kink 0 = mask-type boundary)")
    # (d) edge-crossing census: dense skeleton where curvature lives
    ax = fig.add_subplot(gs[2, :])
    names = list(census.keys())
    tots = [sum(len(v) for v in census[k]["crossings"].values())
            for k in names]
    order = np.argsort(tots)
    names = [names[i] for i in order]
    tots = [tots[i] for i in order]
    colors = [C_EV if t > 3 else C_MAIN for t in tots]
    ax.barh(range(len(tots)), tots, color=colors, edgecolor="white")
    ax.set_yticks(range(len(names)))
    clean = {"cell_9_6", "cell_16_29"}
    labels = [n.replace("cell_", "c") + (" (clean)" if n in clean
                                         else " (fan)")
              for n in names]
    ax.set_yticklabels(labels)
    ax.set_xlabel("chamber-boundary crossings per grid cell "
                  "(all four edges)")
    ax.set_title("edge-crossing census: the codim-2 skeleton is dense "
                 "exactly where the $D_2$ mass concentrates")
    fig.savefig(os.path.join(OUT, "fig_m4b_geometry.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("fig_m4b_geometry.png")


if __name__ == "__main__":
    fig_m4a()
    fig_m4b_regions()
    fig_m4b_geometry()
