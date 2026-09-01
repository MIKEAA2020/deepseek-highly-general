#!/usr/bin/env python3
"""
v14b manuscript patcher — CRITICAL CORRECTION ROUND.

Removes two false statements from journal_manuscript.tex that were
introduced by the v13 narrative and left standing by the v14 correction:

  F1 (method description): the v13 paragraph claimed the Keio fallback
     computes per-gene kappa_V "via the iJO1366 reaction whose GPR rule
     most overlaps the recovered b-number, or ... via a reaction-level
     proxy drawn from the gene's curated functional annotation in
     EcoCyc". FALSE on both counts: kappa_V is the max over ALL GPR
     reactions of the recovered b-number, and there is NO EcoCyc proxy
     (unmatched genes keep the global biomass-deficit fallback).

  F2 (result interpretation): the v13 paragraph claimed the patch
     "replaces their zero with per-gene heterogeneous kappa_V values
     drawn from their actual iJO1366 GPR reactions", that v13's -0.019
     delta vs v12 is due to "heterogeneous ... noise", and that the
     MAPPED-only r = -0.158 is "a real biological signal" of
     protein-level regulation. ALL FALSE: 14/15 mapped genes' reactions
     carry ZERO flux under the Lemuth condition (kappa_V = 0, same
     end-state as the v12 mask); v12 vs v13 differ at exactly one gene
     (b2097); the MAPPED-only r is a degenerate artifact (14 identical
     zeros + 1 outlier; drop the outlier and Pearson r is undefined).

Also fixes the echo of F2 in the E10 Results follow-ups paragraph and
adds a new subsection sec:novelty-v14b documenting the audit.

All replacement numbers come from the first-principles verification
(v14b_verify_claims.py + v14b_reconstruct_kappa.py, both of which
reproduce the stored r values exactly).
"""
import re
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
            print(f"  {name}: expected {count} occurrence(s), found "
                  f"{src.count(old)} -- ABORT")
            sys.exit(1)
        src = src.replace(old, new)
        n_applied += 1
        print(f"  {name}: APPLIED")
    elif new.strip()[:80] in src:
        print(f"  {name}: already applied (idempotent)")
    else:
        print(f"  {name}: TARGET NOT FOUND -- ABORT")
        sys.exit(1)


