#!/usr/bin/env python3
"""E23 probe 5 (final): verify all 8 condition designs at T1/T8 before the study."""
import warnings
warnings.filterwarnings("ignore")
from cobra.io import load_model
from cobra import Reaction

model = load_model("iJO1366")
q_glc = [5.0, 1.0]
q_O2 = [22.0, 5.0]

print("0. gene names + reaction bounds of interest")
for gid in ("b4055", "b1801", "b1015", "b4111", "b1732", "b3942", "b1710",
            "b3029", "b2533", "b1226", "b1897", "b1197", "b3450", "b0758",
            "b2480", "b4219", "b1778", "b3908", "b0037", "b2129", "b2130",
            "b2677", "b2678", "b2097"):
    try:
        g = model.genes.get_by_id(gid)
        print(f"  {gid:7s} {g.name:10s} n_rxns={len(g.reactions):2d}")
    except KeyError:
        print(f"  {gid:7s} NOT FOUND")
for rid in ("GTHPi", "FESD1s", "THIORDXi", "METSOXR1", "METSOXR2",
            "G2PP", "G2PPpp", "GLYBt2pp", "PROt2rpp"):
    r = model.reactions.get_by_id(rid)
    print(f"  {rid:12s} bounds={r.bounds}")
print("  3fe4s_c consumers:", [r.id for r in model.metabolites.get_by_id("3fe4s_c").reactions])

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

# C3: glycerol carbon (2x trajectory), P-limited, glyc2p sole P, KO b4055
def setup_c3(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_glyc_e.lower_bound = -2.0 * q_glc[ti]
    m.reactions.EX_pi_e.lower_bound = 0.0
    m.reactions.EX_glyc2p_e.lower_bound = -2.0
    m.genes.get_by_id("b4055").knock_out()
for ti in (0, 1):
    run("C3 glyc-Plim", setup_c3,
        ["GLYC2Pabcpp", "G2PP", "GLYC2Ptex", "EX_glyc2p_e", "GLYC3Pabcpp"], ti)

# C5: proline-N, KO putP(b1015) + proP(b4111)
def setup_c5(m, ti):
    m.reactions.EX_nh4_e.lower_bound = 0.0
    m.reactions.EX_pro__L_e.lower_bound = -20.0
    m.genes.get_by_id("b1015").knock_out()
    m.genes.get_by_id("b4111").knock_out()
for ti in (0, 1):
    run("C5 proline-N", setup_c5,
        ["PROabcpp", "PROtex", "PROD2", "EX_pro__L_e", "PROt2rpp", "PROt4pp"], ti)

# C4: trehalose carbon (half trajectory)
def setup_c4(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_tre_e.lower_bound = -0.5 * q_glc[ti]
for ti in (0, 1):
    run("C4 trehalose-C", setup_c4,
        ["TREHpp", "TREtex", "TREptspp", "TRE6PP", "TRE6PH", "TREH", "TRE6PS"], ti)

# C6: oxidative WT arm (open SPODM, forced QMO2 + METOX)
def setup_c6(m, ti):
    m.reactions.SPODM.bounds = (0.0, 1000.0)
    m.reactions.QMO2.bounds = (0.05 * q_glc[ti], 0.05 * q_glc[ti])
    m.reactions.METOX1s.bounds = (0.01 * q_glc[ti], 0.01 * q_glc[ti])
    m.reactions.METOX2s.bounds = (0.01 * q_glc[ti], 0.01 * q_glc[ti])
for ti in (0, 1):
    run("C6 oxid-WT", setup_c6,
        ["SPODM", "QMO2", "METSOXR1", "METSOXR2", "THIORDXi", "MOX",
         "GTHPi", "FESD1s", "METOX1s"], ti)

# C7: oxidative vulnerable arm (+ MOX irreversible, KO gpx b1710)
def setup_c7(m, ti):
    setup_c6(m, ti)
    m.reactions.MOX.bounds = (0.0, 1000.0)
    m.genes.get_by_id("b1710").knock_out()
for ti in (0, 1):
    run("C7 oxid-vuln", setup_c7,
        ["SPODM", "METSOXR1", "METSOXR2", "THIORDXi", "MOX", "GTHPi",
         "TRDR"], ti)

# C8: osmotic retention (KO proP + b1801; glyb + tre import; scaled demands)
def setup_c8(m, ti):
    m.genes.get_by_id("b4111").knock_out()
    m.genes.get_by_id("b1801").knock_out()
    m.reactions.EX_glyb_e.lower_bound = -1.0
    m.reactions.EX_tre_e.lower_bound = -1.0
    for mid, f in [("glyb_c", 0.05), ("tre_c", 0.10)]:
        dm = Reaction("DM_" + mid[:4])
        m.add_reactions([dm])
        dm.add_metabolites({m.metabolites.get_by_id(mid): -1.0})
        dm.bounds = (f * q_glc[ti], f * q_glc[ti])
for ti in (0, 1):
    run("C8 osmo-ret", setup_c8,
        ["GLYBabcpp", "GLYBtex", "GLYBt2pp", "TRE6PP", "TREHpp", "TREptspp"], ti)

print("\nDONE (probe 5)")
