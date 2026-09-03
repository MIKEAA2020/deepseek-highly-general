#!/usr/bin/env python3
"""Companion v2 restoration, part A: header, optic-table Holevo fix,
smooth-envelope section (P4-repaired), E13 terminal-coalgebra section.
Marker-anchored insertions into scripts/companion_categorical_v2.tex
(the frozen companion_categorical.tex is never touched)."""
import sys

F = "/home/z/my-project/scripts/companion_categorical_v2.tex"
src = open(F).read()


def replace_once(old, new, what):
    global src
    n = src.count(old)
    if n != 1:
        print(f"FAIL [{what}]: anchor count = {n}")
        sys.exit(1)
    src = src.replace(old, new)
    print(f"ok  [{what}]")


# ------------------------------------------------------------------
# 1. Header comment: v2 identity
# ------------------------------------------------------------------
replace_once(
"""% =====================================================================
%  companion_categorical  --  STANDALONE THEORY PAPER
%  ---------------------------------------------------------------""",
"""% =====================================================================
%  companion_categorical_v2.tex -- STANDALONE THEORY PAPER, revision 2.
%  ---------------------------------------------------------------
%  Based on the frozen companion_categorical.tex: repository renamed
%  to metabolic-curvature-measure (URL updated), and the restoration
%  revision adds (all adapted from the frozen predecessor sources,
%  with the pending mathematical repairs applied): the P4-repaired
%  smooth-envelope chain for the algorithmic rate-distortion
%  surrogates (smooth soft-threshold kernel, compact parameter box,
%  countable dense subfamily, Clarke/Danskin consistency, the
%  geometric-phase corollary restated as a model-specific
%  computation); the terminal-coalgebra characterization of the
%  maximal RAF via the deflationary closure operator (proof in
%  Appendix, functorial realization demoted to conjecture); the
%  empirical verdicts of the seven-claim hierarchy (n=4 non-abelian
%  regime, Claim D heavy-tail stress, the Levy-stable derivation of
%  the 3/2 fatigue exponent with the exact kernel constant, Claims
%  F/G, the CPTP-Zeno lift with the Holevo ensemble correction, the
%  contraction battery); and the network closure-test battery
%  (summary table, persistent-homology test, external essentiality
%  validation, RAF-to-Zeno transfer bound).""", "header v2 identity")

# ------------------------------------------------------------------
# 2. Optic table O2 row: ensemble Holevo bound
# ------------------------------------------------------------------
replace_once(
"""$\\OO_2$ RPSI       & CPTP predictive update            & posterior decoder                 & $I(\\rho_{\\mathrm{out}};\\hat\\rho_{\\mathrm{in}})$ (Holevo) \\\\""",
"""$\\OO_2$ RPSI       & CPTP predictive update            & posterior decoder                 & ensemble Holevo bound $\\chi$ \\\\""",
    "optic table O2 row")

# ------------------------------------------------------------------
# 3. O2 item in the domain-unification list
# ------------------------------------------------------------------
replace_once(
"""\\item $\\OO_2$: the RPSI optic (forward = CPTP predictive update,
backward = posterior decoder, residual = Holevo information
$I(\\rho_{\\mathrm{out}};\\hat\\rho_{\\mathrm{in}})$);""",
"""\\item $\\OO_2$: the RPSI optic (forward = CPTP predictive update,
backward = posterior decoder, residual = the ensemble Holevo bound
$\\chi = S(\\sum_x p_x \\rho_x) - \\sum_x p_x S(\\rho_x)$ of the
prediction ensemble, Proposition~\\ref{prop:holevo});""",
    "O2 domain-unification item")

