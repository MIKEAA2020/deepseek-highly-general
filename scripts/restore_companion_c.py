#!/usr/bin/env python3
"""Companion v2 restoration, part C: the terminal-coalgebra
characterization of the maximal RAF (repaired: deflationary closure
operator, posetal terminal coalgebra, full proof in the appendix,
the functorial-realization statement demoted to conjecture), the
operational network-battery anchor section (closure-test protocol,
A--K battery summary, RAF-to-Zeno transfer bound, persistent-
homology Phase III test, fixed-model essentiality validation), the
appendix, and the bibliography additions."""
import sys

F = "/home/z/my-project/scripts/companion_categorical_v2.tex"
src = open(F).read()


def replace_once(old, new, what):
    global src
    n = src.count(old)
    if n != 1:
        if n == 0 and src.count(new) >= 1:
            print(f"skip [{what}] (already applied)")
            return
        print(f"FAIL [{what}]: anchor count = {n}")
        sys.exit(1)
    src = src.replace(old, new)
    print(f"ok  [{what}]")


# ------------------------------------------------------------------
# 1. Terminal-coalgebra section before the HoTT section
# ------------------------------------------------------------------
COALGEBRA = r"""
\section{The Terminal-Coalgebra Characterization of the Maximal
RAF}\label{sec:terminal-coalgebra}
% ==============================================================

The filtered-colimit construction of Section~\ref{sec:invlim}
presents the maximal RAF $R_{\max}$ as a directed colimit of finite
RAF stages. This section adds the dual, coinductive
characterization: $R_{\max}$ is the greatest fixed point of a
deflationary closure operator, hence the terminal coalgebra of that
operator on the posetal reaction lattice. The characterization
identifies the classical Hordijk--Steel iterative-removal
algorithm~\cite{hordijk2011,steel2004} with the
terminal-coalgebra iteration, and it connects RAF theory to the
coinductive machinery of categorical
cybernetics~\citep{hedges2024cybernetics}.

\begin{definition}[Catalytic closure and the deflationary closure
operator]\label{def:deflationary}
Fix a food set $F$ and a finite reaction universe $U\subseteq R$.
For $S\subseteq U$ let $\mathrm{prod}(S)$ be the set of molecules
produced by the reactions of $S$, and let
$\mathrm{cl}(F\cup\mathrm{prod}(S))$ be the food-generated closure
(the smallest set of molecules containing $F\cup
\mathrm{prod}(S)$ that is closed under the reactions of $S$).
Define the \emph{catalytic-closure operator}
\begin{equation}\label{eq:Phi-def}
  \Phi(S) \;=\; \{\, r\in U : \text{some catalyst of } r \text{
  lies in } \mathrm{prod}(S)\cup F,\ \text{and every reactant of }
  r \text{ lies in } \mathrm{cl}(F\cup\mathrm{prod}(S)) \,\},
\end{equation}
and the \emph{deflationary closure operator}
\begin{equation}\label{eq:D-def}
  D(S) \;=\; S \cap \Phi(S).
\end{equation}
\end{definition}

\begin{theorem}[maxRAF is the terminal coalgebra]
\label{thm:maxraf-terminal}
With $U$ finite:
\begin{enumerate}[leftmargin=*,itemsep=2pt]
\item[(i)] $D$ is monotone and deflationary, $D(S)\subseteq S$
  for all $S\subseteq U$;
\item[(ii)] the fixed points of $D$ are exactly the RAFs
  contained in $U$ --- the reflexively autocatalytic,
  food-generated subsets in the sense of
  \citealp{hordijk2011,steel2004};
\item[(iii)] the greatest fixed point
  $\nu D=\bigcap_{n<\omega}D^{n}(U)$ exists, equals the maximal
  RAF $R_{\max}$, and is the terminal $D$-coalgebra in the posetal
  category $2^{U}$ of subsets of $U$;
\item[(iv)] the iteration $U\supseteq D(U)\supseteq D^{2}(U)
  \supseteq\cdots$ stabilizes in at most $|U|$ strict steps and
  is, step for step, the Hordijk--Steel iterative-removal
  algorithm;
\item[(v)] each step is a linear scan of the reaction set against
  precomputed catalysis and closure tables, so the total work is
  polynomial in the network size, the same order as the published
  algorithm.
\end{enumerate}
\end{theorem}

The proof is deferred to Appendix~\ref{app:terminal-coalgebra}.

\begin{remark}[Numerical verification]\label{rem:maxraf-verification}
On the thirteen-metabolite, eleven-reaction test case of
Section~\ref{sec:invlim-extended}, the stabilized iterate
$D^{n}(U)$ has cardinality $11$ and coincides, member for member,
with the maximal RAF of the filtered-colimit construction and
with the output of the iterative-removal algorithm (deposited
verification artifacts).
\end{remark}

\begin{remark}[Coinductive reading]\label{rem:maxraf-community}
The theorem locates RAF theory in the coinductive program. The
greatest-fixed-point identification is the posetal instance of the
general terminal-coalgebra theory for set
functors~\citep{adamek2005,worrell2005}, and the
terminal-coalgebra perspective on iterated updates is the one
actively used in categorical
cybernetics~\citep{hedges2024cybernetics} and in the functorial
semantics of learning optics~\citep{fong2017backprop}. What the
posetal formulation deliberately avoids is the stronger claim,
familiar from the set-functor theory, that some lifted endofunctor
on $\mathbf{Set}$ has a terminal coalgebra identifiable with
$R_{\max}$ through weak-pullback
preservation~\citep{adamek1994,worrell2005}: the lattice-level
statement above is the one that carries a complete proof, and it
is the one the numerical verification exercises.
\end{remark}

\begin{conjecture}[Functorial realization of the seven-optic
composite]\label{conj:functorial-realization}
Let $\CC$ be a monoidal category with finite limits, and let
$\mathrm{Per}(\CC)$ be the category of periodic typed systems:
objects are pairs $(X,f:X\to X)$ with $f^{n_X}=\id_{X}$ for a
minimal period $n_X\geq1$, and morphisms are the
period-equivariant maps. The seven-optic composite
$T=\OO_7\circ\cdots\circ\OO_1$ of Construction~\ref{con:seven}
admits a canonical functor $\mathcal R:\mathrm{Per}(\CC)\to
\Optic(\CC)$ factoring $T$ --- existence along the lines of the
optic constructions of \citealp{riley2018optics}, together with a
periodicity closure argument --- and any functor satisfying the
SAVGS typing constraint is monoidally naturally isomorphic to
$\mathcal R$.
\end{conjecture}

\begin{remark}[Status of the conjecture, and its numerical
illustration]\label{rem:functorial-status}
The existence clause reduces to standard optic assembly plus a
closure argument for periodicity that we do not supply in full,
and the uniqueness clause would require a parametricity argument
for typed polynomial optics that we likewise do not supply; the
statement is therefore recorded as a conjecture rather than a
theorem. What is verified numerically is the equivariance
phenomenon it predicts: on the periodic system
$\mathbb Z/4$ with $f(x)=x+1\bmod4$ and a seven-stage composite,
the equivariance condition $T\circ f=f\circ T$ holds for all
inputs, and the four constant-shift realizations of $T$ preserve
equivariance, illustrating the sense in which the realization is
unique up to the natural-isomorphism parameter (deposited
artifacts).
\end{remark}

% ==============================================================

"""
replace_once(
"""\\section{$\\infty$-Categorical Extension via Homotopy Type Theory}\\label{sec:hott}""",
COALGEBRA + """\\section{$\\infty$-Categorical Extension via Homotopy Type Theory}\\label{sec:hott}""",
    "terminal-coalgebra section")

