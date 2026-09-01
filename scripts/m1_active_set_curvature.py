#!/usr/bin/env python3
"""
M1 -- Second-order finite differences of the lexicographic-pFBA response
path vs active-set switches (iML1515 + iJO1366 replication).

Executes the strengthened M1 from the joint assessment of the six
"unifying object" audits (opus Route C1, upgraded to the FBA
active-set verification specified by the user):

  * sweep a scalar parameter theta (glucose uptake, O2 uptake, or gene
    knockdown capacity c) over a fine grid;
  * at each theta_k solve the 3-stage lexicographic pFBA (biomass ->
    parsimony -> fixed-weight tie-break; unique deterministic optimum)
    -> flux vector v(theta_k);
  * first-order response   D1_k = ||v_{k+1} - v_k||_1
  * second-order response  D2_k = ||v_{k+1} - 2 v_k + v_{k-1}||_1
    (discrete curvature of the solution path);
  * operational active-set events: change of the material support
    S(theta) or the binding set B(theta) between theta_{k-1} and
    theta_{k+1} (robustness thresholds 1e-6 / 1e-5);
  * tests: D2 mass concentration on events, fold enrichment,
    Mann-Whitney, rank AUC, turning angle, piecewise-affine segment
    residuals.

Theory anchor: for a parametric LP whose parameter enters constraint
bounds linearly, the lexicographic optimum path is piecewise affine in
theta with breakpoints at active-set (basis) changes, so the path's
second derivative is a measure supported on those changes -- the
discrete analogue of curvature singular at stratum boundaries (mpLP
critical-region picture).

Outputs -> /home/z/my-project/download/m1_m3/ :
  m1_<tag>.npz            raw sweep data (V, S, B, S5, B5, growth, t)
  m1_points_<tag>.csv     per-grid-point diagnostics
  m1_summary.json         aggregate statistics (part 'stats')

Usage: python m1_active_set_curvature.py --part nutrient|kd|ijo|stats
"""
import argparse
import json
import os
import sys
import time
import warnings
from collections import Counter

import numpy as np
import cobra
from cobra.util.solver import linear_reaction_coefficients
from scipy.stats import mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_engine import LPEngine

warnings.filterwarnings("ignore")

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "m1_m3")
os.makedirs(OUT, exist_ok=True)

TOL_M = 1e-6        # material-flux threshold (main)
TOL_M5 = 1e-5       # material-flux threshold (robustness)
TOL_B = 1e-7        # binding tolerance, absolute

KD_GENES = ["pgi", "zwf", "tktA", "pfkA", "eno", "gltA", "aceA",
            "ppc", "gnd", "rpe"]


def build_engine(path):
    model = cobra.io.load_json_model(path)
    co = linear_reaction_coefficients(model)
    c_bio = np.zeros(len(model.reactions))
    for r, c in co.items():
        c_bio[model.reactions.index(r)] = c
    bio_id = list(co.keys())[0].id
    rng = np.random.default_rng(20240901)
    W = rng.uniform(0.5, 1.5, len(model.reactions))
    eng = LPEngine(model, W, c_bio)
    return model, eng, eng.index[bio_id], bio_id


def classify(v, lb, ub):
    material = np.abs(v) >= TOL_M
    material5 = np.abs(v) >= TOL_M5
    at_bound = (np.abs(v - lb) <= TOL_B) | (np.abs(v - ub) <= TOL_B)
    return material, material & at_bound, material5, material5 & at_bound


def run_sweep(eng, bio_idx, base_lb, base_ub, apply_param, values, tag):
    """apply_param(value, lb, ub) mutates bound arrays in place (from
    base copies)."""
    n, R = len(values), eng.R
    V = np.full((n, R), np.nan)
    growth = np.full(n, np.nan)
    S = np.zeros((n, R), np.uint8)
    B = np.zeros((n, R), np.uint8)
    S5 = np.zeros((n, R), np.uint8)
    B5 = np.zeros((n, R), np.uint8)
    t0 = time.time()
    for k, val in enumerate(values):
        lb = base_lb.copy()
        ub = base_ub.copy()
        apply_param(val, lb, ub)
        out = eng.solve_lex(lb, ub, bio_idx)
        if out is not None:
            v, mu, s2 = out
            V[k] = v
            growth[k] = mu
            s, b, s5, b5 = classify(v, lb, ub)
            S[k], B[k], S5[k], B5[k] = s, b, s5, b5
        if (k + 1) % 100 == 0:
            el = time.time() - t0
            print(f"  [{tag}] {k + 1}/{n} ({el:.0f}s, "
                  f"{el / (k + 1):.2f}s/pt)", flush=True)
    np.savez_compressed(
        os.path.join(OUT, f"m1_{tag}.npz"), V=V, S=S, B=B, S5=S5, B5=B5,
        growth=growth, t=np.asarray(values), lb=base_lb, ub=base_ub,
        rxn_ids=np.array(eng.rxn_ids))
    print(f"[{tag}] done: {int(np.isfinite(growth).sum())}/{n} feasible "
          f"({time.time() - t0:.0f}s)", flush=True)
    return V, growth, S, B


