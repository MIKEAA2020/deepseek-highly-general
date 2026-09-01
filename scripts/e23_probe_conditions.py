#!/usr/bin/env python3
"""
E23 (Option D) PROBE: model diagnostics before writing the study.

Checks, for the 14 zero-kappa_V MAPPED genes:
  1. GPR rules of every target reaction (confirm b-number membership).
  2. Which exchanges exist for candidate stress substrates.
  3. Which metabolites exist for ROS / osmoprotectant sinks.
  4. Quick T1/T8 feasibility + target-reaction flux probe per condition.
Nothing is written to download/ --- pure diagnostics.
"""
import warnings
warnings.filterwarnings("ignore")
from cobra.io import load_model

model = load_model("iJO1366")
RXN_SET = (
    "THIORDXi", "METSOXR1", "METSOXR2", "SPODM",
    "NO3R1pp", "NO3R2pp", "TRE6PP", "TREHpp", "UGLT",
    "G3PSabcpp", "GLYC2Pabcpp", "G3PEabcpp",
    "PROabcpp", "CTBTabcpp", "CRNabcpp", "CHLabcpp", "GLYBabcpp",
    "CTBTCAL2", "CRNCAL2", "CRNDCAL2",
)

print("=" * 78)
print("1. GPR rules of the target reactions")
print("=" * 78)
for rid in RXN_SET:
    try:
        r = model.reactions.get_by_id(rid)
        gpr = str(r.gpr) if r.gpr else "(none)"
        print(f"  {rid:12s} | {r.reaction[:60]:60s} | {gpr[:48]}")
    except KeyError:
        print(f"  {rid:12s} | NOT FOUND")

print()
print("=" * 78)
print("2. Exchanges of interest")
print("=" * 78)
WANT = ["no3", "no2", "glyc", "gal", "tre", "glyb", "bet", "car", "chol",
        "pro", "h2o2", "glyc3p", "g3p", "glyc2p", "crn", "ctbt", "mso",
        "met", "so3", "sufd", "o2s", "for", "ac"]
ex_ids = [r.id for r in model.reactions if r.id.startswith("EX_")]
for w in WANT:
    hits = [e for e in ex_ids if w in e.lower()]
    print(f"  {w:10s} -> {hits}")

print()
print("=" * 78)
print("3. Candidate stress metabolites (cytosolic / periplasmic / external)")
print("=" * 78)
for mid in ["so3_c", "o2s_c", "sufd_c", "h2o2_c", "h2o2_p", "h2o2_e",
            "mso_c", "mso_L_c", "metsox_c", "trdrd_c", "trdox_c",
            "tre6p_c", "tre_c", "tre_p", "tre_e", "glyb_c", "glyb_p",
            "glyb_e", "beto_c", "chol_c", "chol_e", "pro_L_c", "pro_L_e",
            "glyc3p_c", "glyc3p_p", "glyc3p_e", "glyc2p_c", "glyc2p_e",
            "crn_c", "crn_e", "ctbt_c", "ctbt_e", "no3_c", "no3_p", "no3_e"]:
    try:
        m = model.metabolites.get_by_id(mid)
        rx = [r.id for r in m.reactions]
        print(f"  {mid:12s} OK   n_rxns={len(rx):3d}  e.g. {rx[:6]}")
    except KeyError:
        print(f"  {mid:12s} ----")

print()
print("=" * 78)
print("4. Trehalose-6-P producers/consumers (TRE6PP activation path)")
print("=" * 78)
try:
    m = model.metabolites.get_by_id("tre6p_c")
    for r in m.reactions:
        print(f"  {r.id:12s} {r.reaction[:70]}")
except KeyError:
    print("  tre6p_c NOT FOUND")

print()
print("=" * 78)
print("5. Quick condition probes (T1: q_glc=5, q_O2=22; T8: q_glc=1, q_O2=5)")
print("=" * 78)
q_glc = [5.0, 1.0]
q_O2 = [22.0, 5.0]

def probe(name, setup, targets):
    for ti in (0, 1):
        with model:
            model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
            model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
            try:
                extra = setup(model, ti)
                sol = model.optimize()
                if sol.status != "optimal":
                    print(f"  [{name} T{ti+1}] status={sol.status}")
                    continue
                vals = {r: round(float(sol.fluxes[r]), 4) for r in targets}
                print(f"  [{name} T{ti+1}] mu={sol.objective_value:.4f} "
                      + " ".join(f"{r}={v}" for r, v in vals.items()))
            except Exception as e:
                print(f"  [{name} T{ti+1}] ERROR: {e}")

# 5a. baseline
probe("baseline", lambda m, ti: None,
      ["FBA", "NO3R1pp", "SPODM", "THIORDXi", "TRE6PP", "TREHpp"])

# 5b. anaerobic + nitrate
def setup_anaer(m, ti):
    m.reactions.EX_o2_e.lower_bound = 0.0
    m.reactions.EX_no3_e.lower_bound = -15.0
    return None
probe("anaer+NO3", setup_anaer, ["NO3R1pp", "NO3R2pp", "FBA"])

# 5c. glycerol
def setup_glyc(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_glyc_e.lower_bound = -q_glc[ti]
    return None
probe("glycerol", setup_glyc, ["G3PSabcpp", "GLYC2Pabcpp", "G3PEabcpp", "FBA"])

# 5d. galactose
def setup_gal(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_gal_e.lower_bound = -q_glc[ti]
    return None
probe("galactose", setup_gal, ["UGLT", "FBA"])

# 5e. oxidative: sinks for superoxide + met-sulfoxide
from cobra import Reaction
def setup_oxid(m, ti):
    F = 0.5
    # superoxide supply (id guesses resolved at runtime)
    for mid, cand in [("so3_c", "SPODM"), ("o2s_c", "SPODM")]:
        if mid in [x.id for x in m.metabolites]:
            sk = Reaction("SK_probe_" + mid)
            m.add_reactions([sk])
            sk.add_metabolites({m.metabolites.get_by_id(mid): -1.0})
            sk.bounds = (-F, -F)
            break
    for mid in ["mso_c", "mso_L_c"]:
        if mid in [x.id for x in m.metabolites]:
            sk2 = Reaction("SK_probe_" + mid)
            m.add_reactions([sk2])
            sk2.add_metabolites({m.metabolites.get_by_id(mid): -1.0})
            sk2.bounds = (-F, -F)
            break
    return None
probe("oxidative", setup_oxid, ["SPODM", "METSOXR1", "METSOXR2", "THIORDXi"])

# 5f. osmotic: trehalose exchange + glycine-betaine exchange + retain demand
def setup_osmo(m, ti):
    m.reactions.EX_tre_e.lower_bound = -q_glc[ti] * 0.1 if hasattr(
        m.reactions, "EX_tre_e") else 0
    return None
probe("osmo-tre", setup_osmo, ["TREHpp", "TRE6PP"])

print()
print("DONE (probe)")
