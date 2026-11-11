"""Score the blind human audit (eval/PREREG_human_audit.md). Written before any human answer or Kev evaluation.

Usage  py -m audit.score <frozen_dir> <verdicts>
  <verdicts>: a directory of ArtifactData JSON files (one per item, from the page's "verdicts" collection) or a JSON
  file {item_id: {"v": ..., "note": ...}} (the page's backup text). Item ids look like p07-00 (pair p07, question 0).
"""
import glob, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from policywatch import evaluate

BENCH = os.path.join(ROOT, 'bench', 'out'); SEED = 20261111; KS = (25, 50, 100, 182)
VALID = ('changed', 'passage', 'none', 'unsure')


def read_jsonl(path):
    if not os.path.exists(path): return []
    with open(path, encoding='utf-8') as f: return [json.loads(l) for l in f if l.strip()]


def load_verdicts(src):
    if os.path.isdir(src):
        raw = {}
        for fn in glob.glob(os.path.join(src, '**', '*.json'), recursive=True):
            with open(fn, encoding='utf-8') as f: d = json.load(f)
            if isinstance(d, dict) and isinstance(d.get('data'), dict): d = d['data']
            raw[os.path.splitext(os.path.basename(fn))[0]] = d
    else:
        with open(src, encoding='utf-8') as f: raw = json.load(f)
    V = {}
    for k, d in raw.items():
        if not isinstance(d, dict) or d.get('v') not in VALID or '-' not in k: continue
        pid, q = k.rsplit('-', 1)
        if not q.isdigit(): continue
        V[f'{pid}|{int(q)}'] = {'v': d['v'], 'note': str(d.get('note') or '')}
    return V


def orders(frozen):
    """Every arm's ranking of the 2,450 items, built exactly as bench/kev_vs_llm.py eval_cmd (KEV, LLM-DIFF, LLM-QA,
    same seeds and the same order of random draws) and rq.py evaluate (KEV+RULE); BGE by max cosine."""
    pairs, arms, G, kev = evaluate.load(frozen)
    items = [f"{p['id']}|{k}" for p in pairs for k in range(70)]
    d = {i: abs(kev[i.split('|')[0] + '|new'][f"q{int(i.split('|')[1]):02d}"] - kev[i.split('|')[0] + '|old'][f"q{int(i.split('|')[1]):02d}"]) for i in items}
    rng = random.Random(SEED)

    def tail(head):
        rest = [i for i in items if i not in set(head)]; rng.shuffle(rest); return head + rest

    O = {'KEV': sorted(items, key=lambda i: (-d[i], i))}
    ruled = sorted(set(arms['RULE']), key=lambda i: (-d[i], i))
    O['KEV+RULE'] = ruled + sorted([i for i in items if i not in set(ruled)], key=lambda i: (-d[i], i))
    O['BGE'] = sorted(items, key=lambda i: (-arms['BGE'][i], i))
    D = {r['id']: r for r in read_jsonl(os.path.join(BENCH, 'llm_diff.jsonl'))}
    Qa = {r['id']: r for r in read_jsonl(os.path.join(BENCH, 'llm_qa.jsonl'))}
    if len(D) == len(pairs):
        per = {p['id']: [f"{p['id']}|{k}" for k in ((D.get(p['id']) or {}).get('parsed') or [])] for p in pairs}
        inter = [lst[j] for j in range(max([len(l) for l in per.values()] + [0])) for lst in per.values() if j < len(lst)]
        O['LLM-DIFF'] = tail(inter)
    if len(D) == len(pairs) and len(Qa) == 2 * len(pairs):     # the bench draws LLM-QA's tail second from the same rng
        flips = []
        for p in pairs:
            o, n = Qa.get(p['id'] + '|old'), Qa.get(p['id'] + '|new')
            if o and n and o['parsed'] is not None and n['parsed'] is not None:
                flips += [f"{p['id']}|{k}" for k in range(70) if (k in o['parsed']) != (k in n['parsed'])]
        rng2 = random.Random(SEED); rng2.shuffle(flips); O['LLM-QA'] = tail(flips)
    within = {}
    for p in pairs:
        own = sorted([f"{p['id']}|{k}" for k in range(70)], key=lambda i: (-d[i], i))
        for r, i in enumerate(own, 1): within[i] = r
    return pairs, arms, G, O, within


