"""Relocation, hardened (stale/PREREG_relocate2.md): the relocation test's 200 points against stronger arms, and a
proposed quote from Kev.

Same points, pieces, questions and gold as stale/relocate.py (stale/out/reloc_docs.json, the first 200 of the fixed
order). KEV, BM25, BGE and QNN scores are the hashed ones from that test. New arms rank the same pieces:
  QWEN       Qwen3.5-4B (instruct, Q8_0, thinking off; Kev's base family) asked the same question of each piece.
             One zero-shot prompt. Score: log P(yes) - log P(no) over its first answer token (top 20 logprobs, case and
             spaces ignored); an answer outside the top 20 gets the 20th logprob, an upper bound.
  RERANK     bge-reranker-v2-m3 cross-encoder logit for (case title, piece), max 1,024 tokens (no piece is cut).
  KEV_SHORT  Kev-4B with the short question layout of eval/RESULT_short_layout.md (no option descriptions).
Secondary, computed from scores already on disk (no new model call): CASCADE_<RERANK|BM25> = Kev's ranking of the
arm's top 10 pieces, keeping every piece tied with the 10th (Kev reads a quarter of a 40-piece document).
Part C, the proposed quote: Kev's top piece is cut into units (sentences, list items; under 5 words joined to the
next). Kev (r20 wrapper) is asked the point's case question of each unit; the top unit is the proposed quote.

Usage  py -m stale.relocate2 qwen [port]            -> stale/out/reloc_qwen.json
       <venv python> -m stale.relocate2 rerank      -> stale/out/reloc_rerank.json
       py -m stale.relocate2 kevshort [port]        -> stale/out/reloc_kevshort.json
       py -m stale.relocate2 quote [port]           -> stale/out/reloc_quote.json
       py -m stale.relocate2 eval                   -> stale/out/reloc2_result.json
"""
import collections, json, math, os, random, re, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.relocate import sample, psha, hit, bm25, KS, SEED
from stale.match import words, grams, coverage

N = 200; TOPK = 10; UNIT_MIN = 5; MATCH = .5
F = {a: os.path.join(OUT, f'reloc_{a}.json') for a in ('qwen', 'rerank', 'kevshort', 'quote')}


def needed():
    D, need, chosen = sample(N)
    return [d for d in D['docs'] if d['doc'] in need], need, chosen


def load(path):
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}


def save(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(obj, f)
    os.replace(tmp, path)


# ---------------------------------------------------------------- QWEN
def qwen_ask(port, piece, q):
    body = json.dumps({'messages': [{'role': 'user', 'content': f'TEXT:\n{piece}\n\nQuestion: {q}\nAnswer yes or no.'}],
                       'temperature': 0, 'max_tokens': 1, 'logprobs': True, 'top_logprobs': 20, 'cache_prompt': True,
                       'chat_template_kwargs': {'enable_thinking': False}}).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions', body, {'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=3600) as r: d = json.loads(r.read())
    top = d['choices'][0]['logprobs']['content'][0]['top_logprobs']
    py = sum(math.exp(x['logprob']) for x in top if x['token'].strip().lower() == 'yes')
    pn = sum(math.exp(x['logprob']) for x in top if x['token'].strip().lower() == 'no')
    floor = math.exp(min(x['logprob'] for x in top))       # an answer outside the top 20 has at most this probability
    return {'lo': round(math.log(py or floor) - math.log(pn or floor), 6), 'mass': round(py + pn, 6),
            'yes': py > 0, 'no': pn > 0, 'top': top[0]['token']}


def qwen(port='9996'):
    docs, need, _ = needed(); out = load(F['qwen']); t0 = time.time()
    for k, d in enumerate(docs, 1):
        if d['doc'] in out: continue
        qs = need[d['doc']]; rows = []; miss = 0; t1 = time.time()
        for piece in d['pieces']:            # piece first: the server reuses the piece's prefix across questions
            row = {}
            for q in qs:
                r = qwen_ask(port, piece, q); miss += not (r['yes'] or r['no']); row[q] = r
            rows.append(row)
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': rows, 'sec': round(time.time() - t1, 1), 'no_yes_no': miss}
        save(F['qwen'], out)
        print(f'[{k}/{len(docs)} {time.time() - t0:.0f}s] {d["doc"]}: {len(d["pieces"])} x {len(qs)}, no yes/no token {miss}', flush=True)


