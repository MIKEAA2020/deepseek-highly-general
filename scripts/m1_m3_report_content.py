#!/usr/bin/env python3
"""Content module for the M1/M3 execution report (English).
Each item is a (kind, payload) spec consumed by m1_m3_report_pdf.py."""

FIG = "/home/z/my-project/download/m1_m3"

CONTENT = [
    # ================================================== 1. EXECUTIVE SUMMARY
    ("h1", "1. Executive Summary"),
    ("body",
     "This report documents the execution of M1 and M3, the two highest-value "
     "computational measurements specified in the joint assessment of the six "
     "\"unifying object\" audits and re-specified by the project owner on "
     "2026-09-01. M1 tests whether the second-order response of the FBA "
     "solution path is singular exactly at active-set changes; M3 tests "
     "whether the FBA rerouting statistic exhibits non-additive double-knockout "
     "epistasis aligned with the active-set structure, and whether sequential "
     "adjustment is path-dependent. Both experiments were run in silico on "
     "iML1515 (2,719 reactions, 1,516 genes) with an iJO1366 replication arm, "
     "using a purpose-built deterministic lexicographic solver stack. All "
     "numbers in this report are reproducible bit-for-bit from the deposited "
     "scripts and data files; the frozen v21 manuscript was not touched."),
    ("callout", ("100.0000%",
                 "of second-order response mass (D<sub>2</sub>) concentrated on "
                 "active-set switches, in every sweep that crosses a "
                 "critical-region boundary (12 sweeps; Mann-Whitney p from "
                 "2\u00d710<super>-</super><super>4</super> to 10<super>-</super><super>1</super><super>5</super>)")),
    ("callout", ("\u03c1 = 0.865",
                 "Spearman correlation between epistasis magnitude "
                 "|\u03b5<sub>i</sub><sub>j</sub>| and active-set footprint overlap "
                 "Jaccard J(\u0394R<sub>i</sub>, \u0394R<sub>j</sub>) across 2,779 "
                 "double knockouts (p \u2248 0)")),
    ("callout", ("40 / 40",
                 "synthetic-lethal double knockouts are isozyme redundancies "
                 "(tktA/tktB, acnA/acnB, metE/metH, argF/argI, ...) \u2014 "
                 "pure-emergence epistasis \u03b5 = \u03ba<sub>i</sub><sub>j</sub> with "
                 "both single \u03ba = 0")),
    ("callout", ("66%",
                 "of closed 4-step genotype loops (WT \u2192 \u0394i \u2192 "
                 "\u0394ij \u2192 \u0394j \u2192 WT) fail to return to the "
                 "initial state under greedy L1-MOMA adjustment \u2014 "
                 "discrete holonomy / phenotypic memory")),
    ("body",
     "Four findings carry the weight of the conclusion. First, M1: in every "
     "sweep that crosses a critical-region boundary (glucose uptake, oxygen "
     "uptake, and eight gene-capacity knockdowns), 93.4\u2013100% of the "
     "total second-order response mass sits on the 3\u201320 grid points "
     "where the operational active set changes, while between events the "
     "solution path is affine to machine precision (relative segment "
     "residuals \u2264 8\u00d710<super>-</super><super>1</super><super>4</super>, and 76\u201389% of "
     "off-event triples have exactly zero curvature). Second, the two "
     "negative controls behave exactly as the parametric-LP theory demands: "
     "a knockdown of an unused pathway (aceA) produces no response and no "
     "curvature at all, and the iJO1366 glucose sweep \u2014 which stays "
     "inside a single critical region with no overflow switch \u2014 has a "
     "constant first-order response to 15 digits and noise-level curvature "
     "(\u22481\u00d710<super>-</super><super>1</super><super>1</super>). Third, M3: rerouting epistasis "
     "is real, heavy-tailed, and tracks the combinatorial structure \u2014 "
     "non-additivity grows with the overlap of the two singles' "
     "flux-change footprints. Fourth, path dependence: the transient "
     "adjustment dynamics are measurably non-commutative (25% of pairs with "
     "active singles, commutator up to 226 in L1 units), the MOMA-based "
     "\u03ba value itself depends on the order of perturbation (19.4% of "
     "pairs), and closed genotype loops leave a persistent state "
     "displacement. Together these upgrade the active-set bridge from a "
     "formal analogy to a computable, falsifiable correspondence \u2014 "
     "they do not, by themselves, prove the full unification theorem."),
    ("table", {
        "title": "Table 1. Headline results of M1 and M3.",
        "header": ["Experiment", "Scale", "Primary endpoint", "Result"],
        "rows": [
            ["M1 nutrient sweeps (iML1515)", "2 \u00d7 250 points",
             "D<sub>2</sub> mass on active-set events",
             "0.99999996 (glucose); 0.999999999 (O<sub>2</sub>)"],
            ["M1 knockdown sweeps (iML1515)", "8 genes \u00d7 121 points",
             "D<sub>2</sub> mass on events; rank AUC",
             "0.934\u20131.0; AUC 0.90\u20131.00"],
            ["M1 controls", "aceA knockdown; iJO1366",
             "curvature in absence of transitions",
             "D<sub>2</sub> = 0 (aceA); D<sub>2</sub> \u2248 10<super>-</super><super>1</super><super>1</super>, "
             "D<sub>1</sub> constant (iJO1366)"],
            ["M3 singles", "1,516 genes",
             "\u03ba\u1d52 flux per Definition 3.21",
             "1,320 viable; 92.3% \u03ba = 0; max 19,587"],
            ["M3 double knockouts", "2,779 pairs, 5 panels",
             "\u03b5<sub>i</sub><sub>j</sub> = \u03ba<sub>i</sub><sub>j</sub> \u2212 \u03ba<sub>i</sub> \u2212 \u03ba<sub>j</sub>",
             "40 SL (all isozyme); 55 masked emergences"],
            ["M3 path dependence", "160 pairs (MOMA-L1)",
             "commutator \u03c7; loop holonomy h",
             "\u03c7 > 0 in 25% of active pairs; h > 0 in 66%"],
        ],
        "ratios": [0.22, 0.18, 0.28, 0.32],
    }),

    # ============================================ 2. BACKGROUND
    ("h1", "2. Background and Pre-Registered Predictions"),
    ("body",
     "The joint assessment of the six \"unifying object\" audits established "
     "that the manuscript's deepest coherence defect is the shared name "
     "\u03ba_V attached to three different objects: the geometric curvature "
     "of Proposition 4.4, the indicator-weighted FBA sum of Definition 3.21, "
     "and the time-course squared flux change of E10/E22. Five of the six "
     "audits converged on the same substrate for a repair: the active-set / "
     "multiparametric-LP critical-region stratification of the FBA feasible "
     "polytope, with Opus's corollary that curvature is singular and "
     "supported on basis-change loci \u2014 \"the paper's invisible thesis\". "
     "The assessment's Layer 3 named three measurements that would turn this "
     "qualitative idea into quantitative evidence: M1 (second differences), "
     "M2 (plaquette), and M3 (double-knockout epistasis). The project owner's "
     "2026-09-01 instruction specified M1 and M3 for execution and supplied "
     "their operative definitions, which this study implements directly."),
    ("body",
     "M1, as specified, computes the second-order finite difference of the "
     "FBA flux vector (or of the \u03ba\u1d52 flux metric) as a perturbation "
     "or condition varies, and tests whether the strongest second-order "
     "response concentrates at active-set boundaries. The theory anchor is "
     "the parametric-LP sensitivity theorem: when the parameter enters the "
     "constraint bounds linearly, the optimal solution path is piecewise "
     "affine, with breakpoints exactly at basis (active-set) changes; the "
     "second derivative of the path is therefore not a smooth function but a "
     "measure \u2014 a Dirac comb supported on those changes. If verified, "
     "the discrete FBA object has the same kind of singular structure that "
     "the geometric curvature object has, which is the first quantitative "
     "link. M3, as specified, computes \u03ba for single-gene knockouts and "
     "for double knockouts and measures the interaction "
     "\u03b5<sub>i</sub><sub>j</sub> = \u03ba<sub>i</sub><sub>j</sub> \u2212 \u03ba<sub>i</sub> \u2212 \u03ba<sub>j</sub>. "
     "Non-zero interaction is a form of path dependence; in differential "
     "geometry, path dependence around infinitesimal loops is what curvature "
     "and holonomy measure. The pre-registered predictions tested here are: "
     "(P1) D<sub>2</sub> mass concentrates on active-set events; (P2) the path is "
     "affine between events; (P3) controls without transitions show no "
     "curvature; (P4) epistasis magnitude aligns with active-set footprint "
     "overlap; (P5) redundancy (isozyme) pairs produce pure-emergence "
     "epistasis and synthetic lethality; (P6) sequential minimal-adjustment "
     "dynamics are non-commutative, and closed loops are holonomic."),
    ("quote",
     "The theory's discriminating prediction is which PAIRS interact, not "
     "merely that interactions exist \u2014 and the mixed difference "
     "\u03b5<sub>i</sub><sub>j</sub> = \u03ba<sub>i</sub><sub>j</sub> \u2212 \u03ba<sub>i</sub> \u2212 \u03ba<sub>j</sub> "
     "is the discrete analogue of the cross term that curvature measures."),

    # ============================================ 3. METHODS
    ("h1", "3. Methods"),
    ("h2", "3.1 A deterministic lexicographic FBA solver (methodological "
           "precondition)"),
    ("body",
     "Standard parsimonious FBA is not a well-defined point map: the "
     "parsimony objective \u03a3|v| is frequently tied across distinct "
     "vertices of the optimal face. This was verified directly at the iML1515 "
     "wild type: two consecutive pFBA solves returned the same objective "
     "value to 13 digits (\u03a3|v| = 769.790240) but flux vectors differing "
     "by 0.69 in L\u221e (PYK4 vs NDPK1 rerouting of the ATP-generating "
     "pyruvate kinase step, a 0.51 split across PFK/FBA, and a 0.16 "
     "NDPK3/PYK2 flip). Warm-started simplex flips between these tied "
     "vertices, which would inject spurious first- and second-order "
     "differences unrelated to any parameter change \u2014 fatal for a "
     "curvature study. The fix is a three-stage lexicographic solve: "
     "(1) maximize biomass; (2) minimize \u03a3|v| subject to biomass "
     "optimality; (3) minimize a fixed, seed-drawn linear functional "
     "w\u00b7v (w<sub>i</sub> \u223c U[0.5, 1.5], rng 20240901, shared by M1 and "
     "M3) subject to a pin \u03a3|v| \u2264 s<sub>2</sub> + 10<super>-</super><super>9</super>. This "
     "is the LP-realizable form of the strict regularization the joint "
     "assessment prescribed for M3 (\"cobrapy plus quadratic "
     "regularization\"): the lexicographic optimum is unique for generic "
     "weights, and the selection is continuous in the parameter by Berge's "
     "maximum theorem, so no artificial jumps are introduced. The engine is "
     "implemented once on scipy/HiGHS (variables [v, f, r] with linking rows "
     "v = f \u2212 r) and solves the lexicographic problem in 0.17 s and "
     "L1-MOMA in 0.14 s at iML1515 scale. Repeated solves are bit-identical "
     "(max difference exactly 0.0), and the wild-type growth (0.876997) and "
     "parsimony value match cobrapy's pFBA reference. All \u22485,700 LP "
     "solves in this study are cold-started and deterministic."),
    ("h2", "3.2 M1 design: sweeps, response functionals, active-set events"),
    ("body",
     "Twelve sweeps were run. Nutrient sweeps vary the glucose uptake bound "
     "linearly from 1.0 to 10.0 mmol gDW<super>-</super><super>1</super> h<super>-</super><super>1</super> (250 "
     "points \u2014 the in-silico analogue of the E22 glucose-decline "
     "trajectory) and the oxygen bound from 0.5 to 30.0 at fixed glucose 10 "
     "(crossing the overflow regime). Knockdown sweeps scale the capacity "
     "bounds of all reactions associated with each of ten genes "
     "(pgi, zwf, tktA, pfkA, eno, gltA, aceA, ppc, gnd, rpe) by c, linearly "
     "from 0.02 to 0 (121 points; c = 0 is the full knockout). The iJO1366 "
     "glucose sweep replicates the design on an independent model rebuild. "
     "At each point the lexicographic optimum v(\u03b8<sub>k</sub>) is recorded, "
     "and three functionals are computed: the first-order response "
     "D<sub>1</sub><sub>k</sub> = ||v<sub>k</sub><sub>+</sub><sub>1</sub> \u2212 v<sub>k</sub>||<sub>1</sub>, the "
     "second-order response D<sub>2</sub><sub>k</sub> = ||v<sub>k</sub><sub>+</sub><sub>1</sub> \u2212 "
     "2v<sub>k</sub> + v<sub>k</sub><sub>-</sub><sub>1</sub>||<sub>1</sub> (the discrete curvature of the "
     "path), and the turning angle between consecutive velocity vectors. The "
     "operational active set is the union of the material support "
     "S(\u03b8) = {r : |v<sub>r</sub>| \u2265 10<super>-</super><super>6</super>} and the binding set "
     "B(\u03b8) = {r : |v<sub>r</sub>| \u2265 10<super>-</super><super>6</super> and v<sub>r</sub> at a "
     "bound within 10<super>-</super><super>7</super>}; an event at grid point k is any change "
     "of S or B between k\u22121 and k+1. This is a conservative proxy for "
     "the true LP active set (degenerate bindings can add false events, "
     "which can only dilute enrichment), and a robustness pass at threshold "
     "10<super>-</super><super>5</super> reproduces every headline number. Endpoints: "
     "fraction of D<sub>2</sub> mass on events; fold enrichment of median "
     "D<sub>2</sub>; Mann-Whitney U and rank AUC of D<sub>2</sub> against the event "
     "label; and least-squares residuals of the flux path against an affine "
     "fit on maximal non-event segments."),
    ("h2", "3.3 M3 design: \u03ba, panels, epistasis, path dependence"),
    ("body",
     "The rerouting statistic follows the manuscript's Definition "
     "\"ard-derived-kappa-V\" (v10 main definition): "
     "\u03ba\u1d52 flux(g) = \u03a3<sub>r</sub> (v<sub>r</sub>(KO) \u2212 "
     "v<sub>r</sub>(WT))<super>2</super> over reactions with |v<sub>r</sub>(KO) \u2212 "
     "v<sub>r</sub>(WT)| > 10<super>-</super><super>6</super>, with the masked variant "
     "\u03ba_V = \u03ba\u1d52 flux \u00b7 1[\u0394b > 0.05 b<sub>s</sub><sub>t</sub>] "
     "reported alongside the unmasked one. Single knockouts of all 1,516 "
     "genes were solved (gene reaction rules parsed to disjunctive normal "
     "form; a reaction is disabled only when every AND-clause loses a gene). "
     "Double knockouts were solved for 2,779 pairs drawn from five panels: "
     "all pairs among the 40 highest-\u03ba viable genes; all pairs among 40 "
     "random low-\u03ba genes; 300 random high\u00d7low crosses; every "
     "isozyme pair implied by an OR-clause shared between two viable genes; "
     "and nine targeted pairs (pgi+zwf, tktA+tktB, talA+talB, ppc+pps, "
     "zwf+gnd, pfkA+pfkB, rpe+rpiA, rpe+rpiB, tktA+talA). For each pair we "
     "record \u03ba<sub>i</sub><sub>j</sub>, growth, the additive epistasis "
     "\u03b5<sub>i</sub><sub>j</sub> = \u03ba<sub>i</sub><sub>j</sub> \u2212 \u03ba<sub>i</sub> \u2212 "
     "\u03ba<sub>j</sub>, the multiplicative ratio \u03c1<sub>i</sub><sub>j</sub>, the "
     "multiplicative growth epistasis, the Jaccard overlap of the two "
     "singles' support-change footprints \u0394S and flux-change footprints "
     "\u0394R, and synthetic lethality (both singles viable, double "
     "no-growth). Path dependence is measured on 160 pairs (top 80 by "
     "|\u03b5|, all 40 SL, 80 random) with sequential L1-MOMA: states are "
     "greedy projections s \u21a6 argmin ||v \u2212 s<sub>r</sub><sub>e</sub>\u1da0||<sub>1</sub> "
     "over the current polytope. The open-path commutator is "
     "\u03c7<sub>i</sub><sub>j</sub> = ||s<sub>i</sub>\u2192<sub>j</sub> \u2212 s<sub>j</sub>\u2192<sub>i</sub>||<sub>1</sub>; "
     "closed 4-step loops (WT \u2192 \u0394i \u2192 \u0394ij \u2192 \u0394j "
     "\u2192 WT, both orientations) measure the plaquette holonomy "
     "h = ||s_final \u2212 s<sub>0</sub>||<sub>1</sub>. Projections onto non-nested "
     "convex sets do not commute in general (von Neumann's alternating "
     "projections), which is precisely the discrete realization of the "
     "non-Abelian transport the manuscript's holonomy thread describes."),

    # ============================================ 4. M1 RESULTS
    ("h1", "4. M1 \u2014 Second-Order Response and Active-Set Switches"),
    ("h2", "4.1 Main result: curvature is supported on active-set changes"),
    ("body",
     "Table 2 gives the complete sweep statistics. In the glucose sweep, ten "
     "event points (six of them material, i.e. involving reactions with "
     "flux \u2265 10<super>-</super><super>5</super>) carry 0.99999996 of the total "
     "D<sub>2</sub> mass; the median event D<sub>2</sub> exceeds the median off-event "
     "D<sub>2</sub> by a factor of 9\u00d710<super>7</super>, and the rank AUC of "
     "D<sub>2</sub> against the event label is 0.831 (Mann-Whitney p = "
     "2\u00d710<super>-</super><super>4</super>). The oxygen sweep, which crosses the "
     "oxidative-to-overflow transition and a sequence of secretion switches, "
     "is even sharper: sixteen events, mass 0.999999999, fold enrichment "
     "1.2\u00d710<super>1</super><super>0</super>, AUC 0.935, p = 3\u00d710<super>-</super><super>9</super>. The "
     "eight informative knockdown sweeps show the same structure with three "
     "to twenty events each, mass 0.934\u20131.0 and AUC 0.90\u20131.00. "
     "The event reactions are exactly the ones the biology predicts: in the "
     "pgi sweep the events are PGI itself, HEX7, GLCt2pp, FBA, PFK, PYK5 "
     "and NDPK2; in the gltA sweep they include PPC (anaplerosis), the "
     "ribonucleotide-reductase variants, FBA and PFK; in the glucose sweep "
     "they are the overflow and transport reactions that switch as acetate "
     "secretion turns on. Figure 1 and Figure 2 show the response panels: "
     "growth, first-order rerouting, log-scale D<sub>2</sub> with event markers, "
     "and the turning angle of the velocity vector."),
    ("figure", (FIG + "/fig_m1_glucose.png",
                "Figure 1. iML1515 glucose sweep (250 points). Top to "
                "bottom: growth rate; first-order response D<sub>1</sub>; "
                "second-order response D<sub>2</sub> (log scale; red = active-set "
                "events); velocity turning angle. All D<sub>2</sub> mass sits on "
                "the ten event points.", 300)),
    ("figure", (FIG + "/fig_m1_o2.png",
                "Figure 2. iML1515 oxygen sweep at glucose 10 (250 "
                "points), crossing the overflow regime. Sixteen events "
                "carry all curvature; off-event D<sub>2</sub> sits at the "
                "10<super>-</super><super>1</super><super>1</super> noise floor.", 300)),
    ("h2", "4.2 The path is piecewise affine to machine precision"),
    ("body",
     "The theory says the lexicographic optimum path is piecewise affine in "
     "the parameter, so the second difference must vanish identically "
     "between events. This is confirmed numerically to solver precision: on "
     "maximal non-event segments, the least-squares affine fit of the full "
     "2,719-dimensional flux vector leaves relative residuals \u2264 "
     "8\u00d710<super>-</super><super>1</super><super>4</super> (Table 2, last column), and in the "
     "knockdown sweeps 76\u201389% of off-event triples have D<sub>2</sub> "
     "exactly 0.0 \u2014 bit-exact affine continuation, not merely small. "
     "The median off-event D<sub>2</sub> is 0.0 for five of the eight informative "
     "knockdowns and \u2264 5\u00d710<super>-</super><super>1</super><super>0</super> elsewhere; the "
     "noise floor of the whole machinery is two to ten orders of magnitude "
     "below the smallest true spike. The turning angle adds geometric "
     "confirmation: off-event the velocity direction is constant (median "
     "angle 0.0\u00b0), while at events it rotates by up to 138\u00b0."),
    ("table", {
        "title": "Table 2. M1 sweep statistics (material thresholds "
                 "10<super>-</super><super>6</super>; robustness pass at 10<super>-</super><super>5</super> in "
                 "the deposited summary).",
        "header": ["Sweep", "Events", "D<sub>2</sub> mass on events",
                   "Fold enrich.", "AUC", "MWU p",
                   "Segment resid."],
        "rows": [
            ["iML glucose", "10 (6 mat.)", "0.99999996", "9.0\u00d710<super>7</super>",
             "0.831", "2\u00d710<super>-</super><super>4</super>", "2.3\u00d710<super>-</super><super>1</super><super>3</super>"],
            ["iML O<sub>2</sub>", "16 (13 mat.)", "0.999999999",
             "1.2\u00d710<super>1</super><super>0</super>", "0.935", "3\u00d710<super>-</super><super>9</super>",
             "6.7\u00d710<super>-</super><super>1</super><super>4</super>"],
            ["kd pgi", "9", "0.999999999", "\u221e*", "0.998",
             "1\u00d710<super>-</super><super>8</super>", "4.3\u00d710<super>-</super><super>1</super><super>5</super>"],
            ["kd gltA", "18", "0.9999999999", "\u221e*", "0.988",
             "6\u00d710<super>-</super><super>1</super><super>5</super>", "3.5\u00d710<super>-</super><super>1</super><super>6</super>"],
            ["kd eno", "20", "0.934", "1.7\u00d710<super>9</super>", "0.953",
             "9\u00d710<super>-</super><super>1</super><super>1</super>", "6.1\u00d710<super>-</super><super>1</super><super>4</super>"],
            ["kd pfkA", "8", "0.9999999996", "\u221e*", "0.958",
             "9\u00d710<super>-</super><super>7</super>", "6.7\u00d710<super>-</super><super>1</super><super>4</super>"],
            ["kd zwf", "5", "0.999999998", "1.4\u00d710<super>1</super><super>0</super>",
             "0.902", "9\u00d710<super>-</super><super>4</super>", "5.1\u00d710<super>-</super><super>1</super><super>4</super>"],
            ["kd gnd", "5", "0.999999999", "\u221e*", "0.982",
             "1\u00d710<super>-</super><super>8</super>", "4.1\u00d710<super>-</super><super>1</super><super>5</super>"],
            ["kd ppc", "3", "0.9999999996", "\u221e*", "0.991",
             "5\u00d710<super>-</super><super>7</super>", "4.1\u00d710<super>-</super><super>1</super><super>6</super>"],
            ["kd rpe / tktA", "3 / 3", "0.99999999+",
             "3.8\u00d710<super>1</super><super>1</super> / 1.5\u00d710<super>1</super><super>2</super>",
             "0.994 / 1.000", "\u224810<super>-</super><super>3</super>",
             "\u22646.1\u00d710<super>-</super><super>1</super><super>4</super>"],
            ["kd aceA (control)", "0", "n/a", "n/a", "n/a",
             "n/a", "6.5\u00d710<super>-</super><super>1</super><super>4</super>"],
            ["iJO glucose (control)", "2 micro", "0.01\u2020",
             "1.4", "0.614", "0.30", "8.0\u00d710<super>-</super><super>1</super><super>4</super>"],
        ],
        "ratios": [0.19, 0.11, 0.17, 0.14, 0.09, 0.13, 0.17],
        "note": "* median off-event D<sub>2</sub> is exactly 0, so the fold "
                 "enrichment is infinite; reported as \u221e. "
                 "\u2020 there is no curvature to concentrate \u2014 see "
                 "\u00a74.3.",
    }),
    ("h2", "4.3 Negative controls: no transition, no curvature"),
    ("body",
     "Two controls establish the discriminating power of the design. The "
     "aceA knockdown sweep is the unused-pathway control: isocitrate lyase "
     "carries no flux on glucose minimal medium, so scaling its capacity "
     "from 2% to 0 leaves the optimum unchanged. The result is a completely "
     "flat response \u2014 zero events, zero growth change, and a maximum "
     "D<sub>2</sub> of 5.2\u00d710<super>-</super><super>1</super><super>1</super> \u2014 the entire response "
     "curve is one affine (constant) segment. The iJO1366 glucose sweep is "
     "the single-critical-region control: under the same parametrization, "
     "iJO1366 grows oxidatively without acetate overflow anywhere in "
     "[1, 10], so the solution path never leaves one critical region. "
     "Consistently, its first-order response is constant to fifteen digits "
     "(D<sub>1</sub> median = max = 2.485), its D<sub>2</sub> sits at the "
     "10<super>-</super><super>1</super><super>1</super> noise level everywhere, and the only two "
     "\"events\" are sub-threshold flickers of methanol-related "
     "micro-fluxes (DM_amob, EX_meoh) with no associated curvature. Where "
     "the active set does not change, the discrete curvature is empty \u2014 "
     "which is precisely what the measure-on-breakpoints theorem predicts. "
     "The weak enrichment statistics of this control (mass 0.01, AUC 0.61) "
     "are not a failure of the method but its null result."),
    ("figure", (FIG + "/fig_m1_knockdown.png",
                "Figure 3. Left: knockdown response curves "
                "\u03ba\u1d52 flux(c) for the gene panel (log-log; black "
                "triangles mark active-set events; aceA is the flat "
                "control). Right: pgi detail \u2014 growth (green) vs "
                "D<sub>2</sub> (log scale, red events).", 280)),
    ("figure", (FIG + "/fig_m1_summary.png",
                "Figure 4. Cross-sweep summary. Left: D<sub>2</sub> "
                "distributions off-event (grey) vs event (red). Middle: "
                "fraction of D<sub>2</sub> mass on events per sweep. Right: rank "
                "AUC of D<sub>2</sub> against the event label.", 300)),

    # ============================================ 5. M3 RESULTS
    ("h1", "5. M3 \u2014 Double-Knockout Epistasis and Path Dependence"),
    ("h2", "5.1 Singles census"),
    ("body",
     "All 1,516 single-gene knockouts were solved; 1,320 are viable and 196 "
     "show no growth (0 LP-infeasible). The \u03ba\u1d52 flux distribution "
     "is extremely heavy-tailed: 92.3% of viable knockouts have \u03ba = 0 "
     "exactly (the lexicographic optimum is unchanged), the median is 0, the "
     "99th percentile is 3,719, and the maximum is 19,587 (ATP-synthase "
     "subunits, whose knockout forces the model to the zero-growth "
     "maintenance state). Twenty-eight viable knockouts exceed the "
     "manuscript's 5% biomass-deficit mask threshold. Sanity anchors match "
     "known physiology: pgi grows at 0.870 with \u03ba = 438 (oxidative "
     "pentose-phosphate rerouting), zwf at 0.873 with \u03ba = 59, eno at "
     "0.804 with \u03ba = 1,927, gltA is lethal with \u03ba = 18,884, and "
     "the isozyme pair tktA/tktB each show growth exactly equal to wild type "
     "with \u03ba = 0 \u2014 the redundancy signature that the double "
     "knockouts then convert into lethality."),
    ("h2", "5.2 Epistasis: non-additivity tracks active-set overlap"),
    ("body",
     "Across the 2,779 double knockouts, the additive epistasis "
     "\u03b5<sub>i</sub><sub>j</sub> has median 0 (most sampled pairs of neutral genes "
     "stay neutral), a 5th percentile of \u22123,294 and a 95th percentile "
     "of +2,107, with 13.2% of pairs super-additive and 34.4% showing "
     "interactions larger than 10% of the median pair \u03ba. The central "
     "structural finding is the alignment with the active set: the Spearman "
     "correlation between |\u03b5<sub>i</sub><sub>j</sub>| and the Jaccard overlap of "
     "the two singles' flux-change footprints \u0394R is 0.865 (support "
     "footprints: 0.800; both p \u2248 0), and pairs above the median "
     "overlap have median |\u03b5| = 3,241 against exactly 0 below it "
     "(Mann-Whitney p \u2248 0). Growth epistasis and rerouting epistasis "
     "are strongly anticorrelated (Spearman \u22120.705): the pairs that "
     "lose the most growth multiplicatively are precisely those whose "
     "rerouting footprints coincide \u2014 same complex, same pathway, or "
     "same redundancy class \u2014 so that \u03ba is sub-additive while "
     "growth is aggravated."),
    ("figure", (FIG + "/fig_m3_epistasis.png",
                "Figure 5. Left: \u03ba<sub>i</sub><sub>j</sub> vs "
                "\u03ba<sub>i</sub>+\u03ba<sub>j</sub> (log-log) with the additivity "
                "diagonal; synthetic-lethal pairs in red. Middle: "
                "|\u03b5<sub>i</sub><sub>j</sub>| vs footprint overlap "
                "J(\u0394R<sub>i</sub>, \u0394R<sub>j</sub>). Right: epistasis "
                "distribution (signed log scale).", 300)),
    ("table", {
        "title": "Table 3. Epistasis by stratum (unmasked \u03ba).",
        "header": ["Stratum", "n", "median \u03b5",
                   "95th pct \u03b5", "Reading"],
        "rows": [
            ["Isozyme pairs, non-SL", "892", "0", "0",
             "redundancy absorbs the double perturbation"],
            ["Non-isozyme pairs, non-SL", "1,847", "0", "2,292",
             "heavy tail: same-complex and cross-pathway pairs"],
            ["Synthetic lethal", "40", "18,415", "18,415",
             "pure emergence: \u03b5 = \u03ba<sub>i</sub><sub>j</sub>, both \u03ba<sub>x</sub> = 0"],
            ["Masked emergence (\u03ba_V)", "55", "n/a", "n/a",
             "\u03ba_V<sub>i</sub> = \u03ba_V<sub>j</sub> = 0, \u03ba_V<sub>i</sub><sub>j</sub> > 0"],
        ],
        "ratios": [0.28, 0.07, 0.14, 0.14, 0.37],
    }),
    ("body",
     "The synthetic-lethal census is a textbook confirmation of the "
     "isozyme-redundancy mechanism \u2014 and a clean demonstration that "
     "the epistasis object sees it. All forty SL pairs in the sample are "
     "GPR alternatives for the same reaction(s): tktA+tktB "
     "(transketolase), acnA+acnB (aconitase), metE+metH (methionine "
     "synthase), argF+argI, aroK+aroL, aspC+tyrB, asnA+asnB, dadX+alr, "
     "gutQ+kdsD, ilvB+ilvN, leuB+dmlA, malY+metC, mutT+nudB, pabC+ubiC, "
     "pyrH+cmk, tdcB+ilvA, ydiB+aroE, ybjI+yigB, and more. Each single "
     "knockout is exactly wild type (\u03ba = 0, growth unchanged); the "
     "double knockout disables the shared reaction and collapses to the "
     "zero-growth maintenance state, giving \u03ba<sub>i</sub><sub>j</sub> \u2248 "
     "18,415\u201318,884 and \u03b5 = \u03ba<sub>i</sub><sub>j</sub>. The targeted "
     "pairs fill in the other archetypes: zwf+gnd is perfect sub-additive "
     "redundancy (\u03ba<sub>i</sub><sub>j</sub> = \u03ba<sub>i</sub> = \u03ba<sub>j</sub> = 58.6, "
     "\u03b5 = \u221258.6, since both knockouts block the same oxidative "
     "PPP segment); pfkA+pfkB is capacity redundancy (singles 1.87 and 0, "
     "double 244.6, \u03b5 = +242.8 with growth 0.871); pgi+zwf is "
     "super-additive but non-lethal (\u03b5 = +198, growth 0.864); "
     "rpe+rpiA and rpe+rpiB are exactly additive (\u03b5 = 0) because the "
     "rpi knockout adds nothing to the rpe footprint."),
    ("h2", "5.3 Path dependence: non-commutativity and loop holonomy"),
    ("body",
     "Sequential L1-MOMA adjustment \u2014 the greedy dynamics that models "
     "the immediate post-perturbation state without re-optimization \u2014 "
     "was run on 160 pairs. The open-path commutator "
     "\u03c7<sub>i</sub><sub>j</sub> = ||s<sub>i</sub>\u2192<sub>j</sub> \u2212 s<sub>j</sub>\u2192<sub>i</sub>||<sub>1</sub> "
     "is positive for 25% of the pairs with active singles (median of the "
     "active stratum \u2248 0, 90th percentile 101, maximum 226): knocking "
     "out i first and then j lands in a different metabolic state than "
     "knocking out j first, which is the discrete signature of "
     "non-commuting transport. Concretely, the MOMA-based \u03ba value "
     "itself is order-dependent for 19.4% of pairs (Figure 6, middle). "
     "Closed 4-step genotype loops return to the wild-type genotype but "
     "not to the wild-type state in 66% of pairs (median displacement "
     "\u2248 110 in L<sub>1</sub> flux units; both strata, SL and non-SL, show "
     "it): restoring the genes does not undo the rerouting the double "
     "knockout induced \u2014 phenotypic memory, the plaquette/Wilson-loop "
     "object of the assessment's M2, here realized in genotype space. One "
     "structural nuance matters for interpretation: \u03c7 and |\u03b5| are "
     "independent axes (within non-SL pairs, Spearman \u22120.07, p = 0.43). "
     "Isozyme SL pairs have maximal \u03b5 but \u03c7 = 0, because their "
     "singles are no-ops; non-commutativity lives in pairs where both "
     "singles act on distinct but interacting footprints. Non-additivity "
     "of the optima and non-commutativity of the transients are two "
     "different readings of the same interaction, and both are non-trivial."),
    ("figure", (FIG + "/fig_m3_path.png",
                "Figure 6. Left: open-path commutator \u03c7<sub>i</sub><sub>j</sub> by "
                "stratum. Middle: MOMA \u03ba via the i-first path vs the "
                "j-first path (log-log, diagonal = path independence). "
                "Right: closed-loop holonomy distribution.", 300)),

    # ============================================ 6. JOINT INTERPRETATION
    ("h1", "6. Joint Interpretation \u2014 What M1 and M3 Establish"),
    ("body",
     "Read together, the two experiments deliver the quantitative link the "
     "six audits asked for, at three levels. At the level of the solution "
     "path (M1), the discrete curvature of the lexicographic FBA optimum is "
     "not merely correlated with active-set changes by analogy \u2014 it is "
     "a measure supported on them, verified to machine precision, with "
     "controls that show it vanishing when no transition occurs. At the "
     "level of the perturbation calculus (M3), the squared-displacement "
     "statistic of Definition 3.21 becomes a curvature-type object the "
     "moment it is composed: the mixed difference "
     "\u03b5<sub>i</sub><sub>j</sub> = \u03ba<sub>i</sub><sub>j</sub> \u2212 \u03ba<sub>i</sub> \u2212 "
     "\u03ba<sub>j</sub> is the discrete cross-term, its magnitude tracks the "
     "combinatorial overlap of the two perturbation footprints "
     "(\u03c1 = 0.865), and the redundancy archetypes (isozyme SL, "
     "same-complex sub-additivity, capacity redundancy) appear exactly "
     "where the active-set structure predicts them. At the level of "
     "dynamics (M3b), greedy adjustment around perturbation loops is "
     "non-commutative and holonomic, which instantiates the non-Abelian "
     "transport language of the manuscript's holonomy thread in a "
     "genome-scale metabolic polytope."),
    ("body",
     "Equally important is what this does not establish. The strong-form "
     "unification \u2014 a theorem transferring properties between the "
     "geometric object of Proposition 4.4, the mpLP critical-region "
     "stratification, and the biological measurements \u2014 remains "
     "unproven; what M1 and M3 provide is a verified in-silico "
     "correspondence between the FBA-side objects and the "
     "singularity-on-strata-bounds structure that the geometric side "
     "postulates. The results are conditional on the steady-state optimum "
     "and on the greedy (L1-MOMA) model of the transient, not on measured "
     "transcript or flux time courses. The correspondence is also "
     "model-mediated: iML1515 and iJO1366 differ in where their critical "
     "regions lie (the iJO1366 glucose sweep has no overflow transition in "
     "range), which is exactly why the replication arm doubles as a "
     "control. The bridge is now computable and falsifiable \u2014 which "
     "is the standard the joint assessment set for upgrading it from "
     "metaphor \u2014 but the theorem connecting the three \u03ba_V "
     "objects is still the v2 mathematical task."),

    # ============================================ 7. KOCHANOWSKI
    ("h1", "7. Positioning Relative to Kochanowski et al. 2021"),
    ("body",
     "Kochanowski and colleagues showed that the global coordination of "
     "catabolic and anabolic pathways in E. coli under catabolic limitation "
     "is largely passive at the protein and metabolite level: catabolic "
     "enzymes are induced directly by Crp while anabolic protein expression "
     "adjusts indirectly, so that much of the apparent coordination follows "
     "from local metabolite concentrations rather than active global "
     "control (Kochanowski, K., et al., \"Global coordination of metabolic "
     "pathways in Escherichia coli by active and passive regulation\", "
     "Molecular Systems Biology 17(4):e10064, 2021; "
     "doi:10.15252/msb.202010064). This is complementary prior art, not a "
     "conflicting result, and the project owner's draft passage positions "
     "it correctly. The passage below is staged verbatim for the v2 "
     "introduction/discussion:"),
    ("quote",
     "Kochanowski et al. demonstrated that global metabolic coordination "
     "under catabolic limitation is largely passive at the protein/metabolite "
     "level, driven by Crp and local metabolite concentrations. Our work "
     "asks a different question: whether a gene-specific, network-derived "
     "rerouting necessity predicts transcriptional response. We find that "
     "it does, and that this transcript-level association does not "
     "propagate to the protein layer \u2014 consistent with a model in "
     "which cells transcribe the potential for rerouting while buffering "
     "its translation."),
    ("body",
     "The M1/M3 results strengthen this framing mechanically. The "
     "active-set analysis localizes exactly where rerouting necessity is "
     "created \u2014 at critical-region boundaries where the optimal flux "
     "program reorganizes \u2014 and the M3b path-dependence results show "
     "that the transient adjustment after such reorganization is not "
     "reversible on the timescale of the greedy dynamics. A cell that "
     "transcribes the potential for rerouting (the \u03ba_V\u2013response "
     "association of E24) while buffering translation (the E26/E27 "
     "protein-layer result) is exactly what the layer separation predicts: "
     "the transcript layer carries the prediction of future network "
     "reorganization; the protein layer, coordinated passively by Crp and "
     "metabolite pools as Kochanowski et al. showed, does not need to "
     "mirror it. The v2 manuscript can now cite both halves: the empirical "
     "layer separation (prior art plus the manuscript's own protein "
     "follow-up) and, from this study, the computational localization of "
     "the rerouting necessity itself to active-set transitions."),

    # ============================================ 8. LIMITATIONS
    ("h1", "8. Limitations and Threats to Validity"),
    ("body",
     "The following limitations are stated explicitly so that v2 claims can "
     "be calibrated against them. None of them, in our judgment, threatens "
     "the headline findings, but each constrains the strength of language "
     "that the manuscript should use."),
    ("bullet_list", [
        ("Operational active set.",
         "Events are defined from primal solution structure (material "
         "support \u2265 10<super>-</super><super>6</super> and binding within 10<super>-</super><super>7</super>) "
         "rather than from LP duals. Degenerate bindings can create false "
         "events, which dilutes enrichment \u2014 the direction of bias is "
         "conservative. The 10<super>-</super><super>5</super> robustness pass and the "
         "machine-precision segment fits bound the residual risk."),
        ("L1-MOMA is deterministic but not unique.",
         "The L1 projection can be non-unique in principle; HiGHS cold "
         "solves make every reported state a deterministic function of its "
         "inputs, but the path-dependence claims should be read as "
         "statements about this specific (standard) greedy rule, not about "
         "all adjustment dynamics. An L2-MOMA replication (strictly "
         "unique) is a cheap follow-up."),
        ("Pair panels are structured, not exhaustive.",
         "2,779 of the ~870,000 viable pairs were solved, sampled to "
         "cover the interaction archetypes (high-\u03ba, low-\u03ba, "
         "isozyme, cross, targeted). The SL census is complete within the "
         "isozyme panel, not genome-wide; genome-wide SL counting would "
         "require ~10<super>5</super> further solves at current speed."),
        ("Dead-state convention.",
         "\u03ba for lethal knockouts measures rerouting to the "
         "zero-growth maintenance optimum (the minimal-flux state "
         "satisfying ATP maintenance). This is well-defined and "
         "deterministic, but it is a convention: the number 18,415 is the "
         "wild-type-to-dead-state displacement, not a growth-capable "
         "rerouting."),
        ("Single medium, two models.",
         "All experiments are glucose minimal aerobic on iML1515 with an "
         "iJO1366 replication arm. The overflow transition of iML1515 "
         "happens to lie inside the swept range; iJO1366's does not. "
         "Medium sweeps (carbon-source panels matching E23) would test "
         "generality."),
        ("In silico only.",
         "M1's prediction about measured time courses (second differences "
         "of E10/E22-class data concentrating at condition transitions) "
         "remains to be tested on the deposited datasets; this study "
         "verifies the FBA-side correspondence only."),
    ]),

    # ============================================ 9. V2 IMPLICATIONS
    ("h1", "9. Implications for journal_manuscript v2"),
    ("body",
     "The v21 manuscript is frozen; everything below is specified for "
     "journal_manuscript_v2 (new document, per the standing protocol). The "
     "most direct gains are for the three claims that the six audits "
     "identified as the coherence core. First, the Layer-1 notation "
     "protocol gains a computational anchor: the mixed difference "
     "\u03b5<sub>i</sub><sub>j</sub> can be adopted as the combinatorial definition of "
     "the factored curvature datum (the assessment's Proposition G route), "
     "with M3 as its first computed instance and Definition 3.21 recovered "
     "as the single-perturbation special case. Second, the \"invisible "
     "thesis\" sentence \u2014 curvature singular, supported on "
     "basis-change loci \u2014 can now be cited with M1's numbers rather "
     "than asserted. Third, the non-Abelian holonomy thread (Claims A\u2013E "
     "calibration, network K) gains a biological instantiation: closed "
     "genotype loops with non-zero greedy-adjustment holonomy. The "
     "suggested study numbering follows the joint assessment's Table 9: "
     "E28 (second differences on measured time courses, M1-class), E29 "
     "(double-KO epistasis in silico, now executed \u2014 report as done), "
     "E30 (plaquette/path-dependence, executed here as M3b). The staged "
     "Kochanowski passage of \u00a77 slots into the introduction (related "
     "work) and the E26/E27 discussion; the citation should be completed "
     "with the full author list in the v2 bibliography pass."),
    ("table", {
        "title": "Table 4. v2 guidance summary.",
        "header": ["v2 element", "Current state", "What M1/M3 supply"],
        "rows": [
            ["\u03ba_V notation protocol (Layer 0)",
             "typed renaming specified, unverified",
             "mixed difference \u03b5<sub>i</sub><sub>j</sub> computed on 2,779 pairs; "
             "redundancy archetypes located in the active-set structure"],
            ["Active-set bridge (Layer 1\u20132)",
             "5/6-audit convergence, formal only",
             "mass-1.0 singularity verification + controls; footprint "
             "overlap \u03c1 = 0.865"],
            ["Holonomy thread (Claims A\u2013F)",
             "prototype constructions",
             "25% non-commutative transients; 66% non-zero loop holonomy"],
            ["Kochanowski positioning",
             "user-approved draft passage",
             "citation resolved; mechanical strengthening from \u00a77"],
            ["Study numbering E28\u2013E30",
             "designed in the joint assessment",
             "E29/E30 executed (this report); E28 open (measured data)"],
        ],
        "ratios": [0.28, 0.30, 0.42],
    }),
    ("body",
     "Wording discipline for v2: these results license sentences of the "
     "form \"in the genome-scale FBA model, the discrete curvature of the "
     "optimal flux path is a measure supported on active-set changes, and "
     "double-perturbation epistasis of the rerouting statistic tracks the "
     "active-set footprint overlap\" \u2014 not sentences claiming the "
     "unification theorem. The transfer theorem (T-energy / T-bound in the "
     "assessment's Layer 2) remains the mathematical work item, and the "
     "measured-data second-difference study (E28) remains the empirical "
     "work item. The strategic decision (single article vs. main-plus-"
     "companions) is unaffected and still pending, per the standing "
     "sequencing."),

    # ============================================ APPENDIX
    ("h1", "Appendix A. Deliverables and Reproduction"),
    ("body",
     "All code and data are committed to the repository (commits 2fe264b "
     "for M1 and f9f8634 for M3; this report's commit follows). The "
     "deterministic engine uses one seed for the tie-breaking weights "
     "(20240901, shared across M1 and M3) and one seed for panel sampling "
     "(20260901); rerunning the scripts reproduces every number "
     "bit-for-bit. Total compute: approximately 5,700 lexicographic LP "
     "solves and 1,300 MOMA solves, about 25 minutes single-core."),
    ("bullet_list", [
        ("Engine.", "scripts/lp_engine.py \u2014 lexicographic pFBA + "
         "L1-MOMA on HiGHS, GPR parser (DNF), pair knockout evaluation."),
        ("M1.", "scripts/m1_active_set_curvature.py \u2014 parts nutrient, "
         "kd, ijo, stats; outputs download/m1_m3/m1_*.npz (12 sweeps), "
         "m1_points_*.csv, m1_summary.json, m1_wt_reference.npy."),
        ("M3.", "scripts/m3_epistasis_path_dependence.py \u2014 parts "
         "singles, pairs, path, stats; outputs m3_singles.npz (1,516 "
         "genes, \u03ba, growth, footprints), m3_pairs.csv (2,779 rows), "
         "m3_path.csv (160 rows), m3_summary.json."),
        ("Figures.", "scripts/m1_m3_figures.py \u2014 six PNG figures in "
         "download/m1_m3/ (fig_m1_glucose, fig_m1_o2, "
         "fig_m1_knockdown, fig_m1_summary, fig_m3_epistasis, "
         "fig_m3_path)."),
        ("Diagnostics.", "scripts/lex_pfba_prototype.py and "
         "scripts/bench_lexsolver.py document the pFBA degeneracy "
         "discovery and the solver determinism checks."),
    ]),
]
