"""The base family on the states-the-case measure (stale/PREREG_states_case_qwen.md). Scores already on disk.

build   QWEN's top passage for the 120 points; new cards only where not already rated, plus 30 ANCHOR re-ratings and 10
        RANDOM controls -> stale/audit_states3/; key -> stale/out/states_case3_key.json
score   -> stale/out/states_case_qwen.json
Usage   py -m stale.states_case_qwen build | score
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale import states_case as S, states_case_ext as E
from stale.miss_audit import load
from stale.relocate2 import boot, reading
AUD = os.path.join(HERE, 'audit_states3'); KEY = os.path.join(OUT, 'states_case3_key.json'); SEED = 20261120
QF = {'A': 'reloc_qwen.json', 'B': 'heldout_qwen.json'}


def earlier():
    """(part, point, piece) -> verdict, and the two keys, from the first test and the extension."""
    V = {}; keys = []
    for kf, af in ((S.KEY, S.AUD), (E.KEY, E.AUD)):
        K = json.load(open(kf, encoding='utf-8')); vv = json.load(open(os.path.join(af, 'verdicts.json'), encoding='utf-8')); keys.append(K)
        for cid, c in K['cards'].items():
            if 'RANDOM' not in c['arms']: V[(c['part'], c['point'], c['piece'])] = (vv[cid]['verdict'], cid)
    return V, keys


def qwen_tops(keys):
    Q = {p: json.load(open(os.path.join(OUT, f), encoding='utf-8')) for p, f in QF.items()}
    X = {(x['part'], x['point']): x for p in QF for x in load(p)}; qs = {p: S.questions(p) for p in QF}
    out = []
    for K in keys:
        for p in K['points']:
            x = X[(p['part'], p['point'])]
            sc = [s[qs[p['part']][p['point']]]['lo'] for s in Q[p['part']][p['doc']]['scores']]
            assert len(sc) == len(x['pieces'])
            out.append((p, x, S.top(sc), sc))
    return out


def build():
    rng = random.Random(SEED); V, keys = earlier(); T = qwen_tops(keys)
    cards = {}
    for p, x, t, sc in T:
        if (p['part'], p['point'], t) not in V: cards[(p['part'], p['point'], t, 'Q')] = {'x': x, 'piece': t, 'kind': 'QWEN'}
    X = {(x['part'], x['point']): x for p_, x, t, sc in T}
    for k in rng.sample(sorted(V), 30):
        cards[(k[0], k[1], k[2], 'A')] = {'x': X[(k[0], k[1])], 'piece': k[2], 'kind': 'ANCHOR', 'earlier': V[k][0]}
    made = 0
    for p, x, t, sc in rng.sample(T, len(T)):
        rated = set(p['tops'].values()) | {t}
        top5 = set(sorted(range(len(sc)), key=lambda j: -sc[j])[:5]) | rated
        pool = [j for j in range(len(x['pieces'])) if j not in top5 and j not in x['gold']]
        if not pool: continue
        i = rng.choice(pool); cards[(x['part'], x['point'], i, 'R')] = {'x': x, 'piece': i, 'kind': 'RANDOM'}; made += 1
        if made == 10: break
    order = sorted(cards, key=str); rng.shuffle(order)
    os.makedirs(AUD, exist_ok=True)
    L = [f'# {len(order)} cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
    key = {}
    for n, k in enumerate(order, 1):
        c = cards[k]; x = c['x']; cid = f'U{n:03d}'
        L += [f'## {cid}', f'**Case:** {x["case"]}', '', '**Passage:**', '', '```', x['pieces'][c['piece']].strip(), '```', '']
        key[cid] = {'part': x['part'], 'point': x['point'], 'doc': x['doc'], 'piece': c['piece'], 'kind': c['kind'],
                    'earlier': c.get('earlier')}
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({c: {'verdict': '', 'why': ''} for c in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f:
        json.dump({'cards': key, 'qwen_tops': [{'part': p['part'], 'point': p['point'], 'piece': t} for p, x, t, sc in T]}, f, indent=1)
    print(len(key), 'cards:', sum(c['kind'] == 'QWEN' for c in key.values()), 'new QWEN,',
          sum(c['kind'] == 'ANCHOR' for c in key.values()), 'anchors,', sum(c['kind'] == 'RANDOM' for c in key.values()), 'random ->', AUD)


def score():
    K = json.load(open(KEY, encoding='utf-8')); V3 = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V3) == set(K['cards']) and all(V3[c]['verdict'] in ('YES', 'PARTLY', 'NO') for c in V3)
    V, keys = earlier()
    anc = [(c['earlier'], V3[cid]['verdict']) for cid, c in K['cards'].items() if c['kind'] == 'ANCHOR']
    agree = sum((a == 'YES') == (b == 'YES') for a, b in anc)
    shift = round(sum(b == 'YES' for a, b in anc) / len(anc) - sum(a == 'YES' for a, b in anc) / len(anc), 3)
    rnd = [V3[cid]['verdict'] for cid, c in K['cards'].items() if c['kind'] == 'RANDOM']
    new = {(c['part'], c['point'], c['piece']): V3[cid]['verdict'] for cid, c in K['cards'].items() if c['kind'] == 'QWEN'}
    rows = E.rows_of(keys[0], json.load(open(os.path.join(S.AUD, 'verdicts.json'), encoding='utf-8'))) + \
           E.rows_of(keys[1], json.load(open(os.path.join(E.AUD, 'verdicts.json'), encoding='utf-8')))
    qt = {(q['part'], q['point']): q['piece'] for q in K['qwen_tops']}
    for r in rows:
        k = (r['part'], r['point'], qt[(r['part'], r['point'])]); v = new.get(k) or V[k][0]
        r['QWEN'] = {'yes': int(v == 'YES'), 'yes_or_partly': int(v != 'NO')}
    n = len(rows)
    res = {'points': n, 'anchors_agree': agree, 'anchors_n': len(anc), 'anchor_yes_shift': shift,
           'random_yes': rnd.count('YES'), 'random_n': len(rnd), 'new_qwen_cards': len(new),
           'states_at1': {a: round(sum(r[a]['yes'] for r in rows) / n, 3) for a in ('KEV', 'QWEN', 'RERANK', 'BM25')}}
    valid = agree >= 24 and abs(shift) <= .10 and rnd.count('YES') <= 2; res['valid'] = valid
    for a, b in (('KEV', 'QWEN'), ('QWEN', 'RERANK')):
        d = boot(rows, lambda r: r[a]['yes'] - r[b]['yes']); res[f'{a}_minus_{b}'] = d
        res[f'reading_{a}_vs_{b}'] = reading(d['raw'], f'{a} better', f'{b} better', 'no difference shown') if valid else 'not called (rater check failed)'
    with open(os.path.join(OUT, 'states_case_qwen.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': rows}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'build': build, 'score': score}[sys.argv[1]]()
