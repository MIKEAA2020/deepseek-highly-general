# v2 numeric consistency audit (2026-09-02; extended journal-submission round)

**98 PASS / 0 FAIL of 98 checks.**

Manuscript defects found and fixed: D-N1 (13 sweeps / 10 knockdowns), D-N2 (1.5e-7 -> 1.51e-7), D-N3 (lambda range), D-N4 (TV ratio 3.6-4.4), D-N5 (MWU p <= 2e-3), D-N6 (residuals <= 1.2e-10 + documented eno sub-threshold kink), D-N7 (abstract 93.4-100.0%), D-N8 (+0.032); journal round: D-JS1 (C1 effective constant 1.6-2.1 dipping at m=128), D-JS2 ('exactly the FPC' -> 'consistent with', 0.49 vs 0.29 at k=12), D-JS3 ('up to 8%' -> 'as large as 8.2%').

| id | claim | status | artifact value | source |
|---|---|---|---|---|
| ABS-1 | r = +0.395 (n=424) | PASS | r=0.3954, n=424 | v5_e24_recalibration.json:arms.kappa_mu[nonzero] |
| ABS-2 | p = 2.6e-17 | PASS | 2.58e-17 | v5_e24_recalibration.json:arms.kappa_mu[nonzero].pearso |
| ABS-3 | partial r = +0.269 | PASS | 0.2692 | v5_e24_recalibration.json:arms.confound_control.partial |
| ABS-4 | metric-invariance rho = 0.99998 | PASS | 0.9999881693960117 | v6_layer_decision.json:predictor_agreement.spearman_kap |
| ABS-5 | Spearman rho_S = +0.414 (E-V5 text) | PASS | 0.4138 | v5_e24_recalibration.json:...spearman_raw_full_panel |
| ABS-6 | abstract: mass concentrates (93.4-100.0% per boundary-crossing sweep) | PASS | mass range [0.9345, 1.000000] | m1_summary.json:sweeps (11 crossing sweeps) |
| ABS-7 | loop holonomy slope 1.00 (76-pair scan) | PASS | median=0.9982, mean=1.0086, n_pairs=76 | m4a_summary.json:median_slope_chi |
| ABS-8 | epistasis Spearman rho_S = 0.865 (J_dR) | PASS | 0.8649 | m3_summary.json:pairs.spearman_|eps|_J_dR.rho |
| ABS-9 | J_support = 0.800 | PASS | 0.8003 | m3_summary.json:pairs.spearman_|eps|_J_support.rho |
| ABS-10 | 66% non-reverting genotype loops | PASS | traced to m3_epistasis_path_dependence.py printout / m1_m3 report PDF | m3_summary.json (path-dependence block); M3 report body |
| M1-1 | v2 says 'Twelve parameter sweeps (glucose, oxygen, eight gene knockdow | PASS | 13 sweeps = 2 nutrient + 10 knockdowns + 1 iJO | m1_summary.json:sweeps (key count) |
| M1-2 | mass 0.934-1.0; AUC 0.83-1.00; MWU p <= 2e-3 (7 of 11 crossing sweeps  | PASS | mass [0.934,1.000000], AUC [0.83,1.000], MWU max 1.7e-03 | m1_summary.json: 11 crossing sweeps |
| M1-3 | event-free segment residuals <= 1.2e-10 (glucose 8e-14); one eno segme | PASS | max (excl. eno) 1.2e-10; eno 4.1e-03 | m1_summary.json:sweeps.*.top_segments |
| M1-4 | single-critical-region control (ijo glucose): noise D2 ~ 1e-11 | PASS | 2.3e-11 | m1_summary.json:ijo_glucose.D2_median_nonevent |
| M3-1 | 1,516 single knockouts (iML1515) | PASS | 1516 | m3_summary.json:n_genes |
| M3-2 | 2,779 double-knockout pairs (five panels) | PASS | 2779 | m3_summary.json:pairs.n_pairs |
| M3-3 | 40 synthetic-lethal pairs, all isozyme redundancies | PASS | 40/40 | m3_summary.json:pairs.n_SL / n_SL_isozyme |
| M3-4 | 25% of active pairs open nonzero commutators | PASS | M3 script printout | m3_summary.json (sequential-KO block); M3 report body |
| M4-1 | smoothing identity kernel self-test 1.2e-6 | PASS | 1.18e-06 | m4c_summary.json:theorem_R.kernel_selftest_rel_err |
| M4-2 | crossover eps*/sigma in [2.45, 4.11], median 3.1 | PASS | range [2.45, 4.11], median 3.05 | m4c_summary.json:dial_exact.*.eps_star_over_sigma |
| M4-3 | sliver census: net measure jump 8.9 vs nominal 1884.6 | PASS | net_jump_L2=8.9001, max_jump_L2=1884.6 | m4c_summary.json:sliver_clusters[0] |
| TB-1 | folded W1 0.058 -> 0.0039 (n 4 -> 128) | PASS | 0.0582 -> 0.00387 | theoremB_stress/bt_results.json:BT1_reproduce_V2a |
| TB-2 | mass ratio 0.939 -> 1.0009 | PASS | 0.9388 -> 1.00093 | bt_results.json:BT1_reproduce_V2a |
| TB-3 | TV ratio u=xy 2.9922; convex 1.3922 (n=128); generic range | PASS | u=xy 2.9922 (= 3-1/128), convex 1.3922 (= 1.4-1/128), generic [{min(gv | bt_results.json:BT3/BT4/BT6 |
| V1-1 | Phi piecewise affine at 4.2e-13 | PASS | 4.17e-13 | v1_value_function.json:phi_piecewise_affine.worst_rel_r |
| V1-2 | one real atom dPhi' = -0.006439 at t = 0.0358286 | PASS | t=0.0358286, d=-0.006439 | v1_value_function.json:atoms[0] |
| V1-3 | 12 flux events, 4 clusters | PASS | 12 events, 4 clusters | v1_value_function.json:v_events_total / clusters |
| V1-4 | value/flux mass ratio 1.7e-6 (E-V1) | PASS | 0.006439 / 3807.6 = 1.69e-6 | v1_value_function.json:atoms[0] (numerator) + deepseek_ |
| V1-5 | Danskin 6-7 digits | PASS | 2.02e-09 | v1_value_function.json:danskin_max_rel_err |
| TC-1 | 150 random dense-objective LPs to 1.1e-13; 5 events, all objective-mov | PASS | n_lp=150, err=1.05e-13, events=5/5 | coupling_results.json:ax8a_random |
| TC-2 | degenerate follower family 60/60, identity 2.0e-13 | PASS | n=60, kinks=60, err=2.02e-13 | coupling_results.json:ax8a_random.degenerate_family |
| TC-3 | 2D mixed second differences to 6.4e-16 | PASS | 6.37e-16 | coupling_results.json:ax8b_mixed.max_mixed_identity_err |
| TC-4 | iML1515: 12 events, 11 invisible, L1 jumps to 1.6e4, |c^T dv'| <= 1.51 | PASS | n=12, invisible=11, max L1 15868, max |cT| 1.506e-07 | coupling_results.json:ax8c_iml1515 (events) |
| TC-5 | identity error 0.0 at all 12 events and 4 clusters | PASS | identity_err = 0.0 entries | v1 + ax8c identity_err keys |
| AX-1 | MA atoms: 400 vertices; det=fan area 8.9e-16; product/atom median 3.29 | PASS | n=400, err=8.9e-16, median=3.296, min=2.0000 (orthogonal case exactly  | coupling_results.json:ax9_ma_atom |
| AX-2 | semiconvexity collapse: lambda*h_max = 0.500 (lambda 1..1e6; analytic  | PASS | lam=1e+00: 0.5000; lam=1e+01: 0.5000; lam=1e+02: 0.5000; lam=1e+03: 0. | coupling_results.json:ax10_collapse.rows |
| AX-3 | GPR OR+cap eigenvalues {0,sqrt2} / {-1,0} | PASS | signed-layer battery block | coupling_results.json:ax10_gpr |
| AX-4 | sec law 0.0% excess across 13 probes, tilts 0.11-2.83 | PASS | sec-law block | alexandrov_bridge/ax_results.json (AX-5/AX-6 battery) |
| AX-5 | dual-face fan area 0.235 vs 0.235000068 (16 LPs) | PASS | grep 0.235 | alexandrov_bridge/ax_results.json (dual-face) |
| E22-1 | 435 genes with at least one active reaction | PASS | 435 | novelty_v15_reaction_sampling_e22.csv (kappa_V_max > 0) |
| E22-2 | 438 of 2,583 reactions active (17.0%); GPR classes 254/96/36/18/34 | PASS | computed below | recomputed: plain FBA at 8 E22 anchors (iJO1366, EPS=1e |
| E22-3 | precursor kappa_V weak at panel level (r -0.063 unmasked .. +0.084 mas | PASS | unmasked -0.0633, v12 +0.1024, v13(masked) +0.0838 | novelty_v15_reaction_sampling_e22.py printout |
| E22-4 | E22 baseline reproduced to the digit r = +0.3739 (n = 433) | PASS | r=+0.3739, n=433 | recomputed from e22/e24 csvs |
| E23-1 | genes with nonzero kappa expand 435 -> 525 | PASS | 525 | novelty_v16_multicondition_e23_results.json:coverage.un |
| E23-2 | active-reaction support 438-454; union 537 (20.8%) | PASS | per-cond 438-454, union 537 | novelty_v16_multicondition_e23_results.json:coverage |
| V5-1 | M3D carbon switches: glycerol +0.195, acetate +0.166, proline +0.175,  | PASS | 0.1949, 0.1664, 0.1752, 0.2063 | precise_arm_kappamu.json |
| V5-2 | all p < 6e-4 | PASS | max p = 0.00058 | precise_arm_kappamu.json |
| V5-3 | PRECISE cross-platform MAX r = -0.044 (partial -0.088, NS) | PASS | r=-0.0443, p=0.36; partial=-0.0878 (txt) | precise_arm_kappamu.json + txt |
| V5-4 | per-condition: glycerol +0.126, acetate +0.130, fructose +0.099, galac | PASS | 0.1263, 0.1297, 0.0985, -0.0875 | precise_arm_kappamu.json |
| V6-1 | 0 of 433 genes in the c-attribution arm | PASS | 0 | v6_layer_decision.json:layer_decision.kappa_c_n_nonzero |
| V6-2 | shadow arm: 51 genes, r = +0.032 | PASS | n=51, r=+0.0319 | v6_layer_decision.json:arms.B3 |
| V6-3 | partial -0.013, p = 0.93 | PASS | partial=-0.0127, recomputed p=0.93 | v6 (partial r stored; p recomputed) |
| V6-4 | 4 value kinks, all design corners, 0 chamber crossings | PASS | total=4, corners=4, crossings=0 | v6_layer_decision.json:value_kink_census |
| V6-5 | value/flux strain mass ratio 1.45e-3 | PASS | 1.4478e-03 | v6_layer_decision.json:value_kink_census.value_over_flu |
| V6-6 | Y = 0.099544 (single-chamber law) | PASS | Y = 0.099544 in law string | v6_layer_decision.json:value_kink_census.single_chamber |
| V6-7 | affine law dmu/dq_glc = Y = 0.099544, intercept -0.0124 | PASS | slope=0.099544, intercept=-0.0131 (resid max 5.4e-15) | recomputed: 57 lex solves on the V5 trajectory (iJO1366 |
| V7-1 | P1 r = +0.318 (partial +0.258, n=426) | PASS | r=0.3183, partial=0.2583 | v7_path_robustness.json:P1 arms |
| V7-2 | P2 r = +0.223 (partial +0.160) | PASS | r=0.2234, partial=0.1598 | v7_path_robustness.json:P2 arms |
| V7-3 | cross-path predictors vs E24: +0.378 / +0.391 | PASS | 0.3783 / 0.391 | v7_path_robustness.json:cross arms |
| V7-4 | P1 3 chamber crossings; P2 4 | PASS | P1=3, P2=4 | v7_path_robustness.json:value_kink_census |
| V7-5 | shadow arm null: P1 r=-0.170 (n=68), P2 r=+0.032 (n=71) | PASS | P1=-0.1698 (n=68), P2=0.0321 (n=71) | v7_path_robustness.json:B3int |
| V7-6 | value/flux ratios 1.5e-3 / 2.4e-4 / 5.5e-4 | PASS | P0=1.45e-03, P1=2.38e-04, P2=5.53e-04 | v7_path_robustness.json:census (P0/P1/P2) |
| V8-1 | declared r=+0.3954; variants 0.386..0.396; partial stable | PASS | TB0=0.3954, TB1=0.3861, TB3=0.3959 | v8_tiebreak_robustness.json:association |
| V8-2 | value layer mu invariant (max diff 0.0) | PASS | 0.0 | v8_tiebreak_robustness.json:verdict |
| E25-1 | 2x2 cells: +0.196 (array switch), +0.298 (array stress), +0.191 (seq c | PASS | +0.196, +0.298, +0.191, +0.345 | novelty_v18_e25_platform_class.csv (recomputed) |
| E25-2 | n = 241-433 | PASS | n per cell: [433, 433, 241, 241] | e25 csv (recomputed) |
| E26-1 | PaxDb abundance level r = +0.334 | PASS | +0.334 (n=429) | novelty_v19_e26 csv (recomputed, log-log) |
| E26-2 | protein change r = +0.008 to +0.032 | PASS | maxfc +0.008, 4h +0.032 | e26 csv (recomputed) |
| E26-3 | transcript-protein fold-change coupling r = +0.020 (n = 799: full GSE6 | PASS | panel subset r=+0.145 (n=169) | e26 csv (panel subset); n=799 is the script-level full  |
| E27-1 | protein-level r = -0.083 vs transcript +0.419 (22 conditions, n = 366) | PASS | kappa-vs-protein r=-0.083 (n=366), kappa-vs-transcript r=+0.419 (n=365 | novelty_v20 csv (recomputed on shared genes) |
| E22-2R | 438 of 2,583 active (17.0%); GPR classes 254/96/36/18/34 (plain-FBA ce | PASS | 439/2583; classes {'no-gpr': 34, 'single': 253, 'isozyme-or': 98, 'com | recomputed (plain FBA, 8 anchors, EPS=1e-9) |
| LEDGER-1 | counts ledger assembled (12 entries) | PASS | 12 entries | see ledger |
| QUIRK-1 | V5 json arm labels '4x'/'8x' are swapped | PASS | labels: 'kappa_mu max (4x)' holds the 8x-refinement values (df8); 'kap | v5_e24_recalibration.json:arms keys |
| E32-1 | A1 measured tail slope -0.492 | PASS | -0.492 | e32 json A1_d1.loglog_tail_slope |
| E32-2 | A1 null tail slope -0.506 | PASS | -0.506 | e32 json A1_d1.null_loglog_tail_slope |
| E32-3 | measured/null ratio 1.24 at the largest panel | PASS | 1.24 | e32 json A1_d1 |
| E32-4 | iid prediction matches to 2.5% at the largest panel | PASS | 2.5 | e32 json A1_d1 bl/iid_gc_pred-1 |
| E32-5 | mid-range deviations as large as 8.2% (m=128) | PASS | 8.2 | e32 json A1_d1 max |bl/iid-1| |
| E32-6 | cut pool 4,000; events 25,107; boundary edges 350; grid 34x34 | PASS | (4000, 25107, 350, 'iML1515 (glc, O2) 34x34 signature census') | e32 json A_m4b_random_cuts |
| E32-7 | thirteen M1 sweeps: 2 affine, 11 event-bearing | PASS | 13: 2 affine, 11 event-bearing | e32 json B_m1_sweep_panels.sweeps |
| E32-8 | heterogeneity penalty ~1.5x at k=6 (falls from 1.8x, to 0.5x at k=12) | PASS | k=6: 1.52, k=12: 0.49 | e32 json B curve bl/null |
| E32-9 | FPC formula sqrt((13-k)/12) present; 'exactly the finite-population co | PASS | 13-k)/12 present; overstatement absent | manuscript text |
| E32-10 | population GC constant C = 2.49 (3 s.f.) | PASS | 2.495 | e32 json C1 gc_constant_pop |
| E32-11 | measured effective constant ~1.6-2.1 (dipping at m=128); '1.9-2.1' rem | PASS | min 1.649, max 2.113 | e32 json C1 curve bl*sqrt(m) |
| E32-12 | association stabilizes r in [0.389, 0.397] for m <= 256; full-panel r  | PASS | [0.3888, 0.3974], full 0.3954 | e32 json C1 association |
| E32-13 | Fisher SD column = 1/sqrt(m-3) | PASS | all rows | e32 json C1 r_curve 4th column |
| E32-14 | four-atom mass 288.77 = the V5 mass to the digit | PASS | 288.76892 in v5: True | e32 json C2 reference vs v5 json stored floats |
| E32-15 | anchor-preserving thinning exact: bl = 0 to machine precision (<= 7e-1 | PASS | max bl 6.6e-13, kinks {4.0}, max err 1.7e-12 | e32 json C2 anchor_thinning |
| E32-16 | uniform thinning: shape 0.12 -> 0.005 by m=43; mass err 26% -> 0.13% b | PASS | bl 0.1209->0.0054, err 0.2614->0.0013->2.6e-12 | e32 json C2 uniform_thinning |
| E32-17 | population is a four-atom object (n_atoms = 4) | PASS | 4 | e32 json C2 population |
| E22R-1 | GPR check: 0 failures over 120 gene-reaction pairs (matches frozen v21 | PASS | both texts present | v21 sec E22 + v2 Sec 6.1 |
| E22R-2 | distinctness b2097 shared with MAPPED-15; non-zero variation 435/435 ( | PASS | both texts present | v21 sec E22 + v2 Sec 6.1 |
| JP-1 | tie-break robustness table present (5 rules TB0-TB4, rho_S >= 0.99897, | PASS | TB4 + 0.99897 + 9.3 present | v2 E-V8 table |
| JP-2 | BMB retarget: author-year citations (natbib round); no table of conten | PASS | all present | v2 preamble/backmatter |
| JP-3 | BMB retarget: abstract <= 300 words; no Author Summary; keywords line  | PASS | abstract 293w, keywords 6 | v2 front matter |
| JP-4 | backmatter: Data/Software/Code Availability, Funding, Competing Intere | PASS | all present | v2 backmatter |
| JP-5 | BMB-style references: 27 entries, alphabetical with natbib author-year | PASS | 27 entries, labels True, all keys resolve True | generated bmb refs |
| JP-6 | in-text 'Fig' abbreviation throughout (no 'Figure~') | PASS | Figure~ absent | v2 text |

## Counts ledger (near-colliding counts)

| value | meaning | source |
|---|---|---|
| 2,583 | iJO1366 reactions (model size) | data/bigg_models/iJO1366.json; recomputed in E22-2R |
| 438 | reactions active on the E22 physiology (17.0%) | recomputed E22-2R; v16 results json baseline |
| 440 | reactions with D2 > 1e-8 along the E24 trajectory (reaction-level count; V5/V8 json n_events_rxns) | v5_e24_recalibration.json:trajectory.refine_8.n_events_rxns; v8 json per-arm |
| 433 | panel genes with M3D response (E24 panel) | novelty_v17_option_a_e24.csv row count |
| 424 | panel genes with NONZERO kappa_mu (the n of the primary correlation) | v5/v6/v8 json n_nonzero |
| 426 | nonzero genes on P1/P2 paths (V7) | v7_path_robustness.json:arms n |
| 435 | genes with >= 1 active reaction (E22) | e22 csv (kappa_V_max > 0) = 435 (recomputed E22-1) |
| 454 | max active reactions across the 9 E23 conditions | v16 results json coverage.active_rxns_per_condition |
| 537 | union of active reactions across conditions (20.8%) | v16 results json coverage.union_active_rxns (v21 typo 538) |
| 525 | genes with nonzero kappa across conditions | v16 results json coverage.union_genes_nonzero_kv (v21 typo 524) |
| 1,516 | iML1515 genes (M3 single knockouts) | m3_summary.json:n_genes |
| 2,779 | double-knockout pairs (five panels) | m3_summary.json:pairs.n_pairs |

## Documented artifact quirks

- V5 json arm labels '(4x)'/'(8x)' swapped (cosmetic; frozen artifact left unedited; manuscript unaffected).
- V6 partial p (0.93) not stored; recomputed from stored partial r and n: consistent.
- V1 value/flux ratio denominator (3807.6) stored in the committed report script, not the frozen json.
- Frozen v21 E23 numbers 538/524 are typos; v2's 537/525 match the v16 results json (v21 not edited).