"""
Sweep k_cat and M22-reverse stoichiometry for Network J dampener to find
the configuration that achieves 50/50 = 100% Phase I closure (FBP
dampened, no new PYR limit cycle).

Sweep:
  - M21/M22 k_cat: 0.1, 0.2, 0.3, 0.5, 1.0, 1.5
  - M22 reverse stoichiometry:
      "amp4x":  {"DHAP": -1, "G3P": -1, "FBP": 2}   -- 4x amplification (current default)
      "amp2x":  {"DHAP": -2, "G3P": -2, "FBP": 2}   -- 2x amplification (matches M19/M20 pattern in Network I)
      "neutral":{"DHAP": -2, "G3P": -2, "FBP": 1}   -- neutral (no amplification)
      "amp1x":  {"DHAP": -1, "G3P": -1, "FBP": 1}   -- no doubling (no amplification)
"""
import sys, os, importlib.util, itertools, copy, csv
import numpy as np

# Load Network J module dynamically
spec = importlib.util.spec_from_file_location(
    "netj_mod", "/home/z/my-project/scripts/autopoiesis_network_J.py"
)
# Pre-import the script as a module (suppress its main execution via env flag)
os.environ["NETJ_SWEEP"] = "1"
mod = importlib.util.module_from_spec(spec)
# We need to prevent the script from running its closure test on import.
# Hack: read the source, strip the bottom execution block, exec into a namespace.
with open("/home/z/my-project/scripts/autopoiesis_network_J.py") as f:
    src = f.read()
# Cut at the "print(" line that starts the main execution
cut_marker = 'print("=" * 78)\nprint("NETWORK J'
cut_idx = src.find(cut_marker)
assert cut_idx > 0, "cut marker not found"
ns = {}
exec(compile(src[:cut_idx], "netj_mod.py", "exec"), ns)

simulate_network = ns["simulate_network"]
simulate_network_recover = ns["simulate_network_recover"]
closure_test = ns["closure_test"]
network_J_template = ns["network_J"]

sweep = []
for stoich_mode in ["amp4x", "amp2x", "neutral", "amp1x"]:
    for k_cat in [0.1, 0.2, 0.3, 0.5, 1.0, 1.5]:
        # Build a fresh network with custom M22 stoichiometry and k_cat
        net = copy.deepcopy(network_J_template)
        for r in net["reactions"]:
            if r["id"] in ("M21a", "M21b"):
                r["k_cat_override"] = k_cat
            elif r["id"] in ("M22a", "M22b"):
                r["k_cat_override"] = k_cat
                if stoich_mode == "amp4x":
                    r["stoich"] = {"DHAP": -1, "G3P": -1, "FBP": 2}
                elif stoich_mode == "amp2x":
                    r["stoich"] = {"DHAP": -2, "G3P": -2, "FBP": 2}
                elif stoich_mode == "neutral":
                    r["stoich"] = {"DHAP": -2, "G3P": -2, "FBP": 1}
                elif stoich_mode == "amp1x":
                    r["stoich"] = {"DHAP": -1, "G3P": -1, "FBP": 1}
        # Quick Phase I closure test (skip Phase III for speed)
        records, baseline = closure_test(net, f"J-{stoich_mode}-k{k_cat}", T=500)
        n_auto = sum(1 for r in records if r["causally_internal"])
        n_tot = len(records)
        # Find FBP and PYR rows
        fbp = next((r for r in records if r["component"] == "FBP"), None)
        pyr = next((r for r in records if r["component"] == "PYR"), None)
        sweep.append({
            "stoich_mode": stoich_mode,
            "k_cat": k_cat,
            "n_auto": n_auto,
            "n_tot": n_tot,
            "fbp_baseline": fbp["baseline_conc"] if fbp else None,
            "fbp_recover": fbp["recover_conc_final"] if fbp else None,
            "fbp_pass": fbp["causally_internal"] if fbp else None,
            "pyr_baseline": pyr["baseline_conc"] if pyr else None,
            "pyr_recover": pyr["recover_conc_final"] if pyr else None,
            "pyr_pass": pyr["causally_internal"] if pyr else None,
        })
        print(f"  stoich={stoich_mode:<8s} k_cat={k_cat:.2f}  Phase I = {n_auto}/{n_tot}  "
              f"FBP(baseline={fbp['baseline_conc']:.3f}, recover={fbp['recover_conc_final']:.3f}, pass={fbp['causally_internal']})  "
              f"PYR(baseline={pyr['baseline_conc']:.3f}, recover={pyr['recover_conc_final']:.3f}, pass={pyr['causally_internal']})")

# Save CSV
with open("/home/z/my-project/download/autopoiesis_network_J_sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sweep[0].keys()))
    w.writeheader()
    w.writerows(sweep)

print("\nBest candidates (n_auto == n_tot, or highest n_auto):")
best = max(sweep, key=lambda r: r["n_auto"])
print(f"  Best: stoich={best['stoich_mode']} k_cat={best['k_cat']} -> {best['n_auto']}/{best['n_tot']}")
print("  FBP:", best["fbp_pass"], "PYR:", best["pyr_pass"])
