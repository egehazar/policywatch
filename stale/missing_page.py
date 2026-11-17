"""Curator page for the missing points pilot (stale/PREREG_missing.md): cases a document may state that ToS;DR has
no point for on that service (out/site/missing.html).

For each of the pilot's four documents and the larger test's ten (stale/PREREG_missing2.md): the top 10 candidate
cases with no approved point on the service (the tests' negatives), ranked by one method's best-passage score, each
with that passage. A place to look, not a verdict.
The method is the pilot's pick once stale/out/missing_result.json exists ('method'), otherwise Kev; an argument
overrides it. Cases already approved on the service (on this document or another) are never suggested, and the page
shows the measured accuracy for the method shown (the pilot's, and the larger test's once it is scored), or says it
is not measured yet.
The remaining documents of the 20 platforms come from the cascade run (stale/RESULT_missing_wide.md), and a document
whose archived text changed after it was scored is shown as re-scored on the current text (stale/missing_watch.py);
both are marked not rated.
Usage  py -m stale.missing_page [KEV|RERANK|BM25]
"""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from policywatch.report import page, esc, badge
from stale.missing import DOCS, TOP, all_points, best, wilson
from stale import missing2, missing_wide, missing_watch, missing_rest

FILES = {'KEV': 'missing_kev.json', 'RERANK': 'missing_rerank.json', 'BM25': 'missing_bm25.json'}


def wide_note(arm, d=None):
    if arm != 'KEV': return ''
    m = os.path.join(OUT, 'missing_wide_measures.json'); r2 = os.path.join(OUT, 'missing2_result.json')
    t = ('<p class="sm note">Not rated. On this document the reranker picked 3 passages per case and Kev read only '
         'those (the cascade)')
    if os.path.exists(r2):
        a = json.load(open(r2, encoding='utf-8'))['precision_at_10']['CASCADE_KEV']
        t += f'; in the larger test an AI rater judged {a["yes"]} of the cascade&rsquo;s {a["cards"]} top-10 suggestions to state the case'
    if os.path.exists(m):
        w = json.load(open(m, encoding='utf-8'))
        t += (f'; on the {len(w["docs"])} documents of this run with 10 or more approved cases whose quote is still in '
              f'the text, it ranked those cases above the rest with AUROC {w["auroc"]["CASCADE_KEV"]:.2f} (reranker {w["auroc"]["RERANK"]:.2f})')
    return t + '.</p>'


def watch_note(arm, d):
    return (f'<p class="sm note">Not rated. The archived text changed on {esc(d["changed"][:10])} (a new Open Terms '
            f'Archive version), after this document was first scored{" and its suggestions were rated" if d["rated"] else ""}. '
            'These suggestions are on the current text, through the cascade: the reranker picked 3 passages per case '
            'and Kev read only those.</p>')


EN = set('the and of to you your we our is for in or with that this are'.split())


def english(pieces):
    """Share of common English function words; on the page's 40 documents Telegram's two (German) score .013 and .017,
    every other document .26 or more."""
    w = re.findall(r'[^\W\d_]+', ' '.join(pieces).lower()); return sum(x in EN for x in w) / max(len(w), 1) >= .10


def rest_note(arm, d=None):
    return ('<p class="sm note">Not rated. ToS;DR has no point matched to this document, so there was nothing to check '
            'the ranking against here. The reranker picked 3 passages per case and Kev read only those (the cascade).</p>')


# (documents file, scores file per arm, a note under each document): the pilot's four, the larger test's ten, then the
# remaining documents through the cascade (stale/PLAN_missing_wide.md)
SOURCES = ((DOCS, FILES, None), (missing2.DOCS, {a: f'missing2_{a.lower()}.json' for a in FILES}, None),
           (missing_wide.DOCS, {'KEV': 'missing_wide_kev.json', 'RERANK': 'missing_wide_rerank.json'}, wide_note),
           (missing_rest.DOCS, {'KEV': 'missing_rest_kev.json', 'RERANK': 'missing_rest_rerank.json'}, rest_note))
NAMES = {'KEV': 'the decision model (Kev-4B), p(yes) that the passage states the case',
         'RERANK': 'a cross-encoder reranker (bge-reranker-v2-m3), case title vs passage',
         'BM25': 'word match on the case title (BM25)'}
