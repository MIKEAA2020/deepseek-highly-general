"""Trace FBP, G6P, PEP, PYR recovery trajectories in Network I to understand
the FBP limit cycle and design a targeted dampener."""
import os, copy

with open("/home/z/my-project/scripts/autopoiesis_network_I.py") as f:
    src = f.read()
cut_marker = 'print("=" * 78)\nprint("NETWORK I'
cut_idx = src.find(cut_marker)
ns = {}
exec(compile(src[:cut_idx], "neti_mod.py", "exec"), ns)
simulate_network = ns["simulate_network"]
simulate_network_recover = ns["simulate_network_recover"]
network_I = ns["network_I"]

T = 500
m_j = "FBP"
knock = simulate_network(network_I, knockout_species=m_j, T=T)
recover_init = knock[T // 2]
recover = simulate_network_recover(network_I, init=recover_init, T=T - T // 2)

print("Network I FBP KO + recovery trajectory:")
print(f"  At recovery start (T=250 of KO):")
for s in ["FBP", "G6P", "PEP", "PYR", "PFK1", "PFK2", "ALDO1", "ALDO2", "Glycogen"]:
    print(f"    {s:<10} = {recover_init.get(s, 0):.4f}")
print(f"\n  Recovery trajectory at every 25 steps:")
print(f"    {'step':<6}{'FBP':<10}{'G6P':<10}{'PEP':<10}{'PYR':<10}{'PFK1':<10}{'ALDO1':<10}{'Glycogen':<10}")
for i in list(range(0, 251, 25)) + [249, 250]:
    if i < len(recover):
        t = recover[i]
        print(f"    {i:<6}{t['FBP']:<10.3f}{t['G6P']:<10.3f}{t['PEP']:<10.3f}{t['PYR']:<10.3f}{t['PFK1']:<10.3f}{t['ALDO1']:<10.3f}{t['Glycogen']:<10.3f}")
