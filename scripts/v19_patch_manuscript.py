#!/usr/bin/env python3
"""
v19 manuscript patcher.

Part 1 (user-directed Recommendation 4 -- mechanistic follow-up):
  P3  Insert sec:novelty-v19 (Study E26: protein-abundance
      mechanistic test via PaxDb + GSE64021 matched proteomics).

Part 2 (user-directed Recommendation 2 -- abstract and framing):
  P1  Abstract: add the genome-scale biological validation passage
      (kappa_V vs transcript response, platform replication, null
      controls, protein-layer decoupling), explicitly correlational.
  P2  Introduction: new contribution item for the E24--E26 line.
  P4  Conclusion: new paragraph summarizing the biology line.
  P5  Data availability: external compendia provenance (M3D, PRECISE,
      GSE64021, PaxDb).

All numbers come from download/novelty_v19_e26_protein_abundance_results.json
(fresh run of scripts/novelty_v19_e26_protein_abundance.py) and the
E24/E25 results JSONs.
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
# P1: abstract -- genome-scale biological validation passage
# ----------------------------------------------------------------------
OLD_P1 = r"""and a fully autopoietic integrated
MR-GR network with isozymes, substrate-induced enzyme expression, basal
constitutive TF, backup ATP, and anaplerotic PEPC ($24/29 = 82.8\%$,
strictly greater than the $5/17$ baseline, with the entire enzyme
and regulatory layers causally internal). The core claims are numerically
supported under stated tolerances; all extended claims are established
under explicit additional hypotheses with no remaining open
conjectures."""

NEW_P1 = r"""and a fully autopoietic integrated
MR-GR network with isozymes, substrate-induced enzyme expression, basal
constitutive TF, backup ATP, and anaplerotic PEPC ($24/29 = 82.8\%$,
strictly greater than the $5/17$ baseline, with the entire enzyme
and regulatory layers causally internal). Beyond the synthetic
prototypes, the operational $\kk$ is computed on the genome-scale
\emph{E.~coli} reconstruction iJO1366 ($435$-gene active-reaction
panel, baseline glucose-decline trajectory) and tested against
external expression compendia (M3D, PRECISE, GSE64021): $\kk$
correlates with the magnitude of the transcriptional response to
carbon exhaustion across the metabolic network ($r = +0.374$,
$n = 433$, $p \approx 10^{-15}$; partial $r = +0.251$ controlling
expression level; replicated on an independent RNA-seq platform
under carbon starvation, $r = +0.187$, $n = 241$), an association
that scales with growth-state-transition severity rather than
carbon identity, is bounded by null controls (balanced growth on
alternative carbon sources; phosphorus limitation), and does not
propagate to protein abundance changes (matched tandem-MS proteomics,
$r \approx +0.01$), localizing the $\kk$ signal to the regulatory
layer. All biological findings are stated as correlational, with
explicit coverage, platform, and perturbation-class limitations.
The core claims are numerically
supported under stated tolerances; all extended claims are established
under explicit additional hypotheses with no remaining open
conjectures."""

apply("P1 abstract biology passage", OLD_P1, NEW_P1)

# ----------------------------------------------------------------------
# P2: introduction -- new contribution item
# ----------------------------------------------------------------------
OLD_P2 = r"""\item \emph{Smooth-envelope theorem for the algorithmic upper bound}
(closing Conjecture~\ref{conj:alg-envelope}): the smooth envelope"""

NEW_P2 = r"""\item \emph{Genome-scale biological validation of the operational
$\kk$}: on the BiGG iJO1366 reconstruction, the per-gene $\kk$ of the
$435$-gene active-reaction panel (baseline glucose-decline trajectory)
correlates with the magnitude of the transcriptional response to
carbon exhaustion in the M3D compendium ($r = +0.374$, $n = 433$,
$p \approx 10^{-15}$; partial $r = +0.251$ controlling expression
level), replicates on an independent RNA-seq platform under carbon
starvation (GSE64021, $r = +0.187$, $n = 241$, starvation-depth
gradient), is bounded by null controls under carbon-source switching
and phosphorus limitation, and does not extend to protein
fold-changes on the matched proteome ($r \approx +0.01$ on the
$169$-gene subset where the transcript association is $+0.42$),
localizing the association to the regulatory layer
(Studies~E24--E26, Sections~\ref{sec:novelty-v17}
--\ref{sec:novelty-v19}). All biological claims are correlational,
with platform, perturbation-class, and coverage limitations stated
explicitly.
\item \emph{Smooth-envelope theorem for the algorithmic upper bound}
(closing Conjecture~\ref{conj:alg-envelope}): the smooth envelope"""

apply("P2 intro contribution item", OLD_P2, NEW_P2)

# ----------------------------------------------------------------------
# P3: insert sec:novelty-v19 (E26) after the v18 subsection
# ----------------------------------------------------------------------
OLD_P3 = r"""per-condition bars).

