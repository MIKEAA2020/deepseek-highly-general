#!/usr/bin/env python3
"""
Deep content-loss scan: latest v2 manuscript (20 pp) vs the previous
drafts in the version chain (8 -> 10 -> 12 -> 20 pp) and vs the frozen
v21 (10,830 lines) + companion (33 pp).

Questions (user round 2026-09-02):
  1. accidental content loss between successive v2 versions?
  2. condensation of legit content (present earlier, compressed now)?
  3. anything worth restoring, as-is or after corrections?

Method: structural inventory (sections, theorems, definitions,
propositions, lemmas, corollaries, conjectures, remarks, experiments
[E-*], tables, figures, appendices, labels) per version; set diffs
between successive versions; v21 coverage check (every v21 labeled
environment -> present in v2 / companion / neither); text-level
paragraph survival ratios (condensation detector).
"""
import json
import re
import os

TMP = "/tmp/mscan"
BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")
os.makedirs(OUT, exist_ok=True)

VERS = [
    ("v2_51ce934_L0_8pp", f"{TMP}/v2_51ce934.tex"),
    ("v2_3c0f876_8pp", f"{TMP}/v2_3c0f876.tex"),
    ("v2_3cc5f8a_10pp", f"{TMP}/v2_3cc5f8a.tex"),
    ("v2_f3342b1_12pp", f"{TMP}/v2_f3342b1.tex"),
    ("v2_828c89a_20pp", f"{TMP}/v2_HEAD.tex"),
]
ENV_RE = re.compile(
    r"\\begin\{(theorem|lemma|proposition|corollary|conjecture|"
    r"definition|remark|example|construction|notation)\}"
    r"(?:\[([^\]]*)\])?(?:\\label\{([^}]*)\})?")
