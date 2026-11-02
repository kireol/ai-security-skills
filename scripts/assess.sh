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

# Only one assessment at a time. The run file holds the PID of the process running it and that process's start
# time (so a reused PID isn't mistaken for it). assess.ps1 uses the same file. What to stop depends on how the
# previous run was started: assess.sh execs the assistant, so its process is the assistant, or this script
# still asking questions. assess.ps1 runs the assistant as a child process, possibly inside an interactive
# PowerShell window, which must be left open.
RUN_FILE="$DATA/assess.pid"
MARKER="full-assessment skill"   # appears in the assistant's command line (the prompt)
start_time() { LC_ALL=C ps -p "$1" -o lstart= 2>/dev/null | sed 's/  *$//'; }
command_of() { ps -ww -p "$1" -o command= 2>/dev/null || true; }
targets=""
if [ -f "$RUN_FILE" ]; then
  old_pid=$(sed -n 1p "$RUN_FILE"); old_start=$(sed -n 2p "$RUN_FILE")
  case "$old_pid" in ''|*[!0-9]*) old_pid="" ;; esac
  if [ -n "$old_pid" ] && [ "$old_pid" != $$ ] && kill -0 "$old_pid" 2>/dev/null \
    && [ -n "$old_start" ] && [ "$(start_time "$old_pid")" = "$old_start" ]; then
    agents=""
    for c in $(ps -A -o pid= -o ppid= | awk -v p="$old_pid" '$2 == p { print $1 }'); do
      case "$(command_of "$c")" in *"$MARKER"*) agents="$agents $c" ;; esac
    done
    case "$(command_of "$old_pid")" in
      *"$MARKER"*) targets=$old_pid ;;
      *assess.sh*|*assess.ps1*) targets="$agents $old_pid" ;;
      *) targets=$agents ;;   # an interactive PowerShell window: only its assistant, if one is running
    esac
  fi
fi
if [ -n "$(echo $targets)" ]; then
  echo "Another assessment started by this script is still running (process $old_pid)."
  if [ ! -t 0 ]; then
    echo "Stop it first, or run this again from a terminal to be asked." >&2; exit 1
  fi
  echo "  1) Stop the previous run and start a new one"
  echo "  2) Exit and leave the previous run alone"
  printf "Choose 1-2: "
  read -r choice
  [ "$choice" = 1 ] || { echo "Nothing started."; exit 0; }
  for t in $targets; do kill "$t" 2>/dev/null || true; done
  tries=0
  for t in $targets; do
    while kill -0 "$t" 2>/dev/null; do
      tries=$((tries + 1))
      if [ $tries -ge 20 ]; then kill -9 "$t" 2>/dev/null || true; break; fi
      sleep 0.25
    done
  done
  echo "Previous run stopped. Its run folder and any dashboard it started are left as they are."
fi
mkdir -p "$DATA"
chmod 700 "$DATA"
printf '%s\n%s\n' $$ "$(start_time $$)" >"$RUN_FILE"

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
  label=${2:-"Copy this link into your browser to open the dashboard:"}
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
  LOCAL_URL="http://127.0.0.1:$PORT/#token=$TOKEN"
  LAN_URLS=""
  if [ "$ACCESS" = lan ]; then
    # The dashboard flushes its startup lines at the end, so they may lag the port opening by a moment.
    tries=0
    while [ $tries -lt 8 ]; do
      LAN_URLS=$(grep '^On your LAN:' "$DATA/dashboard.log" 2>/dev/null | sed 's/^On your LAN: *//')
      [ -n "$LAN_URLS" ] && break
      tries=$((tries + 1)); sleep 0.25
    done
  fi
  if [ -n "$LAN_URLS" ]; then
    # In LAN mode the box shows the LAN IP address, which works from this computer and every other device.
    BOX_URL=$(printf '%s\n' "$LAN_URLS" | grep -E '^http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:' | head -n 1)
    [ -n "$BOX_URL" ] || BOX_URL=$(printf '%s\n' "$LAN_URLS" | head -n 1)
    url_box "$BOX_URL" "Copy this link into a browser on this or any device on your network:"
    echo "Other ways to open it:"
    printf '%s\n' "$LAN_URLS" | grep -vxF "$BOX_URL" | sed 's/^/  /'
    echo "  $LOCAL_URL (this computer only)"
  else
    url_box "$LOCAL_URL"
  fi
  open_url "$LOCAL_URL"
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
