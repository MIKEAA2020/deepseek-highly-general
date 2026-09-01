#!/usr/bin/env python3
"""
v16 manuscript patcher -- adds the sec:novelty-v16 subsection (Study E23,
multi-condition FBA / Option D) after the v15 subsection, updates the v15
forward pointer, and extends the E10-results narrative pointer.

All numbers come from download/novelty_v16_multicondition_e23_results.json
(fresh run of scripts/novelty_v16_multicondition_e23.py).
"""
import json
import sys

TEX = "/home/z/my-project/scripts/journal_manuscript.tex"
RES = "/home/z/my-project/download/novelty_v16_multicondition_e23_results.json"
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
# PATCH 1: v15 forward pointer -> executed as v16
# ----------------------------------------------------------------------
OLD_PTR = r"""Extending it requires either an expression compendium over the panel
(COLOMBOS/M3D, Option~A, deferred) or condition swaps that activate
the $14$ zero-$\kappa_V$ genes (Option~D, the natural next round)."""

NEW_PTR = r"""Extending it requires either an expression compendium over the panel
(COLOMBOS/M3D, Option~A, deferred) or condition swaps that activate
the $14$ zero-$\kappa_V$ genes (Option~D) --- executed as the v16
round (\S\ref{sec:novelty-v16}), which re-activates $13/14$ of them
and computes the cross-condition correlation."""

apply("P1 v15 forward-pointer", OLD_PTR, NEW_PTR)

# ----------------------------------------------------------------------
# PATCH 2: E10-results narrative pointer (extend the v15 sentence)
# ----------------------------------------------------------------------
OLD_E10 = r"""then inverts the mapping direction --- sampling genes \emph{from} the
$438$ active reactions rather than mapping the Lemuth panel
\emph{into} the model --- and confirms that the disjointness is
structural: the Lemuth panel and the active-reaction gene set share
exactly one gene ($b2097$)."""

NEW_E10 = r"""then inverts the mapping direction --- sampling genes \emph{from} the
$438$ active reactions rather than mapping the Lemuth panel
\emph{into} the model --- and confirms that the disjointness is
structural: the Lemuth panel and the active-reaction gene set share
exactly one gene ($b2097$). The v16 round (\S\ref{sec:novelty-v16})
then swaps the FBA \emph{condition} itself: $13$ of the $14$
zero-$\kappa_V$ genes are activated under biologically matched
conditions, and the cross-condition correlation over the seven
endogenously re-activated genes is positive ($r = +0.571$,
sign-stable under leave-one-out) though under-powered at $n=7$."""

apply("P2 E10 narrative pointer", OLD_E10, NEW_E10)

# ----------------------------------------------------------------------
# PATCH 3: insert the v16 subsection before \section{Main Proposition}
# ----------------------------------------------------------------------
OLD_ANCHOR = r"""\section{Main Proposition}\label{sec:mainprop}"""

