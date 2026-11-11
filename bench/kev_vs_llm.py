"""Decision model vs ordinary LLM on the same diffs (eval/PREREG_kev_vs_llm.md, pre-registered 22:28:07Z).

Arms over the frozen r20 test (35 updates x 70 v1 questions):
  KEV       |p_new - p_old| from the r20 run (ranking); timing re-measured here, one request at a time.
  LLM-DIFF  Qwen3.5-4B (instruct, Q8_0) reads OLD and NEW and lists the question numbers whose answer changed.
  LLM-QA    the same model answers all 70 questions (y-list) on OLD and on NEW separately; flips first.
Writes bench/out/<arm>.jsonl (resumable) and bench/out/result.json. Every request is timed; tokens from usage.

Usage  py -m bench.kev_vs_llm run-llm  <qwen_port> <frozen_dir>
       py -m bench.kev_vs_llm time-kev <kev_port>  <frozen_dir>
       py -m bench.kev_vs_llm scale-kev <kev_port> <frozen_dir>
       py -m bench.kev_vs_llm eval <frozen_dir>
"""
import json, os, random, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from policywatch.scorer import q_obj          # the exact Kev wrapper used in r20
from policywatch import evaluate

SEED = 20261111; KS = (25, 50, 100, 182)

HEAD = 'Each question asks: does the text state or clearly imply the following?'


def bank70():
    with open(os.path.join(ROOT, 'data', 'bank_v1_r20.json'), encoding='utf-8') as f: return json.load(f)


def qlist(bank):
    return '\n'.join(f'{i}. {b["title"]}' for i, b in enumerate(bank))


def prompt_diff(old, new, bank):
    return (f'Below are two versions of an excerpt from a platform\'s Terms of Service or Privacy Policy ("[...]" marks '
            f'omitted text).\n\nOLD:\n{old}\n\nNEW:\n{new}\n\nQUESTIONS. {HEAD}\n{qlist(bank)}\n\n'
            'List the numbers of the questions whose yes/no answer differs between OLD and NEW, most certain first, as a '
            'JSON list of integers, for example [12, 3]. Write [] if none. Output only the JSON list.')


def prompt_qa(text, bank):
    return (f'Below is an excerpt from a platform\'s Terms of Service or Privacy Policy ("[...]" marks omitted text).\n\n'
            f'TEXT:\n{text}\n\nQUESTIONS. {HEAD}\n{qlist(bank)}\n\n'
            'Answer each question y if the text states or clearly implies it, otherwise n (including when the text is '
            'silent). Output only a JSON list of the numbers you answer y, for example [3, 17]. Write [] if none.')


def chat(port, content, max_tokens=400):
    body = json.dumps({'messages': [{'role': 'user', 'content': content}], 'temperature': 0, 'max_tokens': max_tokens,
                       'chat_template_kwargs': {'enable_thinking': False}}).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions', body, {'Content-Type': 'application/json'})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=3600) as r: d = json.loads(r.read())
    return d['choices'][0]['message']['content'], d.get('usage', {}), round(time.time() - t0, 2)


def parse_ints(text, n=70):
    m = re.search(r'\[[^\[\]]*\]', text or '')
    if not m: return None
    try: xs = json.loads(m.group(0))
    except ValueError: return None
    out = []
    for x in xs:
        if isinstance(x, int) and 0 <= x < n and x not in out: out.append(x)
    return out


def load_pairs(frozen):
    with open(os.path.join(frozen, 'pairs.jsonl'), encoding='utf-8') as f: return [json.loads(l) for l in f]


def done_ids(path):
    if not os.path.exists(path): return set()
    with open(path, encoding='utf-8') as f: return {json.loads(l)['id'] for l in f if l.strip()}


def append(path, rec):
    with open(path, 'a', encoding='utf-8') as f: f.write(json.dumps(rec) + '\n')


