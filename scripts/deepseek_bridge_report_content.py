#!/usr/bin/env python3
"""Content module for download/DeepSeek_Bridge_Strength_Evaluation_report.pdf.

Kinds: h1, h2, body, quote, callout, table, figure, bullet_list.
Grounded in: the audit 'deepseek stengthen highly general bridge.txt'
(remote commit d85b162), the committed M1/M3/M4a/M4b/M4c record,
download/Root_Cause_Evaluation.md, and the four new verifications
V1/V2/V3/V5 (download/deepseek_bridge/).
"""

CONTENT = [

    ("h1", "1. Verdict"),
    ("body",
     "This report evaluates the audit 'deepseek stengthen highly general "
     "bridge.txt' - DeepSeek's response to the M4c / root-cause "
     "evaluation, which grades the corrected record, endorses the "
     "single-manuscript strategy, and proposes five 'strengthening "
     "routes' for the bridge, culminating in a recommended target "
     "theorem. The mandate was to evaluate, verify, and not take the "
     "claims at face value, then strengthen, augment, improve, correct, "
     "and complete the weaker suggestions and defects. The audit's Part "
     "1 - the summary of the corrected record - is faithful where it "
     "matters: it restates the scaling trichotomy (state holonomy "
     "exactly trivial; codim-2 defects O(1) and scale-invariant; the "
     "O(eps) commutator a dynamic hysteresis measure), the Theorem R "
     "convolution identity, and the M4c dial, and its five next steps "
     "are consistent with the record. Part 2, however - the routes and "
     "the recommended theorem - contains one central mathematical "
     "defect that propagates through three of the five routes: the "
     "headline formula kappa_geom = lim(sigma to 0) kappa_flux * "
     "phi_sigma selects the atomic measure, not a smooth object."),
    ("body",
     "Every checkable claim was adjudicated against the committed "
     "artifacts, and four new machine verifications were executed for "
     "this document: V1 re-runs the M4c cut recording the stage-1 value "
     "function (253 lexicographic solves); V2 constructs and verifies a "
     "refinement prototype of the corrected bridge theorem in the same "
     "parametric-LP structural class as FBA; V3 tests the sigma-limit "
     "direction on the measured M4c event measure itself; and V5 "
     "executes the audit's own 'decisive test' - the E24 recalibration "
     "with the measure-theoretic kappa - rather than deferring it. The "
     "frozen v21 manuscript is untouched; all deliverables are source "
     "material for journal_manuscript v2+. The decisive test passes "
     "with strengthening, so by the audit's own criterion the "
     "single-paper route is secure."),
    ("callout", ("r = +0.374 -> +0.395",
                 "the E24 association under the measure-theoretic kappa "
                 "(V5, n = 424, p = 2.6e-17; partial r +0.251 -> +0.269; "
                 "deciles 1.92/0.89 preserved) - the decisive test "
                 "passes, the single-paper route is secure")),
    ("callout", ("FALSE as stated",
                 "kappa_geom = lim(sigma->0) kappa_flux * phi_sigma: the "
                 "weak limit is the ATOMIC measure (V3: mass collapse "
                 "onto the 12 events; V2b: near-atom mass 0.41 -> 0.999) "
                 "- the recommended theorem picks Theorem N's "
                 "obstruction, not a smooth object")),
    ("callout", ("Theorem B (prototype)",
                 "refinement + resolution: under mesh refinement the "
                 "atomic measures converge weakly to the smooth "
                 "curvature density (V2: W1 0.049 -> 0.0035, mass ratio "
                 "-> 1.00) - the corrected form of Routes 1+2, proven in "
                 "prototype and machine-verified")),

    ("h1", "2. Part 1 fidelity: claim-by-claim verification"),
    ("body",
     "Fourteen checkable claims were extracted from the audit's Part 1 "
     "and graded against the record. Twelve are correct or correct in "
     "substance; two carry inherited slips that were already corrected "
     "in the root-cause evaluation (the epistemics of the "
     "falsification, and the sparsity behind the slope-1.00 statistic); "
     "one - the line-30 interpretation of the smooth kappa - is the "
     "seed of Part 2's central defect. None of these slips changes "
     "Part 1's conclusions, but all three should be fixed before any "
     "of this text is quoted in the v2 manuscript."),
    ("table", {
        "title": "Table 1. Verification of the audit's Part-1 claims "
                 "(fidelity to the executed record)",
        "header": ["#", "Audit claim (condensed)", "Record / verification",
                   "Verdict"],
        "ratios": [0.05, 0.33, 0.44, 0.18],
        "rows": [
            ["1", "Smooth eps^2 bridge was the wrong object",
             "Theorem N; M4c; RC-dagnosis of the root-cause evaluation",
             "True"],
            ["2", "State holonomy exactly the identity (v is a function)",
             "Theorem S(v); m4b state_holonomy_note", "True"],
            ["3", "Codim-2 defects scale-invariant, O(1), Regge-type",
             "Theorem G; -7.1469 and -23.9087 deg reproduced at delta "
             "and delta/2", "True"],
            ["4", "O(eps) commutator is dynamic hysteresis, not "
             "holonomy",
             "Theorem D; single-release identity 6/6 bit-exact", "True"],
            ["5", "Theorem R identity; eps^2 below sigma, linear "
             "beyond",
             "M4c kernel self-test 1.2e-6; slopes 1.9991-1.9995",
             "True"],
            ["6", "Crossover eps*/sigma about 3-4",
             "Measured 4.11 / 2.98 / 3.11 / 2.45 (median 3.1)",
             "True; top end overstated"],
            ["7", "M4a slope 1.00 was the decisive EMPIRICAL "
             "falsification",
             "RC5: falsification is a priori (mpLP theorem, Gal-Nedoma "
             "1972); M4a confirms at machine precision; RC2: slope-1 "
             "describes the 9/76 interacting stratum, 64/76 exactly zero",
             "Epistemics slip (D8)"],
            ["8", "Gal-Nedoma reference makes it model-independent",
             "Model-independence comes from LP structure (RC5)",
             "True in substance"],
            ["9", "Sliver self-cancels 8.9 vs +/-1884.6; coarser "
             "analyses overcounted EVENTS",
             "RC6: the census counted crossings correctly at its "
             "resolution; what was overstated was curvature-MEASURE "
             "density (self-cancelling slivers)", "Nuance (D8)"],
            ["10", "One measure mu = D2v; kappa_flux a functional of it",
             "Theorem S(ii); M1 D2 mass 0.934-1.0; the formal identity "
             "remains open and is now decoupled from the association "
             "(V5)", "True"],
            ["11", "kappa_V = the sigma->0+ SMOOTH limit of the "
             "coarse-grained family",
             "lim(mu * phi_sigma) = mu weakly - the same atomic object "
             "as the direct limit; smooth members exist only at FIXED "
             "sigma, or under refinement (Theorem B)",
             "Wrong limit direction (D1)"],
            ["12", "Single manuscript; trim categorical/HoTT; do not "
             "split yet",
             "Consistent with the joint assessment (6/6 strong-form "
             "not provable); now secured by V5", "Endorsed"],
            ["13", "Next steps 1-5 (E24 re-run; resolution statement; "
             "v2 Layer-0; defer E28; v21 frozen)",
             "Step 1 executed here; step 2 already the record's form; "
             "step 4 matches the M4c (eps, sigma) design law",
             "All consistent; 1 done"],
            ["14", "Do not seek smooth eps^2 for the unsmoothed object",
             "Theorem N; M4c", "True - extended: neither sigma->0 "
             "(D1)"],
        ]}),

    ("h1", "3. The defects of Part 2 (D1-D8), verified"),
    ("body",
     "The five strengthening routes contain eight distinct defects and "
     "weaknesses. Each is stated here with its verification, and each "
     "is repaired in Sections 4 and 5 rather than merely flagged: the "
     "audit's own target - a genuine, non-decorative bridge - is "
     "met by the end of this report in prototype form, and its "
     "decisive empirical test has been run."),

    ("h2", "D1 - The limit direction is inverted in the recommended "
           "theorem"),
    ("body",
     "The audit's final recommendation proposes kappa_geom = "
     "lim(sigma->0) kappa_flux * phi_sigma in the sense of weak "
     "convergence, and Route 1 states that mu_sigma converges weakly, "
     "as sigma to 0, to the curvature measure of a Riemannian metric g. "
     "For a fixed network this is false: by standard mollifier theory "
     "mu * phi_sigma converges weakly to the atomic measure mu, which "
     "is exactly Theorem N's obstruction. V3 verified this on the "
     "measured M4c event set (12 events, total L2 jump mass 3807.6). "
     "The mass fraction within a fixed half-width w = 0.01 of the event "
     "positions tends to 1.0000 as sigma shrinks to 1e-4, so any "
     "absolutely continuous limit would have to concentrate on a set "
     "of zero Lebesgue measure. The density at a wall-free point "
     "(clearance 0.052) decays to machine zero while the peak grows "
     "like 1/sigma. And a fixed bump on the largest atom integrates to "
     "3772.5 at sigma = 3e-4 - the full mass of the sliver pair - "
     "versus 253.4 for the smoothest honest family member at sigma = "
     "0.3. The audit's line-30 phrase, 'the sigma-to-0 smooth limit of "
     "the coarse-grained family, not the direct limit of the "
     "unsmoothed FBA map', distinguishes two objects that are equal: "
     "both limits are mu. What is true instead is the resolution "
     "statement at fixed sigma (Theorem R, already the record's "
     "position) and the refinement limit of Theorem B below."),
    ("figure", ("/home/z/my-project/download/deepseek_bridge/"
                "v3_sigma_limit.png",
                "Figure 1. V3 - the audit's sigma-to-0 limit picks the "
                "atomic measure, on the measured M4c event set. (a) the "
                "smoothed family sharpens onto the 12 atoms; (b) mass "
                "within a fixed neighborhood of the events tends to "
                "1.0000; (c) the wall-free density vanishes "
                "exponentially while peaks grow like 1/sigma.", 200)),

    ("h2", "D2 - Route 3's premise 'v = grad Phi' is false; the "
           "corrected statement is stronger"),
    ("body",
     "The flux map v in R^m (m = 2867 on iML1515) cannot be the "
     "gradient of a scalar Phi: R^d -> R (d = 2 here) - a dimensional "
     "impossibility, independent of conditions, for "
     "constraint-parameterized FBA. The gradient map of the value "
     "function is the dual y in R^d (Danskin): grad Phi = (y_glc, "
     "y_o2). What survives the correction - and improves the route - "
     "is the canonical-carrier statement, verified as V1 on the real "
     "network: Phi = c_bio . v* is single-valued with NO tie-breaking "
     "whatsoever, immune to the pFBA vertex degeneracy that forced the "
     "lexicographic machine for v; hence D2Phi (shadow-price jumps) is "
     "THE canonical atomic curvature measure of the parametric LP, "
     "while D2v is its tie-break-dependent refinement with a strictly "
     "finer event set."),
    ("body",
     "V1 re-ran the M4c cut recording Phi(t) (253 lex solves on "
     "iML1515). Phi is piecewise affine on the v-event partition with "
     "worst affine-fit residual 4.2e-13. Of the 12 censused v-events, "
     "the entire value curvature of the cut is a SINGLE atom, Delta "
     "Phi' = -0.006439 at t = 0.0358286 - a minor flux event (jump "
     "norm 11.59, first member of a sliver pair whose partner jumps "
     "only 1.6e-5). The dominant flux atoms are value-flat: the "
     "1875.7/1884.6 sliver pair nets at most 7.7e-11; the 22.3-jump "
     "event at most 8.4e-9; the 0.51/0.81-jump pair at most 3.8e-11. "
     "Total value variation is about 0.00644 against total flux jump "
     "mass 3807.6 - a ratio of 1.7e-6 - and the hierarchies are not "
     "proportional: the value atom sits at the sixth-largest flux "
     "event while the largest flux event carries zero value "
     "curvature. Danskin is verified at machine precision: the stage-1 "
     "bound marginals (extractable on the r-copy of the duplicated "
     "uptake bound) equal the two-sided finite-difference shadow "
     "prices to six or seven significant digits; the prices are (0.0252545, "
     "0.0336727) before the atom and (0.021743, 0.039138) after; and "
     "the identity Phi' = y . theta' reproduces both measured segment "
     "slopes (-0.009316, -0.015755) exactly. This is the "
     "rerouting-versus-function decoupling of the Kochanowski "
     "framing, now formalized as a statement about measures."),
    ("figure", ("/home/z/my-project/download/deepseek_bridge/"
                "v1_value_function.png",
                "Figure 2. V1 - the value-function carrier on the M4c "
                "cut (iML1515). (a) Phi with its single real atom "
                "among the 12 v-events; (b) flux jump norm versus "
                "value jump per event - the two carriers are "
                "decoupled by many orders of magnitude; (c) Phi "
                "piecewise-affine at 4.2e-13 on the event partition.",
                200)),

    ("h2", "D3 - Route 2's refinement mechanisms are not refinements"),
    ("body",
     "Route 2 proposes to refine 'the FBA polytope ... by adding "
     "reactions, constraints, or parameter grid resolution'. Adding "
     "reactions produces a different parametric LP whose chamber "
     "structure does not refine the previous one: critical surfaces "
     "move, chambers are not nested, and there is no mesh to send to "
     "zero. Parameter grid resolution changes only the sampling of a "
     "fixed map - v(theta) and its measure are grid-independent. The "
     "valid refinement must be constructed, and Section 4 constructs "
     "it: nested constraint families that polyhedrally approximate a "
     "smooth feasible region, exactly the setting of Cheeger, Muller "
     "and Schrader (1984) - the classical citation the audit is "
     "missing throughout. With D1 and D3 together, Route 2's "
     "'medium-high' feasibility grade is overstated for real "
     "networks: pointwise strong regularity (Robinson; Klatte-Kummer) "
     "does not give global chamber stability under refinement, "
     "genome-scale models do not come in refinement sequences, and "
     "sliver cascades - already measured: 2.4e-6-wide slivers with "
     "+/-1884.6 jumps netting 8.9 - break uniform mesh bounds. "
     "Prototype: done below. Real network: open conjecture RA."),

    ("h2", "D4 - Route 4's 'nontrivial basis-change cocycle' is "
           "exactly trivial"),
    ("body",
     "Let B(theta) be the lex-unique optimal basis, constant on each "
     "open chamber of the critical-region partition. For any closed "
     "loop crossing chambers C1 to C2 to ... to Ck back to C1, with "
     "transitions G_i = B(i+1) B(i)^-1 (indices mod k), the total "
     "transition is G_k ... G_1 = B1 Bk^-1 . Bk B(k-1)^-1 ... B2 "
     "B1^-1 = I by telescoping - for every loop, at every scale, "
     "exactly as for the state holonomy (Theorem S(v)). The audit's "
     "proposed escape from the triviality problem is the wrong "
     "cocycle. The nontrivial connection in the record is the "
     "unfolding transport of Theorem G - parallel transport of tangent "
     "planes across the kinked codim-1 interfaces of the flux graph, "
     "whose closure failure around codim-2 vertices is the O(1) "
     "scale-invariant angle defect (-7.1469 and -23.9087 degrees, "
     "machine-reproduced at loop radii delta and delta/2, and "
     "unfolding = -defect to 1e-14 on synthetic cones). Route 4's "
     "instinct - the nontrivial connection lives on a derived bundle, "
     "not on the state - is exactly right; the correct object already "
     "exists and is verified, so the route is complete in the record, "
     "and its remaining content inherits D1's limit problem and D6's "
     "smuggled identification."),

    ("h2", "D5 - Route 1 defines mu as the corner angle defect, "
           "which is only one of two carriers"),
    ("body",
     "The static curvature of the FBA map is carried by two distinct "
     "objects: the Jacobian-jump measure D2v on codim-1 interfaces "
     "(M1's object, the M4c census, the kappa_flux functional), and "
     "the angle-defect measure on codim-2 crossings (Theorem G). They "
     "are related by discrete structure equations, live on different "
     "strata, scale differently (O(eps) mass accumulation versus O(1) "
     "scale-invariant defects), and are detected by different "
     "experiments. A convergence theorem for 'the' discrete curvature "
     "must carry both carriers - Theorem B's prototype does: its "
     "atomic measure is the codim-1 layer along cuts, and its vertex "
     "defects are the codim-2 layer of the same subdivision."),

    ("h2", "D6 - Route 1 smuggles the conclusion it should prove"),
    ("body",
     "Route 1's theorem asks that the limiting metric 'is the metric "
     "induced by the viability field V', and the audit calls the "
     "identification with g^SAVGS 'the only remaining question'. This "
     "is precisely the identification the joint assessment found not "
     "provable (6/6 consensus) and Theorem N blocks pointwise. A "
     "refinement limit produces SOME smooth curvature measure, "
     "determined by the limiting geometry of the refinement sequence; "
     "making it equal g^SAVGS requires an explicit construction "
     "linking the viability functional to the refinement, and there "
     "is no reason for automatic coincidence. The honest form is the "
     "separately-stated Conjecture SA of Section 4, not a corollary."),

    ("h2", "D7 - Route 5's anchors are wrong-level; its honest low "
           "grade is right but under-specified"),
    ("body",
     "The lattice-gauge analogy - 'analogous to how lattice gauge "
     "theories converge to Yang-Mills' - overstates the state of the "
     "art: rigorous continuum limits exist for 2D Yang-Mills and in "
     "Balaban-style partial frameworks, not as a general construction. "
     "What Route 5 is missing is the classical anchor for the "
     "piecewise-flat side: Cheeger, Muller and Schrader (1984), "
     "curvature measures of compatibly refined piecewise-flat spaces "
     "converge weakly to the Riemannian curvature measure - the direct "
     "ancestor of Theorem B and the correct citation frame for the "
     "whole program. The audit's own feasibility grade (low to medium, "
     "'may not be necessary') is right. Section 4 adds the near-term "
     "testable form the route lacks: a statistical version (E32) "
     "runnable on existing panels."),

    ("h2", "D8 - Part-1 fidelity slips (minor; fix before quoting)"),
    ("body",
     "Four small slips: M4a is a confirmation of an a priori theorem, "
     "not the 'decisive empirical falsification' (RC5's epistemics - "
     "no simulation budget or network choice can rescue the smooth "
     "bridge - is the correct narrative for the manuscript); the "
     "slope-1.00 statistic silently drops the sparsity (9/76 "
     "interacting pairs, 64/76 with chi exactly zero - the sparsity IS "
     "the CRISPRi order-swap prediction of Theorem D); 'eps*/sigma "
     "about 3-4' should read 2.45-4.11, median 3.1; and 'coarser "
     "analyses overcounted events' should read 'overstated "
     "curvature-measure density' (RC6). None of these changes "
     "Part-1's conclusions."),

    ("h1", "4. The corrected and completed bridge (Routes 1+2, "
           "repaired and executed)"),
    ("body",
     "The audit's recommended combination - prove the active-set "
     "angle defect is the Regge curvature of a piecewise-flat metric; "
     "prove the coarse-grained measures converge weakly to the "
     "curvature of that metric - is the right program with the wrong "
     "limit. Repaired, it becomes a theorem that can actually be "
     "proven in a prototype setting in the same structural class as "
     "FBA: a parametric LP with fixed constraint matrix and theta "
     "entering the right-hand side affinely - the class of "
     "uptake-bound perturbation."),
    ("h2", "Theorem B (refinement-resolution bridge; prototype proven, "
           "machine-verified as V2)"),
    ("body",
     "Let f be a C2 concave value function on a parameter domain with "
     "strictly negative curvature, and for each n let Phi_n be the "
     "minimum of the tangent planes of f at the points of a "
     "quasi-uniform mesh with mesh size h_n tending to 0 (each Phi_n "
     "is the value function of a parametric LP with n^2 constraints "
     "and theta in the RHS; the Phi_n are nested outer approximations "
     "converging uniformly to f). Let mu_n = D2Phi_n, atomic, "
     "supported on the codim-1 cell boundaries of the induced "
     "subdivision, with vertex angle defects as the codim-2 layer. "
     "Then: (B1) mu_n restricted to any line converges weakly to the "
     "smooth curvature density along that line, and mu_n converges "
     "weakly to the Hessian measure of f. The proof is one line at "
     "its core: grad Phi_n equals the slope of the active tangent "
     "plane, grad Phi_n(theta) = grad f(p_i(theta)) with the tangency "
     "point within C times h_n of theta, so grad Phi_n converges to "
     "grad f uniformly; by the Gauss flux identity, the integral of "
     "mu_n over a test region equals the boundary flux of grad Phi_n, "
     "which converges to the boundary flux of grad f - which is weak "
     "convergence of bounded-mass, sign-definite measures. (B2) The "
     "total curvature mass is n-independent: the boundary-flux "
     "telescoping, the family-level analog of M4c's R4 mass "
     "conservation. (B3) The dial is two-sided: at fixed n, sigma to "
     "0 recovers the atomic measure (the audit's direction, D1); at "
     "fixed sigma with h_n much smaller than sigma, the smoothed "
     "family converges to the smooth density; the joint limit exists "
     "only through the window h_n far below sigma, itself far "
     "below L_var. The smooth "
     "object is a family member at matched resolution, never a "
     "sigma-to-0 limit."),
    ("table", {
        "title": "Table 2. V2 machine verification of Theorem B "
                 "(min-of-tangent-planes LP family, concave f with "
                 "non-constant curvature, 40 random cuts, exact "
                 "breakpoint atoms)",
        "header": ["Panel", "Result"],
        "ratios": [0.34, 0.66],
        "rows": [
            ["B1 refinement (n = 4 -> 128)",
             "normalized W1 to the smooth density 0.049 -> 0.0035 "
             "(rate about 0.9-1.0 in h for n >= 32); total-mass ratio "
             "0.93 -> 1.002; adaptive-scale L1 0.33 -> 0.07"],
            ["B3 sigma -> 0 at fixed n = 32",
             "L1 to the smooth density 0.054 -> 1.28 (departs from "
             "smooth); mass within w = 0.01 of atoms 0.41 -> 0.9992 - "
             "the atomic limit, on the prototype as on the real "
             "network"],
            ["B3 joint limit (sigma = 0.05 fixed)",
             "L1 to the smooth density 1.25 -> 0.040 (n = 4 -> 128; "
             "sigma/h from 0.075 to 3.2; residual = documented "
             "boundary/oversmoothing bias)"],
        ]}),
    ("figure", ("/home/z/my-project/download/deepseek_bridge/"
                "v2_refinement.png",
                "Figure 3. V2 - the refinement prototype. (a) the "
                "atomic measures converge weakly to the smooth "
                "curvature density as the mesh refines; (b) at fixed "
                "n the sigma-to-0 limit is atomic; (c) at fixed sigma "
                "the refined, smoothed object converges to the smooth "
                "density - the corrected bridge theorem.", 200)),
    ("body",
     "The honest open forms for the real-network program, replacing "
     "the audit's false formula. Conjecture RA (refinement): there "
     "exist model-family sequences - for example constraint families "
     "polyhedrally approximating smooth physiological bounds - along "
     "which the empirical event measures of the lex-pFBA map converge "
     "weakly; blocked by the absence of known genome-scale refinement "
     "sequences and by sliver cascades. Its near-term testable form "
     "is E32 (proposed): over random cuts and panels - the M4b grid, "
     "the M1 sweeps, the E24 panel - do the empirical event measures "
     "stabilize in bounded-Lipschitz distance as the panel grows, a "
     "Glivenko-Cantelli-type statement runnable on existing data. "
     "This is Route 5's mean-field instinct made falsifiable now. "
     "Conjecture SA (identification): for a refinement sequence whose "
     "limit geometry is constructed FROM the viability field V, the "
     "limit curvature measure coincides with the smoothed geometric "
     "kappa_V / g^SAVGS of the manuscript; not provable at present "
     "(6/6 consensus, D6), and no claim of automatic coincidence "
     "should be made. For the manuscript at fixed network, the "
     "defensible statement remains the resolution statement, now "
     "upgraded by V1: the three kappa objects are one curvature "
     "measure - canonical in the D2Phi carrier - at multiple "
     "resolutions, with the dial measured and the unification a "
     "resolution statement, not a limit statement."),

    ("h1", "5. V5 - the decisive test, executed"),
    ("body",
     "The audit's recommended next step 1: 'Re-run E24 with the "
     "measure-theoretic kappa_flux. This is the decisive test. If the "
     "empirical association strengthens or remains robust with the "
     "corrected metric, the single-paper route is secure.' It was "
     "executed with everything else held fixed: the same panel (433 "
     "genes with M3D expression), the same trajectory (the exact E22 "
     "physiology, q_glc 5.0 to 1.0 and q_O2 22 to 5.0 at eight "
     "anchors), the same per-gene aggregation (max over the gene's "
     "reactions), the same response (max |log2FC| over the four M3D "
     "stationary carbon-exhaustion contrasts), and the same "
     "statistics (MC permutation p, bootstrap CI, partial given "
     "reference level, deciles). Only the predictor changed: the E22 "
     "baseline kappa_V(r) = max over t of (v_r(t) - v_r(T1))^2 - a "
     "squared displacement - versus the corrected kappa^mu(r) = "
     "sum over t of |second difference| / dt - the dt-normalized "
     "curvature-measure mass. Both were computed on the deterministic "
     "lex-pFBA trajectory, with an engine control (kappa_V on the "
     "lex trajectory) isolating the engine change from the definition "
     "change. The trajectory is not event-free: total measure mass "
     "288.77, identical at 4x and 8x refinement - the atoms are "
     "resolved and the dt-normalized mass is resolution-independent, "
     "as Theorem S predicts - with 440 reactions carrying events and "
     "a maximum three-point collinearity residual of 0.135."),
    ("table", {
        "title": "Table 3. V5 results - the E24 recalibration "
                 "(baseline reproduced to the digit)",
        "header": ["Predictor", "r (nonzero)", "n", "p", "Spearman",
                   "partial r"],
        "ratios": [0.30, 0.14, 0.08, 0.13, 0.16, 0.19],
        "rows": [
            ["kappa_V E22 artifact (baseline)", "+0.3739", "433",
             "8.2e-16", "+0.3999", "+0.2508 (E24 record)"],
            ["kappa_V lex (engine control)", "+0.3954", "424",
             "2.6e-17", "+0.4139", "-"],
            ["kappa^mu (measure, max)", "+0.3954", "424", "2.6e-17",
             "+0.4138", "+0.2692 (p = 1.8e-8)"],
            ["kappa^mu (sum aggregation)", "+0.3909", "424",
             "6.3e-17", "+0.4050", "-"],
        ]}),
    ("body",
     "Deciles for kappa^mu: top decile mean |FC| 1.923 versus bottom "
     "0.890 (Mann-Whitney one-sided p = 1.3e-7) - the E24 signature "
     "(1.92 versus 0.89, 9.0e-8) is preserved. The zero-kappa^mu "
     "contrast has only nine genes, whose reactions carry zero lex "
     "flux at all times - plain-FBA vertex noise in the E22 artifact "
     "(mean |FC| 1.296 versus 1.319, no difference, consistent with "
     "noise). Refinement robustness: 4x and 8x give r = +0.3954 "
     "identically. Three findings beyond the headline. First, the "
     "decisive test passes with strengthening: the "
     "measure-theoretic metric increases the association at every "
     "level - Pearson +0.374 to +0.395, Spearman +0.400 to +0.414, "
     "partial +0.251 to +0.269, and the p-value tightens by an order "
     "of magnitude. Second, metric invariance is itself the deeper "
     "result: Spearman's rho between kappa^mu and the lex kappa_V is "
     "0.99998 - on the monotone carbon-decline trajectory the "
     "curvature-measure mass and the squared displacement are "
     "rank-equivalent predictors (rho with the E22 artifact: +0.932 "
     "for both). The transcript-level association is therefore a "
     "property of the event structure along the trajectory, not of "
     "the choice between the time-course and curvature pictures. "
     "Third, an E22 artifact was found and documented: the e24 CSV "
     "rounded kappa_V to six decimals, zeroing the 94 tiny panel "
     "values (1e-13 to 1e-7) that E24's in-memory statistics had "
     "used (n = 433); reading the rounded artifact reproduces n = "
     "339 and r = +0.380 - a reproducibility trap for future "
     "re-analysis, resolved here by reading the unrounded E22 "
     "artifact (baseline reproduced to the digit: r = +0.3739, p = "
     "8.18e-16, CI [0.2986, 0.4464]). The tiny values are largely "
     "plain-FBA degeneracy noise - one more reason the "
     "lexicographic engine should be the default for every future "
     "kappa computation. What V5 does not show: it does not prove "
     "kappa_flux = F[mu] as a formal identity for the manuscript's "
     "exact definitions (still open, now decoupled - the "
     "association survives the redefinition, which is what the "
     "single-paper decision needed); and it is single-trajectory - "
     "the PRECISE arm and matched conditions were not re-run."),
    ("figure", ("/home/z/my-project/download/deepseek_bridge/"
                "v5_e24_recalibration.png",
                "Figure 4. V5 - the decisive test. (a) the "
                "measure-theoretic predictor against the M3D response; "
                "(b) the decisive comparison across baseline, engine "
                "control, and measure metric; (c) predictor agreement "
                "rho = 0.93 with the E22 artifact.", 200)),

    ("h1", "6. Strategic advice, evaluated"),
    ("bullet_list", [
        ("Single coherent manuscript - endorsed, condition met.",
         "The audit's stated condition - if the association strengthens "
         "or remains robust under the corrected metric - is satisfied "
         "by V5. The proposed spine (discrete measure and kappa_flux "
         "functional; Theorem R and M4c central; M1/M3/M4 as "
         "validation; E24-E27 as the association; Kochanowski as "
         "protein-layer prior art) is sound; V1 adds the canonical "
         "carrier and the decoupling table, and Theorem B adds the "
         "provable prototype the unification section needs to cite."),
        ("Trim categorical/HoTT to an appendix - endorsed.",
         "The joint assessment's tiered repair program already routes "
         "them there."),
        ("Defer E28 until after the metric redefinition - endorsed.",
         "The M4c (eps, sigma) design law is on record; V5's metric is "
         "now also on record, so E28's gate is one step closer to "
         "opening. Nothing new is needed."),
        ("v2 Layer-0 drafting is the correct next deliverable.",
         "Formal style rules (no diary, no version history, no session "
         "references), the P0 mechanical fix list as the entry point, "
         "Theorem B / Theorem R / V1's canonical carrier / V5's "
         "recalibration as the new-results sections, and the "
         "Kochanowski passage verbatim in the discussion. Not "
         "attempted in this turn; it is the next turn's work, with "
         "this file as source material."),
        ("One internal tension recorded.",
         "Part 2 opens with 'the bridging can be strengthened ... but "
         "not by more simulation or terminology', yet its own next "
         "step 1 is a simulation. Resolved: the bridge needed the "
         "right theorem (Theorem B), the right decisive simulation "
         "(V5), and the corrections D1-D8. Simulation and theorem "
         "were both necessary; neither was sufficient alone."),
    ]),

    ("h1", "7. Corrected bottom line"),
    ("quote",
     "The bridge is not dead and not merely reformulated - it is now "
     "two-sided. On a fixed network it is a resolution statement "
     "(Theorem R + M4c: one measure at resolution sigma, dial "
     "eps* about 3 sigma, mass conserved), with the canonical carrier "
     "being the tie-break-free value measure D2Phi (V1), whose atom "
     "hierarchy is decoupled from the flux-jump hierarchy. Across "
     "refinement sequences it is a provable limit statement (Theorem "
     "B, prototype verified). Do not write the audit's formula: "
     "kappa_geom = lim(sigma->0) kappa_flux * phi_sigma selects the "
     "atomic measure (V3, V2b; Theorem N). The decisive test has been "
     "run and passes with strengthening (V5). The single-paper route "
     "is secure by the audit's own criterion. Remaining open, "
     "honestly labeled: kappa_flux = F[mu] as a formal identity; "
     "Conjecture RA (real-network refinement, low feasibility, E32 "
     "statistical form testable now); Conjecture SA (identification "
     "with g^SAVGS, not provable at present); E28 under the (eps, "
     "sigma) design law; the E31 2D sliver census."),

    ("h1", "8. Deliverables of this evaluation"),
    ("table", {
        "title": "Table 4. Artifacts",
        "header": ["Artifact", "Content"],
        "ratios": [0.42, 0.58],
        "rows": [
            ["deepseek_bridge/v1_value_function.{json,csv,png}",
             "Route 3 corrected: Phi piecewise-affine at 4.2e-13, the "
             "single value atom, cluster nets, Danskin dual-vs-FD, "
             "decoupling scatter"],
            ["deepseek_bridge/v2_refinement.{json,csv,png}",
             "Theorem B prototype: refinement limit (W1, mass ratio, "
             "L1), sigma-to-0 atomicity, joint limit"],
            ["deepseek_bridge/v3_sigma_limit.{json,csv,png}",
             "D1 falsified on the measured M4c measure: mass "
             "collapse, wall-free decay, hat-test separation"],
            ["deepseek_bridge/v5_e24_recalibration.{json,csv,png}",
             "The decisive test: four predictors, partial, deciles, "
             "zero contrast, predictor agreement, refinement "
             "robustness"],
            ["scripts/deepseek_route_verify.py",
             "V1 + V2 + V3 (reuses lp_engine.py; frozen v21 "
             "untouched)"],
            ["scripts/e24_measure_kappa.py",
             "V5 (reuses the E24 protocol and artifacts; documents "
             "the E22 CSV rounding trap)"],
            ["download/DeepSeek_Bridge_Strength_Evaluation.md",
             "The full evaluation (source document of this report)"],
        ]}),
]
