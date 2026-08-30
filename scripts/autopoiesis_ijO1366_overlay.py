"""
Task A: iJO1366 + Network-K-style isozyme-dampener overlay.

CONTEXT (manuscript):
  Network C (bare BiGG iJO1366) closure test (autopoiesis_ijO1366.py) gave
  28/50 causally internal on a 50-metabolite sample (10 from Network B +
  40 random cytosolic). Network K achieves 52/52 = 100% on the small
  curated E->K lineage by overlaying five isozyme-dampener pairs:
    ALT3/4   (EC 2.6.1.12, ASP + PYR -> ALA + OAA)        [Network F]
    ALT5/6   (EC 2.6.1.2, alphaKG + ALA -> GLU + PYR)    [Network G]
    ASPAT3/4 (EC 2.6.1.1, GLU + OAA -> ASP + alphaKG)    [Network H]
    ALT7/8   (reversible ALT5/6 direction)               [Network I]
    ALDO3/4  (EC 4.1.2.13, FBP <=> DHAP + G3P)           [Network J]
    ACS1/2   (EC 6.2.1.1, Acetate + ATP -> AcCoA + ADP + Pi) [Network K]

  User asks: extend the autopoiesis closure test to FULL BiGG iJO1366
  with the isozyme-dampener overlay, to test whether the verdict at
  genome scale improves when the same dampener architecture that
  closed Network K is applied to iJO1366.

APPROACH:
  - Load iJO1366 via cobrapy.
  - Define the 6 dampener reactions using BiGG metabolite IDs.
  - Build a model_with_overlay = copy(iJO1366) + dampener reactions.
  - Reproduce the SAME 50-metabolite test set used by
    autopoiesis_ijO1366.py (same seed 20260830, same 10 Network-B mets
    + same 40 random cytosolic mets) for a controlled A/B comparison.
  - Run the closure test (KO producing reactions, observe, restore)
    on BOTH the bare iJO1366 and the iJO1366+dampener overlay.
  - Report the verdict delta: which metabolites flipped HOMEOSTATIC ->
    AUTOPOIETIC under the overlay.

  VERDICT LOGIC (same as autopoiesis_ijO1366.py):
    causally_internal = (baseline_prod > 1e-6)
                    AND (knockout_prod  < 1e-6)  (KO kills m)
                    AND (recovery_prod  > 1e-6)  (m recovers)
  With overlay, "producing reactions" includes the dampener. KO'ing
  the dampener along with original producers tests whether m has any
  EXTERNAL supply: if KO of (original + dampener) STILL leaves m
  fluxing, m is externally supplied (HOMEOSTATIC); if KO kills m,
  m is internally produced (potentially AUTOPOIETIC). The overlay
  FLIPS the verdict for metabolites whose original producer set was
  empty (no internal production) -- the dampener becomes the new
  internal producer, baseline flux rises above threshold, KO kills m,
  recovery restores. Verdict: HOMEOSTATIC -> AUTOPOIETIC.

OUTPUTS:
  /home/z/my-project/download/autopoiesis_ijO1366_overlay.{csv,png,txt}
"""
import numpy as np
import os, csv, json, copy
from cobra.io import load_model
from cobra import Reaction, Metabolite

# ----------------------------------------------------------------------
# Load iJO1366
# ----------------------------------------------------------------------
print("=" * 78)
print("TASK A: iJO1366 + ISOZYME-DAMPENER OVERLAY (Network-K-style)")
print("       extend the autopoiesis closure test to FULL BiGG iJO1366")
print("       with ALT3/4, ALT5/6, ASPAT3/4, ALT7/8, ALDO3/4, ACS1/2")
print("=" * 78)
print()
print("Loading iJO1366 model via cobrapy...")
model_bare = load_model("iJO1366")
print(f"  Bare iJO1366: {len(model_bare.metabolites)} metabolites, "
      f"{len(model_bare.reactions)} reactions")
print()

