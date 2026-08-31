#!/usr/bin/env python3
"""
v17 manuscript patcher.

Part 1 (user-directed v16 text review, pre-finalization):
  P1  v15 forward pointer: Option A is no longer deferred (v17 executes it).
  P2  E10 remark: state the v16 non-significance plainly (permutation
      p = 0.18) and forward-point to the v17 power resolution.
  P3  v16 endogeneity paragraph: make the burden-exclusion CIRCULARITY
      explicit (reviewer-proofing).
  P4  v16 primary-result paragraph: "supports the trend without
      establishing it at alpha = 0.05".
  P5  v16 verdict: the exact honest-limitation wording requested ---
      not statistically significant (permutation p = 0.18), CI includes
      zero, supports the trend, does not establish at alpha = 0.05.

Part 2:
  P6  Insert the new subsection sec:novelty-v17 (Study E24, Option A:
      M3D + PRECISE expression coverage) after the v16 subsection.

All numbers come from download/novelty_v17_option_a_e24_results.json
(fresh run of scripts/novelty_v17_option_a_e24.py).
"""
import json
import sys

TEX = "/home/z/my-project/scripts/journal_manuscript.tex"
with open(TEX, encoding="utf-8") as f:
    src = f.read()
orig_len = len(src)
n_applied = 0


def apply(name, old, new, count=1):
    global src, n_applied
    if old in src:
        if src.count(old) != count:
            print(f"  {name}: expected {count}, found {src.count(old)} -- ABORT")
            sys.exit(1)
        src = src.replace(old, new)
        n_applied += 1
        print(f"  {name}: APPLIED")
    elif new.strip()[:90] in src:
        print(f"  {name}: already applied (idempotent)")
    else:
        print(f"  {name}: TARGET NOT FOUND -- ABORT")
        sys.exit(1)


# ----------------------------------------------------------------------
# P1: v15 forward pointer -> Option A executed as v17
# ----------------------------------------------------------------------
OLD_P1 = r"""Extending it requires either an expression compendium over the panel
(COLOMBOS/M3D, Option~A, deferred) or condition swaps that activate
the $14$ zero-$\kappa_V$ genes (Option~D) --- executed as the v16
round (\S\ref{sec:novelty-v16}), which re-activates $13/14$ of them
and computes the cross-condition correlation."""

NEW_P1 = r"""Extending it requires either an expression compendium over the panel
(COLOMBOS/M3D, Option~A) or condition swaps that activate
the $14$ zero-$\kappa_V$ genes (Option~D) --- executed as the v16
round (\S\ref{sec:novelty-v16}), which re-activates $13/14$ of them
and computes the cross-condition correlation, and followed by the
v17 round (\S\ref{sec:novelty-v17}), which obtains the compendium
and runs the panel-scale test."""

apply("P1 v15 forward-pointer", OLD_P1, NEW_P1)

# ----------------------------------------------------------------------
# P2: E10 remark -- v16 non-significance stated plainly + v17 pointer
# ----------------------------------------------------------------------
OLD_P2 = r"""The v16 round (\S\ref{sec:novelty-v16})
then swaps the FBA \emph{condition} itself: $13$ of the $14$
zero-$\kappa_V$ genes are activated under biologically matched
conditions, and the cross-condition correlation over the seven
endogenously re-activated genes is positive ($r = +0.571$,
sign-stable under leave-one-out) though under-powered at $n=7$."""

NEW_P2 = r"""The v16 round (\S\ref{sec:novelty-v16})
then swaps the FBA \emph{condition} itself: $13$ of the $14$
zero-$\kappa_V$ genes are activated under biologically matched
conditions, and the cross-condition correlation over the seven
endogenously re-activated genes is positive ($r = +0.571$,
sign-stable under leave-one-out) but under-powered and
\emph{not statistically significant} at $n=7$ (permutation
$p = 0.18$). The v17 round (\S\ref{sec:novelty-v17}) then supplies
the missing expression coverage externally and finds
$r = +0.374$ at $n = 433$ ($p \approx 10^{-15}$)."""

apply("P2 E10 remark honesty", OLD_P2, NEW_P2)

# ----------------------------------------------------------------------
# P3: v16 endogeneity paragraph -- explicit circularity
# ----------------------------------------------------------------------
OLD_P3 = r"""(a modeling assumption with no counterpart in
the experiment); their $\kappa_V$ would encode the assumed burden
scale rather than any model-derived signal, so they are reported
structurally but \emph{excluded} from the primary correlation."""

NEW_P3 = r"""(a modeling assumption with no counterpart in
the experiment); their $\kappa_V$ would encode the assumed burden
scale rather than any model-derived signal --- including them in the
correlation would make the test \emph{circular}, correlating the
echo of an assumption against the very data used to evaluate it ---
so they are reported structurally but \emph{excluded} from the
primary correlation and from every correlation statistic in this
subsection. The distinction, and the exclusion, are methodological
boundary conditions, not post-hoc choices."""

