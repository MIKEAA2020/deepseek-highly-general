# Metric Lock and Path Robustness: Evaluation of the Completed-Round Review

**Target:** the completed-round external evaluation ("Evaluation of the
completed round" + residual risks + recommended next steps + the R/D/E
hierarchy, received 2026-09-02). This review assesses the previous
round's closures (Theorem C, the signed crease layer, the V6 layer
decision) and conditions the Layer-1 porting on four further items.

**Machine batteries (this round):**
- `scripts/v7_path_robustness.py` (V7: three trajectories, chamber
  classification, layer arms) →
  `download/deepseek_bridge/v7_path_robustness.{json,csv,png}` +
  per-path CSVs
- `scripts/precise_arm_kappamu.py` (the PRECISE-arm replication with
  the locked metric) →
  `download/deepseek_bridge/precise_arm_kappamu.{json,txt}`

**Standing instructions honored:** verify, do not trust (the review's
own numbers were checked against the artifacts first); evaluate
jointly with the six-audit corpus; strengthen, correct, complete
weaker suggestions and defects before implementing; v21 frozen; every
implemented claim carries a machine dossier; commit and push.

---

## 1. Executive verdict

The review is **sound in substance and correct in its four
recommendations** — all four are now executed. Its assessment of the
three closures is accurate (W1: the identity is sound and the value
measure is a contraction; W2: the semiconvexity refutation is correct
and the signed-measure repair legitimate; W3: the V6 one-chamber
result is decisive for the E24 path). Verification found **five
defects in the review itself** (three factual/precision, two
conceptual), none of which changes a conclusion; one of them exposed a
genuine imprecision in *our own* v2 text, which is now repaired. The
headline of the new execution (V7): **the one-chamber property is
path-dependent — it fails on the oxygen-limitation and acetate-switch
paths — but the layer decision survives in a stronger form: even when
the value layer is nonempty, it contributes nothing to the
association on any path, and the flux-layer association generalizes to
matched oxygen and carbon-switch responses.** The PRECISE-arm
replication closes the last open empirical item: the cross-platform
dissociation is metric-robust (it survives replacing the precursor
metric with the locked κ^μ).

| # | Review item | Verdict | Machine evidence |
|---|---|---|---|
| W1-assess | "Identity is sound for fixed c, consistent v*; value measure is a contraction, not an independent object; define κ^μ as the metric, value as derived diagnostic" | **ENDORSED and IMPLEMENTED** (with a provenance correction: the identity is immediate from the pointwise optimality Φ = cᵀv*, not the envelope theorem — see D-R2). The metric lock (v2 Remark rem:lock) states exactly this hierarchy | Theorem C dossier (prior round); v2 §3 |
| W2-assess | "Semiconvexity result classical and correct; signed crease repair legitimate but must be defined explicitly and stated as an extension of Alexandrov; determinant law needs normalization/sign conventions" | **ENDORSED and IMPLEMENTED**: new conventions remark (v2 rem:conventions) gives the signed density A_F = [∇(−Φ)]_F ⊗ n_F \|F\|, the eigenvalue-sign flags, the Alexandrov coincidence on the concave class, and the ½\|det\| / (1/p!)\|det\| fan-volume normalizations | v2 §3; AX-10/AX-9 dossiers (prior round) |
| W3-assess | "V6 decisive: one chamber on the glucose-decline path; association is flux-layer; value-layer null" | **ENDORSED with corrected numbers** (D-R1: 424, not 440; D-R5: the +0.032 arm is the shadow-price arm, the direct value arms are structurally degenerate — stronger than null) and **EXTENDED by V7** (the property is path-dependent; the decision is not) | V6/V7 JSONs |
| R1 | Path dependence: test multiple paths or state condition-specificity | **EXECUTED (V7)**: P1 oxygen limitation → 3 genuine chamber crossings; P2 acetate switch → 4 (two large); value arms contribute nothing on either; flux association survives with matched responses | v7_path_robustness.json |
| R2 | OR-GPR signed measures: show tie-break independence or state the lexicographic tie-breaking | **CORRECTED then IMPLEMENTED** (D-R4): independence is the wrong demand for the flux layer — it is selection-dependent by construction; the tie-break is now *declared as part of the metric's definition* (rem:lock), the value layer's exact invariance and the c-contraction are the theorem, and association robustness is *measured* (rank identity 0.99998; V7 trajectory substitutions) | v2 rem:lock; E-V5/E-V7 |
| R3 | Determinant law is MA-layer: clarify which layer is correlated | **IMPLEMENTED**: rem:lock(iv) names the layer — the codim-1 Hessian/crease layer of the flux map; the MA atom layer is the dual-face diagnostic, concave class only | v2 §3 |
| R4 | Novelty: application, not theorem; state it plainly | **IMPLEMENTED**: new Discussion paragraph "What this paper is and is not" | v2 §7 |
| Step 1 | Lock the metric definition | **DONE**: rem:lock (carrier, tie-break, mass convention, value-as-diagnostic, layer assignment, measured robustness) | v2 |
| Step 2 | Test path robustness before porting | **DONE (V7)** — and the porting proceeded only after it | this document §3 |
| Step 3 | Layer-1 porting of E22–E27 + PRECISE arm concurrently | **DONE**: E22/E23/E25/E26 ported with R/D/E discipline (E24→E-V5 extended with the PRECISE arm; E27 already ported; V6/V7 blocks new); PRECISE arm run with κ^μ | v2 §6; precise_arm_kappamu.json |
| Step 4 | Do not overclaim Alexandrov novelty | **DONE**: Discussion paragraph + intro claim list kept at application level | v2 §7 |

