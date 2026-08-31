"""Detailed diagnostic for amp2x k=1.0 — check all metabolic baselines."""
import os, copy

with open("/home/z/my-project/scripts/autopoiesis_network_J.py") as f:
    src = f.read()
cut_marker = 'print("=" * 78)\nprint("NETWORK J'
cut_idx = src.find(cut_marker)
ns = {}
exec(compile(src[:cut_idx], "netj_mod.py", "exec"), ns)
simulate_network = ns["simulate_network"]
simulate_network_recover = ns["simulate_network_recover"]
network_J_template = ns["network_J"]

# amp2x, k=1.0
net = copy.deepcopy(network_J_template)
for r in net["reactions"]:
    if r["id"] in ("M21a", "M21b"):
        r["k_cat_override"] = 1.0
    elif r["id"] in ("M22a", "M22b"):
        r["k_cat_override"] = 1.0
        r["stoich"] = {"DHAP": -2, "G3P": -2, "FBP": 2}

baseline = simulate_network(net, knockout_species=None, T=500)
baseline_final = baseline[-1]
print("amp2x k=1.0 BASELINE:")
print(f"  {'Species':<12} {'Baseline':<12}")
for s in net["species"]:
    print(f"  {s:<12} {baseline_final[s]:<12.4f}")

# Now AcCoA knockout/recovery trajectory
print("\nAcCoA KO + recovery trajectory (first 100 / last 100 steps of recovery):")
knock = simulate_network(net, knockout_species="AcCoA", T=500)
recover_init = knock[250]
print(f"  At recovery start (T=250 of KO):")
for s in ["AcCoA", "PYR", "NAD+", "PDH1", "PDH2", "ALA", "ASP", "ATP", "OAA", "PEP", "FBP"]:
    print(f"    {s:<10} = {recover_init.get(s, 0):.4f}")
recover = simulate_network_recover(net, init=recover_init, T=250)
print(f"  Recovery trajectory (key species at every 25 steps):")
print(f"    {'step':<6}{'AcCoA':<10}{'PDH1':<10}{'PDH2':<10}{'PYR':<10}{'ALA':<10}{'ASP':<10}{'PEP':<10}{'FBP':<10}{'GLU':<10}{'OAA':<10}")
for i in [0, 25, 50, 100, 150, 200, 249]:
    t = recover[i]
    print(f"    {i:<6}{t['AcCoA']:<10.3f}{t['PDH1']:<10.3f}{t['PDH2']:<10.3f}{t['PYR']:<10.3f}{t['ALA']:<10.3f}{t['ASP']:<10.3f}{t['PEP']:<10.3f}{t['FBP']:<10.3f}{t['GLU']:<10.3f}{t['OAA']:<10.3f}")
