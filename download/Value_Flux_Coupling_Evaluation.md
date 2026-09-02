# The Value–Flux Coupling: Evaluation of the Follow-up Audit Round

**Target:** the follow-up external audit ("Weaknesses / remaining open
issues" + "Advice for next steps" + "Bottom line", received 2026-09-02).
This audit reviews the previous round's repairs (the two-layer
structure, the κ^μ misattribution correction, the GPR caveat) and
demands: resolve the value–flux layer relation, resolve the OR/max GPR
concavity break, decide which curvature layer carries the biological
association — before any Layer-1 porting.

**Machine batteries (this round):**
- `scripts/alexandrov_coupling_verify.py` (AX-8a/8b/8c, AX-9, AX-10) →
  `download/alexandrov_bridge/{coupling_results.json,
  coupling_summary.txt, coupling_figures.png}`
- `scripts/e24_layer_decision.py` (V6, the audit's requested direct
  computation) →
  `download/deepseek_bridge/v6_layer_decision.{json,csv,png}`

**Standing instructions honored:** verify, do not trust; evaluate
jointly with the six-audit corpus; strengthen, correct, complete weaker
suggestions before implementing; v21 frozen; every claim below carries
a machine dossier.

---

## 1. Executive verdict

The audit's three "weaknesses" are all real, all resolvable, and the
resolution is **stronger than the audit's own suggestions** in each
case. The centerpiece is a new exact theorem (Theorem C below) that
closes the "most critical theoretical gap" the audit names: the value
layer and the flux layer are linked by an *identity*, not by a
proportionality or a rank agreement. One of the audit's suggested
repairs (semiconvexity for OR GPRs) is **false as stated** — and is
repaired into a strictly stronger statement (a signed Hessian layer
that needs no convexity at all). One of its two conjectured forms of
the layer relation ("trace of the Hessian over active reactions") is
**false**, and the other ("MA atom = product of codim-1 jumps") is
**false in general and off by a factor ≥ 2** — both are replaced by
the correct formulas. The layer decision is then settled by the direct
computation the audit demanded (V6), with an outcome sharper than the
audit anticipated: on the E24 trajectory the value layer carries
**zero network events** (the path stays in one chamber of Φ; all four
value kinks are artifacts of the piecewise-linear trajectory design),
so the association *must* and *does* live on the flux layer —
r = +0.395 (n = 424, partial +0.269) versus null arms for every
value-layer attribution (0/433 genes; 51 genes at r = +0.032).

