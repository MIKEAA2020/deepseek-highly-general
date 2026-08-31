"""
E11: Cross-organism closure test on iAF1260 + iMM904 BiGG models.

CONTEXT (manuscript):
  Qwen §8.5 'stop engineering networks; apply test to fixed real networks'
  Original E2 (Remark rem:iJO1366-external-v2) applied the closure test to
  FIXED E. coli iJO1366 only. The Qwen audit explicitly asks for cross-
  organism generalization to a SECOND BiGG model. Future Directions listed
  this as NOT-YET-IMPLEMENTED (journal_manuscript.tex line ~7125).

APPROACH:
  Apply the EXACT SAME closure-test pipeline as autopoiesis_ijO1366_overlay.py
  to two additional BiGG models (locally cached XML files):
    - iAF1260  (Feist et al. 2010 Nat Biotechnol; E. coli K-12 MG1655
                reconstruction, alt to iJO1366): 1668 mets, 2382 rxns, 1261 genes
    - iMM904  (Mo et al. 2009 BMC Syst Biol; S. cerevisiae):
                1226 mets, 1577 rxns, 905 genes; 8 compartments (c,e,g,m,n,r,v,x)

  Three tests:
    (A) Closure verdict per model (50-metabolite test set: 10 Network B
        metabolites that exist + 40 random cytosolic). For iMM904 we use the
        'c' (cytosol) compartment.
    (B) Cross-organism confusion matrix: for ORTHOLOGOUS metabolites (same
        BiGG ID across models), do the closure verdicts agree?
    (C) Universal signature test: is the 'metabolic robust + enzyme fragile'
        profile (Qwen §8.5) present in iAF1260 and iMM904 as it was in
        iJO1366?

  The iJO1366 verdicts are loaded from the existing
  autopoiesis_ijO1366_overlay.csv (run by autopoiesis_ijO1366_overlay.py)
  to avoid redundant FBA computation.

OUTPUTS:
  /home/z/my-project/download/autopoiesis_cross_organism.{csv,txt,png}
  /home/z/my-project/download/novelty_cross_organism_e11_results.json
"""
import os, csv, json, copy, warnings
warnings.filterwarnings("ignore")
import numpy as np
from cobra.io import read_sbml_model
from cobra import Reaction

# ----------------------------------------------------------------------
# 0. Helper functions (copied from autopoiesis_ijO1366_overlay.py)
# ----------------------------------------------------------------------
def producing_reactions(met, model):
    producers = []
    for r in met.reactions:
        coef = r.metabolites.get(met, 0)
        if coef > 0:
            producers.append((r.id, coef))
    return producers

def consuming_reactions(met, model):
    consumers = []
    for r in met.reactions:
        coef = r.metabolites.get(met, 0)
        if coef < 0:
            consumers.append((r.id, abs(coef)))
    return consumers

def run_fba(m):
    sol = m.optimize()
    if sol.status == 'optimal':
        return sol.objective_value, sol.fluxes
    return None, None

# ----------------------------------------------------------------------
# 1. Load all three models
# ----------------------------------------------------------------------
DATA_DIR = "/home/z/my-project/data/bigg_models"
OUT_DIR  = "/home/z/my-project/download"
os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 78)
print("E11: CROSS-ORGANISM CLOSURE TEST (Qwen §8.5)")
print("  iJO1366 (E. coli K-12 MG1655, Orth et al. 2011)")
print("  iAF1260 (E. coli K-12 MG1655, Feist et al. 2010)")
print("  iMM904  (S. cerevisiae, Mo et al. 2009)")
print("=" * 78)

# Use the cached XML we downloaded for iAF1260 + iMM904
print("\nLoading iAF1260...")
model_iAF1260 = read_sbml_model(f"{DATA_DIR}/iAF1260.xml")
print(f"  iAF1260: {len(model_iAF1260.metabolites)} mets, "
      f"{len(model_iAF1260.reactions)} rxns, {len(model_iAF1260.genes)} genes; "
      f"compartments {sorted(set(m.compartment for m in model_iAF1260.metabolites))}")

print("Loading iMM904...")
model_iMM904 = read_sbml_model(f"{DATA_DIR}/iMM904.xml")
print(f"  iMM904:  {len(model_iMM904.metabolites)} mets, "
      f"{len(model_iMM904.reactions)} rxns, {len(model_iMM904.genes)} genes; "
      f"compartments {sorted(set(m.compartment for m in model_iMM904.metabolites))}")

