"""Missing points, the larger test (stale/PREREG_missing2.md): the pilot (stale/PREREG_missing.md) on 10 more documents,
plus Kev against its base family on the same shortlisted passages.

prep            choose the 10 documents and their candidate cases -> stale/out/missing2_docs.json (no model)
kev [server]    Kev-4B p(yes) for every piece and candidate case -> stale/out/missing2_kev.json
rerank          bge-reranker-v2-m3 for every piece and case -> stale/out/missing2_rerank.json
bm25            -> stale/out/missing2_bm25.json
qwen [port]     Qwen3.5-4B instruct, yes/no log-odds, only on each case's reranker top 3 pieces -> stale/out/missing2_qwen.json
measures        measures 1-2 and the blind cards -> stale/audit_missing2/, stale/out/missing2_key.json, missing2_measures.json
score           stale/audit_missing2/verdicts.json -> stale/out/missing2_result.json
Usage  py -m stale.missing2 prep | kev [server] | rerank | bm25 | qwen [port] | measures | score
"""
import collections, json, math, os, random, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import typ, all_points, save, best, auroc, reading, wilson, MIN_POINTS
from stale.relocate import bm25 as bm25_scores
from stale.triage import TEMPLATE

DOCS = os.path.join(OUT, 'missing2_docs.json'); AUD = os.path.join(HERE, 'audit_missing2')
KEY = os.path.join(OUT, 'missing2_key.json'); SEED = 20261122; DRAWS = 2000
MAX_PIECES = 40; MIN_POS = 10; SHORT = 3; TOP = 10; RANDOM_CARDS = 20; MAX_RANDOM_YES = 3; R_AT = 20
PILOT = {'Bluesky/Privacy Policy.md', 'X/Privacy Policy.md', 'Pinterest/Terms of Service.md', 'YouTube/Terms of Service.md'}
ARMS = ('KEV', 'RERANK', 'BM25', 'CASCADE_KEV', 'CASCADE_QWEN')
CARD_ARMS = ('KEV', 'RERANK', 'CASCADE_KEV', 'CASCADE_QWEN')
F = {a: os.path.join(OUT, f'missing2_{a.lower()}.json') for a in ('KEV', 'RERANK', 'BM25', 'QWEN')}


def load(p): return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def prep():
    R = json.load(open(os.path.join(OUT, 'reloc_docs.json'), encoding='utf-8'))
    pga = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    freq = collections.defaultdict(collections.Counter)
    for r in all_points(): freq[typ(r.get('tosdr_document'))][r['case_title']] += 1
    out = []
    for d in sorted(R['docs'], key=lambda d: d['doc']):
        name = d['doc']; t = typ(name.split('/', 1)[1]); P = sorted({it['case_title'] for it in d['items'] if it.get('gold')})
        if name in PILOT or t not in ('privacy', 'terms') or len(d['pieces']) > MAX_PIECES or len(P) < MIN_POS: continue
        plat = name.split('/', 1)[0]
        C = sorted({c for c, n in freq[t].items() if n >= MIN_POINTS} | set(P))
        E = sorted({r['case_title'] for r in pga if r['platform'] == plat} - set(P))
        N = sorted(set(C) - set(P) - set(E))
        out.append({'doc': name, 'type': t, 'pieces': d['pieces'], 'positives': P, 'excluded': [c for c in E if c in C],
                    'negatives': N, 'cases': [c for c in C if c not in E]})
        print(f'{name} ({t}): {len(d["pieces"])} pieces, {len(P)} positives, {len(N)} negatives -> {len(P) + len(N)} questions')
    with open(DOCS, 'w', encoding='utf-8') as f: json.dump({'docs': out}, f, ensure_ascii=False)
    print(len(out), 'documents;', sum(len(x['pieces']) * len(x['cases']) for x in out), 'piece-question cells;',
          sum(SHORT * len(x['cases']) for x in out), 'shortlist cells for the base family')


def kev(server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    D = json.load(open(DOCS, encoding='utf-8'))['docs']
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    out = load(F['KEV']); t0 = time.time(); timing = out.get('_timing', {})
    for n, d in enumerate(D, 1):
        if d['doc'] in out and len(out[d['doc']]) == len(d['pieces']): continue
        qs = [TEMPLATE.format(c) for c in d['cases']]; rows = []; a0, h0, s0 = S.asked, S.hits, time.time()
        for piece in d['pieces']:
            ps = S.score(piece, qs); rows.append({c: ps[qid(q)] for c, q in zip(d['cases'], qs)})
        out[d['doc']] = rows
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'pieces': len(d['pieces']), 'questions': len(qs),
                            'asked_cells': S.asked - a0, 'cached_cells': S.hits - h0}
        out['_timing'] = timing; save(F['KEV'], out)
        print(f'[{n}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}: {timing[d["doc"]]}', flush=True)
    print('kev done; asked', S.asked, 'cache hits', S.hits)


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


def bm25():
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; out = {}
    for d in D:
        per = {c: bm25_scores(c, d['pieces']) for c in d['cases']}
        out[d['doc']] = [{c: round(per[c][i], 5) for c in d['cases']} for i in range(len(d['pieces']))]
    save(F['BM25'], out); print('bm25 done')


