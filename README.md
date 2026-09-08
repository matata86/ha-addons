# Nokturno add-ons pro Home Assistant

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matata86)

Doplňky pro Home Assistant kolem českého streamování — společně s Kodi doplňkem [Nokturno](https://github.com/matata86/plugin.video.nokturno) tvoří jeden celek: **Luna** běží jednou na HA a obslouží Stremio, Nuvio i Kodi v celé domácnosti.

[![Přidat repozitář do Home Assistantu](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmatata86%2Fha-addons)

| addon | k čemu |
|---|---|
| **[Luna Absolute Cinema](luna/)** | server [Luna](https://stremio.cz/d/47-luna-absolute-cinema-addon-pro-prehravani-sifrovaneho-obsahu-z-webshare) — Stremio/Nuvio/Kodi doplněk pro přehrávání z WebShare (TMDB katalogy, kvalita, jazyky). Jedna instalace pro celou LAN, HTTP i HTTPS. |
| **[Sosáč proxy pro Nuvio](sosac_proxy/)** | opravuje odpovědi Stremio doplňku Sosáč TV tak, aby je přečetl striktní parser Nuvia. Bez ní se v Nuviu nenačte detail titulu. |

## Instalace

1. Home Assistant → **Nastavení → Doplňky → Obchod s doplňky → ⋮ (vpravo nahoře) → Repozitáře**
2. Vlož `https://github.com/matata86/ha-addons` a potvrď (nebo klikni na tlačítko výše).
3. V obchodě se objeví sekce *Nokturno add-ons pro Home Assistant* → vyber addon → **Instalovat**.

### Luna – co je potřeba navíc

Luna není volně šiřitelná binárka, proto ji addon neobsahuje. Stáhni `luna-x_y_z-linux-amd64` z [fóra stremio.cz](https://stremio.cz/d/47-luna-absolute-cinema-addon-pro-prehravani-sifrovaneho-obsahu-z-webshare) a nahraj ji přes Samba do sdílené složky HA jako **`share/luna/luna`** (nebo vyplň `luna_binary_url`). Pak addon spusť a otevři jeho webové rozhraní (`http://IP-HA:7126/setup`), kde přihlásíš WebShare a dostaneš adresy doplňku:

- **Stremio v LAN** — instaluj přes HTTPS adresu `https://192-168-x-y.my.local-ip.co:7127/…` (Stremio jiné než HTTPS v LAN nepřijme)
- **Nuvio, Kodi (Nokturno)** — stačí HTTP adresa `http://IP-HA:7126/…`

Podrobnosti a nastavení: [luna/DOCS.md](luna/DOCS.md).

### Sosáč proxy – kdy ji potřebuješ

Jen pokud používáš Sosáč v **Nuviu**. Nastav `user_id` (ze Stremio adresy Sosáče, část za `?userId=`), spusť addon a v Nuviu nainstaluj `http://IP-HA:7128/manifest.json`. Podrobnosti: [sosac_proxy/DOCS.md](sosac_proxy/DOCS.md).

## Nemáš Home Assistant?

Oba addony jsou obyčejné programy, HA je jen obal:

- **Luna** — spusť binárku přímo na NAS / Raspberry / mini PC (`./luna --https --no-update`), nebo přes Docker; návod v [luna/DOCS.md](luna/DOCS.md#bez-home-assistantu).
- **Sosáč proxy** — jeden soubor `proxy.py` v čistém Pythonu, poběží i na PC s Nuviem (`USER_ID=… python3 proxy.py`), Docker compose i systemd v [sosac_proxy/DOCS.md](sosac_proxy/DOCS.md#bez-home-assistantu).

## Architektura

```
              ┌────────────────────────── Home Assistant ──────────────────────────┐
WebShare ───▶ │  Luna (7126 HTTP / 7127 HTTPS)      Sosáč proxy (7128) ───▶ stremio.sosac.tv
              └───────┬───────────────┬────────────────────┬───────────────────────┘
                      │               │                    │
                 Stremio (HTTPS)   Nuvio (HTTP)      Kodi – Nokturno (HTTP)
```

## Licence

MIT (samotná Luna má vlastní licenci svého autora).

---

## Podpora

Pomohlo ti to? Kafe autorovi udělá radost ☕

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matata86)

**https://ko-fi.com/matata86**
