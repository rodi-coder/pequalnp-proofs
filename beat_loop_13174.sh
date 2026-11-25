#!/usr/bin/env bash
# Keep the lease for L-meta-11244 alive: beat every 4 minutes (local) for up to 3 hours.
# Writes STOP to .pnp/STOP_META_11244 if the desk says the lease is gone (410/error).
LEASE="0f6e5ead-66a5-4044-8ddc-ddb439d0ba22"
LOG="$(git rev-parse --show-toplevel)/.pnp/beat_11244.log"
i=0
while [ $i -lt 45 ]; do
  i=$((i+1))
  out="$(curl -s -o /tmp/beat_out.json -w '%{http_code}' -X POST "https://pequalnp.com/desk/beat?lease=$LEASE" 2>/dev/null)"
  code="$out"
  body="$(cat /tmp/beat_out.json 2>/dev/null)"
  echo "[$i] http=$code $(echo "$body" | head -c 120)" >> "$LOG"
  if [ "$code" = "410" ] || echo "$body" | grep -q '"error"'; then
    echo "STOP: lease gone (http=$code)" >> "$LOG"
    echo "STOP" > "$(git rev-parse --show-toplevel)/.pnp/STOP_META_11244"
    exit 0
  fi
  sleep 240
done
echo "[loop done after 45 beats]" >> "$LOG"
