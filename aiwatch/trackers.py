"""Tracker check (PLAN_ledger.md, addendum 1): for each verified grant, does each public AI-training-clause tracker
cover the service, record this clause, and from what date?

  py -m aiwatch.trackers sheet     -> out/ledger/trackers/items.txt (from out/ledger/verified.jsonl)
  py -m aiwatch.trackers tally     -> out/ledger/trackers/tally.json, rows.jsonl (needs answers_<tracker>.jsonl)
"""
import collections, datetime as dt, json, os, re, sys
from aiwatch.ledger import LED, diff_link

TR = os.path.join(LED, 'trackers')
TRACKERS = {
    'iitom': 'Is It Training on Me? (isittrainingonme.com): per-app pages /app/<slug>/ with quoted clauses, capture '
             'dates and a change history',
    'tostracker': 'TOSTracker (tostracker.app): the AI-training-rights analysis '
                  '(tostracker.app/analysis/ai-training-rights, CSV at /analysis/ai-training-rights.csv) and any '
                  'per-organisation pages in its archive',
    'conductatlas': 'ConductAtlas (conductatlas.com): per-platform pages /platform/<slug>/<document>/<provision>/ '
                    'with machine-written provision records and first-captured dates'}

ASK = ('For each item below: a change archived by Open Terms Archive on the given date added the given sentence to '
       'the service\'s document. Check ONE tracker, named at the top, and record for each item:\n'
       '- covers: does the tracker have a page or record for this service at all? (yes / no / unknown)\n'
       '- clause: does it record THIS AI-training permission for this service (the same or equivalent wording, in '
       'the same kind of document)? (yes / no / unknown)\n'
       '- earliest: the earliest date the tracker shows for that clause (a capture date, a change-log date or a '
       '"first captured" date), as YYYY-MM-DD, or "none" or "unknown". Do not guess.\n'
       '- url: the page you used.\n'
       'Use only the tracker\'s own site (web search restricted to it, or fetching its pages). Answer as JSON lines, '
       'one per item, nothing else: {"item": "<id>", "covers": "", "clause": "", "earliest": "", "url": ""}')


def verified():
    return [json.loads(l) for l in open(os.path.join(LED, 'verified.jsonl'), encoding='utf-8')]


def sheet():
    os.makedirs(TR, exist_ok=True)
    V = verified()
    with open(os.path.join(TR, 'items.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(ASK + '\n\n')
        for k in V:
            also = ', '.join(sorted({a['svc'] for a in k['also']}))
            f.write(f'=== ITEM T{k["card"][1:]} ===\nservice: {k["svc"]}' + (f' (same text also under: {also})' if also else '')
                    + f'\ndocument: {k["doc"]}\ndate first archived: {k["date"]}\nsentence: {k["quote_1"]}\n'
                    f'archive diff: {diff_link(k)}\n\n')
    print(f'{len(V)} items -> {os.path.join(TR, "items.txt")}')


def tally():
    V = verified(); res, rows = {}, {('T' + k['card'][1:]): dict(k, diff=diff_link(k)) for k in V}
    for t in TRACKERS:
        A = {}
        for line in open(os.path.join(TR, f'answers_{t}.jsonl'), encoding='utf-8'):
            if line.strip().startswith('{'): a = json.loads(line); A[a['item']] = a
        miss = [i for i in rows if i not in A]
        if miss: raise SystemExit(f'{t}: {len(miss)} items unanswered, e.g. {miss[:3]}')
        lags = []
        for i, r in rows.items():
            a = A[i]; r[t] = a
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', a.get('earliest') or ''):
                lags.append((dt.date.fromisoformat(a['earliest']) - dt.date.fromisoformat(r['date'])).days)
        yes = lambda f: sum((A[i].get(f) or '').lower() == 'yes' for i in rows)
        res[t] = {'items': len(rows), 'covers_service': yes('covers'), 'records_clause': yes('clause'),
                  'dated': len(lags), 'archive_earlier': sum(l > 0 for l in lags),
                  'tracker_earlier_or_same': sum(l <= 0 for l in lags),
                  'median_tracker_minus_archive_days': sorted(lags)[len(lags) // 2] if lags else None}
        res[t]['covered_but_clause_missing'] = sum((A[i].get('covers') or '').lower() == 'yes'
                                                  and (A[i].get('clause') or '').lower() == 'no' for i in rows)
    res['in_no_tracker'] = sum(all((r[t].get('clause') or '').lower() != 'yes' for t in TRACKERS) for r in rows.values())
    with open(os.path.join(TR, 'rows.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for i, r in sorted(rows.items(), key=lambda x: x[1]['date']): f.write(json.dumps(dict(r, item=i), ensure_ascii=False) + '\n')
    json.dump(res, open(os.path.join(TR, 'tally.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'sheet': sheet, 'tally': tally}[sys.argv[1]]()
