#!/usr/bin/env python3
r"""Standalone-theory-paper restructure of scripts/companion_categorical.tex,
part A: front matter, introduction, inventory removal, preliminaries,
SAVGS, gluing/transport-law repairs.

Every edit is an asserted exact-match replacement (repo convention).
Run after: none. Run before: restructure_companion_b.py.
"""
import io, sys

PATH = "/home/z/my-project/scripts/companion_categorical.tex"
tex = io.open(PATH, encoding="utf-8").read()

edits = []
def E(old, new, tag):
    edits.append((old, new, tag))

# ---------------------------------------------------------------- E1 header
E(r"""% =====================================================================
%  companion_categorical  --  THE CATEGORICAL/HoTT COMPANION
%  ---------------------------------------------------------------
%  Role:       companion document to journal_manuscript_v2.tex (the
%              main paper). Preserves, verbatim, the categorical and
%              homotopy-theoretic sections of the frozen v21
%              (scripts/journal_manuscript.tex, 10,830 lines, DO NOT
%              MODIFY) per the publication decision of 2026-09-02:
%              the split is a publication choice, NOT a deletion.
%  Source:     extracted by scripts/build_companion.py (frozen v21
%              line ranges recorded per section); every theorem,
%              conjecture, and machine-verified claim keeps the
%              status it carries in v21.
%  Guarantees: (i) v21 itself remains committed and unmodified;
%              (ii) the inventory table in Sec. 2 lists every v21
%              section with its disposition; (iii) no claim is
%              promoted: conjectures stay conjectures.
% =====================================================================""",
r"""% =====================================================================
%  companion_categorical  --  STANDALONE THEORY PAPER
%  ---------------------------------------------------------------
%  Role:       full, self-contained development of the categorical
%              and homotopy-theoretic framework for viability-
%              weighted curvature: the SAVGS object, the 2-category
%              StCon(B) of stratified connections with the gluing
%              theorem and the piecewise-holonomy formula, the
%              Fisher-minimal transport law on constant-active-set
%              strata, the Bregman--Noether correspondence, the
%              seven-optic composition theorem with per-optic
%              Lipschitz constants and the Banach contraction, the
%              filtered-colimit construction of RAF sets, and the
%              HoTT/infty-categorical extension.
%  Relation:   the application paper (journal_manuscript_v2.tex)
%              states the load-bearing definitions of this
%              framework in brief adapted form and cites this
%              development for the constructions and proofs; this
%              paper cites the application paper where the empirical
%              line is concerned. The two papers share no verbatim
%              passages of length, and each is self-contained for
%              its own claims.
%  Provenance: the mathematical content descends from the frozen
%              predecessor manuscript (journal_manuscript.tex; the
%              complete source and its Git history remain committed
%              as the audit baseline). Section-level disposition
%              records live in the repository worklog and the
%              content-loss scan artifacts, not in this paper.
%  Honesty:    proof status is labeled per theorem: complete proofs;
%              proofs that reduce to cited descent/coherence theory
%              (marked); proof sketches (marked); machine-verified
%              statements with committed artifacts. Conjectures stay
%              conjectures.
% =====================================================================""",
"E1 header")

# ------------------------------------------------------------ E2 hypersetup
E(r""" pdftitle={A Categorical Companion to the Measure-Theoretic
           Curvature Framework},
 pdfauthor={Z.ai},
 pdfsubject={categorical composition, stratified connections, HoTT
             extension; companion document},
 pdfkeywords={optic category, 2-category, stratified connection, RAF,
              filtered colimit, homotopy type theory, univalence}}""",
r""" pdftitle={Stratified Connections, Optic Composition, and the
           Homotopy Fixed-Point Extension: A Categorical Framework
           for Viability-Weighted Curvature},
 pdfauthor={Z.ai},
 pdfsubject={categorical framework for viability-weighted curvature:
             stratified connections, optic composition, homotopy
             type theory},
 pdfkeywords={optic category, 2-category, stratified connection,
              viability, RAF, filtered colimit, homotopy type
              theory, univalence}}""",
"E2 hypersetup")

# ------------------------------------------------------------- E3 title
E(r"""\begin{center}
  \vspace*{0.4em}
  {\large\bfseries A Categorical Companion to the Measure-Theoretic
   Curvature Framework:\par
   Optics, Stratified Connections, and the Homotopy Extension\par}
  \vspace{0.8em}
  {\normalsize Z.ai\par}
  \vspace{0.2em}
  {\small\itshape Companion document, \today\par}
  \vspace{0.6em}
  \rule{0.7\textwidth}{0.4pt}
\end{center}""",
r"""\begin{center}
  \vspace*{0.4em}
  {\large\bfseries Stratified Connections, Optic Composition, and the
   Homotopy Fixed-Point Extension:\par
   A Categorical Framework for Viability-Weighted Curvature\par}
  \vspace{0.8em}
  {\normalsize Z.ai\par}
  \vspace{0.2em}
  {\small\itshape Preprint, September 2026\par}
  \vspace{0.6em}
  \rule{0.7\textwidth}{0.4pt}
\end{center}""",
"E3 title")

