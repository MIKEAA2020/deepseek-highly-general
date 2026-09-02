#!/usr/bin/env python3
"""Final classification of the v21 environments that scan_content_loss.py
flagged as 'not found verbatim in v2 or companion'.

For each flagged env, extract its v21 BODY text (\\begin{kind}...\\end{kind}),
and test distinctive 5-gram containment against the CONCATENATED text of
(v2 22pp + companion).  This separates:

  PRESENT-RETITLE   : body present (>=50% 5-grams) -- title was adjusted
                      (e.g. cross-reference repairs in the companion)
  FROZEN-V21-ONLY   : body absent (<50%) -- lives only in the frozen v21,
                      which is exactly what the companion Sec. 2 inventory
                      documents with explicit dispositions.

Output: console summary + per-item classification JSON for the report.
"""
import json
import re
import os

BASE = "/home/z/my-project"
TMP = "/tmp/mscan"

ENV_KINDS = ("theorem|lemma|proposition|corollary|conjecture|definition|"
             "remark|example|construction|notation")


def strip_comments(tex):
    return "\n".join(l.split("%", 1)[0] if "%" in l and not l.strip().startswith("%")
                     else l for l in tex.splitlines())


def norm_words(tex):
    return re.findall(r"[A-Za-z]{2,}", strip_comments(tex).lower())


def five_grams(words):
    return set(tuple(words[i:i + 5]) for i in range(len(words) - 4))


v21_tex = strip_comments(open(os.path.join(BASE, "scripts",
                                           "journal_manuscript.tex")).read())
comp_tex = open(os.path.join(BASE, "scripts",
                             "companion_categorical.tex")).read()
v2_tex = open(os.path.join(BASE, "scripts",
                           "journal_manuscript_v2.tex")).read()
target_words = norm_words(comp_tex + "\n" + v2_tex)
target_grams = five_grams(target_words)

scan = json.load(open(os.path.join(BASE, "download", "deepseek_bridge",
                                   "v2_content_loss_scan.json")))
flagged = scan["v21_coverage"]["v21_envs_not_found_verbatim_in_v2_or_companion"]

# dedupe by (kind, title)
seen = set()
uniq = []
for x in flagged:
    k = (x["kind"], x["title"])
    if k not in seen:
        seen.add(k)
        uniq.append(x)

# locate each env's body in v21
bodies = []
for m in re.finditer(
        r"\\begin\{(" + ENV_KINDS + r")\}(?:\[([^\]]*)\])?", v21_tex):
    kind, title = m.group(1), (m.group(2) or "").strip()
    end = v21_tex.find("\\end{" + kind + "}", m.start())
    if end == -1:
        continue
    body = v21_tex[m.start():end]
    bodies.append({"kind": kind, "title": title, "body": body})

report = []
n_present = n_frozen = n_unmatched = 0
for x in uniq:
    # find the matching body (first occurrence with same kind+title)
    body = None
    for b in bodies:
        if b["kind"] == x["kind"] and b["title"] == x["title"]:
            body = b["body"]
            break
    if body is None:
        # unlabeled env with empty title: match by kind only is too loose;
        # report as unmatched
        report.append({"kind": x["kind"], "title": x["title"],
                       "class": "BODY-NOT-LOCATED", "frac": None})
        n_unmatched += 1
        continue
    words = re.findall(r"[A-Za-z]{2,}", body.lower())
    grams = five_grams(words)
    if not grams:
        report.append({"kind": x["kind"], "title": x["title"],
                       "class": "EMPTY-BODY", "frac": None})
        n_unmatched += 1
        continue
    hit = sum(1 for g in grams if g in target_grams)
    frac = hit / len(grams)
    if frac >= 0.50:
        cls = "PRESENT-RETITLE"
        n_present += 1
    else:
        cls = "FROZEN-V21-ONLY"
        n_frozen += 1
    report.append({"kind": x["kind"], "title": x["title"],
                   "class": cls, "frac": round(frac, 3)})

out = {"summary": {"unique_flagged": len(uniq),
                   "present_retitle": n_present,
                   "frozen_v21_only": n_frozen,
                   "body_not_located": n_unmatched},
       "items": report}
json.dump(out, open(os.path.join(BASE, "download", "deepseek_bridge",
                                 "v21_flagged_env_classification.json"),
                    "w"), indent=1)

print(f"unique flagged envs:      {len(uniq)}")
print(f"  PRESENT-RETITLE:        {n_present}  "
      "(body in v2/companion, title adjusted)")
print(f"  FROZEN-V21-ONLY:        {n_frozen}  "
      "(documented dispositions in companion Sec. 2)")
print(f"  BODY-NOT-LOCATED:       {n_unmatched}")
print()
from collections import Counter
print("FROZEN-V21-ONLY by kind:",
      dict(Counter(r["kind"] for r in report
                   if r["class"] == "FROZEN-V21-ONLY")))
print()
print("Sample FROZEN-V21-ONLY titles:")
for r in [r for r in report if r["class"] == "FROZEN-V21-ONLY"][:12]:
    t = r["title"].replace("\n", " ")
    print(f"  [{r['kind']:12s}] {t[:80]} (5-gram frac {r['frac']})")
