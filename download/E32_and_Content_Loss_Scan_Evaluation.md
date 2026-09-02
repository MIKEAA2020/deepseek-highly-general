# E32 Execution and Deep Content-Loss Scan — Evaluation Report

Round: 2026-09-02 (user tasks: "1- execute E32; 2- check latest manuscript
version against previous drafts: any accidental content loss? condensation
of legit content? anything worth restoring, either as is or after
corrections? scan deep").

Deliverables of this round:

| Item | Artifact |
|------|----------|
| E32 experiment (5 arms) | `scripts/e32_event_measure_stabilization.py`, `download/deepseek_bridge/e32_event_measure_stabilization.{json,csv,png}` |
| Content-loss scan | `scripts/scan_content_loss.py`, `download/deepseek_bridge/v2_content_loss_scan.json` |
| Flagged-env classification | `scripts/classify_flagged_envs.py`, `download/deepseek_bridge/v21_flagged_env_classification.json` |
| Block survival trace | `scripts/trace_non_surviving_blocks.py` (console report) |
| Manuscript updates | `scripts/journal_manuscript_v2.{tex,pdf}` — new [E-E32] section + figure, E22 panel-construction checks restored, abstract/intro/contributions/limitations/porting-map/ledger updates; now 22 pages, 0 undefined references |

---

## Part I — E32: event-measure stabilization (Glivenko–Cantelli type)

### Design

E32 asks the near-term statistical form of the frozen v21's Route-5
question (*do the empirical event point measures of the lex-pFBA map
converge as the sampled family grows?*). The metric is the
bounded-Lipschitz distance (domains normalized to unit diameter, where it
equals W1; exact in 1D, transport LP in 2D), each arm carries a
permutation null (event locations replaced by uniforms, panel structure
kept), and the 1D arms carry the classical Glivenko–Cantelli asymptotic
constant C = ∫√(F(1−F))dx of del Barrio–Giné–Uzet computed from the
population. Five arms over three existing data sources:

| Arm | Source | Result (verdict, traced to json) |
|-----|--------|----------------------------------|
| A1 (d=1) | M4b random cuts: 4,000 cuts through the 34×34 (q_glc, q_O2) signature census (350 boundary edges), 25,107 pooled cut events | **STABILIZES AT GC RATE** — tail slope −0.492 vs null −0.506; measured/null ratio 1.24 at the largest panel; iid prediction C/√n matches to 2.5% at the largest panel (mid-range deviations up to 8%) |
| A2 (d=2) | same, pooled 2D locations (transport LP) | decays with the panel; reference-noise floor at large n (capped LP atoms); consistent with the d=2 GC rate |
| B | thirteen M1 parameter sweeps (2 affine, 11 event-bearing) | **STABILIZES** — mid-range heterogeneity penalty ≈1.5× the uniform null (traced: 0.0991/0.0651 = 1.52 at the mid-range size m=6); tail faster than iid-GC = the finite-population correction √((13−k)/12) of sampling without replacement from 13 heterogeneous sweeps |
| C1 | E24 gene panel (κ^μ over 424 nonzero of 433 panel genes) | **STABILIZES AT GC RATE** — measured effective constant ≈1.9–2.1 across panel sizes against the population GC constant C = 2.4948 (log10 κμ axis); the association itself stabilizes at r ∈ [+0.389, +0.397] for m ≤ 256 with the Fisher SD 1/√(m−3) |
| C2 | E24 trajectory (one TB0 declared lex-pFBA engine run, 57 points) | the event point measure is a **four-atom object** — the four design corners carry the entire flux-layer mass 288.77 (the V5 mass to the digit); anchor-preserving thinning reproduces it exactly at every panel size (shape distance 0, mass error ~1e-12, value-kink census ≡ 4); uniform thinning decays by corner censoring (shape distance 0.121 → 0.005, mass error 26% → 0.13%, zero by m = 43) |

### Interpretation (as integrated in the manuscript)

The mean-field instinct is confirmed in its statistical form — the
empirical event measures over random panels (cuts, sweeps, genes) are
Glivenko–Cantelli objects — and simultaneously sharpened: stabilization
has two regimes, statistical for random panels and structural (exact,
design-immediate) for designed panels. The C2 result is the one-chamber
structure of E-V6 in its event form, and the resolution effect is the
L1-reconstruction regime of Theorem B′(iv). The deterministic
refinement-sequence form (Route 5 proper: model-family sequences) remains
open and is stated as such.

### Numeric verification of the manuscript claims (this session)

Every E-E32 manuscript number was re-checked against the committed JSON:
tail slopes (−0.49218 / −0.50608), ratio 1.24 (0.00990/0.007957),
C = 2.49 (2.49488), mass 288.77 (288.76892), panel counts (4,000 cuts /
25,107 events / 350 edges / 34×34), C2 curve values (0.121→0.005,
0.261→0.001, zero at m=43), anchor exactness (bl ≡ 0.0, kinks ≡ 4),
B-arm mid-range ratio (1.52), C1 association bracket
(r ∈ [0.389, 0.397], Fisher SD column = 1/√(m−3)). All traced.

Two precision defects found and repaired (audit discipline):

- **D-E32-1**: "iid prediction C/√n matches the measured curve to 2%" —
  the actual largest-panel deviation is 2.53% and mid-range deviations
  reach +8.2% (m=128) / −4.9% (m=4). Repaired in section text and figure
  caption to "2.5% at the largest panel (mid-range deviations up to 8%)".
- **D-E32-2**: "stabilizes at the GC rate with the predicted asymptotic
  constant (C = 2.49)" — the measured effective constant is ≈1.9–2.1
  (77–84% of the population BGU constant; finite-sample level of the W1
  bridge). Repaired to state the measured effective constant against the
  population constant, in both section text and caption.

Artifact quirks documented, not patched (consistent with the project's
bug-honesty convention):

- The C1 association curve's m = 424 row is a single WITH-replacement
  draw (the script's `replace=(m > ok.sum()//2)` boundary flips at
  m > 212), giving r = 0.325 with sd = 0.0 (one replicate) — not the
  full-panel value 0.3954 (which is stored separately as
  `r_full_nonzero` and matches V5). The manuscript does not cite the
  m = 424 row.
- The same with-replacement boundary applies to the m = 256 points
  (bootstrap semantics rather than subsample semantics); the C1 bl curve
  at m = 424 is the population self-distance (0.0 by construction).
- The B-arm population is k = 13 sweeps, so the largest without-
  replacement subset is k = 12; the curve excludes k = 13 (noted in the
  json).

---

## Part II — Deep content-loss scan

### Method

Three independent passes:

1. **Version-chain inventory** (scan_content_loss.py): structural
   inventory (sections, theorem-class environments, paragraphs, E-items,
   tables, figures, labels, citations, word counts) of all five v2
   versions — L0 8pp (51ce934) → 8pp (3c0f876) → 10pp (3cc5f8a) →
   12pp (f3342b1) → 20pp (828c89a) — with set diffs between successive
   versions.
2. **v21 coverage**: every v21 environment (332 total) checked for
   verbatim label/title presence in the 20pp v2 and the 33pp companion;
   flagged items then classified by **body-text 5-gram containment**
   (classify_flagged_envs.py) to separate title-repair false negatives
   from genuinely frozen-only material.
3. **Condensation detector**: >40-word content blocks tracked across
   versions by leading-25-word hash (scan) plus a 5-gram survival trace
   for every non-surviving block (trace_non_surviving_blocks.py).

### Finding 1 — No accidental content loss in the v2 lineage

| Transition | envs | sections | words | dropped envs | dropped sections |
|------------|------|----------|-------|--------------|------------------|
| L0 8pp → 8pp | 14 → 20 | 18 → 19 | 2,825 → 3,474 | 0 | 0 |
| 8pp → 10pp | 20 → 25 | 19 → 21 | 3,474 → 4,447 | 0 | 0 |
| 10pp → 12pp | 25 → 28 | 21 → 24 | 4,447 → 5,756 | 0 | 0 |
| 12pp → 20pp | 28 → 33 | 24 → 31 | 5,756 → 8,321 | 0 | 0 |

Monotone growth at every level; the only dropped paragraphs anywhere in
the chain are the three 12pp Methods stubs ("Engine.", "Data.",
"Reproducibility.") — replaced by the full five-subsection Methods of the
journal-format completion, which subsumes them.

### Finding 2 — No illegitimate condensation

Block-level trace of the 12pp → 20pp transition (the only transition
with non-verbatim blocks): of 52 content blocks, 49 survive reworded
(≥60% distinctive 5-grams), 1 partial, and the only 2 below 25% survival
are exactly the old "Data." and "Reproducibility." stubs whose content
the new Methods covers in greater depth (the "Reproducibility" stub
already shows 14 of its 4-grams inside the new text). No block with
legitimate content was compressed or lost. No shrink >25% anywhere in
the chain.

### Finding 3 — v21 coverage: everything is either ported, companioned, or dispositioned

- 115 v21 environments live verbatim in the companion; 28 in the v2.
- The scan's title-match flagged 212 entries (117 unique; the rest are
  v21-internal duplicate restatements of the same items). Body-text
  classification: **1 title-repair false negative** (the 2-categorical
  gluing theorem — present in the companion at 88% body containment,
  title adjusted by the cross-reference repair) and **116
  frozen-v21-only** items.
