#!/usr/bin/env python3
"""
v21 patch: P0-mechanical + P1-typesetting corrections from the 2nd-wave
joint assessment (download/joint_assessment_2nd_wave.pdf), executed per
the user's directive: mechanical subset NOW, P0-editorial (citation
annotations / uncited refs) and P2-P5 HELD pending the
in-place-vs-deconstruction decision.

Every replacement below was verified against the v20 source, the
deposited result JSONs/CSVs, the BiGG model files, IUBMB nomenclature,
or a fresh cobrapy re-run (verify_e12_e16_biomass_units.py) BEFORE
being applied. Asserts guarantee exact-match application.
"""
import io, sys

PATH = "scripts/journal_manuscript.tex"

def R(old, new, count=1, tag=""):
    return (old, new, count, tag)

REPLACEMENTS = [
# ---------------- P0-mechanical ----------------
R("\\cite{orth2011comprehensive}. The indicator",
  "\\cite{orth2011}. The indicator", 1, "P0-1 broken cite key -> [?]"),

R("sign from $-0.008$ to $+0.466$ (the denser network's flux-rerouting",
  "sign from $-0.018$ to $+0.466$ (the denser network's flux-rerouting",
  1, "P0-2a -0.008 -> -0.018 (E16 JSON: -0.0178)"),

R("   & $+0.085$ & $+0.351$ & $-0.008$ & $+0.466$ \\\\",
  "   & $+0.085$ & $+0.351$ & $-0.018$ & $+0.466$ \\\\",
  1, "P0-2b table cell -0.008 -> -0.018"),

R("The iML1515 Pearson $r$ \\emph{flips sign} from $-0.008$ to $+0.466$:",
  "The iML1515 Pearson $r$ \\emph{flips sign} from $-0.018$ to $+0.466$:",
  1, "P0-2c -0.008 -> -0.018"),

R("$|\\Delta r_{\\text{Pearson}}| \\, 0.093 \\to 0.115$ (worse, but both",
  "$|\\Delta r_{\\text{Pearson}}| \\, 0.103 \\to 0.115$ (worse, but both",
  1, "P0-2d gap 0.093 -> 0.103 (0.0847+0.0178)"),

R("correlation flips sign and rises by a factor of $\\sim 56$.",
  "correlation flips sign and rises by a factor of $\\sim 26$.",
  1, "P0-2e DEPENDENT claim (audits missed): 0.466/0.0178=26.2, not 56"),

R("GLYP1/GLYP2 phosphorylase EC 2.7.4.1): M13 stores G6P as glycogen",
  "GLYP1/GLYP2 phosphorylase EC 2.4.1.1): M13 stores G6P as glycogen",
  1, "P0-3a glycogen phosphorylase EC (iJO1366 GLCP2 = 2.4.1.1); "
    "PolyP PPK EC 2.7.4.1 and transaminase EC 2.6.1.12 verified "
    "correct vs IUBMB and retained"),

R("$n=4$ non-abelian regime (structure group $\\CO(3)$, Lie algebra",
  "$n=4$ non-abelian regime (structure group $SO(3)$, Lie algebra",
  1, "P0-4 Fig.7 caption CO(3) -> SO(3) (sec:n4 defines G_C=SO(3); "
    "figure panel titles say so(3))"),

R("""corrected (see the manuscript's \\S 7 research-integrity notes for
specific corrections applied to the bibliography in the v6 revision).""",
  """corrected directly in the bibliography in the v6 revision (the
corrected entries themselves are the record of those corrections).""",
  1, "P0-5a dangling '\\S 7 research-integrity notes' (Section 7 is the "
    "Composition Theorem; no such notes exist)"),

R("\\S1.4 form",
  "Proposition~\\ref{prop:kappa-derivation} form", 2,
  "P0-5b dangling '\\S1.4' x2 -> the operational form the invlim "
  "section itself cites"),

R("""\\textbf{Applicability matrix (E1--E14).} Of the 14 earlier studies,
only \\textbf{3 compute $\\kappa_V$ from FBA gene-KO biomass}:
E10 (iJO1366 time-series), E12 (iJO1366 Keio validation),
E15 (iJO1366 direct raw-Keio) and E16 (iML1515 direct raw-Keio).
The remaining \\textbf{10 studies are N/A} because their $\\kappa_V$ is
\\emph{not} biomass-based:""",
  """\\textbf{Applicability matrix (E1--E16).} Of the 16 earlier studies,
only \\textbf{4 compute $\\kappa_V$ from FBA gene-KO biomass}:
E10 (iJO1366 time-series), E12 (iJO1366 Keio validation),
E15 (iJO1366 direct raw-Keio) and E16 (iML1515 direct raw-Keio).
The remaining \\textbf{12 studies are N/A} because their $\\kappa_V$ is
\\emph{not} biomass-based:""",
  1, "P0-6a 'only 3' -> 4 (four listed); coherent arithmetic: "
    "16 studies = 4 + 12 (the itemized N/A list has 12)"),

R("""\\textbf{Net v10 tally on E1--E14}: of the $14$ earlier studies,
$2$ are STRENGTHENED (E12, E15$+$E16), $1$ is MIXED (E10), $0$ are
UNCHANGED or REGRESSED, and $11$ are N/A (no FBA biomass $\\Delta b$:
E1, E2, E3, E4, E5, E6, E7, E8, E9, E11, E13, E14 -- counting E6/E7
as folded-into-E2/E5 verdicts gives $11$ distinct N/A slots, or $13$
if counted separately). Deliverables:""",
  """\\textbf{Net v10 tally on E1--E16}: of the $14$ evaluation slots
($16$ studies; E6/E7 folded, E15$+$E16 paired), $2$ are
STRENGTHENED (E12, E15$+$E16), $1$ is MIXED (E10), $0$ are
UNCHANGED or REGRESSED, and $11$ are N/A (no FBA biomass $\\Delta b$:
E1, E2, E3, E4, E5, E6, E7, E8, E9, E11, E13, E14 -- counting E6/E7
as folded-into-E2/E5 verdicts gives $11$ distinct N/A slots, or $12$
if counted separately). Deliverables:""",
  1, "P0-6b tally re-labeled (slots vs studies made explicit); "
    "'13 if counted separately' -> 12"),

R("""\\item Wild-type biomass flux $b_{\\mathrm{wt}} = 15.444$~h$^{-1}$
  (FBA on glucose minimal medium, $10$~mmol/gDW/h glucose $+$
  $20$~mmol/gDW/h O$_2$ uptake, with minerals).""",
  """\\item Wild-type biomass flux $b_{\\mathrm{wt}} = 15.444$ (FBA objective
  value; the medium was \\emph{intended} as glucose minimal ---
  $10$~mmol/gDW/h glucose $+$ $20$~mmol/gDW/h O$_2$ uptake, with
  minerals --- but the v21 medium-audit note below shows this value is
  a trehalose artifact, not a glucose-minimal growth rate).""",
  1, "P0-7a E12 b_wt: re-labeled honestly (artifact, not h^-1)"),

R("""  $5\\%$-threshold used by Orth et al. 2011).
\\end{itemize}

Results:""",
  """  $5\\%$-threshold used by Orth et al. 2011).
\\end{itemize}

\\noindent\\emph{v21 medium-audit note (the $15.444$ vs $0.9259$
question).} Re-verification with the deposited model files
(\\texttt{scripts/verify\\_e12\\_e16\\_biomass\\_units.py};
\\texttt{download/verify\\_e12\\_e16\\_biomass\\_units.json}) shows
that the E12 wild-type objective value $15.444$ is an artifact of the
medium construction, not of the biomass stoichiometry and not a unit
conversion: the E12 script's ``minerals'' re-open list includes the
trehalose exchange \\texttt{EX\\_tre\\_e} at $-1000$~mmol/gDW/h, and
the optimizer grows on unlimited trehalose (uptake
$-337$~mmol/gDW/h at the optimum; closing \\texttt{EX\\_tre\\_e}
alone gives $0.982$~h$^{-1}$, the canonical iJO1366 glucose-minimal
optimum of Orth et al. 2011). The nominally identical E16 protocol
for iML1515 re-opens the same exchange at only
$-10$~mmol/gDW/h (effective uptake $-6.4$), giving
$0.9259$~h$^{-1}$ against a glucose-only optimum of
$0.822$~h$^{-1}$. The two wild-type values are therefore neither
mutually comparable growth rates nor a stoichiometry effect, and both
were mislabeled ``glucose minimal'' in earlier versions of this
remark and of Remark~\\ref{rem:e16-iml1515-cross-rebuild}.
Essentiality calls use the relative $5\\%$-of-WT threshold
\\emph{within} each model, which is invariant to the absolute scale
of $b_{\\mathrm{wt}}$; however, the identity of the available carbon
sources does enter every KO solution, so the E12/E15/E16
essentiality sets, $\\kappa_V$ values, and calibration statistics
inherit the medium asymmetry. A corrected glucose-only re-run of
E12/E15 (and the E16 comparison on the same corrected medium) is
scheduled as a methodological repair (joint-assessment plan, item
P4); the deposited E12/E15/E16 results are reported unaltered and
flagged here rather than silently recomputed.

Results:""",
  1, "P0-7b E12 medium-audit note inserted (verified numbers)"),

R("""Wild-type FBA biomass $= 0.9259$ h$^{-1}$ (iML1515 uses different
biomass stoichiometry than iJO1366's $15.444$ h$^{-1}$, but both are
on the same glucose+O$_2$ minimal medium and the essentiality
threshold is taken relative to WT, so cross-model comparison is valid).""",
  """Wild-type FBA biomass $= 0.9259$ h$^{-1}$ (v21 medium-audit
correction: this is \\emph{not} the same medium as E12's, and the
difference from E12's $15.444$ is not a biomass-stoichiometry effect
--- the two scripts re-open the accidentally included trehalose
exchange \\texttt{EX\\_tre\\_e} at $-10$ vs $-1000$~mmol/gDW/h
respectively; the glucose+O$_2$-only optima are $0.822$~h$^{-1}$ for
iML1515 and $0.982$~h$^{-1}$ for iJO1366, see the E12 medium-audit
note and \\texttt{verify\\_e12\\_e16\\_biomass\\_units.py}; the
essentiality threshold is taken relative to WT within each model, so
the cross-model essentiality comparison is unaffected by the absolute
values).""",
  1, "P0-7c E16 site: false 'same medium / stoichiometry' claims "
    "replaced with the verified mechanism"),

R("$9/10$ cases ($90\\%$); metabolites with $n_{\\mathrm{prod}} \\leq 3$ are",
  "$10/11$ cases ($91\\%$); metabolites with $n_{\\mathrm{prod}} \\leq 3$ are",
  1, "P0-8 nprod>=5 stratum: CSV ground truth 10/11 (only rib__D_c, "
    "nprod=7, fails)"),

R("under carbon starvation, $r = +0.187$, $n = 241$), an association",
  "under carbon starvation, $r = +0.191$, $n = 241$), an association",
  1, "P0-9a abstract: +0.187(n=241) conflated -> primary +0.191(n=241)"),

R("(GSE64021, $r = +0.187$, $n = 241$, starvation-depth",
  "(GSE64021, $r = +0.191$, $n = 241$, starvation-depth",
  1, "P0-9b intro"),

R("""the RNA-seq platform under carbon depletion ($r = +0.187$ at
$n = 241$, $p = 2.9 \\times 10^{-3}$) with both a platform and a""",
  """the RNA-seq platform under carbon depletion ($r = +0.191$ at
$n = 241$, $p = 2.9 \\times 10^{-3}$) with both a platform and a""",
  1, "P0-9c E24 remark (p=2.9e-3 matches the primary +0.1913)"),

R("""GSE64021 RNA-seq
$r = +0.187$ at $n = 241$), with the association scaling with""",
  """GSE64021 RNA-seq
$r = +0.191$ at $n = 241$), with the association scaling with""",
  1, "P0-9d conclusion"),

R("""$p = 0.003$; CI $[0.069, 0.315]$). The per-time course deepens with""",
  """$p = 0.003$; CI $[0.069, 0.315]$). (The $+0.187$ that also appears
in the round-level summaries of this study is the \\emph{same}
association recomputed on the $240$-gene set common to both platforms
--- the ``common-set matrix'' below --- and is quoted there at its
own $n = 240$; the two values differ only through the gene-set
restriction, not through any re-analysis. The v21 round reconciles
the four summary-level citations that had paired $+0.187$ with
$n = 241$ to the primary full-panel value.) The per-time course deepens with""",
  1, "P0-9e v18 subsection: explicit reconciliation note"),

# ---------------- P1 typesetting ----------------
R("""\\begin{enumerate}[leftmargin=*,itemsep=2pt]
\\item[\\emph{(i)} \\emph{Knockout.}] Set the internal repair flux of""",
  """\\begin{enumerate}[label=\\textit{(\\roman*)},leftmargin=*,itemsep=2pt]
\\item \\emph{Knockout.} Set the internal repair flux of""",
  1, "P1-10a Def 3.18: step tags as proper labels (was clipped off-page)"),

R("\\item[\\emph{(ii)} \\emph{Drift under dynamics.}] Integrate the",
  "\\item \\emph{Drift under dynamics.} Integrate the", 1, "P1-10b"),

R("\\item[\\emph{(iii)} \\emph{Recovery above threshold.}] Record the",
  "\\item \\emph{Recovery above threshold.} Record the", 1, "P1-10c"),

R("\\item[\\emph{(iv)} \\emph{Downstream cascade.}] Every $m_{j'}$ whose",
  "\\item \\emph{Downstream cascade.} Every $m_{j'}$ whose", 1, "P1-10d"),

R("\\item[\\emph{(v)} \\emph{Restoration control.}] Restore the repair",
  "\\item \\emph{Restoration control.} Restore the repair", 1, "P1-10e"),

R("""\\begin{table}[h]
\\centering
\\begin{tabular}{lllll}""",
  """\\begin{table}[h]
\\centering
\\small
\\begin{tabularx}{\\columnwidth}{@{}lll>{\\raggedright\\arraybackslash}X>{\\raggedright\\arraybackslash}X@{}}""",
  1, "P1-11a Table 6: width-constrained tabularx (last column ran off "
    "the page edge, cutting 'growt' x3 and 'regulat')"),

R("""\\end{tabular}
\\caption{The $12$ persistent model-gap candidates""",
  """\\end{tabularx}
\\caption{The $12$ persistent model-gap candidates""",
  1, "P1-11b Table 6 environment close"),

# ---------------- v21 round record ----------------
R("""\\section{Main Proposition}\\label{sec:mainprop}""",
  """\\subsection{v21 mechanical-integrity round: second-wave audit
corrections (P0/P1)}\\label{sec:novelty-v21}

The second wave of external audits (three line-level reviews of the
v20 manuscript; joint assessment in
\\texttt{download/joint\\_assessment\\_2nd\\_wave.pdf}) produced a
prioritized repair plan whose tiers were separated by risk. This
round implements the \\textbf{P0-mechanical} tier (unambiguous
correctness defects whose corrections remain valid under any later
structural decision) and the \\textbf{P1-typesetting} tier (rendering
defects), and deliberately \\emph{defers} the P0-editorial tier (six
false ``Cited in~\\S X'' annotations; twelve uncited bibliography
entries) together with the P2--P5 tiers until the strategic
in-place-vs-deconstruction decision is made, so that no
citation-annotation or bibliography work is later undone by a
three-way split. Every claim was re-verified against the deposited
source, scripts, and result files before implementation; where the
audits' framing did not survive verification, the verified mechanism
was implemented instead (items 2, 7, and 9 below).

\\textbf{Corrections applied.}
\\begin{enumerate}\\itemsep0pt
\\item Broken citation key \\texttt{orth2011comprehensive} (rendered
``{[?]}'' in v20) corrected to the deposited key \\texttt{orth2011}.
\\item Stale E16 numbers: iML1515 original Pearson $r$ corrected from
$-0.008$ to $-0.018$ at three sites (deposited E16 result:
$-0.0178$); the cross-rebuild Pearson gap $0.093$ corrected to
$0.103$; and the dependent headline ``rises by a factor of
$\\sim 56$'' corrected to $\\sim 26$ --- a dependent-claim defect the
audits had not flagged ($0.466/0.0178 = 26.2$, the same
magnitude-ratio convention as E12's ``factor $2.54$'').
\\item Glycogen phosphorylase EC corrected from $2.7.4.1$ to
$2.4.1.1$ (the iJO1366 \\texttt{GLCP2} annotation). The co-occurring
polyphosphate kinase EC $2.7.4.1$ was verified correct against IUBMB
(ATP-polyphosphate phosphotransferase) and retained; the
aspartate--pyruvate transaminase EC $2.6.1.12$ (alanine--oxo-acid
transaminase, IUBMB) was verified correct and retained.
\\item Figure~7 caption: structure group $\\CO(3)$ corrected to
$SO(3)$ --- Section~\\ref{sec:n4} defines $G_C = SO(3)$ for the $n=4$
regime, the figure's numerics are pure $SO(3)$ rotations, and the
$CO(3)$ conformal group is the \\emph{different} third verification
regime of the Remark in Section~\\ref{sec:savgs}.
\\item Dangling pointers: the Authorship statement's ``\\S 7
research-integrity notes'' (Section~\\ref{sec:composition} is the
composition theorem; no such notes exist anywhere in the manuscript)
was withdrawn and reworded truthfully; the two ``operational \\S1.4
form'' references (the Introduction has no subsections) now point to
the operational Proposition~\\ref{prop:kappa-derivation} form that the
inverse-limit section itself cites.
\\item Applicability matrix arithmetic: ``only $3$ compute $\\kappa_V$
from FBA gene-KO biomass'' corrected to $4$ (E10, E12, E15, E16);
``the remaining $10$'' corrected to $12$ (the itemized list contains
twelve studies); the matrix and tally headers extended from E1--E14
to E1--E16; the tally re-labeled as $14$ \\emph{evaluation slots}
($16$ studies; E6/E7 folded, E15$+$E16 paired); and ``$13$ if
counted separately'' corrected to $12$.
\\item The $n_{\\mathrm{prod}} \\geq 5$ closure-test stratum corrected
from $9/10$ ($90\\%$) to $10/11$ ($91\\%$): the deposited
\\texttt{autopoiesis\\_ijO1366.csv} contains $11$ metabolites with
five or more producing reactions, of which $10$ are causally internal
(the single failure, ribose-D, has $n_{\\mathrm{prod}} = 7$); the
totals $28/50$ and $18/39$ are unaffected.
\\item E25 reconciliation: the primary RNA-seq carbon-depletion
replication is the full-panel max-metric $r = +0.191$ at $n = 241$
($p = 2.9 \\times 10^{-3}$), while $+0.187$ is the same association
on the $240$-gene set common to both platforms; four summary-level
citations (abstract, introduction, E24 remark, conclusion) had paired
$+0.187$ with $n = 241$ and are corrected to the primary value, with
an explicit reconciliation note added in
Section~\\ref{sec:novelty-v18}.
\\item Biomass $15.444$ vs $0.9259$: the audits framed this as a
units issue; re-running the deposited models
(\\texttt{verify\\_e12\\_e16\\_biomass\\_units.py}) shows it is a
\\emph{medium-construction artifact} --- both scripts list the
trehalose exchange \\texttt{EX\\_tre\\_e} among the ``minerals'',
re-opened at $-1000$ (E12, unlimited-trehalose growth, uptake
$-337$) vs $-10$ (E16, uptake $-6.4$) --- with glucose-only optima
$0.982$ (iJO1366) and $0.822$ (iML1515). Honest medium-audit notes
were added at the E12 and E16 sites; the essentiality comparisons
(relative thresholds) are unaffected, and the full corrected-medium
re-run is scheduled as the P4 methodological repair.
\\item P1, Definition~\\ref{def:autopoiesis}: the five step labels
were physically clipped off the left page edge in the v20 render
(label spans began at $x < 0$; ``Drift/Recovery/Downstream/
Restoration'' absent from the text layer). The enumerate was
restructured so the step tags $(i)$--$(v)$ are proper labels and the
step titles begin the item bodies; all step cross-references remain
valid.
\\item P1, Table~\\ref{tab:gem-limitations}: the natural-width
five-column tabular overflowed the page edge (last column ending at
$x \\approx 597$ on a $595$-pt page), cutting ``growth rate'' to
``growt'' (three cells) and ``(regulatory)'' to ``(regulat''. The
table is now a width-constrained \\texttt{tabularx} with wrapped
\\texttt{X} columns; no cell text was changed.
\\end{enumerate}

\\textbf{Honest scope note.} This round changes no analysis, no
deposited result, and no verdict; it corrects transcription,
labeling, counting, and rendering defects, adds two verified
provenance notes, and documents one newly discovered methodological
caveat (the trehalose medium asymmetry) without recomputing the
affected studies. The P0-editorial and P2--P5 tiers remain open and
are sequenced after the strategic decision, per the joint
assessment's plan. Verification artifacts:
\\texttt{scripts/verify\\_e12\\_e16\\_biomass\\_units.py} (cobrapy
re-run of both wild-type media),
\\texttt{download/verify\\_e12\\_e16\\_biomass\\_units.json},
\\texttt{scripts/v21\\_patch\\_mechanical.py} (this patch, with
asserted exact-match replacements), and the joint assessment PDF.

\\section{Main Proposition}\\label{sec:mainprop}""",
  1, "P0-12 v21 round record subsection"),
]

def main():
    with io.open(PATH, encoding="utf-8") as f:
        src = f.read()
    n_ok = 0
    failures = []
    for old, new, expect, tag in REPLACEMENTS:
        c = src.count(old)
        if c != expect:
            failures.append((tag, c, expect))
            print(f"FAIL  [{tag}]  found {c}, expected {expect}")
            continue
        src = src.replace(old, new)
        n_ok += 1
        print(f"OK    [{tag}]")
    if failures:
        print(f"\n{len(failures)} replacement(s) FAILED -- file NOT written")
        sys.exit(1)
    with io.open(PATH, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"\nAll {n_ok}/{len(REPLACEMENTS)} replacements applied; file written.")

if __name__ == "__main__":
    main()
