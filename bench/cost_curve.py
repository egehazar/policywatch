"""The cost curve, measured on an idle CPU (bench/PLAN_cost_curve.md): seconds per passage-question for Kev-4B
(/v1/systemone: one request per passage with all its questions) and for its base family Qwen3.5-4B instruct (one
chat request per passage and question), at 1, 2, 4, 8 and 16 questions per passage.

The relocation write-ups fit Kev's cost (about 6.9 s per 1,500-character passage plus 1.05 s per question) from part
B's timings, which shared the CPU with other jobs. This measures it alone. Every call gets a passage no earlier call
saw, so neither server can reuse a cached prefix across calls. Within a passage the instruct model is asked its
questions one after another with cache_prompt on: if llama.cpp could reuse the passage's prefix for that model, its
later questions would be much faster than its first; the plan records what that would look like.

plan               draw 60 passages of part B (stale/out/heldout_docs.json, 1,300-1,500 characters, at most one per
                   document while possible) and 16 case questions; levels assigned 12 passages each, order shuffled
                   -> bench/out/cost_plan.json
kev  <port>        -> bench/out/cost_kev.jsonl   (resumable; one line per call)
qwen <port>        -> bench/out/cost_qwen.jsonl  (resumable; one line per question)
result             -> bench/out/cost_result.json
Usage  py -m bench.cost_curve plan|kev 9995|qwen 9996|result
"""
import json, os, random, statistics as st, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
SEED = 20261115; LEVELS = (1, 2, 4, 8, 16); PER = 12; LO, HI = 1300, 1500
F = {k: os.path.join(OUT, f'cost_{k}') for k in ('plan.json', 'kev.jsonl', 'qwen.jsonl', 'result.json')}


def plan():
    from stale.relocate import psha
    D = json.load(open(os.path.join(ROOT, 'stale', 'out', 'heldout_docs.json'), encoding='utf-8'))['docs']
    rng = random.Random(SEED)
    qs = sorted({q for d in D for q in d['questions']}); qs = rng.sample(qs, max(LEVELS))
    pool = [(d['doc'], i, p) for d in D for i, p in enumerate(d['pieces']) if LO <= len(p) <= HI]
    rng.shuffle(pool); seen_doc, seen_text, pick = set(), set(), []
    for rnd in (0, 1):                                    # one per document first, then fill
        for doc, i, p in pool:
            if len(pick) == PER * len(LEVELS): break
            if p in seen_text or (rnd == 0 and doc in seen_doc): continue
            pick.append((doc, i, p)); seen_doc.add(doc); seen_text.add(p)
    assert len(pick) == PER * len(LEVELS), f'only {len(pick)} passages in {LO}-{HI} characters'
    levels = [q for q in LEVELS for _ in range(PER)]; rng.shuffle(levels)
    items = [{'id': f'c{k:02d}', 'doc': doc, 'piece': i, 'chars': len(p), 'text': p, 'q': q,
              'questions': rng.sample(qs, q)} for k, ((doc, i, p), q) in enumerate(zip(pick, levels))]
    os.makedirs(OUT, exist_ok=True)
    with open(F['plan.json'], 'w', encoding='utf-8') as f:
        json.dump({'seed': SEED, 'questions': qs, 'pieces_sha': psha([it['text'] for it in items]), 'items': items}, f, indent=1)
    print(len(items), 'calls planned; chars', min(it['chars'] for it in items), '-', max(it['chars'] for it in items))


def done(path):
    return {json.loads(l)['key'] for l in open(path, encoding='utf-8')} if os.path.exists(path) else set()


def append(path, row):
    with open(path, 'a', encoding='utf-8') as f: f.write(json.dumps(row) + '\n')


def kev(port='9995'):
    from policywatch.scorer import Server
    S = Server(f'http://127.0.0.1:{port}'); assert S.served == 'Kev-4B-Q8_0.gguf', S.served
    P = json.load(open(F['plan.json'], encoding='utf-8')); ds = done(F['kev.jsonl'])
    for it in P['items']:
        if it['id'] in ds: continue
        t = time.perf_counter(); ans = S.ask(it['text'], {f'q{k}': q for k, q in enumerate(it['questions'])}); sec = time.perf_counter() - t
        append(F['kev.jsonl'], {'key': it['id'], 'q': it['q'], 'chars': it['chars'], 'sec': round(sec, 3), 'answers': ans})
        print(it['id'], it['q'], round(sec, 2), flush=True)


def qwen(port='9996'):
    from stale.relocate2 import qwen_ask
    P = json.load(open(F['plan.json'], encoding='utf-8')); ds = done(F['qwen.jsonl'])
    for it in P['items']:
        for k, q in enumerate(it['questions']):
            key = f'{it["id"]}|{k}'
            if key in ds: continue
            t = time.perf_counter(); a = qwen_ask(port, it['text'], q); sec = time.perf_counter() - t
            append(F['qwen.jsonl'], {'key': key, 'item': it['id'], 'k': k, 'q': it['q'], 'chars': it['chars'], 'sec': round(sec, 3), 'lo': a['lo']})
        print(it['id'], it['q'], flush=True)


def fit(xs, ys):
    mx, my = st.mean(xs), st.mean(ys); b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def result():
    K = [json.loads(l) for l in open(F['kev.jsonl'], encoding='utf-8')]
    Q = [json.loads(l) for l in open(F['qwen.jsonl'], encoding='utf-8')]
    a, b = fit([r['q'] for r in K], [r['sec'] for r in K])
    first = [r['sec'] for r in Q if r['k'] == 0]; later = [r['sec'] for r in Q if r['k'] > 0]
    per_q = st.median(r['sec'] for r in Q)
    lv = {}
    for q in LEVELS:
        kq = [r['sec'] for r in K if r['q'] == q]; qq = [r['sec'] for r in Q if r['q'] == q]
        if not kq or not qq: continue
        k_pq = st.median(kq) / q; q_pq = st.median([sum(r['sec'] for r in Q if r['item'] == i) / q for i in {r['item'] for r in Q if r['q'] == q}])
        lv[q] = {'kev_s_per_call_median': round(st.median(kq), 2), 'kev_s_per_question': round(k_pq, 2),
                 'qwen_s_per_question': round(q_pq, 2), 'qwen_over_kev': round(q_pq / k_pq, 2)}
    res = {'calls_kev': len(K), 'questions_qwen': len(Q),
           'kev_fit': {'s_per_passage': round(a, 2), 's_per_question': round(b, 3)},
           'qwen_s_per_question_median': round(per_q, 2),
           'qwen_first_question_median': round(st.median(first), 2), 'qwen_later_questions_median': round(st.median(later), 2) if later else None,
           'qwen_later_over_first': round(st.median(later) / st.median(first), 3) if later else None,
           'levels': lv,
           'break_even_questions': round(a / (per_q - b), 2) if per_q > b else None,
           'ceiling_ratio': round(per_q / b, 1) if b > 0 else None}
    with open(F['result.json'], 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1]
    {'plan': plan, 'result': result}.get(cmd, lambda: None)()
    if cmd == 'kev': kev(*sys.argv[2:])
    if cmd == 'qwen': qwen(*sys.argv[2:])
