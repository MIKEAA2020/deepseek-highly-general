#!/usr/bin/env python3
"""Content for the Active-Set Bridge v2 solution report (English).
Consumed by active_set_bridge_v2_report_pdf.py."""

FIG = "/home/z/my-project/download/m4"

CONTENT = [
    # ================================================== 1. executive summary
    ("h1", "1. Executive Summary"),
    ("body",
     "This report evaluates, verifies, corrects, completes, and then "
     "attempts to solve the\u00a0\u201cActive-Set Bridge Conjecture\u201d "
     "formulation deposited in <i>external audits/unifying object/"
     "deepseek formulation.txt</i> (316 lines: the conjecture with "
     "assumptions A1\u2013A5, a five-step proof sketch, three testable "
     "consequences, a status paragraph, and the model's own five-point "
     "self-critique with a revised statement). The evaluation uses "
     "three evidence classes: the mathematical structure of "
     "multi-parametric linear programming; the executed M1/M3/M3b "
     "numerical record on the deterministic lexicographic-pFBA engine "
     "(iML1515); and two new measurements, M4a and M4b, designed and "
     "executed for this report to attack the formulation's own "
     "declared missing ingredient \u2014 the scaling limit A4. The "
     "verdict is mixed in a precise way: the formulation's structural "
     "half (piecewise-affinity, event concentration, active-set "
     "substrate) is correct and already machine-verified, while its "
     "central analytic claim \u2014 an \u03b5<super>2</super>-scaled "
     "holonomy limit equal to the geometric curvature \u2014 is false "
     "in both layers in which it could be interpreted, and it is false "
     "for reasons that are now theorems, not opinions."),
    ("body",
     "The repaired formulation delivered here (Section 5) replaces the "
     "conjecture with a five-part architecture: a static curvature-"
     "measure theorem (S), an intrinsic defect theorem with a validated "
     "unfolding transport (G), a new structural lemma discovered during "
     "verification (N1,\u00a0\u201cno loose kinks\u201d), an atomicity "
     "obstruction theorem that explains exactly why the strong form "
     "cannot be proven (N), and a first-order dynamic commutator law "
     "(D) that M4a measured to slope 0.998. What survives of the "
     "original bridge is substantial: the active-set skeleton is the "
     "common carrier of every object, exactly as the six unifying-"
     "object audits converged in the joint assessment. What is "
     "abandoned is the infinitesimal \u03b5<super>2</super> pointwise "
     "identification, and its abandonment is now a proven necessity "
     "rather than a stylistic caution."),
    ("callout", ("slope 1.00, not 2",
                 "M4a measured the dynamic commutator scaling on 76 gene "
                 "pairs at six perturbation depths: 64 pairs are exactly "
                 "commutative (\u03c7 \u2261 0) and the 9 nonzero pairs "
                 "scale linearly (median slope 0.998, exact halving "
                 "ratios across five octaves). The \u03b5<super>2</super> law of "
                 "A4 is falsified in the only layer where it was "
                 "meaningful.")),
    ("callout", ("1e-14 / 1e-11",
                 "The corrected unfolding transport equals the corner-"
                 "angle defect to machine precision on synthetic "
                 "piecewise-affine maps (including a 190.6\u00b0 cone), "
                 "and composes to the exact identity on real iML1515 "
                 "interfaces away from codim-2 strata (5/5 flat "
                 "controls). The geometric machinery the conjecture "
                 "needed exists; it was attached to the wrong limit.")),
    ("body",
     "Two findings go beyond the audit task. First, the atomicity "
     "obstruction (Theorem N) converts the six-audit consensus that the "
     "strong-form unification\u00a0\u201cis not provable\u201d into a "
     "localized reason: for a fixed model the curvature of the flux "
     "graph is supported on the codim-1 and codim-2 skeletons, so any "
     "\u03b5<super>2</super>-normalized loop limit is either zero "
     "(generic points) or divergent (skeleton points), and the only "
     "sound limits are mesoscopic (defect density, an assumption on "
     "model families) or dynamic (Theorem D). Second, the edge-"
     "crossing census of the (glucose, oxygen) plane shows the skeleton "
     "is operationally dense precisely where the second-derivative mass "
     "concentrates \u2014 up to nine boundary crossings inside a single "
     "grid cell of the overflow-metabolism fan, versus exactly two in "
     "flat regions \u2014 which is the empirical face of the same "
     "obstruction."),
    # ==================================================== 2. the formulation
    ("h1", "2. The Formulation Under Evaluation"),
    ("body",
     "The file advances a single conjecture with supporting apparatus. "
     "Its setting is a genome-scale metabolic network solved as a "
     "parametric FBA family with a fixed lexicographic pFBA tie-break, "
     "making the optimal flux map v(\u03b8) unique for almost every "
     "\u03b8 and piecewise affine on a finite polyhedral decomposition "
     "of the parameter space. On the chamber complex the file defines "
     "\u201caffine-extension transition maps\u201d T<sub>ij</sub> "
     "between the affine representatives of adjacent regions, asserts "
     "the cocycle condition on triple overlaps, and assembles a "
     "\u201cdiscrete holonomy\u201d H<sub>\u03b3</sub> as the product "
     "of transitions along a closed piecewise-smooth loop \u03b3."),
    ("body",
     "Five assumptions carry the statement. A1 (nondegenerate FBA) "
     "grants uniqueness and a basis-like active set off a measure-zero "
     "set. A2 (polyhedral regularity) makes the active-set boundaries "
     "transverse hypersurfaces of a finite complex. A3 (geometric "
     "embedding) posits a smooth embedding \u03a6 of the parameter "
     "space into a Riemannian manifold B carrying a vector bundle, a "
     "connection \u2207 with curvature \u03a9<sup>\u2207</sup>, and a "
     "viability field V, from which the geometric viability-weighted "
     "curvature \u03ba<sub>geom</sub> is defined as the V-contraction "
     "of \u03a9<sup>\u2207</sup>. A4 (scaling limit) asserts that the "
     "\u03b5<super>2</super>-normalized loop holonomy converges to "
     "\u03a9<sup>\u2207</sup>(\u03a6<sub>*</sub>X, \u03a6<sub>*</sub>Y) "
     "and its norm to \u03ba<sub>geom</sub>, independently of the loop "
     "shape within a fixed tangent plane. A5 (flatness on strata) "
     "declares the discrete connection flat on each open stratum. The "
     "conjecture is then the displayed limit; the proof sketch runs "
     "piecewise affinity, jump encoding, second-order holonomy, "
     "Dirac-supported D<super>2</super>v, and a comparison step; and "
     "three consequences are claimed \u2014 second-order concentration "
     "on active-set events, double-knockout non-additivity as a "
     "rectangle holonomy, and the time-course object as integrated "
     "curvature. The status paragraph concedes that only the scaling "
     "limit A4 is missing."),
    ("body",
     "The file's second half is a self-critique proposing five fixes: "
     "replace the infinite-dimensional affine-map holonomy by a "
     "finite-dimensional tangent-space transport P<sub>ij</sub>; "
     "construct the connection explicitly from KKT basis exchanges "
     "(rank-one updates); restrict the limit to regular crossing "
     "points or restate it distributionally; make the parallel "
     "transport precise as an orthogonal projection; and replace the "
     "holonomy estimate by an exact second-order expansion "
     "H<sub>\u03b5</sub> \u2212 I = \u0394<sub>e1</sub>\u0394"
     "<sub>e2</sub>\u03b5<super>2</super> + O(\u03b5<super>3</super>). "
     "A revised compact statement incorporates these. Our audit "
     "confirms the instincts behind all five fixes while finding "
     "specific technical errors in three of them (Section 4), and it "
     "finds the claimed empirical support overstated in one place "
     "(C5) \u2014 the file asserts that M1 and M3\u00a0\u201cconfirm the "
     "first two consequences to numerical precision,\u201d which is "
     "true for consequence 1 and contradicted for consequence 2."),
    # ============================================ 3. verification vs record
    ("h1", "3. Verification Against the Executed Record"),
    ("body",
     "Every checkable claim of the formulation was re-verified against "
     "the M1/M3/M3b artifacts (commit lineage 2fe264b, f9f8634, "
     "6cdd563) rather than against the summaries. The record is "
     "consistent with the formulation's structural claims: the 12 "
     "parametric sweeps of M1 measured second-order response mass on "
     "material active-set events at 0.99999996 (glucose sweep), "
     "0.99999946 (oxygen sweep), and 0.934\u20131.0 across the eight "
     "gene knockdowns, with piecewise-affine segment residuals at or "
     "below 8 \u00d7 10<super>-14</super> relative and two negative "
     "controls behaving as a flat map must (the unused-pathway "
     "knockdown kd_aceA produced zero events and D2 \u2261 0; the "
     "iJO1366 glucose replication stayed within a single critical "
     "region with D2 at the 10<super>-11</super> noise floor). The 2,779 "
     "double knockouts of M3 support the substrate claim: rerouting "
     "epistasis tracks active-set footprint overlap with Spearman "
     "\u03c1 = 0.865 on the dR mask (p \u2248 0), all 40 synthetic "
     "lethals are isozyme redundancies, and growth epistasis "
     "anticorrelates with flux epistasis at \u03c1 = \u22120.705."),
    ("table", {
        "title": "Table 1. Formulation claims against the executed record.",
        "header": ["Formulation element", "Verdict", "Evidence"],
        "ratios": [0.42, 0.16, 0.42],
        "rows": [
            ["v(\u03b8) piecewise affine on a finite complex (A1/A2)",
             "Verified",
             "M1: affine residuals \u2264 8e-14 relative on 12 sweeps; "
             "M4b Jacobians exact within chambers (affine-consistency "
             "test)"],
            ["v continuous across interfaces",
             "Verified",
             "M1 D1 kinks, not jumps; M4b continuity diagnostics "
             "consistent with kink slopes; no tears at analyzed loci"],
            ["D<super>2</super>v a measure on active-set interfaces",
             "Verified",
             "M1 D2 mass 0.934\u20131.0; M4b 1D cut through a codim-2 "
             "region: 100.0000000% on 11 events"],
            ["Consequence 1 (second-order concentration)",
             "Confirmed",
             "M1 headline result, both models, two controls"],
            ["Consequence 2: \u03b5<sub>ij</sub> = rectangle holonomy",
             "Contradicted",
             "M3b: \u03c7 vs |\u03b5| Spearman \u22120.347 full panel "
             "(p = 6.8e-6), \u22120.07 within non-SL (p = 0.43): the "
             "optimum non-additivity and the transient non-commutativity "
             "are independent"],
            ["Consequence 3: \u03ba\u2033 = curvature measure",
             "Imprecise",
             "Missing smooth term 2||v\u0307||<super>2</super>; pointwise equality "
             "should be an integral identity (Theorem S(iv))"],
            ["The status-paragraph confirmation claim (M1 and M3\u00a0\u201cconfirm consequences 1\u20132 to numerical precision\u201d)",
             "Overstated",
             "True for consequence 1 only (C5)"],
            ["Cocycle of T<sub>ij</sub> on overlaps",
             "True, and fatal",
             "A globally consistent affine representative system forces "
             "H<sub>\u03b3</sub> = I exactly (C1/C6)"],
            ["A4 \u03b5<super>2</super> scaling limit",
             "Falsified",
             "M4a: slope 0.998 on the nonzero stratum; Theorem N for "
             "the static layer"],
        ],
        "note": "Record: m1_summary.json, m3_summary.json, m4a_summary."
                "json, m4b_summary.json (all under download/m1_m3/ and "
                "download/m4/).",
    }),
    ("body",
     "One verification deserves emphasis because it changes the "
     "interpretation of M3b. The closed-loop non-return measured in M3b "
     "(66.25% of genotype loops return to the wild-type genotype but "
     "not to the initial state, median displacement 109 L1 units) was "
     "described there as a holonomy. The release-identity check run in "
     "M4a (6/6 pairs, bit-exact) shows that every relaxation projection "
     "is the identity \u2014 the state after a loop fails to return "
     "because the greedy L1-MOMA dynamics never climbs back once "
     "displaced, not because a connection rotates the state around a "
     "plaquette. The M3b loop statistic is irreversibility; the genuine "
     "non-commutativity is the open-path commutator \u03c7, and it is "
     "\u03c7 that M4a scales. This distinction propagates into the "
     "repaired Theorem D."),
    # ================================================== 4. mathematical audit
    ("h1", "4. Mathematical Audit"),
    ("h2", "4.1 C1 \u2014 The central object is trivially flat"),
    ("body",
     "The affine-extension holonomy H<sub>\u03b3</sub> is exactly the "
     "identity for every closed loop, because v is a single-valued "
     "continuous function. The chamber representatives of a common "
     "region agree on shared interfaces (this is the file's own "
     "cocycle claim, verified), so composing transition maps around any "
     "loop telescopes back to the starting representative. The "
     "conjecture's central display therefore evaluates to 0 = "
     "\u03a9<sup>\u2207</sup> for the static map. This is not a "
     "normalization defect that a better limit could repair: single-"
     "valuedness forbids any holonomy on the function's own "
     "representatives. The nontrivial static curvature is the "
     "distributional Jacobian-jump measure on codim-1 interfaces \u2014 "
     "the object M1 measured \u2014 together with the defect measure on "
     "codim-2 strata (Theorem G). Any correct bridge must carry these "
     "two measures, not a loop limit of affine maps."),
    ("h2", "4.2 C2 \u2014 The \u03b5<super>2</super> law fails in both layers"),
    ("body",
     "In the static layer the law cannot even be posed (C1). In the "
     "dynamic layer \u2014 the sequential L1-MOMA adjustment, the only "
     "path-dependent object in the executed program \u2014 M4a measured "
     "the commutator \u03c7(\u03b5) under a flux-relative scaled "
     "knockdown family in which \u03b5 = 1 is the M3 full knockout and "
     "\u03b5 = 0 is the wild-type operating point. The measured law is "
     "\u03c7(\u03b5) = c\u00b7\u03b5 + O(\u03b5<super>2</super>) on the "
     "non-decoupled stratum (Section 6). The mechanism is structural: "
     "each knockout adds an O(1) face to the binding set and thereby "
     "changes the tangent cone of the feasible set by an O(1) jump, and "
     "the second adjustment step inherits a different cone depending on "
     "the order, so the order mismatch accumulates at first order. The "
     "\u03b5<super>2</super> commutator regime would require the two adjustment "
     "maps to share a common linear part at the operating point; the "
     "data exclude this at every sampled scale. A4 is thus resolved "
     "negatively in the only place it was meaningful, and the honest "
     "replacement is Theorem D's first-order law \u2014 which is, "
     "notably, a new falsifiable prediction for graded perturbation "
     "experiments."),
    ("h2", "4.3 C3 \u2014 The proposed transport is not a connection"),
    ("body",
     "The self-critique's finite-dimensional repair transports tangent "
     "vectors by orthogonal projection from F<sub>i</sub> to "
     "F<sub>j</sub>. Projections are not invertible \u2014 "
     "P<sub>ji</sub>P<sub>ij</sub> \u2260 I whenever the subspaces "
     "differ \u2014 so the transition system violates the groupoid "
     "inverse axiom, holonomy is ill-defined, and back-tracking does "
     "not cancel. The correct object is the minimal-rotation "
     "(unfolding, polar) map: the rotation about the shared edge that "
     "carries one face's tangent plane onto the other's. It is an "
     "invertible isometry, fixes the common edge exactly, reduces to "
     "the identity in the coplanar limit, and makes curvature "
     "concentrate on the codim-2 skeleton. This report validated that "
     "transport in two independent ways: on synthetic piecewise-affine "
     "maps, where the loop composition equals the corner-angle defect "
     "to 10<super>-14</super> including a 190.6\u00b0 cone, and on real "
     "iML1515 interfaces, where crossing one interface twice composes "
     "to the identity at 10<super>-11</super> with axis and angle "
     "constant along the interface (Section 7)."),
    ("h2", "4.4 C4 \u2014 A3 is unfalsifiable as stated"),
    ("body",
     "A3 merely assumes the existence of an embedding \u03a6, a "
     "connection, and a viability field. Under that assumption nothing "
     "can be proven or refuted \u2014 any map embeds into any geometry "
     "trivially (a constant embedding already forces \u03a9 = 0), and "
     "the conjecture's right-hand side is unconstrained. The repair is "
     "constructive: take the graph map G(\u03b8) = (\u03b8, v(\u03b8)) "
     "with the induced Euclidean metric as the Riemannian object, and "
     "define \u03ba<sub>geom</sub> as the viability-weighted discrete "
     "Gauss curvature (angle defect) of this graph. The embedding, the "
     "metric, and the connection are then fixed by the FBA data itself, "
     "the static bridge becomes a theorem (Theorem G), and the only "
     "remaining identification \u2014 with the manuscript's continuum "
     "objects \u2014 is coarse-grained and empirical, which is exactly "
     "what the E28 item already tracks. This also matches the joint "
     "assessment's Layer-1 adjudication: opus's mixed difference as the "
     "combinatorial definition, with the geometric thread organized "
     "smoothly rather than assumed existentially."),
    ("h2", "4.5 C5 \u2014 The claimed confirmations are overstated"),
    ("body",
     "The file's status paragraph asserts that M1 and M3 confirm the "
     "first two consequences\u00a0\u201cto numerical precision.\u201d The "
     "record supports half of that sentence. Consequence 1 is confirmed "
     "outright. Consequence 2's central identity \u2014 that the "
     "epistasis \u03b5<sub>ij</sub> equals, in the small-perturbation "
     "limit, the holonomy of the perturbation rectangle \u2014 is "
     "contradicted: M3b measured both statistics on the same 160-pair "
     "panel and found no positive association (full-panel Spearman "
     "\u22120.347 driven by the synthetic-lethal structure; within "
     "non-lethal pairs \u22120.07, p = 0.43). What M3 actually "
     "established is different and stronger in its own way: "
     "non-additivity aligns with active-set footprint overlap "
     "(\u03c1 = 0.865). The repaired reading keeps both facts: the "
     "optimum-level non-additivity and the transient-level "
     "non-commutativity are distinct signatures carried by the same "
     "skeleton, and the bridge must transport them separately rather "
     "than identify them."),
    ("h2", "4.6 C6 and the additional corrections"),
    ("body",
     "C6: A5 (flatness on strata) is not merely compatible with the "
     "conjecture \u2014 it is the reason the conjecture's conclusion "
     "cannot follow. A globally consistent representative system is "
     "exactly a flat connection; only transports on objects that are "
     "not single-valued (tangent frames across kinked folds, dynamic "
     "states under greedy adjustment) can carry holonomy, and then "
     "only as O(1) defects at codim-2 strata. Additional corrections: "
     "A1 is achievable but non-trivial \u2014 the engine's own "
     "construction history is the existence proof, since vertex "
     "degeneracy in the parsimony stage (sum|v| ties to 13 digits with "
     "0.69-magnitude flux flips between warm starts) had to be broken "
     "by a seeded third-stage tie-break; on measure-zero strata the "
     "deterministic selection may tear, which the analysis must "
     "tolerate (none were found at the analyzed loci). The rank-one "
     "update claim is correct within a stage under nondegeneracy, and "
     "the three-stage lexicographic structure makes the connection a "
     "tower \u2014 matching the factored curvature datum of the joint "
     "assessment's Layer 1. The proof-sketch step\u00a0\u201cholonomy = "
     "integral of the second-order measure\u201d is replaced by the "
     "true structure equations: the codim-1 jump measure and the "
     "codim-2 defect measure are linked by the unfolding composition "
     "(the incident dihedral kinks determine the vertex defect)."),
    # ============================================== 5. repaired formulation
    ("h1", "5. The Repaired Formulation (Active-Set Bridge v2)"),
    ("body",
     "Setting: a compact polyhedral parameter space \u0398 "
     "environmental bounds and/or genetic capacities, the optimal flux "
     "map v of the genome-scale LP under the fixed three-stage "
     "lexicographic tie-break, its chamber complex C with codim-1 "
     "skeleton C<super>(p\u22121)</super> and codim-2 skeleton "
     "C<super>(p\u22122)</super>. The full statement, with proofs and "
     "the status table, is preserved as the standalone document "
     "download/Active_Set_Bridge_v2.md for the manuscript pipeline; "
     "the five components are summarized here with their verification "
     "status."),
    ("quote",
     "Theorem S (static curvature measure). v is continuous and affine "
     "per chamber; D<super>2</super>v is a matrix-valued measure on "
     "C<super>(p\u22121)</super> with interface density "
     "(M<sub>j</sub> \u2212 M<sub>i</sub>) \u2297 n<sub>ij</sub>; along "
     "any piecewise-C<super>1</super> path the acceleration of v is a sum of "
     "velocity-jump Diracs at events; the squared-displacement time-"
     "course object decomposes as a piecewise-constant smooth term "
     "plus a signed event measure (an integral identity, not a "
     "pointwise one); closed-loop state holonomy is exactly trivial."),
    ("body",
     "Proof route: multi-parametric LP chamber theory (Gal\u2013"
     "Nedema; Bemporad\u2013Morari\u2013Dua\u2013Pistikopoulos), "
     "Berge continuity of the singleton solution map, and the "
     "distributional chain rule. Machine verification: M1's twelve "
     "sweeps (D2 mass 0.934\u20131.0, affine residuals \u2264 8 \u00d7 "
     "10<super>-14</super>) and the M4b one-dimensional cut through a "
     "codim-2 region (eleven events carrying 100.0000000% of the "
     "second-derivative mass). Theorem S is the repaired container for "
     "everything the formulation said about second-order response "
     "concentration, and its part (iv) is the precise version of "
     "consequence 3 that the E24\u2013E27 objects can actually be "
     "compared against."),
    ("quote",
     "Theorem G (intrinsic defect \u2014 the constructed \u03ba"
     "<sub>geom</sub>). For p = 2 the graph G(\u03b8) = (\u03b8, "
     "v(\u03b8)) is a piecewise-flat surface in R<super>m+2</super>; "
     "with the unfolding transport P<sub>ij</sub> (minimal rotation "
     "about the shared edge), loops crossing interfaces in canceling "
     "pairs compose to the identity exactly, and at a transverse "
     "four-chamber crossing the small-loop holonomy is the rotation "
     "by the corner-angle defect K(\u03b8<sub>0</sub>) = 2\u03c0 \u2212 "
     "\u03a3\u03b1<sub>q</sub> \u2014 an O(1), exactly scale-independent "
     "quantity. \u03ba<sub>geom</sub> := the viability-weighted defect "
     "and jump measures."),
    ("body",
     "Proof route: discrete Gauss\u2013Bonnet / Regge unfolding. "
     "Verification: the synthetic unit tests of Section 7.1 (transport "
     "= \u2212defect to 10<super>-14</super> on flat, conical, and "
     "generic four-sector maps) and the iML1515 flat controls "
     "(identity at \u2264 3.4 \u00d7 10<super>-11</super>; interface "
     "axis and angle constant to 10<super>-11</super>). The defects at "
     "the three analyzable fan vertices are scale-invariant to four "
     "decimals (\u22127.1469\u00b0, \u221223.9087\u00b0, "
     "+0.0104\u00b0 at both probe scales), with the face-consistency "
     "diagnostics flagging \u2014 as designed \u2014 that the wedge-fan "
     "there is below the operational resolution (Theorem N). Theorem G "
     "is the repaired A3: the geometry is constructed, not assumed."),
    ("quote",
     "Lemma N1 (no loose kinks). On a continuous piecewise-affine map, "
     "a codim-1 stratum with nonzero Jacobian jump cannot T-terminate "
     "in the interior of another stratum: the three tangential-"
     "derivative identities around a T-junction force the terminating "
     "stratum to be Jacobian-flat. Mask-type T-junctions have defect "
     "exactly zero and identity holonomy; kinked strata must cross."),
    ("body",
     "This lemma was discovered during the verification itself, when "
     "the\u00a0\u201cthree-boundary-point\u201d cells of the (glucose, "
     "oxygen) plane refused the four-sector model. Its empirical "
     "signature is strong: three of the five flat controls sit on "
     "interfaces whose dihedral kink is exactly 0.0000\u00b0 \u2014 "
     "operational-signature events with no flux kink (support/"
     "materiality crossings) \u2014 and the census of Section 7.4 "
     "resolves the corner cells into nested thin slivers whose visible "
     "terminators are precisely such mask lines. The lemma sharpens "
     "the operational-active-set caveat inherited from M1: the "
     "signature method over-counts geometric events, and N1 says "
     "exactly which over-counts are harmless."),
    ("quote",
     "Theorem N (atomicity obstruction). For a fixed model the "
     "intrinsic curvature is supported on the codim-1 and codim-2 "
     "skeletons; hence the \u03b5<super>2</super>-normalized loop limit is 0 at "
     "generic points and divergent on C<super>(p\u22122)</super>. The "
     "only sound scaling limits are mesoscopic (defect density \u2014 "
     "a regularity property of a model sequence, not a theorem of LP) "
     "and dynamic (Theorem D). In the biologically relevant region the "
     "skeleton is operationally dense, so even the mesoscopic limit is "
     "a coarse-graining statement there."),
    ("body",
     "Theorem N is the formal resolution of the formulation's declared "
     "\u201cmissing ingredient.\u201d It converts the joint "
     "assessment's six-audit consensus \u2014 that the strong-form "
     "unification is not provable \u2014 into a localized mechanism: "
     "what would be needed is a sequence of models whose chamber "
     "diameter tends to zero while per-vertex defects shrink as "
     "O(diameter<super>2</super>), which is a property one may assume and test "
     "but cannot derive from LP structure. The empirical face of N is "
     "the edge-crossing census (Section 7.4): nine to ten chamber "
     "boundaries inside single grid cells of the overflow fan, against "
     "exactly two in flat regions \u2014 the skeleton is dense exactly "
     "where the D2 mass concentrates."),
    ("quote",
     "Theorem D (dynamic layer). Under the flux-relative scaled "
     "knockdown family the sequential L1-MOMA commutator obeys "
     "\u03c7(\u03b5) = \u03b5\u2016\u0394<sub>1</sub>\u2016 + "
     "O(\u03b5<super>2</super>) with \u0394<sub>1</sub> the first-order tangent-cone "
     "mismatch, and \u03c7 \u2261 0 exactly on the decoupled stratum; "
     "release projections are exact identities, so closed-loop "
     "non-return is irreversibility, not connection holonomy."),
    ("body",
     "Theorem D is measured, not merely stated: 76 pairs at six depths "
     "(Section 6). Its content is the honest replacement of the "
     "\u03b5<super>2</super> curvature law in the layer where path dependence "
     "actually lives, and it carries a testable laboratory prediction "
     "\u2014 the order-sensitivity of graded double knockdowns should "
     "scale linearly with knockdown depth \u2014 which is new science "
     "produced by trying to solve the formulation rather than by "
     "accepting it."),
    # ======================================================== 6. M4a
    ("h1", "6. M4a: The Scaling Test of the Dynamic Layer"),
    ("h2", "6.1 Design"),
    ("body",
     "A4's limit needed a perturbation family that reaches the "
     "executed M3 knockouts at full depth while remaining differentiable "
     "at the wild-type point. The flux-relative convention does both: "
     "for every reaction k of the gene set, the bound in the direction "
     "of the wild-type flux v<sub>wt,k</sub> is tightened to "
     "(1\u2212\u03b5)v<sub>wt,k</sub>, mirrored for negative fluxes and "
     "scaled homothetically for zero-flux reactions, so that "
     "\u03b5 = 0 is the wild-type operating point (the MOMA projection "
     "is the identity), \u03b5 = 1 is exactly the M3 full knockout, and "
     "every nonzero-flux reaction binds at every \u03b5 > 0 \u2014 no "
     "capacity-slack threshold. For each of 76 pairs (30 top-|"
     "\u03b5|, 30 random, 10 synthetic-lethal, 6 archetypes including "
     "zwf+gnd, pfkA+pfkB, pgi+zwf, tktA+tktB, acnA+acnB) and each depth "
     "\u03b5 \u2208 {1, 1/2, 1/4, 1/8, 1/16, 1/32}, the two sequential "
     "adjustment paths were solved and the open-path commutator \u03c7"
     "(\u03b5) = \u2016s<sup>i\u2192j</sup> \u2212 s<sup>j\u2192i</sup>"
     "\u2016<sub>1</sub> recorded together with the single-response magnitudes "
     "as a linearity control. 1,856 deterministic L1-MOMA solves on the "
     "M1/M3 engine; runtime 59 seconds."),
    ("h2", "6.2 Results"),
    ("table", {
        "title": "Table 2. M4a scaling census (76 pairs, six depths).",
        "header": ["Class", "Pairs", "Reading"],
        "ratios": [0.2, 0.12, 0.68],
        "rows": [
            ["\u03c7 \u2261 0 (exactly commutative)", "64",
             "The dominant stratum: the two adjustments do not interact "
             "at any depth; order-independence is exact, not "
             "approximate"],
            ["slope \u2248 1 (0.976\u20131.244, median 0.998)", "9",
             "First-order non-commutativity: sdhD+nuoG halves exactly "
             "101.29 \u2192 50.56 \u2192 25.29 \u2192 12.66 \u2192 6.34 "
             "\u2192 3.19; atpD+nuoJ reproduces the M3b maximum 226.48 "
             "at \u03b5 = 1 and halves thereafter"],
            ["noise-floor / insufficient", "3",
             "\u03c7 \u2248 1\u20133 units with chamber flips at "
             "alternative-optima noise; excluded from slope fits"],
            ["single-response control (all pairs)", "73",
             "Median slope 1.01 \u2014 the perturbation itself responds "
             "linearly, isolating the commutator as the object of "
             "interest"],
            ["release-identity checks", "6/6",
             "Relaxation projections return the state bit-exactly \u2014 "
             "M3b's closed-loop non-return is irreversibility"],
        ],
        "note": "Source: download/m4/m4a_scaling.csv, m4a_pairs.csv, "
                "m4a_summary.json.",
    }),
    ("figure", (FIG + "/fig_m4a_scaling.png",
                "Figure 1. M4a. (top) \u03c7(\u03b5) on log\u2013log "
                "axes for the nonzero pairs with the slope-1 law "
                "(measured) and the slope-2 law (conjectured A4); "
                "(middle) slope histograms for \u03c7 and the "
                "single-response control; (bottom) class census.",
                300)),
    ("body",
     "The verdict against A4 is unambiguous. Where the commutator is "
     "nonzero it scales linearly \u2014 the fitted slopes cluster at "
     "1.00 with halving ratios exact to five octaves, and the two "
     "pairs whose \u03b5 = 1 point sits in a different chamber (gapA+"
     "atpC, zwf+gnd) show a clean break at full depth and pure linear "
     "behavior below it, as the piecewise structure of the family "
     "predicts. The slope-2 regime would appear as \u03c7 collapsing "
     "toward zero faster than the perturbation; it does not occur at "
     "any sampled scale. The 84% exactly-commutative stratum is itself "
     "informative: the L1 geometry of the two adjustment cones "
     "commutes when the perturbed reaction sets do not interact, which "
     "is the generic situation at small depth \u2014 order effects are "
     "a sparse, targeted phenomenon, not a diffuse curvature field. "
     "This is the same qualitative lesson as M3b's 19.4% active "
     "fraction, now resolved in \u03b5."),
    # ======================================================== 7. M4b
    ("h1", "7. M4b: The Two-Parameter Static Geometry"),
    ("h2", "7.1 Machinery validation on synthetic maps"),
    ("body",
     "Before touching the model, the corrected defect\u2013transport "
     "machinery was validated on synthetic piecewise-affine maps with "
     "known geometry: the flat case (four identical quadrant "
     "Jacobians), polyhedral cones (deficits up to 190.6\u00b0), and "
     "generic four-sector maps with the continuity constraints imposed "
     "exactly. In every case the unfolding-transport composition "
     "around the vertex returns the initial tangent frame rotated by "
     "the corner-angle defect to 10<super>-14</super> (net + defect = "
     "0 modulo 2\u03c0), the frame remains in the starting plane to "
     "10<super>-16</super>, and the shared-edge identities hold to "
     "machine zero. One implementation error was caught by this test "
     "itself \u2014 an early version transported the negated "
     "transverse direction, which the flat case exposed immediately. "
     "The machinery that then runs on real FBA data is therefore "
     "proven, not presumed."),
    ("h2", "7.2 The (glucose, oxygen) plane"),
    ("body",
     "A 34 \u00d7 34 grid over glucose 1.5\u201310 and oxygen "
     "1\u201322 (1,156 lexicographic solves, 2,122 total with "
     "refinement) resolves 24 operational chambers. The signature map "
     "shows the classical overflow-metabolism portrait: a fan of thin "
     "wedge chambers radiating from the low-nutrient corner, wide "
     "chambers above, a strong horizontal boundary near oxygen 11.2, "
     "and mask-type boundaries (zero dihedral) interleaved with "
     "kinked ones. Three vertices in the fan admit a full four-sector "
     "analysis; their defects are scale-invariant to four decimals "
     "(\u22127.1469\u00b0 and \u221223.9087\u00b0 at both \u03b4 and "
     "\u03b4/2; +0.0104\u00b0) \u2014 the O(1), size-independent "
     "behavior Theorem G predicts \u2014 while their face-consistency "
     "diagnostics self-flag the under-resolution of the nested slivers "
     "(shared-edge residuals of order 0.2\u20133.7 on three of four "
     "edges, one edge exact at 10<super>-10</super>). The state-"
     "holonomy null is trivially exact: v is a function of its bounds, "
     "so every closed loop in the plane returns the identical flux "
     "vector \u2014 the original conjecture's H<sub>\u03b3</sub> = I."),
    ("figure", (FIG + "/fig_m4b_regions.png",
                "Figure 2. M4b. Operational active-set signature map "
                "(24 chambers) and growth surface over the (glucose, "
                "oxygen) plane; stars mark the analyzed fan vertices.",
                235)),
    ("h2", "7.3 Flat controls and the mask/kink dichotomy"),
    ("body",
     "Five control cells straddling single interfaces were analyzed "
     "with the full transport machinery: crossing the interface and "
     "crossing back composes to the identity at 10<super>-11</super> "
     "to 10<super>-23</super>, with the transport axis and angle "
     "constant along the interface to 10<super>-11</super> \u2014 "
     "flatness off the codim-2 skeleton is exact, not approximate. "
     "The controls also expose the dichotomy that Lemma N1 "
     "systematizes: two interfaces carry O(1) dihedral kinks "
     "(50.07\u00b0, the same value on both sides of the plane \u2014 "
     "the overflow fold), while three carry exactly 0.0000\u00b0 \u2014 "
     "operational-signature events with no flux kink, the mask type. "
     "The M1 event census (events were overwhelmingly support-only) "
     "and the M4b census are consistent: the operational active set "
     "is a strict superset of the geometric event set, and the "
     "difference is precisely the Jacobian-flat strata."),
    ("figure", (FIG + "/fig_m4b_geometry.png",
                "Figure 3. M4b. (a) the 1D cut through a codim-2 "
                "region: eleven events carry 100.0000000% of the D2 "
                "mass; (b) flat-control identity residuals; (c) "
                "interface dihedral kinks including the 0.0000\u00b0 "
                "mask type; (d) edge-crossing census \u2014 the "
                "skeleton is dense exactly where curvature "
                "concentrates.",
                300)),
    ("h2", "7.4 The wedge-fan anatomy and the edge-crossing census"),
    ("body",
     "The cells that defeated the four-sector analysis were not noise. "
     "A full multi-crossing census (every edge of every structurally "
     "rich cell resolved by scanning plus bisection) shows that the "
     "low-nutrient corner is a nested wedge-fan: thin sliver chambers "
     "\u2014 one signature separating the wide ones on a single edge "
     "\u2014 stacked so that a single grid edge can contain up to four "
     "boundary crossings and a single cell up to ten, against exactly "
     "two in flat regions. The visible terminators inside this fan are "
     "mask lines (Lemma N1's flat strata), while the kinked fan lines "
     "either cross the horizontal boundaries in true four-chamber "
     "vertices or reflect. This anatomy is the empirical content of "
     "the atomicity obstruction: the codim-2 skeleton is not an "
     "edge-case garnish \u2014 in the region where the second-"
     "derivative mass actually concentrates, it is dense at the "
     "operational scale, and any smooth \u03b5<super>2</super> limit would have "
     "to average over it. The one-dimensional cut through such a "
     "region records eleven events carrying 100.0000000% of the "
     "second-derivative mass \u2014 M1's law reproduced at the vertex "
     "scale."),
    ("body",
     "What M4b deliberately does not claim: fully resolved defect "
     "values at the fan vertices. The three computed defects are "
     "reported with their self-flagged diagnostics as scale-invariant "
     "estimates at under-resolved loci. Resolving the nested wedges "
     "requires an adaptive chamber-refinement study at tighter "
     "materiality tolerance, which is recorded as the open item E31 "
     "in Section 8 \u2014 the honest boundary of what this report's "
     "machinery could measure at the fixed operational signature."),
    # ================================================== 8. solved and open
    ("h1", "8. What Is Solved and What Remains Open"),
    ("h2", "8.1 Solved"),
    ("bullet_list", [
        ("The static bridge is now a theorem pair, not a conjecture:",
         "Theorem S (curvature measures on the skeletons, the "
         "time-course integral identity) and Theorem G (intrinsic "
         "defect with a machine-validated unfolding transport) are "
         "proven and verified; \u03ba<sub>geom</sub> is constructed "
         "from FBA data, retiring the unfalsifiable A3."),
        ("A4 is resolved \u2014 negatively and constructively:",
         "Theorem N proves the \u03b5<super>2</super> limit cannot exist for a "
         "fixed model (zero at generic points, divergent on the "
         "skeleton), Theorem D measures the dynamic layer's true "
         "first-order law, and the atomicity obstruction localizes "
         "exactly why the strong-form unification fails."),
        ("A new structural lemma (N1, no loose kinks):",
         "T-terminating strata must be Jacobian-flat; mask-type events "
         "carry zero defect and identity holonomy; empirically "
         "confirmed by the 0.0000\u00b0 kink interfaces and the "
         "sliver-terminator anatomy."),
        ("The transport the conjecture needed exists and is exact:",
         "invertible, shared-edge-fixing, validated to 10<super>-14"
         "</super> synthetically and 10<super>-11</super> on iML1515 \u2014 "
         "the file's projection-based repair is corrected to the "
         "unfolding map."),
        ("The M3b loop statistic is re-interpreted:",
         "release-identity (6/6 bit-exact) proves the closed-loop "
         "non-return is greedy-dynamics irreversibility, cleanly "
         "separating it from the genuine commutator \u03c7."),
    ]),
    ("h2", "8.2 Open"),
    ("bullet_list", [
        ("E28 (unchanged, now sharper):",
         "second differences on measured time courses \u2014 the "
         "empirical identification of the integrated event measure of "
         "Theorem S(iv) with the E24\u2013E27 objects; the repaired "
         "statement finally specifies the exact functional form to "
         "test."),
        ("The strong-form pointwise identification:",
         "\u03ba<sub>geom</sub> = \u03ba<sub>V</sub> remains out of "
         "reach, now for a precise reason (atomicity); the defensible "
         "target is the coarse-grained, mesoscopic identification."),
        ("Model-family regularity:",
         "whether any biologically meaningful family of models has "
         "defect densities with an asymptotic limit \u2014 the "
         "assumption any mesoscopic theorem would need; testable in "
         "silico across model scales (iML1515 \u2192 iJO1366 \u2192 "
         "smaller)."),
        ("E31 (new):",
         "adaptive resolution of the nested wedge-fan vertices at "
         "tighter materiality tolerance \u2014 the census localizes "
         "where and why the current signature resolution saturates."),
        ("Laboratory test of Theorem D:",
         "order-sensitivity of graded double knockdowns scaling "
         "linearly with depth \u2014 a CRISPRi-graded design could "
         "falsify or confirm the first-order law in vivo."),
    ]),
    ("h2", "8.3 Consequences for the manuscript program"),
    ("body",
     "Nothing in this report touches the frozen v21 manuscript, and "
     "the standing disciplines are unchanged: all integration happens "
     "in the future journal_manuscript_v2+ documents. For that "
     "integration, the repaired formulation slots into the joint "
     "assessment's architecture with minimal disturbance: Layer 0 "
     "(notation protocol) should adopt the mixed-difference anchor "
     "together with the skeleton-measure notation of Theorems S/G; "
     "Layer 1 (factored curvature datum) gains the defect measure as "
     "the geometric instantiation next to opus's mixed difference as "
     "the combinatorial definition; Layer 2 already contains T-energy "
     "and T-bound, to which Theorems S, G, N1, and N are natural "
     "additions \u2014 all four provable now; Layer 3 (measurements) "
     "extends from M1\u2013M3 to M4a/M4b, with E29/E30 (executed) and "
     "E28/E31 (open) tracked as before. The Kochanowski et al. 2021 "
     "positioning is unaffected: the complementary-prior-work framing "
     "and the staged verbatim passage belong to the v2 Layer-0 pass "
     "exactly as recorded in the M1/M3 report, and nothing in the "
     "repaired bridge changes the transcript-versus-protein-layer "
     "story that passage tells. The one-word discipline that v2 "
     "should adopt from this audit: never write\u00a0\u201cholonomy\u201d "
     "where the object is a measure, an irreversibility, or a "
     "first-order commutator \u2014 each of the three κ threads now "
     "has its own correct name."),
    # ================================================== 9. deliverables
    ("h1", "9. Deliverables and Reproduction Map"),
    ("table", {
        "title": "Table 3. Deliverables produced by this evaluation.",
        "header": ["Artifact", "Content"],
        "ratios": [0.44, 0.56],
        "rows": [
            ["download/Active_Set_Bridge_v2.md",
             "The repaired and completed formulation: verified strengths, "
             "corrections C1\u2013C6, Theorems S/G/N1/N/D with proofs, "
             "the status table of every original element, and the "
             "honest residue \u2014 staged as v2 source material"],
            ["download/m4/m4a_scaling.csv, m4a_pairs.csv, "
             "m4a_summary.json",
             "The 76-pair \u00d7 6-depth scaling record: \u03c7(\u03b5), "
             "single-response controls, slope fits, class census, "
             "release-identity checks"],
            ["download/m4/m4b_grid.npz, m4b_summary.json, "
             "m4b_edge_census.json",
             "The 34\u00d734 signature/growth grid; the vertex analyses "
             "(defects, kinks, transport, diagnostics); the flat "
             "controls; the 1D cut; the 11-cell multi-crossing census"],
            ["download/m4/fig_m4a_scaling.png, fig_m4b_regions.png, "
             "fig_m4b_geometry.png",
             "The three report figures (also used by the m4 figure "
             "script)"],
            ["scripts/m4a_scaling.py, m4b_2d_geometry.py, "
             "m4b_machinery_test.py, m4b_edge_census.py, "
             "m4_figures.py",
             "The complete reproduction path on the shared "
             "deterministic engine (lp_engine.py, seeds 20240901 / "
             "20260901); machinery_test is the synthetic validation "
             "suite"],
            ["scripts/active_set_bridge_v2_report_content.py, "
             "active_set_bridge_v2_report_pdf.py",
             "This report's source (pdf skill report route)"],
        ],
        "note": "Determinism: all solves use the 3-stage lexicographic "
                "pFBA engine with the fixed seeded tie-break; the "
                "synthetic validation suite re-runs in seconds.",
    }),
    ("body",
     "Reproduction order: m4b_machinery_test.py (validates the "
     "machinery), m4a_scaling.py (59 s), m4b_2d_geometry.py "
     "(grid pass 196 s cached thereafter, full analysis 363 s), "
     "m4b_edge_census.py, m4_figures.py, then this report's builder. "
     "All artifacts live under download/m4/ and download/; the "
     "repository state after this session carries the new experiments "
     "and both formulation documents, with the v21 manuscript "
     "untouched throughout, per the standing version discipline. "
     "Everything is committed and pushed to the repository remote "
     "under the standing PAT-based workflow."),
]
