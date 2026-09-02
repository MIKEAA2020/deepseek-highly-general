#!/usr/bin/env python3
r"""Standalone-theory-paper restructure of scripts/companion_categorical.tex,
part B: from the FBA-operational kappa_V removal through the tail
(future-directions section, extraction-record removal, key fixes).

Every edit is an asserted exact-match replacement.
"""
import io, sys

PATH = "/home/z/my-project/scripts/companion_categorical.tex"
tex = io.open(PATH, encoding="utf-8").read()

edits = []
def E(old, new, tag):
    edits.append((old, new, tag))

# ---- B0 fix cross-citation key: the companion cites the APPLICATION
#      paper, whose key is zai2026measure (3 occurrences from part A)
E(r"""An application of this framework to metabolic flux rerouting --- the
atomic curvature measure of parametric flux balance analysis and its
genome-scale empirical validation --- appears in a companion
application paper.
\par
\vspace{0.4em}
\emph{Status: standalone theory paper; an application paper
\citep{zai2026categorical} cites it for constructions and proofs.}""",
r"""An application of this framework to metabolic flux rerouting --- the
atomic curvature measure of parametric flux balance analysis and its
genome-scale empirical validation --- appears in a companion
application paper.
\par
\vspace{0.4em}
\emph{Status: standalone theory paper; the application paper
\citep{zai2026measure} cites it for constructions and proofs.}""",
"B0 abstract key")

E(r"""measure-theoretic discretization used in the application paper
\citep{zai2026categorical} replaces the $2$-form $F$ by an atomic
crease measure.""",
r"""measure-theoretic discretization used in the application paper
\citep{zai2026measure} replaces the $2$-form $F$ by an atomic
crease measure.""",
"B0b def:kv key")

E(r"""An application of this framework to metabolic flux rerouting appears
in a separate manuscript \citep{zai2026categorical}: there the""",
r"""An application of this framework to metabolic flux rerouting appears
in a separate manuscript \citep{zai2026measure}: there the""",
"B0c intro key")

# ---- B1 remove the FBA-operational indicator-weighted kappa_V block
E(r"""% =============================================================
\begin{definition}[FBA-operational viability-weighted curvature $\kappa_V$;
v10 main definition, indicator-weighted]
\label{def:ard-derived-kappa-V}
For a metabolic network with wild-type biomass flux $b_{wt}$ and a
gene-KO biomass flux $b_{KO}(g)$, the
\emph{FBA-operational viability-weighted curvature} is
\begin{equation}\label{eq:kappa-V-FBA}
  \kappa_V(g) \;\coloneqq\;
  \underbrace{\Big[\textstyle\sum_{r\in\Delta R(g)}
  (v_r(\mathrm{KO}) - v_r(\mathrm{WT}))^2\Big]}_{\kappa_V^{\mathrm{flux}}(g)}
  \;\cdot\;
  \mathbb{1}\!\left[\Delta b(g) > \tau\,b_{wt}\right],
\end{equation}
where $\Delta R(g) = \{r : |v_r(\mathrm{KO}) - v_r(\mathrm{WT})| > 10^{-6}\}$
is the set of reactions with nontrivial flux change under KO of $g$,
$\Delta b(g) = b_{wt} - b_{KO}(g)$ is the biomass deficit, and
$\tau = 0.05$ is the standard essentiality threshold
\cite{orth2011}. The indicator $\mathbb{1}[\cdot]$ zeroes
$\kappa_V$ for KOs that do NOT reduce biomass by more than $\tau\,b_{wt}$,
restricting the curvature to the sub-population of KOs that actually impact
viability.

The \emph{naive (unweighted) variant} $\kappa_V^{\mathrm{flux}}$ (without
the indicator) is retained for backward comparability with the v1--v9
elevation studies; it coincides with $\kappa_V$ on the sub-population of
in-silico-essential KOs and is bounded above by $\kappa_V$ on the rest
(since the indicator zeroes non-essential KO flux-rerouting noise). On
synthetic Stokes problems (Study E1, $V = 1 - x^2 - y^2$ on the $n=3$
prototype; $\kappa_V = a^2$ by Stokes theorem) the indicator is undefined
because there is no biomass variable; the synthetic-Stokes $\kappa_V$ is
the curvature $\kappa^{\mathrm{alg}}$ of Theorem~\textup{(v21 4.2)}, not
the FBA-operational $\kappa_V$ of this Definition.

\textbf{Empirical justification (v10, E18; v11, E19).} Promoting the
indicator-weighted variant from v9 refinement to v10 main definition
(Study E18) strengthened the two biomass-based studies whose findings were
previously the weakest under the unweighted definition: E12's calibration
$r(\log_{10}\kappa_V, \Delta b)$ jumped from $+0.370$ to $+0.938$ (factor
$2.54$); iML1515's direct correlation with raw Keio essentiality flipped
sign from $-0.018$ to $+0.466$ (the denser network's flux-rerouting noise
was producing a slightly negative correlation; the indicator mask zeroes
this noise and direction-of-effect is restored). Study E19 (v11) extended
the indicator mask to E8 (Network K ODE viability erosion): marginal
strengthening at small $\tau$ (partial $r(\kappa_V, \mathrm{erosion} \mid
\mathrm{viability\_margin})$ rose from $+0.849$ to $+0.864$ at $\tau = 0.01$;
$95\%$ CI $[+0.736, +0.949]$ vs original $[+0.713, +0.940]$), demonstrating
that the indicator-mask concept is cross-domain transferable but with
diminishing returns on ODE-level viability compared to FBA-biomass.
\end{definition}

% =============================================================
""",
r"""\begin{remark}[The operational, data-side curvature is not defined here]
\label{rem:fba-kappa-superseded}
A predecessor of this framework also carried an
\emph{FBA-operational} viability-weighted curvature: an
indicator-masked, gene-knockout flux-rerouting statistic whose
indicator imports the model's own essentiality call into the
predictor, and whose adoption was justified post hoc by the
strengthening it produced in two empirical studies. That object is
\emph{not} carried in this paper: it is superseded, in the
application paper \citep{zai2026measure}, by a measure-theoretic
sensitivity metric derived from the atomic curvature measure of
parametric FBA --- a construction whose selection-rule dependence is
exposed and audited rather than masked (tie-break robustness across
five lexicographic selection rules), and whose empirical validation
carries an explicit protein-layer null. The categorical framework of
the present paper is independent of that choice: Definition~\ref{def:kv}
is the geometric object; any faithful operationalization of it is
welcome.
\end{remark}

% =============================================================
""",
"B1 remove FBA kappa_V")