def run_llm(port, frozen):
    os.makedirs(OUT, exist_ok=True); bank = bank70(); P = load_pairs(frozen)
    pd, pq = os.path.join(OUT, 'llm_diff.jsonl'), os.path.join(OUT, 'llm_qa.jsonl')
    dd, dq = done_ids(pd), done_ids(pq)
    for p in P:
        if p['id'] not in dd:
            txt, use, sec = chat(port, prompt_diff(p['old_region'], p['new_region'], bank))
            append(pd, {'id': p['id'], 'raw': txt, 'parsed': parse_ints(txt), 'usage': use, 'sec': sec}); print(p['id'], 'diff', sec, flush=True)
        for side in ('old', 'new'):
            k = f"{p['id']}|{side}"
            if k in dq: continue
            txt, use, sec = chat(port, prompt_qa(p[side + '_region'], bank))
            append(pq, {'id': k, 'raw': txt, 'parsed': parse_ints(txt), 'usage': use, 'sec': sec}); print(k, 'qa', sec, flush=True)


def kev_post(port, text, qs):
    body = json.dumps({'state': text, 'questions': {f'q{k:02d}': q_obj(q) for k, q in enumerate(qs)}}).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/v1/systemone', body, {'Content-Type': 'application/json'})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=3600) as r: d = json.loads(r.read())
    return {k: round(v['noul'], 4) for k, v in d['answers'].items()}, d.get('usage'), round(time.time() - t0, 2)


def time_kev(port, frozen):
    """One request at a time (no concurrency), the 70 v1 questions, every r20 state: wall time per state."""
    os.makedirs(OUT, exist_ok=True); qs = [b['q'] for b in bank70()]; pk = os.path.join(OUT, 'kev_timing.jsonl'); dk = done_ids(pk)
    for p in load_pairs(frozen):
        for side in ('old', 'new'):
            k = f"{p['id']}|{side}"
            if k in dk: continue
            ps, use, sec = kev_post(port, p[side + '_region'], qs)
            append(pk, {'id': k, 'sec': sec, 'usage': use, 'p': ps}); print(k, 'kev', sec, flush=True)


def scale_kev(port, frozen):
    """Timing only: banks of 25, 70, 101 and 500 questions on 5 fixed states (500 = v2 questions with numbered
    variants appended; never scored for accuracy)."""
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'bank.json'), encoding='utf-8') as f: v2 = [b['q'] for b in json.load(f)]
    big = (v2 * 5)[:500]; big = [q if i < len(v2) else q.replace('?', f' (variant {i // len(v2)})?') for i, q in enumerate(big)]
    banks = {25: v2[:25], 70: v2[:70], 101: v2, 500: big}
    P = load_pairs(frozen); rng = random.Random(SEED); states = rng.sample([(p['id'], p['old_region']) for p in P], 5)
    ps = os.path.join(OUT, 'kev_scale.jsonl'); ds = done_ids(ps)
    for sid, text in states:
        for n, qs in banks.items():
            k = f'{sid}|{n}'
            if k in ds: continue
            _, use, sec = kev_post(port, text, qs)
            append(ps, {'id': k, 'n_questions': n, 'chars': len(text), 'sec': sec, 'usage': use}); print(k, sec, flush=True)


def read(path):
    with open(path, encoding='utf-8') as f: return [json.loads(l) for l in f if l.strip()]


