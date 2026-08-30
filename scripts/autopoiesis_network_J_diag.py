"""Identify the lone Phase I failure in the best Network J configs."""
import os, copy, importlib.util

with open("/home/z/my-project/scripts/autopoiesis_network_J.py") as f:
    src = f.read()
cut_marker = 'print("=" * 78)\nprint("NETWORK J'
cut_idx = src.find(cut_marker)
ns = {}
exec(compile(src[:cut_idx], "netj_mod.py", "exec"), ns)
closure_test = ns["closure_test"]
network_J_template = ns["network_J"]

configs = [
    ("amp4x", 1.0),
    ("amp4x", 1.5),
    ("amp2x", 1.0),
    ("amp2x", 1.5),
    ("neutral", 1.0),
    ("neutral", 1.5),
    ("amp1x", 1.5),
]
for stoich_mode, k_cat in configs:
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
    records, baseline = closure_test(net, f"J-{stoich_mode}-k{k_cat}", T=500)
    n_auto = sum(1 for r in records if r["causally_internal"])
    fails = [r for r in records if not r["causally_internal"]]
    print(f"=== stoich={stoich_mode} k_cat={k_cat} ===  {n_auto}/{len(records)}")
    for r in fails:
        print(f"  FAIL {r['component']:<10}  baseline={r['baseline_conc']:.4f}  "
              f"knock_final={r['knockout_conc_final']:.4f}  recover_final={r['recover_conc_final']:.4f}  "
              f"knock_ok={r['knockout_success']}  recover_ok={r['recover_success']}")
