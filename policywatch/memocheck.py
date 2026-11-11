"""Recall against human write-ups: Open Terms Archive memos (eval/memo_targets.json, frozen before scoring).

A memo is CAUGHT if, in any of its matched real updates, a target question is flagged (|dp| >= tau) or ranked in
that update's top 5. Coverage gaps (no bank question fits) and rewrites (not scored) are reported separately.

Variants (all fixed before scoring): primary = my targets with bank v2; v1 = my targets and ranks restricted to the 70
questions of bank v1 (a v1 miss stays a miss: Fable r23); fable = Fable 5.2's independent mapping; union = either.
"""
import json, os
from . import archive

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.join(HERE, '..', 'eval')
V1 = 70


def _load(name):
    with open(os.path.join(EVAL, name), encoding='utf-8') as f: return json.load(f)


def memo_updates(archive_dir):
    T = _load('memo_targets.json')['memos']
    want = {(m['platform'], m['doc'], d) for m in T for d in m['commits']}
    us = []
    for plat, doc in {(p, d) for p, d, _ in want}:
        us += [u for u in archive.updates(archive_dir, docs=(doc,), platforms=[plat]) if (plat, doc, u.date) in want]
    return T, us


def _chance(recs, targets, bank):
    """P(caught) if the update's ranking were random: a target lands in the top max(5, number of flags) of n.
    'broad' is caught by any flag, so its chance is 1 whenever anything was flagged."""
    from math import comb
    miss = 1.0
    for r in recs:
        n = len(r['questions']); m = max(5, sum(x['dp'] >= r['tau'] for x in r['questions']))
        if targets == 'broad':
            p = 1.0 if any(x['dp'] >= r['tau'] for x in r['questions']) else 0.0
        else:
            k = len(targets); p = 1 - comb(n - k, m) / comb(n, m) if n >= m else 1.0
        miss *= 1 - p
    return round(1 - miss, 3)


def _judge(recs, targets, bank, restrict=None, strict=False):
    """recs: scored records of one memo. -> (caught, detail). strict: a target must be FLAGGED (no top-5 rescue)."""
    hit = False; detail = []
    for r in recs:
        qs = [x for x in r['questions'] if restrict is None or x['q'] in restrict]
        flags = [x for x in qs if x['dp'] >= r['tau']]
        if targets == 'broad':
            hit |= bool(flags); detail.append({'date': r['date'], 'flags': len(flags)}); continue
        for t in targets:
            if restrict is not None and bank[t]['q'] not in restrict: continue
            q = next(x for x in qs if x['q'] == bank[t]['q']); rank = qs.index(q) + 1
            ok = q['dp'] >= r['tau'] or (rank <= 5 and not strict); hit |= ok
            detail.append({'date': r['date'], 'target': bank[t]['title'][:60], 'dp': q['dp'], 'rank': rank, 'caught': ok})
    return hit, detail


def check(out_dir, T, bank):
    recs = {}
    for f in os.listdir(os.path.join(out_dir, 'updates')):
        if not f.endswith('.json'): continue
        with open(os.path.join(out_dir, 'updates', f), encoding='utf-8') as fh: r = json.load(fh)
        recs[(r['platform'], r['doc'], r['date'])] = r
    fable = _load('memo_targets_fable.json'); v1q = {b['q'] for b in bank[:V1]}
    uniq = []
    for m in T:
        if (m['memo'], m['doc']) not in [(u['memo'], u['doc']) for u in uniq]: uniq.append(m)
    rows = []
    for i, m in enumerate(uniq, 1):
        rs = [recs.get((m['platform'], m['doc'], d)) for d in m['commits']]
        row = {'id': f'M{i}', 'memo': m['memo'], 'platform': m['platform'], 'doc': m['doc'],
               'kinds': [r['kind'] if r else 'not scanned' for r in rs]}
        scored = [r for r in rs if r and r['kind'] == 'scored']
        ft = fable.get(f'M{i}')
        union = 'broad' if m['targets'] == 'broad' else sorted(set(m['targets']) | set(ft if isinstance(ft, list) else []))
        variants = {'primary': (m['targets'], None), 'v1': (m['targets'], v1q), 'fable': (ft, None), 'union': (union, None),
                    'strict': ('excluded' if m['targets'] == 'broad' else m['targets'], None)}
        for name, (tg, restrict) in variants.items():
            if tg == 'excluded':
                row[name] = 'excluded'
            elif tg == [] or (tg != 'broad' and restrict is not None and not [t for t in tg if bank[t]['q'] in restrict]):
                row[name] = 'coverage gap'
            elif not scored and 'rewrite' in row['kinds']:
                row[name] = 'missed'     # the frozen rule: rewrites (not scored) count as NOT caught (review 11-11)
            elif not scored:
                row[name] = 'not scored (' + ', '.join(row['kinds']) + ')'
            else:
                hit, det = _judge(scored, tg, bank, restrict, strict=(name == 'strict'))
                row[name] = 'CAUGHT' if hit else 'missed'
                if name == 'primary': row['detail'] = det; row['chance'] = _chance(scored, tg, bank)
        row['result'] = row['primary']
        rows.append(row)

    def summ(name):
        return {'caught': sum(r[name] == 'CAUGHT' for r in rows), 'judged': sum(r[name] in ('CAUGHT', 'missed') for r in rows),
                'coverage_gaps': sum(r[name] == 'coverage gap' for r in rows), 'not_scored': sum(r[name].startswith('not scored') for r in rows)}
    summary = {'memos': len(rows), **summ('primary'), 'variants': {v: summ(v) for v in ('v1', 'fable', 'union', 'strict')},
               'chance_expected': round(sum(r.get('chance', 0) for r in rows if r['primary'] in ('CAUGHT', 'missed')), 2),
               'broad_memos': sum(m['targets'] == 'broad' for m in uniq)}
    return {'summary': summary, 'rows': rows}


def run(archive_dir, out_dir, bank, analyze_one):
    T, us = memo_updates(archive_dir)
    done = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(out_dir, 'updates'))} if os.path.isdir(os.path.join(out_dir, 'updates')) else set()
    for u in us:
        if u.key not in done: analyze_one(u)
    res = check(out_dir, T, bank)
    with open(os.path.join(out_dir, 'memo_check.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    return res
