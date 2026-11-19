"""Private tracker notes (PLAN_ledger.md, addendum 1): Ege's review sheet, then one gap table per tracker.

  py -m aiwatch.notes review    -> out/ledger/notes/REVIEW_for_Ege.md: every verified grant still in the current
                                   text that some tracker lacks; Ege marks each KEEP or STRIKE <reason>
  py -m aiwatch.notes tables    -> out/ledger/notes/gaps_<tracker>.md (KEEP rows only; refuses while any is undecided)

Nothing here is published. The tables are material for private notes that Ege writes and sends.
"""
import json, os, re, sys
from aiwatch.ledger import LED, updates
from aiwatch.trackers import TR, TRACKERS

NOTES = os.path.join(LED, 'notes')
REVIEW = os.path.join(NOTES, 'REVIEW_for_Ege.md')
NAMES = {'iitom': 'Is It Training on Me?', 'tostracker': 'TOSTracker', 'conductatlas': 'ConductAtlas'}


def rows():
    cur = json.load(open(os.path.join(TR, 'current.json'), encoding='utf-8'))
    fa = json.load(open(os.path.join(LED, 'first_appearance.json'), encoding='utf-8'))
    R = [dict(json.loads(l)) for l in open(os.path.join(TR, 'rows.jsonl'), encoding='utf-8')]
    for r in R:
        r['current'] = cur.get(r['item'])
        f = fa.get(r['card'], {})
        r['alert_date'] = r['date']
        if f.get('first_date') and f['first_date'] < r['date']:   # the sentence was archived before this alert
            r['date'] = f['first_date']
            r['diff'] = f'https://github.com/OpenTermsArchive/{r["coll"]}/commit/{f["first_commit"]}'
    return R


def gap(r, t):
    """'missing' (service covered, clause not recorded), 'uncovered', or None (recorded)."""
    a = r[t]
    if (a.get('clause') or '').lower() == 'yes': return None
    return 'missing' if (a.get('covers') or '').lower() == 'yes' else 'uncovered'


def review():
    os.makedirs(NOTES, exist_ok=True)
    try: U = updates(True)
    except SystemExit: U = updates(False)
    blocks = {(u['coll'], u['commit'], u['doc']): u['blocks'] for u in U}
    R = [r for r in rows() if r['current'] and any(gap(r, t) for t in TRACKERS)]
    out = ['# Review: AI-training clauses for the tracker notes (for Ege; nothing is sent until you decide)', '',
           f'{len(R)} rows: verified grants (both AI raters) whose sentence is still in the current archived text and '
           'that at least one tracker lacks. For each, read BEFORE and AFTER. KEEP only if the AFTER text really lets '
           'the company use its users\' content or personal data to train AI (or clearly widens that). Then replace '
           'the row\'s "Decision: ?" line with "Decision: KEEP" or "Decision: STRIKE <reason>".', '']
    for i, r in enumerate(sorted(R, key=lambda r: (r['svc'], r['date'])), 1):
        also = ', '.join(sorted({a['svc'] for a in r['also']}))
        tr = '; '.join(f'{NAMES[t]}: {gap(r, t) or "has it (" + (r[t].get("earliest") or "?") + ")"}' for t in TRACKERS)
        out += [f'## {i}. {r["svc"]}, {r["doc"]}, first archived {r["date"]}  [{r["item"]}]',
                f'- Same text also under: {also}' if also else '- Same text under no other service',
                f'- Archive diff: {r["diff"]}',
                f'- Scope (raters): {r["scope_1"]} / {r["scope_2"]}. Deciding sentence: "{r["quote_1"]}"',
                f'- Trackers: {tr}']
        for o, nw in blocks.get((r['coll'], r['commit'], r['doc']), []):
            out += ['', '**BEFORE**', '', '> ' + o.replace('\n', '\n> '), '', '**AFTER**', '', '> ' + nw.replace('\n', '\n> ')]
        out += ['', 'Decision: ?', '']
    open(REVIEW, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
    print(f'{len(R)} rows -> {REVIEW}')


def decisions():
    """Addendum 3: Fable 5.2 and GPT-6 review the rows instead of Ege. -> item -> (keep_both, fable_row)"""
    F, G = {}, {}
    for f in sorted(os.listdir(NOTES)):
        tgt = F if f.startswith('review_fable_') else G if f == 'review_gpt.jsonl' else None
        if tgt is None or not f.endswith('.jsonl'): continue
        for line in open(os.path.join(NOTES, f), encoding='utf-8'):
            if line.strip().startswith('{'): a = json.loads(line); tgt[a['item']] = a
    return {i: (F[i]['decision'] == 'KEEP' and G[i]['decision'] == 'KEEP', F[i]) for i in F if i in G}


def tables():
    D = decisions(); R = [r for r in rows() if r['current'] and any(gap(r, t) for t in TRACKERS)]
    und = [r['item'] for r in R if r['item'] not in D]
    if und: raise SystemExit(f'{len(und)} rows lack a Fable or GPT review; nothing written')
    keep = [r for r in R if D[r['item']][0]]
    allr = rows()
    for t in TRACKERS:
        dated = [r for r in allr if (r[t].get('clause') or '').lower() == 'yes' and re.fullmatch(r'\d{4}-\d{2}-\d{2}', r[t].get('earliest') or '')]
        early = [r for r in dated if r['date'] < r[t]['earliest']]
        lines = [f'# {NAMES[t]}: AI-training clauses in the Open Terms Archive history that it lacks', '',
                 'Draft material for a private note that Ege writes. Dates are when the archive first recorded '
                 'the text, not when the company introduced it. Every row was labelled a grant by two AI raters '
                 '(Claude, GPT) blind to the method, then kept by two AI reviewers (Fable, GPT) who read the full text; '
                 "Fable confirmed each gap on the tracker's own site. No person has read the rows.", '']
        for kind, title in (('missing', 'Services it covers, clause not recorded'), ('uncovered', 'Services it does not cover')):
            # a tracker claim is used only if Fable confirmed it on the tracker's own site (addendum 3)
            sel = sorted([r for r in keep if gap(r, t) == kind and D[r['item']][1]['trackers'].get(t) == 'confirmed'],
                         key=lambda r: (r['svc'], r['date']))
            lines += [f'## {title} ({len(sel)})', '', '| Service | Document | First archived | Sentence | Archive diff |', '|---|---|---|---|---|']
            lines += [f'| {r["svc"]} | {r["doc"]} | {r["date"]} | {r["quote_1"][:220]} | {r["diff"]} |' for r in sel] + ['']
        lines += ['## History it could backfill', '',
                  f'Of the {len(dated)} clauses it records with a date, the archive has {len(early)} earlier '
                  f'(back to {min((r["date"] for r in early), default="-")}).', '']
        open(os.path.join(NOTES, f'gaps_{t}.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print(f'{len(keep)} rows kept of {len(R)} -> {NOTES}')


if __name__ == '__main__':
    {'review': review, 'tables': tables}[sys.argv[1]]()
