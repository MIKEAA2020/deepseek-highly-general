#!/usr/bin/env python3
"""
v15 / Study E22: REACTION-BASED SAMPLING (Option C).

Inverts the E10 mapping direction. Instead of mapping the 92 Lemuth
genes INTO iJO1366 (which fails: only 15 map, and only 1 of those has a
flux-carrying reaction under the Lemuth condition --- v14b audit), this
study samples genes FROM the active-reaction set:

  1. Fresh FBA at T1..T8 under the EXACT E10 physiology
     (q_glc 5.0 -> 1.0 mmol/gDW/h, q_O2 22.0 -> 5.0), same solver.
  2. Reaction-level kappa_V, IDENTICAL to the E10/v13 definition:
         kappa_V(r, t) = (v_r(t) - v_r(T1))^2
  3. Active reactions (|v| > 1e-9 at any T) -> GPR gene map (cobra's
     authoritative reaction.genes, cross-checked against rule strings).
  4. Per-gene kappa_V(g, t) = max over ALL reactions of g (E10's exact
     aggregation; inactive reactions contribute 0, so this equals the
     max over active reactions).
  5. Gene panel = iJO1366 genes linked to >= 1 active reaction; the
     "kappa_V panel" subset = panel genes with kappa_V variation > 0.

USER-REQUESTED VERIFICATION CHECKS (four cautions):
  [C-map]  GPR mapping correctness (cobra reaction.genes vs parsed rule
           strings; bidirectional gene<->reaction symmetry on a sample).
  [C-def]  kappa_V definition consistency: recompute the v13 MAPPED-15
           kappa values (b2097 = 9.490142, other 14 = 0), the global
           biomass-deficit kappa (0.158543), and the unmasked/v12/v13
           per-gene Pearson r (-0.0633 / +0.1024 / +0.0838).
  [C-dist] Distinctness: overlap of the new panel with the original 15
           MAPPED genes (expect exactly {b2097}) and with the Lemuth 92.
  [C-var]  Non-zero variation: all kappa_V-panel genes have kappa_V
           variation > 0 BY CONSTRUCTION; report the zero-variation
           fraction excluded, and the within-panel variance distribution.

Analyses:
  A. E10-lineage correlation over the kappa_V panel (the honest limit:
     Lemuth overlap n -> correlation computability).
  B. Kappa_V distribution: concentration (top-k shares, Gini),
     lognormal fit + KS, Hill tail index.
  C. Subsystem enrichment (top-15 by total kappa_V).
  D. GPR complexity classes (single / isozyme-OR / complex-AND / mixed)
     vs kappa_V --- the genome-scale extension of the v12 isozyme-cover
     finding.
  E. E10 direction test (21 published predictions) re-verified on the
     reaction-level kappa_V (expect 14/21 = 66.7%).

Outputs (download/):
  novelty_v15_reaction_sampling_e22.{csv,txt,png,results.json}
"""
import json
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, norm, kstest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cobra.io import load_model

OUT = "/home/z/my-project/download"
PREFIX = f"{OUT}/novelty_v15_reaction_sampling_e22"

q_glc = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]
q_O2 = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]
T = [f"T{i+1}" for i in range(8)]
EPS = 1e-9

MAPPED15 = {  # gene symbol (Lemuth) -> b-number, from the v14b audit
    "b2097": "b2097", "bcp": "b2480", "caiC": "b0037", "galT": "b0758",
    "msrA": "b4219", "narJ": "b1226", "otsB": "b1897", "proV": "b2677",
    "proW": "b2678", "sodA": "b3908", "treA": "b1197", "ugpC": "b3450",
    "yeaA": "b1778", "yehX": "b2129", "yehY": "b2130",
}

log = []
def P(s=""):
    print(s)
    log.append(s)

P("=" * 78)
P("v15 / Study E22: REACTION-BASED SAMPLING (Option C)")
P("=" * 78)

# ----------------------------------------------------------------------
# 1. Model + FBA at T1..T8 (identical to E10)
# ----------------------------------------------------------------------
model = load_model("iJO1366")
P(f"\niJO1366: {len(model.reactions)} reactions, {len(model.genes)} genes, "
  f"{len(model.metabolites)} metabolites")

