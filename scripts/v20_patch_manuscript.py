#!/usr/bin/env python3
"""
v20 manuscript patcher.

Part 1 (user-directed task 2 -- review the v19 subsection wording for
precision and overstatement):
  W1-W5  Hedge the v19 (E26) subsection: correlational-mechanism
         language ("is confirmed", "post-translational buffering",
         "protein capacity itself is buffered", "whatsoever"), the
         metric-dependence of the magnitude gap, and replace the
         "remains the natural follow-up" sentence with a pointer to
         the executed replication.

Part 2 (user-directed task 1 -- perform the additional replication):
  P6  Insert sec:novelty-v20 (Study E27: Schmidt et al. 2016
      condition-dependent quantitative proteome, protein-layer
      replication of E26; PRECISE 2.0 evaluated and set aside with
      the documented reason).
  P7  Abstract: add the E27 replication numbers.
  P8  Introduction contribution item: extend to E24-E27 / v17-v20.
  P9  Conclusion: add the replication + the magnitude-parity
      correction.
  P10 Data availability: Schmidt 2016 + PRECISE-1K scan provenance.

All numbers come from download/novelty_v20_e27_schmidt_replication
_results.json (fresh run of scripts/novelty_v20_e27_schmidt_
replication.py) and the E26 results JSON.
"""
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
# W1: [P-tp] stability sentence -- flag as single-shot observation
# ----------------------------------------------------------------------
OLD_W1 = r"""($r = -0.427$, $p = 9.3 \times 10^{-4}$) even as the transcript
response shows no within-stratum gradient ($-0.004$) --- the most
sensitive genes (the oxidative-phosphorylation and transport
machinery that carries the $\kappa_V$ mass) have the most
\emph{stable} protein levels."""

NEW_W1 = r"""($r = -0.427$, $p = 9.3 \times 10^{-4}$) even as the transcript
response shows no within-stratum gradient ($-0.004$) --- on the
single-shot spectral counts, the most sensitive genes (the
oxidative-phosphorylation and transport machinery that carries the
$\kappa_V$ mass) appear to have the most \emph{stable} protein
levels; the v20 quantitative replication re-examines exactly this
observation (Section~\ref{sec:novelty-v20})."""

apply("W1 stability sentence hedged", OLD_W1, NEW_W1)

# ----------------------------------------------------------------------
# W2: verdict (ii) -- "is confirmed" -> "finds support", hedge mechanism
# ----------------------------------------------------------------------
OLD_W2 = r"""abundance stratum. (ii) Its refined, protein-level prediction
\emph{is} confirmed: no $\kappa_V$ gradient in protein fold-changes
on the very genes where the transcript gradient is strongest, and
within the top stratum the highest-$\kappa_V$ proteins are the most
stable --- post-translational buffering of the most heavily
leveraged machinery."""

NEW_W2 = r"""abundance stratum. (ii) Its refined, protein-level prediction
\emph{finds support}: no $\kappa_V$ gradient in protein fold-changes
on the very genes where the transcript gradient is strongest, and
within the top stratum the highest-$\kappa_V$ proteins are the most
stable on spectral counts --- a pattern consistent with (but, at
$n = 169$ with single-shot counting, not by itself establishing)
post-translational buffering of the most heavily leveraged
machinery."""

apply("W2 verdict (ii) hedged", OLD_W2, NEW_W2)

# ----------------------------------------------------------------------
# W3: verdict (iii) + "Together" passage
# ----------------------------------------------------------------------
OLD_W3 = r"""(iii) The high-$\kappa_V$ transcripts that do
change are the ones whose protein counts track them most closely
(coupling $+0.21$ vs.\ $+0.09$), so the transcript signal is
\emph{coupled}, not noise. Together: $\kappa_V$ predicts the
transcriptional \emph{reporting} of metabolic stress ---
directionally consistent, platform-robust, abundance-independent
--- while protein capacity itself is buffered; the association
lives at the regulatory layer."""

