# Tie-Break Robustness and Journal-Format Completion — Evaluation

**Round:** 2026-09-02 ("v2 now clean" review: 4 residual risks, 5 advice
items)
**Task:** evaluate and verify before implementing; respond in English;
commit and push.
**Protocol:** R/D/E discipline (verify every premise against committed
artifacts; fix defects before implementing; never promote a conjecture).

---

## 1. Verification of the review's premises (all five verified)

| # | Review premise | Verdict | Evidence |
|---|---|---|---|
| 0 | "The 12-page v2 is a good skeleton; not the final paper" | **VERIFIED** | `pdfinfo`: 12 pages at round start; 0 `\cite` commands, no `\bibliography`, no figures, Methods = 3 paragraphs — a skeleton by construction |
| 1 | Tie-break dependence of κ^μ: manuscript lacks a robustness table across tie-break variants | **VERIFIED (gap confirmed)** | `rem:lock` declares the lex tie-break and cites ρ = 0.99998 — a *metric* comparison on the *same* tie-break — and E-V7's trajectory substitutions keep the same declared selection. No experiment varies the selection rule itself. **Closed by V8 below.** |
| 2 | 440 vs 424/433 number consistency; every number must trace to one artifact | **VERIFIED (the risk is real and productive)** | v2 contains 424/433 (correct); 440 exists as a *reaction-level* count in the V5/V8 artifacts (`n_events_rxns`); the near-collision of 424/433/435/438/440/525/537 motivated the full audit, which found **8 manuscript defects** (D-N1..D-N8) |
| 3 | v2 lacks full bibliographic formatting, formal captions, supplementary, extended methods | **VERIFIED** | zero citations, zero figures, 3-paragraph Methods at round start; now fixed (see §4) |
| 4 | Categorical/HoTT material must be preserved, not discarded | **VERIFIED (the v2 promise was unfulfilled)** | v2's Discussion promised "a companion document" but no companion artifact existed; the frozen v21 (10,830 lines) holds the material. **Now built** (see §5) |

**Review defects found (2, both minor):**

| # | Defect | Disposition |
|---|---|---|
| D-S1 | "The 440 vs 424/433 discrepancy is minor" — the discrepancy is not *in* the manuscript: 440 traces to a real artifact key (reactions with D₂ > 1e-8), and the previous round's D-R1 documented the external review's "440 reaction events" as matching no *panel-level* artifact. The correct action was not "fix a number" but "add a counts ledger" — done (Appendix A of v2). | documented; ledger added |
| D-S2 | "lacks ... supplementary material" — v2 had an appendix (porting map) and inline proofs; the actual gaps were bibliographic formatting, captions, Methods depth. | implemented precisely |

---

## 2. V8 — the tie-break robustness experiment (risk 1 / advice 1)

**Design.** V5/V6 protocol frozen (iJO1366, E22 physiology, 8× refinement =
57 grid points, E24 panel of 433 genes, M3D carbon-depletion maxFC
response, reference-level confound control); only the **stage-3
tie-break** of the engine varies:

| Variant | Rule | n_nz | r | partial r | ρ_S vs TB0 | genes changed |
|---|---|---|---|---|---|---|
| TB0 (declared) | w ~ U(0.5,1.5) seed 20240901, min wᵀv | 424 | **+0.3954** | +0.269 | — | — |
| TB1 (fresh seed) | same family, seed 20240902 | 426 | +0.3861 | +0.270 | 0.99998 | 91 |
| TB2 (family swap) | w ~ LogN(0,1) clipped [0.05,20], seed 20240903 | 424 | +0.3954 | +0.269 | 0.99999 | 90 |
| TB3 (rule swap) | min Σ w_r(f_r+r_r) (weighted \|v\|) | 425 | +0.3959 | +0.269 | 0.99897 | 109 |
| TB4 (adversarial) | max wᵀv (far end of pinned face) | 424 | +0.3954 | +0.269 | 0.99998 | 117 |

**Control:** TB0 reproduces V5 digit-exactly (r = +0.3954, p = 2.6e-17).

**Findings.**
1. **The association is stable:** r ∈ [+0.386, +0.396] (max deviation
   0.009; all p ≤ 1.4e-16); partial r constant to three decimals
   (+0.269–+0.270).
2. **The tie-break genuinely binds** — an honest, informative negative
   inside the robustness result: the stage-2-pinned optimal face is
   multi-vertex; the alternative rules select different flux vectors at
   all 57 grid points (max ‖Δv‖∞ up to 5.0), changing per-gene κ^μ for
   90–117 of 433 genes. Yet the per-gene ranking is essentially
   unchanged (ρ_S ≥ 0.99897), the changed values are small on the κ^μ
   scale (max 9.3e-5), and the TB1 deviation of 0.009 traces to two
   boundary genes entering the nonzero support (424 → 426), not to a
   reshaping of the metric.
3. **The value layer is exactly invariant:** stage-1 biomass μ and
   stage-2 ℓ₁ mass s² agree across all variants to **0.0** —
   Proposition (alex) (tie-break-freeness of the value layer),
   *measured* on the full E24 trajectory. This is the cleanest
   empirical form of the value/flux layer separation.

