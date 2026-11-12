# policywatch

When a platform changes its terms or privacy policy, which approved answers about it stopped being true?

policywatch reads each update from [Open Terms Archive](https://opentermsarchive.org). It asks a small decision model
every question in a fixed bank (for example "Does the text state or clearly imply: the service can delete your account
without notice?") of the old changed text and of the new changed text, then lists the answers whose score moved. A
person reviews that short list instead of re-reading every answer.

It runs on a desktop CPU with no API key: Kev-4B (Q8) served by llama.cpp's `/v1/systemone` endpoint.

## Why
Measured on 35 real Terms of Service and Privacy Policy updates (Open Terms Archive, 2,450 update x question pairs).
Two independent LLM raters (not humans) judged each question on the changed excerpt only, not the whole document.
- In 25 of the 2,450 cases both raters' answer flipped, and in 31 more one rater's did. Most real edits are cosmetic
  or structural.
- A common shortcut (re-check every answer whose top-5 retrieved paragraphs, by bge-small, touch a changed
  paragraph) re-read 365 answers. 96% of those had not changed, and it missed 12 of the 25 changes, which sat outside
  the retrieved paragraphs.
- This shows what one retriever misses on one test. It does not show that dependency tracking cannot work.

## How it works
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

## Questions
`data/bank.json` has 101 yes/no questions made from ToS;DR case titles: the 70 cases approved on at least 100
services, plus every bad or blocker case approved on 30-99. The second group was added after the first 70 turned out
to have no question about AI training, which would have hidden Twitch's 2026-08-12 privacy update. Because that
update motivated the added questions, it is excluded from every accuracy claim; results with the 70 original
questions are reported separately. See `data/BANK.md`.

What this measures: whether a model's answers to generic case questions move between two versions of the changed
text. It does not show that a specific approved answer for that service became wrong. Tying the questions to a
service's actual approved answers (for example its ToS;DR points) is future work.

## Accuracy
Three measurements, all shown on the site's "How it works" page:
1. **Frozen test** (`python -m policywatch eval`): the pre-registered verdict of that test (quoted, never
   recomputed), then recall at k and precision/recall at the flag threshold on the 35 updates above. One-rater items
   are counted both ways. n = 25 real changes, LLM raters, one model.
   - **Result (2026-11-12): the pre-registered test FAILED.** The bar was 24 of the 25 changes within 182 reviewed
     answers, half of the shortcut's 365. The tool's ranked list needed 684.
   - The tool still ranks usefully. At 182 reviews it holds 19 of the 25 changes (20 without the number/date rule);
     the shortcut re-reads 365 and holds 13. But it is not near-complete, and for this job a missed broken answer is
     the costly error.
   - Most of its late misses are updates where the model already misread the old text.
   - A blind human check of the LLM raters' answer key is in progress (`audit/`, `eval/PREREG_human_audit.md`).
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
3. **Running human record** (`serve`): precision of flags and audited misses, as counts.

## Stale evidence for ToS;DR points (`stale/`)
ToS;DR approves each point with a quote from the platform's document. When the platform rewrites that passage, the
point keeps pointing at text that is no longer there. `stale/` checks every approved quote against every recorded
version of the platform's documents in Open Terms Archive. This part is string matching only: no model decides
anything.

- **Snapshot 2026-11-12.** 22 pga-versions platforms are on ToS;DR; 20 have approved points with a quote, 1,114 in
  all.
  - 757 quotes are in the current text, 83 partly and 97 gone. 177 are in no archived version: the document is not
    tracked, or the quote is older than the archive.
  - 141 quotes dropped in an edit by the platform itself (82 gone, 59 partly), each with the archive commit where
    it dropped. 39 more dropped at an archive extraction change or have no single drop version, and are not listed.
  - For 133 of the 141, ToS;DR's own stored copy of the document still holds the quote: the copy predates the edit,
    and a re-crawl would mark them "approved-not-found". For 8, the stored copy no longer holds the quote, yet the
    point is approved (`stale/phoenix.py`).
- **Prior art.** ToS;DR already marks a point "approved-not-found" when a re-crawl misses its quote. Curators then
  re-find the quote by hand (their Dec 2020 re-crawl did this to 1,589 points). What this adds: when the quote dropped,
  whether the platform or the archive changed, and the passage that replaced it.
- **Curator page.** `py -m stale.report` writes `out/site/stale.html`: each point with the old passage, the most
  similar new passage (or "no similar passage") and the drop commit. `stale/out/stale_points.csv` has one row per
  point.
- **Daily.** `py -m stale.daily <pga-versions>` fast-forwards the archive, refreshes ToS;DR's approved points
  incrementally (one request per platform, plus one per new or edited point) and lists what changed since the last run:
  new drops, new points, recovered quotes. Output goes to `stale/live/` (`digest.html`, one JSON per run). The
  snapshot above is never rewritten.
- **Where the decision model would come in: relocation.** When a quote is gone, a curator has to find the passage that
  now states the case, or decline the point. A pre-registered test (`stale/PREREG_relocate.md`, hashed before any
  arm was scored) asks whether Kev-4B finds the curator's own quoted passage among a document's 1,500-character pieces
  better than bge-small and BM25. It uses the points whose quote is still present, so the curator's quote is the
  answer key. Result: pending.

## Run
```
llama-server -m kev-4b-q8.gguf --port 9995 -np 4 -c 16384      # a llama.cpp build with /v1/systemone
python -m policywatch scan   --archive path/to/pga-versions --since 2026-10-01
python -m policywatch report --archive path/to/pga-versions
python -m policywatch serve                                    # review at http://127.0.0.1:8787
python -m unittest discover -s tests
```
Python 3.12+ (tested on 3.14), standard library only.

## Credits
- Documents: Open Terms Archive, pga-versions (Platform Governance Archive, University of Bremen), ODC-BY 1.0.
- Questions: case titles from ToS;DR (tosdr.org).
- The re-asking mechanic follows jev-why (github.com/Mahad-007/jev-why).
