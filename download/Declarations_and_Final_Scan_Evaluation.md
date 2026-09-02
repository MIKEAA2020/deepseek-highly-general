# Declarations, Journal Target, and Final Sentence-Level Scans — Evaluation

**Date:** 2026-09-02 (final pre-submission round)
**Round directive:** (1) commit + push, English, PAT retained; (2) fill all
submitter declarations (no funding, no competing interests, data
availability, ethics, formal AI declaration for GLM and DeepSeek, sole
author X) and confirm the companion journal (TAC — full name?); (3) deep
sentence-level scan for accidental content loss or condensation and for
earlier-draft material worth incorporating; (4) scan for conceptual
clarity, seamless flow, remnants and redundancy, stylistic writing and
syntax.

---

## 1. Declarations (both papers) — executed

Main paper (`scripts/journal_manuscript_v2.tex`), backmatter:

- **Funding:** no specific grant from any funding agency in the public,
  commercial, or not-for-profit sectors; no funding for research,
  authorship, or publication.
- **Competing Interests:** none.
- **Ethics Approval:** not applicable — fully computational study, no
  human/animal subjects, no new experiments, public data only.
- **Declaration of Generative AI in Scientific Writing:** GLM (Z.ai) and
  DeepSeek used under the author's direction and supervision to assist
  with drafting/editing and analysis-code development; all assisted
  content reviewed, verified, edited by the author, who takes full
  responsibility.
- **Author Contributions:** X is the sole author: conceived the study
  design, developed the methodology and analysis code, performed the
  data analysis, drafted and revised the manuscript, approved the
  submitted version.
- Data/Software/Code Availability section retained (already factual).

Companion paper (`scripts/companion_categorical.tex`): equivalent
Declarations block added (funding, competing interests, ethics,
data/code availability, generative-AI declaration, author
contributions), worded **semantically identically but textually
distinctly** from the main paper so that the package's "no verbatim
passages of length" property remains strictly true (verified by the
7-gram cross-paper scan; see §4).

**Author identity consistency:** `Z.ai` authorship replaced by `X`
everywhere it appears as an author: `\author{}` and `pdfauthor` of both
papers, the companion title block, the bib entries
(`zai2026categorical`, `zai2026measure`), and the generated BMB
reference list (alphabetical position preserved: Wang < X < Ziegler).
Mathematical "we" (author + reader) is retained in both papers, per
standard practice; sole authorship is carried by the declarations and
the cover letters, which are now first-person singular throughout.

**Cover letters:** `download/cover_letter_bmb.md` — plural voice
corrected to singular, author block set to X, declarations block filled
(no funding / no competing interests / ethics not applicable / AI
disclosure), companion target named with the TAC full name.
`download/cover_letter_tac.md` — new companion cover letter for
Theory and Applications of Categories, with the reciprocal related-
manuscript disclosure, reproducibility note, sole-author and AI
declarations.

## 2. Companion journal: TAC full name — answered and verified

**TAC = Theory and Applications of Categories** (ISSN 1201-561X;
www.tac.mta.ca). Scope: "articles that significantly advance the study
of categorical algebra or methods" — the companion's content
(2-categories, optics, filtered colimits, HoTT extension) fits. Fee
status verified by web search (`scripts/search_tac{,2}.json`): TAC is a
free electronic journal (one of the first), no subscription and no
author-side charges (diamond open access) — satisfying the user's
no-fee constraint. Active (Volume 45, 2026). Recorded in
`download/Two_Paper_Submission_Package_Evaluation.md` §1 row 3.

## 3. Sentence-level content-loss scan — executed, clean

New script `scripts/scan_sentence_loss.py` (artifact
`download/deepseek_bridge/sentence_loss_scan.json`): every sentence
(≥6 words) of each earlier draft — frozen v21 (2,105 fragments),
v2@e6a0c61 (239), v2@5219ef0 (249), companion@e6a0c61 (429) — is
5-gram-traced into the current two-paper union; plus environment-level
coverage and a pre-vs-post-restructure delta.

| Source | frags | survived | reworded (light/heavy) | dropped |
|---|---|---|---|---|
| v21 (frozen legacy) | 2,105 | 16% (by design: split, see below) | 51/236 | 1,482 (all dispositioned, see below) |
| v2@e6a0c61 | 239 | 90.4% | 19/2 | 2 |
| v2@5219ef0 (PLOS) | 249 | 92.0% | 9/1 | 10 |
| companion@e6a0c61 | 429 | 77.9% | 46/20 | 29 |

**Zero accidental loss, zero unexplained condensation:**

- v2@5219ef0 → current: the 10 dropped sentences are the PLOS Author
  Summary (6; BMB does not use author summaries and the abstract
  carries the same numbers), the frozen-v21 audit-baseline sentence
  and the Layer-1 porting-map appendix (both v21-bookkeeping,
  intentionally removed in the BMB retarget; the provenance note is
  kept), and the two placeholder funding/competing-interest blocks
  (replaced this round by the real declarations above).
