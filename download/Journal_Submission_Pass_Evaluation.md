# Journal-Submission Pass — Evaluation Report

Round: 2026-09-02 (user items: 1 tie-break robustness table; 2 full
journal formatting; 3 PRECISE-1K deferred; 4 final overstatement pass;
recommended next step: execute the journal-submission pass now).

## Premise verdicts

| # | Reviewer premise | Verdict | Evidence |
|---|------------------|---------|----------|
| 1 | "I do not see [the tie-break robustness table] in this round's summary… the last methodological gap" | **FALSE — already done** | The formal E-V8 table has been in the manuscript since the v2-finalization round (commit `828c89a`, section [E-V8] "Tie-break robustness"): 5 selection rules TB0–TB4 with n / r / partial r / ρ_S / genes-changed per rule (TB0 +0.3954; TB1 +0.3861; TB2 +0.3954; TB3 +0.3959; TB4 +0.3954; ρ_S ≥ 0.99897), plus a dedicated figure. This round's summary led with E32 + the content-loss scan, which is why the reviewer missed it. Audit check JP-1 now guards its presence (PASS). |
| 2 | v2 may lack final journal-style formatting (references, captions, abstract, cover letter) | **TRUE (in part)** | Captions, figures, and a 289-word abstract were already journal-grade; the genuine gaps were: references not in a target-journal style (plainnat author-year), no Author Summary, no keywords line, no backmatter (availability/funding/competing interests), ToC still present, no cover letter. All executed this round. |
| 3 | PRECISE-1K not needed for the current submission | **ACCEPTED — no action** | Remains a post-submission/background item, as already recorded in the Discussion's open items. |
| 4 | "One final pass over Results and Discussion… all numbers trace exactly; 'matches to X%' accurately stated" | **TRUE — 5 defects found and fixed** | D-JS1–D-JS5 below; final audit 98/98 PASS with a dedicated phrase audit. |

## Target journal

**PLOS Computational Biology** (Research Article). Rationale: methods +
biological insight, FBA as core community methodology, long LaTeX
manuscripts and supplementary information well supported, public-data
policy matched by the repo's full reproducibility bundle. Alternatives
that fit (Bioinformatics, npj Systems Biology and Applications) require
only mechanical re-formatting: the reference generator
(`scripts/build_plos_refs.py`) is venue-parameterizable and the
cover letter is modular. **The choice is a default, not a commitment —
say the word to retarget.**

## What was executed

1. **References in PLOS style** (`scripts/build_plos_refs.py` →
   `scripts/journal_manuscript_v2_plos_refs.tex`, auto-generated):
   26 numbered references in order of first citation; PLOS entry
   layout (Author AB, Author CD (Year) Title. Journal Vol: Pages);
   surname+initials; 6-author et al. rule; natbib optional labels for
   the two textually-cited keys (Kochanowski et al. 2013, Schmidt et
   al. 2016); species italics converted to `\emph{}`. Superscript
   numeric citations in text (`natbib [super,sort&compress]`, the PLOS
   citation form). Journal names kept as stored (full names; PLOS
   copyediting abbreviates at proof — documented, not silently
   altered).
2. **Front matter**: keywords line (8 terms); Author Summary (158
   words, non-technical, PLOS Comp Bio requirement); abstract verified
   at 289 words (≤ 300 limit); table of contents removed (journal
   articles do not carry ToCs).
3. **Captions/labels**: `caption` package with period label separator;
   "Fig 1." caption labels; in-text citations of figures abbreviated
   to "Fig ~\ref" (6 occurrences).
4. **Backmatter**: "Data, Software, and Code Availability" (public
   repo, SHA-256 manifest, public sources, no new experiments);
   "Funding" and "Competing Interests" as clearly-marked submitter
   placeholders (facts about the authors are not invented by the
   tooling).
