# Evaluation of the "Root Cause" Analysis — Verified, Corrected, and Extended by M4c

**Document status.** This is the evaluation of the "Root cause: the
bridge weakened because it was built on the wrong order of smoothness"
analysis supplied in the current turn (the retrospective reading of the
M4a/M4b record). Mandate: evaluate, verify, explore. Every verdict is
grounded in the committed record — M1, M3/M3b, M4a, M4b, the Active-Set
Bridge v2 theorem set (Theorems S/G/N1/N/D, `download/
Active_Set_Bridge_v2.md`), and the new measurement **M4c** executed for
this document (`download/m4/m4c_*`, `scripts/m4c_regime_dial.py`). The
frozen v21 manuscript is untouched; this file is source material for
`journal_manuscript_v2+`. Standing instructions honored: push check
first (all prior work already on `origin/main` at `8403b7d`; nothing
unpushed), commit and push at the end, English response.

---

## 0. One-paragraph verdict

The text's **diagnosis is correct and important**: the smooth bridge
failed because the FBA flux map is continuous and piecewise affine, so
its singularities are first-order kinks, while the bridge assumed a
smooth manifold whose holonomy is second-order. That diagnosis is now
theorem-backed, not merely measured. But the text **misdescribes the
measured objects in three ways** (an "O(ε) holonomy" does not exist in
any layer; the slope-1.00 statistic is drawn from a 9-of-76 interacting
stratum, not from 76 pairs; the slope-1 law is a *dynamic*-layer result
that cannot support the *static* discrete bridge), and its constructive
program **understates what is already proven** while leaving its own
central concept — "treat the smooth geometric κ_V as a separate regime"
— unmechanized. This document corrects the three misdescriptions and
closes the gap: **Theorem R (below) + M4c give the separate regime a
mechanism, a law, and a measured crossover.** The root-cause text is
best read as a correct popularization of the v2 record with three
technical slips and one missing theorem.

---

## 1. Claim-by-claim verification against the record

