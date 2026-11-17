#!/bin/bash
# GPT rates the contrib cards as a second rater (stale/PLAN_missing_contrib.md: "GPT (Codex) rates the same cards as a
# second rater: reported beside the first, never read"). Same prompt build as the larger test's
# (README lines 1-16, the reply instruction, the cards verbatim), one codex run per folder, in an empty directory.
# Usage: bash run.sh <scratch dir>
H="$1"; PW=/c/Users/egeha/projects/policywatch; mkdir -p "$H/empty" "$H/out" "$H/logs"
for x in a b; do
  F="$PW/stale/audit_contrib_$x"
  { head -n 16 "$F/README.md"
    cat <<'EOT'
Do not open, list or search any file or directory, do not run commands, and do not use the web: everything you need
is below. Your final reply must be ONLY one JSON object covering every card, with nothing before or after it, in this
shape: {"C001": {"verdict": "YES", "why": "one short sentence"}, ...}, using each card's own id. "verdict" is one of
YES, PARTLY, NO, and "why" is one short sentence (the words that state the case, or what is missing).

==========================================================================================
EOT
    cat "$F/cards.md"; } > "$H/prompt_$x.md"
  sha256sum "$H/prompt_$x.md" "$F/cards.md"
  s=$(date -u +%T); codex exec --skip-git-repo-check -s read-only -C "$H/empty" -o "$H/out/gpt_contrib_$x.txt" - < "$H/prompt_$x.md" > "$H/logs/gpt_contrib_$x.txt" 2>&1
  echo "gpt contrib $x exit $? $s-$(date -u +%T) UTC"
  grep -q -i 'usage limit' "$H/logs/gpt_contrib_$x.txt" && { echo "USAGE LIMIT: $(grep -i -o 'try again at [^.]*' "$H/logs/gpt_contrib_$x.txt" | head -1)"; exit 3; }
  cp "$H/prompt_$x.md" "$H/out/gpt_contrib_$x.txt" "$PW/stale/out/missing_contrib_gpt_raw/" 2>/dev/null
  cp "$H/logs/gpt_contrib_$x.txt" "$PW/stale/out/missing_contrib_gpt_raw/gpt_contrib_${x}_log.txt"
done
echo "gpt contrib done $(date -u +%T) UTC"
