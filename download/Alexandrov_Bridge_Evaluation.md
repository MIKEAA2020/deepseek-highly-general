# The Alexandrov Strengthening Bridge: Evaluation, Verification, and Strengthening

**Target file:** `external_audits/unifying object/deepseek alexandrov strengthening bridge.txt` (656 lines)
**Machine battery:** `scripts/alexandrov_bridge_verify.py` (AX-1 … AX-7, AX-2b)
**Evidence:** `download/alexandrov_bridge/{ax_results.json, ax_summary.txt, ax_figures.png}`
**Prior art searches:** `tool-results/alexandrov_search/s1.json … s13.json` (13 queries)
**Standing instructions honored:** verify, do not trust; deep web search for novelty; strengthen, correct, complete weaker suggestions and defects; joint assessment with the six-audit corpus; v21 frozen.

**Companion artifacts already in place (not duplicated here):**
- The formulation file (`deepseek formulation.txt`) was evaluated, verified, and rigorously repaired in the prior session: `download/Active_Set_Bridge_v2.md` (Theorems S/G/N/D) and `download/Active_Set_Bridge_v2_solution_report.pdf`; its "attempt to solve" was completed by Theorem B' and the stress battery `download/theoremB_stress/`.
- Theorem B' and its machine dossier: `download/TheoremB_Verification_and_Strengthening.md`.

---

## 1. Executive verdict

The file proposes one real strengthening and one real conjecture, quotes a classical
theorem correctly, proves one theorem correctly, contains one embedded and honest
self-refutation, and commits **three substantive errors** — one of which (the
codimension-2 atom claim) is the exact mirror of the (p−2)-skeleton defect already
falsified in the Theorem B audit. All three errors are repaired below, and the
repair is *strictly stronger* than the original proposal: the corrected statement
exhibits a **two-layer structure** (Hessian measure on codim-1 facets; Monge-Ampère
atoms on codim-2 vertices), an exact **dual-optimal-face identity** (now
machine-verified on a generic LP), and an exact **normal-cone identity chain**
(Regge defect = spherical area = gnomonic-weighted fan area, agreement to 0.0).

