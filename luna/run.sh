#!/usr/bin/env bash
set -e

CONFIG=/data/options.json
PORT=$(jq -r '.port // 7126' "$CONFIG")
HTTPS_PORT=$(jq -r '.https_port // 7127' "$CONFIG")
ENABLE_HTTPS=$(jq -r '.enable_https // true' "$CONFIG")
NO_UPDATE=$(jq -r '.no_update // true' "$CONFIG")
BIN_URL=$(jq -r '.luna_binary_url // ""' "$CONFIG")
BIN=/data/luna

# 1) binárka nahraná uživatelem do sdílené složky HA (Samba → share/luna/luna)
if [ -f /share/luna/luna ]; then
  if ! cmp -s /share/luna/luna "$BIN"; then
    echo "[luna] beru binárku z /share/luna/luna"
    cp /share/luna/luna "$BIN"
  fi
# 2) nebo stažení z adresy v nastavení (jen když ještě žádnou nemáme)
elif [ ! -f "$BIN" ] && [ -n "$BIN_URL" ]; then
  echo "[luna] stahuji binárku z $BIN_URL"
  curl -fsSL "$BIN_URL" -o "$BIN.tmp" && mv "$BIN.tmp" "$BIN"
fi

if [ ! -f "$BIN" ]; then
  echo "[luna] CHYBA: chybí binárka Luny. Nahraj soubor luna-x_y_z-linux-amd64 jako /share/luna/luna"
  echo "[luna]        (přes Samba: share/luna/luna) nebo vyplň luna_binary_url v nastavení addonu."
  exit 1
fi
chmod +x "$BIN"

# Perzistentní data (konfigurace, tokeny) – /data přežije restart i update addonu
export HOME=/data
cd /data

ARGS=(-port "$PORT" -https-port "$HTTPS_PORT")
[ "$ENABLE_HTTPS" = "true" ] && ARGS+=(-https)
[ "$NO_UPDATE" = "true" ] && ARGS+=(-no-update)

echo "[luna] spouštím: luna ${ARGS[*]}"
exec "$BIN" "${ARGS[@]}"
