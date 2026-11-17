"""Exploratory, after the page rating was scored (stale/RESULT_wide_rate.md); nothing here is a reading.

- The PAGE cards' rated YES share by Kev's p(yes) on the shown passage: does the score the page prints tell a curator
  which suggestions to read first?
- Per document: PAGE YES count against the number of cases ToS;DR already approved on the document (known positives)
  and the number of candidate cases: are the weak documents the well-covered ones?
-> stale/out/wide_rate_explore.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import best, wilson
from stale.wide_rate import KEY, FOLDERS, docs

BINS = ((0, .5), (.5, .7), (.7, .9), (.9, 1.01))


def spearman(x, y):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    a, b = rk(x), rk(y); ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    return num / (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** .5


def main():
    K = json.load(open(KEY, encoding='utf-8')); V = {}
    for f in FOLDERS.values(): V.update(json.load(open(os.path.join(f, 'verdicts.json'), encoding='utf-8')))
    D = {d['doc']: (d, rows) for _, d, rows, _ in docs()}
    res = {'by_kev_score': {}, 'by_doc': []}
    page = [c for c in K if 'PAGE' in K[c]['arms']]
    s = {c: D[K[c]['doc']][1]['PAGE'][K[c]['piece']][K[c]['case']] for c in page}
    for lo, hi in BINS:
        cs = [c for c in page if lo <= s[c] < hi]; y = sum(V[c]['verdict'] == 'YES' for c in cs)
        res['by_kev_score'][f'{lo:.1f}-{min(hi, 1):.1f}'] = {'cards': len(cs), 'yes': y, 'wilson95': wilson(y, len(cs))}
    for doc, (d, _) in sorted(D.items()):
        cs = [c for c in page if K[c]['doc'] == doc]
        res['by_doc'].append({'doc': doc, 'page_yes': sum(V[c]['verdict'] == 'YES' for c in cs),
                              'known_positives': len(d['positives']), 'candidates': len(d['negatives'])})
    B = res['by_doc']
    res['spearman_yes_vs_known_positives'] = round(spearman([b['page_yes'] for b in B], [b['known_positives'] for b in B]), 3)
    res['spearman_yes_vs_candidates'] = round(spearman([b['page_yes'] for b in B], [b['candidates'] for b in B]), 3)
    with open(os.path.join(OUT, 'wide_rate_explore.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'by_doc'}, indent=1))


if __name__ == '__main__':
    main()