**Interpretation.** The declared selection is a convention; the value
layer does not see it; and the flux-layer association is a property of
the lexicographic protocol class, not of one rule. This closes the last
methodological gap named by the review.

Artifacts: `scripts/v8_tiebreak_robustness.py`,
`download/deepseek_bridge/v8_tiebreak_robustness.{json,csv,png}`.

---

## 3. The numeric consistency audit (risk 2 / advice 5)

**Method.** `scripts/audit_v2_numbers.py` loads each committed artifact
(json/csv/txt under download/), extracts the relevant number, and
compares against the manuscript claim at the manuscript's stated
precision; claims whose artifacts store only derived statistics are
recomputed from deposited per-gene data (E22-2R recomputes the active
reaction census from 8 fresh plain-FBA solves; V6-7 refits the affine
growth law over 57 fresh lex solves; E25/E26/E27 recompute all
correlations from the deposited CSVs). Frozen artifacts are never
edited.

**Result: 73 checks, 73 PASS (after manuscript repairs), 8 manuscript
defects found and fixed (D-N1..D-N8):**

| # | Defect | Repair in v2 |
|---|---|---|
| D-N1 | "Twelve parameter sweeps (… eight gene knockdowns)" | 13 sweeps, 10 knockdowns (m1_summary.json; the M1 report's own "8 genes" table entry is its internal error) |
| D-N2 | "\|cᵀΔv′\| ≤ 1.5×10⁻⁷" | ≤ 1.51×10⁻⁷ (ax8c: 1.506e-7 — false by 0.4% at face value) |
| D-N3 | "λ·h_max ≡ 0.500 across λ = 1..10¹²" | numerically 1..10⁶, analytic law at every scale, grid floors above 10⁷ (ax10) |
| D-N4 | generic TV ratio "3.7–4.4" | 3.6–4.4 (BT6 battery: [3.62, 4.39]) |
| D-N5 | "MWU p ≤ 10⁻⁴" | p ≤ 2×10⁻³ with 7 of 11 crossing sweeps at ≤ 10⁻⁴ (rpe 1.7e-3, tktA 1.6e-3, zwf 9.1e-4) |
| D-N6 | "segment residuals ≤ 8×10⁻¹⁴" | ≤ 1.2×10⁻¹⁰ (glucose 8e-14) + the documented eno sub-threshold kink at 4.1e-3 (which also explains eno's 0.934 event mass) |
| D-N7 | Abstract "100.0000%" | 93.4–100.0% per boundary-crossing sweep (10 of 11 exactly 1.000000; eno 0.9345) |
| D-N8 | "r = +0.03" (P2 shadow arm) | +0.032 to match artifact digits |

**Where the review's caveat was vindicated:** the defects D-N5/D-N6/D-N7
are exactly the "every number must trace to a single committed
artifact" class — headline numbers inherited from report *callouts*
rather than the artifact tables. Conversely, two v2 numbers the audit
*confirmed against the frozen v21's typos* (E23 union 537 and gene
count 525 match the v16 results json; the v21's 538/524 were the
errors) — the audit cuts both ways, which is the point.

**Counts ledger** (now Appendix A of v2): 2,583 / 438 / 440 / 433 /
424 / 426 / 435 / 454 / 537 / 525 / 1,516 / 2,779, each with meaning
and artifact source.

**Documented artifact quirks (not patched; frozen):**
- V5 json arm labels "(4x)/(8x)" swapped (cosmetic; the deposited csv
  is the 8x refinement and the reported +0.3954 is the 8x value);
- V6 partial p (0.93) not stored; recomputed from stored partial r and
  n — consistent;
- V1 value/flux ratio denominator (3807.6) lives in the committed
  report script, not the frozen json;
- the E22 plain-FBA census is solver-version-sensitive at ±1 reaction /
  ±2 class counts (recomputed 439/253/98/36/18/34 vs the v15 printout's
  438/254/96/36/18/34) — the gene-level panel (435) reproduces exactly;
  v2 Methods now states this.

Artifacts: `download/deepseek_bridge/v2_number_audit.{json,md}`.

---

## 4. v2 completed to journal format (risk 3 / advice 2)

The manuscript grew from 12 pages (skeleton) to **20 pages**, compiled
with tectonic, **0 undefined references**:

- **Full Methods** (5 subsections): the lexicographic pFBA engine with
  the three LP stages as display math, degeneracy documentation, the
  tie-break protocol with the V8 robustness pointer, the E22-census
  solver-sensitivity note; models and data provenance (iJO1366, iML1515,
  M3D with SHA-256 manifest, PRECISE, Schmidt 2016, PaxDb, GSE64021);
  panel construction and GPR association; statistical protocols
  (Pearson/Spearman/partial/permutation/bootstrap/deciles);
  reproducibility with the audit pointer.
- **Bibliography:** 25 verifiable references
  (`journal_manuscript_v2_refs.bib`), natbib/plainnat, cited throughout
  (FBA/pFBA/MOMA, PhPP, mpLP, Alexandrov, Monge-Ampère, Regge/Cheeger,
  Danskin, transport, data sources).
- **Five figures with formal captions**, all from committed artifacts
  (M1 summary, Theorem-C coupling, V5 primary association, V7 path
  robustness, V8 tie-break robustness), each referencing its artifact
  path.
- **Formal table** for E-V8 (tie-break robustness).
- **New [E-V8] section** with the three-finding interpretation.
- **Appendices:** (A) the counts ledger; (B) proofs and proof sketches
  for Theorem C, Proposition S, Proposition M (ported from the
  committed evaluation document, with the machine dossier numbers);
  (C) the Layer-1 porting map (updated).
- The E-series intro, rem:lock, Discussion Limitations, and the
  "companion document" paragraph all updated; the affine-law and
  shadow-arm numbers repaired (D-N8, D-R3 lineage).

Not done (deliberately, per advice 4): **E32 is not started** — it
remains demoted to honest status in the Discussion; the review's
instruction "not load-bearing for the current claim" is respected.

---

## 5. The categorical/HoTT companion (risk 4 / advice 3)

**Built:** `scripts/companion_categorical.tex` / `.pdf` (33 pages,
tectonic, 0 undefined references), assembled by
`scripts/build_companion.py` from the frozen v21 with recorded line
ranges. The split is a publication choice, not a deletion:

- **Extracted verbatim (8 sections):** Preliminaries (optic category),
  the SAVGS framework (2-categorical gluing theorem, Fisher-minimal
  transport law, autopoiesis closure test), the Bregman-Noether
  correspondence, the seven-claim falsification hierarchy, the single
  composition theorem, per-optic Lipschitz constants / Banach
  contraction, the filtered-colimit RAF construction, and the
  ∞-categorical HoTT extension (univalence closure test).
- **Status preserved:** theorems stay theorems, conjectures stay
  conjectures, machine-verified claims keep their artifact pointers;
  the new front matter says exactly this.
- **Inventory guarantee:** Sec. 2 of the companion lists *every* v21
  section with its disposition (companion / main paper / frozen v21
  with artifacts) — nothing is silently excised; the frozen v21 and
  its Git history remain committed.
- **Cross-reference repair:** the 19 dangling references to
  non-extracted sections resolve to textual pointers ("(v21 18.8)")
  with the mapping recorded in the build script.
- **Bib repair:** two entries missing from the shared v21 bib
  (orth2011, adamek1994) were added — this also fixes the frozen v21's
  own undefined citations without touching its .tex.
- The main paper's Discussion now carries an explicit pointer to the
  companion (title, role, and the "preserved, not discarded" framing).

---

## 6. Advice-item scorecard

| Advice | Status |
|---|---|
| 1. Tie-break robustness check (2–3 alternative rules) | **EXECUTED (V8, 5 rules)** — stable (max deviation 0.009, partial constant); value layer exactly invariant |
| 2. Complete v2 to journal length/format | **EXECUTED** — 20 pages: full Methods, bibliography (25 refs), 5 captioned figures, formal table, appendices (ledger, proofs, porting map) |
| 3. Decide the categorical/HoTT subset explicitly | **EXECUTED** — companion document (33 pp) built from the frozen v21 with inventory; main paper keeps only the falsifiable content, companion explicitly linked |
| 4. Do not start E32 until the main paper is near final | **RESPECTED** — E32 not started; stays demoted in the Discussion |
| 5. Final numeric consistency pass | **EXECUTED** — 73-check audit, 73 PASS after repairs; 8 defects fixed; counts ledger added; two artifact quirks documented |

---

## 7. Reproducibility

- V8: `python scripts/v8_tiebreak_robustness.py` (~1 min; requires
  cobra 0.32.1; the M3D compendium tarball re-downloaded and SHA-256
  verified against the committed manifest
  e73088f7b9318dd592a9790683fa1255c0dfc38f7813ff2a744ee2dd73fa976e).
- Audit: `python scripts/audit_v2_numbers.py` (~2 min; includes fresh
  lex solves for the affine-law check and the plain-FBA census
  recomputation).
- Companion: `python scripts/build_companion.py` then
  `tectonic scripts/companion_categorical.tex`.
- Manuscript: `tectonic scripts/journal_manuscript_v2.tex` (bibtex
  automatic).

## 8. Bug honesty

- The V5 frozen artifact's "(4x)/(8x)" label swap and the V6 unstored
  partial p were documented rather than patched (frozen artifacts are
  not edited); both are noted in the audit and the counts ledger.
- The audit itself required two repair iterations mid-round: initial
  versions mis-scoped the M1 claim (including negative controls),
  used 4-digit tolerances too tight for 2-decimal manuscript
  roundings, and mis-attributed the E27 transcript contrast; each was
  caught by re-reading the artifact structures before any FAIL was
  reported as a manuscript defect.
- The E22 census recomputation differs from the v15 printout by one
  active reaction (solver degeneracy); this is disclosed in v2
  Methods rather than silently reconciled.