# ---- B2 Noether remark pointer
E(r"""\begin{remark}[Application to gauge invariance of $\kk$]
If the policy connection and viability margins of
Proposition~\textup{(v21 4)} are constructed from a Bregman""",
r"""\begin{remark}[Application to gauge invariance of $\kk$]
If the policy connection and viability margins of
Definition~\ref{def:kv} are constructed from a Bregman""",
"B2 noether pointer")

# ---- B3 hierarchy pointers
E(r"""\begin{definition}[Falsification hierarchy]
\label{def:hierarchy}
The viability-weighted curvature $\kk$ of
Definition~\ref{def:kappa-depth} (viability depth) and
Proposition~\textup{(v21 4)} (curvature-based $\kk$) generate
a seven-claim falsification
hierarchy on the prototype of Section~\textup{(v21 10)}. Each claim is a""",
r"""\begin{definition}[Falsification hierarchy]
\label{def:hierarchy}
The viability-weighted curvature $\kk$ of
Definition~\ref{def:kv} generates
a seven-claim falsification
hierarchy on the abelian $n=3$ prototype. Each claim is a""",
"B3 hierarchy pointers")

# ---- B4 optics-decomp pointer
E(r"""because the RPSI self-reference paradox
requires the quantum lift of Section~\textup{(v21 14)}. The $n=3$""",
r"""because the RPSI self-reference paradox
requires the quantum lift of Section~\ref{sec:lipschitz}. The $n=3$""",
"B4 optics-decomp pointer")

# ---- B5 optics-physical pointer
E(r"""existence is decoupled from definitional rhetoric and reduced to the
empirical contraction-rate question settled in
Section~\textup{(v21 15)}.""",
r"""existence is decoupled from definitional rhetoric and reduced to the
empirical contraction-rate question settled in
Section~\ref{sec:lipschitz}.""",
"B5 optics-physical pointer")

# ---- B6 thm:composition tail
E(r"""not established here; the operational fixed-point claim is instead
realized through a realization functor $R$ from endo-optics to
endomaps on a complete metric state space $S$ and proven under an
explicit Lipschitz contraction bound (Proposition~\textup{(v21 15)}).""",
r"""not established here; the operational fixed-point claim is instead
realized through the realization construction of
Definition~\ref{def:realization} --- which evaluates an endo-optic as
an endomap on a complete metric state space $S$ --- and proven under an
explicit Lipschitz contraction bound
(Theorem~\ref{thm:unconditional-banach}).""",
"B6 thm:composition tail")

# ---- B7 remark after prop:sufficient
E(r"""The full proof of the composition theorem is
contained in this article (Theorem~\ref{thm:composition} together
with the per-optic Lipschitz analysis of
Section~\ref{sec:lipschitz}); the optic decomposition table is
Table~\ref{tab:optics}, and the sufficient-condition argument is
Proposition~\textup{(v21 15)}. A separate companion treatment of
free cornerings of monoidal categories appears
in~\cite{riley2023}, but the proofs needed here are self-contained
in the present article, and the sufficient condition is confirmed
empirically in Section~\textup{(v21 15)}.""",
r"""The full proof of the composition theorem is
contained in this article (Theorem~\ref{thm:composition} together
with the per-optic Lipschitz analysis of
Section~\ref{sec:lipschitz}); the optic decomposition table is
Table~\ref{tab:optics}, and the sufficient-condition argument is
Proposition~\ref{prop:treg-lip}. A separate treatment of
free cornerings of monoidal categories appears
in~\cite{riley2023}, but the proofs needed here are self-contained
in the present article, and the sufficient condition is confirmed
numerically across the $375$-configuration robustness grid
documented in the project repository.""",
"B7 remark sufficient")

# ---- B8 rem:typed-optic
E(r"""The full functorial
construction is open and is treated as
Conjecture~\textup{(v21 21.6)}'s analogue for the
endofunctor semantics. The operational fixed-point claim---that the
realized update map $T = R(O) : S \to S$ (for a realization functor $R$
from endo-optics to endomaps on a complete metric state space $S$)
has a unique fixed point whenever $T$ is a contraction---is established
in Proposition~\textup{(v21 15)} (analytic upper bound on
$\Lip(T_{\mathrm{reg}})$) and Section~\textup{(v21 15)} (numerical
evidence across $375$ configurations).""",
r"""The full functorial
construction is open and is recorded as
the endofunctor-semantics analogue of the contraction agenda closed
in Section~\ref{sec:lipschitz}. The operational fixed-point claim---that the
realized update map $T = R(O) : S \to S$ (for the realization
construction $R$ of Definition~\ref{def:realization}, which evaluates
an endo-optic as an endomap on a complete metric state space $S$)
has a unique fixed point whenever $T$ is a contraction---is established
in Theorem~\ref{thm:unconditional-banach} (analytic upper bound on
$\Lip(T_{\mathrm{reg}})$) with numerical
evidence across $375$ configurations in the project repository.""",
"B8 rem typed-optic")

