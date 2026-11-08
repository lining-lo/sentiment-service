#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$APP_DIR/.user-frontend.pid"

if [[ ! -f "$PID_FILE" ]]; then
    printf 'user-frontend is not running.\n'
    exit 0
fi

pid="$(<"$PID_FILE")"
if kill -0 "$pid" 2>/dev/null; then
    kill -- "-$pid" 2>/dev/null || kill "$pid"
    printf 'user-frontend stopped (PID %s).\n' "$pid"
else
    printf 'Process %s was not found.\n' "$pid"
fi

rm -f "$PID_FILE"