---

## 2. Defects found in the review (verify, do not trust)

- **D-R1 (factual).** "the flux layer contains 440 reaction events."
  No artifact contains 440. The V6 census: 424 of 433 panel genes have
  nonzero κ^μ (the association n), 4 value kinks (all anchor corners),
  71–197 reactions per dual jump. The correct statement is in v2 E-V6.
- **D-R2 (provenance precision).** "The identity ΔΦ′ = cᵀΔv′ is a
  consequence of the envelope theorem." It is immediate from the
  pointwise optimality identity Φ = cᵀv* for a consistent
  (lexicographic) selection — no envelope argument is needed. The
  envelope (Danskin) theorem is the *dual* statement, ∂Φ/∂θ = shadow
  prices, which the manuscript uses separately and verifies to 6–7
  digits (E-V1). Conflating the two understates the identity's proof.
- **D-R3 (exposed a defect in our own text — productive).** The review
  writes "the value function is affine" for the E24 path. Correct in
  substance (single chamber), but the v2 E-V6 text had overreached
  further, stating μ(t) = Y·q_glc(t) — proportionality, which is false
  at the anchors (μ = 0.48465 at q_glc = 5, not 0.4977). Repaired to
  the true affine law: dμ/dq_glc = Y = 0.099544 (= the constant
  glucose shadow price; intercept −0.0124). The review's looser
  phrasing "affine with constant shadow prices" is exactly right.
- **D-R4 (ill-posed demand).** "Its independence from tie-breaking
  must be shown for OR rules." For the *value* layer this is already a
  theorem (selection-free; Prop. alex). For the *flux* layer it is
  impossible by construction: D²v* depends on the selection, and the
  lexicographic tie-break is part of what defines κ^μ. The correct
  demands — now implemented — are (i) declare the tie-break in the
  metric definition, (ii) the c-contraction invariance (Theorem C)
  as the exact bridge, and (iii) *measured* robustness of the
  association under the declared selection (rank identity 0.99998;
  V7's trajectory substitutions reproduce the association on two
  further paths).
- **D-R5 (imprecision).** "the value-layer correlation is null
  (r = +0.032)" — the +0.032 arm is the *shadow-price (dual)* arm
  (n = 51). The direct value-layer arms are not null but
  *structurally degenerate* (c-attribution: 0 of 433 genes), which is
  the stronger statement and the one the manuscript makes.

No defect changes any of the review's conclusions; the recommendations
were implemented with these corrections folded in.

---

## 3. V7 — path robustness (the review's residual risk 1, executed)

Frozen: engine, seed 20240901, iJO1366, panel, statistics. Varied:
the trajectory and its matched response. Kink classification (new,
repaired mid-round): the parameters are the uptake bounds, so
∇Φ = (y_glc, y_O2, y_ac); a kink is a **design corner** iff it sits
at a trajectory anchor *and* the uptake shadow prices are continuous
across it (jump ≤ 1e-9); a **chamber crossing** iff they jump.

