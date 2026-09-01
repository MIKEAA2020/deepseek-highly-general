#!/usr/bin/env python3
"""Remove the accidentally duplicated v14b subsection from the manuscript
(P3 was applied twice due to a broken idempotency check)."""
from pathlib import Path

p = Path("/home/z/my-project/scripts/journal_manuscript.tex")
lines = p.read_text(encoding="utf-8").split("\n")

# Find both copy start indices (1-indexed line numbers -> 0-indexed)
idxs = [i for i, ln in enumerate(lines)
        if ln.startswith("\\subsection{v14b correction round: audit")]
assert len(idxs) == 2, f"expected 2 copies, found {len(idxs)}: {idxs}"

first, second = idxs
# copy2 block spans from the '% ====' comment line above `second`
# through the blank line just before \section{Main Proposition}
start = second - 1
assert lines[start].startswith("% ===="), lines[start]
# find the section line after `second`
sec = next(i for i in range(second, len(lines))
           if lines[i].startswith("\\section{Main Proposition}"))
# delete lines[start : sec-1]? No: delete [start, sec) but keep ONE blank line
# between copy1's end and the section. copy1 ends at `first`-block; after
# deletion, lines[first_block_end] (blank) then \section.
# The block to remove: from start (comment of copy2) to sec-1 (blank before
# section) inclusive.
end = sec  # exclusive
# ensure what we cut ends with a blank line
assert lines[end - 1].strip() == "", repr(lines[end - 1])
del lines[start:end]
# ensure exactly one blank line between previous content and \section
# (lines[start-1] is the blank after copy1; lines[start] is now \section)
assert lines[start].startswith("\\section{Main Proposition}"), lines[start]
assert lines[start - 1].strip() == "", repr(lines[start - 1])

p.write_text("\n".join(lines), encoding="utf-8")
print(f"Removed duplicate block: lines {start+1}..{end} (0-indexed {start}..{end-1})")
print(f"New total lines: {len(lines)}")