| # | File's claim | Verdict | Machine evidence |
|---|--------------|---------|-------------------|
| C1 | Alexandrov's theorem quoted as: convex f ⇒ D²f is a symmetric matrix-valued Radon measure | **TRUE, classical** (correctly quoted; attribution must stay classical) | s1.json (standard references); no claim of novelty permitted |
| C2 | "For a convex piecewise affine function, the singular part [of D²f] is a sum of atoms on the codimension-2 active-set corners" (§2) and "codim-2 concentration, no mass on codim-1 facets" (§5.3) | **FALSE as stated** — D²f is concentrated on codim-1 facets; the codim-2 atomicity holds for the *Monge-Ampère layer* det D²f (p = 2) | AX-1: D² mass in ε-box = [2, 1, 0.5, 0.25, 0.125] (slope 1.000, vanishes — codim-1 law); MA mass = 0.5 for every ε (codim-2 atom); AX-2: gradient piecewise-constant with between-jump residual 0.0 |
| C3 | Concavity of Φ (convexity of −Φ) for affine bound parameterizations, via LP duality (§"Convexity…") | **TRUE — proof verified correct** (pointwise min of affine functions over a θ-independent dual feasible set) | AX-1: concavity violation 0.0; AX-2: 7.1e-15 over 600 exact LP midpoints; AX-2b: 1.0 feasible, chambers = min cuts |
| C4 | (Implicit) "the exact parameterization used in the study" is covered | **FALSE in general — GPR caveat**: OR/max rules (isoenzymes) break joint concavity; AND/min and single-gene capacity slices retain it. iML1515 contains isoenzyme pairs (pfkA/pfkB, acnA/acnB were M4a archetypes) | AX-3: AND/min violation 0.0; OR/max canonical violation 0.5 (Φ(1,0)=Φ(0,1)=1, Φ(½,½)=½); s9.json (GPR AND/OR semantics is standard) |
| C5 | Value function + its Hessian measure are tie-break-free; canonical | **TRUE** (canonical existence: classical; tie-break-freeness: structural) | AX-6: value identical (0.0) under two lexicographic tie-breaks; V1 artifact: 12 flux events vs 1 value atom |
| C6 | "the empirical κ^μ … is a functional of κ_A = tr_V D²Φ"; "both are functionals of the same Alexandrov measure" (§3C, conjecture item 4) | **FALSE as attributed** — V5's κ^μ is the *flux-map strain* measure (sum_t |D²v|/dt per reaction), not a functional of the value function's Alexandrov Hessian | `download/deepseek_bridge/v5_e24_recalibration.json`: κ^μ := "measure mass: sum_t \|D2\|/dt per reaction, per-gene max (definition change)"; AX-6: atom-free value layer while the follower's flux-strain mass flips 0.0100 ↔ 1.1e-13 with the tie-break; V1: value/flux mass ratio 1.7e-6 |
| C7 | The embedded obstruction section: "the requested proof cannot be given as stated" (flat connection, quadratic Φ counterexample; type mismatch) | **TRUE — honest and correct**; the definitional re-identification (route A) is the only rigorous move and is *endorsed* | hand-check: Ω^∇ = 0 vs (D²Φ)(V,V) = VᵀAV > 0 for Φ = ½θᵀAθ; matches the M4b/M4c falsification of the ε² Riemannian identification |
| C8 | Novelty self-assessment: theorem classical; application may be new; frame the paper on the empirical result | **CONFIRMED by 13 searches** — no prior art at the (Alexandrov Hessian measure) × (genome-scale FBA value function) × (transcriptomic association) intersection; nearest neighbors identified (below) | s1–s13 (dossier in §5) |
| C9 | "This is precisely what the earlier V1 experiment discovered numerically" (value curvature = single atom, flux jumps curvature-flat) | **TRUE — and it *refutes* the file's own C6**: V1's decoupling shows the flux layer is *not* a functional of the value layer | V1 artifact; AX-6 |

---

## 2. The three defects, precisely stated and repaired

### 2.1 D-A (the codimension error — decisive)

**File text (§2, line 60):** "For a convex piecewise affine function, the singular
part is a sum of atoms on the codimension-2 active-set corners."
**File text (§5, item 3):** "Show that the singular part κ_A^s has the correct
atomic structure: codim-2 concentration, no mass on codim-1 facets."

**Why it is false.** For f convex piecewise affine, the distributional Hessian
D²f acts on φ by ∫ φ d(D²f) = ∫ f ∇²φ. On each codim-1 facet F with one-sided
gradients g^±, D²f has density [∂_n f] · (g^+ − g^−) ⊗ n per unit facet measure:
**the Hessian measure is (p−1)-dimensional**. Its mass in an ε-ball around a
codim-2 vertex scales like ε (facet lengths shrink), hence *vanishes* — there is
no atom. The codim-2 atomicity is instead the exact statement for the
**Monge-Ampère measure** det D²f (p = 2): det D²f(Q) = |∇f(Q)| (area of the
gradient image, with multiplicity), which at a vertex is the area of the normal
fan — an honest atom, constant under ε-shrinking.

**Machine evidence (AX-1).** Φ = min(0, θ₁, θ₂) realized as an LP (3-cap
encoding, Danskin duals exact to 0.0 over 3,540 interior grid points):

| ε | mass of D²Φ in [−ε,ε]² | MA measure det D²(−Φ) of the box |
|---|---|---|
| 0.5 | 2.000 | 0.5 |
| 0.25 | 1.000 | 0.5 |
| 0.125 | 0.500 | 0.5 |
| 0.0625 | 0.250 | 0.5 |
| 0.03125 | 0.125 | 0.5 |

