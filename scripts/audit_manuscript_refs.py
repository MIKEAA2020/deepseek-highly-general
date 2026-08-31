#!/usr/bin/env python3
"""
Audit of dangling cross-references in the local manuscript.

Scope:
  - Local file: /tmp/my-project/scripts/journal_manuscript.tex
  - All \\label{...} definitions (single-arg, brace-delimited).
  - All reference macros that take a brace-delimited key list:
        \\ref, \\eqref, \\autoref, \\nameref, \\pageref, \\cpageref,
        \\cref, \\Cref, \\crefrange, \\Crefrange (with comma-separated multi-keys)
  - Multi-line splits handled by scanning the full file as one string.
  - Comments: lines starting with % are skipped AFTER unescaping \\%.

Outputs:
  - stdout summary
  - /home/z/my-project/download/audit_manuscript_refs_local.md (markdown report)
  - /home/z/my-project/download/audit_manuscript_refs_local.json (structured)
  - exit code 0 if clean, 1 if dangling refs found.
"""
from __future__ import annotations
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

MANUSCRIPT = Path("/tmp/my-project/scripts/journal_manuscript.tex")
OUT_MD = Path("/home/z/my-project/download/audit_manuscript_refs_local.md")
OUT_JSON = Path("/home/z/my-project/download/audit_manuscript_refs_local.json")

# Reference macros that take exactly one brace-delimited key list.
# We treat them uniformly: the first {...} group after the macro is the key list,
# which may be comma-separated (cleveref-style) or single-key (everything else).
REF_MACROS = [
    r"ref", r"eqref", r"autoref", r"nameref", r"pageref", r"cpageref",
    r"cref", r"Cref", r"crefrange", r"Crefrange",
]
# Macros that take TWO brace groups (e.g., \crefrange{a}{b}):
# We handle the first group only (the "from" key) and the second group (the "to" key)
# separately — both are reference targets.
RANGE_MACROS = [r"crefrange", r"Crefrange"]

LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
# For each non-range macro, capture the first brace group.
NON_RANGE_RE = re.compile(
    r"\\(?P<macro>" + "|".join(m for m in REF_MACROS if m not in RANGE_MACROS) + r")\{([^{}]+)\}"
)
# For range macros, capture both brace groups.
RANGE_RE = re.compile(
    r"\\(?P<macro>" + "|".join(RANGE_MACROS) + r")\{([^{}]+)\}\{([^{}]+)\}"
)
# Also \cref{a,b,c} style — handled by splitting the captured group on commas.


def strip_comments(text: str) -> str:
    """Remove LaTeX line comments (%...) while preserving escaped \\%."""
    out_lines = []
    for line in text.split("\n"):
        # Walk the line char by char; a % not preceded by \ starts a comment.
        i = 0
        out = []
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line):
                out.append(line[i:i + 2])
                i += 2
                continue
            if ch == "%":
                break  # rest of line is comment
            out.append(ch)
            i += 1
        out_lines.append("".join(out))
    return "\n".join(out_lines)


def collect_labels(text: str) -> dict[str, list[int]]:
    """Return {label_key: [line numbers where it's defined]}."""
    found: dict[str, list[int]] = defaultdict(list)
    for lineno, line in enumerate(text.split("\n"), start=1):
        for m in LABEL_RE.finditer(line):
            found[m.group(1).strip()].append(lineno)
    return found


def collect_refs(text: str) -> list[dict]:
    """Return a list of {macro, keys: [..], line: int} entries."""
    refs: list[dict] = []
    # Combine lines so multi-line refs are still scanned per-line for line numbers.
    for lineno, line in enumerate(text.split("\n"), start=1):
        # Range macros (two brace groups)
        for m in RANGE_RE.finditer(line):
            keys = []
            for grp in (m.group(2), m.group(3)):
                keys.extend([k.strip() for k in grp.split(",")])
            refs.append({"macro": m.group(1), "keys": keys, "line": lineno})
        # Non-range macros (one brace group)
        for m in NON_RANGE_RE.finditer(line):
            keys = [k.strip() for k in m.group(2).split(",")]
            refs.append({"macro": m.group(1), "keys": keys, "line": lineno})
    return refs


