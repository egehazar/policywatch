#!/usr/bin/env bash
# stale/PREREG_relocate2.md: RERANK, QWEN, KEV_SHORT, Part C (proposed quote), eval. Then the steps of run_stale.sh
# that were deferred to make room for it (triage hints, memo check, backfill), still on the r20 wrapper.
# Start only after run_stale.sh was stopped past "page rebuilt with kev".   Usage: bash run_reloc2.sh
PGA=../decision-serving/data/pga-versions
VENV=/c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe     # sentence-transformers + the reranker cached
PW="py -m policywatch"
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:$1/health | grep -q 200; }
echo "reloc2 start $(date -u +%T) UTC"

HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 $VENV -m stale.relocate2 rerank > stale/out/reloc2_rerank.log 2>&1
echo "rerank exit $? at $(date -u +%T) UTC"

powershell -NoProfile -File bench/start_qwen.ps1 -Threads 6
for i in $(seq 1 60); do up 9996 && break; sleep 5; done
if up 9996; then
  py -m stale.relocate2 qwen 9996 > stale/out/reloc2_qwen.log 2>&1; echo "qwen exit $? at $(date -u +%T) UTC"
else echo "QWEN SERVER DID NOT START at $(date -u +%T) UTC"; fi
powershell -NoProfile -File bench/stop_qwen.ps1

if ! up 9995; then echo "KEV SERVER DOWN at $(date -u +%T) UTC"; exit 2; fi
py -m stale.relocate2 kevshort 9995 > stale/out/reloc2_kevshort.log 2>&1; echo "kevshort exit $? at $(date -u +%T) UTC"
py -m stale.relocate2 quote 9995 > stale/out/reloc2_quote.log 2>&1; echo "quote exit $? at $(date -u +%T) UTC"
py -m stale.relocate2 eval > stale/out/reloc2_eval.log 2>&1; echo "eval exit $? at $(date -u +%T) UTC"
{ echo "# result $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  sha256sum stale/out/reloc_rerank.json stale/out/reloc_qwen.json stale/out/reloc_kevshort.json stale/out/reloc_quote.json stale/out/reloc2_result.json; } >> stale/PREREG_relocate2.sha256
echo "reloc2 done at $(date -u +%T) UTC"; grep -A4 '"reading"' stale/out/reloc2_eval.log

# deferred from run_stale.sh
py -m stale.triage score > stale/out/triage.log 2>&1; echo "triage score exit $? at $(date -u +%T) UTC"
if ! up 9995; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: no memo check"; exit 2; fi
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
$PW report --archive $PGA --out out
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up 9995; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
echo "all done at $(date -u +%T) UTC"