\section{Main Proposition}\label{sec:mainprop}"""

NEW_P3 = r"""per-condition bars).

% =============================================================
\subsection{v19 protein-abundance mechanistic test: the regulatory
layer (E26)}\label{sec:novelty-v19}
% =============================================================

The v17/v18 reviews identified the remaining scientific question:
\emph{why} does the $\kappa_V$--transcript association exist --- and,
specifically, whether the earlier lineage hypothesis (heavy-flux-
perturbation genes are regulated post-translationally while
small-perturbation genes rely on transcriptional compensation;
retracted as an artifact at $n=15$ in v14b) can be re-examined
properly with protein data. Study E26 (script
\texttt{novelty\_v19\_e26\_protein\_abundance.py}) tests the
protein layer with two sources: the PaxDb v6.1 integrated
whole-organism proteome of K-12 MG1655 ($3{,}747$ proteins, $91\%$
coverage, b-number indexed; \texttt{data/paxdb/README.md}) for
\emph{baseline} abundance, and the GSE64021 matched tandem-MS
spectral counts (\texttt{PeptideRaw}) for \emph{protein
fold-changes} under the same carbon-starvation contrasts as the E25
RNA-seq arm. The $\kappa_V$ panel is unchanged from E22; the
transcript metrics are the E24 (M3D exhaustion) and E25 (GSE64021
starvation) primaries.

\emph{[P-paxdb] Baseline abundance and mediation.} $\kappa_V$
correlates with baseline protein abundance ($r(\log_{10}\kappa_V,
\log_{10}\mathrm{ppm}) = +0.334$, $n = 429$, $p = 1.2 \times
10^{-12}$), and protein abundance correlates with mRNA level
($r = +0.632$) --- so abundance is a plausible confounder. It is
not, however, a substantive one: the partial correlation of $\kappa_V$
with the E24 transcript metric given mRNA level is $+0.244$, and
adding protein abundance moves it only to $+0.230$. Stratifying the
E24 association by PaxDb abundance tertiles shows the association in
\emph{every} stratum (low $+0.258$, $p = 1.9 \times 10^{-3}$; mid
$+0.365$, $p = 8.0 \times 10^{-6}$; high $+0.205$, $p = 0.014$) ---
it is not concentrated among low-abundance enzymes (where
transcription would be the only lever) and not absent among
high-abundance ones. The naive effect-modification reading of the
compensation hypothesis finds no support.

\emph{[P-protfc] The protein fold-change test (the decisive one).}
$169$ panel genes carry matched GSE64021 proteomics. On exactly
those genes the transcript association is \emph{present} --- E25
metric $r = +0.204$ ($p = 7.9 \times 10^{-3}$), E24 metric
$r = +0.420$ ($p = 1.3 \times 10^{-8}$) --- while the
\emph{protein} association is \emph{absent}: $r(\log_{10}\kappa_V,
\max|\log_2 \Delta\mathrm{P}|) = +0.008$ ($p = 0.92$; Spearman
$-0.009$), robust to the $4$~h-only window ($+0.032$) and to
requiring $\geq 6$ peptides ($+0.007$, $n = 150$). The mean response
magnitudes on the subset are $5.29$ (transcript, $\log_2$) versus
$1.26$ (spectral counts, $\log_2$) --- spectral counting compresses
and attenuates, which is stated as a limitation --- but the
transcript-layer gradient across $\kappa_V$ ($+0.20$/$+0.42$) has
no protein-layer counterpart whatsoever.

\emph{[P-tp] Transcript--protein coupling by $\kappa_V$ stratum.}
The signed transcript--protein coupling $r(\Delta T, \Delta P)$
rises monotonically with $\kappa_V$: $+0.088$ (NS) in the low
tertile, $+0.164$ ($p = 0.014$) in the mid, $+0.212$
($p = 1.3 \times 10^{-3}$) in the high. Within the top $\kappa_V$
tertile the protein response \emph{decreases} with $\kappa_V$
($r = -0.427$, $p = 9.3 \times 10^{-4}$) even as the transcript
response shows no within-stratum gradient ($-0.004$) --- the most
sensitive genes (the oxidative-phosphorylation and transport
machinery that carries the $\kappa_V$ mass) have the most
\emph{stable} protein levels. The $|\Delta P|/|\Delta T|$
implementation ratio is flat across strata ($0.235$ vs.\ $0.261$,
MWU $p = 0.78$).

