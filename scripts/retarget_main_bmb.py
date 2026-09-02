#!/usr/bin/env python3
r"""Main-paper retarget pass (Bulletin of Mathematical Biology, no-fee
route) + two-paper division of labor per the 2026-09-02 blueprint:

  - PLOS-specific Author Summary removed; keywords trimmed to 6
  - natbib superscript numbered -> author-year [round] (BMB style)
  - PLOS refs file -> BMB refs file (alphabetical, natbib labels)
  - new [D5] "The categorical reading, in brief" subsection (adapted,
    summarized, cross-citing the companion theory paper -- no verbatim
    overlap with the companion)
  - Discussion "companion document" paragraph -> division-of-labor
    statement
  - Layer-1 porting-map appendix removed (internal provenance; lives
    in the repository)
  - residual v21 mentions in body text removed
"""
import io, sys

PATH = "/home/z/my-project/scripts/journal_manuscript_v2.tex"
tex = io.open(PATH, encoding="utf-8").read()

edits = []
def E(old, new, tag):
    edits.append((old, new, tag))

# ---- M1 header comment status
E(r"""%  Status:     Layer-1 in progress (E22-E27 ported; V6/V7 executed;
%              metric locked). The frozen v21 (scripts/
%              journal_manuscript.tex, 10,830 lines, DO NOT MODIFY)
%              remains the audit baseline.""",
r"""%  Status:     journal-ready. Target journal: Bulletin of
%              Mathematical Biology (Springer hybrid; subscription
%              route, no author charges). Author-year citations,
%              BMB reference list (scripts/build_bmb_refs.py). The
%              categorical framework is carried by the standalone
%              theory companion (scripts/companion_categorical.tex),
%              cross-cited here; [D5] states it in brief adapted
%              form only. The frozen v21 remains the audit baseline
%              in the repository (provenance, not cited in body).""",
"M1 header")

# ---- M2 natbib author-year
E(r"""\usepackage[super,sort&compress]{natbib}""",
r"""\usepackage[round]{natbib}""",
"M2 natbib round")

# ---- M3 remove Author Summary (PLOS-specific)
E(r"""\bigskip
\section*{Author Summary}
When a bacterium's environment changes, its metabolism must reroute:
reactions switch on and off, and the pattern of switching carries the
geometry of the adaptation. This paper gives that geometry an exact,
measurable form for flux-balance-analysis models: the second derivative
of the optimal flux map is a matrix-valued measure concentrated on the
switching surfaces of the active set. From this measure we derive a
per-gene sensitivity score (the measure mass along a gene's parameter
trajectory) and test it on \emph{E.~coli}: genes scored high by the
geometry are the genes whose transcription responds to carbon
starvation, with a robust statistical association that survives every
robustness check we designed (metric, tie-break convention, path, and
panel resampling), while the protein layer buffers the predicted
change. The same geometry organizes double-knockout epistasis and
predicts the memory of genetic loops. All code, data, and artifacts
are publicly available, and every number in the paper is regenerated
by committed scripts.

""",
r"""\bigskip

""",
"M3 remove Author Summary")

# ---- M4 keywords: 8 -> 6 (Springer convention)
E(r"""\noindent\textbf{Keywords:} discrete curvature; active set; parametric
linear programming; flux rerouting; carbon depletion; transcriptional
response; epistasis; holonomy""",
r"""\noindent\textbf{Keywords:} discrete curvature; active set; parametric
linear programming; flux rerouting; transcriptional response;
carbon depletion""",
"M4 keywords")