D² mass slope (log-log): **1.000** (codim-1 law, vanishes); MA mass **constant
0.5** (codim-2 atom). Crease gradient jumps measured at 1.000, 1.000, √2
(analytic: 1, 1, √2). MA atom cross-checked against the dual optimal face
enumerated by 16 LPs: 0.5 = 0.5 exactly.

**Repair.** Replace the claim by the two-layer statement (Proposition A2 below).
The file's own §5.3 research program ("show codim-2 concentration, no mass on
codim-1") is **vacuous as stated** — it asks to prove a false structure; the
correct program is stated in §4 (Repaired conjecture, items 2–3).

This defect is the exact p-dimensional mirror of the (p−2)-skeleton support
defect (D-A) already falsified in the Theorem B audit
(`download/TheoremB_Verification_and_Strengthening.md`), and of the angle-defect
conflation (D-E) repaired there by the sec law. Three independent audits now
agree on the same layered structure; this convergence is itself evidence.

### 2.2 D-B (the misattribution of κ^μ)

**File text (§3C):** "The measure-theoretic metric used in V5 can be defined as
κ^μ(g) = ∫ ‖D²Φ‖_V dμ_g … both are functionals of the same Alexandrov measure,
and the lexicographic κ merely samples it at selected events." (Also conjecture
item 4.)

**Why it is false.** V5's executed definition
(`download/deepseek_bridge/v5_e24_recalibration.json`) is:
`kappa_mu = "measure mass: sum_t |D2|/dt per reaction, per-gene max (definition
change)"` — the second differences of the *flux-map trajectory* v(θ(t)) of the
deterministic lexicographic pFBA engine, *not* of the value function. The
misattribution is not cosmetic: the two layers are provably decoupled.

**Machine evidence.**
- **V1 artifact** (iML1515 single-reaction bound cut): 12 flux-map events vs
  **1** value-function atom; value/flux mass ratio 1.7 × 10⁻⁶.
- **AX-6** (new toy, honest two-stage lexicographic LPs): the value function is
  *affine* (atom-free, identical 0.0 under both tie-breaks) while the follower
  variable's |Δ²| mass is 0.0100 with 1 event under tie-break A (min |s|) and
  1.1 × 10⁻¹³ with 0 events under tie-break B (max s). The flux-strain event
  structure is a **tie-break artifact** in the degenerate layer; the value
  function's measure is not. A functional of an atom-free measure cannot
  produce a nonzero kink count.

**Why the rank identity ρ(κ^μ, κ_lex) = 0.99998 is nevertheless real:** both
metrics sample the *same event structure of the same flux-map trajectory* (the
lexicographic engine's active-set crossings). The identity is a
trajectory-consistency property of the flux layer, **not** a shadow of a common
value-function measure. The honest justification is one sentence, and it is
stronger than the file's: the association is invariant to the *metric*
(event-counting vs measure-mass along the same trajectory), which is what a
reviewer needs to hear.

**Repair.** Conjecture item 4 is deleted as stated and replaced by the
decoupling statement (Proposition A4 below): κ^μ is a functional of the
*flux-map* Hessian measure D²v (Definition D1 of the v2 manuscript), which is
tie-break-*sensitive*; the value function's Alexandrov measure is tie-break-free
but carries different information. The bridge between them is an open problem,
correctly demoted to a conjecture (§4, item 5).

### 2.3 D-C (the convexity overclaim)

**File text (§4 "Application to the study"):** "Every parameterization used in
the study satisfies the affine-bound condition … Hence −Φ is convex, and
Alexandrov's theorem applies directly."

**Why it is an overclaim.** The LP-duality proof is correct *for affine bound
functions*. Gene-capacity parameterizations are affine in θ **only after the
GPR evaluation is resolved**. For an AND (enzyme complex) rule, the capacity is
min(c_g1, c_g2) — realizable as two affine rows v_r ≤ c_gi u_r — jointly convex,
concavity of Φ preserved. For an **OR (isoenzyme) rule**, the capacity is
max(c_g1, c_g2) — not affine, and the joint feasible set in (c, v) is not convex.

**Machine evidence (AX-3).** AND/min gate feeding a chain: concavity violation
0.0 over 2,000 random midpoint tests (LP-level). OR/max canonical counterexample:
Φ(1,0) = Φ(0,1) = 1, Φ(½,½) = ½ ⇒ violation 0.5 (measured 0.548 worst-case
random, 0.5 canonical). The study's own model iML1515 contains isoenzyme pairs —
(pfkA, pfkB) and (acnA, acnB) were M4a archetypes precisely because they are
alternative optima switches.

**Repair.** The convexity theorem holds verbatim along (i) any single-gene
capacity axis, (ii) any substrate-uptake/exchange bound family, (iii) AND-only
subnetworks; it **fails in general for simultaneous multi-gene capacity vectors
on OR rules**. All value-function cuts used in the executed program (V1: single
reaction bound; E24/V5: uptake trajectory) are in the safe class. The v2
manuscript must state the caveat; §6 gives the wording.

---

## 3. What the file gets right (and is kept)

1. **The core move is sound and valuable:** promote the value function Φ to the
   canonical, tie-break-free object and let Alexandrov's theorem endow it with a
   matrix-valued Radon measure without smoothness, mesh, or interpolation
   assumptions. This *removes the extrinsic character* of Theorem B' (existence
   no longer needs a refinement sequence — only convergence statements do).
   The v2 manuscript should adopt this as the *existence layer* and keep
   Theorem B' as the *resolution/refinement layer*. The two are complementary,
   not competing: the file's claim that this "avoids the false TV-convergence
   claim" is exactly the right division of labor.
