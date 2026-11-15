# Exploratory: when Kev's top passage is not the curator's, does it state the case anyway?

Written 2026-11-15 ~02:00 UTC, after parts A and B were final (`stale/RESULT_relocate2.md`) and before any card was
built. Exploratory, not a pre-registered test: it changes no reading and no page. The cards, the answer key and this
plan are hashed in `stale/PLAN_miss_audit.sha256` before rating.

## Why
In parts A and B, hit@1 counts a point as found only when Kev's top passage is one the curator quoted. A case can be
stated in more than one passage (a summary at the top and the full clause below, a privacy policy that repeats
itself), and then a "miss" still sends the curator to the right place. 44 of Kev's 76 misses in part A, and 27 of 50
in part B, were also missed by both Qwen3.5-4B and the reranker, which fits that reading but does not show it.

## Cases (built by `stale/miss_audit.py`, seed 20261117)
- **MISS** 40: points where Kev's hit@1 < 1, 20 drawn from part A and 20 from part B. The passage shown is Kev's
  highest-scoring passage that is not a gold passage.
- **GOLD** 15: points where Kev's hit@1 = 1, drawn from both parts; the passage shown is the gold passage. A positive
  control: the rater should say YES to nearly all.
- **RANDOM** 15: from the same documents as the GOLD draws, a passage drawn at random among those that are neither
  gold nor in Kev's top 5 for the case. A negative control: the rater should say NO to nearly all.
The 70 cards are shuffled together and show only the case and the passage.

## Rater
A Claude subagent (Opus 5.5) that reads only `stale/audit_misses/`. For each card: does the passage state or clearly
imply the case? YES / PARTLY (something close: narrower, broader, or only part of the case) / NO.

## What gets reported
- The YES share (and YES or PARTLY) on MISS, beside the YES share on GOLD (the rater's sensitivity) and on RANDOM (its
  false-positive rate). If GOLD is under .8 or RANDOM over .2, the rater is not reliable enough and the MISS share is
  not interpreted.
- Otherwise, an exploratory estimate: the share of points where Kev's top passage states the case = hit@1 +
  (1 - hit@1) x the MISS YES share, per part, labelled as an LLM rater's reading, with the control rates beside it.

## Prediction
MISS YES 45%; GOLD YES 90%; RANDOM YES 5%.