NEW_W3 = r"""(iii) The high-$\kappa_V$ transcripts that do
change are the ones whose protein counts track them most closely
(coupling $+0.21$ vs.\ $+0.09$, within-experiment), so the transcript
signal is weakly \emph{coupled} to protein change rather than pure
noise. Together: $\kappa_V$ predicts the transcriptional
\emph{reporting} of metabolic stress --- directionally consistent,
platform-robust, abundance-independent --- while protein-level
fold-changes show no corresponding $\kappa_V$ gradient; on this
evidence the association is localized to the regulatory layer, a
localization the v20 replication then tests with quantitative
proteomics (Section~\ref{sec:novelty-v20})."""

apply("W3 verdict (iii)/Together passage revised", OLD_W3, NEW_W3)

# ----------------------------------------------------------------------
# W4: "remains the natural follow-up" -> executed (v20 pointer)
# ----------------------------------------------------------------------
OLD_W4 = r"""conditions. A targeted replicate proteomics experiment (e.g.\ the
Schmidt et al.\ condition-dependent format) remains the natural
follow-up."""

NEW_W4 = r"""conditions. The v20 round performs exactly this replication,
with the Schmidt et al.\ condition-dependent quantitative proteome
(Section~\ref{sec:novelty-v20})."""

apply("W4 follow-up executed pointer", OLD_W4, NEW_W4)

# ----------------------------------------------------------------------
# W5: [P-protfc] magnitude precision + drop "whatsoever"
# ----------------------------------------------------------------------
OLD_W5 = r"""magnitudes on the subset are $5.29$ (transcript, $\log_2$) versus
$1.26$ (spectral counts, $\log_2$) --- spectral counting compresses
and attenuates, which is stated as a limitation --- but the
transcript-layer gradient across $\kappa_V$ ($+0.20$/$+0.42$) has
no protein-layer counterpart whatsoever."""

NEW_W5 = r"""magnitudes on the subset are $5.29$ (transcript, $\log_2$, on the
zero-inflated GSE TPM metric) versus $1.26$ (spectral counts,
$\log_2$) --- spectral-count noise attenuates protein correlations
toward zero, which is stated as a limitation --- but the
transcript-layer gradient across $\kappa_V$ ($+0.20$/$+0.42$) has
no protein-layer counterpart (a contrast the v20 quantitative
replication then confirms)."""

apply("W5 magnitude precision", OLD_W5, NEW_W5)

# ----------------------------------------------------------------------
# P6: insert sec:novelty-v20 (E27) after the v19 subsection
# ----------------------------------------------------------------------
OLD_P6 = r"""\texttt{novelty\_v19\_e26\_protein\_abundance.\{csv,txt,
results.json\}} in \texttt{download/} (the CSV carries the panel
with PaxDb ppm, both transcript metrics, and the protein
fold-changes).

\section{Main Proposition}\label{sec:mainprop}"""

