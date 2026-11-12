# Result: decision model vs ordinary LLM on the same diffs (2026-11-12)

Pre-registration: `eval/PREREG_kev_vs_llm.md` (design 2026-11-11T22:28Z, implementation frozen 22:38Z). Output hashes:
`eval/PREREG_kev_vs_llm.sha256` ("# bench result 2026-11-12T14:38:17Z"). Numbers from `bench/out/result.json`.

## Pre-registered reading: NO CLEAR WINNER
Kev-4B found more changes, but at more than twice the comparator's CPU time, so neither win condition held.

## Counts (35 updates, 2,450 update x question items, 25 gold changes, LLM-rater gold)
| Arm | found within 25 / 50 / 100 / 182 reviews | ambiguous counted as changes (/56) at 182 | CPU s per update |
|---|---|---|---|
| KEV (Kev-4B, \|p_new - p_old\|) | 12 / 14 / 16 / **20** | 24 | 179.8 |
| LLM-DIFF (Qwen3.5-4B lists changed question numbers) | 1 / 1 / 1 / **2** | 3 | 49.1 |
| LLM-QA (Qwen3.5-4B answers all 70 y/n per side) | 1 / 3 / 6 / **12** | 16 | 81.7 |

Same CPU (6-core i5-11600K), same llama.cpp build, both Q8_0, one request at a time.

## What the counts say beyond the reading
- **The pre-registered comparator was degenerate.** LLM-DIFF answered `[]` (no question changed) on 32 of 35 updates,
  listed 69 of 70 questions on one, and 1 and 33 on the other two. Its outputs all parsed. So its ranking is
  almost entirely the random tail. This is how Qwen3.5-4B with thinking off handled this prompt, not a parse failure.
  The prompt was fixed before any real run and is not changed after the fact.
- **The informative comparison is LLM-QA** (the pre-registered ablation, with no verdict attached): Kev finds 20 of 25
  within 182 reviews, Qwen answering every question 12, at 2.2x the CPU time per update.
- **Kev's cost is per question, not per text.** Timing on 5 fixed states (one request in flight):
  | Questions | 25 | 70 | 101 | 500 |
  |---|---|---|---|---|
  | Mean seconds per state | 35.9 | 80.3 | 109.8 | 580.0 |

  A least-squares fit over all 90 timed requests gives about 1.14 s per question plus 0.005 s per character of
  text (stale/cost.py), with a mean absolute error of 6%.
  - With the r20 states (median a few hundred words), the per-question template dominates.
  - Sharing one prefill across questions saves the text, which is small here, not the questions.
  - On this CPU, the "many questions for the price of one read" property does not show up at these text lengths.

## Not claimed
- Anything about GPUs, batch serving, or long documents (where the shared text would dominate).
- Anything about human-verified changes: the gold is two LLM raters on excerpts (see `audit/`).
