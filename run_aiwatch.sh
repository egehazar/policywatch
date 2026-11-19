#!/usr/bin/env bash
# aiwatch/PLAN_aiwatch.md: prep (no model), hash check, Kev scores on the deployed server (9995), result.
cd /c/Users/egeha/projects/policywatch
grep -E '^[0-9a-f]{64} ' aiwatch/PLAN_aiwatch.sha256 | (cd aiwatch && sha256sum -c --quiet) || { echo "HASH MISMATCH: not run"; exit 1; }
echo "aiwatch prep start $(date -u +%T) UTC"
py -m aiwatch.backtest prep 5 || { echo "PREP FAILED"; exit 1; }
curl -s -m 15 http://127.0.0.1:9995/health | grep -q ok || { echo "KEV 9995 DOWN: not scored"; exit 1; }
echo "aiwatch score start $(date -u +%T) UTC"
py -m aiwatch.backtest score 9995 || { echo "SCORE FAILED"; exit 1; }
py -m aiwatch.backtest result > aiwatch/out/result.log 2>&1; echo "result exit $? at $(date -u +%T) UTC"; cat aiwatch/out/result.log
{ echo "outputs $(date -u +%FT%TZ)"; sha256sum aiwatch/out/candidates.jsonl aiwatch/out/result.json | sed 's/  / */'; } >> aiwatch/PLAN_aiwatch.sha256
echo "aiwatch all done at $(date -u +%T) UTC"
