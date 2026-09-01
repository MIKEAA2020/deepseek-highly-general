#!/usr/bin/env python3
"""M4b addendum: full edge-crossing census for the structurally rich
cells.  Single-crossing bisection under-fits the chamber complex: the
low-nutrient corner is a nested wedge-fan (thin sliver chambers between
the wide ones, vertical fan lines T-terminating on sliver boundaries).
This census resolves ALL crossings per cell edge and records the
anatomy, formalizing the resolution obstruction (the codim-2 skeleton
is dense exactly where the curvature measure concentrates).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
m4b = importlib.import_module("m4b_2d_geometry")

OUT = "/home/z/my-project/download/m4"


def edge_crossings(sv, p, q, nseg=12, depth=8):
    """All signature-change points on the segment p->q (scan + bisect)."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    pts = [p + (q - p) * (k / nseg) for k in range(nseg + 1)]
    sigs = [m4b.sig_id_at(sv, x) for x in pts]
    out = []
    for k in range(nseg):
        if sigs[k] != sigs[k + 1]:
            lo, hi = pts[k].copy(), pts[k + 1].copy()
            slo = sigs[k]
            for _ in range(depth):
                mid = 0.5 * (lo + hi)
                s = m4b.sig_id_at(sv, mid)
                if s == slo:
                    lo = mid
                else:
                    hi = mid
            b = 0.5 * (lo + hi)
            out.append((b.tolist(),
                        (sigs[k] % 10000, sigs[k + 1] % 10000)))
    return out


def main():
    eng, bi = m4b.build()
    sv = m4b.Solver(eng, bi)
    z = np.load(os.path.join(OUT, "m4b_grid.npz"), allow_pickle=True)
    glc_ax, o2_ax, SIG = z["glc_ax"], z["o2_ax"], z["SIG"]
    cells = m4b.find_cells(SIG)
    census = {}
    targets = ([tuple(c) for c in cells["cross"]]
               + [tuple(c) for c in cells["other"][:6]]
               + [(9, 6), (0, 2), (16, 29)])      # flat-control cells too
    for cell in targets:
        i, j = cell
        if not (0 <= i < len(glc_ax) - 1 and 0 <= j < len(o2_ax) - 1):
            continue
        corners = dict(BL=(glc_ax[i], o2_ax[j]),
                       BR=(glc_ax[i + 1], o2_ax[j]),
                       TL=(glc_ax[i], o2_ax[j + 1]),
                       TR=(glc_ax[i + 1], o2_ax[j + 1]))
        rec = {}
        for ename, a, b in [("bottom", "BL", "BR"), ("top", "TL", "TR"),
                            ("left", "BL", "TL"), ("right", "BR", "TR")]:
            xs = edge_crossings(sv, corners[a], corners[b])
            rec[ename] = [dict(point=[float(v) for v in p],
                               sig_pair=[int(x) for x in pr])
                          for p, pr in xs]
        census[f"cell_{i}_{j}"] = dict(
            glc=[float(glc_ax[i]), float(glc_ax[i + 1])],
            o2=[float(o2_ax[j]), float(o2_ax[j + 1])],
            corner_sigs={k: int(m4b.sig_id_at(sv, np.array(v)) % 10000)
                         for k, v in corners.items()},
            crossings=rec)
        n_tot = sum(len(v) for v in rec.values())
        print(f"cell ({i},{j}): {n_tot} edge crossings total "
              f"(bottom {len(rec['bottom'])}, top {len(rec['top'])}, "
              f"left {len(rec['left'])}, right {len(rec['right'])})",
              flush=True)
    with open(os.path.join(OUT, "m4b_edge_census.json"), "w") as f:
        json.dump(census, f, indent=2)
    print(f"saved {OUT}/m4b_edge_census.json ({len(census)} cells)")


if __name__ == "__main__":
    main()