# ---- B9 sec:lipschitz intro
E(r"""Proposition~\textup{(v21 15)} gives a conditional Banach contraction:
the regularized update $T_{\mathrm{reg}}$ is contractive \emph{provided}
the per-optic product $\prod_{i=1}^{7}\Lip(f_{i})<1$. This section
removes the conditional character of the bound by giving explicit
analytic Lipschitz constants for each of the seven forward maps of
Construction~\ref{con:seven}, computing the product analytically, and
verifying numerically that the bound holds throughout the dimensional
range $d\in\{2,3,5,10,20\}$. The same machinery closes
Conjecture~\textup{(v21 21.6)} (Zeno self-reference resolution by
contraction): the projected CPTP channel""",
r"""A direct analysis gives a conditional Banach contraction:
the regularized update $T_{\mathrm{reg}}$ is contractive \emph{provided}
the per-optic product $\prod_{i=1}^{7}\Lip(f_{i})<1$. This section
removes the conditional character of the bound by giving explicit
analytic Lipschitz constants for each of the seven forward maps of
Construction~\ref{con:seven}, computing the product analytically, and
verifying numerically that the bound holds throughout the dimensional
range $d\in\{2,3,5,10,20\}$. The same machinery settles
the Zeno self-reference resolution by
contraction: the projected CPTP channel""",
"B9 lipschitz intro")

