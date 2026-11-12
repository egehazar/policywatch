"""Compare ToS;DR's own stored copy of each document (Phoenix, api.tosdr.org document/v1) with the archive.

Fable r25: if Phoenix's copy still holds a quote the platform has since removed, the finding is "re-crawl pending",
not "wrong point". For every gone/partly point: coverage of its quote in Phoenix's copy, and which archived version
of the home document Phoenix's copy is closest to (share of Phoenix's word 6-grams found in that version).
Usage  py -m stale.phoenix <pga-versions>     -> stale/out/phoenix.jsonl, stale/data/docs/<id>.json (cache)
"""
import glob, json, os, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); DOCS = os.path.join(HERE, 'data', 'docs')
sys.path.insert(0, os.path.dirname(HERE))
from stale.match import words, grams, coverage, versions, low_priority
from stale.pull import API, UA


def doc(did):
    p = os.path.join(DOCS, f'{did}.json')
    if os.path.exists(p): return json.load(open(p, encoding='utf-8'))
    req = urllib.request.Request(f'{API}/document/v1?id={did}', headers=UA)
    d = json.loads(urllib.request.urlopen(req, timeout=60).read()); d = d.get('parameters', d); time.sleep(0.6)
    rec = {k: d.get(k) for k in ('id', 'name', 'url', 'text', 'updated_at', 'created_at', 'service_id')}
    os.makedirs(DOCS, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False)
    return rec


def run(arch):
    low_priority()
    rows = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    src = {}
    for f in glob.glob(os.path.join(HERE, 'data', '*.json')):
        S = json.load(open(f, encoding='utf-8'))
        for p in S['points']: src[p['id']] = p
    sel = [r for r in rows if r['status'] in ('gone', 'partly')]
    closest = {}
    out = []
    for r in sel:
        did = src[r['point']]['document_id']; D = doc(did); text = D.get('text') or ''
        dw = words(text); dg = grams(dw); ds = ' ' + ' '.join(dw) + ' '
        qw = words(r['quote'], quote=True)
        cov = coverage(qw, grams(qw), ds, dg) if dw else None
        key = (did, r['doc'])
        if key not in closest and dg:
            best = (0.0, None, None)
            for h, date, subj, vt in versions(arch, r['doc']):
                vg = grams(words(vt))
                c = len(dg & vg) / len(dg)
                if c > best[0]: best = (c, date, h)
            closest[key] = best
        c, date, h = closest.get(key, (0.0, None, None))
        out.append({'point': r['point'], 'platform': r['platform'], 'doc': r['doc'], 'status': r['status'],
                    'drop_kind': r.get('drop_kind'), 'dropped': (r.get('dropped_at') or {}).get('date'),
                    'phoenix_doc': did, 'phoenix_doc_updated_at': (D.get('updated_at') or '')[:10],
                    'phoenix_chars': len(text), 'quote_in_phoenix': None if cov is None else round(cov, 3),
                    'phoenix_closest_version': date, 'phoenix_closest_share': round(c, 3)})
    with open(os.path.join(OUT, 'phoenix.jsonl'), 'w', encoding='utf-8') as f:
        for x in out: f.write(json.dumps(x) + '\n')
    pe = [x for x in out if x['drop_kind'] == 'platform edit']
    stale_copy = sum(1 for x in pe if (x['quote_in_phoenix'] or 0) >= .8)
    print(f'{len(pe)} points dropped in a platform edit: Phoenix copy still holds the quote for {stale_copy} '
          f'(re-crawl pending), lacks it for {sum(1 for x in pe if x["quote_in_phoenix"] is not None and x["quote_in_phoenix"] < .8)}, '
          f'no stored text for {sum(1 for x in pe if x["quote_in_phoenix"] is None)}')
    for (did, d), (c, date, h) in sorted(closest.items(), key=lambda kv: kv[0][1]):
        print(f'  Phoenix doc {did} ~ {d} as of {date} ({c:.0%} of its 6-grams)')


if __name__ == '__main__':
    run(sys.argv[1])