def main() -> int:
    if not MANUSCRIPT.exists():
        print(f"ERROR: manuscript not found at {MANUSCRIPT}", file=sys.stderr)
        return 2
    raw = MANUSCRIPT.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)

    labels = collect_labels(text)
    refs = collect_refs(text)

    # Build report
    dangling: list[dict] = []      # refs with no matching label
    used_labels: set[str] = set()  # labels referenced at least once
    multi_def: list[dict] = []     # labels defined more than once
    for key, linenos in labels.items():
        if len(linenos) > 1:
            multi_def.append({"label": key, "lines": linenos})
    for r in refs:
        for k in r["keys"]:
            if k not in labels:
                dangling.append({
                    "macro": r["macro"], "key": k, "line": r["line"]
                })
            else:
                used_labels.add(k)

    unused_labels = sorted(set(labels.keys()) - used_labels)

    # Prefix buckets (high-signal — def:, sec:, eq:, fig:, tab:, thm:, lem:, cor:, prop:, rem:, conj:, ass:, constr:)
    prefix_buckets = defaultdict(list)
    for d in dangling:
        prefix = d["key"].split(":", 1)[0] if ":" in d["key"] else "(no-prefix)"
        prefix_buckets[prefix].append(d)

    # Print to stdout
    n_total_refs = sum(len(r["keys"]) for r in refs)
    print("=" * 70)
    print("MANUSCRIPT REFERENCE AUDIT")
    print("=" * 70)
    print(f"Manuscript: {MANUSCRIPT}")
    print(f"Total \\label definitions:    {len(labels)}")
    print(f"Total \\label *occurrences* (multi-def counted): {sum(len(v) for v in labels.values())}")
    print(f"Total ref-macro *keys*:       {n_total_refs}")
    print(f"Total ref-macro *calls*:     {len(refs)}")
    print()
    print(f"Labels defined more than once: {len(multi_def)}")
    for d in multi_def[:10]:
        print(f"  DUP {d['label']:40s} at lines {d['lines']}")
    print()
    print(f" DANGLING REFERENCES (ref → missing label): {len(dangling)} ".center(70, "="))
    if dangling:
        by_prefix = Counter(d["key"].split(":", 1)[0] if ":" in d["key"] else "(no-prefix)" for d in dangling)
        print(f"  by prefix: {dict(by_prefix)}")
        for d in dangling[:50]:
            print(f"  line {d['line']:5d}: \\{d['macro']}{{{d['key']}}}")
        if len(dangling) > 50:
            print(f"  ... and {len(dangling) - 50} more (see markdown report)")
    else:
        print("  (none)")
    print()
    print(f" UNUSED LABELS (defined but never referenced): {len(unused_labels)} ".center(70, "="))
    for label in unused_labels[:50]:
        print(f"  {label:50s} defined at line(s) {labels[label]}")
    if len(unused_labels) > 50:
        print(f"  ... and {len(unused_labels) - 50} more (see markdown report)")
    print()
    print(f"Ref-macro usage by macro:")
    macro_counter = Counter(r["macro"] for r in refs)
    for m, n in sorted(macro_counter.items(), key=lambda x: -x[1]):
        print(f"  \\{m:12s} : {n}")

    # Write markdown report
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Manuscript Reference Audit\n\n")
        f.write(f"**Manuscript:** `{MANUSCRIPT}`\n\n")
        f.write(f"**Total `\\label` definitions:** {len(labels)}\n")
        f.write(f"**Total ref-macro keys:** {n_total_refs}\n")
        f.write(f"**Total ref-macro calls:** {len(refs)}\n\n")
        f.write(f"## Dangling references ({len(dangling)})\n\n")
        if dangling:
            f.write("| Line | Macro | Key |\n|---:|---|---|\n")
            for d in dangling:
                f.write(f"| {d['line']} | `\\{d['macro']}` | `{d['key']}` |\n")
        else:
            f.write("_(none)_\n")
        f.write(f"\n## Unused labels ({len(unused_labels)})\n\n")
        if unused_labels:
            f.write("| Label | Defined at line(s) |\n|---|---|\n")
            for label in unused_labels:
                f.write(f"| `{label}` | {labels[label]} |\n")
        else:
            f.write("_(none)_\n")
        f.write(f"\n## Labels defined more than once ({len(multi_def)})\n\n")
        if multi_def:
            f.write("| Label | Lines |\n|---|---|\n")
            for d in multi_def:
                f.write(f"| `{d['label']}` | {d['lines']} |\n")
        else:
            f.write("_(none)_\n")
        f.write(f"\n## Ref-macro usage\n\n")
        f.write("| Macro | Count |\n|---|---:|\n")
        for m, n in sorted(macro_counter.items(), key=lambda x: -x[1]):
            f.write(f"| `\\{m}` | {n} |\n")

    # Write JSON report
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "manuscript": str(MANUSCRIPT),
        "total_labels": len(labels),
        "total_ref_keys": n_total_refs,
        "total_ref_calls": len(refs),
        "dangling": dangling,
        "unused_labels": [{"label": l, "lines": labels[l]} for l in unused_labels],
        "multi_defined": multi_def,
        "ref_macro_usage": dict(macro_counter),
        "prefix_buckets_dangling": {k: v for k, v in prefix_buckets.items()},
    }, indent=2), encoding="utf-8")

    print(f"\nWrote:\n  {OUT_MD}\n  {OUT_JSON}")
    return 1 if dangling else 0


if __name__ == "__main__":
    sys.exit(main())
