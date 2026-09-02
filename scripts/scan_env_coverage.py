#!/usr/bin/env python3
"""Strict coverage audit: for every theorem-like env and every proof env in v1,
trace (a) env survival (label/title), (b) body coverage by word 8-grams
against the current two-paper union, (c) proof-env pairing: which v1 proofs
prove which v1 statements, and whether the current papers carry a proof for
the surviving statements.
"""
import re, json

V1 = '/home/z/my-project/scripts/journal_manuscript.tex'
V2 = '/home/z/my-project/scripts/journal_manuscript_v2.tex'
COMP = '/home/z/my-project/scripts/companion_categorical.tex'

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read().split('\n')

def norm_line(line):
    line = re.sub(r'(?<!\\)%.*$', '', line)
    return line.strip()

def norm_lines(raw):
    return [norm_line(l) for l in raw if norm_line(l)]

THEOREM_ENVS = ['theorem','lemma','proposition','corollary','definition',
                'conjecture','construction','example','remark','assumption']

def grams(text, n=8):
    words = re.findall(r'[A-Za-z\\{}]+', text)
    return set(tuple(words[i:i+n]) for i in range(max(0, len(words)-n+1)))

def envs_of(lines, path):
    """Return list of (env, label, title, startline, endline, body_lines)."""
    out = []
    stack = []
    raw = read(path)
    # map normalized index -> original number
    idx = []
    nlines = []
    for ono, l in enumerate(raw, 1):
        nl = norm_line(l)
        if nl:
            idx.append(ono)
            nlines.append(nl)
    opens = []
    for i, l in enumerate(nlines):
        m = re.match(r'\\begin\{(\w+)\}(?:\[(.*?)\])?(.*?)$', l)
        if m and (m.group(1) in THEOREM_ENVS or m.group(1) == 'proof'):
            lab = None
            lm = re.search(r'\\label\{([^}]+)\}', l)
            if lm: lab = lm.group(1)
            opens.append([m.group(1), lab, m.group(2) or '', i])
    for env, lab, title, i in opens:
        # find matching end (first \end{env} after i)
        end = None
        depth = 1
        for j in range(i+1, len(nlines)):
            if re.match(r'\\begin\{'+env+r'\}', nlines[j]):
                depth += 1
            if re.match(r'\\end\{'+env+r'\}', nlines[j]):
                depth -= 1
                if depth == 0:
                    end = j
                    break
        if end is None:
            continue
        body = ' '.join(nlines[i+1:end])
        out.append({
            'env': env, 'label': lab, 'title': title.strip(),
            'lines': [idx[i], idx[end]],
            'body': body, 'nbody': len(body.split()),
        })
    return out

def main():
    v1 = envs_of(read(V1), V1)
    v2n = ' '.join(norm_lines(read(V2)))
    compn = ' '.join(norm_lines(read(COMP)))
    union = re.sub(r'\s+', ' ', v2n + ' ' + compn)
    union_grams = grams(union)

    results = []
    for e in v1:
        g = grams(e['body'])
        if g:
            cov = sum(1 for x in g if x in union_grams) / len(g)
        else:
            cov = 1.0 if len(e['body']) < 40 else 0.0
        lab_present = e['label'] and e['label'] in (v2n + compn)
        # title (first 6 words) presence
        twords = ' '.join(re.sub(r'[^\w\s]', ' ', e['title']).split()[:6])
        title_present = twords and twords in re.sub(r'[^\w\s]', ' ', union)
        results.append(dict(e, cov8=round(cov, 2),
                            label_present=bool(lab_present),
                            title_present=bool(title_present)))
    # proof pairing
    proofs = [r for r in results if r['env'] == 'proof']
    thms = [r for r in results if r['env'] != 'proof']
    # for each v1 proof, find the nearest preceding theorem-like env
    pairs = []
    for p in proofs:
        prev = [t for t in thms if t['lines'][0] < p['lines'][0]]
        tgt = prev[-1] if prev else None
        pairs.append({
            'proof_lines': p['lines'], 'proof_cov8': p['cov8'],
            'proof_title': p['title'][:70],
            'target_env': tgt['env'] if tgt else None,
            'target_label': tgt['label'] if tgt else None,
            'target_title': (tgt['title'][:70] if tgt else ''),
            'target_label_present': tgt['label'] and tgt['label'] in (v2n + compn),
            'target_cov8': tgt['cov8'] if tgt else None,
        })
    # theorem-like envs in v1 with NO v1 proof at all
    proved = set()
    for p in pairs:
        if p['target_label']:
            proved.add(p['target_label'])
    unproved_v1 = [t for t in thms if t['label'] not in proved]
    out = {
        'n_envs_v1': len(v1),
        'n_proofs_v1': len(proofs),
        'pairs': pairs,
        'unproved_in_v1': [
            {'env': t['env'], 'label': t['label'], 'title': t['title'][:80],
             'lines': t['lines'], 'cov8': t['cov8'],
             'label_present': t['label_present']}
            for t in unproved_v1],
        'envs': [
            {'env': r['env'], 'label': r['label'], 'title': r['title'][:80],
             'lines': r['lines'], 'nbody': r['nbody'], 'cov8': r['cov8'],
             'label_present': r['label_present']}
            for r in results],
    }
    with open('/home/z/my-project/download/deepseek_bridge/env_coverage_audit.json', 'w') as f:
        json.dump(out, f, indent=1)
    # console summary
    print(f"v1 envs: {len(v1)} (proofs: {len(proofs)})")
    print("\n== v1 proof envs and their targets ==")
    for p in pairs:
        flag = ''
        if p['proof_cov8'] < 0.3:
            flag += ' PROOF-LOST'
        if p['target_label'] and not p['target_label_present'] and (p['target_cov8'] or 0) < 0.3:
            flag += ' TARGET-LOST'
        print(f"  proof@{p['proof_lines']} cov={p['proof_cov8']:.2f} -> {p['target_env']}:{p['target_label'] or p['target_title'][:40]} (tgt present={bool(p['target_label_present'])}, tgt cov={p['target_cov8']}){flag}")
    print("\n== v1 theorem-like envs with NO v1 proof (selected) ==")
    for t in unproved_v1:
        if t['cov8'] < 0.3:
            print(f"  LOST {t['env']}:{t['label'] or ''} {t['title'][:60]} @{t['lines']} cov={t['cov8']}")

if __name__ == '__main__':
    main()
