"""Exploratory (written while the re-score ran, not fixed in advance). Pinterest's two documents changed on 2026-11-14
and were re-scored by stale/missing_watch.py: how much did the page's top-10 suggestions move, and how much of that is
the text change rather than the method change (the old page had Kev on every passage; the watch uses the cascade)?
And of the old top-10 suggestions the blind raters judged YES, how many are still in the new top 10?

py -m stale.missing_watch_diff -> stale/out/missing_watch_diff.json"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT); os.chdir(ROOT)
from stale import missing2, missing_watch as W, missing_page as MP
from stale.missing import best

OUT = 'stale/out'
L = lambda f: json.load(open(os.path.join(OUT, f), encoding='utf-8'))
OLD = {'missing_docs.json': ('missing_kev.json', 'missing_rerank.json', 'stale/audit_missing/verdicts.json', 'missing_key.json'),
       'missing2_docs.json': ('missing2_kev.json', 'missing2_rerank.json', 'stale/audit_missing2/verdicts.json', 'missing2_key.json')}


def top(rows, neg, k=10):
    sc = {c: best(rows, c)[0] for c in neg}; return sorted(neg, key=lambda c: -sc[c])[:k]


def cascade(kev_rows, rr_rows, cases):
    rows = [{c: -1.0 for c in cases} for _ in kev_rows]
    for c in cases:
        for i in missing2.shortlist(rr_rows, c): rows[i][c] = kev_rows[i][c]
    return rows


res = {}
cur = W.current('KEV')
for wd in L('missing_watch_docs.json')['docs']:
    doc = wd['doc']
    if doc not in cur: print(doc, 'not re-scored yet'); continue
    kf, rf, vf, keyf = OLD[wd['scored_in']]
    od = {d['doc']: d for d in L(wd['scored_in'])['docs']}[doc]
    plat = doc.split('/', 1)[0]; A = MP.approved(plat)
    neg = [c for c in od['negatives'] if c.strip() not in A]
    old_full = top(L(kf)[doc], neg)
    old_casc = top(cascade(L(kf)[doc], L(rf)[doc], od['cases']), neg)
    new_casc = top(cur[doc][1], neg)
    V = json.load(open(vf, encoding='utf-8')); K = L(keyf)
    yes = {K[c]['case'] for c in K if K[c]['doc'] == doc and 'KEV' in K[c]['arms'] and V[c]['verdict'] == 'YES'}
    yes_top = [c for c in old_full if c in yes]
    res[doc] = {'cases_suggested_from': len(neg),
                'old_page_vs_new_page_overlap': len(set(old_full) & set(new_casc)),
                'method_only (old text: every passage vs cascade)': len(set(old_full) & set(old_casc)),
                'text_only (cascade: old text vs new text)': len(set(old_casc) & set(new_casc)),
                'old_top10_rated_yes': len(yes_top),
                'of_those_still_in_new_top10': sum(c in new_casc for c in yes_top),
                'new_in_top10': [c.strip() for c in new_casc if c not in old_full],
                'dropped_from_top10': [c.strip() for c in old_full if c not in new_casc]}
print(json.dumps(res, indent=1, ensure_ascii=False))
json.dump(res, open(os.path.join(OUT, 'missing_watch_diff.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
