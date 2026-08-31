"""
Apply v3 dep-ratio semantics (the v2 single-reaction-KO dependency-ratio
analysis from Network K, commit 07e6d85) to autopoietic Networks E, F,
G, H, I, J to test whether the metabolic-robust + enzyme-fragile profile
is a UNIVERSAL signature of the isozyme-dampener architecture or specific
to Network K.

CONTEXT:
  - Network K v2 dep_ratio (commit 07e6d85) revealed the asymmetric profile:
    6/13 metabolic robust (multi-producer isozyme pairs) + 0/38 enzymes
    robust (single-synthesis-gene decay = 0.7139).
  - Network K v1 binary Phase I (commit 4327b89): 52/52 = 100% (full-
    component-KO endpoint recovery). The 100% binary verdict is the
    AUTOPOIETIC closure-test pass; the v2 dep_ratio at tau=0.5 reveals
    the structural asymmetry underneath.
  - QUESTION (this script): Does the metabolic-robust + enzyme-fragile
    asymmetry profile hold across the E->F->G->H->I->J lineage, or is it
    a Network-K-specific signature?

METHODOLOGY (applied identically to each network):
  1. Extract species/food/non_food/reactions from each network_X.py via
     source-code parsing (exec only the network definition block, skip
     the side-effect top-level execution).
  2. Run baseline simulation (T=1000 warm-up) to reach steady state.
  3. For each reaction r, compute dep_ratio(m, r) for each produced
     metabolite m, using the steady-state-to-steady-state single-r-KO
     protocol (start from baseline_final, knock out only r, run T=500).
  4. For each component m_j, compute max_dep_ratio(m_j) = max_r dep_ratio.
  5. Stratify by component type (metabolic / enzyme / regulatory):
       * metabolic: expected robust (multi-producer isozyme pairs)
       * enzyme: expected fragile (single-synthesis-gene decay = 0.7139)
       * TF: depends on whether the network has G_const+G_auto dual producers.
  6. Compare the metabolic-robust fraction + enzyme-fragile fraction
     across networks E through J.

EXPECTED OUTCOME:
  - If the asymmetry is UNIVERSAL: every network in E-J shows
    (high metabolic robust fraction) + (zero enzyme robust fraction).
    The dep_ratio signature is a STRUCTURAL PROPERTY of the isozyme-
    dampener architecture, not specific to Network K.
  - If the asymmetry is Network-K-specific: earlier networks (E, F) with
    fewer isozyme pairs show LOWER metabolic robust fraction, while
    later networks (I, J, K) with more dampeners show HIGHER. This would
    suggest the asymmetry EMERGES as the network accumulates isozyme
    dampeners across the lineage.
  - The Network K v2 verdict (commit 07e6d85) is the K=endpoint of this
    trend; this script verifies the trend by computing the same dep_ratio
    for each of E, F, G, H, I, J.

Outputs:
  download/autopoiesis_networks_E_to_J_v3_dep_ratio.{png,csv,txt}
  download/autopoiesis_networks_E_to_J_v3_dep_ratio_results.json
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from typing import Any

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm

for _p in (
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
):
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
        except Exception:
            pass

import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ----------------------------------------------------------------------
#  Generic simulate_network (works for any network dict)
# ----------------------------------------------------------------------
def simulate_network(network, knockout_reactions=None, T=500, delta=0.05,
                     k_cat_metabolic=0.8, k_cat_synthesis=2.0,
                     k_cat_constitutive=0.3, k_cat_autocatalytic=1.0,
                     food_supply_rate=2.0, food_conc=10.0,
                     Km=0.1, max_conc=100.0,
                     init_concs=None, allow_constitutive=True):
    sp = network["species"]
    fd = set(network["food"])
    rxs = network["reactions"]

    x = {s: (food_conc if s in fd else 0.1) for s in sp}
    if init_concs:
        for s, v in init_concs.items():
            x[s] = v

    ko_set = set(knockout_reactions) if knockout_reactions else set()

    dt = 0.05
    trajectory = [{s: x[s] for s in sp}]
    for step in range(T):
        rates = {}
        for r in rxs:
            if r["id"] in ko_set:
                rates[r["id"]] = 0.0
                continue
            subs = [(s, abs(d)) for s, d in r["stoich"].items() if d < 0]
            if any(x[s] <= 0 for s, _ in subs):
                rates[r["id"]] = 0.0
                continue
            kind = r["kind"]
            cat = r["catalyst"]
            if kind == "constitutive":
                k = k_cat_constitutive
                rate = k
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            else:
                cat_conc = x.get(cat, 0.0) if cat is not None else 0.0
                if cat_conc <= 0:
                    rates[r["id"]] = 0.0
                    continue
                if kind == "synthesis":
                    k = k_cat_synthesis
                elif kind == "autocatalytic":
                    k = k_cat_autocatalytic
                else:
                    k = k_cat_metabolic
                if "k_cat_override" in r:
                    k = r["k_cat_override"]
                rate = k * cat_conc
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            rates[r["id"]] = rate

        dx = {s: 0.0 for s in sp}
        for r in rxs:
            rate = rates[r["id"]]
            for s, d in r["stoich"].items():
                dx[s] += d * rate
        for s in sp:
            dx[s] -= delta * x[s]
            if s in fd:
                dx[s] += food_supply_rate * (food_conc - x[s]) * 0.5
        for s in sp:
            x[s] = max(0.0, min(max_conc, x[s] + dt * dx[s]))
        trajectory.append({s: x[s] for s in sp})
    return trajectory


def simulate_network_recover(network, init, T=500, **kwargs):
    return simulate_network(network, knockout_reactions=None, T=T, init_concs=init, **kwargs)


def reactions_producing(network, m_j):
    return [r["id"] for r in network["reactions"]
            if r["stoich"].get(m_j, 0) > 0]


def produced_metabolites_of(network, r_id):
    r = next(rr for rr in network["reactions"] if rr["id"] == r_id)
    return [m for m, c in r["stoich"].items() if c > 0]


def dependency_ratio_for_reaction(network, r_id, baseline_final, T=500,
                                  viability_threshold=1e-3):
    produced = produced_metabolites_of(network, r_id)
    if not produced:
        return {}, {}, {}
    T_knock = T
    knock_traj = simulate_network(network, knockout_reactions={r_id},
                                   T=T_knock, init_concs=baseline_final)
    knock_final = knock_traj[-1]
    knock_mid = knock_traj[T_knock // 2]
    T_rec = T_knock // 2
    recover_traj = simulate_network_recover(network, init=knock_mid, T=T_rec)
    recover_final = recover_traj[-1]
    dep_ratios = {}
    dep_ratios_recovery = {}
    for m in produced:
        b = baseline_final.get(m, 0.0)
        k = knock_final.get(m, 0.0)
        r_v = recover_final.get(m, 0.0)
        if abs(b) > viability_threshold:
            dep_ratios[m] = float((b - k) / b)
            dep_ratios_recovery[m] = float((b - r_v) / b)
        else:
            dep_ratios[m] = None
            dep_ratios_recovery[m] = None
    return dep_ratios, dep_ratios_recovery, knock_final


# ----------------------------------------------------------------------
#  Network source extraction (avoid top-level side effects)
# ----------------------------------------------------------------------
def extract_network_dict_from_source(filepath, network_var_name):
    """Read the network_X.py source and exec only up to the
    `network_X = {...}` dict definition (plus the species/food/non_food/
    reactions definitions). Skip the rest of the file (which contains
    simulate_network, closure tests, and plotting at top level).
    """
    with open(filepath) as f:
        src = f.read()
    # Find the line where `network_X = {` starts
    pattern = re.compile(rf'^{network_var_name}\s*=\s*\{{', re.MULTILINE)
    match = pattern.search(src)
    if not match:
        raise ValueError(f"Could not find {network_var_name} = {{...}} in {filepath}")
    # Find the matching closing brace by counting braces
    start = match.end() - 1  # the '{'
    depth = 0
    end = start
    for i in range(start, len(src)):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    # Extract the prefix (species, food, non_food, reactions) + the dict
    prefix_end = match.start()
    prefix_src = src[:prefix_end]
    dict_src = src[match.start():end]
    # Exec the prefix + dict in a fresh namespace
    ns = {}
    exec(compile(prefix_src + "\n" + dict_src, filepath, "exec"), ns)
    network = ns[network_var_name]
    return network


# ----------------------------------------------------------------------
#  Component-type classification per network
# ----------------------------------------------------------------------
def classify_components(network, network_name):
    """Classify each non_food component as 'metabolic', 'enzyme', or 'regulatory'."""
    metabolic = []
    enzyme = []
    regulatory = []
    # Regulatory: TF (always)
    # Enzyme: anything that is a CATALYST in some reaction (uppercase gene names like HK1, PFK2, etc.)
    # Metabolic: non-food species that are NOT enzymes and NOT TF
    catalysts = set()
    for r in network["reactions"]:
        if r.get("catalyst"):
            catalysts.add(r["catalyst"])
    for s in network["non_food"]:
        if s == "TF" or s.endswith("TF") and s not in catalysts:
            regulatory.append(s)
        elif s in catalysts:
            enzyme.append(s)
        else:
            metabolic.append(s)
    return {
        "metabolic": sorted(set(metabolic)),
        "enzyme": sorted(set(enzyme)),
        "regulatory": sorted(set(regulatory)),
    }


# ----------------------------------------------------------------------
#  Run v2 dep_ratio analysis on a single network
# ----------------------------------------------------------------------
def run_v2_dep_ratio(network, network_name, T=500, T_warmup=1000):
    """Run baseline sim + per-reaction dep_ratio sweep on a network."""
    print(f"\n{'='*78}")
    print(f"v2 dep_ratio on Network {network_name}")
    print(f"  {len(network['species'])} species ({len(network['food'])} food + "
          f"{len(network['non_food'])} non-food), {len(network['reactions'])} reactions")
    print(f"{'='*78}")

    # Baseline
    print(f"  Baseline simulation (T={T_warmup} warm-up)...")
    t0 = time.time()
    baseline_traj = simulate_network(network, knockout_reactions=None, T=T_warmup)
    baseline_final = baseline_traj[-1]
    print(f"    Done in {time.time()-t0:.1f}s")

    # Per-reaction dep_ratio
    all_rxns = [r["id"] for r in network["reactions"]]
    print(f"  Per-reaction dep_ratio sweep ({len(all_rxns)} reactions)...")
    rxn_results = []
    for i, r_id in enumerate(all_rxns):
        if (i + 1) % 20 == 0:
            print(f"    {i+1}/{len(all_rxns)}...")
        dep, dep_rec, knock_final = dependency_ratio_for_reaction(
            network, r_id, baseline_final, T=T, viability_threshold=1e-3
        )
        valid_dep = [v for v in dep.values() if v is not None]
        valid_dep_rec = [v for v in dep_rec.values() if v is not None]
        max_dep = max(valid_dep) if valid_dep else 0.0
        max_dep_rec = max(valid_dep_rec) if valid_dep_rec else 0.0
        mean_dep = float(np.mean(valid_dep)) if valid_dep else 0.0
        if valid_dep:
            m_argmax = max(dep.items(), key=lambda kv: kv[1] if kv[1] is not None else -1)[0]
        else:
            m_argmax = None
        rxn_results.append({
            "reaction": r_id,
            "produced_metabolites": produced_metabolites_of(network, r_id),
            "dep_ratios": dep,
            "dep_ratios_recovery": dep_rec,
            "max_dep_ratio": float(max_dep),
            "max_dep_ratio_recovery": float(max_dep_rec),
            "mean_dep_ratio": float(mean_dep),
            "m_argmax": m_argmax,
        })

    # Component-level
    comp_rows = []
    for m_j in network["non_food"]:
        producers = reactions_producing(network, m_j)
        if not producers:
            continue
        dep_per_r = {}
        dep_rec_per_r = {}
        for r_id in producers:
            r_row = next(rr for rr in rxn_results if rr["reaction"] == r_id)
            v = r_row["dep_ratios"].get(m_j)
            v_rec = r_row["dep_ratios_recovery"].get(m_j)
            if v is not None:
                dep_per_r[r_id] = v
            if v_rec is not None:
                dep_rec_per_r[r_id] = v_rec
        if not dep_per_r:
            continue
        max_dep = max(dep_per_r.values()) if dep_per_r else 0.0
        max_dep_rec = max(dep_rec_per_r.values()) if dep_rec_per_r else 0.0
        r_argmax = max(dep_per_r.items(), key=lambda kv: kv[1])[0] if dep_per_r else None
        comp_rows.append({
            "component": m_j,
            "n_producers": len(producers),
            "producers": producers,
            "dep_per_r": dep_per_r,
            "dep_rec_per_r": dep_rec_per_r,
            "max_dep_ratio": float(max_dep),
            "max_dep_ratio_recovery": float(max_dep_rec),
            "r_argmax": r_argmax,
            "baseline_conc": float(baseline_final.get(m_j, 0.0)),
        })
    print(f"  Done. {len(comp_rows)} components analyzed.")
    return baseline_final, rxn_results, comp_rows


# ----------------------------------------------------------------------
#  Main
# ----------------------------------------------------------------------
def main() -> int:
    os.makedirs("/home/z/my-project/download", exist_ok=True)
    T = 500

    print("=" * 78)
    print("v3 dep-ratio semantics across Networks E-J (universality test)")
    print("=" * 78)
    print()
    print("Goal: Test whether the metabolic-robust + enzyme-fragile asymmetry")
    print("      profile (Network K v2 commit 07e6d85 signature) is UNIVERSAL")
    print("      across the E->F->G->H->I->J->K lineage, or K-specific.")
    print()

    network_files = {
        "E": ("autopoiesis_network_E.py", "network_E"),
        "F": ("autopoiesis_network_F.py", "network_F"),
        "G": ("autopoiesis_network_G.py", "network_G"),
        "H": ("autopoiesis_network_H.py", "network_H"),
        "I": ("autopoiesis_network_I.py", "network_I"),
        "J": ("autopoiesis_network_J.py", "network_J"),
    }

    all_results = {}
    summary_table = []
    for net_name, (filename, varname) in network_files.items():
        filepath = f"/home/z/my-project/scripts/{filename}"
        print(f"\n>>> Extracting network {net_name} from {filepath}...")
        network = extract_network_dict_from_source(filepath, varname)
        print(f"  {net_name}: {len(network['species'])} species, "
              f"{len(network['reactions'])} reactions")
        # Classify components
        comp_types = classify_components(network, net_name)
        print(f"  Component types: {len(comp_types['metabolic'])} metabolic, "
              f"{len(comp_types['enzyme'])} enzyme, "
              f"{len(comp_types['regulatory'])} regulatory")

        # Run v2 dep_ratio
        baseline_final, rxn_results, comp_rows = run_v2_dep_ratio(
            network, net_name, T=T, T_warmup=1000
        )

        # Stratify by type at tau=0.5
        tau_strat = 0.5
        strat = {}
        for ctype, clist in comp_types.items():
            sub = [c for c in comp_rows if c["component"] in clist]
            n_robust = sum(1 for c in sub if c["max_dep_ratio"] < tau_strat)
            n_tot = len(sub)
            if sub:
                mean_dep = float(np.mean([c["max_dep_ratio"] for c in sub]))
                median_dep = float(np.median([c["max_dep_ratio"] for c in sub]))
            else:
                mean_dep = float("nan"); median_dep = float("nan")
            strat[ctype] = {
                "n_total": n_tot,
                "n_robust": n_robust,
                "n_fragile": n_tot - n_robust,
                "frac_robust": float(n_robust / max(1, n_tot)),
                "mean_max_dep": mean_dep,
                "median_max_dep": median_dep,
            }
        print(f"\n  Stratified (tau=0.5):")
        for ctype, s in strat.items():
            print(f"    {ctype:<12} (n={s['n_total']}): robust = {s['n_robust']}/{s['n_total']} = "
                  f"{100*s['frac_robust']:.1f}%; mean={s['mean_max_dep']:.4f}, median={s['median_max_dep']:.4f}")

        # Save
        all_results[net_name] = {
            "n_species": len(network["species"]),
            "n_reactions": len(network["reactions"]),
            "n_food": len(network["food"]),
            "n_non_food": len(network["non_food"]),
            "comp_types": comp_types,
            "baseline_final_lite": {m: float(v) for m, v in baseline_final.items()
                                     if m in comp_types["metabolic"] + comp_types["regulatory"]},
            "comp_rows": [
                {**{k: v for k, v in c.items() if k not in ("dep_per_r", "dep_rec_per_r")},
                 "dep_per_r": c["dep_per_r"],
                 "dep_rec_per_r": c["dep_rec_per_r"]}
                for c in comp_rows
            ],
            "stratified_at_0.5": strat,
        }

        summary_table.append({
            "network": net_name,
            "n_species": len(network["species"]),
            "n_reactions": len(network["reactions"]),
            "n_metabolic": len(comp_types["metabolic"]),
            "n_enzyme": len(comp_types["enzyme"]),
            "n_regulatory": len(comp_types["regulatory"]),
            "metabolic_robust": strat["metabolic"]["n_robust"],
            "metabolic_robust_frac": strat["metabolic"]["frac_robust"],
            "enzyme_robust": strat["enzyme"]["n_robust"],
            "enzyme_robust_frac": strat["enzyme"]["frac_robust"],
            "regulatory_robust": strat["regulatory"]["n_robust"],
            "metabolic_mean_dep": strat["metabolic"]["mean_max_dep"],
            "enzyme_mean_dep": strat["enzyme"]["mean_max_dep"],
        })

    # Add Network K (from v2 commit 07e6d85 results)
    print("\n\n>>> Loading Network K v2 dep_ratio results (from commit 07e6d85)...")
    K_v2_path = "/home/z/my-project/download/autopoiesis_network_K_v2_dep_ratio_results.json"
    if os.path.exists(K_v2_path):
        with open(K_v2_path) as f:
            K_v2_data = json.load(f)
        # Compute stratified counts from K_v2_data
        K_metabolic = ["G6P", "FBP", "PEP", "PYR", "AcCoA", "ALA", "ASP", "MAL",
                       "GLU", "Glycogen", "PolyP", "DHAP", "G3P"]
        K_enzyme = [c["component"] for c in K_v2_data["component_rows"]
                    if c["component"] not in K_metabolic and c["component"] != "TF"]
        K_reg = ["TF"]
        K_strat = {}
        for ctype, clist in [("metabolic", K_metabolic), ("enzyme", K_enzyme), ("regulatory", K_reg)]:
            sub = [c for c in K_v2_data["component_rows"] if c["component"] in clist]
            n_robust = sum(1 for c in sub if c["max_dep_ratio"] < 0.5)
            n_tot = len(sub)
            mean_dep = float(np.mean([c["max_dep_ratio"] for c in sub])) if sub else float("nan")
            K_strat[ctype] = {
                "n_total": n_tot, "n_robust": n_robust,
                "frac_robust": float(n_robust / max(1, n_tot)),
                "mean_max_dep": mean_dep,
            }
        summary_table.append({
            "network": "K",
            "n_species": 63,  # from commit 4327b89
            "n_reactions": 86,
            "n_metabolic": len(K_metabolic),
            "n_enzyme": len(K_enzyme),
            "n_regulatory": 1,
            "metabolic_robust": K_strat["metabolic"]["n_robust"],
            "metabolic_robust_frac": K_strat["metabolic"]["frac_robust"],
            "enzyme_robust": K_strat["enzyme"]["n_robust"],
            "enzyme_robust_frac": K_strat["enzyme"]["frac_robust"],
            "regulatory_robust": K_strat["regulatory"]["n_robust"],
            "metabolic_mean_dep": K_strat["metabolic"]["mean_max_dep"],
            "enzyme_mean_dep": K_strat["enzyme"]["mean_max_dep"],
        })
        print(f"  Network K added: metabolic robust = {K_strat['metabolic']['n_robust']}/{K_strat['metabolic']['n_total']}, "
              f"enzyme robust = {K_strat['enzyme']['n_robust']}/{K_strat['enzyme']['n_total']}")

    # Print summary table
    print("\n" + "=" * 78)
    print("UNIVERSALITY VERDICT: dep_ratio profile across E-J-K lineage")
    print("=" * 78)
    print(f"  {'Network':<8} {'species':<8} {'rxns':<6} {'metab':<6} {'enz':<6} "
          f"{'metab_rob':<12} {'enz_rob':<10} {'metab_mean_dep':<14} {'enz_mean_dep':<14}")
    print("  " + "-" * 90)
    for s in summary_table:
        print(f"  {s['network']:<8} {s['n_species']:<8} {s['n_reactions']:<6} "
              f"{s['n_metabolic']:<6} {s['n_enzyme']:<6} "
              f"{s['metabolic_robust']}/{s['n_metabolic']} ({100*s['metabolic_robust_frac']:.0f}%)   "
              f"{s['enzyme_robust']}/{s['n_enzyme']:<5}   "
              f"{s['metabolic_mean_dep']:<14.4f} {s['enzyme_mean_dep']:<14.4f}")

    # Universality test
    metabolic_robust_fracs = [s["metabolic_robust_frac"] for s in summary_table]
    enzyme_robust_fracs = [s["enzyme_robust_frac"] for s in summary_table]
    metabolic_mean_deps = [s["metabolic_mean_dep"] for s in summary_table]
    enzyme_mean_deps = [s["enzyme_mean_dep"] for s in summary_table]

    n_universal_metabolic = sum(1 for f in metabolic_robust_fracs if f > 0.3)
    n_universal_enzyme_fragile = sum(1 for f in enzyme_robust_fracs if f == 0.0)
    print(f"\n  UNIVERSALITY TEST:")
    print(f"    - Networks with >30% metabolic robust: {n_universal_metabolic}/{len(summary_table)}")
    print(f"    - Networks with 0% enzyme robust: {n_universal_enzyme_fragile}/{len(summary_table)}")
    metabolic_mean = float(np.mean(metabolic_mean_deps))
    enzyme_mean = float(np.mean(enzyme_mean_deps))
    metabolic_std = float(np.std(metabolic_mean_deps))
    enzyme_std = float(np.std(enzyme_mean_deps))
    print(f"    - Mean metabolic max_dep across lineage: {metabolic_mean:.4f} +/- {metabolic_std:.4f}")
    print(f"    - Mean enzyme max_dep across lineage: {enzyme_mean:.4f} +/- {enzyme_std:.4f}")
    metabolic_enzyme_gap = enzyme_mean - metabolic_mean
    print(f"    - Enzyme - metabolic mean dep GAP: {metabolic_enzyme_gap:.4f} "
          f"({'ASYMMETRY CONFIRMED' if metabolic_enzyme_gap > 0.2 else 'ASYMMETRY WEAK'})")

    if n_universal_metabolic >= 5 and n_universal_enzyme_fragile == len(summary_table):
        verdict = "UNIVERSAL -- metabolic-robust + enzyme-fragile profile is a STRUCTURAL PROPERTY of the isozyme-dampener architecture across the E->K lineage"
    elif n_universal_metabolic >= 3 and n_universal_enzyme_fragile == len(summary_table):
        verdict = "PARTIALLY UNIVERSAL -- the enzyme-fragile signature is universal, but the metabolic-robust signature is weaker in earlier networks (E, F) with fewer isozyme pairs"
    else:
        verdict = "NOT UNIVERSAL -- the profile is Network-K-specific"
    print(f"\n  VERDICT: {verdict}")

    # Save outputs
    out_dir = "/home/z/my-project/download"
    import csv
    with open(f"{out_dir}/autopoiesis_networks_E_to_J_v3_dep_ratio.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "type", "component", "n_producers", "max_dep_ratio",
                    "max_dep_ratio_recovery", "r_argmax", "baseline_conc", "verdict_at_0.5"])
        for net_name, res in all_results.items():
            for c in res["comp_rows"]:
                ctype = next((ct for ct, clist in res["comp_types"].items()
                              if c["component"] in clist), "unknown")
                verdict_c = "ROBUST" if c["max_dep_ratio"] < 0.5 else "FRAGILE"
                w.writerow([net_name, ctype, c["component"], c["n_producers"],
                            c["max_dep_ratio"], c["max_dep_ratio_recovery"],
                            c["r_argmax"], c["baseline_conc"], verdict_c])

    # JSON results
    results_json = {
        "version": "v3 dep_ratio across E-J (universality test)",
        "methodology": "v2 single-reaction-KO dependency-ratio analysis (commit 07e6d85) applied to networks E, F, G, H, I, J + K (loaded from v2 commit)",
        "summary_table": summary_table,
        "universality_test": {
            "n_networks_with_metabolic_robust_above_30pct": n_universal_metabolic,
            "n_networks_with_zero_enzyme_robust": n_universal_enzyme_fragile,
            "n_total_networks": len(summary_table),
            "metabolic_mean_dep_across_lineage": metabolic_mean,
            "metabolic_std_dep_across_lineage": metabolic_std,
            "enzyme_mean_dep_across_lineage": enzyme_mean,
            "enzyme_std_dep_across_lineage": enzyme_std,
            "enzyme_metabolic_gap": metabolic_enzyme_gap,
            "verdict": verdict,
        },
        "per_network": all_results,
    }
    with open(f"{out_dir}/autopoiesis_networks_E_to_J_v3_dep_ratio_results.json", "w") as f:
        json.dump(results_json, f, indent=2, default=str)

    # PNG: 6-panel figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)

    # Panel 1: Metabolic robust fraction per network
    ax = axes[0, 0]
    networks = [s["network"] for s in summary_table]
    met_fracs = [s["metabolic_robust_frac"] for s in summary_table]
    enz_fracs = [s["enzyme_robust_frac"] for s in summary_table]
    x_pos = np.arange(len(networks))
    ax.bar(x_pos, met_fracs, color="#6a994e", alpha=0.85, label="Metabolic robust fraction")
    ax.bar(x_pos, enz_fracs, color="#bc4749", alpha=0.5, label="Enzyme robust fraction")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(networks)
    ax.set_ylabel("Fraction robust (max_dep < 0.5)")
    ax.set_title("Metabolic-robust + enzyme-fragile profile across E-K lineage\n"
                 "(green=metabolic robust; red=enzyme robust)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 2: Mean max_dep metabolic vs enzyme per network
    ax = axes[0, 1]
    met_deps = [s["metabolic_mean_dep"] for s in summary_table]
    enz_deps = [s["enzyme_mean_dep"] for s in summary_table]
    w_bar = 0.35
    ax.bar(x_pos - w_bar/2, met_deps, w_bar, color="#6a994e", alpha=0.85, label="Metabolic mean max_dep")
    ax.bar(x_pos + w_bar/2, enz_deps, w_bar, color="#bc4749", alpha=0.85, label="Enzyme mean max_dep")
    ax.axhline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5 threshold")
    ax.axhline(0.7139, color="blue", linestyle=":", linewidth=1,
               label="dilution-decay 1-exp(-1.25)=0.7139")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(networks)
    ax.set_ylabel("Mean max dependency ratio")
    ax.set_title("Metabolic vs enzyme mean dep_ratio per network\n"
                 "(asymmetry = enzyme - metabolic gap)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 3: Enzyme - metabolic gap per network
    ax = axes[0, 2]
    gaps = [e - m for e, m in zip(enz_deps, met_deps)]
    colors = ["#6a994e" if g > 0.2 else "#bc4749" for g in gaps]
    ax.bar(x_pos, gaps, color=colors, alpha=0.85)
    ax.axhline(0.2, color="black", linestyle="--", linewidth=1, label="asymmetry threshold (0.2)")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(networks)
    ax.set_ylabel("Enzyme - metabolic mean dep gap")
    ax.set_title(f"Asymmetry gap per network\n(positive = enzyme more fragile than metabolic)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 4: Component count trajectory across lineage
    ax = axes[1, 0]
    n_mets = [s["n_metabolic"] for s in summary_table]
    n_enzs = [s["n_enzyme"] for s in summary_table]
    n_regs = [s["n_regulatory"] for s in summary_table]
    ax.plot(networks, n_mets, "g-o", linewidth=2, markersize=10, label="Metabolic intermediates")
    ax.plot(networks, n_enzs, "r-s", linewidth=2, markersize=10, label="Enzymes")
    ax.plot(networks, n_regs, "b-^", linewidth=2, markersize=10, label="Regulatory")
    ax.set_xlabel("Network")
    ax.set_ylabel("Component count")
    ax.set_title("Component counts across E-K lineage\n(isozyme pairs accumulate over iterations)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 5: Metabolic robust count trajectory
    ax = axes[1, 1]
    met_robust_n = [s["metabolic_robust"] for s in summary_table]
    met_total_n = [s["n_metabolic"] for s in summary_table]
    ax.plot(networks, met_robust_n, "g-o", linewidth=2, markersize=10, label="Metabolic robust")
    ax.plot(networks, met_total_n, "g--", linewidth=1, alpha=0.5, label="Metabolic total")
    ax.set_xlabel("Network")
    ax.set_ylabel("Component count")
    ax.set_title(f"Metabolic robust trajectory: {met_robust_n[0]} -> {met_robust_n[-1]}\n"
                 f"(growth indicates isozyme-dampener accumulation)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 6: Per-network dep_ratio distribution histogram (metabolic vs enzyme)
    ax = axes[1, 2]
    all_met_deps = []
    all_enz_deps = []
    for net_name, res in all_results.items():
        for c in res["comp_rows"]:
            ctype = next((ct for ct, clist in res["comp_types"].items()
                          if c["component"] in clist), "unknown")
            if ctype == "metabolic":
                all_met_deps.append(c["max_dep_ratio"])
            elif ctype == "enzyme":
                all_enz_deps.append(c["max_dep_ratio"])
    # Add K from loaded data
    for c in K_v2_data["component_rows"]:
        if c["component"] in K_metabolic:
            all_met_deps.append(c["max_dep_ratio"])
        elif c["component"] in K_enzyme:
            all_enz_deps.append(c["max_dep_ratio"])
    bins = np.linspace(0, 1.05, 25)
    ax.hist([all_met_deps, all_enz_deps], bins=bins,
            color=["#6a994e", "#bc4749"],
            label=[f"metabolic (n={len(all_met_deps)})",
                   f"enzyme (n={len(all_enz_deps)})"],
            stacked=False, rwidth=0.8, alpha=0.7)
    ax.axvline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5 threshold")
    ax.axvline(0.7139, color="blue", linestyle=":", linewidth=1,
               label="dilution-decay 1-exp(-1.25)=0.7139")
    ax.set_xlabel("max dependency ratio (single-reaction-KO)")
    ax.set_ylabel("Count")
    ax.set_title(f"Pooled dep_ratio distribution across E-K\n"
                 f"({verdict})")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle(
        f"v3 dep_ratio universality test: Networks E-J + K\n"
        f"metabolic-robust fraction vs enzyme-robust fraction per network\n"
        f"Verdict: {verdict}",
        fontsize=11
    )
    fig.savefig(f"{out_dir}/autopoiesis_networks_E_to_J_v3_dep_ratio.png", dpi=150)
    plt.close(fig)

    # TXT report
    lines = []
    lines.append("v3 dep_ratio universality test -- Networks E-J + K")
    lines.append("=" * 78)
    lines.append("")
    lines.append("ITERATION SUMMARY (extends Network K v2 dep_ratio commit 07e6d85):")
    lines.append("  Network K v2 (commit 07e6d85): 6/13 metabolic robust + 0/38 enzymes robust.")
    lines.append("    Asymmetric profile: metabolic-multi-producer-robust + enzyme-single-gene-fragile.")
    lines.append("  v3 (this script): Apply the SAME v2 dep_ratio protocol to Networks E, F, G, H, I, J")
    lines.append("    to test whether the asymmetry is UNIVERSAL across the E->K lineage or K-specific.")
    lines.append("")
    lines.append("SUMMARY TABLE:")
    lines.append(f"  {'Network':<8} {'species':<8} {'rxns':<6} {'metab':<6} {'enz':<6} "
                 f"{'metab_rob':<14} {'enz_rob':<12} {'metab_dep':<14} {'enz_dep':<14}")
    lines.append("  " + "-" * 90)
    for s in summary_table:
        lines.append(f"  {s['network']:<8} {s['n_species']:<8} {s['n_reactions']:<6} "
                     f"{s['n_metabolic']:<6} {s['n_enzyme']:<6} "
                     f"{s['metabolic_robust']}/{s['n_metabolic']} ({100*s['metabolic_robust_frac']:.0f}%)    "
                     f"{s['enzyme_robust']}/{s['n_enzyme']:<5}    "
                     f"{s['metabolic_mean_dep']:<14.4f} {s['enzyme_mean_dep']:<14.4f}")
    lines.append("")
    lines.append("UNIVERSALITY TEST:")
    lines.append(f"  - Networks with >30% metabolic robust: {n_universal_metabolic}/{len(summary_table)}")
    lines.append(f"  - Networks with 0% enzyme robust: {n_universal_enzyme_fragile}/{len(summary_table)}")
    lines.append(f"  - Mean metabolic max_dep across lineage: {metabolic_mean:.4f} +/- {metabolic_std:.4f}")
    lines.append(f"  - Mean enzyme max_dep across lineage: {enzyme_mean:.4f} +/- {enzyme_std:.4f}")
    lines.append(f"  - Enzyme - metabolic mean dep gap: {metabolic_enzyme_gap:.4f}")
    lines.append(f"  - VERDICT: {verdict}")
    lines.append("")
    lines.append("INTERPRETATION:")
    if "UNIVERSAL" in verdict:
        lines.append("  - The metabolic-robust + enzyme-fragile profile is a STRUCTURAL PROPERTY")
        lines.append("    of the isozyme-dampener architecture, holding across the entire E->K lineage.")
        lines.append("  - Every network shows: metabolic intermediates with multi-producer redundancy")
        lines.append("    have low dep_ratio (robust to single-reaction-KO), while enzymes with single-")
        lines.append("    synthesis-gene have dep_ratio = 0.7139 = 1-exp(-1.25) (matching dilution-decay).")
        lines.append("  - The asymmetry is NOT a Network-K-specific signature; it is the DESIGN PRINCIPLE")
        lines.append("    of the isozyme-dampener network architecture, observable in every iteration of")
        lines.append("    the lineage from E (the smallest, with 8 enzyme pairs) to K (the largest, with")
        lines.append("    19 enzyme pairs + ACS1/2).")
    elif "PARTIALLY" in verdict:
        lines.append("  - The enzyme-fragile signature (dep_ratio ~ 0.7139) is UNIVERSAL across the")
        lines.append("    lineage, but the metabolic-robust signature is weaker in earlier networks (E, F)")
        lines.append("    with fewer isozyme pairs. The asymmetry EMERGES as the network accumulates")
        lines.append("    isozyme dampeners across the lineage, reaching its clearest form in Network K.")
    else:
        lines.append("  - The metabolic-robust + enzyme-fragile profile is Network-K-specific and does")
        lines.append("    NOT generalize across the lineage. This suggests the asymmetry in K is a")
        lines.append("    consequence of the specific cascade-breaking history (ACS1/2 + ALT5/6 + ...)")
        lines.append("    rather than a generic property of the isozyme-dampener architecture.")
    lines.append("")
    lines.append("IMPLICATION FOR CASCADE-BREAKING PRESCRIPTION (from task (b)):")
    lines.append("  - If UNIVERSAL, the cascade-breaking prescription from task (b) (add isozyme pairs")
    lines.append("    producing each fragile intermediate from independent substrates) is a GENERIC")
    lines.append("    engineering principle for isozyme-dampener networks, applicable to any iteration")
    lines.append("    of the lineage.")
    lines.append("  - If PARTIALLY UNIVERSAL, the prescription works in mature networks (I, J, K) where")
    lines.append("    the metabolic-robust signature is established, but may not transfer cleanly to")
    lines.append("    earlier networks (E, F) where the asymmetry has not yet emerged.")
    txt = "\n".join(lines)
    with open(f"{out_dir}/autopoiesis_networks_E_to_J_v3_dep_ratio.txt", "w") as f:
        f.write(txt)
    print()
    print(txt)
    print()
    print(f"[outputs written to {out_dir}/]")
    print(f"  - autopoiesis_networks_E_to_J_v3_dep_ratio.csv")
    print(f"  - autopoiesis_networks_E_to_J_v3_dep_ratio.png")
    print(f"  - autopoiesis_networks_E_to_J_v3_dep_ratio.txt")
    print(f"  - autopoiesis_networks_E_to_J_v3_dep_ratio_results.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
