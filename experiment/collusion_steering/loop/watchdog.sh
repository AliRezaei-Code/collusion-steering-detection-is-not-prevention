#!/usr/bin/env bash
# Watchdog: keep the critic-actor orchestrator alive for the loop window.
# Restarts only if the orchestrator process is gone and DONE.md is absent.
set +e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="$ROOT/loop/watchdog.log"
DURATION="${1:-7200}"
END=$(( $(date +%s) + DURATION ))

echo "watchdog start $(date -u +%Y-%m-%dT%H:%M:%SZ) duration=${DURATION}s" >> "$LOG"

while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$ROOT/loop/DONE.md" ]; then
    echo "watchdog: DONE.md found, exiting $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
    exit 0
  fi
  if ! pgrep -f "loop/orchestrator.py" >/dev/null 2>&1; then
    REMAIN=$(( END - $(date +%s) ))
    if [ "$REMAIN" -le 0 ]; then
      break
    fi
    echo "watchdog: orchestrator missing; restarting for ${REMAIN}s at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
    python3 loop/orchestrator.py --duration "$REMAIN" >> "$LOG" 2>&1 &
  fi
  sleep 60
done

echo "watchdog end $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
