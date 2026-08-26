#!/usr/bin/env python3
"""Save each assistant turn to its own file based on Thought-for marker split."""
import re
from pathlib import Path

txt = Path('/home/z/my-project/download/deepseek_text.txt').read_text(encoding='utf-8')

markers = list(re.finditer(r'Thought for (\d+) seconds', txt))
sidebar_start = txt.find("shouldn't there be a perfectly reasonable", 5000)

outdir = Path('/home/z/my-project/download/turns_v2')
outdir.mkdir(exist_ok=True)

for i, m in enumerate(markers):
    end_pos = markers[i+1].start() if i+1 < len(markers) else sidebar_start
    answer = txt[m.end():end_pos]
    fn = outdir / f"a{i+1:02d}.txt"
    fn.write_text(answer, encoding='utf-8')

# Also save what's between the last Thought marker and the sidebar (tail)
print("Saved 11 assistant turns to turns_v2/")
print(f"Sidebar starts at: {sidebar_start}")
print(f"Last assistant answer goes up to: {end_pos}")
print(f"Tail (last user msg + boilerplate) length: {len(txt) - end_pos}")
print()
# Print the actual user message list in order
print("ACTUAL CONVERSATION STRUCTURE:")
print("Q1: shouldn't there be a perfectly reasonable... → A1 (29s)")
print("Q2: can u rigorously prove... → A2 (85s)")
print("Q3: no, not trivial... → A3 (72s)")
print("Q4: math, physics, CS, bio, philosophy... → A4 (97s) ← I MISSED THIS TURN!")
print("Q5: 1- u are not limited to one chat... → A5 (117s)")
print("Q6: but is this truly novel? → A6 (17s)")
print("Q7: can't u go beyond raf? → A7 (38s)")
print("Q8: can you take it another step beyond...? → A8 (25s)")
print("Q9: bridge to quantum computing? → A9 (24s)")
print("Q10: bring abiogenesis? → A10 (52s)")
print("Q11: arrow of time? → A11 (32s)")
print("Q12: Rate-Distortion Theory & Automata Theory → (UNANSWERED in share)")
