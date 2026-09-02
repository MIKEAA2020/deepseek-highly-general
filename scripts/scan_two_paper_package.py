#!/usr/bin/env python3
r"""Three machine scans for the two-paper submission package:

1. CROSS-PAPER DUPLICATION: 7-word shingle overlap between the main
   paper and the companion theory paper (comment-stripped,
   macro-flattened). Short standard phrases (<= 7 words, math formula
   names) are acceptable; long verbatim runs are not.
2. INTRA-PAPER REDUNDANCY: repeated 8-word shingles inside the main
   paper (duplicated sentences/caveats).
3. REMNANT SCAN: PLOS-era remnants, stale companion wording, v21
   mentions in rendered text.
"""
import io
import re
import json
from collections import Counter

MAIN = "/home/z/my-project/scripts/journal_manuscript_v2.tex"
COMP = "/home/z/my-project/scripts/companion_categorical.tex"

def load_tex(path):
    t = io.open(path, encoding="utf-8").read()
    # strip comments (keep \%
    lines = []
    for ln in t.split("\n"):
        s = ln.strip()
        if s.startswith("%"):
            continue
        # strip trailing comments not preceded by backslash
        ln = re.sub(r"(?<!\\)%.*$", "", ln)
        lines.append(ln)
    t = " ".join(lines)
    # flatten braces/commands conservatively
    t = t.replace("\\par", " ").replace("~", " ")
    t = re.sub(r"\\(begin|end)\{[a-z*]+\}", " ", t)
    t = re.sub(r"\\(citep|citet|cite|ref|eqref|label|input)\{[^}]*\}", " ", t)
    t = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?", " ", t)
    t = re.sub(r"[{}\\]", " ", t)
    t = re.sub(r"[^A-Za-z0-9.\- ]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()

def shingles(text, n):
    w = text.split()
    return [" ".join(w[i:i+n]) for i in range(len(w) - n + 1)]

main_t = load_tex(MAIN)
comp_t = load_tex(COMP)

# ---- 1. cross-paper duplication (7-gram) ----
m7 = set(shingles(main_t, 7))
c7 = set(shingles(comp_t, 7))
inter = m7 & c7
# filter formula-ish shingles: >40% non-letters
def formulaish(s):
    toks = s.split()
    nomath = [t for t in toks if re.fullmatch(r"[a-z.]+", t)]
    return len(nomsafe(toks)) < 0.6 * len(toks)
def nomsafe(toks):
    return [t for t in toks if re.fullmatch(r"[a-z.]+", t) and len(t) > 1]
real = sorted([s for s in inter if len(nomsafe(s.split())) >= 0.6 * len(s.split())])
# maximal runs: expand to contiguous runs of shared shingles
shared = set(inter)
runs, cur = [], []
mw = main_t.split()
for i in range(len(mw) - 6):
    sh = " ".join(mw[i:i+7])
    if sh in shared:
        if cur and cur[1] == i:
            cur = (cur[0], i + 1)
        else:
            if cur:
                runs.append(cur)
            cur = (i, i + 1)
if cur:
    runs.append(cur)
runs = [(a, b) for a, b in runs if b - a >= 7]  # at least 7 words
print("=" * 60)
print("1. CROSS-PAPER DUPLICATION (7-gram shingles, maximal runs >= 7 words)")
print(f"   main words={len(mw)}, companion words={len(comp_t.split())}")
print(f"   shared 7-grams: {len(inter)}; maximal prose runs >= 7 words: {len(runs)}")
for a, b in runs[:20]:
    print(f"   RUN [{a}:{b}]: {' '.join(mw[a:b])[:160]}")

# ---- 2. intra-paper redundancy (8-gram repeats, main paper) ----
m8 = Counter(shingles(main_t, 8))
dups = {k: v for k, v in m8.items() if v > 1 and len(nomsafe(k.split())) >= 0.6 * len(k.split())}
print("=" * 60)
print("2. INTRA-PAPER REDUNDANCY (8-gram repeated >= 2x in main paper)")
print(f"   repeated 8-grams: {len(dups)}")
for k, v in sorted(dups.items(), key=lambda kv: -kv[1])[:25]:
    print(f"   x{v}: {k[:120]}")

# ---- 3. remnant scan ----
raw_main = io.open(MAIN, encoding="utf-8").read()
raw_comp = io.open(COMP, encoding="utf-8").read()
checks = {
    "main: Author Summary": "Author Summary" in raw_main,
    "main: PLOS mention": bool(re.search(r"PLOS", raw_main)),
    "main: plos_refs input": "plos_refs" in raw_main,
    "main: v21 in body": bool(re.search(r"v21", re.sub(r"(?<!\\)%.*$", "", raw_main, flags=re.M))),
    "main: 'companion document'": "companion document" in raw_main,
    "main: superscript natbib": "super" in raw_main and "natbib" in raw_main,
    "comp: v21 in body": bool(re.search(r"v21", re.sub(r"(?<!\\)%.*$", "", raw_comp, flags=re.M))),
    "comp: 'companion document'": "companion document" in raw_comp,
    "comp: 'not independently submitted'": "Not independently submitted" in raw_comp,
    "comp: extraction record": "Extraction record" in raw_comp,
    "comp: 'predecessor manuscript'": "predecessor manuscript" in raw_comp,
}
print("=" * 60)
print("3. REMNANT SCAN (True = REMNANT PRESENT, should be False)")
bad = {k: v for k, v in checks.items() if v}
for k, v in checks.items():
    print(f"   {'REMNANT ' if v else 'clean   '} {k}")
print()
print("SUMMARY:", "CLEAN" if not bad else f"{len(bad)} remnants: {list(bad)}")