| # | Audit item | Verdict | Machine evidence |
|---|---|---|---|
| W1 | Value–flux layer relation unresolved ("most critical theoretical gap") | **RESOLVED by Theorem C** (exact identity D²Φ = cᵀ D²v*, per-crease ΔΦ′ = cᵀΔv′), strictly stronger than the requested proportionality/rank-equivalence | AX-8a: toys exact (0.0); 150 random LPs: max identity err 1.05e-13; degenerate family 60/60, err 2.0e-13; AX-8b: 2-D mixed differences, err 6.4e-16; AX-8c (iML1515): **err 0.0 at all 12 events and all 4 clusters**; V6: err 0.0 at all kinks |
| W2 | OR/max GPR concavity break; three strategies proposed | **RESOLVED with correction.** The audit's preferred option (c) — "the value function is semiconvex and Alexandrov extends to semiconvex functions" — is **FALSE as a hypothesis**: a continuous PWL function is semiconvex iff it is convex (Proposition S). But the *intended conclusion* is true for free: every continuous PWL Φ (any GPR structure) carries a finite **signed** crease measure; concavity is needed only for the Monge–Ampère layer. Option (a) (AND-only restriction) is valid but unnecessarily weak; option (b) (regularization) is subsumed by the Theorem B′ resolution layer | AX-10: λ·h_max ≡ 0.500 (no finite semiconvexity constant at any scale); crease A PSD {0, √2} vs crease B NSD {−1, 0} — genuinely signed; AND concave-only / OR convex-only / SUM affine / OR+cap **neither**; disaggregation divergence 1 vs 2 |
| W3 | Two-layer structure: which layer for the biological association? | **DECIDED by direct computation (V6).** On the E24 trajectory: **0 interior value kinks** (single chamber, μ = Y·q_glc, Y = 0.099544 constant; uptake shadow prices jump by exactly 0); value/flux strain ratio 1.45e-3; c-attribution arm **0/433 genes**; dual arm 51 genes, r = +0.032 (null); flux layer r = +0.3954, partial +0.2692 | V6 artifacts; the 12-vs-1 decoupling of V1 now measured in slope-jump units (AX-8c: invisible L1 jumps up to 1.6e4 vs \|cᵀΔv′\| ≤ 1.5e-7) |
| A1 | Make the ρ(κ^μ, κ_lex) = 0.99998 relation explicit | **Corrected (second time).** The rank identity is a *within-flux-layer* trajectory-consistency statement (κ^μ and κ_V_lex both sample the same lexicographic flux trajectory), **not** a value↔flux equivalence. The cross-layer relation is Theorem C. Reproduced: ρ = 0.99999 | V5/V6 predictor agreement; V1 decoupling |
| A2 | Address OR/max directly (three options) | Evaluated in full (see W2): (a) unnecessarily weak; (b) subsumed; (c) false-as-stated, repaired to a stronger signed layer | AX-10 |
| A3 | "Test both [layers]. This needs direct computation." | **EXECUTED (V6):** both value-layer attribution arms degenerate or null; the flux layer is the sole carrier | V6 |
| A4 | Port Layer-1 only after the metric is settled | **Metric settled:** κ^μ := the per-reaction total variation of the crease measure of the lex-optimal flux map (Layer A), with Theorem C as its exact bridge to the value layer. Porting may proceed | this document; v2 [D4] |
| A5 | Attack Conjecture A6 ("flux-strain = trace of the Hessian over active reactions" or "MA atom = product of codim-1 jumps") | **Both conjectured forms FALSE; both repaired to exact statements.** The coupling is the **objective contraction** cᵀ D²v* (not a trace — the trace fails whenever objective-inactive reactions reroute, which is 11 of 12 V1 events); the MA atom is the **determinant** ½\|det(j₁, j₂)\| = ½\|j₁\|\|j₂\| sin∠ (the product overestimates by 2/sin∠ ≥ 2, with equality iff the jumps are orthogonal) | AX-8c (11/12 c-orthogonal); AX-9 (400 vertices: det = hull to 8.9e-16; product/atom median 3.296, min 2.000; 2/sin law to 2.5e-12; orthogonal case exactly 2) |
| A6 | Keep application framing | **Endorsed, unchanged.** Theorem C is supporting method: an elementary identity (Φ = cᵀv* pointwise) plus a regularity lemma; it must not be oversold | — |

---

## 2. The mathematics, stated precisely and proved

### 2.1 Theorem C (value–flux crease coupling) — closes W1/A1/A5

**Setup.** Φ(θ) = max{cᵀv : Sv = 0, ℓ(θ) ≤ v ≤ u(θ)} with ℓ, u
continuous piecewise affine in θ (any GPR structure after resolution:
a min/max tree of affine leaf functions is PWL, and on each GPR cell
the bounds are affine). Let v*(θ) be any *continuous piecewise-affine
optimal selection* (e.g. the three-stage lexicographic selection).

**(i) Identity of measures.** Φ = cᵀv* pointwise, hence
distributionally
  D²Φ = Σ_r c_r D²v*_r
as symmetric matrix-valued signed Radon measures on the parameter
domain. Along any parameter path θ(t) (itself PWL, as the E22
trajectory is), at every crease time t_k:
  ΔΦ′(t_k) = cᵀ Δv′(t_k),   Δv′ = slope jump of v*(t).

**(ii) Bound.** |ΔΦ′(t_k)| ≤ ‖c‖_∞ ‖Δv′(t_k)‖₁: the flux strain at an
event bounds the value strain.

