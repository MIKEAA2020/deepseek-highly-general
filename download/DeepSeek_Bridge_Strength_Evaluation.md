# DeepSeek "Strengthen the Highly General Bridge" Audit — Evaluated, Verified, Corrected, and Completed

**Document status.** This is the evaluation of the audit
`external_audits/unifying object/deepseek stengthen highly general
bridge.txt` (DeepSeek's response to the M4c / root-cause evaluation,
186 lines: a Part-1 assessment of M4c + a strategic recommendation, and
a Part-2 list of five "strengthening routes" for the bridge with a
recommended target theorem). Mandate: **evaluate, verify, do not take
at face value; strengthen, augment, improve, correct, and complete the
weaker suggestions and defects.** Every verdict below is grounded in
either the committed record (M1, M3/M3b, M4a/b/c, the Active-Set Bridge
v2 theorem set, `download/Root_Cause_Evaluation.md`) or in new machine
verifications executed for this document: **V1** (value-function
carrier on the real network), **V2** (refinement prototype of the
corrected bridge theorem), **V3** (the sigma-limit direction on the
*measured* M4c measure), and **V5** (the audit's "decisive test" — the
E24 recalibration with the measure-theoretic kappa — executed, not
deferred). The frozen v21 manuscript is untouched; this file is source
material for `journal_manuscript_v2+`. Standing instructions honored:
push check first (all prior work on `origin/main` at `98e24fe`; the
audit itself arrived in remote commit `d85b162`), commit and push at
the end, English response.

---

## 0. One-paragraph verdict

The audit's **Part 1 is a faithful summary of the corrected record**
— it restates the RC1 trichotomy (state holonomy exactly trivial;
codim-2 defects O(1) scale-invariant; the O(ε) commutator is dynamic
hysteresis, not holonomy), the Theorem-R convolution identity, and the
M4c dial accurately, and its five recommended next steps are all
consistent with the record (four of the five were already the record's
own open items). But the audit's **Part 2 — the five strengthening
routes and the recommended target theorem — contains one central
mathematical defect**: its headline formula

> κ_geom = lim_{σ→0} κ_flux ∗ φ_σ  (weak convergence of measures)

**selects the atomic object, not a smooth one.** As σ→0 the family
μ ∗ φ_σ converges weakly to the atomic measure μ — verified here on
the measured M4c event set (V3: mass collapses onto the 12 events;
wall-free density vanishes exponentially) and in the prototype (V2b).
The same inversion appears in Route 1's statement and in the audit's
line-30 interpretation ("the σ→0⁺ smooth limit of the coarse-grained
family, not the direct limit of the unsmoothed FBA map" — these two
limits are the *same* limit). A genuine limit theorem requires
**refinement of the underlying complex**, which the audit names but
never uses; we construct it, prove it in prototype form (Theorem B),
and verify it numerically (V2a/c). Route 3's premise
(v(θ) = ∇Φ(θ)) is false for constraint-parameterized FBA and is
replaced by the correct, *stronger* statement (D²Φ is the canonical
tie-break-free carrier; V1). Route 4's "nontrivial basis-change
cocycle" is exactly trivial (two-line telescoping proof); the
nontrivial connection already exists in the record (Theorem G).
Finally, the audit's decisive empirical test — re-run E24 with the
measure-theoretic κ — is **executed here (V5) and passes with
strengthening**: r = +0.374 → **+0.395**, partial r = +0.251 →
**+0.269**, deciles 1.92/0.89 preserved. By the audit's own criterion,
the single-paper route is secure.

---

## 1. Claim-by-claim verification of Part 1 (fidelity to the record)

