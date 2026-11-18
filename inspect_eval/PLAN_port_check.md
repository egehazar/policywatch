# Plan: does the Inspect AI port reproduce the repo's own harness?

Written 2026-11-18 ~20:20 UTC, before the run. Hashed with the code and data (`inspect_eval/PLAN_port_check.sha256`)
before it starts.

## Why
The relocation test (`stale/PREREG_relocate*.md`) was run with the repo's own scripts. `inspect_eval/` re-implements
it as an Inspect AI task so that others can run it with standard tooling. A port is only useful if it computes the
same thing. This run checks that on one model and a fixed slice, not a new result.

## What runs
- Model: Qwen3.5-4B instruct (Q8_0, thinking off), the same file and server flags as the repo's run
  (`bench/start_qwen.ps1`: llama.cpp build-fix, `-np 1 -c 16384 -t 6 --jinja`), port 9996.
- Points: the first 40 points of sample A's fixed order (`-T samples=A -T first=40`), 1,640 passage-question
  cells. Not all 200: the repo measured this model at 9.4 s per cell on this CPU, so 200 points (8,386 cells) would
  take about a day.
- `inspect eval inspect_eval/relocation.py --model llama-cpp-python/qwen --model-base-url http://127.0.0.1:9996/v1
  --max-connections 1 -T samples=A -T first=40`, then `python -m inspect_eval.compare <log>`.
- It starts after the 1-slot timing run (`stale/PLAN_multiq_addendum1.md`) ends, so it does not touch that timing.

## Readings (fixed now)
- Repo scores: `stale/out/reloc_qwen.json` (the repo's Qwen arm on sample A, 2026-11-14).
- Per cell: mean |log-odds (Inspect) - log-odds (repo)| over the 1,640 cells.
- On the 40 points: hit@1 and MRR from each set of scores, with the same tie rule.
- **"Port reproduces the repo"** if the mean |difference| is at most .05 and hit@1 and MRR each differ by at most
  .01. Otherwise **"port differs"**, reported with the cells that differ most and the cause if found.

## Predictions (written before running)
- Mean |difference| under .02; top passage the same on at least 38 of 40 points; "port reproduces the repo" (85%).
- The main risk: Inspect sends the request differently (message format, extra parameters), so the chat template
  renders a different prompt. The smoke test below checks one point first.

## What this cannot show
- That the task is a good benchmark: the gold is one curator quote per point (DATA_CARD.md, Limits).
- Anything about other models or about samples B and D, which the port has not been run on.

## Smoke test before hashing (2026-11-18 ~17:06-17:11 UTC)
The first point of sample A (A-318964, 27 passages; it is also the first of the 40 measured points), run with the
command above and `-T first=1` while the scanner backfill shared the CPU (4 min 34 s). Every one of the 27 log-odds
equalled the repo's stored value exactly (mean and max |difference| 0.0); hit@1 0 and reciprocal rank .5 in both.
The plan and predictions above were written before this result and are left as written.
