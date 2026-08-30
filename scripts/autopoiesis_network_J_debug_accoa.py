"""Debug AcCoA failure: run closure_test's exact path, print full trajectory."""
import os, copy, numpy as np

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

# Closure test for AcCoA exactly as closure_test does it
T = 500
m_j = "AcCoA"
print(f"Debug closure_test for {m_j} (amp2x k=1.0):")
knock = simulate_network(net, knockout_species=m_j, T=T)
knock_final = knock[-1]
print(f"  knock_final[{m_j}] = {knock_final[m_j]:.4f}")
print(f"  knock[250][AcCoA] = {knock[250]['AcCoA']:.4f}")
print(f"  knock[250][PYR]   = {knock[250]['PYR']:.4f}")
print(f"  knock[250][NAD+]   = {knock[250]['NAD+']:.4f}")
print(f"  knock[250][ATP]   = {knock[250]['ATP']:.4f}")
print(f"  knock[250][PDH1]  = {knock[250]['PDH1']:.4f}")
print(f"  knock[250][ALA]   = {knock[250]['ALA']:.4f}")
print(f"  knock[250][ASP]   = {knock[250]['ASP']:.4f}")
print(f"  knock[250][OAA]   = {knock[250]['OAA']:.4f}")
recover_start_idx = T // 2
recover_init = knock[recover_start_idx]
print(f"  recover_init[AcCoA] = {recover_init['AcCoA']:.4f}")
recover = simulate_network_recover(net, init=recover_init, T=T - recover_start_idx)
recover_final = recover[-1]
print(f"  recover_final[AcCoA] = {recover_final[m_j]:.4f}")
print(f"  recover_final has {len(recover)} entries (T+1)")
print(f"  recover trajectory for AcCoA at every 25 steps + last 5:")
for i in list(range(0, 251, 25)) + [245, 246, 247, 248, 249, 250]:
    if i < len(recover):
        print(f"    step {i}: AcCoA={recover[i]['AcCoA']:.4f}  PYR={recover[i]['PYR']:.4f}  "
              f"NAD+={recover[i]['NAD+']:.4f}  PDH1={recover[i]['PDH1']:.4f}  "
              f"ATP={recover[i]['ATP']:.4f}  ASP={recover[i]['ASP']:.4f}")