# Load iJO1366 via cobrapy HTTP cache (already works)
print("Loading iJO1366 (control)...")
from cobra.io import load_model
model_iJO1366 = load_model("iJO1366")
print(f"  iJO1366: {len(model_iJO1366.metabolites)} mets, "
      f"{len(model_iJO1366.reactions)} rxns, {len(model_iJO1366.genes)} genes; "
      f"compartments {sorted(set(m.compartment for m in model_iJO1366.metabolites))}")

MODELS = {
    "iJO1366": (model_iJO1366, "E. coli K-12 MG1655 (Orth 2011)"),
    "iAF1260": (model_iAF1260, "E. coli K-12 MG1655 (Feist 2010)"),
    "iMM904":  (model_iMM904,  "S. cerevisiae (Mo 2009)"),
}

# ----------------------------------------------------------------------
# 2. Define the 10 Network B metabolites (BiGG IDs, cytosolic _c)
# ----------------------------------------------------------------------
NETWORK_B_BIDS = [
    "g6p_c", "fdp_c", "pep_c", "pyr_c", "accoa_c",
    "cit_c", "akg_c", "succ_c", "mal__L_c", "oaa_c"
]
print(f"\nNetwork B cytosolic metabolites (orthologous across all 3 models): "
      f"{len(NETWORK_B_BIDS)}")
# Verify each metabolite exists in each model
for mname, (m, mlabel) in MODELS.items():
    found = [bid for bid in NETWORK_B_BIDS if bid in [mm.id for mm in m.metabolites]]
    missing = [bid for bid in NETWORK_B_BIDS if bid not in [mm.id for mm in m.metabolites]]
    print(f"  {mname}: {len(found)}/{len(NETWORK_B_BIDS)} Network B mets found"
          + (f"; missing: {missing}" if missing else ""))

# ----------------------------------------------------------------------
# 3. Build the random cytosolic pool per model (same seed; first 40 random)
# ----------------------------------------------------------------------
np.random.seed(20260830)
test_sets = {}
for mname, (m, _) in MODELS.items():
    exchange_rxns = [r for r in m.reactions if r.id.startswith("EX_")]
    food_metabolites = set()
    for r in exchange_rxns:
        for met in r.metabolites:
            if r.metabolites[met] < 0:
                food_metabolites.add(met.id)
    cytosolic_mets = [mt for mt in m.metabolites if mt.compartment == 'c'
                      and mt.id not in food_metabolites]
    n_bids = [bid for bid in NETWORK_B_BIDS
              if bid in [mm.id for mm in cytosolic_mets]]
    pool = [mt.id for mt in cytosolic_mets if mt.id not in n_bids]
    random_sample = np.random.choice(pool, size=min(40, len(pool)),
                                     replace=False).tolist()
    test_sets[mname] = n_bids + random_sample
    print(f"  {mname} test set: {len(test_sets[mname])} mets "
          f"({len(n_bids)} Network B + {len(random_sample)} random cytosolic)")

# ----------------------------------------------------------------------
# 4. Closure test per model
# ----------------------------------------------------------------------
def closure_test_on_model(model, model_name, baseline_fluxes, test_ids):
    """Same closure test logic as autopoiesis_ijO1366_overlay.py."""
    print(f"\nRunning closure test on {model_name}...")
    print(f"  {'metabolite':>16}  {'n_prod':>6}  {'baseline':>10}  "
          f"{'knockout':>10}  {'recover':>10}  {'verdict':>14}")
    print("  " + "-" * 78)
    records = []
    flux_threshold = 1e-6
    for m_id in test_ids:
        met = model.metabolites.get_by_id(m_id)
        producers = producing_reactions(met, model)
        consumers = consuming_reactions(met, model)
        n_prod = len(producers)
        # baseline production flux
        baseline_prod = 0.0
        if baseline_fluxes is not None:
            for rid, coef in producers:
                rflux = baseline_fluxes[rid] if rid in baseline_fluxes.index else 0.0
                baseline_prod += coef * max(rflux, 0.0)
        # KO producers
        with model:
            for rid, _ in producers:
                if rid in model.reactions:
                    r = model.reactions.get_by_id(rid)
                    r.lower_bound = 0
                    r.upper_bound = 0
            knock_obj, knock_fluxes = run_fba(model)
        knock_prod = 0.0
        if knock_fluxes is not None:
            for rid, coef in producers:
                rflux = knock_fluxes[rid] if rid in knock_fluxes.index else 0.0
                knock_prod += coef * max(rflux, 0.0)
        # Recovery
        rec_obj, rec_fluxes = run_fba(model)
        rec_prod = 0.0
        if rec_fluxes is not None:
            for rid, coef in producers:
                rflux = rec_fluxes[rid] if rid in rec_fluxes.index else 0.0
                rec_prod += coef * max(rflux, 0.0)
        knock_success = baseline_prod > flux_threshold and knock_prod < flux_threshold
        recover_success = rec_prod > flux_threshold
        causally_internal = knock_success and recover_success
        verdict = "AUTOPOIETIC" if causally_internal else "HOMEOSTATIC"
        records.append({
            "metabolite_id": m_id, "n_producing_reactions": n_prod,
            "baseline_prod_flux": baseline_prod,
            "knockout_prod_flux": knock_prod,
            "recovery_prod_flux": rec_prod,
            "knockout_success": knock_success,
            "recover_success": recover_success,
            "causally_internal": causally_internal, "verdict": verdict,
        })
        short_id = m_id[:14]
        print(f"  {short_id:>16}  {n_prod:>6}  {baseline_prod:>10.6f}  "
              f"{knock_prod:>10.6f}  {rec_prod:>10.6f}  {verdict:>14}")
    n_auto = sum(1 for r in records if r["causally_internal"])
    print(f"\n  {model_name}: {n_auto}/{len(records)} causally internal "
          f"({100.0*n_auto/len(records):.1f}%)")
    return records