| # | Root-cause text claim | Record | Verdict |
|---|---|---|---|
| 1 | Bridge assumed smooth map; holonomy O(ε²) is curvature | deepseek formulation A4 + display `lim (1/ε²)(H−I) = Ω` | **True** (that is what was assumed) |
| 2 | v(θ) is continuous and piecewise affine; derivative jumps at active-set events | Theorem S(i); M1: affine segments ≤ 8e-14 rel. on all 12 sweeps; mpLP chamber theory (Gal–Nedoma 1972; Bemporad et al. 2002) | **True, verified** |
| 3 | Derivative jump is a first-order singularity | Theorem S(ii): D²v is a measure on codim-1 interfaces | **True** |
| 4 | "Holonomy that scales as O(ε)" | **No such object.** Static state holonomy ≡ I exactly (m4b `state_holonomy_note`; Theorem S(v)); codim-2 defect is O(1) and scale-invariant (−7.1469°, −23.9087°, +0.0104° at δ and δ/2); the O(ε) objects are the second-difference measure mass and the dynamic commutator χ (Theorem D) — hysteresis, not holonomy (release identity 6/6 bit-exact) | **Wrong object — see RC1** |
| 5 | "M4a measured exactly that: 76 pairs: the observed slope was 1.00, not 2" | M4a: 76 pairs × 6 depths; **64/76 χ = 0 exactly at every depth**; 9 nonzero pairs, slopes 0.857–1.244 (median 0.998); 3 near-floor insufficient; χ = sequential L1-MOMA open-path commutator | **Number right, description wrong — see RC2** |
| 6 | "The proposed smooth curvature bridge is falsified" | Theorem N: the (1/ε²)(H−I) limit is 0 at generic points and divergent on C⁽ᵖ⁻²⁾; slope-1 dynamic law | **True, and theorem-backed** |
| 7 | FBA map lives on a stratified polyhedral complex; geometry of PA maps with kinks | Theorem S; 24 operational chambers in the (glc,O₂) plane | **True** |
| 8 | Curvature not a smooth density; concentrated on strata, especially codim-2 | Two distinct carriers: D²v measure on **codim-1** (M1's object); angle **defect** at codim-2 (Theorem G); related by discrete structure equations, not identical | **Imprecise — see RC4** |
| 9 | "Holonomy can be first-order in loop size" | Defect is O(1)/scale-invariant; state holonomy exactly trivial; dynamic χ is O(ε) but is not a loop holonomy | **False — see RC1** |
| 10 | Correct Gauss–Bonnet analogue = discrete angle defect | Theorem G(ii): unfolding transport = −defect to 1e-14 on synthetic cones (incl. 190.6°); discrete GB via Regge unfolding; **plus** the exact measure identity μ(Q) = ΔᵢΔⱼv (Theorem S(iii)) is a second, trivially exact GB-type statement the text omits | **True for the graph geometry** |
| 11 | M4b's dense wedge-fan where curvature concentrates = piecewise-flat singular space behavior | Edge census: 9–10 boundary crossings/cell (up to 4 per edge) in the overflow corner vs exactly 2 in flat cells; M4c refinement: the fan contains sub-resolution sliver chambers (width 2.4e-6, jump pair ±1884.6, **net 8.9**) that largely self-cancel in the measure | **True, with a refinement — see RC6** |
| 12 | Correct bridge: discrete connection on stratified space; "holonomy and curvature are singular, first-order objects" | Discrete connection exists (unfolding transport, Theorem G — the projection transport of the file's own Fix 4 is *not* a connection, v2 C3); its curvature (defect) is singular **O(1)**, not first-order | **Half-right — see RC1/RC4** |
| 13 | Cannot unify by proving FBA metric converges to smooth κ_V; strong claim off the table | Theorem N (atomicity obstruction); 6/6 audit consensus "strong form not provable" | **True** |
| 14 | Program step 1: define a discrete curvature from active-set structure | Done: Theorem S (jump measure) + Theorem G (defect measure), machine-verified | **Already executed (v2)** |
| 15 | Program step 2: show κ_flux is a discretization of *this* discrete curvature | Partially: M1 D2 mass 0.934–1.0 on active-set events; M3 footprint Spearman 0.865; the formal identity κ_flux = F[μ] is not yet written as a theorem | **Open (flagged)** |
| 16 | Program step 3: treat smooth κ_V as conceptual ancestor or separate regime | v2 constructs the geometry intrinsically (C4/Theorem G); **this document adds the mechanism and law of the regime (Theorem R + M4c)** | **Now executed (M4c)** |
| 17 | Program step 4: κ_time = integrated squared displacement along a path through the discrete curvature structure | Theorem S(iv): κ''(t) = 2‖v'‖² + signed event measure; the E24-style object is an *integral* of the event measure; **M4c adds the (ε, σ) design constraint for E28** | **Already executed (v2), extended here** |
| 18 | "A discrete stratified bridge… may already be partially proven by M4's slope-1 law and the no-loose-kinks lemma" | N1 is proven and supports the static picture; the slope-1 law is a **dynamic**-layer result, statistically independent of the static epistasis (Spearman(χ,|ε_ij|) = −0.347 full panel, −0.07 non-SL, p=0.43) | **Misattribution — see RC3** |
| 19 | Bottom line: do not connect FBA metric to smooth κ_V; promote the discrete curvature object as the genuine bridge | Correct direction; incomplete statement — the connection that *does* exist is coarse-graining (Theorem R), and it is measurable | **Replaced by §6** |

---

## 2. What the text gets right (verified)

1. **The root cause.** The order-of-smoothness mismatch is the actual
   reason the ε² bridge failed. This is now established at three
   levels: a priori theory (mpLP: the optimizer of a parametric LP
   under a fixed tie-break is PA on a finite polyhedral complex — the
   smoothness assumption was inadmissible from the start), machine
   measurement (M1: piecewise-affine to 8e-14 between events; D2 mass
   0.934–1.0 on active-set events), and theorem (v2 Theorem N: no
   renormalization of the static holonomy yields a finite nonzero ε²
   limit).
2. **The falsification verdict.** The smooth bridge is false, and not
   because the computations were wrong — because the mathematical
   object is different. Agreed, and strengthened: the falsification is
   model-independent (it follows from LP structure, not from any
   particular network), so no better simulation can rescue it.
3. **The discrete bridge direction.** "A different, more appropriate
   bridge almost certainly exists — but it is discrete, not smooth" is
   exactly the v2 position, now with a constructed connection
   (unfolding transport), a proven no-loose-kinks lemma, measured O(1)
   defects, and the active-set skeleton as substrate.
4. **The Gauss–Bonnet instinct.** For the graph geometry the discrete
   angle defect is the right GB analogue (Theorem G, verified to 1e-14
   on synthetic cones, scale-invariant defects on iML1515).
5. **The four-step program.** All four steps are the right program —
   and steps 1, 2 (empirically), and 4 were already executed by the v2
   record; step 3 is completed by this document (Theorem R + M4c).

---

## 3. Corrections (RC1–RC6)

**RC1 — There is no "holonomy that scales as O(ε)"; the layer
scalings form a trichotomy, and each object has its own.**
In the executed record:
- *Static state holonomy* (v around a closed loop): **exactly the
  identity**, for every loop, at every scale — v is a single-valued
  function (m4b `state_holonomy_note`; Theorem S(v); v2 C1).
- *Static defect holonomy* (unfolding transport around a codim-2
  vertex): **O(1), scale-invariant** — −7.1469° and −23.9087°
  reproduced to four decimals at loop radius δ and δ/2. This is the
  Regge/angle-defect behavior the text itself invokes — which
  *contradicts* its own "first-order holonomy" claim two paragraphs
  earlier.
- *Dynamic commutator* χ (sequential L1-MOMA, the object M4a actually
  measured): **O(ε), slope ≈ 1** — but it is the hysteresis of greedy
  adjustment, not a connection holonomy: single releases are bit-exact
  identities (6/6), so the closed-loop non-return is irreversibility
  of the dynamics (Theorem D).
- *Second-difference measure mass* D(ε) = μ([t₀−ε, t₀+ε]): **O(ε)**
  for ε above the smoothing scale — the static first-order object.
The sentence "the result is holonomy that scales as O(ε), not O(ε²)"
should read: *the mismatch objects (curvature-measure mass; dynamic
commutator) scale as O(ε), the genuine defect holonomy is O(1)
scale-invariant, and the state holonomy is exactly trivial.* The
distinction is not pedantry: it determines what experiment can detect
each object (loop compositions for defects; second differences for
measure mass; order-swap protocols for χ), and the text's own program
depends on exactly these detection channels.

**RC2 — "76 perturbation pairs: the observed slope was 1.00" describes
9 of them.** The M4a census: 64/76 pairs (84%) have χ = 0 **exactly**
at all six depths (the decoupled stratum: the two knockdowns do not
interact through the tangent cone); 9 pairs scale with slopes
0.857–1.244 (median 0.9982: sdhD+nuoG 0.9982, sdhD+nuoH 0.9982,
gapA+atpC 1.2439, atpD+nuoJ 0.9982, ptsH+gapA 1.0049, atpH+nuoM
0.9982, aceE+cyoC 0.9759, zwf+gnd 0.8573, pgi+zwf 1.0026); 3 are
near-floor. The bimodality {exactly 0, slope ≈ 1} is itself a finding:
first-order non-commutativity is **sparse and structural**, confined to
the non-decoupled stratum — quoting a single slope hides the sparsity
that the CRISPRi order-swap prediction (Theorem D) actually forecasts.

**RC3 — The slope-1 law cannot support the static bridge.** The text
writes that the discrete bridge "may already be partially proven by
M4's slope-1 law and the no-loose-kinks lemma." N1 (no loose kinks) is
proven and does support the static stratified picture. But the slope-1
law is a property of the **dynamic layer** (sequential adjustment), and
M3b measured its independence from the static-layer epistasis on the
same pair panel: Spearman(χ, |ε_ij|) = −0.347 (p = 6.8e-6) over the
full panel, −0.07 (p = 0.43) within non-synthetic-lethal pairs. The
optimum-level non-additivity and the transient-level
non-commutativity are distinct signatures (v2 C5); evidence for one is
not evidence for the other.

**RC4 — "Curvature concentrated … especially codim-2 corners"
conflates the two carriers.** The static curvature of the FBA map is
carried by **two distinct singular objects**: the Jacobian-jump
measure D²v supported on **codim-1** interfaces (M1's object: the
"distributional second derivative … Dirac measures supported on
active-set interfaces" that the deepseek formulation itself states),
and the angle-defect measure supported on **codim-2** crossings
(Theorem G). They are related by discrete structure equations (the
dihedral kinks of incident faces determine the vertex defect through
the unfolding composition) but they are not the same object, live on
different strata, and are detected by different experiments. M4c adds
the next level of the hierarchy: *within* a codim-1 wall cluster there
are sub-resolution sliver chambers (RC6) — the fine structure is atomic
at multiple scales, which is precisely Theorem N's content.

**RC5 — "Falsified" is the right conclusion with the wrong epistemics.
** The piecewise-affine structure of the lex-pFBA optimizer is an a
priori theorem of multiparametric LP (Gal–Nedoma 1972; Bemporad–
Borrelli–Morari 2002 and the mp-control literature thereafter). The
smoothness assumption was therefore never admissible: M4a's slope-1,
M1's D2 concentration, and M4b's chambers *confirm* the theorem's
structure at machine precision rather than discovering a failure.
This matters for the manuscript narrative: the result is robust and
model-independent — no simulation budget or network choice can rescue
the smooth bridge — and the correct citation frame is mpLP theory plus
Theorem N, not an empirical surprise.

**RC6 — The wedge-fan is operationally dense but measure-tame at fine
scale.** The edge census is as the text says: up to 9–10 chamber-
boundary crossings per grid cell (up to 4 on a single edge; nested
slivers) in the overflow corner where D2 mass concentrates, versus
exactly 2 per cell in flat regions. But M4c's finer census resolves
what M4b could not (its E31): the sliver cluster at t ≈ 0.00187 on the
vertex cut is **2.44×10⁻⁶ wide**, carries opposite jump vectors of L2
norm 1884.6, and **self-cancels to a net measure jump of 8.90**
(cluster 2: width 3.7e-6, jumps ≤ 0.81, net 1.32; cluster 3: width
6.5e-4, max jump 22.3, net 9.54). So the fan's operational signature
density overstates its curvature-measure density: many thin chambers
contribute little net μ-mass. "Dense wedge-fan where curvature
concentrates" is correct at the resolution M4b analyzed; at M4c
resolution the same locus is a hierarchy of self-cancelling atoms.

---

## 4. Exploration: Theorem R — the regime dial (new, executed as M4c)

The root-cause text's step 3 — "treat the smooth geometric κ_V as a
conceptual ancestor or as a separate regime, not as the limit object"
— was, until now, a *position* without a mechanism. Theorem N blocks
the σ→0 pointwise limit; nothing in the record said what the smooth
regime *is* or when it is entered. The following closes that gap.

**Theorem R (coarse-graining identity and dial law).** Let v be the
continuous PA lex-pFBA map, μ = D²v its curvature measure (Theorem
S(ii)), φ_σ a Gaussian mollifier at scale σ, and v_σ = v ∗ φ_σ.
Then:
- **(R1) Exact convolution identity.** D²v_σ = μ ∗ φ_σ. On a line
  through the parameter space with events (t_e, Δ_e):
  v_σ″(t) = Σ_e Δ_e φ_σ(t − t_e). The smoothed map's curvature is the
  *same measure, smeared* — no new object appears.
- **(R2) Second-difference law.** The ε-second difference of v_σ at
  t₀ equals Σ_e Δ_e K(t₀ − t_e; ε, σ) with the closed-form kernel
  K(d; ε, σ) = ∫_{−ε}^{ε} (ε−|u|) φ_σ(d+u) du. Asymptotically:
  D(ε,σ) ~ ε² ‖μ_σ(t₀)‖ for ε ≪ σ (**slope 2 — the smooth/Riemannian
  regime**), and D(ε,σ) → Σ_e Δ_e (ε − |t₀−t_e|)₊ for ε ≫ σ (**slope
  1 — the discrete/kink regime**).
- **(R3) Crossover.** The transition occurs at ε\* = c·σ; on the
  measured network, c ≈ 3.
- **(R4) Mass conservation.** The total vector mass of μ_σ is
  σ-independent (telescoping: Σ_e Δ_e = v′(T) − v′(−T); measured
  residual 4.0×10⁻¹⁴). The discrete and smooth objects carry the same
  curvature; only its distribution differs.

**Biological reading.** σ is not a free parameter — it is the
resolution of the measurement process: ensemble averaging over enzyme
expression noise, population heterogeneity, or any explicit
regularization. ε is the perturbation magnitude. The dial: a
knockout-scale perturbation (ε ~ 1) sees kinks; infinitesimal
sensing at fixed population noise (ε → 0) sees smooth curvature.
**The smooth κ_V is not the limit of the discrete object (Theorem N
blocks that); it is the same measure at finite resolution σ.** This
gives the root-cause text's "separate regime" a precise, falsifiable
content.

**M4c execution** (`scripts/m4c_regime_dial.py`, iML1515, locus = the
M4b codim-2 vertex (glc 1.692, O₂ 1.480), cut along the M4b dB
direction; 858 lexicographic solves; census at 10⁻⁶-resolution
bisection; kernel closed-form self-test 1.2×10⁻⁶):
- *Census (machine):* 12 events, 11 kinked, 1 mask-type (the N1
  prediction appears again: a signature change with no flux kink);
  telescoping residual 4.0×10⁻¹⁴; three sliver clusters as in RC6.
- *Dial (exact convolution of the measured measure, 24-point ε-grid
  per σ):*
  - σ = 0.003: slope(ε ≤ σ/3) = **1.9995**; slope(ε ≥ 3σ) = 1.13
    (local slopes → 1.0 at the grid top); ε\* = 0.0123 (**ε\*/σ = 4.11**)
  - σ = 0.01: 1.9991 / 1.16; ε\* = 0.0298 (**2.98**)
  - σ = 0.03: 1.9994 / 1.14; ε\* = 0.0933 (**3.11**)
  - σ = 0.1: 1.9992 / 1.17; ε\* = 0.2447 (**2.45**)
  The ε² law holds to four significant figures at every σ; ε\*
  scales linearly in σ with c ≈ 3 — the crossover is a property of
  (ε, σ), not of the network.
- *Identity validation (machine):* independent 5-point Gauss–Hermite
  evaluations of v_σ match the exact convolution with median relative
  error 0.4% (σ=0.003), 1.9%, 5.4%, 8.7% (σ=0.1) in the resolvable
  regime ε ≥ σ/2.
- *Locality control:* at a wall-free base point (clearance 0.165,
  σ=0.03), the machine second difference is ≤ 1.5×10⁻¹¹ for all
  ε below reach — curvature is carried by the (smeared) walls, not by
  the chamber interiors.
- *Methodological finding (new, and a numerical echo of Theorem N):*
  a **fixed-node quadrature does not smooth below its node spacing**.
  The 5-point GH evaluation of v_σ is itself piecewise affine in t
  (each node translates v's kinks), so the machine D vanishes exactly
  for ε below the distance to the nearest node-translated kink, while
  the exact convolution gives the ε² law. Discretized smoothing does
  not remove the atoms unless the kernel itself is resolved — the
  atomicity obstruction manifests even at the numerical level. Any
  future E28-style empirical second-difference protocol must state
  its (ε, σ) pair and resolve the kernel (or work measure-theoretically),
  or it will silently measure a translated-kink artifact.

**What M4c means for the open items.**
- **E31 (wedge-fan resolution):** partially resolved — the fan's
  sliver structure is now measured (RC6); the remaining task is a
  2D (not cut) census at matched resolution.
- **E28 (second differences on measured time courses):** now has a
  design law — the outcome depends on where the experiment sits on
  the (ε, σ) dial; the analysis plan must bin by ε/σ.
- **The manuscript's smooth κ_V:** repositioned as a resolution
  statement (R1/R4), which is exactly the defensible form the joint
  assessment's "coarse-grained and empirical identification" called
  for.

---

## 5. What the bridge now honestly says (supersedes v2 §3)

1. The three κ objects connect through the active-set skeleton as one
   **measure at multiple resolutions**: the geometric curvature is the
   (viability-weighted) defect + jump measure of the flux graph
   (Theorems S, G); the rerouting statistics are event-triggered
   functionals of the same measure (M1, M3); the time-course object
   integrates the event measure along trajectories (Theorem S(iv));
   the smooth κ_V is the same measure convolved at resolution σ
   (Theorem R) — entered whenever ε ≪ σ; the dynamic
   order-sensitivity is a first-order commutator (Theorem D).
2. The static and dynamic signatures remain distinct and must be
   carried separately (RC3); the bridge transports the skeleton into
   both, not one into the other.
3. Open, now precisely localized: (a) E28 under the (ε, σ) design law;
   (b) the formal statement κ_flux = F[μ] for the manuscript's exact
   κ_flux definition, with the E24-calibration test (does the
   transcript-level correlation survive the measure-theoretic
   redefinition?); (c) model-family regularity for any mesoscopic
   defect-density limit (Theorem N(iii)(a)); (d) the 2D sliver census
   (E31 remainder).

---

## 6. The corrected bottom line (replacement text)

> - **Root cause:** correct — FBA is piecewise affine, so its static
>   curvature is a measure on the active-set skeleton, not a smooth
>   2-form; the ε² holonomy normalization was inadmissible (an mpLP
>   theorem, so the failure is model-independent).
> - **Bridge status:** the smooth bridge is not merely falsified — it
>   is blocked by the atomicity theorem (N). The discrete bridge is
>   not "plausible and partially proven" — it is constructed and
>   machine-verified (S, G, N1, D), with the dynamic commutator law
>   (slope 1, sparse: 9/76 interacting pairs) as its falsifiable
>   prediction. One identification step remains open (κ_flux = F[μ]
>   + E24 recalibration).
> - **Implication:** do not claim convergence of the FBA metric to the
>   smooth κ_V — and do not merely "treat κ_V as a separate regime."
>   State the dial: the smooth object is the same curvature measure
>   at resolution σ (Theorem R); perturbation scale ε versus
>   resolution σ selects the regime, with measured crossover
>   ε\* ≈ 3σ and mass conservation across the dial. The unification
>   is a resolution statement, not a limit statement.

---

## 7. Deliverables of this evaluation

| Artifact | Content |
|---|---|
| `download/m4/m4c_summary.json` | dial, census, validation, slivers, control, GH-resolution finding |
| `download/m4/m4c_scaling.csv` | machine + exact D(ε, σ) grid |
| `download/m4/m4c_cut_events.csv` | 12 events: positions, jump norms, segment slopes, kinked/mask |
| `download/m4/fig_m4c_scaling.png` | the dial: exact curves + machine points + slope guides |
| `download/m4/fig_m4c_density.png` | smeared curvature density κ_σ(t) + identity validation panel |
| `scripts/m4c_regime_dial.py` | the experiment (reuses `lp_engine.py`) |
| `scripts/lp_engine.py` | engine patch: deterministic presolve-off retry (activates only where the original returned failure; previously computed results unchanged) |
| this file | the evaluation |