- All 116 trace to v21 sections whose dispositions are explicitly
  recorded in the companion Sec. 2 inventory (nothing silently
  excised, by construction): the algorithmic rate-distortion / κ_geo
  theory (superseded by the measure-theoretic κ^μ — the κ_geo panel
  weakness is documented in the main paper), the autopoiesis
  closure-test executions A–K (frozen with artifacts), Claims F/G
  foundational tests, the n=3 / n=4 prototypes, the Lévy 3/2 fatigue
  derivation, the CPTP–Zeno lift, and the elevation studies E1–E20
  (superseded by the locked-metric E-series).

### Finding 4 — Restorations executed

One genuine restoration, already integrated: the **E22 panel-construction
four verification checks** (GPR mapping correctness with 0 failures over
120 gene–reaction pairs; κ_V definition consistency; distinctness —
exactly one shared b-number b2097 with the MAPPED-15; non-zero variation
435/435) — v21 §E22 material that the v2 condensation had dropped and
that materially strengthens §6.1's panel-construction claim. Verified
against v21 lines 8275–8300.

**Nothing else qualifies for restoration.** The remaining frozen-v21-only
material is either (a) superseded in corrected form in the main paper
(κ_geo → κ^μ; Theorem B → Theorem B′), (b) a different research line not
load-bearing for the κ^μ paper (closure tests, quantum CPTP, fatigue), or
(c) preserved verbatim in the frozen v21, which remains committed in the
repository. Restoring any of it would re-bloat a deliberately 22-page
main paper; the companion was designed as the routing for heavier
theory, and the frozen v21 remains the archival record.

### Manuscript state after this round

22 pages (20 + the E-E32 section and figure + the restored E22 checks),
tectonic rebuild clean, 0 undefined references, 0 multiply-defined
labels. The E-E32 section reports the two-regime result; the abstract,
contributions list, limitations, reproducibility paragraph, Layer-1
porting map (Appendix C: "V6/V7/V8/E32 new"), and counts ledger (three
new rows: 4 trajectory atoms / 350 M4b boundary edges / 25,107 cut
events) were updated consistently. The Discussion's open-items list no
longer carries E32 as deferred — the statistical form is executed and
the deterministic Route-5 form is stated as the remaining open question.

---

## Reproducibility

```
python3 scripts/e32_event_measure_stabilization.py      # ~77 s, includes one 57-solve TB0 engine run
python3 scripts/scan_content_loss.py                     # requires the five version .tex files (reconstructible from git history)
python3 scripts/classify_flagged_envs.py
python3 scripts/trace_non_surviving_blocks.py
tectonic scripts/journal_manuscript_v2.tex               # 22 pages, 0 undefined refs
```

All numbers in this report were re-derived from the committed artifacts
during verification.
