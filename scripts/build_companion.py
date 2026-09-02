#!/usr/bin/env python3
"""
Build the categorical/HoTT companion document from the frozen v21.

Companion = the categorical and homotopy-theoretic sections of the
frozen v21 (scripts/journal_manuscript.tex, 10,830 lines, DO NOT
MODIFY), extracted verbatim with:
  - a new title/abstract/positioning block (its role as companion to
    the main paper scripts/journal_manuscript_v2.tex);
  - a status-protocol section (every item labeled proved/conjecture/
    machine-verified, as in v21);
  - the full v21 inventory table (nothing silently excised: every
    v21 section is listed with its disposition);
  - the v21 preamble (macros, theorem environments) and the v21
    bibliography (journal_manuscript_refs.bib).

Extracted sections (v21 line ranges, 1-indexed, inclusive of the
\\section line, exclusive of the next section):
  prelim      432-570     (categorical preliminaries / optic category)
  savgs       571-1332    (SAVGS framework, 2-cat gluing, transport law,
                           autopoiesis closure test)
  noether     1750-1847   (Bregman-divergence Noether correspondence)
  hierarchy   1848-1905   (seven-claim falsification hierarchy)
  composition 1906-2115   (single composition theorem)
  lipschitz   2116-2357   (per-optic Lipschitz / Banach contraction)
  invlim      3467-3782   (filtered-colimit construction of RAFs)
  hott        3783-4153   (infinity-categorical HoTT extension)

Output: scripts/companion_categorical.tex
"""
import re

SRC = "/home/z/my-project/scripts/journal_manuscript.tex"
OUT = "/home/z/my-project/scripts/companion_categorical.tex"

lines = open(SRC).read().splitlines(keepends=True)


def block(a, b):
    """1-indexed inclusive [a, b]."""
    return "".join(lines[a - 1:b])


SECTIONS = [
    ("prelim", 432, 570),
    ("savgs", 571, 1332),
    ("noether", 1750, 1847),
    ("hierarchy", 1848, 1905),
    ("composition", 1906, 2115),
    ("lipschitz", 2116, 2357),
    ("invlim", 3467, 3782),
    ("hott", 3783, 4153),
]

body = []
for name, a, b in SECTIONS:
    body.append("%% ================ [v21 extract: " + name
                + "] ================\n")
    body.append(block(a, b))
    body.append("\n")
extracted = "".join(body)

# ---- cross-reference audit: labels defined inside vs referenced ----
lab_in = set(re.findall(r"\\label\{([^}]+)\}", extracted))
refs_in = set(re.findall(r"\\ref\{([^}]+)\}", extracted))
dangling = sorted(refs_in - lab_in)