# ======================================================================
# PATCH 1 -- v13 paragraph: replace the false narrative block
# (from 'The v13 round (Study E21,' to the end of the paragraph)
# ======================================================================
OLD_V13 = r"""The v13 round (Study E21, ``E10 v2 --- Keio b-number fallback'') replaces
that homogeneous fallback with a per-gene heterogeneous signal: the $77$
previously-unmapped gene symbols are re-mapped against the Tomoya Baba
2006 Keio supplementary table MOESM5 (which tabulates ECK number, gene
symbol, JW ID, and b-number for the full Keio collection), and each
recovered b-number is used to compute a per-gene $\kappa_V$ via the
iJO1366 reaction whose gene-protein-reaction (GPR) rule most overlaps the
recovered b-number, or, where no GPR match exists (the flagella and
chemotaxis genes that iJO1366 explicitly excludes), via a reaction-level
proxy drawn from the gene's curated functional annotation in EcoCyc.
Re-running the E10 per-gene Pearson regression with this Keio-fallback
$\kappa_V$ yields $r = +0.0838$ (95\% CI $[-0.12, +0.28]$, $n=92$,
two-tailed $p \approx 0.43$ under the Fisher-z transform), an
\emph{independent} sign flip from the unmasked $-0.0633$ ($\Delta =
+0.147$ above the unmasked baseline, with the same positive sign as
v12). Whereas the v12 mask is a binary filter that \emph{zeroes} the
$\kappa_V$ of the 15 non-perturbing metabolic genes, the v13 patch
\emph{replaces} their zero with per-gene heterogeneous $\kappa_V$ values
drawn from their actual iJO1366 GPR reactions (e.g., $b2480 \to$ THIORDXi
peroxide stress, $b4219 \to$ METSOXR1 methionine sulfoxide, $b3908 \to$
SPODM superoxide dismutase, $b1197 \to$ TREHpp trehalose hydrolysis,
$b1897 \to$ TRE6PP trehalose-6-phosphate synthase, $b0758 \to$ UGLT
galactose metabolism, $b1226 \to$ NO3R1pp/NO3R2pp nitrate respiration,
$b3450 \to$ G3PSabcpp glycerol-3-phosphate transport). The v13 $r$ is
slightly \emph{below} the v12 $r$ ($\Delta = -0.019$ versus v12); this is
biologically interpretable because the heterogeneous per-gene $\kappa_V$
values of the 14 newly-mapped metabolic genes introduce modest noise
relative to v12's clean binary zeroing. \textbf{Verdict:} the v12
STRENGTHENED verdict on E10 is \textbf{independently confirmed} by v13;
the Keio b-number fallback provides an alternative, biologically richer
pathway to the same sign-flip conclusion as v12, with both variants
placing $r$ in the same $[+0.08, +0.10]$ weakly-positive band well above
the unmasked $-0.0633$ baseline. \textbf{Counterintuitive MAPPED-only
finding:} restricting to the $n=15$ MAPPED metabolic genes alone, the
per-gene-max Pearson $r$ is \emph{negative} ($-0.158$, $n=15$; 95\% CI
$[-0.62, +0.39]$, two-tailed $p \approx 0.58$), consistent with the
interpretation that metabolic genes with the largest flux perturbations
are tightly regulated at the protein level (less transcriptional
compensation needed), while small-perturbation metabolic genes rely more
on transcriptional response --- a real biological signal that warrants
follow-up on a metabolic-gene-only expression compendium. \textbf{Honest
limitation:} at $n=92$ genes neither the v12 nor the v13 per-gene Pearson
$r$ is individually significant at $\alpha=0.05$ under the Fisher-z
transform (95\% CI for v12: $[-0.10, +0.30]$, $p \approx 0.33$; for v13:
$[-0.12, +0.28]$, $p \approx 0.43$; both intervals include zero); the
consolidation verdict therefore rests on the sign-flip consistency
across two methodologically distinct $\kappa_V$-refinement paths
(unmasked $-0.0633 \,\to\,$ gene-mask $+0.1024$; unmasked $-0.0633 \,\to\,$
b-number fallback $+0.0838$) rather than on a single-variant
significance test, and a permutation null would not be expected to reach
$\alpha=0.05$ at this sample size."""

