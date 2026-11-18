# Plan: does the decision model's cost edge survive one prompt with all the questions?

Written 2026-11-18 ~22:45 UTC, before any arm below has run. Hashed with its code (stale/multiq.py) before the run.

## Why
On the missing-points task the decision-model endpoint (Kev-4B, /v1/systemone) took 1.11 s per question against
6.05 s for its base family's instruct model, Qwen3.5-4B (stale/RESULT_missing2.md). The two were scored the same on
accuracy (AUROC .721 vs .715 on the reranker's shortlist). But the instruct model was asked one question per request,
and its llama.cpp server could not reuse the passage's prefix, so it read the passage again for every question.

An adversarial review (2026-11-18) asked the obvious interview question: what if the instruct model is asked all of a
passage's questions in ONE prompt? It then reads the passage once, like Kev. Nothing here has measured that. This
plan measures it on the same cells, once.

## Cells
The larger missing-points test's cascade cells (stale/out/missing2_docs.json, reranker shortlist SHORT = 3):
- 10 documents, 275 passages, 2,043 (passage, case) cells;
- questions per passage: median 5, mean 7.4, maximum 44;
- known positives and negatives as in that test.
The question is the same TEMPLATE as Kev's and the single-question instruct arm's.

## Arms
- **CASCADE_KEV.** The hashed missing2 scores (for accuracy). For cost, Kev is re-timed on exactly these cells: one
  /v1/systemone request per passage with its shortlisted questions, bypassing the score cache. The server is as
  deployed: -np 4, -t 6.
- **CASCADE_QWEN.** The hashed single-question instruct scores (for accuracy). Their measured cost on these cells is
  12,351 s for 2,043 cells, 6.05 s per question (missing2, 2026-11-16).
- **QWEN_MULTI (new).** Qwen3.5-4B instruct, Q8_0, thinking off, its own llama.cpp server (-np 1, as in the earlier
  instruct runs).
  - One chat request per passage: the passage, then its questions numbered 1..k, then "Answer with one line per
    question in the form "1: yes"".
  - A grammar forces exactly k lines "j: yes|no".
  - The score of question j is log P(yes) - log P(no) over the answer token's top 20 logprobs, as in the
    single-question arm (an answer outside the top 20 gets the 20th logprob).
  - Questions keep the order the shortlist gives them.
- **Case score.** In every arm, the best score over the case's shortlisted passages, as in missing2.

## Measures and readings (fixed now)
1. **Accuracy.** Per-document AUROC of known positives against negatives. The difference CASCADE_KEV - QWEN_MULTI is
   averaged over the 10 documents.
   - Primary interval: a paired t-interval over documents.
   - Secondary interval: the missing2 within-document bootstrap (2,000 draws, seed 20261125).
   - Reading on the primary interval: "KEV better" if its lower bound > 0, "MULTI better" if its upper bound < 0,
     otherwise "no difference shown".
   - Secondary, same rule: CASCADE_QWEN - QWEN_MULTI (does putting all questions in one prompt hurt the instruct
     model?).
2. **Cost.** Wall-clock seconds per question, on the same cells, one arm after the other, nothing else running on
   the CPU.
   - R = QWEN_MULTI s/question ÷ KEV s/question (both measured in this run).
   - Reading: "Kev's cost edge holds" if R >= 1.5; "edge gone" if R <= 1.0; otherwise "edge reduced".
3. **Format.** If more than 5% of cells cannot be read from a grammar-forced reply, QWEN_MULTI is "format
   unreliable". Its failed cells score 0 and its accuracy reading is reported as void.

## My predictions (written before running)
- QWEN_MULTI AUROC about .70 (.66-.73).
- KEV - MULTI: no difference shown (P 65%).
- QWEN - MULTI: no difference shown (P 70%).
- Kev on these cells about 1.9 s per question (7.4 questions per passage): its fit is 7.38 s per passage plus 0.93 s
  per question.
- QWEN_MULTI about 1.4 s per question (0.8-2.5): one read of about 6 s, plus about 0.5 s of generation per answer.
- R about 0.75, so "edge gone" (P 55%), "edge reduced" (P 35%), "edge holds" (P 10%).
- Format failures under 1%.

## What this cannot show
- Only one prompt wording and one question order.
- It is CPU only: on GPUs with batched serving the costs differ.
- The decision model's other offers (a calibrated probability per question without generation, no parsing,
  order-free) are not priced here. Only accuracy on this task and time on this machine are.

## Smoke test before hashing (2026-11-18 ~11:05 UTC)
I ran 3 passages of the pilot's first document (stale/out/missing_docs.json) with 6 cases each. They are not among
the measured cells.
- Every reply parsed (18 of 18 answers).
- QWEN_MULTI took 13.0-16.6 s per passage, against 39-47 s for the same 6 questions asked one at a time.
- Both arms said yes to the same 2 of the 18.
The predictions above are left as written.
