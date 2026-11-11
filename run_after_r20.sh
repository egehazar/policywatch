#!/usr/bin/env bash
# Starts the first real policywatch scan once the r20 Kev scorer (PID $1) has exited with all 70 states scored.
F=/c/Users/egeha/projects/decision-serving/play/reviewq/out
while tasklist //FI "PID eq $1" 2>/dev/null | grep -qi "py.exe"; do sleep 30; done
n=$(grep -c . $F/kev.jsonl)
echo "r20 scorer exited at $(date -u +%T) UTC with $n/70"
if [ "$n" -lt 70 ]; then echo "NOT STARTING: r20 incomplete"; exit 1; fi
cd /c/Users/egeha/projects/policywatch
py -I -m policywatch seed --frozen $F --out out
py -I -m policywatch scan --archive ../decision-serving/data/pga-versions --since 2026-10-01 --out out > out/scan.log 2>&1
echo "scan exit $? at $(date -u +%T) UTC"; tail -3 out/scan.log
py -I -m policywatch report --archive ../decision-serving/data/pga-versions --out out