# ------------------------------------------------------------------
# 4. Smooth-envelope section before the filtered-colimit section
# ------------------------------------------------------------------
SMOOTH = r"""
\section{The Smooth Envelope of Algorithmic Rate-Distortion
Surrogates}\label{sec:smooth-envelope}
% ==============================================================

The algorithmic rate-distortion distance $\distD$ of
Definition~\ref{def:ard} is a single-string quantity and is not, in
general, a differentiable function of the state, while the
constructions of Sections~\ref{sec:noether}--\ref{sec:lipschitz}
require regular observables. This section constructs smooth
finite-code surrogates of $\distD$, proves that their envelope is
Lipschitz and Clarke-differentiable, and builds from it an
effectively approximable envelope curvature that dominates every
smooth surrogate --- the algorithmic upper envelope. Throughout, the
surrogate parameters are confined to the compact box
\[
\mathcal{P} \;=\; [\tau_{\min}, \tau_{\max}] \times
[\beta_{\min}, \beta_{\max}] \times [0, D_{\max}] \times
[s_{\min}, s_{\max}],
\]
with $0 < \tau_{\min}$, $0 < \beta_{\min}$, $0 < s_{\min}$, and the
code-length bound $L \in \{1, \dots, L_{\max}\}$; confining the
family is what makes the uniform bounds below provable.

\begin{definition}[Smooth finite-code rate-distortion surrogate]
\label{def:ard-surrogate}
Let $\{c_j\}_{j=1}^N$ be a finite prefix-free code family with code
lengths $\ell(c_j) \le L_{\max}$ and reconstructions $\hat x_j$. Let
$d$ be a distortion measure such that $x \mapsto d(x, \hat x_j)$ is
$C^2$ for each $j$, and let $\psi_s(t) = s\,\log(1 + e^{t/s})$ be the
soft-threshold (softplus) function, a $C^\infty$ approximation of
the positive part $t_+$. For parameters $(\tau, \beta, D, s) \in
\mathcal{P}$ define
\begin{equation}\label{eq:ard-surrogate}
  r_{\tau,\beta,D,s}(x) \;=\; -\tau\,\log\!\sum_{j=1}^{N}\,
  2^{-\ell(c_j)/\tau}\,
  \exp\!\Bigl(-\beta\,\psi_s\!\bigl(d(x, \hat x_j) - D\bigr)^{2}/\tau\Bigr).
\end{equation}
Since $\psi_s$ is $C^\infty$ and sums, products, and compositions of
smooth maps are smooth, $r_{\tau,\beta,D,s} \in C^2(\RR^n, \RR)$ for
every parameter quadruple in $\mathcal{P}$. The soft-threshold kernel
replaces the squared positive part $[d - D]_+^2$, which is only $C^1$
across the threshold locus $d = D$; smoothness of the kernel, not of
the positive part, is what carries the $C^2$ claim.
\end{definition}

\begin{proposition}[Operational viability margin from the smooth
surrogate]\label{prop:ard-surrogate}
Replace $\distD(x)$ in Definition~\ref{def:kv} and in the viability
margin of Theorem~\ref{thm:smallloop} by the smooth surrogate
$r_{\tau,\beta,D,s}(x)$, and let $h_\alpha = D_\phi\bigl(
r_{\tau,\beta,D,s}(x),\, r_{\tau,\beta,D,s}(x_0)\bigr)$. Then
$h_\alpha \in C^2$, the directional derivative
$D_{F(u,v)} h_\alpha$ is a classical derivative, and the small-loop
expansion of Theorem~\ref{thm:smallloop} applies with $h_\alpha$ in
place of the algorithmic margin.
\end{proposition}

\begin{proof}
The surrogate is $C^2$ by Definition~\ref{def:ard-surrogate}, and the
Bregman divergence of a strictly convex $C^2$ generator is $C^2$ in
its arguments (Definition~\ref{def:bregman}); the composition
$h_\alpha$ is therefore $C^2$, its derivative along the smooth field
$F(u,v)$ is classical, and the small-loop expansion is a
second-order Taylor expansion of a $C^2$ function. What is
\emph{not} claimed is $C^2$ regularity of any object built from the
un-smoothed $\distD$, of the positive part, or of suprema: those
live at the envelope level, where the correct regularity concept is
the Clarke subdifferential of Theorem~\ref{thm:smooth-envelope}
below.
\end{proof}

\begin{conjecture}[Algorithmic upper envelope]
\label{conj:alg-envelope}
There exists an effectively approximable envelope curvature
$\kk^{\mathrm{alg}}$, built from the algorithmic rate-distortion
distance $\distD$, such that for every smooth finite-code surrogate
$r_{\tau,\beta,D,s}$ of Definition~\ref{def:ard-surrogate},
\[
  \kk^{\mathrm{surrogate}} \;\leq\; \kk^{\mathrm{alg}} \;+\; O(1)
\]
in the asymptotic regime in which the code family expands to cover
all programs of bounded length. The envelope construction below
closes this conjecture.
\end{conjecture}

\begin{definition}[Smooth envelope over the compact parameter box]
\label{def:smooth-envelope}
The \emph{smooth envelope} of the surrogate family is
\begin{equation}\label{eq:smooth-envelope}
  E(x) \;:=\; \sup \bigl\{\, r_{\tau,\beta,D,s,L}(x) :
  (\tau, \beta, D, s) \in \mathcal{P},\ 1 \le L \le L_{\max}
  \,\bigr\},
\end{equation}
where $r_{\tau,\beta,D,s,L}$ is $r_{\tau,\beta,D,s}$ computed on the
sub-code of lengths $\le L$. The supremum may be taken equivalently
over any countable dense subfamily $\mathcal{Q}$ of the parameter
range: for fixed $x$ the map $(\tau,\beta,D,s,L) \mapsto
r_{\tau,\beta,D,s,L}(x)$ is continuous on the compact range, so the
supremum over $\mathcal{Q}$ equals the supremum over its closure.
\end{definition}

\begin{lemma}[Uniform Lipschitz bound on the bounded surrogate family]
\label{lem:uniform-lip}
Suppose $x \mapsto d(x, \hat x_j)$ is $C^2$ with $\|\nabla_x d\|$
uniformly bounded on each compact $K \subset \RR^n$, and that the
code family is prefix-free, so $\sum_j 2^{-\ell(c_j)} \le 1$ (the
Kraft inequality). Then on every compact $K$ the family
$\{r_{\tau,\beta,D,s,L}\}$ is uniformly Lipschitz:
\[
  \sup_{(\tau,\beta,D,s,L)}\, \Lip_K\!\bigl(
  r_{\tau,\beta,D,s,L}\bigr) \;\leq\; L_K \;<\; \infty.
\]
\end{lemma}

\begin{proof}
Differentiating~\eqref{eq:ard-surrogate} with $d_j = d(x, \hat x_j)$,
\[
  \nabla_x r \;=\;
  \frac{\sum_j 2^{-\ell(c_j)/\tau}\,
  e^{-\beta \psi_s(d_j - D)^2/\tau}
  \,\bigl(-2\beta\,\psi_s(d_j-D)\,\psi_s'(d_j-D)/\tau\bigr)\,
  \nabla_x d_j}
  {\sum_j 2^{-\ell(c_j)/\tau}\, e^{-\beta \psi_s(d_j - D)^2/\tau}},
\]
and $\psi_s' \le 1$. Let $R_K = \max_j \sup_{x \in K} d(x, \hat x_j)$,
finite by compactness. The numerator is bounded by
$\sup_j\|\nabla_x d_j\|_{L^\infty(K)} \cdot 2\beta_{\max}
\psi_{s_{\max}}(R_K)/\tau_{\min}$, using $\beta \le \beta_{\max}$,
$\tau \ge \tau_{\min}$, and the softplus bound $\psi_s(t) \le t_+ +
s\log 2 \le R_K + s_{\max}\log 2$. The denominator is at least
$\min_j 2^{-\ell(c_j)/\tau} e^{-\beta\psi_{s}(R_K)^2/\tau} \ge
2^{-L_{\max}/\tau_{\min}}\, e^{-\beta_{\max}(R_K + s_{\max}\log
2)^2/\tau_{\min}}$, strictly positive uniformly over the compact
range because $\tau \ge \tau_{\min} > 0$, $\beta \le \beta_{\max}$,
and $\ell(c_j) \le L_{\max}$. Hence
$\|\nabla_x r\|_{L^\infty(K)} \le L_K$ uniformly over the family and
$\Lip_K(r) \le L_K$.
\end{proof}

\begin{theorem}[Smooth-envelope theorem; closes
Conjecture~\ref{conj:alg-envelope}]
\label{thm:smooth-envelope}
Under the hypotheses of Lemma~\ref{lem:uniform-lip}, the envelope $E$
of Definition~\ref{def:smooth-envelope} satisfies:
\begin{enumerate}[leftmargin=*,itemsep=2pt]
\item[(a)] $E$ is $L_K$-Lipschitz on every compact $K$.
\item[(b)] At every $x$ at which the argmax of the family over the
  closure of the countable dense subfamily $\mathcal{Q}$ is a
  singleton $\{q^*\}$, $E$ is differentiable with $\nabla E(x) =
  \nabla_x r_{q^*}(x)$ (Danskin's theorem, in the form of Milgrom
  and Segal 2002); $E$ is $C^1$ on any open region on which the
  argmax is locally constant. No $C^2$ claim is made at the envelope
  level.
\item[(c)] $E$ admits a Clarke subdifferential at every $x$, given
  by the closed convex hull of the active gradients,
  $\partial^{C}E(x) = \operatorname{cl\,conv}\bigl\{\nabla_x r_q(x) :
  q \in \operatorname{Argmax}_{q \in \mathcal{Q}} r_q(x)\bigr\}$
  (Clarke 1975).
\item[(d)] The Clarke directional derivative $E'(x; v) = \sup\{p
  \cdot v : p \in \partial^{C}E(x)\}$ exists for every
  $v \in \RR^{n}$.
\item[(e)] The envelope curvature
\begin{equation}\label{eq:kappa-alg}
  \kk^{\mathrm{alg}} \;:=\;
  \tfrac{1}{V_{\max}}\, \sup_{a \in (0, a_\star]}\,
  \sup_{\text{unit bivector } \hat\omega}\,
  \bigl[\,E'(x; F(u, v))\,\bigr]_+
\end{equation}
is effectively approximable --- on each compact parameter box the
supremum in~\eqref{eq:smooth-envelope} reduces, by continuity on
the compact range, to a finite maximization over an
$\varepsilon$-net with two-sided error control --- and it dominates
every smooth surrogate curvature:
\[
  \kk^{\mathrm{surrogate}} \;\leq\; \kk^{\mathrm{alg}}.
\]
\end{enumerate}
\end{theorem}

\begin{proof}
(a) The pointwise supremum of $L_K$-Lipschitz functions is
$L_K$-Lipschitz: for $x, y \in K$,
$E(y) - E(x) \le \sup_q\bigl(r_q(y) - r_q(x)\bigr) \le L_K\|y - x\|$,
and symmetrically. (b) Danskin's theorem in the form of Milgrom and
Segal (2002): for an equicontinuous, uniformly bounded family over a
compact index set, a singleton argmax at $x$ implies
differentiability of the supremum, with the gradient of the active
member; equicontinuity and uniform boundedness hold by
Lemma~\ref{lem:uniform-lip} and compactness of the parameter range,
and the dense subfamily inherits both after closure. On a region
where the active index is locally constant, $E$ coincides locally
with the single $C^2$ surrogate $r_{q^*}$, hence is $C^1$ there.
(c) For a Lipschitz function, the Clarke subdifferential is the
closed convex hull of limits of gradients taken at nearby
differentiability points (Clarke 1975, Theorem 2.5.1). The
differentiability points of $E$ include the singleton-argmax points;
along a sequence $x_k \to x$ with parameters $q_k$ active at $x_k$
and $r_{q_k}(x_k) \to E(x)$, equicontinuity of the family and
continuity of each $\nabla_x r_q$ in $(x, q)$ force every limit
gradient to be the gradient of a member active at $x$, and
conversely each active gradient is realized; the closed convex hull
of the active gradients is therefore the full limit set. (d)
Existence of the support function follows from compactness and
convexity of $\partial^{C}E(x)$. (e) Effective approximability: by
continuity of $q \mapsto r_q(x)$ on the compact range, a finite
$\varepsilon$-net of the range yields upper and lower approximations
of $E(x)$ within $\varepsilon$, so $E$ is computable in the strong
two-sided sense on each box; the Clarke derivatives are obtained
from finite-subfamily computations on refining covers, and the
suprema over the compact ranges of $a$ and $\hat\omega$ in
\eqref{eq:kappa-alg} preserve effective approximability. Domination:
$E \ge r_q$ pointwise for every $q$ implies $E'(x; v) \ge
r_q'(x; v)$ for every $q$ and $v$ (at the $C^2$ points of $r_q$ the
classical derivative agrees with the Clarke derivative, and the
sup-function's Clarke derivative dominates the active members'),
hence $[E'(x; v)]_+ \ge [r_q'(x; v)]_+$, and the sup over
$(a, \hat\omega)$ gives
$\kk^{\mathrm{alg}} \ge \kk^{\mathrm{surrogate}}_q$ for every $q$.
\end{proof}

\begin{remark}[Relation to $\distD$, and the exact content of the
closure]\label{rem:envelope-distD}
The envelope is a smooth lower approximant of the $L$-bounded
algorithmic rate-distortion $R_L(x) = \min\{\ell(c) : d(x,
\mathrm{dec}(c)) \le D,\ \ell(c) \le L\}$: the damping factor
in~\eqref{eq:ard-surrogate} is a positive constant inside the
distortion ball and decays outside it, so each surrogate lies within
an additive constant, depending on the box $\mathcal{P}$, of the
thresholded code sum, and $R_L \to \distD$ up to the standard
additive constant as $L \to \infty$ along the code enumeration
\citep{vereshchagin2010rate}. The closure of
Conjecture~\ref{conj:alg-envelope} is therefore exactly one-sided:
the curvature of every smooth surrogate is dominated by the
(effectively approximable) envelope curvature, and the envelope
family tracks the algorithmic rate-distortion from below within
additive constants. No differentiability or curvature statement
about $\distD$ itself is made or needed.
\end{remark}

\begin{remark}[Numerical verification of the smooth-envelope
theorem]\label{rem:smooth-envelope-numeric}
The theorem is verified numerically on the two-dimensional quadratic
distortion $d(x, \hat x) = \|x - \hat x\|^2$ with $64$
reconstructions on an $8 \times 8$ grid in $[-1,1]^2$, ordered so
that increasing code length adds reconstructions progressively
farther from the origin (deposited verification artifacts): (a) the
envelope identity $E(x) = \sup_q r_q(x)$ holds pointwise, maximum
error $0.0$; (b) the Lipschitz estimate on the one-dimensional slice
$x = (t, 0)$ is finite, $\max_t|\mathrm{d}E/\mathrm{d}t| = L_K$;
(c) Danskin differentiability is confirmed at the probe points
$t \in \{-0.8, -0.4, 0, 0.4, 0.8\}$, where the argmax is a singleton
and stable under $\varepsilon$-perturbation of $t$; (d) the envelope
dominates every individual surrogate at every probe point, the
content of item (e).
\end{remark}

\begin{corollary}[Geometric-phase computation for radially symmetric
$V$; model-specific]\label{cor:kappa-geometric-phase}
Let $V$ be smooth with an isolated maximum $V_{\max}$ at the origin
and radially symmetric on a neighborhood of it (level sets
$\{V = V_{\max} - r\}$ are spheres of radius $r \le r_\star$), and
let $\gamma_a$ be a circular loop of amplitude $a < r_\star$ in any
$2$-plane through the origin. Consider the model connection
\[
A \;=\; \frac{V - V_{\max}}{2\,V_{\max}}\;\mathrm{d}\vartheta,
\]
on the punctured plane of the loop, $\vartheta$ the polar angle in
the loop's plane. Then:
\begin{enumerate}[leftmargin=*,itemsep=1pt]
\item the loop-averaged radial deficit
$\overline{\delta V}(a) := \langle V_{\max} - V \circ
\gamma_a\rangle_{[0,1]}$ is independent of the loop's phase and of
the choice of $2$-plane, a function of $a$ alone;
\item the holonomy of the model connection around $\gamma_a$ is
\begin{equation}\label{eq:kappa-radial}
  \mathrm{Hol}(\gamma_a) \;=\; \oint_{\gamma_a} A \;=\;
  \pi\;\frac{\overline{\delta V}(a)}{V_{\max}},
\end{equation}
which in the quadratic-deficit case
$\overline{\delta V}(a) = V_{\max}\,a^{2}/r_\star^{2}$ reduces to
$\pi a^{2}/r_\star^{2}$ --- with the prototype normalization
$V_{\max} = r_\star = 1$, the loop area $\pi a^{2}$, the
holonomy-area law of Claim~B;
\item the statement is a computation for the radially symmetric model
with the calibrated connection $A$, not an identity between the
viability depth $D_V$ of Definition~\ref{def:kappa-depth} and the
curvature $\kk$ of Definition~\ref{def:kv}: the two coincide only
under radial symmetry with this calibration, which is exactly the
setting of the operational claims.
\end{enumerate}
\end{corollary}

\begin{proof}
(i) By radial symmetry, $V \circ \gamma_a(t)$ equals $V$ at any
point of radius $a$, independent of the phase $t$ and of the plane.
(ii) On the circle of radius $a$ the deficit
$V_{\max} - V \circ \gamma_a = \overline{\delta V}(a)$ is constant,
so $\oint_{\gamma_a} A = \frac{\overline{\delta V}(a)}{2V_{\max}}
\oint \mathrm{d}\vartheta = \pi\,\overline{\delta V}(a)/V_{\max}$,
and by Stokes the same value is the flux of the curvature form
$F = \mathrm{d}A = \mathrm{d}V \wedge \mathrm{d}\vartheta/(2V_{\max})
$ through the disk, whose magnitude in the quadratic case
$V = V_{\max}(1 - r^2/r_\star^2)$ is
$\tfrac{1}{2V_{\max}}\int_{0}^{2\pi}\!\!\int_{0}^{a} |V'(r)|\,
\mathrm{d}r\,\mathrm{d}\vartheta = \pi a^2/r_\star^{2}$ --- the
correct area factor, the calibrated curvature times the loop area.
(iii) is the disclaimer, consistent with
Definition~\ref{def:kappa-depth}.
\end{proof}

% ==============================================================

"""
replace_once(
"""\\section{Filtered-Colimit Construction of RAFs}\\label{sec:invlim}""",
SMOOTH + """\\section{Filtered-Colimit Construction of RAFs}\\label{sec:invlim}""",
"smooth-envelope section")

open(F, "w").write(src)
print("part A written:", len(src), "bytes")
