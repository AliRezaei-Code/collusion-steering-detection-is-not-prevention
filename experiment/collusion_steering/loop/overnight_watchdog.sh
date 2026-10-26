#!/usr/bin/env bash
# Watchdog for the overnight loop: restart the orchestrator if it dies.
set +e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="$ROOT/loop/overnight_watchdog.log"
DURATION="${1:-28800}"
END=$(( $(date +%s) + DURATION ))

echo "overnight watchdog start $(date -u +%Y-%m-%dT%H:%M:%SZ) duration=${DURATION}s" >> "$LOG"

while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$ROOT/loop/OVERNIGHT_DONE.md" ]; then
    echo "overnight watchdog: DONE found, exiting" >> "$LOG"
    exit 0
  fi
  if ! pgrep -f "loop/overnight_orchestrator.py" >/dev/null 2>&1; then
    REMAIN=$(( END - $(date +%s) ))
    if [ "$REMAIN" -le 0 ]; then
      break
    fi
    echo "overnight watchdog: orchestrator missing; restarting for ${REMAIN}s at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
    python3 loop/overnight_orchestrator.py --duration "$REMAIN" >> "$LOG" 2>&1 &
  fi
  sleep 60
done

echo "overnight watchdog end $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
