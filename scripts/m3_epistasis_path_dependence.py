#!/usr/bin/env python3
"""
M3 -- Double-knockout epistasis of the FBA rerouting statistic
kappa_flux, plus sequential path dependence (non-commutativity /
plaquette holonomy). iML1515, glucose minimal aerobic.

Executes the strengthened M3 (opus Route C2) from the joint assessment
of the six "unifying object" audits, as specified by the user:

  * kappa_flux(g) = sum_{r in dR(g)} (v_r(KO) - v_r(WT))^2
    (manuscript Definition "ard-derived-kappa-V", v10 main definition,
    unmasked variant; masked variant 1[db > 0.05 b_wt] also reported)
  * single KOs: all 1516 genes -> kappa_i, growth_i, footprints
  * double KOs: pair panels -> kappa_ij
  * epistasis  eps_ij = kappa_ij - kappa_i - kappa_j
    (the mixed second difference: the discrete curvature object of the
    FBA thread; "FBA = epistasis" in the assessment's Layer-1 reading)
  * multiplicative analogue rho_ij = kappa_ij / (kappa_i + kappa_j)
  * active-set footprint overlap: Jaccard of support-change masks
  * synthetic lethality census (viable singles, dead double)
  * path dependence (L1-MOMA sequential adjustment):
      open-path commutator  chi_ij = ||s^{i->j} - s^{j->i}||_1
      closed 4-step loops (i-first vs j-first) returning to WT:
      holonomy h = ||s_final - s_0||_1  (genotype loop, state not
      returned -- the plaquette/Wilson-loop object of audit M2,
      realized in genotype perturbation space)
  * the MOMA-based kappa is itself path dependent:
      kappa^{i->j} != kappa^{j->i}  in general

All optima use the 3-stage lexicographic pFBA (lp_engine), so every
state is unique and deterministic.

Usage: python m3_epistasis_path_dependence.py
       --part singles|pairs|path|stats
"""
import argparse
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
OUT = os.path.join(BASE, "download", "m1_m3")
os.makedirs(OUT, exist_ok=True)

TOL_M = 1e-6        # material threshold (support, dR)
GROWTH_DEAD = 1e-6  # no-growth threshold
EPS0 = 1e-12
TAU_MASK = 0.05     # manuscript essentiality mask threshold

RNG = np.random.default_rng(20260901)


def build():
    model = cobra.io.load_json_model(
        os.path.join(BASE, "data", "bigg_models", "iML1515.json"))
    co = linear_reaction_coefficients(model)
    c_bio = np.zeros(len(model.reactions))
    for r, c in co.items():
        c_bio[model.reactions.index(r)] = c
    bio_id = list(co.keys())[0].id
    rng = np.random.default_rng(20240901)   # same weights as M1
    W = rng.uniform(0.5, 1.5, len(model.reactions))
    eng = LPEngine(model, W, c_bio)
    dnf = gpr_dnf(model)
    return model, eng, eng.index[bio_id], dnf


def kappa_from(v, v_wt):
    dv = v - v_wt
    m = np.abs(dv) > TOL_M
    return float((dv[m] ** 2).sum()), m, dv


def ko_bounds(eng, dis_idx):
    lb = eng.lb0.copy()
    ub = eng.ub0.copy()
    for i in dis_idx:
        lb[i] = 0.0
        ub[i] = 0.0
    return lb, ub


def touched_map(dnf):
    """gene id -> reaction ids whose GPR mentions the gene."""
    tm = {}
    for rid, clauses in dnf.items():
        for cl in clauses:
            for g in cl:
                tm.setdefault(g, set()).add(rid)
    return tm


def disabled_for_pair(dnf, touched, g1, g2):
    """Reactions disabled when BOTH g1 and g2 are non-functional
    (evaluates GPRs correctly, incl. isozyme OR-clauses)."""
    ko = {g1, g2}
    out = []
    for rid in (touched.get(g1, set()) | touched.get(g2, set())):
        clauses = dnf[rid]
        if clauses and all(cl & ko for cl in clauses):
            out.append(rid)
    return out


