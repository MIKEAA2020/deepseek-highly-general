#!/usr/bin/env python3
"""Figures for M1 (active-set curvature) and M3 (epistasis + path
dependence). English labels (manuscript language). All data from
download/m1_m3/."""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "m1_m3")

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "legend.fontsize": 8, "figure.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
})

C_EV = "#d62728"      # event color
C_NE = "#7f7f7f"      # non-event
C_MAIN = "#1f77b4"


def load_points(tag):
    d = np.genfromtxt(os.path.join(OUT, f"m1_points_{tag}.csv"),
                      delimiter=",", names=True)
    return d


# ---------------------------------------------------------------- fig M1-1
def sweep_figure(tag, title, fname, xlabel):
    d = load_points(tag)
    t, g = d["t"], d["growth"]
    D1, D2, ev = d["D1"], d["D2"], d["event"]
    th = d["theta_deg"]
    fig, axes = plt.subplots(4, 1, figsize=(6.5, 7.2), sharex=True,
                             constrained_layout=True)
    ax = axes[0]
    ax.plot(t, g, color="#2ca02c", lw=1.4)
    ax.set_ylabel("growth rate $\\mu^*$")
    ax.set_title(title)
    for x in t[ev > 0]:
        ax.axvline(x, color=C_EV, lw=0.6, alpha=0.5)
    ax = axes[1]
    ax.plot(t, D1, color=C_MAIN, lw=1.2)
    ax.set_ylabel("$D_1$\n(first-order\nrerouting)")
    for x in t[ev > 0]:
        ax.axvline(x, color=C_EV, lw=0.6, alpha=0.5)
    ax = axes[2]
    pos = (D2 > 0) & np.isfinite(D2)
    ax.semilogy(t[pos], D2[pos], ".", ms=2.5, color=C_NE)
    ax.semilogy(t[ev > 0], np.maximum(D2[ev > 0], 1e-16), "o", ms=4,
                color=C_EV, label="active-set event")
    ax.set_ylabel("$D_2$\n(second-order\nresponse)")
    ax.legend(loc="best", frameon=False)
    ax.set_yscale("log")
    ax = axes[3]
    ax.plot(t, th, color="#9467bd", lw=0.9)
    for x in t[ev > 0]:
        ax.axvline(x, color=C_EV, lw=0.6, alpha=0.5)
    ax.set_ylabel("turning angle\n$\\theta$ (deg)")
    ax.set_xlabel(xlabel)
    evn = int((ev > 0).sum())
    mass = None
    S = json.load(open(os.path.join(OUT, "m1_summary.json")))
    r = S["sweeps"].get(tag, {})
    mass = r.get("D2_mass_on_events")
    axes[0].text(0.02, 0.92,
                 f"{evn} events; D$_2$ mass on events = "
                 f"{mass:.6f}" if mass is not None else "",
                 transform=axes[0].transAxes, va="top", fontsize=8,
                 color=C_EV)
    fig.savefig(os.path.join(OUT, fname))
    plt.close(fig)
    print("saved", fname)


# ---------------------------------------------------------------- fig M1-3
def knockdown_figure():
    S = json.load(open(os.path.join(OUT, "m1_summary.json")))
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2),
                             constrained_layout=True)
    ax = axes[0]
    for tag, r in sorted(S["sweeps"].items()):
        if not tag.startswith("kd_"):
            continue
        kap = np.array(r.get("kappa_curve", []), dtype=float)
        z = load_points(tag)
        t = z["t"]
        ev = z["event"] > 0
        gene = tag[3:]
        if kap.size:
            ax.loglog(t[np.isfinite(kap) & (kap > 0)],
                      kap[np.isfinite(kap) & (kap > 0)], lw=1.1,
                      label=gene, alpha=0.85)
            if ev.any():
                ax.plot(t[ev & (kap > 0)], kap[ev & (kap > 0)], "v", ms=4,
                        color="k", alpha=0.6)
    ax.set_xlabel("gene capacity $c$")
    ax.set_ylabel("$\\kappa_{\\mathrm{flux}}(c)$")
    ax.set_title("knockdown response curves (8 genes + control)")
    ax.legend(ncol=2, frameon=False, loc="lower left")
    # zoom: pgi with D2
    ax = axes[1]
    z = load_points("kd_pgi")
    ax.plot(z["t"], z["growth"], color="#2ca02c", lw=1.3)
    ax.set_xlabel("pgi capacity $c$")
    ax.set_ylabel("growth rate $\\mu^*$", color="#2ca02c")
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    pos = (z["D2"] > 0) & np.isfinite(z["D2"])
    ax2.loglog(z["t"][pos], z["D2"][pos], ".", ms=2.5, color=C_NE)
    ev = z["event"] > 0
    ax2.loglog(z["t"][ev], np.maximum(z["D2"][ev], 1e-16), "o", ms=4,
               color=C_EV)
    ax2.set_ylabel("$D_2$", color=C_NE)
    ax.set_title("pgi knockdown: growth vs curvature")
    fig.savefig(os.path.join(OUT, "fig_m1_knockdown.png"))
    plt.close(fig)
    print("saved fig_m1_knockdown.png")


