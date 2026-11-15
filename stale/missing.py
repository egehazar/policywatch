"""Missing points pilot (stale/PREREG_missing.md): which ToS;DR cases does a document state that ToS;DR has no point for?

prep            choose the 4 documents and their candidate cases -> stale/out/missing_docs.json (no model)
kev [server]    Kev-4B p(yes), all of a document's candidate questions per piece -> stale/out/missing_kev.json
rerank          bge-reranker-v2-m3 (case title, piece) -> stale/out/missing_rerank.json
bm25            -> stale/out/missing_bm25.json
measures        measures 1 and 2, and the blind cards for measure 3 -> stale/audit_missing/cards.md, README.md,
                stale/out/missing_key.json, stale/out/missing_measures.json
score           stale/audit_missing/verdicts.json -> stale/out/missing_result.json (measure 3 and the readings)
Usage  py -m stale.missing prep | kev [server] | rerank | bm25 | measures | score
"""
import collections, glob, json, math, os, random, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.relocate import bm25 as bm25_scores
from stale.triage import TEMPLATE

DOCS = os.path.join(OUT, 'missing_docs.json'); AUD = os.path.join(HERE, 'audit_missing')
KEY = os.path.join(OUT, 'missing_key.json'); SEED = 20261121; DRAWS = 2000
MAX_PIECES = 30; PER_TYPE = 2; MIN_POINTS = 10; TOP = 10; RANDOM_CARDS = 10; R_AT = 20
ARMS = ('KEV', 'RERANK', 'BM25')


def typ(name):
    n = (name or '').lower()
    if 'privacy' in n or 'data policy' in n: return 'privacy'
    if 'terms' in n: return 'terms'
    return 'other'


def all_points():
    rows = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    for f in sorted(glob.glob(os.path.join(HERE, 'wide', '*', 'out', 'points.jsonl'))):
        rows += [json.loads(l) for l in open(f, encoding='utf-8')]
    return rows


def prep():
    R = json.load(open(os.path.join(OUT, 'reloc_docs.json'), encoding='utf-8'))
    pga = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    freq = collections.defaultdict(collections.Counter)
    for r in all_points(): freq[typ(r.get('tosdr_document'))][r['case_title']] += 1
    ranked = []
    for d in R['docs']:
        t = typ(d['doc'].split('/', 1)[1]); P = sorted({it['case_title'] for it in d['items'] if it.get('gold')})
        if t in ('privacy', 'terms') and len(d['pieces']) <= MAX_PIECES: ranked.append((-len(P), d['doc'], t, P, d))
    ranked.sort(key=lambda x: (x[0], x[1]))
    chosen, used, per = [], set(), collections.Counter()
    for _, name, t, P, d in ranked:
        plat = name.split('/', 1)[0]
        if per[t] < PER_TYPE and plat not in used:
            chosen.append((name, t, P, d)); used.add(plat); per[t] += 1
    out = []
    for name, t, P, d in chosen:
        plat = name.split('/', 1)[0]
        frequent = {c for c, n in freq[t].items() if n >= MIN_POINTS}
        C = sorted(frequent | set(P))
        E = sorted({r['case_title'] for r in pga if r['platform'] == plat} - set(P))
        N = sorted(set(C) - set(P) - set(E))
        out.append({'doc': name, 'type': t, 'pieces': d['pieces'], 'positives': P, 'excluded': [c for c in E if c in C],
                    'negatives': N, 'cases': [c for c in C if c not in E]})
        print(f'{name} ({t}): {len(d["pieces"])} pieces, {len(P)} positives, {len(N)} negatives, '
              f'{len(set(E) & set(C))} excluded -> {len(P) + len(N)} questions')
    with open(DOCS, 'w', encoding='utf-8') as f: json.dump({'docs': out}, f, ensure_ascii=False)
    print(sum(len(x['pieces']) * len(x['cases']) for x in out), 'piece-question cells')


