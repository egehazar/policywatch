# Addendum 1 to stale/PLAN_multiq.md: Kev re-timed on a 1-slot server

Written 2026-11-18 ~13:50 UTC, after the main result (stale/RESULT_multiq.md: R 0.89, "edge gone") and before this
run. Hashed with its code (stale/multiq_np1.py, run_multiq_np1.sh) before it starts.

## Why
In the main run Kev's server had 4 slots (as deployed) and the instruct model's 1. A review (Fable 5.2, 2026-11-18)
named "4 slots against 1" as the first objection an engineer would raise. This addendum removes it: Kev on a server
set up like the instruct model's, timing only.

## What runs
- A second Kev server, same build (llama.cpp build-fix), same model file (Kev-4B-Q8_0.gguf), set up like the
  instruct model's server: `-np 1 -c 16384 -t 6`, port 9997. It starts after the main chain ends ("chain all done")
  and is stopped by PID afterwards.
- The same 275 passages and 2,043 questions as the main run, one /v1/systemone request per passage, same order, no
  score cache. Output: stale/out/multiq_kev_np1.json.
- Nothing else on the CPU by me. The GPT rater queued for 22:20 UTC (stale/missing_contrib_gpt) runs mostly in the
  cloud; if it overlaps the timing, that is reported.

## Measures and readings (fixed now)
- **Agreement.** Mean |p(1 slot) - p(4 slots, main run)| over the 2,043 cells. If above .01, the scores differ
  enough that the timing is not of the same computation: the reading is "void".
- **Cost.** Kev1 = seconds per question on the 1-slot server. R1 = QWEN_MULTI s per question (1.785, measured in the
  main run, not re-run) / Kev1.
  - Reading: "Kev's cost edge holds" if R1 >= 1.5; "edge gone" if R1 <= 1.0; otherwise "edge reduced" (the main
    plan's bands).
- Accuracy is not re-measured (the scores are the same computation if agreement passes).

## Predictions (written before running)
- Agreement under .005.
- Kev1 about 2.3 s per question (2.0-3.0): one slot runs the questions one after another instead of 4 at a time.
  P(Kev1 > 2.011, slower than with 4 slots) 70%.
- R1 about 0.78; "edge gone" P 85%, "edge reduced" P 13%, "edge holds" P 2%.

## What this cannot show
- The instruct model is not re-timed in the same session; machine state can differ by some percent between runs
  hours apart.
- Same limits as the main plan: one CPU, one quantization, one prompt wording.

## Smoke test before hashing (2026-11-18 ~13:46-13:48 UTC)
One pilot passage (stale/out/missing_docs.json, first document, first piece; not a measured cell), 6 questions, on
the 1-slot server and then on the deployed 4-slot one, both sharing the CPU with the scanner backfill (so the times,
111 s and 79 s, mean nothing). The 1-slot server answered; its p(yes) differed from the 4-slot server's by .0005 to
.008, mean .004, under the .01 void line. The predictions above are left as written.