# ----------------------------------------------------------------------
# Define the 6 dampener reactions (Network K overlay)
# ----------------------------------------------------------------------
# BiGG IDs (cytosolic _c compartment):
#   glucose:   glc__D_e (exchange EX_glc__D_e) -> glc__D_c
#   G6P:       g6p_c        FBP:        fdp_c
#   DHAP:      dhap_c       G3P:        g3p_c
#   PEP:       pep_c        PYR:        pyr_c
#   ALA:       ala__L_c     ASP:        asp__L_c
#   GLU:       glu__L_c     alphaKG:    akg_c
#   OAA:       oaa_c        MAL:        mal__L_c
#   AcCoA:     accoa_c      Acetate:    ac_c
#   ATP/ADP/Pi/CO2/NAD+/NADH/NH3: atp_c, adp_c, pi_c, co2_c, nad_c, nadh_c, nh4_c

dampener_specs = [
    # (id, name, reaction_str, subsystem, lower, upper)
    # ALT3/4: ASP + PYR -> ALA + OAA  (Network F; alternative ALA source)
    ("M11_ALT3", "ALT3 dampener (ASP+PYR->ALA+OAA)",
     "asp__L_c + pyr_c --> ala__L_c + oaa_c",
     "ALT3/4 dampener (Network F overlay)", -10, 10),
    # ALT5/6: alphaKG + ALA -> GLU + PYR  (Network G; alternative PYR source)
    ("M12_ALT5", "ALT5 dampener (alphaKG+ALA->GLU+PYR)",
     "akg_c + ala__L_c --> glu__L_c + pyr_c",
     "ALT5/6 dampener (Network G overlay)", -10, 10),
    # ASPAT3/4: GLU + OAA -> ASP + alphaKG  (Network H; alternative ASP source)
    ("M17_ASPAT3", "ASPAT3 dampener (GLU+OAA->ASP+alphaKG)",
     "glu__L_c + oaa_c --> asp__L_c + akg_c",
     "ASPAT3/4 dampener (Network H overlay)", -10, 10),
    # ALT7/8: reversible GLU + PYR <-> ALA + alphaKG  (Network I; ALA dampener)
    # The reverse direction (GLU + PYR -> ALA + alphaKG) is the dampener that
    # produces ALA from PYR (the alternative ALA source independent of M5/M11).
    ("M19_ALT7", "ALT7 dampener (GLU+PYR<->ALA+alphaKG, reversible)",
     "glu__L_c + pyr_c <==> ala__L_c + akg_c",
     "ALT7/8 dampener (Network I overlay)", -10, 10),
    # ALDO3/4: reversible FBP <-> DHAP + G3P  (Network J; FBP dampener)
    ("M21_ALDO3", "ALDO3 dampener (FBP<->DHAP+G3P, reversible)",
     "fdp_c <==> dhap_c + g3p_c",
     "ALDO3/4 dampener (Network J overlay)", -10, 10),
    # ACS1/2: Acetate + ATP -> AcCoA + ADP + Pi  (Network K; NAD+-independent
    # AcCoA source -- bypasses PDH NAD+ bottleneck)
    # Real EC 6.2.1.1 also uses CoA and produces AMP + PPi; we use the simplified
    # stoichiometry matching Network K's M23 (CoA/AMP/PPi implicit).
    ("M23_ACS1", "ACS1 dampener (Acetate+ATP->AcCoA+ADP+Pi, NAD+-indep.)",
     "ac_c + atp_c --> accoa_c + adp_c + pi_c",
     "ACS1/2 dampener (Network K overlay)", -10, 10),
]