def shortlist(rr_rows, c):
    """The reranker's top SHORT pieces for case c (ties to the earliest piece), in piece order."""
    return sorted(sorted(range(len(rr_rows)), key=lambda k: (-rr_rows[k][c], k))[:SHORT])


def qwen(port='9996'):
    from stale.relocate2 import qwen_ask
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; RR = load(F['RERANK']); out = load(F['QWEN']); t0 = time.time()
    timing = out.get('_timing', {})
    for n, d in enumerate(D, 1):
        if d['doc'] in out: continue
        need = collections.defaultdict(list)                         # piece -> cases shortlisted on it
        for c in d['cases']:
            for i in shortlist(RR[d['doc']], c): need[i].append(c)
        rows = {}; s0 = time.time(); miss = 0
        for i in sorted(need):                                       # piece first: one passage, then its questions
            rows[str(i)] = {}
            for c in need[i]:
                r = qwen_ask(port, d['pieces'][i], TEMPLATE.format(c)); miss += not (r['yes'] or r['no']); rows[str(i)][c] = r['lo']
        out[d['doc']] = rows
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'cells': sum(map(len, need.values())), 'pieces': len(need), 'no_yes_no': miss}
        out['_timing'] = timing; save(F['QWEN'], out)
        print(f'[{n}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}: {timing[d["doc"]]}', flush=True)
    print('qwen done')


def case_scores(D):
    """arm -> doc -> case -> (score, best piece)."""
    S = {a: load(F[a]) for a in F}; cs = {a: {} for a in ARMS}
    for d in D:
        doc = d['doc']; rr = S['RERANK'][doc]
        for a in ('KEV', 'RERANK', 'BM25'): cs[a][doc] = {c: best(S[a][doc], c) for c in d['cases']}
        ck, cq = {}, {}
        for c in d['cases']:
            sl = shortlist(rr, c)
            ck[c] = max(((S['KEV'][doc][i][c], -i) for i in sl)); ck[c] = (ck[c][0], -ck[c][1])
            cq[c] = max(((S['QWEN'][doc][str(i)][c], -i) for i in sl)); cq[c] = (cq[c][0], -cq[c][1])
        cs['CASCADE_KEV'][doc], cs['CASCADE_QWEN'][doc] = ck, cq
    return cs


def boot_diff(D, cs, a, b, rng):
    diffs = []
    for _ in range(DRAWS):
        tot = 0
        for d in D:
            P = [rng.choice(d['positives']) for _ in d['positives']]; N = [rng.choice(d['negatives']) for _ in d['negatives']]
            x, y = cs[a][d['doc']], cs[b][d['doc']]
            tot += auroc([x[c][0] for c in P], [x[c][0] for c in N]) - auroc([y[c][0] for c in P], [y[c][0] for c in N])
        diffs.append(tot / len(D))
    diffs.sort(); return [round(diffs[int(.025 * DRAWS)], 3), round(diffs[int(.975 * DRAWS) - 1], 3)]