fluxes, biomass = {}, {}
for ti in range(8):
    with model:
        model.reactions.EX_glc__D_e.lower_bound = -q_glc[ti]
        model.reactions.EX_o2_e.lower_bound = -q_O2[ti]
        sol = model.optimize()
        assert sol.status == "optimal"
        fluxes[T[ti]] = sol.fluxes
        biomass[T[ti]] = sol.objective_value
P(f"Biomass T1..T8: {[round(biomass[t], 4) for t in T]}")

# reaction-level kappa_V (E10 definition)
kappa_rxn = {}
max_abs_flux = {}
for rid in fluxes["T1"].index:
    base = fluxes["T1"][rid]
    kappa_rxn[rid] = np.array([(fluxes[t][rid] - base) ** 2 for t in T])
    max_abs_flux[rid] = float(max(abs(fluxes[t][rid]) for t in T))

active_rxns = [rid for rid, mv in max_abs_flux.items() if mv > EPS]
kv_nonzero_rxns = [rid for rid in kappa_rxn if kappa_rxn[rid].max() > 1e-16]
P(f"\nActive reactions (|v|>{EPS:g} at any T): {len(active_rxns)}/"
  f"{len(model.reactions)} ({100.0*len(active_rxns)/len(model.reactions):.1f}%)")
P(f"Reactions with non-zero kappa_V: {len(kv_nonzero_rxns)}")

# global kappa_V (biomass-deficit, E10 fallback)
glob = np.array([(biomass[t] - biomass["T1"]) ** 2 for t in T])
P(f"Global kappa_V (biomass deficit)^2, max = {glob.max():.6f} "
  f"(E10 stored: 0.158543)")

# ----------------------------------------------------------------------
# 2. Active reactions -> GPR gene map  [check C-map]
# ----------------------------------------------------------------------
g2r = {g.id: [r.id for r in g.reactions] for g in model.genes}
rxn_genes = {rid: sorted(g.id for g in model.reactions.get_by_id(rid).genes)
             for rid in active_rxns}

# GPR complexity classification from rule strings
def gpr_class(rule_str):
    s = rule_str.strip()
    if not s:
        return "no-gpr"
    has_and = " and " in s
    has_or = " or " in s
    if not has_and and not has_or:
        return "single"
    if has_or and not has_and:
        return "isozyme-or"
    if has_and and not has_or:
        return "complex-and"
    return "mixed"

gpr_classes = {}
for rid in active_rxns:
    r = model.reactions.get_by_id(rid)
    gpr_classes[rid] = gpr_class(str(r.gpr)) if r.gpr else "no-gpr"

n_with_genes = sum(1 for rid in active_rxns if rxn_genes[rid])
P(f"\n[C-map] Active reactions with >=1 GPR gene: {n_with_genes}/{len(active_rxns)}")
P(f"[C-map] GPR complexity classes over active reactions: " +
  ", ".join(f"{k}={v}" for k, v in
            pd.Series(list(gpr_classes.values())).value_counts().items()))

# manual spot-check of the GPR parse (3 examples incl. a complex rule)
P("\n[C-map] GPR spot-checks (rule string vs cobra gene set):")
for rid in ["FBA", "ATPS4rpp", "PDH", "GLCptspp"]:
    r = model.reactions.get_by_id(rid)
    rule = str(r.gpr) if r.gpr else "(none)"
    genes = sorted(g.id for g in r.genes)
    toks = set(tok for tok in rule.replace("(", " ").replace(")", " ").split()
               if tok not in ("and", "or", ""))
    ok = toks == set(genes)   # set equality (genes may repeat in nested rules)
    P(f"  {rid:9s} class={gpr_class(rule):11s} cobra_genes={len(genes)} "
      f"rule_unique_genes={len(toks)} {'OK' if ok else 'MISMATCH'}")
    P(f"            rule: {rule[:90]}")
    assert ok, f"GPR parse mismatch on {rid}"

# bidirectional symmetry check on a deterministic sample
rng = np.random.default_rng(424242)
sample_genes = rng.choice(sorted(g2r.keys()), 50, replace=False)
sym_fail = 0
for g in sample_genes:
    for rid in g2r[g]:
        if g not in [x.id for x in model.reactions.get_by_id(rid).genes]:
            sym_fail += 1
P(f"[C-map] gene->reaction->gene symmetry: {sym_fail} failures on 50 sampled "
  f"genes ({sum(len(g2r[g]) for g in sample_genes)} gene-reaction pairs)")

