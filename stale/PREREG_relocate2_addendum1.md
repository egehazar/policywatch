# Addendum 1 to parts A and B (`stale/PREREG_relocate2.md`, `stale/PREREG_relocate2b.md`): run order and the Qwen
# server's memory

Written 2026-11-13 ~13:00 UTC. At this point only part A's RERANK arm and the first 4 of 29 documents of part A's QWEN
arm had been scored. No evaluation of either part had been run or looked at.

## What happened
- `run_night.sh` started at 01:27 UTC. RERANK finished at 02:22.
- The QWEN arm then ran into a memory shortage. llama.cpp's host prompt cache (default 8 GiB, about 110 MiB per
  entry for Qwen3.5's hybrid state) grew the Qwen server to 12.7 GB. With Kev's server (4 GB) and the browsers, the PC
  ran low on memory: Claude Code stopped its background tasks around 02:40 (the script itself kept running). The first
  QWEN document took 7.7 hours, about 93 s per cell, against about 6 s per cell once memory settled.
- At 12:37 UTC QWEN had finished 4 of 29 documents. At that rate the two parts would have run until about 11-15.

## Changes (none touches an arm, a prompt, a score or a reading)
1. **The Qwen server's prompt cache is off** (`--cache-ram 0`, via a new `-CacheRam` option of
   `bench/start_qwen.ps1`, default unchanged).
   - The cache was never used: all 1,745 QWEN requests so far evaluated their whole prompt (the shortest 173
     tokens), as expected for a hybrid recurrent model with a different piece or question in every request.
   - Check: 8 cells already scored (2 per finished document, drawn with seed 7) were scored again with the cache
     off. All 8 gave the same log-odds and the same yes+no mass to 6 decimals.
2. **Run order.** `run_resume.sh` runs the same commands as `run_night.sh` in this order:
   - part B's base arms (RERANK, BGE, BM25) and Kev arms (KEV, KEV_SHORT);
   - part A's KEV_SHORT and the quote step;
   - the QWEN server (cache off), part A's QWEN (resuming from document 5, as the pre-registrations allow for a
     failed arm), then part B's QWEN;
   - part A's eval and result hashes, part B's eval and result hashes;
   - the deferred steps of `run_stale.sh`, unchanged.
   The QWEN arm was stopped by me at 12:38 UTC, 6 minutes into document 5. That document is scored again from the
   start.
3. **Interim looks.** Readings that do not involve QWEN (part A's R2 and R3, part C; part B's B0, B2 and B3) may be
   computed as soon as their arms finish. No remaining step can be changed by them: every arm, prompt and reading is
   fixed, and the official `eval` steps run unchanged at the end.

## Effect on reported cost
QWEN's `cost_sec_per_cell` for part A includes the 7.7 hours of the first document under memory pressure. The result
reports it with and without the first 4 documents. Cost is not part of any reading.