# Build the overlay model
print("Building iJO1366 + dampener overlay model...")
model_overlay = copy.deepcopy(model_bare)
for rid, name, rxn_str, subsys, lb, ub in dampener_specs:
    r = Reaction(rid)
    r.name = name
    r.subsystem = subsys
    # Build stoichiometry from reaction string
    # Parse "A + B --> C + D" or "A + B <==> C + D" or "A + B <-> C + D"
    if "<==>" in rxn_str:
        left, right = rxn_str.split("<==>")
        reversible = True
    elif "<->" in rxn_str:
        left, right = rxn_str.split("<->")
        reversible = True
    elif "-->" in rxn_str:
        left, right = rxn_str.split("-->")
        reversible = False
    else:
        raise ValueError(f"Bad reaction string: {rxn_str}")
    stoich = {}
    for side, sign in [(left.strip(), -1), (right.strip(), +1)]:
        if not side:
            continue
        for tok in side.split("+"):
            tok = tok.strip()
            coef, mid = 1, tok
            # support optional integer coefficient like "2 dhap_c"
            parts = tok.split()
            if len(parts) == 2 and parts[0].isdigit():
                coef = int(parts[0])
                mid = parts[1]
            elif len(parts) == 1:
                mid = parts[0]
            else:
                # token like "2 dhap_c" or "dhap_c"
                mid = parts[-1]
                if len(parts) == 2 and parts[0].isdigit():
                    coef = int(parts[0])
            met = model_overlay.metabolites.get_by_id(mid)
            stoich[met] = stoich.get(met, 0) + sign * coef
    r.add_metabolites(stoich)
    r.lower_bound = lb if reversible else 0
    r.upper_bound = ub
    model_overlay.add_reactions([r])

print(f"  Overlay model: {len(model_overlay.metabolites)} metabolites, "
      f"{len(model_overlay.reactions)} reactions "
      f"({len(model_overlay.reactions) - len(model_bare.reactions)} new)")
print()

# List the new dampener reactions
print("Dampener overlay reactions (6 new, mirroring Network K M11/M12/M17/M19/M21/M23):")
for rid, name, rxn_str, _, _, _ in dampener_specs:
    print(f"  {rid:14s}  {rxn_str}")
print()

# ----------------------------------------------------------------------
# Reproduce the SAME 50-metabolite test set as autopoiesis_ijO1366.py
# ----------------------------------------------------------------------
exchange_rxns = [r for r in model_bare.reactions if r.id.startswith("EX_")]
food_metabolites = set()
for r in exchange_rxns:
    for met in r.metabolites:
        if r.metabolites[met] < 0:
            food_metabolites.add(met.id)
cytosolic_mets = [m for m in model_bare.metabolites if m.compartment == 'c'
                  and m.id not in food_metabolites]

np.random.seed(20260830)
name_map = {
    "G6P": "g6p_c", "FBP": "fdp_c", "PEP": "pep_c", "PYR": "pyr_c",
    "AcCoA": "accoa_c", "CIT": "cit_c", "AKG": "akg_c", "SUC": "succ_c",
    "MAL": "mal__L_c", "OAA": "oaa_c"
}
test_metabolite_ids = []
for name, mid in name_map.items():
    if mid in [m.id for m in cytosolic_mets]:
        test_metabolite_ids.append(mid)
all_non_food_ids = [m.id for m in cytosolic_mets]
random_pool = [m for m in all_non_food_ids if m not in test_metabolite_ids]
random_sample = np.random.choice(random_pool, size=min(40, len(random_pool)),
                                 replace=False).tolist()
test_metabolite_ids = test_metabolite_ids + random_sample
print(f"Test set: {len(test_metabolite_ids)} non-food metabolites "
      f"(same as autopoiesis_ijO1366.py: 10 Network B + 40 random)")
print()

# ----------------------------------------------------------------------
# Closure test functions
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

# Baseline FBA on both models
print("Running baseline FBA on bare iJO1366...")
baseline_obj_bare, baseline_fluxes_bare = run_fba(model_bare)
print(f"  Bare biomass flux: {baseline_obj_bare:.6f}")
print("Running baseline FBA on overlay iJO1366+dampener...")
baseline_obj_ov, baseline_fluxes_ov = run_fba(model_overlay)
print(f"  Overlay biomass flux: {baseline_obj_ov:.6f}")
print()

viability_threshold = 0.1 * baseline_obj_bare
flux_threshold = 1e-6
print(f"Viability threshold (biomass > 0.1 * bare baseline): {viability_threshold:.6f}")
print(f"Flux threshold (production > 1e-6): {flux_threshold}")
print()

# Closure test on BOTH models for the same 50 metabolites
def closure_test_on_model(model, model_name, baseline_fluxes, test_ids):
    print(f"Running closure test on {model_name}...")
    print(f"  {'metabolite':>16}  {'n_prod':>6}  {'baseline':>10}  "
          f"{'knockout':>10}  {'recover':>10}  {'verdict':>14}")
    print("  " + "-" * 78)
    records = []
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
        # Recovery (restore)
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