REPO = 'https://github.com/OpenTermsArchive/pga-versions/blob/main/'


def approved(plat, _cache={}):
    """Every case title with an approved point on the platform, in the 11-12 snapshot (stale/data/<platform>.json) or
    the daily watch's newer copy (stale/live/data/), including the points whose quote is under 3 words: stale/match.py
    skips those, so the tests' negatives can hold them (3 of the larger test's 425); the page never suggests them."""
    if plat not in _cache:
        _cache[plat] = set()
        for p in (os.path.join(HERE, 'data', plat + '.json'), os.path.join(HERE, 'live', 'data', plat + '.json')):
            d = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
            _cache[plat] |= {x['case_title'].strip() for x in d.get('points', []) if x.get('status') == 'approved'}
    return _cache[plat]


def rated_wide():
    """{(doc, case, passage index): verdict} from the blind rating of the page's unrated documents
    (stale/PLAN_wide_rate.md), once it is scored. A rating is used only while the page shows the same passage text the
    card showed (checked against the card file), so a document whose text changes again loses its ratings."""
    if not os.path.exists(os.path.join(OUT, 'wide_rate_result.json')): return {}
    from stale import wide_rate
    K = json.load(open(wide_rate.KEY, encoding='utf-8')); V, T = {}, {}
    for x, f in wide_rate.FOLDERS.items():
        V.update(json.load(open(os.path.join(f, 'verdicts.json'), encoding='utf-8')))
        T[x] = open(os.path.join(f, 'cards.md'), encoding='utf-8').read()
    P = {d['doc']: d['pieces'] for _, d, _, _ in wide_rate.docs()}; out = {}
    for c, k in K.items():
        t, i = P.get(k['doc'], []), k['piece']
        block = '\n'.join([f'## {c}', f'**Case:** {k["case"]}', '', '**Passage:**', '', '```', t[i].strip() if i < len(t) else '', '```', ''])
        if i < len(t) and block in T[k['folder']]:
            out[(k['doc'], k['case'], i)] = V[c]['verdict']
    return out


VERDICT = {'YES': 'AI rater: states it', 'PARTLY': 'AI rater: partly', 'NO': 'AI rater: does not state it'}


def method():
    if len(sys.argv) > 1: return sys.argv[1].upper()
    p = os.path.join(OUT, 'missing_result.json')
    if os.path.exists(p): return 'KEV' if json.load(open(p, encoding='utf-8')).get('method') == 'Kev' else 'RERANK'
    return 'KEV'


