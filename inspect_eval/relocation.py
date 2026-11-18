"""The relocation test as an Inspect AI task: where does a document state a ToS;DR case now?

Each sample is one approved ToS;DR point. The model is asked, for every passage of the document's current text, the
same yes/no question the repo's own harness asks (stale/relocate2.py, qwen_ask), and the passages are ranked by
log P(yes) - log P(no) over the first answer token (top 20 logprobs). Gold = the passage(s) holding the curator's own
quote. Scores: hit@1/@3/@5 and reciprocal rank of the best-ranked gold passage, ties broken uniformly at random in
expectation (stale/relocate.py, hit).

Run (llama.cpp server with an OpenAI-compatible endpoint; RUN.md has the model files and flags):
  inspect eval inspect_eval/relocation.py --model llama-cpp-python/qwen --model-base-url http://127.0.0.1:9996/v1 \
      --max-connections 1 -T samples=A -T first=40
"""
import json
import math
import os
from math import comb

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageUser, GenerateConfig, ModelOutput, get_model
from inspect_ai.scorer import Score, Target, mean, scorer, stderr
from inspect_ai.solver import Generate, TaskState, solver

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
KS = (1, 3, 5)
PROMPT = 'TEXT:\n{passage}\n\nQuestion: {question}\nAnswer yes or no.'          # stale/relocate2.py, qwen_ask
CONFIG = GenerateConfig(temperature=0, max_tokens=1, logprobs=True, top_logprobs=20,
                        extra_body={'chat_template_kwargs': {'enable_thinking': False}, 'cache_prompt': True})


def _jsonl(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def _documents():
    return {d['document']: d['passages'] for d in _jsonl('documents.jsonl')}


def dataset(samples='A', first=0):
    rows = [p for p in _jsonl('points.jsonl') if p['sample'] in samples.split(',')]
    if first: rows = [p for p in rows if p['rank'] < int(first)]          # the first N of each sample's fixed order
    return [Sample(id=p['id'], input=p['question'], target=[str(g) for g in p['gold']],
                   metadata={k: p[k] for k in ('sample', 'rank', 'point', 'service', 'document', 'case_title')})
            for p in rows]


def log_odds(output: ModelOutput):
    """log P(yes) - log P(no) over the first token, case and spaces ignored; an answer outside the top 20 gets the
    20th logprob (an upper bound). Same as stale/relocate2.py, qwen_ask."""
    top = output.choices[0].logprobs.content[0].top_logprobs
    py = sum(math.exp(t.logprob) for t in top if t.token.strip().lower() == 'yes')
    pn = sum(math.exp(t.logprob) for t in top if t.token.strip().lower() == 'no')
    floor = math.exp(min(t.logprob for t in top))
    return {'lo': round(math.log(py or floor) - math.log(pn or floor), 6), 'mass': round(py + pn, 6)}


@solver
def score_passages():
    docs = _documents()

    async def solve(state: TaskState, generate: Generate):
        model = get_model(); cells = []
        for passage in docs[state.metadata['document']]:
            out = await model.generate([ChatMessageUser(content=PROMPT.format(passage=passage, question=state.input_text))],
                                       config=CONFIG)
            cells.append(log_odds(out))
        state.metadata['cells'] = cells
        best = max(range(len(cells)), key=lambda i: cells[i]['lo'])       # ties: the earliest passage
        state.output = ModelOutput.from_content(str(get_model()), f'passage {best}')
        return state

    return solve


def hit(scores, gold):
    """Expected hit@k and reciprocal rank of the best-ranked gold passage, ties broken uniformly at random
    (stale/relocate.py, hit)."""
    gold = set(gold); s = max(scores[g] for g in gold)
    hi = sum(1 for i, x in enumerate(scores) if x > s and i not in gold)
    t = sum(1 for i, x in enumerate(scores) if x == s and i not in gold)
    m = sum(1 for g in gold if scores[g] == s)
    gt = lambda x: comb(t, x) / comb(t + m, x) if x <= t else 0.0          # P(first gold in the tie is past x)
    hk = {k: (0.0 if k - hi <= 0 else 1 - gt(k - hi)) for k in KS}
    rr = sum((gt(x - 1) - gt(x)) / (hi + x) for x in range(1, t + 2))
    return hk, rr


@scorer(metrics={'hit1': [mean(), stderr()], 'hit3': [mean()], 'hit5': [mean()], 'rr': [mean()]})
def gold_rank():
    async def score(state: TaskState, target: Target):
        lo = [c['lo'] for c in state.metadata['cells']]
        hk, rr = hit(lo, [int(g) for g in target.target])
        return Score(value={'hit1': hk[1], 'hit3': hk[3], 'hit5': hk[5], 'rr': rr},
                     answer=state.output.completion, metadata={'lo': lo})
    return score


@task
def relocation(samples: str = 'A', first: int = 0):
    """samples: A, B, D or a comma list; first: only the first N points of each sample's fixed order (0 = all)."""
    return Task(dataset=dataset(samples, first), solver=score_passages(), scorer=gold_rank(), config=CONFIG)
