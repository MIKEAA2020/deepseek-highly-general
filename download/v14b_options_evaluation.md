# Phase 1 Verification Report: Options A & B + Critical Reanalysis of v13

## TL;DR — verification found a problem that changes the question

The audit of the 15 MAPPED metabolic genes from the v13 patched E10 CSV reveals a **critical structural fact** that requires us to re-evaluate both options before implementing either:

> **Of the 15 MAPPED metabolic genes, only 1 (b2097 / fbaA) has any non-zero κ_V across the 8 timepoints T1..T8. The other 14 have κ_V = 0 across all 8 timepoints because their assigned iJO1366 reactions carry ZERO flux under glucose-limited aerobic FBA.**

This means the v13 "Keio b-number fallback" did NOT actually provide per-gene heterogeneous κ_V signals — it provided the **same end-state as the v12 mask** (zeroed κ_V for 14 of 15 mapped genes), but via a different mechanism:

| Mechanism | Why κ_V = 0 for these 14 genes |
|---|---|
| v12 mask | Per-gene max Δb (biomass change on gene KO) = 0, because isozyme cover / anaerobic-only / conditionally-inactive transporters |
| v13 patch | The reaction itself carries 0 flux under glucose-limited aerobic FBA (e.g., THIORDXi, METSOXR1, SPODM, TREHpp, TRE6PP, UGLT, NO3R1pp/NO3R2pp, G3PSabcpp) |

Both arrive at κ_V = 0 for the same 14 genes. The only real difference between v12 and v13 is whether b2097's κ_V is zeroed (v12) or kept (v13: max κ_V = 9.49).

This changes the v13 paragraph narrative **again**: the manuscript currently says (after my v14 correction) that "the v13 patch replaces their zero with per-gene heterogeneous κ_V values drawn from their actual iJO1366 GPR reactions". **This is false.** The v13 patch ATTEMPTS to do this, but the assigned reactions are inactive under this condition, so the result is still zero. The corrected narrative is:

> "The v13 patch assigns the 14 newly-mapped metabolic genes to their actual iJO1366 GPR reactions. However, under glucose-limited aerobic FBA (the Lemuth condition), 14 of these 15 reactions carry ZERO flux (THIORDXi, METSOXR1, SPODM, TREHpp, TRE6PP, UGLT, NO3R1pp/NO3R2pp, G3PSabcpp, etc., are inactive under this condition). The v13 patch therefore arrives at the SAME end-state as the v12 mask: 14 of 15 mapped metabolic genes have κ_V = 0; only b2097 has non-zero κ_V (max = 9.49). The v12 and v13 routes are independent confirmations of the structural finding that 14 of 15 Lemuth-mapped metabolic genes are NOT perturbing biomass under glucose-limited aerobic FBA."

And the "Counterintuitive MAPPED-only finding (n=15, r=-0.158)" is **an artifact of a single outlier**, not a real biological signal:
- 14 genes have identically zero κ_V (after log10 transform: 14 values of -12)
- 1 gene (b2097) has max κ_V = 9.49 (log10 = 0.776) with max |log2 FC| = 0.44
- Mean max |log2 FC| of the 14 zero genes = 0.59
- So b2097 sits high-x / below-average-y → drives a NEGATIVE Pearson r
- This is **n=15 with 14 identical points and 1 outlier** — not a meaningful correlation

---

## Internet-access verification

Tested 6 public databases for both options (Option A needs COLOMBOS/M3D expression data; Option B needs PaxDB protein abundance):

| Database | URL pattern | Status | Usable? |
|---|---|---|---|
| UniProt | rest.uniprot.org | HTTP 200 (full JSON for b2097/dnaK) | ✓ YES |
| PaxDB | pax-db.org/api/... | HTTP 404 (endpoint moved or removed) | ✗ NO |
| Colombos | colombos.net/... | connection timeout (blocked) | ✗ NO |
| String-DB | string-db.org/api/... | HTTP 403 forbidden | ✗ NO |
| KEGG REST | rest.kegg.jp/... | HTTP 404 (URL changed) | ✗ NO |
| EcoCyc | ecocyc.org/... | connection timeout | ✗ NO |

