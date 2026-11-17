"""GPT as the second rater of the page-rating cards (stale/PLAN_wide_rate.md: "GPT (Codex) may rate the same cards as a
second rater if its usage allows: reported beside the first, never read"). Nothing here changes a reading.

ingest: GPT's two replies (stale/out/wide_rate_gpt_raw/gpt_wide_{a,b}.txt) -> stale/out/wide_rate_gpt_raw/verdicts_gpt.json
        (kept out of the rater folders, so the Claude raters never see it)
report: GPT's YES shares per arm, its random-control YES count and its PAGE - RERANK difference, beside the Claude
        raters', and card-level agreement (YES against not YES, kappa) -> stale/out/wide_rate_gpt.json
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.suggest_eval import kappa
from stale.wide_rate import KEY, FOLDERS, ARMS, VERD, SEED, share, diff

RAW = os.path.join(OUT, 'wide_rate_gpt_raw'); GV = os.path.join(RAW, 'verdicts_gpt.json')


def ingest():
    K = json.load(open(KEY, encoding='utf-8')); A = {}
    for x in FOLDERS:
        raw = open(os.path.join(RAW, f'gpt_wide_{x}.txt'), encoding='utf-8').read()
        A.update(json.loads(raw[raw.index('{'):raw.rindex('}') + 1]))
    missing = sorted(set(K) - set(A)); bad = sorted(c for c in K if c in A and A[c].get('verdict') not in VERD)
    assert not missing and not bad, f'missing {missing[:10]} ({len(missing)}), bad {bad[:10]} ({len(bad)})'
    out = {c: {'verdict': A[c]['verdict'], 'why': str(A[c].get('why', ''))} for c in sorted(K)}
    with open(GV, 'w', encoding='utf-8', newline='\n') as f: json.dump(out, f, indent=1, ensure_ascii=False)
    print({v: sum(x['verdict'] == v for x in out.values()) for v in VERD})


def report():
    K = json.load(open(KEY, encoding='utf-8')); G = json.load(open(GV, encoding='utf-8')); C = {}
    for x in FOLDERS: C.update(json.load(open(os.path.join(FOLDERS[x], 'verdicts.json'), encoding='utf-8')))
    rnd = [c for c in K if 'RANDOM' in K[c]['arms']]; ids = sorted(K)
    g = [G[c]['verdict'] == 'YES' for c in ids]; cl = [C[c]['verdict'] == 'YES' for c in ids]
    side = lambda V, s: {'precision_at_10': {a: share(K, V, [c for c in K if a in K[c]['arms']]) for a in ARMS},
                         'random_yes': sum(V[c]['verdict'] == 'YES' for c in rnd),
                         'PAGE_minus_RERANK': diff(K, V, 'PAGE', 'RERANK', random.Random(s))}
    res = {'gpt': side(G, SEED + 1), 'claude': side(C, SEED + 1), 'random_n': len(rnd),
           'agreement': {'cards': len(ids), 'agree_yes_vs_not': sum(x == y for x, y in zip(g, cl)),
                         'kappa_yes_vs_not': round(kappa(g, cl), 3), 'agree_three_way': sum(G[c]['verdict'] == C[c]['verdict'] for c in ids),
                         'gpt_yes': sum(g), 'claude_yes': sum(cl),
                         'both_yes_by_arm': {a: sum(G[c]['verdict'] == 'YES' and C[c]['verdict'] == 'YES'
                                                    for c in K if a in K[c]['arms']) for a in ARMS}}}
    with open(os.path.join(OUT, 'wide_rate_gpt.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'ingest': ingest, 'report': report}[sys.argv[1]]()