NEW_V13 = r"""The v13 round (Study E21, ``E10 v2 --- Keio b-number fallback'') tightens
the gene-to-reaction mapping: the $77$ previously-unmapped gene symbols
are re-mapped against the Tomoya Baba 2006 Keio supplementary table
MOESM5 (which tabulates ECK number, gene symbol, JW ID, and b-number for
the full Keio collection); $14$ of them recover b-numbers present in
iJO1366 (bcp/b2480, caiC/b0037, galT/b0758, msrA/b4219, narJ/b1226,
otsB/b1897, proV/b2677, proW/b2678, sodA/b3908, treA/b1197, ugpC/b3450,
yeaA/b1778, yehX/b2129, yehY/b2130), expanding the MAPPED set from $1$
to $15$ and shrinking the GLOBAL proxy set from $91$ to $77$. Each
recovered b-number's per-gene $\kappa_V$ is computed exactly as for the
original direct match --- the max over the $\kappa_V$ of the iJO1366
reactions in its GPR rule --- while genes with no iJO1366 b-number
retain the global biomass-deficit proxy. Re-running the E10 per-gene
Pearson regression with this Keio-fallback $\kappa_V$ yields $r =
+0.0838$ (95\% CI $[-0.12, +0.28]$, $n=92$, two-tailed $p \approx
0.43$ under the Fisher-z transform), a sign flip from the unmasked
$-0.0633$ ($\Delta = +0.147$) with the same positive sign as v12.

\medskip
\emph{v14b audit finding (correction).} A first-principles re-derivation
of the v13 pipeline (fresh cobrapy FBA at the published Lemuth/Ishii
physiology values, fresh GPR lookup, fresh Keio MOESM5 parsing; scripts
\texttt{v14b\_verify\_claims.py} and
\texttt{v14b\_reconstruct\_kappa.py}, which reproduce the stored
unmasked/v12/v13 $r$ values of $-0.0633/+0.1024/+0.0838$ exactly) shows
that the sign flip is \textbf{not} driven by per-gene
\emph{heterogeneous} $\kappa_V$ values, as this paragraph previously
claimed, and the previously-quoted EcoCyc annotation proxy for
GPR-unmatched genes does not exist in the pipeline. Under
glucose-limited aerobic FBA only $438$ of iJO1366's $2583$ reactions
($17.0\%$) carry non-zero flux, and every reaction in the GPR rules of
the $14$ newly-mapped genes is among the $2145$ inactive ones:
THIORDXi, METSOXR1, METSOXR2, SPODM, TREHpp, TRE6PP, UGLT,
NO3R1pp/NO3R2pp, the carnitine/betaine transporters of caiC, proV and
proW, and the glycerol-3-phosphate transporters of ugpC all carry
exactly zero flux at every one of T1--T8, so their $\kappa_V$ is $0$ at
every time point --- the same end-state the v12 mask produces by binary
zeroing, reached by an independent route (reaction inactivity rather
than $\Delta b = 0$ isozyme logic). The two rounds differ at exactly
one gene, $b2097$/$\mathit{fbaA}$: v12 zeroes its $\kappa_V$ (per-gene
max $\Delta b = 0$ under single-gene KO, GPR ``b1773 or b2097 or
b2925''), whereas v13 retains its genuine reaction-derived $\kappa_V$
(max $= 9.49$ from the FBA reaction, which does carry flux); the
$-0.019$ difference between the v12 and v13 $r$ values is attributable
entirely to this single gene. \textbf{Verdict (corrected):} v12 and v13
are \emph{structural corroboration} rather than \emph{methodological
independence}: both remove the spurious non-zero global-proxy
$\kappa_V$ that the unmasked E10 assigned to Lemuth metabolic genes
whose reactions do not respond under the Lemuth condition, they agree
on that removal for $14$ of the $15$ mapped genes, and they differ only
on whether $b2097$'s genuine reaction-derived $\kappa_V$ is retained.
\textbf{Retraction of the ``counterintuitive MAPPED-only finding'':}
restricting to the $n=15$ MAPPED metabolic genes gives a per-gene-max
Pearson $r$ of $-0.158$ ($n=15$; 95\% CI $[-0.62, +0.39]$, two-tailed
$p \approx 0.58$), but this number is a degenerate small-sample
artifact, not a biological signal: $14$ of the $15$ genes have
identically zero $\kappa_V$ (log$_{10}$-clipped to $-12$) and the
single remaining gene ($b2097$) sits at high $\kappa_V$ with
below-average $|\log_2 \mathrm{FC}|$ ($0.44$ versus mean $0.59$ of the
fourteen zeros); removing that one point leaves zero variance in $x$,
so the Pearson $r$ is formally undefined on the remaining $14$. The
earlier interpretation of this $r = -0.158$ as evidence of protein-level
regulation of heavy-flux-perturbation metabolic genes is
\emph{retracted}; it rested on the false premise of heterogeneous
$\kappa_V$ within the MAPPED set. \textbf{Honest limitation:} at $n=92$
genes neither the v12 nor the v13 per-gene Pearson $r$ is individually
significant at $\alpha=0.05$ under the Fisher-z transform (95\% CI for
v12: $[-0.10, +0.30]$, $p \approx 0.33$; for v13: $[-0.12, +0.28]$,
$p \approx 0.43$; both intervals include zero); the sign-flip verdict
therefore rests on the consistent removal of the same global-proxy
artifact across two masking routes (unmasked $-0.0633 \,\to\,$
gene-mask $+0.1024$; unmasked $-0.0633 \,\to\,$ b-number fallback
$+0.0838$) rather than on a single-variant significance test, and a
permutation null would not be expected to reach $\alpha=0.05$ at this
sample size. The structural cause of the depressed Pearson $r$ --- the
$77/92$ global-proxy dominance --- is unaffected by this correction;
the v15 round (\S\ref{sec:novelty-v15}) addresses it head-on by
sampling genes \emph{from the active-reaction set} instead of mapping
Lemuth genes \emph{into} it."""

apply("P1 v13 paragraph correction", OLD_V13, NEW_V13)

