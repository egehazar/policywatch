# Plan: the cost curve on an idle CPU (bench/cost_curve.py)

Written 2026-11-15 ~07:50 UTC, before any timed call (one smoke-test call ran on a scratch copy of one planned
passage while other jobs used the CPU; it is not part of the data). A measurement, not a pass/fail test: it replaces
the fitted, not-isolated cost figures in the write-ups with measured ones.

## Why
The relocation write-ups say Kev-4B costs about 6.9 s per 1,500-character passage plus 1.05 s per question, and its
base family's instruct model (Qwen3.5-4B) about 6.6 s per passage and question, so Kev is slower at one question per
passage and cheaper from two on (1.9-3.1x where documents had 3-7 questions). Those figures come from part B's
timings, which shared the CPU with other jobs, and the reason given for the instruct model's cost ("it reads the
passage again for each question; its hybrid recurrent architecture likely leaves llama.cpp no prefix to reuse") was
never measured.

## What runs
- 60 passages of part B's held-out documents, 1,300-1,500 characters, one per document, each used for exactly one
  call per model (no passage is seen twice by a server, so no cached prefix crosses calls). 16 case questions drawn
  from part B's. 12 passages at each of 1, 2, 4, 8 and 16 questions; call order shuffled (seed 20261115).
- Kev: the Kev-4B Q8 server already running (llama.cpp /v1/systemone, -np 4, -t 6), one request per passage with
  all its questions, no score cache. With -np 4 the server works through the questions 4 slots at a time, which is
  part of what is measured.
- Instruct model: Qwen3.5-4B Q8 on its own server (bench/start_qwen.ps1 -Threads 6 -CacheRam 0, the configuration
  of the relocation arms), the relocation prompt, one request per question, cache_prompt on, the passage's
  questions asked one after another.
- Run after the wider pages' suggestions finish and before the scanner backfill, with nothing else on the CPU (the
  two servers run one at a time: Kev's calls first, then the instruct model's).

## Reported
- Kev: least-squares fit of seconds per call against questions: seconds per passage and per question.
- Instruct model: median seconds per question; the median for the first question of a passage against the later
  ones (later/first).
- Per level: Kev's median seconds per call and per question, the instruct model's per question, and the ratio.
- Break-even questions per passage, and the ceiling ratio (instruct seconds per question / Kev's per question).

## Predictions (mine, before any timed call)
- Kev: 5.5-7.5 s per passage and 0.8-1.2 s per question (idle may be faster than part B's shared CPU).
- Instruct model: 5.5-6.5 s per question; later/first at least .85 (no prefix reuse). If later/first is below .5,
  llama.cpp does reuse the prefix for this model, and the write-ups' explanation of its cost is wrong.
- Ratio instruct/Kev per question: about 0.8 at 1 question, 1.4 at 2, 2.2 at 4, 3.3 at 8, 4.2 at 16.
- I will report whatever comes out and change the write-ups' cost figures to the measured ones.
