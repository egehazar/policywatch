# Instructions for the rater

ToS;DR (tosdr.org) describes what a service's terms or privacy policy say as short "cases", for example "You waive
your right to a class action". Each card in `cards.md` shows one case and one passage from a service's terms or
privacy policy.

For each card M01-M70, answer one question: **does this passage state or clearly imply the case?**

- **YES**: a careful reader could quote this passage as evidence for the case.
- **PARTLY**: the passage states something close (narrower, broader, or only part of the case), or implies it only
  weakly.
- **NO**: the passage does not state or imply the case.

Judge each card on its own text: do not assume anything about the rest of the document or the service. There is no
expected distribution of answers.

Write your answers into `verdicts.json` in this folder: for each card, `"verdict"` is one of `YES`, `PARTLY`, `NO`,
and `"why"` is one short sentence (the words that state the case, or what is missing). Read only the files in this
folder.