# ---- M5 [D5] subsection before section 4
E(r"""Theorem~\ref{thm:coupling} is the exact form of the value--flux
relation previously left open: the empirical $\kmu$ is the
per-reaction total variation of the flux-layer crease measure whose
objective contraction is $D^2\Phi$ --- the metric is the primal
layer of the canonical object, justified by identity rather than by
rank agreement.
\end{remark}

% =====================================================================
\section{The refinement--resolution bridge (Theorem B$'$)}
\label{sec:theoremB}""",
r"""Theorem~\ref{thm:coupling} is the exact form of the value--flux
relation previously left open: the empirical $\kmu$ is the
per-reaction total variation of the flux-layer crease measure whose
objective contraction is $D^2\Phi$ --- the metric is the primal
layer of the canonical object, justified by identity rather than by
rank agreement.
\end{remark}

\subsection{[D5] The categorical reading, in brief}\label{sec:categorical}

The measure-theoretic development above is self-contained: nothing in
this section uses categorical language, and the reader may take
$\kmu$ exactly as defined. This subsection records, briefly and in
adapted form, the categorical reading that first suggested the
active-set curvature interpretation; the full framework --- with its
constructions, proofs, and machine verifications --- is developed in
a companion theory paper \citep{zai2026categorical}, and nothing
below is a premise of the empirical results.

\emph{Strata as a stratified base.} The lexicographic pFBA engine
(\S\ref{sec:engine}) partitions parameter space into chambers on
which the optimizer is affine; the codimension-one facets where the
active set switches are exactly the facets that carry the atomic
measure $\mu$ of Definition~\ref{def:mu}. In the categorical reading,
this partition is a stratified base and the optimizer organizes the
policy fiber stratum by stratum, as a stratified connection in the
companion's $2$-category $\mathbf{StCon}(B)$: connection $1$-forms on
each stratum, glued along the switching facets by a boundary
transition satisfying a gauge matching condition, with a gluing
theorem (proved there by reduction to stack-descent theory, and with
its piecewise-holonomy consequences machine-verified in five loop
geometries and three structure groups).

\emph{The active-set bridge, summarized.} Two companion results
connect this geometry to viability, and we summarize them in words
(the displayed constructions appear in
\citep{zai2026categorical}). First, on each constant-active-set
stratum, a Fisher-minimal transport law defines the connection in
closed form as a constrained projection with the Fisher--Rao metric;
its curvature is the smooth avatar of the per-facet density that
$\mu$ concentrates on. Second, a small-loop viability--holonomy
theorem bounds the endpoint erosion of a viability margin around a
small parameter loop by the \emph{viability-weighted curvature}:
the worst case, over unit-area parameter bivectors and active
viability margins, of the positive part of the margin's change along
the connection curvature, normalized by the margin itself. The
per-pair form of $\kmu$ is the measure-theoretic discretization of
that object --- the atomic crease measure replaces the curvature
$2$-form, and the value--flux coupling
(Theorem~\ref{thm:coupling}) supplies the survival covectors.

\emph{Division of labor.} The present paper states only this brief
reading; the companion theory paper develops the SAVGS object, the
gluing theorem and piecewise holonomy formula, the
optic-composition semantics with its contraction analysis, the
filtered-colimit construction of autocatalytic sets, and the
homotopy-type-theoretic extension, with proofs and extensions. The
two manuscripts share no verbatim passages of length, and neither
depends on the other's claims: the association evidence below is
statistical and self-contained, and the categorical development is
mathematical and self-contained.

% =====================================================================
\section{The refinement--resolution bridge (Theorem B$'$)}
\label{sec:theoremB}""",
"M5 D5 subsection")

# ---- M6 Discussion companion paragraph
E(r"""\paragraph{The companion document.}
The categorical and homotopy-theoretic material of the predecessor
manuscript (optic-category composition, the $2$-category
$\mathbf{StCon}(B)$ of stratified connections, the gluing and
composition theorems, the filtered-colimit RAF construction, the
HoTT/$\infty$-categorical extension) is \emph{preserved, not
discarded}: it is extracted, with its status labels (proved /
conjecture / machine-verified), into a separate companion paper
(\emph{A Categorical Companion to the Measure-Theoretic Curvature
Framework}, compiled from the frozen v21 source), which shares no
load-bearing content with the present manuscript. The full frozen
v21 (10{,}830 lines) and its complete Git history remain committed
as the audit baseline; the split is a publication choice, not a
deletion.""",
r"""\paragraph{The companion theory paper.}
The categorical and homotopy-theoretic reading behind the
active-set curvature interpretation --- the $2$-category
$\mathbf{StCon}(B)$ of stratified connections with its gluing
theorem, the Fisher-minimal transport law on constant-active-set
strata, the optic-composition semantics with its contraction
analysis, the filtered-colimit construction of autocatalytic sets,
and the homotopy-type-theoretic extension --- is developed in full,
as a standalone theory paper with its own proofs and machine
verifications, in a companion manuscript \citep{zai2026categorical}.
The division of labor is deliberate and is disclosed here and in the
covering letter: this paper is the application --- the
measure-theoretic curvature of parametric FBA, the metric $\kmu$,
and the genome-scale empirical association with its layer decision
--- and carries only a brief adapted statement of the load-bearing
definitions (\S\ref{sec:categorical}); the companion carries the
framework. The two manuscripts share no verbatim passages of length
and neither depends on the other's claims.""",
"M6 discussion paragraph")