# Baseline FBA per model
print("\nRunning baseline FBA per model...")
baselines = {}
for mname, (m, _) in MODELS.items():
    obj, flx = run_fba(m)
    baselines[mname] = (obj, flx)
    print(f"  {mname}: biomass flux = {obj:.6f}")

records_per_model = {}
for mname, (m, _) in MODELS.items():
    records_per_model[mname] = closure_test_on_model(
        m, mname, baselines[mname][1], test_sets[mname]
    )

# ----------------------------------------------------------------------
# 5. Cross-organism confusion matrix on Network B (orthologous metabolites)
# ----------------------------------------------------------------------
print("\n" + "=" * 78)
print("CROSS-ORGANISM VERDICT COMPARISON (Network B orthologous metabolites)")
print("=" * 78)
print(f"  {'metabolite':>16}  {'iJO1366':>14}  {'iAF1260':>14}  {'iMM904':>14}")
print("  " + "-" * 64)

n_agree_iAF = 0
n_agree_iMM = 0
n_agree_iAF_iMM = 0
n_total_b = 0
for bid in NETWORK_B_BIDS:
    verdicts = {}
    for mname in MODELS:
        # Find this metabolite's record in each model
        rec = next((r for r in records_per_model[mname]
                    if r["metabolite_id"] == bid), None)
        verdicts[mname] = rec["verdict"] if rec else "MISSING"
    print(f"  {bid:>16}  {verdicts['iJO1366']:>14}  "
          f"{verdicts['iAF1260']:>14}  {verdicts['iMM904']:>14}")
    if verdicts["iJO1366"] != "MISSING" and verdicts["iAF1260"] != "MISSING":
        n_total_b += 1
        if verdicts["iJO1366"] == verdicts["iAF1260"]:
            n_agree_iAF += 1
    if verdicts["iJO1366"] != "MISSING" and verdicts["iMM904"] != "MISSING":
        if verdicts["iJO1366"] == verdicts["iMM904"]:
            n_agree_iMM += 1
    if verdicts["iAF1260"] != "MISSING" and verdicts["iMM904"] != "MISSING":
        if verdicts["iAF1260"] == verdicts["iMM904"]:
            n_agree_iAF_iMM += 1

print(f"\nVerdict agreement on the {n_total_b} Network B metabolites "
      f"(orthologous across iJO1366 + iAF1260):")
print(f"  iJO1366 vs iAF1260 (same organism, different reconstruction): "
      f"{n_agree_iAF}/{n_total_b} agree")
print(f"  iJO1366 vs iMM904  (cross-organism, E. coli vs S. cerevisiae): "
      f"{n_agree_iMM}/10 agree")
print(f"  iAF1260 vs iMM904  (alt E. coli vs S. cerevisiae):            "
      f"{n_agree_iAF_iMM}/10 agree")