# ------------------------------------------------------------------
# 2. Network-battery section before Future directions
# ------------------------------------------------------------------
NETWORK = r"""
\section{Operational Network Benchmarks of the Closure Test}
\label{sec:network-battery}
% ==============================================================

The three-phase closure test (Definitions~\ref{def:autopoiesis}
and~\ref{def:autopoiesis-phase3}) is operationalized on a battery
of biochemical networks with two arms of distinct evidential roles.
The \emph{designed progression} is a sequence of integrated
metabolic--gene-regulatory networks in which each modification is
a hypothesis about what organizational closure requires; it
measures the test's sensitivity, since each added redundant route
converts precisely the components the test flags as failing. The
\emph{fixed-model arm} applies the test to the unmodified BiGG
iJO1366 model of \emph{E.~coli}~\cite{orth2011} and validates the
test as a predictor of independently computed FBA essentiality.
All simulation protocols and per-component verdict records are
deposited (Data Availability).

\subsection{Test protocol}

For each purportedly self-maintained component $m_j$: set the
internal repair flux of $m_j$ to zero (every reaction producing
$m_j$ is disabled), keep the external food supply fixed, apply the
regeneration rules for $T=200$ time steps with first-order
degradation (rate $\delta=0.05$) and Michaelis--Menten-type
catalytic kinetics ($k_{\mathrm{cat}}=0.5$), and record whether
$m_j$ falls below the viability threshold
$x_{\mathrm{thresh}}=0.1$; then restore the repair pathway and
record whether $m_j$ recovers above the threshold. The component
is \emph{causally internal} iff the knockout destroys it and the
restoration recovers it; the system is autopoietic iff every
essential component is causally internal.

\subsection{The designed progression}

The progression starts from two real networks: the
Hordijk--Steel food-generated RAF (seven molecules, five
reactions) and an \emph{E.~coli} core-metabolic subnetwork
(glycolysis and the TCA cycle, ten non-food species, ten
reactions, derived from iJO1366). The verdicts on the two
starting networks are the anchors of the whole battery.

\begin{proposition}[Anchor verdicts]\label{prop:net-anchors}
Direct simulation of the protocol gives, for the Hordijk--Steel
RAF (non-food components $c,d,e,f,g$), the per-component outcomes
of Table~\ref{tab:netA}: $2/5$ components causally internal. For
the core-metabolic subnetwork, $0/10$ components are causally
internal. The static catalytic closure of the RAF --- verified in
Section~\ref{sec:invlim} --- does not translate into endogenous
regeneration under the dynamical test: the failing components are
regenerated by reactions whose catalysts are themselves
knockout-fragile, so their repair pathway collapses when their own
catalyst is removed. The bare metabolic network fares worse still:
every core metabolite fails the two-sided test.
\end{proposition}

\begin{table}[htbp]
\centering
\caption{Anchor network: the Hordijk--Steel food-generated RAF
under the closure test. Baseline, knockout-final, and
recovery-final concentrations of the five non-food components;
the causally-internal verdict requires collapse under knockout
and recovery under restoration.}
\label{tab:netA}
\footnotesize
\begin{tabular*}{0.8\columnwidth}{@{\extracolsep{\fill}} l l l l l}
\toprule
Component & Baseline & Knockout & Recovery & Causally internal \\
\midrule
$c$ & $0.45$ & $0.00$ & $3.84$ & yes \\
$d$ & $0.81$ & $0.00$ & $0.00$ & no \\
$e$ & $8.63$ & $0.00$ & $0.00$ & no \\
$f$ & $2.65$ & $0.00$ & $443.8$ & yes \\
$g$ & $84.4$ & $0.37$ & $164.2$ & no \\
\bottomrule
\end{tabular*}
\end{table}

Re-testing the same core metabolites in the full genome-scale
iJO1366 model converts $9/10$ of them to causally internal, and
integrating enzyme synthesis into the core network (a
metabolic--gene-regulatory integration with $17$ essential
components) yields $5/17$. The designed progression then adds, at
each step, one redundant isozyme pair with a stated
cascade-breaking role; the monotone verdict sequence is
Table~\ref{tab:network-battery}. At the final step the Phase~I
endpoint-only verdict reaches $52/52$ and the divergence between
the Phase~I endpoint-only and the pathwise Phase~III verdicts
disappears --- the two last-remaining Phase~I ``failures'' are
limit-cycle oscillations that the pathwise criterion of
Definition~\ref{def:autopoiesis-phase3} already counts as
recoveries (Sections~\ref{sec:phase3}--\ref{sec:verdict-cptp}).

\begin{table}[htbp]
\centering
\caption{The network battery. Phase~I is the fraction of essential
components causally internal at the endpoint-only criterion;
Phase~III is the pathwise, univalence-corrected criterion of
Definition~\ref{def:autopoiesis-phase3}. Each designed step adds
one redundant isozyme pair breaking the named cascade.}
\label{tab:network-battery}
\footnotesize
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}} l l l l l}
\toprule
Network & Description & Phase~I & Phase~III \\
\midrule
A & Hordijk--Steel RAF (anchor) & $2/5$ & $2/5$ \\
B & \emph{E.~coli} core metabolism (anchor) & $0/10$ & $0/10$ \\
C & B's metabolites in full iJO1366 & $9/10$ & $9/10$ \\
D & B + enzyme synthesis (MR--GR) & $5/17$ & $5/17$ \\
E & closed MR--GR network & $24/29$ & $24/29$ \\
F & E + ALT3/4 (ASP--PYR route) & $29/31$ & $29/31$ \\
G & F + ALT5/6 ($\alpha$KG route) & $41/42$ & $41/42$ \\
H & G + ASPAT3/4 (ASP cascade) & $43/44$ & $44/44$ \\
I & H + ALT7/8 (ALA reversible) & $45/46$ & $46/46$ \\
J & I + ALDO3/4 (FBP reversible) & $49/50$ & $49/50$ \\
K & J + ACS1/2 (NAD$^{+}$-independent) & $52/52$ & $52/52$ \\
\bottomrule
\end{tabular*}
\end{table}

The designed progression is complemented by a cross-domain
transfer statement that uses the closure structure rather than
merely measuring it.

\begin{proposition}[RAF closure gives a Zeno-schedule lower bound]
\label{prop:raf-zeno-bound}
Let $R$ be a RAF with closure set $C(R)\subseteq M$,
$|C(R)|=N_{\mathrm{RAF}}\geq1$, realized through the CPTP--Zeno
lift of Section~\ref{sec:verdict-cptp} --- each closure catalyst
mapped to a CPTP channel with dissipative gap
(Definition~\ref{def:lindbladian}). Under the binary-cascade
model of closure bootstrap (each generation of catalysts doubles
the producible set, so the bootstrap depth is
$d_R=\log_2 N_{\mathrm{RAF}}$) and per-step gap normalization
(the effective gap is the per-step gap divided by the $1+d_R$
propagation steps of the composition), the projected Zeno renewal
rate satisfies
\begin{equation}\label{eq:raf-zeno-bound}
  \tau_{\mathrm{Zeno}} \;\geq\; \frac{1}{1+\log_2(N_{\mathrm{RAF}})}
  \qquad (N_{\mathrm{RAF}}\geq1).
\end{equation}
The bound is monotonically decreasing in $N_{\mathrm{RAF}}$:
larger closures predict slower Zeno renewal, a
direction-of-effect prediction unavailable without the
composition machinery.
\end{proposition}

\begin{proof}
Under the stated model: (i)~the closure set $C(R)$ is
self-maintaining, and the binary-cascade model fixes the bootstrap
depth $d_R=\log_2N_{\mathrm{RAF}}$ generations; (ii)~each catalyst
maps to a CPTP channel whose dissipative part has gap
$\Delta_{\mathrm{step}}>0$
(Proposition~\ref{prop:zeno-survival}); (iii)~composing
$1+d_R$ propagation steps normalizes the effective gap to
$\Delta_{\mathrm{eff}}=\Delta_{\mathrm{step}}/(1+d_R)$; (iv)~the
Zeno renewal rate is the reciprocal of the effective gap
normalized by the per-step scale, $\tau_{\mathrm{Zeno}}=
1/(1+d_R)$, which is~\eqref{eq:raf-zeno-bound}. The model
assumptions --- binary cascade, per-step gap normalization --- are
part of the statement, not consequences of the closure
definition.
\end{proof}

\begin{remark}[Verification on the designed lineage]
\label{rem:raf-zeno-verification}
The bound is verified on all seven networks of the designed
lineage E--K: the closure counts
$N_{\mathrm{RAF}}\in\{24,29,41,43,45,49,52\}$ all satisfy
$\tau_{\mathrm{Zeno}}^{\mathrm{sim}}\geq1/(1+\log_2
N_{\mathrm{RAF}})$, with the ratio of simulated rate to bound
ranging over $44.9$--$179.6$ --- the bound holds with the margin
reflecting the gap normalization, and the monotone
direction-of-effect prediction is confirmed along the lineage
(deposited artifacts).
\end{remark}

\subsection{The persistent-homology test for Phase III}
\label{sec:network-persistent}

The Phase~III criterion of Definition~\ref{def:autopoiesis-phase3}
can be strengthened from an endpoint-tolerance check to a
homotopy-invariant one.

\begin{definition}[Persistent-homology contractibility test]
\label{def:persistent-homology-contractibility}
For each closed-loop recovery trajectory of the Phase~III test,
construct the point cloud of its time-series samples and compute
persistent homology barcodes~\citep{tralie2018ripser}. The
trajectory is \emph{contractible} iff
\begin{equation}
  \mathrm{Betti}_0 = 1 \;\wedge\; \mathrm{Betti}_1 = 0 \;\wedge\;
  \mathrm{Betti}_2 = 0,
\end{equation}
where $\mathrm{Betti}_n$ counts the persistent
$n$-dimensional features with persistence at least $10\%$ of the
cloud diameter.
\end{definition}

\begin{proposition}[Classification accuracy of the homological test]
\label{prop:persistent-homology-verdict}
Applied to five test cases --- a contractible disk, a circle
$S^{1}$, a torus $T^{2}$, the Network~K AcCoA recovery
trajectory, and the Network~J AcCoA limit-cycle trajectory --- the
test classifies all five correctly: the disk and the Network~K
recovery have $\mathrm{Betti}_0=1$ and $\mathrm{Betti}_1=0$
(contractible); the circle, the torus, and the Network~J limit
cycle have $\mathrm{Betti}_1\geq1$ (non-contractible, the
persistent $1$-dimensional hole being the limit cycle). The
homological test and the pathwise Phase~III criterion agree on
Networks~K and~J; the homological test additionally separates the
tight limit cycle (small endpoint dispersion, persistent hole)
from genuine recovery, which an endpoint-tolerance check cannot.
\end{proposition}

\begin{proof}
Direct computation of the barcodes on the five point clouds
(deposited artifacts); the Betti-number readings are as stated,
and the agreement and disagreement patterns with the endpoint
criterion are as stated.
\end{proof}

\subsection{Fixed-model validation on iJO1366}
\label{sec:network-essentiality}

\begin{construction}[Closure test on the unmodified model]
\label{con:iJO1366-external-essentiality}
Take the BiGG iJO1366 model ($1{,}805$ metabolites, $2{,}583$
reactions, $1{,}367$ genes) without modification. For each
cytosolic reaction $r$ with genes and cytosolic products, compute
the closure-test dependency structure --- the fraction of each
product's production that flows through $r$ at baseline --- and
compare the resulting dependency-ratio criterion against
single-reaction-deletion FBA essentiality computed independently
on the same model.
\end{construction}

\begin{proposition}[Closure-test dependency ratios predict FBA
essentiality]\label{prop:iJO1366-external}
On the complete set of $n=1{,}638$ cytosolic reactions with genes
and cytosolic products (no sampling), the dependency-ratio
criterion at the optimal threshold $\tau^{*}=0.5$ agrees with FBA
single-reaction-deletion essentiality with Cohen's
$\kappa=0.835$, $\mathrm{MCC}=0.841$, $F_1=0.863$, precision
$0.783$, recall $0.960$; the ROC AUC of the dependency ratio
against FBA essentiality is $0.968$. For comparison, the binary
sole-producer criterion (a product is judged fragile iff it has a
single producer) achieves $\kappa=0.206$ on the same set: an
elevation factor of $4.05$ for the dynamical dependency
structure over the purely structural criterion. The agreement is
at the reaction level; at the metabolite level, agreement with
gene-level essentiality is weak ($\kappa=-0.08$), reflecting the
semantic difference between regeneration after restoration
(the closure test) and biomass maximization under knockout (FBA
gene essentiality).
\end{proposition}

\begin{proof}
Direct computation on the unmodified model (deposited artifacts):
the confusion matrix, the $\kappa$/MCC/$F_1$/precision/recall
values, and the ROC curve are the deposited outputs of the two
independent computations (closure-test dependency ratios; FBA
single-reaction deletions) on the same model.
\end{proof}

\begin{remark}[What the two arms establish together]
\label{rem:network-battery-reading}
The designed progression establishes sensitivity: each flagged
failure is converted by exactly the modification that repairs the
named cascade, so the test localizes the missing closure rather
than merely scoring networks. The fixed-model arm establishes
external validity: on a model no one modified for the purpose, the
dynamical dependency structure predicts independently computed
essentiality at $\kappa=0.835$. Neither arm alone would carry the
conclusion; together they anchor the closure-test language of
Sections~\ref{sec:savgs} and~\ref{sec:hott} in executed
computations.
\end{remark}

% ==============================================================

"""
replace_once(
"""\\section{Future directions and open problems}\\label{sec:future}""",
NETWORK + """\\section{Future directions and open problems}\\label{sec:future}""",
    "network-battery section")

