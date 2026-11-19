# Addendum 1 to inspect_eval/PLAN_port_check.md: the port check on 10 points instead of 40

Written 2026-11-19 ~12:57 UTC, before any complete run. Hashed (`inspect_eval/PLAN_port_check_addendum1.sha256`).

## What changed and why
- **Points:** the first 10 points of sample A's fixed order (`-T first=10`, about 410 cells, about an hour), instead
  of 40 (1,640 cells, 3-4.5 hours).
- **Why:**
  - Two attempts at 40 points were stopped before finishing, neither giving a result (logs in
    `inspect_eval/logs/interrupted/`). The first was stopped for the owner's sleep. The second was reaped for low
    memory: the Qwen server with its 8 GB prompt cache reached 12.7 GB.
  - An independent review (Fable 5.2, 2026-11-19) judged that 40 points changes no decision, since the smoke point
    already matched exactly, and advised about 10 or none. 10 keeps a check beyond the smoke point at a quarter of
    the memory-hours.
- **Order:** it runs after policywatch addendum 3 (Kev re-timing), and only once at least 14 GB of RAM is free.
- **Unchanged:** the model, the server flags (`bench/start_qwen.ps1`, 8 GB cache), the command apart from `first`,
  the repo scores, the readings ("port reproduces the repo" if mean |difference| <= .05 and hit@1 and MRR each
  differ by at most .01) and the compare script.

## Predictions (written before running)
- Mean |difference| under .02, the top passage the same on all 10 points, "port reproduces the repo" (85%, as
  before).
- With 10 points, one changed top passage moves hit@1 by .1, so the hit@1 and MRR lines are stricter per point than
  with 40.
