"""Part D, addendum 1 (stale/PREREG_relocate_d_addendum1.md): is a suggestion whose top passage leads by a margin
"clear"? Secondary, read only for the curator page's label; it changes no reading of part D.

margin  Kev's highest p(yes) over a point's document pieces minus the second highest (0 when they tie)
clear   margin >= CLEAR
rule    LABEL ADOPTED if at least MIN_N points are clear, their hit@1 (ties in expectation) is at least .85, and the
        lower bound of its 95% cluster bootstrap over services (relocate2.boot) is at least .75. Otherwise NO LABEL.
Also reported for parts A and B (exploratory: the cut was chosen after seeing them).
Usage  py -m stale.reloc_margin            -> stale/out/contrib_margin.json (part D), and the A/B figures
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.dirname(HERE))
from stale.relocate import hit
from stale.relocate2 import boot

CLEAR = .30; MIN_N = 30; BAR = .85; LOWER = .75


def margin(scores):
    s = sorted(scores, reverse=True)
    return s[0] - s[1] if len(s) > 1 else 1.0


def rows_for(docs, kev, cluster):
    out = []
    for d in docs:
        for it in d['items']:
            k = [s[it['question']] for s in kev[d['doc']]['scores']]; h = hit(k, it['gold'])[0]
            out.append({'point': it['point'], 'doc': cluster(d), 'margin': round(margin(k), 4), 'hit1': h[1], 'hit3': h[3]})
    return out


def summary(rows):
    C = [r for r in rows if r['margin'] >= CLEAR]; R = [r for r in rows if r['margin'] < CLEAR]
    out = {'points': len(rows), 'clear': len(C), 'clear_share': round(len(C) / len(rows), 3),
           'clear_hit1': round(sum(r['hit1'] for r in C) / len(C), 3) if C else None,
           'rest_hit1': round(sum(r['hit1'] for r in R) / len(R), 3) if R else None,
           'rest_hit3': round(sum(r['hit3'] for r in R) / len(R), 3) if R else None}
    if len({r['doc'] for r in C}) >= 2:
        b = boot(C, lambda r: r['hit1']); out['clear_hit1_ci95'] = b['ci95']; out['_lower_raw'] = b['raw'][0]
    return out


def main():
    res = {}
    import stale.relocate2 as A, stale.relocate_b as B
    docs, need, chosen = A.needed(); K = json.load(open(os.path.join(OUT, 'reloc_kev.json'), encoding='utf-8'))
    da = [{**d, 'items': [it for it in d['items'] if it['point'] in chosen]} for d in docs]
    res['A_exploratory'] = summary(rows_for(da, K, lambda d: d['doc']))
    res['B_exploratory'] = summary(rows_for(B.docs(), json.load(open(B.F['kev'], encoding='utf-8')), lambda d: d['service']))
    pd = os.path.join(OUT, 'contrib_docs.json'); pk = os.path.join(OUT, 'contrib_kev.json')
    if os.path.exists(pd) and os.path.exists(pk):
        D = json.load(open(pd, encoding='utf-8'))['docs']; KD = json.load(open(pk, encoding='utf-8'))
        s = summary(rows_for(D, KD, lambda d: d['service']))
        ok = s['clear'] >= MIN_N and s['clear_hit1'] is not None and s['clear_hit1'] >= BAR and s.get('_lower_raw', -1) >= LOWER
        s['reading'] = 'LABEL ADOPTED' if ok else 'NO LABEL'
        res['D'] = s
    for k, v in res.items(): v.pop('_lower_raw', None); print(k, json.dumps(v))
    with open(os.path.join(OUT, 'contrib_margin.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