2. **The embedded obstruction section (lines 304–457) is honest and correct:**
   tr_V Ω^∇ for the trivial connection is identically 0 while (D²Φ)(V,V) > 0 for
   quadratic Φ — the requested equality is type-mismatched; only the definitional
   re-identification (route A) or a graph-metric identification with proof
   (route B) are available, and B is blocked by M4b/M4c. **We endorse route A**
   and note it is *already* what the v2 spine does (κ_geom := density of the
   viability-contracted Alexandrov measure, as a definition).
3. **The novelty self-assessment is confirmed** (§5 below): the theorem is
   classical; the combination (value-function Alexandrov measure as the
   canonical curvature carrier for genome-scale metabolic models + the
   two-layer structure + the empirical association + protein-layer buffering) is
   the contribution, and it is an application. The file's recommended framing
   sentences are adopted nearly verbatim in §6.
4. **The observation that V1 is "precisely" the numerical signature of the
   Alexandrov layer** — value atom well-defined, flux jumps large but
   curvature-flat — is correct and, taken seriously, *forces* the two-layer
   correction (D-A) and the decoupling (D-B). The file is better than its own
   claim here.

---

## 4. The repaired conjecture (strictly stronger form)

All statements below are either classical, proved here, or machine-verified as
noted; the single remaining open item is isolated in item 5.

**Proposition A1 (existence layer; classical).** Let
Φ(θ) = max{cᵀv : Sv = 0, ℓ(θ) ≤ v ≤ u(θ)} with ℓ, u affine, feasible and
bounded. Then Φ is concave (pointwise infimum of the affine functions
yᵀu(θ) − zᵀℓ(θ) over the θ-independent dual feasible set), and
D²(−Φ) exists as a symmetric matrix-valued Radon measure (Alexandrov).
*Validity:* proof verified; concavity machine-checked (AX-1: 0.0; AX-2: 7.1e-15;
AX-2b: 0 by cut structure). *Caveat:* OR/max GPR rules break joint concavity in
the multi-gene capacity vector (AX-3); single-gene axes, exchange bounds, and
AND-only subnetworks are safe.

