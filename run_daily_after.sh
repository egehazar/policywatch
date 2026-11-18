#!/usr/bin/env bash
# The daily watch, once, after the Inspect port check (run_inspect_port.sh) ends. run_multiq.sh's call failed
# ("'daily.cmd' is not recognized", 2026-11-18 17:42 UTC); this calls it by its full Windows path.
cd /c/Users/egeha/projects/policywatch
until grep -q "inspect port all done" inspect_eval/port_chain.log; do sleep 120; done
echo "daily start $(date -u +%T) UTC"
cmd.exe //c "$(cygpath -w "$PWD/daily.cmd")"; echo "daily exit $? at $(date -u +%T) UTC"
tail -8 stale/live/daily.log
echo "daily all done at $(date -u +%T) UTC"