# ---- B10 insert def:realization + prop:treg-lip before the Banach thm
E(r"""\begin{theorem}[Unconditional Banach contraction of $T_{\mathrm{reg}}$]
\label{thm:unconditional-banach}
With the seven forward maps $f_{1},\ldots,f_{7}$ instantiated as in
\eqref{eq:fi-contracting}--\eqref{eq:f2-expansion} with the parameters
of Lemma~\ref{lem:lip-per-optic}, the product Lipschitz bound is
\begin{equation}\label{eq:product-lip}
  \prod_{i=1}^{7}\Lip(f_{i}) \;\leq\; 0.92^{6}\cdot 1.15
  \;=\; 0.6064\cdot 1.15 \;=\; 0.697 \;<\; 1.
\end{equation}
Consequently, by Proposition~\textup{(v21 15)}, the Bregman-regularized
update
$T_{\mathrm{reg}}(K)=(1-\lambda)\,T(K)+\lambda\,\Pi_{\mathcal K}(T(K))$
is Lipschitz with
\begin{equation}\label{eq:treg-uncond}
  \Lip(T_{\mathrm{reg}}) \;\leq\; (1-\lambda)\cdot 0.697+\lambda
  \;<\; 1
\end{equation}
for every $\lambda\in[0,1)$. The Banach fixed-point theorem applies
unconditionally: $T_{\mathrm{reg}}:X\to X$ on the complete metric space
$X=[0,1]^{d}$ (Euclidean metric, $d\in\{2,3,5,10,20\}$) has a unique
fixed point $K^{*}$, which is the unification object of
Corollary~\ref{cor:unification}.
\end{theorem}

\begin{proof}
Substitute the bounds of Lemma~\ref{lem:lip-per-optic} into the product
to obtain~\eqref{eq:product-lip}. The Bregman-regularized bound
follows from Proposition~\textup{(v21 15)}, using the $1$-Lipschitz
property of the Euclidean projection $\Pi_{\mathcal K}$ onto a closed
convex set (Moreau decomposition theorem). The Banach fixed-point
theorem~\cite{banach1922} applies on the complete metric space
$X=[0,1]^{d}$ (compact subset of $\RR^{d}$, hence complete; the
Euclidean metric is complete) because $\Lip(T_{\mathrm{reg}})<1$.
\end{proof}""",
r"""\begin{definition}[Realization of an endo-optic]
\label{def:realization}
Let $O = \sigma \circ O_n \circ \cdots \circ O_1$ be a typed
endo-optic on an interface $I_0$
(Theorem~\ref{thm:composition}), with forward components
$\mathrm{fwd}_i$ and backward components $\mathrm{bwd}_i$ acting on a
residual $\mathrm{Res}_O$. The \emph{realization} of $O$ on a
complete metric state space $S$ (e.g.\ $X=[0,1]^d$ with the Euclidean
metric) is the endomap
\begin{equation}\label{eq:realization}
  R(O) : S \to S, \qquad
  R(O)(x) \;=\; \mathrm{bwd}_1\!\bigl(\mathrm{Res}_O,\,
  \mathrm{fwd}_n \circ \cdots \circ \mathrm{fwd}_1(x)\bigr),
\end{equation}
i.e.\ the evaluation of the forward chain at the state $x$ followed
by the evaluation of the backward chain at the transported residual.
$R$ is a construction on \emph{realized} (set-level) optic data: it
assigns to each instantiated endo-optic one endomap of $S$. Whether
$R$ extends to a genuine functor on a category of typed endo-optics
is an open problem (Section~\ref{sec:future}); the fixed-point
claims of this paper use only the endomap $R(O)$, whose contraction
behavior is analyzed directly.
\end{definition}

\begin{proposition}[Lipschitz bound for the Bregman-regularized update]
\label{prop:treg-lip}
Let $T : X \to X$ be $\rho$-Lipschitz on the closed convex set
$X \subseteq \RR^d$, and let $\Pi_{\mathcal K}$ be the Euclidean
projection onto a closed convex subset $\mathcal K \subseteq X$. The
Krasnoselskii--Mann-averaged (Bregman-regularized) update
\begin{equation}\label{eq:treg-def}
  T_{\mathrm{reg}}(K) \;=\; (1-\lambda)\,T(K) +
  \lambda\,\Pi_{\mathcal K}(T(K)), \qquad \lambda \in [0,1),
\end{equation}
is Lipschitz with
\begin{equation}\label{eq:treg-lip}
  \Lip(T_{\mathrm{reg}}) \;\leq\; (1-\lambda)\,\rho + \lambda,
\end{equation}
the $\lambda$-term reflecting that $\Pi_{\mathcal K}$ is
$1$-Lipschitz but not a contraction. In particular, if $\rho < 1$
then $\Lip(T_{\mathrm{reg}}) < 1$ for every $\lambda \in [0,1)$.
\end{proposition}

\begin{proof}
For $x, y \in X$,
$\|T_{\mathrm{reg}}(x) - T_{\mathrm{reg}}(y)\| \leq
(1-\lambda)\|T(x)-T(y)\| + \lambda\|\Pi_{\mathcal K}(T(x)) -
\Pi_{\mathcal K}(T(y))\| \leq (1-\lambda)\rho\|x-y\| +
\lambda\|x-y\|$
by the triangle inequality, the $\rho$-Lipschitz property of $T$,
and the $1$-Lipschitz property of the Euclidean projection onto a
closed convex set (Moreau decomposition).
\end{proof}

\begin{theorem}[Banach contraction of $T_{\mathrm{reg}}$ for the chosen
seven-map instantiation]
\label{thm:unconditional-banach}
With the seven forward maps $f_{1},\ldots,f_{7}$ instantiated as in
\eqref{eq:fi-contracting}--\eqref{eq:f2-expansion} with the
parameters of Lemma~\ref{lem:lip-per-optic}
($\alpha_{i}=0.40$, $s_{i}=1.00$, $\rho_{i}=0.80$ for the six
contracting optics and $\lambda_{2}=1.15$ for the expansion optic),
the product Lipschitz bound is
\begin{equation}\label{eq:product-lip}
  \prod_{i=1}^{7}\Lip(f_{i}) \;\leq\; 0.92^{6}\cdot 1.15
  \;=\; 0.6064\cdot 1.15 \;=\; 0.697 \;<\; 1.
\end{equation}
The bound is uniform in the dimension $d$ (it uses only operator
norms and the $1$-Lipschitz property of $\tanh$) and is verified to
hold at the sampled dimensions $d\in\{2,3,5,10,20\}$
(Remark~\ref{rem:lip-numerical}). Consequently, by
Proposition~\ref{prop:treg-lip}, the Bregman-regularized
update~\eqref{eq:treg-def}
is Lipschitz with
\begin{equation}\label{eq:treg-uncond}
  \Lip(T_{\mathrm{reg}}) \;\leq\; (1-\lambda)\cdot 0.697+\lambda
  \;<\; 1
\end{equation}
for every $\lambda\in[0,1)$. The Banach fixed-point theorem then
applies without further hypotheses: $T_{\mathrm{reg}}:X\to X$ on the
complete metric space
$X=[0,1]^{d}$ has a unique
fixed point $K^{*}$, which is the unification object of
Corollary~\ref{cor:unification}.
\end{theorem}

\begin{proof}
Substitute the bounds of Lemma~\ref{lem:lip-per-optic} into the product
to obtain~\eqref{eq:product-lip}. The Bregman-regularized bound
follows from Proposition~\ref{prop:treg-lip}, using the $1$-Lipschitz
property of the Euclidean projection $\Pi_{\mathcal K}$ onto a closed
convex set (Moreau decomposition theorem). The Banach fixed-point
theorem~\cite{banach1922} applies on the complete metric space
$X=[0,1]^{d}$ (compact subset of $\RR^{d}$, hence complete; the
Euclidean metric is complete) because $\Lip(T_{\mathrm{reg}})<1$.
\end{proof}""",
"B10 realization+treg props")

# ---- B11 figure caption conjecture pointer
E(r"""giving the unconditional Banach contraction of
Theorem~\ref{thm:unconditional-banach} (Conjecture~\textup{(v21 21.6)}
closed for the optic-side bound).}""",
r"""giving the Banach contraction of
Theorem~\ref{thm:unconditional-banach} for the chosen instantiation
(the optic-side bound of the contraction agenda).}""",
"B11 fig lip caption")

# ---- B12 CPTP subsection + theorem + caption + remark
E(r"""\subsection{Projected CPTP channel contraction (closing Conjecture~\textup{(v21 21.6)})}

Theorem~\ref{thm:unconditional-banach} closes the optic-side Banach
argument; Conjecture~\textup{(v21 21.6)} further requires that
the projected CPTP channel $\rho\mapsto P\Phi(P\rho P)P$ be a strict
contraction in trace distance. We instantiate $\Phi$ as the""",
r"""\subsection{Projected CPTP channel contraction (Zeno self-reference
resolution)}

Theorem~\ref{thm:unconditional-banach} settles the optic-side Banach
argument; the Zeno self-reference resolution further requires that
the projected CPTP channel $\rho\mapsto P\Phi(P\rho P)P$ be a strict
contraction in trace distance. We instantiate $\Phi$ as the""",
"B12 cptp subsection")

