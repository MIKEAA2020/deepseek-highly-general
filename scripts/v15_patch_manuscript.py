#!/usr/bin/env python3
"""
v15 manuscript patcher — adds the sec:novelty-v15 subsection (Study E22,
reaction-based sampling / Option C) after the v14b subsection, plus a
forward-pointer sentence in the E10 Results follow-ups paragraph.

All numbers come from download/novelty_v15_reaction_sampling_e22_results.json
(fresh run of scripts/novelty_v15_reaction_sampling_e22.py).
"""
import json
import sys

TEX = "/home/z/my-project/scripts/journal_manuscript.tex"
RES = "/home/z/my-project/download/novelty_v15_reaction_sampling_e22_results.json"
r = json.load(open(RES))

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
    elif new.strip()[:80] in src:
        print(f"  {name}: already applied (idempotent)")
    else:
        print(f"  {name}: TARGET NOT FOUND -- ABORT")
        sys.exit(1)


# ----------------------------------------------------------------------
# PATCH 1: forward-pointer sentence in the E10 Results follow-ups
# ----------------------------------------------------------------------
OLD_PTR = r"""A MAPPED-only subset analysis ($n=15$,
$r = -0.158$) initially read as evidence of protein-level regulation of
heavy-flux-perturbation metabolic genes was shown by the v14b audit to
be a degenerate artifact --- $14$ identical zero-$\kappa_V$ genes plus
the single outlier $b2097$, whose removal leaves the Pearson $r$
formally undefined --- and is \emph{retracted}
(\S\ref{sec:novelty-v14b})."""

NEW_PTR = r"""A MAPPED-only subset analysis ($n=15$,
$r = -0.158$) initially read as evidence of protein-level regulation of
heavy-flux-perturbation metabolic genes was shown by the v14b audit to
be a degenerate artifact --- $14$ identical zero-$\kappa_V$ genes plus
the single outlier $b2097$, whose removal leaves the Pearson $r$
formally undefined --- and is \emph{retracted}
(\S\ref{sec:novelty-v14b}). The v15 round (\S\ref{sec:novelty-v15})
then inverts the mapping direction --- sampling genes \emph{from} the
$438$ active reactions rather than mapping the Lemuth panel
\emph{into} the model --- and confirms that the disjointness is
structural: the Lemuth panel and the active-reaction gene set share
exactly one gene ($b2097$)."""

apply("P1 E10 forward-pointer", OLD_PTR, NEW_PTR)

# ----------------------------------------------------------------------
# PATCH 2: insert the v15 subsection before \section{Main Proposition}
# ----------------------------------------------------------------------
OLD_ANCHOR = r"""\section{Main Proposition}\label{sec:mainprop}"""