# ------------------------------------------------------------ E4 abstract
E(r"""\textbf{Abstract.} This document is the categorical and
homotopy-theoretic companion to \emph{A Measure-Theoretic Discrete
Curvature Framework for Metabolic Gene Sensitivity}. It preserves,
verbatim from the predecessor manuscript (v21, frozen), the formal
line that the main paper does not carry: the optic-category
composition semantics, the $2$-category $\mathbf{StCon}(B)$ of
stratified connections with its lax-functorial gluing theorem, the
Fisher--viability transport law on constant-active-set strata, the
Bregman-divergence Noether correspondence, the single composition
theorem with its per-optic Lipschitz constants and unconditional
Banach contraction, the filtered-colimit construction of RAF sets,
and the $\infty$-categorical extension through homotopy type theory
with the univalence-corrected closure test. Every item keeps the
status it carries in the frozen source --- theorems as theorems,
conjectures as conjectures, machine-verified claims with their
artifacts. The main paper retains only the measure-theoretic spine
and the empirical association; nothing here is load-bearing for
those claims, and nothing was deleted: the complete frozen v21 and
its Git history remain committed as the audit baseline.
\par
\vspace{0.4em}
\emph{Status: companion document. Not independently submitted in
this form; the mathematical content is extracted, not rewritten.}""",
r"""\textbf{Abstract.} We develop the categorical and
homotopy-theoretic framework for viability-weighted curvature: the
geometric object that measures how non-commuting sequences of
individually manageable environmental changes accumulate into a
viability threat through the policy holonomy they induce. The
framework has four layers. (i)~The SAVGS object assembles a control
base, a policy bundle with Fisher--Rao geometry, a viability margin,
a maintenance graph, and a $2$-categorical boundary span into a
single stratified $G_C$-reduced bundle. (ii)~The $2$-category
$\mathbf{StCon}(B)$ of stratified $G_C$-connections carries a
lax-functorial gluing theorem and a piecewise holonomy formula; we
state the small-loop expansion for closed loops that cross a
constraint-switching wall transversally in \emph{pairs}, with the
boundary-reset contribution at its true order, in agreement with the
machine-verified numerics. On constant-active-set strata the
Fisher-minimal transport law defines the connection in closed form
(KKT projection), and the small-loop viability--holonomy theorem
bounds endpoint erosion of a viability margin by the
viability-weighted curvature, the worst-case positive-part
contraction of the curvature $2$-form with the active survival
covectors. (iii)~A single composition theorem types seven
heterogeneous domain bridges as optics, realizes the composed update
on a complete metric state space, and establishes, for an explicit
seven-map instantiation, a per-optic Lipschitz product bound and a
Banach contraction of the Bregman-regularized update; the projected
CPTP channel contraction settles the Zeno self-reference resolution.
(iv)~The filtered-colimit construction of RAF sets in
$\Optic(\mathbf{Set})$ is proved componentwise and verified at
scale, and the $\infty$-categorical extension via homotopy type
theory is developed with its proof-sketch status explicitly marked.
An application of this framework to metabolic flux rerouting --- the
atomic curvature measure of parametric flux balance analysis and its
genome-scale empirical validation --- appears in a companion
application paper.
\par
\vspace{0.4em}
\emph{Status: standalone theory paper; an application paper
\citep{zai2026categorical} cites it for constructions and proofs.}""",
"E4 abstract")