# ---- M7 remove the Layer-1 porting map appendix
E(r"""
\section{Layer-1 porting map}\label{sec:portmap}

\begin{tabularx}{\textwidth}{lX}
\toprule
\textbf{v2 section} & \textbf{v21 source (frozen; do not modify)} \\
\midrule
\S\ref{sec:intro} & v21 sec 1 (rewritten to the single story) \\
\S\ref{sec:notation} & v21 sec 2 (subset: active-set notation only) \\
\S\ref{sec:measure} & v21 active-set stratification defs; new D1/D2 \\
\S\ref{sec:theoremB} & new (Theorem B$'$; replaces the smooth bridge) \\
\S\ref{sec:computational} & M1/M3/M4 report bodies \\
\S\ref{sec:empirical} & v21 E22--E27 sections (E22, E23, E25, E26
      ported; E24 $\to$ E-V5 with the PRECISE arm; E27 $\to$ E-E27;
      V6/V7/V8/E32 new) \\
\S\ref{sec:discussion} & v21 discussion, rewritten as resolution statement \\
\S\ref{sec:methods} & v21 methods; engine documentation (expanded) \\
Appendices~\ref{sec:counts}--\ref{sec:proofs} & new (numeric audit
      ledger; proofs of Theorem~C and Propositions S, M) \\
companion & categorical/HoTT sections of v21 (preserved in
      \emph{A Categorical Companion}, separate document) \\
\bottomrule
\end{tabularx}

""",
r"""\vspace{0.6em}
\noindent\emph{Provenance note (for editors and reviewers).} A
section-level record of how this manuscript relates to the authors'
predecessor drafts, and the audit artifacts that accompany it, is
available from the public repository together with the code and
data; the covering letter summarizes the division of labor with the
companion theory paper \citep{zai2026categorical}.

""",
"M7 remove portmap")

# ---- M8 v21 remnants in body text
E(r"""Proposition~\ref{prop:semiconvex}. Panel construction passed four
verification checks (v21 \S E22, restored here after the content-loss
scan): (i) GPR mapping taken from cobra's authoritative""",
r"""Proposition~\ref{prop:semiconvex}. Panel construction passed four
verification checks: (i) GPR mapping taken from cobra's authoritative""",
"M8 e22 provenance")

E(r"""The refinement-stabilization question behind the frozen v21's
Route-5 program (\emph{do the empirical event point measures of the
lex-pFBA map converge as the sampled family grows?}) has a
near-term statistical form, proposed as E32 and executed here on""",
r"""The refinement-stabilization question
(\emph{do the empirical event point measures of the
lex-pFBA map converge as the sampled family grows?}) has a
near-term statistical form, proposed as E32 and executed here on""",
"M8b e32 provenance")

E(r"""$537$ & union of active reactions across conditions, $20.8\%$ (v16
         results json; the frozen v21's $538$ is a typo) \\
$525$ & genes with nonzero $\kappa$ across conditions (v16 results
         json; the frozen v21's $524$ is a typo) \\""",
r"""$537$ & union of active reactions across conditions, $20.8\%$ (v16
         results json) \\
$525$ & genes with nonzero $\kappa$ across conditions (v16 results
         json) \\""",
"M8c counts ledger")

# ---- M9 refs file
E(r"""\input{journal_manuscript_v2_plos_refs}""",
r"""\input{journal_manuscript_v2_bmb_refs}""",
"M9 refs file")

n_fail = 0
for old, new, tag in edits:
    c = tex.count(old)
    if c != 1:
        print(f"FAIL {tag}: count={c}")
        n_fail += 1
        continue
    tex = tex.replace(old, new, 1)
    print(f"OK   {tag}")

if n_fail:
    sys.exit(f"{n_fail} edits failed; file NOT written")
io.open(PATH, "w", encoding="utf-8").write(tex)
print("written:", PATH)
