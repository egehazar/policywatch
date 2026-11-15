#!/bin/bash
# GPT rates the missing-points pilot's blind cards (stale/PREREG_missing.md, measure 3: "GPT (Codex) rates the same
# cards as a second rater if its usage allows (reported, not read)"). Waits for the pilot's measures step, builds the
# prompt exactly as for the states-the-case folders (README lines 1-16, the reply instruction, the cards verbatim), one run.
# Usage: bash run.sh <scratch dir> <after-wide chain output file>
H="$1"; W="$2"; PW=/c/Users/egeha/projects/policywatch
echo "gpt missing waiter start $(date -u +%T) UTC"
until grep -qE 'missing measures exit|missing pilot not run|KEV SERVER DOWN' "$W" 2>/dev/null; do sleep 120; done
grep -E 'missing (kev|rerank|measures) exit|missing pilot not run|KEV SERVER DOWN' "$W"
if ! grep -q 'missing measures exit 0' "$W" || [ ! -s "$PW/stale/audit_missing/cards.md" ]; then echo "NO CARDS: gpt not run $(date -u +%T) UTC"; exit 2; fi
{ head -n 16 "$PW/stale/audit_missing/README.md"
  cat <<'TXT'
Do not open, list or search any file or directory, do not run commands, and do not use the web: everything you need
is below. Your final reply must be ONLY one JSON object covering every card, with nothing before or after it, in this
shape: {"S001": {"verdict": "YES", "why": "one short sentence"}, ...}, using each card's own id. "verdict" is one of
YES, PARTLY, NO, and "why" is one short sentence (the words that state the case, or what is missing).

==========================================================================================
TXT
  cat "$PW/stale/audit_missing/cards.md"; } > "$H/prompt.md"
sha256sum "$H/prompt.md" "$PW/stale/audit_missing/cards.md"
s=$(date -u +%T); codex exec --skip-git-repo-check -s read-only -C "$H/empty" -o "$H/out/gpt_missing.txt" - < "$H/prompt.md" > "$H/logs/gpt_missing.txt" 2>&1
echo "gpt missing exit $? $s-$(date -u +%T) UTC"
grep -q -i 'usage limit' "$H/logs/gpt_missing.txt" && echo "USAGE LIMIT: $(grep -i -o 'try again at [^.]*' "$H/logs/gpt_missing.txt" | head -1)"
echo "gpt missing done $(date -u +%T) UTC"
