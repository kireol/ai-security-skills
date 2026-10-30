#!/bin/sh
# One command to start a full security assessment.
#
#   scripts/assess.sh                 ask which AI assistant to use, then start it with the kick-off prompt
#   scripts/assess.sh --dashboard     also start the live dashboard and open it in your browser
#   scripts/assess.sh --stop          stop the dashboard
#
# Options: --agent claude|codex|gemini|print   skip the question and use this choice
#          --port N                            dashboard port (default 8770)
#
# Reports and run data go to ~/ai-security-reports/<run-id>/ (override with AISS_REPORTS).

set -eu
REPO=$(cd "$(dirname "$0")/.." && pwd)
DATA=${AISS_DASHBOARD_DATA:-$HOME/.ai-security-dashboard}
REPORTS=${AISS_REPORTS:-$HOME/ai-security-reports}
PORT=8770
DASHBOARD=no
STOP=no
AGENT=""
KNOWN_AGENTS="claude codex gemini"

while [ $# -gt 0 ]; do
  case "$1" in
    --dashboard) DASHBOARD=yes ;;
    --stop) STOP=yes ;;
    --agent) AGENT=${2:-}; shift ;;
    --port) PORT=${2:-}; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1 (see --help)" >&2; exit 2 ;;
  esac
  shift
done

if [ "$STOP" = yes ]; then
  # Prefer the process this script started; otherwise find whatever dashboard is listening on the port.
  pid=""
  [ -f "$DATA/dashboard.pid" ] && pid=$(cat "$DATA/dashboard.pid")
  if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
    pid=""
    for candidate in $(lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null); do
      if ps -p "$candidate" -o command= | grep -q 'dashboard\.py serve'; then pid=$candidate; fi
    done
  fi
  rm -f "$DATA/dashboard.pid"
  if [ -n "$pid" ] && kill "$pid" 2>/dev/null; then
    echo "Dashboard stopped."
  else
    echo "No dashboard is running on port $PORT."
  fi
  exit 0
fi

# Ask which assistant to use before starting anything, so "exit" leaves nothing running.
if [ -z "$AGENT" ]; then
  installed=""
  for a in $KNOWN_AGENTS; do
    if command -v "$a" >/dev/null 2>&1; then installed="$installed $a"; fi
  done
  if [ ! -t 0 ]; then
    AGENT=print
  else
    echo "Which AI assistant should run the assessment?"
    n=0
    for a in $installed; do n=$((n + 1)); echo "  $n) $a"; done
    print_choice=$((n + 1)); exit_choice=$((n + 2))
    echo "  $print_choice) Print the prompt so I can paste it into another assistant"
    echo "  $exit_choice) Exit without doing anything"
    [ -z "$installed" ] && echo "(No supported assistant found on this computer: $KNOWN_AGENTS.)"
    printf "Choose 1-%s: " "$exit_choice"
    read -r choice
    case "$choice" in
      ''|*[!0-9]*) echo "Not a valid choice; nothing started."; exit 1 ;;
    esac
    if [ "$choice" -eq "$exit_choice" ]; then echo "Nothing started."; exit 0
    elif [ "$choice" -eq "$print_choice" ]; then AGENT=print
    elif [ "$choice" -ge 1 ] && [ "$choice" -le "$n" ]; then AGENT=$(echo $installed | cut -d' ' -f"$choice")
    else echo "Not a valid choice; nothing started."; exit 1
    fi
  fi
fi
case "$AGENT" in
  claude|codex|gemini)
    command -v "$AGENT" >/dev/null 2>&1 || { echo "$AGENT isn't installed on this computer." >&2; exit 1; } ;;
  print) ;;
  *) echo "Unknown assistant: $AGENT (use claude, codex, gemini, or print)" >&2; exit 2 ;;
esac

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
    echo "Dashboard started. When you're done, stop it with: scripts/assess.sh --stop"
  fi
  if [ -n "${AISS_DASHBOARD_TOKEN:-}" ]; then TOKEN=$AISS_DASHBOARD_TOKEN; else TOKEN=$(cat "$DATA/token"); fi
  open_url "http://127.0.0.1:$PORT/#token=$TOKEN"
  DASHBOARD_NOTE=" A live dashboard is running and reads the run folder automatically, so always write events there."
fi

PROMPT="Use the full-assessment skill from the ai-security-skills collection at $REPO \
(skills/orchestration/full-assessment/SKILL.md; product skills are in dist/) to run a complete security \
assessment of my network. Start with the kick-off questions. Put the run folder under $REPORTS.$DASHBOARD_NOTE \
Don't change anything without my approval."

cd "$REPO"
case "$AGENT" in
  claude) exec claude "$PROMPT" ;;
  codex) exec codex "$PROMPT" ;;
  gemini) exec gemini -i "$PROMPT" ;;
  print)
    echo
    echo "Paste this into your AI assistant (start it from $REPO so it can read the skills):"
    echo
    echo "$PROMPT"
    if command -v pbcopy >/dev/null 2>&1; then printf '%s' "$PROMPT" | pbcopy; echo; echo "(Copied to the clipboard.)"; fi ;;
esac
