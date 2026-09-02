#!/usr/bin/env python3
"""Trace the non-surviving content blocks (12pp -> 20pp) identified by
scan_content_loss.py: for each 12pp block that did not survive verbatim
into the 20pp version, check whether its content reappears in modified
form (fuzzy containment) in the 20pp text.  Classification:
  REWORDED   : >=60% of the block's distinctive 5-grams appear in the
               20pp text (content present, wording changed)
  PARTIAL    : 25-60% of distinctive 5-grams appear
  LOST       : <25% of distinctive 5-grams appear
"""
import re
import sys


def strip_comments(tex):
    return "\n".join(l.split("%", 1)[0] if "%" in l and not l.strip().startswith("%")
                     else l for l in tex.splitlines())


def norm_words(tex):
    return re.findall(r"[A-Za-z]{2,}", strip_comments(tex).lower())


def blocks_of(path):
    tex = strip_comments(open(path).read())
    out = []
    for b in re.split(r"\n\s*\n", tex):
        w = len(re.findall(r"[A-Za-z]{2,}", b))
        if w > 40:
            out.append((w, b))
    return out


def five_grams(words):
    return set(tuple(words[i:i + 5]) for i in range(len(words) - 4))


def main():
    old_path, new_path = "/tmp/mscan/v2_f3342b1.tex", "/tmp/mscan/v2_828c89a.tex"
    old_blocks = blocks_of(old_path)
    new_words = norm_words(open(new_path).read())
    new_grams = five_grams(new_words)

    # also fuzzy: allow 4-gram containment as secondary signal
    new4 = set(tuple(new_words[i:i + 4]) for i in range(len(new_words) - 3))

    n_reworded = n_partial = n_lost = 0
    lost_report = []
    for w, blk in old_blocks:
        words = re.findall(r"[A-Za-z]{2,}", blk.lower())
        grams = five_grams(words)
        if not grams:
            continue
        hit = sum(1 for g in grams if g in new_grams)
        frac = hit / len(grams)
        if frac >= 0.60:
            n_reworded += 1
        elif frac >= 0.25:
            n_partial += 1
        else:
            n_lost += 1
            hit4 = sum(1 for g in set(tuple(words[i:i + 4]) for i in range(len(words) - 3))
                       if g in new4)
            lost_report.append((w, frac, hit4, blk))
    total = n_reworded + n_partial + n_lost
    print(f"12pp blocks >40 words: {total}")
    print(f"  REWORDED (>=60% 5-grams survive): {n_reworded}")
    print(f"  PARTIAL  (25-60%):                {n_partial}")
    print(f"  LOST     (<25%):                  {n_lost}")
    print()
    for w, frac, hit4, blk in lost_report:
        head = " ".join(re.findall(r"[A-Za-z]{2,}", blk)[:18])
        print(f"--- LOST block ({w} words, 5-gram survival {frac:.2f}, "
              f"4-gram hits {hit4}) ---")
        print(f"    {head} ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