**Implication**: Direct programmatic access to COLOMBOS, M3D, and PaxDB is **NOT AVAILABLE** in this environment. UniProt works but only provides protein sequence / functional annotation, NOT expression or abundance data. This means:

- **Option A (COLOMBOS/M3D)** would require manual download of the compendium (multi-hundred-MB) to the project's `data/` directory by the user, then local parsing. Not impossible, but requires user action.
- **Option B (PaxDB protein abundance)** similarly blocked. Could substitute with iJO1366's own GPR + UniProt's functional annotation, but that gives only gene regulation category, not quantitative protein-abundance weights.

---

## Re-evaluation of Option A (COLOMBOS / M3D metabolic-gene-only)

### What it would actually do, given the critical finding

The user's original framing assumed the v13 patch gives "per-gene heterogeneous κ_V" for 15 mapped genes. **That assumption was wrong** — only 1 of the 15 has non-zero κ_V. The real structural problem is:

> Of iJO1366's 2583 reactions, only **438 (17.0%) carry non-zero flux** under glucose-limited aerobic FBA (the Lemuth condition). The other 2145 reactions are inactive, so any gene mapped only to inactive reactions will have κ_V = 0 regardless of how clever the mapping is.

Adding more metabolic genes from COLOMBOS won't fix this — it just gives us more genes whose reactions are mostly inactive under this specific condition. The fundamental bottleneck is **condition↔reaction coverage**, not gene↔reaction coverage.

### Revised feasibility verdict

