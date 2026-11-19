# Result: the decision model's cost edge does not survive one prompt with all the questions

Plan: `stale/PLAN_multiq.md`, hashed with its code (`stale/multiq.py`, `run_multiq.sh`) at 11:01:18Z on 2026-11-18,
before any measured cell ran (`stale/PLAN_multiq.sha256`, commits 037a596 and e063c69). Outputs hashed by the run
script at 13:10:56Z. Numbers: `stale/out/multiq_result.json`.

## Readings (fixed in advance)
- **Accuracy: no difference shown.** Per-document AUROC, mean of 10 documents: Kev on the reranker's shortlist
  .721, the instruct model asked one question per request .715, the instruct model asked all of a passage's
  questions in one prompt (QWEN_MULTI) **.733**.
  - KEV - MULTI: -.012, paired t over documents [-.057, +.032]; within-document bootstrap [-.041, +.016]; Kev ahead
    on 4 of 10 documents. **No difference shown** (predicted, P 65%).
  - QWEN - MULTI: -.018 [-.040, +.005]; bootstrap [-.041, +.006]; 2 of 10. **No difference shown** (predicted, P 70%):
    putting all the questions in one prompt did not hurt the instruct model.
- **Format: reliable.** 0 of 2,043 cells (0 of 275 replies) failed to parse under the grammar (predicted under 1%).
- **Cost: edge gone.** On the same 275 passages and 2,043 questions, one arm after the other:
  - Kev (`/v1/systemone`, one request per passage, server as deployed: 4 slots, 6 threads): 4,109 s, **2.01 s per
    question** (predicted about 1.9).
  - QWEN_MULTI (one chat request per passage, 1 slot, 6 threads, prompt cache off): 3,647 s, **1.79 s per question**
    (predicted about 1.4, range 0.8-2.5).
  - **R = 1.79 / 2.01 = 0.89: "edge gone"** (R at most 1.0; predicted R about 0.75, "edge gone" P 55%).
  - For scale: the same instruct model asked one question per request took 6.05 s per question on these cells
    (missing2, measured), which is where the earlier 5.4x came from.

| | AUROC (mean of 10 docs) | s per question | Failed cells |
|---|---|---|---|
| Kev-4B, /v1/systemone | .721 | 2.01 | - |
| Qwen3.5-4B instruct, one question per request | .715 | 6.05 (missing2) | - |
| Qwen3.5-4B instruct, all questions in one prompt | .733 | 1.79 | 0 of 2,043 |

Against the predictions: every reading went the predicted way. QWEN_MULTI's AUROC (.733) is .003 above the top of its
predicted range (.66-.73), and its cost (1.79 s) is inside its range but above the point guess (1.4).

## Checks
- **Kev's re-timing reproduced its hashed scores**: mean |p(new) - p(missing2)| = .0006 over the 2,043 cells, so the
  timing pass ran the same model on the same inputs.
- **Other work on the machine.** The plan asked for nothing else on the CPU. During the first 20 minutes of Kev's
  68-minute pass I did light work: the contrib result's scoring (about 3 s at 11:03:41), building and publishing the
  curator page and the ledger, and two commits (11:05:24, 11:07:56); the GPT rater's launch at about 11:03 stopped
  at once on its usage limit. Nothing ran during the instruct model's pass apart from a one-line log check each
  minute and the keep-awake helper. Exploratory, after the result: on the 206 passages Kev started after 11:21 UTC,
  Kev took 2.08 s and QWEN_MULTI 1.85 s per question, R 0.889, the same as on all 275.

## Exploratory, after the result
- **There is no question count at which Kev is cheaper here.** By questions per passage (k), R was 0.92 at k = 1
  (33 passages), 0.88 at 2-3 (57), 0.88 at 4-7 (85), 0.87 at 8-15 (72) and 0.92 at 16-44 (28).
- **Why.** Both arms read a passage once. A straight-line fit over the 275 calls gives Kev 6.0 s per passage plus
  1.20 s per question, and QWEN_MULTI 5.15 s plus 1.09 s. Kev's extra question costs its own short prefill in a
  slot plus the decision; the instruct model's costs the question's tokens in the prompt plus about four generated
  tokens ("3: no" and a newline). On this CPU these are about the same. The earlier cost edge (1.4-5.4x,
  `bench/RESULT_cost_curve.md`, `stale/RESULT_missing2.md`) was measured against an instruct model that re-read the
  passage for every question; those numbers stand, but they compared Kev with a weak way of asking.
- The llama.cpp build serving Kev already carries the fix for re-reading the shared state per slot group (the
  10-20 fix, `build-fix`), so that known inefficiency is not the cause.

## What this means for policywatch
- **Nothing measured in policywatch comes from the decision model.** Its base family's ordinary instruct model, asked
  the same question, matched Kev's accuracy wherever it ran (relocation parts A and B, "states the case", missing
  points), its probabilities were not better calibrated (exploratory), and now, asked all of a passage's questions
  in one prompt, it cost no more (one run per arm, servers set up differently: no cost difference shown, corrected
  2026-11-19 from "slightly cheaper"). policywatch's results are those of a 4B LLM reading each passage.
- The tool's results stand as they are; Kev could be replaced by the instruct model with one prompt per passage
  with no measured loss.

## What this does not show
- One machine (CPU, 6 threads per server), one quantization (Q8_0), one prompt wording, one question order (the
  shortlist's). On GPUs with batched serving, or on a hosted decision-model API, the costs differ and were not
  measured.
- Kev's printed p(yes) worked as a label on contrib (p >= 0.90: 86% rated YES, the rest 37%). Whether the instruct
  model's log-odds give an equally good mark was not tested.
- The servers were not set up the same way (Kev 4 slots, the instruct model 1), each as it had been run before; the
  plan fixed this in advance.