def eval_cmd(frozen):
    pairs, arms, G, kev = evaluate.load(frozen)
    items = [f"{p['id']}|{k}" for p in pairs for k in range(70)]; pos = [i for i in items if G[i] == 1]
    amb = [i for i in items if G[i] is None]
    rng = random.Random(SEED)
    def tail(head):
        rest = [i for i in items if i not in set(head)]; rng.shuffle(rest); return head + rest
    d = {i: abs(kev[i.split('|')[0] + '|new'][f"q{int(i.split('|')[1]):02d}"] - kev[i.split('|')[0] + '|old'][f"q{int(i.split('|')[1]):02d}"]) for i in items}
    orders = {'KEV': sorted(items, key=lambda i: (-d[i], i))}
    D = {r['id']: r for r in read(os.path.join(OUT, 'llm_diff.jsonl'))}
    head = []
    for p in pairs:
        r = D.get(p['id'])
        if r and r['parsed']: head += [f"{p['id']}|{k}" for k in r['parsed']]
    # interleave by position within each update's list: all first mentions, then all second mentions, ...
    per = {p['id']: [f"{p['id']}|{k}" for k in ((D.get(p['id']) or {}).get('parsed') or [])] for p in pairs}
    inter = [lst[j] for j in range(max([len(l) for l in per.values()] + [0])) for lst in per.values() if j < len(lst)]
    orders['LLM-DIFF'] = tail(inter)
    Qa = {r['id']: r for r in read(os.path.join(OUT, 'llm_qa.jsonl'))}
    flips = []
    for p in pairs:
        o, n = Qa.get(p['id'] + '|old'), Qa.get(p['id'] + '|new')
        if o and n and o['parsed'] is not None and n['parsed'] is not None:
            flips += [f"{p['id']}|{k}" for k in range(70) if (k in o['parsed']) != (k in n['parsed'])]
    rng2 = random.Random(SEED); rng2.shuffle(flips); orders['LLM-QA'] = tail(flips)
    res = {'gold1': len(pos), 'ambiguous': len(amb), 'recall_at': {}, 'recall_at_amb_as_pos': {}}
    for a, o in orders.items():
        res['recall_at'][a] = {k: sum(G.get(i) == 1 for i in o[:k]) for k in KS}
        res['recall_at_amb_as_pos'][a] = {k: sum(G.get(i) != 0 for i in o[:k]) for k in KS}
    res['llm_diff_unparsed'] = sum(1 for r in D.values() if r['parsed'] is None)
    res['llm_qa_unparsed'] = sum(1 for r in Qa.values() if r['parsed'] is None)
    res['llm_diff_listed'] = len(inter); res['llm_qa_flips'] = len(flips)
    sec = lambda rs: round(sum(r['sec'] for r in rs) / max(len(pairs), 1), 1)
    kt = read(os.path.join(OUT, 'kev_timing.jsonl')) if os.path.exists(os.path.join(OUT, 'kev_timing.jsonl')) else []
    res['sec_per_update'] = {'KEV': sec(kt) if len(kt) == 2 * len(pairs) else None, 'LLM-DIFF': sec(list(D.values())), 'LLM-QA': sec(list(Qa.values()))}
    r182 = res['recall_at']; c = res['sec_per_update']
    if None in c.values() or len(D) < len(pairs) or len(Qa) < 2 * len(pairs):
        res['reading'] = 'INCOMPLETE'
    else:
        k, l = r182['KEV'][182], r182['LLM-DIFF'][182]
        if (k >= l and c['KEV'] <= c['LLM-DIFF']) or (k >= l + 3 and c['KEV'] <= 2 * c['LLM-DIFF']): res['reading'] = 'DECISION MODEL WINS'
        elif l >= k + 3 and c['LLM-DIFF'] <= 2 * c['KEV']: res['reading'] = 'LLM WINS'
        else: res['reading'] = 'NO CLEAR WINNER'
    sc = os.path.join(OUT, 'kev_scale.jsonl')
    if os.path.exists(sc):
        by = {}
        for r in read(sc): by.setdefault(r['n_questions'], []).append(r['sec'])
        res['kev_scale_sec'] = {n: round(sum(v) / len(v), 1) for n, v in sorted(by.items())}
    print(json.dumps(res, indent=1))
    with open(os.path.join(OUT, 'result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'run-llm': run_llm(sys.argv[2], sys.argv[3])
    elif c == 'time-kev': time_kev(sys.argv[2], sys.argv[3])
    elif c == 'scale-kev': scale_kev(sys.argv[2], sys.argv[3])
    elif c == 'eval': eval_cmd(sys.argv[2])
