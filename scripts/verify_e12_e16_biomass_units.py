#!/usr/bin/env python3
"""
P0-mechanical verification: why does E12's iJO1366 wild-type biomass read
15.444 "h^-1" while E16's iML1515 reads 0.9259 h^-1 under nominally the
same "glucose+O2 minimal medium"?

Hypothesis (from code reading of novelty_keio_validation_e12.py):
  the E12 "minerals" re-open list includes EX_tre_e (trehalose), a CARBON
  source, at lower_bound = -1000, so the medium is NOT glucose-minimal;
  the 15.444 objective value is dominated by unlimited trehalose.
  E16 (novelty_keio_iml1515_e16.py) has the same list element, but the
  question is whether iML1515's trehalose exchange exists / behaves the
  same way.

This script re-runs the wild-type FBA under four conditions per model:
  A. exact E12/E16 script medium (glc -10, O2 -20, minerals incl. tre -1000)
  B. same but EX_tre_e CLOSED (glucose truly minimal)
  C. glc -10, O2 -20, minerals WITHOUT tre
  D. tre only (glc closed, tre -1000)  [iJO1366 only, to isolate]
and reports objective value + uptake fluxes.
"""
import json
import cobra
from cobra.io import load_json_model

RESULTS = {}

def set_medium(model, glc=-10.0, o2=-20.0, tre=-1000.0, minerals=True):
    for r in model.reactions:
        if r.id.startswith("EX_"):
            r.lower_bound = 0
    model.reactions.get_by_id("EX_glc__D_e").lower_bound = glc
    o2_id = "EX_o2_e" if "EX_o2_e" in [r.id for r in model.reactions] else "EX_o2s_e"
    model.reactions.get_by_id(o2_id).lower_bound = o2
    min_list = ["EX_nh4_e", "EX_pi_e", "EX_so4_e", "EX_k_e", "EX_na1_e",
                "EX_mg2_e", "EX_ca2_e", "EX_cl_e", "EX_fe2_e", "EX_fe3_e",
                "EX_cu2_e", "EX_mn2_e", "EX_zn2_e", "EX_cobalt2_e",
                "EX_mobd_e", "EX_ni2_e", "EX_sel_e"]
    if minerals:
        for ex_id in min_list:
            if ex_id in [r.id for r in model.reactions]:
                model.reactions.get_by_id(ex_id).lower_bound = -1000.0
    tre_ids = [r.id for r in model.reactions if "tre" in r.id.lower() and r.id.startswith("EX_")]
    if tre is not None:
        for t in tre_ids:
            model.reactions.get_by_id(t).lower_bound = tre
    return tre_ids

def run(model, tag, tre_setting, glc=-10.0):
    tre_ids = set_medium(model, glc=glc, o2=-20.0, tre=tre_setting)
    sol = model.optimize()
    if sol.status != "optimal":
        print(f"  [{tag}] status={sol.status}")
        return
    glc_flux = sol.fluxes.get("EX_glc__D_e", 0.0)
    o2_flux = sol.fluxes.get("EX_o2_e", sol.fluxes.get("EX_o2s_e", 0.0))
    tre_flux = sum(sol.fluxes.get(t, 0.0) for t in tre_ids) if tre_ids else 0.0
    print(f"  [{tag}] obj={sol.objective_value:.4f}  glc={glc_flux:.2f}  "
          f"o2={o2_flux:.2f}  tre({tre_ids if tre_ids else 'none'})={tre_flux:.2f}")
    RESULTS[tag] = dict(objective=sol.objective_value, glc=glc_flux, o2=o2_flux, tre=tre_flux)

print("=== iJO1366 (E12 model) ===")
m1 = load_json_model("data/bigg_models/iJO1366.json")
run(m1, "iJO script-medium (tre -1000)", -1000.0)
m1b = load_json_model("data/bigg_models/iJO1366.json")
run(m1b, "iJO tre CLOSED (glucose-minimal)", None)
m1c = load_json_model("data/bigg_models/iJO1366.json")
run(m1c, "iJO tre-only (glc closed)", -1000.0, glc=0.0)

print("=== iML1515 (E16 model) ===")
m2 = load_json_model("data/bigg_models/iML1515.json")
run(m2, "iML script-medium (tre -1000)", -1000.0)
m2b = load_json_model("data/bigg_models/iML1515.json")
run(m2b, "iML tre CLOSED (glucose-minimal)", None)

with open("download/verify_e12_e16_biomass_units.json", "w") as f:
    json.dump(RESULTS, f, indent=2)
print("\nsaved download/verify_e12_e16_biomass_units.json")