NEW_V16 = r"""% =============================================================
\subsection{v16 multi-condition FBA: cross-condition $\kappa_V$
(E23)}\label{sec:novelty-v16}
% =============================================================

The v16 round (Study E23, ``multi-condition FBA''; script
\texttt{novelty\_v16\_multicondition\_e23.py}) executes the Option~D
design approved after E22: instead of changing the \emph{gene} set,
it changes the \emph{FBA condition} so that the $14$ zero-$\kappa_V$
reactions of the MAPPED genes activate, and then asks whether a
gene's $\kappa_V$ under its \emph{matched} condition predicts its
$|\log_2\mathrm{FC}|$ under the Lemuth glucose-limited aerobic
condition --- a cross-condition test of the
$\kappa_V \to$ transcript-response hypothesis. All nine conditions
run on the E10 time axis ($q_{glc}$ $5.0 \to 1.0$ mmol/gDW/h,
$q_{O_2}$ $22.0 \to 5.0$, carbon-matched feeds for substrate swaps),
the same solver, and the identical $\kappa_V$ definition
($\kappa_V(r,t) = (v_r(t) - v_r(\mathrm{T1}))^2$, per-gene
max-aggregation over the gene's GPR reactions).

\emph{Condition design and the endogeneity criterion.} The
methodological decision of this round is to split activations into
two classes before any correlation is computed. \emph{Primary}
(endogenous) activations are those whose flux magnitude follows from
medium composition, feed trajectory, and FBA optimality --- exactly
the class of E10's own $b2097$/FBA signal, whose glycolytic flux
also tracks the declining carbon feed. \emph{Burden} activations are
those whose flux magnitude is fixed by an imposed damage- or
retention-\emph{rate} (a modeling assumption with no counterpart in
the experiment); their $\kappa_V$ would encode the assumed burden
scale rather than any model-derived signal, so they are reported
structurally but \emph{excluded} from the primary correlation. The
six primary conditions are: anaerobic glucose + nitrate ad libitum
(\emph{narJ}/b1226; NO3R1pp $22.10 \to 5.52$, electron-balance
limited, nitrate non-binding); galactose as sole carbon
(\emph{galT}/b0758; UGLT $5.0 \to 1.0$); glycerol as sole carbon with
a phosphate-free medium in which glycerol-2-phosphate is the only
phosphorus source, in a $\Delta b4055$ background that removes the
periplasmic phosphatase bypass of the Ugp system
(\emph{ugpC}/b3450; GLYC2Pabcpp $2.0 \to 0.4$ --- the Ugp transporter
is the $\mathit{pho}$-regulon route for external
glycerol-phosphate); trehalose as sole carbon in a
$\Delta\mathit{treB}$ (b4240) background that removes the PTS route
and leaves the periplasmic trehalase (\emph{treA}/b1197; TREHpp
$2.5 \to 0.5$); and proline as sole nitrogen source in a
$\Delta\mathit{putP}\,\Delta\mathit{proP}$ (b1015, b4111) background
that forces uptake through the ProU ABC system
(\emph{proV}/b2677 and \emph{proW}/b2678; PROabcpp $9.97 \to 1.99$,
endogenously determined and non-binding at the proline cap). The
burden conditions are an oxidative-damage arm (superoxide from forced
quinol autoxidation at $5\%$ of $q_{glc}$ plus methionine-oxidation
damage at $1\%$: \emph{sodA}, \emph{msrA}, \emph{yeaA}), its
peroxide-vulnerable variant ($\Delta\mathit{gpx}$/b1710, spontaneous
FESD1s disabled: \emph{bcp}, THIORDXi $0.15 \to 0.03$), and an
osmotic-retention arm ($\Delta\mathit{proP}$ $\Delta$b1801, with
glycine-betaine and trehalose import and scaled retention demands:
\emph{otsB}, \emph{yehX}, \emph{yehY}). \emph{caiC}/b0037 is excluded
a priori on structural grounds (below).

\emph{Verification (four checks, all passed).}
\begin{enumerate}\itemsep0pt
\item \textbf{Baseline reproduces E22 exactly} {[D-cons]}: the fresh
  baseline run gives $438$ active reactions, the global
  biomass-deficit $\kappa_V$ maximum $0.158543$, all $15$ MAPPED
  $\kappa_V$ maxima ($b2097 = 9.490142$, the other $14$ zero), and
  the unmasked/v12/v13 Pearson $r$ ($-0.0633$, $+0.1024$, $+0.0838$)
  to four decimals.
\item \textbf{GPR membership} {[D-map]}: each of the $27$
  MAPPED-gene/reaction pairs from the v14b audit was verified to
  contain the gene in the reaction's cobra GPR set ($27/27$).
\item \textbf{Activation} {[D-act]}: $13$ of the $14$ zero-$\kappa_V$
  genes obtain non-zero $\kappa_V$ under their matched conditions;
  together with $b2097$ (active at baseline, and --- a useful
  robustness signal --- active in every carbon condition,
  $\kappa_V \in [8.9, 11.2]$), $14/15$ MAPPED genes carry non-zero
  $\kappa_V$.
\item \textbf{Endogeneity audit} {[D-end]}: the nitrate and proline
  uptakes are non-binding at every T; the glycerol-2-phosphate co-feed
  is the limiting nutrient trajectory at every T (feed-determined, the
  same class as $q_{glc}$ itself); the trehalose feed is
  carbon-matched by design.
\end{enumerate}

\emph{The \emph{caiC} dead-end (structural proof).} caiC's three
audit reactions (CTBTCAL2, CRNCAL2, CRNDCAL2) are irreversible
ATP-consuming CoA ligases feeding a carnitine-CoA ester pool
(crncoa/ctbtcoa/crnDcoa) whose only other reactions interconvert
esters and release crotonobetaine and $\gamma$-butyrobetaine --- both
without exchanges and absent from biomass. The proof is a permissive
linear program: with \emph{every} exchange reaction opened to
$\pm 1000$ and the objective set to the ligase flux itself, the
maximum attainable steady-state flux is $0.000000$ for all three
reactions --- \emph{no} medium and \emph{no} objective can carry flux
through caiC's reactions. The empirical swap test (anaerobic +
nitrate + $10$ mmol carnitine) confirms: all three fluxes are
identically zero. caiC is therefore not ``not yet activated'' but
\emph{structurally unactivatable} in iJO1366.

\emph{Two model findings from the oxidative design.} First, SPODM
(superoxide dismutase, \emph{sodA}'s reaction) and CAT (catalase) are
bounds-blocked $(0,0)$ in the published iJO1366 --- no superoxide
source exists in the default growth program. Second, opening SPODM
while MOX (a \emph{reversible, spontaneous} malate oxidase) keeps its
published reversibility creates a thermodynamically infeasible energy
loop --- quinol autoxidation $\to$ SPODM $\to$ hydrogen peroxide
$\to$ MOX-reverse $\to$ malate $\to$ NADH --- which raises $\mu$(T1)
from $0.4847$ to $0.6924$; this is presumably why the model's
publishers blocked SPODM. MOX was therefore made irreversible (a
thermodynamic model correction) in all oxidative arms, restoring
$\mu \approx$ baseline ($0.482$); a growth guard asserts
$\mu(\mathrm{T1}) \le$ baseline $+ 0.02$ for every burden condition.
Similarly, the trehalose and proline designs each required removing a
cheaper \emph{bypass} (the PTS trehalose route, the ProP/PutP
symporters, the periplasmic glycerol-phosphate phosphatase) so that
the target reaction becomes the used route --- the same
loss-of-function logic as the catalase-deficient peroxide arm, with
the flux magnitude still set by feed and optimality, not by hand.

\emph{Primary result (cross-condition correlation, $n=7$).} Over the
six endogenously re-activated genes plus $b2097$: Pearson
$r = +0.5712$ ($p = 0.180$), Spearman $\rho = +0.5636$
($p = 0.188$), $95\%$ bootstrap CI $[-0.166, +0.969]$ ($10{,}000$
resamples), and an exact permutation test over all $5{,}040$
condition--gene reassignments gives $p = 0.178$. Leave-one-out
sensitivity keeps $r \in [+0.47, +0.68]$ and strictly positive for
every omitted gene --- the sign is stable and is not carried by any
single point --- but the test is under-powered at $n=7$. For
contrast, the baseline-only MAPPED-15 analysis (the retracted v14b
artifact) gives $r = -0.158$, and the all-conditions envelope over
the $13$ activated genes (mixed endogenous/burden classes) gives
$r = +0.230$.

\emph{Burden-class activations (reported, not correlated).} The seven
burden-class genes --- \emph{sodA} (SPODM, $0.25 \to 0.05$),
\emph{msrA} (METSOXR1, $0.05 \to 0.01$), \emph{yeaA} (METSOXR2,
$0.05 \to 0.01$), \emph{bcp} (THIORDXi, $0.15 \to 0.03$),
\emph{otsB} (TRE6PP, $0.25 \to 0.05$), and \emph{yehX}/\emph{yehY}
(GLYBabcpp, $0.25 \to 0.05$) --- all obtain non-zero, varying
$\kappa_V$ under the designed stress conditions. Their magnitudes
scale with the imposed burden fractions ($5\%$ quinol-autoxidation
leak, $1\%$ methionine-oxidation damage, $5\%$ osmoprotectant
retention) and are therefore \emph{assumption-dependent}: they
demonstrate that these reactions can carry flux under their matched
stresses, not that the magnitudes predict anything.

\emph{Condition--reaction coverage.} The condition swaps lift the
active-reaction coverage from $438$ ($17.0\%$, baseline) to a union
of $538$ over the nine conditions ($20.8\%$ of $2583$; $+100$
reactions, $+22.8\%$ relative), and the gene set with non-zero
$\kappa_V$ from $435$ to $524$ ($38.3\%$ of the $1367$ model genes).
The condition$\,\leftrightarrow\,$reaction coverage bottleneck that
produced the zero-$\kappa_V$ problem is thus partially --- but only
partially --- removable by condition engineering: $2{,}045$ reactions
remain inactive across all nine conditions.

\textbf{Verdict:} E23 makes the cross-condition test \emph{computable}
where the v14b/v15 rounds had only zeros: $13/14$ blocked genes are
activated, one is proven structurally unactivatable, and the
endogeneity criterion cleanly separates the seven genes that support
correlation from the seven that cannot. The resulting association is
positive ($r = +0.571$), consistent in sign with the E10-lineage
estimates ($r \in [+0.08, +0.10]$) and stable under leave-one-out,
but individually non-significant at $n=7$. Together with E22's
finding that the Lemuth panel and the active-reaction gene set are
structurally disjoint, the honest conclusion is that local data
cannot decide the $\kappa_V \to$ transcript-response hypothesis at
meaningful power: what is missing is \emph{expression coverage} of
the multi-condition gene panel (Option~A), not more genes, mappings,
or conditions.

\textbf{Artifacts.} Script:
\texttt{novelty\_v16\_multicondition\_e23.py} ($\sim$$700$ lines,
five diagnostic probe scripts \texttt{e23\_probe\_conditions*.py}).
Outputs:
\texttt{novelty\_v16\_multicondition\_e23.\{csv,txt,png,results.json\}}
in \texttt{download/} (the CSV is the full $15 \times 9$
gene$\times$condition $\kappa_V$ matrix with matched-condition and
class annotations).

"""

apply("P3 insert v16 subsection", OLD_ANCHOR, NEW_V16 + OLD_ANCHOR)

if src.count("\\subsection{v16 multi-condition FBA") > 1:
    print("  P3: DUPLICATE v16 subsection -- ABORT")
    sys.exit(1)

with open(TEX, "w", encoding="utf-8") as f:
    f.write(src)
print(f"\n{orig_len} -> {len(src)} chars ({n_applied} patches applied)")

assert src.count("\\label{sec:novelty-v16}") == 1
n_refs = src.count("\\ref{sec:novelty-v16}")
print(f"sec:novelty-v16 defined once, referenced {n_refs} times "
      f"(expect 3: v15 pointer + E10 pointer + self-subsection header)")
print("DONE")
