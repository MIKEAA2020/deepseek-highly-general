#!/usr/bin/env python3
"""E23 probe 3: lock the endogenous-activation designs.

Questions:
  A. unlimited nitrate -> endogenous NO3R1pp trajectory?
  B. trehalose as sole carbon -> endogenous TREHpp / TRE6PP shares?
  C. proline as sole N source (+putP KO) -> PROabcpp endogenous?
     (check pro__L routes, proline->glutamate catabolism)
  D. P-limited + glyc2p as sole P -> GLYC2Pabcpp endogenous + varying?
     (check no other default-medium P source)
  E. QMO2/QMO3 equations + can their flux be forced under aerobic glucose?
  F. carnitine dead-end: consumers of crncoa/ctbtcoa/crnDcoa?
  G. metsox transport chain e -> p -> c reactions + GPRs
  H. PROt/PROt2pp/PROt4pp GPRs (which to KO)
  I. glyb secretion route (for choline->glyb bypass check)
"""
import warnings
warnings.filterwarnings("ignore")
from cobra.io import load_model
from cobra import Reaction

model = load_model("iJO1366")
q_glc = [5.0, 1.0]
q_O2 = [22.0, 5.0]

print("A/B/C/E extra reaction equations")
for rid in ("QMO2", "QMO3", "PRODH", "PROD2", "PRO2x", "P5CDr", "P5CDH",
            "GPDDA1", "CHOLD", "BETALDHy", "METOX1s", "METOX2s"):
    try:
        r = model.reactions.get_by_id(rid)
        print(f"  {rid:10s} {r.reaction[:70]} | {(str(r.gpr) or '-')[:36]}")
    except KeyError:
        print(f"  {rid:10s} NOT FOUND")

print("\nC. proline routes (e->p->c) + catabolism")
for mid in ("pro__L_e", "pro__L_p", "pro__L_c"):
    print(f"  --- {mid}")
    for r in model.metabolites.get_by_id(mid).reactions:
        print(f"    {r.id:12s} {r.reaction[:58]} | {(str(r.gpr) or '-')[:30]}")

print("\nG. metsox transport chain")
for mid in ("metsox_S__L_e", "metsox_S__L_p", "metsox_S__L_c"):
    try:
        m = model.metabolites.get_by_id(mid)
        print(f"  --- {mid}")
        for r in m.reactions:
            print(f"    {r.id:16s} {r.reaction[:56]} | {(str(r.gpr) or '-')[:26]}")
    except KeyError:
        print(f"  {mid} NOT FOUND")

print("\nF. carnitine CoA-ester consumers (caiC dead-end?)")
for mid in ("crncoa_c", "ctbtcoa_c", "crnDcoa_c"):
    try:
        m = model.metabolites.get_by_id(mid)
        print(f"  --- {mid}")
        for r in m.reactions:
            print(f"    {r.id:12s} {r.reaction[:64]}")
    except KeyError:
        print(f"  {mid} NOT FOUND")

print("\nD. default medium (P-containing sources?)")
med = model.medium
for k, v in sorted(med.items()):
    if v < 0:
        print(f"    {k:24s} {v}")

print("\n=== CONDITION PROBES (T1 q=5 / T2 q=1) ===")

def run(name, setup, targets, ti):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
        model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
        try:
            setup(model, ti)
            sol = model.optimize()
            if sol.status != "optimal":
                print(f"  [{name} T{ti+1}] status={sol.status}")
                return
            vals = {r: round(float(sol.fluxes[r]), 4)
                    for r in targets if r in sol.fluxes.index}
            print(f"  [{name} T{ti+1}] mu={sol.objective_value:.4f}  "
                  + "  ".join(f"{k}={v}" for k, v in vals.items()))
        except Exception as e:
            print(f"  [{name} T{ti+1}] ERROR: {type(e).__name__}: {e}")

# A. anaerobic, UNLIMITED nitrate
def setup_an(m, ti):
    m.reactions.EX_o2_e.lower_bound = 0.0
    m.reactions.EX_no3_e.lower_bound = -1000.0
for ti in (0, 1):
    run("anaer-NO3unlim", setup_an, ["NO3R1pp", "NO3R2pp", "NO3t7pp"], ti)

# B. trehalose as sole carbon
def setup_tre(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_tre_e.lower_bound = -q_glc[ti]
for ti in (0, 1):
    run("trehalose-C", setup_tre,
        ["TREtex", "TREptspp", "TREHpp", "TRE6PP", "TRE6PH", "TRE6PS", "TREH"], ti)

# C. proline as sole N source, putP KO
def setup_proN(m, ti):
    m.reactions.EX_nh4_e.lower_bound = 0.0
    m.reactions.EX_pro__L_e.lower_bound = -1000.0
    for gid in ("b3491",):   # putP
        try:
            m.genes.get_by_id(gid).knock_out()
        except Exception as e:
            print("  putP KO failed:", e)
for ti in (0, 1):
    run("proline-N +putPko", setup_proN,
        ["PROabcpp", "PROt2pp", "PROt4pp", "PROtex", "PRODH", "PROD2", "P5CDr"], ti)

# D. glycerol carbon + P limitation with glyc2p as sole P
def setup_plim(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_glyc_e.lower_bound = -q_glc[ti]
    m.reactions.EX_pi_e.lower_bound = 0.0
    m.reactions.EX_glyc2p_e.lower_bound = -1000.0
for ti in (0, 1):
    run("glyc+Plim", setup_plim,
        ["GLYC2Pabcpp", "GLYC2Ptex", "G2PP", "GLYC3Pabcpp", "EX_glyc2p_e"], ti)

# E. forced QMO2 leak under aerobic glucose (feasibility)
def setup_leak(m, ti):
    r = m.reactions.QMO2
    r.bounds = (0.05 * q_glc[ti], 0.05 * q_glc[ti])
for ti in (0, 1):
    run("QMO2-leak", setup_leak, ["QMO2", "QMO3", "SPODM", "CAT"], ti)

# I. osmotic retention with scaled demands (variation check)
def setup_osmo(m, ti):
    m.reactions.EX_tre_e.lower_bound = -1.0
    for mid, f in [("glyb_c", 0.05), ("pro__L_c", 0.05), ("tre_c", 0.10)]:
        dm = Reaction("DM_" + mid[:4])
        m.add_reactions([dm])
        dm.add_metabolites({m.metabolites.get_by_id(mid): -1.0})
        dm.bounds = (f * q_glc[ti], f * q_glc[ti])
    m.reactions.EX_glyb_e.lower_bound = -1.0
    m.reactions.EX_pro__L_e.lower_bound = -1.0
for ti in (0, 1):
    run("osmo-scaled", setup_osmo,
        ["TRE6PP", "TREHpp", "GLYBabcpp", "PROabcpp", "GLYBtex", "PROtex",
         "GLYBt2pp"], ti)

print("\nDONE (probe 3)")
