"""Missing points beyond the 20 platforms (stale/PLAN_missing_contrib.md): 20 privacy policies and terms of service drawn
at random from Open Terms Archive's contrib collection, through the curator page's cascade (the reranker scores every
passage, Kev reads only its top 3 passages per case), then rated blind: the page's top 10 per document against the
reranker's own top 10, with random controls; and the p(yes) the page prints, read as a label (0.90 or more).

prep          no model: draw the documents and their candidate cases -> stale/out/missing_contrib_docs.json
rerank        bge-reranker-v2-m3 on every passage-case cell (dedupe-research venv, offline) -> missing_contrib_rerank.json
kev [server]  Kev-4B on the reranker's top 3 passages per case -> missing_contrib_kev.json
cards         blind cards -> stale/audit_contrib_a/, stale/audit_contrib_b/, stale/out/missing_contrib_key.json
score         -> stale/out/missing_contrib_result.json
"""
import collections, json, os, random, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import typ, all_points, save, best, wilson, MIN_POINTS, TOP
from stale.triage import TEMPLATE
from stale import missing2, missing_wide

SEED = 20261118; DRAWS = 2000; PER_TYPE = 10; MAX_PIECES = 80; RANDOM_CARDS = 20; MAX_RANDOM_YES = 3
HIGH = .90; LABEL_MIN = .70                       # the label: printed p(yes) 0.90 or more; adopted at a Wilson low >= .70
PAGE_RANGE = (.60, .80)
WIDE = os.path.join(HERE, 'wide', 'contrib')
DOCS = os.path.join(OUT, 'missing_contrib_docs.json')
F = {a: os.path.join(OUT, f'missing_contrib_{a.lower()}.json') for a in ('KEV', 'RERANK')}
KEY = os.path.join(OUT, 'missing_contrib_key.json'); RESULT = os.path.join(OUT, 'missing_contrib_result.json')
FOLDERS = {x: os.path.join(HERE, f'audit_contrib_{x}') for x in 'ab'}
NAMES = missing_wide.NAMES; NOFILL = missing_wide.NOFILL
ARMS = ('PAGE', 'RERANK'); SCORES = {'PAGE': 'KEV', 'RERANK': 'RERANK'}; VERD = ('YES', 'PARTLY', 'NO')


def load(p): return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def approved(service):
    """Every case title with an approved point on the service in the snapshot (stale/wide/contrib/data/), any quote
    length."""
    d = load(os.path.join(WIDE, 'data', service + '.json'))
    return {p['case_title'].strip() for p in d.get('points', []) if p.get('status') == 'approved'}


def population():
    """[(doc, type, pieces)]: every "Privacy Policy.md" and "Terms of Service.md" at the contrib clone's HEAD whose
    service is mapped to ToS;DR (stale/wide/contrib/map.json; the 20 platforms are not mapped there), with 1 to
    MAX_PIECES passages, in English by stale.missing_page.english. Passages as part D cut them."""
    from policywatch import archive
    from stale.relocate_d import current_pieces
    from stale.wide import vdir
    from stale.missing_page import english
    M = json.load(open(os.path.join(WIDE, 'map.json'), encoding='utf-8'))['mapped']
    out = []
    for f in sorted(archive.git(vdir('contrib'), 'ls-tree', '-r', '--name-only', 'HEAD').split('\n')):
        if '/' not in f: continue
        svc, base = f.split('/', 1)
        if svc not in M or base not in NAMES: continue
        _, P = current_pieces(f)
        if 1 <= len(P) <= MAX_PIECES and english(P): out.append((f, typ(base), P))
    return out


def draw(pop, rng):
    """Services in a seeded random order; from each, one document of a type still short of PER_TYPE (a coin flip when
    both types are open and the service has both), until there are PER_TYPE of each."""
    by = collections.defaultdict(dict)
    for f, t, P in pop: by[f.split('/', 1)[0]][t] = (f, P)
    svcs = sorted(by); rng.shuffle(svcs); n = collections.Counter(); out = []
    for s in svcs:
        opts = [t for t in ('privacy', 'terms') if t in by[s] and n[t] < PER_TYPE]
        if not opts: continue
        t = rng.choice(opts); n[t] += 1; out.append((by[s][t][0], t, by[s][t][1]))
        if len(out) == 2 * PER_TYPE: break
    return out


