"""Stale evidence beyond the 20 platforms: the same pipeline over other Open Terms Archive collections.

The 20-platform page (stale/match.py over pga-versions) is extended to every service of another collection (contrib,
genai-contrib, dating, user-rights) that ToS;DR also reviews. stale/match.py, stale/triage.py and stale/suggest.py are
hashed in pre-registrations, so they are used unchanged: only their module paths are pointed at stale/wide/<collection>/
(as stale/daily.py does).

map     <collection>              OTA services -> ToS;DR services, by exact name or by web domain (the declaration's
                                  fetch URLs and its tosback2 import, against ToS;DR's service URLs). The 22
                                  pga-versions services are left out.  -> stale/wide/<collection>/map.json
pull    <collection>              ToS;DR's approved points with quotes for the mapped services (service/v3, then
                                  point/v1 per point, about one request per 0.6 s; resumable per service)
                                  -> stale/wide/<collection>/data/<OTA service>.json, in stale/pull.py's format
match   <collection>              stale.match over that collection (raw/, one row per point and folder), then dedupe
                                  -> stale/wide/<collection>/out/points.jsonl, summary.json
cheap   <collection>              no model: passages (stale.triage prep), ToS;DR's stored copy (stale.phoenix), BM25
                                  suggestions, the page out/site/stale_<collection>.html
kev     <collection> [port]       Kev's suggestions (stale.suggest kev) and proposed quotes (stale.propose), the page
Usage   py -m stale.wide map contrib
"""
import glob, json, os, re, sys, time
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); WIDE = os.path.join(HERE, 'wide')
DATA_ROOT = os.path.join(os.path.dirname(ROOT), 'decision-serving', 'data')
sys.path.insert(0, ROOT)
from stale.pull import SERVICES, get

SECOND = {'co', 'com', 'org', 'net', 'gov', 'ac', 'edu', 'ne', 'or', 'go'}     # co.uk, com.au, ne.jp ...


def site(host):
    """Registrable domain, roughly: the last two labels, or three under a two-letter country code's second level."""
    h = (host or '').lower().split(':')[0].strip('.')
    if h.startswith('www.'): h = h[4:]
    p = h.split('.')
    if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in SECOND: return '.'.join(p[-3:])
    return '.'.join(p[-2:])


def norm(name):
    return re.sub(r'[^a-z0-9]', '', (name or '').lower())


def declarations(collection):
    """OTA service name -> {'urls': fetch URLs, 'imported': tosback2 rule domain or None, 'types': document types}."""
    out = {}
    for f in sorted(glob.glob(os.path.join(DATA_ROOT, f'{collection}-declarations', 'declarations', '*.json'))):
        if f.endswith('.history.json'): continue
        d = json.load(open(f, encoding='utf-8'))
        terms = d.get('terms') or d.get('documents') or {}
        urls = []
        for v in terms.values():
            fs = v.get('fetch') if isinstance(v, dict) else None
            if isinstance(v, list): fs = [x.get('fetch') for x in v if isinstance(x, dict)]
            urls += fs if isinstance(fs, list) else [fs] if fs else []
        imp = d.get('importedFrom') or ''
        m = re.search(r'/rules/([^/]+)\.xml$', imp)
        out[os.path.basename(f)[:-5]] = {'name': d.get('name'), 'urls': [u for u in urls if isinstance(u, str)],
                                         'imported': m.group(1) if m else None, 'types': sorted(terms)}
    return out