| Path | Design | Chamber crossings | Value strain / flux strain | A κ^μ r (matched response) | Best value-layer arm |
|---|---|---|---|---|---|
| P0 glucose decline (V6 control) | E22 anchors | **0** (4 design corners, dual jumps = 0) | 1.45e-3 | **+0.3954** (partial +0.2692; carbon depletion) — V6 reproduced digit-exactly | B3all +0.032 (n=51, null) |
| P1 oxygen limitation | q_glc = 5 fixed; q_O2 22→1 linear | **3** (q_O2 ≈ 9.3, 6.3, 2.9; \|ΔΦ′\| up to 0.68; y_O2 jumps +0.032 at the respiratory boundary) | 2.38e-4 | **+0.3183** (partial +0.2583, p = 6.4e-8, n = 426; M3D WT anaerobic vs aerobic) | B3int −0.170 (n = 68, null-negative) |
| P2 acetate switch | q_O2 = 22; glucose 5→0, acetate 0→10 | **4** (two large near the glucose–acetate handoff; two micro-slivers, dual jumps ~1e-4) | 5.53e-4 | **+0.2234** (partial +0.1598, p = 9.3e-4; M3D acetate vs glucose switch) | B3int +0.032 (n = 71, null) |

**Findings.**
1. **The one-chamber property is path-dependent.** It is a property of
   the glucose-decline design (o2 kept in excess throughout), not a
   law: P1 crosses three chamber boundaries, P2 four. The manuscript
   now states the condition-specificity explicitly — the honest form
   of the review's "either test multiple paths or state it".
2. **The layer decision survives — in the stronger form.** When value
   kinks *do* appear, they contribute nothing: the c-attribution arm
   is degenerate on every path (0/433 — the sparse-objective
   corollary is path-free, as Theorem C predicts); the
   chamber-crossing shadow-price arm is null-to-negative (−0.17 / +0.03);
   value-gated flux strain is a subset of κ^μ (equal or weaker on
   every path, never stronger). "The signal is flux-layer specific"
   generalizes from "the value layer is empty" to "the value layer is
   empty *or irrelevant*".
3. **The association itself generalizes.** With matched responses: P1
   vs the M3D anaerobic contrast r = +0.318 (partial +0.258);
   P2 vs the M3D acetate-switch response r = +0.223 (partial +0.160).
   Cross-path predictor robustness: the P1/P2 κ^μ vectors correlate
   with the E24 carbon response at r = +0.378 / +0.391 — the per-gene
   ranking is largely trajectory-independent, so the E24 association
   is not an artifact of one trajectory's event times.
4. **Theorem C holds at every kink on all three paths** (identity
   error 0.0; worst 1.6e-15) — now verified on 12 kinks across three
   physiologies, not just the E24 path.

---

## 4. The PRECISE-arm replication (the review's step 3, executed)

The v17/E24 round had run the PRECISE carbon-switch arm only with the
precursor κ_V predictor (r = −0.054, NS). Re-run with the locked κ^μ
(frozen V6 vector, n = 424 nonzero):

| Response | r | p | partial (ref level) |
|---|---|---|---|
| E24 carbon depletion (reproduction anchor) | **+0.3954** | 2.6e-17 | +0.2692 |
| M3D microarray switch glycerol | +0.1949 | 5.3e-05 | +0.1128 |
| M3D microarray switch acetate | +0.1664 | 5.8e-04 | +0.0931 |
| M3D microarray switch proline | +0.1752 | 2.9e-04 | +0.0847 |
| M3D microarray switch MAX | +0.2063 | 1.9e-05 | +0.1141 |
| PRECISE RNA-seq galactose | −0.0875 | 0.072 | −0.0910 |
| PRECISE RNA-seq glycerol | +0.1263 | 9.2e-03 | +0.1441 |
| PRECISE RNA-seq acetate (wt_ac) | +0.1297 | 7.5e-03 | +0.1233 |
| PRECISE RNA-seq fructose (wt_fru) | +0.0985 | 4.3e-02 | +0.1180 |
| PRECISE RNA-seq MAX (10 WT conditions) | **−0.0443** | 0.36 | −0.0878 |

**Verdict.** The cross-platform dissociation is **metric-robust**:
same-platform carbon switching replicates with κ^μ (+0.17…+0.21) while
the cross-platform PRECISE aggregate does not (−0.044, NS; per-condition
heterogeneity: glycerol/acetate/fructose weakly positive, galactose
negative). The honest negative stands, now verified with the locked
metric rather than inherited from the precursor — exactly what "run
the PRECISE-arm replication" required. The interpretation is
unchanged: the association is specific to the carbon-exhaustion class
and the platform-matched design.

---

## 5. Manuscript integration (v2; v21 untouched)

