"""Which approved points were re-anchored by a curator after a platform edit? No model.

A point whose CURRENT quote first appears in the archive after the point was created must have had its quote replaced:
the text it quotes did not exist when the point was made. If that first appearance is also later than the document's
first archived version and is a platform edit (not an extraction change), the platform wrote that text after the
archive began, so the curator moved the point to new text. These are the relocations curators actually did by hand.

For the relocation test's eligible points (stale/out/reloc_docs.json 'order'): the first archived version of the home
document holding >= .8 of the quote, the document's first archived version, and the point's created_at
(stale/data/<platform>.json). Written before the relocation evaluation, as a declared secondary subgroup.
Usage  py -m stale.reanchored <pga-versions>   -> stale/out/reanchored.json
"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.dirname(HERE))
from stale.match import words, grams, coverage, versions, low_priority, drop_kind


def run(arch):
    low_priority()
    D = json.load(open(os.path.join(OUT, 'reloc_docs.json'), encoding='utf-8'))
    elig = set(D['order'])
    src = {}
    for f in glob.glob(os.path.join(HERE, 'data', '*.json')):
        for p in json.load(open(f, encoding='utf-8'))['points']: src[p['id']] = p
    rows = {json.loads(l)['point']: json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')}
    head = {}
    for line in os.popen(f'git -C "{arch}" rev-parse HEAD'): head = line.strip()
    out = []
    bydoc = {}
    for pid in elig: bydoc.setdefault(rows[pid]['doc'], []).append(pid)
    for doc, pids in sorted(bydoc.items()):
        V = versions(arch, doc)
        V = [v for v in V if v[3]]
        first_doc = V[0][1] if V else None
        cache = [(h, d, sj, (lambda ws: (' ' + ' '.join(ws) + ' ', grams(ws)))(words(t))) for h, d, sj, t in V]
        for pid in pids:
            q = rows[pid]['quote']; qw = words(q, quote=True); qg = grams(qw)
            fs = next(((h, d, sj) for h, d, sj, (s, g) in cache if coverage(qw, qg, s, g) >= .8), (None, None, ''))
            created = (src[pid].get('created_at') or '')[:10]
            out.append({'point': pid, 'doc': doc, 'created_at': created, 'doc_first_version': first_doc,
                        'quote_first_seen': fs[1], 'quote_first_commit': fs[0], 'first_seen_kind': drop_kind(fs[2]) if fs[2] else None,
                        'reanchored': bool(fs[1] and first_doc and fs[1] > first_doc and created and created < fs[1]
                                           and drop_kind(fs[2]) == 'platform edit')})
    res = {'archive_head': head, 'rule': 'quote_first_seen > doc_first_version and created_at < quote_first_seen and the first-seen version is a platform edit',
           'n_eligible': len(out), 'n_reanchored': sum(r['reanchored'] for r in out),
           'reanchored_in_order': [p for p in D['order'] if any(r['point'] == p and r['reanchored'] for r in out)],
           'points': sorted(out, key=lambda r: r['point'])}
    with open(os.path.join(OUT, 'reanchored.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    o = D['order']
    for n in (100, 150, 200, 300):
        print(f'first {n} of the fixed order: {sum(1 for p in o[:n] if p in set(res["reanchored_in_order"]))} re-anchored')
    print(res['n_reanchored'], 'of', res['n_eligible'], 'eligible points were re-anchored by a curator (rule above)')


if __name__ == '__main__':
    run(sys.argv[1])
