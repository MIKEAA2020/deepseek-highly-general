#!/usr/bin/env python3
"""
v16 / Study E23: MULTI-CONDITION FBA (Option D).

Approved design (after v14b + v15/E22): swap the FBA condition so the 14
zero-kappa_V MAPPED reactions activate, then test the cross-condition
hypothesis: does a gene's kappa_V under ITS matched condition predict its
|log2 FC| under the Lemuth glucose-limited aerobic condition?

  All conditions run on the E10 carbon-limitation time axis
  (q_glc 5.0 -> 1.0 mmol/gDW/h, q_O2 22.0 -> 5.0), same solver (GLPK),
  same kappa_V definition:  kappa_V(r,t) = (v_r(t) - v_r(T1))^2,
  per-gene kappa_V(g,t) = max over the gene's reactions (E10/E22 exact).

CONDITIONS (9):
  C0 baseline            glucose aerobic (E10 exact; MUST reproduce E22)
  C1 anaerobic-nitrate   O2=0, NO3 unlimited          -> narJ   (primary)
  C2 galactose           EX_gal = q_glc (C-matched)   -> galT   (primary)
  C3 glycerol-P-limited  glycerol C, EX_pi=0, glyc2p
                        sole P (0.4*q_glc feed), -b4055 -> ugpC  (primary)
  C4 trehalose           EX_tre = q_glc/2 (C-matched)-> treA   (primary)
  C5 proline-nitrogen    -putP(b1015) -proP(b4111),
                        NH4 off, proline unlimited   -> proV/proW (primary)
  C6 oxidative-WT        open SPODM, forced QMO2 quinol-
                        autoxidation leak + METOX damage; MOX made
                        irreversible (model fix; kills energy loop)
                                                      -> sodA/msrA/yeaA (burden)
  C7 oxidative-vuln      C6 + -gpx(b1710), FESD1s off-> bcp    (burden)
  C8 osmotic-retention   -proP(b4111) -b1801; glyb+tre import,
                        retention demands ~ q_glc     -> otsB/yehX/yehY (burden)
  caiC: structurally unactivatable (closed carnitine-CoA cycle) - excluded.

PRIMARY/SECONDARY ENDGENEITY CRITERION (the methodological point):
  primary   = flux follows medium composition + feed trajectory + FBA
              optimality (the same class as E10's b2097/FBA flux);
  secondary = flux magnitude is fixed by an imposed damage/retention
              burden rate (a modeling assumption) -> reported structurally,
              EXCLUDED from the primary correlation.

USER-REQUESTED VERIFICATION CHECKS:
  [D-cons] baseline reproduces E22 exactly (438 active reactions, global
           kappa 0.158543, b2097 = 9.490142, r = -0.0633/+0.1024/+0.0838).
  [D-def]  identical kappa_V formula / solver / T1 reference / aggregation.
  [D-map]  every audit-assigned reaction's GPR contains the MAPPED gene.
  [D-act]  per-condition activation of the 14 target gene sets (flux > 0
           at some T, kappa_V > 0), caiC dead-end proof (closed-subnetwork
           BFS + empirical swap test).

Outputs (download/):
  novelty_v16_multicondition_e23.{csv,txt,png,results.json}
"""
import json
import warnings
warnings.filterwarnings("ignore")
import itertools
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cobra.io import load_model
from cobra import Reaction

OUT = "/home/z/my-project/download"
PREFIX = f"{OUT}/novelty_v16_multicondition_e23"

q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_O2 = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]
T = [f"T{i+1}" for i in range(8)]
EPS = 1e-9
KV_EPS = 1e-16

MAPPED15 = {  # gene symbol (Lemuth) -> b-number (v14b audit)
    "b2097": "b2097", "bcp": "b2480", "caiC": "b0037", "galT": "b0758",
    "msrA": "b4219", "narJ": "b1226", "otsB": "b1897", "proV": "b2677",
    "proW": "b2678", "sodA": "b3908", "treA": "b1197", "ugpC": "b3450",
    "yeaA": "b1778", "yehX": "b2129", "yehY": "b2130",
}
# b-number -> audit-assigned reactions + matched condition + class
GENE_PLAN = {
    "b2097": (["FBA"], "baseline", "primary"),
    "b1226": (["NO3R1pp", "NO3R2pp"], "anaerobic-nitrate", "primary"),
    "b0758": (["UGLT"], "galactose", "primary"),
    "b3450": (["G3PSabcpp", "GLYC2Pabcpp", "G3PEabcpp"],
              "glycerol-P-limited", "primary"),
    "b1197": (["TREHpp"], "trehalose", "primary"),
    "b2677": (["PROabcpp", "CTBTabcpp", "CRNabcpp"],
              "proline-nitrogen", "primary"),
    "b2678": (["PROabcpp", "CTBTabcpp", "CRNabcpp"],
              "proline-nitrogen", "primary"),
    "b3908": (["SPODM"], "oxidative-WT", "burden"),
    "b4219": (["METSOXR1"], "oxidative-WT", "burden"),
    "b1778": (["METSOXR2"], "oxidative-WT", "burden"),
    "b2480": (["THIORDXi"], "oxidative-vulnerable", "burden"),
    "b1897": (["TRE6PP"], "osmotic-retention", "burden"),
    "b2129": (["CHLabcpp", "GLYBabcpp"], "osmotic-retention", "burden"),
    "b2130": (["CHLabcpp", "GLYBabcpp"], "osmotic-retention", "burden"),
    "b0037": (["CTBTCAL2", "CRNCAL2", "CRNDCAL2"], None, "excluded"),
}

