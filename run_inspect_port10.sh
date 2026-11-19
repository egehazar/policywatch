#!/usr/bin/env bash
# inspect_eval/PLAN_port_check_addendum1.md: the port check cut to the first 10 points of sample A (was 40),
# against the repo's own scores. Starts after the 1-slot timing (run_multiq_np1.sh) ends.
cd /c/Users/egeha/projects/policywatch
# (the wait for the 1-slot timing is gone: it ended 2026-11-18)
grep -E '^[0-9a-f]{64} ' inspect_eval/PLAN_port_check_addendum1.sha256 | sha256sum -c --quiet || { echo "HASH MISMATCH: not run"; exit 1; }
echo "port start $(date -u +%T) UTC"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/start_qwen.ps1
for i in $(seq 90); do curl -s -m 5 http://127.0.0.1:9996/health | grep -q ok && break; sleep 5; done
mkdir -p inspect_eval/logs
PYTHONUTF8=1 .venv-inspect/Scripts/inspect.exe eval inspect_eval/relocation.py --model llama-cpp-python/qwen \
  --model-base-url http://127.0.0.1:9996/v1 --max-connections 1 -T samples=A -T first=10 \
  --log-dir inspect_eval/logs --display plain > inspect_eval/logs/run.txt 2>&1
echo "inspect exit $? at $(date -u +%T) UTC"; tail -12 inspect_eval/logs/run.txt
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/stop_qwen.ps1
LOG=$(ls -t inspect_eval/logs/*.eval | head -1)
PYTHONUTF8=1 .venv-inspect/Scripts/python.exe -m inspect_eval.compare "$LOG" inspect_eval/port_check_result.json
{ echo "outputs $(date -u +%FT%TZ)"; sha256sum "$LOG" inspect_eval/port_check_result.json | sed 's/  / */'; } >> inspect_eval/PLAN_port_check_addendum1.sha256
echo "inspect port all done at $(date -u +%T) UTC"