| # | Audit claim | Record / verification | Verdict |
|---|---|---|---|
| 1 | "The smooth ε² bridge was indeed the wrong object" | Root-cause RC-dagnosis; Theorem N; M4c | **True** |
| 2 | "State holonomy is exactly the identity (trivial, as v is a function)" | Theorem S(v); m4b `state_holonomy_note` | **True** |
| 3 | "Codim-2 defects are scale-invariant, O(1) angle defects — discrete Regge-type curvature" | Theorem G; −7.1469°/−23.9087° reproduced at δ and δ/2 | **True** |
| 4 | "The O(ε) commutator is a dynamic hysteresis measure, not geometric holonomy" | Theorem D; release identity 6/6 bit-exact | **True** |
| 5 | Theorem R identity D²(v∗φ_σ) = (D²v)∗φ_σ; ε² for ε≪σ, linear for ε≫σ | M4c (kernel self-test 1.2e-6; slopes 1.999x) | **True** |
| 6 | "Measured crossover ε\*/σ ≈ 3–4" | M4c: 4.11 / 2.98 / 3.11 / **2.45** (median 3.1) | **True, slightly overstated at the top** |
| 7 | "M4a measurement of slope 1.00 … was the decisive empirical falsification" | RC5: the falsification is **a priori** (mpLP theorem, Gal–Nedoma 1972); M4a *confirms* it at machine precision; RC2: slope-1.00 describes the 9/76 interacting stratum (64/76 have χ = 0 exactly) | **Epistemics slip — see D8** |
| 8 | "The Gal–Nedoma reference makes it model-independent" | RC5 wording: model-independence comes from LP structure, not from a citation | **True in substance** |
| 9 | "A very thin chamber self-cancels to a net measure jump of 8.9 instead of ±1884.6 … earlier coarser analyses overcounted events" | RC6: M4b's *signature density* overstates curvature-measure density; the census count was correct at its resolution (12 events at M4c resolution) | **True with a nuance — see D8** |
| 10 | "There is one underlying discrete curvature measure μ = D²v, concentrated on active-set boundaries; κ_flux is a functional of that measure" | Theorem S(ii); M1 (D2 mass 0.934–1.0 on events); the formal identity κ_flux = F[μ] is still open — and now *tested empirically* by V5 | **True; the open step is now decoupled from the association (V5)** |
| 11 | "κ_V should be interpreted as the σ→0⁺ smooth limit of the coarse-grained family, not the direct limit of the unsmoothed FBA map" | **False as stated**: lim_{σ→0} μ∗φ_σ = μ weakly — the same atomic object as "the direct limit of the unsmoothed map". The smooth member of the family exists only at **fixed σ > 0** (the resolution statement), or under **refinement** (Theorem B) | **Wrong limit direction — see D1** |
| 12 | Strategic spine: single coherent manuscript; trim categorical/HoTT to appendix; "do not split yet" | Consistent with the joint assessment (6/6: strong-form unification not provable; the repair program); now **secured by V5** (the audit's own stated condition) | **Endorsed, condition now met** |
| 13 | Next steps 1–5 (E24 re-run; resolution-statement section; v2 Layer-0; defer E28; keep v21 frozen) | Step 1 executed here (V5); step 2 already the record's §5 form; step 4 matches the M4c (ε,σ) design law; step 5 honored | **All consistent; step 1 done** |
| 14 | "Do not attempt to prove smooth ε² behavior for the unsmoothed object; that is known to be false" | Theorem N; M4c | **True — and extended: also do not take the σ→0 limit of the smoothed object (D1)** |

Part-1 summary: **faithful where it summarizes the record (rows 1–6,
12–14), with two inherited slips (rows 7, 9) and one forward-looking
error (row 11) that becomes the central defect of Part 2.**

---

## 2. The defects of Part 2 (D1–D8), each with its verification

**D1 — The limit direction is inverted in the recommended theorem
(fatal as stated; corrected in §3).** The audit's final recommendation
(Routes 1+2 combined) proposes

> κ_geom = lim_{σ→0} κ_flux ∗ φ_σ  in the sense of weak convergence of
> measures,

and Route 1 states "the coarse-grained measure μ_σ = μ ∗ φ_σ converges
weakly, as σ→0, to the curvature measure of a Riemannian metric g."
For a **fixed** network (fixed complex) this is false: by standard
mollifier theory μ ∗ φ_σ ⇀ μ (the atomic measure) as σ→0, which is
precisely Theorem N's obstruction — no renormalization of the family
yields a finite nonzero smooth limit. We verified this on the
**measured** M4c event set (12 events, total L2 jump mass 3807.6):

- **V3 (mass collapse):** the fraction of μ_σ mass within a *fixed*
  half-width w = 0.01 of the 12 event positions → **1.0000** as
  σ → 1e-4. Any absolutely continuous limit with bounded density puts
  vanishing mass in a fixed-measure neighborhood set; the limit is
  concentrated on the atoms.
- **V3 (wall-free density):** κ_σ(t₀)/κ_σ^peak at a wall-free point
  (clearance ≈ 0.052) decays to **0** (machine zero; exponentially in
  (clearance/σ)²) while the peak grows like 1/σ.
- **V3 (test-function separation):** a fixed bump on the largest atom
  integrates to **3772.5** at σ = 3e-4 (the full mass of the sliver
  pair 1884.6 + 1875.7) versus **253.4** for the smoothest honest
  family member (σ = 0.3) — the σ→0 family converges *to the atomic
  measure's action*, not to any smooth density's.
- The audit's line-30 phrase "the σ→0⁺ smooth limit of the coarse-grained
  family, **not** the direct limit of the unsmoothed FBA map"
  distinguishes two objects that are *equal*: both limits are μ.

**What is true instead** — two defensible statements, one already in
the record and one new: (i) the **resolution statement** (Theorem R /
M4c): at every fixed σ > 0 the smoothed map is smooth and carries the
same curvature mass (R4: σ-independent, telescoping residual 4.0e-14),
with the ε²/ε¹ dial at ε\* ≈ 3σ; (ii) the **refinement limit**
(Theorem B below): under a sequence of *refined* parametric-LP
families, the atomic measures converge weakly to the smooth curvature
density — the audit gestures at this in Route 2 ("as the FBA polytope
is successively refined") but then drops the refinement from its final
formula. The corrected theorem is stated, proven in prototype, and
machine-verified in §3.

**D2 — Route 3's premise "v(θ) = ∇_θΦ(θ)" is false for the relevant
parameterization; the corrected statement is stronger than the route
it replaces.** The flux map v ∈ R^m (m = 2867 on iML1515) cannot be
the gradient of a scalar Φ: R^d → R (d = 2 here) — a dimensional
impossibility, independent of conditions. The gradient map of the
value function is the **dual** y ∈ R^d (Danskin/envelope theorem):
∇Φ = (y_glc, y_o2). The route's further claim "D²v is therefore the
Hessian of Φ" fails with it. What survives — and improves the route —
is this, verified as **V1** on the real network (253 lex solves on the
M4c cut, iML1515):

- **(a) Φ is piecewise affine on the v-event partition**, worst
  affine-fit residual **4.2×10⁻¹³** over all 5 grid-resolved segments
  of the full ±0.4 cut. (Trivially, kinks of Φ ⊆ kinks of v because
  Φ = c_bio·v\*; the nontrivial content is the *atom structure*.)
- **(b) The canonical carrier.** Φ = c_bio·v\* is single-valued **with
  no tie-breaking whatsoever** — the value function is immune to the
  pFBA vertex degeneracy that forced the lexicographic machine for v.
  D²Φ (shadow-price jumps) is therefore *the* canonical curvature
  measure of the parametric LP; D²v is its tie-break-dependent
  refinement with a strictly finer event set.
- **(c) One real atom.** Of the 12 censused v-events, the entire value
  curvature of the cut is a **single atom** ΔΦ′ = **−0.006439** at
  t = 0.0358286 — a *minor* flux event (jump norm 11.59, the first
  member of a sliver pair whose partner has jump 1.6×10⁻⁵). The
  dominant flux atoms are value-flat: the 1875.7/1884.6 sliver pair
  (t ≈ 0.001869) nets **≤ 7.7×10⁻¹¹**; the 22.3-jump event
  (t = 0.0354385) nets ≤ 8.4×10⁻⁹; the 0.51/0.81-jump pair ≤ 3.8×10⁻¹¹.
  Total value TV ≈ 0.00644 versus total flux jump mass 3807.6 — a
  ratio of 1.7×10⁻⁶, and the two hierarchies are **not proportional**:
  the value atom sits at the *sixth-largest* flux event, and the
  largest flux event carries *zero* value curvature.
- **(d) Danskin verified at machine precision.** The stage-1 LP's
  bound marginals (extractable on the r-copy of the duplicated uptake
  bound) equal the two-sided FD shadow prices to 6–7 significant
  digits at all 5 probe points; the prices are constant
  (y_glc, y_o2) = (0.0252545, 0.0336727) on [−0.4, 0.0352) and
  (0.021743, 0.039138) on (0.0358, 0.4] — they jump exactly at the
  value atom; and the identity Φ′(t) = y·θ′(t) reproduces both
  measured segment slopes (−0.009316, −0.015755) exactly.

The corrected Route 3 therefore reads: *the value function's
distributional Hessian D²Φ is the canonical, degeneracy-free atomic
curvature measure of parametric FBA (the shadow-price-jump measure of
classical LP sensitivity analysis); Theorem R applies to it verbatim
(D²(Φ∗φ_σ) = (D²Φ)∗φ_σ); and its atom hierarchy is decoupled from the
flux-jump hierarchy* — a formalization of the rerouting-vs-function
decoupling that the Kochanowski framing already articulated at the
protein layer. This is a genuine strengthening, not a repair.

**D3 — Route 2's refinement mechanisms are not refinements.** "Adding
reactions" produces a *different* parametric LP whose chamber
structure does **not** refine the previous one (critical surfaces
move; chambers are not nested — there is no mesh to send to zero).
"Parameter grid resolution" changes only the *sampling* of a fixed
map: v(θ) and its measure μ are grid-independent. The valid
refinement must be *constructed* — nested constraint families that
polyhedrally approximate a smooth feasible region (exactly the
prototype of §3, and the classical setting of Cheeger–Müller–Schrader
1984, the citation the audit is missing throughout). With D1 and D3
together, Route 2's "medium-high" feasibility grade is **overstated
for real networks**: pointwise strong regularity (Robinson,
Klatte–Kummer) does not give global chamber stability under
refinement, and genome-scale models do not come in refinement
sequences. Prototype: done (§3). Real network: open conjecture (RA,
§3), low feasibility, blocked by exactly the sliver cascades the
record already measured (RC6: 2.4×10⁻⁶-wide slivers with ±1884.6
jumps; Theorem N(iii)(a) model-family regularity open).

**D4 — Route 4's "nontrivial basis-change cocycle" is exactly
trivial.** Let B(θ) be the (lex-unique) optimal basis, constant on
each open chamber. For any closed loop crossing chambers
C₁→C₂→…→C_k→C₁ with transitions G_i = B_{i+1}B_i⁻¹ (indices mod k),

  G_k ⋯ G_1 = (B₁B_k⁻¹)(B_kB_{k−1}⁻¹) ⋯ (B₂B₁⁻¹) = I,

by telescoping — for *every* loop, at *every* scale, exactly as for
the state holonomy (Theorem S(v)). The audit's proposed escape from
the triviality problem ("the basis-change cocycle is nontrivial") is
the wrong cocycle. The nontrivial connection in the record is the
**unfolding transport** of Theorem G — parallel transport of tangent
planes across the kinked codim-1 interfaces of the flux graph, whose
closure failure around codim-2 vertices is the O(1) scale-invariant
angle defect (−7.1469°, −23.9087°, machine-reproduced at loop radii δ
and δ/2, and unfolding = −defect to 10⁻¹⁴ on synthetic cones). Route
4's *instinct* — the nontrivial connection lives on a derived bundle,
not on the state — is exactly right; the correct object already exists
and is verified. Route 4 is thereby **complete in the record**, and
its remaining content (holonomy of the smoothed basis connection
converging to the SAVGS connection) inherits both D1's limit-direction
problem and D6's smuggled identification.

**D5 — Route 1 defines μ as "the angle defect at each corner," which
is only one of the two carriers (RC4).** The static curvature of the
FBA map is carried by (i) the Jacobian-jump measure D²v on **codim-1**
interfaces (M1's object; the M4c census; the κ_flux functional) and
(ii) the angle-defect measure on **codim-2** crossings (Theorem G).
They are related by discrete structure equations but live on different
strata, have different scales (O(ε) mass accumulation vs O(1)
scale-invariant defects), and are detected by different experiments.
A convergence theorem for "the" discrete curvature must carry both
carriers — Theorem B's prototype does (its atomic measure is the
codim-1 layer along cuts; its vertex defects are the codim-2 layer of
the same subdivision).

**D6 — Route 1 smuggles the conclusion it should prove.** "…and this
g is the metric induced by the viability field V" / "The only
remaining question is whether the limiting Riemannian metric coincides
with the manuscript's g^SAVGS" — this is precisely the identification
that the joint assessment found **not provable** (6/6 consensus) and
that Theorem N blocks in the pointwise sense. A refinement limit
produces *some* smooth curvature measure determined by the limiting
geometry of the refinement sequence; making it equal g^SAVGS requires
an explicit construction linking the viability functional to the
refinement — there is no reason for automatic coincidence. The honest
form is a separate, explicitly-open **Conjecture SA** (§3), not "the
only remaining question."

**D7 — Route 5's anchors are wrong-level, and its honest low grade is
correct but under-specified.** The lattice-gauge analogy ("analogous
to how lattice gauge theories converge to Yang–Mills") overstates the
state of the art: rigorous continuum limits exist for 2D Yang–Mills
and in Balaban-style partial frameworks, not as a general construction
— the analogy is aspirational, and the audit's own "low to medium, may
not be necessary" is the right grade. What Route 5 is missing is the
classical anchor for the *piecewise-flat* side: **Cheeger, Müller,
Schrader (1984)** — curvature measures of compatibly refined
piecewise-flat spaces converge weakly to the Riemannian curvature
measure — which is the direct ancestor of Theorem B and the correct
citation frame for the entire program. We also add the near-term
statistical version the route lacks (E32 proposal, §3).

**D8 — Part-1 fidelity slips (minor, worth fixing in any citation of
this audit).** (i) M4a is a *confirmation* of an a priori mpLP
theorem, not "the decisive empirical falsification" (RC5's epistemics:
no simulation budget or network choice can rescue the smooth bridge —
the correct narrative for the manuscript). (ii) The slope-1.00
statistic silently drops the sparsity: 9/76 interacting pairs, 64/76
with χ = 0 *exactly* — the sparsity *is* the CRISPRi order-swap
prediction of Theorem D, and quoting a single slope hides it (RC2).
(iii) "ε\*/σ ≈ 3–4" — measured 2.45–4.11, median 3.1. (iv) "earlier
coarser analyses overcounted events" — the census counted crossings
correctly at its resolution; what it overstated was *curvature-measure
density* (RC6's self-cancelling slivers). None of these changes
Part-1's conclusions.

---

## 3. The corrected and completed bridge (Routes 1+2, repaired and executed)

The audit's recommended combination — "prove the active-set angle
defect is the Regge curvature of a piecewise-flat metric; prove μ_σ
converges weakly to the curvature of that metric" — is the right
program with the wrong limit. Repaired, it becomes a theorem we can
actually prove in a prototype setting that is *in the same structural
class as FBA* (parametric LP, fixed constraint matrix, θ entering the
RHS affinely — the class of uptake-bound perturbation):

**Theorem B (refinement–resolution bridge; prototype proven,
machine-verified as V2).** Let f be a C² concave value function on
Θ ⊂ R² with strictly negative curvature, and for each n let Φ_n =
min_{i≤n²} ℓ_i be the parametric-LP value function given by the minimum
of the tangent planes ℓ_i of f at the points of a quasi-uniform mesh
with mesh size h_n → 0 (each Φ_n is the value function of a parametric
LP with n² constraints and θ in the RHS; the Φ_n are nested outer
approximations converging uniformly to f). Let μ_n = D²Φ_n (atomic,
supported on the codim-1 cell boundaries of the induced subdivision,
with vertex angle defects as the codim-2 layer). Then:

- **(B1) Refinement limit.** μ_n restricted to any line converges
  weakly to the smooth curvature density u^⊤∇²f u along that line;
  equivalently μ_n ⇀ ∇²f·dθ as matrix-valued measures. *Proof (one
  line at the core):* ∇Φ_n equals the slope of the active tangent
  plane, ∇Φ_n(θ) = ∇f(p_i(θ)) with |p_i(θ) − θ| ≤ C·h_n, hence
  ∇Φ_n → ∇f uniformly; by the Gauss/flux identity
  ∫_Ω dμ_n = ∮_{∂Ω} ∇Φ_n·n ds → ∮_{∂Ω} ∇f·n ds = ∫_Ω ∇²f dθ for every
  test region, which is weak convergence of the (bounded-mass,
  sign-definite) measures. ∎
- **(B2) Mass conservation.** The total curvature mass is
  n-independent: ∫ dμ_n = ∮_{∂Θ} ∇f·n ds exactly (the R4/telescoping
  analog at the family level).
- **(B3) The two-sided dial.** For the smoothed family
  μ_n,σ = μ_n ∗ φ_σ: at fixed n, σ→0 recovers the **atomic** measure
  (the audit's direction — D1); at fixed σ with h_n ≪ σ (any test
  scale L with h_n ≪ σ ≪ L_var), μ_n,σ converges to the smooth density
  φ_σ ∗ (∇²f dθ) → the joint limit exists **only through the window
  h_n ≪ σ ≪ L_var**, and the smooth object is a family member at
  matched resolution, never a σ→0 limit.

**V2 machine verification** (min-of-tangent-planes family,
f = 2 − ½|θ|² − 0.1Σθ_i⁴ — concave with non-constant curvature;
40 random cuts; exact breakpoint atoms):

| panel | result |
|---|---|
| B1 refinement (n = 4 → 128) | normalized W1 to the smooth density: **0.049 → 0.0035** (rate ≈ 0.9–1.0 in h for n ≥ 32); total-mass ratio → **1.002** (from 0.93); adaptive-scale L1: 0.33 → 0.07 |
| B3 σ→0 at fixed n = 32 | L1 distance to the smooth density: **0.054 → 1.28** as σ: 0.06 → 0.003 (departs from smooth!); mass within w = 0.01 of atom positions: 0.41 → **0.9992** — the atomic limit |
| B3 joint limit (σ = 0.05 fixed) | L1 to the smooth density: **1.25 → 0.040** (n = 4 → 128; σ/h_n = 0.075 → 3.2; residual = documented boundary/oversmoothing bias) |

The prototype carries **both** carriers of D5: along a cut the atoms
are the codim-1 layer; at the subdivision vertices the slope-jump
composition gives the codim-2 angle defects (the Regge layer of the
same complex — the Route-1 instinct, now with a real convergence
statement). Theorem B is, to our knowledge, the first *provable*
statement of the "discrete → smooth" bridge in a parametric-LP class,
and it is exactly what the audit asked for once D1's direction is
repaired.

**The honest open forms for the real-network program** (replacing the
audit's false formula):

- **Conjecture RA (refinement, real networks).** There exist
  model-family sequences (e.g., constraint families polyhedrally
  approximating smooth physiological bounds) along which the empirical
  event measures of the lex-pFBA map converge weakly. *Blocked by:*
  no known genome-scale refinement sequences; sliver cascades (RC6,
  Theorem N(iii)(a)). The near-term testable form is statistical:
  **E32 (proposed)** — over random cuts/panels (the M4b grid, the M1
  sweeps, the E24 panel), do the empirical event point measures
  stabilize in bounded-Lipschitz distance as the panel grows
  (Glivenko–Cantelli-type)? This is Route 5's mean-field instinct made
  falsifiable with existing data.
- **Conjecture SA (identification).** For a refinement sequence whose
  limit geometry is constructed *from* the viability field V, the limit
  curvature measure of RA coincides with the (smoothed) geometric
  κ_V/g^SAVGS of the manuscript. *Status:* not provable at present
  (6/6 audit consensus; D6); any claim of automatic coincidence is
  smuggled.
- **For the manuscript (fixed network):** the defensible statement
  remains the **resolution statement** (Theorem R + M4c), now
  restatable with V1's refinement: *the three κ objects are one
  curvature measure — canonical in the D²Φ carrier — at multiple
  resolutions; the dial is measured (ε\* ≈ 3σ); the unification is a
  resolution statement, not a limit statement.*

---

## 4. V5 — the audit's decisive test, executed

The audit's recommended next step 1: "Re-run E24 with the
measure-theoretic κ_flux. This is the decisive test. If the empirical
association strengthens or remains robust with the corrected metric,
the single-paper route is secure." We executed it with everything else
held fixed: the same panel (433 genes with M3D expression), the same
trajectory (the exact E22 physiology: q_glc 5.0→1.0, q_O2 22→5.0, 8
anchors), the same per-gene aggregation (max over the gene's
reactions), the same response (max |log2FC| over the four M3D
stationary carbon-exhaustion contrasts), the same statistics
(E24's corr_stats: MC permutation p, bootstrap CI, partial given
reference level, deciles). Only the predictor changed:

  E22 baseline: κ_V(r) = max_t (v_r(t) − v_r(T1))²  [displacement²]
  corrected:    κ^μ(r) = Σ_t |Δ² v_r(t)|/dt          [curvature-measure
                                                        mass, dt-normalized]

both computed on the **deterministic lex-pFBA trajectory** (the E22
physiology re-run with the lexicographic engine; 4× and 8× per-segment
refinement), with an engine control (κ_V on the same lex trajectory)
isolating the engine change from the definition change. The trajectory
is **not** event-free — total measure mass 288.77 (identical at 4× and
8× refinement, i.e., the atoms are resolved and the dt-normalized mass
is resolution-independent, exactly as Theorem S predicts), 440
reactions carrying events, max 3-point collinearity residual 0.135.

| predictor | r (nonzero panel) | n | p | Spearman (full) | partial r (given ref level) |
|---|---|---|---|---|---|
| κ_V E22 artifact (baseline) | **+0.3739** | 433 | 8.2e-16 | +0.3999 | +0.2508 (E24 record) |
| κ_V lex (engine control) | **+0.3954** | 424 | 2.6e-17 | +0.4139 | — |
| **κ^μ (measure-theoretic, max)** | **+0.3954** | 424 | 2.6e-17 | +0.4138 | **+0.2692** (p = 1.8e-8) |
| κ^μ (sum aggregation) | +0.3909 | 424 | 6.3e-17 | +0.4050 | — |

Deciles (κ^μ): top 10% mean |FC| = **1.923** vs bottom 10% = **0.890**
(MWU one-sided p = 1.3e-7) — the E24 signature (1.92 vs 0.89, 9.0e-8)
is preserved. Zero-κ^μ contrast: only 9 genes (their reactions carry
zero lex flux at all T — plain-FBA vertex noise in the E22 artifact;
mean |FC| 1.296 vs 1.319, no difference, consistent with noise).
Refinement robustness: 4× and 8× give r = +0.3954 identically.

Three findings beyond the headline:

1. **The decisive test passes with strengthening.** The
   measure-theoretic metric *increases* the association at every level
   (Pearson +0.374 → +0.395; Spearman +0.400 → +0.414; partial
   +0.251 → +0.269; p tightens by an order of magnitude). By the
   audit's own criterion, **the single-paper route is secure.**
2. **Metric invariance is itself the deeper result.**
   ρ(κ^μ, κ_V_lex) = **0.99998** — on the monotone carbon-decline
   trajectory, the curvature-measure mass and the squared displacement
   are rank-equivalent predictors (ρ(·, κ_V_E22) = +0.932 for both).
   The transcript-level association is therefore a property of the
   *event structure* along the trajectory, not of the choice between
   the time-course and curvature pictures — the two κ objects that
   Part 1 of the audit worried about reconciling are, on this
   trajectory, the same information. (They need not be on non-monotone
   paths; the invariance is a trajectory property to state, not assume.)
3. **An E22 artifact was found and documented.** The e24 CSV rounded
   κ_V to 6 decimals, zeroing the 94 tiny panel values (1e-13…1e-7)
   that E24's in-memory statistics had used (n = 433); reading the
   rounded artifact reproduces n = 339 and r = +0.380 — a
   reproducibility trap for any future re-analysis. The V5 script
   reads the unrounded E22 artifact (baseline reproduced to the digit:
   r = +0.3739, p = 8.18e-16, CI [0.2986, 0.4464]). The tiny values
   themselves are largely plain-FBA degeneracy noise (9 genes drop to
   exactly zero under the deterministic engine) — a v2-level note for
   the E22/E24 methods paragraph, and one more reason the lexicographic
   engine should be the default for every future κ computation.

**What V5 does *not* show:** it does not prove κ_flux = F[μ] as a
formal identity for the manuscript's exact definitions (still open,
now decoupled: the *association* survives the redefinition, which is
what the single-paper decision needed); and it is single-trajectory —
the PRECISE arm and matched conditions were not re-run (the primary
M3D panel is the decisive arm per E24's own design).

---

## 5. Strategic advice, evaluated

- **"A single coherent manuscript … Do not split yet" — endorsed, and
  now conditional-proof complete.** The audit's stated condition ("if
  the empirical association strengthens or remains robust with the
  corrected metric") is met by V5. The spine it proposes (discrete
  measure → κ_flux functional; Theorem R + M4c as the central
  theoretical result; M1/M3/M4 as computational validation; E24–E27 as
  the empirical association; Kochanowski as protein-layer prior art)
  is sound and matches the v2 plan; V1 adds the *canonical carrier*
  (D²Φ) and the decoupling table to that spine, and Theorem B adds
  the provable prototype that the "unification as resolution
  statement" section needs to cite.
- **Trimming the categorical/HoTT sections to an appendix — endorsed**
  (joint assessment's tiered repair program already routes them there).
- **"Defer E28 until after the metric re-definition … must be designed
  under the new (ε, σ) design law" — endorsed; nothing new needed**
  (the M4c design law is already on record; V5's metric is now also on
  record, so E28's gate is one step closer to opening).
- **v2 Layer-0 drafting (audit's next step 3) is the correct next
  deliverable** after this document: formal style rules (no diary, no
  version history, no session references), the P0 mechanical fix list
  as the entry point, Theorem B / Theorem R / V1's canonical carrier
  / V5's recalibration as the new-results sections, and the
  Kochanowski passage (verbatim as supplied) in the discussion. Not
  attempted here — it is the next turn's work, with this file and its
  artifacts as source material.
- **One internal tension in the audit worth recording:** Part 2 opens
  with "the bridging can be strengthened … but **not by more
  simulation** or terminology," yet its own next step 1 is a
  simulation. Resolved: what the bridge did not need was more *dial*
  measurements (M4c already measured the dial); what it needed — and
  what this document supplies — is the *right* theorem (Theorem B),
  the *right* decisive simulation (V5), and the corrections D1–D8.
  Simulation and theorem were both necessary; neither was sufficient
  alone.

---

## 6. Corrected bottom line (replacement text for the audit's conclusion)

> - **The bridge is not dead and not merely reformulated — it is now
>   two-sided.** On a fixed network it is a **resolution statement**
>   (Theorem R + M4c: one measure at resolution σ; dial ε\* ≈ 3σ; mass
>   conserved), with the canonical carrier being the tie-break-free
>   value measure D²Φ (V1), whose atom hierarchy is decoupled from the
>   flux-jump hierarchy. Across refinement sequences it is a
>   **provable limit statement** (Theorem B, prototype verified:
>   W1 → 0.0035, mass ratio → 1.00, joint limit through the window
>   h ≪ σ ≪ L_var) — the first provable discrete→smooth bridge in the
>   parametric-LP class.
> - **Do not write the audit's formula.**
>   κ_geom = lim_{σ→0} κ_flux ∗ φ_σ selects the atomic measure (V3,
>   V2b; Theorem N) — the limit the bridge is *not*. The smooth object
>   is a family member at matched resolution, or the weak limit under
>   refinement (Theorem B), never the σ→0 limit of a fixed network's
>   smoothed measure.
> - **The decisive test has been run and passes with strengthening**
>   (V5: r +0.374 → +0.395; partial +0.251 → +0.269; deciles
>   preserved; metric-invariant on the trajectory, ρ = 0.99998).
>   The single-paper route is secure by the audit's own criterion.
> - **Remaining open, honestly labeled:** κ_flux = F[μ] as a formal
>   identity; Conjecture RA (real-network refinement — low
>   feasibility, E32 statistical form testable now); Conjecture SA
>   (identification with g^SAVGS — not provable at present); E28 under
>   the (ε, σ) design law; E31 2D sliver census.

---

## 7. Deliverables of this evaluation

| Artifact | Content |
|---|---|
| `download/deepseek_bridge/v1_value_function.{json,csv,png}` | Route 3 corrected: Φ piecewise-affine (4.2e-13), the single value atom, cluster nets, Danskin dual-vs-FD, decoupling scatter |
| `download/deepseek_bridge/v2_refinement.{json,csv,png}` | Theorem B prototype: refinement limit (W1, mass ratio, L1), σ→0 atomicity, joint limit |
| `download/deepseek_bridge/v3_sigma_limit.{json,csv,png}` | D1 falsified on the measured M4c measure: mass collapse, wall-free decay, hat-test separation |
| `download/deepseek_bridge/v5_e24_recalibration.{json,csv,png}` | the decisive test: all four predictors, partial, deciles, zero contrast, predictor agreement, refinement robustness |
| `scripts/deepseek_route_verify.py` | V1 + V2 + V3 (reuses `lp_engine.py`; frozen v21 untouched) |
| `scripts/e24_measure_kappa.py` | V5 (reuses the E24 protocol and artifacts; documents the E22 CSV rounding trap) |
| this file | the evaluation |