def accuracy(arm, unrated=0):
    p = os.path.join(OUT, 'missing_result.json')
    if not os.path.exists(p):
        return ('<p class="note"><b>Accuracy: not measured yet.</b> A pre-registered pilot is checking these suggestions '
                'blind (stale/PREREG_missing.md). Until it reports, treat every line below as unchecked.</p>')
    r = json.load(open(p, encoding='utf-8')); a = r['precision_at_10'][arm]; lo, hi = a['wilson95']
    p2 = os.path.join(OUT, 'missing2_result.json')
    r2 = json.load(open(p2, encoding='utf-8')) if os.path.exists(p2) else None
    if r2 and arm in r2['precision_at_10']:
        b = r2['precision_at_10'][arm]; y, n = a['yes'] + b['yes'], a['cards'] + b['cards']; plo, phi = wilson(y, n)
        wide = ''; pw = os.path.join(OUT, 'wide_rate_result.json')
        if unrated and os.path.exists(pw) and arm == 'KEV':
            w = json.load(open(pw, encoding='utf-8')); q, rr = w['precision_at_10']['PAGE'], w['precision_at_10']['RERANK']
            wlo, whi = q['wilson95']
            wide = (f' The {unrated} documents with a note under their title were scored later through the cascade (the '
                    'remaining documents, and any document whose text changed after it was scored). A third blind check '
                    f'rated their suggestions afterwards: the AI rater judged {q["yes"]} of {q["cards"]} to state the case '
                    f'({q["yes_share"]:.0%}, 95% interval {wlo:.0%} to {whi:.0%}), against {rr["yes"]} of {rr["cards"]} '
                    f'for the reranker&rsquo;s own top 10 on the same documents (<code>stale/RESULT_wide_rate.md</code>).')
        elif unrated:
            wide = (f' The {unrated} documents marked &ldquo;Not rated&rdquo; were scored later through the cascade (the '
                    'remaining documents, and any document whose text changed after it was scored); none of their '
                    'suggestions was rated (<code>stale/RESULT_missing_wide.md</code>).')
        return (f'<p class="note"><b>Measured accuracy:</b> in two blind checks, an AI rater (a Claude model, not a '
                f'person) judged that {a["yes"]} of this method&rsquo;s {a["cards"]} top-10 suggestions on the pilot&rsquo;s '
                f'four documents state the case, and {b["yes"]} of {b["cards"]} on the larger test&rsquo;s ten: {y} of {n} '
                f'in all ({y / n:.0%}, 95% interval {plo:.0%} to {phi:.0%}). {gpt(arm, b)}Readings: pilot '
                f'{esc(r["reading"].lower())}; larger test {esc(r2["reading_replication"].lower())}. '
                f'<code>stale/RESULT_missing.md</code>, <code>stale/RESULT_missing2.md</code>.{wide}</p>')
    return (f'<p class="note"><b>Measured accuracy:</b> in the pilot&rsquo;s blind check, an AI rater (a Claude model, '
            f'not a person) judged that {a["yes"]} of this method&rsquo;s {a["cards"]} top-10 suggestions state the case '
            f'({a["yes_share"]:.0%}, 95% interval {lo:.0%} to {hi:.0%}), and {a["yes_or_partly_share"]:.0%} to state it at '
            f'least partly. {gpt(arm)}Pilot reading: {esc(r["reading"].lower())}. Four documents only; '
            f'<code>stale/RESULT_missing.md</code>.</p>')


def gpt(arm, larger=None):
    p = os.path.join(OUT, 'missing_gpt.json')
    if not os.path.exists(p): return ''
    g = json.load(open(p, encoding='utf-8')); a = g['gpt']['precision_at_10'][arm]; ag = g['agreement']
    if larger is not None:
        p2 = os.path.join(OUT, 'missing2_gpt.json')
        if not os.path.exists(p2) or arm not in json.load(open(p2, encoding='utf-8'))['gpt']['precision_at_10']: return ''
        g2 = json.load(open(p2, encoding='utf-8')); b = g2['gpt']['precision_at_10'][arm]; ag2 = g2['agreement']
        return (f'A second AI rater (GPT) judged {a["yes"]} of {a["cards"]} and {b["yes"]} of {b["cards"]}; the two raters '
                f'agreed on whether a card states the case for {ag["agree"] + ag2["agree"]} of {ag["cards"] + ag2["cards"]} '
                f'cards. ')
    return (f'A second AI rater (GPT) judged {a["yes"]} of the {a["cards"]} to state the case; the two agreed on '
            f'whether a card states the case for {ag["agree"]} of {ag["cards"]} cards. ')


