#!/usr/bin/env python3
"""E23 probe 2: close the remaining design questions."""
import warnings
warnings.filterwarnings("ignore")
from cobra.io import load_model
from cobra import Reaction

model = load_model("iJO1366")
q_glc = [5.0, 1.0]
q_O2 = [22.0, 5.0]

print("=" * 78)
print("1. h2o2_c full reaction list (catalase present?)")
print("=" * 78)
for r in model.metabolites.h2o2_c.reactions:
    print(f"  {r.id:14s} {r.reaction[:64]} | {(str(r.gpr) or '-')[:40]}")

print()
print("=" * 78)
print("2. trdrd_c / trdox_c full lists (thioredoxin reductase present?)")
print("=" * 78)
for mid in ("trdrd_c", "trdox_c"):
    print(f"  --- {mid}")
    for r in model.metabolites.get_by_id(mid).reactions:
        print(f"  {r.id:14s} {r.reaction[:64]}")

print()
print("=" * 78)
print("3. g3ps_c / g3ps_p / g3ps_e reactions")
print("=" * 78)
for mid in ("g3ps_c", "g3ps_p", "g3ps_e"):
    print(f"  --- {mid}")
    for r in model.metabolites.get_by_id(mid).reactions:
        print(f"  {r.id:14s} {r.reaction[:64]}")

print()
print("=" * 78)
print("4. o2s_e / metsox exchanges and carnitine set")
print("=" * 78)
for rid in ("EX_o2s_e", "EX_metsox_S__L_e", "EX_metsox_R__L_e", "EX_crn_e",
            "EX_glyb_e", "EX_chol_e", "EX_pro__L_e", "EX_pi_e", "EX_tre_e",
            "EX_g3ps_e"):
    r = model.reactions.get_by_id(rid)
    print(f"  {rid:20s} bounds={r.bounds}  {r.reaction[:40]}")

print()
print("=" * 78)
print("5. CONDITIONS (T1 q_glc=5 / T8 q_glc=1)")
print("=" * 78)

def run(name, setup, targets, ti):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
        model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
        try:
            setup(model)
            sol = model.optimize()
            if sol.status != "optimal":
                print(f"  [{name} T{ti+1}] status={sol.status}")
                return
            vals = {r: round(float(sol.fluxes[r]), 3)
                    for r in targets if r in sol.fluxes.index}
            print(f"  [{name} T{ti+1}] mu={sol.objective_value:.4f}  "
                  + "  ".join(f"{k}={v}" for k, v in vals.items()))
        except Exception as e:
            print(f"  [{name} T{ti+1}] ERROR: {type(e).__name__}: {e}")

# --- 5a. oxidative: superoxide + metsox-S/R import
def setup_oxid(m):
    m.reactions.EX_o2s_e.lower_bound = -1.0
    m.reactions.EX_metsox_S__L_e.lower_bound = -0.5
    m.reactions.EX_metsox_R__L_e.lower_bound = -0.5
OX = ["SPODM", "SPODMpp", "THIORDXi", "METSOXR1", "METSOXR2", "CAT",
      "TRSR", "DSBDR"]
for ti in (0, 1):
    run("oxid", setup_oxid, OX, ti)

# --- 5b. osmotic: osmoprotectant import + retention demands
def setup_osmo(m):
    m.reactions.EX_glyb_e.lower_bound = -0.5
    m.reactions.EX_chol_e.lower_bound = -0.5
    m.reactions.EX_pro__L_e.lower_bound = -0.5
    m.reactions.EX_crn_e.lower_bound = -0.5
    m.reactions.EX_tre_e.lower_bound = -1.0
    for mid, rid in [("glyb_c", "DM_glyb"), ("pro__L_c", "DM_pro"),
                     ("tre_c", "DM_tre"), ("crn_c", "DM_crn")]:
        dm = Reaction(rid)
        m.add_reactions([dm])
        dm.add_metabolites({m.metabolites.get_by_id(mid): -1.0})
        dm.bounds = (0.5, 0.5)
OSMO = ["GLYBabcpp", "CHLabcpp", "PROabcpp", "CRNabcpp", "CTBTabcpp",
        "TRE6PP", "TREHpp", "TREptspp", "TRE6PS", "TREtex"]
for ti in (0, 1):
    run("osmo", setup_osmo, OSMO, ti)

# --- 5c. P-limited + g3p as sole P source
def setup_plim(m):
    m.reactions.EX_pi_e.lower_bound = 0.0
    m.reactions.EX_g3ps_e.lower_bound = -2.0
PLIM = ["G3PSabcpp", "GLYC3Pabcpp", "GLYC2Pabcpp", "G3PEabcpp", "EX_g3ps_e"]
for ti in (0, 1):
    run("plim-g3ps", setup_plim, PLIM, ti)

# --- 5d. glycerol + g3ps demand (fallback operationalization)
def setup_glyc_g3p(m):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_glyc_e.lower_bound = -q_glc[0]
    dm = Reaction("DM_g3ps")
    m.add_reactions([dm])
    dm.add_metabolites({m.metabolites.get_by_id("g3ps_c"): -1.0})
    dm.bounds = (0.5, 0.5)
for ti in (0, 1):
    run("glyc+g3psDM", lambda m: setup_glyc_g3p(m), ["G3PSabcpp"], ti)

# --- 5e. carnitine (aerobic + anaerobic) for caiC
def setup_carn(m):
    m.reactions.EX_crn_e.lower_bound = -1.0
CARN = ["CRNCAL2", "CRNDCAL2", "CTBTCAL2", "CRNabcpp", "CRNCBCT", "CRNBTCT"]
for ti in (0,):
    run("carn-aerobic", setup_carn, CARN, ti)

def setup_carn_anaer(m):
    m.reactions.EX_o2_e.lower_bound = 0.0
    m.reactions.EX_no3_e.lower_bound = -15.0
    m.reactions.EX_crn_e.lower_bound = -1.0
for ti in (0,):
    run("carn-anaer", setup_carn_anaer, CARN, ti)

print()
print("DONE (probe 2)")
