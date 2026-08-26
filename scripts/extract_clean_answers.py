#!/usr/bin/env python3
"""For each assistant turn, find the actual final answer (after the reasoning chain).
DeepSeek's reasoning ends with phrases like 'Let's produce final' or 'Let me craft'
followed by the actual response. Extract just that final portion for each turn.
"""
import re
from pathlib import Path

indir = Path('/home/z/my-project/download/turns_v2')
outdir = Path('/home/z/my-project/download/clean_answers')
outdir.mkdir(exist_ok=True)

# Markers that typically signal end of reasoning and start of final answer
# In order of likelihood
final_markers = [
    r"Let's produce final[^\n]*\n",
    r"Let's craft final[^\n]*\n",
    r"Let me craft final[^\n]*\n",
    r"Let's write final[^\n]*\n",
    r"Let's draft final[^\n]*\n",
    r"Let's draft:[^\n]*\n",
    r"Let me draft final[^\n]*\n",
    r"Now craft final[^\n]*\n",
    r"Let's craft response[^\n]*\n",
    r"Now let's craft[^\n]*\n",
    r"Final answer[^\n]*\n",
    r"Here is (?:the|a) final[^\n]*\n",
    r"^I'll now[^\n]*\n",
    r"^I will now[^\n]*\n",
    r"^I'll produce[^\n]*\n",
]

for fp in sorted(indir.glob("a*.txt")):
    txt = fp.read_text(encoding='utf-8')
    # Try each marker
    found = None
    for pat in final_markers:
        m = re.search(pat, txt, re.MULTILINE)
        if m:
            found = (pat, m.end())
            break
    if found:
        pat, start = found
        clean = txt[start:].strip()
    else:
        # Fall back: take last 60% of the text
        start = len(txt) * 2 // 5
        clean = txt[start:].strip()
        clean = f"[FALLBACK - no marker found, taking last 60%]\n\n{clean}"
    
    out_fp = outdir / fp.name.replace("a", "clean_a")
    out_fp.write_text(clean, encoding='utf-8')
    print(f"{fp.name}: reasoning={len(txt)} chars, clean answer={len(clean)} chars (marker: {found[0] if found else 'FALLBACK'})")
