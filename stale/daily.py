"""Daily stale-evidence watch: which approved ToS;DR points lost their quoted evidence since the last run. No model.

Each run
 1. archive  git fetch + fast-forward of the pga-versions clone (skipped with --no-fetch, or when its work tree has
             local changes). Open Terms Archive records new versions most days.
 2. ToS;DR   service/v3 for each platform (one request each), point/v1 only for points that are new or whose
             updated_at changed. The live copy is stale/live/data/; stale/data/ (the snapshot hashed in the relocation
             pre-registration) is never written.
 3. match    stale.match over the live copy -> stale/live/out/points.jsonl. stale/match.py is hashed in
             stale/PREREG_relocate.sha256, so it is used unchanged: only its module paths point at the live copy.
 4. compare  with the previous run (the first run compares with the 11-12 snapshot, stale/out/points.jsonl):
               new drop     the quote was present at the last run and is now gone or partly gone
               worse        partly gone before, gone now
               new point    approved since the last run (status as found; a new point can already be stale)
               recovered    gone or partly gone before, present now (a curator re-anchored it, or the text came back)
               removed      no longer listed as approved with a quote
               now tracked / lost track   the quote moved into or out of the archived documents
             Every new drop gets the old passage and the most similar new passage (stale.triage.align).
    -> stale/live/runs/<UTC timestamp>.json, one line per run in stale/live/log.jsonl, and stale/live/out/digest.html
Usage  py -m stale.daily <pga-versions> [--no-fetch] [--no-tosdr]
"""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LIVE = os.path.join(HERE, 'live'); DATA = os.path.join(LIVE, 'data'); OUT = os.path.join(LIVE, 'out')
RUNS = os.path.join(LIVE, 'runs'); SNAPSHOT = os.path.join(HERE, 'out', 'points.jsonl')
sys.path.insert(0, ROOT)
from stale import match
from stale.pull import SERVICES, get
from stale.triage import align
from policywatch import archive
from policywatch.diffing import paras
from policywatch.report import page, esc, wdiff, badge