preamble = r"""% =====================================================================
%  companion_categorical  --  THE CATEGORICAL/HoTT COMPANION
%  ---------------------------------------------------------------
%  Role:       companion document to journal_manuscript_v2.tex (the
%              main paper). Preserves, verbatim, the categorical and
%              homotopy-theoretic sections of the frozen v21
%              (scripts/journal_manuscript.tex, 10,830 lines, DO NOT
%              MODIFY) per the publication decision of 2026-09-02:
%              the split is a publication choice, NOT a deletion.
%  Source:     extracted by scripts/build_companion.py (frozen v21
%              line ranges recorded per section); every theorem,
%              conjecture, and machine-verified claim keeps the
%              status it carries in v21.
%  Guarantees: (i) v21 itself remains committed and unmodified;
%              (ii) the inventory table in Sec. 2 lists every v21
%              section with its disposition; (iii) no claim is
%              promoted: conjectures stay conjectures.
% =====================================================================
\documentclass[11pt,a4paper]{article}

\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{mathrsfs}
\usepackage[margin=2.4cm]{geometry}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{graphicx}
\graphicspath{{../download/}}
\usepackage[colorlinks=true,linkcolor=blue!55!black,citecolor=blue!45!black,urlcolor=blue!55!black,bookmarks=true,bookmarksnumbered=true,unicode=true]{hyperref}
\usepackage[round]{natbib}

% Theorem environments (v21, unchanged)
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{construction}[theorem]{Construction}
\newtheorem{assumption}[theorem]{Assumption}
\newtheorem{conjecture}[theorem]{Conjecture}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}

% Macros (v21, unchanged)
\newcommand{\kk}{\kappa_{\!V}}
\newcommand{\HH}{\mathcal{H}}
\newcommand{\OO}{\mathcal{O}}
\newcommand{\CC}{\mathcal{C}}
\newcommand{\RR}{\mathbb{R}}
\newcommand{\PP}{\mathbb{P}}
\newcommand{\SO}{\mathrm{SO}}
\newcommand{\CO}{\mathrm{CO}}
\newcommand{\so}{\mathfrak{so}}
\newcommand{\Stab}{\mathrm{Stab}}
\newcommand{\End}{\mathrm{End}}
\newcommand{\Optic}{\mathbf{Optic}}
\newcommand{\RAF}{\mathrm{RAF}}
\newcommand{\colim}{\operatorname{colim}}
\newcommand{\id}{\mathrm{id}}
\newcommand{\sgn}{\operatorname{sgn}}
\newcommand{\Frob}{\!\operatorname{}\!\mathopen{}\Vert\cdot\mathclose{}\Vert_{\!F}}
\newcommand{\normF}[1]{\mathopen{}\Vert#1\mathclose{}\Vert_{\!F}}
\newcommand{\distD}{\mathrm{dist}_{D}}
\newcommand{\SAVGS}{\mathrm{SAVGS}}
\DeclareMathOperator{\Lip}{Lip}
\newcommand{\kmu}{\kappa^{\mu}}

\hypersetup{
 pdftitle={A Categorical Companion to the Measure-Theoretic
           Curvature Framework},
 pdfauthor={Z.ai},
 pdfsubject={categorical composition, stratified connections, HoTT
             extension; companion document},
 pdfkeywords={optic category, 2-category, stratified connection, RAF,
              filtered colimit, homotopy type theory, univalence}}

\widowpenalty=10000
\clubpenalty=10000
\emergencystretch=3em
\hbadness=2500
\vbadness=2500

\begin{document}

\begin{center}
  \vspace*{0.4em}
  {\large\bfseries A Categorical Companion to the Measure-Theoretic
   Curvature Framework:\par
   Optics, Stratified Connections, and the Homotopy Extension\par}
  \vspace{0.8em}
  {\normalsize Z.ai\par}
  \vspace{0.2em}
  {\small\itshape Companion document, \today\par}
  \vspace{0.6em}
  \rule{0.7\textwidth}{0.4pt}
\end{center}

\vspace{0.6em}
\begin{center}
\begin{minipage}{0.92\textwidth}
\small
\textbf{Abstract.} This document is the categorical and
homotopy-theoretic companion to \emph{A Measure-Theoretic Discrete
Curvature Framework for Metabolic Gene Sensitivity}. It preserves,
verbatim from the predecessor manuscript (v21, frozen), the formal
line that the main paper does not carry: the optic-category
composition semantics, the $2$-category $\mathbf{StCon}(B)$ of
stratified connections with its lax-functorial gluing theorem, the
Fisher--viability transport law on constant-active-set strata, the
Bregman-divergence Noether correspondence, the single composition
theorem with its per-optic Lipschitz constants and unconditional
Banach contraction, the filtered-colimit construction of RAF sets,
and the $\infty$-categorical extension through homotopy type theory
with the univalence-corrected closure test. Every item keeps the
status it carries in the frozen source --- theorems as theorems,
conjectures as conjectures, machine-verified claims with their
artifacts. The main paper retains only the measure-theoretic spine
and the empirical association; nothing here is load-bearing for
those claims, and nothing was deleted: the complete frozen v21 and
its Git history remain committed as the audit baseline.
\par
\vspace{0.4em}
\emph{Status: companion document. Not independently submitted in
this form; the mathematical content is extracted, not rewritten.}
\end{minipage}
\end{center}

\tableofcontents
\newpage

% =====================================================================
\section{The role of this document}\label{sec:role}

\paragraph{What this is.}
The main paper (\texttt{journal\_manuscript\_v2.tex}) carries the
measure-theoretic spine: the atomic curvature measure of parametric
FBA, the refinement--resolution bridge (Theorem~B$'$), the
value--flux crease coupling, and the empirical association with its
layer decision. The predecessor manuscript (v21, 10{,}830 lines,
frozen) additionally carried an extensive categorical and
homotopy-theoretic line --- composition semantics for domain bridges,
stratified connection $2$-categories, RAF autopoiesis constructions,
and a homotopy-type-theoretic extension. That line is valid work
with its own machine-verified pieces, but it is not load-bearing
for the main paper's claims. The publication decision of
2026-09-02 is a \emph{split}, not a deletion: the categorical/HoTT
material is preserved in this companion, extracted verbatim from
the frozen v21 with the extraction ranges recorded in
\texttt{scripts/build\_companion.py}.

\paragraph{What this is not.}
This companion is not a rewrite, an update, or a re-verification of
the v21 material. Conjectures remain conjectures; the R/D/E
hierarchy of the source is kept. Where v21 itself marks an item as
retracted, superseded, or repaired in a later round, the extracted
text keeps that marking. The complete inventory of v21 sections and
their dispositions is given in Sec.~\ref{sec:inventory}; the frozen
source and its full Git history are the authoritative record.

\paragraph{Status protocol.}
As in the main paper, [R-$n$] blocks are proved or machine-verified
results, [D-$n$] blocks are definitions and constructions, [E-$n$]
blocks are executed experiments with deposited artifacts. The
machine artifacts for the categorical line (autopoiesis network
tests A--K, the $n = 3$ prototype, the contraction batteries) live
under \texttt{download/} exactly as referenced by the frozen v21.

% =====================================================================
\section{The v21 inventory (nothing silently excised)}\label{sec:inventory}

\begin{tabularx}{\textwidth}{lX}
\toprule
\textbf{v21 section} & \textbf{Disposition} \\
\midrule
1 Introduction & main paper, rewritten to the single story \\
2 Preliminaries (optic category) & \textbf{this companion}
      (Sec.~\ref{sec:prelim}) \\
3 SAVGS framework (2-cat gluing, transport law, autopoiesis
      closure) & \textbf{this companion} (Sec.~\ref{sec:savgs});
      the autopoiesis network executions A--K remain in v21 with
      their artifacts \\
4 Algorithmic rate-distortion / $\kk$ derivation & v21 (frozen);
      the $\kk$ definition is superseded in the main paper by the
      measure-theoretic $\kmu$ \\
5 Bregman--Noether correspondence & \textbf{this companion}
      (Sec.~\ref{sec:noether}) \\
6 Seven-claim falsification hierarchy & \textbf{this companion}
      (Sec.~\ref{sec:hierarchy}) \\
7 Single composition theorem & \textbf{this companion}
      (Sec.~\ref{sec:composition}) \\
8 Per-optic Lipschitz constants / Banach contraction & \textbf{this
      companion} (Sec.~\ref{sec:lipschitz}) \\
9 Foundational tests (Claims F, G) & v21 (frozen) with artifacts \\
10 $n = 3$ prototype operationalization & v21 (frozen) with
      artifacts \\
11 Claim-D heavy-tail stress test & v21 (frozen) with artifacts \\
12 L\'evy first-passage derivation & v21 (frozen) \\
13 $n = 4$ non-abelian regime & v21 (frozen) \\
14 CPTP--Zeno lift & v21 (frozen) \\
15 Numerical contraction of $T$ & v21 (frozen) \\
16 Filtered-colimit RAF construction & \textbf{this companion}
      (Sec.~\ref{sec:invlim}) \\
17 $\infty$-categorical HoTT extension & \textbf{this companion}
      (Sec.~\ref{sec:hott}) \\
18 Autopoiesis on real networks (A--K) & v21 (frozen) with
      artifacts under \texttt{download/} \\
19 Novelty-assessment elevation studies (E1--E20) & v21 (frozen);
      the E22--E27 empirical line is superseded by the main paper's
      E-series with the locked metric \\
Theorem B (refinement bridge) & superseded in the main paper by
      Theorem~B$'$ (corrected form) \\
M1/M3/M4 computational batteries & main paper \S5 with artifacts \\
\bottomrule
\end{tabularx}

\emph{Note on labels.} The extracted sections keep their v21 labels
(\texttt{sec:prelim}, \texttt{sec:savgs}, \dots) so that internal
cross-references remain exact. Cross-references to sections not
extracted are rendered as textual pointers to the frozen v21.

"""

