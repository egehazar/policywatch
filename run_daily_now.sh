#!/usr/bin/env bash
# The daily watch, once, now (2026-11-19): run_daily_after.sh's body without its wait for the port check. The owner
# left the restart order to Claude after the memory reap; the Kev re-timing (addendum 3) goes first and the port
# check last, so the daily no longer waits for it. Writes "daily all done" to the same log.
cd /c/Users/egeha/projects/policywatch
echo "daily start $(date -u +%T) UTC (run_daily_now.sh: not waiting for the port check, see the STOPPED line above)"
cmd.exe //c "$(cygpath -w "$PWD/daily.cmd")"; echo "daily exit $? at $(date -u +%T) UTC"
tail -8 stale/live/daily.log
echo "daily all done at $(date -u +%T) UTC"
