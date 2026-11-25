#!/usr/bin/env bash
# Polls the desk gently until a step opens, then writes the answer and stops.
set -uo pipefail
DESK="https://pequalnp.com/desk"
OUT="$(git rev-parse --show-toplevel)/.pnp"
mkdir -p "$OUT"
n=0
while true; do
  n=$((n+1))
  ans="$(curl -fsS -m 15 "$DESK/next?handle=rodi-coder&value=1" 2>/dev/null)" || { echo "[$n] desk unreachable; retrying"; sleep 90; continue; }
  gap="$(printf '%s' "$ans" | python3 -I -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: sys.exit(0)
g=d.get("gap")
if isinstance(g,dict): print("GAP")
else:
  note=str(d.get("note") or d.get("error") or "")
  import sys
  if "queue" in note.lower(): print("QUEUE")
  else: print("OTHER")' 2>/dev/null)"
  case "$gap" in
    GAP)
      echo "[$n] STEP AVAILABLE"
      printf '%s' "$ans" > "$OUT/.desk_gap.json"
      break
      ;;
    QUEUE)
      echo "[$n] still queued"
      sleep 120
      ;;
    *)
      echo "[$n] other answer: $(printf '%s' "$ans" | head -c 200)"
      printf '%s' "$ans" > "$OUT/.desk_gap.json"
      break
      ;;
  esac
done
