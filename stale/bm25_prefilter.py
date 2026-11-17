"""Exploratory, no model run: would a BM25 first filter in front of the reranker have changed the cascade?
(stale/RESULT_missing_wide.md, Cost: "A cheaper first filter in front of the reranker (BM25 takes milliseconds) would
cut its 5.9 h; not tested.")

On the remaining-documents run's 20 documents (stale/missing_wide.py), for each case and each k: keep BM25's top k
passages (case title against passage), let the reranker pick its top 3 among only those, and compare with the
reranker's top 3 over every passage (the shortlist Kev read). Reported per k:
- reranker cells needed (k per case instead of every passage) and the share of the run's cells that is;
- cases whose shortlist is unchanged;
- of the page's 200 suggestions (Kev's best shortlisted passage per case), how many keep that passage on the new
  shortlist; for the rest Kev would have to read new passages (not run, so their new rank is unknown).
-> stale/out/bm25_prefilter.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import TOP, best
from stale.missing2 import shortlist
from stale.missing_page import approved
from stale import missing_wide
from stale.relocate import bm25 as bm25_scores

KS = (3, 5, 10, 15, 20, 30)


def top(rows, c, keep, n=3):
    return sorted(sorted(keep, key=lambda k: (-rows[k][c], k))[:n])


def main():
    D = json.load(open(missing_wide.DOCS, encoding='utf-8'))['docs']
    RR = json.load(open(missing_wide.F['RERANK'], encoding='utf-8')); KV = json.load(open(missing_wide.F['KEV'], encoding='utf-8'))
    cells = sum(len(d['pieces']) * len(d['cases']) for d in D)
    res = {'documents': len(D), 'cases': sum(len(d['cases']) for d in D), 'reranker_cells': cells, 'by_k': {}}
    page = []
    for d in D:
        neg = [c for c in d['negatives'] if c.strip() not in approved(d['doc'].split('/', 1)[0])]
        sc = {c: best(KV[d['doc']], c) for c in neg}
        page += [(d['doc'], c, sc[c][1]) for c in sorted(neg, key=lambda c: -sc[c][0])[:TOP]]
    bm = {d['doc']: {c: bm25_scores(c, d['pieces']) for c in d['cases']} for d in D}
    for k in KS:
        same = need = kept = 0
        for d in D:
            n = len(d['pieces']); rows = RR[d['doc']]
            for c in d['cases']:
                b = bm[d['doc']][c]; keep = sorted(range(n), key=lambda i: (-b[i], i))[:k]
                need += min(k, n); same += top(rows, c, keep) == shortlist(rows, c)
        for doc, c, i in page:
            dd = next(x for x in D if x['doc'] == doc); b = bm[doc][c]
            keep = sorted(range(len(dd['pieces'])), key=lambda j: (-b[j], j))[:k]
            kept += i in top(RR[doc], c, keep)
        res['by_k'][k] = {'reranker_cells': need, 'share_of_cells': round(need / cells, 3),
                          'shortlist_unchanged': same, 'shortlist_unchanged_share': round(same / res['cases'], 3),
                          'page_passage_kept': kept, 'page_suggestions': len(page)}
        print(k, res['by_k'][k])
    with open(os.path.join(OUT, 'bm25_prefilter.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