# ----------------------------------------------------------------------
# 6. 'metabolic robust + enzyme fragile' universality test
# ----------------------------------------------------------------------
# For each model: stratify by n_producing_reactions
# Metabolic robust: metabolites with n_prod >= 2 are more likely AUTOPOIETIC
# (multiple producers → robust to single-KO)
# Enzyme fragile: metabolites with n_prod == 1 are more likely HOMEOSTATIC
print("\n" + "=" * 78)
print("'METABOLIC ROBUST + ENZYME FRAGILE' UNIVERSALITY TEST")
print("=" * 78)
print(f"  {'model':>10}  {'n_prod=1':>30}  {'n_prod>=2':>30}")
print(f"  {'':>10}  {'A/I  H/I  Total':>30}  {'A/I  H/I  Total':>30}")
print("  " + "-" * 76)
universal_results = {}
for mname, recs in records_per_model.items():
    p1 = [r for r in recs if r["n_producing_reactions"] == 1]
    p2 = [r for r in recs if r["n_producing_reactions"] >= 2]
    p1_a = sum(1 for r in p1 if r["causally_internal"])
    p1_h = len(p1) - p1_a
    p2_a = sum(1 for r in p2 if r["causally_internal"])
    p2_h = len(p2) - p2_a
    pct_p1 = 100.0 * p1_a / len(p1) if p1 else 0
    pct_p2 = 100.0 * p2_a / len(p2) if p2 else 0
    print(f"  {mname:>10}  "
          f"{p1_a:>4}/{len(p1):<3} {p1_h:>3}/{len(p1):<3}  {len(p1):>5}    "
          f"{p2_a:>4}/{len(p2):<3} {p2_h:>3}/{len(p2):<3}  {len(p2):>5}")
    print(f"  {'':>10}  ({pct_p1:>5.1f}% AUTOPOIETIC)              "
          f"({pct_p2:>5.1f}% AUTOPOIETIC)")
    universal_results[mname] = {
        "n_prod_1": {"A": p1_a, "H": p1_h, "total": len(p1),
                     "pct_auto": pct_p1},
        "n_prod_2plus": {"A": p2_a, "H": p2_h, "total": len(p2),
                         "pct_auto": pct_p2},
    }

# ----------------------------------------------------------------------
# 7. Save outputs
# ----------------------------------------------------------------------
n_auto_per_model = {mname: sum(1 for r in recs if r["causally_internal"])
                    for mname, recs in records_per_model.items()}
n_test_per_model = {mname: len(recs) for mname, recs in records_per_model.items()}
print("\n" + "=" * 78)
print("FINAL CROSS-ORGANISM CLOSURE VERDICT")
print("=" * 78)
for mname, (m, mlabel) in MODELS.items():
    print(f"  {mname} ({mlabel}): {n_auto_per_model[mname]}/{n_test_per_model[mname]} "
          f"({100.0*n_auto_per_model[mname]/n_test_per_model[mname]:.1f}%) "
          f"causally internal")

with open(f"{OUT_DIR}/autopoiesis_cross_organism.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metabolite_id",
                "n_prod_iJO1366", "verdict_iJO1366",
                "n_prod_iAF1260", "verdict_iAF1260",
                "n_prod_iMM904", "verdict_iMM904",
                "cross_organism_agreement"])
    all_mets = sorted(set(
        r["metabolite_id"] for mname in MODELS
        for r in records_per_model[mname]
    ))
    for mid in all_mets:
        row = [mid]
        for mname in ["iJO1366", "iAF1260", "iMM904"]:
            rec = next((r for r in records_per_model[mname]
                        if r["metabolite_id"] == mid), None)
            if rec:
                row.extend([rec["n_producing_reactions"], rec["verdict"]])
            else:
                row.extend(["", "MISSING"])
        # agreement: all three the same (excluding MISSING)
        present_verdicts = [row[i] for i in [2, 4, 6]
                            if row[i] not in ("", "MISSING")]
        agree = "AGREE" if len(set(present_verdicts)) == 1 else "DISAGREE"
        if len(present_verdicts) < 2:
            agree = "PARTIAL"
        row.append(agree)
        w.writerow(row)

