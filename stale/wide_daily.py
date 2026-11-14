"""Daily stale-evidence watch for the wider Open Terms Archive collections (stale/wide.py): stale/daily.py's steps,
per collection, on a live copy under stale/wide/live/<collection>/. The snapshot in stale/wide/<collection>/ (part D's
population) is never written.

Each run
 1. archive  fast-forward of the <collection>-versions clone (stale.daily.update_archive), unless --no-fetch
 2. ToS;DR   service/v3 for each mapped ToS;DR service, point/v1 only for new or edited points (seeded from the
             snapshot's stale/wide/_tosdr/), unless --no-tosdr; a failed service keeps its last copy
 3. match    stale.match, then stale.wide's dedupe and broken-capture guard, in a staging folder
 4. compare  with the previous run (the first run compares with the snapshot) using stale.daily.compare: new drops,
             new points, recovered quotes ... ; every new drop gets its old and new passage (stale.daily.passage)
 -> stale/wide/live/<collection>/runs/<UTC>.json, log.jsonl, out/points.jsonl (the new baseline, written last),
    out/digest.html
Usage  py -m stale.wide_daily <collection> [--no-fetch] [--no-tosdr]
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from stale import daily, match, wide
from stale.pull import get

LIVE = os.path.join(wide.WIDE, 'live')


def refresh(collection, sids):
    """Incremental ToS;DR refresh into live/_tosdr/<sid>.json; returns (point fetches, failures)."""
    d = os.path.join(LIVE, '_tosdr'); os.makedirs(d, exist_ok=True); fetched, failed = 0, []
    for sid in sorted(sids):
        path = os.path.join(d, f'{sid}.json'); seed = path if os.path.exists(path) else os.path.join(wide.TOSDR, f'{sid}.json')
        S0 = json.load(open(seed, encoding='utf-8')) if os.path.exists(seed) else {'points': []}
        prev = {p['id']: p for p in S0['points']}
        try:
            s = get(f'/service/v3/?id={sid}'); listed = [p for p in s.get('points', []) if p.get('status') == 'approved']
            if not isinstance(s.get('points'), list): raise ValueError('no points list in the response')
            if len(prev) >= 10 and len(listed) < .5 * len(prev): raise ValueError(f'{len(listed)} approved, {len(prev)} last time')
        except Exception as e:
            failed.append(f'{sid}: {type(e).__name__}: {str(e)[:100]}')
            if seed != path and S0['points']: shutil.copy(seed, path)
            continue
        pts = []
        for p in listed:
            old = prev.get(p['id'])
            if old and (old.get('updated_at') or '')[:19] == (p.get('updated_at') or '')[:19]: pts.append(old); continue
            try:
                q = get(f"/point/v1/?id={p['id']}"); c = q.get('case') or {}; fetched += 1
                if q.get('id') != p['id']: raise ValueError('unexpected point/v1 body')
            except Exception as e:
                failed.append(f"{sid} point {p['id']}: {type(e).__name__}")
                if old: pts.append(old)
                continue
            pts.append({'id': q['id'], 'case_id': c.get('id'), 'case_title': c.get('title'), 'classification': c.get('classification'),
                        'status': q.get('status'), 'document_id': q.get('document_id'), 'quote_text': q.get('quote_text'),
                        'quote_start': q.get('quote_start'), 'quote_end': q.get('quote_end'), 'created_at': q.get('created_at'),
                        'updated_at': q.get('updated_at'), 'source': q.get('source'), 'title': q.get('title')})
        rec = {'service_id': sid, 'service': s.get('name'), 'pulled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'documents': [{'id': x['id'], 'name': x['name'], 'url': x.get('url'), 'updated_at': x.get('updated_at')} for x in s.get('documents', [])],
               'points': pts}
        with open(path + '.tmp', 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
        os.replace(path + '.tmp', path)
    return fetched, failed


def run(collection, fetch=True, tosdr=True):
    match.low_priority()
    base = os.path.join(LIVE, collection); stage_root = os.path.join(LIVE, '_stage'); stage = os.path.join(stage_root, collection)
    M = json.load(open(os.path.join(wide.WIDE, collection, 'map.json'), encoding='utf-8'))
    prev_path = os.path.join(base, 'out', 'points.jsonl')
    compared_with = 'the previous run' if os.path.exists(prev_path) else 'the snapshot in stale/wide/' + collection
    prev = daily.load(prev_path if os.path.exists(prev_path) else os.path.join(wide.WIDE, collection, 'out', 'points.jsonl'))
    arch = wide.vdir(collection)
    arch_state = daily.update_archive(arch) if fetch else {'head': daily.git(arch, 'rev-parse', 'HEAD').stdout.strip(), 'fetched': False, 'why': '--no-fetch'}
    sids = {m['tosdr_id'] for m in M['mapped'].values()}
    fetched, failed = refresh(collection, sids) if tosdr else (0, ['--no-tosdr'])
    shutil.rmtree(stage, ignore_errors=True); os.makedirs(os.path.join(stage, 'data'))
    shutil.copy(os.path.join(wide.WIDE, collection, 'map.json'), os.path.join(stage, 'map.json'))
    for key, m in M['mapped'].items():
        src = os.path.join(LIVE, '_tosdr', f"{m['tosdr_id']}.json")
        if not os.path.exists(src): src = os.path.join(wide.TOSDR, f"{m['tosdr_id']}.json")
        if not os.path.exists(src): continue
        with open(os.path.join(stage, 'data', key + '.json'), 'w', encoding='utf-8') as f:
            json.dump({'platform': key, **json.load(open(src, encoding='utf-8'))}, f, ensure_ascii=False)
    match.HERE, match.OUT, match.DIRS = stage, os.path.join(stage, 'raw'), {}
    match.run(arch)
    old_wide = wide.WIDE; wide.WIDE = stage_root
    try: wide.dedupe(collection)
    finally: wide.WIDE = old_wide
    cur = daily.load(os.path.join(stage, 'out', 'points.jsonl'))
    ev = daily.compare(prev, cur)
    # a drop into a broken capture or an archive change is not news for a curator: kept in the run record, off the digest
    noise = [e for e in ev if e['kind'] in ('new drop', 'worse') and e.get('drop_kind') != 'platform edit']
    ev = [e for e in ev if e not in noise]
    for e in ev:
        if e['kind'] in ('new drop', 'worse', 'new point') and e['status'] in ('gone', 'partly') and e.get('drop_kind') == 'platform edit':
            e['passage'] = daily.passage(arch, e)
    counts, by = {}, {}
    for r in cur.values(): counts[r['status']] = counts.get(r['status'], 0) + 1
    for e in ev: by[e['kind']] = by.get(e['kind'], 0) + 1
    now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    rec = {'run_at': now, 'collection': collection, 'compared_with': compared_with, 'archive': arch_state,
           'archive_head_date': daily.git(arch, 'log', '-1', '--format=%cI').stdout.strip(), 'tosdr_point_fetches': fetched,
           'tosdr_failed': failed, 'points': len(cur), 'counts': counts, 'events_by_kind': by, 'events': ev,
           'not_platform_edits': noise}
    runs_dir = os.path.join(base, 'runs'); os.makedirs(runs_dir, exist_ok=True); os.makedirs(os.path.join(base, 'out'), exist_ok=True)
    with open(os.path.join(runs_dir, now.replace(':', '') + '.json'), 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
    with open(os.path.join(base, 'log.jsonl'), 'a', encoding='utf-8') as f: f.write(json.dumps({k: v for k, v in rec.items() if k not in ('events', 'not_platform_edits')}) + '\n')
    for name in ('points.jsonl', 'summary.json'): os.replace(os.path.join(stage, 'out', name), os.path.join(base, 'out', name))
    runs = [json.load(open(os.path.join(runs_dir, f), encoding='utf-8')) for f in sorted(os.listdir(runs_dir))]
    daily.OUT = os.path.join(base, 'out')
    from policywatch import archive
    daily.digest(runs, (archive.remote_url(arch) or f'https://github.com/OpenTermsArchive/{collection}-versions').removesuffix('.git'))
    print(now, collection, 'archive', arch_state, 'refetched', fetched, 'failed', len(failed), 'points', counts, 'events', by)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    run(a[0], fetch='--no-fetch' not in sys.argv, tosdr='--no-tosdr' not in sys.argv)