apply("P3 burden circularity explicit", OLD_P3, NEW_P3)

# ----------------------------------------------------------------------
# P4: v16 primary-result paragraph -- alpha = 0.05 phrasing
# ----------------------------------------------------------------------
OLD_P4 = r"""reassignments gives $p = 0.178$. Leave-one-out
sensitivity keeps $r \in [+0.47, +0.68]$ and strictly positive for
every omitted gene --- the sign is stable and is not carried by any
single point --- but the test is under-powered at $n=7$."""

NEW_P4 = r"""reassignments gives $p = 0.178$. Leave-one-out
sensitivity keeps $r \in [+0.47, +0.68]$ and strictly positive for
every omitted gene --- the sign is stable and is not carried by any
single point --- but the test is under-powered at $n=7$: it
\emph{supports the trend without establishing it} at $\alpha = 0.05$."""

apply("P4 primary-result alpha phrasing", OLD_P4, NEW_P4)

# ----------------------------------------------------------------------
# P5: v16 verdict -- the exact honest-limitation wording requested
# ----------------------------------------------------------------------
OLD_P5 = r"""The resulting association is
positive ($r = +0.571$), consistent in sign with the E10-lineage
estimates ($r \in [+0.08, +0.10]$) and stable under leave-one-out,
but individually non-significant at $n=7$. Together with E22's
finding that the Lemuth panel and the active-reaction gene set are
structurally disjoint, the honest conclusion is that local data
cannot decide the $\kappa_V \to$ transcript-response hypothesis at
meaningful power: what is missing is \emph{expression coverage} of
the multi-condition gene panel (Option~A), not more genes, mappings,
or conditions."""

NEW_P5 = r"""The resulting association is
positive ($r = +0.571$, $n = 7$), consistent in sign with the
E10-lineage estimates ($r \in [+0.08, +0.10]$) and sign-stable under
leave-one-out, but \emph{not statistically significant}: the exact
permutation test gives $p = 0.18$ and the $95\%$ bootstrap CI
$[-0.166, +0.969]$ includes zero. The cross-condition test
\emph{supports the trend but does not establish it at $\alpha =
0.05$}. Together with E22's finding that the Lemuth panel and the
active-reaction gene set are structurally disjoint, the honest
conclusion of the v16 round is that local data cannot decide the
$\kappa_V \to$ transcript-response hypothesis at meaningful power:
what is missing is \emph{expression coverage} of the
multi-condition gene panel (Option~A), not more genes, mappings, or
conditions. The v17 round (\S\ref{sec:novelty-v17}) obtains exactly
that coverage and decides the question."""

apply("P5 v16 verdict honest wording", OLD_P5, NEW_P5)

