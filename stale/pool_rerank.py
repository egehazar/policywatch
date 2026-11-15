"""Exploratory (not pre-registered, written after all three results were seen): Kev against the reranker, and Kev
against its base family, pooled over the relocation samples.

Parts A (stale/out/reloc2_result.json, 200 points, clustered by document), B (heldout_result.json, 202 points,
clustered by service) and D (contrib_result.json, 200 points, clustered by service) each read KEV - RERANK on hit@1
separately: +.07 (no difference shown), +.10 (Kev better), +.06 (no difference shown). This pools the per-point
differences with a bootstrap that resamples clusters within each part (stratified), so each part keeps its size.
It is a summary of results already reported, not a new test, and it decides nothing on the pages.
Usage  py -m stale.pool_rerank   -> stale/out/pool_rerank.json
"""
import json, os, random
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
PARTS = {'A': 'reloc2_result.json', 'B': 'heldout_result.json', 'D': 'contrib_result.json'}
SEED = 20261115; DRAWS = 4000


def diffs(rows, a, b):
    """{cluster: [per-point hit@1 difference]} for the points scored by both arms."""
    out = {}
    for r in rows:
        if a in r and b in r: out.setdefault(r['doc'], []).append(r[a]['hit']['1'] - r[b]['hit']['1'])
    return out


def pooled(parts, rng):
    point = sum(sum(sum(v) for v in c.values()) for c in parts) / sum(sum(len(v) for v in c.values()) for c in parts)
    stats = []
    for _ in range(DRAWS):
        s = n = 0
        for c in parts:
            keys = list(c)
            for k in (rng.choice(keys) for _ in keys): s += sum(c[k]); n += len(c[k])
        stats.append(s / n)
    stats.sort()
    return {'point': round(point, 3), 'ci95': [round(stats[int(.025 * DRAWS)], 3), round(stats[int(.975 * DRAWS) - 1], 3)],
            'points': sum(sum(len(v) for v in c.values()) for c in parts)}


def main():
    rng = random.Random(SEED)
    R = {p: json.load(open(os.path.join(OUT, f), encoding='utf-8'))['rows'] for p, f in PARTS.items()}
    res = {'note': 'exploratory: pooled after all three parts were read; stratified cluster bootstrap'}
    for a, b, ps in (('KEV', 'RERANK', 'ABD'), ('KEV', 'QWEN', 'AB'), ('QWEN', 'RERANK', 'AB')):
        per = {p: diffs(R[p], a, b) for p in ps}
        res[f'{a}_minus_{b}'] = {'parts': ps, 'per_part': {p: round(sum(sum(v) for v in c.values()) / sum(len(v) for v in c.values()), 3)
                                                          for p, c in per.items()}, **pooled(list(per.values()), rng)}
    with open(os.path.join(OUT, 'pool_rerank.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
