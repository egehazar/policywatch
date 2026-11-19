# Result, addendum 3: with the patch fixed for one slot (v4), Kev on one slot costs what it did on four

Plan: `stale/PLAN_multiq_addendum3.md`, hashed with its code (`stale/multiq_np1v4.py`, `run_multiq_np1v4.sh`,
`bench/start_kev_np1v4.ps1`, `bench/stop_kev_np1v4.ps1`) before it started (`stale/PLAN_multiq_addendum3.sha256`,
commit 5590e85). The run went from 13:21:39 to 14:34:01 UTC on 2026-11-19; the run script hashed the outputs at
14:34:04Z. Numbers: `stale/out/multiq_np1v4_result.json`. Gate: the v4 checks on the test models read "v4 fixes the
one-slot case" (`decision-serving/RESULTS.md`, 2026-11-18 v4).

## Readings (fixed in advance)
- **Agreement: passes.** Mean |p(v4, 1 slot) - p(v2, 1 slot, addendum 1)| = .0031 over the 2,043 cells (void above
  .01).
- **Patch: "speedup on the real workload".** Kev on one slot with v4: 4,335 s for 2,043 questions, **2.12 s per
  question**, against 8.87 with the patch as posted (addendum 1). S = 8.87 / 2.12 = **4.18** (threshold 2).
- **Cost against the instruct model: edge gone.** R = 1.785 (QWEN_MULTI, main run) / 2.12 = **0.84** (edge gone at 1.0
  or below).

## Against the predictions
| | Predicted | Measured |
|---|---|---|
| Agreement with v2 1-slot | under .005 | .0031 |
| Mean \|dp\| against the main 4-slot run | under .005 | .0006 |
| v4 1-slot, s per question | about 2.1 (1.7-3.0) | 2.12 |
| S | about 4.2 (3-5) | 4.18 |
| R | about 0.85 | 0.84 |
| Reading | "edge gone" P 85% | edge gone |

All six went as predicted, and the sizes were close. The prediction came from the main 4-slot run's fit (6.0 s per
passage plus 1.2 s per question), on the reasoning that one slot doing the questions one after another should cost
about the same once the passage is kept. That is what happened (below).

## Descriptive numbers (not readings)
- **Per-passage fit** over the 275 requests (straight line, seconds against questions per passage):

  | Server | Per passage | Per question |
  |---|---:|---:|
  | v4, 1 slot (this run) | 6.1 s | 1.3 s |
  | v2, 4 slots (main run) | 6.0 s | 1.2 s |
  | v2, 1 slot (addendum 1) | -5.2 s | 9.6 s |

  With v4 the passage is paid once and each further question costs about what it does on 4 slots.
- **Totals:** 4,335 s (v4, 1 slot), 4,109 s (v2, 4 slots), 18,111 s (v2, 1 slot).
- **Answers:**
  - **v4 1-slot against the 4-slot run:** 1,648 of the 2,043 probabilities are bitwise equal. The largest difference
    is .018, and no answer crosses 0.5.
  - **v4 1-slot against v2 1-slot:** 5 answers cross 0.5 and the largest difference is .023. These are exactly the
    5 cells where addendum 1's 1-slot run already differed from the 4-slot run (the same set). So it is the
    no-checkpoint run, which re-reads the passage in different batches, that differs from the other two.

## Checks
- **Other work on the machine.**
  - My daily watch had ended at 13:20:42 UTC, and addendum 2's chain had exited at its gate ("v3 checks did not pass:
    not run").
  - During the run, mine were only waiting scripts:
    - the queued port check, which checked a log file every 2 minutes;
    - a keep-awake.
  - The deployed Kev server (port 9995, 4 slots) stayed up, as in addendum 1. As far as I know it served no requests.
  - What the owner did on the PC during the run is not known.
- The progress log (`stale/out/multiq_np1v4.log`, every 25 passages) shows no stall.
- The v4 server was stopped by PID afterwards (`bench/stop_kev_np1v4.ps1`, PID 31132), and I verified that it was
  gone.

## What this means
- **For policywatch: nothing changes.** The main result (`stale/RESULT_multiq.md`) read "edge gone" with Kev on its
  deployed 4 slots. On one slot, with the checkpoint working, Kev costs about the same (R 0.84 against 0.89).
- **For the serving patch.** On the real workload, PR #31502 as posted gives a 1-slot server no speedup. v4 closes
  that gap: one slot now matches four within 6% of total time, with the same answers.
  - The evidence on the test models is in `decision-serving/RESULTS.md` (2026-11-18 v4 and 2026-11-19 master).
  - This run is the one measurement on the real model.

## What this does not show
- **Same limits as addenda 1 and 2:** one CPU, one quantization, one prompt wording, and the instruct model not
  re-timed in the same session.
- **v4 is post hoc.** It was made after addendum 1 showed the gap, and it is local and uncommitted (branch
  `decision-checkpoints-v4`, built as build-fix4 on 954de24). Addendum 1's result stands as measured on the patch as
  posted.
- **One request per passage.** Each request carries all of a passage's questions. A client that sends one question
  per request is not helped by v4: the last task of a request has no next task to share a checkpoint with
  (`decision-serving/notes/PR31502_v4_evidence.md`). This workload does not test that case.