# ----------------------------------------------------------------------
# P6: insert the sec:novelty-v17 subsection before Main Proposition
# ----------------------------------------------------------------------
NEW_SUB = r"""
% =============================================================
\subsection{v17 external expression coverage: the genome-panel
test (E24)}\label{sec:novelty-v17}
% =============================================================

The v17 round (Study E24, ``Option A''; script
\texttt{novelty\_v17\_option\_a\_e24.py}) executes the step the v16
verdict identified as decisive: obtaining \emph{expression coverage}
for the E22 panel. Two compendia were retrieved directly and archived
(\texttt{data/m3d/}, \texttt{data/precise/}): the M3D \emph{E.~coli}
compendium (Faith et al.\ 2008, Nucleic Acids Res.\ 36:D866--D870;
\texttt{E\_coli\_v4\_Build\_6} from \texttt{m3d.mssm.edu},
$117{,}091{,}420$ bytes: $907$ uniformly normalized Affymetrix arrays
$\times$ $4{,}297$ gene probe sets, log$_2$ scale, structured
per-chip condition metadata) and PRECISE (Sastry et al.\ 2019,
bioRxiv 10.1101/080929; \texttt{github.com/SBRG/precise-db}, $278$
RNA-seq samples of K-12 MG1655 with per-sample carbon/nitrogen/
electron-acceptor metadata). The COLOMBOS host itself was unreachable
from the analysis environment, so coverage is closed with M3D --- one
of the two compendia Option~A named --- plus PRECISE as an
independent-platform check.

\emph{Combining C and D cannot substitute (the requested
evaluation).} The Lemuth series covers $92$ genes; symbol-matching
against the M3D probe tables recovers $74$ b-numbers, of which
exactly one ($b2097$) lies in the E22 panel --- the same
one-gene intersection E22 found against the Keio symbol table
($73$ b-numbers). Adding Option C's $435$ genes to Option D's $7$
on \emph{local} expression data therefore adds nothing: the binding
constraint is expression coverage, not gene supply, and only an
external compendium can lift it.

\emph{Design of the primary (genome-panel) test.} The E22 panel's
per-gene $\kappa_V$ values (baseline glucose-decline trajectory,
unchanged from E22) are tested against M3D's carbon-exhaustion
series: the Blattner/Allen ``carbon source foraging'' design (Allen
TE; MG1655, MOPS minimal $+$ NH$_4$, $37^{\circ}$C, aerobic) with a
log-phase glucose reference (\texttt{WT\_MOPS\_glucose}, $5$
replicates, $t=0$) and stationary-phase samples at $t = 135$, $330$,
$480$, $720$ min ($2$ replicates each; within-series contrasts, so
platform/lab effects cancel). Per gene, $|\log_2\mathrm{FC}|$ at each
time point is the stationary mean minus the reference mean, and the
primary response metric is the \emph{maximum} over the four time
points --- the same per-gene-max metric as E10. The perturbation
class is matched to the $\kappa_V$ trajectory (carbon exhaustion vs.\
declining glucose feed), but the experiments are not the same
experiment; this is a class-level test, stated as such.

\emph{Verification (five checks).}
\begin{enumerate}\itemsep0pt
\item \textbf{Source integrity} {[A-src]}: M3D tarball
  gzip-verified and fully extracted ($9$ files, $4{,}297 \times 907$
  gene matrix as documented); PRECISE retrieved via the SBRG
  repository ($3{,}923$ genes $\times$ $278$ samples, b-number
  index).
\item \textbf{Probe mapping} {[A-map]}: M3D probe sets embed their
  loci (\emph{aaeA\_b3241\_14} $\to$ b3241), cross-checked against
  the \texttt{probe\_set\_descriptions} table ($4{,}297/4{,}297$
  gene probes resolve, no duplicate loci in the genes-only file);
  $433/435$ panel genes carry expression (absent: \texttt{s0001},
  the iJO1366 spontaneous pseudo-entry, and \texttt{b4468}).
\item \textbf{Contrast design} {[A-contrast]}: verified from the
  structured metadata that the reference and all four stationary
  points share strain, medium, temperature, aeration, and
  experimenter, differing only in time point and growth phase.
\item \textbf{Definition consistency} {[A-def]}: $\kappa_V$ values
  are taken unchanged from the E22/E23 artifacts; the
  $\log_{10}\kappa_V$ transform matches the E10-lineage definition;
  every correlation runs over genes with non-zero $\kappa_V$
  variation only (the E22 panel guarantee).
\item \textbf{Zero control} {[A-zero]}: the $930$ iJO1366 genes
  whose baseline reactions are all inactive respond significantly
  less than the panel (mean max-$|\mathrm{FC}|$ $0.904$ vs.\
  $1.318$, median $0.679$ vs.\ $1.092$; Mann--Whitney
  $p = 7.8 \times 10^{-22}$) --- the zero-$\kappa_V$ regime is
  empirically distinguishable, not just analytically excluded.
\end{enumerate}

\emph{Primary result (genome panel, $n = 433$).} Pearson
$r(\log_{10}\kappa_V, \max|\log_2\mathrm{FC}|) = +0.3739$
($p = 8.2 \times 10^{-16}$), Spearman $+0.3991$
($p = 5.6 \times 10^{-18}$), $95\%$ bootstrap CI $[0.299, 0.446]$,
Monte-Carlo permutation $p < 10^{-4}$ ($10^5$ shuffles). The
association emerges with the depth of carbon exhaustion --- $r =
-0.02$ at $t=135$ (NS), $+0.26$ at $t=330$, $+0.40$ at $t=480$,
$+0.35$ at $t=720$ --- and is robust to the mean-metric
($+0.334$), to including late-log ($+0.374$), to removing $b2097$
($+0.373$), and to two out-of-series second-lab contrasts (M9/glycerol
stationary-vs-exponential, Oberto lab: $+0.111$, $p = 0.020$;
biofilm glucose-removal: $+0.175$, $p = 2.7 \times 10^{-4}$). The
top decile of $\kappa_V$ responds $2.2$-fold more than the bottom
decile ($1.923$ vs.\ $0.887$, MWU $p = 9.0 \times 10^{-8}$). By GPR
class the association is strongest for complex AND-GPR genes
($+0.604$) and mixed GPRs ($+0.528$), present for single-enzyme
genes ($+0.339$), weakest for isozyme OR-GPRs ($+0.173$) --- the
same ordering E22 found for $\kappa_V$ concentration.

\emph{Confound control.} Baseline expression level correlates with
both variables ($r(\kappa_V,\text{level}) = +0.291$;
$r(\max|\mathrm{FC}|,\text{level}) = +0.679$ --- highly expressed
genes show larger measured fold-changes), so part of the raw
association is level-mediated. The partial correlation controlling
for reference expression level remains $+0.251$
($p = 1.2 \times 10^{-7}$): the $\kappa_V$ association is genuine
but roughly one-third of the raw magnitude is shared with
expression level.

\emph{The PRECISE dissociation (class specificity).} The same panel
tested against PRECISE's ten WT carbon-\emph{switch} conditions
(galactose, glycerol, sorbitol, ribose, glucarate,
N-acetylglucosamine, gluconate, pyruvate, acetate, fructose vs.\
the glucose control) gives $r = -0.054$ ($p = 0.26$; Spearman
$+0.078$, NS): growing \emph{on another carbon source} does not
reproduce the association. Two readings are possible --- platform
difference (microarray vs.\ RNA-seq) or genuine perturbation-class
specificity (exhaustion of the feed, not substitution of it) ---
and the design cannot separate them; what the null \emph{does}
establish is that the M3D result is not a generic
``high-$\kappa_V$ genes respond to anything carbon-related''
artifact.

\emph{Matched-expression replication of E23.} Replacing the Lemuth
cross-condition fold-changes with \emph{matched-condition}
expression (proV/proW: M3D proline vs.\ glucose; ugpC: M3D glycerol
vs.\ glucose; narJ: PRECISE anaerobic glucose $+$ KNO$_3$;
galT: PRECISE galactose; b2097: M3D carbon exhaustion) reproduces
E23's estimate almost exactly: $r = +0.561$ at $n = 6$
($p = 0.25$) vs.\ E23's $r = +0.571$ at $n = 7$; the
ugpC-from-PRECISE sensitivity gives $+0.540$. treA has no matched
trehalose expression data in either compendium and is excluded
honestly. The two estimates bracket the same magnitude at the edge
of power; the genome-panel result is the decisive one.

\emph{Burden-class oxidative check (reported, not correlated).} The
v16 endogeneity criterion stands: burden-class $\kappa_V$ values
encode imposed rates and stay out of every correlation. PRECISE's
paraquat arm ($250\,\mu$M, WT) confirms the matched \emph{expression}
responses exist and are large --- \emph{sodA} $2.53$, \emph{bcp}
$1.02$, \emph{msrA} $0.59$ (\emph{yeaA} absent from PRECISE's
filtered matrix) --- so the exclusion is a modeling-boundary
decision, not a data gap.

\textbf{Verdict:} with external expression coverage the
$\kappa_V \to$ transcript-response hypothesis is \emph{decided in
the affirmative within the carbon-exhaustion class}: $r = +0.374$
at $n = 433$ ($p \approx 10^{-15}$; partial $r = +0.251$
controlling expression level), consistent in sign with every
lineage estimate (E10 masked $+0.08$--$+0.10$; E23 $+0.571$ at
$n=7$; E23 matched-expression replication $+0.561$ at $n=6$), and
bounded by an honest dissociation --- no association under
carbon-source \emph{switching} (PRECISE, NS), whose reading
(platform vs.\ class) remains open. The v16 limitation is resolved
not by more conditions but by coverage, exactly as its verdict
predicted.

\textbf{Artifacts.} Script:
\texttt{novelty\_v17\_option\_a\_e24.py} (plus four exploration
scripts \texttt{e24\_explore\_*.py}); data archives
\texttt{data/m3d/} ($117$ MB) and \texttt{data/precise/}. Outputs:
\texttt{novelty\_v17\_option\_a\_e24.\{csv,txt,png,results.json\}}
in \texttt{download/} (the CSV is the $433$-gene panel with all
per-contrast fold-changes and class flags).

"""

OLD_SEC = r"""\section{Main Proposition}\label{sec:mainprop}"""
NEW_SEC = NEW_SUB + OLD_SEC

apply("P6 insert v17 subsection", OLD_SEC, NEW_SEC)

# ----------------------------------------------------------------------
with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\nwrote {TEX}: {orig_len} -> {len(src)} chars "
      f"({len(src) - orig_len:+} applied patches: {n_applied})")

# sanity: balanced braces delta must be even
d_open = NEW_SUB.count("{") - NEW_SUB.count("}")
for nm, o, n in [("P1", OLD_P1, NEW_P1), ("P2", OLD_P2, NEW_P2),
                 ("P3", OLD_P3, NEW_P3), ("P4", OLD_P4, NEW_P4),
                 ("P5", OLD_P5, NEW_P5)]:
    d_open += n.count("{") - n.count("}") - (o.count("{") - o.count("}"))
print(f"brace delta from patch content: {d_open} (must be 0)")
assert d_open == 0, "unbalanced braces introduced!"
print("OK")