# ---------------------------------------------------------------- fig M1-4
def summary_figure():
    S = json.load(open(os.path.join(OUT, "m1_summary.json")))
    tags = [t for t in S["sweeps"] if t != "kd_aceA"]
    tags = sorted(tags, key=lambda t: S["sweeps"][t]["n_events"])
    labels = [t.replace("_", " ") for t in tags]
    mass = [S["sweeps"][t].get("D2_mass_on_events") or 0 for t in tags]
    auc = [S["sweeps"][t].get("AUC") or np.nan for t in tags]
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.4),
                             constrained_layout=True)
    ax = axes[0]
    ev_m, ev_ne = [], []
    for t in tags:
        z = load_points(t)
        D2, ev = z["D2"], z["event"] > 0
        ev_m.append(D2[ev & np.isfinite(D2) & (D2 > 0)])
        ev_ne.append(D2[(~ev) & np.isfinite(D2) & (D2 > 0)])
    parts = ax.violinplot(ev_ne, showmedians=True, widths=0.8)
    for pc in parts["bodies"]:
        pc.set_facecolor(C_NE)
        pc.set_alpha(0.55)
    parts2 = ax.violinplot(ev_m, showmedians=True, widths=0.4)
    for pc in parts2["bodies"]:
        pc.set_facecolor(C_EV)
        pc.set_alpha(0.7)
    ax.set_yscale("log")
    ax.set_xticks(range(1, len(tags) + 1))
    ax.set_xticklabels([str(S["sweeps"][t]["n_events"]) for t in tags],
                       fontsize=7)
    ax.set_xlabel("sweep (x = #events)")
    ax.set_ylabel("$D_2$ distribution")
    ax.set_title("off-event (grey) vs event (red)")
    ax = axes[1]
    ax.bar(range(len(tags)), mass, color=C_MAIN, alpha=0.85)
    ax.set_ylim(0.9, 1.0000001)
    ax.set_xticks(range(len(tags)))
    ax.set_xticklabels([l.replace("iml ", "").replace("kd ", "")
                        for l in labels], rotation=60, ha="right",
                       fontsize=6.5)
    ax.set_ylabel("fraction of $D_2$ mass on events")
    ax.set_title("curvature mass concentration")
    ax = axes[2]
    ax.bar(range(len(tags)), auc, color="#ff7f0e", alpha=0.9)
    ax.set_ylim(0.5, 1.02)
    ax.set_xticks(range(len(tags)))
    ax.set_xticklabels([l.replace("iml ", "").replace("kd ", "")
                        for l in labels], rotation=60, ha="right",
                       fontsize=6.5)
    ax.set_ylabel("rank AUC")
    ax.set_title("D$_2$ ranks vs event labels")
    fig.savefig(os.path.join(OUT, "fig_m1_summary.png"))
    plt.close(fig)
    print("saved fig_m1_summary.png")


# ---------------------------------------------------------------- fig M3-1
def epistasis_figure():
    rows = list(csv.DictReader(open(os.path.join(OUT, "m3_pairs.csv"))))

    def f(r, c):
        try:
            return float(r[c])
        except (TypeError, ValueError):
            return np.nan
    ki = np.array([f(r, "kappa_i") for r in rows])
    kj = np.array([f(r, "kappa_j") for r in rows])
    kij = np.array([f(r, "kappa_ij") for r in rows])
    eps = np.array([f(r, "eps_add") for r in rows])
    JR = np.array([f(r, "J_dR") for r in rows])
    SL = np.array([r["SL"] == "True" for r in rows])
    ISO = np.array(["ISO" in r["panel"] for r in rows])
    fig, axes = plt.subplots(1, 3, figsize=(9.8, 3.4),
                             constrained_layout=True)
    ax = axes[0]
    m = np.isfinite(kij) & (ki + kj + kij > 0)
    ax.loglog((ki[m] + kj[m] + 1e-9), kij[m] + 1e-9, ".", ms=2.2,
              color=C_NE, alpha=0.5, label="pairs")
    mm = m & SL
    ax.loglog((ki[mm] + kj[mm] + 1e-9), kij[mm] + 1e-9, "o", ms=4,
              color=C_EV, label="synthetic lethal")
    lim = [1e-9, 1e5]
    ax.plot(lim, lim, "k--", lw=0.8, label="additivity $\\kappa_{ij}=\\kappa_i+\\kappa_j$")
    ax.set_xlabel("$\\kappa_i + \\kappa_j$")
    ax.set_ylabel("$\\kappa_{ij}$")
    ax.set_title("double-KO rerouting vs additivity")
    ax.legend(frameon=False, loc="upper left", fontsize=7)
    ax = axes[1]
    m = np.isfinite(eps) & np.isfinite(JR) & ~SL
    ax.scatter(JR[m], np.abs(eps[m]), s=3, c=C_MAIN, alpha=0.45,
               linewidths=0)
    m = SL & np.isfinite(eps)
    ax.scatter(JR[m], np.abs(eps[m]), s=12, c=C_EV, alpha=0.8,
               linewidths=0, label="SL (all isozyme)")
    ax.set_yscale("log")
    ax.set_xlabel("active-set footprint overlap $J(\\Delta R_i,\\Delta R_j)$")
    ax.set_ylabel("$|\\varepsilon_{ij}|$")
    ax.set_title("epistasis vs footprint overlap\n"
                 "(Spearman $\\rho$=0.865, $p\\approx 0$)")
    ax.legend(frameon=False, fontsize=7)
    ax = axes[2]
    m = np.isfinite(eps)
    e = eps[m]
    e = e[e != 0]
    ax.hist(np.sign(e) * np.log10(np.abs(e) + 1e-9), bins=60,
            color=C_MAIN, alpha=0.8)
    ax.set_xlabel("sign($\\varepsilon$)$\\cdot\\log_{10}|\\varepsilon|$")
    ax.set_ylabel("# pairs")
    ax.set_title("epistasis distribution "
                 "($\\varepsilon=\\kappa_{ij}-\\kappa_i-\\kappa_j$)")
    ax.axvline(0, color="k", lw=0.8)
    fig.savefig(os.path.join(OUT, "fig_m3_epistasis.png"))
    plt.close(fig)
    print("saved fig_m3_epistasis.png")


