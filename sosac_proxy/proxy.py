#!/usr/bin/env python3
"""Sosáč → Nuvio proxy.

Přeposílá požadavky Stremio protokolu na stremio.sosac.tv a v odpovědích
normalizuje pole, která Sosáč vrací mimo specifikaci (a na kterých padá
striktní JSON parser Nuvia):
  language, country : list  -> "a, b"
  imdbRating        : number -> "7.2"
Vše ostatní jde beze změny.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get("UPSTREAM", "https://stremio.sosac.tv/cs").rstrip("/")
USER_ID = os.environ.get("USER_ID", "").strip()
PORT = int(os.environ.get("PORT", "7128"))
TIMEOUT = 30

STRING_FIELDS = ("language", "country")


def log(msg):
    print(msg, flush=True)


def fix_meta(meta):
    if not isinstance(meta, dict):
        return meta
    for key in STRING_FIELDS:
        val = meta.get(key)
        if isinstance(val, list):
            meta[key] = ", ".join(str(x) for x in val)
    rating = meta.get("imdbRating")
    if isinstance(rating, str) and rating.strip().isdigit():
        rating = int(rating)
    if isinstance(rating, bool):
        meta["imdbRating"] = str(int(rating))
    elif isinstance(rating, (int, float)):
        # Sosáč posílá 72 = 7.2/10 (v katalogu jako string "78", v meta jako číslo)
        meta["imdbRating"] = f"{rating / 10:.1f}" if rating > 10 else f"{rating:.1f}"
    for video in meta.get("videos") or []:
        fix_meta(video)
    return meta


def fix_body(body):
    try:
        data = json.loads(body)
    except ValueError:
        return body
    if isinstance(data, dict):
        if "meta" in data:
            fix_meta(data["meta"])
        for m in data.get("metas") or []:
            fix_meta(m)
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "SosacNuvioProxy/1.0"

    def log_message(self, fmt, *args):
        log("[proxy] " + fmt % args)

    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            return self._send(200, self.index_page(), "text/html; charset=utf-8")
        if path == "/health":
            return self._send(200, b'{"ok":true}')

        query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        if USER_ID and not query.get("userId"):
            query["userId"] = USER_ID
        url = UPSTREAM + path
        if query:
            url += "?" + urllib.parse.urlencode(query)

        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (SosacNuvioProxy)",
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                body = resp.read()
                ctype = resp.headers.get("Content-Type", "application/json")
                status = resp.status
        except urllib.error.HTTPError as e:
            body = e.read()
            ctype = e.headers.get("Content-Type", "application/json")
            status = e.code
        except Exception as e:  # síť, timeout
            log(f"[proxy] upstream chyba {url}: {e}")
            return self._send(502, json.dumps({"error": str(e)}).encode())

        if "json" in ctype and path.endswith(".json"):
            body = fix_body(body)
            ctype = "application/json; charset=utf-8"
        self._send(status, body, ctype)

    def index_page(self):
        host = self.headers.get("Host", f"localhost:{PORT}")
        base = f"http://{host}"
        install = f"{base}/manifest.json" + (f"?userId={USER_ID}" if USER_ID else "?userId=<TVOJE_USER_ID>")
        html = f"""<!doctype html><meta charset="utf-8"><title>Sosáč proxy pro Nuvio</title>
<style>body{{font:15px/1.5 system-ui;max-width:720px;margin:40px auto;padding:0 16px;color:#222}}code{{background:#eee;padding:2px 6px;border-radius:4px}}</style>
<h1>Sosáč proxy pro Nuvio</h1>
<p>Přeposílá <code>{UPSTREAM}</code> a opravuje <code>language</code>, <code>country</code> a <code>imdbRating</code> v meta odpovědích tak, aby je Nuvio umělo přečíst.</p>
<p><b>Adresa doplňku pro Nuvio:</b><br><code>{install}</code></p>
<p>userId vezmi z původní instalační adresy Sosáče (část za <code>?userId=</code>). Pokud je nastaveno v konfiguraci addonu, doplňuje se automaticky.</p>
<p><a href="{base}/manifest.json{'?userId=' + USER_ID if USER_ID else ''}">manifest.json</a> · <a href="{base}/health">health</a></p>"""
        return html.encode("utf-8")


def main():
    log(f"[proxy] upstream={UPSTREAM} user_id={'nastaveno' if USER_ID else 'není'} port={PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