def prep():
    from policywatch import archive
    from stale.wide import vdir
    assert not os.path.exists(DOCS), 'documents drawn already'
    freq = collections.defaultdict(collections.Counter)
    for r in all_points(): freq[typ(r.get('tosdr_document'))][r['case_title']] += 1
    pts = [json.loads(l) for l in open(os.path.join(WIDE, 'out', 'points.jsonl'), encoding='utf-8')]
    pop = population(); out = []
    for name, t, pieces in draw(pop, random.Random(SEED)):
        svc = name.split('/', 1)[0]
        P = sorted({r['case_title'] for r in pts if r.get('doc') == name and r.get('status') == 'present'})
        C = sorted({c for c, n in freq[t].items() if n >= MIN_POINTS} | set(P))
        A = approved(svc); E = sorted(c for c in C if c not in P and c.strip() in A)
        N = sorted(c for c in C if c not in P and c not in E)
        out.append({'doc': name, 'type': t, 'pieces': pieces, 'positives': P, 'excluded': E, 'negatives': N,
                    'cases': [c for c in C if c not in E]})
        print(f'{name} ({t}): {len(pieces)} pieces, {len(P)} known positives, {len(E)} excluded, {len(N)} candidates')
    head = archive.git(vdir('contrib'), 'rev-parse', 'HEAD').strip()
    with open(DOCS, 'w', encoding='utf-8') as f:
        json.dump({'archive_head': head, 'population': len(pop), 'docs': out}, f, ensure_ascii=False)
    print(len(pop), 'documents in the population;', len(out), 'drawn at', head[:10], ';',
          sum(len(x['pieces']) * len(x['cases']) for x in out), 'reranker cells;',
          sum(missing2.SHORT * len(x['cases']) for x in out), 'Kev cells at most')


def rerank():
    from sentence_transformers import CrossEncoder
    m = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    D = load(DOCS)['docs']; out = load(F['RERANK']); t0 = time.time()
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
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    D = load(DOCS)['docs']; RR = load(F['RERANK']); out = load(F['KEV']); timing = out.get('_timing', {}); t0 = time.time()
    for n, d in enumerate(D, 1):
        if d['doc'] in out: continue
        need = collections.defaultdict(list)                         # passage -> cases shortlisted on it
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


def shown(s):
    """p(yes) as the page prints it (two decimals)."""
    return float(f'{s:.2f}')


