"""Relocation on held-out services (stale/PREREG_relocate2.md, part B): the relocation test's arms on ToS;DR points of
45 services outside the 22 pga-versions platforms, on ToS;DR's own stored copy of each document (stale/heldout.py).

Arms are those of stale/relocate.py and stale/relocate2.py with the same settings: KEV (r20 wrapper), KEV_SHORT, QWEN,
RERANK, BM25 and BGE (case title). Gold: the pieces holding >= .3 of the curator's quote's 6-grams (1-3 pieces).
The bootstrap clusters on services (a service's documents and points are not independent).

Usage  py -m stale.relocate_b kev [port]          -> stale/out/heldout_kev.json
       py -m stale.relocate_b kevshort [port]     -> stale/out/heldout_kevshort.json
       py -m stale.relocate_b qwen [port]         -> stale/out/heldout_qwen.json
       <venv python> -m stale.relocate_b base     -> stale/out/heldout_base.json (RERANK, BGE, BM25)
       py -m stale.relocate_b eval                -> stale/out/heldout_result.json
"""
import collections, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.relocate import psha, hit, bm25, KS, BGE_INSTR
from stale.relocate2 import qwen_ask, boot, reading, load, save

DOCS = os.path.join(OUT, 'heldout_docs.json')
F = {a: os.path.join(OUT, f'heldout_{a}.json') for a in ('kev', 'kevshort', 'qwen', 'base')}


def docs():
    return json.load(open(DOCS, encoding='utf-8'))['docs']