NEW_P6 = r"""\texttt{novelty\_v19\_e26\_protein\_abundance.\{csv,txt,
results.json\}} in \texttt{download/} (the CSV carries the panel
with PaxDb ppm, both transcript metrics, and the protein
fold-changes).

% =============================================================
\subsection{v20 protein-layer replication: the Schmidt
condition-dependent proteome (E27)}\label{sec:novelty-v20}
% =============================================================

The v19 verdict closed on the honest limitation that its decisive
protein test rested on single-shot spectral counting, and named the
replication that would settle it. This round performs that
replication (user-directed), with the quantitative condition-
dependent proteome of Schmidt et al.\ 2016: $22$ growth conditions
in biological triplicate (label-free quantification, median ratios
to the glucose reference, per-condition q-values and coefficients
of variation; strain BW25113, a K-12 derivative). The alternative
candidate, PRECISE 2.0, was evaluated first: a scan of all
$1{,}035$ samples of the expanded SBRG compendium
(\texttt{precise1k\_metadata\_qc\_scan.csv}) finds no
carbon-depletion condition at all --- the only starvation-like
samples are iron- and nitrogen-limited, non-carbon classes already
covered by E25's controls --- and the transcript side is already
replicated on two platforms (E24, E25). The decisive gap is the
protein layer, and the Schmidt proteome fills it. The $\kappa_V$
panel is unchanged from E22; the transcript metrics are recomputed
with the exact E26 code; the condition classes mirror E24/E25:
\emph{carbon exhaustion} (stationary phase 1 and 3 days after
glucose depletion --- the E24 class), \emph{carbon limitation}
(glucose-limited chemostats at $\mu = 0.5/0.35/0.20/0.12$~h
$^{-1}$), \emph{carbon switch} (11 alternative carbon sources),
\emph{stress on glucose} (NaCl, $42^{\circ}$C, pH~6), and an
\emph{internal null} (an independent glucose batch culture,
``Glucose.2'').

\emph{[S-src] Provenance.} The supplementary workbook
(NIHMS65833) was retrieved via the Europe PMC REST endpoint for
PMC4888949 (raw data: PRIDE PXD000498); sha256 and file inventory
in \texttt{data/schmidt2016/README.md}. Tables S4--S8 were located
by name; the analysis uses Table S8 (dataset 2, the paper's
higher-confidence triplicate set), with Table S7 (dataset 1, no
replicates) as a cross-dataset sensitivity.

\emph{[S-map] Gene mapping.} $2{,}284$ of $2{,}350$ Table-S6
proteins carry b-numbers (the final table's own annotation); spot
checks pass (aceA $=$ b4015, rpoB $=$ b3987, gapA $=$
P0A9B2/b1779, groL $=$ b4143); $4$ duplicate-b-number rows (clpB
listed twice, bioD under two accessions) are averaged --- the same
convention as E26's duplicate probes. $366/435$ panel genes ($84\%$;
E26: $169$, $39\%$) carry quantitative triplicate protein
fold-changes.

\emph{[S-contrast] Class assignment.} Stationary-phase harvest
$1/3$ days after glucose exhaustion is the same perturbation class
as the E24 M3D stationary series; the chemostats are steady-state
carbon limitation; the glucose-matched stresses are chronic (grown
at $42^{\circ}$C/pH~6/+NaCl) rather than E25's acute shocks;
Glucose.2 is an independent culture of the reference condition.

\emph{[S-internal-null] Data quality and technical baseline.} The
independent glucose batch shows median $|\log_2 \Delta P| = 0.18$
across all $2{,}058$ proteins, versus $0.81/0.80$ under stationary
phase and $0.43$ (median) under carbon switching --- the noise
floor sits far below the biological signal, and the dynamic range
extends to $|\log_2 \Delta P| = 12.3$. The batch control also
carries its own weak $\kappa_V$ gradient: $r = -0.119$ ($p =
0.023$) --- even across replicate cultures of the \emph{same}
medium, higher-$\kappa_V$ proteins vary slightly \emph{less}; the
class tests below must be read against this technical baseline.

\emph{[R-protfc] The primary replication (decisive).} On the
$366$-gene intersection the three-way contrast reads: E24
transcript metric $r = +0.419$ ($p = 6.4 \times 10^{-17}$, $n =
365$); E25 transcript metric $r = +0.237$ ($p = 5.8 \times
10^{-4}$, $n = 207$); E26 protein (spectral counts) $r = +0.025$;
\emph{E27 protein (quantitative triplicates) $r = -0.083$} ($p =
0.12$, CI $[-0.188, +0.033]$, permutation $p = 0.115$). The E26
conclusion --- transcript association present, protein association
absent, on the same genes --- \emph{replicates} with high-quality
quantitative proteomics, and the attenuation/saturation
explanation for the protein null is rejected: triplicate
measurement (median CV $\approx 15\%$), full dynamic range, and a
noise floor of $0.18$ leave no room for a hidden positive gradient
of the transcript size. Sensitivities: significant changers only
($q < 0.05$, $n = 277$) $r = -0.148$ ($p = 0.014$) --- conditioned
on changing at all, higher-$\kappa_V$ proteins change \emph{less};
mean triplicate CV $\leq 20\%$ ($n = 254$) $r = -0.017$;
excluding b2097 $r = -0.084$; the no-replicate dataset 1 (Table
S7, $n = 333$) $r = -0.126$ ($p = 0.022$). Across every
specification the protein gradient is null-to-negative, never
positive.

\emph{[R-profile] All 22 conditions.} No carbon-depletion,
carbon-limitation, or stress condition shows a positive protein
$\kappa_V$ gradient (stationary $-0.073/-0.036$; chemostats
$+0.089/+0.014/-0.042/-0.067$ at $\mu = 0.5 \to 0.12$ --- a
\emph{declining} profile, the opposite of the transcript layer's
starvation-depth gradient; NaCl/$42^{\circ}$C/pH~6
$-0.071/-0.094/-0.096$). The only significant positives are two
switch conditions (glycerol+AA $+0.134$, pyruvate $+0.138$, both
$p < 0.02$) --- the same attenuated switch-class signal the
transcript layer shows (E25) --- and the switch-class max metric is
$+0.040$ (Pearson, NS; Spearman $+0.141$, $p = 0.007$). LB (out of
class) $+0.091$ (NS).

\emph{[R-tp] Coupling, cross-experiment.} Pairing each gene's
signed E24 exhaustion fold-change with its signed Schmidt
stationary fold-change (cross-experiment: microarray vs.\ LC-MS,
MG1655 vs.\ BW25113, different defined media, hours- vs.\
days-scale stationary harvest --- stated), the coupling by
$\kappa_V$ tertile is $+0.150$ (NS, $p = 0.10$), $+0.353$ ($p =
6.7 \times 10^{-5}$), $+0.240$ ($p = 7.7 \times 10^{-3}$):
significant in the mid and high strata, null in the low,
directionally consistent with E26's within-experiment rise
($+0.088/+0.164/+0.212$) but \emph{not monotone}; the E25-GSE-dT
cross-experiment variant is null ($+0.024$). Cross-experiment
pairing is the weaker instrument, and the discrepancy is stated
rather than smoothed.

\emph{[R-magnitude] Magnitudes: parity, not suppression.} On the
same $366$ genes the mean protein response is $1.26$ ($\log_2$)
against the E24 transcript metric's $1.42$ (ratio $0.89$); by
$\kappa_V$ tertile the transcript means rise ($0.90 \to 1.52 \to
1.84$) while the protein means are $\kappa$-flat, slightly
declining ($1.50 \to 1.20 \to 1.11$), so the $|\Delta P|/|\Delta
T|$ implementation ratio \emph{falls} across strata ($2.49 \to
1.10 \to 1.06$; high-vs-low MWU $p = 1.0$ against an increase).
Two readings follow. First, the E26 magnitude gap ($5.29$ vs
$1.26$) was an artifact of the zero-inflated GSE TPM metric, not a
property of the biology: proteins change about as much as
transcripts on matched log-ratio scales. Second, and more
precisely, what is buffered is not protein \emph{magnitude} but
the $\kappa_V$-\emph{graded organization} of the response: graded
transcripts, flat proteins.

\emph{[R-stability] The stability claim, corrected.} The E26
within-top-tertile stability gradient ($r = -0.427$, spectral
counts) \emph{does not replicate}: with quantitative triplicates
it is $+0.114$ ($p = 0.21$), while the same tertile's transcript
gradient on the E24 metric is $+0.266$ ($p = 3.1 \times 10^{-3}$)
--- the most sensitive genes' transcripts respond hardest while
their proteins do not decline. The strong E26 value was therefore
most plausibly a spectral-count saturation artifact for the most
abundant (highest-$\kappa_V$) machinery. What \emph{does} survive
is the weaker, condition-independent form: the internal batch
control itself shows $|\Delta P|$ decreasing with $\kappa_V$
($-0.119$, $p = 0.023$) --- high-$\kappa_V$ proteins are the least
variable even across replicate cultures --- and the
exhaustion-class gradient ($-0.083$) is no stronger than that
baseline, i.e.\ carbon exhaustion adds no $\kappa$-graded protein
response on top of intrinsic stability.

\emph{[R-zero] The zero-$\kappa_V$ control.} At the protein layer
the panel does \emph{not} respond more than zero-$\kappa_V$ genes
(mean max $|\log_2 \Delta P|$: $1.26$ vs.\ $1.63$,
$n_{\mathrm{zero}} = 526$, MWU $p \approx 1$), whereas at the
transcript layer the same contrast was decisive (E24: $1.32$ vs
$0.90$, $p = 7.8 \times 10^{-22}$) --- a further localization of
the $\kappa_V$ signal to the transcript layer.

\textbf{Verdict:} the replication \emph{confirms the core} --- on
the same genes, the $\kappa$--transcript association is present on
two platforms while the $\kappa$--protein association is absent
under carbon exhaustion with quantitative triplicate proteomics
(the attenuation explanation excluded) --- and it \emph{corrects
two secondary E26 readings}: the ``most stable machinery''
top-tertile gradient was a saturation artifact (replaced by the
weaker batch-level stability, $-0.119$), and ``protein capacity is
buffered'' is imprecise --- protein response magnitudes are
comparable to transcript magnitudes; what is transcript-specific
is the $\kappa_V$-graded \emph{organization}. Refined statement:
$\kappa_V$ predicts the transcriptional reporting of carbon
exhaustion with graded magnitude across the metabolic network,
while the protein layer responds abundantly but without
$\kappa_V$-graded organization --- correlational throughout, with
cross-strain (BW25113), cross-medium, chronic-vs-acute, and
single-proteome-source caveats stated. A second independent
proteome source (or targeted PRM/SRM quantification of the
highest-$\kappa_V$ machinery under acute starvation) remains the
natural next escalation.

\textbf{Artifacts.} Scripts: \texttt{e27\_prepare\_schmidt.py}
(table extraction), \texttt{e27\_plot.py} (figure), and
\texttt{novelty\_v20\_e27\_schmidt\_replication.py} (analysis);
data \texttt{data/schmidt2016/} (S8/S6/S7 CSVs, provenance
README, PRECISE-1K metadata scan). Outputs:
\texttt{novelty\_v20\_e27\_schmidt\_replication.\{csv,
png,txt,results.json\}} in \texttt{download/} (the CSV joins,
per panel gene: $\kappa_V$, the Schmidt protein fold-changes by
class, the E24/E25 transcript metrics, and the E26
spectral-count metric).

\section{Main Proposition}\label{sec:mainprop}"""

