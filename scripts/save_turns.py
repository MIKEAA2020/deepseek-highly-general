#!/usr/bin/env python3
"""Save each turn as its own file for easy reading."""
import re
from pathlib import Path

txt = Path('/home/z/my-project/download/deepseek_answer.txt').read_text(encoding='utf-8')

# These are start positions of user questions (the START of each user turn)
user_starts = [
    (0, "Q1: shouldn't there be a perfectly reasonable..."),
    (10928, "Q2: can u rigorously prove..."),
    (35304, "Q3: no, not trivial..."),
    (86353, "Q4: 1- u are not limited..."),
    (122408, "Q5: but is this truly novel?"),
    (129340, "Q6: can't u go beyond raf?"),
    (145045, "Q7: can you take it another step beyond..."),
    (159796, "Q8: bridge to quantum computing"),
    (177693, "Q9: bring abiogenesis"),
    (198720, "Q10: arrow of time?"),
    # Add end of file as the final boundary
    (len(txt), "END"),
]

# Save each segment (answer to question N) as a separate file
outdir = Path('/home/z/my-project/download/turns')
outdir.mkdir(exist_ok=True)

for i in range(len(user_starts) - 1):
    start_pos = user_starts[i][0]
    end_pos = user_starts[i + 1][0]
    segment = txt[start_pos:end_pos]
    fname = outdir / f"turn_{i+1:02d}.txt"
    fname.write_text(segment, encoding='utf-8')
    # Print summary
    print(f"Turn {i+1}: {user_starts[i][1][:60]}")
    print(f"  Length: {len(segment)} chars, saved to {fname.name}")
    
    # Find "Thought for" markers within this segment
    thoughts = list(re.finditer(r'Thought for \d+ seconds', segment))
    if thoughts:
        for t in thoughts:
            print(f"  {t.group()}")

# Save also the final tail (after last user question)
tail = txt[user_starts[-2][0]:]
Path('/home/z/my-project/download/turns/turn_final_tail.txt').write_text(tail, encoding='utf-8')

# Print specifically the section that likely contains the RAF discussion
# That should be Turn 5 (answer to "but is this truly novel?") — between positions 122408 and 129340
print("\n" + "=" * 70)
print("TURN 5 (likely the RAF construction):")
print("=" * 70)
turn5 = txt[122408:129340]
print(turn5)
