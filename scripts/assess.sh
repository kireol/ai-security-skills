#!/bin/sh
# One command to start a full security assessment.
#
#   scripts/assess.sh                 start your AI assistant with the kick-off prompt (no dashboard)
#   scripts/assess.sh --dashboard     also start the live dashboard and open it in your browser
#   scripts/assess.sh --stop          stop a dashboard started by this script
#
# Options: --agent claude|codex|print   which assistant to launch (default: claude if installed, else print)
#          --port N                     dashboard port (default 8770)
#
# Reports and run data go to ~/ai-security-reports/<run-id>/ (override with AISS_REPORTS).

set -eu
REPO=$(cd "$(dirname "$0")/.." && pwd)
DATA=${AISS_DASHBOARD_DATA:-$HOME/.ai-security-dashboard}
REPORTS=${AISS_REPORTS:-$HOME/ai-security-reports}
PORT=8770
DASHBOARD=no
AGENT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dashboard) DASHBOARD=yes ;;
    --stop)
      if [ -f "$DATA/dashboard.pid" ] && kill "$(cat "$DATA/dashboard.pid")" 2>/dev/null; then
        rm -f "$DATA/dashboard.pid"; echo "Dashboard stopped."
      else
        echo "No dashboard started by this script is running."
      fi
      exit 0 ;;
    --agent) AGENT=$2; shift ;;
    --port) PORT=$2; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1 (see --help)" >&2; exit 2 ;;
  esac
  shift
done

if [ -z "$AGENT" ]; then
  if command -v claude >/dev/null 2>&1; then AGENT=claude; else AGENT=print; fi
fi

mkdir -p "$REPORTS"
chmod 700 "$REPORTS"

open_url() {
  if command -v open >/dev/null 2>&1; then open "$1"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1
  else echo "Open this in your browser: $1"
  fi
}

DASHBOARD_NOTE=""
if [ "$DASHBOARD" = yes ]; then
  mkdir -p "$DATA"
  if curl -s -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/"; then
    echo "Dashboard already running on port $PORT."
  else
    nohup python3 -I "$REPO/tools/dashboard/dashboard.py" serve --port "$PORT" --data "$DATA" \
      --reports "$REPORTS" >"$DATA/dashboard.log" 2>&1 &
    echo $! >"$DATA/dashboard.pid"
    tries=0
    until curl -s -o /dev/null --max-time 1 "http://127.0.0.1:$PORT/"; do
      tries=$((tries + 1))
      if [ $tries -ge 20 ]; then echo "Dashboard didn't start; see $DATA/dashboard.log" >&2; exit 1; fi
      sleep 0.25
    done
    echo "Dashboard started (stop it with: scripts/assess.sh --stop)."
  fi
  if [ -n "${AISS_DASHBOARD_TOKEN:-}" ]; then TOKEN=$AISS_DASHBOARD_TOKEN; else TOKEN=$(cat "$DATA/token"); fi
  open_url "http://127.0.0.1:$PORT/#token=$TOKEN"
  DASHBOARD_NOTE=" A live dashboard is running and reads the run folder automatically, so always write events there."
fi

PROMPT="Use the full-assessment skill from the ai-security-skills collection at $REPO \
(skills/orchestration/full-assessment/SKILL.md; product skills are in dist/) to run a complete security \
assessment of my network. Start with the kick-off questions. Put the run folder under $REPORTS.$DASHBOARD_NOTE \
Don't change anything without my approval."

case "$AGENT" in
  claude) cd "$REPO" && exec claude "$PROMPT" ;;
  codex) cd "$REPO" && exec codex "$PROMPT" ;;
  print)
    echo
    echo "Paste this into your AI assistant:"
    echo
    echo "$PROMPT"
    if command -v pbcopy >/dev/null 2>&1; then printf '%s' "$PROMPT" | pbcopy; echo; echo "(Copied to the clipboard.)"; fi ;;
  *) echo "Unknown agent: $AGENT (use claude, codex, or print)" >&2; exit 2 ;;
esac