with open(f"{OUT_DIR}/autopoiesis_cross_organism.txt", "w") as f:
    f.write("E11: CROSS-ORGANISM CLOSURE TEST (Qwen §8.5 deeper)\n")
    f.write("=" * 78 + "\n")
    f.write("Models tested (all FIXED, no engineering):\n")
    for mname, (_, mlabel) in MODELS.items():
        f.write(f"  {mname}: {mlabel}\n")
    f.write("\n")
    f.write(f"Test set per model: 10 Network B + 40 random cytosolic = 50 mets\n")
    f.write("Closure test (autopoiesis regeneration):\n")
    f.write("  causally_internal = (baseline_prod > 1e-6)\n")
    f.write("                  AND (knockout_prod  < 1e-6)\n")
    f.write("                  AND (recovery_prod  > 1e-6)\n")
    f.write("\n")
    f.write("BASELINE FBA per model:\n")
    for mname in MODELS:
        obj, _ = baselines[mname]
        f.write(f"  {mname}: biomass flux = {obj:.6f}\n")
    f.write("\n")
    f.write("CLOSURE VERDICT per model:\n")
    for mname in MODELS:
        f.write(f"  {mname}: {n_auto_per_model[mname]}/{n_test_per_model[mname]} "
                f"({100.0*n_auto_per_model[mname]/n_test_per_model[mname]:.1f}%) "
                f"causally internal\n")
    f.write("\n")
    f.write("CROSS-ORGANISM VERDICT (Network B orthologous mets):\n")
    f.write(f"  iJO1366 vs iAF1260 (same org, diff reconstruction): "
            f"{n_agree_iAF}/{n_total_b} agree\n")
    f.write(f"  iJO1366 vs iMM904  (E. coli vs S. cerevisiae):        "
            f"{n_agree_iMM}/10 agree\n")
    f.write(f"  iAF1260 vs iMM904  (alt E. coli vs S. cerevisiae):    "
            f"{n_agree_iAF_iMM}/10 agree\n")
    f.write("\n")
    f.write("'METABOLIC ROBUST + ENZYME FRAGILE' universality:\n")
    f.write(f"  {'model':>10}  {'n_prod=1':>20}  {'n_prod>=2':>20}\n")
    for mname in MODELS:
        r = universal_results[mname]
        f.write(f"  {mname:>10}  "
                f"auto%={r['n_prod_1']['pct_auto']:.1f}% ({r['n_prod_1']['A']}/{r['n_prod_1']['total']})  "
                f"auto%={r['n_prod_2plus']['pct_auto']:.1f}% ({r['n_prod_2plus']['A']}/{r['n_prod_2plus']['total']})\n")
    f.write("\n")
    f.write("Per-metabolite Network B verdict table:\n")
    f.write(f"  {'met_id':>16}  {'iJO1366':>14}  {'iAF1260':>14}  {'iMM904':>14}\n")
    for bid in NETWORK_B_BIDS:
        verdicts = {}
        for mname in MODELS:
            rec = next((r for r in records_per_model[mname]
                        if r["metabolite_id"] == bid), None)
            verdicts[mname] = rec["verdict"] if rec else "MISSING"
        f.write(f"  {bid:>16}  {verdicts['iJO1366']:>14}  "
                f"{verdicts['iAF1260']:>14}  {verdicts['iMM904']:>14}\n")

# JSON results
results_json = {
    "task": "E11 cross-organism closure test (Qwen §8.5 deeper)",
    "models": {
        mname: {"label": mlbl,
                "n_mets": len(mdl.metabolites),
                "n_rxns": len(mdl.reactions),
                "n_genes": len(mdl.genes),
                "biomass_flux": baselines[mname][0],
                "test_set_size": n_test_per_model[mname],
                "n_causally_internal": n_auto_per_model[mname],
                "pct_causally_internal": 100.0*n_auto_per_model[mname]/n_test_per_model[mname]}
        for mname, (mdl, mlbl) in MODELS.items()
    },
    "cross_organism_agreement_network_B": {
        "iJO1366_vs_iAF1260": f"{n_agree_iAF}/{n_total_b}",
        "iJO1366_vs_iMM904":  f"{n_agree_iMM}/10",
        "iAF1260_vs_iMM904":  f"{n_agree_iAF_iMM}/10",
    },
    "universal_signature": universal_results,
    "verdict_summary": (
        f"Cross-organism generalization: iJO1366 {n_auto_per_model['iJO1366']}/{n_test_per_model['iJO1366']} "
        f"({100.0*n_auto_per_model['iJO1366']/n_test_per_model['iJO1366']:.1f}%) "
        f"vs iAF1260 {n_auto_per_model['iAF1260']}/{n_test_per_model['iAF1260']} "
        f"({100.0*n_auto_per_model['iAF1260']/n_test_per_model['iAF1260']:.1f}%) "
        f"vs iMM904 {n_auto_per_model['iMM904']}/{n_test_per_model['iMM904']} "
        f"({100.0*n_auto_per_model['iMM904']/n_test_per_model['iMM904']:.1f}%). "
        f"Network B orthologs: iJO1366 vs iMM904 {n_agree_iMM}/10 agree."
    ),
}
with open(f"{OUT_DIR}/novelty_cross_organism_e11_results.json", "w") as f:
    json.dump(results_json, f, indent=2)