apply("P6 insert v20 subsection", OLD_P6, NEW_P6)

# ----------------------------------------------------------------------
# P7: abstract -- add the E27 replication numbers
# ----------------------------------------------------------------------
OLD_P7 = r"""phosphorus limitation), and does not
propagate to protein abundance changes (matched tandem-MS proteomics,
$r \approx +0.01$), localizing the $\kk$ signal to the regulatory
layer."""

NEW_P7 = r"""phosphorus limitation), and does not
propagate to protein fold-changes (matched tandem-MS proteomics,
$r \approx +0.01$; replicated on an independent $22$-condition
quantitative triplicate proteome, $r = -0.08$ at $n = 366$, where
protein and transcript response magnitudes are comparable), 
localizing the $\kk$ signal to the regulatory layer."""

apply("P7 abstract replication numbers", OLD_P7, NEW_P7)

# ----------------------------------------------------------------------
# P8: introduction contribution item -- extend to E24-E27 / v17-v20
# ----------------------------------------------------------------------
OLD_P8 = r"""and does not extend to protein
fold-changes on the matched proteome ($r \approx +0.01$ on the
$169$-gene subset where the transcript association is $+0.42$),
localizing the association to the regulatory layer
(Studies~E24--E26, Sections~\ref{sec:novelty-v17}
--\ref{sec:novelty-v19})."""