E(r"""trace-distance metric. This closes
Conjecture~\textup{(v21 21.6)}.
\end{theorem}""",
r"""trace-distance metric. This settles the Zeno self-reference
resolution.
\end{theorem}""",
"B12b zeno thm")

E(r"""at $(n{=}2,k{=}2,p{=}0.5)$
strongly contractive ($\mu=0.667$). Conjecture~\textup{(v21 21.6)}
closed.}""",
r"""at $(n{=}2,k{=}2,p{=}0.5)$
strongly contractive ($\mu=0.667$). Zeno self-reference resolution
settled.}""",
"B12c zeno caption")

E(r"""The two results together close
Conjecture~\textup{(v21 21.6)}: the quantum predictor's
self-referential fixed-point equation $\rho^{*}=P\Phi(P\rho^{*}P)P$
admits a unique solution unconditionally (given the depolarizing
instantiation of $\Phi$), and the unification object of
Corollary~\ref{cor:unification} exists unconditionally as the fixed
point of $T_{\mathrm{reg}}$. The previous conditional language
(``provided the projected channel is a contraction'') is removed.""",
r"""The two results together settle
the Zeno self-reference resolution: the quantum predictor's
self-referential fixed-point equation $\rho^{*}=P\Phi(P\rho^{*}P)P$
admits a unique solution unconditionally (given the depolarizing
instantiation of $\Phi$), and the unification object of
Corollary~\ref{cor:unification} exists unconditionally as the fixed
point of $T_{\mathrm{reg}}$. No conditional hypothesis on the
projected channel remains.""",
"B12d two-contractions remark")

# ---- B13 con:invlim pointers
E(r"""\item residual $= D_\varphi(\mathrm{dist}_D(R), \mathrm{dist}_D(R_0))$
(the viability-kernel distance, Definition~\textup{(v21 4)}).""",
r"""\item residual $= D_\varphi(\mathrm{dist}_D(R), \mathrm{dist}_D(R_0))$
(the viability-kernel distance; Definitions~\ref{def:ard}
and~\ref{def:bregman}).""",
"B13 con:invlim residual")

E(r"""The construction is verified by direct computation on the small
network; the universal colimit existence in $\Optic(\mathbf{Set})$ for
larger networks is treated as
Conjecture~\textup{(v21 21.6)}.""",
r"""The construction is verified by direct computation on the small
network; the universal colimit existence in $\Optic(\mathbf{Set})$ for
larger networks is established componentwise below
(Theorem~\ref{thm:filtered-colimits-optic}).""",
"B13b con:invlim colimit")

# ---- B14 prop:invlim pointer
E(r"""Equivalently, the viability-weighted curvature $\kk(R_{\max})$
computed both via the filtered-colimit construction and via the
operational Proposition~\textup{(v21 4)} agrees within
machine precision ($10^{-9}$) on the present small network.""",
r"""Equivalently, the viability-weighted curvature $\kk(R_{\max})$
computed both via the filtered-colimit construction and via the
operational form of Definition~\ref{def:kv} agrees within
machine precision ($10^{-9}$) on the present small network.""",
"B14 prop:invlim")

# ---- B15 filtered-colimit subsection title + conjecture wording
E(r"""\subsection{Componentwise filtered colimits in $\Optic(\mathbf{Set})$
(closing Conjecture~\textup{(v21 21.6)})}

The filtered colimit of
Construction~\ref{con:invlim} is computed by direct enumeration on the
small Hordijk--Steel network. The general result---that
$\Optic(\mathbf{Set})$ admits filtered colimits constructed
componentwise---was stated as
Conjecture~\textup{(v21 21.6)}. We now close the
conjecture with an explicit componentwise construction.""",
r"""\subsection{Componentwise filtered colimits in $\Optic(\mathbf{Set})$}

The filtered colimit of
Construction~\ref{con:invlim} is computed by direct enumeration on the
small Hordijk--Steel network. The general result---that
$\Optic(\mathbf{Set})$ admits filtered colimits constructed
componentwise---holds, with an explicit componentwise construction.""",
"B15 colimits subsection")

# ---- B16 sec:invlim-extended intro
E(r"""This is the smallest non-trivial example that demonstrates the
directed-system axioms and the viability-preservation match at the
colimit. The future-direction item of Section~\textup{(v21 21)}
had explicitly suggested extending ``to reaction networks with
$|M|>10$ to test the viability-preservation under inverse limit at
scale.'' The present subsection closes that item with an explicit
scale-up to $|M|=13$ and $|R|=11$.""",
r"""This is the smallest non-trivial example that demonstrates the
directed-system axioms and the viability-preservation match at the
colimit. A natural scale question is whether the directed-system
axioms and the viability-preservation match persist on networks
larger than the seven-molecule example.
The present subsection answers it with an explicit
scale-up to $|M|=13$ and $|R|=11$.""",
"B16 invlim-extended intro")

