"""Kev with a short question layout (eval/PREREG_short_layout.md): the r20 questions with no option descriptions.

Kev's systemone template (GGUF tokenizer.chat_template.systemone) renders each question as
  <|fim_middle|>{instructions}<|box_start|>yes[: description]<|box_end|><|box_start|>no[: description]<|box_end|><|fim_suffix|>
and everything after the shared state is processed once per question. The r20 wrapper (policywatch/scorer.py q_obj)
adds "Yes, this is true of the text." / "No, this is not true of the text." as descriptions. KEV-SHORT omits the
criteria, so the template shows bare "yes" and "no" (and the server's default option order). Instructions unchanged.

Usage  py -m bench.short_layout time <kev_port> <frozen_dir>   -> bench/out/kev_short.jsonl (resumable)
       py -m bench.short_layout eval <frozen_dir>              -> bench/out/short_result.json
"""
import json, os, random, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out'); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from policywatch import evaluate
from bench.kev_vs_llm import bank70, load_pairs, read, append, done_ids, SEED, KS

ADOPT_RECALL = 19          # KEV's recall@182 on r20 was 20 (bench/out/result.json); at most one change lost
ADOPT_CPU = 0.7            # and at most 0.7x KEV's CPU per update (179.8 s)


def q_short(q):
    return {'type': 'noul', 'instructions': f'Answer this question about the text: {q}'}


def post(port, text, qs):
    body = json.dumps({'state': text, 'questions': {f'q{k:02d}': q_short(q) for k, q in enumerate(qs)}}).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/systemone', body, {'Content-Type': 'application/json'})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=3600) as r: d = json.loads(r.read())
    return {k: round(v['noul'], 4) for k, v in d['answers'].items()}, d.get('usage'), round(time.time() - t0, 2)


def time_short(port, frozen):
    """One request at a time, the 70 v1 questions, every r20 state (as bench time-kev)."""
    os.makedirs(OUT, exist_ok=True); qs = [b['q'] for b in bank70()]; pk = os.path.join(OUT, 'kev_short.jsonl'); dk = done_ids(pk)
    for p in load_pairs(frozen):
        for side in ('old', 'new'):
            k = f"{p['id']}|{side}"
            if k in dk: continue
            ps, use, sec = post(port, p[side + '_region'], qs)
            append(pk, {'id': k, 'sec': sec, 'usage': use, 'p': ps}); print(k, 'short', sec, flush=True)


def recall(order, G):
    return ({k: sum(G.get(i) == 1 for i in order[:k]) for k in KS}, {k: sum(G.get(i) != 0 for i in order[:k]) for k in KS})


def eval_cmd(frozen):
    pairs, arms, G, kev = evaluate.load(frozen)
    items = [f"{p['id']}|{k}" for p in pairs for k in range(70)]
    S = {r['id']: r for r in read(os.path.join(OUT, 'kev_short.jsonl'))}
    if len(S) < 2 * len(pairs): raise SystemExit(f'incomplete: {len(S)} of {2 * len(pairs)} states')
    dq = lambda P, i: abs(P[i.split('|')[0] + '|new'][f"q{int(i.split('|')[1]):02d}"] - P[i.split('|')[0] + '|old'][f"q{int(i.split('|')[1]):02d}"])
    Ps = {k: v['p'] for k, v in S.items()}
    d_kev = {i: dq(kev, i) for i in items}; d_short = {i: dq(Ps, i) for i in items}
    o_kev = sorted(items, key=lambda i: (-d_kev[i], i)); o_short = sorted(items, key=lambda i: (-d_short[i], i))
    B = json.load(open(os.path.join(OUT, 'result.json'), encoding='utf-8'))
    res = {'gold1': B['gold1'], 'ambiguous': B['ambiguous']}
    for name, o in (('KEV', o_kev), ('KEV-SHORT', o_short)):
        r, ra = recall(o, G); res.setdefault('recall_at', {})[name] = r; res.setdefault('recall_at_amb_as_pos', {})[name] = ra
    for a in ('LLM-DIFF', 'LLM-QA'):
        res['recall_at'][a] = {int(k): v for k, v in B['recall_at'][a].items()}          # JSON keys are strings
        res['recall_at_amb_as_pos'][a] = {int(k): v for k, v in B['recall_at_amb_as_pos'][a].items()}
    cpu_short = round(sum(r['sec'] for r in S.values()) / len(pairs), 1)
    res['sec_per_update'] = {**B['sec_per_update'], 'KEV-SHORT': cpu_short}
    res['input_tokens_per_state'] = {'KEV': None, 'KEV-SHORT': round(sum((r['usage'] or {}).get('input_tokens', 0) for r in S.values()) / len(S))}
    kt = read(os.path.join(OUT, 'kev_timing.jsonl'))
    res['input_tokens_per_state']['KEV'] = round(sum((r['usage'] or {}).get('input_tokens', 0) for r in kt) / len(kt))
    # rank agreement of the two layouts' |dp| (Spearman, ties averaged)
    def ranks(d):
        s = sorted(items, key=lambda i: d[i]); r = {}; j = 0
        while j < len(s):
            k = j
            while k + 1 < len(s) and d[s[k + 1]] == d[s[j]]: k += 1
            for m in range(j, k + 1): r[s[m]] = (j + k) / 2
            j = k + 1
        return r
    ra_, rb_ = ranks(d_kev), ranks(d_short); n = len(items); ma = sum(ra_.values()) / n; mb = sum(rb_.values()) / n
    cov = sum((ra_[i] - ma) * (rb_[i] - mb) for i in items); va = sum((ra_[i] - ma) ** 2 for i in items); vb = sum((rb_[i] - mb) ** 2 for i in items)
    res['spearman_KEV_vs_SHORT_dp'] = round(cov / (va * vb) ** .5, 4)
    k182 = res['recall_at']['KEV-SHORT'][182]; c = res['sec_per_update']
    res['adopt_short'] = bool(k182 >= ADOPT_RECALL and cpu_short <= ADOPT_CPU * c['KEV'])
    # the bench reading rule (eval/PREREG_kev_vs_llm.md), applied to KEV-SHORT: a second test, pre-registered in
    # eval/PREREG_short_layout.md after the first reading was known
    l = res['recall_at']['LLM-DIFF'][182]
    if (k182 >= l and cpu_short <= c['LLM-DIFF']) or (k182 >= l + 3 and cpu_short <= 2 * c['LLM-DIFF']): rd = 'DECISION MODEL WINS'
    elif l >= k182 + 3 and c['LLM-DIFF'] <= 2 * cpu_short: rd = 'LLM WINS'
    else: rd = 'NO CLEAR WINNER'
    res['bench_rule_reading_short_vs_llm_diff'] = rd
    q = res['recall_at']['LLM-QA'][182]
    res['short_vs_llm_qa'] = {'recall182': [k182, q], 'cpu': [cpu_short, c['LLM-QA']],
                              'short_at_least_as_good_on_both': bool(k182 >= q and cpu_short <= c['LLM-QA'])}
    print(json.dumps(res, indent=1))
    with open(os.path.join(OUT, 'short_result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'time': time_short(sys.argv[2], sys.argv[3])
    elif c == 'eval': eval_cmd(sys.argv[2])