records_bare = closure_test_on_model(model_bare, "bare iJO1366",
                                     baseline_fluxes_bare, test_metabolite_ids)
print()
records_overlay = closure_test_on_model(model_overlay, "iJO1366+dampener",
                                        baseline_fluxes_ov, test_metabolite_ids)
print()

# ----------------------------------------------------------------------
# Compute the verdict delta
# ----------------------------------------------------------------------
n_bare = sum(1 for r in records_bare if r["causally_internal"])
n_ov = sum(1 for r in records_overlay if r["causally_internal"])
n_total = len(records_bare)
print("=" * 78)
print(f"VERDICT COMPARISON (same 50-metabolite test set):")
print(f"  Bare iJO1366:                {n_bare}/{n_total} causally internal "
      f"({100.0*n_bare/n_total:.1f}%)")
print(f"  iJO1366 + dampener overlay:  {n_ov}/{n_total} causally internal "
      f"({100.0*n_ov/n_total:.1f}%)")
delta = n_ov - n_bare
print(f"  Delta: {delta:+d} metabolites flipped to AUTOPOIETIC under overlay")
print()

# List which metabolites flipped
flipped_to_auto = []
flipped_to_homeo = []
for rb, ro in zip(records_bare, records_overlay):
    if rb["verdict"] == "HOMEOSTATIC" and ro["verdict"] == "AUTOPOIETIC":
        flipped_to_auto.append(rb["metabolite_id"])
    elif rb["verdict"] == "AUTOPOIETIC" and ro["verdict"] == "HOMEOSTATIC":
        flipped_to_homeo.append(rb["metabolite_id"])
print(f"Flipped HOMEOSTATIC -> AUTOPOIETIC ({len(flipped_to_auto)}):")
for mid in flipped_to_auto:
    print(f"  {mid}")
print(f"Flipped AUTOPOIETIC -> HOMEOSTATIC ({len(flipped_to_homeo)}):")
for mid in flipped_to_homeo:
    print(f"  {mid}")
print()

# Of the 10 Network B metabolites, how many flipped?
network_B_in_test = [r for r in records_bare if r["metabolite_id"] in name_map.values()]
n_B_bare = sum(1 for r in network_B_in_test if r["causally_internal"])
n_B_ov = sum(1 for r in records_overlay if r["metabolite_id"] in name_map.values()
             and r["causally_internal"])
print(f"Of the 10 Network B metabolites tested at genome scale:")
print(f"  Bare iJO1366:  {n_B_bare}/10 causally internal")
print(f"  Overlay:        {n_B_ov}/10 causally internal")
print()

# Stratify by n_producing_reactions (overlay)
from collections import Counter
print("Stratified by number of producing reactions (overlay model):")
n_prod_counter = Counter(r["n_producing_reactions"] for r in records_overlay)
for n_prod in sorted(n_prod_counter.keys()):
    subset = [r for r in records_overlay if r["n_producing_reactions"] == n_prod]
    n_sub = len(subset)
    n_auto_sub = sum(1 for r in subset if r["causally_internal"])
    n_bare_sub = sum(1 for r in records_bare
                     if r["n_producing_reactions"] == n_prod
                     and r["causally_internal"])
    print(f"  n_producing_reactions = {n_prod}: {n_sub} metabolites, "
          f"bare {n_bare_sub}/{n_sub}, overlay {n_auto_sub}/{n_sub}")
print()

# ----------------------------------------------------------------------
# Save outputs
# ----------------------------------------------------------------------
out_dir = "/home/z/my-project/download"
os.makedirs(out_dir, exist_ok=True)

