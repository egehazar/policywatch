# Addendum 3 to stale/PLAN_multiq.md: Kev on one slot, with the server patch fixed for one slot (v4)

Written 2026-11-18 ~23:08 UTC. Hashed with its code (`stale/PLAN_multiq_addendum3.sha256`) before it starts. At the
time, the v4 checks on the test models were building; their result was unknown.

## Why
Addendum 1 (`stale/RESULT_multiq_addendum1.md`) measured Kev on a 1-slot server at 8.87 s per question, against 2.01
with 4 slots. The server patch (PR #31502 as posted, `build-fix`) keeps no checkpoint with one slot, so every question
re-reads the whole passage. Addendum 2 was to re-time Kev with a fixed patch (v3), but v3 failed its checks
(`decision-serving/RESULTS.md`, 2026-11-18: it changed nothing on one slot) and addendum 2 does not run. v4
(`decision-serving/notes/PLAN_v4_one_slot.md`) checkpoints a lone question where its prompt stops matching the next
question's. This addendum re-times Kev on one slot with v4.

## What runs
- **Server:** Kev-4B, same model file and flags as addendum 1 (`-np 1 -c 16384 -t 6`), built from
  `decision-checkpoints-v4` (build-fix4), on port 9998 (bench/start_kev_np1v4.ps1). It is stopped by PID afterwards.
- **Workload:** the same 275 passages and 2,043 questions, one /v1/systemone request per passage, same order, no
  score cache. Output: stale/out/multiq_kev_np1v4.json.
- **Order:** it starts only after the daily watch that follows the Inspect port check has finished, and after
  addendum 2's chain has ended, so nothing else of mine is on the CPU.
- **Gate:** it runs only if `decision-serving/notes/PLAN_v4_one_slot.md` read "v4 fixes the one-slot case".

## Measures and readings (fixed now; the same as addendum 2)
- **Agreement:** mean |p(v4, 1 slot) - p(v2, 1 slot, addendum 1)| over the 2,043 cells. Above .01 the reading is
  "void".
- **Patch speedup:** S = seconds per question v2 1-slot / v4 1-slot. "Speedup on the real workload" if S >= 2 (and
  the agreement passes).
- **Cost against the instruct model:** R = 1.785 (QWEN_MULTI s per question, main run) / v4 1-slot s per question.
  Bands:
  - "Kev's cost edge holds" if R >= 1.5;
  - "edge gone" if R <= 1.0;
  - otherwise "edge reduced".
- **Accuracy:** not re-measured.

## Predictions (written before running)
- Agreement under .005. Against the main 4-slot run, mean |dp| under .005 (v4 cuts the prompt at the shared prefix
  as the 4-slot server does, but at a different place in the batch).
- v4 1-slot about 2.1 s per question (1.7-3.0). The main 4-slot run fits 6.0 s per passage plus 1.2 s per question.
  On one CPU, one slot doing the questions one after another should cost about the same.
- S about 4.2 (3-5).
- R about 0.85:
  - "edge gone" P 85%;
  - "edge reduced" P 14%;
  - "edge holds" P 1%.

  The main result's conclusion would stand.

## What this cannot show
- Same limits as addenda 1 and 2: one CPU, one quantization, one prompt wording, and the instruct model not re-timed
  in the same session.
- Both patch fixes are post hoc, made after addendum 1 showed the gap. Addendum 1's result stands as measured on the
  patch as posted.
