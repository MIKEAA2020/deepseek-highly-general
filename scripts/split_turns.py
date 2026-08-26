#!/usr/bin/env python3
"""Split the DeepSeek answer text by user-question markers so we can read turn-by-turn."""
import re
from pathlib import Path

txt = Path('/home/z/my-project/download/deepseek_answer.txt').read_text(encoding='utf-8')

# The user questions we already know from the tail:
user_questions = [
    "shouldn't there be a perfectly reasonable, understandable, satisfactory explanation or why something rather than nothing exists?",
    "can u rigorously prove (possibly after several refining turns) something that automatically follows all knowledge discovered by humans but has not been stated or proven yet?",
    "no, not trivial, and it should virtually require all human knowledge",
    "1- u are not limited to one chat. 2- all human knowledge is still finite!",
    "but is this truly novel?",
    "can't u go beyond raf? again, you aren't restricted to one pass, but to the best of your abilities, it must be groundbreaking novel",
    "can you take it another step beyond, while still maintaining the prospect of rigor, rather than loose analogies?",
    "can you rigorously bridge the entire topic to some other concept, like quantum computing? again, u can use as many turns as it takes.",
    "can u also rigorously bring abiogenisis into the picture? again, as many turns as it takes, but there should be a genuine prospect of rigor",
    "arrow of time?",
    "Rate-Distortion Theory & Automata Theory",
]

# Find positions of each user question (case-insensitive)
positions = []
lower = txt.lower()
for q in user_questions:
    idx = lower.find(q.lower())
    if idx >= 0:
        positions.append((idx, q))
positions.sort()
print(f"Found {len(positions)} of {len(user_questions)} user questions at positions:")
for p, q in positions:
    print(f"  {p}: {q[:80]}")

print()
print("=" * 70)
print("TOTAL TEXT LENGTH:", len(txt))
print("=" * 70)

# Print the segment around RAF
raf_idx = txt.lower().find("raf")
print(f"\nFirst 'raf' occurrence at index {raf_idx}")
print(f"Context around it:")
start = max(0, raf_idx - 500)
end = min(len(txt), raf_idx + 3000)
print(txt[start:end])