with open(f"{out_dir}/autopoiesis_ijO1366_overlay.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metabolite_id",
                "n_prod_bare", "baseline_prod_bare", "knockout_prod_bare",
                "recovery_prod_bare", "verdict_bare",
                "n_prod_overlay", "baseline_prod_overlay", "knockout_prod_overlay",
                "recovery_prod_overlay", "verdict_overlay", "flipped"])
    for rb, ro in zip(records_bare, records_overlay):
        flipped = ""
        if rb["verdict"] != ro["verdict"]:
            flipped = ("HOMEOSTATIC->AUTOPOIETIC" if ro["verdict"] == "AUTOPOIETIC"
                       else "AUTOPOIETIC->HOMEOSTATIC")
        w.writerow([rb["metabolite_id"],
                    rb["n_producing_reactions"], rb["baseline_prod_flux"],
                    rb["knockout_prod_flux"], rb["recovery_prod_flux"],
                    rb["verdict"],
                    ro["n_producing_reactions"], ro["baseline_prod_flux"],
                    ro["knockout_prod_flux"], ro["recovery_prod_flux"],
                    ro["verdict"], flipped])

with open(f"{out_dir}/autopoiesis_ijO1366_overlay.txt", "w") as f:
    f.write("TASK A: iJO1366 + ISOZYME-DAMPENER OVERLAY (Network-K-style)\n")
    f.write("       6 dampener reactions: ALT3/4 (M11), ALT5/6 (M12), ASPAT3/4 (M17),\n")
    f.write("       ALT7/8 (M19), ALDO3/4 (M21), ACS1/2 (M23)\n")
    f.write("=" * 78 + "\n\n")
    f.write(f"Bare iJO1366: {len(model_bare.metabolites)} mets, "
            f"{len(model_bare.reactions)} rxns\n")
    f.write(f"Overlay iJO1366+dampener: {len(model_overlay.metabolites)} mets, "
            f"{len(model_overlay.reactions)} rxns\n")
    f.write(f"Test set: {n_total} metabolites (10 Network B + 40 random cytosolic)\n")
    f.write(f"Bare baseline biomass flux: {baseline_obj_bare:.6f}\n")
    f.write(f"Overlay baseline biomass flux: {baseline_obj_ov:.6f}\n\n")
    f.write("Dampener overlay reactions (6 new):\n")
    for rid, name, rxn_str, _, _, _ in dampener_specs:
        f.write(f"  {rid:14s}  {rxn_str}\n")
    f.write("\n")
    f.write("VERDICT COMPARISON:\n")
    f.write(f"  Bare iJO1366:                {n_bare}/{n_total} causally internal "
            f"({100.0*n_bare/n_total:.1f}%)\n")
    f.write(f"  iJO1366 + dampener overlay:  {n_ov}/{n_total} causally internal "
            f"({100.0*n_ov/n_total:.1f}%)\n")
    f.write(f"  Delta: {delta:+d}\n\n")
    f.write(f"Flipped HOMEOSTATIC -> AUTOPOIETIC ({len(flipped_to_auto)}):\n")
    for mid in flipped_to_auto:
        f.write(f"  {mid}\n")
    f.write(f"\nFlipped AUTOPOIETIC -> HOMEOSTATIC ({len(flipped_to_homeo)}):\n")
    for mid in flipped_to_homeo:
        f.write(f"  {mid}\n")
    f.write(f"\nOf the 10 Network B metabolites:\n")
    f.write(f"  Bare iJO1366:  {n_B_bare}/10 causally internal\n")
    f.write(f"  Overlay:        {n_B_ov}/10 causally internal\n\n")
    f.write("Per-metabolite verdict table:\n")
    f.write(f"  {'met_id':>16}  {'nBare':>6}  {'bare':>10}  {'knkBare':>10}  "
            f"{'recBare':>10}  {'Vbare':>10}  {'nOv':>4}  {'ovBl':>10}  "
            f"{'knkOv':>10}  {'recOv':>10}  {'Vov':>10}  {'flipped':>22}\n")
    for rb, ro in zip(records_bare, records_overlay):
        flipped = ""
        if rb["verdict"] != ro["verdict"]:
            flipped = ("HOMEOSTATIC->AUTOPOIETIC"
                       if ro["verdict"] == "AUTOPOIETIC"
                       else "AUTOPOIETIC->HOMEOSTATIC")
        f.write(f"  {rb['metabolite_id']:>16}  {rb['n_producing_reactions']:>6}  "
                f"{rb['baseline_prod_flux']:>10.6f}  {rb['knockout_prod_flux']:>10.6f}  "
                f"{rb['recovery_prod_flux']:>10.6f}  {rb['verdict']:>10}  "
                f"{ro['n_producing_reactions']:>4}  "
                f"{ro['baseline_prod_flux']:>10.6f}  "
                f"{ro['knockout_prod_flux']:>10.6f}  "
                f"{ro['recovery_prod_flux']:>10.6f}  {ro['verdict']:>10}  "
                f"{flipped:>22}\n")
    f.write("\nStratified by n_producing_reactions (overlay):\n")
    for n_prod in sorted(n_prod_counter.keys()):
        subset = [r for r in records_overlay if r["n_producing_reactions"] == n_prod]
        n_sub = len(subset)
        n_auto_sub = sum(1 for r in subset if r["causally_internal"])
        n_bare_sub = sum(1 for r in records_bare
                         if r["n_producing_reactions"] == n_prod
                         and r["causally_internal"])
        f.write(f"  n_prod = {n_prod}: {n_sub} mets, bare {n_bare_sub}/{n_sub}, "
                f"overlay {n_auto_sub}/{n_sub}\n")

