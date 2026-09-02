#!/usr/bin/env python3
r"""Journal retarget (Bulletin of Mathematical Biology, no-fee route):
generate a BMB/Springer author-year reference list from
journal_manuscript_v2_refs.bib, for inclusion via \input{} with
natbib [round].

BMB layout (submission guidelines: "Cite references in the text by
name and year in parentheses"):
  Article:  Author AB, Author CD (Year) Title. Journal Vol: Pages.
  Book:     Author AB (Year) Title. Edition. City: Publisher.
Authors: surname + initials; up to six listed, then et al. List is
ALPHABETICAL by first author surname (Springer author-year style).
Natbib optional labels \bibitem[Author(Year)]{key} supply the
author-year citation text.
"""
import re
import sys

BASE = "/home/z/my-project/scripts"
BIB = f"{BASE}/journal_manuscript_v2_refs.bib"
OUT = f"{BASE}/journal_manuscript_v2_bmb_refs.tex"

# ---- 1. cited keys = every key in the .bib (the list is the union;
#          the manuscript cites all of them plus the companion) ------
bib = open(BIB).read()
entries = {}
i = 0
while True:
    m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(bib, i)
    if not m:
        break
    kind, key = m.group(1).lower(), m.group(2)
    depth, j = 1, m.end()
    while depth > 0:
        c = bib[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        j += 1
    body = bib[m.end():j - 1]
    i = j
    fields = {}
    k = 0
    while k < len(body):
        fm = re.compile(r"(\w+)\s*=\s*").search(body, k)
        if not fm:
            break
        name = fm.group(1).lower()
        k = fm.end()
        if body[k] == "{":
            depth, start = 1, k + 1
            while depth > 0:
                if body[k + 1] == "{":
                    depth += 1
                elif body[k + 1] == "}":
                    depth -= 1
                k += 1
            val = body[start:k]
            k += 1
        elif body[k] == '"':
            e = body.index('"', k + 1)
            val = body[k + 1:e]
            k = e + 1
        else:
            e = body.find(",", k)
            e = len(body) if e == -1 else e
            val = body[k:e]
            k = e
        fields.setdefault(name, val.strip())
        nxt = body.find(",", k)
        k = len(body) if nxt == -1 else nxt + 1
    entries[key] = (kind, fields)

# ---- 2. formatting helpers (shared conventions with the PLOS pass) -
def initials(first):
    out = []
    for tok in first.split():
        tok = tok.strip("{}")
        if not tok:
            continue
        out.append(tok[0])
    return "".join(out)

def fmt_author(a):
    if "," in a:
        last, first = a.split(",", 1)
        return f"{last.strip()} {initials(first)}"
    toks = a.split()
    return f"{toks[-1]} {''.join(t[0] for t in toks[:-1])}".strip()

def fmt_authors(field):
    field = re.sub(r"\s+", " ", field).strip()
    parts = [p.strip() for p in field.split(" and ")]
    et_al = False
    if parts and parts[-1].lower() == "others":
        parts, et_al = parts[:-1], True
    names = [fmt_author(p) for p in parts]
    if len(names) > 6 or (et_al and len(names) >= 6):
        names = names[:6] + ["et al."]
    elif et_al:
        names = names + ["et al."]
    return ", ".join(names)

def short_author(field, year):
    r"""Natbib optional-label form: Surname (1); Surname and Surname
    (2); Surname et~al. (3+)."""
    field = re.sub(r"\s+", " ", field).strip()
    parts = [p.strip() for p in field.split(" and ")]
    if parts and parts[-1].lower() == "others":
        parts = parts[:-1]
    surnames = [p.split(",")[0].strip() for p in parts]
    surnames = [s for s in surnames if s]
    if not surnames:
        return f"[Z.ai({year})]"
    if len(surnames) >= 3:
        lab = surnames[0] + " et~al."
    elif len(surnames) == 2:
        lab = surnames[0] + " and " + surnames[1]
    else:
        lab = surnames[0]
    return f"[{lab}({year})]"

def sort_key(key):
    kind, f = entries[key]
    field = re.sub(r"\s+", " ", f["author"]).strip()
    parts = [p.strip() for p in field.split(" and ")]
    if parts and parts[-1].lower() == "others":
        parts = parts[:-1]
    surname = parts[0].split(",")[0].strip() if parts else "zzz"
    return (surname.lower(), f.get("year", "9999"), key)

def fmt_title(t):
    return re.sub(r"\{\\it\s*", r"\\emph{", t)

def join_period(fragment):
    return fragment if fragment[-1:] in ".?!" else fragment + "."

def fmt_entry(key):
    kind, f = entries[key]
    auth = fmt_authors(f["author"])
    year = f.get("year", "")
    title = fmt_title(f["title"]).strip()
    if kind == "book":
        s = f"{auth} ({year}) {title}"
        if f.get("edition"):
            s += f". {f['edition']} edition"
        s += f". {f.get('address', '')}: {f.get('publisher', '')}."
        return s
    if kind in ("misc", "unpublished") or not f.get("journal"):
        s = f"{auth} ({year}) " + join_period(title)
        note = f.get("note", "")
        if note:
            s += f" {join_period(note)}"
        return s
    s = f"{auth} ({year}) " + join_period(title) + f" {fmt_title(f['journal'])}"
    if f.get("volume"):
        s += f" {f['volume']}"
        if f.get("pages"):
            s += f": {f['pages']}"
    s = join_period(s)
    note = f.get("note", "")
    if note:
        if re.match(r"^10\.\d", note):
            s += f" doi:{note}."
        else:
            s += f" {note}."
    return s

# ---- 3. emit (alphabetical) -------------------------------------------
order = sorted(entries.keys(), key=sort_key)
lines = ["% journal_manuscript_v2_bmb_refs.tex -- AUTO-GENERATED by",
         "% scripts/build_bmb_refs.py (BMB retarget pass).",
         "% Springer/BMB author-year references, ALPHABETICAL by first",
         "% author surname, with natbib optional labels.",
         "% Do not edit by hand; re-run the generator instead.",
         "\\begin{thebibliography}{%d}" % len(order),
         "\\setlength{\\itemsep}{2pt}",
         "\\small"]
for key in order:
    kind, f = entries[key]
    label = short_author(f["author"], f.get("year", ""))
    lines.append(f"\\bibitem{label}{{{key}}}")
    lines.append(fmt_entry(key))
lines.append("\\end{thebibliography}")
open(OUT, "w").write("\n".join(lines) + "\n")
print(f"wrote {OUT}: {len(order)} entries")
for key in order:
    print("  ", sort_key(key), key)
