#!/usr/bin/env python3
"""Malá webová obsluha doplňku Luna: stav, nahrání nové binárky, odkaz na /setup.

Neřeší nic z Luny samotné (uzavřený binární program) — jen ulehčuje výměnu
binárky, kterou dřív šlo nahrát jen přes Samba/SFTP do /share/luna/.
"""
import base64
import http.server
import json
import os
import re
import socket

CONFIG_PATH = "/data/options.json"
ICON_PATH = "/icon.png"
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


def load_icon_data_uri():
    try:
        with open(ICON_PATH, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    except FileNotFoundError:
        return ""


ICON_DATA_URI = load_icon_data_uri()


PAGE_TMPL = """<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luna – správa doplňku</title>
<style>
:root {{
  --pozadi:#0d0c1d; --panel:#17162b; --panel-2:#1c1b33; --pole:#201f38; --okraj:#2f2d4d;
  --text:#e8e6f5; --tlumene:#9a97b8; --akcent:#7b5bf5; --akcent-tmavy:#6547d6;
  --ok:#3ecf8e; --ok-pozadi:#12291f; --vystraha:#f5a524; --vystraha-pozadi:#2a2214;
  --chyba:#ff6b6b; --chyba-pozadi:#2c1518;
}}
*{{box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;max-width:736px;
     margin:2.5rem auto;padding:0 1.25rem 3rem;background:var(--pozadi);color:var(--text)}}
header{{display:flex;align-items:center;gap:.8rem;margin-bottom:1.5rem}}
.logo{{width:44px;height:44px;border-radius:12px;flex:none;display:block;object-fit:cover;
      background:var(--panel-2)}}
h1{{font-size:1.35rem;font-weight:700;margin:0}}
.sub{{color:var(--tlumene);font-size:.85rem;margin-top:.15rem}}
.panel{{background:var(--panel);border:1px solid var(--okraj);border-radius:14px;
       padding:1.1rem 1.2rem;margin-bottom:1.1rem}}
.status-panel{{display:flex;flex-wrap:wrap;gap:.5rem 1.6rem;align-items:center}}
.status-item{{display:flex;flex-direction:column;gap:.15rem}}
.status-item .label{{color:var(--tlumene);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}}
.status-item .value{{font-size:1rem;font-weight:600}}
.pill{{display:inline-flex;align-items:center;gap:.35rem;padding:.2rem .65rem;border-radius:999px;
      font-size:.8rem;font-weight:600;white-space:nowrap}}
.pill.ok{{background:var(--ok-pozadi);color:var(--ok)}}
.pill.bad{{background:var(--chyba-pozadi);color:var(--chyba)}}
h2{{font-size:1.05rem;margin:0 0 .5rem}}
.hint{{color:var(--tlumene);font-size:.9rem;line-height:1.5;margin:0 0 1rem}}
.hint a{{color:var(--akcent)}}
code{{background:var(--pole);border:1px solid var(--okraj);padding:.1rem .4rem;
     border-radius:6px;font-size:.85em}}
input[type=file]{{display:block;width:100%;background:var(--pole);border:1px solid var(--okraj);
     color:var(--tlumene);border-radius:8px;padding:.55rem .7rem;font-size:.9rem;margin-bottom:.9rem}}
input[type=file]::file-selector-button{{background:var(--panel-2);color:var(--text);
     border:1px solid var(--okraj);border-radius:7px;padding:.45rem .9rem;font-size:.85rem;
     font-weight:600;cursor:pointer;margin-right:.8rem}}
input[type=file]::file-selector-button:hover{{background:var(--okraj)}}
.btn{{display:inline-flex;align-items:center;gap:.4rem;border:0;border-radius:9px;
     padding:.65rem 1.3rem;font-size:.92rem;font-weight:600;cursor:pointer;
     text-decoration:none;color:#fff}}
.btn-primary{{background:linear-gradient(160deg,var(--akcent),var(--akcent-tmavy))}}
.btn-secondary{{background:var(--pole);color:var(--text);border:1px solid var(--okraj)}}
.msg{{margin-top:.9rem;font-size:.9rem}}
.msg.err{{color:var(--chyba)}} .msg.okmsg{{color:var(--ok)}}
</style></head><body>
<header>
  <img class="logo" src="{icon}" alt="Luna">
  <div>
    <h1>Luna Absolute Cinema</h1>
    <div class="sub">Správa doplňku</div>
  </div>
</header>

<div class="panel status-panel">
  <span class="pill {status_class}">{status_text}</span>
  <div class="status-item"><span class="label">Verze</span><span class="value">{version}</span></div>
  <div class="status-item"><span class="label">Architektura</span><span class="value"><code>{arch}</code></span></div>
</div>

<div class="panel">
  <h2>Nahrát novou verzi</h2>
  <p class="hint">Stáhni novou Lunu z fóra <a href="{forum_url}" target="_blank" rel="noopener">stremio.cz</a>
  (vlákno „Luna: Absolute Cinema"). Pro tenhle doplněk vyber přesně soubor
  <code>luna-&lt;verze&gt;-{expected_suffix}</code> — žádný windows/macos/apk balíček.</p>
  <form method="post" action="/upload" enctype="multipart/form-data">
    <input type="file" name="binary" accept="*" required>
    <button class="btn btn-primary" type="submit">Nahrát a restartovat Lunu</button>
  </form>
  <div class="msg">{upload_message}</div>
</div>

<div class="panel">
  <a class="btn btn-secondary" href="http://{host}:{luna_port}/setup">⚙️ Otevřít nastavení Luny</a>
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
        icon=ICON_DATA_URI,
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
            render(self, "<p style='color:var(--chyba)'>Nahrání se nepovedlo (chybný formát).</p>")
            return

        filename, body = parse_multipart_file(self.rfile, length, boundary_match.group(1).strip('"'))
        if not filename or not body:
            render(self, "<p style='color:var(--chyba)'>Nahrání se nepovedlo — soubor nenalezen.</p>")
            return

        fname_lower = filename.lower()
        expected_suffix = ARCH_TO_LINUX_SUFFIX.get(ARCH, "linux-" + ARCH)
        match_re = ARCH_MATCH_RE.get(ARCH)
        matches = match_re.search(fname_lower) if match_re else (expected_suffix in fname_lower)
        if not matches:
            render(
                self,
                f"<p style='color:var(--chyba)'>Soubor <code>{filename}</code> neodpovídá téhle architektuře "
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
        render(self, f"<p style='color:var(--ok)'>Nahráno{version_txt}. Luna se restartuje…</p>")


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("0.0.0.0", WEBUI_PORT), Handler).serve_forever()
