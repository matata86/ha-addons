#!/usr/bin/env bash
set -e
CONFIG=/data/options.json
export UPSTREAM=$(jq -r '.upstream // "https://stremio.sosac.tv/cs"' "$CONFIG")
export USER_ID=$(jq -r '.user_id // ""' "$CONFIG")
export PORT=$(jq -r '.port // 7128' "$CONFIG")
exec python3 -u /app/proxy.py
