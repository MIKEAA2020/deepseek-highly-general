#!/usr/bin/env python3
"""
Sentence-level content-loss scan (user round 2026-09-02, final pass).

Question: did the journal passes (PLOS formatting @5219ef0, BMB
retarget + companion restructure @9b3e4aa, declarations round) lose
or condense any earlier content, and is anything from earlier drafts
worth incorporating (as-is or adapted)?

Sources (earlier drafts):
  v21      : scripts/journal_manuscript.tex @ HEAD (frozen legacy)
  v2_e32   : journal_manuscript_v2.tex @ e6a0c61 (22 pp, pre-journal pass)
  v2_plos  : journal_manuscript_v2.tex @ 5219ef0 (21 pp, PLOS-formatted)
  comp_pre : companion_categorical.tex @ e6a0c61 (verbatim-extraction 33 pp)
Targets (current working tree):
  v2_cur   : scripts/journal_manuscript_v2.tex
  comp_cur : scripts/companion_categorical.tex

Method: strip comments/math/commands -> (section, sentence) fragments;
5-gram survival fraction of every source fragment in the union of the
two current papers; plus environment (theorem/def/...) coverage of v21
and of the pre-restructure companion. Dropped and heavily-reworded
fragments are listed for manual triage.
"""
import json
import os
import re
import subprocess

BASE = "/home/z/my-project"
OUT = os.path.join(BASE, "download", "deepseek_bridge")

MATH_ENVS = ["equation", "equation*", "align", "align*", "gather",
             "gather*", "multline", "multline*", "displaymath", "math",
             "eqnarray", "eqnarray*"]
ENV_RE = re.compile(
    r"\\begin\{(theorem|lemma|proposition|corollary|conjecture|"
    r"definition|remark|example|construction|assumption)\}"
    r"(?:\[([^\]]*)\])?")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")


def git_show(rev, path):
    return subprocess.run(
        ["git", "-C", BASE, "show", f"{rev}:{path}"],
        capture_output=True, text=True, check=True).stdout


def strip_comments(tex):
    out = []
    for line in tex.splitlines():
        # remove full-line and trailing comments, honoring escaped \%
        res = ""
        i = 0
        while i < len(line):
            c = line[i]
            if c == "\\" and i + 1 < len(line):
                res += line[i:i+2]
                i += 2
                continue
            if c == "%":
                break
            res += c
            i += 1
        out.append(res)
    return "\n".join(out)