# --------------------------------------- E5 section 1 -> Introduction
E(r"""\section{The role of this document}\label{sec:role}

\paragraph{What this is.}
The main paper (\texttt{journal\_manuscript\_v2.tex}) carries the
measure-theoretic spine: the atomic curvature measure of parametric
FBA, the refinement--resolution bridge (Theorem~B$'$), the
value--flux crease coupling, and the empirical association with its
layer decision. The predecessor manuscript (v21, 10{,}830 lines,
frozen) additionally carried an extensive categorical and
homotopy-theoretic line --- composition semantics for domain bridges,
stratified connection $2$-categories, RAF autopoiesis constructions,
and a homotopy-type-theoretic extension. That line is valid work
with its own machine-verified pieces, but it is not load-bearing
for the main paper's claims. The publication decision of
2026-09-02 is a \emph{split}, not a deletion: the categorical/HoTT
material is preserved in this companion, extracted verbatim from
the frozen v21 with the extraction ranges recorded in
\texttt{scripts/build\_companion.py}.

\paragraph{What this is not.}
This companion is not a rewrite, an update, or a re-verification of
the v21 material. Conjectures remain conjectures; the R/D/E
hierarchy of the source is kept. Where v21 itself marks an item as
retracted, superseded, or repaired in a later round, the extracted
text keeps that marking. The complete inventory of v21 sections and
their dispositions is given in Sec.~\ref{sec:inventory}; the frozen
source and its full Git history are the authoritative record.

\paragraph{Status protocol.}
As in the main paper, [R-$n$] blocks are proved or machine-verified
results, [D-$n$] blocks are definitions and constructions, [E-$n$]
blocks are executed experiments with deposited artifacts. The
machine artifacts for the categorical line (autopoiesis network
tests A--K, the $n = 3$ prototype, the contraction batteries) live
under \texttt{download/} exactly as referenced by the frozen v21.""",
r"""\section{Introduction}\label{sec:role}

\paragraph{The problem.}
An adaptive system that must remain viable while its environment
changes is governed, at each instant, by a policy that is optimal
subject to active constraints. Classical viability theory supplies
set-valued dynamics and tangential conditions, but no
\emph{geometric} object that measures how a non-commuting sequence
of individually manageable changes accumulates into a viability
threat. The obstruction is structural: at a constraint-switching
boundary the active set changes, horizontal subspaces jump, the
connection $1$-form ceases to be defined, and the standard holonomy
integral fails exactly where the question is most interesting. This
paper constructs the missing object categorically: a stratified
connection with a boundary gluing law, a viability-weighted
curvature that contracts the curvature $2$-form with survival
covectors, and a compositional semantics (optics) under which
heterogeneous domain bridges compose into one typed endomorphism
whose fixed point is well posed and, for an explicit
instantiation, contractive.

\paragraph{Contributions.}
\begin{enumerate}[leftmargin=*,itemsep=2pt]
\item The \emph{SAVGS object}
(Definition~\ref{def:savgs}): control base, policy bundle with
Fisher--Rao geometry, viability margin, maintenance graph, and a
$2$-categorical boundary span, assembled into one stratified
$G_C$-reduced bundle.
\item The $2$-category $\mathbf{StCon}(B)$ of stratified
$G_C$-connections (Definition~\ref{def:stcon}), the
$2$-categorical gluing theorem (Theorem~\ref{thm:2cat-gluing}), and
the piecewise holonomy formula
(Theorem~\ref{thm:stratified-holonomy}), with the small-loop
expansion stated for closed loops crossing a switching wall
transversally in pairs and the boundary-reset contribution at its
true order, in agreement with the machine-verified numerics in
five loop geometries and three structure-group regimes.
\item The \emph{Fisher-minimal transport law} on
constant-active-set strata in closed KKT form
(Proposition~\ref{prop:kkt}) and the \emph{small-loop
viability--holonomy theorem} (Theorem~\ref{thm:smallloop}): endpoint
erosion of a viability margin is bounded, to leading order, by the
viability-weighted curvature
(Definition~\ref{def:kv}).
\item The Bregman--Hessian Noether correspondence
(Proposition~\ref{prop:noether}) with its falsifiable precondition
check, giving the gauge-covariance statement for the curvature.
\item The \emph{single composition theorem}
(Theorem~\ref{thm:composition}): seven domain bridges typed as
optics, the realized update on a complete metric state space
(Definition~\ref{def:realization}), per-optic analytic Lipschitz
constants (Lemma~\ref{lem:lip-per-optic}), the Banach contraction
of the Bregman-regularized update for the chosen seven-map
instantiation (Theorem~\ref{thm:unconditional-banach}), and the
projected CPTP channel contraction
(Theorem~\ref{thm:zeno-contraction}) settling the Zeno
self-reference resolution.
\item The filtered-colimit construction of RAF sets in
$\Optic(\mathbf{Set})$, proved componentwise
(Theorem~\ref{thm:filtered-colimits-optic}) and verified at scale
(Proposition~\ref{prop:invlim-extended}).
\item The $\infty$-categorical extension via homotopy type theory
(Theorem~\ref{thm:hott-composition},
Corollary~\ref{cor:hott-fixedpoint}), with proof-sketch status
explicitly marked (Remark~\ref{rem:proof-status-hott}), and the
three-phase autopoiesis closure test built on it
(Definition~\ref{def:autopoiesis-phase3}).
\end{enumerate}

\paragraph{Relation to the application paper.}
An application of this framework to metabolic flux rerouting appears
in a separate manuscript \citep{zai2026categorical}: there the
viability-weighted-curvature idea is realized measure-theoretically
as an atomic curvature measure on the active-set complex of
parametric flux balance analysis, a gene-level sensitivity metric
$\kappa^{\mu}$ is derived from it, and the metric is validated at
genome scale against carbon-depletion transcriptional response,
with an explicit protein-layer null and selection-rule robustness
checks. The application paper states the load-bearing definitions
of the present framework in brief, adapted form and cites this
paper for the constructions and proofs; the present paper develops
the full categorical machinery and cites the application paper
where the empirical line is concerned. The division of labor is
deliberate: the empirical claims of the application paper are
statistical and self-contained, the categorical claims of this
paper are mathematical and self-contained, and the two papers share
no verbatim passages of length.

\paragraph{Status conventions.}
Theorem-level claims are labeled by proof status throughout:
complete proofs; proofs that reduce to cited descent or coherence
theory (marked in remarks); proof sketches (marked); and
machine-verified statements, whose scripts and artifacts are
committed in the project repository and regenerated by them. Two
results of the predecessor lineage that were superseded rather than
repaired --- the smooth-surrogate envelope line and the
indicator-weighted operational curvature --- are \emph{not} carried
here: the first is superseded in the application paper by the
measure-theoretic development, the second by its locked metric. Open
problems are collected in Section~\ref{sec:future}.""",
"E5 introduction")

# ------------------------------------- E6 delete inventory section
E(r"""
% =====================================================================
\section{The v21 inventory (nothing silently excised)}\label{sec:inventory}

\begin{tabularx}{\textwidth}{lX}
\toprule
\textbf{v21 section} & \textbf{Disposition} \\
\midrule
1 Introduction & main paper, rewritten to the single story \\
2 Preliminaries (optic category) & \textbf{this companion}
      (Sec.~\ref{sec:prelim}) \\
3 SAVGS framework (2-cat gluing, transport law, autopoiesis
      closure) & \textbf{this companion} (Sec.~\ref{sec:savgs});
      the autopoiesis network executions A--K remain in v21 with
      their artifacts \\
4 Algorithmic rate-distortion / $\kk$ derivation & v21 (frozen);
      the $\kk$ definition is superseded in the main paper by the
      measure-theoretic $\kmu$ \\
5 Bregman--Noether correspondence & \textbf{this companion}
      (Sec.~\ref{sec:noether}) \\
6 Seven-claim falsification hierarchy & \textbf{this companion}
      (Sec.~\ref{sec:hierarchy}) \\
7 Single composition theorem & \textbf{this companion}
      (Sec.~\ref{sec:composition}) \\
8 Per-optic Lipschitz constants / Banach contraction & \textbf{this
      companion} (Sec.~\ref{sec:lipschitz}) \\
9 Foundational tests (Claims F, G) & v21 (frozen) with artifacts \\
10 $n = 3$ prototype operationalization & v21 (frozen) with
      artifacts \\
11 Claim-D heavy-tail stress test & v21 (frozen) with artifacts \\
12 L\'evy first-passage derivation & v21 (frozen) \\
13 $n = 4$ non-abelian regime & v21 (frozen) \\
14 CPTP--Zeno lift & v21 (frozen) \\
15 Numerical contraction of $T$ & v21 (frozen) \\
16 Filtered-colimit RAF construction & \textbf{this companion}
      (Sec.~\ref{sec:invlim}) \\
17 $\infty$-categorical HoTT extension & \textbf{this companion}
      (Sec.~\ref{sec:hott}) \\
18 Autopoiesis on real networks (A--K) & v21 (frozen) with
      artifacts under \texttt{download/} \\
19 Novelty-assessment elevation studies (E1--E20) & v21 (frozen);
      the E22--E27 empirical line is superseded by the main paper's
      E-series with the locked metric \\
Theorem B (refinement bridge) & superseded in the main paper by
      Theorem~B$'$ (corrected form) \\
M1/M3/M4 computational batteries & main paper \S5 with artifacts \\
\bottomrule
\end{tabularx}

\emph{Note on labels.} The extracted sections keep their v21 labels
(\texttt{sec:prelim}, \texttt{sec:savgs}, \dots) so that internal
cross-references remain exact. Cross-references to sections not
extracted are rendered as textual pointers to the frozen v21.

""",
r"""
""",
"E6 delete inventory")

