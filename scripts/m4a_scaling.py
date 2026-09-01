#!/usr/bin/env python3
"""
M4a -- Scaling test of the dynamic (sequential L1-MOMA) commutator.

Purpose: the DeepSeek "Active-Set Bridge Conjecture" (external_audits/
unifying object/deepseek formulation.txt) asserts a scaling limit

    lim_{eps->0} (1/eps^2) (H_eps - I) = Omega

(A4, "the missing ingredient ... a proof of the scaling limit").  The
static lex-pFBA map cannot carry this limit (it is a single-valued
function: closed-loop holonomy is exactly the identity).  The only
path-dependent object in the executed program is the sequential
L1-MOMA adjustment of M3b.  This experiment measures the actual
scaling exponent of that object under a linearly-scaled perturbation
family, which is the honest, computable version of A4.

Design (flux-relative knockdown, eps = perturbation depth):
  For each gene set G and depth eps, the bounds of the reactions
  disabled by G in M3 are scaled toward the WT operating point:

      v_wt[k] > 0 :  ub_k(eps) = (1-eps) v_wt[k],  lb_k(eps) = (1-eps) lb_base
      v_wt[k] < 0 :  lb_k(eps) = (1-eps) v_wt[k],  ub_k(eps) = (1-eps) ub_base
      v_wt[k] = 0 :  both homothetic: (1-eps) * base bounds

  eps = 0  -> WT feasible set at the operating point (MOMA = identity),
  eps = 1  -> exactly the M3 full knockout ([0,0] on all disabled
              reactions).  The perturbation binds for every eps > 0 on
              every nonzero-flux reaction (no capacity-slack threshold).

Measured per pair (i, j) and eps:
  s_i(eps)   = MOMA(v_wt ; bounds_i(eps))
  s_j(eps)   = MOMA(v_wt ; bounds_j(eps))
  s_ij^i     = MOMA(s_i(eps) ; bounds_ij(eps))      (i applied first)
  s_ij^j     = MOMA(s_j(eps) ; bounds_ij(eps))      (j applied first)
  chi(eps)   = || s_ij^i - s_ij^j ||_1              (open-path commutator)
  d1_i(eps)  = || s_i(eps) - v_wt ||_1              (single response, O(eps) control)
  release identity check: MOMA(s_ij^i ; bounds_j(eps)) == s_ij^i
    (relaxation projections must be exact identities -- verifies that
     the M3b closed-loop non-return is irreversibility, not a release
     adjustment)

Predictions adjudicated by the data:
  slope(log chi vs log eps) ~ 2  -> the eps^2 / commutator law holds
                                    (A4 true in the dynamic layer)
  slope ~ 1                      -> first-order non-commutativity: the
                                    tangent-cone change at each knockout
                                    is an O(1) jump and order mismatch
                                    accumulates at O(eps) (A4 false as
                                    stated; repaired statement needed)

Usage: python m4a_scaling.py
"""
import csv
import json
import os
import sys
import time
import warnings

import numpy as np
import cobra
from cobra.util.solver import linear_reaction_coefficients

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_engine import LPEngine, gpr_dnf, disabled_reactions

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "m4")
os.makedirs(OUT, exist_ok=True)

EPS_GRID = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
CHI_FLOOR = 1e-6          # below this chi is treated as exactly zero
RNG = np.random.default_rng(20260901)

N_TOP = 30                # top-|eps| non-SL pairs
N_RAND = 30               # random non-SL pairs
N_SL = 10                 # synthetic-lethal pairs (feasible only eps<1)
ARCHETYPES = [            # M3 archetypes by gene name
    ("zwf", "gnd"), ("pfkA", "pfkB"), ("pgi", "zwf"),
    ("tktA", "tktB"), ("rpe", "rpiA"), ("acnA", "acnB"),
]
RELEASE_CHECK_PAIRS = 6   # verify release-identity on this many pairs


