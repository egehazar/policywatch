"""Curator page: approved ToS;DR points whose quoted evidence changed in a platform edit (out/site/stale.html).

No model decides anything on this page. Quote coverage and passage alignment are string matching (stale/match.py,
stale/triage.py). If stale/out/triage.jsonl exists, the decision model's answer to the point's case question on the
old and new passage is shown as a hint.
Usage  py -m stale.report [repo url] [bm25|bge|kev] [data dir] [page path] [noun]
       (the arm whose <data dir>/suggest_<arm>.jsonl is shown, default bm25; data dir default stale/out)
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from policywatch.report import page, esc, wdiff, badge

REPO = 'https://github.com/OpenTermsArchive/pga-versions'


def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


ARMS = {'bm25': 'word match on the case title (BM25)', 'bge': 'embedding similarity to the case title (bge-small)',
        'kev': 'decision model (Kev-4B), p(yes) for the case question'}


def label_adopted():
    """Part D addendum 1: the clear / close label is shown only once its held-out rule said LABEL ADOPTED."""
    p = os.path.join(HERE, 'out', 'contrib_margin.json')
    return os.path.exists(p) and json.load(open(p, encoding='utf-8')).get('D', {}).get('reading') == 'LABEL ADOPTED'


CLEAR = .30      # stale/reloc_margin.py


def confidence(s, arm):
    # the label was validated with Kev scoring every piece: not shown for cascade suggestions (Kev saw the top 10 only)
    if arm != 'kev' or s.get('cascade') or len(s.get('top') or []) < 2 or not label_adopted(): return ''
    m = round(s['top'][0]['score'] - s['top'][1]['score'], 4)                # as stale/reloc_margin.py rounds it
    if m >= CLEAR:
        return ('<p class="sm"><b>Clear:</b> passage 1 scored well ahead of the next. In testing, a lead this large meant the '
                'passage held the curator&rsquo;s quote about 9 times in 10.</p>')
    return '<p class="sm"><b>Close:</b> the top passages scored close together; check passages 2 and 3 too.</p>'


def suggestion(s, arm, prop=None):
    """prop: Kev's proposed quote from its top passage (stale/propose.py), shown only with the kev arm."""
    if not s: return ''
    def body(k, t):
        n, txt = 900, None                                    # passage 1 is shown at least up to the end of the quote
        m = prop and k == 1 and re.search(r'\s+'.join(map(re.escape, prop['quote'].split())), t['text'])   # units join lines
        if m:
            n = max(n, m.end()); x = t['text']
            txt = f'{esc(x[:m.start()])}<ins>{esc(x[m.start():m.end()])}</ins>{esc(x[m.end():n])}'
        txt = txt or esc(t['text'][:n])
        return (f'<div class="diff"><span class="ctx">{k}. passage {t["piece"] + 1} of {s["n_pieces"]} (score {t["score"]:.3g}):</span>\n'
                f'{txt}{"…" if len(t["text"]) > n else ""}</div>')
    tops = ''.join(body(k, t) for k, t in enumerate(s['top'], 1))
    pq = (f'<p class="sm"><i>Suggested quote</i> (the decision model&rsquo;s pick from passage {prop["piece"] + 1}; when the passage '
          f'was right, this pick matched the curator&rsquo;s own quote 83% of the time in testing; check it before use): '
          f'<ins>{esc(prop["quote"])}</ins></p>') if prop else ''
    return confidence(s, arm) + pq + (f'<details class="sm"><summary>Where the case may be stated now: top {len(s["top"])} passages of the current text by '
            f'{esc(ARMS.get(arm, arm))}. A place to look, not a verdict: the case may no longer be stated at all.</summary>{tops}</details>')


