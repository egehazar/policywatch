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


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'sample': sample(sys.argv[2])
