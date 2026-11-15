"""'Does the top passage state the case?' re-rated by GPT (stale/PREREG_states_case_gpt.md). Exploratory.

ingest <folder> <raw reply>: GPT's reply for stale/<folder>/cards.md -> stale/<folder>/verdicts_gpt.json (all cards,
  verdict YES / PARTLY / NO).
score: the 120-point readings of stale/RESULT_states_case.md (first test + extension + base family) with GPT's
  verdicts in place of the Claude raters' -> stale/out/states_case_gpt.json.

Usage  py -m stale.states_case_gpt ingest audit_states <file>  |  py -m stale.states_case_gpt score
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale import states_case as S, states_case_ext as E, states_case_qwen as Q
from stale.relocate2 import boot, reading
from stale.suggest_eval import kappa

KEYS = {'audit_states': S.KEY, 'audit_states2': E.KEY, 'audit_states3': Q.KEY}
VERD = ('YES', 'PARTLY', 'NO')


def parse(raw):
    a, b = raw.index('{'), raw.rindex('}')
    return json.loads(raw[a:b + 1])


def ingest(folder, path):
    K = json.load(open(KEYS[folder], encoding='utf-8'))
    A = parse(open(path, encoding='utf-8').read())
    missing = sorted(set(K['cards']) - set(A)); bad = sorted(c for c in K['cards'] if c in A and A[c].get('verdict') not in VERD)
    assert not missing and not bad, f'missing {missing[:10]} ({len(missing)}), bad {bad[:10]} ({len(bad)})'
    out = {c: {'verdict': A[c]['verdict'], 'why': str(A[c].get('why', ''))} for c in sorted(K['cards'])}
    with open(os.path.join(HERE, folder, 'verdicts_gpt.json'), 'w', encoding='utf-8', newline='\n') as f: json.dump(out, f, indent=1, ensure_ascii=False)
    print(folder, {v: sum(1 for x in out.values() if x['verdict'] == v) for v in VERD})


def load(folder, who):
    return json.load(open(os.path.join(HERE, folder, 'verdicts_gpt.json' if who == 'gpt' else 'verdicts.json'), encoding='utf-8'))


def score():
    K = {f: json.load(open(k, encoding='utf-8')) for f, k in KEYS.items()}
    G = {f: load(f, 'gpt') for f in KEYS}; C = {f: load(f, 'claude') for f in KEYS}
    k1, k2, k3 = K['audit_states'], K['audit_states2'], K['audit_states3']
    rows = E.rows_of(k1, G['audit_states']) + E.rows_of(k2, G['audit_states2'])
    earlier = {}
    for f, KK in (('audit_states', k1), ('audit_states2', k2)):
        for cid, c in KK['cards'].items():
            if 'RANDOM' not in c['arms']: earlier[(c['part'], str(c['point']), str(c['piece']))] = G[f][cid]['verdict']
    norm = lambda c: (c['part'], str(c['point']), str(c['piece']))
    new = {norm(c): G['audit_states3'][cid]['verdict'] for cid, c in k3['cards'].items() if c['kind'] == 'QWEN'}
    qt = {(q['part'], str(q['point'])): str(q['piece']) for q in k3['qwen_tops']}
    for r in rows:
        kk = (r['part'], str(r['point']), qt[(r['part'], str(r['point']))]); v = new.get(kk) or earlier[kk]
        r['QWEN'] = {'yes': int(v == 'YES'), 'yes_or_partly': int(v != 'NO')}
    arms = ('KEV', 'QWEN', 'RERANK', 'BM25'); n = len(rows)
    rnd = [G['audit_states'][c]['verdict'] for c, x in k1['cards'].items() if 'RANDOM' in x['arms']] + \
          [G['audit_states2'][c]['verdict'] for c, x in k2['cards'].items() if 'RANDOM' in x['arms']] + \
          [G['audit_states3'][c]['verdict'] for c, x in k3['cards'].items() if x['kind'] == 'RANDOM']
    anc = [(earlier[norm(x)], G['audit_states3'][c]['verdict']) for c, x in k3['cards'].items() if x['kind'] == 'ANCHOR']
    a_all, b_all = [], []
    for f in KEYS:
        for c in sorted(K[f]['cards']): a_all.append(G[f][c]['verdict'] == 'YES'); b_all.append(C[f][c]['verdict'] == 'YES')
    res = {'points': n, 'states_at1': {a: round(sum(r[a]['yes'] for r in rows) / n, 3) for a in arms},
           'yes_or_partly_at1': {a: round(sum(r[a]['yes_or_partly'] for r in rows) / n, 3) for a in arms},
           'random_yes': rnd.count('YES'), 'random_n': len(rnd),
           'anchor_self_agree': sum((a == 'YES') == (b == 'YES') for a, b in anc), 'anchors_n': len(anc),
           'cards_vs_claude': {'cards': len(a_all), 'agree': sum(x == y for x, y in zip(a_all, b_all)),
                               'kappa': round(kappa(a_all, b_all), 3), 'gpt_yes': sum(a_all), 'claude_yes': sum(b_all)}}
    valid = rnd.count('YES') <= 3; res['valid'] = valid
    calls = {}
    for a, b in (('KEV', 'RERANK'), ('KEV', 'BM25'), ('KEV', 'QWEN'), ('QWEN', 'RERANK')):
        d = boot(rows, lambda r: r[a]['yes'] - r[b]['yes']); res[f'{a}_minus_{b}'] = {'point': d['point'], 'ci95': d['ci95']}
        calls[(a, b)] = reading(d['raw'], f'{a} better', f'{b} better', 'no difference shown')
        res[f'call_{a}_vs_{b}'] = calls[(a, b)] if valid else 'not called'
    if not valid: res['reading'] = 'NOT VALID (more than 3 random controls rated YES)'
    elif calls[('KEV', 'BM25')] != 'KEV better': res['reading'] = 'DOES NOT HOLD'
    elif calls[('KEV', 'RERANK')] == 'KEV better' and calls[('KEV', 'QWEN')] == 'no difference shown': res['reading'] = 'HOLDS UNDER GPT'
    else: res['reading'] = 'PARTLY HOLDS'
    with open(os.path.join(OUT, 'states_case_gpt.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': rows}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'ingest': ingest(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'score': score()