# ------------------------------------------------------------- experiments
def part_nutrient():
    model, eng, bi, bio_id = build_engine(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    print(f"iML1515: {eng.R} reactions, biomass = {bio_id}")

    # determinism self-test (must be bit-exact)
    o1 = eng.solve_lex(eng.lb0, eng.ub0, bi)
    o2 = eng.solve_lex(eng.lb0, eng.ub0, bi)
    d = float(np.max(np.abs(o1[0] - o2[0])))
    print(f"determinism: max|v1-v2| = {d:.2e}")
    assert d == 0.0, "engine non-deterministic!"

    base_lb, base_ub = eng.lb0, eng.ub0
    v_wt = o1[0]
    np.save(os.path.join(OUT, "m1_wt_reference.npy"), v_wt)
    print(f"WT: mu={o1[1]:.6f}, s2={o1[2]:.4f}")

    i_glc = eng.index["EX_glc__D_e"]

    def set_glc(t, lb, ub):
        lb[i_glc] = -t

    run_sweep(eng, bi, base_lb, base_ub, set_glc,
              np.linspace(1.0, 10.0, 250), "iml_glucose")

    i_o2 = eng.index["EX_o2_e"]

    def set_o2(t, lb, ub):
        lb[i_o2] = -t

    run_sweep(eng, bi, base_lb, base_ub, set_o2,
              np.linspace(0.5, 30.0, 250), "iml_o2")


def part_kd():
    model, eng, bi, bio_id = build_engine(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    base_lb, base_ub = eng.lb0, eng.ub0
    by_name = {g.name: g for g in model.genes}
    for name in KD_GENES:
        gene = by_name.get(name)
        if gene is None:
            print(f"[kd] {name} not found -- skipped")
            continue
        idxs = [eng.index[r.id] for r in gene.reactions]
        print(f"[kd] {name} ({gene.id}): {len(idxs)} reactions "
              f"{[r.id for r in gene.reactions][:10]}", flush=True)

        def set_c(c, lb, ub, idxs=idxs):
            for i in idxs:
                lb[i] = c * base_lb[i]
                ub[i] = c * base_ub[i]

        vals = np.linspace(0.02, 0.0, 121)
        run_sweep(eng, bi, base_lb, base_ub, set_c, vals, f"kd_{name}")


def part_ijo():
    model, eng, bi, bio_id = build_engine(
        os.path.join(BASE, "data", "bigg_models", "iJO1366.json"))
    print(f"iJO1366: {eng.R} reactions, biomass = {bio_id}")
    i_glc = eng.index["EX_glc__D_e"]

    def set_glc(t, lb, ub):
        lb[i_glc] = -t

    run_sweep(eng, bi, eng.lb0, eng.ub0, set_glc,
              np.linspace(1.0, 10.0, 250), "ijo_glucose")


# ------------------------------------------------------------------- stats
def path_stats(V, S, B, t, v_ref=None):
    n = V.shape[0]
    valid = np.all(np.isfinite(V), axis=1)
    res = {"n_points": int(n), "n_valid": int(valid.sum())}

    D1 = np.abs(V[1:] - V[:-1]).sum(axis=1)
    D2 = np.abs(V[2:] - 2 * V[1:-1] + V[:-2]).sum(axis=1)
    evS = (S[:-2] != S[2:]).any(axis=1)
    evB = (B[:-2] != B[2:]).any(axis=1)
    ev = evS | evB
    trip_valid = valid[:-2] & valid[1:-1] & valid[2:]
    ev = ev & trip_valid
    D2m = np.where(trip_valid, D2, np.nan)
    tot = float(np.nansum(D2m))

    # event reaction attribution
    changed = (S[:-2] != S[2:]) | (B[:-2] != B[2:])
    changed = changed & trip_valid[:, None]
    cnt = Counter()
    ev_material = np.zeros_like(ev)
    for j in np.where(ev)[0]:
        mats = []
        for i in np.where(changed[j])[0]:
            cnt[int(i)] += 1
            if (np.abs(V[j + 1, i]) >= 1e-5 or np.abs(V[j, i]) >= 1e-5
                    or np.abs(V[j - 1, i]) >= 1e-5):
                mats.append(i)
        if mats:
            ev_material[j] = True
    res["n_events_material"] = int(ev_material.sum())
    ev_m = D2m[ev_material]
    if np.any(np.isfinite(ev_m)) and ev_material.sum() > 0:
        res["D2_mass_on_material_events"] = (
            float(np.nansum(ev_m) / tot) if tot > 0 else np.nan)
        res["D2_median_material_event"] = float(np.nanmedian(ev_m))
        ne_f2 = D2m[~ev_material]
        if np.any(np.isfinite(ne_f2)) and ne_f2.size:
            u2, p2 = mannwhitneyu(ev_m, ne_f2, alternative="greater")
            res["AUC_material"] = float(u2 / (ev_m.size * ne_f2.size))
            res["MWU_p_material"] = float(p2)

    dV1 = V[1:] - V[:-1]
    with np.errstate(invalid="ignore", divide="ignore"):
        num = (dV1[1:] * dV1[:-1]).sum(axis=1)
        den = (np.linalg.norm(dV1[1:], axis=1)
               * np.linalg.norm(dV1[:-1], axis=1))
        cosang = np.where(den > 0,
                          np.clip(num / np.where(den > 0, den, 1.0),
                                  -1, 1), 1.0)
    theta = np.degrees(np.arccos(cosang))
    theta = np.where(trip_valid, theta, np.nan)

    ev_f = D2m[ev]
    ne_f = D2m[~ev]
    res["n_events"] = int(ev.sum())
    res["event_fraction"] = float(ev.mean()) if ev.size else np.nan
    res["event_S_only"] = int((evS & ~evB & trip_valid).sum())
    res["event_B_only"] = int((evB & ~evS & trip_valid).sum())
    res["D2_total"] = tot
    if tot > 0 and ev.sum() > 0:
        res["D2_mass_on_events"] = float(np.nansum(ev_f) / tot)
    noise = float(np.nanmedian(ne_f)) if np.any(np.isfinite(ne_f)) else np.nan
    spike = float(np.nanmedian(ev_f)) if np.any(np.isfinite(ev_f)) else np.nan
    res["D2_median_nonevent"] = noise
    res["D2_median_event"] = spike
    res["D2_q05_nonevent"] = (float(np.nanpercentile(ne_f, 5))
                              if np.any(np.isfinite(ne_f)) else np.nan)
    res["D2_max"] = float(np.nanmax(D2m)) if np.any(np.isfinite(D2m)) else np.nan
    if noise is not None and spike is not None and noise > 0:
        res["D2_fold_enrichment"] = spike / noise
    if ne_f.size and np.any(np.isfinite(ne_f)):
        res["affine_fraction_nonevent"] = float(
            np.mean(ne_f[np.isfinite(ne_f)] == 0.0))
    if (np.any(np.isfinite(ev_f)) and np.any(np.isfinite(ne_f))
            and ev_f.size and ne_f.size):
        u, p = mannwhitneyu(ev_f, ne_f, alternative="greater")
        res["MWU_p"] = float(p)
        res["AUC"] = float(u / (ev_f.size * ne_f.size))
    res["theta_median_event"] = (float(np.nanmedian(theta[ev]))
                                 if np.any(np.isfinite(theta[ev]))
                                 else np.nan)
    res["theta_median_nonevent"] = (
        float(np.nanmedian(theta[~ev]))
        if np.any(np.isfinite(theta[~ev])) else np.nan)
    res["theta_max"] = (float(np.nanmax(theta))
                        if np.any(np.isfinite(theta)) else np.nan)

    # piecewise-affine verification on non-event runs
    breaks = set(np.where(ev)[0].tolist())
    run, segments = [], []
    for k in np.where(valid)[0]:
        if k in breaks:
            if len(run) >= 5:
                segments.append((run[0], run[-1]))
            run = []
        else:
            run = run + [k] if run else [k]
    if len(run) >= 5:
        segments.append((run[0], run[-1]))
    seg_stats = []
    for a, b in segments:
        seg = V[a:b + 1]
        if b - a < 4 or not np.all(np.isfinite(seg)):
            continue
        tt = np.linspace(0, 1, seg.shape[0])
        A = np.vstack([np.ones_like(tt), tt]).T
        coef, *_ = np.linalg.lstsq(A, seg, rcond=None)
        resid = np.abs(seg - A @ coef).sum(axis=1)
        scale = np.abs(seg).sum(axis=1) + 1e-9
        seg_stats.append({"i0": int(a), "i1": int(b),
                          "length": int(b - a + 1),
                          "max_abs_residual": float(resid.max()),
                          "max_rel_residual": float((resid / scale).max())})
    seg_stats.sort(key=lambda d: -d["length"])
    res["n_segments_ge5"] = len(seg_stats)
    res["top_segments"] = seg_stats[:5]

    # scalar kappa response (knockdown): manuscript Def 3.21 form
    if v_ref is not None:
        dv = V - v_ref
        kap = np.nansum(np.where(np.abs(dv) > 1e-6, dv ** 2, 0.0), axis=1)
        d2k = kap[2:] - 2 * kap[1:-1] + kap[:-2]
        d2k = np.where(trip_valid, d2k, np.nan)
        res["kappa_curve"] = [float(x) for x in kap]
        res["d2kappa_median_event"] = (
            float(np.nanmedian(np.abs(d2k[ev])))
            if np.any(np.isfinite(d2k[ev])) else np.nan)
        res["d2kappa_median_nonevent"] = (
            float(np.nanmedian(np.abs(d2k[~ev])))
            if np.any(np.isfinite(d2k[~ev])) else np.nan)
        res["kappa_final"] = float(kap[valid][-1]) if valid.any() else np.nan

    extras = {"D1": D1, "D2m": D2m, "ev": ev, "evS": evS, "evB": evB,
              "theta": theta, "counter": cnt}
    return res, extras


def part_stats():
    files = sorted(f for f in os.listdir(OUT) if f.startswith("m1_")
                   and f.endswith(".npz"))
    v_ref = None
    p_ref = os.path.join(OUT, "m1_wt_reference.npy")
    if os.path.exists(p_ref):
        v_ref = np.load(p_ref)
    summary = {"tol_material": TOL_M, "tol_material_robust": TOL_M5,
               "tol_binding": TOL_B, "sweeps": {}}
    rxn_ids = None
    for f in files:
        tag = f[3:-4]
        z = np.load(os.path.join(OUT, f), allow_pickle=True)
        V, S, B, t = z["V"], z["S"], z["B"], z["t"]
        rxn_ids = [str(x) for x in z["rxn_ids"]]
        vr = v_ref if tag.startswith("kd_") else None
        res, ex = path_stats(V, S, B, t, v_ref=vr)
        res5, _ = path_stats(V, z["S5"], z["B5"], t, v_ref=None)
        res["robust_1e5"] = {k: res5.get(k) for k in
                             ["n_events", "D2_mass_on_events",
                              "D2_fold_enrichment", "AUC", "MWU_p"]}
        top = ex["counter"].most_common(15)
        res["top_event_reactions"] = [
            {"reaction": rxn_ids[i], "event_points": int(c)}
            for i, c in top]
        g = z["growth"]
        n = len(t)
        D1 = np.full(n, np.nan)
        D1[:-1] = ex["D1"]
        D2 = np.full(n, np.nan)
        D2[1:-1] = ex["D2m"]
        th = np.full(n, np.nan)
        th[1:-1] = ex["theta"]
        ev = np.zeros(n, int)
        ev[1:-1] = ex["ev"]
        evS = np.zeros(n, int)
        evS[1:-1] = ex["evS"]
        evB = np.zeros(n, int)
        evB[1:-1] = ex["evB"]
        pp = np.column_stack([t, g, D1, D2, ev, evS, evB, th])
        hdr = "t,growth,D1,D2,event,event_S,event_B,theta_deg"
        np.savetxt(os.path.join(OUT, f"m1_points_{tag}.csv"), pp,
                   delimiter=",", header=hdr, comments="", fmt="%.10g")
        summary["sweeps"][tag] = res
        print(f"{tag}: events={res['n_events']}/{res['n_valid']} "
              f"mass={res.get('D2_mass_on_events')} "
              f"fold={res.get('D2_fold_enrichment')} "
              f"AUC={res.get('AUC')} p={res.get('MWU_p')}")
    with open(os.path.join(OUT, "m1_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print("saved m1_summary.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True,
                    choices=["nutrient", "kd", "ijo", "stats"])
    args = ap.parse_args()
    t0 = time.time()
    {"nutrient": part_nutrient, "kd": part_kd,
     "ijo": part_ijo, "stats": part_stats}[args.part]()
    print(f"part {args.part} total {time.time() - t0:.0f}s")