**Proposition A2 (two-layer structure; proved + machine-verified).** Let f be
convex piecewise affine.
(i) The singular part of D²f is supported on the (p−1)-facets, with density
[∂_n f](g⁺ − g⁻) ⊗ n per unit facet measure; it has **no atoms**: the mass in
an ε-neighborhood of any codim-2 vertex is O(ε) (AX-1 slope 1.000).
(ii) The Monge-Ampère measure det D²f (p = 2) is atomic at codim-2 vertices:
the atom equals the (p−1)-volume of the normal fan
conv{∇f(τ): τ ∋ vertex} (AX-1: 0.5 constant; analytic 0.5).

**Proposition A3 (dual-optimal-face identity; machine-verified, AX-2b).**
At a codim-2 vertex θ_v of a parametric LP value function, the MA atom of
−Φ equals the area of the normal fan, and the fan is the image of the **LP dual
optimal face** under θ ↦ Uᵀy:
  det D²(−Φ)({θ_v}) = |conv{∇C_i}| = |{Uᵀy : (λ, y) optimal dual}|.
*Evidence:* max-flow LP (the phenotype phase plane in miniature), vertex
detected at (0.7660, 0.8085) (refined by exact triple-tie solve), Φ(LP) =
3.5553191489361677 vs tie 3.5553191489361664; fan area 0.235 vs dual-face
enumeration area 0.235000068 (16 direction-LPs over
{Sᵀλ + y ≥ c, y ≥ 0, yᵀu(θ_v) ≤ Φ}). This upgrades the audit's dual-face
remark to a machine-verified identity on a generic LP and is the
"FBA-visible" form of the Alexandrov normal-cone construction.

**Proposition A4 (normal-cone identity chain; machine-verified, AX-4).**
For the polyhedral graph of f at a vertex with normal fan N:
  Regge angle defect = (spherical area of the Gauss image)
                     = ∫_N (1 + |g|²)^(−3/2) dg   (gnomonic Jacobian),
while the MA atom = |N| (unweighted planar area). *Evidence:* f = max(0,−x,−y):
defect = spherical excess = gnomonic integral = 0.3398369094541218 rad
(three independent computations, pairwise differences 0.0); MA atom 0.5. The
two curvature layers differ *exactly* by the projection weighting — this is the
closed form of the sec-law correction (BT-7/7b) and the rigorous version of the
audit's "Route 1 (Regge)".

**Proposition A5 (tie-break-freeness vs. flux-layer degeneracy;
machine-verified, AX-6 + V1).** The value function and D²Φ are independent of
the optimal-flux selection rule; the flux-map strain measure D²v is not
(a degenerate follower variable's |Δ²| mass flips 0.0100 ↔ 1.1e-13 between two
lexicographic tie-breaks while Φ stays affine and identical). Consequently the
empirical κ^μ (V5: flux-strain along the lexicographic trajectory) is **not** a
functional of D²Φ.

**Conjecture A6 (the repaired Alexandrov Active-Set Bridge; the only open
item).** Keep the file's items 1–3 in corrected form (canonical existence;
κ_A^{ac} identified with κ_geom *by definition* under the viability contraction;
singular part supported on the active-set complex — codim-1 for the Hessian
layer, codim-2 for the MA layer), **replace** item 4 by: *there is a controlled
relation between the flux-strain measure D²v (which κ^μ integrates along
trajectories) and the value-function measure D²Φ (which is canonical)* — e.g.
a bound of the event structure of v by the facet structure of Φ along generic
cuts, with the V1 ratio 1.7 × 10⁻⁶ and the M4a ε¹-vs-ε² dichotomy (AX-7: slopes
1.0000000000000002 vs 2.0) as the two endpoints of the regime. Until proved, the
association κ^μ ↔ transcriptional response stands on the flux layer alone, which
is where the evidence (E24 r = +0.374, V5 r = +0.395, n = 424/433) actually
lives.

---

## 5. Novelty assessment (13 searches, verified)

**Queries covered:** Alexandrov second derivatives/proof; Hessian measures of
convex functions; multiparametric LP piecewise-affine value functions;
parametric FBA value function curvature; phenotype phase planes; discrete
Monge-Ampère / Aleksandrov solutions; convex PL functions on simplices; FBA
degeneracy and alternate optima; GPR AND/OR semantics; carbon-depletion
proteome/transcriptome buffering; bounded Hessian/nonsmooth analysis; "Alexandrov
space" + metabolic networks; FBA solution non-uniqueness.

