# Pre-registration: the base family on the states-the-case measure

Written 2026-11-15 ~02:24 UTC, after the pooled states-the-case result (`stale/RESULT_states_case.md`: KEV .725,
RERANK .608, BM25 .417 on 120 points) and before any card of this test was built. Hashed with the code, cards and key
in `stale/PREREG_states_case_qwen.sha256` before rating.

## Why
On hit@1, Kev's base family (Qwen3.5-4B instruct, the same yes/no question per passage) showed no difference from Kev
in either part. The states-the-case result left it out, so it cannot say whether its lead over the reranker belongs to
Kev's decision-model training or to any language model asked per passage. Qwen's scores are on disk.

## Cards (`stale/states_case_qwen.py`, seed 20261120)
- The same 120 points. QWEN's top passage per point (highest yes-minus-no log-odds, ties to the earliest passage).
  Where that (point, passage) was already rated in the first test or the extension, that verdict is reused. 25 are
  new.
- 30 ANCHOR cards: drawn from the already-rated non-random cards of both tests, rated again blind, to measure whether
  the new rater judges like the old ones.
- 10 RANDOM controls: a passage outside QWEN's top 5, not any rated arm's top passage, and not gold.
- All shuffled; case and passage only; a fresh Claude subagent (Opus 5.5), the same README.

## Readings
- QWEN states@1 on the 120 points; paired KEV - QWEN and QWEN - RERANK, 95% cluster bootstrap over documents; called
  only when the interval excludes 0.
- Validity, both required before anything is called: anchors agree with the earlier verdict (YES vs not YES) on at
  least 24 of 30, the anchors' YES share differs from the earlier raters' by at most .10, and at most 2 of 10 RANDOM
  cards are rated YES. Otherwise reported as unreliable.
- LLM raters, not people; beside the hit@1 results, not in place of them.

## Predictions
QWEN states@1 .71. KEV - QWEN: no difference shown. QWEN - RERANK: QWEN better (about 60% likely).
