# Pre-registration: which arm's top passage states the case? (a blind, LLM-rated comparison)

Written 2026-11-15 ~02:05 UTC, after the exploratory miss audit (`stale/RESULT_miss_audit.md`) and before any card
of this test was built. Hashed with the code, cards and key in `stale/PREREG_states_case.sha256` before rating.

## Why
Parts A and B score an arm by whether its top passage is one the curator quoted (hit@1). The miss audit found that 23
of 40 Kev misses still point to a passage stating the case, so hit@1 understates every arm by an unknown amount, and
possibly unevenly. A curator needs a passage that states the case. This test compares KEV, the reranker (RERANK,
bge-reranker-v2-m3) and BM25 on that, using only scores already on disk (no new model call).

## Points and cards (`stale/states_case.py`, seed 20261118)
- 60 points: 30 drawn from part A's 200 and 30 from part B's 202 (sorted by point id, then `random.Random`).
- For each point and arm, the arm's top passage (highest score; ties go to the earliest passage). One card per
  distinct (point, passage), so a passage two arms share is rated once.
- 10 RANDOM control cards: for 10 of the drawn points, a passage outside every arm's top 5 and not gold.
- All cards are shuffled and show only the case title and the passage, as in the miss audit.

## Rater
A fresh Claude subagent (Opus 5.5), the same instructions as the miss audit (`stale/audit_states/README.md`: YES /
PARTLY / NO, "does this passage state or clearly imply the case?"), reading only `stale/audit_states/`.

## Measures and readings
- States@1 per arm: the share of the 60 points whose top passage is rated YES. Also reported: YES or PARTLY, and
  hit@1 on the same 60 points.
- Paired differences KEV - RERANK and KEV - BM25, 95% cluster bootstrap over documents (2,000 draws), as in parts A
  and B. A difference is called only when its interval excludes 0: "KEV better", "KEV worse", else "no difference
  shown".
- Validity: if the rater says YES to more than 2 of the 10 RANDOM cards, the comparison is reported as unreliable and
  no difference is called.
- This is one LLM rater on 60 points: the README reports it as such, beside the pre-registered hit@1 results, never
  in place of them.

## Predictions
States@1: KEV .85, RERANK .78, BM25 .50. KEV - RERANK: no difference shown. KEV - BM25: KEV better.
