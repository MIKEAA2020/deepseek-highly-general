# The Active-Set Bridge, v2 — Repaired and Completed Formulation

**Document status.** This is the corrected, completed, and strengthened
version of `external_audits/unifying object/deepseek formulation.txt`
(the "Active-Set Bridge Conjecture" and its five-point self-critique),
produced under the standing instructions: evaluate, verify, strengthen,
augment, improve, correct, complete, and attempt to solve. Every
verdict below is grounded either in a proof, in the executed M1/M3/M3b
numerical record (iML1515, deterministic lexicographic-pFBA engine), or
in the two new measurements M4a/M4b executed for this document. The
frozen v21 manuscript is untouched; this file is source material for
the future `journal_manuscript_v2+` passes.

---

## 0. What the original formulation got right (verified)

1. **Piecewise-affine structure.** Under a fixed lexicographic
   tie-break, the optimal flux map `v(theta)` is single-valued and
   piecewise affine on a finite polyhedral complex of the parameter
   space (multi-parametric LP chamber theory). *Verified:* M1 measured
   machine-precision affine segments (residuals <= 8e-14 relative) on
   all 12 sweeps; M4b's finite-difference Jacobians are exact within
   chambers by the affine-consistency test.
2. **Continuity across interfaces.** *Verified:* M1's D1 kinks (not
   jumps); M4b's continuity diagnostics across the analyzed interfaces
   (finite-distance jumps consistent with the kink slopes, no tears
   found at the analyzed loci).
3. **Distributional second derivative supported on active-set
   interfaces.** *Verified:* D2 mass on material events 0.99999996
   (glucose), 0.99999946 (O2), 0.934-1.0 (knockdowns); M4b 1D cut
   through a codim-2 region: 100.0000000% of D2 mass on 11 events.
4. **The bridge runs through the active-set skeleton.** *Verified:*
   rerouting epistasis aligns with active-set footprint overlap
   (Spearman 0.865, p ~ 0).
5. **The five self-critique instincts** (finite-dimensional
   transports, explicit KKT connection, regular-crossing limits,
   concrete transport rule, exact second-order expansion) are the right
   directions — but each fix as written contains a specific technical
   error (see C3, C5, C6 below).

## 1. Where the formulation fails (the corrections)

