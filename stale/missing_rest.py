"""Missing points on the last documents of the 20 platforms: the "Privacy Policy" and "Terms of Service" files in the
archive that no earlier run covered, because the earlier document lists (stale/out/reloc_docs.json) hold only documents
with a ToS;DR point matched to them (the fact-check of stale/RESULT_missing_wide.md found 6). A build through the same
cascade (the reranker on every passage, Kev on its top 3 per case); with no matched point there are no known positives,
so nothing here is measured or rated.

prep <pga-versions> | rerank (dedupe-research venv, offline) | kev [server]
-> stale/out/missing_rest_docs.json, missing_rest_rerank.json, missing_rest_kev.json
"""
import collections, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import typ, all_points, save, MIN_POINTS
from stale.triage import TEMPLATE
from stale import missing, missing2, missing_wide

DOCS = os.path.join(OUT, 'missing_rest_docs.json')
F = {a: os.path.join(OUT, f'missing_rest_{a.lower()}.json') for a in ('KEV', 'RERANK')}
NOFILL = missing_wide.NOFILL


def load(p): return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def platforms():
    """The 20 platforms: those in stale/data with at least one approved point."""
    out = []
    for f in sorted(os.listdir(os.path.join(HERE, 'data'))):
        if f.endswith('.json') and missing_wide.approved(f[:-5]): out.append(f[:-5])
    return out


def prep(arch):
    from stale.missing_watch import current_pieces
    done = {d['doc'] for p in (missing.DOCS, missing2.DOCS, missing_wide.DOCS) for d in load(p).get('docs', [])}
    freq = collections.defaultdict(collections.Counter)
    for r in all_points(): freq[typ(r.get('tosdr_document'))][r['case_title']] += 1
    out = []
    for plat in platforms():
        for base in missing_wide.NAMES:
            name = f'{plat}/{base}'
            if name in done or not os.path.exists(os.path.join(arch, plat, base)): continue
            t = typ(base); P = current_pieces(arch, name)
            C = sorted(c for c, n in freq[t].items() if n >= MIN_POINTS)
            A = missing_wide.approved(plat); E = sorted(c for c in C if c.strip() in A); N = [c for c in C if c not in E]
            out.append({'doc': name, 'type': t, 'pieces': P, 'positives': [], 'excluded': E, 'negatives': N, 'cases': N})
            print(f'{name} ({t}): {len(P)} pieces, {len(E)} excluded, {len(N)} asked')
    with open(DOCS, 'w', encoding='utf-8') as f: json.dump({'docs': out}, f, ensure_ascii=False)
    print(len(out), 'documents;', sum(len(x['pieces']) * len(x['cases']) for x in out), 'reranker cells;',
          sum(3 * len(x['cases']) for x in out), 'Kev cells at most')


def rerank():
    from sentence_transformers import CrossEncoder
    m = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    out = load(F['RERANK'])
    for d in load(DOCS)['docs']:
        if d['doc'] in out: continue
        s0 = time.time(); rows = []
        for piece in d['pieces']:
            sc = m.predict([(c, piece) for c in d['cases']], batch_size=16)
            rows.append({c: round(float(x), 5) for c, x in zip(d['cases'], sc)})
        out[d['doc']] = rows; out.setdefault('_timing', {})[d['doc']] = round(time.time() - s0, 1); save(F['RERANK'], out)
        print(d['doc'], out['_timing'][d['doc']], flush=True)
    print('rerank done')


def kev(server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    RR = load(F['RERANK']); out = load(F['KEV']); timing = out.setdefault('_timing', {})
    for d in load(DOCS)['docs']:
        if d['doc'] in out: continue
        need = collections.defaultdict(list)
        for c in d['cases']:
            for i in missing2.shortlist(RR[d['doc']], c): need[i].append(c)
        rows = [{c: NOFILL for c in d['cases']} for _ in d['pieces']]; a0, h0, s0 = S.asked, S.hits, time.time()
        for i in sorted(need):
            qs = [TEMPLATE.format(c) for c in need[i]]; ps = S.score(d['pieces'][i], qs)
            for c, q in zip(need[i], qs): rows[i][c] = ps[qid(q)]
        out[d['doc']] = rows
        timing[d['doc']] = {'seconds': round(time.time() - s0, 1), 'pieces': len(need), 'cells': sum(map(len, need.values())),
                            'asked_cells': S.asked - a0, 'cached_cells': S.hits - h0}
        save(F['KEV'], out); print(d['doc'], timing[d['doc']], flush=True)
    print('kev done')


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'prep': prep(sys.argv[2])
    elif c == 'kev': kev(*sys.argv[2:3])
    else: {'rerank': rerank}[c]()