log = []
def P(s=""):
    print(s)
    log.append(s)

P("=" * 78)
P("v16 / Study E23: MULTI-CONDITION FBA (Option D)")
P("=" * 78)

lemuth = json.load(open("/tmp/lemuth_ts_clean.json"))
fc_max = {rec["gene"]: max(abs(rec[f"T{i}"]) for i in range(1, 9))
          for rec in lemuth}

# ----------------------------------------------------------------------
# Condition setups (fresh model per condition; `with model:` per timepoint)
# ----------------------------------------------------------------------
def dm(m, mid, rate):
    r = Reaction(f"DM_e23_{mid}")
    m.add_reactions([r])
    r.add_metabolites({m.metabolites.get_by_id(mid): -1.0})
    r.bounds = (rate, rate)

def c0_baseline(m, ti):
    pass  # EX_glc / EX_o2 already set by the harness (E10 exact)

def c1_anaer_nitrate(m, ti):
    m.reactions.EX_o2_e.lower_bound = 0.0
    m.reactions.EX_no3_e.lower_bound = -1000.0

def c2_galactose(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_gal_e.lower_bound = -q_glc[ti]

def c3_glycerol_plim(m, ti):
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_glyc_e.lower_bound = -2.0 * q_glc[ti]
    m.reactions.EX_pi_e.lower_bound = 0.0
    m.reactions.EX_glyc2p_e.lower_bound = -0.4 * q_glc[ti]
    m.genes.get_by_id("b4055").knock_out()  # periplasmic glyc2p/g3p phosphatase

def c4_trehalose(m, ti):
    # treB-deficient background: the trehalose PTS (TREptspp, GPR
    # ptsH/ptsI/crr AND treB=b4240) is the FBA-preferred (degenerate)
    # route; removing the trehalose-specific component b4240 alone forces
    # the periplasmic trehalase route (treA/TREHpp) -- the treB-mutant
    # phenotype
    m.reactions.EX_glc__D_e.lower_bound = 0.0
    m.reactions.EX_tre_e.lower_bound = -0.5 * q_glc[ti]
    m.genes.get_by_id("b4240").knock_out()  # treB

def c5_proline_n(m, ti):
    m.reactions.EX_nh4_e.lower_bound = 0.0
    m.reactions.EX_pro__L_e.lower_bound = -20.0
    m.genes.get_by_id("b1015").knock_out()  # putP
    m.genes.get_by_id("b4111").knock_out()  # proP

def c6_oxidative_wt(m, ti):
    m.reactions.SPODM.bounds = (0.0, 1000.0)
    m.reactions.QMO2.bounds = (0.05 * q_glc[ti], 0.05 * q_glc[ti])
    m.reactions.METOX1s.bounds = (0.01 * q_glc[ti], 0.01 * q_glc[ti])
    m.reactions.METOX2s.bounds = (0.01 * q_glc[ti], 0.01 * q_glc[ti])
    m.reactions.MOX.bounds = (0.0, 1000.0)  # irreversible: kills energy loop

def c7_oxidative_vuln(m, ti):
    c6_oxidative_wt(m, ti)
    m.genes.get_by_id("b1710").knock_out()  # gpx
    m.reactions.FESD1s.bounds = (0.0, 0.0)

def c8_osmotic_ret(m, ti):
    m.genes.get_by_id("b4111").knock_out()  # proP
    m.genes.get_by_id("b1801").knock_out()  # glyb/pro-betaine symport clause
    # carbon-matched trehalose co-feed: 0.1 trehalose = 0.2 hexose-equiv,
    # replacing the same hexose fraction of the glucose feed
    m.reactions.EX_glc__D_e.lower_bound = -(0.8 * q_glc[ti])
    m.reactions.EX_tre_e.lower_bound = -(0.10 * q_glc[ti])
    m.reactions.EX_glyb_e.lower_bound = -1.0
    dm(m, "glyb_c", 0.05 * q_glc[ti])
    dm(m, "tre_c", 0.05 * q_glc[ti])

CONDITIONS = [
    ("baseline", c0_baseline),
    ("anaerobic-nitrate", c1_anaer_nitrate),
    ("galactose", c2_galactose),
    ("glycerol-P-limited", c3_glycerol_plim),
    ("trehalose", c4_trehalose),
    ("proline-nitrogen", c5_proline_n),
    ("oxidative-WT", c6_oxidative_wt),
    ("oxidative-vulnerable", c7_oxidative_vuln),
    ("osmotic-retention", c8_osmotic_ret),
]

cond_flux, cond_mu = {}, {}
RXN_IDS = None
for cname, setup in CONDITIONS:
    model = load_model("iJO1366")
    fluxes, mus = [], []
    for ti in range(8):
        with model:
            model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
            model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
            setup(model, ti)
            sol = model.optimize()
            assert sol.status == "optimal", f"{cname} T{ti+1} {sol.status}"
            fluxes.append(sol.fluxes.to_numpy())
            mus.append(sol.objective_value)
    cond_flux[cname] = np.array(fluxes)          # 8 x n_rxn
    cond_mu[cname] = mus
    if RXN_IDS is None:                          # baseline: canonical order
        RXN_IDS = list(sol.fluxes.index)
    P(f"[{cname:21s}] mu T1..T8: " +
      " ".join(f"{mu:.3f}" for mu in mus))

# canonical reaction ids: from the baseline condition (no pseudo-reactions;
# later conditions may append DM_* columns, which are ignored via RXN_IDX)
RXN_IDX = {r: i for i, r in enumerate(RXN_IDS)}
assert len(RXN_IDS) == 2583 and len(set(RXN_IDS)) == 2583

# kappa_V per reaction per condition (E10 definition, T1 reference)
kappa = {}   # cond -> 8 x n_rxn
for cname, _ in CONDITIONS:
    F = cond_flux[cname]
    kappa[cname] = (F - F[0:1, :]) ** 2

active = {c: [r for r in RXN_IDS
              if np.abs(cond_flux[c][:, RXN_IDX[r]]).max() > EPS]
          for c, _ in CONDITIONS}
kv_nonzero = {c: [r for r in RXN_IDS
                  if kappa[c][:, RXN_IDX[r]].max() > KV_EPS]
              for c, _ in CONDITIONS}
P(f"\nActive reactions per condition (|v|>{EPS:g} at any T):")
for c, _ in CONDITIONS:
    P(f"  {c:21s} {len(active[c]):5d} active, {len(kv_nonzero[c]):5d} with kappa_V>0")
union_active = set().union(*[set(active[c]) for c, _ in CONDITIONS])
P(f"  UNION over 9 conditions: {len(union_active)} "
  f"({100.0*len(union_active)/len(RXN_IDS):.1f}% of {len(RXN_IDS)}) "
  f"vs baseline {len(active['baseline'])} "
  f"({100.0*len(active['baseline'])/len(RXN_IDS):.1f}%)")

# energy-loop guard for the oxidative arms
mu_base_T1 = cond_mu["baseline"][0]
for c in ("oxidative-WT", "oxidative-vulnerable", "osmotic-retention"):
    assert cond_mu[c][0] < mu_base_T1 + 0.02, \
        f"{c}: mu(T1)={cond_mu[c][0]:.4f} suggests an energy loop"
P(f"\nEnergy-loop guard: mu(T1) baseline={mu_base_T1:.4f}; oxidative-WT "
  f"{cond_mu['oxidative-WT'][0]:.4f}; oxidative-vulnerable "
  f"{cond_mu['oxidative-vulnerable'][0]:.4f} (all <= baseline+0.02: OK)")

# ----------------------------------------------------------------------
# [D-cons] baseline must reproduce E22 exactly
# ----------------------------------------------------------------------
P("\n[D-cons] Baseline reproduction of E22/E10:")
model = load_model("iJO1366")
g2r = {g.id: [r.id for r in g.reactions] for g in model.genes}
kappa_base = kappa["baseline"]
kv_rxn_base = {r: kappa_base[:, RXN_IDX[r]] for r in RXN_IDS}
kv_gene_base = {}
for g, rids in g2r.items():
    kv_gene_base[g] = max((kv_rxn_base[r].max() for r in rids), default=0.0)

n_act_base = len(active["baseline"])
P(f"  active reactions: {n_act_base} (E22: 438)")
biom = np.array([(cond_mu['baseline'][t] - cond_mu['baseline'][0]) ** 2
                 for t in range(8)])
glob_max = float(biom.max())
P(f"  global kappa_V (biomass deficit)^2 max = {glob_max:.6f} (E22: 0.158543)")

cdef_ok = (n_act_base == 438) and abs(glob_max - 0.158543) < 1e-5

# the 15 MAPPED kappa values
for gene_sym, bnum in MAPPED15.items():
    kv_here = max((kappa_base[:, RXN_IDX[r]].max() for r in g2r[bnum]),
                  default=0.0)
    expect = 9.490142 if bnum == "b2097" else 0.0
    ok = abs(kv_here - expect) < 1e-4
    cdef_ok &= ok
    P(f"  {gene_sym:6s} ({bnum}) kappa_max = {kv_here:10.6f} "
      f"(expected {expect:10.6f}) {'OK' if ok else 'MISMATCH'}")

# the three E10-lineage Pearson r values (E22 code path)
keio = pd.read_excel("/home/z/my-project/raw tomoya baba supp/"
                     "44320_2006_BFMSB4100050_MOESM5_ESM.xls",
                     sheet_name=0, header=3)
keio = keio.dropna(subset=[keio.columns[1], "b number"]).copy()
keio["_g"] = keio[keio.columns[1]].astype(str).str.strip().str.lower()
keio["_b"] = keio["b number"].astype(str).str.strip()
KEIO = {}
for _, row in keio.iterrows():
    if row["_g"] and row["_g"] not in KEIO:
        KEIO[row["_g"]] = row["_b"]

kv_unmasked, kv_v12, kv_v13 = {}, {}, {}
for rec in lemuth:
    gene = rec["gene"]
    mg = gene if gene in g2r else None
    if mg is None:
        for alt in [gene.upper(), gene.capitalize()]:
            if alt in g2r:
                mg = alt
                break
    mg_orig = mg
    if mg is None:
        kb = KEIO.get(gene.strip().lower())
        if kb and kb in g2r:
            mg = kb
    if mg is not None:
        kv = max((kv_rxn_base[r].max() for r in g2r[mg]), default=0.0)
        kv_v13[gene] = kv
        kv_v12[gene] = 0.0
        kv_unmasked[gene] = kv if mg_orig is not None else glob_max
    else:
        kv_unmasked[gene] = kv_v12[gene] = kv_v13[gene] = glob_max

genes92 = [r["gene"] for r in lemuth]
fc92 = np.array([fc_max[g] for g in genes92])
r_unmasked = pearsonr(np.log10(np.clip([kv_unmasked[g] for g in genes92],
                                       1e-12, None)), fc92)[0]
r_v12 = pearsonr(np.log10(np.clip([kv_v12[g] for g in genes92],
                                  1e-12, None)), fc92)[0]
r_v13 = pearsonr(np.log10(np.clip([kv_v13[g] for g in genes92],
                                  1e-12, None)), fc92)[0]
P(f"  r unmasked {r_unmasked:+.4f} (exp -0.0633), v12 {r_v12:+.4f} "
  f"(exp +0.1024), v13 {r_v13:+.4f} (exp +0.0838)")
cdef_ok &= (abs(r_unmasked + 0.0633) < 5e-4 and abs(r_v12 - 0.1024) < 5e-4
            and abs(r_v13 - 0.0838) < 5e-4)
P(f"[D-cons] overall: {'BASELINE REPRODUCES E22 EXACTLY' if cdef_ok else 'MISMATCH'}")
assert cdef_ok

# ----------------------------------------------------------------------
# [D-map] every audit reaction's GPR contains the MAPPED b-number
# ----------------------------------------------------------------------
P("\n[D-map] GPR membership of the MAPPED genes in their audit reactions:")
dmap_ok = True
for sym, bnum in MAPPED15.items():
    rxns, matched, cls = GENE_PLAN[bnum]
    for rid in rxns:
        gset = {g.id for g in model.reactions.get_by_id(rid).genes}
        ok = bnum in gset
        dmap_ok &= ok
        P(f"  {sym:6s} {rid:14s} {'OK' if ok else 'NOT IN GPR!'}")
P(f"[D-map] overall: {'ALL 15 MAPPED GENES PRESENT IN THEIR GPRs' if dmap_ok else 'MISMATCH'}")
assert dmap_ok

# ----------------------------------------------------------------------
# [D-act] per-gene activation under every condition + caiC dead-end proof
# ----------------------------------------------------------------------
gene_names = {g.id: (g.name or g.id) for g in model.genes}
COND_NAMES = [c for c, _ in CONDITIONS]
gene_kv_matrix = {}   # (bnum, cond) -> per-gene kappa trajectory (8-vec)
for bnum in MAPPED15.values():
    rids = [r for r in g2r[bnum]]
    for c in COND_NAMES:
        K = kappa[c]
        traj = np.array([max((K[t, RXN_IDX[r]] for r in rids
                              if r in RXN_IDX), default=0.0)
                         for t in range(8)])
        gene_kv_matrix[(bnum, c)] = traj

P("\n[D-act] Matched-condition activation of the 14 zero-kappa_V genes:")
act_table = {}
for sym, bnum in MAPPED15.items():
    rxns, matched, cls = GENE_PLAN[bnum]
    if matched is None:
        act_table[sym] = {"activated": False, "reason": "dead-end"}
        P(f"  {sym:6s} EXCLUDED (closed carnitine-CoA cycle; proof below)")
        continue
    traj = gene_kv_matrix[(bnum, matched)]
    kv_max = float(traj.max())
    act = kv_max > KV_EPS
    act_table[sym] = {"activated": act, "kv_max": kv_max,
                      "matched": matched, "class": cls}
    fl = cond_flux[matched]
    f1 = max(abs(fl[0, RXN_IDX[r]]) for r in rxns if r in RXN_IDX)
    f8 = max(abs(fl[7, RXN_IDX[r]]) for r in rxns if r in RXN_IDX)
    P(f"  {sym:6s} [{matched:21s}] flux T1={f1:8.3f} T8={f8:8.3f} "
      f"kappa_max={kv_max:10.6f} {'ACTIVATED' if act else 'NOT ACTIVATED'}")
n_act_zero = sum(1 for sym, v in act_table.items()
                  if sym != "b2097" and v.get("activated"))
n_act_all = sum(1 for v in act_table.values() if v.get("activated"))
P(f"[D-act] {n_act_zero}/14 zero-kappa_V genes activated under matched "
  f"conditions (+ b2097, already active) = {n_act_all}/15 MAPPED genes; "
  f"caiC is the one structural dead-end")

# caiC dead-end proof: airtight permissive-LP argument -- with EVERY
# exchange open (+/-1000) and the objective set to the ligase flux itself,
# the maximum attainable steady-state flux is 0 => NO steady-state flux
# vector (under any medium, any objective) carries flux through caiC's
# reactions. Plus the empirical medium-swap test.
P("\n[D-act] caiC structural proof (no steady-state flux through the ligases):")
model_c2 = load_model("iJO1366")
for r in model_c2.reactions:
    if r.id.startswith("EX_"):
        r.bounds = (-1000.0, 1000.0)
max_lig = {}
for rid in ("CTBTCAL2", "CRNCAL2", "CRNDCAL2"):
    with model_c2:
        model_c2.objective = rid
        sol = model_c2.optimize()
        assert sol.status == "optimal"
        max_lig[rid] = float(sol.objective_value)
P("  permissive LP (all 221+ exchanges open +/-1000, objective = ligase"
  " flux, no growth constraint):")
for k, v in max_lig.items():
    P(f"    max steady-state flux {k} = {v:.6f}")
closed_ok = all(abs(v) < 1e-9 for v in max_lig.values())
P("  mechanism: the ligases are irreversible (ATP-consuming) into a CoA-"
  "ester pool (crncoa/ctbtcoa/crnDcoa) whose only reactions interconvert")
P("  esters and release ctbt/gbbtn (both without exchanges, not in"
  " biomass) -- the pool has no net sink, so steady state forbids any")
P("  positive ligase flux regardless of medium or objective.")

model_c = load_model("iJO1366")
with model_c:
    model_c.reactions.EX_glc__D_e.lower_bound = -5.0
    model_c.reactions.EX_o2_e.lower_bound = 0.0
    model_c.reactions.EX_no3_e.lower_bound = -1000.0
    model_c.reactions.EX_crn_e.lower_bound = -10.0
    sol_c = model_c.optimize()
    cai_fluxes = {r: float(sol_c.fluxes[r]) for r in GENE_PLAN["b0037"][0]}
P(f"  empirical swap (anaerobic+NO3+carnitine 10 mmol): " +
  ", ".join(f"{k}={v:.3f}" for k, v in cai_fluxes.items()))
empirical_ok = all(abs(v) < EPS for v in cai_fluxes.values())
P(f"[D-act] caiC dead-end: closed-subnetwork={closed_ok}, "
  f"empirically-zero={empirical_ok} "
  f"{'CONFIRMED STRUCTURALLY UNACTIVATABLE' if closed_ok and empirical_ok else 'RE-EXAMINE'}")

# ----------------------------------------------------------------------
# PRIMARY analysis: cross-condition correlation (endogenous activations)
# ----------------------------------------------------------------------
P("\n[A] PRIMARY cross-condition correlation (matched kappa_V vs Lemuth "
  "|log2 FC|, endogenous activations only):")

primary_genes = [sym for sym, bnum in MAPPED15.items()
                 if GENE_PLAN[bnum][2] == "primary"]
rows = []
for sym in primary_genes:
    bnum = MAPPED15[sym]
    matched = GENE_PLAN[bnum][1]
    kv = float(gene_kv_matrix[(bnum, matched)].max())
    rows.append({"gene": sym, "bnum": bnum, "matched": matched,
                 "kv_max": kv, "log10_kv": np.log10(kv), "fc_max": fc_max[sym]})
pdf_ = pd.DataFrame(rows)
assert all(r["kv_max"] > 0 for r in rows), \
    "primary gene with zero matched kappa_V -- activation failed"
P(pdf_[["gene", "matched", "kv_max", "fc_max"]].to_string(index=False))

x = pdf_["log10_kv"].to_numpy()
y = pdf_["fc_max"].to_numpy()
r_obs, p_obs = pearsonr(x, y)
rho_obs, rho_p = spearmanr(x, y)

# exact permutation test (all 7! = 5040 assignments of conditions to genes)
rng = np.random.default_rng(20260831)
perm_rs = []
for perm in itertools.permutations(x):
    perm_rs.append(pearsonr(np.array(perm), y)[0])
perm_rs = np.array(perm_rs)
perm_p = float(np.mean(np.abs(perm_rs) >= abs(r_obs)))

# bootstrap CI (10k resamples)
boot = []
n = len(x)
for _ in range(10000):
    idx = rng.integers(0, n, n)
    if np.std(x[idx]) == 0 or np.std(y[idx]) == 0:
        continue
    boot.append(pearsonr(x[idx], y[idx])[0])
boot = np.array(boot)
boot = boot[~np.isnan(boot)]   # drop degenerate resamples
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

P(f"  n = {n} (6 endogenously re-activated + b2097 at its native condition)")
P(f"  Pearson r = {r_obs:+.4f} (p = {p_obs:.4f}), Spearman rho = "
  f"{rho_obs:+.4f} (p = {rho_p:.4f})")
P(f"  95% bootstrap CI: [{ci_lo:+.4f}, {ci_hi:+.4f}] (10,000 resamples)")
P(f"  exact permutation p (5,040 condition-gene reassignments): {perm_p:.4f}")

# leave-one-out sensitivity (which genes carry the association)
loo = []
for i in range(len(x)):
    mask = np.ones(len(x), bool)
    mask[i] = False
    loo.append((primary_genes[i], float(pearsonr(x[mask], y[mask])[0])))
P("  leave-one-out r: " + ", ".join(f"-{g}: {v:+.3f}" for g, v in loo))

# control 1: the v14b zero-dominated artifact (baseline-only MAPPED-15)
xb = np.array([np.log10(max(float(gene_kv_matrix[(b, 'baseline')].max()),
                            1e-12)) for b in MAPPED15.values()])
yb = np.array([fc_max[s] for s in MAPPED15.keys()])
r_v14b = pearsonr(xb, yb)[0]
P(f"  [control] baseline-only MAPPED-15 (v14b artifact): r = {r_v14b:+.4f} "
  f"(stored v14b: -0.158)")

# control 2: all-conditions envelope over the 13 activated genes (caveated)
envelope_rows = []
for sym, bnum in MAPPED15.items():
    if sym == "caiC":
        continue
    env = max(float(gene_kv_matrix[(bnum, c)].max()) for c in COND_NAMES)
    envelope_rows.append({"gene": sym, "env_kv": env,
                          "log10_env": np.log10(env), "fc": fc_max[sym],
                          "class": GENE_PLAN[bnum][2]})
env_df = pd.DataFrame(envelope_rows)
r_env = pearsonr(env_df["log10_env"].to_numpy(),
                 env_df["fc"].to_numpy())[0]
r_env_primary_only = pearsonr(x, y)[0]
P(f"  [control] 13-gene all-condition envelope (mixed classes): r = "
  f"{r_env:+.4f} (caveated: burden-class kappa_V magnitudes are imposed, "
  f"not model-derived)")

# ----------------------------------------------------------------------
# SECONDARY: burden-class activations (reported, not correlated)
# ----------------------------------------------------------------------
P("\n[B] SECONDARY burden-class activations (imposed burden rates; NOT "
  "entered into the primary correlation):")
burden_rows = []
for sym, bnum in MAPPED15.items():
    if GENE_PLAN[bnum][2] != "burden":
        continue
    matched = GENE_PLAN[bnum][1]
    traj = gene_kv_matrix[(bnum, matched)]
    kv = float(traj.max())
    burden_rows.append({"gene": sym, "bnum": bnum, "matched": matched,
                        "kv_max": kv, "fc_max": fc_max[sym]})
    P(f"  {sym:6s} [{matched:21s}] kappa_max = {kv:.6f} "
      f"(burden rate is imposed; magnitude not interpretable)")
burden_df = pd.DataFrame(burden_rows)
P("  caveat: these kappa_V values scale with the imposed burden fractions")
P("  (QMO2 leak 5% of q_glc; METOX damage 1%; retention 5-10%); they show")
P("  the reactions CAN carry varying flux under designed stress, not that")
P("  the magnitudes predict anything.")

# ----------------------------------------------------------------------
# [C] condition <-> reaction coverage (the structural payoff)
# ----------------------------------------------------------------------
P("\n[C] Multi-condition coverage (the condition-reaction bottleneck):")
base_rxn = set(active["baseline"])
for c in COND_NAMES:
    new = set(active[c]) - base_rxn
    P(f"  {c:21s}: {len(active[c]):5d} active ({len(new):4d} newly "
      f"activated vs baseline)")
P(f"  UNION: {len(union_active)} / {len(RXN_IDS)} "
  f"({100.0*len(union_active)/len(RXN_IDS):.1f}%) vs 438 (17.0%) baseline")
P(f"  coverage lift: {len(union_active) - len(base_rxn)} additional "
  f"reactions, i.e. {100.0*(len(union_active)/len(base_rxn)-1):.1f}% relative")

# gene-level coverage
base_gene_set = set(kv_gene_base)
def genes_with_kv(c):
    s = set()
    K = kappa[c]
    for g, rids in g2r.items():
        if any(K[:, RXN_IDX[r]].max() > KV_EPS for r in rids
               if r in RXN_IDX):
            s.add(g)
    return s
cov_genes = {c: genes_with_kv(c) for c in COND_NAMES}
union_genes = set().union(*cov_genes.values())
P(f"  genes with non-zero kappa_V: baseline {len(cov_genes['baseline'])}, "
  f"union over 9 conditions {len(union_genes)} "
  f"({100.0*len(union_genes)/len(g2r):.1f}% of {len(g2r)} model genes)")

# per-condition flux binding checks (endogeneity audit)
P("\n[D-end] Endogeneity audit (feed caps non-binding / flux not cap-set):")
f_no3 = [abs(cond_flux["anaerobic-nitrate"][t, RXN_IDX["NO3R1pp"]])
         for t in range(8)]
P(f"  NO3R1pp T1={f_no3[0]:.2f} T8={f_no3[7]:.2f} "
  f"(EX_no3 cap 1000: non-binding)")
f_g2p = [-cond_flux["glycerol-P-limited"][t, RXN_IDX["EX_glyc2p_e"]]
         for t in range(8)]
f_g2p_cap = [0.4 * q for q in q_glc]
binding_g2p = [f_g2p[i] >= f_g2p_cap[i] - 1e-6 for i in range(8)]
P(f"  glyc2p uptake T1={f_g2p[0]:.3f} (cap {f_g2p_cap[0]:.2f}) "
  f"T8={f_g2p[7]:.3f} (cap {f_g2p_cap[7]:.2f}); "
  f"binding at T: {[i+1 for i, b in enumerate(binding_g2p) if b] or 'none'}")
f_pro = [-cond_flux["proline-nitrogen"][t, RXN_IDX["EX_pro__L_e"]]
         for t in range(8)]
P(f"  proline uptake T1={f_pro[0]:.2f} T8={f_pro[7]:.2f} "
  f"(EX_pro cap 20: non-binding)")
f_tre = [-cond_flux["trehalose"][t, RXN_IDX["EX_tre_e"]] for t in range(8)]
P(f"  trehalose uptake T1={f_tre[0]:.2f} T8={f_tre[7]:.2f} "
  f"(= the C-matched feed trajectory by design)")

# ----------------------------------------------------------------------
# Persist outputs
# ----------------------------------------------------------------------
out_rows = []
for sym, bnum in MAPPED15.items():
    rxns, matched, cls = GENE_PLAN[bnum]
    row = {"gene": sym, "b_number": bnum, "gene_name": gene_names.get(bnum, ""),
           "class": cls, "matched_condition": matched or "(none)",
           "reactions": "; ".join(rxns), "max_abs_log2_FC": fc_max[sym]}
    for c in COND_NAMES:
        row[f"kv_{c}"] = float(gene_kv_matrix[(bnum, c)].max())
    if matched:
        row["kv_matched"] = float(gene_kv_matrix[(bnum, matched)].max())
    else:
        row["kv_matched"] = 0.0
    out_rows.append(row)
df_out = pd.DataFrame(out_rows)
df_out.to_csv(f"{PREFIX}.csv", index=False)

results = {
    "study": "v16 multi-condition FBA (Option D, E23)",
    "conditions": [c for c, _ in CONDITIONS],
    "trajectory": {"q_glc": q_glc, "q_O2": q_O2},
    "mu_per_condition": {c: [float(v) for v in cond_mu[c]]
                         for c, _ in CONDITIONS},
    "checks": {
        "D_cons_baseline_reproduces_e22": bool(cdef_ok),
        "D_map_gpr_membership": bool(dmap_ok),
        "D_act_activated_of_14": int(n_act_zero),
        "D_act_caiC_dead_end": bool(closed_ok and empirical_ok),
        "D_end_glyc2p_binding_T": [i + 1 for i, b in enumerate(binding_g2p)
                                   if b],
    },
    "primary_correlation": {
        "n": int(len(x)), "genes": primary_genes,
        "pearson_r": float(r_obs), "pearson_p": float(p_obs),
        "spearman_rho": float(rho_obs), "spearman_p": float(rho_p),
        "bootstrap_ci95": [float(ci_lo), float(ci_hi)],
        "permutation_p_exact_5040": float(perm_p),
        "leave_one_out_r": {g: v for g, v in loo},
        "points": rows,
    },
    "controls": {
        "v14b_artifact_r": float(r_v14b),
        "envelope_13gene_r": float(r_env),
        "e10_lineage_r": {"unmasked": float(r_unmasked),
                          "v12": float(r_v12), "v13": float(r_v13)},
    },
    "burden_class": burden_rows,
    "coverage": {
        "active_rxns_per_condition": {c: len(active[c]) for c in COND_NAMES},
        "union_active_rxns": len(union_active),
        "baseline_active_rxns": len(base_rxn),
        "newly_activated_vs_baseline": len(union_active - base_rxn),
        "genes_nonzero_kv": {c: len(cov_genes[c]) for c in COND_NAMES},
        "union_genes_nonzero_kv": len(union_genes),
    },
}
with open(f"{PREFIX}_results.json", "w") as f:
    json.dump(results, f, indent=1, default=str)

with open(f"{PREFIX}.txt", "w") as f:
    f.write("\n".join(log) + "\n")
P(f"\nWrote {PREFIX}.csv, {PREFIX}_results.json, {PREFIX}.txt")

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)

