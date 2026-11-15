"""Exploratory (stale/PLAN_miss_audit.md): when Kev's top passage is not the curator's, does it state the case anyway?

build   40 MISS cards (Kev's best non-gold passage), 15 GOLD and 15 RANDOM control cards from parts A and B, shuffled,
        to stale/audit_misses/cards.md; the key to stale/out/miss_audit_key.json
score   stale/audit_misses/verdicts.json -> stale/out/miss_audit_result.json
Usage   py -m stale.miss_audit build | score
"""
import json, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
AUD = os.path.join(HERE, 'audit_misses'); KEY = os.path.join(OUT, 'miss_audit_key.json')
SEED = 20261117
PARTS = {'A': ('reloc_docs.json', 'reloc_kev.json', 'reloc2_result.json'),
         'B': ('heldout_docs.json', 'heldout_kev.json', 'heldout_result.json')}


def load(part):
    df, kf, rf = (os.path.join(OUT, f) for f in PARTS[part])
    D = json.load(open(df, encoding='utf-8'))['docs']; K = json.load(open(kf, encoding='utf-8'))
    hit1 = {r['point']: r['KEV']['hit']['1'] for r in json.load(open(rf, encoding='utf-8'))['rows']}
    out = []
    for d in D:
        for it in d['items']:
            if it.get('gold') is None or it['point'] not in hit1: continue
            sc = [s[it['question']] for s in K[d['doc']]['scores']]
            out.append({'part': part, 'point': it['point'], 'doc': d['doc'], 'case': it['case_title'], 'gold': sorted(it['gold']),
                        'hit1': hit1[it['point']], 'scores': sc, 'pieces': d['pieces']})
    return sorted(out, key=lambda x: x['point'])


def build():
    rng = random.Random(SEED); cards = []
    P = {p: load(p) for p in PARTS}
    for p in PARTS:
        for x in rng.sample([x for x in P[p] if x['hit1'] < 1], 20):
            i = max((j for j in range(len(x['scores'])) if j not in x['gold']), key=lambda j: x['scores'][j])
            cards.append(('MISS', x, i))
    hits = sorted([x for p in PARTS for x in P[p] if x['hit1'] == 1], key=lambda x: (x['part'], x['point']))
    for x in rng.sample(hits, 15):
        cards.append(('GOLD', x, x['gold'][0]))
        top5 = set(sorted(range(len(x['scores'])), key=lambda j: -x['scores'][j])[:5])
        pool = [j for j in range(len(x['pieces'])) if j not in x['gold'] and j not in top5]
        cards.append(('RANDOM', x, rng.choice(pool)))
    rng.shuffle(cards)
    os.makedirs(AUD, exist_ok=True)
    L = ['# 70 cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
    key = {}
    for n, (kind, x, i) in enumerate(cards, 1):
        cid = f'M{n:02d}'
        L += [f'## {cid}', f'**Case:** {x["case"]}', '', '**Passage:**', '', '```', x['pieces'][i].strip(), '```', '']
        key[cid] = {'kind': kind, 'part': x['part'], 'point': x['point'], 'doc': x['doc'], 'piece': i, 'hit1': x['hit1'],
                    'kev_score': round(x['scores'][i], 4)}
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({c: {'verdict': '', 'why': ''} for c in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump(key, f, indent=1)
    print(len(key), 'cards ->', AUD)


def score():
    K = json.load(open(KEY, encoding='utf-8')); V = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V) == set(K) and all(V[c]['verdict'] in ('YES', 'PARTLY', 'NO') for c in V)
    res = {}
    for kind in ('MISS', 'GOLD', 'RANDOM'):
        cs = [c for c in K if K[c]['kind'] == kind]; v = [V[c]['verdict'] for c in cs]
        res[kind] = {'n': len(cs), 'YES': v.count('YES'), 'PARTLY': v.count('PARTLY'), 'NO': v.count('NO'),
                     'yes_share': round(v.count('YES') / len(cs), 3), 'yes_or_partly': round((len(cs) - v.count('NO')) / len(cs), 3)}
    for part in PARTS:
        cs = [c for c in K if K[c]['kind'] == 'MISS' and K[c]['part'] == part]
        res['MISS_' + part] = {'n': len(cs), 'YES': sum(V[c]['verdict'] == 'YES' for c in cs)}
    ok = res['GOLD']['yes_share'] >= .8 and res['RANDOM']['yes_share'] <= .2
    res['rater_reliable'] = ok
    if ok:
        H = {'A': .620, 'B': .752}          # Kev's official hit@1, stale/RESULT_relocate2.md
        res['estimate_states_case_at1'] = {p: round(H[p] + (1 - H[p]) * res['MISS_' + p]['YES'] / res['MISS_' + p]['n'], 3) for p in PARTS}
    with open(os.path.join(OUT, 'miss_audit_result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'build': build, 'score': score}[sys.argv[1]]()
