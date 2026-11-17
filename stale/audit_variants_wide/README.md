# Instructions for the checker

ToS;DR (tosdr.org) describes what a service's terms or privacy policy say as short "cases", for example "You waive
your right to a class action". A curator attaches a case to a service as an approved "point".

`items.json` lists suggested cases, each for one service. `approved_cases.json` lists, for each of those services, the
case titles that already have an approved point on it.

For each item, compare its suggested case with the service's approved cases (titles only) and give one category:

- **VARIANT**: an approved case on the service makes essentially the same claim (a rewording, narrower or broader, a
  near-synonym, an older or newer version of the same case).
- **CLOSE**: an approved case overlaps clearly but makes a distinguishably different claim.
- **NONE**: no approved case on the service states anything close.

Judge each item on its own. There is no expected distribution of answers.

Write `variants.json` in this folder: an object keyed by item id, each value
`{"category": "VARIANT" | "CLOSE" | "NONE", "nearest_approved_case": "<the closest approved title, or empty for NONE>",
"why": "<one short sentence>"}`. Every item must be filled. Read only the files in this folder.