def clean_text(tex):
    t = strip_comments(tex)
    for env in MATH_ENVS:
        t = re.sub(r"\\begin\{" + re.escape(env) + r"\}.*?\\end\{"
                   + re.escape(env) + r"\}", " MATH ", t, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", " MATH ", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", " MATH ", t)
    t = re.sub(r"\\\(.*?\\\)", " MATH ", t, flags=re.S)
    t = re.sub(r"\\\[.*?\\\]", " MATH ", t, flags=re.S)
    # drop commands (with optional args), keep their brace contents
    t = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\[^a-zA-Z]", " ", t)
    t = re.sub(r"[{}~]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t


def norm_words(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def fragments(tex):
    """-> list of (section, [words]) for sentences with >= 6 words."""
    t = strip_comments(tex)
    # walk sections on the raw text, clean each section separately
    sec_marks = list(re.finditer(r"\\section\*?\{([^}]*)\}", t))
    out = []
    if not sec_marks:
        cleaned = clean_text(t)
        for sent in re.split(r"(?<=[.!?])\s+", cleaned):
            w = norm_words(sent)
            if len(w) >= 6:
                out.append(("", w))
        return out
    bounds = [(m.start(), m.group(1).strip()) for m in sec_marks]
    bounds.append((len(t), "__END__"))
    for (s0, title), (s1, _) in zip(bounds, bounds[1:]):
        body = t[s0:s1]
        cleaned = clean_text(body)
        for sent in re.split(r"(?<=[.!?])\s+", cleaned):
            w = norm_words(sent)
            if len(w) >= 6:
                out.append((title, w))
    return out


def grams(words, n=5):
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def union_gram_set(texts):
    g = set()
    for tex in texts:
        for _, w in fragments(tex):
            g |= grams(w)
    return g


def env_inventory(tex):
    inv = []
    for m in ENV_RE.finditer(strip_comments(tex)):
        label = None
        tail = tex[m.end():m.end()+200]
        lm = LABEL_RE.search(tail)
        if lm:
            label = lm.group(1)
        inv.append({"kind": m.group(1),
                    "title": (m.group(2) or "").strip(), "label": label})
    return inv


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# ---------------- load ----------------
SRC = {
    "v21": open(os.path.join(BASE, "scripts",
                             "journal_manuscript.tex")).read(),
    "v2_e32": git_show("e6a0c61", "scripts/journal_manuscript_v2.tex"),
    "v2_plos": git_show("5219ef0", "scripts/journal_manuscript_v2.tex"),
    "comp_pre": git_show("e6a0c61", "scripts/companion_categorical.tex"),
}
TGT = {
    "v2_cur": open(os.path.join(BASE, "scripts",
                                "journal_manuscript_v2.tex")).read(),
    "comp_cur": open(os.path.join(BASE, "scripts",
                                  "companion_categorical.tex")).read(),
}

report = {"summary": {}, "sources": {}, "env_coverage": {}}

union = union_gram_set(TGT.values())
report["summary"]["union_5grams"] = len(union)
report["summary"]["union_fragments"] = sum(
    len(fragments(t)) for t in TGT.values())

# ---------------- per-source sentence survival ----------------
for name, tex in SRC.items():
    frs = fragments(tex)
    n_words = sum(len(w) for _, w in frs)
    dropped, heavy, light, survived = [], [], 0, 0
    for sec, w in frs:
        g = grams(w)
        if not g:
            continue
        f = len(g & union) / len(g)
        sent = " ".join(w)
        if f == 0:
            dropped.append({"sec": sec, "words": len(w), "text": sent[:300]})
        elif f < 0.5:
            heavy.append({"sec": sec, "frac": round(f, 2), "words": len(w),
                          "text": sent[:300]})
        elif f < 1:
            light += 1
        else:
            survived += 1
    tot = len(frs)
    report["sources"][name] = {
        "fragments": tot, "sentence_words": n_words,
        "survived": survived, "reworded_light": light,
        "reworded_heavy": len(heavy), "dropped": len(dropped),
        "dropped_list": dropped, "heavily_reworded_list": heavy[:80],
    }
    print(f"{name:9s}: {tot:5d} frags | survived {survived:5d} "
          f"({100*survived/max(tot,1):.1f}%) | light {light:4d} | "
          f"heavy {len(heavy):4d} | dropped {len(dropped):4d}")

# ---------------- environment coverage ----------------
def env_cover(inv, texts):
    txts = [norm(strip_comments(t)) for t in texts]
    labels = set()
    for t in texts:
        labels |= set(LABEL_RE.findall(strip_comments(t)))
    missing = []
    for e in inv:
        k = e["label"] or e["title"]
        if not k:
            continue
        kn = norm(k)
        found = (e["label"] and e["label"] in labels) or \
                any(kn and kn in tn for tn in txts)
        if not found:
            missing.append(e)
    return missing


inv21 = env_inventory(SRC["v21"])
inv_pre = env_inventory(SRC["comp_pre"])
inv_plos = env_inventory(SRC["v2_plos"])
report["env_coverage"] = {
    "v21_envs": len(inv21),
    "v21_missing_in_current_union": env_cover(inv21, TGT.values()),
    "comp_pre_envs": len(inv_pre),
    "comp_pre_missing_in_current_companion": env_cover(
        inv_pre, [TGT["comp_cur"]]),
    "v2_plos_envs": len(inv_plos),
    "v2_plos_missing_in_current_v2": env_cover(inv_plos, [TGT["v2_cur"]]),
}
print("\nv21 envs:", len(inv21), "| missing in current union:",
      len(report["env_coverage"]["v21_missing_in_current_union"]))
for e in report["env_coverage"]["v21_missing_in_current_union"][:30]:
    print(f"    {e['kind']:12s} {e['title'][:60]} ({e['label']})")
print("comp_pre envs:", len(inv_pre), "| missing in current companion:",
      len(report["env_coverage"]["comp_pre_missing_in_current_companion"]))
for e in report["env_coverage"]["comp_pre_missing_in_current_companion"][:30]:
    print(f"    {e['kind']:12s} {e['title'][:60]} ({e['label']})")
print("v2_plos envs:", len(inv_plos), "| missing in current v2:",
      len(report["env_coverage"]["v2_plos_missing_in_current_v2"]))
for e in report["env_coverage"]["v2_plos_missing_in_current_v2"][:30]:
    print(f"    {e['kind']:12s} {e['title'][:60]} ({e['label']})")

with open(os.path.join(OUT, "sentence_loss_scan.json"), "w") as f:
    json.dump(report, f, indent=1)
print("\nwritten:", os.path.join(OUT, "sentence_loss_scan.json"))
