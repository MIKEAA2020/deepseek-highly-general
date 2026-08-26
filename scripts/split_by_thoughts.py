#!/usr/bin/env python3
"""Split conversation by 'Thought for N seconds' markers — each marks an assistant turn."""
import re
from pathlib import Path

txt = Path('/home/z/my-project/download/deepseek_text.txt').read_text(encoding='utf-8')

# Find all "Thought for N seconds" markers
markers = list(re.finditer(r'Thought for (\d+) seconds', txt))
print(f"Found {len(markers)} Thought-for markers (one per assistant turn)\n")

# Find the sidebar listing position (where user questions are listed compactly)
# The sidebar starts right after the final answer's last paragraph
# Find the position of the second occurrence of the first user question
sidebar_start = txt.find("shouldn't there be a perfectly reasonable", 5000)
print(f"Sidebar appears to start at: {sidebar_start}")
print(f"Total file length: {len(txt)}")
print()

# Extract each assistant turn = text from this marker to next marker
# But before each marker is the user's question
for i, m in enumerate(markers):
    # Find user message before this marker
    prev_end = markers[i-1].end() if i > 0 else 0
    # The user message is between prev_end and this marker's start
    user_msg = txt[prev_end:m.start()].strip()
    # Truncate to first 200 chars
    user_preview = user_msg[:200] if user_msg else "(no user msg)"
    print(f"--- Assistant turn {i+1} (thought {m.group(1)}s) ---")
    print(f"  PRECEDING USER MSG: {user_preview!r}")
    # Answer runs from end of this marker to start of next marker (or to sidebar)
    end_pos = markers[i+1].start() if i+1 < len(markers) else sidebar_start
    answer = txt[m.end():end_pos]
    print(f"  ANSWER LENGTH: {len(answer)} chars")
    print()
