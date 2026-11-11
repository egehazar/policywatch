"""Accuracy on the frozen r20 test (decision-serving/play/reviewq/out): 35 real Open Terms Archive updates x 70
questions, gold = both blind LLM raters (Sonnet 5.5, Opus 5.5) flip their answer between the old and new region.

This module only DESCRIBES the tool's accuracy on that test. The pre-registered verdict of the test is rq.py eval
alone and is quoted, never recomputed here.
"""
import json, os
from .report import esc


def load(frozen):
    pairs = [json.loads(l) for l in open(os.path.join(frozen, 'pairs.jsonl'), encoding='utf-8')]
    arms = json.load(open(os.path.join(frozen, 'arms.json')))
    rd = os.path.join(frozen, 'raters'); key = json.load(open(os.path.join(rd, 'key.json')))
    ans = {r: {} for r in ('A', 'B')}
    for r in ans:
        for b, ids in key.items():
            d = json.load(open(os.path.join(rd, f'{r}_{b}.json')))
            for pi, ps in enumerate(ids, 1):
                ys = set(d[f'P{pi}']); ans[r][ps] = ''.join('y' if k in ys else 'n' for k in range(70))
    G = {}
    for p in pairs:
        for k in range(70):
            fl = [ans[r][p['id'] + '|old'][k] != ans[r][p['id'] + '|new'][k] for r in ans]
            G[f"{p['id']}|{k}"] = 1 if all(fl) else 0 if not any(fl) else None
    kev = {json.loads(l)['id']: json.loads(l)['p'] for l in open(os.path.join(frozen, 'kev.jsonl'), encoding='utf-8') if l.strip()}
    return pairs, arms, G, kev


def recall_at(order, G, k):
    pos = sum(1 for g in G.values() if g == 1)
    return sum(1 for i in order[:k] if G.get(i) == 1) / max(pos, 1)