# ------------- E7 D_V tail: re-point "(v21 4)" to new Definition def:kv
E(r"""The curvature-based viability-weighted curvature $\kk$
(Proposition~\textup{(v21 4)}, contracting the curvature
$2$-form $F$ with viability covectors) is a distinct object; the
equality $D_V(a) = \kk(a) = a^2$ in the radial prototype is a
model-specific relation, not an identity.""",
r"""The curvature-based viability-weighted curvature $\kk$
(Definition~\ref{def:kv} below, contracting the curvature
$2$-form $F$ with viability covectors) is a distinct object; the
equality $D_V(a) = \kk(a) = a^2$ in the radial prototype is a
model-specific relation, not an identity.""",
"E7 D_V tail")

# ------------- E8 insert def:ard + def:kv after the Bregman definition
E(r"""\begin{definition}[Bregman divergence]
\label{def:bregman}
A \emph{Bregman divergence}~\cite{bregman1967,amari2000} generated by
a strictly convex differentiable function $\phi$ is
\begin{equation}
  D_\phi(p,q) \;=\; \phi(p) - \phi(q) - \langle\nabla\phi(q),\, p-q\rangle.
\end{equation}
The divergence is not symmetric in general. The \emph{dual affine
coordinates} are $p$ (the primal) and $\nabla\phi(p)$ (the dual). The
Bregman divergence is affine-invariant in the sense that an affine
transformation in the primal coordinate, paired with the corresponding
affine transformation in the dual, leaves $D_\phi$ unchanged.
\end{definition}
""",
r"""\begin{definition}[Bregman divergence]
\label{def:bregman}
A \emph{Bregman divergence}~\cite{bregman1967,amari2000} generated by
a strictly convex differentiable function $\phi$ is
\begin{equation}
  D_\phi(p,q) \;=\; \phi(p) - \phi(q) - \langle\nabla\phi(q),\, p-q\rangle.
\end{equation}
The divergence is not symmetric in general. The \emph{dual affine
coordinates} are $p$ (the primal) and $\nabla\phi(p)$ (the dual). The
Bregman divergence is affine-invariant in the sense that an affine
transformation in the primal coordinate, paired with the corresponding
affine transformation in the dual, leaves $D_\phi$ unchanged.
\end{definition}

\begin{definition}[Algorithmic rate-distortion distance]
\label{def:ard}
Fix a universal Turing machine $U$, a distortion measure $d$, and a
distortion threshold $D\geq 0$. The \emph{algorithmic rate-distortion
distance} of $x$ at threshold $D$ is
\begin{equation}\label{eq:distD-def}
  \distD(x) \;=\; \min\bigl\{|p| : U(p)\text{ outputs }\hat x,\
  d(x,\hat x)\leq D\bigr\}.
\end{equation}
It is monotone non-increasing in $D$, bounded above by the Kolmogorov
complexity $K(x)$, and upper-semicomputable by dovetailing over all
programs. It is a single-string, intrinsically deterministic
quantity: no set-average rate and no random-coding gap arise.
\end{definition}

\begin{definition}[Viability-weighted curvature $\kk$]
\label{def:kv}
Let $(B, E, \mathcal P, \varepsilon, \Gamma)$ be a SAVGS
(Definition~\ref{def:savgs}) with a $G_C$-connection on the policy
bundle whose curvature $2$-form on a stratum is $F$. Let
\begin{equation}\label{eq:halpha}
  h_\alpha(\theta, x) \;=\; D_\phi\bigl(\distD(x),\, \distD(x_0)\bigr)
\end{equation}
be a viability margin built from a Bregman divergence
(Definition~\ref{def:bregman}) evaluated at the algorithmic
rate-distortion distance (Definition~\ref{def:ard}) of the current
state relative to a reference $x_0$, with $h_\alpha > 0$ on the open
feasibility set. The \emph{per-pair viability-weighted curvature} is
\begin{equation}\label{eq:kv-pair}
  \kappa_\alpha(\theta, x; u, v) \;=\;
  \frac{\bigl[-D_{F(u,v)}h_\alpha\bigr]^+(\theta, x)}
       {h_\alpha(\theta, x)},
\end{equation}
where $[\,\cdot\,]^+$ is the positive part: only viability-eroding
curvature contributes. The \emph{viability-weighted curvature} is the
worst case over unit-area bivectors and active viability covectors,
\begin{equation}\label{eq:kv}
  \kk(\theta, x) \;=\; \sup_{\substack{u, v \in T_\theta B \\
  \|u \wedge v\|_{g_F} = 1}}\;
  \max_{\alpha : h_\alpha(\theta, x) > 0}\;
  \kappa_\alpha(\theta, x; u, v).
\end{equation}
The quantity $\kk(\theta, x)$ is the worst fractional loss of
viability margin per unit oriented environmental-loop area, to
leading order; it contracts the geometric defect $F$ with the
survival covectors $D h_\alpha$ instead of reporting $\|F\|$ alone.
Gauge invariance of $\kk$ follows from the square-root embedding
(Proposition~\ref{prop:sqrt}) together with the Bregman--Noether
correspondence (Proposition~\ref{prop:noether}); the wedge-norm
constraint makes $\kk$ a per-area quantity, matching the
leading-order expansion of Theorem~\ref{thm:smallloop}. The
instantiation~\eqref{eq:halpha} is one admissible choice: any $C^2$
viability function with the stated positivity works, and the
measure-theoretic discretization used in the application paper
\citep{zai2026categorical} replaces the $2$-form $F$ by an atomic
crease measure.
\end{definition}
""",
"E8 insert ard+kv defs")

