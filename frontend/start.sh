#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$APP_DIR/.user-frontend.pid"
STDOUT_LOG="$APP_DIR/user-frontend.log"

if [[ -f "$PID_FILE" ]]; then
    pid="$(<"$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
        printf 'user-frontend is already running (PID %s).\n' "$pid"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

cd "$APP_DIR"
setsid npm run dev -- --host 0.0.0.0 >"$STDOUT_LOG" 2>&1 &
pid=$!
printf '%s\n' "$pid" >"$PID_FILE"

printf 'user-frontend started (PID %s).\n' "$pid"
printf 'URL: http://localhost:3000\n'