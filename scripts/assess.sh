#!/bin/sh
# One command to start a full security assessment.
#
#   scripts/assess.sh                 ask which AI assistant to use and whether to start the live dashboard,
#                                     then start the assistant with the kick-off prompt
#   scripts/assess.sh --stop          stop the dashboard
#
# Options: --agent claude|codex|gemini|print   skip the question and use this choice
#          --local | --lan | --no-dashboard    skip the dashboard question: viewable from this computer only,
#                                              from your LAN, or no dashboard
#          --port N                            dashboard port (default 8770)
#          --no-lookup                         don't ask an outside service for your public address
#
# Reports and run data go to ~/ai-security-reports/<run-id>/ (override with AISS_REPORTS).

set -eu
REPO=$(cd "$(dirname "$0")/.." && pwd -P)
DATA=${AISS_DASHBOARD_DATA:-$HOME/.ai-security-dashboard}
REPORTS=${AISS_REPORTS:-$HOME/ai-security-reports}
PORT=8770
DASHBOARD=""
STOP=no
AGENT=""
ACCESS=""
LOOKUP=yes
KNOWN_AGENTS="claude codex gemini"

while [ $# -gt 0 ]; do
  case "$1" in
    --stop) STOP=yes ;;
    --agent) AGENT=${2:-}; shift ;;
    --local) DASHBOARD=yes; ACCESS=local ;;
    --lan) DASHBOARD=yes; ACCESS=lan ;;
    --no-dashboard) DASHBOARD=no ;;
    --port) PORT=${2:-}; shift ;;
    --no-lookup) LOOKUP=no ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
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
    command -v lsof >/dev/null 2>&1 || echo "(lsof isn't installed, so only a dashboard started by this script can be found.)"
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

# Whether to start the live dashboard, and who may view it. A computer without a screen has no browser, so
# "this computer only" would mean nobody can see it unless they use an SSH tunnel.
if [ -z "$DASHBOARD" ]; then
  if [ ! -t 0 ]; then
    DASHBOARD=no
  else
    echo
    echo "Start a live dashboard so you can watch the assessment in a web browser?"
    echo "  1) Yes, viewable only from this computer (most private; from another computer, use an SSH tunnel:"
    echo "     ssh -L $PORT:127.0.0.1:$PORT <this computer>, then open the link on that computer)"
    echo "  2) Yes, viewable from any device on my local network (choose this for a computer without a"
    echo "     screen; the page is unencrypted on your network, so only on a network you trust)"
    echo "  3) No dashboard"
    printf "Choose 1-3: "
    read -r choice
    case "$choice" in
      1) DASHBOARD=yes; ACCESS=local ;;
      2) DASHBOARD=yes; ACCESS=lan ;;
      3) DASHBOARD=no ;;
      *) echo "Not a valid choice; nothing started."; exit 1 ;;
    esac
  fi
fi

# Is something already on the dashboard port? Reuse it only if it's this copy's dashboard, running this
# version of the code, with this data folder's token; otherwise say what's there and stop.
RUNNING=""
STOP_CMD="scripts/assess.sh --stop"
[ "$PORT" = 8770 ] || STOP_CMD="$STOP_CMD --port $PORT"
if [ "$DASHBOARD" = yes ]; then
  command -v python3 >/dev/null 2>&1 || { echo "The dashboard needs Python 3.9 or later (python3)." >&2; exit 1; }
  probe=$(python3 -I "$REPO/tools/dashboard/dashboard.py" probe --port "$PORT" --data "$DATA")
  probe_status=$(printf '%s\n' "$probe" | sed -n 1p)
  probe_access=$(printf '%s\n' "$probe" | sed -n 2p)
  probe_root=$(printf '%s\n' "$probe" | sed -n 3p)
  case "$probe_status" in
    free) ;;
    current)
      RUNNING=$probe_access
      if [ -n "$ACCESS" ] && [ "$ACCESS" != "$RUNNING" ]; then
        echo "The dashboard already running on port $PORT is set to '$RUNNING', not '$ACCESS'. To change it,"
        echo "stop it first ($STOP_CMD) and run this again. Using it as it is."
      fi
      ACCESS=$RUNNING ;;
    outdated)
      if [ "$probe_root" = "$REPO" ]; then
        echo "A dashboard started before this copy was updated is running on port $PORT, so it would show" >&2
        echo "the old version." >&2
      elif [ "$probe_root" = unknown ]; then
        echo "A dashboard from an older version of this project is running on port $PORT." >&2
      else
        echo "A dashboard from another copy of this project is running on port $PORT:" >&2
        echo "  $probe_root" >&2
      fi
      echo "Stop it with '$STOP_CMD' and run this again, or use another port with --port N." >&2
      exit 1 ;;
    wrong_token)
      echo "A dashboard is running on port $PORT, but it was started with a different data folder, so this" >&2
      echo "script can't give you a working link to it. Stop it with '$STOP_CMD' and run this" >&2
      echo "again, or use another port with --port N." >&2
      exit 1 ;;
    *)
      echo "Port $PORT is in use by another program. Use another port with --port N (for example --port $((PORT + 1)))." >&2
      exit 1 ;;
  esac
fi

mkdir -p "$REPORTS"
chmod 700 "$REPORTS"

# Python is already required for the dashboard, so use it rather than curl (missing on minimal systems).
dashboard_up() {
  python3 -I -c 'import socket, sys
try:
    socket.create_connection(("127.0.0.1", int(sys.argv[1])), timeout=1).close()
except OSError:
    sys.exit(1)' "$PORT"
}

