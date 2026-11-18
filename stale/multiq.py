"""Does the decision model's cost edge survive one prompt with all the questions? (stale/PLAN_multiq.md)

Usage  py -m stale.multiq kev [port]     Kev re-timed on the missing2 cascade cells, no score cache -> stale/out/multiq_kev.json
       py -m stale.multiq qwen [port]    Qwen3.5-4B instruct, all of a passage's questions in one prompt -> stale/out/multiq_qwen.json
       py -m stale.multiq result         -> stale/out/multiq_result.json
"""
import collections, json, math, os, random, statistics as st, sys, time, urllib.request
from stale.missing import auroc, save
from stale.missing2 import DOCS, F as F2, load, shortlist
from stale.triage import TEMPLATE

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
F = {'kev': os.path.join(OUT, 'multiq_kev.json'), 'qwen': os.path.join(OUT, 'multiq_qwen.json'),
     'result': os.path.join(OUT, 'multiq_result.json')}
SEED, DRAWS = 20261125, 2000
T975 = {9: 2.262}


def cells():
    """[(doc, piece index, piece text, [cases])] in a fixed order: the missing2 cascade cells."""
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; RR = load(F2['RERANK']); out = []
    for d in D:
        need = collections.defaultdict(list)
        for c in d['cases']:
            for i in shortlist(RR[d['doc']], c): need[i].append(c)
        out += [(d['doc'], i, d['pieces'][i], need[i]) for i in sorted(need)]
    return out


def kev(port='9995'):
    from policywatch.scorer import Server, qid
    S = Server(f'http://127.0.0.1:{port}'); assert S.served == 'Kev-4B-Q8_0.gguf', S.served
    out = load(F['kev']); t0 = time.time()
    for n, (doc, i, text, cs) in enumerate(cells(), 1):
        key = f'{doc}|{i}'
        if key in out: continue
        qs = [TEMPLATE.format(c) for c in cs]
        t = time.perf_counter(); ans = S.ask(text, {qid(q): q for q in qs}); sec = time.perf_counter() - t
        out[key] = {'sec': round(sec, 3), 'k': len(cs), 'p': {c: ans[qid(q)] for c, q in zip(cs, qs)}}
        save(F['kev'], out)
        if n % 25 == 0: print(f'[kev {n} {time.time() - t0:.0f}s]', flush=True)
    print('kev done')


def grammar(k):
    lines = ' '.join(f'"{j}: " ans "\\n"' for j in range(1, k + 1))
    return f'root ::= {lines}\nans ::= "yes" | "no"\n'


def prompt(text, qs):
    listed = '\n'.join(f'{j}. {q}' for j, q in enumerate(qs, 1))
    return (f'TEXT:\n{text}\n\nAnswer each question below about the text with yes or no.\n{listed}\n'
            f'Answer with one line per question in the form "1: yes".')


def lo(top):
    py = sum(math.exp(x['logprob']) for x in top if x['token'].strip().lower() == 'yes')
    pn = sum(math.exp(x['logprob']) for x in top if x['token'].strip().lower() == 'no')
    floor = math.exp(min(x['logprob'] for x in top))
    return round(math.log(py or floor) - math.log(pn or floor), 6)


def qwen_multi(port, text, qs):
    body = json.dumps({'messages': [{'role': 'user', 'content': prompt(text, qs)}], 'temperature': 0,
                       'max_tokens': 8 * len(qs) + 16, 'logprobs': True, 'top_logprobs': 20, 'cache_prompt': False,
                       'grammar': grammar(len(qs)), 'chat_template_kwargs': {'enable_thinking': False}}).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions', body, {'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=3600) as r: d = json.loads(r.read())
    toks = d['choices'][0]['logprobs']['content']
    ans = [t for t in toks if t['token'].strip().lower() in ('yes', 'no')]
    return {'text': d['choices'][0]['message']['content'], 'lo': [lo(t['top_logprobs']) for t in ans] if len(ans) == len(qs) else None}


def qwen(port='9996'):
    out = load(F['qwen']); t0 = time.time()
    for n, (doc, i, text, cs) in enumerate(cells(), 1):
        key = f'{doc}|{i}'
        if key in out: continue
        qs = [TEMPLATE.format(c) for c in cs]
        t = time.perf_counter(); r = qwen_multi(port, text, qs); sec = time.perf_counter() - t
        out[key] = {'sec': round(sec, 3), 'k': len(cs), 'ok': r['lo'] is not None,
                    'lo': dict(zip(cs, r['lo'])) if r['lo'] is not None else {c: 0.0 for c in cs},
                    'reply': r['text'] if r['lo'] is None else ''}
        save(F['qwen'], out)
        if n % 25 == 0: print(f'[qwen {n} {time.time() - t0:.0f}s]', flush=True)
    print('qwen done')