**Findings.**
1. **Alexandrov's theorem: fully classical** (s1: standard references, MathOverflow
   discussions; Hessian-measure theory of convex functions is textbook material).
   The file's warning that presenting it as new would be "reinventing the wheel"
   is confirmed.
2. **mpLP chamber theory: established** (s2: Bemporad et al. mpLP convexity and
   piecewise-affine solutions; Pappas et al. 2021 on exploring all optimal active
   sets; the emergent-mind topic survey). The *value function of a parametric LP
   is PWL and its nonsmoothness lives on the chamber complex* is decades-old.
   Note the prior session's search also surfaced a *converse*-type result
   (Hempel et al. 2013: every PWL function arises as an mpLP value function) —
   i.e. even the structure of D²Φ for general mpLP is fully charted territory.
3. **Phenotype phase planes: the direct metabolic prior art** (s3: Edwards,
   Ibarra, Palsson 2001, cited 1,325×: "phase plane analysis of the metabolic
   genotype-phenotype relation"; the value function of the two-uptake FBA
   problem with its linear sectors is exactly a 2-parameter PL concave Φ). The
   file's bridge must therefore be positioned as a *second-order refinement of
   PhPP* (curvature measure on the PhPP chamber complex), not as a new object.
   AX-2b is literally a PhPP in miniature and shows the vertices are where the
   MA atoms live — the natural slogan: "PhPP sectors = chambers; PhPP sector
   corners = atoms."
4. **Discrete Monge-Ampère: adjacent, not intersecting** (s4, s5:
   Froese–Oberman-type MA solvers, Benamou 2010, convergence of FD schemes to
   Aleksandrov solutions; PL convex functions and Minkowski sums). Nobody there
   connects MA atoms to parametric LP value functions *as metabolic objects*.
5. **Regge calculus codim-2 hinges: established geometry, no FBA link** (s7:
   Christiansen 2024: "In dimension 2, the distributional curvature features
   vertex Diracs corresponding to linearized deficit angles" — the codim-2
   statement in its correct home; Weisstein's summary: curvature concentrated
   on codim-2 subsimplices). Proposition A4 is the exact bridge statement
   between that literature and the MA layer, and no prior statement of it at
   this intersection was found.
6. **"Alexandrov space" + metabolic networks: unrelated** (s12: metric-geometry
   Alexandrov spaces for network alignment — a different Alexandrov notion;
   no hit uses Hessian measures).
7. **FBA degeneracy/alternate optima: known, but only first-order** (s6, s13:
   Orth et al. 2010; Reznik et al. 2013; alternate optima literature). The
   *second-order* (measure-theoretic, tie-break-free) reformulation of
   degeneracy via the value function is not present there.
8. **GPR AND/OR semantics: standard** (s9: Di Filippo et al. 2021, GPRuler) —
   supports the D-C caveat being routine domain knowledge that the file should
   have carried.
9. **Empirical layer:** (s10) carbon-utilization proteome/transcriptome studies
   (Scott et al., Shimizu, Boecker) — no curvature-measure predictor of
   transcriptional response exists in this literature; the association claim
   remains novel.

**Verdict.** No prior art at the three-fold intersection. The file's own
bottom line — "the bridge is not new mathematically; the application, metric,
and empirical findings may be new; frame the paper around the biological
result" — is **confirmed** and adopted. The strongest defensible novelty
statements are: (a) the two-layer dissection of the FBA value function's
curvature (Prop A2) with the dual-face identity (A3) as its LP-visible form;
(b) the normal-cone identity chain (A4); (c) κ^μ's association with
carbon-depletion transcriptional response and its protein-layer null. All
three are applications/theorems-about-applications, and all three now have
machine dossiers.

---

## 6. Manuscript integration (v2 Layer-0 edits; v21 untouched)

