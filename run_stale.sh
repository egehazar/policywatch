#!/usr/bin/env bash
# After the short-layout test (11-12): the stale-point suggestion arms of stale/PREREG_suggest.md, cheap ones first,
# then Kev (~4 CPU hours), then the rest of run_next.sh (triage hints, memo check, backfill).  Usage: bash run_stale.sh
# The archive must stay at the HEAD the gold was built on: stale.daily must not run until this finishes.
PGA=../decision-serving/data/pga-versions
VENV=/c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe     # has sentence_transformers + bge cached
PW="py -m policywatch"
cd /c/Users/egeha/projects/policywatch
want=$(python -c "import json;print(json.load(open('stale/out/fullread/key.json'))['archive_head'])")
have=$(git -C $PGA rev-parse HEAD)
if [ "$want" != "$have" ]; then echo "ARCHIVE MOVED ($have, gold built on $want): stop"; exit 2; fi
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; }

for arm in quote_bm25 hunk; do py -m stale.suggest $PGA $arm > stale/out/suggest_$arm.log 2>&1; echo "suggest $arm exit $? at $(date -u +%T) UTC"; done
for arm in bge quote; do $VENV -m stale.suggest $PGA $arm > stale/out/suggest_$arm.log 2>&1; echo "suggest $arm exit $? at $(date -u +%T) UTC"; done
if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC"; exit 2; fi
py -m stale.suggest $PGA kev > stale/out/suggest_kev.log 2>&1; echo "suggest kev exit $? at $(date -u +%T) UTC"
{ echo "# arms $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum stale/out/suggest_*.jsonl; } >> stale/PREREG_suggest.sha256
py -m stale.report https://github.com/OpenTermsArchive/pga-versions kev; echo "page rebuilt with kev at $(date -u +%T) UTC"

# rest of run_next.sh
py -m stale.triage score > stale/out/triage.log 2>&1; echo "triage score exit $? at $(date -u +%T) UTC"
if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC: no memo check"; exit 2; fi
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
$PW report --archive $PGA --out out
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up; then echo "MODEL SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
