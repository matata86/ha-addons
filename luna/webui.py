#!/usr/bin/env python3
"""Malá webová obsluha doplňku Luna: stav, nahrání nové binárky, odkaz na /setup.

Neřeší nic z Luny samotné (uzavřený binární program) — jen ulehčuje výměnu
binárky, kterou dřív šlo nahrát jen přes Samba/SFTP do /share/luna/.
"""
import http.server
import json
import os
import re
import socket

CONFIG_PATH = "/data/options.json"
SHARE_DIR = "/share/luna"
VERSION_FILE = "/data/luna_version.txt"
RESTART_FLAG = "/data/.restart_flag"
ARCH = os.environ.get("ARCH", "amd64")
WEBUI_PORT = int(os.environ.get("WEBUI_PORT", "7130"))
FORUM_URL = "https://stremio.cz/d/47-luna-absolute-cinema-addon-pro-prehravani-sifrovaneho-obsahu-z-webshare"

ARCH_TO_LINUX_SUFFIX = {"amd64": "linux-amd64", "aarch64": "linux-arm64", "armv7": "linux-arm"}
# "linux-arm" je podřetězec "linux-arm64" - při ověřování názvu souboru pro armv7
# musí jít o přesnou shodu, ne o "linux-arm64" omylem uznané jako platné pro armv7.
ARCH_MATCH_RE = {
    "amd64": re.compile(r"linux-amd64"),
    "aarch64": re.compile(r"linux-arm64"),
    "armv7": re.compile(r"linux-arm(?!64)"),
}


def load_options():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def luna_port():
    return int(load_options().get("port", 7126))


def is_luna_running():
    try:
        with socket.create_connection(("127.0.0.1", luna_port()), timeout=1):
            return True
    except OSError:
        return False


def read_version():
    try:
        with open(VERSION_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def write_version(v):
    with open(VERSION_FILE, "w") as f:
        f.write(v)


def bin_path():
    return os.path.join(SHARE_DIR, f"luna-{ARCH}")


PAGE_TMPL = """<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luna – správa doplňku</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:640px;margin:2rem auto;padding:0 1rem;
     background:#111417;color:#eee}}
h1{{font-size:1.4rem}}
.status{{padding:.75rem 1rem;border-radius:8px;margin:1rem 0;line-height:1.6}}
.ok{{background:#173a1e}} .bad{{background:#3a1717}}
.card{{background:#1b1e22;border-radius:10px;padding:1.1rem 1.2rem;margin:1rem 0}}
button,input[type=submit]{{background:#3d6bdb;color:#fff;border:0;padding:.6rem 1.2rem;
     border-radius:6px;cursor:pointer;font-size:1rem}}
a.btn{{display:inline-block;background:#2a2e33;color:#eee;text-decoration:none;
     padding:.6rem 1.2rem;border-radius:6px;margin-top:.4rem}}
input[type=file]{{color:#eee;margin:.5rem 0}}
code{{background:#000;padding:.15rem .35rem;border-radius:4px}}
.hint{{color:#aaa;font-size:.92rem}}
.msg{{margin-top:.8rem}}
</style></head><body>
<h1>🌙 Luna Absolute Cinema</h1>
<div class="status {status_class}">
  <strong>Stav:</strong> {status_text}<br>
  <strong>Verze:</strong> {version}<br>
  <strong>Architektura:</strong> <code>{arch}</code>
</div>
<div class="card">
  <h2 style="margin-top:0">Nahrát novou verzi</h2>
  <p class="hint">Stáhni novou Lunu z fóra <a href="{forum_url}" target="_blank" rel="noopener">stremio.cz</a>
  (vlákno „Luna: Absolute Cinema"). Pro tenhle doplněk vyber přesně soubor
  <code>luna-&lt;verze&gt;-{expected_suffix}</code> (žádný windows/macos/apk balíček).</p>
  <form method="post" action="/upload" enctype="multipart/form-data">
    <input type="file" name="binary" accept="*" required><br>
    <input type="submit" value="Nahrát a restartovat Lunu">
  </form>
  <div class="msg">{upload_message}</div>
</div>
<div class="card">
  <a class="btn" href="http://{host}:{luna_port}/setup">⚙️ Otevřít nastavení Luny</a>
</div>
</body></html>
"""


def render(handler, message=""):
    version = read_version() or "neznámá (nahraj binárku, nebo počkej na start)"
    running = is_luna_running()
    host = handler.headers.get("Host", "").split(":")[0] or "HOST"
    html = PAGE_TMPL.format(
        status_class="ok" if running else "bad",
        status_text="✅ Luna běží" if running else "⛔ Luna neběží (nebo se právě restartuje)",
        version=version,
        arch=ARCH,
        expected_suffix=ARCH_TO_LINUX_SUFFIX.get(ARCH, "linux-" + ARCH),
        upload_message=message,
        host=host,
        luna_port=luna_port(),
        forum_url=FORUM_URL,
    ).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(html)))
    handler.end_headers()
    handler.wfile.write(html)


def parse_multipart_file(rfile, length, boundary):
    """Vrátí (filename, obsah) prvního souborového pole, nebo (None, None)."""
    data = rfile.read(length)
    boundary_bytes = ("--" + boundary).encode()
    for part in data.split(boundary_bytes):
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        header_blob, sep, body = part.partition(b"\r\n\r\n")
        if not sep:
            continue
        headers = header_blob.decode("utf-8", "replace")
        m = re.search(r'filename="([^"]*)"', headers)
        if not m or not m.group(1):
            continue
        if body.endswith(b"\r\n"):
            body = body[:-2]
        return m.group(1), body
    return None, None


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "LunaWebUI/1.0"

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path in ("/", ""):
            render(self)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/upload":
            self.send_response(404)
            self.end_headers()
            return

        content_type = self.headers.get("Content-Type", "")
        boundary_match = re.search(r"boundary=(.+)$", content_type)
        length = int(self.headers.get("Content-Length", 0))
        if "multipart/form-data" not in content_type or not boundary_match or length <= 0:
            render(self, "<p style='color:#f77'>Nahrání se nepovedlo (chybný formát).</p>")
            return

        filename, body = parse_multipart_file(self.rfile, length, boundary_match.group(1).strip('"'))
        if not filename or not body:
            render(self, "<p style='color:#f77'>Nahrání se nepovedlo — soubor nenalezen.</p>")
            return

        fname_lower = filename.lower()
        expected_suffix = ARCH_TO_LINUX_SUFFIX.get(ARCH, "linux-" + ARCH)
        match_re = ARCH_MATCH_RE.get(ARCH)
        matches = match_re.search(fname_lower) if match_re else (expected_suffix in fname_lower)
        if not matches:
            render(
                self,
                f"<p style='color:#f77'>Soubor <code>{filename}</code> neodpovídá téhle architektuře "
                f"(<code>{ARCH}</code>, čekám v názvu <code>{expected_suffix}</code>). Nic jsem nezměnil.</p>",
            )
            return

        os.makedirs(SHARE_DIR, exist_ok=True)
        with open(bin_path(), "wb") as f:
            f.write(body)
        os.chmod(bin_path(), 0o755)

        version_match = re.search(r"luna[-_]([\d_]+)", fname_lower)
        version = version_match.group(1).replace("_", ".") if version_match else None
        if version:
            write_version(version)

        with open(RESTART_FLAG, "w"):
            pass

        version_txt = f" (verze {version})" if version else ""
        render(self, f"<p style='color:#8e8'>Nahráno{version_txt}. Luna se restartuje…</p>")


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("0.0.0.0", WEBUI_PORT), Handler).serve_forever()
