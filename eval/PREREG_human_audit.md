# Blind human audit of the r20 test (GPT r1's "one measurement"), pre-registered 2026-11-11T23:50:16Z

Written while the r20 Kev run stood at 63/70 states, before any evaluation of Kev on r20, and before the Qwen baseline
(eval/PREREG_kev_vs_llm.md) had run at all. Code: audit/human_audit.py. Sample: audit/sample.json. Both hashed below.

## Why
The r20 gold is two LLM raters reading excerpts. GPT r1: "Another model-as-judge experiment would not" change the
assessment; the decisive number is human-verified changes the tool misses at a fixed review budget.

## Sample (seed 20261112), drawn now, from things fixed before any model output was read
Population: 2,450 items (35 updates x 70 v1 questions). The sample uses only the LLM-rater gold and the chunk-hash arm
(bge-small, computed at selection time). It never looks at Kev or Qwen, so the choice of items favours neither.
- S1: all 25 gold-1 items (both raters flip).
- S2: all 31 ambiguous items (one rater flips).
- S3a: 30 of the 346 gold-0 items inside the chunk-hash queue (CH), at random.
- S3b: 20 of the 2,048 gold-0 items outside CH, at random (the low-ranked cases GPT asked for).
106 items over 32 updates. Ege is the human (not an expert; reading comprehension). One person, disclosed.

## What the human sees (blind)
Updates in random order; for each, the old and new changed passages with word-level highlights, and the full old and
new documents (expandable, searchable). Then that update's sampled questions in random order. No model score, no rater
label, no stratum, no count of how many items are "real".
Per question, one choice:
- CHANGED: after this update, the document's answer to the question is different.
- PASSAGE ONLY: the edited passage reads differently on this point, but other text in the document gives the same
  answer before and after.
- NO CHANGE.
- CAN'T TELL (excluded from denominators, counted and reported).
Optional free-text note. Progress is saved; stopping early leaves a random subset (order is random), reported as such.

## Human gold
- H_doc = 1 for CHANGED, 0 for PASSAGE ONLY or NO CHANGE. Primary (an approved answer is invalidated).
- H_pass = 1 for CHANGED or PASSAGE ONLY, 0 for NO CHANGE. Secondary (what the raters and the models were asked).

## Reported, all as counts with the sample's composition (never as corpus recall)
1. Rater gold against the human: H=1 share in S1, S2, S3a, S3b.
2. Rater misses: H=1 items in S3a and S3b.
3. GPT r1's decisive number: H_doc=1 items that KEV ranks outside its update's top 5, and outside the global top 182.
4. Each arm on human gold (KEV, LLM-DIFF, LLM-QA from the bench; BGE; CH): how many sampled H=1 items it ranks within
   k = 25, 50, 100, 182 (rankings exactly as in bench/kev_vs_llm.py and rq.py).
5. Info only: an inverse-probability-weighted estimate of H=1 items among all 2,394 gold-0 items (S3a weight 346/30,
   S3b weight 2048/20). Wide; one hit in S3b counts as ~102.

## Reading rule (fixed now)
Over the sampled items with H_doc = 1: the PREREG_kev_vs_llm.md rule, unchanged, with human gold in place of rater gold
(KEV vs LLM-DIFF at k = 182; a difference of >= 3 items is a difference; cost from the bench). Also stated: if the
human confirms fewer than 10 H_doc = 1 items in total, the comparison is reported as underpowered, no winner.

## Not claimed
Anything beyond this sample, one human, and these 35 updates; expertise in law.

## Addendum 2026-11-11T23:54:39Z: the page (before any Kev evaluation; r20 at 63/70)
- audit/human_audit.py gained the `page` command (blind data: texts, question wording, GitHub links; no gold, stratum
  or model output). `sample` is unchanged: re-running it reproduces audit/sample.json byte for byte (hash above).
- Page: audit/page.html, published privately for Ege at claude.ai/artifact/N25CWMZpfBAtY388DymbPH. Answers save to the
  page's own store (collection "verdicts", one document per item: v, note, t) and to the browser as a backup.
- Known leak, disclosed: the number of statements per update differs (1 to 11), which hints that some updates hold more
  rater-flagged items. Order within an update is random.