- companion@e6a0c61 → current: the 29 dropped sentences decompose as
  17 bookkeeping sentences (the deleted "role of this document" /
  v21-inventory / extraction-record sections), 8 sentences of the
  deliberately removed indicator-weighted FBA κ_V definition (the
  definition-shopping object; its supersession is documented in
  Remark rem:fba-kappa-superseded), and 4 pointer-conversion rewrites
  ("Conjecture v21 21.6" meta-references). The 20 heavily-reworded
  sentences are the documented theorem repairs (two-crossing
  small-loop formula, standard-gauge matching, instantiation-scoped
  Banach) and v21→internal-label conversions.
- Environment-level: exactly **2** v21 environments were present
  pre-restructure and absent now — the FBA κ_V definition (deliberate,
  documented) and the AcCoA limit-cycle remark (false positive: it
  exists, retitled "...in the Network~G benchmark"). The other 117
  "missing" v21 environments were already frozen-only at e6a0c61, i.e.
  the previously documented disposition set (superseded by κ^μ / frozen
  with artifacts / iteration bookkeeping), re-confirmed.
- **Worth incorporating?** Nothing qualifies: the Author Summary is
  duplicated by the abstract; the port map is provenance bookkeeping;
  the frozen-only set is dispositioned with reasons (ARD/κ_geo theory
  superseded by the measure-theoretic line; autopoiesis network battery
  A–K summarized in the companion with artifacts in the repo; Claims
  F/G verdicts and Lévy-3/2 closed theorem frozen with committed
  scripts and referenced via the repository; Zeno/CPTP/Holevo content
  present in adapted form; POMDP terminology absent from the companion
  so the v21 remark is not needed; adding v21-era "(CLOSED)" meta-
  bookkeeping would reverse the standalone rewrite's deliberate
  style).

## 4. Editorial scan (clarity, flow, remnants, redundancy, syntax) — 7 fixes

Main paper: **stale audit-count claims repaired** — Methods §Statistical
protocols and §Reproducibility said "73 checks"; the numeric audit is
98 checks and 13 repaired defects (D-N1–N8 + D-JS1–5). Both updated
("$98$ checks; $13$ repaired defects across audit generations, D-N1--N8
and D-JS1--5"). No other clarity/flow/syntax defects found in a full
sentence-level read; the mathematical "we" is consistent; R/D/E
protocol, transitions, and cross-references are clean.

Companion paper (full sentence-level read):

1. **Flow remnant (real defect):** Remark rem:2cat-span said the
   2-categorical development "is left for future work" — while the very
   next subsection opens "We now close the 2-categorical gluing agenda
   sketched in Remark rem:2cat-span." Corrected to point forward to
   §sec:2cat-gluing (gluing + coherence) and §sec:hott
   (homotopy-theoretic well-definedness).
2. **v21-style ALL-CAPS emphasis remnants (9 occurrences):** THIRD,
   CENTRAL, ALL THREE, GEOMETRY-INDEPENDENT (×2), TRIANGULAR,
   NON-PERPENDICULAR, ASYMMETRIC, FIVE → \emph{} (italic emphasis),
   consistent with the paper's typography.
3. **Redundancy:** rem:typed-optic repeated the realization-construction
   explanation already stated in thm:composition; tightened to a
   reference.
4. **Logic-of-prose defect:** prop:invlim attached its κ-agreement
   consistency check with "Equivalently," (it is not an equivalent of
   the viability inequality) → "As a consistency check," — matching the
   0=0 honesty remark rem:zero-zero.
5. **Syntax error:** "...canonically a term in $\mathcal{U}$. the
   endpoint-only closure-test verdict..." (period + lowercase
   mid-sentence) → "$\mathcal{U}$; the endpoint-only...".

Cross-paper duplication after this round: 44 shared 7-grams, **zero
prose runs ≥7 words** (the single flagged run is the known
theorem-environment-name preamble artifact); the declarations were
reworded in the companion to keep this strictly true. Remnant scan: 2
flags, both false positives ("supersede"/"supervision" matching the
substring "super"; "predecessor manuscript" occurring only in a source
comment). Overfull boxes: main 4 (all ≤4pt plus the known counts-ledger
table strut), companion 0 — unchanged from the pre-round state.

## 5. Builds and audits

- `tectonic journal_manuscript_v2.tex`: 22 pages, clean, 0 undefined
  references, 0 multiply-defined labels (PDF:
  `download/journal_manuscript_v2.pdf`).
- `tectonic companion_categorical.tex`: 35 pages, clean, 0 undefined
  references (PDF: `download/companion_categorical.pdf`).
- `scripts/audit_v2_numbers.py`: **98 PASS / 0 FAIL of 98 checks**
  (cobra 0.32.1 reinstalled into the venv after session restart; all
  manuscript numbers re-derived from committed artifacts, including
  after this round's edits).
- `scripts/scan_two_paper_package.py`: duplication/remnant/overfull
  results as in §4.

## 6. Open (submitter-level) items

- Fill [Affiliation] / [Email] in both cover letters; suggested
  reviewers optional.
- If the real name is to replace the placeholder "X", it must be
  changed consistently in: both papers' author fields, both bib
  entries, the BMB generated reference list, and both cover letters
  (all sites are listed in §1).
- PRECISE-1K remains deferred (post-submission decision).