open_url() {
  if [ "$(uname)" = Darwin ] && open "$1" 2>/dev/null; then return; fi
  if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && command -v xdg-open >/dev/null 2>&1 \
    && xdg-open "$1" >/dev/null 2>&1; then return; fi
  return 0
}

# Print the dashboard link inside a box of asterisks so it stands out before the assistant takes over the
# terminal. Colour only on a terminal, and never when NO_COLOR is set (https://no-color.org).
url_box() {
  label="Copy this link into your browser to open the dashboard:"
  if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then on_label=$(printf '\033[1;33m'); on_url=$(printf '\033[1;36m'); off=$(printf '\033[0m')
  else on_label=""; on_url=""; off=""; fi
  width=${#label}
  [ ${#1} -gt "$width" ] && width=${#1}
  stars=$(printf '%*s' $((width + 4)) '' | tr ' ' '*')
  echo
  echo "$stars"
  printf '* %s%-*s%s *\n' "$on_label" "$width" "$label" "$off"
  printf '* %*s *\n' "$width" ''
  printf '* %s%-*s%s *\n' "$on_url" "$width" "$1" "$off"
  echo "$stars"
  echo
}

# Suggested kick-off answers: the /24 around this computer's address, the network's public address (from an
# outside service, unless --no-lookup), and one agent. The user confirms them; the dashboard pre-fills them.
SUGGESTED=""
if command -v python3 >/dev/null 2>&1; then
  set --
  [ "$DASHBOARD" = yes ] && set -- "$@" --data "$DATA"
  [ "$LOOKUP" = no ] && set -- "$@" --no-lookup
  echo
  if [ "$LOOKUP" = yes ]; then echo "Finding suggested kick-off answers (this computer's network and its public address)..."
  else echo "Finding suggested kick-off answers (this computer's network)..."; fi
  suggestions=$(python3 -I "$REPO/tools/dashboard/dashboard.py" prefill "$@" 2>/dev/null) || suggestions=""
  if [ -n "$suggestions" ]; then
    printf '%s\n' "$suggestions" | sed 's/^/  /'
    SUGGESTED=" Suggested kick-off answers detected on this computer: $(printf '%s\n' "$suggestions" | paste -sd ';' - \
| sed 's/;/; /g'). Offer them as defaults, and record them only once I've confirmed or changed them."
  fi
fi

DASHBOARD_NOTE=""
if [ "$DASHBOARD" = yes ]; then
  mkdir -p "$DATA"
  if [ -n "$RUNNING" ]; then
    echo "Using the dashboard that's already running on port $PORT. To change who can view it, stop it first:"
    echo "  $STOP_CMD"
  else
    LAN_FLAG=""
    [ "$ACCESS" = lan ] && LAN_FLAG=--lan
    nohup python3 -I "$REPO/tools/dashboard/dashboard.py" serve $LAN_FLAG --port "$PORT" --data "$DATA" \
      --reports "$REPORTS" >"$DATA/dashboard.log" 2>&1 &
    echo $! >"$DATA/dashboard.pid"
    tries=0
    until dashboard_up; do
      tries=$((tries + 1))
      if [ $tries -ge 20 ]; then
        echo "Dashboard didn't start; see $DATA/dashboard.log. If port $PORT is taken, use --port N." >&2; exit 1
      fi
      sleep 0.25
    done
    echo "Dashboard started. When you're done, stop it with: $STOP_CMD"
  fi
  if [ -n "${AISS_DASHBOARD_TOKEN:-}" ]; then TOKEN=$AISS_DASHBOARD_TOKEN; else TOKEN=$(cat "$DATA/token"); fi
  url_box "http://127.0.0.1:$PORT/#token=$TOKEN"
  open_url "http://127.0.0.1:$PORT/#token=$TOKEN"
  if grep -q '^On your LAN:' "$DATA/dashboard.log" 2>/dev/null; then
    echo "From another device on your network, open one of these:"
    grep '^On your LAN:' "$DATA/dashboard.log" | sed 's/^On your LAN: */  /'
  fi
  if [ "$ACCESS" = lan ]; then VIEW="this computer and other devices on the user's local network"
  else VIEW="this computer only"; fi
  DASHBOARD_NOTE=" A live dashboard is running (viewable from $VIEW) and reads the run folder automatically, \
so always write events there. I can also answer the kick-off questions in the dashboard's Kick-off settings tab, \
even before you ask: read events-dashboard.jsonl in the run folder before asking, and ask only what's still \
unanswered. Record the dashboard choice in the kick-off answers."
fi

PROMPT="Use the full-assessment skill from the ai-security-skills collection at $REPO \
(skills/orchestration/full-assessment/SKILL.md; product skills are in dist/) to run a complete security \
assessment of my network. Follow its \"Before anything else\" rules: set up the run folder under $REPORTS first, \
then ask me the kick-off questions, and don't scan or probe my network until I've answered them.$SUGGESTED\
$DASHBOARD_NOTE \
Don't change anything without my approval."

# The assistant takes over the terminal, so give the user time to copy the dashboard links first.
if [ "$DASHBOARD" = yes ] && [ "$AGENT" != print ] && [ -t 0 ]; then
  echo
  printf "Press any key to start %s (Ctrl+C to cancel)... " "$AGENT"
  old_stty=$(stty -g)
  trap 'stty "$old_stty"; echo; exit 130' INT
  stty -icanon -echo min 1
  dd bs=1 count=1 >/dev/null 2>&1
  stty "$old_stty"
  trap - INT
  echo
fi

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