**(iii) Visibility dichotomy (new).** An event with unique optima on
both sides is a *transversal optimal-vertex switch* and is necessarily
objective-moving (cᵀΔv′ ≠ 0, because the objective difference of the
two vertices crosses zero transversally). Objective-invisible events
(cᵀΔv′ = 0, Δv′ ≠ 0) are therefore exactly the *degenerate*
reroutings inside a ≥ 1-dimensional optimal face — the mask-type
events of M1/V1. **The tie-break sensitivity of the flux layer is
concentrated precisely in the invisible events**, which is why the
c-contraction (the value layer) is tie-break-free: it annihilates the
degenerate layer's arbitrariness.

**(iv) Sparse-objective corollary (FBA).** With c = γ e_bio (the
standard sparse objective), D²Φ = γ D²v*_bio: *the value layer is the
crease measure of the single biomass component*. Per-gene attribution
from the value layer is then structurally impossible (the biomass
pseudo-reaction carries no GPR), and every other component's events
are c-orthogonal.

*Proof of (i).* Φ = cᵀv* holds pointwise by optimality; both sides are
continuous PWL, and differentiation of distributions is linear: D² of
the identity gives the measure identity, whose restriction to a crease
facet gives the displayed per-crease form. The regularity input is the
lex-selection lemma: the lexicographic optimal solution of a
parametric LP with PWL data is continuous PWL (its graph is a
polyhedron in (v, θ)-space — each lexicographic stage adds the graph
of a PWL value function, which is polyhedral; an injective polyhedral
projection is PWL). This regularity is *measured*, not assumed:
segment residuals ≤ 8 × 10⁻¹⁴ (M1), Φ piecewise-affine at
4.2 × 10⁻¹³ (V1). ∎

