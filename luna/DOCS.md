# Luna Absolute Cinema

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matata86)

Server **Luna: Absolute Cinema** (Stremio addon server pro WebShare) jako addon Home Assistantu. Jedna instalace obslouží Stremio, Nuvio i Kodi (doplněk [Nokturno](https://github.com/matata86/plugin.video.nokturno)) na všech zařízeních v síti.

## Webové rozhraní doplňku (nejjednodušší cesta k nové binárce)

Tlačítko **Otevřít webové rozhraní** v Home Assistantu vede na vlastní stránku addonu (port 7130) — ne rovnou na `/setup` Luny. Ukáže:

- jestli Luna běží a jakou má verzi,
- architekturu, kterou HA potřebuje (`amd64` / `aarch64` / `armv7`),
- formulář pro nahrání binárky přímo z prohlížeče — s nápovědou na přesný název souboru pro tuhle architekturu,
- tlačítko na skutečné nastavení Luny (`/setup`).

Po nahrání addon binárku sám ověří (odmítne soubor pro jinou architekturu), uloží do `/share/luna/` a Lunu restartuje — bez restartu celého addonu. Verzi si stránka přečte přímo z názvu nahraného souboru (např. `luna-1_7_0-linux-amd64` → `1.7.0`).

Samba/SFTP do `/share/luna/` (níž) pořád funguje jako alternativa, hlavně když chceš mít binárky pro víc architektur připravené najednou.

## Binárka Luny

Luna není volně šiřitelná, proto ji addon neobsahuje. Stáhni binárku(y) pro architekturu(y) svého HA z fóra [stremio.cz](https://stremio.cz/d/47-luna-absolute-cinema-addon-pro-prehravani-sifrovaneho-obsahu-z-webshare):

- **amd64** (PC, Intel NUC, většina VM) → `luna-x_y_z-linux-amd64`
- **aarch64** (Raspberry Pi ve 64bit HAOS, což je dnes většina RPi instalací) → `luna-x_y_z-linux-arm64`
- **armv7** (32bit HAOS, starší Raspberry Pi) → `luna-x_y_z-linux-arm`

Soubory nahraj do sdílené složky HA (Samba addon → složka `share`, podsložka `luna`) a přejmenuj podle architektury, kterou obsahují:

- `share/luna/luna-amd64`
- `share/luna/luna-aarch64`
- `share/luna/luna-armv7`

Klidně tam nahraj **všechny tři najednou** — addon si při startu sám zjistí architekturu HA (`uname -m`) a použije odpovídající soubor, ostatní ignoruje. Jedna sdílená složka tak funguje pro všechny instalace v síti bez ohledu na to, na jakém HW běží. Pokud chceš použít jinou architekturu, než jakou má tvůj HA (např. test), přepni ji v nastavení addonu volbou **Architektura binárky** (`auto` / `amd64` / `aarch64` / `armv7`).

Starší jednoarchové instalace mohou nadále používat `share/luna/luna` (bez přípony) — pořád funguje jako záloha, když soubor pro danou architekturu chybí.

Alternativa bez Samby: vyplň `luna_binary_url` – přímou adresu ke stažení (např. z vlastního NAS/webu). Pokud adresa obsahuje `{arch}`, addon ho při stahování nahradí za `amd64`/`aarch64`/`armv7` podle zjištěné architektury — jedna URL tak může mířit na všechny varianty najednou.

Addon si binárku uloží do `/data` a při každém startu ji ze sdílené složky obnoví, pokud se změnila – nová verze Luny = jen přepsat soubor(y) a restartovat addon.

## Nastavení

| volba | výchozí | význam |
|---|---|---|
| `luna_binary_url` | prázdné | adresa ke stažení binárky, když není v `/share/luna/`; podporuje `{arch}` jako zástupný symbol |
| `luna_arch` | `auto` | architektura binárky (`auto` = podle HW HA, nebo vynuceně `amd64`/`aarch64`/`armv7`) |
| `port` | 7126 | HTTP port |
| `https_port` | 7127 | HTTPS port (Stremio v LAN ho vyžaduje) |
| `enable_https` | true | zapne HTTPS s certifikátem local-ip.co |
| `no_update` | true | vypne autoaktualizaci uvnitř Luny (verzi řídíš binárkou) |

## Použití

- Konfigurace Luny (WebShare účet, streamy…): z webového rozhraní doplňku klikni na **Otevřít nastavení Luny**, nebo rovnou `http://IP-HA:7126/setup`
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

**Docker** (na NAS): od verze 1.7.0 je linuxová binárka dynamicky linkovaná proti glibc — Alpine (musl) ji nespustí (`exec /luna: no such file or directory`). Použij glibc-based image:

```yaml
services:
  luna:
    image: debian:bookworm-slim
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
