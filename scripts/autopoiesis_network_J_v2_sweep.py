"""
Network J v2 -- extend Network I with FBP1/FBP2 (fructose-bisphosphatase
isozymes, EC 3.1.3.11, with alpha-KG+GLU-based SYNTHESIS analogous to
ASPAT3/4/ALT7/8) to dampen the FBP limit-cycle of Network I via a
one-way drain.

DESIGN RATIONALE:
  The M21/M22 reversible aldolase approach (Network J v1) creates an
  amplification feedback loop (FBP ⇌ DHAP+G3P with mass-doubling) that
  saturates the glycolysis backbone (FBP, PYR, OAA all reach max_conc=100)
  and creates new limit cycles in PYR and AcCoA. The user's alternative
  suggestion -- a fructose-bisphosphatase backup -- is a ONE-WAY drain
  on FBP that does NOT create amplification feedback.

  FBP1/FBP2 -- fructose-bisphosphatase isozymes (EC 3.1.3.11) catalyze
  the one-way hydrolysis
    D-fructose-1,6-bisphosphate + H2O -> D-fructose-6-phosphate + Pi
    FBP -> F6P + Pi
  In this simplified network (skipping the F6P intermediate of real
  biochemistry, since M2 PFK already simplifies F6P -> G6P), the reaction
  becomes:
    M21a/b:  FBP -> G6P + Pi   (FBP1 / FBP2; one-way drain)
  The stoichiometry {FBP: -2, G6P: 1, Pi: 1} is MASS-NEUTRAL with
  M2 PFK's {G6P: -1, FBP: 2}: 1 M2 + 1 M21 = net zero, no amplification.

  The one-way drain fires when FBP is HIGH (above Km=0.1), draining FBP
  back to G6P. This dampens the FBP HIGH phase (peak) of the limit cycle,
  preventing the overshoot that would otherwise swing back to a severe
  LOW phase (trough). With reduced oscillation amplitude, the endpoint
  of the recovery window is more likely to catch FBP above the viability
  threshold (Phase I PASS).

  KEY design choice: the FBP1/2 SYNTHESIS (E21a/E21b) uses alpha-KG as
  inducer (food, always supplied) and GLU as amino-acid substrate,
  analogous to ASPAT3/4 (E17a/b) and ALT7/8 (E19a/b):
    E21:  GLU + alpha-KG + ATP -> FBP1/FBP2 + ADP + 2 Pi
  Critically, the synthesis does NOT use FBP as substrate or inducer,
  so FBP1/2 stay at high level during FBP knockout. At recovery, M21
  fires (using available FBP) to drain FBP overshoot back to G6P, which
  then re-enters M2 PFK to be re-phosphorylated to FBP. This forms a
  futile-cycle FBP → G6P → FBP that buffers FBP against large swings.

  k_cat for M21: TUNED to break the FBP limit-cycle without disturbing
  the G6P/PEP/PYR equilibrium. Sweeping 0.1, 0.2, 0.3, 0.5, 1.0, 1.5.

  Total Network J v2: 59 species (11 food + 48 non-food), 80 reactions
  (76 Network I + 4 new: M21a/M21b + E21a/E21b).
  New non-food: 48 = 46 Network I + FBP1 + FBP2.
"""
import numpy as np, os, csv, copy

with open("/home/z/my-project/scripts/autopoiesis_network_J.py") as f:
    src = f.read()
cut_marker = 'print("=" * 78)\nprint("NETWORK J'
cut_idx = src.find(cut_marker)
ns = {}
exec(compile(src[:cut_idx], "netj_mod.py", "exec"), ns)
simulate_network = ns["simulate_network"]
simulate_network_recover = ns["simulate_network_recover"]
closure_test = ns["closure_test"]
network_J_template = ns["network_J"]