ax = axes[0, 0]
colors = {"primary": "#3b6fb6", "burden": "#b6453b"}
for _, row in pdf_.iterrows():
    bnum = MAPPED15[row["gene"]]
    traj = gene_kv_matrix[(bnum, row["matched"])]
    ax.plot(range(1, 9), traj, lw=1.8, marker="o", ms=3.5,
            color=colors["primary"], label=f"{row['gene']} ({row['matched']})")
ax.set_yscale("log")
ax.set_xlabel("time point (T1..T8)")
ax.set_ylabel("kappa_V(g, t) under matched condition")
ax.set_title("(A) primary: matched-condition kappa_V trajectories (n=7)")
ax.legend(fontsize=7, ncol=2)

ax = axes[0, 1]
ax.scatter(x, y, s=70, color="#3b6fb6", edgecolor="white", zorder=3)
for _, row in pdf_.iterrows():
    ax.annotate(row["gene"], (row["log10_kv"], row["fc_max"]),
                fontsize=8, xytext=(5, 4), textcoords="offset points")
b, a = np.polyfit(x, y, 1)
xs = np.linspace(x.min() - 0.3, x.max() + 0.3, 100)
ax.plot(xs, a + b * xs, "--", color="#b6453b", lw=1.6,
        label=f"r = {r_obs:+.3f} (p = {p_obs:.3f})")
