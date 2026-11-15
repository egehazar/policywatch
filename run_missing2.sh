#!/usr/bin/env bash
# The missing points larger test (stale/PREREG_missing2.md), then the scanner backfill slices it paused.
# Order: BM25, Kev (port 9995), the reranker (venv), Qwen3.5-4B on port 9996 (host prompt cache off) for the shortlist,
# measures (the blind cards), the outputs' hashes; then the backfill slices (`scan` skips updates already scanned).
# Usage: bash run_missing2.sh
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
echo "missing2 start $(date -u +%T) UTC"
py -m stale.missing2 bm25 > stale/out/missing2_bm25.log 2>&1; echo "missing2 bm25 exit $? at $(date -u +%T) UTC"
if up; then
  py -m stale.missing2 kev >> stale/out/missing2_kev.log 2>&1; echo "missing2 kev exit $? at $(date -u +%T) UTC"
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe -m stale.missing2 rerank >> stale/out/missing2_rerank.log 2>&1; echo "missing2 rerank exit $? at $(date -u +%T) UTC"
  powershell -NoProfile -ExecutionPolicy Bypass -File bench/start_qwen.ps1 -Threads 6 -CacheRam 0 > /dev/null 2>&1
  for i in $(seq 1 60); do up 9996 && break; sleep 5; done
  if up 9996; then py -m stale.missing2 qwen 9996 >> stale/out/missing2_qwen.log 2>&1; echo "missing2 qwen exit $? at $(date -u +%T) UTC"
  else echo "QWEN SERVER DID NOT START at $(date -u +%T) UTC"; fi
  powershell -NoProfile -ExecutionPolicy Bypass -File bench/stop_qwen.ps1 > /dev/null 2>&1
  py -m stale.missing2 measures > stale/out/missing2_measures.log 2>&1; echo "missing2 measures exit $? at $(date -u +%T) UTC"
  if [ -s stale/audit_missing2/cards.md ]; then
    { echo "# scores, measures, cards and key $(date -u +%FT%TZ), before any rating"
      sha256sum stale/out/missing2_kev.json stale/out/missing2_rerank.json stale/out/missing2_bm25.json stale/out/missing2_qwen.json \
        stale/out/missing2_measures.json stale/audit_missing2/cards.md stale/audit_missing2/README.md stale/audit_missing2/verdicts.json \
        stale/out/missing2_key.json | sed 's/  / */'; } >> stale/PREREG_missing2.sha256
    echo "missing2 cards hashed at $(date -u +%T) UTC"
  fi
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: missing2 not run"; fi
echo "missing2 done $(date -u +%T) UTC"
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
echo "backfill all done at $(date -u +%T) UTC"