# ---- B17 prop:invlim-extended items 2 and 3
E(r"""\item \emph{Inverse limit}: there is a unique maximal RAF
  $R_{\max}=\{r_1,\ldots,r_{11}\}$ with $|R_{\max}|=11$, which
  equals the union of all $16$ enumerated RAFs. The $15$ projection
  arrows $R_{\max}\to R_i$ (for $i\ne\text{limit}$) are the
  inclusions, witnessing the universal property of the limit in
  $\Optic(\mathbf{Set})$.
\item \emph{Falsifiable prediction}: $\kk(R_{\max})$ computed via the
  filtered-colimit construction (the colimit's viability-weighted
  curvature as the colimit of the per-$i$ curvatures, scaled by the
  $h_\alpha$ at $R_{\max}$) equals $\kk(R_{\max})$ computed via the
  operational Proposition~\textup{(v21 4)} form on the
  maximal RAF's Bregman-projected structure. Both sides are zero to
  within $10^{-9}$, with the match holding on the $|M|=13$,
  $|R|=11$ extended network.""",
r"""\item \emph{Filtered colimit}: there is a unique maximal RAF
  $R_{\max}=\{r_1,\ldots,r_{11}\}$ with $|R_{\max}|=11$, which
  equals the union of all $16$ enumerated RAFs. The $15$ structure
  arrows $R_i \to R_{\max}$ are the
  inclusions, witnessing the universal property of the colimit in
  $\Optic(\mathbf{Set})$.
\item \emph{Consistency check}: $\kk(R_{\max})$ computed via the
  filtered-colimit construction (the colimit's viability-weighted
  curvature as the colimit of the per-$i$ curvatures, scaled by the
  $h_\alpha$ at $R_{\max}$) equals $\kk(R_{\max})$ computed via the
  operational form of Definition~\ref{def:kv} on the
  maximal RAF's Bregman-projected structure. Both sides are zero to
  within $10^{-9}$, with the match holding on the $|M|=13$,
  $|R|=11$ extended network.""",
"B17 prop invlim-extended")

# ---- B18 interpretation paragraph + 0=0 remark
E(r"""\noindent\emph{Interpretation.} The match between the
filtered-colimit computation and the operational form on a network
roughly twice as large as the original (in both $|M|$ and $|R|$)
confirms that the inverse-limit construction's viability-preservation
property is not an artifact of the small Hordijk--Steel example. The
falsifiable prediction $\kk(R_{\max})=0$ holds at scale, and the
directed-system axioms---which fail generically for non-catalytic
reaction networks---are verified to hold for this richer, multi-branch
catalytic network.""",
r"""\begin{remark}[The vanishing is structural, not predictive]
\label{rem:zero-zero}
The equality $\kk(R_{\max})=0$ in item~3 of
Proposition~\ref{prop:invlim-extended} is a \emph{consistency check
of the implementation}, not an independent falsifiable prediction:
every RAF in the directed system is viability-preserving
\emph{by construction}, so both computed quantities vanish
structurally (as the caption of Figure~\ref{fig:hasse-extended}
states), and their agreement verifies that the colimit computation
and the operational computation implement the same object. The
falsifiable content of Proposition~\ref{prop:invlim-extended} is
instead carried by items~1 and~2: the directed-system axioms
\emph{do} fail generically for non-catalytic reaction networks, so
their survival on a multi-branch catalytic network at twice the
original scale is a genuine, refutable check of the construction.
\end{remark}

\noindent\emph{Interpretation.} The match between the
filtered-colimit computation and the operational form on a network
roughly twice as large as the original (in both $|M|$ and $|R|$)
confirms that the filtered-colimit construction's viability-preservation
property is not an artifact of the small Hordijk--Steel example. The
structural vanishing $\kk(R_{\max})=0$ holds at scale
(Remark~\ref{rem:zero-zero}), and the
directed-system axioms---which fail generically for non-catalytic
reaction networks---are verified to hold for this richer, multi-branch
catalytic network.""",
"B18 zero-zero remark")

# ---- B19 HoTT section intro
E(r"""This section closes future-direction item~3
(Section~\textup{(v21 21)}, item~3), which had been left open as
``extension of the composition theorem (Theorem~\ref{thm:composition})
to $\infty$-categorical settings and homotopy type theory.'' The
strict-fiber 1-categorical optic composition of""",
r"""This section extends the composition theorem
(Theorem~\ref{thm:composition})
to $\infty$-categorical settings and homotopy type theory. The
strict-fiber 1-categorical optic composition of""",
"B19 hott intro")

# ---- B20 Claim G pointer in HoTT setup
E(r"""channels of Claim~G (Section~\textup{(v21 14)}). The restriction to""",
r"""channels of Claim~G (Definition~\ref{def:hierarchy}). The restriction to""",
"B20 claim G pointer")

# ---- B21 insert proof-status remark after cor:hott-fixedpoint proof
E(r"""(``equivalence is equivalent to equality''), the type of contractible
$\infty$-groupoids is equivalent to the universe type $\mathcal{U}$,
providing the canonical identification. (A model-independent treatment
using the language of $\infty$-topoi and the univalent universe appears
in~\cite{cisinski2019}.)
\end{proof}""",
r"""(``equivalence is equivalent to equality''), the type of contractible
$\infty$-groupoids is equivalent to the universe type $\mathcal{U}$,
providing the canonical identification. (A model-independent treatment
using the language of $\infty$-topoi and the univalent universe appears
in~\cite{cisinski2019}.)
\end{proof}

\begin{remark}[Proof status of Theorem~\ref{thm:hott-composition} and
Corollary~\ref{cor:hott-fixedpoint}]
\label{rem:proof-status-hott}
Both proofs above are \emph{sketches}, and we mark them as such.
Specifically: (i) the symmetric monoidal structure of
$\Optic(\mathcal{C}_\infty)$ under homotopy-pullback residuals is
\emph{cited} (homotopy-coherent Mac Lane
theorem~\cite[Thm.~2.4.3]{lurie2017ha}), not constructed
--- an explicit $\infty$-categorical optic composition, with its
coherence data, is not in the literature to our knowledge and is
recorded as an open problem in Section~\ref{sec:future};
(ii) the $\infty$-categorical Yoneda step in
Corollary~\ref{cor:hott-fixedpoint}'s proof is stated informally
(the contraction hypothesis is $1$-categorical in nature, applied to
simplicial mapping spaces); and (iii) the univalence identification
is model-dependent (it assumes a univalent universe in the ambient
model). What is fully verified is the concrete instance: the
$2$-optic composition in $\mathcal{S}=\mathrm{sSet}$ whose homotopy
pullback is computed explicitly and shown contractible
(Remark~\ref{rem:hott-holim}), and the operational Phase~III test
built on the contractibility idea
(Definition~\ref{def:autopoiesis-phase3},
Remark~\ref{rem:phase3-operational}).
\end{remark}""",
"B21 hott proof status")