\textbf{Verdict:} the protein layer sharpens the interpretation in
three steps. (i) The retracted v14b hypothesis is \emph{rejected in
its naive form}: high-$\kappa_V$ genes do \emph{not} respond less
transcriptionally --- they respond more (E24/E25), in every
abundance stratum. (ii) Its refined, protein-level prediction
\emph{is} confirmed: no $\kappa_V$ gradient in protein fold-changes
on the very genes where the transcript gradient is strongest, and
within the top stratum the highest-$\kappa_V$ proteins are the most
stable --- post-translational buffering of the most heavily
leveraged machinery. (iii) The high-$\kappa_V$ transcripts that do
change are the ones whose protein counts track them most closely
(coupling $+0.21$ vs.\ $+0.09$), so the transcript signal is
\emph{coupled}, not noise. Together: $\kappa_V$ predicts the
transcriptional \emph{reporting} of metabolic stress ---
directionally consistent, platform-robust, abundance-independent
--- while protein capacity itself is buffered; the association
lives at the regulatory layer. Honest limitations: $n = 169$
(biased toward detectable, more abundant proteins); single-shot
(no replicate) spectral-count proteomics, whose noise attenuates
protein correlations toward zero and whose dynamic range is
compressed; and PaxDb's integrated abundance averages many
conditions. A targeted replicate proteomics experiment (e.g.\ the
Schmidt et al.\ condition-dependent format) remains the natural
follow-up.

\textbf{Artifacts.} Script:
\texttt{novelty\_v19\_e26\_protein\_abundance.py}; data
\texttt{data/paxdb/} and \texttt{data/gse64021/} (PeptideRaw
columns). Outputs:
\texttt{novelty\_v19\_e26\_protein\_abundance.\{csv,txt,
results.json\}} in \texttt{download/} (the CSV carries the panel
with PaxDb ppm, both transcript metrics, and the protein
fold-changes).

\section{Main Proposition}\label{sec:mainprop}"""

apply("P3 insert v19 subsection", OLD_P3, NEW_P3)

# ----------------------------------------------------------------------
# P4: conclusion -- biology paragraph
# ----------------------------------------------------------------------
OLD_P4 = r"""from the prediction of failure. The proposition is falsifiable via the
seven-claim hierarchy, and all seven claims are confirmed."""

NEW_P4 = r"""from the prediction of failure. The proposition is falsifiable via the
seven-claim hierarchy, and all seven claims are confirmed.
On the biological side, the operational $\kk$ is validated at
genome scale on the \emph{E.~coli} iJO1366 reconstruction: the
$435$-gene panel's $\kk$ values correlate with the magnitude of the
transcriptional response to carbon exhaustion across two expression
platforms (M3D microarray $r = +0.374$ at $n = 433$,
$p \approx 10^{-15}$, partial $r = +0.251$; GSE64021 RNA-seq
$r = +0.187$ at $n = 241$), with the association scaling with
growth-state-transition severity rather than carbon identity,
bounded by null controls (carbon-source switching, phosphorus
limitation), and decoupled from protein abundance changes on the
matched proteome ($r \approx +0.01$ where the transcript
association is $+0.42$) --- a regulatory-layer signature, stated
throughout as correlational
(Sections~\ref{sec:novelty-elevation}--\ref{sec:novelty-v19})."""

apply("P4 conclusion biology paragraph", OLD_P4, NEW_P4)

# ----------------------------------------------------------------------
# P5: data availability -- external compendia provenance
# ----------------------------------------------------------------------
OLD_P5 = r"""\item \textbf{External data citations.} The Lemuth et al. 2008
  transcript time-series (PMC2583496) is reproduced from the
  published HTML supplementary; the Ishii et al. 2007 chemostat
  physiology values are from the published paper body. The Keio
  collection (Baba et al.~\cite{baba2006keio}) is referenced via
  Orth et al.'s 2011 iJO1366-vs-Keio validation anchor.
\end{itemize}"""

NEW_P5 = r"""\item \textbf{External data citations.} The Lemuth et al. 2008
  transcript time-series (PMC2583496) is reproduced from the
  published HTML supplementary; the Ishii et al. 2007 chemostat
  physiology values are from the published paper body. The Keio
  collection (Baba et al.~\cite{baba2006keio}) is referenced via
  Orth et al.'s 2011 iJO1366-vs-Keio validation anchor. The external
  expression compendia of the E24--E26 studies are: M3D
  (\texttt{E\_coli\_v4\_Build\_6}, Faith et al.\ 2008, retrieved
  from \texttt{m3d.mssm.edu}; sha256 and per-file provenance in
  \texttt{data/m3d/README.md}; raw tarball and large matrices not
  committed --- re-download per the README), PRECISE (Sastry et al.\
  2019, \texttt{github.com/SBRG/precise-db}; log-TPM matrices not
  committed), GSE64021 (Tabari, Li, Dong, Lee, Hwang, and Su, UNC
  Charlotte; series public 2023-12-15, SRA SRP050994; cited by
  accession; all $22$ per-sample processed files sha256-recorded in
  \texttt{data/gse64021/README.md}), and the PaxDb v6.1
  \emph{E.~coli} integrated whole-organism proteome (CC BY 4.0;
  \texttt{data/paxdb/README.md}).
\end{itemize}"""

apply("P5 data availability", OLD_P5, NEW_P5)

# ----------------------------------------------------------------------
with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\n{orig_len} -> {len(src)} chars (+{len(src)-orig_len})")
print(f"{n_applied}/5 patches applied")
