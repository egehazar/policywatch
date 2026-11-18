# Result, addendum 1: Kev on a 1-slot server is 4.4x slower, because the server patch keeps no checkpoint with one slot

Plan: `stale/PLAN_multiq_addendum1.md`, hashed with its code (`stale/multiq_np1.py`, `run_multiq_np1.sh`,
`bench/start_kev_np1.ps1`, `bench/stop_kev_np1.ps1`) before it started (`stale/PLAN_multiq_addendum1.sha256`). The run
went from 17:43:31 to 22:45:31 UTC on 2026-11-18; the run script hashed the outputs at 22:45:36Z. Numbers:
`stale/out/multiq_np1_result.json`.

## Readings (fixed in advance)
- **Agreement: passes.** Mean |p(1 slot) - p(4 slots, main run)| = .0031 over the 2,043 cells (void above .01;
  predicted under .005). The 1-slot server computed the same scores.
- **Cost: edge gone.** Kev on one slot: 18,111 s for 2,043 questions, **8.87 s per question** (4 slots in the main
  run: 2.01). R1 = 1.785 (QWEN_MULTI, main run) / 8.87 = **0.20: "edge gone"**.

Against the predictions: the reading and the agreement went as predicted ("edge gone" P 85%), and Kev was slower
than on 4 slots (P 70%). The size was badly wrong: predicted about 2.3 s per question (2.0-3.0) and R1 about 0.78;
measured 8.87 and 0.20. The section below explains the cause.

## Why it is this slow (found during the run)
- A straight-line fit over the 275 requests: on 1 slot, **-5.2 s + 9.56 s per question**; on 4 slots (main run),
  6.0 s + 1.20 s per question. With one slot every question pays for the whole passage again. With four slots the
  passage is paid once and each further question about 1.2 s.
- The cause is in the server patch, not in the model. The llama.cpp build serving Kev (`build-fix`, the local branch
  behind PR #31502) keeps a prompt checkpoint only for a group of questions that has a parent. The server groups
  questions by the number of slots, and a group needs at least two questions to have a parent. With `-np 1` every
  question is its own group, so no checkpoint is kept, and a hybrid model like Kev-4B cannot roll its state back
  without one: the server re-reads the passage for every question. The server log fits this: each ~365-token
  request took about 10 s although consecutive requests shared about 89% of their tokens. This was found by reading
  the code during the run, and is being checked on a build (below).
- So this addendum measured the patch as posted, on one slot. It does not measure what a 1-slot server could do
  with a checkpoint.

## Checks
- **Other work on the machine.** The plan allowed the GPT rater queued for 22:20 UTC and said to report an overlap.
  It ran 22:23-22:33 UTC (Codex, cloud model; locally a CLI process). Its ingest and report (a few seconds of
  Python) and two commits followed by 22:35. The 9 passages that finished after 22:23 ran at 10.5 s per question,
  against 1.48 s for the same passages on 4 slots. Before 22:20 the rate was 8.74 against 2.05. Passage length
  differs between these subsets and affects the two servers differently, so the slowdown cannot be measured from
  this. Without those passages, the 263 that finished before 22:20 give 8.74 s per question and R1 0.20, the same
  reading. Otherwise I did only light work during the run (reading and editing files, web fetches, commits). The v3
  build and its checks were queued to start after the run ended.

## What follows
- **A fixed patch (v3)**, local branch `decision-checkpoints-v3` in decision-serving, keeps a checkpoint where a lone
  question begins, so the next question on the same passage starts from it. Its checks run on the small test model
  before anything else (`decision-serving/notes/PLAN_v3_one_slot.md`, pre-registered).
- **Addendum 2** (`stale/PLAN_multiq_addendum2.md`, pre-registered, commit 4fbc14f) re-times Kev on one slot with v3
  on the same 2,043 questions, if those checks pass. Predicted: about 2.25 s per question, R about 0.79, still
  "edge gone".

## What this means for policywatch
- Nothing changes. The main result (`stale/RESULT_multiq.md`) already read "edge gone" with Kev on its deployed 4
  slots; on 1 slot, with the patch as posted, Kev is slower still.
- It is a finding about the serving patch: PR #31502 as posted gives no speedup to a 1-slot server.

## What this does not show
- What Kev costs on one slot with a working checkpoint. That is addendum 2.
- Same limits as the main plan: one CPU, one quantization, one prompt wording. The instruct model was not re-timed
  in the same session.