# Build Network J v2 (FBPase one-way drain)
def build_net_v2(k_cat_m21):
    net = copy.deepcopy(network_J_template)
    # Remove the v1 ALDO3/ALDO4 reactions (M21a/b, M22a/b, E21a/b) — replace with FBP1/2
    net["reactions"] = [r for r in net["reactions"]
                        if not r["id"].startswith("M21") and
                           not r["id"].startswith("M22") and
                           not r["id"].startswith("E21")]
    # Remove DHAP/G3P/ALDO3/ALDO4 species
    net["species"] = [s for s in net["species"]
                      if s not in ("DHAP", "G3P", "ALDO3", "ALDO4")]
    net["non_food"] = [s for s in net["non_food"]
                       if s not in ("DHAP", "G3P", "ALDO3", "ALDO4")]
    # Add FBP1, FBP2 to species
    net["species"].extend(["FBP1", "FBP2"])
    net["non_food"].extend(["FBP1", "FBP2"])
    # Add new reactions: M21a/b (FBP -> G6P + Pi, one-way drain), E21a/b (synthesis)
    new_rxns = [
        # M21a, M21b: FBP -> G6P + Pi (FBP1 / FBP2; fructose-bisphosphatase, EC 3.1.3.11)
        # MASS-NEUTRAL with M2 PFK: 1 M2 (G6P→2FBP) + 1 M21 (2FBP→G6P) = net 0
        {"id": "M21a", "stoich": {"FBP": -2, "G6P": 1, "Pi": 1},
         "catalyst": "FBP1", "kind": "metabolic", "k_cat_override": k_cat_m21},
        {"id": "M21b", "stoich": {"FBP": -2, "G6P": 1, "Pi": 1},
         "catalyst": "FBP2", "kind": "metabolic", "k_cat_override": k_cat_m21},
        # E21a, E21b: FBP1/FBP2 synthesis -- alpha-KG + GLU based (NOT FBP-based)
        # (analogous to ASPAT3/4's E17a/b and ALT7/8's E19a/b)
        {"id": "E21a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1,
                                  "FBP1": 1, "ADP": 2, "Pi": 2},
         "catalyst": "TF", "kind": "synthesis"},
        {"id": "E21b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1,
                                  "FBP2": 1, "ADP": 2, "Pi": 2},
         "catalyst": "TF", "kind": "synthesis"},
    ]
    net["reactions"].extend(new_rxns)
    return net

print("NETWORK J v2 (FBPase one-way drain) -- sweep k_cat for M21a/b")
print(f"  Total species: {len(build_net_v2(0.5)['species'])}, "
      f"reactions: {len(build_net_v2(0.5)['reactions'])}")
print()
print(f"  {'k_cat':<6} {'Phase I':<10} {'FBP base':<10} {'FBP rec':<10} {'FBP pass':<10} "
      f"{'PYR base':<10} {'PYR rec':<10} {'PYR pass':<10} "
      f"{'AcCoA base':<10} {'AcCoA rec':<10} {'AcCoA pass':<10}")
best = None
for k_cat in [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
    net = build_net_v2(k_cat)
    records, baseline = closure_test(net, f"J-v2-k{k_cat}", T=500)
    n_auto = sum(1 for r in records if r["causally_internal"])
    n_tot = len(records)
    fbp = next((r for r in records if r["component"] == "FBP"), None)
    pyr = next((r for r in records if r["component"] == "PYR"), None)
    acc = next((r for r in records if r["component"] == "AcCoA"), None)
    fails = [r["component"] for r in records if not r["causally_internal"]]
    print(f"  {k_cat:<6} {n_auto}/{n_tot:<8} "
          f"{fbp['baseline_conc']:<10.3f} {fbp['recover_conc_final']:<10.3f} {str(fbp['causally_internal']):<10} "
          f"{pyr['baseline_conc']:<10.3f} {pyr['recover_conc_final']:<10.3f} {str(pyr['causally_internal']):<10} "
          f"{acc['baseline_conc']:<10.3f} {acc['recover_conc_final']:<10.3f} {str(acc['causally_internal']):<10} "
          f"fails={fails}")
    if best is None or n_auto > best[1]:
        best = (k_cat, n_auto, fails)

print(f"\nBest: k_cat={best[0]} -> {best[1]}/50, fails={best[2]}")
