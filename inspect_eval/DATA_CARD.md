# Relocation set: where does a document state a ToS;DR case now?

602 approved [ToS;DR](https://tosdr.org) points. Each has a case (e.g. "You must provide your legal name, pseudonyms
are not allowed"), the current text of the document it quotes, cut into passages, and the gold: the passages that
hold the curator's own quote. The task is to rank the passages so a gold one comes first. Exported from the repo's
three pre-registered relocation tests by `py -m inspect_eval.export`; the Inspect AI task is `relocation.py`.

## Files
- `data/points.jsonl`: one line per point: `id` (sample-point), `sample` (A, B or D), `rank` (position in that
  sample's fixed order), `point` (ToS;DR point id), `service`, `document`, `n_passages`, `case_title`, `question`
  (the yes/no question every model arm was asked), `gold` (passage indices).
- `data/documents.jsonl`: one line per document: `document`, `passages_sha` (the digest the tests checked), `passages`.

## The three samples
| Sample | Points | Documents | Text | Plan |
|---|---|---|---|---|
| A | 200 | 29 | current version (Open Terms Archive pga-versions HEAD), 17 of the 20 large platforms | `stale/PREREG_relocate.md` |
| B | 202 | 71 | ToS;DR's own stored copy, 41 services outside those platforms | `stale/PREREG_relocate2.md` (part B) |
| D | 200 | 70 | current version in Open Terms Archive's contrib collection, 47 other services | `stale/PREREG_relocate_d.md` |

- Points: approved ToS;DR points whose quote is still in the text, drawn in a fixed seeded order (sample A: the
  first 200 of that order).
- Passages: paragraphs joined up to 1,500 characters.
- Gold: the passages holding at least .3 of the quote's word 6-grams (1-3 passages). The curator's quote marks one
  place where the case is stated; a case can be stated elsewhere too, so every ranker's hit rate is a lower bound.

## Reference results (hit@1, from the repo's own harness; RESULTS.md)
- A: Kev-4B .62, Qwen3.5-4B (this task's prompt) .60, reranker .55, BM25 .36, bge-small .295.
- B: Kev-4B .75, Qwen3.5-4B .74, reranker (bge-reranker-v2-m3) .65, bge-small .43, BM25 .41.
- D: Kev-4B .625, reranker .565, BM25 .345, bge-small .34 (Qwen3.5-4B was not run on D).

## Licences and attribution
- ToS;DR point data (case titles, quotes, stored documents in sample B): CC BY-SA 3.0, tosdr.org.
- Document text in samples A and D: Open Terms Archive (pga-versions, Platform Governance Archive, University of
  Bremen; contrib), ODC-BY 1.0. The documents are the services' own terms and policies.
- The code in this folder: MIT (the repository's LICENSE).

## Limits
- Gold comes from one curator quote per point, matched by string overlap, not from a person reading each passage.
- English only; terms of service and privacy policies only.
