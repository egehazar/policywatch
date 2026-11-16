"""Missing points on the rest of the 20 platforms' documents (stale/PLAN_missing_wide.md): every "Privacy Policy" and
"Terms of Service" of the 20 platforms that neither the pilot nor the larger test covered (most have more than 40
passages), through the cascade the larger test measured: the reranker scores every passage-case cell, then Kev reads
only the reranker's top 3 passages per case. A build for the curator page, with one built-in accuracy check (measure 1
on the documents with at least 10 known positives); no blind cards.

Differences from stale/missing2.py, both on purpose:
- negatives exclude every case with an approved point on the platform in stale/data/<platform>.json (all approved
  points, also those whose quote is under 3 words, which stale/match.py skips: the larger test's caveat);
- Kev's scores are stored as full rows with -1.0 for cells not on the shortlist, so stale.missing.best() picks the best
  shortlisted passage unchanged (p(yes) is never below 0).

prep | rerank (dedupe-research venv, offline) | kev [server] | measures
-> stale/out/missing_wide_docs.json, missing_wide_rerank.json, missing_wide_kev.json, missing_wide_measures.json
"""
import collections, json, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import typ, all_points, save, best, auroc, reading, MIN_POINTS
from stale.triage import TEMPLATE
from stale import missing2

DOCS = os.path.join(OUT, 'missing_wide_docs.json')
F = {a: os.path.join(OUT, f'missing_wide_{a.lower()}.json') for a in ('KEV', 'RERANK')}
NAMES = ('Privacy Policy.md', 'Terms of Service.md'); MIN_POS = 10; SHORT = 3; SEED = 20261124; DRAWS = 2000
NOFILL = -1.0


def load(p): return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def approved(plat):
    d = load(os.path.join(HERE, 'data', plat + '.json'))
    return {p['case_title'].strip() for p in d.get('points', []) if p.get('status') == 'approved'}


def prep():
    R = json.load(open(os.path.join(OUT, 'reloc_docs.json'), encoding='utf-8'))
    done = set(missing2.PILOT) | {d['doc'] for d in json.load(open(missing2.DOCS, encoding='utf-8'))['docs']}
    freq = collections.defaultdict(collections.Counter)
    for r in all_points(): freq[typ(r.get('tosdr_document'))][r['case_title']] += 1
    out = []
    for d in sorted(R['docs'], key=lambda d: d['doc']):
        name = d['doc']; plat, base = name.split('/', 1)
        if name in done or base not in NAMES: continue
        t = typ(base); P = sorted({it['case_title'] for it in d['items'] if it.get('gold')})
        C = sorted({c for c, n in freq[t].items() if n >= MIN_POINTS} | set(P))
        A = approved(plat); E = sorted(c for c in C if c not in P and c.strip() in A)
        N = sorted(c for c in C if c not in P and c not in E)
        out.append({'doc': name, 'type': t, 'pieces': d['pieces'], 'positives': P, 'excluded': E, 'negatives': N,
                    'cases': [c for c in C if c not in E]})
        print(f'{name} ({t}): {len(d["pieces"])} pieces, {len(P)} positives, {len(E)} excluded, {len(N)} negatives')
    with open(DOCS, 'w', encoding='utf-8') as f: json.dump({'docs': out}, f, ensure_ascii=False)
    cells = sum(len(x['pieces']) * len(x['cases']) for x in out)
    print(len(out), 'documents;', cells, 'reranker cells;', sum(SHORT * len(x['cases']) for x in out), 'Kev cells at most')


def rerank():
    from sentence_transformers import CrossEncoder
    m = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; out = load(F['RERANK']); t0 = time.time()
    for n, d in enumerate(D, 1):
        if d['doc'] in out: continue
        s0 = time.time(); rows = []
        for piece in d['pieces']:
            sc = m.predict([(c, piece) for c in d['cases']], batch_size=16)
            rows.append({c: round(float(x), 5) for c, x in zip(d['cases'], sc)})
        out[d['doc']] = rows; out.setdefault('_timing', {})[d['doc']] = round(time.time() - s0, 1); save(F['RERANK'], out)
        print(f'[{n}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}', flush=True)
    print('rerank done')


