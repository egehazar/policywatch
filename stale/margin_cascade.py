"""Exploratory (not pre-registered): does addendum 1's "clear" label hold for the cascade's suggestions?

Addendum 1 validated the label with Kev scoring every piece of a document (part D: 53 of 200 clear, hit@1 .943). The
wider pages use the reranker-first cascade (part D's D1), where Kev scores only each case's reranker top 10, so a
suggestion's margin there is Kev's top minus its second highest among those 10. This applies addendum 1's fixed cut
(.30, chosen on parts A and B) and its rule to part D's cascade arm. The cut was not tuned on part D, but the rule was
not registered for the cascade, and this runs after part D's result was seen: it can inform the page, not decide it.
No model call: the scores are in stale/out/contrib_kev.json and contrib_base.json.
Usage  py -m stale.margin_cascade   -> stale/out/margin_cascade.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.dirname(HERE))
from stale.relocate import hit
from stale.reloc_margin import summary, margin, CLEAR, MIN_N, BAR, LOWER
from stale.cascade import top_k


def rows():
    D = json.load(open(os.path.join(OUT, 'contrib_docs.json'), encoding='utf-8'))['docs']
    K = json.load(open(os.path.join(OUT, 'contrib_kev.json'), encoding='utf-8'))
    B = json.load(open(os.path.join(OUT, 'contrib_base.json'), encoding='utf-8'))
    out = []
    for d in D:
        for it in d['items']:
            q = it['question']; k = [s[q] for s in K[d['doc']]['scores']]; keep = top_k(B['RERANK'][d['doc']][q])
            c = [k[i] if i in keep else -1.0 for i in range(len(k))]          # as relocate_d.evaluate ranks the cascade
            h = hit(c, it['gold'])[0]
            out.append({'point': it['point'], 'doc': d['service'], 'margin': round(margin([k[i] for i in keep]), 4),
                        'hit1': h[1], 'hit3': h[3]})
    return out


def main():
    s = summary(rows())
    ok = s['clear'] >= MIN_N and s['_clear_hit1_raw'] is not None and s['_clear_hit1_raw'] >= BAR and s.get('_lower_raw', -1) >= LOWER
    s['rule_would_read'] = 'LABEL ADOPTED' if ok else 'NO LABEL'
    s.pop('_lower_raw', None); s.pop('_clear_hit1_raw', None)
    s['note'] = 'exploratory: addendum 1 rule applied to the cascade arm after part D was seen'
    with open(os.path.join(OUT, 'margin_cascade.json'), 'w', encoding='utf-8') as f: json.dump(s, f, indent=1)
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main()