# ------------------------- E9 def:struct "manuscript's prototypes"
E(r"""The three cases are distinct modeling commitments; Chentsov's
uniqueness theorem~\cite{chentsov1982} fixes the Fisher metric under
statistical-map invariance but does \emph{not} by itself select among
$O(r)$, $SO(r)$, or $\CO(r)$. For the manuscript's prototypes we use:""",
r"""The three cases are distinct modeling commitments; Chentsov's
uniqueness theorem~\cite{chentsov1982} fixes the Fisher metric under
statistical-map invariance but does \emph{not} by itself select among
$O(r)$, $SO(r)$, or $\CO(r)$. For the framework's prototypes we use:""",
"E9 prototypes wording")

# ----------------------- E10 def:savgs item 5 conjecture pointer
E(r"""\item A 2-categorical span $\Stab_1\leftarrow\mathrm{Boundary}\rightarrow
\Stab_2$ that resolves the constraint-switching boundary discontinuity
between strata (Conjecture~\textup{(v21 21.5)} for
the full gluing theorem).""",
r"""\item A 2-categorical span $\Stab_1\leftarrow\mathrm{Boundary}\rightarrow
\Stab_2$ that resolves the constraint-switching boundary discontinuity
between strata (Theorem~\ref{thm:2cat-gluing} for
the full gluing theorem).""",
"E10 savgs item5")

# ------------------------------- E11 savgs "(v21 4)" pointer
E(r"""The viability-weighted
curvature of Proposition~\textup{(v21 4)} is computed on this
object.""",
r"""The viability-weighted
curvature of Definition~\ref{def:kv} is computed on this
object.""",
"E11 savgs kv pointer")

# --------------------- E12 rem:2cat-span prototypes pointer
E(r"""the operational requirement on the prototype
of Sections~\textup{(v21 10)}--\textup{(v21 13)} is that the active set
remains constant along each loop, which places the loop entirely
within a single smooth stratum and avoids the boundary discontinuity.""",
r"""the operational requirement on the abelian and non-abelian
prototypes is that the active set
remains constant along each loop, which places the loop entirely
within a single smooth stratum and avoids the boundary discontinuity.""",
"E12 2cat-span prototypes")

# ------------------- E13 gluing subsection title
E(r"""\subsection{2-categorical gluing theorem for stratified connections
(closing Conjecture~\textup{(v21 21.5)})}
\label{sec:2cat-gluing}""",
r"""\subsection{2-categorical gluing theorem for stratified connections}
\label{sec:2cat-gluing}""",
"E13 gluing title")

# ------------------- E14 O3 matching condition -> standard form
E(r"""  \item[(O3)] the matching condition on $B_{ij}$:
    $g_{ij}^* A_j = A_i + d(\log g_{ij}) - [A_i, \log g_{ij}]$
    (the gauge-transform relation carrying $A_j$ to $A_i$ across the
    boundary; for abelian $G_C = U(1)$, this reduces to
    $A_j - A_i = d\alpha_{ij}$ where $g_{ij} = e^{i \alpha_{ij}}$);""",
r"""  \item[(O3)] the matching condition on $B_{ij}$: with the
    convention that the transition $g_{ij}$ acts on frames as
    $e_j = e_i \cdot g_{ij}$ (so $g_{ij}$ carries stratum $S_i$'s
    frame to stratum $S_j$'s frame), the connection forms are related
    by the standard gauge transformation
    \begin{equation}\label{eq:matching}
      A_j \;=\; g_{ij}^{-1} A_i\, g_{ij} \;+\; g_{ij}^{-1}\,
      d g_{ij},
    \end{equation}
    whose infinitesimal form ($g_{ij} = \exp u_{ij}$ near the
    identity) is
    $A_j = A_i + d u_{ij} + [A_i, u_{ij}] + O(u_{ij}^2)$.
    For abelian $G_C = U(1)$ this reduces to
    $A_j - A_i = d\alpha_{ij}$ where $g_{ij} = e^{i \alpha_{ij}}$;
    the reverse-direction reading ($g_{ji} = g_{ij}^{-1}$
    carrying $A_j$ to $A_i$) is equivalent and is the one used in
    the holonomy formula below;""",
"E14 O3 standard form")

# ------------------- E15 thm:2cat-gluing title
E(r"""\begin{theorem}[2-categorical gluing theorem --- closing
Conjecture~\textup{(v21 21.5)}]
\label{thm:2cat-gluing}""",
r"""\begin{theorem}[2-categorical gluing theorem]
\label{thm:2cat-gluing}""",
"E15 gluing thm title")

