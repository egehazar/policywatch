#!/bin/bash
# Rater 2 (GPT-6 via Codex) on ledger cards: one run per batch, no web search, read-only sandbox.
# Usage: bash aiwatch/run_gpt_rater.sh p1   (from the policywatch folder). Skips batches already answered in full;
# on a usage-limit error it waits 20 minutes and retries.
PH=${1:-p1}; L=aiwatch/out/ledger
for f in $L/batch_${PH}_*.txt; do
  b=$(basename $f .txt); b=${b#batch_}; out=$L/answers_gpt_$b.jsonl
  n=$(grep -c "=== CARD" $f)
  tries=0
  while [ $tries -lt 4 ]; do
    if [ -f $out ] && [ "$(grep -c '"card"' $out)" -ge "$n" ]; then echo "$b done ($n)"; break; fi
    P=$(mktemp)
    cat > $P <<PROMPT
You are a blind rater for a research study. Read ONLY this file: C:/Users/egeha/projects/policywatch/$f
It starts with instructions, then $n cards. Do not open any other file and do not look anything up; judge only from
the text on each card. Follow the instructions exactly. Be strict: a sentence that only says the company uses AI
features, or that third-party models exist, is not a grant; a grant must let the company (or partners it shares
with) use users' content or personal data to train or improve AI/ML models. Read each card in full.
Your final message must be exactly $n JSON lines, one per card, nothing else:
{"card": "<id>", "label": "<NEW|WIDER|SAME|NO|UNCLEAR>", "scope": "<THIRD|GENERAL|NARROW|->", "quote": "<the deciding AFTER sentence, or ->"}
PROMPT
    codex exec -s read-only -C /c/Users/egeha/projects/policywatch --skip-git-repo-check -o $out.tmp - < $P > $L/gpt_rater_$b.log 2>&1
    rm -f $P
    if [ -f $out.tmp ] && [ "$(grep -c '"card"' $out.tmp)" -ge "$n" ]; then mv $out.tmp $out; echo "$b ok $(date -u +%H:%M)"; continue; fi
    if grep -q "usage limit" $L/gpt_rater_$b.log; then echo "$b usage limit $(date -u +%H:%M), waiting"; sleep 1200; else tries=$((tries+1)); echo "$b failed $(date -u +%H:%M) (try $tries)"; tail -3 $L/gpt_rater_$b.log; sleep 60; fi
  done
done
echo "gpt rater $PH all done"