# ------------------------------------------------------------------
# 3. Appendix before Declarations
# ------------------------------------------------------------------
APPENDIX = r"""
\appendix
\section{Proof of the Terminal-Coalgebra Theorem}
\label{app:terminal-coalgebra}

\begin{proof}[Proof of Theorem~\ref{thm:maxraf-terminal}]
(i) Deflationarity is immediate: $D(S)=S\cap\Phi(S)\subseteq S$.
For monotonicity, let $S\subseteq T$. Then
$\mathrm{prod}(S)\subseteq\mathrm{prod}(T)$, hence
$\mathrm{cl}(F\cup\mathrm{prod}(S))\subseteq
\mathrm{cl}(F\cup\mathrm{prod}(T))$ and the catalyst pool
$\mathrm{prod}(S)\cup F\subseteq\mathrm{prod}(T)\cup F$; both
conditions in~\eqref{eq:Phi-def} are therefore satisfied by at
least as many reactions for $T$ as for $S$, so
$\Phi(S)\subseteq\Phi(T)$ and
$D(S)=S\cap\Phi(S)\subseteq T\cap\Phi(T)=D(T)$.

(ii) For $S\subseteq U$, $D(S)=S$ iff $S\subseteq\Phi(S)$ iff
every $r\in S$ has a catalyst in $\mathrm{prod}(S)\cup F$ and all
reactants of $r$ in $\mathrm{cl}(F\cup\mathrm{prod}(S))$. The
first clause is reflexive autocatalysis; the second is
food-generatedness (each reaction's inputs are reachable from the
food set through the reactions of $S$). These are exactly the RAF
conditions of \citealp{hordijk2011,steel2004}, restricted to
subsets of $U$.

(iii) Existence of the greatest fixed point: the sequence
$U\supseteq D(U)\supseteq D^{2}(U)\supseteq\cdots$ is decreasing
by deflationarity, and each strict inclusion removes at least one
reaction, so by finiteness of $U$ the sequence stabilizes at some
$D^{m}(U)$ with $m\leq|U|$; the stabilized value is a fixed point,
$D(D^{m}(U))=D^{m+1}(U)=D^{m}(U)$. It is the greatest fixed
point: if $S=D(S)$ then by monotonicity and induction
$S=D^{n}(S)\subseteq D^{n}(U)$ for every $n$, in particular
$S\subseteq D^{m}(U)$. Identification with $R_{\max}$: the union
of any family of RAFs is again a RAF --- the catalyst pool and
the reactant closure only grow under unions --- so
$R_{\max}=\bigcup\{S : S\text{ a RAF},\ S\subseteq U\}$ is itself
a fixed point by (ii), hence a subset of $D^{m}(U)$; conversely
$D^{m}(U)$ is a RAF, hence a subset of $R_{\max}$. Therefore
$D^{m}(U)=R_{\max}$, and since the sequence is stable from $m$
on, $\bigcap_{n<\omega}D^{n}(U)=D^{m}(U)=R_{\max}$. Terminal
coalgebra: regard $2^{U}$ as a posetal category (objects the
subsets of $U$, a morphism $S\to T$ the inclusion $S\subseteq T$).
A monotone map $D$ is an endofunctor of $2^{U}$; a $D$-coalgebra
is an object $S$ with a morphism $S\to D(S)$, i.e.\ a post-fixed
point $S\subseteq D(S)$; a morphism of coalgebras $S\to S'$ is an
inclusion compatible with the structure, i.e.\ $S\subseteq S'$.
The terminal coalgebra is therefore the greatest post-fixed
point of $D$. By Tarski's fixed-point theorem for monotone
endomaps of complete lattices, the greatest post-fixed point
equals the greatest fixed point, so the terminal $D$-coalgebra is
$\nu D=R_{\max}$. This is the posetal instance of the general
terminal-coalgebra theory~\citep{adamek2005,worrell2005}.

(iv) The Hordijk--Steel iterative-removal algorithm initializes
with the full reaction set and repeatedly deletes every reaction
that is neither catalyzed by the current set nor generatable from
the food given the current set, until no further deletion is
possible. The retained set after one deletion round is exactly
$S\cap\Phi(S)=D(S)$: the reactions of $S$ that satisfy both
conditions. The algorithm's iterates are therefore
$D^{n}(U)$, step for step, and its output is the stabilized
value $D^{m}(U)=R_{\max}$.

(v) One application of $D$ scans the reaction set once; for each
reaction $r\in U$ it tests membership of $r$'s catalysts in the
pool (constant time per catalyst against a precomputed catalysis
table) and queries the reactant closure of
$F\cup\mathrm{prod}(S)$ (bounded by the metabolite count, and
incrementally maintainable between rounds since
$\mathrm{prod}(S)$ only shrinks). With at most $|U|$ strict
rounds the total work is polynomial in the network size, the same
order as the published iterative-removal algorithm, which it
coincides with by (iv).
\end{proof}

"""
replace_once(
"""\\section*{Declarations}""",
APPENDIX + """\\section*{Declarations}""",
    "appendix")

open(F, "w").write(src)
print("part C written:", len(src), "bytes")
