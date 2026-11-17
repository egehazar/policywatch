"""GPT as the second rater of the contrib cards (stale/PLAN_missing_contrib.md: "GPT (Codex) rates the same cards as a
second rater: reported beside the first, never read"). Nothing here changes a reading.

ingest: GPT's two replies (stale/out/missing_contrib_gpt_raw/gpt_contrib_{a,b}.txt)
        -> stale/out/missing_contrib_gpt_raw/verdicts_gpt.json (kept out of the rater folders)
report: GPT's YES shares per arm and for the label's two groups, its random-control YES count and its PAGE - RERANK
        difference, beside the Claude raters', and card-level agreement -> stale/out/missing_contrib_gpt.json
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.suggest_eval import kappa
from stale import missing_contrib as X

RAW = os.path.join(OUT, 'missing_contrib_gpt_raw'); GV = os.path.join(RAW, 'verdicts_gpt.json')
RES = os.path.join(OUT, 'missing_contrib_gpt.json')


def ingest():
    K = X.load(X.KEY); A = {}
    for x in X.FOLDERS:
        raw = open(os.path.join(RAW, f'gpt_contrib_{x}.txt'), encoding='utf-8').read()
        A.update(json.loads(raw[raw.index('{'):raw.rindex('}') + 1]))
    missing = sorted(set(K) - set(A)); bad = sorted(c for c in K if c in A and A[c].get('verdict') not in X.VERD)
    assert not missing and not bad, f'missing {missing[:10]} ({len(missing)}), bad {bad[:10]} ({len(bad)})'
    out = {c: {'verdict': A[c]['verdict'], 'why': str(A[c].get('why', ''))} for c in sorted(K)}
    with open(GV, 'w', encoding='utf-8', newline='\n') as f: json.dump(out, f, indent=1, ensure_ascii=False)
    print({v: sum(x['verdict'] == v for x in out.values()) for v in X.VERD})


def side(K, V):
    high = lambda k: 'PAGE' in k['arms'] and X.shown(k['page_p']) >= X.HIGH
    rest = lambda k: 'PAGE' in k['arms'] and X.shown(k['page_p']) < X.HIGH
    return {'precision_at_10': {a: X.share(V, [c for c in K if a in K[c]['arms']]) for a in X.ARMS},
            'random_yes': sum(V[c]['verdict'] == 'YES' for c in K if 'RANDOM' in K[c]['arms']),
            'PAGE_minus_RERANK': X.boot(K, V, lambda k: 'PAGE' in k['arms'], lambda k: 'RERANK' in k['arms'], random.Random(X.SEED + 2)),
            'label': {'high': X.share(V, [c for c in K if high(K[c])]), 'rest': X.share(V, [c for c in K if rest(K[c])]),
                      'high_minus_rest': X.boot(K, V, high, rest, random.Random(X.SEED + 3))}}


def report(gv=None, res=None):
    K = X.load(X.KEY); G = X.load(gv or GV); C = {}
    for x in X.FOLDERS: C.update(X.load(os.path.join(X.FOLDERS[x], 'verdicts.json')))
    ids = sorted(K); g = [G[c]['verdict'] == 'YES' for c in ids]; cl = [C[c]['verdict'] == 'YES' for c in ids]
    out = {'gpt': side(K, G), 'claude': side(K, C), 'random_n': sum('RANDOM' in K[c]['arms'] for c in K),
           'agreement': {'cards': len(ids), 'agree_yes_vs_not': sum(x == y for x, y in zip(g, cl)),
                         'kappa_yes_vs_not': None if kappa(g, cl) is None else round(kappa(g, cl), 3), 'agree_three_way': sum(G[c]['verdict'] == C[c]['verdict'] for c in ids),
                         'gpt_yes': sum(g), 'claude_yes': sum(cl)}}
    with open(res or RES, 'w', encoding='utf-8') as f: json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    {'ingest': ingest, 'report': report}[sys.argv[1]]()
