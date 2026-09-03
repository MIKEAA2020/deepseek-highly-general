#!/usr/bin/env python3
"""Companion v2 restoration, part D: formalize the remaining
script-name mentions in the pre-existing sections (deposited-artifact
conventions per the journal-submission hygiene standard)."""
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


R = [
("""is numerically verified by script
\\texttt{two\\_cat\\_gluing\\_stratified.py} on a two-stratum base""",
"""is numerically verified on a two-stratum base""",
    "stratified gluing script"),

("""(Definition~\\ref{def:struct}) by script
\\texttt{two\\_cat\\_gluing\\_so3.py}. The""",
"""(Definition~\\ref{def:struct}); the deposited verification
artifacts cover both settings. The""",
    "so3 gluing script"),

("""scaling). Script \\texttt{two\\_cat\\_gluing\\_co3.py} verifies: (a)""",
"""scaling). The numerical verification confirms: (a)""",
    "co3 gluing script"),

("""shape), script \\texttt{two\\_cat\\_gluing\\_so3\\_triangular.py} repeats
the $SO(3)$ verification on a \\emph{triangular} loop""",
"""shape), the $SO(3)$ verification is repeated on a
\\emph{triangular} loop""",
    "triangular gluing script"),

("""To further validate geometry-independence, script
\\texttt{two\\_cat\\_gluing\\_so3\\_topology.py} repeats the $SO(3)$
verification on three additional loop topologies""",
"""To further validate geometry-independence, the $SO(3)$
verification is repeated on three additional loop topologies""",
    "topology gluing script"),

("""(script \\texttt{lipschitz\\_constants\\_per\\_optic.py}). The numerical""",
"""(deposited verification artifacts). The numerical""",
    "lipschitz per-optic script (bound)"),

("""places (script \\texttt{lipschitz\\_constants\\_per\\_optic.py},
Figure~\\ref{fig:cptc-zeno}).""",
"""places (Figure~\\ref{fig:cptc-zeno}; deposited verification
artifacts).""",
    "lipschitz per-optic script (zeno)"),

("""(script
\\texttt{inverse\\_limit\\_raf\\_extended.py}) produces""",
""") produces""",
    "inverse-limit script"),

("""follows (script \\texttt{autopoiesis\\_network\\_H.py},
\\texttt{phase\\_iii\\_verdict} function). Given""",
"""follows. Given""",
    "phase-iii script"),

("""example (script
\\texttt{hott\\_simplicial\\_holim.py}). The setup""",
"""example (deposited verification artifacts). The setup""",
    "holim script"),
]

for old, new, what in R:
    replace_once(old, new, what)

open(F, "w").write(src)
print("part D written:", len(src), "bytes")
