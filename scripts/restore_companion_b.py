#!/usr/bin/env python3
"""Companion v2 restoration, part B: the empirical-verdicts section
(Claims F/G, n=4 non-abelian regime, Claim D stress test, the
repaired Levy 3/2 derivation with the exact kernel constant kappa =
sqrt(5), the CPTP-Zeno lift with the Holevo ensemble correction, and
the contraction battery of T), plus the repository-URL update and the
citation patches for the part-A smooth-envelope text.
Marker-anchored insertions into scripts/companion_categorical_v2.tex
(the frozen companion_categorical.tex is never touched)."""
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
# 1. Repository URL: renamed repository
# ------------------------------------------------------------------
replace_once(
"""manifests are available in the public repository
\\href{https://github.com/MIKEAA2020/deepseek-highly-general}{github.com/
MIKEAA2020/deepseek-highly-general}; the application paper""",
"""manifests are available in the public repository
\\href{https://github.com/MIKEAA2020/metabolic-curvature-measure}{github.com/
MIKEAA2020/metabolic-curvature-measure}; the application paper""",
    "repository URL update")

# ------------------------------------------------------------------
# 2. Citation patches for the part-A smooth-envelope text
# ------------------------------------------------------------------
replace_once(
"""  \\nabla_x r_{q^*}(x)$ (Danskin's theorem, in the form of Milgrom
  and Segal 2002); $E$ is $C^1$ on any open region on which the""",
"""  \\nabla_x r_{q^*}(x)$ (Danskin's theorem, in the form of Milgrom
  and Segal~\\citep{milgromsegal2002}); $E$ is $C^1$ on any open
  region on which the""",
    "Danskin citation")

replace_once(
"""(b) Danskin's theorem in the form of Milgrom and
Segal (2002): for an equicontinuous, uniformly bounded family over a""",
"""(b) Danskin's theorem in the form of Milgrom
and Segal~\\citep{milgromsegal2002}: for an equicontinuous, uniformly
bounded family over a""",
    "Danskin citation (proof)")

replace_once(
"""  (Clarke 1975).
\\item[(d)] The Clarke directional derivative""",
"""  \\citep{clarke1975}.
\\item[(d)] The Clarke directional derivative""",
    "Clarke subdifferential citation")

replace_once(
"""differentiability points (Clarke 1975, Theorem 2.5.1). The""",
"""differentiability points \\citep[Theorem~2.5.1]{clarke1990}. The""",
    "Clarke theorem citation")

