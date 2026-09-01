#!/usr/bin/env python3
"""
v18 manuscript patcher.

Part 1 (user-directed v17 text review -- "correlational, not causal"):
  P1  Confound-control paragraph: state what the partial correlation
      DOES (removes the linear effect of expression level) and does
      NOT do (other confounders remain).
  P2  PRECISE-dissociation paragraph: the null control bounds the
      interpretation without isolating the mechanism; forward-point
      to the v18 resolution.
  P3  v17 verdict: association wording (no causal arrow), explicit
      "correlational, not causal" sentence, forward-pointer to v18.
  P4  v16 verdict forward-pointer: "decides the question" -> decides
      in the affirmative; v18 stress-tests the reading.
  P5  E10-remark history trail: append the v18 replication line.

Part 2:
  P6  Insert the new subsection sec:novelty-v18 (Study E25, the
      platform-vs-class 2x2 disambiguation) after the v17 subsection.

All numbers come from download/novelty_v18_e25_platform_class_results.json
(fresh run of scripts/novelty_v18_e25_platform_class.py).
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
# P1: confound control -- what the partial correlation does/does not show
# ----------------------------------------------------------------------
OLD_P1 = r"""association is level-mediated. The partial correlation controlling
for reference expression level remains $+0.251$
($p = 1.2 \times 10^{-7}$): the $\kappa_V$ association is genuine
but roughly one-third of the raw magnitude is shared with
expression level."""

NEW_P1 = r"""association is level-mediated. The partial correlation controlling
for reference expression level remains $+0.251$
($p = 1.2 \times 10^{-7}$): the $\kappa_V$ association is genuine
but roughly one-third of the raw magnitude is shared with
expression level. What the partial correlation \emph{does} is remove
the \emph{linear} effect of baseline expression level; what it does
\emph{not} do is address the remaining confounders --- gene length,
operon co-regulation, growth-rate coupling, and platform measurement
dynamic range among them --- so ``genuine'' here means
``not wholly a level effect,'' not ``unconfounded.'' Both the raw
($+0.374$) and the partial ($+0.251$) correlations are reported and
should be read together."""

apply("P1 partial-correlation does/does-not", OLD_P1, NEW_P1)

# ----------------------------------------------------------------------
# P2: PRECISE dissociation -- bounds, does not isolate; forward to v18
# ----------------------------------------------------------------------
OLD_P2 = r"""reproduce the association. Two readings are possible --- platform
difference (microarray vs.\ RNA-seq) or genuine perturbation-class
specificity (exhaustion of the feed, not substitution of it) ---
and the design cannot separate them; what the null \emph{does}
establish is that the M3D result is not a generic
``high-$\kappa_V$ genes respond to anything carbon-related''
artifact."""

NEW_P2 = r"""reproduce the association. Two readings are possible --- platform
difference (microarray vs.\ RNA-seq) or genuine perturbation-class
specificity (exhaustion of the feed, not substitution of it) ---
and the design cannot separate them: a negative control that changes
platform and class in a single step \emph{bounds} the interpretation
without \emph{isolating} the mechanism, so the null does not by
itself license the class-specificity reading. What the null
\emph{does} establish is that the M3D result is not a generic
``high-$\kappa_V$ genes respond to anything carbon-related''
artifact \emph{on the RNA-seq platform}. Which reading holds --- and
in what proportions --- is decided by the v18 round
(\S\ref{sec:novelty-v18}), which completes the
platform$\times$class matrix."""

apply("P2 dissociation bounds-not-isolates", OLD_P2, NEW_P2)

# ----------------------------------------------------------------------
# P3: v17 verdict -- correlational, not causal
# ----------------------------------------------------------------------
OLD_P3 = r"""\textbf{Verdict:} with external expression coverage the
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
predicted."""

NEW_P3 = r"""\textbf{Verdict:} with external expression coverage the
$\kappa_V$--transcript-response \emph{association} is \emph{decided
in the affirmative within the carbon-exhaustion class}: $r = +0.374$
at $n = 433$ ($p \approx 10^{-15}$; partial $r = +0.251$
controlling expression level), consistent in sign with every
lineage estimate (E10 masked $+0.08$--$+0.10$; E23 $+0.571$ at
$n=7$; E23 matched-expression replication $+0.561$ at $n=6$), and
bounded by an honest dissociation --- no association under
carbon-source \emph{switching} (PRECISE, NS), whose reading
(platform vs.\ class) is resolved by the v18 round
(\S\ref{sec:novelty-v18}). The finding is \emph{correlational, not
causal}: $\kappa_V$ is a model-derived sensitivity and the response
is a measured fold-change, so nothing in this design identifies the
direction of the relationship, the intermediate regulatory
machinery, or the mechanism. The v16 limitation is resolved
not by more conditions but by coverage, exactly as its verdict
predicted."""

apply("P3 verdict correlational-not-causal", OLD_P3, NEW_P3)

# ----------------------------------------------------------------------
# P4: v16 verdict forward pointer
# ----------------------------------------------------------------------
OLD_P4 = r"""what is missing is \emph{expression coverage} of the
multi-condition gene panel (Option~A), not more genes, mappings, or
conditions. The v17 round (\S\ref{sec:novelty-v17}) obtains exactly
that coverage and decides the question."""

NEW_P4 = r"""what is missing is \emph{expression coverage} of the
multi-condition gene panel (Option~A), not more genes, mappings, or
conditions. The v17 round (\S\ref{sec:novelty-v17}) obtains exactly
that coverage and decides the question in the affirmative; the v18
round (\S\ref{sec:novelty-v18}) then stress-tests the platform and
class readings of its dissociation control."""

apply("P4 v16 verdict pointer", OLD_P4, NEW_P4)

# ----------------------------------------------------------------------
# P5: E10 remark history trail -- append v18 line
# ----------------------------------------------------------------------
OLD_P5 = r"""The v17 round (\S\ref{sec:novelty-v17}) then supplies
the missing expression coverage externally and finds
$r = +0.374$ at $n = 433$ ($p \approx 10^{-15}$)."""

NEW_P5 = r"""The v17 round (\S\ref{sec:novelty-v17}) then supplies
the missing expression coverage externally and finds
$r = +0.374$ at $n = 433$ ($p \approx 10^{-15}$), and the v18
round (\S\ref{sec:novelty-v18}) shows the association replicates on
the RNA-seq platform under carbon depletion ($r = +0.187$ at
$n = 241$, $p = 2.9 \times 10^{-3}$) with both a platform and a
class component in the original dissociation."""

apply("P5 E10 remark v18 trail", OLD_P5, NEW_P5)

# ----------------------------------------------------------------------
# P6: insert sec:novelty-v18 after the v17 subsection
# ----------------------------------------------------------------------
OLD_SEC = r"""in \texttt{download/} (the CSV is the $433$-gene panel with all
per-contrast fold-changes and class flags).

