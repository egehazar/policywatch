# Decision model vs ordinary LLM on the same diffs (GPT r1's "decision-model result"), pre-registered 2026-11-11

Status: DESIGN ONLY. The baseline model is not on disk; downloading it needs Ege's OK. Nothing below has been run.

## Question
At equal hardware (this 6-core CPU, llama.cpp), does Kev-4B (a decision model fine-tuned from Qwen3.5-4B-Base, which
answers a bank of yes/no questions per text in one shared-prefix pass) find the changed answers better and/or more
cheaply than its own base family used the ordinary way: Qwen3.5-4B (instruct), Q8_0, reading the same diff?

## Data
The frozen r20 test: 35 OTA ToS/Privacy updates, the 70 v1 questions, old and new changed regions (byte-identical),
and the gold already frozen (both LLM raters flip = 1, neither = 0, one = ambiguous).
- Twitch (p05) stays in. The v1 bank predates the Twitch finding, so v1 has no leakage.
- Caveat stated up front: the gold is LLM raters on excerpts, not humans (GPT r1 point 4). The human audit (separate
  file) is what upgrades it.

## Arms (each produces a ranking of the 2,450 (update, question) items)
- KEV: |p_new - p_old| from the r20 run, as already scored.
- LLM-DIFF: Qwen3.5-4B Q8_0 at temperature 0, thinking off, one prompt per update. The prompt holds the old and new
  regions and the 70 numbered questions, and asks for the question numbers whose answer changed, most certain
  first. Rank = order of mention; unmentioned items follow in random order (seed 20261111).
- LLM-QA: the same model answers all 70 questions as y/n for the old region, and separately for the new one, in one
  generation each. An item counts as flipped when its answers differ. Flipped items come first in random order,
  then the rest. This is GPT r1's "direct answer classification" ablation, run on a generative model.

## Metrics
- Recall of gold-1 items at reviewer budgets k = 25, 50, 100, 182 items. Ambiguous items are reported both ways.
- Primary: recall@182 (the r20 build line's budget).
- Cost:
  - end-to-end CPU wall time per update, at -np 1 for every arm (Kev also at its normal -np 4)
  - prompt and generated tokens
  - peak RSS of llama-server
- Scaling (Kev only, its architectural claim): wall time per update with banks of 25, 70, 101 and 500 questions.
  500 = the 101 v2 questions plus synthetic paraphrases, timing only, never scored for accuracy.

## Reading rule (fixed now)
- "Decision model wins": KEV recall@182 >= LLM-DIFF recall@182 AND KEV's CPU time per update <= LLM-DIFF's, or
  KEV recall@182 exceeds LLM-DIFF's by >= 3 gold items at <= 2x its CPU time.
- "LLM wins": LLM-DIFF recall@182 exceeds KEV's by >= 3 items at <= 2x KEV's CPU time.
- Otherwise "no clear winner".
- With 25 positives, a 3-item margin is the smallest difference reported as a difference. Every result is shown as
  counts.
- LLM-DIFF output that does not parse is scored as an empty list (a miss), and its count is reported.

## Not claimed
- Anything about human-verified invalidation (see the human-audit design).
- Anything about other model sizes or quantizations.
