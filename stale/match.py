"""Is each approved ToS;DR point's quoted evidence still in the platform's current document? No model is used.

For every approved point with a quote, every recorded version of every document of that platform in pga-versions is
normalized (markdown links and HTML tags dropped, lower case, words only) and the quote's COVERAGE measured: the
share of its word 6-grams found in that version (quotes under 6 words: found as a whole or not).

  doc            the archive document with the highest coverage in any version (the quote's home)
  status         present (current coverage >= .8) | partly (.3-.8) | gone (< .3) | not in archive (never >= .5)
  last_present   the last version where coverage was >= .8, and dropped_at: the version right after it
A cut-off capture can hide a quote for one version; only the CURRENT version decides the status, and dropped_at is
the start of the final run of versions without it.

Usage  py -m stale.match <pga-versions dir>      -> stale/out/points.jsonl, stale/out/summary.json
"""
import glob, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); N = 6
DIRS = {'X': ['X', 'Twitter']}           # ToS;DR has one service for both archive folders


def map_doc(name):
    """ToS;DR document name -> archive document type (for explaining a quote that is in no archived version)."""
    n = name.lower()
    if 'cookie' in n or 'tracker' in n: return 'Trackers Policy'
    if 'data policy' in n or ('privacy' in n and not any(k in n for k in ('basics', 'california', 'framework'))): return 'Privacy Policy'
    if 'community' in n: return 'Community Guidelines'
    if 'law enforcement' in n: return 'Law Enforcement Guidelines'
    if ('terms' in n or 'user agreement' in n) and not n.startswith('ai '): return 'Terms of Service'
    return None


def drop_kind(subject):
    """A version is a platform edit ("Record new changes", or "Update <service> <doc>" in the archive's older format)
    or an archive change (a new extraction filter or declaration), which can drop text the platform never removed."""
    if subject.startswith('Record new changes') or (subject.startswith('Update ') and 'README' not in subject): return 'platform edit'
    if subject.startswith(('Apply technical', 'Refilter')): return 'archive change'
    return 'other'


def low_priority():
    if os.name == 'nt':     # IDLE_PRIORITY_CLASS; child git processes inherit it
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)


LIST = re.compile(r'(?m)^\s*(?:[-*+]|\d+(?:\\?\.\d+)*\\?[.)])\s+')    # markdown list markers ("1.", "2\.", "-")


def words(t, quote=False):
    """Words only. HTML tags (any length, and in a quote a tag cut off at either end) and list numbering are dropped:
    ToS;DR quotes are HTML (<ol><li> carries no numbers), the archive is markdown ("1.  Implied warranties").
    (Review 11-12: an 80-character tag limit and kept list numbers made present quotes look partly gone.)"""
    t = html.unescape(t or '')
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'<[^<>]*>', ' ', t)
    if quote:
        t = re.sub(r'<[^<>]*$', ' ', t)                                      # a tag cut off at the end
        t = re.sub(r'^\s*/?[a-zA-Z][a-zA-Z0-9]{0,15}(?:\s+[a-zA-Z-]+=[^<>]{0,300})?>', ' ', t)   # "p>", "a href=..>"
    t = LIST.sub(' ', t)
    return re.findall(r"[a-z0-9]+", t.lower())


def grams(ws):
    return {hash(tuple(ws[i:i + N])) for i in range(len(ws) - N + 1)}


def coverage(qw, qg, doc_ws_str, doc_g):
    if len(qw) < N: return 1.0 if (' ' + ' '.join(qw) + ' ') in doc_ws_str else 0.0
    return sum(1 for g in qg if g in doc_g) / len(qg)


def versions(archive, path):
    """[(commit, date, subject, text)] oldest first, read with one git cat-file process."""
    log = subprocess.run(['git', '-C', archive, 'log', '--format=%H%x09%ad%x09%s', '--date=short', '--', path],
                         capture_output=True, encoding='utf-8', errors='replace').stdout.splitlines()[::-1]
    rows = [l.split('\t', 2) for l in log]
    inp = ''.join(f'{h}:{path}\n' for h, _, _ in rows).encode('utf-8')
    raw = subprocess.run(['git', '-C', archive, 'cat-file', '--batch'], input=inp, capture_output=True).stdout
    out, i = [], 0
    for h, d, s in rows:
        j = raw.index(b'\n', i); line = raw[i:j]
        if line.endswith(b' missing'): i = j + 1; out.append((h, d, s, '')); continue   # the path may hold spaces
        n = int(line.split()[2]); text = raw[j + 1:j + 1 + n].decode('utf-8', 'replace'); i = j + 1 + n + 1
        out.append((h, d, s, text))
    return out