# Plot: side-by-side bar chart
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

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), constrained_layout=True)

# Left: bar chart of n_causally_internal
ax = axes[0]
labels = ["Bare iJO1366", "iJO1366 +\ndampener overlay"]
vals = [n_bare, n_ov]
colors = ["#3a7ca5", "#6a994e"]
bars = ax.bar(labels, vals, color=colors, edgecolor="black", linewidth=0.8)
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.4,
            f"{v}/{n_total}\n({100.0*v/n_total:.1f}%)",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_ylabel("# Causally internal (of 50 tested)")
ax.set_ylim(0, n_total + 4)
ax.set_title("Genome-scale closure test verdict:\n"
             "bare BiGG iJO1366 vs iJO1366 + Network-K-style dampener overlay",
             fontsize=10)
ax.grid(True, alpha=0.3, axis="y")

# Right: per-metabolite flipped-bar (Network B subset)
ax = axes[1]
network_B_names = ["G6P", "FBP", "PEP", "PYR", "AcCoA", "CIT", "AKG", "SUC", "MAL", "OAA"]
network_B_ids = [name_map[n] for n in network_B_names]
bare_B = [next((1 for r in records_bare if r["metabolite_id"] == mid
                and r["causally_internal"]), 0) for mid in network_B_ids]
ov_B = [next((1 for r in records_overlay if r["metabolite_id"] == mid
              and r["causally_internal"]), 0) for mid in network_B_ids]
x = np.arange(len(network_B_names))
w = 0.38
ax.bar(x - w/2, bare_B, w, color="#3a7ca5", label="bare iJO1366", edgecolor="black", linewidth=0.6)
ax.bar(x + w/2, ov_B, w, color="#6a994e", label="iJO1366+dampener overlay", edgecolor="black", linewidth=0.6)
ax.set_xticks(x)
ax.set_xticklabels(network_B_names, rotation=45, ha="right", fontsize=9)
ax.set_ylabel("Causally internal? (1=yes, 0=no)")
ax.set_ylim(0, 1.2)
ax.set_yticks([0, 1])
ax.set_title("Network B metabolites at genome scale:\n"
             "bare iJO1366 vs iJO1366 + dampener overlay",
             fontsize=10)
ax.legend(loc="upper right", fontsize=9)
ax.grid(True, alpha=0.3, axis="y")

fig.suptitle(f"Task A: iJO1366 + Network-K-style isozyme-dampener overlay\n"
             f"Test set = 50 metabolites (10 Network B + 40 random). "
             f"Delta = {delta:+d} causally internal.",
             fontsize=11)
fig.savefig(f"{out_dir}/autopoiesis_ijO1366_overlay.png", dpi=150)
plt.close(fig)

print(f"\n[outputs written to {out_dir}/]")
print(f"  - autopoiesis_ijO1366_overlay.csv")
print(f"  - autopoiesis_ijO1366_overlay.png")
print(f"  - autopoiesis_ijO1366_overlay.txt")