# ---- B22 phase3 intro pointers
E(r"""The endpoint-only closure test of Definition~\ref{def:autopoiesis} (Phase~I)
and the pathwise viability tube of Remark~\ref{rem:pathwise} (Phase~II) are
the two operational levels at which the autopoiesis closure test has been
applied in Sections~\textup{(v21 18)}--\textup{(v21 18.8)}.
The $\infty$-categorical extension of Section~\ref{sec:hott} (Theorem~\ref{thm:hott-composition}
+ Corollary~\ref{cor:hott-fixedpoint}) provides a third, strictly
weaker-than-endpoint-only closure test that formalizes the higher-categorical
recovery of components whose endpoint-only trajectory lands in a limit
cycle (as for AcCoA in Network~G, Remark~\ref{rem:netG-accola-cycle}, and
for ALA in Network~H, Proposition~\textup{(v21 18.9)}).""",
r"""The endpoint-only closure test of Definition~\ref{def:autopoiesis} (Phase~I)
and the pathwise viability tube of Remark~\ref{rem:pathwise} (Phase~II) are
the two operational levels at which the autopoiesis closure test has been
applied in the operational network benchmarks of the project repository.
The $\infty$-categorical extension of Section~\ref{sec:hott} (Theorem~\ref{thm:hott-composition}
+ Corollary~\ref{cor:hott-fixedpoint}) provides a third, strictly
weaker-than-endpoint-only closure test that formalizes the higher-categorical
recovery of components whose endpoint-only trajectory lands in a limit
cycle (as for AcCoA in the Network~G benchmark, Remark~\ref{rem:netG-accola-cycle}, and
for ALA in the Network~H benchmark).""",
"B22 phase3 intro")

# ---- B23 rem:hott-falsifiable item 2 pointer
E(r"""the $\infty$-categorical homotopy-fixed-point $T^*$ under the
inclusion $\Optic(\mathcal{C}) \hookrightarrow
\Optic(\mathcal{C}_\infty)$, to within the analytical tolerance
$\prod_i \Lip(f_i) = 0.697 < 1$ (Proposition~\textup{(v21 15)}).""",
r"""the $\infty$-categorical homotopy-fixed-point $T^*$ under the
inclusion $\Optic(\mathcal{C}) \hookrightarrow
\Optic(\mathcal{C}_\infty)$, to within the analytical tolerance
$\prod_i \Lip(f_i) = 0.697 < 1$
(Theorem~\ref{thm:unconditional-banach}).""",
"B23 falsifiable item2")

# ---- B24 "verified in the present manuscript" block
E(r"""\noindent Predictions~2 and~3 are verified in the present manuscript:

\begin{itemize}[leftmargin=*, itemsep=2pt]
\item Prediction~2 is verified numerically in Section~\textup{(v21 15)}
across the $375$-configuration robustness grid; cf.\ the analytic
per-optic Lipschitz bound of Theorem~\ref{thm:unconditional-banach}""",
r"""\noindent Predictions~2 and~3 are verified:

\begin{itemize}[leftmargin=*, itemsep=2pt]
\item Prediction~2 is verified numerically
across the $375$-configuration robustness grid (project repository);
cf.\ the analytic
per-optic Lipschitz bound of Theorem~\ref{thm:unconditional-banach}""",
"B24 verified block")

# ---- B25 implications
E(r"""\subsection{Implications}

The $\infty$-categorical extension closes the open problem stated as
future-direction item~3 (Section~\textup{(v21 21)}). The seven-fold
optic composition is now a homotopy-coherent construction, allowing
three concrete generalizations:""",
r"""\subsection{Implications}

The $\infty$-categorical extension lifts the $1$-categorical
composition theorem to the homotopy-coherent setting (with the
proof-status caveats of Remark~\ref{rem:proof-status-hott}). The
seven-fold optic composition becomes a homotopy-coherent construction,
allowing
three concrete generalizations:""",
"B25 implications")

E(r"""\item \emph{Quantum information}: the CPTP channels of Claim~G
(Section~\textup{(v21 14)}) are 1-morphisms in the $\infty$-category""",
r"""\item \emph{Quantum information}: the CPTP channels of Claim~G
(Definition~\ref{def:hierarchy}) are 1-morphisms in the $\infty$-category""",
"B25b implications claimG")

# ---- B26 netG remark opening
E(r"""\begin{remark}[AcCoA limit cycle in Network~G]
\label{rem:netG-accola-cycle}
Network~G (Section~\textup{(v21 18.8)},
Proposition~\textup{(v21 18.8)}) achieves $41/42 = 97.6\%$
causally internal under the endpoint-only closure test, with the single""",
r"""\begin{remark}[AcCoA limit cycle in the Network~G benchmark]
\label{rem:netG-accola-cycle}
Network~G --- a $42$-component catalytic maintenance network of the
project repository's benchmark series, whose full specification and
execution logs are deposited there --- achieves $41/42 = 97.6\%$
causally internal under the endpoint-only closure test, with the single""",
"B26 netG remark")

