"""Recall against human write-ups: Open Terms Archive memos (eval/memo_targets.json, frozen before scoring).

A memo is CAUGHT if, in any of its matched real updates, a target question is flagged (|dp| >= tau) or ranked in
that update's top 5. Coverage gaps (no bank question fits) and rewrites (not scored) are reported separately.
"""
import json, os
from . import archive

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.join(HERE, '..', 'eval')


def memo_updates(archive_dir):
    with open(os.path.join(EVAL, 'memo_targets.json'), encoding='utf-8') as f: T = json.load(f)['memos']
    want = {(m['platform'], m['doc'], d) for m in T for d in m['commits']}
    us = []
    for plat, doc in {(p, d) for p, d, _ in want}:
        us += [u for u in archive.updates(archive_dir, docs=(doc,), platforms=[plat]) if (plat, doc, u.date) in want]
    return T, us


def check(out_dir, T, bank):
    recs = {}
    for f in os.listdir(os.path.join(out_dir, 'updates')):
        with open(os.path.join(out_dir, 'updates', f), encoding='utf-8') as fh: r = json.load(fh)
        recs[(r['platform'], r['doc'], r['date'])] = r
    rows = []
    for m in T:
        rs = [recs.get((m['platform'], m['doc'], d)) for d in m['commits']]
        row = {'memo': m['memo'], 'platform': m['platform'], 'doc': m['doc'], 'kinds': [r['kind'] if r else 'not scanned' for r in rs]}
        scored = [r for r in rs if r and r['kind'] == 'scored']
        if m['targets'] == []:
            row['result'] = 'coverage gap'
        elif not scored:
            row['result'] = 'not scored (' + ', '.join(row['kinds']) + ')'
        else:
            hit = False; detail = []
            for r in scored:
                flags = [x for x in r['questions'] if x['dp'] >= r['tau']]
                if m['targets'] == 'broad':
                    hit |= bool(flags); detail.append({'date': r['date'], 'flags': len(flags)})
                else:
                    for t in m['targets']:
                        q = next(x for x in r['questions'] if x['q'] == bank[t]['q'])
                        rank = r['questions'].index(q) + 1
                        ok = q['dp'] >= r['tau'] or rank <= 5; hit |= ok
                        detail.append({'date': r['date'], 'target': bank[t]['title'][:60], 'dp': q['dp'], 'rank': rank, 'caught': ok})
            row['result'] = 'CAUGHT' if hit else 'missed'; row['detail'] = detail
        rows.append(row)
    judged = [r for r in rows if r['result'] in ('CAUGHT', 'missed')]
    summary = {'memos': len(rows), 'caught': sum(r['result'] == 'CAUGHT' for r in rows), 'judged': len(judged),
               'coverage_gaps': sum(r['result'] == 'coverage gap' for r in rows),
               'not_scored': sum(r['result'].startswith('not scored') for r in rows)}
    return {'summary': summary, 'rows': rows}


def run(archive_dir, out_dir, bank, analyze_one):
    T, us = memo_updates(archive_dir)
    done = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(out_dir, 'updates'))} if os.path.isdir(os.path.join(out_dir, 'updates')) else set()
    for u in us:
        if u.key not in done: analyze_one(u)
    res = check(out_dir, T, bank)
    with open(os.path.join(out_dir, 'memo_check.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    return res
