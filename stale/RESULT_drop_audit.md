# Result: are the listed drops real platform edits? (the blind audit)

Pre-registration: `stale/PREREG_drop_audit.md`. The pre-registration, the code, the 50 cards, the instructions and the
answer key were hashed at 01:17 UTC on 2026-11-15, before any rating, and the rater's verdicts were hashed before
scoring (`stale/PREREG_drop_audit.sha256`). Scores: `stale/out/drop_audit_result.json`
(`py -m stale.drop_audit score`).

The rater was a Claude subagent (Opus 5.5) that read only the case folder and did not know which list a case came
from. This is an LLM rater's reading, not a person's. It answered GENUINE 35, CAPTURE 15, UNSURE 0.

## Readings
| List | Cases | Real platform edit (GENUINE) | Share, Wilson 95% | Predicted |
|---|---|---|---|---|
| contrib, the 521 listed drops (L) | 30 | 27 | .90 [.74, .97] | 26 of 30 |
| 20 platforms, the 141 listed drops (P) | 10 | 8 | .80 [.49, .94] | 9 of 10 |

| Set aside by the broken-capture guard (G) | Cases | Rated CAPTURE | Predicted |
|---|---|---|---|
| contrib, the 74 set-asides | 10 | 10 | 8 of 10 |

- The contrib list's share is above .80, so under the pre-registered rule the contrib page gets no warning line. The
  README reports the share next to the 521.
- The guard did not set aside any real edit in the 10 sampled (fewer than 5 rated GENUINE): not too eager.
- The 20-platform list, which never had the guard, had 2 capture problems in 10. Neither is the kind the guard
  catches, because neither capture shrank.

## What the 5 listed drops rated CAPTURE were
All five are the archive saving a different variant of the page, not a broken page:
- **Another language**: Telegram's privacy policy, captured in German. The same sentence is in the German section
  3.3.1.
- **Another region**: LinkedIn's capture became the European Regional Privacy Notice, a supplement. Yahoo's became
  the older Oath (EMEA) terms under Irish law. Google's became the same policy version in en-GB, where the sentence
  survives with British spelling ("analyse", "optimise").
- **A lost page header**: on BBC's privacy policy, sections 1-15 are identical. Only the header holding the quote
  ("Page updated: August 2019 Version 3.1") was dropped by the extraction.

The guard's 10 set-asides were all title-only captures (Bing and Skype at 61 characters, Apple Game Center at 83,
Instacart at 29) or a login page (Airbnb).

## Exploratory, after the result: would a language check have caught them?
I compared the share of common English words before and after each audited drop. A drop to under 60% of the earlier
share flags Telegram's German capture. It flags none of the region switches or the header loss, and an absolute
threshold would also flag Orange's French policy, which was French in both captures and was a real edit. One catch
in five does not justify a new guard. Region switches need the archive's own page metadata, not the text.

## What this changes
- README: "521 dropped in a platform edit" now reads with the audit beside it: about 9 in 10 are real edits by
  this rater, the rest are mostly the archive saving another language or region of the page.
- The curator pages already say "a place to look, not a verdict" and show the drop commit, so a curator can see a
  language or region switch in one click. No page change.