def build(arm=None):
    arm = arm or method()
    cid, cls = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    for r in all_points():
        cid[r['case_title']][r.get('case_id')] += 1; cls[r['case_title']][r.get('classification')] += 1
    secs = []; unrated = 0; watch = missing_watch.current(arm); R = rated_wide() if arm == 'KEV' else {}
    for docs, files, note in SOURCES:
        if arm not in files or not os.path.exists(os.path.join(OUT, files[arm])): continue
        p = os.path.join(OUT, files[arm])
        D = json.load(open(docs, encoding='utf-8'))['docs']; S = json.load(open(p, encoding='utf-8'))
        for d in D:
            if d['doc'] not in S: continue
            rows, nt, before = S[d['doc']], note, None
            neg = [c for c in d['negatives'] if c.strip() not in approved(d['doc'].split('/', 1)[0])]
            if d['doc'] in watch:                     # re-scored on its current text: mark what the change brought in
                before = set(sorted(neg, key=lambda c: -best(rows, c)[0])[:TOP])
                (d, rows), nt = watch[d['doc']], watch_note
            sc = {c: best(rows, c) for c in neg}
            top = sorted(neg, key=lambda c: -sc[c][0])[:TOP]
            items = []
            nh = nt(arm, d) if nt else ''
            if before is not None:
                kept = sum(c in before for c in top)
                nh = nh[:-len('</p>')] + (f' {kept} of these {len(top)} were in the top {TOP} before the change; the other '
                                          f'{len(top) - kept} are marked new.</p>')
            rv = [R[(d['doc'], c, sc[c][1])] for c in top if (d['doc'], c, sc[c][1]) in R]
            if rv and nh.startswith('<p class="sm note">Not rated. '):
                who = f'these {len(top)}' if len(rv) == len(top) else f'the {len(rv)} of these {len(top)} it rated'
                nh = nh.replace('Not rated. ', f'Rated afterwards, blind: an AI rater (a Claude model, not a person) judged '
                                               f'{rv.count("YES")} of {who} to state the case. ', 1)
            if not english(d['pieces']):
                nh += ('<p class="sm note">This archived text is not in English (by a simple word count); no policywatch '
                       'test checked Kev on text that is not in English.</p>')
            for k, c in enumerate(top, 1):
                new = ' <span class="badge">new since the text changed</span>' if before is not None and c not in before else ''
                s, i = sc[c]; t = d['pieces'][i]; n = 1600            # pieces are at most 1,500 characters: shown whole
                if (d['doc'], c, i) in R: new += f' <span class="badge">{VERDICT[R[(d["doc"], c, i)]]}</span>'
                case_id = cid[c].most_common(1)[0][0] if cid[c] else None
                link = f' <a class="sm" href="https://edit.tosdr.org/cases/{esc(case_id)}">case {esc(case_id)}</a>' if case_id else ''
                shown = f'p(yes) {s:.2f}' if arm == 'KEV' else f'score {s:.3g}'
                items.append(f'<div class="card"><div class="row"><b>{k}. {esc(c.strip())}</b> '
                             f'{badge(cls[c].most_common(1)[0][0] if cls[c] else "")}{link}{new}</div>'
                             f'<details class="sm"><summary>Best passage: {i + 1} of {len(d["pieces"])} ({shown})</summary>'
                             f'<div class="diff">{esc(t[:n])}{"…" if len(t) > n else ""}</div></details></div>')
            plat, name = d['doc'].split('/', 1)
            secs.append(f'<h2>{esc(plat)}: {esc(name[:-3] if name.endswith(".md") else name)}</h2>'
                        f'<p class="sm mut">{len(d["positives"])} cases already have an approved point quoting this document; '
                        f'{len(d["excluded"]) + len(d["negatives"]) - len(neg)} more are approved for {esc(plat)} (on another document, or on this one with a quote that is '
                        f'gone, partial or short) and are not suggested. Asked: '
                        f'{len(neg)} cases that ToS;DR often approves on {esc(d["type"])} documents and has no point '
                        f'for on {esc(plat)}. <a href="{REPO}{esc(d["doc"])}">Current text</a>.</p>'
                        + nh + ''.join(items))
            unrated += bool(nt)
    body = (f'<h1>Possible missing points</h1>'
            f'<p>Cases these documents may state that ToS;DR has no point for on the service yet: for each document, the '
            f'{TOP} highest-scoring cases by {esc(NAMES[arm])}, each with the passage that scored highest. A place to '
            f'look, not a verdict: read the passage before proposing a point; a case may be stated weakly, only in part, '
            f'or not at all. &ldquo;No point&rdquo; means no <em>approved</em> point: ToS;DR&rsquo;s public data does not '
            f'show pending or declined ones. Some suggestions are variants of, or close to, a case already approved for '
            f'the service: an AI check of the titles found 9 variants and 31 close ones among the 87 suggestions rated '
            f'YES, and nothing close on the service for the other 47.</p>' + accuracy(arm, unrated) + ''.join(secs))
    dest = os.path.join(ROOT, 'out', 'site', 'missing.html')
    with open(dest, 'w', encoding='utf-8') as f: f.write(page('Possible missing points', body))
    print(dest, arm, len(secs), 'documents')


if __name__ == '__main__':
    build()