def build():
    model = cobra.io.load_json_model(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    co = linear_reaction_coefficients(model)
    c_bio = np.zeros(len(model.reactions))
    for r, c in co.items():
        c_bio[model.reactions.index(r)] = c
    rng = np.random.default_rng(20240901)     # same tie-break weights as M1/M3
    W = rng.uniform(0.5, 1.5, len(model.reactions))
    eng = LPEngine(model, W, c_bio)
    dnf = gpr_dnf(model)
    by_name = {g.name: g.id for g in model.genes}
    return model, eng, dnf, by_name


def scaled_bounds(eng, v_wt, idx, eps):
    """Flux-relative knockdown bounds at depth eps (see module docstring)."""
    lb = eng.lb0.copy()
    ub = eng.ub0.copy()
    c = 1.0 - eps
    for k in idx:
        if v_wt[k] > 0:
            ub[k] = c * v_wt[k]
            lb[k] = c * eng.lb0[k]
        elif v_wt[k] < 0:
            lb[k] = c * v_wt[k]
            ub[k] = c * eng.ub0[k]
        else:
            lb[k] = c * eng.lb0[k]
            ub[k] = c * eng.ub0[k]
    return lb, ub


def pick_pairs(model, by_name):
    rows = list(csv.DictReader(open(os.path.join(
        BASE, "download", "m1_m3", "m3_pairs.csv"))))
    tof = lambda x: float(x) if x not in ("", None) else np.nan
    non_sl = [r for r in rows if r["SL"] == "False"]
    sl = [r for r in rows if r["SL"] == "True"]
    top = sorted(non_sl, key=lambda r: -abs(tof(r["eps_add"])))[:N_TOP]
    rest = [r for r in non_sl if r not in top]
    rand = list(RNG.choice(rest, size=min(N_RAND, len(rest)), replace=False))
    slp = sl[:N_SL]
    chosen, seen = [], set()
    for r in top + rand + slp:
        key = (r["g1"], r["g2"])
        if key not in seen:
            seen.add(key)
            chosen.append(dict(g1=r["g1"], g2=r["g2"],
                               n1=r["n1"], n2=r["n2"],
                               eps_add=tof(r["eps_add"]), SL=r["SL"],
                               panel=r["panel"], origin="panel"))
    for a, b in ARCHETYPES:
        ga, gb = by_name.get(a), by_name.get(b)
        if ga is None or gb is None:
            continue
        key = (ga, gb)
        if key not in seen and (gb, ga) not in seen:
            seen.add(key)
            chosen.append(dict(g1=ga, g2=gb, n1=a, n2=b,
                               eps_add=np.nan, SL=False,
                               panel="ARCH", origin="archetype"))
    return chosen


def main():
    t00 = time.time()
    model, eng, dnf, by_name = build()
    v_wt = np.load(os.path.join(BASE, "download", "m1_m3",
                                "m1_wt_reference.npy"))
    pairs = pick_pairs(model, by_name)
    print(f"pairs: {len(pairs)} "
          f"({N_TOP} top-|eps| + {N_RAND} random + {N_SL} SL + "
          f"{len(ARCHETYPES)} archetypes)", flush=True)

    gene_rx = {}
    for g in {p["g1"] for p in pairs} | {p["g2"] for p in pairs}:
        dis = disabled_reactions(dnf, [g])
        gene_rx[g] = [eng.index[r] for r in dis]

    moma_cache = {}

    def moma(idx, eps, v_ref):
        key = (tuple(idx), eps)
        if key not in moma_cache:
            lb, ub = scaled_bounds(eng, v_wt, idx, eps)
            moma_cache[key] = eng.solve_moma(lb, ub, v_ref)
        return moma_cache[key]

    # NOTE: caching keyed by (gene-set, eps) is sound for the SINGLES
    # (v_ref = v_wt always), but the double states depend on the path,
    # so they are solved directly below.
    out_rows = []
    release_checks = []
    for q, p in enumerate(pairs):
        i, j = p["g1"], p["g2"]
        idx_i, idx_j = gene_rx[i], gene_rx[j]
        idx_ij = sorted(set(idx_i) | set(idx_j))
        for eps in EPS_GRID:
            s_i = moma(tuple(idx_i), eps, v_wt)
            s_j = moma(tuple(idx_j), eps, v_wt)
            if s_i is None or s_j is None:
                out_rows.append(dict(p, eps=eps, feasible=False,
                                     chi=np.nan, d1_i=np.nan, d1_j=np.nan,
                                     d1_ij=np.nan))
                continue
            lb, ub = scaled_bounds(eng, v_wt, idx_ij, eps)
            s_ij_i = eng.solve_moma(lb, ub, s_i)     # i first
            s_ij_j = eng.solve_moma(lb, ub, s_j)     # j first
            if s_ij_i is None or s_ij_j is None:
                out_rows.append(dict(p, eps=eps, feasible=False,
                                     chi=np.nan, d1_i=np.nan, d1_j=np.nan,
                                     d1_ij=np.nan))
                continue
            chi = float(np.abs(s_ij_i - s_ij_j).sum())
            d1_i = float(np.abs(s_i - v_wt).sum())
            d1_j = float(np.abs(s_j - v_wt).sum())
            d1_ij = float(np.abs(s_ij_i - v_wt).sum())
            out_rows.append(dict(p, eps=eps, feasible=True, chi=chi,
                                 d1_i=d1_i, d1_j=d1_j, d1_ij=d1_ij))
            # release-identity verification (first pairs, largest eps)
            if (q < RELEASE_CHECK_PAIRS and eps == EPS_GRID[0]
                    and len(release_checks) < RELEASE_CHECK_PAIRS):
                lbj, ubj = scaled_bounds(eng, v_wt, idx_j, eps)
                s3 = eng.solve_moma(lbj, ubj, s_ij_i)
                lbi, ubi = scaled_bounds(eng, v_wt, idx_i, eps)
                s4 = eng.solve_moma(lbi, ubi, s_ij_j)
                ok1 = s3 is not None and float(
                    np.abs(s3 - s_ij_i).max()) == 0.0
                ok2 = s4 is not None and float(
                    np.abs(s4 - s_ij_j).max()) == 0.0
                release_checks.append(dict(
                    g1=i, g2=j, n1=p["n1"], n2=p["n2"], eps=eps,
                    release_i_identity=ok1, release_j_identity=ok2,
                    max_dev_release_i=(None if s3 is None else float(
                        np.abs(s3 - s_ij_i).max())),
                    max_dev_release_j=(None if s4 is None else float(
                        np.abs(s4 - s_ij_j).max()))))
        if (q + 1) % 10 == 0:
            el = time.time() - t00
            print(f"  {q + 1}/{len(pairs)} pairs ({el:.0f}s, "
                  f"{el / (q + 1):.1f}s/pair)", flush=True)

    # ------------------------------------------------------- slope analysis
    def slope_fit(d):
        pts = [(r["eps"], r["chi"]) for r in d
               if r["feasible"] and np.isfinite(r["chi"])
               and r["chi"] > CHI_FLOOR]
        if len(pts) < 3:
            return None, len(pts)
        x = np.log([p[0] for p in pts])
        y = np.log([p[1] for p in pts])
        A = np.column_stack([x, np.ones_like(x)])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        return float(coef[0]), len(pts)

    pair_summary = []
    by_pair = {}
    for r in out_rows:
        by_pair.setdefault((r["g1"], r["g2"]), []).append(r)
    for (g1, g2), d in by_pair.items():
        d = sorted(d, key=lambda r: -r["eps"])
        sl, npts = slope_fit(d)
        chis = [r["chi"] for r in d if r["feasible"]]
        n_zero = sum(1 for c in chis if np.isfinite(c) and c <= CHI_FLOOR)
        d1s = [(r["eps"], r["d1_i"]) for r in d
               if r["feasible"] and np.isfinite(r.get("d1_i", np.nan))
               and r["d1_i"] > CHI_FLOOR]
        sl1 = None
        if len(d1s) >= 3:
            x = np.log([p[0] for p in d1s])
            y = np.log([p[1] for p in d1s])
            A = np.column_stack([x, np.ones_like(x)])
            coef, *_ = np.linalg.lstsq(A, y, rcond=None)
            sl1 = float(coef[0])
        if sl is None:
            cls = "zero" if n_zero == len(chis) and chis else "insufficient"
        elif sl < 0.7:
            cls = "sublinear"
        elif sl < 1.3:
            cls = "slope~1"
        elif sl < 1.7:
            cls = "slope~1.5"
        elif sl < 2.3:
            cls = "slope~2"
        else:
            cls = "superlinear"
        meta = d[0]
        pair_summary.append(dict(
            g1=g1, g2=g2, n1=meta["n1"], n2=meta["n2"],
            SL=meta["SL"], panel=meta["panel"], origin=meta["origin"],
            slope_chi=sl, n_fit_points=npts, class_chi=cls,
            slope_d1_i=sl1,
            chi_max=max([c for c in chis if np.isfinite(c)], default=0.0),
            chi_at_eps1=next((r["chi"] for r in d if r["eps"] == 1.0
                              and r["feasible"]), np.nan)))

    cls_counts = {}
    for s in pair_summary:
        cls_counts[s["class_chi"]] = cls_counts.get(s["class_chi"], 0) + 1
    slopes2 = [s["slope_chi"] for s in pair_summary
               if s["slope_chi"] is not None]
    slopes_d1 = [s["slope_d1_i"] for s in pair_summary
                 if s["slope_d1_i"] is not None]
    summary = dict(
        experiment="M4a scaling of the sequential L1-MOMA commutator",
        model="iML1515", n_pairs=len(pair_summary),
        eps_grid=EPS_GRID, chi_floor=CHI_FLOOR,
        bound_convention="flux-relative: ub=(1-eps)v_wt on v>0, mirrored "
                         "on v<0, homothetic on v=0; eps=1 equals the M3 "
                         "full knockout",
        class_counts=cls_counts,
        median_slope_chi=(float(np.median(slopes2)) if slopes2 else None),
        mean_slope_chi=(float(np.mean(slopes2)) if slopes2 else None),
        median_slope_d1_single=(float(np.median(slopes_d1))
                                if slopes_d1 else None),
        release_identity_checks=release_checks,
        runtime_s=round(time.time() - t00, 1))

    with open(os.path.join(OUT, "m4a_scaling.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "g1", "g2", "n1", "n2", "eps", "feasible", "chi",
            "d1_i", "d1_j", "d1_ij", "eps_add", "SL", "panel", "origin"])
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k) for k in w.fieldnames})
    with open(os.path.join(OUT, "m4a_pairs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pair_summary[0].keys()))
        w.writeheader()
        for s in pair_summary:
            w.writerow(s)
    with open(os.path.join(OUT, "m4a_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("release_identity_checks",)},
                     indent=2))
    print(f"\nrelease identity checks: "
          f"{sum(1 for c in release_checks if c['release_i_identity'])}"
          f"/{len(release_checks)} exact (i-release), "
          f"{sum(1 for c in release_checks if c['release_j_identity'])}"
          f"/{len(release_checks)} exact (j-release)")
    print(f"done in {time.time() - t00:.0f}s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