# --------------------------------------------------------------- singles
def part_singles():
    model, eng, bi, dnf = build()
    gene_ids = [g.id for g in model.genes]
    gene_names = {g.id: g.name for g in model.genes}
    touched = touched_map(dnf)

    # wild type (same deterministic lex-pFBA as M1)
    p_ref = os.path.join(OUT, "m1_wt_reference.npy")
    if os.path.exists(p_ref):
        v_wt = np.load(p_ref)
    else:
        v_wt = eng.solve_lex(eng.lb0, eng.ub0, bi)[0]
        np.save(p_ref, v_wt)
    mu_wt = float(v_wt[bi])
    print(f"WT mu = {mu_wt:.6f}")
    s_wt, b_wt, _, _ = None, None, None, None
    mat_wt = np.abs(v_wt) >= TOL_M
    R = eng.R
    n_g = len(gene_ids)

    growth = np.full(n_g, np.nan)
    kappa_dr = np.full(n_g, np.nan)
    kappa_full = np.full(n_g, np.nan)
    n_dis = np.zeros(n_g, int)
    dS = np.zeros((n_g, R), np.uint8)    # support footprint change
    dR = np.zeros((n_g, R), np.uint8)    # material flux-change mask
    v_ko = np.zeros((n_g, R), np.float32)  # compressed storage

    t0 = time.time()
    for k, gid in enumerate(gene_ids):
        dis = disabled_reactions(dnf, [gid])
        n_dis[k] = len(dis)
        idx = [eng.index[r] for r in dis]
        lb, ub = ko_bounds(eng, idx)
        out = eng.solve_lex(lb, ub, bi)
        if out is None:
            continue          # infeasible -> essential (kappa undefined)
        v, mu, s2 = out
        growth[k] = mu
        v_ko[k] = v
        kap, m, dv = kappa_from(v, v_wt)
        kappa_dr[k] = kap
        kappa_full[k] = float((dv ** 2).sum())
        dS[k] = (np.abs(v) >= TOL_M) != mat_wt
        dR[k] = m
        if (k + 1) % 150 == 0:
            el = time.time() - t0
            print(f"  singles {k + 1}/{n_g} ({el:.0f}s, "
                  f"{el / (k + 1):.2f}s/gene)", flush=True)

    np.savez_compressed(
        os.path.join(OUT, "m3_singles.npz"),
        gene_ids=np.array(gene_ids), growth=growth,
        kappa_dr=kappa_dr, kappa_full=kappa_full, n_dis=n_dis,
        dS=dS, dR=dR, v_ko=v_ko, mu_wt=mu_wt,
        rxn_ids=np.array(eng.rxn_ids))
    viable = np.isfinite(growth) & (growth > GROWTH_DEAD)
    print(f"singles done in {time.time() - t0:.0f}s: "
          f"{int(viable.sum())} viable, "
          f"{int((~np.isfinite(growth)).sum())} infeasible, "
          f"{int((growth <= GROWTH_DEAD).sum())} no-growth")
    # quick sanity: known genes
    for nm in ["pgi", "zwf", "tktA", "tktB", "eno", "gltA"]:
        g = [x.id for x in model.genes if x.name == nm]
        if g:
            k = gene_ids.index(g[0])
            print(f"  {nm}({g[0]}): growth={growth[k]:.6f} "
                  f"kappa_dr={kappa_dr[k]:.4f} n_dis={n_dis[k]}")


# ----------------------------------------------------------------- pairs
def load_singles(eng):
    z = np.load(os.path.join(OUT, "m3_singles.npz"), allow_pickle=True)
    return z


def isozyme_pairs(dnf, viable_set):
    """Gene pairs that are alternatives for the same reaction (appear in
    different OR clauses of one GPR)."""
    from itertools import combinations
    pairs = set()
    for rid, clauses in dnf.items():
        if len(clauses) < 2:
            continue
        # union of genes across clauses of this reaction
        gs = set().union(*clauses)
        # alternatives: genes from different clauses
        for g1, g2 in combinations(sorted(gs), 2):
            if any(g1 in c for c in clauses) and any(g2 in c for c in clauses):
                # not in the same clause (same clause = complex, not isozyme)
                if not any(g1 in c and g2 in c for c in clauses):
                    if g1 in viable_set and g2 in viable_set:
                        pairs.add((g1, g2))
    return sorted(pairs)


