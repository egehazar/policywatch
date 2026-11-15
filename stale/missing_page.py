"""Curator page for the missing points pilot (stale/PREREG_missing.md): cases a document may state that ToS;DR has
no point for on that service (out/site/missing.html).

For each of the pilot's four documents: the top 10 candidate cases with no approved point on the service (the pilot's
negatives), ranked by one method's best-passage score, each with that passage. A place to look, not a verdict.
The method is the pilot's pick once stale/out/missing_result.json exists ('method'), otherwise Kev; an argument
overrides it. Cases already approved on the service (on this document or another) are never suggested, and the page
shows the pilot's measured accuracy for the method shown, or says it is not measured yet.
Usage  py -m stale.missing_page [KEV|RERANK|BM25]
"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from policywatch.report import page, esc, badge
from stale.missing import DOCS, TOP, all_points, best

FILES = {'KEV': 'missing_kev.json', 'RERANK': 'missing_rerank.json', 'BM25': 'missing_bm25.json'}
NAMES = {'KEV': 'the decision model (Kev-4B), p(yes) that the passage states the case',
         'RERANK': 'a cross-encoder reranker (bge-reranker-v2-m3), case title vs passage',
         'BM25': 'word match on the case title (BM25)'}
REPO = 'https://github.com/OpenTermsArchive/pga-versions/blob/main/'


def method():
    if len(sys.argv) > 1: return sys.argv[1].upper()
    p = os.path.join(OUT, 'missing_result.json')
    if os.path.exists(p): return 'KEV' if json.load(open(p, encoding='utf-8')).get('method') == 'Kev' else 'RERANK'
    return 'KEV'


def accuracy(arm):
    p = os.path.join(OUT, 'missing_result.json')
    if not os.path.exists(p):
        return ('<p class="note"><b>Accuracy: not measured yet.</b> A pre-registered pilot is checking these suggestions '
                'blind (stale/PREREG_missing.md). Until it reports, treat every line below as unchecked.</p>')
    r = json.load(open(p, encoding='utf-8')); a = r['precision_at_10'][arm]; lo, hi = a['wilson95']
    return (f'<p class="note"><b>Measured accuracy:</b> in the pilot&rsquo;s blind check, an AI rater (a Claude model, '
            f'not a person) judged that {a["yes"]} of this method&rsquo;s {a["cards"]} top-10 suggestions state the case '
            f'({a["yes_share"]:.0%}, 95% interval {lo:.0%} to {hi:.0%}), and {a["yes_or_partly_share"]:.0%} to state it at '
            f'least partly. {gpt(arm)}Pilot reading: {esc(r["reading"].lower())}. Four documents only; '
            f'<code>stale/RESULT_missing.md</code>.</p>')


def gpt(arm):
    p = os.path.join(OUT, 'missing_gpt.json')
    if not os.path.exists(p): return ''
    g = json.load(open(p, encoding='utf-8')); a = g['gpt']['precision_at_10'][arm]; ag = g['agreement']
    return (f'A second AI rater (GPT) judged {a["yes"]} of the {a["cards"]} to state the case; the two agreed on '
            f'whether a card states the case for {ag["agree"]} of {ag["cards"]} cards. ')


def build(arm=None):
    arm = arm or method()
    D = json.load(open(DOCS, encoding='utf-8'))['docs']
    S = json.load(open(os.path.join(OUT, FILES[arm]), encoding='utf-8'))
    cid, cls = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for r in all_points():
        cid[r['case_title']][r.get('case_id')] += 1; cls[r['case_title']][r.get('classification')] += 1
    secs = []
    for d in D:
        if d['doc'] not in S: continue
        rows = S[d['doc']]; sc = {c: best(rows, c) for c in d['negatives']}
        top = sorted(d['negatives'], key=lambda c: -sc[c][0])[:TOP]
        items = []
        for k, c in enumerate(top, 1):
            s, i = sc[c]; t = d['pieces'][i]; n = 1600            # pieces are at most 1,500 characters: shown whole
            case_id = cid[c].most_common(1)[0][0] if cid[c] else None
            link = f' <a class="sm" href="https://edit.tosdr.org/cases/{esc(case_id)}">case {esc(case_id)}</a>' if case_id else ''
            shown = f'p(yes) {s:.2f}' if arm == 'KEV' else f'score {s:.3g}'
            items.append(f'<div class="card"><div class="row"><b>{k}. {esc(c.strip())}</b> '
                         f'{badge(cls[c].most_common(1)[0][0] if cls[c] else "")}{link}</div>'
                         f'<details class="sm"><summary>Best passage: {i + 1} of {len(d["pieces"])} ({shown})</summary>'
                         f'<div class="diff">{esc(t[:n])}{"…" if len(t) > n else ""}</div></details></div>')
        plat, name = d['doc'].split('/', 1)
        secs.append(f'<h2>{esc(plat)}: {esc(name[:-3] if name.endswith(".md") else name)}</h2>'
                    f'<p class="sm mut">{len(d["positives"])} cases already have an approved point quoting this document; '
                    f'{len(d["excluded"])} more are approved for {esc(plat)} (on another document, or on this one with a quote that is '
                    f'gone, partial or short) and are not suggested. Asked: '
                    f'{len(d["negatives"])} cases that ToS;DR often approves on {esc(d["type"])} documents and has no point '
                    f'for on {esc(plat)}. <a href="{REPO}{esc(d["doc"])}">Current text</a>.</p>' + ''.join(items))
    body = (f'<h1>Possible missing points</h1>'
            f'<p>Cases these documents may state that ToS;DR has no point for on the service yet: for each document, the '
            f'{TOP} highest-scoring cases by {esc(NAMES[arm])}, each with the passage that scored highest. A place to '
            f'look, not a verdict: read the passage before proposing a point; a case may be stated weakly, only in part, '
            f'or not at all. &ldquo;No point&rdquo; means no <em>approved</em> point: ToS;DR&rsquo;s public data does not '
            f'show pending or declined ones, and a few suggestions are variants of a case already approved for the '
            f'service.</p>' + accuracy(arm) + ''.join(secs))
    dest = os.path.join(ROOT, 'out', 'site', 'missing.html')
    with open(dest, 'w', encoding='utf-8') as f: f.write(page('Possible missing points', body))
    print(dest, arm, len(secs), 'documents')


if __name__ == '__main__':
    build()