def q95(order, G):
    pos = [i for i, g in G.items() if g == 1]; need = -(-95 * len(pos) // 100); hit = 0
    for n, it in enumerate(order, 1):
        hit += G.get(it) == 1
        if hit >= need: return n
    return len(order)


def run(frozen, tau):
    pairs, arms, G, kev = load(frozen)
    items = [f"{p['id']}|{k}" for p in pairs for k in range(70)]
    missing = [p['id'] for p in pairs if f"{p['id']}|old" not in kev or f"{p['id']}|new" not in kev]
    if missing: return {'status': f'INCOMPLETE: {len(missing)} pairs not scored'}
    d = {i: abs(kev[i.split('|')[0] + '|new'][f"q{int(i.split('|')[1]):02d}"] - kev[i.split('|')[0] + '|old'][f"q{int(i.split('|')[1]):02d}"]) for i in items}
    pos = [i for i in items if G[i] == 1]; lab = [i for i in items if G[i] is not None]
    kev_order = sorted(items, key=lambda i: (-d[i], i))
    ruled = sorted(set(arms['RULE']), key=lambda i: (-d[i], i))
    rule_order = ruled + [i for i in kev_order if i not in set(ruled)]
    bge_order = sorted(items, key=lambda i: (-arms['BGE'][i], i))
    CH = set(arms['CH'])
    half = len(set(arms['CH'])) // 2; ks = sorted({25, 50, 100, half, len(set(arms['CH']))})
    out = {'status': 'ok', 'pairs': len(pairs), 'items': len(items), 'gold_changes': len(pos),
           'chunk_hash': {'reviews': len(CH), 'recall': round(sum(i in CH for i in pos) / len(pos), 3),
                          'wasted_share': round(sum(G[i] == 0 for i in CH if G[i] is not None) / max(sum(G[i] is not None for i in CH), 1), 3)},
           'kev_recall_at': {k: round(recall_at(kev_order, G, k), 3) for k in ks},
           'kev_rule_first_recall_at': {k: round(recall_at(rule_order, G, k), 3) for k in ks},
           'bge_recall_at': {k: round(recall_at(bge_order, G, k), 3) for k in ks},
           'q95': {'kev': q95(kev_order, G), 'kev_rule_first': q95(rule_order, G), 'bge': q95(bge_order, G)}}
    th = {}
    for t in (.1, .2, .3, .5):
        fl = [i for i in items if d[i] >= t]; fl_lab = [i for i in fl if G[i] is not None]
        amb = [i for i in items if G[i] is None]
        th[t] = {'flagged': len(fl), 'per_update': round(len(fl) / len(pairs), 2),
                 'recall': round(sum(G[i] == 1 for i in fl) / len(pos), 3),
                 'precision': round(sum(G[i] == 1 for i in fl_lab) / max(len(fl_lab), 1), 3),
                 # ambiguous items (one rater flips) counted both ways, since dropping them flatters both numbers
                 'recall_if_ambiguous_are_changes': round(sum(G[i] != 0 for i in fl) / max(len(pos) + len(amb), 1), 3),
                 'precision_if_ambiguous_are_not': round(sum(G[i] == 1 for i in fl) / max(len(fl), 1), 3)}
    out['threshold'] = th; out['ambiguous'] = sum(G[i] is None for i in items)
    rp = os.path.join(frozen, 'result.json')     # the pre-registered verdict (rq.py eval), quoted, never recomputed
    if os.path.exists(rp):
        with open(rp, encoding='utf-8') as f: R = json.load(f)
        out['preregistered'] = {k: R.get(k) for k in ('verdict', 'Q95_KEV', 'CH', 'Q95_KEV_over_CH', 'CH_keep_share', 'CH_recall', 'gold1')}
    out['missed_at_tau'] = [{'item': i, 'dp': round(d[i], 3)} for i in pos if d[i] < tau]
    t = th[tau] if tau in th else None
    rows = ''.join(f'<tr><td>{k}</td><td>{out["kev_recall_at"][k]:.0%}</td><td>{out["kev_rule_first_recall_at"][k]:.0%}</td>'
                   f'<td>{out["bge_recall_at"][k]:.0%}</td></tr>' for k in ks)
    pre = out.get('preregistered')
    out['html'] = ((f'<p class="note"><b>Pre-registered verdict:</b> {esc(pre["verdict"])}. The bar, fixed before scoring: '
                    f'95% of real changes within the first {pre["CH"] // 2 if isinstance(pre.get("CH"), int) else "?"} answers '
                    f'(half of what the usual rule re-checks). The tool needed {esc(pre["Q95_KEV"])}.</p>' if pre and pre.get('verdict') else
                    '<p class="note">The pre-registered verdict of this test is not on disk yet.</p>')
                   + f'<p>Test: {len(pairs)} real updates to Terms of Service and Privacy Policies (Open Terms Archive), '
                   f'{len(items)} (update, question) pairs. An answer counts as changed when two independent LLM raters '
                   f'(not humans) both flip it, judging only the changed excerpt, not the whole document: {len(pos)} did, and '
                   f'{out["ambiguous"]} more were flipped by one rater only.</p>'
                   f'<p>The usual rule (re-check answers whose top-5 retrieved paragraphs changed) re-checks {len(CH)} answers, '
                   f'{out["chunk_hash"]["wasted_share"]:.0%} of them unchanged, and catches {out["chunk_hash"]["recall"]:.0%} '
                   f'of the real changes.</p><table><tr><th>Re-check the top …</th><th>by model movement</th>'
                   f'<th>numbers first, then movement</th><th>by retrieval similarity</th></tr>{rows}</table>'
                   + (f'<p>At the report threshold ({tau}): {t["per_update"]} answers flagged per update, '
                      f'{t["recall"]:.0%} of real changes caught, {t["precision"]:.0%} of flags real. Counting the one-rater '
                      f'items against the tool: {t["recall_if_ambiguous_are_changes"]:.0%} caught, '
                      f'{t["precision_if_ambiguous_are_not"]:.0%} of flags real.</p>' if t else '')
                   + '<p class="sm mut">n is small; LLM raters, not humans; one model. Treat these as a description of '
                     'this test, not a guarantee.</p>')
    return out