def run(archive):
    low_priority(); os.makedirs(OUT, exist_ok=True)
    rows, summary = [], {}
    for f in sorted(glob.glob(os.path.join(HERE, 'data', '*.json'))):
        with open(f, encoding='utf-8') as fh: S = json.load(fh)
        plat = S['platform']; docname = {d['id']: d['name'] for d in S['documents']}
        pts = [p for p in S['points'] if p['status'] == 'approved' and len(words(p['quote_text'], quote=True)) >= 3]
        Q = {p['id']: (words(p['quote_text'], quote=True),) for p in pts}
        Q = {k: (w, grams(w)) for k, (w,) in Q.items()}
        series = {}
        for d in DIRS.get(plat, [plat]):
            for path in sorted(glob.glob(os.path.join(archive, d, '*.md'))):
                rel = os.path.relpath(path, archive).replace('\\', '/')
                V = versions(archive, rel); cache = {}
                for p in pts: series[(p['id'], rel)] = []
                for h, date, subj, text in V:
                    if text not in cache:
                        ws = words(text); cache = {text: (' ' + ' '.join(ws) + ' ', grams(ws))}
                    s, g = cache[text]
                    for p in pts:
                        c = coverage(*Q[p['id']], s, g); series[(p['id'], rel)].append((h, date, subj, round(c, 3)))
        live = {rel for (_, rel) in series if rel.split('/')[0] == plat}     # X: the frozen Twitter/ folder is history only
        counts = {}
        for p in pts:
            # home: the live document holding most of the quote NOW, then the most ever (review 11-12: taking the first
            # document to reach the maximum made quotes that moved between documents look gone)
            cand = [(ser[-1][3] if rel in live else -1.0, max(x[3] for x in ser), rel)
                    for (pid, rel), ser in series.items() if pid == p['id'] and ser]
            cur_, mx, rel = max(cand, default=(0.0, 0.0, None))
            hist_only = mx < .5 and any(c[1] >= .5 and c[2] not in live for c in cand)
            if rel is not None and rel not in live: rel = None
            r = {'platform': plat, 'point': p['id'], 'case_id': p['case_id'], 'case_title': p['case_title'],
                 'classification': p['classification'], 'tosdr_document': docname.get(p['document_id']),
                 'point_updated_at': (p['updated_at'] or '')[:10], 'quote': p['quote_text'], 'max_coverage': round(mx, 3)}
            if mx < .5 or rel is None:
                r['status'] = 'not in archive'
                m = map_doc(r['tosdr_document'] or '')
                homes = [f'{d}/{m}.md' for d in DIRS.get(plat, [plat]) if m and os.path.exists(os.path.join(archive, d, m + '.md'))]
                if hist_only: r['why'] = 'only in the history of a folder the archive no longer updates (Twitter/)'
                elif not homes: r['why'] = 'document not tracked by the archive'
                else:
                    first = min(series[(p['id'], h)][0][1] for h in homes if series.get((p['id'], h)))
                    r['why'] = f'not in any archived version of {m} (archive from {first})'
                    r['archive_from'] = first
            else:
                ser = series[(p['id'], rel)]; cur = ser[-1][3]
                r.update(doc=rel, current_coverage=cur, versions=len(ser),
                         status='present' if cur >= .8 else 'partly' if cur >= .3 else 'gone')
                if r['status'] != 'present':
                    k = max((i for i, x in enumerate(ser) if x[3] >= .8), default=None)
                    if k is not None and k + 1 < len(ser):
                        r['last_present'] = {'commit': ser[k][0], 'date': ser[k][1]}
                        r['dropped_at'] = {'commit': ser[k + 1][0], 'date': ser[k + 1][1], 'subject': ser[k + 1][2],
                                           'coverage': ser[k + 1][3]}
                        r['drop_after_point_update'] = ser[k + 1][1] > r['point_updated_at']
                        r['drop_kind'] = drop_kind(ser[k + 1][2])
                    r['first_seen'] = next((x[1] for x in ser if x[3] >= .8), None)
            counts[r['status']] = counts.get(r['status'], 0) + 1; rows.append(r)
        summary[plat] = {'approved_with_quote': len(pts), **counts}
        print(plat, summary[plat], flush=True)
    tot = {}
    for v in summary.values():
        for k, n in v.items(): tot[k] = tot.get(k, 0) + n
    with open(os.path.join(OUT, 'points.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(os.path.join(OUT, 'summary.json'), 'w', encoding='utf-8') as f: json.dump({'total': tot, 'platforms': summary}, f, indent=1)
    print('TOTAL', tot)


if __name__ == '__main__':
    run(sys.argv[1])