def git(arch, *a, timeout=900):
    try:
        return subprocess.run(['git', '-C', arch, *a], capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(a, 124, '', f'git {a[0]} timed out after {timeout} s')


def update_archive(arch):
    """Moves the shared clone: run this job alone, not while a scan or memo check reads the archive."""
    before = git(arch, 'rev-parse', 'HEAD').stdout.strip()
    if git(arch, 'status', '--porcelain', '--untracked-files=no').stdout.strip():
        return {'head': before, 'fetched': False, 'why': 'work tree has local changes'}
    f = git(arch, 'fetch', '--quiet', 'origin')
    if f.returncode: return {'head': before, 'fetched': False, 'why': f.stderr.strip()[:300]}
    m = git(arch, 'merge', '--ff-only', '--quiet', '@{u}')
    after = git(arch, 'rev-parse', 'HEAD').stdout.strip()
    return {'head': after, 'previous_head': before, 'fetched': True, 'new_commits': int(git(arch, 'rev-list', '--count', f'{before}..{after}').stdout.strip() or 0),
            'why': m.stderr.strip()[:300] if m.returncode else ''}


def refresh_tosdr():
    """Incremental: one service/v3 request per platform; point/v1 only for new or edited points."""
    os.makedirs(DATA, exist_ok=True); fetched, failed = 0, []
    for plat, sid in SERVICES.items():
        path = os.path.join(DATA, plat + '.json')
        seed = path if os.path.exists(path) else os.path.join(HERE, 'data', plat + '.json')
        prev = {}
        if os.path.exists(seed):
            with open(seed, encoding='utf-8') as fh: S0 = json.load(fh)
            prev = {p['id']: p for p in S0['points']}
        try:
            s = get(f'/service/v3/?id={sid}')
            listed = s.get('points')
            if not isinstance(listed, list): raise ValueError('no points list in the response')
            if len(prev) >= 10 and len(listed) < .5 * len(prev):     # an error page or a partial answer, not a purge
                raise ValueError(f'{len(listed)} points listed, {len(prev)} last time')
        except Exception as e:      # keep the last copy: a platform missing from the live copy would read as "removed"
            failed.append(f'{plat}: {type(e).__name__}: {str(e)[:120]}')
            if seed != path and prev:
                with open(path, 'w', encoding='utf-8') as fh: json.dump(S0, fh, ensure_ascii=False, indent=1)
            continue
        pts = []
        for p in listed:
            old = prev.get(p['id'])
            if old and (old.get('updated_at') or '')[:19] == (p.get('updated_at') or '')[:19]:
                pts.append(old); continue
            try:
                d = get(f"/point/v1/?id={p['id']}"); c = d.get('case') or {}; fetched += 1
                if d.get('id') != p['id']: raise ValueError('unexpected point/v1 body')
            except Exception as e:      # keep the old record (or skip a new point until the next run)
                failed.append(f"{plat} point {p['id']}: {type(e).__name__}")
                if old: pts.append(old)
                continue
            pts.append({'id': d['id'], 'case_id': c.get('id'), 'case_title': c.get('title'), 'classification': c.get('classification'),
                        'status': d.get('status'), 'document_id': d.get('document_id'), 'quote_text': d.get('quote_text'),
                        'quote_start': d.get('quote_start'), 'quote_end': d.get('quote_end'), 'created_at': d.get('created_at'),
                        'updated_at': d.get('updated_at'), 'source': d.get('source'), 'title': d.get('title')})
        rec = {'platform': plat, 'service_id': sid, 'service': s.get('name'), 'pulled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'documents': [{'id': x['id'], 'name': x['name'], 'url': x.get('url'), 'updated_at': x.get('updated_at')} for x in s.get('documents', [])],
               'points': pts}
        with open(path + '.tmp', 'w', encoding='utf-8') as fh: json.dump(rec, fh, ensure_ascii=False, indent=1)
        os.replace(path + '.tmp', path)
    return fetched, failed


def load(p):
    if not os.path.exists(p): return {}
    with open(p, encoding='utf-8') as fh: return {r['point']: r for r in (json.loads(l) for l in fh if l.strip())}


def compare(prev, cur):
    ev = []
    for pid, r in cur.items():
        a, b = (prev.get(pid) or {}).get('status'), r['status']
        if a is None: kind = 'new point'
        elif a == 'present' and b in ('gone', 'partly'): kind = 'new drop'
        elif a == 'partly' and b == 'gone': kind = 'worse'
        elif a in ('gone', 'partly') and b == 'present': kind = 'recovered'
        elif a == 'not in archive' and b != 'not in archive': kind = 'now tracked'
        elif a != 'not in archive' and b == 'not in archive': kind = 'lost track'    # e.g. the archive dropped the document
        else: continue
        ev.append({'kind': kind, 'before': a, **r})
    ev += [{'kind': 'removed', 'before': r['status'], **r, 'status': 'no longer approved with a quote'}
           for pid, r in prev.items() if pid not in cur]
    return ev


def passage(arch, r):
    if not (r.get('last_present') and r.get('dropped_at')): return None
    old = archive.git(arch, 'show', f"{r['last_present']['commit']}:{r['doc']}")
    new = archive.git(arch, 'show', f"{r['dropped_at']['commit']}:{r['doc']}")
    ps = align(r['quote'], paras(old), paras(new)) or {}
    ps['looks_cut_off'] = archive.History.cut_off(old, new)     # a capture cut off part-way hides quotes for a version
    return ps


def digest(runs, repo, sug=None, prop=None, arm=None):
    """One page: the latest run's events with passages, then the run log. sug/prop/arm: optional suggestions for the
    events whose quote is gone or partly gone (stale/daily_suggest.py), shown as on the curator pages."""
    last = runs[-1]; sug = sug or {}
    order = {'new drop': 0, 'worse': 1, 'new point': 2, 'recovered': 3, 'removed': 4, 'now tracked': 5, 'lost track': 6}
    cards = []
    for e in sorted(last['events'], key=lambda e: (order[e['kind']], e['platform'])):
        d = e.get('dropped_at') or {}; ps = e.get('passage') or {}
        when = f' since <a href="{repo}/commit/{d["commit"]}">{d["date"]}</a> ({esc(d.get("subject", ""))})' if d else ''
        body = ('<p class="sm"><b>The new capture looks cut off part-way</b>: the quote may come back at the next capture.</p>'
                if ps.get('looks_cut_off') else '')
        if 'old' not in ps: pass
        elif ps.get('removed'):
            body += f'<div class="diff"><span class="ctx">Old passage:</span>\n{esc(ps["old"])}</div><p class="sm"><b>No similar passage in the new text.</b></p>'
        elif ps.get('similarity', 0) >= .6:
            body += f'<div class="diff">{wdiff(ps["old"], ps["new"])}</div>'
        else:
            body += (f'<div class="diff"><span class="ctx">Old passage:</span>\n{esc(ps["old"])}</div><div class="diff"><span class="ctx">'
                    f'Most similar new passage ({ps["similarity"]:.0%} of its word triples shared):</span>\n{esc(ps["new"])}</div>')
        if e['point'] in sug and e['status'] in ('gone', 'partly'):
            from stale.report import suggestion
            body += suggestion(sug[e['point']], arm, (prop or {}).get(e['point']))
        cards.append(f'<div class="card"><div class="row"><b>{esc(e["kind"])}</b> · {esc(e["platform"])} · {esc(e["case_title"])}'
                     f'{badge(e.get("classification"))}<a class="sm" href="https://edit.tosdr.org/points/{e["point"]}">point {e["point"]}</a></div>'
                     f'<div class="sm mut">quote {esc(e.get("before") or "new")} &rarr; {esc(e["status"])}{when}</div>{body}</div>')
    rows = ''.join(f'<tr><td>{esc(r["run_at"][:16])}</td><td>{esc((r["archive"].get("head") or "")[:8])}</td><td>{r["archive"].get("new_commits", "")}</td>'
                   f'<td>{r["tosdr_point_fetches"]}</td><td>{r["counts"].get("present", 0)}</td><td>{r["counts"].get("partly", 0)}</td>'
                   f'<td>{r["counts"].get("gone", 0)}</td>' + ''.join(f'<td>{r["events_by_kind"].get(k, 0)}</td>' for k in order) + '</tr>'
                   for r in reversed(runs))
    A = last['archive']
    arch_note = (f'Archive updated: {A.get("new_commits", 0)} new versions.' if A.get('fetched') and not A.get('why')
                 else f'<b>Archive not updated</b> ({esc(A.get("why") or "unknown")}).')
    fail = (f' <b>ToS;DR refresh failed for</b> {esc("; ".join(last["tosdr_failed"]))} (last copy kept).'
            if last.get('tosdr_failed') else '')
    head = (f'<h1>Approved points whose evidence changed: daily</h1><p class="mut">Run {esc(last["run_at"])}, compared with '
            f'{esc(last["compared_with"])}. String matching only; whether a point still holds is a curator&rsquo;s call.</p>'
            f'<p class="sm">{arch_note}{fail}</p>')
    table = ('<h2>Runs</h2><table><tr><th>Run (UTC)</th><th>Archive</th><th>New versions</th><th>Points refetched</th><th>Present</th>'
             '<th>Partly</th><th>Gone</th>' + ''.join(f'<th>{k}</th>' for k in order) + f'</tr>{rows}</table>')
    body = head + (f'<h2>{len(cards)} changes in the latest run</h2>' + ''.join(cards) if cards else '<p>No changes in the latest run.</p>') + table
    os.makedirs(OUT, exist_ok=True)
    html_ = re.sub(r'<nav class="sm">.*?</nav>', '', page('Stale evidence: daily', body), count=1)   # no index/about here
    with open(os.path.join(OUT, 'digest.html'), 'w', encoding='utf-8') as fh: fh.write(html_)


def run(arch, fetch=True, tosdr=True):
    match.low_priority()
    prev_path = os.path.join(OUT, 'points.jsonl')
    compared_with = 'the previous run' if os.path.exists(prev_path) else 'the 2026-11-12 snapshot'
    prev = load(prev_path if os.path.exists(prev_path) else SNAPSHOT)
    arch_state = update_archive(arch) if fetch else {'head': git(arch, 'rev-parse', 'HEAD').stdout.strip(), 'fetched': False, 'why': '--no-fetch'}
    fetched, failed = refresh_tosdr() if tosdr else (0, ['--no-tosdr'])
    if not os.path.isdir(DATA):
        raise SystemExit('no live ToS;DR copy yet: run once without --no-tosdr')
    tmp = os.path.join(LIVE, 'tmp')
    match.HERE, match.OUT = LIVE, tmp          # match.run reads HERE/data/*.json and writes OUT/points.jsonl, summary.json
    match.run(arch)
    cur = load(os.path.join(tmp, 'points.jsonl'))
    ev = compare(prev, cur)
    for e in ev:
        if e['kind'] in ('new drop', 'worse', 'new point') and e['status'] in ('gone', 'partly'):
            e['passage'] = passage(arch, e)
    counts = {}
    for r in cur.values(): counts[r['status']] = counts.get(r['status'], 0) + 1
    by = {}
    for e in ev: by[e['kind']] = by.get(e['kind'], 0) + 1
    now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    rec = {'run_at': now, 'compared_with': compared_with, 'archive': arch_state,
           'archive_head_date': git(arch, 'log', '-1', '--format=%cI').stdout.strip(), 'tosdr_point_fetches': fetched,
           'tosdr_failed': failed, 'points': len(cur), 'counts': counts, 'events_by_kind': by, 'events': ev}
    os.makedirs(RUNS, exist_ok=True)
    with open(os.path.join(RUNS, now.replace(':', '') + '.json'), 'w', encoding='utf-8') as fh: json.dump(rec, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(LIVE, 'log.jsonl'), 'a', encoding='utf-8') as fh:
        fh.write(json.dumps({k: v for k, v in rec.items() if k != 'events'}) + '\n')
    os.makedirs(OUT, exist_ok=True)            # the new baseline only once this run's events are saved
    for f in ('points.jsonl', 'summary.json'): os.replace(os.path.join(tmp, f), os.path.join(OUT, f))
    runs = []
    for f in sorted(os.listdir(RUNS)):
        with open(os.path.join(RUNS, f), encoding='utf-8') as fh: runs.append(json.load(fh))
    digest(runs, archive.remote_url(arch) or 'https://github.com/OpenTermsArchive/pga-versions')
    print(now, 'archive', arch_state, 'refetched', fetched, 'points', counts, 'events', by)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    run(a[0], fetch='--no-fetch' not in sys.argv, tosdr='--no-tosdr' not in sys.argv)
