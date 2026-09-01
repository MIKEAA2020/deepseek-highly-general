#!/usr/bin/env python3
"""Content module for download/Root_Cause_Evaluation_report.pdf.

Kinds: h1, h2, body, quote, callout, table, figure, bullet_list.
Grounded in: download/m4/m4a_* , m4b_* , m4c_* (this turn), M1/M3 record,
and download/Active_Set_Bridge_v2.md (Theorems S/G/N1/N/D).
"""

CONTENT = [
    ("h1", "1. Verdict"),
    ("body",
     "This report evaluates, verifies, and explores the root-cause analysis "
     "supplied in the current turn: the claim that the unifying bridge "
     "weakened because it was built on the wrong order of smoothness. The "
     "text's diagnosis is correct and important, and it is now "
     "theorem-backed rather than merely measured: the lexicographic pFBA "
     "flux map is continuous and piecewise affine, its static curvature is "
     "a measure supported on the active-set skeleton, and the epsilon-"
     "squared holonomy normalization of the original conjecture was never "
     "admissible. However, the text misdescribes the measured objects in "
     "three ways, it attributes evidence to the wrong layer in one place, "
     "and its constructive program understates what is already proven "
     "while leaving its own central concept - treat the smooth geometric "
     "kappa as a separate regime - unmechanized. This document corrects "
     "the misdescriptions and closes the gap: Theorem R and the new "
     "measurement M4c give the separate regime a mechanism, a law, and a "
     "measured crossover."),
    ("callout", ("1.9995",
                 "slope of the second-difference law at epsilon << sigma "
                 "(sigma = 0.003; 1.9991-1.9995 at all four sigma) - the "
                 "smooth regime is real and entered by resolution")),
    ("callout", ("epsilon* / sigma = 3.1 - 0.7",
                 "measured crossover of the regime dial across four "
                 "smoothing scales (4.11 / 2.98 / 3.11 / 2.45) - the dial "
                 "position is a property of (epsilon, sigma), not of the "
                 "network")),
    ("body",
     "The root-cause text is best read as a correct popularization of the "
     "Active-Set Bridge v2 record with three technical slips and one "
     "missing theorem. Every claim was checked against the committed "
     "artifacts: the M4a pair census (76 pairs, six depths), the M4b "
     "two-parameter geometry and edge census, the M1/M3 record, the v2 "
     "theorem set, and - new in this turn - the M4c regime-dial "
     "experiment executed at the same codim-2 locus, 858 lexicographic "
     "solves. The frozen v21 manuscript is untouched; all deliverables "
     "are committed as source material for journal_manuscript v2+."),

    ("h1", "2. Claim-by-claim verification"),
    ("body",
     "Nineteen checkable claims were extracted from the text and "
     "adjudicated against the record. The verdicts: twelve correct "
     "(several already stronger in the record than in the text), four "
     "imprecise or misattributed, and three wrong as stated. The "
     "corrected replacements appear in Sections 4 and 5."),
    ("table", {
        "title": "Table 1. Verification of the root-cause claims (1-10)",
        "header": ["#", "Claim (condensed)", "Record", "Verdict"],
        "ratios": [0.05, 0.34, 0.42, 0.19],
        "rows": [
            ["1", "Bridge assumed a smooth map; holonomy O(eps^2)",
             "deepseek formulation A4 and its central display",
             "True (that is what was assumed)"],
            ["2", "v(theta) continuous, piecewise affine; derivative jumps "
             "at active-set events",
             "Theorem S(i); M1: affine segments to 8e-14 relative on all "
             "12 sweeps; mpLP chamber theory",
             "True, verified"],
            ["3", "The derivative jump is a first-order singularity",
             "Theorem S(ii): D^2 v is a measure on codim-1 interfaces",
             "True"],
            ["4", "Holonomy that scales as O(eps)",
             "No such object: state holonomy is exactly the identity; "
             "codim-2 defects are O(1) and scale-invariant; the O(eps) "
             "objects are the measure mass and the dynamic commutator",
             "Wrong object (RC1)"],
            ["5", "M4a: 76 pairs, observed slope 1.00, not 2",
             "64/76 pairs have chi = 0 exactly at all depths; 9 nonzero "
             "pairs with slopes 0.857-1.244, median 0.998; 3 near-floor",
             "Number right, description wrong (RC2)"],
            ["6", "The smooth curvature bridge is falsified",
             "Theorem N: the (1/eps^2)(H-I) limit is 0 at generic points "
             "and divergent on the codim-2 skeleton; slope-1 dynamic law",
             "True, and theorem-backed"],
            ["7", "FBA map lives on a stratified polyhedral complex",
             "Theorem S; 24 operational chambers in the (glc, O2) plane",
             "True"],
            ["8", "Curvature concentrated on strata, especially codim-2",
             "Two carriers: the D^2 v measure on codim-1 interfaces (M1's "
             "object) and the angle defect at codim-2 (Theorem G)",
             "Imprecise (RC4)"],
            ["9", "Holonomy can be first-order in loop size",
             "Defects are O(1), scale-invariant to four decimals; state "
             "holonomy exactly trivial; chi is O(eps) but is hysteresis",
             "False (RC1)"],
            ["10", "Gauss-Bonnet analogue = discrete angle defect",
             "Theorem G(ii): unfolding transport equals the defect to "
             "1e-14 on synthetic cones; plus the exact measure identity "
             "mu(Q) = the mixed second difference",
             "True for the graph geometry"],
        ],
        "note": "Record sources: download/m4/m4a_pairs.csv, m4b_summary.json, "
                "m1_m3/ summaries, Active_Set_Bridge_v2.md.",
    }),
    ("table", {
        "title": "Table 2. Verification of the root-cause claims (11-19)",
        "header": ["#", "Claim (condensed)", "Record", "Verdict"],
        "ratios": [0.05, 0.34, 0.42, 0.19],
        "rows": [
            ["11", "M4b's dense wedge-fan = piecewise-flat singular space",
             "Edge census: 9-10 boundary crossings per grid cell (up to 4 "
             "per edge) in the overflow corner vs exactly 2 in flat "
             "cells; M4c resolves the fan's slivers (RC6)",
             "True, with a refinement"],
            ["12", "Discrete connection; holonomy and curvature are "
             "singular first-order objects",
             "Connection exists (unfolding transport; the file's own "
             "projection transport is not one - v2 C3); its curvature is "
             "singular and O(1), not first-order",
             "Half-right (RC1, RC4)"],
            ["13", "Cannot unify by convergence to the smooth kappa_V",
             "Theorem N (atomicity obstruction); 6/6 audit consensus",
             "True"],
            ["14", "Step 1: define a discrete curvature from the active set",
             "Done: Theorem S (jump measure) + Theorem G (defect), "
             "machine-verified",
             "Already executed"],
            ["15", "Step 2: kappa_flux discretizes this discrete curvature",
             "M1 D2 mass 0.934-1.0 on active-set events; M3 footprint "
             "Spearman 0.865; the formal identity is not yet written",
             "Open (flagged)"],
            ["16", "Step 3: smooth kappa_V as ancestor or separate regime",
             "v2 constructs the geometry intrinsically; M4c (this turn) "
             "supplies the mechanism and law of the regime",
             "Now executed (M4c)"],
            ["17", "Step 4: kappa_time as integrated squared displacement",
             "Theorem S(iv): the exact integral identity, including the "
             "smooth term the text omits; M4c adds the (eps, sigma) "
             "design constraint",
             "Executed, extended"],
            ["18", "Bridge partially proven by the slope-1 law and the "
             "no-loose-kinks lemma",
             "N1 is proven and static; the slope-1 law is dynamic and "
             "independent of static epistasis (Spearman -0.347 full "
             "panel, -0.07 non-SL)",
             "Misattribution (RC3)"],
            ["19", "Do not connect the FBA metric to the smooth kappa_V",
             "Correct direction; the connection that does exist is "
             "coarse-graining (Theorem R), and it is measurable",
             "Replaced (Section 7)"],
        ],
        "note": "Spearman values from the M3b commutator-epistasis "
                "correlation panel (download/m1_m3/).",
    }),

    ("h1", "3. What the text gets right"),
    ("body",
     "Five substantive points survive verification unchanged, and each is "
     "stronger in the record than in the text. First, the root cause "
     "itself: the order-of-smoothness mismatch is the actual reason the "
     "epsilon-squared bridge failed, established at three independent "
     "levels - a priori theory (parametric LP: the optimizer under a "
     "fixed tie-break is piecewise affine on a finite complex, so the "
     "smoothness assumption was inadmissible from the start), machine "
     "measurement (M1's affine segments to 8e-14 and its second-order "
     "mass concentration), and theorem (v2 Theorem N, which proves no "
     "renormalization of the static holonomy yields a finite nonzero "
     "epsilon-squared limit)."),
    ("bullet_list", [
        ("Root cause.", "Wrong order of smoothness - correct, and now "
         "theorem-backed at three independent levels."),
        ("Falsification verdict.", "The smooth bridge is false because the "
         "mathematical object is different, not because the computations "
         "were wrong - agreed, and model-independent: the falsification "
         "follows from LP structure, so no simulation can rescue it."),
        ("Discrete bridge direction.", "A discrete stratified bridge exists "
         "- and is already constructed: the unfolding transport with "
         "proven no-loose-kinks lemma, measured O(1) defects, and the "
         "active-set skeleton as substrate."),
        ("Gauss-Bonnet instinct.", "For the flux-graph geometry the "
         "discrete angle defect is the right analogue, verified to 1e-14 "
         "on synthetic cones and scale-invariant on iML1515."),
        ("The four-step program.", "All four steps are the right program; "
         "steps 1, 2 (empirically), and 4 were already executed by the v2 "
         "record, and step 3 is completed by this report."),
    ]),

    ("h1", "4. Corrections"),
    ("h2", "RC1 - There is no O(eps) holonomy; the scalings form a "
           "trichotomy"),
    ("body",
     "In the executed record there are exactly four loop- or difference-"
     "like objects, and each has its own scaling. The static state "
     "holonomy of the flux map is exactly the identity for every closed "
     "loop at every scale, because v is a single-valued function. The "
     "static defect holonomy of the unfolding transport around a "
     "codim-2 vertex is O(1) and scale-invariant: the defects -7.1469 "
     "degrees and -23.9087 degrees reproduce to four decimals at loop "
     "radius delta and delta/2 - this is the Regge, angle-defect behavior "
     "the text itself invokes two paragraphs after claiming first-order "
     "holonomy, so the text contradicts itself. The dynamic commutator "
     "chi of sequential L1-MOMA adjustment - the object M4a actually "
     "measured - is O(eps) with slope near 1, but it is the hysteresis "
     "of greedy adjustment, not a connection holonomy: single releases "
     "are bit-exact identities (6 of 6), so the closed-loop non-return "
     "is irreversibility of the dynamics. The second-difference measure "
     "mass is O(eps) above the smoothing scale - the static first-order "
     "object. The distinction is not pedantry: it determines which "
     "experiment can detect which object (loop compositions for defects, "
     "second differences for measure mass, order-swap protocols for chi), "
     "and the text's own program depends on exactly these channels."),
    ("h2", "RC2 - The slope-1.00 statistic describes 9 of the 76 pairs"),
    ("body",
     "The M4a census is bimodal, and the bimodality is the finding. "
     "Sixty-four of the 76 pairs (84 percent) have chi exactly zero at "
     "every one of the six perturbation depths - the decoupled stratum "
     "in which the two knockdowns do not interact through the tangent "
     "cone. Nine pairs scale with slopes from 0.857 to 1.244 (median "
     "0.9982: sdhD+nuoG 0.9982, sdhD+nuoH 0.9982, gapA+atpC 1.2439, "
     "atpD+nuoJ 0.9982, ptsH+gapA 1.0049, atpH+nuoM 0.9982, aceE+cyoC "
     "0.9759, zwf+gnd 0.8573, pgi+zwf 1.0026), and three are near the "
     "floor. The first-order non-commutativity is therefore sparse and "
     "structural, confined to the interacting stratum. Quoting a single "
     "slope of 1.00 as if it applied to all 76 pairs hides precisely the "
     "sparsity that the graded-CRISPRi order-swap prediction forecasts: "
     "most pairs are order-insensitive; a minority are linearly "
     "order-sensitive."),
    ("h2", "RC3 - The slope-1 law cannot support the static bridge"),
    ("body",
     "The text writes that the discrete bridge may already be partially "
     "proven by M4's slope-1 law and the no-loose-kinks lemma. The "
     "lemma is indeed proven and static. But the slope-1 law is a "
     "property of the dynamic layer - the sequential adjustment maps - "
     "and M3b measured its independence from the static-layer epistasis "
     "on the same pair panel: Spearman of chi against the epistasis "
     "magnitude is -0.347 (p = 6.8e-6) over the full panel and -0.07 "
     "(p = 0.43, no association) within non-synthetic-lethal pairs. The "
     "optimum-level non-additivity and the transient-level "
     "non-commutativity are distinct signatures that must be carried "
     "separately; evidence for one is not evidence for the other, and "
     "the bridge transports the active-set skeleton into both."),
    ("h2", "RC4 - Two curvature carriers, not one"),
    ("body",
     "The static curvature of the FBA map is carried by two distinct "
     "singular objects. The Jacobian-jump measure D^2 v is supported on "
     "the codim-1 interfaces - the object M1 measured and the object the "
     "deepseek formulation itself describes as Dirac measures on the "
     "active-set interfaces. The angle-defect measure is supported on "
     "the codim-2 crossings of the flux graph - Theorem G's object, with "
     "the Gauss-Bonnet content. They are related by discrete structure "
     "equations (the dihedral kinks of incident faces determine the "
     "vertex defect through the unfolding composition) but they are not "
     "the same object: different strata, different normalizations, "
     "different detection experiments. M4c adds the next level of the "
     "hierarchy: within a codim-1 wall cluster there are sub-resolution "
     "sliver chambers, so the fine structure is atomic at multiple "
     "scales - precisely the content of Theorem N."),
    ("h2", "RC5 - The falsification is a priori, not empirical"),
    ("body",
     "The piecewise-affine structure of the lexicographic optimizer is a "
     "theorem of multiparametric linear programming (Gal and Nedoma "
     "1972; Bemporad, Borrelli and Morari 2002 and the mp-control "
     "literature thereafter). The smoothness assumption was therefore "
     "never admissible: M4a's slope near 1, M1's mass concentration, "
     "and M4b's chamber census confirm the theorem's structure at "
     "machine precision rather than discovering a failure. This matters "
     "for the manuscript narrative: the result is robust and "
     "model-independent - no simulation budget or network choice can "
     "rescue the smooth bridge - and the correct citation frame is mpLP "
     "theory plus Theorem N, not an empirical surprise."),
    ("h2", "RC6 - The wedge-fan is operationally dense but measure-tame"),
    ("body",
     "The edge census is as the text says: up to 9-10 chamber-boundary "
     "crossings per grid cell, with up to 4 on a single edge and nested "
     "sliver chambers, in the overflow corner where the D2 mass "
     "concentrates, versus exactly 2 per cell in flat regions. But the "
     "finer M4c census resolves what M4b could not: the sliver cluster "
     "at t approximately 0.00187 on the vertex cut is 2.44e-6 wide, "
     "carries opposite jump vectors of L2 norm 1884.6, and self-cancels "
     "to a net measure jump of 8.90 (the second cluster: width 3.7e-6, "
     "jumps at most 0.81, net 1.32; the third: width 6.5e-4, max jump "
     "22.3, net 9.54). The fan's operational signature density "
     "overstates its curvature-measure density: many thin chambers "
     "contribute little net mass. Dense is correct at the analyzed "
     "resolution; at the finer resolution the same locus is a hierarchy "
     "of self-cancelling atoms."),

    ("h1", "5. Exploration: Theorem R and the M4c regime dial"),
    ("h2", "5.1 The theorem"),
    ("body",
     "The text's step 3 - treat the smooth geometric kappa as a "
     "conceptual ancestor or a separate regime, not as the limit object "
     "- was a position without a mechanism: Theorem N blocks the "
     "pointwise limit, but nothing in the record said what the smooth "
     "regime is or when it is entered. Theorem R closes the gap. Let v "
     "be the continuous piecewise-affine map, mu = D^2 v its curvature "
     "measure, and phi_sigma a Gaussian mollifier at scale sigma. Then "
     "D^2 of the smoothed map equals mu convolved with phi_sigma - "
     "exactly: the smoothed curvature is the same measure, smeared, and "
     "no new object appears. On a line through the parameter space with "
     "events (t_e, Delta_e), the epsilon-second difference of the "
     "smoothed map equals the sum of Delta_e weighted by a closed-form "
     "kernel K evaluated at the event offsets. Asymptotically it scales "
     "as eps-squared times the smeared density for epsilon much less "
     "than sigma - the smooth, Riemannian regime - and approaches the "
     "sum of Delta_e times (epsilon minus distance) for epsilon much "
     "greater than sigma - the discrete, kink regime. The crossover is "
     "at epsilon-star proportional to sigma. And the total vector mass "
     "is sigma-independent: the discrete and smooth objects carry the "
     "same curvature, only distributed differently."),
    ("quote",
     "The smooth kappa_V is not the limit of the discrete object - "
     "Theorem N blocks that. It is the same measure at finite "
     "resolution sigma. The perturbation scale epsilon versus the "
     "resolution sigma selects the regime; the dial is measurable and "
     "falsifiable."),
    ("h2", "5.2 The measurement"),
    ("body",
     "M4c was executed at the M4b codim-2 vertex (glucose 1.692, oxygen "
     "1.480), along the same cut direction, with the deterministic "
     "lexicographic engine: 858 solves, an event census refined by "
     "signature bisection to 1e-6, and a kernel closed-form self-test "
     "at 1.2e-6. The census found 12 events, 11 kinked and one "
     "mask-type (the no-loose-kinks prediction: a signature change with "
     "no flux kink), with a telescoping residual of 4.0e-14. The dial "
     "was read from the exact convolution of the machine-measured "
     "measure, with independent 5-point Gauss-Hermite machine "
     "evaluations as validation wherever epsilon is at least sigma/2."),
    ("table", {
        "title": "Table 3. The regime dial (exact convolution of the "
                 "measured measure)",
        "header": ["sigma", "slope (eps <= sigma/3)", "slope (eps >= 3 sigma)",
                   "eps*", "eps*/sigma"],
        "ratios": [0.14, 0.24, 0.26, 0.18, 0.18],
        "rows": [
            ["0.003", "1.9995", "1.13 (local -> 1)", "0.0123", "4.11"],
            ["0.01", "1.9991", "1.16", "0.0298", "2.98"],
            ["0.03", "1.9994", "1.14", "0.0933", "3.11"],
            ["0.1", "1.9992", "1.17", "0.2447", "2.45"],
        ],
        "note": "The epsilon-squared law holds to four significant figures "
                "at every sigma; the crossover scales linearly in sigma "
                "with c approximately 3.",
    }),
    ("figure", ("/home/z/my-project/download/m4/fig_m4c_scaling.png",
                "Figure 1. The regime dial: second-difference magnitude "
                "versus perturbation step, one curve per smoothing scale. "
                "Slope 2 guides the smooth regime, slope 1 the discrete "
                "regime; dotted verticals mark epsilon = sigma.",
                300)),
    ("table", {
        "title": "Table 4. Machine validation of the convolution identity "
                 "(epsilon >= sigma/2)",
        "header": ["sigma", "n valid", "median rel. error", "max rel. error"],
        "ratios": [0.22, 0.22, 0.28, 0.28],
        "rows": [
            ["0.003", "9", "0.4%", "11.9%"],
            ["0.01", "8", "1.9%", "56.7%"],
            ["0.03", "7", "5.4%", "84.0%"],
            ["0.1", "6", "8.7%", "70.1%"],
        ],
        "note": "Errors grow with sigma as the node-kink discretization and "
                "Gaussian-tail truncation of the quadrature grow; the "
                "sigma = 0.003 column is the clean independent check.",
    }),
    ("figure", ("/home/z/my-project/download/m4/fig_m4c_density.png",
                "Figure 2. Left: the smeared curvature density - the "
                "measure convolved with Gaussians at three scales - with "
                "the kink jumps as stems. Right: machine versus exact "
                "identity validation.",
                225)),
    ("callout", ("8.9 vs 1884.6",
                 "net measure jump versus internal jump pair of the "
                 "resolved sliver chamber (width 2.4e-6) - E31's fine "
                 "structure: the operational fan overcounts events, the "
                 "measure is tamer")),
    ("h2", "5.3 Two findings beyond the dial"),
    ("body",
     "First, a numerical echo of Theorem N: a fixed-node quadrature does "
     "not smooth below its node spacing. The 5-point Gauss-Hermite "
     "evaluation of the smoothed map is itself piecewise affine in the "
     "evaluation point - each node translates the kinks of v - so the "
     "machine difference vanishes exactly for epsilon below the distance "
     "to the nearest node-translated kink, while the exact convolution "
     "gives the epsilon-squared law. Discretized smoothing does not "
     "remove the atoms unless the kernel itself is resolved. This "
     "constrains any future empirical second-difference protocol "
     "(the open item E28): the analysis must state its (epsilon, sigma) "
     "pair and resolve the kernel, or it will silently measure a "
     "translated-kink artifact. Second, the wall-free control at "
     "clearance 0.165 with sigma = 0.03: the machine second difference "
     "is at most 1.5e-11 below reach - curvature is carried by the "
     "smeared walls, not by the chamber interiors, which is the locality "
     "side of the same coin."),

    ("h1", "6. What the bridge now says"),
    ("body",
     "With Theorem R in place, the three kappa objects connect through "
     "the active-set skeleton as one measure at multiple resolutions. "
     "The geometric curvature is the viability-weighted defect plus jump "
     "measure of the flux graph (Theorems S and G, provable and machine-"
     "verified). The rerouting statistics are event-triggered "
     "functionals of the same measure (M1: mass 0.934-1.0; M3: footprint "
     "alignment 0.865). The time-course object integrates the event "
     "measure along trajectories (Theorem S(iv), with its smooth term "
     "and its integral - not pointwise - form). The smooth geometric "
     "kappa is the same measure convolved at resolution sigma (Theorem "
     "R), entered whenever epsilon is much smaller than sigma. The "
     "dynamic order-sensitivity is the first-order commutator (Theorem "
     "D) - a distinct signature, statistically independent of the "
     "optimum-level epistasis, and carried separately. What remains "
     "open is now precisely localized: the formal statement kappa_flux "
     "= F of mu for the manuscript's exact definition, with the E24 "
     "recalibration test; E28 under its new (epsilon, sigma) design "
     "law; the two-dimensional sliver census; and model-family "
     "regularity for any mesoscopic defect-density limit."),

    ("h1", "7. The corrected bottom line"),
    ("quote",
     "Root cause: correct - FBA is piecewise affine, so its static "
     "curvature is a measure on the active-set skeleton, not a smooth "
     "two-form; the epsilon-squared holonomy normalization was "
     "inadmissible (an mpLP theorem, so the failure is model-"
     "independent). Bridge status: the smooth bridge is not merely "
     "falsified - it is blocked by the atomicity theorem; the discrete "
     "bridge is not plausible-and-partially-proven - it is constructed "
     "and machine-verified, with the dynamic commutator law (slope 1, "
     "sparse: 9 of 76 interacting pairs) as its falsifiable prediction; "
     "one identification step remains open. Implication: do not claim "
     "convergence of the FBA metric to the smooth kappa_V - and do not "
     "merely treat kappa_V as a separate regime. State the dial: the "
     "smooth object is the same curvature measure at resolution sigma; "
     "perturbation scale versus resolution selects the regime, with "
     "measured crossover epsilon-star approximately 3 sigma and mass "
     "conservation across the dial. The unification is a resolution "
     "statement, not a limit statement."),

    ("h1", "8. Deliverables and status"),
    ("table", {
        "title": "Table 5. Artifacts of this evaluation",
        "header": ["Artifact", "Content"],
        "ratios": [0.42, 0.58],
        "rows": [
            ["download/m4/m4c_summary.json",
             "dial, census, validation, slivers, control, the "
             "quadrature-resolution finding"],
            ["download/m4/m4c_scaling.csv",
             "machine and exact second differences over the (eps, sigma) "
             "grid"],
            ["download/m4/m4c_cut_events.csv",
             "12 events: positions, jump norms, segment slopes, "
             "kinked/mask classification"],
            ["download/m4/fig_m4c_scaling.png, fig_m4c_density.png",
             "the dial figure and the density/validation figure"],
            ["scripts/m4c_regime_dial.py",
             "the experiment (reuses scripts/lp_engine.py)"],
            ["scripts/lp_engine.py",
             "engine patch: deterministic presolve-off retry, activating "
             "only where the original returned failure"],
            ["download/Root_Cause_Evaluation.md",
             "the full evaluation (source material for v2+)"],
        ],
    }),
    ("body",
     "Standing instructions were honored throughout: the push check "
     "confirmed all previous work already on the remote before this turn "
     "began; the frozen v21 manuscript is untouched; every number quoted "
     "in this report is traceable to a committed artifact. The strategic "
     "consequence for the manuscript line: the missing theorem of the "
     "unification section should be written as a resolution statement - "
     "one measure, multiple resolutions, measured dial - replacing both "
     "the falsified smooth-limit claim and the vague separate-regime "
     "language, with Theorems S, G, N1, N, D, and R as the supporting "
     "spine and E28 as the empirical residue."),
]
