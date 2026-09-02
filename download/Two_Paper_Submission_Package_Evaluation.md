# Two-Paper Submission Package — Round Evaluation and Execution Report

**Date:** 2026-09-02 (session round; journal-submission package finalized)
**Inputs:** user directives (1) commit+push with retained PAT; (2) triage any
remaining audit points worth implementing from `external_audits/2nd wave`;
(3) target journal must not require paying; (4) sentence-level flow scan;
(5) remnant/redundancy scan; (6) clarification-merit scan; (7) the two-paper
blueprint (main = load-bearing categorical parts only + cross-citation;
companion = full standalone theory paper; no verbatim duplication;
disclose in cover letter).
**Deliverables:** retargeted main paper (BMB), restructured standalone
companion theory paper, BMB reference generator, cover letter, scan
scripts, this report.

---

## 1. Premise verdicts

| # | Directive | Verdict | Action |
|---|-----------|---------|--------|
| 1 | commit + push, English, PAT retained | standing | done at end of round |
| 2 | remaining audit points worth implementing | 12 implemented this round; 5 verified already present; 6 rejected with reasons (§3) | executed |
| 3 | no-pay target journal | PLOS Comp Bio charges APC (~$3,190); **retargeted to Bulletin of Mathematical Biology** (Springer hybrid; free under the standard subscription route; author-year citations per BMB submission guidelines) — verified by web search | executed |
| 4 | sentence-level flow scan | strong (one investigation, clean transitions); 1 mid-round glitch fixed; 1 verbatim triple tightened | executed |
| 5 | remnant/redundancy scan | PLOS remnants 0; v21 body mentions 0 (both papers); overfull 26 → 4 (all ≤ 4pt or a pre-existing table-strut artifact) | executed |
| 6 | clarification-merit scan | 4 warranted non-superficial additions (L_var defined, E28 glossed, dynamic-range claim made verifiable); candidates rejected as decorative are listed (§6) | executed |
| 7 | two-paper blueprint | companion converted from verbatim archive to standalone theory paper; main paper carries [D5] brief adapted reading; cross-citations both ways; 0 verbatim prose overlap (7-gram scan); cover letter discloses | executed |

## 2. What was executed

### 2.1 Companion → standalone theory paper (`scripts/companion_categorical.tex`, 35 pp)

- **New front matter:** title "Stratified Connections, Optic Composition,
  and the Homotopy Fixed-Point Extension: A Categorical Framework for
  Viability-Weighted Curvature"; standalone abstract; "Preprint,
  September 2026" (was: "Companion document … not independently
  submitted in this form; extracted, not rewritten").
- **New Introduction** replaces "The role of this document": the problem
  (viability under constraint switching), a contributions list keyed to
  the paper's theorems, the division-of-labor paragraph with the
  cross-citation `\citep{zai2026measure}`, and honest status conventions
  (proof statuses labeled; two superseded lines of the predecessor
  explicitly NOT carried).
- **Removed:** the v21 inventory section ("nothing silently excised"
  table — dispositions live in the repository worklog/content-loss
  artifacts, not in a standalone paper) and the "Extraction record"
  section. All 92 v21 mentions converted (52 `\textup{(v21 X)}`
  pointers resolved to internal labels, prose rewritten, or re-scoped to
  the project repository).
- **Made self-contained** (previously dangling dependencies on an
  unpublished third manuscript): new `def:ard` (algorithmic
  rate-distortion distance), new `def:kv` (viability-weighted curvature
  — the central object, previously only a textual pointer),
  `def:realization` (the realization of an endo-optic as an endomap —
  the audit-flagged undefined functor R, now defined operationally with
  functoriality left open), `prop:vulnerability` (vulnerability ≤ κ_V,
  previously "Proposition (v21 20)"), `prop:treg-lip` (the KM-averaged
  Lipschitz bound for T_reg, previously "Proposition (v21 15)").
- **New Future directions and open problems section** (7 items: the
  closed-loop O(ε²) boundary term; endofunctor semantics; filtered
  colimits beyond Set; an explicit ∞-optic composition; sharpening the
  contraction bound; operational instantiations of κ_V; closure-test
  benchmarks not designed by the authors).

### 2.2 Audit-derived theorem repairs in the companion (the P4 tier)

