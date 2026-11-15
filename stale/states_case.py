"""Which arm's top passage states the case? (stale/PREREG_states_case.md). Scores already on disk, no model call.

build   60 points (30 from part A, 30 from part B); one card per distinct (point, top passage of KEV / RERANK / BM25),
        plus 10 RANDOM controls -> stale/audit_states/cards.md; key -> stale/out/states_case_key.json
score   stale/audit_states/verdicts.json -> stale/out/states_case_result.json
Usage   py -m stale.states_case build | score
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.miss_audit import load
from stale.relocate import hit
from stale.relocate2 import boot, reading
AUD = os.path.join(HERE, 'audit_states'); KEY = os.path.join(OUT, 'states_case_key.json')
SEED = 20261118; N = 30; ARMS = ('KEV', 'RERANK', 'BM25')


def arm_scores(part):
    """(doc, question) -> scores, for RERANK and BM25."""
    if part == 'A':
        R = json.load(open(os.path.join(OUT, 'reloc_rerank.json'), encoding='utf-8'))
        B = json.load(open(os.path.join(OUT, 'reloc_base.json'), encoding='utf-8'))
        return {'RERANK': lambda d, q: R[d]['scores'][q], 'BM25': lambda d, q: B['BM25'][d][q]}
    B = json.load(open(os.path.join(OUT, 'heldout_base.json'), encoding='utf-8'))
    return {'RERANK': lambda d, q: B['RERANK'][d][q], 'BM25': lambda d, q: B['BM25'][d][q]}


def questions(part):
    f = {'A': 'reloc_docs.json', 'B': 'heldout_docs.json'}[part]
    return {it['point']: it['question'] for d in json.load(open(os.path.join(OUT, f), encoding='utf-8'))['docs'] for it in d['items']}


def top(sc): return max(range(len(sc)), key=lambda j: (sc[j], -j))


def build():
    rng = random.Random(SEED); pts = []
    for part in ('A', 'B'):
        X = load(part); S = arm_scores(part); Q = questions(part)
        for x in rng.sample(X, N):
            sc = {'KEV': x['scores'], **{a: S[a](x['doc'], Q[x['point']]) for a in ('RERANK', 'BM25')}}
            assert all(len(v) == len(x['pieces']) for v in sc.values())
            pts.append((x, {a: top(sc[a]) for a in ARMS}, sc))
    cards = {}
    for x, tops, sc in pts:
        for a, i in tops.items(): cards.setdefault((x['part'], x['point'], i), {'x': x, 'piece': i, 'arms': []})['arms'].append(a)
    made = 0
    for x, tops, sc in rng.sample(pts, len(pts)):          # 10 controls, from drawn points that have such a passage
        top5 = {j for a in ARMS for j in sorted(range(len(sc[a])), key=lambda j: -sc[a][j])[:5]}
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
        c = cards[k]; x = c['x']; cid = f'S{n:03d}'
        L += [f'## {cid}', f'**Case:** {x["case"]}', '', '**Passage:**', '', '```', x['pieces'][c['piece']].strip(), '```', '']
        key[cid] = {'part': x['part'], 'point': x['point'], 'doc': x['doc'], 'piece': c['piece'], 'arms': c['arms'],
                    'gold': c['piece'] in x['gold']}
    pts_key = [{'part': x['part'], 'point': x['point'], 'doc': x['doc'], 'tops': tops,
                'hit1': {a: hit(sc[a], x['gold'])[0][1] for a in ARMS}} for x, tops, sc in pts]
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({c: {'verdict': '', 'why': ''} for c in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump({'cards': key, 'points': pts_key}, f, indent=1)
    print(len(key), 'cards for', len(pts), 'points ->', AUD)


def score():
    K = json.load(open(KEY, encoding='utf-8')); V = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V) == set(K['cards']) and all(V[c]['verdict'] in ('YES', 'PARTLY', 'NO') for c in V)
    by = {(c['part'], c['point'], c['piece']): V[cid]['verdict'] for cid, c in K['cards'].items() if 'RANDOM' not in c['arms']}
    rows = []
    for p in K['points']:
        r = {'doc': p['doc'], 'point': p['point'], 'part': p['part']}
        for a in ARMS:
            v = by[(p['part'], p['point'], p['tops'][a])]
            r[a] = {'yes': int(v == 'YES'), 'yes_or_partly': int(v != 'NO'), 'hit1': p['hit1'][a]}
        rows.append(r)
    n = len(rows); rnd = [V[c]['verdict'] for c, k in K['cards'].items() if 'RANDOM' in k['arms']]
    res = {'points': n, 'random_yes': rnd.count('YES'), 'random_n': len(rnd),
           'states_at1': {a: round(sum(r[a]['yes'] for r in rows) / n, 3) for a in ARMS},
           'yes_or_partly_at1': {a: round(sum(r[a]['yes_or_partly'] for r in rows) / n, 3) for a in ARMS},
           'hit_at1_same_points': {a: round(sum(r[a]['hit1'] for r in rows) / n, 3) for a in ARMS}}
    valid = res['random_yes'] <= 2; res['valid'] = valid
    for b in ('RERANK', 'BM25'):
        d = boot(rows, lambda r: r['KEV']['yes'] - r[b]['yes']); res[f'KEV_minus_{b}'] = d
        res[f'reading_KEV_vs_{b}'] = reading(d['raw'], 'KEV better', 'KEV worse', 'no difference shown') if valid else 'not called (rater unreliable)'
    with open(os.path.join(OUT, 'states_case_result.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': rows}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'build': build, 'score': score}[sys.argv[1]]()