1. **§3 (sec:measure), new subsection [D3] "The value-function layer":** state
   Proposition A1 (existence, classical, with the GPR/OR caveat sentence),
   Proposition A2 (two-layer structure) with AX-1 numbers, and Proposition A3
   (dual-face identity) with AX-2b numbers. Position vs. PhPP as in §5.3.
2. **§4 (sec:theoremB):** add one paragraph after Theorem B': existence no
   longer requires refinement (Alexandrov); Theorem B' governs *resolution*
   (what a discrete trajectory can see of the measure). The file's claim that
   this division "avoids the false TV-convergence claim" becomes the
   transitional sentence.
3. **§5 [E-V1] block:** add the AX-6 tie-break decoupling sentence and the
   value/flux layer separation (already present as the 1.7e-6 ratio; cite AX-6
   as the controlled toy).
4. **§6 [E-V5] remark:** replace any "same Alexandrov measure" justification of
   the rank identity 0.99998 with the trajectory-consistency justification
   (both metrics sample the same flux-event structure of the same lexicographic
   trajectory). **Do not** present κ^μ as a functional of D²Φ.
5. **Conjecture A6** replaces the file's Conjecture item 4 in the bridge
   discussion; the ε¹/ε² dichotomy citation becomes AX-7 + M4a + BT-8.
6. **Framing sentences (adopted from the file, minimally edited):**
   - "We apply the classical Alexandrov theorem to the parametric-FBA value
     function: its Hessian exists as a matrix-valued Radon measure without
     smoothness assumptions, and is independent of solver tie-breaking."
   - "The Monge-Ampère layer of this measure is atomic at the codimension-two
     vertices of the chamber complex — the corners of phenotype phase planes —
     where each atom equals the area of the LP dual optimal face."
   - "The discrete (active-set) and smooth regimes are the singular and
     absolutely continuous parts of one measure; the identification of the
     latter with the geometric curvature density is a definition, not a
     theorem."
7. **Citations to add:** Alexandrov (1939/1957 as quoted in modern texts);
   Rockafellar (1970) for PL convex duality; Bemporad et al. (mpLP survey);
   Edwards, Ibarra & Palsson (2001) for PhPP; Christiansen (2024) for the
   Regge codim-2 statement; Froese & Oberman / Benamou (2010) for discrete MA;
   Hempel & co. (converse, from the earlier search wave) if the mpLP
   completeness remark is kept.

---

## 7. Reproducibility

- Battery: `python3 scripts/alexandrov_bridge_verify.py` (≈70 s; scipy HiGHS;
  deterministic seed 20260902). Outputs:
  `download/alexandrov_bridge/ax_results.json` (all numbers quoted above),
  `ax_summary.txt`, `ax_figures.png` (3 panels: AX-7 dichotomy, AX-6
  tie-break decoupling, AX-2b chamber map with vertex and atom).
- Prior-art dossier: `tool-results/alexandrov_search/s1.json … s13.json`
  (13 queries, top hits with URLs).
- Cross-references: `download/TheoremB_Verification_and_Strengthening.md`
  (Theorem B' and the sec law — the p-dimensional counterpart of D-A),
  `download/Active_Set_Bridge_v2.md` (the formulation file's rigorous repair),
  `download/deepseek_bridge/v5_e24_recalibration.json` (κ^μ definition),
  `download/deepseek_bridge/v1_value_function.json` (decoupling), V1 numbers
  in the v2 spine (§5 [E-V1]).

**Bug honesty note.** The battery as first written contained three defects
(linprog bounds tuple; crease finite differences straddling the crease; a
vacuous AX-6 design in which both tie-breaks coincided; plus a dead-code AX-7
that never called its field, and an AX-2 concavity test with grid
discretization noise). All were repaired before the results above were
recorded; the AX-4 Duffy-map quadrature bug was caught *by the run itself*
(the identity it tested is true — three independent computations agree at
0.0 — and the faulty quadrature was fixed, not the conclusion).
