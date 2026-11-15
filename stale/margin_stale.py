"""Exploratory (not pre-registered): the "clear" label on the 141 real stale points, against the full-read gold.

Addendum 1's label (stale/reloc_margin.py: Kev's top p(yes) minus its second >= .30) was adopted on part D, where every
point's case is still stated by construction. On the 20 platforms' stale points the case may be stated in new words,
or no longer at all. This counts, against the full-read rater's gold (stale/PREREG_suggest.md; an LLM rater until the
human gate is answered), how often a Clear suggestion's top passage states the case, and how many Clear labels land on
points whose case the rater found no longer stated (always wrong). Pooled over points; no interval is claimed.
Usage  py -m stale.margin_stale   -> stale/out/margin_stale.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); FDIR = os.path.join(OUT, 'fullread')
sys.path.insert(0, os.path.dirname(HERE))
from stale.reloc_margin import margin, CLEAR


def main():
    key = json.load(open(os.path.join(FDIR, 'key.json'), encoding='utf-8'))
    G = json.load(open(os.path.join(FDIR, 'gold_opus.json'), encoding='utf-8'))['gold']
    S = {r['point']: r for r in map(json.loads, open(os.path.join(OUT, 'suggest_kev.jsonl'), encoding='utf-8'))}
    assert {r['archive_head'] for r in S.values()} == {key['archive_head']}, 'suggestions and gold on different archive heads'
    rows = []
    for d, items in key['plan'].items():
        for it in items:
            if it['kind'] != 'stale': continue
            gold = set(G[d][it['label']])
            for p in it['points']:
                s = S[p]; sc = [t['score'] for t in s['top']]
                rows.append({'point': p, 'doc': d, 'stated': bool(gold), 'margin': round(margin(sc), 4),
                             'hit1': float(s['top'][0]['piece'] in gold), 'hit3': float(any(t['piece'] in gold for t in s['top'][:3]))})
    C = [r for r in rows if r['margin'] >= CLEAR]; R = [r for r in rows if r['margin'] < CLEAR]
    f = lambda xs, k: round(sum(r[k] for r in xs) / len(xs), 3) if xs else None
    res = {'points': len(rows), 'stated': sum(r['stated'] for r in rows), 'clear': len(C),
           'clear_on_not_stated': sum(not r['stated'] for r in C),
           'clear_hit1': f(C, 'hit1'), 'clear_right': int(sum(r['hit1'] for r in C)),
           'rest': len(R), 'rest_hit1': f(R, 'hit1'), 'rest_hit3': f(R, 'hit3'),
           'stated_rest_hit1': f([r for r in R if r['stated']], 'hit1'),
           'note': 'exploratory; gold is an LLM rater (full read) until the human gate; pooled over points'}
    with open(os.path.join(OUT, 'margin_stale.json'), 'w', encoding='utf-8') as fh: json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
