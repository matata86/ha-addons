# Luna Absolute Cinema

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matata86)

Server **Luna: Absolute Cinema** (Stremio addon server pro WebShare) jako addon Home Assistantu. Jedna instalace obslouží Stremio, Nuvio i Kodi (doplněk [Nokturno](https://github.com/matata86/plugin.video.nokturno)) na všech zařízeních v síti.

## Binárka Luny

Luna není volně šiřitelná, proto ji addon neobsahuje. Stáhni **`luna-x_y_z-linux-amd64`** z fóra [stremio.cz](https://stremio.cz/d/47-luna-absolute-cinema-addon-pro-prehravani-sifrovaneho-obsahu-z-webshare) a:

- **buď** ji nahraj do sdílené složky HA jako `share/luna/luna` (přes Samba addon → složka `share`, podsložka `luna`, soubor pojmenuj `luna`),
- **nebo** vyplň `luna_binary_url` – přímou adresu ke stažení (např. z vlastního NAS/webu).

Addon si binárku uloží do `/data` a při každém startu ji z `/share/luna/luna` obnoví, pokud se změnila – nová verze Luny = jen přepsat soubor a restartovat addon.

## Nastavení

| volba | výchozí | význam |
|---|---|---|
| `luna_binary_url` | prázdné | adresa ke stažení binárky, když není v `/share/luna/` |
| `port` | 7126 | HTTP port |
| `https_port` | 7127 | HTTPS port (Stremio v LAN ho vyžaduje) |
| `enable_https` | true | zapne HTTPS s certifikátem local-ip.co |
| `no_update` | true | vypne autoaktualizaci uvnitř Luny (verzi řídíš binárkou) |

## Použití

- Konfigurace: tlačítko **Otevřít webové rozhraní** → `http://IP-HA:7126/setup`
- Stremio v LAN: instaluj doplněk přes HTTPS adresu, kterou setup vypíše (`https://192-168-x-y.my.local-ip.co:7127/…`)
- Nuvio a Kodi (Nokturno): stačí HTTP adresa doplňku ze setupu

Addon běží v `host_network`, protože Luna nabízí instalační adresu podle IP, na které poslouchá — v bridge síti Dockeru by nabídla vnitřní IP kontejneru.

## Bez Home Assistantu

Luna je jedna binárka, HA je jen pohodlný obal. Stejné `luna-x_y_z-linux-amd64` (nebo verze pro Windows/macOS/ARM z fóra) spustíš přímo na libovolném počítači, který běží pořád — NAS, Raspberry Pi (verze `linux-arm64`), mini PC:

```bash
chmod +x luna-1_6_0-linux-amd64
./luna-1_6_0-linux-amd64 --https --no-update
```

Setup pak najdeš na `http://<IP-počítače>:7126/setup`, HTTPS pro Stremio na `https://<IP-s-pomlčkami>.my.local-ip.co:7127/setup`. Parametry `--port`, `--https-port`, `--https` viz `luna --help`.

**Aby běžela pořád (Linux, systemd):**

```ini
# /etc/systemd/system/luna.service
[Unit]
Description=Luna Absolute Cinema
After=network-online.target

[Service]
ExecStart=/opt/luna/luna --https --no-update
WorkingDirectory=/opt/luna
Restart=always

[Install]
WantedBy=multi-user.target
```

`sudo systemctl enable --now luna`

**Docker** (na NAS): binárka je statická, stačí minimální image s host sítí:

```yaml
services:
  luna:
    image: alpine:3
    container_name: luna
    restart: unless-stopped
    network_mode: host      # Luna musí vidět skutečnou IP kvůli instalační adrese doplňku
    volumes:
      - ./luna:/luna:ro
      - ./data:/root
    command: /luna --https --no-update
```

Windows/macOS: stáhni zip pro svou platformu z fóra a spusť aplikaci — má stejné `/setup`.

---

## Podpora

Pomohlo ti to? Kafe autorovi udělá radost ☕

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matata86)

**https://ko-fi.com/matata86**