# ---------------------------------------------------------------- fig M3-2
def path_figure():
    rows = list(csv.DictReader(open(os.path.join(OUT, "m3_path.csv"))))

    def f(r, c):
        return float(r[c])
    chi = np.array([f(r, "chi") for r in rows])
    hA = np.array([f(r, "h_loop_ifirst") for r in rows])
    kif = np.array([f(r, "kappa_moma_ij_ifirst") for r in rows])
    kjf = np.array([f(r, "kappa_moma_ij_jfirst") for r in rows])
    SL = np.array([r["SL"] == "True" for r in rows])
    fig, axes = plt.subplots(1, 3, figsize=(9.8, 3.4),
                             constrained_layout=True)
    ax = axes[0]
    data = [chi[SL], chi[~SL]]
    parts = ax.violinplot([np.maximum(d[d > 0], 1e-16) if (d > 0).any()
                           else [1e-16] for d in data], showmedians=True)
    for pc, c in zip(parts["bodies"], [C_EV, C_MAIN]):
        pc.set_facecolor(c)
        pc.set_alpha(0.6)
    ax.set_yscale("log")
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["synthetic lethal\n(isozyme)", "active pairs\n(non-SL)"])
    ax.set_ylabel("commutator $\\chi_{ij}$")
    ax.set_title("open-path non-commutativity\n"
                 "$\\|s^{i\\to j}-s^{j\\to i}\\|_1$ (25% of non-SL > 0)")
    ax = axes[1]
    m = (kif > 0) & (kjf > 0)
    ax.loglog(kif[m], kjf[m], ".", ms=3, color=C_MAIN, alpha=0.6)
    ax.loglog(kif[m & SL], kjf[m & SL], "o", ms=4, color=C_EV, alpha=0.8)
    lim = [1e-3, 1e6]
    ax.plot(lim, lim, "k--", lw=0.8)
    ax.set_xlabel("$\\kappa^{(i\\to j)}$ (i first)")
    ax.set_ylabel("$\\kappa^{(j\\to i)}$ (j first)")
    ax.set_title("MOMA $\\kappa$ is path-dependent\n"
                 "(19.4% of pairs off-diagonal)")
    ax = axes[2]
    hpos = hA[hA > 0]
    ax.hist(np.log10(np.maximum(hpos, 1e-9)), bins=40, color="#9467bd",
            alpha=0.85)
    ax.axvline(np.log10(1e-9), color="k", lw=0.8, linestyle="--")
    ax.set_xlabel("$\\log_{10}$ loop holonomy $\\|s_{\\mathrm{final}}-s_0\\|_1$")
    ax.set_ylabel("# pairs")
    ax.set_title("closed genotype loops:\n66% do not return to $s_0$")
    fig.savefig(os.path.join(OUT, "fig_m3_path.png"))
    plt.close(fig)
    print("saved fig_m3_path.png")


if __name__ == "__main__":
    sweep_figure("iml_glucose",
                 "M1 - iML1515 glucose sweep (250 pts)",
                 "fig_m1_glucose.png",
                 "glucose uptake bound (mmol gDW$^{-1}$ h$^{-1}$)")
    sweep_figure("iml_o2",
                 "M1 - iML1515 oxygen sweep (250 pts, glucose 10)",
                 "fig_m1_o2.png",
                 "O$_2$ uptake bound (mmol gDW$^{-1}$ h$^{-1}$)")
    knockdown_figure()
    summary_figure()
    epistasis_figure()
    path_figure()
    print("all figures done")
