#!/usr/bin/env python3
"""v21 render QA (final): verify every P0/P1 fix in the compiled PDF.
Excludes the v21 subsection's own documentation quotes of the old defects."""
import fitz, re, sys

doc = fitz.open("scripts/journal_manuscript.pdf")
full = "\n".join(doc[p].get_text() for p in range(len(doc)))
norm = full.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")

# locate v21 subsection page range (documentation quotes live there)
v21_pages = set(pno for pno in range(len(doc)) if "v21 mechanical-integrity round" in doc[pno].get_text())
# widen to the whole subsection (spans ~2 pages after that heading)
v21_start = min(v21_pages) if v21_pages else None
v21_text = "\n".join(doc[p].get_text() for p in range(v21_start, min(v21_start + 3, len(doc)))) if v21_start is not None else ""
body = "\n".join(doc[p].get_text() for p in range(len(doc)) if p not in range(v21_start, min(v21_start + 3, len(doc)))) if v21_start is not None else full
bodyn = body.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")

ok, fail = [], []
def check(name, cond):
    (ok if cond else fail).append(name)

check("P0-1 no '[?]' outside v21 documentation", "[?]" not in body)
check("P0-2a '-0.018' present (>=3)", bodyn.count("-0.018") >= 3)
check("P0-2b no '-0.008' defect outside v21 doc", "-0.008" not in bodyn)
check("P0-2c gap '0.103' present", "0.103" in bodyn)
check("P0-2d no '0.093' defect outside v21 doc", "0.093" not in bodyn)
check("P0-2e factor '~26' present, '~56' absent", 
      re.search(r"factor of\s*[~∼]\s*26", bodyn) is not None and
      re.search(r"factor of\s*[~∼]\s*56", bodyn) is None)
check("P0-3a glycogen phosphorylase EC 2.4.1.1", "phosphorylase EC 2.4.1.1" in bodyn.replace("\n", " "))
check("P0-3b PPK EC 2.7.4.1 retained", "polyphosphate kinase EC" in body.replace("\n", " "))
check("P0-4 Fig.7 caption structure group SO(3)",
      "n = 4 non-abelian regime\n(structure group SO(3)" in norm)
check("P0-5a Authorship: no research-integrity pointer", "research-integrity" not in body)
check("P0-5b no 'S1.4' outside v21 doc", "S1.4" not in body.replace("\n", " "))
check("P0-5c invlim operational Proposition form x2+",
      len(re.findall(r"operational Proposition\s*4.4 form", norm)) >= 2)
check("P0-6a matrix 'only 4 compute'", "only 4 compute" in bodyn.replace("\n", " "))
check("P0-6b no 'only 3 compute' outside v21 doc", "only 3 compute" not in bodyn.replace("\n", " "))
check("P0-6c 'remaining 12 studies'", "remaining 12 studies" in bodyn.replace("\n", " "))
check("P0-7a medium-audit note present", "medium-audit note" in norm)
check("P0-7b EX_tre_e artifact + 0.982/0.822 optima",
      "EX_tre_e" in norm.replace("\n", "") and "0.982" in norm and "0.822" in norm)
check("P0-8 '10/11 cases (91%)'", "10/11 cases (91%)" in bodyn)
check("P0-9a no '+0.187 at n = 241' mispair outside docs",
      "0.187 at n = 241" not in bodyn.replace("\n", " "))
check("P0-9b common-set '+0.187 (p = 3.7' retained (correct site)",
      "0.187 (p = 3.7" in norm)
check("P0-9c '+0.191' >= 4 sites", bodyn.count("+0.191") >= 4)
check("P0-9d reconciliation note present", "The +0.187" in norm and "240-gene set common to both platforms" in norm)

# P1-10: Def 3.18 labels geometry
def_page = next((p for p in range(len(doc)) if "viability concentration threshold" in doc[p].get_text()), None)
labels_ok, n_labels = True, 0
if def_page is not None:
    d = doc[def_page].get_text("dict")
    for b in d["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if re.fullmatch(r"\((i|ii|iii|iv|v)\) (Knockout|Drift under dynamics|Recovery above threshold|Downstream cascade|Restoration control)\.", t):
                    n_labels += 1
                    if s["bbox"][0] < 40: labels_ok = False
check("P1-10 Def 3.18 all 5 step labels on-page", labels_ok and n_labels == 5)

# P1-11: Table 6
t6_page = next((p for p in range(len(doc)) if "likely missing term" in doc[p].get_text()), None)
t6 = doc[t6_page].get_text() if t6_page is not None else ""
check("P1-11a Table 6 'growth rate' complete", "growth rate" in t6)
check("P1-11b Table 6 '(regulatory)' complete", "(regulatory)" in t6)
check("P1-11c no 'growt' fragment", "growt\n" not in t6 and "growt " not in t6)
check("P1-11d Table 6 within page", all(
    s["bbox"][2] < 540 for b in doc[t6_page].get_text("dict")["blocks"]
    for l in b.get("lines", []) for s in l["spans"] if s["bbox"][1] < 260 and s["bbox"][0] > 100)
    if t6_page is not None else False)

check("v21 subsection present + bookmarked",
      "v21 mechanical-integrity round" in full and any("v21" in str(it) for it in doc.get_toc()))
check("chain v17-v21 all present", all(v in norm for v in ["v17", "v18", "v19", "v20", "v21"]))
check("page count sane", 131 <= len(doc) <= 136)

print(f"PAGES: {len(doc)}   v21 doc pages: {sorted(p+1 for p in v21_pages)}")
print(f"PASS {len(ok)} / FAIL {len(fail)}")
for n in fail: print("  [XX]", n)
sys.exit(1 if fail else 0)
