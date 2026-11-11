#!/usr/bin/env bash
# Overnight: wait for the r20 Kev scorer (PID $1), seed the cache from it, write the accuracy page, scan the
# memo-matched updates (human gold), then backfill ToS/Privacy updates newest-first in slices, rebuilding the site
# after each. Resumable: rerun any time. (Not `py -I`: isolated mode drops the cwd, so the package is not importable.)
F=/c/Users/egeha/projects/decision-serving/play/reviewq/out
PGA=../decision-serving/data/pga-versions
PW="py -m policywatch"
while tasklist //FI "PID eq $1" 2>/dev/null | grep -qi "py.exe"; do sleep 30; done
n=$(grep -c . $F/kev.jsonl)
echo "r20 scorer exited at $(date -u +%T) UTC with $n/70"
if [ "$n" -lt 70 ]; then echo "NOT STARTING: r20 incomplete"; exit 1; fi
cd /c/Users/egeha/projects/policywatch
$PW seed --frozen $F --out out || exit 2
$PW eval --frozen $F --out out > out/eval.log 2>&1
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1
echo "memocheck done at $(date -u +%T) UTC (exit $?)"; tail -14 out/memocheck.log
$PW report --archive $PGA --out out
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1
  echo "slice since $since done at $(date -u +%T) UTC (exit $?)"
  $PW report --archive $PGA --out out
done