ax.set_xlabel("log10 kappa_V(matched condition)")
ax.set_ylabel("max |log2 FC| (Lemuth)")
ax.set_title("(B) primary cross-condition correlation (n=7)")
ax.legend(fontsize=9)

ax = axes[1, 0]
names = COND_NAMES
vals = [len(active[c]) for c in names]
newv = [len(set(active[c]) - base_rxn) for c in names]
ax.bar(range(len(names)), vals, color="#3b8657", edgecolor="white",
       label="active reactions")
ax.bar(range(len(names)), newv, color="#c9a227", edgecolor="white",
       label="newly active vs baseline")
ax.axhline(len(base_rxn), color="k", ls=":", lw=1)
ax.set_xticks(range(len(names)))
ax.set_xticklabels([c.replace("-", "\n") for c in names], fontsize=7.5)
ax.set_ylabel("reactions with non-zero flux")
ax.set_title(f"(C) coverage: baseline {len(base_rxn)} -> union "
             f"{len(union_active)} ({100.0*len(union_active)/len(RXN_IDS):.1f}%)")
ax.legend(fontsize=8)

ax = axes[1, 1]
for _, row in burden_df.iterrows():
    bnum = MAPPED15[row["gene"]]
    traj = gene_kv_matrix[(bnum, row["matched"])]
    ax.plot(range(1, 9), traj, lw=1.6, marker="s", ms=3,
            color=colors["burden"], label=row["gene"])
ax.set_yscale("log")
ax.set_xlabel("time point (T1..T8)")
ax.set_ylabel("kappa_V(g, t) (burden-scaled)")
ax.set_title("(D) secondary: burden-class activations (imposed rates)")
ax.legend(fontsize=7, ncol=2)

fig.suptitle("v16 / E23 multi-condition FBA: 13/14 zero-kappa_V genes "
             "activated; primary cross-condition r = %+.3f (n=7)" % r_obs,
             fontsize=12)
fig.savefig(f"{PREFIX}.png", dpi=150)
P(f"Wrote {PREFIX}.png")
print("DONE")
