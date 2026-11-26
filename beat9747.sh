#!/usr/bin/env bash
# Keep the lease for L-meta-9747 alive: beat every 4 minutes (local time) for up to 3 hours.
# Writes STOP to .pnp/STOP_META_9747 if the desk says the lease is gone.
LEASE="80b42de2-8c9f-4ba1-a7f1-5f4843f656c2"
ROOT="/Users/rodrigodocarmo/AI-Projects/pequalnp/pequalnp-proofs"
LOG="$ROOT/.pnp/beat_9747.log"
i=0
while [ $i -lt 45 ]; do
  i=$((i+1))
  code="$(curl -s -o /tmp/beat_out.json -w '%{http_code}' -X POST "https://pequalnp.com/desk/beat?lease=$LEASE" 2>/dev/null)"
  body="$(cat /tmp/beat_out.json 2>/dev/null | head -c 200)"
  echo "[$i] $(date +%H:%M:%S) http=$code $body" >> "$LOG"
  if [ "$code" = "410" ] || printf '%s' "$body" | grep -q '"error"'; then
    echo "[$i] STOP: lease gone (http=$code)" >> "$LOG"
    echo "STOP" > "$ROOT/.pnp/STOP_META_9747"
    exit 0
  fi
  sleep 240
done
echo "[loop done after 45 beats]" >> "$LOG"