*Machine dossier.* AX-8a: two exact toys (objective-moving event:
ΔΦ′ = −0.300000 = cᵀΔv′ to 0.0; mask-type event: flux jump 0.8 with
cᵀ jump = ΔΦ′ = 0.0 under both tie-breaks — the kink present only
under min|y|, absent under max y, the value identical); 150 random
dense-c LPs: 5 events, all objective-moving (dichotomy), max
|ΔΦ′ − cᵀΔv′| = 1.05 × 10⁻¹³; degenerate follower family: 60/60 trials
with an invisible kink, max identity error 2.0 × 10⁻¹³. AX-8b (2-D):
400 mixed second differences at crease-straddling boxes, max error
6.4 × 10⁻¹⁶. AX-8c (iML1515, the V1/M4c cut, sparse objective):
**identity error 0.0 at all 12 events and all 4 event clusters**;
Φ = cᵀv* to 1.0 × 10⁻⁹ (the engine's stage-1 pin tolerance);
11 of 12 events invisible with flux L1 slope jumps up to 1.6 × 10⁴
against |cᵀΔv′| ≤ 1.5 × 10⁻⁷. V6 (iJO1366, E24 trajectory): identity
error 0.0 at all kinks.

### 2.2 Proposition S (semiconvexity collapse) — repairs W2/A2

A continuous piecewise-affine f is λ-semiconvex (resp. semiconcave)
for some finite λ **iff** f is convex (resp. concave).

*Proof.* If f is semiconvex, D²f + λI·Leb ⪰ 0 as symmetric-matrix
measures. For continuous PWL f, D²f is supported on the codim-1
skeleton, so it is purely singular with respect to Lebesgue; testing
on skeleton sets forces the singular part itself PSD, hence D²f ⪰ 0,
hence f is convex (mollify: D²(f*ρ_ε) = D²f*ρ_ε ⪰ 0; uniform limits
of convex functions are convex). ∎

**Consequences.**
1. The audit's suggestion (c) — "for OR GPRs the value function is
   semiconvex" — is *vacuous as a hypothesis*: for the PWL value
   functions of LPs, semiconvexity is not weaker than convexity. The
   OR counterexample (Φ(1,0) = Φ(0,1) = 1, Φ(½,½) = ½) is not
   semiconvex, not semiconcave, and no finite λ rescues it
   (AX-10: λ·h_max ≡ 0.500 across λ = 1 … 10¹² — the required
   constant blows up like 1/(2h) at every scale).
2. The *intended conclusion* holds without any convexity: every
   continuous PWL Φ carries a finite **signed** symmetric
   matrix-valued Radon measure D²Φ supported on the crease skeleton
   (elementary distribution theory; no Alexandrov needed at PWL
   regularity). The OR+cap value function Φ_sat = min(max(θ₁,θ₂),K)
   — neither convex nor concave — has crease densities with **both
   signs**: the diagonal crease is PSD (eigenvalues {0, √2}), the cap
   crease is NSD ({−1, 0}).
3. What concavity is genuinely needed for: (i) positivity of the
   measure (curvature-mass interpretation); (ii) the Monge–Ampère
   layer (det D²(−Φ) as codim-2 atoms = normal-fan volumes; requires
   the monotone gradient of a convex function); (iii) the dual-face
   identity (Prop A3 of the previous round). The manuscript strategy:
   **signed Hessian layer for all genes and GPRs; MA layer restricted
   to the concave class** (single-gene axes, exchange-bound families,
   AND-only subnetworks — exactly the classes the executed program
   uses); OR-containing compound GPRs flagged per reaction.
4. The audit's option (a) (AND-only restriction) is therefore valid
   but unnecessarily weak; option (b) (regularized perturbation) is
   subsumed: any C² mollification is simultaneously semiconvex and
   semiconcave, and the signed crease measure is recovered as its
   weak limit — this is precisely the Theorem B′ resolution layer,
   which already exists in the manuscript.
5. **Disaggregation caveat (completed).** Modeling isozymes as
   *separate reactions* (the iML1515/iJO1366 convention for pfkA/pfkB,
   acnA/acnB, …) restores affine bounds and concavity — but it
   silently replaces max-semantics (substitutable isozymes, capacity
   = max) with sum-semantics (additive capacities): at full
   expression the disaggregated object doubles the capacity
   (measured: Φ_or(1,1) = 1 vs Φ_sum(1,1) = 2). Convexification here
   is *not* a regularization of the same object; it is a different
   biological model. The manuscript must say which semantics it uses.

### 2.3 Proposition M (MA atom = determinant, not product) — repairs A5

For f convex PWL on R² at a generic vertex with incident gradients
n₁, n₂, n₃ (the normal fan), the Monge–Ampère atom is
  det D²f({vertex}) = area conv{n₁,n₂,n₃}
                   = ½ |det(j₁, j₂)|,
                   j_i = codim-1 gradient jumps,
while the audit's conjectured product |j₁| · |j₂| overestimates by
  product / atom = 2 / sin∠(j₁, j₂) ≥ 2,
with equality iff the two jumps are orthogonal. In p dimensions the
generic statement is atom = (1/p!)|det(j₁,…,j_p)| for simplex fans
(and the polytope volume of the fan in general). *Machine dossier*
(AX-9, 400 three-fan vertices from random max-of-affine): det formula
= hull area to 8.9 × 10⁻¹⁶; product/atom ratio median 3.296, min
2.000 (the orthogonal edge case lands at exactly 2.000000); the
2/sin∠ law holds to 2.5 × 10⁻¹²; the atom is constant under
ε-shrinking of the gradient image at scales 10⁻³ and 10⁻⁴.

### 2.4 The GPR concavity classification (completed form of D-C)

Under multiplicative activity scaling v_r ∈ a_r(θ)·[ℓ_r, u_r] with
ℓ ≤ 0 ≤ u: Φ(θ) = Ψ(a(θ)) where Ψ is concave (LP duality: the bound
map a ↦ (a⊙u, a⊙l) is affine and the LP value is concave in the
bounds) and nondecreasing (interval nesting). Hence: all a_r concave
(min-trees, AND-only) ⇒ Φ concave; any top-level max node (OR) ⇒ Φ
can fail concavity (canonical counterexample, measured violation
0.51); composed with a viability cap, min(max(·),K) ⇒ **neither**
(violations −0.28 and −0.27). All four classes are machine-classified
in AX-10 with LP realizations; in every case Φ remains continuous PWL
with a signed crease measure.

---

## 3. The layer decision (V6) — the audit's direct computation, executed

Design: V5 frozen verbatim (engine, seed 20240901, iJO1366, E22
physiology, 8× refinement = 57 points, panel, response, statistics);
only the predictors are extended. Arms:

| Arm | Layer | n nonzero | Pearson r (nonzero) | partial r \| ref level |
|---|---|---|---|---|
| A κ^μ (flux strain, all events) | flux (Layer A) | 424 | **+0.3954** | **+0.2692** (p = 1.8e-8) |
| B1 κ^vg (flux strain gated to value-kink times) | flux @ value times | 424 | +0.3954 | +0.2692 |
| B1b κ^vg interior kinks only | flux @ chamber crossings | **0** | degenerate | — |
| B2 κ^c (c-attribution of the value strain) | value (Theorem C) | **0** | degenerate | — |
| B3 κ^dual (shadow-price jump attribution) | dual/MA shadow | 51 | +0.0319 | −0.0127 (p = 0.93) |
| κ_V_lex (V5 engine control) | flux | 424 | +0.3954 | — |

**Structural findings.**
1. **The value layer has zero network events on this trajectory.** 0
   interior (chamber-crossing) value kinks; the path is entirely
   glucose-limited: μ(t) = Y·q_glc(t) with Y = 0.099544 gDW/mmol
   constant to 6 digits across all kinks, and the uptake shadow prices
   (y_glc, y_o2) jump by exactly 0 at every kink. All 4 detected value
   kinks sit at the 7 anchor corners of the piecewise-linear
   trajectory design and have magnitudes exactly
   ΔΦ′ = Y·Δ(dq_glc/dt) — path-design artifacts, present in any affine
   chamber, carrying no network structure.
2. **Value/flux strain mass ratio 1.45 × 10⁻³** — the V1 decoupling
   (12 vs 1; ratio 1.7 × 10⁻⁶ on the M4c cut) reproduced on the E24
   trajectory.
3. **The coupling identity holds at machine precision on the real
   trajectory** (error 0.0 at every kink; Theorem C).
4. **The c-attribution arm is structurally empty** (0/433 genes): the
   sparse FBA objective supports the value strain on the biomass
   pseudo-reaction alone, which carries no GPR — per-gene attribution
   from the value layer is impossible, exactly as the
   sparse-objective corollary predicts.
5. **The dual arm is null** (51 genes, r = +0.032, partial −0.013):
   the full bound-marginal jumps (71–197 reactions per kink) are
   internal basis changes — dual-side *flux*-layer structure — and do
   not associate with transcriptional response.
6. **B1 ≡ A exactly (433/433 genes)**: every gene's flux-strain
   maximum is attained at a value-kink time (an anchor corner) on this
   trajectory. Gating on the value layer's event set therefore costs
   nothing here — but that is a property of the trajectory design
   (anchor rerouting dominates the per-gene maxima), not evidence of
   value-layer content; the interior-only gate (the honest
   network-event gate) is empty.
7. **ρ(κ^μ, κ_V_lex) = 0.99999** (the V5 rank identity, reproduced):
   a within-flux-layer trajectory-consistency statement.

**Verdict.** The audit's prediction — "the V1 decoupling suggests the
value-function measure may be too coarse; the flux-strain measure may
capture more biological signal" — is confirmed in the strongest
possible form: on the E24 physiology the value layer is not merely
coarse, it is *structurally empty* of per-gene network events, and the
entire association (r = +0.395, partial +0.269) lives on the flux
layer, which Theorem C identifies as the primal object whose
objective contraction is the value measure. The empirical metric is
now justified *by theorem*, not by rank agreement.

---

## 4. What the audit gets right (kept)

1. **The prioritization is correct**: the value–flux relation is the
   critical gap; W1 is resolved first and it subsumes W3.
2. **The three GPR strategies are the right option space**; the audit's
   instinct that option (c) "may resolve the issue elegantly" was
   directionally right — the signed-measure extension is the answer —
   but the mechanism is not semiconvexity (false for PWL) and requires
   no extension of Alexandrov at all.
3. **"Needs direct computation" was right**: V6 produced a decision,
   and a sharper one than the theory alone (the single-chamber
   structure of the E24 path was not predicted by us in advance).
4. **The porting discipline (A4) is sound** and has been followed: the
   metric is settled before Layer-1 porting; this round changed only
   [D4]-level definitions, results, and the resolved conjecture in the
   v2 skeleton.
5. **The application framing (A6) is endorsed** and unchanged; the
   framing sentences adopted last round stand.

---

## 5. Manuscript integration (v2 Layer-0 edits; v21 untouched)

1. **§3 new subsection [D4] "The value–flux coupling"** after [D3]:
   the lex-selection regularity lemma (with the measured residuals),
   Theorem C with parts (i)–(iv) (identity, bound, visibility
   dichotomy, sparse-objective corollary) and its machine dossier;
   Proposition S with the λ·h ≡ 0.500 table and the signed
   crease-density eigenvalues; Proposition M with the determinant law
   and the 2/sin∠ bound; the disaggregation caveat sentence.
2. **Conjecture conj:valueflux is resolved and replaced**: the
   conjecture block becomes Theorem C plus a corollary stating the
   decoupling (11 of 12 V1 events c-orthogonal; invisible L1 jumps up
   to 1.6 × 10⁴ vs |cᵀΔv′| ≤ 1.5 × 10⁻⁷). The *conjectured direction*
   ("the event structure of v is bounded by the facet structure of Φ")
   was one-sided and is reversed: value events ⊆ flux events, never
   the converse; E-V1's cross-reference updated.
3. **§5 [E-V1] block**: add the AX-8c coupling numbers (identity error
   0.0 at all events/clusters; Φ = cᵀv* at 1.0 × 10⁻⁹; the 11
   invisible events with L1 slope jumps up to 1.6 × 10⁴).
4. **§6 new [E-V6] subsection** (layer decision): the arm table, the
   single-chamber law (Y = 0.099544; zero uptake-dual jumps), the
   value/flux ratio 1.45 × 10⁻³, the B2/B3 nulls, and the B1 ≡ A
   coincidence with its honest interpretation.
5. **[D2] remark**: one sentence added — κ^μ's per-reaction masses are
   the components of the flux-layer crease measure whose c-contraction
   is D²Φ (Theorem C); the metric is the primal layer of the canonical
   object.
6. **prop:alex caveat sentence** extended: OR-containing compound GPRs
   enter the signed Hessian layer (all genes) with the MA layer
   restricted to the concave class; disaggregated isozyme models are
   affine but change semantics (max → sum).
7. **Discussion**: the open item "the formal identity κ_flux = F[μ]"
   is closed by Theorem C (it was decoupled from the empirical
   association by the metric-invariance result; it is now *also*
   structurally resolved); the remaining open items are unchanged.

---

## 6. Reproducibility

- `python3 scripts/alexandrov_coupling_verify.py` (≈ 3 min; scipy
  HiGHS + cobra/iML1515; deterministic seed 20260902; 55 lex solves on
  the M4c cut) → `download/alexandrov_bridge/coupling_*.{json,txt,png}`.
- `python3 scripts/e24_layer_decision.py` (≈ 30 s; iJO1366; seed
  20240901) → `download/deepseek_bridge/v6_layer_decision.*`. M3D
  compendium re-provenance: the 117 MB tarball was re-downloaded from
  the URL in `data/m3d/README.md` and the sha256 matched the committed
  manifest (e73088f7…) before extraction.
- Cross-references: `download/Alexandrov_Bridge_Evaluation.md`
  (previous round: C1–C9, A1–A6, novelty dossier),
  `download/TheoremB_Verification_and_Strengthening.md` (Theorem B′ —
  the resolution layer that subsumes the "regularized perturbation"
  option), `download/deepseek_bridge/v1_value_function.json` and
  `v5_e24_recalibration.json` (the V1/V5 evidence this round
  re-measures and explains).

**Bug honesty note.** Two of this round's own defects were caught and
repaired before recording results: (a) the first version of the
c-orthogonal toy was accidentally degenerate (its "unique optimum"
analysis was wrong — the optimal face was 1-dimensional; this failure
*became* the visibility dichotomy, so the bug was productive); (b) the
AX-8b crease-detection gradient used a scalar/slice indexing error
(`gg1[2]` for `gg1[2:]`) that produced divide-by-zero noise in the
detector while leaving the identity check itself valid (it was fixed
and the check re-run). The V6 atom flag initially counted FD noise as
value atoms; it now uses the V1 resolution-floor threshold.
