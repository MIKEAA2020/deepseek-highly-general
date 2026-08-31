"""Run Network J at amp4x k=1.0 with full Phase III check."""
import os, copy

with open("/home/z/my-project/scripts/autopoiesis_network_J.py") as f:
    src = f.read()
cut_marker = 'print("=" * 78)\nprint("NETWORK J'
cut_idx = src.find(cut_marker)
ns = {}
exec(compile(src[:cut_idx], "netj_mod.py", "exec"), ns)
simulate_network = ns["simulate_network"]
simulate_network_recover = ns["simulate_network_recover"]
closure_test = ns["closure_test"]
phase_iii_verdict = ns["phase_iii_verdict"]
network_J_template = ns["network_J"]

for stoich_mode, k_cat in [("amp4x", 1.0), ("amp4x", 1.5), ("amp2x", 1.5), ("amp2x", 0.5)]:
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
    records, baseline = closure_test(net, f"J-{stoich_mode}-k{k_cat}", T=500)
    n_auto = sum(1 for r in records if r["causally_internal"])
    fails = [r for r in records if not r["causally_internal"]]
    print(f"=== stoich={stoich_mode} k_cat={k_cat} ===  Phase I = {n_auto}/{len(records)}")
    n_p3 = n_auto
    for r in fails:
        p3 = phase_iii_verdict(net, r["component"], T=500)
        print(f"  FAIL {r['component']:<10}  Phase I FAIL, pathwise={'PASS' if p3['pathwise_pass'] else 'FAIL'} "
              f"(frac={p3['recovery_traj_above_frac']:.3f}, mean={p3['recovery_traj_mean']:.3f}), "
              f"contractible={'PASS' if p3['contractible_pass'] else 'FAIL'} -> Phase III={'PASS' if p3['phase_iii_pass'] else 'FAIL'}")
        if p3["phase_iii_pass"]:
            n_p3 += 1
    print(f"  Phase III = {n_p3}/{len(records)} = {100.0*n_p3/len(records):.1f}%")
    print()