def reading(r, O):
    if r['positives'] < 10: return 'UNDERPOWERED (fewer than 10 human-confirmed changes)'
    if 'LLM-DIFF' not in O: return 'INCOMPLETE (no LLM-DIFF run)'
    p = os.path.join(BENCH, 'result.json')
    if not os.path.exists(p): return 'INCOMPLETE (no bench result)'
    with open(p, encoding='utf-8') as f: c = json.load(f).get('sec_per_update', {})
    if c.get('KEV') is None or c.get('LLM-DIFF') is None: return 'INCOMPLETE (no timing)'
    k, l = r['within_k']['KEV'][182], r['within_k']['LLM-DIFF'][182]
    if (k >= l and c['KEV'] <= c['LLM-DIFF']) or (k >= l + 3 and c['KEV'] <= 2 * c['LLM-DIFF']): return 'DECISION MODEL WINS'
    if l >= k + 3 and c['LLM-DIFF'] <= 2 * c['KEV']: return 'LLM WINS'
    return 'NO CLEAR WINNER'


def score(frozen, src):
    with open(os.path.join(HERE, 'sample.json'), encoding='utf-8') as f: S = json.load(f)
    stratum = {i: s for s, v in S['strata'].items() for i in v}
    V = load_verdicts(src)
    pairs, arms, G, O, within = orders(frozen)
    CH = set(arms['CH']); rank = {a: {i: n for n, i in enumerate(o, 1)} for a, o in O.items()}
    res = {'answered': sum(1 for i in V if i in stratum), 'of': len(stratum),
           'not_in_sample_ignored': sum(1 for i in V if i not in stratum),
           'cant_tell': sum(1 for i in V if i in stratum and V[i]['v'] == 'unsure'), 'arms_available': sorted(O)}
    w = {s: S['stratum_sizes'][s] / S['sampled'][s] for s in ('S3a_gold0_in_CH', 'S3b_gold0_outside_CH')}
    for name, keep in (('H_doc', ('changed',)), ('H_pass', ('changed', 'passage'))):
        H = {i: int(V[i]['v'] in keep) for i in V if i in stratum and V[i]['v'] != 'unsure'}
        pos = sorted(i for i, h in H.items() if h)
        r = {'positives': len(pos), 'judged': len(H)}
        r['by_stratum'] = {s: {'judged': sum(1 for i in H if stratum[i] == s), 'human_yes': sum(1 for i in pos if stratum[i] == s)}
                           for s in S['strata']}
        r['within_k'] = {a: {k: sum(1 for i in pos if rank[a][i] <= k) for k in KS} for a in O}
        r['in_CH'] = sum(1 for i in pos if i in CH)
        r['kev_outside_update_top5'] = sum(1 for i in pos if within[i] > 5)
        r['kev_outside_global_182'] = sum(1 for i in pos if rank['KEV'][i] > 182)
        r['ipw_estimate_rater_missed_changes'] = round(sum(w[stratum[i]] for i in pos if stratum[i] in w), 1)
        r['reading'] = reading(r, O)
        r['items'] = [{'item': i, 'stratum': stratum[i], **{a: rank[a][i] for a in O}, 'kev_in_update': within[i],
                       'note': V[i]['note']} for i in pos]
        res[name] = r
    res['notes'] = {i: V[i]['note'] for i in V if V[i]['note']}
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    with open(os.path.join(HERE, 'out', 'result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    return res


if __name__ == '__main__':
    out = score(sys.argv[1], sys.argv[2])
    print(json.dumps({k: v for k, v in out.items() if k != 'notes'}, indent=1))