\section{Main Proposition}\label{sec:mainprop}"""

NEW_SEC = r"""in \texttt{download/} (the CSV is the $433$-gene panel with all
per-contrast fold-changes and class flags).

% =============================================================
\subsection{v18 platform-versus-class disambiguation: completing
the \texorpdfstring{$2\times2$}{2x2} matrix (E25)}
\label{sec:novelty-v18}
% =============================================================

The v17 review identified the one open reading of the E24
dissociation: the PRECISE carbon-switch null changed
\emph{platform} (RNA-seq vs.\ microarray) and \emph{perturbation
class} (substitution vs.\ exhaustion of the carbon source) in a
single step, so either factor, or both together, could produce it.
Study E25 (script \texttt{novelty\_v18\_e25\_platform\_class.py};
fetch script \texttt{e25\_download\_data.py}; figure script
\texttt{e25\_plot.py}) completes the platform$\times$class
$2\times2$ design by filling the two missing cells with new data
and adds non-carbon stress controls on both platforms. The E22
$\kappa_V$ panel is again taken \emph{unchanged}; only the
expression side moves.

\emph{Data acquisition.} Two new sources. (i) GSE64021 (``Antisense
transcription and its roles in response to environmental changes
in E.~coli K12''; contributors Tabari, Li, Dong, Lee, Hwang, and
Su, UNC Charlotte; series public 2023-12-15, SRA study SRP050994;
no journal record linked at retrieval date, so it is cited by
accession): MG1655 grown in LB to OD$_{600} = 1.0$, pelleted, and
resuspended in MOPS minimal medium --- \emph{with} glucose (MOPS
control), \emph{without} glucose (carbon starvation, ``M-C''),
without KH$_2$PO$_4$ (phosphorus starvation, ``M-P''), or with
glucose at $48^{\circ}$C (heat shock, ``HS'') --- sampled at
$1/2/4/6$~h (HS also $15/30$~min); directional RNA-seq with
per-gene processed tables (mRNATPM; PeptideRaw --- used by the v19
round). All $22$ per-sample files were downloaded and checksummed
(\texttt{data/gse64021/README.md}). (ii) The M3D compendium itself
supplies the microarray switch cells: the same Blattner/Allen
WT\_MOPS series contains log-phase growth on alternative sole
carbon sources --- glycerol ($11$~mM, $2$ replicates), acetate
($17$~mM), proline ($6.7$~mM) --- against the log-phase glucose
reference ($5.6$~mM, $5$ replicates), plus three non-carbon acute
stress chips in MOPS$+$glucose (heat $50^{\circ}$C for $10$~min,
acid pH~$2$ for $10$~min, ciprofloxacin for $10$~min).

