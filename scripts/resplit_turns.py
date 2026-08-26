#!/usr/bin/env python3
"""Re-split the conversation using the full correct user-question list."""
import re
from pathlib import Path

txt = Path('/home/z/my-project/download/deepseek_text.txt').read_text(encoding='utf-8')

# The CORRECT user question list (from sidebar)
user_qs = [
    "shouldn't there be a perfectly reasonable, understandable, satisfactory explanation or why something rather than nothing exists?",
    "can u rigorously prove (possibly after several refining turns) something that automatically follows all knowledge discovered by humans but has not been stated or proven yet?",
    "no, not trivial, and it should virtually require all human knowledge",
    "math, physics, computer science, biology, philosophy. not a corollary, but some cross-domain unification that bridges gaps towards coherent math object rather than relying on loose analogies",
    "1- u are not limited to one chat. 2- all human knowledge is still finite!",
    "but is this truly novel?",
    "can't u go beyond raf? again, you aren't restricted to one pass, but to the best of your abilities, it must be groundbreaking novel",
    "can you take it another step beyond, while still maintaining the prospect of rigor, rather than loose analogies?",
    "can you rigorously bridge the entire topic to some other concept, like quantum computing? again, u can use as many turns as it takes.",
    "can u also rigorously bring abiogenisis into the picture? again, as many turns as it takes, but there should be a genuine prospect of rigor",
    "arrow of time?",
    "Rate-Distortion Theory &amp; Automata Theory",
]

# Find positions (in main body, before the sidebar listing near the end)
sidebar_start = txt.find("shouldn't there be a perfectly reasonable")  # first occurrence
# find the second occurrence — that's where the sidebar begins
sidebar_start = txt.find("shouldn't there be a perfectly reasonable", sidebar_start + 1)
print(f"Sidebar listing starts at position: {sidebar_start}")

body = txt[:sidebar_start]
print(f"Main body length: {len(body)}")

# Now find each user question in body
positions = []
lower = body.lower()
for q in user_qs:
    needle = q.lower().replace("&amp;", "&")
    idx = lower.find(needle)
    if idx >= 0:
        positions.append((idx, q))
        print(f"  found at {idx}: {q[:70]}")
    else:
        print(f"  NOT FOUND: {q[:70]}")

positions.sort()
positions.append((len(body), "END"))

outdir = Path('/home/z/my-project/download/turns2')
outdir.mkdir(exist_ok=True)
for i in range(len(positions) - 1):
    seg = body[positions[i][0]:positions[i+1][0]]
    fname = outdir / f"turn_{i+1:02d}.txt"
    fname.write_text(seg, encoding='utf-8')
    # Count "Thought for" markers
    thoughts = re.findall(r"Thought for \d+ seconds", seg)
    print(f"Turn {i+1}: {positions[i][1][:60]!r}  len={len(seg)}  thoughts={thoughts}")

print(f"\nTotal turns: {len(positions) - 1}")
