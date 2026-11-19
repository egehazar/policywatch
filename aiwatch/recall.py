"""Recall sample (PLAN_ledger.md, addendum 2): a random sample of the AI-vocabulary updates the keyword arm did not
alert on, rated blind like the ledger cards, so recall can be estimated, not just precision.

  py -m aiwatch.recall cards      -> out/ledger/batch_r_*.txt, recall_key.jsonl
  py -m aiwatch.recall tally      -> out/ledger/recall_tally.json (after both raters; Kev columns once scored)
"""
import collections, hashlib, json, math, os, random, sys
from aiwatch.backtest import DELTA, cands
from aiwatch.ledger import LED, QUESTION, BATCH, GRANTISH, cut

SEED, N = 41, 120
CARD_TOTAL = 20000        # characters per card; further blocks are listed as not shown (counted in the tally)


def strata():
    """Distinct AI-vocabulary updates (identical block sets once) -> (keyword-alerted, not keyword-alerted)."""
    by = collections.OrderedDict()
    for c in cands(): by.setdefault((c['coll'], c['svc'], c['doc'], c['commit'], c['date']), []).append(c)
    seen, alerted, rest = set(), [], []
    for k, blocks in by.items():
        ident = frozenset((b['old_text'], b['new_text']) for b in blocks)
        if ident in seen: continue
        seen.add(ident)
        u = {'coll': k[0], 'svc': k[1], 'doc': k[2], 'commit': k[3], 'date': k[4],
             'blocks': [(b['old_text'], b['new_text']) for b in blocks]}
        (alerted if any(b['regex_alert'] for b in blocks) else rest).append(u)
    return alerted, rest


def cards():
    _, rest = strata()
    rest.sort(key=lambda u: (u['coll'], u['commit'], u['doc']))
    S = random.Random(SEED).sample(rest, N)
    key, txt = [], []
    for i, u in enumerate(S):
        cid = 'R' + hashlib.sha256(f'{SEED}|{u["coll"]}|{u["commit"]}|{u["doc"]}'.encode()).hexdigest()[:6]
        parts, n, hidden = [], 0, 0
        for o, nw in u['blocks']:
            p = f'BEFORE:\n{cut(o)}\n\nAFTER:\n{cut(nw)}'
            if parts and n + len(p) > CARD_TOTAL: hidden += 1; continue
            parts.append(p); n += len(p)
        if hidden: parts.append(f'[... {hidden} more changed passages not shown ...]')
        key.append(dict({k: v for k, v in u.items() if k != 'blocks'}, card=cid, batch=i // BATCH,
                        blocks=len(u['blocks']), hidden=hidden))
        txt.append((i // BATCH, f'=== CARD {cid} ===\n' + '\n\n'.join(parts) + '\n'))
    with open(os.path.join(LED, 'recall_key.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for k in key: f.write(json.dumps(k, ensure_ascii=False) + '\n')
    for b in sorted({b for b, _ in txt}):
        with open(os.path.join(LED, f'batch_r_{b:02d}.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(QUESTION + '\n\nAnswer as JSON lines: {"card": "<id>", "label": "<NEW|WIDER|SAME|NO|UNCLEAR>", '
                    '"scope": "<THIRD|GENERAL|NARROW|->", "quote": "<sentence>"}\n\n')
            f.write('\n'.join(t for bb, t in txt if bb == b))
    print(f'{len(S)} of {len(rest)} updates without a keyword alert sampled; '
          f'{sum(k["hidden"] > 0 for k in key)} cards with passages not shown -> {LED}')


def wilson(x, n, z=1.96):
    if n == 0: return (None, None)
    p = x / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def tally():
    from aiwatch.ledger import answers
    K = [json.loads(l) for l in open(os.path.join(LED, 'recall_key.jsonl'), encoding='utf-8')]
    A1, A2 = answers('claude'), answers('gpt')
    miss = [k['card'] for k in K if k['card'] not in A1 or k['card'] not in A2]
    if miss: raise SystemExit(f'{len(miss)} recall cards unanswered')
    alerted, rest = strata()
    v = [k for k in K if A1[k['card']]['label'] in GRANTISH and A2[k['card']]['label'] in GRANTISH]
    lo, hi = wilson(len(v), len(K))
    found = sum(json.loads(l)['verified'] for l in open(os.path.join(LED, 'verified.jsonl'), encoding='utf-8')
                if json.loads(l).get('regex_alert'))
    est = len(v) / len(K) * len(rest)
    res = {'population_without_keyword_alert': len(rest), 'sampled': len(K), 'verified_in_sample': len(v),
           'cards_with_hidden_passages': sum(k['hidden'] > 0 for k in K),
           'est_grants_missed_by_keywords': round(est, 1),
           'est_missed_ci95': [round(lo * len(rest), 1), round(hi * len(rest), 1)],
           'keyword_verified_grants': found,
           'keyword_recall_est': round(found / (found + est), 3) if found + est else None,
           'keyword_recall_ci95': [round(found / (found + hi * len(rest)), 3), round(found / (found + lo * len(rest)), 3)],
           'verified_in_sample_cards': [dict(k, quote=A1[k['card']]['quote']) for k in v]}
    # Kev: every Kev alert is rated in the ledger (phases 1-2), so its verified grants are a count, not an estimate.
    VR = [json.loads(l) for l in open(os.path.join(LED, 'verified.jsonl'), encoding='utf-8')]
    KEY = [json.loads(l) for l in open(os.path.join(LED, 'cards_key.jsonl'), encoding='utf-8')]
    if any(k.get('kev_alert') for k in KEY):
        kf = sum(bool(r.get('kev_alert')) for r in VR)
        kev_only = sum(bool(r.get('kev_alert')) and not r.get('regex_alert') for r in VR)
        res['kev_verified_grants'] = kf
        res['kev_only_verified_grants'] = kev_only
        # total grants: keyword-alerted verified + the estimate for the rest (which Kev-only grants are part of)
        tot, tot_lo, tot_hi = found + max(est, kev_only), found + max(lo * len(rest), kev_only), found + max(hi * len(rest), kev_only)
        res['kev_recall_est'] = round(kf / tot, 3)
        res['kev_recall_ci95'] = [round(kf / tot_hi, 3), round(kf / tot_lo, 3)]
    else:
        res['kev'] = 'not yet: Kev scoring or phase 2 not finished'
    json.dump(res, open(os.path.join(LED, 'recall_tally.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'verified_in_sample_cards'}, indent=1))


if __name__ == '__main__':
    {'cards': cards, 'tally': tally}[sys.argv[1]]()
