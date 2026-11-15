# Result: which arm's top passage states the case? (blind, LLM-rated)

Pre-registration: `stale/PREREG_states_case.md` (02:07 UTC, 2026-11-15). Code, cards and key hashed before rating;
one code revision before any card existed (a short document had no passage for a random control; logged in
`stale/PREREG_states_case.sha256`); verdicts hashed before scoring. Scores: `stale/out/states_case_result.json`.

One Claude subagent (Opus 5.5) rated 150 cards blind (case and passage only). This is one LLM rater on 60 points, not
a person: it sits beside the pre-registered hit@1 results, not in place of them.

## Readings
| | KEV | RERANK | BM25 |
|---|---|---|---|
| States the case @1 (top passage rated YES) | **.717** | .583 | .417 |
| YES or PARTLY @1 | .917 | .767 | .667 |
| hit@1 (the curator's passage) on the same 60 points | .550 | .467 | .306 |

- **KEV - BM25: +.300 [+.167, +.418], KEV better.**
- **KEV - RERANK: +.133 [.000, +.258], no difference shown** (the lower bound sits exactly at 0).
- Validity: 0 of 10 random control passages rated YES, so the comparison is called.

## What it adds
- The order holds and the gaps widen slightly when "right" means "states the case" instead of "the passage the
  curator quoted". When an arm's top passage was not the curator's, the rater still found it stating the case 17
  times in 27 for Kev, 13 in 32 for the reranker and 10 in 42 for BM25: Kev's misses are more often near-misses.
- Kev against the reranker is still not shown, now on a second measure, at the edge of the interval.
- The rater was strict: it rated 42 of 53 curator-quoted passages YES (9 PARTLY, 2 NO). So the absolute rates are
  lower than a lenient reader would give, and in part B Kev's states@1 (.633) is below its hit@1 (.667). The
  comparison between arms, all judged by the same rater, is the meaningful part.

## Prediction against result
| | predicted | result |
|---|---|---|
| States@1 KEV / RERANK / BM25 | .85 / .78 / .50 | .717 / .583 / .417 |
| KEV - RERANK | no difference shown | no difference shown |
| KEV - BM25 | KEV better | KEV better |

By part (30 points each), states@1: A KEV .80, RERANK .63, BM25 .47; B KEV .63, RERANK .53, BM25 .37.