def save(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(obj, f)
    os.replace(tmp, path)


def kev(server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    D = json.load(open(DOCS, encoding='utf-8'))['docs']
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    path = os.path.join(OUT, 'missing_kev.json'); out = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    t0 = time.time(); timing = out.get('_timing', {})
    for n, d in enumerate(D, 1):
        if d['doc'] in out and len(out[d['doc']]) == len(d['pieces']): continue
        qs = [TEMPLATE.format(c) for c in d['cases']]; rows = []; a0, h0, s0 = S.asked, S.hits, time.time()
        for piece in d['pieces']:
            ps = S.score(piece, qs); rows.append({c: ps[qid(q)] for c, q in zip(d['cases'], qs)})
        out[d['doc']] = rows
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'pieces': len(d['pieces']), 'questions': len(qs),
                            'asked_cells': S.asked - a0, 'cached_cells': S.hits - h0}
        out['_timing'] = timing; save(path, out)
        print(f'[{n}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}: {len(d["pieces"])} pieces x {len(qs)} questions, '
              f'{timing[d["doc"]]}', flush=True)
    print('kev done; asked', S.asked, 'cache hits', S.hits)


def rerank():
    from sentence_transformers import CrossEncoder
    m = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    D = json.load(open(DOCS, encoding='utf-8'))['docs']
    path = os.path.join(OUT, 'missing_rerank.json'); out = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    t0 = time.time()
    for n, d in enumerate(D, 1):
        if d['doc'] in out: continue
        s0 = time.time(); rows = []
        for piece in d['pieces']:
            sc = m.predict([(c, piece) for c in d['cases']], batch_size=16)
            rows.append({c: round(float(x), 5) for c, x in zip(d['cases'], sc)})
        out[d['doc']] = rows; out.setdefault('_timing', {})[d['doc']] = round(time.time() - s0, 1); save(path, out)
        print(f'[{n}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}', flush=True)
    print('rerank done')


def bm25():
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; out = {}
    for d in D:
        per = {c: bm25_scores(c, d['pieces']) for c in d['cases']}
        out[d['doc']] = [{c: round(per[c][i], 5) for c in d['cases']} for i in range(len(d['pieces']))]
    save(os.path.join(OUT, 'missing_bm25.json'), out); print('bm25 done')


def scores():
    f = {'KEV': 'missing_kev.json', 'RERANK': 'missing_rerank.json', 'BM25': 'missing_bm25.json'}
    return {a: json.load(open(os.path.join(OUT, p), encoding='utf-8')) for a, p in f.items()}


def best(rows, c):
    """(best score, best piece) for case c; ties go to the earliest piece."""
    i = max(range(len(rows)), key=lambda k: (rows[k][c], -k)); return rows[i][c], i


def auroc(pos, neg):
    if not pos or not neg: return None
    return sum((x > y) + .5 * (x == y) for x in pos for y in neg) / (len(pos) * len(neg))


def reading(ci, better, worse, none):
    return better if ci[0] > 0 else worse if ci[1] < 0 else none


def measures():
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; S = scores(); rng = random.Random(SEED)
    case_score = {a: {d['doc']: {c: best(S[a][d['doc']], c) for c in d['cases']} for d in D} for a in ARMS}
    res = {'docs': [], 'auroc': {}, 'recall_at_20': {}}
    au = {a: {} for a in ARMS}
    for d in D:
        row = {'doc': d['doc'], 'positives': len(d['positives']), 'negatives': len(d['negatives'])}
        for a in ARMS:
            cs = case_score[a][d['doc']]
            au[a][d['doc']] = auroc([cs[c][0] for c in d['positives']], [cs[c][0] for c in d['negatives']])
            ranked = sorted(d['cases'], key=lambda c: -cs[c][0])[:R_AT]
            row[f'{a}_auroc'] = round(au[a][d['doc']], 3); row[f'{a}_recall20'] = round(sum(c in d['positives'] for c in ranked) / len(d['positives']), 3)
        res['docs'].append(row)
    for a in ARMS:
        res['auroc'][a] = round(sum(au[a].values()) / len(D), 3)
        res['recall_at_20'][a] = round(sum(r[f'{a}_recall20'] for r in res['docs']) / len(D), 3)
    for b in ('RERANK', 'BM25'):
        diffs = []
        for _ in range(DRAWS):
            tot = 0
            for d in D:
                P = [rng.choice(d['positives']) for _ in d['positives']]; N = [rng.choice(d['negatives']) for _ in d['negatives']]
                k = case_score['KEV'][d['doc']]; o = case_score[b][d['doc']]
                tot += auroc([k[c][0] for c in P], [k[c][0] for c in N]) - auroc([o[c][0] for c in P], [o[c][0] for c in N])
            diffs.append(tot / len(D))
        diffs.sort(); ci = [round(diffs[int(.025 * DRAWS)], 3), round(diffs[int(.975 * DRAWS) - 1], 3)]
        res[f'KEV_minus_{b}_auroc'] = {'point': round(res['auroc']['KEV'] - res['auroc'][b], 3), 'ci95': ci,
                                       'reading': reading(ci, 'KEV better', 'KEV worse', 'no difference shown')}
    # measure 3: blind cards
    cards = {}
    for d in D:
        for a in ARMS:
            cs = case_score[a][d['doc']]
            for c in sorted(d['negatives'], key=lambda c: -cs[c][0])[:TOP]:
                cards.setdefault((d['doc'], c, cs[c][1]), set()).add(a)
    for _ in range(RANDOM_CARDS):
        d = rng.choice(D); c = rng.choice(d['negatives']); i = rng.randrange(len(d['pieces']))
        cards.setdefault((d['doc'], c, i), set()).add('RANDOM')
    order = sorted(cards); rng.shuffle(order)
    piece = {d['doc']: d['pieces'] for d in D}
    os.makedirs(AUD, exist_ok=True)
    L = [f'# {len(order)} cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
    key = {}
    for n, (doc, c, i) in enumerate(order, 1):
        cid = f'M{n:03d}'; key[cid] = {'doc': doc, 'case': c, 'piece': i, 'arms': sorted(cards[(doc, c, i)])}
        L += [f'## {cid}', f'**Case:** {c}', '', '**Passage:**', '', '```', piece[doc][i].strip(), '```', '']
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
    shutil.copyfile(os.path.join(HERE, 'audit_states', 'README.md'), os.path.join(AUD, 'README.md'))
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({cid: {'verdict': '', 'why': ''} for cid in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump(key, f, indent=1, ensure_ascii=False)
    res['cards'] = {'total': len(key), 'random': sum('RANDOM' in v['arms'] for v in key.values()),
                    'per_arm': {a: sum(a in v['arms'] for v in key.values()) for a in ARMS}}
    timing = {a: S[a].get('_timing') for a in ('KEV', 'RERANK')}; res['timing'] = timing
    with open(os.path.join(OUT, 'missing_measures.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


def wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; den = 1 + z * z / n; mid = (p + z * z / (2 * n)) / den; half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(mid - half, 3), round(mid + half, 3)]


def score():
    K = json.load(open(KEY, encoding='utf-8')); V = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V) == set(K) and all(V[c]['verdict'] in ('YES', 'PARTLY', 'NO') for c in V), 'verdicts incomplete'
    M = json.load(open(os.path.join(OUT, 'missing_measures.json'), encoding='utf-8'))
    rnd = [V[c]['verdict'] for c in K if 'RANDOM' in K[c]['arms']]
    res = {'random_yes': rnd.count('YES'), 'random_n': len(rnd), 'valid': rnd.count('YES') <= 2, 'precision_at_10': {}}
    for a in ARMS:
        cs = [c for c in K if a in K[c]['arms']]; y = sum(V[c]['verdict'] == 'YES' for c in cs)
        yp = sum(V[c]['verdict'] != 'NO' for c in cs)
        res['precision_at_10'][a] = {'cards': len(cs), 'yes': y, 'yes_share': round(y / len(cs), 3), 'wilson95': wilson(y, len(cs)),
                                     'yes_or_partly_share': round(yp / len(cs), 3)}
    k = res['precision_at_10']['KEV']
    worth = res['valid'] and k['yes_share'] >= .30 and k['wilson95'][0] >= .15 and M['KEV_minus_BM25_auroc']['reading'] == 'KEV better'
    res['reading'] = ('NOT VALID (random controls)' if not res['valid'] else 'WORTH BUILDING' if worth else 'NOT WORTH BUILDING AS IS')
    kr = M['KEV_minus_RERANK_auroc']['reading']; pr = res['precision_at_10']
    res['method'] = ('Kev' if kr == 'KEV better' and pr['KEV']['yes_share'] >= pr['RERANK']['yes_share'] else
                     'the reranker (Kev ahead not shown)')
    res['measures'] = {k_: M[k_] for k_ in ('auroc', 'recall_at_20', 'KEV_minus_RERANK_auroc', 'KEV_minus_BM25_auroc')}
    with open(os.path.join(OUT, 'missing_result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'kev': kev(*sys.argv[2:3])
    else: {'prep': prep, 'rerank': rerank, 'bm25': bm25, 'measures': measures, 'score': score}[c]()
