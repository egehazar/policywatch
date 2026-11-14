"""Exploratory, not pre-registered: the relocation arms on points their models cannot have memorised.

Kev-4B is a LoRA adapter and a head on a frozen Qwen3.5-4B-Base; its own training data has no ToS;DR text (model card,
huggingface.co/jaredpalmer/kev-4b, checked 2026-11-14). So the only way Kev could know which passage a ToS;DR curator
quoted for a case is the base model's pretraining. Qwen/Qwen3.5-4B-Base was first published on the Hub on 2026-02-27
(createdAt) and last modified on 2026-04-23 (lastModified). A point created on ToS;DR after either date did not
exist when the base model's pretraining data was collected.

For both parts of the relocation follow-up this reads the official per-point rows (stale/out/reloc2_result.json and
heldout_result.json), splits them by the point's creation date and gives hit@1 per arm and the paired KEV - other
intervals (the same cluster bootstrap: documents in part A, services in part B).
Usage  py -m stale.reloc_fresh [result.json for A] [result.json for B]   -> stale/out/reloc_fresh.json
"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.dirname(HERE))
from stale.relocate2 import boot

CUTS = {'before 2025-07-01': ('', '2025-07-01'), 'from 2025-07-01': ('2025-07-01', '9'),
        'after the base model was published (from 2026-02-28)': ('2026-02-28', '9'),
        'after its last modification (from 2026-04-24)': ('2026-04-24', '9')}


def created():
    c = {}
    for f in glob.glob(os.path.join(HERE, 'data', '*.json')):
        S = json.load(open(f, encoding='utf-8'))
        for p in S.get('points', []) if isinstance(S, dict) else []: c[p['id']] = (p.get('created_at') or '')[:10]
    for f in glob.glob(os.path.join(HERE, 'data', 'heldout', '*.json')):
        for p in json.load(open(f, encoding='utf-8'))['points']: c[p['point']] = (p.get('created_at') or '')[:10]
    return c


def part(path, C):
    R = json.load(open(path, encoding='utf-8')); rows = R['rows']
    arms = [a for a in rows[0] if isinstance(rows[0][a], dict) and 'hit' in rows[0][a]]
    miss = [r['point'] for r in rows if not C.get(r['point'])]
    assert not miss, f'no creation date for {miss[:5]}'
    out = {}
    for name, (lo, hi) in CUTS.items():
        S = [r for r in rows if lo <= C[r['point']] < hi]
        if not S: out[name] = {'n': 0}; continue
        h1 = lambda r, a: r[a]['hit']['1'] if '1' in r[a]['hit'] else r[a]['hit'][1]
        o = {'n': len(S), 'clusters': len({r['doc'] for r in S}),
             'hit_at_1': {a: round(sum(h1(r, a) for r in S) / len(S), 3) for a in arms}}
        if o['clusters'] >= 5:
            o['KEV_minus'] = {b: {k: v for k, v in boot(S, lambda r, b=b: h1(r, 'KEV') - h1(r, b)).items() if k != 'raw'}
                              for b in arms if b != 'KEV' and not b.startswith(('CASCADE', 'RANDOM'))}
        out[name] = o
    return out


def main(a=os.path.join(OUT, 'reloc2_result.json'), b=os.path.join(OUT, 'heldout_result.json')):
    C = created(); res = {}
    for nm, p in (('A', a), ('B', b)):
        if os.path.exists(p): res[nm] = part(p, C)
    with open(os.path.join(OUT, 'reloc_fresh.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    for nm, P in res.items():
        print(f'== part {nm}')
        for cut, o in P.items():
            if not o['n']: print(f'  {cut}: none'); continue
            print(f"  {cut}: n {o['n']} in {o['clusters']} clusters  " + '  '.join(f'{k} {v:.3f}' for k, v in o['hit_at_1'].items()))
            for b, x in (o.get('KEV_minus') or {}).items(): print(f"      KEV - {b}: {x['point']:+.3f} {x['ci95']}")


if __name__ == '__main__':
    main(*sys.argv[1:])