# ---- B27 insert Future Directions section after the netG remark
E(r"""The endpoint-only closure-test verdict undercounts by
one; the pathwise + univalence-corrected verdict is $42/42 = 100\%$
causally internal, recovering the full autopoiesis closure.
\end{remark}

% =============================================================


% =====================================================================
\section*{Extraction record}
\addcontentsline{toc}{section}{Extraction record}

This document was assembled by \texttt{scripts/build\_companion.py}
from the frozen v21 (\texttt{scripts/journal\_manuscript.tex}) on
2026-09-02, using the line ranges recorded in that script. The v21
source was not modified. Dangling cross-references to
non-extracted sections were resolved to textual pointers by the
same script; the resolution list is reproduced in the script's
output and in the worklog.

\bibliographystyle{plainnat}
\bibliography{journal_manuscript_refs}

\end{document}""",
r"""the endpoint-only closure-test verdict undercounts by
one; the pathwise + univalence-corrected verdict is $42/42 = 100\%$
causally internal, recovering the full autopoiesis closure.
\end{remark}

% =============================================================


% =====================================================================
\section{Future directions and open problems}\label{sec:future}

The following problems are open. Items previously listed as future
directions in the predecessor lineage and since resolved (the
$2$-categorical gluing, the piecewise-holonomy verification across
loop geometries and structure groups, the filtered-colimit
construction and its scale-up, the contraction agenda, the
$\infty$-categorical extension at sketch level) are closed in the
body of this paper and are not repeated here.

\begin{enumerate}[leftmargin=*,itemsep=3pt]
\item \emph{Closed-loop boundary term at order $\varepsilon^2$.}
Theorem~\ref{thm:stratified-holonomy} controls the residual boundary
contribution of a small closed loop at its true order
($O(\varepsilon)$, the tangential variation of the transition
function), and the abelian case exhibits an exact leading-order
cancellation. A complete expansion of the
\emph{boundary-interaction} contribution at $O(\varepsilon^2)$
(commutators of the resets with the adjacent stratum transports, and
the second-order variation of the transition function) is not
derived here; for non-abelian $G_C$ the coefficient of the
$O(\varepsilon)$ term under general matching conditions is likewise
not fully tracked.
\item \emph{Endofunctor semantics.} The full functorial construction
of the composed update on a category of periodic typed systems
$\mathsf{Sys}_7$ (object map, morphism map, identity and composition
preservation) remains open
(Remark~\ref{rem:typed-optic}); the present fixed-point claims use
only the realized endomap.
\item \emph{Filtered colimits beyond $\mathbf{Set}$.} The
componentwise construction of
Theorem~\ref{thm:filtered-colimits-optic} uses that $\mathbf{Set}$ is
locally finitely presentable: filtered colimits exist, commute with
finite limits, and are preserved by hom-functors. The extension to
general lfp monoidal categories $\CC$ --- and the identification of
the minimal hypotheses under which componentwise colimits remain
optics --- is open (Remark~\ref{rem:set-suffices}).
\item \emph{An explicit $\infty$-optic composition.} The symmetric
monoidal structure of $\Optic(\mathcal{C}_\infty)$ is cited in the
proof of Theorem~\ref{thm:hott-composition}, not constructed. An
explicit construction of $\infty$-categorical optics with its
coherence data, or a proof that no such construction exists under
the stated hypotheses, would close the most significant gap in
Section~\ref{sec:hott} (Remark~\ref{rem:proof-status-hott}).
\item \emph{Sharpening the contraction bound.} The analytic bound
$\prod_i \Lip(f_i) \leq 0.697$ is sufficient but not tight: the
measured contraction factors of the Bregman-regularized iteration
across the $375$-configuration grid are systematically smaller
(the regularization reorganizes trajectories toward the interior of
$\mathcal K$ rather than merely averaging them). Recovering the
empirical rates analytically is open.
\item \emph{Operational instantiations of $\kk$.}
Definition~\ref{def:kv} is geometric; the application paper
\citep{zai2026measure} instantiates the idea measure-theoretically
on parametric FBA. Other faithful operationalizations --- ODE-level
viability models, control benchmarks, experimentally measured
channels --- would test the framework's reach; each should carry the
selection-rule robustness audit that the application paper
introduces.
\item \emph{Benchmarks for the closure test.} The three-phase
autopoiesis closure test (Definition~\ref{def:autopoiesis-phase3})
has been exercised on a series of designed catalytic maintenance
networks deposited in the project repository. Calibration on
benchmarks \emph{not} designed by the framework's authors --- and a
theoretical account of when Phase~III's contractibility criterion is
strictly weaker than Phase~I in a way that matters --- is open.
\end{enumerate}

\bibliographystyle{plainnat}
\bibliography{journal_manuscript_refs}

\end{document}""",
"B27 future directions + drop extraction record")

# ---- B28 remove [v21 extract] comments
for name in ["prelim", "savgs", "noether", "hierarchy", "composition",
             "lipschitz", "invlim", "hott"]:
    # NOTE: do not use %-formatting here -- "%%" would escape to a single
    # "%" and leave a stray comment char on the following \section line.
    E("%% ================ [v21 extract: " + name + "] ================\n",
      "", "B28 comment " + name)

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
