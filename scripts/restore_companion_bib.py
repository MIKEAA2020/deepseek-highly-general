#!/usr/bin/env python3
"""Append the restoration bibliography entries to
scripts/journal_manuscript_refs.bib (companion v2 restoration)."""
import sys

F = "/home/z/my-project/scripts/journal_manuscript_refs.bib"
src = open(F).read()

ENTRIES = """
@misc{hedges2024cybernetics,
  author = {Hedges, Jules and others},
  title = {Reinforcement learning in categorical cybernetics},
  howpublished = {Electronic Proceedings in Theoretical Computer
                  Science, vol.~429 (Applied Category Theory 2024)},
  year = {2024},
  note = {arXiv:2404.02688}
}

@misc{fong2017backprop,
  author = {Fong, Brendan and Spivak, David I. and Tuy{\\'e}ras,
            R{\\'e}my},
  title = {Backprop as functor: A compositional perspective on
           supervised learning},
  year = {2017},
  note = {arXiv:1711.10455}
}

@article{vereshchagin2010rate,
  author = {Vereshchagin, Nikolai K. and Vit{\\'a}nyi, Paul M. B.},
  title = {Rate distortion and denoising of individual data under
           a general reproduction function},
  journal = {IEEE Transactions on Information Theory},
  year = {2010},
  volume = {56},
  number = {7},
  pages = {3438--3454}
}

@article{clarke1975,
  author = {Clarke, Frank H.},
  title = {Generalized gradients and applications},
  journal = {Transactions of the American Mathematical Society},
  year = {1975},
  volume = {205},
  pages = {247--262}
}

@book{clarke1990,
  author = {Clarke, Frank H.},
  title = {Optimization and Nonsmooth Analysis},
  publisher = {Society for Industrial and Applied Mathematics},
  address = {Philadelphia},
  edition = {Classics in Applied Mathematics 5},
  year = {1990}
}

@article{milgromsegal2002,
  author = {Milgrom, Paul and Segal, Ilya},
  title = {Envelope theorems for arbitrary choice sets},
  journal = {Econometrica},
  year = {2002},
  volume = {70},
  number = {2},
  pages = {583--609}
}

@misc{adamek2005,
  author = {Ad{\\'a}mek, Ji{\\v{r}}{\\'i}},
  title = {Introduction to Coalgebra: Towards a Mathematics of
           States and Observation},
  howpublished = {Lecture notes, Technische Universit{\\'a}t
                  Braunschweig},
  year = {2005}
}

@article{worrell2005,
  author = {Worrell, James},
  title = {On the final sequence of a finitary set functor},
  journal = {Theoretical Computer Science},
  year = {2005},
  volume = {338},
  number = {1--3},
  pages = {184--199}
}

@misc{tralie2018ripser,
  author = {Tralie, Christopher and Saul, Nathaniel and
            Bar-On, Hadas},
  title = {{Ripser.py}: a lean implementation of the
            Vietoris--Rips persistent homology computation},
  howpublished = {Journal of Open Source Software, vol.~3, no.~29},
  year = {2018}
}
"""

# In the triple-quoted block above, \\' produces the literal LaTeX
# accent escape \' matching the existing entries' style.

keys = ["hedges2024cybernetics", "fong2017backprop",
        "vereshchagin2010rate", "clarke1975", "clarke1990",
        "milgromsegal2002", "adamek2005", "worrell2005",
        "tralie2018ripser"]
for k in keys:
    if ("{" + k + ",") in src:
        print(f"skip [{k}] (already present)")
        continue
    print(f"ok  [{k}]")

if all(("{" + k + ",") in src for k in keys):
    print("nothing to append")
    sys.exit(0)

with open(F, "a") as f:
    f.write(ENTRIES)
print("bib entries appended")
