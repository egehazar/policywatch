"""Blind human audit of the r20 test (GPT r1's decisive measurement; eval/PREREG_human_audit.md).

The sample uses only things fixed before any model output was read: the LLM-rater gold and the chunk-hash arm (bge).
It never looks at Kev or at the Qwen baseline, so neither arm is favoured by the choice of items.

Usage  py -m audit.human_audit sample <frozen_dir>          -> audit/sample.json (frozen, hashed)
       py -m audit.human_audit page   <frozen_dir> <pga>    -> audit/out/data.json (what the blind page shows)
       py -m audit.human_audit score  <frozen_dir> <verdicts.json>
"""
import json, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from policywatch import evaluate

SEED = 20261112; N_CH = 30; N_REST = 20
PARA = chr(10) * 2; SEP = PARA + '[...]' + PARA      # rq.py's block separator


def sample(frozen):
    pairs, arms, G, _ = evaluate.load(frozen)
    CH = set(arms['CH']); items = sorted(G)
    g1 = [i for i in items if G[i] == 1]; amb = [i for i in items if G[i] is None]
    g0ch = [i for i in items if G[i] == 0 and i in CH]; g0rest = [i for i in items if G[i] == 0 and i not in CH]
    rng = random.Random(SEED)
    s3a = sorted(rng.sample(g0ch, N_CH)); s3b = sorted(rng.sample(g0rest, N_REST))
    strata = {'S1_gold1': g1, 'S2_ambiguous': amb, 'S3a_gold0_in_CH': s3a, 'S3b_gold0_outside_CH': s3b}
    sizes = {'S1_gold1': len(g1), 'S2_ambiguous': len(amb), 'S3a_gold0_in_CH': len(g0ch), 'S3b_gold0_outside_CH': len(g0rest)}
    out = {'seed': SEED, 'population': len(items), 'stratum_sizes': sizes,
           'sampled': {k: len(v) for k, v in strata.items()}, 'strata': strata,
           'updates_touched': len({i.split('|')[0] for v in strata.values() for i in v})}
    with open(os.path.join(HERE, 'sample.json'), 'w', encoding='utf-8') as f: json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'strata'}, indent=1))


def _git(pga, *a):
    return subprocess.run(['git', '-C', pga, *a], capture_output=True, encoding='utf-8', errors='replace').stdout


def _clean(text):
    # the same normalization the raters' regions used: link targets dropped, whitespace collapsed, one paragraph per line
    from policywatch.diffing import paras
    return PARA.join(paras(text))


def page(frozen, pga):
    """Blind data for the review page: texts and question wording only. No gold, no stratum, no model output."""
    from policywatch.diffing import word_diff
    S = json.load(open(os.path.join(HERE, 'sample.json'), encoding='utf-8'))
    items = sorted(i for v in S['strata'].values() for i in v)
    pairs = {p['id']: p for p in (json.loads(l) for l in open(os.path.join(frozen, 'pairs.jsonl'), encoding='utf-8'))}
    bank = json.load(open(os.path.join(ROOT, 'data', 'bank_v1_r20.json'), encoding='utf-8'))
    by = {}
    for i in items: by.setdefault(i.split('|')[0], []).append(int(i.split('|')[1]))
    rng = random.Random(SEED + 1); order = sorted(by); rng.shuffle(order)
    remote = _git(pga, 'remote', 'get-url', 'origin').strip().removesuffix('.git')
    site = os.path.join(HERE, 'out', 'site'); os.makedirs(os.path.join(site, 'full'), exist_ok=True)
    ups = []
    for n, pid in enumerate(order, 1):
        p = pairs[pid]; qs = by[pid][:]; rng.shuffle(qs)
        blocks = [word_diff(o, nw) for o, nw in zip(p['old_region'].split(SEP), p['new_region'].split(SEP))]
        parent = _git(pga, 'rev-parse', p['commit'] + '^').strip()
        u = f'u{n:02d}'
        ups.append({'u': u, 'platform': p['platform'], 'doc': p['doc'][:-3], 'date': p['date'],
                    'blocks': blocks, 'commit_url': f"{remote}/commit/{p['commit']}",
                    'old_url': f"{remote}/blob/{parent}/{p['path'].replace(' ', '%20')}",
                    'new_url': f"{remote}/blob/{p['commit']}/{p['path'].replace(' ', '%20')}",
                    'questions': [{'id': f'{pid}-{k:02d}', 'text': bank[k]['title']} for k in qs]})
        full = {'old': _clean(_git(pga, 'show', f"{p['commit']}^:{p['path']}")), 'new': _clean(_git(pga, 'show', f"{p['commit']}:{p['path']}"))}
        with open(os.path.join(site, 'full', f'{u}.json'), 'w', encoding='utf-8') as f: json.dump(full, f, ensure_ascii=False)
    data = {'items': len(items), 'updates': ups, 'source': remote}
    with open(os.path.join(site, 'data.json'), 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False)
    print(len(ups), 'updates,', len(items), 'items ->', site)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'sample': sample(sys.argv[2])
    elif c == 'page': page(sys.argv[2], sys.argv[3])
