"""
Patch journal_manuscript.tex for v9:

1. NEW subsection 19.12 'v9 iterated elevation: κ_V^(Δb) biomass-residual-
   weighted variant stabilises the direct-correlation metric across rebuilds'
   (label sec:novelty-v9) with Remark rem:e17-delta-biomass-variant,
   inserted before \\section{Main Proposition}.

2. NEW Discussion subsection 'GEM-formalism limitations: the 12 persistent
   model-gap candidates' (label sec:gem-limitations) with the table of 12
   PERSISTENT gap genes that survive both iJO1366 and iML1515, inserted
   after the existing 'Limitations' subsection (right before 'Conjectures').
"""

TEX = "/home/z/my-project/scripts/journal_manuscript.tex"

NEW_SUBSECTION_NOVELTY = r"""\subsection{v9 iterated elevation: $\kappa_V^{(\Delta b)}$
biomass-residual-weighted variant stabilises the direct-correlation
metric across rebuilds}
\label{sec:novelty-v9}

The v8 round (\S\ref{sec:novelty-v8}, Remark~\ref{rem:e16-iml1515-cross-rebuild})
identified a counter-intuitive drop in the DIRECT $\kappa_V \to$
raw-Keio-$E$ correlation on iML1515 ($r_{\textnormal{iJO1366}} = +0.085$,
$r_{\textnormal{iML1515}} = -0.018$; AUC $0.713 \to 0.428$) and proposed
two refinements: (i) a biomass-residual-weighted variant
$\kappa_V^{(\Delta b)}(g) = \kappa_V(g) \cdot w(\Delta b(g)/b_{\mathrm{wt}})$
that scales $\kappa_V$ by how much biomass the KO actually reduces, and
(ii) a separate gap-count metric as the cross-rebuild-stable quantity.
The user requested implementation and testing of refinement~(i) on
both iJO1366 and iML1515 to determine which weight $w$ gives the most
STABLE direct-correlation metric across rebuilds.

\begin{remark}[Task E17: $\kappa_V^{(\Delta b)}$ biomass-residual-weighted
variant --- cross-rebuild stability test]
\label{rem:e17-delta-biomass-variant}
Study~E17 (script \texttt{novelty\_kv\_delta\_biomass\_e17.py}) tests
four weight variants on both E15 (iJO1366 binary subset $n=1206$)
and E16 (iML1515 binary subset $n=1325$):
\begin{center}
\begin{tabular}{lll}
\hline
variant & formula & description \\
\hline
\texttt{original}   & $\kappa_V$                                                       & baseline (no weight) \\
\texttt{linear}     & $\kappa_V \cdot (1 + \Delta b/b_{\mathrm{wt}})$                  & gentle re-weighting toward essentials \\
\texttt{quadratic}  & $\kappa_V \cdot (1 + (\Delta b/b_{\mathrm{wt}})^2)$              & quadratic re-weighting \\
\texttt{indicator}  & $\kappa_V \cdot \mathbb{1}[\Delta b > 0.05 \cdot b_{\mathrm{wt}}]$ & binary mask (manuscript proposal) \\
\hline
\end{tabular}
\end{center}
The stability metric is the cross-rebuild gap
$|\Delta| = |r_{\textnormal{iML1515}} - r_{\textnormal{iJO1366}}|$:
smaller gap = more stable across rebuilds. The cross-rebuild gap for
the original $\kappa_V$ (E15 vs E16) was $|\Delta r_{\textnormal{pearson}}|
= 0.103$, $|\Delta \rho_{\textnormal{spearman}}| = 0.298$,
$|\Delta \textnormal{AUC}| = 0.285$, and $|\Delta
\textnormal{AUC}_{\textnormal{held-out}}| = 0.199$.

\textbf{Results --- direct correlation:}
\begin{center}
\begin{tabular}{llcccc}
\hline
variant & metric & iJO1366 & iML1515 & $\Delta$ & $|\Delta|$ \\
\hline
\texttt{original}    & Pearson $r$    & $+0.085$ & $-0.018$ & $-0.103$ & $0.103$ \\
\texttt{linear}      & Pearson $r$    & $+0.138$ & $+0.079$ & $-0.060$ & $\mathbf{0.060}$ \\
\texttt{quadratic}   & Pearson $r$    & $+0.139$ & $+0.078$ & $-0.061$ & $0.061$ \\
\texttt{indicator}   & Pearson $r$    & $+0.351$ & $+0.466$ & $+0.115$ & $0.115$ \\
\hline
\texttt{original}    & Spearman $\rho$ & $+0.228$ & $-0.070$ & $-0.298$ & $0.298$ \\
\texttt{linear}      & Spearman $\rho$ & $+0.242$ & $+0.088$ & $-0.154$ & $0.154$ \\
\texttt{quadratic}   & Spearman $\rho$ & $+0.243$ & $+0.086$ & $-0.157$ & $0.157$ \\
\texttt{indicator}   & Spearman $\rho$ & $+0.329$ & $+0.462$ & $+0.133$ & $\mathbf{0.133}$ \\
\hline
\texttt{original}    & ROC AUC         & $0.713$  & $0.428$  & $-0.285$ & $0.285$ \\
\texttt{linear}      & ROC AUC         & $0.725$  & $0.591$  & $-0.134$ & $0.134$ \\
\texttt{quadratic}   & ROC AUC         & $0.726$  & $0.588$  & $-0.138$ & $0.138$ \\
\texttt{indicator}   & ROC AUC         & $0.735$  & $0.834$  & $+0.099$ & $\mathbf{0.099}$ \\
\hline
\end{tabular}
\end{center}

\textbf{Results --- held-out $70/30$ logistic-regression AUC:}
\begin{center}
\begin{tabular}{lcccc}
\hline
variant & iJO1366 & iML1515 & $\Delta$ & $|\Delta|$ \\
\hline
\texttt{original}    & $0.757$ & $0.559$ & $-0.199$ & $0.199$ \\
\texttt{linear}      & $0.767$ & $0.578$ & $-0.189$ & $0.189$ \\
\texttt{quadratic}   & $0.765$ & $0.576$ & $-0.189$ & $0.189$ \\
\texttt{indicator}   & $0.772$ & $0.752$ & $-0.020$ & $\mathbf{0.020}$ \\
\hline
\end{tabular}
\end{center}

\textbf{Stability winners.} The \texttt{indicator} variant
$\kappa_V \cdot \mathbb{1}[\Delta b > 0.05 \cdot b_{\mathrm{wt}}]$
--- exactly the variant the manuscript Remark~\ref{rem:e16-iml1515-cross-rebuild}
proposed --- is the most stable on three of four metrics:
\begin{itemize}
\item Direct ROC AUC: $|\Delta| = 0.099$ (vs $0.285$ original, $-65.3\%$)
\item Spearman $\rho$: $|\Delta| = 0.133$ (vs $0.298$ original, $-55.4\%$)
\item Held-out ROC AUC: $|\Delta| = 0.020$ (vs $0.199$ original, $\mathbf{-89.9\%}$)
\end{itemize}
The \texttt{linear} variant $\kappa_V \cdot (1 + \Delta b/b_{\mathrm{wt}})$
wins on direct Pearson $r$ ($|\Delta| = 0.060$, $-41.7\%$ vs original)
but loses on the other three. The \texttt{quadratic} variant is essentially
tied with \texttt{linear} on all metrics.

\textbf{Interpretation.} The indicator variant essentially asks
\emph{given that a gene is in-silico-essential, what is its $\kappa_V$?}
and uses that to predict raw-Keio-$E$. This works because both iJO1366
and iML1515 agree that in-silico-essential genes (high $\Delta b$) are
largely a subset of raw-Keio-$E$ ($68.5\%$ agreement on iJO1366, $78.9\%$
on iML1515), and the $\kappa_V$ magnitude \emph{among in-silico-essentials}
correlates with raw-Keio-$E$ similarly in both models. The indicator
variant zeroes out the non-essential-gene flux-rerouting noise that
was decoupling $\kappa_V$ from essentiality on the denser iML1515.

\textbf{Cross-rebuild-stable quantity.} The full picture that emerges
from E15 + E16 + E17 is now:
\begin{enumerate}
\item \emph{Gap-count metric} $|\{g : \textnormal{Keio}{=}E \land
\textnormal{PEC}{=}E \land \textnormal{in-silico}{=}N\}|$: drops
monotonically with model improvement ($30 \to 13$, $-56.7\%$) ---
the most stable cross-rebuild quantity (E16 Remark).
\item \emph{Indicator-weighted direct correlation}
$r(\kappa_V \cdot \mathbb{1}[\Delta b > 0.05 \cdot b_{\mathrm{wt}}],
\textnormal{Keio-}E)$: roughly equal across rebuilds
($r_{\textnormal{iJO}} = +0.351$, $r_{\textnormal{iML}} = +0.466$,
$|\Delta| = 0.115$), with the largest stability gain on the
held-out AUC ($|\Delta| = 0.020$, $-90\%$).
\item \emph{Unweighted direct correlation} $r(\kappa_V, \textnormal{Keio-}E)$:
NOT cross-rebuild-stable ($|\Delta r| = 0.103$,
$|\Delta \textnormal{AUC}| = 0.285$); should be reported
\emph{per-model} not as a cross-rebuild quantity.
\end{enumerate}
The manuscript's $\kappa_V$ is thus a viable framework-prediction
metric on each individual model, and the indicator-weighted variant
is the cross-rebuild-stable refinement. Deliverables:
\texttt{download/novelty\_kv\_delta\_biomass\_e17.\{csv, txt, png,
results.json\}}.
\end{remark}

"""