\emph{Verification (five checks).}
\begin{enumerate}\itemsep0pt
\item \textbf{Source integrity} {[S-src]}: every GSE64021 file
  gzip-verified and sha256-recorded at download; the M3D chips are
  the already-audited compendium matrices of E24.
\item \textbf{Gene mapping} {[S-map]}: GSE64021 gene names map to
  b-numbers via the PRECISE \texttt{gene\_info.csv} table
  (supplemented with iJO1366 gene names; $4{,}340$ names); $2{,}104$
  of $2{,}324$ named genes map ($221$ unmapped names, mostly
  non-K-12/MG1655 or RNA features); $241/435$ panel genes carry
  GSE64021 expression; $0$ duplicate overwrites.
\item \textbf{Contrast design} {[S-contrast]}: M-C vs.\ MOPS at
  \emph{matched} time points only (both arms share strain, prior
  growth, medium, resuspension, and sampling protocol; they differ
  only in the presence of glucose); HS contrasts use the matched
  $1/2/4$~h points; M3D switch contrasts are within-series (same
  lab, medium, phase; only the carbon source changes).
\item \textbf{Definition consistency} {[S-def]}: $\kappa_V$
  unchanged from E22; $\log_{10}$ transform as in the E10 lineage;
  per-gene $\max|\log_2\mathrm{FC}|$ response metric as in E10/E24,
  with per-condition $|\log_2\mathrm{FC}|$ values reported alongside.
\item \textbf{Zero control} {[S-zero]}: the $541$ model genes whose
  baseline reactions are all inactive respond significantly less
  than the panel in the GSE64021 carbon-starvation contrast (mean
  max-$|\mathrm{FC}|$ $3.22$ vs.\ $5.10$; Mann--Whitney
  $p = 1.5 \times 10^{-30}$).
\end{enumerate}

\emph{The two new cells.} [S1-array-switch] On the microarray
platform (the platform of the positive result), balanced growth on
alternative carbon sources gives a \emph{positive but attenuated}
association: per-condition $r$ of $+0.191$ (glycerol,
$p = 6.3 \times 10^{-5}$), $+0.158$ (acetate,
$p = 9.6 \times 10^{-4}$), $+0.165$ (proline,
$p = 5.6 \times 10^{-4}$), max-metric $r = +0.196$
($p = 3.9 \times 10^{-5}$; Spearman $+0.294$) --- roughly half the
E24 exhaustion value. [S2-seq-depletion] On the RNA-seq platform
(the platform of the null), carbon \emph{depletion} reproduces the
association: max-metric $r = +0.191$ at $n = 241$
($p = 2.9 \times 10^{-3}$; Spearman $+0.248$; permutation
$p = 0.003$; CI $[0.069, 0.315]$). The per-time course deepens with
starvation exactly as the E24 exhaustion course did --- $r =
+0.03$ (1~h, NS), $+0.15$ ($p = 0.019$), $+0.21$ ($p = 1.3 \times
10^{-3}$) at $4$~h --- before washing out at $6$~h ($-0.02$, NS;
by then the glucose in the control arm itself is plausibly
exhausted --- the control arm's own time course shows no $\kappa_V$
signal, $r = +0.06$, NS, so the wash-out is a both-arms effect,
not a recovery). The result is robust to merging the paired-end
re-sequencing libraries (identical $+0.191$), to the mean metric
($+0.139$, $p = 0.031$), to a $0.5$ pseudocount ($+0.140$,
$p = 0.030$), and --- strongest --- to requiring measurable TPM
($\geq 1$ in both arms of every contrast, removing all
zero-inflation artifacts: $r = +0.313$ at $n = 97$,
$p = 1.8 \times 10^{-3}$). The top $\kappa_V$ decile responds more
than the bottom decile ($5.93$ vs.\ $5.06$; MWU $p = 0.057$ ---
marginal at this $n$, reported as such).

