# Instructions for the rater

Open Terms Archive saves the text of services' terms and privacy policies each time they change. ToS;DR volunteers
quote these documents as evidence. Each case below is one quote that was present in an earlier capture of a document
and absent from the next capture.

For each case C01-C50 in `cards.md`, answer one question:

> Between these two captures, did the service change the document's own text so that the quoted wording is no longer
> there?

- **GENUINE**: yes. The later capture is a real version of the document, and the wording was removed or rewritten
  (moving it elsewhere with different words, shortening it, or deleting the section all count).
- **CAPTURE**: no. The later capture is not a faithful copy of the document: truncated, a title or menu only, a
  login, cookie, consent or error page, a different page, or the document in another language or for another region.
  If the wording is still there in substance and only formatting or extraction changed (for example markup, list
  markers, line breaks or tables flattened), that is also CAPTURE.
- **UNSURE**: the card and the full files do not settle it.

Each card shows the quote, the passage of the earlier capture holding it, the passage of the later capture most like
that one, both lengths, and the start of the later capture. When the card is not enough, open `Cxx_before.md` and
`Cxx_after.md` in this folder (the full captures) and search them.

Write your answers into `verdicts.json`: for each case, `"verdict"` is one of `GENUINE`, `CAPTURE`, `UNSURE`, and
`"why"` is one short sentence of evidence (what changed, or what is wrong with the later capture). Judge each case on
its own. Read only the files in this folder.
