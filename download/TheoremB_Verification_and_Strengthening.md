# Theorem B — Second-Order Verification and Strengthening

**Task.** Evaluate, verify (not at face value), augment, strengthen, correct and
complete the final recommendation of the bridge-strength evaluation (commit
`e31fd69`, `download/DeepSeek_Bridge_Strength_Evaluation.md`): the single-manuscript
route with Theorem B (discrete-to-smooth curvature convergence under mesh
refinement) as the theoretical spine, the measure-theoretic `kappa^mu` as the
metric, `journal_manuscript_v2` Layer-0 drafting, E32/PRECISE-arm replication as
supplementary, and v21 frozen.

**Method.** Every checkable claim of the recommendation was re-derived
independently and re-executed with an independent seed
(`scripts/theoremB_stress_test.py`, seed 20260902; deliverables
`download/theoremB_stress/{bt_results.json, bt_summary.txt, bt_figures.png}`).
The recommendation's quoted numbers were checked against the record
(`download/deepseek_bridge/v2_refinement.json`, `v5_e24_recalibration.json`,
`v1_value_function.json`).

---

## 1. Executive verdict

**The strategic recommendation is ENDORSED and the single-paper route stands.**
The V2a numbers reproduce independently (BT-1: folded W1 0.058 -> 0.0039, mass
ratio 0.939 -> 1.0009, vs the record's 0.049 -> 0.0035 and 0.930 -> 1.0023 with
a different seed); the V5 recalibration (r = +0.3739 -> +0.3954, partial
+0.251 -> +0.269, rho(kappa^mu, kappa_V_lex) = 0.99998) is confirmed in the
record; v21 remains untouched.

**However, Theorem B as stated in the recommendation is FALSE in two of its
claims and its proof contains one invalid step.** The defects are not cosmetic:
each was invisible to the V2 prototype because that prototype lives in the one
regime (1D cuts, one-signed measures, telescoping) where the false claims hold
automatically. After repair, the theorem is *strictly stronger* than the
recommendation's version, and one of the verification side-results (the exact
sec-law bias of the angle-defect layer, §2.5 below) materially corrects the
audit's Route 1 (Regge-Alexandrov). All repairs are machine-verified.

