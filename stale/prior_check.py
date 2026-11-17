"""Two checks on the missing-points AUROC results, added after the fact (2026-11-18, exploratory), prompted by an
adversarial review (a Claude Fable 5.2 subagent) and recomputed here.

1. A text-blind baseline, PRIOR: rank a document's candidate cases by how many approved points the case has on OTHER
   services' documents of the same type (privacy / terms). It never reads the document. If it ranks known positives
   above negatives about as well as an arm that reads the text, the AUROC measures curators' coverage habits.
2. Document-level intervals: the published intervals resample positives and negatives within each fixed document, so
   they speak only for these documents. Here the per-document differences are resampled instead (a t-interval and a
   bootstrap over documents).

py -m stale.prior_check   ->  stale/out/prior_check.json
"""
import collections, json, math, os, random, statistics as st
from stale import missing

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
TESTS = [('pilot', 'missing_docs.json', 'missing_measures.json', 'KEV', 0),
         ('larger test', 'missing2_docs.json', 'missing2_measures.json', 'KEV', 0),
         ('20 more documents (check fixed in advance)', 'missing_wide_docs.json', 'missing_wide_measures.json', 'CASCADE_KEV', 10)]
T975 = {3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
SEED, DRAWS = 20261118, 5000


def auroc(p, n):
    return sum(1 if a > b else .5 if a == b else 0 for a in p for b in n) / (len(p) * len(n))


def prior(rows, doc, typ):
    plat = doc.split('/', 1)[0]
    return collections.Counter(r['case_title'] for r in rows if missing.typ(r.get('tosdr_document')) == typ and r['platform'] != plat)


def intervals(x, rng):
    m = st.mean(x); s = st.stdev(x) / math.sqrt(len(x)); t = T975[len(x) - 1]
    b = sorted(st.mean(rng.choice(x) for _ in x) for _ in range(DRAWS))
    return {'mean': round(m, 3), 't95': [round(m - t * s, 3), round(m + t * s, 3)],
            'boot95_docs': [round(b[int(.025 * DRAWS)], 3), round(b[int(.975 * DRAWS) - 1], 3)], 'docs_above_0': sum(v > 0 for v in x), 'docs': len(x)}


def main():
    rows = missing.all_points(); rng = random.Random(SEED); res = {}
    for name, docs_f, meas_f, kev, min_pos in TESTS:
        D = [d for d in json.load(open(os.path.join(OUT, docs_f), encoding='utf-8'))['docs'] if len(d['positives']) >= min_pos and d['negatives']]
        M = {r['doc']: r for r in json.load(open(os.path.join(OUT, meas_f), encoding='utf-8'))['docs']}
        per = []
        for d in D:
            c = prior(rows, d['doc'], d['type'])
            per.append({'doc': d['doc'], 'PRIOR': round(auroc([c[x] for x in d['positives']], [c[x] for x in d['negatives']]), 3),
                        kev: M[d['doc']][f'{kev}_auroc'], 'RERANK': M[d['doc']]['RERANK_auroc']})
        diff = lambda a, b: [r[a] - r[b] for r in per]
        res[name] = {'docs': per, 'mean_auroc': {a: round(st.mean(r[a] for r in per), 3) for a in ('PRIOR', kev, 'RERANK')},
                     f'{kev}-RERANK': intervals(diff(kev, 'RERANK'), rng), f'{kev}-PRIOR': intervals(diff(kev, 'PRIOR'), rng),
                     'RERANK-PRIOR': intervals(diff('RERANK', 'PRIOR'), rng)}
    with open(os.path.join(OUT, 'prior_check.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    for name, r in res.items():
        print(name, r['mean_auroc'], {k: v for k, v in r.items() if '-' in k})


if __name__ == '__main__':
    main()
