#!/usr/bin/env bash
# After the relocation test (11-12): the pre-registered short-layout test alone on the CPU, then the rest of
# run_after.sh (stale triage hints, memo check, backfill).  Usage: bash run_next.sh
PGA=../decision-serving/data/pga-versions
FROZEN=../decision-serving/play/reviewq/out
PW="py -m policywatch"
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; }
if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC"; exit 2; fi

# 1. short layout (eval/PREREG_short_layout.md): timing alone, then eval and hashes
py -m bench.short_layout time 9995 $FROZEN > bench/out/short_time.log 2>&1; echo "short time exit $? at $(date -u +%T) UTC"
py -m bench.short_layout eval $FROZEN > bench/out/short_eval.log 2>&1; echo "short eval exit $? at $(date -u +%T) UTC"
{ echo "# short result $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum bench/out/kev_short.jsonl bench/out/short_result.json bench/short_layout.py; } >> eval/PREREG_short_layout.sha256
grep -E '"adopt_short"|"bench_rule|KEV-SHORT' bench/out/short_eval.log | head -8

# 2. triage hints for the stale page, then rebuild it
py -m stale.triage score > stale/out/triage.log 2>&1; echo "triage score exit $? at $(date -u +%T) UTC"
py -m stale.report

# 3. memo check, then backfill
if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC: no memo check"; exit 2; fi
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
$PW report --archive $PGA --out out
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