| Criterion | Old estimate (user's framing) | Revised estimate |
|---|---|---|
| Data availability | "compendium download" | **Manual download needed** (Colombos timeout) |
| Implementation effort | moderate | moderate (download + ID mapping + parsing) |
| Condition mismatch risk | acknowledged | unchanged (the user's caveat stands) |
| Circularity risk | low (Lemuth separate) | unchanged |
| **Expected impact on per-gene Pearson r** | "potentially hundreds of metabolic genes" | **Likely marginal** — most compendium genes' reactions are also inactive under glucose-limited aerobic FBA; only ~438/2583 reactions are active regardless of gene set |

**Verdict on Option A**: Marginal value without first solving the "inactive reaction" structural problem. The condition mismatch + the inactive-reaction bottleneck means Option A would give us more genes, but most would still have κ_V = 0 (because their reactions don't carry flux under this FBA condition).

---

## Re-evaluation of Option B (explore MAPPED-only n=15, r=−0.158)

### What it would actually do, given the critical finding

The user's original framing assumed r=−0.158 is "a real biological signal suggesting protein-level regulation". **That assumption was also wrong** — with 14/15 genes having identically zero κ_V and only 1 outlier (b2097), the Pearson r is purely a small-sample artifact driven by b2097's high-x/below-average-y position. There is no real biological signal to explore.

### What Option B CAN still do (pivot to the real question)

The actually interesting question is: **why do 14 of the 15 Lemuth-mapped metabolic genes have zero-flux reactions under glucose-limited aerobic FBA?** The v12 manuscript paragraph already enumerates three categories:

| Category | Example genes | Reason for zero flux |
|---|---|---|
| (i) isozyme cover | b2097 → FBA (GPR: "b1773 or b2097 or b2925") | Single-gene KO doesn't disable reaction; other isozymes carry flux |
| (ii) anaerobic-only | b1226 → NO3R1pp/NO3R2pp (nitrate reductase) | Reaction requires nitrate as electron acceptor, absent in aerobic glucose |
| (iii) conditionally-inactive transporters | b3450 → G3PSabcpp (glycerol-3-phosphate transporter) | Not used when glucose is the carbon source |

But wait — for the v13 patch, b2097's κ_V is NON-ZERO (9.49). That's because b2097 → FBA reaction CARRIES flux under glucose aerobic FBA (FBA flux ≈ 7.78 under default conditions). So category (i) is partially wrong: b2097's reaction IS active, but its SINGLE-GENE KO doesn't perturb biomass (because of isozymes). The v12 and v13 routes then diverge:

- v12 mask: zero out b2097's κ_V (because Δb=0 from KO, due to isozymes)
- v13 patch: keep b2097's real κ_V (the actual reaction flux DOES decline over T1..T8 as glucose uptake drops)

So the v13 patch is actually more informative than v12 for the single gene b2097. For the other 14 genes, neither approach gives non-zero κ_V.

### Revised feasibility verdict

| Criterion | Original Option B (post-translational regulation exploration) | Revised Option B (why 14/15 are inactive) |
|---|---|---|
| Feasibility | High (data on hand) | High (data on hand + iJO1366 GPR) |
| Novel biological insight | Maybe (post-translational buffering hypothesis) | **Already covered in v12 manuscript narrative** (lines 7886-7893) |
| Sample size | n=15 (weak) | n=14 inactive + n=1 active (too small for stats) |
| PaxDB availability | assumed available | **NOT available** (404) |
| Expected impact | maybe reveal mechanism | **Minimal new info** — v12 already explains the categories |

**Verdict on Option B**: Largely subsumed by the existing v12 manuscript narrative. The "counterintuitive finding" was an artifact, so there's no biological mystery to chase. The "why inactive" question is already answered in the v12 paragraph.

---

## Critical fix to the v13 paragraph (must-do, regardless of A/B/C/D)

Before pursuing any new option, the v13 paragraph in the manuscript still needs correction. The current text (after v14 commit) wrongly says the v13 patch provides "per-gene heterogeneous κ_V values drawn from their actual iJO1366 GPR reactions". The verified reality is that those reactions are inactive under this condition, so the κ_V is zero (same end-state as v12 mask). I'll fix this in a v14b commit.

## New Option C — Reaction-based sampling (most promising, fully local)

### Concept

Instead of trying to MAP Lemuth genes to reactions (which fails because most mapped reactions are inactive), INVERT the mapping:

1. Compute the iJO1366 FBA flux solution at T1..T8 under the Lemuth glucose-limited aerobic condition (already done — 438 active reactions)
2. For each active reaction, compute κ_V(reaction, t) = (v_r(t) − v_r(T1))^2 — the actual flux-perturbation curvature
3. For each active reaction, look up its GPR rule and identify the catalyzing gene(s)
4. Cross-reference these genes against the Lemuth 92-gene list — see how many Lemuth genes are linked to active reactions
5. Also compute per-gene κ_V for the FULL iJO1366 gene set (not just Lemuth) — gives ~1100+ genes with non-zero κ_V
6. Re-run the per-gene Pearson r on this expanded set

### Why this is the most promising option

- **No external data needed** — entirely uses iJO1366 + cobrapy + the existing FBA solutions
- **Solves the "inactive reaction" bottleneck** — only active reactions are used, so every included gene has non-zero κ_V
- **Massively increases sample size** — from n=92 (Lemuth) to potentially n=1100+ (iJO1366 genes with active reactions)
- **No condition mismatch** — uses the SAME glucose-limited aerobic FBA condition as Lemuth, so the κ_V remains interpretable as "flux-perturbation curvature under the Lemuth condition"
- **No circularity** — Lemuth |log2 FC| remains the response variable; iJO1366-derived κ_V is the predictor (different datasets)

### Caveat / open question

- The Lemuth 92-gene list is dominated by flagellar/chemotaxis genes (not in iJO1366) — so the Lemuth-specific Pearson r may not improve much
- The bigger payoff would be to also use a NEW expression dataset matched to the iJO1366 active gene set. The candidate datasets are: 
  - **EcoGene expression** (local UniProt lookups can give functional category)
  - **RegulonDB** transcription-factor targets (would need download)
  - COLOMBOS (if user can manually download)

### Expected impact

If 100+ of iJO1366's ~1100 active genes overlap with any expression dataset, the per-gene Pearson r could move from +0.0838 (current v13) to a more statistically meaningful estimate (smaller CI, smaller p-value). The sign flip should be preserved (positive direction).

## New Option D — Switch experimental condition (highest biological leverage)

### Concept

Instead of changing the gene set, change the **FBA condition** so the 14 inactive reactions become active:

| Candidate condition | Genes that would activate | Source |
|---|---|---|
| Anaerobic glucose + NO3 (nitrate) | narJ/b1226 (NO3R1pp/NO3R2pp) | Lemuth-style + nitrate |
| Glycerol carbon source | ugpC/b3450 (G3PSabcpp), glpT | Standard iJO1366 swap |
| Oxidative stress (H2O2 pulse) | bcp/b2480 (THIORDXi), sodA/b3908 (SPODM), msrA/b4219 (METSOXR1), yeaA/b1778 (METSOXR2) | iJO1366 + demand reaction |
| High osmolarity (KCl pulse) | proV/proW/proM (ProU transporter), otsB/b1897 (TRE6PP), treA/b1197 (TREHpp) | Standard iJO1366 swap |

### Why this is interesting biologically

- The Lemuth 2008 study actually IS glucose-limited aerobic fed-batch, so it doesn't have these conditions
- BUT: if we ran FBA under anaerobic/glucose, glycerol, oxidative-stress, or osmotic-stress conditions, the 14 currently-inactive reactions would activate, and their κ_V would become non-zero
- We could then test: do those genes' κ_V under THEIR relevant stress condition predict their |log2 FC| under the Lemuth condition? (A cross-condition test of the κ_V → transcript-response hypothesis)
- This is a different claim than the original E10 question, but it's biologically richer: "the framework's predicted flux-perturbation curvature in the relevant stress condition predicts transcriptional response in glucose-limited aerobic"

### Feasibility

- Fully local (iJO1366 + cobrapy + manual medium swaps)
- Each condition swap is ~10 lines of cobrapy code
- Total implementation: ~2 hours
- Sample size: 14 newly-active genes × 8 timepoints = 112 new data points (cross-condition κ_V vs Lemuth |log2 FC|)

### Expected impact

Could turn the 14 zero-κ_V genes into 14 heterogeneous non-zero κ_V values, dramatically enriching the per-gene signal. The per-gene Pearson r on the MAPPED-only subset (n=15) could move from the artifact r=−0.158 to a real r value (positive expected, given the v12/v13 sign flip pattern).

---

## Recommendation

**Strong recommendation**: Implement in this order:

1. **CRITICAL FIX (v14b)**: Correct the v13 paragraph AGAIN to remove the false "per-gene heterogeneous κ_V" claim and the false "counterintuitive finding" claim. This is mandatory regardless of which option we pursue.

2. **Option C first** (reaction-based sampling): no external data needed, fully local, solves the structural "inactive reaction" problem, gives the largest sample size, and preserves the Lemuth |log2 FC| interpretation. **Estimated 1-2 hours**.

3. **Option D second** (multi-condition FBA swap): gives the biologically richest interpretation, but is a different question than the original E10 (cross-condition κ_V vs same-condition transcript response). **Estimated 2 hours**, but worth doing after Option C because it depends on the same reaction→gene mapping.

4. **Option A only if user manually downloads COLOMBOS**: defer until user provides the compendium. Note that even with COLOMBOS, the condition-mismatch caveat remains.

5. **Option B**: largely subsumed by v12 narrative + the critical fix; defer unless user wants a deeper functional-category breakdown using UniProt (which IS accessible).

---

## Phase 1 artifacts produced

- `/home/z/my-project/scripts/v14b_mapped15_audit.py` — audit script
- `/home/z/my-project/download/v14b_mapped15_audit.{csv,txt,json}` — audit outputs
- `/home/z/my-project/download/` (PaxDB/Colombos internet tests — none downloaded, all blocked)
