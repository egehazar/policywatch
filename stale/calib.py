"""Exploratory (not pre-registered): are the decision model's probabilities calibrated, against its base family's?

Kev-4B is trained to return calibrated p(yes) for typed questions. Its base family's instruct model (Qwen3.5-4B,
the relocation QWEN arm) gives log P(yes) - log P(no) over its first answer token, read here as a probability with
the logistic function. Both scored every passage of parts A and B for every case. The states-the-case checks
(stale/RESULT_states_case.md) had blind raters (Claude models, not people) judge whether a passage states its case;
those judged passages, anchors left out, are the labels: YES = 1, NO or PARTLY = 0 (and, as a second reading,
PARTLY left out). The passages are mostly the methods' top picks plus random controls, not a random sample of
passages, so this describes the scores where a curator would look.
Reports per model: Brier score, log loss, expected calibration error over 10 equal-width bins, AUROC, and the bins.
Usage  py -m stale.calib   -> stale/out/calib.json
"""
import json, math, os, random
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
KEYS = (('audit_states', 'states_case_key'), ('audit_states2', 'states_case2_key'), ('audit_states3', 'states_case3_key'))
SRC = {'A': ('reloc_docs.json', 'reloc_kev.json', 'reloc_qwen.json'), 'B': ('heldout_docs.json', 'heldout_kev.json', 'heldout_qwen.json')}
SEED = 20261115
J = lambda f: json.load(open(os.path.join(OUT, f), encoding='utf-8'))


def labelled():
    """{(part, doc, piece, point): verdict} over the three rounds, anchors left out; one verdict per passage-point."""
    out = {}
    for d, k in KEYS:
        V = json.load(open(os.path.join(HERE, d, 'verdicts.json'), encoding='utf-8')); K = J(f'{k}.json')['cards']
        for cid, c in K.items():
            if c.get('kind') == 'ANCHOR' or cid not in V: continue
            out.setdefault((c['part'], c['doc'], c['piece'], c['point']), V[cid]['verdict'])
    return out


def scores():
    S = {}
    for part, (fd, fk, fq) in SRC.items():
        docs = J(fd)['docs']; K, Q = J(fk), J(fq)
        for d in docs:
            for it in d['items']:
                q = it['question']
                if d['doc'] not in K or d['doc'] not in Q or q not in K[d['doc']]['scores'][0]: continue   # not a scored point
                S[(part, d['doc'], it['point'])] = ([s[q] for s in K[d['doc']]['scores']], [s[q]['lo'] for s in Q[d['doc']]['scores']])
    return S


def auroc(pos, neg):
    return sum((x > y) + .5 * (x == y) for x in pos for y in neg) / (len(pos) * len(neg)) if pos and neg else None


def metrics(ps, ys):
    eps = 1e-6; n = len(ps)
    bins = [[] for _ in range(10)]
    for p, y in zip(ps, ys): bins[min(9, int(p * 10))].append((p, y))
    ece = sum(len(b) / n * abs(sum(p for p, _ in b) / len(b) - sum(y for _, y in b) / len(b)) for b in bins if b)
    return {'n': n, 'brier': round(sum((p - y) ** 2 for p, y in zip(ps, ys)) / n, 4),
            'log_loss': round(-sum(y * math.log(max(p, eps)) + (1 - y) * math.log(max(1 - p, eps)) for p, y in zip(ps, ys)) / n, 4),
            'ece': round(ece, 4), 'auroc': round(auroc([p for p, y in zip(ps, ys) if y], [p for p, y in zip(ps, ys) if not y]), 4),
            'mean_p': round(sum(ps) / n, 3), 'share_yes': round(sum(ys) / n, 3),
            'bins': [{'range': f'{k / 10:.1f}-{(k + 1) / 10:.1f}', 'n': len(b), 'mean_p': round(sum(p for p, _ in b) / len(b), 3),
                      'share_yes': round(sum(y for _, y in b) / len(b), 3)} for k, b in enumerate(bins) if b]}


def main():
    L = labelled(); S = scores(); rows = []
    for (part, doc, piece, point), v in L.items():
        kev, qwen = S[(part, doc, point)]
        rows.append({'v': v, 'kev': kev[piece], 'qwen': 1 / (1 + math.exp(-qwen[piece]))})
    res = {'note': 'exploratory; labels are blind LLM raters (states the case), anchors left out; Qwen p = logistic(log-odds of yes vs no)'}
    for name, keep, lab in (('YES_vs_rest', lambda r: True, lambda r: int(r['v'] == 'YES')),
                            ('YES_vs_NO', lambda r: r['v'] in ('YES', 'NO'), lambda r: int(r['v'] == 'YES'))):
        R = [r for r in rows if keep(r)]
        res[name] = {m: metrics([r[m] for r in R], [lab(r) for r in R]) for m in ('kev', 'qwen')}
        d = [(r['kev'] - lab(r)) ** 2 - (r['qwen'] - lab(r)) ** 2 for r in R]; rng = random.Random(SEED)
        bs = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(4000))
        res[name]['brier_kev_minus_qwen'] = {'point': round(sum(d) / len(d), 4), 'ci95': [round(bs[100], 4), round(bs[3899], 4)]}
    with open(os.path.join(OUT, 'calib.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    for name in ('YES_vs_rest', 'YES_vs_NO'):
        for m in ('kev', 'qwen'):
            x = res[name][m]; print(name, m, {k: x[k] for k in ('n', 'brier', 'log_loss', 'ece', 'auroc', 'mean_p', 'share_yes')})
    for m in ('kev', 'qwen'): print(m, [(b['range'], b['n'], b['mean_p'], b['share_yes']) for b in res['YES_vs_rest'][m]['bins']])


if __name__ == '__main__':
    main()
