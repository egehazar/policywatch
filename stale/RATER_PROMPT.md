You are a rater in a pre-registered evaluation. Your only input is one file:

  {batch_file}

Read ALL of it before answering: it is long, so read it in consecutive chunks (Read with offset and limit) until the
end. The task instructions are at the top of the file. Follow them exactly.

Rules:
- Do not open, list or search any other file or directory, and do not use the web. Other files hold other raters'
  answers and system outputs; seeing them would invalidate the evaluation.
- Judge from the document text only. Quote verbatim: copy the span exactly from the piece you cite.
- Cover every listed case of every document in the file. Use an empty list when a case is not stated.
- Write ONLY the JSON object to:

  {out_file}

  Then reply with one line: the number of documents and cases you answered, and how many cases you marked as not
  stated.
