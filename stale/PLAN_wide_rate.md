# Plan: rate the curator page's unrated suggestions, blind

Written 2026-11-17, before any card exists. Code: `stale/wide_rate.py`. Hashes of this plan and the code go in
`stale/PLAN_wide_rate.sha256` before the cards are built; the cards' hashes are appended before any rater starts.

## Why
The private curator page lists 10 suggestions per document for all 40 privacy policies and terms of the 20 platforms.
On 28 of the 40 no suggestion was ever rated: the 20 documents of `stale/missing_wide.py`, the 6 of
`stale/missing_rest.py`, and Pinterest's two, which the watch re-scored on their new text. For those the page borrows
the larger test's rated precision (73 of 100 cascade suggestions rated YES), on other documents. This run measures the
page itself, and checks on 28 new documents the larger test's finding that Kev's suggestions are rated YES more often
than the reranker's (there +.23, Kev on every passage; the cascade +.27 descriptively).

## Cards
- PAGE: each of the 28 documents' top 10 exactly as the page shows them (Kev-4B on the reranker's top 3 passages per
  case, the best of those passages; current text). 280 cards before deduplication.
- RERANK: the reranker's (bge-reranker-v2-m3) top 10 on every passage, same candidate cases, its best passage.
- 20 random controls: a random candidate case of a random one of the 28 documents with a random passage of it.
- A card is (document, case, passage); one picked by both arms is rated once and counts for both.
- Shuffled (seed 20261117), then cut in two halves: `stale/audit_wide_a/`, `stale/audit_wide_b/`, each with the
  instructions the larger test used (`stale/audit_states/README.md`, unchanged) and an empty `verdicts.json`.

## Raters
One fresh Claude Opus subagent per folder, the larger test's rater setup: it reads only its folder (README, cards,
verdicts file), sees case and passage only (no arm, no score, no document name), and answers YES / PARTLY / NO with one
short reason. GPT (Codex) may rate the same cards as a second rater if its usage allows: reported beside the first,
never read.

## Readings (fixed now)
- Validity: at most 3 of the 20 random controls rated YES. If more, both readings are NOT VALID.
- Page precision: the YES share of the PAGE cards, with a Wilson 95% interval. Predicted .55-.75. The result says
  whether it falls in, below or above that range; it is reported either way.
- PAGE against RERANK: the PAGE YES share minus the RERANK YES share, 95% interval from 2,000 draws resampling the
  28 documents (seed 20261118). "PAGE better" if the interval is above 0, "RERANK better" if below, otherwise "no
  difference shown". Predicted +.10 to +.30 (RERANK alone .35-.55); I put P(PAGE better) at 75%.

## Descriptive only (nothing is read from these)
The two arms by run (20 / 6 / Pinterest's 2), on the English documents only (Telegram's two are German), by rank (1-5
against 6-10), by document, by folder (rater); YES-or-PARTLY shares; verdict counts.

## What it can and cannot show
- An AI rater, not a person, and not ToS;DR's curators: "rated YES" means one Claude Opus subagent judged that the
  passage states or clearly implies the case. That is how the larger test's 73 of 100 was measured too.
- It rates the passage the arm picked, not the document: a NO can be a right case with the wrong passage.
- I built the page and have seen some of its suggestions (Pinterest's comparison, Telegram's German passages), but
  have rated none, and the raters see neither the page nor this plan.
- Whatever the result, the page will state this run's measured precision for these 28 documents in place of the
  borrowed figure. Whether to show each card's verdict on the page is not decided here.
