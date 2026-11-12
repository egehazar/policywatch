"""Re-find the evidence for approved ToS;DR points in the CURRENT version of each document (stale/PREREG_relocate.md).

Each document's current text (the archive's HEAD) is cut into pieces of at most PIECE characters at paragraph
boundaries. Every arm ranks the pieces for each point's case question:
  KEV    p(yes) from Kev-4B on each piece, all of the document's case questions in one request per piece
  BGE    cosine of bge-small-en-v1.5 (query with its retrieval instruction) between the case title and each piece
  BM25   the case title's words against the document's pieces (k1 1.2, b .75, document-local statistics)
Gold (points whose quote is still present): the pieces holding >= .3 of the quote's word 6-grams; the curator's quote
marks one place the case is stated, so hit rates are lower bounds for every arm alike. Ties count in expectation.

Usage  py -m stale.relocate prep <pga-versions>   -> stale/out/reloc_docs.json (no model)
       py -m stale.relocate kev [server]          -> stale/out/reloc_kev.json
       py -m stale.relocate base                  -> stale/out/reloc_base.json (BGE, BM25)
       py -m stale.relocate eval                  -> stale/out/reloc_result.json
"""
import json, math, os, random, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from policywatch import archive
from policywatch.diffing import paras
from policywatch.watch import pieces
from stale.match import words, grams, coverage
from stale.triage import TEMPLATE

PIECE = 1500; GOLD_MIN = .3; GOLD_MAX = 3; KS = (1, 3, 5); SEED = 20261112
DOCS = os.path.join(OUT, 'reloc_docs.json')
BGE_INSTR = 'Represent this sentence for searching relevant passages: '
STOP = set('a an the of to and or in on for by with is are be this that your you we our us it its as at from any may can will not no'.split())


def psha(P):
    import hashlib
    return hashlib.sha256('\x00'.join(P).encode('utf-8')).hexdigest()[:16]


def qcov(quote, text):
    qw = words(quote, quote=True); ws = words(text)
    return coverage(qw, grams(qw), ' ' + ' '.join(ws) + ' ', grams(ws))


def prep(arch):
    rows = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    homes = sorted({r['doc'] for r in rows if r.get('doc')})
    docs = []
    for d in homes:
        text = archive.git(arch, 'show', f'HEAD:{d}')
        P = [p for p in pieces('\n\n'.join(paras(text)), PIECE) if p.strip()]
        pts = [r for r in rows if r.get('doc') == d]
        cases = sorted({r['case_title'] for r in pts})
        items = []
        for r in pts:
            it = {'point': r['point'], 'platform': r['platform'], 'case_title': r['case_title'], 'status': r['status'],
                  'question': TEMPLATE.format(r['case_title'])}
            if r['status'] == 'present' and len(words(r['quote'], quote=True)) >= 6:
                # quotes under 6 words (often headings) are not gold: they match many pieces (review 11-12)
                cov = [qcov(r['quote'], p) for p in P]
                it['gold'] = [i for i, c in enumerate(cov) if c >= GOLD_MIN]
            items.append(it)
        docs.append({'doc': d, 'chars': sum(len(p) for p in P), 'pieces': P, 'questions': [TEMPLATE.format(c) for c in cases],
                     'cases': cases, 'items': items})
    docs.sort(key=lambda x: x['doc'])
    # the scored sample: a fixed random order of eligible points (1-3 gold pieces; a quote matching more pieces is
    # boilerplate repeated across the document). A run scores the first N; N is set by CPU cost alone.
    elig = sorted(it['point'] for d in docs for it in d['items'] if it.get('gold') and len(it['gold']) <= GOLD_MAX)
    random.Random(SEED).shuffle(elig)
    with open(DOCS, 'w', encoding='utf-8') as f: json.dump({'order': elig, 'docs': docs}, f, ensure_ascii=False)
    print(len(elig), 'eligible points in the fixed order; first 10:', elig[:10])
    n_pres = sum(1 for d in docs for it in d['items'] if it['status'] == 'present')
    n_gold = sum(1 for d in docs for it in d['items'] if it.get('gold'))
    print(len(docs), 'documents,', sum(len(d['pieces']) for d in docs), 'pieces,', sum(d['chars'] for d in docs), 'chars;',
          sum(len(d['questions']) for d in docs), 'document-questions;', n_pres, 'present points,', n_gold, 'with a gold piece;',
          sum(1 for d in docs for it in d['items'] if it['status'] in ('gone', 'partly')), 'gone/partly points')


