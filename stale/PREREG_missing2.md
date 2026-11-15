# Missing points, the larger test: 10 more documents, and Kev against its base family (pre-registered)

Written 2026-11-15 ~20:40 UTC, after the pilot's result (`stale/RESULT_missing.md`) and before any score of these 10
documents exists from any arm of this test. Code: `stale/missing2.py` (tested on random stand-in scores only).

## Why
The pilot (four documents) read "worth building, on Kev": 18 of Kev's 40 top-10 suggestions stated a case with no
approved point on the service, twice the reranker's 9, and Kev ranked the known positives better (AUROC +.084). Its
own rules say a pilot is a reason for a larger test, not a result to quote. Two questions are open: does it hold on
other documents, and does Kev's lead come from its decision-model training or from asking a language model about each
passage at all (the base family was not run in the pilot, for cost)?

## Documents (fixed rule, applied to `stale/out/reloc_docs.json`)
Every privacy or terms document of the 20 platforms with at most 40 pieces and at least 10 known positives (the
pilot's definitions), except the pilot's four. This gives 10 documents, 293 pieces, 19,804 piece-question cells:
Bluesky, Instagram, LinkedIn, Parler, Reddit and WhatsApp Terms of Service; Pinterest, Snapchat, Spotify and Tumblr
Privacy Policy. Candidate cases, positives, exclusions and negatives exactly as in the pilot.

## Arms (a case's score in a document = the best score over the pieces the arm looks at)
- KEV, RERANK, BM25: as in the pilot, every piece.
- CASCADE_KEV and CASCADE_QWEN: for each case, the reranker's top 3 pieces in that document (ties to the earliest
  piece). CASCADE_KEV takes Kev's p(yes) on those pieces (from the KEV arm's cells); CASCADE_QWEN asks Qwen3.5-4B
  instruct (Kev's base family, port 9996, llama.cpp's host prompt cache off as in the cost benchmark) the same question on the same pieces, scored as yes/no
  log-odds of its first answer token (`stale/relocate2.qwen_ask`, the relocation tests' scorer). Same cells, two
  models: the comparison isolates the per-passage model. The shortlist exists because the instruct model pays for
  every question: on all 19,804 cells it would take about 35 h; on the 2,043 shortlist cells about 3.6 h.

## Measures
1. **Known positives first (primary):** per document, AUROC of positives against negatives by case score; mean over
   the 10 documents. KEV - RERANK, KEV - BM25 and CASCADE_KEV - CASCADE_QWEN, each with a 95% interval from 2,000
   draws resampling positives and negatives within each document (seed 20261122).
2. Recall@20 per arm (descriptive).
3. **New suggestions:** the top 10 negatives per document of KEV, RERANK, CASCADE_KEV and CASCADE_QWEN, each with
   the arm's best piece, become blind cards (case and passage only; deduplicated over document, case and piece),
   plus 20 random controls. Rated YES / PARTLY / NO with the pilot's instructions by a fresh Claude Opus subagent that
   reads only its folder; GPT (Codex) rates the same cards as a second rater if its usage allows (reported, not
   read). Precision@10 = share of an arm's 100 cards rated YES, Wilson 95% interval. KEV - RERANK and CASCADE_KEV -
   CASCADE_QWEN precision differences with a 95% interval from resampling documents (descriptive). Valid only if at
   most 3 of the 20 random controls are rated YES.
4. Cost: Kev's seconds for the KEV arm (cells asked and cached), the reranker's, and the instruct model's seconds per
   cell on the shortlist.

## Readings (fixed now)
- **Replication:** REPLICATED if valid, Kev's precision@10 is at least .30 with a Wilson lower bound of at least .15,
  and measure 1 reads KEV better than BM25. Otherwise NOT REPLICATED.
- **Kev against the reranker:** "KEV better" if measure 1 KEV - RERANK reads KEV better and Kev's precision@10 is at
  least the reranker's; "RERANK better" if it reads KEV worse and the reranker's precision is at least Kev's;
  otherwise "no difference shown".
- **Decision-model training:** measure 1 CASCADE_KEV - CASCADE_QWEN: interval above 0, "KEV better than its base
  family"; below 0, "base family better"; otherwise "no difference shown" (and the lead belongs to a language model
  per passage, as on every earlier measure). Precision@10 of the two cascade arms is reported beside it.
- Pooled over the pilot's 4 and these 10 documents: descriptive only.

## Predictions
AUROC KEV .72-.80, RERANK .63-.72, BM25 .50-.58, CASCADE_KEV within .02 of KEV, CASCADE_QWEN .70-.80. KEV - RERANK
+.04 to +.10 with P(KEV better) 60%. CASCADE_KEV - CASCADE_QWEN about 0, P(no difference shown) 75%. Precision@10
KEV .35-.50, RERANK .18-.30, both cascade arms .35-.50. P(REPLICATED) 70%.

## Schedule and the shared CPU
The scanner backfill (`run_backfill.sh`, started 20:26 UTC after the pilot) is stopped for this test, as it was for
part D, and re-queued after it (`scan` skips updates already scanned). Order: BM25, KEV, RERANK, then the Qwen server
(Kev's server idle) for CASCADE_QWEN, then measures. Timings are reported with that note.

## Disclosures
- The pilot's results are known; the document rule, arms and readings were written knowing them.
- These documents were used in the relocation tests (Kev, the reranker, BM25 and Qwen scored their pieces for the
  curator-quote cases), so some KEV cells come from the score cache. No score of this test's measures was computed
  before this file was hashed; `prep`'s output (the list above) was seen.
- `stale/missing2.py` was run on random stand-in scores to test it (`measures`, `score`), with outputs in a scratch
  folder.
