# Addendum 2 to stale/PLAN_multiq.md: Kev on one slot, with the server patch fixed for one slot

Written 2026-11-18 ~20:15 UTC. Addendum 1 (`stale/PLAN_multiq_addendum1.md`) was still running at the time; its
result was unknown, apart from its own progress log. Hashed with its code (`stale/PLAN_multiq_addendum2.sha256`)
before it starts.

## Why
Addendum 1 times Kev on a 1-slot server built from the local llama.cpp patch (PR #31502, build-fix). After 109 of
275 passages, it ran at 9.0 s per question, against 1.87 s on the same cells with 4 slots.

The patch creates its prompt checkpoint only for a group of questions that has a parent. With one slot every question
is its own group, so Kev re-reads the whole passage for every question. That is a gap in the patch, not a property
of the model: a server with one slot can reuse the passage as well as one with four, if it keeps a checkpoint.

A fixed patch (v3, `decision-serving/notes/PLAN_v3_one_slot.md`) checkpoints a lone question where its question
begins. This addendum re-times Kev on one slot with it. The 1-slot comparison against the instruct model then uses
a server that does what the 4-slot one already did.

## What runs
- **Server:** Kev-4B, same model file and flags as addendum 1 (`-np 1 -c 16384 -t 6`), built from
  `decision-checkpoints-v3` (build-fix3), on port 9998 (bench/start_kev_np1v3.ps1). It is stopped by PID afterwards.
- **Workload:** the same 275 passages and 2,043 questions, one /v1/systemone request per passage, same order, no
  score cache. Output: stale/out/multiq_kev_np1v3.json.
- **Order:** it starts only after the daily watch that follows the Inspect port check has finished, so nothing else
  of mine is on the CPU.
- **Gate:** it runs only if `decision-serving/notes/PLAN_v3_one_slot.md` read "v3 fixes the one-slot case" on the
  test model.

## Measures and readings (fixed now)
- **Agreement:** mean |p(v3, 1 slot) - p(v2, 1 slot, addendum 1)| over the 2,043 cells. Above .01 the reading is
  "void".
- **Patch speedup:** S = seconds per question v2 1-slot / v3 1-slot. "Speedup on the real workload" if S >= 2 (and
  the agreement passes).
- **Cost against the instruct model:** R = 1.785 (QWEN_MULTI s per question, main run) / v3 1-slot s per question.
  Same bands as before:
  - "Kev's cost edge holds" if R >= 1.5;
  - "edge gone" if R <= 1.0;
  - otherwise "edge reduced".
- **Accuracy:** not re-measured.

## Predictions (written before running)
- Agreement under .005. v3 on one slot splits each prompt where the question starts, as the 4-slot server does, so its
  scores should be nearly identical to the main 4-slot run's (mean |dp| under .001).
- v3 1-slot about 2.25 s per question (1.8-3.0). The first question of a passage still pays the whole passage, about
  9 s; each further one pays only its ~40 question tokens, about 1.2 s.
- S about 4 (3-5).
- R about 0.79:
  - "edge gone" P 85%;
  - "edge reduced" P 14%;
  - "edge holds" P 1%.

  The main result's conclusion, that the cost edge came from serving rather than from the model, would stand.

## What this cannot show
- Same limits as addendum 1: one CPU, one quantization, one prompt wording, and the instruct model not re-timed in
  the same session.
- The patch fix is post hoc, made after addendum 1 showed the gap. Addendum 1's result stands as measured on the
  patch as posted.