1. **§3 [D2] new Remark (Locked status, tie-breaking, layer
   assignment)** — the metric lock: carrier = flux-layer signed crease
   measure of the lex-optimal flux; tie-break declared as part of the
   definition; unsigned total-variation masses; value layer = derived
   diagnostic only ("no claim of this manuscript attributes
   transcriptional response to Alexandrov curvature of the value
   function"); layer assignment = codim-1 Hessian/crease layer, not
   the MA atom layer; measured robustness (rank identity, V7
   substitutions).
2. **§3 new Remark (Sign and normalization conventions)** — the
   explicit signed-measure definition (A_F = [∇(−Φ)]_F ⊗ n_F \|F\|,
   eigenvalue sign flags), the statement that this *extends
   Alexandrov's setting* (coincides with it on the concave class),
   and the determinant-law normalizations (½\|det\| = fan volume;
   (1/p!)\|det\| for simplex fans; signed determinants only in the
   concave class).
3. **§6 [E-V6] repaired** — the affine law stated correctly
   (dμ/dq_glc = Y = 0.099544, the constant glucose shadow price;
   intercept −0.0124; zero chamber crossings), replacing the
   proportional form.
4. **§6 new [E-V7]** — the path-robustness block: chamber test,
   path dependence of one-chamber, layer-decision survival, the
   matched-response generalizations, the cross-path predictor
   robustness, the 12-kink coupling-identity record.
5. **§6 [E-V5] extended** — the PRECISE-arm table sentence
   (same-platform replication, cross-platform dissociation,
   metric-robustness of the honest negative).
6. **§6 Layer-1 ports**: [E-E22] panel and GPR classes; [E-E23]
   multi-condition support; [E-E25] the 2×2 platform-by-class
   disambiguation (with the honest note that it was executed with the
   precursor metric, rank-equivalent at ρ = 0.99998); [E-E26] protein
   abundance vs change. [E-E27] unchanged.
7. **§7 Discussion**: new "What this paper is and is not" paragraph
   (application, not theorem; classical machinery; nearest prior art
   named); Limitations updated (one-chamber condition-specific, layer
   decision path-robust; PRECISE dissociation as a bound on
   generality; tie-break declared).
8. **§1 Introduction** claim list updated (E-series now includes the
   V7 generalizations); Methods and porting map updated. Recompiled:
   12 pages, zero undefined references.

---

## 6. R/D/E discipline this round

- **R**: V7 numbers (crossing census, arm table, matched-response
  associations, coupling identity at 12 kinks); the PRECISE-arm table;
  the E22/E23/E25/E26 verified statistics; the repaired affine law
  (machine-checked against the V6 run: slope values
  0.099544·ΔΔq·7 = 0.418 total strain, digit-exact).
- **D**: the precursor κ_V family's panel-level weakness is retained
  as a *demoted* framing (it motivated the recalibration; its
  cross-platform behavior is now superseded by the κ^μ replication);
  E25's execution under the precursor metric is disclosed, not hidden.
- **E**: no diary, session, version-history, or audit-folder language
  entered v2; the R/D/E rubric supplied with this review is recorded
  here (in the audit response document, not the manuscript) and
  governed the porting.

---

## 7. Reproducibility and bug honesty

- `python3 scripts/v7_path_robustness.py` (≈ 1 min; iJO1366; seed
  20240901; 171 lex solves + 22 stage-1 solves) →
  `v7_path_robustness.{json,csv,png}`, `v7_P0_glucose_decline.csv`,
  `v7_P1_oxygen_limitation.csv`, `v7_P2_acetate_switch.csv`.
- `python3 scripts/precise_arm_kappamu.py` (≈ 20 s; reads the frozen
  V6 κ^μ vector and the v17 per-gene response columns) →
  `precise_arm_kappamu.{json,txt}`.
- **Bug honesty note.** V7's first run classified kinks by *position*
  (anchor-adjacency). That rule — inherited from V6, where it is
  adequate because all four kinks sit exactly at anchors with zero
  dual jumps — misclassified P1's genuine chamber crossing at
  q_O2 ≈ 6.25 as an "anchor corner" (its cluster touched the anchor
  grid point). Caught by inspection of the uptake-dual jumps (0.013 /
  0.010 — a real ∇Φ jump), repaired to the chamber test stated above,
  and re-run; the V6-reproduction control confirms the repair changes
  nothing on P0 (still 4 design corners, 0 crossings, r = +0.3954
  digit-exact). The P1 t = 0.75 kink is now correctly counted as a
  crossing.
- Cross-references: `download/Value_Flux_Coupling_Evaluation.md`
  (previous round: Theorem C, Propositions S/M, V6),
  `download/deepseek_bridge/v6_layer_decision.json` (the frozen V6
  protocol that V7 varies), `download/novelty_v17_option_a_e24.csv`
  (the per-gene response columns the PRECISE arm reuses).
