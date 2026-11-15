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

## Final: the pre-registered extension and the pooled 120-point reading
`stale/PREREG_states_case_ext.md` (02:12 UTC), fixed in advance as the only further look: 60 new points (30 from each
part), the same protocol, a fresh rater, then a pooled reading called only if the pooled interval excludes 0 and the
extension points the same way. Hashes in `stale/PREREG_states_case_ext.sha256`; scores in
`stale/out/states_case_pooled.json` (`py -m stale.states_case_ext score`).

| | KEV | RERANK | BM25 |
|---|---|---|---|
| Extension (60 points): states the case @1 | .733 | .633 | .417 |
| **Pooled (120 points): states the case @1** | **.725** | .608 | .417 |
| Pooled: YES or PARTLY @1 | .900 | .758 | .650 |
| Pooled: hit@1 (the curator's passage) on the same points | .625 | .542 | .373 |

- Extension alone: KEV - RERANK +.100 [.000, +.208]; KEV - BM25 +.317 [+.196, +.452]. 0 of 10 random controls rated
  YES; the extension's rater rated 42 of 48 curator-quoted passages YES.
- **Pooled KEV - RERANK: +.117 [+.034, +.200]. Final reading: KEV better than the reranker** on this measure.
- **Pooled KEV - BM25: +.308 [+.206, +.407]. KEV better.**
- On the same 120 points, hit@1 KEV - RERANK is +.083 [-.020, +.183], no difference shown. The gap becomes a shown
  difference because Kev's misses state the case more often: 24 of 45 for Kev, 19 of 55 for the reranker, 14 of 76
  for BM25.
- Predicted: pooled +.11 with about even odds of "KEV better"; result +.117, KEV better.

## How far this goes
- Both raters are Claude models judging passages a language model ranked. A rater that shares a language model's
  sense of relevance could favour Kev's picks; nothing here rules that out. A person's ratings would.
- It does not overturn the pre-registered hit@1 results, where KEV and the reranker were not separated in part A and
  were in part B. It adds a second measure, closer to what a curator needs, on which Kev is ahead by about 12 points.
- Kev's base family (Qwen3.5-4B, asked the same yes/no question per passage) was not rated here. On hit@1 it showed no
  difference from Kev, so this result is about asking a language model per passage, not about decision-model
  training.
- The reranker remains 3.6-5x cheaper; part D tests whether a reranker-first cascade keeps Kev's accuracy at a
  fraction of its cost.