def sid(name):
    """A section anchor for a platform name."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'x'


def build(repo=REPO, arm='bm25', base=None, dest=None, noun='platforms'):
    """base: the folder with points.jsonl etc. (default stale/out); dest: the page (default out/site/stale.html)."""
    base = base or os.path.join(HERE, 'out')
    sug = {r['point']: r for r in jl(os.path.join(base, f'suggest_{arm}.jsonl'))}
    prop = {r['point']: r for r in jl(os.path.join(base, 'propose_kev.jsonl'))} if arm == 'kev' else {}
    pts = jl(os.path.join(base, 'points.jsonl'))
    pas = {r['point']: r for r in jl(os.path.join(base, 'passages.jsonl'))}
    tri = {r['point']: r for r in jl(os.path.join(base, 'triage.jsonl'))}
    phx = {r['point']: r for r in jl(os.path.join(base, 'phoenix.jsonl'))}
    S = json.load(open(os.path.join(base, 'summary.json'), encoding='utf-8'))
    T = S['total']
    rows = ''.join(f'<tr><td>{esc(p)}</td><td>{v.get("approved_with_quote", 0)}</td><td>{v.get("present", 0)}</td>'
                   f'<td>{v.get("partly", 0)}</td><td>{v.get("gone", 0)}</td><td>{v.get("not in archive", 0)}</td></tr>'
                   for p, v in sorted(S['platforms'].items()) if v.get('approved_with_quote'))
    head = (f'<h1>Approved points whose evidence changed</h1><p class="mut">ToS;DR approves each point with a quote from a '
            f'platform\'s terms or privacy policy. This page checks every approved quote on the {len([1 for v in S["platforms"].values() if v.get("approved_with_quote")])} '
            f'Open Terms Archive {noun} that ToS;DR covers against every recorded version of the documents.</p>'
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
    held = [r for r in drops if (phx.get(r['point'], {}).get('quote_in_phoenix') or 0) >= .8]
    lack = [r for r in drops if r['point'] in phx and (phx[r['point']].get('quote_in_phoenix') or 0) < .8]
    body = [head, f'<h2>{len(drops)} points whose quote dropped in a platform edit</h2>'
                  f'<p><b>{len(held)}</b> of them still read correctly against ToS;DR&rsquo;s own stored copy of the document, which '
                  'predates the platform&rsquo;s edit: the points are not wrong on ToS;DR, its copy is out of date, and a re-crawl '
                  f'would mark them not found. <b>{len(lack)}</b> are approved although ToS;DR&rsquo;s stored copy no longer holds the '
                  'quote either.</p>'
                  f'<p class="mut sm">{other} more dropped at an archive extraction change or have no single drop version; '
                  'they are not listed because the platform may not have changed anything.</p>']
    if lack:     # the points a curator can act on now: ToS;DR's own copy has lost the quote too
        body.append('<p class="sm"><b>Start here</b> (approved, but ToS;DR&rsquo;s stored copy no longer holds the quote): '
                    + ' · '.join(f'<a href="#p{r["point"]}">{esc(r["platform"])}: {esc(r["case_title"])}</a>' for r in lack) + '</p>')
    n = {}
    for r in drops: n[r['platform']] = n.get(r['platform'], 0) + 1
    if len(n) > 1:
        body.append('<p class="sm mut">By platform: ' + ' · '.join(f'<a href="#s{sid(p)}">{esc(p)}</a> ({k})' for p, k in n.items()) + '</p>')
    cur = None
    for r in drops:
        if r['platform'] != cur:
            cur = r['platform']; body.append(f'<h2 id="s{sid(cur)}">{esc(cur)}</h2>')
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
        cap = f' · archive&rsquo;s latest capture {esc(r["latest_capture"])}' if r.get('latest_capture') else ''
        x = phx.get(r['point'])
        if x and (x.get('quote_in_phoenix') or 0) >= .8:
            phl = (f'<div class="sm">ToS;DR&rsquo;s stored copy (document {x["phoenix_doc"]}) still holds the quote; it matches the '
                   f'archive as of {esc(x["phoenix_closest_version"])} ({x["phoenix_closest_share"]:.0%}): <b>re-crawl pending</b></div>')
        elif x:
            phl = (f'<div class="sm">ToS;DR&rsquo;s stored copy (document {x["phoenix_doc"]}, close to the archive as of '
                   f'{esc(x["phoenix_closest_version"])}) <b>no longer holds the quote</b>, yet the point is approved</div>')
        else:
            phl = ''
        body.append(
            f'<div class="card" id="p{r["point"]}"><div class="row"><b>{esc(r["case_title"])}</b>{badge(r.get("classification"))}'
            f'<a class="sm" href="https://edit.tosdr.org/points/{r["point"]}">point {r["point"]}</a></div>'
            f'<div class="sm mut">{esc(r["doc"].split("/")[1][:-3])} · quote {r["status"]} since '
            f'<a href="{repo}/commit/{d["commit"]}">{d["date"]}</a> ({esc(d["subject"])}) · point last edited '
            f'{esc(r["point_updated_at"])}, {when} the change · current coverage {r["current_coverage"]:.0%}'
            f'{cap}</div>'
            f'{phl}<p class="sm"><i>Quote:</i> {esc(re.sub(r"<[^<>]*>", "", r["quote"])[:600])}</p>{diff}{hint}'
            f'{suggestion(sug.get(r["point"]), arm, prop.get(r["point"]))}</div>')
    path = dest or os.path.join(ROOT, 'out', 'site', 'stale.html'); os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f: f.write(page('Stale evidence', ''.join(body)))
    print(path, len(drops), 'points listed')


if __name__ == '__main__':
    build(*sys.argv[1:])