# ======================================================================
# PATCH 2 -- E10 Results follow-ups paragraph (two echo fixes)
# ======================================================================
OLD_ECHO = r"""Neither variant is individually significant at $\alpha=0.05$ at
$n=92$, but the sign-flip \emph{consistency} across two
methodologically distinct refinement paths (binary zeroing via mask
vs.\ per-gene heterogeneous $\kappa_V$ via Keio GPR mapping)
strengthens the original E10 verdict from WEAK-TO-MODERATE to
WEAK-TO-MODERATE-WITH-CONFIRMED-SIGN-FLIP. The original $91/92$
global-proxy dominance (the structural cause of the depressed Pearson
$r$) is also reduced by the v13 patch to $77/92$ (i.e., $15/92$ MAPPED
via GPR after Keio fallback). A counterintuitive MAPPED-only finding
($n=15$, $r = -0.158$) suggests heavy-flux-perturbation metabolic genes
are regulated at the protein level rather than transcriptionally; this
warrants follow-up on a metabolic-gene-only expression compendium."""

NEW_ECHO = r"""Neither variant is individually significant at $\alpha=0.05$ at
$n=92$, but the sign-flip \emph{consistency} across two routes that
remove the same global-proxy artifact (binary $\Delta b = 0$ zeroing
via the v12 mask vs.\ reaction-inactivity zeroing via the v13 GPR
mapping; the v14b audit, \S\ref{sec:novelty-v14b}, shows both routes
assign $\kappa_V = 0$ to the same $14$ metabolic genes and differ only
at $b2097$) strengthens the original E10 verdict from WEAK-TO-MODERATE
to WEAK-TO-MODERATE-WITH-CONFIRMED-SIGN-FLIP. The original $91/92$
global-proxy dominance (the structural cause of the depressed Pearson
$r$) is also reduced by the v13 patch to $77/92$ (i.e., $15/92$ MAPPED
via GPR after Keio fallback). A MAPPED-only subset analysis ($n=15$,
$r = -0.158$) initially read as evidence of protein-level regulation of
heavy-flux-perturbation metabolic genes was shown by the v14b audit to
be a degenerate artifact --- $14$ identical zero-$\kappa_V$ genes plus
the single outlier $b2097$, whose removal leaves the Pearson $r$
formally undefined --- and is \emph{retracted}
(\S\ref{sec:novelty-v14b})."""

apply("P2 E10 Results echo correction", OLD_ECHO, NEW_ECHO)

# ======================================================================
# PATCH 3 -- insert the v14b subsection after the v13 subsection
# (before \section{Main Proposition})
# ======================================================================
OLD_ANCHOR = r"""\section{Main Proposition}\label{sec:mainprop}"""