NEW_P8 = r"""and does not extend to protein
fold-changes on the matched proteome ($r \approx +0.01$ on the
$169$-gene subset where the transcript association is $+0.42$;
replicated on the Schmidt et al.\ $22$-condition quantitative
triplicate proteome, $r = -0.08$ on the $366$-gene intersection,
with protein and transcript magnitudes comparable and the graded
organization transcript-specific), localizing the association to
the regulatory layer (Studies~E24--E27,
Sections~\ref{sec:novelty-v17}--\ref{sec:novelty-v20})."""

apply("P8 intro contribution item extended", OLD_P8, NEW_P8)

# ----------------------------------------------------------------------
# P9: conclusion -- replication + magnitude-parity correction
# ----------------------------------------------------------------------
OLD_P9 = r"""bounded by null controls (carbon-source switching, phosphorus
limitation), and decoupled from protein abundance changes on the
matched proteome ($r \approx +0.01$ where the transcript
association is $+0.42$) --- a regulatory-layer signature, stated
throughout as correlational
(Sections~\ref{sec:novelty-elevation}--\ref{sec:novelty-v19})."""

NEW_P9 = r"""bounded by null controls (carbon-source switching, phosphorus
limitation), and decoupled from protein fold-changes on the
matched proteome ($r \approx +0.01$ where the transcript
association is $+0.42$; replicated on the independent
$22$-condition quantitative triplicate proteome of Schmidt et
al., $r = -0.08$ at $n = 366$, with protein and transcript
response \emph{magnitudes} comparable --- the $\kk$-graded
organization is transcript-layer-specific, not a magnitude
effect) --- a regulatory-layer signature, stated throughout as
correlational
(Sections~\ref{sec:novelty-elevation}--\ref{sec:novelty-v20})."""