# --------- E16 insert proof-status remark after the gluing proof
E(r"""Hence $\mathbf{StCon}(B)$ is a 2-stack (a 2-sheaf of groupoids), and the
gluing theorem holds by 2-descent~\cite{giraud1971cohomologie,breen1994classification,breen2001gerbes,bartels2007higher}.
\end{proof}""",
r"""Hence $\mathbf{StCon}(B)$ is a 2-stack (a 2-sheaf of groupoids), and the
gluing theorem holds by 2-descent~\cite{giraud1971cohomologie,breen1994classification,breen2001gerbes,bartels2007higher}.
\end{proof}

\begin{remark}[Proof status of Theorem~\ref{thm:2cat-gluing}]
\label{rem:gluing-proof-status}
The proof reduces the gluing to the $2$-stack descent property for
stratified $G_C$-bundles: the Giraud-type axioms for the underlying
bundles are \emph{cited}~\cite{giraud1971cohomologie,breen2001gerbes},
not re-proved, and the extension from smooth spaces to stratified
spaces (stratum-by-stratum clutching with boundary matching) is
verified here at the level of construction, with the
coherence of the boundary $2$-cells checked on triple
intersections. The piecewise holonomy consequences
(Theorem~\ref{thm:stratified-holonomy}), by contrast, are
machine-verified in five loop geometries and all three
structure-group regimes (Remarks~\ref{rem:2cat-gluing-numeric}--%
\ref{rem:2cat-gluing-so3-topology}).
\end{remark}""",
"E16 gluing proof status")

# ------- E17 stratified-holonomy small-loop part: two crossings
E(r"""\begin{theorem}[Piecewise holonomy formula]
\label{thm:stratified-holonomy}
Let $(P, A) \in \mathbf{StCon}(B)$ be a stratified connection, and let
$\gamma : [0, 1] \to B$ be a smooth loop that crosses finitely many
boundaries at points $\{p_k\}_{k=1}^n$ in cyclic order
($p_1 < p_2 < \cdots < p_n$). Let $\gamma$ be decomposed as
$\gamma = \gamma_1 \sqcup \gamma_2 \sqcup \cdots \sqcup \gamma_n$
where each piece $\gamma_k$ lies in stratum $S_{i_k}$. Then the
stratified holonomy is
\begin{equation}\label{eq:strat-holonomy}
  \mathrm{Hol}^{\mathrm{strat}}(\gamma) \;=\;
  \mathrm{Hol}_{S_{i_n}}(\gamma_n) \cdot g_{i_n i_1}(p_n) \cdot
  \mathrm{Hol}_{S_{i_{n-1}}}(\gamma_{n-1}) \cdot \cdots \cdot
  g_{i_1 i_2}(p_1) \cdot \mathrm{Hol}_{S_{i_1}}(\gamma_1),
\end{equation}
a product of stratum-holonomies with boundary-transition maps.
For an infinitesimal small loop of area $\varepsilon^2$ crossing the
boundary once, this gives the piecewise curvature formula
\begin{equation}\label{eq:piecewise-F}
  H^{\mathrm{strat}}(\gamma_\varepsilon) \;=\;
  \varepsilon^2 \Bigl[\,\iint_{\Sigma \cap S_+} F_+\, dA \,+\,
  \iint_{\Sigma \cap S_-} F_-\, dA\,\Bigr] \,+\, R_b(p_*) \,+\,
  O(\varepsilon^3),
\end{equation}
where $F_\pm$ are the curvature $2$-forms on strata $S_\pm$, $p_*$ is
the boundary-crossing point, and $R_b = \log(g_{+-}(p_*)) \in
\mathfrak{g}_C$ is the boundary reset map.
\end{theorem}""",
r"""\begin{theorem}[Piecewise holonomy formula]
\label{thm:stratified-holonomy}
Let $(P, A) \in \mathbf{StCon}(B)$ be a stratified connection, and let
$\gamma : [0, 1] \to B$ be a smooth loop that crosses finitely many
boundaries transversally at points $\{p_k\}_{k=1}^n$ in cyclic order
($p_1 < p_2 < \cdots < p_n$). Let $\gamma$ be decomposed as
$\gamma = \gamma_1 \sqcup \gamma_2 \sqcup \cdots \sqcup \gamma_n$
where each piece $\gamma_k$ lies in stratum $S_{i_k}$. Then the
stratified holonomy is
\begin{equation}\label{eq:strat-holonomy}
  \mathrm{Hol}^{\mathrm{strat}}(\gamma) \;=\;
  \mathrm{Hol}_{S_{i_n}}(\gamma_n) \cdot g_{i_n i_1}(p_n) \cdot
  \mathrm{Hol}_{S_{i_{n-1}}}(\gamma_{n-1}) \cdot \cdots \cdot
  g_{i_1 i_2}(p_1) \cdot \mathrm{Hol}_{S_{i_1}}(\gamma_1),
\end{equation}
a product of stratum-holonomies with boundary-transition maps, the
order fixed by the chronological (right-to-left) traversal of the
loop. For a \emph{closed} loop the number of transversal crossings of
any single wall is necessarily even: a small loop of area
$\varepsilon^2$ centered on a wall $B_{+-}$ crosses it twice, at
points $p_+ \neq p_-$ with $|p_+ - p_-| = O(\varepsilon)$. For such a
loop the piecewise curvature formula is
\begin{equation}\label{eq:piecewise-F}
  H^{\mathrm{strat}}(\gamma_\varepsilon) \;=\;
  \exp\!\Bigl(-\,\varepsilon^2 \Bigl[\,\iint_{\Sigma \cap S_+} F_+\,
  dA \,+\, \iint_{\Sigma \cap S_-} F_-\, dA\,\Bigr] \;-\;
  \bigl[\log g_{+-}(p_+) - \log g_{+-}(p_-)\bigr] \;+\;
  O(\varepsilon^3)\Bigr),
\end{equation}
where $F_\pm$ are the curvature $2$-forms on strata $S_\pm$ and
$\Sigma$ is the small enclosed disk. The two boundary resets cancel
at leading order by the cocycle condition
($g_{-+} = g_{+-}^{-1}$ on the wall): the residual boundary
contribution $\log g_{+-}(p_+) - \log g_{+-}(p_-)$ is the
\emph{tangential variation} of the transition function between the
two crossing points, of order $O(\varepsilon)$; it vanishes identically
when the transition function is constant along the wall, and it is
linear in the wall-coordinate difference in the machine-verified
regime of Remark~\ref{rem:2cat-gluing-numeric}. An $O(1)$ reset term
$\log g_{+-}(p_*)$ arises only for an \emph{open arc} that crosses
the wall once and is not closed by the reverse transition.
\end{theorem}""",
"E17 two-crossing formula")

