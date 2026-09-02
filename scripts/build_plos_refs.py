#!/usr/bin/env python3
r"""Journal-submission pass, step 1: generate a PLOS-style reference list
(numbered, order of first citation, PLOS entry layout) from
journal_manuscript_v2_refs.bib, for inclusion via \input{}.

PLOS layout implemented:
  Article:  Author AB, Author CD (Year) Title. Journal Vol: Pages.
  Book:     Author AB (Year) Title. Edition. City: Publisher.
  Preprint: Author AB (Year) Title. bioRxiv. doi:NNNN.
Authors: surname + initials without periods; up to six listed, then
"et al."; TeX accent escapes in surnames are preserved. Journal names
are kept as stored in the committed .bib (full names); PLOS copyediting
abbreviates at proof stage. Species italics {\it X} -> \emph{X}.
"""
import re
import sys

BASE = "/home/z/my-project/scripts"
TEX = f"{BASE}/journal_manuscript_v2.tex"
BIB = f"{BASE}/journal_manuscript_v2_refs.bib"
OUT = f"{BASE}/journal_manuscript_v2_plos_refs.tex"

# ---- 1. citation order from the manuscript -----------------------------
tex = open(TEX).read()
order = []
citet_keys = set()
for m in re.finditer(r"\\cite[tp]?\{([^}]*)\}", tex):
    for k in m.group(1).split(","):
        k = k.strip()
        if k and k not in order:
            order.append(k)
for m in re.finditer(r"\\citet\{([^}]*)\}", tex):
    for k in m.group(1).split(","):
        citet_keys.add(k.strip())

# ---- 2. parse the .bib -------------------------------------------------
bib = open(BIB).read()
entries = {}
i = 0
while True:
    m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(bib, i)
    if not m:
        break
    kind, key = m.group(1).lower(), m.group(2)
    # brace-match the entry body
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
    # parse fields with brace matching
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
            k += 1  # past the closing brace
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

missing = [k for k in order if k not in entries]
if missing:
    sys.exit(f"ERROR: cited keys without bib entries: {missing}")


# ---- 3. PLOS formatting -------------------------------------------------
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
    # no comma: "First Last" (not used in this bib, but safe)
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


def fmt_title(t):
    return re.sub(r"\{\\it\s*", r"\\emph{", t)


def join_period(fragment):
    """Append a period unless the fragment already ends with sentence
    punctuation (avoids 'analysis?.')."""
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
    # article
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


# ---- 4. emit ------------------------------------------------------------
lines = ["% journal_manuscript_v2_plos_refs.tex -- AUTO-GENERATED by",
         "% scripts/build_plos_refs.py (journal-submission pass).",
         "% PLOS-style numbered references in order of first citation.",
         "% Do not edit by hand; re-run the generator instead.",
         "\\begin{thebibliography}{%d}" % len(order),
         "\\setlength{\\itemsep}{2pt}",
         "\\small"]
def short_author(field):
    r"""Natbib short form for \citet: 1 author -> Surname; 2 ->
    Surname and Surname; 3+ -> Surname et~al."""
    field = re.sub(r"\s+", " ", field).strip()
    parts = [p.strip() for p in field.split(" and ")]
    if parts and parts[-1].lower() == "others":
        parts = parts[:-1]
    surnames = [p.split(",")[0].strip() for p in parts]
    surnames = [s for s in surnames if s]
    if len(surnames) >= 3:
        return surnames[0] + " et~al."
    if len(surnames) == 2:
        return surnames[0] + " and " + surnames[1]
    return surnames[0] if surnames else ""


for n, key in enumerate(order, 1):
    kind, f = entries[key]
    if key in citet_keys:
        lines.append(f"\\bibitem[{short_author(f['author'])}({f['year']})]{{{key}}}")
    else:
        lines.append(f"\\bibitem{{{key}}}")
    lines.append(f"{fmt_entry(key)}")
    lines.append("")
lines.append("\\end{thebibliography}")
open(OUT, "w").write("\n".join(lines) + "\n")

print(f"[PLOS-REFS] {len(order)} entries in citation order -> {OUT}")
for n, key in enumerate(order, 1):
    print(f"  [{n:2d}] {key}: {fmt_entry(key)[:90]}")
