"""The states-the-case extension (stale/PREREG_states_case_ext.md): 60 new points, then the pooled 120-point reading.

build   as stale.states_case.build, seed 20261119, excluding the first test's 60 points -> stale/audit_states2/,
        key -> stale/out/states_case2_key.json
score   the extension alone and pooled with stale/out/states_case_result.json -> stale/out/states_case_pooled.json
Usage   py -m stale.states_case_ext build | score
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale import states_case as S
from stale.miss_audit import load
from stale.relocate import hit
from stale.relocate2 import boot, reading
AUD = os.path.join(HERE, 'audit_states2'); KEY = os.path.join(OUT, 'states_case2_key.json'); SEED = 20261119


def build():
    first = {(p['part'], p['point']) for p in json.load(open(S.KEY, encoding='utf-8'))['points']}
    rng = random.Random(SEED); pts = []
    for part in ('A', 'B'):
        X = [x for x in load(part) if (part, x['point']) not in first]; A = S.arm_scores(part); Q = S.questions(part)
        for x in rng.sample(X, S.N):
            sc = {'KEV': x['scores'], **{a: A[a](x['doc'], Q[x['point']]) for a in ('RERANK', 'BM25')}}
            assert all(len(v) == len(x['pieces']) for v in sc.values())
            pts.append((x, {a: S.top(sc[a]) for a in S.ARMS}, sc))
    cards = {}
    for x, tops, sc in pts:
        for a, i in tops.items(): cards.setdefault((x['part'], x['point'], i), {'x': x, 'piece': i, 'arms': []})['arms'].append(a)
    made = 0
    for x, tops, sc in rng.sample(pts, len(pts)):
        top5 = {j for a in S.ARMS for j in sorted(range(len(sc[a])), key=lambda j: -sc[a][j])[:5]}
        pool = [j for j in range(len(x['pieces'])) if j not in top5 and j not in x['gold']]
        if not pool: continue
        i = rng.choice(pool); cards[(x['part'], x['point'], i, 'R')] = {'x': x, 'piece': i, 'arms': ['RANDOM']}
        made += 1
        if made == 10: break
    order = sorted(cards, key=str); rng.shuffle(order)
    os.makedirs(AUD, exist_ok=True)
    L = [f'# {len(order)} cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
    key = {}
    for n, k in enumerate(order, 1):
        c = cards[k]; x = c['x']; cid = f'T{n:03d}'
        L += [f'## {cid}', f'**Case:** {x["case"]}', '', '**Passage:**', '', '```', x['pieces'][c['piece']].strip(), '```', '']
        key[cid] = {'part': x['part'], 'point': x['point'], 'doc': x['doc'], 'piece': c['piece'], 'arms': c['arms'],
                    'gold': c['piece'] in x['gold']}
    pts_key = [{'part': x['part'], 'point': x['point'], 'doc': x['doc'], 'tops': tops,
                'hit1': {a: hit(sc[a], x['gold'])[0][1] for a in S.ARMS}} for x, tops, sc in pts]
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({c: {'verdict': '', 'why': ''} for c in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump({'cards': key, 'points': pts_key}, f, indent=1)
    print(len(key), 'cards for', len(pts), 'points ->', AUD)


def rows_of(K, V):
    by = {(c['part'], c['point'], c['piece']): V[cid]['verdict'] for cid, c in K['cards'].items() if 'RANDOM' not in c['arms']}
    rows = []
    for p in K['points']:
        r = {'doc': p['doc'], 'point': p['point'], 'part': p['part']}
        for a in S.ARMS:
            v = by[(p['part'], p['point'], p['tops'][a])]
            r[a] = {'yes': int(v == 'YES'), 'yes_or_partly': int(v != 'NO'), 'hit1': p['hit1'][a]}
        rows.append(r)
    return rows


def summary(rows):
    n = len(rows); res = {'points': n, 'states_at1': {a: round(sum(r[a]['yes'] for r in rows) / n, 3) for a in S.ARMS},
                          'yes_or_partly_at1': {a: round(sum(r[a]['yes_or_partly'] for r in rows) / n, 3) for a in S.ARMS},
                          'hit_at1': {a: round(sum(r[a]['hit1'] for r in rows) / n, 3) for a in S.ARMS}}
    for b in ('RERANK', 'BM25'): res[f'KEV_minus_{b}'] = boot(rows, lambda r: r['KEV']['yes'] - r[b]['yes'])
    return res


def score():
    K = json.load(open(KEY, encoding='utf-8')); V = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V) == set(K['cards']) and all(V[c]['verdict'] in ('YES', 'PARTLY', 'NO') for c in V)
    rnd = [V[c]['verdict'] for c, k in K['cards'].items() if 'RANDOM' in k['arms']]
    ext = rows_of(K, V); first = json.load(open(os.path.join(OUT, 'states_case_result.json'), encoding='utf-8'))['rows']
    res = {'extension': {**summary(ext), 'random_yes': rnd.count('YES'), 'random_n': len(rnd)}}
    valid = rnd.count('YES') <= 2; res['extension_valid'] = valid
    if valid:
        res['pooled'] = summary(first + ext)
        for b in ('RERANK', 'BM25'):
            pr = res['pooled'][f'KEV_minus_{b}']['raw']; e = res['extension'][f'KEV_minus_{b}']['point']
            call = reading(pr, 'KEV better', 'KEV worse', 'no difference shown')
            if call != 'no difference shown' and (e > 0) != (call == 'KEV better'): call = 'no difference shown (the extension points the other way)'
            res[f'final_KEV_vs_{b}'] = call
    else:
        res['final'] = 'extension unreliable: the first test stands, nothing pooled'
    with open(os.path.join(OUT, 'states_case_pooled.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': ext}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'build': build, 'score': score}[sys.argv[1]]()