def measures():
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; cs = case_scores(D); rng = random.Random(SEED)
    res = {'docs': [], 'auroc': {}, 'recall_at_20': {}}; au = {a: {} for a in ARMS}
    for d in D:
        row = {'doc': d['doc'], 'positives': len(d['positives']), 'negatives': len(d['negatives'])}
        for a in ARMS:
            s = cs[a][d['doc']]
            au[a][d['doc']] = auroc([s[c][0] for c in d['positives']], [s[c][0] for c in d['negatives']])
            ranked = sorted(d['cases'], key=lambda c: -s[c][0])[:R_AT]
            row[f'{a}_auroc'] = round(au[a][d['doc']], 3); row[f'{a}_recall20'] = round(sum(c in d['positives'] for c in ranked) / len(d['positives']), 3)
        res['docs'].append(row)
    for a in ARMS:
        res['auroc'][a] = round(sum(au[a].values()) / len(D), 3)
        res['recall_at_20'][a] = round(sum(r[f'{a}_recall20'] for r in res['docs']) / len(D), 3)
    for a, b, better, worse in (('KEV', 'RERANK', 'KEV better', 'KEV worse'), ('KEV', 'BM25', 'KEV better', 'KEV worse'),
                                ('CASCADE_KEV', 'CASCADE_QWEN', 'KEV better than its base family', 'base family better')):
        ci = boot_diff(D, cs, a, b, rng)
        res[f'{a}_minus_{b}_auroc'] = {'point': round(res['auroc'][a] - res['auroc'][b], 3), 'ci95': ci,
                                       'reading': reading(ci, better, worse, 'no difference shown')}
    cards = {}
    for d in D:
        for a in CARD_ARMS:
            s = cs[a][d['doc']]
            for c in sorted(d['negatives'], key=lambda c: -s[c][0])[:TOP]: cards.setdefault((d['doc'], c, s[c][1]), set()).add(a)
    for _ in range(RANDOM_CARDS):
        d = rng.choice(D); c = rng.choice(d['negatives']); i = rng.randrange(len(d['pieces']))
        cards.setdefault((d['doc'], c, i), set()).add('RANDOM')
    order = sorted(cards); rng.shuffle(order); piece = {d['doc']: d['pieces'] for d in D}
    os.makedirs(AUD, exist_ok=True)
    L = [f'# {len(order)} cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
    key = {}
    for n, (doc, c, i) in enumerate(order, 1):
        cid = f'N{n:03d}'; key[cid] = {'doc': doc, 'case': c, 'piece': i, 'arms': sorted(cards[(doc, c, i)])}
        L += [f'## {cid}', f'**Case:** {c}', '', '**Passage:**', '', '```', piece[doc][i].strip(), '```', '']
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
    shutil.copyfile(os.path.join(HERE, 'audit_states', 'README.md'), os.path.join(AUD, 'README.md'))
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({cid: {'verdict': '', 'why': ''} for cid in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump(key, f, indent=1, ensure_ascii=False)
    res['cards'] = {'total': len(key), 'random': sum('RANDOM' in v['arms'] for v in key.values()),
                    'per_arm': {a: sum(a in v['arms'] for v in key.values()) for a in CARD_ARMS}}
    res['timing'] = {a: load(F[a]).get('_timing') for a in ('KEV', 'RERANK', 'QWEN')}
    with open(os.path.join(OUT, 'missing2_measures.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'timing'}, indent=1))


def prec(K, V, arms):
    r = {}
    for a in arms:
        cs = [c for c in K if a in K[c]['arms']]; y = sum(V[c]['verdict'] == 'YES' for c in cs)
        r[a] = {'cards': len(cs), 'yes': y, 'yes_share': round(y / len(cs), 3), 'wilson95': wilson(y, len(cs)),
                'yes_or_partly_share': round(sum(V[c]['verdict'] != 'NO' for c in cs) / len(cs), 3)}
    return r


def prec_diff(K, V, a, b, rng):
    """YES share of arm a minus arm b, 95% interval from resampling documents."""
    docs = sorted({K[c]['doc'] for c in K}); by = collections.defaultdict(list)
    for c in K: by[K[c]['doc']].append(c)
    def share(ds, arm):
        cs = [c for d in ds for c in by[d] if arm in K[c]['arms']]
        return sum(V[c]['verdict'] == 'YES' for c in cs) / len(cs) if cs else 0
    diffs = sorted(share(s, a) - share(s, b) for s in ([rng.choice(docs) for _ in docs] for _ in range(DRAWS)))
    return {'point': round(share(docs, a) - share(docs, b), 3), 'ci95': [round(diffs[int(.025 * DRAWS)], 3), round(diffs[int(.975 * DRAWS) - 1], 3)]}


def score():
    K = json.load(open(KEY, encoding='utf-8')); V = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V) == set(K) and all(V[c]['verdict'] in ('YES', 'PARTLY', 'NO') for c in V), 'verdicts incomplete'
    M = json.load(open(os.path.join(OUT, 'missing2_measures.json'), encoding='utf-8')); rng = random.Random(SEED + 1)
    rnd = [V[c]['verdict'] for c in K if 'RANDOM' in K[c]['arms']]
    res = {'random_yes': rnd.count('YES'), 'random_n': len(rnd), 'valid': rnd.count('YES') <= MAX_RANDOM_YES,
           'precision_at_10': prec(K, V, CARD_ARMS),
           'precision_diff': {'KEV_minus_RERANK': prec_diff(K, V, 'KEV', 'RERANK', rng),
                              'CASCADE_KEV_minus_CASCADE_QWEN': prec_diff(K, V, 'CASCADE_KEV', 'CASCADE_QWEN', rng)}}
    k = res['precision_at_10']['KEV']; p = res['precision_at_10']
    rep = res['valid'] and k['yes_share'] >= .30 and k['wilson95'][0] >= .15 and M['KEV_minus_BM25_auroc']['reading'] == 'KEV better'
    res['reading_replication'] = 'NOT VALID (random controls)' if not res['valid'] else 'REPLICATED' if rep else 'NOT REPLICATED'
    kr = M['KEV_minus_RERANK_auroc']['reading']
    res['reading_reranker'] = ('KEV better' if kr == 'KEV better' and p['KEV']['yes_share'] >= p['RERANK']['yes_share'] else
                               'RERANK better' if kr == 'KEV worse' and p['RERANK']['yes_share'] >= p['KEV']['yes_share'] else
                               'no difference shown')
    res['reading_base_family'] = M['CASCADE_KEV_minus_CASCADE_QWEN_auroc']['reading']
    res['measures'] = {x: M[x] for x in ('auroc', 'recall_at_20', 'KEV_minus_RERANK_auroc', 'KEV_minus_BM25_auroc',
                                          'CASCADE_KEV_minus_CASCADE_QWEN_auroc')}
    with open(os.path.join(OUT, 'missing2_result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'kev': kev(*sys.argv[2:3])
    elif c == 'qwen': qwen(*sys.argv[2:3])
    else: {'prep': prep, 'rerank': rerank, 'bm25': bm25, 'measures': measures, 'score': score}[c]()
