"""The AI-training clause ledger as files a person can read: Ege's review sheet, then the public CSV and page.

  py -m aiwatch.page review     -> aiwatch/out/ledger/REVIEW_for_Ege.md (old and new text of every row, KEEP/STRIKE)
  py -m aiwatch.page build      -> aiwatch/out/ledger/ai_training_clauses.csv and .html (rows Ege kept only)

Rows come from out/ledger/press/ledger_rows.jsonl (ledger.press_tally). Ege's decisions are read from the review
sheet: each row's line "Decision: KEEP" or "Decision: STRIKE <reason>". Nothing is built while a row is undecided.
"""
import csv, html, json, os, re, sys
from aiwatch.ledger import LED, diff_link, updates

P = os.path.join(LED, 'press')
REVIEW = os.path.join(LED, 'REVIEW_for_Ege.md')
SCOPE = {'THIRD': 'shared for other companies to train', 'GENERAL': 'general or generative AI',
         'NARROW': 'one named purpose (ads, recommendations, fraud, safety...)'}


def rows():
    return [json.loads(l) for l in open(os.path.join(P, 'ledger_rows.jsonl'), encoding='utf-8')]


def press_text(r):
    if not r['press_any']: return 'no press report found by two documented searches'
    if r['press_first']: return f"first press report found: {r['press_first']} ({r['press_lag_days']:+d} days)"
    return 'press report found (date unknown)'


