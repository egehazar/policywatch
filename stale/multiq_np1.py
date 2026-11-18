"""Addendum 1 to stale/PLAN_multiq.md: Kev re-timed on a 1-slot server (stale/PLAN_multiq_addendum1.md).

Usage  py -m stale.multiq_np1 kev [port]   -> stale/out/multiq_kev_np1.json  (server: -np 1 -c 16384 -t 6)
       py -m stale.multiq_np1 result       -> stale/out/multiq_np1_result.json
"""
import json, os, statistics as st, sys, time
from stale.missing import save
from stale.missing2 import load
from stale.multiq import F as FM, cells
from stale.triage import TEMPLATE

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
F = {'kev': os.path.join(OUT, 'multiq_kev_np1.json'), 'result': os.path.join(OUT, 'multiq_np1_result.json')}
MULTI_S_PER_Q = 1.785          # stale/out/multiq_result.json, cost.multi_s_per_question


def kev(port='9997'):
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
        if n % 25 == 0: print(f'[kev np1 {n} {time.time() - t0:.0f}s]', flush=True)
    print('kev np1 done')


def result():
    K1, K4 = load(F['kev']), load(FM['kev'])
    keys = [f'{d}|{i}' for d, i, _, _ in cells()]
    assert all(k in K1 for k in keys), 'run incomplete'
    agree = st.mean(abs(K1[k]['p'][c] - K4[k]['p'][c]) for k in keys for c in K4[k]['p'])
    q = sum(K1[k]['k'] for k in keys); s = sum(K1[k]['sec'] for k in keys); k1 = s / q
    R1 = MULTI_S_PER_Q / k1
    reading = 'void' if agree > .01 else "Kev's cost edge holds" if R1 >= 1.5 else 'edge gone' if R1 <= 1.0 else 'edge reduced'
    res = {'agreement_mean_abs_dp_vs_4_slots': round(agree, 4), 'kev1_seconds': round(s), 'kev1_questions': q,
           'kev1_s_per_question': round(k1, 3), 'kev4_s_per_question_main_run': round(sum(K4[k]['sec'] for k in keys) / q, 3),
           'multi_s_per_question_main_run': MULTI_S_PER_Q, 'R1_multi_over_kev1': round(R1, 3), 'reading': reading}
    with open(F['result'], 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'kev': kev, 'result': result}[cmd](*sys.argv[2:])