def kev(port='9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    S = Scorer(Server(f'http://127.0.0.1:{port}'), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', 'port does not serve Kev-4B Q8'
    out = load(F['kev']); D = docs(); t0 = time.time()
    for k, d in enumerate(D, 1):
        if d['doc'] in out: continue
        t1 = time.time(); rows = []
        for piece in d['pieces']:
            ps = S.score(piece, d['questions']); rows.append({q: ps[qid(q)] for q in d['questions']})
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': rows, 'sec': round(time.time() - t1, 1)}
        save(F['kev'], out)
        print(f'[{k}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}: {len(d["pieces"])} x {len(d["questions"])}', flush=True)
    print('asked', S.asked, 'cache hits', S.hits)


def kevshort(port='9995'):
    from bench.short_layout import post
    from policywatch.scorer import Server
    assert Server(f'http://127.0.0.1:{port}').served == 'Kev-4B-Q8_0.gguf', 'port does not serve Kev-4B Q8'
    out = load(F['kevshort']); D = docs(); t0 = time.time()
    for k, d in enumerate(D, 1):
        if d['doc'] in out: continue
        rows = []; sec = 0.0
        for piece in d['pieces']:
            ps, _, s = post(port, piece, d['questions']); sec += s
            rows.append({q: ps[f'q{i:02d}'] for i, q in enumerate(d['questions'])})
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': rows, 'sec': round(sec, 1)}
        save(F['kevshort'], out)
        print(f'[{k}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}', flush=True)


def qwen(port='9996'):
    out = load(F['qwen']); D = docs(); t0 = time.time()
    for k, d in enumerate(D, 1):
        if d['doc'] in out: continue
        t1 = time.time(); rows = []; miss = 0
        for piece in d['pieces']:
            row = {}
            for q in d['questions']:
                r = qwen_ask(port, piece, q); miss += not (r['yes'] or r['no']); row[q] = r
            rows.append(row)
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': rows, 'sec': round(time.time() - t1, 1), 'no_yes_no': miss}
        save(F['qwen'], out)
        print(f'[{k}/{len(D)} {time.time() - t0:.0f}s] {d["doc"]}: no yes/no token {miss}', flush=True)


def base():
    os.environ.setdefault('HF_HUB_OFFLINE', '1'); os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
    import torch
    from sentence_transformers import SentenceTransformer, CrossEncoder
    emb = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cpu')
    rr = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    out = {'BGE': {}, 'BM25': {}, 'RERANK': {}, 'pieces_sha': {}, 'rerank_sec': 0.0, 'rerank_truncated': 0}
    for d in docs():
        out['pieces_sha'][d['doc']] = psha(d['pieces']); n = len(d['pieces'])
        E = emb.encode(d['pieces'], normalize_embeddings=True, batch_size=32)
        Qv = emb.encode([BGE_INSTR + c for c in d['cases']], normalize_embeddings=True); S = Qv @ E.T
        out['BGE'][d['doc']] = {q: [round(float(x), 5) for x in S[k]] for k, q in enumerate(d['questions'])}
        out['BM25'][d['doc']] = {q: [round(x, 5) for x in bm25(c, d['pieces'])] for q, c in zip(d['questions'], d['cases'])}
        pairs = [(c, p) for c in d['cases'] for p in d['pieces']]
        out['rerank_truncated'] += sum(1 for a, b in pairs if len(rr.tokenizer(a, b)['input_ids']) > 1024)
        t1 = time.time(); s = rr.predict(pairs, batch_size=16, activation_fn=torch.nn.Identity(), show_progress_bar=False)
        out['rerank_sec'] += time.time() - t1
        out['RERANK'][d['doc']] = {q: [round(float(x), 5) for x in s[k * n:(k + 1) * n]] for k, q in enumerate(d['questions'])}
        print(d['doc'], flush=True)
    save(F['base'], out)


def evaluate():
    D = docs(); K, KS_, Q, B = (json.load(open(F[a], encoding='utf-8')) for a in ('kev', 'kevshort', 'qwen', 'base'))
    for name, A in (('KEV', K), ('KEV_SHORT', KS_), ('QWEN', Q)):
        bad = [d['doc'] for d in D if d['doc'] not in A or A[d['doc']]['pieces_sha'] != psha(d['pieces'])]; assert not bad, (name, bad[:3])
    assert all(B['pieces_sha'][d['doc']] == psha(d['pieces']) for d in D)
    arm = {'KEV': lambda d, q: [s[q] for s in K[d]['scores']], 'KEV_SHORT': lambda d, q: [s[q] for s in KS_[d]['scores']],
           'QWEN': lambda d, q: [s[q]['lo'] for s in Q[d]['scores']], 'RERANK': lambda d, q: B['RERANK'][d][q],
           'BM25': lambda d, q: B['BM25'][d][q], 'BGE': lambda d, q: B['BGE'][d][q]}
    per = []
    for d in D:
        n = len(d['pieces'])
        for it in d['items']:
            row = {'point': it['point'], 'doc': d['service'], 'n_pieces': n}   # 'doc' holds the service: the bootstrap's cluster
            for a, f in arm.items():
                hk, rr = hit(f(d['doc'], it['question']), it['gold']); row[a] = {'hit': hk, 'rr': rr}
            g = len(it['gold']); row['RANDOM'] = {'hit': {k: 1 - math.comb(n - g, k) / math.comb(n, k) if n - g >= k else 1.0 for k in KS}, 'rr': 0}
            per.append(row)
    names = list(arm) + ['RANDOM']; N = len(per)
    res = {'points': N, 'services': len({r['doc'] for r in per}), 'documents': len(D),
           'hit_at': {a: {k: round(sum(r[a]['hit'][k] for r in per) / N, 3) for k in KS} for a in names},
           'mrr': {a: round(sum(r[a]['rr'] for r in per) / N, 3) for a in names if a != 'RANDOM'}}
    d_ = lambda a, b: (lambda r: r[a]['hit'][1] - r[b]['hit'][1])
    for a, b in (('KEV', 'BM25'), ('KEV', 'BGE'), ('KEV', 'QWEN'), ('KEV', 'RERANK'), ('KEV_SHORT', 'KEV')):
        res[f'{a}_minus_{b}'] = boot(per, d_(a, b))
    cq = [c for d in D for row in Q[d['doc']]['scores'] for c in row.values()]
    res['qwen_validity'] = {'cells': len(cq), 'no_yes_no_share': round(sum(not (c['yes'] or c['no']) for c in cq) / len(cq), 4),
                            'median_mass': round(sorted(c['mass'] for c in cq)[len(cq) // 2], 4),
                            'top_tokens': dict(collections.Counter(c['top'].strip().lower() for c in cq).most_common(5))}
    qwen_ok = res['qwen_validity']['no_yes_no_share'] <= .01 and res['qwen_validity']['median_mass'] >= .5
    rep = res['KEV_minus_BM25']['raw'][0] > 0 and res['KEV_minus_BGE']['raw'][0] > 0
    res['reading'] = {
        'B0_replication': 'REPLICATED' if rep else 'NOT REPLICATED',
        'B1_base_family': 'INVALID (QWEN validity gate failed)' if not qwen_ok else reading(res['KEV_minus_QWEN']['raw'], 'DECISION MODEL BETTER THAN ITS BASE FAMILY', 'BASE LLM BETTER', 'NO DIFFERENCE SHOWN'),
        'B2_reranker': reading(res['KEV_minus_RERANK']['raw'], 'DECISION MODEL BETTER THAN THE RERANKER', 'RERANKER BETTER', 'NO DIFFERENCE SHOWN'),
        'B3_short_layout': 'KEV_SHORT HOLDS' if res['KEV_SHORT_minus_KEV']['raw'][0] >= -.05 else 'KEV_SHORT LOSES'}
    cells = sum(len(d['pieces']) * len(d['questions']) for d in D)
    res['cost_sec_per_cell'] = {'KEV': round(sum(K[d['doc']]['sec'] for d in D) / cells, 3), 'KEV_SHORT': round(sum(KS_[d['doc']]['sec'] for d in D) / cells, 3),
                                'QWEN': round(sum(Q[d['doc']]['sec'] for d in D) / cells, 3), 'RERANK': round(B['rerank_sec'] / cells, 3)}
    res['cells'] = cells; res['rerank_truncated'] = B['rerank_truncated']
    # memorisation check (exploratory): points created on ToS;DR on/after 2025-07-01
    created = {}
    for f in os.listdir(os.path.join(HERE, 'data', 'heldout')):
        for p in json.load(open(os.path.join(HERE, 'data', 'heldout', f), encoding='utf-8'))['points']: created[p['point']] = p.get('created_at') or ''
    late = [r for r in per if created.get(r['point'], '') >= '2025-07-01']
    res['created_after_2025_07'] = {'n': len(late), **({a: round(sum(r[a]['hit'][1] for r in late) / len(late), 3) for a in names} if late else {})}
    with open(os.path.join(OUT, 'heldout_result.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': per}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    c = sys.argv[1]
    {'kev': kev, 'kevshort': kevshort, 'qwen': qwen, 'base': base, 'eval': evaluate}[c](*sys.argv[2:])
