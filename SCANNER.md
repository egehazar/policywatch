# The meaning-diff scanner (`policywatch/`)
The original goal, kept with its results: it failed its pre-registered tests as a detector of real changes.

### Why
Measured on 35 real Terms of Service and Privacy Policy updates (Open Terms Archive, 2,450 update x question pairs).
Two independent LLM raters (not humans) judged each question on the changed excerpt only, not the whole document.
- In 25 of the 2,450 cases both raters' answer flipped, and in 31 more one rater's did. Most real edits are cosmetic
  or structural.
- A common shortcut (re-check every answer whose top-5 retrieved paragraphs, by bge-small, touch a changed
  paragraph) re-read 365 answers. 96% of those had not changed, and it missed 12 of the 25 changes, which sat outside
  the retrieved paragraphs.
- This shows what one retriever misses on one test. It does not show that dependency tracking cannot work.

### How it works
1. **Diff.** Paragraph diff of the two versions, with link targets and whitespace normalized away. Each changed
   block is read together with one unchanged paragraph on either side.
2. **Ask.** One decision-model request per side answers every question in the bank over the same text. Scores are
   cached in SQLite by (model, text hash, question), so no text is read twice.
3. **Rank.** Questions are ranked by |p_new - p_old|. The model is used as a comparator (the same question on two
   versions), never as an oracle: in earlier tests its ranking was reliable while its 0.5 cut-off was not.
4. **Localize.** For each flagged question, the question is re-asked of each changed block alone, and the block
   that moved it most is shown as evidence.
5. **Numbers and links by rule.** Two kinds of change are listed separately, whatever the model says:
   - a paragraph whose number or date tokens changed ("30 days" -> "14 days")
   - a paragraph whose text is unchanged but whose link now points elsewhere (the linked document can carry
     obligations)
6. **Report.** A static HTML site: one page per update, with word-level diffs, linked to the source commit.
7. **Capture noise is labelled, not scored.** In 2026 so far, 267 of the archive's 835 recorded "changes" (32%) are
   not edits.
   - Either the text returned to a recent version, a recurrence (TikTok's UK-ads banner flips on and off between
     captures), or the new capture was cut off part-way (Reddit's privacy policy, cut at a table about every other
     capture).
   - A recurrence can also be a platform retracting and reinstating a change, so recurrences are labelled and shown
     with their diff, never hidden.
   - Across the whole archive it is 426 of 2,672 (`eval/noise_stats.json`).
   - A return to an older version (more than 6 captures or 45 days back) is scored as a real rollback.
   - After a cut-off capture, the next version is compared with the last full one.
8. **Human review.** `python -m policywatch serve` serves the site with buttons to mark each flagged answer changed,
   not changed or unsure, and to record a change the tool missed. Verdicts go to an append-only file, and the index
   shows running precision and audited misses as counts.

More than 80 changed paragraphs counts as a rewrite: the report says "review everything" and scores nothing.

### Questions
`data/bank.json` has 101 yes/no questions made from ToS;DR case titles: the 70 cases approved on at least 100
services, plus every bad or blocker case approved on 30-99. The second group was added after the first 70 turned out
to have no question about AI training, which would have hidden Twitch's 2026-08-12 privacy update. Because that
update motivated the added questions, it is excluded from every accuracy claim; results with the 70 original
questions are reported separately. See `data/BANK.md`.

What this measures: whether a model's answers to generic case questions move between two versions of the changed
text. It does not show that a specific approved answer for that service became wrong. Tying the questions to a
service's actual approved answers (for example its ToS;DR points) is future work.

### Accuracy
Four measurements; the first three are shown on the site's "How it works" page (the third has no entries yet):
1. **Frozen test** (`python -m policywatch eval`): the pre-registered verdict of that test (quoted, never
   recomputed), then recall at k and precision/recall at the flag threshold on the 35 updates above. One-rater items
   are counted both ways. n = 25 real changes, LLM raters, one model.
   - **Result (2026-11-12): the pre-registered test FAILED.** The bar was 24 of the 25 changes within 182 reviewed
     answers, half of the shortcut's 365. The tool's ranked list needed 684.
   - The tool still ranks usefully. At 182 reviews it holds 19 of the 25 changes (20 without the number/date rule);
     the shortcut re-reads 365 and holds 13. But it is not near-complete, and for this job a missed broken answer is
     the costly error.
   - Half of its late misses (3 of the 6 changes found after review 182) are items where the model's answer on the
     old text already disagreed with the raters; such items were missed 3 times in 7, the others 3 in 18 (a side
     check, information only, kept with the r20 review-queue work outside this repo).
   - A blind human check of the LLM raters' answer key is pre-registered (`audit/`, `eval/PREREG_human_audit.md`) but
     not done: no human verdicts yet.
2. **Human write-ups** (`python -m policywatch memocheck`): Open Terms Archive memos about these documents. Each memo
   was mapped to the questions a correct tool should move before anything was scored (`eval/memo_targets.json`,
   hashes in `eval/MEMO_TARGETS.sha256`).
   - A memo counts as caught if one of those questions is flagged or in the update's top 5. A rewrite counts as
     missed.
   - Shown alongside:
     - the count a random ranking would catch
     - a stricter count (a target must be flagged)
     - the original 70-question bank
     - a second rater's mapping
   - 8 of the 19 memos have no recorded update within 10 days and are left out.
   - **Result (2026-11-15): failed.** Caught 1 of 10 judged memos (TikTok's 2026 US rewrite); a random ranking would
     catch about 2. The stricter count is 0 of 9, and the 70-question bank and the second rater's mapping also
     catch 1. One memo has no bank question that fits. The scanner does not find what the archive's editors wrote
     up.
   - **Re-run (2026-11-18), after the backfill scored the updates since 2025-11-11:** unchanged. Caught 1 of 10
     (strict 0 of 9; every bank variant 1), against about 2 expected by chance.
3. **Running human record** (`serve`): precision of flags and audited misses, as counts. No update has been reviewed
   yet (`out/human_record.json`).
4. **Decision model vs an ordinary LLM** (`bench/`, `eval/PREREG_kev_vs_llm.md`, result in
   `eval/RESULT_kev_vs_llm.md`). Same 35 updates and CPU, against Qwen3.5-4B (Kev's base family, instruct, Q8_0).
   - Pre-registered reading: **no clear winner**. Kev finds more, but at more than the 2x CPU the rule allowed.
   - Changes found within 182 reviews, of 25:
     - Kev: 20, at 180 s of CPU per update
     - Qwen answering all 70 questions yes/no on each side: 12, at 82 s
     - Qwen asked to list the changed questions (the pre-registered comparator): 2, at 49 s. It answered "none" on
       32 of 35 updates.
   - On these short excerpts (a few hundred words) Kev costs about 1.1 s per question (fit: 1.14 s per question plus
     0.005 s per character): 80 s for 70 questions, 580 s for 500. On longer text the read itself dominates (about
     7.4 s per 1,400-character passage, measured later; see the cost section above).
   - **Follow-up, pre-registered before it ran (`eval/RESULT_short_layout.md`).** The question wrapper's two option
     descriptions were dropped, so the template shows bare "yes"/"no".
     - Recall 21 of 25 at 102.8 s per update (0.57x), so it was adopted under its rule.
     - Against Qwen's yes/no arm: 21 vs 12 changes at 1.26x the CPU. It is still "no clear winner" under the bench
       rule.