def tci(x):
    m = st.mean(x); s = st.stdev(x) / math.sqrt(len(x)); t = T975[len(x) - 1]
    return [round(m - t * s, 3), round(m + t * s, 3)]


def reading(ci, a, b):
    return f'{a} better' if ci[0] > 0 else f'{b} better' if ci[1] < 0 else 'no difference shown'


def result():
    D = json.load(open(DOCS, encoding='utf-8'))['docs']; RR = load(F2['RERANK'])
    K2, Q2 = load(F2['KEV']), load(F2['QWEN']); M = load(F['qwen']); KT = load(F['kev'])
    cs = {a: {} for a in ('CASCADE_KEV', 'CASCADE_QWEN', 'QWEN_MULTI')}
    for d in D:
        doc = d['doc']
        for a in cs: cs[a][doc] = {}
        for c in d['cases']:
            sl = shortlist(RR[doc], c)
            cs['CASCADE_KEV'][doc][c] = max(K2[doc][i][c] for i in sl)
            cs['CASCADE_QWEN'][doc][c] = max(Q2[doc][str(i)][c] for i in sl)
            cs['QWEN_MULTI'][doc][c] = max(M[f'{doc}|{i}']['lo'][c] for i in sl)
    au = {a: {d['doc']: auroc([cs[a][d['doc']][c] for c in d['positives']], [cs[a][d['doc']][c] for c in d['negatives']]) for d in D} for a in cs}
    rng = random.Random(SEED)

    def comp(a, b):
        diffs = [au[a][d['doc']] - au[b][d['doc']] for d in D]; ci = tci(diffs); bs = []
        for _ in range(DRAWS):
            tot = 0
            for d in D:
                P = [rng.choice(d['positives']) for _ in d['positives']]; N = [rng.choice(d['negatives']) for _ in d['negatives']]
                x, y = cs[a][d['doc']], cs[b][d['doc']]
                tot += auroc([x[c] for c in P], [x[c] for c in N]) - auroc([y[c] for c in P], [y[c] for c in N])
            bs.append(tot / len(D))
        bs.sort()
        return {'point': round(st.mean(diffs), 3), 't95_docs': ci, 'boot95_within_docs': [round(bs[int(.025 * DRAWS)], 3), round(bs[int(.975 * DRAWS) - 1], 3)],
                'docs_above_0': sum(x > 0 for x in diffs), 'reading': reading(ci, a, b)}

    n_cells = sum(v['k'] for v in M.values()); bad = sum(v['k'] for v in M.values() if not v['ok'])
    kev_s = sum(v['sec'] for v in KT.values()); kev_q = sum(v['k'] for v in KT.values())
    mul_s = sum(v['sec'] for v in M.values())
    R = (mul_s / n_cells) / (kev_s / kev_q)
    cost_reading = "Kev's cost edge holds" if R >= 1.5 else 'edge gone' if R <= 1.0 else 'edge reduced'
    res = {'docs': [{'doc': d['doc'], **{a: round(au[a][d['doc']], 3) for a in au}} for d in D],
           'auroc': {a: round(st.mean(au[a].values()), 3) for a in au},
           'KEV_minus_MULTI': comp('CASCADE_KEV', 'QWEN_MULTI'), 'QWEN_minus_MULTI': comp('CASCADE_QWEN', 'QWEN_MULTI'),
           'format': {'cells': n_cells, 'failed_cells': bad, 'failed_passages': sum(not v['ok'] for v in M.values()),
                      'unreliable': bad > .05 * n_cells},
           'cost': {'kev_s_per_question': round(kev_s / kev_q, 3), 'kev_seconds': round(kev_s), 'kev_questions': kev_q,
                    'multi_s_per_question': round(mul_s / n_cells, 3), 'multi_seconds': round(mul_s),
                    'single_qwen_s_per_question_missing2': 6.046, 'R_multi_over_kev': round(R, 3), 'reading': cost_reading},
           'agreement_kev_vs_new_kev_timing_run': round(st.mean(abs(KT[f'{doc}|{i}']['p'][c] - K2[doc][i][c])
                                                               for doc, i, _, cl in cells() for c in cl), 4)}
    if res['format']['unreliable']: res['KEV_minus_MULTI']['reading'] = res['QWEN_minus_MULTI']['reading'] = 'void: format unreliable'
    with open(F['result'], 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'docs'}, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'kev': kev, 'qwen': qwen, 'result': result}[cmd](*sys.argv[2:])