def build_map(collection):
    S = json.load(open(os.path.join(HERE, 'data', 'services_list.json'), encoding='utf-8'))['services']
    pga = set(SERVICES.values())
    by_name, by_site = {}, {}
    for s in S:
        if s['id'] in pga: continue
        by_name.setdefault(norm(s['name']), []).append(s)
        for u in s.get('urls') or []: by_site.setdefault(site(u), []).append(s)
    D = declarations(collection)
    vdir = os.path.join(DATA_ROOT, f'{collection}-versions')
    M, unmatched = {}, []
    for key, d in D.items():
        if not os.path.isdir(os.path.join(vdir, key)): continue          # declared but never recorded
        sites = {site(urlparse(u).netloc) for u in d['urls']} | ({site(d['imported'])} if d['imported'] else set())
        cand, how = by_name.get(norm(d['name'] or key), []), 'name'
        if not cand:
            cand = [s for x in sites for s in by_site.get(x, [])]; how = 'domain'
        cand = list({s['id']: s for s in cand}.values())
        if not cand: unmatched.append(key); continue
        # several ToS;DR services: the comprehensively reviewed one, then the one whose name is closest
        cand.sort(key=lambda s: (not s['is_comprehensively_reviewed'], norm(s['name']) != norm(key), s['id']))
        s = cand[0]
        M[key] = {'tosdr_id': s['id'], 'tosdr_name': s['name'], 'how': how, 'rating': s['rating'],
                  'comprehensive': s['is_comprehensively_reviewed'], 'sites': sorted(sites), 'types': d['types'],
                  'alternatives': [c['id'] for c in cand[1:]]}
    seen = {}
    for k, v in M.items(): seen.setdefault(v['tosdr_id'], []).append(k)
    for sid, ks in seen.items():        # two OTA folders on one ToS;DR service: both kept, flagged
        if len(ks) > 1:
            for k in ks: M[k]['shared_with'] = [x for x in ks if x != k]
    os.makedirs(os.path.join(WIDE, collection), exist_ok=True)
    with open(os.path.join(WIDE, collection, 'map.json'), 'w', encoding='utf-8') as f:
        json.dump({'collection': collection, 'built': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                   'services_list_fetched': json.load(open(os.path.join(HERE, 'data', 'services_list.json'), encoding='utf-8'))['fetched'],
                   'declared': len(D), 'mapped': M, 'unmatched': unmatched}, f, ensure_ascii=False, indent=1)
    by = {}
    for v in M.values(): by[v['how']] = by.get(v['how'], 0) + 1
    print(collection, 'declared', len(D), 'mapped', len(M), by, 'unmatched', len(unmatched),
          'comprehensive', sum(v['comprehensive'] for v in M.values()), 'shared', sum('shared_with' in v for v in M.values()))


TOSDR = os.path.join(WIDE, '_tosdr')          # one file per ToS;DR service, shared by every collection and folder


