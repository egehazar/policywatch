"""The reranker-first cascade for the wider pages' suggestions: used only if part D's D1 reads CASCADE ADOPTED
(stale/PREREG_relocate_d.md). Otherwise stale/wide.py kev asks Kev about every piece.

rerank  <collection>         bge-reranker-v2-m3 (the revision and max_length of the relocation arms), case title vs
                             every piece of the current text of each document with a dropped point
                             -> stale/wide/<collection>/out/rerank_scores.json   (needs the sentence-transformers venv)
kev     <collection> [port]  Kev with the r20 wrapper, asked a piece's case questions only for the cases whose top 10
                             reranker pieces hold it (pieces tied with the 10th stay in), one request per piece; other
                             pieces rank last. Writes suggest_kev.jsonl in stale/suggest.py's format, then the proposed
                             quotes (stale/propose.py) and the page.
Usage  <venv python> -m stale.cascade rerank contrib;  py -m stale.cascade kev contrib 9995
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from stale.relocate import PIECE, psha
from stale.triage import TEMPLATE

TOPK = 10; TOP = 3


def adopted():
    p = os.path.join(HERE, 'out', 'contrib_result.json')
    return os.path.exists(p) and json.load(open(p, encoding='utf-8'))['result']['reading'].get('D1_cascade') == 'CASCADE ADOPTED'


def inputs(collection):
    from policywatch import archive
    from policywatch.diffing import paras
    from policywatch.watch import pieces
    from stale import wide
    R = wide.drops_of(collection); arch = wide.vdir(collection)
    docs = sorted({r['doc'] for r in R})
    P = {d: [p for p in pieces('\n\n'.join(paras(archive.git(arch, 'show', f'HEAD:{d}'))), PIECE) if p.strip()] for d in docs}
    cases = {d: sorted({r['case_title'] for r in R if r['doc'] == d}) for d in docs}
    head = archive.git(arch, 'rev-parse', 'HEAD').strip()
    return R, docs, P, cases, head, os.path.join(wide.WIDE, collection, 'out')


def rerank(collection):
    os.environ.setdefault('HF_HUB_OFFLINE', '1'); os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
    import torch
    from sentence_transformers import CrossEncoder
    R, docs, P, cases, head, out = inputs(collection)
    rr = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    res = {'archive_head': head, 'docs': {}}; t0 = time.time()
    for d in docs:
        pairs = [(c, p) for c in cases[d] for p in P[d]]; n = len(P[d])
        s = rr.predict(pairs, batch_size=16, activation_fn=torch.nn.Identity(), show_progress_bar=False)
        res['docs'][d] = {'pieces_sha': psha(P[d]), 'scores': {c: [round(float(x), 5) for x in s[k * n:(k + 1) * n]] for k, c in enumerate(cases[d])}}
        print(f'[{time.time() - t0:.0f}s] {d}: {n} pieces x {len(cases[d])} cases', flush=True)
    res['sec'] = round(time.time() - t0, 1)
    with open(os.path.join(out, 'rerank_scores.json'), 'w', encoding='utf-8') as f: json.dump(res, f)


def top_k(s, k=TOPK):
    cut = sorted(s, reverse=True)[min(k, len(s)) - 1]
    return {i for i, x in enumerate(s) if x >= cut}


def kev(collection, port='9995', cache=None):
    from policywatch.scorer import Server, Cache, Scorer, qid
    from stale import propose, wide
    R, docs, P, cases, head, out = inputs(collection)
    RR = json.load(open(os.path.join(out, 'rerank_scores.json'), encoding='utf-8'))
    assert RR['archive_head'] == head, 'the archive moved since the reranker ran'
    S = Scorer(Server(f'http://127.0.0.1:{port}'), Cache(cache or os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    scores, cells, full = {}, 0, 0; t0 = time.time()
    for n, d in enumerate(docs, 1):
        assert RR['docs'][d]['pieces_sha'] == psha(P[d])
        keep = {c: top_k(RR['docs'][d]['scores'][c]) for c in cases[d]}
        for c in cases[d]: scores[(d, c)] = [-1.0] * len(P[d])
        for i, piece in enumerate(P[d]):
            cs = [c for c in cases[d] if i in keep[c]]
            if not cs: continue
            qs = [TEMPLATE.format(c) for c in cs]; ps = S.score(piece, qs); cells += len(qs)
            for c, q in zip(cs, qs): scores[(d, c)][i] = ps[qid(q)]
        full += len(P[d]) * len(cases[d])
        print(f'[{n}/{len(docs)} {time.time() - t0:.0f}s] {d}', flush=True)
    with open(os.path.join(out, 'suggest_kev.jsonl'), 'w', encoding='utf-8') as f:
        for r in R:
            s = scores[(r['doc'], r['case_title'])]; order = sorted(range(len(s)), key=lambda i: -s[i])[:TOP]
            f.write(json.dumps({'point': r['point'], 'doc': r['doc'], 'archive_head': head, 'arm': 'kev', 'cascade': f'rerank top {TOPK}',
                                'n_pieces': len(P[r['doc']]), 'top': [{'piece': i, 'score': round(s[i], 4), 'text': P[r['doc']][i]} for i in order]},
                               ensure_ascii=False) + '\n')
    print(f'{len(R)} points, {len(docs)} documents: Kev asked {cells} of {full} piece-question cells ({cells / max(full, 1):.0%}); '
          f'asked {S.asked}, cache hits {S.hits}')
    propose.run(port, out, cache)
    wide.page(collection, 'kev')


if __name__ == '__main__':
    cmd, col = sys.argv[1], sys.argv[2]
    if cmd == 'rerank': rerank(col)
    elif cmd == 'kev': kev(col, *sys.argv[3:])
    elif cmd == 'adopted': print('CASCADE ADOPTED' if adopted() else 'not adopted'); sys.exit(0 if adopted() else 1)
    else: raise SystemExit(__doc__)
