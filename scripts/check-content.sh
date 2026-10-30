#!/bin/sh
# Flags content that may violate CONTENT_RULES.md. Review every hit; exit 1 if any are found.
# Usage: scripts/check-content.sh [path ...]   (default: whole repo)

cd "$(dirname "$0")/.." || exit 2
[ $# -eq 0 ] && set -- .

hits=0
scan() {
  label=$1; pattern=$2; shift 2
  out=$(grep -rnIE -e "$pattern" "$@" \
    --exclude-dir=.git --exclude=.private-denylist --exclude=.private-denylist.example \
    --exclude=CONTENT_RULES.md --exclude=check-content.sh 2>/dev/null)
  if [ -n "$out" ]; then
    printf '\n== %s ==\n%s\n' "$label" "$out"
    hits=1
  fi
}

# IPv4 addresses, excluding RFC 5737 documentation ranges, 0.0.0.0, and loopback. Four numbers that are
# part of a longer dotted sequence (SNMP OIDs such as 1.3.6.1.2.1.1.1.0) are not addresses; a sentence-
# ending period is allowed. Four-part version numbers still match and need a human look.
ipv4=$(grep -rnIoE '(^|[^0-9.])([0-9]{1,3}\.){3}[0-9]{1,3}($|[^0-9.]|\.($|[^0-9]))' "$@" \
  --exclude-dir=.git --exclude=CONTENT_RULES.md --exclude=check-content.sh 2>/dev/null \
  | sed -E 's/^(.*:[0-9]+:)[^0-9]?([0-9]+(\.[0-9]+){3}).*$/\1\2/' \
  | grep -vE ':(192\.0\.2|198\.51\.100|203\.0\.113)\.[0-9]+$|:0\.0\.0\.0$|:127\.[0-9.]+$')
if [ -n "$ipv4" ]; then
  printf '\n== IPv4 addresses (non-documentation) ==\n%s\n' "$ipv4"
  hits=1
fi

scan "MAC addresses" '\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b' "$@"
scan "Email addresses" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' "$@"
scan "Secrets / keys" '-----BEGIN [A-Z ]*PRIVATE KEY-----|ssh-(ed25519|rsa) AAAA|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{20,}\.' "$@"
scan "Home directory paths" '/(Users|home)/[A-Za-z][A-Za-z0-9._-]+/' "$@"

if [ -f .private-denylist ]; then
  terms=$(grep -vE '^\s*(#|$)' .private-denylist)
  if [ -n "$terms" ]; then
    out=$(printf '%s\n' "$terms" | grep -rnIiF -f /dev/stdin "$@" \
      --exclude-dir=.git --exclude=.private-denylist 2>/dev/null)
    if [ -n "$out" ]; then
      printf '\n== Private denylist terms ==\n%s\n' "$out"
      hits=1
    fi
  fi
else
  printf 'note: no .private-denylist found; personal identifiers are not being checked.\n' >&2
fi

[ $hits -eq 0 ] && echo "check-content: no hits."
exit $hits