# ----------------------------------------------------------------------
# 8. Plot: 3-panel cross-organism verdict
# ----------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for p in [
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]:
    try:
        fm.fontManager.addfont(p)
    except Exception:
        pass
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)

# Panel 1: bar chart of causally internal per model
ax = axes[0]
mnames = list(MODELS.keys())
vals = [n_auto_per_model[m] for m in mnames]
totals = [n_test_per_model[m] for m in mnames]
colors = ["#3a7ca5", "#6a994e", "#bc4749"]
bars = ax.bar(mnames, vals, color=colors, edgecolor="black", linewidth=0.8)
for bar, v, t in zip(bars, vals, totals):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.4,
            f"{v}/{t}\n({100.0*v/t:.1f}%)",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_ylabel("# Causally internal (of 50 tested)")
ax.set_ylim(0, max(totals) + 4)
ax.set_title("Closure verdict across organisms",
             fontsize=11)
ax.grid(True, alpha=0.3, axis="y")

# Panel 2: Network B verdict heatmap per model
ax = axes[1]
verdict_matrix = np.zeros((len(NETWORK_B_BIDS), 3))
for i, bid in enumerate(NETWORK_B_BIDS):
    for j, mname in enumerate(mnames):
        rec = next((r for r in records_per_model[mname]
                    if r["metabolite_id"] == bid), None)
        verdict_matrix[i, j] = 1.0 if (rec and rec["causally_internal"]) else 0.0
im = ax.imshow(verdict_matrix, aspect="auto", cmap="RdYlGn",
               vmin=0, vmax=1, interpolation="nearest")
ax.set_xticks(range(3))
ax.set_xticklabels(mnames, fontsize=9, rotation=30)
ax.set_yticks(range(len(NETWORK_B_BIDS)))
ax.set_yticklabels(NETWORK_B_BIDS, fontsize=8)
ax.set_title("Network B closure verdict\n(green=AUTOPOIETIC, red=HOMEOSTATIC)",
             fontsize=10)
# Annotate cells
for i in range(len(NETWORK_B_BIDS)):
    for j in range(3):
        val = verdict_matrix[i, j]
        ax.text(j, i, "A" if val > 0 else "H",
                ha="center", va="center", fontsize=10, fontweight="bold",
                color="black" if 0.3 < val < 0.7 else ("white" if val > 0.5 else "black"))

# Panel 3: n_producing_reactions stratification per model
ax = axes[2]
x = np.arange(len(mnames))
w = 0.35
p1_auto = [universal_results[m]["n_prod_1"]["pct_auto"] for m in mnames]
p2_auto = [universal_results[m]["n_prod_2plus"]["pct_auto"] for m in mnames]
ax.bar(x - w/2, p1_auto, w, label="n_prod = 1 (enzyme fragile)",
       color="#bc4749", edgecolor="black", linewidth=0.6)
ax.bar(x + w/2, p2_auto, w, label="n_prod >= 2 (metabolic robust)",
       color="#6a994e", edgecolor="black", linewidth=0.6)
ax.set_xticks(x)
ax.set_xticklabels(mnames, fontsize=9, rotation=30)
ax.set_ylabel("% causally internal (AUTOPOIETIC)")
ax.set_ylim(0, 105)
ax.set_title("Universality: 'metabolic robust + enzyme fragile'\n"
             "(n_prod>=2 should have HIGHER auto% than n_prod=1)",
             fontsize=10)
ax.legend(loc="upper left", fontsize=8)
ax.grid(True, alpha=0.3, axis="y")

fig.suptitle("E11: Cross-organism closure test (iJO1366 vs iAF1260 vs iMM904) — "
             "Qwen §8.5 deeper",
             fontsize=12)
fig.savefig(f"{OUT_DIR}/autopoiesis_cross_organism.png", dpi=150)
plt.close(fig)

print(f"\n[outputs written to {OUT_DIR}/]")
print(f"  - autopoiesis_cross_organism.csv")
print(f"  - autopoiesis_cross_organism.txt")
print(f"  - autopoiesis_cross_organism.png")
print(f"  - novelty_cross_organism_e11_results.json")