def service(sid):
    """ToS;DR service sid with its approved points and their quotes (cached in stale/wide/_tosdr/<sid>.json)."""
    path = os.path.join(TOSDR, f'{sid}.json')
    if os.path.exists(path): return json.load(open(path, encoding='utf-8')), 0
    s = get(f'/service/v3/?id={sid}'); pts = []; n = 0
    for p in s.get('points', []):
        if p.get('status') != 'approved': continue
        d = get(f"/point/v1/?id={p['id']}"); c = d.get('case') or {}; n += 1
        pts.append({'id': d['id'], 'case_id': c.get('id'), 'case_title': c.get('title'), 'classification': c.get('classification'),
                    'status': d.get('status'), 'document_id': d.get('document_id'), 'quote_text': d.get('quote_text'),
                    'quote_start': d.get('quote_start'), 'quote_end': d.get('quote_end'), 'created_at': d.get('created_at'),
                    'updated_at': d.get('updated_at'), 'source': d.get('source'), 'title': d.get('title')})
    rec = {'service_id': sid, 'service': s.get('name'), 'pulled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'documents': [{'id': x['id'], 'name': x['name'], 'url': x.get('url'), 'updated_at': x.get('updated_at')} for x in s.get('documents', [])],
           'points': pts}
    os.makedirs(TOSDR, exist_ok=True)
    with open(path + '.tmp', 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
    os.replace(path + '.tmp', path)
    return rec, n + 1


def pull(collection):
    """One data file per OTA folder (platform = the folder), holding its ToS;DR service's points: a service mapped from
    several folders (Google from Gmail, AdSense, ...) is checked against each, and dedupe() keeps each point's best home."""
    M = json.load(open(os.path.join(WIDE, collection, 'map.json'), encoding='utf-8'))['mapped']
    out = os.path.join(WIDE, collection, 'data'); os.makedirs(out, exist_ok=True)
    t0 = time.time(); n = 0
    for key, m in sorted(M.items(), key=lambda x: x[1]['tosdr_id']):
        path = os.path.join(out, key + '.json')
        if os.path.exists(path): continue
        rec, k = service(m['tosdr_id']); n += k
        with open(path + '.tmp', 'w', encoding='utf-8') as f: json.dump({'platform': key, **rec}, f, ensure_ascii=False, indent=1)
        os.replace(path + '.tmp', path)
        print(f'[{time.time() - t0:.0f}s, {n} requests] {key} -> {m["tosdr_id"]} {rec["service"]}: {len(rec["points"])} approved, '
              f'{sum(1 for p in rec["points"] if p["quote_text"])} with quotes', flush=True)


def vdir(collection):
    return os.path.join(DATA_ROOT, f'{collection}-versions')


def run_match(collection):
    """stale.match unchanged, one row per (point, folder) in raw/, then dedupe() -> out/points.jsonl, out/summary.json."""
    from stale import match
    base = os.path.join(WIDE, collection)
    match.HERE, match.OUT, match.DIRS = base, os.path.join(base, 'raw'), {}
    match.run(vdir(collection))
    dedupe(collection)


def dedupe(collection):
    """A point is matched against every folder mapped to its ToS;DR service. Its home is the row match.py itself would
    pick across those folders: a row with an archived home first, then the highest current coverage, then the highest
    coverage ever. Rows with no home anywhere keep the folder whose name is closest to the service's."""
    base = os.path.join(WIDE, collection)
    M = json.load(open(os.path.join(base, 'map.json'), encoding='utf-8'))['mapped']
    rows = [json.loads(l) for l in open(os.path.join(base, 'raw', 'points.jsonl'), encoding='utf-8')]
    best = {}
    for r in rows:
        k = (r['status'] != 'not in archive', r.get('current_coverage') or 0, r['max_coverage'],
             norm(r['platform']) == norm(M[r['platform']]['tosdr_name']), r['platform'])
        if r['point'] not in best or k > best[r['point']][0]: best[r['point']] = (k, r)
    out = [r for _, r in sorted(best.values(), key=lambda x: (x[1]['platform'], x[1]['point']))]
    summary = {}
    for r in out:
        s = summary.setdefault(r['platform'], {'approved_with_quote': 0}); s['approved_with_quote'] += 1
        s[r['status']] = s.get(r['status'], 0) + 1
    tot = {}
    for v in summary.values():
        for k, n in v.items(): tot[k] = tot.get(k, 0) + n
    os.makedirs(os.path.join(base, 'out'), exist_ok=True)
    with open(os.path.join(base, 'out', 'points.jsonl'), 'w', encoding='utf-8') as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(os.path.join(base, 'out', 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump({'total': tot, 'platforms': summary}, f, indent=1)
    pe = [r for r in out if r['status'] in ('gone', 'partly') and r.get('drop_kind') == 'platform edit']
    print(collection, len(rows), 'rows ->', len(out), 'points', tot, '| dropped in a platform edit:', len(pe))


def point_modules(collection):
    """The hashed modules, pointed at stale/wide/<collection>/out (their own code unchanged)."""
    from stale import triage, suggest, phoenix
    out = os.path.join(WIDE, collection, 'out')
    triage.OUT = suggest.OUT = phoenix.OUT = out
    phoenix.HERE = os.path.join(WIDE, collection)          # phoenix reads HERE/data/*.json for each point's document id
    return triage, suggest, phoenix, out


def cheap(collection):
    """Everything without a model: passages, ToS;DR's stored copy, BM25 suggestions, the page."""
    triage, suggest, phoenix, out = point_modules(collection)
    triage.prep(vdir(collection)); phoenix.run(vdir(collection)); suggest.run(vdir(collection), 'bm25')
    page(collection, 'bm25')


def kev(collection, port='9995'):
    """Kev's suggestions and proposed quotes (hours of CPU), then the page."""
    from stale import propose
    triage, suggest, phoenix, out = point_modules(collection)
    suggest.run(vdir(collection), 'kev', f'http://127.0.0.1:{port}')
    propose.run(port, out)
    page(collection, 'kev')


def page(collection, arm):
    from stale import report
    from policywatch import archive
    repo = archive.remote_url(vdir(collection)) or f'https://github.com/OpenTermsArchive/{collection}-versions'
    report.build(repo.removesuffix('.git'), arm, os.path.join(WIDE, collection, 'out'),
                 os.path.join(ROOT, 'out', 'site', f'stale_{collection}.html'), 'services')


if __name__ == '__main__':
    cmd, col = sys.argv[1], sys.argv[2]
    if cmd == 'map': build_map(col)
    elif cmd == 'pull': pull(col)
    elif cmd == 'match': run_match(col)
    elif cmd == 'dedupe': dedupe(col)
    elif cmd == 'cheap': cheap(col)
    elif cmd == 'kev': kev(col, *sys.argv[3:])
    elif cmd == 'page': page(col, sys.argv[3] if len(sys.argv) > 3 else 'kev')
    else: raise SystemExit(__doc__)