apply("P9 conclusion replication + correction", OLD_P9, NEW_P9)

# ----------------------------------------------------------------------
# P10: data availability -- Schmidt + PRECISE-1K scan provenance
# ----------------------------------------------------------------------
OLD_P10 = r"""  \texttt{data/gse64021/README.md}), and the PaxDb v6.1
  \emph{E.~coli} integrated whole-organism proteome (CC BY 4.0;
  \texttt{data/paxdb/README.md}).
\end{itemize}"""

NEW_P10 = r"""  \texttt{data/gse64021/README.md}), and the PaxDb v6.1
  \emph{E.~coli} integrated whole-organism proteome (CC BY 4.0;
  \texttt{data/paxdb/README.md}). The E27 replication uses the
  Schmidt et al.\ 2016 condition-dependent proteome (Nat.\
  Biotechnol.\ 34:104--110; raw data PRIDE PXD000498; processed
  supplementary tables retrieved from PMC4888949 via the Europe
  PMC REST supplementary-files endpoint --- sha256 and per-file
  provenance in \texttt{data/schmidt2016/README.md}; the 17~MB
  workbook and 24~MB zip are not committed and are re-downloadable
  per the README; the extracted analysis tables
  \texttt{schmidt2016\_s8\_fc.csv}, \texttt{schmidt2016\_s6\_map.csv},
  and \texttt{schmidt2016\_s7\_fc.csv} are committed). The
  PRECISE-1K metadata scan (all $1{,}035$ samples, retrieved from
  \texttt{github.com/SBRG/precise1k}) is archived as
  \texttt{data/schmidt2016/precise1k\_metadata\_qc\_scan.csv} and
  documents the absence of carbon-depletion conditions in that
  compendium.
\end{itemize}"""

apply("P10 data availability Schmidt provenance", OLD_P10, NEW_P10)

# ----------------------------------------------------------------------
with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\n{orig_len} -> {len(src)} chars (+{len(src)-orig_len})")
print(f"{n_applied}/10 patches applied")