# ---------------------------------------------------------------- RERANK
def rerank():
    os.environ.setdefault('HF_HUB_OFFLINE', '1'); os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
    import torch
    from sentence_transformers import CrossEncoder
    m = CrossEncoder('BAAI/bge-reranker-v2-m3', max_length=1024, device='cpu', revision='953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e')
    tok = m.tokenizer; docs, need, _ = needed(); out = load(F['rerank']); t0 = time.time()
    for k, d in enumerate(docs, 1):
        if d['doc'] in out: continue
        case = dict(zip(d['questions'], d['cases'])); qs = need[d['doc']]
        pairs = [(case[q], p) for q in qs for p in d['pieces']]
        long = sum(1 for a, b in pairs if len(tok(a, b)['input_ids']) > 1024)
        t1 = time.time(); s = m.predict(pairs, batch_size=16, activation_fn=torch.nn.Identity(), show_progress_bar=False)
        n = len(d['pieces'])
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': {q: [round(float(x), 5) for x in s[i * n:(i + 1) * n]] for i, q in enumerate(qs)},
                         'sec': round(time.time() - t1, 1), 'truncated_pairs': long}
        save(F['rerank'], out)
        print(f'[{k}/{len(docs)} {time.time() - t0:.0f}s] {d["doc"]}: {n} x {len(qs)}, truncated {long}', flush=True)


# ---------------------------------------------------------------- KEV_SHORT
def kevshort(port='9995'):
    from bench.short_layout import post
    from policywatch.scorer import Server
    assert Server(f'http://127.0.0.1:{port}').served == 'Kev-4B-Q8_0.gguf', 'port does not serve Kev-4B Q8'
    docs, need, _ = needed(); out = load(F['kevshort']); t0 = time.time()
    for k, d in enumerate(docs, 1):
        if d['doc'] in out: continue
        qs = need[d['doc']]; rows = []; sec = 0.0
        for piece in d['pieces']:
            ps, _, s = post(port, piece, qs); sec += s
            rows.append({q: ps[f'q{i:02d}'] for i, q in enumerate(qs)})
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'scores': rows, 'sec': round(sec, 1)}
        save(F['kevshort'], out)
        print(f'[{k}/{len(docs)} {time.time() - t0:.0f}s] {d["doc"]}: {len(d["pieces"])} x {len(qs)}', flush=True)


# ---------------------------------------------------------------- Part C: the proposed quote
SENT = re.compile(r'(?<=[.!?;])\s+(?=[\[("“A-Z0-9*_-])')


def units(piece):
    """Sentences and list items of a piece, in order; a unit under UNIT_MIN words is joined to the next one."""
    raw = [s.strip() for line in piece.split('\n') for s in SENT.split(line) if s.strip()]
    out, carry = [], ''
    for s in raw:
        s = (carry + ' ' + s).strip() if carry else s
        if len(words(s)) < UNIT_MIN: carry = s; continue
        out.append(s); carry = ''
    if carry:
        if out: out[-1] = out[-1] + ' ' + carry
        else: out.append(carry)
    return out


def top_piece(scores):
    best = max(scores); return scores.index(best)          # ties: the earliest piece (fixed before running)


def tied_mean(scores, m):
    """Expected match of the top unit when ties at the top are broken uniformly at random."""
    best = max(scores); t = [i for i, x in enumerate(scores) if x == best]
    return sum(m[i] for i in t) / len(t)


def overlap(a_ws, b_ws):
    """Share of a's word 6-grams found in b (a under 6 words: found whole or not)."""
    return coverage(a_ws, grams(a_ws), ' ' + ' '.join(b_ws) + ' ', grams(b_ws))


def matches(unit, quote):
    u = words(unit); q = words(quote, quote=True)
    return overlap(q, u) >= MATCH or overlap(u, q) >= MATCH


def kev_scores():
    K = json.load(open(os.path.join(OUT, 'reloc_kev.json'), encoding='utf-8'))
    return lambda d, q: [s[q] for s in K[d]['scores']]