NEW_V14B_SUBSEC = r"""% =============================================================
\subsection{v14b correction round: audit of the v13 MAPPED set
(E10 v2)}\label{sec:novelty-v14b}
% =============================================================

The v14b round is a \emph{correction} round, not a new elevation. A
first-principles re-derivation of the v13 pipeline --- fresh cobrapy
FBA at the published Lemuth/Ishii physiology values ($q_{glc}$
declining $5.0 \to 1.0$ mmol/gDW/h, $q_{O2}$ $22.0 \to 5.0$), fresh
GPR lookup, fresh Keio MOESM5 parsing; scripts
\texttt{v14b\_verify\_claims.py} (claim-by-claim audit) and
\texttt{v14b\_reconstruct\_kappa.py} (full $\kappa_V$ reconstruction)
--- reproduced the stored unmasked/v12/v13 per-gene Pearson $r$ values
($-0.0633$, $+0.1024$, $+0.0838$) to four decimal places and then
audited the $n=15$ MAPPED set. The audit found that the v13 narrative
contained two false statements (a nonexistent EcoCyc proxy in the
method description, and the ``per-gene heterogeneous $\kappa_V$'' /
``real biological signal'' interpretation of the result), which are
corrected in \S\ref{sec:novelty-v13} above. The verified facts are:
\begin{enumerate}\itemsep0pt
\item \textbf{Inactive-reaction bottleneck.} Only $438$ of iJO1366's
  $2583$ reactions ($17.0\%$) carry non-zero flux under the Lemuth
  glucose-limited aerobic FBA condition; $437$ of these have non-zero
  $\kappa_V$ over T1--T8. All reactions in the GPR rules of the $14$
  newly-mapped metabolic genes (bcp, caiC, galT, msrA, narJ, otsB,
  proV, proW, sodA, treA, ugpC, yeaA, yehX, yehY) are among the
  $2145$ inactive reactions, so their $\kappa_V$ is exactly $0$ at
  every time point.
\item \textbf{v12/v13 equivalence up to one gene.} The v12 masked and
  v13 patched per-gene $\kappa_V$ vectors over the $92$ Lemuth genes
  differ at exactly one gene: $b2097$ ($\mathit{fbaA}$; $0$ under v12,
  $9.49$ under v13). The $-0.019$ difference between the v12 and v13
  $r$ values is attributable entirely to this single gene.
\item \textbf{MAPPED-only degeneracy.} The $n=15$ MAPPED-only Pearson
  $r = -0.158$ is a small-sample artifact: $14$ identical
  zero-$\kappa_V$ genes plus one outlier ($b2097$: high $\kappa_V$,
  below-average $|\log_2 \mathrm{FC}|$). Dropping the outlier leaves
  zero variance in the predictor, so the Pearson $r$ is undefined on
  the remaining $14$; no biological signal can be extracted from this
  subset. The protein-level-regulation interpretation is retracted.
\end{enumerate}
\noindent The v12 and v13 rounds therefore constitute
\emph{structural corroboration} (two routes to the same
global-proxy-artifact removal) rather than \emph{methodological
independence}, and the honest characterization of E10 after v14b is:
the per-gene $\kappa_V$ signal over the Lemuth $92$-gene panel is
weakly positive after artifact removal ($r \in [+0.08, +0.10]$,
individually non-significant at $n=92$), with the dominant residual
limitation being the $77/92$ global-proxy fraction and the $17.0\%$
active-reaction coverage of the condition itself. Both limitations
motivate the v15 reaction-based sampling round
(\S\ref{sec:novelty-v15}), which inverts the mapping direction ---
sampling genes \emph{from} the $438$ active reactions rather than
mapping the Lemuth panel \emph{into} the full reaction set --- and
asks whether per-gene $\kappa_V$ heterogeneity across the
active-reaction gene set carries transcript-level signal.

\textbf{Artifacts.} Scripts: \texttt{v14b\_verify\_claims.py},
\texttt{v14b\_reconstruct\_kappa.py},
\texttt{v14b\_restore\_lemuth\_data.py} (rebuilds the Lemuth JSON
input from the archived v1-backup CSV; the JSON is bit-exact against
the archived per-time-point $\log_2$ values). Outputs:
\texttt{v14b\_verification.\{txt,json\}},
\texttt{v14b\_mapped15\_firstprinciples.json},
\texttt{v14b\_mapped15\_audit.\{csv,txt,json\}} (Phase-1 audit),
\texttt{v14b\_options\_evaluation.md} (options A--D evaluation with
the internet-access verification table). The audit verdicts: C1
(14/15 zero-$\kappa_V$) CONFIRMED, C2 (438/2583 active) CONFIRMED,
C3 (outlier artifact) CONFIRMED, C4 (named reactions inactive)
CONFIRMED.

"""

apply("P3 insert v14b subsection", OLD_ANCHOR,
      NEW_V14B_SUBSEC + OLD_ANCHOR)

# NOTE: P3's generic idempotency check (`new.strip()[:80] in src`) can
# fail because the leading '% ====' comment line is common in this
# manuscript. An explicit post-check for the subsection label is done
# below; the patcher must not be re-run after P3 has been applied.
if src.count("\\subsection{v14b correction round: audit") > 1:
    print("  P3: DUPLICATE subsection detected -- run v14b_dedupe_subsection.py")
    sys.exit(1)

# ======================================================================
# Persist
# ======================================================================
with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\n{orig_len} -> {len(src)} chars ({n_applied} patches applied)")
print(f"Wrote {TEX}")

# Sanity: the false statements must be GONE
must_be_gone = [
    "per-gene heterogeneous signal",
    "proxy drawn from the gene's curated functional annotation in EcoCyc",
    "per-gene heterogeneous $\\kappa_V$ values",
    "a real biological signal that warrants",
    "heterogeneous per-gene $\n\\kappa_V$",  # multi-line wrap of F2
]
for s in must_be_gone:
    assert s not in src, f"FALSE STATEMENT STILL PRESENT: {s}"
print("Sanity check: all false-statement markers removed. OK")
