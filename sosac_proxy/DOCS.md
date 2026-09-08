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
