# Short question layout for Kev (pre-registered 2026-11-12, before any short-layout request)

## Why
The Kev vs Qwen3.5-4B bench (eval/RESULT_kev_vs_llm.md) read NO CLEAR WINNER on CPU: Kev found 20 of 25 changes
within 182 reviews but cost 179.8 s per update, about 1.14 s per question. Kev's systemone template (in the GGUF,
`tokenizer.chat_template.systemone`) renders each question after the shared state as

    <|fim_middle|>{instructions}<|box_start|>yes[: description]<|box_end|><|box_start|>no[: description]<|box_end|><|fim_suffix|>

and that part is processed once per question. policywatch's wrapper (policywatch/scorer.py `q_obj`) adds two option
descriptions ("Yes, this is true of the text." / "No, this is not true of the text."). Fable r26 (Kev's README and a
llama.cpp decision-model write-up) points out that the per-question cost is the wrapper's own text, and that removing
option descriptions changed a smaller Kev's probabilities (top probability .92 -> .69). This tests the one change.

This is a second test, designed after the bench result was known. The Qwen numbers it is compared with are already
fixed (bench/out/result.json, hashed in eval/PREREG_kev_vs_llm.sha256). The bench's own reading stays NO CLEAR WINNER.

## Arm
KEV-SHORT: the same server (Kev-4B Q8_0, llama.cpp build-fix, port 9995, -np 4) with one request in flight; the same
70 v1 questions and instructions ("Answer this question about the text: {question}"); `criteria` omitted, so the
template shows bare "yes" and "no" in the server's default option order. Every r20 state (35 updates x old/new),
timed as in bench time-kev. Code: bench/short_layout.py (hashed below). Nothing else runs on the CPU during it.

## Measures
- Primary: recall of the 25 gold changes within 182 reviews, ranking by |p_new - p_old| (ties by item id, as KEV).
- CPU seconds per update (both states).
- Also reported: recall at 25/50/100, ambiguous counted as changes, Spearman between the two layouts' |dp|.

## Rules (fixed now)
1. Adopt the short layout in policywatch and stale/ if KEV-SHORT recall@182 >= 19 (KEV had 20) AND its CPU per update
   is <= 0.7 x KEV's 179.8 s. Otherwise keep the r20 wrapper.
2. The bench rule (eval/PREREG_kev_vs_llm.md) applied to KEV-SHORT against LLM-DIFF, reported as this second test's
   reading. Because LLM-DIFF was degenerate (empty on 32 of 35 updates), also report KEV-SHORT vs LLM-QA: "at least as
   good on both" means recall@182 >= 12 and CPU <= 81.7 s per update.
3. Report all counts whatever the outcome. If adopted, cached scores of the two layouts never mix (a new wrapper id).

## Prediction (mine)
CPU per update about 95 s (0.53x); recall@182 between 18 and 21. P(adopt) 55%. P(KEV-SHORT at least as good as
LLM-QA on both) 15%.
