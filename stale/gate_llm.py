"""The 60 gate cards answered by GPT and Fable instead of a person (stale/PREREG_gate_llm.md).

ingest <rater> <raw file>: pulls the JSON object out of a rater's raw reply, checks it holds all 60 card ids with
  v in yes/no/unsure, and writes stale/out/fullread/gate_answers_<rater>.json ({id: {"v", "why"}}).
score: kappa of each rater vs the grader (Opus) on its yes/no cards, GPT vs Fable, yes counts per stratum, unsure
  counts -> stale/out/fullread/gate_llm.json, and the reading fixed in the plan.

Usage  py -m stale.gate_llm ingest gpt <file>  |  py -m stale.gate_llm ingest fable <file>  |  py -m stale.gate_llm score
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FDIR = os.path.join(HERE, 'out', 'fullread')
sys.path.insert(0, os.path.dirname(HERE))
from stale.suggest_eval import kappa

RATERS = ('gpt', 'fable')
STRATA = ('cited', 'uncited', 'none')


def parse(raw):
    a, b = raw.index('{'), raw.rindex('}')
    return json.loads(raw[a:b + 1])


def ingest(rater, path):
    gk = json.load(open(os.path.join(FDIR, 'gate_key.json'), encoding='utf-8'))
    A = parse(open(path, encoding='utf-8').read())
    missing = sorted(set(gk) - set(A)); extra = sorted(set(A) - set(gk))
    bad = sorted(i for i in A if i in gk and (A[i].get('v') if isinstance(A[i], dict) else None) not in ('yes', 'no', 'unsure'))
    assert not (missing or extra or bad), f'missing {missing} extra {extra} bad {bad}'
    out = {i: {'v': A[i]['v'], 'why': str(A[i].get('why', ''))} for i in sorted(gk)}
    with open(os.path.join(FDIR, f'gate_answers_{rater}.json'), 'w', encoding='utf-8') as f: json.dump(out, f, indent=1, ensure_ascii=False)
    print(rater, {v: sum(1 for x in out.values() if x['v'] == v) for v in ('yes', 'no', 'unsure')})


def pair_kappa(x, y, ids):
    pairs = [(x[i], y[i]) for i in ids if x.get(i) in (True, False) and y.get(i) in (True, False)]
    k = kappa([a for a, _ in pairs], [b for _, b in pairs])
    return {'n': len(pairs), 'agree': sum(a == b for a, b in pairs), 'kappa': round(k, 3) if k is not None else None}


def reading(ks):
    if any(k is None for k in ks): return 'NOT COMPUTABLE'
    if min(ks) < .4: return 'OTHER AI RATERS DO NOT BACK THE GRADER (below .4): withdraw the 74% figure from summaries'
    if min(ks) < .6: return 'OTHER AI RATERS DO NOT BACK THE GRADER: mark the 74% figure doubtful'
    return 'TWO OTHER AI RATERS AGREE WITH THE GRADER (still provisional: not a human check)'


def score():
    gk = json.load(open(os.path.join(FDIR, 'gate_key.json'), encoding='utf-8'))
    ids = sorted(gk)
    yn = lambda v: True if v == 'yes' else False if v == 'no' else None
    L = {'opus': {i: gk[i]['opus_yes'] for i in ids}}
    raw = {}
    for r in RATERS:
        raw[r] = json.load(open(os.path.join(FDIR, f'gate_answers_{r}.json'), encoding='utf-8'))
        L[r] = {i: yn(raw[r][i]['v']) for i in ids}
    res = {'items': len(ids),
           'vs_grader': {r: pair_kappa(L[r], L['opus'], ids) for r in RATERS},
           'gpt_vs_fable': pair_kappa(L['gpt'], L['fable'], ids),
           'unsure': {r: sum(1 for i in ids if L[r][i] is None) for r in RATERS},
           'by_stratum': {s: {'n': sum(1 for i in ids if gk[i]['stratum'] == s),
                              **{f'{r}_yes': sum(1 for i in ids if gk[i]['stratum'] == s and L[r][i] is True) for r in ('opus',) + RATERS}}
                          for s in STRATA}}
    res['reading'] = reading([res['vs_grader'][r]['kappa'] for r in RATERS])
    res['disagreements'] = [{'id': i, 'stratum': gk[i]['stratum'], 'opus': 'yes' if L['opus'][i] else 'no',
                             **{r: raw[r][i]['v'] for r in RATERS}, **{f'{r}_why': raw[r][i]['why'] for r in RATERS}}
                            for i in ids if any(L[r][i] is not None and L[r][i] != L['opus'][i] for r in RATERS)]
    with open(os.path.join(FDIR, 'gate_llm.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != 'disagreements'}, indent=1))
    print('disagreements with the grader:', len(res['disagreements']))


if __name__ == '__main__':
    if sys.argv[1] == 'ingest': ingest(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'score': score()