def review():
    """One section per row: the card text Kev and the keywords saw, the raters' labels, the press searches."""
    try: U = updates(True)
    except SystemExit: U = updates(False)          # Kev scores not complete: keyword-alert blocks only
    blocks = {(u['coll'], u['commit'], u['doc']): u['blocks'] for u in U}
    out = ['# Review: AI-training clause ledger rows (for Ege, before anything is published)', '',
           'For each row, read the BEFORE and AFTER text. Keep it only if the AFTER text really lets the company use '
           'its users\' content or personal data to train AI (or clearly widens that), and the sentence quoted is the '
           'one that says so. Replace "Decision: ?" with "Decision: KEEP" or "Decision: STRIKE <reason>".', '']
    for i, r in enumerate(sorted(rows(), key=lambda r: r['date']), 1):
        also = ', '.join(sorted({a['svc'] for a in r['also']}))
        out += [f'## {i}. {r["svc"]}, {r["doc"]}, first archived {r["date"]}  [{r["item"]}]',
                f'- Same text also under: {also}' if also else '- Same text under no other service',
                f'- Archive diff: {r["diff"]}',
                f'- Raters: scope {r["scope_1"]} / {r["scope_2"]}; deciding sentence (rater 1): "{r["quote_1"]}"',
                f'- Press: {press_text(r)}; company mention: {"yes" if r["company"] else "no"}; '
                f'tracker record: {"yes" if r["tracker"] else "no"}']
        for s in r['searches']:
            if s.get('press_url'): out.append(f'  - press: {s.get("press_date")} {s.get("press_outlet", "")} {s["press_url"]}')
            if s.get('company_url'): out.append(f'  - company: {s.get("company_date", "")} {s["company_url"]}')
            if s.get('tracker_url'): out.append(f'  - tracker: {s["tracker_url"]}')
        for o, n in blocks.get((r['coll'], r['commit'], r['doc']), []):
            out += ['', '**BEFORE**', '', '> ' + o.replace('\n', '\n> '), '', '**AFTER**', '', '> ' + n.replace('\n', '\n> ')]
        out += ['', 'Decision: ?', '']
    open(REVIEW, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
    print(f'{len(rows())} rows -> {REVIEW}')


def decisions():
    d, cur = {}, None
    for line in open(REVIEW, encoding='utf-8'):
        m = re.match(r'## \d+\. .*\[(P\w+)\]', line)
        if m: cur = m.group(1)
        m = re.match(r'Decision: (KEEP|STRIKE)\s*(.*)', line.strip())
        if m and cur: d[cur] = (m.group(1), m.group(2).strip())
    return d


def build():
    R, D = rows(), decisions()
    undecided = [r['item'] for r in R if r['item'] not in D]
    if undecided: raise SystemExit(f'{len(undecided)} rows undecided in {REVIEW}; nothing built')
    keep = sorted([r for r in R if D[r['item']][0] == 'KEEP'], key=lambda r: r['date'])
    struck = [(r, D[r['item']][1]) for r in R if D[r['item']][0] == 'STRIKE']
    tally = json.load(open(os.path.join(LED, 'tally.json'), encoding='utf-8'))
    with open(os.path.join(LED, 'ai_training_clauses.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['date_first_archived', 'service', 'also_under', 'document', 'sentence_added', 'scope',
                    'press_report', 'press_first_date', 'company_mention', 'tracker_record', 'archive_diff'])
        for r in keep:
            w.writerow([r['date'], r['svc'], '; '.join(sorted({a['svc'] for a in r['also']})), r['doc'], r['quote_1'],
                        r['scope_1'], 'yes' if r['press_any'] else 'none found', r['press_first'] or '',
                        'yes' if r['company'] else 'no', 'yes' if r['tracker'] else 'no', r['diff']])
    n_none = sum(not r['press_any'] for r in keep)
    e = html.escape
    trs = '\n'.join(
        f'<tr><td class="d">{e(r["date"])}</td><td><b>{e(r["svc"])}</b><br><span class="m">{e(r["doc"])}</span></td>'
        f'<td class="q">&ldquo;{e(r["quote_1"])}&rdquo;</td><td class="m">{e(SCOPE.get(r["scope_1"], r["scope_1"]))}</td>'
        f'<td class="m">{e(press_text(r))}</td><td><a href="{e(r["diff"])}">diff</a></td></tr>' for r in keep)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI-training clauses, 2023-2026</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1c1a;--mut:#6b675f;--line:#e4e0d8;--acc:#8a4b14}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151412;--fg:#ece8e1;--mut:#a39d92;--line:#2e2b27;--acc:#e0a46a}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;margin:0}}
main{{max-width:1100px;margin:0 auto;padding:32px 16px 64px}} h1{{font-size:1.7rem;line-height:1.25;margin:0 0 12px}}
p{{max-width:72ch}} .m{{color:var(--mut);font-size:.9rem}} a{{color:var(--acc)}}
.wrap{{overflow-x:auto;border-top:1px solid var(--line);margin-top:24px}} table{{border-collapse:collapse;width:100%;min-width:760px}}
td,th{{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid var(--line)}} th{{font-size:.8rem;color:var(--mut);font-weight:600}}
td.d{{white-space:nowrap;font-variant-numeric:tabular-nums}} td.q{{max-width:46ch}}
</style></head><body><main>
<h1>AI-training clauses added to archived terms and privacy policies, 2023&ndash;2026</h1>
<p>Open Terms Archive records every change to the terms and privacy policies of about 470 online services. Between
January 2023 and November 2026, <b>{len(keep)}</b> recorded changes on <b>{len({r["svc"] for r in keep})}</b> services
added text that lets the company use its users&rsquo; content or personal data to train AI or machine-learning models,
or clearly widened such a right. For <b>{n_none}</b> of them, two documented searches found no press report.</p>
<p class="m">Each row quotes the sentence added; the date is when the archive first recorded it, not when the company
introduced it. A sentence describes a permitted use; it does not show that the company does this. Rows were found by
a keyword rule and a small language model, labelled by two AI raters from different companies, and each one was read
by a person before publication ({len(struck)} struck). Corrections: CORRECTIONS_ADDRESS.</p>
<div class="wrap"><table><thead><tr><th>First archived</th><th>Service</th><th>Sentence added</th><th>Scope</th>
<th>Press</th><th>Archive</th></tr></thead><tbody>
{trs}
</tbody></table></div>
<h2>How the monitor was measured</h2>
<p class="m">Cards rated: {tally["cards"]}. Verified by both raters: {tally["verified_grants"]} (agreement kappa
{tally["kappa_grant"]}). Precision: keyword rule {tally["precision"]["regex"]}, Kev-4B {tally["precision"]["kev"]}.
Share of verified rows each found: keyword rule {tally["relative_recall"]["regex"]}, Kev-4B
{tally["relative_recall"]["kev"]}. Method and pre-registered plan: aiwatch/PLAN_ledger.md.</p>
</main></body></html>'''
    open(os.path.join(LED, 'ai_training_clauses.html'), 'w', encoding='utf-8', newline='\n').write(page)
    print(f'{len(keep)} rows kept, {len(struck)} struck -> ai_training_clauses.csv/.html')


if __name__ == '__main__':
    {'review': review, 'build': build}[sys.argv[1]]()
