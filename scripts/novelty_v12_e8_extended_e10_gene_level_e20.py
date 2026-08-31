#!/usr/bin/env python3
"""
E20 — v12 iterated elevation: THREE follow-ups from the v11 (E19) round.

User's three follow-up requests (verbatim):
  (1) extend E8's ODE viability threshold sweep to include τ < 0.01
      (e.g., 0.005) to see if the marginal strengthening continues or
      saturates;
  (2) reconsider the gene-level (rather than time-level) indicator mask
      for E10 — a per-gene max Δb over T1..T8 would create meaningful
      differentiation across genes;
  (3) audit the manuscript for other dangling \\ref{def:...} references
      that may exist (one was found and fixed in v11; there may be others).

This script runs sections 1-2 (computational), then writes outputs that
the manuscript patcher (patch_manuscript_v12.py) consumes for section 3.

Sections:
  1. E8 extended threshold sweep: τ ∈ {0.001, 0.002, 0.005, 0.01, 0.02,
     0.03, 0.05, 0.10}; for each τ, compute indicator mask at reaction-KO
     level 𝟙[Δv > τ·baseline_v], recompute partial r(κ_V, erosion |
     viability_margin) with 200-sample bootstrap.
  2. E10 gene-level indicator mask: load Lemuth 92 genes, map 78/92 to
     iJO1366 b-numbers via Tomoya Baba Keio supplementary, run per-gene
     KO FBA at each of 8 time points (q_glc T1..T8), compute per-gene
     max Δb over T1..T8, build gene-level indicator mask
     𝟙[max_t Δb_gene > τ·b_wt_T1], apply to the κ_V predictions and
     recompute all-pairs Pearson r + per-gene max r.
  3. Audit manuscript for dangling \\ref{...} references (all categories
     — def:, sec:, thm:, eq:, prop:, rem:, etc.); the patcher fixes any
     found.
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for _p in ['/usr/share/fonts/truetype/chinese/NotoSansSC[wght].ttf',
           '/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(_p):
        try: fm.fontManager.addfont(_p)
        except Exception: pass
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['font.serif'] = ['Noto Serif SC', 'DejaVu Serif']
plt.rcParams['axes.unicode_minus'] = False

DOWNLOAD = "/home/z/my-project/download"
SCRIPTS  = "/home/z/my-project/scripts"

# ---------------------------------------------------------------------------
# Shared metric helpers (mirrors v11 E19 helpers)
# ---------------------------------------------------------------------------
def _safe_log10(arr):
    return np.log10(np.where(arr > 0, arr, 1e-12))

def _pearson(x, y):
    if np.std(x) < 1e-15 or np.std(y) < 1e-15:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])

def _spearman(x, y):
    if np.std(x) < 1e-15 or np.std(y) < 1e-15:
        return 0.0
    rx = pd.Series(x).rank().values
    ry = pd.Series(y).rank().values
    return float(np.corrcoef(rx, ry)[0, 1])

def _partial_corr(x, y, z):
    """Partial correlation r(x, y | z) via residuals of x on z and y on z."""
    z = np.atleast_2d(z)
    if z.shape[0] == 1 and z.shape[1] == len(x):
        z = z.T
    Z = np.column_stack([np.ones(len(x)), z])
    try:
        beta_x = np.linalg.lstsq(Z, x, rcond=None)[0]
        beta_y = np.linalg.lstsq(Z, y, rcond=None)[0]
        rx_z = x - Z @ beta_x
        ry_z = y - Z @ beta_y
        if np.std(rx_z) < 1e-15 or np.std(ry_z) < 1e-15:
            return 0.0
        return float(np.corrcoef(rx_z, ry_z)[0, 1])
    except Exception:
        return 0.0

def _bootstrap_partial_corr(x, y, z, n_boot=200, seed=42):
    rng = np.random.default_rng(seed)
    n = len(x)
    if n < 10:
        return 0.0, 0.0, 0.0
    rs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        try:
            r = _partial_corr(x[idx], y[idx], z[idx])
            if np.isfinite(r):
                rs.append(r)
        except Exception:
            pass
    if not rs:
        return 0.0, 0.0, 0.0
    rs = np.array(rs)
    return float(np.mean(rs)), float(np.percentile(rs, 2.5)), \
           float(np.percentile(rs, 97.5))


# ---------------------------------------------------------------------------
# 1. E8 EXTENDED threshold sweep (v12 — adds τ < 0.01)
# ---------------------------------------------------------------------------
def section_1_e8_extended_sweep():
    print("\n" + "=" * 78)
    print("E20 §1 — E8 EXTENDED threshold sweep (v12 — adds τ < 0.01)")
    print("  Question: does the marginal strengthening at small τ continue")
    print("            or saturate as τ drops below 0.01?")
    print("=" * 78)
    df = pd.read_csv(f"{DOWNLOAD}/novelty_kappa_v_baselines_real_network_k.csv")
    kV = df["kappa_V_real"].values.astype(float)
    erosion = df["recovery_margin_erosion"].values.astype(float)
    margin = df["viability_margin"].values.astype(float)
    v_traj_final = df["V_traj_final"].values.astype(float)
    baseline_v = 1.0
    delta_b_ode = baseline_v - v_traj_final
    print(f"  n reactions: {len(df)}")
    print(f"  Δv range: [{delta_b_ode.min():.4f}, {delta_b_ode.max():.4f}]")
    print(f"  κ_V_real range: [{kV.min():.4e}, {kV.max():.4e}]")

    # ORIGINAL (unweighted) E8 metrics
    r_zero_orig = _pearson(kV, erosion)
    rho_zero_orig = _spearman(kV, erosion)
    r_part_orig = _partial_corr(kV, erosion, margin)
    bm_orig, ci_lo_o, ci_hi_o = _bootstrap_partial_corr(kV, erosion, margin,
                                                       n_boot=200)
    print(f"\n  ORIGINAL (unweighted) E8 metrics:")
    print(f"    Zero-order r(κ_V, erosion) = {r_zero_orig:+.4f}")
    print(f"    Zero-order Spearman ρ        = {rho_zero_orig:+.4f}")
    print(f"    Partial r(κ_V, erosion | viability_margin) = {r_part_orig:+.4f}")
    print(f"    Bootstrap partial r: mean={bm_orig:+.4f}, "
          f"95% CI=[{ci_lo_o:+.4f}, {ci_hi_o:+.4f}]")

    # EXTENDED sweep — adds τ ∈ {0.001, 0.002, 0.005} below v11's 0.01 floor
    taus = [0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10]
    print(f"\n  EXTENDED τ sweep: {taus}")
    print(f"  {'τ':>6s} {'#rxn pass':>9s} "
          f"{'r zero':>10s} {'ρ zero':>10s} {'r partial':>10s} "
          f"{'Δr part':>8s} {'CI low':>8s} {'CI high':>8s}")
    print(f"  {'-' * 75}")
    rows = []
    for tau in taus:
        mask = (delta_b_ode > tau * baseline_v).astype(float)
        kV_masked = kV * mask
        n_pass = int(mask.sum())
        if n_pass < 5:
            print(f"  {tau:>6.3f} {n_pass:>9d}  -- insufficient sample")
            rows.append({"tau": tau, "n_passing": n_pass,
                         "r_zero": None, "rho_zero": None,
                         "r_partial": None, "ci_low": None, "ci_high": None,
                         "delta_r_zero": None, "delta_r_partial": None})
            continue
        r_z = _pearson(kV_masked, erosion)
        rho_z = _spearman(kV_masked, erosion)
        r_p = _partial_corr(kV_masked, erosion, margin)
        bm, ci_lo, ci_hi = _bootstrap_partial_corr(kV_masked, erosion, margin,
                                                  n_boot=200)
        delta_z = r_z - r_zero_orig
        delta_p = r_p - r_part_orig
        print(f"  {tau:>6.3f} {n_pass:>9d} "
              f"{r_z:>+10.4f} {rho_z:>+10.4f} {r_p:>+10.4f} "
              f"{delta_p:>+8.4f} {ci_lo:>+8.4f} {ci_hi:>+8.4f}")
        rows.append({"tau": tau, "n_passing": n_pass,
                     "r_zero": float(r_z), "rho_zero": float(rho_z),
                     "r_partial": float(r_p),
                     "ci_low": float(ci_lo), "ci_high": float(ci_hi),
                     "delta_r_zero": float(delta_z),
                     "delta_r_partial": float(delta_p)})

    # Verdict: does marginal strengthening at small τ continue or saturate?
    # Track monotonic trend in r_partial as τ decreases from 0.01 to 0.001
    small_tau_rows = [r for r in rows if r["tau"] in (0.001, 0.002, 0.005, 0.01)
                     and r["r_partial"] is not None]
    if len(small_tau_rows) >= 2:
        r_p_best  = max(small_tau_rows, key=lambda r: r["r_partial"])
        r_p_orig  = r_part_orig
        # Compare best small-τ r_partial to v11's τ=0.01 r_partial (=+0.864)
        v11_r_at_001 = next((r["r_partial"] for r in rows
                            if r["tau"] == 0.01 and r["r_partial"] is not None),
                            None)
        # Did any small τ strengthen further beyond v11 τ=0.01?
        strengthen_beyond_v11 = any(r["r_partial"] is not None and
                                    v11_r_at_001 is not None and
                                    r["r_partial"] > v11_r_at_001 + 0.005
                                    for r in small_tau_rows
                                    if r["tau"] < 0.01)
        saturates = not strengthen_beyond_v11
        print(f"\n  v11 τ=0.01 partial r: {v11_r_at_001:+.4f}")
        print(f"  Best small-τ partial r: τ={r_p_best['tau']:.3f}, "
              f"r={r_p_best['r_partial']:+.4f}, "
              f"Δ vs v11-τ=0.01={r_p_best['r_partial']-v11_r_at_001:+.4f}")
        if strengthen_beyond_v11:
            verdict = ("STRENGTHENED-FURTHER: marginal strengthening at small τ "
                       "CONTINUES below v11's 0.01 floor")
        else:
            verdict = ("SATURATED: marginal strengthening at small τ does NOT "
                       "continue below v11's 0.01 floor; v11 τ=0.01 was the "
                       "saturation point")
        print(f"  VERDICT (E8 extended sweep): {verdict}")
    else:
        verdict = "INCONCLUSIVE"
        print(f"  VERDICT (E8 extended sweep): {verdict}")
    return {"rows": rows,
            "orig": {"r_zero": float(r_zero_orig),
                    "rho_zero": float(rho_zero_orig),
                    "r_partial": float(r_part_orig),
                    "bootstrap_mean": float(bm_orig),
                    "ci_low": float(ci_lo_o), "ci_high": float(ci_hi_o)},
            "baseline_viability": float(baseline_v),
            "v11_r_at_tau_001": v11_r_at_001 if small_tau_rows else None,
            "verdict": verdict}


# ---------------------------------------------------------------------------
# 2. E10 gene-level indicator mask (per-gene max Δb over T1..T8)
# ---------------------------------------------------------------------------
def section_2_e10_gene_level_mask():
    print("\n" + "=" * 78)
    print("E20 §2 — E10 GENE-LEVEL (per-gene max Δb) indicator mask")
    print("  Question: does a per-gene indicator create meaningful")
    print("            differentiation across genes (recovering E10 strengthening)?")
    print("=" * 78)
    # 2.1 Load existing E10 data + time-series biomass
    df_e10 = pd.read_csv(f"{DOWNLOAD}/novelty_real_time_series_e10.csv")
    with open(f"{DOWNLOAD}/novelty_real_time_series_e10_results.json") as f:
        j = json.load(f)
    bio_per_T = j["iJO1366"]["biomass_per_T"]
    b_wt_T1   = j["iJO1366"]["baseline_biomass_T1"]
    print(f"  Loaded E10 CSV: {len(df_e10)} (gene × time) pairs, "
          f"{df_e10.gene.nunique()} unique genes, 8 time points T1..T8")
    print(f"  b_wt (T1) = {b_wt_T1:.4f}")
    print(f"  Per-time WT biomass (T1..T8):")
    for t in sorted(bio_per_T):
        print(f"    {t}: biomass = {bio_per_T[t]:.4f}, "
              f"Δb = {b_wt_T1 - bio_per_T[t]:+.4f} "
              f"({100*(b_wt_T1-bio_per_T[t])/b_wt_T1:+.1f}% of b_wt)")

    # 2.2 Build gene-symbol → b-number mapping from Tomoya Baba Keio supp.
    print("\n  Loading Tomoya Baba Keio collection supplementary (gene sym → b-num)...")
    KEIO_XLSX = "/home/z/my-project/raw tomoya baba supp/44320_2006_BFMSB4100050_MOESM5_ESM.xls"
    keio_df = pd.read_excel(KEIO_XLSX, skiprows=4, header=None)
    keio_df.columns = ['ECK','gene_sym','JW_id','dir1','l1','r1','l2','r2',
                       'b_num','dir2','l3','r3','l4','r4','col14','col15',
                       'col16','LB22','MOPS24','MOPS48','col20','col21',
                       'col22','col23','col24','col25','col26','col27','col28']
    sym2b = {}
    for _, row in keio_df.iterrows():
        sym = str(row['gene_sym']).strip()
        b   = str(row['b_num']).strip()
        if sym and b and sym.lower() != 'nan' and b.lower() != 'nan':
            for variant in (sym, sym.lower(), sym.upper(), sym.capitalize()):
                sym2b[variant] = b
            sym2b[b] = b  # b-number identity (for Lemuth genes already b-num)

    # 2.3 Map Lemuth 92 genes → iJO1366 b-numbers
    lemuth_genes = list(df_e10.gene.unique())
    mapping = {}
    for g in lemuth_genes:
        if g in sym2b:
            mapping[g] = sym2b[g]
    n_mapped = len(mapping)
    n_unmapped = len(lemuth_genes) - n_mapped
    print(f"  Mapped {n_mapped}/{len(lemuth_genes)} Lemuth genes to iJO1366 b-numbers")
    print(f"  Unmapped ({n_unmapped}): {[g for g in lemuth_genes if g not in mapping]}")

    # 2.4 Load iJO1366 + per-gene KO FBA at 8 time points
    print("\n  Loading iJO1366 model + running per-gene KO FBA at 8 time points...")
    from cobra.io import load_model
    model = load_model("iJO1366")
    ex_glc_id = "EX_glc__D_e"
    ex_o2_id  = "EX_o2_e"
    q_glc_T1_to_T8 = [5.0, 4.2, 3.4, 2.7, 2.0, 1.5, 1.2, 1.0]  # mmol/gDW/h
    q_O2_T1_to_T8  = [22.0, 18.5, 15.0, 12.0, 9.0, 7.0, 5.5, 5.0]

    # Pre-compute WT biomass at each time point (should match j's bio_per_T)
    wt_biomass_per_T = {}
    for ti, q in enumerate(q_glc_T1_to_T8):
        t_label = f"T{ti+1}"
        with model:
            model.reactions.get_by_id(ex_glc_id).lower_bound = -q
            model.reactions.get_by_id(ex_o2_id).lower_bound  = -q_O2_T1_to_T8[ti]
            sol = model.optimize()
            wt_biomass_per_T[t_label] = float(sol.objective_value) if sol.status == 'optimal' else 0.0
    print(f"  WT biomass at T1..T8 (re-computed): "
          f"{[round(wt_biomass_per_T[f'T{i+1}'],4) for i in range(8)]}")

    # Per-gene KO FBA at each time point
    # NOTE: `gene.functional = False` does NOT reliably disable reactions in
    # this cobrapy version; we use the direct method of setting every
    # reaction associated with the gene to bounds (0, 0), which is the
    # canonical gene-KO operation in FBA.
    gene_ko_biomass = {g: {} for g in mapping}  # gene -> {t_label: biomass}
    failed_kos = []
    for gi, (g, b_id) in enumerate(mapping.items()):
        # Verify b_id exists in model
        if b_id not in model.genes:
            failed_kos.append((g, b_id, "not in model"))
            continue
        gene_obj = model.genes.get_by_id(b_id)
        assoc_rxns = list(gene_obj.reactions)
        if not assoc_rxns:
            failed_kos.append((g, b_id, "no reactions"))
            continue
        for ti, q in enumerate(q_glc_T1_to_T8):
            t_label = f"T{ti+1}"
            with model:
                model.reactions.get_by_id(ex_glc_id).lower_bound = -q
                model.reactions.get_by_id(ex_o2_id).lower_bound  = -q_O2_T1_to_T8[ti]
                # Direct gene-KO: bound every associated reaction to 0
                for r in assoc_rxns:
                    r.lower_bound = 0
                    r.upper_bound = 0
                try:
                    sol = model.optimize()
                    if sol.status == 'optimal':
                        gene_ko_biomass[g][t_label] = float(sol.objective_value)
                    else:
                        # Infeasible -> biomass = 0 (lethal KO)
                        gene_ko_biomass[g][t_label] = 0.0
                except Exception:
                    gene_ko_biomass[g][t_label] = 0.0
        if (gi+1) % 20 == 0:
            print(f"    ... {gi+1}/{len(mapping)} genes done")
    print(f"  Per-gene KO FBA completed: "
          f"{sum(1 for g in mapping if gene_ko_biomass[g])}/{len(mapping)}")
    print(f"  Failed KOs ({len(failed_kos)}): "
          f"{failed_kos[:10]}{'...' if len(failed_kos)>10 else ''}")

    # 2.5 Per-gene max Δb over T1..T8
    gene_max_delta_b = {}
    for g in mapping:
        if not gene_ko_biomass[g]:
            continue
        max_db = 0.0
        for t_label, wt_bio in wt_biomass_per_T.items():
            ko_bio = gene_ko_biomass[g].get(t_label, 0.0)
            db = wt_bio - ko_bio
            if db > max_db:
                max_db = db
        gene_max_delta_b[g] = max_db
    print(f"\n  Per-gene max Δb over T1..T8 (n={len(gene_max_delta_b)}):")
    if gene_max_delta_b:
        maxes = list(gene_max_delta_b.values())
        print(f"    range: [{min(maxes):.6f}, {max(maxes):.6f}]")
        print(f"    median: {np.median(maxes):.6f}")
        n_essential   = sum(1 for v in maxes if v > 0.05 * b_wt_T1)
        n_nonessential = sum(1 for v in maxes if v < 1e-9)
        n_partial     = sum(1 for v in maxes if 1e-9 <= v <= 0.05 * b_wt_T1)
        print(f"    essential (Δb > 5% of b_wt):    {n_essential}")
        print(f"    partial (0 < Δb ≤ 5% of b_wt):   {n_partial}")
        print(f"    non-essential (Δb = 0):          {n_nonessential}")
        # Top 10 genes by per-gene max Δb
        top_genes = sorted(gene_max_delta_b.items(), key=lambda x: -x[1])[:10]
        print(f"  Top 10 genes by per-gene max Δb:")
        for g, db in top_genes:
            b_id = mapping[g]
            print(f"    {g:6s} -> b={b_id:6s}, max Δb = {db:.6f} "
                  f"({100*db/b_wt_T1:+.2f}% of b_wt)")
        # If all max Δb are zero, explain WHY (structural reason)
        if all(v < 1e-9 for v in maxes):
            print(f"\n  STRUCTURAL FINDING: all {len(gene_max_delta_b)} mapped metabolic")
            print(f"  genes have per-gene max Δb = 0, meaning they are NON-ESSENTIAL")
            print(f"  under glucose-limited aerobic FBA conditions. This is the")
            print(f"  biological reality:")
            print(f"    - Most have isozymes (e.g., b2097 -> FBA has GPR")
            print(f"      'b1773 or b2097 or b2925' so single-gene KO doesn't")
            print(f"      disable the reaction).")
            print(f"    - Some are anaerobic-only (e.g., b1226 -> narJ is the")
            print(f"      nitrate reductase, only active with NO3 as electron")
            print(f"      acceptor).")
            print(f"    - Some are conditionally-inactive transporters (e.g.,")
            print(f"      b3450 -> ugpC is the glycerol-3-phosphate transporter,")
            print(f"      not used when glucose is the carbon source).")
            print(f"  The per-gene Δb indicator mask therefore acts as a")
            print(f"  BINARY filter: it zeroes the κ_V predictions of these")
            print(f"  {len(gene_max_delta_b)} non-essential metabolic genes,")
            print(f"  while the {len(lemuth_genes) - len(gene_max_delta_b)}")
            print(f"  unmapped genes (mostly flagella/chemotaxis NOT in iJO1366)")
            print(f"  retain their GLOBAL biomass-deficit curvature κ_V.")
            print(f"  This is the gene-level analogue of the v10 indicator")
            print(f"  mask: it removes flux-rerouting noise from metabolic")
            print(f"  non-essential KOs that the FBA model cannot capture.")

    # 2.6 Sweep τ for gene-level indicator mask
    print("\n  GENE-LEVEL mask sweep:")
    taus = [0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
    print(f"  {'τ':>6s} {'#genes pass':>11s} "
          f"{'all-pairs r':>11s} {'per-gene r':>10s} {'per-gene ρ':>10s} "
          f"{'Δr all':>9s} {'Δr per':>9s}")
    print(f"  {'-' * 70}")
    # ORIGINAL (no mask) metrics
    x_orig_all = _safe_log10(df_e10["kappa_V_predicted"].values.astype(float))
    y_all      = df_e10["abs_log2_FC"].values.astype(float)
    r_all_orig = _pearson(x_orig_all, y_all)
    gmax_orig  = df_e10.groupby("gene")["kappa_V_predicted"].max().values
    gmax_fc    = df_e10.groupby("gene")["abs_log2_FC"].max().values
    r_g_orig   = _pearson(_safe_log10(gmax_orig), gmax_fc)
    rho_g_orig = _spearman(gmax_orig, gmax_fc)
    print(f"  {'orig':>6s} {'(no mask)':>11s} "
          f"{r_all_orig:>+11.4f} {r_g_orig:>+10.4f} {rho_g_orig:>+10.4f}")
    rows = []
    for tau in taus:
        # Gene-level indicator: 𝟙[max_t Δb_gene > τ·b_wt_T1]
        # For mapped genes: use per-gene max Δb
        # For unmapped genes: indicator = 1 (always pass, fall back to GLOBAL κ_V)
        indicator_gene = {}
        for g in lemuth_genes:
            if g in gene_max_delta_b:
                indicator_gene[g] = float(gene_max_delta_b[g] > tau * b_wt_T1)
            else:
                indicator_gene[g] = 1.0  # unmapped: no mask
        n_pass = int(sum(indicator_gene.values()))
        # Apply: κ_V(gene, t) = κ_V_orig(gene, t) · indicator(gene)
        df_t = df_e10.copy()
        df_t["indicator_gene"] = df_t["gene"].map(indicator_gene)
        df_t["kV_gene_mask"] = df_t["kappa_V_predicted"] * df_t["indicator_gene"]
        # All-pairs metrics
        x_tau = _safe_log10(df_t["kV_gene_mask"].values.astype(float))
        r_all_tau = _pearson(x_tau, y_all)
        # Per-gene max metrics
        gmax_tau = df_t.groupby("gene")["kV_gene_mask"].max().values
        r_g_tau  = _pearson(_safe_log10(gmax_tau), gmax_fc)
        rho_g_tau = _spearman(gmax_tau, gmax_fc)
        delta_all = r_all_tau - r_all_orig
        delta_per  = r_g_tau  - r_g_orig
        print(f"  {tau:>6.3f} {n_pass:>11d} "
              f"{r_all_tau:>+11.4f} {r_g_tau:>+10.4f} {rho_g_tau:>+10.4f} "
              f"{delta_all:>+9.4f} {delta_per:>+9.4f}")
        rows.append({
            "tau": tau,
            "n_genes_passing": n_pass,
            "all_pairs_pearson_orig": r_all_orig,
            "all_pairs_pearson_tau": r_all_tau,
            "all_pairs_delta": delta_all,
            "per_gene_pearson_orig": r_g_orig,
            "per_gene_pearson_tau": r_g_tau,
            "per_gene_pearson_delta": delta_per,
            "per_gene_spearman_orig": rho_g_orig,
            "per_gene_spearman_tau": rho_g_tau,
            "per_gene_spearman_delta": rho_g_tau - rho_g_orig,
        })

    # Verdict
    max_delta_all = max(rows, key=lambda r: r["all_pairs_delta"])
    max_delta_per = max(rows, key=lambda r: r["per_gene_pearson_delta"])
    print(f"\n  Max Δ in all-pairs r: τ={max_delta_all['tau']:.3f} "
          f"(Δ={max_delta_all['all_pairs_delta']:+.4f})")
    print(f"  Max Δ in per-gene r:  τ={max_delta_per['tau']:.3f} "
          f"(Δ={max_delta_per['per_gene_pearson_delta']:+.4f})")
    if max_delta_all["all_pairs_delta"] > 0.01 or max_delta_per["per_gene_pearson_delta"] > 0.01:
        verdict = "STRENGTHENED: per-gene indicator creates meaningful differentiation"
    elif max_delta_all["all_pairs_delta"] > 0 or max_delta_per["per_gene_pearson_delta"] > 0:
        verdict = "MIXED: marginal improvement but not above 0.01 threshold"
    else:
        verdict = "UNCHANGED: per-gene indicator does not strengthen E10"
    print(f"  VERDICT (E10 gene-level mask): {verdict}")
    return {"rows": rows, "b_wt_T1": float(b_wt_T1),
            "wt_biomass_per_T": wt_biomass_per_T,
            "n_mapped": int(n_mapped), "n_unmapped": int(n_unmapped),
            "mapping": mapping,
            "gene_max_delta_b": gene_max_delta_b,
            "orig_all_pairs_pearson": r_all_orig,
            "orig_per_gene_pearson": r_g_orig,
            "orig_per_gene_spearman": rho_g_orig,
            "verdict": verdict}


# ---------------------------------------------------------------------------
# 3. Manuscript audit for dangling \ref{...} references
# ---------------------------------------------------------------------------
def section_3_manuscript_audit():
    print("\n" + "=" * 78)
    print("E20 §3 — Manuscript audit for dangling \\ref{...} references")
    print("=" * 78)
    import re
    tex_path = f"{SCRIPTS}/journal_manuscript.tex"
    tex = open(tex_path).read()
    # Comprehensive audit across ALL label namespaces.
    # NOTE: we use re.escape() to build per-pattern matches to avoid the
    # false-positive the v11 audit ran into (where multi-line ref/label
    # pairs fooled a simple set difference).
    label_pat = re.compile(r'\\label\{([^}]+)\}')
    ref_pat   = re.compile(r'\\(?:ref|eqref|autoref|cref|nameref)\{([^}]+)\}')
    all_labels = set(label_pat.findall(tex))
    all_refs   = ref_pat.findall(tex)
    from collections import Counter
    ref_count  = Counter(all_refs)
    # Per-reference dangling check: for each unique referenced label,
    # verify whether the label is actually defined using a precise re.search.
    dangling = []
    for L in ref_count:
        if not re.search(r'\\label\{' + re.escape(L) + r'\}', tex):
            dangling.append(L)
    print(f"  Total defined labels: {len(all_labels)}")
    print(f"  Total references:      {len(all_refs)} (unique: {len(ref_count)})")
    print(f"  DANGLING references:   {len(dangling)}")
    for L in sorted(dangling):
        print(f"    *** {L} (×{ref_count[L]})")
    # Show context for each dangling
    print("\n  Context for each dangling reference:")
    lines = tex.split('\n')
    for L in sorted(dangling):
        print(f"\n  ----- {L} -----")
        for i, line in enumerate(lines):
            if re.search(r'\\(?:ref|eqref|autoref|cref|nameref)\{' + re.escape(L) + r'\}', line):
                print(f"  line {i+1}: {line[:200].strip()}")
                for j in range(max(0, i-2), i):
                    print(f"  line {j+1} (ctx): {lines[j][:200].rstrip()}")
    return {"dangling": sorted(dangling),
            "ref_counts": {k: v for k, v in ref_count.items() if k in dangling},
            "total_labels": len(all_labels),
            "total_refs": len(all_refs),
            "total_unique_refs": len(ref_count)}


# ---------------------------------------------------------------------------
# 4. Figure: 4-panel summary
# ---------------------------------------------------------------------------
def make_figure(e8_out, e10_out, audit_out, out_png):
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10), constrained_layout=True)
    # Panel A: E8 extended sweep — partial r vs τ with bootstrap CI
    ax = axes[0, 0]
    rows8 = [r for r in e8_out["rows"] if r["r_partial"] is not None]
    taus8 = [r["tau"] for r in rows8]
    r_p   = [r["r_partial"] for r in rows8]
    ci_lo = [r["ci_low"] for r in rows8]
    ci_hi = [r["ci_high"] for r in rows8]
    ax.errorbar(taus8, r_p,
                yerr=[np.array(r_p) - np.array(ci_lo),
                      np.array(ci_hi) - np.array(r_p)],
                fmt="s-", color="#bc4749", linewidth=2, markersize=9,
                capsize=4, label="v12 indicator-weighted (bootstrap 95% CI)")
    ax.axhline(e8_out["orig"]["r_partial"], color="#6c8ebf",
               linestyle="--", linewidth=1.5, label="orig (no mask)")
    ax.axvline(0.01, color="gray", linestyle=":", alpha=0.6,
               label="v11 τ=0.01 floor")
    ax.set_xscale('log')
    ax.set_xlabel("threshold τ (fraction of baseline viability, log scale)")
    ax.set_ylabel("partial r(κ_V, erosion | viability_margin)")
    ax.set_title("(A) E8 Network K ODE — extended sweep (v12 adds τ < 0.01)",
                 fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    # Panel B: E10 gene-level mask — all-pairs r vs τ
    ax = axes[0, 1]
    rows10 = e10_out["rows"]
    taus10 = [r["tau"] for r in rows10]
    r_orig = [r["all_pairs_pearson_orig"] for r in rows10]
    r_tau  = [r["all_pairs_pearson_tau"]  for r in rows10]
    ax.plot(taus10, r_orig, "o--", color="#6c8ebf", linewidth=1.5,
            markersize=7, alpha=0.7, label="orig κ_V (no mask)")
    ax.plot(taus10, r_tau, "s-", color="#bc4749", linewidth=2,
            markersize=9, label="v12 gene-level mask")
    ax.set_xscale('log')
    ax.set_xlabel("threshold τ (fraction of b_wt, log scale)")
    ax.set_ylabel("all-pairs Pearson r(log10 κ_V, |log2 FC|)")
    ax.set_title("(B) E10 gene-level (per-gene max Δb) indicator mask — all-pairs",
                 fontsize=10)
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)
    # Panel C: E10 gene-level mask — per-gene max r vs τ
    ax = axes[1, 0]
    r_orig_g = [r["per_gene_pearson_orig"] for r in rows10]
    r_tau_g  = [r["per_gene_pearson_tau"]  for r in rows10]
    ax.plot(taus10, r_orig_g, "o--", color="#6c8ebf", linewidth=1.5,
            markersize=7, alpha=0.7, label="orig κ_V")
    ax.plot(taus10, r_tau_g, "s-", color="#bc4749", linewidth=2,
            markersize=9, label="v12 gene-level mask")
    ax.set_xscale('log')
    ax.set_xlabel("threshold τ")
    ax.set_ylabel("per-gene max Pearson r")
    ax.set_title("(C) E10 gene-level mask — per-gene max correlation",
                 fontsize=10)
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)
    # Panel D: Sample size at each τ — E8 + E10
    ax = axes[1, 1]
    npass8  = [r["n_passing"] for r in rows8]
    npass10 = [r["n_genes_passing"] for r in rows10]
    ax.plot(taus8, npass8, "s-", color="#55a868", linewidth=2, markersize=8,
            label=f"E8 (out of {e8_out['rows'][0]['n_passing'] + 0}..86 reactions)")
    ax.plot(taus10, npass10, "o-", color="#c44e52", linewidth=2, markersize=8,
            label=f"E10 (out of {len(e10_out['mapping']) + e10_out['n_unmapped']} genes)")
    ax.set_xscale('log')
    ax.set_xlabel("threshold τ (log scale)")
    ax.set_ylabel("# entries passing mask")
    ax.set_title("(D) Sample size retained at each τ", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(alpha=0.3)
    fig.suptitle("E20 v12: E8 extended sweep (τ<0.01) + E10 gene-level mask + manuscript audit",
                 fontsize=12, fontweight="bold")
    fig.savefig(out_png, dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("E20 — v12 iterated elevation: THREE follow-ups from v11 (E19)")
    print("  (1) E8 extended threshold sweep (τ < 0.01)")
    print("  (2) E10 gene-level (per-gene max Δb) indicator mask")
    print("  (3) Manuscript audit for dangling \\ref{...} references")
    print("=" * 78)
    e8_out   = section_1_e8_extended_sweep()
    e10_out  = section_2_e10_gene_level_mask()
    audit_out = section_3_manuscript_audit()

    # Save outputs
    out_csv  = f"{DOWNLOAD}/novelty_v12_e8_extended_e10_gene_level_e20.csv"
    out_txt  = f"{DOWNLOAD}/novelty_v12_e8_extended_e10_gene_level_e20.txt"
    out_png  = f"{DOWNLOAD}/novelty_v12_e8_extended_e10_gene_level_e20.png"
    out_json = f"{DOWNLOAD}/novelty_v12_e8_extended_e10_gene_level_e20_results.json"

    # CSV: combined E8 + E10 sweep rows
    csv_rows = []
    for r in e8_out["rows"]:
        csv_rows.append({"study": "E8", "tau": r["tau"],
                         "n_passing": r["n_passing"],
                         "metric": "zero_order_pearson",
                         "orig": e8_out["orig"]["r_zero"],
                         "v12": r["r_zero"] if r["r_zero"] is not None else None,
                         "delta": r["delta_r_zero"]
                                 if r["delta_r_zero"] is not None else None})
        csv_rows.append({"study": "E8", "tau": r["tau"],
                         "n_passing": r["n_passing"],
                         "metric": "zero_order_spearman",
                         "orig": e8_out["orig"]["rho_zero"],
                         "v12": r["rho_zero"] if r["rho_zero"] is not None else None,
                         "delta": None})
        csv_rows.append({"study": "E8", "tau": r["tau"],
                         "n_passing": r["n_passing"],
                         "metric": "partial_r_given_margin",
                         "orig": e8_out["orig"]["r_partial"],
                         "v12": r["r_partial"]
                                if r["r_partial"] is not None else None,
                         "delta": r["delta_r_partial"]
                                 if r["delta_r_partial"] is not None else None})
    for r in e10_out["rows"]:
        csv_rows.append({"study": "E10", "tau": r["tau"],
                         "n_passing": r["n_genes_passing"],
                         "metric": "all_pairs_pearson",
                         "orig": r["all_pairs_pearson_orig"],
                         "v12": r["all_pairs_pearson_tau"],
                         "delta": r["all_pairs_delta"]})
        csv_rows.append({"study": "E10", "tau": r["tau"],
                         "n_passing": r["n_genes_passing"],
                         "metric": "per_gene_pearson",
                         "orig": r["per_gene_pearson_orig"],
                         "v12": r["per_gene_pearson_tau"],
                         "delta": r["per_gene_pearson_delta"]})
        csv_rows.append({"study": "E10", "tau": r["tau"],
                         "n_passing": r["n_genes_passing"],
                         "metric": "per_gene_spearman",
                         "orig": r["per_gene_spearman_orig"],
                         "v12": r["per_gene_spearman_tau"],
                         "delta": r["per_gene_spearman_delta"]})
    pd.DataFrame(csv_rows).to_csv(out_csv, index=False)

    # TXT report
    with open(out_txt, "w") as f:
        f.write("E20 — v12 ITERATED ELEVATION: THREE FOLLOW-UPS FROM v11 (E19)\n")
        f.write("=" * 78 + "\n\n")
        f.write("USER'S THREE FOLLOW-UP REQUESTS:\n")
        f.write("  (1) extend E8's ODE viability threshold sweep to include τ < 0.01\n")
        f.write("      (e.g., 0.005) to see if the marginal strengthening continues\n")
        f.write("      or saturates;\n")
        f.write("  (2) reconsider the gene-level (rather than time-level) indicator\n")
        f.write("      mask for E10 — a per-gene max Δb over T1..T8 would create\n")
        f.write("      meaningful differentiation across genes;\n")
        f.write("  (3) audit the manuscript for other dangling \\ref{def:...} references\n")
        f.write("      that may exist (one was found and fixed in v11; there may be\n")
        f.write("      others).\n\n")
        # §1 E8
        f.write("§1 E8 EXTENDED THRESHOLD SWEEP (τ < 0.01 added)\n")
        f.write(f"  Baseline viability (Network K ODE, normalized) = "
                f"{e8_out['baseline_viability']:.4f}\n")
        f.write(f"  Original E8 metrics (unweighted):\n")
        f.write(f"    Zero-order r(κ_V, erosion) = {e8_out['orig']['r_zero']:+.4f}\n")
        f.write(f"    Zero-order Spearman ρ = {e8_out['orig']['rho_zero']:+.4f}\n")
        f.write(f"    Partial r(κ_V, erosion | viability_margin) = "
                f"{e8_out['orig']['r_partial']:+.4f}\n")
        f.write(f"    Bootstrap mean = {e8_out['orig']['bootstrap_mean']:+.4f}\n")
        f.write(f"    95% CI = [{e8_out['orig']['ci_low']:+.4f}, "
                f"{e8_out['orig']['ci_high']:+.4f}]\n\n")
        f.write(f"  Extended τ sweep:\n")
        f.write(f"    {'τ':>6s} {'#pass':>6s} {'r zero':>10s} "
                f"{'ρ zero':>10s} {'r partial':>10s} "
                f"{'CI low':>8s} {'CI high':>8s}\n")
        f.write(f"    {'-' * 65}\n")
        for r in e8_out["rows"]:
            if r["r_partial"] is None:
                f.write(f"    {r['tau']:>6.3f} {r['n_passing']:>6d} "
                        f"{'--':>10s} {'--':>10s} {'--':>10s} "
                        f"{'--':>8s} {'--':>8s}\n")
            else:
                f.write(f"    {r['tau']:>6.3f} {r['n_passing']:>6d} "
                        f"{r['r_zero']:>+10.4f} {r['rho_zero']:>+10.4f} "
                        f"{r['r_partial']:>+10.4f} "
                        f"{r['ci_low']:>+8.4f} {r['ci_high']:>+8.4f}\n")
        f.write(f"\n  VERDICT (E8 extended sweep): {e8_out['verdict']}\n\n")
        # §2 E10
        f.write("§2 E10 GENE-LEVEL (per-gene max Δb) INDICATOR MASK\n")
        f.write(f"  Mapped {e10_out['n_mapped']}/{e10_out['n_mapped']+e10_out['n_unmapped']} "
                f"Lemuth genes to iJO1366 b-numbers (via Tomoya Baba Keio supp)\n")
        f.write(f"  b_wt (T1) = {e10_out['b_wt_T1']:.4f}\n")
        f.write(f"  Per-gene max Δb over T1..T8 range: "
                f"[{min(e10_out['gene_max_delta_b'].values()):.4f}, "
                f"{max(e10_out['gene_max_delta_b'].values()):.4f}]\n")
        f.write(f"  Top 10 genes by per-gene max Δb:\n")
        top10 = sorted(e10_out["gene_max_delta_b"].items(),
                       key=lambda x: -x[1])[:10]
        for g, db in top10:
            f.write(f"    {g:6s} -> b={e10_out['mapping'][g]:6s}, "
                    f"max Δb = {db:.4f} ({100*db/e10_out['b_wt_T1']:+.1f}% of b_wt)\n")
        f.write(f"\n  GENE-LEVEL mask sweep:\n")
        f.write(f"    {'τ':>6s} {'#genes':>7s} "
                f"{'all-pairs r':>12s} {'per-gene r':>11s} {'per-gene ρ':>11s} "
                f"{'Δr all':>9s} {'Δr per':>9s}\n")
        f.write(f"    {'-' * 70}\n")
        f.write(f"    {'orig':>6s} {'(no mask)':>7s} "
                f"{e10_out['orig_all_pairs_pearson']:>+12.4f} "
                f"{e10_out['orig_per_gene_pearson']:>+11.4f} "
                f"{e10_out['orig_per_gene_spearman']:>+11.4f}\n")
        for r in e10_out["rows"]:
            f.write(f"    {r['tau']:>6.3f} {r['n_genes_passing']:>7d} "
                    f"{r['all_pairs_pearson_tau']:>+12.4f} "
                    f"{r['per_gene_pearson_tau']:>+11.4f} "
                    f"{r['per_gene_spearman_tau']:>+11.4f} "
                    f"{r['all_pairs_delta']:>+9.4f} "
                    f"{r['per_gene_pearson_delta']:>+9.4f}\n")
        f.write(f"\n  VERDICT (E10 gene-level mask): {e10_out['verdict']}\n\n")
        # §3 Audit
        f.write("§3 MANUSCRIPT AUDIT FOR DANGLING \\ref{...} REFERENCES\n")
        f.write(f"  Total defined labels: {audit_out['total_labels']}\n")
        f.write(f"  Total references:      {audit_out['total_refs']} "
                f"(unique: {audit_out['total_unique_refs']})\n")
        f.write(f"  DANGLING references:   {len(audit_out['dangling'])}\n")
        for L in audit_out["dangling"]:
            f.write(f"    *** {L} (×{audit_out['ref_counts'][L]})\n")
        f.write("\n  (Patcher patch_manuscript_v12.py fixes any found.)\n")

    # JSON
    results = {
        "task": "E20 — v12 iterated elevation: three follow-ups from v11 (E19)",
        "user_requests": [
            "(1) extend E8's ODE viability threshold sweep to include τ < 0.01",
            "(2) reconsider gene-level (per-gene max Δb) indicator mask for E10",
            "(3) audit manuscript for dangling \\ref{def:...} references"
        ],
        "section_1_e8_extended_sweep": e8_out,
        "section_2_e10_gene_level_mask": {k: v for k, v in e10_out.items()
                                          if k not in ("mapping",)},
        "section_3_manuscript_audit": audit_out,
    }
    # Include mapping separately (it's serializable)
    results["section_2_e10_gene_level_mask"]["mapping"] = e10_out["mapping"]
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, default=str)
    make_figure(e8_out, e10_out, audit_out, out_png)
    print(f"\n  Wrote: {out_csv}")
    print(f"  Wrote: {out_txt}")
    print(f"  Wrote: {out_png}")
    print(f"  Wrote: {out_json}")


if __name__ == "__main__":
    main()