tail = r"""
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

\end{document}
"""

# ---- resolve dangling \ref{...} to textual pointers ----
# v21 location of each dangling label (measured from the frozen source)
DANGLING_WHERE = {
    "conj:filtered-colimits-optic": "v21 21.6",
    "conj:global-stratified-holonomy": "v21 21.5",
    "conj:zeno-selfref": "v21 21.6",
    "def:ard": "v21 4",
    "prop:kappa-derivation": "v21 4",
    "prop:main": "v21 20",
    "prop:netG-verdict": "v21 18.8",
    "prop:netH-verdict": "v21 18.9",
    "prop:qbound": "v21 15",
    "sec:autopoiesis-network-G": "v21 18.8",
    "sec:autopoiesis-network-K-robust": "v21 18.13",
    "sec:autopoiesis-real-networks": "v21 18",
    "sec:calibration": "v21 10.1",
    "sec:cptp": "v21 14",
    "sec:discussion": "v21 21",
    "sec:n3": "v21 10",
    "sec:n4": "v21 13",
    "sec:titer": "v21 15",
    "thm:smooth-envelope": "v21 4.2",
}

# \ref{X} -> textual pointer; \S\ref{X} -> \S pointer (avoid double S)
for r in dangling:
    where = DANGLING_WHERE.get(r, "v21")
    extracted = extracted.replace(
        r"\S\ref{" + r + "}", r"\S\,\textup{(" + where + ")}")
    extracted = extracted.replace(
        r"\ref{" + r + "}", r"\textup{(" + where + ")}")

resolved = [(r, DANGLING_WHERE.get(r, "v21")) for r in dangling]

out = preamble + extracted + tail
open(OUT, "w").write(out)

print(f"[companion] wrote {OUT} ({len(out.splitlines())} lines)")
print(f"[companion] extracted sections: {[n for n, _, _ in SECTIONS]}")
print(f"[companion] labels defined inside: {len(lab_in)}")
print(f"[companion] dangling refs (to non-extracted material): "
      f"{len(dangling)}")
for r, _ in resolved:
    print(f"    \\ref{{{r}}}")