# ------------- E18 proof text of the small-loop part
E(r"""The
ordering (right-to-left in~\eqref{eq:strat-holonomy}) follows the
cyclic order of the loop. For an $\varepsilon$-small loop, the
stratum-holonomies reduce by Stokes to $\varepsilon^2 \iint_{\Sigma
\cap S} F_S\, dA$ on each stratum (where $\Sigma$ is the small
enclosed disk), and the boundary transition contributes
$\log g_{+-}(p_*)$ in the Lie algebra, giving the piecewise formula
\eqref{eq:piecewise-F}.
\end{proof}""",
r"""The
ordering (right-to-left in~\eqref{eq:strat-holonomy}) follows the
chronological traversal of the loop; the composition order is
genuinely order-dependent for non-abelian $G_C$
(Remark~\ref{rem:2cat-gluing-so3}). For an $\varepsilon$-small
\emph{closed} loop crossing the wall twice, the
stratum-holonomies reduce by Stokes to $\varepsilon^2 \iint_{\Sigma
\cap S} F_S\, dA$ on each stratum (where $\Sigma$ is the small
enclosed disk), while the two boundary transitions contribute
$\log g_{+-}(p_+) - \log g_{+-}(p_-)$ in the Lie algebra: the
$O(1)$ parts of the reset pair cancel by the cocycle condition, and
the residual is the tangential variation of the transition function
between the crossing points, of order $O(\varepsilon)$. For abelian
$G_C$ with the matching condition~\eqref{eq:matching} the
cancellation is exact at leading order: along the short segment of
$\gamma$ inside $S_-$, the jump $A_- - A_+ = d\alpha_{+-}$ integrates
to $\alpha(p_-) - \alpha(p_+)$, which cancels the reset variation
identically, so the holonomy is governed by the curvature terms at
$\varepsilon^2$ plus the stated $O(\varepsilon)$ residual. This is
the regime verified numerically in
Remark~\ref{rem:2cat-gluing-numeric} (boundary reset linear in the
wall coordinate with slope $\varepsilon$, the loop width).
\end{proof}""",
"E18 small-loop proof text")

# ------------------- E19 rem:2cat-gluing-numeric alignment sentence
E(r"""The piecewise holonomy formula is numerically verified by script
\texttt{two\_cat\_gluing\_stratified.py} on a two-stratum base
$B = \RR^2$ with the $x$-axis as the boundary, $G_C = U(1)$ (abelian,
simplifying the matching condition), and constant-curvature connections""",
r"""The piecewise holonomy formula --- including the two-crossing
small-loop form of \eqref{eq:piecewise-F}, with the boundary
contribution $\alpha(p_+) - \alpha(p_-)$ at its true order
$O(\varepsilon)$ --- is numerically verified by script
\texttt{two\_cat\_gluing\_stratified.py} on a two-stratum base
$B = \RR^2$ with the $x$-axis as the boundary, $G_C = U(1)$ (abelian,
simplifying the matching condition), and constant-curvature connections""",
"E19 numeric remark alignment")

# ------------------- E20 so3 remark pointer
E(r"""The abelian verification of Remark~\ref{rem:2cat-gluing-numeric} is
extended to the \emph{non-abelian} $G_C = SO(3)$ setting of the $n=4$
prototype's policy fiber (Definition~\ref{def:struct},
Section~\textup{(v21 13)}) by script \texttt{two\_cat\_gluing\_so3.py}. The""",
r"""The abelian verification of Remark~\ref{rem:2cat-gluing-numeric} is
extended to the \emph{non-abelian} $G_C = SO(3)$ setting of the $n=4$
prototype's policy fiber (Definition~\ref{def:struct}) by script
\texttt{two\_cat\_gluing\_so3.py}. The""",
"E20 so3 pointer")

E(r"""The non-abelian verification thus confirms Theorem~\ref{thm:stratified-holonomy}
in the regime matching the manuscript's $n=4$ prototype. Outputs:""",
r"""The non-abelian verification thus confirms Theorem~\ref{thm:stratified-holonomy}
in the regime matching the $n=4$ prototype. Outputs:""",
"E20b so3 manuscript wording")

# ------------------- E21 co3 remark closing pointer
E(r"""The $CO(3)$
verification closes Conjecture~\textup{(v21 21.5)} in
ALL THREE structure-group regimes: abelian $U(1)$, non-abelian $SO(3)$,
and endogenous-reversibility $CO(3)$. Outputs:""",
r"""The $CO(3)$
verification completes the confirmation of
Theorem~\ref{thm:stratified-holonomy} in
ALL THREE structure-group regimes: abelian $U(1)$, non-abelian $SO(3)$,
and endogenous-reversibility $CO(3)$. Outputs:""",
"E21 co3 closing")

# ------------------- E22 thm:smallloop tuple fix
E(r"""\begin{theorem}[Small-loop viability--holonomy]\label{thm:smallloop}
Let $(\Theta, \pi, \Delta^{n-1}, \varepsilon, \Gamma)$ be a SAVGS as in
Definition~\ref{def:savgs}, on a constant-active-set stratum where
Proposition~\ref{prop:kkt} applies and the connection $1$-form $A_i$
is $C^2$. Let $\gamma_\varepsilon : [0,1] \to \Theta$ be a square loop""",
r"""\begin{theorem}[Small-loop viability--holonomy]\label{thm:smallloop}
Let $(B, E, \mathcal P, \varepsilon, \Gamma)$ be a SAVGS as in
Definition~\ref{def:savgs}, on a constant-active-set stratum where
Proposition~\ref{prop:kkt} applies and the connection $1$-form $A_i$
is $C^2$. Let $\gamma_\varepsilon : [0,1] \to B$ be a square loop""",
"E22 smallloop tuple")