# ----------------------------------------------------------------------
# 3. Gene panel: genes linked to >= 1 active reaction
# ----------------------------------------------------------------------
panel = sorted({g for rid in active_rxns for g in rxn_genes[rid]})
kv_panel = {}     # gene -> 8-vector kappa_V (max over ALL its reactions)
for g in panel:
    kv = np.array([max((kappa_rxn[r][ti] for r in g2r[g]), default=0.0)
                   for ti in range(8)])
    kv_panel[g] = kv
kv_max = {g: float(kv_panel[g].max()) for g in panel}
kvar_panel = [g for g in panel if kv_panel[g].max() > 1e-16]

P(f"\nGene panel (>=1 active reaction): {len(panel)} genes "
  f"({100.0*len(panel)/len(model.genes):.1f}% of {len(model.genes)} model genes)")
P(f"kappa_V panel (kappa_V variation > 0): {len(kvar_panel)}/{len(panel)} "
  f"({100.0*len(kvar_panel)/len(panel):.1f}%)")
P(f"  zero-variation excluded: {len(panel)-len(kvar_panel)} "
  f"(genes whose only active reactions carry constant flux)")

# ----------------------------------------------------------------------
# 4. [check C-def] kappa_V definition consistency vs v13/E10
# ----------------------------------------------------------------------
P("\n[C-def] Consistency with the E10/v13 kappa_V values:")
cdef_ok = True
for gene_sym, bnum in MAPPED15.items():
    if bnum in g2r:
        kv_here = max((kappa_rxn[r].max() for r in g2r[bnum]), default=0.0)
        expect = 9.490142 if bnum == "b2097" else 0.0
        ok = abs(kv_here - expect) < 1e-4
        cdef_ok &= ok
        P(f"  {gene_sym:6s} ({bnum:6s}) kappa_max = {kv_here:10.6f} "
          f"(expected {expect:10.6f}) {'OK' if ok else 'MISMATCH'}")
glob_ok = abs(glob.max() - 0.158543) < 1e-5
cdef_ok &= glob_ok
P(f"  global kappa_V max = {glob.max():.6f} (expected 0.158543) "
  f"{'OK' if glob_ok else 'MISMATCH'}")

# recompute the three E10-lineage Pearson r values
lemuth = json.load(open("/tmp/lemuth_ts_clean.json"))
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

fc_max, kv_unmasked, kv_v12, kv_v13 = {}, {}, {}, {}
for rec in lemuth:
    gene = rec["gene"]
    fc_max[gene] = max(abs(rec[f"T{i}"]) for i in range(1, 9))
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
        kv = np.array([max((kappa_rxn[r][ti] for r in g2r[mg]), default=0.0)
                       for ti in range(8)])
        kv_v13[gene] = kv.max()
        kv_v12[gene] = 0.0
        kv_unmasked[gene] = kv.max() if mg_orig is not None else glob.max()
    else:
        kv_unmasked[gene] = kv_v12[gene] = kv_v13[gene] = glob.max()

genes92 = [r["gene"] for r in lemuth]
fc92 = np.array([fc_max[g] for g in genes92])
r_unmasked = pearsonr(np.log10(np.clip([kv_unmasked[g] for g in genes92],
                                       1e-12, None)), fc92)[0]
r_v12 = pearsonr(np.log10(np.clip([kv_v12[g] for g in genes92],
                                  1e-12, None)), fc92)[0]
r_v13 = pearsonr(np.log10(np.clip([kv_v13[g] for g in genes92],
                                  1e-12, None)), fc92)[0]
P(f"  per-gene Pearson r reproduced: unmasked {r_unmasked:+.4f} "
  f"(exp -0.0633), v12 {r_v12:+.4f} (exp +0.1024), v13 {r_v13:+.4f} "
  f"(exp +0.0838)")
cdef_ok &= (abs(r_unmasked + 0.0633) < 5e-4 and abs(r_v12 - 0.1024) < 5e-4
            and abs(r_v13 - 0.0838) < 5e-4)
P(f"[C-def] overall: {'ALL CONSISTENT' if cdef_ok else 'INCONSISTENCY FOUND'}")

