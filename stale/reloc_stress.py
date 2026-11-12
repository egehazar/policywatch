"""Stress checks on the relocation result, computed from scores on disk (exploratory, written after the result).

1. Wrong question: Kev's top piece for ANOTHER point's question in the same document, scored against this point's
   gold. If Kev only picked salient pieces, this would stay high; if it reads the question, it falls toward chance.
2. Clustering: the KEV-minus-baseline intervals resampling cases (111) and documents x cases, not documents alone.
3. Gold threshold: gold = pieces with >= .5 / >= .8 of the quote's 6-grams instead of .3.
4. Where the lexical baseline misses: Kev's hit@1 on the points BM25 gets wrong, and the reverse.
5. Recent points: points created on ToS;DR in 2026 (after Qwen3.5's release, so outside its pretraining).
Usage  python -m stale.reloc_stress
"""
import collections, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); sys.path.insert(0, os.path.dirname(HERE))
from stale.relocate import sample, hit, qcov, SEED

D, need, chosen = sample(200)
K = json.load(open(os.path.join(OUT, 'reloc_kev.json'), encoding='utf-8'))
B = json.load(open(os.path.join(OUT, 'reloc_base.json'), encoding='utf-8'))
P = {json.loads(l)['point']: json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')}
CREATED = {p['point']: p.get('created_at') or '' for p in json.load(open(os.path.join(OUT, 'reanchored.json'), encoding='utf-8'))['points']}
arm = {'KEV': lambda d, q: [s[q] for s in K[d]['scores']], 'BM25': lambda d, q: B['BM25'][d][q], 'BGE': lambda d, q: B['BGE'][d][q]}
rows = []
for d in D['docs']:
    if d['doc'] not in need: continue
    qs = need[d['doc']]
    for it in d['items']:
        if it['point'] not in chosen: continue
        r = {'doc': d['doc'], 'case': it['case_title'], 'point': it['point'], 'q': it['question'], 'gold': it['gold'], 'n': len(d['pieces']),
             'created': CREATED.get(it['point'], '')}
        for a, f in arm.items():
            r[a] = hit(f(d['doc'], it['question']), it['gold'])[0][1]
            other = [q for q in qs if q != it['question']]
            r[a + '_wrongq'] = sum(hit(f(d['doc'], q), it['gold'])[0][1] for q in other) / len(other) if other else None
        r['chance'] = len(it['gold']) / len(d['pieces'])
        r['_d'] = d; r['_it'] = it
        rows.append(r)
mean = lambda xs: round(sum(xs) / len(xs), 3) if xs else None

print('1. WRONG QUESTION (points whose document has another sampled question)')
w = [r for r in rows if r['KEV_wrongq'] is not None]
for a in arm: print(f'   {a:5} right question {mean([r[a] for r in w])}   another point\'s question {mean([r[a + "_wrongq"] for r in w])}')
print(f'   chance {mean([r["chance"] for r in w])}   (n={len(w)})')


def boot(f, unit):
    rng = random.Random(SEED); docs = sorted({r['doc'] for r in rows}); cases = sorted({r['case'] for r in rows}); ds = []
    for _ in range(2000):
        if unit == 'case':
            c = collections.Counter(rng.choice(cases) for _ in cases); wts = [c[r['case']] for r in rows]
        else:      # two-way: documents and cases drawn independently, a point counts doc-draws x case-draws times
            cd = collections.Counter(rng.choice(docs) for _ in docs); cc = collections.Counter(rng.choice(cases) for _ in cases)
            wts = [cd[r['doc']] * cc[r['case']] for r in rows]
        if sum(wts): ds.append(sum(w_ * f(r) for w_, r in zip(wts, rows)) / sum(wts))
    ds.sort(); k = len(ds)
    return [round(ds[int(.025 * k)], 3), round(ds[int(.975 * k) - 1], 3)]


print('\n2. CLUSTERING: KEV minus baseline, hit@1, 95% intervals')
for o in ('BM25', 'BGE'):
    f = lambda r, o=o: r['KEV'] - r[o]
    print(f'   KEV-{o}: point {mean([f(r) for r in rows])}  cases {boot(f, "case")}  documents x cases {boot(f, "two")}')

print('\n3. GOLD THRESHOLD (pieces with >= t of the quote\'s 6-grams)')
for t in (.3, .5, .8):
    res = collections.defaultdict(list)
    for r in rows:
        d, it = r['_d'], r['_it']
        g = [i for i, p in enumerate(d['pieces']) if qcov(P[it['point']]['quote'], p) >= t]
        if not g: continue
        for a, f in arm.items(): res[a].append(hit(f(d['doc'], it['question']), g)[0][1])
    print(f'   t={t}: n={len(res["KEV"])}  ' + '  '.join(f'{a} {mean(v)}' for a, v in res.items()))

print('\n4. WHERE THE OTHER ARM MISSES')
for o in ('BM25', 'BGE'):
    miss = [r for r in rows if r[o] < .5]; hitr = [r for r in rows if r[o] >= .5]
    print(f'   {o} misses (n={len(miss)}): KEV {mean([r["KEV"] for r in miss])}   {o} hits (n={len(hitr)}): KEV {mean([r["KEV"] for r in hitr])}')
km = [r for r in rows if r['KEV'] < .5]
print(f'   KEV misses (n={len(km)}): BM25 {mean([r["BM25"] for r in km])}  BGE {mean([r["BGE"] for r in km])}')

print('\n5. RECENT POINTS (ToS;DR point created on/after the date)')
for day in ('2025-07-01', '2026-01-01', '2026-06-01'):
    s = [r for r in rows if r['created'] >= day]
    print(f'   {day}: n={len(s)}  ' + '  '.join(f'{a} {mean([r[a] for r in s])}' for a in arm))
