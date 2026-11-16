"""Keeps the missing-points page on the current text. Each of the page's documents was scored on the archive as it stood
when its run prepared it; when Open Terms Archive records a new version, the page's passages may be gone. This step
re-scores the changed documents through the cascade of the remaining-documents run (stale/RESULT_missing_wide.md): the
reranker on every passage (a passage whose text was already scored is reused, not re-run), then Kev on the reranker's
top 3 passages per case (Kev's cache serves questions already asked). A build step, not a test: nothing here is rated.

check <pga-versions>   -> stale/out/missing_watch_docs.json: the page documents whose text at the archive's HEAD differs
                          from the text they were scored on (same cases; passages cut as in stale/relocate.py)
rerank                 (dedupe-research venv, offline) -> stale/out/missing_watch_rerank.json
kev [server]           -> stale/out/missing_watch_kev.json
A document whose passages change again is re-scored on the next run (each output records a hash of its passages).
"""
import hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale import missing, missing2, missing_wide, missing_rest
from stale.missing import save
from stale.triage import TEMPLATE

DOCS = os.path.join(OUT, 'missing_watch_docs.json')
F = {a: os.path.join(OUT, f'missing_watch_{a.lower()}.json') for a in ('KEV', 'RERANK')}
# (documents file, its reranker scores, whether its suggestions were rated)
SOURCES = ((missing.DOCS, 'missing_rerank.json', True), (missing2.DOCS, 'missing2_rerank.json', True),
           (missing_wide.DOCS, 'missing_wide_rerank.json', False), (missing_rest.DOCS, 'missing_rest_rerank.json', False))
NOFILL = missing_wide.NOFILL


def load(p): return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def phash(pieces): return hashlib.sha256('\x00'.join(pieces).encode('utf-8')).hexdigest()[:16]


def current_pieces(arch, doc):
    from policywatch import archive
    from policywatch.diffing import paras
    from policywatch.watch import pieces
    from stale.relocate import PIECE
    return [p for p in pieces('\n\n'.join(paras(archive.git(arch, 'show', f'HEAD:{doc}'))), PIECE) if p.strip()]


def check(arch):
    from policywatch import archive
    head = archive.git(arch, 'rev-parse', 'HEAD').strip(); out = []
    for path, rr, rated in SOURCES:
        for d in load(path).get('docs', []):
            P = current_pieces(arch, d['doc'])
            if not P or P == d['pieces']: continue
            changed = archive.git(arch, 'log', '-1', '--format=%cI', '--', d['doc']).strip()
            out.append({**{k: d[k] for k in ('doc', 'type', 'positives', 'excluded', 'negatives', 'cases')}, 'pieces': P,
                        'hash': phash(P), 'old_pieces': d['pieces'], 'old_rerank': rr, 'rated': rated,
                        'scored_in': os.path.basename(path), 'changed': changed})
            old = set(d['pieces'])
            print(f'{d["doc"]}: changed {changed}; {len(d["pieces"])} -> {len(P)} passages, {sum(p not in old for p in P)} new')
    with open(DOCS, 'w', encoding='utf-8') as f: json.dump({'head': head, 'checked': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'docs': out}, f, ensure_ascii=False)
    print(len(out), 'changed documents at', head[:8])


def rerank(model=None):
    if model is None:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    out = load(F['RERANK']); hs = out.setdefault('_hash', {}); timing = out.setdefault('_timing', {})
    for d in load(DOCS).get('docs', []):
        if hs.get(d['doc']) == d['hash']: continue
        known = dict(zip(d['old_pieces'], load(os.path.join(OUT, d['old_rerank'])).get(d['doc'], [])))
        s0 = time.time(); rows = []; new = 0
        for piece in d['pieces']:
            k = known.get(piece)
            if k is not None and all(c in k for c in d['cases']): rows.append({c: k[c] for c in d['cases']}); continue
            sc = model.predict([(c, piece) for c in d['cases']], batch_size=16); new += 1
            rows.append({c: round(float(x), 5) for c, x in zip(d['cases'], sc)})
        out[d['doc']] = rows; hs[d['doc']] = d['hash']
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'new_pieces': new, 'pieces': len(d['pieces'])}
        save(F['RERANK'], out); print(d['doc'], timing[d['doc']], flush=True)
    print('rerank done')


def kev(server='http://127.0.0.1:9995', scorer=None):
    if scorer is None:
        from policywatch.scorer import Server, Cache, Scorer
        scorer = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
        assert scorer.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {scorer.server.served}, not Kev-4B Q8'
    from policywatch.scorer import qid
    RR = load(F['RERANK']); out = load(F['KEV']); hs = out.setdefault('_hash', {}); timing = out.setdefault('_timing', {})
    for d in load(DOCS).get('docs', []):
        if hs.get(d['doc']) == d['hash']: continue
        assert RR.get('_hash', {}).get(d['doc']) == d['hash'], f'{d["doc"]}: reranker scores are not on the current text'
        need = {}
        for c in d['cases']:
            for i in missing2.shortlist(RR[d['doc']], c): need.setdefault(i, []).append(c)
        rows = [{c: NOFILL for c in d['cases']} for _ in d['pieces']]; a0, h0, s0 = scorer.asked, scorer.hits, time.time()
        for i in sorted(need):
            qs = [TEMPLATE.format(c) for c in need[i]]; ps = scorer.score(d['pieces'][i], qs)
            for c, q in zip(need[i], qs): rows[i][c] = ps[qid(q)]
        out[d['doc']] = rows; hs[d['doc']] = d['hash']
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'cells': sum(map(len, need.values())),
                            'asked_cells': scorer.asked - a0, 'cached_cells': scorer.hits - h0}
        save(F['KEV'], out); print(d['doc'], timing[d['doc']], flush=True)
    print('kev done')


def current(arm):
    """{doc: (doc dict, rows)} for the documents re-scored on their current text with this arm's scores, if any."""
    S = load(F[arm]) if arm in F else {}
    return {d['doc']: (d, S[d['doc']]) for d in load(DOCS).get('docs', [])
            if d['doc'] in S and S.get('_hash', {}).get(d['doc']) == d['hash']}


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'check': check(sys.argv[2])
    elif c == 'kev': kev(*sys.argv[2:3])
    else: {'rerank': rerank}[c]()
