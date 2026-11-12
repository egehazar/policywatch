#!/usr/bin/env bash
# After the Kev-vs-Qwen benchmark (11-12): the pre-registered relocation test first, then the stale triage hints,
# then the memo check and the backfill from run_day.sh. Usage: bash run_after.sh <N>   (N from stale/PREREG_relocate.md)
N=$1
PGA=../decision-serving/data/pga-versions
PW="py -m policywatch"
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; }
if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC"; exit 2; fi

# 1. relocation (stale/PREREG_relocate.md): baselines, Kev on the first N points, evaluation, hashes
py -m stale.relocate base > stale/out/reloc_base.log 2>&1; echo "relocate base exit $? at $(date -u +%T) UTC"
py -m stale.relocate kev $N > stale/out/reloc_kev.log 2>&1; echo "relocate kev N=$N exit $? at $(date -u +%T) UTC"
py -m stale.relocate eval $N > stale/out/reloc_eval.log 2>&1; echo "relocate eval exit $? at $(date -u +%T) UTC"
{ echo "# result N=$N $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum stale/out/reloc_kev.json stale/out/reloc_base.json stale/out/reloc_result.json stale/relocate.py; } >> stale/PREREG_relocate.sha256
grep -A12 '"hit_at"' stale/out/reloc_eval.log | head -14; grep -A3 'KEV_minus' stale/out/reloc_eval.log

# 2. triage hints for the stale page (one question per passage pair), then rebuild it
py -m stale.triage score > stale/out/triage.log 2>&1; echo "triage score exit $? at $(date -u +%T) UTC"
py -m stale.report

# 3. memo check, then backfill (as in run_day.sh)
if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC: no memo check"; exit 2; fi
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
$PW report --archive $PGA --out out
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