SEC_RE = re.compile(r"\\(section|subsection|subsubsection)\*?\{([^}]*)\}")
PARA_RE = re.compile(r"\\paragraph\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
CITE_RE = re.compile(r"\\cite[tp]?\{([^}]*)\}")
E_RE = re.compile(r"\[E[- ]([A-Za-z0-9]+)\]")


def strip_comments(tex):
    return "\n".join(l.split("%", 1)[0] if "%" in l and not l.strip().startswith("%")
                     else l for l in tex.splitlines())


def inventory(path):
    tex = strip_comments(open(path).read())
    inv = {"envs": [], "secs": [], "paras": [], "labels": set(),
           "cites": set(), "E_items": [], "tables": 0, "figures": 0,
           "n_words": len(re.findall(r"[A-Za-z]{2,}", tex))}
    for m in ENV_RE.finditer(tex):
        inv["envs"].append({"kind": m.group(1), "title": (m.group(2) or "").strip(),
                            "label": m.group(3)})
    # envs with separate \label right after
    for m in re.finditer(
            r"\\begin\{(theorem|lemma|proposition|corollary|conjecture|"
            r"definition|remark)\}(?:\[([^\]]*)\])?\s*\\label\{([^}]*)\}",
            tex):
        if not any(e["label"] == m.group(3) for e in inv["envs"]):
            inv["envs"].append({"kind": m.group(1),
                                "title": (m.group(2) or "").strip(),
                                "label": m.group(3)})
    for m in SEC_RE.finditer(tex):
        inv["secs"].append({"level": m.group(1), "title": m.group(2).strip()})
    for m in PARA_RE.finditer(tex):
        inv["paras"].append(m.group(1).strip())
    inv["labels"] = set(LABEL_RE.findall(tex))
    inv["cites"] = set(c for m in CITE_RE.finditer(tex)
                       for c in m.group(1).split(","))
    inv["E_items"] = sorted(set(E_RE.findall(tex)))
    inv["tables"] = len(re.findall(r"\\begin\{table", tex))
    inv["figures"] = len(re.findall(r"\\begin\{figure", tex))
    inv["n_paras"] = len(inv["paras"])
    return inv


def key_env(e):
    return (e["label"] or e["title"] or e["kind"]).lower()


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


report = {"versions": {}, "transitions": [], "v21_coverage": {},
          "condensation": []}
invs = {}
for name, path in VERS:
    invs[name] = inventory(path)
    report["versions"][name] = {
        "envs": len(invs[name]["envs"]),
        "env_kinds": {k: sum(1 for e in invs[name]["envs"]
                             if e["kind"] == k)
                      for k in sorted({e["kind"] for e in invs[name]["envs"]})},
        "sections": len(invs[name]["secs"]),
        "paragraphs": invs[name]["n_paras"],
        "E_items": invs[name]["E_items"],
        "tables": invs[name]["tables"], "figures": invs[name]["figures"],
        "words": invs[name]["n_words"],
        "cites": len(invs[name]["cites"])}

# ---------------- transitions: dropped items ----------------
for (n0, _), (n1, _) in zip(VERS, VERS[1:]):
    a, b = invs[n0], invs[n1]
    dropped_envs = [e for e in a["envs"]
                    if not any(key_env(e) == key_env(f) for f in b["envs"])]
    dropped_secs = [s for s in a["secs"]
                    if not any(norm(s["title"]) == norm(t["title"])
                               for t in b["secs"])]
    dropped_paras = [p for p in a["paras"]
                     if not any(norm(p) == norm(q) for q in b["paras"])]
    report["transitions"].append({
        "from": n0, "to": n1,
        "dropped_envs": [{"kind": e["kind"], "title": e["title"],
                          "label": e["label"]} for e in dropped_envs],
        "dropped_sections": dropped_secs,
        "dropped_paragraphs": dropped_paras,
        "words": [a["n_words"], b["n_words"]],
    })

# ---------------- v21 coverage ----------------
v21_path = os.path.join(BASE, "scripts", "journal_manuscript.tex")
comp_path = os.path.join(BASE, "scripts", "companion_categorical.tex")
inv21 = inventory(v21_path)
invC = inventory(comp_path)
invH = invs["v2_828c89a_20pp"]
v2_text = strip_comments(open(VERS[-1][1]).read())
comp_text = strip_comments(open(comp_path).read())

missing = []
for e in inv21["envs"]:
    k = e["label"] or e["title"]
    if not k:
        continue
    kn = norm(k)
    in_v2 = (e["label"] and e["label"] in invH["labels"]) or \
            kn in norm(v2_text)
    in_comp = (e["label"] and e["label"] in invC["labels"]) or \
              kn in norm(comp_text)
    if not in_v2 and not in_comp:
        missing.append({"kind": e["kind"], "title": e["title"],
                        "label": e["label"]})
report["v21_coverage"] = {
    "v21_envs": len(inv21["envs"]),
    "v21_sections": len(inv21["secs"]),
    "companion_envs": len(invC["envs"]),
    "v2_envs": len(invH["envs"]),
    "v21_envs_not_found_verbatim_in_v2_or_companion": missing,
    "note": "verbatim label/title match only; companion Sec. 2 records "
            "the authoritative dispositions (frozen-v21 items are "
            "preserved by design, not by verbatim inclusion)",
}

# ---------------- condensation: paragraph survival ----------------
def paras_full(path):
    tex = strip_comments(open(path).read())
    # split on blank lines; keep blocks > 40 words as "content blocks"
    blocks = re.split(r"\n\s*\n", tex)
    out = {}
    for b in blocks:
        w = len(re.findall(r"[A-Za-z]{2,}", b))
        if w > 40:
            head = norm(" ".join(re.findall(r"[A-Za-z]{2,}", b)[:25]))
            out[head] = (w, b)
    return out


for (n0, p0), (n1, p1) in zip(VERS, VERS[1:]):
    a, b = paras_full(p0), paras_full(p1)
    surv, shrunk = 0, []
    for h, (w, blk) in a.items():
        if h in b:
            surv += 1
            if b[h][0] < 0.75 * w:
                shrunk.append({"head": h[:60], "was": w, "now": b[h][0]})
    report["condensation"].append({
        "from": n0, "to": n1,
        "blocks_before": len(a), "blocks_after": len(b),
        "verbatim_surviving": surv,
        "shrunk_gt25pct": shrunk[:30],
    })

with open(os.path.join(OUT, "v2_content_loss_scan.json"), "w") as f:
    json.dump(report, f, indent=1)

# ---------------- console summary ----------------
print("=== version stats ===")
for n in report["versions"]:
    v = report["versions"][n]
    print(f"{n:22s} envs={v['envs']:3d} sec={v['sections']:3d} "
          f"para={v['paragraphs']:3d} E={len(v['E_items']):2d} "
          f"tab={v['tables']} fig={v['figures']} "
          f"words={v['words']:6d} cites={v['cites']}")
print("\n=== transitions: dropped envs/sections/paras ===")
for t in report["transitions"]:
    print(f"{t['from']} -> {t['to']}: envs -{len(t['dropped_envs'])}, "
          f"secs -{len(t['dropped_sections'])}, "
          f"paras -{len(t['dropped_paragraphs'])}, "
          f"words {t['words'][0]} -> {t['words'][1]}")
    for e in t["dropped_envs"][:12]:
        print(f"    ENV  {e['kind']:12s} {e['title'][:70]} ({e['label']})")
    for s in t["dropped_sections"][:12]:
        print(f"    SEC  {s['level']:12s} {s['title'][:70]}")
    for p in t["dropped_paragraphs"][:15]:
        print(f"    PARA {p[:80]}")
print("\n=== v21 coverage ===")
print(f"v21: {report['v21_coverage']['v21_envs']} envs, "
      f"{report['v21_coverage']['v21_sections']} sections")
print(f"not found verbatim in v2 or companion: "
      f"{len(report['v21_coverage']['v21_envs_not_found_verbatim_in_v2_or_companion'])}")
for e in report["v21_coverage"]["v21_envs_not_found_verbatim_in_v2_or_companion"][:25]:
    print(f"    {e['kind']:12s} {e['title'][:70]} ({e['label']})")
print("\n=== condensation (content blocks) ===")
for c in report["condensation"]:
    print(f"{c['from']} -> {c['to']}: blocks {c['blocks_before']} -> "
          f"{c['blocks_after']}, verbatim surviving {c['verbatim_surviving']}, "
          f"shrunk>25%: {len(c['shrunk_gt25pct'])}")
    for s in c["shrunk_gt25pct"][:10]:
        print(f"    SHRUNK {s['head'][:55]} was={s['was']} now={s['now']}")