5. **Cover letter** (`download/cover_letter_plos_compbio.md`): PLOS
   Comp Bio, Research Article, three-point significance case using
   only manuscript-traced numbers, standard declarations, placeholders
   for the corresponding author and optional suggested reviewers.
6. **Final accuracy pass** (item 4): extended the numeric audit by 25
   checks (E32-1..17, E22R-1..2, JP-1..6) → **98/98 PASS**
   (`download/deepseek_bridge/v2_number_audit.{json,md}`); plus a
   phrase audit of every "exactly / identical / to the digit /
   matches" occurrence in Results and Discussion — each is now either
   a mathematical identity, a machine-verified claim, or quantified.

## Defects found and fixed this round (final accuracy pass)

- **D-JS1**: C1 effective GC constant stated "≈ 1.9–2.1"; recomputed
  from the e32 json the range is **1.649–2.113** (the m = 128 point
  dips). Fixed in section text and figure caption, with the dip named.
- **D-JS2**: sweep arm claimed the tail is "**exactly** the
  finite-population correction"; measured null-relative ratio at
  k = 12 is 0.49 against the pure FPC value 0.29. Repaired to
  "consistent with", with the measured ratio curve stated honestly
  (≈1.8× small panels → ≈1.5× at k = 6 → ≈0.5× at k = 12) and the
  residual attributed to sweep heterogeneity.
- **D-JS3**: "mid-range deviations up to 8%" — the maximum is 8.2%
  (m = 128). Fixed to "as large as 8.2%".
- **D-JS4**: the restored E22 distinctness check omitted the specific
  identifier (b2097) present in the frozen v21 source. Restored.
- **D-JS5**: the C2 trajectory claims "shape distance 0 / total-mass
  error 0" and "mass error … 0 from m = 43" were float-level
  imprecise: anchor bl ≤ 6.6×10⁻¹³, mass error ≤ 1.7×10⁻¹², and the
  uniform-thinning mass error at m = 43 is 2.6×10⁻¹² (exactly 0 only
  at the full panel m = 57). All three phrases now carry their
  machine-zero bounds explicitly.

## Compliance summary

| Item | Value | Limit / requirement |
|------|-------|---------------------|
| Pages | 21 (tectonic, 0 undefined refs, 0 warnings) | — |
| Abstract | 289 words | ≤ 300 (PLOS) |
| Author Summary | 158 words | ≤ 200 (PLOS Comp Bio) |
| Keywords | 8 | 3–10 |
| Figures | 6, all captioned, artifact-traced | — |
| Formal tables | 1 (E-V8 tie-break robustness) + appendix tabularx displays | — |
| References | 26, PLOS layout, citation order, 26/26 cited keys resolve | — |
| Citations | superscript numerals, compressed ranges | PLOS style |
| Backmatter | availability / funding / competing interests | present |
| Numeric audit | 98/98 PASS | 0 fail |
| Cover letter | download/cover_letter_plos_compbio.md | present |

## Open items for the human submitter

1. Author names, affiliations, corresponding email (currently "Z.ai" /
   placeholders — not invented by tooling).
2. Funding and competing-interest declarations (backmatter
   placeholders).
3. Optional suggested reviewers in the cover letter.
4. At upload time: split Appendices A–C into PLOS Supporting
   Information files (mechanical; offered as a next step).
5. Consider citing the published version of Sastry et al. 2019
   (PRECISE 1.0) instead of the bioRxiv preprint currently in the
   committed bib (kept faithful to the committed artifact; a
   submitter-level reference upgrade).
6. Confirm the target journal (default PLOS Comp Bio; retargeting is
   mechanical).

## Reproducibility

```
python3 scripts/build_plos_refs.py        # regenerates the PLOS reference list
python3 scripts/audit_v2_numbers.py       # 98 checks, 98 PASS (needs cobra; installed this round)
tectonic scripts/journal_manuscript_v2.tex  # 21 pages, 0 undefined refs
```

PRECISE-1K monitoring remains deferred until after submission
(item 3, accepted).
