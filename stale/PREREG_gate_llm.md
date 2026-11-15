# The 60 gate cards, answered by GPT and Fable instead of a person (written before either rater runs)

Written 2026-11-15 ~10:20 UTC. A disclosed change to `stale/PREREG_suggest.md`.

## Why
`stale/PREREG_suggest.md` made the stale-suggestion result (`stale/RESULT_suggest.md`) final only if a person
(Ege) answered 60 blind cards and agreed with the grader (Claude Opus) at kappa >= .6. Ege chose not to answer them
and asked for GPT and Fable to answer them instead (2026-11-15). Two more AI raters are not a human check, so this
**cannot make the result final**: it stays PROVISIONAL whatever happens below. What this can show is whether two
raters from outside the grader's own run (one from another company) read the cards the way the grader did.

## Raters
- **GPT:** Codex CLI 0.154.0 (`codex exec`), model gpt-6-astra, reasoning effort xhigh (Ege's config), read-only
  sandbox, run in an empty folder; the cards and instructions arrive in the prompt.
- **Fable:** Claude Fable 5.2, as a Claude Code subagent (`model: fable`), told to read only one file that holds the
  cards and the instructions, and to write its answers to one file.
- Both get the same text: the human page's instructions, verbatim, and the 60 cards from `audit/gate/data.json`
  (platform, document, case, case description, passage), in the page's order. Nothing about strata, the grader's
  labels or any model's picks. Each card is answered yes / no / unsure, with a reason of at most 15 words.
- One run each; no reruns unless a run fails to return all 60 answers in the asked format (then once more, said so).

## What is computed (`stale/gate_llm.py`, the same kappa as `stale.gate score`)
1. Cohen's kappa, each rater vs the grader, on the cards that rater answered yes or no.
2. Kappa GPT vs Fable on the cards both answered yes or no.
3. Per stratum (cited / uncited / none): yes counts for each rater and for the grader.
4. Unsure counts.

## Reading (fixed now)
- **Both raters >= .6 against the grader:** "two other AI raters agree with the grader". The result stays
  provisional; the line is added to `stale/RESULT_suggest.md`.
- **Either rater below .6:** "the other AI raters do not back the grader". The result stays provisional, and its
  headline figure (Kev's first suggestion right for 74% of the 141 points) is marked doubtful wherever it is quoted.
- **Either rater below .4:** as above, and the 74% figure is withdrawn from summaries (README, ledger, drafts) until
  a person checks it; `stale/RESULT_suggest.md` keeps it with the note.
- GPT vs Fable agreement is reported, not used in the reading.

## What this does not touch
The three relocation tests (graded against the curator's own quote), the Clear label, the cost results and the
finder's output do not depend on the grader and are unaffected.
