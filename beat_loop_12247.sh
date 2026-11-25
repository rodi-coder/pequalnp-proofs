#!/usr/bin/env bash
# Keep the lease for L-meta-12247 alive: beat every 4 minutes (local) for up to 3 hours.
# Writes STOP to .pnp/STOP_META_12247 if the desk says the lease is gone (410/error).
LEASE="69d03ade-c1e5-41ca-8137-76656c9d4b54"
LOG="$(git rev-parse --show-toplevel)/.pnp/beat_12247.log"
i=0
while [ $i -lt 45 ]; do
  i=$((i+1))
  out="$(curl -s -o /tmp/beat_out.json -w '%{http_code}' -X POST "https://pequalnp.com/desk/beat?lease=$LEASE" 2>/dev/null)"
  code="$out"
  body="$(cat /tmp/beat_out.json 2>/dev/null)"
  echo "[$i] http=$code $(echo "$body" | head -c 120)" >> "$LOG"
  if [ "$code" = "410" ] || echo "$body" | grep -q '"error"'; then
    echo "STOP: lease gone (http=$code)" >> "$LOG"
    echo "STOP" > "$(git rev-parse --show-toplevel)/.pnp/STOP_META_12247"
    exit 0
  fi
  sleep 240
done
echo "[loop done after 45 beats]" >> "$LOG"
