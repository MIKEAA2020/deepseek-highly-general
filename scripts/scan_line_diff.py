#!/usr/bin/env python3
"""Line-level normalized diff scan: v1 (frozen v21) vs current two-paper union.

Normalization: strip LaTeX comments, collapse whitespace, drop empty lines,
drop pure-preamble/bookkeeping lines. Then split into block units
(environments + paragraphs) and trace v1 blocks into the union:
  - verbatim (normalized substring match)
  - light reword (token-set overlap)
  - dropped
Output: JSON catalogue of dropped v1 blocks with env type, label, title,
line range, and first/last lines, for manual restoration triage.
"""
import re, json, subprocess, sys, difflib

V1 = '/home/z/my-project/scripts/journal_manuscript.tex'
V2 = '/home/z/my-project/scripts/journal_manuscript_v2.tex'
COMP = '/home/z/my-project/scripts/companion_categorical.tex'

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

def norm_line(line):
    # strip comments (naive but fine: % not preceded by \)
    line = re.sub(r'(?<!\\)%.*$', '', line)
    line = line.strip()
    return line

def norm_text(text):
    out = []
    for ln in text.split('\n'):
        ln = norm_line(ln)
        if not ln:
            continue
        out.append(ln)
    return out

DROP_PAT = re.compile(
    r'^(\\documentclass|\\usepackage|\\newtheorem|\\theoremstyle|\\newcommand|'
    r'\\renewcommand|\\DeclareMathOperator|\\graphicspath|\\hypersetup|'
    r'\\title|\\author|\\date|\\begin\{document\}|\\end\{document\}|'
    r'\\bibliographystyle|\\bibliography|\\input|\\include|\\appendix|'
    r'\\tableofcontents|\\newpage|\\clearpage|\\vspace|\\hspace|\\small|\\footnotesize|'
    r'\\begin\{figure\}|\\end\{figure\}|\\begin\{table\}|\\end\{table\})')

def keep_line(ln):
    if DROP_PAT.match(ln):
        return False
    return True

def blocks_from(lines, path):
    """Split into units: environments (begin..end) and paragraphs (blank-line
    groups after normalization are already collapsed; use heuristic:
    a block = sequence of lines starting at env begin or after a blank in
    original, up to next env begin / blank)."""
    units = []
    i = 0
    n = len(lines)
    raw = read(path).split('\n')
    # We operate on normalized lines but need original line numbers:
    # rebuild index map
    idx_map = []   # normalized line -> original line number
    for ono, ln in enumerate(raw, 1):
        nl = norm_line(ln)
        if not nl:
            continue
        idx_map.append(ono)
    assert len(idx_map) == len(lines)
    cur_start = 0
    for i, ln in enumerate(lines):
        if not keep_line(ln):
            continue
        is_env_begin = re.match(r'\\begin\{(theorem|lemma|proposition|corollary|definition|conjecture|construction|remark|example|proof|equation|align|align\*|displaymath)\}', ln)
        if is_env_begin and i != cur_start and i > cur_start:
            units.append((cur_start, i))
            cur_start = i
    units.append((cur_start, n))
    return units, idx_map

def unit_text(lines, a, b):
    return [ln for ln in lines[a:b] if keep_line(ln)]

def token_set(text_lines):
    toks = re.findall(r'[A-Za-z]+', ' '.join(text_lines).lower())
    return set(toks)

def main():
    v1_lines = norm_text(read(V1))
    v2_text = ' '.join(norm_text(read(V2)))
    comp_text = ' '.join(norm_text(read(COMP)))
    union = v2_text + ' ' + comp_text
    union_norm = re.sub(r'\s+', ' ', union)

    units, idx_map = blocks_from(v1_lines, V1)

    report = []
    for (a, b) in units:
        ul = unit_text(v1_lines, a, b)
        if not ul:
            continue
        if len(ul) < 3:      # trivial fragments
            continue
        txt = ' '.join(ul)
        txt_norm = re.sub(r'\s+', ' ', txt).strip()
        if len(txt_norm) < 60:   # too short to matter
            continue
        # verbatim coverage?
        verbatim = txt_norm in union_norm
        # token overlap (Jaccard on 2+ char words)
        ts = token_set(ul)
        if verbatim:
            status = 'verbatim'
            score = 1.0
        else:
            # coverage = fraction of v1-block tokens appearing in union text
            hit = sum(1 for t in ts if t in union_norm.lower())
            score = hit / max(1, len(ts))
            status = 'reworded' if score >= 0.8 else ('partial' if score >= 0.5 else 'dropped')
        # classify env
        m = re.match(r'\\begin\{(\w+)\}(?:\[([^\]]*)\])?', ul[0]) if ul else None
        env = m.group(1) if m else 'para'
        title = (m.group(2) if m else '') or ''
        lm = re.search(r'\\label\{([^}]+)\}', ' '.join(ul[:3]))
        label = lm.group(1) if lm else ''
        report.append({
            'v1_lines': [idx_map[a], idx_map[b-1]],
            'env': env, 'label': label, 'title': title.strip(),
            'nlines': b - a, 'status': status, 'tokscore': round(score, 3),
            'head': txt_norm[:160],
        })
    # summarize
    from collections import Counter
    cnt = Counter(r['status'] for r in report)
    env_cnt = Counter((r['status'], r['env']) for r in report)
    dropped = [r for r in report if r['status'] in ('dropped', 'partial')]
    out = {
        'totals': dict(cnt),
        'env_status': {f'{s}/{e}': c for (s, e), c in sorted(env_cnt.items())},
        'n_units': len(report),
        'dropped_units': dropped,
    }
    with open('/home/z/my-project/download/deepseek_bridge/line_diff_scan.json', 'w') as f:
        json.dump(out, f, indent=1)
    print('units:', len(report), dict(cnt))
    print('dropped+partial:', len(dropped))
    for r in dropped[:80]:
        print(f"  {r['v1_lines']} {r['env']:12s} {r['label'][:28]:28s} {r['tokscore']:.2f} {r['title'][:60] or r['head'][:60]}")

if __name__ == '__main__':
    main()