| # | Recommendation claim | Independent verification | Verdict |
|---|---|---|---|
| 1 | Single coherent manuscript, do not split | V5 passes with strengthening; joint assessment 6/6 | **Endorsed** |
| 2 | "(p-2)-skeleton" support; "atoms are the angle defects" | Atoms of D^2 u_h live on the (p-1)-skeleton; the (p-2) object is a different measure with a different (biased) limit | **False — repaired (B'.1, B'.5)** |
| 3 | `||mu_h||_TV -> ||mu||_TV` | Exact counterexamples: u=xy ratio = 3 - 1/n (measured 2.9922 at n=128); strictly convex u = 2x^2-xy+2y^2 ratio = 1.4 - 1/n (measured 1.3922); generic map 3.73 (aligned) / 4.39 (jittered) | **False in general — repaired (B'.3, B'.4)** |
| 4 | Proof step 3: TV convergence "by lower semicontinuity and the assumed mass bound" | l.s.c. gives liminf >= target; an upper bound gives no equality; counterexamples show strict inequality | **Invalid — replaced** |
| 5 | `W_1(mu_h, mu)` | W_1 is defined for positive measures; the record's V2a actually computed a folded W_1 between absolute values; the correct signed-measure metric is the KR/flat norm (verified -> 0, BT-6) | **Misnamed — corrected** |
| 6 | V2 numerical table (W1 0.049 -> 0.0035; mass ratio 1.00) | Reproduced with independent seed; numbers honest but taken from the 1D one-signed regime that cannot falsify claims 2-3 | **Reproduced; regime-limited** |
| 7 | "Read as proposition for interpolation, conjecture for parametric LP/FBA" | Correct instinct; sharpened: the missing assumption for the LP case is a per-cell discrete-duality identity (structured complexes) or a DDFV dual-diamond pairing (general complexes) | **Sharpened (B'.6)** |
| 8 | kappa^mu metric + rank identity as robustness | V5 confirmed; kappa^mu is a 1D-trajectory telescoping object — the safe regime of B'.4 | **Endorsed** |
| 9 | Freeze v21; new content in v2 | Honored throughout | **Endorsed** |

---

## 2. The defects, each with its verification

### 2.1 D-A — The support claim conflates two layers

The recommendation states: *"mu_h is a finite signed measure concentrated on
the (p-2)-skeleton of T_h. In the planar case p = 2, its atoms are the angle
defects of the polyhedral surface (x, u_h(x))."*

For `mu_h = D^2 u_h` (distributional second derivative of the piecewise-affine
interpolant) this is false in every dimension:

- **(p >= 2):** `D^2 u_h` is supported on the **(p-1)-skeleton** (the facets).
  On each interior facet F shared by triangles tau-, tau+ the atom is
  `A_F = [grad u_h]_F (x) n_F |F|` (jump of the piecewise-constant gradient,
  outer product with the conormal, weighted by the facet measure). Machine
  check (BT-3/4/5): all atoms sit on edges; the vertex count is reported in the
  facet census and no atom sits on a vertex.
- **(p = 1):** atoms sit on the 0-skeleton, which is the (p-1)-skeleton; the
  (p-2)-skeleton is empty. The claim is therefore inconsistent with the
  recommendation's own 1D prototype (V2: breakpoints).
- The **(p-2)-skeleton object** — vertex angle defects of the graph — is a
  genuinely different measure (§2.5): its weak limit is not the Hessian
  density but a *nonlinear, biased* functional of it.

The record's own evaluation doc (§3 of `DeepSeek_Bridge_Strength_Evaluation.md`)
had this right ("supported on the codim-1 cell boundaries ... with vertex angle
defects as the codim-2 layer"); the recommendation's restatement collapsed the
two layers into one wrong sentence. **Repair: B'.1.**

### 2.2 D-B — Total-variation convergence is false in general

Claim: `||mu_h||_TV -> ||mu||_TV`. Three exact counterexamples, all with
machine-verified arithmetic on the standard right-triangle mesh of [0,1]^2
(entrywise TV; Frobenius behaves the same way):

| Map | Hessian | TV ratio (n -> inf) | Measured (n=128) | Status |
|---|---|---|---|---|
| u = xy | [[0,1],[1,0]] indefinite | **3 - 1/n** | 2.9922 | falsifies |
| u = 2x^2 - xy + 2y^2 | [[4,-1],[-1,4]] **strictly convex** | **1.4 - 1/n** | 1.3922 | falsifies even under convexity |
| u = x^2 | diag(2,0) axis-aligned | 1 - 1/n | 0.9922 | explains the audit's "1.00" |
| sin(pi x) sin(pi y) + 0.3 r^2 | indefinite, varying | 3.73 (aligned) / 4.39 (jittered 0.22h) | 3.73 / 4.39 | generic |

The quadratic ratios are *exactly* `c - 1/n` (the 1/n is the missing boundary
facets): per cell of the aligned mesh the three atoms are

```
A_diag = b h^2 [[1,1],[1,1]],  A_vert = (a-b) h^2 e_x (x) e_x,
A_horiz = (c-b) h^2 e_y (x) e_y          for H = [[a,b],[b,c]],
```

whose **sum is exactly `h^2 H`** (per-cell atom-sum error 0.0e+00, BT-3/4/5 —
this identity is the repair's engine), while the entrywise TV is
`|a-b| + |c-b| + 4|b|` per cell versus the target `|a| + |c| + 2|b|`. For
u = xy: 6 vs 2 (ratio 3); for the convex example: 14 vs 10 (ratio 1.4).

**Why the V2 prototype could not see this.** The prototype tests 1D cuts of a
*concave* min-of-tangent-planes family. In 1D with one sign, TV convergence is
automatic: (i) in 1D the atoms are Riemann samples of the density, so
`sum |atoms| -> int |g''|` for *any* sign (BT-2: mixed-sign 1D ratios
0.43 -> 0.997); (ii) for concave 1D maps the derivative is monotone, so total
variation telescopes to the endpoint difference exactly (BT-1 reproduces mass
ratio -> 1.0009). The false claim is invisible in that regime — the evidence
was real but unrepresentative. **Repair: B'.3 / B'.4.**

### 2.3 D-C — The proof's step 3 is logically invalid, and steps 1-2 are needlessly muddled

- Step 3 argues TV convergence "by lower semicontinuity and the assumed mass
  bound." Lower semicontinuity of TV under weak convergence yields
  `liminf ||mu_h||_TV >= ||mu||_TV`; an upper bound yields limsup <= bound;
  neither gives equality, and §2.2 shows equality fails.
- Step 1's "boundary terms that vanish as h -> 0" do not exist: for
  `phi in C_c^inf(Omega)` the pairing
  `<D^2 u_h, phi> = int u_h D^2 phi` holds *by definition* of the
  distributional derivative. The weak-convergence proof is then two lines and
  needs less than assumed (shape-regularity and h -> 0; quasi-uniformity is
  only needed for the uniform TV bound; assumption 3 "Refinement" is implied
  by h -> 0 on a compact family). **Repair: B'.2 with the full short proof.**

### 2.4 D-D — W_1 is the wrong name for the metric actually computed

The recommendation's table reports `W_1(mu_h, mu)` for signed measures; W_1 is
defined between positive measures. The record's V2a computed a *folded* W_1
between the absolute-value (positive) measures — legitimate in the one-signed
regime where |.| is linear, but not a distance between the signed objects. For
the general statement the correct metric is the **Kantorovich-Rubinstein / flat
norm** `||mu||_KR = sup_{Lip(phi)<=1} |int phi d mu|`. BT-6 verifies it -> 0
(5.4e-3 at n=256, aligned; 5.1e-3, jittered) alongside weak convergence at
rate ~2. **Repair: B'.2 (iii).**

### 2.5 D-E — The angle-defect layer is biased by an exact sec law (new result)

BT-7/BT-7b separated the two layers on the same meshes:

- **(p-1) layer (Hessian atoms):** unbiased. Weak convergence to
  `D^2 u dvol` at rate ~2 on both the aligned and the jittered mesh families
  (BT-6), and exact per-cell duality on quadratics (BT-3/4/5).
- **(p-2) layer (vertex angle defects of the graph):** converges weakly to
  the **Gauss-map area density**
  `det(D^2 u) / (1 + |grad u|^2)^(3/2) = K * sqrt(1 + |grad u|^2)`, i.e.
  curvature per *projected parameter area*, **not** the intrinsic Gaussian
  curvature `K = det(D^2 u)/(1 + |grad u|^2)^2` (per surface area).

The bias law is exact: for the right-triangle stencil,
`defect(v) = K(v) * sqrt(1 + |grad u(v)|^2) * h^2 * (1 + o(1))`, verified to
**0.0% excess against the sqrt(1 + tau^2) prediction across 13 probes**
(tilts 0.11-2.83; diagonal, axis, and near-zero tilt directions), and the
BT-7 pairing "errors" (0.0376 vs the intrinsic target 0.1786, convex and
saddle) equal the sec-law prediction exactly (0.2162 = the Gauss-map-area
pairing). Consequences:

1. The recommendation's sentence "its atoms are the angle defects" fails not
   merely at the level of support but at the level of *limits*.
2. The audit's Route 1 (Regge-Alexandrov: "the angle defect *is* the
   curvature") needs the explicit area correction `sqrt(1 + |grad u|^2)` to
   recover intrinsic curvature — a statement the record's Theorem G (fixed
   complex, O(1) defects) does not contradict, since Theorem G measures
   defects of the *fixed* FBA complex, not interpolant refinement limits.
3. For the manuscript: the canonical discrete object is the **(p-1) Hessian
   layer**; angle defects may be reported as Gauss-map-area curvature with the
   bias law stated.

### 2.6 D-F — Dropped content that must be restored

The recommendation's "Remark on the FBA setting" keeps the honest
interpolant-vs-LP caveat but drops the record's crown jewel: the **two-sided
window law** `h << sigma << L_var` (B3), which is the actual content of the
M4c regime dial and the corrected resolution statement. Restored in B'.5.

---

## 3. The repaired theorem (B-prime), stated for the v2 manuscript

Throughout, `Omega subset R^p` compact, `u in C^2(Omega; R^m)`,
`{T_h}` shape-regular with `h -> 0`; `u_h` the continuous piecewise-affine
interpolant on `T_h`; `mu_h = D^2 u_h`; `mu = D^2 u dvol`.

**B'.1 (Atom representation; support on the (p-1)-skeleton).**
`mu_h` is a matrix-valued Radon measure concentrated on the (p-1)-skeleton of
`T_h`. For each interior facet F with unit conormal `n_F` oriented from
`tau-` to `tau+`,

```
A_F = [ grad u_h ]_F  (x)  n_F  |F|        (jump (x) conormal x facet measure),
```

and `mu_h = sum_F A_F delta_F`. In p = 1 this is the slope-jump measure at
breakpoints (the V2 prototype's object). The (p-2)-skeleton carries a
different measure (B'.5).

**B'.2 (Weak convergence; two-line proof; rates).**
(i) For every `phi in C_c^infty(Omega)`, `<mu_h, phi> = int_Omega u_h D^2 phi`
(by definition of distributional derivatives — there are no boundary terms).
(ii) `||u - u_h||_infty <= C h^2 |u|_{C^2}` on shape-regular families, so
`<mu_h, phi> -> <mu, phi>`; hence `mu_h -> mu` weakly as matrix-valued
measures. (iii) In the KR/flat norm, `||mu_h - mu||_KR -> 0` (for one-signed
limits this is W_1; in general use the flat norm — the recommendation's W_1
notation is corrected thereby). Machine rates: O(h^2) against smooth test
families on both aligned and jittered meshes (BT-6: rates 2.00 / 1.99).

**B'.3 (Total variation: what is true, what is false).**
(i) Uniform bound: `||mu_h||_TV <= C |u|_{C^2} |Omega|` (quasi-uniformity).
(ii) Lower semicontinuity: `liminf ||mu_h||_TV >= ||mu||_TV`.
(iii) **Convergence fails in general** — explicit counterexamples with exact
arithmetic: u = xy (ratio 3), strictly convex u = 2x^2-xy+2y^2 (ratio 1.4),
generic smooth maps (3.7-4.4). It holds in the one-signed regime (convex or
concave *and* 1D-directional), which is where the V2 prototype and the V5
kappa^mu (1D-trajectory telescoping) live — and why both are sound.

**B'.4 (The correct no-mass-loss statement: dual-cell L^1 reconstruction).**
On structured (aligned) complexes define the per-cell reconstructed density
`rho_h(cell) = (1/|cell|) sum_{F assigned to cell} A_F`. Then
`rho_h -> D^2 u` **strongly in L^1** with rate O(h) for `u in C^3`
(machine-verified: rate 0.99, BT-6 aligned; exact to 0.0e+00 on quadratics,
BT-3/4/5), and therefore `||rho_h||_{L^1} -> ||mu||_TV`: the "mass ratio
-> 1.00" phenomenon is real *for the reconstruction*, not for the raw atomic
TV. Caveat (verified, not a defect of the theorem): on unstructured (jittered)
meshes the naive 3-facet per-cell patch is no longer the dual cell — the
reconstruction there requires the DDFV dual-diamond pairing (flat ~0.29
relative error at 0.22h jitter, BT-6); weak convergence is unaffected.

**B'.5 (The two layers and the sec law).**
The (p-2) angle-defect measure `K_h = sum_v defect(v) delta_v` of the
polyhedral graph converges weakly to the Gauss-map area density
`det(D^2 u)/(1+|grad u|^2)^(3/2) dvol` with exact bias factor
`sqrt(1+|grad u|^2)` (sec law, 0.0% excess across 13 probes). Recovering the
intrinsic Gaussian curvature requires dividing by the graph area factor. The
canonical curvature carrier for the FBA bridge is the (p-1) Hessian layer
(B'.1-B'.4), not the angle-defect layer.

**B'.6 (Bridge to parametric LP / FBA).**
Read B'.1-B'.4 as a *proposition* for interpolants on structured complexes.
For parametric-LP value-function families (min of tangent planes; theta in the
RHS; nested outer approximations) the same statements hold along 1D
parameter cuts by monotone telescoping (BT-1 reproduces the record's V2a
numbers with an independent seed). For general mpLP/FBA sequences the
corrected theorem is a **conjecture** whose precise missing assumption is now
identified: a per-cell discrete-duality identity (structured complexes) or a
DDFV dual-diamond pairing stability (general complexes), plus the uniform
convergence of the PL family to a C^2 limit. The two-sided resolution window
`h << sigma << L_var` (the record's B3/M4c dial) is retained: the smooth
object is a member of the coarse-grained family at matched resolution, never a
sigma -> 0 limit (Theorem N's obstruction stands).

**B'.7 (Regime dichotomy, exact arithmetic).**
Curvature mass captured by a loop of radius eps: smooth map -> slope 2
(measured 2.000); piecewise-affine map with fixed kink complex -> slope 1
(measured 1.000). M4a's slope-1.00 measurement is the second regime, here
replicated in closed form (BT-8).

---

## 4. Impact on the v2 manuscript (Layer-0 drafting rules)

1. **Theorem B block must be re-typed as B'.** with the (p-1) support
   statement, the two-line weak-convergence proof, the honest TV statement
   (B'.3 with the counterexamples in a remark), and the L^1 reconstruction
   (B'.4) as the "no mass loss" result. The recommendation's version must not
   be pasted.
2. **kappa^mu is safe as defined** (V5: measure mass along the 1D lex-pFBA
   trajectory — the telescoping regime of B'.3(iii)/B'.4). The rank identity
   (rho = 0.99998) is correctly reported as metric-invariance robustness.
3. **Angle defects / Regge material**: either include the sec-law correction
   (B'.5) or relegate to a remark; the audit's Route-1 phrasing ("the angle
   defect *is* the curvature") must not be pasted.
4. **E32 (event-measure stabilization) design**: test that kappa^mu mass
   stabilizes under trajectory refinement — this is exactly B'.4's regime
   (1D telescoping + Riemann); expected outcome: resolution-independent mass
   (the record already measured 288.77 across 4x/8x refinement).
5. **Window law retained**: the resolution statement (one measure, several
   smoothings, measured crossover) stays as the record's §5 form, with the
   h << sigma << L_var window explicit.
6. v21 stays frozen; all of the above goes into `journal_manuscript_v2.tex`
   (Layer-0, R/D/E hierarchy), ported section by section in later layers.

---

## 5. Reproducibility

- Script: `scripts/theoremB_stress_test.py` (independent seed 20260902; no
  dependency on the record's scripts).
- Outputs: `download/theoremB_stress/bt_results.json` (all tables),
  `bt_summary.txt`, `bt_figures.png` (7 panels: TV ratios, weak convergence,
  generic-map both-mesh panel, angle-defect pairing, V2a reproduction, M4a
  miniature, sec-law panel).
- Record artifacts cross-checked: `download/deepseek_bridge/v2_refinement.json`,
  `v5_e24_recalibration.json`, `v1_value_function.json`,
  `download/DeepSeek_Bridge_Strength_Evaluation.md`.
- Frozen v21 (`scripts/journal_manuscript.tex`, 10,830 lines): untouched.
