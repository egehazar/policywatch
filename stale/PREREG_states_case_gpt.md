# "Does the top passage state the case?" re-rated by GPT (written before GPT sees a card)

Written 2026-11-15 ~10:40 UTC. Exploratory addition to `stale/PREREG_states_case.md`, `_ext.md` and `_qwen.md`;
it changes none of their readings.

## Why
`stale/RESULT_states_case.md` says, on 120 points, Kev's top passage states the case more often than the reranker's
(pooled +.117 [+.034, +.200], "KEV better") and BM25's (+.308), with no difference from its base family Qwen3.5-4B.
Every verdict came from Claude raters, and the result itself names the risk: "A rater that shares a language model's
sense of relevance could favour Kev's picks." A rater from another company is a partial answer to that (not a
person).

## Rater
GPT through Codex CLI 0.154.0 (`codex exec`), gpt-6-astra, reasoning effort xhigh (Ege's config), read-only
sandbox, an empty folder, no web. One run per folder (`stale/audit_states`, `audit_states2`, `audit_states3`: 150,
122 and 65 cards), each given that folder's `README.md` and `cards.md` verbatim, with the file-writing instruction
replaced by "reply with only the JSON object". Cards are blind (case and passage only; ids say nothing). A run is
redone once only if its reply is not parseable or misses cards (said so).

## What is computed (`stale/states_case_gpt.py`)
With GPT's verdicts in place of the Claude raters', on the same 120 points and the same bootstrap as the originals:
1. States the case @1 (top passage YES) for KEV, QWEN, RERANK, BM25; YES or PARTLY @1.
2. KEV - RERANK, KEV - BM25, KEV - QWEN, QWEN - RERANK with 95% intervals.
3. Checks: random controls rated YES (the originals allowed at most 2 per test); GPT's self-agreement on the 30
   anchor cards (the same passages rated twice, in two folders); card-level agreement with the Claude raters (YES vs
   not YES, kappa).

## Reading (fixed now)
- **HOLDS UNDER GPT** if GPT's random-control YES count is at most 3 of 30, AND KEV - RERANK and KEV - BM25 both
  have intervals above 0, AND KEV - QWEN shows no difference: the same three conclusions as with Claude raters.
- **PARTLY HOLDS** if KEV - BM25 is above 0 but KEV - RERANK's interval includes 0 (or KEV - QWEN shows a
  difference): the reranker comparison (or the base-family one) then depends on the rater, and the README and
  write-up say so.
- **DOES NOT HOLD** if KEV - BM25's interval includes 0 or goes the other way.
- Not valid if more than 3 of 30 random controls are rated YES; then nothing is called.

## Predictions
GPT stricter or similar to Claude: states@1 KEV .65-.75, RERANK .55-.65, BM25 .35-.45; KEV - RERANK +.05 to +.12
(about even odds its interval clears 0); KEV - BM25 clearly above 0; KEV - QWEN no difference; card-level kappa with
Claude raters .55-.75.