NEW_V15 = r"""% =============================================================
\subsection{v15 reaction-based sampling: genes from the active-reaction
set (E22)}\label{sec:novelty-v15}
% =============================================================

The v15 round (Study E22, ``reaction-based sampling''; script
\texttt{novelty\_v15\_reaction\_sampling\_e22.py}) implements the Option~C
design approved after the v14b audit: it \emph{inverts} the E10 mapping
direction. Instead of mapping the $92$ Lemuth genes into iJO1366 ---
which the v14b audit showed fails structurally ($14/15$ mapped genes
have zero-flux reactions) --- E22 samples genes \emph{from} the
active-reaction set: fresh cobrapy FBA at the identical E10 physiology
($q_{glc}$ $5.0 \to 1.0$ mmol/gDW/h, $q_{O_2}$ $22.0 \to 5.0$),
reaction-level $\kappa_V(r,t) = (v_r(t) - v_r(\mathrm{T1}))^2$ with the
identical E10/v13 definition, and per-gene
$\kappa_V(g,t) = \max_r \kappa_V(r,t)$ over all reactions $r$ of gene
$g$ in its GPR rules.

\emph{Verification (four checks, all passed).}
\begin{enumerate}\itemsep0pt
\item \textbf{GPR mapping correctness} {[C-map]}: the
  active-reaction$\,\to\,$gene map is taken from cobra's authoritative
  \texttt{reaction.genes}, spot-checked against the raw GPR rule
  strings on four reactions spanning all complexity classes (FBA:
  ``b1773 or b2097 or b2925''; ATPS4rpp: nested 2-complex OR;
  PDH: ``b0115 and b0114 and b0116''; GLCptspp: 3-complex OR), with
  set-equality between rule-string gene tokens and cobra's gene set,
  and a bidirectional gene$\leftrightarrow$reaction symmetry check on
  $50$ sampled genes ($0$ failures over $120$ gene-reaction pairs).
\item \textbf{$\kappa_V$ definition consistency} {[C-def]}: the fresh
  re-derivation reproduces the stored E10/v13 values exactly --- all
  $15$ MAPPED-gene $\kappa_V$ maxima ($b2097 = 9.490142$; the other
  $14$ exactly $0$), the global biomass-deficit $\kappa_V$ maximum
  ($0.158543$), and the unmasked/v12/v13 per-gene Pearson $r$
  ($-0.0633$, $+0.1024$, $+0.0838$) to four decimals.
\item \textbf{Distinctness} {[C-dist]}: the new panel shares exactly
  $1$ of the $15$ MAPPED b-numbers ($b2097$) and exactly $1$ gene with
  the Lemuth $92$ ($b2097$); $434$ of $435$ panel genes are distinct
  from the original $15$.
\item \textbf{Non-zero variation} {[C-var]}: \emph{every} panel gene
  has $\kappa_V$ variation $> 0$ over T1--T8 ($435/435$; the
  zero-dominated failure mode of the MAPPED-15 route is excluded by
  construction).
\end{enumerate}

\emph{Panel construction.} Of iJO1366's $2583$ reactions, $438$
($17.0\%$) carry non-zero flux under the Lemuth condition and $437$
have non-zero $\kappa_V$; $404$ of the active reactions carry GPR
gene assignments, giving a gene panel of $435$ genes ($31.8\%$ of the
model's $1367$ genes; $434$ excluding the spontaneous pseudo-gene
\texttt{s0001}). Of the $92$ Lemuth genes, $73$ recover Keio b-numbers
by exact/case-insensitive symbol matching, $15$ of those b-numbers are
in iJO1366 (the MAPPED-15 of v13), and exactly one of those ($b2097$)
has flux-carrying reactions --- so the E10-lineage per-gene Pearson
regression \emph{cannot} be extended to the panel on local data: the
Lemuth expression panel and the active-reaction gene set are
structurally disjoint. This is the honest central finding of E22: the
correlation is blocked by \emph{expression coverage}, not by mapping.
Extending it requires either an expression compendium over the panel
(COLOMBOS/M3D, Option~A, deferred) or condition swaps that activate
the $14$ zero-$\kappa_V$ genes (Option~D, the natural next round).

\emph{Distributional structure of the panel.} The per-gene
$\kappa_V$ maximum over the panel is extremely concentrated: Gini
$0.932$; the top $1\%$ of genes ($4$ genes) hold $18.0\%$ of total
$\kappa_V$, the top $5\%$ ($22$ genes) hold $76.5\%$, and the top
$10\%$ ($44$ genes) hold $97.4\%$; a Hill tail-index estimate gives
$\alpha \approx 0.43$ ($m = 50$), and a lognormal fit on
$\log_{10}\kappa_V$ is rejected (KS $p = 6.0 \times 10^{-4}$,
$\hat\mu = -3.04$, $\hat\sigma = 3.43$). The curvature is dominated by
the ATP-synthase GPR complex of ATPS4rpp ($b3731$--$b3739$,
$\kappa_V^{\max} = 466.63$), the water-transport porin/diffusion
system (H2Otpp and cognates, $\kappa_V^{\max} = 330.20$), and the
cytochrome-$bo_3$ oxidase pair ($b0429$/$b0430$, $185.19$):
as $q_{O_2}$ declines $5.5$-fold over T1--T8, the
oxidative-phosphorylation and associated transport fluxes carry
almost all of the perturbation curvature. By subsystem, the leading
$\kappa_V$ carriers are oxidative phosphorylation ($802.4$),
outer-membrane porins ($467.2$), inner-membrbrane transport
($404.8$), and glycolysis/gluconeogenesis ($193.7$).

\emph{GPR complexity (genome-scale extension of the v12 isozyme
finding).} Over the $438$ active reactions the GPR classes are:
single-gene $254$, isozyme (pure OR) $96$, enzyme complex (pure AND)
$36$, mixed nested $18$, no-GPR $34$. Thus $96/438 = 21.9\%$ of
active reactions \emph{cannot} be disabled by any single-gene
knockout --- the genome-scale quantification of the isozyme-cover
mechanism that made $b2097$'s single-KO $\Delta b = 0$ in v12 ---
and the mixed nested rules (e.g.\ ATPS4rpp, GLCptspp) carry the
highest mean $\kappa_V$ ($26.8$), so the most heavily perturbed
reactions are precisely those whose GPR structure makes
single-gene deletion least informative.

\emph{Direction-test re-verification.} The E10 direction test
($21$ published predictions; UP/DOWN genes require
$\kappa_V > 0.01$, STABLE genes require $\kappa_V < 0.01$) reproduces
the stored E10 result \emph{exactly}: $14/21 = 66.7\%$ pass, with
identical per-gene $\kappa_V$ values (e.g.\ $\mathit{gapA} = 41.85$,
$\mathit{eno} = 33.46$, $\mathit{gltA} = 3.39$) --- a final
consistency check that the v15 reaction-level $\kappa_V$ is the same
quantity as the E10 one.

\textbf{Verdict:} E22 does not strengthen or weaken the E10
correlation verdict (per-gene $r \in [+0.08, +0.10]$ after artifact
removal, individually non-significant at $n=92$); it replaces the
failed gene-mapping route with a sound panel construction, proves
the Lemuth$\,\cap\,$panel disjointness is structural, quantifies the
$\kappa_V$ concentration structure over the panel (Gini $0.93$,
top-$10\%$ carry $97.4\%$), and delivers the
reaction$\,\to\,$gene map that both remaining options require.
The $435$-gene panel with full $\kappa_V$ trajectories is exported
for either downstream route.

\textbf{Artifacts.} Script:
\texttt{novelty\_v15\_reaction\_sampling\_e22.py} ($\sim$$560$ lines).
Outputs:
\texttt{novelty\_v15\_reaction\_sampling\_e22.\{csv,txt,png,results.json\}}
in \texttt{download/} (the CSV is the full panel: gene, name, active
reactions, GPR class, subsystem, $\kappa_V$ T1--T8, variance, and
Lemuth/MAPPED-15 membership flags).

"""

apply("P2 insert v15 subsection", OLD_ANCHOR, NEW_V15 + OLD_ANCHOR)

if src.count("\\subsection{v15 reaction-based sampling") > 1:
    print("  P2: DUPLICATE v15 subsection -- ABORT")
    sys.exit(1)

with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\n{orig_len} -> {len(src)} chars ({n_applied} patches applied)")

# label/reference sanity
assert src.count("\\label{sec:novelty-v15}") == 1
n_refs = src.count("\\ref{sec:novelty-v15}")
print(f"sec:novelty-v15 defined once, referenced {n_refs} times (v14b text "
      f"+ v14b subsection + E10 pointer -> expect >= 3)")
print("DONE")