def sample(n):
    """The first n points of the fixed order -> {doc: sorted questions needed}, {point ids}."""
    D = json.load(open(DOCS, encoding='utf-8')); chosen = set(D['order'][:int(n)])
    need = {}
    for d in D['docs']:
        qs = sorted({it['question'] for it in d['items'] if it['point'] in chosen})
        if qs: need[d['doc']] = qs
    return D, need, chosen


def cells(n):
    D, need, _ = sample(n); P = {d['doc']: len(d['pieces']) for d in D['docs']}
    return sum(P[d] * len(q) for d, q in need.items())


def kev(n, server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    D, need, _ = sample(n); docs = sorted((d for d in D['docs'] if d['doc'] in need), key=lambda d: len(d['pieces']) * len(need[d['doc']]))
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite'))); out = {}; t0 = time.time()
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    print(f'N={n}: {len(docs)} documents, {cells(n)} piece-question cells', flush=True)
    for n_, d in enumerate(docs, 1):
        qs = need[d['doc']]
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': []}
        for piece in d['pieces']:
            ps = S.score(piece, qs)
            out[d['doc']]['scores'].append({q: ps[qid(q)] for q in qs})
        with open(os.path.join(OUT, 'reloc_kev.json'), 'w', encoding='utf-8') as f: json.dump(out, f)
        print(f'[{n_}/{len(docs)} {time.time() - t0:.0f}s] {d["doc"]}: {len(d["pieces"])} pieces x {len(qs)} questions', flush=True)
    print('asked', S.asked, 'cache hits', S.hits)


def bm25(query, P, k1=1.2, b=.75):
    toks = [words(p) for p in P]; N = len(P); avg = sum(map(len, toks)) / max(1, N)
    df = {}
    for t in toks:
        for w in set(t): df[w] = df.get(w, 0) + 1
    q = [w for w in words(query) if w not in STOP]
    out = []
    for t in toks:
        tf = {}
        for w in t: tf[w] = tf.get(w, 0) + 1
        s = 0.0
        for w in q:
            if w in tf:
                idf = math.log(1 + (N - df[w] + .5) / (df[w] + .5))
                s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        out.append(s)
    return out


def base():
    os.environ.setdefault('HF_HUB_OFFLINE', '1'); os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cpu')
    docs = json.load(open(DOCS, encoding='utf-8'))['docs']; out = {'BGE': {}, 'BM25': {}, 'pieces_sha': {}}
    for d in docs:
        out['pieces_sha'][d['doc']] = psha(d['pieces'])
        E = m.encode(d['pieces'], normalize_embeddings=True, batch_size=32)
        Qv = m.encode([BGE_INSTR + c for c in d['cases']], normalize_embeddings=True)
        S = Qv @ E.T
        out['BGE'][d['doc']] = {q: [round(float(x), 5) for x in S[k]] for k, q in enumerate(d['questions'])}
        out['BM25'][d['doc']] = {q: [round(x, 5) for x in bm25(c, d['pieces'])] for q, c in zip(d['questions'], d['cases'])}
    with open(os.path.join(OUT, 'reloc_base.json'), 'w', encoding='utf-8') as f: json.dump(out, f)
    print('base arms written for', len(docs), 'documents')


def hit(scores, gold, k=None):
    """Expected hit@k and reciprocal rank of the best-ranked gold piece, ties broken uniformly at random.
    hi non-gold pieces score above the best gold score s; t non-gold and m gold pieces tie at s. X = the position of
    the first gold piece within the tied group: P(X > x) = C(t, x) / C(t+m, x). (Review 11-12: the first version
    treated m tied gold pieces as one.)"""
    from math import comb
    gold = set(gold); s = max(scores[g] for g in gold)
    hi = sum(1 for i, x in enumerate(scores) if x > s and i not in gold)
    t = sum(1 for i, x in enumerate(scores) if x == s and i not in gold)
    m = sum(1 for g in gold if scores[g] == s)
    gt = lambda x: comb(t, x) / comb(t + m, x) if x <= t else 0.0          # P(X > x)
    hk = {k: (0.0 if k - hi <= 0 else 1 - gt(k - hi)) for k in KS}
    rr = sum((gt(x - 1) - gt(x)) / (hi + x) for x in range(1, t + 2))
    return hk, rr


def evaluate(n):
    D, need, chosen = sample(n); docs = [d for d in D['docs'] if d['doc'] in need]
    K = json.load(open(os.path.join(OUT, 'reloc_kev.json'), encoding='utf-8'))
    B = json.load(open(os.path.join(OUT, 'reloc_base.json'), encoding='utf-8'))
    # every arm must cover every document, on exactly the pieces in reloc_docs.json (review 11-12)
    missing = [d['doc'] for d in docs if d['doc'] not in K or d['doc'] not in B['BGE']]
    assert not missing, f'arms missing {len(missing)} documents, e.g. {missing[:3]}'
    short = [d['doc'] for d in docs if not set(need[d['doc']]) <= set(K[d['doc']]['scores'][0])]
    assert not short, f'Kev was run for a smaller N on {short[:3]}'
    bad = [d['doc'] for d in docs if K[d['doc']]['pieces_sha'] != psha(d['pieces']) or B['pieces_sha'][d['doc']] != psha(d['pieces'])]
    assert not bad, f'pieces changed since scoring: {bad[:3]}'
    arm_scores = {'KEV': lambda d, q: [s[q] for s in K[d]['scores']], 'BGE': lambda d, q: B['BGE'][d][q],
                  'BM25': lambda d, q: B['BM25'][d][q]}
    per = []          # one row per gold point
    for d in docs:
        n = len(d['pieces'])
        for it in d['items']:
            if it['point'] not in chosen: continue
            row = {'point': it['point'], 'doc': d['doc'], 'n_pieces': n, 'n_gold': len(it['gold'])}
            for a, f in arm_scores.items():
                hk, rr = hit(f(d['doc'], it['question']), it['gold'], 1); row[a] = {'hit': hk, 'rr': rr}
            g = len(it['gold']); row['RANDOM'] = {'hit': {k: min(1.0, 1 - math.comb(n - g, k) / math.comb(n, k)) if n - g >= k else 1.0 for k in KS},
                                                 'rr': None}
            per.append(row)
    arms = ['KEV', 'BGE', 'BM25', 'RANDOM']
    assert len(per) == len(chosen), (len(per), len(chosen))
    res = {'N': int(n), 'points': len(per), 'documents': len({r['doc'] for r in per}),
           'hit_at': {a: {k: round(sum(r[a]['hit'][k] for r in per) / len(per), 3) for k in KS} for a in arms},
           'mrr': {a: round(sum(r[a]['rr'] for r in per) / len(per), 3) for a in arms if a != 'RANDOM'}}
    rng = random.Random(SEED); docs_ = sorted({r['doc'] for r in per}); by = {d: [r for r in per if r['doc'] == d] for d in docs_}
    for other in ('BGE', 'BM25'):
        diffs = []
        for _ in range(2000):     # cluster bootstrap over documents (points within a document are not independent)
            smp = [r for d in (rng.choice(docs_) for _ in docs_) for r in by[d]]
            diffs.append(sum(r['KEV']['hit'][1] - r[other]['hit'][1] for r in smp) / len(smp))
        diffs.sort()
        res[f'KEV_minus_{other}_hit1'] = {'point': round(sum(r['KEV']['hit'][1] - r[other]['hit'][1] for r in per) / len(per), 3),
                                          'ci95': [round(diffs[50], 3), round(diffs[1949], 3)]}
    with open(os.path.join(OUT, 'reloc_result.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': per}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'prep': prep(sys.argv[2])
    elif c == 'kev': kev(*sys.argv[2:])
    elif c == 'base': base()
    elif c == 'cells': print({n: cells(n) for n in sys.argv[2:]})
    else: evaluate(sys.argv[2])