| Repair | Source | Form |
|---|---|---|
| Piecewise-holonomy small-loop formula restated for **two transversal crossings**; boundary reset at its true order O(ε) (tangential variation of the transition function; O(1) parts cancel by the cocycle condition; abelian case exact cancellation derived) | joint-2nd-wave P4; own numerics (n_cross = 2, reset slope ε) | Theorem 3.6 restated + proof + numerics remark aligned |
| Matching condition O3 in the **standard gauge form** with an explicit frame-transition convention | deepseek #8; P4 | Definition 3.3 (O3) + eq:matching |
| "Unconditional" Banach contraction **renamed and parameter-scoped** | deepseek #9 | Theorem 7.3 "for the chosen seven-map instantiation" + uniformity-in-d |
| HoTT composition/fixed-point **proof-sketch status marked**; what is cited vs constructed named | deepseek #11; P4 | Remark 9.4 |
| Gluing-theorem **proof status** (reduction to cited stack-descent, not re-proved) | Line-level "proof by asserted Giraud axioms" | Remark 3.5 |
| κ_V(R_max) = 0 "falsifiable prediction" **re-scoped as a consistency check** (both sides vanish by construction) | Line-level "0=0" | Proposition 8.4 item 3 + Remark 8.5 |
| FBA-operational indicator-weighted κ_V **removed** from the theory paper (definition-shopping narrative; superseded by the main paper's locked metric) | GLM definition-shopping + label-leakage | Remark 3.14 (scoping pointer) |
| SAVGS tuple in thm:smallloop harmonized with the corrected 5-tuple (B, E, P, ε, Γ) | deepseek #4 (adjacent) | Theorem 3.7 |

**Not resurrected:** the smooth-surrogate/envelope line (v21 Lemma 4.10,
Theorem 4.11, Corollary 4.14 — all audit-flagged) is in neither submitted
paper; it is superseded by the main paper's measure-theoretic D-layer and
stays in the frozen v21. Repairing unsolicited theory was rejected as
out of scope.

### 2.3 Main paper (`scripts/journal_manuscript_v2.tex`, 21 pp)

- **BMB retarget:** PLOS Author Summary removed (PLOS-specific);
  keywords 8 → 6; natbib `[super,sort&compress]` → `[round]` (author-year);
  references regenerated as **27 BMB-style entries, alphabetical, with
  natbib author-year labels** (`scripts/build_bmb_refs.py` →
  `journal_manuscript_v2_bmb_refs.tex`); the companion added as entry
  `zai2026categorical`.
- **New §3.5 [D5] "The categorical reading, in brief"** (the user's
  blueprint): strata as a stratified base; the two companion bridge
  results summarized *in words* (no displayed duplication of the
  companion's construction); explicit division-of-labor paragraph with
  cross-citation; explicit statement that nothing in it is a premise of
  the empirical results.
- **Discussion paragraph rewritten** ("The companion theory paper"):
  division of labor, disclosed here and in the covering letter, no
  shared verbatim passages, neither paper depends on the other.
- **Layer-1 porting-map appendix removed** (internal provenance;
  contradicts the paper's own "no version history" policy); replaced by
  a 4-line provenance note pointing to the repository. Residual v21
  body mentions removed (E22 provenance parenthetical, E32 route-5
  framing, counts-ledger typo notes).
- **Typography:** overfull hboxes 26 → 4 (remaining: 3.8/2.4/1.3 pt +
  one pre-existing invisible table-strut artifact at 17 pt);
  filenames de-spaced with `\allowbreak` breakpoints; E-E32 heading
  shortened; counts-ledger table ragged-right.

### 2.4 Scans (machine-verified)

- **Cross-paper duplication** (`scripts/scan_two_paper_package.py`):
  38 shared 7-grams between the two papers, of which the only maximal
  run ≥ 7 words is a preamble-macro artifact (theorem-environment
  names). **Zero verbatim prose overlap** — the user's
  no-duplication rule is satisfied.
- **Intra-paper redundancy:** the one verbatim triple sentence
  (tie-break invariance, stated in §3, caption, and E-M1) tightened in
  §3 to a forward pointer; abstract/intro echoes of the headline
  finding retained (standard practice).
- **Remnants:** PLOS mentions 0; Author Summary 0; v21 in rendered body
  0 (both papers); "companion document" wording 0. Two flagged items
  are confirmed false positives (the word "supersedes"; a `%` source
  comment in the companion header).
- **Numeric audit:** `audit_v2_numbers.py` extended — JP-2/JP-3/JP-5
  retargeted from PLOS to BMB structure — **98/98 PASS** (all numeric
  claims still trace to committed artifacts after the edits).
- **Builds:** tectonic clean for both papers; 0 undefined references, 0
  multiply-defined labels.

### 2.5 Cover letter (`download/cover_letter_bmb.md`)

BMB; three-point significance case with manuscript-traced numbers; the
**required disclosure block**: related companion manuscript, division of
labor, availability (public repository + on request), not under
consideration elsewhere; explicit note that the standard subscription
route is intended (no open-access charges requested).

## 3. Audit triage — remaining points from `external_audits/2nd wave` (and related waves)

**Implemented this round (12):** the table in §2.2 (two-crossing formula;
standard gauge form; unconditional→scoped; HoTT sketch status; gluing
proof status; 0=0 re-scope; R defined; T_reg dependency internalized;
vulnerability prop inlined; FBA-κ_V removal; SAVGS tuple; plus the
main-paper accuracy items "thirteen-fold"→~130-fold with support ratio,
L_var defined, E28 glossed).

**Verified already present (5):** E-V8 tie-break table (JP-1 guard);
D_V ≠ κ_V identity honesty marker; filtered-colimits scoped to Set with
the lfp generalization recorded open; E25 0.191/0.187 reconciliation
(v21-round fix, inherited); all v21 P0/P1 mechanical corrections
inherited by v2's fresh text.

**Rejected / superseded / out of scope (6, with reasons):**
1. P4 smooth-surrogate repairs (Lemma 4.10 box, Thm 4.11 countable
   dense, Cor 4.14 deletion) — that line is in neither submitted paper;
   superseded by the main paper's D-layer. Repairing unsolicited theory
   is out of scope.
2. E13 Theorem A/B repairs — not extracted into either submitted paper
   (RAF filtered-colimits are; the terminal-coalgebra theorem is frozen
   v21 only).
3. Network-C closure re-implementation, E14 NE re-run, Phase-I endpoint
   sampling redesign — networks A–K/E14 are not in either submitted
   paper; repository-level future work.
4. Table 4 / conjecture-count / stale-abstract items — v20/v21-era;
   fully superseded by the v2 rewrite (fresh abstract, no Table 4, no
   conjecture-closure narrative).
5. P5 three-paper split — superseded by the user's two-paper decision,
   implemented this round.
6. Bibliography phantom-reference repairs — v2 has its own generated,
   key-resolved list (JP-5 guard); v21's bibliography is frozen
   history.

## 4. Journal decision record

- **PLOS Computational Biology (previous default): rejected** — gold-OA
  journal, APC £2,290 / $3,190 (verified via Springer/PLOS pages).
- **Bulletin of Mathematical Biology (new target): selected** — Springer
  hybrid; the standard subscription route carries **no author charges**
  (APC applies only to the optional open-access route; verified via
  Springer's how-to-publish page); author-year citations ("cite
  references in the text by name and year in parentheses" per BMB
  submission guidelines); publishes long methodological papers; strongest
  mathematical fit for the content.
- Alternatives documented: Journal of Theoretical Biology (Elsevier
  hybrid, free subscription route, author-year), Journal of Mathematical
  Biology (same model). Retargeting is mechanical via
  `scripts/build_bmb_refs.py` (regenerate the list in the target style
  and swap the natbib options).
- Companion venue (later decision): Theory and Applications of
  Categories (fully free) or Applied Categorical Structures are natural
  candidates; the companion is currently a self-contained preprint,
  citable and available.

## 5. Reproducibility

```bash
# regenerate the BMB reference list
python3 scripts/build_bmb_refs.py
# rebuild both papers (tectonic)
cd scripts && tectonic journal_manuscript_v2.tex && tectonic companion_categorical.tex
# full numeric audit (98 checks)
python3 scripts/audit_v2_numbers.py
# package scans (duplication, redundancy, remnants)
python3 scripts/scan_two_paper_package.py
# restructure scripts (for the record; already applied)
python3 scripts/restructure_companion_a.py   # needs pre-round source from git
python3 scripts/restructure_companion_b.py
python3 scripts/retarget_main_bmb.py
```

## 6. Open items

- Submitter-level: author/affiliation details, funding, competing
  interests, suggested reviewers (cover-letter placeholders).
- The 4 remaining overfull hboxes (≤ 4 pt, plus one pre-existing
  invisible table-strut artifact) — cosmetic.
- PRECISE-1K: remains deferred per user instruction (post-review
  decision).
- Companion venue selection (TAC / ACS / preprint) — user decision.
