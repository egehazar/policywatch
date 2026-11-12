"""Curator page: approved ToS;DR points whose quoted evidence changed in a platform edit (out/site/stale.html).

No model decides anything on this page. Quote coverage and passage alignment are string matching (stale/match.py,
stale/triage.py). If stale/out/triage.jsonl exists, the decision model's answer to the point's case question on the
old and new passage is shown as a hint.
Usage  py -m stale.report [repo url]
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from policywatch.report import page, esc, wdiff, badge

REPO = 'https://github.com/OpenTermsArchive/pga-versions'


def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


def build(repo=REPO):
    pts = jl(os.path.join(HERE, 'out', 'points.jsonl'))
    pas = {r['point']: r for r in jl(os.path.join(HERE, 'out', 'passages.jsonl'))}
    tri = {r['point']: r for r in jl(os.path.join(HERE, 'out', 'triage.jsonl'))}
    S = json.load(open(os.path.join(HERE, 'out', 'summary.json'), encoding='utf-8'))
    T = S['total']
    rows = ''.join(f'<tr><td>{esc(p)}</td><td>{v.get("approved_with_quote", 0)}</td><td>{v.get("present", 0)}</td>'
                   f'<td>{v.get("partly", 0)}</td><td>{v.get("gone", 0)}</td><td>{v.get("not in archive", 0)}</td></tr>'
                   for p, v in sorted(S['platforms'].items()) if v.get('approved_with_quote'))
    head = (f'<h1>Approved points whose evidence changed</h1><p class="mut">ToS;DR approves each point with a quote from a '
            f'platform\'s terms or privacy policy. This page checks every approved quote on the {len([1 for v in S["platforms"].values() if v.get("approved_with_quote")])} '
            f'Open Terms Archive platforms that ToS;DR covers against every recorded version of the documents.</p>'
            f'<p>{T["approved_with_quote"]} approved points with a quote: <b>{T.get("present", 0)}</b> still in the current text, '
            f'<b>{T.get("partly", 0)}</b> partly, <b>{T.get("gone", 0)}</b> gone, {T.get("not in archive", 0)} in no archived version '
            f'(the document is not tracked, or the quote predates the archive).</p>'
            '<div class="note">ToS;DR\'s own platform marks a point "approved-not-found" when a recrawl misses its quote. '
            'This list adds when the quote dropped (the archive version), whether that was the platform\'s edit or a change in '
            'the archive\'s extraction, and the passage that replaced it. Whether a point still holds is a curator\'s call.</div>'
            f'<table><tr><th>Platform</th><th>With quote</th><th>Present</th><th>Partly</th><th>Gone</th><th>Not in archive</th></tr>{rows}</table>')
    drops = [r for r in pts if r['status'] in ('gone', 'partly') and r.get('drop_kind') == 'platform edit']
    drops.sort(key=lambda r: (r['platform'], r['dropped_at']['date']), reverse=False)
    other = sum(1 for r in pts if r['status'] in ('gone', 'partly') and r.get('drop_kind') != 'platform edit')
    body = [head, f'<h2>{len(drops)} points whose quote dropped in a platform edit</h2>'
                  f'<p class="mut sm">{other} more dropped at an archive extraction change or have no single drop version; '
                  'they are not listed because the platform may not have changed anything.</p>']
    cur = None
    for r in drops:
        if r['platform'] != cur:
            cur = r['platform']; body.append(f'<h2>{esc(cur)}</h2>')
        d = r['dropped_at']; p = pas.get(r['point']) or {}; ps = p.get('passage')
        when = 'before' if r.get('drop_after_point_update') else 'after'      # drop after the edit = edited before it
        hint = ''
        t = tri.get(r['point'])
        if t and t.get('p_old') is not None and ps and ps.get('removed'):
            hint = (f'<div class="sm">Decision model, "{esc(t["question"])}": old passage {t["p_old"]:.2f} '
                    '(no new passage to compare; a hint, not a verdict)</div>')
        elif t and t.get('p_old') is not None:
            hint = (f'<div class="sm">Decision model, "{esc(t["question"])}": old passage {t["p_old"]:.2f}, new passage '
                    f'{t["p_new"]:.2f} (a hint, not a verdict)</div>')
        if ps and ps.get('removed'):
            diff = (f'<div class="diff"><span class="ctx">Old passage:</span>\n{esc(ps["old"])}</div>'
                    '<p class="sm"><b>No similar passage in the new text</b> (removed, or rewritten beyond word overlap).</p>')
        elif ps and ps.get('similarity', 0) >= .6:
            diff = f'<div class="diff">{wdiff(ps["old"], ps["new"])}</div>'
        elif ps:     # a heavy rewrite: a word diff would be unreadable
            diff = (f'<div class="diff"><span class="ctx">Old passage:</span>\n{esc(ps["old"])}</div>'
                    f'<div class="diff"><span class="ctx">Most similar new passage ({ps["similarity"]:.0%} of its word triples '
                    f'shared):</span>\n{esc(ps["new"])}</div>')
        else:
            diff = '<p class="sm mut">The quote could not be placed in the old text (it spans several passages).</p>'
        body.append(
            f'<div class="card"><div class="row"><b>{esc(r["case_title"])}</b>{badge(r.get("classification"))}'
            f'<a class="sm" href="https://edit.tosdr.org/points/{r["point"]}">point {r["point"]}</a></div>'
            f'<div class="sm mut">{esc(r["doc"].split("/")[1][:-3])} · quote {r["status"]} since '
            f'<a href="{repo}/commit/{d["commit"]}">{d["date"]}</a> ({esc(d["subject"])}) · point last edited '
            f'{esc(r["point_updated_at"])}, {when} the change · current coverage {r["current_coverage"]:.0%}</div>'
            f'<p class="sm"><i>Quote:</i> {esc(re.sub(r"<[^<>]*>", "", r["quote"])[:600])}</p>{diff}{hint}</div>')
    out = os.path.join(ROOT, 'out', 'site'); os.makedirs(out, exist_ok=True)
    path = os.path.join(out, 'stale.html')
    with open(path, 'w', encoding='utf-8') as f: f.write(page('Stale evidence', ''.join(body)))
    print(path, len(drops), 'points listed')


if __name__ == '__main__':
    build(*sys.argv[1:])
