"""Exploratory, written after the remaining-documents check (stale/RESULT_missing_wide.md) and before running: on the
one document where the cascade lost to the reranker (Facebook's privacy policy, 146 passages; cascade AUROC .699,
reranker .763), does Kev on every passage do better than Kev on the reranker's top 3 passages per case?

Question fixed before the run: AUROC of the document's approved cases against the cases the service has no point for,
KEV_FULL (Kev on every passage) next to CASCADE_KEV and RERANK from the run, plus how many approved cases had their
best KEV_FULL passage outside the shortlist. One document, so no interval is read as a result: this says whether the
shortlist explains that document, not whether it does in general.

Usage  py -m stale.missing_wide_full ["Facebook/Privacy Policy.md"] [server]
-> stale/out/missing_wide_full.json (scores per document; reruns are served from the cache)
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import best, auroc, save
from stale.triage import TEMPLATE
from stale import missing2, missing_wide

DEST = os.path.join(OUT, 'missing_wide_full.json')


def run(doc='Facebook/Privacy Policy.md', server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    d = {x['doc']: x for x in json.load(open(missing_wide.DOCS, encoding='utf-8'))['docs']}[doc]
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
    out = missing_wide.load(DEST); qs = [TEMPLATE.format(c) for c in d['cases']]; rows = []; a0, h0, t0 = S.asked, S.hits, time.time()
    for n, piece in enumerate(d['pieces'], 1):
        ps = S.score(piece, qs); rows.append({c: ps[qid(q)] for c, q in zip(d['cases'], qs)})
        if n % 10 == 0: print(f'[{n}/{len(d["pieces"])} {time.time() - t0:.0f}s]', flush=True)
    RR = missing_wide.load(missing_wide.F['RERANK'])[doc]; CK = missing_wide.load(missing_wide.F['KEV'])[doc]
    sc = {'KEV_FULL': rows, 'CASCADE_KEV': CK, 'RERANK': RR}
    au = {a: round(auroc([best(r, c)[0] for c in d['positives']], [best(r, c)[0] for c in d['negatives']]), 3) for a, r in sc.items()}
    off = sum(best(rows, c)[1] not in missing2.shortlist(RR, c) for c in d['positives'])
    out[doc] = {'auroc': au, 'positives': len(d['positives']), 'negatives': len(d['negatives']),
                'positives_best_full_passage_off_shortlist': off,
                'timing': {'seconds': round(time.time() - t0, 1), 'asked_cells': S.asked - a0, 'cached_cells': S.hits - h0},
                'rows': rows}
    save(DEST, out); print(json.dumps({k: v for k, v in out[doc].items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    run(*sys.argv[1:3])