\emph{The common-set matrix (the disambiguation).} All four cells
recomputed on the $240$ genes covered by \emph{both} platforms, so
the platform and class comparisons are within one fixed gene set:
\begin{center}
\begin{tabular}{lcc}
\hline
 & carbon depletion & carbon switch \\
\hline
microarray (M3D) & $+0.431$ ($p = 3.0 \times 10^{-12}$) &
$+0.184$ ($p = 4.3 \times 10^{-3}$) \\
RNA-seq & $+0.187$ ($p = 3.7 \times 10^{-3}$) &
$-0.058$ (NS) \\
\hline
\end{tabular}
\end{center}
Every one of the four Fisher-$z$ contrasts is significant: the
\emph{class effect} is real on both platforms (depletion $>$
switch: microarray $z = -2.99$, $p = 0.0028$; RNA-seq $z = +2.68$,
$p = 0.0073$), and the \emph{platform effect} is real in both
classes (microarray $>$ RNA-seq: depletion $z = -2.96$,
$p = 0.0031$; switch $z = +2.65$, $p = 0.0081$). The E24
dissociation was therefore \emph{over-determined} --- the stacked
attenuations of platform \emph{and} class --- and neither reading
alone is correct: the null was not pure class specificity, and the
positive was not a platform artifact.

\emph{Non-carbon stress controls (specificity revision).} The
acute-stress arms weaken any strict carbon-specificity reading.
On M3D, $10$-minute heat ($+0.295$), acid ($+0.303$), and
ciprofloxacin ($+0.284$) shocks in MOPS$+$glucose all show
$|\mathrm{FC}|$ associations comparable to carbon exhaustion; on
GSE64021, heat shock gives $+0.322$/$+0.393$/$+0.445$ at
$1/2/4$~h. Phosphorus starvation is null on the max metric
($+0.039$, NS) with a $4$~h transient ($+0.195$,
$p = 2.3 \times 10^{-3}$). The \emph{signed} direction is
consistent everywhere stress is acute: high-$\kappa_V$ genes move
\emph{down} (M3D stress $-0.22$ to $-0.29$; GSE64021 heat
$-0.30$ to $-0.31$; GSE64021 $4$~h starvation $-0.19$) --- the
energy-machinery genes that carry the $\kappa_V$ mass are
repressed when growth slows, whatever the cause. The honest
refinement of the v17 verdict is therefore that the association
tracks the \emph{severity of the growth-state transition} (carbon
exhaustion being the cleanest instance), not carbon identity:
present and strong under growth arrest, halved under balanced
growth on alternative carbon (microarray), absent under balanced
growth on the RNA-seq platform.

\textbf{Verdict:} the ambiguity is resolved with a two-factor
answer. The $\kappa_V$--transcript-response association (i) is
\emph{not} a microarray artifact --- it replicates on RNA-seq under
carbon depletion with a starvation-depth gradient and every
sensitivity check --- and (ii) has \emph{both} a class component
(depletion $>$ switch within each platform) and a platform
component (microarray amplifies the $|\mathrm{FC}|$ association
roughly twofold within each class), so the E24 null control was
over-determined and the v17 caution against reading it as pure
class specificity was warranted. The association is correlational,
directionally stress-responsive, and strongest for perturbations
that arrest growth; the mechanism remains open and is taken up by
the v19 protein-abundance round.

\textbf{Artifacts.} Script:
\texttt{novelty\_v18\_e25\_platform\_class.py} ($\sim$$500$
lines); data \texttt{data/gse64021/} ($22$ sample tables $+$
README with sha256). Outputs:
\texttt{novelty\_v18\_e25\_platform\_class.\{csv,txt,png,
results.json\}} in \texttt{download/} (the CSV carries the
$435$-gene panel with every per-condition fold-change, class and
stress annotations; the PNG shows the $2\times2$ matrix and the
per-condition bars).

\section{Main Proposition}\label{sec:mainprop}"""

apply("P6 insert v18 subsection", OLD_SEC, NEW_SEC)

# ----------------------------------------------------------------------
with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\n{orig_len} -> {len(src)} chars (+{len(src)-orig_len})")
print(f"{n_applied}/6 patches applied")