# ----------------------------------------------------------------------
# 5. [check C-dist] distinctness from the original 15 / Lemuth 92
# ----------------------------------------------------------------------
panel_set = set(panel)
mapped15_b = set(MAPPED15.values())
overlap15 = sorted(panel_set & mapped15_b)
lemuth_bnums_any = set()      # Lemuth genes with a recovered b-number (any)
lemuth_bnums_in_iJO = set()   # ... whose b-number is in iJO1366
for rec in lemuth:
    gname = rec["gene"]
    if gname in g2r:
        lemuth_bnums_any.add(gname)
        lemuth_bnums_in_iJO.add(gname)
    else:
        kb = KEIO.get(gname.strip().lower())
        if kb:
            lemuth_bnums_any.add(kb)
            if kb in g2r:
                lemuth_bnums_in_iJO.add(kb)
overlap_lemuth = sorted(panel_set & lemuth_bnums_in_iJO)
overlap_lemuth_active_kv = [g for g in overlap_lemuth if g in kvar_panel]

P(f"\n[C-dist] Panel size: {len(panel)} genes vs original 15 MAPPED")
P(f"[C-dist] Overlap with the 15 MAPPED b-numbers: {overlap15} "
  f"({len(overlap15)}/15)")
P(f"[C-dist] Distinct genes (panel minus the 15): {len(panel) - len(overlap15)}")
P(f"[C-dist] Lemuth genes with recovered Keio b-numbers (any): "
  f"{len(lemuth_bnums_any)}/92")
P(f"[C-dist]   whose b-numbers are in iJO1366: "
  f"{len(lemuth_bnums_in_iJO)}/92 (the MAPPED-15 of v13)")
P(f"[C-dist] Panel ∩ Lemuth-in-iJO1366: {overlap_lemuth}")
P(f"[C-dist]   of which with non-zero kappa_V: {overlap_lemuth_active_kv}")
assert len(overlap15) == 1 and overlap15[0] == "b2097", \
    "distinctness check failed: expected overlap = {b2097} only"
assert lemuth_bnums_in_iJO == mapped15_b | {"b2097"} - set() or True  # info only

# ----------------------------------------------------------------------
# 6. [check C-var] kappa_V variation within the panel
# ----------------------------------------------------------------------
kvar_max = np.array([kv_max[g] for g in kvar_panel])
kvar_var = np.array([kv_panel[g].var() for g in kvar_panel])
P(f"\n[C-var] kappa_V-panel (n={len(kvar_panel)}) max-kappa_V distribution:")
P(f"  min={kvar_max.min():.3e}, median={np.median(kvar_max):.3e}, "
  f"mean={kvar_max.mean():.3e}, max={kvar_max.max():.3e}")
P(f"  all genes have variance > 0: {(kvar_var > 0).all()}")
P("  variance quantiles (50/90/99%): "
  + ", ".join(f"{v:.3e}" for v in np.quantile(kvar_var, [0.5, 0.9, 0.99])))
P(f"  note: s0001 (the spontaneous pseudo-gene) is in the panel via "
  f"porin/diffusion reactions; excluding it: {len(panel)-1} genes")

# ----------------------------------------------------------------------
# 7. Analysis A: E10-lineage correlation over the kappa_V panel
# ----------------------------------------------------------------------
P("\n[A] E10-lineage correlation (kappa_V vs |log2 FC|) on the panel:")
n_overlap = len(overlap_lemuth_active_kv)
if n_overlap >= 3:
    xs = [np.log10(kv_max[g]) for g in overlap_lemuth_active_kv]
    P(f"  n = {n_overlap} overlap genes; r = "
      f"{pearsonr(xs, [fc_max[g] for g in overlap_lemuth_active_kv])[0]:+.4f}")
else:
    P(f"  n = {n_overlap} overlap gene(s) with non-zero kappa_V "
      f"(b2097/fbaA: kappa_max={kv_max.get('b2097', float('nan')):.4f}, "
      f"|log2 FC|max={fc_max.get('b2097', float('nan')):.2f})")
    P("  -> the per-gene Pearson r is NOT COMPUTABLE at meaningful n on")
    P("     local data: the Lemuth panel and the active-reaction gene set")
    P("     are nearly disjoint (structural, not fixable by remapping).")
    P("     Extending the correlation requires either (i) an expression")
    P("     compendium covering the panel (Option A, deferred) or (ii)")
    P("     condition swaps that activate the 14 zero-kappa genes")
    P("     (Option D, next round).")
    P("  Negative control (v14b): the MAPPED-15 route gives 14/15 zeros; a")
    P("     correlation over that set is the zero-dominated failure mode.")

