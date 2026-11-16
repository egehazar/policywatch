# Missing points on the remaining documents: a build, with one accuracy check fixed in advance

Written 2026-11-16 ~08:05 UTC, after the larger test's result (`stale/RESULT_missing2.md`) and before any score of
these documents exists from this run. Code: `stale/missing_wide.py` (its `measures` step tested on random stand-in
scores only; `prep` run, its document list is below).

## What and why
The two tests covered 14 documents of at most 40 passages. The private curator page should cover every "Privacy
Policy" and "Terms of Service" of the 20 platforms. The rest are mostly longer (5-146 passages), where asking Kev
every case on every passage would take about 19 h; the larger test found the cascade (the reranker's top 3 passages
per case, then Kev on those) lost nothing measurable in AUROC against Kev on every passage (+.002 [-.014, +.017],
exploratory) and rated 73 of 100 top suggestions YES. So this run uses the cascade: about 5 h of reranker and at most
about 3 h of Kev.

## Documents (fixed rule, applied to `stale/out/reloc_docs.json`)
Every document named exactly "Privacy Policy" or "Terms of Service" of the 20 platforms that neither test covered:
20 documents, 1,003 passages, 59,014 reranker cells, at most 3,693 Kev cells. Candidate cases as in the tests (cases
approved at least MIN_POINTS times on that document type, plus the document's positives). One change on purpose:
cases with any approved point on the platform in `stale/data/<platform>.json` are excluded, including points whose
quote is under 3 words (the larger test's caveat: `stale/match.py` skips those).

## The accuracy check (fixed now)
On the 7 documents with at least 10 known positives (Facebook, Reddit and YouTube privacy policies; Snapchat,
Spotify, Twitch and X terms): AUROC of positives against negatives, CASCADE_KEV (Kev on the shortlist) and RERANK
(every passage), mean over the 7, and CASCADE_KEV - RERANK with a 95% interval from 2,000 draws resampling positives
and negatives within each document (seed 20261124). Reading: interval above 0 "CASCADE_KEV better", below 0 "RERANK
better", otherwise "no difference shown". There are no blind cards in this run: the page will say that these
documents' suggestions were not rated, and give the larger test's rated accuracy for the cascade and this check.

Predictions: CASCADE_KEV .66-.76, RERANK .58-.68, difference +.02 to +.10, P(CASCADE_KEV better) 50%. These
documents are longer and hold more positives per document than the tests', so the shortlist may miss more.

## Order and the shared CPU
The scanner backfill (`run_missing2.sh`, restarted 07:21 UTC; about 13 minutes per update and hundreds of updates
left) is stopped for this run and restarted after it (`scan` skips updates already scanned; the update or two in
progress are lost). Order: reranker (the dedupe-research venv, offline), Kev (port 9995), measures, the page.