**C1 — The central object is trivially flat.** The affine-extension
holonomy `H_gamma` of the original statement is *exactly the identity*
for every closed loop, because `v` is a single-valued continuous
function: the chamber representatives agree on shared interfaces (the
file's own cocycle claim), so composing transition maps around any
loop returns the starting representative. The conjecture's display
`lim (1/eps^2)(H - I) = Omega` therefore reads `0 = Omega` for the
static map. The nontrivial static curvature is not holonomy; it is the
*distributional Jacobian-jump measure* on codim-1 interfaces — the
object M1 measured. *This is a structural error, not a normalization
error.*

**C2 — The eps^2 scaling law is falsified in both layers.**
(a) *Static:* a fixed piecewise-affine map has no eps^2-scaled holonomy
at all (C1). (b) *Dynamic:* the only path-dependent object in the
executed program is the sequential L1-MOMA adjustment. M4a measured
its commutator under a linearly scaled perturbation family
(76 pairs, six depths from 1 to 1/32): 64 pairs have `chi(eps) = 0`
exactly at every depth; the 9 nonzero pairs scale with slope
0.976-1.244 (median 0.998) — exact halving ratios across five octaves
(e.g. sdhD+nuoG: 101.29, 50.56, 25.29, 12.66, 6.34, 3.19). The
non-commutativity is **first-order in the perturbation depth**: the
tangent cone changes by an O(1) face at each knockout and the order
mismatch accumulates at O(eps). The single-response control scales at
slope 1.01 as expected. The conjecture's A4 ("the missing ingredient
is a proof of the scaling limit") is thereby resolved *negatively*:
the limit exists but with exponent 1, and only on the
non-decoupled stratum.

**C3 — The file's own repair breaks the connection axioms.** The
proposed parallel transport "orthogonal projection F_i -> F_j" is not
invertible (`P_ji P_ij != I` in general), so the transition system is
not a connection and holonomy is not well-defined. The correct
transport is the *minimal-rotation (unfolding / polar) map*: the
rotation about the shared edge that maps one face's tangent plane onto
the other's. It is an invertible isometry, fixes the shared edge
exactly, and reduces to the identity in the coplanar limit. With this
rule, back-tracking cancels *exactly* and curvature concentrates at
codim-2 crossings. *Verified:* synthetic unit tests (transport =
-defect at 1e-14 including a 190.6-degree cone; flat case exactly 0);
on iML1515, flat controls compose to the identity at <= 3.4e-11 with
axis/angle constancy along interfaces at 1e-11.

**C4 — Assumption A3 (existential geometric embedding) is
unfalsifiable.** Any map embeds into any geometry trivially; the
conjecture cannot be proven or falsified while Phi, nabla, V are merely
assumed to exist. The repair: **construct the geometry intrinsically.**
The graph map `G(theta) = (theta, v(theta))` with the induced
Euclidean metric is the Riemannian object; its discrete Gauss
curvature (angle defect at codim-2 vertices) contracted with the
viability weights is `kappa_geom`. The static bridge then becomes a
*theorem* (Theorem G below), and the only remaining identification
with the manuscript's continuum objects is coarse-grained and
empirical (E28).

**C5 — The claimed confirmations are overstated.** The file states "M1
and M3 confirm the first two consequences to numerical precision."
Consequence 1 (second-order concentration): confirmed. Consequence 2
(double-knockout non-additivity `eps_ij` = rectangle holonomy):
**contradicted** — M3b measured the open-path commutator chi and the
epistasis |eps| on the same pair panel: full-panel Spearman = -0.347
(p = 6.8e-06; driven by the synthetic-lethal structure), within
non-synthetic-lethal pairs -0.07 (p = 0.43, no association). The
optimum-level non-additivity and the transient-level non-commutativity
are *distinct* signatures that must be carried separately through any
bridge. Consequence 3 (time-course object): the stated identity misses
the smooth term `2||v'(t)||^2` and misstates a pointwise equality for
what is an *integral* identity (Theorem S(iv)).

**C6 — Flatness (A5) is incompatible with the intended conclusion.**
The cocycle condition the file derives is exactly the statement that
the affine connection is globally trivial; a globally consistent
system of representatives cannot produce nontrivial holonomy. Only a
transport on objects that are *not* single-valued (tangent frames
across kinked folds; dynamic states under greedy adjustment) can carry
holonomy, and then the curvature concentrates on the codim-2 skeleton
as O(1) defects — never as an eps^2 infinitesimal 2-form for a fixed
model (Theorem N).

**Additional corrections.**
- A1 is achievable but non-trivial: the M1 engine *discovered*
  vertex degeneracy in the parsimony stage (sum|v| ties to 13 digits
  with 0.69-magnitude flux flips between warm starts), resolved by the
  seeded third-stage tie-break. The engine is the existence proof that
  A1 can be implemented deterministically; on measure-zero strata the
  deterministic selection may tear, which the analysis must tolerate
  (no tears were found at the analyzed loci).
- The rank-one-update claim (basis exchange across a chamber boundary)
  is correct within a stage under nondegeneracy; across the three
  lexicographic stages the connection is a *tower*, matching the
  factored-curvature-datum architecture of the joint assessment
  (Layer 1).
- The proof-sketch step "holonomy = integral of the second-order
  measure" is not a theorem for the static map (C1); the true
  structure equation is: the codim-1 jump measure (M1's object) and
  the codim-2 defect measure (Theorem G) are related by discrete
  structure equations — the dihedral kinks of the incident faces
  determine the vertex defect via the unfolding composition.

## 2. The repaired formulation

**Setting.** `Theta` a compact polyhedral parameter space
(environmental bounds and/or genetic capacities); `v: Theta -> R^m` the
optimal flux map of the genome-scale LP under a fixed 3-stage
lexicographic pFBA tie-break (biomass -> parsimony -> seeded linear
term). Let `C` be its chamber complex, `C^{(p-1)}` the codim-1
skeleton (interfaces), `C^{(p-2)}` the codim-2 skeleton (crossings).

### Theorem S (static curvature measure)
(i) `v` is continuous and affine on each chamber of the finite complex
`C`.
(ii) The distributional derivative is `Dv = sum_r M_r 1_{R_r}`, and
`D^2 v` is a matrix-valued measure supported on `C^{(p-1)}` with
density `(M_j - M_i) (x) n_ij dH^{p-1}` on the interface between
chambers `i, j`.
(iii) For any piecewise-C^1 path `gamma`, the acceleration of
`v(gamma(t))` in distributions is
`sum_e (M^+ - M^-) gamma'(t_e) delta(t - t_e)`.
(iv) For the squared displacement `kappa(t) = ||v(gamma(t)) -
v(gamma(0))||^2`:
`kappa''(t) = 2||v'(t)||^2 + 2 sum_e <v(t_e) - v(0), Delta v'(t_e)>
delta_e` — a piecewise-constant smooth term plus a signed measure on
the event set. The empirical E24-style object is an *integral* of the
event measure along the trajectory.
(v) Closed-loop state holonomy is exactly trivial: `v(gamma(0)) =
v(gamma(1))` for every closed loop.

*Proof.* Chamber structure and finiteness: standard mpLP theory
(Gal-Nedoma 1972; Bemporad-Morari-Dua-Pistikopoulos 2002) applied to
the three-stage lexicographic family. Continuity: Berge's maximum
theorem applied to the (singleton-valued a.e.) solution map, extended
to the interfaces by the tie-broken selection. (ii)-(iii):
distributional chain rule for BV-affine functions. (iv): product rule
with (iii). (v): function-hood. *Machine verification:* M1 (12 sweeps,
D2 mass 0.934-1.0, affine residuals <= 8e-14); M4b cut (11 events,
D2 mass 1.0). ∎

### Theorem G (intrinsic defect — the constructed kappa_geom)
For `p = 2` (two-parameter families): the graph
`G(theta) = (theta, v(theta))` is a piecewise-flat polyhedral surface
in `R^{m+2}`. Define the **unfolding transport** `P_ij` between
adjacent faces as the minimal rotation about their shared edge (the
corrected `P_ij`: invertible, isometric, identity on the common edge).
Then:
(i) (Flatness off the skeleton) any closed loop whose interface
crossings pair up across the same chamber pairs composes to the
identity *exactly*;
(ii) (Defect at crossings) at a transverse crossing of two interfaces
where four chambers `q = I, II, III, IV` meet with Jacobians `M_q`, the
holonomy of a small enclosing loop is the rotation by the corner-angle
defect
`K(theta_0) = 2 pi - sum_q alpha_q`,
`alpha_q = angle(g_q(r_1), g_q(r_2))`, `g_q(d) = (d, M_q d)` — an
O(1) quantity, exactly independent of the loop scale;
(iii) define `kappa_geom` := the viability-weighted defect measure on
`C^{(p-2)}` (plus the weighted jump measure on `C^{(p-1)}`); this is
the *constructed* geometric object the bridge needs — no existential
embedding.

*Proof.* (i) inverse cancellation of the unfolding rotations; (ii)
discrete Gauss-Bonnet / Regge unfolding: composing the four edge
unfolding rotations returns the initial frame rotated by the deficit
(the classical polyhedral-cone holonomy). *Machine verification:*
synthetic piecewise-affine maps (flat case: defect = transport = 0;
cones up to 190.6 degrees: transport = -defect to 1e-14; generic
4-sector maps: same); on iML1515 (glc, O2) plane: flat controls 5/5
exact (identity residual <= 3.4e-11; axis and angle constancy along
interfaces <= 1e-11); defects at the three analyzable corner vertices
are scale-invariant to four decimals (-7.1469 deg and -23.9087 deg at
both delta and delta/2; +0.0104 deg) with the face-consistency
diagnostics self-flagging the under-resolution of the wedge-fan there
(see Theorem N). ∎

### Lemma N1 (no loose kinks)
On a continuous piecewise-affine map, a codim-1 stratum with nonzero
Jacobian jump cannot terminate in the interior of another codim-1
stratum. Equivalently: at any "T-junction" of three chambers A, B, S
(A-B terminating on the A-S / B-S spine), tangential-derivative
continuity along all three shared rays forces `M_A = M_B` — the
terminating stratum is Jacobian-flat ("mask-type": an
operational-signature event, e.g. a support/materiality crossing,
with no flux kink). Consequently every T-junction has corner defect
*exactly zero* and identity holonomy; kinked strata must either cross
(4-chamber vertex, Theorem G) or the chambers on the far side must
split.

*Proof.* The three shared-edge tangential identities:
`M_A d_T = M_B d_T` (along the terminator), `M_A d_S = M_S d_S` and
`M_B d_S = M_S d_S` (along the spine rays), give `M_A = M_B` on both
columns. The corner angles then satisfy
`alpha_A + alpha_B = pi` and `alpha_S = pi`, so the defect vanishes. ∎
*Empirical signature:* Jacobian-flat (kink = 0.0000 deg) interfaces
exist in the (glc, O2) plane (three of the five flat controls); the
"3-boundary-point" cells decompose into thin sliver chambers whose
visible terminators are mask lines.

### Theorem N (atomicity obstruction — A4 cannot be repaired as stated)
For a *fixed* model, the intrinsic curvature of the static layer is a
measure supported on the codim-1 and codim-2 skeletons. Hence:
(i) at a generic point (off the skeletons) every small loop has
trivial holonomy, so `lim (1/eps^2)(H - I) = 0` — the conjecture's
display would force `kappa_geom = 0` at generic points;
(ii) on `C^{(p-2)}`, `H - I = O(1)` (the defect) while `eps^2 -> 0`,
so the normalized limit diverges;
(iii) the only sound scaling limits are (a) *mesoscopic*: loops of
scale much larger than the chamber diameter, `(1/Area)(H - I) ->` the
defect density, which exists only under an asymptotic-density
assumption on the model family (a regularity property, not a theorem
of LP); and (b) *dynamic*: the sequential-adjustment commutator, which
scales as `eps^1` (Theorem D).
Moreover, in the biologically relevant region the skeleton is
*operationally dense*: the edge-crossing census of the (glc, O2) plane
finds up to 9-10 chamber-boundary crossings per grid cell (up to 4 per
single edge, nested sliver chambers) in the overflow-fan corner where
the D2 mass concentrates, versus exactly 2 per cell in flat regions.
The atomicity obstruction is therefore not an edge case: it is the
typical state of the curvature-carrying region.

*This resolves the formulation's "missing ingredient" by showing what
it would actually take:* A4 is not a provable lemma but a regularity
property of a *sequence* of models (chamber diameter -> 0 with
per-vertex defects O(diameter^2)). The strong-form pointwise
identification `kappa_geom = kappa_V` (the 6/6 audit consensus "not
provable") is blocked exactly and only by this obstruction; the
defensible identification is coarse-grained and empirical (E28). ∎

### Theorem D (dynamic layer — the repaired commutator law)
For the flux-relative scaled knockdown family (perturbation depth
`eps`; `eps = 1` equals the M3 full knockout; `eps = 0` the WT
operating point), the sequential L1-MOMA adjustment maps are
piecewise affine jointly in (state, eps). The open-path commutator
obeys
`chi(eps) = eps ||Delta_1|| + O(eps^2)`,
where `Delta_1 = [u_i + u^{(2)}_{j|i}] - [u_j + u^{(2)}_{i|j}]` is the
first-order tangent-cone mismatch (the second adjustment step sees a
tangent cone tightened by the first gene's newly-binding constraint —
an O(1) face change), and `chi identically 0` on the decoupled
stratum where the two adjustments do not interact. The release
(relaxation) projections are exact identities (states remain
feasible), so the closed-loop non-return of M3b is the *irreversibility
of the greedy dynamics*, not a connection holonomy.

*Measured (M4a, 76 pairs, six depths):* 64 pairs `chi = 0` at every
depth (84%); 9 nonzero pairs with log-log slope 0.976-1.244 (median
0.998) and exact halving ratios; single-response slope median 1.01
(linearity control); release identity 6/6 bit-exact. The `eps^2`
commutator law would require the two adjustment maps to share a
common linear part at the operating point; the data exclude this at
the sampled scale. The genuine content of the original A4 in the
dynamic layer is therefore: *the order-sensitivity of sequential
perturbations scales linearly with depth* — a new falsifiable
prediction (graded-CRISPRi order-swap experiments). ∎

## 3. What the bridge now honestly says

1. The three kappa_V objects connect through the active-set skeleton
   as follows: the **geometric curvature** is the (viability-weighted)
   defect + jump measure of the flux graph (Theorems S, G — provable,
   machine-verified); the **rerouting statistics** are event-triggered
   functionals of the same measure (M1: mass 1.0; M3: footprint
   alignment 0.865); the **time-course object** integrates the event
   measure along trajectories (Theorem S(iv)); the **dynamic
   order-sensitivity** is a first-order commutator (Theorem D).
2. The optimum-level non-additivity (`eps_ij`) and the transient-level
   non-commutativity (`chi`) are *distinct* signatures (C5) and must be
   carried separately: the bridge transports the active-set skeleton
   into both, not one into the other.
3. What remains open, now precisely localized: (a) E28 — second
   differences on measured time courses (the empirical identification
   of the integrated event measure); (b) the strong-form pointwise
   identification with the manuscript's smooth kappa_V — blocked by
   the atomicity obstruction (Theorem N); (c) model-family regularity
   (defect-density asymptotics) for any mesoscopic limit theorem;
   (d) full resolution of the wedge-fan vertices (nested sliver
   chambers) at finer operational tolerance.

## 4. Status table

| Original element | Verdict | Repaired statement |
|---|---|---|
| Piecewise-affine v, finite complex (A1/A2) | True, verified | Theorem S(i) |
| T_ij cocycle on affine maps | True but implies trivial holonomy | C1, C6 |
| A3 existential embedding Phi, nabla, V | Unfalsifiable | Constructed graph geometry (C4, Theorem G) |
| A4 scaling limit (1/eps^2)(H-I) -> Omega | False (static: 0 or divergent; dynamic: slope 1) | Theorem N + Theorem D |
| A5 flatness on strata | True and *incompatible* with nontrivial holonomy | Theorem G(i) |
| Proof sketch step 1 (PWL structure) | Correct | Theorem S |
| Step 2 (transitions = Jacobian jumps) | Correct content, wrong carrier | Theorem S(ii)-(iii) |
| Step 3 (holonomy second order, commutator) | False for the static map; first order for the dynamic layer | C1, C2, Theorem D |
| Step 4 (D^2 v measure on interfaces) | Correct, verified | Theorem S(ii) |
| Step 5 (identification with Omega) | Not a theorem; atomicity obstruction | Theorem N |
| Consequence 1 (second-order concentration) | Confirmed (M1) | Theorem S(iii) |
| Consequence 2 (eps_ij = rectangle holonomy) | Contradicted (chi independent of eps) | Section 3.2 |
| Consequence 3 (kappa_time identity) | Imprecise (missing smooth term; integral not pointwise) | Theorem S(iv) |
| Fix 1 (tangent-space transports) | Right direction; projection not invertible | Unfolding transport (C3) |
| Fix 2 (KKT/gauge connection) | Right direction; tower across lex stages | Remark in Section 1 |
| Fix 3 (regular point / distributional limit) | Correct direction | Theorem N |
| Fix 4 (projection-based transport) | Not a connection | C3 |
| Fix 5 (H = Delta Delta eps^2) | Wrong object; eps^1 measured | Theorem D |
| "M1 and M3 confirm consequences 1-2" | Consequence 1 yes; consequence 2 no | C5 |
| Status: "missing ingredient = proof of A4" | Resolved negatively; replaced by Theorem N + D | Section 2 |