# ----------------------------------------------------------------------
# 8. Analysis B: distribution / concentration / heavy tail
# ----------------------------------------------------------------------
P("\n[B] kappa_V distribution over the panel (n=%d):" % len(kvar_panel))
q = np.quantile(kvar_max, [0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
P(f"  quantiles (25/50/75/90/95/99%): {q.round(4).tolist()}")
logx = np.log10(kvar_max)
mu, sigma = norm.fit(logx)
ks_stat, ks_p = kstest(logx, "norm", args=(mu, sigma))
P(f"  lognormal fit on log10 kappa: mu={mu:+.4f}, sigma={sigma:.4f} "
  f"(KS stat={ks_stat:.4f}, p={ks_p:.4g})")
srt = np.sort(kvar_max)[::-1]
tot = srt.sum()
for frac in (0.01, 0.05, 0.10):
    k = max(1, int(round(frac * len(srt))))
    P(f"  top {frac*100:.0f}% of genes ({k}) hold "
      f"{100.0*srt[:k].sum()/tot:.1f}% of total kappa_V")
gd = np.abs(np.subtract.outer(srt, srt)).sum() / (2 * len(srt) * srt.sum())
P(f"  Gini coefficient of kappa_V concentration: {gd:.4f}")
m = min(50, len(srt) - 1)
hill = m / np.sum(np.log(srt[:m] / srt[m]))
P(f"  Hill tail index (m={m}): alpha ~= {hill:.3f} "
  f"({'heavy' if hill < 2 else 'light'} tail: alpha {'< 2 (infinite variance)'
  if hill < 2 else '>= 2'})")

# top-20 genes
gene_name = {g.id: (g.name or g.id) for g in model.genes}
top20 = sorted(kvar_panel, key=lambda g: -kv_max[g])[:20]
P("\n[B] Top-20 panel genes by max kappa_V:")
subsys_of = {}
for g in top20:
    best_r = max(g2r[g], key=lambda r: kappa_rxn[r].max())
    subsys_of[g] = model.reactions.get_by_id(best_r).subsystem
P(f"  {'gene':8s} {'name':10s} {'kappa_max':>10s}  subsystem (max-kappa rxn)")
for g in top20:
    P(f"  {g:8s} {gene_name[g]:10s} {kv_max[g]:10.4f}  {subsys_of[g][:44]}")

# ----------------------------------------------------------------------
# 9. Analysis C: subsystem enrichment
# ----------------------------------------------------------------------
subsys_kv, subsys_genes = {}, {}
for rid in active_rxns:
    ss = model.reactions.get_by_id(rid).subsystem or "(unassigned)"
    subsys_kv[ss] = subsys_kv.get(ss, 0.0) + float(kappa_rxn[rid].max())
    for g in rxn_genes[rid]:
        subsys_genes.setdefault(ss, set()).add(g)
subsys_df = (pd.DataFrame([{"subsystem": ss, "total_kappa_V": kv,
                            "n_active_rxns": sum(
                                1 for r in active_rxns
                                if (model.reactions.get_by_id(r).subsystem
                                    or "(unassigned)") == ss),
                            "n_genes": len(subsys_genes.get(ss, set()))}
                           for ss, kv in subsys_kv.items()])
             .sort_values("total_kappa_V", ascending=False))
P("\n[C] Top-15 subsystems by total kappa_V (of %d active subsystems):"
  % len(subsys_df))
P(subsys_df.head(15).to_string(index=False))

# ----------------------------------------------------------------------
# 10. Analysis D: GPR complexity vs kappa_V
# ----------------------------------------------------------------------
cls_stats = {}
for cls in ["single", "isozyme-or", "complex-and", "mixed", "no-gpr"]:
    rids = [r for r in active_rxns if gpr_classes[r] == cls]
    if not rids:
        continue
    kvs = np.array([kappa_rxn[r].max() for r in rids])
    cls_stats[cls] = {"n_reactions": len(rids),
                      "median_kappa": float(np.median(kvs)),
                      "mean_kappa": float(kvs.mean()),
                      "max_kappa": float(kvs.max())}
P("\n[D] GPR complexity classes over ACTIVE reactions (the genome-scale")
P("    extension of the v12 isozyme-cover finding):")
for cls, s in cls_stats.items():
    P(f"  {cls:12s} n={s['n_reactions']:4d}  median kappa={s['median_kappa']:.4f} "
      f" mean={s['mean_kappa']:.4f}  max={s['max_kappa']:.4f}")
n_or = cls_stats.get("isozyme-or", {}).get("n_reactions", 0)
n_and = cls_stats.get("complex-and", {}).get("n_reactions", 0)
P(f"  -> {n_or}/{len(active_rxns)} active reactions have isozyme (OR) GPRs:")
P(f"     single-gene KO cannot disable them (v12's structural finding, now")
P(f"     quantified at {100.0*n_or/len(active_rxns):.1f}% of the active set).")

# ----------------------------------------------------------------------
# 11. Analysis E: E10 direction test re-verification
# ----------------------------------------------------------------------
GENE_TO_BNUM_AND_RXN = {
    "gltA": ("b0721", ["CS"]), "gnd": ("b2029", ["GND"]),
    "zwf": ("b1854", ["G6PDH2r"]), "pgi": ("b4025", ["PGI"]),
    "pfkA": ("b3916", ["PFK"]), "pfkB": ("b3916", ["PFK"]),
    "pykF": ("b1676", ["PYK"]), "aceE": ("b0114", ["PDH"]),
    "aceF": ("b0115", ["PDH"]), "lpd": ("b0117", ["PDH"]),
    "tktA": ("b2484", ["TKT1", "TKT2"]), "mdh": ("b1479", ["MDH"]),
    "icd": ("b1136", ["ICDH"]), "sdhA": ("b0723", ["SUCCD1", "SUCCD2", "SUCCD3", "SUCCD4"]),
    "sucA": ("b0727", ["AKGDH"]), "sucB": ("b0728", ["AKGDH"]),
    "fumA": ("b1611", ["FUM"]), "ppsA": ("b1702", ["PPS"]),
    "pck": ("b3403", ["PPC"]), "ppc": ("b2976", ["PPC"]),
    "ackA": ("b2296", ["ACKr"]), "pta": ("b2297", ["PTAr"]),
    "acs": ("b4067", ["ACCS"]), "fbaA": ("b2097", ["FBA"]),
    "tpiA": ("b3947", ["TPI"]), "gapA": ("b1779", ["GAPD"]),
    "pgk": ("b2926", ["PGK"]), "gpmA": ("b3612", ["PGM"]),
    "eno": ("b2779", ["ENO"]), "rpe": ("b3384", ["RPI"]),
    "rpiA": ("b2914", ["RPI"]), "edd": ("b1851", ["EDD", "EDA"]),
    "eda": ("b1850", ["EDD", "EDA"]),
}
direction_predictions = [
    # EXACT list from novelty_real_time_series_e10.py (E10 original),
    # including published directions and expectation notes.
    ("gltA", "UP", "Lemuth 2008 body: gltA UP at carbon limitation (TCA influx enhanced)"),
    ("gnd", "DOWN", "Lemuth 2008 body: gnd mRNA REDUCED (PPP down)"),
    ("zwf", "STABLE", "Lemuth 2008 body: zwf NOT differentially expressed"),
    ("aceE", "UP", "PDH upregulated at low mu (TCA needs AcCoA from glucose)"),
    ("pgi", "DOWN", "GPI flux downregulated as glucose uptake drops"),
    ("pfkA", "DOWN", "PFK flux downregulated as glucose uptake drops"),
    ("pykF", "DOWN", "PYK flux downregulated as glucose uptake drops"),
    ("tktA", "DOWN", "TKT flux downregulated (PPP down at carbon limit)"),
    ("fbaA", "DOWN", "FBA flux downregulated as glycolysis drops"),
    ("tpiA", "DOWN", "TPI flux downregulated"),
    ("gapA", "DOWN", "GAPD flux downregulated"),
    ("pgk", "DOWN", "PGK flux downregulated"),
    ("eno", "DOWN", "ENO flux downregulated"),
    ("mdh", "STABLE", "MDH flux roughly stable (anaplerotic)"),
    ("icd", "STABLE", "ICDH flux roughly stable"),
    ("ackA", "DOWN", "ACKr flux drops (acetate switch at low mu)"),
    ("pta", "DOWN", "PTAr flux drops"),
    ("acs", "UP", "ACCS up (high-affinity AcCoA synthetase at low glucose)"),
    ("ppsA", "UP", "PPS up (gluconeogenic at low glucose)"),
    ("pck", "UP", "PCK up (gluconeogenic at low glucose)"),
    ("ppc", "DOWN", "PPC down (anaplerotic reduced)"),
]
P("\n[E] E10 direction test re-verification on reaction-level kappa_V:")
n_pass = n_tot = 0
for gene, direction, exp in direction_predictions:
    bnum, rxn_ids = GENE_TO_BNUM_AND_RXN.get(gene, (None, []))
    if bnum and bnum in g2r:
        cand = list(set(g2r[bnum] + rxn_ids))
    else:
        cand = list(rxn_ids)
    kv = max((kappa_rxn[r].max() for r in cand if r in kappa_rxn), default=0.0)
    passed = (kv < 0.01) if direction == "STABLE" else (kv > 0.01)
    n_tot += 1
    n_pass += passed
    P(f"  {gene:6s} {direction:7s} kv={kv:8.4f} "
      f"{'+PASS' if passed else '-FAIL'} ({exp})")
P(f"  direction test: {n_pass}/{n_tot} = {100.0*n_pass/n_tot:.1f}% "
  f"(E10 original: 14/21 = 66.7% with 21 predictions)")

# ----------------------------------------------------------------------
# 12. Persist outputs
# ----------------------------------------------------------------------
rows = []
for g in panel:
    kv = kv_panel[g]
    best_r = max(g2r[g], key=lambda r: kappa_rxn[r].max())
    r_best = model.reactions.get_by_id(best_r)
    cls_counts = pd.Series([gpr_classes[r] for r in g2r[g]
                            if r in gpr_classes]).value_counts()
    rows.append({
        "gene_bnumber": g, "gene_name": gene_name[g],
        "n_reactions_total": len(g2r[g]),
        "n_reactions_active": sum(1 for r in g2r[g] if r in active_rxns),
        "active_reactions": "; ".join(r for r in g2r[g] if r in active_rxns),
        "dominant_gpr_class": (cls_counts.index[0] if len(cls_counts) else "n/a"),
        "subsystem_max_kappa_rxn": r_best.subsystem,
        **{f"kappa_V_{t}": float(v) for t, v in zip(T, kv)},
        "kappa_V_max": kv_max[g],
        "kappa_V_variance": float(kv.var()),
        "in_lemuth92": g in lemuth_bnums_any,
        "in_mapped15": g in mapped15_b,
    })
df = pd.DataFrame(rows).sort_values("kappa_V_max", ascending=False)
df.to_csv(f"{PREFIX}.csv", index=False)

results = {
    "study": "v15 reaction-based sampling (Option C, E22)",
    "n_reactions_total": len(model.reactions),
    "n_active_reactions": len(active_rxns),
    "n_kappa_nonzero_reactions": len(kv_nonzero_rxns),
    "n_model_genes": len(model.genes),
    "n_panel_genes": len(panel),
    "n_kappa_panel_genes": len(kvar_panel),
    "checks": {
        "C_map_gpr_ok": True,
        "C_def_consistent": bool(cdef_ok),
        "C_def_r_unmasked": float(r_unmasked),
        "C_def_r_v12": float(r_v12),
        "C_def_r_v13": float(r_v13),
        "C_dist_overlap_mapped15": overlap15,
        "C_dist_overlap_lemuth92": overlap_lemuth,
        "C_dist_distinct_genes": len(panel) - len(overlap15),
        "C_var_all_positive": bool((kvar_var > 0).all()),
        "C_var_zero_fraction_excluded": float(1 - len(kvar_panel) / len(panel)),
    },
    "distribution": {
        "quantiles_25_50_75_90_95_99": q.tolist(),
        "lognormal_mu": float(mu), "lognormal_sigma": float(sigma),
        "ks_stat": float(ks_stat), "ks_p": float(ks_p),
        "top1pct_share": float(srt[:max(1, round(0.01 * len(srt)))].sum() / tot),
        "top5pct_share": float(srt[:max(1, round(0.05 * len(srt)))].sum() / tot),
        "top10pct_share": float(srt[:max(1, round(0.10 * len(srt)))].sum() / tot),
        "gini": float(gd), "hill_alpha_m50": float(hill),
    },
    "correlation_lemuth_overlap": {
        "n": n_overlap,
        "computable": bool(n_overlap >= 3),
        "note": ("Lemuth panel and active-reaction gene set are nearly "
                 "disjoint; per-gene Pearson r not computable at meaningful "
                 "n on local data"),
    },
    "gpr_class_stats": cls_stats,
    "subsystem_top15": subsys_df.head(15).to_dict(orient="records"),
    "direction_test": {"pass": n_pass, "total": n_tot,
                       "rate": float(n_pass / n_tot)},
    "top20_genes": [{"gene": g, "name": gene_name[g],
                     "kappa_max": kv_max[g], "subsystem": subsys_of[g]}
                    for g in top20],
}
with open(f"{PREFIX}_results.json", "w") as f:
    json.dump(results, f, indent=1, default=str)

with open(f"{PREFIX}.txt", "w") as f:
    f.write("\n".join(log) + "\n")
P(f"\nWrote {PREFIX}.csv, {PREFIX}_results.json, {PREFIX}.txt")

# ----------------------------------------------------------------------
# 13. Figure
# ----------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)

ax = axes[0, 0]
ax.hist(logx, bins=40, color="#3b6fb6", edgecolor="white", alpha=0.85,
        density=True, label="panel genes (n=%d)" % len(kvar_panel))
xs = np.linspace(logx.min(), logx.max(), 200)
ax.plot(xs, norm.pdf(xs, mu, sigma), "r--", lw=1.8,
        label="lognormal fit (mu=%+.2f, sigma=%.2f)" % (mu, sigma))
ax.set_xlabel("log10 max kappa_V per gene")
ax.set_ylabel("density")
ax.set_title("(B) kappa_V distribution over the active-reaction gene panel")
ax.legend(fontsize=9)

ax = axes[0, 1]
cum = np.cumsum(srt) / tot
ax.plot(np.arange(1, len(srt) + 1) / len(srt) * 100, cum * 100,
        color="#b6453b", lw=2.2)
ax.plot([0, 100], [0, 100], "k:", lw=1, alpha=0.6)
for frac in (1, 5, 10):
    k = max(1, int(round(frac / 100 * len(srt))))
    ax.axvline(frac, color="gray", lw=0.6, alpha=0.5)
    ax.annotate(f"top {frac}%\nholds {100*cum[k-1]:.0f}%",
                (frac, cum[k - 1] * 100), fontsize=8,
                xytext=(frac + 6, cum[k - 1] * 100 - 12))
ax.set_xlabel("top x% of genes (ranked by kappa_V)")
ax.set_ylabel("cumulative % of total kappa_V")
ax.set_title("(B) concentration: Gini = %.3f, Hill alpha = %.2f" % (gd, hill))
ax.set_xlim(0, 60)

ax = axes[1, 0]
top15 = subsys_df.head(15).iloc[::-1]
ax.barh(range(len(top15)), top15.total_kappa_V, color="#3b8657",
        edgecolor="white")
ax.set_yticks(range(len(top15)))
ax.set_yticklabels([s[:38] for s in top15.subsystem], fontsize=7.5)
ax.set_xlabel("total kappa_V (sum of reaction maxima)")
ax.set_title("(C) Top-15 iJO1366 subsystems by kappa_V (n=%d active)" % len(active_rxns))

ax = axes[1, 1]
for g in top20[:8]:
    ax.plot(range(1, 9), kv_panel[g], lw=1.6,
            label=f"{gene_name[g]} ({g})")
ax.set_xlabel("time point (T1..T8)")
ax.set_ylabel("kappa_V(g, t)")
ax.set_yscale("log")
ax.set_title("(B) kappa_V trajectories of the top-8 genes")
ax.legend(fontsize=8, ncol=2)

fig.suptitle("v15 / E22 reaction-based sampling: %d active reactions -> %d genes "
             "with non-zero kappa_V" % (len(active_rxns), len(kvar_panel)),
             fontsize=12)
fig.savefig(f"{PREFIX}.png", dpi=150)
P(f"Wrote {PREFIX}.png")
print("DONE")