def part_pairs():
    model, eng, bi, dnf = build()
    z = load_singles(eng)
    gene_ids = [str(x) for x in z["gene_ids"]]
    gene_names = {g.id: g.name for g in model.genes}
    growth, kappa_dr = z["growth"], z["kappa_dr"]
    dS, dR = z["dS"], z["dR"]
    mu_wt = float(z["mu_wt"])
    v_wt = np.load(os.path.join(OUT, "m1_wt_reference.npy"))
    touched = touched_map(dnf)
    viable = np.isfinite(growth) & (growth > GROWTH_DEAD)
    viable_set = {gene_ids[k] for k in np.where(viable)[0]}
    R = eng.R

    by_name = {g.name: g.id for g in model.genes}
    # ---------------- panels
    ok = [k for k in range(len(gene_ids))
          if viable[k] and np.isfinite(kappa_dr[k])]
    order = sorted(ok, key=lambda k: -kappa_dr[k])
    A = order[:40]                                   # high-kappa stratum
    lowpool = [k for k in ok if kappa_dr[k] <= np.median(kappa_dr[ok])]
    B = list(RNG.choice(lowpool, size=min(40, len(lowpool)),
                        replace=False))              # low-kappa stratum
    iso = isozyme_pairs(dnf, viable_set)
    iso_idx = [(gene_ids.index(a), gene_ids.index(b)) for a, b in iso]
    print(f"panels: |A|={len(A)} |B|={len(B)} isozyme pairs={len(iso_idx)}")

    pairs = set()
    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            pairs.add((min(A[i], A[j]), max(A[i], A[j])))
    for i in range(len(B)):
        for j in range(i + 1, len(B)):
            pairs.add((min(B[i], B[j]), max(B[i], B[j])))
    # cross panel: 300 random A x B
    cross = []
    for _ in range(300):
        a = int(RNG.choice(A))
        b = int(RNG.choice(B))
        cross.append((min(a, b), max(a, b)))
    pairs.update(cross)
    pairs.update(iso_idx)
    targeted = []
    for n1, n2 in [("pgi", "zwf"), ("tktA", "tktB"), ("talA", "talB"),
                   ("ppc", "pps"), ("zwf", "gnd"), ("pfkA", "pfkB"),
                   ("rpe", "rpiA"), ("rpe", "rpiB"), ("tktA", "talA")]:
        g1, g2 = by_name.get(n1), by_name.get(n2)
        if g1 in viable_set and g2 in viable_set:
            targeted.append((gene_ids.index(g1), gene_ids.index(g2)))
    pairs.update(targeted)
    pairs = sorted(pairs)
    print(f"total pairs to solve: {len(pairs)}")

    # subsystems
    subs = {r.id: r.subsystem for r in model.reactions}

    rows = []
    t0 = time.time()
    for p, (i, j) in enumerate(pairs):
        g1, g2 = gene_ids[i], gene_ids[j]
        dis = disabled_for_pair(dnf, touched, g1, g2)
        idx = [eng.index[r] for r in dis]
        lb, ub = ko_bounds(eng, idx)
        out = eng.solve_lex(lb, ub, bi)
        if out is None:
            v_ij, mu_ij = None, np.nan
            kap_ij = np.nan
            m_ij = np.zeros(R, bool)
        else:
            v_ij, mu_ij, _ = out
            kap_ij, m_ij, _ = kappa_from(v_ij, v_wt)
        ki, kj = kappa_dr[i], kappa_dr[j]
        gi, gj = growth[i], growth[j]
        w_i, w_j = gi / mu_wt, gj / mu_wt
        eps = kap_ij - ki - kj if np.isfinite(kap_ij) else np.nan
        rho = ((kap_ij + EPS0) / (ki + kj + 2 * EPS0)
               if np.isfinite(kap_ij) else np.nan)
        w_ij = (mu_ij / mu_wt) if np.isfinite(mu_ij) else 0.0
        eps_g = w_ij - w_i * w_j
        SL = (np.isfinite(gi) and np.isfinite(gj) and
              (not np.isfinite(mu_ij) or mu_ij <= GROWTH_DEAD))
        # footprint Jaccards
        si, sj = dS[i].astype(bool), dS[j].astype(bool)
        ri_, rj_ = dR[i].astype(bool), dR[j].astype(bool)
        def jac(a, b):
            u = (a | b).sum()
            return float((a & b).sum() / u) if u else 0.0
        JS, JR = jac(si, sj), jac(ri_, rj_)
        inter = ri_ & rj_
        shared_sub = sorted({subs[eng.rxn_ids[x]] for x in np.where(inter)[0]}
                            )[:3] if inter.any() else []
        # masked (manuscript main def)
        mask_i = (mu_wt - gi) > TAU_MASK * mu_wt
        mask_j = (mu_wt - gj) > TAU_MASK * mu_wt
        mask_ij = (np.isfinite(mu_ij)
                   and (mu_wt - mu_ij) > TAU_MASK * mu_wt)
        kVi = ki if mask_i else 0.0
        kVj = kj if mask_j else 0.0
        kVij = kap_ij if mask_ij else (0.0 if np.isfinite(kap_ij) else np.nan)
        epsV = (kVij - kVi - kVj) if np.isfinite(kap_ij) else np.nan
        panel = []
        if i in A and j in A:
            panel.append("A")
        if i in B and j in B:
            panel.append("B")
        if (i, j) in iso_idx or (min(i, j), max(i, j)) in iso_idx:
            panel.append("ISO")
        if (i, j) in targeted:
            panel.append("TGT")
        if (i, j) in cross:
            panel.append("X")
        rows.append(dict(
            g1=g1, g2=g2, n1=gene_names.get(g1, ""), n2=gene_names.get(g2, ""),
            kappa_i=ki, kappa_j=kj, kappa_ij=kap_ij,
            eps_add=eps, rho=rho, eps_growth=eps_g,
            growth_i=gi, growth_j=gj, growth_ij=(mu_ij if np.isfinite(mu_ij)
                                                 else 0.0),
            J_support=JS, J_dR=JR, SL=bool(SL), panel="+".join(panel) or "X",
            kappaV_i=kVi, kappaV_j=kVj, kappaV_ij=kVij, eps_masked=epsV,
            n_dis_ij=len(dis),
            shared_subsystems=";".join(shared_sub)))
        if (p + 1) % 200 == 0:
            el = time.time() - t0
            print(f"  pairs {p + 1}/{len(pairs)} ({el:.0f}s, "
                  f"{el / (p + 1):.2f}s/pair)", flush=True)

    import csv
    cols = list(rows[0].keys())
    with open(os.path.join(OUT, "m3_pairs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    np.save(os.path.join(OUT, "m3_pairs_meta.npy"),
            np.array([{"A": A, "B": B, "iso": iso_idx,
                       "targeted": targeted, "n_pairs": len(pairs)},
                      ], dtype=object))
    print(f"pairs done in {time.time() - t0:.0f}s -> m3_pairs.csv "
          f"({len(rows)} rows)")


# ------------------------------------------------------------------ path
def part_path():
    model, eng, bi, dnf = build()
    z = load_singles(eng)
    gene_ids = [str(x) for x in z["gene_ids"]]
    gene_names = {g.id: g.name for g in model.genes}
    growth, kappa_dr = z["growth"], z["kappa_dr"]
    v_wt = np.load(os.path.join(OUT, "m1_wt_reference.npy"))
    touched = touched_map(dnf)
    import csv
    rows = list(csv.DictReader(open(os.path.join(OUT, "m3_pairs.csv"))))

    def tof(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return np.nan

    order = sorted(rows, key=lambda r: -abs(tof(r["eps_add"])))
    SL = [r for r in rows if r["SL"] == "True"]
    top = order[:80]
    rest = [r for r in rows if r not in top and r not in SL]
    rand = list(RNG.choice(rest, size=min(80, len(rest)), replace=False))
    subset = []
    seen = set()
    for r in top + SL + rand:
        key = (r["g1"], r["g2"])
        if key not in seen:
            seen.add(key)
            subset.append(r)
    print(f"path subset: {len(subset)} pairs "
          f"({len(top)} top-|eps| + {len(SL)} SL + {len(rand)} random)")

    moma_cache = {}

    def moma_ko(gid):
        if gid not in moma_cache:
            dis = disabled_reactions(dnf, [gid])
            idx = [eng.index[r] for r in dis]
            lb, ub = ko_bounds(eng, idx)
            moma_cache[gid] = eng.solve_moma(lb, ub, v_wt)
        return moma_cache[gid]

    def bounds_pair(g1, g2):
        dis = disabled_for_pair(dnf, touched, g1, g2)
        idx = [eng.index[r] for r in dis]
        return ko_bounds(eng, idx)

    def bounds_single(gid):
        dis = disabled_reactions(dnf, [gid])
        idx = [eng.index[r] for r in dis]
        return ko_bounds(eng, idx)

    out_rows = []
    t0 = time.time()
    for q, r in enumerate(subset):
        g1, g2 = r["g1"], r["g2"]
        s_i, s_j = moma_ko(g1), moma_ko(g2)
        if s_i is None or s_j is None:
            continue
        lb_ij, ub_ij = bounds_pair(g1, g2)
        s_ij_i = eng.solve_moma(lb_ij, ub_ij, s_i)   # i first
        s_ij_j = eng.solve_moma(lb_ij, ub_ij, s_j)   # j first
        if s_ij_i is None or s_ij_j is None:
            continue
        chi = float(np.abs(s_ij_i - s_ij_j).sum())   # commutator
        kap_ij_i = float(((s_ij_i - v_wt) ** 2).sum())
        kap_ij_j = float(((s_ij_j - v_wt) ** 2).sum())
        # closed loops: WT -> d_i -> d_ij -> d_j -> WT (i-first)
        lb_j, ub_j = bounds_single(g2)
        s3_i = eng.solve_moma(lb_j, ub_j, s_ij_i)
        lb_i, ub_i = bounds_single(g1)
        s3_j = eng.solve_moma(lb_i, ub_i, s_ij_j)
        if s3_i is None or s3_j is None:
            continue
        h_i = float(np.abs(s3_i - v_wt).sum())       # loop holonomy i-first
        h_j = float(np.abs(s3_j - v_wt).sum())       # loop holonomy j-first
        h_loop_diff = float(np.abs(s3_i - s3_j).sum())
        # MOMA single kappa for reference
        kap_i_moma = float(((s_i - v_wt) ** 2).sum())
        kap_j_moma = float(((s_j - v_wt) ** 2).sum())
        out_rows.append(dict(
            g1=g1, g2=g2, n1=gene_names.get(g1, ""), n2=gene_names.get(g2, ""),
            chi=chi, kappa_moma_i=kap_i_moma, kappa_moma_j=kap_j_moma,
            kappa_moma_ij_ifirst=kap_ij_i, kappa_moma_ij_jfirst=kap_ij_j,
            kappa_path_asymmetry=abs(kap_ij_i - kap_ij_j),
            h_loop_ifirst=h_i, h_loop_jfirst=h_j,
            h_loop_asym=h_loop_diff,
            eps_add=tof(r["eps_add"]), kappa_i=tof(r["kappa_i"]),
            kappa_j=tof(r["kappa_j"]), kappa_ij=tof(r["kappa_ij"]),
            SL=r["SL"], panel=r["panel"]))
        if (q + 1) % 40 == 0:
            el = time.time() - t0
            print(f"  path {q + 1}/{len(subset)} ({el:.0f}s, "
                  f"{el / (q + 1):.2f}s/pair)", flush=True)

    cols = list(out_rows[0].keys())
    with open(os.path.join(OUT, "m3_path.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)
    print(f"path done in {time.time() - t0:.0f}s -> m3_path.csv "
          f"({len(out_rows)} rows)")


# ----------------------------------------------------------------- stats
def part_stats():
    from scipy.stats import spearmanr, mannwhitneyu
    import csv
    z = np.load(os.path.join(OUT, "m3_singles.npz"), allow_pickle=True)
    gene_ids = [str(x) for x in z["gene_ids"]]
    growth, kappa_dr = z["growth"], z["kappa_dr"]
    mu_wt = float(z["mu_wt"])
    viable = np.isfinite(growth) & (growth > GROWTH_DEAD)
    summary = {"model": "iML1515", "n_genes": len(gene_ids),
               "mu_wt": mu_wt,
               "n_viable": int(viable.sum()),
               "n_infeasible": int((~np.isfinite(growth)).sum()),
               "n_nogrowth": int((growth <= GROWTH_DEAD).sum())}
    kv = kappa_dr[viable]
    summary["kappa_singles"] = {
        "median": float(np.median(kv)), "mean": float(np.mean(kv)),
        "q90": float(np.percentile(kv, 90)),
        "q99": float(np.percentile(kv, 99)),
        "max": float(np.max(kv)),
        "frac_zero": float(np.mean(kv < 1e-12)),
        "n_masked": int(np.sum((mu_wt - growth[viable])
                               > TAU_MASK * mu_wt))}

    if os.path.exists(os.path.join(OUT, "m3_pairs.csv")):
        rows = list(csv.DictReader(open(os.path.join(OUT, "m3_pairs.csv"))))

        def arr(col):
            return np.array([float(r[col]) if r[col] not in
                             ("", "nan", "None") else np.nan
                             for r in rows])
        eps, rho = arr("eps_add"), arr("rho")
        JS, JR = arr("J_support"), arr("J_dR")
        epsg = arr("eps_growth")
        kap_ij = arr("kappa_ij")
        SL = np.array([r["SL"] == "True" for r in rows])
        iso = np.array(["ISO" in r["panel"] for r in rows])
        finite = np.isfinite(eps)
        summary["pairs"] = {
            "n_pairs": len(rows),
            "n_SL": int(SL.sum()),
            "n_SL_isozyme": int((SL & iso).sum()),
            "eps_median": float(np.nanmedian(eps)),
            "eps_q05": float(np.nanpercentile(eps, 5)),
            "eps_q95": float(np.nanpercentile(eps, 95)),
            "frac_superadditive": float(np.nanmean(eps > 0)),
            "frac_large_interaction": float(
                np.nanmean(np.abs(eps[finite])
                           > 0.1 * np.nanmedian(kap_ij[finite]))),
            "rho_median": float(np.nanmedian(rho)),
            "eps_masked_emergence": int(np.sum(
                np.isfinite(arr("eps_masked"))
                & (arr("kappaV_i") < 1e-12)
                & (arr("kappaV_j") < 1e-12)
                & (arr("kappaV_ij") > 1e-12))),
        }
        # correlations with footprint overlap
        for lab, X, Y in [("spearman_|eps|_J_support", np.abs(eps), JS),
                          ("spearman_|eps|_J_dR", np.abs(eps), JR),
                          ("spearman_eps_growth_vs_eps", epsg, eps),
                          ("spearman_rho_J_dR", rho, JR)]:
            m = np.isfinite(X) & np.isfinite(Y)
            if m.sum() > 10:
                rho_s, p = spearmanr(X[m], Y[m])
                summary["pairs"][lab] = {"rho": float(rho_s), "p": float(p)}
        # strata: iso vs non-iso
        for lab, msk in [("iso", iso & ~SL), ("noniso", ~iso & ~SL),
                         ("SL", SL)]:
            e = eps[msk & finite]
            if e.size:
                summary["pairs"][f"eps_{lab}"] = {
                    "n": int(e.size),
                    "median": float(np.median(e)),
                    "q95": float(np.percentile(e, 95)) if e.size > 3
                    else None}
        # overlap high/low contrast
        medJ = np.nanmedian(JS)
        hi = JS > medJ
        lo = ~hi
        e_hi, e_lo = np.abs(eps[hi & finite]), np.abs(eps[lo & finite])
        if e_hi.size > 5 and e_lo.size > 5:
            u, p = mannwhitneyu(e_hi, e_lo, alternative="greater")
            summary["pairs"]["MWU_hilowJ"] = {
                "medianJS": float(medJ), "p": float(p),
                "median_hi": float(np.median(e_hi)),
                "median_lo": float(np.median(e_lo))}
        # top epistasis table + SL table
        order = np.argsort(-np.nan_to_num(np.abs(eps), nan=0.0))
        summary["pairs"]["top_eps"] = [
            {"genes": f'{rows[i]["n1"]}({rows[i]["g1"]}) + '
                      f'{rows[i]["n2"]}({rows[i]["g2"]})',
             "panel": rows[i]["panel"], "eps": float(eps[i]),
             "kappa_i": float(rows[i]["kappa_i"]),
             "kappa_j": float(rows[i]["kappa_j"]),
             "kappa_ij": float(rows[i]["kappa_ij"]),
             "growth_ij": float(rows[i]["growth_ij"]),
             "J_dR": float(JR[i])} for i in order[:15]]
        sl_rows = [i for i in np.where(SL)[0]]
        summary["pairs"]["SL_table"] = [
            {"genes": f'{rows[i]["n1"]}({rows[i]["g1"]}) + '
                      f'{rows[i]["n2"]}({rows[i]["g2"]})',
             "panel": rows[i]["panel"],
             "kappa_i": float(rows[i]["kappa_i"]),
             "kappa_j": float(rows[i]["kappa_j"]),
             "growth_i": float(rows[i]["growth_i"]),
             "growth_j": float(rows[i]["growth_j"]),
             "J_dR": float(JR[i])} for i in sl_rows[:40]]

    if os.path.exists(os.path.join(OUT, "m3_path.csv")):
        rows = list(csv.DictReader(open(os.path.join(OUT, "m3_path.csv"))))

        def arr(col):
            return np.array([float(r[col]) for r in rows])
        chi = arr("chi")
        hA, hB = arr("h_loop_ifirst"), arr("h_loop_jfirst")
        hasym = arr("h_loop_asym")
        kpAs = arr("kappa_path_asymmetry")
        eps = arr("eps_add")
        kij = arr("kappa_ij")
        summary["path"] = {
            "n_pairs": len(rows),
            "frac_chi_positive": float(np.mean(chi > 1e-9)),
            "chi_median": float(np.median(chi)),
            "chi_max": float(chi.max()),
            "frac_kappa_path_asymmetric": float(np.mean(kpAs > 1e-9)),
            "kappa_path_asym_median": float(np.median(kpAs)),
            "frac_loop_holonomy_nonzero": float(np.mean(hA > 1e-9)),
            "h_loop_median": float(np.median(hA)),
            "h_loop_asym_median": float(np.median(hasym)),
            "h_loop_asym_max": float(hasym.max()),
        }
        for lab, X, Y in [("spearman_chi_vs_|eps|", chi, np.abs(eps)),
                          ("spearman_chi_vs_kappa_ij", chi, kij),
                          ("spearman_hasym_vs_|eps|", hasym,
                           np.abs(eps))]:
            m = np.isfinite(X) & np.isfinite(Y)
            if m.sum() > 10:
                rho_s, p = spearmanr(X[m], Y[m])
                summary["path"][lab] = {"rho": float(rho_s), "p": float(p)}
        # SL-stratified path stats (isozyme SL pairs have no-op singles,
        # so chi is trivially zero there; non-commutativity lives in the
        # distinct-footprint pairs)
        SLm = np.array([r["SL"] == "True" for r in rows])
        if (~SLm).sum() > 10:
            rho_s, p = spearmanr(chi[~SLm], np.abs(eps)[~SLm])
            summary["path"]["spearman_chi_vs_|eps|_nonSL"] = {
                "rho": float(rho_s), "p": float(p), "n": int((~SLm).sum())}
        summary["path"]["SL_strata"] = {
            "SL": {"n": int(SLm.sum()),
                   "frac_chi_positive": float(np.mean(chi[SLm] > 1e-9))
                   if SLm.sum() else None,
                   "h_loop_median": float(np.median(hA[SLm]))
                   if SLm.sum() else None},
            "nonSL": {"n": int((~SLm).sum()),
                      "frac_chi_positive": float(
                          np.mean(chi[~SLm] > 1e-9)),
                      "h_loop_median": float(np.median(hA[~SLm])),
                      "chi_median": float(np.median(chi[~SLm])),
                      "chi_q90": float(np.percentile(chi[~SLm], 90))},
        }

    with open(os.path.join(OUT, "m3_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1)[:4000])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True,
                    choices=["singles", "pairs", "path", "stats"])
    args = ap.parse_args()
    t0 = time.time()
    {"singles": part_singles, "pairs": part_pairs,
     "path": part_path, "stats": part_stats}[args.part]()
    print(f"part {args.part} total {time.time() - t0:.0f}s")