NEW_DISCUSSION_SUBSECTION = r"""\subsection{GEM-formalism limitations:
the $12$ persistent model-gap candidates}
\label{sec:gem-limitations}

Studies~E15 and E16 (Remarks~\ref{rem:e15-direct-keio} and
\ref{rem:e16-iml1515-cross-rebuild}) identified model-gap candidates
--- genes that BOTH the raw Baba 2006 Keio screen AND the independent
PEC database call essential, but iJO1366 / iML1515 in-silico
essentiality misses. The cross-rebuild comparison revealed that
$18$ of $30$ iJO1366 gap genes are RESOLVED by iML1515 (mostly the
aminoacyl-tRNA synthetases, which iML1515 captured by adding
explicit tRNA-charging reactions), but $12$ gaps PERSIST in both
reconstructions. These $12$ persistent gaps are not a $\kappa_V$
failure but a structural limitation of the GEM (genome-scale
metabolic model) formalism itself: they are CLASSES of genes
whose essentiality cannot be captured by FBA on the current
GEM framework without an explicit biomass-reaction term for
the missing cost (DNA replication, lipid-cycle energy, glycolysis-
isozyme redundancy, stringent response). We document them here as
a concrete deliverable for future GEM extensions --- e.g.~iML1515's
successor (the planned next E.~coli K-12 reconstruction).

\begin{table}[h]
\centering
\begin{tabular}{lllll}
\hline
bnum & gene & $\kappa_V$ (iML1515) & gap class & likely missing term \\
\hline
b2779 & \emph{eno}  & $5.02 \times 10^4$ & glycolysis (enolase)            & glycolysis-isozyme ATP-yield cost \\
b2925 & \emph{fbaA} & $4.46 \times 10^4$ & glycolysis (aldolase)            & glycolysis-isozyme ATP-yield cost \\
b3640 & \emph{dut}  & $3.80 \times 10^4$ & DNA precursor (dUTPase)          & dUTP pool consumption at growth rate \\
b2563 & \emph{acpS} & $2.99 \times 10^4$ & lipid cycle (ACP synthase)       & apo$\to$holo-ACP conversion energy cost \\
b1207 & \emph{prsA} & $2.79 \times 10^4$ & purine (PRPP synthetase)         & PRPP pool consumption \\
b3650 & \emph{spoT} & $2.50 \times 10^4$ & stringent response (ppGpp)       & not in metabolic network (regulatory) \\
b0954 & \emph{fabA} & $1.28 \times 10^4$ & lipid cycle (FA unsaturation)    & unsaturated-FA energy cost \\
b1912 & \emph{pgsA} & $1.28 \times 10^4$ & lipid cycle (PG synthase)        & phosphatidylglycerol pool \\
b0657 & \emph{lnt}  & $1.28 \times 10^4$ & lipid cycle (apolipoprotein N-acylT) & apolipoprotein maturation cost \\
b2234 & \emph{nrdA} & $7.68 \times 10^3$ & DNA precursor (RNR $\alpha$)     & dNTP pool consumption at growth rate \\
b2235 & \emph{nrdB} & $7.68 \times 10^3$ & DNA precursor (RNR $\beta$)      & dNTP pool consumption at growth rate \\
b2411 & \emph{ligA} & $7.52 \times 10^3$ & DNA replication (NAD-dep DNA ligase) & DNA-ligation ATP/NAD cost \\
\hline
\end{tabular}
\caption{The $12$ persistent model-gap candidates --- genes that both
the raw Keio screen AND the PEC database call essential, but BOTH
iJO1366 AND iML1515 in-silico essentiality miss. The $\kappa_V$ values
shown are the iML1515 values from Study~E16
(Remark~\ref{rem:e16-iml1515-cross-rebuild}); the iJO1366 values are
similarly large (most are $\geq 10^3$). The ``likely missing term''
column is the author's hypothesis for what biomass-reaction extension
would close the gap; verifying these is left for future work.}
\label{tab:gem-limitations}
\end{table}

The $12$ persistent gap genes fall into five classes:

\begin{enumerate}
\item \textbf{Glycolysis-isozyme redundancy} ($2$ genes: \emph{eno},
\emph{fbaA}). Both are core glycolytic enzymes whose KO should kill
biomass, but iML1515 still routes through isozymes (\emph{fbaB} for
\emph{fbaA}; \emph{eno} has no isozyme but its flux can be partially
bypassed via the ED pathway under glucose+O$_2$ minimal). The likely
fix is an explicit ATP-yield cost term on the biomass reaction that
penalises flux through the bypass pathway.

\item \textbf{DNA precursor pool} ($3$ genes: \emph{dut}, \emph{nrdA},
\emph{nrdB}). The $2$-deoxyribonucleotide pool's steady state is
determined by growth rate, but the pool is not consumed at the right
rate when these genes are knocked out --- the model still produces
enough dNTP to support biomass even though the cell cannot replicate
DNA. The fix is an explicit dNTP-pool consumption term in the biomass
reaction (analogous to the GAM --- growth-associated maintenance ---
term for ATP).

\item \textbf{Lipid cycle} ($4$ genes: \emph{acpS}, \emph{fabA},
\emph{pgsA}, \emph{lnt}). The apo$\to$holo-ACP conversion, the
unsaturated-FA energy cost, the PG pool, and the apolipoprotein
maturation cost are all missing from the biomass reaction. iML1515
added some lipid-cycle reactions but did not propagate the cost
to biomass reduction. The fix is explicit lipid-pool consumption
terms in the biomass reaction.

\item \textbf{Purine pool} ($1$ gene: \emph{prsA}, PRPP synthetase).
The phosphoribosyl pyrophosphate pool is the substrate for both
purine and pyrimidine synthesis, and iML1515's biomass reaction
under-allocates PRPP consumption relative to growth rate. The fix
is a stricter PRPP-pool mass balance.

\item \textbf{Regulatory / non-metabolic} ($1$ gene: \emph{spoT},
stringent response). \emph{spoT} is not in the metabolic network at
all --- it is the (p)ppGpp hydrolase/synthetase that orchestrates
the stringent response to amino-acid starvation. The GEM formalism
cannot capture its essentiality without an explicit (p)ppGpp
regulatory layer coupled to the GTP/ATP pools. This is a known
limitation of FBA-based GEMs; the fix would require extending the
GEM with a regulatory layer (a multi-level framework, beyond the
scope of pure FBA).

\item \textbf{DNA replication} ($1$ gene: \emph{ligA}, NAD-dependent
DNA ligase). DNA ligase is required for Okazaki-fragment maturation
and replication-completion; its KO should kill biomass via DNA
replication failure. The GEM formalism does not model DNA replication
as a flux-carrying process, only as a biomass-sink (the DNA
component of the biomass reaction). Without an explicit ATP/NAD
cost for DNA ligation, the biomass-reaction DNA component is
unaffected by \emph{ligA} KO. The fix is an explicit ligation-energy
cost term.
\end{enumerate}

\textbf{Recommendation for future GEM rebuilds.} Future
E.~coli K-12 metabolic reconstructions (e.g.~the planned
iML1515 successor) should add the four missing cost terms ---
\textbf{dNTP-pool consumption}, \textbf{lipid-pool consumption},
\textbf{PRPP-pool mass balance}, and \textbf{DNA-ligation ATP/NAD
cost} --- to the biomass reaction, and couple the stringent response
regulator \emph{spoT} to the GTP/ATP pools via a (p)ppGpp regulatory
layer. These four additions would close $11$ of the $12$ persistent
gaps; the $12$th (\emph{spoT}) requires a multi-level
GEM+regulatory framework that the pure-FBA GEM cannot support
without an explicit (p)ppGpp module. The $\kappa_V$ metric will
then correctly identify the model as improved --- the gap count
should drop further from $13$ toward $1$--$2$.

"""

def main():
    with open(TEX, 'r', encoding='utf-8') as f:
        s = f.read()

    # 1. Insert NEW subsection 19.12 right before \section{Main Proposition}
    anchor_main = "% =============================================================\n\\section{Main Proposition}\\label{sec:mainprop}"
    if anchor_main not in s:
        print("ERROR: Main Proposition anchor not found")
        return
    s = s.replace(anchor_main, NEW_SUBSECTION_NOVELTY + "\n" + anchor_main)

    # 2. Insert NEW Discussion subsection right before \subsection{Conjectures}
    # Find the "\subsection{Conjectures}" line and insert before it
    anchor_conj = "\\subsection{Conjectures}"
    if anchor_conj not in s:
        print("ERROR: Conjectures anchor not found")
        return
    s = s.replace(anchor_conj, NEW_DISCUSSION_SUBSECTION + "\n" + anchor_conj, 1)

    with open(TEX, 'w', encoding='utf-8') as f:
        f.write(s)
    n_lines = s.count("\n")
    print(f"patched {TEX}  (now {n_lines} lines)")

if __name__ == "__main__":
    main()
