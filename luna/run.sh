#!/usr/bin/env bash
set -e

CONFIG=/data/options.json
PORT=$(jq -r '.port // 7126' "$CONFIG")
HTTPS_PORT=$(jq -r '.https_port // 7127' "$CONFIG")
# pozor: jq „//“ bere false jako null → false by se změnilo na true
ENABLE_HTTPS=$(jq -r 'if .enable_https == null then true else .enable_https end' "$CONFIG")
NO_UPDATE=$(jq -r 'if .no_update == null then true else .no_update end' "$CONFIG")
BIN_URL=$(jq -r '.luna_binary_url // ""' "$CONFIG")
ARCH_OPT=$(jq -r '.luna_arch // "auto"' "$CONFIG")
BIN=/data/luna

# architektura: buď vynucená v nastavení addonu, nebo zjištěná automaticky (uname -m)
if [ "$ARCH_OPT" != "auto" ]; then
  ARCH="$ARCH_OPT"
else
  case "$(uname -m)" in
    x86_64|amd64) ARCH=amd64 ;;
    aarch64|arm64) ARCH=aarch64 ;;
    armv7l|armv6l) ARCH=armv7 ;;
    *) ARCH=amd64 ;;
  esac
fi
echo "[luna] architektura: $ARCH (nastavení: $ARCH_OPT)"

# 1) binárka pro danou architekturu ve sdílené složce HA (share/luna/luna-<arch>)
#    2) starší jednoarchová instalace (share/luna/luna, bez rozlišení architektury)
#    3) stažení z adresy v nastavení (jen když ještě žádnou nemáme); {arch} v URL se
#       nahradí za amd64/aarch64/armv7, takže jedna adresa může mířit na všechny archivy
SHARE_BIN=""
if [ -f "/share/luna/luna-$ARCH" ]; then
  SHARE_BIN="/share/luna/luna-$ARCH"
elif [ -f /share/luna/luna ]; then
  SHARE_BIN="/share/luna/luna"
fi

if [ -n "$SHARE_BIN" ]; then
  if ! cmp -s "$SHARE_BIN" "$BIN"; then
    echo "[luna] beru binárku z $SHARE_BIN"
    cp "$SHARE_BIN" "$BIN"
  fi
elif [ ! -f "$BIN" ] && [ -n "$BIN_URL" ]; then
  BIN_URL="${BIN_URL//\{arch\}/$ARCH}"
  echo "[luna] stahuji binárku z $BIN_URL"
  curl -fsSL "$BIN_URL" -o "$BIN.tmp" && mv "$BIN.tmp" "$BIN"
fi

if [ ! -f "$BIN" ]; then
  echo "[luna] CHYBA: chybí binárka Luny pro architekturu $ARCH."
  echo "[luna]        Nahraj soubor jako /share/luna/luna-$ARCH (víc architektur najednou:"
  echo "[luna]        luna-amd64, luna-aarch64, luna-armv7 vedle sebe) nebo starší /share/luna/luna"
  echo "[luna]        (přes Samba: share/luna/), případně vyplň luna_binary_url v nastavení addonu."
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