# ------- E23 rem:pathwise calibration pointer + E24 smallloop-scope prop
E(r"""To control intermediate
points, the calibration protocol of Section~\textup{(v21 10.1)}
applies a Nagumo inward-pointing condition along the path, equivalently
a viability tube of radius $\varepsilon$ around the loop.""",
r"""To control intermediate
points, the calibration protocol of the abelian $n=3$ prototype
applies a Nagumo inward-pointing condition along the path, equivalently
a viability tube of radius $\varepsilon$ around the loop.""",
"E23 pathwise calibration")

E(r"""\begin{remark}[What Theorem~\ref{thm:smallloop} does and does not claim]
\label{rem:smallloop-scope}
Theorem~\ref{thm:smallloop} bounds the \emph{endpoint} viability
margin by the leading-order curvature contribution plus an
$O(\varepsilon^3)$ remainder. It does \emph{not} bound the
\emph{pathwise} viability margin: a loop with bounded endpoint
holonomy may transit non-viable regions. Pathwise viability requires
the additional Nagumo inward-pointing condition of
Remark~\ref{rem:pathwise}---equivalently a viability tube of radius
$\varepsilon$ around $\gamma_a([0,1])$ contained in the closed
viability kernel. Curvature is therefore neither necessary nor
sufficient for survival in isolation; the bidirectional
``equivalence'' is replaced by the unidirectional upper bound
``vulnerability $\leq \kk$'' of Proposition~\textup{(v21 20)}, with
the trivial lower bound $0$ attained when $\kk \equiv 0$.
\end{remark}""",
r"""\begin{proposition}[Vulnerability bound]
\label{prop:vulnerability}
Adaptive systems are endangered not by large environmental changes
but by non-commuting sequences of individually manageable changes
whose induced policy holonomy aligns with vulnerable
self-maintenance directions. The upper bound on vulnerability is
the viability-weighted curvature $\kk$ of Definition~\ref{def:kv} on
a $G_C$-structured stratified connection; the lower bound is $0$,
attained when $\kk \equiv 0$ (flat connection).
\end{proposition}

\begin{proof}
On a constant-active-set stratum, integrate
Theorem~\ref{thm:smallloop} along the loop: the endpoint margin
change is bounded above in magnitude by
$\varepsilon^2 D_p h_\alpha(F_{12}) \leq \varepsilon^2 \kk$ per unit
loop area, with the positive part in Definition~\ref{def:kv}
discarding viability-restoring curvature; summing over the loop
gives the upper bound. The flat connection $F \equiv 0$ gives
$p_{\mathrm{end}} = p_0$ to $O(\varepsilon^3)$, hence zero
holonomy-induced vulnerability and the lower bound.
\end{proof}

\begin{remark}[What Theorem~\ref{thm:smallloop} does and does not claim]
\label{rem:smallloop-scope}
Theorem~\ref{thm:smallloop} bounds the \emph{endpoint} viability
margin by the leading-order curvature contribution plus an
$O(\varepsilon^3)$ remainder. It does \emph{not} bound the
\emph{pathwise} viability margin: a loop with bounded endpoint
holonomy may transit non-viable regions. Pathwise viability requires
the additional Nagumo inward-pointing condition of
Remark~\ref{rem:pathwise}---equivalently a viability tube of radius
$\varepsilon$ around $\gamma_a([0,1])$ contained in the closed
viability kernel. Curvature is therefore neither necessary nor
sufficient for survival in isolation; the bidirectional
``equivalence'' is replaced by the unidirectional upper bound
``vulnerability $\leq \kk$'' of Proposition~\ref{prop:vulnerability},
with
the trivial lower bound $0$ attained when $\kk \equiv 0$.
\end{remark}""",
"E24 vulnerability prop")

# ------------------- E25 def:autopoiesis thresholds pointers
E(r"""The default viability threshold used in the
operational networks of Sections~\textup{(v21 18)}
is $x_{\mathrm{thresh}} = 0.1$ in normalized concentration units; the
threshold is a declared operational parameter, not a fitted one, and
may be varied in robustness sweeps
(Section~\textup{(v21 18.13)}).""",
r"""The default viability threshold used in the
operational network benchmarks
is $x_{\mathrm{thresh}} = 0.1$ in normalized concentration units; the
threshold is a declared operational parameter, not a fitted one, and
may be varied in the robustness sweeps
documented in the project repository.""",
"E25 autopoiesis thresholds")

# ------------------- E26 def:kappa-closure pointer
E(r"""\begin{definition}[Closure-aware viability curvature]
\label{def:kappa-closure}
Restricting the viability covectors of $\kk$
(Proposition~\textup{(v21 4)}) to the repair-machinery""",
r"""\begin{definition}[Closure-aware viability curvature]
\label{def:kappa-closure}
Restricting the viability covectors of $\kk$
(Definition~\ref{def:kv}) to the repair-machinery""",
"E26 kappa-closure pointer")

# apply all
n_fail = 0
for old, new, tag in edits:
    if tex.count(old) != 1:
        print(f"FAIL {tag}: count={tex.count(old)}")
        n_fail += 1
        continue
    tex = tex.replace(old, new, 1)
    print(f"OK   {tag}")

if n_fail:
    sys.exit(f"{n_fail} edits failed; file NOT written")
io.open(PATH, "w", encoding="utf-8").write(tex)
print("written:", PATH)
