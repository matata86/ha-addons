# Sosáč proxy pro Nuvio

Doplněk **Sosáč TV** pro Stremio funguje ve Stremiu, ale v **Nuviu** se detail titulu nenačte: Sosáč vrací `language` a `country` jako pole a `imdbRating` jako číslo, zatímco Stremio protokol čeká řetězce — striktní parser Nuvia na tom spadne (`JsonArray is not a JsonPrimitive`).

Tato proxy přeposílá všechny požadavky (manifest, catalog, meta, stream) 1:1 na `stremio.sosac.tv` a jen v odpovědích `meta`/`metas` ta tři pole narovná. Nic jiného nemění, nic neukládá.

## Nastavení

| volba | výchozí | význam |
|---|---|---|
| `upstream` | `https://stremio.sosac.tv/cs` | základ adresy Sosáče |
| `user_id` | prázdné | tvoje `userId` ze Stremio adresy Sosáče (část za `?userId=`); když je vyplněné, doplňuje se automaticky |
| `port` | 7128 | HTTP port proxy |

## Instalace v Nuviu

Otevři **webové rozhraní** addonu (`http://IP-HA:7128/`) — ukáže hotovou adresu k překopírování:

`http://IP-HA:7128/manifest.json?userId=<tvoje userId>` (s vyplněným `user_id` v nastavení stačí `http://IP-HA:7128/manifest.json`).

Původní Sosáč v Nuviu vypni, ať se katalogy nezdvojí. Stremio nech na originálu.

## Bez Home Assistantu

Proxy je jeden soubor v čistém Pythonu ([`proxy.py`](proxy.py)), bez závislostí. Poběží kdekoli, kde je Python 3 — NAS, Raspberry Pi, starý notebook, i přímo na PC, kde běží Nuvio.

**Přímo v Pythonu:**

```bash
curl -O https://raw.githubusercontent.com/matata86/ha-addons/main/sosac_proxy/proxy.py
UPSTREAM=https://stremio.sosac.tv/cs USER_ID=<tvoje userId> PORT=7128 python3 proxy.py
```

Adresa pro Nuvio: `http://<IP-počítače>:7128/manifest.json` (na stejném PC `http://127.0.0.1:7128/manifest.json`).

Windows: nainstaluj Python z python.org, stáhni `proxy.py`, spusť v příkazovém řádku:

```bat
set USER_ID=<tvoje userId>
py proxy.py
```

**Docker / docker-compose** (NAS Synology, QNAP, Unraid…):

```yaml
services:
  sosac-proxy:
    image: python:3-alpine
    container_name: sosac-proxy
    restart: unless-stopped
    ports:
      - "7128:7128"
    environment:
      UPSTREAM: https://stremio.sosac.tv/cs
      USER_ID: "<tvoje userId>"
      PORT: "7128"
    volumes:
      - ./proxy.py:/app/proxy.py:ro
    command: python3 -u /app/proxy.py
```

`docker compose up -d` ve složce se staženým `proxy.py`.

**Aby běžela pořád (Linux, systemd):**

```ini
# /etc/systemd/system/sosac-proxy.service
[Unit]
Description=Sosáč proxy pro Nuvio
After=network-online.target

[Service]
Environment=USER_ID=<tvoje userId>
Environment=PORT=7128
ExecStart=/usr/bin/python3 /opt/sosac-proxy/proxy.py
Restart=always

[Install]
WantedBy=multi-user.target
```

`sudo systemctl enable --now sosac-proxy`