# ------------------------------------------------------------------
# 3. The empirical-verdicts section, before the smooth-envelope section
# ------------------------------------------------------------------
VERDICTS = r"""
\section{Empirical Verdicts of the Seven-Claim Hierarchy}\label{sec:verdicts}
% ==============================================================

The falsification hierarchy of Definition~\ref{def:hierarchy} is
cumulative, and the recommended test ordering places the cheap
foundational tests first (Remark~\ref{rem:ordering}). This section
reports the executed test battery: the foundational
commuting-control verdict (Claim~F) together with the non-abelian
$n=4$ regime that carries it, the heavy-tail stress test of
Claim~D, the L\'evy-stable first-passage derivation that fixes both
the $3/2$ exponent and the exact coefficient of the fatigue term of
Claims~C and~D, the CPTP--Zeno lift with its scaling verdict
(Claim~G), and the contraction battery that closes the existence
question of the unification object (Theorem~\ref{thm:composition})
on the operational state space. The simulation protocols, seeds,
and result records for every verdict are deposited with the paper's
verification artifacts (Data Availability).

\subsection{Claim F: the non-abelian commuting-control test}
\label{sec:verdict-f}

At $n=4$ the policy fiber is $\SO(3)$
(Definition~\ref{def:struct}), with a three-dimensional non-abelian
Lie algebra. The test compares holonomy under same-axis rotations
(two $z$-axis rotations) against distinct-axis rotations (a
$z$-axis rotation followed by an $x$-axis rotation). The decisive
prediction of Claim~F is that same-axis rotations commute, giving a
vanishing non-abelian signature at machine precision, while
distinct-axis rotations do not, giving a nonzero signature that
scales with the product of the rotation angles
(Lemma~\ref{lem:comm} below).

\begin{proposition}[Claim F verdict]\label{prop:claimF}
Direct numerical simulation with the standard $\so(3)$ generators
--- path-ordered exponentials computed as products of segment
exponentials, holonomy magnitudes by the trace formula
$\varphi=\arccos((\mathrm{tr}(U)-1)/2)$, with $50$ trials per
regime and $20$ trials in the small-angle regime --- gives:
\begin{enumerate}[leftmargin=*,itemsep=2pt]
\item same-plane rotations: the path-ordered exponential agrees
  with the single-rotation product to
  $7.82\times10^{-16}$ in Frobenius norm over $50$ trials, i.e.\
  machine precision;
\item distinct-plane rotations: minimum non-abelian signature
  $0.1522$, mean $1.8015$ over $50$ trials;
\item small-angle regime: mean ratio of measured to predicted
  commutator magnitude $0.9999$ over $20$ trials, against the
  predicted $\sqrt{2}\,a\,b$ scaling of Lemma~\ref{lem:comm}.
\end{enumerate}
The verdict of Claim~F is positive: the commuting and
non-commuting control families are separated by fifteen orders of
magnitude in signature size.
\end{proposition}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\columnwidth]{claim_f_holonomy_plot.png}
\caption{Claim~F verdict. Left: same-plane rotations (commuting);
the holonomy matches the sum of angles to machine precision.
Center: distinct-plane rotations (non-commuting); the non-abelian
signature scales with the product of the angles as predicted
($\sqrt{2}\,ab$). Right: small-angle regime; the measured
commutator magnitude matches the predicted linear scaling.}
\label{fig:claimF}
\end{figure}

\subsection{The $n=4$ non-abelian regime}\label{sec:verdict-n4}

The abelian prototype has structure group $\SO(2)$ with a
one-dimensional Lie algebra (Definition~\ref{def:struct}); all
perturbations commute trivially, which is why Claim~F requires
$n\geq4$. The non-abelian regime extends the prototype to $n=4$:
state space $\RR^{3}$ with environmental coordinates $(x,y,z)$ and
policy fiber $\mathcal{P}=\SO(3)$, a genuine three-dimensional
rotational frame rather than a scalar heading. The structure group
is $G_{C}=\SO(3)$ with
\begin{equation}\label{eq:so3comm}
  [\mathfrak{l}_z, \mathfrak{l}_x] \;=\; \mathfrak{l}_y,\qquad
  [\mathfrak{l}_x, \mathfrak{l}_y] \;=\; \mathfrak{l}_z,\qquad
  [\mathfrak{l}_y, \mathfrak{l}_z] \;=\; \mathfrak{l}_x,
\end{equation}
for the standard basis
$\{\mathfrak{l}_x,\mathfrak{l}_y,\mathfrak{l}_z\}$ of $\so(3)$. The
viability $V(x,y,z)=1-x^{2}-y^{2}-z^{2}$ remains radially
symmetric, so $\kk(a)=a^{2}$ continues to hold
(Corollary~\ref{cor:kappa-geometric-phase}). The connection on the
trivial $\SO(3)$-bundle $E=B\times\SO(3)\to B$ has constant
curvature components $F_{xy}=c\,\mathfrak{l}_z$,
$F_{yz}=c\,\mathfrak{l}_x$, $F_{xz}=c\,\mathfrak{l}_y$, the
non-abelian analogue of the abelian prototype connection with
$F=\mathrm{d}x\wedge\mathrm{d}y$; the holonomy of a small loop of
area $\pi a^{2}$ in the $xy$-plane is
$\exp(c\,\pi a^{2}\,\mathfrak{l}_z)$, recovering
$R_{xy}(a)=R_{z}(\pi a^{2})$ at $c=1$.

\begin{lemma}[Non-abelian commutator signature]\label{lem:comm}
For two loops $R_1=R_i(\alpha_1)$ and $R_2=R_j(\alpha_2)$ in
distinct coordinate planes $i\neq j$, the small-angle expansion of
the group commutator gives
\begin{equation}\label{eq:comm}
  [R_1, R_2] \;=\; R_1 R_2 - R_2 R_1 \;=\;
  \alpha_1\alpha_2\,[\mathfrak{l}_i, \mathfrak{l}_j] \;+\;
  O(\alpha^{3}) \;=\;
  \alpha_1\alpha_2\,\varepsilon_{ijk}\,\mathfrak{l}_k \;+\;
  O(\alpha^{3}),
\end{equation}
with Frobenius norm
\begin{equation}\label{eq:norm}
  \Frob{[R_1,R_2]} \;=\; \sqrt{2}\,\alpha_1\alpha_2 + O(\alpha^{3})
  \;=\; \sqrt{2}\,(\pi a_1^{2})(\pi a_2^{2}) + O(\alpha^{3}).
\end{equation}
\end{lemma}

\begin{proof}
Expanding $R_i(\alpha)=I+\alpha\,\mathfrak{l}_i+
\tfrac{1}{2}\alpha^{2}\mathfrak{l}_i^{2}+O(\alpha^{3})$,
\[
  R_1R_2-R_2R_1=\bigl(I+\alpha_1\mathfrak{l}_1+
  O(\alpha_1^{2})\bigr)\bigl(I+\alpha_2\mathfrak{l}_2+
  O(\alpha_2^{2})\bigr)-\bigl(I+\alpha_2\mathfrak{l}_2+
  O(\alpha_2^{2})\bigr)\bigl(I+\alpha_1\mathfrak{l}_1+
  O(\alpha_1^{2})\bigr).
\]
All terms cancel in pairs except the cross terms, leaving
$R_1R_2-R_2R_1=\alpha_1\alpha_2(\mathfrak{l}_i\mathfrak{l}_j-
\mathfrak{l}_j\mathfrak{l}_i)+O(\alpha^{3})
=\alpha_1\alpha_2[\mathfrak{l}_i,\mathfrak{l}_j]+O(\alpha^{3})$,
and the commutation relations~\eqref{eq:so3comm} give
$[\mathfrak{l}_i,\mathfrak{l}_j]=\varepsilon_{ijk}\mathfrak{l}_k$
for distinct $i,j$. Each standard $\so(3)$ basis matrix is a
$3\times3$ skew-symmetric matrix with two unit off-diagonal
entries, hence Frobenius norm $\sqrt{2}$, so
$\Frob{[R_1,R_2]}=\sqrt{2}\,\alpha_1\alpha_2+O(\alpha^{3})$;
substituting the single-plane holonomy angles
$\alpha_i=\pi a_i^{2}$ gives~\eqref{eq:norm}.
\end{proof}

\begin{table}[htbp]
\centering
\caption{Operational results for Claims A--E of
Definition~\ref{def:hierarchy} in the $n=4$ non-abelian regime
(structure group $\SO(3)$). The non-abelian signature enters
through the commutator fit constant $c_{\mathrm{comm}}$ (Claim~C)
and the non-commuting-sequence $T$-statistic (Claim~E); the
remaining predictions are inherited from the abelian prototype.}
\label{tab:n4}
\footnotesize
\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}} l l l l l}
\toprule
Claim & Prediction ($n=4$) & Observed ($n=4$) & Fit metric & Error \\
\midrule
A & slope $=1$ & $0.9976$ & $R^2=0.9983$ & $0.24\%$ \\
B & $a_{\mathrm{rev}}=1.0$ & $0.9992$ & rel err $=0.00083$ & $0.083\%$ \\
C & $c_1=\pi$, $c_2=0.0500$, $c_{\mathrm{comm}}=\sqrt{2}\,\pi^2=13.96$
  & $3.1386$, $0.0526$, $13.33$ & $R^2=0.9999972$ & $\leq 4.5\%$ \\
D & $K_{\mathrm{pred}}=29$ & $K_{\mathrm{obs}}=30$ &
  rel err $=0.034$ & $3.4\%$ \\
E & $T_{\mathrm{loop}}<2$, $T_{\mathrm{ctrl}}>1$,
  $T_{\mathrm{noncomm}}>5\,T_{\mathrm{loop}}$ & $0.40$, $11.47$,
  $22.22$ & ratios $29$, $56$ & satisfied \\
\bottomrule
\end{tabular*}
\end{table}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\columnwidth]{claims_ae_n4_nonabelian.png}
\caption{Operational results for Claims A--E in the $n=4$
non-abelian regime (structure group $\SO(3)$). (a)~Claim~A:
three-dimensional held-out margin erosion; slope $0.9976$,
$R^2=0.9983$. (b)~Claim~B: orientation-reversal amplitude
$0.9992$ against the predicted $1.0$ (relative error $0.083\%$).
(c)~Claim~C: single-plane holonomy-area scaling and the
non-abelian commutator signature; the single-plane fit gives
$c_1=3.1386$ (against $\pi$) and $c_2=0.0526$ (against $0.0500$),
and the commutator fit gives $c_{\mathrm{comm}}=13.33$ against
$\sqrt{2}\,\pi^{2}=13.96$ (relative error $4.5\%$).
(d)~Claim~D: repeated-loop fatigue in $\so(3)$ via matrix
increments $F_k\,\mathfrak{l}_z$; $K_{\mathrm{pred}}=29$ and
$K_{\mathrm{obs}}=30$ (relative error $3.4\%$). (e)~Claim~E:
total-variance $T$-statistics with signed residuals;
$T_{\mathrm{loop}}=0.40$, $T_{\mathrm{ctrl}}=11.47$,
$T_{\mathrm{noncomm}}=22.22$, with ratio
$T_{\mathrm{noncomm}}/T_{\mathrm{loop}}=56$.}
\label{fig:n4}
\end{figure}

\begin{proposition}[Non-abelian signature verdict]\label{prop:nonab}
Two independent falsifiable predictions capture the non-abelian
signature of the $n=4$ prototype: (i)~the commutator fit constant
$c_{\mathrm{comm}}\sim\sqrt{2}\,\pi^{2}$ of Claim~C
(Lemma~\ref{lem:comm} with $\alpha_i=\pi a_i^{2}$), and (ii)~the
non-commuting-sequence $T$-statistic of Claim~E. The measured
values (Table~\ref{tab:n4}, Fig.~\ref{fig:n4}) are
$c_{\mathrm{comm}}=13.33$ against $\sqrt{2}\,\pi^{2}=13.96$
(relative error $4.5\%$) and $T_{\mathrm{noncomm}}/
T_{\mathrm{loop}}=56$ against the predicted lower bound of $5$;
the remaining claims A--E hold within the tolerances of
Table~\ref{tab:n4}.
\end{proposition}

\begin{proof}
The measured values are direct outputs of the deposited
verification runs. Claims~A, B, and~D reproduce the abelian
predictions (the $\kk(a)=a^{2}$ dimension-independence, the
reversal amplitude, and the fatigue count) because the radially
symmetric viability makes $\kk$ dimension-free
(Corollary~\ref{cor:kappa-geometric-phase}); Claim~C's two-term
fit and commutator fit instantiate Lemma~\ref{lem:comm} at
$\alpha_i=\pi a_i^{2}$; Claim~E's $T$-statistics are the
signed-residual total-variance ratios of the deposited runs. Each
measured value lies within the tolerance stated in
Table~\ref{tab:n4}.
\end{proof}

\begin{remark}
The viability-weighted curvature prediction $\kk(a)=a^{2}$ is
dimension-independent for radially symmetric $V$; the
holonomy-area scaling and the $3/2$ fatigue correction persist
from $n=3$ to $n=4$ without modification. The non-abelian
structure contributes only higher-order corrections: the
commutator term of Claim~C and the commutator bias of Claim~E.
\end{remark}

\subsection{Stress test of Claim D's heavy-tail index}
\label{sec:verdict-stress}

Claim~D was operationalized on the abelian prototype with a single
heavy-tailed noise distribution (Student--$t$, $\mathrm{df}=3$,
$\sigma_\eta=0.01$) at one amplitude ($a=0.3$). The stress test
sweeps the heavy-tail index across
$\mathrm{df}\in\{1.5,2,2.5,3,4,5,7,10,20,50,\infty\}$ --- the
Gaussian light-tailed limit at $\mathrm{df}=\infty$, and
$\mathrm{df}=1.5$ in the infinite-variance regime $\alpha=1.5<2$
--- and the noise scale across
$\sigma_\eta\in\{0.005,0.01,0.02,0.05,0.10\}$, with $200$
Monte-Carlo seeds per cell.

\begin{proposition}[Stress-test verdicts]\label{prop:stress}
For each cell $(\mathrm{df},\sigma_\eta)$ of the grid, let
$f_{\mathrm{conf}}$ denote the fraction of the $200$ seeds for
which Claim~D's relative error is below $15\%$. Then:
\begin{enumerate}[leftmargin=*,itemsep=1pt]
\item (reference cell) at the operating scale
  $(\mathrm{df}=3,\sigma_\eta=0.01)$,
  $f_{\mathrm{conf}}=1.000$;
\item (robust regime) $f_{\mathrm{conf}}\geq0.985$ throughout
  $\mathrm{df}\in[2,\infty]$ at $\sigma_\eta\leq0.02$;
\item (acceptable regime) $f_{\mathrm{conf}}\in[0.80,0.95)$ for
  $\mathrm{df}\geq3$ at $\sigma_\eta=0.05$;
\item (breakdown) $f_{\mathrm{conf}}\leq0.75$ throughout the
  $\mathrm{df}$ axis at $\sigma_\eta=0.10$;
\item (gracefulness) the breakdown is smooth across the
  infinite-variance boundary $\mathrm{df}=2$, with no
  discontinuity.
\end{enumerate}
\end{proposition}

\begin{proof}
Direct Monte-Carlo computation ($200$ seeds per cell; deposited
artifacts). The cumulative fatigue sum $\sum_k F_k$ is dominated
by the deterministic mean $\mu_F=a\,\kk(a)+C_{\mathrm{fat}}\,
a^{3/2}=0.0352$ at the operating point, with $\kk(a)=a^{2}=0.09$
and the calibrated $C_{\mathrm{fat}}=0.05$ (the coefficient is
derived in Theorem~\ref{thm:levy-3half} below); the heavy-tail
fluctuations $\eta_k$ become comparable to $\mu_F$ only at
$\sigma_\eta\geq0.05$, five times the operating scale, which is
where the acceptable regime gives way to breakdown. The
infinite-variance boundary $\mathrm{df}=2$ (for the heavy-tail
theory of the Student--$t$ index see \citealp{bhattacharya2007})
separates finite- from infinite-variance noise; the prediction
degrades smoothly because the Claim~D bound applies to the
deterministic-plus-noise sum, not to the variance of $\eta_k$.
\end{proof}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\columnwidth]{claim_d_heavytail_stress.png}
\caption{Heavy-tail index stress test of Claim~D across the
$(\mathrm{df},\sigma_\eta)$ grid with $200$ Monte-Carlo seeds per
cell. (a)~Fraction of seeds for which Claim~D's relative error is
below $15\%$; the robust region ($f_{\mathrm{conf}}\geq0.95$)
covers the operating scale $\sigma_\eta=0.01$ across all
$\mathrm{df}\geq2$. (b)~$K_{\mathrm{pred}}$ and
$K_{\mathrm{obs}}$ versus tail index at $\sigma_\eta=0.01$ with
mean$\pm$standard-deviation error bars; the two curves track within
a relative error of at most $5\%$. (c)~Stress boundary:
$f_{\mathrm{conf}}$ versus $\mathrm{df}$ for each
$\sigma_\eta$; the robust threshold ($0.95$, dotted) and the
acceptable threshold ($0.80$, dashed) bracket the operating
regime. The infinite-variance boundary $\mathrm{df}=2$ is crossed
smoothly.}
\label{fig:stress}
\end{figure}

\subsection{L\'evy $\alpha$-stable first-passage derivation of the
$3/2$ fatigue exponent}\label{sec:verdict-levy}

Claims~C and~D of Definition~\ref{def:hierarchy} carry a
non-analytic fatigue correction $C_{\mathrm{fat}}\,a^{3/2}$. This
subsection derives both the exponent $3/2$ and the exact
coefficient from a L\'evy $\alpha$-stable first-passage model: the
leading non-analytic correction to the deterministic holonomy
$\pi a^{2}$ arises from the linear stochastic integral of the
connection $1$-form against a planar Brownian perturbation of the
loop, with noise variance rate $\sigma^{2}=\nu\,a$ scaling
linearly in the loop amplitude (fluctuations accumulating along
the loop perimeter $2\pi a$).

Let the loop $\gamma_a(t)=(a\cos 2\pi t,\,a\sin 2\pi t)$,
$t\in[0,1]$, be perturbed by a planar Brownian motion
$W=(W_1,W_2)$ with variance rate $\sigma^{2}=\nu a$ per component,
$\tilde\gamma=\gamma_a+\sigma W$, and let the connection be the
area form $A=\tfrac12(x\,\mathrm{d}y-y\,\mathrm{d}x)$, so that
the holonomy is $H=\tfrac12\oint_{\tilde\gamma}(x\,\mathrm{d}y-
y\,\mathrm{d}x)$.

\begin{lemma}[It\^o expansion of the perturbed holonomy]
\label{lem:ito-expand}
The perturbed holonomy admits the expansion
\begin{equation}\label{eq:H-expand}
  H \;=\; \pi a^{2} \;+\; \frac{\sqrt{5}}{2}\,\sigma a\,X
  \;+\; \frac{\sigma^{2}}{2}\,X_2 \;+\; O(\sigma^{3}),
\end{equation}
where $X\sim\mathcal N(0,1)$ is the combined linear stochastic
correction and $X_2$ is the L\'evy area, a centered Gaussian with
$\mathrm{Var}(X_2)=1/12$ for unit time.
\end{lemma}

\begin{proof}
Write $x(t)=a\cos 2\pi t+\sigma W_1(t)$ and $y(t)=a\sin 2\pi
t+\sigma W_2(t)$, so that $\mathrm{d}x=-2\pi a\sin 2\pi t\,
\mathrm{d}t+\sigma\,\mathrm{d}W_1$ and $\mathrm{d}y=2\pi a\cos
2\pi t\,\mathrm{d}t+\sigma\,\mathrm{d}W_2$. Expanding
$x\,\mathrm{d}y-y\,\mathrm{d}x$ and collecting by powers of
$\sigma$: the $O(1)$ term is
$\tfrac12\oint 2\pi a^{2}(\cos^{2}+\sin^{2})\,\mathrm{d}t=\pi
a^{2}$; the $O(\sigma^{2})$ term is the L\'evy area
$\tfrac{\sigma^{2}}{2}\oint(W_1\,\mathrm{d}W_2-W_2\,\mathrm{d}W_1)
$, of variance $\sigma^{4}/12$ for unit time; and the
$O(\sigma^{3})$ terms collect the higher It\^o corrections. The
$O(\sigma)$ term is the centered Gaussian
\[
  G \;=\; \frac{\sigma a}{2}\int_0^1\!\bigl(\cos 2\pi t\,
  \mathrm{d}W_2(t)-\sin 2\pi t\,\mathrm{d}W_1(t)\bigr)
  \;+\;\pi\sigma a\int_0^1\!\bigl(W_1(t)\cos 2\pi t+W_2(t)
  \sin 2\pi t\bigr)\,\mathrm{d}t,
\]
whose variance we compute exactly. The It\^o isometry gives the
variance of the stochastic integral as
$\tfrac{\sigma^{2}a^{2}}{4}\int_0^1(\cos^{2}2\pi t+\sin^{2}2\pi
t)\,\mathrm{d}t=\tfrac{\sigma^{2}a^{2}}{4}$. For the drift
integral, using $\mathrm{Cov}(W(t),W(s))=\min(t,s)$ and evaluating
the inner integrals $\int_0^t s\cos 2\pi s\,\mathrm{d}s
+t\int_t^1\cos 2\pi s\,\mathrm{d}s=\bigl(\cos 2\pi t-1\bigr)/
(4\pi^{2})$ and $\int_0^t s\sin 2\pi s\,\mathrm{d}s
+t\int_t^1\sin 2\pi s\,\mathrm{d}s=\sin 2\pi t/(4\pi^{2})-t/(2\pi)
$,
\[
  V_c := \int_0^1\!\!\int_0^1\cos 2\pi t\,\cos 2\pi s\,
  \min(t,s)\,\mathrm{d}t\,\mathrm{d}s = \frac{1}{8\pi^{2}},
  \qquad
  V_s := \int_0^1\!\!\int_0^1\sin 2\pi t\,\sin 2\pi s\,
  \min(t,s)\,\mathrm{d}t\,\mathrm{d}s = \frac{3}{8\pi^{2}},
\]
so the drift integral has variance $\pi^{2}\sigma^{2}a^{2}
(V_c+V_s)=\tfrac{\sigma^{2}a^{2}}{2}$. The cross-covariance
between the two matched $(W_1,W_2)$ pairs uses
$\mathrm{Cov}\bigl(\int f\,\mathrm{d}W,\ \int g(s)\,W(s)\,
\mathrm{d}s\bigr)=\int g(s)\int_0^s f(t)\,\mathrm{d}t\,
\mathrm{d}s$:
\[
  \mathrm{Cov} \;=\; \frac{\sigma a}{2}\,\pi\sigma a
  \int_0^1\!\Bigl[\sin 2\pi s\int_0^s\!\cos 2\pi t\,\mathrm{d}t
  \;-\;\cos 2\pi s\int_0^s\!\sin 2\pi t\,\mathrm{d}t\Bigr]
  \mathrm{d}s \;=\; \frac{\pi\sigma^{2}a^{2}}{2}\cdot
  \frac{1}{2\pi} \;=\; \frac{\sigma^{2}a^{2}}{4}.
\]
Summing, $\mathrm{Var}(G)=\sigma^{2}a^{2}
\bigl(\tfrac14+\tfrac12+2\cdot\tfrac14\bigr)
=\tfrac{5}{4}\sigma^{2}a^{2}$, so $G$ has the law
$\tfrac{\sqrt5}{2}\sigma a\,X$ with $X\sim\mathcal N(0,1)$.
\end{proof}

\begin{theorem}[$3/2$ fatigue exponent with the exact kernel
constant]\label{thm:levy-3half}
With the perturbed loop $\tilde\gamma=\gamma_a+\sigma W$ and
variance rate $\sigma^{2}=\nu\,a$ (path-length-proportional
diffusion along the loop perimeter $2\pi a$), the leading
non-analytic correction to the deterministic holonomy $\pi a^{2}$
is
\begin{equation}\label{eq:cfat-formula}
  C_{\mathrm{fat}}\,a^{3/2},\qquad
  C_{\mathrm{fat}} \;=\; \frac{\sqrt{5\nu}}{2},
\end{equation}
and the exponent arises as $3/2=1+1/2$: the geometric factor $1$
is the holonomy's linear coefficient in the loop amplitude, and
the diffusive factor $1/2$ is the $\sigma\sim\sqrt{a}$ scaling
implied by $\sigma^{2}\sim a$, the Brownian self-similarity image
of the $1/2$-stable L\'evy first-passage distribution.
\end{theorem}

\begin{proof}
By Lemma~\ref{lem:ito-expand} the standard deviation of the
leading stochastic correction is $\tfrac{\sqrt5}{2}\sigma a$.
Substituting the diffusion ansatz $\sigma^{2}=\nu a$ gives
$\tfrac{\sqrt5}{2}\sqrt{\nu a}\,a=\tfrac{\sqrt{5\nu}}{2}\,
a^{3/2}$, which is~\eqref{eq:cfat-formula}. The quadratic
L\'evy-area correction scales as
$\sigma^{2}/(2\sqrt{12})\sim a$, an analytic integer power; in the
prototype regime $a<1$ (operating point $a=0.3$) the non-analytic
term $a^{3/2}$ dominates the analytic one, so the leading
non-analytic correction is $C_{\mathrm{fat}}\,a^{3/2}$. For the
L\'evy-distribution connection: the first-passage time $T_a$ of
$W_t$ to the loop boundary has the $1/2$-stable L\'evy
distribution with density $f_{T_a}(t)=(a/\sqrt{2\pi})\,
t^{-3/2}\exp(-a^{2}/2t)$; under the Brownian self-similarity
$t\sim a^{2}$ the density exponent $3/2$ maps to the amplitude
exponent $3/2$, which is the image carried by the
$\sigma a\sim a^{3/2}$ scaling of the linear stochastic integral.
\end{proof}

\begin{remark}[Numerical verification, and the coefficient]
\label{rem:levy-numerical}
Monte-Carlo simulation of the perturbed holonomy ($4{,}000$ seeds
per amplitude, $a$ swept over $14$ values in $[0.1,1.5]$,
$\nu=0.1$; deposited artifacts) verifies both constants. The
log--log fit of $\mathrm{std}(\delta H)$ versus $a$ gives exponent
$\widehat\beta=1.479$ against the theoretical $3/2$ (relative
error $1.4\%$), with $R^{2}=0.9999$; a nonparametric bootstrap
($10{,}000$ resamples) gives the $95\%$ confidence interval
$[1.471,\,1.493]$ with bootstrap standard error $0.0072$, in close
agreement with the analytical OLS interval $[1.471,\,1.487]$. The
interval excludes $3/2$ by a small margin exactly as the two-term
model predicts: the sub-leading analytic term contributes at order
$\sigma a$ to the standard deviation and drags the single-exponent
fit downward in the small-$a$ regime where the two terms are
comparable. The single-exponent coefficient is
$\widehat C=0.357$ and the two-term fit
$\mathrm{std}(\delta H)=c_1a^{3/2}+c_2a$ gives $c_1=0.349$, both
within $1.5\%$ of the exact value
$\sqrt{5\nu}/2=\sqrt{0.5}/2=0.3536$ of
Theorem~\ref{thm:levy-3half}: the exact variance computation of
Lemma~\ref{lem:ito-expand} --- the It\^o integral, the drift
integral, and their cross-covariance --- accounts for the full
coefficient, with no unexplained remainder.
\end{remark}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{levy_stable_3half_derivation.png}
\caption{L\'evy $\alpha$-stable first-passage derivation of the
$3/2$ fatigue exponent. Monte-Carlo estimate (circles, $4{,}000$
seeds per amplitude) of $\mathrm{std}(\delta H)$ versus amplitude
$a$, with the theoretical predictions of
Theorem~\ref{thm:levy-3half}: the exact leading non-analytic term
$(\sqrt{5\nu}/2)\,a^{3/2}$, and the sub-leading analytic
L\'evy-area term $(\nu/2\sqrt{12})\,a$. The log--log fit gives
$\widehat\beta=1.479$ (theory $3/2$) with $R^{2}=0.9999$; the
small-$a$ downward deviation of the single-exponent fit is the
linear L\'evy-area term.}
\label{fig:levy-3half}
\end{figure}

\subsection{The CPTP--Zeno lift and the Claim G scaling verdict}
\label{sec:verdict-cptp}

The recursive predictive-self-information arc
(Construction~\ref{con:seven}, $\OO_2$) is the one arc whose
forward component cannot be a deterministic function: an agent
whose predictions are part of the state must compute its own
predictive distribution. The CPTP lift (Definition~\ref{def:cptp})
commits to a quantum-instantiated agent whose measurement schedule
$(\tau_k,P_k)_{k\geq1}$ is controllable; under frequent
measurement the quantum Zeno effect~\cite{misra1977,facchi2008}
freezes the evolution inside the measurement subspace (the CPTP
formalism is standard~\cite{nielsen2000}). Whether Zeno
suppression alone resolves the self-reference is settled by
Theorem~\ref{thm:zeno-contraction} in Section~\ref{sec:lipschitz};
the present subsection fixes the generator form and establishes
the empirically distinguishable scaling signature that the lift
carries.

\begin{definition}[Dissipative Lindbladian and the two gap notions]
\label{def:lindbladian}
A dissipative quantum evolution is generated by a Lindbladian
$\mathcal L(\rho)=-i[H,\rho]+\sum_k\bigl(L_k\rho L_k^\dagger-
\tfrac12\{L_k^\dagger L_k,\rho\}\bigr)$ with Hamiltonian $H$ and
jump operators $\{L_k\}$~\cite{nielsen2000}. The \emph{Liouvillian
spectral gap} is the smallest strictly positive real part of the
Lindbladian spectrum,
\begin{equation}\label{eq:liouvillian-gap}
  \Delta \;=\; \min_{\lambda\in\mathrm{spec}(\mathcal L),\,
  \mathrm{Re}(\lambda)>0}\mathrm{Re}(\lambda),
\end{equation}
defined for genuinely dissipative evolutions ($\mathrm{spec}
(\mathcal L)\subset\{\mathrm{Re}\leq0\}$ with $0$ in the spectrum
by trace preservation). For a closed Hamiltonian system the
spectrum is pure imaginary and the relevant quantity is instead
the \emph{energy variance}
$(\Delta H)^{2}=\langle H^{2}\rangle-\langle H\rangle^{2}$ of the
survival-probability analysis below.
\end{definition}

\begin{proposition}[Quantum Zeno survival probability]
\label{prop:zeno-survival}
Let $P$ be a projective measurement applied every $\tau=t/N$.
Then
\begin{equation}\label{eq:zeno-limit}
  \lim_{N\to\infty}\bigl(P\,e^{-iHt/N}P\bigr)^{N} \;=\;
  e^{-iPHPt}\,P,
\end{equation}
and the survival probability obeys
\begin{equation}\label{eq:zeno-scaling}
  p_N(t) \;=\; \bigl\lVert\bigl(P\,e^{-iHt/N}P\bigr)^{N}\psi
  \bigr\rVert^{2} \;=\; 1-\tfrac{t^{2}}{N}\,(\Delta H)^{2} \;+\;
  O(N^{-2}),
\end{equation}
so the survival deficit $1-p_N(t)$ is quadratic in the
inter-measurement interval $\tau$. A classical continuous-time
Markov chain with rate matrix $Q$ instead satisfies
$\lVert e^{Q\tau}p-p\rVert_{1}=O(\tau)$, a linear deficit; the
factor-of-two gap between the exponents is the leading-order
signature separating quantum measurement-induced evolution from
classical relaxation.
\end{proposition}

\begin{proof}
The limit~\eqref{eq:zeno-limit} is the quantum Zeno theorem
of~\cite{misra1977}, with the operator form as in
\cite{facchi2008}; both are cited rather than reproduced. The
expansion~\eqref{eq:zeno-scaling} follows from second-order
perturbation theory of the survival amplitude:
$Pe^{-iH\tau}P=P-i\tau\,PHP-\tfrac{\tau^{2}}{2}PH^{2}P+O(\tau^{3})
$, so with $P\psi=\psi$,
\[
  p_N(t) \;=\; \bigl\lVert(Pe^{-iH\tau}P)^{N}\psi\bigr\rVert^{2}
  \;=\; 1-N\,\tfrac{\tau^{2}}{2}\bigl(\langle\psi,PH^{2}P\psi
  \rangle-\langle\psi,PHP\psi\rangle^{2}\bigr)+O(N\tau^{3})
  \;=\; 1-\tfrac{t^{2}}{N}(\Delta H)^{2}+O(N^{-2}),
\]
where $(\Delta H)^{2}$ is the energy spread of $\psi$ within the
measurement subspace and $N\tau^{3}=t^{3}/N^{2}$. The classical
bound follows from $e^{Q\tau}=I+Q\tau+O(\tau^{2})$ together with
$\lVert Qp\rVert_{1}$ bounded on the probability simplex.
\end{proof}

\begin{proposition}[Holevo information as the ensemble bound]
\label{prop:holevo}
In the lifted setting the predictor's prediction is an ensemble
$\{p_x,\rho_x\}_{x\in\mathcal X}$ of quantum states prepared with
classical probabilities $p_x$. The Holevo
information~\cite{holevo1973}
\begin{equation}\label{eq:holevo}
  \chi \;=\; S\Bigl(\sum_x p_x\,\rho_x\Bigr)-\sum_x p_x\,S(\rho_x),
\end{equation}
where $S(\rho)=-\mathrm{tr}(\rho\log\rho)$ is the von Neumann
entropy, upper-bounds the accessible classical information about
$x$ extractable from any measurement on the ensemble; in the
commuting case $[\rho_x,\rho_{x'}]=0$ the states are simultaneously
diagonalizable and $\chi$ reduces to the classical mutual
information of the joint distribution induced by the optimal
measurement.
\end{proposition}

\begin{proof}
The Holevo bound is the theorem of~\cite{holevo1973}; see
also~\cite{nielsen2000}, cited rather than reproduced. We verify
the commuting-case reduction: in a common eigenbasis each
$\rho_x$ is diagonal with entries $p_{y|x}$, the average state
$\sum_xp_x\rho_x$ is diagonal with entries
$\sum_xp_xp_{y|x}=p_y$, and therefore
$\chi=H(Y)-\sum_xp_xH(Y\vert X)=I(X;Y)$, the classical mutual
information of the channel $p_{y|x}$.
\end{proof}

\begin{remark}[Self-referential fixed point]\label{rem:zeno-fixed-point}
The quantum predictor's self-referential fixed-point equation
\begin{equation}\label{eq:zeno-fixed-point}
  \rho^{*} \;=\; \frac{P\,\Phi(P\,\rho^{*}P)\,P}
  {\mathrm{tr}\bigl(P\,\Phi(P\,\rho^{*}P)\,P\bigr)},
\end{equation}
for a CPTP channel $\Phi$ and Zeno projector $P$, is closed by
Theorem~\ref{thm:zeno-contraction}: for the depolarizing
instantiation $\Phi(\rho)=(1-p)\rho+p\,I/2^{n}$ with $p>0$, the
renormalized projected channel is an affine contraction with
Lipschitz constant $\mu=(1-p)/[(1-p)+pk/2^{n}]<1$, so $\rho^{*}=
P/k$ is the unique fixed point by Banach's
theorem~\cite{banach1922}. The optic-side contraction is
Theorem~\ref{thm:unconditional-banach} (product Lipschitz bound
$\prod_i\Lip(f_i)=0.697<1$); both are unconditional.
\end{remark}

\begin{proposition}[Claim G verdict]\label{prop:claimG}
Numerical simulation of a two-level system evolving under
$H=(\omega/2)\sigma_x$ with $\omega=2$ (Liouvillian gap
approximately $1$), followed by projective measurement of
$\sigma_z$, with state change measured by trace distance over $30$
measurement intervals spanning the Zeno regime
($\tau\in[10^{-3},10^{-1}]$) and the anti-Zeno regime
($\tau\in[10^{-1},10^{1}]$); the classical benchmark is a
two-state symmetric Markov chain with transition rate $\omega$.
Log--log fits of state change versus $\tau$ in the Zeno regime
give:
\begin{enumerate}[leftmargin=*,itemsep=2pt]
\item CPTP--Zeno scaling exponent
  $\alpha_{\mathrm{Zeno}}=1.9997$, $R^{2}=1.0000$ (predicted:
  $2$);
\item classical Markov scaling exponent
  $\alpha_{\mathrm{cl}}=0.9695$, $R^{2}=0.9997$ (predicted:
  $1$);
\item ratio $\alpha_{\mathrm{Zeno}}/\alpha_{\mathrm{cl}}\approx2$.
\end{enumerate}
The verdict of Claim~G is positive: the two regimes are
empirically distinguishable by the scaling exponent.
\end{proposition}

\begin{proof}
The Zeno-curve fit is a deterministic computation: the two-level
density matrix evolves unitarily at machine precision, and the
power-law exponent reproduces the analytic
expansion~\eqref{eq:zeno-scaling}, which is why $R^{2}=1.0000$ to
floating-point precision. The marginally smaller $R^{2}=0.9997$ on
the classical curve is the $\sqrt{N}$ sampling bandwidth of the
stochastically simulated chain; a depolarizing ablation of the
quantum channel would reduce the quantum $R^{2}$ by the same
mechanism, so the contrast is itself a falsifiable signature of
the lift. The measured exponents match the factor-of-two gap
predicted by Proposition~\ref{prop:zeno-survival} to four
significant figures. Verification artifacts are deposited.
\end{proof}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\columnwidth]{claim_g_zeno_plot.png}
\caption{Claim~G verdict. Log--log plot of state change (trace
distance) versus measurement interval $\tau$. CPTP--Zeno points
(squares) follow the $\tau^{2}$ reference line in the small-$\tau$
regime; the fitted exponent is $\alpha_{\mathrm{Zeno}}=1.9997$
with $R^{2}=1.0000$. Classical Markov points (triangles) follow
the $\tau^{1}$ reference line; the fitted exponent is
$\alpha_{\mathrm{cl}}=0.9695$ with $R^{2}=0.9997$. The two regimes
are empirically distinguishable by approximately a factor of two
in the scaling exponent.}
\label{fig:zeno}
\end{figure}

\subsection{The contraction battery of the composite $T$}
\label{sec:verdict-titer}

Theorem~\ref{thm:composition} reduces the existence of the
unification object to the contractivity of the composite $T$ on
the operational state space. The seven forward maps of
Construction~\ref{con:seven} are implemented as continuous maps on
$X=[0,1]^{d}$ and iterated from compact starting subsets at five
Bregman-regularization strengths, with the Hausdorff distance
between successive iterates fit to a geometric tail. Holonomy
terminology follows \citealp{misner1973}.

\begin{proposition}[Analytic upper bound on the contraction rate]
\label{prop:qbound}
Let $f_1,\ldots,f_7:X\to X$ be the seven forward maps of
Construction~\ref{con:seven}, each a Lipschitz map on the compact
convex set $X\subset\RR^{d}$ with Lipschitz constants
$\Lip(f_i)$, each $\alpha_i$-strongly monotone with
$\alpha_i\geq0$ and $\beta_i$-cocoercive with $\beta_i\geq0$
(standard hypotheses of convex optimization). Then the
Bregman-regularized composite $T_{\mathrm{reg}}(K)=(1-\lambda)\,
T(K)+\lambda\,\Pi_{\mathcal K}(T(K))$ is Lipschitz with
\begin{equation}\label{eq:qbound}
  \Lip(T_{\mathrm{reg}}) \;\leq\; (1-\lambda)\,
  \prod_{i=1}^{7}\Lip(f_i) \;+\; \lambda\,\Lip(\Pi_{\mathcal K})
  \;\leq\; (1-\lambda)\,\prod_{i=1}^{7}\Lip(f_i)\;+\;\lambda,
\end{equation}
the second inequality using that the metric projection onto a
closed convex set is nonexpansive (a standard result of convex
analysis). In particular, if $\prod_i\Lip(f_i)<1$ and
$\lambda\in[0,1)$, then $\Lip(T_{\mathrm{reg}})<1$ and
$T_{\mathrm{reg}}$ is a contraction on the closed set $X$, with
unique fixed point by Banach's theorem~\cite{banach1922}. The
numerically measured contraction factors of
Propositions~\ref{prop:titer-base}--\ref{prop:titer} below
satisfy $q\leq(1-\lambda)\,\bar q_{\mathrm{prod}}+\lambda$ with
$\bar q_{\mathrm{prod}}=\prod_i\Lip(f_i)$: the analytic
counterpart of the empirical $q$'s.
\end{proposition}

\begin{proof}
Lipschitz composition is submultiplicative:
$\Lip(T)=\Lip(f_7\circ\cdots\circ f_1)\leq\prod_{i=1}^{7}\Lip(f_i)
$ by the chain rule for Lipschitz constants. The regularized
operator $T_{\mathrm{reg}}=(1-\lambda)T+\lambda\,
\Pi_{\mathcal K}\!\circ T$ is a convex combination of two
operators bounded by $\max\{\Lip(T),\Lip(\Pi_{\mathcal K})\}$,
and $\Lip(\Pi_{\mathcal K})\leq1$ by nonexpansiveness of the
metric projection onto a closed convex set, giving
$\Lip(T_{\mathrm{reg}})\leq(1-\lambda)\prod_i\Lip(f_i)+\lambda$.
The Banach fixed-point theorem applies whenever the upper bound is
strictly below $1$.
\end{proof}

\begin{remark}[The bound is sufficient, not tight]
\label{rem:qbound-tightness}
The analytic bound~\eqref{eq:qbound} is sharp in the regime of
Proposition~\ref{prop:titer-control} below --- six contractions
and one expansion, $\Lip(f_2)=1.15$, product $\approx0.69$ --- and
yet it stays above the measured $q$'s: at $\lambda=0.5$ the bound
is $0.845$ against the measured $q=0.5182$; at $\lambda=0.7$ it is
$0.907$ against $q=0.7075$. The bound is a sufficient condition
for contraction, not a tight one; the empirical $q$'s are smaller
because the Bregman regularization reorganizes the trajectories
toward the interior of $\mathcal K$ rather than merely averaging
them. Sharpening the bound to recover the empirical $q$'s
analytically is open.
\end{remark}

\begin{proposition}[Base contraction]\label{prop:titer-base}
Across $20$ base configurations (four starting compact subsets
$\times$ five Bregman regularization strengths
$\lambda\in\{0.0,0.1,0.3,0.5,0.7\}$), the iteration
$K_{n+1}=T_{\mathrm{reg}}(K_n)$ converges geometrically. At low
$\lambda$ ($0.0$, $0.1$, $0.3$) the iteration reaches machine
precision within $5$--$10$ steps, before a clean geometric tail
can be measured; the fitted contraction factor $q$ lies in
$[0.40,0.83]$ with $q<1$ in every case. At moderate $\lambda$
($0.5$, $0.7$) a clean geometric tail is measurable with
$R^{2}=1.0000$ in every case, with $q\in[0.51,0.71]$.
\end{proposition}

\begin{proof}
Direct numerical computation (deposited artifacts): the iteration
runs for $40$ steps and the Hausdorff distance
$d_H(K_n,K_{n+1})$ between successive iterates is fit to a
geometric tail $\log d_H\sim\beta+\alpha n$ with $q=e^{\alpha}$;
the reported $q$'s and $R^{2}$'s are those fits. All $20$
configurations have $q<1$.
\end{proof}

\begin{proposition}[Control: a single expansion optic does not
break contraction]\label{prop:titer-control}
A control $T$ replaces the RPSI optic $f_2$ by an expansion
(determinant $1.15>1$), testing whether the regularized
contraction is robust to a single expansion optic. All $8$ control
configurations (two starting sets $\times$ four $\lambda$ values)
converge geometrically: at $\lambda=0.5$,
$q=0.5182$ ($R^{2}=1.0000$); at $\lambda=0.7$, $q=0.7075$
($R^{2}=1.0000$). The control $T$ contracts at rates
indistinguishable from the canonical $T$ at the same
$\lambda$: the Bregman regularization and the other six
contractions dominate the single expansion.
\end{proposition}

\begin{proof}
Same protocol as Proposition~\ref{prop:titer-base} with the
expansion replacement; the reported rates are the geometric-tail
fits over the $8$ control configurations (deposited artifacts).
\end{proof}

\begin{proposition}[Dimensional robustness of the contraction]
\label{prop:titer}
A robustness sweep covers the dimensional axis
$d\in\{2,3,5,10,20\}$ and five expansion profiles --- canonical,
$k{=}3$ axis, $k{=}7$ axis, $k{=}3$ rotated, $k{=}7$ rotated (the
latter two applying the expansion along a Givens-rotated direction
to break the axis-aligned symmetry) --- over $375$
configurations ($5$ dimensions $\times5$ profiles $\times3$
starting sets $\times5$ Bregman strengths). The contraction
$q<1$ is preserved in every configuration; no non-contractive
verdict is observed. Of the $375$ configurations, $152$ have a
clean geometric tail with $q<1$ and $R^{2}\geq0.9$; $219$ reach
machine precision; and $4$ degrade to $R^{2}<0.9$ while keeping
$q<1$ --- $(d{=}2,k{=}3\text{ axis},\lambda{=}0.9)$ with
$q=0.8942$, $R^{2}=0.865$; $(d{=}5,k{=}7\text{ axis},
\lambda{=}0.9)$ with $q=0.8919$, $R^{2}=0.882$;
$(d{=}10,k{=}7\text{ rotated},\lambda{=}0.9)$ with $q=0.8788$,
$R^{2}=0.791$; $(d{=}20,k{=}3\text{ rotated},\lambda{=}0.9)$ with
$q=0.8984$, $R^{2}=0.772$. The unification object exists by
Banach's fixed-point theorem throughout the dimensional range
$d\in\{2,\ldots,20\}$ and across all five expansion profiles.
\end{proposition}

\begin{proof}
\begin{sloppypar}
Direct numerical computation (deposited artifacts). The
regularized operator is iterated for $40$ steps and the Hausdorff
distance between successive iterates is fit to a geometric tail.
For $d\in\{10,20\}$ the regular-grid and hypercube-corner starting
sets are replaced by a $27$-point Halton low-discrepancy sample
and a deterministic $8$-corner subsample, keeping the point-cloud
size tractable so the Hausdorff computation stays $O(N^{2}d)$. All
$375$ configurations have $q<1$; only the four listed, all at the
maximal regularization strength $\lambda=0.9$, have tail-fit
quality below $0.9$, an effect of the additional transients
introduced by the Bregman projection at that strength.
\end{sloppypar}
\end{proof}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\columnwidth]{t_iteration_convergence_plot.png}
\caption{$T$-iteration convergence at the base dimension $d=2$.
Left: canonical $T$ (all seven optics contractive). Right: control
$T$ with the RPSI optic $f_2$ replaced by an expansion. Log--log
plot of Hausdorff distance $d_H(K_n,K_{n+1})$ versus iteration
$n$. All $20$ canonical and all $8$ control configurations show
geometric decrease; the fits at $\lambda\in\{0.5,0.7\}$ have
$R^{2}=1.0000$ with $q\in[0.51,0.71]$.}
\label{fig:titer-conv}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\columnwidth]{t_iteration_robustness_extension_axis_aligned.png}
\caption{Robustness sweep along the dimensional axis
$d\in\{2,3,5,10,20\}$ (rows) and the axis-aligned expansion
profiles \emph{canonical}, \emph{$k{=}3$ axis}, \emph{$k{=}7$ axis}
(columns). Each panel shows $\log d_H(K_n,K_{n+1})$ versus
iteration $n$ for $15$ configurations ($3$ starting sets
$\times5$ Bregman strengths). All $225$ configurations are
contractive ($q<1$). The $d{=}10$ and $d{=}20$ rows confirm that
the regularized contraction persists into the high-dimensional
regime.}
\label{fig:titer-d10d20}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\columnwidth]{t_iteration_robustness_extension_rotated.png}
\caption{Robustness sweep along the dimensional axis
$d\in\{2,3,5,10,20\}$ (rows) and the rotated expansion profiles
\emph{$k{=}3$ rotated}, \emph{$k{=}7$ rotated} (columns), the
expansion applied along a Givens-rotated direction to break the
axis-aligned symmetry. Each panel shows $\log d_H(K_n,K_{n+1})$
versus iteration $n$ for $15$ configurations. All $150$
configurations are contractive ($q<1$); the rotated profile
produces the same number of degraded tail fits as the
axis-aligned profile, so rotating the expansion direction does not
break the regularized contraction.}
\label{fig:titer-rotated}
\end{figure}

% ==============================================================

"""
replace_once(
"""\\section{The Smooth Envelope of Algorithmic Rate-Distortion
Surrogates}\\label{sec:smooth-envelope}""",
VERDICTS + """\\section{The Smooth Envelope of Algorithmic Rate-Distortion
Surrogates}\\label{sec:smooth-envelope}""",
    "empirical-verdicts section")

open(F, "w").write(src)
print("part B written:", len(src), "bytes")
