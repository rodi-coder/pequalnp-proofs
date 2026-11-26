#!/usr/bin/env bash
# Keep the lease for L-meta-14689 alive: beat every 4 minutes (local time) for up to 3 hours.
# Writes STOP to .pnp/STOP_META_14689 if the desk says the lease is gone.
LEASE="6c9ab4f4-95ea-4bf2-929d-c1b881a95473"
ROOT="/Users/rodrigodocarmo/AI-Projects/pequalnp/pequalnp-proofs"
LOG="$ROOT/.pnp/beat_14689.log"
i=0
while [ $i -lt 45 ]; do
  i=$((i+1))
  code="$(curl -s -o /tmp/beat_out.json -w '%{http_code}' -X POST "https://pequalnp.com/desk/beat?lease=$LEASE" 2>/dev/null)"
  body="$(cat /tmp/beat_out.json 2>/dev/null | head -c 200)"
  echo "[$i] $(date +%H:%M:%S) http=$code $body" >> "$LOG"
  if [ "$code" = "410" ] || printf '%s' "$body" | grep -q '"error"'; then
    echo "[$i] STOP: lease gone (http=$code)" >> "$LOG"
    echo "STOP" > "$ROOT/.pnp/STOP_META_14689"
    exit 0
  fi
  sleep 240
done
echo "[loop done after 45 beats]" >> "$LOG"
