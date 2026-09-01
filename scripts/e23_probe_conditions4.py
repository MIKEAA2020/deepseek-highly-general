#!/usr/bin/env python3
"""E23 probe 4: debug the glyc2p runaway loop + QMO2 infeasibility."""
import warnings
warnings.filterwarnings("ignore")
from cobra.io import load_model

model = load_model("iJO1366")

print("1. ALL reactions containing glyc2p")
for r in model.reactions:
    if "glyc2p" in r.reaction:
        print(f"  {r.id:16s} {r.reaction[:72]} | bounds={r.bounds} | {(str(r.gpr) or '-')[:28]}")

print("\n2. GLYBt2pp / PROt2rpp / PROt4pp GPRs (proP/putP identification)")
for rid in ("GLYBt2pp", "PROt2rpp", "PROt4pp", "GLYBtex", "PROtex"):
    r = model.reactions.get_by_id(rid)
    print(f"  {rid:12s} {r.reaction[:50]} | {str(r.gpr) or '-'}")

print("\n3. QMO2/QMO3 bounds + GPR")
for rid in ("QMO2", "QMO3", "SPODM", "CAT", "MOX", "FESD1s"):
    r = model.reactions.get_by_id(rid)
    print(f"  {rid:10s} bounds={r.bounds} | {r.reaction[:56]} | {(str(r.gpr) or '-')}")

print("\n4. QMO2 forced tiny leak test")
for f in (1e-4, 1e-3, 0.01):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -5.0
        model.reactions.EX_o2_e.lower_bound = -22.0
        model.reactions.QMO2.bounds = (f, f)
        sol = model.optimize()
        print(f"  QMO2={f}: status={sol.status}, mu={sol.objective_value}")

print("\n5. Default medium")
for k, v in sorted(model.medium.items()):
    print(f"  {k:24s} {v}")

print("\n6. glyc2p runaway debug: fluxes of all glyc2p reactions")
with model:
    model.reactions.EX_glc__D_e.lower_bound = 0.0
    model.reactions.EX_glyc_e.lower_bound = -5.0
    model.reactions.EX_pi_e.lower_bound = 0.0
    model.reactions.EX_glyc2p_e.lower_bound = -1000.0
    sol = model.optimize()
    print(f"  status={sol.status} mu={sol.objective_value}")
    for r in model.reactions:
        if "glyc2p" in r.reaction:
            print(f"  {r.id:16s} flux={sol.fluxes[r.id]:10.3f}")

print("\n7. P-limited WITHOUT glycerol (glucose carbon), glyc2p sole P, capped")
for cap in (0.2, 0.5, 1.0, 2.0, 1000.0):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -5.0
        model.reactions.EX_o2_e.lower_bound = -22.0
        model.reactions.EX_pi_e.lower_bound = 0.0
        model.reactions.EX_glyc2p_e.lower_bound = -cap
        sol = model.optimize()
        if sol.status == "optimal":
            print(f"  cap={cap:8}: mu={sol.objective_value:.4f} "
                  f"GLYC2Pabcpp={sol.fluxes['GLYC2Pabcpp']:.4f} "
                  f"EX={sol.fluxes['EX_glyc2p_e']:.3f}")
        else:
            print(f"  cap={cap:8}: {sol.status}")

print("\nDONE (probe 4)")