def kev(server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; RR = load(F['RERANK'])
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    out = load(F['KEV']); timing = out.get('_timing', {}); t0 = time.time()
    for n, d in enumerate(D, 1):
        if d['doc'] in out: continue
        need = collections.defaultdict(list)                         # piece -> cases shortlisted on it
        for c in d['cases']:
            for i in missing2.shortlist(RR[d['doc']], c): need[i].append(c)
        rows = [{c: NOFILL for c in d['cases']} for _ in d['pieces']]; a0, h0, s0 = S.asked, S.hits, time.time()
        for i in sorted(need):                                       # one request per passage with its shortlisted cases
            qs = [TEMPLATE.format(c) for c in need[i]]; ps = S.score(d['pieces'][i], qs)
            for c, q in zip(need[i], qs): rows[i][c] = ps[qid(q)]
        out[d['doc']] = rows
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'pieces': len(need), 'cells': sum(map(len, need.values())),
                            'asked_cells': S.asked - a0, 'cached_cells': S.hits - h0}
        out['_timing'] = timing; save(F['KEV'], out)
        print(f'[{n}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}: {timing[d["doc"]]}', flush=True)
    print('kev done; asked', S.asked, 'cache hits', S.hits)


def measures():
    """Measure 1 on the documents with at least MIN_POS positives: CASCADE_KEV (Kev on the shortlist) and RERANK (every
    passage), AUROC of positives against negatives, mean over those documents, and the difference with a 95% interval
    (resampling positives and negatives within each document)."""
    D = [d for d in json.load(open(DOCS, encoding='utf-8'))['docs'] if len(d['positives']) >= MIN_POS and d['negatives']]
    S = {a: load(F[a]) for a in F}; rng = random.Random(SEED)
    cs = {'CASCADE_KEV': {d['doc']: {c: best(S['KEV'][d['doc']], c)[0] for c in d['cases']} for d in D},
          'RERANK': {d['doc']: {c: best(S['RERANK'][d['doc']], c)[0] for c in d['cases']} for d in D}}
    au = {a: {d['doc']: auroc([cs[a][d['doc']][c] for c in d['positives']], [cs[a][d['doc']][c] for c in d['negatives']]) for d in D} for a in cs}
    mean = lambda a: sum(au[a].values()) / len(D)
    diffs = []
    for _ in range(DRAWS):
        tot = 0
        for d in D:
            P = [rng.choice(d['positives']) for _ in d['positives']]; N = [rng.choice(d['negatives']) for _ in d['negatives']]
            tot += (auroc([cs['CASCADE_KEV'][d['doc']][c] for c in P], [cs['CASCADE_KEV'][d['doc']][c] for c in N]) -
                    auroc([cs['RERANK'][d['doc']][c] for c in P], [cs['RERANK'][d['doc']][c] for c in N]))
        diffs.append(tot / len(D))
    diffs.sort(); ci = [round(diffs[int(.025 * DRAWS)], 3), round(diffs[int(.975 * DRAWS) - 1], 3)]
    res = {'docs': [{'doc': d['doc'], 'positives': len(d['positives']), 'negatives': len(d['negatives']),
                     **{f'{a}_auroc': round(au[a][d['doc']], 3) for a in au}} for d in D],
           'auroc': {a: round(mean(a), 3) for a in au},
           'CASCADE_KEV_minus_RERANK_auroc': {'point': round(mean('CASCADE_KEV') - mean('RERANK'), 3), 'ci95': ci,
                                              'reading': reading(ci, 'CASCADE_KEV better', 'RERANK better', 'no difference shown')},
           'timing': {a: S[a].get('_timing') for a in S}}
    with open(os.path.join(OUT, 'missing_wide_measures.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'timing'}, indent=1))


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'kev': kev(*sys.argv[2:3])
    else: {'prep': prep, 'rerank': rerank, 'measures': measures}[c]()
