# policywatch

When a platform changes its terms or privacy policy, which approved answers about it stopped being true?

policywatch reads each update from [Open Terms Archive](https://opentermsarchive.org). It asks a small decision model
every question in a fixed bank (for example "Does the text state or clearly imply: the service can delete your account
without notice?") of the old changed text and of the new changed text, then lists the answers whose score moved. A
person reviews that short list instead of re-reading every answer.

It runs on a desktop CPU with no API key: Kev-4B (Q8) served by llama.cpp's `/v1/systemone` endpoint.

## Why
Measured on 35 real Terms of Service and Privacy Policy updates (Open Terms Archive, 2,450 update x question pairs,
two independent LLM raters):
- Only 25 of the 2,450 answers actually changed. Most real edits are cosmetic or structural.
- The usual rule re-checks every answer whose top-5 retrieved paragraphs changed. It re-read 364 answers, and 96% of
  them had not changed.
- It also missed 12 of the 25 real changes, because the edit that changed them was outside their retrieved
  evidence. Dependency tracking cannot see these by construction.

## How it works
1. **Diff.** Paragraph diff of the two versions, with link targets and whitespace normalized away. Each changed
   block is read together with one unchanged paragraph on either side.
2. **Ask.** One decision-model request per side answers every question in the bank over the same text. Scores are
   cached in SQLite by (model, text hash, question), so no text is read twice.
3. **Rank.** Questions are ranked by |p_new - p_old|. The model is used as a comparator (the same question on two
   versions), never as an oracle: in earlier tests its ranking was reliable while its 0.5 cut-off was not.
4. **Localize.** For each flagged question, the question is re-asked of each changed block alone, and the block
   that moved it most is shown as evidence.
5. **Numbers by rule.** A paragraph whose number or date tokens changed ("30 days" -> "14 days") is listed
   separately, whatever the model says.
6. **Report.** A static HTML site: one page per update, with word-level diffs, linked to the source commit.

More than 80 changed paragraphs counts as a rewrite: the report says "review everything" and scores nothing.

## Accuracy
See `out/eval.json` and the site's "How it works" page. These are filled from the frozen test above by
`python -m policywatch eval`. The numbers describe that one test (n = 25 real changes, LLM raters, one model). They
are not a guarantee.

## Run
```
llama-server -m kev-4b-q8.gguf --port 9995 -np 4 -c 16384      # a llama.cpp build with /v1/systemone
python -m policywatch scan   --archive path/to/pga-versions --since 2026-10-01
python -m policywatch report --archive path/to/pga-versions
python -m unittest discover -s tests
```
Python 3.10+, standard library only.

## Credits
- Documents: Open Terms Archive, pga-versions (Platform Governance Archive, University of Bremen), ODC-BY 1.0.
- Questions: case titles from ToS;DR (tosdr.org).
- The re-asking mechanic follows jev-why (github.com/Mahad-007/jev-why).