def cards():
    assert not os.path.exists(KEY), 'cards exist already: never rebuild them after rating has started'
    rng = random.Random(SEED + 1); D = load(DOCS)['docs']; S = {a: load(F[a]) for a in F}
    C = collections.defaultdict(dict); page_p = {}
    for d in D:
        for a in ARMS:
            rows = S[SCORES[a]][d['doc']]; sc = {c: best(rows, c) for c in d['negatives']}
            for r, c in enumerate(sorted(d['negatives'], key=lambda c: -sc[c][0])[:TOP], 1):
                C[(d['doc'], c, sc[c][1])][a] = r
                if a == 'PAGE': page_p[(d['doc'], c, sc[c][1])] = sc[c][0]
    for _ in range(RANDOM_CARDS):
        d = rng.choice(D); c = rng.choice(d['negatives']); i = rng.randrange(len(d['pieces']))
        C[(d['doc'], c, i)]['RANDOM'] = 0
    info = {d['doc']: d for d in D}
    order = sorted(C); rng.shuffle(order); half = (len(order) + 1) // 2; key = {}
    for x, part in (('a', order[:half]), ('b', order[half:])):
        os.makedirs(FOLDERS[x], exist_ok=True)
        L = [f'# {len(part)} cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
        for doc, c, i in part:
            cid = f'C{len(key) + 1:03d}'
            key[cid] = {'doc': doc, 'case': c, 'piece': i, 'arms': C[(doc, c, i)], 'folder': x, 'type': info[doc]['type'],
                        'known_positives': len(info[doc]['positives'])}
            if (doc, c, i) in page_p: key[cid]['page_p'] = page_p[(doc, c, i)]
            L += [f'## {cid}', f'**Case:** {c}', '', '**Passage:**', '', '```', info[doc]['pieces'][i].strip(), '```', '']
        with open(os.path.join(FOLDERS[x], 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
        shutil.copyfile(os.path.join(HERE, 'audit_states', 'README.md'), os.path.join(FOLDERS[x], 'README.md'))
        with open(os.path.join(FOLDERS[x], 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump({cid: {'verdict': '', 'why': ''} for cid in key if key[cid]['folder'] == x}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump(key, f, indent=1, ensure_ascii=False)
    n = {a: sum(a in v['arms'] for v in key.values()) for a in ARMS + ('RANDOM',)}
    print(len(key), 'cards;', n, '; both arms:', sum(all(a in v['arms'] for a in ARMS) for v in key.values()),
          '; folder a', sum(v['folder'] == 'a' for v in key.values()), ', b', sum(v['folder'] == 'b' for v in key.values()))


def share(V, cs):
    y = sum(V[c]['verdict'] == 'YES' for c in cs)
    return {'cards': len(cs), 'yes': y, 'yes_share': round(y / len(cs), 3) if cs else None, 'wilson95': wilson(y, len(cs)),
            'yes_or_partly_share': round(sum(V[c]['verdict'] != 'NO' for c in cs) / len(cs), 3) if cs else None}


def boot(K, V, ga, gb, rng):
    """YES share of card group ga minus group gb (each a predicate on a key entry), pooled over documents; 95%
    interval from resampling documents (draws where either group is empty are dropped and counted)."""
    by = collections.defaultdict(list)
    for c in K: by[K[c]['doc']].append(c)
    docs = sorted(by)
    def sh(ds, g):
        cs = [c for d in ds for c in by[d] if g(K[c])]
        return sum(V[c]['verdict'] == 'YES' for c in cs) / len(cs) if cs else None
    ds = []
    for _ in range(DRAWS):
        s = [rng.choice(docs) for _ in docs]; a, b = sh(s, ga), sh(s, gb)
        if a is not None and b is not None: ds.append(a - b)
    ds.sort(); n = len(ds)
    return {'documents': len(docs), 'point': round(sh(docs, ga) - sh(docs, gb), 3), 'draws_used': n,
            'ci95': [round(ds[int(.025 * n)], 3), round(ds[int(.975 * n) - 1], 3)]}


def score():
    K = load(KEY); V = {}
    for x in FOLDERS: V.update(load(os.path.join(FOLDERS[x], 'verdicts.json')))
    assert set(V) == set(K) and all(V[c]['verdict'] in VERD for c in V), 'verdicts incomplete'
    rnd = [V[c]['verdict'] for c in K if 'RANDOM' in K[c]['arms']]; valid = rnd.count('YES') <= MAX_RANDOM_YES
    arm = lambda a, f=lambda k: True: [c for c in K if a in K[c]['arms'] and f(K[c])]
    high = lambda k: 'PAGE' in k['arms'] and shown(k['page_p']) >= HIGH
    rest = lambda k: 'PAGE' in k['arms'] and shown(k['page_p']) < HIGH
    res = {'random_yes': rnd.count('YES'), 'random_n': len(rnd), 'valid': valid,
           'precision_at_10': {a: share(V, arm(a)) for a in ARMS},
           'PAGE_minus_RERANK': boot(K, V, lambda k: 'PAGE' in k['arms'], lambda k: 'RERANK' in k['arms'], random.Random(SEED + 2)),
           'label': {'high': share(V, [c for c in K if high(K[c])]), 'rest': share(V, [c for c in K if rest(K[c])]),
                     'high_minus_rest': boot(K, V, high, rest, random.Random(SEED + 3))}}
    p = res['precision_at_10']['PAGE']['yes_share']; d = res['PAGE_minus_RERANK']; L = res['label']
    no = 'NOT VALID (random controls)'
    res['reading_page'] = (no if not valid else 'in the predicted range' if PAGE_RANGE[0] <= p <= PAGE_RANGE[1] else
                           'below the predicted range' if p < PAGE_RANGE[0] else 'above the predicted range')
    res['reading_compare'] = (no if not valid else 'PAGE better' if d['ci95'][0] > 0 else
                              'RERANK better' if d['ci95'][1] < 0 else 'no difference shown')
    res['reading_label'] = (no if not valid else 'label adopted' if L['high']['wilson95'] and L['high']['wilson95'][0] >= LABEL_MIN
                            and L['high_minus_rest']['ci95'][0] > 0 else 'label not adopted')
    # descriptive, read nothing from these
    res['by_type'] = {t: {a: share(V, arm(a, lambda k: k['type'] == t)) for a in ARMS} for t in ('privacy', 'terms')}
    res['by_rank'] = {a: {'1-5': share(V, [c for c in arm(a) if K[c]['arms'][a] <= 5]),
                          '6-10': share(V, [c for c in arm(a) if K[c]['arms'][a] > 5])} for a in ARMS}
    res['by_known_positives'] = {g: {a: share(V, arm(a, f)) for a in ARMS} for g, f in
                                 (('0-4', lambda k: k['known_positives'] < 5), ('5 or more', lambda k: k['known_positives'] >= 5))}
    res['by_doc'] = {doc: {a: share(V, arm(a, lambda k: k['doc'] == doc)) for a in ARMS} for doc in sorted({k['doc'] for k in K.values()})}
    res['by_folder'] = {x: {a: share(V, arm(a, lambda k: k['folder'] == x)) for a in ARMS} for x in FOLDERS}
    res['verdict_counts'] = dict(collections.Counter(V[c]['verdict'] for c in K))
    with open(RESULT, 'w', encoding='utf-8') as f: json.dump(res, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ('random_yes', 'random_n', 'valid', 'precision_at_10', 'PAGE_minus_RERANK', 'label',
                                          'reading_page', 'reading_compare', 'reading_label')}, indent=1))


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'kev': kev(*sys.argv[2:3])
    else: {'prep': prep, 'rerank': rerank, 'cards': cards, 'score': score}[c]()
