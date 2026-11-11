#!/usr/bin/env bash
# Overnight: wait for the r20 Kev scorer (PID $1), seed the cache from it, write the accuracy page, then backfill
# ToS/Privacy updates newest-first in slices, rebuilding the site after each slice. Resumable: rerun any time.
F=/c/Users/egeha/projects/decision-serving/play/reviewq/out
PGA=../decision-serving/data/pga-versions
while tasklist //FI "PID eq $1" 2>/dev/null | grep -qi "py.exe"; do sleep 30; done
n=$(grep -c . $F/kev.jsonl)
echo "r20 scorer exited at $(date -u +%T) UTC with $n/70"
if [ "$n" -lt 70 ]; then echo "NOT STARTING: r20 incomplete"; exit 1; fi
cd /c/Users/egeha/projects/policywatch
py -I -m policywatch seed --frozen $F --out out
py -I -m policywatch eval --frozen $F --out out > out/eval.log 2>&1
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  py -I -m policywatch scan --archive $PGA --since $since --out out >> out/scan.log 2>&1
  echo "slice since $since done at $(date -u +%T) UTC (exit $?)"
  py -I -m policywatch report --archive $PGA --out out
done
