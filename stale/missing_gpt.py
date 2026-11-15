"""GPT as the second rater of the missing points pilot's cards (stale/PREREG_missing.md, measure 3: "GPT (Codex) rates
the same cards as a second rater if its usage allows (reported, not read)"). Nothing here changes a reading.

ingest <raw reply>: GPT's reply for stale/audit_missing/cards.md -> stale/audit_missing/verdicts_gpt.json
report: GPT's precision@10 per arm and its random-control YES count, beside the Claude rater's, and card-level
  agreement (YES vs not YES, kappa) -> stale/out/missing_gpt.json

Usage  py -m stale.missing_gpt ingest <file>  |  py -m stale.missing_gpt report
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import KEY, AUD, ARMS, wilson
from stale.suggest_eval import kappa

VERD = ('YES', 'PARTLY', 'NO')


def ingest(path):
    K = json.load(open(KEY, encoding='utf-8')); raw = open(path, encoding='utf-8').read()
    A = json.loads(raw[raw.index('{'):raw.rindex('}') + 1])
    missing = sorted(set(K) - set(A)); bad = sorted(c for c in K if c in A and A[c].get('verdict') not in VERD)
    assert not missing and not bad, f'missing {missing[:10]} ({len(missing)}), bad {bad[:10]} ({len(bad)})'
    out = {c: {'verdict': A[c]['verdict'], 'why': str(A[c].get('why', ''))} for c in sorted(K)}
    with open(os.path.join(AUD, 'verdicts_gpt.json'), 'w', encoding='utf-8', newline='\n') as f: json.dump(out, f, indent=1, ensure_ascii=False)
    print({v: sum(1 for x in out.values() if x['verdict'] == v) for v in VERD})


def prec(K, V):
    r = {}
    for a in ARMS:
        cs = [c for c in K if a in K[c]['arms']]; y = sum(V[c]['verdict'] == 'YES' for c in cs)
        r[a] = {'cards': len(cs), 'yes': y, 'yes_share': round(y / len(cs), 3), 'wilson95': wilson(y, len(cs)),
                'yes_or_partly_share': round(sum(V[c]['verdict'] != 'NO' for c in cs) / len(cs), 3)}
    return r


def report(key=None, aud=None, out=None):
    K = json.load(open(key or KEY, encoding='utf-8')); aud = aud or AUD
    G = json.load(open(os.path.join(aud, 'verdicts_gpt.json'), encoding='utf-8'))
    C = json.load(open(os.path.join(aud, 'verdicts.json'), encoding='utf-8'))
    rnd = [c for c in K if 'RANDOM' in K[c]['arms']]
    g = [G[c]['verdict'] == 'YES' for c in sorted(K)]; cl = [C[c]['verdict'] == 'YES' for c in sorted(K)]
    res = {'gpt': {'precision_at_10': prec(K, G), 'random_yes': sum(G[c]['verdict'] == 'YES' for c in rnd)},
           'claude': {'precision_at_10': prec(K, C), 'random_yes': sum(C[c]['verdict'] == 'YES' for c in rnd)},
           'random_n': len(rnd),
           'agreement': {'cards': len(g), 'agree': sum(x == y for x, y in zip(g, cl)), 'kappa': round(kappa(g, cl), 3),
                         'gpt_yes': sum(g), 'claude_yes': sum(cl),
                         'both_yes_by_arm': {a: sum(G[c]['verdict'] == 'YES' and C[c]['verdict'] == 'YES'
                                                    for c in K if a in K[c]['arms']) for a in ARMS}}}
    with open(os.path.join(out or OUT, 'missing_gpt.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'ingest': ingest(sys.argv[2])
    elif sys.argv[1] == 'report': report()
