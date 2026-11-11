# Addendum 2026-11-11T21:37:47Z: second rater for memo targets (sensitivity only)
- Fable 5.2 (claude.ai chat 14b31dc3, r23) maps the same 11 memos to bank v2 questions, from the memo titles only,
  blind to my mapping and to any Kev output (out/updates holds 0 records; the brief
  is notes/fable52_r23_brief.md in decision-serving).
- Primary result: memo_targets.json (mine, hashed 21:34:10Z). Reported alongside: Fable's mapping, the agreement
  (Jaccard per memo), and the caught count under Fable's targets and under the union.

# Addendum 2026-11-11T22:20:12Z: after an independent code review, before any memo update is scored
- out/updates holds 0 records.
- Bug fix to MATCH the frozen rule: rewrites now count as NOT caught, so they enter the "judged" denominator. The
  code had dropped them.
- Added and reported, never replacing the primary count:
  - (a) the expected number caught by a random ranking under the same rule (top max(5, flags) of n, per commit);
  - (b) a STRICT variant: a target must be flagged (|dp| >= .3), no top-5 rule, the 'broad' memo excluded.
- The about page now states that 8 of the 19 memo-documents have no recorded update within +-10 days and are left
  out.
- The noise classifier changed (partial = new side only; reverts limited to 6 versions / 45 days; diff against the
  last full version after a cut). This can change which memo updates get scored, e.g. TikTok 2024-04-17 is now a real
  change.