def quote(port='9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    docs, need, chosen = needed(); ks = kev_scores()
    S = Scorer(Server(f'http://127.0.0.1:{port}'), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', 'port does not serve Kev-4B Q8'
    out = load(F['quote']); t0 = time.time()
    for k, d in enumerate(docs, 1):
        if d['doc'] in out: continue
        groups = {}                                  # Kev's top piece -> the questions whose top piece it is
        for it in d['items']:
            if it['point'] in chosen: groups.setdefault(top_piece(ks(d['doc'], it['question'])), set()).add(it['question'])
        res = {}; t1 = time.time()
        for i, qs in sorted(groups.items()):
            qs = sorted(qs); U = units(d['pieces'][i]); rows = []
            for u in U:
                ps = S.score(u, qs); rows.append({q: ps[qid(q)] for q in qs})
            res[str(i)] = {'units': U, 'scores': rows}
        out[d['doc']] = {'pieces_sha': psha(d['pieces']), 'pieces': res, 'sec': round(time.time() - t1, 1)}
        save(F['quote'], out)
        print(f'[{k}/{len(docs)} {time.time() - t0:.0f}s] {d["doc"]}: {len(groups)} top pieces, '
              f'{sum(len(v["units"]) for v in res.values())} units', flush=True)
    print('asked', S.asked, 'cache hits', S.hits)


# ---------------------------------------------------------------- evaluation
def boot(per, f, seed=SEED):
    """Mean of f(row) and its 95% cluster bootstrap interval over documents (2,000 draws, a fresh seed per call)."""
    rng = random.Random(seed); docs_ = sorted({r['doc'] for r in per}); by = {d: [r for r in per if r['doc'] == d] for d in docs_}
    ds = []
    for _ in range(2000):
        smp = [r for d in (rng.choice(docs_) for _ in docs_) for r in by[d]]
        ds.append(sum(f(r) for r in smp) / len(smp))
    ds.sort()
    return {'point': round(sum(f(r) for r in per) / len(per), 3), 'ci95': [round(ds[50], 3), round(ds[1949], 3)], 'raw': [ds[50], ds[1949]]}


def reading(ci, better, worse, none):
    return better if ci[0] > 0 else worse if ci[1] < 0 else none


def evaluate():
    docs, need, chosen = needed()
    K = json.load(open(os.path.join(OUT, 'reloc_kev.json'), encoding='utf-8'))
    B = json.load(open(os.path.join(OUT, 'reloc_base.json'), encoding='utf-8'))
    Q, R, KS_ = (json.load(open(F[a], encoding='utf-8')) for a in ('qwen', 'rerank', 'kevshort'))
    for name, A in (('QWEN', Q), ('RERANK', R), ('KEV_SHORT', KS_)):
        miss = [d['doc'] for d in docs if d['doc'] not in A]; assert not miss, f'{name} missing {miss[:3]}'
        bad = [d['doc'] for d in docs if A[d['doc']]['pieces_sha'] != psha(d['pieces'])]; assert not bad, f'{name} pieces changed {bad[:3]}'
    arm = {'KEV': lambda d, q: [s[q] for s in K[d]['scores']], 'QWEN': lambda d, q: [s[q]['lo'] for s in Q[d]['scores']],
           'RERANK': lambda d, q: R[d]['scores'][q], 'KEV_SHORT': lambda d, q: [s[q] for s in KS_[d]['scores']],
           'BM25': lambda d, q: B['BM25'][d][q], 'BGE': lambda d, q: B['BGE'][d][q], 'QNN': lambda d, q: B['QNN'][d][q]}

    def cascade(first):
        def f(d, q):
            s0 = arm[first](d, q); cut = sorted(s0, reverse=True)[min(TOPK, len(s0)) - 1]   # pieces tied with the 10th stay
            keep = {i for i, x in enumerate(s0) if x >= cut}; k = arm['KEV'](d, q)
            return [k[i] if i in keep else -1.0 for i in range(len(k))]
        return f
    for a in ('RERANK', 'BM25'): arm[f'CASCADE_{a}'] = cascade(a)
    per = []
    for d in docs:
        for it in d['items']:
            if it['point'] not in chosen: continue
            row = {'point': it['point'], 'doc': d['doc'], 'n_pieces': len(d['pieces'])}
            for a, f in arm.items():
                hk, rr = hit(f(d['doc'], it['question']), it['gold']); row[a] = {'hit': hk, 'rr': rr}
            per.append(row)
    assert len(per) == N
    names = list(arm)
    res = {'points': len(per), 'documents': len({r['doc'] for r in per}),
           'hit_at': {a: {k: round(sum(r[a]['hit'][k] for r in per) / N, 3) for k in KS} for a in names},
           'mrr': {a: round(sum(r[a]['rr'] for r in per) / N, 3) for a in names}}
    h1 = lambda a: (lambda r: r[a]['hit'][1])
    d_ = lambda a, b: (lambda r: r[a]['hit'][1] - r[b]['hit'][1])
    res['KEV_minus_QWEN'] = boot(per, d_('KEV', 'QWEN')); res['KEV_minus_RERANK'] = boot(per, d_('KEV', 'RERANK'))
    res['KEV_SHORT_minus_KEV'] = boot(per, d_('KEV_SHORT', 'KEV'))
    for a in ('RERANK', 'BM25'): res[f'CASCADE_{a}_minus_KEV'] = boot(per, d_(f'CASCADE_{a}', 'KEV'))
    cq = [c for d in docs for row in Q[d['doc']]['scores'] for c in row.values()]
    res['qwen_validity'] = {'cells': len(cq), 'no_yes_no_share': round(sum(not (c['yes'] or c['no']) for c in cq) / len(cq), 4),
                            'median_mass': round(sorted(c['mass'] for c in cq)[len(cq) // 2], 4),
                            'top_tokens': dict(collections.Counter(c['top'].strip().lower() for c in cq).most_common(5))}
    qwen_ok = res['qwen_validity']['no_yes_no_share'] <= .01 and res['qwen_validity']['median_mass'] >= .5
    res['reading'] = {
        'R1_base_family': 'INVALID (QWEN validity gate failed)' if not qwen_ok else reading(res['KEV_minus_QWEN']['raw'], 'DECISION MODEL BETTER THAN ITS BASE FAMILY', 'BASE LLM BETTER', 'NO DIFFERENCE SHOWN'),
        'R2_reranker': reading(res['KEV_minus_RERANK']['raw'], 'DECISION MODEL BETTER THAN THE RERANKER', 'RERANKER BETTER', 'NO DIFFERENCE SHOWN'),
        'R3_short_layout': 'KEV_SHORT USED' if res['KEV_SHORT_minus_KEV']['raw'][0] >= -.05 else 'R20 WRAPPER KEPT'}
    cells = sum(len(d['pieces']) * len(need[d['doc']]) for d in docs)
    res['cost_sec_per_cell'] = {'QWEN': round(sum(Q[d['doc']]['sec'] for d in docs) / cells, 3),
                                'RERANK': round(sum(R[d['doc']]['sec'] for d in docs) / cells, 3),
                                'KEV_SHORT': round(sum(KS_[d['doc']]['sec'] for d in docs) / cells, 3),
                                'KEV': round(16013 / 8270, 3)}   # first test: 16,013 s over the 8,270 cells it asked (116 cache hits)
    res['qwen_no_yes_no'] = sum(Q[d['doc']]['no_yes_no'] for d in docs)
    res['rerank_truncated_pairs'] = sum(R[d['doc']]['truncated_pairs'] for d in docs)
    res['cells'] = sum(len(d['pieces']) * len(need[d['doc']]) for d in docs)
    res['quote'] = quote_eval(docs, chosen) if os.path.exists(F['quote']) else None
    with open(os.path.join(OUT, 'reloc2_result.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': per}, f, indent=1)
    print(json.dumps(res, indent=1))


def quote_eval(docs, chosen):
    P = {int(json.loads(l)['point']): json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')}
    C = json.load(open(F['quote'], encoding='utf-8')); ks = kev_scores(); rows = []
    for d in docs:
        assert C[d['doc']]['pieces_sha'] == psha(d['pieces'])
        case = dict(zip(d['questions'], d['cases']))
        for it in d['items']:
            if it['point'] not in chosen: continue
            i = top_piece(ks(d['doc'], it['question'])); g = C[d['doc']]['pieces'][str(i)]
            U = g['units']; s = [r[it['question']] for r in g['scores']]; q = P[int(it['point'])]['quote']
            m = [matches(u, q) for u in U]; b = bm25(case[it['question']], U)
            rows.append({'kev_ties': s.count(max(s)), 'doc': d['doc'], 'piece_hit': i in it['gold'], 'units': len(U), 'any': any(m),
                         'KEV': tied_mean(s, m), 'BM25': tied_mean(b, m), 'FIRST': float(m[0]), 'RANDOM': sum(m) / len(U),
                         'kev_unit_words': len(words(U[top_piece(s)])), 'quote_words': len(words(q, quote=True))})
    hitrows = [r for r in rows if r['piece_hit']]
    out = {'points': len(rows), 'piece_hit': len(hitrows), 'mean_units': round(sum(r['units'] for r in rows) / len(rows), 1),
           'given_piece_hit': {a: round(sum(r[a] for r in hitrows) / len(hitrows), 3) for a in ('KEV', 'BM25', 'FIRST', 'RANDOM', 'any')},
           'kev_top_ties': sum(1 for r in hitrows if r['kev_ties'] > 1),
           'end_to_end_KEV': round(sum(r['KEV'] for r in rows if r['piece_hit']) / len(rows), 3),
           'KEV_minus_BM25_given_piece_hit': boot(hitrows, lambda r: r['KEV'] - r['BM25']),
           'median_words': {'kev_unit': sorted(r['kev_unit_words'] for r in rows)[len(rows) // 2],
                            'curator_quote': sorted(r['quote_words'] for r in rows)[len(rows) // 2]}}
    return out


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'qwen': qwen(*sys.argv[2:])
    elif c == 'rerank': rerank()
    elif c == 'kevshort': kevshort(*sys.argv[2:])
    elif c == 'quote': quote(*sys.argv[2:])
    elif c == 'eval': evaluate()
